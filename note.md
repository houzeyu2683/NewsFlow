# Side Project 面試筆記

## 專案情境

用戶以自然語言輸入 query，agent 根據 query 去不同新聞來源爬取頭條新聞，彙整成報告後輸出。

---

## 架構流程

### 1. API 層（FastAPI）
- 用戶送 `POST /reports`，帶著 query
- API 回傳 `job_id`，用戶之後用 `GET /reports/{job_id}` 查進度和結果

### 2. Redis Queue
- query 推進 Redis `task_queue`，確保程式崩潰後任務不丟失
- `job:{job_id}` 存任務狀態（pending / running / done / failed）
- **未實作**：持久化（AOF）、ACK 機制

### 3. Worker（ADK pipeline）
- 用 `brpop` 監聽 `task_queue`，有任務進來就拿走執行
- `brpop` 是原子操作，多個 worker 不會拿到同一個任務
- scale agent=10 代表 10 個 worker 同時監聽，同時處理 10 個任務

### 4. Parallel Fetchers（2 個 agent）
- 不管什麼 query，固定同時呼叫兩個 fetcher agent
  - `bbc_fetcher`：抓 BBC 中文國際新聞
  - `cnyes_fetcher`：抓鉅亨網台股財經新聞
- 透過 MCP server 用 Playwright 開瀏覽器爬取

### 5. Filter Agent
- 拿到兩個來源的標題清單
- 根據 query 判斷相關性，挑出最值得深讀的 3 篇
- 把 3 篇的 URL 存進 session state（`url_0`、`url_1`、`url_2`）

### 6. Reader Agents（3 個 agent）
- 每個 agent 讀一篇文章，透過 MCP server 爬取完整內文
- 用 `SequentialAgent` 依序跑，每篇之間睡 10 秒避免觸發 rate limit
- 閱讀結果存進 session state（`article_0`、`article_1`、`article_2`）

### 7. Reporter Agent
- 拿三篇文章摘要，參考 `prompts/reporter.md` 的格式
- 整合成一份結構化的最終報告

---

## Agent 之間怎麼溝通

pipeline 裡的 agent 有上下游依賴，用 **ADK session state** 當共享記憶體：
- 每個 agent 用 `output_key` 把結果寫入 state
- 下游 agent 用 `{var_name}` 從 state 讀出來
- session 結束就消失，純粹是這次 pipeline 執行過程的暫存資料

**Redis state 和 ADK state 是兩個獨立的東西：**
- ADK state：agent 之間傳遞中間結果（headlines、urls、articles）
- Redis：API 和 worker 之間傳遞任務、存最終 job 狀態

---

## MCP Server
- 自己寫的 MCP server，封裝 Playwright 爬蟲
- 提供兩個工具給 agent 呼叫：
  - `getTopic(source)`：抓指定來源的標題列表
  - `getArticle(source, link)`：抓單篇文章完整內文
- agent 像呼叫工具一樣使用瀏覽器，不需要知道爬蟲細節

---

## Docker 架構
```
docker-compose
├── redis    ← 任務 queue + job 狀態
├── api      ← FastAPI，接請求、推 queue、查狀態
└── agent    ← worker，監聽 queue、跑 pipeline
```

api 和 agent 共用同一個 image，跑不同指令。水平擴展只需要：
```bash
docker compose up --scale agent=10
```

---

## 未實作 / 已知問題（面試時誠實說）

| 問題 | 說明 | 解法 |
|------|------|------|
| Redis 無持久化 | 重啟後 queue 和狀態消失 | 開啟 AOF |
| 無 ACK 機制 | worker 處理到一半掛掉，任務消失 | 用 `LMOVE` + processing queue |
| API 無認證 | 任何人都能打 | 加 API key 或 JWT |

---

## 面試話術

**架構設計：**
> "API、Queue、Worker 分層設計，Redis 解耦 API 和 Agent，支援水平擴展。通常這些是不同角色分工，我一個人 end-to-end 做完，對每層的職責和邊界都有實際理解。"

**Agent 協作：**
> "pipeline 裡的 agent 有上下游依賴，用 ADK 的 session state 當共享記憶體，每個 agent 寫入自己的結果，下游 agent 直接讀，不需要手動傳參數。"

**誠實說明限制：**
> "Redis 目前只做任務 queue 和狀態追蹤，持久化還沒實作。如果要上線，會開 AOF 確保重啟後任務不丟失，另外也需要補 ACK 機制，避免 worker 處理到一半掛掉任務消失。"
