"""CONSOLIDATION x INDUCTIVE (real CSKG): does INTERLEAVED-replay manufacture NOVEL-ENTITY inference structure on
REAL reduced-CSKG, beating COMPUTE-MATCHED task-blocked CONTINUAL and a FAIR FREQUENCY baseline?

ENVELOPE-PUSH of the construction-proof cell exp_consol_interleaved_replay_v1 (commit a6d93fbae, BELIEVED
construction-proof). That cell had TWO honest bounds the FULL VET flagged: (a) TRANSDUCTIVE split (held-out =
novel (head,rel) PAIRS, both endpoints individually seen -- NOT novel-entity); (b) a PLANTED hierarchical arena
matched to the additive/TransE readout's inductive bias. This cell removes BOTH:
  (1) ARENA  = REAL reduced-CSKG k-core (NOT a planted synthetic).
  (2) SPLIT  = INDUCTIVE, hold out ENTITIES entirely. A held-out entity appears ONLY as a HEAD in edges
               (h_held, r, t_seen) whose TAIL is a SEEN entity; the held-out head has NO trained code and its
               edges are NEVER in train. Its query tail (a SEEN, frequency-having entity) is predicted from the
               entity's OWN support edges to seen anchors via the frozen scaffold -- genuine novel-ENTITY inference.
               Predicting a SEEN tail (not the novel entity itself) makes the FREQUENCY baseline a FAIR, informative,
               beatable BAR (the VET named frequency as the bar to clear).

THE MECHANISM UNDER TEST = the batch SCHEDULE that produces the frozen scaffold (X entity codes, D relation
displacements). ALL arms fit the SAME additive/TransE model with the SAME CE self-adversarial loss and the SAME
TOTAL GRADIENT-STEP BUDGET; the ONLY difference is HOW the scaffold is fit:
  INTERLEAVED : i.i.d. minibatch SGD over ALL train edges, P_max passes (replay/consolidation).  THE MECHANISM.
  CONTINUAL   : task-blocked by DOMAIN (a deterministic entity-group partition), P_max passes PER domain in order,
                NO replay. COMPUTE-MATCHED: each edge is trained P_max times in BOTH arms (equal total steps), so a
                beat cannot be a compute artifact (the VET predicts compute-matched continual forgets WORSE).
  SHUFFLE     : interleaved schedule but the arena's relational structure DESTROYED (train tails randomized) ->
                the scaffold carries no transferable relational signal -> inductive lift must stay flat.  MUST-FAIL.
The INDUCTIVE READOUT (identical across the 3 scaffold arms) is ZERO-training ANCHOR-COMPOSE: a held-out head's
code is reconstructed as E_derived[h] = mean_i(X[t_i] - D[r_i]) over its support edges (h, r_i, t_i) (TransE head
estimate; degree-invariant bundle), then the query (h, r_q, ?) is scored by the REAL additive readout
additive_direct_scores (score(c) = -||E_derived[h] + D[r_q] - X[c]||) over ALL candidate tails, filtered-MRR ranked.

NON-SCAFFOLD REFERENCE ARMS (same readout / fair bar / ceiling):
  SCRAMBLE    : ANCHOR-COMPOSE on the INTERLEAVED scaffold with support RELATION ids scrambled -> isolates whether
                the RELATION operators carry the signal vs an anchor-identity/degree confound.  MUST-FAIL.
  RANDOM      : random-init X + random D + the same readout = the chance null.
  ORACLE      : transductive interleaved fit with the held-out entities FOLDED IN (codes LEARNED) = info-ceiling /
                arena-answerable positive control. If ORACLE does not fire, the arena is not answerable (gated
                INCONCLUSIVE, not a substrate negative).
  POP_RELFREQ : rank the gold SEEN tail by per-relation tail frequency = the FAIR FREQUENCY BAR (VET named).

CEILING-AWARE, DEGREE-UNBIASED eval (info-ceiling discipline): primary metric = FILTERED MRR rank-vs-ALL (KGE
standard, no sampled-negative pool -> no popularity/degree bias). The held-out-ENTITY arena has an info-ceiling; the
ANCHOR bands are FRACTIONS of the MEASURED oracle headroom H = ORACLE_mrr - RANDOM_mrr, so ONE FULL run computes the
ceiling AND scores against a fair fraction of it.

PRE-REG BANDS (picked BEFORE the run; see preregs/2026-07-14_consol_inductive_entity_replay_cskg_v1.md;
H = MEASURED oracle headroom):
  ORACLE-FIRES (arena answerable): ORACLE_mrr >= 3.0x RANDOM_mrr AND (ORACLE_mrr - RANDOM_mrr) >= 0.003.
  HARD_PASS : INTERLEAVED beats CONTINUAL by >= max(0.10*H, 0.003) MRR AND beats POP_RELFREQ by >= max(0.10*H,
              0.003) AND recovers >= 0.30*H of the oracle headroom over RANDOM AND ORACLE fires AND must-fails fire
              (SHUFFLE and SCRAMBLE within 0.25*H of RANDOM) AND sub-ceiling (INTERLEAVED_mrr < ORACLE_mrr) AND not
              broken AND holds on a majority of seeds.
  REFUTE    : ORACLE fires AND (INTERLEAVED - CONTINUAL <= 0.001 OR INTERLEAVED - POP_RELFREQ <= 0.001) -- replay
              does NOT beat compute-matched continual OR does NOT beat frequency on real+inductive. A VALUABLE,
              drill-worthy negative about what consolidation can/can't do on real data. Reported honestly, not forced.
  MIDDLE    : ORACLE fires, beats both by > 0.001 but below the HARD_PASS margins (partial transfer).
  INCONCLUSIVE: ORACLE does not fire (arena not answerable / underfit) or too few held-out queries or broken control.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): the 7 arms produce >=5 distinct score signatures per seed.
# - final_metrics_atomicity = tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: raw hits@K-vs-all-N has a ceiling; FIX = primary metric FILTERED MRR + ceiling-RELATIVE
#   bands (fractions of the MEASURED oracle headroom H). discriminator_reachability: bands scale to whatever H the
#   FULL measures; the ORACLE positive control proves the metric can move at scale.
# - baseline_in_band (META_RULE_AG): ORACLE must fire (>=3x RANDOM_mrr AND headroom>=0.003); RANDOM/POP near floor;
#   INTERLEAVED strictly between (self-test asserts POP<=INTERLEAVED<=ORACLE and 0<RANDOM band).
# - discriminator survives scale: self-test fires INTERLEAVED-beats-CONTINUAL + beats-RANDOM + SHUFFLE/SCRAMBLE-flat
#   directionally on the planted hierarchical arena; analytical (B): compute-matched task-blocking forgets shared
#   D[r]/cross-domain X at ANY N, and a random-init scaffold cannot compose, so the ordering persists at scale.
# - HARD_PASS strictly above floor: margins are FRACTIONS of H + an absolute MIN_SIG_MRR floor (not >=0).
# - HP_SCOPE: the beat gates apply to INTERLEAVED only. ORACLE=positive control (must fire); RANDOM/SHUFFLE/SCRAMBLE
#   =must-not-clear-bar controls; CONTINUAL=the compute-matched head-to-head; POP_RELFREQ=the fair frequency bar.
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all 7 arms + >=5 distinct sigs.
# - per-unit failure-class instrumentation (META_RULE_J; no bare except; per-seed failure_class recorded).
# - calibration_check = adaptive_with_discriminator_gate: all FRACs/eps pre-registered, NOT tuned on real data; the
#   beat targets are FRACTIONS OF THE MEASURED oracle headroom H (computed in-run), not fixed thresholds.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the prereg.
# - real_code_path: self-test EXERCISES the REAL readout/eval substrate primitives (additive_direct_scores,
#   filtered_hits_from_scores, pop_hits, build_ids, _to_int_edges) via run_corpus on the planted arena; the REAL
#   CSKG loader build_cskg_core_triples is exercised by the local MEMSMOKE gate before ship.
# - substrate_signature binds additive_direct_scores against inspect.signature; base/portable positional args only.
# - guard_baseline_valid: the beats-POP guard is validated against POP being above the RANDOM/chance floor (head-
#   holdout keeps POP informative, unlike tail-holdout where POP is a structural zero).
# - deterministic integer seeds only; no salted-hash / list(set()) seeding (PROT-023 static scan runs on ship).
# - progress_logging: line_buffered_stdout + per-seed/per-arm flush prints (FULL timeout_s >= 1800).

ASCII-only. Explicit float32. Deterministic integer seeds. No bare except; except SystemExit before except Exception.
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np
import torch
import torch.nn.functional as F

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, write_partial, assert_discriminator_fires,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from experiments.exp_gt_induction_fb15k237_dense_v1 import build_ids  # noqa: E402
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, filtered_hits_from_scores, pop_hits, PRIMARY_K,
)
from experiments._course_c_rotate_core_v1 import additive_direct_scores  # noqa: E402

ANCHOR_NAME = "consol_inductive_entity_replay_cskg_v1"

# ---- Arm names ----
INTERLEAVED = "INTERLEAVED"      # mechanism: i.i.d. replay SGD scaffold
CONTINUAL = "CONTINUAL"          # compute-matched task-blocked scaffold (catastrophic-forgetting head-to-head)
SHUFFLE = "SHUFFLE"              # structure-destroyed-train scaffold (must stay flat)
SCRAMBLE = "SCRAMBLE"            # relation-scrambled anchor-compose on the interleaved scaffold (must-fail)
RANDOM = "RANDOM"                # random-init scaffold + readout (chance null)
ORACLE = "ORACLE"                # transductive interleaved, held-out folded in (info-ceiling positive control)
POP = "POP_RELFREQ"              # fair frequency bar
SCAFFOLD_ARMS = [INTERLEAVED, CONTINUAL, SHUFFLE]
ALL_ARMS = [INTERLEAVED, CONTINUAL, SHUFFLE, SCRAMBLE, RANDOM, ORACLE, POP]

# ---- Pre-registered bands (HYPOTHESIZED; ceiling-relative -- resolved to absolute MRR from MEASURED H) ----
ORACLE_FIRE_RATIO = 3.0          # ORACLE_mrr >= 3x RANDOM_mrr (scale-free arena-answerable gate)
ORACLE_FIRE_ABS = 0.003          # AND ORACLE_mrr - RANDOM_mrr >= this (non-noise absolute floor)
MIN_SIG_MRR = 0.003              # absolute significance floor the beat margins must ALSO clear
HP_CEIL_FRAC = 0.30              # HARD_PASS: (INTERLEAVED - RANDOM)_mrr >= 30% of H
BEAT_CONT_FRAC = 0.10            # HARD_PASS: (INTERLEAVED - CONTINUAL)_mrr >= max(10% of H, MIN_SIG)
BEAT_POP_FRAC = 0.10             # HARD_PASS: (INTERLEAVED - POP)_mrr >= max(10% of H, MIN_SIG)
DOSE_FRAC = 0.10                 # supporting signature: INTERLEAVED mrr(P_max) - mrr(P=1) >= 10% of H
FLAT_FRAC = 0.25                 # must-fail: (SHUFFLE - RANDOM) and (SCRAMBLE - RANDOM) <= 25% of H
REFUTE_EPS = 0.001               # <= this beat over CONTINUAL or POP (with ORACLE firing) -> REFUTE
CONTROL_LOSE_EPS = 0.005         # broken guard: a null control beating POP by > max(this, FLAT_FRAC*H) = degenerate
MIN_HELDOUT = 20                 # min held-out QUERY edges for a valid discriminator
MIN_STEP_MATCH = 0.02            # |steps_interleaved - steps_continual| / steps_interleaved must be <= this
EVAL_KS = (1, 3, 10, 100)
CEIL_METRIC = "mrr"
PRIMARY_METRIC = "hits@%d" % PRIMARY_K

# ---- self-test planted thresholds (relaxed; calibrated on the planted TransE arena, NOT real data) ----
ST_ORACLE_MRR_MIN = 0.30         # planted: ORACLE (learned held-out codes) mrr at least this
ST_INTER_MRR_MIN = 0.12          # planted: INTERLEAVED anchor-compose mrr at least this
ST_INTER_BEATS_RANDOM = 0.06     # planted: (INTERLEAVED - RANDOM)_mrr >= this
ST_INTER_BEATS_CONT = 0.02       # planted: (INTERLEAVED - CONTINUAL)_mrr >= this (forgetting fires -> achievable)
ST_INTER_BEATS_POP = 0.005       # planted: (INTERLEAVED - POP)_mrr >= this (relational beats frequency -> achievable)
ST_SCRAMBLE_MARGIN = 0.02        # planted: (INTERLEAVED - SCRAMBLE)_mrr >= this (relation operators carry signal)
ST_SHUFFLE_MARGIN = 0.04         # planted: (INTERLEAVED - SHUFFLE)_mrr >= this (structure carries signal)
ST_MIN_HO = 8                    # planted: minimum held-out QUERY edges

SCORE_CHUNK = 256

# ---- Config profiles (self_test = planted TransE arena; memsmoke/full = REAL reduced CSKG k-core) ----
# CONTINUAL blocks by RELATION-BUCKET (relation-incremental continual, a standard CL-KGE protocol): each block is
# a group of relations; the shared ENTITY codes are contested across blocks (an entity appears in many relations,
# esp. on cross-cutting CSKG edges), so sequential blocking drags entity codes toward the last relation-block and
# forgets early-relation structure -> degraded inductive anchor-compose for early-relation support. INTERLEAVED
# co-adapts all codes with all relations throughout. compute-matched: each edge trained P_max times in both arms.
SELFTEST_CFG = dict(mode="planted", n_ent=500, n_rel=10, k_lat=10, deg=5,
                    k=24, P_max=20, n_neg=16, batch=256, lr=0.05, g_domains=5,
                    heldout_entity_frac=0.20, support_frac=0.5, n_heldout_eval=0,
                    checkpoints=[1, 2, 4, 8, 14, 20], min_heldout=ST_MIN_HO, step_match_tol=0.30, seeds=[7])
# MEMSMOKE = REAL CSKG reduced core, few passes, 1 seed, small eval. Proves the REAL loader+fit+readout+verdict path
# runs end-to-end without OOM/error BEFORE the multi-seed FULL. NOT a discriminator gate (few passes under-train).
MEMSMOKE_CFG = dict(mode="cskg", k_core=30, cskg_max_lines=0, cskg_max_nodes=0,
                    k=24, P_max=4, n_neg=32, batch=1024, lr=0.05, g_domains=4,
                    heldout_entity_frac=0.15, support_frac=0.5, n_heldout_eval=500,
                    checkpoints=[1, 2, 4], min_heldout=10, step_match_tol=0.10, seeds=[7])
FULL_CFG = dict(mode="cskg", k_core=30, cskg_max_lines=0, cskg_max_nodes=0,
                k=32, P_max=20, n_neg=32, batch=1024, lr=0.05, g_domains=4,
                heldout_entity_frac=0.15, support_frac=0.5, n_heldout_eval=2000,
                checkpoints=[1, 2, 4, 8, 14, 20], min_heldout=MIN_HELDOUT, step_match_tol=0.02,
                seeds=[7, 13, 17, 23, 29])

GAMMA = 9.0
ADV_TEMP = 1.0


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _sig(arr):
    a = np.round(np.asarray(arr, dtype=np.float64), 4)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Defensive-error-checking helpers.
# ---------------------------------------------------------------------------

def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
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
# Planted HIGH-intrinsic-dim TransE-consistent arena (self-test only; copied from the VET'd inductive-entity cell
# exp_anchor_compose_inductive_entity_cskg_v1 build_planted_transe_arena). Entities get random latents z ~ N(0,I) in
# k_lat dims; relations get random translations w_r; edge (h,r,t) connects h to the entity NEAREST to z[h]+w[r]. A
# held-out entity is recovered ONLY by mean_i(z[t_i]-w[r_i])==z[h] (anchor-compose); scrambling relations offsets the
# bundle -> the must-fail control genuinely fails. The additive fit rediscovers a consistent embedding; DIVERSE tails
# keep POP a fair, beatable bar. deterministic (default_rng(seed) + order-preserving dedup). Returns label triples.
# ---------------------------------------------------------------------------

def build_planted_transe_arena(cfg, seed):
    n_ent, n_rel = int(cfg["n_ent"]), int(cfg["n_rel"])
    k_lat, deg = int(cfg["k_lat"]), int(cfg["deg"])
    rng = np.random.default_rng(seed * 100019 + 3)
    z = rng.standard_normal((n_ent, k_lat))
    w = rng.standard_normal((n_rel, k_lat))
    edges = []
    for h in range(n_ent):
        rels = rng.choice(n_rel, size=deg, replace=False)
        for r in rels:
            target = z[h] + w[r]
            d = np.linalg.norm(z - target, axis=1)
            d[h] = np.inf
            t = int(np.argmin(d))
            edges.append(("e%d" % h, "r%d" % r, "e%d" % t))
    return list(dict.fromkeys(edges))   # order-preserving dedup (NOT set-based dedup; cross-process determinism)


# ---------------------------------------------------------------------------
# INDUCTIVE held-out-HEAD split. Hold out a fraction of HEAD-appearing entities; a held-out entity keeps ONLY edges
# where it is the HEAD and the TAIL is a SEEN entity; partition those into SUPPORT (build E_derived) + QUERY (scored),
# disjoint (no leakage). train = both-endpoints-seen edges. deterministic integer seeds only.
# ---------------------------------------------------------------------------

def build_heldout_head_split(pool_int, N, frac, support_frac, seed):
    head_ids = sorted(set(int(h) for h in pool_int[:, 0].tolist()))
    rng = np.random.default_rng(seed * 100003 + 7)
    n_hold = max(1, int(frac * len(head_ids)))
    perm = rng.permutation(len(head_ids))
    hold_ids = set(int(head_ids[perm[i]]) for i in range(n_hold))

    train_rows, held_by_head = [], defaultdict(list)
    for i in range(pool_int.shape[0]):
        h = int(pool_int[i, 0]); t = int(pool_int[i, 2])
        h_hold = h in hold_ids; t_hold = t in hold_ids
        if not h_hold and not t_hold:
            train_rows.append(i)
        elif h_hold and not t_hold:
            held_by_head[h].append(i)
    support_rows, query_rows, n_cold = [], [], 0
    rng2 = np.random.default_rng(seed * 991 + 5)
    for hh in sorted(held_by_head.keys()):
        rows = held_by_head[hh]
        d = len(rows)
        if d == 1:
            query_rows.append(rows[0]); n_cold += 1
            continue
        order = rng2.permutation(d)
        n_sup = max(1, int(round(support_frac * d)))
        n_sup = min(n_sup, d - 1)
        sup_idx = set(int(x) for x in order[:n_sup].tolist())
        for j, rr in enumerate(rows):
            (support_rows if j in sup_idx else query_rows).append(rr)
    train_int = pool_int[np.array(sorted(train_rows), dtype=np.int64)] if train_rows else np.zeros((0, 3), np.int64)
    support_int = pool_int[np.array(sorted(support_rows), dtype=np.int64)] if support_rows else np.zeros((0, 3), np.int64)
    query_int = pool_int[np.array(sorted(query_rows), dtype=np.int64)] if query_rows else np.zeros((0, 3), np.int64)
    return train_int, support_int, query_int, hold_ids, n_cold


def assign_domains(train_int, n_rel, g_domains, seed):
    """Deterministic RELATION-bucket partition (relation-incremental continual). Each relation -> one of g_domains
    buckets; edge domain = its relation's bucket. The shared ENTITY codes are contested across buckets (entities
    appear in many relations, esp. on cross-cutting CSKG edges), so sequential blocking forgets early-relation
    structure in the codes. Returns per-train-edge domain (bucket) id."""
    rng = np.random.default_rng(seed * 7717 + 13)
    rel_bucket = rng.integers(0, int(g_domains), size=int(n_rel)).astype(np.int64)
    return rel_bucket[train_int[:, 1]]


def destroy_structure(train_int, N, seed):
    """SHUFFLE control: replace each train edge's TAIL with a random entity (kills relational signal)."""
    rng = np.random.default_rng(seed * 100057 + 19)
    out = train_int.copy()
    out[:, 2] = rng.integers(0, N, size=train_int.shape[0]).astype(np.int64)
    return out


