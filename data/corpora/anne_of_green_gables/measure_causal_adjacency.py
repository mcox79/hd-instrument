# -*- coding: utf-8 -*-
"""
Explicit-connective causal-relation adjacency scan for Anne of Green Gables,
using the SAME connective-detection + clause_gap measurement logic as
tools/gen_causal_relations_gold.py (the miner that measured McGuffey g5/g6 at
207/208 links adjacent, ~99.5%). Reused near-verbatim (paragraph split,
sentence split, INTRA/CROSS connective matchers, clause_gap = abs(effect_idx
- cause_idx)) so the two corpora's explicit-connective adjacency distributions
are directly comparable -- this IS "the exact check that would have caught
McGuffey's 99.5%-adjacent collapse", per the task brief.

Divergence (structural only): operates over the WHOLE cleaned novel in
paragraph order (no LESSON/grade scoping), and additionally records which
CHAPTER each instance falls in (from chapters.json) so cross-chapter links,
if any, are visible.

This measures EXPLICIT LEXICAL-CONNECTIVE causation only (because/so/
therefore/etc.). It does NOT and CANNOT detect narrative-level causal
payoffs that aren't marked by these connectives (e.g. "the currant wine
incident causes a rift many chapters later" told through unmarked narration)
-- that class needs a manual spot-check, done separately and reported
alongside this script's output, not invented here.

Pure stdlib. ASCII-only script.
"""
import json
import re
from collections import Counter

BASE = r"d:/AI/hd-instrument/data/corpora/anne_of_green_gables/cleaned"
CLEAN = BASE + "/anne_of_green_gables.clean.txt"
CHAPTERS = BASE + "/anne_of_green_gables.chapters.json"
OUT = BASE + "/causal_adjacency_report.json"

SENT_SPLIT_RE = re.compile(r'(?<=[.!?])\s+(?=[A-Z"\'“‘])')
SPEECH_TAG_RE = re.compile(
    r'^["\'“‘]?\s*(said|asked|cried|replied|answered|exclaimed|added|continued|whispered)\b',
    re.IGNORECASE,
)


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def split_paragraphs_with_chapter(lines, chapters):
    """Return list of (chapter_num, para_text) in document order, skipping
    the '# CHAPTER n title' marker lines themselves."""
    bounds = []
    for i, ch in enumerate(chapters):
        start = ch["start_out_idx"]
        end = chapters[i + 1]["start_out_idx"] if i + 1 < len(chapters) else len(lines)
        bounds.append((ch["num"], start, end))
    out = []
    for num, start, end in bounds:
        body = "\n".join(lines[start + 1:end])  # skip marker line
        for p in re.split(r"\n\s*\n", body):
            p = norm(p)
            if len(p) < 40:
                continue
            out.append((num, p))
    return out


def split_sentences(para):
    parts = SENT_SPLIT_RE.split(para)
    return [norm(p) for p in parts if norm(p)]


def is_trivial_clause(c):
    if len(c) < 20:
        return True
    if SPEECH_TAG_RE.match(c):
        return True
    return False


def try_because(sent):
    m = re.search(r"\bbecause\b", sent, re.IGNORECASE)
    if not m:
        return None
    if sent[m.end():m.end() + 3].strip().lower().startswith("of"):
        return None
    effect = sent[:m.start()].strip().rstrip(",;")
    cause = sent[m.start():].strip()
    if len(effect) < 15 or len(cause) < 20:
        return None
    return (effect, cause, "effect_before_cause", "because")


def try_so_that(sent):
    m = re.search(r"\bso that\b", sent, re.IGNORECASE)
    if not m:
        return None
    cause = sent[:m.start()].strip().rstrip(",;")
    effect = sent[m.start():].strip()
    if len(cause) < 15 or len(effect) < 20:
        return None
    return (cause, effect, "cause_before_effect", "so_that")


def try_in_order_to(sent):
    m = re.search(r"\bin order to\b", sent, re.IGNORECASE)
    if not m:
        return None
    cause = sent[:m.start()].strip().rstrip(",;")
    effect = sent[m.start():].strip()
    if len(cause) < 15 or len(effect) < 15:
        return None
    return (cause, effect, "cause_before_effect", "in_order_to")


def try_so_causal_midsentence(sent):
    if re.search(r"\bso that\b", sent, re.IGNORECASE):
        return None
    m = re.search(r",\s*so\s+(he|she|it|they|we|I|you|the|his|her|their)\b", sent, re.IGNORECASE)
    if not m:
        return None
    cause = sent[:m.start()].strip().rstrip(",;")
    effect = sent[m.start() + 1:].strip()
    if len(cause) < 15 or len(effect) < 15:
        return None
    return (cause, effect, "cause_before_effect", "so_midsentence")


