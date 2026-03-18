from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.governance_rule import GovernanceRule
from app.models.score_range import ScoreRange
from app.models.user import User
from app.schemas.governance import GovernanceRuleCreate, GovernanceRuleUpdate, GovernanceRuleResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/governance-rules", tags=["governance"])


@router.get("", response_model=list[GovernanceRuleResponse])
async def list_governance_rules(
    size: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(GovernanceRule)
        .where(GovernanceRule.is_active == True)
        .order_by(GovernanceRule.display_order)
    )
    if size:
        subq = select(ScoreRange.id).where(ScoreRange.size_code == size)
        query = query.where(GovernanceRule.score_range_id.in_(subq))

    result = await db.execute(query)
    rules = result.scalars().all()

    # Enrich with size_code
    range_ids = {r.score_range_id for r in rules}
    if range_ids:
        sr_result = await db.execute(
            select(ScoreRange).where(ScoreRange.id.in_(range_ids))
        )
        sr_map = {sr.id: sr.size_code for sr in sr_result.scalars().all()}
    else:
        sr_map = {}

    response = []
    for rule in rules:
        data = GovernanceRuleResponse.model_validate(rule)
        data.size_code = sr_map.get(rule.score_range_id)
        response.append(data)
    return response


@router.post("", response_model=GovernanceRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_governance_rule(
    data: GovernanceRuleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    rule = GovernanceRule(**data.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.put("/{rule_id}", response_model=GovernanceRuleResponse)
async def update_governance_rule(
    rule_id: int,
    data: GovernanceRuleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(GovernanceRule).where(GovernanceRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Regola governance non trovata")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(rule, key, value)
    await db.commit()
    await db.refresh(rule)
    return rule
