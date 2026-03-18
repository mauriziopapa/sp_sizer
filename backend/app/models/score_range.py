from typing import Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class ScoreRange(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "score_ranges"

    id: Mapped[int] = mapped_column(primary_key=True)
    size_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    size_label: Mapped[str] = mapped_column(String(200), nullable=False)
    min_score: Mapped[int] = mapped_column(Integer, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    emoji: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
