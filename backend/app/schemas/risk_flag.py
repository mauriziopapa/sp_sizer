from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class RiskFlagBase(BaseModel):
    code: str
    label: str
    description: str
    condition_logic: Optional[dict[str, Any]] = None
    severity: str = "WARNING"
    display_order: int = 0


class RiskFlagCreate(RiskFlagBase):
    pass


class RiskFlagUpdate(BaseModel):
    code: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    condition_logic: Optional[dict[str, Any]] = None
    severity: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class RiskFlagResponse(RiskFlagBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
