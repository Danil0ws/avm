use std::collections::HashMap;

use avm_core::{environment, inventory::Inventory, paths, version::VersionSpec};

pub fn run(args: &[String]) -> anyhow::Result<()> {
    if args.is_empty() {
        anyhow::bail!("Usage: avm exec [tool@version] <command> [args...]");
    }

    let (version_spec, cmd_args) = parse_exec_args(args)?;

    let install_path = match &version_spec {
        Some(spec) => {
            let vs = VersionSpec::parse(spec)?;
            let version = vs.version.as_deref().unwrap_or("").to_string();
            let inventory = Inventory::load(&paths::inventory_path())?;
            inventory
                .find(&vs.tool, &version)
                .map(|v| v.path.clone())
                .ok_or_else(|| {
                    anyhow::anyhow!(
                        "{} {} not installed. Run: avm install {}",
                        vs.tool,
                        version,
                        spec
                    )
                })?
        }
        None => anyhow::bail!("No tool specified. Use: avm exec java@21 java -version"),
    };

    if cmd_args.is_empty() {
        anyhow::bail!("No command specified");
    }

    let vs = version_spec
        .as_ref()
        .and_then(|s| VersionSpec::parse(s).ok());
    let env_vars: HashMap<String, String> = match vs.as_ref().map(|v| v.tool.as_str()) {
        Some("java") => environment::build_env_for_java(&install_path),
        Some("node") => environment::build_env_for_node(&install_path),
        Some("go") => avm_providers::go::build_environment(&install_path),
        Some("python") => avm_providers::python::build_environment(&install_path),
        Some("dotnet") => avm_providers::dotnet::build_environment(&install_path),
        Some("php") => avm_providers::php::build_environment(&install_path),
        Some("ruby") => avm_providers::ruby::build_environment(&install_path),
        Some("rust") => avm_providers::rust_toolchain::build_environment(&install_path),
        _ => HashMap::new(),
    };

    let executable = find_executable(
        &install_path,
        &cmd_args[0],
        vs.as_ref().map(|v| v.tool.as_str()).unwrap_or(""),
    )
    .unwrap_or_else(|| std::path::PathBuf::from(&cmd_args[0]));

    let mut cmd = std::process::Command::new(&executable);
    cmd.args(&cmd_args[1..]);
    for (k, v) in &env_vars {
        cmd.env(k, v);
    }

    let status = cmd
        .status()
        .map_err(|e| anyhow::anyhow!("Failed to execute {:?}: {}", executable, e))?;

    std::process::exit(status.code().unwrap_or(1));
}

fn parse_exec_args(args: &[String]) -> anyhow::Result<(Option<String>, Vec<String>)> {
    if args.is_empty() {
        return Ok((None, vec![]));
    }
    if args[0].contains('@') {
        let spec = args[0].clone();
        return Ok((Some(spec), args[1..].to_vec()));
    }
    // Infer tool from command name
    let cmd = &args[0];
    if let Some(tool) = infer_tool(cmd) {
        let inventory = Inventory::load(&paths::inventory_path())?;
        let versions = inventory.list_tool(tool);
        if let Some(latest) = versions.last() {
            let spec = format!("{}@{}", tool, latest.version);
            return Ok((Some(spec), args.to_vec()));
        }
    }
    Ok((None, args.to_vec()))
}

fn infer_tool(cmd: &str) -> Option<&'static str> {
    match cmd {
        "java" | "javac" | "jar" | "javap" | "jshell" => Some("java"),
        "node" | "npm" | "npx" | "corepack" => Some("node"),
        "go" | "gofmt" => Some("go"),
        "python" | "python3" | "pip" | "pip3" => Some("python"),
        "dotnet" => Some("dotnet"),
        "php" | "composer" => Some("php"),
        "ruby" | "gem" | "bundle" | "irb" => Some("ruby"),
        "rustc" | "cargo" | "rustup" | "rustfmt" => Some("rust"),
        _ => None,
    }
}

fn find_executable(
    install_path: &std::path::Path,
    cmd: &str,
    tool: &str,
) -> Option<std::path::PathBuf> {
    let candidates: Vec<std::path::PathBuf> = match (tool, cfg!(windows)) {
        ("java", false) => vec![install_path.join("bin").join(cmd)],
        ("java", true) => vec![
            install_path.join("bin").join(format!("{}.exe", cmd)),
            install_path.join("bin").join(cmd),
        ],
        ("node", false) => vec![
            install_path.join("bin").join(cmd),
            install_path.join(cmd),
        ],
        ("node", true) => vec![
            install_path.join(format!("{}.exe", cmd)),
            install_path.join(cmd),
            install_path.join("bin").join(format!("{}.exe", cmd)),
        ],
        ("dotnet", false) => vec![install_path.join(cmd)],
        ("dotnet", true) => vec![
            install_path.join(format!("{}.exe", cmd)),
            install_path.join(cmd),
        ],
        ("php", true) => vec![
            install_path.join(format!("{}.exe", cmd)),
            install_path.join(cmd),
        ],
        (_, false) => vec![install_path.join("bin").join(cmd)],
        (_, true) => vec![
            install_path.join("bin").join(format!("{}.exe", cmd)),
            install_path.join("bin").join(cmd),
            install_path.join(format!("{}.exe", cmd)),
        ],
    };
    candidates.into_iter().find(|p| p.exists())
}
