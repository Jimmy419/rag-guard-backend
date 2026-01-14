import os
import sys
import asyncio
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.chat_models.tongyi import ChatTongyi
from typing import Dict, List, Any


# 使用langgraph推荐方式定义大模型
llm = ChatTongyi(
    model="qwen-max",
    temperature=0,
    streaming=True,
)


# 解析消息列表
def parse_messages(messages: List[Any]) -> None:
    """
    解析消息列表，打印 HumanMessage、AIMessage 和 ToolMessage 的详细信息

    Args:
        messages: 包含消息的列表，每个消息是一个对象
    """
    print("=== 消息解析结果 ===")
    for idx, msg in enumerate(messages, 1):
        print(f"\n消息 {idx}:")
        # 获取消息类型
        msg_type = msg.__class__.__name__
        print(f"类型: {msg_type}")
        # 提取消息内容
        content = getattr(msg, "content", "")
        print(f"内容: {content if content else '<空>'}")
        # 处理附加信息
        additional_kwargs = getattr(msg, "additional_kwargs", {})
        if additional_kwargs:
            print("附加信息:")
            for key, value in additional_kwargs.items():
                if key == "tool_calls" and value:
                    print("  工具调用:")
                    for tool_call in value:
                        print(f"    - ID: {tool_call['id']}")
                        print(f"      函数: {tool_call['function']['name']}")
                        print(f"      参数: {tool_call['function']['arguments']}")
                else:
                    print(f"  {key}: {value}")
        # 处理 ToolMessage 特有字段
        if msg_type == "ToolMessage":
            tool_name = getattr(msg, "name", "")
            tool_call_id = getattr(msg, "tool_call_id", "")
            print(f"工具名称: {tool_name}")
            print(f"工具调用 ID: {tool_call_id}")
        # 处理 AIMessage 的工具调用和元数据
        if msg_type == "AIMessage":
            tool_calls = getattr(msg, "tool_calls", [])
            if tool_calls:
                print("工具调用:")
                for tool_call in tool_calls:
                    print(f"  - 名称: {tool_call['name']}")
                    print(f"    参数: {tool_call['args']}")
                    print(f"    ID: {tool_call['id']}")
            # 提取元数据
            metadata = getattr(msg, "response_metadata", {})
            if metadata:
                print("元数据:")
                token_usage = metadata.get("token_usage", {})
                print(f"  令牌使用: {token_usage}")
                print(f"  模型名称: {metadata.get('model_name', '未知')}")
                print(f"  完成原因: {metadata.get('finish_reason', '未知')}")
        # 打印消息 ID
        msg_id = getattr(msg, "id", "未知")
        print(f"消息 ID: {msg_id}")
        print("-" * 50)


# 保存状态图的可视化表示
def save_graph_visualization(graph, filename: str = "graph.png") -> None:
    """保存状态图的可视化表示。

    Args:
        graph: 状态图实例。
        filename: 保存文件路径。
    """
    # 尝试执行以下代码块
    try:
        # 以二进制写模式打开文件
        with open(filename, "wb") as f:
            # 将状态图转换为Mermaid格式的PNG并写入文件
            f.write(graph.get_graph().draw_mermaid_png())
        # 记录保存成功的日志
        print(f"Graph visualization saved as {filename}")
    # 捕获IO错误
    except IOError as e:
        # 记录警告日志
        print(f"Failed to save graph visualization: {e}")


# 全局变量存储 agent 实例
_agent_instance = None

# 定义并运行agent
async def get_agent():
    global _agent_instance
    
    # 如果已经初始化过，直接返回
    if _agent_instance is not None:
        return _agent_instance

    # 实例化MCP Server客户端
    client = MultiServerMCPClient(
        {
            "rag-knowledge-base": {
                "command": sys.executable,
                "args": [
                    "/Users/jimmy/Documents/jimmy/projects/master-degree-project/rag-guard-backend/rag_mcp/ragMCPServer.py"
                ],
                "transport": "stdio",
                "env": {
                    "DASHSCOPE_API_KEY": os.getenv("DASHSCOPE_API_KEY"),
                    "PATH": os.getenv("PATH"),
                },
            },
            "amap-maps-streamableHTTP": {
                "url": "https://mcp.amap.com/mcp?key=" + os.getenv("AMAP_MAPS_API_KEY"),
                "transport": "streamable_http",
            },
        }
    )

    # 从MCP Server中获取可提供使用的全部工具
    tools = await client.get_tools()

    # 基于内存存储的short-term
    checkpointer = InMemorySaver()

    # 定义系统消息，指导如何使用工具
    system_message = SystemMessage(
        content=(
            "你是一个AI助手，请始终使用Markdown格式回答所有问题，包括标题、列表、代码块等。\n"
            "你是VO2公司的智能助手，你的知识库中包含了一些项目的介绍以及公司的员工手册。\n"
            "当用户询问有关公司项目、规章制度等内部信息时，请务必优先使用 `query_knowledge_base` 工具从知识库中检索信息。\n"
            "只有当知识库中检索不到相关信息时，再使用你自己的通用知识进行回答。"
        )
    )

    # 创建ReAct风格的agent
    agent = create_react_agent(
        model=llm, tools=tools, prompt=system_message, checkpointer=checkpointer
    )

    # 保存实例
    _agent_instance = agent

    return agent


async def run_agent():
    agent = await get_agent()

    # 将定义的agent的graph进行可视化输出保存至本地
    save_graph_visualization(agent)

    # 定义short-term需使用的thread_id
    # config = {"configurable": {"thread_id": "1"}}

    print("Agent initialized and graph saved.")


if __name__ == "__main__":
    asyncio.run(run_agent())
