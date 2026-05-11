# Python 保留 / Java 迁移服务拆分清单

## 1. 文档目标

本文档基于当前项目 `D:\pyCharmProjects\workSpace03` 的实际文件结构，给出面向 **Python + Java Flowable + 分布式演进** 的服务拆分清单，明确回答两个问题：

1. 当前哪些能力继续保留在 Python。
2. 当前哪些能力应迁移到 Java 服务侧实现，其中审批流优先落在 `Flowable`，其余能力则按企业级项目标准、技术生态匹配度与长期维护成本决定归属。

本文档强调的是 **领域边界**，不是简单按语言喜好做切分。

---

## 2. 拆分原则

### 2.1 总体原则

1. **技术选型不能只按语言偏好决定，而要按业务领域特征、技术生态优势与企业级治理要求决定。**
2. **AI、对话、知识、数据分析、智能编排等更适合 Python 生态的能力，继续优先保留在 Python。**
3. **审批流引擎、复杂事务编排、长生命周期流程、企业级集成、强治理后台能力等更适合 Java 生态的能力，优先落在 Java。当前最明确的第一批落地方向是 `Flowable` 审批流。**
4. **认证与当前用户上下文短期继续保留在 Python，Java 作为身份消费方；后续是否拆分统一身份中心，取决于组织规模与系统复杂度。**
5. **跨服务采用 BFF + 适配器模式，不让前端直接承受过多服务拆分成本。**
6. **所有拆分都必须符合企业级项目标准：单一职责、边界清晰、服务端鉴权、审计可追溯、配置可治理、异常可定位、演进可持续。**

### 2.2 判断标准

如果某项能力满足以下特征，优先保留在 Python：

- 与 LLM、RAG、自然语言理解、知识检索、Prompt 编排强相关
- 更偏聚合、编排、数据处理、算法调用、轻交互体验
- 需要快速迭代验证、试错成本低、模型替换频繁
- 更适合作为前端统一入口、智能中台或业务编排层

如果某项能力满足以下特征，优先迁移到 Java：

- 需要 BPMN 引擎或复杂流程编排
- 需要强事务一致性、复杂状态流转、长生命周期业务管理
- 需要审批节点状态管理、流程版本、流程历史、审计闭环
- 需要复杂企业级治理能力，例如任务中心、规则扩展、组织架构映射、对接 ERP/OA/消息中心等集成场景
- 需要更稳定的模块化分层、成熟中间件生态和长期后台治理能力

### 2.3 企业级拆分结论

本项目引入 Java，**不是为了“只有审批流才用 Java”**，而是为了建立一套更符合企业级项目标准的技术分工原则：

- **适合 Python 的能力由 Python 实现**，发挥 AI、编排、数据处理与快速迭代优势。
- **适合 Java 的能力由 Java 实现**，发挥流程引擎、复杂事务、治理能力与企业集成优势。
- **审批流只是第一批最适合拆到 Java 的领域，不是 Java 的唯一职责边界。**

因此，后续如果出现以下企业级能力，也应优先评估是否迁移或新增到 Java 侧：

- 统一任务中心
- 复杂消息/通知编排中心
- 组织架构与岗位规则中心
- 规则引擎、集成适配层、主数据治理模块

最终目标不是“语言混搭”，而是形成 **按领域分工、按优势选型、按企业标准治理** 的可持续架构。

---

## 3. 路由层拆分清单（完成事项 2 的第一部分）

| 当前文件 | 当前职责 | 建议归属 | 处理建议 |
|---|---|---|---|
| `app/api/routes/auth_routes.py` | 登录、当前用户、菜单 | 保留 Python | 继续作为统一认证入口；Java 不重复建设登录接口 |
| `app/api/routes/chat_routes.py` | AI 对话操作 | 保留 Python | 继续保留；后续可通过意图识别联动审批发起 |
| `app/api/routes/query_routes.py` | 数据问答 | 保留 Python | 继续保留 |
| `app/api/routes/knowledge_routes.py` | 知识问答 | 保留 Python | 继续保留 |
| `app/api/routes/dashboard_routes.py` | 仪表盘总览 | 保留 Python | 保留聚合层职责，后续增加对 Java 审批待办数的聚合查询 |
| `app/api/routes/attendance_routes.py` | 考勤打卡与月汇总 | 第一阶段保留 Python | 后续如果组织规模扩大，可独立拆分为考勤服务 |
| `app/api/routes/audit_routes.py` | 审计日志查询 | 第一阶段保留 Python | 平台审计先统一保留；后续可做跨服务审计汇聚 |
| `app/api/routes/workflow_routes.py` | 当前审批动作接口 | **保留路由，迁移内部能力到 Java** | 该文件未来改造成 Python BFF，对前端保持稳定契约，内部转发到 Java Flowable 服务 |

### 重点说明：`workflow_routes.py`

当前文件：

- `app/api/routes/workflow_routes.py`

当前逻辑直接调用：

- `ApprovalService`
- `NotificationService`

未来建议改造成：

