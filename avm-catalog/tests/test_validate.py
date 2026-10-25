import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "public", "schema", "catalog.schema.json")

VALID_CATALOG = {
    "schema_version": 1,
    "generated_at": "2025-10-25T00:00:00Z",
    "tool": "node",
    "source": "nodejs.org",
    "versions": [
        {
            "version": "22.14.0",
            "release_date": "2025-02-06",
            "channel": "lts",
            "distribution": None,
            "artifacts": [
                {
                    "os": "linux",
                    "arch": "x64",
                    "archive_type": "tar.xz",
                    "url": "https://nodejs.org/dist/v22.14.0/node-v22.14.0-linux-x64.tar.xz",
                    "sha256": "d4f9f22c71e82ce0e94c7ff9f57c5f2ad1aabd76c76a15e74e9ea07bdbfc3cc1",
                    "size_bytes": None,
                }
            ],
        }
    ],
}


def test_valid_catalog():
    from validate import validate_catalog

    errors = validate_catalog(VALID_CATALOG, SCHEMA_PATH)
    assert errors == [], f"Unexpected errors: {errors}"


def test_invalid_sha256():
    from validate import validate_catalog

    bad = json.loads(json.dumps(VALID_CATALOG))
    bad["versions"][0]["artifacts"][0]["sha256"] = "notahash"
    errors = validate_catalog(bad, SCHEMA_PATH)
    assert len(errors) > 0


def test_non_https_url():
    from validate import validate_catalog

    bad = json.loads(json.dumps(VALID_CATALOG))
    bad["versions"][0]["artifacts"][0]["url"] = "http://insecure.example.com/node.tar.xz"
    errors = validate_catalog(bad, SCHEMA_PATH)
    assert any("https" in e.lower() or "http" in e for e in errors)


def test_duplicate_versions():
    from validate import validate_catalog

    dup = json.loads(json.dumps(VALID_CATALOG))
    dup["versions"].append(dup["versions"][0])
    errors = validate_catalog(dup, SCHEMA_PATH)
    assert any("duplicate" in e.lower() for e in errors)
