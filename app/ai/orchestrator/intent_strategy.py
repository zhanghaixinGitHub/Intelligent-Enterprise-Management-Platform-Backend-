from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field

from app.ai.prompt.prompt_engineering_service import PromptEngineeringService
from app.infra.logging.logger import AppLogger


@dataclass
class IntentResult:
    intent: str
    confidence: float
    route: str = "unknown"
    reason: str = ""


class _IntentDecision(BaseModel):
    """
    LLM Function Calling 的结构化输出模型。
    通过 Pydantic 约束字段，确保兜底识别返回可解析的稳定结构。
    """

    intent: Literal["leave", "reimburse", "workflow", "query", "knowledge", "minutes", "unknown"] = Field(
        description="识别出的业务意图枚举。"
    )
    confidence: float = Field(ge=0.0, le=1.0, description="意图置信度，范围 0~1。")
    reason: str = Field(description="给出简短判断依据，便于观测和调试。")


class RuleEngineIntentRecognizer:
    """
    第一层：规则引擎（快速路径）。
    设计说明：
    - 采用“策略模式（Strategy Pattern）”封装可替换识别器；
    - 当前使用关键词规则，耗时低、可解释性强，适合作为高频意图的首层路由。
    """

    _RULES: dict[str, tuple[str, ...]] = {
        "leave": ("请假", "休假", "调休", "年假", "病假"),
        "reimburse": ("报销", "发票", "差旅费", "餐补", "费用"),
        "workflow": ("审批", "流程", "待办", "通过", "驳回"),
        "query": ("查询", "统计", "多少", "报表", "数据"),
        "knowledge": ("制度", "政策", "规范", "手册", "知识库"),
        "minutes": ("会议纪要", "会议总结", "纪要"),
    }

    def detect(self, message: str) -> IntentResult:
        for intent, keywords in self._RULES.items():
            if any(keyword in message for keyword in keywords):
                return IntentResult(
                    intent=intent,
                    confidence=0.96,
                    route="rule_engine",
                    reason=f"命中关键词：{keywords}",
                )
        return IntentResult(intent="unknown", confidence=0.0, route="rule_engine", reason="未命中规则")


class SemanticIntentRecognizer:
    """
    第二层：语义匹配（中等复杂度）。
    设计说明：
    - 同样采用“策略模式（Strategy Pattern）”独立语义层能力；
    - 通过语义词簇加权匹配，处理“同义表达 / 口语化表达 / 不完整表达”。
    """

    _SEMANTIC_TERMS: dict[str, dict[str, float]] = {
        "leave": {"请假": 1.0, "休息": 0.7, "出勤": 0.6, "假条": 0.9, "离岗": 0.6},
        "reimburse": {"报销": 1.0, "垫付": 0.8, "发票": 0.9, "打款": 0.6, "成本": 0.6},
        "workflow": {"流程": 0.9, "审批": 1.0, "节点": 0.7, "待办": 0.8, "签核": 0.8},
        "query": {"查询": 1.0, "统计": 0.9, "分析": 0.6, "报表": 0.9, "趋势": 0.6},
        "knowledge": {"制度": 1.0, "政策": 1.0, "规则": 0.8, "条款": 0.8, "指引": 0.7},
        "minutes": {"纪要": 1.0, "会议": 0.7, "总结": 0.7, "行动项": 0.8, "决议": 0.8},
    }
    _PASS_THRESHOLD = 0.45

    def detect(self, message: str) -> IntentResult:
        msg = message.lower()
        best_intent = "unknown"
        best_score = 0.0
        matched_terms: list[str] = []

        for intent, terms in self._SEMANTIC_TERMS.items():
            hit_score = 0.0
            current_matches: list[str] = []
            for term, weight in terms.items():
                if term in msg or term in message:
                    hit_score += weight
                    current_matches.append(term)
            if hit_score > best_score:
                best_score = hit_score
                best_intent = intent
                matched_terms = current_matches

        confidence = min(best_score / 2.2, 0.9)
        if confidence >= self._PASS_THRESHOLD:
            return IntentResult(
                intent=best_intent,
                confidence=confidence,
                route="semantic_matching",
                reason=f"语义词命中：{matched_terms}",
            )
        return IntentResult(
            intent="unknown",
            confidence=confidence,
            route="semantic_matching",
            reason="语义分不足，进入 LLM 兜底",
        )


