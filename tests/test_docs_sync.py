from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
CONTRIBUTING_PATH = REPO_ROOT / "CONTRIBUTING.md"
MAKEFILE_PATH = REPO_ROOT / "Makefile"
REQUIREMENTS_PATH = REPO_ROOT / "requirements.txt"

# The README is campaign-first and delegates build/reproducibility to
# CONTRIBUTING.md, so the parliamentary-corpus contract is enforced there.


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def requirement_ref(requirements: str, package: str) -> str | None:
    match = re.search(
        rf"{re.escape(package)}\[http,pdf\]\s+@\s+git\+https://github\.com/CommonerLLP/"
        rf"{re.escape(package)}\.git@([^\s]+)",
        requirements,
    )
    return match.group(1) if match else None


def test_contributing_pinned_refresh_refs_match_requirements() -> None:
    docs = read_text(CONTRIBUTING_PATH)
    requirements = read_text(REQUIREMENTS_PATH)

    commoner_ref = requirement_ref(requirements, "commoner-probe")
    sansad_ref = requirement_ref(requirements, "sansad-semantic-crawler")

    assert commoner_ref, "requirements.txt should pin commoner-probe by ref"
    assert sansad_ref, "requirements.txt should pin sansad-semantic-crawler by ref"
    assert re.search(rf"pinned at\s+`{re.escape(commoner_ref)}`", docs), (
        "CONTRIBUTING.md should document commoner-probe's pinned ref"
    )
    assert re.search(rf"pinned at\s+`{re.escape(sansad_ref)}`", docs), (
        "CONTRIBUTING.md should document sansad-semantic-crawler's pinned ref"
    )


def test_makefile_keeps_acquisition_and_analysis_split() -> None:
    makefile = read_text(MAKEFILE_PATH)

    assert "$(PROBE) sansad" in makefile
    assert "$(PROBE) committees" in makefile
    assert "sansad_semantic_crawler parse" in makefile
    assert "sansad_semantic_crawler export" in makefile
    assert "sansad_semantic_crawler analyse-discourse" in makefile
    assert "sansad_semantic_crawler analyse-ministry" in makefile


def _code_spans(text: str) -> str:
    """Only fenced blocks and inline code — so prose like 'make the case' is ignored."""
    fences = re.findall(r"```.*?```", text, flags=re.DOTALL)
    inline = re.findall(r"`[^`]+`", text)
    return "\n".join(fences + inline)


def test_documented_make_commands_exist_in_makefile() -> None:
    code = _code_spans(read_text(README_PATH)) + "\n" + _code_spans(read_text(CONTRIBUTING_PATH))
    makefile = read_text(MAKEFILE_PATH)

    documented_targets = set(re.findall(r"make ([a-z0-9-]+)", code))
    actual_targets = set(
        match.group(1)
        for match in re.finditer(r"^([a-z0-9-]+):", makefile, flags=re.MULTILINE)
        if not match.group(1).startswith(".")
    )

    missing = documented_targets - actual_targets
    assert not missing, f"Docs reference make targets missing from Makefile: {sorted(missing)}"


def test_contributing_mentions_public_artifacts_and_local_intermediates() -> None:
    docs = read_text(CONTRIBUTING_PATH)

    expected_paths = {
        "assets/parliament_libraries.js",
        "topics/libraries.json",
        "data/_parliament_libraries/manifest.jsonl",
        "data/_parliament_libraries/analysis.jsonl",
        "data/_parliament_libraries/_runs.jsonl",
        "data/_parliament_libraries/probe.log",
        "data/_parliament_libraries/answers.jsonl",
        "analysis_discourse.jsonl",
        "ministry_summary_qa.jsonl",
    }

    missing = {path for path in expected_paths if path not in docs}
    assert not missing, f"CONTRIBUTING.md should mention corpus artifacts: {sorted(missing)}"


def test_named_public_routes_exist() -> None:
    # v2.0.0 content routes served at the repo root + the generated corpus artifact.
    artifact_paths = [
        REPO_ROOT / "index.html",
        REPO_ROOT / "status-quo/index.html",
        REPO_ROOT / "history/index.html",
        REPO_ROOT / "act/index.html",
        REPO_ROOT / "writing/index.html",
        REPO_ROOT / "library/index.html",
        REPO_ROOT / "assets/parliament_libraries.js",
    ]

    missing = [str(path.relative_to(REPO_ROOT)) for path in artifact_paths if not path.exists()]
    assert not missing, f"Documented public routes/artifacts missing from repo: {missing}"
