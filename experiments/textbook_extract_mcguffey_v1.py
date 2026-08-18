#!/usr/bin/env python
# -*- coding: ascii -*-
"""
Layer-1 TEXTBOOK INGESTION EXTRACTOR (path 5) -- BUILD-TIME PLUMBING.

Turns a real graded-reader PDF (McGuffey First Reader) into the structured
"vision-ready" ingestion format so the substrate encoders can consume it and
nothing is thrown away:
  - TEXT   : per-page reading-order text stream + document-order concatenation
             (Gutenberg license header/footer boilerplate stripped)
  - FIGURES: each embedded image extracted (pristine bytes) as PNG + page + bbox
  - CAPTION/ASSOCIATION: nearby text blocks linked to each figure by same-column
             vertical proximity (primer layout = illustration above/beside lesson)
  - LAYOUT : structured JSON, per page = {page, text, figures:[{img_path,bbox,
             nearby_text}]}

This is a TOOL, not a capability-claim. Glass-box invariant is on RUNTIME
reasoning, not on this parser (same policy category as KB-ingest).
LOCAL only. ASCII-only. Uses default `python` (fitz/PyMuPDF is there).

Run:
  python experiments/textbook_extract_mcguffey_v1.py --pdf <path> [--outdir <dir>]
"""
import argparse
import io
import json
import os
import sys

try:
    import fitz  # PyMuPDF
except Exception as e:  # pragma: no cover
    sys.stderr.write("FATAL: PyMuPDF (fitz) not importable in this python: %s\n" % e)
    sys.exit(2)

try:
    from PIL import Image
    HAVE_PIL = True
except Exception:
    HAVE_PIL = False

START_MARK = "START OF THIS PROJECT"
END_MARK = "END OF THIS PROJECT"


def sanitize(s):
    """ASCII-safe: replace the smart-quote/apostrophe artifacts seen in this
    Gutenberg text (McGuffey s -> McGuffey's) and drop non-ASCII bytes."""
    if s is None:
        return ""
    # common cp1252-ish substitutions that survive as U+FFFD-like glyphs
    # (built via chr() so this source file stays pure ASCII)
    repl = {
        chr(0x2019): "'", chr(0x2018): "'", chr(0x201C): '"', chr(0x201D): '"',
        chr(0x2014): "--", chr(0x2013): "-", chr(0x2026): "...",
        chr(0xFFFD): "'", chr(0x00A0): " ",
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    return s.encode("ascii", "ignore").decode("ascii")


def column_reading_order(page):
    """Return (concatenated_text, list_of_text_blocks).

    Reading order for the two-column primer spread: left column
    (x0 < page_mid) top-to-bottom first, then right column. Each block is
    {bbox:(x0,y0,x1,y1), text:str, col:'L'|'R'}.
    """
    mid = page.rect.width / 2.0
    d = page.get_text("dict")
    blocks = []
    for b in d.get("blocks", []):
        if b.get("type", 1) != 0:
            continue
        txt = ""
        for ln in b.get("lines", []):
            for sp in ln.get("spans", []):
                txt += sp.get("text", "")
            txt += "\n"
        txt = sanitize(txt).strip()
        if not txt:
            continue
        x0, y0, x1, y1 = b["bbox"]
        blocks.append({
            "bbox": [round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)],
            "text": txt,
            "col": "L" if x0 < mid else "R",
        })
    left = sorted([b for b in blocks if b["col"] == "L"], key=lambda b: b["bbox"][1])
    right = sorted([b for b in blocks if b["col"] == "R"], key=lambda b: b["bbox"][1])
    ordered = left + right
    concat = "\n".join(b["text"] for b in ordered)
    return concat, ordered


def strip_boilerplate(pno, text, n_pages):
    """Strip Gutenberg license header (page 0 before START) / footer
    (page-with-END after END; pure-license tail pages dropped by caller)."""
    if pno == 0 and START_MARK in text:
        idx = text.find(START_MARK)
        nl = text.find("\n", idx)
        return text[nl + 1:].strip() if nl != -1 else ""
    if END_MARK in text:
        idx = text.find(END_MARK)
        # keep content BEFORE the end marker line
        ls = text.rfind("\n", 0, idx)
        return text[:ls].strip() if ls != -1 else ""
    return text


