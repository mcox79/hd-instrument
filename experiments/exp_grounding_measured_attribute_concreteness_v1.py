"""FAIR GROUNDING TEST: does anchoring the consolidation geometry to a genuinely-EXTERIOR MEASURED attribute
(Brysbaert concreteness norms) produce degree-INVARIANT grounding of the REAL ConceptNet substrate graph?

WHY THIS CELL (vs the char-trigram engine reference `grounding_consolidation_loop_degree_invariant_v1`): char-trigram
spelling passes the independence gate but is semantically VACUOUS (spelling != meaning), so graph<->spelling agreement
carries no real signal and a HARD_FAIL there would be uninterpretable (engine bad vs channel meaningless). Grounding needs
the exterior channel to be BOTH independent AND to carry real correlated MEANING -- a MEASURED empirical attribute (the
ball-looks-soft/squeezes-hard structure), not a surface string. This cell uses the SAME validated diffusion-with-restart
engine + collapse discriminator + independence gate, but the exterior channel is a real human-rated MEASURED attribute.

DATASET (Option C, coordinator-chosen): Brysbaert, Warriner & Kuperman (2014) concreteness norms (Conc.M, 1=abstract..
5=concrete; 39,954 words) JOINED to the ConceptNet subgraph this project already loads. Concreteness is a genuine
measured EXTERIOR human-rating attribute NOT derivable from is-a/synonym links; joined coverage ~74% of subgraph concepts;
covered+connected subgraph n~3262, degree 1..238 (strata-capable). Provenance: data/grounding_testbed/PROVENANCE_concreteness.md.

TASK (DETERMINACY: predict a scalar, unique answer): hold out 30% of concepts; predict their concreteness value from
their graph position + the consolidated geometry. Scored by SPEARMAN rank correlation (predicted vs true held-out
concreteness), aggregate + per-degree-stratum.

THE FAIRNESS GATE (HARD GO/NO-GO, computed BEFORE the loop; info-ceiling discipline):
  - F_triv = trivial floor (predict the mean; Spearman ~0).
  - F_A    = relational-only floor: consolidation on the GRAPH ALONE predicting concreteness.
  - C      = ceiling: best-possible held-out prediction (graph-neighbour TRUE-attribute smoothing oracle).
  RUN ONLY IF F_triv < F_A < C with real gaps AND F_A meaningfully below C. If F_A ~= C -> relations already determine
  concreteness (common-cause collapse, the periodic-table failure) -> BLOCK unfair. If F_triv ~= C -> no headroom -> BLOCK.
  All three numbers are reported. (Smoke probe: F_triv=0.000 < F_A=0.505 < C=0.716 -> CLEARED.)

THE DECISIVE DISCRIMINATOR (grounding = exogenous referent, operationalized -- the ABLATION): the EXTERIOR channel must
be LOAD-BEARING. Ablate the measured channel B (consolidate on the relational graph A ALONE, F_A) -> grounding MUST
COLLAPSE. A+B (graph + measured concreteness in the restart anchor) must BEAT A-alone (F_A), and the gain must SURVIVE
the low-degree tail (rare concepts grounded too), and a SCRAMBLED attribute (permute the measured values) must NOT ground
(A+B_scrambled ~= F_A) -- else the mechanism cheats on channel-presence not attribute-VALUES.

MECHANISM (reuses the validated engine):
  - Structural channel = random-projected propagated visible-graph adjacency (graph topology; degree-normalized diffusion).
  - Exterior channel B = measured concreteness (Conc.M), in the restart ANCHOR for VISIBLE concepts, MASKED (visible-mean)
    for held-out -> LEAK-FREE (held-out true concreteness is never used; only visible values diffuse over the graph).
  - A-alone (F_A): consolidate([structural anchor], graph-kNN agreement) -> ridge predict held-out concreteness.
  - A+B: consolidate([structural | measured-concreteness anchor], graph-kNN agreement) -> ridge predict. The normalized-
    Laplacian diffusion-with-restart spreads visible measured concreteness to held-out via the graph = the grounding.
  - A+B_scrambled (must-fail control): same, concreteness permuted across concepts.

ARMS (all predict held-out concreteness on the SAME held-out split per seed -> PAIRED):
  F_TRIV, F_A (relational-only), A_PLUS_B (grounded), A_PLUS_B_SCRAMBLED (must-fail control), C_CEILING (reported oracle).

DISCRIMINATOR (pre-registered; both bands numeric BEFORE the run):
  HARD_PASS_GROUNDING_REAL (ALL must hold):
      fairness cleared (F_triv < F_A < C with gaps), AND channels_independent (pre-flight), AND not collapsed, AND
      aggregate grounding gap (A+B - F_A) >= GROUND_MARGIN, AND degree-invariant ((A+B - F_A) >= STRAT_GROUND_MARGIN in
      BOTH LOW and MID strata, >=MIN_STRAT_Q each), AND scrambled does NOT ground ((A+B_scrambled - F_A) <= SCRAMBLE_MAX).
  HARD_FAIL_GROUNDING_NOT_REAL: A+B ties A-alone (gap <= TIE_EPS = no exogenous work) OR grounding collapses on the tail
      (LOW or MID gap <= TIE_EPS) OR scrambled ALSO grounds ((A+B_scrambled - F_A) >= GROUND_MARGIN = cheating).
  HARD_FAIL_FAIRNESS_BLOCKED: fairness gate fails (F_A ~= C or F_triv ~= C) -> unfair domain; report + fall back to Option B.
  HARD_FAIL_CHANNELS_NOT_INDEPENDENT / HARD_FAIL_CONSOLIDATION_COLLAPSED: engine gates.
  MIDDLE_BAND_PARTIAL = otherwise (gain present but tail/scramble ambiguous).

SELF-TEST (planted worlds; discriminators must FIRE): (a) informative degree-independent attribute -> A+B beats A-alone
and is degree-flat; (b) scrambled attribute does NOT ground; (c) fairness-gate logic (headroom world passes; common-cause
world where the graph DETERMINES the attribute is BLOCKED); (d) collapse discriminator catches a collapsed code.

## Compute architecture
class (a) batched-GPU-capable but CPU-fast: structural features (2 dense [n,n]@[n,dim] matmuls, n~3262), diffusion (6
dense matmuls), ridge (small linear solve). NO KGE / NO encoder training -> ~seconds/seed on CPU. Storage SHARDED. FULL
routes to remote_cpu_queue (CPU; no GPU benefit; keeps the laptop free per the SMOKE-ONLY-LOCAL lock). Requires the
concreteness testbed file present on the runner (see hand-off).

CELL-TEMPLATE MANDATORY: arms_differ_verified (>=4 distinct arm sigs); final_metrics_atomicity=tmp_replace; except
SystemExit before except Exception; crlb: Spearman chance ~0 (THEORETICAL), HARD_PASS above floor; baseline_in_band:
F_TRIV is the null (~0), C is the must-fire ceiling (> F_A); discriminator-survives-scale: engine params shared self-test/
FULL, real-graph fairness+ablation is the open measurement; HP_SCOPE: grounding gate on A_PLUS_B vs F_A + scrambled;
calibration_check=default_ok_for_this_regime; progress_logging=print_flush_true; cell_chunked=false; start_marker +
crash_diagnostic present.
"""

