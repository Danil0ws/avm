use std::collections::HashMap;
use std::path::Path;

pub fn build_env_for_java(install_path: &Path) -> HashMap<String, String> {
    let mut env = HashMap::new();
    env.insert("JAVA_HOME".to_string(), install_path.to_string_lossy().to_string());
    let bin = install_path.join("bin");
    prepend_path(&mut env, &bin.to_string_lossy());
    env
}

pub fn build_env_for_node(install_path: &Path) -> HashMap<String, String> {
    let mut env = HashMap::new();
    let bin = if cfg!(windows) {
        install_path.to_path_buf()
    } else {
        install_path.join("bin")
    };
    prepend_path(&mut env, &bin.to_string_lossy());
    env
}

fn prepend_path(env: &mut HashMap<String, String>, new_dir: &str) {
    let current_path = std::env::var("PATH").unwrap_or_default();
    let sep = if cfg!(windows) { ";" } else { ":" };
    env.insert("PATH".to_string(), format!("{}{}{}", new_dir, sep, current_path));
}
