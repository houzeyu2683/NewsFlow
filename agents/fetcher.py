from pathlib import Path
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from config import MODEL, MCP_SERVER

PROMPT_BBC = (Path(__file__).parent.parent / "prompts" / "fetcher_bbc.md").read_text()
PROMPT_CNYES = (Path(__file__).parent.parent / "prompts" / "fetcher_cnyes.md").read_text()


def _mcp_toolset() -> MCPToolset:
    return MCPToolset(connection_params=StdioServerParameters(
        command="python",
        args=[MCP_SERVER],
    ))


def create_bbc_fetcher_agent() -> Agent:
    """抓取 BBC 頭條，輸出 JSON 清單存入 state["bbc_headlines"]"""
    return Agent(
        name="bbc_fetcher",
        model=MODEL,
        description="抓取 BBC 中文最新頭條。",
        instruction=PROMPT_BBC,
        tools=[_mcp_toolset()],
        output_key="bbc_headlines",
    )


def create_cnyes_fetcher_agent() -> Agent:
    """抓取鉅亨網頭條，輸出 JSON 清單存入 state["cnyes_headlines"]"""
    return Agent(
        name="cnyes_fetcher",
        model=MODEL,
        description="抓取鉅亨網最新台股財經頭條。",
        instruction=PROMPT_CNYES,
        tools=[_mcp_toolset()],
        output_key="cnyes_headlines",
    )
