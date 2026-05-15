"""
Slide renderers (v3) — each type is 3-8 lines composing helpers.

Each renderer: render_xxx(slide, spec) -> None
"""

from __future__ import annotations

import math

from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

from . import styles as S
from .helpers import H, L, TBL, BIG, IMG, LOGO, ML, CW, COL_GAP, COL_W, SH
from .helpers import TOP_TITLE, TOP_BODY, BODY_H, MINT_TOP, MINT_LEFT, MINT_W
from .helpers import (
    CASE_TITLE_W,
    CASE_TITLE_H,
    CASE_SUBTITLE_GAP,
    CASE_SUBTITLE_H,
    CASE_BODY_GAP,
    CASE_IMG_TOP,
    CASE_IMG_H,
    CASE_IMG_LEFT,
    CASE_IMG_W,
)
from .helpers import _placeholder, _run
from .parser import SlideSpec


def _body_top_for_title(title: str, base=TOP_BODY):
    """
    Shift body down for long titles so content never overlaps heading.
    Heuristic: ~38 chars per heading line at current width/font.
    """
    clean = " ".join((title or "").split())
    if not clean:
        return base
    estimated_lines = max(1, math.ceil(len(clean) / 38))
    extra_lines = max(0, estimated_lines - 1)
    # ~0.22" per extra line + a little breathing room.
    shift = Inches(min(0.75, extra_lines * 0.22))
    return base + shift


# ═══════════════════════════════════════════════════════════════════
#  1. COVER
# ═══════════════════════════════════════════════════════════════════

def render_cover(slide, spec: SlideSpec):
    LOGO(slide, "black")
    H(slide, spec.title, size=Pt(S.FS_COVER), top=MINT_TOP,
      left=MINT_LEFT, width=MINT_W)
    if spec.content:
        L(slide, [spec.content.split("\n")[0]],
          top=Inches(3.6), left=MINT_LEFT, width=MINT_W,
          size=Pt(S.FS_BODY_LG), color=S.DARK)


# ═══════════════════════════════════════════════════════════════════
#  2. SECTION
# ═══════════════════════════════════════════════════════════════════

def render_section(slide, spec: SlideSpec):
    H(slide, spec.title, size=Pt(S.FS_SECTION), top=MINT_TOP,
      left=MINT_LEFT, width=MINT_W, font=S.FONT_HEADING, bold=False)
    if spec.content:
        L(slide, [spec.content.split("\n")[0]],
          top=Inches(3.6), left=MINT_LEFT, width=MINT_W,
          size=Pt(S.FS_BODY_LG), color=S.DARK)


# ═══════════════════════════════════════════════════════════════════
#  3. STATS
# ═══════════════════════════════════════════════════════════════════

def render_stats(slide, spec: SlideSpec):
    H(slide, spec.title, size=Pt(S.FS_BODY_LG))
    body_top = _body_top_for_title(spec.title)

    stats = [it for it in spec.items if "_footer" not in it]
    footer = next((it["_footer"] for it in spec.items if "_footer" in it), "")

    if stats:
        metric_lines = []
        for item in stats:
            metric_lines.append(f"{item['value']}  —  {item.get('label', '')}")
        L(slide, metric_lines, top=body_top, size=Pt(S.FS_BODY_LG),
          font=S.FONT_HEADING, spacing=Pt(12))

    body = spec.content.strip()
    if body:
        lines = body.split("\n")
        y = Inches(3.2) if stats else body_top
        L(slide, lines, top=y, size=Pt(S.FS_BODY))

    if footer:
        L(slide, [footer], top=Inches(4.4), size=Pt(S.FS_BODY), color=S.GRAY_TEXT)


# ═══════════════════════════════════════════════════════════════════
#  4. TEXT
# ═══════════════════════════════════════════════════════════════════

def render_text(slide, spec: SlideSpec):
    H(slide, spec.title)
    if spec.content:
        L(slide, spec.content.split("\n"), top=_body_top_for_title(spec.title))


# ═══════════════════════════════════════════════════════════════════
#  5. COLUMNS (2 or 3 columns with sub-headers)
# ═══════════════════════════════════════════════════════════════════

