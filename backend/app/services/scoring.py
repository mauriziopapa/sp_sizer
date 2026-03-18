"""Core scoring engine for the SOLID PROJECT Sizer."""

import operator
from typing import Any

from app.models.sizer_factor import SizerFactor
from app.models.score_range import ScoreRange
from app.models.risk_flag import RiskFlag

OPERATORS = {
    ">=": operator.ge,
    "<=": operator.le,
    ">": operator.gt,
    "<": operator.lt,
    "==": operator.eq,
    "!=": operator.ne,
}


def calculate_section_scores(
    responses: dict[str, int],
    factors: list[SizerFactor],
    sections_map: dict[int, str],
) -> dict[str, dict[str, int]]:
    """Calculate raw and max scores per section.

    Returns: {"BUSINESS": {"raw": 93, "max": 155}, "TECNICO": {"raw": 103, "max": 120}}
    """
    section_scores: dict[str, dict[str, int]] = {}

    for factor in factors:
        if not factor.is_active:
            continue
        section_code = sections_map.get(factor.section_id, "UNKNOWN")
        if section_code not in section_scores:
            section_scores[section_code] = {"raw": 0, "max": 0}

        max_contribution = factor.weight * factor.max_score
        section_scores[section_code]["max"] += max_contribution

        user_score = responses.get(factor.code)
        if user_score is not None:
            weighted = user_score * factor.weight
            section_scores[section_code]["raw"] += weighted

    return section_scores


def calculate_normalized_score(section_scores: dict[str, dict[str, int]]) -> int:
    """Calculate normalized 0-100 score from section scores."""
    total_raw = sum(s["raw"] for s in section_scores.values())
    total_max = sum(s["max"] for s in section_scores.values())
    if total_max == 0:
        return 0
    return round((total_raw / total_max) * 100)


def determine_size(
    normalized_score: int, score_ranges: list[ScoreRange]
) -> ScoreRange | None:
    """Find the matching score range for a normalized score."""
    for sr in sorted(score_ranges, key=lambda x: x.min_score):
        if not sr.is_active:
            continue
        if sr.min_score <= normalized_score <= sr.max_score:
            return sr
    return None


def calculate_completeness(
    responses: dict[str, int],
    factors: list[SizerFactor],
    sections_map: dict[int, str],
) -> dict[str, float]:
    """Calculate completeness per section and global.

    Returns: {"BUSINESS": 1.0, "TECNICO": 0.75, "global": 0.875}
    """
    section_totals: dict[str, int] = {}
    section_filled: dict[str, int] = {}

    for factor in factors:
        if not factor.is_active:
            continue
        section_code = sections_map.get(factor.section_id, "UNKNOWN")
        section_totals[section_code] = section_totals.get(section_code, 0) + 1
        if factor.code in responses and responses[factor.code] is not None:
            section_filled[section_code] = section_filled.get(section_code, 0) + 1

    completeness: dict[str, float] = {}
    total_factors = 0
    total_filled = 0
    for code, total in section_totals.items():
        filled = section_filled.get(code, 0)
        completeness[code] = round(filled / total, 4) if total > 0 else 0.0
        total_factors += total
        total_filled += filled

    completeness["global"] = (
        round(total_filled / total_factors, 4) if total_factors > 0 else 0.0
    )
    return completeness


def evaluate_risk_flags(
    responses: dict[str, int], risk_flags: list[RiskFlag]
) -> list[dict[str, Any]]:
    """Evaluate risk flag conditions against user responses.

    Returns list of triggered flags with their details.
    """
    triggered = []

    for flag in risk_flags:
        if not flag.is_active:
            continue
        if not flag.condition_logic:
            continue

        conditions = flag.condition_logic.get("factors", [])
        logic = flag.condition_logic.get("logic", "AND")

        results = []
        for cond in conditions:
            factor_code = cond.get("code")
            op_str = cond.get("operator", ">=")
            threshold = cond.get("value", 0)

            user_value = responses.get(factor_code)
            if user_value is None:
                results.append(False)
                continue

            op_func = OPERATORS.get(op_str, operator.ge)
            results.append(op_func(user_value, threshold))

        if not results:
            continue

        is_triggered = all(results) if logic == "AND" else any(results)
        if is_triggered:
            triggered.append({
                "code": flag.code,
                "label": flag.label,
                "description": flag.description,
                "severity": flag.severity,
            })

    return triggered
