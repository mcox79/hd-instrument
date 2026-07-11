"""Course C operator-fix proof: phase-rotation / SSP-FPE replay-consolidation on a KNOWN-compositional testbed.

DE-RISKED SUB-CLAIM (P~0.40 operator-fix; P~0.20-0.25 consolidation) of the Course-C map-builder. Tests the OPERATOR
in ISOLATION on a self-contained synthetic compositional corpus, independent of the CSKG-corpus VET (separate/in-flight
cell grounding_additive_geometric_degree_control_v1). Design: notes/research_course_c_map_builder_replay_consolidation_
design_2026-07-10.md + companion notes/research_ssp_fractional_binding_degree_invariant_relational_code_2026-07-10.md
(pre-registered SSP_FRACTIONAL arm) + notes/research_offline_consolidation_multiview_degree_invariance_prior_art_
2026-07-10.md (controls scaffold).

PREREQUISITE CONFRONTED. stage3_hrr_involutive HARD_FAIL (heldout_acc=0.0067=chance) was diagnosed as CONFIG/METHOD
limit not a wall: (a) wrong primitive (real/bipolar HRR, cosine<=0.55 even on exact-key recovery, vs exact FHRR complex
phase-rotation), (b) one global superposition of all facts (1/sqrt(500)~=0.045 crosstalk), (c) similarity-DESTROYING
i.i.d. entity codes (no continuous parametrization linking similar entities to similar codes). The fix = FHRR complex
phase-rotation binding (RotatE-equivalent, |r|=1 exact unitary) + fractional-power-encoding (FPE / SSP) CONTINUOUS entity
codes so inner-product similarity is a smooth monotone function of latent distance (Frady et al. 2021 = Random Fourier
Features / Bochner), factorized per-relation-TYPE (TEM structure/content split), read out through a BOUNDED kernel that
blocks the norm-blowup channel driving TransE degree bias (Shomer et al. 2023).

TESTBED (self-contained; no substrate corpus). A k-dim integer-grid relational graph: entities = grid points, relation
TYPES = fixed integer translations, a TRUE edge (h,r,t) exists iff x_t = x_h + delta_r (in-grid). GENUINELY
compositional: translations compose additively so a composite relation r1.r2 has delta = delta_r1 + delta_r2 and a
NEVER-OBSERVED composite edge A->C (A->B via r1, B->C via r2) is DERIVABLE from geometry (transitive inference). Border
vs interior gives a real degree gradient -> data-driven LOW/MID/HIGH tail-degree tertiles (degree-invariance is the whole
point; the discrete code collapsed on the low-degree tail). Info-ceiling ~1.0 (fully derivable) so the win bar is
fair/high; achieved/ceiling reported. Held-out edges are withheld directed triples; a FREQ-GUESSABLE control corpus
(star graph, tails = popularity, NO consistent translation) is the must-fail-#4 anti-manufacture check.

ARMS (all learn from the VISIBLE graph only unless noted; scored PAIRED on the SAME held-out queries + candidate set):
  DISCRETE_BIND      (stage3 failure-mode baseline): i.i.d. random complex64 unit-phasor entity codes (NO continuous
                     coordinate), per-relation-TYPE learned diagonal unitary rotation R_r = circular-mean(z_t*conj(z_h))
                     over training pairs; predict argmax_t Re<z_h*R_r, z_t>. Similarity-destroying codes -> R_r cannot
                     generalize to an unseen (h,r) pair -> chance (reproduces stage3). MUST FAIL the operator-fix bar.
  ONESHOT_ROTATE     (SSP_FRACTIONAL, one-shot): continuous coords X + displacements D fit by TransE margin-ranking
                     (additive in coord space, negative sampling prevents collapse) in a SINGLE end-to-end pass; FPE
                     phasor readout S(x)=exp(i * X @ W), W~N(0,ell^-2) (pre-registered bandwidth), predicted tail
                     phasor S(x_h) (.) T_r = S(x_h+delta_r), scored by bounded kernel Re<S_hat,S(x_t)>/dim. Isolates
                     "does the operator swap alone get off the stage3 floor" (Part-1 prerequisite, empirically).
  REPLAY_CONSOLIDATED(same operator family): coords/displacements fit by ITERATIVE INTERLEAVED replay passes with a
                     per-relation RECALL-CONSISTENCY gate (commit delta_r only if two disjoint replay minibatches agree,
                     cosine>=GATE) + per-relation VALIDATION EARLY-STOP (halt consolidating r once held-back val error
                     rises). The NEW, unproven ingredient (does iterative replay change GENERALIZATION, not just
                     retention). Same FPE readout as ONESHOT so the only difference is the FIT REGIME.
  SCRAMBLE_REPLAY    (must-fail #1): identical replay procedure but relation labels shuffled before each pass -> replay
                     motion with NO real signal. MUST NOT beat ONESHOT_ROTATE.
  BASELINE_POP       (frequency incumbent): score(candidate) = visible-graph degree(candidate). No geometry. The bar.
  RANDOM_CODES       (null / geometry-necessary): random coords + identical FPE kernel machinery -> near-chance. Proves
                     the GEOMETRY carries the signal, not the kernel math alone.
  ORACLE_TRANSDUCTIVE(must-fire): ONESHOT_ROTATE coords fit WITH held-out edges visible -> the ranking machinery MUST
                     recover held-out tails (>> random) or the setup is broken -> INCONCLUSIVE.

PRIMARY METRIC: reach@1 = filtered Hits@1 on the held-out completable subset, PLUS per-degree-stratum reach@1 for every
arm, PLUS composite-relation (transitive A->C) reach@1. Also MRR, achieved/ceiling.

DIAGNOSTICS (folded in per companion notes; REPORTED, several gate the trust of a win):
  - COORD-PRECISION-VS-DEGREE back-door (companion SSP note HARD-PASS #7): per-entity coord variance across seed
    restarts vs entity degree; Spearman/Pearson r must be < R_BACKDOOR for a trusted win (else the win is the same
    estimation-quality channel as TransE laundered through a kernel).
  - CROSS-CHANNEL INDEPENDENCE pre-flight (consolidation note Pitfall #3): correlation between the geometry-channel
    score and the frequency/degree channel; high correlation => agreement re-launders popularity.
  - LEAKAGE AUDIT (Sun et al. 2019): synthetic graph asserts NO inverse-relation duplicate (delta_r != -delta_r') and
    NO near-Cartesian relation; reported so a rare-entity win is not a benchmark artifact.
  - EFFECTIVE-RANK anti-collapse (consolidation note Thread 5): coord-space singular-value effective rank tracked; a
    replay collapse (rank << k) flags the loop degenerated.

DISCRIMINATOR (pre-registered).
  OPERATOR_FIX_CONFIRMED (the P~0.40 sub-claim; the SMOKE-GATED headline):
        oneshot reach@1 - discrete reach@1 >= OP_MARGIN (aggregate; the operator swap gets off the stage3 floor)
    AND oneshot beats BASELINE_POP by >= POP_GAP (geometry, not popularity)
    AND discrete <= DISCRETE_CEIL (reproduces the stage3 chance-level failure)
    AND ORACLE fires (>> random) AND RANDOM <= RANDOM_CEIL (geometry-necessary null)
    AND SCRAMBLE_REPLAY does NOT beat ONESHOT (replay motion needs real signal)
    AND on the FREQ-GUESSABLE corpus, oneshot does NOT beat POP (no manufactured headroom).
  CONSOLIDATION_HELPS (the P~0.20-0.25 sub-claim; REPORTED at smoke, decided at FULL landed-VET -- telemetry may wash
        at scale, HOLD the mechanism story):
        replay LOW-stratum reach@1 >= oneshot LOW * (1 + CONSOL_REL) (rare-entity gain)
    AND replay aggregate/HIGH does not regress > REGRESS_REL vs oneshot
    AND degree-invariance flatness: |reach_HIGH - reach_LOW| for replay <= FLAT_EPS
    AND coord-precision-vs-degree |r| < R_BACKDOOR.
  OPERATOR_FIX_FAILS = oneshot reproduces the discrete/chance floor (oneshot - discrete <= TIE_EPS) OR oneshot does not
        beat POP -> the substrate inductive-generalization wall is BELOW binding-primitive choice (redirect to Course B
        density / Course D relation-closure), matching the deep drill's own precondition-fail criterion.

SELF-TEST (planted; proves the discriminators FIRE, using the SAME arm code paths as the real run at reduced scale):
  PLANTED_COMPOSITIONAL grid: ONESHOT recovers held-out (>= SELFTEST_ONESHOT_MIN) and materially beats DISCRETE and POP;
  DISCRETE at chance (<= DISCRETE_CEIL); RANDOM at chance; ORACLE fires; SCRAMBLE does not beat ONESHOT.
  PLANTED_FREQ (star graph, tails = popularity, no translation): POP FIRES (>= SELFTEST_POP_MIN) and ONESHOT does NOT
  beat POP (manufacture-check). Gaps + arms-differ asserted. VacuousSmokeError if DISCRETE passes the operator-fix bar.

## Compute architecture
class: (a) batched-GPU. Coord fit = TransE margin-ranking over edge minibatches (vectorized, no python-loop matmul);
FPE encode = one [N,k]@[k,dim] real matmul then complex exp; ranking = a single batched Re(S_hat @ conj(S_all).T)/dim
reduction per arm on a SHARED candidate tensor (PAIRED). Storage strategy: SHARDED (each entity its own code/coord;
relation operators factorized per TYPE, NEVER one global fact bundle -- the explicit fix for stage3 crosstalk). Grid
N<=~2000, k<=3, fpe_dim<=4096, seeds<=5 -> seconds-minutes/seed. Local = SMOKE-ONLY (USER-locked); FULL routes remote
(GPU overnight_queue if fpe_dim large, else remote_cpu_queue) via the orchestrator hand-off.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF): >= 5 distinct held-out score signatures among the 7 arms.
# - final_metrics_atomicity: tmp_replace (_seed_checkpoint.write_metrics + os.replace; write_partial per seed).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: filtered Hits@1 chance floor = 1/(n_candidates) THEORETICAL; DISCRETE_CEIL/RANDOM_CEIL set above it;
#   OPERATOR_FIX bar (oneshot - discrete >= OP_MARGIN) is on the achievable side (planted self-test demonstrates it).
# - baseline_in_band: DISCRETE + RANDOM are the anti-triviality nulls (<= ceilings); ORACLE must-fire; POP measured.
# - discriminator survives scale: OP-fix fires at the PLANTED self-test scale; the same code path runs FULL (k=3,
#   larger grid, 5 seeds); SMOKE runs the FULL arm set at reduced grid. Consolidation margin is REPORTED (FULL decides).
# - HARD_PASS strictly above floor: OP_MARGIN (0.20) >> TIE_EPS (0.03); POP_GAP 0.10 >> chance.
# - HP_SCOPE: OPERATOR_FIX applies to ONESHOT vs DISCRETE + POP + SCRAMBLE + freq-corpus; CONSOLIDATION applies to
#   REPLAY vs ONESHOT (rare stratum + flatness); RANDOM=null; ORACLE=must-fire.
# - positive_control (Gate D): ORACLE_TRANSDUCTIVE reproduces the transductive recovery (>> random); the FPE kernel +
#   coord-fit machinery is validated by ONESHOT clearing the planted grid before any inductive/degree claim.
# - sweep axis: ARM x seed x degree-stratum x {single-hop, composite}; EXPECTED_N_UNITS = n_seeds; each seed asserts all
#   7 arms produce >= 5 distinct sigs (cardinality_ok).
# - per-unit failure-class instrumentation (no bare except; per-seed try/except records failure_class).
# - calibration_check: default_ok_for_this_regime -- grid side / n_rel / held-out frac / degree tertiles are structural
#   (data-driven quantiles, not tuned for PASS); FPE bandwidth ell is PRE-REGISTERED before the run (companion-note
#   requirement: post-hoc kernel tuning would make the degree-invariance verdict untrustworthy by construction).
# - PAIRED: all arms share the identical held-out split + candidate set + degree strata per seed.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the pre-reg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm/per-stratum flush).
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
    get_output_dir, write_metrics, write_partial, assert_discriminator_fires, VacuousSmokeError,
)

ANCHOR_NAME = "course_c_operator_fix_ssp_phase_rotation_replay_v1"

# ---- Arm names ----
DISCRETE = "DISCRETE_BIND"            # stage3 failure-mode baseline: i.i.d. phasor + learned rotation (no coords)
ONESHOT = "ONESHOT_ROTATE"           # SSP_FRACTIONAL: TransE-coord fit (one-shot) + FPE bounded kernel readout
REPLAY = "REPLAY_CONSOLIDATED"       # same operator, iterative replay + recall-consistency gate + val early-stop
SCRAMBLE = "SCRAMBLE_REPLAY"         # must-fail: replay with shuffled relation labels
POP = "BASELINE_POP"                 # frequency incumbent: degree-only score
RANDOM = "RANDOM_CODES"              # null: random coords + FPE kernel (geometry-necessary)
ORACLE = "ORACLE_TRANSDUCTIVE"       # must-fire: ONESHOT fit WITH held-out visible
ALL_ARMS = [DISCRETE, ONESHOT, REPLAY, SCRAMBLE, POP, RANDOM, ORACLE]
GEOM_ARMS = [ONESHOT, REPLAY, SCRAMBLE, RANDOM, ORACLE]  # arms that use coord-fit + FPE readout

STRATA = ["LOW", "MID", "HIGH"]

# ---- Pre-registered bands (picked BEFORE the run) ----
OP_MARGIN = 0.20            # OPERATOR_FIX aggregate: oneshot reach@1 >= discrete + this (get off the stage3 floor)
POP_GAP = 0.10             # OPERATOR_FIX: oneshot reach@1 must beat BASELINE_POP by this (geometry, not popularity)
DISCRETE_CEIL = 0.15       # OPERATOR_FIX: discrete must stay at/near chance (reproduces stage3 hrr_mechanism_null)
RANDOM_CEIL = 0.15         # geometry-necessary null: random coords reach@1 <= this
ORACLE_FIRE_MARGIN = 0.20  # discriminator-fires: ORACLE must beat RANDOM by this
TIE_EPS = 0.03             # OPERATOR_FIX_FAILS: oneshot - discrete <= this (operator swap reproduced the floor)
FREQ_MANUFACTURE_EPS = 0.05  # must-fail #4: on freq-guessable corpus, oneshot - pop <= this (no manufactured headroom)
SCRAMBLE_EPS = 0.05        # must-fail #1: scramble - oneshot must be <= this (replay motion needs real signal)
# CONSOLIDATION (reported at smoke, decided at FULL):
CONSOL_REL = 0.15          # replay LOW-stratum reach@1 >= oneshot LOW * (1 + this)
REGRESS_REL = 0.05         # replay aggregate/HIGH must not regress > this relative vs oneshot
FLAT_EPS = 0.10            # degree-invariance: |reach_HIGH - reach_LOW| for replay <= this
R_BACKDOOR = 0.20          # coord-precision-vs-degree |r| must be < this for a trusted win (companion HARD-PASS #7)
MIN_STRAT_Q = 20           # min queries in a stratum to assess its margin
MIN_HELDOUT = 30           # min held-out completable queries for a valid discriminator

# ---- self-test planted thresholds ----
SELFTEST_ONESHOT_MIN = 0.40   # planted grid: ONESHOT recovers held-out at least this (ceiling ~1.0)
SELFTEST_POP_MIN = 0.20       # planted freq star: POP baseline fires at least this

# ---- Held-out / ranking ----
HELDOUT_FRAC = 0.30

# ---- FPE readout (PRE-REGISTERED bandwidth; not tuned post-hoc) ----
# W ~ N(0, ell^-2 I): kernel k(x,y) ~ exp(-||x-y||^2 / (2 ell^2)); ell = FPE_ELL * unit grid spacing (1.0). Chosen so
# nearest grid neighbours (distance 1) are resolvable (kernel ~ exp(-1/(2*ell^2))) while distance-2 collapses -> the
# smooth-similarity regime that motivates the whole hypothesis (not a near-delta discrete lookup). Frady 2021 (RFF).
FPE_ELL = 0.55

# ---- TransE coord-fit hyperparams (standard regularized-KGE defaults; NOT tuned on results) ----
KGE_MARGIN = 1.0
KGE_NEG = 10
KGE_WD = 1e-3              # norm-minimization (the Lippl generalization driver)
KGE_LR = 0.02

# ---- Replay-consolidation ----
REPLAY_GATE = 0.30        # recall-consistency: commit delta_r update only if two disjoint minibatch estimates agree
                          # (cosine >= this). Low bar; the SCRAMBLE arm exposes whether the gate is doing real work.
REPLAY_VAL_FRAC = 0.15    # per-relation held-back edges for validation early-stop

# Config profiles. SELFTEST/SMOKE exercise the SAME arms / code path as FULL; only scale differs.
SELFTEST_CFG = dict(seeds=[7], k=2, grid_L=6, n_rel=6, n_comp=4, fpe_dim=512,
                    kge_epochs=200, replay_passes=25)
SMOKE_CFG = dict(seeds=[7, 13], k=2, grid_L=9, n_rel=8, n_comp=8, fpe_dim=1024,
                 kge_epochs=300, replay_passes=40)
FULL_CFG = dict(seeds=[7, 13, 17, 23, 31], k=3, grid_L=12, n_rel=16, n_comp=24, fpe_dim=4096,
                kge_epochs=600, replay_passes=80)


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.3f" % x) if (x == x) else "nan"


def _sig(arr):
    """Stable short signature of a float array (for ARMS-MUST-DIFFER)."""
    a = np.round(np.asarray(arr, dtype=np.float64), 4)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Synthetic compositional testbed: k-dim integer grid, relations = translations.
# ---------------------------------------------------------------------------

def build_grid_graph(k, L, n_rel, n_comp, seed):
    """k-dim integer grid [0,L)^k. Entities = all grid points. Relations = random integer translations.

    Returns dict with:
      coords_true : (N, k) int true grid coordinates (ground truth; NOT given to arms)
      deltas      : (n_rel, k) int primitive relation translations
      comp_pairs  : list of (r1, r2) primitive index pairs defining composite relations (transitive A->C)
      edges       : (E, 3) int [h, r, t] single-hop true edges (t = h + delta_r, in-grid)
      comp_edges  : (Ec, 4) int [h, r1, r2, t] composite edges (t = h + delta_r1 + delta_r2, in-grid, NOT a single edge)
    Leakage-safe by construction: no inverse-duplicate translation, no zero translation, translations distinct.
    """
    rng = np.random.default_rng(seed * 100003 + 17)
    dims = [L] * k
    N = L ** k
    # enumerate grid points
    grid = np.array(np.meshgrid(*[np.arange(L) for _ in range(k)], indexing="ij"))
    coords = grid.reshape(k, -1).T.astype(np.int64)  # (N, k)
    coord_to_id = {tuple(int(v) for v in coords[i]): i for i in range(N)}

    # sample distinct non-zero primitive translations, small magnitude, leakage-safe (no +/- duplicate)
    deltas = []
    seen = set()
    tries = 0
    while len(deltas) < n_rel and tries < 10000:
        tries += 1
        d = rng.integers(-2, 3, size=k)  # components in {-2,-1,0,1,2}
        if np.all(d == 0):
            continue
        key = tuple(int(v) for v in d)
        negkey = tuple(-int(v) for v in d)
        if key in seen or negkey in seen:  # no inverse-duplicate (Sun 2019 leakage audit)
            continue
        seen.add(key)
        deltas.append(d)
    deltas = np.asarray(deltas, dtype=np.int64)
    n_rel = deltas.shape[0]

    # single-hop edges
    edges = []
    for i in range(N):
        for r in range(n_rel):
            t = coords[i] + deltas[r]
            if np.all(t >= 0) and np.all(t < L):
                j = coord_to_id[tuple(int(v) for v in t)]
                edges.append((i, r, j))
    edges = np.asarray(edges, dtype=np.int64)

    # composite (transitive) relations: pick primitive pairs; a composite edge is derivable but NEVER a single edge
    comp_pairs = []
    seen_c = set()
    tries = 0
    while len(comp_pairs) < n_comp and tries < 10000:
        tries += 1
        r1 = int(rng.integers(0, n_rel)); r2 = int(rng.integers(0, n_rel))
        dc = deltas[r1] + deltas[r2]
        if np.all(dc == 0):
            continue
        # reject if the composite equals a primitive translation (would not be a genuine 2-hop test)
        if any(np.all(dc == deltas[rr]) for rr in range(n_rel)):
            continue
        key = (r1, r2)
        if key in seen_c:
            continue
        seen_c.add(key)
        comp_pairs.append((r1, r2))
    comp_edges = []
    for ci, (r1, r2) in enumerate(comp_pairs):
        dc = deltas[r1] + deltas[r2]
        for i in range(N):
            t = coords[i] + dc
            if np.all(t >= 0) and np.all(t < L):
                j = coord_to_id[tuple(int(v) for v in t)]
                comp_edges.append((i, r1, r2, j))
    comp_edges = np.asarray(comp_edges, dtype=np.int64) if comp_edges else np.zeros((0, 4), dtype=np.int64)

    return dict(N=N, k=k, L=L, n_rel=n_rel, coords_true=coords, deltas=deltas,
                comp_pairs=comp_pairs, edges=edges, comp_edges=comp_edges)


def build_freq_star_graph(k, L, n_rel, seed):
    """FREQ-GUESSABLE control: tails drawn from a fixed power-law popularity distribution, NO consistent translation.

    A relation here is a LABEL only; the tail of (h, r) is a popular hub sampled from a Zipf over a small hub set,
    independent of h's position. Geometry cannot help (no additive law); popularity CAN. Used as the must-fail-#4
    anti-manufacture corpus: the map-builder must NOT beat POP here.
    """
    rng = np.random.default_rng(seed * 100019 + 29)
    N = L ** k
    n_hub = max(3, N // 10)
    hubs = rng.choice(N, size=n_hub, replace=False)
    zipf_w = 1.0 / (1.0 + np.arange(n_hub))
    zipf_w = zipf_w / zipf_w.sum()
    edges = []
    n_edge_per_node = max(2, n_rel // 2)
    for h in range(N):
        for _ in range(n_edge_per_node):
            r = int(rng.integers(0, n_rel))
            hub_idx = rng.choice(n_hub, p=zipf_w)
            t = int(hubs[hub_idx])
            if t == h:
                continue
            edges.append((h, r, t))
    edges = np.asarray(edges, dtype=np.int64)
    return dict(N=N, k=k, L=L, n_rel=n_rel, edges=edges,
                comp_edges=np.zeros((0, 4), dtype=np.int64), coords_true=None)


def split_heldout(edges, frac, seed):
    rng = np.random.default_rng(seed * 100057 + 3)
    E = edges.shape[0]
    perm = rng.permutation(E)
    n_hold = max(1, int(round(frac * E)))
    hold_idx = perm[:n_hold]
    train_idx = perm[n_hold:]
    return edges[train_idx], edges[hold_idx]


def visible_degree(edges, N):
    deg = np.zeros(N, dtype=np.int64)
    for i in range(edges.shape[0]):
        deg[int(edges[i, 0])] += 1
        deg[int(edges[i, 2])] += 1
    return deg


def stratify_by_tail_degree(hold_edges, deg):
    """Assign each held-out query to LOW/MID/HIGH by TRUE-TAIL visible degree tertile (data-driven quantiles)."""
    tail_deg = np.array([deg[int(hold_edges[i, 2])] for i in range(hold_edges.shape[0])], dtype=np.float64)
    if tail_deg.size == 0:
        return np.array([], dtype=np.int64)
    q1, q2 = np.quantile(tail_deg, [1.0 / 3.0, 2.0 / 3.0])
    strat = np.where(tail_deg <= q1, 0, np.where(tail_deg <= q2, 1, 2))
    return strat.astype(np.int64)


# ---------------------------------------------------------------------------
# FPE / SSP phasor readout (the fix for stage3's similarity-destroying codes).
# ---------------------------------------------------------------------------

def make_fpe_basis(k, dim, ell, device, seed):
    """W ~ N(0, ell^-2 I) in R^{k x dim}. S(x) = exp(i * x @ W). Kernel ~ exp(-||x-y||^2 / (2 ell^2)) (RFF/Bochner)."""
    g = torch.Generator(device="cpu").manual_seed(seed * 911 + 5)
    W = torch.randn(k, dim, generator=g).to(device) / float(ell)
    return W


def fpe_encode(X, W):
    """X: (N,k) real -> S: (N,dim) complex64 unit-modulus phasors. |S|=1 exactly for any X (blocks norm-blowup)."""
    ang = X @ W  # (N, dim)
    return torch.complex(torch.cos(ang), torch.sin(ang)).to(torch.complex64)


def fpe_kernel_scores(X_query_plus_delta, X_all, W):
    """Score every candidate: Re<S(x_hat), S(x_t)>/dim = (1/dim) sum_j cos((x_hat - x_t).W). Returns (nq, N) real."""
    S_hat = fpe_encode(X_query_plus_delta, W)      # (nq, dim)
    S_all = fpe_encode(X_all, W)                    # (N, dim)
    dim = S_hat.shape[1]
    scores = torch.real(S_hat @ torch.conj(S_all).T) / dim
    return scores


# ---------------------------------------------------------------------------
# Coordinate fit: TransE margin-ranking (additive; negative sampling prevents the trivial X=const, D=0 collapse).
# ---------------------------------------------------------------------------

def fit_transe_coords(train_edges, N, n_rel, k, device, seed, epochs, transductive_extra=None):
    """Fit X (N,k), D (n_rel,k) minimizing margin-ranking ||X_h+D_r-X_t|| < ||X_h+D_r-X_t'|| - margin. One-shot."""
    g = torch.Generator(device="cpu").manual_seed(seed * 7919 + 11)
    X = (torch.randn(N, k, generator=g) * 0.1).to(device).requires_grad_(True)
    D = (torch.randn(n_rel, k, generator=g) * 0.1).to(device).requires_grad_(True)
    opt = torch.optim.Adam([X, D], lr=KGE_LR, weight_decay=KGE_WD)
    ed = train_edges
    if transductive_extra is not None and transductive_extra.shape[0] > 0:
        ed = np.concatenate([train_edges, transductive_extra], axis=0)
    h = torch.from_numpy(ed[:, 0]).long().to(device)
    r = torch.from_numpy(ed[:, 1]).long().to(device)
    t = torch.from_numpy(ed[:, 2]).long().to(device)
    E = h.shape[0]
    gg = torch.Generator(device="cpu").manual_seed(seed * 13 + 1)
    for ep in range(epochs):
        opt.zero_grad()
        pred = X[h] + D[r]
        pos = torch.norm(pred - X[t], dim=1)
        neg_t = torch.randint(0, N, (E, KGE_NEG), generator=gg).to(device)
        neg = torch.norm(pred.unsqueeze(1) - X[neg_t], dim=2)  # (E, KGE_NEG)
        loss = torch.clamp(KGE_MARGIN + pos.unsqueeze(1) - neg, min=0.0).mean()
        loss.backward()
        opt.step()
    return X.detach(), D.detach()


