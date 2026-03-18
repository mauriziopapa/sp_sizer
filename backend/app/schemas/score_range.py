from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ScoreRangeBase(BaseModel):
    size_code: str
    size_label: str
    min_score: int
    max_score: int
    color: Optional[str] = None
    emoji: Optional[str] = None
    description: Optional[str] = None
    display_order: int = 0


class ScoreRangeCreate(ScoreRangeBase):
    pass


class ScoreRangeUpdate(BaseModel):
    size_code: Optional[str] = None
    size_label: Optional[str] = None
    min_score: Optional[int] = None
    max_score: Optional[int] = None
    color: Optional[str] = None
    emoji: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class ScoreRangeResponse(ScoreRangeBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
