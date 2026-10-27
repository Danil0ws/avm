"""Collect Rust toolchain releases from static.rust-lang.org TOML manifest."""
import json
import re
import urllib.request
from typing import Any

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]

CHANNEL_URLS = {
    "stable": "https://static.rust-lang.org/dist/channel-rust-stable.toml",
    "beta": "https://static.rust-lang.org/dist/channel-rust-beta.toml",
}

OS_MAP = {
    "x86_64-unknown-linux-gnu": ("linux", "x64"),
    "aarch64-unknown-linux-gnu": ("linux", "arm64"),
    "x86_64-apple-darwin": ("macos", "x64"),
    "aarch64-apple-darwin": ("macos", "arm64"),
    "x86_64-pc-windows-msvc": ("windows", "x64"),
    "aarch64-pc-windows-msvc": ("windows", "arm64"),
}


def fetch_channel(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310
        content = resp.read()
    if tomllib is None:
        raise RuntimeError("tomllib/tomli not available; install tomli")
    return tomllib.loads(content.decode())


def parse_channel(data: dict[str, Any], channel: str) -> list[dict[str, Any]]:
    pkg = data.get("pkg", {}).get("rust", {})
    version = pkg.get("version", "")
    m = re.match(r"(\d+\.\d+\.\d+)", version)
    if not m:
        return []
    version_str = m.group(1)
    if channel != "stable":
        version_str = f"{version_str}-{channel}"

    artifacts = []
    for target, info in pkg.get("target", {}).items():
        if not info.get("available"):
            continue
        if target not in OS_MAP:
            continue
        os_name, arch = OS_MAP[target]
        use_xz = bool(info.get("xz_url"))
        url = info.get("xz_url") or info.get("url", "")
        sha256 = info.get("xz_hash") or info.get("hash", "")
        if not (url and sha256):
            continue
        archive_type = "tar.xz" if use_xz else "tar.gz"
        artifacts.append({
            "url": url,
            "sha256": sha256,
            "os": os_name,
            "arch": arch,
            "archive_type": archive_type,
        })

    if not artifacts:
        return []
    return [{"version": version_str, "artifacts": artifacts}]


def collect(channels: list[str] | None = None) -> dict[str, Any]:
    if channels is None:
        channels = ["stable"]
    versions: list[dict[str, Any]] = []
    for ch in channels:
        url = CHANNEL_URLS.get(ch)
        if not url:
            continue
        try:
            data = fetch_channel(url)
            versions.extend(parse_channel(data, ch))
        except Exception as e:
            print(f"Warning: failed to fetch {ch} channel: {e}", flush=True)
    return {"tool": "rust", "versions": versions}


if __name__ == "__main__":
    import sys
    data = collect()
    json.dump(data, sys.stdout, indent=2)
    print()
