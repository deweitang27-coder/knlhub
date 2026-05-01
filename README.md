# KnlHub - AI 智能知识库管理系统

<p align="center">
  上传文档 → 自动解析向量化 → 自然语言对话查询 → AI 智能体 Skills 调用
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Frontend-React_18-blue" />
  <img src="https://img.shields.io/badge/Backend-FastAPI-green" />
  <img src="https://img.shields.io/badge/Database-PostgreSQL_+_pgvector-blueviolet" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

---

## 项目简介

KnlHub 是一款基于 **RAG（Retrieval-Augmented Generation，检索增强生成）** 架构的 AI 知识库管理系统。用户可上传文档（PDF、Word、Markdown、Excel 等），系统自动将文档内容解析、分块并向量化存储，随后通过自然语言对话的方式查询知识库中的内容。此外，还提供了 **AI 智能体** 模块，支持自定义 Skills 扩展 AI 能力。

### 核心特性

- 📄 **多格式文档上传**：PDF、Word、Markdown、TXT、CSV、Excel，自动解析
- 🔍 **智能文本分块**：可配置 chunk_size 和 overlap 参数
- 🧠 **向量相似度检索**：AI Embedding 向量化存储 + pgvector 向量检索
- 💬 **自然语言知识查询**：对话式问答，支持流式输出
- 🤖 **AI 智能体**：类似 ChatGPT 的网页版对话，支持自定义 Skills
- 🛠️ **Skills 管理**：创建/编辑/启用/禁用技能，预设 4 个热门技能模板
- 🌓 **暗色模式**：一键切换明暗主题
- 📊 **使用统计**：查询次数、Token 消耗可视化统计
- 🔐 **多用户隔离**：JWT 认证，每个用户独立知识库
- ⚡ **Redis 缓存**：热门查询缓存，减少 API 费用
- 🎨 **现代 UI**：清爽的 SaaS 风格界面，Markdown 渲染

### 技术架构

```
┌─────────────┐     REST API     ┌──────────────────┐
│   Frontend  │ ───────────────▶ │     Backend      │
│  React + TS │                  │     FastAPI      │
│  TailwindCSS│ ◀─────────────── │  + SQLAlchemy    │
│  Zustand    │   SSE Stream      │  + AsyncIO       │
└─────────────┘                  └────────┬─────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
              ┌──────────┐         ┌──────────          ┌──────────┐
              │PostgreSQL│         │  Redis   │          │ AI API   │
              │+ pgvector│         │  (Cache) │          │(Embedding│
              └──────────          └──────────          │  + LLM)  │
                                                         └──────────┘
```

### 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | React 18, TypeScript, Vite 6, TailwindCSS 3, Zustand, Axios, React Router 6, Lucide Icons, React Markdown |
| **后端** | FastAPI, SQLAlchemy 2.0 (Async), Uvicorn, Pydantic, passlib+bcrypt, python-jose, OpenAI SDK |
| **数据库** | PostgreSQL + pgvector（生产）, SQLite（本地开发） |
| **缓存** | Redis 7 |
| **AI 服务** | 通义千问, 智谱 AI, DeepSeek, Kimi, 月之暗面, OpenAI |
| **文档解析** | pdfplumber, python-docx, openpyxl, beautifulsoup4, pypdf |
| **部署** | Docker, Docker Compose, Nginx, PM2 |

---

## 快速开始

### 前置条件

- Node.js >= 20
- Python >= 3.11
- PostgreSQL >= 15（可选，默认使用 SQLite）
- Redis（可选）
- 至少一个 AI API Key（通义千问 / DeepSeek / 智谱等）

### 1. 克隆项目

```bash
git clone https://github.com/deweitang27-coder/knlhub.git
cd knlhub
```

### 2. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 复制环境变量
cp .env.example .env  # 或直接编辑 .env

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务运行在 http://localhost:8000

### 3. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务运行在 http://localhost:3000

### 4. 环境变量配置

编辑 `backend/.env` 文件：

```env
# 数据库（默认 SQLite，无需额外配置）
DB_TYPE=sqlite

# Redis（可选）
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT 密钥（生产环境务必修改）
JWT_SECRET_KEY=your-secret-key-here

# Embedding 模型配置
EMBEDDING_PROVIDER=tongyi
EMBEDDING_MODEL=text-embedding-v3
EMBEDDING_API_KEY=sk-your-api-key
EMBEDDING_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# LLM 对话模型配置
LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-chat
LLM_API_KEY=sk-your-api-key
LLM_BASE_URL=https://api.deepseek.com/v1

# RAG 参数
CHUNK_SIZE=512
CHUNK_OVERLAP=64
TOP_K=5
MAX_FILE_SIZE=52428800
```

