# NewsRadar

以自然語言輸入主題，自動爬取新聞、篩選、閱讀，產出一份結構化分析報告。

## 架構

```
用戶
  ↓ POST /reports?query=今日股票行情
FastAPI                 ← 接收請求，推任務進 Redis，回傳 job_id
  ↓
Redis                   ← 任務 queue，解耦 API 和 Agent
  ↓
Worker（ADK pipeline）  ← 監聽 queue，拿到任務後執行
  ├── Parallel Fetchers  — 同時抓 BBC 中文 + 鉅亨網頭條
  ├── Filter Agent       — 根據 query 篩選最相關的 3 篇
  ├── Reader Agents × 3  — 各自閱讀一篇文章完整內文
  └── Reporter Agent     — 整合三篇，產出結構化報告
  ↓
用戶
  ↓ GET /reports/{job_id}
API 從 Redis 查詢並回傳結果
```

## 技術

- **Google ADK** — SequentialAgent / ParallelAgent 組合 pipeline
- **Gemini 2.5 Flash** — 篩選、閱讀、生成報告
- **MCP Server** — 自建爬蟲工具，封裝 Playwright，供 agent 呼叫
- **FastAPI** — 非同步 API，任務推入 queue 後立即回應
- **Redis** — 任務 queue + job 狀態追蹤
- **Docker Compose** — 一鍵啟動，支援水平擴展 worker

## 水平擴展

```bash
docker compose up --scale agent=10
```

多個 worker 同時從 Redis queue 搶任務，Redis 確保每個任務只被處理一次。

## 快速開始

**環境變數**（建立 `.env`）
```
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=True
```

**啟動**
```bash
docker compose up --build
```

**送出任務**
```bash
curl -X POST http://localhost:8000/reports \
  -H "Content-Type: application/json" \
  -d '{"query": "今日股票行情"}'
# 回傳 {"job_id": "xxx", "status": "pending"}
```

**查詢結果**
```bash
curl http://localhost:8000/reports/{job_id}
```

## 新聞來源

| 來源 | 適合 query |
|------|-----------|
| BBC 中文 | 國際時事、政治、科技 |
| 鉅亨網 | 台股、財經、投資 |