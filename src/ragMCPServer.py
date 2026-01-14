import os
import logging
from typing import List
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from llama_index.core import Settings
from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels
from llama_index.embeddings.dashscope import (
    DashScopeEmbedding,
    DashScopeTextEmbeddingModels,
)
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.node_parser import TokenTextSplitter

# 日志配置
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("rag_mcp_server")

# 初始化 FastMCP
mcp = FastMCP("rag_knowledge_base")

# 配置 DashScope
Settings.llm = DashScope(
    model_name=DashScopeGenerationModels.QWEN_MAX,
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)

Settings.embed_model = DashScopeEmbedding(
    model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V1,
)

# 确定数据和存储路径（使用绝对路径）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PERSIST_DIR = os.path.join(BASE_DIR, "storage")

logger.info(f"Data directory: {DATA_DIR}")
logger.info(f"Storage directory: {PERSIST_DIR}")

# 全局变量存储 index
index = None


def initialize_index():
    global index
    try:
        if not os.path.exists(PERSIST_DIR):
            logger.info("Storage not found. Creating new index from documents...")
            if not os.path.exists(DATA_DIR):
                logger.error(f"Data directory not found: {DATA_DIR}")
                raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")

            documents = SimpleDirectoryReader(
                DATA_DIR,
                required_exts=[".md", ".pdf"],
            ).load_data()

            node_parser = TokenTextSplitter(chunk_size=512, chunk_overlap=200)
            nodes = node_parser.get_nodes_from_documents(documents)
            index = VectorStoreIndex(nodes)
            index.storage_context.persist(persist_dir=PERSIST_DIR)
            logger.info("Index created and persisted.")
        else:
            logger.info("Loading existing index from storage...")
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context)
            logger.info("Index loaded successfully.")

    except Exception as e:
        logger.error(f"Failed to initialize index: {e}")
        raise


# 在模块加载时初始化索引
initialize_index()


@mcp.tool()
async def query_knowledge_base(query: str) -> list[TextContent]:
    """根据用户的提问，检索知识库中的相关文档片段。

    Args:
        query: 用户的提问，用于检索相关信息。
    """
    logger.info(f"Received retrieval query: {query}")
    if index is None:
        return [TextContent(type="text", text="Error: Knowledge base not initialized.")]

    try:
        # 使用 retriever 而不是 query_engine
        # 获取最相关的5个片段
        retriever = index.as_retriever(similarity_top_k=5)
        nodes = retriever.retrieve(query)

        # 拼接检索到的内容
        context_str = "\n\n".join(
            [f"相关片段 {i+1}:\n{node.get_content()}" for i, node in enumerate(nodes)]
        )

        logger.info(f"Retrieved {len(nodes)} nodes.")
        return [TextContent(type="text", text=context_str)]
    except Exception as e:
        logger.error(f"Error retrieving from knowledge base: {e}")
        return [
            TextContent(
                type="text", text=f"Error retrieving from knowledge base: {str(e)}"
            )
        ]


if __name__ == "__main__":
    logger.info("Starting RAG MCP Server...")
    mcp.run(transport="stdio")
