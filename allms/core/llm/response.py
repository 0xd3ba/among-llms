from __future__ import annotations

from pydantic import BaseModel, field_validator, model_validator
from typing import Any, ClassVar, Dict, Optional, Set


class _AllowedIDsMixin(BaseModel):
    allowed_ids: ClassVar[Set[str]] = set()  # Run-time set of allowed agent IDs

    @classmethod
    def validate_agent_id(cls, agent_id: str) -> str:
        if cls.allowed_ids and agent_id in cls.allowed_ids:
            return agent_id
        raise ValueError(f"Agent ID ({agent_id}) not in the allowed set: {cls.allowed_ids}")


class LLMResponseModel(_AllowedIDsMixin):
    """ Class for defining structured responses from the LLM """
    message: str                              # The actual message to sent to the chat
    intent: str                               # The thought process behind the message
    send_to: Optional[str] = None             # Send to all (None) or a specific agent (will need checking manually)
    suspect: Optional[str] = None             # The current suspect (None if no one)
    suspect_confidence: Optional[int] = None  # Current confidence on the suspect (ignored if no suspect)
    suspect_reason: Optional[str] = None      # The reason for the suspicion
    start_a_vote: bool = False                # True if agent wants to start a vote, else False
    voting_for: Optional[str] = None          # If a vote has started, who is the current LLM voting for ?

    @field_validator("send_to")
    def check_send_to_id(cls, agent_id: Optional[str]) -> Optional[str]:
        """ Validator for send-to ID to ensure it is within the allowed set """
        if agent_id is not None:
            return cls.validate_agent_id(agent_id)
        return agent_id

    @field_validator("voting_for")
    def check_voting_for(cls, agent_id: str) -> Optional[str]:
        if agent_id is not None:
            return cls.validate_agent_id(agent_id)
        return agent_id

    @model_validator(mode="after")
    def check_for_vote(cls, model: LLMResponseModel) -> LLMResponseModel:
        if model.start_a_vote and (model.voting_for is None):
            raise ValueError("start_a_vote=True but didn't vote for any agent (voting_for=None)")
        return model
