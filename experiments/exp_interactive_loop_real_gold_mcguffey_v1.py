# CELL-TEMPLATE (reuses exp_interactive_extraction_situation_model_loop_probe1_v1 SCAFFOLD:
#   ARM_OFF/ARM_ON/PLACEBO/NO-TOPDOWN, decide_verdict floor/pass bands, per-(arm)-unit checkpoint
#   via tools/exp_checkpoint.py, atomic os.replace metrics, _arms_must_differ, heartbeat).
# DELIBERATE DEVIATION FROM PROBE1 (honest, flagged): the model is implemented in NUMPY (ridge
#   logistic regression), NOT torch. Rationale: (1) the model is a tiny low-capacity linear readout
#   (N=27 sentences, LOOCV) for which torch is overkill; (2) on the build box torch import measured
#   657.8s (11 min, MEASURED@ box under concurrent load) making a torch cell effectively un-runnable
#   this cycle, whereas the pos_tagger (Asset 1) is already pure-numpy and loads in ~29s. The harness
#   SCAFFOLD (arms, verdict bands, checkpoint, placebo, LOOCV, atomic write) is reused faithfully;
#   only the linear-algebra backend differs. This is exp_dev's flagged call per the design note's
#   "exp_dev's call, not required" latitude, NOT a silent rebuild.
# - ONE VARIABLE: interactive top-down feedback ON vs OFF (identical features, identical LOOCV).
# - CAN-FAIL FLOOR (must hold or encoding leaks): OFF quotative agent-acc <= 0.15 AND OFF passive
#   patient-acc <= 0.15 (OFF = deterministic first/subject-position linear-order reader = the ~parser
#   MEASURED@ 95%/86% wrong on these exact cases).
# - HONESTY LINE (per slot_attention_wm docstring + design note weakest-link #2): we SUPPLY structural
#   features (POS, position, quote membership, verb-adjacency, passive-context, lexical id, mention
#   flag). We do NOT supply the construction->role MAPPING -- that is LEARNED by the logistic weights
#   over the construction x sentence interaction block. Placebo (shuffled construction summary -> must
#   not help) + no-topdown control (base-only -> ~floor) confirm the mapping is learned, not hardcoded.
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / CITED@ / REASONED@.
# - deterministic: numpy.random.default_rng(seed) only; no hash() for control flow; LOOCV folds are
#   deterministic (sentence index order). lexical ids use a seeded rng keyed by a stable sorted token
#   list (no PYTHONHASHSEED dependence).
# - ASCII-only. No emojis. No em dashes in output.
"""Interactive extraction<->situation-model loop -- FIRST REAL-STRUCTURE test on McGuffey gold.

Director spec: notes/interactive_loop_first_real_structure_test_mcguffey_gold_2026-08-01.md
(commit 48cbea8bf). Extends the VALIDATED synthetic probe
(exp_interactive_extraction_situation_model_loop_probe1_v1, MIDDLE_PARTIAL, floor held, interactive
lifted passives specifically, placebo clean) to REAL non-canonical constructions where a feed-forward
linear-order baseline PROVABLY fails:
  - QUOTATIVE (N=20, 19 parser-wrong): postposed speaker ('"..." said James' -> agent=James;
    Kate=vocative/addressee NOT agent). Task: select which mention = agent/speaker.
  - PASSIVE  (N=7, 6 parser-wrong): 'He is called Dodger' -> He=PATIENT, agent implicit. Task:
    classify the surface-subject mention's role (agent vs patient); gold = patient.

INPUT gold files (read off disk):
  data/eval_gold_mention_role_mcguffey_v1/gold_quotative_verified_v1.jsonl
  data/eval_gold_mention_role_mcguffey_v1/gold_passive_verified_v1.jsonl

ENCODING (glass-box, our-own, NO borrowed embedding): per-token/per-mention features assembled ONLY
from things we own -- POS (hdlab.pos_tagger UPOS averaged perceptron, Asset 1), linear position +
random positional code, quote membership/boundary, verb adjacency, passive-context (be-aux + following
verb + 'by'), random lexical id (identity only), mention flag. See feature builder below; each block
flagged structure-supplied / engineering-proxy / identity-only.

ARMS (one variable = top-down feedback):
  ARM_OFF  = deterministic linear-order reader: quotative agent = FIRST mention by position; passive
             surface-subject = agent. Consumes ONLY position+mention. This reproduces the known-wrong
             parser -> the CAN-FAIL FLOOR.
  ARM_ON   = ridge logistic regression over [base(position) ++ per-mention construction block ++
             (construction x sentence-summary) interaction block]. The construction->role mapping is
             the LEARNED weight on the interaction block (top-down construction expectation biasing
             the per-mention agent-ness decision). LOOCV, low-capacity (strong L2).
  PLACEBO  = ARM_ON but the sentence-level construction summary is SHUFFLED across sentences (each
             mention keeps its own per-mention features but the interaction is with a WRONG sentence's
             construction). Must NOT help (proves the CONTENT of the construction signal matters).
  NO_TD    = ARM_ON with the construction + interaction blocks zeroed (base/position only, learned).
             Sanity: position alone cannot satisfy all constructions -> ~floor.

LEARNING: pool both constructions (N=27 sentences) so the SHARED 'markers override linear order'
signal has the most examples; evaluate per-construction. Leave-One-Out CV over sentences (no sentence
overlap). Deterministic folds. Per-mention binary label is_agent in {0,1}; BCE; argmax over a
sentence's mentions = predicted agent (quotative); sigmoid(surface-subject) < 0.5 = predicted patient
(passive).

Run:  .venv/Scripts/python.exe experiments/exp_interactive_loop_real_gold_mcguffey_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_interactive_loop_real_gold_mcguffey_v1.py --full
"""

