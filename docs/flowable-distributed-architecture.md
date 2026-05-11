# Python + Java Flowable 分布式演进架构方案

## 1. 文档目标

本文档用于明确当前 `workSpace03` 从 **Python 单体智能企业平台** 演进为 **Python + Java Flowable 双服务分布式架构** 的目标蓝图，重点解决以下两个问题：

1. 如何引入 Java `Flowable` 做企业级审批流。
2. 如何在不推翻当前 Python 能力的前提下，把项目逐步演进为分布式系统。

---

## 2. 当前项目现状总结

当前后端项目 `D:\pyCharmProjects\workSpace03` 主要职责如下：

- `app/api`：FastAPI 路由、依赖、鉴权中间件、审计中间件
- `app/domain`：认证、考勤、审批、通知、仪表盘等业务规则
- `app/ai`：对话编排、RAG、NL2Query、工具执行
- `app/infra`：数据库、配置、日志、锁、队列等基础设施
- `data/ai_enterprise.db`：当前 SQLite 数据文件

当前审批能力仍处于轻量模板阶段：

- `app/api/routes/workflow_routes.py`
- `app/domain/services/approval_service.py`
- `app/domain/services/workflow_template_service.py`
- `app/domain/models/workflow_models.py`

这套实现适合 MVP，但不适合后续复杂审批流场景（如流程定义、会签、加签、转办、撤回、历史轨迹、流程图可视化等）。

---

## 3. 为什么采用 Python + Java 双栈

## 3.1 Python 继续保留的原因

Python 已经承担并且适合继续承担以下能力：

- AI 对话中心
- RAG 知识问答
- 自然语言转业务操作
- 数据查询与分析
- 前端聚合接口（BFF）
- 登录态聚合与菜单返回

这些能力与 LLM、检索、编排、数据处理高度相关，Python 生态更有优势。

## 3.2 Java + Flowable 适合引入的原因

审批流属于典型的企业流程引擎场景，Flowable 相比手写流程模板有明显优势：

- 支持 BPMN 流程定义
- 支持流程部署与版本管理
- 支持任务待办、已办、历史轨迹
- 支持条件网关、并行网关、用户任务、服务任务
- 支持会签、加签、委派、转办等扩展能力
- 更适合企业级长期演进

因此推荐采用：

- **Python：智能业务平台 / BFF / AI 中台**
- **Java：Flowable 审批流中心**

---

## 4. 目标架构总览

## 4.1 服务划分

### 4.1.1 Python 平台服务（保留并增强）

职责：

- 用户认证与登录态聚合
- 菜单权限聚合
- AI 对话编排
- 自然语言业务入口
- 知识问答与数据分析
- 仪表盘聚合
- 对审批流服务进行统一适配

建议服务名：`ai-enterprise-platform`

### 4.1.2 Java 审批流服务（新增）

职责：

- 流程定义管理
- BPMN 部署与版本控制
- 流程实例发起
- 待办任务查询
- 审批动作处理
- 历史轨迹查询
- 流程监听、审计、业务回调

建议服务名：`workflow-center`

### 4.1.3 前端应用

当前前端路径已知为：

- `D:\webStormProjects\workSpace06`

前端建议仍然保持一个统一入口，优先对接 Python BFF；后续如审批域成熟，也可以在网关层对部分 Java 接口做透传。

---

## 4.2 分布式拓扑建议

```text
[ Vue 前端 workSpace06 ]
            |
            v
 [ Python BFF / AI 平台服务 ]
      |                 |
      | HTTP            | Redis / MQ / DB
      v                 v
 [ Java Flowable 审批服务 ]
```

### 架构原则

1. 前端优先只感知一个统一业务入口，降低前端复杂度。
2. Python 负责用户体验聚合，Java 负责审批流核心执行。
3. 分布式先从“服务拆分 + HTTP 调用”开始，再逐步引入 Redis、MQ、网关、链路追踪。

