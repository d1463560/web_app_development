"""
Record Model — 收支記錄資料模型

使用原生 sqlite3 操作 SQLite 資料庫，提供收支記錄的 CRUD 方法。
"""

import sqlite3
from datetime import datetime, date


class Record:
    """收支記錄的資料模型，封裝所有資料庫操作。"""

    def __init__(self, id, type, amount, category, note, date, created_at):
        self.id = id
        self.type = type            # 'income' 或 'expense'
        self.amount = amount        # 金額（正數）
        self.category = category    # 分類名稱
        self.note = note            # 備註
        self.date = date            # 記錄日期 (YYYY-MM-DD)
        self.created_at = created_at  # 建立時間

    def to_dict(self):
        """將 Record 物件轉換為字典。"""
        return {
            'id': self.id,
            'type': self.type,
            'amount': self.amount,
            'category': self.category,
            'note': self.note,
            'date': self.date,
            'created_at': self.created_at,
        }

    @staticmethod
    def _get_db(db_path):
        """取得資料庫連線。"""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _row_to_record(row):
        """將資料庫查詢結果轉換為 Record 物件。"""
        if row is None:
            return None
        return Record(
            id=row['id'],
            type=row['type'],
            amount=row['amount'],
            category=row['category'],
            note=row['note'],
            date=row['date'],
            created_at=row['created_at'],
        )

    # ==================== CRUD 操作 ====================

    @staticmethod
    def create(db_path, type, amount, category, note='', record_date=None):
        """
        新增一筆收支記錄。

        Args:
            db_path: 資料庫檔案路徑
            type: 記錄類型 ('income' 或 'expense')
            amount: 金額（正數）
            category: 分類名稱
            note: 備註（可選）
            record_date: 記錄日期，預設為今天 (YYYY-MM-DD)

        Returns:
            新建立的 Record 物件
        """
        if record_date is None:
            record_date = date.today().isoformat()

        conn = Record._get_db(db_path)
        try:
            cursor = conn.execute(
                '''INSERT INTO records (type, amount, category, note, date)
                   VALUES (?, ?, ?, ?, ?)''',
                (type, amount, category, note, record_date)
            )
            conn.commit()
            return Record.get_by_id(db_path, cursor.lastrowid)
        finally:
            conn.close()

    @staticmethod
    def get_all(db_path, order_by='date DESC'):
        """
        取得所有記錄。

        Args:
            db_path: 資料庫檔案路徑
            order_by: 排序方式，預設依日期降冪

        Returns:
            Record 物件的列表
        """
        conn = Record._get_db(db_path)
        try:
            rows = conn.execute(
                f'SELECT * FROM records ORDER BY {order_by}'
            ).fetchall()
            return [Record._row_to_record(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def get_by_id(db_path, record_id):
        """
        依 ID 取得單筆記錄。

        Args:
            db_path: 資料庫檔案路徑
            record_id: 記錄 ID

        Returns:
            Record 物件，若不存在則回傳 None
        """
        conn = Record._get_db(db_path)
        try:
            row = conn.execute(
                'SELECT * FROM records WHERE id = ?',
                (record_id,)
            ).fetchone()
            return Record._row_to_record(row)
        finally:
            conn.close()

    @staticmethod
    def get_by_date(db_path, target_date):
        """
        依日期取得當天所有記錄。

        Args:
            db_path: 資料庫檔案路徑
            target_date: 日期字串 (YYYY-MM-DD)

        Returns:
            Record 物件的列表
        """
        conn = Record._get_db(db_path)
        try:
            rows = conn.execute(
                'SELECT * FROM records WHERE date = ? ORDER BY created_at DESC',
                (target_date,)
            ).fetchall()
            return [Record._row_to_record(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def update(db_path, record_id, type, amount, category, note='', record_date=None):
        """
        更新指定記錄。

        Args:
            db_path: 資料庫檔案路徑
            record_id: 記錄 ID
            type: 記錄類型
            amount: 金額
            category: 分類名稱
            note: 備註
            record_date: 記錄日期

        Returns:
            更新後的 Record 物件
        """
        conn = Record._get_db(db_path)
        try:
            conn.execute(
                '''UPDATE records
                   SET type = ?, amount = ?, category = ?, note = ?, date = ?
                   WHERE id = ?''',
                (type, amount, category, note, record_date, record_id)
            )
            conn.commit()
            return Record.get_by_id(db_path, record_id)
        finally:
            conn.close()

    @staticmethod
    def delete(db_path, record_id):
        """
        刪除指定記錄。

        Args:
            db_path: 資料庫檔案路徑
            record_id: 記錄 ID

        Returns:
            是否成功刪除（True/False）
        """
        conn = Record._get_db(db_path)
        try:
            cursor = conn.execute(
                'DELETE FROM records WHERE id = ?',
                (record_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    # ==================== 統計查詢 ====================

    @staticmethod
    def get_summary(db_path, month=None):
        """
        取得總收入、總支出與結餘。

        Args:
            db_path: 資料庫檔案路徑
            month: 月份篩選 (YYYY-MM)，None 表示全部

        Returns:
            字典：{'total_income': float, 'total_expense': float, 'balance': float}
        """
        conn = Record._get_db(db_path)
        try:
            if month:
                # 依月份篩選：date 欄位前 7 碼為 YYYY-MM
                income_row = conn.execute(
                    "SELECT COALESCE(SUM(amount), 0) as total FROM records WHERE type = 'income' AND substr(date, 1, 7) = ?",
                    (month,)
                ).fetchone()
                expense_row = conn.execute(
                    "SELECT COALESCE(SUM(amount), 0) as total FROM records WHERE type = 'expense' AND substr(date, 1, 7) = ?",
                    (month,)
                ).fetchone()
            else:
                income_row = conn.execute(
                    "SELECT COALESCE(SUM(amount), 0) as total FROM records WHERE type = 'income'"
                ).fetchone()
                expense_row = conn.execute(
                    "SELECT COALESCE(SUM(amount), 0) as total FROM records WHERE type = 'expense'"
                ).fetchone()

            total_income = income_row['total']
            total_expense = expense_row['total']

            return {
                'total_income': total_income,
                'total_expense': total_expense,
                'balance': total_income - total_expense,
            }
        finally:
            conn.close()

    @staticmethod
    def get_expense_by_category(db_path, month=None):
        """
        取得各分類的支出統計（用於圓餅圖）。

        Args:
            db_path: 資料庫檔案路徑
            month: 月份篩選 (YYYY-MM)，None 表示全部

        Returns:
            列表：[{'category': str, 'total': float}, ...]
        """
        conn = Record._get_db(db_path)
        try:
            if month:
                rows = conn.execute(
                    """SELECT category, SUM(amount) as total
                       FROM records
                       WHERE type = 'expense' AND substr(date, 1, 7) = ?
                       GROUP BY category
                       ORDER BY total DESC""",
                    (month,)
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT category, SUM(amount) as total
                       FROM records
                       WHERE type = 'expense'
                       GROUP BY category
                       ORDER BY total DESC"""
                ).fetchall()

            return [{'category': row['category'], 'total': row['total']} for row in rows]
        finally:
            conn.close()

    @staticmethod
    def get_daily_summary(db_path, month=None):
        """
        取得每日的收支統計（用於折線圖）。

        Args:
            db_path: 資料庫檔案路徑
            month: 月份篩選 (YYYY-MM)，None 表示全部

        Returns:
            列表：[{'date': str, 'income': float, 'expense': float}, ...]
        """
        conn = Record._get_db(db_path)
        try:
            if month:
                rows = conn.execute(
                    """SELECT date,
                              COALESCE(SUM(CASE WHEN type = 'income' THEN amount END), 0) as income,
                              COALESCE(SUM(CASE WHEN type = 'expense' THEN amount END), 0) as expense
                       FROM records
                       WHERE substr(date, 1, 7) = ?
                       GROUP BY date
                       ORDER BY date""",
                    (month,)
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT date,
                              COALESCE(SUM(CASE WHEN type = 'income' THEN amount END), 0) as income,
                              COALESCE(SUM(CASE WHEN type = 'expense' THEN amount END), 0) as expense
                       FROM records
                       GROUP BY date
                       ORDER BY date"""
                ).fetchall()

            return [{'date': row['date'], 'income': row['income'], 'expense': row['expense']} for row in rows]
        finally:
            conn.close()
