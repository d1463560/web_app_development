"""
Reports Routes — 財務報表

處理財務報表頁面，提供支出分類統計與收支趨勢圖表資料。
"""

from flask import Blueprint, render_template, request

bp = Blueprint('reports', __name__)


@bp.route('/report', methods=['GET'])
def report():
    """
    財務報表

    GET /report
    - 輸入：Query Parameter `month`（可選，格式 YYYY-MM）
    - 處理：
        1. 呼叫 Record.get_expense_by_category(month) 取得分類統計
        2. 呼叫 Record.get_daily_summary(month) 取得每日統計
    - 輸出：渲染 report.html，傳入 category_data、daily_data、month
    - 錯誤處理：無資料時顯示「尚無記錄」提示
    """
    pass
