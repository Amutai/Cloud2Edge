use edge_agent::server;
use tokio::net::TcpListener;

#[tokio::main]
async fn main() {
    let app = server::build_router();
    let addr = "0.0.0.0:3000";
    println!("edge-agent listening on {}", addr);

    let listener = TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
