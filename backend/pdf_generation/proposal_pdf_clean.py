from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from schemas import ProposalRequest


PRIMARY = colors.HexColor("#2563EB")
DARK_TEXT = colors.HexColor("#111827")
SECONDARY_TEXT = colors.HexColor("#6B7280")
LIGHT_BACKGROUND = colors.HexColor("#F9FAFB")
TABLE_HEADER = colors.HexColor("#E5E7EB")
HIGHLIGHT_BOX = colors.HexColor("#DBEAFE")
BORDER = colors.HexColor("#E5E7EB")
WHITE = colors.white


def format_inr(value: float) -> str:
    rounded = int(round(value))
    raw = str(rounded)
    if len(raw) <= 3:
        return f"Rs. {raw}"

    last_three = raw[-3:]
    remaining = raw[:-3]
    chunks: list[str] = []
    while len(remaining) > 2:
        chunks.insert(0, remaining[-2:])
        remaining = remaining[:-2]
    if remaining:
        chunks.insert(0, remaining)
    return f"Rs. {','.join(chunks + [last_three])}"


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ProposalTitle", fontName="Helvetica-Bold", fontSize=22, leading=28, textColor=DARK_TEXT, spaceAfter=6))
    styles.add(ParagraphStyle(name="SectionTitleBlue", fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=PRIMARY, spaceAfter=6))
    styles.add(ParagraphStyle(name="ProposalBodyText", fontName="Helvetica", fontSize=9.7, leading=15, textColor=DARK_TEXT))
    styles.add(ParagraphStyle(name="ProposalMutedText", fontName="Helvetica", fontSize=8.7, leading=13, textColor=SECONDARY_TEXT))
    styles.add(ParagraphStyle(name="StrongValue", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=DARK_TEXT))
    styles.add(ParagraphStyle(name="MetaLabel", fontName="Helvetica-Bold", fontSize=7.8, leading=10, textColor=SECONDARY_TEXT, uppercase=True))
    styles.add(ParagraphStyle(name="RightMuted", fontName="Helvetica", fontSize=8.5, leading=12, textColor=SECONDARY_TEXT, alignment=TA_RIGHT))
    return styles


def bullet_paragraphs(items: list[str], style: ParagraphStyle) -> list[Paragraph]:
    return [Paragraph(f"- {item}", style) for item in items]


def append_list_section(title: str, items: list[str], story: list, styles, style_name: str = "ProposalBodyText") -> None:
    story.append(Paragraph(title, styles["SectionTitleBlue"]))
    for row in bullet_paragraphs(items, styles[style_name]):
        story.append(row)
        story.append(Spacer(1, 3))
    story.append(Spacer(1, 10))


def build_meta_grid(values: list[tuple[str, str]], styles) -> Table:
    cards = []
    for label, value in values:
        cards.append(
            Table(
                [[Paragraph(label, styles["MetaLabel"])], [Paragraph(value, styles["StrongValue"])]],
                colWidths=[78 * mm],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), WHITE),
                        ("BOX", (0, 0), (-1, -1), 1, BORDER),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                ),
            )
        )

    rows = []
    for index in range(0, len(cards), 2):
        pair = cards[index : index + 2]
        if len(pair) == 1:
            pair.append("")
        rows.append(pair)

    return Table(
        rows,
        colWidths=[82 * mm, 82 * mm],
        style=TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        ),
    )


def build_pricing_table(payload: ProposalRequest, styles) -> tuple[Table, float, float, float]:
    rows = [["Item", "Quantity", "Unit Cost", "Total"]]
    subtotal = 0.0
    for item in payload.pricing:
        total = item.quantity * item.unit_cost
        subtotal += total
        rows.append(
            [
                Paragraph(item.item, styles["ProposalBodyText"]),
                Paragraph(str(item.quantity), styles["ProposalBodyText"]),
                Paragraph(format_inr(item.unit_cost), styles["RightMuted"]),
                Paragraph(format_inr(total), styles["RightMuted"]),
            ]
        )

    gst = subtotal * (payload.commercial_terms.gst_percent / 100)
    grand_total = subtotal + gst
    table = Table(rows, colWidths=[89 * mm, 20 * mm, 35 * mm, 35 * mm], repeatRows=1)
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), DARK_TEXT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("GRID", (0, 0), (-1, -1), 1, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("ALIGN", (1, 0), (-1, 0), "CENTER"),
    ]
    for row_index in range(1, len(rows)):
        if row_index % 2 == 0:
            commands.append(("BACKGROUND", (0, row_index), (-1, row_index), LIGHT_BACKGROUND))
    table.setStyle(TableStyle(commands))
    return table, subtotal, gst, grand_total


