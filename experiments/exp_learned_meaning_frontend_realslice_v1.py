"""learned_meaning_frontend_realslice_v1 -- does the LEARNED meaning front-end move the REAL thin-meaning
wall, on REAL data, PAST the noise floor?

WALL (atoms 29544-29557, VET-confirmed): over frozen GloVe/WordNet meaning the substrate cannot tell the
CORRECT fine content from a lexically-similar-but-WRONG alternative (hydro/nuclear/coal conflate as
"energy"; entailing vs merely-similar facts). Glass-box: hydroelectric->"clean" MISSED, picks "smoke"
0.65 > "clean" 0.52. Component-1 showed frozen GloVe CARRIES item-signal cosine can't use, but only on a
6-concept toy; component-2 showed a single LINEAR readout beats the entangling MLP (+1/9, toy). Both are
+1/N-noise-floor mechanism-isolations. THIS cell tests whether "meaning is learnable" SCALES to the REAL
wall (fine content over dozens-hundreds of REAL WorldTree concepts) or was a toy artifact.

REAL TASK (WorldTree property tables, dozens-hundreds of concepts): for a concept c under a relation r,
pick c's CORRECT property value g among LEXICALLY-SIMILAR-BUT-WRONG alternatives (the nearest-in-frozen-
GloVe distractors from the SAME relation's value pool -- the real hydro/nuclear/coal-type conflation).
Concepts + values are parsed from curated WorldTree v2.1 tables (KINDOF/MADEOF/PARTOF/HABITAT/CONTAINS/
SOURCEOF/USEDFOR/PROP-RESOURCES-RENEWABLE). N is hundreds+ of eval query instances -> report Wilson 95% CI
(not +1/N).

ARMS (ONE variable = the concept->comparison transform; identical eval question, candidate sets, targets):
  FROZEN         score(c,cand) = cos( frozen_concept_vec(c) , value_vec(cand) )                  [baseline]
  LEARNED-LINEAR score(c,cand) = cos( Wlin @ [concept_vec(c); onehot(r)] , value_vec(cand) )      [PRIMARY]
  LEARNED-MLP    score(c,cand) = cos( MLP([concept_vec(c); onehot(r)]) , value_vec(cand) )         [compare]
The learned arms are trained by MSE property-completion (Rumelhart/Rogers-McClelland) against the gold
value_vec over TRAIN triples; the ONLY learned params are the readout. Frozen is flat (no learning).
A LINEAR readout has limited capacity -> in-vocab success means the frozen concept vectors carry LINEARLY
decodable fine signal (NOT arbitrary memorization), and the shuffled control guards relation-marginal-only
shortcuts.

TIERS: COARSE = KINDOF (category-level "what kind of thing"); FINE = the distinctive-content relations.

PRIMARY (in-vocab, REAL content): does LEARNED-LINEAR discriminate the real fine content frozen GloVe
conflates, as a LEARNING CURVE (fine accuracy vs #exposures = flexible/improving), MATERIALLY above frozen
and BEYOND the noise floor (Wilson CI, not +1/N)? AND does it MOVE THE GLASS-BOX WALL (re-test the real
energy cases: hydroelectric/coal/nuclear/solar renewability + fine content -- does the learned front-end
now get RIGHT what frozen missed)?
SECONDARY (held-out to NEW concepts, reported SEPARATELY, honest coverage framing): generalization to
concepts NOT trained on. Distinctive/item-specific properties are EXPECTED to need ingestion of that
concept (curriculum coverage) -> held-out may be near base-rate; that is the coverage story, not a
front-end failure. Report in-vocab AND held-out separately; held-out does NOT gate HARD_PASS/HARD_FAIL.

MUST-FAIL: shuffled-label control (concept->value mapping permuted within relation; marginals preserved).
Train on shuffled, eval on TRUE -> its curve MUST stay flat / materially below the real arm.

GATES (design-gate all four): real baseline (frozen) / can-fail (frozen genuinely conflates, in band) /
difficulty-on (nearest hard distractors; frozen well below ceiling) / one-variable (only the transform).
No-leak (readout never sees held-out concepts). No tuning to force a win (H/LR/epochs/K a priori).

VERDICT (author-designed a priori, following the task spec -- HP gates IN-VOCAB + glass-box + shuffled;
held-out is reported, NOT gated):
  HARD_PASS = in-vocab fine lift (learned-linear - frozen) >= LIFT_HP with CI-lower-bound > 0 AND real-vs-
              shuffled sep >= SEP AND shuffled stays flat AND in-vocab curve rises AND the learned front-
              end moves the glass-box wall (>= GLASS_MIN of the frozen-missed real energy cases now right).
  MIDDLE    = in-vocab fine lift in [LIFT_HF, LIFT_HP) with controls holding (learning real but modest).
  HARD_FAIL = in-vocab fine lift < LIFT_HF -> the toy "learnable" finding did NOT scale to REAL data ->
              the wall needs DEEPER grounding (Barsalou/perceptual), NOT a learned readout over the same
              thin input. Reported STRAIGHT.
  INVALID   = shuffled matches learned in-vocab (leak) OR neither arm rises (pipeline) OR frozen saturates
              (task too easy) OR too few eval items (noise-floor breach).

Contract: INLINE-LOCAL foreground-to-completion (GloVe/WordNet large/git-ignored -> not remote-portable);
NO push/remote-persist; ASCII-only; deterministic (fixed int seeds, numpy default_rng, sorted iteration;
no builtin-hash-seeded RNG); repo .venv; agent-reported VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker at entry ; crash-diagnostic metrics ; heartbeat
# - real_code_path: self_test parses REAL tables + builds REAL SemanticHDEncoder + REAL readout train/eval
#   at tiny scale AND a PLANTED separable env asserting linear readout LEARNS to discriminate (rises ~1)
#   where FROZEN stays ~chance and SHUFFLED stays flat
# - arms_differ: frozen vs learned-linear vs learned-mlp vs shuffled discrimination scores differ
# - no-leak: held-out concepts NEVER in any training triple; shuffled guards in-vocab marginal shortcut
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no builtin-hash
# - baseline_in_band: FROZEN fine accuracy checked in (near-chance, not-saturated) band at smoke
# - discriminator_fires: LEARNED-LINEAR fine curve must rise above FROZEN in smoke (else respec)
# - difficulty_on: nearest hard distractors; report mean cos(gold,distractor); frozen below ceiling
# - storage = no_composition (self-contained differentiation cell; fixed-VSA selection stage UNCHANGED)
# - GLASS-BOX: energy wall cases logged per-arm (frozen pick+scores vs learned pick+scores vs gold)
# - all reported numbers MEASURED@ this cell's metrics.json
"""
from __future__ import annotations

import os
import re
import sys
import csv
import json
import time
import math
import argparse
import platform
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

from experiments.exp_semantic_hd_encoder_meaning_match_v1 import (  # noqa: E402
    SemanticHDEncoder, _load_glove, _load_wordnet)

ANCHOR_NAME = "learned_meaning_frontend_realslice_v1"
SEED = 20260725
PRETRAIN_DIM = 300

_TABLE_DIR = os.path.join(
    _REPO, "data", "corpora", "worldtree",
    "WorldtreeExplanationCorpusV2.1_Feb2020", "tablestore", "v2.1", "tables")