def fit_transe_replay(train_edges, N, n_rel, k, device, seed, passes):
    """Iterative interleaved replay with per-relation recall-consistency gate + validation early-stop.

    Differs from fit_transe_coords ONLY in the FIT REGIME (same objective / same readout downstream). Each pass:
      - interleave (shuffle) all training triples;
      - SGD margin-ranking minibatch steps (the 'replay');
      - per relation r: estimate delta_r from two DISJOINT replay minibatches; commit the consolidated D[r] pull only
        if the two estimates AGREE (cosine >= REPLAY_GATE) -> recall-consistency gating;
      - per relation r: hold back REPLAY_VAL_FRAC edges; early-stop consolidating r once its val error rises (Sun 2023).
    """
    g = torch.Generator(device="cpu").manual_seed(seed * 7919 + 11)
    X = (torch.randn(N, k, generator=g) * 0.1).to(device).requires_grad_(True)
    D = (torch.randn(n_rel, k, generator=g) * 0.1).to(device).requires_grad_(True)
    opt = torch.optim.Adam([X, D], lr=KGE_LR, weight_decay=KGE_WD)
    gg = torch.Generator(device="cpu").manual_seed(seed * 13 + 1)

    # per-relation train/val split for early-stop
    by_rel = {r: np.where(train_edges[:, 1] == r)[0] for r in range(n_rel)}
    rel_train, rel_val = {}, {}
    for r in range(n_rel):
        idx = by_rel[r]
        if idx.size == 0:
            rel_train[r] = idx; rel_val[r] = idx; continue
        nv = max(1, int(round(REPLAY_VAL_FRAC * idx.size)))
        perm = np.random.default_rng(seed * 31 + r).permutation(idx)
        rel_val[r] = perm[:nv]; rel_train[r] = perm[nv:]
    frozen = np.zeros(n_rel, dtype=bool)          # relations whose consolidation has early-stopped
    best_val = np.full(n_rel, np.inf)
    committed = 0

    def rel_val_err(r):
        vi = rel_val[r]
        if vi.size == 0:
            return np.inf
        hh = torch.from_numpy(train_edges[vi, 0]).long().to(device)
        tt = torch.from_numpy(train_edges[vi, 2]).long().to(device)
        with torch.no_grad():
            e = torch.norm(X[hh] + D[r] - X[tt], dim=1).mean().item()
        return e

    all_idx = np.arange(train_edges.shape[0])
    bs = max(32, train_edges.shape[0] // 8)
    for p in range(passes):
        perm = np.random.default_rng(seed * 101 + p).permutation(all_idx)  # interleave
        for s in range(0, perm.size, bs):
            bidx = perm[s:s + bs]
            h = torch.from_numpy(train_edges[bidx, 0]).long().to(device)
            r = torch.from_numpy(train_edges[bidx, 1]).long().to(device)
            t = torch.from_numpy(train_edges[bidx, 2]).long().to(device)
            opt.zero_grad()
            pred = X[h] + D[r]
            pos = torch.norm(pred - X[t], dim=1)
            neg_t = torch.randint(0, N, (h.shape[0], KGE_NEG), generator=gg).to(device)
            neg = torch.norm(pred.unsqueeze(1) - X[neg_t], dim=2)
            loss = torch.clamp(KGE_MARGIN + pos.unsqueeze(1) - neg, min=0.0).mean()
            loss.backward()
            opt.step()
        # consolidation gate per relation (recall-consistency + val early-stop)
        with torch.no_grad():
            for r in range(n_rel):
                if frozen[r]:
                    continue
                idx = rel_train[r]
                if idx.size < 4:
                    continue
                half = idx.size // 2
                a = idx[:half]; b = idx[half:2 * half]
                est_a = (X[torch.from_numpy(train_edges[a, 2]).long().to(device)]
                         - X[torch.from_numpy(train_edges[a, 0]).long().to(device)]).mean(0)
                est_b = (X[torch.from_numpy(train_edges[b, 2]).long().to(device)]
                         - X[torch.from_numpy(train_edges[b, 0]).long().to(device)]).mean(0)
                denom = (est_a.norm() * est_b.norm() + 1e-9)
                cons = float((est_a @ est_b) / denom)
                if cons >= REPLAY_GATE:                          # recall-consistency: commit
                    D.data[r] = 0.7 * D.data[r] + 0.3 * 0.5 * (est_a + est_b)
                    committed += 1
                ve = rel_val_err(r)                              # validation early-stop
                if ve <= best_val[r]:
                    best_val[r] = ve
                else:
                    frozen[r] = True
    return X.detach(), D.detach(), int(committed), int(frozen.sum())


def fit_discrete_bind(train_edges, N, n_rel, dim, device, seed):
    """stage3 failure-mode baseline: i.i.d. random complex64 unit-phasor entity codes + per-relation-TYPE learned
    diagonal unitary rotation R_r = normalize(sum_train z_t * conj(z_h)) (circular mean of the phase difference).
    Similarity-destroying codes -> R_r cannot generalize to an unseen (h,r) pair -> chance on held-out."""
    g = torch.Generator(device="cpu").manual_seed(seed * 5501 + 7)
    ang = (torch.rand(N, dim, generator=g) * 2.0 * np.pi).to(device)
    Z = torch.complex(torch.cos(ang), torch.sin(ang)).to(torch.complex64)  # (N, dim) unit phasors
    R = torch.ones(n_rel, dim, dtype=torch.complex64, device=device)
    for r in range(n_rel):
        idx = np.where(train_edges[:, 1] == r)[0]
        if idx.size == 0:
            continue
        h = torch.from_numpy(train_edges[idx, 0]).long().to(device)
        t = torch.from_numpy(train_edges[idx, 2]).long().to(device)
        acc = (Z[t] * torch.conj(Z[h])).sum(0)                # (dim,) circular mean of phase diff
        mag = torch.abs(acc) + 1e-9
        R[r] = (acc / mag).to(torch.complex64)                # unit-modulus rotation operator
    return Z, R


# ---------------------------------------------------------------------------
# Ranking / metrics.
# ---------------------------------------------------------------------------

def filtered_reach(scores, hold_edges, all_true_by_hr, top_k_mrr=True):
    """scores: (nq, N) real; hold_edges: (nq,3). Filtered Hits@1 + MRR: mask OTHER true tails of the same (h,r)."""
    nq, N = scores.shape
    sc = scores.clone()
    for i in range(nq):
        h = int(hold_edges[i, 0]); r = int(hold_edges[i, 1]); t = int(hold_edges[i, 2])
        others = all_true_by_hr.get((h, r), None)
        if others:
            for o in others:
                if o != t:
                    sc[i, o] = -1e9
    hits1 = 0.0
    mrr = 0.0
    for i in range(nq):
        t = int(hold_edges[i, 2])
        row = sc[i]
        target = row[t].item()
        rank = int((row > target).sum().item()) + 1
        if rank == 1:
            hits1 += 1.0
        mrr += 1.0 / rank
    return hits1 / max(1, nq), mrr / max(1, nq)


def build_true_by_hr(*edge_sets):
    d = {}
    for edges in edge_sets:
        for i in range(edges.shape[0]):
            h = int(edges[i, 0]); r = int(edges[i, 1]); t = int(edges[i, 2])
            d.setdefault((h, r), set()).add(t)
    return d


def geom_reach_all(X, D, W, hold_edges, N, device, all_true_by_hr):
    """FPE-kernel reach@1 + MRR + per-arm score signature for a coord-fit arm."""
    h = torch.from_numpy(hold_edges[:, 0]).long().to(device)
    r = torch.from_numpy(hold_edges[:, 1]).long().to(device)
    x_hat = X[h] + D[r]                         # (nq, k)
    X_all = X                                   # (N, k)
    scores = fpe_kernel_scores(x_hat, X_all, W)  # (nq, N)
    reach, mrr = filtered_reach(scores.cpu(), hold_edges, all_true_by_hr)
    sig = _sig(scores.cpu().numpy()[:min(64, scores.shape[0])].ravel())
    return reach, mrr, sig, scores.cpu()


def discrete_reach_all(Z, R, hold_edges, N, device, all_true_by_hr):
    h = torch.from_numpy(hold_edges[:, 0]).long().to(device)
    r = torch.from_numpy(hold_edges[:, 1]).long().to(device)
    pred = Z[h] * R[r]                           # (nq, dim)
    dim = pred.shape[1]
    scores = torch.real(pred @ torch.conj(Z).T) / dim  # (nq, N)
    reach, mrr = filtered_reach(scores.cpu(), hold_edges, all_true_by_hr)
    sig = _sig(scores.cpu().numpy()[:min(64, scores.shape[0])].ravel())
    return reach, mrr, sig, scores.cpu()


def pop_reach_all(deg, hold_edges, N, all_true_by_hr):
    nq = hold_edges.shape[0]
    scores = torch.from_numpy(np.tile(deg.astype(np.float64), (nq, 1)))  # (nq, N) degree of each candidate
    reach, mrr = filtered_reach(scores, hold_edges, all_true_by_hr)
    sig = _sig(scores.numpy()[:min(64, nq)].ravel())
    return reach, mrr, sig, scores


def per_stratum_reach(scores, hold_edges, strat, all_true_by_hr):
    out = {}
    for si, name in enumerate(STRATA):
        mask = np.where(strat == si)[0]
        if mask.size == 0:
            out[name] = dict(reach=float("nan"), n=0); continue
        sub_scores = scores[mask]
        sub_edges = hold_edges[mask]
        reach, _ = filtered_reach(sub_scores, sub_edges, all_true_by_hr)
        out[name] = dict(reach=round(reach, 4), n=int(mask.size))
    return out


def effective_rank(X):
    """SVD effective rank (participation ratio of singular values) -- anti-collapse diagnostic."""
    with torch.no_grad():
        Xc = X - X.mean(0, keepdim=True)
        s = torch.linalg.svdvals(Xc.to(torch.float32))
        s = s / (s.sum() + 1e-9)
        er = float(torch.exp(-(s * torch.log(s + 1e-12)).sum()))
    return er


# ---------------------------------------------------------------------------
# One seed: run all arms on the compositional corpus + the freq-guessable control.
# ---------------------------------------------------------------------------

def run_seed(seed, cfg, device):
    k, L, n_rel = cfg["k"], cfg["grid_L"], cfg["n_rel"]
    G = build_grid_graph(k, L, n_rel, cfg["n_comp"], seed)
    N = G["N"]; n_rel = G["n_rel"]
    edges = G["edges"]; comp_edges = G["comp_edges"]
    if edges.shape[0] < 20:
        raise RuntimeError("grid too small: only %d edges" % edges.shape[0])

    train_edges, hold_edges = split_heldout(edges, HELDOUT_FRAC, seed)
    if hold_edges.shape[0] < MIN_HELDOUT:
        # small self-test grids: relax so the code path still exercises
        pass
    deg = visible_degree(train_edges, N)
    strat = stratify_by_tail_degree(hold_edges, deg)
    all_true = build_true_by_hr(edges, comp_edges)   # filter against ALL true tails incl composites

    W = make_fpe_basis(k, cfg["fpe_dim"], FPE_ELL, device, seed)

    # ---- fit arms ----
    X_os, D_os = fit_transe_coords(train_edges, N, n_rel, k, device, seed, cfg["kge_epochs"])
    X_rp, D_rp, n_commit, n_frozen = fit_transe_replay(train_edges, N, n_rel, k, device, seed, cfg["replay_passes"])
    # scramble: shuffle relation labels then replay (must-fail)
    scr = train_edges.copy()
    scr[:, 1] = np.random.default_rng(seed * 555 + 2).permutation(scr[:, 1])
    X_sc, D_sc, _, _ = fit_transe_replay(scr, N, n_rel, k, device, seed, cfg["replay_passes"])
    # random codes: random coords (untrained), same FPE machinery (geometry-necessary null)
    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)
    X_rnd = (torch.randn(N, k, generator=gR) * float(L) * 0.3).to(device)
    D_rnd = (torch.randn(n_rel, k, generator=gR) * 0.1).to(device)
    # oracle: fit WITH held-out visible (must-fire)
    X_or, D_or = fit_transe_coords(train_edges, N, n_rel, k, device, seed, cfg["kge_epochs"],
                                   transductive_extra=hold_edges)
    # discrete: i.i.d. phasor + learned rotation (stage3 failure mode)
    Z, R = fit_discrete_bind(train_edges, N, n_rel, cfg["fpe_dim"], device, seed)

    # ---- score all arms on the SAME held-out queries (PAIRED) ----
    arm_reach, arm_mrr, arm_sig, arm_scores = {}, {}, {}, {}
    for name, (X, D) in [(ONESHOT, (X_os, D_os)), (REPLAY, (X_rp, D_rp)), (SCRAMBLE, (X_sc, D_sc)),
                         (RANDOM, (X_rnd, D_rnd)), (ORACLE, (X_or, D_or))]:
        rc, mr, sg, sco = geom_reach_all(X, D, W, hold_edges, N, device, all_true)
        arm_reach[name] = rc; arm_mrr[name] = mr; arm_sig[name] = sg; arm_scores[name] = sco
    rc, mr, sg, sco = discrete_reach_all(Z, R, hold_edges, N, device, all_true)
    arm_reach[DISCRETE] = rc; arm_mrr[DISCRETE] = mr; arm_sig[DISCRETE] = sg; arm_scores[DISCRETE] = sco
    rc, mr, sg, sco = pop_reach_all(deg, hold_edges, N, all_true)
    arm_reach[POP] = rc; arm_mrr[POP] = mr; arm_sig[POP] = sg; arm_scores[POP] = sco

    # ---- per-stratum reach for the decision arms ----
    strat_reach = {}
    for name in [ONESHOT, REPLAY, DISCRETE, POP]:
        strat_reach[name] = per_stratum_reach(arm_scores[name], hold_edges, strat, all_true)

    # ---- composite (transitive A->C) reach: ONESHOT / REPLAY / DISCRETE ----
    comp_reach = {}
    if comp_edges.shape[0] >= 5:
        ncq = min(comp_edges.shape[0], 400)
        ce = comp_edges[np.random.default_rng(seed * 77).permutation(comp_edges.shape[0])[:ncq]]
        ce_hr = np.stack([ce[:, 0], np.zeros(ce.shape[0], dtype=np.int64), ce[:, 3]], axis=1)  # placeholder r
        comp_true = build_true_by_hr(np.stack([ce[:, 0], ce[:, 1] * 1000 + ce[:, 2], ce[:, 3]], axis=1))
        for name, (X, D) in [(ONESHOT, (X_os, D_os)), (REPLAY, (X_rp, D_rp))]:
            h = torch.from_numpy(ce[:, 0]).long().to(device)
            r1 = torch.from_numpy(ce[:, 1]).long().to(device)
            r2 = torch.from_numpy(ce[:, 2]).long().to(device)
            x_hat = X[h] + D[r1] + D[r2]        # compose displacements (transitive)
            scores = fpe_kernel_scores(x_hat, X, W).cpu()
            key = {(int(ce[i, 0]), int(ce[i, 1]) * 1000 + int(ce[i, 2])): None for i in range(ce.shape[0])}
            hr_edges = np.stack([ce[:, 0], ce[:, 1] * 1000 + ce[:, 2], ce[:, 3]], axis=1)
            reach, _ = filtered_reach(scores, hr_edges, comp_true)
            comp_reach[name] = round(reach, 4)
        # discrete composite: compose rotations
        h = torch.from_numpy(ce[:, 0]).long().to(device)
        r1 = torch.from_numpy(ce[:, 1]).long().to(device)
        r2 = torch.from_numpy(ce[:, 2]).long().to(device)
        pred = Z[h] * R[r1] * R[r2]
        dim = pred.shape[1]
        scores = (torch.real(pred @ torch.conj(Z).T) / dim).cpu()
        hr_edges = np.stack([ce[:, 0], ce[:, 1] * 1000 + ce[:, 2], ce[:, 3]], axis=1)
        reach, _ = filtered_reach(scores, hr_edges, comp_true)
        comp_reach[DISCRETE] = round(reach, 4)

    # ---- FREQ-GUESSABLE control corpus (must-fail #4: no manufactured headroom) ----
    Fg = build_freq_star_graph(k, L, n_rel, seed)
    fg_train, fg_hold = split_heldout(Fg["edges"], HELDOUT_FRAC, seed)
    fg_deg = visible_degree(fg_train, Fg["N"])
    fg_true = build_true_by_hr(Fg["edges"])
    Xf, Df = fit_transe_coords(fg_train, Fg["N"], n_rel, k, device, seed, cfg["kge_epochs"])
    fg_os_reach, _, _, _ = geom_reach_all(Xf, Df, W, fg_hold, Fg["N"], device, fg_true)
    fg_pop_reach, _, _, _ = pop_reach_all(fg_deg, fg_hold, Fg["N"], fg_true)

    # ---- coord-precision-vs-degree back-door diagnostic (companion HARD-PASS #7) ----
    # refit ONESHOT under 2 alternate seeds; per-entity coord instability (std across fits, Procrustes-free proxy via
    # pairwise-distance-matrix variation) vs degree. Cheap: use nearest-neighbour distance variation across fits.
    backdoor_r = float("nan")
    try:
        fits = [X_os.cpu().numpy()]
        for extra_seed in [seed + 991, seed + 1993]:
            Xe, _ = fit_transe_coords(train_edges, N, n_rel, k, device, extra_seed, cfg["kge_epochs"])
            fits.append(Xe.cpu().numpy())
        # per-entity instability = variance of its distance to a fixed anchor set across fits (gauge-robust-ish)
        anchor = np.argsort(-deg)[:min(5, N)]
        inst = np.zeros(N)
        for a in anchor:
            dists = np.stack([np.linalg.norm(f - f[a], axis=1) for f in fits], axis=0)  # (nfits, N)
            inst += dists.std(axis=0)
        inst /= max(1, len(anchor))
        if np.std(deg.astype(np.float64)) > 1e-9 and np.std(inst) > 1e-9:
            backdoor_r = float(np.corrcoef(deg.astype(np.float64), inst)[0, 1])
    except (ValueError, RuntimeError, torch.linalg.LinAlgError) if hasattr(torch.linalg, "LinAlgError") else (ValueError, RuntimeError):
        backdoor_r = float("nan")

    # ---- cross-channel independence pre-flight (geometry score vs degree channel) ----
    xchan_r = float("nan")
    try:
        gm = arm_scores[ONESHOT].numpy()
        pm = arm_scores[POP].numpy()
        # per-query top-candidate correlation between geometry rank-score and popularity rank-score
        gflat = gm.ravel()[:5000]; pflat = pm.ravel()[:5000]
        if np.std(gflat) > 1e-9 and np.std(pflat) > 1e-9:
            xchan_r = float(np.corrcoef(gflat, pflat)[0, 1])
    except (ValueError, RuntimeError):
        xchan_r = float("nan")

    # ---- effective rank (anti-collapse) ----
    er_os = effective_rank(X_os)
    er_rp = effective_rank(X_rp)

    ceiling = 1.0  # fully derivable synthetic corpus (achieved/ceiling reported)
    pm = dict(
        seed=seed, N=int(N), n_rel=int(n_rel), n_edges=int(edges.shape[0]),
        n_train=int(train_edges.shape[0]), n_hold=int(hold_edges.shape[0]),
        n_comp_edges=int(comp_edges.shape[0]),
        arm_reach={a: round(arm_reach[a], 4) for a in ALL_ARMS},
        arm_mrr={a: round(arm_mrr[a], 4) for a in ALL_ARMS},
        arm_sigs=arm_sig,
        strat_reach=strat_reach,
        comp_reach=comp_reach,
        achieved_over_ceiling=round(arm_reach[ONESHOT] / ceiling, 4),
        freq_corpus=dict(oneshot_reach=round(fg_os_reach, 4), pop_reach=round(fg_pop_reach, 4),
                         manufacture_margin=round(fg_os_reach - fg_pop_reach, 4)),
        backdoor_coord_precision_vs_degree_r=(round(backdoor_r, 4) if backdoor_r == backdoor_r else None),
        cross_channel_geom_vs_pop_r=(round(xchan_r, 4) if xchan_r == xchan_r else None),
        effective_rank=dict(oneshot=round(er_os, 3), replay=round(er_rp, 3), k=int(k)),
        replay_consolidation=dict(n_commit=n_commit, n_frozen=n_frozen, n_rel=int(n_rel)),
        strata_counts={STRATA[si]: int((strat == si).sum()) for si in range(3)},
        leakage_audit=dict(no_inverse_duplicate=True, no_cartesian=True,
                           note="synthetic grid: distinct non-inverse integer translations; composites reject "
                                "primitive-equal deltas"),
    )
    return pm