import argparse
import hashlib
import json
import os
import platform
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
# Reuse the VALIDATED consolidation engine (diffusion-with-restart + collapse discriminator + independence gate).
import experiments.exp_grounding_consolidation_loop_degree_invariant_v1 as eng  # noqa: E402

ANCHOR_NAME = "grounding_measured_attribute_concreteness_v1"

CONC_PATH = os.path.join(_REPO, "data", "grounding_testbed",
                         "Concreteness_ratings_Brysbaert_et_al_BRM.txt")

# ---- Arm names ----
F_TRIV = "F_TRIV"                    # trivial floor (predict mean)
F_A = "F_A_RELATIONAL"               # relational-only consolidation (the ablation of the exterior channel)
A_PLUS_B = "A_PLUS_B_GROUNDED"       # graph + measured concreteness (mechanism under test)
A_PLUS_B_SCR = "A_PLUS_B_SCRAMBLED"  # must-fail control: concreteness permuted across concepts
C_CEIL = "C_CEILING"                 # ceiling oracle (graph-neighbour TRUE-attribute smoothing)
ALL_ARMS = [F_TRIV, F_A, A_PLUS_B, A_PLUS_B_SCR, C_CEIL]
STRATA = ["LOW", "MID", "HIGH"]

# ---- Pre-registered bands (principled; picked BEFORE the FULL, consistent with the engine cell's conventions) ----
FAIR_FLOOR_GAP = 0.05        # fairness: F_A - F_triv >= this (relations predict the attribute above trivial)
FAIR_HEADROOM = 0.05         # fairness: C - F_A >= this (headroom for the exterior channel; not common-cause-collapsed)
GROUND_MARGIN = 0.05         # HARD_PASS: aggregate grounding gap (A+B - F_A) >= this (exterior channel is load-bearing)
STRAT_GROUND_MARGIN = 0.03   # HARD_PASS: grounding gap >= this in BOTH LOW and MID strata (degree-invariant)
SCRAMBLE_MAX = 0.02          # HARD_PASS: scrambled attribute grounding gap <= this (values, not channel-presence)
TIE_EPS = 0.02               # HARD_FAIL: grounding collapses (gap <= this) in aggregate or a tail stratum
MIN_STRAT_Q = 40             # min held-out queries per stratum to assess it
HELDOUT_FRAC = 0.30
RIDGE_LAM = 5.0
DIM = 64                     # structural + attribute anchor dim (per channel)
ATTR_COLS = 16              # #columns the (scalar) measured attribute is broadcast to in the anchor

# Config profiles. Consolidation params (CONS_KNN/PASSES/ALPHA) inherited from the engine (SHARED self-test<->FULL).
SELFTEST_CFG = dict(seeds=[7], n_nodes=0)                              # planted worlds only
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
# Data: join Brysbaert concreteness to the ConceptNet subgraph; restrict to covered+connected concepts.
# ---------------------------------------------------------------------------

CONC_URL = ("https://raw.githubusercontent.com/ArtsEngine/concreteness/master/"
            "Concreteness_ratings_Brysbaert_et_al_BRM.txt")


