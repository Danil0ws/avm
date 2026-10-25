use avm_core::{catalog::CatalogClient, config::GlobalConfig, paths};

pub fn run(
    tool: &str,
    all: bool,
    lts: bool,
    _distribution: Option<&str>,
    os: Option<&str>,
    arch: Option<&str>,
) -> anyhow::Result<()> {
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

    let os_owned: String;
    let target_os = match os {
        Some(v) => v,
        None => { os_owned = avm_core::resolver::current_os().to_string(); os_owned.as_str() }
    };
    let arch_owned: String;
    let target_arch = match arch {
        Some(v) => v,
        None => { arch_owned = avm_core::resolver::current_arch().to_string(); arch_owned.as_str() }
    };
    let max = if all { usize::MAX } else { 10 };
    let mut shown = 0;

    for version in &catalog.versions {
        if shown >= max {
            break;
        }
        if lts && version.channel.as_deref() != Some("lts") {
            continue;
        }
        let has_artifact = version
            .artifacts
            .iter()
            .any(|a| a.os == target_os && a.arch == target_arch);
        if !has_artifact {
            continue;
        }
        let channel = version.channel.as_deref().unwrap_or("unknown");
        let date = version.release_date.as_deref().unwrap_or("?");
        println!("  {} [{}] {}", version.version, channel, date);
        shown += 1;
    }

    if shown == 0 {
        println!("  No versions found for {}/{}", target_os, target_arch);
    }
    Ok(())
}
