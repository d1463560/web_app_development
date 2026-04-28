-- ============================================
-- 個人記帳簿系統 — 資料庫 Schema
-- 資料庫：SQLite
-- ============================================

-- 建立 records 資料表
-- 用於儲存所有收入與支出記錄
CREATE TABLE IF NOT EXISTS records (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    type       TEXT    NOT NULL CHECK(type IN ('income', 'expense')),
    amount     REAL    NOT NULL CHECK(amount > 0),
    category   TEXT    NOT NULL,
    note       TEXT    DEFAULT '',
    date       TEXT    NOT NULL,
    created_at TEXT    DEFAULT (datetime('now', 'localtime'))
);

-- 建立索引以加速查詢效能
CREATE INDEX IF NOT EXISTS idx_records_date     ON records(date);
CREATE INDEX IF NOT EXISTS idx_records_type     ON records(type);
CREATE INDEX IF NOT EXISTS idx_records_category ON records(category);
