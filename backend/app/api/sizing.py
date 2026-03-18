from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.sizer_section import SizerSection
from app.models.sizer_factor import SizerFactor
from app.models.score_range import ScoreRange
from app.models.governance_rule import GovernanceRule
from app.models.risk_flag import RiskFlag
from app.models.project_sizing import ProjectSizing
from app.models.user import User
from app.schemas.sizing import (
    SizingCreate, SizingUpdate, SizingResponse, SizingResultResponse, SizingListResponse,
)
from app.services.scoring import (
    calculate_section_scores, calculate_normalized_score,
    determine_size, calculate_completeness, evaluate_risk_flags,
)
from app.services.pdf import generate_sizing_pdf
from app.api.deps import get_current_user

router = APIRouter(prefix="/sizings", tags=["sizings"])


async def _compute_sizing(db: AsyncSession, responses: dict[str, int]):
    """Compute all scoring data from responses."""
    # Load factors
    factors_result = await db.execute(
        select(SizerFactor).where(SizerFactor.is_active == True)
    )
    factors = factors_result.scalars().all()

    # Load sections map
    sections_result = await db.execute(
        select(SizerSection).where(SizerSection.is_active == True)
    )
    sections = sections_result.scalars().all()
    sections_map = {s.id: s.code for s in sections}

    # Load score ranges
    ranges_result = await db.execute(
        select(ScoreRange).where(ScoreRange.is_active == True)
    )
    score_ranges = ranges_result.scalars().all()

    # Load risk flags
    flags_result = await db.execute(
        select(RiskFlag).where(RiskFlag.is_active == True)
    )
    risk_flags = flags_result.scalars().all()

    # Calculate
    section_scores = calculate_section_scores(responses, factors, sections_map)
    normalized_score = calculate_normalized_score(section_scores)
    size_range = determine_size(normalized_score, score_ranges)
    completeness = calculate_completeness(responses, factors, sections_map)
    triggered_flags = evaluate_risk_flags(responses, risk_flags)

    resulting_size = size_range.size_code if size_range else "UNKNOWN"
    total_raw = sum(s["raw"] for s in section_scores.values())
    total_max = sum(s["max"] for s in section_scores.values())

    return {
        "section_scores": section_scores,
        "total_raw_score": total_raw,
        "total_max_score": total_max,
        "normalized_score": normalized_score,
        "resulting_size": resulting_size,
        "completeness": completeness,
        "triggered_risk_flags": [f["code"] for f in triggered_flags],
        "triggered_risk_flags_detail": triggered_flags,
        "size_range": size_range,
    }


async def _get_governance_for_size(db: AsyncSession, size_code: str):
    """Get governance rules for a specific size."""
    range_result = await db.execute(
        select(ScoreRange).where(ScoreRange.size_code == size_code)
    )
    sr = range_result.scalar_one_or_none()
    if not sr:
        return []
    rules_result = await db.execute(
        select(GovernanceRule)
        .where(GovernanceRule.score_range_id == sr.id, GovernanceRule.is_active == True)
        .order_by(GovernanceRule.display_order)
    )
    return [
        {"element": r.element, "value": r.value}
        for r in rules_result.scalars().all()
    ]


@router.post("", response_model=SizingResultResponse, status_code=status.HTTP_201_CREATED)
async def create_sizing(
    data: SizingCreate,
    db: AsyncSession = Depends(get_db),
):
    computed = await _compute_sizing(db, data.responses)
    governance = await _get_governance_for_size(db, computed["resulting_size"])

    sizing = ProjectSizing(
        project_name=data.project_name,
        client_name=data.client_name,
        compiled_by=data.compiled_by,
        validated_by=data.validated_by,
        responses=data.responses,
        notes=data.notes,
        section_scores=computed["section_scores"],
        total_raw_score=computed["total_raw_score"],
        total_max_score=computed["total_max_score"],
        normalized_score=computed["normalized_score"],
        resulting_size=computed["resulting_size"],
        completeness=computed["completeness"],
        triggered_risk_flags=computed["triggered_risk_flags"],
    )
    db.add(sizing)
    await db.commit()
    await db.refresh(sizing)

    result = SizingResultResponse.model_validate(sizing)
    result.governance_rules = governance
    result.triggered_risk_flags_detail = computed["triggered_risk_flags_detail"]
    return result


