use std::path::{Path, PathBuf};

use crate::archive::extract;
use crate::catalog::CatalogArtifact;
use crate::download::Downloader;
use crate::error::{AvmError, Result};
use crate::paths;
use crate::verification::verify_sha256;

pub struct InstallPlan {
    pub tool: String,
    pub version: String,
    pub distribution: Option<String>,
    pub artifact: CatalogArtifact,
}

impl InstallPlan {
    pub fn display(&self) {
        println!("  Tool:         {}", self.tool);
        println!("  Version:      {}", self.version);
        if let Some(d) = &self.distribution {
            println!("  Distribution: {}", d);
        }
        println!("  OS/Arch:      {}/{}", self.artifact.os, self.artifact.arch);
        println!("  Archive:      {}", self.artifact.archive_type);
        println!("  URL:          {}", self.artifact.url);
        println!("  SHA-256:      {}", self.artifact.sha256);
    }
}

pub fn install(plan: &InstallPlan) -> Result<PathBuf> {
    let downloads = paths::downloads_dir();
    let temp = paths::temp_dir();
    std::fs::create_dir_all(&downloads)?;
    std::fs::create_dir_all(&temp)?;

    let filename = plan
        .artifact
        .url
        .split('/')
        .last()
        .ok_or_else(|| AvmError::Other("Cannot determine filename from URL".to_string()))?;
    let archive_path = downloads.join(filename);

    println!("Downloading {}...", plan.artifact.url);
    let downloader = Downloader::new()?;
    downloader.download(&plan.artifact.url, &archive_path, plan.artifact.size_bytes)?;

    println!("Verifying SHA-256...");
    verify_sha256(&archive_path, &plan.artifact.sha256)?;
    println!("  OK");

    let extract_dir = temp.join(format!(
        "{}-{}-{}",
        plan.tool,
        plan.version,
        uuid::Uuid::new_v4()
    ));
    std::fs::create_dir_all(&extract_dir)?;
    println!("Extracting...");
    extract(&archive_path, &extract_dir, &plan.artifact.archive_type)?;

    let runtime_root = find_runtime_root(&extract_dir, &plan.tool)?;

    let install_path = paths::runtimes_dir()
        .join(&plan.tool)
        .join(plan.distribution.as_deref().unwrap_or("default"))
        .join(&plan.version);

    if install_path.exists() {
        std::fs::remove_dir_all(&install_path)?;
    }
    if let Some(parent) = install_path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    std::fs::rename(&runtime_root, &install_path)?;

    let _ = std::fs::remove_dir_all(&extract_dir);

    println!("Installed to: {}", install_path.display());
    Ok(install_path)
}

fn find_runtime_root(extract_dir: &Path, tool: &str) -> Result<PathBuf> {
    if has_tool_binaries(extract_dir, tool) {
        return Ok(extract_dir.to_path_buf());
    }
    for entry in std::fs::read_dir(extract_dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.is_dir() && has_tool_binaries(&path, tool) {
            return Ok(path);
        }
    }
    Ok(extract_dir.to_path_buf())
}

fn has_tool_binaries(dir: &Path, tool: &str) -> bool {
    match tool {
        "java" => dir.join("bin").join("java").exists() || dir.join("bin").join("java.exe").exists(),
        "node" => dir.join("bin").join("node").exists() || dir.join("node.exe").exists(),
        _ => false,
    }
}
