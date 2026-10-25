use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::{Path, PathBuf};

use crate::error::Result;

pub const DEFAULT_CATALOG_URL: &str = "https://your-username.github.io/avm-catalog";

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct GlobalConfig {
    pub catalog_url: Option<String>,
    #[serde(default)]
    pub tools: HashMap<String, ToolConfig>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ToolConfig {
    pub version: Option<String>,
    pub distribution: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ProjectConfig {
    pub project: Option<ProjectMeta>,
    pub tools: Option<HashMap<String, ToolConfig>>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ProjectMeta {
    pub name: Option<String>,
}

impl GlobalConfig {
    pub fn load(path: &Path) -> Result<Self> {
        if !path.exists() {
            return Ok(Self::default());
        }
        let content = std::fs::read_to_string(path)?;
        Ok(toml::from_str(&content).unwrap_or_default())
    }

    pub fn catalog_url(&self) -> &str {
        self.catalog_url.as_deref().unwrap_or(DEFAULT_CATALOG_URL)
    }
}

impl ProjectConfig {
    pub fn load(path: &Path) -> Result<Self> {
        if !path.exists() {
            return Ok(Self::default());
        }
        let content = std::fs::read_to_string(path)?;
        Ok(toml::from_str(&content).unwrap_or_default())
    }

    pub fn find_in_dir(dir: &Path) -> Option<PathBuf> {
        let candidate = dir.join("avm.toml");
        if candidate.exists() {
            return Some(candidate);
        }
        dir.parent().and_then(Self::find_in_dir)
    }
}