def try_for_causal_midsentence(sent):
    m = re.search(r";\s*for\s+(he|she|it|they|we|I|you|the)\b", sent, re.IGNORECASE)
    if not m:
        m = re.search(r",\s*for\s+(he|she|it|they|we|I|you|the)\b", sent, re.IGNORECASE)
    if not m:
        return None
    effect = sent[:m.start()].strip().rstrip(",;")
    cause = sent[m.start():].lstrip(";, ").strip()
    if len(effect) < 15 or len(cause) < 20:
        return None
    return (effect, cause, "effect_before_cause", "for_midsentence")


INTRA_MATCHERS = [try_because, try_so_that, try_in_order_to, try_so_causal_midsentence, try_for_causal_midsentence]

CROSS_SENTENCE_PATTERNS = [
    (re.compile(r"^Therefore,?\s*", re.IGNORECASE), "therefore"),
    (re.compile(r"^Consequently,?\s*", re.IGNORECASE), "consequently"),
    (re.compile(r"^Thus,?\s*", re.IGNORECASE), "thus"),
    (re.compile(r"^As a result,?\s*", re.IGNORECASE), "as_a_result"),
    (re.compile(r"^That('s| is) why\s*", re.IGNORECASE), "thats_why"),
    (re.compile(r"^So,?\s+(he|she|it|they|we|I|you|the)\b", re.IGNORECASE), "so_sentence_initial"),
    (re.compile(r"^For\s+(he|she|it|they|we|the)\b", re.IGNORECASE), "for_sentence_initial"),
    (re.compile(r"^Since\s+", re.IGNORECASE), "since_sentence_initial"),
]


def mine_paragraph(chapter, pidx, para, prev_para=None, prev_chapter=None):
    sentences = split_sentences(para)
    if len(sentences) < 1:
        return []
    clauses, clause_sent_idx, intra_hits = [], [], []
    for si, sent in enumerate(sentences):
        hit = None
        for fn in INTRA_MATCHERS:
            hit = fn(sent)
            if hit:
                break
        if hit:
            a, b, order, conn = hit
            idx_before = len(clauses); clauses.append(a); clause_sent_idx.append(si)
            idx_after = len(clauses); clauses.append(b); clause_sent_idx.append(si)
            intra_hits.append((si, idx_before, idx_after, a, b, order, conn))
        else:
            clauses.append(sent); clause_sent_idx.append(si)

    instances = []
    para_ws = para

    for (si, idx_before, idx_after, a, b, order, conn) in intra_hits:
        if order == "cause_before_effect":
            cause_idx, effect_idx, cause_txt, effect_txt = idx_before, idx_after, a, b
        else:
            effect_idx, cause_idx, effect_txt, cause_txt = idx_before, idx_after, a, b
        instances.append(dict(chapter=chapter, pidx=pidx, para=para_ws, clauses=list(clauses),
                               cause_idx=cause_idx, effect_idx=effect_idx,
                               cause_clause=cause_txt, effect_clause=effect_txt,
                               connective=conn, textual_order=order, kind="intra_sentence",
                               cross_chapter=False))

    prev_sentences = split_sentences(prev_para) if prev_para else []
    for si, sent in enumerate(sentences):
        if any(h[0] == si for h in intra_hits):
            continue
        for pat, conn in CROSS_SENTENCE_PATTERNS:
            m = pat.match(sent)
            if not m:
                continue
            effect_txt = sent[m.end():].strip() if conn not in ("so_sentence_initial", "for_sentence_initial", "since_sentence_initial") else sent
            if len(effect_txt) < 15:
                effect_txt = sent

            if si == 0:
                if not prev_sentences:
                    continue
                combined = list(prev_sentences) + list(clauses)
                offset = len(prev_sentences)
                effect_idx = offset
                cause_idx = offset - 1
                while cause_idx > 0 and is_trivial_clause(combined[cause_idx]):
                    cause_idx -= 1
                if cause_idx < 0:
                    continue
                cause_txt = combined[cause_idx]
                gap = offset - cause_idx
                combined_para = (prev_para or "") + "\n\n" + para_ws
                instances.append(dict(chapter=chapter, pidx=pidx, para=combined_para, clauses=combined,
                                       cause_idx=cause_idx, effect_idx=effect_idx,
                                       cause_clause=cause_txt, effect_clause=effect_txt,
                                       connective=conn, textual_order="cause_before_effect",
                                       kind="cross_paragraph", explicit_gap=gap,
                                       cross_chapter=(prev_chapter is not None and prev_chapter != chapter)))
                break

            effect_idx = None
            for ci, sidx in enumerate(clause_sent_idx):
                if sidx == si:
                    effect_idx = ci
                    break
            if effect_idx is None:
                continue
            cause_idx = effect_idx - 1
            while cause_idx > 0 and is_trivial_clause(clauses[cause_idx]):
                cause_idx -= 1
            if cause_idx < 0:
                continue
            cause_txt = clauses[cause_idx]
            instances.append(dict(chapter=chapter, pidx=pidx, para=para_ws, clauses=list(clauses),
                                   cause_idx=cause_idx, effect_idx=effect_idx,
                                   cause_clause=cause_txt, effect_clause=effect_txt,
                                   connective=conn, textual_order="cause_before_effect", kind="cross_sentence",
                                   cross_chapter=False))
            break

    return instances


