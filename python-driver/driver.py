"""
AcdanteSQLMon Python 驱动适配层
统一 Oracle 数据库连接接口，支持多版本适配
"""
import os
import sys
import json
from typing import Optional, Dict, Any, List, Tuple

try:
    import oracledb
    HAS_ORACLEDB = True
except ImportError:
    HAS_ORACLEDB = False

try:
    import cx_Oracle
    HAS_CXORACLE = True
except ImportError:
    HAS_CXORACLE = False


# 版本映射
VERSION_MAP = {
    '10g': {'major': 10, 'driver': 'cx_Oracle', 'need_client': True,  'gv_supported': True},
    '11g': {'major': 11, 'driver': 'cx_Oracle', 'need_client': True,  'gv_supported': True},
    '19c': {'major': 19, 'driver': 'oracledb',  'need_client': False, 'gv_supported': True},
    '23c': {'major': 23, 'driver': 'oracledb',  'need_client': False, 'gv_supported': True},
    '26ai': {'major': 26, 'driver': 'oracledb',  'need_client': False, 'gv_supported': True},
}


class OracleDriver:
    """统一 Oracle 连接驱动"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.oracle_version = config.get('oracle_version', '19c')
        self.need_client = config.get('need_client', False)
        self.client_path = config.get('client_path', '')
        self._connection = None

    def _init_client(self):
        """初始化 Oracle Instant Client (10g/11g 需要)"""
        if self.need_client:
            if not self.client_path or not os.path.exists(self.client_path):
                raise RuntimeError(
                    f"Oracle Instant Client not found at: {self.client_path}\n"
                    f"Please download from: "
                    f"https://www.oracle.com/database/technologies/instant-client/downloads.html"
                )
            if HAS_ORACLEDB:
                oracledb.init_oracle_client(lib_dir=self.client_path)
            elif HAS_CXORACLE:
                # cx_Oracle uses LD_LIBRARY_PATH
                pass

    def connect(self):
        """建立连接"""
        if not HAS_ORACLEDB and not HAS_CXORACLE:
            raise RuntimeError("Neither oracledb nor cx_Oracle is installed. "
                             "Install with: pip install oracledb")

        self._init_client()

        # 构建 DSN
        dsn = oracledb.makedsn(
            self.config['host'],
            self.config.get('port', 1521),
            service_name=self.config.get('service_name'),
            sid=self.config.get('sid')
        )

        # 19c+ 使用 thin mode (无需客户端)
        if not self.need_client and self.oracle_version in ['19c', '23c', '26ai']:
            conn = oracledb.connect(
                user=self.config['username'],
                password=self.config['password'],
                dsn=dsn
            )
        else:
            # 10g/11g 需要 thick mode
            conn = oracledb.connect(
                user=self.config['username'],
                password=self.config['password'],
                dsn=dsn
            )

        self._connection = conn
        return conn

    def test_connection(self) -> Dict[str, Any]:
        """测试连接并返回实例信息"""
        conn = self.connect()
        cursor = conn.cursor()

        # 获取版本
        cursor.execute("SELECT BANNER FROM v$version WHERE ROWNUM = 1")
        version = cursor.fetchone()[0]

        # 获取实例信息
        cursor.execute("SELECT INSTANCE_NAME, HOST_NAME, STATUS FROM v$instance")
        row = cursor.fetchone()
        instance_name, host_name, status = row if row else ('', '', '')

        # 检测是否 RAC
        is_rac = False
        rac_instances = [1]
        try:
            cursor.execute("SELECT inst_id FROM gv$instance")
            rac_instances = [r[0] for r in cursor.fetchall()]
            is_rac = len(rac_instances) > 1
        except Exception:
            pass

        cursor.close()
        conn.close()

        return {
            "version": version,
            "instance_name": instance_name,
            "host_name": host_name,
            "status": status,
            "is_rac": is_rac,
            "rac_instances": rac_instances,
            "connect_success": True,
        }

    def close(self):
        """关闭连接"""
        if self._connection:
            self._connection.close()
            self._connection = None


class SQLAdapter:
    """根据 Oracle 版本选择合适的 SQL 语句"""

    def __init__(self, version: str):
        self.version = version
        self.info = VERSION_MAP.get(version, VERSION_MAP['19c'])
        self.major = self.info['major']

    def get_query(self, module: str, sub_query: str = '') -> str:
        """加载对应版本的 SQL"""
        base_dir = os.path.join(os.path.dirname(__file__), 'queries', module)

        # 尝试精确版本, 回退到最近的低版本
        candidates = [
            os.path.join(base_dir, f"{self.version}.sql"),
            os.path.join(base_dir, f"{self._nearest_version()}.sql"),
            os.path.join(base_dir, "common.sql"),
        ]
        for path in candidates:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return f.read()
        raise FileNotFoundError(f"No query found for {module} on {self.version}")

    def adapt_pagination(self, sql: str, limit: int, offset: int = 0) -> str:
        """分页语法适配"""
        if self.major >= 12:
            return f"{sql}\nOFFSET {offset} ROWS FETCH FIRST {limit} ROWS ONLY"
        else:
            return (
                f"SELECT * FROM (\n"
                f"  SELECT a.*, ROWNUM rn FROM (\n{sql}\n  ) a "
                f"WHERE ROWNUM <= {offset + limit}\n"
                f") WHERE rn > {offset}"
            )

    def adapt_fetch_first(self, sql: str, n: int) -> str:
        """FETCH FIRST 语法适配"""
        if self.major >= 12:
            return f"{sql}\nFETCH FIRST {n} ROWS ONLY"
        else:
            return f"SELECT * FROM ({sql}) WHERE ROWNUM <= {n}"

    def _nearest_version(self) -> str:
        """找到最近的低版本"""
        for v in ['23c', '19c', '11g', '10g']:
            if VERSION_MAP[v]['major'] <= self.major:
                return v
        return '10g'


def get_wait_events_sql(version: str, inst_id: Optional[int] = None) -> str:
    """获取等待事件查询 SQL"""
    adapter = SQLAdapter(version)

    if adapter.major >= 19:
        # 19c+ 增强查询
        inst_filter = f"AND sw.inst_id = {inst_id}" if inst_id else ""
        return f"""
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
  {inst_filter}
