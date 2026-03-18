from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.factor import FactorResponse


class SectionBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    owner_role: Optional[str] = None
    display_order: int = 0


class SectionCreate(SectionBase):
    pass


class SectionUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    owner_role: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class SectionResponse(SectionBase):
    id: int
    is_active: bool
    max_score_theoretical: Optional[int] = None
    factors: list[FactorResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SectionListResponse(SectionBase):
    id: int
    is_active: bool
    max_score_theoretical: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}