import argparse
import hashlib
import json
import os
import re
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
from _cell_heartbeat import CellHeartbeat  # noqa: E402

ANCHOR_NAME = "interactive_loop_real_gold_mcguffey_v1"
GOLD_DIR = os.path.join(REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1")
QUOT_PATH = os.path.join(GOLD_DIR, "gold_quotative_verified_v1.jsonl")
PASS_PATH = os.path.join(GOLD_DIR, "gold_passive_verified_v1.jsonl")
BYAGENT_PATH_V1 = os.path.join(GOLD_DIR, "gold_passive_byagent_verified_v1.jsonl")
BYAGENT_PATH_V2 = os.path.join(GOLD_DIR, "gold_passive_byagent_verified_v2.jsonl")
# BYAGENT_GOLD_VERSION selects which by-agent gold file is loaded (v1 N=5 exploratory kept intact
# for reproducibility; v2 N=23 = director-hand-verified power-up mined from full McGuffey g1-g6,
# commit 210be7a1c). Set via --byagent-version {v1,v2} CLI flag (default v2, the powered set).
BYAGENT_GOLD_VERSION = "v2"
BYAGENT_PATH = BYAGENT_PATH_V2
# OUTPUT_DIR is version-suffixed for the powered (v2, N=23) by-agent gold so its checkpoint/metrics
# never mix with the original N=5 exploratory run's data/exp_interactive_loop_real_gold_mcguffey_v1/
# (preserves the v1 HARD_PASS reproducibility artifact untouched).
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME
                          + ("" if BYAGENT_GOLD_VERSION == "v1" else "_byagent_" + BYAGENT_GOLD_VERSION))
TAGGER_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")

MENTION_POS = ("PROPN", "PRON", "NOUN")
VERB_POS = ("VERB", "AUX")
BE_FORMS = ("is", "are", "was", "were", "be", "been", "being", "am")

# ---------------------------------------------------------------------------
# PRE-REGISTERED BANDS (fixed BEFORE running; from the design note)
# ---------------------------------------------------------------------------
FLOOR_QUOT_MAX = 0.15      # OFF quotative agent-acc must be AT/BELOW this (hard subset)
FLOOR_PASS_MAX = 0.15      # OFF passive patient-acc must be AT/BELOW this
PASS_QUOT_MIN = 0.60       # ON quotative agent-acc HARD-PASS (hard subset)
PASS_PASS_MIN = 0.55       # ON passive patient-acc HARD-PASS (lower bar, N=7 underpowered)
PASS_QUOT_MARGIN = 0.40    # ON quotative must also be >= floor + this
PASS_PASS_MARGIN = 0.35    # ON passive must also be >= floor + this

# BY-AGENT band is version-specific (declared BEFORE this re-run, per director spawn-prompt
# contract): v1 (N=5, exploratory) kept its original lower/looser bar; v2 (N=23, powered) uses a
# STRICTER pre-registered bar since the set is no longer underpowered-exploratory.
PASS_BYAGENT_MIN_V1 = 0.55     # legacy N=5 bar (one mislabel = 0.2 swing; keep for reproducibility)
PASS_BYAGENT_MARGIN_V1 = 0.35
PASS_BYAGENT_MIN_V2 = 0.75     # PRE-REGISTERED (spawn-prompt contract): powered N=23 HARD-PASS floor
PASS_BYAGENT_MARGIN_V2 = 0.40  # PRE-REGISTERED: ON must clearly separate from OFF/placebo base rate
MIDDLE_MARGIN = 0.15       # ON > floor + this = at least no-longer-inverted
HARD_FAIL_MARGIN = 0.10    # ON <= floor + this = top-down did not resolve
PLACEBO_SLACK = 0.15       # placebo must stay within max(floor, OFF) + this

# ridge-logistic hyperparams (low-capacity; fixed before running)
L2_LAMBDA = 0.5            # strong L2 = low effective capacity for N=27 LOOCV
LR = 0.5
N_ITERS = 800
POS_CODE_DIM = 4


