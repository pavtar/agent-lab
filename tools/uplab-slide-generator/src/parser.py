"""
Parse Markdown content files into a list of SlideSpec dicts.

Format:
  ---
  template: templates/Шаблон для презентации.pptx
  output: result.pptx
  breadcrumb: Optional persistent subtitle
  ---

  # slide_type
  ## Title
  content...
  <!-- note: speaker notes -->
"""

from __future__ import annotations

import re
import yaml
from dataclasses import dataclass, field


@dataclass
class SlideSpec:
    slide_type: str
    title: str = ""
    params: dict = field(default_factory=dict)
    content: str = ""
    note: str = ""
    sections: list[dict[str, str]] = field(default_factory=list)
    table_rows: list[list[str]] = field(default_factory=list)
    table_headers: list[str] = field(default_factory=list)
    sidebar: str = ""
    items: list[dict[str, str]] = field(default_factory=list)
    images: list[str] = field(default_factory=list)


def parse_file(path: str) -> tuple[dict, list[SlideSpec]]:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return parse_text(text)


def parse_text(text: str) -> tuple[dict, list[SlideSpec]]:
    frontmatter, body = _split_frontmatter(text)
    slides = _parse_slides(body)
    return frontmatter, slides


# ── Internal ─────────────────────────────────────────────────────

def _split_frontmatter(text: str) -> tuple[dict, str]:
    text = text.strip()
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1]) or {}
            return fm, parts[2].strip()
    return {}, text


def _parse_slides(body: str) -> list[SlideSpec]:
    chunks = re.split(r"^# ", body, flags=re.MULTILINE)
    slides = []
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        spec = _parse_one(chunk)
        if spec:
            slides.append(spec)
    return slides


