"""Generación de la ficha PDF de la demo pública."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)


INK = colors.HexColor("#172A3A")
TEAL = colors.HexColor("#237C7B")
MINT = colors.HexColor("#E6F2EF")
CORAL = colors.HexColor("#E77B62")
SAND = colors.HexColor("#F6F2EA")
SLATE = colors.HexColor("#506273")
LINE = colors.HexColor("#D8E0E1")
LOGO_PATH = Path(__file__).parent / "assets" / "lyvira-logo-transparent.png"


def _text(value: object) -> str:
    """Escapa texto para usarlo dentro de Paragraph sin interpretar HTML."""
    text = str(value).replace("Piloto", "Agente").replace("piloto", "agente")
    return escape(text).replace("\n", "<br/>")


def _bullet_items(items: list[str], style: ParagraphStyle) -> list[Paragraph]:
    return [Paragraph(f"- {_text(item)}", style) for item in items]


def _footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(SLATE)
    canvas.drawString(18 * mm, 9 * mm, "LYVIRA - Diagnóstico express de procesos")
    website = "lyvira.com"
    website_x = 155 * mm
    canvas.setFillColor(TEAL)
    canvas.drawString(website_x, 9 * mm, website)
    canvas.linkURL("https://lyvira.com", (website_x, 8 * mm, website_x + canvas.stringWidth(website, "Helvetica", 8), 12 * mm), relative=0)
    canvas.setFillColor(SLATE)
    canvas.drawRightString(192 * mm, 9 * mm, f"Página {document.page}")
    canvas.restoreState()


def build_result_pdf(result: dict) -> bytes:
    """Construye una ficha PDF lista para previsualizar o descargar."""
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=13 * mm,
        bottomMargin=18 * mm,
        title="LYVIRA · Diagnóstico express de procesos",
        author="LYVIRA",
    )

    base = getSampleStyleSheet()
    styles = {
        "brand": ParagraphStyle("Brand", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=TEAL, alignment=TA_LEFT, spaceAfter=4),
        "title": ParagraphStyle("Title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=21, leading=24, textColor=INK, alignment=TA_LEFT, spaceAfter=3),
        "subtitle": ParagraphStyle("Subtitle", parent=base["Normal"], fontSize=9.5, leading=12, textColor=SLATE, spaceAfter=8),
        "section": ParagraphStyle("Section", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=12.5, leading=15, textColor=INK, spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontSize=8.7, leading=11.5, textColor=INK, spaceAfter=3),
        "small": ParagraphStyle("Small", parent=base["BodyText"], fontSize=8, leading=10, textColor=SLATE, spaceAfter=3),
        "card_title": ParagraphStyle("CardTitle", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=8.5, leading=10.5, textColor=TEAL, spaceAfter=2),
        "card_value": ParagraphStyle("CardValue", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=10, leading=12, textColor=INK),
        "bullet": ParagraphStyle("Bullet", parent=base["BodyText"], fontSize=8.3, leading=10.5, leftIndent=8, firstLineIndent=-7, textColor=INK, spaceAfter=2),
        "score": ParagraphStyle("Score", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=INK, alignment=TA_CENTER),
    }

    area_analysis = result.get("area_analysis") or {}
    facts = area_analysis.get("context_facts", {})
    story = []
    if LOGO_PATH.exists():
        logo_reader = ImageReader(str(LOGO_PATH))
        logo_width = 34 * mm
        source_width, source_height = logo_reader.getSize()
        logo_height = logo_width * source_height / source_width
        logo = Image(str(LOGO_PATH), width=logo_width, height=logo_height, hAlign="LEFT")
        story.extend([logo, Spacer(1, 1 * mm)])
    story.extend([
        Paragraph("LYVIRA · laboratorio de IA aplicada", styles["brand"]),
        Paragraph("LYVIRA · Diagnóstico express de procesos", styles["title"]),
        Paragraph("Ficha de orientación educativa para elegir un primer agente de mejora.", styles["subtitle"]),
        HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=10),
        Table(
            [[
                Paragraph("PROCESO", styles["card_title"]),
                Paragraph("ÁREA", styles["card_title"]),
                Paragraph("RESULTADO", styles["card_title"]),
            ], [
                Paragraph(_text(result.get("process", "")), styles["card_value"]),
                Paragraph(_text(result.get("area", "")), styles["card_value"]),
                Paragraph(_text(result.get("readiness_label", "")), styles["card_value"]),
            ]],
            colWidths=[67 * mm, 47 * mm, 60 * mm],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), MINT),
                ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]),
        ),
        Spacer(1, 8),
        Table([[Paragraph(f"{result.get('score', 0)}/30", styles["score"]), Paragraph(_text(result.get("explanation", "")), styles["body"])]], colWidths=[34 * mm, 140 * mm], style=TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), SAND),
            ("BACKGROUND", (1, 0), (1, 0), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.7, LINE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ])),
        Paragraph("Objetivo declarado", styles["section"]),
        Paragraph(_text(result.get("goal_focus") or "No se indicó un objetivo concreto."), styles["body"]),
        Paragraph("Qué haría primero", styles["section"]),
        Paragraph(_text(result.get("next_step", "")), styles["body"]),
        Paragraph("Papel recomendado para la IA", styles["section"]),
        Paragraph(_text(result.get("ai_role", "")), styles["body"]),
        Paragraph("Qué conviene tener en cuenta", styles["section"]),
    ])
    story.extend(_bullet_items(result.get("blockers", []), styles["bullet"]))

    if facts:
        story.append(Paragraph(f"Lectura específica de { _text(result.get('area', '')) }", styles["section"]))
        fact_rows = [[Paragraph(_text(label), styles["card_title"]), Paragraph(_text(value), styles["body"])] for label, value in facts.items()]
        story.append(Table(fact_rows, colWidths=[55 * mm, 119 * mm], style=TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), MINT),
            ("BOX", (0, 0), (-1, -1), 0.7, LINE),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])))

    story.extend([
        Paragraph("Agente sugerido", styles["section"]),
    ])
    story.extend(_bullet_items(area_analysis.get("pilot", []), styles["bullet"]))
    metrics = area_analysis.get("metrics", [])
    if metrics:
        story.append(Paragraph(f"<b>Métricas:</b> {_text(' · '.join(metrics))}", styles["body"]))
    control_block = [Paragraph("Controles que deberían mantenerse", styles["section"])]
    controls = area_analysis.get("controls", [])
    if controls:
        control_cells = []
        for index in range(0, len(controls), 2):
            row = [Paragraph(f"- {_text(item)}", styles["bullet"]) for item in controls[index:index + 2]]
            if len(row) == 1:
                row.append(Paragraph("", styles["bullet"]))
            control_cells.append(row)
        control_block.append(Table(control_cells, colWidths=[87 * mm, 87 * mm], style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), SAND),
            ("BOX", (0, 0), (-1, -1), 0.7, LINE),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])))
    story.append(KeepTogether(control_block))
    story.extend([
        Spacer(1, 8),
        HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=7),
        Paragraph(_text(result.get("disclaimer", "Orientación educativa basada en tus respuestas.")), styles["small"]),
    ])

    document.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buffer.getvalue()