@router.get("", response_model=list[SizingListResponse])
async def list_sizings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProjectSizing).order_by(ProjectSizing.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{sizing_id}", response_model=SizingResultResponse)
async def get_sizing(sizing_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProjectSizing).where(ProjectSizing.id == sizing_id)
    )
    sizing = result.scalar_one_or_none()
    if not sizing:
        raise HTTPException(status_code=404, detail="Sizing non trovato")

    governance = await _get_governance_for_size(db, sizing.resulting_size)

    # Re-evaluate risk flags for detail
    flags_result = await db.execute(
        select(RiskFlag).where(RiskFlag.is_active == True)
    )
    risk_flags = flags_result.scalars().all()
    triggered_detail = evaluate_risk_flags(sizing.responses, risk_flags)

    result_data = SizingResultResponse.model_validate(sizing)
    result_data.governance_rules = governance
    result_data.triggered_risk_flags_detail = triggered_detail
    return result_data


@router.put("/{sizing_id}", response_model=SizingResultResponse)
async def update_sizing(
    sizing_id: int,
    data: SizingUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ProjectSizing).where(ProjectSizing.id == sizing_id)
    )
    sizing = result.scalar_one_or_none()
    if not sizing:
        raise HTTPException(status_code=404, detail="Sizing non trovato")
    if sizing.status == "COMPLETED":
        raise HTTPException(status_code=400, detail="Sizing già completato, non modificabile")

    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(sizing, key, value)

    # Recalculate if responses changed
    responses = updates.get("responses", sizing.responses)
    computed = await _compute_sizing(db, responses)
    sizing.section_scores = computed["section_scores"]
    sizing.total_raw_score = computed["total_raw_score"]
    sizing.total_max_score = computed["total_max_score"]
    sizing.normalized_score = computed["normalized_score"]
    sizing.resulting_size = computed["resulting_size"]
    sizing.completeness = computed["completeness"]
    sizing.triggered_risk_flags = computed["triggered_risk_flags"]

    await db.commit()
    await db.refresh(sizing)

    governance = await _get_governance_for_size(db, sizing.resulting_size)
    result_data = SizingResultResponse.model_validate(sizing)
    result_data.governance_rules = governance
    result_data.triggered_risk_flags_detail = computed["triggered_risk_flags_detail"]
    return result_data


@router.patch("/{sizing_id}/complete", response_model=SizingResponse)
async def complete_sizing(
    sizing_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ProjectSizing).where(ProjectSizing.id == sizing_id)
    )
    sizing = result.scalar_one_or_none()
    if not sizing:
        raise HTTPException(status_code=404, detail="Sizing non trovato")

    # Check completeness >= 75%
    global_completeness = sizing.completeness.get("global", 0)
    if global_completeness < 0.75:
        raise HTTPException(
            status_code=400,
            detail=f"Completezza insufficiente ({global_completeness:.0%}). Minimo richiesto: 75%",
        )

    sizing.status = "COMPLETED"
    await db.commit()
    await db.refresh(sizing)
    return sizing


@router.get("/{sizing_id}/export/pdf")
async def export_sizing_pdf(sizing_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProjectSizing).where(ProjectSizing.id == sizing_id)
    )
    sizing = result.scalar_one_or_none()
    if not sizing:
        raise HTTPException(status_code=404, detail="Sizing non trovato")

    governance = await _get_governance_for_size(db, sizing.resulting_size)
    flags_result = await db.execute(
        select(RiskFlag).where(RiskFlag.is_active == True)
    )
    risk_flags = flags_result.scalars().all()
    triggered_detail = evaluate_risk_flags(sizing.responses, risk_flags)

    pdf_data = {
        "project_name": sizing.project_name,
        "client_name": sizing.client_name,
        "compiled_by": sizing.compiled_by,
        "validated_by": sizing.validated_by,
        "sizing_date": sizing.sizing_date.strftime("%Y-%m-%d"),
        "section_scores": sizing.section_scores,
        "total_raw_score": sizing.total_raw_score,
        "total_max_score": sizing.total_max_score,
        "normalized_score": sizing.normalized_score,
        "resulting_size": sizing.resulting_size,
        "status": sizing.status,
        "governance_rules": governance,
        "triggered_risk_flags_detail": triggered_detail,
    }

    pdf_bytes = generate_sizing_pdf(pdf_data)
    filename = f"sizing_{sizing.project_name.replace(' ', '_')}_{sizing.id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