- 请求校验
- 当前用户上下文收集
- 调用 `integration/workflow_center/client.py`
- 统一处理超时、熔断、错误映射
- 审批完成后触发平台侧通知或 AI 联动

也就是说：

> `workflow_routes.py` **文件保留**，但它不再承载审批引擎核心逻辑，而是变成平台聚合层入口。

---

## 4. 服务层拆分清单（完成事项 2 的第二部分）

| 当前文件 | 当前职责 | 建议归属 | 处理建议 |
|---|---|---|---|
| `app/domain/services/auth_service.py` | 认证、用户上下文、菜单组装、角色权限解析 | 保留 Python | 作为统一身份与菜单服务 |
| `app/domain/services/attendance_service.py` | 打卡、月度汇总 | 第一阶段保留 Python | 保持现状 |
| `app/domain/services/dashboard_service.py` | 看板汇总 | 保留 Python | 增强为跨服务聚合查询 |
| `app/domain/services/notification_service.py` | 发送通知 | 第一阶段保留 Python | 可作为平台通知中心雏形，后续接 MQ |
| `app/domain/services/approval_service.py` | 审批动作处理 | **迁移到 Java** | Python 侧改为适配门面或删除 |
| `app/domain/services/workflow_template_service.py` | 审批模板骨架 | **迁移到 Java / 废弃** | 被 Flowable 流程定义替代；模板骨架逻辑不再作为核心实现 |

### 重点说明 1：`approval_service.py`

当前 `ApprovalService` 本质上只做了两件事：

1. 乐观锁版本校验
2. 调用 `WorkflowTemplateService` 返回审批结果

这说明它目前是 **轻量模拟审批服务**，并不是真正的企业审批引擎服务。该能力最适合迁移到 Java Flowable 服务，由 Java 统一承接：

- 审批通过/驳回
- 节点流转
- 任务完成
- 版本一致性
- 流程状态更新

### 重点说明 2：`workflow_template_service.py`

当前类使用了 **模板方法模式（Template Method）**，适合做 MVP 演示；但在引入 Flowable 后，审批动作应该交给：

- BPMN 流程定义
- Flowable 任务节点
- Flowable 监听器
- Flowable 历史服务

因此它的定位会发生变化：

- 如果只是历史兼容，Python 中可短期保留为兜底逻辑
- 如果正式切换 Flowable，应逐步退役

---

## 5. 模型层拆分清单（完成事项 2 的第三部分）

| 当前文件 | 当前职责 | 建议归属 | 处理建议 |
|---|---|---|---|
| `app/domain/models/auth_models.py` | 登录账号 | 保留 Python | 继续作为认证中心主表 |
| `app/domain/models/employee_access.py` | 员工与权限策略 | 保留 Python | 短期继续作为身份与菜单主数据 |
| `app/domain/models/conversation_session.py` | 对话会话 | 保留 Python | AI 域核心数据 |
| `app/domain/models/operation_request.py` | 操作请求记录 | 保留 Python | 可用于 AI 到业务的编排审计 |
| `app/domain/models/query_knowledge_models.py` | 数据查询任务、知识条目 | 保留 Python | 继续保留 |
| `app/domain/models/meeting_minutes.py` | 会议纪要 | 保留 Python | 继续保留 |
| `app/domain/models/attendance_record.py` | 考勤记录 | 第一阶段保留 Python | 暂不拆分 |
| `app/domain/models/audit_log.py` | 审计日志 | 第一阶段保留 Python | 平台审计统一保留 |
| `app/domain/models/notification_event.py` | 通知事件 | 第一阶段保留 Python | 后续可演进为独立通知中心 |
| `app/domain/models/workflow_models.py` | 流程实例、审批记录 | **迁移到 Java** | Python 中逐步停止作为流程真相源，改从 Java 审批服务查询 |

### 重点说明：`workflow_models.py`

当前模型包括：

- `WorkflowInstance`
- `ApprovalRecord`

这两张表本质上就是审批流领域主表。引入 Flowable 后：

1. 流程状态真相源应转移到 Java Flowable 服务。
2. Python 不应再继续维护第二份主流程状态。
3. 如确需本地缓存，也只能做只读投影，不做最终写入源。

也就是说：

> `workflow_models.py` 对应的数据职责应迁移到 Java 审批流中心，Python 只保留聚合展示能力。

---

## 6. 常量、配置与安全层拆分清单

| 当前文件/目录 | 当前职责 | 建议归属 | 处理建议 |
|---|---|---|---|
| `app/domain/constants/auth_catalog.py` | 菜单目录、权限种子、动作规则 | 保留 Python | 继续作为平台侧菜单与权限静态目录 |
| `app/api/dependencies/security.py` | 当前用户上下文解析 | 保留 Python | 保持平台统一身份入口 |
| `app/security/token_service.py` | Token 签发与校验 | 保留 Python | 短期统一由 Python 处理登录态 |
| `app/api/middleware/authz_middleware.py` | 平台鉴权中间件 | 保留 Python | 保持现状；Java 需做自身服务端鉴权 |
| `app/api/middleware/audit_middleware.py` | 审计记录 | 保留 Python | 平台审计保留 |
| `app/infra/config/settings.py` | 平台配置中心入口 | 保留 Python | 新增 Java 服务后，两边分别维护自己的配置 |