# ---------------------------------------------------------------------------
# Consolidation-aware additive/TransE fit (the mechanism). CE self-adversarial loss + uniform-random negatives.
# ---------------------------------------------------------------------------

def _init_coords(N, n_rel, k, seed, device):
    g = torch.Generator(device="cpu").manual_seed(int(seed) * 7919 + 11)
    X = (torch.randn(N, k, generator=g, dtype=torch.float32) * 0.1).to(device).requires_grad_(True)
    D = (torch.randn(n_rel, k, generator=g, dtype=torch.float32) * 0.1).to(device).requires_grad_(True)
    return X, D


def _batch_loss(X, D, hb, rb, tb, N, n_neg, gneg, device):
    pred = X[hb] + D[rb]                                            # (b,k)
    pos_score = GAMMA - torch.norm(pred - X[tb], dim=1)            # (b,)
    neg_t = torch.randint(0, N, (hb.shape[0], n_neg), generator=gneg).to(device)   # (b,n_neg)
    neg_score = GAMMA - torch.norm(pred.unsqueeze(1) - X[neg_t], dim=2)            # (b,n_neg)
    with torch.no_grad():
        w = torch.softmax(ADV_TEMP * neg_score, dim=1)
    pos_loss = -F.logsigmoid(pos_score)
    neg_loss = -(w * F.logsigmoid(-neg_score)).sum(dim=1)
    return (pos_loss + neg_loss).mean()


