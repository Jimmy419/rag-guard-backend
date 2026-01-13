import os
from llama_index.core import Settings
from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels
from llama_index.embeddings.dashscope import (
    DashScopeEmbedding,
    DashScopeTextEmbeddingModels,
)


Settings.llm = DashScope(
    model_name=DashScopeGenerationModels.QWEN_MAX,
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)

# LlamaIndex默认使用的Embedding模型被替换为百炼的Embedding模型
Settings.embed_model = DashScopeEmbedding(
    # model_name="text-embedding-v1"
    model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V1,
    # api_key=os.getenv("DASHSCOPE_API_KEY")
)


from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.node_parser import TokenTextSplitter, SentenceSplitter

# 定义持久化存储目录
PERSIST_DIR = "./storage"

if not os.path.exists(PERSIST_DIR):
    # 加载 pdf 文档
    documents = SimpleDirectoryReader(
        "./data",
        required_exts=[".pdf"],
    ).load_data()

    # 定义 Node Parser
    node_parser = TokenTextSplitter(chunk_size=512, chunk_overlap=200)

    # 切分文档
    nodes = node_parser.get_nodes_from_documents(documents)

    # 构建 index
    index = VectorStoreIndex(nodes)

    # 存储到文件
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    # 从文件加载 index
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)


chat_engine = index.as_chat_engine()
response = chat_engine.chat("deepseek v3数学能力怎么样?")
print(response)
