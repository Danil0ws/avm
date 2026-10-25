use avm_core::{config::GlobalConfig, paths};

pub fn status() -> anyhow::Result<()> {
    let config = GlobalConfig::load(&paths::global_config_path())?;
    println!("Catalog URL: {}", config.catalog_url());
    println!("Cache dir:   {}", paths::cache_dir().display());
    Ok(())
}

pub fn refresh() -> anyhow::Result<()> {
    println!("Refreshing catalog... (not yet implemented for offline PoC)");
    println!("Set AVM_CATALOG_URL env or catalog_url in config to point to your catalog.");
    Ok(())
}