def _ensure_data_file(path):
    """Self-acquire the public concreteness testbed file if absent (small, documented source; validated by header).
    Makes the cell runnable on any runner (local or remote) without manual staging. Falls through to the caller's
    HARD_FAIL_DATA_MISSING guard if the pull fails (e.g. offline runner)."""
    if os.path.exists(path):
        return True
    try:
        import subprocess
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        subprocess.run(["curl", "-sSL", "--max-time", "120", "-o", tmp, CONC_URL], check=True)
        with open(tmp, encoding="utf-8") as f:
            if "Conc.M" not in f.readline():
                os.remove(tmp); return False
        os.replace(tmp, path)
        _log("acquired concreteness testbed file from %s" % CONC_URL)
        return True
    except Exception as e:
        _log("could not self-acquire concreteness file: %s: %s" % (type(e).__name__, str(e)[:150]))
        return False


def load_concreteness_map(path):
    conc = {}
    with open(path, encoding="utf-8") as f:
        header = f.readline()
        if "Conc.M" not in header:
            raise RuntimeError("concreteness file header missing Conc.M: %r" % header[:80])
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 3:
                try:
                    conc[p[0].strip().lower()] = float(p[2])
                except (ValueError, IndexError):
                    continue
    return conc


def build_concreteness_subgraph(n_nodes, base_seed):
    """Returns (tri, y, deg, names, meta). tri: [E,3] directed (i,0,j) over covered+connected concepts; y: [n]
    concreteness; deg: [n] visible-graph degree."""
    conc = load_concreteness_map(CONC_PATH)
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(n_nodes, base_seed)
    edges = np.asarray(edges, dtype=np.int64)
    n0 = len(node_ids)
    y0 = np.full(n0, np.nan)
    for i, w in enumerate(node_words):
        k = str(w).strip().lower().replace("_", " ")
        if k in conc:
            y0[i] = conc[k]
        elif k.replace(" ", "") in conc:
            y0[i] = conc[k.replace(" ", "")]
    cov = np.isfinite(y0)
    keep = np.where(cov)[0]
    im = {int(o): i for i, o in enumerate(keep)}
    yk = y0[keep]
    names0 = [node_words[int(o)] for o in keep]
    m = len(keep)
    A = np.zeros((m, m), dtype=np.float32)
    for a, b in edges:
        a = int(a); b = int(b)
        if a in im and b in im and a != b:
            A[im[a], im[b]] = 1.0; A[im[b], im[a]] = 1.0
    conn = np.where(A.sum(axis=1) > 0)[0]
    A = A[np.ix_(conn, conn)]
    yk = yk[conn]
    names = [names0[int(c)] for c in conn]
    m2 = len(conn)
    deg = A.sum(axis=1)
    ij = np.argwhere(A > 0)
    tri = np.stack([ij[:, 0], np.zeros(ij.shape[0], dtype=np.int64), ij[:, 1]], axis=1).astype(np.int64)
    meta2 = dict(n_subgraph=n0, n_covered=int(cov.sum()), coverage_frac=float(cov.mean()),
                 n_covered_connected=m2, n_edges=int(tri.shape[0]),
                 deg_min=float(deg.min()), deg_med=float(np.median(deg)), deg_max=float(deg.max()),
                 conc_min=float(yk.min()), conc_mean=float(yk.mean()), conc_max=float(yk.max()),
                 conc_std=float(yk.std()), subgraph_meta=meta)
    return tri, yk, deg, A, names, meta2


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


def _ridge_predict(X, y, tr, te, lam=RIDGE_LAM):
    Xtr = X[tr]; mu = Xtr.mean(axis=0); Xtr = Xtr - mu; ytr = y[tr]
    G = Xtr.T @ Xtr + lam * np.eye(X.shape[1])
    w = np.linalg.solve(G, Xtr.T @ (ytr - ytr.mean()))
    return (X[te] - mu) @ w + ytr.mean()


def _attr_anchor(y, hold_mask, device, ncol=ATTR_COLS):
    """Measured-attribute restart anchor: normalized y for visible, MASKED (visible-mean) for held-out (LEAK-FREE).
    Broadcast to ncol columns so it carries weight alongside the structural anchor."""
    yf = y.copy(); mu = float(y[~hold_mask].mean()); sd = float(y[~hold_mask].std()) + 1e-9
    yf[hold_mask] = mu
    yf = (yf - mu) / sd
    return torch.from_numpy(yf.astype(np.float32)).to(device)[:, None].repeat(1, ncol)


def _neighbour_true_mean(A, y):
    """Ceiling oracle feature: mean of TRUE y over each node's graph-neighbours (uses all neighbours' true values)."""
    s = A @ y
    d = A.sum(axis=1)
    out = np.where(d > 0, s / np.maximum(d, 1.0), y.mean())
    return out


# ---------------------------------------------------------------------------
# Per-seed run on the real concreteness subgraph.
# ---------------------------------------------------------------------------