def fit_schedule(train_int, N, n_rel, cfg, schedule, seed, device, domain_of=None, extra_int=None):
    """Fit X,D under a batch SCHEDULE. Returns (snaps dict {pass_or_'final': (X_np,D_np)}, n_steps).

    INTERLEAVED / SHUFFLE / ORACLE : i.i.d. minibatch over all edges (ORACLE folds extra_int in), P_max passes.
    CONTINUAL : domain-blocked, P_max passes PER domain in order (each edge trained P_max times = compute-matched).
    """
    k, P_max, n_neg, batch = int(cfg["k"]), int(cfg["P_max"]), int(cfg["n_neg"]), int(cfg["batch"])
    checkpoints = sorted(set(int(c) for c in cfg["checkpoints"]))
    ed = train_int
    if extra_int is not None and extra_int.shape[0] > 0:
        ed = np.concatenate([train_int, extra_int], axis=0)

    torch.manual_seed(int(seed) * 13 + 1)
    gneg = torch.Generator(device="cpu").manual_seed(int(seed) * 17 + 3)
    gperm = np.random.default_rng(int(seed) * 333 + 9)
    X, D = _init_coords(N, n_rel, k, seed, device)
    opt = torch.optim.Adam([X, D], lr=float(cfg["lr"]))

    h_all = torch.from_numpy(ed[:, 0]).long().to(device)
    r_all = torch.from_numpy(ed[:, 1]).long().to(device)
    t_all = torch.from_numpy(ed[:, 2]).long().to(device)

    def snap():
        return (X.detach().cpu().numpy().astype(np.float32), D.detach().cpu().numpy().astype(np.float32))

    def run_block(rows, n_passes):
        n_steps = 0
        for _p in range(n_passes):
            order = torch.from_numpy(gperm.permutation(rows.shape[0])).long()
            rr = rows[order]
            for s in range(0, rr.shape[0], batch):
                bidx = rr[s:s + batch].to(device)
                opt.zero_grad()
                loss = _batch_loss(X, D, h_all[bidx], r_all[bidx], t_all[bidx], N, n_neg, gneg, device)
                loss.backward()
                opt.step()
                n_steps += 1
        return n_steps

    snaps, total_steps = {}, 0
    if schedule == CONTINUAL:
        assert domain_of is not None, "CONTINUAL requires domain_of"
        g_dom = int(cfg["g_domains"])
        for d in range(g_dom):
            mask = np.where(domain_of == d)[0]
            if mask.shape[0] == 0:
                continue
            total_steps += run_block(torch.from_numpy(mask).long(), P_max)
        snaps["final"] = snap()
        return snaps, total_steps

    # INTERLEAVED / SHUFFLE / ORACLE: i.i.d. replay over all edges, snapshot at checkpoints (dose trajectory)
    all_rows = torch.arange(ed.shape[0], dtype=torch.long)
    for p in range(1, P_max + 1):
        total_steps += run_block(all_rows, 1)
        if p in checkpoints:
            snaps[p] = snap()
    snaps["final"] = snap()
    if P_max not in snaps:
        snaps[P_max] = snaps["final"]
    return snaps, total_steps


