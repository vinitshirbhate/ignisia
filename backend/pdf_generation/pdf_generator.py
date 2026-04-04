from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from schemas import ProposalRequest

# ── Palette: Deep Navy · Electric Teal · Warm Gold ───────────────────────────
#
#   PRIMARY          – electric teal  : headings, accents, logo badge, HR rules
#   DARK_TEXT        – crisp white    : body text on dark surfaces / near-black on light
#   SECONDARY_TEXT   – cool slate     : muted labels, footer, right-aligned small text
#   LIGHT_BACKGROUND – midnight tint  : alternating table rows (very subtle dark wash)
#   TABLE_HEADER     – deep navy      : pricing table header band
#   HIGHLIGHT_BOX    – teal wash      : value-add section background
#   BORDER           – steel line     : all borders / grid lines
#
PRIMARY           = colors.HexColor("#057A78")   # electric teal
DARK_TEXT         = colors.HexColor("#0F172A")   # deep navy (body text on white)
SECONDARY_TEXT    = colors.HexColor("#64748B")   # cool slate
LIGHT_BACKGROUND  = colors.HexColor("#F0FDFC")   # barely-teal white (alt rows)
TABLE_HEADER      = colors.HexColor("#02194E")   # deep navy header band
HIGHLIGHT_BOX     = colors.HexColor("#FFFFFF")   # soft teal wash
BORDER            = colors.HexColor("#CBD5E1")   # steel border
STAMP_PATH = Path(__file__).resolve().parent / "stamp.png"


def format_inr(value: float) -> str:
    rounded = int(round(value))
    raw = str(rounded)
    if len(raw) <= 3:
        return f"Rs. {raw}"
    last_three = raw[-3:]
    remaining = raw[:-3]
    parts: list[str] = []
    while len(remaining) > 2:
      parts.insert(0, remaining[-2:])
      remaining = remaining[:-2]
    if remaining:
      parts.insert(0, remaining)
    return f"Rs. {','.join(parts + [last_three])}"


def _styles():
    base = getSampleStyleSheet()
    base.add(
        ParagraphStyle(
            name="TitlePrimary",
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            textColor=DARK_TEXT,
            spaceAfter=6,
        )
    )
    base.add(
        ParagraphStyle(
            name="SectionTitlePrimary",
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=PRIMARY,
            spaceAfter=6,
        )
    )
    base.add(
        ParagraphStyle(
            name="BodyPrimary",
            fontName="Helvetica",
            fontSize=9.7,
            leading=15,
            textColor=DARK_TEXT,
        )
    )
    base.add(
        ParagraphStyle(
            name="BodyMuted",
            fontName="Helvetica",
            fontSize=8.7,
            leading=13,
            textColor=SECONDARY_TEXT,
        )
    )
    base.add(
        ParagraphStyle(
            name="LabelMuted",
            fontName="Helvetica-Bold",
            fontSize=7.8,
            leading=10,
            textColor=SECONDARY_TEXT,
            uppercase=True,
        )
    )
    base.add(
        ParagraphStyle(
            name="ValueStrong",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=DARK_TEXT,
        )
    )
    base.add(
        ParagraphStyle(
            name="SmallRight",
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=SECONDARY_TEXT,
            alignment=TA_RIGHT,
        )
    )
    # Extra style: pricing table header text (white on dark navy)
    base.add(
        ParagraphStyle(
            name="TableHeaderText",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=colors.white,
        )
    )
    return base


def bullet_paragraphs(items: list[str], style: ParagraphStyle) -> list[Paragraph]:
    return [Paragraph(f"• {item}", style) for item in items]


def key_value_grid(values: list[tuple[str, str]], styles) -> Table:
    rows = []
    for index in range(0, len(values), 2):
        pair = values[index : index + 2]
        cells = []
        for label, value in pair:
            cells.append(
                Table(
                    [
                        [Paragraph(label, styles["LabelMuted"])],
                        [Paragraph(value, styles["ValueStrong"])],
                    ],
                    colWidths=[78 * mm],
                    style=TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                            ("BOX", (0, 0), (-1, -1), 1, BORDER),
                            # teal left accent bar on each card
                            ("LINEBEFORE", (0, 0), (0, -1), 3, PRIMARY),
                            ("LEFTPADDING", (0, 0), (-1, -1), 10),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                            ("TOPPADDING", (0, 0), (-1, -1), 8),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                        ]
                    ),
                )
            )
        if len(cells) == 1:
            cells.append("")
        rows.append(cells)

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


