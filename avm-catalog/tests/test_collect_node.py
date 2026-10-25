import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def test_parse_node_index():
    from collect_node import build_artifact_list, parse_index_entry

    with open(os.path.join(FIXTURES, "node_index_excerpt.json")) as f:
        data = json.load(f)
    entry = data[0]  # v22.14.0
    result = parse_index_entry(entry)
    assert result["version"] == "22.14.0"
    assert result["channel"] == "lts"
    artifacts = build_artifact_list(result["version"], entry["files"])
    assert any(a["os"] == "linux" and a["arch"] == "x64" for a in artifacts)
    assert any(a["os"] == "macos" and a["arch"] == "arm64" for a in artifacts)
    assert any(a["os"] == "windows" and a["arch"] == "x64" for a in artifacts)


def test_parse_shasums():
    from collect_node import parse_shasums

    with open(os.path.join(FIXTURES, "node_shasums_excerpt.txt")) as f:
        content = f.read()
    shasums = parse_shasums(content)
    assert (
        shasums["node-v22.14.0-linux-x64.tar.xz"]
        == "d4f9f22c71e82ce0e94c7ff9f57c5f2ad1aabd76c76a15e74e9ea07bdbfc3cc1"
    )
    assert (
        shasums["node-v22.14.0-win-x64.zip"]
        == "e4f9f22c71e82ce0e94c7ff9f57c5f2ad1aabd76c76a15e74e9ea07bdbfc3cc2"
    )


def test_parse_node_current_channel():
    from collect_node import parse_index_entry

    entry = {
        "version": "v23.0.0",
        "date": "2024-10-01",
        "files": ["linux-x64"],
        "lts": False,
    }
    result = parse_index_entry(entry)
    assert result["channel"] == "current"
    assert result["version"] == "23.0.0"


def test_build_artifact_urls():
    from collect_node import build_artifact_list

    arts = build_artifact_list("22.14.0", ["linux-x64", "darwin-arm64"])
    linux = next(a for a in arts if a["os"] == "linux" and a["arch"] == "x64")
    assert linux["url"] == "https://nodejs.org/dist/v22.14.0/node-v22.14.0-linux-x64.tar.xz"
    assert linux["archive_type"] == "tar.xz"
    mac = next(a for a in arts if a["os"] == "macos" and a["arch"] == "arm64")
    assert mac["archive_type"] == "tar.gz"
