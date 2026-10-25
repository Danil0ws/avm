pub fn run() -> anyhow::Result<()> {
    println!("AVM System Information");
    println!("  Version:  {}", env!("CARGO_PKG_VERSION"));
    println!("  OS:       {}", avm_core::resolver::current_os());
    println!("  Arch:     {}", avm_core::resolver::current_arch());
    println!("  AVM Home: {}", avm_core::paths::avm_home().display());
    Ok(())
}
