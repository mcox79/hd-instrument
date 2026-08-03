#!/usr/bin/env python3
"""Mine explicit-connective-triggered causal-relation gold from raw McGuffey g5/g6 text.

Produces data/eval_gold_mention_role_mcguffey_v1/gold_causal_relations_v1.jsonl
per notes/inference_leap_scoping_beyond_role_decode_2026-08-02.md.

VERBATIM GUARD (mandatory, enforced not eyeballed): every emitted cause_clause and
effect_clause, after whitespace-normalization, MUST be a CONTIGUOUS SUBSTRING of
that record's source_paragraph_verbatim (itself a verbatim run pasted straight from
the raw clean/g5.txt or clean/g6.txt file). Allowed source operations ONLY:
(a) split a paragraph into sentences, (b) split a sentence in two at the connective
boundary itself. NO rewording, paraphrase, or invented text. If any check fails the
script raises SystemExit(1) and writes nothing.

CLAUSE-INDEX / ADJACENCY MEASUREMENT: each mined instance is placed inside a
per-paragraph ordered clause list (whole sentences as clause units, except the
connective sentence which is split at the connective into a before-part and an
after-part clause). clause_gap = abs(effect_clause_idx - cause_clause_idx) in that
list. For cross-sentence connectives (therefore/so/consequently/thus/that's why/
as a result at sentence-initial position) the cause-clause search walks BACKWARD
past trivial filler/speech-tag clauses (very short, or "said X"/"asked X" dialogue
tags) so genuinely non-adjacent cause references are captured honestly rather than
defaulting every cross-sentence link to gap=1.

ASCII-only; no em-dashes. gold_verified=false on every record (Director verifies).
"""
import json
import re
import sys

OUT = "data/eval_gold_mention_role_mcguffey_v1/gold_causal_relations_v1.jsonl"
SOURCES = [
    ("g5", "data/corpora/mcguffey_graded/clean/g5.txt"),
    ("g6", "data/corpora/mcguffey_graded/clean/g6.txt"),
]

SENT_SPLIT_RE = re.compile(r'(?<=[.!?])\s+(?=[A-Z"\'“])')
SPEECH_TAG_RE = re.compile(
    r'^["\'“‘]?\s*(said|asked|cried|replied|answered|exclaimed|added|continued|whispered)\b',
    re.IGNORECASE,
)


def norm(s):
    """Whitespace-normalize (guard-legal op; no punctuation stripping so substring
    check stays exact -- we keep clauses as literal split output)."""
    return re.sub(r"\s+", " ", s).strip()


def split_paragraphs(text):
    paras = re.split(r"\n\s*\n", text)
    out = []
    for p in paras:
        p = norm(p)
        if len(p) < 40:
            continue
        out.append(p)
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


# ---------------------------------------------------------------------------
# Connective matchers. Each returns (effect_text, cause_text, order) or None,
# operating on a SINGLE sentence for intra-sentence types.
# order: "cause_before_effect" or "effect_before_cause" (textual order in the
# ORIGINAL sentence, i.e. which clause-half appears first in the raw text).
# ---------------------------------------------------------------------------

def try_because(sent):
    m = re.search(r"\bbecause\b", sent, re.IGNORECASE)
    if not m:
        return None
    if sent[m.end():m.end() + 3].strip().lower().startswith("of"):
        return None  # "because of NP" is a PP not a clause
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
    # "<clause>, so <pronoun/noun> <verb>..." resultative "so", not "so that"
    if re.search(r"\bso that\b", sent, re.IGNORECASE):
        return None
    m = re.search(
        r",\s*so\s+(he|she|it|they|we|I|you|the|his|her|their)\b",
        sent, re.IGNORECASE,
    )
    if not m:
        return None
    cause = sent[:m.start()].strip().rstrip(",;")
    effect = sent[m.start() + 1:].strip()  # keep "so ..." in effect, drop leading comma
    if len(cause) < 15 or len(effect) < 15:
        return None
    return (cause, effect, "cause_before_effect", "so_midsentence")


def try_for_causal_midsentence(sent):
    m = re.search(
        r";\s*for\s+(he|she|it|they|we|I|you|the)\b",
        sent, re.IGNORECASE,
    )
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


