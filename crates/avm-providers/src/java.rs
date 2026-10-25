use std::collections::HashMap;
use std::path::Path;

pub fn build_environment(install_path: &Path) -> HashMap<String, String> {
    avm_core::environment::build_env_for_java(install_path)
}

pub fn verify_installation(install_path: &Path) -> anyhow::Result<()> {
    let java_bin = if cfg!(windows) {
        install_path.join("bin").join("java.exe")
    } else {
        install_path.join("bin").join("java")
    };
    if !java_bin.exists() {
        anyhow::bail!("java binary not found at {:?}", java_bin);
    }
    let output = std::process::Command::new(&java_bin).arg("-version").output()?;
    // java -version exits 0 on success; stderr has the version info
    if !output.status.success() {
        anyhow::bail!("java -version failed with status {}", output.status);
    }
    Ok(())
}
