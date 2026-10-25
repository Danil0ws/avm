# AVM — All Version Manager

[![CI](https://github.com/danil0ws/avm/actions/workflows/ci.yml/badge.svg)](https://github.com/danil0ws/avm/actions/workflows/ci.yml)
[![Release](https://github.com/danil0ws/avm/actions/workflows/release.yml/badge.svg)](https://github.com/danil0ws/avm/actions/workflows/release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Manage Java and Node.js versions without relying on other version managers.  
No nvm, asdf, mise, or any other tool underneath — AVM owns the full lifecycle.

**[📖 Documentation](https://danil0ws.github.io/avm)** · **[Releases](https://github.com/danil0ws/avm/releases)** · **[Catalog](https://danil0ws.github.io/avm/tools/node.json)**

---

## Install

### Linux (recommended — via [Pangeia](https://github.com/danil0ws/pangeia))

```sh
# Install Pangeia first
curl -fsSL https://raw.githubusercontent.com/danil0ws/pangeia/main/install.sh | sh

# Then install AVM
pangeia install avm
```

### Linux / macOS — shell script

```sh
curl -fsSL https://raw.githubusercontent.com/danil0ws/avm/main/install.sh | sh
```

### macOS — Homebrew

```sh
brew tap danil0ws/tap
brew install avm
```

### Windows — winget

```
winget install danil0ws.avm
```

### Windows — PowerShell

```powershell
irm https://raw.githubusercontent.com/danil0ws/avm/main/install.ps1 | iex
```

### From source (Rust 1.75+)

```sh
cargo install avm-cli
```

---

## Quick Start

```sh
# List available versions
avm available node --lts
avm available java

# Install
avm install node@22.14.0
avm install java@21

# Run
avm exec -- node@22.14.0 node --version
avm exec -- java@21 java -version

# Manage
avm installed
avm uninstall node@20.0.0
```

## Project config (`avm.toml`)

```toml
[tools.java]
version = "21"
distribution = "temurin"

[tools.node]
version = "22.14.0"
```

---

## Supported platforms

| OS      | x64 | ARM64   |
|---------|-----|---------|
| Linux   | ✅  | ✅      |
| macOS   | ✅  | ✅      |
| Windows | ✅  | planned |

## Supported runtimes

| Tool    | Source                                    | Distributions   |
|---------|-------------------------------------------|-----------------|
| Java    | [Adoptium API](https://api.adoptium.net/) | Eclipse Temurin |
| Node.js | [nodejs.org](https://nodejs.org/dist/)    | Official        |

---

## Repository layout

```
avm/
├── crates/
│   ├── avm-core/          # core library (download, verify, install, catalog)
│   ├── avm-cli/           # CLI binary
│   └── avm-providers/     # Java and Node.js providers
├── avm-catalog/
│   ├── scripts/           # Python collectors and validators
│   ├── public/            # Generated JSON catalog (GitHub Pages)
│   └── tests/             # Catalog unit tests
├── install.sh             # Linux/macOS installer
├── install.ps1            # Windows installer
└── .github/workflows/
    ├── ci.yml             # Build + test on all platforms
    ├── release.yml        # Build release binaries
    └── catalog.yml        # Refresh catalog every 6h
```

---

## Development

```sh
# Build
cargo build

# Test
cargo test

# Run
cargo run -- --help

# Run catalog collectors locally
cd avm-catalog
pip install -r requirements.txt
python scripts/generate_catalog.py --tool node --max-versions 5

# Test with local catalog
AVM_LOCAL_CATALOG_DIR=avm-catalog/public cargo run -- available node
```

---

## License

MIT © [danil0ws](https://github.com/danil0ws)
