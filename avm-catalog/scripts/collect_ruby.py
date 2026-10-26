"""Collect Ruby releases from cache.ruby-lang.org index.

Source tarballs with SHA-256 checksums are available. Pre-built binaries
for all platforms are not universally available from official sources, so
this collector records source releases only (metadata).
"""
import json
import re
import urllib.request
from typing import Any

RUBY_INDEX_URL = "https://cache.ruby-lang.org/pub/ruby/index.txt"


def fetch_index(url: str = RUBY_INDEX_URL) -> str:
    with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310
        return resp.read().decode()


def parse_index(text: str) -> list[dict[str, Any]]:
    versions: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("name"):
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        filename, url, size, sha256 = parts[0], parts[1], parts[2], parts[3]
        # Only stable tarballs (.tar.gz), skip dev/preview/rc
        if not filename.endswith(".tar.gz"):
            continue
        m = re.match(r"ruby-(\d+\.\d+\.\d+)\.tar\.gz", filename)
        if not m:
            continue
        version = m.group(1)
        if version in seen:
            continue
        # Skip pre-release versions (e.g. 0.x or very old)
        major = int(version.split(".")[0])
        if major < 2:
            continue
        seen.add(version)
        artifact = {
            "url": url,
            "sha256": sha256,
            "os": "source",
            "arch": "source",
            "filename": filename,
        }
        versions.append({"version": version, "artifacts": [artifact]})
    return versions


def collect() -> dict[str, Any]:
    text = fetch_index()
    versions = parse_index(text)
    return {"tool": "ruby", "versions": versions}


if __name__ == "__main__":
    import sys
    data = collect()
    json.dump(data, sys.stdout, indent=2)
    print()
