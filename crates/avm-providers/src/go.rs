use std::collections::HashMap;
use std::path::Path;

pub fn build_environment(install_path: &Path) -> HashMap<String, String> {
    let mut env = HashMap::new();
    env.insert("GOROOT".to_string(), install_path.to_string_lossy().to_string());
    let bin = install_path.join("bin");
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
    let go_bin = if cfg!(windows) {
        install_path.join("bin").join("go.exe")
    } else {
        install_path.join("bin").join("go")
    };
    if !go_bin.exists() {
        anyhow::bail!("go binary not found at {:?}", go_bin);
    }
    let output = std::process::Command::new(&go_bin).arg("version").output()?;
    if !output.status.success() {
        anyhow::bail!("go version failed");
    }
    Ok(())
}
