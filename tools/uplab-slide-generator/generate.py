#!/usr/bin/env python3
"""
Uplab Slide Generator — CLI entry point.

Usage:
    python generate.py content.md
    python generate.py content.md -t templates/MyTemplate.pptx -o result.pptx
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.parser import parse_file
from src.engine import generate


def main():
    ap = argparse.ArgumentParser(
        description="Generate Uplab-branded PPTX presentations from Markdown.",
    )
    ap.add_argument("input_md", help="Path to the Markdown content file")
    ap.add_argument(
        "-t", "--template",
        default=os.path.join("templates", "Шаблон для презентации.pptx"),
        help="Path to the PPTX template (default: templates/Шаблон для презентации.pptx)",
    )
    ap.add_argument(
        "-o", "--output",
        default="output.pptx",
        help="Output PPTX path (default: output.pptx)",
    )
    args = ap.parse_args()

    if not os.path.isfile(args.input_md):
        print(f"Error: markdown file not found: {args.input_md}")
        sys.exit(1)
    if not os.path.isfile(args.template):
        print(f"Error: template not found: {args.template}")
        sys.exit(1)

    frontmatter, slides = parse_file(args.input_md)

    cli_template_explicit = "-t" in sys.argv or "--template" in sys.argv
    cli_output_explicit = "-o" in sys.argv or "--output" in sys.argv

    template = args.template if cli_template_explicit else frontmatter.get("template", args.template)
    output = args.output if cli_output_explicit else frontmatter.get("output", args.output)
    breadcrumb = frontmatter.get("breadcrumb", "")

    if not os.path.isfile(template):
        template = args.template

    print(f"Template : {template}")
    print(f"Slides   : {len(slides)}")
    print(f"Output   : {output}")

    result = generate(template, slides, output, breadcrumb=breadcrumb)

    print(f"Done -> {result}")


if __name__ == "__main__":
    main()
