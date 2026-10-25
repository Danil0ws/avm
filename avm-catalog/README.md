# AVM Catalog

Automated catalog of Java and Node.js runtime versions, published as static JSON via GitHub Pages.

## Structure

```
public/
  index.json          — catalog index
  catalog.json        — combined catalog
  tools/
    java.json         — Java/Temurin versions
    node.json         — Node.js versions
  schema/
    catalog.schema.json
scripts/
  collect_java.py     — fetches from api.adoptium.net
  collect_node.py     — fetches from nodejs.org/dist
  normalize.py        — version sorting/deduplication
  validate.py         — schema validation
  generate_catalog.py — main entry point
```

## Running locally

```bash
pip install -r requirements.txt

# Collect Node.js (limit to 5 versions for speed)
python scripts/generate_catalog.py --tool node --max-versions 5

# Collect Java
python scripts/generate_catalog.py --tool java

# Validate
python scripts/validate.py public/tools/node.json public/schema/catalog.schema.json
```

## Tests

```bash
python -m pytest tests/ -v
```

## GitHub Pages setup

1. Go to repository Settings → Pages
2. Set source to "GitHub Actions"
3. Run the "Refresh Catalog" workflow manually
4. Access at `https://<username>.github.io/<repo>/index.json`

## Catalog URL for AVM CLI

```bash
export AVM_CATALOG_URL=https://<username>.github.io/<repo>
avm available node
```
