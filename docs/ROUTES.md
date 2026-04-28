# 路由設計文件 — 個人記帳簿系統

## 1. 路由總覽表格

| #  | 功能               | HTTP 方法 | URL 路徑         | 對應模板                    | 說明                              |
| -- | ------------------ | --------- | ---------------- | --------------------------- | --------------------------------- |
| 1  | 首頁儀表板         | GET       | `/`              | `templates/index.html`      | 顯示總收入、總支出、結餘          |
| 2  | 新增記錄（頁面）   | GET       | `/add`           | `templates/add.html`        | 顯示新增收支記錄的表單            |
| 3  | 新增記錄（送出）   | POST      | `/add`           | —（重導向至 `/`）           | 接收表單資料，存入資料庫          |
| 4  | 每日收支明細       | GET       | `/daily`         | `templates/daily.html`      | 依日期顯示收支明細                |
| 5  | 編輯記錄（頁面）   | GET       | `/edit/<id>`     | `templates/edit.html`       | 顯示編輯表單（帶入原始資料）      |
| 6  | 編輯記錄（送出）   | POST      | `/edit/<id>`     | —（重導向至 `/daily`）      | 接收修改後資料，更新資料庫        |
| 7  | 刪除記錄           | POST      | `/delete/<id>`   | —（重導向至 `/daily`）      | 刪除指定記錄                      |
| 8  | 財務報表           | GET       | `/report`        | `templates/report.html`     | 顯示圖表化的財務分析報表          |

---

## 2. 每個路由的詳細說明

### 2.1 首頁儀表板

| 項目       | 說明                                                   |
| ---------- | ------------------------------------------------------ |
| **URL**    | `GET /`                                                |
| **輸入**   | Query Parameter: `month`（可選，格式 `YYYY-MM`）       |
| **處理邏輯** | 呼叫 `Record.get_summary(month)` 取得統計數據        |
| **輸出**   | 渲染 `index.html`，傳入 `total_income`、`total_expense`、`balance`、`month` |
| **錯誤處理** | 無特殊錯誤情境                                       |

### 2.2 新增記錄（頁面）

| 項目       | 說明                                                   |
| ---------- | ------------------------------------------------------ |
| **URL**    | `GET /add`                                             |
| **輸入**   | 無                                                     |
| **處理邏輯** | 準備分類選項列表                                     |
| **輸出**   | 渲染 `add.html`，傳入收入分類與支出分類選項、今天日期  |
| **錯誤處理** | 無特殊錯誤情境                                       |

### 2.3 新增記錄（送出）

| 項目       | 說明                                                   |
| ---------- | ------------------------------------------------------ |
| **URL**    | `POST /add`                                            |
| **輸入**   | 表單欄位：`type`、`amount`、`category`、`note`、`date` |
| **處理邏輯** | 1. 驗證輸入（type 必須為 income/expense、amount > 0、date 格式正確）<br/>2. 呼叫 `Record.create()` 新增記錄 |
| **輸出**   | 成功：flash 成功訊息，重導向至 `/`<br/>失敗：flash 錯誤訊息，重導向回 `/add` |
| **錯誤處理** | 金額非正數 → 顯示「金額必須為正數」<br/>必填欄位為空 → 顯示「請填寫所有必填欄位」 |

### 2.4 每日收支明細

| 項目       | 說明                                                   |
| ---------- | ------------------------------------------------------ |
| **URL**    | `GET /daily`                                           |
| **輸入**   | Query Parameter: `date`（可選，格式 `YYYY-MM-DD`，預設今天） |
| **處理邏輯** | 呼叫 `Record.get_by_date(date)` 取得當天記錄         |
| **輸出**   | 渲染 `daily.html`，傳入 `records`、`selected_date`     |
| **錯誤處理** | 日期格式錯誤 → 使用今天日期                          |

### 2.5 編輯記錄（頁面）

| 項目       | 說明                                                   |
| ---------- | ------------------------------------------------------ |
| **URL**    | `GET /edit/<id>`                                       |
| **輸入**   | URL 參數: `id`（記錄 ID）                              |
| **處理邏輯** | 呼叫 `Record.get_by_id(id)` 取得記錄資料             |
| **輸出**   | 渲染 `edit.html`，傳入 `record` 與分類選項             |
| **錯誤處理** | 記錄不存在 → 回傳 404 頁面                           |

