"""Hexagonal-architecture compliance gates for the site (SCOPE.md §4, ROADMAP v2.0.0).

These are fast, dependency-free static checks. They run in the pre-commit hook
(scripts/hooks/pre-commit.local) and in CI (.github/workflows/checks.yml) so
non-compliant code cannot be committed or merged.

The invariants:
  - the domain core (assets/core/domain.js) is PURE — no DOM, no browser state;
  - page content is data-driven through ports — the footer channel list lives
    once in CHANNELS (data.js), is read via ContentPort.channels(), and rendered
    by core/footer.js; it is NEVER hand-written as markup in the HTML pages;
  - any page that shows the channel row loads the core chain (ports + footer).
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "assets" / "core"
PAGES = [
    "index.html", "status-quo/index.html", "history/index.html",
    "act/index.html", "library/index.html",
]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_domain_core_is_pure() -> None:
    """domain.js must hold pure functions only — no DOM, styling, or browser state."""
    src = (CORE / "domain.js").read_text(encoding="utf-8")
    forbidden = ["document", "getComputedStyle", ".innerHTML",
                 "querySelector", "localStorage", "addEventListener"]
    hits = [tok for tok in forbidden if tok in src]
    assert not hits, f"assets/core/domain.js must stay pure — found DOM/browser usage: {hits}"


def test_no_inline_channel_markup_in_pages() -> None:
    """The social-channel icons must be data-driven, never hand-written in HTML."""
    offenders = [p for p in PAGES if 'class="channel"' in _read(p)]
    assert not offenders, (
        "inline channel markup found — channels come from CHANNELS via "
        f"ContentPort + core/footer.js, not hardcoded HTML: {offenders}"
    )


def test_every_page_has_the_data_channels_slot() -> None:
    missing = [p for p in PAGES if "data-channels" not in _read(p)]
    assert not missing, f"pages missing the [data-channels] render slot: {missing}"


def test_channels_have_a_single_source_in_data() -> None:
    data = _read("assets/data.js")
    assert re.search(r"\bconst\s+CHANNELS\s*=", data), \
        "CHANNELS must be defined once in assets/data.js (the single source)"


def test_channels_exposed_through_content_port() -> None:
    ports = (CORE / "ports.js").read_text(encoding="utf-8")
    assert re.search(r"channels\s*:\s*function", ports), \
        "ContentPort must expose channels() — pages read content only through ports"


def test_footer_adapter_renders_via_the_port() -> None:
    footer = (CORE / "footer.js").read_text(encoding="utf-8")
    assert "content.channels()" in footer, \
        "core/footer.js must render channels through ContentPort.channels(), not a baked list"


def test_channel_pages_load_the_core_chain() -> None:
    """A page that renders channels must load ports + the footer adapter."""
    for p in PAGES:
        src = _read(p)
        if "data-channels" in src:
            for asset in ("core/ports.js", "core/footer.js"):
                assert asset in src, f"{p} renders channels but does not load assets/{asset}"
