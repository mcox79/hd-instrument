"""Extract + clean Simple English Wikipedia into a training-ready line corpus.

Streams the bz2 XML dump (stdlib bz2 + xml.etree.iterparse, constant memory),
strips wiki markup with mwparserfromhell, then applies the SAME cleaning /
quality gate / sentence-split / dedup / ASCII-safe pipeline as
tools/build_breadth_corpus_v1.py so the output is drop-in for
experiments/exp_scale_meaning_learn_arc_heldout_v2.py (one line = one sentence,
UTF-8/ASCII, mixed case, punctuation intact).

Run with the repo .venv (Python 3.12 + mwparserfromhell):
  .venv/Scripts/python.exe tools/build_simplewiki_clean_v1.py

Input:  data/corpora/simplewiki/simplewiki-latest-pages-articles.xml.bz2
Output: data/corpora/simplewiki/simplewiki_clean_v1.txt (+ stats.json)
"""
import bz2
import json
import os
import re
import sys
import unicodedata

try:
    import mwparserfromhell
except ImportError:
    print("ERROR: mwparserfromhell not available; run with repo .venv", file=sys.stderr)
    sys.exit(1)

from xml.etree.ElementTree import iterparse

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(_REPO, "data")
SW_DIR = os.path.join(DATA, "corpora", "simplewiki")
DUMP = os.path.join(SW_DIR, "simplewiki-latest-pages-articles.xml.bz2")
OUT_TXT = os.path.join(SW_DIR, "simplewiki_clean_v1.txt")
OUT_STATS = os.path.join(SW_DIR, "stats.json")

# ---- pipeline reused verbatim from build_breadth_corpus_v1.py ----
_WORD_RE = re.compile(r"[a-z]+")
_CITATION_RE = re.compile(r"\b\d+\s*\(\s*\d+\s*\)\s*:\s*\d+")
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"“])")
_WS_RE = re.compile(r"\s+")
_ASCII_MAP = {
    0x2018: "'", 0x2019: "'", 0x201A: "'", 0x201B: "'",
    0x201C: '"', 0x201D: '"', 0x201E: '"', 0x201F: '"',
    0x2013: "-", 0x2014: "-", 0x2015: "-", 0x2212: "-",
    0x2026: "...", 0x00A0: " ", 0x2009: " ", 0x200B: "",
    0x00AB: '"', 0x00BB: '"',
}


def to_ascii(s):
    s = s.translate(_ASCII_MAP)
    s = unicodedata.normalize("NFKD", s)
    return s.encode("ascii", "ignore").decode("ascii")


def quality_ok(line, words):
    if len(words) < 4:
        return False
    n_alpha = sum(len(w) for w in words)
    n_all = len(line)
    if n_all > 0 and (n_alpha / float(n_all)) < 0.55:
        return False
    if _CITATION_RE.search(line):
        return False
    return True


def clean_line(raw):
    return _WS_RE.sub(" ", to_ascii(raw)).strip()


def sentences_from_text(text):
    text = text.replace("\r", " ")
    for p in (p.strip() for p in text.split("\n") if p.strip()):
        for s in _SENT_SPLIT_RE.split(p):
            s = s.strip()
            if s:
                yield s