### 2.6 編輯記錄（送出）

| 項目       | 說明                                                   |
| ---------- | ------------------------------------------------------ |
| **URL**    | `POST /edit/<id>`                                      |
| **輸入**   | URL 參數: `id`；表單欄位：`type`、`amount`、`category`、`note`、`date` |
| **處理邏輯** | 1. 驗證輸入<br/>2. 呼叫 `Record.update(id, ...)` 更新記錄 |
| **輸出**   | 成功：flash 成功訊息，重導向至 `/daily?date=記錄日期`  |
| **錯誤處理** | 記錄不存在 → 404<br/>驗證失敗 → flash 錯誤，重導向回編輯頁 |

### 2.7 刪除記錄

| 項目       | 說明                                                   |
| ---------- | ------------------------------------------------------ |
| **URL**    | `POST /delete/<id>`                                    |
| **輸入**   | URL 參數: `id`（記錄 ID）                              |
| **處理邏輯** | 呼叫 `Record.delete(id)` 刪除記錄                    |
| **輸出**   | flash 成功訊息，重導向至 `/daily`                      |
| **錯誤處理** | 記錄不存在 → flash 錯誤訊息，重導向至 `/daily`       |

### 2.8 財務報表

| 項目       | 說明                                                   |
| ---------- | ------------------------------------------------------ |
| **URL**    | `GET /report`                                          |
| **輸入**   | Query Parameter: `month`（可選，格式 `YYYY-MM`）       |
| **處理邏輯** | 1. 呼叫 `Record.get_expense_by_category(month)` 取得分類統計<br/>2. 呼叫 `Record.get_daily_summary(month)` 取得每日統計 |
| **輸出**   | 渲染 `report.html`，傳入 `category_data`、`daily_data`、`month` |
| **錯誤處理** | 無資料時顯示「尚無記錄」提示                         |

---

## 3. Jinja2 模板清單

所有模板皆繼承 `base.html` 共用版面。

| 模板檔案                | 繼承自        | 用途                                     |
| ----------------------- | ------------- | ---------------------------------------- |
| `templates/base.html`   | —（基礎模板） | 共用版面：HTML head、導覽列、頁尾、flash 訊息 |
| `templates/index.html`  | `base.html`   | 首頁儀表板：總收入/支出/結餘統計卡片     |
| `templates/add.html`    | `base.html`   | 新增收支記錄表單                         |
| `templates/edit.html`   | `base.html`   | 編輯收支記錄表單（帶入原始值）           |
| `templates/daily.html`  | `base.html`   | 每日收支明細列表（含日期選擇器）         |
| `templates/report.html` | `base.html`   | 財務報表頁面（Chart.js 圓餅圖 + 折線圖） |

### 模板繼承關係

```
base.html
├── index.html    （首頁儀表板）
├── add.html      （新增記錄）
├── edit.html     （編輯記錄）
├── daily.html    （每日明細）
└── report.html   （財務報表）
```

### base.html 包含的共用元素

- `<head>`：meta 標籤、CSS 引入（style.css）、Google Fonts
- 導覽列（Navbar）：首頁、新增記錄、每日明細、財務報表
- Flash 訊息區域：顯示操作成功/失敗的提示訊息
- `{% block content %}`：各頁面的主要內容區域
- 頁尾（Footer）
- `<script>`：Chart.js CDN、main.js

---

## 4. 路由骨架程式碼

路由骨架已建立在以下檔案：

| 檔案                    | Blueprint 名稱 | URL 前綴 | 說明            |
| ----------------------- | -------------- | -------- | --------------- |
| `app/routes/__init__.py`| —              | —        | 套件初始化      |
| `app/routes/main.py`    | `main`         | `/`      | 首頁儀表板      |
| `app/routes/records.py` | `records`      | `/`      | 收支記錄 CRUD   |
| `app/routes/reports.py` | `reports`      | `/`      | 財務報表        |

詳細程式碼請參見 `app/routes/` 目錄。
