#!/usr/bin/env python
"""
build_mention_role_eval_mcguffey.py -- DATA-BUILD (not an experiment). No push/store/queue.

Builds a hand-reviewable CANDIDATE (NOT gold) mention/role eval set from real McGuffey
prose (grades 1-4), biased toward the hard-feature classes that are the known dominant
failure modes for real-syntax mention/role extraction: quotative-inversion dialogue tags
("said Andrew" -> Andrew is the postposed AGENT/speaker, not a patient), PP-misattachment,
subordinate-clause scope-bleed, relative clauses, and passives.

This is genuinely complementary to the two existing gold files
(gold_mcguffey_castle_building_svo_v1.json, gold_mcguffey_lccp_argstruct_v1.json), which
BOTH explicitly exclude quotative-inversion speech verbs and have no mention-span
annotation. This set INCLUDES quotative inversion + adds mention spans + a review-ready
candidate format with gold_verified=false for every row.

Labeling aids (candidate-generation only, NOT ground truth):
  hdlab.pos_tagger.PosTagger  (data/frontend_assets/pos_tagger_ud_ewt_upos.json)
  hdlab.arc_parser.ArcParser  (data/frontend_assets/arc_parser_hashed_ud_ewt.npz) --
    returns UNLABELED dependency arcs (head assignment only, no deprel) + per-token
    ParseResult.margins (head-choice confidence). Agent/patient roles are a HEURISTIC
    guess (leftward NOUN/PROPN/PRON child of a verb = candidate agent, rightward child =
    candidate patient) layered on top of the unlabeled arcs -- this heuristic is EXPECTED
    to fail on quotative inversion (postposed subject reads as a rightward child -> gets
    mislabeled candidate-patient), which is exactly the point: expose how hard real
    extraction is, not claim a working extractor.

ASCII-only. Binary-safe UTF-8 write (newline='' to avoid CRLF doubling).
"""
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from hdlab.pos_tagger import PosTagger
from hdlab.arc_parser import ArcParser

