"""Collect Go releases from go.dev/dl API."""
import json
import urllib.request
import urllib.error
from typing import Any

GO_DL_URL = "https://go.dev/dl/?mode=json&include=all"

OS_MAP = {
    "linux": "linux",
    "darwin": "macos",
    "windows": "windows",
}

ARCH_MAP = {
    "amd64": "x64",
    "arm64": "arm64",
}


def fetch_releases(url: str = GO_DL_URL) -> list[dict[str, Any]]:
    with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310
        return json.loads(resp.read())


def parse_releases(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    versions: list[dict[str, Any]] = []
    for release in raw:
        version = release.get("version", "")
        if not version.startswith("go"):
            continue
        version_str = version[2:]  # strip "go" prefix
        if not release.get("stable", False):
            continue

        artifacts = []
        for f in release.get("files", []):
            if f.get("kind") != "archive":
                continue
            goos = f.get("os", "")
            goarch = f.get("arch", "")
            sha256 = f.get("sha256", "")
            filename = f.get("filename", "")
            if not (goos and goarch and sha256 and filename):
                continue
            mapped_os = OS_MAP.get(goos)
            mapped_arch = ARCH_MAP.get(goarch)
            if not (mapped_os and mapped_arch):
                continue
            archive_type = "zip" if mapped_os == "windows" else "tar.gz"
            artifacts.append({
                "url": f"https://dl.google.com/go/{filename}",
                "sha256": sha256,
                "os": mapped_os,
                "arch": mapped_arch,
                "archive_type": archive_type,
            })

        if artifacts:
            versions.append({"version": version_str, "artifacts": artifacts})

    return versions


def collect() -> dict[str, Any]:
    raw = fetch_releases()
    versions = parse_releases(raw)
    return {"tool": "go", "versions": versions}


if __name__ == "__main__":
    import sys
    data = collect()
    json.dump(data, sys.stdout, indent=2)
    print()
