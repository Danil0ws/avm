import json
import re
import sys
from typing import List

try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


def validate_catalog(catalog: dict, schema_path: str) -> List[str]:
    """Validate catalog against schema. Returns list of error strings."""
    errors = []

    if HAS_JSONSCHEMA:
        with open(schema_path) as f:
            schema = json.load(f)
        validator = jsonschema.Draft7Validator(schema)
        for err in validator.iter_errors(catalog):
            errors.append(str(err.message))

    versions_seen = set()
    for v in catalog.get("versions", []):
        version = v.get("version", "")
        if version in versions_seen:
            errors.append(f"Duplicate version: {version}")
        versions_seen.add(version)

        for art in v.get("artifacts", []):
            url = art.get("url", "")
            if not url.startswith("https://"):
                errors.append(f"Non-https URL in {version}: {url}")
            sha = art.get("sha256", "")
            if not re.match(r"^[0-9a-f]{64}$", sha.lower()):
                errors.append(f"Invalid sha256 in {version}: {sha}")

    return errors


def main():
    if len(sys.argv) < 3:
        print("Usage: validate.py <catalog.json> <schema.json>")
        sys.exit(1)

    catalog_path = sys.argv[1]
    schema_path = sys.argv[2]

    with open(catalog_path) as f:
        catalog = json.load(f)

    errors = validate_catalog(catalog, schema_path)
    if errors:
        print(f"Validation FAILED ({len(errors)} errors):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        versions = len(catalog.get("versions", []))
        print(f"Validation OK: {versions} versions")


if __name__ == "__main__":
    main()
