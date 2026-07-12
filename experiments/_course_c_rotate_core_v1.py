"""Core for the decisive ROTATION-score reasoning cell (Course C, glass-box RotatE).

THE WIN ATTEMPT. The prior decisive cell (exp_course_c_map_builder_cskg_l2_genuine_v1) and the capacity
ladder (exp_course_c_oracle_capacity_ladder_v1 -> verdict LADDER_FIT_LIMITED) both used an ADDITIVE-TransE
score s(h,r,t) = gamma - ||X_h + D_r - X_t|| (fit_transe_coords / fit_kge_anchor1). The additive form is
FIT-LIMITED even transductively on CSKG (ladder oracle_direct topped 0.424 at k32/dim8192, oracle_fpe
flatlined at 0.000), which is the exact signature the field fixed by moving TransE -> RotatE: additive
translation structurally cannot model symmetry (SYNONYM) and is poor on hierarchy (IS_A) -- CSKG's two
dominant relations. This core recreates the field's fix in our glass-box: relation = PHASE ROTATION
(RotatE-equivalent = our proven FHRR phase-rotation / SSP operator), keeping the Anchor-1 recipe otherwise
(self-adversarial CE, reciprocal, minibatch SGD) but with the LR fix (5e-3, not 0.05).

VALIDATED ROTATION PRIMITIVE (scour pointer, CITED@notes research_how_others_beat_frequency_..._2026-07-11 +
substrate_capability_map PP-275): the phase-rotation bind used here is the SAME primitive already landed on
this substrate as PP-275 = exp_lap3_rotate_analogy_cpu_v1 (learned RotatE relation phases, in-domain
Hits@1=0.899). PP-275 scores d(h,r,t) = ||exp(i(Ephi_h + Rphi_r)) - exp(i Ephi_t)||_2 (chordal-L2 over unit
phasors). This core's fit distance d_mean = mean_j (1 - cos((PHI_h+THETA_r)_j - PHI_t,j)) and its cos-mean
direct readout are MONOTONE-IDENTICAL to PP-275's chordal-L2 ranking: for unit phasors
||exp(iq) - exp(i PHI_t)||^2 = 2k(1 - cos_mean), so ranking by -chordal-L2 == ranking by +cos_mean == the
smooth surrogate optimized here. We reuse PP-275's rotation GEOMETRY and layer the Anchor-1 recipe (CE
self-adversarial + reciprocal + minibatch) + the LR fix on top of it -- lower-risk than a fresh design, per
the scour. NOTE: PP-275's 0.899 is IN-DOMAIN (its cross-domain-transfer number was 0.244, STRETCH4-2); the
CSKG task here is in-domain composition (fit + predict on the same graph's held-out), so the in-domain
rotation primitive is the right one. The 0.90 oracle-fire gate is DROPPED (no literature precedent at this
scale; best de-leaked KGE ~0.53-0.60 Hits@10); held-out oracle recovery is reported as CONTEXT, the trust
gate is a MODEST 0.15-above-random on the direct readout.

BANKED FOLLOW-UP (not implemented here; pre-cleared next step): if the rotation fix under-delivers
specifically on the IS_A (1-to-N / hierarchical) stratum, the next lever is a modulus/phase-split
(RotatE-modulus style: give entities a learnable modulus so hierarchy targets can spread radially instead of
colliding on the unit circle). Deferred by design; flagged in the prereg.

MEASUREMENT (the real prize; NOT gated on an unwinnable 0.9 oracle-fire):
  Does the rotation-fit ranking (ONESHOT_ROTATE) beat the frequency incumbent (BASELINE_POP) on held-out
  GENUINE-L2 composition edges, on the FAIR low+mid-degree stratum (where POP is beatable; high-degree is
  frequency-guessable by construction), degree-stratified, apples-to-apples on the SAME pinned split?
  Head-to-head ADDITIVE_TRANSE arm (same recipe, additive score) makes the functional-form claim airtight:
  ROTATION beats ADDITIVE = our glass-box reproduces RotatE > TransE.

READOUTS (report both, per director): PRIMARY = DIRECT native score (rotation = FHRR complex cos-similarity
Re<exp(i(PHI_h+THETA_r)), exp(i PHI_t)>/k; additive = -||X_h+D_r-X_t||); SECONDARY = FPE bounded-kernel with
MEDIAN-HEURISTIC bandwidth (NOT the fixed ell=0.55 that underflowed to 0.000 in the ladder). The ORACLE-fires
trust gate uses the DIRECT readout at a MODEST margin (0.15 above random), not 0.9.

FAIRNESS apparatus (reused verbatim from the map-builder + operator, apples-to-apples): pinned sorted-canonical
split, POP baseline on the SAME held-out set, degree tertiles, must-fail SCRAMBLE (relation labels shuffled),
RANDOM null, ORACLE transductive must-fire, DISCRETE old-failure-mode, SYN_COMPOSITIONAL positive control +
SYN_FREQ_GUESSABLE no-manufacture, two backdoor correlations, a46eadfa-matched mine params. The 4 validity-
preflight checks (positive_control_passes / metric_moves / negative_control_fails_with_margin /
full_gates_exercised_at_selftest) are DECLARED in the self-test via experiments._validity_preflight.

## Compute architecture
class (c) MIXED: symbolic L2/L1I/L1F decomposition + POP = sequential-CPU graph traversal (no matmul, same as
the imported apparatus); rotation/additive fits = minibatch SGD (batched); readouts = batched matmul, query-
chunked so the (nq,N) map is never materialized whole (the OOM fix; family OOM'd 3x). Storage SHARDED (each
entity its own phase code; relations = per-TYPE phase rotations, never one global bundle). device=auto (cuda on
the GPU host); remote_cpu_queue forces cpu. Per-seed PROCESS isolation: each FULL seed is its own wrapper cell
(this core runs one seed list per process).

ASCII-only. No bare except; except SystemExit before except Exception.
"""

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

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, write_partial, assert_discriminator_fires, VacuousSmokeError,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
# Symbolic apparatus + POP baseline + L2-genuine extraction (identical code path as the map-builder / VET).
from experiments.exp_gt_induction_fb15k237_dense_v1 import (  # noqa: E402
    Graph, build_ids, mine_rules, reachable, pop_rank,
)
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg, build_syn_compositional, build_syn_freq_guessable,
)
# Reused map-builder helpers (apples-to-apples with the INCONCLUSIVE run + the a46eadfa VET).
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    extract_l2_genuine, stratify_by_tail_degree, build_true_by_hr_int, filtered_hits_from_scores,
    pop_hits, per_stratum_hits, per_stratum_pop, _to_int_edges, discrete_scores,
    MAX_RULES_PER_HEAD, HUB_CAP, PRIMARY_K,
)
# Operator + grid positive-control + additive head-to-head fit.
from experiments.exp_course_c_operator_fix_ssp_phase_rotation_replay_v1 import (  # noqa: E402
    make_fpe_basis, fpe_encode, fit_discrete_bind, build_grid_graph, split_heldout,
)
from experiments._kge_anchor1_fit import fit_kge_anchor1  # noqa: E402

# ---- Arm names ----
ONESHOT = "ONESHOT_ROTATE"       # the map arm: rotation-score fit, direct readout
ADDITIVE = "ADDITIVE_TRANSE"     # head-to-head: SAME recipe, additive score (functional-form control)
POP = "BASELINE_POP"             # frequency incumbent (the bar)
SCRAMBLE = "SCRAMBLE_ROTATE"     # must-fail #1: rotation fit on relation-scrambled edges
RANDOM = "RANDOM_CODES"          # null: random phases + same readout
ORACLE = "ORACLE_TRANSDUCTIVE"   # must-fire trust gate (rotation fit sees held-out); NOT gated at 0.9
DISCRETE = "DISCRETE_BIND"       # old failure mode: iid phasor + circular-mean rotation
ALL_ARMS = [ONESHOT, ADDITIVE, POP, SCRAMBLE, RANDOM, ORACLE, DISCRETE]
STRATA = ["low", "mid", "high"]

