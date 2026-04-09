# Tasks: AI驱动企业管理平台核心能力

**Input**: Design documents from `/specs/001-ai-enterprise-platform/`  
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: 本特性规格未强制 TDD，本清单默认不单列测试开发任务；每个用户故事保留独立验收检查点。  
**Organization**: 任务按用户故事分组，确保每个故事可以独立实现与独立验收。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可并行（不同文件且无未完成依赖）
- **[Story]**: 用户故事标签（US1/US2/US3）
- 每条任务均包含明确文件路径

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 初始化后端与前端骨架、基础配置与开发环境约束

- [x] T001 创建后端目录骨架并提交占位文件于 `d:/pyCharmProjects/workSpace03/app/`
- [x] T002 [P] 创建前端目录骨架并提交占位文件于 `d:/webStormProjects/workSpace06/src/`
- [x] T003 生成后端依赖清单 `d:/pyCharmProjects/workSpace03/requirements.txt`
- [x] T004 [P] 生成前端依赖清单 `d:/webStormProjects/workSpace06/package.json`
- [x] T005 创建后端环境变量模板 `d:/pyCharmProjects/workSpace03/.env.example`
- [x] T006 [P] 创建前端环境变量模板 `d:/webStormProjects/workSpace06/.env.development.example`
- [x] T007 编写统一启动脚本说明至 `d:/pyCharmProjects/workSpace03/docs/startup-guide.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 构建所有用户故事共用的基础能力（必须先完成）

**⚠️ CRITICAL**: 本阶段未完成前，不进入任何 US 业务开发

- [x] T008 创建 FastAPI 应用入口 `d:/pyCharmProjects/workSpace03/app/main.py`
- [x] T009 [P] 建立全局路由注册器 `d:/pyCharmProjects/workSpace03/app/api/router.py`
- [x] T010 [P] 建立统一响应与异常模型 `d:/pyCharmProjects/workSpace03/app/api/schemas/common.py`
- [x] T011 建立 SQLite 连接与会话管理 `d:/pyCharmProjects/workSpace03/app/infra/db/session.py`
- [x] T012 [P] 建立基础实体基类与时间戳字段 `d:/pyCharmProjects/workSpace03/app/domain/models/base.py`
- [x] T013 [P] 实现应用配置加载器（含 Anaconda 场景）`d:/pyCharmProjects/workSpace03/app/infra/config/settings.py`
- [x] T014 实现统一日志组件（格式：类名.方法名 >>> 日志信息）`d:/pyCharmProjects/workSpace03/app/infra/logging/logger.py`
- [x] T015 [P] 实现基础权限中间件骨架 `d:/pyCharmProjects/workSpace03/app/api/middleware/authz_middleware.py`
- [x] T016 实现幂等键与请求去重组件 `d:/pyCharmProjects/workSpace03/app/infra/lock/idempotency_guard.py`
- [x] T017 [P] 实现乐观锁通用支持组件 `d:/pyCharmProjects/workSpace03/app/infra/lock/version_guard.py`
- [x] T018 创建 OpenAPI 合同对齐检查脚本 `d:/pyCharmProjects/workSpace03/app/tests/contract/contract_guard.py`

**Checkpoint**: 基础设施完成，可进入用户故事并行实现

---

## Phase 3: User Story 1 - 员工对话式办理日常事务 (Priority: P1) 🎯 MVP

**Goal**: 员工通过自然语言完成请假、报销、流程发起、数据查询等高频事务  
**Independent Test**: 单一会话内连续发起至少三类事务并获得可执行结果

### Implementation for User Story 1

- [x] T019 [P] [US1] 创建对话会话实体 `d:/pyCharmProjects/workSpace03/app/domain/models/conversation_session.py`
- [x] T020 [P] [US1] 创建业务操作请求实体 `d:/pyCharmProjects/workSpace03/app/domain/models/operation_request.py`
- [x] T021 [P] [US1] 创建员工与权限实体 `d:/pyCharmProjects/workSpace03/app/domain/models/employee_access.py`
- [x] T022 [US1] 实现对话状态机组件 `d:/pyCharmProjects/workSpace03/app/ai/orchestrator/conversation_state_machine.py`
- [x] T023 [US1] 实现意图识别策略接口与策略注册（Strategy）`d:/pyCharmProjects/workSpace03/app/ai/orchestrator/intent_strategy.py`
- [x] T024 [US1] 实现工具执行器工厂（Factory）`d:/pyCharmProjects/workSpace03/app/ai/tools/tool_executor_factory.py`
- [x] T025 [US1] 实现请假/报销/流程/查询工具适配器（Adapter）`d:/pyCharmProjects/workSpace03/app/ai/tools/business_tools.py`
- [x] T026 [US1] 实现对话总编排服务 `d:/pyCharmProjects/workSpace03/app/ai/orchestrator/conversation_orchestrator.py`
- [x] T027 [US1] 实现对话操作 API `POST /api/v1/chat/operate` 于 `d:/pyCharmProjects/workSpace03/app/api/routes/chat_routes.py`
- [x] T028 [US1] 接入操作幂等与重复提交防护到对话入口 `d:/pyCharmProjects/workSpace03/app/api/routes/chat_routes.py`
- [x] T029 [US1] 实现对话中心前端页面与会话交互 `d:/webStormProjects/workSpace06/src/views/AiDialogCenterView.vue`
- [x] T030 [P] [US1] 实现前端对话 API 服务封装 `d:/webStormProjects/workSpace06/src/services/chatService.ts`
- [x] T031 [US1] 实现会话状态仓库 `d:/webStormProjects/workSpace06/src/stores/chatStore.ts`
- [x] T032 [US1] 更新 quickstart 中 US1 验收步骤 `d:/pyCharmProjects/workSpace03/specs/001-ai-enterprise-platform/quickstart.md`

**Checkpoint**: US1 单独可运行，完成“对话即操作”最小闭环

---

## Phase 4: User Story 2 - 管理者高并发审批与流程协作 (Priority: P2)

**Goal**: 在并发场景下稳定完成审批流转、会签与通知  
**Independent Test**: 模拟并发提交与并发审批，验证流转正确、状态一致、通知可达

### Implementation for User Story 2

- [x] T033 [P] [US2] 创建审批流程与审批记录实体 `d:/pyCharmProjects/workSpace03/app/domain/models/workflow_models.py`
- [x] T034 [P] [US2] 创建通知事件实体 `d:/pyCharmProjects/workSpace03/app/domain/models/notification_event.py`
- [x] T035 [US2] 实现流程模板方法骨架（Template Method）`d:/pyCharmProjects/workSpace03/app/domain/services/workflow_template_service.py`
- [x] T036 [US2] 实现审批服务（含乐观锁冲突处理）`d:/pyCharmProjects/workSpace03/app/domain/services/approval_service.py`
- [x] T037 [US2] 实现审批 API `POST /api/v1/workflows/{workflowId}/approve` 于 `d:/pyCharmProjects/workSpace03/app/api/routes/workflow_routes.py`
- [x] T038 [US2] 实现通知投递与重试服务 `d:/pyCharmProjects/workSpace03/app/domain/services/notification_service.py`
- [x] T039 [P] [US2] 实现待办与审批管理页面 `d:/webStormProjects/workSpace06/src/views/WorkflowInboxView.vue`
- [x] T040 [P] [US2] 实现审批与通知前端 API 封装 `d:/webStormProjects/workSpace06/src/services/workflowService.ts`
- [x] T041 [US2] 实现并发审批压测脚本 `d:/pyCharmProjects/workSpace03/app/tests/integration/load_approval_simulation.py`
- [x] T042 [US2] 更新 quickstart 中并发审批验收步骤 `d:/pyCharmProjects/workSpace03/specs/001-ai-enterprise-platform/quickstart.md`

**Checkpoint**: US2 在并发下状态一致、无重复审批、通知链路可追溯

---

## Phase 5: User Story 3 - 员工智能问答与经营洞察 (Priority: P3)

**Goal**: 支持知识问答、数据问答与会议纪要结构化输出  
**Independent Test**: 用户可独立完成知识问答、数据问答、纪要生成三类 AI 场景

### Implementation for User Story 3

- [x] T043 [P] [US3] 创建查询任务与知识条目实体 `d:/pyCharmProjects/workSpace03/app/domain/models/query_knowledge_models.py`
- [x] T044 [P] [US3] 创建会议纪要实体 `d:/pyCharmProjects/workSpace03/app/domain/models/meeting_minutes.py`
- [x] T045 [US3] 实现 NL2Query 解析与白名单执行器 `d:/pyCharmProjects/workSpace03/app/ai/nl2query/query_executor.py`
- [x] T046 [US3] 实现知识检索与回答服务 `d:/pyCharmProjects/workSpace03/app/ai/rag/knowledge_service.py`
- [x] T047 [US3] 实现会议纪要结构化生成服务 `d:/pyCharmProjects/workSpace03/app/ai/orchestrator/meeting_minutes_service.py`
- [x] T048 [US3] 实现数据问答 API `POST /api/v1/query/ask` 于 `d:/pyCharmProjects/workSpace03/app/api/routes/query_routes.py`
- [x] T049 [US3] 实现知识问答 API `POST /api/v1/knowledge/ask` 于 `d:/pyCharmProjects/workSpace03/app/api/routes/knowledge_routes.py`
- [x] T050 [P] [US3] 实现智能问答与洞察页面 `d:/webStormProjects/workSpace06/src/views/InsightAssistantView.vue`
- [x] T051 [P] [US3] 实现数据问答与知识问答前端服务 `d:/webStormProjects/workSpace06/src/services/insightService.ts`
- [x] T052 [US3] 对齐并校验合同文件字段 `d:/pyCharmProjects/workSpace03/specs/001-ai-enterprise-platform/contracts/api-contract.yaml`

**Checkpoint**: US3 三类 AI 场景独立可验收，输出可追溯、可解释

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 全局质量、文档完善、可运行性交付

- [x] T053 [P] 汇总并补全架构设计文档 `d:/pyCharmProjects/workSpace03/docs/architecture.md`
- [x] T054 [P] 补全日志与审计规范文档 `d:/pyCharmProjects/workSpace03/docs/observability.md`
- [x] T055 完成后端启动脚本与命令校验 `d:/pyCharmProjects/workSpace03/scripts/start_backend.ps1`
- [x] T056 [P] 完成前端启动脚本与命令校验 `d:/webStormProjects/workSpace06/scripts/start_frontend.ps1`
- [x] T057 完成端到端联调清单并记录结果 `d:/pyCharmProjects/workSpace03/docs/e2e-validation.md`
- [x] T058 执行 quickstart 全流程验证并修订文档 `d:/pyCharmProjects/workSpace03/specs/001-ai-enterprise-platform/quickstart.md`

---

## Phase 7: Gap Closure (Analyze 补齐任务)

**Purpose**: 补齐分析阶段识别的缺口（FR-008/FR-011/FR-012/FR-013 与 SC 验收能力）

- [x] T059 [US2] 实现考勤打卡与月度汇总模型/服务/接口 `app/domain/models/attendance_record.py`、`app/domain/services/attendance_service.py`、`app/api/routes/attendance_routes.py`
- [x] T060 [US1] 实现 AI 调用失败降级策略并接入对话主流程 `app/ai/orchestrator/conversation_orchestrator.py`
- [x] T061 [US3] 实现经营看板汇总服务与接口 `app/domain/services/dashboard_service.py`、`app/api/routes/dashboard_routes.py`
- [x] T062 [US2] 实现审计日志模型、中间件与查询接口 `app/domain/models/audit_log.py`、`app/api/middleware/audit_middleware.py`、`app/api/routes/audit_routes.py`
- [x] T063 [US3] 接入新增路由注册与建表导入 `app/api/router.py`、`app/main.py`
- [x] T064 [US3] 完成考勤与看板前端页面/服务 `d:/webStormProjects/workSpace06/src/views/AttendanceView.vue`、`d:/webStormProjects/workSpace06/src/views/DashboardOverviewView.vue`
- [x] T065 [US3] 完成看板与考勤前端 API 封装 `d:/webStormProjects/workSpace06/src/services/attendanceService.ts`、`d:/webStormProjects/workSpace06/src/services/dashboardService.ts`
- [x] T066 [US2] 增加关键性能探针脚本用于 SC 验收 `app/tests/integration/chat_latency_probe.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: 可立即开始
- **Phase 2 (Foundational)**: 依赖 Phase 1 完成；阻塞全部用户故事
- **Phase 3/4/5 (US1/US2/US3)**: 统一依赖 Phase 2 完成
- **Phase 6 (Polish)**: 依赖至少一个用户故事完成，建议在 US1/US2/US3 完成后集中执行

