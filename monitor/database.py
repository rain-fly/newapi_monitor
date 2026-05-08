import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict


class Database:
    """数据库管理类"""

    def __init__(self, db_path: str = "data/monitor.db"):
        self.db_path = db_path
        self._ensure_dir()
        self._init_db()

    def _ensure_dir(self):
        """确保数据库目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def _init_db(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 检查是否存在表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_records'")
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            cursor.execute("""
                CREATE TABLE test_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    model TEXT,
                    available INTEGER NOT NULL,
                    latency_ms REAL,
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            # 检查是否存在 model 列
            cursor.execute("PRAGMA table_info(test_records)")
            columns = [col[1] for col in cursor.fetchall()]

            if "model" not in columns:
                cursor.execute("ALTER TABLE test_records ADD COLUMN model TEXT")

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_records_model ON test_records(model)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_records_timestamp ON test_records(timestamp)")

        # 创建 model_tags 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT UNIQUE NOT NULL,
                vendor TEXT,
                use_cases TEXT,
                language_strengths TEXT,
                raw_response TEXT,
                classified_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_model_tags_model ON model_tags(model)")

        conn.commit()
        conn.close()

    def insert_record(self, available: bool, latency_ms: Optional[float] = None,
                      error_message: Optional[str] = None, retry_count: int = 0,
                      model: Optional[str] = None) -> int:
        """插入测试记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO test_records (timestamp, model, available, latency_ms, error_message, retry_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp, model, 1 if available else 0, latency_ms, error_message, retry_count))
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return record_id

    def get_recent_records(self, minutes: int, model: Optional[str] = None) -> List[Dict]:
        """获取最近N分钟内的测试记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(minutes=minutes)).isoformat()

        if model:
            cursor.execute("""
                SELECT timestamp, model, available, latency_ms, error_message
                FROM test_records
                WHERE timestamp >= ? AND model = ?
                ORDER BY timestamp DESC
            """, (cutoff, model))
        else:
            cursor.execute("""
                SELECT timestamp, model, available, latency_ms, error_message
                FROM test_records
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            """, (cutoff,))

        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "timestamp": row[0],
                "model": row[1],
                "available": bool(row[2]),
                "latency_ms": row[3],
                "error_message": row[4]
            }
            for row in rows
        ]

    def get_all_recent_records(self, hours: int, model: Optional[str] = None) -> List[Dict]:
        """获取最近N小时内的所有测试记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()

        if model:
            cursor.execute("""
                SELECT timestamp, model, available, latency_ms
                FROM test_records
                WHERE timestamp >= ? AND model = ?
                ORDER BY timestamp ASC
            """, (cutoff, model))
        else:
            cursor.execute("""
                SELECT timestamp, model, available, latency_ms
                FROM test_records
                WHERE timestamp >= ?
                ORDER BY timestamp ASC
            """, (cutoff,))

        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "timestamp": row[0],
                "model": row[1],
                "available": bool(row[2]),
                "latency_ms": row[3]
            }
            for row in rows
        ]

    def get_all_models(self) -> List[str]:
        """获取所有出现过的模型列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT model FROM test_records
            WHERE model IS NOT NULL AND model != ''
            ORDER BY model
        """)
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def cleanup_old_records(self, days: int):
        """清理超过N天的旧记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        cursor.execute("DELETE FROM test_records WHERE timestamp < ?", (cutoff,))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted

    def get_latest_record(self, model: Optional[str] = None) -> Optional[Dict]:
        """获取最新一条测试记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if model:
            cursor.execute("""
                SELECT timestamp, model, available, latency_ms, error_message
                FROM test_records
                WHERE model = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (model,))
        else:
            cursor.execute("""
                SELECT timestamp, model, available, latency_ms, error_message
                FROM test_records
                ORDER BY timestamp DESC
                LIMIT 1
            """)

        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "timestamp": row[0],
                "model": row[1],
                "available": bool(row[2]),
                "latency_ms": row[3],
                "error_message": row[4]
            }
        return None

    def get_latest_record_by_model(self) -> Dict[str, Optional[Dict]]:
        """获取每个模型的最新一条测试记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t1.timestamp, t1.model, t1.available, t1.latency_ms, t1.error_message
            FROM test_records t1
            INNER JOIN (
                SELECT model, MAX(timestamp) as max_ts
                FROM test_records
                WHERE model IS NOT NULL AND model != ''
                GROUP BY model
            ) t2 ON t1.model = t2.model AND t1.timestamp = t2.max_ts
            ORDER BY t1.model
        """)
        rows = cursor.fetchall()
        conn.close()

        result = {}
        for row in rows:
            result[row[1]] = {
                "timestamp": row[0],
                "model": row[1],
                "available": bool(row[2]),
                "latency_ms": row[3],
                "error_message": row[4]
            }
        return result

    def get_model_tags(self, model: str) -> Optional[Dict]:
        """获取指定模型的分类标签"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT model, vendor, use_cases, language_strengths
            FROM model_tags WHERE model = ?
        """, (model,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "model": row[0],
                "vendor": row[1],
                "use_cases": row[2],
                "language_strengths": row[3]
            }
        return None

    def upsert_model_tags(self, model: str, vendor: str, use_cases: str,
                          language_strengths: str, raw_response: str):
        """插入或更新模型分类标签"""
        import json
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO model_tags (model, vendor, use_cases, language_strengths, raw_response, classified_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(model) DO UPDATE SET
                vendor=excluded.vendor,
                use_cases=excluded.use_cases,
                language_strengths=excluded.language_strengths,
                raw_response=excluded.raw_response,
                updated_at=excluded.updated_at
        """, (model, vendor, use_cases, language_strengths, raw_response, now, now))
        conn.commit()
        conn.close()

    def get_uncategorized_models(self) -> List[str]:
        """获取没有分类标签的模型列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT model FROM test_records
            WHERE model IS NOT NULL AND model != ''
            AND model NOT IN (SELECT model FROM model_tags)
            ORDER BY model
        """)
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def get_all_tags(self) -> Dict:
        """获取所有标签聚合（标签云）"""
        import json
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT vendor, use_cases, language_strengths FROM model_tags")
        rows = cursor.fetchall()
        conn.close()

        vendors = {}
        use_cases = {}
        languages = {}

        for row in rows:
            if row[0] and row[0] != "unknown":
                vendors[row[0]] = vendors.get(row[0], 0) + 1
            if row[1]:
                try:
                    for uc in json.loads(row[1]):
                        use_cases[uc] = use_cases.get(uc, 0) + 1
                except (json.JSONDecodeError, TypeError):
                    pass
            if row[2]:
                try:
                    for lang in json.loads(row[2]):
                        languages[lang] = languages.get(lang, 0) + 1
                except (json.JSONDecodeError, TypeError):
                    pass

        return {
            "vendors": [{"name": k, "count": v} for k, v in sorted(vendors.items(), key=lambda x: -x[1])],
            "use_cases": [{"name": k, "count": v} for k, v in sorted(use_cases.items(), key=lambda x: -x[1])],
            "language_strengths": [{"name": k, "count": v} for k, v in sorted(languages.items(), key=lambda x: -x[1])]
        }
