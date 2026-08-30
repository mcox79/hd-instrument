"""exp_coref_focus_stack_oracle_ceiling_v1 -- BAR ITEM 1 (the can-fail ORACLE CEILING, measured FIRST):
does a segment-structured discourse-FOCUS oracle recover the anti-typical coref residual over the salience/
recency floor -- and does it beat mere finer TOKEN-LOCALITY? If a perfect focus-oracle does NOT beat the floor,
the Grosz-Sidner focus-stack is the WRONG lever and that is a rigorous NEGATIVE (the ~50-60% focus share the
research drill estimated is SPECULATIVE / by-elimination -- this cell tests it directly).

PROBLEM: the_coref_residual_needs_a_discourse_focus_stack. The reader mis-binds pronouns on the ANTI-TYPICAL
residual -- cases where the gold antecedent is NOT the most salient/recent/frequent entity (topic-SHIFT cases).
Three integrated results EXCLUDED the other levers (coherence prior REFUTED; static KB dead ~2-3%; interference
a tie). What remains is DISCOURSE ATTENTIONAL STATE (Grosz & Sidner 1986): focus is a STACK of focus-spaces,
segment-structured, pushed/popped as topics open and close; the preferred antecedent is the segment-LOCAL focus
(Cb), not global recency.

THE BRAIN (frame; PINNED vs OUR-INVENTION):
  * PINNED (the computation): reference consults an attentional-state focus that is STRUCTURED by discourse
    segments and shifts with them (Grosz & Sidner 1986, Computational Linguistics 12(3):175-204); the preferred
    antecedent is the segment-local backward-center Cb (Centering; Grosz/Joshi/Weinstein 1995). A topic SHIFT is
    a segment push/pop that changes which entity is in focus -- so local focus != global salience exactly on the
    residual. In narrative, discourse segments are realized as SCENES (paragraphs) and nested DIALOGUE (quoted
    speech has its own focus: speaker/addressee + the referents of the speech), plus local sub-events.
  * OUR-INVENTION-UNDER-TEST (sweep, don't adopt): the exact segmentation rule + granularity, the push/pop
    discipline, the focus-vs-recency weighting. This cell COPIES the computation (segment-local focus outranks
    global recency; the stack lets a backgrounded entity return) and measures the CEILING under the strongest
    available segment signal -- GOLD quote spans + paragraph breaks -- to see if the headroom EXISTS at all.

WHY "ORACLE": build_instances already uses GOLD entity clusters for the candidate pool + prior-mention histories
(perfect CONTEXT coref -- the reader has resolved prior mentions; the SAME setup as the salience floor). The only
"oracle" ingredient here is the SEGMENT BOUNDARIES (gold quotes / paragraphs). A real deployment must DETECT
boundaries from surface text; the gap between the oracle segmentation and a surface-detected one is the
segment-boundary-recovery ceiling (bounded in a sibling cell). So this cell answers ONLY: given perfect segment
structure, is the anti-typical residual focus-recoverable?

POPULATION: the ANTI-TYPICAL competitive residual = every competitive pronoun instance (>=2 gn-compatible priors,
gold among them) where gold is the argmax on NONE of {global recency, subjecthood, frequency} -- i.e.
`gold_structurally_dominated` from exp_coref_graded_cue_retrieval_litbank_v1.error_anatomy, applied to ALL
instances (NOT conditioned on the resolver erring, so the floor is a genuine >0 baseline, not 0-by-construction).

ARMS (accuracy = argmax == gold on the anti-typical residual; per-doc bootstrap CI):
  recency / strict_cb / graded   FLOORS (global salience) recomputed on THIS population.
  token_recency                  FLOOR: finest global recency (closest LAST mention by TOKEN distance) -- the
                                 37.6% "ungateable finer-locality" oracle; the focus arm must beat THIS too.
  focus_quote / focus_para /     FOCUS oracle: prefer the candidate whose most-recent mention is in the HIGHEST
    focus_entshift / focus_best  (nearest) discourse SEGMENT (segment-local focus; ties -> recency), segmentation
                                 by gold quote-spans / paragraph breaks / entity-topic-shift / best-of.
  focus_shuf                     INFO-FREE twin: segment boundary POSITIONS permuted per doc (same count/size
                                 multiset, boundaries randomized) -> focus signal destroyed, pool unchanged. MUST LOSE.
Run: .venv/Scripts/python.exe experiments/exp_coref_focus_stack_oracle_ceiling_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_coref_focus_stack_oracle_ceiling_v1.py --probe
     .venv/Scripts/python.exe experiments/exp_coref_focus_stack_oracle_ceiling_v1.py --run
ASCII only. Pure numpy. Reads the pre-parsed cache + LitBank conll/quotations/original. Writes only its own dir.
NO hdlab/ write. NO external LLM (the invariant).
# KB_REFERENT: data/litbank/who_did_what_events.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_coref_graded_cue_retrieval_litbank_v1 import (  # noqa: E402
    load_streams, build_instances, _supports, arm_recency, arm_strict_cb, arm_graded, tune_graded)
from experiments.exp_litbank_activation_binder_v1 import PRONOUNS, _gn_compat  # noqa: E402

CONLL = os.path.join(REPO, "data", "litbank", "coref", "conll")
QUOTE = os.path.join(REPO, "data", "litbank", "quotations", "tsv")
ORIG = os.path.join(REPO, "data", "litbank", "original")
OUTDIR = os.path.join(REPO, "data", "exp_coref_focus_stack_oracle_ceiling_v1")
SEED = 20260830

# ---------------------------------------------------------------- conll / segment meta (cached per doc)
_META: Dict[str, Dict] = {}


def _doc_meta(doc: str) -> Dict:
    """Per-doc: sent_lens (tokens/sentence), cumulative token offset per sentence, quote-sentence set (gold),
    and the raw tokens per sentence (for surface quote detection / paragraph alignment)."""
    if doc in _META:
        return _META[doc]
    sents: List[List[str]] = []
    cur: List[str] = []
    with open(os.path.join(CONLL, doc + ".conll"), encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("#"):
                continue
            if not line.strip():
                if cur:
                    sents.append(cur); cur = []
                continue
            cur.append(line.split("\t")[3])
    if cur:
        sents.append(cur)
    sent_lens = [len(s) for s in sents]
    cum = [0]
    for L in sent_lens:
        cum.append(cum[-1] + L)
    # gold quote spans -> set of sentence indices inside a quote (dialogue)
    quote_sents = set()
    qpath = os.path.join(QUOTE, doc + ".ann")
    if os.path.exists(qpath):
        with open(qpath, encoding="utf-8") as fh:
            for line in fh:
                p = line.rstrip("\n").split("\t")
                if len(p) >= 6 and p[0] == "QUOTE":
                    try:
                        s0, s1 = int(p[2]), int(p[4])
                    except ValueError:
                        continue
                    for s in range(s0, s1 + 1):
                        quote_sents.add(s)
    m = {"sents": sents, "sent_lens": sent_lens, "cum": cum, "quote_sents": quote_sents,
         "n_sent": len(sents)}
    _META[doc] = m
    return m


def _gpos(doc: str, sent: int, start: int) -> int:
    """Global token index of a mention = cumulative tokens before its sentence + its within-sentence start."""
    m = _doc_meta(doc)
    c = m["cum"]
    s = min(sent, len(c) - 1)
    return c[s] + start


# ---------------------------------------------------------------- rich instances (carry token starts)
def build_rich(streams: List[Dict]) -> List[Dict]:
    """Same competitive instances as build_instances, but prior_rich carries (sent, role, start) per mention and
    the pronoun's own token start -- needed for TOKEN-distance recency and SEGMENT membership. Parent-compatible
    `prior` (sent, role) kept so _supports / arm_* work unchanged."""
    from experiments.exp_coref_graded_cue_retrieval_litbank_v1 import _entity_gn_gold
    out: List[Dict] = []
    for rec in streams:
        stream = rec["stream"]
        egn = _entity_gn_gold(stream)
        prior_rich: Dict[int, List[Tuple[int, str, int]]] = defaultdict(list)
        for m in stream:
            ht = m["head_text"]
            gold = m["gold"]
            if ht in PRONOUNS:
                pg, pn = PRONOUNS[ht]
                cand = {}
                for c, pri in prior_rich.items():
                    if not pri:
                        continue
                    eg, en = egn.get(c, (None, None))
                    if _gn_compat(pg, pn, eg, en):
                        cand[c] = list(pri)
                if gold in cand and len(cand) >= 2:
                    out.append({
                        "doc": rec["doc"], "pronoun": ht, "p_sent": m["sent"], "p_start": m["start"],
                        "pron_role": m["role"], "gold_cid": gold, "cand_ids": sorted(cand),
                        "prior": {c: [(s, r) for (s, r, _st) in cand[c]] for c in cand},
                        "prior_rich": {c: list(cand[c]) for c in cand},
                    })
            prior_rich[gold].append((m["sent"], m["role"], m["start"]))
    return out


def is_antitypical(sup: Dict[str, np.ndarray], gi: int) -> bool:
    """gold is best on NONE of {global recency, subjecthood, frequency} -> the topic-shift / anti-salient case
    (exp_coref_graded_cue_retrieval_litbank_v1.error_anatomy gold_structurally_dominated), resolver-independent."""
    rec_best = int(np.argmax(sup["recency"])) == gi
    subj_best = bool(sup["subject"][gi] == sup["subject"].max())
    freq_best = bool(sup["freq"][gi] == sup["freq"].max())
    return not (rec_best or subj_best or freq_best)


# ---------------------------------------------------------------- segmentations
# Each returns (belong, stack): belong[s] = the frame a mention in sentence s belongs to (its innermost active
# frame); stack[s] = the list of ENCLOSING frames active at sentence s (bottom..top). For SEQUENTIAL segmentations
# (window/para/entshift) frames do not nest -> belong[s]=seg_id[s], stack[s]=[seg_id[s]]. For QUOTE nesting the
# narration is ONE recurring matrix frame (0) and each quote span PUSHES a nested frame that is POPPED at its end --
# so a narration pronoun's focus space EXCLUDES quote mentions (the Grosz-Sidner stack; a closed quote is popped).
def _sequential(seg_ids: List[int]) -> Tuple[List[int], List[List[int]]]:
    return seg_ids, [[s] for s in seg_ids]


def seg_window(doc: str, k: int) -> Tuple[List[int], List[List[int]]]:
    n = _doc_meta(doc)["n_sent"]
    return _sequential([s // k for s in range(n)])


def seg_quote(doc: str) -> Tuple[List[int], List[List[int]]]:
    """NESTED dialogue focus: narration is the matrix frame 0 (recurring); each maximal run of quoted sentences is
    a PUSHED frame (id>=1) that pops when the quote closes. A narration pronoun's stack = [0] (quote mentions,
    belonging to a popped quote frame, are OUT of focus); a quote pronoun's stack = [0, qid]."""
    m = _doc_meta(doc)
    qs = m["quote_sents"]
    belong, stack = [], []
    qid, prev_inq = 0, False
    for s in range(m["n_sent"]):
        inq = s in qs
        if inq and not prev_inq:
            qid += 1               # a new quote span opens -> push a fresh frame
        if inq:
            belong.append(qid); stack.append([0, qid])
        else:
            belong.append(0); stack.append([0])
        prev_inq = inq
    return belong, stack


