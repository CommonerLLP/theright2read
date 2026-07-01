# theright2read — corpus refresh entry points.
#
# Stage split:
# - commoner-probe acquires LS + RS records into data/_parliament_libraries/.
# - sansad-semantic-crawler parses, analyses, and exports over that corpus.
# The host project supplies topics/libraries.json and the final public artifact
# remains assets/parliament_libraries.js.
#
# `corpus-enrich` joins the manifest export with discourse/ministry analysis
# into assets/parliament_libraries.js via scripts/build_parliament_libraries.py
# because the upstream export only emits the manifest-derived summary.
#
# After regenerating assets/parliament_libraries.js, BUMP THE `?v=N`
# cache-bust suffix everywhere it is referenced.

VENV   := .venv
PYTHON := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip
PROBE  := $(VENV)/bin/commoner-probe

TOPIC_PROFILE := topics/libraries.json
CORPUS_OUT    := data/_parliament_libraries
EXPORT_PATH   := assets/parliament_libraries.js
CORPUS_DEPS   := $(VENV)/.corpus-deps.stamp

.PHONY: deps test corpus-crawl corpus-crawl-committees corpus-parse corpus-export \
        corpus-extract-answers corpus-analyse-discourse corpus-analyse-ministry \
        corpus-analyse corpus-enrich corpus-refresh spend-page sync-agents \
        hooks prune help doctor paper zotero site-content

$(PYTHON):
	python3 -m venv $(VENV)
	$(PIP) install -q -r requirements.txt -r requirements-dev.txt
	touch $(CORPUS_DEPS)

deps: $(PYTHON)
	$(PIP) install -r requirements.txt -r requirements-dev.txt
	touch $(CORPUS_DEPS)

$(CORPUS_DEPS): $(PYTHON) requirements.txt
	$(PIP) install -q -r requirements.txt
	touch $(CORPUS_DEPS)

test: $(PYTHON)
	$(PYTHON) -m pytest tests/ -v

corpus-crawl: $(CORPUS_DEPS)
	@test -f $(TOPIC_PROFILE) || { echo "missing $(TOPIC_PROFILE)"; exit 1; }
	$(PROBE) sansad \
	  --topic $(TOPIC_PROFILE) \
	  --out   $(CORPUS_OUT) \
	  $(ARGS)

# Standing-committee report crawl. Pulls LS + RS committee report records
# (Demands for Grants, subject reports, Action Taken Reports) matching the
# topic profile, downloads PDFs, and appends to manifest.jsonl. Far smaller
# than the Q&A crawl (typically 20-100 reports per topic). Pass scope flags
# through $(ARGS), e.g.:
#   make corpus-crawl-committees ARGS="--from-date 2017-01-01 --house both"
#   make corpus-crawl-committees ARGS="--max-records 5"   # smoke test
corpus-crawl-committees: $(CORPUS_DEPS)
	@test -f $(TOPIC_PROFILE) || { echo "missing $(TOPIC_PROFILE)"; exit 1; }
	$(PROBE) committees \
	  --topic $(TOPIC_PROFILE) \
	  --out   $(CORPUS_OUT) \
	  $(ARGS)

corpus-parse: $(CORPUS_DEPS)
	$(PYTHON) -m sansad_semantic_crawler parse \
	  --topic $(TOPIC_PROFILE) \
	  --out   $(CORPUS_OUT)

corpus-export: $(CORPUS_DEPS)
	$(PYTHON) -m sansad_semantic_crawler export \
	  --topic       $(TOPIC_PROFILE) \
	  --out         $(CORPUS_OUT) \
	  --format      js \
	  --js-global   PARLIAMENT_LIBRARY_DATA \
	  --export-path $(EXPORT_PATH)

# Analytical layer.
corpus-extract-answers: $(CORPUS_DEPS)
	$(PYTHON) -m sansad_semantic_crawler extract-answers \
	  --out $(CORPUS_OUT)

corpus-analyse-discourse: $(CORPUS_DEPS)
	$(PYTHON) -m sansad_semantic_crawler analyse-discourse \
	  --out $(CORPUS_OUT)

