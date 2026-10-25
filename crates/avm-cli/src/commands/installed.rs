use avm_core::{inventory::Inventory, paths};

pub fn run() -> anyhow::Result<()> {
    let inventory = Inventory::load(&paths::inventory_path())?;
    if inventory.versions.is_empty() {
        println!("No versions installed.");
        return Ok(());
    }
    for v in &inventory.versions {
        println!("  {} {} ({:?}) - {}", v.tool, v.version, v.state, v.path.display());
    }
    Ok(())
}
