-- 会话完整信息查询 (用于查杀审计记录)
SELECT
    s.inst_id,
    s.sid,
    s.serial#,
    s.username,
    s.machine,
    s.program,
    s.osuser,
    s.process AS client_pid,
    p.spid AS server_pid,
    s.sql_id,
    sq.sql_text,
    sq.sql_fulltext,
    s.blocking_session,
    s.blocking_instance,
    s.wait_class,
    s.event,
    s.seconds_in_wait,
    s.status,
    s.state,
    s.logon_time,
    s.last_call_et,
    s.type,
    l.lock_type,
    l.mode_held,
    l.mode_requested,
    'ALTER SYSTEM KILL SESSION ''' || s.sid || ',' || s.serial# || ',@' || s.inst_id || ''' IMMEDIATE;' AS kill_session_cmd,
    'ALTER SYSTEM DISCONNECT SESSION ''' || s.sid || ',' || s.serial# || ',@' || s.inst_id || ''' POST_TRANSACTION;' AS disconnect_cmd,
    'kill -9 ' || p.spid AS os_kill_cmd
FROM gv$session s
JOIN gv$process p ON p.addr = s.paddr AND p.inst_id = s.inst_id
LEFT JOIN gv$sql sq ON sq.sql_id = s.sql_id AND sq.inst_id = s.inst_id AND sq.child_number = 0
LEFT JOIN gv$lock l ON l.session_id = s.sid AND l.inst_id = s.inst_id
WHERE s.sid = :sid
  AND s.inst_id = :inst_id;
