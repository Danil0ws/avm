use std::collections::HashMap;
use std::path::Path;

pub fn build_environment(install_path: &Path) -> HashMap<String, String> {
    let mut env = HashMap::new();
    env.insert("DOTNET_ROOT".to_string(), install_path.to_string_lossy().to_string());
    if let Some(path) = std::env::var_os("PATH") {
        let mut paths = std::env::split_paths(&path).collect::<Vec<_>>();
        paths.insert(0, install_path.to_path_buf());
        if let Ok(new_path) = std::env::join_paths(paths) {
            env.insert("PATH".to_string(), new_path.to_string_lossy().to_string());
        }
    } else {
        env.insert("PATH".to_string(), install_path.to_string_lossy().to_string());
    }
    env
}

pub fn verify_installation(install_path: &Path) -> anyhow::Result<()> {
    let dotnet_bin = if cfg!(windows) {
        install_path.join("dotnet.exe")
    } else {
        install_path.join("dotnet")
    };
    if !dotnet_bin.exists() {
        anyhow::bail!("dotnet binary not found at {:?}", dotnet_bin);
    }
    let output = std::process::Command::new(&dotnet_bin).arg("--version").output()?;
    if !output.status.success() {
        anyhow::bail!("dotnet --version failed");
    }
    Ok(())
}
