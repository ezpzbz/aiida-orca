#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "beautifulsoup4>=4.12",
#     "markdownify>=0.13",
#     "pyyaml>=6.0",
# ]
# ///
"""Extract ORCA inputs, prose (as markdown), and validation data from the
downloaded FACCTS ORCA tutorial pages under tutorials/<name>/<name>.html.

All output stays under tutorials/, which is git-ignored: the source pages
are FACCTS copyrighted content and this is a local dev reference corpus
only, never committed or shipped. See docs/orca61_hftype.md history and
.gitignore for context.

Usage:
    uv run scripts/extract_tutorials.py [tutorials_dir]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml
from bs4 import BeautifulSoup, Tag
from markdownify import markdownify as md

INPUT_HEURISTIC = re.compile(r"^\s*!|^\s*\*\s*xyz|^\s*%\w+.*\bend\b", re.IGNORECASE | re.MULTILINE)
ENERGY_HEURISTIC = re.compile(r"FINAL SINGLE POINT ENERGY|TOTAL ENERGY|FINAL ENERGY", re.IGNORECASE)
CITATION_RE = re.compile(r"\[\s*(?:,\s*)*\]")
NUMERIC_CITATION_RE = re.compile(r"\[\s*((?:\d+\s*,\s*)*\d+)\s*\]")
INTERNAL_LINK_RE = re.compile(r"!?\[([^\]\[]+)\]\((?!https?:)[^)]*\)")

NON_CALC_PAGES = {"install", "trouble_install", "opi", "ionic_crystal", "compound"}


def load_article(html_path: Path) -> Tag:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    article = soup.find("article", id="furo-main-content") or soup.find("article", role="main")
    if article is None:
        raise ValueError(f"no <article> found in {html_path}")
    for sel in article.select("nav, .headerlink, .related-pages, footer"):
        sel.decompose()
    return article


def page_title(html_path: Path) -> str:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    title = soup.find("title")
    text = title.get_text(strip=True) if title else html_path.stem
    return re.sub(r"\s*-\s*ORCA 6\.1 TUTORIALS\s*$", "", text)


def find_highlight_blocks(article: Tag) -> list[Tag]:
    return article.select('div[class^="highlight-"] pre')


def classify_and_extract(article: Tag) -> tuple[list[str], list[str]]:
    """Split highlighted <pre> blocks into (input_blocks, output_blocks) text lists,
    removing input blocks from the DOM so they don't pollute the prose markdown."""
    inputs, outputs = [], []
    for pre in find_highlight_blocks(article):
        text = pre.get_text()
        container = pre.find_parent("div", class_=re.compile(r"^highlight-"))
        if INPUT_HEURISTIC.search(text):
            inputs.append(text.strip("\n"))
            (container or pre).decompose()
        elif ENERGY_HEURISTIC.search(text):
            outputs.append(text.strip("\n"))
    return inputs, outputs


def extract_tables(article: Tag) -> list[dict]:
    """Best-effort table extraction: each <table> becomes a list of row dicts
    keyed by header cell text."""
    tables = []
    for table in article.find_all("table"):
        headers = [th.get_text(" ", strip=True) for th in table.select("thead th")]
        if not headers:
            first_row = table.find("tr")
            headers = [c.get_text(" ", strip=True) for c in first_row.find_all(["th", "td"])] if first_row else []
        rows = []
        body_rows = table.select("tbody tr") or table.find_all("tr")[1:]
        for tr in body_rows:
            cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
            if not cells:
                continue
            rows.append(dict(zip(headers, cells)) if headers else cells)
        if rows:
            tables.append({"headers": headers, "rows": rows})
    return tables


def article_to_markdown(article: Tag) -> str:
    markdown = md(str(article), heading_style="ATX", bullets="-", code_language="")
    markdown = CITATION_RE.sub("", markdown)
    markdown = NUMERIC_CITATION_RE.sub("", markdown)
    markdown = INTERNAL_LINK_RE.sub(r"\1", markdown)

    out, in_code, blank = [], False, 0
    for line in markdown.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
            out.append(line.rstrip())
            blank = 0
            continue
        if not in_code:
            line = re.sub(r"^ (?=\S)", "", line)
            line = re.sub(r" {2,}", " ", line)
            line = re.sub(r"\s+([.,;:])", r"\1", line)
            line = line.rstrip()
        if line.strip() == "" and not in_code:
            blank += 1
            if blank <= 1:
                out.append("")
        else:
            blank = 0
            out.append(line)
    return "\n".join(out).strip() + "\n"


def process_tutorial(tut_dir: Path) -> dict:
    name = tut_dir.name
    html_path = tut_dir / f"{name}.html"
    article = load_article(html_path)
    title = page_title(html_path)

    inputs, output_snippets = classify_and_extract(article)
    tables = extract_tables(article)
    markdown = article_to_markdown(article)

    inputs_dir = tut_dir / "inputs"
    if inputs:
        inputs_dir.mkdir(exist_ok=True)
        for i, text in enumerate(inputs, start=1):
            (inputs_dir / f"{name}_{i:02d}.inp").write_text(text.strip() + "\n", encoding="utf-8")

    (tut_dir / f"{name}.md").write_text(f"# {title}\n\n{markdown}", encoding="utf-8")

    expected = {"tables": tables, "output_snippets": output_snippets}
    with (tut_dir / "expected.yaml").open("w", encoding="utf-8") as fh:
        yaml.safe_dump(expected, fh, sort_keys=False, allow_unicode=True, width=100)

    return {
        "name": name,
        "title": title,
        "input_count": len(inputs),
        "table_count": len(tables),
        "output_snippet_count": len(output_snippets),
        "is_calc": name not in NON_CALC_PAGES and len(inputs) > 0,
    }


def main() -> None:
    tutorials_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "tutorials"
    if not tutorials_root.is_dir():
        raise SystemExit(f"tutorials directory not found: {tutorials_root}")

    manifest: list[dict] = []
    for tut_dir in sorted(p for p in tutorials_root.iterdir() if p.is_dir()):
        html_path = tut_dir / f"{tut_dir.name}.html"
        if not html_path.exists():
            continue
        entry = process_tutorial(tut_dir)
        manifest.append(entry)
        print(f"  {entry['name']:<20} inputs={entry['input_count']:<3} tables={entry['table_count']} "
              f"is_calc={entry['is_calc']}")

    manifest_path = tutorials_root / "manifest.yaml"
    with manifest_path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, allow_unicode=True, width=100)

    print(f"\nProcessed {len(manifest)} tutorials -> {manifest_path}")


if __name__ == "__main__":
    main()