# curated (table, subject_col_0idx, value_col_0idx) -- stable semantic columns (verified from headers).
# relation name == table name. KINDOF = COARSE tier (category); the rest = FINE distinctive content.
CURATED_TABLES = (
    ("KINDOF", 1, 4),
    ("MADEOF", 2, 6),
    ("PARTOF", 1, 5),
    ("HABITAT", 3, 5),
    ("CONTAINS", 2, 6),
    ("SOURCEOF", 2, 7),
    ("USEDFOR", 2, 6),
    ("PROP-RESOURCES-RENEWABLE", 0, 4),
)
COARSE_RELS = ("KINDOF",)
RELATIONS = tuple(t for (t, _, _) in CURATED_TABLES)
REL_IDX = {r: i for i, r in enumerate(RELATIONS)}
NREL = len(RELATIONS)

STOP = {"", "a", "an", "the", "some", "all", "many", "most", "something", "that", "this",
        "they", "it", "other", "of", "for", "to", "is", "are", "and", "or"}

# ---------------------------------------------------------------------------
# hyperparameters (a priori; NOT tuned for PASS)
# ---------------------------------------------------------------------------
K_DISTRACT = 5           # candidate set = gold + up-to-K nearest frozen distractors -> chance ~1/(K+1)
LR_LIN = 0.5             # linear readout full-batch GD lr (linear -> higher stable lr)
LR_MLP = 0.1             # MLP hub full-batch GD lr
H_BOTTLENECK = 64        # MLP hidden width
WEIGHT_DECAY = 1e-4      # tiny L2 (GD arms)
RIDGE_LAM_FLOOR = 1e-2   # numerical floor for the closed-form normal-equations solve
GRAD_CLIP = 5.0
# GD exposure curve (the flexible/IMPROVING evidence: accuracy vs #exposures). The DECISIVE asymptotic
# lift is measured separately via the CLOSED-FORM converged linear readout (ridge) so the verdict is not
# confounded by GD under-training at real scale (the shared linear map fits ~1500 pairs and converges
# slowly; closed-form = the exact converged GD optimum, cross-checked against the GD-curve plateau).
EXPOSURE_SCHED_FULL = (0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)
EXPOSURE_SCHED_SMOKE = (0, 8, 64, 256)
HELDOUT_CONCEPT_FRAC = 0.15   # fraction of CONCEPTS held out entirely (never in any training triple)

# ---------------------------------------------------------------------------
# pre-registered bands (a priori)
# ---------------------------------------------------------------------------
LIFT_HP = 0.15           # in-vocab fine lift (learned-linear max-exposure - frozen) >= this -> HARD_PASS
LIFT_HF = 0.05           # fine lift < this -> HARD_FAIL (learnable readout did not scale to real data)
SHUFFLE_SEP = 0.10       # learned-linear fine (max exp) - shuffled fine (max exp) >= this
SHUFFLE_FLAT = 0.12      # shuffled fine must stay within this of its exposure-0 value
FROZEN_SAT = 0.85        # frozen fine >= this -> task too easy -> INVALID (harden distractors)
GLASS_MIN = 0.34         # >= this fraction of frozen-MISSED real energy cases must become RIGHT under learned
MIN_EVAL_FINE = 60       # < this many in-vocab fine eval items -> INVALID (noise-floor breach)

_T0 = [0.0]


# ---------------------------------------------------------------------------
# markers / crash diagnostics / heartbeat
# ---------------------------------------------------------------------------
def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics_atomic(output_dir, metrics):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics_atomic(output_dir, diag)


def _heartbeat(output_dir, stage, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - _T0[0], 1)}
    if extra:
        row.update(extra)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"[hb] {stage} {extra if extra else ''}", flush=True)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _l2(v, eps=1e-12):
    n = np.linalg.norm(v)
    return v / (n + eps) if n > 0 else v


def _tok(phrase):
    out, cur = [], []
    for ch in phrase.lower():
        if "a" <= ch <= "z":
            cur.append(ch)
        else:
            if len(cur) >= 2:
                out.append("".join(cur))
            cur = []
    if len(cur) >= 2:
        out.append("".join(cur))
    return out


def meaning_vec(enc, phrase):
    """Frozen fused meaning vector (300d, L2) for a word/phrase; None if no GloVe/WordNet signal."""
    acc = np.zeros(PRETRAIN_DIM, dtype=np.float32)
    got = False
    for w in _tok(phrase):
        fv = enc.fused(w)
        if fv is not None:
            acc = acc + fv
            got = True
    return _l2(acc) if got else None


