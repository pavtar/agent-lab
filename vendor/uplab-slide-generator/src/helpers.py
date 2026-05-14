"""
Composable rendering primitives for Uplab presentations (v3).

6 helpers that cover all slide types. Each creates minimal shapes.
All geometry is fixed Inches for 16:9 (10 x 5.625").
"""

from __future__ import annotations

import os
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

from . import styles as S

# ── Geometry constants (~15 instead of 70+) ──────────────────────
ML = Inches(0.6)            # left margin
MR = Inches(0.6)            # right margin (symmetric)
CW = Inches(8.8)            # content width (10 - 0.6 - 0.6)
SW = Inches(10.0)           # slide width
SH = Inches(5.625)          # slide height

TOP_TITLE = Inches(0.35)    # Y of heading
TOP_BODY = Inches(1.15)     # Y of body content
BODY_H = Inches(3.8)        # max body height
COL_GAP = Inches(0.3)       # gap between columns
COL_W = (CW - COL_GAP) / 2  # width of each column in 2-col layout

MINT_TOP = Inches(2.4)      # Y of title on mint slides
MINT_LEFT = Inches(0.5)     # left margin on mint slides
MINT_W = Inches(6.5)        # title width on mint slides

TABLE_ROW_H = Inches(0.42)  # row height in tables (room for 12–14 pt text)

# Case slide: title ~2 lines @ 16 pt; gray subtitle under title (left column only)
CASE_TITLE_W = Inches(4.15)       # to ~mid-slide before image column (5.0")
CASE_TITLE_H = Inches(0.74)       # ~2 lines @ 16 pt
CASE_SUBTITLE_GAP = Inches(0.04)
CASE_SUBTITLE_H = Inches(0.38)    # year · category
CASE_BODY_GAP = Inches(0.08)
# Case image: right column, almost full slide height (original layout)
CASE_IMG_TOP = Inches(0.15)
CASE_IMG_H = Inches(5.3)
CASE_IMG_LEFT = Inches(5.0)
CASE_IMG_W = Inches(4.8)

# Bottom-right logo (larger); bottom edge aligned with breadcrumb strip bottom
LOGO_BR_WIDTH = Inches(0.75)

# Bottom band: breadcrumb + logo BR same vertical strip (equal height)
BREADCRUMB_TOP = Inches(5.22)
BREADCRUMB_W = Inches(4.0)
BREADCRUMB_H = Inches(0.36)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ═══════════════════════════════════════════════════════════════════
#  Primitive 1: H — Heading
# ═══════════════════════════════════════════════════════════════════

def H(slide, text: str, size=None, top=None, left=None, width=None,
      font=S.FONT_HEADING, color=S.DARK, bold=True,
      height=None, anchor_top: bool = False):
    """Single heading text box. Returns the shape."""
    if size is None:
        size = Pt(S.FS_PAGE_TITLE)
    if top is None:
        top = TOP_TITLE
    if left is None:
        left = ML
    if width is None:
        width = CW
    if height is None:
        height = Inches(0.85)
    bx = slide.shapes.add_textbox(left, top, width, height)
    tf = bx.text_frame
    tf.word_wrap = True
    if anchor_top:
        tf.vertical_anchor = MSO_ANCHOR.TOP
    _run(tf.paragraphs[0], text, font, size, color, bold)
    return bx


# ═══════════════════════════════════════════════════════════════════
#  Primitive 2: L — List / multiline text in ONE text frame
# ═══════════════════════════════════════════════════════════════════

def L(slide, items: list[str], top=None, left=None, width=None, height=None,
      size=None, font=S.FONT_BODY, color=S.DARK, bold=False,
      spacing=Pt(8), align=PP_ALIGN.LEFT):
    """Multiple lines / bullet points in a single text frame."""
    if top is None:
        top = TOP_BODY
    if left is None:
        left = ML
    if width is None:
        width = CW
    if height is None:
        height = BODY_H
    if size is None:
        size = Pt(S.FS_BODY)
    bx = slide.shapes.add_textbox(left, top, width, height)
    tf = bx.text_frame
    tf.word_wrap = True
    for i, txt in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if txt.startswith("- ") or txt.startswith("* "):
            txt = "\u2022 " + txt[2:]
        _run(p, txt, font, size, color, bold)
        if spacing:
            p.space_before = spacing
    return bx