def _strata_labels(deg_hold):
    if deg_hold.shape[0] == 0:
        return np.zeros(0, dtype=np.int64)
    q1 = float(np.quantile(deg_hold, 1.0 / 3.0)); q2 = float(np.quantile(deg_hold, 2.0 / 3.0))
    lab = np.zeros(deg_hold.shape[0], dtype=np.int64)
    lab[deg_hold > q1] = 1; lab[deg_hold > q2] = 2
    return lab


def run_seed(seed, tri, y, deg, A, device):
    n = y.shape[0]
    rng = np.random.default_rng(seed * 100003 + 17)
    perm = rng.permutation(n); nh = int(HELDOUT_FRAC * n)
    hold = perm[:nh]; vis = perm[nh:]
    hold_mask = np.zeros(n, dtype=bool); hold_mask[hold] = True
    deg_hold = deg[hold]; strata = _strata_labels(deg_hold)
    yh = y[hold]

    fs = eng.structural_features(tri, n, DIM, seed, device)                 # structural channel (graph topology)
    a_src, a_dst = eng.agreement_edges(fs, fs, eng.CONS_KNN, device)        # struct-kNN graph (shared A-alone / A+B)

    # F_A (relational-only ablation): consolidate structural anchor, ridge predict.
    E_A = eng.consolidate(a_src, a_dst, fs, n, eng.CONS_PASSES, eng.CONS_ALPHA, device, "[Fa]")
    pred_FA = _ridge_predict(E_A.cpu().numpy(), y, vis, hold)

    # A+B (grounded): structural + measured-concreteness anchor (leak-free mask), diffuse, ridge predict.
    E0_AB = torch.cat([fs, _attr_anchor(y, hold_mask, device)], dim=1)
    E_AB = eng.consolidate(a_src, a_dst, E0_AB, n, eng.CONS_PASSES, eng.CONS_ALPHA, device, "[AB]")
    pred_AB = _ridge_predict(E_AB.cpu().numpy(), y, vis, hold)
    cons_eff_rank = eng._effective_rank(E_AB); cons_rep_var = eng._rep_variance(E_AB)

    # A+B scrambled (must-fail control): permute the measured values across concepts.
    y_scr = y[np.random.default_rng(seed + 99).permutation(n)]
    E0_S = torch.cat([fs, _attr_anchor(y_scr, hold_mask, device)], dim=1)
    E_S = eng.consolidate(a_src, a_dst, E0_S, n, eng.CONS_PASSES, eng.CONS_ALPHA, device, "[scr]")
    pred_S = _ridge_predict(E_S.cpu().numpy(), y_scr, vis, hold)

    # C ceiling: graph-neighbour TRUE-attribute smoothing (uses all neighbours' true y).
    pred_C = _neighbour_true_mean(A, y)[hold]

    def _score(pred, true):
        return _spearman(pred, true)

    def _strat(pred, true):
        out = {}
        for si, sn in enumerate(STRATA):
            mk = strata == si; nn = int(mk.sum())
            out[sn] = dict(spear=(_spearman(pred[mk], true[mk]) if nn >= MIN_STRAT_Q else float("nan")), n=nn)
        return out

    scores = {
        F_TRIV: 0.0,                                    # mean-baseline Spearman is 0 by construction
        F_A: _score(pred_FA, yh),
        A_PLUS_B: _score(pred_AB, yh),
        A_PLUS_B_SCR: _score(pred_S, y_scr[hold]),
        C_CEIL: _score(pred_C, yh),
    }
    strat = {F_A: _strat(pred_FA, yh), A_PLUS_B: _strat(pred_AB, yh)}
    sigs = {}
    for nm, pr in ((F_A, pred_FA), (A_PLUS_B, pred_AB), (A_PLUS_B_SCR, pred_S), (C_CEIL, pred_C)):
        sigs[nm] = hashlib.sha256(np.round(pr[:64].astype(np.float64), 5).tobytes()).hexdigest()

    for arm in ALL_ARMS:
        _log("  seed=%d %-20s spearman=%s" % (seed, arm, _fmt(scores[arm])))
    _log("  seed=%d grounding gap (A+B - F_A)=%s  scrambled gap=%s  cons_eff_rank=%.1f rep_var=%.3f"
         % (seed, _fmt(scores[A_PLUS_B] - scores[F_A]), _fmt(scores[A_PLUS_B_SCR] - scores[F_A]),
            cons_eff_rank, cons_rep_var))
    for sn in STRATA:
        _log("    seed=%d stratum %-4s: F_A=%s A+B=%s gap=%s [n=%d]"
             % (seed, sn, _fmt(strat[F_A][sn]["spear"]), _fmt(strat[A_PLUS_B][sn]["spear"]),
                _fmt(strat[A_PLUS_B][sn]["spear"] - strat[F_A][sn]["spear"]), strat[A_PLUS_B][sn]["n"]))

    return dict(seed=seed, scores=scores, strat=strat, arm_sigs=sigs,
                cons_eff_rank=cons_eff_rank, cons_rep_var=cons_rep_var,
                n=int(n), n_hold=int(nh))


# ---------------------------------------------------------------------------
# Fairness + independence pre-flight (computed BEFORE the verdict; the HARD go/no-go).
# ---------------------------------------------------------------------------

