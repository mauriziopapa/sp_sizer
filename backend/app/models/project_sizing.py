from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ProjectSizing(Base, TimestampMixin):
    __tablename__ = "project_sizings"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_name: Mapped[str] = mapped_column(String(300), nullable=False)
    client_name: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    compiled_by: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    validated_by: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    sizing_date: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    responses: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    notes: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    section_scores: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    total_raw_score: Mapped[int] = mapped_column(Integer, nullable=False)
    total_max_score: Mapped[int] = mapped_column(Integer, nullable=False)
    normalized_score: Mapped[int] = mapped_column(Integer, nullable=False)
    resulting_size: Mapped[str] = mapped_column(String(50), nullable=False)
    completeness: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    triggered_risk_flags: Mapped[Optional[list[Any]]] = mapped_column(
        JSONB, nullable=True
    )
    status: Mapped[str] = mapped_column(String(50), default="DRAFT")
