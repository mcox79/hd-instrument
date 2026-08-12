# -*- coding: utf-8 -*-
"""
Convert OpenStax "Concepts of Biology" CNXML modules to clean plain text,
using the collection.xml ordering/heading structure, and concatenate into
one corpus file with lightweight heading markers.

No LLM / torch / spaCy used -- pure stdlib XML parsing + regex whitespace
cleanup. This is deterministic markup-stripping, not model-based cleaning.
"""
import argparse
import json
import os
import re
import xml.etree.ElementTree as ET

# Minimally parameterized (2026-08-12) so sibling OpenStax CNXML titles can reuse this cleaner
# without copy/pasting it. Defaults are unchanged from the original hardcoded values (BASE, and
# STRUCT now pointing at the committed raw/collection_structure.json instead of a dead session
# scratchpad path) -- running with no args reproduces the original "Concepts of Biology" output
# bit-identically (verified: diff against the committed cleaned/concepts_biology.clean.txt).
BASE = r"d:/AI/hd-instrument/data/corpora/textbook_concepts_biology"
MOD_DIR = os.path.join(BASE, "raw", "modules")
STRUCT = os.path.join(BASE, "raw", "collection_structure.json")
OUT_TXT = os.path.join(BASE, "cleaned", "concepts_biology.clean.txt")
OUT_STATS = os.path.join(BASE, "cleaned", "module_report.json")

SKIP_TAGS = {"media", "image", "exercise", "problem", "solution", "equation"}
# any tag with an 'm:' style local name that maps to mathml namespace -- we strip by namespace below too.

WS_RE = re.compile(r"[ \t\f\v]+")
NL_RE = re.compile(r"\n{3,}")


def strip_ns(tag):
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def is_mathml(elem):
    return elem.tag.startswith("{http://www.w3.org/1998/Math/MathML}")


def norm(text):
    if not text:
        return ""
    text = text.replace(" ", " ")
    text = WS_RE.sub(" ", text)
    return text.strip()


def inline_text(elem):
    """Concatenate visible text of an element and its descendants, honoring
    XML text/tail semantics. Skips media/image/equation/mathml content but
    keeps their tails. Footnotes are rendered as a parenthetical aside."""
    parts = []
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        tag = strip_ns(child.tag)
        if is_mathml(child) or tag in SKIP_TAGS:
            pass
        elif tag == "footnote":
            txt = norm(inline_text(child))
            if txt:
                parts.append(f" ({txt}) ")
        elif tag == "newline":
            parts.append("\n")
        else:
            parts.append(inline_text(child))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


def direct_child(elem, tag_name):
    for c in elem:
        if strip_ns(c.tag) == tag_name:
            return c
    return None


def emit_heading(blocks, level, text):
    text = norm(text)
    if text:
        blocks.append(("#" * min(level, 6)) + " " + text)


def emit_para(blocks, text):
    text = norm(text)
    if text:
        blocks.append(text)


def emit_bullet(blocks, text):
    text = norm(text)
    if text:
        blocks.append("- " + text)


def walk_children(container, level, blocks):
    for child in container:
        tag = strip_ns(child.tag)
        if is_mathml(child) or tag in SKIP_TAGS:
            continue

        if tag == "title":
            # handled by the parent that owns this container (section/note/
            # table/figure/glossary/document); skip here to avoid double-emit
            continue

        elif tag == "section":
            t = direct_child(child, "title")
            if t is not None:
                emit_heading(blocks, level, inline_text(t))
            walk_children(child, level + 1, blocks)

        elif tag == "para":
            emit_para(blocks, inline_text(child))

        elif tag == "list":
            for item in child:
                if strip_ns(item.tag) == "item":
                    emit_bullet(blocks, inline_text(item))
                else:
                    walk_children_single(item, level, blocks)

        elif tag == "definition":
            term_el = direct_child(child, "term")
            meaning_el = direct_child(child, "meaning")
            term_txt = norm(inline_text(term_el)) if term_el is not None else ""
            meaning_txt = norm(inline_text(meaning_el)) if meaning_el is not None else ""
            if term_txt or meaning_txt:
                blocks.append(f"{term_txt}: {meaning_txt}".strip(": ").strip())

        elif tag == "glossary":
            emit_heading(blocks, level, "Glossary")
            walk_children(child, level + 1, blocks)

        elif tag in ("note",):
            t = direct_child(child, "title")
            label_el = direct_child(child, "label")
            heading_txt = None
            if t is not None:
                heading_txt = inline_text(t)
            elif label_el is not None:
                heading_txt = inline_text(label_el)
            if heading_txt:
                emit_heading(blocks, level + 1, heading_txt)
            walk_children(child, level + 1, blocks)

        elif tag in ("figure", "subfigure"):
            walk_children(child, level, blocks)

        elif tag == "caption":
            emit_para(blocks, inline_text(child))

        elif tag == "table":
            t = direct_child(child, "title")
            if t is not None:
                emit_heading(blocks, level, inline_text(t))
            # walk tgroup -> thead/tbody -> row -> entry
            for tgroup in child:
                if strip_ns(tgroup.tag) != "tgroup":
                    continue
                for part in tgroup:
                    ptag = strip_ns(part.tag)
                    if ptag not in ("thead", "tbody"):
                        continue
                    for row in part:
                        if strip_ns(row.tag) != "row":
                            continue
                        cells = [norm(inline_text(e)) for e in row if strip_ns(e.tag) == "entry"]
                        cells = [c for c in cells if c]
                        if cells:
                            blocks.append(" | ".join(cells))

        elif tag == "label":
            txt = norm(inline_text(child))
            if txt:
                blocks.append(f"[{txt}]")

        elif tag in ("item",):
            emit_bullet(blocks, inline_text(child))

        else:
            # Unknown/generic container (e.g. 'content', wrapper tags) --
            # recurse so nested paragraphs aren't silently dropped.
            walk_children(child, level, blocks)