def render_columns(slide, spec: SlideSpec):
    H(slide, spec.title)
    body_top = _body_top_for_title(spec.title)
    sections = spec.sections
    requested_cols = int(spec.params.get("cols", 0) or 0)
    requested_cols = max(1, min(requested_cols, 3))

    # Fallback for a common reporting case:
    # one continuous numbered/bullet list with `# columns: 2/3` and no `###` blocks.
    # In this mode we auto-split list items evenly across requested columns.
    if requested_cols > 1 and _sections_look_like_single_block(sections):
        list_lines = _extract_list_lines(spec.content)
        if len(list_lines) >= requested_cols:
            sections = _split_lines_to_sections(list_lines, requested_cols)

    n = min(len(sections), requested_cols if requested_cols else len(sections), 3)
    if n == 0:
        return

    gap = COL_GAP
    w = (CW - gap * (n - 1)) / n

    for i, sec in enumerate(sections[:n]):
        x = ML + (w + gap) * i
        lines = []
        if sec.get("title"):
            lines.append(sec["title"])
        body = sec.get("body", "")
        if body:
            lines.extend(body.split("\n"))
        if lines:
            first_bold = bool(sec.get("title"))
            _col_block(slide, lines, x, body_top, w,
                       first_bold=first_bold)


def _sections_look_like_single_block(sections: list[dict[str, str]]) -> bool:
    if len(sections) != 1:
        return False
    sec = sections[0]
    title = (sec.get("title") or "").strip()
    body = (sec.get("body") or "").strip()
    return bool(title or body)


def _extract_list_lines(text: str) -> list[str]:
    lines = []
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("- ") or line.startswith("* "):
            lines.append(line)
            continue
        if "." in line:
            prefix, _rest = line.split(".", 1)
            if prefix.strip().isdigit():
                lines.append(line)
    return lines


def _split_lines_to_sections(lines: list[str], cols: int) -> list[dict[str, str]]:
    chunk_size = int(math.ceil(len(lines) / cols))
    result = []
    for i in range(cols):
        chunk = lines[i * chunk_size:(i + 1) * chunk_size]
        if not chunk:
            continue
        result.append({"title": "", "body": "\n".join(chunk)})
    return result


def _strip_markdown_asterisks_lines(text: str) -> list[str]:
    """Remove ** from sidebar / pasted markdown so labels render clean."""
    return [line.replace("**", "") for line in text.split("\n")]


def _steps_column(slide, sections, start_num: int, x, top, w):
    """Numbered step blocks in one column (bold titles)."""
    if not sections:
        return
    bx = slide.shapes.add_textbox(x, top, w, BODY_H)
    tf = bx.text_frame
    tf.word_wrap = True
    num = start_num
    first = True
    for sec in sections:
        title = (sec.get("title") or "").strip()
        body = (sec.get("body") or "").strip()
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        _run(p, f"{num}. {title}", S.FONT_HEADING, Pt(S.FS_BODY), S.DARK, True)
        p.space_before = Pt(10)
        num += 1
        for raw in body.split("\n"):
            ln = raw.strip()
            if not ln:
                continue
            p2 = tf.add_paragraph()
            if ln.startswith("- ") or ln.startswith("* "):
                ln = "\u2022 " + ln[2:]
            _run(p2, ln, S.FONT_BODY, Pt(S.FS_BODY), S.DARK, False)
            p2.space_before = Pt(4)


def _col_block(slide, lines, left, top, width, first_bold=False):
    """Column block: optional bold first line, then body lines."""
    bx = slide.shapes.add_textbox(left, top, width, BODY_H)
    tf = bx.text_frame
    tf.word_wrap = True
    for i, txt in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        is_bullet = txt.startswith("- ") or txt.startswith("* ")
        if is_bullet:
            txt = "\u2022 " + txt[2:]
        bold = first_bold and i == 0
        font = S.FONT_HEADING if bold else S.FONT_BODY
        _run(p, txt, font, Pt(S.FS_BODY), S.DARK, bold)
        p.space_before = Pt(6)
    return bx


# ═══════════════════════════════════════════════════════════════════
#  6. TABLE (+ optional sidebar)
# ═══════════════════════════════════════════════════════════════════

def render_table(slide, spec: SlideSpec):
    H(slide, spec.title)
    body_top = _body_top_for_title(spec.title)

    if not spec.table_headers:
        if spec.content:
            L(slide, spec.content.split("\n"))
        return

    has_sidebar = bool(spec.sidebar)
    tbl_w = Inches(5.8) if has_sidebar else CW

    TBL(slide, spec.table_headers, spec.table_rows, width=tbl_w, top=body_top)

    if has_sidebar and spec.sidebar:
        side_lines = _strip_markdown_asterisks_lines(spec.sidebar)
        L(slide, side_lines,
          left=Inches(7.0), width=Inches(2.4), top=body_top,
          size=Pt(S.FS_BODY_LG))


