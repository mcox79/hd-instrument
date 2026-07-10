"""MULTI-ATTRIBUTE GROUNDING FUSION: does reliability-weighted fusion of several GENUINELY-INDEPENDENT measured
attributes turn the WEAK single-attribute grounding (concreteness-only: grounding_gap 0.059 but cv 0.69, HIGH washes,
carried by one seed) into a ROBUST grounding lift that clears the MM->CG promotion criterion the single attribute missed?

BRAIN GROUND (ATL hub-and-spoke; Patterson/Lambon-Ralph; Ernst&Banks MLE cue combination; law of inverse effectiveness):
robust grounding is NEVER one channel -- it is convergence of many independent weak "senses" onto a shared hub, weighted
in inverse proportion to each channel's noise (MLE / inverse-variance), and the WEAKER each channel the LARGER its
proportional fusion gain (inverse effectiveness). A single MARGINAL attribute is exactly the regime where the biology
predicts the largest payoff from adding independent channels -- NOT a sign the lever is played out.

WHAT THIS CELL EXTENDS: `exp_grounding_measured_attribute_concreteness_v1` (commit 382b6ae5e). Same VALIDATED
diffusion-with-restart engine (`grounding_consolidation_loop_degree_invariant_v1`), same fairness gate (F_triv<F_A<C),
same degree strata, same leak-free held-out masking, same scrambled must-fail -- APPLIED PER ATTRIBUTE, then FUSED.

TARGET (apples-to-apples with the weak result): held-out concreteness (Brysbaert Conc.M). Hold out 30% of concepts;
predict their concreteness from graph position + the exterior measured channels; Spearman rank corr, aggregate + per
degree stratum. grounding_gap == Spearman(fused) - Spearman(relational-only) -- the SAME metric that read 0.059.

ATTRIBUTES (joined to the ConceptNet subgraph; all public human-rating norms; provenance-tracked LOCAL testbed inputs,
NOT canonical substrate_index; self-acquired via curl if absent):
  concreteness (Brysbaert)  | valence/arousal/dominance (Warriner)  | 6 Lynott-Connell/Lancaster sensory-modality
  perceptual-strength means (Visual/Haptic/Auditory/Gustatory/Olfactory/Interoceptive)  | Kuperman age-of-acquisition.

GUARDRAIL 1 -- PER-ATTRIBUTE INDEPENDENCE GATE (make-or-break; the candidate attributes are NOT all independent):
  * report the FULL own-data pairwise correlation matrix among all candidates (the drill's explicit deliverable);
  * SELECT the fused set by INCREMENTAL VALIDITY (the correct conditional test, since two channels that both measure
    the target are MARGINALLY correlated by construction -- CLIP/co-training conditional-independence subtlety):
    SEL=[concreteness]; order remaining by |r_target| desc; ADD a candidate iff (a) marginal |r| with every already-
    selected attr < REDUNDANT_R_HARD (near-duplicate guard, catches the imageability/concreteness r=-0.8 case) AND
    (b) it adds incremental R^2 >= INCR_R2_MIN for predicting the target beyond SEL. FUSE only the selected set.
  * if fewer than 2 attributes survive -> HARD_FAIL_CHANNELS_NOT_INDEPENDENT (nothing non-redundant to fuse).

GUARDRAIL 2 -- REDUNDANCY-FAKING MUST-FAIL CONTROL: an arm that fuses concreteness with near-duplicate copies of itself
  (r~0.99, no new sense) must NOT beat single-attribute. If it does, the fusion metric is laundering re-weighted
  redundancy as a K-channel gain -> the whole result is vacuous -> HARD_FAIL_REDUNDANCY_CHEAT.

FUSION MECHANIC (late fusion = free per-channel ablation; reliability-weighted MLE, the most literature-validated rule):
  per selected attribute k: build the leak-free restart anchor from attribute-k VISIBLE values (held-out AND missing
  MASKED to the visible-observed mean), concat to the structural channel, diffuse-with-restart, ridge-predict held-out
  concreteness -> pred_k. reliability w_k = max(0, visible-CV Spearman)^2 (inverse-variance proxy) computed ONLY on a
  visible sub-holdout (val nodes masked in the anchor) -> NO leakage from the decision split (anti-overfit, Pitfall #2).
  fused prediction = sum_k w_k * z(pred_k). ALL channels are masked on held-out so every channel grounds PURELY via graph
  diffusion (the "rare concept lacks all norms" regime; no direct feature access).

ARMS (all predict held-out concreteness on the SAME split per seed -> PAIRED):
  F_TRIV (mean null), F_A (relational-only = ablation of ALL exterior channels), A_PLUS_B_SINGLE (concreteness-only =
  the v1 mechanism, the baseline-to-BEAT), A_PLUS_FUSED (reliability-weighted fusion of the selected set = MECHANISM),
  A_PLUS_FUSED_REDUNDANT (near-duplicate copies = must-fail redundancy control), A_PLUS_FUSED_SCRAMBLED (selected attrs
  permuted across concepts = must-fail values control), C_CEILING (graph-neighbour TRUE-concreteness smoothing oracle).

PROMOTION CRITERION (pre-registered HARD_PASS_FUSION_ROBUST; the VET-banked MM->CG bar the single attribute MISSED; ALL):
  fairness cleared AND >=2 attrs survive independence AND not collapsed AND
  (1) mean grounding_gap(fused) >= GROUND_MARGIN (0.05)                        [material lift]
  (2) cross-seed cv(grounding_gap) < CV_MAX (0.15)                            [robust, not seed-fragile]
  (3) LEAVE-ONE-SEED-OUT: dropping ANY seed, mean grounding_gap still >= 0.05 [not carried by one seed]
  (4) HIGH-degree stratum fused gap >= HIGH_NONNEG (0.0; NON-NEGATIVE)        [degree-uniform, HIGH no longer washes]
  (5) fusion BEATS single: mean(fused - single) >= FUSION_BEAT (0.02)         [fusion, not just the concreteness channel]
  (6) redundancy control: (redundant - single) <= REDUNDANT_MAX (0.02)       [not laundering redundancy]
  (7) scramble control: (scrambled - F_A) <= SCRAMBLE_MAX (0.02)             [depends on VALUES]

HARD_FAIL_FUSION_NOT_ROBUST: fusion ties single (fused-single <= 0) OR seed-fragile (cv >= CV_FAIL 0.30 OR a LOSO drop
  falls below 0.05) OR HIGH still washes (HIGH gap < 0).
HARD_FAIL_REDUNDANCY_CHEAT: redundant control beats single by >= FUSION_BEAT OR scrambled grounds (>= GROUND_MARGIN).
HARD_FAIL_FAIRNESS_BLOCKED / HARD_FAIL_CHANNELS_NOT_INDEPENDENT / HARD_FAIL_CONSOLIDATION_COLLAPSED: gates.
MIDDLE_BAND_PARTIAL: otherwise (lift present but cv in [0.15,0.30) / gap sub-material / fusion-beat small).

COVERAGE-DENSITY DIAGNOSTIC (cheap disambiguator, logged BEFORE the fusion verdict): per-held-out-node single-attribute
lift = |err_FA| - |err_AB| correlated with visible-degree + #visible-neighbours. MEASURED@existing v1 result: lift
correlates NEGATIVELY with density (Spearman ~ -0.07 / -0.05; mean lift LOW-degree +0.029 vs HIGH -0.013) -> the
marginality is NOT coverage-limited (the channel helps MOST in sparse regions; it vanishes at HIGH degree because F_A
already saturates there = a HEADROOM/ceiling artifact, not missing coverage) -> channel-limited in low/mid = the regime
fusion targets; HIGH washout is an F_A-ceiling effect, so do not expect fusion to rescue HIGH beyond non-negative.

SELF-TEST (planted worlds; discriminators must FIRE): (a) independent-attributes-COMPOUND (K channels = latent + INDEP
noise -> fused BEATS single); (b) correlated-attributes-DONT-beat-single (redundant near-duplicate copies -> redundant
gap ~0; independence gate PRUNES them to 1); (c) scrambled-all does NOT ground; (d) collapse caught; (e) fairness gate
passes headroom world + blocks unpredictable world. Saturation-vacuous guard: the must-fail controls FAIL at self-test
scale by construction.

## Compute architecture
class (a) batched-GPU-capable but CPU-fast: structural features + per-channel diffusion (dense [n,n]@[n,dim], n~3262) +
ridge (small solves). ~K*(2 diffusions) per seed, K~4-6 selected -> ~seconds/seed on CPU. NO KGE / NO encoder training.
Storage SHARDED. FULL routes to remote_cpu_queue (CPU; no GPU benefit; SMOKE-ONLY-LOCAL lock keeps the laptop free).

CELL-TEMPLATE MANDATORY: arms_differ_verified (>=6 distinct arm sigs); final_metrics_atomicity=tmp_replace; except
SystemExit before except Exception (no BaseException/bare); crlb: Spearman chance ~0 (THEORETICAL), HARD_PASS strictly
above floor; baseline_in_band: F_TRIV null ~0, C must-fire ceiling > F_A; discriminator-survives-scale: engine params
shared self-test<->FULL, real-graph fusion robustness is the open measurement (self-test fires compound/redundant/
scramble discriminators); HP_SCOPE: robustness gate on A_PLUS_FUSED vs F_A + single + redundant + scrambled;
calibration_check=default_ok_for_this_regime; progress_logging=print_flush_true; cell_chunked=false; start_marker +
crash_diagnostic present; cardinality_ok EXPECTED_N_UNITS=n_seeds.
"""

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir, write_metrics, write_partial  # noqa: E402
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import SUBGRAPH_BASE_SEED  # noqa: E402
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import load_typed_cn_subgraph  # noqa: E402
import experiments.exp_grounding_consolidation_loop_degree_invariant_v1 as eng  # noqa: E402

