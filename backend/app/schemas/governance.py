from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GovernanceRuleBase(BaseModel):
    element: str
    score_range_id: int
    value: str
    display_order: int = 0


class GovernanceRuleCreate(GovernanceRuleBase):
    pass


class GovernanceRuleUpdate(BaseModel):
    element: Optional[str] = None
    score_range_id: Optional[int] = None
    value: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class GovernanceRuleResponse(GovernanceRuleBase):
    id: int
    is_active: bool
    size_code: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
