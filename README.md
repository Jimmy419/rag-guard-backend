# RAG-Guard Backend

## 项目介绍

RAG-Guard Backend 是一个基于 FastAPI 和 LangChain 构建的智能后台系统，旨在为企业提供基于 RAG (Retrieval-Augmented Generation) 的问答服务及管理功能。

### 核心功能

1.  **智能问答 (RAG Agent)**
    *   基于 DashScope (Qwen) 大模型。
    *   集成向量知识库，支持从 PDF/Markdown 文档中检索信息（如项目介绍、员工手册）。
    *   具备联网搜索能力（集成高德地图 API）。
    *   基于 LangGraph 构建 ReAct 风格的 Agent，支持复杂的工具调用。

2.  **管理后台 (Admin Dashboard)**
    *   提供用户反馈管理界面，支持查看和标记反馈状态。
    *   **Admin Chat**: 一个智能数据分析助手，支持通过自然语言查询数据库。
    *   **MCP (Model Context Protocol) 架构**:
        *   **DB MCP Server**: 安全地查询反馈数据库。
        *   **Chart MCP Server**: 动态生成数据图表（柱状图、饼图），支持中文显示。

3.  **自动化运维**
    *   Docker 化部署支持。
    *   内置定时任务，每日自动清理生成的临时图表文件。

## 文件结构

```text
rag-guard-backend/
├── Dockerfile                  # Docker 镜像构建文件
├── requirements.txt            # Python 依赖列表
├── docker_scripts/             # Docker 运行相关脚本
│   ├── start.sh                # 容器启动脚本（启动 Cron 和 Uvicorn）
│   └── cleanup_charts.sh       # 定时清理图表文件的脚本
├── src/                        # 源代码目录
│   ├── server.py               # FastAPI 主应用入口
│   ├── mcp_client.py           # 用户侧 RAG Agent 客户端
│   ├── admin_mcp_client.py     # 管理侧数据分析 Agent 客户端
│   ├── ragMCPServer.py         # 知识库 MCP 服务
│   ├── db_mcp_server.py        # 数据库查询 MCP 服务
│   ├── chart_mcp_server.py     # 图表生成 MCP 服务
│   ├── data/                   # RAG 知识库原始文档 (PDF/MD)
│   ├── storage/                # 向量索引持久化存储
│   ├── static/                 # 静态文件 (HTML/生成的图表)
│   ├── feedback.db             # SQLite 反馈数据库
│   └── init_db.sql             # 数据库初始化脚本
└── README.md                   # 项目说明文档
```

## Docker 部署指南

### 1. 构建镜像

在项目根目录下执行以下命令构建 Docker 镜像。
*注意：为了加速构建，Dockerfile 中已配置使用清华大学 Debian 镜像源。*

```bash
docker build -t rag-guard-backend .
```

### 2. 运行容器

启动容器时，需要配置必要的环境变量（API Key）。

```bash
docker run -d \
  -p 8000:8000 \
  -e DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx" \
  -e AMAP_MAPS_API_KEY="your_amap_key" \
  --name rag-guard \
  rag-guard-backend
```

**参数说明：**
*   `-d`: 后台运行。
*   `-p 8000:8000`: 端口映射（宿主机:容器）。
*   `-e DASHSCOPE_API_KEY`: 阿里云 DashScope API Key（必填，用于大模型调用）。
*   `-e AMAP_MAPS_API_KEY`: 高德地图 API Key（选填，用于地图查询功能）。

### 3. 功能验证

*   **API 服务**: 访问 `http://localhost:8000/docs` 查看 Swagger 文档。
*   **管理后台**: 访问 `http://localhost:8000/static/index.html` 进入管理界面。
*   **定时任务**: 容器内置 Cron 服务，将于每天 00:00 自动清理 `src/static/charts` 目录下的过期图表。

### 4. 常用运维命令

**查看容器日志：**
```bash
docker logs -f rag-guard
```

**进入容器内部：**
```bash
docker exec -it rag-guard /bin/bash
```

**手动停止/删除容器：**
```bash
docker stop rag-guard
docker rm rag-guard
```

## 开发环境运行 (Local)

如果不使用 Docker，也可以在本地直接运行：

1.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **设置环境变量**:
    建议创建 `.env` 文件或直接 export：
    ```bash
    export DASHSCOPE_API_KEY="sk-..."
    ```

3.  **启动服务**:
    ```bash
    cd src
    uvicorn server:app --reload --host 0.0.0.0 --port 8000
    ```