---

## 5. 推荐技术选型

## 5.1 Python 服务

- 框架：FastAPI
- ORM：SQLAlchemy
- 配置：环境变量 + `.env`
- 缓存：Redis（后续）
- 异步任务：Celery / RQ（二选一，后续按场景引入）
- 日志：统一结构化日志，日志格式遵循 `类名.方法名   >>>   日志信息`

## 5.2 Java 服务

- JDK：17+
- 框架：Spring Boot 3.x
- 审批引擎：Flowable
- 数据访问：MyBatis-Plus 或 Spring Data JPA（二选一，建议团队统一）
- 工具库：优先评估 Hutool
- 缓存：Redis
- 数据库：MySQL 8.x / PostgreSQL
- 日志：统一结构化日志，日志格式遵循 `类名.方法名   >>>   日志信息`

## 5.3 基础设施

- 主数据库：MySQL 8.x（推荐）
- 缓存：Redis
- 消息队列：RabbitMQ 或 Kafka（第二阶段引入）
- 网关：Nginx / Spring Cloud Gateway / APISIX（后续按规模引入）
- 可观测性：Prometheus + Grafana + TraceId 链路追踪

> 说明：当前项目仍使用 SQLite，本地演示可以保留；但要落地 Flowable 与分布式，不建议继续以 SQLite 作为主业务数据库。

---

## 6. 目标目录结构设计（完成事项 1）

## 6.1 Python 项目未来目录建议

```text
workSpace03/
├─ app/
│  ├─ api/
│  │  ├─ dependencies/
│  │  ├─ middleware/
│  │  ├─ routes/
│  │  │  ├─ auth_routes.py
│  │  │  ├─ chat_routes.py
│  │  │  ├─ knowledge_routes.py
│  │  │  ├─ query_routes.py
│  │  │  ├─ dashboard_routes.py
│  │  │  ├─ attendance_routes.py
│  │  │  ├─ workflow_routes.py          # 未来改为审批聚合/适配入口
│  │  │  └─ audit_routes.py
│  │  └─ schemas/
│  ├─ application/
│  │  ├─ dto/
│  │  ├─ assemblers/
│  │  └─ workflow_facade/               # 新增：调用 Java Flowable 的门面层
│  ├─ ai/
│  │  ├─ orchestrator/
│  │  ├─ rag/
│  │  ├─ nl2query/
│  │  ├─ prompt/
│  │  └─ tools/
│  ├─ domain/
│  │  ├─ constants/
│  │  ├─ models/
│  │  ├─ repositories/
│  │  └─ services/
│  ├─ integration/
│  │  └─ workflow_center/
│  │     ├─ client.py                   # 新增：审批中心 HTTP 客户端
│  │     ├─ request_mapper.py           # 新增：跨服务请求转换
│  │     ├─ response_mapper.py          # 新增：跨服务响应转换
│  │     └─ fallback.py                 # 新增：降级与超时兜底
│  ├─ infra/
│  │  ├─ cache/
│  │  ├─ config/
│  │  ├─ db/
│  │  ├─ lock/
│  │  ├─ logging/
│  │  └─ queue/
│  ├─ security/
│  └─ main.py
├─ data/
├─ docs/
├─ scripts/
├─ tests/
│  ├─ contract/
│  ├─ integration/
│  └─ unit/
└─ specs/
```

### 设计说明

1. **保留现有 FastAPI 主体结构**，避免对已形成的 AI 能力造成冲击。
2. 新增 `application` 与 `integration` 层，用于承接跨服务调用与 DTO 适配。
3. `workflow_routes.py` 不再直接承载流程引擎逻辑，而是变为 **BFF/适配层入口**。
4. `integration/workflow_center` 采用 **适配器模式（Adapter Pattern）**，隔离 Java 服务契约变化对现有业务代码的影响。

---

## 6.2 Java Flowable 服务目录建议