ANCHOR_NAME = "grounding_multiattribute_fusion_v1"

TESTBED = os.path.join(_REPO, "data", "grounding_testbed")

# ---- Testbed dataset files + self-acquire URLs (public human-rating norms; LOCAL testbed inputs; NOT canonical store) --
DATASETS = {
    "conc": dict(path=os.path.join(TESTBED, "Concreteness_ratings_Brysbaert_et_al_BRM.txt"),
                 url="https://raw.githubusercontent.com/ArtsEngine/concreteness/master/"
                     "Concreteness_ratings_Brysbaert_et_al_BRM.txt", header_key="Conc.M"),
    "warriner": dict(path=os.path.join(TESTBED, "Ratings_Warriner_et_al.csv"),
                     url="https://raw.githubusercontent.com/JULIELab/XANEW/master/Ratings_Warriner_et_al.csv",
                     header_key="V.Mean.Sum"),
    "lancaster": dict(path=os.path.join(TESTBED, "Lancaster_sensorimotor_norms_for_39707_words.csv"),
                      url="https://osf.io/48wsc/download", header_key="Visual.mean"),
    "aoa": dict(path=os.path.join(TESTBED, "AoA_51715_words.csv"),
                url="https://raw.githubusercontent.com/Cody-Lange/Milestone-2-Text-Difficulty-Classifier/"
                    "main/assets/AoA_51715_words.csv", header_key="AoA_Kup"),
}

# ---- Candidate attributes (name -> (dataset, column)); TARGET is concreteness (index 0) ----
TARGET = "concreteness"
CANDIDATES = [
    ("concreteness", "conc", "Conc.M"),
    ("valence", "warriner", "V.Mean.Sum"),
    ("arousal", "warriner", "A.Mean.Sum"),
    ("dominance", "warriner", "D.Mean.Sum"),
    ("visual", "lancaster", "Visual.mean"),
    ("haptic", "lancaster", "Haptic.mean"),
    ("auditory", "lancaster", "Auditory.mean"),
    ("gustatory", "lancaster", "Gustatory.mean"),
    ("olfactory", "lancaster", "Olfactory.mean"),
    ("interoceptive", "lancaster", "Interoceptive.mean"),
    ("aoa", "aoa", "AoA_Kup"),
]

# ---- Arm names ----
F_TRIV = "F_TRIV"
F_A = "F_A_RELATIONAL"
A_SINGLE = "A_PLUS_B_SINGLE"           # concreteness-only exterior channel (the v1 mechanism; baseline-to-beat)
A_FUSED = "A_PLUS_FUSED"               # reliability-weighted fusion of the independence-selected set (MECHANISM)
A_FUSED_RED = "A_PLUS_FUSED_REDUNDANT"  # must-fail: near-duplicate copies (redundancy cheat control)
A_FUSED_SCR = "A_PLUS_FUSED_SCRAMBLED"  # must-fail: selected attrs permuted across concepts (values control)
C_CEIL = "C_CEILING"
ALL_ARMS = [F_TRIV, F_A, A_SINGLE, A_FUSED, A_FUSED_RED, A_FUSED_SCR, C_CEIL]
STRATA = ["LOW", "MID", "HIGH"]

# ---- Pre-registered bands (principled; picked BEFORE the run) ----
FAIR_FLOOR_GAP = 0.05
FAIR_HEADROOM = 0.05
GROUND_MARGIN = 0.05        # (1) material fused lift over relational-only
CV_MAX = 0.15              # (2) HARD_PASS robustness: cross-seed cv(grounding_gap) below this
CV_FAIL = 0.30            # HARD_FAIL fragility: cv at/above this
HIGH_NONNEG = 0.0        # (4) HIGH-degree stratum fused gap must be >= this (non-negative)
FUSION_BEAT = 0.02      # (5) fusion must beat single-attribute by at least this
REDUNDANT_MAX = 0.02   # (6) redundant control must not beat single by more than this
SCRAMBLE_MAX = 0.02   # (7) scrambled fusion grounding gap must be <= this
TIE_EPS = 0.0        # HARD_FAIL "ties single": (fused - single) <= this
MIN_STRAT_Q = 40
HELDOUT_FRAC = 0.30
VIS_VAL_FRAC = 0.30        # visible sub-holdout for reliability weighting (leak-free; val nodes masked in the anchor)
RIDGE_LAM = 5.0
DIM = 64
ATTR_COLS = 16

# ---- Independence selection thresholds ----
REDUNDANT_R = 0.70         # marginal |r| pruning: candidate is redundant with an already-selected attr if |r| >= this
                           # ("highly correlated -> treat as one channel"; drill's ~0.5-0.7 guidance) -> pruned.
MIN_TARGET_R = 0.20       # a candidate must explain >= ~4% of target variance (|r| >= this) to count as a real "sense"
                          # -> excludes near-zero-correlation valence/dominance (per drill "add VAD only if it clears")
INCR_R2_MIN = 0.003      # reported-only diagnostic: incremental R^2 for the target beyond the selected set
REDUNDANT_COPY_NOISE = 0.15  # near-duplicate copy noise (std fraction) -> mutual r ~ 0.99 (no new sense)

SELFTEST_CFG = dict(seeds=[7], n_nodes=0)
SMOKE_CFG = dict(seeds=[7, 13], n_nodes=2500)
FULL_CFG = dict(seeds=[7, 13, 17, 23, 29], n_nodes=5000)


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.3f" % x) if (x == x) else "nan"


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp"); final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp"); final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Data acquisition + join.
# ---------------------------------------------------------------------------

def _ensure_dataset(key):
    d = DATASETS[key]; path = d["path"]
    if os.path.exists(path):
        return True
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        subprocess.run(["curl", "-sSL", "--max-time", "180", "-o", tmp, d["url"]], check=True)
        with open(tmp, encoding="utf-8", errors="replace") as f:
            head = f.readline()
        if d["header_key"] not in head:
            os.remove(tmp); return False
        os.replace(tmp, path)
        _log("acquired %s from %s" % (key, d["url"]))
        return True
    except Exception as e:
        _log("could not self-acquire %s: %s: %s" % (key, type(e).__name__, str(e)[:150]))
        return False


