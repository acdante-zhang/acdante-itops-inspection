-- 锁信息查询 (通用版, 兼容 10g~26ai)
-- 支持 GV$ 全局视图, 兼容 RAC 集群
SELECT
    lo.inst_id,
    lo.session_id      AS sid,
    s.serial#,
    s.username,
    s.machine,
    s.program,
    s.osuser,
    s.process          AS os_pid,
    lo.lock_type,
    lo.mode_held,
    lo.mode_requested,
    lo.lock_id1,
    lo.lock_id2,
    do.owner || '.' || do.object_name AS object_name,
    do.object_type,
    s.sql_id,
    s.blocking_session,
    s.blocking_instance,
    s.seconds_in_wait AS hold_seconds,
    s.status,
    s.state,
    CASE
        WHEN s.seconds_in_wait > 600 THEN 'CRITICAL'
        WHEN s.seconds_in_wait > 300 THEN 'WARNING'
        WHEN s.blocking_session IS NOT NULL THEN 'BLOCKED'
        ELSE 'NORMAL'
    END AS severity,
    'ALTER SYSTEM KILL SESSION ''' || s.sid || ',' || s.serial# || ',@' || lo.inst_id || ''' IMMEDIATE;' AS kill_session_cmd,
    p.spid AS server_pid
FROM gv$lock lo
JOIN gv$session s ON s.inst_id = lo.inst_id AND s.sid = lo.session_id
LEFT JOIN gv$locked_object lobj ON lobj.session_id = lo.session_id AND lobj.inst_id = lo.inst_id
LEFT JOIN dba_objects do ON do.object_id = lobj.object_id
LEFT JOIN gv$process p ON p.addr = s.paddr AND p.inst_id = s.inst_id
WHERE lo.mode_requested != 'None'
   OR s.blocking_session IS NOT NULL
ORDER BY s.seconds_in_wait DESC;
