"""ANCHOR_COMPOSE: the INDUCTIVE, entity-generalizing map-builder (held-out-ENTITY probe, additive/geometric bind).

THE INDUCTIVE FIX (staging build for the memorize->induct pivot). The per-entity KGE line (ONESHOT_ROTATE /
ADDITIVE_TRANSE) is a MEMORIZING regime: a fixed per-entity embedding table has NO vector for an entity absent from
train, so it cannot rank a held-out entity above a random code (GraIL/NBFNet architectural fact; CITED@notes
research_inductive_entity_generalizing_factorized_map_builder_2026-07-12 Part A). ANCHOR_COMPOSE represents a
brand-new entity with ZERO gradient training as a BUNDLE of relation-operator-bound anchor-neighbour estimates,
reusing the substrate's native additive store geometry:

  For a held-out entity t whose (test-time-visible) SUPPORT edges reach seen anchors h_i via relation r_i:
      E_derived[t] = mean_i ( X[h_i] + D[r_i] )                       # additive/degree-INVARIANT bundle
  (TransE tail estimate X_h + D_r per support edge, averaged -> a denoised position estimate). X (anchor codes) and
  D (relation operators) are the FROZEN scaffold trained ONLY on both-seen train edges; E_derived is pure arithmetic
  computed AFTER the fit is frozen, from t's OWN support edges -- a genuine zero-shot construction, no leakage.

OPERATOR CHOICE = ADDITIVE, NOT ROTATION (VET skunkworks a7688ea3, CITED): on the FAIR held-out test ADDITIVE beats
rotation and rotation's apparent win is popularity/degree-confounded. The additive/geometric code is the
degree-invariant one (relations = directions, inference = vector subtraction) -- so ANCHOR_COMPOSE binds with the
ADDITIVE operator (X_h + D_r). This is HDGL's node construction (Dalvi & Honavar arXiv:2402.17073) generalized to
CSKG typed multi-relation structure, with the fair-operator directive applied.

FAIR + WEAK-POINT-LOCALIZED head-to-head (the whole point; all arms scored PAIRED on the SAME query edges + candidate
set). The mechanism arm ANCHOR_COMPOSE and the memorize control ADDITIVE_TRANSE SHARE THE SAME additive fit (X, D):
the ONLY difference is whether a held-out entity's code is the anchor-composed bundle (inductive) or its random-init
table row (memorize). That isolates the entity-representation mechanism to a single knob.

ARMS (SHARDED per-entity codes; relations = per-TYPE operators; the held-out bundle is a per-ENTITY mean, never a
global fact bundle):
  ANCHOR_COMPOSE   : additive fit X/D; held-out codes REPLACED by E_derived (bundle of support-edge tail estimates).
  ADDITIVE_TRANSE  : additive fit X/D; held-out codes stay RANDOM-INIT (the per-entity-fit memorize control -- the
                     DIRECT comparison, same fit).
  ONESHOT_ROTATE   : rotation fit; held-out codes stay random-init (2nd per-entity-fit control, functional-form
                     variety).
  RANDOM_CODES     : random X + random D + same additive readout (the null; the bar to clear by >=0.05).
  ANCHOR_SCRAMBLE  : ANCHOR_COMPOSE with the SUPPORT relation ids SCRAMBLED (D[perm[r]] not D[r]) -> same anchors,
                     same degrees, broken relational signal. MUST-FAIL: isolates whether the RELATION operators
                     carry the signal vs a popularity/anchor-identity/degree confound.
  ORACLE_ADDITIVE  : additive fit with the held-out edges FOLDED IN (held-out codes LEARNED) -> positive control /
                     arena-answerable ceiling. If it fires, a null in ANCHOR/ADDITIVE is interpretable (cannot
                     induce), not an underfit harness.
  BASELINE_POP     : frequency incumbent (held-out tails have train freq 0 -> ~floor; fit-independence sanity).

PRE-REG BANDS (picked BEFORE the run; margins on held-out hits@10, degree-stratified):
  HARD-PASS : ANCHOR_COMPOSE - RANDOM >= 0.05 (real transferable relational signal to genuinely unseen entities)
              AND ANCHOR_COMPOSE - max(ADDITIVE_TRANSE, ONESHOT_ROTATE) >= 0.02 (beats the memorize arms on unseen
              entities -- the architectural claim) AND ORACLE fires AND scramble controlled AND not broken AND the
              margin holds on the low+mid degree stratum (not super-hub-confined; P1 skew HARD_FAIL demands this).
  MIDDLE    : 0.02 <= ANCHOR-RANDOM < 0.05, OR ANCHOR-RANDOM>=0.05 but form-margin<0.02, OR a scramble/degree
              confound is present -> stratify by anchor-support degree (does margin scale with support?).
  HARD-FAIL : ANCHOR_COMPOSE - RANDOM < 0.02 with ORACLE firing (a genuine negative: even the right-shaped
              construction fails on CSKG -> localize to sparsity vs crosstalk via the stratified diagnostics).
  Gated INCONCLUSIVE if ORACLE does not fire (arena not answerable), too few held-out queries, or a control beats POP.

FOUR VALIDITY-PREFLIGHT CHECKS (declared in the self-test via experiments._validity_preflight):
  (1) positive_control_passes : ORACLE_ADDITIVE recovers planted held-out tails and clears RANDOM by the fire margin.
  (2) metric_moves            : held-out hits@10 MOVES across [RANDOM, ADDITIVE_TRANSE, ANCHOR_COMPOSE, ORACLE].
  (3) negative_control_margin : RANDOM + ANCHOR_SCRAMBLE sit below ORACLE by margin, deterministically (>=2 vals).
  (4) full_gates_exercised    : aggregate_and_verdict runs on the planted per-seed, firing every fail-closed gate.

## Compute architecture
class (c) MIXED: split + support/query partition + POP = sequential-CPU graph ops (no matmul); the additive/rotate
fits = minibatch SGD (batched, neg-chunked on FULL); E_derived construction = a single vectorized index_add_ bundle
(no training, seconds); readouts = query-chunked batched matmul (the (nq,N) map is never materialized whole).
Storage SHARDED (each entity its own code; relations = per-TYPE additive displacements; the ONLY bundle is the
per-ENTITY anchor mean, not a global fact store). device=auto (cuda on the GPU host); remote_cpu forces cpu. FULL
fits are fit-checkpointed (ckpt_every) so a timeout/outage resumes each arm from its last epoch. The FULL needs a fit
for the anchor operator -> a multi-seed MEMSMOKE (FULL memory footprint, 2 seeds IN-PROCESS, few epochs) validates
no-OOM + per-seed empty_cache BEFORE the multi-hour FULL; the discriminator-fires proof is the self-test + analytical
(B), NOT the memsmoke.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): 7 arms produce >=5 distinct score signatures per seed.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: chance hits@10 = 10/N ~ 0.0004 at N~25.7k. HARD-PASS 0.05-above-random is on the achievable side (the
#   ORACLE positive control demonstrates it when the code is LEARNED). discriminator_reachability: OK.
# - baseline_in_band: ORACLE must fire in (RANDOM+margin, 1.0); RANDOM/POP near the 10/N floor on held-out.
# - discriminator survives scale: analytical (B) -- a per-entity table cannot encode an unseen entity by
#   construction (GraIL/NBFNet), so the memorize null persists at ANY N; the ORACLE-fires control proves the metric
#   can move at scale. The self-test fires the ANCHOR-beats-RANDOM + scramble-fails discriminators deterministically.
# - HARD-PASS strictly above floor: 0.05 clears HARD-FAIL 0.02 by 5%+ band-width; the form-margin adds strictness.
# - HP_SCOPE: the inductive HARD-PASS gates apply to ANCHOR_COMPOSE only. ORACLE = positive control (must fire);
#   RANDOM/ANCHOR_SCRAMBLE = must-not-clear-bar controls; ADDITIVE_TRANSE/ONESHOT_ROTATE = memorize head-to-heads;
#   POP = fit-independence sanity.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all 7 arms (arm cardinality) + >=5 sigs.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: adaptive_with_discriminator_gate -- HELDOUT_ENTITY_FRAC/SUPPORT_FRAC/ORACLE_FIRE_MARGIN
#   pre-registered, NOT tuned on real data; the planted self-test verifies ORACLE+ANCHOR recover on additive-
#   consistent structure when codes exist / can be composed.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the prereg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm flush prints).

ASCII-only. No bare except; except SystemExit before except Exception.
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, write_partial, assert_discriminator_fires,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from experiments.exp_gt_induction_fb15k237_dense_v1 import Graph, build_ids  # noqa: E402
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, filtered_hits_from_scores, pop_hits,
    stratify_by_tail_degree, PRIMARY_K,
)
from experiments._course_c_rotate_core_v1 import (  # noqa: E402
    fit_kge_rotate, rotate_direct_scores, additive_direct_scores, ROT_LR,
)
from experiments._kge_anchor1_fit import fit_kge_anchor1, A1_LR  # noqa: E402
from experiments._fit_checkpoint import FitCheckpoint, cleanup_seed_checkpoints  # noqa: E402

ANCHOR_NAME = "anchor_compose_inductive_entity_cskg_v1"

# ---- Arm names ----
ANCHOR = "ANCHOR_COMPOSE"        # mechanism: additive bundle of anchor-neighbour tail estimates (zero-training)
ADDITIVE = "ADDITIVE_TRANSE"     # per-entity-fit memorize control (SAME additive fit; held-out code random-init)
ONESHOT = "ONESHOT_ROTATE"       # 2nd per-entity-fit control (rotation fit)
RANDOM = "RANDOM_CODES"          # null (the bar: clear this by >=0.05)
SCRAMBLE = "ANCHOR_SCRAMBLE"     # must-fail: bundle with support relation ids scrambled (degree/anchor confound)
ORACLE = "ORACLE_ADDITIVE"       # positive control: additive fit with held-out folded in (codes learned)
POP = "BASELINE_POP"             # frequency incumbent (fit-independence sanity)
GEOM_ARMS = [ANCHOR, ADDITIVE, ONESHOT, RANDOM, SCRAMBLE, ORACLE]   # scored via geometry readouts
ALL_ARMS = GEOM_ARMS + [POP]

# ---- Pre-registered bands (picked BEFORE the run; hits@10 margins) ----
HARD_PASS_MARGIN = 0.05    # ANCHOR - RANDOM >= this (transferable relational signal to unseen entities)
FORM_GAP = 0.02            # ANCHOR - max(ADDITIVE, ONESHOT) >= this (beats memorize arms on unseen entities)
MIDDLE_LO = 0.02           # MIDDLE-BAND floor: ANCHOR - RANDOM in [0.02, 0.05)
ORACLE_FIRE_MARGIN = 0.10  # positive control: ORACLE - RANDOM >= this (arena answerable)
SCRAMBLE_EPS = 0.02        # must-fail: SCRAMBLE - RANDOM <= this (else relational signal is a degree/anchor confound)
CONTROL_LOSE_EPS = 0.03    # broken-test guard: a control (RANDOM/SCRAMBLE) beating POP by > this = broken
MIN_HELDOUT = 20           # min held-out QUERY edges for a valid discriminator
MIN_STRAT_Q = 8            # min queries in a stratum to report its margin
PRIMARY_METRIC = "hits@%d" % PRIMARY_K   # PRIMARY_K = 10

# ---- Held-out-entity split knobs (pre-registered; NOT tuned on real data) ----
HELDOUT_ENTITY_FRAC = 0.15   # fraction of entities withheld from EVERY train edge (codes never updated)
SUPPORT_FRAC = 0.5           # fraction of a held-out entity's edges reserved as SUPPORT (build E_derived); rest=query

# ---- self-test planted thresholds (calibrated on the synthetic additive-consistent grid, not real data) ----
SELFTEST_ORACLE_MIN = 0.30   # planted grid: ORACLE recovers held-out tails (codes learned) to at least this h@10
SELFTEST_ANCHOR_MIN = 0.20   # planted grid: ANCHOR_COMPOSE recovers held-out tails ZERO-TRAINING to at least this
SELFTEST_AC_BEATS_RANDOM = 0.08  # planted grid: ANCHOR - RANDOM >= this (discriminator fires)
SELFTEST_SCRAMBLE_MARGIN = 0.05  # planted grid: ANCHOR - SCRAMBLE >= this (relation signal, not anchor identity)
SELFTEST_MIN_HO = 8          # planted grid: minimum held-out QUERY edges

# ---- hardest relation tertile (weak-point-localization target) ----
# CITED@data/exp_cskg_graph_structure_diagnostic_v1/metrics.json:diagnostic.hardest_tertile (cardinality-heavy).
HARDEST_TERTILE_RELS = frozenset([
    "hascontext", "antonym", "mayhaveproperty", "locatednear", "xattr", "haslexicalunit", "hassubevent",
    "motivatedbygoal", "desires", "synonym", "usedfor", "similarto", "hasprerequisite", "xwant",
])

SCORE_CHUNK = 256

# Config profiles. SELFTEST/MEMSMOKE/FULL exercise the SAME split->partition->fit->compose->score->verdict path.
SELFTEST_CFG = dict(k=12, epochs=350, n_neg=32, batch=4096,
                    heldout_entity_frac=0.15, support_frac=0.5, n_heldout_eval=0, min_heldout=SELFTEST_MIN_HO)
# MEMSMOKE = FULL memory footprint (full N + k=24 + n_neg=128 + neg_chunk) but few epochs + 2 seeds IN-PROCESS.
# Purpose: prove no OOM + per-seed empty_cache between seeds BEFORE the multi-hour FULL. NOT a discriminator gate
# (few epochs under-train the oracle by design); the discriminator-fires proof is the self-test + analytical (B).
MEMSMOKE_CFG = dict(k=24, epochs=25, n_neg=128, batch=8192, neg_chunk=16,
                    heldout_entity_frac=HELDOUT_ENTITY_FRAC, support_frac=SUPPORT_FRAC,
                    cskg_max_lines=0, k_core=12, cskg_max_nodes=0,
                    n_heldout_eval=2000, min_heldout=10, seeds=[7, 13])
# FULL: k=24 matches the completed gpu1024 / v1-heldout capacity knob. epochs=500 = the v1-heldout v2 fidelity that
# targets the ORACLE positive control firing on the harder held-out-entity oracle (support-only-trained codes).
# More epochs only sharpen the SEEN/oracle geometry; a held-out tail in ADDITIVE/ONESHOT has NO vector to sharpen
# (random-init by split construction) and ANCHOR is training-free -> epochs CANNOT manufacture a memorize->induct
# false positive. ckpt_every makes each fit outage-resumable; neg_chunk bounds the (batch,n_neg,k) transient.
FULL_CFG = dict(k=24, epochs=500, n_neg=128, batch=8192, neg_chunk=16, ckpt_every=20,
                heldout_entity_frac=HELDOUT_ENTITY_FRAC, support_frac=SUPPORT_FRAC,
                cskg_max_lines=0, k_core=12, cskg_max_nodes=0,
                n_heldout_eval=3000, min_heldout=MIN_HELDOUT, seeds=[7, 13, 17])


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _sig(arr):
    a = np.round(np.asarray(arr, dtype=np.float64), 4)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    final = os.path.join(str(output_dir), "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    final = os.path.join(str(output_dir), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Held-out-ENTITY split WITH a per-entity SUPPORT / QUERY partition.
#   withhold ~frac of entities from every train edge; train = both-seen edges.
#   a held-out entity t appears only as a TAIL in (h_i seen, r_i, t) edges (head-withheld edges are dropped).
#   partition t's held edges: SUPPORT (build E_derived) + QUERY (scored) -- disjoint, so no leakage.
#   degree-1 held-out entities are COLD (no support): scored as queries with ANCHOR falling back to random code.
# ---------------------------------------------------------------------------

def build_planted_transe_arena(seed, n_ent=300, n_rel=6, k_lat=8, deg=3, w_scale=1.0):
    """Planted HIGH-intrinsic-dim TransE-consistent arena where the RELATION operator is NECESSARY (no smooth
    low-dim embedding exists, so plain neighbour-averaging fails -- unlike a 2D grid). Entities get random latents
    z ~ N(0,I) in k_lat dims; relations get random translations w_r; an edge (h,r,t) connects h to the entity
    NEAREST to z[h]+w[r]. A held-out entity t is recovered ONLY by mean_i(z[h_i]+w[r_i])==z[t]; scrambling the
    relations offsets the bundle by mean(w[perm(r)]-w[r]) != 0 -> the must-fail control genuinely fails. The
    additive fit rediscovers a consistent embedding; deterministic (default_rng(seed) + order-preserving dedup)."""
    rng = np.random.default_rng(seed * 100019 + 3)
    z = rng.standard_normal((n_ent, k_lat))
    w = rng.standard_normal((n_rel, k_lat)) * w_scale
    edges = []
    for h in range(n_ent):
        rels = rng.choice(n_rel, size=deg, replace=False)
        for r in rels:
            target = z[h] + w[r]
            d = np.linalg.norm(z - target, axis=1)
            d[h] = np.inf
            t = int(np.argmin(d))
            edges.append(("e%d" % h, "r%d" % r, "e%d" % t))
    return list(dict.fromkeys(edges))   # order-preserving dedup (NOT list(set(...)); cross-process determinism)


def build_heldout_entity_split_ac(pool_lbl, ent2i, frac, support_frac, seed):
    n_ent = len(ent2i)
    rng = np.random.default_rng(seed * 100003 + 7)
    n_hold = max(1, int(frac * n_ent))
    hold_ids = set(int(x) for x in rng.choice(n_ent, size=n_hold, replace=False))
    train_lbl = []
    held_by_tail = defaultdict(list)
    for (h, r, t) in pool_lbl:
        hi = ent2i[h]; ti = ent2i[t]
        h_hold = hi in hold_ids; t_hold = ti in hold_ids
        if not h_hold and not t_hold:
            train_lbl.append((h, r, t))
        elif t_hold and not h_hold:
            held_by_tail[ti].append((h, r, t))
    support_lbl, query_lbl = [], []
    n_cold = 0
    rng2 = np.random.default_rng(seed * 991 + 5)
    # deterministic tail order for a stable partition across processes
    for ti in sorted(held_by_tail.keys()):
        edges = held_by_tail[ti]
        d = len(edges)
        if d == 1:
            query_lbl.append(edges[0]); n_cold += 1
            continue
        order = rng2.permutation(d)
        n_sup = max(1, int(round(support_frac * d)))
        n_sup = min(n_sup, d - 1)   # always leave >=1 query edge
        sup_idx = set(int(x) for x in order[:n_sup].tolist())
        for j, e in enumerate(edges):
            (support_lbl if j in sup_idx else query_lbl).append(e)
    return train_lbl, support_lbl, query_lbl, hold_ids, n_cold


# ---------------------------------------------------------------------------
# ANCHOR_COMPOSE construction: E_derived[t] = mean over t's support edges of (X[h] + D[r]) -- degree-invariant
# additive bundle. Returns a patched entity table (held-out rows replaced) + support-degree per entity.
# ---------------------------------------------------------------------------

def build_anchor_compose_codes(X, D, support_int, device, rel_perm=None):
    N, k = X.shape[0], X.shape[1]
    Xp = X.clone()
    support_deg = np.zeros(N, dtype=np.int64)
    if support_int.shape[0] == 0:
        return Xp, support_deg
    h = torch.from_numpy(support_int[:, 0]).long().to(device)
    r_np = support_int[:, 1].copy()
    if rel_perm is not None:
        r_np = rel_perm[r_np]                       # scramble: map each support relation id -> a shuffled id
    r = torch.from_numpy(r_np).long().to(device)
    t = torch.from_numpy(support_int[:, 2]).long().to(device)
    est = X[h] + D[r]                               # (S,k) per-edge TransE tail estimate
    acc = torch.zeros(N, k, device=device, dtype=X.dtype)
    acc.index_add_(0, t, est)                       # sum of estimates per tail
    cnt = torch.zeros(N, device=device, dtype=X.dtype)
    cnt.index_add_(0, t, torch.ones(t.shape[0], device=device, dtype=X.dtype))
    mask = cnt > 0
    Xp[mask] = acc[mask] / cnt[mask].unsqueeze(1)   # MEAN = degree-invariant bundle
    support_deg = cnt.detach().to("cpu").numpy().astype(np.int64)
    return Xp, support_deg


# ---------------------------------------------------------------------------
# Fit the arms + build E_derived + score PAIRED on the SAME held-out QUERY edges.
# ---------------------------------------------------------------------------

def _mk_ckpt(ckpt_dir, ckpt_every, tag, seed):
    if ckpt_dir is None or not ckpt_every:
        return None
    return FitCheckpoint(ckpt_dir, "%s_seed%d" % (tag, seed), ckpt_every)


def fit_and_score(train_int, support_int, query_int, hold_all, N, n_rel, cfg, device, seed,
                  rel_tail_freq, all_true, ckpt_dir=None):
    k = cfg["k"]; epochs = cfg["epochs"]; n_neg = cfg["n_neg"]; batch = cfg["batch"]
    neg_chunk = cfg.get("neg_chunk"); ckpt_every = cfg.get("ckpt_every")

    def _ec():
        if getattr(device, "type", "") == "cuda":
            torch.cuda.empty_cache()

    # ADDITIVE fit (shared by ADDITIVE_TRANSE + ANCHOR_COMPOSE + ANCHOR_SCRAMBLE): X (N,k), D (n_rel,k)
    Xa, Da = fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, reciprocal=True, lr=A1_LR,
                             n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk,
                             ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "additive", seed))
    _ec()
    # ROTATION fit (ONESHOT_ROTATE)
    PHI, THETA = fit_kge_rotate(train_int, N, n_rel, k, device, seed, epochs, lr=ROT_LR, n_neg=n_neg,
                                batch_size=batch, neg_chunk=neg_chunk,
                                ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "rotate_oneshot", seed))
    _ec()
    # ORACLE additive fit (held-out folded in -> held-out codes LEARNED) = positive control
    Xo, Do = fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, transductive_extra=hold_all,
                             reciprocal=True, lr=A1_LR, n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk,
                             ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "additive_oracle", seed))
    _ec()
    # RANDOM codes (random X + random D + additive readout) = the null
    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)
    Xr = (torch.randn(N, k, generator=gR) * 0.1).to(device)
    Dr = (torch.randn(n_rel, k, generator=gR) * 0.1).to(device)

    # ANCHOR_COMPOSE + ANCHOR_SCRAMBLE codes (zero-training; reuse the additive scaffold Xa/Da)
    Xac, support_deg = build_anchor_compose_codes(Xa, Da, support_int, device)
    rel_perm = np.random.default_rng(seed * 4441 + 17).permutation(n_rel)
    Xscr, _ = build_anchor_compose_codes(Xa, Da, support_int, device, rel_perm=rel_perm)

    arm_metric, arm_sig, arm_scores = {}, {}, {}
    for name, sc in [
        (ANCHOR, additive_direct_scores(Xac, Da, query_int, device, chunk=SCORE_CHUNK)),
        (ADDITIVE, additive_direct_scores(Xa, Da, query_int, device, chunk=SCORE_CHUNK)),
        (ONESHOT, rotate_direct_scores(PHI, THETA, query_int, device, chunk=SCORE_CHUNK)),
        (SCRAMBLE, additive_direct_scores(Xscr, Da, query_int, device, chunk=SCORE_CHUNK)),
        (ORACLE, additive_direct_scores(Xo, Do, query_int, device, chunk=SCORE_CHUNK)),
        (RANDOM, additive_direct_scores(Xr, Dr, query_int, device, chunk=SCORE_CHUNK)),
    ]:
        arm_metric[name] = filtered_hits_from_scores(sc, query_int, all_true, ks=(1, PRIMARY_K))
        arm_sig[name] = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
        arm_scores[name] = sc
    pop_m, pop_rank_vec = pop_hits(rel_tail_freq, query_int, all_true, N, ks=(1, PRIMARY_K))
    arm_metric[POP] = pop_m
    arm_sig[POP] = _sig(pop_rank_vec.astype(np.float64))

    del Xa, Da, PHI, THETA, Xo, Do, Xr, Dr, Xac, Xscr
    _ec()
    return dict(arm_metric=arm_metric, arm_sig=arm_sig, arm_scores=arm_scores, support_deg=support_deg)


# ---------------------------------------------------------------------------
# Weak-point localization: per anchor-support-degree bin, per global-degree tertile, per relation-tertile.
# ---------------------------------------------------------------------------

def _hits_subset(scores, query_int, all_true, mask, k=PRIMARY_K):
    idx = np.where(mask)[0]
    if idx.size < 1:
        return dict(hits=float("nan"), n=0)
    sub = filtered_hits_from_scores(scores[idx], query_int[idx], all_true, ks=(k,))
    return dict(hits=round(sub["hits@%d" % k], 5), n=int(idx.size))


def _pop_subset(rel_tail_freq, query_int, all_true, n_ent, mask, k=PRIMARY_K):
    idx = np.where(mask)[0]
    if idx.size < 1:
        return dict(hits=float("nan"), n=0)
    sub, _ = pop_hits(rel_tail_freq, query_int[idx], all_true, n_ent, ks=(k,))
    return dict(hits=round(sub["hits@%d" % k], 5), n=int(idx.size))


SUPPORT_BINS = [(0, 0, "cold"), (1, 1, "d1"), (2, 3, "d2_3"), (4, 7, "d4_7"), (8, 10 ** 9, "d8plus")]


def localize_weak_points(arm_scores, query_int, all_true, support_deg, node_degree, rel_i2lbl,
                         rel_tail_freq, N):
    """Stratify the mechanism vs controls three ways for weak-point localization."""
    nq = query_int.shape[0]
    gold = query_int[:, 2]
    q_support = np.array([support_deg[int(g)] for g in gold], dtype=np.int64)          # anchor-support degree
    q_gdeg = np.array([node_degree.get(int(g), 0) for g in gold], dtype=np.float64)    # global degree (super-hub)
    strat, tert = stratify_by_tail_degree(query_int, node_degree)                      # low/mid/high tertiles
    q_hardest = np.array([rel_i2lbl.get(int(query_int[i, 1]), "") in HARDEST_TERTILE_RELS
                          for i in range(nq)], dtype=bool)
    report_arms = [ANCHOR, ADDITIVE, RANDOM, ORACLE]

    def _by_mask(mask):
        out = {a: _hits_subset(arm_scores[a], query_int, all_true, mask) for a in report_arms}
        out[POP] = _pop_subset(rel_tail_freq, query_int, all_true, N, mask)
        return out

    by_support = {}
    for lo, hi, name in SUPPORT_BINS:
        by_support[name] = _by_mask((q_support >= lo) & (q_support <= hi))
    by_gdeg_tertile = {nm: _by_mask(strat == si) for si, nm in enumerate(["low", "mid", "high"])}
    fair_lowmid = _by_mask((strat == 0) | (strat == 1))       # non-super-hub arena (P1 skew fairness)
    by_reltertile = dict(hardest=_by_mask(q_hardest), rest=_by_mask(~q_hardest))
    return dict(by_support_degree=by_support, by_global_degree_tertile=by_gdeg_tertile,
                fair_low_mid=fair_lowmid, by_relation_tertile=by_reltertile,
                global_degree_tertile_bounds=tert,
                support_deg_hist={name: int(((q_support >= lo) & (q_support <= hi)).sum())
                                  for lo, hi, name in SUPPORT_BINS})


# ---------------------------------------------------------------------------
# One corpus run.
# ---------------------------------------------------------------------------

def run_corpus(pool_lbl, cfg, device, seed, corpus_name, ckpt_dir=None, localize=True):
    ent2i, rel2i = build_ids(pool_lbl, [], [])
    N = len(ent2i); n_rel = len(rel2i)
    rel_i2lbl = {v: k for k, v in rel2i.items()}
    train_lbl, support_lbl, query_lbl, hold_ids, n_cold = build_heldout_entity_split_ac(
        pool_lbl, ent2i, cfg["heldout_entity_frac"], cfg["support_frac"], seed)
    n_query_total = len(query_lbl)

    # optional bounded subsample of query edges (scoring cost = nq * N)
    if cfg.get("n_heldout_eval") and n_query_total > cfg["n_heldout_eval"]:
        rng = np.random.default_rng(seed * 777 + 3)
        idx = sorted(rng.choice(n_query_total, size=cfg["n_heldout_eval"], replace=False).tolist())
        query_lbl = [query_lbl[i] for i in idx]

    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    support_int = _to_int_edges(support_lbl, ent2i, rel2i)
    query_int = _to_int_edges(query_lbl, ent2i, rel2i)
    hold_all = np.concatenate([support_int, query_int], axis=0) if query_int.shape[0] else support_int
    gd = Graph(train_lbl, ent2i, rel2i)
    all_true = build_true_by_hr_int(train_int, support_int, query_int)

    result = dict(corpus=corpus_name, seed=seed, N=int(N), n_rel=int(n_rel), n_train=int(train_int.shape[0]),
                  n_heldout_entities=len(hold_ids), n_support=int(support_int.shape[0]),
                  n_query_total=n_query_total, n_query_scored=int(query_int.shape[0]), n_cold=int(n_cold),
                  heldout_entity_frac=cfg["heldout_entity_frac"], support_frac=cfg["support_frac"])
    if query_int.shape[0] < 1:
        result["empty"] = True
        return result

    fs = fit_and_score(train_int, support_int, query_int, hold_all, N, n_rel, cfg, device, seed,
                       gd.rel_tail_freq, all_true, ckpt_dir=ckpt_dir)
    am = fs["arm_metric"]
    result.update(
        arm_hits={a: {kk: round(vv, 5) for kk, vv in am[a].items() if kk != "n"} for a in ALL_ARMS},
        arm_n={a: am[a]["n"] for a in ALL_ARMS},
        arm_sigs=fs["arm_sig"],
    )
    if localize:
        result["localization"] = localize_weak_points(
            fs["arm_scores"], query_int, all_true, fs["support_deg"], gd.node_degree, rel_i2lbl,
            gd.rel_tail_freq, N)
    return result


# ---------------------------------------------------------------------------
# Aggregate + verdict (per_seed list length 1..3).
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _h10(ps, arm):
    return ps["arm_hits"][arm].get(PRIMARY_METRIC, float("nan"))


def _fair_lowmid_h10(ps, arm):
    loc = ps.get("localization", {})
    cell = loc.get("fair_low_mid", {}).get(arm, {})
    if cell.get("n", 0) >= MIN_STRAT_Q:
        return cell.get("hits", float("nan"))
    return float("nan")


def aggregate_and_verdict(per_seed):
    def agg(arm):
        return _nm([_h10(ps, arm) for ps in per_seed])

    def agg_fair(arm):
        return _nm([_fair_lowmid_h10(ps, arm) for ps in per_seed])

    h = {a: agg(a) for a in ALL_ARMS}
    hf = {a: agg_fair(a) for a in [ANCHOR, ADDITIVE, ONESHOT, RANDOM, ORACLE, POP]}
    n_query = int(_nm([ps["n_query_scored"] for ps in per_seed]))

    d_anchor = (h[ANCHOR] - h[RANDOM]) if (h[ANCHOR] == h[ANCHOR] and h[RANDOM] == h[RANDOM]) else float("nan")
    best_memorize = _nm([max(v for v in (h[ADDITIVE], h[ONESHOT]) if v == v)]) \
        if (h[ADDITIVE] == h[ADDITIVE] or h[ONESHOT] == h[ONESHOT]) else float("nan")
    form_margin = (h[ANCHOR] - best_memorize) if (h[ANCHOR] == h[ANCHOR] and best_memorize == best_memorize) \
        else float("nan")
    d_scramble = (h[SCRAMBLE] - h[RANDOM]) if (h[SCRAMBLE] == h[SCRAMBLE] and h[RANDOM] == h[RANDOM]) else float("nan")
    oracle_margin = (h[ORACLE] - h[RANDOM]) if (h[ORACLE] == h[ORACLE] and h[RANDOM] == h[RANDOM]) else float("nan")
    fair_anchor_margin = (hf[ANCHOR] - hf[RANDOM]) if (hf[ANCHOR] == hf[ANCHOR] and hf[RANDOM] == hf[RANDOM]) \
        else float("nan")

    enough_heldout = bool(n_query >= MIN_HELDOUT)
    oracle_fires = bool(oracle_margin == oracle_margin and oracle_margin >= ORACLE_FIRE_MARGIN)
    scramble_controlled = bool(d_scramble == d_scramble and d_scramble <= SCRAMBLE_EPS)
    broken = bool((h[RANDOM] == h[RANDOM] and h[POP] == h[POP] and (h[RANDOM] - h[POP]) > CONTROL_LOSE_EPS)
                  or (h[SCRAMBLE] == h[SCRAMBLE] and h[POP] == h[POP] and (h[SCRAMBLE] - h[POP]) > CONTROL_LOSE_EPS))
    fair_holds = bool(fair_anchor_margin == fair_anchor_margin and fair_anchor_margin > 0.0)

    hard_pass = bool(d_anchor == d_anchor and d_anchor >= HARD_PASS_MARGIN
                     and form_margin == form_margin and form_margin >= FORM_GAP
                     and oracle_fires and scramble_controlled and not broken and fair_holds)
    hard_fail = bool(d_anchor == d_anchor and d_anchor < MIDDLE_LO)
    middle = bool(d_anchor == d_anchor and not hard_pass and not hard_fail)

    if not enough_heldout:
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT"
    elif broken:
        verdict = "BROKEN_TEST_CONTROL_BEATS_POP"
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_ORACLE_UNDERFIT"
    elif hard_pass:
        verdict = "HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE"
    elif hard_fail:
        verdict = "HARD_FAIL_ANCHOR_COMPOSE_NO_TRANSFER"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_ANCHOR_TRANSFER"

    verdict_msg = (
        "%s || HELD-OUT hits@%d [nq=%d]: ANCHOR=%s | ADDITIVE=%s ONESHOT=%s | RANDOM=%s SCRAMBLE=%s | ORACLE=%s "
        "POP=%s || anchor_margin_vs_random=%s (HARD_PASS>=%.2f MIDDLE[%.2f,%.2f) HARD_FAIL<%.2f) | "
        "form_margin_vs_memorize=%s (>=%.2f) | fair_lowmid_anchor_margin=%s (>0) | scramble_margin=%s (<=%.2f) | "
        "ORACLE fires(>=%.2f)=%s margin=%s | broken=%s | frac=%.2f support_frac=%.2f seeds=%d" % (
            verdict, PRIMARY_K, n_query, _fmt(h[ANCHOR]), _fmt(h[ADDITIVE]), _fmt(h[ONESHOT]), _fmt(h[RANDOM]),
            _fmt(h[SCRAMBLE]), _fmt(h[ORACLE]), _fmt(h[POP]), _fmt(d_anchor), HARD_PASS_MARGIN, MIDDLE_LO,
            HARD_PASS_MARGIN, MIDDLE_LO, _fmt(form_margin), FORM_GAP, _fmt(fair_anchor_margin), _fmt(d_scramble),
            SCRAMBLE_EPS, ORACLE_FIRE_MARGIN, oracle_fires, _fmt(oracle_margin), broken,
            _nm([ps["heldout_entity_frac"] for ps in per_seed]),
            _nm([ps["support_frac"] for ps in per_seed]), len(per_seed)))

    gates = dict(
        verdict=verdict,
        heldout_hits_at_k={a: (round(h[a], 5) if h[a] == h[a] else None) for a in ALL_ARMS},
        heldout_hits_at_1={a: _nm([ps["arm_hits"][a].get("hits@1", float("nan")) for ps in per_seed])
                           for a in ALL_ARMS},
        fair_lowmid_hits_at_k={a: (round(hf[a], 5) if hf[a] == hf[a] else None)
                               for a in [ANCHOR, ADDITIVE, ONESHOT, RANDOM, ORACLE, POP]},
        primary_k=PRIMARY_K,
        anchor_margin_vs_random=(round(d_anchor, 5) if d_anchor == d_anchor else None),
        form_margin_vs_memorize=(round(form_margin, 5) if form_margin == form_margin else None),
        fair_lowmid_anchor_margin=(round(fair_anchor_margin, 5) if fair_anchor_margin == fair_anchor_margin else None),
        scramble_margin_vs_random=(round(d_scramble, 5) if d_scramble == d_scramble else None),
        oracle_margin_vs_random=(round(oracle_margin, 5) if oracle_margin == oracle_margin else None),
        n_query_scored=n_query,
        bands=dict(HARD_PASS_MARGIN=HARD_PASS_MARGIN, FORM_GAP=FORM_GAP, MIDDLE_LO=MIDDLE_LO,
                   ORACLE_FIRE_MARGIN=ORACLE_FIRE_MARGIN, SCRAMBLE_EPS=SCRAMBLE_EPS, MIN_HELDOUT=MIN_HELDOUT,
                   HELDOUT_ENTITY_FRAC=HELDOUT_ENTITY_FRAC, SUPPORT_FRAC=SUPPORT_FRAC),
        enough_heldout=enough_heldout, oracle_fires=oracle_fires, scramble_controlled=scramble_controlled,
        broken=broken, fair_holds=fair_holds, hard_pass=hard_pass, hard_fail=hard_fail, middle=middle,
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism self-test. Planted DENSE additive-consistent grid: hold out a fraction of entities, partition their
# edges into support/query. ANCHOR_COMPOSE (bundle of support-edge tail estimates, ZERO training) recovers held-out
# tails >> RANDOM; ANCHOR_SCRAMBLE (support relations shuffled) fails; ORACLE (held-out folded in) recovers and
# fires. Proves (a) split->partition->compose->score->verdict runs, (b) the arena registers positive signal so the
# >=0.05 bar is achievable-in-principle, (c) the RELATION operators (not anchor identity/degree) carry the signal,
# (d) arms differ. Determinism-pinned to single-thread CPU (tiny grids have symmetry ties).
# ---------------------------------------------------------------------------

def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    device = torch.device("cpu")
    try:
        return _mechanism_selftest_body(device)
    finally:
        torch.set_num_threads(_prev)


def _mechanism_selftest_body(device):
    pool = build_planted_transe_arena(7, n_ent=300, n_rel=6, k_lat=8, deg=3)
    cfg = dict(SELFTEST_CFG)
    res = run_corpus(pool, cfg, device, 7, "PLANTED_TRANSE_HELDOUT_ENTITY", localize=True)
    out = dict(n_grid_entities=res.get("N"), n_heldout_entities=res.get("n_heldout_entities"),
               n_support=res.get("n_support"), n_query=res.get("n_query_scored"), n_cold=res.get("n_cold"))
    if res.get("empty") or res.get("n_query_scored", 0) < SELFTEST_MIN_HO:
        out["fail"] = "planted grid produced too few held-out-entity queries (%s)" % res.get("n_query_scored")
        return False, out

    ah = res["arm_hits"]
    h = {a: ah[a].get(PRIMARY_METRIC, float("nan")) for a in ALL_ARMS}
    n_sigs = len(set(res["arm_sigs"].values()))
    anchor_margin = h[ANCHOR] - h[RANDOM]
    scramble_margin = h[ANCHOR] - h[SCRAMBLE]
    oracle_margin = h[ORACLE] - h[RANDOM]

    oracle_recovers = bool(h[ORACLE] == h[ORACLE] and h[ORACLE] >= SELFTEST_ORACLE_MIN)
    oracle_fires = bool(oracle_margin == oracle_margin and oracle_margin >= ORACLE_FIRE_MARGIN)
    anchor_recovers = bool(h[ANCHOR] == h[ANCHOR] and h[ANCHOR] >= SELFTEST_ANCHOR_MIN)
    anchor_beats_random = bool(anchor_margin == anchor_margin and anchor_margin >= SELFTEST_AC_BEATS_RANDOM)
    scramble_fails = bool(scramble_margin == scramble_margin and scramble_margin >= SELFTEST_SCRAMBLE_MARGIN)
    pop_at_floor = bool(h[POP] == h[POP] and h[POP] <= max(h[RANDOM], 0.05) + CONTROL_LOSE_EPS)
    arms_differ = bool(n_sigs >= 5)

    # VACUOUS-SMOKE guard: the RANDOM null must NOT reach ANCHOR_COMPOSE on the planted held-out arena.
    random_reached_anchor = bool(anchor_margin <= SELFTEST_AC_BEATS_RANDOM)
    assert_discriminator_fires(random_reached_anchor, control_name=RANDOM,
                               headline_name="anchor_compose_beats_random_heldout", run_mode="self_test",
                               extra="RANDOM reached ANCHOR_COMPOSE on the planted held-out-entity arena -> arena "
                                     "not answerable / metric frozen")

    st_verdict, st_msg, st_gates = aggregate_and_verdict([res])

    vp_ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(oracle_recovers and oracle_fires),
         "control_name": "ORACLE_ADDITIVE", "headline_name": "oracle_beats_random_heldout",
         "extra": "planted grid: ORACLE (learned held-out codes) recovers held-out tails and clears RANDOM by the "
                  "fire margin -> the >=0.05 inductive bar is achievable when the entity code exists"},
        {"kind": "metric_moves", "metric_name": "heldout_hits_at_k",
         "values": [h[RANDOM], h[ADDITIVE], h[ANCHOR], h[ORACLE]],
         "extra": "RANDOM=%.3f ADDITIVE=%.3f ANCHOR=%.3f ORACLE=%.3f: held-out readout responds to composed/learned "
                  "codes" % (h[RANDOM], h[ADDITIVE], h[ANCHOR], h[ORACLE])},
        {"kind": "negative_control_margin", "control_scores": [h[RANDOM], h[SCRAMBLE]],
         "headline_threshold": h[ANCHOR], "higher_is_pass": True, "margin": SELFTEST_SCRAMBLE_MARGIN,
         "n_repeats_min": 2, "control_name": "RANDOM_and_ANCHOR_SCRAMBLE_below_anchor",
         "extra": "RANDOM + relation-scrambled ANCHOR must sit below ANCHOR_COMPOSE by the margin on held-out "
                  "queries -> the RELATION operators carry the signal, not anchor identity/degree"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "oracle_fires", "scramble_controlled", "broken_test_guard",
                                    "enough_heldout", "band_gate"],
         "exercised_gates": ["arms_differ", "oracle_fires", "scramble_controlled", "broken_test_guard",
                             "enough_heldout", "band_gate"],
         "extra": "aggregate_and_verdict verdict=%s at self-test scale" % st_verdict},
    ], run_mode="self_test")

    out.update(
        heldout_hits={a: round(h[a], 5) for a in ALL_ARMS},
        n_distinct_sigs=n_sigs, anchor_margin=round(anchor_margin, 5), scramble_margin=round(scramble_margin, 5),
        oracle_margin=round(oracle_margin, 5),
        oracle_recovers=oracle_recovers, oracle_fires=oracle_fires, anchor_recovers=anchor_recovers,
        anchor_beats_random=anchor_beats_random, scramble_fails=scramble_fails, pop_at_floor=pop_at_floor,
        arms_differ=arms_differ, selftest_verdict=st_verdict, validity_preflight_ok=bool(vp_ok),
        support_deg_hist=res.get("localization", {}).get("support_deg_hist"),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest"],
    )
    ok = bool(oracle_recovers and oracle_fires and anchor_recovers and anchor_beats_random
              and scramble_fails and pop_at_floor and arms_differ)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def _resolve_device(arg_device):
    env_queue = os.environ.get("HDLAB_QUEUE", "")
    env_dev = os.environ.get("HDLAB_DEVICE", "")
    force_cpu = (arg_device == "cpu") or (env_dev == "cpu") or (env_queue == "remote_cpu_queue")
    if force_cpu:
        return torch.device("cpu")
    want_cuda = (arg_device in ("auto", "cuda")) or (env_dev == "cuda")
    return torch.device("cuda" if (want_cuda and torch.cuda.is_available()) else "cpu")


def core_main(run_mode, device):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "memsmoke": MEMSMOKE_CFG, "full": FULL_CFG}[run_mode])
    seeds = [7] if run_mode == "self_test" else cfg["seeds"]
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=%s cuda=%s run_mode=%s seeds=%s k=%s epochs=%s" %
         (device, torch.cuda.is_available(), run_mode, seeds, cfg["k"], cfg["epochs"]))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s anchor_margin=%s scramble_margin=%s oracle_fires=%s vp_ok=%s heldout_hits=%s" %
         (st_ok, st_res.get("anchor_margin"), st_res.get("scramble_margin"), st_res.get("oracle_fires"),
          st_res.get("validity_preflight_ok"), st_res.get("heldout_hits")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (ANCHOR_COMPOSE did not recover/beat-random, or scramble did not "
                        "fail, or ORACLE did not fire, or POP not at floor, or arms not distinct): %s"
                        % st_res.get("fail", ""),
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS ANCHOR_COMPOSE inductive probe: zero-training bundle recovers planted held-out "
                        "tails and clears RANDOM; relation-scramble fails; ORACLE fires; POP at floor; 4 validity-"
                        "preflight checks declared",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    if not _ensure_cskg():
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    per_seed, seed_failures = [], []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(
                cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
            pool = list(train_lbl) + list(valid_lbl) + list(test_lbl)
            _log("cskg seed=%d core_nodes=%d core_edges=%d avgdeg=%.1f rels=%d pool_edges=%d"
                 % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["core_avgdeg"],
                    prov["n_rel_tokens"], len(pool)))
            res = run_corpus(pool, cfg, device, seed, "CSKG_CORE_HELDOUT_ENTITY", ckpt_dir=out_dir, localize=True)
            res["cskg_provenance"] = prov
            if res.get("empty") or res["n_query_scored"] < cfg.get("min_heldout", MIN_HELDOUT):
                raise RuntimeError("held-out-entity query edges too few (%d < %d)" %
                                   (res.get("n_query_scored", 0), cfg.get("min_heldout", MIN_HELDOUT)))
            sigset = set(res["arm_sigs"].values())
            if len(sigset) < 5:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct sigs" % (seed, len(sigset)))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            cleanup_seed_checkpoints(out_dir, seed)
            ah = res["arm_hits"]
            _log("seed=%d nq=%d n_sup=%d n_cold=%d | h@%d ANCHOR=%s ADDITIVE=%s ONESHOT=%s RANDOM=%s SCRAMBLE=%s "
                 "ORACLE=%s POP=%s (%.1fs)" %
                 (seed, res["n_query_scored"], res["n_support"], res["n_cold"], PRIMARY_K,
                  _fmt(ah[ANCHOR][PRIMARY_METRIC]), _fmt(ah[ADDITIVE][PRIMARY_METRIC]), _fmt(ah[ONESHOT][PRIMARY_METRIC]),
                  _fmt(ah[RANDOM][PRIMARY_METRIC]), _fmt(ah[SCRAMBLE][PRIMARY_METRIC]), _fmt(ah[ORACLE][PRIMARY_METRIC]),
                  _fmt(ah[POP][PRIMARY_METRIC]), time.time() - ts))
            _hb("cskg", si)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))
        finally:
            if getattr(device, "type", "") == "cuda":
                torch.cuda.empty_cache()

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=seeds, config=cfg, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "memsmoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--memsmoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("memsmoke" if args.memsmoke else args.run_mode)
    # Honor HDLAB_RUN_MODE only when no explicit argv mode was given (the runner injects "full"; an orchestrator
    # one-shot may inject "memsmoke"/"self_test"). Bare queue dispatch -> full. argv flags always win.
    if not args.self_test and not args.memsmoke and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "memsmoke", "full"):
            run_mode = _env_mode
    device = _resolve_device(args.device)
    out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(run_mode, device)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
