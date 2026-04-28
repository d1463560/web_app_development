"""
Records Routes — 收支記錄 CRUD

處理收支記錄的新增、查看、編輯與刪除操作。
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

bp = Blueprint('records', __name__)


# ==================== 新增記錄 ====================

@bp.route('/add', methods=['GET'])
def add_form():
    """
    新增記錄（頁面）

    GET /add
    - 輸入：無
    - 處理：準備收入/支出分類選項列表
    - 輸出：渲染 add.html，傳入分類選項與今天日期
    """
    pass


@bp.route('/add', methods=['POST'])
def add_submit():
    """
    新增記錄（送出）

    POST /add
    - 輸入：表單欄位 type、amount、category、note、date
    - 處理：
        1. 驗證輸入（type 為 income/expense、amount > 0、date 格式正確）
        2. 呼叫 Record.create() 新增記錄
    - 輸出：
        成功 → flash 成功訊息，重導向至 /
        失敗 → flash 錯誤訊息，重導向回 /add
    """
    pass


# ==================== 每日明細 ====================

@bp.route('/daily', methods=['GET'])
def daily():
    """
    每日收支明細

    GET /daily
    - 輸入：Query Parameter `date`（可選，格式 YYYY-MM-DD，預設今天）
    - 處理：呼叫 Record.get_by_date(date) 取得當天記錄
    - 輸出：渲染 daily.html，傳入 records、selected_date
    - 錯誤處理：日期格式錯誤時使用今天日期
    """
    pass


# ==================== 編輯記錄 ====================

@bp.route('/edit/<int:id>', methods=['GET'])
def edit_form(id):
    """
    編輯記錄（頁面）

    GET /edit/<id>
    - 輸入：URL 參數 id（記錄 ID）
    - 處理：呼叫 Record.get_by_id(id) 取得記錄資料
    - 輸出：渲染 edit.html，傳入 record 與分類選項
    - 錯誤處理：記錄不存在 → 回傳 404
    """
    pass


@bp.route('/edit/<int:id>', methods=['POST'])
def edit_submit(id):
    """
    編輯記錄（送出）

    POST /edit/<id>
    - 輸入：URL 參數 id；表單欄位 type、amount、category、note、date
    - 處理：
        1. 驗證輸入
        2. 呼叫 Record.update(id, ...) 更新記錄
    - 輸出：
        成功 → flash 成功訊息，重導向至 /daily?date=記錄日期
        失敗 → flash 錯誤訊息，重導向回 /edit/<id>
    - 錯誤處理：記錄不存在 → 404；驗證失敗 → flash 錯誤
    """
    pass


# ==================== 刪除記錄 ====================

@bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """
    刪除記錄

    POST /delete/<id>
    - 輸入：URL 參數 id（記錄 ID）
    - 處理：呼叫 Record.delete(id) 刪除記錄
    - 輸出：flash 成功訊息，重導向至 /daily
    - 錯誤處理：記錄不存在 → flash 錯誤訊息，重導向至 /daily
    """
    pass
