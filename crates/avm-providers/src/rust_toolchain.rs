use std::collections::HashMap;
use std::path::Path;

pub fn build_environment(install_path: &Path) -> HashMap<String, String> {
    let mut env = HashMap::new();
    let bin = install_path.join("bin");
    if let Some(path) = std::env::var_os("PATH") {
        let mut paths = std::env::split_paths(&path).collect::<Vec<_>>();
        paths.insert(0, bin);
        if let Ok(new_path) = std::env::join_paths(paths) {
            env.insert("PATH".to_string(), new_path.to_string_lossy().to_string());
        }
    } else {
        env.insert("PATH".to_string(), install_path.join("bin").to_string_lossy().to_string());
    }
    env
}

pub fn verify_installation(install_path: &Path) -> anyhow::Result<()> {
    let rustc_bin = if cfg!(windows) {
        install_path.join("bin").join("rustc.exe")
    } else {
        install_path.join("bin").join("rustc")
    };
    if !rustc_bin.exists() {
        anyhow::bail!("rustc binary not found at {:?}", rustc_bin);
    }
    let output = std::process::Command::new(&rustc_bin).arg("--version").output()?;
    if !output.status.success() {
        anyhow::bail!("rustc --version failed");
    }
    Ok(())
}
