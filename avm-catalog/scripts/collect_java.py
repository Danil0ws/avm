import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
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

    versions: list[tuple[str, bool]] = []
    seen: set[str] = set()
    page = 0
    while True:
        try:
            r = requests.get(f"{url}&page={page}", timeout=TIMEOUT)
            r.raise_for_status()
            data = r.json().get("result", [])
            new_count = 0
            for pkg in data:
                v = pkg.get("java_version", "")
                tos = pkg.get("term_of_support", "")
                if v and v not in seen:
                    seen.add(v)
                    versions.append((v, tos == "lts"))
                    new_count += 1
            # Stop when no new versions or page returned less than a full page
            if new_count == 0 or len(data) < 100:
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


def collect(previous_sha: dict | None = None) -> dict:
    """Collect Java versions.

    previous_sha: {(version, os, arch): sha256} — skips fetch for known entries.
    """
    previous_sha = previous_sha or {}
    versions: dict = {}

    # Build all (target, version, is_lts) work items first
    work_items: list[tuple] = []
    for foojay_os, foojay_arch, our_os, our_arch, ms_arch, ext in TARGETS:
        ver_list = fetch_versions(foojay_os, foojay_arch)
        log.info(f"Found {len(ver_list)} versions for {foojay_os}/{foojay_arch}")
        for java_version, is_lts in ver_list:
            ms_os = foojay_os
            filename = f"microsoft-jdk-{java_version}-{ms_os}-{ms_arch}.{ext}"
            url = f"{MS_DL}/{filename}"
            work_items.append((java_version, is_lts, our_os, our_arch, ext, url))

    # Separate known (SHA already cached) from new (need HTTP fetch)
    known: list[tuple] = []
    to_fetch: list[tuple] = []
    for item in work_items:
        java_version, _, our_os, our_arch, _, _ = item
        if (java_version, our_os, our_arch) in previous_sha:
            known.append(item)
        else:
            to_fetch.append(item)

    log.info(f"SHA cache: {len(known)} hits, {len(to_fetch)} to fetch")

    # Parallel SHA fetch for new entries
    fetched_sha: dict[tuple, Optional[str]] = {}

    def _fetch(item: tuple) -> tuple[tuple, Optional[str]]:
        java_version, _, our_os, our_arch, _, url = item
        return (java_version, our_os, our_arch), fetch_sha256(url)

    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(_fetch, item): item for item in to_fetch}
        for future in as_completed(futures):
            key, sha = future.result()
            fetched_sha[key] = sha

    # Assemble versions dict
    for item in work_items:
        java_version, is_lts, our_os, our_arch, ext, url = item
        key = (java_version, our_os, our_arch)
        sha256 = previous_sha.get(key) or fetched_sha.get(key)

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

    def _sort_key(v: dict) -> list[int]:
        clean = v["version"].split("+")[0]
        parts = clean.split(".")
        result = []
        for p in parts:
            try:
                result.append(int(p))
            except ValueError:
                result.append(0)
        return result

    sorted_versions = sorted(versions.values(), key=_sort_key, reverse=True)
    return {"versions": sorted_versions}
