use thiserror::Error;

#[derive(Error, Debug)]
pub enum AvmError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("HTTP error: {0}")]
    Http(#[from] reqwest::Error),
    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),
    #[error("Version not found: {tool} {version}")]
    VersionNotFound { tool: String, version: String },
    #[error("No artifact for {tool} {version} on {os}/{arch}")]
    NoArtifact { tool: String, version: String, os: String, arch: String },
    #[error("Checksum mismatch: expected {expected}, got {actual}")]
    ChecksumMismatch { expected: String, actual: String },
    #[error("Already installed: {tool} {version}")]
    AlreadyInstalled { tool: String, version: String },
    #[error("Not installed: {tool} {version}")]
    NotInstalled { tool: String, version: String },
    #[error("Catalog error: {0}")]
    Catalog(String),
    #[error("Config error: {0}")]
    Config(String),
    #[error("Extraction error: {0}")]
    Extraction(String),
    #[error("Verification failed: {0}")]
    VerificationFailed(String),
    #[error("{0}")]
    Other(String),
}

pub type Result<T> = std::result::Result<T, AvmError>;