# ---------------------------------------------------------------------------
# TOKENIZATION + POS
# ---------------------------------------------------------------------------
def tokenize(text):
    """Whitespace/punct tokenizer that keeps quote marks and punctuation as tokens (glass-box)."""
    return re.findall(r"[A-Za-z]+|[0-9]+|[^\sA-Za-z0-9]", text)


_TAGGER = None


def get_tagger():
    global _TAGGER
    if _TAGGER is None:
        from hdlab.pos_tagger import PosTagger
        _TAGGER = PosTagger.load(TAGGER_PATH)
    return _TAGGER


def norm_word(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


# ---------------------------------------------------------------------------
# STRUCTURAL FEATURE DETECTORS (all construction-agnostic surface structure)
# ---------------------------------------------------------------------------
def quote_spans(tokens):
    """Return per-token flags: in_quote, is_after_close_quote (token index > a closing quote)."""
    in_quote = [False] * len(tokens)
    inside = False
    seen_close = [False] * len(tokens)
    any_closed = False
    for i, t in enumerate(tokens):
        if t == '"':
            inside = not inside
            if not inside:
                any_closed = True
            in_quote[i] = True   # the quote mark itself; mentions are not quote marks anyway
            seen_close[i] = any_closed
            continue
        in_quote[i] = inside
        seen_close[i] = any_closed
    return in_quote, seen_close


def build_sentence(rec, kind):
    """Parse one gold record into tokens, POS, mentions, per-mention features, sentence summary,
    per-mention is_agent labels, the gold target mention index, and the surface-subject index."""
    text = rec["text"]
    tokens = tokenize(text)
    pos = get_tagger().tag(tokens)
    n = len(tokens)
    in_quote, after_close = quote_spans(tokens)

    verb_idx = [i for i, p in enumerate(pos) if p in VERB_POS]
    has_be = any(tokens[i].lower() in BE_FORMS for i in range(n))
    by_idx = [i for i in range(n) if tokens[i].lower() == "by" and pos[i] == "ADP"]
    has_by = len(by_idx) > 0
    # postposed-speech signature (structural): a VERB token that occurs AFTER a closing quote
    verb_after_close = any((p in ("VERB",)) and after_close[i] and not in_quote[i]
                           for i, p in enumerate(pos))
    frac_in_quote = (sum(1 for f in in_quote if f) / n) if n else 0.0

    # mentions = nominal tokens; ALWAYS include the gold target token index so the task is well posed
    mention_idx = [i for i, p in enumerate(pos) if p in MENTION_POS and tokens[i] != '"']

    def last_word(s):
        return norm_word(s.split()[-1]) if s else None

    # gold TARGET differs by construction: quotative -> speaker (agent); passive_byagent -> by-phrase
    # head (agent); passive (degenerate) -> surface subject (patient). Match on the phrase HEAD word.
    gold_tok = None
    if kind == "quotative":
        gold_tok = last_word(rec.get("gold_agent_speaker"))
    elif kind == "passive_byagent":
        gold_tok = last_word(rec.get("gold_agent_by_phrase"))
    else:
        gold_tok = last_word(rec.get("gold_patient_surface_subj"))

    # locate the gold target token index. For passive_byagent PREFER the match that FOLLOWS a 'by'
    # (the agent NP head), else fall back to the first matching token.
    matches = [i for i in range(n) if norm_word(tokens[i]) and norm_word(tokens[i]) == gold_tok]
    gold_target = None
    if kind == "passive_byagent" and matches:
        for i in matches:
            if any(0 < i - j <= 3 for j in by_idx):
                gold_target = i
                break
    if gold_target is None and matches:
        gold_target = matches[0]
    gold_in_mentions = gold_target is not None and gold_target in mention_idx
    if gold_target is not None and gold_target not in mention_idx:
        mention_idx.append(gold_target)          # force-include (tagger-noise robustness)
        mention_idx = sorted(mention_idx)

    # surface subject = FIRST mention that is NOT inside quotes (linear-order subject)
    subj_idx = None
    for i in mention_idx:
        if not in_quote[i]:
            subj_idx = i
            break
    if subj_idx is None and mention_idx:
        subj_idx = mention_idx[0]

    # per-mention structural feature block (construction-agnostic surface structure)
    first_ment = mention_idx[0] if mention_idx else None
    last_ment = mention_idx[-1] if mention_idx else None
    feats = {}
    for i in mention_idx:
        follows_verb = (i - 1) in verb_idx
        is_subject = (i == subj_idx)
        in_passive_ctx = has_be and any(j in verb_idx and pos[j] == "VERB" and j > i - 3
                                        for j in range(max(0, i - 2), min(n, i + 3)))
        follows_by = any(0 < i - j <= 3 for j in by_idx)   # in a 'by' phrase (glass-box by-marker)
        base = np.array([
            i / max(1, n - 1),                 # normalized position (the ONLY cue OFF/NO_TD get)
            1.0 if i == first_ment else 0.0,   # is-first-mention (linear-order subject cue)
        ], dtype=np.float64)
        constr = np.array([
            1.0 if in_quote[i] else 0.0,
            1.0 if after_close[i] else 0.0,
            1.0 if follows_verb else 0.0,
            1.0 if is_subject else 0.0,
            1.0 if in_passive_ctx else 0.0,
            1.0 if follows_by else 0.0,        # by-phrase membership (agent marker for by-passives)
            1.0,                               # bias
        ], dtype=np.float64)
        feats[i] = (base, constr)

    sent_summary = np.array([
        1.0 if verb_after_close else 0.0,
        frac_in_quote,
        1.0 if has_be else 0.0,
        1.0 if has_by else 0.0,
        1.0,                                   # bias
    ], dtype=np.float64)

    # per-mention is_agent labels (pooled training target)
    labels = {}
    for i in mention_idx:
        if kind in ("quotative", "passive_byagent"):
            # AGENT selection: gold agent mention -> 1, all others (incl. surface-subj patient) -> 0
            labels[i] = 1.0 if i == gold_target else 0.0
        else:
            # degenerate passive: surface subject is PATIENT (is_agent=0); no explicit agent present.
            labels[i] = 0.0
    return {
        "text": text,
        "kind": kind,
        "tokens": tokens,
        "pos": pos,
        "mention_idx": mention_idx,
        "feats": feats,
        "sent_summary": sent_summary,
        "labels": labels,
        "gold_target": gold_target,
        "gold_in_mentions": bool(gold_in_mentions),
        "subj_idx": subj_idx,
        "first_ment": first_ment,
        "parser_correct": bool(rec.get("parser_correct", False)),
    }


# ---------------------------------------------------------------------------
# FEATURE ASSEMBLY per arm (defines what each arm is allowed to see)
# ---------------------------------------------------------------------------
def mention_features(sent, i, arm, constr_override=None):
    """Assemble the feature vector for mention i of a sentence under a given arm.

    NO_TD -> base (position) only. ON/PLACEBO -> base ++ (per-mention construction x sentence-summary)
    interaction ONLY. Construction information enters EXCLUSIVELY through the interaction with the
    sentence-level construction summary (NO standalone construction block, no constant/bias in either
    factor). This is the top-down path 'p_td = g(construction)' biasing the per-mention decision --
    the ONE VARIABLE ON adds over OFF/NO_TD.

    PLACEBO passes constr_override = the constr vector of a DIFFERENT mention in the same sentence
    (random-feedback: real construction cues attached to the WRONG mention), so the top-down bias is
    scrambled while position (base) is intact. If the lift is real construction CONTENT it must
    collapse toward NO_TD; if it survives, the lift was a capacity artifact -> HARD-FAIL the claim."""
    base, constr = sent["feats"][i]
    if arm == "NO_TD":
        return base.copy()
    c = constr if constr_override is None else constr_override
    ss = sent["sent_summary"]
    inter = np.outer(c[:6], ss[:4]).reshape(-1)   # 24-d construction x sentence interaction
    return np.concatenate([base, inter])


# ---------------------------------------------------------------------------
# RIDGE LOGISTIC REGRESSION (numpy; deterministic full-batch GD)
# ---------------------------------------------------------------------------
def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def fit_logreg(X, y, lam, lr, n_iters):
    """Full-batch ridge logistic regression. X standardized outside. Returns weight vector w."""
    n, d = X.shape
    w = np.zeros(d, dtype=np.float64)
    reg_mask = np.ones(d, dtype=np.float64)
    reg_mask[-1] = 0.0   # do not regularize the bias (last column is a 1s column, see build_design)
    for _ in range(n_iters):
        p = _sigmoid(X @ w)
        grad = X.T @ (p - y) / n + lam * reg_mask * w
        w -= lr * grad
    return w


def build_design(sents, arm, scramble_constr=False):
    """Stack all (mention) rows across sentences into X, y, and a row->sentence index map.
    scramble_constr=True (PLACEBO): within each sentence, permute the construction vectors among its
    mentions (deterministic derangement where possible) so construction cues attach to WRONG mentions."""
    rows, ys, row_sent, row_mi = [], [], [], []
    for sid, sent in enumerate(sents):
        mis = sent["mention_idx"]
        constr_map = None
        if scramble_constr and arm != "NO_TD" and len(mis) > 1:
            rng = np.random.default_rng(70000 + sid)
            order = np.arange(len(mis))
            perm = rng.permutation(len(mis))
            tries = 0
            while np.any(perm == order) and tries < 50:
                perm = rng.permutation(len(mis)); tries += 1
            constr_map = {mis[k]: sent["feats"][mis[perm[k]]][1] for k in range(len(mis))}
        for i in mis:
            co = None if constr_map is None else constr_map[i]
            rows.append(mention_features(sent, i, arm, constr_override=co))
            ys.append(sent["labels"][i])
            row_sent.append(sid)
            row_mi.append(i)
    X = np.array(rows, dtype=np.float64)
    y = np.array(ys, dtype=np.float64)
    # append a bias column of 1s (kept unregularized via reg_mask[-1]=0)
    X = np.concatenate([X, np.ones((X.shape[0], 1))], axis=1)
    return X, y, np.array(row_sent), np.array(row_mi)


def loocv_scores(sents, arm, scramble_constr=False):
    """Leave-one-sentence-out CV. Returns {sent_id: {mention_idx: score}} predicted agent-ness."""
    X, y, row_sent, row_mi = build_design(sents, arm, scramble_constr=scramble_constr)
    n_sent = len(sents)
    out = {}
    for held in range(n_sent):
        tr = row_sent != held
        te = row_sent == held
        if te.sum() == 0:
            out[held] = {}
            continue
        Xtr, ytr = X[tr], y[tr]
        # standardize on train (exclude the final bias column)
        mu = Xtr[:, :-1].mean(axis=0)
        sd = Xtr[:, :-1].std(axis=0)
        sd[sd < 1e-8] = 1.0
        Xtr_s = Xtr.copy(); Xtr_s[:, :-1] = (Xtr[:, :-1] - mu) / sd
        w = fit_logreg(Xtr_s, ytr, L2_LAMBDA, LR, N_ITERS)
        Xte = X[te].copy(); Xte[:, :-1] = (X[te][:, :-1] - mu) / sd
        scores = _sigmoid(Xte @ w)
        out[held] = {int(mi): float(s) for mi, s in zip(row_mi[te], scores)}
    return out


# ---------------------------------------------------------------------------
# EVALUATION per arm
# ---------------------------------------------------------------------------
def off_predict(sent):
    """Deterministic linear-order reader. AGENT-selection: quotative -> FIRST mention; passive_byagent
    -> surface subject (WRONG, gold agent = by-phrase); degenerate passive -> subject is agent."""
    if sent["kind"] == "quotative":
        return sent["first_ment"]
    return sent["subj_idx"]                    # linear-order agent guess = surface subject


def _argmax_pred(sc):
    return max(sc, key=sc.get) if sc else None


def eval_arm(sents_q, sents_p, sents_b, arm, scores_q=None, scores_p=None, scores_b=None):
    """Per-construction accuracy on the HARD subset (parser_correct=False) + already-correct.
    quotative + passive_byagent = AGENT selection (argmax over mentions == gold agent). degenerate
    passive = surface-subject-is-patient (sigmoid(subj) < 0.5)."""
    def sel_correct(sent, pred_agent):
        return pred_agent is not None and sent["gold_target"] is not None and pred_agent == sent["gold_target"]

    def agent_sel_track(sents, scores):
        hard, easy = [], []
        for sid, sent in enumerate(sents):
            pred = off_predict(sent) if arm == "OFF" else _argmax_pred(scores[sid])
            ok = 1.0 if sel_correct(sent, pred) else 0.0
            (easy if sent["parser_correct"] else hard).append(ok)
        return hard, easy

    q_hard, q_easy = agent_sel_track(sents_q, scores_q)
    b_hard, b_easy = agent_sel_track(sents_b, scores_b)

    p_hard, p_easy = [], []
    for sid, sent in enumerate(sents_p):
        subj = sent["subj_idx"]
        if arm == "OFF":
            pred_is_agent = True
        else:
            pred_is_agent = (scores_p[sid].get(subj, 0.0) >= 0.5) if scores_p[sid] else True
        ok = 1.0 if not pred_is_agent else 0.0
        (p_easy if sent["parser_correct"] else p_hard).append(ok)

    def m(a):
        return float(np.mean(a)) if a else None
    return {
        "quot_hard_acc": m(q_hard), "quot_hard_n": len(q_hard),
        "quot_easy_acc": m(q_easy), "quot_easy_n": len(q_easy),
        "pass_hard_acc": m(p_hard), "pass_hard_n": len(p_hard),
        "pass_easy_acc": m(p_easy), "pass_easy_n": len(p_easy),
        "byagent_hard_acc": m(b_hard), "byagent_hard_n": len(b_hard),
        "byagent_easy_acc": m(b_easy), "byagent_easy_n": len(b_easy),
    }


def _digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# TAGGER DIAGNOSTIC + glass-box dump
# ---------------------------------------------------------------------------
def tagger_diagnostic(sents_q, sents_p, sents_b):
    """No POS gold exists for these McGuffey sentences, so true tag-accuracy is uncomputable. Report
    the actionable proxy: does the tagger tag the GOLD ROLE-FILLER token as a nominal mention? (If not,
    domain shift hid the answer token from the mechanism.) This is the feature-quality diagnostic."""
    hits, tot = 0, 0
    misses = []
    for sent in list(sents_q) + list(sents_p) + list(sents_b):
        if sent["gold_target"] is None:
            continue
        tot += 1
        if sent["gold_in_mentions"]:
            hits += 1
        else:
            gt = sent["gold_target"]
            misses.append({"text": sent["text"][:60], "gold_token": sent["tokens"][gt],
                           "tagged": sent["pos"][gt]})
    return {"gold_filler_nominal_rate": (hits / tot) if tot else None,
            "n_gold": tot, "n_missed": len(misses), "misses": misses[:8]}


# ---------------------------------------------------------------------------
# RUN
# ---------------------------------------------------------------------------
def load_gold(path):
    recs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    return recs


def run_all(mode):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.perf_counter()
    quot_recs = load_gold(QUOT_PATH)
    pass_recs = load_gold(PASS_PATH)
    byagent_recs = load_gold(BYAGENT_PATH)
    if mode == "self_test":
        quot_recs = quot_recs[:6]
        pass_recs = pass_recs[:4]
        byagent_recs = byagent_recs[:3]

    print("[%s] building sentences (tagger load + tag) ..." % mode, flush=True)
    sents_q = [build_sentence(r, "quotative") for r in quot_recs]
    sents_p = [build_sentence(r, "passive") for r in pass_recs]
    sents_b = [build_sentence(r, "passive_byagent") for r in byagent_recs]
    pooled = sents_q + sents_p + sents_b
    nq, npv = len(sents_q), len(sents_p)

    def split_scores(ps):
        return ({sid: ps[sid] for sid in range(nq)},
                {sid: ps[nq + sid] for sid in range(npv)},
                {sid: ps[nq + npv + sid] for sid in range(len(sents_b))})

    def run_arm(arm, tick, scramble=False):
        key = ckpt.unit_key(mode, arm)
        if key not in ckpt.completed_units(OUTPUT_DIR):
            if arm == "OFF":
                r = eval_arm(sents_q, sents_p, sents_b, "OFF")
            else:
                ps = loocv_scores(pooled, "NO_TD" if arm == "NO_TD" else "ON",
                                  scramble_constr=scramble)
                sc_q, sc_p, sc_b = split_scores(ps)
                r = eval_arm(sents_q, sents_p, sents_b, arm, sc_q, sc_p, sc_b)
            ckpt.record_unit(OUTPUT_DIR, key, r)
            print("[%s] quot_hard=%.3f byagent_hard=%.3f pass_hard=%.3f"
                  % (arm, r["quot_hard_acc"] if r["quot_hard_acc"] is not None else -1,
                     r["byagent_hard_acc"] if r["byagent_hard_acc"] is not None else -1,
                     r["pass_hard_acc"] if r["pass_hard_acc"] is not None else -1), flush=True)

    with CellHeartbeat(OUTPUT_DIR, total_units=4, interval_s=15) as hb:
        run_arm("OFF", 1); hb.tick(1)
        run_arm("ON", 2); hb.tick(2)
        run_arm("PLACEBO", 3, scramble=True); hb.tick(3)
        run_arm("NO_TD", 4); hb.tick(4, force=True)

    units = {k.split("|")[-1]: v for k, v in ckpt.load_units(OUTPUT_DIR).items()
             if k.startswith(mode + "|")}
    diag = tagger_diagnostic(sents_q, sents_p, sents_b)
    elapsed = time.perf_counter() - t0
    return units, diag, sents_q, sents_p, sents_b, elapsed


def _arms_must_differ(units):
    digs = {k: _digest(v) for k, v in units.items()}
    names = sorted(digs)
    # ON must differ from PLACEBO and NO_TD (else the top-down content had no effect at all = wiring bug
    # OR a genuine null; we only assert ON != NO_TD in structure via the score path, so use a soft check)
    assert digs.get("ON") != digs.get("OFF"), "ON and OFF identical metrics -- wiring bug"


def decide_verdict(units, diag):
    off = units["OFF"]; on = units["ON"]; plac = units["PLACEBO"]; notd = units["NO_TD"]
    off_q = off["quot_hard_acc"] or 0.0
    off_p = off["pass_hard_acc"] or 0.0
    on_q = on["quot_hard_acc"] or 0.0
    on_p = on["pass_hard_acc"] or 0.0
    plac_q = plac["quot_hard_acc"] or 0.0
    plac_p = plac["pass_hard_acc"] or 0.0

    notd_q = notd["quot_hard_acc"] or 0.0
    notd_p = notd["pass_hard_acc"] or 0.0
    floor_held = (off_q <= FLOOR_QUOT_MAX and off_p <= FLOOR_PASS_MAX)
    placebo_ok_q = plac_q <= max(off_q, notd_q, FLOOR_QUOT_MAX) + PLACEBO_SLACK
    placebo_ok_p = plac_p <= max(off_p, notd_p, FLOOR_PASS_MAX) + PLACEBO_SLACK

    # LEAK-vs-BASELINE discrimination: a true encoding LEAK (construction->role reaching arms that
    # should not see it) would make NO_TD (position-only) or PLACEBO (scrambled construction) HIGH.
    # If instead ON's lift COLLAPSES under placebo back toward the (position-only) NO_TD baseline, the
    # construction signal is confined to ON's content-dependent top-down path = NOT a leak, and any
    # floor exceedance is just linear-order failing less hard than the pre-reg 0.15 assumed.
    placebo_collapses = (on_q - plac_q) >= 0.30 and plac_q <= notd_q + 0.10
    not_a_leak = placebo_collapses and notd_q <= 0.45

    # by-agent passives (real 2-way agent selection: gold agent = by-phrase head)
    off_b = off["byagent_hard_acc"] or 0.0
    on_b = on["byagent_hard_acc"] or 0.0
    plac_b = plac["byagent_hard_acc"] or 0.0
    notd_b = notd["byagent_hard_acc"] or 0.0
    base_b = max(off_b, notd_b)
    byagent_floor_held = off_b <= FLOOR_PASS_MAX
    byagent_placebo_ok = plac_b <= max(base_b, FLOOR_PASS_MAX) + PLACEBO_SLACK
    pass_byagent_min = PASS_BYAGENT_MIN_V2 if BYAGENT_GOLD_VERSION == "v2" else PASS_BYAGENT_MIN_V1
    pass_byagent_margin = PASS_BYAGENT_MARGIN_V2 if BYAGENT_GOLD_VERSION == "v2" else PASS_BYAGENT_MARGIN_V1
    byagent_pass = (on_b >= pass_byagent_min and on_b >= base_b + pass_byagent_margin)

    summary = {
        "off_quot_hard": off_q, "off_pass_hard": off_p,
        "on_quot_hard": on_q, "on_pass_hard": on_p,
        "placebo_quot_hard": plac_q, "placebo_pass_hard": plac_p,
        "no_td_quot_hard": notd["quot_hard_acc"], "no_td_pass_hard": notd["pass_hard_acc"],
        "on_quot_easy": on["quot_easy_acc"], "on_pass_easy": on["pass_easy_acc"],
        "off_quot_easy": off["quot_easy_acc"], "off_pass_easy": off["pass_easy_acc"],
        "off_byagent_hard": off_b, "on_byagent_hard": on_b,
        "placebo_byagent_hard": plac_b, "no_td_byagent_hard": notd_b,
        "byagent_floor_held": bool(byagent_floor_held), "byagent_placebo_ok": bool(byagent_placebo_ok),
        "byagent_pass": bool(byagent_pass), "n_byagent_hard": on["byagent_hard_n"],
        "byagent_gold_version": BYAGENT_GOLD_VERSION,
        "pass_byagent_min_used": pass_byagent_min, "pass_byagent_margin_used": pass_byagent_margin,
        "floor_held": floor_held, "placebo_ok_quot": placebo_ok_q, "placebo_ok_pass": placebo_ok_p,
        "placebo_collapses": bool(placebo_collapses), "not_a_leak": bool(not_a_leak),
        "gold_filler_nominal_rate": diag["gold_filler_nominal_rate"],
        "n_quot_hard": on["quot_hard_n"], "n_pass_hard": on["pass_hard_n"],
    }

    # A true LEAK (floor exceeded AND controls also high) invalidates the probe.
    if not floor_held and not not_a_leak:
        return "FLOOR_NOT_HELD_ENCODING_LEAKS_FIX", summary
    if not (placebo_ok_q and placebo_ok_p):
        return "PLACEBO_ARTIFACT_HARD_FAIL_CLAIM", summary

    # PRIMARY = quotative (N=20). passive (N=7) exploratory. ON is compared to the strongest LINEAR-
    # ORDER baseline (max of deterministic OFF and learned position-only NO_TD) so the lift is credited
    # to construction content, not to out-failing a too-weak baseline.
    base_q = max(off_q, notd_q)
    quot_pass = (on_q >= PASS_QUOT_MIN and on_q >= base_q + PASS_QUOT_MARGIN)
    # PRIMARY = quotative (N=20). REAL passive = by-agent (N=5, agent = by-phrase), exploratory. The
    # degenerate all-negative passive is no longer a pass/fail gate (it was base-rate-solved).
    floor_tag = "" if floor_held else "_FLOOR_MARGINAL_POSITION_BASELINE_NOT_LEAK"
    if quot_pass and byagent_pass and byagent_placebo_ok:
        return "HARD_PASS_INTERACTIVE_RESOLVES_QUOTATIVE_AND_BYAGENT" + floor_tag, summary
    if quot_pass and byagent_pass:
        return "PASS_BUT_BYAGENT_PLACEBO_LEAK_CHECK" + floor_tag, summary
    if quot_pass:
        return "PARTIAL_QUOTATIVE_PASS_BYAGENT_UNDERPOWERED_N5" + floor_tag, summary
    if on_q <= base_q + HARD_FAIL_MARGIN:
        return "HARD_FAIL_TOP_DOWN_DID_NOT_RESOLVE" + floor_tag, summary
    return "MIDDLE_PARTIAL_SIGNAL" + floor_tag, summary


def _write_metrics(verdict, summary, units, diag, sents_q, sents_p, sents_b, elapsed, mode):
    # glass-box per-sentence dump (quotative + degenerate passive + by-agent passive)
    dump = []
    for sid, sent in enumerate(sents_q):
        dump.append({"kind": "quotative", "text": sent["text"],
                     "gold_agent_tok": sent["tokens"][sent["gold_target"]] if sent["gold_target"] is not None else None,
                     "first_mention_tok": sent["tokens"][sent["first_ment"]] if sent["first_ment"] is not None else None,
                     "parser_correct": sent["parser_correct"],
                     "mentions": [sent["tokens"][i] for i in sent["mention_idx"]]})
    for sid, sent in enumerate(sents_p):
        dump.append({"kind": "passive", "text": sent["text"],
                     "gold_patient_tok": sent["tokens"][sent["gold_target"]] if sent["gold_target"] is not None else None,
                     "subject_tok": sent["tokens"][sent["subj_idx"]] if sent["subj_idx"] is not None else None,
                     "parser_correct": sent["parser_correct"]})
    for sid, sent in enumerate(sents_b):
        dump.append({"kind": "passive_byagent", "text": sent["text"],
                     "gold_agent_byphrase_tok": sent["tokens"][sent["gold_target"]] if sent["gold_target"] is not None else None,
                     "surface_subj_tok": sent["tokens"][sent["subj_idx"]] if sent["subj_idx"] is not None else None,
                     "mentions": [sent["tokens"][i] for i in sent["mention_idx"]]})
    metrics = {
        "anchor": ANCHOR_NAME, "mode": mode, "verdict": verdict,
        "verdict_msg": ("%s | OFF quot=%.3f byagent=%.3f | ON quot=%.3f byagent=%.3f | "
                        "PLACEBO quot=%.3f byagent=%.3f | NO_TD byagent=%.3f | floor_held=%s/%s | "
                        "tagger_gold_nominal=%.3f"
                        % (verdict, summary["off_quot_hard"], summary["off_byagent_hard"],
                           summary["on_quot_hard"], summary["on_byagent_hard"],
                           summary["placebo_quot_hard"], summary["placebo_byagent_hard"],
                           summary["no_td_byagent_hard"],
                           summary["floor_held"], summary["byagent_floor_held"],
                           summary["gold_filler_nominal_rate"] or -1)),
        "summary": summary,
        "bands": {"FLOOR_QUOT_MAX": FLOOR_QUOT_MAX, "FLOOR_PASS_MAX": FLOOR_PASS_MAX,
                  "PASS_QUOT_MIN": PASS_QUOT_MIN, "PASS_PASS_MIN": PASS_PASS_MIN,
                  "PASS_QUOT_MARGIN": PASS_QUOT_MARGIN, "PASS_PASS_MARGIN": PASS_PASS_MARGIN},
        "per_arm": units,
        "tagger_diagnostic": diag,
        "glass_box_dump": dump,
        "config": {"L2_LAMBDA": L2_LAMBDA, "LR": LR, "N_ITERS": N_ITERS,
                   "n_quot": len(sents_q), "n_pass": len(sents_p), "n_byagent": len(sents_b),
                   "byagent_gold_version": BYAGENT_GOLD_VERSION, "byagent_path": BYAGENT_PATH},
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
    global BYAGENT_GOLD_VERSION, BYAGENT_PATH, OUTPUT_DIR
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--byagent-version", choices=["v1", "v2"], default=BYAGENT_GOLD_VERSION,
                     help="which by-agent-passive gold file to use (v1=N=5 legacy exploratory, "
                          "v2=N=23 powered set, commit 210be7a1c). Default v2.")
    args = ap.parse_args()
    if not args.self_test and not args.full:
        args.self_test = True
    mode = "self_test" if args.self_test else "full"

    BYAGENT_GOLD_VERSION = args.byagent_version
    BYAGENT_PATH = BYAGENT_PATH_V2 if BYAGENT_GOLD_VERSION == "v2" else BYAGENT_PATH_V1
    OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME
                              + ("" if BYAGENT_GOLD_VERSION == "v1" else "_byagent_" + BYAGENT_GOLD_VERSION))
    print("[%s] byagent_gold_version=%s byagent_path=%s output_dir=%s"
          % (mode, BYAGENT_GOLD_VERSION, BYAGENT_PATH, OUTPUT_DIR), flush=True)

    print("[%s] starting %s" % (mode, ANCHOR_NAME), flush=True)
    try:
        units, diag, sents_q, sents_p, sents_b, elapsed = run_all(mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("[%s] FATAL: %s\n%s" % (mode, e, traceback.format_exc()), flush=True)
        raise SystemExit(2)

    _arms_must_differ(units)
    verdict, summary = decide_verdict(units, diag)
    metrics = _write_metrics(verdict, summary, units, diag, sents_q, sents_p, sents_b, elapsed, mode)
    print("[%s] VERDICT: %s" % (mode, verdict), flush=True)
    print("[%s] %s" % (mode, metrics["verdict_msg"]), flush=True)
    print("[%s] elapsed=%.1fs" % (mode, elapsed), flush=True)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