### 5. 支持的 AI 服务商

| 服务商 | 类型 | Base URL | 推荐模型 |
|--------|------|----------|----------|
| 通义千问 | Embedding + LLM | `https://dashscope.aliyuncs.com/compatible-mode/v1` | text-embedding-v3, qwen-plus |
| 智谱 AI | Embedding + LLM | `https://open.bigmodel.cn/api/paas/v4` | embedding-3, glm-4 |
| DeepSeek | LLM | `https://api.deepseek.com/v1` | deepseek-chat |
| Kimi | LLM | `https://api.moonshot.cn/v1` | kimi-chat |
| 月之暗面 | LLM | `https://api.moonshot.cn/v1` | moonshot-v1-8k |

---

## 功能模块

### 📚 知识问答
上传文档后，通过自然语言对话查询知识库内容。支持流式输出、引用溯源、Markdown 渲染。

###  AI 智能体
类似 ChatGPT 的网页版对话界面。可激活多个 Skills，AI 会综合所有激活技能的要求来回答问题。

### 🛠️ 技能管理
- 创建自定义技能：定义名称、描述、图标、颜色和系统提示词
- 预设技能：代码助手、写作大师、学术导师、商业顾问
- 技能启用/禁用控制
- 支持 10 种图标和 8 种颜色主题

###  文档管理
- 文档列表、状态跟踪、分块预览
- 支持 PDF、Word、Excel、Markdown 等多种格式

### 📊 使用统计
- 查询次数统计（今日/本周/本月）
- Token 消耗统计
- 最近文档动态

### ⚙️ 系统设置
- LLM 模型和 API Key 配置
- Embedding 模型配置
- 分块参数调整

---

## 部署方案

### 方案一：Docker Compose 一键部署（推荐生产环境）

```bash
cd ai-knowledge-base

cp .env.example .env
# 编辑 .env 填入你的配置

docker compose up -d
docker compose logs -f
```

服务端口：
- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- PostgreSQL：localhost:5432
- Redis：localhost:6379

### 方案二：本地开发模式

```bash
# 终端1：启动后端
cd backend && uvicorn app.main:app --reload --port 8000

# 终端2：启动前端
cd frontend && npm run dev
```

### 方案三：PM2 进程管理部署

```bash
npm install -g pm2

cd backend
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name knlhub-api

cd ../frontend
npm run build
pm2 serve dist/ 3000 --name knlhub-web --spa

pm2 save
```

---

## 项目结构

```
ai-knowledge-base/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── auth.py          # 注册/登录
│   │   │   ├── documents.py     # 文档上传/管理
│   │   │   ├── query.py         # 知识问答（流式）
│   │   │   ├── conversations.py # 对话历史
│   │   │   ├── skills.py        # AI 智能体 + Skills
│   │   │   ├── settings.py      # 系统设置
│   │   │   └── statistics.py    # 使用统计
│   │   ├── core/
│   │   │   ├── config.py        # 配置管理（用户级缓存）
│   │   │   ├── database.py      # 数据库连接
│   │   │   ├── embeddings.py    # Embedding API
│   │   │   ├── vector_store.py  # 向量检索
│   │   │   ├── cache.py         # Redis 缓存
│   │   │   ├── security.py      # JWT 认证
│   │   │   └── dependencies.py  # 依赖注入
│   │   ├── models/models.py     # ORM 模型
│   │   └── main.py              # FastAPI 入口
│   ├── uploads/                 # 上传文件存储
│   ├── requirements.txt
│   ── .env
│
├── frontend/
│   ├── src/
│   │   ├── api/                 # API 客户端
│   │   │   ├── client.ts        # Axios 实例 + 拦截器
│   │   │   ├── auth.ts          # 认证 API
│   │   │   └── skills.ts        # 智能体/Skills API
│   │   ├── components/
│   │   │   ├── Login.tsx        # 登录页
│   │   │   ├── Register.tsx     # 注册页
│   │   │   ├── Layout.tsx       # 主布局（侧边栏 + 主题切换）
│   │   │   ├── ChatWindow.tsx   # 知识问答（流式 + Markdown）
│   │   │   ├── AgentChat.tsx    # AI 智能体（Skills 对话）
│   │   │   ├── SkillsManager.tsx # 技能管理（预设 + 自定义）
│   │   │   ├── DocLibrary.tsx   # 文档管理
│   │   │   ├── DocumentUpload.tsx # 文件上传
│   │   │   ├── Statistics.tsx   # 使用统计
│   │   │   ├── Settings.tsx     # 系统设置
│   │   │   └── MarkdownRenderer.tsx # Markdown 渲染
│   │   ├── store/authStore.ts   # Zustand 状态
│   │   └── index.css            # 全局样式 + 暗色模式
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── docker-compose.yml
└── README.md
```

