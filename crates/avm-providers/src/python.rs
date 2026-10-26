use std::collections::HashMap;
use std::path::Path;

pub fn build_environment(install_path: &Path) -> HashMap<String, String> {
    let mut env = HashMap::new();
    let bin = if cfg!(windows) {
        install_path.to_path_buf()
    } else {
        install_path.join("bin")
    };
    if let Some(path) = std::env::var_os("PATH") {
        let mut paths = std::env::split_paths(&path).collect::<Vec<_>>();
        paths.insert(0, bin);
        if let Ok(new_path) = std::env::join_paths(paths) {
            env.insert("PATH".to_string(), new_path.to_string_lossy().to_string());
        }
    } else {
        env.insert("PATH".to_string(), bin.to_string_lossy().to_string());
    }
    env
}

pub fn verify_installation(install_path: &Path) -> anyhow::Result<()> {
    // Try python3 first, then python
    let candidates = if cfg!(windows) {
        vec![install_path.join("python.exe"), install_path.join("python3.exe")]
    } else {
        vec![
            install_path.join("bin").join("python3"),
            install_path.join("bin").join("python"),
        ]
    };
    let python_bin = candidates.iter().find(|p| p.exists()).ok_or_else(|| {
        anyhow::anyhow!("python binary not found in {:?}", install_path)
    })?;
    let output = std::process::Command::new(python_bin).arg("--version").output()?;
    if !output.status.success() {
        anyhow::bail!("python --version failed");
    }
    Ok(())
}
