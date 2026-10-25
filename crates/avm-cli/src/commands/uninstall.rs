use avm_core::{inventory::Inventory, paths, version::VersionSpec};

pub fn run(spec: &str) -> anyhow::Result<()> {
    let vs = VersionSpec::parse(spec)?;
    let version = vs.version.as_deref().unwrap_or("").to_string();
    let mut inventory = Inventory::load(&paths::inventory_path())?;
    match inventory.find(&vs.tool, &version).map(|v| v.path.clone()) {
        Some(path) => {
            println!("Removing {} {}...", vs.tool, version);
            if path.exists() {
                std::fs::remove_dir_all(&path)?;
            }
            inventory.remove(&vs.tool, &version);
            inventory.save(&paths::inventory_path())?;
            println!("Uninstalled {} {}", vs.tool, version);
        }
        None => anyhow::bail!("{} {} not installed", vs.tool, version),
    }
    Ok(())
}
