use std::io::{Read, Write};
use std::path::Path;
use std::time::Duration;

use crate::error::{AvmError, Result};

pub struct Downloader {
    client: reqwest::blocking::Client,
}

impl Downloader {
    pub fn new() -> Result<Self> {
        let client = reqwest::blocking::Client::builder()
            .timeout(Duration::from_secs(600))
            .https_only(true)
            .build()
            .map_err(AvmError::Http)?;
        Ok(Downloader { client })
    }

    pub fn download(&self, url: &str, dest: &Path, expected_size: Option<u64>) -> Result<()> {
        if !url.starts_with("https://") {
            return Err(AvmError::Other(format!("Refusing non-HTTPS URL: {}", url)));
        }

        let mut resp = self.client.get(url).send().map_err(AvmError::Http)?;

        if !resp.status().is_success() {
            return Err(AvmError::Other(format!("HTTP {} downloading {}", resp.status(), url)));
        }

        let mut file = std::fs::File::create(dest)?;
        let mut downloaded: u64 = 0;
        let mut buf = [0u8; 65536];

        loop {
            let n = resp
                .read(&mut buf)
                .map_err(|e| AvmError::Other(format!("Read error: {}", e)))?;
            if n == 0 {
                break;
            }
            file.write_all(&buf[..n])?;
            downloaded += n as u64;
        }

        if let Some(expected) = expected_size {
            if downloaded != expected {
                return Err(AvmError::Other(format!(
                    "Size mismatch: expected {} bytes, got {}",
                    expected, downloaded
                )));
            }
        }

        Ok(())
    }
}
