from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class FactorBase(BaseModel):
    section_id: int
    code: str
    name: str
    question: str
    weight: int = Field(ge=1, le=10)
    min_score: int = 1
    max_score: int = 5
    score_labels: Optional[dict[str, Any]] = None
    sub_area: Optional[str] = None
    owner_role: Optional[str] = None
    display_order: int = 0


class FactorCreate(FactorBase):
    pass


class FactorUpdate(BaseModel):
    section_id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None
    question: Optional[str] = None
    weight: Optional[int] = Field(default=None, ge=1, le=10)
    min_score: Optional[int] = None
    max_score: Optional[int] = None
    score_labels: Optional[dict[str, Any]] = None
    sub_area: Optional[str] = None
    owner_role: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class FactorReorder(BaseModel):
    display_order: int


class FactorResponse(FactorBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
