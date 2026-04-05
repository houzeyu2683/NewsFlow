# mcpout branch 說明

## 變更內容

移除 MCPToolset，改用直接呼叫 Playwright 的 Python function tools。

**原因：** ADK 1.28.0 的 `AsyncExitStack` 與 mcp 1.26.0 的 anyio TaskGroup 不相容，
導致 K8s 環境下 MCP session 無法建立（詳見 `test/undebug.md`）。

## 測試 FastAPI 端點

```bash
# POST 建立任務
curl -X POST http://34.28.105.197/reports \
  -H "Content-Type: application/json" \
  -d '{"query": "股票"}'

# GET 查詢結果（約 5 分鐘後）
curl http://34.28.105.197/reports/{job_id}
```

## 注意事項

- `project/` 目錄下的 `app.py` 仍使用舊版 MCP 架構，需切換到 `fresh` branch 才能正常使用
- `core/` 目錄下的 pipeline 已移除 MCP 依賴，使用 `core/tools/scraper.py` 直接呼叫 Playwright