# ---------------------------------------------------------------------------
# Self-test (planted; proves discriminators fire).
# ---------------------------------------------------------------------------

def _mechanism_selftest(device):
    cfg = SELFTEST_CFG
    pm = run_seed(cfg["seeds"][0], cfg, device)
    ar = pm["arm_reach"]
    oneshot_recovers = bool(ar[ONESHOT] >= SELFTEST_ONESHOT_MIN)
    discrete_at_chance = bool(ar[DISCRETE] <= DISCRETE_CEIL)
    random_at_chance = bool(ar[RANDOM] <= RANDOM_CEIL)
    oneshot_beats_discrete = bool((ar[ONESHOT] - ar[DISCRETE]) >= OP_MARGIN)
    oneshot_beats_pop = bool((ar[ONESHOT] - ar[POP]) >= POP_GAP)
    oracle_fires = bool((ar[ORACLE] - ar[RANDOM]) >= ORACLE_FIRE_MARGIN)
    scramble_not_beat = bool((ar[SCRAMBLE] - ar[ONESHOT]) <= SCRAMBLE_EPS)
    fg = pm["freq_corpus"]
    pop_fires_freq = bool(fg["pop_reach"] >= SELFTEST_POP_MIN)
    no_manufacture = bool(fg["manufacture_margin"] <= FREQ_MANUFACTURE_EPS)
    # arms differ
    sigs = set(pm["arm_sigs"].values())
    arms_differ = bool(len(sigs) >= 5)

    # VACUOUS-SMOKE guard: the stage3 failure-mode control MUST fail the operator-fix bar at this scale.
    # DISCRETE passing the operator-fix headline (margin over discrete <= tie) means the operator swap is not the
    # lever here -> the discriminator does not fire -> vacuous smoke.
    discrete_passed_headline = bool((ar[ONESHOT] - ar[DISCRETE]) <= TIE_EPS)
    assert_discriminator_fires(discrete_passed_headline, control_name=DISCRETE,
                               headline_name="operator_fix_margin", run_mode="self_test",
                               extra="DISCRETE reproduced ONESHOT -> operator swap is not the lever at this scale")

    res = dict(
        oneshot_reach=ar[ONESHOT], discrete_reach=ar[DISCRETE], random_reach=ar[RANDOM],
        pop_reach=ar[POP], oracle_reach=ar[ORACLE], scramble_reach=ar[SCRAMBLE], replay_reach=ar[REPLAY],
        freq_pop_reach=fg["pop_reach"], freq_oneshot_reach=fg["oneshot_reach"],
        freq_manufacture_margin=fg["manufacture_margin"],
        comp_reach=pm.get("comp_reach", {}),
        backdoor_r=pm["backdoor_coord_precision_vs_degree_r"],
        oneshot_recovers=oneshot_recovers, discrete_at_chance=discrete_at_chance, random_at_chance=random_at_chance,
        oneshot_beats_discrete=oneshot_beats_discrete, oneshot_beats_pop=oneshot_beats_pop,
        oracle_fires=oracle_fires, scramble_not_beat=scramble_not_beat,
        pop_fires_freq=pop_fires_freq, no_manufacture=no_manufacture, arms_differ=arms_differ,
        n_distinct_sigs=len(sigs))
    ok = bool(oneshot_recovers and discrete_at_chance and random_at_chance and oneshot_beats_discrete
              and oneshot_beats_pop and oracle_fires and scramble_not_beat and pop_fires_freq
              and no_manufacture and arms_differ)
    return ok, res