def _clean(s):
    s = s.strip().lower()
    s = s.split(";")[0].strip()
    s = re.sub(r"[^a-z0-9 \-]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def wilson_ci(k, n, z=1.96):
    """Wilson 95% CI for a binomial proportion; returns (lo, hi)."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / d
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / d
    return (round(center - half, 4), round(center + half, 4))


# ---------------------------------------------------------------------------
# parse curated WorldTree tables -> (concept, relation, value) triples
# ---------------------------------------------------------------------------
def parse_tables(tables):
    triples = []
    for tbl, si, vi in tables:
        path = os.path.join(_TABLE_DIR, tbl + ".tsv")
        with open(path, encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f, delimiter="\t"))
        for row in rows[1:]:
            if len(row) <= max(si, vi):
                continue
            subj = _clean(row[si])
            val = _clean(row[vi])
            if subj in STOP or val in STOP:
                continue
            if not subj or not val:
                continue
            if len(subj.split()) > 4 or len(val.split()) > 4:
                continue
            if subj == val:
                continue
            triples.append((subj, tbl, val))
    # dedupe deterministically
    seen = set()
    out = []
    for t in triples:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return sorted(out)


# ---------------------------------------------------------------------------
# environment: encode concepts + values (frozen), build items + hard candidate sets
# ---------------------------------------------------------------------------
def build_environment(enc, triples, kindof_cap, seed, output_dir):
    """Return env dict. Encodes every concept + value with the frozen encoder (drops OOV). Builds eval
    items (concept, relation, gold-value) and, per item, a HARD candidate set = gold + nearest-K frozen
    distractors from the SAME relation's value pool. Splits CONCEPTS into train vs held-out."""
    # optionally cap KINDOF (dominant table) for balance/speed -- deterministic subsample
    by_rel = defaultdict(list)
    for (c, r, v) in triples:
        by_rel[r].append((c, r, v))
    rng = np.random.default_rng(seed + 101)
    kept_triples = []
    for r in sorted(by_rel.keys()):
        lst = sorted(by_rel[r])
        if r in COARSE_RELS and kindof_cap and len(lst) > kindof_cap:
            idx = np.sort(rng.permutation(len(lst))[:kindof_cap])
            lst = [lst[i] for i in idx.tolist()]
        kept_triples.extend(lst)
    kept_triples = sorted(set(kept_triples))

    # unique concepts + values
    concepts = sorted({c for (c, r, v) in kept_triples})
    values = sorted({v for (c, r, v) in kept_triples})
    _heartbeat(output_dir, "encode_concepts", {"n_concept": len(concepts), "n_value": len(values)})

    # encode (frozen); drop OOV
    cvec = {}
    for c in concepts:
        mv = meaning_vec(enc, c)
        if mv is not None:
            cvec[c] = mv
    vvec = {}
    for v in values:
        mv = meaning_vec(enc, v)
        if mv is not None:
            vvec[v] = mv

    # keep triples whose concept AND value are in-vocab
    triples_iv = [(c, r, v) for (c, r, v) in kept_triples if c in cvec and v in vvec]
    dropped = len(kept_triples) - len(triples_iv)

    # per-relation value pool (distinct in-vocab values that appear as a gold for that relation)
    pool = defaultdict(list)
    for (c, r, v) in triples_iv:
        pool[r].append(v)
    pool = {r: sorted(set(vs)) for r, vs in pool.items()}
    # value_vec matrix per relation for nearest-distractor search
    pool_mat = {r: np.stack([vvec[v] for v in pool[r]], axis=0) for r in pool}

    # gold-values-per-(concept,relation) to exclude true-positives from distractor pool
    gold_by_cr = defaultdict(set)
    for (c, r, v) in triples_iv:
        gold_by_cr[(c, r)].add(v)

    # concept index + train/held-out split by CONCEPT (no-leak)
    all_conc = sorted(cvec.keys())
    cidx = {c: i for i, c in enumerate(all_conc)}
    rng2 = np.random.default_rng(seed + 202)
    perm = rng2.permutation(len(all_conc))
    n_hold = int(round(HELDOUT_CONCEPT_FRAC * len(all_conc)))
    held_concepts = {all_conc[i] for i in perm[:n_hold].tolist()}

    # value index
    all_val = sorted(vvec.keys())
    vidx = {v: i for i, v in enumerate(all_val)}
    value_vecs = np.stack([vvec[v] for v in all_val], axis=0).astype(np.float32)
    concept_vecs = np.stack([cvec[c] for c in all_conc], axis=0).astype(np.float32)

    # build items with hard candidate sets
    items = []  # dict: c_i, r_i, gold_vi, cand_vi(list), tier, concept, relation, gold
    dist_cos_accum = []
    for (c, r, v) in triples_iv:
        p = pool[r]
        if len(p) < 2:
            continue
        gv = vvec[v]
        pm = pool_mat[r]
        sims = pm @ gv  # cosine (all L2)
        order = np.argsort(-sims)  # nearest first
        excl = gold_by_cr[(c, r)]
        distractors = []
        for j in order.tolist():
            cand = p[j]
            if cand == v or cand in excl:
                continue
            distractors.append(cand)
            if len(distractors) >= K_DISTRACT:
                break
        if not distractors:
            continue
        cand_vals = [v] + distractors
        cand_vi = [vidx[x] for x in cand_vals]
        # record mean distractor cosine (difficulty-on evidence)
        dsel = np.array([float(vvec[d] @ gv) for d in distractors], dtype=np.float64)
        dist_cos_accum.append(float(np.mean(dsel)))
        items.append({
            "c_i": cidx[c], "r_i": REL_IDX[r], "gold_vi": vidx[v], "cand_vi": cand_vi,
            "tier": ("coarse" if r in COARSE_RELS else "fine"),
            "concept": c, "relation": r, "gold": v, "held": (c in held_concepts),
        })

    env = {
        "concept_vecs": concept_vecs, "value_vecs": value_vecs,
        "all_conc": all_conc, "all_val": all_val, "cidx": cidx, "vidx": vidx,
        "items": items, "held_concepts": sorted(held_concepts),
        "n_triples_parsed": len(kept_triples), "n_triples_invocab": len(triples_iv), "dropped_oov": dropped,
        "pool_sizes": {r: len(pool[r]) for r in sorted(pool.keys())},
        "mean_distractor_cosine": round(float(np.mean(dist_cos_accum)), 4) if dist_cos_accum else None,
    }
    return env


# ---------------------------------------------------------------------------
# training-pair construction (item + relation -> gold value_vec)
# ---------------------------------------------------------------------------
def _rel_onehot_batch(r_idx_arr):
    M = np.zeros((len(r_idx_arr), NREL), dtype=np.float32)
    M[np.arange(len(r_idx_arr)), r_idx_arr] = 1.0
    return M


def make_train_matrix(env, train_items, shuffle_seed=None):
    """X [n, 300+NREL], Y [n, 300]. If shuffle_seed given, permute the gold value_vec assignment WITHIN
    each relation (marginals preserved, concept->value mapping destroyed) = must-fail control targets."""
    cvecs = env["concept_vecs"]
    vvecs = env["value_vecs"]
    ci = np.array([it["c_i"] for it in train_items])
    ri = np.array([it["r_i"] for it in train_items])
    gi = np.array([it["gold_vi"] for it in train_items])
    if shuffle_seed is not None:
        rng = np.random.default_rng(shuffle_seed)
        gi = gi.copy()
        by_r = defaultdict(list)
        for pos, it in enumerate(train_items):
            by_r[it["r_i"]].append(pos)
        for r in sorted(by_r.keys()):
            pos = np.array(sorted(by_r[r]))
            gi[pos] = gi[pos][rng.permutation(len(pos))]
    X = np.concatenate([cvecs[ci], _rel_onehot_batch(ri)], axis=1).astype(np.float32)
    Y = vvecs[gi].astype(np.float32)
    return X, Y


# ---------------------------------------------------------------------------
# readouts: LINEAR (single matrix) + MLP (tanh bottleneck). full-batch GD, MSE.
# ---------------------------------------------------------------------------
class LinearReadout:
    kind = "linear"

    def __init__(self, in_dim, out_dim, seed):
        rng = np.random.default_rng(seed)
        self.W = (rng.standard_normal((in_dim, out_dim)).astype(np.float32) / np.sqrt(in_dim))
        self.b = np.zeros(out_dim, dtype=np.float32)

    def forward(self, X):
        return X @ self.W + self.b

    def train_epochs(self, X, Y, n_epochs, lr, wd, clip=GRAD_CLIP):
        n = max(1, X.shape[0])
        for _ in range(n_epochs):
            Yh = X @ self.W + self.b
            dYh = (2.0 / n) * (Yh - Y)
            dW = X.T @ dYh + wd * self.W
            db = dYh.sum(axis=0)
            if clip:
                for g in (dW, db):
                    nrm = np.linalg.norm(g)
                    if nrm > clip:
                        g *= clip / nrm
            self.W -= lr * dW
            self.b -= lr * db


class ClosedFormLinear:
    """CONVERGED linear readout via ridge regression: W* = argmin ||[X,1] W - Y||^2 + lam||W||^2.
    Exact convex optimum -> the GD asymptote without under-training (the 308x308 normal equations are
    tiny/instant). Same model class as LinearReadout; used for the DECISIVE asymptotic-lift measurement."""
    kind = "linear_converged"

    def __init__(self, X, Y, lam):
        n, d = X.shape
        Xa = np.concatenate([X, np.ones((n, 1), dtype=np.float32)], axis=1)
        A = Xa.T @ Xa + lam * np.eye(d + 1, dtype=np.float64)
        B = Xa.T @ Y
        self.Wa = np.linalg.solve(A.astype(np.float64), B.astype(np.float64)).astype(np.float32)

    def forward(self, X):
        Xa = np.concatenate([X, np.ones((X.shape[0], 1), dtype=np.float32)], axis=1)
        return Xa @ self.Wa


def fit_converged_linear(env, train_items, weight_decay, shuffle_seed=None):
    """Converged linear readout = the EXACT optimum of the GD arm's objective
    (1/n)||XW-Y||^2 + (wd/2)||W||^2, whose ridge lambda in the normal equations is lam = wd*n/2 (matched
    so the closed form reproduces GD-at-convergence, not a differently-regularized point)."""
    X, Y = make_train_matrix(env, train_items, shuffle_seed=shuffle_seed)
    lam = max(weight_decay * X.shape[0] / 2.0, RIDGE_LAM_FLOOR)
    return ClosedFormLinear(X, Y, lam)


class MLPReadout:
    kind = "mlp"

    def __init__(self, in_dim, h, out_dim, seed):
        rng = np.random.default_rng(seed)
        self.W1 = (rng.standard_normal((in_dim, h)).astype(np.float32) / np.sqrt(in_dim))
        self.b1 = np.zeros(h, dtype=np.float32)
        self.W2 = (rng.standard_normal((h, out_dim)).astype(np.float32) / np.sqrt(h))
        self.b2 = np.zeros(out_dim, dtype=np.float32)

    def forward(self, X):
        A1 = np.tanh(X @ self.W1 + self.b1)
        return A1 @ self.W2 + self.b2

    def train_epochs(self, X, Y, n_epochs, lr, wd, clip=GRAD_CLIP):
        n = max(1, X.shape[0])
        for _ in range(n_epochs):
            Z1 = X @ self.W1 + self.b1
            A1 = np.tanh(Z1)
            Yh = A1 @ self.W2 + self.b2
            dYh = (2.0 / n) * (Yh - Y)
            dW2 = A1.T @ dYh + wd * self.W2
            db2 = dYh.sum(axis=0)
            dA1 = dYh @ self.W2.T
            dZ1 = dA1 * (1.0 - A1 * A1)
            dW1 = X.T @ dZ1 + wd * self.W1
            db1 = dZ1.sum(axis=0)
            if clip:
                for g in (dW1, db1, dW2, db2):
                    nrm = np.linalg.norm(g)
                    if nrm > clip:
                        g *= clip / nrm
            self.W1 -= lr * dW1
            self.b1 -= lr * db1
            self.W2 -= lr * dW2
            self.b2 -= lr * db2


# ---------------------------------------------------------------------------
# vectorized discrimination eval
# ---------------------------------------------------------------------------
def _l2_rows(M, eps=1e-12):
    n = np.linalg.norm(M, axis=1, keepdims=True)
    return M / (n + eps)


def _cand_arrays(env, items):
    """Fixed-width candidate index matrix + validity mask + gold index vector for a list of items."""
    W = K_DISTRACT + 1
    n = len(items)
    C = np.zeros((n, W), dtype=np.int64)
    mask = np.zeros((n, W), dtype=bool)
    gold = np.array([it["gold_vi"] for it in items], dtype=np.int64)
    for i, it in enumerate(items):
        cv = it["cand_vi"]
        C[i, :len(cv)] = cv
        mask[i, :len(cv)] = True
    return C, mask, gold


def discriminate(env, items, reps, C, mask, gold):
    """reps [n,300] = the scorer vector per item (frozen concept_vec OR learned pred). Returns accuracy +
    per-tier + per-relation accuracy over the candidate sets."""
    if len(items) == 0:
        return {"acc": None, "n": 0, "per_tier": {}, "per_rel": {}, "correct_mask": np.zeros(0, bool)}
    R = _l2_rows(reps)
    Vc = env["value_vecs"][C]  # [n, W, 300]
    scores = np.einsum("nd,nwd->nw", R, Vc)  # [n, W]
    scores = np.where(mask, scores, -1e30)
    pick = C[np.arange(len(items)), np.argmax(scores, axis=1)]
    correct = (pick == gold)
    acc = round(float(np.mean(correct)), 4)
    per_tier = {}
    for tier in ("coarse", "fine"):
        idx = [i for i, it in enumerate(items) if it["tier"] == tier]
        if idx:
            k = int(np.sum(correct[idx]))
            per_tier[tier] = {"acc": round(k / len(idx), 4), "n": len(idx), "ci": wilson_ci(k, len(idx))}
    per_rel = {}
    for r in sorted(set(it["relation"] for it in items)):
        idx = [i for i, it in enumerate(items) if it["relation"] == r]
        k = int(np.sum(correct[idx]))
        per_rel[r] = {"acc": round(k / len(idx), 4), "n": len(idx)}
    return {"acc": acc, "n": len(items), "per_tier": per_tier, "per_rel": per_rel, "correct_mask": correct}


def frozen_reps(env, items):
    return env["concept_vecs"][np.array([it["c_i"] for it in items], dtype=np.int64)]


def learned_reps(env, items, readout):
    ci = np.array([it["c_i"] for it in items], dtype=np.int64)
    ri = np.array([it["r_i"] for it in items], dtype=np.int64)
    X = np.concatenate([env["concept_vecs"][ci], _rel_onehot_batch(ri)], axis=1).astype(np.float32)
    return readout.forward(X)


# ---------------------------------------------------------------------------
# exposure curve
# ---------------------------------------------------------------------------
def exposure_curve(env, train_items, eval_groups, schedule, readout_ctor, lr, seed, label,
                   output_dir, shuffle_seed=None):
    """Train readout from scratch on train_items (targets shuffled if shuffle_seed); at each exposure
    milestone measure discrimination on each eval group. eval_groups: dict name -> (items,C,mask,gold).
    Returns {exposures, groups:{name:{fine[],coarse[],acc[]}}, readout}."""
    X, Y = make_train_matrix(env, train_items, shuffle_seed=shuffle_seed)
    readout = readout_ctor(seed)
    groups = {name: {"acc": [], "fine": [], "coarse": []} for name in eval_groups}
    prev = 0
    for e in schedule:
        step = e - prev
        if step > 0:
            readout.train_epochs(X, Y, step, lr, WEIGHT_DECAY)
            prev = e
        for name, (items, C, mask, gold) in eval_groups.items():
            reps = learned_reps(env, items, readout)
            res = discriminate(env, items, reps, C, mask, gold)
            groups[name]["acc"].append(res["acc"])
            groups[name]["fine"].append(res["per_tier"].get("fine", {}).get("acc"))
            groups[name]["coarse"].append(res["per_tier"].get("coarse", {}).get("acc"))
        _heartbeat(output_dir, f"curve_{label}", {"exposure": e,
                   "iv_fine": groups.get("invocab", {}).get("fine", [None])[-1]})
    return {"exposures": list(schedule), "groups": groups, "readout": readout}


def _crossing(exposures, accs, frac=0.8):
    vals = [a for a in accs if a is not None]
    if not vals:
        return None
    asy = max(vals)
    if asy <= 0:
        return None
    thr = frac * asy
    for e, a in zip(exposures, accs):
        if a is not None and a >= thr:
            return e
    return None


# ---------------------------------------------------------------------------
# glass-box energy wall re-test
# ---------------------------------------------------------------------------
ENERGY_KEYS = ("solar", "wind", "hydro", "nuclear", "coal", "geo", "gas", "oil", "fossil",
               "tidal", "wave", "biomass", "chemical", "electric", "fuel")


def glassbox_energy(env, items, frozen_correct, learned_correct):
    """Report the REAL energy wall cases: concept(+relation) where the gold/concept is an energy source.
    For each, whether FROZEN got it right and whether LEARNED got it right (moves-the-wall accounting)."""
    cases = []
    frozen_missed = 0
    learned_fixed = 0
    for i, it in enumerate(items):
        text = it["concept"] + " " + it["gold"]
        if not any(k in text for k in ENERGY_KEYS):
            continue
        fc = bool(frozen_correct[i])
        lc = bool(learned_correct[i])
        cases.append({"concept": it["concept"], "relation": it["relation"], "gold": it["gold"],
                      "n_cand": len(it["cand_vi"]), "frozen_correct": fc, "learned_correct": lc})
        if not fc:
            frozen_missed += 1
            if lc:
                learned_fixed += 1
    frac_fixed = round(learned_fixed / frozen_missed, 4) if frozen_missed else None
    return {"n_energy_cases": len(cases), "frozen_missed": frozen_missed,
            "learned_fixed_of_missed": learned_fixed, "frac_missed_now_fixed": frac_fixed,
            "cases": sorted(cases, key=lambda d: (d["relation"], d["concept"]))[:40]}


# ---------------------------------------------------------------------------
# self-test: planted separable env (linear readout learns) + real code path
# ---------------------------------------------------------------------------
def _planted_linear(nd=64):
    """Planted env: distinct concept vectors; per-(concept,rel) target = a distinct random value drawn
    from a shared per-relation value pool. A LINEAR readout MUST learn to map concept+rel -> its own
    value so fine discrimination rises to ~1, FROZEN (concept-vs-value cosine) stays ~chance, and a
    SHUFFLED-trained readout evaluated on TRUE targets stays flat."""
    global PRETRAIN_DIM
    old = PRETRAIN_DIM
    PRETRAIN_DIM = nd
    try:
        rng = np.random.default_rng(31)
        n_c, W = 6, K_DISTRACT + 1
        n_val = 12
        value_vecs = _l2_rows(rng.standard_normal((n_val, nd)).astype(np.float32))
        concept_vecs = _l2_rows(rng.standard_normal((n_c, nd)).astype(np.float32))
        # each concept -> a distinct gold value under relation 0
        golds = list(range(n_c))  # concept i gold = value i
        items = []
        for i in range(n_c):
            distract = [j for j in range(n_val) if j != golds[i]][:K_DISTRACT]
            items.append({"c_i": i, "r_i": 0, "gold_vi": golds[i], "cand_vi": [golds[i]] + distract,
                          "tier": "fine", "concept": f"c{i}", "relation": "R0", "gold": f"v{golds[i]}",
                          "held": False})
        env = {"concept_vecs": concept_vecs, "value_vecs": value_vecs}
        C, mask, gold = _cand_arrays(env, items)
        # frozen
        fr = discriminate(env, items, frozen_reps(env, items), C, mask, gold)
        # learned linear
        X, Y = make_train_matrix(env, items)
        ro = LinearReadout(nd + NREL, nd, seed=7)
        ro.train_epochs(X, Y, 1500, 0.5, 0.0)
        lr_res = discriminate(env, items, learned_reps(env, items, ro), C, mask, gold)
        # shuffled-trained, eval-true
        Xs, Ys = make_train_matrix(env, items, shuffle_seed=1)
        ros = LinearReadout(nd + NREL, nd, seed=7)
        ros.train_epochs(Xs, Ys, 1500, 0.5, 0.0)
        sh_res = discriminate(env, items, learned_reps(env, items, ros), C, mask, gold)
    finally:
        PRETRAIN_DIM = old
    assert lr_res["acc"] >= 0.9, f"planted: linear readout did not learn (acc={lr_res['acc']})"
    assert lr_res["acc"] - fr["acc"] >= 0.3, f"planted: no lift over frozen (learned={lr_res['acc']} frozen={fr['acc']})"
    assert lr_res["acc"] - sh_res["acc"] >= 0.3, f"planted: shuffled control not separated (learned={lr_res['acc']} shuffled={sh_res['acc']})"
    return {"frozen": fr["acc"], "learned_linear": lr_res["acc"], "shuffled_true_eval": sh_res["acc"]}


def self_test():
    print("[self-test] planted separable env: linear readout must learn (fine->~1), frozen ~chance, "
          "shuffled flat ...", flush=True)
    planted = _planted_linear()
    print(f"[self-test]   planted: {planted}", flush=True)

    print("[self-test] REAL code path: parse tables + SemanticHDEncoder + build_environment + "
          "one real linear train epoch ...", flush=True)
    output_dir = _out_dir()
    triples = parse_tables(CURATED_TABLES)
    assert len(triples) > 500, f"real: too few triples parsed ({len(triples)})"
    kv = _load_glove()
    _load_wordnet()
    enc = SemanticHDEncoder(n_dim=512, seed=SEED, use_wordnet=True, kv=kv)
    # tiny real env: 2 fine tables only, capped
    tiny = parse_tables((("MADEOF", 2, 6), ("HABITAT", 3, 5)))
    env = build_environment(enc, tiny, kindof_cap=0, seed=SEED, output_dir=output_dir)
    assert len(env["items"]) >= 20, f"real: too few items ({len(env['items'])})"
    train_items = [it for it in env["items"] if not it["held"]]
    C, mask, gold = _cand_arrays(env, train_items)
    fr = discriminate(env, train_items, frozen_reps(env, train_items), C, mask, gold)
    X, Y = make_train_matrix(env, train_items)
    ro = LinearReadout(PRETRAIN_DIM + NREL, PRETRAIN_DIM, seed=SEED + 11)
    ro.train_epochs(X, Y, 3, LR_LIN, WEIGHT_DECAY)
    lr_res = discriminate(env, train_items, learned_reps(env, train_items, ro), C, mask, gold)
    # determinism
    ro2 = LinearReadout(PRETRAIN_DIM + NREL, PRETRAIN_DIM, seed=SEED + 11)
    ro2.train_epochs(X, Y, 3, LR_LIN, WEIGHT_DECAY)
    assert np.allclose(ro.W, ro2.W), "real: training non-deterministic"
    # arms differ
    assert not np.allclose(learned_reps(env, train_items[:1], ro), frozen_reps(env, train_items[:1])), \
        "real: learned arm == frozen arm"
    # converged closed-form linear exercises ClosedFormLinear on the real path
    conv = fit_converged_linear(env, train_items, WEIGHT_DECAY)
    conv_res = discriminate(env, train_items, learned_reps(env, train_items, conv), C, mask, gold)
    assert conv_res["acc"] >= fr["acc"], f"real: converged linear should reach >= frozen ({conv_res['acc']} vs {fr['acc']})"
    print(f"[self-test]   real: n_items={len(env['items'])} frozen_acc={fr['acc']} learned3ep={lr_res['acc']} "
          f"converged_acc={conv_res['acc']} mean_distractor_cos={env['mean_distractor_cosine']} "
          f"dropped_oov={env['dropped_oov']}", flush=True)
    print("[self-test] PASS (planted linear readout fires; real parse+encode+train path; determinism; "
          "arms differ)", flush=True)
    return True


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        # fine content at real-but-reduced scale: 3 fine tables + small KINDOF cap; short schedule
        return {"n_dim": 512,
                "tables": (("KINDOF", 1, 4), ("MADEOF", 2, 6), ("CONTAINS", 2, 6), ("SOURCEOF", 2, 7),
                           ("PROP-RESOURCES-RENEWABLE", 0, 4)),
                "kindof_cap": 200, "schedule": EXPOSURE_SCHED_SMOKE}
    return {"n_dim": 512, "tables": CURATED_TABLES, "kindof_cap": 700, "schedule": EXPOSURE_SCHED_FULL}


# ---------------------------------------------------------------------------
# verdict
# ---------------------------------------------------------------------------
def _verdict(conv_lin_fine, frozen_iv_fine, conv_shuf_fine, gd_lin_curve, gd_shuf_curve, glass,
             frozen_iv_fine_sat, n_eval_fine, conv_ci_lo):
    """DECISIVE lift/sep from the CONVERGED (closed-form) linear readout; the GD curve supplies the
    improving-with-exposure evidence (rises) and the must-fail control's did-not-rise check."""
    lift = round(conv_lin_fine - frozen_iv_fine, 4)
    sep = round(conv_lin_fine - conv_shuf_fine, 4)
    _lv = [a for a in gd_lin_curve if a is not None]
    rises = ((max(_lv) - gd_lin_curve[0]) > 0.05) if _lv else False  # GD accuracy IMPROVES with exposure
    # must-fail control passes iff the shuffled GD arm never RISES materially above its untrained start
    # (a DROP below chance is stronger no-leak evidence, NOT a failure -> one-sided, not abs()).
    _sv = [a for a in gd_shuf_curve if a is not None]
    shuf_did_not_rise = ((max(_sv) - gd_shuf_curve[0]) <= SHUFFLE_FLAT) if _sv else False
    controls_hold = sep >= SHUFFLE_SEP and shuf_did_not_rise
    ci_lo_pos = (conv_ci_lo is not None and conv_ci_lo > frozen_iv_fine)
    glass_ok = (glass["frac_missed_now_fixed"] is not None and glass["frac_missed_now_fixed"] >= GLASS_MIN)
    extra = {"iv_fine_lift_converged": lift, "iv_true_vs_shuffled_sep_converged": sep,
             "iv_curve_rises": bool(rises), "shuffled_did_not_rise": bool(shuf_did_not_rise),
             "controls_hold": bool(controls_hold), "iv_fine_ci_lower_above_frozen": bool(ci_lo_pos),
             "glass_moves_wall": bool(glass_ok), "glass_frac_fixed": glass["frac_missed_now_fixed"]}

    if n_eval_fine < MIN_EVAL_FINE:
        return "INVALID", f"only {n_eval_fine} in-vocab fine eval items (< {MIN_EVAL_FINE}) -- noise-floor breach", extra
    if frozen_iv_fine_sat:
        return "INVALID", f"frozen in-vocab fine acc={frozen_iv_fine} >= {FROZEN_SAT}: task too easy -- harden distractors", extra
    if not rises:
        return "INVALID", "learned-linear GD curve does not improve with exposure (pipeline/degenerate) -- debug before conclusion", extra
    if conv_shuf_fine >= conv_lin_fine - 0.02:
        return "INVALID", f"converged shuffled-trained/true-eval control matched learned-linear in-vocab (sep={sep}) -- leak/marginal-shortcut", extra
    if lift >= LIFT_HP and controls_hold and ci_lo_pos and glass_ok:
        return "HARD_PASS", (f"converged learned-linear lifts REAL in-vocab fine discrimination by {lift}>={LIFT_HP} over "
                             f"frozen (CI-lower > frozen), beyond noise floor; true-vs-shuffled sep={sep}; GD curve improves "
                             f"with exposure; AND moves the glass-box wall ({glass['learned_fixed_of_missed']}/"
                             f"{glass['frozen_missed']} frozen-missed energy cases now RIGHT, frac={glass['frac_missed_now_fixed']}) "
                             f"-> the toy 'meaning is learnable' finding SCALES to real data"), extra
    if lift >= LIFT_HF and controls_hold:
        return "MIDDLE", (f"converged learned-linear in-vocab fine lift={lift} (in [{LIFT_HF},{LIFT_HP})) with controls "
                          f"holding (sep={sep}, CI-lower-above-frozen={ci_lo_pos}); real+improving but modest; glass "
                          f"frac_fixed={glass['frac_missed_now_fixed']}; the learnable front-end MOVES the real wall "
                          f"but not to the HARD_PASS bar -> partial scaling; deeper grounding still indicated for the rest"), extra
    if lift < LIFT_HF:
        return "HARD_FAIL", (f"converged learned-linear in-vocab fine lift={lift} < {LIFT_HF}: the toy 'meaning is "
                             f"learnable' finding did NOT scale to REAL data -> the wall needs DEEPER grounding "
                             f"(Barsalou/perceptual), not a learned readout over the same thin frozen input"), extra
    return "INVALID", (f"lift={lift} >= {LIFT_HF} but controls did not hold (sep={sep}, "
                       f"shuffled_did_not_rise={shuf_did_not_rise}) -- control ambiguous; inspect before conclusion"), extra


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------
def run(mode, output_dir):
    cfg = _config(mode)
    _heartbeat(output_dir, "parse_tables")
    triples = parse_tables(cfg["tables"])
    _heartbeat(output_dir, "load_glove", {"n_triples": len(triples)})
    kv = _load_glove()
    _load_wordnet()
    enc = SemanticHDEncoder(n_dim=cfg["n_dim"], seed=SEED, use_wordnet=True, kv=kv)

    _heartbeat(output_dir, "build_environment")
    env = build_environment(enc, triples, cfg["kindof_cap"], SEED, output_dir)
    items = env["items"]
    train_items = [it for it in items if not it["held"]]
    held_items = [it for it in items if it["held"]]
    # in-vocab eval = trained concepts' items (memorization-inclusive but linear-capacity-limited + shuffled-guarded)
    iv_items = train_items
    print(f"[env] triples_parsed={env['n_triples_parsed']} invocab={env['n_triples_invocab']} "
          f"dropped_oov={env['dropped_oov']} items={len(items)} iv={len(iv_items)} held={len(held_items)}", flush=True)
    print(f"[env] pool_sizes={env['pool_sizes']} mean_distractor_cos={env['mean_distractor_cosine']}", flush=True)

    n_eval_fine = sum(1 for it in iv_items if it["tier"] == "fine")
    n_eval_coarse = sum(1 for it in iv_items if it["tier"] == "coarse")
    if n_eval_fine == 0:
        m = {"verdict": "INVALID", "verdict_msg": "no fine-tier eval items", "summary": "INVALID: no fine items",
             "run_mode": mode, "elapsed_s": round(time.perf_counter() - _T0[0], 2),
             "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
        _write_metrics_atomic(output_dir, m)
        print("[verdict] INVALID: no fine items", flush=True)
        return m

    # candidate arrays per eval group (fixed across arms/milestones)
    iv_C, iv_mask, iv_gold = _cand_arrays(env, iv_items)
    ho_C, ho_mask, ho_gold = (_cand_arrays(env, held_items) if held_items else (None, None, None))
    eval_groups = {"invocab": (iv_items, iv_C, iv_mask, iv_gold)}
    if held_items:
        eval_groups["heldout"] = (held_items, ho_C, ho_mask, ho_gold)

    # ---- FROZEN baseline (flat) ----
    _heartbeat(output_dir, "frozen_baseline")
    fr_iv = discriminate(env, iv_items, frozen_reps(env, iv_items), iv_C, iv_mask, iv_gold)
    frozen_iv_fine = fr_iv["per_tier"].get("fine", {}).get("acc")
    frozen_iv_fine_ci = fr_iv["per_tier"].get("fine", {}).get("ci")
    frozen_iv_coarse = fr_iv["per_tier"].get("coarse", {}).get("acc")
    fr_ho = (discriminate(env, held_items, frozen_reps(env, held_items), ho_C, ho_mask, ho_gold)
             if held_items else {"per_tier": {}})
    frozen_ho_fine = fr_ho["per_tier"].get("fine", {}).get("acc")
    chance_fine = round(float(np.mean([1.0 / len(it["cand_vi"]) for it in iv_items if it["tier"] == "fine"])), 4)
    print(f"[frozen] iv_fine={frozen_iv_fine} (ci={frozen_iv_fine_ci}, chance~{chance_fine}) "
          f"iv_coarse={frozen_iv_coarse} ho_fine={frozen_ho_fine}", flush=True)

    # ---- LEARNED-LINEAR (PRIMARY) exposure curve ----
    _heartbeat(output_dir, "learned_linear_curve")
    lin = exposure_curve(env, train_items, eval_groups, cfg["schedule"],
                         lambda s: LinearReadout(PRETRAIN_DIM + NREL, PRETRAIN_DIM, seed=s + 11),
                         LR_LIN, SEED, "linear", output_dir)
    L_iv_fine = lin["groups"]["invocab"]["fine"]
    L_iv_coarse = lin["groups"]["invocab"]["coarse"]
    L_ho_fine = lin["groups"].get("heldout", {}).get("fine")

    # ---- LEARNED-MLP (comparison) exposure curve ----
    _heartbeat(output_dir, "learned_mlp_curve")
    mlp = exposure_curve(env, train_items, eval_groups, cfg["schedule"],
                         lambda s: MLPReadout(PRETRAIN_DIM + NREL, H_BOTTLENECK, PRETRAIN_DIM, seed=s + 11),
                         LR_MLP, SEED, "mlp", output_dir)
    M_iv_fine = mlp["groups"]["invocab"]["fine"]
    M_ho_fine = mlp["groups"].get("heldout", {}).get("fine")

    # ---- SHUFFLED must-fail control (linear; train shuffled, eval TRUE) ----
    _heartbeat(output_dir, "shuffled_curve")
    shuf = exposure_curve(env, train_items, eval_groups, cfg["schedule"],
                          lambda s: LinearReadout(PRETRAIN_DIM + NREL, PRETRAIN_DIM, seed=s + 11),
                          LR_LIN, SEED, "shuffled", output_dir, shuffle_seed=SEED + 9090)
    S_iv_fine = shuf["groups"]["invocab"]["fine"]
    S_ho_fine = shuf["groups"].get("heldout", {}).get("fine")

    # ---- CONVERGED (closed-form ridge) linear readouts: DECISIVE asymptotic measurement ----
    # true-target converged linear (avoids GD under-training confound at real scale)
    _heartbeat(output_dir, "converged_linear")
    conv_lin = fit_converged_linear(env, train_items, WEIGHT_DECAY)
    conv_lin_res = discriminate(env, iv_items, learned_reps(env, iv_items, conv_lin), iv_C, iv_mask, iv_gold)
    conv_lin_fine = conv_lin_res["per_tier"].get("fine", {}).get("acc")
    conv_lin_fine_ci = conv_lin_res["per_tier"].get("fine", {}).get("ci")
    conv_lin_coarse = conv_lin_res["per_tier"].get("coarse", {}).get("acc")
    conv_ci_lo = conv_lin_fine_ci[0] if conv_lin_fine_ci else None
    # converged shuffled control (train permuted targets, eval TRUE)
    conv_shuf = fit_converged_linear(env, train_items, WEIGHT_DECAY, shuffle_seed=SEED + 9090)
    conv_shuf_res = discriminate(env, iv_items, learned_reps(env, iv_items, conv_shuf), iv_C, iv_mask, iv_gold)
    conv_shuf_fine = conv_shuf_res["per_tier"].get("fine", {}).get("acc")
    # converged held-out (coverage story)
    conv_lin_ho = (discriminate(env, held_items, learned_reps(env, held_items, conv_lin), ho_C, ho_mask, ho_gold)
                   if held_items else {"per_tier": {}})
    conv_lin_ho_fine = conv_lin_ho["per_tier"].get("fine", {}).get("acc")
    print(f"[converged] lin_iv_fine={conv_lin_fine} (ci={conv_lin_fine_ci}) shuf_iv_fine={conv_shuf_fine} "
          f"lin_ho_fine={conv_lin_ho_fine} (frozen_iv_fine={frozen_iv_fine})", flush=True)

    # ---- glass-box energy wall re-test (in-vocab items; on the CONVERGED linear readout) ----
    frozen_correct = fr_iv["correct_mask"]
    learned_correct = conv_lin_res["correct_mask"]
    glass = glassbox_energy(env, iv_items, frozen_correct, learned_correct)
    print(f"[glass] energy_cases={glass['n_energy_cases']} frozen_missed={glass['frozen_missed']} "
          f"learned_fixed={glass['learned_fixed_of_missed']} frac_fixed={glass['frac_missed_now_fixed']}", flush=True)

    # ---- coarse-before-fine ordering (note pred; diagnostic) on the GD curve ----
    coarse_cross = _crossing(cfg["schedule"], L_iv_coarse)
    fine_cross = _crossing(cfg["schedule"], L_iv_fine)
    coarse_before_fine = (coarse_cross is not None and fine_cross is not None and coarse_cross <= fine_cross)

    # ---- guards / verdict (DECISIVE = converged lift/sep; GD curves = improving + control-did-not-rise) ----
    frozen_sat = (frozen_iv_fine is not None and frozen_iv_fine >= FROZEN_SAT)
    verdict, vmsg, gx = _verdict(conv_lin_fine, frozen_iv_fine, conv_shuf_fine, L_iv_fine, S_iv_fine,
                                 glass, frozen_sat, n_eval_fine, conv_ci_lo)

    # arms differ (GD linear vs frozen vs shuffled vs mlp vs converged)
    arms_differ = not (abs(L_iv_fine[-1] - (frozen_iv_fine or 0)) < 1e-9
                       and abs(L_iv_fine[-1] - S_iv_fine[-1]) < 1e-9
                       and abs(L_iv_fine[-1] - M_iv_fine[-1]) < 1e-9
                       and abs((conv_lin_fine or 0) - (frozen_iv_fine or 0)) < 1e-9)

    # held-out lift (SECONDARY, reported, honest coverage framing)
    ho_lin_lift = (round(L_ho_fine[-1] - frozen_ho_fine, 4)
                   if (L_ho_fine and frozen_ho_fine is not None and L_ho_fine[-1] is not None) else None)

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg, "summary": f"{verdict}: {vmsg}",
        "run_mode": mode, "elapsed_s": round(time.perf_counter() - _T0[0], 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME, "seed": SEED,
        "one_variable": "concept->comparison transform (FROZEN vs LEARNED-LINEAR vs LEARNED-MLP); identical eval/candidates/targets",
        "primary_metric": "in-vocab FINE-tier discrimination learning curve (learned-linear vs frozen) on REAL WorldTree content, Wilson CI",
        # scale / difficulty-on
        "n_triples_parsed": env["n_triples_parsed"], "n_triples_invocab": env["n_triples_invocab"],
        "dropped_oov": env["dropped_oov"], "n_items": len(items),
        "n_eval_fine_invocab": n_eval_fine, "n_eval_coarse_invocab": n_eval_coarse,
        "n_heldout_items": len(held_items), "n_heldout_concepts": len(env["held_concepts"]),
        "pool_sizes": env["pool_sizes"], "K_distract": K_DISTRACT, "chance_fine": chance_fine,
        "mean_distractor_cosine": env["mean_distractor_cosine"],
        "exposures": list(cfg["schedule"]),
        # PRIMARY: GD learning curves (in-vocab) = flexible/IMPROVING evidence (accuracy vs #exposures)
        "learned_linear_fine_invocab_curve_GD": L_iv_fine,
        "learned_linear_coarse_invocab_curve_GD": L_iv_coarse,
        "learned_mlp_fine_invocab_curve_GD": M_iv_fine,
        "shuffled_fine_invocab_curve_GD": S_iv_fine,
        "frozen_fine_invocab": frozen_iv_fine, "frozen_fine_invocab_ci": frozen_iv_fine_ci,
        "frozen_coarse_invocab": frozen_iv_coarse,
        # DECISIVE: CONVERGED (closed-form ridge) linear = the asymptotic-lift measurement (no GD under-train confound)
        "converged_linear_fine_invocab": conv_lin_fine,
        "converged_linear_fine_invocab_ci": conv_lin_fine_ci,
        "converged_linear_coarse_invocab": conv_lin_coarse,
        "converged_shuffled_fine_invocab": conv_shuf_fine,
        "in_vocab_fine_lift_over_frozen_converged": gx["iv_fine_lift_converged"],
        "in_vocab_true_vs_shuffled_sep_converged": gx["iv_true_vs_shuffled_sep_converged"],
        "note_converged_vs_GD": "converged = closed-form ridge (exact GD optimum); GD curve is under-trained at real scale (shared linear map fits ~1500 pairs, converges slowly) -> verdict lift/sep use CONVERGED; GD curve shows learnability/improvement with exposure",
        # SECONDARY (held-out; reported separately; coverage story; NOT a HP/HF gate)
        "learned_linear_fine_heldout_curve_GD": L_ho_fine,
        "learned_mlp_fine_heldout_curve_GD": M_ho_fine,
        "shuffled_fine_heldout_curve_GD": S_ho_fine,
        "converged_linear_fine_heldout": conv_lin_ho_fine,
        "frozen_fine_heldout": frozen_ho_fine,
        "heldout_fine_lift_over_frozen_GD": ho_lin_lift,
        "heldout_fine_lift_over_frozen_converged": (round(conv_lin_ho_fine - frozen_ho_fine, 4)
                                                    if (conv_lin_ho_fine is not None and frozen_ho_fine is not None) else None),
        "heldout_note": "distinctive/item-specific properties expected to need per-concept ingestion (curriculum coverage); held-out near base-rate is the coverage story, NOT a front-end failure",
        # controls / gates
        "controls_hold": gx["controls_hold"], "shuffled_did_not_rise": gx["shuffled_did_not_rise"],
        "iv_curve_rises": gx["iv_curve_rises"], "iv_fine_ci_lower_above_frozen": gx["iv_fine_ci_lower_above_frozen"],
        # glass-box wall
        "glassbox_energy": glass, "glass_moves_wall": gx["glass_moves_wall"],
        # ordering diagnostic
        "coarse_before_fine": {"coarse_cross": coarse_cross, "fine_cross": fine_cross,
                               "coarse_before_fine": bool(coarse_before_fine)},
        # bands
        "bands": {"LIFT_HP": LIFT_HP, "LIFT_HF": LIFT_HF, "SHUFFLE_SEP": SHUFFLE_SEP,
                  "SHUFFLE_FLAT": SHUFFLE_FLAT, "FROZEN_SAT": FROZEN_SAT, "GLASS_MIN": GLASS_MIN,
                  "MIN_EVAL_FINE": MIN_EVAL_FINE},
        "hub_config": {"K_DISTRACT": K_DISTRACT, "LR_LIN": LR_LIN, "LR_MLP": LR_MLP,
                       "H_BOTTLENECK": H_BOTTLENECK, "WEIGHT_DECAY": WEIGHT_DECAY},
        "arms_differ_verified": bool(arms_differ),
        "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": "fixed_int_seeds_numpy_default_rng_sorted_no_builtin_hash",
        "storage": "no_composition_selfcontained_differentiation",
        "difficulty_on": f"nearest-frozen hard distractors; mean_distractor_cos={env['mean_distractor_cosine']}; frozen fine below ceiling",
        "contract": "INLINE-LOCAL foreground-to-completion; no push/remote-persist; VET-PENDING",
    }
    _write_metrics_atomic(output_dir, metrics)
    print(f"[verdict] {verdict}: {vmsg}", flush=True)
    print(f"[curves] frozen_iv_fine={frozen_iv_fine} GD_learned_lin_iv_fine={L_iv_fine}", flush=True)
    print(f"[curves] GD_learned_mlp_iv_fine={M_iv_fine} GD_shuffled_iv_fine={S_iv_fine}", flush=True)
    print(f"[converged] lin_iv_fine={conv_lin_fine} shuf_iv_fine={conv_shuf_fine} "
          f"lift={gx['iv_fine_lift_converged']} sep={gx['iv_true_vs_shuffled_sep_converged']}", flush=True)
    print(f"[curves] heldout: frozen={frozen_ho_fine} conv_lin={conv_lin_ho_fine} GD_lin={L_ho_fine}", flush=True)
    print(f"[gates] {gx}", flush=True)
    return metrics


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    _T0[0] = time.perf_counter()
    output_dir = _out_dir()

    if args.self_test:
        _write_start_marker(output_dir, "self_test")
        ok = self_test()
        sys.exit(0 if ok else 1)

    mode = "smoke" if args.smoke else "full"
    _write_start_marker(output_dir, mode)
    run(mode, output_dir)
    sys.exit(0)


if __name__ == "__main__":
    _out_dir_top = _out_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_out_dir_top, e)
        raise
