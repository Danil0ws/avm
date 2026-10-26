"""Tests for collect_go.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from collect_go import parse_releases  # noqa: E402

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "go_releases_excerpt.json"


@pytest.fixture
def raw_releases():
    with open(FIXTURE_PATH) as f:
        return json.load(f)


def test_parse_stable_versions(raw_releases):
    versions = parse_releases(raw_releases)
    version_strs = [v["version"] for v in versions]
    assert "1.22.3" in version_strs
    assert "1.21.10" in version_strs


def test_skips_unstable(raw_releases):
    versions = parse_releases(raw_releases)
    version_strs = [v["version"] for v in versions]
    # rc/beta should be filtered out
    assert not any("rc" in v for v in version_strs)


def test_artifact_os_mapping(raw_releases):
    versions = parse_releases(raw_releases)
    v = next(v for v in versions if v["version"] == "1.22.3")
    oses = {a["os"] for a in v["artifacts"]}
    assert "linux" in oses
    assert "macos" in oses
    assert "windows" in oses


def test_artifact_arch_mapping(raw_releases):
    versions = parse_releases(raw_releases)
    v = next(v for v in versions if v["version"] == "1.22.3")
    archs = {a["arch"] for a in v["artifacts"]}
    assert "x86_64" in archs
    assert "aarch64" in archs


def test_skips_source_kind(raw_releases):
    versions = parse_releases(raw_releases)
    v = next(v for v in versions if v["version"] == "1.22.3")
    # source kind entries (no os/arch) should be filtered
    assert all(a["os"] != "" for a in v["artifacts"])


def test_sha256_present(raw_releases):
    versions = parse_releases(raw_releases)
    v = next(v for v in versions if v["version"] == "1.22.3")
    for artifact in v["artifacts"]:
        assert artifact["sha256"], f"Missing sha256 for {artifact}"


def test_url_format(raw_releases):
    versions = parse_releases(raw_releases)
    v = next(v for v in versions if v["version"] == "1.22.3")
    for artifact in v["artifacts"]:
        assert artifact["url"].startswith("https://dl.google.com/go/")
