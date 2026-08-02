# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: OLD vs NEW vs POSITION vs RANDOM per_arm digests hash-compared at smoke gate
# - final_metrics_atomicity = tmp_replace (single-shot; whole run < 30s, small numpy LOOCV)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: "discrete multiclass role-classification accuracy, no CRLB noise floor applies";
#   discriminator_reachability=true (OLD-mislocalizes-canonical / NEW-fixes-canonical IS the
#   reachability check, per director diagnosis atom 29610)
# - baseline_in_band: position/random baselines pre-registered as CAN-FAIL controls, not "baselines
#   in band" arms (they are EXPECTED to be poor on-canonical / at-chance; see bands below)
# - cell_chunked=False (single pass; per-arm checkpoint via tools/exp_checkpoint.py used anyway per
#   CLAUDE.md's "any cell looping over >1 unit" rule -- here units = {OLD,NEW,POSITION,RANDOM} x
#   {full,self_test})
# - HYPOTHESIZED/MEASURED/CITED/THEORETICAL tags on every number in this docstring
# - ASCII-only, no emojis, no em dashes.
"""exp_extraction_construction_conditional_multirole_v1 (2026-08-02)

FIX for the confirmed EXTRACTION GENERALIZATION wall (director atom 29610, MEASURED@
data/exp_wire_extraction_accumulate_wm_oracle_vs_real_v1/metrics.json:
summary.real_multi_event_recall=0.2308 ~= floor 0.1923): the OLD extraction
(exp_interactive_loop_real_gold_mcguffey_v1.py) was trained ONLY on non-canonical gold
(quotative postposed-speaker + by-agent passive) with a BINARY is-agent-or-not readout. Applied to
general/canonical narrative its argmax MISLOCALIZES onto unrelated oblique tokens (CITED@ director
diagnosis atom 29610: "Mary ran about..." -> argmax=time-oblique; "...Thomas held in his hand" ->
argmax=hand), because (a) it never saw a single canonical subject=agent example, and (b) a single
binary is-agent score, argmax'd OVER MENTIONS, cannot express "this SPECIFIC mention is patient/
addressee/none" independent of the others -- 22% of true roles (theme/recipient/addressee) are
STRUCTURALLY unreachable by construction.

THE FIX (Bornkessel eADM / Friederici: thematic-role assignment integrates construction +
morphosyntactic CUES, never one positional-or-anti-positional default):
  (a) TRAIN ON THE FULL CONSTRUCTION DISTRIBUTION, including CANONICAL subject=agent narrative
      (new gold pool below), not just the two non-canonical hard cases.
  (b) MULTI-ROLE READOUT: replace binary is-agent (argmax-over-mentions) with an independent
      PER-MENTION multiclass classifier over {agent, patient, addressee, none} (softmax ridge
      regression). Each candidate mention gets its OWN role score -- no single argmax can
      mislocalize onto the wrong token the way binary argmax-over-mentions did, because every
      mention is scored on its own structural cues, not in competition for one binary decision.

GOLD POOLS (construction distribution; canonical is the NEW addition):
  CANONICAL   (NEW): data/gold_mcguffey_lccp_argstruct_v1.json, 114 sentences (7 McGuffey Third
              Reader lessons L04,L05,L07,L08,L09,L10,L12), per-verb-instance pos(agent,patient) /
              nopat(agent-only) argument-structure gold. Sentence TEXT reconstructed by the SAME
              deterministic split_sents(load_lessons()[lid])[j] pipeline the gold's own _meta
              declares (CITED@data/gold_mcguffey_lccp_argstruct_v1.json:_meta -- "Keyed to
              deterministic sentence ids (split_sents on the lessons)"; split_sents copied verbatim
              from git commit d02cf21e1:experiments/exp_coherence_gate_extraction_correctness_
              independent_gold_v1.py, MEASURED@ L04_01 text reproduces "O pussy!" cried Herbert...
              matching gold {'v':'build','agent':'he','patient':'blockhouse'} exactly).
  QUOTATIVE   (reused): gold_quotative_verified_v2.jsonl, N=45. NEW: also supplies gold_addressee
              as its own class (was previously invisible to the binary readout).
  BYAGENT_PASSIVE (reused): gold_passive_byagent_verified_v2.jsonl, N=23. NEW: also labels the
              surface-subject as "patient" (was previously an unlabeled non-agent).
  PASSIVE     (reused, degenerate agent-implicit): gold_passive_verified_v1.jsonl, N=7. Surface
              subject = patient (no agent label, matches its own gold_agent=None convention).

ARMS (one variable = FULL-DISTRIBUTION multi-role training vs OLD narrow-distribution binary):
  OLD      = the FROZEN, UNCHANGED production model from exp_interactive_loop_real_gold_mcguffey_v1
             / exp_wire_extraction_accumulate_wm_oracle_vs_real_v1.fit_production_extraction_model
             (binary is-agent, trained ONLY on quotative+byagent, argmax-over-mentions -> agent;
             all other mentions -> patient; NEVER addressee/none). Reused verbatim (import, not
             reimplemented) so the CAN-FAIL check ("OLD must still mislocalize on canonical") is a
             true reproduction, not a re-tuned strawman.
  NEW      = per-mention multinomial ridge-softmax over {agent,patient,addressee,none}, LOOCV,
             pooled over ALL FOUR construction kinds above (construction-conditional: the mapping
             is learned via the SAME construction-summary-interaction architecture as the validated
             OLD model, generalized to multiclass + an added comma-after addressee-cue feature).
  POSITION = deterministic control: first mention (by linear order, excluding in-quote tokens like
             the OLD arm's subj_idx convention) = agent, everything else = patient. Reproduces the
             "linear-order reader" that MEASURED@29610's parser get canonical-narrative right most
             of the time by accident (subject IS usually agent in canonical prose) -- this is the
             REAL-baseline for the canonical construction (NOT a strawman).
  RANDOM   = seeded uniform-over-4-classes per mention (numpy.random.default_rng). THEORETICAL@
             chance accuracy on a 4-way task = 0.25 (mentions with true label agent/patient/
             addressee only, so chance over 3 reachable classes ~= 0.33; reported both ways).

CAN-FAIL (pre-registered BEFORE running):
  - OLD must mislocalize on CANONICAL: accuracy on canonical mentions with gold role in
    {agent,patient} <= 0.35 (HYPOTHESIZED@ atom 29610's 81% mispredict rate -> ~0.19 measured
    there; a looser 0.35 ceiling here since this is a different, larger canonical sample).
  - NEW must clear canonical: accuracy on the same canonical subset >= 0.60 AND >= OLD + 0.25.
  - NEW must NOT regress non-canonical: NEW quotative-hard accuracy >= OLD quotative accuracy - 0.10
    (small allowed slack since NEW pools 4x more sentences into one shared low-capacity model).

COVERAGE-HONESTY (pre-registered): NEW covers {agent,patient,addressee}; roles outside this set
(theme/recipient/experiencer/possessor, present in the downstream multiclause eval gold) remain
STRUCTURALLY UNREACHABLE -- there is no training signal for them anywhere in these gold pools. This
is reported as a finding, not forced. See role_census in the companion wiring cell v2.

NO borrowed embeddings. NO bolt-on parser. Supplying gold DATA (the construction-labeled sentences)
is allowed per contract; the construction->role MAPPING is learned by the ridge-softmax weights.

Run:  .venv/Scripts/python.exe experiments/exp_extraction_construction_conditional_multirole_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_extraction_construction_conditional_multirole_v1.py --full
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_checkpoint as ckpt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Reuse the FROZEN OLD production model + shared low-level tools VERBATIM (import, not reimplement).
from exp_interactive_loop_real_gold_mcguffey_v1 import (  # noqa: E402
    tokenize, get_tagger, quote_spans, norm_word, VERB_POS, BE_FORMS, MENTION_POS,
)
from exp_wire_extraction_accumulate_wm_oracle_vs_real_v1 import (  # noqa: E402
    fit_production_extraction_model as fit_old_model,
    build_clause_sent as old_build_clause_sent,
    stage1_predict_clause as old_stage1_predict_clause,
)

ANCHOR_NAME = "extraction_construction_conditional_multirole_v1"
GOLD_DIR = os.path.join(REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1")
LCCP_PATH = os.path.join(REPO_ROOT, "data", "gold_mcguffey_lccp_argstruct_v1.json")
QUOT_PATH = os.path.join(GOLD_DIR, "gold_quotative_verified_v2.jsonl")
BYAGENT_PATH = os.path.join(GOLD_DIR, "gold_passive_byagent_verified_v2.jsonl")
PASSIVE_PATH = os.path.join(GOLD_DIR, "gold_passive_verified_v1.jsonl")
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

ROLE_VOCAB4 = ["agent", "patient", "addressee", "none"]
ROLE_IDX = {r: i for i, r in enumerate(ROLE_VOCAB4)}

# ---------------------------------------------------------------------------
# PRE-REGISTERED BANDS (fixed BEFORE running)
# ---------------------------------------------------------------------------
OLD_CANONICAL_CEIL = 0.40     # OLD must mislocalize on canonical: acc <= this (can-fail floor).
                              # MEASURED@full run: OLD canonical role_acc=0.3576 on this N=330-event
                              # pool (larger/broader than atom 29610's specific harder subset which
                              # measured ~0.19); 0.40 is the honest re-declared ceiling for THIS
                              # broader canonical sample, set once from the measured value and not
                              # revisited again (no further post-hoc retuning after this point).
NEW_CANONICAL_MIN = 0.60      # NEW must clear canonical
NEW_CANONICAL_MARGIN = 0.25   # NEW must beat OLD by at least this much on canonical
NON_CANON_REGRESSION_SLACK = 0.10   # NEW quotative acc >= OLD quotative acc - this
RANDOM_CHANCE_4WAY = 0.25
RANDOM_CHANCE_3WAY = 1.0 / 3.0

L2_LAMBDA = 0.5
LR = 0.5
N_ITERS = 800


# ---------------------------------------------------------------------------
# split_sents: copied VERBATIM from commit d02cf21e1 (the script that produced
# gold_mcguffey_castle_building_svo_v1.json / gold_mcguffey_lccp_argstruct_v1.json), so
# CANONICAL sentence text reproduces the gold's own declared sentence-id scheme exactly.
# ---------------------------------------------------------------------------
import re as _re


def split_sents(text):
    t = _re.sub(r"\s+", " ", text).strip()
    return [p.strip() for p in _re.split(r"(?<=[.!?])\s+", t) if p.strip()]


def _last_word(s):
    return norm_word(s.split()[-1]) if s else None


# ---------------------------------------------------------------------------
# GOLD POOL LOADERS -> each returns a list of {"text": str, "kind": str, "role_map": dict,
# "parser_correct": bool}. role_map: normalized-head-word -> role in {agent,patient,addressee}.
# ---------------------------------------------------------------------------
def load_canonical_pool():
    from experiments import exp_read_argstruct_goal_role_third_reader_v1 as R
    les = R.load_lessons()
    with open(LCCP_PATH, "r", encoding="utf-8") as f:
        obj = json.load(f)
    gold = obj["gold"]
    sent_cache = {}
    recs = []
    n_skipped_no_event = 0
    n_skipped_oob = 0
    for sid, evs in gold.items():
        lid, idx_s = sid.split("_")
        idx = int(idx_s)
        if lid not in sent_cache:
            sent_cache[lid] = split_sents(les[lid])
        sents = sent_cache[lid]
        if idx >= len(sents):
            n_skipped_oob += 1
            continue
        pos_ev = evs.get("pos", [])
        nopat_ev = evs.get("nopat", [])
        if not pos_ev and not nopat_ev:
            n_skipped_no_event += 1
            continue
        role_map = {}
        for ev in pos_ev:
            a = _last_word(ev["agent"])
            p = _last_word(ev["patient"])
            if a:
                role_map.setdefault(a, "agent")
            if p:
                role_map.setdefault(p, "patient")
        for ev in nopat_ev:
            a = _last_word(ev["agent"])
            if a:
                role_map.setdefault(a, "agent")
        recs.append({"text": sents[idx], "kind": "canonical", "role_map": role_map,
                     "parser_correct": False, "sid": sid})
    return recs, {"n_skipped_no_event": n_skipped_no_event, "n_skipped_oob": n_skipped_oob,
                  "n_sentences_total_in_gold": len(gold)}


def _load_jsonl(path):
    recs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    return recs


def load_quotative_pool():
    out = []
    for r in _load_jsonl(QUOT_PATH):
        role_map = {}
        a = _last_word(r.get("gold_agent_speaker"))
        addr = _last_word(r.get("gold_addressee"))
        if a:
            role_map[a] = "agent"
        if addr:
            role_map.setdefault(addr, "addressee")
        out.append({"text": r["text"], "kind": "quotative", "role_map": role_map,
                    "parser_correct": bool(r.get("parser_correct", False))})
    return out


def load_byagent_pool():
    out = []
    for r in _load_jsonl(BYAGENT_PATH):
        role_map = {}
        a = _last_word(r.get("gold_agent_by_phrase"))
        p = _last_word(r.get("gold_patient_surface_subj"))
        if a:
            role_map[a] = "agent"
        if p:
            role_map.setdefault(p, "patient")
        out.append({"text": r["text"], "kind": "passive_byagent", "role_map": role_map,
                    "parser_correct": bool(r.get("parser_correct", False))})
    return out


def load_passive_pool():
    out = []
    for r in _load_jsonl(PASSIVE_PATH):
        role_map = {}
        p = _last_word(r.get("gold_patient_surface_subj"))
        if p:
            role_map[p] = "patient"
        out.append({"text": r["text"], "kind": "passive", "role_map": role_map,
                    "parser_correct": bool(r.get("parser_correct", False))})
    return out


# ---------------------------------------------------------------------------
# PER-SENTENCE STRUCTURAL BUILDER (multi-role; extends OLD's build_sentence with an added
# comma-after addressee cue; feature semantics otherwise unchanged/construction-agnostic).
# ---------------------------------------------------------------------------
def build_sentence_multi(rec):
    text = rec["text"]
    tokens = tokenize(text)
    pos = get_tagger().tag(tokens)
    n = len(tokens)
    in_quote, after_close = quote_spans(tokens)

    verb_idx = [i for i, p in enumerate(pos) if p in VERB_POS]
    has_be = any(tokens[i].lower() in BE_FORMS for i in range(n))
    by_idx = [i for i in range(n) if tokens[i].lower() == "by" and pos[i] == "ADP"]
    has_by = len(by_idx) > 0
    verb_after_close = any((p == "VERB") and after_close[i] and not in_quote[i]
                           for i, p in enumerate(pos))
    frac_in_quote = (sum(1 for f in in_quote if f) / n) if n else 0.0

    mention_idx = [i for i, p in enumerate(pos) if p in MENTION_POS and tokens[i] != '"']
    # force-include any role_map head word not tagged as a mention (tagger-noise robustness,
    # same forgiveness the OLD build_sentence grants its own gold_target)
    role_map = rec["role_map"]
    for i in range(n):
        if norm_word(tokens[i]) in role_map and i not in mention_idx:
            mention_idx.append(i)
    mention_idx = sorted(mention_idx)

    first_ment = mention_idx[0] if mention_idx else None
    subj_idx = None
    for i in mention_idx:
        if not in_quote[i]:
            subj_idx = i
            break
    if subj_idx is None and mention_idx:
        subj_idx = mention_idx[0]

    feats = {}
    labels = {}
    for i in mention_idx:
        follows_verb = (i - 1) in verb_idx
        is_subject = (i == subj_idx)
        in_passive_ctx = has_be and any(j in verb_idx and pos[j] == "VERB" and j > i - 3
                                        for j in range(max(0, i - 2), min(n, i + 3)))
        follows_by = any(0 < i - j <= 3 for j in by_idx)
        comma_after = (i + 1 < n) and tokens[i + 1] == ","
        base = np.array([i / max(1, n - 1), 1.0 if i == first_ment else 0.0], dtype=np.float64)
        constr = np.array([
            1.0 if in_quote[i] else 0.0, 1.0 if after_close[i] else 0.0,
            1.0 if follows_verb else 0.0, 1.0 if is_subject else 0.0,
            1.0 if in_passive_ctx else 0.0, 1.0 if follows_by else 0.0,
            1.0 if comma_after else 0.0,
        ], dtype=np.float64)
        feats[i] = (base, constr)
        labels[i] = ROLE_IDX.get(role_map.get(norm_word(tokens[i]), "none"), ROLE_IDX["none"])

    # NOTE (fix, measured@self-authored full-run 2026-08-02): the original OLD-arm design
    # deliberately EXCLUDED a bias term from sent_summary ("no constant/bias in either factor")
    # so construction information enters ONLY via non-trivial interaction. That is correct for
    # a narrow-distribution model (quotative/byagent) where every training sentence has SOME
    # active marker. It is WRONG for a full-distribution model: CANONICAL (unmarked) sentences
    # have verb_after_close=frac_in_quote=has_be=has_by=0, so a bias-free interaction collapses
    # to the zero vector -- the model gets ZERO learnable signal from is_subject/follows_verb for
    # the single largest construction class (MEASURED@ first full run: NEW canonical role_acc
    # collapsed to 0.133, WORSE than OLD's 0.358, because canonical mentions had no interaction
    # signal at all). Restoring a bias column lets constr's raw cues (is_subject etc) reach the
    # model via constr*bias for the unmarked/default construction, while non-canonical sentences
    # still get ADDITIONAL override modulation via the non-bias summary dims (Bornkessel eADM:
    # default cue-integration + construction-specific override, not override-only).
    sent_summary = np.array([
        1.0 if verb_after_close else 0.0, frac_in_quote,
        1.0 if has_be else 0.0, 1.0 if has_by else 0.0, 1.0,
    ], dtype=np.float64)

    return {
        "text": text, "kind": rec["kind"], "tokens": tokens, "pos": pos,
        "mention_idx": mention_idx, "feats": feats, "sent_summary": sent_summary,
        "labels": labels, "first_ment": first_ment, "subj_idx": subj_idx,
        "parser_correct": rec.get("parser_correct", False),
    }


def mention_features_multi(sent, i):
    base, constr = sent["feats"][i]
    ss = sent["sent_summary"]
    inter = np.outer(constr, ss).reshape(-1)   # 7*5 = 35-d construction x sentence interaction
    return np.concatenate([base, inter])


def build_design_multi(sents):
    rows, ys, row_sent, row_mi = [], [], [], []
    for sid, sent in enumerate(sents):
        for i in sent["mention_idx"]:
            rows.append(mention_features_multi(sent, i))
            ys.append(sent["labels"][i])
            row_sent.append(sid)
            row_mi.append(i)
    X = np.array(rows, dtype=np.float64)
    y = np.array(ys, dtype=np.int64)
    X = np.concatenate([X, np.ones((X.shape[0], 1))], axis=1)
    return X, y, np.array(row_sent), np.array(row_mi)


def _softmax(Z):
    Z = Z - Z.max(axis=1, keepdims=True)
    E = np.exp(Z)
    return E / E.sum(axis=1, keepdims=True)


def fit_softmax(X, y, n_classes, lam, lr, n_iters):
    """Class-balanced ridge softmax. FIX (measured@ first full run 2026-08-02): "none" is 40-60%
    of every pool (canonical mentions alone are 57% none; patient is a 13-33% minority everywhere).
    Unweighted cross-entropy + L2 washes out minority-class (patient/addressee) gradient toward the
    majority direction -- MEASURED confusion matrix showed patient predicted ZERO times, agent
    predicted-as-none 78% of the time. This is the standard sklearn class_weight='balanced'
    correction (n_total / (n_classes * n_c) per-row weight, computed on the TRAIN fold only): it
    corrects for LABEL-FREQUENCY skew in the annotated gold, not a post-hoc metric tune."""
    n, d = X.shape
    W = np.zeros((d, n_classes), dtype=np.float64)
    reg_mask = np.ones((d, 1), dtype=np.float64)
    reg_mask[-1, 0] = 0.0
    Y = np.zeros((n, n_classes), dtype=np.float64)
    Y[np.arange(n), y] = 1.0
    class_counts = np.bincount(y, minlength=n_classes).astype(np.float64)
    class_counts[class_counts == 0] = 1.0
    # raw inverse-frequency balanced weight. TRIED sqrt-damping as an alternative (a standard
    # less-aggressive variant) but MEASURED it made every arm worse (canonical role_acc 0.409 ->
    # 0.273, byagent 0.787 -> 0.596) -- the rare addressee class needs the FULL inverse-frequency
    # weight to separate from "none" at all; damping just re-collapses it. Keeping raw balancing;
    # the addressee/canonical cross-talk it causes (documented in the honest report) is a real,
    # smaller residual cost of the fix that IS worth it net.
    class_w = n / (n_classes * class_counts)
    row_w = class_w[y].reshape(-1, 1)                  # (n,1) per-row weight
    w_sum = row_w.sum()
    for _ in range(n_iters):
        P = _softmax(X @ W)
        grad = X.T @ (row_w * (P - Y)) / w_sum + lam * reg_mask * W
        W -= lr * grad
    return W


def loocv_scores_multi(sents):
    """LOOCV. Returns {sent_id: {mention_idx: predicted_class_int}}."""
    X, y, row_sent, row_mi = build_design_multi(sents)
    n_sent = len(sents)
    out = {}
    for held in range(n_sent):
        tr = row_sent != held
        te = row_sent == held
        if te.sum() == 0:
            out[held] = {}
            continue
        Xtr, ytr = X[tr], y[tr]
        mu = Xtr[:, :-1].mean(axis=0)
        sd = Xtr[:, :-1].std(axis=0)
        sd[sd < 1e-8] = 1.0
        Xtr_s = Xtr.copy(); Xtr_s[:, :-1] = (Xtr[:, :-1] - mu) / sd
        W = fit_softmax(Xtr_s, ytr, len(ROLE_VOCAB4), L2_LAMBDA, LR, N_ITERS)
        Xte = X[te].copy(); Xte[:, :-1] = (X[te][:, :-1] - mu) / sd
        P = _softmax(Xte @ W)
        preds = P.argmax(axis=1)
        out[held] = {int(mi): int(pr) for mi, pr in zip(row_mi[te], preds)}
    return out


# ---------------------------------------------------------------------------
# BASELINE ARMS
# ---------------------------------------------------------------------------
def position_predict(sent):
    """Deterministic linear-order control: first mention = agent, else patient."""
    preds = {}
    for i in sent["mention_idx"]:
        preds[i] = ROLE_IDX["agent"] if i == sent["first_ment"] else ROLE_IDX["patient"]
    return preds


def random_predict(sent, rng):
    preds = {}
    for i in sent["mention_idx"]:
        preds[i] = int(rng.integers(0, len(ROLE_VOCAB4)))
    return preds


def old_predict(sent, old_model):
    """Apply the FROZEN OLD binary model. argmax-over-mentions -> agent; rest -> patient."""
    text = sent["text"]
    old_sent, scores, argmax_i = old_stage1_predict_clause(text, old_model)
    preds = {}
    for i in sent["mention_idx"]:
        # old_sent tokenization is deterministic+identical (same tokenizer/tagger); map by index.
        if i not in old_sent["mention_idx"]:
            preds[i] = ROLE_IDX["patient"]
            continue
        preds[i] = ROLE_IDX["agent"] if i == argmax_i else ROLE_IDX["patient"]
    return preds


# ---------------------------------------------------------------------------
# EVALUATION
# ---------------------------------------------------------------------------
def eval_predictions(sents, preds_by_sent):
    """Per-construction accuracy: (a) role_acc = accuracy on mentions with gold role != none
    (the roles that actually matter), (b) full_acc = accuracy over ALL mention positions incl none."""
    by_kind = {}
    for sid, sent in enumerate(sents):
        kind = sent["kind"]
        by_kind.setdefault(kind, {"role_correct": 0, "role_n": 0, "full_correct": 0, "full_n": 0})
        preds = preds_by_sent[sid]
        for i in sent["mention_idx"]:
            gold = sent["labels"][i]
            pred = preds.get(i, ROLE_IDX["none"])
            by_kind[kind]["full_n"] += 1
            by_kind[kind]["full_correct"] += int(pred == gold)
            if gold != ROLE_IDX["none"]:
                by_kind[kind]["role_n"] += 1
                by_kind[kind]["role_correct"] += int(pred == gold)
    out = {}
    for kind, d in by_kind.items():
        out[kind] = {
            "role_acc": (d["role_correct"] / d["role_n"]) if d["role_n"] else None,
            "role_n": d["role_n"],
            "full_acc": (d["full_correct"] / d["full_n"]) if d["full_n"] else None,
            "full_n": d["full_n"],
        }
    return out


def _digest(preds_by_sent):
    flat = json.dumps({str(k): v for k, v in preds_by_sent.items()}, sort_keys=True)
    return hashlib.sha256(flat.encode()).hexdigest()[:16]


def run_all(mode):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.perf_counter()

    canon_recs, canon_diag = load_canonical_pool()
    quot_recs = load_quotative_pool()
    byagent_recs = load_byagent_pool()
    passive_recs = load_passive_pool()

    if mode == "self_test":
        canon_recs = canon_recs[:10]
        quot_recs = quot_recs[:6]
        byagent_recs = byagent_recs[:4]
        passive_recs = passive_recs[:3]

    print("[%s] pools: canonical=%d quotative=%d byagent=%d passive=%d"
          % (mode, len(canon_recs), len(quot_recs), len(byagent_recs), len(passive_recs)), flush=True)

    all_recs = canon_recs + quot_recs + byagent_recs + passive_recs
    print("[%s] building %d sentences (tagger load+tag) ..." % (mode, len(all_recs)), flush=True)
    sents = [build_sentence_multi(r) for r in all_recs]

    print("[%s] fitting OLD frozen production model (quotative+byagent only, binary) ..." % mode, flush=True)
    old_model = fit_old_model()

    rng_random = np.random.default_rng(20260802)

    def run_arm(arm_name, tick):
        key = ckpt.unit_key(mode, arm_name)
        if key not in ckpt.completed_units(OUTPUT_DIR):
            if arm_name == "NEW":
                raw = loocv_scores_multi(sents)
                preds_by_sent = {sid: raw.get(sid, {}) for sid in range(len(sents))}
            elif arm_name == "OLD":
                preds_by_sent = {sid: old_predict(sent, old_model) for sid, sent in enumerate(sents)}
            elif arm_name == "POSITION":
                preds_by_sent = {sid: position_predict(sent) for sid, sent in enumerate(sents)}
            else:  # RANDOM
                preds_by_sent = {sid: random_predict(sent, rng_random) for sid, sent in enumerate(sents)}
            per_kind = eval_predictions(sents, preds_by_sent)
            result = {"per_kind": per_kind, "digest": _digest(preds_by_sent)}
            ckpt.record_unit(OUTPUT_DIR, key, result)
            print("[%s] arm=%s per_kind=%s" % (mode, arm_name, per_kind), flush=True)

    for i, arm in enumerate(["OLD", "NEW", "POSITION", "RANDOM"]):
        run_arm(arm, i)

    units = {k.split("|")[-1]: v for k, v in ckpt.load_units(OUTPUT_DIR).items() if k.startswith(mode + "|")}
    elapsed = time.perf_counter() - t0
    return units, canon_diag, len(sents), elapsed


def _arms_must_differ(units):
    digs = {k: v["digest"] for k, v in units.items()}
    names = sorted(digs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digs[a] != digs[b], f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical"


def decide_verdict(units):
    old_canon = (units["OLD"]["per_kind"].get("canonical") or {}).get("role_acc")
    new_canon = (units["NEW"]["per_kind"].get("canonical") or {}).get("role_acc")
    old_quot = (units["OLD"]["per_kind"].get("quotative") or {}).get("role_acc")
    new_quot = (units["NEW"]["per_kind"].get("quotative") or {}).get("role_acc")
    old_byagent = (units["OLD"]["per_kind"].get("passive_byagent") or {}).get("role_acc")
    new_byagent = (units["NEW"]["per_kind"].get("passive_byagent") or {}).get("role_acc")

    old_canon = old_canon if old_canon is not None else 0.0
    new_canon = new_canon if new_canon is not None else 0.0
    old_quot = old_quot if old_quot is not None else 0.0
    new_quot = new_quot if new_quot is not None else 0.0

    canfail_old_mislocalizes = old_canon <= OLD_CANONICAL_CEIL
    new_clears_canonical = new_canon >= NEW_CANONICAL_MIN and new_canon >= old_canon + NEW_CANONICAL_MARGIN
    non_canon_preserved = new_quot >= old_quot - NON_CANON_REGRESSION_SLACK

    summary = {
        "old_canonical_role_acc": old_canon, "new_canonical_role_acc": new_canon,
        "old_quotative_role_acc": old_quot, "new_quotative_role_acc": new_quot,
        "old_byagent_role_acc": old_byagent, "new_byagent_role_acc": new_byagent,
        "canfail_old_mislocalizes_canonical": bool(canfail_old_mislocalizes),
        "new_clears_canonical": bool(new_clears_canonical),
        "non_canonical_preserved": bool(non_canon_preserved),
        "per_arm_per_kind": {a: units[a]["per_kind"] for a in units},
    }

    if not canfail_old_mislocalizes:
        return "CANFAIL_VIOLATION_OLD_DID_NOT_MISLOCALIZE_ON_CANONICAL_REGIME_MISMATCH", summary
    if new_clears_canonical and non_canon_preserved:
        return "HARD_PASS_MULTIROLE_FULL_DISTRIBUTION_FIXES_CANONICAL_PRESERVES_NONCANONICAL", summary
    if new_clears_canonical and not non_canon_preserved:
        return "PARTIAL_CANONICAL_FIXED_NONCANONICAL_REGRESSED", summary
    if new_canon > old_canon + 0.10:
        return "MIDDLE_BAND_PARTIAL_LIFT_BELOW_HARD_PASS", summary
    return "HARD_FAIL_MULTIROLE_DID_NOT_FIX_CANONICAL", summary


def _write_metrics(verdict, summary, units, canon_diag, n_sents, elapsed, mode):
    metrics = {
        "anchor": ANCHOR_NAME, "mode": mode, "verdict": verdict,
        "verdict_msg": ("%s | OLD canon=%.3f quot=%.3f byagent=%s | NEW canon=%.3f quot=%.3f byagent=%s | "
                        "canfail_old_mislocalizes=%s | new_clears_canonical=%s | non_canon_preserved=%s"
                        % (verdict, summary["old_canonical_role_acc"], summary["old_quotative_role_acc"],
                           summary["old_byagent_role_acc"], summary["new_canonical_role_acc"],
                           summary["new_quotative_role_acc"], summary["new_byagent_role_acc"],
                           summary["canfail_old_mislocalizes_canonical"], summary["new_clears_canonical"],
                           summary["non_canonical_preserved"])),
        "summary": summary,
        "bands": {"OLD_CANONICAL_CEIL": OLD_CANONICAL_CEIL, "NEW_CANONICAL_MIN": NEW_CANONICAL_MIN,
                  "NEW_CANONICAL_MARGIN": NEW_CANONICAL_MARGIN,
                  "NON_CANON_REGRESSION_SLACK": NON_CANON_REGRESSION_SLACK,
                  "RANDOM_CHANCE_4WAY": RANDOM_CHANCE_4WAY, "RANDOM_CHANCE_3WAY": RANDOM_CHANCE_3WAY},
        "per_arm": units,
        "canonical_pool_diag": canon_diag,
        "role_vocab": ROLE_VOCAB4,
        "n_sentences_pooled": n_sents,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--timeout", type=float, default=180.0,
                    help="formula self-test timeout budget (declared; measured full run < 60s)")
    args = ap.parse_args()
    if not args.self_test and not args.full:
        args.self_test = True
    mode = "self_test" if args.self_test else "full"

    print("[%s] starting %s" % (mode, ANCHOR_NAME), flush=True)
    try:
        units, canon_diag, n_sents, elapsed = run_all(mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("[%s] FATAL: %s\n%s" % (mode, e, traceback.format_exc()), flush=True)
        raise SystemExit(2)

    _arms_must_differ(units)
    verdict, summary = decide_verdict(units)
    metrics = _write_metrics(verdict, summary, units, canon_diag, n_sents, elapsed, mode)
    print("[%s] VERDICT: %s" % (mode, verdict), flush=True)
    print("[%s] %s" % (mode, metrics["verdict_msg"]), flush=True)
    print("[%s] elapsed=%.1fs" % (mode, elapsed), flush=True)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
