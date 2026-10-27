#!/usr/bin/env python3
"""Main catalog generation script."""
import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from normalize import normalize_catalog
from validate import validate_catalog

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

SCHEMA_VERSION = 1


def load_previous(path: Path) -> dict:
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except Exception as e:
            log.warning(f"Could not load previous catalog at {path}: {e}")
    return {}


def write_json(data: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.rename(path)
    log.info(f"Written: {path}")


def generate_tool_catalog(tool: str, versions: list, source: str) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "schema_version": SCHEMA_VERSION,
        "source": source,
        "tool": tool,
        "versions": versions,
    }


ALL_TOOLS = ["java", "node", "go", "python", "dotnet", "ruby", "rust", "flutter"]

SOURCE_MAP = {
    "java": "adoptium.net",
    "node": "nodejs.org",
    "go": "go.dev",
    "python": "python.org",
    "dotnet": "dotnet.microsoft.com",
    "ruby": "cache.ruby-lang.org",
    "rust": "static.rust-lang.org",
    "flutter": "storage.googleapis.com/flutter_infra_release",
}


def preserve_existing_sha(versions: list, previous: dict) -> list:
    """Fill missing sha256 values from previous catalog to avoid re-fetching."""
    prev_versions = previous.get("versions", [])
    if not prev_versions:
        return versions
    # Build index: (version, os, arch) -> sha256
    prev_index: dict[tuple, str] = {}
    for v in prev_versions:
        for art in v.get("artifacts", []):
            sha = art.get("sha256", "")
            if sha and re.match(r"^[0-9a-f]{64}$", sha):
                key = (v["version"], art.get("os"), art.get("arch"))
                prev_index[key] = sha
    for v in versions:
        for art in v.get("artifacts", []):
            if art.get("sha256"):
                continue
            key = (v["version"], art.get("os"), art.get("arch"))
            if key in prev_index:
                art["sha256"] = prev_index[key]
    return versions


def build_sha_index(previous: dict) -> dict:
    """Build {(version, os, arch): sha256} from a previous catalog for fast lookup."""
    index: dict[tuple, str] = {}
    for v in previous.get("versions", []):
        for art in v.get("artifacts", []):
            sha = art.get("sha256", "")
            if sha and re.match(r"^[0-9a-f]{64}$", sha):
                index[(v["version"], art.get("os"), art.get("arch"))] = sha
    return index


def collect_tool(tool: str, max_versions=None, previous_sha: dict | None = None) -> list:
    if tool == "java":
        from collect_java import collect
        return collect(previous_sha=previous_sha).get("versions", [])
    elif tool == "node":
        from collect_node import collect
        return collect(max_versions=max_versions)
    elif tool == "go":
        from collect_go import collect
        result = collect()
        return result.get("versions", [])
    elif tool == "python":
        from collect_python import collect
        result = collect()
        return result.get("versions", [])
    elif tool == "dotnet":
        from collect_dotnet import collect
        result = collect()
        return result.get("versions", [])
    elif tool == "ruby":
        from collect_ruby import collect
        result = collect()
        return result.get("versions", [])
    elif tool == "rust":
        from collect_rust_toolchain import collect
        result = collect()
        return result.get("versions", [])
    elif tool == "flutter":
        from collect_flutter import collect
        result = collect()
        return result.get("versions", [])
    else:
        raise ValueError(f"Unknown tool: {tool}")


def main():
    parser = argparse.ArgumentParser(description="Generate AVM catalog")
    parser.add_argument("--output-dir", default="public", help="Output directory")
    parser.add_argument("--previous-dir", default=None, help="Previous catalog directory")
    parser.add_argument("--tool", default="all", choices=["all"] + ALL_TOOLS)
    parser.add_argument("--max-versions", type=int, default=None, help="Limit versions (for testing)")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    schema_path = output_dir / "schema" / "catalog.schema.json"

    tools_to_collect = ALL_TOOLS if args.tool == "all" else [args.tool]

    results = {}
    errors = []

    for tool in tools_to_collect:
        out_path = output_dir / "tools" / f"{tool}.json"
        prev_path = (
            Path(args.previous_dir) / "tools" / f"{tool}.json"
            if args.previous_dir
            else out_path
        )

        try:
            log.info(f"Collecting {tool}...")
            previous = load_previous(prev_path)
            sha_index = build_sha_index(previous)
            versions = collect_tool(tool, max_versions=args.max_versions, previous_sha=sha_index)

            versions = preserve_existing_sha(versions, previous)
            versions = normalize_catalog(versions)
            log.info(f"Collected {len(versions)} {tool} versions")

            catalog = generate_tool_catalog(tool, versions, SOURCE_MAP.get(tool, tool))

            if schema_path.exists():
                errs = validate_catalog(catalog, str(schema_path))
                if errs:
                    raise ValueError(f"Validation errors: {errs}")

            results[tool] = catalog
            write_json(catalog, out_path)

        except Exception as e:
            log.error(f"Failed to collect {tool}: {e}")
            errors.append((tool, str(e)))
            if prev_path.exists() and str(prev_path) != str(out_path):
                try:
                    prev = load_previous(prev_path)
                    if prev:
                        log.warning(f"Using previous catalog for {tool}")
                        write_json(prev, out_path)
                        results[tool] = prev
                except Exception as e2:
                    log.error(f"Could not restore previous {tool} catalog: {e2}")

    index = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "schema_version": SCHEMA_VERSION,
        "tools": [
            {"name": t, "path": f"tools/{t}.json"}
            for t in ALL_TOOLS
            if (output_dir / "tools" / f"{t}.json").exists()
        ],
    }
    write_json(index, output_dir / "index.json")

    catalog_combined = {
        "generated_at": index["generated_at"],
        "schema_version": SCHEMA_VERSION,
        "tools": {t: v for t, v in results.items()},
    }
    write_json(catalog_combined, output_dir / "catalog.json")

    if errors:
        log.warning(f"Completed with {len(errors)} error(s): {[e[0] for e in errors]}")
        sys.exit(1)
    else:
        log.info("Catalog generation complete")


if __name__ == "__main__":
    main()