def _norm_word(w):
    return str(w).strip().lower().replace("_", " ")


def _load_col_map(key, column, sep):
    """Load {lowercased_word: float(value)} for one dataset column; skip blank/NA."""
    path = DATASETS[key]["path"]
    with open(path, encoding="utf-8", errors="replace") as f:
        header = f.readline().rstrip("\n").rstrip("\r").split(sep)
    if column not in header:
        raise RuntimeError("column %r not in %s header" % (column, key))
    ci = header.index(column)
    wi = header.index("Word") if "Word" in header else 1
    out = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        f.readline()
        for line in f:
            p = line.rstrip("\n").rstrip("\r").split(sep)
            if len(p) <= max(ci, wi):
                continue
            v = p[ci].strip()
            if v == "" or v.upper() == "NA" or v.upper() == "NAN":
                continue
            try:
                fv = float(v)
            except ValueError:
                continue
            w = _norm_word(p[wi])
            if w and w not in out:
                out[w] = fv
    return out


def build_multiattr_subgraph(n_nodes, base_seed):
    """Join all candidate attributes to the covered+connected ConceptNet subgraph (target=concreteness present).
    Returns (tri, Y, present, deg, A, attr_names, meta). Y: [n, K] with NaN where an attribute is missing for a node."""
    maps = {}
    maps["conc"] = _load_col_map("conc", "Conc.M", "\t")
    maps["warriner"] = None  # per-column loaded below
    # load each candidate's map lazily by (dataset, column)
    col_maps = {}
    seps = {"conc": "\t", "warriner": ",", "lancaster": ",", "aoa": ","}
    for name, ds, col in CANDIDATES:
        col_maps[name] = _load_col_map(ds, col, seps[ds])

    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(n_nodes, base_seed)
    edges = np.asarray(edges, dtype=np.int64)
    n0 = len(node_ids)
    conc_map = col_maps["concreteness"]
    y_conc = np.full(n0, np.nan)
    for i, w in enumerate(node_words):
        k = _norm_word(w)
        if k in conc_map:
            y_conc[i] = conc_map[k]
        elif k.replace(" ", "") in conc_map:
            y_conc[i] = conc_map[k.replace(" ", "")]
    cov = np.isfinite(y_conc)                     # target coverage (concreteness must be present)
    keep = np.where(cov)[0]
    im = {int(o): i for i, o in enumerate(keep)}
    names0 = [node_words[int(o)] for o in keep]
    m = len(keep)
    Amat = np.zeros((m, m), dtype=np.float32)
    for a, b in edges:
        a = int(a); b = int(b)
        if a in im and b in im and a != b:
            Amat[im[a], im[b]] = 1.0; Amat[im[b], im[a]] = 1.0
    conn = np.where(Amat.sum(axis=1) > 0)[0]
    Amat = Amat[np.ix_(conn, conn)]
    names = [names0[int(c)] for c in conn]
    m2 = len(conn)

    # Build [m2, K] attribute matrix over the covered+connected nodes.
    K = len(CANDIDATES)
    Y = np.full((m2, K), np.nan, dtype=np.float64)
    for ci, (name, ds, col) in enumerate(CANDIDATES):
        cm = col_maps[name]
        for i, w in enumerate(names):
            k = _norm_word(w)
            if k in cm:
                Y[i, ci] = cm[k]
            elif k.replace(" ", "") in cm:
                Y[i, ci] = cm[k.replace(" ", "")]
    present = np.isfinite(Y)
    deg = Amat.sum(axis=1)
    ij = np.argwhere(Amat > 0)
    tri = np.stack([ij[:, 0], np.zeros(ij.shape[0], dtype=np.int64), ij[:, 1]], axis=1).astype(np.int64)
    attr_names = [c[0] for c in CANDIDATES]
    cover_frac = {attr_names[ci]: float(present[:, ci].mean()) for ci in range(K)}
    meta2 = dict(n_subgraph=n0, n_covered_concreteness=int(cov.sum()),
                 coverage_frac_concreteness=float(cov.mean()), n_covered_connected=m2,
                 n_edges=int(tri.shape[0]), deg_min=float(deg.min()), deg_med=float(np.median(deg)),
                 deg_max=float(deg.max()), attr_coverage=cover_frac, subgraph_meta=meta)
    return tri, Y, present, deg, Amat, attr_names, meta2


# ---------------------------------------------------------------------------
# Prediction primitives.
# ---------------------------------------------------------------------------

def _spearman(a, b):
    a = np.asarray(a, dtype=np.float64); b = np.asarray(b, dtype=np.float64)
    if a.shape[0] < 3:
        return float("nan")
    ar = np.argsort(np.argsort(a)).astype(np.float64)
    br = np.argsort(np.argsort(b)).astype(np.float64)
    return eng._pearson(ar, br)


def _zscore(v):
    v = np.asarray(v, dtype=np.float64); s = v.std()
    return (v - v.mean()) / (s + 1e-9)


def _ridge_predict(X, y, tr, te, lam=RIDGE_LAM):
    Xtr = X[tr]; mu = Xtr.mean(axis=0); Xtr = Xtr - mu; ytr = y[tr]
    G = Xtr.T @ Xtr + lam * np.eye(X.shape[1])
    w = np.linalg.solve(G, Xtr.T @ (ytr - ytr.mean()))
    return (X[te] - mu) @ w + ytr.mean()


def _attr_anchor(yk, obs_mask, device, ncol=ATTR_COLS):
    """Restart anchor for one attribute: observed (visible AND present) values normalized; everything else (held-out,
    missing, and any reliability-val nodes) MASKED to the visible-observed mean -> LEAK-FREE + missing-safe."""
    yf = np.asarray(yk, dtype=np.float64).copy()
    obs = np.asarray(obs_mask, dtype=bool)
    if obs.sum() < 2:
        mu = 0.0; sd = 1.0
    else:
        mu = float(yf[obs].mean()); sd = float(yf[obs].std()) + 1e-9
    yf[~obs] = mu
    yf = (yf - mu) / sd
    return torch.from_numpy(yf.astype(np.float32)).to(device)[:, None].repeat(1, ncol)


def _neighbour_true_mean(A, y):
    s = A @ y; d = A.sum(axis=1)
    return np.where(d > 0, s / np.maximum(d, 1.0), y.mean())


def _strata_labels(deg_hold):
    if deg_hold.shape[0] == 0:
        return np.zeros(0, dtype=np.int64)
    q1 = float(np.quantile(deg_hold, 1.0 / 3.0)); q2 = float(np.quantile(deg_hold, 2.0 / 3.0))
    lab = np.zeros(deg_hold.shape[0], dtype=np.int64)
    lab[deg_hold > q1] = 1; lab[deg_hold > q2] = 2
    return lab


# ---------------------------------------------------------------------------
# Independence gate: full correlation matrix + incremental-validity selection.
# ---------------------------------------------------------------------------

def _r2_linear(Xcols, ytarget):
    """R^2 of OLS ytarget ~ [1, Xcols] (Xcols: list of 1-D arrays; mean-imputed, finite)."""
    n = ytarget.shape[0]
    X = np.concatenate([np.ones((n, 1))] + [c.reshape(-1, 1) for c in Xcols], axis=1) if Xcols \
        else np.ones((n, 1))
    beta, _res, _rank, _sv = np.linalg.lstsq(X, ytarget, rcond=None)
    pred = X @ beta
    ss_res = float(((ytarget - pred) ** 2).sum())
    ss_tot = float(((ytarget - ytarget.mean()) ** 2).sum()) + 1e-12
    return 1.0 - ss_res / ss_tot


