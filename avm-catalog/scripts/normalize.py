import re
from typing import List


def normalize_version(v: str) -> str:
    """Strip leading 'v' and normalize."""
    return v.lstrip("v").strip()


def sort_versions(versions: list) -> list:
    """Sort versions newest first using semver-like comparison."""

    def sort_key(v):
        ver = v["version"]
        clean = re.split(r"[+]", ver)[0]
        parts = re.split(r"[.\-]", clean)
        result = []
        for p in parts:
            try:
                result.append(int(p))
            except ValueError:
                result.append(0)
        return result

    return sorted(versions, key=sort_key, reverse=True)


def deduplicate(versions: list) -> list:
    """Remove duplicate version entries."""
    seen = set()
    result = []
    for v in versions:
        key = v["version"]
        if key not in seen:
            seen.add(key)
            result.append(v)
    return result


def validate_artifact(art: dict) -> List[str]:
    errors = []
    if not art.get("url", "").startswith("https://"):
        errors.append(f"URL must be https: {art.get('url')}")
    sha = art.get("sha256", "")
    if not re.match(r"^[0-9a-f]{64}$", sha):
        errors.append(f"Invalid sha256: {sha[:20]}...")
    return errors


def normalize_catalog(versions: list) -> list:
    """Normalize and validate a list of version entries."""
    for v in versions:
        v["version"] = normalize_version(v["version"])
        for art in v.get("artifacts", []):
            sha = art.get("sha256")
            art["sha256"] = sha.lower() if sha else None
    # Drop artifacts with no valid SHA-256, then versions with no artifacts left
    for v in versions:
        v["artifacts"] = [
            art for art in v.get("artifacts", [])
            if art.get("sha256") and re.match(r"^[0-9a-f]{64}$", art["sha256"])
        ]
    versions = [v for v in versions if v.get("artifacts")]
    versions = deduplicate(sort_versions(versions))
    return versions