# ---------------------------------------------------------------------------
# INDUCTIVE anchor-compose readout: E_derived[h_held] = mean over support edges of (X[t] - D[r]). Real additive read.
# ---------------------------------------------------------------------------

def build_anchor_head_codes(X, D, support_int, device, rel_perm=None):
    N, k = X.shape[0], X.shape[1]
    Xp = X.clone()
    support_deg = np.zeros(N, dtype=np.int64)
    if support_int.shape[0] == 0:
        return Xp, support_deg
    r_np = support_int[:, 1].copy()
    if rel_perm is not None:
        r_np = rel_perm[r_np]
    h = torch.from_numpy(support_int[:, 0]).long().to(device)
    r = torch.from_numpy(r_np).long().to(device)
    t = torch.from_numpy(support_int[:, 2]).long().to(device)
    est = X[t] - D[r]                                              # TransE head estimate per support edge
    acc = torch.zeros(N, k, device=device, dtype=X.dtype)
    acc.index_add_(0, h, est)
    cnt = torch.zeros(N, device=device, dtype=X.dtype)
    cnt.index_add_(0, h, torch.ones(h.shape[0], device=device, dtype=X.dtype))
    mask = cnt > 0
    Xp[mask] = acc[mask] / cnt[mask].unsqueeze(1)
    support_deg = cnt.detach().to("cpu").numpy().astype(np.int64)
    return Xp, support_deg


def _score_arm(Xtab, Dtab, query_int, all_true, device):
    sc = additive_direct_scores(Xtab, Dtab, query_int, device, chunk=SCORE_CHUNK)
    metric = filtered_hits_from_scores(sc, query_int, all_true, ks=EVAL_KS)
    sig = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
    return metric, sig, sc


# ---------------------------------------------------------------------------
# One corpus run: split -> fit scaffolds -> anchor-compose readout -> score all arms PAIRED on the same query edges.
# ---------------------------------------------------------------------------

