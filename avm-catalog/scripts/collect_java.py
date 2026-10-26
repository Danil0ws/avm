import logging
import time
from typing import Optional

import requests

log = logging.getLogger(__name__)

BASE_URL = "https://api.foojay.io/disco/v3.0"
MS_DL = "https://aka.ms/download-jdk"
TIMEOUT = 30

# (foojay_os, foojay_arch) -> (our_os, our_arch, ms_os_name, ms_arch_name, ext)
TARGETS = [
    ("macos",   "x64",     "macos",   "x64",     "x64",     "tar.gz"),
    ("macos",   "aarch64", "macos",   "arm64",   "aarch64", "tar.gz"),
    ("windows", "x64",     "windows", "x64",     "x64",     "zip"),
    ("windows", "aarch64", "windows", "arm64",   "aarch64", "zip"),
    ("linux",   "x64",     "linux",   "x64",     "x64",     "tar.gz"),
    ("linux",   "aarch64", "linux",   "arm64",   "aarch64", "tar.gz"),
]


def fetch_versions(foojay_os: str, foojay_arch: str) -> list[str]:
    """Return list of java_version strings from Foojay (metadata only, no per-pkg calls)."""
    url = (
        f"{BASE_URL}/packages"
        f"?distribution=microsoft&package_type=jdk&release_status=ga"
        f"&directly_downloadable=true&operating_system={foojay_os}&architecture={foojay_arch}"
        f"&archive_type=tar.gz&page_size=100"
    )
    if foojay_os == "windows":
        url = url.replace("archive_type=tar.gz", "archive_type=zip")

    versions = []
    page = 0
    while True:
        try:
            r = requests.get(f"{url}&page={page}", timeout=TIMEOUT)
            r.raise_for_status()
            data = r.json().get("result", [])
            for pkg in data:
                v = pkg.get("java_version", "")
                tos = pkg.get("term_of_support", "")
                if v:
                    versions.append((v, tos == "lts"))
            if len(data) < 100:
                break
            page += 1
            time.sleep(0.1)
        except requests.RequestException as e:
            log.warning(f"Error fetching versions for {foojay_os}/{foojay_arch}: {e}")
            break
    return versions


def fetch_sha256(url: str) -> Optional[str]:
    try:
        r = requests.get(f"{url}.sha256sum.txt", timeout=TIMEOUT)
        if r.status_code == 200:
            token = r.text.strip().split()[0]
            return token.lower() if len(token) == 64 else None
    except Exception:
        pass
    return None


def collect() -> dict:
    versions: dict = {}

    for foojay_os, foojay_arch, our_os, our_arch, ms_arch, ext in TARGETS:
        ver_list = fetch_versions(foojay_os, foojay_arch)
        log.info(f"Found {len(ver_list)} versions for {foojay_os}/{foojay_arch}")

        for java_version, is_lts in ver_list:
            ms_os = foojay_os  # "macos", "linux", "windows" match Microsoft naming
            filename = f"microsoft-jdk-{java_version}-{ms_os}-{ms_arch}.{ext}"
            url = f"{MS_DL}/{filename}"
            sha256 = fetch_sha256(url)

            artifact = {
                "os": our_os,
                "arch": our_arch,
                "archive_type": ext,
                "url": url,
                "sha256": sha256,
                "size_bytes": None,
            }

            if java_version not in versions:
                versions[java_version] = {
                    "version": java_version,
                    "release_date": None,
                    "lts": is_lts,
                    "distribution": "microsoft",
                    "artifacts": [],
                }

            versions[java_version]["artifacts"].append(artifact)
            time.sleep(0.05)

    sorted_versions = sorted(
        versions.values(),
        key=lambda v: [int(x) for x in v["version"].split(".")],
        reverse=True,
    )
    return {"versions": sorted_versions}
