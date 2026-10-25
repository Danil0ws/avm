import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def test_parse_java_api_response():
    from collect_java import parse_release_asset

    with open(os.path.join(FIXTURES, "java_api_response.json")) as f:
        data = json.load(f)
    result = parse_release_asset(data[0])
    assert result is not None
    assert result["version"] == "21.0.3+9"
    assert result["distribution"] == "temurin"
    assert len(result["artifacts"]) == 1
    art = result["artifacts"][0]
    assert art["os"] == "linux"
    assert art["arch"] == "x64"
    assert art["archive_type"] == "tar.gz"
    assert len(art["sha256"]) == 64
    assert art["url"].startswith("https://")


def test_parse_missing_checksum():
    from collect_java import parse_release_asset

    asset = {
        "binary": {
            "os": "linux",
            "architecture": "x64",
            "package": {"link": "https://example.com/jdk.tar.gz", "checksum": ""},
        },
        "version_data": {"semver": "21.0.3+9"},
        "timestamp": "2024-04-16T05:07:55Z",
    }
    result = parse_release_asset(asset)
    assert result is None


def test_parse_unknown_os():
    from collect_java import parse_release_asset

    with open(os.path.join(FIXTURES, "java_api_response.json")) as f:
        data = json.load(f)
    modified = dict(data[0])
    modified["binary"] = dict(data[0]["binary"])
    modified["binary"]["os"] = "solaris"
    result = parse_release_asset(modified)
    assert result is None