def run_corpus(pool_lbl, cfg, device, seed, corpus_name):
    ent2i, rel2i = build_ids(pool_lbl, [], [])
    N, n_rel = len(ent2i), len(rel2i)
    pool_int = _to_int_edges(pool_lbl, ent2i, rel2i)
    train_int, support_int, query_int, hold_ids, n_cold = build_heldout_head_split(
        pool_int, N, cfg["heldout_entity_frac"], cfg["support_frac"], seed)
    n_query_total = int(query_int.shape[0])

    if cfg.get("n_heldout_eval") and n_query_total > cfg["n_heldout_eval"]:
        rng = np.random.default_rng(seed * 777 + 3)
        idx = sorted(rng.choice(n_query_total, size=cfg["n_heldout_eval"], replace=False).tolist())
        query_int = query_int[np.array(idx, dtype=np.int64)]

    result = dict(corpus=corpus_name, seed=int(seed), N=int(N), n_rel=int(n_rel), n_train=int(train_int.shape[0]),
                  n_heldout_entities=len(hold_ids), n_support=int(support_int.shape[0]),
                  n_query_total=n_query_total, n_query_scored=int(query_int.shape[0]), n_cold=int(n_cold),
                  heldout_entity_frac=cfg["heldout_entity_frac"], support_frac=cfg["support_frac"])
    if query_int.shape[0] < 1 or train_int.shape[0] < 1:
        result["empty"] = True
        return result

    all_true = build_true_by_hr_int(train_int, support_int, query_int)
    rel_tail_freq = defaultdict(Counter)
    node_degree = Counter()
    for i in range(train_int.shape[0]):
        h = int(train_int[i, 0]); r = int(train_int[i, 1]); t = int(train_int[i, 2])
        rel_tail_freq[r][t] += 1
        node_degree[h] += 1; node_degree[t] += 1

    domain_of = assign_domains(train_int, n_rel, int(cfg["g_domains"]), seed)
    shuf_train = destroy_structure(train_int, N, seed)
    hold_all = np.concatenate([support_int, query_int], axis=0)

    # ---- fit the scaffolds ----
    inter_snaps, steps_inter = fit_schedule(train_int, N, n_rel, cfg, INTERLEAVED, seed, device)
    cont_snaps, steps_cont = fit_schedule(train_int, N, n_rel, cfg, CONTINUAL, seed, device, domain_of=domain_of)
    shuf_snaps, steps_shuf = fit_schedule(shuf_train, N, n_rel, cfg, SHUFFLE, seed, device)
    orac_snaps, steps_orac = fit_schedule(train_int, N, n_rel, cfg, ORACLE, seed, device, extra_int=hold_all)
    step_mismatch = abs(steps_inter - steps_cont) / max(1, steps_inter)
    compute_matched = bool(step_mismatch <= float(cfg.get("step_match_tol", MIN_STEP_MATCH)))

    Xi, Di = (torch.from_numpy(a).to(device) for a in inter_snaps["final"])
    Xc, Dc = (torch.from_numpy(a).to(device) for a in cont_snaps["final"])
    Xs, Ds = (torch.from_numpy(a).to(device) for a in shuf_snaps["final"])
    Xo, Do = (torch.from_numpy(a).to(device) for a in orac_snaps["final"])
    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)
    Xr = (torch.randn(N, cfg["k"], generator=gR) * 0.1).to(device)
    Dr = (torch.randn(n_rel, cfg["k"], generator=gR) * 0.1).to(device)

    # ---- inductive anchor-compose readouts (paired on the same query edges) ----
    rel_perm = np.random.default_rng(seed * 4441 + 17).permutation(n_rel)
    Xi_ac, support_deg = build_anchor_head_codes(Xi, Di, support_int, device)
    Xc_ac, _ = build_anchor_head_codes(Xc, Dc, support_int, device)
    Xs_ac, _ = build_anchor_head_codes(Xs, Ds, support_int, device)
    Xi_scr, _ = build_anchor_head_codes(Xi, Di, support_int, device, rel_perm=rel_perm)
    Xr_ac, _ = build_anchor_head_codes(Xr, Dr, support_int, device)

    arm_metric, arm_sig = {}, {}
    for name, (Xt, Dt) in [
        (INTERLEAVED, (Xi_ac, Di)), (CONTINUAL, (Xc_ac, Dc)), (SHUFFLE, (Xs_ac, Ds)),
        (SCRAMBLE, (Xi_scr, Di)), (RANDOM, (Xr_ac, Dr)),
    ]:
        m, sg, _ = _score_arm(Xt, Dt, query_int, all_true, device)
        arm_metric[name] = m; arm_sig[name] = sg
    # ORACLE: held-out head now has a LEARNED code in Xo (no anchor-compose needed) -> transductive ceiling
    mo, sgo, _ = _score_arm(Xo, Do, query_int, all_true, device)
    arm_metric[ORACLE] = mo; arm_sig[ORACLE] = sgo
    # POP_RELFREQ: fair frequency bar
    pop_m, pop_rank = pop_hits(rel_tail_freq, query_int, all_true, N, ks=EVAL_KS)
    arm_metric[POP] = pop_m; arm_sig[POP] = _sig(pop_rank.astype(np.float64))

    # ---- dose-response trajectory (INTERLEAVED anchor-compose MRR over replay passes) ----
    dose_traj = {}
    for p in sorted(set(int(c) for c in cfg["checkpoints"])):
        if p in inter_snaps:
            Xp = torch.from_numpy(inter_snaps[p][0]).to(device)
            Dp = torch.from_numpy(inter_snaps[p][1]).to(device)
            Xp_ac, _ = build_anchor_head_codes(Xp, Dp, support_int, device)
            mp, _, _ = _score_arm(Xp_ac, Dp, query_int, all_true, device)
            dose_traj[str(p)] = round(mp["mrr"], 6)

    result.update(
        arm_hits={a: {kk: round(vv, 6) for kk, vv in arm_metric[a].items() if kk != "n"} for a in ALL_ARMS},
        arm_n={a: arm_metric[a]["n"] for a in ALL_ARMS},
        arm_sigs=arm_sig, dose_traj=dose_traj,
        steps_interleaved=int(steps_inter), steps_continual=int(steps_cont),
        steps_shuffle=int(steps_shuf), steps_oracle=int(steps_orac),
        step_mismatch=round(step_mismatch, 5), compute_matched=compute_matched,
        support_deg_hist={"cold": int((support_deg == 0).sum()), "d1": int((support_deg == 1).sum()),
                          "d2_3": int(((support_deg >= 2) & (support_deg <= 3)).sum()),
                          "d4plus": int((support_deg >= 4).sum())},
    )
    del Xi, Di, Xc, Dc, Xs, Ds, Xo, Do, Xr, Dr, Xi_ac, Xc_ac, Xs_ac, Xi_scr, Xr_ac
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    return result


# ---------------------------------------------------------------------------
# Aggregate + verdict.
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _m(ps, arm):
    return ps["arm_hits"][arm].get(CEIL_METRIC, float("nan"))


def _ratio(a, b):
    if not (a == a and b == b):
        return float("nan")
    return float("inf") if b <= 0 else a / b


def _sub(a, b):
    return (a - b) if (a == a and b == b) else float("nan")


