# rag-enforce-backend

简介
- Python 后端（FastAPI），负责：
  - 文本检索（向量搜索）
  - 上下文构建与提示工程
  - 与 LLM 提供方交互（OpenAI / Azure / 本地 LLM）
  - 结果过滤与可追溯来源返回（source attribution）
  - 会话存储与权限控制

快速开始（本地）
1. 创建虚拟环境并安装依赖
   - python -m venv .venv
   - source .venv/bin/activate
   - pip install -r requirements.txt
2. 运行开发服务器
   - uvicorn app.main:app --reload --port 8000
3. 配置
   - 复制 `.env.example` 为 `.env`，配置向量 DB、LLM key、后端设置

核心组件建议
- FastAPI 用于提供 REST / WebSocket 接口
- LangChain 或自研 retriever 层连接向量 DB（Pinecone / Weaviate / Milvus / Chroma）
- 向量索引同步任务（从源文档生成 embeddings 并入库）
- 安全与合规层：提示过滤、policy enforcement、rate limiting
- 测试：pytest + CI 检查

部署
- 提供 Dockerfile，支持在 k8s / ECS 上部署；可结合 Redis 作缓存或 session 存储

贡献
- 请参见 CONTRIBUTING.md（待添加）

许可证
- 请在创建仓库时选择 LICENSE 类型（如果私有可以选公司许可或 MIT/Apache2）