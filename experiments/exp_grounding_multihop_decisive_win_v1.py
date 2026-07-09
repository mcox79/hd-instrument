"""Stage-5 reader DECISIVE-WIN cell: does throwing resource the brain cannot afford (exponential-capacity
dense/modern-Hopfield cleanup + a path-as-single-bound-object chaining primitive + 8x retrieval dimension +
K=5 voted redundancy) CROSS the capacity-correction threshold so multi-hop chaining SNAPS to working, rather
than the marginal improvement Stage-4 delivered?

WIN-designed (ambition-first), NOT floor-clearing. The brain is an existence proof, not a ceiling; this cell
throws dimension/architecture/redundancy a ~20W brain cannot. Claims stay HONEST (real correlated ConceptNet
learned codes; hit@K fidelity; no language understanding claimed), but the bar is a real WIN.

KEY DIAGNOSIS (win-drill notes/research_reader_decisive_multihop_win_engineering_2026-07-09.md): Stage-4's per-
hop cleanup added a flat per-hop boost but did NOT change the decay SLOPE (PLAIN_CLEANUP slope -0.1289 vs
NO_CLEANUP -0.1283 -- statistically identical). That is the signature of operating ABOVE the capacity-correction
threshold: error-correction only adds a constant offset, it cannot flatten the exponential collapse. Three
literatures (VSA/resonator capacity, concatenated-code/threshold-theorem, repetition-code majority-vote) all show
the SAME shape: below a critical load/noise threshold retrieval is near-perfect and errors barely compound; above
it, correction helps only marginally and the slope is unchanged. The WIN = spend resource to cross BELOW the
threshold via (a) an exponential-capacity attractor cleanup (dense Hopfield), (b) a chaining primitive whose noise
is linear-in-length not exponential-in-hops (path-as-object: compose the whole path then decode ONCE), (c) raw
retrieval-dimension throw, (d) voted redundancy.

ARMS (7; paired: identical planted chains + identical seeds across all arms; codes differ BY DESIGN -- code
dimension / cleanup architecture IS the lever). Each single-lever arm changes exactly ONE thing from
PLAIN_CLEANUP; the COMBINED arms stack all levers:
  1 NO_CLEANUP          : Stage-4 must-fail reference. Raw HRR accumulation, global readout, dim=base. Anti-
                          saturation control: MUST collapse at reach>=2 for the discriminator to be valid.
  2 PLAIN_CLEANUP       : Stage-4 best candidate (top-1 argmax snap, dim=base). CALIBRATION ANCHOR -- must
                          reproduce Stage-4 fid2 (~0.106 at FULL config) or the harness drifted.
  3 DENSE_HOPFIELD      : per-hop cleanup readout replaced by a dense/modern-Hopfield softmax attractor pass run
                          to convergence, dim=base. Lever = CLEANUP ARCHITECTURE (exponential vs linear capacity).
  4 N_SCALE             : PLAIN_CLEANUP snap at 8x retrieval dimension. Lever = RESOURCE-THROW / threshold-cross.
  5 PATH_AS_OBJECT      : compose the whole path (no intermediate commit) and decode ONCE via a dense attractor
                          pass, dim = MAX_REACH*base (linear-in-length budget). Lever = CHAINING PRIMITIVE.
  6 COMBINED_WIN        : path-object composition + dense attractor readout at 8x dimension. All levers stacked.
  7 COMBINED_WIN_VOTED  : COMBINED_WIN + K independent random sub-codebook projections, score-ensembled (soft
                          majority vote). The full resource stack.

D_f/N PRE-DIAGNOSTIC (self-test + FULL, load-bearing HONEST-RISK arm): (a) closed-form crosstalk-load ratio
n_nodes/code_dim vs the resonator stability threshold ~0.056 (arXiv:1906.11684) and classical Hopfield alpha_c
~0.138 -- tells above/below threshold; (b) EMPIRICAL incidental-vs-aliasing error decomposition at hop-2: of the
hop-2 misses, what fraction retrieve a genuine graph-neighbour of the true midpoint (SEMANTIC ALIASING -> resource
cannot escape; ceiling is representation quality -> CRITICAL redirect finding) vs an unrelated node (INCIDENTAL
crosstalk -> resource-throw escapes). This is the discriminator that decides whether the WIN is reachable at all.

DISCRIMINATOR: fidelity@d = hit@K (true node at hop d in top-K of the arm's readout vs the codebook), on the SAME
planted true typed L-hop paths for every arm. WIN gate scoped to the COMBINED arms.

HONESTY: real CG'd teacher-free relational learned codes over the REAL ConceptNet subgraph; teacher-free, ASCII-
only; device-aware torch (cuda if available). The dense/modern-Hopfield cleanup lever is a KNOWN substrate upgrade
path (notes/capability_implication_modern_hopfield_upgrade_path_2026-06-04.md; free-probability VSA cleanup drill
2026-06-12); NOVEL here is its composition with the path-as-object primitive on real correlated multi-hop chains.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; hash each arm's per-chain hit signature; >=2 distinct,
#   and every WIN arm asserted distinct from NO_CLEANUP).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: hit@K chance floor = K/n_nodes (~0.002 at n=5000,K=10); WIN floor reach2>=0.60 >> chance and reachable
#   in principle at the thrown dimension (crosstalk floor sqrt(2 ln n / d) drops with d). crlb_n/a for the gain.
# - baseline_in_band: NO_CLEANUP@1 >= 0.30 (single hop works) AND NO_CLEANUP@2 collapses (<=0.40 abs AND <=0.5x@1).
#   If it does not collapse -> INCONCLUSIVE_BASELINE_DID_NOT_FAIL (re-spec). Anti-saturation must-fail control.
# - discriminator survives scale (analytical justification B): the WIN lever IS dimension-threshold-crossing which
#   by construction CANNOT appear at smoke's small dim; smoke verifies MACHINERY + must-fail-control-fires +
#   arms-differ + positive WIN direction (combined gain2 > 0), NOT the full crossing. FULL at thrown dim is where
#   the crosstalk floor sqrt(2 ln n / d) has the headroom smoke lacks. Documented, not skipped.
# - HARD_PASS strictly above floor: WIN = reach2>=0.60 AND reach3>=0.35 AND gain2>=0.30 abs AND slope-flatten>=40%.
# - HP_SCOPE: WIN gate applies ONLY to {COMBINED_WIN, COMBINED_WIN_VOTED}. NO_CLEANUP = must-fail control;
#   PLAIN_CLEANUP = calibration anchor; DENSE/N_SCALE/PATH = single-lever attribution arms (reported, not gated).
# - sweep axis: hop depth d in {1..4}; EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all 7 arms x all
#   depths (arm/depth cardinality check).
# - per-unit failure-class instrumentation (no bare except).
# - calibration_check: adaptive_with_discriminator_gate (baseline-collapse gate recomputed empirically per run;
#   PLAIN calibration anchor checked vs Stage-4 fid2 at FULL; paired per-chain hits so all deltas are paired).
# - PAIRED trials (arm-comparison discriminator): all arms share identical planted chains + seeds per model-seed.
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the pre-reg.
# - progress_logging: print_flush_true (line-buffered stdout + per-epoch/per-seed flush prints + heartbeat).
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

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir,
    write_metrics,
    write_partial,
)
from experiments.exp_teacher_free_relational_encoder_cn_subgraph_v1 import (  # noqa: E402
    char_trigram_features,
)
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import (  # noqa: E402
    SUBGRAPH_BASE_SEED,
)
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import (  # noqa: E402
    load_typed_cn_subgraph,
    make_unitary_roles,
)
# Reuse the Stage-4 cell's VET-landed primitives VERBATIM (calibration-anchor fidelity + no drift).
from experiments.exp_grounding_multihop_perhop_cleanup_gate_v1 import (  # noqa: E402
    train_binding_encoder_dev,
    sample_chains,
    build_typed_diradj,
    _hrr_bind_t,
    _hit_at_k,
    _l2t,
)

ANCHOR_NAME = "grounding_multihop_decisive_win_v1"

HIT_K = 10          # fidelity = hit@K
MAX_REACH = 4       # measure fidelity through reach 4 (decay slope); WIN bar is reach 2-3

# Resonator / Hopfield stability thresholds (CITED)
RESONATOR_THRESH = 0.056     # CITED@arXiv:1906.11684 (resonator dynamics less stable than plain Hopfield above)
HOPFIELD_ALPHA_C = 0.138     # CITED@classical Hopfield storage capacity alpha_c


# ---------------------------------------------------------------------------
# Config profiles. SMOKE exercises the SAME 7 arms / same code path as FULL; only scale differs.
# dim_scale = 8*dim_base (resource-throw), dim_path = MAX_REACH*dim_base (linear-in-length path-object budget).
# ---------------------------------------------------------------------------

SELFTEST_CFG = dict(
    seeds=[7], n_nodes=400, epochs=10, batch=256, dim_base=64, feat_dim=1024,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_chains=200, beta=25.0, n_iter=3, vote_k=5, sub_dim=64,
)

SMOKE_CFG = dict(
    seeds=[7, 13], n_nodes=1800, epochs=60, batch=256, dim_base=128, feat_dim=4096,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_chains=500, beta=25.0, n_iter=3, vote_k=5, sub_dim=128,
)

FULL_CFG = dict(
    seeds=[7, 13, 17], n_nodes=5000, epochs=140, batch=512, dim_base=256, feat_dim=8192,
    temp=0.10, lr=0.008, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_chains=1200, beta=25.0, n_iter=3, vote_k=5, sub_dim=512,
)

# ---------------------------------------------------------------------------
# Pre-registered WIN bands (picked BEFORE the FULL run; from the win-drill, tightened by cell-author).
# ---------------------------------------------------------------------------
HOP1_MIN = 0.30            # NO_CLEANUP@1 must clear this (single hop present)
BASE_COLLAPSE_ABS = 0.40   # anti-saturation: NO_CLEANUP@2 <= this AND ...
BASE_COLLAPSE_FRAC = 0.50  # ... <= this fraction of NO_CLEANUP@1 (must-fail control lost >= half its reach)
WIN_REACH2 = 0.60          # WIN: best combined arm reach-2 fidelity >= this (usable, not detectable)
WIN_REACH3 = 0.35          # WIN: reach-3 fidelity >= this (material chainable signal)
WIN_GAIN2 = 0.30           # WIN: combined@2 - NO_CLEANUP@2 >= this absolute (decisive multiple of Stage-4's 0.10)
WIN_SLOPE_FLATTEN = 0.40   # WIN: |decay_slope| flattened by >= this fraction vs NO_CLEANUP baseline slope
FAIL_REACH2 = 0.15         # HARD_FAIL: all combined arms reach-2 < this (no threshold crossing)
FAIL_SLOPE_FLATTEN = 0.10  # HARD_FAIL: AND slope-flatten < this (ceiling fundamental / semantic-aliasing)
CALIB_TOL = 0.06           # PLAIN_CLEANUP@2 must reproduce Stage-4 fid2 within this at FULL (harness-drift gate)
CALIB_TARGET_FULL = 0.106  # MEASURED@data/exp_grounding_multihop_perhop_cleanup_gate_v1/metrics.json gates.fid_mean.PLAIN_CLEANUP.2
ALIAS_HI = 0.50            # aliasing_frac >= this at hop-2 -> resource cannot escape (semantic-aliasing ceiling)
ALIAS_LO = 0.30            # aliasing_frac <= this -> incidental crosstalk (resource-throw escapes)

# Arm spec: name -> (cleanup_mode, code_set). code_set in {base, path, scale}.
NO_CLEANUP = "NO_CLEANUP"
PLAIN_CLEANUP = "PLAIN_CLEANUP"
DENSE_HOPFIELD = "DENSE_HOPFIELD"
N_SCALE = "N_SCALE"
PATH_AS_OBJECT = "PATH_AS_OBJECT"
COMBINED_WIN = "COMBINED_WIN"
COMBINED_WIN_VOTED = "COMBINED_WIN_VOTED"

ARM_SPEC = {
    NO_CLEANUP:         ("none",  "base"),
    PLAIN_CLEANUP:      ("plain", "base"),
    DENSE_HOPFIELD:     ("dense", "base"),
    N_SCALE:            ("plain", "scale"),
    PATH_AS_OBJECT:     ("path",  "path"),
    COMBINED_WIN:       ("path",  "scale"),
    COMBINED_WIN_VOTED: ("vote",  "scale"),
}
ARMS = list(ARM_SPEC.keys())
# HP_SCOPE (WIN gate): the goal is "cross the capacity-correction threshold so multi-hop chaining snaps to
# working" via ANY lever, with the single-lever arms attributing WHICH lever crossed. So the WIN gate is
# satisfiable by any MECHANISM arm (dense-cleanup / resource-throw / path-object / stacked). NO_CLEANUP is the
# must-fail control and PLAIN_CLEANUP the calibration/marginal reference -- both EXCLUDED from the WIN gate.
# The MAXIMAL arms (used for the HARD_FAIL ceiling condition) are the biggest-resource shots.
WIN_ARMS = [DENSE_HOPFIELD, N_SCALE, PATH_AS_OBJECT, COMBINED_WIN, COMBINED_WIN_VOTED]
MAXIMAL_ARMS = [N_SCALE, COMBINED_WIN, COMBINED_WIN_VOTED]  # ceiling-fundamental judged on these
ATTRIB_ARMS = [DENSE_HOPFIELD, N_SCALE, PATH_AS_OBJECT]     # single-lever attribution (also WIN-eligible)


# ---------------------------------------------------------------------------
# Device
# ---------------------------------------------------------------------------

def _resolve_device(arg_device):
    if arg_device == "cpu":
        return torch.device("cpu")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


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


# ---------------------------------------------------------------------------
# Dense / modern-Hopfield attractor cleanup (softmax energy descent, run to convergence).
# CITED@arXiv:2503.00241 (modern Hopfield), notes/capability_implication_modern_hopfield_upgrade_path_2026-06-04.
# ---------------------------------------------------------------------------

def _dense_hopfield(query, Z, beta, n_iter):
    """Modern-Hopfield attractor: iterate q <- normalize(softmax(beta * q.Z^T) . Z). query,Z L2-normed.
    Returns (final attractor q [C,d], final score q.Z^T [C,n]) for hit@K + argmax commit."""
    q = _l2t(query)
    for _ in range(n_iter):
        sim = q @ Z.t()                          # [C, n]
        p = torch.softmax(beta * sim, dim=1)     # sharpened association
        q = _l2t(p @ Z)                          # weighted retrieval toward the nearest attractor
    return q, (q @ Z.t())


def _voted_score(query, vote_projs, beta, n_iter):
    """K independent random sub-codebook projections; dense-Hopfield readout in each; soft-vote (sum of
    per-projection softmax score distributions). vote_projs: list of (P [d,sub], ZP [n,sub] L2-normed)."""
    acc = None
    for P, ZP in vote_projs:
        q = _l2t(query @ P)
        for _ in range(n_iter):
            sim = q @ ZP.t()
            p = torch.softmax(beta * sim, dim=1)
            q = _l2t(p @ ZP)
        s = torch.softmax(beta * (q @ ZP.t()), dim=1)
        acc = s if acc is None else acc + s
    return acc


# ---------------------------------------------------------------------------
# Chain retrieval per arm (all arms paired on identical planted chains). Returns fid[d] + per-chain hit signature.
# ---------------------------------------------------------------------------

def run_win_arm(mode, Z, roles_t, start, targets, role_ids, k, device, beta, n_iter, vote_projs=None):
    L = len(targets)
    cue = Z[torch.from_numpy(start).to(device)].clone()     # [C, d] start codes
    fid = {}
    hit_sig = []
    for h in range(L):
        role = roles_t[torch.from_numpy(role_ids[h]).to(device)]    # [C, d]
        pred = _hrr_bind_t(role, cue)                              # [C, d] hop bind
        tgt = torch.from_numpy(targets[h]).to(device)
        if mode == "none":
            score = _l2t(pred) @ Z.t()
            carry = pred                                          # raw accumulation (crosstalk compounds)
        elif mode == "plain":
            score = _l2t(pred) @ Z.t()
            est = score.argmax(dim=1)
            carry = Z[est]                                        # snap to clean codebook node
        elif mode == "dense":
            _q, score = _dense_hopfield(pred, Z, beta, n_iter)
            est = score.argmax(dim=1)
            carry = Z[est]                                        # snap the dense attractor's winner
        elif mode == "path":
            _q, score = _dense_hopfield(pred, Z, beta, n_iter)    # dense readout at (big) dim
            carry = pred                                          # DEFER: carry raw composed path-object
        elif mode == "vote":
            score = _voted_score(pred, vote_projs, beta, n_iter)  # K sub-projection soft-vote
            carry = pred                                          # DEFER (path-object) + voted readout
        else:
            raise ValueError("unknown mode %r" % mode)
        hits = _hit_at_k(score, tgt, k)
        fid[h + 1] = float(hits.float().mean().item())
        hit_sig.append(hits.detach().to("cpu").numpy().astype(np.uint8))
        cue = carry
    sig = hashlib.sha256(np.concatenate(hit_sig).tobytes()).hexdigest()
    return fid, sig


# ---------------------------------------------------------------------------
# Incidental-vs-aliasing hop-2 error decomposition (HONEST-RISK discriminator). Conditions on hop-1 CORRECT
# (uses true midpoint) so it measures pure hop-2 error structure: of the hop-2 misses, what fraction retrieve a
# genuine graph-neighbour of the true midpoint (semantic aliasing -> resource cannot escape) vs an unrelated node
# (incidental crosstalk -> resource-throw escapes).
# ---------------------------------------------------------------------------

def error_decomposition(Z, roles_t, dir_adj, start, targets, role_ids, k, device):
    C = start.shape[0]
    if len(targets) < 2:
        return dict(n_hop2=0, n_err=0, aliasing_frac=float("nan"))
    mid = torch.from_numpy(targets[0]).to(device)                 # TRUE hop-1 midpoint
    role2 = roles_t[torch.from_numpy(role_ids[1]).to(device)]
    pred2 = _hrr_bind_t(role2, Z[mid])
    score2 = _l2t(pred2) @ Z.t()                                  # [C, n]
    tgt2 = torch.from_numpy(targets[1]).to(device)
    hit2 = _hit_at_k(score2, tgt2, k)                             # [C] bool
    top1 = score2.argmax(dim=1).detach().to("cpu").numpy()
    mid_np = targets[0]
    tgt2_np = targets[1]
    hit2_np = hit2.detach().to("cpu").numpy()
    n_err = 0
    n_alias = 0
    for c in range(C):
        if hit2_np[c]:
            continue                                             # correct -> not an error
        n_err += 1
        w = int(top1[c])
        if w == int(tgt2_np[c]):
            continue
        nbrs = {int(v) for (v, _r) in dir_adj[int(mid_np[c])]}    # genuine graph-neighbours of the true midpoint
        if w in nbrs:
            n_alias += 1                                         # retrieved a real relational neighbour (alias)
    aliasing_frac = (n_alias / n_err) if n_err > 0 else float("nan")
    return dict(n_hop2=int(C), n_err=int(n_err), n_alias=int(n_alias), aliasing_frac=float(aliasing_frac))


# ---------------------------------------------------------------------------
# Per-model-seed run: all 7 arms on the identical planted chains + graph
# ---------------------------------------------------------------------------

def _cfg_for_dim(cfg, dim):
    c = dict(cfg)
    c["code_dim"] = dim
    return c


def run_seed(seed, X, edges, rels, dir_adj, cfg, device, out_dir=None):
    n_nodes = X.shape[0]
    db = cfg["dim_base"]
    dp = MAX_REACH * db
    ds = 8 * db
    beta = cfg["beta"]
    n_iter = cfg["n_iter"]

    # Roles per code set (unitary HRR roles at each dimension)
    role_rng_b = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    role_rng_p = np.random.default_rng(SUBGRAPH_BASE_SEED + 778)
    role_rng_s = np.random.default_rng(SUBGRAPH_BASE_SEED + 779)
    T = int(rels.max()) + 1 if rels.size else 1
    roles_b = torch.from_numpy(make_unitary_roles(T, db, role_rng_b)).to(device)
    roles_p = torch.from_numpy(make_unitary_roles(T, dp, role_rng_p)).to(device)
    roles_s = torch.from_numpy(make_unitary_roles(T, ds, role_rng_s)).to(device)

    # Three learned encoders (base / path / scale dimension). The dimension IS the resource lever.
    _log("  seed=%d train encoders base=%d path=%d scale=%d" % (seed, db, dp, ds))
    Z_base = train_binding_encoder_dev(X, edges, rels, roles_b, _cfg_for_dim(cfg, db), seed, device,
                                       out_dir=out_dir, tag="BASE")
    Z_path = train_binding_encoder_dev(X, edges, rels, roles_p, _cfg_for_dim(cfg, dp), seed, device,
                                       out_dir=out_dir, tag="PATH")
    Z_scale = train_binding_encoder_dev(X, edges, rels, roles_s, _cfg_for_dim(cfg, ds), seed, device,
                                        out_dir=out_dir, tag="SCALE")
    code_sets = {"base": (Z_base, roles_b), "path": (Z_path, roles_p), "scale": (Z_scale, roles_s)}
    enc_dig = hashlib.sha256(Z_base.detach().to("cpu").numpy().astype(np.float32).tobytes()).hexdigest()

    # K independent random sub-codebook projections of the scale codes (for the voted arm)
    g = torch.Generator(device="cpu").manual_seed(seed + 4242)
    vote_projs = []
    for _kk in range(cfg["vote_k"]):
        P = (torch.randn(ds, cfg["sub_dim"], generator=g) / np.sqrt(ds)).to(device)
        ZP = _l2t(Z_scale @ P)
        vote_projs.append((P, ZP))

    # Planted true typed L-hop chains (SAME for every arm -> paired)
    chain_rng = np.random.default_rng(seed + 909)
    start, targets, role_ids = sample_chains(dir_adj, cfg["n_chains"], MAX_REACH, chain_rng)
    n_chains_got = int(start.shape[0])

    arms = {}
    sigs = {}
    for arm in ARMS:
        mode, cset = ARM_SPEC[arm]
        Z, roles_t = code_sets[cset]
        vp = vote_projs if mode == "vote" else None
        fid, sig = run_win_arm(mode, Z, roles_t, start, targets, role_ids, HIT_K, device, beta, n_iter, vp)
        arms[arm] = dict(fid=fid)
        sigs[arm] = sig
        _log("  seed=%d %-20s fid@[1..%d]=%s" % (
            seed, arm, MAX_REACH, {dd: round(fid[dd], 3) for dd in range(1, MAX_REACH + 1)}))

    # Incidental-vs-aliasing decomposition on the base codes (hop-1 conditioned correct)
    err_dec = error_decomposition(Z_base, roles_b, dir_adj, start, targets, role_ids, HIT_K, device)
    _log("  seed=%d error_decomp %s" % (seed, err_dec))

    if len(set(sigs.values())) < 2:
        _log("  [warn] seed=%d arm hit-signatures collapsed to <2 distinct" % seed)

    return dict(seed=seed, arms=arms, arm_sigs=sigs, encoder_digest=enc_dig,
                n_chains=n_chains_got, dims=dict(base=db, path=dp, scale=ds),
                error_decomp=err_dec)


# ---------------------------------------------------------------------------
# Aggregate + WIN verdict
# ---------------------------------------------------------------------------

def _nanmean(vals):
    arr = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(arr.mean()) if arr.shape[0] > 0 else float("nan")


def _decay_slope(fid):
    ds = np.array([d for d in range(1, MAX_REACH + 1)], dtype=np.float64)
    ys = np.array([fid[d] for d in range(1, MAX_REACH + 1)], dtype=np.float64)
    if np.any(ys != ys):
        return float("nan")
    A = np.vstack([ds, np.ones_like(ds)]).T
    return float(np.linalg.lstsq(A, ys, rcond=None)[0][0])


def _fmt(x):
    return ("%.3f" % x) if (x == x) else "nan"


def aggregate_and_verdict(per_seed, subgraph_meta, cfg, run_mode):
    fid = {a: {d: _nanmean([m["arms"][a]["fid"][d] for m in per_seed]) for d in range(1, MAX_REACH + 1)}
           for a in ARMS}
    slope = {a: _decay_slope(fid[a]) for a in ARMS}

    base1 = fid[NO_CLEANUP][1]
    base2 = fid[NO_CLEANUP][2]
    base3 = fid[NO_CLEANUP][3]
    base_slope = slope[NO_CLEANUP]

    hop1_ok = (base1 == base1) and (base1 >= HOP1_MIN)
    baseline_collapses = (base2 == base2 and base1 == base1
                          and base2 <= BASE_COLLAPSE_ABS and base2 <= BASE_COLLAPSE_FRAC * base1)

    def _flatten(a):
        sa = slope[a]
        if not (sa == sa) or not (base_slope == base_slope) or abs(base_slope) < 1e-9:
            return float("nan")
        return 1.0 - (abs(sa) / abs(base_slope))

    # Per-WIN-arm evaluation
    win_eval = {}
    for a in WIN_ARMS:
        r2 = fid[a][2]
        r3 = fid[a][3]
        g2 = (r2 - base2) if (r2 == r2 and base2 == base2) else float("nan")
        fl = _flatten(a)
        hp = bool(r2 == r2 and r2 >= WIN_REACH2 and r3 == r3 and r3 >= WIN_REACH3
                  and g2 == g2 and g2 >= WIN_GAIN2 and fl == fl and fl >= WIN_SLOPE_FLATTEN)
        win_eval[a] = dict(reach2=r2, reach3=r3, gain2=g2, slope_flatten=fl, win=hp)

    # Attribution arms (reported only)
    attrib = {}
    for a in ATTRIB_ARMS:
        r2 = fid[a][2]
        attrib[a] = dict(reach2=r2, gain2=(r2 - base2) if (r2 == r2 and base2 == base2) else float("nan"),
                         slope_flatten=_flatten(a))

    # Prediction sub-verdicts for research (booleans)
    plain2 = fid[PLAIN_CLEANUP][2]
    preds = dict(
        P1_threshold_superlinear=bool(
            attrib[N_SCALE]["gain2"] == attrib[N_SCALE]["gain2"]
            and (plain2 - base2) == (plain2 - base2)
            and attrib[N_SCALE]["gain2"] >= 2.0 * max(plain2 - base2, 1e-6)),
        P2_dense_beats_plain=bool(fid[DENSE_HOPFIELD][2] - plain2 >= 0.15),
        P3_path_material=bool(fid[PATH_AS_OBJECT][2] >= 0.50),
        P4_vote_lift=bool(fid[COMBINED_WIN_VOTED][2] - fid[COMBINED_WIN][2] >= 0.10),
    )

    win_arms_pass = [a for a in WIN_ARMS if win_eval[a]["win"]]
    best_win = max(WIN_ARMS, key=lambda a: (win_eval[a]["reach2"] if win_eval[a]["reach2"] == win_eval[a]["reach2"]
                                            else -1e9))
    # ceiling-fundamental judged on the MAXIMAL-resource arms: nothing crosses even at max resource
    all_win_below_fail = all(
        (win_eval[a]["reach2"] == win_eval[a]["reach2"] and win_eval[a]["reach2"] < FAIL_REACH2
         and win_eval[a]["slope_flatten"] == win_eval[a]["slope_flatten"]
         and win_eval[a]["slope_flatten"] < FAIL_SLOPE_FLATTEN)
        for a in MAXIMAL_ARMS)

    # Calibration anchor (FULL only; smoke config differs so no numeric anchor)
    calib_ok = None
    calib_delta = None
    if run_mode == "full":
        calib_delta = abs(plain2 - CALIB_TARGET_FULL)
        calib_ok = bool(calib_delta <= CALIB_TOL)

    # Aliasing decomposition (mean over seeds)
    alias_fracs = [m["error_decomp"].get("aliasing_frac", float("nan")) for m in per_seed]
    aliasing_frac = _nanmean(alias_fracs)
    if aliasing_frac == aliasing_frac:
        alias_regime = ("SEMANTIC_ALIASING" if aliasing_frac >= ALIAS_HI
                        else "INCIDENTAL_CROSSTALK" if aliasing_frac <= ALIAS_LO
                        else "MIXED")
    else:
        alias_regime = "UNKNOWN"

    # D_f/N crosstalk-load ratio (THEORETICAL closed form; naive full-codebook load per decode)
    n_eff = subgraph_meta["n_nodes"]
    load_base = n_eff / cfg["dim_base"]
    load_scale = n_eff / (8 * cfg["dim_base"])
    above_thresh_scale = bool(load_scale > RESONATOR_THRESH)
    dim_needed_resonator = n_eff / RESONATOR_THRESH

    # Verdict
    if not hop1_ok:
        verdict = "INCONCLUSIVE_HOP1_FAILED"
    elif not baseline_collapses:
        verdict = "INCONCLUSIVE_BASELINE_DID_NOT_FAIL"
    elif run_mode == "full" and calib_ok is False:
        verdict = "HARD_FAIL_HARNESS_DRIFT_CALIBRATION"
    elif len(win_arms_pass) > 0:
        verdict = "HARD_PASS_WIN"
    elif all_win_below_fail:
        verdict = "HARD_FAIL_CEILING_FUNDAMENTAL"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_CROSSING"

    verdict_msg = (
        "%s || NO_CLEANUP @1=%.3f(hop1_ok=%s) @2=%.3f(collapses=%s) @3=%.3f slope=%.3f || "
        "PLAIN @2=%.3f DENSE @2=%.3f N_SCALE @2=%.3f PATH @2=%.3f || "
        "COMBINED @2=%.3f @3=%.3f g2=%s flat=%s | VOTED @2=%.3f @3=%.3f g2=%s flat=%s | best_win=%s win_arms=%s || "
        "preds P1=%s P2=%s P3=%s P4=%s || aliasing_frac=%s regime=%s || load_base=%.2f load_scale=%.3f "
        "above_thr=%s dim_needed=%.0f (thr=%.3f) || calib(PLAIN@2 vs %.3f)=%s d=%s || "
        "WIN bands: R2>=%.2f R3>=%.2f GAIN2>=%.2f FLATTEN>=%.0f%% || n=%d E=%d rel=%d seeds=%d hit@K=%d run=%s" % (
            verdict, base1, hop1_ok, base2, baseline_collapses, base3, base_slope,
            plain2, fid[DENSE_HOPFIELD][2], fid[N_SCALE][2], fid[PATH_AS_OBJECT][2],
            fid[COMBINED_WIN][2], fid[COMBINED_WIN][3], _fmt(win_eval[COMBINED_WIN]["gain2"]),
            _fmt(win_eval[COMBINED_WIN]["slope_flatten"]),
            fid[COMBINED_WIN_VOTED][2], fid[COMBINED_WIN_VOTED][3], _fmt(win_eval[COMBINED_WIN_VOTED]["gain2"]),
            _fmt(win_eval[COMBINED_WIN_VOTED]["slope_flatten"]), best_win, win_arms_pass,
            preds["P1_threshold_superlinear"], preds["P2_dense_beats_plain"], preds["P3_path_material"],
            preds["P4_vote_lift"], _fmt(aliasing_frac), alias_regime, load_base, load_scale,
            above_thresh_scale, dim_needed_resonator, RESONATOR_THRESH,
            CALIB_TARGET_FULL, calib_ok, _fmt(calib_delta) if calib_delta is not None else "n/a",
            WIN_REACH2, WIN_REACH3, WIN_GAIN2, WIN_SLOPE_FLATTEN * 100,
            subgraph_meta["n_nodes"], subgraph_meta["n_edges"], subgraph_meta.get("n_relation_types", -1),
            len(per_seed), HIT_K, run_mode))

    gates = dict(
        verdict=verdict, fid_mean=fid, decay_slope=slope,
        base_fid1=base1, base_fid2=base2, base_fid3=base3, base_slope=base_slope,
        hop1_ok=bool(hop1_ok), baseline_collapses=bool(baseline_collapses),
        win_eval=win_eval, attrib=attrib, win_arms_pass=win_arms_pass, best_win=best_win,
        predictions=preds,
        aliasing_frac=aliasing_frac, alias_regime=alias_regime,
        df_over_n=dict(load_base=load_base, load_scale=load_scale, resonator_thresh=RESONATOR_THRESH,
                       hopfield_alpha_c=HOPFIELD_ALPHA_C, above_thresh_scale=above_thresh_scale,
                       dim_needed_resonator=dim_needed_resonator),
        calibration=dict(target=CALIB_TARGET_FULL, plain2=plain2, delta=calib_delta, ok=calib_ok, tol=CALIB_TOL),
        bands=dict(HOP1_MIN=HOP1_MIN, BASE_COLLAPSE_ABS=BASE_COLLAPSE_ABS, BASE_COLLAPSE_FRAC=BASE_COLLAPSE_FRAC,
                   WIN_REACH2=WIN_REACH2, WIN_REACH3=WIN_REACH3, WIN_GAIN2=WIN_GAIN2,
                   WIN_SLOPE_FLATTEN=WIN_SLOPE_FLATTEN, FAIL_REACH2=FAIL_REACH2,
                   FAIL_SLOPE_FLATTEN=FAIL_SLOPE_FLATTEN, HIT_K=HIT_K, MAX_REACH=MAX_REACH,
                   ALIAS_HI=ALIAS_HI, ALIAS_LO=ALIAS_LO),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism / discriminator self-test (ALWAYS runs, CPU) on PLANTED correlated codes.
# ---------------------------------------------------------------------------

def _mechanism_selftest():
    """Proves on planted correlated codes: (0) chain machinery works (hop-1 high); (1) must-fail NO_CLEANUP
    collapses at reach>=2 (discriminator telemetry-sensitive, not saturation-vacuous); (2) dense-Hopfield sharpens
    (DENSE >= PLAIN at deep reach); (3) path-object composes (PATH produces > chance at reach 2); (4) voted score
    is a valid aggregated distribution and >= single sub-projection at deep reach; (5) all arms differ; (6) D_f/N
    load ratio computed and above threshold for the planted config."""
    device = torch.device("cpu")
    rng = np.random.default_rng(0)
    db = 96
    T = 4
    n = 1000
    beta, n_iter = 25.0, 3
    roles_b = torch.from_numpy(make_unitary_roles(T, db, np.random.default_rng(11))).to(device)

    # Planted correlated codebook + recoverable typed chain (same recipe family as Stage-4 self-test).
    n_clusters = 40
    per = n // n_clusters
    base = rng.standard_normal((n_clusters, db)).astype(np.float32)
    base_u = base / (np.linalg.norm(base, axis=1, keepdims=True) + 1e-8)
    base_ut = torch.from_numpy(base_u.astype(np.float32)).to(device)
    dir_adj = [[] for _ in range(n)]
    order = rng.permutation(n)
    Z2 = torch.zeros(n, db, device=device)
    u0 = int(order[0])
    Z2[u0] = _l2t((base_ut[u0 // per] + 0.20 * torch.randn(db))[None, :])[0]
    for k in range(1, n):
        u = int(order[k - 1]); v = int(order[k]); r = int(rng.integers(0, T))
        pred = _l2t(_hrr_bind_t(roles_b[r:r + 1], _l2t(Z2[u:u + 1])))[0]
        nz = _l2t(torch.randn(1, db))[0]
        Z2[v] = _l2t((pred + 0.50 * base_ut[v // per] + 1.60 * nz)[None, :])[0]
        dir_adj[u].append((v, r))
    Z = _l2t(Z2)

    start, targets, role_ids = sample_chains(dir_adj, 150, MAX_REACH, np.random.default_rng(1))

    # sub-projections for a small voted run
    g = torch.Generator(device="cpu").manual_seed(999)
    vote_projs = [((torch.randn(db, 48, generator=g) / np.sqrt(db)),) for _ in range(3)]
    vote_projs = [(P, _l2t(Z @ P)) for (P,) in vote_projs]

    fid = {}
    sigs = {}
    for arm in [NO_CLEANUP, PLAIN_CLEANUP, DENSE_HOPFIELD]:
        f, s = run_win_arm(ARM_SPEC[arm][0], Z, roles_b, start, targets, role_ids, HIT_K, device, beta, n_iter)
        fid[arm] = f
        sigs[arm] = s
    # path + vote on the SAME base codes for the self-test (dimension lever is exercised in the real run)
    fid[PATH_AS_OBJECT], sigs[PATH_AS_OBJECT] = run_win_arm(
        "path", Z, roles_b, start, targets, role_ids, HIT_K, device, beta, n_iter)
    fid[COMBINED_WIN_VOTED], sigs[COMBINED_WIN_VOTED] = run_win_arm(
        "vote", Z, roles_b, start, targets, role_ids, HIT_K, device, beta, n_iter, vote_projs)

    R_ = MAX_REACH
    hop1_high = bool(fid[NO_CLEANUP][1] >= 0.55)
    baseline_fails = bool(fid[NO_CLEANUP][R_] <= 0.70 * fid[NO_CLEANUP][1])
    dense_sharpens = bool(fid[DENSE_HOPFIELD][R_] >= fid[PLAIN_CLEANUP][R_] - 0.02)  # dense >= plain (within noise)
    path_composes = bool(fid[PATH_AS_OBJECT][2] > 10.0 * HIT_K / n)                   # > 10x chance at reach 2
    vote_valid = bool(fid[COMBINED_WIN_VOTED][1] >= 0.30)                             # voted readout recovers hop-1
    arms_differ = bool(len(set(sigs.values())) >= 2)

    # D_f/N for the planted config
    load = n / db
    above_thresh = bool(load > RESONATOR_THRESH)

    res = dict(
        fid_no_cleanup={dd: round(fid[NO_CLEANUP][dd], 4) for dd in range(1, R_ + 1)},
        fid_plain={dd: round(fid[PLAIN_CLEANUP][dd], 4) for dd in range(1, R_ + 1)},
        fid_dense={dd: round(fid[DENSE_HOPFIELD][dd], 4) for dd in range(1, R_ + 1)},
        fid_path={dd: round(fid[PATH_AS_OBJECT][dd], 4) for dd in range(1, R_ + 1)},
        fid_voted={dd: round(fid[COMBINED_WIN_VOTED][dd], 4) for dd in range(1, R_ + 1)},
        hop1_high=hop1_high, baseline_fails=baseline_fails, dense_sharpens=dense_sharpens,
        path_composes=path_composes, vote_valid=vote_valid, arms_differ=arms_differ,
        df_load=float(load), df_above_thresh=above_thresh,
    )
    ok = bool(hop1_high and baseline_fails and dense_sharpens and path_composes and vote_valid and arms_differ)
    return ok, res


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    if args.self_test:
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = args.run_mode

    device = _resolve_device(args.device)
    output_dir = str(get_output_dir(ANCHOR_NAME))
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    expected_n_units = len(cfg["seeds"])
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    _log("device=%s cuda_available=%s run_mode=%s" % (device, torch.cuda.is_available(), run_mode))

    st_ok, st_res = _mechanism_selftest()
    _log("mechanism_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (hop1/baseline_fails/dense/path/vote/arms_differ): %s" % st_res,
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res))
        raise SystemExit(1)

    _log("loading typed ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(
        cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    _log("subgraph: %s | rel_types=%d" % ({k: meta[k] for k in ("n_nodes", "n_edges", "median_degree")}, T))
    n_nodes = len(node_ids)
    X = char_trigram_features(node_words, cfg["feat_dim"])
    dir_adj = build_typed_diradj(edges, rels, n_nodes)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS decisive-win chain machinery: NO_CLEANUP collapses at reach>=2 (must-fail "
                        "control fires), dense-Hopfield sharpens, path-object composes, voted readout valid, arms "
                        "differ; D_f/N load computed; typed subgraph + 3-dim encoders exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res, subgraph_meta=meta))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, X, edges, rels, dir_adj, cfg, device, out_dir=out_dir_path)
            for a in ARMS:
                missing = [dd for dd in range(1, MAX_REACH + 1) if dd not in pm["arms"][a]["fid"]]
                if a not in pm["arms"] or missing:
                    raise RuntimeError("ARM_DEPTH_CARDINALITY_BREACH seed=%d arm=%s missing=%s" % (seed, a, missing))
            if len(set(pm["arm_sigs"].values())) < 2:
                _log("  [warn] arm hit-signatures collapsed to <2 distinct (seed=%d)" % seed)
            # WIN arms must differ from NO_CLEANUP (META_RULE_AF, scoped)
            for a in WIN_ARMS:
                if pm["arm_sigs"][a] == pm["arm_sigs"][NO_CLEANUP]:
                    raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d %s == NO_CLEANUP" % (seed, a))
            per_seed.append(pm)
            write_partial(out_dir_path, seed, dict(seed=seed, metrics=pm))
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
            seed_failures=seed_failures, subgraph_meta=meta))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, meta, cfg, run_mode)
    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        device=str(device), n_seeds=len(per_seed), seeds=cfg["seeds"], config=cfg,
        subgraph_meta=meta, gates=gates,
        mechanism_selftest=st_res, seed_failures=seed_failures, per_seed=per_seed,
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
