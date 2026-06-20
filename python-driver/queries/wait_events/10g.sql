-- 等待事件查询 (10g/11g 兼容版)
-- 无 WAIT_CLASS 关联, 使用事件排除法过滤 Idle 事件
SELECT
    s.inst_id,
    s.sid,
    s.serial#,
    s.username,
    s.machine,
    s.program,
    sw.event,
    sw.p1text, sw.p1, sw.p2text, sw.p2, sw.p3text, sw.p3,
    sw.wait_time,
    sw.seconds_in_wait,
    sw.state,
    s.sql_id,
    s.blocking_session,
    s.blocking_instance,
    s.status
FROM gv$session_wait sw
JOIN gv$session s ON s.inst_id = sw.inst_id AND s.sid = sw.sid
WHERE s.type = 'USER'
  AND s.status = 'ACTIVE'
  AND sw.event NOT IN (
      'SQL*Net message from client',
      'SQL*Net message to client',
      'rdbms ipc message',
      'pmon timer',
      'smon timer',
      'pipe get',
      'client message'
  )
ORDER BY sw.seconds_in_wait DESC;