# ═══════════════════════════════════════════════════════════════════
#  Primitive 3: TBL — Table with gray header
# ═══════════════════════════════════════════════════════════════════

def TBL(slide, headers: list[str], rows: list[list[str]],
        top=None, left=None, width=None,
        hdr_size=None, cell_size=None,
        auto_column_widths: bool = True):
    """Real pptx table. Returns the shape.

    By default, column widths follow content length (see
    ``set_table_column_widths_by_content``). Pass ``auto_column_widths=False``
    for equal-width columns.
    """
    if top is None:
        top = TOP_BODY
    if left is None:
        left = ML
    if width is None:
        width = CW
    if hdr_size is None:
        hdr_size = Pt(S.FS_SMALL)
    if cell_size is None:
        cell_size = Pt(S.FS_SMALL)
    n_rows = len(rows) + 1
    n_cols = len(headers)
    tbl_h = TABLE_ROW_H * n_rows
    shape = slide.shapes.add_table(n_rows, n_cols, left, top, width, tbl_h)
    table = shape.table
    _style_table(table)

    for ci, h in enumerate(headers):
        _fmt_cell(table.cell(0, ci), h, S.FONT_HEADING, hdr_size, S.DARK, bold=True)

    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            if ci < n_cols:
                is_bold = val.startswith("**") and val.endswith("**")
                clean = val.strip("*") if is_bold else val
                _fmt_cell(table.cell(ri + 1, ci), clean, S.FONT_BODY,
                          cell_size, S.DARK, is_bold)

    if auto_column_widths and n_cols > 0:
        set_table_column_widths_by_content(shape, headers, rows)

    return shape


def set_table_column_widths_by_content(shape, headers: list[str], rows: list[list[str]],
                                       min_frac=0.12, max_frac=0.55):
    """Distribute column widths by max text length per column (uses graphic frame width).

    Called automatically from :func:`TBL` unless ``auto_column_widths=False``.
    Can be called manually for tables not created via ``TBL``.
    """
    table = shape.table
    n_cols = len(headers)
    if n_cols == 0:
        return
    total_w = int(shape.width)
    if total_w <= 0:
        return

    lengths = []
    for ci in range(n_cols):
        cells = [headers[ci]] if ci < len(headers) else [""]
        for row in rows:
            if ci < len(row):
                cells.append(row[ci])
        lens = [len(c) for c in cells]
        lengths.append(max(lens) if lens else 1)

    weights = [max(1.0, float(L)) for L in lengths]
    s = sum(weights)
    fracs = [w / s for w in weights]
    fracs = [max(min_frac, min(max_frac, f)) for f in fracs]
    s2 = sum(fracs)
    fracs = [f / s2 for f in fracs]

    widths = [int(round(total_w * f)) for f in fracs]
    drift = total_w - sum(widths)
    if widths:
        widths[-1] = max(1, widths[-1] + drift)

    for ci, w in enumerate(widths):
        table.columns[ci].width = w


# ═══════════════════════════════════════════════════════════════════
#  Primitive 4: BIG — Accent number / statement
# ═══════════════════════════════════════════════════════════════════

def BIG(slide, text: str, size=None, top=None, color=S.DARK,
        font=S.FONT_HEADING, left=None, width=None, align=PP_ALIGN.LEFT, height=None):
    """Large accent text (number, fact, metric)."""
    if size is None:
        size = Pt(S.FS_STAT_NUM)
    if top is None:
        top = Inches(3.4)
    if left is None:
        left = ML
    if width is None:
        width = CW
    if height is None:
        height = Inches(0.7)
    bx = slide.shapes.add_textbox(left, top, width, height)
    tf = bx.text_frame
    tf.word_wrap = True
    _run(tf.paragraphs[0], text, font, size, color, bold=True)
    tf.paragraphs[0].alignment = align
    return bx


# ═══════════════════════════════════════════════════════════════════
#  Primitive 5: IMG — Image or gray placeholder
# ═══════════════════════════════════════════════════════════════════

def IMG(slide, path: str, left=None, top=None, width=None, height=None):
    """Insert image file, or gray placeholder if missing."""
    if left is None:
        left = ML
    if top is None:
        top = TOP_BODY
    if width is None:
        width = CW
    if height is None:
        height = BODY_H
    full = os.path.join(BASE_DIR, path) if not os.path.isabs(path) else path
    if path and os.path.isfile(full):
        return slide.shapes.add_picture(full, left, top, width, height)
    return _placeholder(slide, left, top, width, height, path or "Image")


