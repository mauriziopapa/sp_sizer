from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.sizer_factor import SizerFactor
from app.models.sizer_section import SizerSection
from app.models.user import User
from app.schemas.factor import FactorCreate, FactorUpdate, FactorReorder, FactorResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/factors", tags=["factors"])


@router.get("", response_model=list[FactorResponse])
async def list_factors(
    section: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(SizerFactor).where(SizerFactor.is_active == True)
    if section:
        subq = select(SizerSection.id).where(SizerSection.code == section)
        query = query.where(SizerFactor.section_id.in_(subq))
    query = query.order_by(SizerFactor.display_order)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=FactorResponse, status_code=status.HTTP_201_CREATED)
async def create_factor(
    data: FactorCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    factor = SizerFactor(**data.model_dump())
    db.add(factor)
    await db.commit()
    await db.refresh(factor)
    return factor


@router.put("/{factor_id}", response_model=FactorResponse)
async def update_factor(
    factor_id: int,
    data: FactorUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(SizerFactor).where(SizerFactor.id == factor_id))
    factor = result.scalar_one_or_none()
    if not factor:
        raise HTTPException(status_code=404, detail="Fattore non trovato")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(factor, key, value)
    await db.commit()
    await db.refresh(factor)
    return factor


@router.patch("/{factor_id}/reorder", response_model=FactorResponse)
async def reorder_factor(
    factor_id: int,
    data: FactorReorder,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(SizerFactor).where(SizerFactor.id == factor_id))
    factor = result.scalar_one_or_none()
    if not factor:
        raise HTTPException(status_code=404, detail="Fattore non trovato")
    factor.display_order = data.display_order
    await db.commit()
    await db.refresh(factor)
    return factor


@router.delete("/{factor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_factor(
    factor_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(SizerFactor).where(SizerFactor.id == factor_id))
    factor = result.scalar_one_or_none()
    if not factor:
        raise HTTPException(status_code=404, detail="Fattore non trovato")
    factor.is_active = False
    await db.commit()
