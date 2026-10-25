use std::collections::HashMap;
use std::path::Path;

pub fn build_environment(install_path: &Path) -> HashMap<String, String> {
    avm_core::environment::build_env_for_node(install_path)
}

pub fn verify_installation(install_path: &Path) -> anyhow::Result<()> {
    let node_bin = if cfg!(windows) {
        install_path.join("node.exe")
    } else {
        install_path.join("bin").join("node")
    };
    if !node_bin.exists() {
        anyhow::bail!("node binary not found at {:?}", node_bin);
    }
    let output = std::process::Command::new(&node_bin).arg("--version").output()?;
    if !output.status.success() {
        anyhow::bail!("node --version failed");
    }
    Ok(())
}