def seg_para(doc: str) -> Tuple[List[int], List[List[int]]]:
    """Paragraph (scene) segments from the original text (blank-line-delimited), aligned to conll sentences by a
    token-consuming walk. Sequential (sibling scenes; a new paragraph pops the old)."""
    m = _doc_meta(doc)
    path = os.path.join(ORIG, doc.replace("_brat", "") + ".txt")
    if not os.path.exists(path):
        return _sequential([0] * m["n_sent"])
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    paras, cur = [], []
    for line in raw.split("\n"):
        if line.strip():
            cur.append(line.strip())
        else:
            if cur:
                paras.append(" ".join(cur)); cur = []
    if cur:
        paras.append(" ".join(cur))
    def toks(t):
        return "".join(c.lower() if (c.isalnum() or c == " ") else " " for c in t).split()
    para_len = [len(toks(p)) for p in paras]
    seg, pi, consumed = [], 0, 0
    for s in range(m["n_sent"]):
        seg.append(pi)
        consumed += m["sent_lens"][s]
        while pi < len(para_len) - 1 and consumed >= para_len[pi] * 0.85:
            consumed -= para_len[pi]; pi += 1
    return _sequential(seg)


def seg_entshift(doc: str, streams_by_doc: Dict[str, Dict]) -> Tuple[List[int], List[List[int]]]:
    """Entity-topic-shift segments (entity-stream-derived): seg id increments at a sentence whose SUBJECT entity
    differs from the previous subject-bearing sentence's -- a local focus/topic-shift proxy. Sequential. The most
    circularity-prone signal; the info-free boundary-shuffle twin is the control."""
    m = _doc_meta(doc)
    rec = streams_by_doc.get(doc)
    subj_of = {}
    if rec:
        for mm in rec["stream"]:
            if mm["role"] == "SUBJECT":
                subj_of.setdefault(mm["sent"], mm["gold"])
    seg, sid, prev_subj = [], 0, None
    for s in range(m["n_sent"]):
        cur = subj_of.get(s)
        if cur is not None and prev_subj is not None and cur != prev_subj:
            sid += 1
        if cur is not None:
            prev_subj = cur
        seg.append(sid)
    return _sequential(seg)


