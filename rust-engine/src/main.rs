use actix_cors::Cors;
use actix_web::{get, web, App, HttpServer, HttpResponse, Responder};
use rand::Rng;
use serde::{Deserialize, Serialize};
use std::time::SystemTime;

// --- 数据模型 ---

#[derive(Serialize)]
struct HealthResponse {
    status: String,
    service: String,
    engine: String,
    timestamp: String,
}

#[derive(Serialize)]
struct WaitEventAnalysis {
    instance_id: String,
    health_score: u32,
    anomaly_detected: bool,
    anomaly_details: Vec<String>,
    sync_trend: Vec<SyncTrendPoint>,
    recommendations: Vec<String>,
    engine: String,
}

#[derive(Serialize)]
struct SyncTrendPoint {
    time: String,
    wait_count: u32,
    avg_wait_ms: f64,
}

#[derive(Serialize)]
struct AnomalyResult {
    event_name: String,
    score: f64,
    description: String,
}

#[derive(Serialize)]
struct SqlVersionCompat {
    feature: String,
    v10g: String,
    v11g: String,
    v19c: String,
    v23c: String,
    v26ai: String,
}

#[derive(Deserialize)]
struct AnalysisQuery {
    minutes: Option<u32>,
}

// --- 处理器 ---

#[get("/health")]
async fn health() -> impl Responder {
    HttpResponse::Ok().json(HealthResponse {
        status: "healthy".to_string(),
        service: "AcdanteSQLMon Rust Data Engine".to_string(),
        engine: "Rust/Actix-Web".to_string(),
        timestamp: chrono::Utc::now().to_rfc3339(),
    })
}

#[get("/api/v1/analysis/{instance_id}")]
async fn analyze_instance(path: web::Path<String>, query: web::Query<AnalysisQuery>) -> impl Responder {
    let instance_id = path.into_inner();
    let minutes = query.minutes.unwrap_or(10);
    let mut rng = rand::thread_rng();

    let mut trend = Vec::new();
    for i in 0..minutes {
        trend.push(SyncTrendPoint {
            time: format!("{}m ago", minutes - i),
            wait_count: rng.gen_range(5..80),
            avg_wait_ms: rng.gen_range(1.0..200.0),
        });
    }

    let health_score = rng.gen_range(60..100);
    let anomaly_detected = health_score < 80;

    let mut anomalies = Vec::new();
    if anomaly_detected {
        anomalies.push("enq: TX - row lock contention: 等待时间异常增长".to_string());
        anomalies.push("gc buffer busy acquire: RAC缓存争用频率偏高".to_string());
    }

    let mut recommendations = Vec::new();
    if health_score < 75 {
        recommendations.push("建议检查长事务并优化行锁冲突".to_string());
        recommendations.push("建议增大 SHARED_POOL_SIZE 缓解解析压力".to_string());
    } else if health_score < 90 {
        recommendations.push("建议关注等待事件趋势变化".to_string());
    } else {
        recommendations.push("实例运行状态良好".to_string());
    }

    HttpResponse::Ok().json(WaitEventAnalysis {
        instance_id,
        health_score,
        anomaly_detected,
        anomaly_details: anomalies,
        sync_trend: trend,
        recommendations,
        engine: "Rust/Actix-Web".to_string(),
    })
}

#[get("/api/v1/analysis/{instance_id}/anomaly")]
async fn detect_anomaly(path: web::Path<String>) -> impl Responder {
    let instance_id = path.into_inner();
    let mut rng = rand::thread_rng();

    let events = vec![
        AnomalyResult {
            event_name: "enq: TX - row lock contention".to_string(),
            score: rng.gen_range(0.7..0.99),
            description: "行锁等待异常，可能存在长事务阻塞".to_string(),
        },
        AnomalyResult {
            event_name: "gc buffer busy acquire".to_string(),
            score: rng.gen_range(0.3..0.8),
            description: "RAC缓存争用，热点块可能需要分区".to_string(),
        },
        AnomalyResult {
            event_name: "log file sync".to_string(),
            score: rng.gen_range(0.1..0.5),
            description: "日志同步等待轻微偏高".to_string(),
        },
    ];

    HttpResponse::Ok().json(serde_json::json!({
        "instance_id": instance_id,
        "anomalies": events,
        "engine": "Rust/Actix-Web"
    }))
}

#[get("/api/v1/sql-compat")]
async fn sql_compat_matrix() -> impl Responder {
    let compat = vec![
        SqlVersionCompat {
            feature: "GV$SESSION_WAIT.WAIT_CLASS".to_string(),
            v10g: "需JOIN V$EVENT_NAME".to_string(),
            v11g: "需JOIN".to_string(),
            v19c: "原生支持".to_string(),
            v23c: "原生支持".to_string(),
            v26ai: "原生支持".to_string(),
        },
        SqlVersionCompat {
            feature: "GV$SESSION.BLOCKING_SESSION".to_string(),
            v10g: "支持".to_string(),
            v11g: "支持".to_string(),
            v19c: "支持".to_string(),
            v23c: "支持".to_string(),
            v26ai: "支持".to_string(),
        },
        SqlVersionCompat {
            feature: "FINAL_BLOCKING_SESSION".to_string(),
            v10g: "不支持".to_string(),
            v11g: "不支持".to_string(),
            v19c: "支持(新特性)".to_string(),
            v23c: "支持".to_string(),
            v26ai: "支持".to_string(),
        },
        SqlVersionCompat {
            feature: "FETCH FIRST N ROWS ONLY".to_string(),
            v10g: "用ROWNUM".to_string(),
            v11g: "用ROWNUM".to_string(),
            v19c: "支持(12c+)".to_string(),
            v23c: "支持".to_string(),
            v26ai: "支持".to_string(),
        },
        SqlVersionCompat {
            feature: "GV$ACTIVE_SESSION_HISTORY".to_string(),
            v10g: "需Diagnostics Pack".to_string(),
            v11g: "需Diagnostics Pack".to_string(),
            v19c: "需Diagnostics Pack".to_string(),
            v23c: "需Diagnostics Pack".to_string(),
            v26ai: "需Diagnostics Pack".to_string(),
        },
        SqlVersionCompat {
            feature: "Python oracledb Thin模式".to_string(),
            v10g: "不支持(需Thick)".to_string(),
            v11g: "不支持(需Thick)".to_string(),
            v19c: "支持".to_string(),
            v23c: "支持".to_string(),
            v26ai: "支持".to_string(),
        },
        SqlVersionCompat {
            feature: "Instant Client需求".to_string(),
            v10g: "必须安装".to_string(),
            v11g: "必须安装".to_string(),
            v19c: "不需要(Thin模式)".to_string(),
            v23c: "不需要".to_string(),
            v26ai: "不需要".to_string(),
        },
    ];

    HttpResponse::Ok().json(serde_json::json!({
        "compat_matrix": compat,
        "engine": "Rust/Actix-Web"
    }))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    println!("[AcdanteSQLMon Rust Engine] 启动于 0.0.0.0:8081");

    HttpServer::new(|| {
        let cors = Cors::default()
            .allow_any_origin()
            .allow_any_method()
            .allow_any_header()
            .max_age(3600);

        App::new()
            .wrap(cors)
            .service(health)
            .service(analyze_instance)
            .service(detect_anomaly)
            .service(sql_compat_matrix)
    })
    .bind("0.0.0.0:8081")?
    .run()
    .await
}