# ═══════════════════════════════════════════════════════════════════
#  7. STEPS (title left + 2x1 grid right)
# ═══════════════════════════════════════════════════════════════════

def render_steps(slide, spec: SlideSpec):
    H(slide, spec.title)
    body_top = _body_top_for_title(spec.title)

    items = spec.sections
    if not items:
        return

    n = len(items)
    mid = (n + 1) // 2
    left_items = items[:mid]
    right_items = items[mid:]

    gap = COL_GAP
    w = (CW - gap) / 2

    _steps_column(slide, left_items, 1, ML, body_top, w)
    _steps_column(slide, right_items, len(left_items) + 1, ML + w + gap, body_top, w)


# ═══════════════════════════════════════════════════════════════════
#  8. CASE (company info left + image right)
# ═══════════════════════════════════════════════════════════════════

def _case_body_block(
    slide,
    lines: list[str],
    left,
    top,
    width,
    height,
    tag_line: str | None = None,
):
    """Metrics, goals; optional resource tag (gray, small). «Бизнес-цели:» bold."""
    bx = slide.shapes.add_textbox(left, top, width, height)
    tf = bx.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    first = True
    for line in lines:
        if line == "":
            p = tf.add_paragraph()
            p.space_before = Pt(4)
            first = False
            continue
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        lbl = line.strip().lower().replace("**", "")
        is_goals_hdr = (
            "\u0431\u0438\u0437\u043d\u0435\u0441-\u0446\u0435\u043b\u0438" in lbl
            or lbl.startswith("goals:")
            or lbl.startswith("business goals")
        )
        txt = line.replace("**", "")
        _run(p, txt, S.FONT_BODY, Pt(S.FS_BODY), S.DARK, bold=is_goals_hdr)
        p.space_before = Pt(6)

    if tag_line and tag_line.strip():
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        _run(p, tag_line.strip(), S.FONT_BODY, Pt(S.FS_CASE_TAG),
             S.GRAY_TEXT, False)


def render_case(slide, spec: SlideSpec):
    fields = {it["key"]: it.get("value", "") for it in spec.items if it.get("key") != "_metric"}
    metrics = [it for it in spec.items if it.get("key") == "_metric"]

    company = fields.get("\u041a\u043e\u043c\u043f\u0430\u043d\u0438\u044f", fields.get("Company", spec.title))
    desc = fields.get("\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435", fields.get("Description", ""))

    year_cat = fields.get("\u0413\u043e\u0434", fields.get("Year", ""))
    category = fields.get("\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f", fields.get("Category", ""))
    if category:
        year_cat = f"{year_cat}. {category}" if year_cat else category

    title_text = f"{company}. {desc}" if desc else (company or spec.title)
    H(
        slide,
        title_text,
        size=Pt(S.FS_CASE_TITLE),
        width=CASE_TITLE_W,
        height=CASE_TITLE_H,
        left=ML,
        top=TOP_TITLE,
        anchor_top=True,
    )

    y_after_title = TOP_TITLE + CASE_TITLE_H
    if year_cat:
        y_after_title += CASE_SUBTITLE_GAP
        sb = slide.shapes.add_textbox(ML, y_after_title, CASE_TITLE_W, CASE_SUBTITLE_H)
        stf = sb.text_frame
        stf.word_wrap = True
        stf.vertical_anchor = MSO_ANCHOR.TOP
        _run(stf.paragraphs[0], year_cat, S.FONT_BODY, Pt(S.FS_CASE_SUBTITLE),
             S.GRAY_TEXT, False)
        y_after_title += CASE_SUBTITLE_H

    content_top = y_after_title + CASE_BODY_GAP

    goals = fields.get("\u0417\u0430\u0434\u0430\u0447\u0438", fields.get("\u0426\u0435\u043b\u0438", fields.get("Goals", "")))
    tags = fields.get("\u0422\u0435\u0433\u0438", fields.get("Tags", ""))

    text_w = CASE_TITLE_W
    lines = []
    for m in metrics:
        lines.append(f"{m['value']}  {m.get('label', '')}")
    if goals:
        if lines:
            lines.append("")
        lines.append("\u0411\u0438\u0437\u043d\u0435\u0441-\u0446\u0435\u043b\u0438:")
        lines.extend(goals.split("\n"))
    tag_line = tags.strip() if tags else None

    bottom_safe = Inches(0.38)
    body_h = SH - content_top - bottom_safe

    _case_body_block(slide, lines, ML, content_top, text_w, body_h, tag_line=tag_line)

    if spec.images:
        IMG(slide, spec.images[0], left=CASE_IMG_LEFT, top=CASE_IMG_TOP,
            width=CASE_IMG_W, height=CASE_IMG_H)
    else:
        _placeholder(slide, CASE_IMG_LEFT, CASE_IMG_TOP, CASE_IMG_W, CASE_IMG_H,
                     "Screenshot / Image")