def independence_select(Y, present, attr_names, target_vec):
    """Report the full pairwise |r| matrix; SELECT by MARGINAL-correlation greedy pruning ("highly correlated ->
    treat as one channel"): SEL=[concreteness anchor]; order remaining by |r_target| desc; ADD a candidate iff it
    marginally correlates with the target (|r_target| >= MIN_TARGET_R) AND its max |r| with every already-selected
    attribute < REDUNDANT_R (else it re-weights redundancy). Incremental R^2 is computed + reported as a diagnostic
    only. target_vec is the prediction target (raw concreteness for real data; a hidden latent for the self-test)."""
    K = Y.shape[1]
    Yimp = Y.copy()
    for ci in range(K):
        col = Yimp[:, ci]; m = np.isfinite(col)
        Yimp[~m, ci] = col[m].mean() if m.sum() > 0 else 0.0
    corr = np.eye(K)
    for i in range(K):
        for j in range(i + 1, K):
            both = present[:, i] & present[:, j]
            r = eng._pearson(Y[both, i], Y[both, j]) if both.sum() >= 10 else 0.0
            corr[i, j] = corr[j, i] = r
    ti = attr_names.index(TARGET)
    tv = np.asarray(target_vec, dtype=np.float64)
    r_target = {}
    for ci in range(K):
        m = present[:, ci] & np.isfinite(tv)
        r_target[attr_names[ci]] = eng._pearson(Y[m, ci], tv[m]) if m.sum() >= 10 else 0.0

    sel = [TARGET]
    order = sorted([c for c in range(K) if c != ti], key=lambda c: -abs(r_target[attr_names[c]]))
    audit = []
    for c in order:
        name = attr_names[c]
        max_r_sel = max(abs(corr[c, attr_names.index(s)]) for s in sel)
        target_ok = bool(abs(r_target[name]) >= MIN_TARGET_R)
        redundant = bool(max_r_sel >= REDUNDANT_R)
        # incremental-R2 DIAGNOSTIC (reported only): incremental validity beyond the already-selected NON-anchor extras
        # (concreteness excluded from the predictor pool -- its raw value == the target, so it would trivialize R2).
        extras = [Yimp[:, attr_names.index(s)] for s in sel if s != TARGET]
        r2_old = _r2_linear(extras, tv)
        r2_new = _r2_linear(extras + [Yimp[:, c]], tv)
        incr = r2_new - r2_old
        keep = bool(target_ok and (not redundant))
        audit.append(dict(attr=name, r_target=round(r_target[name], 3), max_r_selected=round(max_r_sel, 3),
                          incr_r2=round(incr, 4), target_ok=target_ok, redundant=redundant, selected=keep))
        if keep:
            sel.append(name)
    info = dict(corr_matrix=[[round(float(corr[i, j]), 3) for j in range(K)] for i in range(K)],
                attr_names=attr_names, r_target={k: round(float(v), 3) for k, v in r_target.items()},
                selection_audit=audit, selected=sel, n_selected=len(sel), redundant_r=REDUNDANT_R)
    return sel, info


# ---------------------------------------------------------------------------
# One attribute channel: diffuse-with-restart, ridge-predict held-out target; + reliability via visible sub-holdout.
# ---------------------------------------------------------------------------

def _channel_pred(fs, a_src, a_dst, yk, present_k, y_target, obs_mask, tr_nodes, te_nodes, n, device):
    """Diffuse structural+attribute-k anchor (obs_mask observed, else masked), ridge-fit target on tr_nodes, predict
    te_nodes. Returns pred over te_nodes."""
    E0 = torch.cat([fs, _attr_anchor(yk, obs_mask, device)], dim=1)
    E = eng.consolidate(a_src, a_dst, E0, n, eng.CONS_PASSES, eng.CONS_ALPHA, device, "")
    En = E.cpu().numpy()
    return _ridge_predict(En, y_target, tr_nodes, te_nodes), E


def _reliability(fs, a_src, a_dst, yk, y_target, vis_nodes, hold_mask, n, device, seed):
    """Visible-CV reliability = max(0, Spearman(pred_val, true_val))^2, val nodes MASKED in the anchor (leak-free)."""
    rng = np.random.default_rng(seed * 7 + 101)
    vperm = rng.permutation(vis_nodes)
    nval = max(1, int(VIS_VAL_FRAC * vis_nodes.shape[0]))
    val = vperm[:nval]; vtr = vperm[nval:]
    obs = np.ones(n, dtype=bool); obs[hold_mask] = False; obs[val] = False   # observed = visible-train AND present-safe
    obs &= np.isfinite(yk)
    pred_val, _E = _channel_pred(fs, a_src, a_dst, yk, None, y_target, obs, vtr, val, n, device)
    r = _spearman(pred_val, y_target[val])
    return float(max(0.0, r) ** 2) if r == r else 0.0


def _fused_prediction(fs, a_src, a_dst, chan_vals, y_target, vis_nodes, hold_nodes, hold_mask, n, device, seed):
    """Reliability-weighted late fusion over a list of attribute-value arrays (chan_vals). Returns (pred_hold, weights,
    per_channel_pred)."""
    preds = []; rels = []
    for ci, yk in enumerate(chan_vals):
        obs = np.ones(n, dtype=bool); obs[hold_mask] = False; obs &= np.isfinite(yk)
        pred, _E = _channel_pred(fs, a_src, a_dst, yk, None, y_target, obs, vis_nodes, hold_nodes, n, device)
        rel = _reliability(fs, a_src, a_dst, yk, y_target, vis_nodes, hold_mask, n, device, seed + ci)
        preds.append(pred); rels.append(rel)
    rels = np.asarray(rels, dtype=np.float64)
    w = rels / rels.sum() if rels.sum() > 1e-12 else np.ones_like(rels) / len(rels)
    fused = np.zeros(hold_nodes.shape[0], dtype=np.float64)
    for ci in range(len(preds)):
        fused = fused + w[ci] * _zscore(preds[ci])
    return fused, w, preds


# ---------------------------------------------------------------------------
# Per-seed run.
# ---------------------------------------------------------------------------

