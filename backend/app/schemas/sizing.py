from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class SizingCreate(BaseModel):
    project_name: str
    client_name: Optional[str] = None
    compiled_by: Optional[str] = None
    validated_by: Optional[str] = None
    responses: dict[str, int]
    notes: Optional[dict[str, str]] = None


class SizingUpdate(BaseModel):
    project_name: Optional[str] = None
    client_name: Optional[str] = None
    compiled_by: Optional[str] = None
    validated_by: Optional[str] = None
    responses: Optional[dict[str, int]] = None
    notes: Optional[dict[str, str]] = None


class SizingResponse(BaseModel):
    id: int
    project_name: str
    client_name: Optional[str] = None
    compiled_by: Optional[str] = None
    validated_by: Optional[str] = None
    sizing_date: datetime
    responses: dict[str, Any]
    notes: Optional[dict[str, Any]] = None
    section_scores: dict[str, Any]
    total_raw_score: int
    total_max_score: int
    normalized_score: int
    resulting_size: str
    completeness: dict[str, Any]
    triggered_risk_flags: Optional[list[Any]] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SizingResultResponse(SizingResponse):
    """Extended response with governance rules and risk flag details."""
    governance_rules: list[dict[str, Any]] = []
    triggered_risk_flags_detail: list[dict[str, Any]] = []


class SizingListResponse(BaseModel):
    id: int
    project_name: str
    client_name: Optional[str] = None
    compiled_by: Optional[str] = None
    sizing_date: datetime
    normalized_score: int
    resulting_size: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
