# 启动指南（后端）

## 1. 创建并激活 Anaconda 环境

```powershell
conda create -n ai_enterprise python=3.11 -y
conda activate ai_enterprise
```

## 2. 安装依赖

```powershell
cd d:\pyCharmProjects\workSpace03
pip install -r requirements.txt
```

## 3. 配置环境变量

复制 `.env.example` 为 `.env`，填入你的 `OPENAI_API_KEY`。

## 4. 启动后端

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

## 5. 验证接口

- 健康检查：`GET /health`
- 对话操作：`POST /api/v1/chat/operate`
- 审批操作：`POST /api/v1/workflows/{workflowId}/approve`
- 数据问答：`POST /api/v1/query/ask`
- 知识问答：`POST /api/v1/knowledge/ask`
