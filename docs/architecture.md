# 系统架构说明（MVP）

## 架构分层

- `app/api`: 对外接口层，负责参数校验与路由编排
- `app/domain`: 业务规则层，沉淀审批、通知、对话业务逻辑
- `app/ai`: AI 能力层，包含 LangChain 编排、工具路由、RAG、NL2Query
- `app/infra`: 基础设施层，负责数据库、配置、日志、锁与并发保护

## 关键设计模式

- `Strategy`：意图识别策略切换
- `Factory`：Tool 执行器统一创建
- `Adapter`：业务工具与外部模型调用适配
- `Template Method`：审批流程执行骨架

## 并发一致性策略

- 请求幂等键去重（避免重复提交）
- 乐观锁版本校验（避免并发审批冲突）
- 统一审计日志（可追溯）

## 架构演进文档

- `docs/flowable-distributed-architecture.md`：Python + Java Flowable 分布式演进架构方案
- `docs/service-split-plan.md`：基于当前代码结构的 Python 保留 / Java 迁移拆分清单

