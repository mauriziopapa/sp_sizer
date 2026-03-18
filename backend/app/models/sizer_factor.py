from typing import Any, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class SizerFactor(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "sizer_factors"

    id: Mapped[int] = mapped_column(primary_key=True)
    section_id: Mapped[int] = mapped_column(
        ForeignKey("sizer_sections.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    weight: Mapped[int] = mapped_column(
        Integer, nullable=False,
        info={"check": CheckConstraint("weight >= 1 AND weight <= 10")}
    )
    min_score: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    score_labels: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    sub_area: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    owner_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    section: Mapped["SizerSection"] = relationship(
        "SizerSection", back_populates="factors"
    )

    __table_args__ = (
        CheckConstraint("weight >= 1 AND weight <= 10", name="ck_factor_weight"),
    )
