from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
MAKEFILE_PATH = REPO_ROOT / "Makefile"
REQUIREMENTS_PATH = REPO_ROOT / "requirements.txt"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def requirement_ref(requirements: str, package: str) -> str | None:
    match = re.search(
        rf"{re.escape(package)}\[http,pdf\]\s+@\s+git\+https://github\.com/CommonerLLP/"
        rf"{re.escape(package)}\.git@([^\s]+)",
        requirements,
    )
    return match.group(1) if match else None


def test_readme_pinned_refresh_refs_match_requirements() -> None:
    readme = read_text(README_PATH)
    requirements = read_text(REQUIREMENTS_PATH)

    commoner_ref = requirement_ref(requirements, "commoner-probe")
    sansad_ref = requirement_ref(requirements, "sansad-semantic-crawler")

    assert commoner_ref, "requirements.txt should pin commoner-probe by ref"
    assert sansad_ref, "requirements.txt should pin sansad-semantic-crawler by ref"
    assert re.search(rf"pinned at\s+`{re.escape(commoner_ref)}`", readme)
    assert re.search(rf"pinned at\s+`{re.escape(sansad_ref)}`", readme)


def test_makefile_keeps_acquisition_and_analysis_split() -> None:
    makefile = read_text(MAKEFILE_PATH)

    assert "$(PROBE) sansad" in makefile
    assert "$(PROBE) committees" in makefile
    assert "sansad_semantic_crawler parse" in makefile
    assert "sansad_semantic_crawler export" in makefile
    assert "sansad_semantic_crawler analyse-discourse" in makefile
    assert "sansad_semantic_crawler analyse-ministry" in makefile


def test_readme_make_commands_exist_in_makefile() -> None:
    readme = read_text(README_PATH)
    makefile = read_text(MAKEFILE_PATH)

    documented_targets = set(re.findall(r"make ([a-z0-9-]+)", readme))
    actual_targets = set(
        match.group(1)
        for match in re.finditer(r"^([a-z0-9-]+):", makefile, flags=re.MULTILINE)
        if not match.group(1).startswith(".")
    )

    missing = documented_targets - actual_targets
    assert not missing, f"README documents make targets missing from Makefile: {sorted(missing)}"


def test_readme_mentions_public_artifacts_and_local_intermediates() -> None:
    readme = read_text(README_PATH)

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

    missing = {path for path in expected_paths if path not in readme}
    assert not missing, f"README should mention artifacts: {sorted(missing)}"


def test_readme_named_public_artifacts_exist() -> None:
    artifact_paths = [
        REPO_ROOT / "index.html",
        REPO_ROOT / "data/index.html",
        REPO_ROOT / "inequality/index.html",
        REPO_ROOT / "assets/parliament_libraries.js",
        REPO_ROOT / "topics/libraries.json",
    ]

    missing = [str(path.relative_to(REPO_ROOT)) for path in artifact_paths if not path.exists()]
    assert not missing, f"Documented public artifacts missing from repo: {missing}"
