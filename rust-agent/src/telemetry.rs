use serde::Serialize;
use std::fs;

const PROC_PATH: &str = "/proc/edge_sensor";

#[derive(Debug, Serialize, PartialEq)]
pub struct Telemetry {
    pub cpu_temp_c: i32,
    pub mem_pressure_pct: i32,
    pub tcp_retrans_segs: i64,
}

pub fn parse_telemetry(content: &str) -> Result<Telemetry, String> {
    let mut cpu_temp_c: Option<i32> = None;
    let mut mem_pressure_pct: Option<i32> = None;
    let mut tcp_retrans_segs: Option<i64> = None;

    for line in content.lines() {
        let Some((key, val)) = line.split_once('=') else {
            continue;
        };
        match key {
            "cpu_temp_c" => cpu_temp_c = val.parse().ok(),
            "mem_pressure_pct" => mem_pressure_pct = val.parse().ok(),
            "tcp_retrans_segs" => tcp_retrans_segs = val.parse().ok(),
            _ => {}
        }
    }

    Ok(Telemetry {
        cpu_temp_c: cpu_temp_c.ok_or("missing cpu_temp_c")?,
        mem_pressure_pct: mem_pressure_pct.ok_or("missing mem_pressure_pct")?,
        tcp_retrans_segs: tcp_retrans_segs.ok_or("missing tcp_retrans_segs")?,
    })
}

pub fn read_telemetry() -> Result<Telemetry, String> {
    let content = fs::read_to_string(PROC_PATH)
        .map_err(|e| format!("failed to read {}: {}", PROC_PATH, e))?;
    parse_telemetry(&content)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_valid_input() {
        let input = "cpu_temp_c=47\nmem_pressure_pct=65\ntcp_retrans_segs=14934\n";
        let t = parse_telemetry(input).unwrap();
        assert_eq!(t, Telemetry {
            cpu_temp_c: 47,
            mem_pressure_pct: 65,
            tcp_retrans_segs: 14934,
        });
    }

    #[test]
    fn test_parse_negative_values() {
        let input = "cpu_temp_c=-1\nmem_pressure_pct=-1\ntcp_retrans_segs=-1\n";
        let t = parse_telemetry(input).unwrap();
        assert_eq!(t, Telemetry {
            cpu_temp_c: -1,
            mem_pressure_pct: -1,
            tcp_retrans_segs: -1,
        });
    }

    #[test]
    fn test_parse_missing_key() {
        let input = "cpu_temp_c=47\nmem_pressure_pct=65\n";
        let err = parse_telemetry(input).unwrap_err();
        assert_eq!(err, "missing tcp_retrans_segs");
    }

    #[test]
    fn test_parse_ignores_unknown_keys() {
        let input = "cpu_temp_c=50\nmem_pressure_pct=40\ntcp_retrans_segs=100\nunknown_key=999\n";
        let t = parse_telemetry(input).unwrap();
        assert_eq!(t.cpu_temp_c, 50);
    }

    #[test]
    fn test_parse_invalid_value() {
        let input = "cpu_temp_c=abc\nmem_pressure_pct=65\ntcp_retrans_segs=100\n";
        let err = parse_telemetry(input).unwrap_err();
        assert_eq!(err, "missing cpu_temp_c");
    }
}
