-- AcdanteSQLMon 数据库 Schema
-- SQLite 格式，用于存储实例配置、审计日志、等待事件快照、知识库

-- 实例配置表
CREATE TABLE IF NOT EXISTS oracle_instances (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    instance_name   VARCHAR(128)  NOT NULL,
    host            VARCHAR(256)  NOT NULL,
    port            INTEGER       NOT NULL DEFAULT 1521,
    service_name    VARCHAR(128),
    sid             VARCHAR(128),
    username        VARCHAR(128)  NOT NULL,
    password_enc    VARCHAR(512)  NOT NULL,
    oracle_version  VARCHAR(32),
    is_rac          BOOLEAN       DEFAULT 0,
    rac_inst_count  INTEGER       DEFAULT 1,
    connect_mode    VARCHAR(16)   DEFAULT 'oracledb',
    need_client     BOOLEAN       DEFAULT 0,
    client_path     VARCHAR(512),
    status          VARCHAR(16)   DEFAULT 'active',
    last_check_time DATETIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 查杀审计日志表
CREATE TABLE IF NOT EXISTS kill_audit_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    instance_id     INTEGER       NOT NULL,
    inst_id         INTEGER,
    sid             INTEGER       NOT NULL,
    serial_num      INTEGER       NOT NULL,
    username        VARCHAR(128),
    machine         VARCHAR(256),
    program         VARCHAR(256),
    os_user         VARCHAR(128),
    process_id      VARCHAR(64),
    sql_text        TEXT,
    sql_id          VARCHAR(64),
    lock_type       VARCHAR(64),
    lock_mode       VARCHAR(32),
    wait_event      VARCHAR(128),
    blocking_sid    INTEGER,
    hold_duration   INTEGER,
    kill_command    TEXT,
    os_kill_command TEXT,
    kill_success    BOOLEAN,
    kill_error      TEXT,
    operator        VARCHAR(64),
    operated_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 等待事件快照表 (用于历史分析)
CREATE TABLE IF NOT EXISTS wait_event_snapshots (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    instance_id     INTEGER       NOT NULL,
    snap_time       DATETIME      NOT NULL,
    inst_id         INTEGER,
    event_name      VARCHAR(256)  NOT NULL,
    wait_class      VARCHAR(128),
    total_waits     INTEGER,
    total_timeout   INTEGER,
    time_waited_ms  INTEGER,
    avg_wait_ms     REAL,
    sql_id          VARCHAR(64),
    sql_text        TEXT
);

-- 等待事件知识库
CREATE TABLE IF NOT EXISTS wait_event_guide (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name      VARCHAR(256)  NOT NULL UNIQUE,
    wait_class      VARCHAR(128),
    description     TEXT          NOT NULL,
    typical_cause   TEXT,
    resolution      TEXT,
    oracle_doc_url  VARCHAR(512),
    severity        VARCHAR(16)   DEFAULT 'info',
    applicable_ver  VARCHAR(256)  DEFAULT 'ALL'
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_kill_audit_instance ON kill_audit_log(instance_id);
CREATE INDEX IF NOT EXISTS idx_kill_audit_time ON kill_audit_log(operated_at);
CREATE INDEX IF NOT EXISTS idx_snap_instance_time ON wait_event_snapshots(instance_id, snap_time);
CREATE INDEX IF NOT EXISTS idx_guide_class ON wait_event_guide(wait_class);
CREATE INDEX IF NOT EXISTS idx_guide_severity ON wait_event_guide(severity);
