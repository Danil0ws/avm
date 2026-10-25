use avm_core::{
    catalog::CatalogClient,
    config::GlobalConfig,
    installer::install,
    inventory::{InstalledVersion, InstallState, Inventory},
    paths,
    resolver::{current_arch, current_os, resolve_install_plan},
    version::VersionSpec,
};

pub fn run(spec: &str, os: Option<&str>, arch: Option<&str>) -> anyhow::Result<()> {
    let vs = VersionSpec::parse(spec)?;
    let tool = &vs.tool;
    let version_req = vs.version.as_deref().unwrap_or("latest");

    let config = GlobalConfig::load(&paths::global_config_path())?;
    let catalog_url = std::env::var("AVM_CATALOG_URL")
        .unwrap_or_else(|_| config.catalog_url().to_string());

    let local_path = std::env::var("AVM_LOCAL_CATALOG_DIR")
        .ok()
        .map(|d| std::path::PathBuf::from(d).join("tools").join(format!("{}.json", tool)));

    let client = CatalogClient::new(&catalog_url, &paths::cache_dir())?;
    let catalog = match local_path {
        Some(ref p) if p.exists() => client.load_local_catalog(p)?,
        _ => client.fetch_tool_catalog(tool)?,
    };

    let plan = resolve_install_plan(&catalog, tool, version_req, vs.distribution.as_deref(), os, arch)?;

    println!("Install plan:");
    plan.display();
    println!();

    let mut inventory = Inventory::load(&paths::inventory_path())?;
    if inventory.is_installed(tool, &plan.version) {
        println!("Already installed: {} {}", tool, plan.version);
        return Ok(());
    }

    let install_path = install(&plan)?;

    match tool.as_str() {
        "java" => {
            let _ = avm_providers::java::verify_installation(&install_path);
        }
        "node" => {
            let _ = avm_providers::node::verify_installation(&install_path);
        }
        _ => {}
    }

    inventory.add(InstalledVersion {
        tool: tool.clone(),
        version: plan.version.clone(),
        distribution: plan.distribution.clone(),
        os: current_os().to_string(),
        arch: current_arch().to_string(),
        path: install_path.clone(),
        sha256: plan.artifact.sha256.clone(),
        installed_at: chrono::Utc::now().to_rfc3339(),
        state: InstallState::Installed,
    });
    inventory.save(&paths::inventory_path())?;

    println!("\nInstalled {} {} at {}", tool, plan.version, install_path.display());
    println!(
        "Run with: avm exec -- {} --version",
        if tool == "java" { "java" } else { "node" }
    );
    Ok(())
}
