# Demo Q&A

## state 存在哪裡？能不能持久化？
存在記憶體（`InMemorySessionService`），程式結束就消失。
如果要持久化，需要換成其他 SessionService 實作（例如接資料庫）。

## Parallel agent 如果其中一個失敗怎麼辦？
`web_reader.py` 的 try/except 會捕捉例外並回傳 `{"status": "error", ...}`。
reader agent 的 instruction 收到 error 時會輸出錯誤說明而不是中止。
其他兩個 reader 繼續跑，pipeline 不會整個掛掉。

## 怎麼擴充新的 pipeline？
在 `news-agent/pipelines/` 新增一個檔案，組裝需要的 agents，
在 `main.py` 加對應的參數判斷即可。現有 agents 和 tools 可以直接複用。
