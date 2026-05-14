"""
Brand tokens for Uplab presentations (v3 — simplified).

Only colors, fonts, font sizes, and layout names.
All geometry lives in helpers.py as fixed Inches values.
"""

from pptx.dml.color import RGBColor

# ── Colors ───────────────────────────────────────────────────────
DARK = RGBColor(0x21, 0x21, 0x21)
GRAY_TEXT = RGBColor(0x99, 0x99, 0x99)
GRAY_BG = RGBColor(0x5E, 0x5E, 0x5E)
BLUE = RGBColor(0x00, 0xA2, 0xFF)
MINT = RGBColor(0x16, 0xE7, 0xCF)
RED = RGBColor(0xFF, 0x64, 0x4E)
GREEN = RGBColor(0x61, 0xD8, 0x36)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

TABLE_HEADER_FILL = "F0F0F0"
PLACEHOLDER_FILL = "E8E8E8"

# ── Fonts ────────────────────────────────────────────────────────
FONT_HEADING = "Inter Medium"
FONT_BODY = "Inter"

# ── Font sizes (pt) ─────────────────────────────────────────────
# Section slides use FS_SECTION only; other slides use bumped sizes (+4 pt body scale).
FS_COVER = 31
FS_SECTION = 30
FS_PAGE_TITLE = 20
FS_BODY = 14
FS_BODY_LG = 17
FS_SMALL = 12
FS_STAT_NUM = 40
FS_STAT_LABEL = 12
FS_CASE_TITLE = 16
FS_CASE_SUBTITLE = 12
FS_CASE_NUM = 31
FS_CASE_DESC = 23
FS_CONTACTS_EMAIL = 44
FS_CONTACTS_LABEL = 14
FS_BREADCRUMB = 10
FS_SLIDE_NUM = 14
FS_TOC = 14
FS_CASE_TAG = 10

# ── Layout names (from templates) ───────────────────────────────
LAYOUT_BLANK = "BLANK"
LAYOUT_DEFAULT = "TITLE_AND_BODY"
LAYOUT_MINT = "mint"
LAYOUT_GRAY = "gray"

# ── Logo paths ───────────────────────────────────────────────────
LOGO_BLACK = "assets/logos/uplab_black.png"
LOGO_WHITE = "assets/logos/uplab_white.png"