### 补充建议

Java 服务不应直接复用 Python 的权限目录代码，而应通过以下两种方式之一获得必要信息：

1. Python 在调用时透传最小权限上下文。
2. Java 通过平台内部接口查询必要的用户/角色信息。

这样可以避免跨语言共享领域代码带来的耦合风险。

---

## 7. AI 能力拆分清单

| 当前目录 | 当前职责 | 建议归属 | 处理建议 |
|---|---|---|---|
| `app/ai/orchestrator/` | 对话状态机、意图编排 | 保留 Python | 继续保留 |
| `app/ai/rag/` | 知识问答 | 保留 Python | 继续保留 |
| `app/ai/nl2query/` | 自然语言转数据查询 | 保留 Python | 继续保留 |
| `app/ai/tools/` | 业务工具执行 | 保留 Python | 后续可增加“发起审批”工具，内部调用 Java Flowable 服务 |
| `app/ai/prompt/` | Prompt 工程 | 保留 Python | 继续保留 |

### 关键设计意图

AI 服务未来可以成为审批流的“自然语言入口”，例如：

- 用户说“帮我提交请假审批”
- Python 识别意图并补齐参数
- Python 调用 Java Flowable 服务发起流程
- Java 返回流程实例信息
- Python 再把结果整理成自然语言回复给前端

这也是为什么：

> 审批流迁移到 Java 后，AI 编排仍然必须留在 Python。

---

## 8. 建议新增的 Python 适配层文件

为支撑拆分后的分布式调用，建议在 Python 中新增如下结构：

```text
app/
├─ application/
│  ├─ dto/
│  │  ├─ workflow_request.py
│  │  └─ workflow_response.py
│  └─ workflow_facade/
│     └─ workflow_facade_service.py
├─ integration/
│  └─ workflow_center/
│     ├─ client.py
│     ├─ request_mapper.py
│     ├─ response_mapper.py
│     └─ fallback.py
```

### 职责说明

- `workflow_facade_service.py`：对路由层提供统一审批门面
- `client.py`：封装 HTTP 调用 Java Flowable 服务
- `request_mapper.py`：把 Python 领域请求转换成 Java 服务契约
- `response_mapper.py`：把 Java 返回结果转换成前端稳定输出
- `fallback.py`：超时、服务不可用、降级处理

这里采用的是 **门面模式 + 适配器模式**，主要目的是在不污染现有 Python 业务层的前提下，平滑接入 Java 审批服务。

---

## 9. 建议新增的 Java 领域能力

Java `workflow-center` 服务中建议重点落以下模块：

1. `ProcessDefinitionController / Service`
   - 部署流程
   - 查询流程定义
   - 管理版本

2. `ProcessInstanceController / Service`
   - 发起流程
   - 查询流程实例
   - 撤回流程

3. `TaskController / Service`
   - 查询待办
   - 查询已办
   - 审批通过/驳回
   - 转办/委派/加签（后续）

4. `AuditTrailService`
   - 记录流程轨迹
   - 输出审计视图

5. `IdentityBridgeService`
   - 对接 Python 用户上下文
   - 解析流程参与人
   - 建立组织架构映射

---

## 10. 推荐迁移顺序

## 第一步：保留外部接口稳定

优先保持前端调用的 `/api/v1/workflows/**` 路径不变，避免前端大面积重构。

## 第二步：迁移流程引擎主逻辑

优先迁移：

- `approval_service.py`
- `workflow_template_service.py`
- `workflow_models.py`

这是价值最高、边界最清晰的一组。

## 第三步：Python 只保留审批聚合入口

保留：

- 请求接收
- 当前用户上下文注入
- 错误转换
- 通知联动
- AI 编排联动

不再保留：

- 主流程状态计算
- 主节点流转
- 审批动作最终执行

## 第四步：增加跨服务查询聚合

例如：

- `dashboard_service.py` 聚合 Java 审批待办数
- `chat` 场景中发起流程与查询流程状态

---

## 11. 最终结论

基于当前项目实际情况，建议形成如下清晰边界：

### 保留在 Python 的核心能力

- 认证登录
- 当前用户上下文
- 菜单权限聚合
- AI 对话
- RAG 知识问答
- NL2Query 数据分析
- 仪表盘聚合
- 通知中心雏形
- 考勤（第一阶段）
- 审计（第一阶段）
- 审批聚合路由与适配层

### 迁移到 Java Flowable 的核心能力

- 流程定义
- 流程部署与版本
- 流程实例生命周期
- 待办/已办任务
- 审批通过/驳回/撤回/转办
- 流程轨迹与历史
- 审批流领域主数据

### 关键一句话

> Python 负责“智能入口与业务聚合”，Java Flowable 负责“审批流执行与流程真相源”。

这个切分方式既符合当前项目现状，也最利于后续平滑演进为企业级分布式系统。

