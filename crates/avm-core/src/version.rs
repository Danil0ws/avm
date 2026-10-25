use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct VersionSpec {
    pub tool: String,
    pub version: Option<String>,
    pub distribution: Option<String>,
}

impl VersionSpec {
    /// Parse "java@21", "java@temurin:21", "node@22.14.0"
    pub fn parse(input: &str) -> crate::error::Result<Self> {
        let (tool, rest) = if let Some(pos) = input.find('@') {
            (&input[..pos], Some(&input[pos + 1..]))
        } else {
            (input, None)
        };

        let (distribution, version) = match rest {
            None => (None, None),
            Some(r) => {
                if let Some(colon) = r.find(':') {
                    (Some(r[..colon].to_string()), Some(r[colon + 1..].to_string()))
                } else {
                    (None, Some(r.to_string()))
                }
            }
        };

        Ok(VersionSpec {
            tool: tool.to_string(),
            version,
            distribution,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_simple() {
        let s = VersionSpec::parse("java@21").unwrap();
        assert_eq!(s.tool, "java");
        assert_eq!(s.version.as_deref(), Some("21"));
        assert_eq!(s.distribution, None);
    }

    #[test]
    fn test_parse_with_distribution() {
        let s = VersionSpec::parse("java@temurin:21").unwrap();
        assert_eq!(s.tool, "java");
        assert_eq!(s.version.as_deref(), Some("21"));
        assert_eq!(s.distribution.as_deref(), Some("temurin"));
    }

    #[test]
    fn test_parse_no_version() {
        let s = VersionSpec::parse("node").unwrap();
        assert_eq!(s.tool, "node");
        assert_eq!(s.version, None);
    }
}