### User Story Dependencies

- **US1 (P1)**: 无需依赖其他故事，是 MVP 主路径
- **US2 (P2)**: 可独立于 US1 开发，但会复用基础日志/权限/幂等能力
- **US3 (P3)**: 可独立于 US1/US2 开发，但共享基础 AI 编排与权限控制

### Within Each User Story

- 模型定义优先于服务实现
- 服务实现优先于 API 路由
- API 路由优先于前端联调
- 每个故事完成后先做独立验收，再进入更高优先级扩展

### Parallel Opportunities

- Setup 阶段：T002/T004/T006 可并行
- Foundational 阶段：T009/T010/T012/T013/T015/T017 可并行
- US1 阶段：T019/T020/T021 与 T030 可并行
- US2 阶段：T033/T034/T039/T040 可并行
- US3 阶段：T043/T044/T050/T051 可并行
- Polish 阶段：T053/T054/T056 可并行

---

## Parallel Example: User Story 1

```bash
Task: "T019 [US1] 创建对话会话实体 in d:/pyCharmProjects/workSpace03/app/domain/models/conversation_session.py"
Task: "T020 [US1] 创建业务操作请求实体 in d:/pyCharmProjects/workSpace03/app/domain/models/operation_request.py"
Task: "T021 [US1] 创建员工与权限实体 in d:/pyCharmProjects/workSpace03/app/domain/models/employee_access.py"
Task: "T030 [US1] 实现前端对话 API 服务封装 in d:/webStormProjects/workSpace06/src/services/chatService.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. 完成 Phase 1 + Phase 2
2. 完成 Phase 3（US1）
3. 执行 US1 独立验收（单会话多事务）
4. 通过后即可先行演示/交付 MVP

### Incremental Delivery

1. 基础能力完成后先交付 US1
2. 叠加 US2（并发审批与通知）
3. 叠加 US3（知识问答、数据问答、会议纪要）
4. 每一阶段保持可运行、可回归、可演示

### Parallel Team Strategy

1. 共同完成 Setup + Foundational
2. 并行分工：
   - 成员 A：US1 对话操作链路
   - 成员 B：US2 审批与通知链路
   - 成员 C：US3 智能问答链路
3. 通过 API 契约与日志规范统一集成

---

## Notes

- 所有任务均满足 `- [ ] Txxx [P?] [US?] 描述 + 文件路径` 格式规范
- 每个用户故事均可独立实现与验收，满足分阶段交付
- 设计模式落地要求：
  - US1: Strategy + Factory + Adapter
  - US2: Template Method + 乐观锁
  - US3: Adapter（模型/检索）+ 安全执行器
- 日志实现必须统一：`类名.方法名 >>> 日志信息`