ORDER BY sw.seconds_in_wait DESC
"""
    else:
        # 10g/11g 兼容版
        inst_filter = f"AND sw.inst_id = {inst_id}" if inst_id else ""
        idle_events = (
            "'SQL*Net message from client', "
            "'SQL*Net message to client', "
            "'rdbms ipc message', "
            "'pmon timer', "
            "'smon timer'"
        )
        return f"""
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
  AND sw.event NOT IN ({idle_events})
  {inst_filter}
ORDER BY sw.seconds_in_wait DESC
"""


def get_locks_sql(version: str) -> str:
    """获取锁信息查询 SQL (通用, 兼容 10g~26ai)"""
    return """
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
ORDER BY s.seconds_in_wait DESC
"""


def get_deadlock_sql(version: str) -> str:
    """获取死锁检测 SQL"""
    return """
WITH lock_chain AS (
    SELECT
        s.inst_id, s.sid, s.serial#, s.username,
        s.sql_id, s.blocking_session, s.blocking_instance,
        s.seconds_in_wait, s.program, s.machine, p.spid
    FROM gv$session s
    JOIN gv$process p ON p.addr = s.paddr AND p.inst_id = s.inst_id
    WHERE s.blocking_session IS NOT NULL
      AND s.type = 'USER'
)
SELECT
    a.inst_id AS waiter_inst_id,
    a.sid AS waiter_sid,
    a.serial# AS waiter_serial,
    a.username AS waiter_user,
    a.sql_id AS waiter_sql_id,
    b.sid AS blocker_sid,
    b.inst_id AS blocker_inst_id,
    b.username AS blocker_user,
    b.sql_id AS blocker_sql_id,
    CASE WHEN b.blocking_session = a.sid THEN 'DEADLOCK' ELSE 'CHAIN' END AS lock_type,
    a.seconds_in_wait AS wait_seconds,
    'ALTER SYSTEM KILL SESSION ''' || a.sid || ',' || a.serial# || ',@' || a.inst_id || ''' IMMEDIATE;' AS kill_cmd,
    'kill -9 ' || a.spid AS os_kill_cmd
FROM lock_chain a
JOIN lock_chain b ON a.blocking_session = b.sid
                  AND (a.blocking_instance = b.inst_id OR a.blocking_instance IS NULL)
ORDER BY lock_type DESC, a.seconds_in_wait DESC
"""


def get_session_detail_sql(version: str) -> str:
    """获取会话完整信息 SQL (用于查杀审计)"""
    return """
SELECT
    s.inst_id, s.sid, s.serial#,
    s.username, s.machine, s.program, s.osuser,
    s.process AS client_pid, p.spid AS server_pid,
    s.sql_id, sq.sql_text, sq.sql_fulltext,
    s.blocking_session, s.blocking_instance,
    s.wait_class, s.event, s.seconds_in_wait,
    s.status, s.state, s.logon_time, s.last_call_et, s.type,
    l.lock_type, l.mode_held, l.mode_requested,
    'ALTER SYSTEM KILL SESSION ''' || s.sid || ',' || s.serial# || ',@' || s.inst_id || ''' IMMEDIATE;' AS kill_session_cmd,
    'ALTER SYSTEM DISCONNECT SESSION ''' || s.sid || ',' || s.serial# || ',@' || s.inst_id || ''' POST_TRANSACTION;' AS disconnect_cmd,
    'kill -9 ' || p.spid AS os_kill_cmd
FROM gv$session s
JOIN gv$process p ON p.addr = s.paddr AND p.inst_id = s.inst_id
LEFT JOIN gv$sql sq ON sq.sql_id = s.sql_id AND sq.inst_id = s.inst_id AND sq.child_number = 0
LEFT JOIN gv$lock l ON l.session_id = s.sid AND l.inst_id = s.inst_id
WHERE s.sid = :sid AND s.inst_id = :inst_id
"""


if __name__ == '__main__':
    # 测试入口
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        print("AcdanteSQLMon Python Driver - Test Mode")
        print(f"oracledb available: {HAS_ORACLEDB}")
        print(f"cx_Oracle available: {HAS_CXORACLE}")

        # 测试 SQL 适配
        for ver in ['10g', '11g', '19c', '23c', '26ai']:
            adapter = SQLAdapter(ver)
            print(f"\n--- {ver} (major={adapter.major}) ---")
            print(f"Pagination: {adapter.adapt_pagination('SELECT * FROM t', 10, 0)[:80]}...")
