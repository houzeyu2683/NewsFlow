SequentialAgent
├── ParallelAgent (fetchers)
│   ├── bbc_fetcher   → state["bbc_headlines"]
│   └── cnyes_fetcher → state["cnyes_headlines"]
├── filter_agent      → 從 10 篇中挑 3 篇（根據 query）
├── ParallelAgent (readers)
│   ├── reader_0
│   ├── reader_1
│   └── reader_2
└── reporter
