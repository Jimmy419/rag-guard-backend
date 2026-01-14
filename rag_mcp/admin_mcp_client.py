import os
import sys
import asyncio
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import SystemMessage
from langchain_community.chat_models.tongyi import ChatTongyi

# Global instance
_admin_agent_instance = None

# Initialize LLM
llm = ChatTongyi(
    model="qwen-max",
    temperature=0,
    # streaming=True, # Disable streaming to avoid IndexError in langchain_community
)

async def get_admin_agent():
    global _admin_agent_instance
    
    if _admin_agent_instance is not None:
        return _admin_agent_instance

    # Define server paths
    cwd = os.getcwd()
    db_server_path = os.path.join(cwd, "db_mcp_server.py")
    chart_server_path = os.path.join(cwd, "chart_mcp_server.py")
    
    # Initialize MultiServerMCPClient
    client = MultiServerMCPClient(
        {
            "db-server": {
                "command": sys.executable,
                "args": [db_server_path],
                "transport": "stdio",
            },
            "chart-server": {
                "command": sys.executable,
                "args": [chart_server_path],
                "transport": "stdio",
            },
        }
    )

    # Get tools
    tools = await client.get_tools()
    
    # Memory
    checkpointer = InMemorySaver()

    # System Message
    system_message = SystemMessage(
        content=(
            "你是一个后台管理助手，负责分析用户反馈数据并生成图表。\n"
            "你可以使用 `query_feedback_db` 工具查询数据库中的反馈信息。\n"
            "数据库表结构: feedback(id, thread_id, question, answer, rating, created_at, resolved)。\n"
            "你可以使用 `generate_bar_chart` 或 `generate_pie_chart` 生成图表。\n"
            "当用户询问统计信息时，请先查询数据库，然后根据数据生成合适的图表，最后总结发现。\n"
            "生成图表的工具会直接返回Markdown格式的图片代码（如 `![Chart](...)`），请直接将其包含在你的回答中，不要修改。\n"
            "请始终使用中文回答。"
        )
    )

    # Create Agent
    agent = create_react_agent(
        model=llm, tools=tools, prompt=system_message, checkpointer=checkpointer
    )

    _admin_agent_instance = agent
    return agent