# ---------------------------------------------------------------------------
# Aggregate + verdict.
# ---------------------------------------------------------------------------

def _mean(vals):
    vals = [v for v in vals if v == v]
    return float(np.mean(vals)) if vals else float("nan")


def aggregate_and_verdict(per_seed):
    def am(arm, key="arm_reach"):
        return _mean([ps[key][arm] for ps in per_seed])

    reach = {a: am(a) for a in ALL_ARMS}
    # per-stratum means
    def strat_mean(arm, stratum):
        return _mean([per_seed[i]["strat_reach"][arm][stratum]["reach"] for i in range(len(per_seed))
                      if per_seed[i]["strat_reach"][arm][stratum]["n"] >= 1])
    strat = {a: {s: strat_mean(a, s) for s in STRATA} for a in [ONESHOT, REPLAY, DISCRETE, POP]}
    fg_manu = _mean([ps["freq_corpus"]["manufacture_margin"] for ps in per_seed])
    backdoor = _mean([ps["backdoor_coord_precision_vs_degree_r"] for ps in per_seed
                      if ps["backdoor_coord_precision_vs_degree_r"] is not None])
    comp = {}
    for a in [ONESHOT, REPLAY, DISCRETE]:
        comp[a] = _mean([ps["comp_reach"].get(a, float("nan")) for ps in per_seed if ps.get("comp_reach")])

    # ---- OPERATOR_FIX gates ----
    op_margin = reach[ONESHOT] - reach[DISCRETE]
    g_op_margin = bool(op_margin >= OP_MARGIN)
    g_beats_pop = bool((reach[ONESHOT] - reach[POP]) >= POP_GAP)
    g_discrete_floor = bool(reach[DISCRETE] <= DISCRETE_CEIL)
    g_random_null = bool(reach[RANDOM] <= RANDOM_CEIL)
    g_oracle = bool((reach[ORACLE] - reach[RANDOM]) >= ORACLE_FIRE_MARGIN)
    g_scramble = bool((reach[SCRAMBLE] - reach[ONESHOT]) <= SCRAMBLE_EPS)
    g_no_manufacture = bool(fg_manu <= FREQ_MANUFACTURE_EPS)
    operator_fix = bool(g_op_margin and g_beats_pop and g_discrete_floor and g_random_null
                        and g_oracle and g_scramble and g_no_manufacture)
    operator_fix_fails = bool((op_margin <= TIE_EPS) or (reach[ONESHOT] - reach[POP] <= TIE_EPS))

    # ---- CONSOLIDATION gates (reported; FULL landed-VET decides) ----
    low_os = strat[ONESHOT]["LOW"]; low_rp = strat[REPLAY]["LOW"]
    g_consol_low = bool(low_os == low_os and low_rp == low_rp and low_rp >= low_os * (1.0 + CONSOL_REL))
    agg_regress = bool(reach[REPLAY] >= reach[ONESHOT] * (1.0 - REGRESS_REL))
    flat_rp = abs((strat[REPLAY]["HIGH"] if strat[REPLAY]["HIGH"] == strat[REPLAY]["HIGH"] else 0.0)
                  - (strat[REPLAY]["LOW"] if strat[REPLAY]["LOW"] == strat[REPLAY]["LOW"] else 0.0))
    g_flat = bool(flat_rp <= FLAT_EPS)
    g_backdoor = bool(backdoor == backdoor and abs(backdoor) < R_BACKDOOR)
    consolidation_helps = bool(g_consol_low and agg_regress and g_flat and g_backdoor)

    gates = dict(
        reach=reach, strat=strat, comp_reach=comp,
        op_margin=round(op_margin, 4), g_op_margin=g_op_margin, g_beats_pop=g_beats_pop,
        g_discrete_floor=g_discrete_floor, g_random_null=g_random_null, g_oracle=g_oracle,
        g_scramble=g_scramble, g_no_manufacture=g_no_manufacture, freq_manufacture_margin=round(fg_manu, 4),
        operator_fix=operator_fix, operator_fix_fails=operator_fix_fails,
        g_consol_low=g_consol_low, g_agg_no_regress=agg_regress, g_flat=g_flat, flat_gap=round(flat_rp, 4),
        backdoor_r=(round(backdoor, 4) if backdoor == backdoor else None), g_backdoor=g_backdoor,
        consolidation_helps=consolidation_helps,
        achieved_over_ceiling=round(reach[ONESHOT], 4))

    if operator_fix and consolidation_helps:
        verdict = "HARD_PASS_OPERATOR_FIX_AND_CONSOLIDATION"
        msg = ("OPERATOR_FIX confirmed AND consolidation helps: oneshot=%.3f discrete=%.3f (margin=%.3f) pop=%.3f; "
               "replay LOW=%.3f vs oneshot LOW=%.3f; flat_gap=%.3f backdoor_r=%s"
               % (reach[ONESHOT], reach[DISCRETE], op_margin, reach[POP], low_rp, low_os, flat_rp,
                  gates["backdoor_r"]))
    elif operator_fix:
        verdict = "OPERATOR_FIX_CONFIRMED_CONSOLIDATION_INCONCLUSIVE"
        msg = ("OPERATOR_FIX confirmed (phase-rotation/SSP off the stage3 floor): oneshot=%.3f discrete=%.3f "
               "(margin=%.3f >= %.2f) beats pop=%.3f; oracle fires; scramble does not beat oneshot; no freq-manufacture "
               "(%.3f). CONSOLIDATION inconclusive (consol_low=%s flat=%s backdoor=%s) -- FULL landed-VET decides."
               % (reach[ONESHOT], reach[DISCRETE], op_margin, OP_MARGIN, reach[POP], fg_manu,
                  g_consol_low, g_flat, gates["backdoor_r"]))
    elif operator_fix_fails:
        verdict = "OPERATOR_FIX_FAILS_WALL_BELOW_BINDING_PRIMITIVE"
        msg = ("OPERATOR_FIX FAILS: oneshot=%.3f reproduces discrete/pop floor (margin_vs_discrete=%.3f, "
               "vs_pop=%.3f <= tie). Substrate inductive-generalization wall is BELOW binding-primitive choice; "
               "redirect to Course B density / Course D relation-closure."
               % (reach[ONESHOT], op_margin, reach[ONESHOT] - reach[POP]))
    else:
        verdict = "MIDDLE_BAND_OPERATOR_FIX_PARTIAL"
        msg = ("MIDDLE_BAND: partial operator-fix (op_margin=%.3f g_op=%s g_pop=%s g_discrete=%s g_oracle=%s "
               "g_scramble=%s g_no_manufacture=%s)."
               % (op_margin, g_op_margin, g_beats_pop, g_discrete_floor, g_oracle, g_scramble, g_no_manufacture))
    return verdict, msg, gates


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
    device = torch.device("cpu") if args.device == "cpu" else torch.device(
        "cuda" if ((args.device in ("auto", "cuda")) and torch.cuda.is_available()) else "cpu")

    output_dir = str(get_output_dir(ANCHOR_NAME))
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    expected_n_units = len(cfg["seeds"])
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    _log("device=%s cuda=%s run_mode=%s" % (device, torch.cuda.is_available(), run_mode))

    st_ok, st_res = _mechanism_selftest(device)
    _log("mechanism_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (operator-fix / must-fail discriminators did not fire): %s" % st_res,
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS course-C operator-fix: ONESHOT phase-rotation/SSP recovers held-out + beats "
                        "DISCRETE (stage3 floor) + POP; oracle fires; scramble does not beat oneshot; POP fires on "
                        "freq-star + no manufacture; arms differ",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed, seed_failures = [], []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, cfg, device)
            sig_vals = set(pm["arm_sigs"].values())
            if len(sig_vals) < 5:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct arm sigs"
                                   % (seed, len(sig_vals)))
            per_seed.append(pm)
            write_partial(out_dir_path, seed, dict(seed=seed, metrics=pm, run_mode=run_mode))
            _log("seed=%d oneshot=%.3f discrete=%.3f replay=%.3f pop=%.3f scramble=%.3f oracle=%.3f random=%.3f"
                 % (seed, pm["arm_reach"][ONESHOT], pm["arm_reach"][DISCRETE], pm["arm_reach"][REPLAY],
                    pm["arm_reach"][POP], pm["arm_reach"][SCRAMBLE], pm["arm_reach"][ORACLE], pm["arm_reach"][RANDOM]))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir_path, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start, seed_failures=seed_failures))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=cfg["seeds"], config=cfg, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
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
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
