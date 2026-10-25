use std::path::{Path, PathBuf};

use serde::{Deserialize, Serialize};

use crate::error::Result;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum InstallState {
    Installed,
    Installing,
    Broken,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InstalledVersion {
    pub tool: String,
    pub version: String,
    pub distribution: Option<String>,
    pub os: String,
    pub arch: String,
    pub path: PathBuf,
    pub sha256: String,
    pub installed_at: String,
    pub state: InstallState,
}

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct Inventory {
    pub versions: Vec<InstalledVersion>,
}

impl Inventory {
    pub fn load(path: &Path) -> Result<Self> {
        if !path.exists() {
            return Ok(Self::default());
        }
        let content = std::fs::read_to_string(path)?;
        Ok(serde_json::from_str(&content).unwrap_or_default())
    }

    pub fn save(&self, path: &Path) -> Result<()> {
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)?;
        }
        let content = serde_json::to_string_pretty(self)?;
        let tmp = path.with_extension("tmp");
        std::fs::write(&tmp, &content)?;
        std::fs::rename(&tmp, path)?;
        Ok(())
    }

    pub fn find(&self, tool: &str, version: &str) -> Option<&InstalledVersion> {
        self.versions
            .iter()
            .find(|v| v.tool == tool && v.version == version && v.state == InstallState::Installed)
    }

    pub fn is_installed(&self, tool: &str, version: &str) -> bool {
        self.find(tool, version).is_some()
    }

    pub fn add(&mut self, entry: InstalledVersion) {
        self.versions
            .retain(|v| !(v.tool == entry.tool && v.version == entry.version));
        self.versions.push(entry);
    }

    pub fn remove(&mut self, tool: &str, version: &str) -> bool {
        let before = self.versions.len();
        self.versions.retain(|v| !(v.tool == tool && v.version == version));
        self.versions.len() < before
    }

    pub fn list_tool(&self, tool: &str) -> Vec<&InstalledVersion> {
        self.versions.iter().filter(|v| v.tool == tool).collect()
    }
}