# ═══════════════════════════════════════════════════════════════════
#  9. IMAGE
# ═══════════════════════════════════════════════════════════════════

def render_image(slide, spec: SlideSpec):
    H(slide, spec.title)
    body_top = _body_top_for_title(spec.title)
    if spec.images:
        n = len(spec.images)
        gap = Inches(0.2)
        w = (CW - gap * (n - 1)) / n
        for i, img in enumerate(spec.images[:3]):
            IMG(slide, img, left=ML + (w + gap) * i, top=body_top,
                width=w, height=BODY_H)
    else:
        IMG(slide, "", top=body_top)
    if spec.content:
        L(slide, [spec.content], top=Inches(5.0), size=Pt(S.FS_SMALL),
          color=S.GRAY_TEXT, height=Inches(0.4))


# ═══════════════════════════════════════════════════════════════════
# 10. GRID (card grid)
# ═══════════════════════════════════════════════════════════════════

def render_grid(slide, spec: SlideSpec):
    H(slide, spec.title)
    body_top = _body_top_for_title(spec.title)
    items = spec.sections
    n = len(items)
    if n == 0:
        return

    cols = spec.params.get("cols", 3)
    gap = Inches(0.2)
    w = (CW - gap * (cols - 1)) / cols
    row_h = Inches(1.1)

    for idx, item in enumerate(items):
        c = idx % cols
        r = idx // cols
        x = ML + c * (w + gap)
        y = body_top + r * (row_h + gap)

        lines = []
        if item.get("title"):
            lines.append(item["title"])
        if item.get("body"):
            lines.extend(item["body"].split("\n"))
        if lines:
            _col_block(slide, lines, x, y, w, first_bold=True)


# ═══════════════════════════════════════════════════════════════════
# 11. QUOTE
# ═══════════════════════════════════════════════════════════════════

def render_quote(slide, spec: SlideSpec):
    text = spec.content.strip()
    author = ""
    if "\n" in text:
        parts = text.rsplit("\n", 1)
        last = parts[-1].strip()
        if last.startswith("--") or last.startswith("\u2014"):
            author = last.lstrip("-\u2014 ").strip()
            text = parts[0].strip()

    BIG(slide, f"\u00ab{text}\u00bb", size=Pt(S.FS_SECTION),
        top=Inches(1.8), left=Inches(1.0), width=Inches(8.0),
        align=PP_ALIGN.CENTER)
    if author:
        L(slide, [author], top=Inches(3.8), left=Inches(1.0),
          width=Inches(8.0), size=Pt(S.FS_BODY), color=S.GRAY_TEXT,
          align=PP_ALIGN.CENTER, height=Inches(0.4))


# ═══════════════════════════════════════════════════════════════════
# 12. HIGHLIGHT (big number/fact)
# ═══════════════════════════════════════════════════════════════════

def render_highlight(slide, spec: SlideSpec):
    H(slide, spec.title)
    lines = spec.content.strip().split("\n")
    big = lines[0] if lines else ""
    sub = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
    big_size = Pt(S.FS_STAT_NUM)

    # Use stable geometry to avoid title/subtitle overlap regressions.
    big_top = Inches(2.05)
    big_height = Inches(1.0)
    BIG(
        slide,
        big,
        size=big_size,
        top=big_top,
        align=PP_ALIGN.CENTER,
        height=big_height,
    )
    if sub:
        sub_top = Inches(3.35)
        L(slide, sub.split("\n"), top=sub_top,
          size=Pt(S.FS_BODY), align=PP_ALIGN.CENTER, height=Inches(1.5))


# ═══════════════════════════════════════════════════════════════════
# 13. TIMELINE (table-based)
# ═══════════════════════════════════════════════════════════════════