def _shuffle_quote(belong: List[int], stack: List[List[int]], rng: np.random.Generator):
    """Info-free twin for the NESTED quote frames: keep the SAME NUMBER of quote sentences (same nesting budget),
    randomize WHICH sentences are quoted -> destroys quote-narration alignment, preserves granularity."""
    n = len(belong)
    quote_sents = [i for i in range(n) if len(stack[i]) > 1]
    if not quote_sents:
        return belong, stack
    new_q = set(int(x) for x in rng.choice(np.arange(n), size=len(quote_sents), replace=False))
    nb, ns = [], []
    qid = 0
    prev = False
    for s in range(n):
        inq = s in new_q
        if inq and not prev:
            qid += 1
        if inq:
            nb.append(1000 + qid); ns.append([0, 1000 + qid])
        else:
            nb.append(0); ns.append([0])
        prev = inq
    return nb, ns


# ---------------------------------------------------------------- focus pick (stack discipline)
def focus_pick(inst: Dict, belong: List[int], stack: List[List[int]]) -> int:
    """Grosz-Sidner segment-local focus: the pronoun's focus space is the STACK of enclosing frames at its
    sentence. Consider frames innermost (top) -> outermost (bottom); pick the candidate whose most-recent mention
    BELONGING TO that frame is closest (token recency within the frame). A closed sub-segment (a popped quote) is
    NOT on the stack, so its mentions are OUT of focus -> focus can RETURN to a less-recent same-frame entity that
    global token recency would miss. Fallback (no candidate in any enclosing frame): global token recency."""
    doc = inst["doc"]
    ln = len(belong)
    p_stack = stack[min(inst["p_sent"], ln - 1)]
    ids = inst["cand_ids"]
    for frame in reversed(p_stack):                       # innermost first
        best_i, best_g = -1, -1
        for i, c in enumerate(ids):
            gs = [_gpos(doc, s, st) for (s, r, st) in inst["prior_rich"][c]
                  if belong[min(s, ln - 1)] == frame]
            if gs:
                g = max(gs)
                if g > best_g:
                    best_g, best_i = g, i
        if best_i >= 0:
            return best_i
    return arm_token_recency(inst)


