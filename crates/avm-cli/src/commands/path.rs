use avm_core::{inventory::Inventory, paths, version::VersionSpec};

pub fn run(spec: &str) -> anyhow::Result<()> {
    let vs = VersionSpec::parse(spec)?;
    let version = vs.version.as_deref().unwrap_or("");
    let inventory = Inventory::load(&paths::inventory_path())?;
    match inventory.find(&vs.tool, version) {
        Some(v) => println!("{}", v.path.display()),
        None => anyhow::bail!("{} {} not installed", vs.tool, version),
    }
    Ok(())
}
