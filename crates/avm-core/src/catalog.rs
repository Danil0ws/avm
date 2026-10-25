use serde::{Deserialize, Serialize};
use std::path::Path;
use std::time::Duration;

use crate::error::{AvmError, Result};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CatalogArtifact {
    pub os: String,
    pub arch: String,
    pub archive_type: String,
    pub url: String,
    pub sha256: String,
    pub size_bytes: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CatalogVersion {
    pub version: String,
    pub release_date: Option<String>,
    pub channel: Option<String>,
    pub distribution: Option<String>,
    pub artifacts: Vec<CatalogArtifact>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolCatalog {
    pub schema_version: u32,
    pub generated_at: String,
    pub tool: String,
    pub source: String,
    pub versions: Vec<CatalogVersion>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CatalogIndex {
    pub schema_version: u32,
    pub generated_at: String,
    pub tools: Vec<CatalogIndexEntry>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CatalogIndexEntry {
    pub name: String,
    pub path: String,
}

pub struct CatalogClient {
    base_url: String,
    #[allow(dead_code)]
    cache_dir: std::path::PathBuf,
    client: reqwest::blocking::Client,
}

impl CatalogClient {
    pub fn new(base_url: &str, cache_dir: &Path) -> Result<Self> {
        let client = reqwest::blocking::Client::builder()
            .timeout(Duration::from_secs(30))
            .https_only(true)
            .build()
            .map_err(AvmError::Http)?;
        Ok(CatalogClient {
            base_url: base_url.trim_end_matches('/').to_string(),
            cache_dir: cache_dir.to_path_buf(),
            client,
        })
    }

    pub fn fetch_tool_catalog(&self, tool: &str) -> Result<ToolCatalog> {
        let url = format!("{}/tools/{}.json", self.base_url, tool);
        let resp = self
            .client
            .get(&url)
            .send()
            .map_err(|e| AvmError::Catalog(format!("Failed to fetch catalog for {}: {}", tool, e)))?;
        if !resp.status().is_success() {
            return Err(AvmError::Catalog(format!("HTTP {} fetching {}", resp.status(), url)));
        }
        let catalog: ToolCatalog = resp
            .json()
            .map_err(|e| AvmError::Catalog(format!("Failed to parse catalog: {}", e)))?;
        Ok(catalog)
    }

    pub fn load_local_catalog(&self, path: &Path) -> Result<ToolCatalog> {
        let content = std::fs::read_to_string(path).map_err(AvmError::Io)?;
        let catalog: ToolCatalog = serde_json::from_str(&content).map_err(AvmError::Json)?;
        Ok(catalog)
    }
}

pub fn find_version_in_catalog<'a>(catalog: &'a ToolCatalog, version_spec: &str) -> Option<&'a CatalogVersion> {
    // Exact match first
    if let Some(v) = catalog.versions.iter().find(|v| v.version == version_spec) {
        return Some(v);
    }
    // Major version match (e.g. "21" matches "21.0.3+9")
    catalog.versions.iter().find(|v| {
        let major = v.version.split('.').next().unwrap_or("").split('+').next().unwrap_or("");
        major == version_spec
    })
}

pub fn filter_artifacts<'a>(version: &'a CatalogVersion, os: &str, arch: &str) -> Vec<&'a CatalogArtifact> {
    version.artifacts.iter().filter(|a| a.os == os && a.arch == arch).collect()
}
