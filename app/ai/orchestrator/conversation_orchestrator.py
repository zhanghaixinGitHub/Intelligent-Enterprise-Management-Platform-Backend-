from __future__ import annotations

from uuid import uuid4
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from app.ai.orchestrator.conversation_state_machine import ConversationStateMachine
from app.ai.orchestrator.intent_strategy import IntentStrategy
from app.ai.prompt.prompt_engineering_service import PromptEngineeringService
from app.ai.tools.tool_executor_factory import ToolExecutorFactory
from app.infra.config.settings import settings
from app.infra.logging.logger import AppLogger


class ConversationOrchestrator:
    def __init__(self) -> None:
        self._logger = AppLogger(self.__class__.__name__)
        self._state_machine = ConversationStateMachine()
        self._tool_factory = ToolExecutorFactory()
        self._prompt_service = PromptEngineeringService()
        self._llm = None
        if settings.openai_api_key:
            self._llm = ChatOpenAI(
                model=settings.openai_model,
                base_url=settings.openai_base_url,
                api_key=SecretStr(settings.openai_api_key),
                temperature=0.2,
            )
        # 将 LLM 注入意图策略，以启用第三层 Function Calling 兜底。
        self._intent_strategy = IntentStrategy(llm=self._llm)

    def handle(self, session_id: str, employee_id: str, message: str) -> dict:
        self._logger.info("handle", "收到对话请求", session_id=session_id, employee_id=employee_id)
        intent_result = self._intent_strategy.detect(message)
        self._logger.info(
            "handle",
            "意图识别完成",
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            route=intent_result.route,
            reason=intent_result.reason,
        )
        tool = self._tool_factory.get(intent_result.intent)

        if tool is None:
            return {
                "requestId": str(uuid4()),
                "status": "needs_more_info",
                "reply": "我暂时没识别到明确业务动作，请补充你要办理的业务类型。",
                "nextRequiredFields": ["operationType"],
            }

        # 提示词工程增强：
        # 通过 PromptEngineeringService 构造“可控模板 + few-shot”提示词，
        # 将路由结果（intent/route/confidence）注入上下文，提升回复一致性。
        if self._llm is not None:
            try:
                reply_prompt = self._prompt_service.build_reply_generation_prompt(
                    message=message,
                    intent=intent_result.intent,
                    route=intent_result.route,
                    confidence=intent_result.confidence,
                )
                llm_reply = self._llm.invoke(reply_prompt).content
            except Exception as exc:
                # AI 调用失败时启动降级策略，确保关键流程可继续。
                self._logger.error("handle", "AI调用失败，进入降级模式", error=str(exc))
                llm_reply = f"已识别为 {intent_result.intent}，当前AI服务繁忙，已切换规则模式受理"
        else:
            llm_reply = f"已识别为 {intent_result.intent}，当前AI服务不可用，已切换规则模式受理"

        _ = tool({"session_id": session_id, "employee_id": employee_id, "message": message})
        state = self._state_machine.transit("collecting", has_missing_fields=False, execution_ok=True)

        return {
            "requestId": str(uuid4()),
            "status": "success" if state.state == "completed" else "processing",
            "reply": f"{llm_reply}，已为你受理。",
            "nextRequiredFields": [],
        }
