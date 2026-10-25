use crate::catalog::{filter_artifacts, find_version_in_catalog, ToolCatalog};
use crate::error::{AvmError, Result};
use crate::installer::InstallPlan;

pub fn current_os() -> &'static str {
    if cfg!(target_os = "windows") {
        "windows"
    } else if cfg!(target_os = "macos") {
        "macos"
    } else {
        "linux"
    }
}

pub fn current_arch() -> &'static str {
    if cfg!(target_arch = "aarch64") {
        "arm64"
    } else {
        "x64"
    }
}

pub fn resolve_install_plan(
    catalog: &ToolCatalog,
    tool: &str,
    version_req: &str,
    distribution: Option<&str>,
    os: Option<&str>,
    arch: Option<&str>,
) -> Result<InstallPlan> {
    let os_owned: String;
    let os = match os {
        Some(v) => v,
        None => { os_owned = current_os().to_string(); os_owned.as_str() }
    };
    let arch_owned: String;
    let arch = match arch {
        Some(v) => v,
        None => { arch_owned = current_arch().to_string(); arch_owned.as_str() }
    };

    let version = find_version_in_catalog(catalog, version_req).ok_or_else(|| AvmError::VersionNotFound {
        tool: tool.to_string(),
        version: version_req.to_string(),
    })?;

    let artifacts = filter_artifacts(version, os, arch);
    let artifact = artifacts.first().copied();

    let artifact = artifact.ok_or_else(|| AvmError::NoArtifact {
        tool: tool.to_string(),
        version: version_req.to_string(),
        os: os.to_string(),
        arch: arch.to_string(),
    })?;

    Ok(InstallPlan {
        tool: tool.to_string(),
        version: version.version.clone(),
        distribution: version
            .distribution
            .clone()
            .or_else(|| distribution.map(String::from)),
        artifact: artifact.clone(),
    })
}
