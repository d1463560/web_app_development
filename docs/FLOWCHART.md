# 流程圖文件 — 個人記帳簿系統

## 1. 使用者流程圖（User Flow）

以下流程圖展示使用者從進入網站到完成各項操作的完整路徑：

```mermaid
flowchart LR
    A([使用者開啟網頁]) --> B["首頁 — 儀表板<br/>顯示總收入/總支出/結餘"]

    B --> C{要執行什麼操作？}

    C -->|新增記錄| D["新增記錄頁面<br/>GET /add"]
    C -->|查看每日明細| H["每日明細頁面<br/>GET /daily"]
    C -->|查看財務報表| L["財務報表頁面<br/>GET /report"]

    %% 新增記錄流程
    D --> E{選擇記錄類型}
    E -->|收入| F1["填寫收入表單<br/>日期/金額/分類/備註"]
    E -->|支出| F2["填寫支出表單<br/>日期/金額/分類/備註"]
    F1 --> G["送出表單<br/>POST /add"]
    F2 --> G
    G --> G1{驗證是否通過？}
    G1 -->|是| G2["顯示成功訊息<br/>重導向首頁"]
    G1 -->|否| G3["顯示錯誤訊息<br/>返回表單"]
    G2 --> B
    G3 --> D

    %% 每日明細流程
    H --> I["選擇日期篩選"]
    I --> J["顯示當日收支列表"]
    J --> K{要對記錄做什麼？}
    K -->|編輯| K1["編輯記錄頁面<br/>GET /edit/id"]
    K -->|刪除| K2["確認刪除<br/>POST /delete/id"]
    K -->|返回| B
    K1 --> K3["修改表單內容"]
    K3 --> K4["送出修改<br/>POST /edit/id"]
    K4 --> J
    K2 --> J

    %% 財務報表流程
    L --> M["選擇時間範圍<br/>本週/本月/自訂"]
    M --> N["顯示圖表<br/>圓餅圖 + 折線圖"]
    N --> O{切換操作}
    O -->|切換月份| M
    O -->|返回首頁| B
```

### 流程說明

1. **首頁（儀表板）**：使用者進入系統後，立即看到總收入、總支出與結餘三大數字
2. **新增記錄**：選擇收入或支出 → 填寫表單 → 驗證 → 成功後回到首頁
3. **每日明細**：選擇日期 → 瀏覽當天記錄 → 可編輯或刪除個別項目
4. **財務報表**：選擇時間範圍 → 查看支出圓餅圖與收支趨勢折線圖

---

## 2. 系統序列圖（Sequence Diagram）

### 2.1 新增收支記錄

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Route as Flask Route<br/>records.py
    participant Model as Record Model<br/>record.py
    participant DB as SQLite

    User->>Browser: 點擊「新增記錄」
    Browser->>Route: GET /add
    Route-->>Browser: 回傳 add.html 表單頁面
    User->>Browser: 填寫表單（類型/日期/金額/分類/備註）
    Browser->>Route: POST /add
    Route->>Route: 驗證輸入資料（金額>0、日期格式）

    alt 驗證失敗
        Route-->>Browser: 回傳 add.html（附錯誤訊息）
        Browser-->>User: 顯示錯誤提示
    else 驗證成功
        Route->>Model: Record.create(type, date, amount, category, note)
        Model->>DB: INSERT INTO records (type, date, amount, category, note, created_at) VALUES (...)
        DB-->>Model: 新增成功
        Model-->>Route: 回傳新記錄
        Route-->>Browser: 302 重導向至首頁（附 flash 成功訊息）
        Browser->>Route: GET /
        Route->>Model: Record.get_summary()
        Model->>DB: SELECT SUM(...) FROM records
        DB-->>Model: 統計結果
        Model-->>Route: 回傳統計資料
        Route-->>Browser: 回傳 index.html（更新後的統計）
        Browser-->>User: 顯示首頁與成功訊息
    end
