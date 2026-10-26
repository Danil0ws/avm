# AVM Provider Status

Status matrix for runtime providers across AVM components.

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Fully supported (SHA-256 verified artifacts) |
| 🔶 | Metadata-only (no portable binaries or checksum limitation) |
| 🚧 | Planned / in progress |
| ❌ | Not supported |

## Rust CLI Providers (`crates/avm-providers`)

| Tool | `build_environment` | `verify_installation` | Notes |
|------|--------------------|-----------------------|-------|
| `java` | ✅ | ✅ | Sets `JAVA_HOME` + `PATH` |
| `node` | ✅ | ✅ | Prepends `bin/` to `PATH` |
| `go` | ✅ | ✅ | Sets `GOROOT` + `PATH` |
| `python` | ✅ | ✅ | Tries `python3` then `python` |
| `dotnet` | ✅ | ✅ | Sets `DOTNET_ROOT` + `PATH` |
| `php` | ✅ | ✅ | Prepends `bin/` to `PATH` |
| `ruby` | ✅ | ✅ | Prepends `bin/` to `PATH` |
| `rust` | ✅ | ✅ | Prepends `bin/` to `PATH`, checks `rustc` |

## Python Catalog Collectors (`avm-catalog/scripts`)

| Tool | Collector | SHA-256 | Source | Notes |
|------|-----------|---------|--------|-------|
| `java` | `collect_java.py` | ✅ | Adoptium API | Full artifact data |
| `node` | `collect_node.py` | ✅ | nodejs.org | Full artifact data |
| `go` | `collect_go.py` | ✅ | go.dev/dl | Full artifact data |
| `python` | `collect_python.py` | 🔶 | python.org API v2 | No SHA-256 in API; metadata only |
| `dotnet` | `collect_dotnet.py` | 🔶 | Microsoft releases | Uses SHA-512, not SHA-256; metadata only |
| `ruby` | `collect_ruby.py` | ✅ | ruby-lang.org | Source tarballs only (no portable binaries) |
| `rust` | `collect_rust_toolchain.py` | ✅ | static.rust-lang.org | Stable channel; requires `tomli` on Python < 3.11 |
| `php` | 🚧 | 🚧 | windows.php.net / source | No official portable Linux binaries |

## Artifact Availability by Platform

| Tool | Linux x86_64 | Linux arm64 | macOS x86_64 | macOS arm64 | Windows x86_64 |
|------|:---:|:---:|:---:|:---:|:---:|
| java | ✅ | ✅ | ✅ | ✅ | ✅ |
| node | ✅ | ✅ | ✅ | ✅ | ✅ |
| go | ✅ | ✅ | ✅ | ✅ | ✅ |
| python | 🔶 | 🔶 | 🔶 | 🔶 | 🔶 |
| dotnet | 🔶 | 🔶 | 🔶 | 🔶 | 🔶 |
| ruby | source | source | source | source | source |
| rust | ✅ | ✅ | ✅ | ✅ | ✅ |
| php | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 |

## Security Constraints

All providers adhere to AVM's security policy:

- **No sudo/UAC elevation required**
- **HTTPS by default, TLS validated**
- **SHA-256 verified** where available (java, node, go, ruby source, rust)
- **No PATH global modification** — environment is set per-invocation only
- **No remote script execution**
- **No writes outside managed directories** (`$AVM_HOME/runtimes/`)
- **Atomic installs** via temp-dir + rename pattern
- **Path traversal protection** in archive extraction