def run_seed(seed, tri, Y, present, deg, A, sel_idx, device, y_target_override=None):
    n = Y.shape[0]
    # target = concreteness (Y[:,0]) on real data; a hidden latent override in the planted self-test worlds so genuinely
    # independent noisy channels can compound (concreteness alone is not a noise-free copy of the target there).
    y_target = np.asarray(y_target_override, dtype=np.float64) if y_target_override is not None else Y[:, 0]
    rng = np.random.default_rng(seed * 100003 + 17)
    perm = rng.permutation(n); nh = int(HELDOUT_FRAC * n)
    hold = perm[:nh]; vis = perm[nh:]
    hold_mask = np.zeros(n, dtype=bool); hold_mask[hold] = True
    deg_hold = deg[hold]; strata = _strata_labels(deg_hold)
    yh = y_target[hold]

    fs = eng.structural_features(tri, n, DIM, seed, device)
    a_src, a_dst = eng.agreement_edges(fs, fs, eng.CONS_KNN, device)

    # F_A relational-only (ablation of ALL exterior channels)
    E_A = eng.consolidate(a_src, a_dst, fs, n, eng.CONS_PASSES, eng.CONS_ALPHA, device, "")
    pred_FA = _ridge_predict(E_A.cpu().numpy(), y_target, vis, hold)

    # A_PLUS_B_SINGLE: concreteness-only exterior channel (the v1 mechanism)
    obs_c = (~hold_mask) & np.isfinite(Y[:, 0])
    pred_single, E_single = _channel_pred(fs, a_src, a_dst, Y[:, 0], None, y_target, obs_c, vis, hold, n, device)
    cons_eff_rank = eng._effective_rank(E_single); cons_rep_var = eng._rep_variance(E_single)

    # A_PLUS_FUSED: reliability-weighted fusion of the selected non-redundant attributes
    sel_vals = [Y[:, ci] for ci in sel_idx]
    pred_fused, w_fused, _pc = _fused_prediction(fs, a_src, a_dst, sel_vals, y_target, vis, hold, hold_mask, n, device,
                                                 seed)

    # A_PLUS_FUSED_REDUNDANT: concreteness + near-duplicate copies (r~0.99); K matched to the selected count
    crng = np.random.default_rng(seed * 13 + 7)
    ystd = float(np.nanstd(Y[:, 0]))
    red_vals = [Y[:, 0]]
    for _ in range(max(1, len(sel_idx) - 1)):
        red_vals.append(Y[:, 0] + REDUNDANT_COPY_NOISE * ystd * crng.standard_normal(n))
    pred_red, w_red, _pr = _fused_prediction(fs, a_src, a_dst, red_vals, y_target, vis, hold, hold_mask, n, device,
                                             seed + 555)

    # A_PLUS_FUSED_SCRAMBLED: selected attributes permuted across concepts (values control)
    scr_vals = [Y[np.random.default_rng(seed + 900 + ci).permutation(n), ci] for ci in sel_idx]
    pred_scr, w_scr, _ps = _fused_prediction(fs, a_src, a_dst, scr_vals, y_target, vis, hold, hold_mask, n, device,
                                             seed + 999)

    # C ceiling
    pred_C = _neighbour_true_mean(A, y_target)[hold]

    def _strat(pred):
        out = {}
        for si, sn in enumerate(STRATA):
            mk = strata == si; nn = int(mk.sum())
            out[sn] = dict(spear=(_spearman(pred[mk], yh[mk]) if nn >= 3 else float("nan")), n=nn)
        return out

    scores = {F_TRIV: 0.0, F_A: _spearman(pred_FA, yh), A_SINGLE: _spearman(pred_single, yh),
              A_FUSED: _spearman(pred_fused, yh), A_FUSED_RED: _spearman(pred_red, yh),
              A_FUSED_SCR: _spearman(pred_scr, yh), C_CEIL: _spearman(pred_C, yh)}
    strat = {F_A: _strat(pred_FA), A_FUSED: _strat(pred_fused)}
    sigs = {}
    for nm, pr in ((F_A, pred_FA), (A_SINGLE, pred_single), (A_FUSED, pred_fused), (A_FUSED_RED, pred_red),
                   (A_FUSED_SCR, pred_scr), (C_CEIL, pred_C)):
        sigs[nm] = hashlib.sha256(np.round(pr[:64].astype(np.float64), 5).tobytes()).hexdigest()

    ground_gap = scores[A_FUSED] - scores[F_A]
    for arm in ALL_ARMS:
        _log("  seed=%d %-22s spearman=%s" % (seed, arm, _fmt(scores[arm])))
    _log("  seed=%d fused_gap(A+F - F_A)=%s  fusion_beats_single=%s  redundant_gap=%s  scrambled_gap=%s  w_fused=%s"
         % (seed, _fmt(ground_gap), _fmt(scores[A_FUSED] - scores[A_SINGLE]),
            _fmt(scores[A_FUSED_RED] - scores[A_SINGLE]), _fmt(scores[A_FUSED_SCR] - scores[F_A]),
            "[" + ",".join("%.2f" % x for x in w_fused) + "]"))
    for sn in STRATA:
        _log("    seed=%d stratum %-4s F_A=%s A+F=%s gap=%s [n=%d]"
             % (seed, sn, _fmt(strat[F_A][sn]["spear"]), _fmt(strat[A_FUSED][sn]["spear"]),
                _fmt(strat[A_FUSED][sn]["spear"] - strat[F_A][sn]["spear"]), strat[A_FUSED][sn]["n"]))

    return dict(seed=seed, scores=scores, strat=strat, arm_sigs=sigs, ground_gap=ground_gap,
                weights=[float(x) for x in w_fused], cons_eff_rank=cons_eff_rank, cons_rep_var=cons_rep_var,
                n=int(n), n_hold=int(nh))


# ---------------------------------------------------------------------------
# Fairness + independence pre-flight.
# ---------------------------------------------------------------------------

def fairness_preflight(tri, Y, deg, A, device, seeds):
    n = Y.shape[0]; y_target = Y[:, 0]
    fs = eng.structural_features(tri, n, DIM, 7, device)
    attr_full = torch.from_numpy(((y_target - y_target.mean()) / (y_target.std() + 1e-9)).astype(np.float32)
                                 ).to(device)[:, None].repeat(1, DIM)
    pf = eng.channel_preflight(fs, attr_full, deg, 7, device)
    a_src, a_dst = eng.agreement_edges(fs, fs, eng.CONS_KNN, device)
    fa_l = []; c_l = []
    for s in seeds:
        rng = np.random.default_rng(s * 100003 + 17); perm = rng.permutation(n); nh = int(HELDOUT_FRAC * n)
        hold = perm[:nh]; vis = perm[nh:]
        E_A = eng.consolidate(a_src, a_dst, fs, n, eng.CONS_PASSES, eng.CONS_ALPHA, device, "")
        fa_l.append(_spearman(_ridge_predict(E_A.cpu().numpy(), y_target, vis, hold), y_target[hold]))
        c_l.append(_spearman(_neighbour_true_mean(A, y_target)[hold], y_target[hold]))
    F_triv = 0.0; F_A_v = float(np.nanmean(fa_l)); C_v = float(np.nanmean(c_l))
    fair_floor_ok = bool(F_A_v - F_triv >= FAIR_FLOOR_GAP)
    fair_headroom_ok = bool(C_v - F_A_v >= FAIR_HEADROOM)
    return dict(F_triv=F_triv, F_A=F_A_v, C=C_v, fair_floor_ok=fair_floor_ok, fair_headroom_ok=fair_headroom_ok,
                fairness_ok=bool(fair_floor_ok and fair_headroom_ok),
                channel_preflight=dict(cross_sim_r=pf["cross_sim_r"], struct_deg_r=pf["struct_deg_r"],
                                       attr_deg_r=pf["lex_deg_r"]))


# ---------------------------------------------------------------------------
# Aggregate + verdict.
# ---------------------------------------------------------------------------