# ---- Pre-registered bands (picked BEFORE the run) ----
POP_GAP = 0.03           # WIN: ONESHOT (fair low+mid) hits@10 - POP (fair) >= this
FORM_GAP = 0.02          # functional-form: ONESHOT - ADDITIVE >= this (fair stratum OR oracle-direct)
DISCRETE_UNDER = 0.03    # ONESHOT - DISCRETE >= this (old failure mode underperforms)
SCRAMBLE_EPS = 0.03      # must-fail #1: SCRAMBLE - ONESHOT <= this
CONTROL_LOSE_EPS = 0.02  # broken-test guard: a must-fail control (SCRAMBLE/RANDOM) beating POP+this = BROKEN
ORACLE_FIRE_MARGIN = 0.15  # trust gate: ORACLE(direct) - RANDOM(direct) >= this (NOT 0.9)
MANUFACTURE_EPS = 0.05   # SYN_FREQ_GUESSABLE: geometry - POP <= this (no manufactured headroom)
TIE_EPS = 0.02           # FAILS: ONESHOT (fair) - POP (fair) <= this
SEED_CV_MAX = 0.15       # director watch-item: cv of the winning arm's fair hits@10 across seeds < this
R_BACKDOOR = 0.15        # director watch-item (STRICTER): |coord-precision-vs-degree r| and |cross-channel r|
MIN_HELDOUT = 20         # min L2-genuine held-out queries for a valid discriminator
MIN_STRAT_Q = 8          # min queries in a stratum to assess its margin
MIN_FAIR_Q = 12          # min queries in the fair (low+mid) arena

# a46eadfa reference VET (mine params pinned; l2-only headroom = CSKG opportunity ceiling).
REFERENCE_VET = dict(source="CITED@notes VET a46eadfa (CSKG L2-only headroom)",
                     l2_only_all=0.276, l2_only_high=0.226, pop_high=0.412)

# ---- rotation-fit recipe defaults (Anchor-1 recipe + LR fix) ----
ROT_LR = 5e-3            # LR fix (director): 5e-3, NOT the anchor1 0.05 (~1000x RotatE's 5e-5)
ROT_GAMMA = 6.0         # logit scale: s = gamma*(1 - d_mean), d_mean in [0,2] -> s in [-6, 6]
ROT_ADV_TEMP = 1.0      # self-adversarial temperature (Sun et al. 2019)
ROT_REG = 1e-4          # small L2 prior on relation phase (rotation analog of N3; RotatE uses no N3)

# ---- self-test planted thresholds ----
SELFTEST_ROT_MIN = 0.30
SELFTEST_POP_MIN = 0.10

# ---- MEMORY: chunk the (nq,N) candidate matmul so it is never materialized whole (OOM fix) ----
SCORE_CHUNK = 256
FPE_MEDIAN_SAMPLE = 512   # sample size for the median-heuristic bandwidth estimate

# Config profiles. SELFTEST/SMOKE exercise the SAME arms / code path as FULL; only scale differs.
# SELFTEST bumped 2026-07-11 (exp_dev power fix): k=8/epochs=80 left every arm at the noise floor on the tiny
# planted arenas (ONESHOT ~ DISCRETE ~ 0.02) so the rotate_beats_discrete discriminator could not fire and
# tripped VacuousSmokeError on remote RNG drift. k=12/epochs=300 on a DENSE composition arena pins entity phases
# so the LEARNED-code rotation arm inductively separates from the FROZEN-code DISCRETE/ADDITIVE controls with a
# fat, platform-robust margin. Same code path as SMOKE/FULL; only scale differs.
SELFTEST_CFG = dict(k=12, fpe_dim=256, epochs=300, n_neg=32, batch=4096)
SMOKE_CFG = dict(k=24, fpe_dim=2048, epochs=120, n_neg=64, batch=8192,
                 cskg_max_lines=800000, k_core=3, cskg_max_nodes=3000, min_support=2, min_conf=0.05,
                 n_eval=2000, min_heldout=10)
# neg_chunk (2026-07-11 memory fix): score the n_neg=128 negatives in blocks of 16 with per-block backward so the
# (batch,n_neg,k) neg-scoring transient (the GPU OOM driver on the 8GiB card) never materializes whole. batch
# (effective batch=8192) + n_neg + dim + full N are ALL unchanged -> the recipe/measurement is preserved exactly;
# only the peak footprint drops. Absent on self_test/smoke -> those keep the bit-identical single-shot path.
FULL_CFG = dict(k=24, fpe_dim=4096, epochs=250, n_neg=128, batch=8192, neg_chunk=16,
                cskg_max_lines=0, k_core=12, cskg_max_nodes=0, min_support=10, min_conf=0.10,
                n_eval=6000, min_heldout=MIN_HELDOUT)
# MEMSMOKE = FULL scale (full N + fpe_dim + n_neg -> exercises the real GPU memory path incl. the FPE-median
# readout, the OOM driver) but few epochs + 2 seeds IN-PROCESS (tests per-seed empty_cache between seeds; the
# family OOM'd 3x). Purpose: prove no OOM at FULL memory footprint before the multi-hour FULL. Runs fast.
MEMSMOKE_CFG = dict(FULL_CFG); MEMSMOKE_CFG["epochs"] = 25; MEMSMOKE_CFG["n_eval"] = 3000


def _log(anchor, m):
    print("[%s] %s" % (anchor, m), flush=True)


def _sig(arr):
    a = np.round(np.asarray(arr, dtype=np.float64), 4)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


