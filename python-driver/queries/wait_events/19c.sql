-- 等待事件查询 (19c/23c/26ai 增强版)
-- 支持 GV$ 全局视图, 兼容 RAC 集群
-- 19c+ 新增 FINAL_BLOCKING_SESSION
SELECT
    s.inst_id,
    s.sid,
    s.serial#,
    s.username,
    s.machine,
    s.program,
    sw.event,
    en.wait_class,
    sw.seconds_in_wait,
    s.sql_id,
    s.blocking_session,
    s.blocking_instance,
    s.final_blocking_session,
    s.final_blocking_instance,
    s.status,
    s.state
FROM gv$session_wait sw
JOIN gv$session s ON s.inst_id = sw.inst_id AND s.sid = sw.sid
LEFT JOIN v$event_name en ON en.event# = sw.event#
WHERE s.type = 'USER'
  AND s.status = 'ACTIVE'
  AND en.wait_class != 'Idle'
ORDER BY sw.seconds_in_wait DESC;