```text
workflow-center/
├─ src/main/java/com/company/workflow/
│  ├─ WorkflowCenterApplication.java
│  ├─ controller/
│  │  ├─ ProcessDefinitionController.java
│  │  ├─ ProcessInstanceController.java
│  │  ├─ TaskController.java
│  │  └─ WorkflowCallbackController.java
│  ├─ service/
│  │  ├─ ProcessDefinitionService.java
│  │  ├─ ProcessInstanceService.java
│  │  ├─ TaskService.java
│  │  ├─ IdentityBridgeService.java
│  │  └─ AuditTrailService.java
│  ├─ service/impl/
│  ├─ dao/
│  ├─ entity/
│  │  ├─ ProcessBusinessEntity.java
│  │  ├─ WorkflowTaskViewEntity.java
│  │  └─ WorkflowAuditEntity.java
│  ├─ dto/
│  │  ├─ request/
│  │  └─ response/
│  ├─ config/
│  │  ├─ FlowableConfig.java
│  │  ├─ SecurityConfig.java
│  │  └─ WebMvcConfig.java
│  ├─ integration/
│  │  └─ python/
│  │     ├─ PythonUserClient.java
│  │     └─ PythonNotifyClient.java
│  ├─ listener/
│  │  ├─ TaskCreateListener.java
│  │  ├─ TaskCompleteListener.java
│  │  └─ ProcessEndListener.java
│  ├─ assembler/
│  ├─ exception/
│  └─ common/
├─ src/main/resources/
│  ├─ application.yml
│  ├─ db/migration/
│  └─ processes/
│     ├─ leave-approval.bpmn20.xml
│     ├─ reimburse-approval.bpmn20.xml
│     └─ purchase-approval.bpmn20.xml
├─ src/test/java/
├─ pom.xml
└─ README.md
```

### 设计说明

1. 遵循团队 Java 规范中的 **分层架构**：`Controller -> Service -> DAO -> Entity`。
2. `listener` 专门承接 Flowable 流程事件，避免将监听逻辑散落在控制层。
3. `integration/python` 用于和 Python 平台进行用户上下文、通知、回调交互，避免跨服务调用污染核心流程服务。
4. `processes/` 存放 BPMN 流程定义文件，纳入版本控制，保证流程配置可追踪、可回滚。

---

## 7. 分布式边界设计

## 7.1 身份边界

### 建议原则

- **Python 服务**：认证中心、用户上下文主源
- **Java 服务**：流程引擎执行方、身份消费方

### 落地方式

Python 在调用 Java 审批流服务时，透传以下最小身份上下文：

- `employeeId`
- `username`
- `displayName`
- `departmentId`
- `roleCodes`
- `tokenId` / `requestId`

Java 服务不要在第一阶段重复建设整套登录与菜单体系，只做服务端鉴权校验与业务参与人映射。

---

## 7.2 数据边界

### Python 数据域

适合继续保留：

- 用户账号与权限主数据
- 对话会话
- 操作请求
- 知识库与查询任务
- 仪表盘聚合
- 考勤数据（第一阶段）

### Java 数据域

适合迁移或新增：

- Flowable 引擎表
- 审批流程定义
- 流程实例业务扩展表
- 审批任务视图表
- 流程历史审计表

### 关键原则

1. 不要让 Python 和 Java 同时写同一份流程状态主表。
2. 流程状态的最终真相源应该在 Java Flowable 服务。
3. Python 需要展示审批信息时，应优先通过接口读取 Java 服务，而不是本地维护第二份流程状态。

---

## 7.3 接口边界

### Python 暴露给前端的接口风格

建议继续保留统一接口前缀：

- `POST /api/v1/workflows/start`
- `GET /api/v1/workflows/todos`
- `GET /api/v1/workflows/done`
- `GET /api/v1/workflows/{workflowId}`
- `POST /api/v1/workflows/{workflowId}/approve`
- `POST /api/v1/workflows/{workflowId}/reject`
- `POST /api/v1/workflows/{workflowId}/withdraw`

