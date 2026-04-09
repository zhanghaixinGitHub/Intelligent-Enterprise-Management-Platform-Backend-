# 端到端联调清单

## 环境

- 后端：`uvicorn app.main:app --reload`
- 前端：`npm run dev`（`d:/webStormProjects/workSpace06`）

## 用例

1. 对话式请假
   - 输入：“帮我请明天年假”
   - 预期：返回受理成功响应

2. 审批通过
   - 调用：`POST /api/v1/workflows/wf-demo-001/approve`
   - 预期：状态变化为 `approved`，版本号递增

3. 数据问答
   - 调用：`POST /api/v1/query/ask`
   - 预期：返回 `success` 与 summary

4. 知识问答
   - 调用：`POST /api/v1/knowledge/ask`
   - 预期：返回 answer 与 citations

## 结果记录

- 当前状态：MVP 骨架通过接口级联调
