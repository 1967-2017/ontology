# Ontology Project

基于 `Next.js + TypeScript`、`FastAPI + SQLAlchemy + Pydantic`、`MySQL 8`、`Neo4j 5` 的 ontology v1 项目骨架。

## 目录

```text
frontend/
backend/
docker/
docs/
```

## Miniconda 环境

推荐统一使用 `conda` 环境 `ontology-dev`：

```bash
conda env create -f environment.yml
conda activate ontology-dev
```

如果当前镜像源不稳定，可临时改用官方源：

```bash
conda create -n ontology-dev --override-channels -c defaults python=3.11 nodejs -y
```

## 运行

1. 启动数据库：

```bash
docker compose -f docker/docker-compose.yml up -d
```

2. 配置后端：

```bash
conda activate ontology-dev
cd backend
copy .env.example .env
uvicorn app.main:app --reload
```

OCR 默认依赖 `ontology-dev` 环境本身，至少需要：

```text
paddleocr
PyMuPDF
Pillow
pypdf
```

如果你确实要复用外部 Python 环境中的 PaddleOCR，可选配置：

```text
PADDLEOCR_ROOT=E:\paddleOCR
```

但默认推荐直接把 OCR 依赖安装在 `ontology-dev` 中，不要依赖外部 venv 路径注入。

PPTX 生成依赖这些后端 `.env` 配置：

```text
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
GPT_IMAGE_API_KEY=
GPT_IMAGE_BASE_URL=https://api.openai.com/v1
GPT_IMAGE_MODEL=gpt-image-2
GPT_IMAGE_SIZE=16:9
```

3. 配置前端：

```bash
conda activate ontology-dev
cd frontend
copy .env.local.example .env.local
npm run dev
```

前端聊天运行时使用这些 `frontend/.env.local` 配置：

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

## 当前实现范围

- 4 个固定类：`Project`、`Team`、`Developer`、`Task`
- 4 个固定图查询模板
- 对话触发表单渲染
- 表单提交写入 MySQL
- 写入后同步 Neo4j
- `/objects` 管理页可脱离聊天独立验证
- 支持通过项目脚本和 skill 将本地 MySQL 表结构、外键关系和全量数据导入 Neo4j
- 支持通过本地 skill + MCP 工具执行 OCR、Chroma 持久知识库检索和 PPTX 生成
- OCR 的推荐运行方式是：在 `ontology-dev` 里直接安装 `paddleocr + PyMuPDF`，图片和扫描版 PDF 都走同一后端环境

## 测试

后端测试：

```bash
conda activate ontology-dev
python -m pytest backend/tests -q
```

前端测试：

```bash
conda activate ontology-dev
cd frontend
npm run test
```

## MySQL 到 Neo4j 导入

脚本入口：

```bash
python scripts/import_mysql_to_neo4j.py --include-table project --include-table team --rebuild
```

管理 API：

```text
POST /admin/import/mysql-to-neo4j
```

Skill：

```text
skills/mysql-to-neo4j-sync
```

## 文档技能与 MCP

Skill：

```text
skills/local-ocr
skills/local-rag
skills/pptx-generator
```

项目内 MCP：

```text
frontend/src/app/api/mcp/local/route.ts
```

默认通过 Next.js 本地地址暴露：

```text
http://127.0.0.1:3000/api/mcp/local
```

如需覆盖地址，可设置：

```text
LOCAL_MCP_SERVER_URL
```

## 已知限制

- 当前 agent 为规则编排版，动作协议已对齐设计稿，等你确认具体 AG-UI 仓库后可替换为真实 SDK 接入。
- 未引入 Alembic，依设计稿使用 `SQLAlchemy metadata.create_all()` 初始化表。
- Neo4j 同步失败时，接口仍返回业务成功，并在 `graph_sync` 中标记失败。