def nearby_text(img_bbox, blocks, v_gap=140.0):
    """Associate figure with nearby lesson text: same-column blocks whose
    vertical distance to the image bbox is within v_gap points, closest first.
    Returns list of {text, bbox, rel} where rel in {above,below,overlap}."""
    ix0, iy0, ix1, iy1 = img_bbox
    imid = (ix0 + ix1) / 2.0
    out = []
    for b in blocks:
        bx0, by0, bx1, by1 = b["bbox"]
        # require horizontal overlap OR block center in the image's column band
        x_overlap = not (bx1 < ix0 - 20 or bx0 > ix1 + 20)
        bmid = (bx0 + bx1) / 2.0
        same_band = abs(bmid - imid) < (ix1 - ix0)  # within one image-width
        if not (x_overlap or same_band):
            continue
        if by1 <= iy0:          # block fully above image
            dist = iy0 - by1
            rel = "above"
        elif by0 >= iy1:        # block fully below image
            dist = by0 - iy1
            rel = "below"
        else:                   # vertical overlap
            dist = 0.0
            rel = "overlap"
        if dist <= v_gap:
            out.append((dist, {"text": b["text"], "bbox": b["bbox"], "rel": rel}))
    out.sort(key=lambda t: t[0])
    return [o[1] for o in out]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--outdir", default="data/exp_textbook_extract_mcguffey_v1")
    ap.add_argument("--repo", default=".")
    args = ap.parse_args()

    outdir = os.path.abspath(os.path.join(args.repo, args.outdir))
    figdir = os.path.join(outdir, "figures")
    sampledir = os.path.join(outdir, "sample")
    os.makedirs(figdir, exist_ok=True)
    os.makedirs(sampledir, exist_ok=True)

    doc = fitz.open(args.pdf)
    n_pages = doc.page_count

    pages_out = []
    doc_stream = []
    fig_count = 0
    seen_xref = {}  # xref -> first png path (dedupe repeated embeds)
    content_ended = False  # once the Gutenberg END marker is passed, tail = license

    for pno in range(n_pages):
        page = doc[pno]
        raw_text, blocks = column_reading_order(page)

        if content_ended:
            text = ""
        elif END_MARK in raw_text or "End of the Project Gutenberg" in raw_text:
            # drop this whole page's text (End-of-ebook line + license start)
            # and everything after it
            content_ended = True
            text = ""
        else:
            text = strip_boilerplate(pno, raw_text, n_pages)

        # Figures on this page.
        # NOTE: this McGuffey PDF embeds each lesson's diacritic pronunciation
        # word-list as a raster strip AND renders pictorial illustrations as
        # rasters too. We classify by bbox height (word-list strips are short).
        # We save PLACEMENT-FAITHFUL crops via get_pixmap(clip=bbox): the raw
        # embedded bytes (extract_image) are stored without the page transform
        # and come out mirrored/rotated for this document, so pixmap render is
        # the correct, upright, bbox-accurate crop.
        figs = []
        for img in page.get_images(full=True):
            xref = img[0]
            rects = page.get_image_rects(xref)
            if not rects:
                continue
            rect = rects[0]
            bbox = [round(v, 1) for v in rect]
            height = rect.y1 - rect.y0
            kind = "illustration" if height > 120 else "wordlist_strip"
            png_name = "p%03d_x%d.png" % (pno, xref)
            png_path = os.path.join(figdir, png_name)
            if xref in seen_xref:
                png_path = seen_xref[xref]
            else:
                pix = page.get_pixmap(clip=rect, dpi=200)
                pix.save(png_path)
                seen_xref[xref] = png_path
            fig_count += 1
            figs.append({
                "img_path": os.path.relpath(png_path, outdir).replace("\\", "/"),
                "xref": xref,
                "kind": kind,
                "bbox": bbox,
                "nearby_text": nearby_text(bbox, blocks),
            })

        pages_out.append({
            "page": pno,
            "text": text,
            "figures": figs,
        })
        if text:
            doc_stream.append(text)

    n_illus = sum(1 for p in pages_out for f in p["figures"] if f["kind"] == "illustration")
    n_wl = sum(1 for p in pages_out for f in p["figures"] if f["kind"] == "wordlist_strip")
    n_text_pages = sum(1 for p in pages_out if p["text"])

    # write per-page structured JSON
    struct_path = os.path.join(outdir, "mcguffey_first_structured.json")
    with open(struct_path, "w") as fh:
        json.dump({
            "source_pdf": os.path.basename(args.pdf),
            "n_pages": n_pages,
            "n_text_pages": n_text_pages,
            "n_figures": fig_count,
            "n_unique_figures": len(seen_xref),
            "n_illustrations": n_illus,
            "n_wordlist_strips": n_wl,
            "figure_kind_note": "illustration=pictorial line-art (bbox h>120pt); "
                                "wordlist_strip=diacritic pronunciation new-words list "
                                "embedded as raster (also present as ASCII text-box in text layer)",
            "pages": pages_out,
        }, fh, indent=1)

    # document-order text stream
    stream_path = os.path.join(outdir, "mcguffey_first_document_order.txt")
    with open(stream_path, "w") as fh:
        fh.write("\n\n".join(doc_stream))

    print("STRUCT_JSON=%s" % struct_path)
    print("TEXT_STREAM=%s" % stream_path)
    print("PAGES=%d TEXT_PAGES=%d" % (n_pages, n_text_pages))
    print("FIGURES_TOTAL=%d UNIQUE=%d ILLUSTRATIONS=%d WORDLIST_STRIPS=%d"
          % (fig_count, len(seen_xref), n_illus, n_wl))
    return pages_out, outdir, figdir, sampledir


if __name__ == "__main__":
    main()
