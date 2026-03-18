"""PDF export service using ReportLab."""

import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable,
)


def generate_sizing_pdf(sizing_data: dict) -> bytes:
    """Generate a PDF report for a sizing result."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=20 * mm, bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"],
        fontSize=18, textColor=colors.HexColor("#0D2137"),
        spaceAfter=6 * mm,
    )
    heading_style = ParagraphStyle(
        "CustomHeading", parent=styles["Heading2"],
        fontSize=13, textColor=colors.HexColor("#2E75B6"),
        spaceBefore=6 * mm, spaceAfter=3 * mm,
    )
    normal_style = styles["Normal"]

    elements = []

    # Title
    elements.append(Paragraph("SOLID PROJECT Sizer — Risultato", title_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0")))
    elements.append(Spacer(1, 4 * mm))

    # Project info
    info_data = [
        ["Progetto:", sizing_data.get("project_name", "—")],
        ["Cliente:", sizing_data.get("client_name", "—")],
        ["Compilato da:", sizing_data.get("compiled_by", "—")],
        ["Validato da:", sizing_data.get("validated_by", "—")],
        ["Data:", str(sizing_data.get("sizing_date", "—"))],
    ]
    info_table = Table(info_data, colWidths=[40 * mm, 120 * mm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 6 * mm))

    # Score result
    elements.append(Paragraph("Risultato Sizing", heading_style))
    size = sizing_data.get("resulting_size", "—")
    normalized = sizing_data.get("normalized_score", 0)
    color_map = {"SMALL": "#22C55E", "PMI": "#F59E0B", "ENTERPRISE": "#EF4444"}
    size_color = color_map.get(size, "#64748B")

    score_data = [
        ["Score Normalizzato", f"{normalized} / 100"],
        ["Size Risultante", size],
        ["Status", sizing_data.get("status", "DRAFT")],
    ]
    score_table = Table(score_data, colWidths=[60 * mm, 100 * mm])
    score_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
        ("TEXTCOLOR", (1, 1), (1, 1), colors.HexColor(size_color)),
        ("FONTNAME", (1, 1), (1, 1), "Helvetica-Bold"),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 4 * mm))

    # Section scores
    elements.append(Paragraph("Punteggi per Sezione", heading_style))
    section_scores = sizing_data.get("section_scores", {})
    sec_header = ["Sezione", "Punteggio", "Massimo", "%"]
    sec_rows = [sec_header]
    for sec_code, scores in section_scores.items():
        raw = scores.get("raw", 0)
        max_s = scores.get("max", 1)
        pct = round((raw / max_s) * 100) if max_s > 0 else 0
        sec_rows.append([sec_code, str(raw), str(max_s), f"{pct}%"])

    sec_rows.append([
        "TOTALE",
        str(sizing_data.get("total_raw_score", 0)),
        str(sizing_data.get("total_max_score", 0)),
        f"{normalized}%",
    ])

    sec_table = Table(sec_rows, colWidths=[50 * mm, 30 * mm, 30 * mm, 30 * mm])
    sec_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D2137")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F7F8FA")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))
    elements.append(sec_table)
    elements.append(Spacer(1, 4 * mm))

    # Governance rules
    governance = sizing_data.get("governance_rules", [])
    if governance:
        elements.append(Paragraph("Governance Applicata", heading_style))
        gov_rows = [["Elemento", "Valore"]]
        for g in governance:
            gov_rows.append([g.get("element", ""), g.get("value", "")])
        gov_table = Table(gov_rows, colWidths=[60 * mm, 100 * mm])
        gov_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E75B6")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
        ]))
        elements.append(gov_table)
        elements.append(Spacer(1, 4 * mm))

    # Risk flags
    risk_flags = sizing_data.get("triggered_risk_flags_detail", [])
    if risk_flags:
        elements.append(Paragraph("Risk Flags Attivati", heading_style))
        risk_rows = [["Codice", "Flag", "Severità", "Descrizione"]]
        for rf in risk_flags:
            risk_rows.append([
                rf.get("code", ""),
                rf.get("label", ""),
                rf.get("severity", ""),
                rf.get("description", ""),
            ])
        risk_table = Table(risk_rows, colWidths=[20 * mm, 45 * mm, 25 * mm, 70 * mm])
        risk_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EF4444")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
        ]))
        elements.append(risk_table)

    # Footer
    elements.append(Spacer(1, 10 * mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0")))
    footer_style = ParagraphStyle(
        "Footer", parent=normal_style,
        fontSize=8, textColor=colors.HexColor("#94A3B8"),
        spaceBefore=2 * mm,
    )
    elements.append(Paragraph(
        "Generato da SOLID PROJECT Sizer — Studioware", footer_style
    ))

    doc.build(elements)
    return buffer.getvalue()