def render_timeline(slide, spec: SlideSpec):
    H(slide, spec.title)
    body_top = _body_top_for_title(spec.title)
    items = spec.items
    if not items:
        return

    headers = ["\u042d\u0442\u0430\u043f", "\u0421\u0440\u043e\u043a", "\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435"]
    rows = []
    for item in items:
        rows.append([
            item.get("name", ""),
            item.get("duration", ""),
            item.get("description", ""),
        ])
    TBL(slide, headers, rows, cell_size=Pt(S.FS_BODY), top=body_top)


# ═══════════════════════════════════════════════════════════════════
# 14. CONTACTS
# ═══════════════════════════════════════════════════════════════════

def render_contacts(slide, spec: SlideSpec):
    fields = {it["key"].lower(): it["value"] for it in spec.items}

    email = fields.get("email", fields.get("e-mail", ""))
    phone = fields.get("phone", fields.get("\u0442\u0435\u043b\u0435\u0444\u043e\u043d", ""))
    city = fields.get("city", fields.get("\u0433\u043e\u0440\u043e\u0434", spec.title or ""))
    address = fields.get("address", fields.get("\u0430\u0434\u0440\u0435\u0441", ""))
    site = fields.get("site", fields.get("\u0441\u0430\u0439\u0442", ""))

    right_x = Inches(5.0)
    right_w = Inches(4.5)

    if email:
        H(slide, email, size=Pt(S.FS_CONTACTS_EMAIL),
          top=Inches(2.0), left=right_x, width=right_w)
    if phone:
        L(slide, [phone], top=Inches(3.2), left=right_x, width=right_w,
          size=Pt(S.FS_BODY), height=Inches(0.3))
    if site:
        L(slide, [site], top=Inches(3.5), left=right_x, width=right_w,
          size=Pt(S.FS_BODY), height=Inches(0.3))

    contact_lines = []
    if city:
        contact_lines.append(city)
    if address:
        contact_lines.append(address)
    if contact_lines:
        L(slide, contact_lines, top=Inches(4.0), left=right_x, width=right_w,
          size=Pt(S.FS_SMALL), height=Inches(1.0))


# ═══════════════════════════════════════════════════════════════════
# 15. TOC (table of contents — single list)
# ═══════════════════════════════════════════════════════════════════

def render_toc(slide, spec: SlideSpec):
    H(slide, spec.title)
    body_top = _body_top_for_title(spec.title)
    items = spec.items
    if not items:
        return

    lines = [f"{i + 1}.   {item.get('title', '')}" for i, item in enumerate(items)]

    n = len(lines)
    if n > 6:
        mid = (n + 1) // 2
        left_lines = lines[:mid]
        right_lines = lines[mid:]
        L(slide, left_lines, left=ML, width=COL_W, size=Pt(S.FS_TOC),
          font=S.FONT_BODY, spacing=Pt(14), top=body_top)
        L(slide, right_lines, left=ML + COL_W + COL_GAP, width=COL_W,
          size=Pt(S.FS_TOC), font=S.FONT_BODY, spacing=Pt(14), top=body_top)
    else:
        L(slide, lines, size=Pt(S.FS_TOC), font=S.FONT_BODY, spacing=Pt(14), top=body_top)


# ═══════════════════════════════════════════════════════════════════
# 16. TEAM (list of members)
# ═══════════════════════════════════════════════════════════════════

def render_team(slide, spec: SlideSpec):
    H(slide, spec.title)
    body_top = _body_top_for_title(spec.title)
    members = spec.sections
    if not members:
        return

    n = len(members)
    cols = min(n, 3)
    gap = Inches(0.3)
    w = (CW - gap * (cols - 1)) / cols
    row_h = Inches(2.0)

    for idx, member in enumerate(members):
        c = idx % cols
        r = idx // cols
        x = ML + c * (w + gap)
        y = body_top + r * (row_h + gap)

        name = member.get("title", "")
        body = member.get("body", "")

        img = ""
        body_lines = []
        import re
        for line in body.split("\n"):
            m_img = re.match(r"!\[.*?\]\((.+?)\)", line.strip())
            if m_img:
                img = m_img.group(1)
            else:
                body_lines.append(line)
        role = "\n".join(body_lines).strip()

        photo_h = Inches(1.1)
        if img:
            IMG(slide, img, left=x, top=y, width=w, height=photo_h)
        else:
            _placeholder(slide, x, y, w, photo_h, name or "Photo")

        lines = []
        if name:
            lines.append(name)
        if role:
            lines.append(role)
        if lines:
            L(slide, lines, left=x, top=y + photo_h + Inches(0.1),
              width=w, height=Inches(0.7), size=Pt(S.FS_BODY),
              spacing=Pt(4))
