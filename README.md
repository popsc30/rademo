# HR 智能助手 (RAG-Powered HR Assistant)

本项目是一个基于 **RAG (Retrieval-Augmented Generation)** 架构和 **CrewAI** 框架构建的智能 HR 助手。它能够通过一个 Web 界面接收用户关于 HR 政策的提问，并从内部知识库中检索相关信息，生成准确、可靠的回答。

## ✨ 功能特性

- **后端 API**:
  - **文件上传**: 通过 `POST /upload` 接口，支持上传 PDF 和 DOCX 文档来动态更新知识库。
  - **智能问答**: 通过 `POST /query` 接口，接收用户问题，返回由 AI 生成的答案及相关的源文档信息。
  - **CORS 支持**: 已启用跨域资源共享，允许前端应用调用。
- **前端界面**:
  - **用户认证**: 基于密码的简单登录页面，保护应用访问。
  - **实时聊天**: 现代化的聊天界面，支持实时问答交互和打字机效果。
  - **文件上传**: 友好的拖拽式文件上传页面，方便 HR 管理员更新知识库。
  - **会话保持**: 聊天记录会自动保存在浏览器会话中，刷新页面不丢失。
- **核心 RAG 流程**:
  - **两阶段检索**: 使用 Milvus (L2 距离) 进行快速向量召回，再由 Cohere Reranker 模���进行高精度精排。
  - **相关性过滤**: 在精排阶段设置了相关性阈值，确保只有高度相关的文档才被用于答案生成，有效避免了内容幻觉。

## 🛠️ 技术栈

- **后端**: Python, FastAPI, CrewAI, LangChain, Milvus, Cohere
- **前端**: React, Vite, TypeScript, Tailwind CSS, shadcn/ui

## 🚀 快速开始

### 1. 环境准备

在开始之前，请确保您已经安装并运行了以下服务：

- **Python** (版本 >=3.10, <3.14)
- **Node.js** (推荐 v20.10.0 或更高版本)
- **Milvus**: 一个运行中的 Milvus 实例。
- **AWS CLI**: 配置好您的 AWS 凭证，因为本项目依赖于 Amazon Bedrock。

### 2. 安装依赖

本项目分为后端 (`rag`) 和前端 (`frontend`) 两个部分，需要分别安装依赖。

**a. 安装后端依赖:**

在项目根目录下，执行以下命令来安装所有 Python 相关的库：

```bash
# 安装 uv（一个快速的 Python 包安装器）
pip install uv

# 使用 uv 安装项目依赖
uv pip install -e .
```

**b. 安装前端依赖:**

进入 `frontend` 目录，并使用 `npm` 安装依赖：

```bash
cd frontend
npm install
```

### 3. 配置环境变量

在项目根目录的 `rag` 文件夹下，创建一个名为 `.env` 的文件，并填入以下内容。请将 `YOUR_...` 替换为您���实际配置。

```env
# .env

# AWS Bedrock 相关配置
AWS_REGION="us-east-1"  # 或者您选择的区域
EMBEDDING_MODEL="amazon.titan-embed-text-v2:0"
# 你可以换成对应的openai/openai-embedding模型，然后取消rerank
RERANK_MODEL= # 或者 cohere.rerank-english-v3.0
# 注意：请根据您的 Bedrock 模型访问权限填写正确的模型ID

# Milvus 数据库配置
MILVUS_HOST="localhost" # Milvus 服务的主机地址
MILVUS_PORT="19530"     # Milvus 服务的端口
```

---

## 📖 使用指南

### 启动 API 服务

要启动后端的 FastAPI 服务，请在**项目根目录**下运行：

```bash
python -m rag.main serve
```

服务启动后，您可以在浏览器中访问 `http://127.0.0.1:8000/docs` 来查看和测试交互式的 API 文档。

### 启动前端应用

要启动前端的 React 应用，请**打开一个新的终端**，进入 `frontend` 目录并运行：

```bash
cd frontend
npm run dev
```

应用启动后，您可以在浏览器中访问 `http://localhost:5173` (或终端提示的其他地址)。

- **登录密码**: `your-super-secret-password` (在 `src/pages/LoginPage.tsx` 中硬编码)

### 上传文件 (更新知识库)

有两种方式可以向知识库中添加新文档：

**a. 通过 Web 界面上传 (推荐)**

1.  启动前端和后端服务。
2.  在浏览器中打开前端应用并登录。
3.  点击页面右上角的 "Upload Document" 按钮。
4.  将您的 PDF 或 DOCX 文件拖拽到上传区域，或点击选择文件。
5.  点击 "Upload" 按钮，等待处理完成。

**b. 通过 `curl` 命令上传**

如果您希望通过命令行直接与 API 交互，可以使用 `curl`：

```bash
curl -X POST "http://127.0.0.1:8000/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@/path/to/your/document.pdf"
```
> 将 `/path/to/your/document.pdf` 替换为您的实际文件路径。

### 进行问答查询

**a. 通过 Web 界面查询**

在前端应用的聊天框中输入您的问题，然后按 `Enter` 或点击 "Send" 按钮。

**b. 通过 `curl` 命令查询**

```bash
curl -X POST "http://127.0.0.1:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "公司的休假政策是什么？"}'
```

### (可选) 使用命令行进行训练和查询

本项目保留了原始的命令行工具，方便进行快速测试。

- **处理单个文档 (训练):**
  ```bash
  python -m rag.main train /path/to/your/document.pdf
  ```

- **运行单个查询:**
  ```bash
  python -m rag.main run "你的问题是什么？"
  ```

- **重置数据库:**
  > **警告**: 此命令会删除 Milvus 中的整个集合，所有已上传的知识都将丢失。
  ```bash
  python -m rag.main reset-db
  ```
