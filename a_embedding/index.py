# import os
# from openai import OpenAI

# client = OpenAI(
#     api_key=os.getenv("DASHSCOPE_API_KEY"),  # 如果您没有配置环境变量，请在此处用您的API Key进行替换
#     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 百炼服务的base_url
# )

# completion = client.embeddings.create(
#     model="text-embedding-v4",
#     input='聚客AI学院',
#     dimensions=1024,
#     encoding_format="float"
# )

# print(completion.model_dump_json())

# import os
# from openai import OpenAI

# api_key = os.getenv("DASHSCOPE_API_KEY")
# print(api_key)
# client = OpenAI(
#     api_key=api_key,
#     # 以下是北京地域base_url，如果使用新加坡地域的模型，需要将base_url替换为：https://dashscope-intl.aliyuncs.com/compatible-mode/v1
#     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
# )
# completion = client.chat.completions.create(
#     model="qwen-plus",
#     messages=[{'role': 'user', 'content': '你是谁？'}]
# )
# print(completion.choices[0].message.content)

import chromadb

client = chromadb.Client()

client = chromadb.PersistentClient(path="./chroma")

from chromadb.utils import embedding_functions

# 默认情况下，Chroma 使用 DefaultEmbeddingFunction，它是基于 Sentence Transformers 的 MiniLM-L6-v2 模型
default_ef = embedding_functions.DefaultEmbeddingFunction()

# 使用 OpenAI 的嵌入模型，默认使用 text-embedding-ada-002 模型
# openai_ef = embedding_functions.OpenAIEmbeddingFunction(
#     api_key="YOUR_API_KEY",
#     model_name="text-embedding-3-small"
# )

# 自定义 Embedding Functions
from chromadb import Documents, EmbeddingFunction, Embeddings

# class MyEmbeddingFunction(EmbeddingFunction):
#     def __call__(self, texts: Documents) -> Embeddings:
#         # embed the documents somehow
#         return embeddings

collection = client.create_collection(
    name = "my_collection",
    configuration = {
        # HNSW 索引算法，基于图的近似最近邻搜索算法（Approximate Nearest Neighbor，ANN）
        "hnsw": {
            "space": "cosine", # 指定余弦相似度计算
            "ef_search": 100,
            "ef_construction": 100,
            "max_neighbors": 16,
            "num_threads": 4
        },
        # 指定向量模型
        "embedding_function": default_ef
    }
)

client.delete_collection(name="my_collection")

# 方式1：自动生成向量（使用集合指定的嵌入模型）
collection.add(
    # 文档的集合
    documents = ["RAG是一种检索增强生成技术", "向量数据库存储文档的嵌入表示", "在机器学习领域，智能体（Agent）通常指能够感知环境、做出决策并采取行动以实现特定目标的实体"],
    # 文档元数据信息
    metadatas = [{"source": "RAG"}, {"source": "向量数据库"}, {"source": "Agent"}],
    # id
    ids = ["id1", "id2", "id3"]
)
# collection = client.get_collection(name="my_collection")

# print(collection.peek())

# print(collection.count())

# print(collection.modify(name="new_name"))

results = collection.query(
    query_texts = ["RAG是什么？"],
    n_results = 3,
    where = {"source": "RAG"}, # 按元数据过滤
    # where_document = {"$contains": "检索增强生成"} # 按文档内容过滤
)

print(results)