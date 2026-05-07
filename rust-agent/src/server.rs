use axum::{Json, Router, http::StatusCode, routing::get};
use crate::telemetry::{Telemetry, read_telemetry};

async fn get_telemetry() -> Result<Json<Telemetry>, (StatusCode, String)> {
    read_telemetry()
        .map(Json)
        .map_err(|e| (StatusCode::SERVICE_UNAVAILABLE, e))
}

async fn health() -> &'static str {
    "ok"
}

pub fn build_router() -> Router {
    Router::new()
        .route("/telemetry", get(get_telemetry))
        .route("/health", get(health))
}
