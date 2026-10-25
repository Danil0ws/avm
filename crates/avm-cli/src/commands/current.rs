use avm_core::{config::GlobalConfig, paths};

pub fn run(tool: Option<&str>) -> anyhow::Result<()> {
    let config = GlobalConfig::load(&paths::global_config_path())?;
    let tools: Vec<String> = if let Some(t) = tool {
        vec![t.to_string()]
    } else {
        config.tools.keys().cloned().collect()
    };
    if tools.is_empty() {
        println!("No default versions configured.");
        println!("Configure in: {}", paths::global_config_path().display());
        return Ok(());
    }
    for t in &tools {
        if let Some(tc) = config.tools.get(t) {
            if let Some(v) = &tc.version {
                println!("  {} -> {}", t, v);
            }
        }
    }
    Ok(())
}