# ---- wiki-markup specific stripping ----
# lines that are clearly non-prose residue after markup strip
_BAD_PREFIX = ("|", "!", "{", "}", "*", "#", ":", ";", "=", "[[", "http")
_REDIRECT_RE = re.compile(r"^\s*#redirect", re.IGNORECASE)
_FILE_LINK_RE = re.compile(r"\[\[(?:File|Image|Category):[^\]]*\]\]", re.IGNORECASE)
_REF_RE = re.compile(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>", re.IGNORECASE | re.DOTALL)
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")
# section headers we don't want prose from
_SKIP_SECTION_RE = re.compile(
    r"^\s*==+\s*(references|other websites|related pages|sources|external links|"
    r"further reading|bibliography|notes|see also|gallery)\s*==+\s*$", re.IGNORECASE)


def wikitext_to_text(wikitext):
    """Strip markup -> plain text. Cuts the article at the first boilerplate
    section (References/External links/etc.) so we keep only body prose."""
    wikitext = _COMMENT_RE.sub("", wikitext)
    wikitext = _REF_RE.sub("", wikitext)
    wikitext = _FILE_LINK_RE.sub("", wikitext)
    # cut at first boilerplate section header
    out_lines = []
    for ln in wikitext.split("\n"):
        if _SKIP_SECTION_RE.match(ln):
            break
        out_lines.append(ln)
    wikitext = "\n".join(out_lines)
    try:
        code = mwparserfromhell.parse(wikitext)
        text = code.strip_code(normalize=True, collapse=True)
    except Exception:
        text = wikitext
    text = _TAG_RE.sub("", text)
    # drop residual markup lines
    keep = []
    for ln in text.split("\n"):
        s = ln.strip()
        if not s:
            keep.append("")
            continue
        if s.startswith(_BAD_PREFIX):
            continue
        keep.append(s)
    return "\n".join(keep)


MAX_WIKITEXT_CHARS = 500000  # skip pathological mega-pages (dumps/lists) that can hang the parser


def iter_pages(dump_path):
    """Yield article wikitext for main-namespace, non-redirect pages.

    Uses start+end events so we can hold the ROOT element and clear it after
    every page -- without this, xml.etree.iterparse accumulates every processed
    <page> shell under the root for the life of the parse (a ~1.5GB-XML memory
    leak that OOMs partway through). elem.clear() alone is NOT enough."""
    with bz2.open(dump_path, "rb") as fh:
        context = iterparse(fh, events=("start", "end"))
        _, root = next(context)  # first start event -> the <mediawiki> root
        for event, elem in context:
            if event != "end":
                continue
            tag = elem.tag.rsplit("}", 1)[-1]
            if tag != "page":
                continue
            ns = title = None
            text = ""
            is_redirect = False
            for child in elem:
                ctag = child.tag.rsplit("}", 1)[-1]
                if ctag == "ns":
                    ns = child.text
                elif ctag == "title":
                    title = child.text
                elif ctag == "redirect":
                    is_redirect = True
                elif ctag == "revision":
                    for rc in child:
                        if rc.tag.rsplit("}", 1)[-1] == "text":
                            text = rc.text or ""
            if ns == "0" and not is_redirect and text and len(text) <= MAX_WIKITEXT_CHARS:
                yield title, text
            elem.clear()
            root.clear()  # drop the processed page shell from the root's child list


def main():
    if not os.path.exists(DUMP):
        print(f"ERROR: dump not found at {DUMP}", file=sys.stderr)
        sys.exit(1)
    os.makedirs(SW_DIR, exist_ok=True)
    seen = set()
    SEEN_CAP = 4_000_000  # bound the cross-page exact-dup set so it can't OOM
    stats = dict(pages_total=0, pages_used=0, redirects_skipped=0,
                 lines=0, tokens=0, dropped_quality=0, dropped_dup=0)
    with open(OUT_TXT, "w", encoding="utf-8", newline="\n") as out:
        for title, wikitext in iter_pages(DUMP):
            stats["pages_total"] += 1
            if _REDIRECT_RE.match(wikitext):
                stats["redirects_skipped"] += 1
                continue
            plain = wikitext_to_text(wikitext)
            stats["pages_used"] += 1
            for raw_sent in sentences_from_text(plain):
                line = clean_line(raw_sent)
                if not line:
                    continue
                words = _WORD_RE.findall(line.lower())
                if not quality_ok(line, words):
                    stats["dropped_quality"] += 1
                    continue
                h = hash(line)
                if h in seen:
                    stats["dropped_dup"] += 1
                    continue
                if len(seen) < SEEN_CAP:
                    seen.add(h)
                out.write(line + "\n")
                stats["lines"] += 1
                stats["tokens"] += len(words)
            if stats["pages_total"] % 10000 == 0:
                print(f"PROGRESS pages={stats['pages_total']} lines={stats['lines']} "
                      f"tokens={stats['tokens']}", flush=True)
    stats["output_bytes"] = os.path.getsize(OUT_TXT)
    stats["output_path"] = OUT_TXT
    with open(OUT_STATS, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