def simple_list_section(title: str, items: list[str], story: list, styles) -> None:
    story.append(Paragraph(title, styles["SectionTitlePrimary"]))
    for item in bullet_paragraphs(items, styles["BodyPrimary"]):
        story.append(item)
        story.append(Spacer(1, 3))
    story.append(Spacer(1, 10))


def build_pricing_table(payload: ProposalRequest, styles) -> tuple[Table, float, float, float]:
    rows = [["Item", "Quantity", "Unit Cost", "Total"]]
    subtotal = 0.0
    for item in payload.pricing:
        total = item.quantity * item.unit_cost
        subtotal += total
        rows.append(
            [
                Paragraph(item.item, styles["BodyPrimary"]),
                Paragraph(str(item.quantity), styles["BodyPrimary"]),
                Paragraph(format_inr(item.unit_cost), styles["SmallRight"]),
                Paragraph(format_inr(total), styles["SmallRight"]),
            ]
        )

    gst = subtotal * (payload.commercial_terms.gst_percent / 100)
    grand_total = subtotal + gst

    table = Table(rows, colWidths=[89 * mm, 20 * mm, 35 * mm, 35 * mm], repeatRows=1)
    style_commands = [
        # Dark navy header with white text
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        # teal bottom border under header for a pop of colour
        ("LINEBELOW", (0, 0), (-1, 0), 2, PRIMARY),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
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
            style_commands.append(("BACKGROUND", (0, row_index), (-1, row_index), LIGHT_BACKGROUND))
    table.setStyle(TableStyle(style_commands))

    return table, subtotal, gst, grand_total


def build_summary_table(subtotal: float, gst: float, grand_total: float, gst_percent: float) -> Table:
    rows = [
        ["Subtotal", format_inr(subtotal)],
        [f"GST ({gst_percent:.0f}%)", format_inr(gst)],
        ["Grand Total", format_inr(grand_total)],
    ]
    table = Table(rows, colWidths=[38 * mm, 38 * mm], hAlign="RIGHT")
    table.setStyle(
        TableStyle(
            [
                ("TEXTCOLOR", (0, 0), (-1, 1), DARK_TEXT),
                ("FONTNAME", (0, 0), (-1, 1), "Helvetica"),
                ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 2), (-1, 2), PRIMARY),
                ("FONTSIZE", (0, 0), (-1, 1), 9),
                ("FONTSIZE", (0, 2), (-1, 2), 13),
                ("LINEABOVE", (0, 0), (-1, 0), 0.5, BORDER),
                ("LINEBELOW", (0, 1), (-1, 1), 2, PRIMARY),   # teal separator above grand total
                ("BACKGROUND", (0, 2), (-1, 2), colors.white),
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
    styles = _styles()
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )

    story = [
        Table(
            [[
                Table(
                    [
                        [
                            Table(
                                [[Paragraph(payload.company.logo_text, ParagraphStyle(
                                    "LogoStyle",
                                    fontName="Helvetica-Bold",
                                    fontSize=13,
                                    textColor=colors.white,
                                    alignment=1,
                                ))]],
                                colWidths=[14 * mm],
                                rowHeights=[14 * mm],
                                style=TableStyle(
                                    [
                                        ("BACKGROUND", (0, 0), (-1, -1), TABLE_HEADER),  # navy badge
                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                        ("BOX", (0, 0), (-1, -1), 2, PRIMARY),           # teal border ring
                                    ]
                                ),
                            ),
                            Paragraph(
                                f"<b>{payload.company.name}</b><br/>{payload.company.tag_line}",
                                styles["BodyPrimary"],
                            ),
                            Paragraph(payload.document.issue_date, styles["SmallRight"]),
                        ]
                    ],
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
            ]],
            colWidths=[174 * mm],
            style=TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]),
        ),
        Spacer(1, 8),
        # Double rule: thin teal over thicker teal for a layered effect
        HRFlowable(width="100%", thickness=3, color=TABLE_HEADER, spaceAfter=2),
        HRFlowable(width="100%", thickness=1.5, color=PRIMARY),
        Spacer(1, 10),
        Paragraph(payload.document.title, styles["SectionTitlePrimary"]),
        Paragraph(payload.project_title, styles["TitlePrimary"]),
        Paragraph(
            f"{payload.client.company_name}<br/>{payload.client.contact_person}, "
            f"{payload.client.designation}<br/>{payload.client.email}",
            styles["BodyMuted"],
        ),
        Spacer(1, 10),
        key_value_grid(
            [
                ("Proposal Reference", payload.document.reference),
                ("Prepared By", payload.document.prepared_by),
                ("Issue Date", payload.document.issue_date),
                ("Validity", payload.document.validity),
            ],
            styles,
        ),
        Spacer(1, 4),
        Paragraph("Executive Summary", styles["SectionTitlePrimary"]),
        Paragraph(payload.executive_summary, styles["BodyPrimary"]),
        Spacer(1, 12),
        Table(
            [[
                Table(
                    [
                        [Paragraph("Business Objectives", styles["SectionTitlePrimary"])],
                        *[[Paragraph(f"• {item}", styles["BodyPrimary"])] for item in payload.business_objectives],
                    ],
                    colWidths=[84 * mm],
                    style=TableStyle(
                        [
                            ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                            ("LINEBEFORE", (0, 0), (0, -1), 3, PRIMARY),   # teal left bar
                            ("TOPPADDING", (0, 0), (-1, -1), 8),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                            ("LEFTPADDING", (0, 0), (-1, -1), 10),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ]
                    ),
                ),
                Table(
                    [
                        [Paragraph("Proposed Response", styles["SectionTitlePrimary"])],
                        *[[Paragraph(f"• {item}", styles["BodyPrimary"])] for item in payload.proposed_solution],
                    ],
                    colWidths=[84 * mm],
                    style=TableStyle(
                        [
                            ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                            ("LINEBEFORE", (0, 0), (0, -1), 3, PRIMARY),   # teal left bar
                            ("TOPPADDING", (0, 0), (-1, -1), 8),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                            ("LEFTPADDING", (0, 0), (-1, -1), 10),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ]
                    ),
                ),
            ]],
            colWidths=[87 * mm, 87 * mm],
            style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]),
        ),
        Spacer(1, 12),
    ]

    simple_list_section("Scope of Work", payload.scope_of_work, story, styles)

    pricing_table, subtotal, gst, grand_total = build_pricing_table(payload, styles)
    story.append(Paragraph("Commercial Proposal", styles["SectionTitlePrimary"]))
    story.append(pricing_table)
    story.append(Spacer(1, 8))
    story.append(build_summary_table(subtotal, gst, grand_total, payload.commercial_terms.gst_percent))
    story.append(Spacer(1, 12))

    story.append(
        Table(
            [
                [Paragraph(payload.value_add_heading, styles["SectionTitlePrimary"])],
                *[[Paragraph(f"• {item}", styles["BodyPrimary"])] for item in payload.value_add_points],
            ],
            colWidths=[174 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), HIGHLIGHT_BOX),
                    ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                    ("LINEBEFORE", (0, 0), (0, -1), 4, PRIMARY),   # bold teal left bar
                    ("LEFTPADDING", (0, 0), (-1, -1), 14),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            ),
        )
    )
    story.append(Spacer(1, 12))

    simple_list_section("Timeline and Milestones", payload.timeline, story, styles)
    simple_list_section("Key Deliverables", payload.deliverables, story, styles)
    simple_list_section("Payment Terms", payload.commercial_terms.payment_terms, story, styles)

    story.append(Paragraph("Terms and Conditions", styles["SectionTitlePrimary"]))
    for term in payload.commercial_terms.terms_and_conditions:
        story.append(Paragraph(f"• {term}", styles["BodyMuted"]))
        story.append(Spacer(1, 2))

    signatory_cells: list[object] = []
    if STAMP_PATH.exists():
        signatory_cells.append(Image(str(STAMP_PATH), width=28 * mm, height=28 * mm))
        signatory_cells.append(Spacer(1, 2))
    signatory_cells.append(
        Paragraph(
            f"<b>Authorized Signatory</b><br/>{payload.authorized_signatory}",
            styles["SmallRight"],
        )
    )

    story.extend(
        [
            Spacer(1, 14),
            HRFlowable(width="100%", thickness=1.5, color=PRIMARY),   # teal footer rule
            HRFlowable(width="100%", thickness=3, color=TABLE_HEADER, spaceAfter=8),
            Spacer(1, 8),
            Table(
                [[
                    Paragraph(
                        f"<b>{payload.company.name}</b><br/>{payload.company.email} | {payload.company.phone}<br/>"
                        f"{payload.company.address} | {payload.company.website}",
                        styles["BodyMuted"],
                    ),
                    Table(
                        [[cell] for cell in signatory_cells],
                        colWidths=[54 * mm],
                        style=TableStyle(
                            [
                                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                ("TOPPADDING", (0, 0), (-1, -1), 0),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                            ]
                        ),
                    ),
                ]],
                colWidths=[120 * mm, 54 * mm],
                style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]),
            ),
        ]
    )

    document.build(story)
    return buffer.getvalue()