GRADES = ["g1", "g2", "g3", "g4"]
CORPUS_DIR = os.path.join(REPO, "data", "corpora", "mcguffey_graded", "clean")
POS_MODEL = os.path.join(REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
ARC_MODEL = os.path.join(REPO, "data", "frontend_assets", "arc_parser_hashed_ud_ewt.npz")
OUT_DIR = os.path.join(REPO, "data", "eval_gold_mention_role_mcguffey_v1")
OUT_PATH = os.path.join(OUT_DIR, "candidates.jsonl")

MENTION_UPOS = {"NOUN", "PROPN", "PRON"}

# --- hard-feature regex classifiers (used only for SAMPLING BIAS / tagging; not gold) ---
QUOTATIVE_RE = re.compile(
    r'"\s*(said|asked|cried|replied|exclaimed|answered|observed)\b|'
    r'\b(said|asked|cried|replied|exclaimed|answered|observed)\s+[A-Z][a-z]+\b|'
    r'\b(said|asked|cried|replied|exclaimed|answered|observed)\s+(he|she|they|I|his|her)\b'
)
PASSIVE_RE = re.compile(r"\b(was|were|is|are|been|be|being)\s+\w+ed\b")
RELATIVE_RE = re.compile(r"\b(who|which|that|whom|whose)\b")
SUBORD_RE = re.compile(r"^(when|because|if|after|while|although|though|since|as|before)\b", re.I)
PP_HEAVY_RE = re.compile(r"\b(in|on|at|with|of|for|to|from|by|into|onto)\b.*\b(in|on|at|with|of|for|to|from|by|into|onto)\b")


def classify_hard_feature(sent_text):
    if QUOTATIVE_RE.search(sent_text):
        return "quotative"
    if PASSIVE_RE.search(sent_text):
        return "passive"
    if RELATIVE_RE.search(sent_text):
        return "relative"
    if SUBORD_RE.search(sent_text.strip()):
        return "PP"  # subordinate-clause scope-bleed bucketed with PP per task's 5-class scheme below
    if PP_HEAVY_RE.search(sent_text):
        return "PP"
    return "simple"


def split_sentences(raw_text):
    """paragraphs separated by blank lines; split each paragraph into sentences on
    [.?!] followed by space+capital or end-of-paragraph. Simple, ASCII-safe."""
    paras = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
    sents = []
    for para in paras:
        para = para.replace("\n", " ")
        # split on sentence-final punctuation followed by a space (keep the punctuation)
        pieces = re.split(r'(?<=[.?!])\s+(?=[A-Z"\'0-9])', para)
        for p in pieces:
            p = p.strip()
            if p:
                sents.append(p)
    return sents


def tokenize(sent):
    """Simple regex tokenizer: words (incl. contractions/hyphens), quotes, and punctuation
    as separate tokens."""
    toks = re.findall(r"[A-Za-z]+(?:['\-][A-Za-z]+)*|[0-9]+|[.,!?;:\"']|--", sent)
    return toks


def load_grade_lines(grade):
    path = os.path.join(CORPUS_DIR, grade + ".txt")
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    # keep an approximate 1-based line index by locating each paragraph's start line
    lines = raw.split("\n")
    para_start_line = []
    cur_line = 1
    para_buf = []
    paras = []
    for i, ln in enumerate(lines, start=1):
        if ln.strip() == "":
            if para_buf:
                paras.append((cur_line, "\n".join(para_buf)))
                para_buf = []
            continue
        if not para_buf:
            cur_line = i
        para_buf.append(ln)
    if para_buf:
        paras.append((cur_line, "\n".join(para_buf)))

    out = []
    for start_line, para_text in paras:
        para_text_flat = para_text.replace("\n", " ")
        pieces = re.split(r'(?<=[.?!])\s+(?=[A-Z"\'0-9])', para_text_flat.strip())
        for p in pieces:
            p = p.strip()
            if p:
                out.append((start_line, p))
    return out


def candidate_mentions(tokens, upos):
    spans = []
    for i, (tok, tag) in enumerate(zip(tokens, upos)):
        if tag in MENTION_UPOS:
            spans.append({"text": tok, "token_idx": i, "upos": tag})
    return spans


def candidate_roles(tokens, upos, parse_result):
    """Heuristic: for each VERB token, candidate agent = nearest preceding NOUN/PROPN/PRON
    child of that verb (per unlabeled arcs); candidate patient = nearest following
    NOUN/PROPN/PRON child of that verb. This is EXPECTED to mislabel quotative-inversion
    postposed subjects as candidate-patients -- that is the exposed failure mode, not a
    claimed correct extractor."""
    n = len(tokens)
    heads = parse_result.heads  # dep_idx(1-based) -> head_idx(0=ROOT,1-based otherwise)
    margins = parse_result.margins
    children_of = {}
    for dep_idx, head_idx in heads.items():
        children_of.setdefault(head_idx, []).append(dep_idx)

    roles = []
    for vi in range(1, n + 1):
        if upos[vi - 1] != "VERB":
            continue
        kids = sorted(children_of.get(vi, []))
        agent = None
        patient = None
        agent_conf = None
        patient_conf = None
        for k in kids:
            if upos[k - 1] not in MENTION_UPOS:
                continue
            if k < vi and agent is None:
                agent = tokens[k - 1]
                agent_conf = margins.get(k)
            elif k > vi and patient is None:
                patient = tokens[k - 1]
                patient_conf = margins.get(k)
        if agent is None and patient is None:
            continue
        conf_vals = [c for c in (agent_conf, patient_conf) if c is not None]
        conf = round(sum(conf_vals) / len(conf_vals), 3) if conf_vals else None
        roles.append({
            "verb": tokens[vi - 1],
            "agent": agent,
            "patient": patient,
            "confidence": conf,
        })
    return roles


def main():
    pt = PosTagger.load(POS_MODEL)
    ap = ArcParser.load(ARC_MODEL)

    # gather candidate sentences per hard-feature class, spread across grades
    pool = []  # (grade, line, text, feature_class)
    for grade in GRADES:
        for line, sent in load_grade_lines(grade):
            if len(sent) < 8 or len(sent) > 260:
                continue
            fc = classify_hard_feature(sent)
            pool.append((grade, line, sent, fc))

    # target distribution: bias toward quotative (dominant known failure class)
    TARGETS = {"quotative": 22, "passive": 10, "relative": 10, "PP": 10, "simple": 8}
    by_class = {}
    for item in pool:
        by_class.setdefault(item[3], []).append(item)

    selected = []
    seen_texts = set()
    for cls, tgt in TARGETS.items():
        items = by_class.get(cls, [])
        # spread across grades: round-robin by grade
        by_grade = {}
        for it in items:
            by_grade.setdefault(it[0], []).append(it)
        grade_cycle = list(by_grade.keys())
        idxs = {g: 0 for g in grade_cycle}
        count = 0
        gi = 0
        guard = 0
        while count < tgt and grade_cycle and guard < 5000:
            guard += 1
            g = grade_cycle[gi % len(grade_cycle)]
            gi += 1
            lst = by_grade[g]
            if idxs[g] < len(lst):
                it = lst[idxs[g]]
                idxs[g] += 1
                if it[2] not in seen_texts:
                    selected.append(it)
                    seen_texts.add(it[2])
                    count += 1
            if all(idxs[g] >= len(by_grade[g]) for g in grade_cycle):
                break

    rows = []
    for grade, line, sent, fc in selected:
        toks = tokenize(sent)
        if not toks:
            continue
        upos = pt.tag(toks)
        pr = ap.parse(toks, upos)
        mentions = candidate_mentions(toks, upos)
        roles = candidate_roles(toks, upos, pr)
        rows.append({
            "grade": grade,
            "line": line,
            "text": sent,
            "tokens": toks,
            "candidate_mentions": mentions,
            "candidate_roles": roles,
            "hard_feature_class": fc,
            "gold_verified": False,
            "notes": "",
        })

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "wb") as f:
        for r in rows:
            line = json.dumps(r, ensure_ascii=True) + "\n"
            f.write(line.encode("ascii"))

    # summary
    from collections import Counter
    gc = Counter(r["grade"] for r in rows)
    fcc = Counter(r["hard_feature_class"] for r in rows)
    print("WROTE %s (%d rows)" % (OUT_PATH, len(rows)))
    print("grade distribution: %s" % dict(gc))
    print("hard_feature_class distribution: %s" % dict(fcc))


if __name__ == "__main__":
    main()