---

## API 接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/auth/register` | 用户注册 | 否 |
| POST | `/api/auth/login` | 用户登录 | 否 |
| GET | `/api/auth/me` | 获取当前用户信息 | 是 |
| POST | `/api/documents/upload` | 上传文档 | 是 |
| GET | `/api/documents/` | 获取文档列表 | 是 |
| DELETE | `/api/documents/{doc_id}` | 删除文档 | 是 |
| POST | `/api/query/` | 知识问答 | 是 |
| POST | `/api/query/stream` | 知识问答（流式） | 是 |
| GET | `/api/conversations/` | 对话历史列表 | 是 |
| GET | `/api/conversations/{id}` | 获取对话详情 | 是 |
| POST | `/api/conversations/` | 创建新对话 | 是 |
| POST | `/api/conversations/{id}/message` | 添加对话消息 | 是 |
| DELETE | `/api/conversations/{id}` | 删除对话 | 是 |
| GET | `/api/skills/` | 技能列表 | 是 |
| POST | `/api/skills/` | 创建技能 | 是 |
| PUT | `/api/skills/{id}` | 更新技能 | 是 |
| DELETE | `/api/skills/{id}` | 删除技能 | 是 |
| GET | `/api/skills/agent/conversations` | 智能体对话历史 | 是 |
| POST | `/api/skills/agent/conversations` | 创建智能体对话 | 是 |
| POST | `/api/skills/agent/conversations/{id}/message` | 添加智能体消息 | 是 |
| PUT | `/api/skills/agent/conversations/{id}/skills` | 更新激活的技能 | 是 |
| POST | `/api/skills/agent/stream` | 智能体流式对话 | 是 |
| GET | `/api/settings/` | 获取系统设置 | 是 |
| POST | `/api/settings/` | 保存系统设置 | 是 |
| GET | `/api/statistics/` | 获取使用统计 | 是 |
| GET | `/api/health` | 健康检查 | 否 |

---

## 常见问题

### Q: 如何配置自己的 API Key？
A: 有两种方式：
1. 编辑 `backend/.env` 文件，设置 `EMBEDDING_API_KEY` 和 `LLM_API_KEY`
2. 登录后在前端「设置」页面中配置（推荐，支持用户级别隔离）

### Q: 支持哪些文件格式？
A: PDF、DOCX、DOC、TXT、MD、CSV、XLSX、PPTX，单个文件最大 50MB（可配置）。

### Q: 为什么检索不到内容？
A: 检查以下几点：
- 文档是否已处理完成（状态为「已完成」）
- Embedding API Key 是否正确
- 问题与文档内容是否相关

### Q: Skills 是什么？怎么用？
A: Skills 是自定义的 AI 能力扩展。每个 Skill 包含一个系统提示词，定义了 AI 在特定场景下的行为模式。在「AI 智能体」对话页面中，你可以激活多个 Skills，AI 会综合所有激活技能的要求来回答问题。系统内置了 4 个预设技能模板。

### Q: 如何切换数据库？
A: 修改 `backend/.env` 中的 `DB_TYPE`：
- `sqlite`：使用 SQLite（本地开发推荐）
- `postgres`：使用 PostgreSQL + pgvector（生产推荐）

### Q: 后端服务无法启动？
A: 检查以下几点：
- Python 版本 >= 3.11
- 虚拟环境已激活且依赖已安装
- 8000 端口没有被占用
- 使用 `py -3 -m uvicorn app.main:app --reload --port 8000` 启动

---

## 更新日志

### v1.1.0 (2026)
-  AI 智能体模块：支持 Skills 的流式对话
- 🆕 技能管理系统：创建/编辑/预设技能
- 🆕 对话历史功能
-  使用统计面板
- 🆕 暗色模式支持
-  Markdown 渲染
- 🆕 流式输出生成
-  修复多处 Session 隔离和缓存问题

### v1.0.0
- 基础 RAG 知识库功能
- 文档上传与向量化
- 知识问答
- 用户认证
- 系统设置

---

## License

MIT
