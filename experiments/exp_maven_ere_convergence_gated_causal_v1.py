# CELL-TEMPLATE MANDATORY (applicable subset; single bounded local pass, not GPU/sweep/multi-seed):
# - arms_differ_verified at smoke gate (META_RULE_AF; real/ablation/scramble prediction-vector hash)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit / except KeyboardInterrupt: raise BEFORE except Exception (no bare except:,
#   no except BaseException:)
# - crlb_n/a: official positive-only micro-F1 over a fixed real corpus slice; no closed-form noise
#   floor applies -- feasibility is the DEV-measured baseline distance (best_base), see pre-reg.
# - cardinality_ok: EXPECTED n_candidate_pairs == 93308 on the fixed 100-doc dev slice (asserted
#   at runtime, not a swept axis)
# - calibration_check: adaptive_with_discriminator_gate (type_compat threshold = 1.5x TRAIN global
#   rate, computed from TRAIN not hand-tuned; discriminator-fires re-verified at smoke: real arm
#   must fire >=1 positive prediction or the cell halts before interpreting)
# - real_code_path_exercised: self-test constructs the REAL hdlab.pos_tagger.PosTagger.load(...)
#   object and asserts the argument_share cue consults its .tag() output on a tiny synthetic doc
# - deterministic_seeding: true (scramble uses hashlib-seeded _deterministic_perm, per-doc-id keyed,
#   never Python hash() / list(set()) ordering -- PROT-023/F.5)
# - no_leak: cue functions take ONLY {sent_id, offset_start, offset_end, trigger, type} mention-meta
#   dicts -- causal_relations is read exclusively by official_gold_labels() for evaluation, never
#   passed into any cue/gate/predict function (asserted structurally in self-test)
# - progress_logging: n/a (timeout_s well under 1800; single local pass, low-minutes wall time)
# - checkpoint_exempt: true (single bounded local pass, no seed/arm remote-dispatch loop)
# See preregs/2026-08-11_maven_ere_convergence_gated_causal_v1.md for the full pre-reg (bands,
# controls, HP_SCOPE, compute architecture).
"""exp_maven_ere_convergence_gated_causal_v1 -- DECISIVE MINIMAL PROTOTYPE (design-gate, not a
full pipeline): does the validated convergence-gated coincidence-detection SELECTION mechanism
(ProPara process-selection, experiments/exp_propara_bridging_frame_activation_v1.py::
_process_convergent, commit 459098f52, 26x real-vs-scramble discrimination) transfer to MAVEN-ERE
CAUSAL relation-type classification (CAUSE / PRECONDITION / NONE)?

MECHANISM: a candidate ordered event-mention pair (m1, m2) is predicted to carry a causal relation
only if >= MIN_CONVERGENT_CUES independent cues converge on it -- causal-connective presence,
forward narrative order, shared nearby argument-noun, TRAIN-derived event-type-pair compatibility.
This is the SAME coincidence-detection SHAPE validated on ProPara (donate only if >=2 distinct
roles are each filled by >=2 distinct participants), ported from process-type candidates to
relation-type candidates. Convergence-gating is precision-oriented, which suits MAVEN-ERE's severe
skew (97.78% NONE / 1.69% PRECONDITION / 0.53% CAUSE per data/benchmark_trap_check/
maven_ere_results.json -- MEASURED@that file, not re-derived here).

ARMS: REAL (>=2-cue gate) / ABLATION (>=1-cue degenerate gate, isolates whether the >=2 threshold
specifically is load-bearing) / SCRAMBLE (per-doc deterministic non-identity permutation of WHICH
mention's textual evidence is consulted when computing cues for a given mention_id, gold stays on
the real mention_id pairs -- isolates whether the win depends on genuine text-content alignment) /
3 baselines (majority / adjacent-sentence-heuristic / bag-of-event-types) refit + re-evaluated on
the SAME 100-doc dev slice via the EXISTING tools/benchmark_trap_check/maven_ere_trap_check.py
functions (imported, not reimplemented).

NO LLM. NO nltk. stdlib + hdlab.pos_tagger (owned, persisted UD-EWT averaged-perceptron) only.
ASCII-only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check"))

from maven_ere_official_eval import (  # noqa: E402
    candidate_pairs,
    official_gold_labels,
    official_prf,
    macro_f1_all_labels,
    accuracy_pct,
)
from maven_ere_trap_check import (  # noqa: E402
    fit_majority,
    predict_majority,
    predict_adjacent_sentence_heuristic,
    fit_bag_of_event_types,
    predict_bag_of_event_types,
    build_mention_to_type,
)
from hdlab.pos_tagger import PosTagger  # noqa: E402

ANCHOR_NAME = "exp_maven_ere_convergence_gated_causal_v1_smoke"
DATA_DIR = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "maven_ere")
POS_MODEL_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)

N_DEV_DOCS = 100
N_TRAIN_DOCS = 400
CONNECTIVE_SENT_DIST = 1
ARG_WINDOW = 4
MIN_TYPE_SUPPORT = 3
TYPE_COMPAT_MULT = 1.5
SOTA_CAUSAL_F1 = 31.96
EXPECTED_N_PAIRS = 93308

SCRAMBLE_KEY = "maven_ere_causal_convergence_scramble_v1"

# CAUSE-signaling connectives (CITED: standard English causal-connective inventory, same family as
# tools/benchmark_trap_check/maven_ere_trap_check.py's CONNECTIVE_RE, extended for the label
# decision, not just presence detection).
CAUSE_WORDS_RE = re.compile(
    r"\b(?:because(?: of)?|due to|owing to|as a result(?: of)?|result(?:s|ed|ing)? in|"
    r"caus(?:e|es|ed|ing)|so that|thus|therefore|hence|consequently|led to|leading to|thereby)\b",
    re.IGNORECASE,
)
# PRECONDITION-signaling connectives.
PRECOND_WORDS_RE = re.compile(
    r"\b(?:in order to|before|require[sd]?|requiring|needed for|needs?|provided that|given that|"
    r"only if|unless|necessary for|prerequisite|must first|so as to|"
    r"enabl(?:e|es|ed|ing)|allow(?:s|ed|ing)?|permit(?:s|ted|ting)?)\b",
    re.IGNORECASE,
)

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "in", "on", "at", "to", "for", "with", "by",
    "from", "as", "is", "was", "were", "are", "be", "been", "being", "that", "this", "these",
    "those", "it", "its", "he", "she", "they", "them", "his", "her", "their", "which", "who",
    "whom", "whose", "what", "when", "where", "why", "how", "not", "no", "so", "if", "then",
    "than", "also", "such", "other", "some", "any", "all", "each", "more", "most", "one", "two",
    "three", "into", "over", "after", "up", "out", "about",
}


# ============================================================================ deterministic RNG
def _det_seed(key: str) -> int:
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big") % (2 ** 31 - 1)


def _deterministic_perm(key: str, n: int) -> List[int]:
    rng = random.Random(_det_seed(key))
    idx = list(range(n))
    rng.shuffle(idx)
    return idx


def _doc_scramble_perm(doc_id: str, n: int) -> List[int]:
    """Per-doc deterministic non-identity permutation (PROT-023/F.5-compliant). Retries with a
    re-seeded key (never randomness) if degenerate; raises loudly (never silently continues) if
    5 attempts all fail (n=1 always fails -- caller must not invoke for n<2)."""
    for attempt in range(5):
        perm = _deterministic_perm(f"{SCRAMBLE_KEY}::{doc_id}::attempt{attempt}", n)
        if perm == list(range(n)):
            continue
        n_fixed = sum(1 for i in range(n) if perm[i] == i)
        if n_fixed <= max(1, n // 2):
            return perm
    raise RuntimeError(f"SCRAMBLE_DEGENERATE_AFTER_RETRIES: doc={doc_id} n={n}")


# ============================================================================ data loading
def load_jsonl(path: str, limit: Optional[int] = None) -> List[dict]:
    out = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if limit is not None and i >= limit:
                break
            if line.strip():
                out.append(json.loads(line))
    return out


# ============================================================================ per-doc context
def _build_mention_context_meta(doc: dict) -> Dict[str, dict]:
    """mention_id -> {sent_id, offset_start, offset_end, trigger, type}. NO-LEAK: this dict NEVER
    carries relation/label info -- structural/textual fields only (asserted in self-test)."""
    meta = {}
    for ev in doc["events"]:
        etype = ev["type"]
        for m in ev["mention"]:
            meta[m["id"]] = {
                "sent_id": m["sent_id"],
                "offset_start": m["offset"][0],
                "offset_end": m["offset"][1],
                "trigger": m["trigger_word"],
                "type": etype,
            }
    return meta


def _sentence_connective_flags(sentences: List[str]) -> List[Tuple[bool, bool]]:
    return [(bool(CAUSE_WORDS_RE.search(s)), bool(PRECOND_WORDS_RE.search(s))) for s in sentences]


def _mention_arg_window(tokens_by_sent: List[List[str]], pos_by_sent: List[List[str]],
                         sent_id: int, off_start: int, off_end: int) -> Set[str]:
    """+/- ARG_WINDOW non-stopword NOUN/PROPN tokens around the trigger span (real POS tags from
    the loaded hdlab.pos_tagger.PosTagger; MEASURED@this build: MAVEN triggers are frequently
    NOMINAL -- 'attack'/'massacre' tag NOUN not VERB -- so hdlab.candidate_generator's verb-
    anchored parse extraction returns an empty candidate set on such sentences; this POS-window
    proxy is the practical substitute for this minimal prototype, still the real persisted tagger)."""
    toks = tokens_by_sent[sent_id]
    pos = pos_by_sent[sent_id]
    lo = max(0, off_start - ARG_WINDOW)
    hi = min(len(toks), off_end + ARG_WINDOW)
    out: Set[str] = set()
    for i in range(lo, hi):
        if off_start <= i < off_end:
            continue
        if pos[i] not in ("NOUN", "PROPN"):
            continue
        w = toks[i].lower()
        if w in STOPWORDS or len(w) < 2:
            continue
        out.add(w)
    return out


def build_doc_context(doc: dict, tagger: PosTagger) -> dict:
    mention_meta = _build_mention_context_meta(doc)
    sent_flags = _sentence_connective_flags(doc["sentences"])
    tokens_by_sent = doc["tokens"]
    pos_by_sent = [tagger.tag(sent_toks) if sent_toks else [] for sent_toks in tokens_by_sent]
    arg_sets = {
        mid: _mention_arg_window(tokens_by_sent, pos_by_sent, m["sent_id"], m["offset_start"], m["offset_end"])
        for mid, m in mention_meta.items()
    }
    return {"mention_meta": mention_meta, "sent_flags": sent_flags, "arg_sets": arg_sets}


def build_scrambled_context(doc_id: str, context: dict) -> dict:
    """Per-doc deterministic non-identity permutation of WHICH mention's textual evidence
    (meta + arg-window) is used when computing cues FOR a given mention_id; sent_flags (a doc-
    level property, not mention-specific) is unchanged. Gold labels stay keyed to the real
    mention_id -- only the cue-sourcing identity is severed from ground truth."""
    meta = context["mention_meta"]
    mids = sorted(meta.keys())
    n = len(mids)
    if n < 2:
        return context  # no candidate pairs possible; nothing to scramble
    perm = _doc_scramble_perm(doc_id, n)
    scrambled_meta = {mids[i]: meta[mids[perm[i]]] for i in range(n)}
    scrambled_arg = {mids[i]: context["arg_sets"][mids[perm[i]]] for i in range(n)}
    return {"mention_meta": scrambled_meta, "arg_sets": scrambled_arg, "sent_flags": context["sent_flags"]}


# ============================================================================ TRAIN-only priors
def fit_type_pair_table(train_docs: List[dict]):
    """TRAIN-only positive-rate + majority-label-among-positives per ordered event-type pair.
    NEVER reads dev gold -- a legitimate corpus-statistic prior, not gold-peeking on dev."""
    totals: Counter = Counter()
    positives: Counter = Counter()
    pos_label_counts: Dict[Tuple[str, str], Counter] = defaultdict(Counter)
    global_total = 0
    global_pos = 0
    global_label_counts: Counter = Counter()
    for doc in train_docs:
        gold = official_gold_labels(doc, "causal")
        m2t = build_mention_to_type(doc)
        for (m1, m2), label in gold.items():
            key = (m2t[m1], m2t[m2])
            totals[key] += 1
            global_total += 1
            if label != 0:
                positives[key] += 1
                global_pos += 1
                pos_label_counts[key][label] += 1
                global_label_counts[label] += 1
    rate_table = {k: positives[k] / totals[k] for k in totals if totals[k] >= MIN_TYPE_SUPPORT}
    global_rate = (global_pos / global_total) if global_total else 0.0
    majority_table = {k: c.most_common(1)[0][0] for k, c in pos_label_counts.items()}
    global_majority = global_label_counts.most_common(1)[0][0] if global_label_counts else 1
    return rate_table, global_rate, majority_table, global_majority


# ============================================================================ cues + gate
def _pair_cues(m1_meta: dict, m2_meta: dict, sent_flags: List[Tuple[bool, bool]],
                arg1: Set[str], arg2: Set[str], type_rate_table: Dict[Tuple[str, str], float],
                global_rate: float) -> dict:
    """4 independent cues for ordered pair (m1_meta, m2_meta). Reads ONLY mention-meta fields
    (sent_id/offset/type) + arg-windows + TRAIN-derived priors -- never causal_relations."""
    s1, s2 = m1_meta["sent_id"], m2_meta["sent_id"]
    lo, hi = min(s1, s2), max(s1, s2)
    if abs(s1 - s2) <= CONNECTIVE_SENT_DIST:
        cause_hit = any(sent_flags[i][0] for i in range(lo, hi + 1))
        precond_hit = any(sent_flags[i][1] for i in range(lo, hi + 1))
    else:
        cause_hit = precond_hit = False
    cue_connective = cause_hit or precond_hit
    cue_order = (s1, m1_meta["offset_start"]) <= (s2, m2_meta["offset_start"])
    cue_argument_share = bool(arg1 & arg2)
    key = (m1_meta["type"], m2_meta["type"])
    rate = type_rate_table.get(key)
    cue_type_compat = (rate is not None) and (rate > TYPE_COMPAT_MULT * global_rate)
    n_other_fired = int(cue_connective) + int(cue_argument_share) + int(cue_type_compat)
    n_fired = n_other_fired + int(cue_order)
    return {
        "cause_hit": cause_hit, "precond_hit": precond_hit,
        "cue_connective": cue_connective, "cue_order": cue_order,
        "cue_argument_share": cue_argument_share, "cue_type_compat": cue_type_compat,
        "n_fired": n_fired, "n_other_fired": n_other_fired, "type_pair": key,
    }


def _gate_pass(cues: dict, min_convergent: int) -> bool:
    """MECHANISM-BUG FIX (found at self-test, before any dev-slice run, per no-silent-swallow
    discipline -- fixed here, not patched around): cue_order is the ONLY cue that distinguishes
    (m1,m2) from (m2,m1) -- cue_connective/argument_share/type_compat can each fire identically in
    BOTH directions of an unordered pair (e.g. a shared connective window or shared argument noun
    doesn't care which mention is 'first'). Treating cue_order as merely one-of-four let BOTH
    directions of a genuine relation clear a same-sentence 'any 2 of 4' gate simultaneously,
    double-firing (one direction right, one direction structurally wrong, crushing precision by
    construction). FIX: cue_order is now a NECESSARY cue (only the forward-ordered direction of
    any unordered pair can ever pass), and the OTHER 3 cues supply the >=1 (min_convergent=2) or
    >=0 (min_convergent=1, ablation) corroborating convergent evidence beyond mere order."""
    return cues["cue_order"] and (cues["n_other_fired"] >= (min_convergent - 1))


def _decide_label(cues: dict, majority_table: Dict[Tuple[str, str], int], global_majority: int) -> int:
    if cues["cause_hit"]:
        return 2
    if cues["precond_hit"]:
        return 1
    return majority_table.get(cues["type_pair"], global_majority)


def build_predictions(doc: dict, context: dict, type_rate_table: Dict[Tuple[str, str], float],
                       global_rate: float, majority_table: Dict[Tuple[str, str], int],
                       global_majority: int, min_convergent: int) -> Dict[Tuple[str, str], int]:
    keys, _ = candidate_pairs(doc)
    meta = context["mention_meta"]
    arg_sets = context["arg_sets"]
    sent_flags = context["sent_flags"]
    pred: Dict[Tuple[str, str], int] = {}
    for (m1, m2) in keys:
        cues = _pair_cues(meta[m1], meta[m2], sent_flags, arg_sets[m1], arg_sets[m2],
                           type_rate_table, global_rate)
        if _gate_pass(cues, min_convergent):
            pred[(m1, m2)] = _decide_label(cues, majority_table, global_majority)
        else:
            pred[(m1, m2)] = 0
    return pred


# ============================================================================ evaluation
def eval_arm(docs: List[dict], gold_cache: List[dict], predict_fn) -> dict:
    all_gold: List[int] = []
    all_pred: List[int] = []
    for doc, gold in zip(docs, gold_cache):
        pred = predict_fn(doc)
        for k, v in gold.items():
            all_gold.append(v)
            all_pred.append(pred[k])
    n = len(all_gold)
    return {
        "official_micro_f1_positive_only": official_prf(all_gold, all_pred, "causal"),
        "macro_f1_all_labels": macro_f1_all_labels(all_gold, all_pred, "causal"),
        "accuracy_pct": accuracy_pct(all_gold, all_pred),
        "n_candidate_pairs": n,
    }


def _pred_vector_hash(docs: List[dict], gold_cache: List[dict], predict_fn) -> str:
    h = hashlib.sha256()
    for doc, gold in zip(docs, gold_cache):
        pred = predict_fn(doc)
        for k in gold.keys():
            h.update(str(pred[k]).encode("ascii"))
    return h.hexdigest()


# ============================================================================ crash diagnostic
def _write_crash_metrics(output_dir: str, anchor_name: str, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


# ============================================================================ self-test
def _selftest() -> dict:
    """Tiny synthetic doc, REAL code path (loads the actual persisted PosTagger, not a synthetic-
    only branch), exercises cues/gate/scramble/ablation/no-leak-structure/arms-differ at N~4
    mentions across 2 tiny docs."""
    tagger = PosTagger.load(POS_MODEL_PATH)
    assert isinstance(tagger, PosTagger), "REAL_CODE_PATH: self-test must construct the real PosTagger"

    # doc A: connective("because") present, order forward, shared argument noun "storm" near both
    # triggers -- 3/4 cues should fire (type_compat depends on the TRAIN fit, tested separately).
    doc_a = {
        "id": "toyA",
        "sentences": [
            "The storm arrived over the coast.",
            "The village flooded because of the storm.",
        ],
        "tokens": [
            ["The", "storm", "arrived", "over", "the", "coast", "."],
            ["The", "village", "flooded", "because", "of", "the", "storm", "."],
        ],
        "events": [
            {"id": "e1", "type": "Arriving", "mention": [{"id": "a_m1", "sent_id": 0, "offset": [2, 3], "trigger_word": "arrived"}]},
            {"id": "e2", "type": "Flood", "mention": [{"id": "a_m2", "sent_id": 1, "offset": [2, 3], "trigger_word": "flooded"}]},
        ],
        "causal_relations": {"CAUSE": [["e1", "e2"]], "PRECONDITION": []},
        "subevent_relations": [],
    }
    ctx_a = build_doc_context(doc_a, tagger)
    meta = ctx_a["mention_meta"]
    assert set(meta["a_m1"].keys()) == {"sent_id", "offset_start", "offset_end", "trigger", "type"}, (
        "NO_LEAK_VIOLATION: mention-meta dict must carry only structural fields, never relation/label info")
    assert "storm" in ctx_a["arg_sets"]["a_m1"], f"REAL_CODE_PATH: expected POS-tagged NOUN 'storm' near trigger, got {ctx_a['arg_sets']['a_m1']}"
    assert "storm" in ctx_a["arg_sets"]["a_m2"], f"expected shared arg 'storm' near second trigger, got {ctx_a['arg_sets']['a_m2']}"

    cues = _pair_cues(meta["a_m1"], meta["a_m2"], ctx_a["sent_flags"], ctx_a["arg_sets"]["a_m1"],
                       ctx_a["arg_sets"]["a_m2"], {}, 0.0)
    assert cues["cause_hit"] is True, f"expected CAUSE connective hit, got {cues}"
    assert cues["cue_order"] is True, f"expected forward order (m1 before m2), got {cues}"
    assert cues["cue_argument_share"] is True, f"expected shared-argument cue to fire on 'storm', got {cues}"
    assert cues["n_fired"] >= 3, f"expected >=3 cues firing (connective+order+argument), got {cues}"

    pred_gate2 = build_predictions(doc_a, ctx_a, {}, 0.0, {}, 1, min_convergent=2)
    assert pred_gate2[("a_m1", "a_m2")] == 2, f"expected gate to pass and predict CAUSE, got {pred_gate2}"
    assert pred_gate2[("a_m2", "a_m1")] == 0, f"reverse direction should not fire (order cue fails), got {pred_gate2}"

    # doc B: no connective, no shared argument, reverse order -- gate must NOT fire at min=2.
    doc_b = {
        "id": "toyB",
        "sentences": ["A man ran.", "A bell rang somewhere else."],
        "tokens": [["A", "man", "ran", "."], ["A", "bell", "rang", "somewhere", "else", "."]],
        "events": [
            {"id": "e1", "type": "Motion", "mention": [{"id": "b_m1", "sent_id": 0, "offset": [2, 3], "trigger_word": "ran"}]},
            {"id": "e2", "type": "Sound", "mention": [{"id": "b_m2", "sent_id": 1, "offset": [2, 3], "trigger_word": "rang"}]},
        ],
        "causal_relations": {"CAUSE": [], "PRECONDITION": []},
        "subevent_relations": [],
    }
    ctx_b = build_doc_context(doc_b, tagger)
    pred_b_gate2 = build_predictions(doc_b, ctx_b, {}, 0.0, {}, 1, min_convergent=2)
    assert pred_b_gate2[("b_m1", "b_m2")] == 0 and pred_b_gate2[("b_m2", "b_m1")] == 0, (
        f"expected NO prediction on docB (only order cue can fire, 1 < min_convergent=2), got {pred_b_gate2}")

    # ABLATION (min_convergent=1): order cue alone should now be enough to fire on ONE direction.
    pred_b_gate1 = build_predictions(doc_b, ctx_b, {}, 0.0, {}, 1, min_convergent=1)
    n_fired_b = sum(1 for v in pred_b_gate1.values() if v != 0)
    assert n_fired_b >= 1, f"ABLATION_SANITY: min_convergent=1 should fire on docB's order-only cue, got {pred_b_gate1}"

    # SCRAMBLE: on doc_a (2 mentions), scrambling swaps which evidence each mention_id sees --
    # cause_hit for (a_m1,a_m2) must no longer be computed against the real 'because' sentence
    # window in the same way once identities are swapped (with n=2 the swap is total: a_m1 now
    # "sees" a_m2's position/type and vice versa) -- predictions must differ from the real arm.
    ctx_a_scrambled = build_scrambled_context("toyA", ctx_a)
    pred_a_scrambled = build_predictions(doc_a, ctx_a_scrambled, {}, 0.0, {}, 1, min_convergent=2)
    assert pred_a_scrambled != pred_gate2, (
        f"SCRAMBLE_NO_OP: scrambled predictions must differ from real predictions, got real={pred_gate2} scrambled={pred_a_scrambled}")

    # fit_type_pair_table on a tiny synthetic TRAIN list -- exercises the real code path.
    rate_table, global_rate, majority_table, global_majority = fit_type_pair_table([doc_a, doc_b])
    assert rate_table.get(("Arriving", "Flood")) is None, (
        "MIN_SUPPORT gate should exclude a type pair seen only once (support=1 < MIN_TYPE_SUPPORT=3)")
    assert global_rate > 0.0, f"expected nonzero global positive rate from doc_a's one CAUSE pair, got {global_rate}"
    assert majority_table.get(("Arriving", "Flood")) == 2, f"expected CAUSE(2) majority for the one seen positive type pair, got {majority_table}"

    # arms-must-differ hash check (META_RULE_AF): real vs ablation vs scramble predictions,
    # combined across BOTH docs (docA alone has n_other_fired>=1 so gate=1 and gate=2 coincide
    # there -- docB's order-only-cue case is what actually distinguishes ablation from real).
    def _hash_pred(pred: dict) -> str:
        return hashlib.sha256(json.dumps(sorted(pred.items())).encode("ascii")).hexdigest()

    pred_a_gate1 = build_predictions(doc_a, ctx_a, {}, 0.0, {}, 1, min_convergent=1)
    ctx_b_scrambled = build_scrambled_context("toyB", ctx_b)
    pred_b_scrambled = build_predictions(doc_b, ctx_b_scrambled, {}, 0.0, {}, 1, min_convergent=2)

    real_combined = {**{("A", *k): v for k, v in pred_gate2.items()}, **{("B", *k): v for k, v in pred_b_gate2.items()}}
    ablation_combined = {**{("A", *k): v for k, v in pred_a_gate1.items()}, **{("B", *k): v for k, v in pred_b_gate1.items()}}
    scramble_combined = {**{("A", *k): v for k, v in pred_a_scrambled.items()}, **{("B", *k): v for k, v in pred_b_scrambled.items()}}
    digests = {
        "real": _hash_pred(real_combined),
        "ablation": _hash_pred(ablation_combined),
        "scramble": _hash_pred(scramble_combined),
    }
    assert len(set(digests.values())) == len(digests), f"META_RULE_AF VIOLATION: arms not all distinct: {digests}"

    return {
        "self_test": "PASS",
        "cues_docA": cues,
        "pred_docA_gate2": {f"{k[0]}->{k[1]}": v for k, v in pred_gate2.items()},
        "arms_differ_digests": digests,
    }


# ============================================================================ main
def run(self_test: bool = False):
    if self_test:
        return _selftest()

    t0 = time.time()
    print(f"[START] {ANCHOR_NAME} pid={os.getpid()}", flush=True)

    train_path = os.path.join(DATA_DIR, "train.jsonl")
    dev_path = os.path.join(DATA_DIR, "valid.jsonl")
    if not os.path.exists(train_path) or not os.path.exists(dev_path):
        raise FileNotFoundError(f"MAVEN-ERE data not found at {DATA_DIR}")

    train_all = load_jsonl(train_path, limit=N_TRAIN_DOCS * 3)  # over-read then sort+slice deterministically
    train_docs = sorted(train_all, key=lambda d: d["id"])[:N_TRAIN_DOCS]
    dev_all = load_jsonl(dev_path)
    dev_docs = sorted(dev_all, key=lambda d: d["id"])[:N_DEV_DOCS]
    print(f"[LOAD] train_docs={len(train_docs)} dev_docs={len(dev_docs)}", flush=True)

    tagger = PosTagger.load(POS_MODEL_PATH)

    dev_gold = [official_gold_labels(d, "causal") for d in dev_docs]
    n_pairs_total = sum(len(g) for g in dev_gold)
    if n_pairs_total != EXPECTED_N_PAIRS:
        raise RuntimeError(
            f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected {EXPECTED_N_PAIRS} candidate "
            f"pairs on the 100-doc dev slice, got {n_pairs_total} (data/environment drift)")
    print(f"[CARDINALITY] n_candidate_pairs={n_pairs_total} (matches pre-registered EXPECTED_N_PAIRS)", flush=True)

    # ---------------------------------------------------------------- TRAIN-only priors
    type_rate_table, global_rate, majority_table, global_majority = fit_type_pair_table(train_docs)
    print(f"[FIT] type_pair_keys_with_support={len(type_rate_table)} global_rate={global_rate:.5f} "
          f"global_majority_label={global_majority}", flush=True)

    # ---------------------------------------------------------------- baselines (SAME slice)
    train_gold = [official_gold_labels(d, "causal") for d in train_docs]
    maj_label, _ = fit_majority(train_gold)
    bag_table, bag_fallback, bag_n_keys = fit_bag_of_event_types(train_docs, train_gold)
    print(f"[FIT] majority_label={maj_label} bag_table_keys={bag_n_keys}", flush=True)

    baseline_results = {
        "majority": eval_arm(dev_docs, dev_gold, lambda d: predict_majority(d, maj_label)),
        "adjacent_sentence_heuristic": eval_arm(dev_docs, dev_gold, predict_adjacent_sentence_heuristic),
        "bag_of_event_types": eval_arm(dev_docs, dev_gold, lambda d: predict_bag_of_event_types(d, bag_table, bag_fallback)),
    }
    print(f"[BASELINES] " + json.dumps({k: v["official_micro_f1_positive_only"]["f1"] for k, v in baseline_results.items()}), flush=True)

    # ---------------------------------------------------------------- REAL / ABLATION / SCRAMBLE contexts
    print("[CONTEXT] building per-doc contexts (POS-tagging each sentence once per doc)...", flush=True)
    real_contexts: Dict[str, dict] = {}
    scrambled_contexts: Dict[str, dict] = {}
    for i, doc in enumerate(dev_docs):
        ctx = build_doc_context(doc, tagger)
        real_contexts[doc["id"]] = ctx
        scrambled_contexts[doc["id"]] = build_scrambled_context(doc["id"], ctx)
        if (i + 1) % 25 == 0:
            print(f"[CONTEXT] {i + 1}/{len(dev_docs)} docs processed elapsed={time.time() - t0:.1f}s", flush=True)

    def _predict_real(d):
        return build_predictions(d, real_contexts[d["id"]], type_rate_table, global_rate,
                                  majority_table, global_majority, min_convergent=2)

    def _predict_ablation(d):
        return build_predictions(d, real_contexts[d["id"]], type_rate_table, global_rate,
                                  majority_table, global_majority, min_convergent=1)

    def _predict_scramble(d):
        return build_predictions(d, scrambled_contexts[d["id"]], type_rate_table, global_rate,
                                  majority_table, global_majority, min_convergent=2)

    real_eval = eval_arm(dev_docs, dev_gold, _predict_real)
    ablation_eval = eval_arm(dev_docs, dev_gold, _predict_ablation)
    scramble_eval = eval_arm(dev_docs, dev_gold, _predict_scramble)
    print(f"[ARMS] real_f1={real_eval['official_micro_f1_positive_only']['f1']:.4f} "
          f"ablation_f1={ablation_eval['official_micro_f1_positive_only']['f1']:.4f} "
          f"scramble_f1={scramble_eval['official_micro_f1_positive_only']['f1']:.4f}", flush=True)

    # ---------------------------------------------------------------- discriminator-fires gate
    n_real_positive = sum(1 for doc in dev_docs for v in _predict_real(doc).values() if v != 0)
    if n_real_positive == 0:
        raise RuntimeError("DISCRIMINATOR_DOES_NOT_FIRE: real arm predicted zero positive relations; cannot interpret")
    print(f"[DISCRIMINATOR] real arm fires {n_real_positive} positive predictions", flush=True)

    # ---------------------------------------------------------------- arms-must-differ (META_RULE_AF)
    real_hash = _pred_vector_hash(dev_docs, dev_gold, _predict_real)
    ablation_hash = _pred_vector_hash(dev_docs, dev_gold, _predict_ablation)
    scramble_hash = _pred_vector_hash(dev_docs, dev_gold, _predict_scramble)
    digests = {"real": real_hash, "ablation": ablation_hash, "scramble": scramble_hash}
    assert len(set(digests.values())) == 3, f"META_RULE_AF VIOLATION: arms not all distinct: {digests}"

    # ---------------------------------------------------------------- bands + verdict
    real_f1 = real_eval["official_micro_f1_positive_only"]["f1"]
    real_precision = real_eval["official_micro_f1_positive_only"]["precision"]
    ablation_f1 = ablation_eval["official_micro_f1_positive_only"]["f1"]
    ablation_precision = ablation_eval["official_micro_f1_positive_only"]["precision"]
    scramble_f1 = scramble_eval["official_micro_f1_positive_only"]["f1"]
    best_base = max(v["official_micro_f1_positive_only"]["f1"] for v in baseline_results.values())

    beats_baseline = real_f1 >= max(1.0, 2.0 * best_base)
    scramble_collapses = scramble_f1 <= 0.5 * real_f1 if real_f1 > 0 else False
    ablation_collapses = (ablation_f1 <= 0.8 * real_f1) or (ablation_precision < 0.5 * real_precision) if real_f1 > 0 else False
    headroom_survives = (SOTA_CAUSAL_F1 - real_f1) >= 15.0

    not_meaningful = real_f1 < max(1.0, 1.3 * best_base)
    scramble_no_collapse = (scramble_f1 > 0.8 * real_f1) if real_f1 > 0 else True
    ablation_not_load_bearing = ablation_f1 >= real_f1

    if not_meaningful or scramble_no_collapse or ablation_not_load_bearing:
        band = "HARD-FAIL"
    elif beats_baseline and scramble_collapses and ablation_collapses and headroom_survives:
        band = "HARD-PASS"
    else:
        band = "MIDDLE_BAND"

    verdict_msg = (
        f"real_f1={real_f1:.4f} best_base={best_base:.4f} beats_baseline={beats_baseline} "
        f"scramble_f1={scramble_f1:.4f} scramble_collapses={scramble_collapses} "
        f"ablation_f1={ablation_f1:.4f} ablation_collapses={ablation_collapses} "
        f"headroom_to_sota={SOTA_CAUSAL_F1 - real_f1:.2f} band={band}"
    )
    print(f"[VERDICT] {verdict_msg}", flush=True)

    elapsed = time.time() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": "smoke",
        "verdict": band,
        "verdict_msg": verdict_msg,
        "summary": f"MAVEN-ERE convergence-gated causal relation classification: {band}",
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "n_dev_docs": len(dev_docs),
        "n_train_docs": len(train_docs),
        "n_candidate_pairs": n_pairs_total,
        "n_real_positive_predictions": n_real_positive,
        "cue_design": {
            "min_convergent_cues_real": 2,
            "min_convergent_cues_ablation": 1,
            "connective_sent_dist": CONNECTIVE_SENT_DIST,
            "arg_window": ARG_WINDOW,
            "min_type_support": MIN_TYPE_SUPPORT,
            "type_compat_mult": TYPE_COMPAT_MULT,
            "global_type_positive_rate_train": global_rate,
            "global_majority_label_train": global_majority,
            "n_type_pair_keys_with_support": len(type_rate_table),
        },
        "arms": {
            "real": real_eval,
            "ablation": ablation_eval,
            "scramble": scramble_eval,
        },
        "baselines_on_slice": baseline_results,
        "cited_published_baselines": {
            "sota_causal_f1_protoem_2023": SOTA_CAUSAL_F1,
            "note": "CITED from data/benchmark_trap_check/maven_ere_results.json; not re-derived here.",
        },
        "bands_prereg": {
            "beats_baseline": beats_baseline,
            "scramble_collapses": scramble_collapses,
            "ablation_collapses": ablation_collapses,
            "headroom_survives": headroom_survives,
            "not_meaningful": not_meaningful,
            "scramble_no_collapse": scramble_no_collapse,
            "ablation_not_load_bearing": ablation_not_load_bearing,
        },
        "arms_differ_digests": digests,
        "arms_differ_verified": True,
        "no_leak_verified": True,
        "deterministic_seeding": True,
        "cardinality_ok": True,
        "checkpoint_exempt": True,
        "prereg_path": "preregs/2026-08-11_maven_ere_convergence_gated_causal_v1.md",
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final_path = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, final_path)
    print(f"[DONE] wrote {final_path} elapsed={elapsed:.1f}s", flush=True)
    return metrics


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    try:
        out = run(self_test=args.self_test)
        if args.self_test:
            print(json.dumps({k: v for k, v in out.items() if k != "pred_docA_gate2"}, indent=2, default=str))
            print("[SELF-TEST] PASS")
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}", file=sys.stderr)
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise
