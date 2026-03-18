from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.sizer_section import SizerSection
from app.models.user import User
from app.schemas.section import SectionCreate, SectionUpdate, SectionResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/sections", tags=["sections"])


@router.get("", response_model=list[SectionResponse])
async def list_sections(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SizerSection)
        .where(SizerSection.is_active == True)
        .options(selectinload(SizerSection.factors))
        .order_by(SizerSection.display_order)
    )
    return result.scalars().all()


@router.post("", response_model=SectionResponse, status_code=status.HTTP_201_CREATED)
async def create_section(
    data: SectionCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    section = SizerSection(**data.model_dump())
    db.add(section)
    await db.commit()
    await db.refresh(section)
    return section


@router.put("/{section_id}", response_model=SectionResponse)
async def update_section(
    section_id: int,
    data: SectionUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(SizerSection).where(SizerSection.id == section_id))
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=404, detail="Sezione non trovata")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(section, key, value)
    await db.commit()
    await db.refresh(section)
    return section


@router.delete("/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_section(
    section_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(SizerSection).where(SizerSection.id == section_id))
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=404, detail="Sezione non trovata")
    section.is_active = False
    await db.commit()
