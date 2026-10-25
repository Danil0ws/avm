import logging
import time
from typing import Optional

import requests

log = logging.getLogger(__name__)

BASE_URL = "https://api.adoptium.net/v3"
TIMEOUT = 30
OS_MAP = {"windows": "windows", "mac": "macos", "linux": "linux"}
ARCH_MAP = {"x64": "x64", "aarch64": "arm64"}
TARGET_COMBOS = [
    ("windows", "x64"),
    ("mac", "x64"),
    ("mac", "aarch64"),
    ("linux", "x64"),
    ("linux", "aarch64"),
]


def get_available_releases() -> list:
    url = f"{BASE_URL}/info/available_releases"
    r = requests.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    majors = data.get("available_releases", [])
    log.info(f"Available Java major versions: {majors}")
    return majors


def get_releases_for_major(major: int, os: str, arch: str) -> list:
    results = []
    page = 0
    while True:
        url = (
            f"{BASE_URL}/assets/feature_releases/{major}/ga"
            f"?architecture={arch}&image_type=jdk&jvm_impl=hotspot"
            f"&os={os}&page={page}&page_size=20&release_type=ga&vendor=eclipse"
        )
        try:
            r = requests.get(url, timeout=TIMEOUT)
            if r.status_code == 404:
                break
            r.raise_for_status()
            data = r.json()
            if not data:
                break
            results.extend(data)
            if len(data) < 20:
                break
            page += 1
            time.sleep(0.2)
        except requests.RequestException as e:
            log.warning(f"Error fetching Java {major} {os}/{arch}: {e}")
            break
    return results


def parse_release_asset(asset: dict) -> Optional[dict]:
    """Parse a single Adoptium API asset into our catalog format."""
    try:
        binary = asset.get("binary", {})
        package = binary.get("package", {})
        version_data = asset.get("version_data", {})

        os_raw = binary.get("os", "")
        arch_raw = binary.get("architecture", "")

        os_mapped = OS_MAP.get(os_raw)
        arch_mapped = ARCH_MAP.get(arch_raw)
        if not os_mapped or not arch_mapped:
            return None

        url = package.get("link", "")
        sha256 = package.get("checksum", "")
        size = package.get("size")

        if not url or not sha256:
            return None

        name = package.get("name", url.split("/")[-1])
        if name.endswith(".zip"):
            archive_type = "zip"
        elif name.endswith(".tar.gz"):
            archive_type = "tar.gz"
        else:
            archive_type = "tar.gz"

        version_str = version_data.get("semver", asset.get("release_name", ""))
        if version_str.startswith("jdk-"):
            version_str = version_str[4:]

        timestamp = asset.get("timestamp", "")
        release_date = timestamp[:10] if timestamp else None

        return {
            "version": version_str,
            "distribution": "temurin",
            "release_date": release_date,
            "channel": "ga",
            "artifacts": [
                {
                    "os": os_mapped,
                    "arch": arch_mapped,
                    "archive_type": archive_type,
                    "url": url,
                    "sha256": sha256.lower(),
                    "size_bytes": size,
                }
            ],
        }
    except Exception as e:
        log.warning(f"Error parsing asset: {e}")
        return None


def collect() -> list:
    """Collect all Java versions from Adoptium API."""
    majors = get_available_releases()
    versions_by_key = {}

    for major in majors:
        for os, arch in TARGET_COMBOS:
            log.info(f"Fetching Java {major} {os}/{arch}...")
            assets = get_releases_for_major(major, os, arch)
            for asset in assets:
                parsed = parse_release_asset(asset)
                if parsed:
                    art = parsed["artifacts"][0]
                    key = (parsed["version"], art["os"], art["arch"])
                    if key not in versions_by_key:
                        versions_by_key[key] = parsed

    merged = {}
    for parsed in versions_by_key.values():
        v = parsed["version"]
        if v not in merged:
            merged[v] = {
                "version": v,
                "distribution": parsed["distribution"],
                "release_date": parsed["release_date"],
                "channel": parsed["channel"],
                "artifacts": [],
            }
        merged[v]["artifacts"].extend(parsed["artifacts"])

    return list(merged.values())