def aggregate_and_verdict(per_seed):
    m = {a: _nm([_m(ps, a) for ps in per_seed]) for a in ALL_ARMS}
    n_query = int(_nm([ps["n_query_scored"] for ps in per_seed]))
    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]
    spectrum = {a: {mk: _nm([ps["arm_hits"][a].get(mk, float("nan")) for ps in per_seed]) for mk in metric_keys}
                for a in ALL_ARMS}

    H = _sub(m[ORACLE], m[RANDOM])                                  # MEASURED info-ceiling headroom
    d_cont = _sub(m[INTERLEAVED], m[CONTINUAL])
    d_pop = _sub(m[INTERLEAVED], m[POP])
    d_rand = _sub(m[INTERLEAVED], m[RANDOM])
    d_shuf = _sub(m[SHUFFLE], m[RANDOM])
    d_scr = _sub(m[SCRAMBLE], m[RANDOM])
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])

    # dose lift (mean over seeds): mrr(P_max) - mrr(first checkpoint)
    dose_lifts = []
    for ps in per_seed:
        dt = ps.get("dose_traj", {})
        if len(dt) >= 2:
            ks = sorted(dt.keys(), key=lambda z: int(z))
            dose_lifts.append(dt[ks[-1]] - dt[ks[0]])
    dose_lift = _nm(dose_lifts)

    enough_heldout = bool(n_query >= MIN_HELDOUT)
    oracle_fires = bool(H == H and H >= ORACLE_FIRE_ABS and oracle_ratio == oracle_ratio
                        and oracle_ratio >= ORACLE_FIRE_RATIO)
    compute_matched = all(ps.get("compute_matched", False) for ps in per_seed)

    # ceiling-relative targets from the MEASURED H
    beat_cont_target = (max(BEAT_CONT_FRAC * H, MIN_SIG_MRR) if H == H else float("nan"))
    beat_pop_target = (max(BEAT_POP_FRAC * H, MIN_SIG_MRR) if H == H else float("nan"))
    hp_ceil_target = (HP_CEIL_FRAC * H if H == H else float("nan"))
    dose_target = (DOSE_FRAC * H if H == H else float("nan"))
    flat_target = (FLAT_FRAC * H if H == H else float("nan"))
    broken_margin = (max(CONTROL_LOSE_EPS, FLAT_FRAC * H) if H == H else CONTROL_LOSE_EPS)

    # per-seed majority agreement on the two beats
    need = (len(per_seed) // 2) + 1
    votes_cont = sum(1 for ps in per_seed if _sub(_m(ps, INTERLEAVED), _m(ps, CONTINUAL)) >= 0)
    votes_pop = sum(1 for ps in per_seed if _sub(_m(ps, INTERLEAVED), _m(ps, POP)) >= 0)

    beats_cont = bool(d_cont == d_cont and beat_cont_target == beat_cont_target and d_cont >= beat_cont_target
                      and votes_cont >= need)
    beats_pop = bool(d_pop == d_pop and beat_pop_target == beat_pop_target and d_pop >= beat_pop_target
                     and votes_pop >= need)
    recovers_ceiling = bool(d_rand == d_rand and hp_ceil_target == hp_ceil_target and d_rand >= hp_ceil_target)
    shuffle_flat = bool(d_shuf == d_shuf and flat_target == flat_target and d_shuf <= flat_target)
    scramble_controlled = bool(d_scr == d_scr and flat_target == flat_target and d_scr <= flat_target)
    sub_ceiling = bool(m[INTERLEAVED] == m[INTERLEAVED] and m[ORACLE] == m[ORACLE]
                       and m[INTERLEAVED] < m[ORACLE])
    sig_dose = bool(dose_lift == dose_lift and dose_target == dose_target and dose_lift >= dose_target)
    broken = bool((m[RANDOM] == m[RANDOM] and m[POP] == m[POP] and (m[RANDOM] - m[POP]) > broken_margin)
                  or (m[SHUFFLE] == m[SHUFFLE] and m[POP] == m[POP] and (m[SHUFFLE] - m[POP]) > broken_margin))

    hard_pass = bool(beats_cont and beats_pop and recovers_ceiling and oracle_fires and shuffle_flat
                     and scramble_controlled and sub_ceiling and compute_matched and not broken)
    refute = bool(oracle_fires and ((d_cont == d_cont and d_cont <= REFUTE_EPS)
                                    or (d_pop == d_pop and d_pop <= REFUTE_EPS)))

    if not enough_heldout:
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT"
    elif broken:
        verdict = "BROKEN_TEST_CONTROL_BEATS_POP"
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_ORACLE_UNDERFIT"
    elif not compute_matched:
        verdict = "INCONCLUSIVE_COMPUTE_UNMATCHED"
    elif hard_pass:
        verdict = "HARD_PASS_INDUCTIVE_REPLAY_BEATS_CONTINUAL_AND_FREQ"
    elif refute:
        verdict = "REFUTE_REPLAY_NO_INDUCTIVE_ADVANTAGE"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_INDUCTIVE_ADVANTAGE"

    n_sigs = int(sig_dose) + int(beats_cont) + int(shuffle_flat) + int(scramble_controlled)
    verdict_msg = (
        "%s || INDUCTIVE HELD-OUT MRR [nq=%d]: INTERLEAVED=%s CONTINUAL=%s SHUFFLE=%s SCRAMBLE=%s | RANDOM=%s "
        "ORACLE=%s POP_RELFREQ=%s || H(oracle-random)=%s ratio=%sx (fires=%s) | beat_cont=%s (>=%s=%s) "
        "beat_pop=%s (>=%s=%s) recover=%s (>=%s=%s) | shuffle_flat=%s scramble_ctl=%s sub_ceiling=%s dose_lift=%s "
        "(>=%s) | compute_matched=%s(mism=%s) broken=%s | signatures=%d/4 seeds=%d"
        % (verdict, n_query, _fmt(m[INTERLEAVED]), _fmt(m[CONTINUAL]), _fmt(m[SHUFFLE]), _fmt(m[SCRAMBLE]),
           _fmt(m[RANDOM]), _fmt(m[ORACLE]), _fmt(m[POP]), _fmt(H),
           (_fmt(oracle_ratio) if oracle_ratio != float("inf") else "inf"), oracle_fires,
           _fmt(d_cont), _fmt(beat_cont_target), beats_cont, _fmt(d_pop), _fmt(beat_pop_target), beats_pop,
           _fmt(d_rand), _fmt(hp_ceil_target), recovers_ceiling, shuffle_flat, scramble_controlled, sub_ceiling,
           _fmt(dose_lift), _fmt(dose_target), compute_matched,
           _fmt(_nm([ps.get("step_mismatch", float("nan")) for ps in per_seed])), broken, n_sigs, len(per_seed)))

    def _rnd(x, nd=6):
        return round(x, nd) if x == x else None

    gates = dict(
        verdict=verdict, ceil_metric=CEIL_METRIC,
        heldout_mrr={a: _rnd(m[a]) for a in ALL_ARMS},
        heldout_metric_spectrum={a: {mk: _rnd(spectrum[a][mk]) for mk in metric_keys} for a in ALL_ARMS},
        oracle_headroom=_rnd(H), oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio
                                              and oracle_ratio != float("inf")) else None),
        beat_continual=_rnd(d_cont), beat_pop=_rnd(d_pop), recover_over_random=_rnd(d_rand),
        shuffle_over_random=_rnd(d_shuf), scramble_over_random=_rnd(d_scr), dose_lift=_rnd(dose_lift),
        resolved_thresholds=dict(beat_cont=_rnd(beat_cont_target), beat_pop=_rnd(beat_pop_target),
                                 recover_ceiling=_rnd(hp_ceil_target), flat=_rnd(flat_target),
                                 dose=_rnd(dose_target), broken_margin=_rnd(broken_margin)),
        seed_votes=dict(beat_cont=votes_cont, beat_pop=votes_pop, need=need),
        n_query_scored=n_query, enough_heldout=enough_heldout, oracle_fires=oracle_fires,
        compute_matched=compute_matched, beats_cont=beats_cont, beats_pop=beats_pop,
        recovers_ceiling=recovers_ceiling, shuffle_flat=shuffle_flat, scramble_controlled=scramble_controlled,
        sub_ceiling=sub_ceiling, sig_dose=sig_dose, broken=broken, hard_pass=hard_pass, refute=refute, n_sigs=n_sigs,
        step_counts=dict(interleaved=int(_nm([ps.get("steps_interleaved", float("nan")) for ps in per_seed])),
                         continual=int(_nm([ps.get("steps_continual", float("nan")) for ps in per_seed]))),
        bands=dict(ORACLE_FIRE_RATIO=ORACLE_FIRE_RATIO, ORACLE_FIRE_ABS=ORACLE_FIRE_ABS, MIN_SIG_MRR=MIN_SIG_MRR,
                   HP_CEIL_FRAC=HP_CEIL_FRAC, BEAT_CONT_FRAC=BEAT_CONT_FRAC, BEAT_POP_FRAC=BEAT_POP_FRAC,
                   DOSE_FRAC=DOSE_FRAC, FLAT_FRAC=FLAT_FRAC, REFUTE_EPS=REFUTE_EPS, MIN_HELDOUT=MIN_HELDOUT),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism self-test on the planted hierarchical arena (exercises the REAL readout/eval substrate primitives).
