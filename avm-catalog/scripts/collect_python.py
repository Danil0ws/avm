"""Collect Python releases from python.org API v2.

Note: python.org does not expose SHA-256 checksums for pre-built portable
binaries via its public API. This collector produces metadata-only entries
(no sha256 field) suitable for display; actual installation requires a
separate download flow with manual verification against the official
release page hashes.
"""
import json
import re
import urllib.request
from typing import Any

PYTHON_API_URL = "https://www.python.org/api/v2/downloads/release/?format=json&pre_release=false&limit=100"

OS_MAP = {
    "Windows": "windows",
    "Mac": "macos",
    "Linux": "linux",
    "Source": None,
}


def fetch_releases(url: str = PYTHON_API_URL) -> list[dict[str, Any]]:
    with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310
        return json.loads(resp.read()).get("results", [])


def parse_version(name: str) -> str | None:
    m = re.search(r"(\d+\.\d+\.\d+)", name)
    return m.group(1) if m else None


def collect() -> dict[str, Any]:
    # python.org API does not expose SHA-256 for pre-built binaries; skip until
    # a source with checksums is available.
    return {"tool": "python", "versions": []}


if __name__ == "__main__":
    import sys
    data = collect()
    json.dump(data, sys.stdout, indent=2)
    print()
