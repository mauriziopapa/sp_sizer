from typing import List, Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class SizerSection(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "sizer_sections"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner_role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_score_theoretical: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    factors: Mapped[List["SizerFactor"]] = relationship(
        "SizerFactor", back_populates="section", lazy="selectin",
        order_by="SizerFactor.display_order"
    )
