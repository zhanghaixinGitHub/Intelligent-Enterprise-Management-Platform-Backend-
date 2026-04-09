# Quickstart - AI驱动企业管理平台核心能力

## 1. 目录约定

- 后端目录：`d:/pyCharmProjects/workSpace03`
- 前端目录：`d:/webStormProjects/workSpace06`

## 2. 后端启动（Anaconda）

1. 打开 Anaconda Prompt。
2. 创建并激活环境（首次）：
   - `conda create -n ai_enterprise python=3.11 -y`
   - `conda activate ai_enterprise`
3. 安装后端依赖（在后端目录执行）：
   - `pip install -r requirements.txt`
4. 配置环境变量（开发环境）：
   - `set OPENAI_BASE_URL=https://api.openai-proxy.org/v1`
   - `set OPENAI_MODEL=gpt-4o-mini`
   - `set OPENAI_API_KEY=<your_api_key>`
5. 启动后端服务：
   - `uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload`

## 3. 前端启动（Vue3）

1. 打开终端并进入前端目录：`d:/webStormProjects/workSpace06`
2. 安装依赖：
   - `npm install`
3. 配置前端环境变量（`.env.development`）：
   - `VITE_API_BASE_URL=http://localhost:8002`
4. 启动前端：
   - `npm run dev`

## 4. 本地联调验证

1. 打开浏览器访问前端开发地址（通常是 `http://localhost:5173`）。
2. 在“AI 对话中心”输入示例：
   - “帮我请明天的年假”
   - “本月研发部加班最多的是谁”
3. 验证：
   - 对话是否自动补齐参数
   - 请求是否生成对应业务记录
   - 后端日志是否遵循：`类名.方法名 >>> 日志信息`

## 5. 并发验证（最小方案）

1. 使用压测脚本并发请求 `POST /api/v1/chat/operate`。
2. 检查点：
   - 无重复业务写入（幂等键生效）
   - 审批状态无冲突（版本号控制生效）
   - 失败请求有可追踪日志与错误响应

## 6. US1 验收补充（对话即操作）

1. 连续输入三条业务语句（例如请假、报销、查询）。
2. 确认每次返回都包含 `requestId` 与 `status`。
3. 重复提交同一幂等键请求，确认服务端拒绝重复处理。

## 7. US2 验收补充（高并发审批）

1. 启动后端后执行压测脚本：
   - `python app/tests/integration/load_approval_simulation.py`
2. 观察响应统计中 `ok` 数量与失败数量。
3. 核对后端日志中审批流转与通知发送记录是否齐全。
