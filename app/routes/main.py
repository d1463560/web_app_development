"""
Main Routes — 首頁儀表板

處理首頁相關的路由，顯示總收入、總支出與結餘統計。
"""

from flask import Blueprint, render_template, request

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """
    首頁儀表板

    GET /
    - 輸入：Query Parameter `month`（可選，格式 YYYY-MM）
    - 處理：呼叫 Record.get_summary(month) 取得統計數據
    - 輸出：渲染 index.html，傳入 total_income、total_expense、balance、month
    """
    pass