# ═══════════════════════════════════════════════════════════════════
#  Primitive 6: LOGO — Company logo
# ═══════════════════════════════════════════════════════════════════

def LOGO(slide, variant="black"):
    """Insert Uplab logo in top-left corner."""
    fname = S.LOGO_BLACK if variant == "black" else S.LOGO_WHITE
    path = os.path.join(BASE_DIR, fname)
    if os.path.isfile(path):
        return slide.shapes.add_picture(
            path, Inches(0.3), Inches(0.2), Inches(0.9))
    return None


def LOGO_BOTTOM_RIGHT(slide, variant="black"):
    """Logo bottom-right at previous size; bottom aligns with breadcrumb row bottom."""
    fname = S.LOGO_BLACK if variant == "black" else S.LOGO_WHITE
    path = os.path.join(BASE_DIR, fname)
    if not os.path.isfile(path):
        return None
    margin = Inches(0.35)
    band_bottom = BREADCRUMB_TOP + BREADCRUMB_H
    pic = slide.shapes.add_picture(
        path, Inches(0), Inches(0), width=LOGO_BR_WIDTH)
    pic.top = int(band_bottom - pic.height)
    pic.left = int(Inches(10.0) - margin - pic.width)
    return pic


# ═══════════════════════════════════════════════════════════════════
#  Engine-level helpers (breadcrumb, slide number)
# ═══════════════════════════════════════════════════════════════════

def add_breadcrumb(slide, text: str):
    """Small text bottom-left; same vertical band as LOGO_BOTTOM_RIGHT."""
    bx = slide.shapes.add_textbox(
        ML, BREADCRUMB_TOP, BREADCRUMB_W, BREADCRUMB_H)
    tf = bx.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    _run(tf.paragraphs[0], text, S.FONT_BODY, Pt(S.FS_BREADCRUMB), S.GRAY_TEXT)


def add_slide_number(slide, number: int):
    """Slide number in top-right corner."""
    bx = slide.shapes.add_textbox(
        Inches(9.3), Inches(0.2), Inches(0.5), Inches(0.3))
    tf = bx.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    _run(p, str(number), S.FONT_BODY, Pt(S.FS_SLIDE_NUM - 2), S.GRAY_TEXT)


# ═══════════════════════════════════════════════════════════════════
#  Internal helpers
# ═══════════════════════════════════════════════════════════════════

def _run(p, text, font=S.FONT_BODY, size=Pt(10), color=S.DARK, bold=False):
    """Add a single formatted run to a paragraph."""
    r = p.add_run()
    r.text = text
    r.font.name = font
    r.font.size = size
    r.font.color.rgb = color
    r.font.bold = bold
    return r


def _placeholder(slide, left, top, width, height, label=""):
    """Gray rectangle placeholder with centered label."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor.from_string(S.PLACEHOLDER_FILL)
    shape.line.fill.background()
    if label:
        tf = shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = f"[{label}]"
        r.font.name = S.FONT_BODY
        r.font.size = Pt(S.FS_SMALL)
        r.font.color.rgb = RGBColor.from_string("999999")
    return shape


def _style_table(table):
    """Minimal Google-Slides-safe table styling."""
    tbl = table._tbl
    pr = tbl.tblPr if tbl.tblPr is not None else tbl._add_tblPr()
    for attr in ("bandRow", "bandCol", "firstRow", "lastRow", "firstCol", "lastCol"):
        pr.set(attr, "0")


def _fmt_cell(cell, text, font=S.FONT_BODY, size=Pt(10),
              color=S.DARK, bold=False):
    """Format a table cell."""
    cell.text = ""
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    _run(p, text, font, size, color, bold)
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    if bold and font == S.FONT_HEADING:
        _cell_fill(cell, S.TABLE_HEADER_FILL)


def _cell_fill(cell, hex_color):
    tc_pr = cell._tc.get_or_add_tcPr()
    old = tc_pr.find(qn("a:solidFill"))
    if old is not None:
        tc_pr.remove(old)
    sf = tc_pr.makeelement(qn("a:solidFill"), {})
    sf.append(sf.makeelement(qn("a:srgbClr"), {"val": hex_color}))
    tc_pr.insert(0, sf)
