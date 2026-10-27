"""Collect Flutter SDK releases from the official Flutter releases JSON API.

Source: storage.googleapis.com/flutter_infra_release/releases/releases_{os}.json
SHA-256 is provided inline — no separate fetch needed.
Only 'stable' channel releases are included.
"""
import json
import logging
import urllib.request
from typing import Any

log = logging.getLogger(__name__)

BASE_URL = "https://storage.googleapis.com/flutter_infra_release/releases"
TIMEOUT = 30

# (os_key, our_os, our_arch, arch_tag)
# arch_tag: substring in the archive filename to identify arm64 builds.
# Flutter does not publish Linux arm64 portable binaries in the releases API.
PLATFORMS = [
    ("linux",   "linux",   "x64",   None),     # flutter_linux_X.X.X-stable.tar.xz
    ("macos",   "macos",   "x64",   None),      # flutter_macos_X.X.X-stable.zip (Intel)
    ("macos",   "macos",   "arm64", "arm64"),   # flutter_macos_arm64_X.X.X-stable.zip
    ("windows", "windows", "x64",   None),      # flutter_windows_X.X.X-stable.zip
]


def fetch_releases(os_key: str) -> dict[str, Any]:
    url = f"{BASE_URL}/releases_{os_key}.json"
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:  # noqa: S310
            return json.loads(resp.read())
    except Exception as e:
        log.warning(f"Failed to fetch Flutter releases for {os_key}: {e}")
        return {}


def _is_arm64(archive: str, arch_tag: str | None) -> bool:
    if arch_tag is None:
        return "arm64" not in archive
    return arch_tag in archive


def collect() -> dict[str, Any]:
    versions: dict[str, dict] = {}

    for os_key, our_os, our_arch, arch_tag in PLATFORMS:
        data = fetch_releases(os_key)
        base_url = data.get("base_url", f"{BASE_URL}/")
        releases = data.get("releases", [])

        for rel in releases:
            if rel.get("channel") != "stable":
                continue

            version = rel.get("version", "").lstrip("v")
            archive = rel.get("archive", "")
            sha256 = rel.get("sha256", "")
            release_date = rel.get("release_date")

            if not version or not archive or not sha256:
                continue

            # Match this release to the right arch slot
            if our_arch == "x64" and "arm64" in archive:
                continue
            if our_arch == "arm64" and "arm64" not in archive:
                continue

            ext = "tar.xz" if archive.endswith(".tar.xz") else "zip"
            artifact = {
                "os": our_os,
                "arch": our_arch,
                "archive_type": ext,
                "url": f"{base_url}{archive}",
                "sha256": sha256.lower(),
                "size_bytes": None,
            }

            if version not in versions:
                versions[version] = {
                    "version": version,
                    "release_date": release_date,
                    "lts": False,
                    "distribution": "flutter",
                    "artifacts": [],
                }
            elif release_date and not versions[version].get("release_date"):
                versions[version]["release_date"] = release_date

            versions[version]["artifacts"].append(artifact)

    def sort_key(v: str) -> list[int]:
        parts = v.split(".")
        result = []
        for p in parts:
            try:
                result.append(int(p))
            except ValueError:
                result.append(0)
        return result

    sorted_versions = sorted(versions.values(), key=lambda v: sort_key(v["version"]), reverse=True)
    return {"versions": sorted_versions}
