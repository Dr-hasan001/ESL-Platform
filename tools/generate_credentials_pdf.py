"""
generate_credentials_pdf.py — Create a printable PDF of student login cards.

Run:  python tools/generate_credentials_pdf.py
Output: student_credentials.pdf  (in the project root)

Requires: pip install reportlab
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

# ── Student data ──────────────────────────────────────────────────────────────

A2_STUDENTS = [
    ("Mohammed Karem",         "m_karem",    "karem1847"),
    ("Aqeel Albdulrazaq",      "aqeel",      "aqeel3856"),
    ("Hussein Ali Adnan",      "h_adnan",    "adnan6274"),
    ("Murtadha Khaled",        "murtadha",   "murtadha9431"),
    ("Ruqaya Mazin",           "ruqaya",     "ruqaya5817"),
    ("Baneen Raad",            "baneen",     "baneen2963"),
    ("Aya Sabah",              "aya",        "aya7154"),
    ("Fatimah Hassan",         "fatimah",    "fatimah4029"),
    ("Mohammed Rida",          "m_rida",     "rida8563"),
    ("Nasser Haider",          "nasser",     "nasser6748"),
    ("Muhsin Ahmed",           "muhsin",     "muhsin3195"),
    ("Hussein Ali Abdulameer", "h_abd",      "abd8342"),
    ("Raghad Mufak",           "raghad",     "raghad5209"),
    ("Aymen",                  "aymen",      "aymen6382"),
    ("Fatima Abd",             "fatima_abd", "abd7519"),
    ("Muntadhar",              "muntadhar",  "muntadhar4617"),
]

B1_STUDENTS = [
    ("Yasser",          "yasser",   "yasser2847"),
    ("Muna",            "muna",     "muna5193"),
    ("Hasan",           "hasan",    "hasan7364"),
    ("Haider",          "haider",   "haider8251"),
    ("Sajad Mohammed",  "sajad",    "sajad3679"),
    ("Wissam",          "wissam",   "wissam4928"),
    ("Ahmed",           "ahmed",    "ahmed6173"),
    ("Mohammed Sadiq",  "m_sadiq",  "sadiq5847"),
    ("Fiqar",           "fiqar",    "fiqar3847"),
    ("Faisal",          "faisal",   "faisal5293"),
    ("Karar",           "karar",    "karar7162"),
    ("Ali Alsajad",     "ali_sajad","sajad9384"),
]

SITE_URL = "https://esl-platform.onrender.com"

# ── PDF setup ─────────────────────────────────────────────────────────────────

OUTPUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "student_credentials.pdf")
doc = SimpleDocTemplate(OUTPUT, pagesize=A4,
                        leftMargin=1.5*cm, rightMargin=1.5*cm,
                        topMargin=1.5*cm, bottomMargin=1.5*cm)

styles = getSampleStyleSheet()

title_style = ParagraphStyle("title", fontSize=18, fontName="Helvetica-Bold",
                              alignment=TA_CENTER, spaceAfter=4)
sub_style   = ParagraphStyle("sub",   fontSize=10, fontName="Helvetica",
                              alignment=TA_CENTER, spaceAfter=12, textColor=colors.grey)
section_style = ParagraphStyle("section", fontSize=13, fontName="Helvetica-Bold",
                                spaceBefore=14, spaceAfter=6,
                                textColor=colors.HexColor("#1E5C72"))

A2_COLOR = colors.HexColor("#1E5C72")   # dark teal
B1_COLOR = colors.HexColor("#4A3580")   # purple

def make_card_table(students, level_color, level_label):
    """Return a ReportLab Table of 2-column login cards."""
    card_width = (A4[0] - 3*cm) / 2   # two cards per row with margins

    cell_style_name = ParagraphStyle("cn", fontSize=11, fontName="Helvetica-Bold", leading=14)
    cell_style_label = ParagraphStyle("cl", fontSize=7.5, fontName="Helvetica",
                                      textColor=colors.grey, spaceBefore=4)
    cell_style_value = ParagraphStyle("cv", fontSize=10, fontName="Helvetica-Bold",
                                      textColor=colors.HexColor("#222222"))
    cell_style_url   = ParagraphStyle("cu", fontSize=7.5, fontName="Helvetica",
                                      textColor=colors.grey)

    def make_cell(name, username, password):
        return [
            Paragraph(f'<font color="{level_color.hexval()}">{level_label}</font>  {name}', cell_style_name),
            Paragraph("Username", cell_style_label),
            Paragraph(username, cell_style_value),
            Paragraph("Password", cell_style_label),
            Paragraph(password, cell_style_value),
            Spacer(1, 4),
            Paragraph(SITE_URL, cell_style_url),
        ]

    # Pair students into rows of 2
    rows = []
    for i in range(0, len(students), 2):
        left  = make_cell(*students[i])
        right = make_cell(*students[i + 1]) if i + 1 < len(students) else [""]
        rows.append([left, right])

    t = Table(rows, colWidths=[card_width, card_width])
    t.setStyle(TableStyle([
        ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("INNERGRID",   (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",  (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0,0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",(0, 0), (-1, -1), 10),
        ("BACKGROUND",  (0, 0), (-1, -1), colors.HexColor("#F9FAFB")),
    ]))
    return t


# ── Build document ────────────────────────────────────────────────────────────

story = [
    Paragraph("ESL Platform — Student Login Cards", title_style),
    Paragraph(SITE_URL, sub_style),

    Paragraph("A2 — Elementary", section_style),
    make_card_table(A2_STUDENTS, A2_COLOR, "A2"),
    Spacer(1, 0.5*cm),

    Paragraph("B1 — Intermediate", section_style),
    make_card_table(B1_STUDENTS, B1_COLOR, "B1"),
]

doc.build(story)
print(f"PDF created: {OUTPUT}")
