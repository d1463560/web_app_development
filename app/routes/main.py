"""
Main Routes — 首頁儀表板

處理首頁相關的路由，顯示總收入、總支出與結餘統計。
"""

from flask import Blueprint, render_template, request, current_app
from app.models.record import Record

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
    month = request.args.get('month')
    db_path = current_app.config['DATABASE']
    summary = Record.get_summary(db_path, month)
    
    return render_template('index.html', 
                           total_income=summary['total_income'], 
                           total_expense=summary['total_expense'], 
                           balance=summary['balance'], 
                           month=month)
