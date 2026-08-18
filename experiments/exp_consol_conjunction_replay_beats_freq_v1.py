"""CONSOLIDATION x CONJUNCTION (planted): does INTERLEAVED-replay manufacture codes that BEAT FREQUENCY on a
CONJUNCTION (XOR/parity) inference target -- the frequency-UNCAPPED regime where consolidation's payoff should
show -- where the prior single-relation cell (exp_consol_inductive_entity_replay_cskg_v1) only MATCHED frequency?

WHY (2x-drill on the consolidation negative): the consolidation envelope-push found interleaved-replay BEATS a
compute-matched task-blocked CONTINUAL scaffold but only MATCHES a fair FREQUENCY baseline on SINGLE-RELATION
inductive inference -- because a single-relation target is frequency-CAPPED (popularity/single-driver already
carries most of the answer, so replay's cleaner codes have no frequency-uncapped headroom to win). Hypothesis: a
CONJUNCTION target (XOR of >=2 latent constituents) is FRAGILE -- it needs ALL constituents simultaneously
decodable and is provably at CHANCE for any single-driver/frequency predictor. So replay's advantage, invisible on
the frequency-capped single-relation task, should become VISIBLE on the conjunction, where CONTINUAL's forgetting
(loses one constituent -> XOR collapses to chance) and FREQUENCY (chance by construction) both fail.

ARENA (planted, glass-box, NO LLM). A TransE-consistent latent arena drives BOTH the relational learning AND the
conjunction target from the SAME latent z, so the codes the schedule learns are exactly what the readout needs:
  - N entities have latent z[e] in R^k_lat; n_rel relations have translations w[r]; edge (h,r,t) connects h to the
    entity NEAREST z[h]+w[r] (deg edges per head). This gives rich CROSS-RELATION structure a scaffold can learn.
  - K_attr ORTHONORMAL planted directions u_i (QR of random); attribute a_i(e) = 1{ <z[e],u_i> > median_i } (a
    MEDIAN split -> each attribute is exactly balanced). TARGET y(e) = XOR/parity of the K_attr attributes.
    XOR is the canonical MINIMAL conjunction: each single attribute carries ZERO information about y (conditioning
    on one balanced bit leaves the parity of the rest balanced) -> FREQUENCY / single-driver are PROVABLY at chance.

MECHANISM UNDER TEST = the batch SCHEDULE producing the frozen scaffold (entity codes X, relation displacements D).
ALL scaffold arms fit the SAME additive/TransE model with the SAME CE self-adversarial loss and the SAME TOTAL
GRADIENT-STEP BUDGET; only HOW it is fit differs (copied verbatim from the proven single-relation cell so the
forgetting dynamics are the VET-confirmed ones):
  INTERLEAVED : i.i.d. minibatch replay over ALL train edges, P_max passes.                        THE MECHANISM.
  CONTINUAL   : task-blocked by RELATION-BUCKET, P_max passes PER block in order, NO replay. COMPUTE-MATCHED (each
                edge trained P_max times in BOTH arms). Shared entity/tail codes are contested across blocks ->
                sequential blocking forgets early-block relational structure -> degraded, information-LOST codes.
  SHUFFLE     : interleaved schedule on structure-DESTROYED train edges (tails randomized) -> codes carry no
                transferable z signal -> the conjunction stays at chance.                            MUST-FAIL.

READOUT (fixed, glass-box, IDENTICAL across every scaffold arm -- the ONLY thing that varies is CODE QUALITY):
INDUCTIVE anchor-compose gives every entity a code E[e] = mean over its support edges of (X[t] - D[r]) (TransE head
estimate; degree-invariant bundle; held-out entities have NO trained code and are reconstructed ONLY from their
OWN support edges to SEEN anchors). K_attr ridge probes are train-fit on SEEN entities' composed codes -> decode the
K_attr attributes of a held-out entity -> combined by the PUBLIC, FIXED parity rule (identical for every arm). The
conjunction being frequency-unsolvable is a property of the TARGET, independent of the readout.

ARMS (accuracy on held-out-entity conjunction inference, paired):
  INTERLEAVED / CONTINUAL / SHUFFLE : the three scaffold schedules (compose readout).
  RANDOM   : random-init codes + the same readout = the chance null.
  ORACLE   : transductive interleaved fit with held-out entities FOLDED IN (their codes LEARNED, decoded directly,
             no compose) = info-ceiling / arena-answerable positive control. If ORACLE does not fire, the arena is
             not answerable (gated INCONCLUSIVE, not a substrate negative).
  FREQ_NULL: max(POP majority-class, best-SINGLE-decoded-attribute -> y train-fit map) = the FAIR frequency /
             single-driver bar. PROVABLY at chance on XOR (the whole point / the load-bearing FAIRNESS check).
  POP      : majority class (base-rate) alone.
MUST-FAILS: SHUFFLE flat (structure destroyed) + ARBITRARY (regime: random y per entity -> even the INTERLEAVED
  codes cannot beat chance on a structureless target). FREQ-AT-CHANCE fairness gate: if FREQ_NULL solves the
  conjunction (> chance + tol) the arena is NOT a real conjunction -> ARENA_INVALID verdict (fix the arena).

PRE-REG BANDS (fixed BEFORE the run; see preregs/2026-07-15_consol_conjunction_replay_beats_freq_v1.md; chance =
MEASURED majority rate ~0.5; H = MEASURED oracle headroom = ORACLE_acc - RANDOM_acc):
  ORACLE-FIRES (arena answerable): ORACLE_acc >= chance + 0.12 AND (ORACLE_acc - RANDOM_acc) >= 0.08.
  FREQ-AT-CHANCE (fairness): FREQ_NULL_acc <= chance + 0.05  (else ARENA_INVALID_FREQ_SOLVES_CONJUNCTION).
  HARD_PASS : INTERLEAVED beats CONTINUAL by >= max(0.10*H, 0.03) AND beats FREQ_NULL by >= max(0.10*H, 0.03) AND
              recovers >= 0.30*H over RANDOM AND FREQ-at-chance AND ORACLE fires AND must-fails fire (SHUFFLE within
              0.25*H of RANDOM; ARBITRARY within chance+0.06) AND sub-ceiling (INTERLEAVED < ORACLE) AND not broken
              AND holds on a majority of seeds.
  REFUTE    : ORACLE fires AND FREQ-at-chance AND (INTERLEAVED - CONTINUAL <= 0.01 OR INTERLEAVED - FREQ_NULL <=
              0.01) -- replay does NOT beat compute-matched continual OR does NOT beat frequency EVEN on the
              frequency-uncapped conjunction. A deep, drill-worthy negative about consolidation's limits. Honest.
  MIDDLE    : ORACLE fires, FREQ-at-chance, beats both by > 0.01 but below the HARD_PASS margins (partial).
  INCONCLUSIVE: ORACLE does not fire / too few held-out / broken control. ARENA_INVALID: FREQ solves the conjunction.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): the arms produce >=5 distinct accuracy/decode signatures.
# - final_metrics_atomicity = tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: accuracy has a [chance,1] ceiling; FIX = ceiling-RELATIVE bands (fractions of the MEASURED
#   oracle headroom H). discriminator_reachability: bands scale to whatever H the FULL measures; ORACLE proves the
#   metric can move at scale.
# - baseline_in_band (META_RULE_AG): ORACLE must fire (>=chance+0.12); RANDOM/FREQ near chance; INTERLEAVED strictly
#   between (self-test asserts FREQ<=INTERLEAVED<=ORACLE and RANDOM near chance).
# - discriminator survives scale: self-test fires INTERLEAVED-beats-CONTINUAL + beats-FREQ + SHUFFLE-flat +
#   ARBITRARY-chance on the planted arena; analytical (B): a conjunction needs ALL constituents decodable, so a
#   forgotten (CONTINUAL) or destroyed (SHUFFLE) code that loses ONE constituent forces XOR to chance at ANY N; a
#   random-init code cannot decode any constituent -> the ordering persists at scale.
# - HARD_PASS strictly above floor: margins are FRACTIONS of H + an absolute MIN_SIG floor (not >=0).
# - HP_SCOPE: the beat gates apply to INTERLEAVED only. ORACLE=positive control (must fire); RANDOM/SHUFFLE/ARBITRARY
#   =must-not-clear-bar controls; CONTINUAL=the compute-matched head-to-head; FREQ_NULL/POP=the fair frequency bar.
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all arms + >=5 distinct sigs.
# - per-unit failure-class instrumentation (META_RULE_J; no bare except; per-seed failure_class recorded).
# - calibration_check = adaptive_with_discriminator_gate: all FRACs/eps pre-registered, NOT tuned on data; the beat
#   targets are FRACTIONS OF THE MEASURED oracle headroom H (computed in-run), not fixed thresholds.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the prereg.
# - real_code_path: self-test EXERCISES the REAL readout/fit substrate primitives (fit_schedule, build_anchor_head_
#   codes, ridge_fit/decode, conjunction_acc) via run_corpus on the planted arena.
# - substrate_signature binds fit_schedule against inspect.signature; base/portable positional args only.
# - guard_baseline_valid: the beats-FREQ guard is validated against FREQ being at the chance floor (a conjunction
#   keeps FREQ a structural-chance bar, so the beats-FREQ gate is a real capability gate not a degenerate one).
# - deterministic integer seeds only; no salted-hash / list(set()) seeding (PROT-023 static scan runs on ship).
# - progress_logging: line_buffered_stdout + per-seed/per-arm flush prints.

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

ANCHOR_NAME = "consol_conjunction_replay_v1"

# ---- Arm names ----
INTERLEAVED = "INTERLEAVED"   # mechanism: i.i.d. replay SGD scaffold
CONTINUAL = "CONTINUAL"       # compute-matched task-blocked scaffold (catastrophic-forgetting head-to-head)
SHUFFLE = "SHUFFLE"           # structure-destroyed-train scaffold (must stay flat)
RANDOM = "RANDOM"             # random-init scaffold + readout (chance null)
ORACLE = "ORACLE"             # transductive interleaved, held-out folded in (info-ceiling positive control)
FREQ = "FREQ_NULL"            # fair frequency / single-driver bar (chance on XOR)
POP = "POP"                   # majority-class base rate
SCAFFOLD_ARMS = [INTERLEAVED, CONTINUAL, SHUFFLE]
ALL_ARMS = [INTERLEAVED, CONTINUAL, SHUFFLE, RANDOM, ORACLE, FREQ, POP]

# ---- Pre-registered bands (HYPOTHESIZED; ceiling-relative -- resolved to absolute acc from MEASURED H) ----
ORACLE_FIRE_ABS = 0.12        # ORACLE_acc >= chance + this
ORACLE_FIRE_HEADROOM = 0.08   # AND ORACLE_acc - RANDOM_acc >= this
FREQ_CHANCE_TOL = 0.05        # FAIRNESS: FREQ_NULL_acc <= chance + this (else ARENA_INVALID)
MIN_SIG = 0.03                # absolute significance floor the beat margins must ALSO clear
HP_RECOVER_FRAC = 0.30        # HARD_PASS: (INTERLEAVED - RANDOM) >= 30% of H
BEAT_CONT_FRAC = 0.10         # HARD_PASS: (INTERLEAVED - CONTINUAL) >= max(10% of H, MIN_SIG)
BEAT_FREQ_FRAC = 0.10         # HARD_PASS: (INTERLEAVED - FREQ_NULL) >= max(10% of H, MIN_SIG)
FLAT_FRAC = 0.25              # must-fail: (SHUFFLE - RANDOM) <= 25% of H
ARB_FLAT_ABS = 0.06           # must-fail: ARBITRARY(interleaved) - chance <= this
REFUTE_EPS = 0.01             # <= this beat over CONTINUAL or FREQ (ORACLE firing + FREQ-at-chance) -> REFUTE
MIN_HELDOUT = 40              # min held-out entities for a valid discriminator (full)

# ---- self-test planted thresholds (calibrated on the planted arena, NOT data) ----
ST_ORACLE_MIN = 0.72          # planted: ORACLE (learned held-out codes) conjunction acc at least this
ST_INTER_MIN = 0.60           # planted: INTERLEAVED conjunction acc at least this
ST_INTER_BEATS_RANDOM = 0.07  # planted: (INTERLEAVED - RANDOM) >= this
ST_INTER_BEATS_CONT = 0.05    # planted: (INTERLEAVED - CONTINUAL) >= this (forgetting fires)
ST_INTER_BEATS_FREQ = 0.05    # planted: (INTERLEAVED - FREQ_NULL) >= this (conjunction beats frequency)
ST_SHUFFLE_FLAT = 0.05        # planted: (SHUFFLE - RANDOM) <= this (structure carries signal)
ST_ARB_FLAT = 0.07            # planted: ARBITRARY(interleaved) - chance <= this
ST_MIN_HO = 20                # planted: minimum held-out entities

GAMMA = 9.0
ADV_TEMP = 1.0
SCORE_CHUNK = 256
RIDGE_LAM = 1.0

# ---- Config profiles (all planted; glass-box CPU; smoke/full differ in seeds/size only) ----
SELFTEST_CFG = dict(n_ent=360, n_rel=8, k_lat=6, deg=6, K_attr=2, k=32, P_max=20, n_neg=16, batch=256, lr=0.05,
                    g_domains=4, heldout_entity_frac=0.25, min_heldout=ST_MIN_HO, step_match_tol=0.30, seeds=[7])
SMOKE_CFG = dict(n_ent=420, n_rel=8, k_lat=6, deg=6, K_attr=2, k=32, P_max=20, n_neg=16, batch=256, lr=0.05,
                 g_domains=4, heldout_entity_frac=0.22, min_heldout=30, step_match_tol=0.10, seeds=[7, 13])
FULL_CFG = dict(n_ent=600, n_rel=10, k_lat=8, deg=6, K_attr=2, k=48, P_max=20, n_neg=24, batch=256, lr=0.05,
                g_domains=5, heldout_entity_frac=0.20, min_heldout=MIN_HELDOUT, step_match_tol=0.05,
                seeds=[7, 13, 17, 23, 29])


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    try:
        return ("%.4f" % x) if (x == x) else "nan"
    except (TypeError, ValueError):
        return str(x)


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
# Planted TransE-consistent latent arena with orthonormal attribute directions + XOR/parity target.
# Deterministic (default_rng(seed) + order-preserving dedup). z drives BOTH the edges AND the conjunction target.
# ---------------------------------------------------------------------------

def build_planted_conjunction_arena(cfg, seed):
    n_ent, n_rel = int(cfg["n_ent"]), int(cfg["n_rel"])
    k_lat, deg, K_attr = int(cfg["k_lat"]), int(cfg["deg"]), int(cfg["K_attr"])
    rng = np.random.default_rng(seed * 100019 + 3)
    z = rng.standard_normal((n_ent, k_lat))
    w = rng.standard_normal((n_rel, k_lat))
    edges = []
    for h in range(n_ent):
        rels = rng.choice(n_rel, size=min(deg, n_rel), replace=False)
        for r in rels:
            target = z[h] + w[r]
            d = np.linalg.norm(z - target, axis=1)
            d[h] = np.inf
            t = int(np.argmin(d))
            edges.append((h, int(r), t))
    edges = list(dict.fromkeys(edges))                     # order-preserving dedup (NOT set(); determinism)
    edges_int = np.asarray(edges, dtype=np.int64)

    # ORTHONORMAL planted attribute directions (QR of a random matrix) -> attributes ~independent -> XOR balanced.
    G = rng.standard_normal((k_lat, K_attr))
    Q, _R = np.linalg.qr(G)                                # (k_lat, K_attr) orthonormal columns
    proj = z @ Q                                           # (n_ent, K_attr)
    med = np.median(proj, axis=0, keepdims=True)
    attrs = (proj > med).astype(np.int64)                  # median split -> each attribute exactly balanced
    y_clean = (attrs.sum(axis=1) % 2).astype(np.int64)     # XOR / parity = the conjunction target
    return dict(edges_int=edges_int, z=z, attrs=attrs, y_clean=y_clean, N=n_ent, n_rel=n_rel, K_attr=K_attr)


def build_heldout_entity_split(edges_int, N, frac, seed):
    """Hold out a fraction of HEAD-appearing entities. train = both-endpoints-seen edges. Each held-out entity keeps
    ALL its head edges to SEEN tails as SUPPORT (compose its code). Deterministic integer seeds only."""
    head_ids = sorted(set(int(h) for h in edges_int[:, 0].tolist()))
    rng = np.random.default_rng(seed * 100003 + 7)
    n_hold = max(1, int(frac * len(head_ids)))
    perm = rng.permutation(len(head_ids))
    hold_ids = set(int(head_ids[perm[i]]) for i in range(n_hold))

    train_rows, support_rows = [], []
    for i in range(edges_int.shape[0]):
        h = int(edges_int[i, 0]); t = int(edges_int[i, 2])
        h_hold = h in hold_ids; t_hold = t in hold_ids
        if not h_hold and not t_hold:
            train_rows.append(i)
        elif h_hold and not t_hold:
            support_rows.append(i)                          # held-out head -> seen tail = support (no leakage)
    train_int = edges_int[np.array(sorted(train_rows), dtype=np.int64)] if train_rows else np.zeros((0, 3), np.int64)
    support_int = (edges_int[np.array(sorted(support_rows), dtype=np.int64)]
                   if support_rows else np.zeros((0, 3), np.int64))
    heldout_ids = sorted(int(h) for h in hold_ids if int(h) in set(int(x) for x in support_int[:, 0].tolist())) \
        if support_int.shape[0] > 0 else []
    return train_int, support_int, hold_ids, heldout_ids


def assign_domains(train_int, n_rel, g_domains, seed):
    """Deterministic RELATION-bucket partition (relation-incremental continual): each relation -> one of g_domains
    buckets; edge domain = its relation's bucket. Shared entity/tail codes are contested across buckets, so
    sequential blocking forgets early-block relational structure. Returns per-train-edge domain (bucket) id."""
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
# Copied verbatim (behaviour-preserving) from the proven single-relation cell so forgetting dynamics are identical.
# ---------------------------------------------------------------------------

def _init_coords(N, n_rel, k, seed, device):
    g = torch.Generator(device="cpu").manual_seed(int(seed) * 7919 + 11)
    X = (torch.randn(N, k, generator=g, dtype=torch.float32) * 0.1).to(device).requires_grad_(True)
    D = (torch.randn(n_rel, k, generator=g, dtype=torch.float32) * 0.1).to(device).requires_grad_(True)
    return X, D


def _batch_loss(X, D, hb, rb, tb, N, n_neg, gneg, device):
    pred = X[hb] + D[rb]
    pos_score = GAMMA - torch.norm(pred - X[tb], dim=1)
    neg_t = torch.randint(0, N, (hb.shape[0], n_neg), generator=gneg).to(device)
    neg_score = GAMMA - torch.norm(pred.unsqueeze(1) - X[neg_t], dim=2)
    with torch.no_grad():
        wgt = torch.softmax(ADV_TEMP * neg_score, dim=1)
    pos_loss = -F.logsigmoid(pos_score)
    neg_loss = -(wgt * F.logsigmoid(-neg_score)).sum(dim=1)
    return (pos_loss + neg_loss).mean()


def fit_schedule(train_int, N, n_rel, cfg, schedule, seed, device, domain_of=None, extra_int=None):
    """Fit X,D under a batch SCHEDULE. Returns ((X_np, D_np), n_steps).
    INTERLEAVED / SHUFFLE / ORACLE : i.i.d. minibatch over all edges (ORACLE folds extra_int in), P_max passes.
    CONTINUAL : relation-bucket-blocked, P_max passes PER block in order (each edge trained P_max times)."""
    k, P_max, n_neg, batch = int(cfg["k"]), int(cfg["P_max"]), int(cfg["n_neg"]), int(cfg["batch"])
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

    total_steps = 0
    if schedule == CONTINUAL:
        assert domain_of is not None, "CONTINUAL requires domain_of"
        for d in range(int(cfg["g_domains"])):
            mask = np.where(domain_of == d)[0]
            if mask.shape[0] == 0:
                continue
            total_steps += run_block(torch.from_numpy(mask).long(), P_max)
        return snap(), total_steps

    all_rows = torch.arange(ed.shape[0], dtype=torch.long)
    total_steps += run_block(all_rows, P_max)
    return snap(), total_steps


def build_anchor_head_codes(X, D, support_int, device):
    """INDUCTIVE anchor-compose: E[h] = mean over support edges of (X[t] - D[r]). Fills held-out (and any supplied)
    head codes into a copy of X. Returns (Xp, support_deg)."""
    N, k = X.shape[0], X.shape[1]
    Xp = X.clone()
    support_deg = np.zeros(N, dtype=np.int64)
    if support_int.shape[0] == 0:
        return Xp, support_deg
    h = torch.from_numpy(support_int[:, 0]).long().to(device)
    r = torch.from_numpy(support_int[:, 1]).long().to(device)
    t = torch.from_numpy(support_int[:, 2]).long().to(device)
    est = X[t] - D[r]
    acc = torch.zeros(N, k, device=device, dtype=X.dtype)
    acc.index_add_(0, h, est)
    cnt = torch.zeros(N, device=device, dtype=X.dtype)
    cnt.index_add_(0, h, torch.ones(h.shape[0], device=device, dtype=X.dtype))
    mask = cnt > 0
    Xp[mask] = acc[mask] / cnt[mask].unsqueeze(1)
    support_deg = cnt.detach().to("cpu").numpy().astype(np.int64)
    return Xp, support_deg


# ---------------------------------------------------------------------------
# Glass-box decode-then-conjoin readout. Ridge probes decode each attribute; PUBLIC fixed parity rule combines.
# ---------------------------------------------------------------------------

def ridge_fit(Xn, y01, lam):
    n, k = Xn.shape
    Xa = np.concatenate([Xn, np.ones((n, 1), dtype=np.float64)], axis=1)
    A = Xa.T @ Xa + lam * np.eye(k + 1)
    return np.linalg.solve(A, Xa.T @ y01.astype(np.float64))


def ridge_pred_raw(Xn, w):
    Xa = np.concatenate([Xn, np.ones((Xn.shape[0], 1), dtype=np.float64)], axis=1)
    return Xa @ w


def decode_attrs(codes_np, probes):
    """codes_np: (n,k). probes: list of ridge weight vectors. Returns (n, K) in {0,1}."""
    cols = [(ridge_pred_raw(codes_np, w) > 0.5).astype(np.int64) for w in probes]
    return np.stack(cols, axis=1) if cols else np.zeros((codes_np.shape[0], 0), dtype=np.int64)


def conjoin(attrs_hat):
    return (attrs_hat.sum(axis=1) % 2).astype(np.int64)


def _acc(pred, gold):
    if len(pred) == 0:
        return float("nan")
    return float((np.asarray(pred) == np.asarray(gold)).mean())


def conjunction_acc_compose(codes_np, seen_ids, heldout_ids, attrs, y, K_attr, lam):
    """Train K ridge probes on SEEN composed codes; decode + parity on HELD-OUT composed codes. Returns (acc, sig)."""
    Xtr = codes_np[seen_ids]
    probes = [ridge_fit(Xtr, attrs[seen_ids, i], lam) for i in range(K_attr)]
    Xho = codes_np[heldout_ids]
    a_hat = decode_attrs(Xho, probes)
    y_hat = conjoin(a_hat)
    return _acc(y_hat, y[heldout_ids]), _sig(y_hat), a_hat, probes


def freq_single_driver_acc(codes_np, seen_ids, heldout_ids, attrs, y, K_attr, lam):
    """FAIR frequency / single-driver bar: max over (POP majority-class, best SINGLE decoded attribute -> y map).
    On XOR each single attribute carries ZERO info about y -> chance. Returns (freq_acc, pop_acc, best_single)."""
    ytr = y[seen_ids]
    pop_label = int(np.argmax(np.bincount(ytr, minlength=2)))
    pop_acc = _acc(np.full(len(heldout_ids), pop_label, dtype=np.int64), y[heldout_ids])
    # best single decoded attribute -> y (2-entry train-fit lookup), applied to held-out
    Xtr = codes_np[seen_ids]; Xho = codes_np[heldout_ids]
    best_single = pop_acc
    for i in range(K_attr):
        w = ridge_fit(Xtr, attrs[seen_ids, i], lam)
        a_tr = (ridge_pred_raw(Xtr, w) > 0.5).astype(np.int64)
        a_ho = (ridge_pred_raw(Xho, w) > 0.5).astype(np.int64)
        lut = {}
        for v in (0, 1):
            m = a_tr == v
            lut[v] = int(np.argmax(np.bincount(ytr[m], minlength=2))) if m.sum() > 0 else pop_label
        pred = np.array([lut[int(v)] for v in a_ho], dtype=np.int64)
        best_single = max(best_single, _acc(pred, y[heldout_ids]))
    return max(pop_acc, best_single), pop_acc, best_single


# ---------------------------------------------------------------------------
# One corpus run: split -> fit scaffolds -> compose codes -> decode-then-conjoin readout -> all arms PAIRED.
# ---------------------------------------------------------------------------

def run_corpus(arena, cfg, device, seed):
    edges_int = arena["edges_int"]; N = arena["N"]; n_rel = arena["n_rel"]; K_attr = arena["K_attr"]
    attrs = arena["attrs"]; y = arena["y_clean"]
    lam = float(cfg.get("ridge_lam", RIDGE_LAM))
    train_int, support_int, hold_ids, heldout_ids = build_heldout_entity_split(
        edges_int, N, cfg["heldout_entity_frac"], seed)
    seen_ids = sorted(set(int(h) for h in train_int[:, 0].tolist())
                      | set(int(t) for t in train_int[:, 2].tolist()))
    seen_ids = [e for e in seen_ids if e not in hold_ids]
    chance = float(max(np.bincount(y, minlength=2)) / max(1, len(y)))

    result = dict(seed=int(seed), N=int(N), n_rel=int(n_rel), K_attr=int(K_attr), n_train=int(train_int.shape[0]),
                  n_heldout=len(heldout_ids), n_seen=len(seen_ids), chance=round(chance, 5),
                  heldout_entity_frac=cfg["heldout_entity_frac"])
    if len(heldout_ids) < 1 or len(seen_ids) < 10 or train_int.shape[0] < 1:
        result["empty"] = True
        return result

    domain_of = assign_domains(train_int, n_rel, int(cfg["g_domains"]), seed)
    shuf_train = destroy_structure(train_int, N, seed)
    hold_support = support_int
    compose_support = np.concatenate([train_int, support_int], axis=0)   # seen heads + held-out heads

    # ---- fit the scaffolds (compute-matched INTERLEAVED vs CONTINUAL) ----
    (Xi, Di), steps_inter = fit_schedule(train_int, N, n_rel, cfg, INTERLEAVED, seed, device)
    (Xc, Dc), steps_cont = fit_schedule(train_int, N, n_rel, cfg, CONTINUAL, seed, device, domain_of=domain_of)
    (Xs, Ds), steps_shuf = fit_schedule(shuf_train, N, n_rel, cfg, SHUFFLE, seed, device)
    (Xo, Do), steps_orac = fit_schedule(train_int, N, n_rel, cfg, ORACLE, seed, device, extra_int=hold_support)
    step_mismatch = abs(steps_inter - steps_cont) / max(1, steps_inter)
    compute_matched = bool(step_mismatch <= float(cfg.get("step_match_tol", 0.05)))

    def _compose(Xnp, Dnp):
        Xt = torch.from_numpy(Xnp).to(device); Dt = torch.from_numpy(Dnp).to(device)
        Xp, _ = build_anchor_head_codes(Xt, Dt, compose_support, device)
        return Xp.detach().cpu().numpy().astype(np.float64)

    codes_inter = _compose(Xi, Di)
    codes_cont = _compose(Xc, Dc)
    codes_shuf = _compose(Xs, Ds)
    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)
    Xr = (torch.randn(N, cfg["k"], generator=gR) * 0.1).numpy().astype(np.float32)
    Dr = (torch.randn(n_rel, cfg["k"], generator=gR) * 0.1).numpy().astype(np.float32)
    codes_rand = _compose(Xr, Dr)
    # ORACLE: held-out entities folded into the interleaved fit -> LEARNED codes (no compose) = ceiling
    codes_oracle_learned = Xo.astype(np.float64)

    arm_acc, arm_sig, arm_ahat = {}, {}, {}
    for name, codes in [(INTERLEAVED, codes_inter), (CONTINUAL, codes_cont), (SHUFFLE, codes_shuf),
                        (RANDOM, codes_rand)]:
        a, sg, ahat, _p = conjunction_acc_compose(codes, seen_ids, heldout_ids, attrs, y, K_attr, lam)
        arm_acc[name] = a; arm_sig[name] = sg; arm_ahat[name] = ahat
    a_o, sg_o, ahat_o, _po = conjunction_acc_compose(codes_oracle_learned, seen_ids, heldout_ids, attrs, y, K_attr, lam)
    arm_acc[ORACLE] = a_o; arm_sig[ORACLE] = sg_o; arm_ahat[ORACLE] = ahat_o

    freq_acc, pop_acc, best_single = freq_single_driver_acc(codes_inter, seen_ids, heldout_ids, attrs, y, K_attr, lam)
    arm_acc[FREQ] = freq_acc; arm_acc[POP] = pop_acc
    arm_sig[FREQ] = _sig(np.array([freq_acc, best_single])); arm_sig[POP] = _sig(np.array([pop_acc]))

    # ---- ARBITRARY must-fail regime: random y per entity on the INTERLEAVED codes -> chance ----
    rng_arb = np.random.default_rng(seed * 100057 + 23)
    y_arb = rng_arb.integers(0, 2, size=N).astype(np.int64)
    attrs_arb = np.stack([rng_arb.integers(0, 2, size=N) for _ in range(K_attr)], axis=1).astype(np.int64)
    arb_acc, _sga, _aha, _pa = conjunction_acc_compose(codes_inter, seen_ids, heldout_ids, attrs_arb, y_arb,
                                                       K_attr, lam)

    # ---- per-attribute decode diagnostic (localization) on INTERLEAVED vs CONTINUAL ----
    def _decode_rates(codes):
        Xtr = codes[seen_ids]; Xho = codes[heldout_ids]
        rates = []
        for i in range(K_attr):
            w = ridge_fit(Xtr, attrs[seen_ids, i], lam)
            a_ho = (ridge_pred_raw(Xho, w) > 0.5).astype(np.int64)
            rates.append(round(_acc(a_ho, attrs[heldout_ids, i]), 5))
        return rates

    result.update(
        arm_acc={a: round(arm_acc[a], 6) for a in ALL_ARMS},
        arm_sigs=arm_sig, arbitrary_acc=round(arb_acc, 6), freq_pop=round(pop_acc, 6),
        freq_best_single=round(best_single, 6),
        decode_rates=dict(INTERLEAVED=_decode_rates(codes_inter), CONTINUAL=_decode_rates(codes_cont),
                          SHUFFLE=_decode_rates(codes_shuf), ORACLE=_decode_rates(codes_oracle_learned)),
        steps_interleaved=int(steps_inter), steps_continual=int(steps_cont), steps_shuffle=int(steps_shuf),
        steps_oracle=int(steps_orac), step_mismatch=round(step_mismatch, 5), compute_matched=compute_matched,
    )
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    return result


# ---------------------------------------------------------------------------
# Aggregate + verdict (ceiling-relative bands from MEASURED H).
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _sub(a, b):
    return (a - b) if (a == a and b == b) else float("nan")


def aggregate_and_verdict(per_seed):
    m = {a: _nm([ps["arm_acc"][a] for ps in per_seed]) for a in ALL_ARMS}
    chance = _nm([ps["chance"] for ps in per_seed])
    arb = _nm([ps["arbitrary_acc"] for ps in per_seed])
    n_heldout = int(_nm([ps["n_heldout"] for ps in per_seed]))

    H = _sub(m[ORACLE], m[RANDOM])
    d_cont = _sub(m[INTERLEAVED], m[CONTINUAL])
    d_freq = _sub(m[INTERLEAVED], m[FREQ])
    d_rand = _sub(m[INTERLEAVED], m[RANDOM])
    d_shuf = _sub(m[SHUFFLE], m[RANDOM])

    enough_heldout = bool(n_heldout >= MIN_HELDOUT)
    oracle_fires = bool(m[ORACLE] == m[ORACLE] and chance == chance and m[ORACLE] >= chance + ORACLE_FIRE_ABS
                        and H == H and H >= ORACLE_FIRE_HEADROOM)
    freq_at_chance = bool(m[FREQ] == m[FREQ] and chance == chance and m[FREQ] <= chance + FREQ_CHANCE_TOL)
    compute_matched = all(ps.get("compute_matched", False) for ps in per_seed)

    beat_cont_target = (max(BEAT_CONT_FRAC * H, MIN_SIG) if H == H else float("nan"))
    beat_freq_target = (max(BEAT_FREQ_FRAC * H, MIN_SIG) if H == H else float("nan"))
    recover_target = (HP_RECOVER_FRAC * H if H == H else float("nan"))
    flat_target = (FLAT_FRAC * H if H == H else float("nan"))

    need = (len(per_seed) // 2) + 1
    votes_cont = sum(1 for ps in per_seed if _sub(ps["arm_acc"][INTERLEAVED], ps["arm_acc"][CONTINUAL]) >= 0)
    votes_freq = sum(1 for ps in per_seed if _sub(ps["arm_acc"][INTERLEAVED], ps["arm_acc"][FREQ]) >= 0)

    beats_cont = bool(d_cont == d_cont and d_cont >= beat_cont_target and votes_cont >= need)
    beats_freq = bool(d_freq == d_freq and d_freq >= beat_freq_target and votes_freq >= need)
    recovers = bool(d_rand == d_rand and d_rand >= recover_target)
    shuffle_flat = bool(d_shuf == d_shuf and flat_target == flat_target and d_shuf <= flat_target)
    arb_flat = bool(arb == arb and chance == chance and (arb - chance) <= ARB_FLAT_ABS)
    sub_ceiling = bool(m[INTERLEAVED] == m[INTERLEAVED] and m[ORACLE] == m[ORACLE] and m[INTERLEAVED] < m[ORACLE])
    broken = bool(m[RANDOM] == m[RANDOM] and m[FREQ] == m[FREQ] and (m[RANDOM] - m[FREQ]) > max(MIN_SIG, flat_target))

    hard_pass = bool(beats_cont and beats_freq and recovers and oracle_fires and freq_at_chance and shuffle_flat
                     and arb_flat and sub_ceiling and compute_matched and not broken)
    refute = bool(oracle_fires and freq_at_chance
                  and ((d_cont == d_cont and d_cont <= REFUTE_EPS) or (d_freq == d_freq and d_freq <= REFUTE_EPS)))

    if not enough_heldout:
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT"
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_ORACLE_UNDERFIT"
    elif not freq_at_chance:
        verdict = "ARENA_INVALID_FREQ_SOLVES_CONJUNCTION"
    elif broken:
        verdict = "BROKEN_TEST_RANDOM_BEATS_FREQ"
    elif not compute_matched:
        verdict = "INCONCLUSIVE_COMPUTE_UNMATCHED"
    elif hard_pass:
        verdict = "HARD_PASS_REPLAY_BEATS_FREQ_AND_CONTINUAL_ON_CONJUNCTION"
    elif refute:
        verdict = "REFUTE_REPLAY_NO_CONJUNCTION_ADVANTAGE"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_CONJUNCTION_ADVANTAGE"

    verdict_msg = (
        "%s || CONJUNCTION(XOR) held-out acc [nho=%d chance=%s]: INTERLEAVED=%s CONTINUAL=%s SHUFFLE=%s | RANDOM=%s "
        "ORACLE=%s FREQ_NULL=%s POP=%s | ARBITRARY(inter)=%s || H(oracle-random)=%s | beat_cont=%s (>=%s=%s) "
        "beat_freq=%s (>=%s=%s) recover=%s (>=%s=%s) | shuffle_flat=%s arb_flat=%s sub_ceiling=%s freq_at_chance=%s "
        "oracle_fires=%s compute_matched=%s(mism=%s) broken=%s | seeds=%d votes(cont=%d freq=%d need=%d)"
        % (verdict, n_heldout, _fmt(chance), _fmt(m[INTERLEAVED]), _fmt(m[CONTINUAL]), _fmt(m[SHUFFLE]),
           _fmt(m[RANDOM]), _fmt(m[ORACLE]), _fmt(m[FREQ]), _fmt(m[POP]), _fmt(arb), _fmt(H),
           _fmt(d_cont), _fmt(beat_cont_target), beats_cont, _fmt(d_freq), _fmt(beat_freq_target), beats_freq,
           _fmt(d_rand), _fmt(recover_target), recovers, shuffle_flat, arb_flat, sub_ceiling, freq_at_chance,
           oracle_fires, compute_matched,
           _fmt(_nm([ps.get("step_mismatch", float("nan")) for ps in per_seed])), broken, len(per_seed),
           votes_cont, votes_freq, need))

    def _rnd(x, nd=6):
        return round(x, nd) if (isinstance(x, float) and x == x) else (x if x == x else None)

    gates = dict(
        verdict=verdict, chance=_rnd(chance),
        heldout_acc={a: _rnd(m[a]) for a in ALL_ARMS}, arbitrary_acc=_rnd(arb),
        oracle_headroom=_rnd(H), beat_continual=_rnd(d_cont), beat_freq=_rnd(d_freq), recover_over_random=_rnd(d_rand),
        shuffle_over_random=_rnd(d_shuf),
        resolved_thresholds=dict(beat_cont=_rnd(beat_cont_target), beat_freq=_rnd(beat_freq_target),
                                 recover=_rnd(recover_target), flat=_rnd(flat_target)),
        seed_votes=dict(beat_cont=votes_cont, beat_freq=votes_freq, need=need),
        n_heldout=n_heldout, enough_heldout=enough_heldout, oracle_fires=oracle_fires, freq_at_chance=freq_at_chance,
        compute_matched=compute_matched, beats_cont=beats_cont, beats_freq=beats_freq, recovers=recovers,
        shuffle_flat=shuffle_flat, arb_flat=arb_flat, sub_ceiling=sub_ceiling, broken=broken,
        hard_pass=hard_pass, refute=refute,
        decode_rates_mean=dict(
            INTERLEAVED=[round(v, 4) for v in np.mean([ps["decode_rates"]["INTERLEAVED"] for ps in per_seed],
                                                      axis=0).tolist()],
            CONTINUAL=[round(v, 4) for v in np.mean([ps["decode_rates"]["CONTINUAL"] for ps in per_seed],
                                                    axis=0).tolist()],
            ORACLE=[round(v, 4) for v in np.mean([ps["decode_rates"]["ORACLE"] for ps in per_seed], axis=0).tolist()]),
        step_counts=dict(interleaved=int(_nm([ps.get("steps_interleaved", float("nan")) for ps in per_seed])),
                         continual=int(_nm([ps.get("steps_continual", float("nan")) for ps in per_seed]))),
        bands=dict(ORACLE_FIRE_ABS=ORACLE_FIRE_ABS, ORACLE_FIRE_HEADROOM=ORACLE_FIRE_HEADROOM,
                   FREQ_CHANCE_TOL=FREQ_CHANCE_TOL, MIN_SIG=MIN_SIG, HP_RECOVER_FRAC=HP_RECOVER_FRAC,
                   BEAT_CONT_FRAC=BEAT_CONT_FRAC, BEAT_FREQ_FRAC=BEAT_FREQ_FRAC, FLAT_FRAC=FLAT_FRAC,
                   ARB_FLAT_ABS=ARB_FLAT_ABS, REFUTE_EPS=REFUTE_EPS, MIN_HELDOUT=MIN_HELDOUT),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism self-test on the planted arena (exercises the REAL fit + compose + decode-then-conjoin readout).
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
    arena = build_planted_conjunction_arena(cfg, 7)
    res = run_corpus(arena, cfg, device, 7)
    exercised.update(["fit_schedule", "build_anchor_head_codes", "ridge_fit", "decode_attrs",
                      "conjunction_acc_compose", "freq_single_driver_acc"])

    out = dict(N=res.get("N"), n_heldout=res.get("n_heldout"), n_seen=res.get("n_seen"), chance=res.get("chance"),
               steps_interleaved=res.get("steps_interleaved"), steps_continual=res.get("steps_continual"),
               step_mismatch=res.get("step_mismatch"), compute_matched=res.get("compute_matched"),
               decode_rates=res.get("decode_rates"))
    if res.get("empty") or res.get("n_heldout", 0) < ST_MIN_HO:
        out["fail"] = "planted arena produced too few held-out entities (%s)" % res.get("n_heldout")
        return False, out

    m = res["arm_acc"]
    inter = m[INTERLEAVED]; cont = m[CONTINUAL]; shuf = m[SHUFFLE]; rand = m[RANDOM]; orac = m[ORACLE]
    freq = m[FREQ]; pop = m[POP]; arb = res["arbitrary_acc"]; chance = res["chance"]
    d_cont = inter - cont; d_freq = inter - freq; d_rand = inter - rand; d_shuf = shuf - rand
    n_sigs = len(set(res["arm_sigs"].values()))

    oracle_recovers = bool(orac == orac and orac >= ST_ORACLE_MIN)
    oracle_fires = bool(orac >= chance + ORACLE_FIRE_ABS and (orac - rand) >= ORACLE_FIRE_HEADROOM)
    inter_recovers = bool(inter == inter and inter >= ST_INTER_MIN)
    inter_beats_random = bool(d_rand == d_rand and d_rand >= ST_INTER_BEATS_RANDOM)
    inter_beats_cont = bool(d_cont == d_cont and d_cont >= ST_INTER_BEATS_CONT)
    inter_beats_freq = bool(d_freq == d_freq and d_freq >= ST_INTER_BEATS_FREQ)
    shuffle_flat = bool(d_shuf == d_shuf and d_shuf <= ST_SHUFFLE_FLAT)
    arb_flat = bool(arb == arb and (arb - chance) <= ST_ARB_FLAT)
    freq_at_chance = bool(freq <= chance + FREQ_CHANCE_TOL)
    baseline_in_band = bool(freq <= inter + 1e-9 and inter <= orac + 1e-6 and abs(rand - chance) <= 0.10)
    arms_differ = bool(n_sigs >= 5)
    compute_matched = bool(res.get("compute_matched"))

    # VACUOUS-SMOKE guard: the RANDOM null must NOT reach INTERLEAVED on the planted arena
    random_reached = bool(d_rand <= ST_INTER_BEATS_RANDOM)
    assert_discriminator_fires(random_reached, control_name=RANDOM,
                               headline_name="interleaved_beats_random_conjunction_heldout", run_mode="self_test",
                               extra="RANDOM reached INTERLEAVED on the planted conjunction arena -> arena not "
                                     "answerable / metric frozen / readout broken")

    vp_ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["fit_schedule", "build_anchor_head_codes", "conjunction_acc_compose",
                                        "freq_single_driver_acc"],
         "exercised_entrypoints": sorted(exercised),
         "extra": "the decode-then-conjoin readout runs through the REAL fit_schedule + anchor-compose + ridge "
                  "decode + parity on the planted arena at self-test scale"},
        {"kind": "substrate_signature", "callable_obj": fit_schedule, "callable_name": "fit_schedule",
         "kwargs": {"train_int": None, "N": None, "n_rel": None, "cfg": None, "schedule": None, "seed": None,
                    "device": None},
         "extra": "positional/portable; copied-in fit, no version-specific kwargs"},
        {"kind": "metric_moves", "metric_name": "conjunction_heldout_acc",
         "values": [rand, cont, inter, orac],
         "extra": "acc RANDOM=%.4f CONTINUAL=%.4f INTERLEAVED=%.4f ORACLE=%.4f: the conjunction readout responds to "
                  "the scaffold schedule" % (rand, cont, inter, orac)},
        {"kind": "negative_control_margin", "control_scores": [shuf, rand, freq],
         "headline_threshold": inter, "higher_is_pass": True, "margin": ST_INTER_BEATS_FREQ, "n_repeats_min": 2,
         "control_name": "SHUFFLE_RANDOM_FREQ_below_interleaved",
         "extra": "structure-destroyed SHUFFLE, random-init RANDOM and the frequency bar FREQ_NULL must sit below "
                  "INTERLEAVED on the conjunction -> replay-manufactured code quality carries the signal"},
        {"kind": "guard_baseline_valid", "baseline_score": freq, "floor_score": rand,
         "guard_name": "INTERLEAVED_BEATS_FREQ", "baseline_name": "FREQ_NULL", "floor_name": "RANDOM", "eps": 0.06,
         "extra": "a conjunction keeps FREQ_NULL a STRUCTURAL-CHANCE bar (XOR single-driver is chance); beats-FREQ "
                  "is a real capability gate, and FREQ sits at the chance floor by construction (that is the point)"},
    ], run_mode="self_test")

    out.update(
        heldout_acc={a: round(m[a], 5) for a in ALL_ARMS}, arbitrary_acc=round(arb, 5),
        n_distinct_sigs=n_sigs, beat_continual=round(d_cont, 5), beat_freq=round(d_freq, 5),
        beat_random=round(d_rand, 5), shuffle_margin=round(d_shuf, 5), oracle_margin=round(orac - rand, 5),
        freq_best_single=res.get("freq_best_single"), freq_pop=res.get("freq_pop"),
        oracle_recovers=oracle_recovers, oracle_fires=oracle_fires, inter_recovers=inter_recovers,
        inter_beats_random=inter_beats_random, inter_beats_cont=inter_beats_cont, inter_beats_freq=inter_beats_freq,
        shuffle_flat=shuffle_flat, arb_flat=arb_flat, freq_at_chance=freq_at_chance, baseline_in_band=baseline_in_band,
        arms_differ=arms_differ, compute_matched=compute_matched, validity_preflight_ok=bool(vp_ok),
        validity_preflight_declared=["real_code_path", "substrate_signature", "metric_moves",
                                     "negative_control_fails_with_margin", "guard_baseline_valid"])
    ok = bool(oracle_recovers and oracle_fires and inter_recovers and inter_beats_random and inter_beats_cont
              and inter_beats_freq and shuffle_flat and arb_flat and freq_at_chance and baseline_in_band
              and arms_differ and compute_matched and vp_ok)
    if not ok:
        out["fail"] = ("selftest discriminator not clean: oracle_recovers=%s oracle_fires=%s inter_recovers=%s "
                       "inter_beats_random=%s inter_beats_cont=%s inter_beats_freq=%s shuffle_flat=%s arb_flat=%s "
                       "freq_at_chance=%s baseline_in_band=%s arms_differ=%s compute_matched=%s vp_ok=%s"
                       % (oracle_recovers, oracle_fires, inter_recovers, inter_beats_random, inter_beats_cont,
                          inter_beats_freq, shuffle_flat, arb_flat, freq_at_chance, baseline_in_band, arms_differ,
                          compute_matched, vp_ok))
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
    cfg = dict({"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode])
    seeds = [7] if run_mode == "self_test" else list(cfg["seeds"])
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(), "unit": tag, "idx": i,
                                "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=%s cuda=%s run_mode=%s seeds=%s k=%s P_max=%s g_domains=%s K_attr=%s"
         % (device, torch.cuda.is_available(), run_mode, seeds, cfg["k"], cfg["P_max"], cfg["g_domains"],
            cfg["K_attr"]))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s inter=%s cont=%s freq=%s beat_cont=%s beat_freq=%s oracle_fires=%s vp_ok=%s"
         % (st_ok, st_res.get("heldout_acc", {}).get(INTERLEAVED), st_res.get("heldout_acc", {}).get(CONTINUAL),
            st_res.get("heldout_acc", {}).get(FREQ), st_res.get("beat_continual"), st_res.get("beat_freq"),
            st_res.get("oracle_fires"), st_res.get("validity_preflight_ok")))
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
            verdict_msg="SELFTEST_PASS consol conjunction-replay: INTERLEAVED codes beat CONTINUAL+FREQ_NULL+RANDOM "
                        "on the planted XOR held-out arena via the fixed decode-then-conjoin readout; SHUFFLE flat; "
                        "ARBITRARY at chance; ORACLE fires; FREQ at chance; compute-matched; 5 validity checks",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    per_seed, seed_failures = [], []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            arena = build_planted_conjunction_arena(cfg, seed)
            res = run_corpus(arena, cfg, device, seed)
            if res.get("empty") or res["n_heldout"] < cfg.get("min_heldout", MIN_HELDOUT):
                raise RuntimeError("held-out entities too few (%d < %d)"
                                   % (res.get("n_heldout", 0), cfg.get("min_heldout", MIN_HELDOUT)))
            sigset = set(res["arm_sigs"].values())
            if len(sigset) < 5:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct sigs" % (seed, len(sigset)))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            m = res["arm_acc"]
            _log("seed=%d nho=%d n_seen=%d steps[i=%d c=%d mism=%.4f] | ACC INTER=%s CONT=%s SHUF=%s RAND=%s ORAC=%s "
                 "FREQ=%s POP=%s ARB=%s (%.1fs)"
                 % (seed, res["n_heldout"], res["n_seen"], res["steps_interleaved"], res["steps_continual"],
                    res["step_mismatch"], _fmt(m[INTERLEAVED]), _fmt(m[CONTINUAL]), _fmt(m[SHUFFLE]), _fmt(m[RANDOM]),
                    _fmt(m[ORACLE]), _fmt(m[FREQ]), _fmt(m[POP]), _fmt(res["arbitrary_acc"]), time.time() - ts))
            _hb("seed", si)
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
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
    if not args.self_test and not args.smoke and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "smoke", "full"):
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
