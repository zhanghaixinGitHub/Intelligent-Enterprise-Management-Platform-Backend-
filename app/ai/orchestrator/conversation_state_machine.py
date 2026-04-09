from dataclasses import dataclass


@dataclass
class ConversationState:
    state: str = "collecting"
    missing_fields: list[str] | None = None


class ConversationStateMachine:
    def transit(self, current_state: str, has_missing_fields: bool, execution_ok: bool) -> ConversationState:
        if current_state == "collecting" and has_missing_fields:
            return ConversationState("collecting", ["date", "type"])
        if current_state == "collecting" and not has_missing_fields:
            return ConversationState("confirming", [])
        if current_state == "confirming" and execution_ok:
            return ConversationState("completed", [])
        if current_state == "confirming" and not execution_ok:
            return ConversationState("failed", [])
        return ConversationState("collecting", [])
