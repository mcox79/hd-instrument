"""Grounding cascade depth: iterative recurrent-settling readout vs one-shot k-NN label propagation.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; hash-test ONESHOT vs ITER_CLAMPED vs PURE_DIFFUSE preds)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (ordering acc chance floor = 0.5; discriminator is the REACH/decay-length of the
#   grounding propagation vs a shuffled-attribute empirical null + an over-smoothing collapse gate, not a
#   closed-form estimator noise floor)
# - baseline_in_band at smoke (ONESHOT far-hop must sit near chance so there is headroom to extend; the
#   shuffled control near-acc must be near chance 0.42..0.58; else leakage/over-smoothing)
# - discriminator survives scale (smoke fires it: PURE_DIFFUSE MUST collapse at max T -> over-smoothing
#   detector demonstrably fires; ITER_CLAMPED reach delta measured on a graph with populated far bins)
# - HARD_PASS strictly above floor (reach_delta >= 1 hop AND monotone AND margin@reach >= floor AND
#   not-collapsed@T*, all AND-gated)
# - HP_SCOPE: mechanism gates apply to ITER_CLAMPED (smooth) vs ONESHOT (smooth) reach; PURE_DIFFUSE is the
#   over-smoothing POSITIVE CONTROL (must collapse at max T); SHUFFLED attribute is the genuineness control
# - sweep axis = T (settling steps) -> cardinality_ok via EXPECTED_N_UNITS = n_model_seeds (per-seed unit;
#   the T-sweep is computed WITHIN each seed unit and asserted complete via len(t_sweep) coverage check)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (shuffled empirical null + attribute assortativity
#   recomputed per run; over-smoothing collapse gate proven to fire on the PURE_DIFFUSE positive control)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the pre-reg

SCIENCE (per notes/research_grounding_cascade_depth_multihop_mechanism_2026-07-09.md, Test 1 /
Prediction 1 -- recurrent settling deepens reach):

  The just-shipped grounding-snowball cell (exp_grounding_snowball_transitive_inheritance_v1, commit
  89a088469) measured a REAL but SHALLOW (~1 hop) transitive grounding-inheritance: near d1=0.630,
  far d3=0.484 (collapsed below chance), decay=0.146, genuine_margin=0.135. Its readout is a ONE-SHOT
  k-NN label propagation: each atom predicts its attribute from its k nearest GROUNDED SEEDS in code
  space. Diffusion theory says a one-shot pass realizes only the first spectral term of a random-walk
  expansion -> reach is bounded to ~1 hop. Brain semantic memory (O'Connor/Cree/McRae 2009; Rogers
  2021 eLife) does NOT do this in one shot: it SETTLES over ~20-28 recurrent ticks into a graded
  attractor, and the deep/graded signature appears only in the SETTLED state.

  This cell replaces the ONE-SHOT readout with an ITERATIVE SETTLING readout over the SAME code space
  and SAME grounded seeds, and asks: does settling LENGTHEN the distance-decay -- grounding reaching
  FARTHER hops -- WITHOUT over-smoothing into a flat/uniform field.

  THE OPERATOR: build a code-space kNN affinity graph W (each atom -> its k_diffuse nearest neighbours
  in code space, non-negative cosine weights), row-normalize to a random-walk transition P = D^-1 W.
  Two settling variants swept over T settling steps:
    ITER_SPREAD (mechanism): Zhou 2004 label spreading / APPNP (Klicpera 2019) with restart:
      f^{t+1} = alpha * P f^t + (1 - alpha) * y0, y0 = seed values at seeds / 0 elsewhere. The
      (1-alpha) restart keeps the field ANCHORED to the grounded seeds, so it settles into a graded
      fixed-point ATTRACTOR that propagates farther than one-shot WITHOUT diluting to the global mean
      (the degenerate failure of hard-clamped harmonic interpolation over sparse seeds). This is the
      over-smoothing-resistant operator the source note names. Reaches farther than one-shot IF the
      code graph faithfully carries ConceptNet adjacency (encoder trained for neighbour-closeness;
      rel_auc~0.87).
    PURE_DIFFUSE (over-smoothing POSITIVE CONTROL): f <- P f each step with NO restart. P is
      row-stochastic -> P^t f0 -> <stationary, f0> = a CONSTANT field as t grows (over-smoothing to
      the global mean). This arm MUST collapse at max T: it is the sensitivity witness that the
      over-smoothing detector FIRES.

  THE DISCRIMINATOR (the whole test): the win signature is a LENGTHENED distance-decay -- reach
  extends to >= 1 hop farther (near-acc holds up at d2/d3/d4 where one-shot collapsed) WITHOUT
  over-smoothing. So we distinguish:
    (a) GENUINE deepened reach: reach_iter(T*) - reach_oneshot >= 1, monotone preserved, genuine_margin
        (smooth - shuffled) preserved at the winning step count, field NOT collapsed to the global mean.
    (b) OVER-SMOOTHING artifact: apparent reach gain comes only from steps where the field collapses
        (field_std_ratio small) / the SHUFFLED control ALSO rises / genuine_margin collapses.
  Over-smoothing is the dominant failure mode of iterative diffusion (Li/Han/Wu AAAI 2018); it is
  gated on explicitly via (i) the T-sweep showing reach-then-collapse, (ii) the field-std-ratio
  collapse gate, (iii) the shuffled-rise gate, and (iv) the PURE_DIFFUSE positive control.

  HARD_PASS = reach lengthens >= 1 hop at some non-collapsed T* AND genuine_margin preserved there AND
    over-smoothing gate passes AND the over-smoothing detector demonstrably fires on PURE_DIFFUSE.
  HARD_FAIL = no reach extension at any non-collapsed T (1-hop is structural to near-random codes ->
    escalate to bind-chain build, Direction 2), OR gains are over-smoothing (shuffled rises / margin
    collapses / only-collapsed T show reach).

  Direction 5 (curriculum/bridging-order re-binning) is SKIPPED: it requires betweenness-centrality on
  the graph + re-running propagation at seed-count checkpoints with a changed seed set -- NOT trivial
  (per the task's "fold in ONLY if trivial, else skip"). Flagged as a separate follow-up cell.

REUSE (NOT rebuilt): exp_grounding_snowball_transitive_inheritance_v1 (commit 89a088469) encoder
(train_encoder), CN 2-core subgraph, graph-smooth synthetic attribute (make_smooth_attribute),
shuffled-grounding control, seed sets, distance bins (multi_source_bfs, distance_bins), one-shot
label_propagation (baseline arm), ordering_accuracy. ONLY the readout is new. Teacher-free /
self-contained: NO BGE, NO external LM, NO network. CPU-only. ASCII-only. No emojis. No em dashes.
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

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir,
    write_metrics,
    write_partial,
)
from experiments.exp_teacher_free_relational_encoder_cn_subgraph_v1 import (  # noqa: E402
    load_cn_subgraph,
    char_trigram_features,
    build_adjlist,
)
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import (  # noqa: E402
    make_smooth_attribute,
    attribute_assortativity,
    multi_source_bfs,
    distance_bins,
    train_encoder,
    label_propagation,       # ONE-SHOT baseline readout (reused verbatim)
    ordering_accuracy,
    relational_auc,
    SUBGRAPH_BASE_SEED,
    MIN_BIN_NODES,
)

ANCHOR_NAME = "grounding_iterative_settling_cascade_depth_v1"

# ---------------------------------------------------------------------------
# Config profiles (SMOKE exercises the SAME branches as FULL; only scale differs)
# Encoder keys copied VERBATIM from the parent snowball cell so codes match that pipeline.
# ADDED: k_diffuse (code-space kNN degree for the settling operator) + t_sweep (settling steps).
# ---------------------------------------------------------------------------

SELFTEST_CFG = dict(
    n_nodes=400, seeds=[7], epochs=10, batch=128,
    code_dim=64, feat_dim=1024, temp=0.15, lr=0.01,
    lambda_cov=1.0, lambda_var=1.0, lambda_attr=1.0,
    n_ground_seeds=20, diffuse_steps=8, n_sources=6,
    ridge_lambda=1.0, k_labelprop=7, n_pairs_per_bin=2000,
    k_diffuse=8, t_sweep=[1, 2, 4, 8], alpha=0.85,
)

SMOKE_CFG = dict(
    n_nodes=2500, seeds=[7, 13], epochs=45, batch=256,
    code_dim=128, feat_dim=4096, temp=0.15, lr=0.01,
    lambda_cov=1.0, lambda_var=1.0, lambda_attr=1.0,
    n_ground_seeds=30, diffuse_steps=10, n_sources=25,
    ridge_lambda=1.0, k_labelprop=7, n_pairs_per_bin=4000,
    k_diffuse=10, t_sweep=[1, 2, 4, 8, 16, 32], alpha=0.85,
)

FULL_CFG = dict(
    n_nodes=12000, seeds=[7, 13, 17, 23, 29], epochs=100, batch=512,
    code_dim=256, feat_dim=8192, temp=0.10, lr=0.008,
    lambda_cov=1.0, lambda_var=1.0, lambda_attr=1.0,
    n_ground_seeds=120, diffuse_steps=12, n_sources=80,
    ridge_lambda=1.0, k_labelprop=7, n_pairs_per_bin=6000,
    k_diffuse=10, t_sweep=[1, 2, 4, 8, 16, 32, 64], alpha=0.85,
)

# ---------------------------------------------------------------------------
# Pre-registered bands (picked BEFORE the FULL run)
# ---------------------------------------------------------------------------

REACH_THRESH = 0.55          # ordering acc floor for a hop to count as "grounded" (chance 0.5 + 0.05)
MARGIN_FLOOR = 0.05          # genuine_margin (smooth - shuffled) required at a hop to count as grounded
COLLAPSE_RATIO_MIN = 0.25    # field_std(pred_smooth)/std(attr) must stay >= this; below = over-smoothed
SHUF_MAX = 0.58              # shuffled near-acc must stay near chance; above = homogenization/leakage
MONOTONE_TOL = 0.04          # per-step acc INCREASE tolerated before flagging non-monotone (near->far)
REACH_DELTA_HP = 1           # HARD_PASS: iterative reach extends >= this many hops beyond one-shot
# Band-floor strictness (META_RULE_L / DISCIPLINE PATTERN 3): a reach that clears its floors by less
# than these margins is BAND-HUGGING -> downgrade HARD_PASS to MIDDLE_BAND_BANDFLOOR (inconclusive,
# not a clean pass). 0.01 is ~5% of the 0.50..0.70 discriminating acc band.
REACH_STRICT_MARGIN = 0.01   # newly-reached bin acc must clear REACH_THRESH by >= this for clean HP
MARGIN_STRICT_FLOOR = MARGIN_FLOOR * 1.05  # genuine_margin at reach must clear floor by >= 5%

# attribute graph-smoothness precondition (adaptive gate; same thresholds as parent)
ATTR_ASSORT_SMOOTH_MIN = 0.45
ATTR_ASSORT_SHUFFLED_MAX = 0.20

# over-smoothing detector sensitivity: PURE_DIFFUSE at max T must collapse below this field-std-ratio
PURE_COLLAPSE_MAX = 0.20     # THEORETICAL: P row-stochastic -> P^t f0 -> constant => ratio -> 0

# distance bins: bin0=d1, bin1=d2, bin2=d3, bin3=d4+  (same convention as parent)


# ---------------------------------------------------------------------------
# Start marker / crash diagnostics (SCHEMA-VET section 13)
# ---------------------------------------------------------------------------

def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(
        pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode,
        expected_n_units=expected_n_units, host=platform.node(),
    )
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(
        verdict="CELL_CRASHED",
        verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
        summary=("CELL_CRASHED: %s" % type(exc).__name__),
        elapsed_s=0.0, traceback=traceback.format_exc()[:5000],
        ts_iso=datetime.now(timezone.utc).isoformat(),
        pid=os.getpid(), anchor_name=ANCHOR_NAME,
    )
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


# ---------------------------------------------------------------------------
# Code-space kNN settling operator (the NEW readout)
# ---------------------------------------------------------------------------

def build_code_knn(codes, k_diffuse, chunk=1024):
    """Row-normalized random-walk transition P over a code-space kNN graph, gather form.

    Returns (nbr, w): nbr[n, k] neighbour indices, w[n, k] row-normalized non-neg cosine weights.
    Self-excluded. Chunked topk to cap memory at FULL n. This is P = D^-1 W in gather form:
    a diffusion step is f_new = (w * f[nbr]).sum(axis=1).
    """
    z = codes.astype(np.float32)
    z = z / (np.linalg.norm(z, axis=1, keepdims=True) + 1e-8)
    n = z.shape[0]
    k = int(min(k_diffuse, n - 1))
    nbr = np.empty((n, k), dtype=np.int64)
    w = np.empty((n, k), dtype=np.float64)
    for s in range(0, n, chunk):
        e = min(n, s + chunk)
        sims = z[s:e] @ z.T                     # [b, n]
        rows = np.arange(s, e)
        sims[np.arange(e - s), rows] = -np.inf  # exclude self
        top = np.argpartition(-sims, k - 1, axis=1)[:, :k]  # [b, k]
        br = np.arange(e - s)[:, None]
        wv = np.maximum(sims[br, top], 0.0) + 1e-9
        wv = wv / wv.sum(axis=1, keepdims=True)
        nbr[s:e] = top
        w[s:e] = wv
    return nbr, w


def _diffuse_step(f, nbr, w):
    """One random-walk diffusion step: f_new[i] = sum_j w[i,j] f[nbr[i,j]]."""
    return np.sum(w * f[nbr], axis=1)


def label_spread(nbr, w, seed_idx, seed_vals, T, alpha):
    """Zhou 2004 label spreading / APPNP (Klicpera 2019) with restart: the RECURRENT-SETTLING readout.

      f^0 = y0 ;  f^{t+1} = alpha * P f^t + (1 - alpha) * y0
      y0[i] = seed value if i is a grounded seed else 0 (zero = the neutral prior; attribute is
      zero-mean). alpha in (0,1) is the propagation/retention balance: the (1-alpha) restart term
      keeps the field ANCHORED to the grounded seeds, so it settles into a graded fixed-point
      ATTRACTOR that propagates farther than one-shot WITHOUT diluting to the global mean (the
      failure mode of hard-clamped harmonic interpolation over sparse seeds). seed_vals is the FULL
      attribute array (indexed internally). T = settling steps (the swept telemetry axis)."""
    n = nbr.shape[0]
    sv = np.asarray(seed_vals, dtype=np.float64)[seed_idx]
    y0 = np.zeros(n, dtype=np.float64)
    y0[seed_idx] = sv
    f = y0.copy()
    for _ in range(int(T)):
        f = alpha * _diffuse_step(f, nbr, w) + (1.0 - alpha) * y0
    return f


def pure_diffuse(nbr, w, seed_idx, seed_vals, T):
    """No-clamp diffusion (over-smoothing positive control): f <- P f, NO re-clamp. P row-stochastic
    -> P^t f0 -> constant field as T grows (collapse to global mean). MUST over-smooth at max T.
    seed_vals is the FULL attribute array (indexed by seed_idx internally)."""
    n = nbr.shape[0]
    sv = np.asarray(seed_vals, dtype=np.float64)[seed_idx]
    f = np.zeros(n, dtype=np.float64)
    f[seed_idx] = sv
    for _ in range(int(T)):
        f = _diffuse_step(f, nbr, w)
    return f


# ---------------------------------------------------------------------------
# Per-arm metric computation (reach / decay / genuine margin / field collapse)
# ---------------------------------------------------------------------------

def _field_std_ratio(pred, truth, nonseed_idx):
    if nonseed_idx.shape[0] < 2:
        return float("nan")
    ps = float(np.std(pred[nonseed_idx]))
    ts = float(np.std(truth[nonseed_idx]))
    if ts < 1e-12:
        return float("nan")
    return ps / ts


def _reach_hops(acc_s, margin):
    """Farthest CONTIGUOUS hop (from d1 outward) with acc >= REACH_THRESH AND margin >= MARGIN_FLOOR."""
    r = 0
    for b in range(4):
        a = acc_s[b]
        m = margin[b]
        if (a == a) and (m == m) and (a >= REACH_THRESH) and (m >= MARGIN_FLOOR):
            r = b + 1
        else:
            break
    return r


def _monotone_ok(acc_s):
    """Non-increasing (near->far) across populated bins within MONOTONE_TOL."""
    seq = [acc_s[b] for b in range(4) if acc_s[b] == acc_s[b]]
    for i in range(1, len(seq)):
        if seq[i] > seq[i - 1] + MONOTONE_TOL:
            return False
    return True


def arm_metrics(pred_smooth, pred_shuf, a_smooth, a_shuf, bins, nonseed_idx, rng, n_pairs):
    acc_s = {}
    acc_h = {}
    margin = {}
    for b in range(4):
        idx = bins[b]
        if idx.shape[0] < MIN_BIN_NODES:
            acc_s[b] = float("nan")
            acc_h[b] = float("nan")
            margin[b] = float("nan")
        else:
            a1, _ = ordering_accuracy(pred_smooth, a_smooth, idx, rng, n_pairs)
            a2, _ = ordering_accuracy(pred_shuf, a_shuf, idx, rng, n_pairs)
            acc_s[b] = a1
            acc_h[b] = a2
            margin[b] = (a1 - a2) if (a1 == a1 and a2 == a2) else float("nan")
    fsr = _field_std_ratio(pred_smooth, a_smooth, nonseed_idx)
    reach = _reach_hops(acc_s, margin)
    mono = _monotone_ok(acc_s)
    near = acc_s[0]
    # far anchor = largest populated bin
    far = float("nan")
    far_bin = None
    for b in (3, 2, 1):
        if acc_s[b] == acc_s[b]:
            far = acc_s[b]
            far_bin = b
            break
    decay = (near - far) if (near == near and far == far) else float("nan")
    return dict(acc_smooth=acc_s, acc_shuf=acc_h, margin=margin,
                field_std_ratio=fsr, reach=reach, monotone=mono,
                near_acc=near, far_acc=far, far_bin=far_bin, decay=decay)


def _arm_collapsed(m):
    """Over-smoothing detector. Over-smoothing = field converges toward the global mean so the SMOOTH
    signal itself degrades AND/OR the shuffled control homogenizes up. Crucially a LOW field_std_ratio
    alone is NOT over-smoothing (it also happens at LOW T when the label simply has not spread yet =
    under-spread, near-signal intact); over-smoothing requires that near discriminability was LOST.
    Returns (collapsed, reason)."""
    fsr = m["field_std_ratio"]
    shuf_near = m["acc_shuf"][0]
    margin_near = m["margin"][0]
    near = m["near_acc"]
    if shuf_near == shuf_near and shuf_near > SHUF_MAX:
        return True, "shuffled_near>%.2f" % SHUF_MAX          # control homogenized up
    if margin_near == margin_near and margin_near < MARGIN_FLOOR:
        return True, "margin_near<%.2f" % MARGIN_FLOOR        # genuine signal gone at near band
    if (fsr == fsr and fsr < COLLAPSE_RATIO_MIN) and (near == near and near < REACH_THRESH):
        return True, "field_flattened_and_near_lost"          # field->mean AND near-signal lost
    return False, "ok"


# ---------------------------------------------------------------------------
# Per-model-seed run
# ---------------------------------------------------------------------------

def _pred_digest(p):
    return hashlib.sha256(np.ascontiguousarray(p.astype(np.float32)).tobytes()).hexdigest()


def run_seed(seed, X, edges, degrees, adj, edge_set, cfg, a_smooth, a_shuf,
             ground_seeds, seed_set, bins, nonseed_idx, out_dir=None):
    n_nodes = X.shape[0]
    rng = np.random.default_rng(seed + 4242)
    gs_arr = np.asarray(ground_seeds, dtype=np.int64)
    seed_vals_smooth = a_smooth
    seed_vals_shuf = a_shuf
    n_pairs = cfg["n_pairs_per_bin"]
    t_sweep = cfg["t_sweep"]

    # ungrounded relational encoder (relational-only) -- reused verbatim from parent
    z_ung = train_encoder(X, adj, cfg, seed, out_dir=out_dir, tag="UNGROUNDED")

    rel_auc = relational_auc(z_ung, edges, edge_set, n_nodes, rng, n_pairs * 2)

    # code-space kNN settling operator (built ONCE per seed; only y0 differs across arms/T)
    _log("  seed=%d building code-kNN operator (n=%d k=%d)..." % (seed, n_nodes, cfg["k_diffuse"]))
    t_knn = time.perf_counter()
    nbr, w = build_code_knn(z_ung, cfg["k_diffuse"])
    _log("  seed=%d kNN built (%.1fs); running settling sweep T=%s..." % (
        seed, time.perf_counter() - t_knn, cfg["t_sweep"]))

    # ---- ONESHOT baseline (parent label_propagation over ungrounded codes) ----
    pred_os_smooth = label_propagation(z_ung, gs_arr, a_smooth, cfg["k_labelprop"])
    pred_os_shuf = label_propagation(z_ung, gs_arr, a_shuf, cfg["k_labelprop"])
    m_oneshot = arm_metrics(pred_os_smooth, pred_os_shuf, a_smooth, a_shuf, bins, nonseed_idx, rng, n_pairs)

    # ---- ITER_CLAMPED sweep (mechanism) + PURE_DIFFUSE sweep (over-smoothing positive control) ----
    iter_by_T = {}
    pure_by_T = {}
    # keep a couple of prediction vectors for the arms-differ hash check
    tmax = max(t_sweep)
    digest_probe = {}
    alpha = cfg["alpha"]
    for T in t_sweep:
        pc_s = label_spread(nbr, w, gs_arr, seed_vals_smooth, T, alpha)
        pc_h = label_spread(nbr, w, gs_arr, seed_vals_shuf, T, alpha)
        iter_by_T[T] = arm_metrics(pc_s, pc_h, a_smooth, a_shuf, bins, nonseed_idx, rng, n_pairs)
        pd_s = pure_diffuse(nbr, w, gs_arr, seed_vals_smooth, T)
        pd_h = pure_diffuse(nbr, w, gs_arr, seed_vals_shuf, T)
        pure_by_T[T] = arm_metrics(pd_s, pd_h, a_smooth, a_shuf, bins, nonseed_idx, rng, n_pairs)
        if T == tmax:
            digest_probe = {
                "oneshot_smooth": _pred_digest(pred_os_smooth),
                "iter_clamped_smooth_Tmax": _pred_digest(pc_s),
                "pure_diffuse_smooth_Tmax": _pred_digest(pd_s),
                "iter_clamped_shuf_Tmax": _pred_digest(pc_h),
            }

    # ARMS-MUST-DIFFER (META_RULE_AF): the three readouts (+ smooth vs shuffled) must be distinct.
    dg = digest_probe
    assert dg["oneshot_smooth"] != dg["iter_clamped_smooth_Tmax"], (
        "META_RULE_AF: ONESHOT == ITER_CLAMPED@Tmax (readout not actually iterating)")
    assert dg["iter_clamped_smooth_Tmax"] != dg["pure_diffuse_smooth_Tmax"], (
        "META_RULE_AF: ITER_CLAMPED == PURE_DIFFUSE@Tmax (clamp had no effect)")
    assert dg["iter_clamped_smooth_Tmax"] != dg["iter_clamped_shuf_Tmax"], (
        "META_RULE_AF: smooth == shuffled predictions (attribute not load-bearing)")

    return dict(
        seed=seed,
        relational_auc=rel_auc,
        t_sweep=list(t_sweep),
        oneshot=m_oneshot,
        iter_by_T={str(T): iter_by_T[T] for T in t_sweep},
        pure_by_T={str(T): pure_by_T[T] for T in t_sweep},
        digests=dg,
    )


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------

def _nanmean(vals):
    arr = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(arr.mean()) if arr.shape[0] > 0 else float("nan")


def _mean_arm(arms):
    """Mean an arm_metrics dict across seeds (bin-wise + scalars)."""
    out = dict(acc_smooth={}, acc_shuf={}, margin={})
    for b in range(4):
        out["acc_smooth"][b] = _nanmean([a["acc_smooth"][b] for a in arms])
        out["acc_shuf"][b] = _nanmean([a["acc_shuf"][b] for a in arms])
        out["margin"][b] = _nanmean([a["margin"][b] for a in arms])
    out["field_std_ratio"] = _nanmean([a["field_std_ratio"] for a in arms])
    out["near_acc"] = _nanmean([a["near_acc"] for a in arms])
    out["far_acc"] = _nanmean([a["far_acc"] for a in arms])
    out["decay"] = _nanmean([a["decay"] for a in arms])
    # reach: recompute from the MEAN curve (more stable than mean of per-seed integer reach)
    out["reach"] = _reach_hops(out["acc_smooth"], out["margin"])
    out["monotone"] = _monotone_ok(out["acc_smooth"])
    # far_bin from mean curve
    fb = None
    for b in (3, 2, 1):
        if out["acc_smooth"][b] == out["acc_smooth"][b]:
            fb = b
            break
    out["far_bin"] = fb
    return out


def aggregate_and_verdict(per_seed, attr_meta, subgraph_meta, t_sweep):
    oneshot = _mean_arm([m["oneshot"] for m in per_seed])
    iter_mean = {}
    pure_mean = {}
    for T in t_sweep:
        k = str(T)
        iter_mean[T] = _mean_arm([m["iter_by_T"][k] for m in per_seed])
        pure_mean[T] = _mean_arm([m["pure_by_T"][k] for m in per_seed])

    rel_auc = _nanmean([m["relational_auc"] for m in per_seed])

    # attribute smoothness precondition (adaptive gate)
    precondition_ok = (attr_meta["assort_smooth"] >= ATTR_ASSORT_SMOOTH_MIN) and \
        (attr_meta["assort_shuffled"] <= ATTR_ASSORT_SHUFFLED_MAX)

    reach_oneshot = oneshot["reach"]

    # ITER_CLAMPED: collapse flag + reach per T; T* = max reach among NON-collapsed T (tie -> smallest T)
    iter_reach = {}
    iter_collapsed = {}
    iter_collapse_reason = {}
    for T in t_sweep:
        c, reason = _arm_collapsed(iter_mean[T])
        iter_collapsed[T] = c
        iter_collapse_reason[T] = reason
        iter_reach[T] = iter_mean[T]["reach"]
    noncollapsed_T = [T for T in t_sweep if not iter_collapsed[T]]
    if noncollapsed_T:
        best_reach = max(iter_reach[T] for T in noncollapsed_T)
        # smallest T achieving best reach among non-collapsed
        t_star = min(T for T in noncollapsed_T if iter_reach[T] == best_reach)
    else:
        best_reach = -1
        t_star = None

    reach_delta = (best_reach - reach_oneshot) if best_reach >= 0 else float("nan")

    # over-smoothing detector sensitivity: PURE_DIFFUSE at max T MUST collapse (fires the gate)
    tmax = max(t_sweep)
    pure_fsr_tmax = pure_mean[tmax]["field_std_ratio"]
    pure_collapsed_tmax, pure_reason = _arm_collapsed(pure_mean[tmax])
    oversmoothing_detector_fires = bool(
        (pure_fsr_tmax == pure_fsr_tmax and pure_fsr_tmax < PURE_COLLAPSE_MAX) or pure_collapsed_tmax)

    # over-smoothing actually OBSERVED on the iterative (clamped) arm = a T collapsed via a genuine
    # over-smoothing signature (shuffled rose OR field flattened + near lost), NOT merely margin-fail.
    oversmoothing_observed = pure_collapsed_tmax or any(
        iter_collapsed[T] and (("shuffled" in iter_collapse_reason[T]) or
                               ("field_flattened" in iter_collapse_reason[T]))
        for T in t_sweep)

    # T* arm details
    if t_star is not None:
        arm_star = iter_mean[t_star]
        margin_at_reach = arm_star["margin"][best_reach - 1] if best_reach >= 1 else float("nan")
        reach_bin_acc = arm_star["acc_smooth"][best_reach - 1] if best_reach >= 1 else float("nan")
        monotone_star = arm_star["monotone"]
        collapsed_star = iter_collapsed[t_star]
    else:
        arm_star = None
        margin_at_reach = float("nan")
        reach_bin_acc = float("nan")
        monotone_star = False
        collapsed_star = True

    # band-floor strictness (META_RULE_L / PATTERN 3): does the newly-reached bin clear its floors
    # by a strict margin, or is it band-hugging?
    strictly_above_floor = (
        reach_bin_acc == reach_bin_acc and margin_at_reach == margin_at_reach and
        (reach_bin_acc >= REACH_THRESH + REACH_STRICT_MARGIN) and
        (margin_at_reach >= MARGIN_STRICT_FLOOR))

    # ---- VERDICT ----
    if not precondition_ok:
        verdict = "PRECONDITION_FAIL"
    elif not oversmoothing_detector_fires:
        # the over-smoothing GATE never demonstrated firing -> cannot certify no-over-smoothing claims
        verdict = "MIDDLE_BAND_GATE_NOT_FIRING"
    elif t_star is None:
        # every iterative T collapses. If via genuine over-smoothing signatures -> OVERSMOOTHING;
        # if only via margin-fail (never produced near signal) -> no-extension / structural.
        verdict = "HARD_FAIL_OVERSMOOTHING" if oversmoothing_observed else "HARD_FAIL_NO_EXTENSION"
    elif (reach_delta == reach_delta and reach_delta >= REACH_DELTA_HP and monotone_star and
          (margin_at_reach == margin_at_reach and margin_at_reach >= MARGIN_FLOOR) and not collapsed_star):
        # reach extends >= 1 hop with genuine margin + no over-smoothing. Strict-above-floor -> clean
        # HARD_PASS; band-hugging (reach bin barely clears 0.55) -> MIDDLE_BAND (inconclusive).
        verdict = "HARD_PASS" if strictly_above_floor else "MIDDLE_BAND_BANDFLOOR"
    elif (reach_delta == reach_delta and reach_delta <= 0):
        # no reach extension at any non-collapsed T -> 1-hop structural -> escalate to bind-chain
        verdict = "HARD_FAIL_NO_EXTENSION"
    else:
        verdict = "MIDDLE_BAND"

    def curve(arm):
        return [round(arm["acc_smooth"][b], 4) if arm["acc_smooth"][b] == arm["acc_smooth"][b] else None
                for b in range(4)]

    def shuf_curve(arm):
        return [round(arm["acc_shuf"][b], 4) if arm["acc_shuf"][b] == arm["acc_shuf"][b] else None
                for b in range(4)]

    verdict_msg = (
        "%s | rel_auc=%.3f | ONESHOT reach=%d near=%.3f far(d%s)=%.3f decay=%.3f "
        "smooth=%s shuf=%s | ITER_SPREAD T*=%s reach=%d reach_delta=%s near=%.3f far=%.3f "
        "margin@reach=%.3f strict_above_floor=%s monotone=%s fsr=%.3f | OVERSMOOTH_DETECTOR_FIRES=%s "
        "PURE_DIFFUSE@Tmax fsr=%.3f collapsed=%s (%s) | attr_assort smooth=%.3f shuf=%.3f precond=%s | "
        "subgraph n=%d E=%d seeds=%d" % (
            verdict, rel_auc,
            reach_oneshot, oneshot["near_acc"],
            str(oneshot["far_bin"] + 1) if oneshot["far_bin"] is not None else "?", oneshot["far_acc"],
            oneshot["decay"], curve(oneshot), shuf_curve(oneshot),
            str(t_star), best_reach if best_reach >= 0 else -1,
            ("%.1f" % reach_delta) if reach_delta == reach_delta else "nan",
            arm_star["near_acc"] if arm_star else float("nan"),
            arm_star["far_acc"] if arm_star else float("nan"),
            margin_at_reach, strictly_above_floor, monotone_star,
            arm_star["field_std_ratio"] if arm_star else float("nan"),
            oversmoothing_detector_fires, pure_fsr_tmax, pure_collapsed_tmax, pure_reason,
            attr_meta["assort_smooth"], attr_meta["assort_shuffled"], precondition_ok,
            subgraph_meta["n_nodes"], subgraph_meta["n_edges"], attr_meta["n_ground_seeds"]))

    gates = dict(
        relational_auc_mean=rel_auc,
        reach_oneshot=reach_oneshot,
        reach_iter_best=best_reach,
        t_star=t_star,
        reach_delta=reach_delta,
        margin_at_reach=margin_at_reach,
        reach_bin_acc=reach_bin_acc,
        strictly_above_floor=strictly_above_floor,
        monotone_at_tstar=monotone_star,
        oversmoothing_detector_fires=oversmoothing_detector_fires,
        oversmoothing_observed=oversmoothing_observed,
        pure_diffuse_fsr_tmax=pure_fsr_tmax,
        pure_diffuse_collapsed_tmax=pure_collapsed_tmax,
        precondition_ok=precondition_ok,
        attr_assort_smooth=attr_meta["assort_smooth"],
        attr_assort_shuffled=attr_meta["assort_shuffled"],
        oneshot_curve=curve(oneshot),
        oneshot_shuf_curve=shuf_curve(oneshot),
        oneshot_reach=reach_oneshot,
        oneshot_decay=oneshot["decay"],
        iter_reach_by_T={str(T): iter_reach[T] for T in t_sweep},
        iter_collapsed_by_T={str(T): iter_collapsed[T] for T in t_sweep},
        iter_collapse_reason_by_T={str(T): iter_collapse_reason[T] for T in t_sweep},
        iter_curve_by_T={str(T): curve(iter_mean[T]) for T in t_sweep},
        iter_shuf_curve_by_T={str(T): shuf_curve(iter_mean[T]) for T in t_sweep},
        iter_fsr_by_T={str(T): iter_mean[T]["field_std_ratio"] for T in t_sweep},
        pure_curve_by_T={str(T): curve(pure_mean[T]) for T in t_sweep},
        pure_fsr_by_T={str(T): pure_mean[T]["field_std_ratio"] for T in t_sweep},
        bands=dict(REACH_THRESH=REACH_THRESH, MARGIN_FLOOR=MARGIN_FLOOR,
                   COLLAPSE_RATIO_MIN=COLLAPSE_RATIO_MIN, SHUF_MAX=SHUF_MAX,
                   REACH_DELTA_HP=REACH_DELTA_HP, PURE_COLLAPSE_MAX=PURE_COLLAPSE_MAX),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Discriminator telemetry-sensitivity self-test (ALWAYS runs)
# ---------------------------------------------------------------------------

def discriminator_selftest():
    """Prove the settling readout + reach + over-smoothing gate are telemetry-sensitive (not
    analytically pinned). Plant a 1-D chain with CLUSTERED sparse seeds so large regions are far in
    code space from ALL seeds:
      - ONESHOT (nearest-seed) grounds only near the seed clusters -> short reach.
      - ITER_CLAMPED settling propagates step-by-step through intermediate non-seed nodes -> LONGER
        reach (must exceed one-shot).
      - PURE_DIFFUSE at high T over-smooths to a near-constant field -> field_std_ratio collapses and
        ordering acc falls to chance (over-smoothing detector fires).
      - perturbing T changes reach; perturbing seed VALUES changes acc (telemetry-sensitive)."""
    rng = np.random.default_rng(0)
    n = 600
    pos = np.arange(n)
    # position encoding -> code-space kNN reconstructs chain adjacency
    freqs = np.array([1, 2, 3, 4, 6, 8], dtype=np.float64)
    ang = 2.0 * np.pi * np.outer(pos / n, freqs)              # [n, F]
    z = np.concatenate([np.cos(ang), np.sin(ang)], axis=1)    # [n, 2F]
    z += 0.05 * rng.standard_normal(z.shape)
    z = (z / (np.linalg.norm(z, axis=1, keepdims=True) + 1e-8)).astype(np.float32)

    # smooth attribute over the chain (monotone-ish low-frequency)
    a = (pos / n) + 0.10 * np.sin(2.0 * np.pi * pos / n)
    a = (a - a.mean()) / (a.std() + 1e-9)
    a_shuf = a.copy()
    np.random.default_rng(9).shuffle(a_shuf)

    # CLUSTERED sparse seeds: 3 clusters -> mid-chain regions far from all seeds in code space
    seed_idx = np.concatenate([
        np.arange(40, 60), np.arange(280, 300), np.arange(520, 540)]).astype(np.int64)
    seed_set = set(int(x) for x in seed_idx)

    # chain distance to nearest seed -> bins
    seed_pos = pos[seed_idx]
    dist = np.min(np.abs(pos[:, None] - seed_pos[None, :]), axis=1)
    bins = {0: [], 1: [], 2: [], 3: []}
    for v in range(n):
        if v in seed_set:
            continue
        d = int(dist[v])
        if d <= 15:
            bins[0].append(v)     # d1 near band
        elif d <= 45:
            bins[1].append(v)     # d2
        elif d <= 90:
            bins[2].append(v)     # d3
        else:
            bins[3].append(v)     # d4+ far
    bins = {k: np.array(v, dtype=np.int64) for k, v in bins.items()}
    nonseed_idx = np.concatenate([bins[b] for b in range(4) if bins[b].shape[0] > 0])

    nbr, w = build_code_knn(z, 8)
    n_pairs = 4000
    alpha = 0.85

    def metr(pred_s, pred_h):
        return arm_metrics(pred_s, pred_h, a, a_shuf, bins, nonseed_idx,
                           np.random.default_rng(1), n_pairs)

    m_os = metr(label_propagation(z, seed_idx, a, 7), label_propagation(z, seed_idx, a_shuf, 7))
    t_sweep = [1, 2, 4, 8, 16, 32]
    iter_reach = {}
    iter_collapsed = {}
    for T in t_sweep:
        mi = metr(label_spread(nbr, w, seed_idx, a, T, alpha),
                  label_spread(nbr, w, seed_idx, a_shuf, T, alpha))
        c, _ = _arm_collapsed(mi)
        iter_reach[T] = mi["reach"]
        iter_collapsed[T] = c
    noncol = [T for T in t_sweep if not iter_collapsed[T]]
    best_iter_reach = max((iter_reach[T] for T in noncol), default=-1)

    tmax = max(t_sweep)
    m_pure = metr(pure_diffuse(nbr, w, seed_idx, a, tmax),
                  pure_diffuse(nbr, w, seed_idx, a_shuf, tmax))
    pure_fsr = m_pure["field_std_ratio"]

    # telemetry axis 1 (the one the task names): reach RESPONDS to settling-step count T.
    telemetry_T = (max(iter_reach.values()) != min(iter_reach.values()))
    # telemetry axis 2: perturb seed identity (grounding) -> genuine smooth-vs-shuffled margin at the
    # near band must be large (the graph-smooth attribute is load-bearing; shuffling it kills it).
    m_base8 = metr(label_spread(nbr, w, seed_idx, a, 8, alpha),
                   label_spread(nbr, w, seed_idx, a_shuf, 8, alpha))
    near_margin = m_base8["margin"][0]
    telemetry_seed = (near_margin == near_margin) and (near_margin > 0.10)
    telemetry_moves = bool(telemetry_T and telemetry_seed)

    res = dict(
        oneshot_reach=int(m_os["reach"]), oneshot_curve=[m_os["acc_smooth"][b] for b in range(4)],
        iter_reach_by_T={str(T): int(iter_reach[T]) for T in t_sweep},
        iter_collapsed_by_T={str(T): bool(iter_collapsed[T]) for T in t_sweep},
        best_iter_reach=int(best_iter_reach),
        pure_diffuse_fsr_tmax=float(pure_fsr),
        pure_curve_tmax=[m_pure["acc_smooth"][b] for b in range(4)],
        telemetry_T=bool(telemetry_T), near_margin=float(near_margin),
        telemetry_seed=bool(telemetry_seed), telemetry_moves=bool(telemetry_moves),
    )
    ok = (best_iter_reach > int(m_os["reach"])) and \
        (pure_fsr == pure_fsr and pure_fsr < PURE_COLLAPSE_MAX) and \
        bool(telemetry_moves)
    return bool(ok), res


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args, _unknown = ap.parse_known_args()
    if args.self_test:
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = args.run_mode

    output_dir = str(get_output_dir(ANCHOR_NAME))
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    expected_n_units = len(cfg["seeds"])
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()

    # ---- discriminator telemetry-sensitivity self-test (ALWAYS) ----
    st_ok, st_res = discriminator_selftest()
    _log("discriminator_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="DISCRIMINATOR_SELFTEST_FAILED (not telemetry-sensitive): %s" % st_res,
            summary="discriminator selftest failed", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res))
        raise SystemExit(1)

    # ---- load real ConceptNet subgraph (reused verbatim) ----
    _log("loading ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, meta = load_cn_subgraph(cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    _log("subgraph: %s" % meta)
    n_nodes = len(node_ids)
    X = char_trigram_features(node_words, cfg["feat_dim"])
    adj = build_adjlist(edges, n_nodes)
    edge_set = set((int(a), int(b)) for a, b in edges)

    # ---- graph-smooth attribute + shuffled control + ground seeds (reused verbatim) ----
    attr_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 555)
    a_smooth = make_smooth_attribute(edges, degrees, n_nodes, attr_rng,
                                     cfg["n_sources"], cfg["diffuse_steps"])
    a_shuf = a_smooth.copy()
    attr_rng.shuffle(a_shuf)
    assort_smooth = attribute_assortativity(a_smooth, edges)
    assort_shuffled = attribute_assortativity(a_shuf, edges)
    _log("attribute assortativity: smooth=%.3f shuffled=%.3f" % (assort_smooth, assort_shuffled))

    n_gs = int(min(cfg["n_ground_seeds"], n_nodes // 4))
    ground_seeds = attr_rng.choice(n_nodes, size=n_gs, replace=False)
    seed_set = set(int(x) for x in ground_seeds)
    dist = multi_source_bfs(adj, [int(x) for x in ground_seeds], n_nodes)
    bins, n_unreachable = distance_bins(dist, seed_set)
    nonseed_idx = np.concatenate([bins[b] for b in range(4) if bins[b].shape[0] > 0]) \
        if any(bins[b].shape[0] > 0 for b in range(4)) else np.array([], dtype=np.int64)
    _log("distance bins (non-seed): d1=%d d2=%d d3=%d d4+=%d unreachable=%d" % (
        bins[0].shape[0], bins[1].shape[0], bins[2].shape[0], bins[3].shape[0], n_unreachable))

    attr_meta = dict(assort_smooth=assort_smooth, assort_shuffled=assort_shuffled,
                     n_ground_seeds=n_gs, n_unreachable=int(n_unreachable),
                     bin_counts={b: int(bins[b].shape[0]) for b in range(4)})

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS settling readout + reach + over-smoothing gate telemetry-sensitive",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res, subgraph_meta=meta, attr_meta=attr_meta))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, X, edges, degrees, adj, edge_set, cfg, a_smooth, a_shuf,
                          ground_seeds, seed_set, bins, nonseed_idx, out_dir=out_dir_path)
            pm_persist = {k: v for k, v in pm.items() if k != "digests"}
            per_seed.append(pm_persist)
            write_partial(out_dir_path, seed, dict(seed=seed, metrics=pm_persist))
            osr = pm["oneshot"]["reach"]
            _log("seed=%d rel_auc=%.3f oneshot_reach=%d oneshot_curve=%s" % (
                seed, pm["relational_auc"], osr,
                [round(pm["oneshot"]["acc_smooth"][b], 3) if pm["oneshot"]["acc_smooth"][b] == pm["oneshot"]["acc_smooth"][b] else None for b in range(4)]))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:  # per-seed failure-class instrumentation (META_RULE_J)
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir_path, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (
                expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, subgraph_meta=meta, attr_meta=attr_meta))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, attr_meta, meta, cfg["t_sweep"])
    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_seeds=len(per_seed), seeds=cfg["seeds"], config=cfg,
        subgraph_meta=meta, attr_meta=attr_meta, gates=gates,
        discriminator_selftest=st_res, seed_failures=seed_failures, per_seed=per_seed,
    )
    write_metrics(out_dir_path, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


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
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_od, e)
        raise
