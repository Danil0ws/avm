"""Collect .NET releases from Microsoft releases-index.json.

Note: Microsoft's releases API provides SHA-512 checksums, not SHA-256.
This collector produces metadata-only entries without sha256 fields.
"""
import json
import urllib.request
from typing import Any

RELEASES_INDEX_URL = "https://dotnetcli.azureedge.net/dotnet/release-metadata/releases-index.json"

OS_MAP = {
    "linux": "linux",
    "osx": "macos",
    "win": "windows",
}

ARCH_MAP = {
    "x64": "x86_64",
    "arm64": "aarch64",
    "x86": "x86",
}


def fetch_index(url: str = RELEASES_INDEX_URL) -> list[dict[str, Any]]:
    with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310
        data = json.loads(resp.read())
    return data.get("releases-index", [])


def fetch_channel(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310
        return json.loads(resp.read())


def collect(max_channels: int = 5) -> dict[str, Any]:
    index = fetch_index()
    versions: list[dict[str, Any]] = []
    for channel in index[:max_channels]:
        support_phase = channel.get("support-phase", "")
        if support_phase == "eol":
            continue
        releases_url = channel.get("releases.json")
        if not releases_url:
            continue
        try:
            channel_data = fetch_channel(releases_url)
        except Exception:
            continue
        for release in channel_data.get("releases", [])[:3]:
            version = release.get("release-version", "")
            if not version:
                continue
            versions.append({"version": version, "artifacts": []})
    return {"tool": "dotnet", "versions": versions}


if __name__ == "__main__":
    import sys
    data = collect()
    json.dump(data, sys.stdout, indent=2)
    print()