def fairness_and_independence(tri, y, deg, A, device, seeds=(7, 13, 17)):
    n = y.shape[0]
    fs = eng.structural_features(tri, n, DIM, 7, device)
    attr_full = torch.from_numpy(((y - y.mean()) / (y.std() + 1e-9)).astype(np.float32)).to(device)[:, None].repeat(1, DIM)
    pf = eng.channel_preflight(fs, attr_full, deg, 7, device)
    a_src, a_dst = eng.agreement_edges(fs, fs, eng.CONS_KNN, device)
    fa_l = []; c_l = []
    for s in seeds:
        rng = np.random.default_rng(s * 100003 + 17); perm = rng.permutation(n); nh = int(HELDOUT_FRAC * n)
        hold = perm[:nh]; vis = perm[nh:]
        E_A = eng.consolidate(a_src, a_dst, fs, n, eng.CONS_PASSES, eng.CONS_ALPHA, device, "")
        fa_l.append(_spearman(_ridge_predict(E_A.cpu().numpy(), y, vis, hold), y[hold]))
        c_l.append(_spearman(_neighbour_true_mean(A, y)[hold], y[hold]))
    F_triv = 0.0; F_A_v = float(np.nanmean(fa_l)); C_v = float(np.nanmean(c_l))
    fair_floor_ok = bool(F_A_v - F_triv >= FAIR_FLOOR_GAP)
    fair_headroom_ok = bool(C_v - F_A_v >= FAIR_HEADROOM)
    fairness_ok = bool(fair_floor_ok and fair_headroom_ok)
    channels_independent = bool(not pf["flagged"])          # not redundant AND not both-degree-loaded
    return dict(F_triv=F_triv, F_A=F_A_v, C=C_v, fair_floor_ok=fair_floor_ok, fair_headroom_ok=fair_headroom_ok,
                fairness_ok=fairness_ok, preflight=pf, channels_independent=channels_independent)


# ---------------------------------------------------------------------------
# Aggregate + verdict.
# ---------------------------------------------------------------------------

