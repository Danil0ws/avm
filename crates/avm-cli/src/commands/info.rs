use avm_core::{
    catalog::{find_version_in_catalog, CatalogClient},
    config::GlobalConfig,
    paths,
    version::VersionSpec,
};

pub fn run(spec: &str) -> anyhow::Result<()> {
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

    let version = find_version_in_catalog(&catalog, version_req)
        .ok_or_else(|| anyhow::anyhow!("Version {} not found", version_req))?;

    println!("Tool:    {}", catalog.tool);
    println!("Version: {}", version.version);
    if let Some(d) = &version.release_date {
        println!("Date:    {}", d);
    }
    if let Some(c) = &version.channel {
        println!("Channel: {}", c);
    }
    println!("Artifacts ({}):", version.artifacts.len());
    for a in &version.artifacts {
        println!("  {}/{} {} {}", a.os, a.arch, a.archive_type, &a.sha256[..16]);
    }
    Ok(())
}
