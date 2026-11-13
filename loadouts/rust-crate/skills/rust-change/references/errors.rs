//! Typed error pattern without extra dependencies. Callers can match on the variant; humans get a clear message.
//! When copying, change `fixture_crate::errors` in the doc test to your crate and module path.

use std::fmt;
use std::num::ParseIntError;

#[derive(Debug, PartialEq)]
pub enum ConfigError {
    /// A required key is missing.
    Missing(&'static str),
    /// A value could not be parsed.
    BadNumber { key: &'static str, source: ParseIntError },
    /// A value is outside the allowed range.
    OutOfRange { key: &'static str, value: u32, max: u32 },
}

impl fmt::Display for ConfigError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Missing(key) => write!(f, "missing required setting `{key}`"),
            Self::BadNumber { key, .. } => write!(f, "setting `{key}` is not a whole number"),
            Self::OutOfRange { key, value, max } => write!(f, "setting `{key}` is {value}, the maximum is {max}"),
        }
    }
}

impl std::error::Error for ConfigError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            Self::BadNumber { source, .. } => Some(source),
            _ => None,
        }
    }
}

/// Reads the worker count from `key=value` lines.
///
/// ```
/// # use fixture_crate::errors::workers;
/// assert_eq!(workers("workers=4"), Ok(4));
/// ```
pub fn workers(config: &str) -> Result<u32, ConfigError> {
    const KEY: &str = "workers";
    const MAX: u32 = 64;
    let raw = config
        .lines()
        .filter_map(|line| line.split_once('='))
        .find(|(k, _)| k.trim() == KEY)
        .map(|(_, v)| v.trim())
        .ok_or(ConfigError::Missing(KEY))?;
    let value: u32 = raw.parse().map_err(|source| ConfigError::BadNumber { key: KEY, source })?;
    if value > MAX {
        return Err(ConfigError::OutOfRange { key: KEY, value, max: MAX });
    }
    Ok(value)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::error::Error;

    #[test]
    fn reads_value() {
        assert_eq!(workers("name=x\nworkers = 8\n"), Ok(8));
    }

    #[test]
    fn missing_key() {
        assert_eq!(workers("name=x"), Err(ConfigError::Missing("workers")));
    }

    #[test]
    fn bad_number_keeps_source() {
        let err = workers("workers=lots").unwrap_err();
        assert!(matches!(err, ConfigError::BadNumber { .. }));
        assert!(err.source().is_some());
        assert_eq!(err.to_string(), "setting `workers` is not a whole number");
    }

    #[test]
    fn out_of_range() {
        assert_eq!(workers("workers=100"), Err(ConfigError::OutOfRange { key: "workers", value: 100, max: 64 }));
    }
}
