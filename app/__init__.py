"""
個人記帳簿系統 — Flask 應用程式工廠

初始化 Flask app、註冊 Blueprint、建立資料庫。
"""

import os
import sqlite3

from flask import Flask
from config import Config


def create_app(config_class=Config):
    """
    Flask Application Factory

    建立並設定 Flask 應用程式實例。

    Args:
        config_class: 設定類別，預設使用 Config

    Returns:
        Flask app 實例
    """
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    app.config.from_object(config_class)

    # 確保 instance 資料夾存在
    os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)

    # 初始化資料庫
    init_db(app)

    # 註冊 Blueprint
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.routes.records import bp as records_bp
    app.register_blueprint(records_bp)

    from app.routes.reports import bp as reports_bp
    app.register_blueprint(reports_bp)

    return app


def init_db(app):
    """
    初始化資料庫

    讀取 database/schema.sql 並執行建表語法。
    如果資料表已存在則不會重複建立（使用 IF NOT EXISTS）。
    """
    db_path = app.config['DATABASE']
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'schema.sql')

    # 如果 schema.sql 不存在，使用內建的建表語法
    if os.path.exists(schema_path):
        conn = sqlite3.connect(db_path)
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            conn.commit()
        finally:
            conn.close()
    else:
        conn = sqlite3.connect(db_path)
        try:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS records (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    type       TEXT    NOT NULL CHECK(type IN ('income', 'expense')),
                    amount     REAL    NOT NULL CHECK(amount > 0),
                    category   TEXT    NOT NULL,
                    note       TEXT    DEFAULT '',
                    date       TEXT    NOT NULL,
                    created_at TEXT    DEFAULT (datetime('now', 'localtime'))
                );
                CREATE INDEX IF NOT EXISTS idx_records_date     ON records(date);
                CREATE INDEX IF NOT EXISTS idx_records_type     ON records(type);
                CREATE INDEX IF NOT EXISTS idx_records_category ON records(category);
            ''')
            conn.commit()
        finally:
            conn.close()