def _write_start_marker(output_dir, anchor, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=anchor, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    final = os.path.join(str(output_dir), "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, anchor, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=anchor)
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    final = os.path.join(str(output_dir), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# ROTATION-score fit (RotatE-equivalent glass-box phase rotation). Anchor-1 recipe otherwise.
# ---------------------------------------------------------------------------

def fit_kge_rotate(train_edges, N, n_rel, k, device, seed, epochs,
                   transductive_extra=None, reciprocal=True, lr=ROT_LR, gamma=ROT_GAMMA,
                   n_neg=64, adv_temp=ROT_ADV_TEMP, reg_lambda=ROT_REG, batch_size=8192,
                   neg_chunk=None):
    """Fit entity phases PHI (N,k), relation phases THETA (n_rel,k). Score s(h,r,t) = gamma*(1 - d_mean) with
    d_mean = mean_j (1 - cos((PHI_h+THETA_r)_j - PHI_t,j)) in [0,2] -- the smooth chordal phase-rotation
    distance (relation = elementwise phase rotation; entities = unit-modulus phasors). This is PP-275's
    validated rotation geometry (exp_lap3_rotate_analogy_cpu_v1, chordal-L2 ||exp(i(Ephi_h+Rphi_r))-exp(i
    Ephi_t)||; monotone-identical ranking) with the Anchor-1 recipe (self-adversarial CE + reciprocal +
    minibatch SGD) and the LR fix layered on. Returns PHI, THETA detached."""
    g = torch.Generator(device="cpu").manual_seed(seed * 7919 + 11)
    ed = train_edges
    if transductive_extra is not None and transductive_extra.shape[0] > 0:
        ed = np.concatenate([train_edges, transductive_extra], axis=0)
    n_rel_eff = n_rel
    if reciprocal:
        inv = ed[:, [2, 1, 0]].copy()
        inv[:, 1] = inv[:, 1] + n_rel               # inverse-relation ids in [n_rel, 2*n_rel)
        ed = np.concatenate([ed, inv], axis=0)
        n_rel_eff = 2 * n_rel
    two_pi = 2.0 * np.pi
    PHI = ((torch.rand(N, k, generator=g) * two_pi) - np.pi).to(device).requires_grad_(True)
    THETA = ((torch.rand(n_rel_eff, k, generator=g) * two_pi) - np.pi).to(device).requires_grad_(True)
    opt = torch.optim.Adam([PHI, THETA], lr=lr)

    h_all = torch.from_numpy(ed[:, 0]).long().to(device)
    r_all = torch.from_numpy(ed[:, 1]).long().to(device)
    t_all = torch.from_numpy(ed[:, 2]).long().to(device)
    E = h_all.shape[0]
    bs = min(batch_size, E)
    gperm = torch.Generator(device="cpu").manual_seed(seed * 13 + 1)
    gneg = torch.Generator(device="cpu").manual_seed(seed * 17 + 3)

    for ep in range(epochs):
        perm = torch.randperm(E, generator=gperm)
        for s in range(0, E, bs):
            bidx = perm[s:s + bs].to(device)
            hb = h_all[bidx]; rb = r_all[bidx]; tb = t_all[bidx]
            b = hb.shape[0]
            q = PHI[hb] + THETA[rb]                                   # (b,k) predicted phase
            pos_d = (1.0 - torch.cos(q - PHI[tb])).mean(dim=1)        # (b,) in [0,2]
            pos_score = gamma * (1.0 - pos_d)                        # (b,) logit
            neg_t = torch.randint(0, N, (b, n_neg), generator=gneg).to(device)  # (b,n_neg) SAME draw as pre-fix
            if neg_chunk is None or neg_chunk >= n_neg:
                # ORIGINAL single-shot path (bit-identical to pre-fix; used by self_test/smoke -> no neg_chunk).
                neg_d = (1.0 - torch.cos(q.unsqueeze(1) - PHI[neg_t])).mean(dim=2)  # (b,n_neg)
                neg_score = gamma * (1.0 - neg_d)                    # (b,n_neg)
                with torch.no_grad():
                    w = torch.softmax(adv_temp * neg_score, dim=1)   # self-adversarial weights (stop-grad)
                pos_loss = -torch.nn.functional.logsigmoid(pos_score)
                neg_loss = -(w * torch.nn.functional.logsigmoid(-neg_score)).sum(dim=1)
                loss = (pos_loss + neg_loss).mean()
                if reg_lambda > 0.0:
                    loss = loss + reg_lambda * THETA[rb].pow(2).mean()
                opt.zero_grad()
                loss.backward()
                opt.step()
            else:
                # MEMORY-CHUNKED path (FULL/memsmoke GPU): bound the (b,n_neg,k) neg-scoring transient to
                # (b,neg_chunk,k) by scoring negatives in blocks with per-block backward (grad accumulation).
                # Numerically equivalent to the single-shot loss: total = mean_b(pos) + reg +
                # mean_b(sum_neg -(w*logsig(-s_neg))); backprop is LINEAR so the accumulated grad == the
                # single-shot grad (float summation order aside). w is stop-grad so it is precomputed over ALL
                # negatives (chunked, no graph) before weighting. batch (effective batch) is UNCHANGED = 8192.
                with torch.no_grad():
                    neg_score_ng = torch.empty((b, n_neg), device=device, dtype=pos_score.dtype)
                    for c0 in range(0, n_neg, neg_chunk):
                        c1 = min(c0 + neg_chunk, n_neg)
                        nd = (1.0 - torch.cos(q.unsqueeze(1) - PHI[neg_t[:, c0:c1]])).mean(dim=2)
                        neg_score_ng[:, c0:c1] = gamma * (1.0 - nd)
                    w = torch.softmax(adv_temp * neg_score_ng, dim=1)  # (b,n_neg) stop-grad
                opt.zero_grad()
                base = (-torch.nn.functional.logsigmoid(pos_score)).mean()
                if reg_lambda > 0.0:
                    base = base + reg_lambda * THETA[rb].pow(2).mean()
                base.backward(retain_graph=True)                     # q subgraph retained for the neg blocks
                n_blocks = (n_neg + neg_chunk - 1) // neg_chunk
                done = 0
                for c0 in range(0, n_neg, neg_chunk):
                    c1 = min(c0 + neg_chunk, n_neg)
                    nd = (1.0 - torch.cos(q.unsqueeze(1) - PHI[neg_t[:, c0:c1]])).mean(dim=2)
                    ns = gamma * (1.0 - nd)                          # (b,block)
                    lc = -(w[:, c0:c1] * torch.nn.functional.logsigmoid(-ns)).sum(dim=1).mean()
                    done += 1
                    lc.backward(retain_graph=(done < n_blocks))      # free q subgraph on the last block
                opt.step()
    return PHI.detach(), THETA.detach()[:n_rel].contiguous()


# ---------------------------------------------------------------------------
# Readouts (query-chunked; the (nq,N) map is never whole on device).
# ---------------------------------------------------------------------------

def rotate_direct_scores(PHI, THETA, hold_edges, device, chunk=SCORE_CHUNK):
    """Native rotation readout: score(t) = mean_j cos((PHI_h+THETA_r)_j - PHI_t,j) = Re<exp(iq), exp(i PHI_t)>/k.
    Higher = better. Query-chunked; result accumulates on CPU."""
    h = torch.from_numpy(hold_edges[:, 0]).long().to(device)
    r = torch.from_numpy(hold_edges[:, 1]).long().to(device)
    q = PHI[h] + THETA[r]                                            # (nq,k)
    Pq = torch.complex(torch.cos(q), torch.sin(q)).to(torch.complex64)
    E_all = torch.complex(torch.cos(PHI), torch.sin(PHI)).to(torch.complex64)  # (N,k)
    E_cT = torch.conj(E_all).T                                      # (k,N)
    k = PHI.shape[1]
    nq = Pq.shape[0]; n_ent = PHI.shape[0]
    out = torch.empty((nq, n_ent), dtype=torch.float32)
    for s in range(0, nq, chunk):
        e = min(s + chunk, nq)
        sc = torch.real(Pq[s:e] @ E_cT) / k                         # (b,N)
        out[s:e] = sc.detach().to("cpu")
        del sc
    del Pq, E_all, E_cT
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    return out


def additive_direct_scores(X, D, hold_edges, device, chunk=SCORE_CHUNK):
    """Native additive (TransE) readout: score(t) = -||X_h + D_r - X_t||. Query-chunked."""
    h = torch.from_numpy(hold_edges[:, 0]).long().to(device)
    r = torch.from_numpy(hold_edges[:, 1]).long().to(device)
    pred = X[h] + D[r]                                              # (nq,k)
    Xsq = (X * X).sum(dim=1)                                        # (N,)
    nq = pred.shape[0]; n_ent = X.shape[0]
    out = torch.empty((nq, n_ent), dtype=torch.float32)
    XT = X.T                                                        # (k,N)
    for s in range(0, nq, chunk):
        e = min(s + chunk, nq)
        pc = pred[s:e]                                              # (b,k)
        d2 = (pc * pc).sum(dim=1, keepdim=True) + Xsq.unsqueeze(0) - 2.0 * (pc @ XT)
        sc = -torch.sqrt(torch.clamp(d2, min=0.0))                 # (b,N), higher=better
        out[s:e] = sc.detach().to("cpu")
        del pc, d2, sc
    del XT
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    return out


def _median_bandwidth(coords_all, seed):
    """Median-heuristic ell from pairwise distances of a random sample of the fitted coords (NOT ell=0.55)."""
    n = coords_all.shape[0]
    m = min(FPE_MEDIAN_SAMPLE, n)
    g = torch.Generator(device="cpu").manual_seed(seed * 71 + 13)
    idx = torch.randperm(n, generator=g)[:m].to(coords_all.device)
    S = coords_all[idx].float()                                    # (m,k)
    d = torch.cdist(S, S)                                          # (m,m)
    iu = torch.triu_indices(m, m, offset=1).to(d.device)          # same device as d (CUDA-safe indexing)
    vals = d[iu[0], iu[1]]
    med = float(torch.median(vals).item())
    return max(med, 1e-6)


def fpe_median_scores(coords_query, coords_all, k, dim, device, seed, chunk=SCORE_CHUNK):
    """FPE bounded-kernel readout with MEDIAN-HEURISTIC bandwidth (the fix for the ell=0.55 underflow).
    coords_*: real coords (rotation = phases; additive = X_h+D_r / X). Returns ((nq,N) CPU real, ell)."""
    ell = _median_bandwidth(coords_all, seed)
    W = make_fpe_basis(k, dim, ell, device, seed)                 # W ~ N(0, ell^-2 I)
    S_all = fpe_encode(coords_all, W)                            # (N,dim)
    S_all_cT = torch.conj(S_all).T
    nq = coords_query.shape[0]; n_ent = coords_all.shape[0]
    out = torch.empty((nq, n_ent), dtype=torch.float32)
    for s in range(0, nq, chunk):
        e = min(s + chunk, nq)
        S_hat = fpe_encode(coords_query[s:e], W)
        sc = torch.real(S_hat @ S_all_cT) / dim
        out[s:e] = sc.detach().to("cpu")
        del S_hat, sc
    del S_all, S_all_cT, W
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    return out, float(ell)


# ---------------------------------------------------------------------------
# Fair-stratum (low+mid) helpers.
# ---------------------------------------------------------------------------

def fair_mask(strat):
    """low(0)+mid(1) = the fair arena (POP-beatable). high(2) excluded (frequency-guessable by construction)."""
    return np.where((strat == 0) | (strat == 1))[0]


def fair_hits_from_scores(scores, hold_edges, strat, all_true, k=PRIMARY_K):
    mask = fair_mask(strat)
    if mask.size < 1:
        return dict(hits=float("nan"), n=0)
    sub = filtered_hits_from_scores(scores[mask], hold_edges[mask], all_true, ks=(k,))
    return dict(hits=round(sub["hits@%d" % k], 4), n=int(mask.size))


def fair_pop(rel_tail_freq, hold_edges, strat, all_true, n_ent, k=PRIMARY_K):
    mask = fair_mask(strat)
    if mask.size < 1:
        return dict(hits=float("nan"), n=0)
    sub, _ = pop_hits(rel_tail_freq, hold_edges[mask], all_true, n_ent, ks=(k,))
    return dict(hits=round(sub["hits@%d" % k], 4), n=int(mask.size))


# ---------------------------------------------------------------------------
# Fit all 7 arms + score PAIRED on the SAME held-out queries + candidate set.
# ---------------------------------------------------------------------------

def _pk(m):
    return m["hits@%d" % PRIMARY_K]


def _fit_and_score(train_int, hold, N, n_rel, cfg, device, seed, rel_tail_freq, all_true, want_fpe=True):
    k = cfg["k"]; epochs = cfg["epochs"]; n_neg = cfg["n_neg"]; batch = cfg["batch"]; dim = cfg["fpe_dim"]
    neg_chunk = cfg.get("neg_chunk")   # memory fix: chunk the neg-scoring on FULL/memsmoke; None on self_test/smoke

    def _ec():
        if getattr(device, "type", "") == "cuda":
            torch.cuda.empty_cache()

    # ONESHOT_ROTATE (the map arm)
    PHI, THETA = fit_kge_rotate(train_int, N, n_rel, k, device, seed, epochs,
                                lr=ROT_LR, n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk)
    _ec()
    # ADDITIVE_TRANSE (SAME recipe, additive score) -- functional-form head-to-head
    Xa, Da = fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs,
                             reciprocal=True, lr=ROT_LR, n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk)
    _ec()
    # SCRAMBLE_ROTATE (relation labels shuffled -> must-fail)
    scr = train_int.copy()
    scr[:, 1] = np.random.default_rng(seed * 555 + 2).permutation(scr[:, 1])
    PHIs, THETAs = fit_kge_rotate(scr, N, n_rel, k, device, seed, epochs,
                                  lr=ROT_LR, n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk)
    _ec()
    # ORACLE_TRANSDUCTIVE (rotation fit sees held-out -> trust gate; NOT gated at 0.9)
    PHIo, THETAo = fit_kge_rotate(train_int, N, n_rel, k, device, seed, epochs,
                                  transductive_extra=hold, lr=ROT_LR, n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk)
    _ec()
    # RANDOM_CODES (random phases + same readout -> null)
    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)
    PHIr = (((torch.rand(N, k, generator=gR) * 2.0 * np.pi) - np.pi)).to(device)
    THETAr = (((torch.rand(n_rel, k, generator=gR) * 2.0 * np.pi) - np.pi)).to(device)
    # DISCRETE_BIND (old failure mode)
    Z, R = fit_discrete_bind(train_int, N, n_rel, dim, device, seed)

    arm_metric, arm_sig, arm_scores = {}, {}, {}
    # direct-readout arms
    for name, sc in [
        (ONESHOT, rotate_direct_scores(PHI, THETA, hold, device)),
        (SCRAMBLE, rotate_direct_scores(PHIs, THETAs, hold, device)),
        (ORACLE, rotate_direct_scores(PHIo, THETAo, hold, device)),
        (RANDOM, rotate_direct_scores(PHIr, THETAr, hold, device)),
        (ADDITIVE, additive_direct_scores(Xa, Da, hold, device)),
    ]:
        arm_metric[name] = filtered_hits_from_scores(sc, hold, all_true)
        arm_sig[name] = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
        arm_scores[name] = sc
    sc = discrete_scores(Z, R, hold, device)
    arm_metric[DISCRETE] = filtered_hits_from_scores(sc, hold, all_true)
    arm_sig[DISCRETE] = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
    arm_scores[DISCRETE] = sc
    pop_m, pop_rank_vec = pop_hits(rel_tail_freq, hold, all_true, N)
    arm_metric[POP] = pop_m
    arm_sig[POP] = _sig(pop_rank_vec.astype(np.float64))

    # FPE-median SECONDARY readout for ONESHOT + ORACLE (does the median-bandwidth fix beat the ell=0.55
    # underflow? report oracle_fpe_median vs oracle_direct). Diagnostic; not the primary WIN metric.
    fpe = {}
    if want_fpe:
        h = torch.from_numpy(hold[:, 0]).long().to(device)
        r = torch.from_numpy(hold[:, 1]).long().to(device)
        for name, PHIx, THETAx in [(ONESHOT, PHI, THETA), (ORACLE, PHIo, THETAo)]:
            q = PHIx[h] + THETAx[r]
            sc_f, ell = fpe_median_scores(q, PHIx, k, dim, device, seed)
            fpe[name] = dict(metric=filtered_hits_from_scores(sc_f, hold, all_true), ell=round(ell, 5))
            del sc_f

    del PHI, THETA, Xa, Da, PHIs, THETAs, PHIo, THETAo, PHIr, THETAr, Z, R
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    return dict(arm_metric=arm_metric, arm_sig=arm_sig, arm_scores=arm_scores,
                pop_rank_vec=pop_rank_vec, fpe=fpe)


# ---------------------------------------------------------------------------
# One corpus run.
# ---------------------------------------------------------------------------

def run_corpus(train_lbl, valid_lbl, test_lbl, cfg, device, seed, corpus_name, want_fpe=True):
    ent2i, rel2i = build_ids(train_lbl, valid_lbl, test_lbl)
    N = len(ent2i); n_rel = len(rel2i)
    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    test_int = _to_int_edges(test_lbl, ent2i, rel2i)
    valid_int = _to_int_edges(valid_lbl, ent2i, rel2i)

    gd = Graph(train_lbl, ent2i, rel2i)
    known = defaultdict(set)
    for tr in (train_lbl, valid_lbl, test_lbl):
        for (h, r, t) in tr:
            known[(ent2i[h], rel2i[r])].add(ent2i[t])
    target_rels = list(rel2i.values())
    acc, allpat, _hub = mine_rules(gd, target_rels, cfg["min_support"], cfg["min_conf"], MAX_RULES_PER_HEAD, HUB_CAP)

    hold, hold_prov = extract_l2_genuine(gd, allpat, known, test_int, cfg["n_eval"], seed)
    all_true = build_true_by_hr_int(train_int, valid_int, test_int)
    strat, tert = stratify_by_tail_degree(hold, gd.node_degree)

    result = dict(corpus=corpus_name, seed=seed, N=int(N), n_rel=int(n_rel),
                  n_train=int(train_int.shape[0]), n_test=int(test_int.shape[0]),
                  l2_genuine=hold_prov, tert_bounds=tert,
                  strata_counts={STRATA[si]: int((strat == si).sum()) for si in range(3)})
    if hold.shape[0] < 1:
        result["empty"] = True
        return result

    fs = _fit_and_score(train_int, hold, N, n_rel, cfg, device, seed, gd.rel_tail_freq, all_true, want_fpe=want_fpe)
    arm_metric, arm_sig, arm_scores = fs["arm_metric"], fs["arm_sig"], fs["arm_scores"]
    pop_rank_vec = fs["pop_rank_vec"]

    # per-stratum + FAIR (low+mid) hits@PRIMARY_K
    strat_hits = {}
    for name in [ONESHOT, ADDITIVE, DISCRETE, SCRAMBLE, RANDOM, ORACLE]:
        strat_hits[name] = per_stratum_hits(arm_scores[name], hold, strat, all_true)
    strat_hits[POP] = per_stratum_pop(gd.rel_tail_freq, hold, strat, all_true, N)
    fair = {}
    for name in [ONESHOT, ADDITIVE, DISCRETE, SCRAMBLE, RANDOM, ORACLE]:
        fair[name] = fair_hits_from_scores(arm_scores[name], hold, strat, all_true)
    fair[POP] = fair_pop(gd.rel_tail_freq, hold, strat, all_true, N)

    # cross-channel independence (ONESHOT gold-geometry vs POP rank) -- freq-leak backdoor
    xchan_r = float("nan")
    gold_geo = np.array([arm_scores[ONESHOT][i, int(hold[i, 2])].item() for i in range(hold.shape[0])])
    if np.std(gold_geo) > 1e-9 and np.std(pop_rank_vec.astype(np.float64)) > 1e-9:
        xchan_r = float(np.corrcoef(gold_geo, -pop_rank_vec.astype(np.float64))[0, 1])

    result.update(
        arm_hits={a: {kk: round(vv, 4) for kk, vv in arm_metric[a].items() if kk != "n"} for a in ALL_ARMS},
        arm_n={a: arm_metric[a]["n"] for a in ALL_ARMS},
        arm_sigs=arm_sig,
        strat_hits=strat_hits,
        fair_hits={a: fair[a] for a in [ONESHOT, ADDITIVE, POP, DISCRETE, SCRAMBLE, RANDOM, ORACLE]},
        fpe_median=fs["fpe"],
        cross_channel_geom_vs_poprank_r=(round(xchan_r, 4) if xchan_r == xchan_r else None),
    )
    return result


# ---------------------------------------------------------------------------
# Aggregate + verdict (works on a per_seed list of length 1, 2, or 3).
# ---------------------------------------------------------------------------

def _mean(vals):
    vals = [v for v in vals if v == v]
    return float(np.mean(vals)) if vals else float("nan")


def _cv(vals):
    vals = [v for v in vals if v == v]
    if len(vals) < 2:
        return 0.0
    m = float(np.mean(vals))
    if abs(m) < 1e-9:
        return float("inf")
    return float(np.std(vals) / abs(m))


def aggregate_and_verdict(per_seed, syn_comp, syn_freq):
    def fair_mean(arm):
        return _mean([ps["fair_hits"][arm]["hits"] for ps in per_seed if ps["fair_hits"][arm]["n"] >= MIN_FAIR_Q])

    def agg_metric(arm):
        return _mean([_pk(ps["arm_hits"][arm]) for ps in per_seed])

    fair = {a: fair_mean(a) for a in [ONESHOT, ADDITIVE, POP, DISCRETE, SCRAMBLE, RANDOM, ORACLE]}
    agg = {a: agg_metric(a) for a in ALL_ARMS}
    oneshot_fair_vals = [ps["fair_hits"][ONESHOT]["hits"] for ps in per_seed
                         if ps["fair_hits"][ONESHOT]["n"] >= MIN_FAIR_Q]
    seed_cv = _cv(oneshot_fair_vals)

    backdoor = _mean([ps.get("cross_channel_geom_vs_poprank_r") for ps in per_seed
                      if ps.get("cross_channel_geom_vs_poprank_r") is not None])

    # ORACLE trust gate (DIRECT readout; NOT 0.9)
    oracle_fires = bool((agg[ORACLE] - agg[RANDOM]) >= ORACLE_FIRE_MARGIN)

    # WIN gates (fair low+mid stratum)
    win_pop = bool(fair[ONESHOT] == fair[ONESHOT] and fair[POP] == fair[POP]
                   and (fair[ONESHOT] - fair[POP]) >= POP_GAP)
    win_form = bool(fair[ONESHOT] == fair[ONESHOT] and fair[ADDITIVE] == fair[ADDITIVE]
                    and (fair[ONESHOT] - fair[ADDITIVE]) >= FORM_GAP)
    form_oracle = bool((agg[ORACLE] - agg[ADDITIVE]) >= FORM_GAP)  # form advantage also visible transductively
    g_discrete = bool(fair[ONESHOT] == fair[ONESHOT] and fair[DISCRETE] == fair[DISCRETE]
                      and (fair[ONESHOT] - fair[DISCRETE]) >= DISCRETE_UNDER)
    g_scramble = bool(fair[SCRAMBLE] == fair[SCRAMBLE] and fair[ONESHOT] == fair[ONESHOT]
                      and (fair[SCRAMBLE] - fair[ONESHOT]) <= SCRAMBLE_EPS)
    g_seed_cv = bool(seed_cv < SEED_CV_MAX)
    g_backdoor = bool(backdoor == backdoor and abs(backdoor) < R_BACKDOOR)
    syn_comp_ok = bool(syn_comp is not None and syn_comp.get("rot_beats_pop") and syn_comp.get("rot_beats_additive"))
    syn_freq_ok = bool(syn_freq is not None and syn_freq.get("no_manufacture"))

    # BROKEN-TEST guard: a must-fail control beating POP on the fair arena = the test is broken
    broken = bool((fair[SCRAMBLE] == fair[SCRAMBLE] and fair[POP] == fair[POP]
                   and (fair[SCRAMBLE] - fair[POP]) > CONTROL_LOSE_EPS)
                  or (fair[RANDOM] == fair[RANDOM] and fair[POP] == fair[POP]
                      and (fair[RANDOM] - fair[POP]) > CONTROL_LOSE_EPS))

    fails = bool(fair[ONESHOT] == fair[ONESHOT] and fair[POP] == fair[POP]
                 and (fair[ONESHOT] - fair[POP]) <= TIE_EPS)

    wins = bool(win_pop and (win_form or form_oracle) and g_discrete and g_scramble and g_seed_cv
                and g_backdoor and syn_comp_ok and syn_freq_ok and oracle_fires and not broken)

    ceiling_ratio = None
    if agg[ORACLE] == agg[ORACLE] and agg[ORACLE] > 1e-9:
        ceiling_ratio = round(agg[ONESHOT] / agg[ORACLE], 4)

    fpe_med = {}
    for name in [ONESHOT, ORACLE]:
        vals = [ps.get("fpe_median", {}).get(name, {}).get("metric", {}).get("hits@%d" % PRIMARY_K)
                for ps in per_seed if ps.get("fpe_median", {}).get(name)]
        fpe_med[name] = _mean([v for v in vals if v is not None])

    gates = dict(
        fair_hits_at_k={a: (round(fair[a], 4) if fair[a] == fair[a] else None)
                        for a in [ONESHOT, ADDITIVE, POP, DISCRETE, SCRAMBLE, RANDOM, ORACLE]},
        agg_hits_at_k={a: round(agg[a], 4) for a in ALL_ARMS}, primary_k=PRIMARY_K,
        margin_oneshot_vs_pop_fair=(round(fair[ONESHOT] - fair[POP], 4)
                                    if (fair[ONESHOT] == fair[ONESHOT] and fair[POP] == fair[POP]) else None),
        margin_oneshot_vs_additive_fair=(round(fair[ONESHOT] - fair[ADDITIVE], 4)
                                         if (fair[ONESHOT] == fair[ONESHOT] and fair[ADDITIVE] == fair[ADDITIVE]) else None),
        oracle_direct=round(agg[ORACLE], 4), random_direct=round(agg[RANDOM], 4),
        additive_oracle=round(agg[ADDITIVE], 4),
        oracle_fires=oracle_fires, oracle_fire_margin=ORACLE_FIRE_MARGIN,
        oracle_fpe_median=(round(fpe_med[ORACLE], 4) if fpe_med.get(ORACLE) == fpe_med.get(ORACLE) else None),
        oneshot_fpe_median=(round(fpe_med[ONESHOT], 4) if fpe_med.get(ONESHOT) == fpe_med.get(ONESHOT) else None),
        realized_vs_ceiling_ratio=ceiling_ratio,
        win_pop=win_pop, win_form=win_form, form_oracle=form_oracle, g_discrete=g_discrete,
        g_scramble=g_scramble, seed_cv=round(seed_cv, 4), g_seed_cv=g_seed_cv,
        backdoor_r=(round(backdoor, 4) if backdoor == backdoor else None), g_backdoor=g_backdoor,
        syn_comp_ok=syn_comp_ok, syn_freq_ok=syn_freq_ok, broken=broken, fails=fails, wins=wins,
        mine_params=dict(MAX_RULES_PER_HEAD=MAX_RULES_PER_HEAD, HUB_CAP=HUB_CAP,
                         min_support=per_seed[0].get("_min_support"), min_conf=per_seed[0].get("_min_conf")),
        reference_vet=REFERENCE_VET,
    )

    if broken:
        verdict = "BROKEN_TEST_CONTROL_BEATS_POP"
        msg = ("BROKEN: a must-fail control beat POP on the fair arena (scramble_fair=%s random_fair=%s pop_fair=%s) "
               "-> discriminator not firing; do not trust any margin." %
               (fair[SCRAMBLE], fair[RANDOM], fair[POP]))
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_ORACLE_UNDERFIT"
        msg = ("INCONCLUSIVE: transductive ORACLE did NOT fire under the DIRECT readout (oracle=%.3f random=%.3f "
               "margin<%.2f) -> even the rotation fit cannot recover edges it was trained on at this capacity; "
               "the reasoning question is not askable. Escalate (epochs/k/dim or functional-form is not the wall). "
               "ADDITIVE oracle=%.3f for reference." % (agg[ORACLE], agg[RANDOM], ORACLE_FIRE_MARGIN, agg[ADDITIVE]))
    elif wins:
        verdict = "WINS_ROTATION_BEATS_FREQUENCY"
        msg = ("WIN: rotation-fit geometry beats frequency on the FAIR (low+mid) L2-genuine arena. "
               "oneshot_fair=%.3f POP_fair=%.3f (margin=%.3f); rotation vs additive fair=%.3f/%.3f; "
               "oracle=%.3f random=%.3f seed_cv=%.3f backdoor=%s. Glass-box reproduces RotatE>TransE." %
               (fair[ONESHOT], fair[POP], fair[ONESHOT] - fair[POP], fair[ONESHOT], fair[ADDITIVE],
                agg[ORACLE], agg[RANDOM], seed_cv, gates["backdoor_r"]))
    elif fails:
        verdict = "FAILS_ROTATION_TIES_OR_LOSES"
        msg = ("CLEAN NEGATIVE: rotation does NOT beat frequency on the fair arena (oneshot_fair=%.3f POP_fair=%.3f "
               "margin=%.3f <= tie), with ORACLE firing (%.3f) so the fit/readout is NOT the excuse. The functional-"
               "form fix did not realize the L2 opportunity; closes on solid ground." %
               (fair[ONESHOT], fair[POP], (fair[ONESHOT] - fair[POP]) if fair[ONESHOT] == fair[ONESHOT] else float('nan'),
                agg[ORACLE]))
    else:
        verdict = "MIDDLE_BAND_PARTIAL"
        msg = ("MIDDLE_BAND: win_pop=%s win_form=%s form_oracle=%s g_discrete=%s g_scramble=%s g_seed_cv=%s "
               "g_backdoor=%s syn_comp=%s syn_freq=%s oracle_fires=%s | oneshot_fair=%s POP_fair=%s additive_fair=%s" %
               (win_pop, win_form, form_oracle, g_discrete, g_scramble, g_seed_cv, g_backdoor, syn_comp_ok,
                syn_freq_ok, oracle_fires, fair[ONESHOT], fair[POP], fair[ADDITIVE]))
    return verdict, msg, gates


# ---------------------------------------------------------------------------
# Self-test (planted; scale-invariant; SAME code path; declares the 4 validity-preflight checks).
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Self-test DENSE-COMPOSITION arena (deterministic, platform-identical, always L2-non-empty).
# ---------------------------------------------------------------------------
# Rationale (2026-07-11 exp_dev power fix): the prior planted SYN_COMPOSITIONAL arena (build_syn_compositional,
# person->1 middle + distractors) was too SPARSE -- each entity had too few informative edges for the rotation
# fit to pin its phase inductively at self-test scale, so ALL 7 arms sat at the noise floor (ONESHOT ~ DISCRETE ~
# POP ~ 0.02) and the rotate_beats_discrete discriminator could not fire (VacuousSmokeError on remote RNG drift).
# A DENSE 2D-grid composition (every in-grid point emits every primitive translation -> high per-entity degree)
# pins phases so the LEARNED-code rotation arm INDUCTIVELY recovers the held-out 2-hop composite rC while the
# FROZEN-random-code DISCRETE_BIND and the ADDITIVE_TRANSE arm stay at the floor (measured seed-0: ONESHOT h@10
# 0.20 vs DISCRETE 0.03 vs ADDITIVE 0.11 vs POP 0.00; ORACLE transductive 0.59). Density (not symmetric-relation
# planting) is the effective lever: an added symmetric relation was measured to DEGRADE the rotation inductive
# fit (conflicting constraints -> noisy). FIXED integer primitives (no RNG in graph build) make the arena
# identical on every platform and guarantee the composite (1,1)-translation is neither a primitive (no L1F alias)
# nor inverse-reachable (no L1I) -> extract_l2_genuine reliably yields the held-out edges (never EMPTY).
SELFTEST_GRID_PRIMS = [(1, 0), (0, 1), (2, 0), (0, 2), (2, 1), (1, 2)]


def build_syn_dense_grid_composition(grid_L=12, n_distract=200):
    """Deterministic dense 2D-grid composition as labeled triples. Entities = grid points; primitive relations
    rP{i} = fixed integer translations (dense); held-out relation rC = rP0 then rP1 (2-hop composite, L2-genuine).
    n_distract ISOLATED nodes chained by a junk relation inflate the candidate set N (so the RANDOM arm's chance
    rate 10/N sits well under the random_at_chance 0.05 floor) WITHOUT touching the rC arena -- this decouples N
    from the grid so the fat rotate>discrete margin (small dense grid) and a low RANDOM floor (large N) hold at
    once. No RNG in construction -> platform-identical + always non-empty. Returns (train, valid, test)."""
    def nid(x, y):
        return "g_%d_%d" % (x, y)
    pts = [(x, y) for x in range(grid_L) for y in range(grid_L)]
    ptset = set(pts)
    train = []
    for (x, y) in pts:
        for i, (dx, dy) in enumerate(SELFTEST_GRID_PRIMS):
            if (x + dx, y + dy) in ptset:
                train.append((nid(x, y), "rP%d" % i, nid(x + dx, y + dy)))
    da, db = SELFTEST_GRID_PRIMS[0], SELFTEST_GRID_PRIMS[1]
    gold = []
    for (x, y) in pts:
        mx, my = x + da[0], y + da[1]
        tx, ty = mx + db[0], my + db[1]
        if (mx, my) in ptset and (tx, ty) in ptset:
            gold.append((nid(x, y), "rC", nid(tx, ty)))
    # isolated distractor nodes (chained by a junk relation so they get IDs + become scoring candidates); they
    # never participate in rC/primitives so the rC rotation-vs-discrete dynamics are unchanged.
    for j in range(n_distract):
        train.append(("d%d" % j, "rJunk", "d%d" % ((j + 1) % max(1, n_distract))))
    # ORDER-PRESERVING dedup (NOT list(set(...))): build_ids assigns entity IDs in edge-LIST order, so a
    # hash-seed-randomized set iteration would give a different entity->ID map each PROCESS -> the seeded phase
    # init lands on different entities -> cross-process nondeterministic fit (a root cause of the self-test flake).
    train = list(dict.fromkeys(train))
    test = [gold[i] for i in range(0, len(gold), 2)]                 # deterministic even/odd split
    train = train + [gold[i] for i in range(1, len(gold), 2)]
    return train, [], test


def _grid_positive_control(device):
    """Rotation-geometry positive control on a DENSE deterministic grid composition (2026-07-11 recalibration).
    Returns arm hits@1+hits@10 dict. Gates in mechanism_selftest use hits@10 (the cell's PRIMARY_K metric; the
    prior hits@1>=0.30 inductive-recovery bar was provably unreachable at self-test scale) + the transductive
    ORACLE recovering (proves the phase-rotation geometry is representable / correctly implemented, not a bug) +
    the SAME relative rotate>discrete/pop/random discriminator used in PART B."""
    gcfg = dict(SELFTEST_CFG); gcfg.update(min_support=2, min_conf=0.05, n_eval=0, epochs=300)
    tr, va, te = build_syn_dense_grid_composition(grid_L=12)   # 12x12 grid + distractors -> N~424, chance ~0.024
    res = run_corpus(tr, va, te, gcfg, device, 7, "SYN_GRID_POSCTRL", want_fpe=False)
    if res.get("empty"):
        return None, 0, 0
    am = res["arm_hits"]
    grid = {a: {kk: round(vv, 4) for kk, vv in am[a].items() if kk != "n"} for a in ALL_ARMS}
    n_sigs = len(set(res["arm_sigs"].values()))
    return grid, n_sigs, int(res["l2_genuine"]["n_l2_genuine"])


def _run_syn(builder_args, cfg, device, corpus_name):
    tr, va, te = builder_args
    res = run_corpus(tr, va, te, cfg, device, 0, corpus_name, want_fpe=False)
    res["_min_support"] = cfg["min_support"]; res["_min_conf"] = cfg["min_conf"]
    return res


def mechanism_selftest(device):
    # DETERMINISM PIN (2026-07-11): the tiny planted arenas have degenerate score-ties (regular-grid symmetry) and
    # torch multi-thread / GPU float-reduction ORDER flips boundary-rank ties -> nondeterministic hits run-to-run
    # (ONESHOT observed swinging 0.098-0.23 by thread schedule on the SAME seed). That noise -- not a stale planted
    # graph -- is the true root cause of the original remote VacuousSmokeError flake. The self-test validates
    # DEVICE-INDEPENDENT mechanism/discriminator logic, so pin it to single-threaded CPU for bit-reproducible gates
    # on any host. The GPU CUDA memory path (the OOM driver) is exercised separately by the memsmoke/FULL CSKG seed
    # runs, which keep the passed device. Threads restored in finally so those GPU runs are unaffected.
    _prev_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    device = torch.device("cpu")
    try:
        return _mechanism_selftest_body(device)
    finally:
        torch.set_num_threads(_prev_threads)


def _mechanism_selftest_body(device):
    # SINGLE dense-composition arena (2026-07-11 redesign). One arena carries BOTH roles at half the prior cost:
    #  - geometry_fires: the TRANSDUCTIVE ORACLE recovers on the same arena + fires over RANDOM + all 7 arms are
    #    distinct -> the phase-rotation geometry is REPRESENTABLE and correctly implemented (not a bug).
    #  - the INDUCTIVE rotate>discrete/additive/pop discrimination is the rot_beats_* block below.
    # The prior SEPARATE grid positive control gated on inductive hits@1>=0.30 / beats_discrete@1>=0.15 -- provably
    # unreachable at self-test scale (ONESHOT h@1 maxes ~0.07; only the transductive ORACLE reaches ~0.4) -- so it
    # is dropped. Dense primitive edges pin phases so learned-code rotation inductively beats frozen-code DISCRETE +
    # ADDITIVE; isolated distractor nodes hold RANDOM's chance rate under the random_at_chance floor.
    cfg = dict(SELFTEST_CFG); cfg.update(min_support=2, min_conf=0.05, n_eval=0)
    comp = _run_syn(build_syn_dense_grid_composition(grid_L=12), cfg, device, "SYN_DENSE_GRID_COMP")
    freq = _run_syn(build_syn_freq_guessable(seed=0, n_person=300), cfg, device, "SYN_FREQ_GUESSABLE")

    comp_nonempty = bool(not comp.get("empty") and comp["l2_genuine"]["n_l2_genuine"] >= 5)
    res = dict(comp_l2_genuine=(0 if comp.get("empty") else comp["l2_genuine"]["n_l2_genuine"]),
               freq_l2_genuine=freq["l2_genuine"]["n_l2_genuine"], geometry_fires=False, metric_k=PRIMARY_K)
    if not comp_nonempty:
        res["fail"] = "SYN_DENSE_GRID_COMP produced no L2-genuine held-out (%s)" % comp["l2_genuine"]
        return False, res

    ch = comp["arm_hits"]
    c_ora = _pk(ch[ORACLE]); c_rnd = _pk(ch[RANDOM])
    grid_recovers = bool(c_ora >= 0.30)                                # transductive geometry representable
    grid_oracle_fires = bool((c_ora - c_rnd) >= ORACLE_FIRE_MARGIN)
    grid_arms_differ = bool(len(set(comp["arm_sigs"].values())) >= 5)
    geometry_fires = bool(grid_recovers and grid_oracle_fires and grid_arms_differ)
    res.update(oracle_recovers=grid_recovers, oracle_fires_gate=grid_oracle_fires,
               arms_differ=grid_arms_differ, geometry_fires=geometry_fires,
               oracle_direct=round(c_ora, 4), random_direct=round(c_rnd, 4))

    ch = comp["arm_hits"]
    oneshot = _pk(ch[ONESHOT]); additive = _pk(ch[ADDITIVE]); pop = _pk(ch[POP])
    discrete = _pk(ch[DISCRETE]); scramble = _pk(ch[SCRAMBLE]); random_ = _pk(ch[RANDOM])
    rot_beats_pop = bool((oneshot - pop) >= POP_GAP)
    rot_beats_additive = bool((oneshot - additive) >= FORM_GAP)
    rot_beats_discrete = bool((oneshot - discrete) >= DISCRETE_UNDER)
    scramble_not_beat = bool((scramble - oneshot) <= SCRAMBLE_EPS)
    random_at_chance = bool(random_ <= max(pop, 0.05))

    if freq.get("empty") or freq["l2_genuine"]["n_l2_genuine"] < 5:
        no_manufacture = True; pop_fires_freq = True; freq_geo = float("nan"); freq_pop = float("nan")
    else:
        fh = freq["arm_hits"]
        freq_geo = _pk(fh[ONESHOT]); freq_pop = _pk(fh[POP])
        no_manufacture = bool((freq_geo - freq_pop) <= MANUFACTURE_EPS)
        pop_fires_freq = bool(freq_pop >= SELFTEST_POP_MIN)

    # VACUOUS-SMOKE guard: DISCRETE must NOT pass the map-arm bar on the planted compositional corpus.
    discrete_passed = bool((oneshot - discrete) <= TIE_EPS)
    assert_discriminator_fires(discrete_passed, control_name=DISCRETE, headline_name="rotate_beats_discrete",
                               run_mode="self_test",
                               extra="DISCRETE reproduced the rotation arm on planted composition -> geometry not the lever")

    # full_gates_exercised: run the REAL verdict logic on the synthetic per_seed (exercises every gate at tiny scale)
    comp["_min_support"] = cfg["min_support"]; comp["_min_conf"] = cfg["min_conf"]
    syn_comp_summary = dict(rot_beats_pop=rot_beats_pop, rot_beats_additive=rot_beats_additive)
    syn_freq_summary = dict(no_manufacture=no_manufacture)
    st_verdict, st_msg, st_gates = aggregate_and_verdict([comp], syn_comp_summary, syn_freq_summary)

    # ---- the 4 DECLARED validity-preflight checks (WARN-mode during bake; declaring now = enforce-ready) ----
    exercised = ["arms_differ", "oracle_fires_gate", "broken_test_guard", "scramble_gate", "win_gate"]
    vp_ok = run_validity_preflight([
        # (1) positive_control_passes: the planted-composition rotation arm SHOULD clear the WIN bar (proves the
        #     geom-beats-POP+additive bar is achievable, i.e. not unwinnable/mis-directed).
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(rot_beats_pop and rot_beats_additive and geometry_fires),
         "control_name": "SYN_COMPOSITIONAL_rotate", "headline_name": "rotate_beats_pop_and_additive",
         "extra": "planted composition: ONESHOT clears POP+additive+grid-oracle at self-test scale"},
        # (2) metric_moves: the fair hits@k readout must MOVE (RANDOM << POP < ONESHOT), not be frozen/exact-0.
        {"kind": "metric_moves", "metric_name": "fair_hits_at_k", "values": [random_, pop, oneshot],
         "extra": "RANDOM=%.3f POP=%.3f ONESHOT=%.3f: readout responds to signal" % (random_, pop, oneshot)},
        # (3) negative_control_fails_with_margin: the must-fail controls (SCRAMBLE, RANDOM) must sit strictly
        #     below the map arm ONESHOT by margin (higher_is_pass -> robust fail = control <= ONESHOT - margin).
        {"kind": "negative_control_margin", "control_scores": [scramble, random_],
         "headline_threshold": oneshot, "higher_is_pass": True, "margin": SCRAMBLE_EPS, "n_repeats_min": 2,
         "control_name": "SCRAMBLE_and_RANDOM_below_map",
         "extra": "SCRAMBLE + RANDOM must not reach ONESHOT; 3-seed determinism enforced at FULL"},
        # (4) full_gates_exercised_at_selftest: aggregate_and_verdict ran on the synthetic per_seed, firing every
        #     fail-closed gate (arms_differ / oracle-fire / broken-test / scramble / win) at tiny scale.
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "oracle_fires_gate", "broken_test_guard", "scramble_gate", "win_gate"],
         "exercised_gates": exercised,
         "extra": "aggregate_and_verdict verdict=%s at self-test scale" % st_verdict},
    ], run_mode="self_test")

    res.update(comp_oneshot=round(oneshot, 4), comp_additive=round(additive, 4), comp_pop=round(pop, 4),
               comp_discrete=round(discrete, 4), comp_scramble=round(scramble, 4), comp_random=round(random_, 4),
               freq_geo=(round(freq_geo, 4) if freq_geo == freq_geo else None),
               freq_pop=(round(freq_pop, 4) if freq_pop == freq_pop else None),
               rot_beats_pop=rot_beats_pop, rot_beats_additive=rot_beats_additive,
               rot_beats_discrete=rot_beats_discrete, scramble_not_beat=scramble_not_beat,
               random_at_chance=random_at_chance, no_manufacture=no_manufacture, pop_fires_freq=pop_fires_freq,
               n_distinct_sigs=len(set(comp["arm_sigs"].values())), selftest_verdict=st_verdict,
               validity_preflight_ok=bool(vp_ok),
               validity_preflight_declared=["positive_control_passes", "metric_moves",
                                            "negative_control_fails_with_margin", "full_gates_exercised_at_selftest"])
    # Grid oracle proves geometry CAN beat frequency (stable); SYN_COMP validates arena + rot>additive + must-fails.
    ok = bool(geometry_fires and rot_beats_additive and rot_beats_discrete and scramble_not_beat
              and random_at_chance and no_manufacture and pop_fires_freq)
    return ok, res