def main():
    lines = open(CLEAN, encoding="utf-8").read().split("\n")
    chapters = json.load(open(CHAPTERS, encoding="utf-8"))
    paras = split_paragraphs_with_chapter(lines, chapters)

    all_records = []
    seen_keys = set()
    for pidx, (chapter, para) in enumerate(paras):
        prev_chapter, prev_para = (paras[pidx - 1][0], paras[pidx - 1][1]) if pidx > 0 else (None, None)
        for inst in mine_paragraph(chapter, pidx, para, prev_para=prev_para, prev_chapter=prev_chapter):
            key = (chapter, pidx, inst["kind"], inst["cause_idx"], inst["effect_idx"], inst["connective"])
            if key in seen_keys:
                continue
            seen_keys.add(key)
            all_records.append(inst)

    failures = []
    records = []
    for i, inst in enumerate(all_records):
        para_ws = inst["para"]
        cc = norm(inst["cause_clause"]); ec = norm(inst["effect_clause"])
        if not cc or cc not in para_ws:
            failures.append(("CAUSE", i, inst["chapter"], inst["pidx"], inst["cause_clause"])); continue
        if not ec or ec not in para_ws:
            failures.append(("EFFECT", i, inst["chapter"], inst["pidx"], inst["effect_clause"])); continue
        gap = abs(inst["effect_idx"] - inst["cause_idx"])
        records.append(dict(
            passage_id="anne_causal_ch%02d_p%04d_%s_%d" % (inst["chapter"], inst["pidx"], inst["connective"], i),
            chapter=inst["chapter"], cause_clause=cc, effect_clause=ec,
            clause_gap=gap, connective=inst["connective"], connective_kind=inst["kind"],
            textual_order=inst["textual_order"], cross_chapter=inst.get("cross_chapter", False),
            source_paragraph_verbatim=para_ws,
        ))

    print("MINING REPORT (Anne of Green Gables, explicit-connective causal links)")
    print("  raw candidate instances:", len(all_records))
    print("  verbatim-guard failures:", len(failures))
    if failures:
        for fmode, i, ch, p, txt in failures[:20]:
            print("   FAIL", fmode, ch, p, repr(txt[:80]))
    print("  passed verbatim guard:", len(records))

    gap_counts = Counter(r["clause_gap"] for r in records)
    conn_counts = Counter(r["connective"] for r in records)
    nontrivial = [r for r in records if r["clause_gap"] >= 2 or r["textual_order"] == "effect_before_cause"]
    strictly_nonadjacent = [r for r in records if r["clause_gap"] >= 2]
    cross_ch = [r for r in records if r["cross_chapter"]]

    summary = dict(
        n_instances=len(records),
        gap_distribution={str(k): v for k, v in sorted(gap_counts.items())},
        connective_counts=dict(conn_counts.most_common()),
        pct_gap1_adjacent=round(100 * gap_counts.get(1, 0) / len(records), 1) if records else 0,
        n_nontrivial_gap_ge2_or_reversed=len(nontrivial),
        pct_nontrivial=round(100 * len(nontrivial) / len(records), 1) if records else 0,
        n_strictly_nonadjacent_gap_ge2=len(strictly_nonadjacent),
        pct_strictly_nonadjacent=round(100 * len(strictly_nonadjacent) / len(records), 1) if records else 0,
        n_cross_chapter_links=len(cross_ch),
        strictly_nonadjacent_examples=[
            {"passage_id": r["passage_id"], "chapter": r["chapter"], "clause_gap": r["clause_gap"],
             "connective": r["connective"], "cause_clause": r["cause_clause"][:150],
             "effect_clause": r["effect_clause"][:150]}
            for r in strictly_nonadjacent[:10]
        ],
    )
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(dict(summary=summary, records=records), f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