corpus-analyse-ministry: $(CORPUS_DEPS)
	$(PYTHON) -m sansad_semantic_crawler analyse-ministry \
	  --topic $(TOPIC_PROFILE) \
	  --out   $(CORPUS_OUT)

corpus-analyse: corpus-extract-answers corpus-analyse-discourse corpus-analyse-ministry

# Join the upstream manifest export with the v1.0.0 analytical outputs
# into a single enriched assets/parliament_libraries.js.
corpus-enrich: corpus-export
	$(PYTHON) scripts/build_parliament_libraries.py

# Build the /spend/ page (Quarto).
spend-page: $(PYTHON)
	cd spend && QUARTO_PYTHON=../$(PYTHON) quarto render index.qmd

# Full pipeline: crawl → parse → analyse → export → enrich. After this
# finishes, manually bump the `?v=N` cache-bust everywhere index.html /
# data/index.html / inequality/index.html load assets/parliament_libraries.js.
corpus-refresh: corpus-crawl corpus-parse corpus-analyse corpus-enrich

sync-agents:
	python3 scripts/sync_agents.py

hooks:  ## Install git pre-commit hook (run once after clone)
	bash ../_org/scripts/install-hooks.sh

doctor:  ## Verify local toolchain pins
	bash ../_org/scripts/toolchain-doctor.sh

WP ?= 1
paper:  ## Build a full working paper PDF (front matter + body): make paper WP=1
	bash research/working-papers/build-paper.sh $(WP)

zotero: $(PYTHON)  ## Generate the Zotero upsert snippet from papers.toml
	$(PYTHON) research/working-papers/_shared/papers_to_zotero.py

site-content: $(PYTHON)  ## Regenerate /writing + /library data from papers.toml + Zotero
	$(PYTHON) research/working-papers/_shared/site_content.py

prune:  ## Delete local branches already merged into main
	git fetch --prune
	git branch --merged main | grep -vE '^\*|main' | xargs -r git branch -d

help:
	@echo "Corpus refresh (commoner-probe acquisition + sansad-semantic-crawler analysis):"
	@echo "  make corpus-refresh                   — full pipeline (crawl + parse + analyse + enrich)"
	@echo "  make corpus-crawl   ARGS='--max-records 5 --no-download'  — acquisition smoke-test"
	@echo "  make corpus-crawl-committees          — standing-committee reports (opt-in; not in corpus-refresh)"
	@echo "  make corpus-crawl-committees ARGS='--from-date 2017-01-01 --max-records 5'  — smoke-test"
	@echo "  make corpus-parse                     — re-extract text from cached PDFs"
	@echo "  make corpus-analyse                   — extract-answers + analyse-discourse + analyse-ministry"
	@echo "  make corpus-export                    — upstream manifest-only export"
	@echo "  make corpus-enrich                    — export + join analytical files (the public artefact)"
	@echo "Setup:"
	@echo "  make deps                             — install pinned deps into .venv"
	@echo "  make test                             — run docs/code sync checks"
	@echo "  make doctor                           — verify toolchain pins (quarto/python/tex/fonts)"
	@echo "Working papers:"
	@echo "  make paper WP=1                       — build a full working paper (cover + colophon + body)"
	@echo "  make zotero                           — generate the Zotero upsert snippet from papers.toml"
	@echo "  make site-content                     — regenerate /writing + /library data (papers.toml + Zotero)"
	@echo "Agent rules:"
	@echo "  make sync-agents                      — regenerate local dev config"
	@echo "  make hooks                            — install pre-commit hook into .git/hooks/"
	@echo "  make prune                            — delete local branches merged into main"

data-init:  ## Create the local corpus output directory under the public data page
	mkdir -p data/_parliament_libraries

data-link:  ## Symlink only the corpus output dir: make data-link EXTERNAL=/path/to/drive
	@test -n "$(EXTERNAL)" || (echo "Usage: make data-link EXTERNAL=/path/to/drive"; exit 1)
	mkdir -p data
	mkdir -p $(EXTERNAL)/$(shell basename $(CURDIR))/_parliament_libraries
	ln -sfn $(EXTERNAL)/$(shell basename $(CURDIR))/_parliament_libraries data/_parliament_libraries
	@echo "data/_parliament_libraries/ → $(EXTERNAL)/$(shell basename $(CURDIR))/_parliament_libraries"
