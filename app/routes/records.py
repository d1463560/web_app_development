"""
Records Routes — 收支記錄 CRUD

處理收支記錄的新增、查看、編輯與刪除操作。
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.models.record import Record
from datetime import date, datetime

bp = Blueprint('records', __name__)

INCOME_CATEGORIES = ['薪資', '獎金', '兼職', '投資收益', '其他']
EXPENSE_CATEGORIES = ['餐飲', '交通', '娛樂', '購物', '日用品', '醫療', '教育', '其他']

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
    today = date.today().isoformat()
    return render_template('add.html', 
                           income_categories=INCOME_CATEGORIES,
                           expense_categories=EXPENSE_CATEGORIES,
                           today=today)


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
    r_type = request.form.get('type')
    amount_str = request.form.get('amount')
    category = request.form.get('category')
    note = request.form.get('note', '')
    r_date = request.form.get('date')

    if not all([r_type, amount_str, category, r_date]):
        flash('請填寫所有必填欄位', 'danger')
        return redirect(url_for('records.add_form'))

    if r_type not in ['income', 'expense']:
        flash('記錄類型錯誤', 'danger')
        return redirect(url_for('records.add_form'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash('金額必須為大於 0 的有效數字', 'danger')
        return redirect(url_for('records.add_form'))

    try:
        datetime.strptime(r_date, '%Y-%m-%d')
    except ValueError:
        flash('日期格式錯誤', 'danger')
        return redirect(url_for('records.add_form'))

    db_path = current_app.config['DATABASE']
    Record.create(db_path, r_type, amount, category, note, r_date)
    flash('記錄新增成功！', 'success')
    return redirect(url_for('main.index'))


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
    selected_date = request.args.get('date')
    if not selected_date:
        selected_date = date.today().isoformat()
    else:
        try:
            datetime.strptime(selected_date, '%Y-%m-%d')
        except ValueError:
            selected_date = date.today().isoformat()

    db_path = current_app.config['DATABASE']
    records = Record.get_by_date(db_path, selected_date)
    
    return render_template('daily.html', records=records, selected_date=selected_date)


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
    db_path = current_app.config['DATABASE']
    record = Record.get_by_id(db_path, id)
    if not record:
        flash('找不到該筆記錄', 'danger')
        return redirect(url_for('main.index'))
        
    return render_template('edit.html', 
                           record=record,
                           income_categories=INCOME_CATEGORIES,
                           expense_categories=EXPENSE_CATEGORIES)


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
    db_path = current_app.config['DATABASE']
    record = Record.get_by_id(db_path, id)
    if not record:
        flash('找不到該筆記錄', 'danger')
        return redirect(url_for('main.index'))

    r_type = request.form.get('type')
    amount_str = request.form.get('amount')
    category = request.form.get('category')
    note = request.form.get('note', '')
    r_date = request.form.get('date')

    if not all([r_type, amount_str, category, r_date]):
        flash('請填寫所有必填欄位', 'danger')
        return redirect(url_for('records.edit_form', id=id))

    if r_type not in ['income', 'expense']:
        flash('記錄類型錯誤', 'danger')
        return redirect(url_for('records.edit_form', id=id))

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash('金額必須為大於 0 的有效數字', 'danger')
        return redirect(url_for('records.edit_form', id=id))

    try:
        datetime.strptime(r_date, '%Y-%m-%d')
    except ValueError:
        flash('日期格式錯誤', 'danger')
        return redirect(url_for('records.edit_form', id=id))

    Record.update(db_path, id, r_type, amount, category, note, r_date)
    flash('記錄更新成功！', 'success')
    return redirect(url_for('records.daily', date=r_date))


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
    db_path = current_app.config['DATABASE']
    success = Record.delete(db_path, id)
    if success:
        flash('記錄已刪除', 'success')
    else:
        flash('刪除失敗或找不到該記錄', 'danger')
        
    return redirect(url_for('records.daily'))