这些接口由 Python BFF 接收后，内部转发给 Java Flowable 服务。

### Java 服务内部接口建议

- `POST /internal/process-definitions/deploy`
- `POST /internal/process-instances/start`
- `GET /internal/tasks/todo`
- `GET /internal/tasks/done`
- `POST /internal/tasks/{taskId}/complete`
- `GET /internal/process-instances/{processInstanceId}`
- `GET /internal/process-instances/{processInstanceId}/history`

---

## 8. 分阶段实施路线

## 阶段一：边界收敛

目标：在 Python 代码层面先把审批域与 AI 域区分清楚。

交付：

- 审批域接口清单
- Python 对 Java 的 DTO 设计
- 统一用户上下文透传模型

## 阶段二：建设 Java Flowable 服务

目标：具备流程定义、发起、待办、审批、历史查询基础能力。

交付：

- Java 服务骨架
- Flowable 基础流程
- MySQL 持久化
- 审批核心接口

## 阶段三：Python 对接 Java 审批中心

目标：前端仍通过 Python 访问，但审批底层已经切换到 Java。

交付：

- Python 适配客户端
- 审批聚合路由
- 跨服务超时与降级策略

## 阶段四：引入 Redis

目标：增强分布式基础能力。

交付：

- 缓存热点查询
- 分布式锁
- 幂等控制
- Token 黑名单（如需要）

## 阶段五：引入 MQ

目标：让审批、通知、AI 总结之间异步解耦。

交付：

- 审批完成事件
- 催办通知事件
- AI 摘要任务事件

## 阶段六：治理与可观测性

目标：补足企业级分布式治理能力。

交付：

- 网关
- TraceId 链路追踪
- 指标监控
- 告警
- 审计与日志归集

---

## 9. 风险与约束

## 9.1 当前最需要规避的风险

1. **过早引入过重微服务全家桶**：先拆服务，不要一开始就上全套注册中心、服务网格。
2. **双主身份源风险**：不要在 Python 与 Java 两边各自维护一套用户体系。
3. **双写流程状态风险**：流程状态最终真相源必须单一。
4. **SQLite 持续扩张风险**：本地演示可以保留，分布式落地必须迁移到 MySQL/PostgreSQL。

## 9.2 关键架构决策

- 审批流最终选型：**Flowable**
- 分布式演进方式：**按领域拆分服务，渐进式演进**
- 前端访问策略：**优先经由 Python BFF 聚合**
- 身份中心：**短期保留在 Python**

---

## 10. 设计模式说明

本方案建议采用的核心设计思想如下：

1. **BFF 模式**：Python 服务作为前端统一入口，降低前端直连多服务的复杂度。
2. **适配器模式**：Python 通过 `integration/workflow_center` 适配 Java Flowable 服务。
3. **防腐层模式（Anti-Corruption Layer）**：隔离 Flowable 领域对象，避免 Java 服务契约直接污染 Python 内部领域模型。
4. **事件驱动模式**：后续通过 MQ 实现审批完成、通知、AI 总结等异步联动。
5. **分层架构模式**：Java 服务遵循 `Controller -> Service -> DAO -> Entity`，Python 服务继续坚持 `api -> domain -> infra` 分层。

---

## 11. 结论

当前项目最合理的演进路线不是推翻重做，而是：

1. 保留 Python 作为智能业务平台主服务。
2. 新增 Java `Flowable` 审批流中心。
3. 通过明确领域边界把项目自然演进为分布式架构。
4. 先实现“两个服务 + HTTP 调用”，再逐步补齐 Redis、MQ、网关和可观测性。

这条路线既符合当前项目基础，也符合企业级系统的真实性、可维护性、可扩展性与后续落地成本控制要求。

