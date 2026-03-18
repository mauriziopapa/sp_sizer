from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class GovernanceRule(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "governance_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    element: Mapped[str] = mapped_column(String(200), nullable=False)
    score_range_id: Mapped[int] = mapped_column(
        ForeignKey("score_ranges.id"), nullable=False
    )
    value: Mapped[str] = mapped_column(Text, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    score_range: Mapped["ScoreRange"] = relationship("ScoreRange", lazy="selectin")