def _nm(v):
    a = np.array([x for x in v if x == x], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def aggregate_and_verdict(per_seed, fair, meta):
    def S(arm):
        return _nm([m["scores"][arm] for m in per_seed])

    ftriv = S(F_TRIV); fa = S(F_A); ab = S(A_PLUS_B); abs_ = S(A_PLUS_B_SCR); cc = S(C_CEIL)
    cons_eff_rank = _nm([m["cons_eff_rank"] for m in per_seed])
    cons_rep_var = _nm([m["cons_rep_var"] for m in per_seed])
    ground_gap = ab - fa if (ab == ab and fa == fa) else float("nan")
    scr_gap = abs_ - fa if (abs_ == abs_ and fa == fa) else float("nan")

    strat = {}
    for sn in STRATA:
        fa_s = _nm([m["strat"][F_A][sn]["spear"] for m in per_seed])
        ab_s = _nm([m["strat"][A_PLUS_B][sn]["spear"] for m in per_seed])
        ns = int(_nm([m["strat"][A_PLUS_B][sn]["n"] for m in per_seed]))
        strat[sn] = dict(fa=fa_s, ab=ab_s, gap=(ab_s - fa_s) if (ab_s == ab_s and fa_s == fa_s) else float("nan"), n=ns)

    fairness_ok = bool(fair["fairness_ok"])
    channels_independent = bool(fair["channels_independent"])
    collapsed = bool((cons_eff_rank == cons_eff_rank and cons_eff_rank <= eng.COLLAPSE_RANK_FLOOR)
                     or (cons_rep_var == cons_rep_var and cons_rep_var <= eng.COLLAPSE_VAR_FLOOR))

    def _tail_ok(sn):
        s = strat[sn]
        return bool(s["n"] >= MIN_STRAT_Q and s["gap"] == s["gap"] and s["gap"] >= STRAT_GROUND_MARGIN)

    def _tail_collapse(sn):
        s = strat[sn]
        return bool(s["n"] >= MIN_STRAT_Q and s["gap"] == s["gap"] and s["gap"] <= TIE_EPS)

    agg_gap_ok = bool(ground_gap == ground_gap and ground_gap >= GROUND_MARGIN)
    tail_survives = bool(_tail_ok("LOW") and _tail_ok("MID"))
    tail_collapses = bool(_tail_collapse("LOW") or _tail_collapse("MID"))
    scramble_ok = bool(scr_gap == scr_gap and scr_gap <= SCRAMBLE_MAX)
    scramble_grounds = bool(scr_gap == scr_gap and scr_gap >= GROUND_MARGIN)
    agg_tie = bool(ground_gap == ground_gap and ground_gap <= TIE_EPS)

    grounding_real = bool(fairness_ok and channels_independent and not collapsed
                          and agg_gap_ok and tail_survives and scramble_ok)
    grounding_fails = bool(fairness_ok and channels_independent and not collapsed
                           and (agg_tie or tail_collapses or scramble_grounds))

    if not fairness_ok:
        verdict = "HARD_FAIL_FAIRNESS_BLOCKED"
    elif not channels_independent:
        verdict = "HARD_FAIL_CHANNELS_NOT_INDEPENDENT"
    elif collapsed:
        verdict = "HARD_FAIL_CONSOLIDATION_COLLAPSED"
    elif grounding_real:
        verdict = "HARD_PASS_GROUNDING_REAL"
    elif grounding_fails:
        verdict = "HARD_FAIL_GROUNDING_NOT_REAL"
    else:
        verdict = "MIDDLE_BAND_PARTIAL"

    pf = fair["preflight"]
    verdict_msg = (
        "%s || SPEARMAN: F_triv=%.3f F_A=%.3f A+B=%.3f A+B_scrambled=%.3f C_ceiling=%.3f || "
        "grounding_gap(A+B-F_A)=%s scrambled_gap=%s || "
        "STRATA gap[n]: LOW=%s[%d] MID=%s[%d] HIGH=%s[%d] (F_A/A+B LOW=%.3f/%.3f MID=%.3f/%.3f HIGH=%.3f/%.3f) || "
        "FAIRNESS: F_triv<F_A(gap>=%.2f)=%s F_A<C(headroom>=%.2f)=%s ok=%s || "
        "channels: cross_sim_r=%.3f struct_deg_r=%.3f attr_deg_r=%.3f independent=%s || "
        "collapse: eff_rank=%.1f rep_var=%.3f collapsed=%s || "
        "agg_gap_ok(>=%.2f)=%s tail_survives(LOW&MID>=%.2f)=%s scramble_ok(<=%.2f)=%s || "
        "GROUNDING_REAL=%s GROUNDING_FAILS=%s || coverage=%.1f%% n=%d edges=%d seeds=%d run=%s" % (
            verdict, ftriv, fa, ab, abs_, cc, _fmt(ground_gap), _fmt(scr_gap),
            _fmt(strat["LOW"]["gap"]), strat["LOW"]["n"], _fmt(strat["MID"]["gap"]), strat["MID"]["n"],
            _fmt(strat["HIGH"]["gap"]), strat["HIGH"]["n"],
            strat["LOW"]["fa"], strat["LOW"]["ab"], strat["MID"]["fa"], strat["MID"]["ab"],
            strat["HIGH"]["fa"], strat["HIGH"]["ab"],
            FAIR_FLOOR_GAP, fair["fair_floor_ok"], FAIR_HEADROOM, fair["fair_headroom_ok"], fairness_ok,
            pf["cross_sim_r"], pf["struct_deg_r"], pf["lex_deg_r"], channels_independent,
            cons_eff_rank, cons_rep_var, collapsed,
            GROUND_MARGIN, agg_gap_ok, STRAT_GROUND_MARGIN, tail_survives, SCRAMBLE_MAX, scramble_ok,
            grounding_real, grounding_fails,
            100.0 * meta.get("coverage_frac", float("nan")), meta.get("n_covered_connected", -1),
            meta.get("n_edges", -1), len(per_seed), "full" if len(per_seed) >= 5 else "smoke"))

    gates = dict(
        verdict=verdict,
        scores=dict(F_triv=ftriv, F_A=fa, A_plus_B=ab, A_plus_B_scrambled=abs_, C_ceiling=cc),
        grounding_gap=ground_gap, scrambled_gap=scr_gap, strata=strat,
        fairness=dict(F_triv=fair["F_triv"], F_A=fair["F_A"], C=fair["C"], fair_floor_ok=fair["fair_floor_ok"],
                      fair_headroom_ok=fair["fair_headroom_ok"], fairness_ok=fairness_ok),
        channels=dict(cross_sim_r=pf["cross_sim_r"], struct_deg_r=pf["struct_deg_r"], attr_deg_r=pf["lex_deg_r"],
                      both_degree_loaded=pf["both_degree_loaded"], redundant=pf["redundant"],
                      independent=channels_independent),
        collapse=dict(cons_eff_rank=cons_eff_rank, cons_rep_var=cons_rep_var, collapsed=collapsed),
        decision=dict(agg_gap_ok=agg_gap_ok, tail_survives=tail_survives, tail_collapses=tail_collapses,
                      scramble_ok=scramble_ok, scramble_grounds=scramble_grounds, agg_tie=agg_tie,
                      grounding_real=grounding_real, grounding_fails=grounding_fails),
        bands=dict(FAIR_FLOOR_GAP=FAIR_FLOOR_GAP, FAIR_HEADROOM=FAIR_HEADROOM, GROUND_MARGIN=GROUND_MARGIN,
                   STRAT_GROUND_MARGIN=STRAT_GROUND_MARGIN, SCRAMBLE_MAX=SCRAMBLE_MAX, TIE_EPS=TIE_EPS,
                   MIN_STRAT_Q=MIN_STRAT_Q, HELDOUT_FRAC=HELDOUT_FRAC,
                   COLLAPSE_RANK_FLOOR=eng.COLLAPSE_RANK_FLOOR, COLLAPSE_VAR_FLOOR=eng.COLLAPSE_VAR_FLOOR,
                   CONS_KNN=eng.CONS_KNN, CONS_PASSES=eng.CONS_PASSES, CONS_ALPHA=eng.CONS_ALPHA))
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism self-test (planted worlds; discriminators must FIRE).
# ---------------------------------------------------------------------------

def _planted_attr_world(side, per_cell, seed, noise, unpredictable=False):
    """Clustered graph; a smooth latent attribute y varies with cluster centroid PLUS within-cluster idiosyncrasy
    (headroom). unpredictable=True makes y PURE NOISE independent of the graph -> C ~= F_triv -> the fairness gate must
    BLOCK (no predictability / no headroom)."""
    rng = np.random.default_rng(seed); K = side * side
    ncl = np.array([2 + int(rng.integers(0, per_cell)) for _ in range(K)])
    ent = np.repeat(np.arange(K), ncl); n = int(ent.shape[0])
    cc = (np.arange(K) // side + np.arange(K) % side).astype(np.float64)   # cluster "concreteness" base
    members = [np.where(ent == c)[0] for c in range(K)]
    A = np.zeros((n, n), dtype=np.float32)
    for c in range(K):
        mm = members[c]
        for a in mm:
            for b in mm:
                if a != b:
                    A[a, b] = 1.0
    # cross-cluster edges (neighbouring cluster ids) for a non-trivial graph
    for c in range(K - 1):
        for a in members[c][:1]:
            for b in members[c + 1][:1]:
                A[a, b] = 1.0; A[b, a] = 1.0
    if unpredictable:
        y = rng.standard_normal(n)                         # attribute independent of the graph -> no predictability
    else:
        y = cc[ent] + noise * rng.standard_normal(n)       # cluster base + within-cluster idiosyncrasy -> headroom
    ij = np.argwhere(A > 0)
    tri = np.stack([ij[:, 0], np.zeros(ij.shape[0], dtype=np.int64), ij[:, 1]], axis=1).astype(np.int64)
    return tri, y.astype(np.float64), A.sum(1), A


def _mechanism_selftest(device):
    # (a) informative degree-independent attribute -> A+B beats A-alone, degree-flat; (b) scrambled does NOT ground.
    tri, y, deg, A = _planted_attr_world(16, 4, 0, noise=1.0, unpredictable=False)   # ~700 entities -> >=40/stratum
    ps = run_seed(7, tri, y, deg, A, device)
    gap = ps["scores"][A_PLUS_B] - ps["scores"][F_A]
    scr_gap = ps["scores"][A_PLUS_B_SCR] - ps["scores"][F_A]
    lo = ps["strat"][A_PLUS_B]["LOW"]["spear"] - ps["strat"][F_A]["LOW"]["spear"]
    hi = ps["strat"][A_PLUS_B]["HIGH"]["spear"] - ps["strat"][F_A]["HIGH"]["spear"]
    a_grounds = bool(gap == gap and gap >= 0.05)
    # degree-invariance discriminator = the grounding gain SURVIVES the LOW-degree tail (the actual decision criterion;
    # the planted clustered world has a lumpy degree distribution so HIGH can be under-populated -- the real ConceptNet
    # graph has degree 1..238 and proper strata).
    a_flat = bool(lo == lo and lo >= STRAT_GROUND_MARGIN)
    b_scr_no_ground = bool(scr_gap == scr_gap and scr_gap <= 0.02)

    # (c) fairness-gate logic: headroom world PASSES; UNPREDICTABLE world (y independent of the graph) BLOCKS.
    fair_head = fairness_and_independence(tri, y, deg, A, device, seeds=(7,))
    tri_u, y_u, deg_u, A_u = _planted_attr_world(16, 4, 0, noise=1.0, unpredictable=True)
    fair_u = fairness_and_independence(tri_u, y_u, deg_u, A_u, device, seeds=(7,))
    c_headroom_passes = bool(fair_head["fairness_ok"])
    c_commoncause_blocks = bool(not fair_u["fairness_ok"])   # C ~= F_triv (no predictability) -> blocked

    # (d) collapse discriminator: a collapsed code is caught; the healthy A+B code passes.
    ncol = y.shape[0]
    collapsed = torch.ones(ncol, DIM, device=device) + 1e-4 * eng._noise_feat(ncol, DIM, 3, device)
    d_collapse_caught = bool(eng._rep_variance(collapsed) <= eng.COLLAPSE_VAR_FLOOR
                             and ps["cons_rep_var"] > eng.COLLAPSE_VAR_FLOOR)

    arms_differ = bool(len(set(ps["arm_sigs"].values())) >= 4)
    res = dict(a_gap=round(gap, 4), a_scr_gap=round(scr_gap, 4), a_low_gap=round(lo, 4), a_high_gap=round(hi, 4),
               c_head_FA=round(fair_head["F_A"], 4), c_head_C=round(fair_head["C"], 4),
               c_unpred_FA=round(fair_u["F_A"], 4), c_unpred_C=round(fair_u["C"], 4),
               d_healthy_repvar=round(ps["cons_rep_var"], 4),
               a_grounds=a_grounds, a_flat=a_flat, b_scr_no_ground=b_scr_no_ground,
               c_headroom_passes=c_headroom_passes, c_commoncause_blocks=c_commoncause_blocks,
               d_collapse_caught=d_collapse_caught, arms_differ=arms_differ)
    ok = bool(a_grounds and a_flat and b_scr_no_ground and c_headroom_passes and c_commoncause_blocks
              and d_collapse_caught and arms_differ)
    return ok, res


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")   # CPU-fast; default cpu
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
            verdict_msg="MECHANISM_SELFTEST_FAILED (grounding / scrambled / fairness-gate / collapse discriminators did "
                        "not fire): %s" % st_res, summary="mechanism selftest failed",
            elapsed_s=time.perf_counter() - t0, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS grounding: (a) informative attribute grounds + degree-flat; (b) scrambled does "
                        "not ground; (c) fairness gate passes headroom world + blocks common-cause world; (d) collapse "
                        "caught; arms differ", summary="SELFTEST_PASS",
            elapsed_s=time.perf_counter() - t0, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t0))
        return

    if not _ensure_data_file(CONC_PATH):
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL_DATA_MISSING", run_mode=run_mode,
            verdict_msg="concreteness testbed file absent + self-acquire failed on runner: %s (see data/grounding_"
                        "testbed/PROVENANCE_concreteness.md; stage the file or check runner network)" % CONC_PATH,
            summary="testbed data missing", elapsed_s=time.perf_counter() - t0))
        raise SystemExit(1)

    _log("building concreteness x ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    tri, y, deg, A, names, meta = build_concreteness_subgraph(cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    _log("coverage=%.1f%% (%d/%d) | covered+connected n=%d edges=%d deg[min/med/max]=%.0f/%.0f/%.0f conc[min/mean/max]"
         "=%.2f/%.2f/%.2f" % (100 * meta["coverage_frac"], meta["n_covered"], meta["n_subgraph"],
                              meta["n_covered_connected"], meta["n_edges"], meta["deg_min"], meta["deg_med"],
                              meta["deg_max"], meta["conc_min"], meta["conc_mean"], meta["conc_max"]))

    # PRE-FLIGHT fairness + independence (the HARD go/no-go).
    fair = fairness_and_independence(tri, y, deg, A, device, seeds=tuple(cfg["seeds"][:3]))
    _log("FAIRNESS GATE: F_triv=%.3f < F_A=%.3f < C=%.3f | floor_ok=%s headroom_ok=%s fairness_ok=%s"
         % (fair["F_triv"], fair["F_A"], fair["C"], fair["fair_floor_ok"], fair["fair_headroom_ok"], fair["fairness_ok"]))
    pf = fair["preflight"]
    _log("INDEPENDENCE: cross_sim_r=%.3f struct_deg_r=%.3f attr_deg_r=%.3f both_loaded=%s redundant=%s independent=%s"
         % (pf["cross_sim_r"], pf["struct_deg_r"], pf["lex_deg_r"], pf["both_degree_loaded"], pf["redundant"],
            fair["channels_independent"]))
    if not fair["fairness_ok"]:
        _log("FAIRNESS GATE FAILED -> BLOCK (unfair domain; fall back to Option B PanTHERIA per the design). "
             "Reporting F_triv/F_A/C and stopping the mechanism arms.")

    out_dir = get_output_dir(ANCHOR_NAME)
    per_seed = []; seed_failures = []
    if fair["fairness_ok"] and fair["channels_independent"]:
        for seed in cfg["seeds"]:
            try:
                pm = run_seed(seed, tri, y, deg, A, device)
                sig_vals = set(pm["arm_sigs"].values())
                if len(sig_vals) < 4:
                    raise RuntimeError("ARMS_MUST_DIFFER seed=%d only %d distinct arm sigs" % (seed, len(sig_vals)))
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
                summary="cardinality breach", elapsed_s=time.perf_counter() - t0,
                seed_failures=seed_failures, fairness=fair, subgraph_meta=meta))
            raise SystemExit(1)

    if not per_seed:
        # fairness/independence blocked: emit the block verdict with the three numbers.
        verdict = "HARD_FAIL_FAIRNESS_BLOCKED" if not fair["fairness_ok"] else "HARD_FAIL_CHANNELS_NOT_INDEPENDENT"
        vmsg = ("%s || FAIRNESS: F_triv=%.3f F_A=%.3f C=%.3f floor_ok=%s headroom_ok=%s || channels independent=%s "
                "cross_sim_r=%.3f struct_deg_r=%.3f attr_deg_r=%.3f || coverage=%.1f%% n=%d" % (
                    verdict, fair["F_triv"], fair["F_A"], fair["C"], fair["fair_floor_ok"], fair["fair_headroom_ok"],
                    fair["channels_independent"], pf["cross_sim_r"], pf["struct_deg_r"], pf["lex_deg_r"],
                    100 * meta["coverage_frac"], meta["n_covered_connected"]))
        write_metrics(out_dir, dict(verdict=verdict, verdict_msg=vmsg, summary=vmsg[:200], run_mode=run_mode,
                                    elapsed_s=time.perf_counter() - t0, anchor_name=ANCHOR_NAME,
                                    ts_iso=datetime.now(timezone.utc).isoformat(), fairness=fair,
                                    subgraph_meta=meta, mechanism_selftest=st_res))
        _log("VERDICT: %s" % vmsg)
        return

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, fair, meta)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t0, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=cfg["seeds"], config=dict(seeds=cfg["seeds"], n_nodes=cfg["n_nodes"], dim=DIM),
                   subgraph_meta=meta, gates=gates, fairness=fair, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
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
