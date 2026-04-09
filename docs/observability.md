# 观测与审计规范

## 日志格式

统一格式：

`类名.方法名 >>> 日志信息`

示例：

`ConversationOrchestrator.handle >>> 收到对话请求 | {'session_id': 's1', 'employee_id': 'u1'}`

## 必记日志点

- 对话请求接入
- 意图识别与工具路由
- 审批状态变更
- 通知投递结果
- 查询执行与权限拒绝
- 异常堆栈（error 级别）

## 审计追踪建议

- `operator_id`: 操作人
- `biz_id`: 业务主键
- `trace_id`: 跨层链路追踪 ID