def mine_paragraph(grade, pidx, para, prev_para=None):
    """Return list of raw instance dicts for one paragraph.

    prev_para (verbatim text of the immediately preceding paragraph, or None) is
    used ONLY to resolve a cross-sentence connective that opens its paragraph
    (si==0, no in-paragraph prior clause) -- the cause is then searched in the
    tail of prev_para and the emitted source_paragraph_verbatim becomes the
    literal contiguous "prev_para + blank-line + para" excerpt of the raw file.
    """
    sentences = split_sentences(para)
    if len(sentences) < 1:
        return []
    # build clause list: each sentence is one clause UNLESS it matches an intra-
    # sentence connective, in which case it is split into 2 clauses.
    clauses = []            # list of clause strings
    clause_sent_idx = []    # which original sentence index each clause came from
    intra_hits = []         # (sent_idx, clause_idx_before, clause_idx_after, effect, cause, order, conn)
    for si, sent in enumerate(sentences):
        hit = None
        for fn in INTRA_MATCHERS:
            hit = fn(sent)
            if hit:
                break
        if hit:
            a, b, order, conn = hit
            idx_before = len(clauses)
            clauses.append(a)
            clause_sent_idx.append(si)
            idx_after = len(clauses)
            clauses.append(b)
            clause_sent_idx.append(si)
            intra_hits.append((si, idx_before, idx_after, a, b, order, conn))
        else:
            clauses.append(sent)
            clause_sent_idx.append(si)

    instances = []
    para_ws = para

    # --- intra-sentence causal links ---
    for (si, idx_before, idx_after, a, b, order, conn) in intra_hits:
        if order == "cause_before_effect":
            cause_idx, effect_idx = idx_before, idx_after
            cause_txt, effect_txt = a, b
        else:
            effect_idx, cause_idx = idx_before, idx_after
            effect_txt, cause_txt = a, b
        instances.append(dict(
            grade=grade, pidx=pidx, para=para_ws, clauses=list(clauses),
            cause_idx=cause_idx, effect_idx=effect_idx,
            cause_clause=cause_txt, effect_clause=effect_txt,
            connective=conn, textual_order=order, kind="intra_sentence",
        ))

    # --- cross-sentence causal links ---
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
                # cause must come from the tail of the PREVIOUS paragraph
                if not prev_sentences:
                    continue
                combined = list(prev_sentences) + list(clauses)
                offset = len(prev_sentences)
                effect_idx = offset  # this sentence's clause is the first of `clauses`, i.e. combined[offset]
                cause_idx = offset - 1
                while cause_idx > 0 and is_trivial_clause(combined[cause_idx]):
                    cause_idx -= 1
                if cause_idx < 0:
                    continue
                cause_txt = combined[cause_idx]
                gap = offset - cause_idx
                combined_para = prev_para + "\n\n" + para_ws
                instances.append(dict(
                    grade=grade, pidx=pidx, para=combined_para, clauses=combined,
                    cause_idx=cause_idx, effect_idx=effect_idx,
                    cause_clause=cause_txt, effect_clause=effect_txt,
                    connective=conn, textual_order="cause_before_effect",
                    kind="cross_paragraph", explicit_gap=gap,
                ))
                break

            # locate effect clause idx = the clause built from this sentence
            effect_idx = None
            for ci, sidx in enumerate(clause_sent_idx):
                if sidx == si:
                    effect_idx = ci
                    break
            if effect_idx is None:
                continue
            # walk backward past trivial filler / speech-tag clauses
            cause_idx = effect_idx - 1
            while cause_idx > 0 and is_trivial_clause(clauses[cause_idx]):
                cause_idx -= 1
            if cause_idx < 0:
                continue
            cause_txt = clauses[cause_idx]
            instances.append(dict(
                grade=grade, pidx=pidx, para=para_ws, clauses=list(clauses),
                cause_idx=cause_idx, effect_idx=effect_idx,
                cause_clause=cause_txt, effect_clause=effect_txt,
                connective=conn, textual_order="cause_before_effect", kind="cross_sentence",
            ))
            break  # one connective match per sentence

    return instances


