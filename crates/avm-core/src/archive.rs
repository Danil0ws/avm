use std::path::Path;

use crate::error::{AvmError, Result};

pub fn extract(archive_path: &Path, dest_dir: &Path, archive_type: &str) -> Result<()> {
    std::fs::create_dir_all(dest_dir)?;
    match archive_type {
        "zip" => extract_zip(archive_path, dest_dir),
        "tar.gz" => extract_tar_gz(archive_path, dest_dir),
        "tar.xz" => extract_tar_xz(archive_path, dest_dir),
        other => Err(AvmError::Extraction(format!("Unsupported archive type: {}", other))),
    }
}

fn check_path_traversal(dest: &Path, out_path: &Path) -> Result<()> {
    let dest_str = dest.to_string_lossy();
    let out_str = out_path.to_string_lossy();
    if !out_str.starts_with(dest_str.as_ref()) {
        return Err(AvmError::Extraction(format!(
            "Path traversal attempt: {:?}",
            out_path
        )));
    }
    Ok(())
}

fn extract_zip(archive: &Path, dest: &Path) -> Result<()> {
    let file = std::fs::File::open(archive)?;
    let mut zip =
        zip::ZipArchive::new(file).map_err(|e| AvmError::Extraction(format!("ZIP open error: {}", e)))?;
    for i in 0..zip.len() {
        let mut entry = zip
            .by_index(i)
            .map_err(|e| AvmError::Extraction(format!("ZIP entry error: {}", e)))?;
        let name = entry.name().to_string();
        let out_path = dest.join(std::path::Path::new(&name));
        check_path_traversal(dest, &out_path)?;
        if entry.is_dir() {
            std::fs::create_dir_all(&out_path)?;
        } else {
            if let Some(parent) = out_path.parent() {
                std::fs::create_dir_all(parent)?;
            }
            let mut out_file = std::fs::File::create(&out_path)?;
            std::io::copy(&mut entry, &mut out_file)?;
            #[cfg(unix)]
            {
                use std::os::unix::fs::PermissionsExt;
                if let Some(mode) = entry.unix_mode() {
                    std::fs::set_permissions(&out_path, std::fs::Permissions::from_mode(mode))?;
                }
            }
        }
    }
    Ok(())
}

fn extract_tar_gz(archive: &Path, dest: &Path) -> Result<()> {
    let file = std::fs::File::open(archive)?;
    let gz = flate2::read::GzDecoder::new(file);
    let mut tar = tar::Archive::new(gz);
    tar.set_preserve_permissions(true);
    extract_tar_entries(&mut tar, dest)
}

fn extract_tar_xz(archive: &Path, dest: &Path) -> Result<()> {
    let file = std::fs::File::open(archive)?;
    let xz = xz2::read::XzDecoder::new(file);
    let mut tar = tar::Archive::new(xz);
    tar.set_preserve_permissions(true);
    extract_tar_entries(&mut tar, dest)
}

fn extract_tar_entries<R: std::io::Read>(tar: &mut tar::Archive<R>, dest: &Path) -> Result<()> {
    for entry in tar.entries().map_err(|e| AvmError::Extraction(format!("TAR entries: {}", e)))? {
        let mut entry = entry.map_err(|e| AvmError::Extraction(format!("TAR entry: {}", e)))?;
        let path = entry
            .path()
            .map_err(|e| AvmError::Extraction(format!("TAR path: {}", e)))?
            .to_path_buf();
        let out_path = dest.join(&path);
        check_path_traversal(dest, &out_path)?;
        entry
            .unpack(&out_path)
            .map_err(|e| AvmError::Extraction(format!("TAR unpack: {}", e)))?;
    }
    Ok(())
}