# ---------------------------------------------------------------------------

def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        return _mechanism_selftest_body()
    finally:
        torch.set_num_threads(_prev)


def _mechanism_selftest_body():
    device = torch.device("cpu")
    cfg = dict(SELFTEST_CFG)
    exercised = set()
    pool = build_planted_transe_arena(cfg, 7)
    res = run_corpus(pool, cfg, device, 7, "PLANTED_TRANSE_HELDOUT_HEAD")
    exercised.update(["additive_direct_scores", "filtered_hits_from_scores", "pop_hits", "build_ids", "_to_int_edges"])

    out = dict(N=res.get("N"), n_heldout=res.get("n_heldout_entities"), n_support=res.get("n_support"),
               n_query=res.get("n_query_scored"), n_cold=res.get("n_cold"),
               steps_interleaved=res.get("steps_interleaved"), steps_continual=res.get("steps_continual"),
               step_mismatch=res.get("step_mismatch"), compute_matched=res.get("compute_matched"))
    if res.get("empty") or res.get("n_query_scored", 0) < ST_MIN_HO:
        out["fail"] = "planted arena produced too few held-out queries (%s)" % res.get("n_query_scored")
        return False, out

    ah = res["arm_hits"]
    m = {a: ah[a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS}
    inter = m[INTERLEAVED]; cont = m[CONTINUAL]; shuf = m[SHUFFLE]; scr = m[SCRAMBLE]
    rand = m[RANDOM]; orac = m[ORACLE]; pop = m[POP]
    d_cont = inter - cont; d_rand = inter - rand; d_scr = inter - scr; d_shuf = inter - shuf
    n_sigs = len(set(res["arm_sigs"].values()))

    oracle_recovers = bool(orac == orac and orac >= ST_ORACLE_MRR_MIN)
    oracle_ratio = _ratio(orac, rand)
    oracle_fires = bool((orac - rand) == (orac - rand) and (orac - rand) >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)
    inter_recovers = bool(inter == inter and inter >= ST_INTER_MRR_MIN)
    inter_beats_random = bool(d_rand == d_rand and d_rand >= ST_INTER_BEATS_RANDOM)
    inter_beats_cont = bool(d_cont == d_cont and d_cont >= ST_INTER_BEATS_CONT)
    d_pop = inter - pop
    inter_beats_pop = bool(d_pop == d_pop and d_pop >= ST_INTER_BEATS_POP)
    scramble_fails = bool(d_scr == d_scr and d_scr >= ST_SCRAMBLE_MARGIN)
    shuffle_fails = bool(d_shuf == d_shuf and d_shuf >= ST_SHUFFLE_MARGIN)
    baseline_in_band = bool(pop <= inter + 1e-9 and inter <= orac + 1e-6 and 0.0 <= rand <= 1.0)
    arms_differ = bool(n_sigs >= 5)
    compute_matched = bool(res.get("compute_matched"))
    # guard-vs-arena-floor: POP must be above the RANDOM/chance floor (head-holdout keeps frequency informative)
    pop_above_floor = bool(pop == pop and pop >= rand)

    # VACUOUS-SMOKE guard: the RANDOM null must NOT reach INTERLEAVED on the planted arena
    random_reached = bool(d_rand <= ST_INTER_BEATS_RANDOM)
    assert_discriminator_fires(random_reached, control_name=RANDOM,
                               headline_name="interleaved_beats_random_inductive_heldout", run_mode="self_test",
                               extra="RANDOM reached INTERLEAVED on the planted held-out-head arena -> arena not "
                                     "answerable / metric frozen / readout broken")

    vp_ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["additive_direct_scores", "filtered_hits_from_scores", "pop_hits",
                                        "build_ids", "_to_int_edges"],
         "exercised_entrypoints": sorted(exercised),
         "extra": "the inductive readout runs through the REAL additive_direct_scores + filtered_hits_from_scores + "
                  "pop_hits over build_ids/_to_int_edges int edges at self-test scale (the FULL loader "
                  "build_cskg_core_triples is exercised by the local MEMSMOKE gate before ship)"},
        {"kind": "substrate_signature", "callable_obj": additive_direct_scores, "callable_name": "additive_direct_scores",
         "kwargs": {}, "extra": "positional (X, D, hold_edges, device); portable, no version-specific kwargs"},
        {"kind": "metric_moves", "metric_name": "inductive_heldout_mrr",
         "values": [rand, cont, inter, orac],
         "extra": "MRR RANDOM=%.4f CONTINUAL=%.4f INTERLEAVED=%.4f ORACLE=%.4f: readout responds to the scaffold "
                  "schedule" % (rand, cont, inter, orac)},
        {"kind": "negative_control_margin", "control_scores": [shuf, scr, rand],
         "headline_threshold": inter, "higher_is_pass": True, "margin": ST_INTER_BEATS_RANDOM, "n_repeats_min": 2,
         "control_name": "SHUFFLE_SCRAMBLE_RANDOM_below_interleaved",
         "extra": "structure-destroyed SHUFFLE, relation-scrambled SCRAMBLE and random-init RANDOM must sit below "
                  "INTERLEAVED -> the relational structure the interleaved scaffold manufactures carries the signal"},
        {"kind": "guard_baseline_valid", "baseline_score": pop, "floor_score": rand,
         "guard_name": "INTERLEAVED_BEATS_POP", "baseline_name": "POP_RELFREQ", "floor_name": "RANDOM", "eps": 0.0,
         "extra": "head-holdout keeps the gold tail a SEEN, frequency-having entity so POP_RELFREQ is a FAIR bar "
                  "above the chance floor (not a structural zero); beats-POP is a real capability gate"},
    ], run_mode="self_test")

    out.update(
        heldout_mrr={a: round(m[a], 5) for a in ALL_ARMS},
        heldout_hits_at_10={a: round(ah[a].get(PRIMARY_METRIC, float("nan")), 5) for a in ALL_ARMS},
        dose_traj=res.get("dose_traj"), n_distinct_sigs=n_sigs,
        beat_continual=round(d_cont, 5), beat_random=round(d_rand, 5), scramble_margin=round(d_scr, 5),
        shuffle_margin=round(d_shuf, 5), oracle_margin=round(orac - rand, 5),
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        oracle_recovers=oracle_recovers, oracle_fires=oracle_fires, inter_recovers=inter_recovers,
        inter_beats_random=inter_beats_random, inter_beats_cont=inter_beats_cont, inter_beats_pop=inter_beats_pop,
        beat_pop=round(d_pop, 5), scramble_fails=scramble_fails,
        shuffle_fails=shuffle_fails, baseline_in_band=baseline_in_band, pop_above_floor=pop_above_floor,
        arms_differ=arms_differ, compute_matched=compute_matched, validity_preflight_ok=bool(vp_ok),
        support_deg_hist=res.get("support_deg_hist"),
        validity_preflight_declared=["real_code_path", "substrate_signature", "metric_moves",
                                     "negative_control_fails_with_margin", "guard_baseline_valid"])
    ok = bool(oracle_recovers and oracle_fires and inter_recovers and inter_beats_random and inter_beats_cont
              and inter_beats_pop and scramble_fails and shuffle_fails and baseline_in_band and pop_above_floor
              and arms_differ and compute_matched and vp_ok)
    if not ok:
        out["fail"] = ("selftest discriminator not clean: oracle_recovers=%s oracle_fires=%s inter_recovers=%s "
                       "inter_beats_random=%s inter_beats_cont=%s inter_beats_pop=%s scramble_fails=%s "
                       "shuffle_fails=%s baseline_in_band=%s pop_above_floor=%s arms_differ=%s compute_matched=%s "
                       "vp_ok=%s" % (oracle_recovers, oracle_fires, inter_recovers, inter_beats_random,
                                     inter_beats_cont, inter_beats_pop, scramble_fails, shuffle_fails,
                                     baseline_in_band, pop_above_floor, arms_differ, compute_matched, vp_ok))
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def _resolve_device(arg_device):
    env_queue = os.environ.get("HDLAB_QUEUE", "")
    env_dev = os.environ.get("HDLAB_DEVICE", "")
    if (arg_device == "cpu") or (env_dev == "cpu") or (env_queue == "remote_cpu_queue"):
        return torch.device("cpu")
    want_cuda = (arg_device in ("auto", "cuda")) or (env_dev == "cuda")
    return torch.device("cuda" if (want_cuda and torch.cuda.is_available()) else "cpu")


