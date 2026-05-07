use axum::{Json, Router, http::StatusCode, routing::get};
use serde::Serialize;
use std::fs;
use tokio::net::TcpListener;

const PROC_PATH: &str = "/proc/edge_sensor";

#[derive(Debug, Serialize)]
pub struct Telemetry {
    pub cpu_temp_c: i32,
    pub mem_pressure_pct: i32,
    pub tcp_retrans_segs: i64,
}

pub fn read_telemetry() -> Result<Telemetry, String> {
    let content = fs::read_to_string(PROC_PATH)
        .map_err(|e| format!("failed to read {}: {}", PROC_PATH, e))?;

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

async fn get_telemetry() -> Result<Json<Telemetry>, (StatusCode, String)> {
    read_telemetry()
        .map(Json)
        .map_err(|e| (StatusCode::SERVICE_UNAVAILABLE, e))
}

async fn health() -> &'static str {
    "ok"
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/telemetry", get(get_telemetry))
        .route("/health", get(health));

    let addr = "0.0.0.0:3000";
    println!("edge-agent listening on {}", addr);

    let listener = TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
