"""Typed WorldTree tablestore parser: TSV rows -> {uid: {relation, arg0, arg1, confident}}.

P1 promotion (integration audit 2026-07-25): the canonical, self-contained home for
`parse_tablestore_typed`, previously trapped inside experiments/exp_arc_selection_relational_meaning_v1.py.
The relation type is the table NAME; arg0/arg1 are split around the relation-verb pivot column.
Self-contained (numpy/torch-free, no exp-tower imports) so the composed reasoner can consume it as a
stable hdlab API. ASCII-only.
"""
from __future__ import annotations

import os
import csv
import glob
from typing import Dict, List, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_WT = os.path.join(_REPO, "data", "corpora", "worldtree", "WorldtreeExplanationCorpusV2.1_Feb2020")
TABLES_DIR = os.path.join(_WT, "tablestore", "v2.1", "tables")

# LICENSED relation types = valid derivation steps (causal / conditional / functional).
# STRUCTURAL (KINDOF/PARTOF/MADEOF) are premise-linking only, not a derivation license.
LICENSED = ("CAUSE", "IFTHEN", "REQUIRES", "COUPLEDRELATIONSHIP", "SOURCEOF", "USEDFOR")

# FILL-header connectives that are articles/glue, NOT the relation verb (never a pivot preference).
_ARTICLE_FILL = frozenset({"a", "an", "the", "a/the", "as", "as a/the", "if", "when", "if/when a/the",
                           "if/when", ",", "then / ,", "for", "by", "by/through", "by/through/how",
                           "by/through/due to"})
# header-substring hints that a FILL/VERB column carries the relation verb (pivot preference)
_VERB_HINTS = ("kind of", "part of", "used", "cause", "means", "require", "source", "made of",
               "contain", "then", "become", "produce", "provide", "example", "called", "instance",
               "affect", "transfer", "opposite", "synonym", "habitat", "locat", "measure", "form",
               "predator", "consume", "perceiv", "change", "is a", "provides", "sourceof")


def _classify_header(hdr: List[str]) -> Tuple[List[str], int]:
    """Return per-column kind: 'SKIP' | 'FILL' | 'NAMED' | 'EMPTY', plus the UID column index."""
    kinds: List[str] = []
    uidcol = None
    for i, h in enumerate(hdr):
        hs = h.strip()
        if hs.startswith("[SKIP]"):
            kinds.append("SKIP")
        elif hs.startswith("[FILL]"):
            kinds.append("FILL")
        elif hs == "":
            kinds.append("EMPTY")
        else:
            kinds.append("NAMED")
        if "UID" in hs:
            uidcol = i
    return kinds, uidcol


def _fill_text(h: str) -> str:
    """The connective text of a [FILL] header (lowercased, marker stripped)."""
    return h.replace("[FILL]", "").strip().lower()


def _is_verb_pivot_header(h: str) -> bool:
    """True iff a FILL/VERB header looks like it carries the relation verb (not an article)."""
    hl = h.lower()
    if _fill_text(h) in _ARTICLE_FILL:
        return False
    return any(v in hl for v in _VERB_HINTS)


def _split_row_typed(row: List[str], kinds: List[str], hdr: List[str],
                     pivot_candidates: List[int]) -> Tuple[str, str, bool]:
    """Pick the pivot column yielding BOTH sides non-empty (prefer verb-hint, then balance);
    return (arg0_text, arg1_text, confident). NAMED-column content only."""
    def named_content(lo: int, hi: int) -> List[str]:
        cells = []
        for j in range(lo, hi):
            if j >= len(row):
                break
            if kinds[j] == "NAMED":
                c = row[j].strip()
                if c:
                    cells.append(c)
        return cells

    best = None  # (score, arg0, arg1)
    for p in pivot_candidates:
        a0 = named_content(0, p)
        a1 = named_content(p + 1, len(row))
        if a0 and a1:
            verb = 1 if (p < len(hdr) and _is_verb_pivot_header(hdr[p])) else 0
            balance = -abs(len(a0) - len(a1))
            score = (verb * 100) + balance
            if best is None or score > best[0]:
                best = (score, " ".join(a0), " ".join(a1))
    if best is not None:
        return best[1], best[2], True
    # fallback: split ALL named content at its midpoint (low-confidence; still records structure)
    allc = named_content(0, len(row))
    if len(allc) >= 2:
        mid = len(allc) // 2
        return " ".join(allc[:mid]), " ".join(allc[mid:]), False
    return "", "", False


def parse_tablestore_typed(tables_dir: str = TABLES_DIR) -> Dict[str, dict]:
    """Parse every tablestore TSV -> uid -> {relation, arg0, arg1, confident}. Deterministic (sorted)."""
    uid2typed: Dict[str, dict] = {}
    for path in sorted(glob.glob(os.path.join(tables_dir, "*.tsv"))):
        relation = os.path.splitext(os.path.basename(path))[0]
        with open(path, "r", encoding="utf-8") as f:
            rd = csv.reader(f, delimiter="\t")
            hdr = next(rd)
            kinds, uidcol = _classify_header(hdr)
            pivot_candidates = []
            for j, k in enumerate(kinds):
                if k == "FILL" and _fill_text(hdr[j]) not in _ARTICLE_FILL:
                    pivot_candidates.append(j)
                elif k == "NAMED" and hdr[j].strip().upper().startswith("VERB"):
                    pivot_candidates.append(j)
            if not pivot_candidates:
                pivot_candidates = [j for j, k in enumerate(kinds) if k == "FILL"]
            pivot_candidates = sorted(pivot_candidates)
            for r in rd:
                if not any(c.strip() for c in r):
                    continue
                uid = r[uidcol].strip() if (uidcol is not None and uidcol < len(r)) else ""
                if not uid:
                    continue
                a0, a1, conf = _split_row_typed(r, kinds, hdr, pivot_candidates)
                uid2typed[uid] = {"relation": relation, "arg0": a0, "arg1": a1, "confident": conf}
    return uid2typed


def licensed_rows(uid2typed: Dict[str, dict], licensed: Tuple[str, ...] = LICENSED) -> List[dict]:
    """Filter to LICENSED, confident, non-empty rows -> list of {relation, arg0, arg1}. Deterministic."""
    rows = []
    for uid in sorted(uid2typed):
        d = uid2typed[uid]
        if d["relation"] in licensed and d["confident"] and d["arg0"].strip() and d["arg1"].strip():
            rows.append({"relation": d["relation"], "arg0": d["arg0"].strip(),
                         "arg1": d["arg1"].strip()})
    return rows


if __name__ == "__main__":
    u = parse_tablestore_typed()
    rows = licensed_rows(u)
    per = {}
    for r in rows:
        per[r["relation"]] = per.get(r["relation"], 0) + 1
    print(f"parsed {len(u)} typed rows; {len(rows)} LICENSED-confident-nonempty; per-relation={per}")