def arm_token_recency(inst: Dict) -> int:
    """Finest global recency: candidate with the closest LAST mention by TOKEN distance (the finer-locality
    floor the focus arm must beat)."""
    doc = inst["doc"]
    ids = inst["cand_ids"]
    best_i, best_g = -1, -1
    for i, c in enumerate(ids):
        g = max(_gpos(doc, s, st) for (s, r, st) in inst["prior_rich"][c])
        if g > best_g:
            best_g, best_i = g, i
    return best_i


# ---------------------------------------------------------------- evaluation
def _ci(pairs, n_boot, seed):
    arr = np.array(pairs, float)
    tot = arr[:, 1].sum()
    acc = arr[:, 0].sum() / tot if tot else 0.0
    r = np.random.default_rng(seed)
    nd = len(arr)
    boots = []
    for _ in range(n_boot):
        idx = r.integers(0, nd, nd)
        c, n = arr[idx, 0].sum(), arr[idx, 1].sum()
        boots.append(c / n if n else 0.0)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"acc": round(acc, 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4), "n": int(tot)}


def _paired(a_map, b_map, n_boot, seed):
    docs = sorted(set(a_map) & set(b_map))
    a = np.array([a_map[d] for d in docs], float)
    b = np.array([b_map[d] for d in docs], float)
    delta = a[:, 0].sum() / max(a[:, 1].sum(), 1) - b[:, 0].sum() / max(b[:, 1].sum(), 1)
    r = np.random.default_rng(seed)
    nd = len(docs)
    boots = []
    for _ in range(n_boot):
        idx = r.integers(0, nd, nd)
        boots.append(a[idx, 0].sum() / max(a[idx, 1].sum(), 1) - b[idx, 0].sum() / max(b[idx, 1].sum(), 1))
    boots = np.array(boots)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    null_p95 = float(np.percentile(np.abs(boots - boots.mean()), 95))
    return {"delta": round(float(delta), 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4),
            "half_width": round(float(hi - lo) / 2, 4), "null_p95": round(null_p95, 4),
            "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}


def run(docs: Optional[int] = None, n_boot: int = 2000, seed: int = SEED, window_k: int = 3) -> Dict:
    streams = load_streams(docs)
    streams_by_doc = {r["doc"]: r for r in streams}
    insts = build_rich(streams)

    # tune the graded floor on the standard dev half (parent's split), apply to all
    parent_insts = build_instances(streams)
    all_docs = sorted({i["doc"] for i in parent_insts})
    dev_docs = set(all_docs[0::2])
    dev = [i for i in parent_insts if i["doc"] in dev_docs]
    weights, gain, d = tune_graded(dev)

    # anti-typical population
    pop = []
    for inst in insts:
        ids, sup, gi = _supports(inst)
        if is_antitypical(sup, gi):
            pop.append((inst, sup, gi))

    rng = np.random.default_rng(seed)
    seg_cache = {}

    def segs_for(doc):
        if doc not in seg_cache:
            seg_cache[doc] = {
                "window": seg_window(doc, window_k),
                "quote": seg_quote(doc),
                "para": seg_para(doc),
                "entshift": seg_entshift(doc, streams_by_doc),
            }
        return seg_cache[doc]

    ARMS = ("recency", "strict_cb", "graded", "token_recency",
            "focus_window", "focus_quote", "focus_para", "focus_entshift", "focus_best", "focus_quote_shuf")
    per_doc = {a: defaultdict(lambda: [0, 0]) for a in ARMS}
    # diagnostic: where does focus_quote DIVERGE from token_recency, and who is right?
    diverge = {"n_diff": 0, "focus_right_token_wrong": 0, "token_right_focus_wrong": 0}

    for inst, sup, gi in pop:
        doc = inst["doc"]
        ids = inst["cand_ids"]
        sg = segs_for(doc)
        qb, qs = sg["quote"]
        qb_sh, qs_sh = _shuffle_quote(qb, qs, rng)
        picks = {
            "recency": arm_recency(ids, sup, gi)["pick"],
            "strict_cb": arm_strict_cb(ids, sup, gi, inst)["pick"],
            "graded": arm_graded(ids, sup, gi, inst, weights, gain, d)["pick"],
            "token_recency": arm_token_recency(inst),
            "focus_window": focus_pick(inst, sg["window"][0], sg["window"][1]),
            "focus_quote": focus_pick(inst, qb, qs),
            "focus_para": focus_pick(inst, sg["para"][0], sg["para"][1]),
            "focus_entshift": focus_pick(inst, sg["entshift"][0], sg["entshift"][1]),
            "focus_quote_shuf": focus_pick(inst, qb_sh, qs_sh),
        }
        focus_variants = [picks["focus_window"], picks["focus_quote"], picks["focus_para"], picks["focus_entshift"]]
        picks["focus_best"] = gi if any(p == gi for p in focus_variants) else picks["focus_quote"]
        if picks["focus_quote"] != picks["token_recency"]:
            diverge["n_diff"] += 1
            diverge["focus_right_token_wrong"] += int(picks["focus_quote"] == gi and picks["token_recency"] != gi)
            diverge["token_right_focus_wrong"] += int(picks["token_recency"] == gi and picks["focus_quote"] != gi)
        for a in ARMS:
            per_doc[a][doc][0] += int(picks[a] == gi)
            per_doc[a][doc][1] += 1

    acc = {a: _ci([tuple(v) for v in per_doc[a].values()], n_boot, seed + 10 + i) for i, a in enumerate(ARMS)}
    floor = "graded"
    contrasts = {}
    for a in ("token_recency", "focus_window", "focus_quote", "focus_para", "focus_entshift", "focus_best"):
        contrasts[a + "_minus_graded"] = _paired(dict(per_doc[a]), dict(per_doc[floor]), n_boot, seed + 40)
    contrasts["focus_best_minus_token_recency"] = _paired(dict(per_doc["focus_best"]), dict(per_doc["token_recency"]), n_boot, seed + 80)
    contrasts["focus_quote_minus_token_recency"] = _paired(dict(per_doc["focus_quote"]), dict(per_doc["token_recency"]), n_boot, seed + 81)
    contrasts["focus_quote_minus_focus_quote_shuf"] = _paired(dict(per_doc["focus_quote"]), dict(per_doc["focus_quote_shuf"]), n_boot, seed + 82)

    n_pop = len(pop)
    return {
        "anchor": "coref_focus_stack_oracle_ceiling_v1",
        "population": "LitBank anti-typical competitive coref residual (gold best on NONE of global recency/subject/freq)",
        "n_docs": len(all_docs), "n_antitypical_instances": n_pop,
        "n_all_competitive_instances": len(insts),
        "tuned_weights": {k: round(v, 3) for k, v in weights.items()}, "window_k": window_k,
        "accuracy": acc,
        "floor_arm": floor,
        "focus_quote_vs_token_recency_divergence": diverge,
        "contrasts": contrasts,
        "reading": _reading(acc, contrasts),
    }


def _reading(acc, contrasts) -> Dict:
    fb = contrasts["focus_best_minus_graded"]                      # focus vs salience floor
    ftl = contrasts["focus_quote_minus_token_recency"]            # focus STACK beyond finer-locality
    tw = contrasts["focus_quote_minus_focus_quote_shuf"]         # vs info-free boundary shuffle
    headroom = fb["band"] == "ABOVE"
    beats_locality = ftl["band"] == "ABOVE"
    twin_loses = tw["band"] == "ABOVE"
    return {
        "focus_oracle_beats_salience_floor_CI_sep": headroom,
        "focus_STACK_beats_token_locality_CI_sep": beats_locality,
        "info_free_quote_shuffle_twin_LOSES_CI_sep": twin_loses,
        "note": ("token-locality is a FLOOR here, not the focus mechanism; the focus STACK earns its keep only "
                 "if it beats token_recency (beats_locality) with the quote-shuffle twin losing"),
        "verdict": ("FOCUS_STACK_ADDS_OVER_LOCALITY_BUILD_IT" if (beats_locality and twin_loses)
                    else ("FOCUS_REDUCES_TO_FINER_LOCALITY_NOT_A_DISTINCT_LEVER" if headroom
                          else "FOCUS_ORACLE_DOES_NOT_CLEAR_FLOOR_RIGOROUS_NEGATIVE")),
    }


# ---------------------------------------------------------------- probe / self-test
def probe():
    streams = load_streams()
    insts = build_rich(streams)
    n_anti = 0
    for inst in insts:
        ids, sup, gi = _supports(inst)
        if is_antitypical(sup, gi):
            n_anti += 1
    d0 = streams[0]["doc"]
    m = _doc_meta(d0)
    # quote alignment sanity
    n_quote_docs = sum(1 for r in streams if _doc_meta(r["doc"])["quote_sents"])
    print(f"n_competitive_instances = {len(insts)}")
    print(f"n_antitypical_instances = {n_anti}  ({n_anti/max(len(insts),1):.3f} of competitive)")
    print(f"doc0 = {d0}: n_sent={m['n_sent']} tot_tok={m['cum'][-1]} quote_sents={len(m['quote_sents'])}")
    print(f"docs_with_gold_quotes = {n_quote_docs}/{len(streams)}")
    qb, qs = seg_quote(d0)
    print(f"seg_quote(doc0) n_quote_sents = {sum(1 for x in qs if len(x)>1)} n_matrix = {sum(1 for x in qs if len(x)==1)}")
    print(f"seg_para(doc0)  n_segments = {max(seg_para(d0)[0])+1}")
    print(f"seg_entshift(doc0) n_segments = {max(seg_entshift(d0, {r['doc']: r for r in streams})[0])+1}")
    # how many anti-typical pronouns sit in a NARRATION sentence with a quote somewhere before them (return-case potential)?
    sbd = {r["doc"]: r for r in streams}
    near_quote = 0
    for inst in insts:
        ids, sup, gi = _supports(inst)
        if not is_antitypical(sup, gi):
            continue
        qb2, qs2 = seg_quote(inst["doc"])
        ps = min(inst["p_sent"], len(qs2) - 1)
        if len(qs2[ps]) == 1 and any(len(qs2[s]) > 1 for s in range(ps)):
            near_quote += 1
    print(f"antitypical pronouns in narration AFTER some quote = {near_quote}")


def dump_cases(n=20, hard_only=True, seed=SEED):
    """Diagnostic: print anti-typical residual cases (optionally only where token-recency ALSO fails -- the truly
    hard core) with surrounding sentence text + each candidate's head word / last mention / role, so a human can
    read what mechanism the brain actually uses. Understanding the wall, per the standing directive."""
    streams = load_streams()
    streams_by_doc = {r["doc"]: r for r in streams}
    insts = build_rich(streams)
    # representative head word per (doc, cluster) = most common non-pronoun head
    head_by = defaultdict(Counter)
    for r in streams:
        for m in r["stream"]:
            if m["head_text"] not in PRONOUNS:
                head_by[(r["doc"], m["gold"])][m["head_text"]] += 1

    def name(doc, c):
        hb = head_by[(doc, c)]
        return hb.most_common(1)[0][0] if hb else "(pron-only)"

    rng = np.random.default_rng(seed)
    cases = []
    for inst in insts:
        ids, sup, gi = _supports(inst)
        if not is_antitypical(sup, gi):
            continue
        tok = arm_token_recency(inst)
        if hard_only and tok == gi:
            continue
        cases.append((inst, sup, gi, tok))
    rng.shuffle(cases)
    print(f"=== {len(cases)} anti-typical {'HARD (token-recency also wrong)' if hard_only else ''} cases; showing {min(n,len(cases))} ===\n")
    for inst, sup, gi, tok in cases[:n]:
        doc = inst["doc"]
        sents = _doc_meta(doc)["sents"]
        ps = inst["p_sent"]
        lo = max(0, ps - 3)
        print(f"--- {doc}  pronoun='{inst['pronoun']}' (role {inst['pron_role']}) sent {ps} ---")
        for s in range(lo, ps + 1):
            if s < len(sents):
                txt = " ".join(sents[s])
                print(f"  [{s}] {txt[:160]}")
        print("  candidates:")
        for i, c in enumerate(inst["cand_ids"]):
            last = max(inst["prior_rich"][c], key=lambda x: (x[0], x[2]))
            tag = "GOLD" if i == gi else ("<-token_pick" if i == tok else "")
            print(f"    {name(doc,c):18s} role_last={last[1]:8s} last_sent={last[0]:3d} nmentions={len(inst['prior_rich'][c])}  {tag}")
        print()


def self_test():
    """Can-fail fixture: a topic-SHIFT case a segment-local focus MUST get and global recency MUST miss.
    Entity A (gold) is the topic of the current segment (seg 1); a distractor B was mentioned MORE RECENTLY but
    inside a just-closed PRIOR segment (seg 0). Global token-recency grabs B; segment-local focus grabs A."""
    # candidate A=1 (gold): subject in sent 4 (current segment). B=2: subject in sent 5 but a different segment.
    inst = {"doc": "__t", "pronoun": "he", "p_sent": 6, "p_start": 0, "pron_role": "SUBJECT",
            "gold_cid": 1, "cand_ids": [1, 2],
            "prior": {1: [(4, "SUBJECT")], 2: [(5, "SUBJECT")]},
            "prior_rich": {1: [(4, "SUBJECT", 0)], 2: [(5, "SUBJECT", 0)]}}
    _META["__t"] = {"sents": [[]], "sent_lens": [10] * 8, "cum": [0, 10, 20, 30, 40, 50, 60, 70, 80],
                    "quote_sents": set(), "n_sent": 8}
    # global token recency: B (sent 5) is closer than A (sent 4) -> picks B (index 1) -> WRONG
    tok = arm_token_recency(inst)
    assert tok == 1, f"token-recency floor MUST grab the more-recent distractor B (got idx {tok})"
    # NESTED quote: sent 5 (B) is INSIDE a quote (pushed frame, POPPED before the pronoun); sent 4 (A) + the
    # pronoun (sent 6) are narration (matrix frame 0). A's mention belongs to frame 0; B's to the quote frame.
    # A narration pronoun's stack=[0] EXCLUDES B -> focus RETURNS to A even though B is more recent.
    belong = [0, 0, 0, 0, 0, 1, 0, 0]         # sent 5 is the quote
    stack = [[0], [0], [0], [0], [0], [0, 1], [0], [0]]
    foc = focus_pick(inst, belong, stack)
    assert foc == 0, f"nested-quote focus MUST return to the matrix topic A (got idx {foc})"
    # info-free shuffle (quote sentence relocated at random) should generally NOT reliably recover A; valid idx only
    rng = np.random.default_rng(0)
    b2, s2 = _shuffle_quote(belong, stack, rng)
    sh = focus_pick(inst, b2, s2)
    assert sh in (0, 1), "shuffle pick must be a valid candidate index"
    del _META["__t"]
    print("SELF-TEST PASS (token-recency grabs the in-quote distractor; nested-quote focus returns to the matrix topic)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--cases", type=int, default=0)
    ap.add_argument("--all-anti", action="store_true", help="dump ALL anti-typical (not only token-hard) cases")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--window-k", type=int, default=3)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.probe:
        probe(); return
    if args.cases:
        dump_cases(n=args.cases, hard_only=not args.all_anti); return
    if args.run:
        m = run(docs=args.docs, n_boot=args.n_boot, window_k=args.window_k)
        os.makedirs(OUTDIR, exist_ok=True)
        tmp = os.path.join(OUTDIR, "metrics.json.tmp")
        with open(tmp, "w", encoding="ascii") as fh:
            json.dump(m, fh, indent=2)
        os.replace(tmp, os.path.join(OUTDIR, "metrics.json"))
        print(json.dumps(m, indent=2))
        return
    print("use --self-test | --probe | --run")


if __name__ == "__main__":
    main()