def walk_children_single(elem, level, blocks):
    """Handle a single element the same way walk_children would dispatch it
    (used for non-'item' children occasionally found inside <list>)."""
    fake_container = list([elem])

    class _C:
        def __iter__(self):
            return iter(fake_container)

    walk_children(_C(), level, blocks)


def process_module(mod_id, mod_dir=None):
    path = os.path.join(mod_dir if mod_dir is not None else MOD_DIR, mod_id + ".cnxml")
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        return None, f"PARSE_ERROR: {e}"
    root = tree.getroot()

    blocks = []
    title_el = direct_child(root, "title")
    module_title = inline_text(title_el) if title_el is not None else mod_id
    content = direct_child(root, "content")
    if content is None:
        return None, "NO_CONTENT"

    walk_children(content, 6, blocks)

    # <glossary> is a sibling of <content> under <document> in per-module
    # CNXML (not nested inside content) -- process it separately if present.
    glossary = direct_child(root, "glossary")
    if glossary is not None:
        emit_heading(blocks, 6, "Glossary")
        walk_children(glossary, 6, blocks)

    return {"title": norm(module_title), "blocks": blocks}, None


def main(struct_path=None, mod_dir=None, out_txt=None, out_stats=None):
    struct_path = struct_path or STRUCT
    mod_dir = mod_dir or MOD_DIR
    out_txt = out_txt or OUT_TXT
    out_stats = out_stats or OUT_STATS

    with open(struct_path, encoding="utf-8") as f:
        struct = json.load(f)

    book_title = struct["title"]
    items = struct["items"]

    out_lines = []
    out_lines.append("# " + book_title)
    out_lines.append("")

    report = {"book_title": book_title, "modules": [], "errors": []}

    for it in items:
        if it["type"] == "heading":
            emit_heading(out_lines, it["level"] + 1, it["title"])
            out_lines.append("")
        elif it["type"] == "module":
            mid = it["id"]
            result, err = process_module(mid, mod_dir)
            if err:
                report["errors"].append({"module": mid, "error": err})
                continue
            out_lines.append("##### " + result["title"])
            out_lines.append("")
            for b in result["blocks"]:
                out_lines.append(b)
                out_lines.append("")
            report["modules"].append({"id": mid, "title": result["title"], "n_blocks": len(result["blocks"])})

    text = "\n".join(out_lines)
    # Drop empty-parenthetical artifacts left behind by CNXML <link
    # target-id="..."/> figure references (the renderer normally fills these
    # with an auto-numbered "Figure X.Y"; as plain text there is no visible
    # link text, so they collapse to bare "()" -- strip them, then tidy the
    # resulting stray whitespace/punctuation.
    text = re.sub(r"\s*\(\s*\)", "", text)
    # Strip photo/figure credit boilerplate ("(credit: modification of work
    # by NASA)", "(credit a: ..., credit b: ...)") -- captioning metadata,
    # not expository content.
    text = re.sub(r"\s*\(credit[^)]*\)", "", text)
    text = re.sub(r"[ \t]+([.,;:])", r"\1", text)
    text = NL_RE.sub("\n\n", text)

    os.makedirs(os.path.dirname(out_txt), exist_ok=True)
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(text)

    with open(out_stats, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("wrote", out_txt, "chars=", len(text))
    print("modules processed:", len(report["modules"]), "errors:", len(report["errors"]))
    if report["errors"]:
        for e in report["errors"]:
            print("  ERR", e)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--struct", default=None, help="path to collection_structure.json (default: biology)")
    ap.add_argument("--mod-dir", default=None, help="dir of raw <id>.cnxml module files (default: biology)")
    ap.add_argument("--out-txt", default=None, help="output cleaned .txt path (default: biology)")
    ap.add_argument("--out-stats", default=None, help="output module_report.json path (default: biology)")
    args = ap.parse_args()
    main(args.struct, args.mod_dir, args.out_txt, args.out_stats)