def core_main(run_mode, device):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "memsmoke": MEMSMOKE_CFG, "full": FULL_CFG}[run_mode])
    seeds = [7] if run_mode == "self_test" else list(cfg["seeds"])
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(), "unit": tag, "idx": i,
                                "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=%s cuda=%s run_mode=%s seeds=%s k=%s P_max=%s g_domains=%s"
         % (device, torch.cuda.is_available(), run_mode, seeds, cfg["k"], cfg["P_max"], cfg["g_domains"]))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s inter=%s cont=%s beat_cont=%s beat_rand=%s oracle_fires=%s compute_matched=%s vp_ok=%s"
         % (st_ok, st_res.get("heldout_mrr", {}).get(INTERLEAVED), st_res.get("heldout_mrr", {}).get(CONTINUAL),
            st_res.get("beat_continual"), st_res.get("beat_random"), st_res.get("oracle_fires"),
            st_res.get("compute_matched"), st_res.get("validity_preflight_ok")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED: %s" % st_res.get("fail", ""),
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS consol inductive-replay: INTERLEAVED anchor-compose beats CONTINUAL+RANDOM on "
                        "the planted held-out-head arena via REAL additive readout; SHUFFLE/SCRAMBLE controls below; "
                        "ORACLE fires; POP above floor; compute-matched; 5 validity-preflight checks declared",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    if not _ensure_cskg():
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode, verdict_msg="CSKG data absent and self-acquire failed",
            summary="cskg missing", elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    # Stream + build the reduced core ONCE (k-core is seed-independent at max_nodes=0); re-split per seed.
    _log("building CSKG reduced core (k_core=%d) ..." % cfg["k_core"])
    tr, va, te, prov = build_cskg_core_triples(cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], 7)
    pool = list(tr) + list(va) + list(te)
    _log("cskg core_nodes=%d core_edges=%d avgdeg=%.1f rels=%d pool=%d"
         % (prov["n_core_nodes"], prov["n_core_edges"], prov["core_avgdeg"], prov["n_rel_tokens"], len(pool)))

    per_seed, seed_failures = [], []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            res = run_corpus(pool, cfg, device, seed, "CSKG_CORE_HELDOUT_HEAD_INDUCTIVE")
            if res.get("empty") or res["n_query_scored"] < cfg.get("min_heldout", MIN_HELDOUT):
                raise RuntimeError("held-out query edges too few (%d < %d)"
                                   % (res.get("n_query_scored", 0), cfg.get("min_heldout", MIN_HELDOUT)))
            sigset = set(res["arm_sigs"].values())
            if len(sigset) < 5:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct sigs" % (seed, len(sigset)))
            res["cskg_provenance"] = prov
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            ah = res["arm_hits"]
            _log("seed=%d nq=%d n_sup=%d n_cold=%d steps[i=%d c=%d mism=%.4f] | MRR INTER=%s CONT=%s SHUF=%s SCR=%s "
                 "RAND=%s ORAC=%s POP=%s (%.1fs)"
                 % (seed, res["n_query_scored"], res["n_support"], res["n_cold"], res["steps_interleaved"],
                    res["steps_continual"], res["step_mismatch"], _fmt(ah[INTERLEAVED]["mrr"]),
                    _fmt(ah[CONTINUAL]["mrr"]), _fmt(ah[SHUFFLE]["mrr"]), _fmt(ah[SCRAMBLE]["mrr"]),
                    _fmt(ah[RANDOM]["mrr"]), _fmt(ah[ORACLE]["mrr"]), _fmt(ah[POP]["mrr"]), time.time() - ts))
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
