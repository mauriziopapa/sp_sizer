from typing import Any, Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class RiskFlag(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "risk_flags"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    condition_logic: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )
    severity: Mapped[str] = mapped_column(String(20), default="WARNING")
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
