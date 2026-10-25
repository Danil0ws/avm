use std::path::PathBuf;

pub fn avm_home() -> PathBuf {
    if let Ok(v) = std::env::var("AVM_HOME") {
        return PathBuf::from(v);
    }
    #[cfg(target_os = "windows")]
    {
        dirs::data_local_dir()
            .unwrap_or_else(|| PathBuf::from("C:\\Users\\Default\\AppData\\Local"))
            .join("AVM")
    }
    #[cfg(target_os = "macos")]
    {
        dirs::data_dir()
            .unwrap_or_else(|| dirs::home_dir().unwrap().join("Library/Application Support"))
            .join("avm")
    }
    #[cfg(not(any(target_os = "windows", target_os = "macos")))]
    {
        std::env::var("XDG_DATA_HOME")
            .map(PathBuf::from)
            .unwrap_or_else(|_| dirs::home_dir().unwrap().join(".local/share"))
            .join("avm")
    }
}

pub fn config_dir() -> PathBuf {
    if let Ok(v) = std::env::var("AVM_CONFIG_DIR") {
        return PathBuf::from(v);
    }
    #[cfg(target_os = "windows")]
    {
        dirs::config_dir().unwrap().join("avm")
    }
    #[cfg(target_os = "macos")]
    {
        dirs::config_dir()
            .unwrap_or_else(|| dirs::home_dir().unwrap().join("Library/Application Support"))
            .join("avm")
    }
    #[cfg(not(any(target_os = "windows", target_os = "macos")))]
    {
        std::env::var("XDG_CONFIG_HOME")
            .map(PathBuf::from)
            .unwrap_or_else(|_| dirs::home_dir().unwrap().join(".config"))
            .join("avm")
    }
}

pub fn cache_dir() -> PathBuf {
    avm_home().join("cache")
}

pub fn runtimes_dir() -> PathBuf {
    avm_home().join("runtimes")
}

pub fn downloads_dir() -> PathBuf {
    avm_home().join("downloads")
}

pub fn temp_dir() -> PathBuf {
    avm_home().join("temp")
}

pub fn inventory_path() -> PathBuf {
    avm_home().join("state").join("inventory.json")
}

pub fn global_config_path() -> PathBuf {
    config_dir().join("config.toml")
}