def _parse_one(chunk: str) -> SlideSpec | None:
    lines = chunk.split("\n")
    slide_type, params = _parse_type_line(lines[0].strip())
    rest = "\n".join(lines[1:]).strip()

    note = _extract_note(rest)
    rest = re.sub(r"<!--\s*note:.*?-->", "", rest, flags=re.DOTALL).strip()

    title, content = _extract_title(rest)

    images = [path for _, path in re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", content)]
    content_clean = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", content).strip()

    spec = SlideSpec(
        slide_type=slide_type, title=title, params=params,
        content=content_clean, note=note, images=images,
    )

    if slide_type in ("columns", "pricing"):
        spec.sections = _parse_sections(content_clean)
    elif slide_type == "steps":
        spec.sections = _parse_steps(content_clean)
    elif slide_type == "stats":
        spec.items = _parse_stats(content_clean)
    elif slide_type in ("table", "comparison"):
        spec.table_headers, spec.table_rows, spec.sidebar = _parse_table(content_clean)
    elif slide_type == "timeline":
        spec.items = _parse_timeline(content_clean)
    elif slide_type == "case":
        spec.items = _parse_case(content_clean)
    elif slide_type == "grid":
        spec.sections = _parse_sections(content_clean)
    elif slide_type == "contacts":
        spec.items = _parse_contacts(content_clean)
    elif slide_type == "toc":
        spec.items = _parse_toc(content_clean)
    elif slide_type == "team":
        spec.sections = _parse_sections(content_clean)

    return spec


def _parse_type_line(line: str) -> tuple[str, dict]:
    parts = line.split(":", 1)
    stype = parts[0].strip().lower()
    params: dict = {}
    if len(parts) > 1:
        val = parts[1].strip()
        if val.isdigit():
            params["cols"] = int(val)
        elif val == "sidebar":
            params["sidebar"] = True
        else:
            params["variant"] = val
    return stype, params


def _extract_note(text: str) -> str:
    m = re.search(r"<!--\s*note:\s*(.*?)\s*-->", text, re.DOTALL)
    return m.group(1).strip() if m else ""


def _extract_title(text: str) -> tuple[str, str]:
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("## "):
            title = line[3:].strip()
            content = "\n".join(lines[i + 1:]).strip()
            return title, content
    return "", text


def _parse_sections(text: str) -> list[dict[str, str]]:
    """Split by ### headers."""
    parts = re.split(r"^### ", text, flags=re.MULTILINE)
    result = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lines = part.split("\n", 1)
        result.append({
            "title": lines[0].strip(),
            "body": lines[1].strip() if len(lines) > 1 else "",
        })
    return result


def _parse_steps(text: str) -> list[dict[str, str]]:
    """Steps: try ### headers first, fall back to numbered list `1. Title | Body`."""
    if "### " in text:
        return _parse_sections(text)

    items = []
    for line in text.split("\n"):
        m = re.match(r"^\d+\.\s*(.+)", line.strip())
        if m:
            parts = m.group(1).split("|", 1)
            items.append({
                "title": parts[0].strip(),
                "body": parts[1].strip() if len(parts) > 1 else "",
            })
    return items


def _parse_stats(text: str) -> list[dict[str, str]]:
    """Parse `- VALUE | label` lines and optional `> footer`."""
    items = []
    footer = ""
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith(">"):
            footer = line.lstrip("> ").strip()
            continue
        if (line.startswith("- ") or line.startswith("* ")) and "|" in line:
            val, label = line[2:].split("|", 1)
            items.append({"value": val.strip(), "label": label.strip()})
    if footer:
        items.append({"_footer": footer})
    return items


def _parse_timeline(text: str) -> list[dict[str, str]]:
    """Parse `1. Name | Duration | Description`."""
    items = []
    for line in text.split("\n"):
        m = re.match(r"^\d+\.\s*(.+)", line.strip())
        if m:
            parts = m.group(1).split("|")
            item = {"name": parts[0].strip()}
            if len(parts) > 1:
                item["duration"] = parts[1].strip()
            if len(parts) > 2:
                item["description"] = parts[2].strip()
            items.append(item)
    return items


def _parse_table(text: str) -> tuple[list[str], list[list[str]], str]:
    """Markdown table + optional `---sidebar---` block."""
    sidebar = ""
    main = text
    if "---sidebar---" in text:
        main, sidebar = text.split("---sidebar---", 1)
        main = main.strip()
        sidebar = sidebar.strip()

    headers: list[str] = []
    rows: list[list[str]] = []
    for line in main.split("\n"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if all(set(c) <= {"-", " ", ":"} for c in cells):
            continue
        if not headers:
            headers = cells
        else:
            rows.append(cells)
    return headers, rows, sidebar


def _parse_case(text: str) -> list[dict[str, str]]:
    """Parse **Key:** Value pairs and `- VALUE | label` metrics."""
    items: list[dict[str, str]] = []
    cur_key = None
    cur_lines: list[str] = []

    def _flush():
        nonlocal cur_key, cur_lines
        if cur_key:
            items.append({"key": cur_key, "value": "\n".join(cur_lines).strip()})
        cur_key = None
        cur_lines = []

    for line in text.split("\n"):
        s = line.strip()
        m = re.match(r"^\*\*(.+?):\*\*\s*(.*)", s)
        if m:
            _flush()
            cur_key = m.group(1).strip()
            v = m.group(2).strip()
            if v:
                cur_lines = [v]
            continue

        if s.startswith("- ") and "|" in s:
            _flush()
            val, label = s[2:].split("|", 1)
            items.append({"key": "_metric", "value": val.strip(), "label": label.strip()})
            continue

        if cur_key:
            cur_lines.append(s)

    _flush()
    return items


def _parse_toc(text: str) -> list[dict[str, str]]:
    """Parse numbered list for table of contents: `1. Title`."""
    items = []
    for line in text.split("\n"):
        m = re.match(r"^\d+\.\s*(.+)", line.strip())
        if m:
            items.append({"title": m.group(1).strip()})
    return items


def _parse_contacts(text: str) -> list[dict[str, str]]:
    """Parse **Label:** value lines."""
    items = []
    for line in text.split("\n"):
        m = re.match(r"^\*\*(.+?):\*\*\s*(.*)", line.strip())
        if m:
            items.append({"key": m.group(1).strip(), "value": m.group(2).strip()})
    return items