# ---------------------------------------------------------------------------
# Device selection + core entry.
# ---------------------------------------------------------------------------

def select_device(arg_device="auto"):
    env_queue = os.environ.get("HDLAB_QUEUE", "")
    env_dev = os.environ.get("HDLAB_DEVICE", "")
    force_cpu = (arg_device == "cpu") or (env_dev == "cpu") or (env_queue == "remote_cpu_queue")
    if force_cpu:
        return torch.device("cpu")
    want_cuda = (arg_device in ("auto", "cuda")) or (env_dev == "cuda")
    return torch.device("cuda" if (want_cuda and torch.cuda.is_available()) else "cpu")


def core_main(anchor_name, seeds, run_mode, device):
    """Run one process worth of the rotation cell: self-test (always) + the seed list at the chosen scale.
    seeds = [7] for a per-seed FULL wrapper (process isolation); [7,17] for the memory smoke."""
    out_dir = get_output_dir(anchor_name)
    cfg = dict({"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG,
                "memsmoke": MEMSMOKE_CFG, "full": FULL_CFG}[run_mode])
    # fpe_dim override (2026-07-12): HDLAB_FPE_DIM env (set by --fpe-dim, or the dedicated GPU wrapper) reduces
    # ONLY the SECONDARY FPE-median readout projection dim -- the S_all (N, fpe_dim) complex phasor bank + its
    # conj-transpose is the ~3.1GiB 8GiB-card OOM driver. The PRIMARY direct-distance win metric and the KGE
    # embedding dim k are UNAFFECTED (fpe_dim is orthogonal to k), so a dim2048 run is a fully valid win-check
    # (SMOKE_CFG already uses fpe_dim=2048 and is memory-safe). Default: unset -> cfg unchanged (full=4096), so
    # the CPU definitive seeds are bit-identical to the pre-knob path. Applied to a COPY; module dicts untouched.
    _fpe_override = os.environ.get("HDLAB_FPE_DIM")
    if _fpe_override:
        try:
            _fd = int(_fpe_override)
        except ValueError:
            raise SystemExit("HDLAB_FPE_DIM=%r is not an int" % (_fpe_override,))
        if _fd <= 0:
            raise SystemExit("HDLAB_FPE_DIM=%r must be a positive int" % (_fpe_override,))
        cfg["fpe_dim"] = _fd
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, anchor_name, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log(anchor_name, "device=%s cuda=%s run_mode=%s seeds=%s fpe_dim=%s%s" %
         (device, torch.cuda.is_available(), run_mode, seeds, cfg["fpe_dim"],
          " (HDLAB_FPE_DIM override)" if _fpe_override else ""))

    st_ok, st_res = mechanism_selftest(device)
    _log(anchor_name, "mechanism_selftest ok=%s geometry_fires=%s vp_ok=%s" %
         (st_ok, st_res.get("geometry_fires"), st_res.get("validity_preflight_ok")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (rotation map-arm / must-fail discriminators did not fire)",
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS course-C ROTATION: grid oracle fires, SYN_COMPOSITIONAL rotation beats "
                        "POP+additive+discrete, SCRAMBLE does not beat, RANDOM at chance, SYN_FREQ no-manufacture; "
                        "4 validity-preflight checks declared",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log(anchor_name, "SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
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
            _log(anchor_name, "cskg seed=%d core_nodes=%d core_edges=%d avgdeg=%.1f rels=%d train=%d test=%d"
                 % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["core_avgdeg"],
                    prov["n_rel_tokens"], prov["n_train"], prov["n_test"]))
            res = run_corpus(train_lbl, valid_lbl, test_lbl, cfg, device, seed, "CSKG_XCUT_CORE", want_fpe=True)
            res["cskg_provenance"] = prov
            res["_min_support"] = cfg["min_support"]; res["_min_conf"] = cfg["min_conf"]
            min_hold = cfg.get("min_heldout", MIN_HELDOUT)
            if res.get("empty") or res["l2_genuine"]["n_l2_genuine"] < min_hold:
                raise RuntimeError("CSKG L2-genuine held-out too small (%d < %d)" %
                                   (res.get("l2_genuine", {}).get("n_l2_genuine", 0), min_hold))
            sigset = set(res["arm_sigs"].values())
            if len(sigset) < 5:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct sigs" % (seed, len(sigset)))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            fh = res["fair_hits"]; ah = res["arm_hits"]
            _log(anchor_name, "seed=%d L2gen=%d | FAIR h@%d oneshot=%s additive=%s POP=%s | agg oracle=%.3f random=%.3f "
                 "(%.1fs)" % (seed, res["l2_genuine"]["n_l2_genuine"], PRIMARY_K, fh[ONESHOT]["hits"],
                              fh[ADDITIVE]["hits"], fh[POP]["hits"], _pk(ah[ORACLE]), _pk(ah[RANDOM]), time.time() - ts))
            _hb("cskg", si)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log(anchor_name, "SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))
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

    syn_comp_summary = dict(rot_beats_pop=st_res.get("rot_beats_pop"), rot_beats_additive=st_res.get("rot_beats_additive"))
    syn_freq_summary = dict(no_manufacture=st_res.get("no_manufacture"))
    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, syn_comp_summary, syn_freq_summary)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=anchor_name,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=seeds, config=cfg, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed, reference_vet=REFERENCE_VET,
                   cross_seed_note=("single-seed process-isolated FULL; 3-seed cv gate is computed downstream over the "
                                    "3 seed metrics files (seed_cv here spans only this process's seed list)"))
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log(anchor_name, "VERDICT: %s" % verdict_msg)
    _log(anchor_name, "done (%.1fs)" % (time.perf_counter() - t_start))


def wrapper_run(anchor_name, default_seeds, default_run_mode):
    """Shared wrapper entry: parse the (optional) override flags, select device, run, with crash diagnostics."""
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "memsmoke", "full"], default=default_run_mode)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    ap.add_argument("--fpe-dim", type=int, default=None,
                    help="Override the SECONDARY FPE-readout projection dim only (primary direct-distance win "
                         "metric + KGE dim k unaffected). Sets HDLAB_FPE_DIM for core_main. Use 2048 for the "
                         "memory-safe GPU shot; unset keeps the cfg default (full=4096).")
    args, _unknown = ap.parse_known_args()
    # Unify CLI + env at the single read point in core_main. Env (set by the dedicated GPU wrapper or the
    # dispatch environment) is honored when --fpe-dim is not passed; an explicit --fpe-dim wins.
    if args.fpe_dim is not None:
        os.environ["HDLAB_FPE_DIM"] = str(args.fpe_dim)
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
    seeds = [7] if run_mode == "self_test" else default_seeds
    device = select_device(args.device)
    out_dir = str(get_output_dir(anchor_name))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(anchor_name, seeds, run_mode, device)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, anchor_name, e)
        raise
