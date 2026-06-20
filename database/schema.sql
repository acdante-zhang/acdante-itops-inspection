-- Acdante ITOps Inspection Platform 数据库 Schema
-- SQLite 格式，用于存储巡检对象、模板、任务、报告、SNMP等

-- ============================================================
-- 巡检对象表
-- ============================================================
CREATE TABLE IF NOT EXISTS inspection_targets (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(256)  NOT NULL,
    target_type     VARCHAR(32)   NOT NULL,
    brand           VARCHAR(64),
    model           VARCHAR(128),
    version         VARCHAR(32),
    location        VARCHAR(256),
    connection_protocol VARCHAR(32) NOT NULL DEFAULT 'ssh',
    host            VARCHAR(256)  NOT NULL,
    port            INTEGER,
    username        VARCHAR(128),
    password_enc    VARCHAR(512),
    snmp_community  VARCHAR(128),
    snmp_version    VARCHAR(8),
    database_name   VARCHAR(128),
    offline_mode    BOOLEAN       DEFAULT 0,
    status          VARCHAR(16)   DEFAULT 'active',
    health_score    INTEGER       DEFAULT 100,
    last_inspection_at DATETIME,
    tags            TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- SNMP 模板表
-- ============================================================
CREATE TABLE IF NOT EXISTS snmp_templates (
    id              VARCHAR(64)   PRIMARY KEY,
    name            VARCHAR(256)  NOT NULL,
    device_type     VARCHAR(32)   NOT NULL,
    brand           VARCHAR(64),
    model           VARCHAR(128),
    description     TEXT,
    vendor_mib      VARCHAR(32),
    is_builtin      BOOLEAN       DEFAULT 0,
    item_count      INTEGER       DEFAULT 0,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- SNMP OID 注册表
-- ============================================================
CREATE TABLE IF NOT EXISTS snmp_oid_registry (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor          VARCHAR(64)   NOT NULL,
    category        VARCHAR(64),
    oid_name        VARCHAR(128)  NOT NULL,
    oid             VARCHAR(256)  NOT NULL,
    name            VARCHAR(256)  NOT NULL,
    oid_type        VARCHAR(32)   DEFAULT 'gauge',
    is_table        BOOLEAN       DEFAULT 0,
    description     TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 巡检模板表（扩展版）
-- ============================================================
CREATE TABLE IF NOT EXISTS inspection_templates (
    id              VARCHAR(64)   PRIMARY KEY,
    name            VARCHAR(256)  NOT NULL,
    target_type     VARCHAR(32)   NOT NULL,
    brand           VARCHAR(64),
    version         VARCHAR(32),
    description     TEXT,
    template_type   VARCHAR(16)   DEFAULT 'ssh',
    is_builtin      BOOLEAN       DEFAULT 0,
    created_by      VARCHAR(64),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 巡检项表
-- ============================================================
CREATE TABLE IF NOT EXISTS inspection_items (
    id              VARCHAR(64)   PRIMARY KEY,
    template_id     VARCHAR(64)   NOT NULL,
    name            VARCHAR(256)  NOT NULL,
    category        VARCHAR(64),
    command         TEXT          NOT NULL,
    command_type    VARCHAR(16)   DEFAULT 'ssh',
    is_read_only    BOOLEAN       DEFAULT 1,
    warning_text    TEXT,
    parser          VARCHAR(32)   DEFAULT 'raw',
    parser_config   TEXT,
    threshold_metric VARCHAR(64),
    threshold_operator VARCHAR(8),
    threshold_critical REAL,
    threshold_warning REAL,
    threshold_unit  VARCHAR(16),
    expected_value  TEXT,
    suggestion      TEXT,
    weight          INTEGER       DEFAULT 10,
    sort_order      INTEGER       DEFAULT 1,
    FOREIGN KEY (template_id) REFERENCES inspection_templates(id) ON DELETE CASCADE
);

-- ============================================================
-- 巡检任务表
-- ============================================================
CREATE TABLE IF NOT EXISTS inspection_tasks (
    id              VARCHAR(64)   PRIMARY KEY,
    name            VARCHAR(256)  NOT NULL,
    template_id     VARCHAR(64)   NOT NULL,
    target_ids      TEXT,
    schedule_type   VARCHAR(16)   DEFAULT 'once',
    cron_expr       VARCHAR(64),
    status          VARCHAR(16)   DEFAULT 'pending',
    last_run_at     DATETIME,
    next_run_at     DATETIME,
    notify_email    TEXT,
    notify_webhook  VARCHAR(512),
    created_by      VARCHAR(64),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES inspection_templates(id)
);

-- ============================================================
-- 巡检结果表
-- ============================================================
CREATE TABLE IF NOT EXISTS inspection_results (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id         VARCHAR(64)   NOT NULL,
    target_id       INTEGER       NOT NULL,
    target_name     VARCHAR(256),
    item_id         VARCHAR(64)   NOT NULL,
    item_name       VARCHAR(256),
    category        VARCHAR(64),
    raw_value       TEXT,
    parsed_value    TEXT,
    status          VARCHAR(16)   DEFAULT 'ok',
    threshold_desc  TEXT,
    suggestion      TEXT,
    executed_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    duration_ms     INTEGER,
    FOREIGN KEY (task_id) REFERENCES inspection_tasks(id) ON DELETE CASCADE
);

-- ============================================================
-- 巡检报告表
-- ============================================================
CREATE TABLE IF NOT EXISTS inspection_reports (
    id              VARCHAR(64)   PRIMARY KEY,
    task_id         VARCHAR(64)   NOT NULL,
    task_name       VARCHAR(256),
    target_ids      TEXT,
    format          VARCHAR(8)    DEFAULT 'html',
    health_score    INTEGER       DEFAULT 0,
    total_items     INTEGER       DEFAULT 0,
    ok_count        INTEGER       DEFAULT 0,
    warning_count   INTEGER       DEFAULT 0,
    critical_count  INTEGER       DEFAULT 0,
    error_count     INTEGER       DEFAULT 0,
    skipped_count   INTEGER       DEFAULT 0,
    summary         TEXT,
    ai_analysis     TEXT,
    file_path       VARCHAR(512),
    generated_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES inspection_tasks(id)
);

-- ============================================================
-- 报告模板表
-- ============================================================
CREATE TABLE IF NOT EXISTS report_templates (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(128)  NOT NULL,
    description     TEXT,
    template_type   VARCHAR(16)   DEFAULT 'standard',
    is_default      BOOLEAN       DEFAULT 0,
    config_json     TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 巡检历史表（趋势分析）
-- ============================================================
CREATE TABLE IF NOT EXISTS inspection_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    target_id       INTEGER       NOT NULL,
    target_name     VARCHAR(256),
    task_id         VARCHAR(64),
    health_score    INTEGER,
    ok_count        INTEGER       DEFAULT 0,
    warning_count   INTEGER       DEFAULT 0,
    critical_count  INTEGER       DEFAULT 0,
    total_items     INTEGER       DEFAULT 0,
    summary         TEXT,
    snapshot_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- SNMP 采集历史表
-- ============================================================
CREATE TABLE IF NOT EXISTS snmp_collection_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    target_id       INTEGER       NOT NULL,
    template_id     VARCHAR(64),
    oid             VARCHAR(256)  NOT NULL,
    oid_name        VARCHAR(256),
    value           TEXT,
    value_type      VARCHAR(32),
    status          VARCHAR(16)   DEFAULT 'ok',
    error_message   TEXT,
    response_time_ms REAL,
    collected_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 创建索引
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_targets_type ON inspection_targets(target_type);
CREATE INDEX IF NOT EXISTS idx_targets_status ON inspection_targets(status);
CREATE INDEX IF NOT EXISTS idx_templates_type ON inspection_templates(target_type);
CREATE INDEX IF NOT EXISTS idx_templates_brand ON inspection_templates(brand);
CREATE INDEX IF NOT EXISTS idx_items_template ON inspection_items(template_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON inspection_tasks(status);
CREATE INDEX IF NOT EXISTS idx_results_task ON inspection_results(task_id);
CREATE INDEX IF NOT EXISTS idx_results_status ON inspection_results(status);
CREATE INDEX IF NOT EXISTS idx_results_target ON inspection_results(target_id);
CREATE INDEX IF NOT EXISTS idx_reports_task ON inspection_reports(task_id);
CREATE INDEX IF NOT EXISTS idx_reports_time ON inspection_reports(generated_at);
CREATE INDEX IF NOT EXISTS idx_history_target ON inspection_history(target_id);
CREATE INDEX IF NOT EXISTS idx_history_time ON inspection_history(snapshot_at);
CREATE INDEX IF NOT EXISTS idx_snmp_target ON snmp_collection_history(target_id);
CREATE INDEX IF NOT EXISTS idx_snmp_time ON snmp_collection_history(collected_at);
CREATE INDEX IF NOT EXISTS idx_oid_registry_vendor ON snmp_oid_registry(vendor);
CREATE INDEX IF NOT EXISTS idx_oid_registry_category ON snmp_oid_registry(category);

-- ============================================================
-- 插入默认报告模板
-- ============================================================
INSERT OR IGNORE INTO report_templates (id, name, description, template_type, is_default) VALUES
(1, '标准报告模板', '包含封面、健康度概览、问题汇总、详细结果、附录', 'standard', 1),
(2, '详细报告模板', '在标准模板基础上增加趋势图表和分析', 'detailed', 0),
(3, '简洁报告模板', '仅包含关键指标和问题汇总', 'compact', 0);