def _nm(v):
    a = np.array([x for x in v if x == x], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def aggregate_and_verdict(per_seed, fair, sel_info, meta):
    def S(arm):
        return _nm([m["scores"][arm] for m in per_seed])
    gaps = np.array([m["ground_gap"] for m in per_seed if m["ground_gap"] == m["ground_gap"]], dtype=np.float64)
    fa = S(F_A); single = S(A_SINGLE); fused = S(A_FUSED); red = S(A_FUSED_RED); scr = S(A_FUSED_SCR); cc = S(C_CEIL)
    ftriv = S(F_TRIV)
    ground_gap = _nm([m["ground_gap"] for m in per_seed])
    cv = float(gaps.std() / abs(gaps.mean())) if gaps.shape[0] > 0 and abs(gaps.mean()) > 1e-9 else float("inf")
    # leave-one-seed-out means
    loso = []
    if gaps.shape[0] >= 2:
        for i in range(gaps.shape[0]):
            loso.append(float(np.delete(gaps, i).mean()))
    loso_min = float(min(loso)) if loso else float("nan")
    fusion_beats_single = fused - single if (fused == fused and single == single) else float("nan")
    redundant_gap = red - single if (red == red and single == single) else float("nan")
    scrambled_gap = scr - fa if (scr == scr and fa == fa) else float("nan")

    cons_eff_rank = _nm([m["cons_eff_rank"] for m in per_seed])
    cons_rep_var = _nm([m["cons_rep_var"] for m in per_seed])

    strat = {}
    for sn in STRATA:
        fa_s = _nm([m["strat"][F_A][sn]["spear"] for m in per_seed])
        af_s = _nm([m["strat"][A_FUSED][sn]["spear"] for m in per_seed])
        ns = int(_nm([m["strat"][A_FUSED][sn]["n"] for m in per_seed]))
        strat[sn] = dict(fa=fa_s, af=af_s, gap=(af_s - fa_s) if (af_s == af_s and fa_s == fa_s) else float("nan"), n=ns)
    high_gap = strat["HIGH"]["gap"]

    fairness_ok = bool(fair["fairness_ok"])
    channels_independent = bool(sel_info["n_selected"] >= 2)
    collapsed = bool((cons_eff_rank == cons_eff_rank and cons_eff_rank <= eng.COLLAPSE_RANK_FLOOR)
                     or (cons_rep_var == cons_rep_var and cons_rep_var <= eng.COLLAPSE_VAR_FLOOR))

    # promotion-criterion sub-gates
    g_material = bool(ground_gap == ground_gap and ground_gap >= GROUND_MARGIN)
    g_cv = bool(cv == cv and cv < CV_MAX)
    g_loso = bool(loso_min == loso_min and loso_min >= GROUND_MARGIN) if loso else False
    g_high = bool(high_gap == high_gap and high_gap >= HIGH_NONNEG)
    g_beats = bool(fusion_beats_single == fusion_beats_single and fusion_beats_single >= FUSION_BEAT)
    g_redundant = bool(redundant_gap == redundant_gap and redundant_gap <= REDUNDANT_MAX)
    g_scramble = bool(scrambled_gap == scrambled_gap and scrambled_gap <= SCRAMBLE_MAX)

    promotion = bool(fairness_ok and channels_independent and not collapsed and g_material and g_cv and g_loso
                     and g_high and g_beats and g_redundant and g_scramble)

    # hard-fail conditions
    ties_single = bool(fusion_beats_single == fusion_beats_single and fusion_beats_single <= TIE_EPS)
    fragile = bool((cv == cv and cv >= CV_FAIL) or (loso and loso_min == loso_min and loso_min < GROUND_MARGIN and cv >= CV_MAX))
    high_washes = bool(high_gap == high_gap and high_gap < HIGH_NONNEG)
    redundancy_cheat = bool(redundant_gap == redundant_gap and redundant_gap >= FUSION_BEAT)
    scramble_grounds = bool(scrambled_gap == scrambled_gap and scrambled_gap >= GROUND_MARGIN)
    not_robust = bool(ties_single or fragile or high_washes)

    if not fairness_ok:
        verdict = "HARD_FAIL_FAIRNESS_BLOCKED"
    elif not channels_independent:
        verdict = "HARD_FAIL_CHANNELS_NOT_INDEPENDENT"
    elif collapsed:
        verdict = "HARD_FAIL_CONSOLIDATION_COLLAPSED"
    elif redundancy_cheat or scramble_grounds:
        verdict = "HARD_FAIL_REDUNDANCY_CHEAT"
    elif promotion:
        verdict = "HARD_PASS_FUSION_ROBUST"
    elif not_robust:
        verdict = "HARD_FAIL_FUSION_NOT_ROBUST"
    else:
        verdict = "MIDDLE_BAND_PARTIAL"

    verdict_msg = (
        "%s || SPEARMAN: F_triv=%.3f F_A=%.3f single=%.3f FUSED=%.3f redundant=%.3f scrambled=%.3f C=%.3f || "
        "fused_gap(FUSED-F_A)=%s cv=%s loso_min=%s | fusion_beats_single=%s redundant_gap=%s scrambled_gap=%s || "
        "STRATA fused_gap[n]: LOW=%s[%d] MID=%s[%d] HIGH=%s[%d] || "
        "selected=%s (n=%d) || fairness F_triv<F_A<C ok=%s | collapse eff_rank=%.1f rep_var=%.3f collapsed=%s || "
        "GATES material(>=%.2f)=%s cv(<%.2f)=%s loso(>=%.2f)=%s high_nonneg=%s beats_single(>=%.2f)=%s "
        "redundant_ok(<=%.2f)=%s scramble_ok(<=%.2f)=%s || PROMOTION=%s || coverage_conc=%.1f%% n=%d edges=%d seeds=%d "
        "run=%s" % (
            verdict, ftriv, fa, single, fused, red, scr, cc,
            _fmt(ground_gap), _fmt(cv), _fmt(loso_min), _fmt(fusion_beats_single), _fmt(redundant_gap),
            _fmt(scrambled_gap), _fmt(strat["LOW"]["gap"]), strat["LOW"]["n"], _fmt(strat["MID"]["gap"]),
            strat["MID"]["n"], _fmt(strat["HIGH"]["gap"]), strat["HIGH"]["n"],
            ",".join(sel_info["selected"]), sel_info["n_selected"], fairness_ok, cons_eff_rank, cons_rep_var, collapsed,
            GROUND_MARGIN, g_material, CV_MAX, g_cv, GROUND_MARGIN, g_loso, g_high, FUSION_BEAT, g_beats,
            REDUNDANT_MAX, g_redundant, SCRAMBLE_MAX, g_scramble, promotion,
            100.0 * meta.get("coverage_frac_concreteness", float("nan")), meta.get("n_covered_connected", -1),
            meta.get("n_edges", -1), len(per_seed), "full" if len(per_seed) >= 5 else "smoke"))

    gates = dict(
        verdict=verdict,
        scores=dict(F_triv=ftriv, F_A=fa, single=single, fused=fused, redundant=red, scrambled=scr, C=cc),
        ground_gap=ground_gap, cv=cv, loso_means=loso, loso_min=loso_min,
        fusion_beats_single=fusion_beats_single, redundant_gap=redundant_gap, scrambled_gap=scrambled_gap,
        strata=strat, high_gap=high_gap, per_seed_gaps=[float(x) for x in gaps],
        fairness=dict(F_triv=fair["F_triv"], F_A=fair["F_A"], C=fair["C"], fairness_ok=fairness_ok),
        collapse=dict(cons_eff_rank=cons_eff_rank, cons_rep_var=cons_rep_var, collapsed=collapsed),
        independence=sel_info,
        subgates=dict(material=g_material, cv_ok=g_cv, loso_ok=g_loso, high_nonneg=g_high, beats_single=g_beats,
                      redundant_ok=g_redundant, scramble_ok=g_scramble, promotion=promotion,
                      ties_single=ties_single, fragile=fragile, high_washes=high_washes,
                      redundancy_cheat=redundancy_cheat, scramble_grounds=scramble_grounds),
        bands=dict(GROUND_MARGIN=GROUND_MARGIN, CV_MAX=CV_MAX, CV_FAIL=CV_FAIL, HIGH_NONNEG=HIGH_NONNEG,
                   FUSION_BEAT=FUSION_BEAT, REDUNDANT_MAX=REDUNDANT_MAX, SCRAMBLE_MAX=SCRAMBLE_MAX,
                   FAIR_FLOOR_GAP=FAIR_FLOOR_GAP, FAIR_HEADROOM=FAIR_HEADROOM, MIN_STRAT_Q=MIN_STRAT_Q,
                   REDUNDANT_R=REDUNDANT_R, MIN_TARGET_R=MIN_TARGET_R))
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Coverage-density diagnostic (logged BEFORE the fusion verdict).
# ---------------------------------------------------------------------------

def coverage_density_diagnostic(tri, Y, deg, A, device, seeds):
    n = Y.shape[0]; y = Y[:, 0]
    lifts = []; degs = []; visnbr = []
    for seed in seeds:
        rng = np.random.default_rng(seed * 100003 + 17); perm = rng.permutation(n); nh = int(HELDOUT_FRAC * n)
        hold = perm[:nh]; vis = perm[nh:]; hold_mask = np.zeros(n, dtype=bool); hold_mask[hold] = True
        fs = eng.structural_features(tri, n, DIM, seed, device)
        a_src, a_dst = eng.agreement_edges(fs, fs, eng.CONS_KNN, device)
        E_A = eng.consolidate(a_src, a_dst, fs, n, eng.CONS_PASSES, eng.CONS_ALPHA, device, "")
        pred_FA = _ridge_predict(E_A.cpu().numpy(), y, vis, hold)
        obs = (~hold_mask) & np.isfinite(y)
        pred_AB, _E = _channel_pred(fs, a_src, a_dst, y, None, y, obs, vis, hold, n, device)
        yh = y[hold]
        lift = np.abs(pred_FA - yh) - np.abs(pred_AB - yh)
        nbr_vis = (A[hold][:, (~hold_mask)] > 0).sum(axis=1)
        lifts.append(lift); degs.append(deg[hold]); visnbr.append(nbr_vis)
    lift = np.concatenate(lifts); dg = np.concatenate(degs); vn = np.concatenate(visnbr)
    r_deg = _spearman(lift, dg); r_vn = _spearman(lift, vn)
    med = np.median(dg)
    lo = float(lift[dg <= med].mean()); hi = float(lift[dg > med].mean())
    diag = dict(mean_lift=float(lift.mean()), frac_helped=float((lift > 0).mean()),
                spearman_lift_vs_degree=r_deg, spearman_lift_vs_visible_neighbours=r_vn,
                mean_lift_low_degree=lo, mean_lift_high_degree=hi, delta_hi_lo=hi - lo,
                interpretation=("coverage_limited" if (r_deg > 0.10) else
                                "channel_limited_low_mid_ceiling_limited_high"))
    _log("COVERAGE-DENSITY DIAG: mean_lift=%.4f frac_helped=%.3f | r(lift,deg)=%+.4f r(lift,vis_nbr)=%+.4f | "
         "mean_lift LOW-deg=%.4f HIGH-deg=%.4f (delta=%+.4f) -> %s"
         % (diag["mean_lift"], diag["frac_helped"], r_deg, r_vn, lo, hi, diag["delta_hi_lo"], diag["interpretation"]))
    return diag


# ---------------------------------------------------------------------------
# Mechanism self-test (planted worlds; discriminators must FIRE).
# ---------------------------------------------------------------------------

def _planted_multiattr_world(side, per_cell, seed, noise, mode):
    """Clustered graph + latent target; K attribute channels. mode='independent' -> each channel = latent + INDEP noise;
    mode='redundant' -> each channel = latent + SHARED noise (no new sense); mode='unpredictable' -> target is graph-
    independent pure noise (fairness must BLOCK)."""
    rng = np.random.default_rng(seed); K = side * side
    ncl = np.array([2 + int(rng.integers(0, per_cell)) for _ in range(K)])
    ent = np.repeat(np.arange(K), ncl); n = int(ent.shape[0])
    cc = (np.arange(K) // side + np.arange(K) % side).astype(np.float64)
    members = [np.where(ent == c)[0] for c in range(K)]
    Amat = np.zeros((n, n), dtype=np.float32)
    for c in range(K):
        mm = members[c]
        for a in mm:
            for b in mm:
                if a != b:
                    Amat[a, b] = 1.0
    for c in range(K - 1):
        for a in members[c][:1]:
            for b in members[c + 1][:1]:
                Amat[a, b] = 1.0; Amat[b, a] = 1.0
    if mode == "unpredictable":
        latent = rng.standard_normal(n)               # graph-independent -> fairness must BLOCK
    else:
        latent = cc[ent] + 0.3 * cc.std() * rng.standard_normal(n)   # mostly graph-smooth + some idiosyncrasy (headroom)
    latent = (latent - latent.mean()) / (latent.std() + 1e-9)        # unit variance so channel noise sets mutual r
    ncand = 5
    Y = np.zeros((n, ncand + 1), dtype=np.float64)
    shared = rng.standard_normal(n)
    # ALL channels (including concreteness Y[:,0]) are NOISY unit-latent measurements; the latent is the prediction
    # target (override). INDEP noise (std 1.0) -> mutual r ~ 0.5 (< the 0.70 gate) -> genuine senses that compound;
    # SHARED noise -> mutual r ~ 0.98 (>= gate) -> pruned, and the redundant arm cannot beat single.
    for j in range(ncand + 1):
        if mode == "redundant":
            Y[:, j] = latent + 0.15 * shared
        else:
            Y[:, j] = latent + 1.0 * rng.standard_normal(n)
    present = np.ones_like(Y, dtype=bool)
    ij = np.argwhere(Amat > 0)
    tri = np.stack([ij[:, 0], np.zeros(ij.shape[0], dtype=np.int64), ij[:, 1]], axis=1).astype(np.int64)
    return tri, Y, present, Amat.sum(1), Amat, latent


def _mechanism_selftest(device):
    attr_names = ["concreteness"] + ["c%d" % j for j in range(5)]
    # (a) INDEPENDENT world: fusion of genuine independent channels BEATS single (target = hidden latent).
    tri, Y, present, deg, A, latent = _planted_multiattr_world(16, 4, 0, noise=1.0, mode="independent")
    sel_i, info_i = independence_select(Y, present, attr_names, latent)
    sel_idx_i = [attr_names.index(s) for s in sel_i]
    ps_i = run_seed(7, tri, Y, present, deg, A, sel_idx_i, device, y_target_override=latent)
    fused_beats = ps_i["scores"][A_FUSED] - ps_i["scores"][A_SINGLE]
    ground_i = ps_i["scores"][A_FUSED] - ps_i["scores"][F_A]
    scr_i = ps_i["scores"][A_FUSED_SCR] - ps_i["scores"][F_A]
    a_compound = bool(fused_beats >= 0.02 and ground_i >= 0.05)
    a_indep_selects = bool(info_i["n_selected"] >= 2)
    c_scr_no_ground = bool(scr_i == scr_i and scr_i <= 0.02)

    # (b) REDUNDANT world: near-duplicate channels do NOT beat single + independence gate PRUNES the extras.
    tri_r, Y_r, present_r, deg_r, A_r, latent_r = _planted_multiattr_world(16, 4, 1, noise=1.0, mode="redundant")
    sel_r, info_r = independence_select(Y_r, present_r, attr_names, latent_r)
    sel_idx_r = [attr_names.index(s) for s in sel_r]
    ps_r = run_seed(7, tri_r, Y_r, present_r, deg_r, A_r, sel_idx_r if len(sel_idx_r) >= 2 else [0, 1], device,
                    y_target_override=latent_r)
    redundant_beats = ps_r["scores"][A_FUSED_RED] - ps_r["scores"][A_SINGLE]
    b_redundant_no_beat = bool(redundant_beats == redundant_beats and redundant_beats <= 0.02)
    b_gate_prunes = bool(info_r["n_selected"] <= 2)   # near-duplicate world: gate prunes the redundant extras

    # (c) fairness gate: headroom world passes; unpredictable world blocks.
    fair_head = fairness_preflight(tri, Y, deg, A, device, seeds=(7,))
    tri_u, Y_u, present_u, deg_u, A_u, _lu = _planted_multiattr_world(16, 4, 0, noise=1.0, mode="unpredictable")
    fair_u = fairness_preflight(tri_u, Y_u, deg_u, A_u, device, seeds=(7,))
    c_headroom_passes = bool(fair_head["fairness_ok"])
    c_commoncause_blocks = bool(not fair_u["fairness_ok"])

    # (d) collapse discriminator.
    ncol = Y.shape[0]
    collapsed = torch.ones(ncol, DIM, device=device) + 1e-4 * eng._noise_feat(ncol, DIM, 3, device)
    d_collapse_caught = bool(eng._rep_variance(collapsed) <= eng.COLLAPSE_VAR_FLOOR
                             and ps_i["cons_rep_var"] > eng.COLLAPSE_VAR_FLOOR)

    arms_differ = bool(len(set(ps_i["arm_sigs"].values())) >= 6)
    res = dict(a_fused_beats_single=round(fused_beats, 4), a_ground_gap=round(ground_i, 4),
               a_scr_gap=round(scr_i, 4), a_n_selected=info_i["n_selected"],
               b_redundant_beats_single=round(redundant_beats, 4), b_n_selected=info_r["n_selected"],
               c_head_FA=round(fair_head["F_A"], 4), c_head_C=round(fair_head["C"], 4),
               c_unpred_FA=round(fair_u["F_A"], 4), c_unpred_C=round(fair_u["C"], 4),
               d_healthy_repvar=round(ps_i["cons_rep_var"], 4),
               a_compound=a_compound, a_indep_selects=a_indep_selects, c_scr_no_ground=c_scr_no_ground,
               b_redundant_no_beat=b_redundant_no_beat, b_gate_prunes=b_gate_prunes,
               c_headroom_passes=c_headroom_passes, c_commoncause_blocks=c_commoncause_blocks,
               d_collapse_caught=d_collapse_caught, arms_differ=arms_differ)
    ok = bool(a_compound and a_indep_selects and c_scr_no_ground and b_redundant_no_beat and b_gate_prunes
              and c_headroom_passes and c_commoncause_blocks and d_collapse_caught and arms_differ)
    return ok, res


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
    device = torch.device("cpu") if args.device == "cpu" else torch.device(
        "cuda" if ((args.device in ("auto", "cuda")) and torch.cuda.is_available()) else "cpu")

    output_dir = str(get_output_dir(ANCHOR_NAME))
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    expected_n_units = len(cfg["seeds"])
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t0 = time.perf_counter()
    _log("device=%s run_mode=%s" % (device, run_mode))

    st_ok, st_res = _mechanism_selftest(device)
    _log("mechanism_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (compound / redundant-no-beat / independence-select / scramble / "
                        "fairness / collapse discriminators did not fire): %s" % st_res,
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t0, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS fusion: (a) independent channels COMPOUND (fused beats single); (b) redundant "
                        "near-duplicates do NOT beat single + gate prunes; (c) scrambled does not ground; fairness "
                        "gate passes headroom + blocks unpredictable; (d) collapse caught; arms differ",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t0, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t0))
        return

    for key in DATASETS:
        if not _ensure_dataset(key):
            write_metrics(get_output_dir(ANCHOR_NAME), dict(
                verdict="HARD_FAIL_DATA_MISSING", run_mode=run_mode,
                verdict_msg="testbed dataset %r absent + self-acquire failed on runner: %s (see data/grounding_testbed/"
                            "PROVENANCE_multiattribute.md; stage the file or check runner network)" % (key,
                            DATASETS[key]["path"]),
                summary="testbed data missing", elapsed_s=time.perf_counter() - t0))
            raise SystemExit(1)

    _log("building multi-attribute x ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    tri, Y, present, deg, A, attr_names, meta = build_multiattr_subgraph(cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    _log("coverage(concreteness)=%.1f%% | n=%d edges=%d deg[min/med/max]=%.0f/%.0f/%.0f" % (
        100 * meta["coverage_frac_concreteness"], meta["n_covered_connected"], meta["n_edges"],
        meta["deg_min"], meta["deg_med"], meta["deg_max"]))
    _log("attr coverage: %s" % {k: round(v, 3) for k, v in meta["attr_coverage"].items()})

    # INDEPENDENCE GATE (Guardrail 1): full correlation matrix + marginal-correlation pruning.
    sel, sel_info = independence_select(Y, present, attr_names, Y[:, 0])
    _log("INDEPENDENCE MATRIX (|r| rows=%s):" % attr_names)
    for i, row in enumerate(sel_info["corr_matrix"]):
        _log("  %-14s %s" % (attr_names[i], " ".join("%+.2f" % v for v in row)))
    _log("SELECTED (non-redundant, incremental-validity): %s (n=%d)" % (sel, sel_info["n_selected"]))
    for a in sel_info["selection_audit"]:
        _log("  cand=%-14s r_target=%+.3f max_r_sel=%.3f incr_r2=%.4f target_ok=%s redundant=%s SELECTED=%s"
             % (a["attr"], a["r_target"], a["max_r_selected"], a["incr_r2"], a["target_ok"], a["redundant"],
                a["selected"]))
    sel_idx = [attr_names.index(s) for s in sel]

    # COVERAGE-DENSITY DIAGNOSTIC (cheap; logged BEFORE the fusion verdict).
    cov_diag = coverage_density_diagnostic(tri, Y, deg, A, device, cfg["seeds"][:3])

    # FAIRNESS pre-flight.
    fair = fairness_preflight(tri, Y, deg, A, device, tuple(cfg["seeds"][:3]))
    _log("FAIRNESS GATE: F_triv=%.3f < F_A=%.3f < C=%.3f | floor_ok=%s headroom_ok=%s fairness_ok=%s"
         % (fair["F_triv"], fair["F_A"], fair["C"], fair["fair_floor_ok"], fair["fair_headroom_ok"], fair["fairness_ok"]))

    out_dir = get_output_dir(ANCHOR_NAME)
    channels_independent = bool(sel_info["n_selected"] >= 2)
    per_seed = []; seed_failures = []
    if fair["fairness_ok"] and channels_independent:
        for seed in cfg["seeds"]:
            try:
                pm = run_seed(seed, tri, Y, present, deg, A, sel_idx, device)
                if len(set(pm["arm_sigs"].values())) < 6:
                    raise RuntimeError("ARMS_MUST_DIFFER seed=%d only %d distinct sigs" % (seed,
                                       len(set(pm["arm_sigs"].values()))))
                per_seed.append(pm); write_partial(out_dir, seed, dict(seed=seed, metrics=pm))
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as e:
                seed_failures.append(dict(seed=seed, failure_class=type(e).__name__, msg=str(e)[:300]))
                _log("SEED_FAILED seed=%d class=%s: %s" % (seed, type(e).__name__, str(e)[:200]))
        if len(per_seed) < expected_n_units:
            write_metrics(out_dir, dict(
                verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
                verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
                summary="cardinality breach", elapsed_s=time.perf_counter() - t0, seed_failures=seed_failures,
                fairness=fair, independence=sel_info, subgraph_meta=meta, coverage_density=cov_diag))
            raise SystemExit(1)

    if not per_seed:
        verdict = "HARD_FAIL_FAIRNESS_BLOCKED" if not fair["fairness_ok"] else "HARD_FAIL_CHANNELS_NOT_INDEPENDENT"
        vmsg = ("%s || FAIRNESS F_triv=%.3f F_A=%.3f C=%.3f ok=%s || independence selected=%s n=%d || coverage=%.1f%% "
                "n=%d" % (verdict, fair["F_triv"], fair["F_A"], fair["C"], fair["fairness_ok"], sel_info["selected"],
                          sel_info["n_selected"], 100 * meta["coverage_frac_concreteness"],
                          meta["n_covered_connected"]))
        write_metrics(out_dir, dict(verdict=verdict, verdict_msg=vmsg, summary=vmsg[:200], run_mode=run_mode,
                                    elapsed_s=time.perf_counter() - t0, anchor_name=ANCHOR_NAME,
                                    ts_iso=datetime.now(timezone.utc).isoformat(), fairness=fair,
                                    independence=sel_info, subgraph_meta=meta, coverage_density=cov_diag,
                                    mechanism_selftest=st_res))
        _log("VERDICT: %s" % vmsg)
        return

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, fair, sel_info, meta)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t0, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=cfg["seeds"], config=dict(seeds=cfg["seeds"], n_nodes=cfg["n_nodes"], dim=DIM),
                   subgraph_meta=meta, gates=gates, fairness=fair, independence=sel_info, coverage_density=cov_diag,
                   mechanism_selftest=st_res, seed_failures=seed_failures, per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t0))


if __name__ == "__main__":
    _od = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
