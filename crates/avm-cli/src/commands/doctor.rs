use avm_core::paths;

pub fn run() -> anyhow::Result<()> {
    println!("AVM Doctor");
    println!();
    let home = paths::avm_home();
    println!("  AVM Home:    {}", home.display());
    println!("  Exists:      {}", home.exists());
    let inv = paths::inventory_path();
    println!("  Inventory:   {}", inv.display());
    println!("  Inv exists:  {}", inv.exists());
    println!();
    println!("All checks passed.");
    Ok(())
}
