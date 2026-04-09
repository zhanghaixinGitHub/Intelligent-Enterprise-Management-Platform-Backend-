# Phase 1 Data Model - AI驱动企业管理平台核心能力

## 1. Employee（员工账号）

### Fields
- `employee_id` (string, unique)
- `name` (string, required)
- `department_id` (string, required)
- `role_codes` (array[string], required)
- `status` (enum: active/inactive/left)
- `created_at` / `updated_at` (datetime)

### Validation Rules
- `employee_id` 不可为空且全局唯一。
- 离职状态员工不可发起新业务操作。

### Relationships
- Employee 1:N ConversationSession
- Employee 1:N OperationRequest
- Employee N:M AccessPolicy（通过角色映射）

---

## 2. ConversationSession（对话会话）

### Fields
- `session_id` (string, unique)
- `employee_id` (string, required)
- `current_intent` (string, nullable)
- `state` (enum: collecting/confirming/executing/completed/failed)
- `context_snapshot` (json)
- `last_message_at` (datetime)

### Validation Rules
- 同一会话状态必须满足状态机迁移规则，不允许非法跳转。

### Relationships
- ConversationSession 1:N OperationRequest

### State Transitions
- collecting -> confirming
- confirming -> executing
- executing -> completed
- executing -> failed
- failed -> collecting（重试）

---

## 3. OperationRequest（业务操作请求）

### Fields
- `request_id` (string, unique)
- `session_id` (string, required)
- `employee_id` (string, required)
- `operation_type` (enum: leave/reimburse/workflow/query/knowledge/minutes)
- `payload` (json, required)
- `idempotency_key` (string, required)
- `status` (enum: pending/processing/success/rejected/failed)
- `error_message` (string, nullable)
- `created_at` / `updated_at` (datetime)

### Validation Rules
- `idempotency_key` 在同一 `employee_id + operation_type` 维度下唯一。
- `payload` 需通过操作类型对应 schema 校验。

### Relationships
- OperationRequest 0..1 -> WorkflowInstance
- OperationRequest 0..N -> NotificationEvent

---

## 4. WorkflowInstance（审批流程实例）

### Fields
- `workflow_id` (string, unique)
- `request_id` (string, required)
- `workflow_type` (enum: leave/reimburse/purchase/contract/other)
- `current_node` (string)
- `status` (enum: running/approved/rejected/cancelled)
- `version` (integer, optimistic lock)
- `started_at` / `finished_at` (datetime)

### Validation Rules
- 每次状态变更必须校验 `version`，冲突时返回重试提示。

### Relationships
- WorkflowInstance 1:N ApprovalRecord

### State Transitions
- running -> approved
- running -> rejected
- running -> cancelled

---

## 5. ApprovalRecord（审批记录）

### Fields
- `approval_id` (string, unique)
- `workflow_id` (string, required)
- `approver_id` (string, required)
- `action` (enum: approve/reject/transfer/comment)
- `comment` (string, nullable)
- `acted_at` (datetime, required)

### Validation Rules
- 同一节点同一审批人不可重复提交终态审批动作。

---

## 6. QueryTask（数据问答任务）

### Fields
- `query_id` (string, unique)
- `employee_id` (string, required)
- `question` (string, required)
- `query_dsl` (json, required)
- `result_summary` (string, nullable)
- `result_payload` (json, nullable)
- `status` (enum: pending/success/failed/forbidden)
- `created_at` / `updated_at` (datetime)

### Validation Rules
- `query_dsl` 必须通过权限和白名单规则验证后方可执行。

---

## 7. KnowledgeEntry（知识条目）

### Fields
- `knowledge_id` (string, unique)
- `title` (string, required)
- `source_path` (string, required)
- `content_chunk` (text, required)
- `tags` (array[string])
- `version` (string)
- `effective_from` / `effective_to` (datetime, nullable)

### Validation Rules
- 已过期条目默认不参与主检索结果。

---

## 8. MeetingMinutes（会议纪要）

### Fields
- `minutes_id` (string, unique)
- `meeting_topic` (string, required)
- `participants` (array[string], required)
- `summary` (text, required)
- `action_items` (array[object], required)
- `decision_items` (array[string], required)
- `owner_employee_id` (string, required)
- `created_at` (datetime)

### Validation Rules
- `action_items` 每项至少包含 `task`, `owner`, `due_date`。

---

## 9. NotificationEvent（通知事件）

### Fields
- `notification_id` (string, unique)
- `event_type` (enum: approval/task/announcement/system)
- `receiver_id` (string, required)
- `channel` (enum: in_app/email/webhook)
- `delivery_status` (enum: pending/sent/failed/read)
- `retry_count` (integer, default 0)
- `payload` (json, required)
- `created_at` / `updated_at` (datetime)

### Validation Rules
- `failed` 状态需记录失败原因，且允许受控重试。

---

## 10. AccessPolicy（权限策略）

### Fields
- `policy_id` (string, unique)
- `role_code` (string, required)
- `menu_scopes` (array[string])
- `action_scopes` (array[string])
- `data_scopes` (array[string])
- `enabled` (boolean)

### Validation Rules
- 任一业务请求执行前必须加载并验证匹配的 AccessPolicy。