```

### 2.2 查看每日收支明細

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Route as Flask Route<br/>records.py
    participant Model as Record Model<br/>record.py
    participant DB as SQLite

    User->>Browser: 點擊「每日明細」
    Browser->>Route: GET /daily
    Route->>Model: Record.get_by_date(today)
    Model->>DB: SELECT * FROM records WHERE date = ?
    DB-->>Model: 查詢結果
    Model-->>Route: 回傳記錄列表
    Route-->>Browser: 回傳 daily.html（含當日記錄）
    Browser-->>User: 顯示每日收支明細

    User->>Browser: 選擇其他日期
    Browser->>Route: GET /daily?date=2026-04-20
    Route->>Model: Record.get_by_date("2026-04-20")
    Model->>DB: SELECT * FROM records WHERE date = ?
    DB-->>Model: 查詢結果
    Model-->>Route: 回傳記錄列表
    Route-->>Browser: 回傳 daily.html（含指定日期記錄）
    Browser-->>User: 顯示篩選後的明細
```

### 2.3 編輯與刪除記錄

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Route as Flask Route<br/>records.py
    participant Model as Record Model<br/>record.py
    participant DB as SQLite

    Note over User,DB: ── 編輯記錄 ──
    User->>Browser: 點擊「編輯」按鈕
    Browser->>Route: GET /edit/5
    Route->>Model: Record.get_by_id(5)
    Model->>DB: SELECT * FROM records WHERE id = 5
    DB-->>Model: 記錄資料
    Model-->>Route: 回傳記錄
    Route-->>Browser: 回傳 edit.html（表單帶入原始資料）
    User->>Browser: 修改內容並送出
    Browser->>Route: POST /edit/5
    Route->>Model: Record.update(5, ...)
    Model->>DB: UPDATE records SET ... WHERE id = 5
    DB-->>Model: 更新成功
    Model-->>Route: 回傳結果
    Route-->>Browser: 302 重導向至每日明細

    Note over User,DB: ── 刪除記錄 ──
    User->>Browser: 點擊「刪除」按鈕
    Browser->>Route: POST /delete/5
    Route->>Model: Record.delete(5)
    Model->>DB: DELETE FROM records WHERE id = 5
    DB-->>Model: 刪除成功
    Model-->>Route: 回傳結果
    Route-->>Browser: 302 重導向至每日明細
```

### 2.4 查看財務報表

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Route as Flask Route<br/>reports.py
    participant Model as Record Model<br/>record.py
    participant DB as SQLite
    participant Chart as Chart.js

    User->>Browser: 點擊「財務報表」
    Browser->>Route: GET /report
    Route->>Model: Record.get_expense_by_category(month)
    Model->>DB: SELECT category, SUM(amount) FROM records WHERE type='expense' GROUP BY category
    DB-->>Model: 分類統計
    Route->>Model: Record.get_daily_summary(month)
    Model->>DB: SELECT date, type, SUM(amount) FROM records GROUP BY date, type
    DB-->>Model: 每日統計
    Model-->>Route: 回傳統計資料
    Route-->>Browser: 回傳 report.html（含 JSON 資料）
    Browser->>Chart: 初始化圓餅圖（支出分類比例）
    Browser->>Chart: 初始化折線圖（收支趨勢）
    Chart-->>Browser: 渲染圖表
    Browser-->>User: 顯示財務報表
```

---

## 3. 功能清單對照表

| #  | 功能             | URL 路徑          | HTTP 方法    | Controller          | 說明                              |
| -- | ---------------- | ----------------- | ------------ | ------------------- | --------------------------------- |
| 1  | 首頁儀表板       | `/`               | `GET`        | `routes/main.py`    | 顯示總收入、總支出、結餘          |
| 2  | 新增記錄（頁面） | `/add`            | `GET`        | `routes/records.py` | 顯示新增收支記錄的表單            |
| 3  | 新增記錄（送出） | `/add`            | `POST`       | `routes/records.py` | 處理表單送出，新增記錄至資料庫    |
| 4  | 每日收支明細     | `/daily`          | `GET`        | `routes/records.py` | 依日期顯示收支明細，支援日期篩選  |
| 5  | 編輯記錄（頁面） | `/edit/<id>`      | `GET`        | `routes/records.py` | 顯示編輯表單（帶入原始資料）      |
| 6  | 編輯記錄（送出） | `/edit/<id>`      | `POST`       | `routes/records.py` | 處理修改並更新資料庫              |
| 7  | 刪除記錄         | `/delete/<id>`    | `POST`       | `routes/records.py` | 刪除指定記錄                      |
| 8  | 財務報表         | `/report`         | `GET`        | `routes/reports.py` | 顯示支出分類圓餅圖與收支趨勢圖   |
