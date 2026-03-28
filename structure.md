## 初期規模

專案目錄&檔案架構

/mcp               <- 所有任務共用，MCP server 從一開始就放外層
  server.py
  /utility
/任務名稱
  /agents
  /pipelines
  /tools     <- 任務專屬工具，規模大了再拉出來到 /shared/tools
  main.py    <- 任務執行入口
/任務名稱
  /agents
  /pipelines
  /tools
  main.py
...

## 規模擴大後（有跨任務共用需求時）

專案目錄&檔案架構

/shared
  /tools     <- 從各任務的 /tools 拉出來的共用工具
/mcp
/任務名稱
/任務名稱