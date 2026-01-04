import os
import logging
import pickle
from PyPDF2 import PdfReader
from langchain.chains.question_answering import load_qa_chain
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.callbacks.manager import get_openai_callback
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from typing import List, Tuple


def extract_text_with_page_numbers(pdf) -> Tuple[str, List[int]]:
    """
    从PDF中提取文本并记录每行文本对应的页码

    参数:
        pdf: PDF文件对象 (需支持.pages属性迭代)

    返回:
        text: 提取的文本内容 (行之间用\\n分隔)
        page_numbers: 每行文本对应的页码列表 (与text.split('\\n')严格对应)
    """
    all_lines = []  # 存储所有文本行
    page_numbers = []  # 存储每行对应的页码

    for page_number, page in enumerate(pdf.pages, start=1):
        extracted_text = page.extract_text()

        if not extracted_text or extracted_text.isspace():
            logging.warning(f"No text found on page {page_number}.")
            continue  # 跳过空页面

        # 按行分割并保留空行 (关键: keepends=False 确保不保留换行符)
        lines = extracted_text.splitlines(keepends=False)

        # 过滤掉纯空白行 (可选，根据需求决定是否保留空行)
        # lines = [line for line in lines if line.strip() != ""]

        # 记录有效行及其页码
        all_lines.extend(lines)
        page_numbers.extend([page_number] * len(lines))

    # 重建完整文本 (行之间用\\n连接)
    text = "\n".join(all_lines)
    return text, page_numbers


def process_text_with_splitter(
    text: str, page_numbers: List[int], save_path: str = None
) -> FAISS:
    """
    处理文本并创建向量存储

    参数:
        text: 提取的文本内容
        page_numbers: 每行文本对应的页码列表
        save_path: 可选，保存向量数据库的路径

    返回:
        knowledgeBase: 基于FAISS的向量存储对象
    """
    # 创建文本分割器（递归字符文本分割器），用于将长文本分割成小块
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " ", ""],
        chunk_size=512,
        chunk_overlap=128,
        length_function=len,
    )

    # 分割文本
    chunks = text_splitter.split_text(text)
    # logging.debug(f"Text split into {len(chunks)} chunks.")
    print(f"文本被分割成 {len(chunks)} 个块。")

    # 创建嵌入模型，OpenAI嵌入模型，配置环境变量 OPENAI_API_KEY
    # embeddings = OpenAIEmbeddings()

    # 调用阿里百炼平台文本嵌入模型，配置环境变量 DASHSCOPE_API_KEY
    embeddings = DashScopeEmbeddings(model="text-embedding-v4")
    # 从文本块创建知识库
    knowledgeBase = FAISS.from_texts(chunks, embeddings)
    print("已从文本块创建知识库...")

    # 存储每个文本块对应的页码信息
    page_info = {chunk: page_numbers[i] for i, chunk in enumerate(chunks)}
    knowledgeBase.page_info = page_info

    # 如果提供了保存路径，则保存向量数据库和页码信息
    if save_path:
        # 确保目录存在
        os.makedirs(save_path, exist_ok=True)

        # 保存FAISS向量数据库
        knowledgeBase.save_local(save_path)
        print(f"向量数据库已保存到: {save_path}")

        # 保存页码信息到同一目录
        with open(os.path.join(save_path, "page_info.pkl"), "wb") as f:
            pickle.dump(page_info, f)
        print(f"页码信息已保存到: {os.path.join(save_path, 'page_info.pkl')}")

    return knowledgeBase


def load_knowledge_base(load_path: str, embeddings=None) -> FAISS:
    """
    从磁盘加载向量数据库和页码信息

    参数:
        load_path: 向量数据库的保存路径
        embeddings: 可选，嵌入模型。如果为None，将创建一个新的DashScopeEmbeddings实例

    返回:
        knowledgeBase: 加载的FAISS向量数据库对象
    """
    # 如果没有提供嵌入模型，则创建一个新的
    if embeddings is None:
        embeddings = DashScopeEmbeddings(model="text-embedding-v4")

    # 加载FAISS向量数据库，添加allow_dangerous_deserialization=True参数以允许反序列化
    knowledgeBase = FAISS.load_local(
        load_path, embeddings, allow_dangerous_deserialization=True
    )
    print(f"向量数据库已从 {load_path} 加载。")

    # 加载页码信息
    page_info_path = os.path.join(load_path, "page_info.pkl")
    if os.path.exists(page_info_path):
        with open(page_info_path, "rb") as f:
            page_info = pickle.load(f)
        knowledgeBase.page_info = page_info
        print("页码信息已加载。")
    else:
        print("警告: 未找到页码信息文件。")

    return knowledgeBase


# 读取PDF文件
pdf_reader = PdfReader("./浦发上海浦东发展银行西安分行个金客户经理考核办法.pdf")
# 提取文本和页码信息
text, page_numbers = extract_text_with_page_numbers(pdf_reader)

print(f"提取的文本长度: {len(text)} 个字符。")

# 处理文本并创建知识库，同时保存到磁盘
save_dir = "./vector_db"
knowledgeBase = process_text_with_splitter(text, page_numbers, save_path=save_dir)

# 处理文本并创建知识库
knowledgeBase = process_text_with_splitter(text, page_numbers)

print(knowledgeBase)

import os
from langchain_community.llms import Tongyi

# 设置查询问题
query = "客户经理被投诉了，投诉一次扣多少分？"
# query = "客户经理每年评聘申报时间是怎样的？"
if query:
    # 调用阿里百炼平台文本嵌入模型，配置环境变量 DASHSCOPE_API_KEY
    embeddings = DashScopeEmbeddings(model="text-embedding-v4")
    # 初始化对话大模型
    llm = Tongyi(
        model_name="qwen-max", dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
    )

    # 从磁盘加载向量数据库
    loaded_knowledgeBase = load_knowledge_base("./assets/vector_db", embeddings)
    # 使用加载的知识库进行查询 top_k 和 top_n
    # 一般比较优的文档个数 5 个左右
    docs = loaded_knowledgeBase.similarity_search(query, k=5)
    print(docs)

    # 加载问答链
    chain = load_qa_chain(llm, chain_type="stuff")

    # 准备输入数据
    input_data = {"input_documents": docs, "question": query}

    # 执行问答链
    response = chain.invoke(input=input_data)
    print(response["output_text"])
