import logging
import time
from typing import Dict, List, Optional

import requests

log = logging.getLogger(__name__)

INDEX_URL = "https://nodejs.org/dist/index.json"
DIST_URL = "https://nodejs.org/dist"
TIMEOUT = 30

FILE_PATTERNS = {
    ("windows", "x64"): lambda v: (f"node-v{v}-win-x64.zip", "zip"),
    ("windows", "arm64"): lambda v: (f"node-v{v}-win-arm64.zip", "zip"),
    ("macos", "x64"): lambda v: (f"node-v{v}-darwin-x64.tar.gz", "tar.gz"),
    ("macos", "arm64"): lambda v: (f"node-v{v}-darwin-arm64.tar.gz", "tar.gz"),
    ("linux", "x64"): lambda v: (f"node-v{v}-linux-x64.tar.xz", "tar.xz"),
    ("linux", "arm64"): lambda v: (f"node-v{v}-linux-arm64.tar.xz", "tar.xz"),
}

FILES_MAP = {
    "win-x64-zip": ("windows", "x64"),
    "win-arm64-zip": ("windows", "arm64"),
    "darwin-x64": ("macos", "x64"),
    "darwin-arm64": ("macos", "arm64"),
    "linux-x64": ("linux", "x64"),
    "linux-arm64": ("linux", "arm64"),
}


def parse_shasums(content: str) -> Dict[str, str]:
    """Parse SHASUMS256.txt content into {filename: sha256}."""
    result = {}
    for line in content.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            sha, filename = parts
            result[filename.strip()] = sha.lower()
    return result


def fetch_shasums(version: str) -> Optional[Dict[str, str]]:
    """Fetch SHASUMS256.txt for a Node.js version."""
    url = f"{DIST_URL}/v{version}/SHASUMS256.txt"
    try:
        r = requests.get(url, timeout=TIMEOUT)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return parse_shasums(r.text)
    except requests.RequestException as e:
        log.warning(f"Failed to fetch SHASUMS for v{version}: {e}")
        return None


def parse_index_entry(entry: dict) -> dict:
    """Parse index.json entry into our version format (without artifacts)."""
    version = entry["version"].lstrip("v")
    lts = entry.get("lts", False)
    channel = "lts" if lts else "current"
    return {
        "version": version,
        "release_date": entry.get("date"),
        "channel": channel,
        "distribution": None,
    }


def build_artifact_list(version: str, files: list) -> list:
    """Build list of expected artifacts based on files field."""
    artifacts = []
    for file_entry in files:
        if file_entry in FILES_MAP:
            os_name, arch = FILES_MAP[file_entry]
            pattern = FILE_PATTERNS.get((os_name, arch))
            if pattern:
                filename, archive_type = pattern(version)
                artifacts.append(
                    {
                        "os": os_name,
                        "arch": arch,
                        "archive_type": archive_type,
                        "filename": filename,
                        "url": f"{DIST_URL}/v{version}/{filename}",
                        "sha256": None,
                        "size_bytes": None,
                    }
                )
    return artifacts


def collect(max_versions: Optional[int] = None) -> list:
    """Collect Node.js versions from official index."""
    log.info("Fetching Node.js index...")
    r = requests.get(INDEX_URL, timeout=TIMEOUT)
    r.raise_for_status()
    index = r.json()
    log.info(f"Found {len(index)} Node.js versions")

    if max_versions:
        index = index[:max_versions]

    versions = []
    for i, entry in enumerate(index):
        parsed = parse_index_entry(entry)
        version = parsed["version"]

        artifacts = build_artifact_list(version, entry.get("files", []))
        if not artifacts:
            log.debug(f"No supported artifacts for v{version}, skipping")
            continue

        log.info(f"Fetching checksums for v{version} ({i + 1}/{len(index)})...")
        shasums = fetch_shasums(version)

        resolved = []
        skip_version = False
        for art in artifacts:
            if shasums and art["filename"] in shasums:
                art["sha256"] = shasums[art["filename"]]
                del art["filename"]
                resolved.append(art)
            elif shasums is None:
                log.warning(f"Cannot get SHASUMS for v{version}")
                skip_version = True
                break
            else:
                log.debug(f"No checksum for {art['filename']} in v{version}")

        if not skip_version and resolved:
            parsed["artifacts"] = resolved
            versions.append(parsed)

        time.sleep(0.1)

    return versions
