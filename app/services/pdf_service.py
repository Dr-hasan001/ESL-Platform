"""
pdf_service.py — Generate a results PDF for a completed homework submission.
"""

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

GREEN  = colors.HexColor("#2A6B3D")
RED    = colors.HexColor("#C84830")
BLUE   = colors.HexColor("#1E5C72")
GREY   = colors.HexColor("#888888")
LGREY  = colors.HexColor("#F5F5F5")
LGREEN = colors.HexColor("#EAF4ED")
LRED   = colors.HexColor("#FAEAEA")

LETTERS = ["A", "B", "C", "D"]


def _style(name, **kw):
    base = ParagraphStyle(name, fontName="Helvetica", fontSize=10, leading=14)
    for k, v in kw.items():
        setattr(base, k, v)
    return base


def generate_submission_pdf(hw, student, submission, questions, answers_map) -> bytes:
    """
    hw           — HomeworkAssignment ORM object
    student      — User ORM object
    submission   — Submission ORM object
    questions    — list[HomeworkQuestion] ordered by position
    answers_map  — dict { question_id: SubmissionAnswer }
    Returns      — raw PDF bytes
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )

    # ── Styles ────────────────────────────────────────────────────────────────
    s_title   = _style("title",  fontSize=18, fontName="Helvetica-Bold",
                        alignment=TA_CENTER, spaceAfter=4, textColor=BLUE)
    s_meta    = _style("meta",   fontSize=9,  alignment=TA_CENTER,
                        textColor=GREY, spaceAfter=3)
    s_score   = _style("score",  fontSize=22, fontName="Helvetica-Bold",
                        alignment=TA_CENTER, spaceAfter=4)
    s_q_num   = _style("qnum",   fontSize=7.5, fontName="Helvetica-Bold",
                        textColor=GREY, spaceAfter=2, spaceBefore=14)
    s_q_text  = _style("qtext",  fontSize=11, fontName="Helvetica-Bold",
                        leading=16, spaceAfter=6)
    s_opt     = _style("opt",    fontSize=9.5, leading=13, leftIndent=4)

    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph(hw.title, s_title))
    story.append(Paragraph(
        f"Student: <b>{student.display_name or student.username}</b>"
        + (f"  |  Class: <b>{student.class_name}</b>" if student.class_name else ""),
        s_meta,
    ))
    submitted_date = ""
    if submission.submitted_at:
        submitted_date = submission.submitted_at.strftime("%B %d, %Y  %H:%M")
    story.append(Paragraph(f"Submitted: {submitted_date}", s_meta))
    story.append(Spacer(1, 0.3 * cm))

    correct = submission.correct_count or 0
    total   = submission.total_questions or len(questions)
    pct     = f"  ({submission.score:.0f}%)" if submission.score is not None else ""
    score_color = GREEN if (submission.score or 0) >= 60 else RED
    story.append(Paragraph(
        f'<font color="{score_color.hexval()}"><b>{correct} / {total}{pct}</b></font>',
        s_score,
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#DDDDDD"),
                             spaceAfter=8))

    # ── Questions ─────────────────────────────────────────────────────────────
    for i, q in enumerate(questions, start=1):
        ans     = answers_map.get(q.id)
        chosen  = ans.chosen_index if ans is not None else -1
        is_ok   = ans.is_correct   if ans is not None else None

        story.append(Paragraph(f"Question {i} of {total}", s_q_num))
        story.append(Paragraph(q.question_text, s_q_text))

        if q.options:
            rows = []
            for j, opt_text in enumerate(q.options):
                letter = LETTERS[j] if j < 4 else str(j + 1)
                label  = f"{letter}."

                is_student_pick = (j == chosen)
                is_correct_ans  = (j == q.correct_index)

                # Marker column
                if is_student_pick and is_correct_ans:
                    marker = "OK"
                    bg     = LGREEN
                    fg     = GREEN
                    bold   = True
                elif is_student_pick and not is_correct_ans:
                    marker = "X"
                    bg     = LRED
                    fg     = RED
                    bold   = True
                elif is_correct_ans:
                    marker = "ans"
                    bg     = LGREEN
                    fg     = GREEN
                    bold   = True
                else:
                    marker = ""
                    bg     = colors.white
                    fg     = GREY
                    bold   = False

                m_style = _style(f"m{i}{j}", fontSize=7.5, fontName="Helvetica-Bold",
                                 textColor=fg, alignment=TA_CENTER)
                o_style = _style(f"o{i}{j}", fontSize=9.5, leading=13,
                                 textColor=fg if bold else colors.black,
                                 fontName="Helvetica-Bold" if bold else "Helvetica")

                rows.append([
                    Paragraph(marker, m_style),
                    Paragraph(label,  o_style),
                    Paragraph(opt_text, o_style),
                ])

            col_w = [A4[0] - 4 * cm]  # full usable width
            tbl = Table(rows, colWidths=[1.2 * cm, 1.0 * cm, A4[0] - 4 * cm - 2.2 * cm])

            # Build row styles
            tbl_styles = [
                ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
                ("TOPPADDING",    (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white]),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#EEEEEE")),
                ("ROUNDEDCORNERS", [4]),
            ]
            for j in range(len(rows)):
                ans_j = q.options[j]
                is_pick = (j == chosen)
                is_corr = (j == q.correct_index)
                if (is_pick and is_corr) or (is_corr and not is_pick):
                    tbl_styles.append(("BACKGROUND", (0, j), (-1, j), LGREEN))
                elif is_pick and not is_corr:
                    tbl_styles.append(("BACKGROUND", (0, j), (-1, j), LRED))

            tbl.setStyle(TableStyle(tbl_styles))
            story.append(tbl)
            story.append(Spacer(1, 0.2 * cm))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()
