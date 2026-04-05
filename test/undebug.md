# Undebug — 未解決問題記錄

## MCPToolset 在 K8s 無法建立 Session

### 症狀
Worker pod 執行 pipeline 時，`status` 立即變為 `failed`：
```json
{"status": "failed", "error": "unhandled errors in a TaskGroup (2 sub-exceptions)"}
```

### 錯誤堆疊
```
ConnectionError: Failed to create MCP session:
  -> TimeoutError
  -> asyncio.exceptions.CancelledError (at session_context.py _ready_event.wait())
  -> Error on session runner task: unhandled errors in a TaskGroup (1 sub-exception)
```

### 根本原因（推測）
ADK 1.28.0 的 `MCPSessionManager.create_session()` 使用：
```python
session = await asyncio.wait_for(
    exit_stack.enter_async_context(SessionContext(...)),
    timeout=5.0,
)
```
`SessionContext._run()` 是 background asyncio task，內部透過 `AsyncExitStack` 進入 `stdio_client`。
`stdio_client` (mcp 1.26.0) 用 anyio `create_task_group()` 管理 `stdout_reader` / `stdin_writer`。

**anyio 的 cancel scope 在 `AsyncExitStack` + `asyncio.wait_for` 的組合下行為異常**，
導致 `session.initialize()` 永久卡住，5 秒後 timeout。

### 已驗證
- MCP server 本身可以正常啟動（`kubectl exec` 測試）
- Playwright 可以在 container 內正常執行
- 直接用 `async with stdio_client(...) as ...:` 可以成功 initialize
- 但 ADK 的 `MCPToolset`（透過 `AsyncExitStack`）在 K8s 中必定失敗
- `PYTHONUNBUFFERED=1` 和 `-u` flag 無效

### 環境
- `google-adk==1.28.0`
- `mcp==1.26.0`
- `anyio==4.13.0`
- Python 3.12, GKE

### 解法
移除 MCPToolset，改用直接 Python async function 呼叫 Playwright（見 `core/tools/scraper.py`）。
