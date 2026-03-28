功能：

使用者輸入任務（例如：摘要文章）
API 收到後丟進 Redis
Agent 處理：
呼叫 LLM
回傳結果
DB 存結果

---

## 系統架構

```
使用者
  ↓ POST /news?topic=AI
API（FastAPI）        ← 純工程：接收請求、排隊、回傳結果
  ↓ 推任務進 Redis，回傳 task_id
Redis                ← 純工程：任務 queue，解耦 API 和 Agent
  ↓ Agent 監聽並拿任務
Agent（ADK pipeline）← LLM 在這裡：判斷、理解、生成
  ├── Filter：LLM 判斷哪 3 篇值得讀
  ├── Reader：LLM 理解文章、寫摘要
  └── Reporter：LLM 整合成結構化報告
  ↓ 存結果
DB                   ← 純工程：存報告結果

使用者
  ↓ GET /result?task_id=xxx
API 從 DB 查詢並回傳
```

## Docker 組成

```
docker-compose
├── api      ← FastAPI（你的程式碼）
├── agent    ← ADK pipeline worker（你的程式碼）
├── redis    ← 現成 image
└── db       ← 現成 image（PostgreSQL）
```

api 和 agent 共用同一個 Dockerfile，跑不同指令。

## 各層職責

- Docker / Redis / DB → 解決工程問題（可靠、可擴展）
- ADK Agent → 解決智慧問題（判斷、理解、生成）

## 水平擴展

大量 request 進來時，只需一行指令增加 agent worker：

```bash
docker-compose up --scale agent=10
```

- 沒有 Docker → 手動裝環境、設定，很痛苦
- 有 Docker → 環境一致，秒級擴展

Redis queue 確保任務不丟失，多個 worker 同時從 queue 拿任務處理。

## 三個技術的分工

- ADK   → agent 有智慧處理任務
- Redis → 大量任務排隊，不丟失
- Docker → worker 快速水平擴展