def build_summary_table(subtotal: float, gst: float, grand_total: float, gst_percent: float) -> Table:
    table = Table(
        [["Subtotal", format_inr(subtotal)], [f"GST ({gst_percent:.0f}%)", format_inr(gst)], ["Grand Total", format_inr(grand_total)]],
        colWidths=[38 * mm, 38 * mm],
        hAlign="RIGHT",
    )
    table.setStyle(
        TableStyle(
            [
                ("TEXTCOLOR", (0, 0), (-1, 1), DARK_TEXT),
                ("FONTNAME", (0, 0), (-1, 1), "Helvetica"),
                ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 2), (-1, 2), PRIMARY),
                ("FONTSIZE", (0, 0), (-1, 1), 9),
                ("FONTSIZE", (0, 2), (-1, 2), 12),
                ("LINEABOVE", (0, 0), (-1, 0), 1, BORDER),
                ("LINEBELOW", (0, 1), (-1, 1), 1, BORDER),
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def build_proposal_pdf(payload: ProposalRequest) -> bytes:
    styles = build_styles()
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm)

    logo = Table(
        [[Paragraph(payload.company.logo_text, ParagraphStyle(name="LogoStyle", fontName="Helvetica-Bold", fontSize=13, textColor=WHITE, alignment=1))]],
        colWidths=[14 * mm],
        rowHeights=[14 * mm],
        style=TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BOX", (0, 0), (-1, -1), 0, PRIMARY),
            ]
        ),
    )

    header = Table(
        [[logo, Paragraph(f"<b>{payload.company.name}</b><br/>{payload.company.tag_line}", styles["ProposalBodyText"]), Paragraph(payload.document.issue_date, styles["RightMuted"])]],
        colWidths=[18 * mm, 112 * mm, 32 * mm],
        style=TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        ),
    )

    objective_columns = Table(
        [[
            Table([[Paragraph("Business Objectives", styles["SectionTitleBlue"])]] + [[Paragraph(f"- {item}", styles["ProposalBodyText"])] for item in payload.business_objectives], colWidths=[84 * mm], style=TableStyle([("BOX", (0, 0), (-1, -1), 1, BORDER), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)])),
            Table([[Paragraph("Proposed Response", styles["SectionTitleBlue"])]] + [[Paragraph(f"- {item}", styles["ProposalBodyText"])] for item in payload.proposed_solution], colWidths=[84 * mm], style=TableStyle([("BOX", (0, 0), (-1, -1), 1, BORDER), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)])),
        ]],
        colWidths=[87 * mm, 87 * mm],
        style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]),
    )

    pricing_table, subtotal, gst, grand_total = build_pricing_table(payload, styles)
    summary_table = build_summary_table(subtotal, gst, grand_total, payload.commercial_terms.gst_percent)

    value_add_box = Table(
        [[Paragraph(payload.value_add_heading, styles["SectionTitleBlue"])]] + [[Paragraph(f"- {item}", styles["ProposalBodyText"])] for item in payload.value_add_points],
        colWidths=[174 * mm],
        style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), HIGHLIGHT_BOX), ("BOX", (0, 0), (-1, -1), 1, BORDER), ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]),
    )

    footer = Table(
        [[Paragraph(f"<b>{payload.company.name}</b><br/>{payload.company.email} | {payload.company.phone}<br/>{payload.company.address} | {payload.company.website}", styles["ProposalMutedText"]), Paragraph(f"<b>Authorized Signatory</b><br/>{payload.authorized_signatory}", styles["RightMuted"])]],
        colWidths=[120 * mm, 54 * mm],
        style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]),
    )

    story = [
        header,
        Spacer(1, 8),
        HRFlowable(width="100%", thickness=1.2, color=PRIMARY),
        Spacer(1, 10),
        Paragraph(payload.document.title, styles["SectionTitleBlue"]),
        Paragraph(payload.project_title, styles["ProposalTitle"]),
        Paragraph(f"{payload.client.company_name}<br/>{payload.client.contact_person}, {payload.client.designation}<br/>{payload.client.email}", styles["ProposalMutedText"]),
        Spacer(1, 10),
        build_meta_grid([("Proposal Reference", payload.document.reference), ("Prepared By", payload.document.prepared_by), ("Issue Date", payload.document.issue_date), ("Validity", payload.document.validity)], styles),
        Spacer(1, 4),
        Paragraph("Executive Summary", styles["SectionTitleBlue"]),
        Paragraph(payload.executive_summary, styles["ProposalBodyText"]),
        Spacer(1, 12),
        objective_columns,
        Spacer(1, 12),
    ]

    append_list_section("Scope of Work", payload.scope_of_work, story, styles)
    story.append(Paragraph("Commercial Proposal", styles["SectionTitleBlue"]))
    story.append(pricing_table)
    story.append(Spacer(1, 8))
    story.append(summary_table)
    story.append(Spacer(1, 12))
    story.append(value_add_box)
    story.append(Spacer(1, 12))
    append_list_section("Timeline and Milestones", payload.timeline, story, styles)
    append_list_section("Key Deliverables", payload.deliverables, story, styles)
    append_list_section("Payment Terms", payload.commercial_terms.payment_terms, story, styles)
    append_list_section("Terms and Conditions", payload.commercial_terms.terms_and_conditions, story, styles, style_name="ProposalMutedText")
    story.extend([Spacer(1, 14), HRFlowable(width="100%", thickness=1, color=BORDER), Spacer(1, 8), footer])

    document.build(story)
    return buffer.getvalue()