def main():
    all_records = []
    seen_keys = set()
    for grade, path in SOURCES:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        paras = split_paragraphs(text)
        for pidx, para in enumerate(paras):
            prev_para = paras[pidx - 1] if pidx > 0 else None
            for inst in mine_paragraph(grade, pidx, para, prev_para=prev_para):
                key = (grade, pidx, inst["kind"], inst["cause_idx"], inst["effect_idx"], inst["connective"])
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                all_records.append(inst)

    # ---- VERBATIM GUARD ----
    failures = []
    records = []
    for i, inst in enumerate(all_records):
        para_ws = inst["para"]
        cc = norm(inst["cause_clause"])
        ec = norm(inst["effect_clause"])
        if not cc or cc not in para_ws:
            failures.append(("CAUSE", i, inst["grade"], inst["pidx"], inst["cause_clause"]))
            continue
        if not ec or ec not in para_ws:
            failures.append(("EFFECT", i, inst["grade"], inst["pidx"], inst["effect_clause"]))
            continue
        passage_id = "%s_causal_p%04d_%s_%d" % (inst["grade"], inst["pidx"], inst["connective"], i)
        gap = abs(inst["effect_idx"] - inst["cause_idx"])
        rec = {
            "passage_id": passage_id,
            "grade": inst["grade"],
            "cause_clause": cc,
            "effect_clause": ec,
            "cause_clause_idx": inst["cause_idx"],
            "effect_clause_idx": inst["effect_idx"],
            "clause_gap": gap,
            "connective": inst["connective"],
            "connective_kind": inst["kind"],
            "textual_order": inst["textual_order"],
            "clauses": inst["clauses"],
            "gold_verified": False,
            "candidate_source": "mcguffey_graded_raw_regex_mine",
            "source_paragraph_verbatim": para_ws,
        }
        records.append(rec)

    print("MINING REPORT")
    print("  raw candidate instances:", len(all_records))
    print("  verbatim-guard failures:", len(failures))
    if failures:
        for fmode, i, g, p, txt in failures[:20]:
            print("   FAIL", fmode, g, p, repr(txt[:80]))
        raise SystemExit(1)
    print("  passed verbatim guard:", len(records))

    # ascii guard
    for rec in records:
        for ch in json.dumps(rec, ensure_ascii=False):
            if ord(ch) > 127:
                raise SystemExit("NON-ASCII in " + rec["passage_id"] + ": " + repr(ch))

    with open(OUT, "w", encoding="utf-8", newline="") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=True) + "\n")
    print("  ALL CLAUSES VERBATIM. wrote", OUT, "n=", len(records))

    # ---- adjacency-distance distribution ----
    from collections import Counter
    gap_counts = Counter(r["clause_gap"] for r in records)
    conn_counts = Counter(r["connective"] for r in records)
    order_counts = Counter(r["textual_order"] for r in records)
    print("\nADJACENCY-DISTANCE DISTRIBUTION (clause_gap -> count)")
    for g in sorted(gap_counts):
        print("  gap=%d: %d (%.1f%%)" % (g, gap_counts[g], 100.0 * gap_counts[g] / len(records)))
    print("\nCONNECTIVE COUNTS")
    for c, n in conn_counts.most_common():
        print("  %s: %d" % (c, n))
    print("\nTEXTUAL ORDER COUNTS")
    for o, n in order_counts.most_common():
        print("  %s: %d" % (o, n))
    nontrivial = [r for r in records if r["clause_gap"] >= 2 or r["textual_order"] == "effect_before_cause"]
    print("\nNON-TRIVIAL SUBSET (clause_gap>=2 OR reversed textual order): %d / %d (%.1f%%)" % (
        len(nontrivial), len(records), 100.0 * len(nontrivial) / len(records)))
    strictly_nonadjacent = [r for r in records if r["clause_gap"] >= 2]
    print("STRICTLY NON-ADJACENT (clause_gap>=2): %d / %d (%.1f%%)" % (
        len(strictly_nonadjacent), len(records), 100.0 * len(strictly_nonadjacent) / len(records)))


if __name__ == "__main__":
    main()