class LLMFunctionCallingIntentRecognizer:
    """
    第三层：LLM Function Calling（复杂场景兜底）。
    设计说明：
    - 使用“适配器模式（Adapter Pattern）”封装 LangChain + OpenAI 的结构化调用细节；
    - 将提示词组织交由 PromptEngineeringService，做到“模板集中管理、业务变量动态注入”。
    """

    def __init__(self, llm, prompt_service: PromptEngineeringService) -> None:
        self._llm = llm
        self._prompt_service = prompt_service
        self._logger = AppLogger(self.__class__.__name__)

    def detect(self, message: str) -> IntentResult:
        if self._llm is None:
            return IntentResult(
                intent="unknown",
                confidence=0.0,
                route="llm_function_calling",
                reason="未配置 LLM",
            )

        try:
            # method="function_calling" 显式启用函数调用风格的结构化输出。
            fc_model = self._llm.with_structured_output(_IntentDecision, method="function_calling")
            prompt = self._prompt_service.build_intent_routing_prompt(message=message)
            decision = fc_model.invoke(prompt)
            return IntentResult(
                intent=decision.intent,
                confidence=decision.confidence,
                route="llm_function_calling",
                reason=decision.reason,
            )
        except Exception as exc:
            self._logger.error("detect", "LLM Function Calling 失败", error=str(exc))
            return IntentResult(
                intent="unknown",
                confidence=0.0,
                route="llm_function_calling",
                reason="LLM 兜底失败",
            )


class IntentStrategy:
    """
    意图路由总入口。
    设计说明：
    - 采用“责任链模式（Chain of Responsibility）”编排三层识别器；
    - 层级顺序固定：规则引擎 -> 语义匹配 -> LLM Function Calling。
    """

    def __init__(self, llm=None) -> None:
        self._logger = AppLogger(self.__class__.__name__)
        self._prompt_service = PromptEngineeringService()
        self._rule_recognizer = RuleEngineIntentRecognizer()
        self._semantic_recognizer = SemanticIntentRecognizer()
        self._llm_recognizer = LLMFunctionCallingIntentRecognizer(llm=llm, prompt_service=self._prompt_service)

    def detect(self, message: str) -> IntentResult:
        # 第一层：规则引擎快速路径
        rule_result = self._rule_recognizer.detect(message)
        if rule_result.intent != "unknown":
            self._logger.info(
                "detect",
                "规则引擎命中",
                route=rule_result.route,
                intent=rule_result.intent,
                confidence=rule_result.confidence,
            )
            return rule_result

        # 第二层：语义匹配
        semantic_result = self._semantic_recognizer.detect(message)
        if semantic_result.intent != "unknown":
            self._logger.info(
                "detect",
                "语义匹配命中",
                route=semantic_result.route,
                intent=semantic_result.intent,
                confidence=semantic_result.confidence,
            )
            return semantic_result

        # 第三层：LLM Function Calling 兜底
        llm_result = self._llm_recognizer.detect(message)
        if llm_result.intent != "unknown":
            self._logger.info(
                "detect",
                "LLM Function Calling 命中",
                route=llm_result.route,
                intent=llm_result.intent,
                confidence=llm_result.confidence,
            )
            return llm_result

        # 三层均未命中，返回 unknown，交由上层提示补充信息。
        return IntentResult(
            intent="unknown",
            confidence=0.0,
            route="none",
            reason="三层路由均未识别到明确意图",
        )
