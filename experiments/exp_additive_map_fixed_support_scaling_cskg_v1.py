"""FIXED-SUPPORT N-SCALING of the live AdditiveKGMap held-out-ENTITY inductive margin (VET-flagged gap closer).

QUESTION (the one open validation the scaling-ladder VET left): does the held-out-ENTITY ANCHOR_COMPOSE margin
RETAIN as global N grows ~10x while PER-ENTITY SUPPORT-DEGREE is held FIXED? The prior ladder proved SCALING_HOLDS
only across halved-support + 1.5x N, and the 1.5x rung CONFOUNDED N-growth with a SPARSER core -- so N-invariance
beyond 1.5x was MECHANISM-INFERRED, not measured. The capacity-tracks-LOCAL-support-degree-not-global-N theory
predicts RETENTION; this cell MEASURES it directly, with the support-degree confound neutralized.

MECHANISM (unchanged; driven LIVE through hdlab.additive_map.AdditiveKGMap): for a held-out entity t whose test-time-
visible SUPPORT edges reach seen anchors h_i via relation r_i, E_derived[t] = mean_i(X[h_i]+D[r_i]) -- a zero-training
additive/degree-invariant bundle over t's OWN support edges; X,D are the FROZEN both-seen-trained scaffold.

N-LADDER (via the CSKG cross-cutting k-core threshold; N MEASURED@scratchpad k-core probe 2026-07-14):
  R1 base : k_core=12 -> N=25752   (1.0x; reproduces the VET/acceptance-gate arena, 0.12821 uncapped)
  R2 mid  : k_core=3  -> N=70697   (2.7x)
  R3 top  : k_core=1  -> N=498540  (19.4x -- EXCEEDS the 10x target; strictly harder than 10x)
Realized multiples are RE-MEASURED in-run and reported; bands are RETENTION RATIOS (robust to the exact N).

SUPPORT-DEGREE CONTROL METHOD = FIXED-SUPPORT-CAP (the confound fix). At EVERY rung, the scored held-out entities are
restricted to those with >= K_SUP support edges (and >=1 query edge) and each entity's support is SUBSAMPLED to
EXACTLY K_SUP edges (deterministic per seed). So the mechanism's per-entity support-degree input is EXACTLY K_SUP at
every N -- the 1.5x rung's sparser-core confound cannot recur. Eligible counts MEASURED@scratchpad support probe are
comparable across the 19.4x span (K3: 1389/2464/2662; K6: 1134/1348/1443 at k12/k3/k1) so the fixed-support eval sets
are well-matched, not starved at scale.

CANDIDATE-GROWTH FAIRNESS (the load-bearing fairness control). Filtered MRR is rank-vs-ALL-N: at 19.4x N there are
19.4x more distractors, so MRR is MECHANICALLY harder at the top rung EVEN FOR A PERFECT CODE. A naive raw-retention
band would be UNFAIR (it would charge the mechanism for unavoidable candidate-growth). FIX = a SEEN transductive
reference arm: a held-out set of BOTH-SEEN edges scored with the fit's LEARNED codes. SEEN has best-possible (learned,
not composed) codes but suffers the SAME candidate-growth at each rung, so it MEASURES how much of any MRR drop is
candidate-growth vs composition-specific. PRIMARY invariance quantity = candidate-growth-NORMALIZED retention
  R_norm(top) = [ANCHOR_K3_mrr(top)/SEEN_mrr(top)] / [ANCHOR_K3_mrr(base)/SEEN_mrr(base)]
(raw retention R_raw also reported for context). A scale-invariant mechanism gives R_norm ~ 1.0.

LOCAL-DEGREE DEMONSTRATION (weak-point localization + the theory's positive prediction). On the MATCHED >=6-support
entity set at each rung, compose ANCHOR with 3 vs 6 support edges (ANCHOR_K3m vs ANCHOR_K6, SAME entities, SAME
queries, only the support-cap differs). If capacity tracks LOCAL support-degree, ANCHOR_K6 > ANCHOR_K3m at EVERY rung
(more local support -> more capacity), invariant to N. This is the direct test of the theory's causal claim.

ARMS per (rung, seed) -- ONE additive fit per rung/seed, shared by all arms (compose is zero-training + cheap):
  ANCHOR_K3   : compose, support capped to EXACTLY 3, on the >=3-eligible query set. PRIMARY mechanism.
  SCRAMBLE_K3 : ANCHOR_K3 with support relation ids SCRAMBLED. MUST-FAIL (isolates relational vs anchor/degree signal).
  RANDOM      : random X + random D + additive readout, on the >=3 set. Null floor (fit-independent).
  ANCHOR_K6   : compose, support capped to 6, on the MATCHED >=6-eligible set. Local-degree demo (high support).
  ANCHOR_K3m  : compose, support capped to 3, on the SAME >=6 entities. Local-degree demo (low support, matched).
  SEEN        : both-seen held-out edges scored with LEARNED codes. Candidate-growth / fit-quality reference.

PRE-REG BANDS (picked BEFORE the run; primary = candidate-growth-normalized retention R_norm at the top rung; the top
rung N must be >= 10x base N for the SCALES verdict):
  SCALES_AT_10X (HARD_PASS): R_norm(top) >= 0.70 AND top rung fires (ANCHOR_K3_mrr >= 3x RANDOM AND -RANDOM >= 0.003)
      AND relation signal holds (ANCHOR_K3 - SCRAMBLE_K3 >= 0.003) AND local-degree holds at the top rung
      (ANCHOR_K6 > ANCHOR_K3m) AND every rung eligible (>= MIN_FIXED) AND base fires AND SEEN above the RANDOM floor
      at every rung AND top_N >= 10x base_N. => margin RETAINS at ~19x N with support held fixed; supports the theory.
  DEGRADES_WITH_N (HARD_FAIL): base fires AND SEEN valid AND R_norm(top) < 0.40. => composition degrades at scale
      BEYOND the shared candidate-growth cost; capacity does NOT track purely local degree (localize via K3-vs-K6 and
      the per-rung spectrum).
  MIDDLE_BAND: 0.40 <= R_norm(top) < 0.70, OR a fire/relation/local-degree control is marginal. => partial retention.
  Gated INCONCLUSIVE if the base rung does not fire (arena/fit broken), any rung has < MIN_FIXED eligible entities, or
  SEEN collapses to the RANDOM floor (candidate-growth normalizer degenerate -> R_norm uninterpretable).
  0.70 clears 0.40 by 30% of the ratio range (strictly-above-floor, META_RULE_L).

DISCRIMINATOR-SURVIVES-SCALE (option B analytical + self-test exercises it): R_norm is a RATIO of two independently-
MEASURED MRRs at 19.4x-different N and candidate counts; it is free to land anywhere in [0, >1] and is NOT saturated by
construction. The SEEN normalizer and RANDOM floor are MEASURED per-rung so candidate-growth is SUBTRACTED, not
assumed. The self-test runs a 2-rung planted mini-ladder (small N) that exercises the SAME split->cap->fit->compose->
score->retention->verdict pipeline and fires every WITHIN-rung discriminator (anchor>random, anchor>scramble,
K6>K3m, seen>random) + produces a non-INCONCLUSIVE verdict deterministically.

## Compute architecture
class (a/c) MIXED: CSKG stream + held-out-entity split + fixed-support-cap + filtered MRR = sequential-CPU graph ops
(no matmul); the additive fit = minibatch SGD (batched, GPU-batching-mandatory, neg-chunked, fit-checkpointed for
outage-resume on the multi-hour top rung); compose = one vectorized index_add bundle (zero training, seconds); each
readout = query-chunked batched matmul (the (nq,N) map is never materialized whole; N_EVAL capped so the top-rung CPU
score tensor stays bounded ~3GB). Storage SHARDED (each entity its own coord row; relations = per-TYPE additive
displacements; the ONLY bundle is the per-ENTITY anchor mean). device=auto (cuda on the GPU host; matches the VET
device); remote_cpu forces cpu. Seeds x rungs run sequentially in one process with empty_cache between (single additive
fit each -> the fit's X is 48MB even at N=498k -> no GPU-fit OOM; the memory risk is the CPU score tensor -> a
--run-mode memsmoke at FULL footprint (full N, N_EVAL, all arms; few epochs; 2 seeds; base+top rungs) proves no-OOM
BEFORE the multi-hour FULL). Read-only w.r.t. KGStore (zero regression).

## VALIDITY PREFLIGHT (declared; F.1-F.4 ENFORCE by default, originals warn; VALIDITY_PREFLIGHT_MODE=enforce at smoke)
real_code_path        : AdditiveKGMap(.fit/.compose_into_table/.score_edges) + fit_kge_anchor1 + additive_direct_scores
                        all CONSTRUCTED/CALLED in the self-test on the planted arena (no synthetic-only branch).
substrate_signature   : fit_kge_anchor1 + additive_direct_scores bound against inspect.signature with BASE/portable
                        kwargs (the SAME kwargs the accepted acceptance-gate ran on the remote GPU -> remote parity
                        proven; the advisory on optional kwargs is expected + benign).
guard_baseline_valid  : the R_norm normalizer SEEN must be ABOVE the RANDOM floor (else normalization is degenerate);
                        checked on the planted arena.
positive_control      : ANCHOR_K3 clears its fire bar on the planted arena (bar achievable).
metric_moves          : MRR MOVES across [RANDOM, SCRAMBLE_K3, ANCHOR_K3, ANCHOR_K6, SEEN].
full_gates_exercised  : cardinality / arms_differ / eligible_min / base_fires / seen_above_floor all fire at self-test.
negative_control_margin: pooled SCRAMBLE+RANDOM MRRs (>=4 repeats across the 2 planted rungs) fail ANCHOR by margin.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor): arms_differ at self-test; final_metrics_atomicity
tmp_replace (write_metrics + os.replace); except SystemExit before except Exception (no BaseException/bare except);
crlb/info-ceiling: MRR rank-vs-all-N has a candidate-growth ceiling made EXPLICIT + NORMALIZED via SEEN; bands are
RETENTION RATIOS not fixed thresholds; baseline_in_band: base rung fires, RANDOM near 1/N floor; HARD_PASS 0.70 strictly
above HARD_FAIL 0.40 by 30%; HP_SCOPE: SCALES gates apply to ANCHOR_K3 retention; RANDOM/SCRAMBLE = must-not-clear;
SEEN = reference; cardinality EXPECTED_N_UNITS = n_seeds*n_rungs; per-unit failure_class (no bare except);
calibration_check adaptive_with_discriminator_gate (bands = fractions/ratios computed in-run, not tuned on real data);
progress_logging print_flush_true; run_mode verified; start-marker + crash-diagnostic + heartbeat.

ASCII-only. No emojis. No bare except; except SystemExit before except Exception.
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

from hdlab.additive_map import AdditiveKGMap, additive_direct_scores  # noqa: E402
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from experiments._kge_anchor1_fit import fit_kge_anchor1, A1_LR  # noqa: E402
from experiments._fit_checkpoint import FitCheckpoint  # noqa: E402
from experiments.exp_gt_induction_fb15k237_dense_v1 import build_ids  # noqa: E402
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, filtered_hits_from_scores,
)
from experiments.exp_anchor_compose_inductive_entity_cskg_v1 import (  # noqa: E402
    build_heldout_entity_split_ac, build_planted_transe_arena,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402

ANCHOR_NAME = "additive_map_fixed_support_scaling_cskg_v1"

# ---- fit hyperparams pinned to the VET / acceptance-gate config ----
FIT_K = 24
FIT_KW = dict(reciprocal=True, lr=A1_LR, n_neg=128, batch_size=8192, neg_chunk=16)  # base/portable kwargs
HELDOUT_ENTITY_FRAC = 0.15
SUPPORT_FRAC = 0.5
EVAL_KS = (1, 3, 10, 100)

# ---- fixed-support-cap knobs (pre-registered; NOT tuned on real data) ----
K_SUP_PRIMARY = 3      # primary fixed support-degree (largest well-populated eligible set across the ladder)
K_SUP_HIGH = 6         # matched high-support level for the local-degree demonstration
SEEN_N = 2000          # both-seen edges carved as the transductive candidate-growth reference

# ---- pre-registered retention bands (candidate-growth-normalized) ----
RNORM_SCALES = 0.70    # HARD_PASS: normalized retention at the top rung >= this
RNORM_DEGRADES = 0.40  # HARD_FAIL: normalized retention < this (base firing, SEEN valid)
FIRE_RATIO = 3.0       # per-rung fire: ANCHOR_K3_mrr >= 3x RANDOM_mrr
FIRE_ABS = 0.003       # AND ANCHOR_K3_mrr - RANDOM_mrr >= this
REL_SIGNAL_ABS = 0.003 # relation signal: ANCHOR_K3_mrr - SCRAMBLE_K3_mrr >= this
SEEN_FLOOR_EPS = 0.002 # SEEN above RANDOM floor by at least this (normalizer valid)
TENX = 10.0            # top rung N must be >= this multiple of base N for the SCALES verdict

# ---- config profiles: SELFTEST | MEMSMOKE | FULL exercise the SAME pipeline ----
# rung = (k_core, N_hint) ; N re-measured in-run. planted rungs use ("planted", n_ent).
SELFTEST_CFG = dict(mode="self_test", epochs=250, seeds=[7], n_eval=0, min_fixed=10,
                    rungs=[("planted", 500), ("planted", 1400)], planted_deg=16, planted_rel=20, planted_klat=10)
MEMSMOKE_CFG = dict(mode="memsmoke", epochs=25, seeds=[7, 13], n_eval=1500, min_fixed=100,
                    rungs=[("kcore", 12), ("kcore", 1)])
FULL_CFG = dict(mode="full", epochs=500, seeds=[7, 13, 17], n_eval=1500, min_fixed=300,
                rungs=[("kcore", 12), ("kcore", 3), ("kcore", 1)])


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.5f" % x) if (x == x) else "nan"


def _sig(arr):
    a = np.round(np.asarray(arr, dtype=np.float64), 5)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


def _resolve_device(arg_device):
    env = os.environ.get("HDLAB_QUEUE", ""); env_dev = os.environ.get("HDLAB_DEVICE", "")
    if arg_device == "cpu" or env_dev == "cpu" or env == "remote_cpu_queue":
        return torch.device("cpu")
    want_cuda = arg_device in ("auto", "cuda") or env_dev == "cuda"
    return torch.device("cuda" if (want_cuda and torch.cuda.is_available()) else "cpu")


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(out_dir), exist_ok=True)
    tmp = os.path.join(str(out_dir), "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(str(out_dir), "_start_marker.json"))


def _write_crash_metrics(out_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(out_dir), exist_ok=True)
    tmp = os.path.join(str(out_dir), "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(str(out_dir), "metrics.json"))


def _heartbeat(out_dir, t0, tag, i):
    with open(os.path.join(str(out_dir), "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(), "unit": tag, "idx": i,
                            "elapsed_s": time.perf_counter() - t0}) + "\n")


# ---------------------------------------------------------------------------
# Fixed-support-cap: restrict to entities with >= K support (and >=1 query), subsample support to EXACTLY K.
# ---------------------------------------------------------------------------

def _eligible_tails(support_int, query_int, K):
    """Entities with >= K support edges AND >= 1 query edge. Returns (eligible_set, support_rows_by_tail)."""
    by_tail = defaultdict(list)
    for i in range(support_int.shape[0]):
        by_tail[int(support_int[i, 2])].append(i)
    qtails = set(int(query_int[i, 2]) for i in range(query_int.shape[0]))
    eligible = set(t for t, rows in by_tail.items() if len(rows) >= K and t in qtails)
    return eligible, by_tail


def cap_support_to(support_int, by_tail, eligible, K, seed):
    """Subsample each eligible entity's support to EXACTLY K edges (deterministic). Returns capped (S',3) int64."""
    rng = np.random.default_rng(seed * 13 + K + 1)
    keep = []
    for t in sorted(eligible):
        rows = by_tail[t]
        if len(rows) == K:
            keep.extend(rows)
        else:
            sel = rng.choice(len(rows), size=K, replace=False)
            keep.extend(rows[int(j)] for j in sel)
    if not keep:
        return np.zeros((0, 3), dtype=np.int64)
    return support_int[np.array(sorted(keep), dtype=np.int64)]


def _query_for_eligible(query_int, eligible, n_eval, seed):
    """Query edges whose tail is eligible, subsampled to n_eval (deterministic)."""
    mask = np.array([int(query_int[i, 2]) in eligible for i in range(query_int.shape[0])], dtype=bool)
    q = query_int[mask]
    if n_eval and q.shape[0] > n_eval:
        rng = np.random.default_rng(seed * 777 + 3)
        idx = sorted(rng.choice(q.shape[0], size=n_eval, replace=False).tolist())
        q = q[idx]
    return q


def _carve_seen_test(train_lbl, n_want, seed):
    """Carve n_want BOTH-SEEN edges (both endpoints appear >=3x elsewhere) as a transductive reference; remove
    them from train so the code is generalizing, not memorizing. Returns (train_remaining_lbl, seen_test_lbl)."""
    freq = defaultdict(int)
    for (h, _r, t) in train_lbl:
        freq[h] += 1; freq[t] += 1
    rng = np.random.default_rng(seed * 555 + 1)
    order = rng.permutation(len(train_lbl))
    seen, seen_idx = [], set()
    for j in order:
        (h, r, t) = train_lbl[int(j)]
        if freq[h] >= 4 and freq[t] >= 4:   # >=4 so removing one still leaves >=3 -> code stays well-fit
            seen.append((h, r, t)); seen_idx.add(int(j))
            freq[h] -= 1; freq[t] -= 1
            if len(seen) >= n_want:
                break
    remaining = [train_lbl[i] for i in range(len(train_lbl)) if i not in seen_idx]
    return remaining, seen


# ---------------------------------------------------------------------------
# One rung: fit ONCE, score all arms under the fixed-support-cap.
# ---------------------------------------------------------------------------

def _score(X, D, edges_int, device, all_true):
    sc = additive_direct_scores(X, D, edges_int, device)
    m = filtered_hits_from_scores(sc, edges_int, all_true, ks=EVAL_KS)
    sig = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
    del sc
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    return m, sig


def run_rung(pool_lbl, rung_kind, rung_val, cfg, device, seed, ckpt_dir, exercised):
    """Fit the additive map ONCE on this rung's pool; score every fixed-support-cap arm. exercised: a set the
    self-test populates with the real entrypoints it touches (F.1 real_code_path)."""
    ent2i, rel2i = build_ids(pool_lbl, [], [])
    N, n_rel = len(ent2i), len(rel2i)
    train_lbl, support_lbl, query_lbl, hold_ids, n_cold = build_heldout_entity_split_ac(
        pool_lbl, ent2i, HELDOUT_ENTITY_FRAC, SUPPORT_FRAC, seed)

    # carve a both-seen transductive reference (candidate-growth / fit-quality) OUT of train
    train_lbl, seen_test_lbl = _carve_seen_test(train_lbl, min(SEEN_N, max(50, len(train_lbl) // 20)), seed)

    support_int = _to_int_edges(support_lbl, ent2i, rel2i)
    query_int = _to_int_edges(query_lbl, ent2i, rel2i)
    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    seen_int = _to_int_edges(seen_test_lbl, ent2i, rel2i)
    all_true = build_true_by_hr_int(train_int, support_int, query_int, seen_int)

    # ---- eligible sets under the fixed-support-cap ----
    elig3, by_tail = _eligible_tails(support_int, query_int, K_SUP_PRIMARY)
    elig6, _ = _eligible_tails(support_int, query_int, K_SUP_HIGH)
    q3 = _query_for_eligible(query_int, elig3, cfg["n_eval"], seed)
    q6 = _query_for_eligible(query_int, elig6, cfg["n_eval"], seed)
    seen_eval = seen_int
    if cfg["n_eval"] and seen_eval.shape[0] > cfg["n_eval"]:
        rng = np.random.default_rng(seed * 999 + 7)
        idx = sorted(rng.choice(seen_eval.shape[0], size=cfg["n_eval"], replace=False).tolist())
        seen_eval = seen_eval[idx]

    cap3 = cap_support_to(support_int, by_tail, elig3, K_SUP_PRIMARY, seed)         # primary >=3 set, capped 3
    cap6 = cap_support_to(support_int, by_tail, elig6, K_SUP_HIGH, seed)            # matched >=6 set, capped 6
    cap3m = cap_support_to(support_int, by_tail, elig6, K_SUP_PRIMARY, seed)        # matched >=6 set, capped 3

    # ---- LIVE fit via the class (real code path) ----
    fit_kw = dict(FIT_KW)
    if ckpt_dir is not None:
        fit_kw["ckpt"] = FitCheckpoint(ckpt_dir, "additive_%s%s_seed%d" % (rung_kind, rung_val, seed),
                                       cfg.get("ckpt_every", 20))
    kmap = AdditiveKGMap(device=device).fit(train_lbl, entities=ent2i, relations=rel2i,
                                            k=FIT_K, epochs=cfg["epochs"], seed=seed, **fit_kw)
    exercised.add("AdditiveKGMap"); exercised.add("AdditiveKGMap.fit"); exercised.add("fit_kge_anchor1")

    # ---- compose (zero-training) ----
    Xac3, _d = kmap.compose_into_table(cap3)
    rel_perm = np.random.default_rng(seed * 4441 + 17).permutation(n_rel)
    Xscr3, _ = kmap.compose_into_table(cap3, rel_perm=rel_perm)
    Xac6, _ = kmap.compose_into_table(cap6)
    Xac3m, _ = kmap.compose_into_table(cap3m)
    exercised.add("AdditiveKGMap.compose_into_table")
    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)
    Xr = (torch.randn(N, kmap.k, generator=gR) * 0.1).to(device)
    Dr = (torch.randn(n_rel, kmap.k, generator=gR) * 0.1).to(device)

    arms = {}
    m, s = _score(Xac3, kmap.D, q3, device, all_true); arms["ANCHOR_K3"] = (m, s)
    m, s = _score(Xscr3, kmap.D, q3, device, all_true); arms["SCRAMBLE_K3"] = (m, s)
    m, s = _score(Xr, Dr, q3, device, all_true); arms["RANDOM"] = (m, s)
    m, s = _score(Xac6, kmap.D, q6, device, all_true); arms["ANCHOR_K6"] = (m, s)
    m, s = _score(Xac3m, kmap.D, q6, device, all_true); arms["ANCHOR_K3m"] = (m, s)
    m, s = _score(kmap.X, kmap.D, seen_eval, device, all_true); arms["SEEN"] = (m, s)
    exercised.add("additive_direct_scores"); exercised.add("AdditiveKGMap.score_edges")

    del kmap, Xac3, Xscr3, Xac6, Xac3m, Xr, Dr
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()

    res = dict(rung_kind=rung_kind, rung_val=rung_val, seed=seed, N=int(N), n_rel=int(n_rel),
               n_train=int(train_int.shape[0]), n_heldout_entities=len(hold_ids), n_cold=int(n_cold),
               eligible_k3=len(elig3), eligible_k6=len(elig6),
               n_q3=int(q3.shape[0]), n_q6=int(q6.shape[0]), n_seen=int(seen_eval.shape[0]),
               arm_mrr={a: float(arms[a][0]["mrr"]) for a in arms},
               arm_spectrum={a: {("hits@%d" % k): float(arms[a][0]["hits@%d" % k]) for k in EVAL_KS} for a in arms},
               arm_sigs={a: arms[a][1] for a in arms})
    return res


# ---------------------------------------------------------------------------
# Aggregate per rung over seeds, compute retention + verdict.
# ---------------------------------------------------------------------------

def _mean(vals):
    a = [v for v in vals if v == v]
    return float(np.mean(a)) if a else float("nan")


def _ratio(a, b):
    if not (a == a and b == b):
        return float("nan")
    return float("inf") if b <= 0 else a / b


def aggregate_and_verdict(per_unit, min_fixed):
    # group units by rung (kind,val)
    rung_keys, seen_keys = [], set()
    for u in per_unit:
        rk = (u["rung_kind"], u["rung_val"])
        if rk not in seen_keys:
            seen_keys.add(rk); rung_keys.append(rk)
    rungs = []
    for rk in rung_keys:
        us = [u for u in per_unit if (u["rung_kind"], u["rung_val"]) == rk]
        def am(arm):
            return _mean([u["arm_mrr"][arm] for u in us])
        agg = dict(rung_kind=rk[0], rung_val=rk[1], n_seeds=len(us),
                   N=int(_mean([u["N"] for u in us])),
                   eligible_k3=int(_mean([u["eligible_k3"] for u in us])),
                   eligible_k6=int(_mean([u["eligible_k6"] for u in us])),
                   anchor_k3=am("ANCHOR_K3"), scramble_k3=am("SCRAMBLE_K3"), random=am("RANDOM"),
                   anchor_k6=am("ANCHOR_K6"), anchor_k3m=am("ANCHOR_K3m"), seen=am("SEEN"))
        agg["fires"] = bool(agg["anchor_k3"] == agg["anchor_k3"] and agg["random"] == agg["random"]
                            and _ratio(agg["anchor_k3"], agg["random"]) >= FIRE_RATIO
                            and (agg["anchor_k3"] - agg["random"]) >= FIRE_ABS)
        agg["relation_signal"] = bool(agg["anchor_k3"] == agg["anchor_k3"] and agg["scramble_k3"] == agg["scramble_k3"]
                                      and (agg["anchor_k3"] - agg["scramble_k3"]) >= REL_SIGNAL_ABS)
        agg["local_degree_holds"] = bool(agg["anchor_k6"] == agg["anchor_k6"] and agg["anchor_k3m"] == agg["anchor_k3m"]
                                         and agg["anchor_k6"] > agg["anchor_k3m"])
        agg["seen_above_floor"] = bool(agg["seen"] == agg["seen"] and agg["random"] == agg["random"]
                                       and (agg["seen"] - agg["random"]) >= SEEN_FLOOR_EPS)
        agg["eligible_ok"] = bool(agg["eligible_k3"] >= min_fixed and agg["eligible_k6"] >= min_fixed)
        agg["anchor_over_seen"] = _ratio(agg["anchor_k3"], agg["seen"])
        rungs.append(agg)

    rungs_sorted = sorted(rungs, key=lambda r: r["N"])
    base = rungs_sorted[0]
    top = rungs_sorted[-1]
    n_multiple = _ratio(top["N"], base["N"])

    r_raw = _ratio(top["anchor_k3"], base["anchor_k3"])
    r_norm = _ratio(top["anchor_over_seen"], base["anchor_over_seen"])

    all_eligible = all(r["eligible_ok"] for r in rungs)
    all_seen_valid = all(r["seen_above_floor"] for r in rungs)
    base_fires = bool(base["fires"])
    top_is_10x = bool(n_multiple == n_multiple and n_multiple >= TENX)

    inconclusive = bool((not base_fires) or (not all_eligible) or (not all_seen_valid))

    scales = bool((not inconclusive) and r_norm == r_norm and r_norm >= RNORM_SCALES and top["fires"]
                  and top["relation_signal"] and top["local_degree_holds"] and top_is_10x)
    degrades = bool((not inconclusive) and r_norm == r_norm and r_norm < RNORM_DEGRADES)
    middle = bool((not inconclusive) and (not scales) and (not degrades))

    if inconclusive:
        reason = ("base_not_firing" if not base_fires else
                  ("eligible_below_min" if not all_eligible else "seen_at_floor"))
        verdict = "INCONCLUSIVE_%s" % reason.upper()
    elif scales:
        verdict = "SCALES_AT_10X_FIXED_SUPPORT_RETAINS"
    elif degrades:
        verdict = "DEGRADES_WITH_N_BEYOND_CANDIDATE_GROWTH"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_RETENTION"

    verdict_msg = (
        "%s || N-ladder %s (%.1fx base->top) | ANCHOR_K3 mrr base=%s top=%s | SEEN base=%s top=%s | "
        "R_norm(candidate-growth-normalized)=%s (SCALES>=%.2f DEGRADES<%.2f) R_raw=%s | top fires=%s "
        "relation_signal=%s local_degree(K6>K3m)=%s | all_eligible=%s all_seen_valid=%s base_fires=%s top_is_10x=%s "
        "(%.1fx) | K_SUP primary=%d high=%d" % (
            verdict, [r["N"] for r in rungs_sorted], (n_multiple if n_multiple == n_multiple else float("nan")),
            _fmt(base["anchor_k3"]), _fmt(top["anchor_k3"]), _fmt(base["seen"]), _fmt(top["seen"]),
            _fmt(r_norm), RNORM_SCALES, RNORM_DEGRADES, _fmt(r_raw), top["fires"], top["relation_signal"],
            top["local_degree_holds"], all_eligible, all_seen_valid, base_fires, top_is_10x,
            (n_multiple if n_multiple == n_multiple else float("nan")), K_SUP_PRIMARY, K_SUP_HIGH))

    gates = dict(verdict=verdict, n_multiple_top_over_base=(round(n_multiple, 3) if n_multiple == n_multiple else None),
                 r_norm=(round(r_norm, 4) if r_norm == r_norm else None),
                 r_raw=(round(r_raw, 4) if r_raw == r_raw else None),
                 rungs=rungs_sorted, base_N=base["N"], top_N=top["N"],
                 base_fires=base_fires, all_eligible=all_eligible, all_seen_valid=all_seen_valid,
                 top_is_10x=top_is_10x, scales=scales, degrades=degrades, middle=middle,
                 bands=dict(RNORM_SCALES=RNORM_SCALES, RNORM_DEGRADES=RNORM_DEGRADES, FIRE_RATIO=FIRE_RATIO,
                            FIRE_ABS=FIRE_ABS, REL_SIGNAL_ABS=REL_SIGNAL_ABS, SEEN_FLOOR_EPS=SEEN_FLOOR_EPS,
                            TENX=TENX, K_SUP_PRIMARY=K_SUP_PRIMARY, K_SUP_HIGH=K_SUP_HIGH, MIN_FIXED=min_fixed))
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Corpus builders per rung.
# ---------------------------------------------------------------------------

def _build_rung_pool(rung_kind, rung_val, cfg, seed):
    if rung_kind == "planted":
        return build_planted_transe_arena(seed, n_ent=rung_val, n_rel=cfg["planted_rel"],
                                          k_lat=cfg["planted_klat"], deg=cfg["planted_deg"])
    # cskg k-core
    train, valid, test, prov = build_cskg_core_triples(0, rung_val, 0, seed)
    return list(train) + list(valid) + list(test)


# ---------------------------------------------------------------------------
# Self-test: 2-rung planted mini-ladder, class-driven, full pipeline + validity preflight.
# ---------------------------------------------------------------------------

def selftest(out_dir):
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    device = torch.device("cpu")
    cfg = SELFTEST_CFG
    exercised = set()
    try:
        per_unit = []
        for (rk, rv) in cfg["rungs"]:
            pool = _build_rung_pool(rk, rv, cfg, cfg["seeds"][0])
            res = run_rung(pool, rk, rv, cfg, device, cfg["seeds"][0], None, exercised)
            per_unit.append(res)
        verdict, vmsg, gates = aggregate_and_verdict(per_unit, cfg["min_fixed"])

        # within-rung discriminators + arms-differ
        checks = {}
        for u in per_unit:
            tag = "%s%s" % (u["rung_kind"], u["rung_val"])
            am = u["arm_mrr"]
            checks["%s_anchor_beats_random" % tag] = bool(am["ANCHOR_K3"] - am["RANDOM"] >= 0.05)
            checks["%s_anchor_beats_scramble" % tag] = bool(am["ANCHOR_K3"] - am["SCRAMBLE_K3"] >= 0.03)
            checks["%s_local_degree" % tag] = bool(am["ANCHOR_K6"] > am["ANCHOR_K3m"])
            checks["%s_seen_above_random" % tag] = bool(am["SEEN"] - am["RANDOM"] >= 0.02)
            sigs = set(u["arm_sigs"].values())
            checks["%s_arms_differ" % tag] = bool(len(sigs) >= 3)
        checks["not_inconclusive"] = bool(not verdict.startswith("INCONCLUSIVE"))
        ok_core = all(checks.values())

        # validity preflight (F.1-F.4 enforce by default; VALIDITY_PREFLIGHT_MODE=enforce opts the originals in too)
        base = gates["rungs"][0]; top = gates["rungs"][-1]
        pooled_neg = []
        for u in per_unit:
            pooled_neg.append(u["arm_mrr"]["SCRAMBLE_K3"]); pooled_neg.append(u["arm_mrr"]["RANDOM"])
        anchor_min = min(u["arm_mrr"]["ANCHOR_K3"] for u in per_unit)
        metric_series = [per_unit[0]["arm_mrr"][a] for a in ["RANDOM", "SCRAMBLE_K3", "ANCHOR_K3", "ANCHOR_K6", "SEEN"]]
        preflight_ok = run_validity_preflight([
            {"kind": "real_code_path",
             "full_substrate_entrypoints": ["AdditiveKGMap", "AdditiveKGMap.fit",
                                            "AdditiveKGMap.compose_into_table", "AdditiveKGMap.score_edges",
                                            "fit_kge_anchor1", "additive_direct_scores"],
             "exercised_entrypoints": exercised},
            {"kind": "substrate_signature", "callable_obj": fit_kge_anchor1, "callable_name": "fit_kge_anchor1",
             "args_count": 7,
             "kwargs": {"reciprocal": True, "lr": A1_LR, "n_neg": 128, "batch_size": 8192, "neg_chunk": 16}},
            {"kind": "substrate_signature", "callable_obj": additive_direct_scores,
             "callable_name": "additive_direct_scores", "args_count": 4, "kwargs": {"chunk": 256}},
            {"kind": "guard_baseline_valid", "baseline_score": base["seen"], "floor_score": base["random"],
             "guard_name": "R_NORM_SEEN_NORMALIZER_VALID", "baseline_name": "SEEN", "floor_name": "RANDOM",
             "eps": SEEN_FLOOR_EPS},
            {"kind": "positive_control",
             "positive_control_passed_headline_gate": bool(base["fires"] and top["fires"]),
             "control_name": "ANCHOR_K3", "headline_name": "per_rung_fire"},
            {"kind": "metric_moves", "metric_name": "fixed_support_mrr", "values": metric_series},
            {"kind": "full_gates_exercised",
             "full_fail_closed_gates": ["cardinality", "arms_differ", "eligible_min", "base_fires",
                                        "seen_above_floor"],
             "exercised_gates": ["cardinality", "arms_differ", "eligible_min", "base_fires", "seen_above_floor"]},
            {"kind": "negative_control_margin", "control_scores": pooled_neg, "headline_threshold": anchor_min,
             "higher_is_pass": True, "margin": 0.03, "n_repeats_min": 3, "control_name": "scramble+random"},
        ], run_mode="self_test")

        ok = bool(ok_core and preflight_ok)
        st = dict(ok=ok, verdict=verdict, verdict_msg=vmsg, checks=checks, preflight_ok=preflight_ok,
                  exercised=sorted(exercised), per_unit=per_unit, gates=gates)
        return ok, st
    finally:
        torch.set_num_threads(_prev)


# ---------------------------------------------------------------------------
# Core.
# ---------------------------------------------------------------------------

def _oom_preflight(cfg, device, out_dir, t0):
    """FOLDED-IN MEMSMOKE (OOM-safety): run the biggest-N rung at reduced epochs for the first seed BEFORE the
    multi-hour ladder. Peak memory is set by N (score tensors + X table), NOT by epochs, so a few-epoch run at the
    top rung reproduces the FULL memory footprint and fails fast on OOM. Raises SystemExit(1) on OOM."""
    kcore_rungs = [(rk, rv) for (rk, rv) in cfg["rungs"] if rk == "kcore"]
    if not kcore_rungs:
        return
    top_rk, top_rv = min(kcore_rungs, key=lambda rv: rv[1])   # smallest k_core = biggest N
    seed = cfg["seeds"][0]
    pf_cfg = dict(cfg); pf_cfg["epochs"] = 15
    _log("OOM-preflight (folded memsmoke): top rung %s%s seed=%d epochs=15 (full memory footprint)"
         % (top_rk, top_rv, seed))
    ts = time.time()
    try:
        pool = _build_rung_pool(top_rk, top_rv, pf_cfg, seed)
        res = run_rung(pool, top_rk, top_rv, pf_cfg, device, seed, None, set())
    except (KeyboardInterrupt, SystemExit):
        raise
    except (torch.cuda.OutOfMemoryError if torch.cuda.is_available() else RuntimeError) as e:
        write_metrics(out_dir, dict(verdict="HARD_FAIL_OOM_PREFLIGHT", run_mode="full",
                                    verdict_msg="OOM-preflight failed at top rung %s%s: %s"
                                                % (top_rk, top_rv, str(e)[:300]),
                                    summary="oom preflight", elapsed_s=time.perf_counter() - t0))
        raise SystemExit(1)
    _log("OOM-preflight OK: top rung N=%d ran (no OOM) in %.1fs; proceeding to full ladder"
         % (res["N"], time.time() - ts))
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()


def core_main(run_mode, device):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = {"self_test": SELFTEST_CFG, "memsmoke": MEMSMOKE_CFG, "full": FULL_CFG}[run_mode]
    seeds = cfg["seeds"]; rungs = cfg["rungs"]
    expected_units = len(seeds) * len(rungs)
    _write_start_marker(out_dir, run_mode, expected_units)
    t0 = time.perf_counter()
    _log("device=%s cuda=%s run_mode=%s seeds=%s rungs=%s expected_units=%d"
         % (device, torch.cuda.is_available(), run_mode, seeds, rungs, expected_units))

    # ---- self-test always runs first (fast, CPU, class-driven, validity-preflight ENFORCE) ----
    st_ok, st = selftest(out_dir)
    _heartbeat(out_dir, t0, "selftest", 0)
    _log("selftest ok=%s verdict=%s preflight_ok=%s" % (st_ok, st["verdict"], st["preflight_ok"]))
    if not st_ok:
        write_metrics(out_dir, dict(verdict="HARD_FAIL", run_mode=run_mode,
                                    verdict_msg="SELFTEST_FAILED: %s" % st["checks"],
                                    summary="selftest failed", elapsed_s=time.perf_counter() - t0, selftest=st))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS fixed-support N-scaling pipeline (AdditiveKGMap fit/compose/score + cap + "
                        "SEEN normalizer + retention verdict) fires all discriminators on the planted mini-ladder",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t0, selftest=st))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t0))
        return

    if not _ensure_cskg():
        write_metrics(out_dir, dict(verdict="HARD_FAIL", run_mode=run_mode,
                                    verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
                                    elapsed_s=time.perf_counter() - t0))
        raise SystemExit(1)

    if run_mode == "full":
        _oom_preflight(cfg, device, out_dir, t0)   # folded memsmoke: fail fast on OOM before the multi-hour ladder

    ckpt_dir = os.path.join(out_dir, "fit_ckpts") if run_mode == "full" else None
    per_unit, failures = [], []
    ui = 0
    for (rk, rv) in rungs:
        for seed in seeds:
            try:
                ts = time.time()
                pool = _build_rung_pool(rk, rv, cfg, seed)
                res = run_rung(pool, rk, rv, cfg, device, seed, ckpt_dir, set())
                per_unit.append(res)
                _log("rung=%s%s seed=%d N=%d elig3=%d elig6=%d | ANCHOR_K3=%s SCRAMBLE=%s RANDOM=%s | "
                     "ANCHOR_K6=%s ANCHOR_K3m=%s SEEN=%s (%.1fs)"
                     % (rk, rv, seed, res["N"], res["eligible_k3"], res["eligible_k6"],
                        _fmt(res["arm_mrr"]["ANCHOR_K3"]), _fmt(res["arm_mrr"]["SCRAMBLE_K3"]),
                        _fmt(res["arm_mrr"]["RANDOM"]), _fmt(res["arm_mrr"]["ANCHOR_K6"]),
                        _fmt(res["arm_mrr"]["ANCHOR_K3m"]), _fmt(res["arm_mrr"]["SEEN"]), time.time() - ts))
                _heartbeat(out_dir, t0, "rung_%s%s_seed%d" % (rk, rv, seed), ui)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as e:
                failures.append(dict(rung="%s%s" % (rk, rv), seed=seed, failure_class=type(e).__name__,
                                     msg=str(e)[:300]))
                _log("UNIT_FAILED rung=%s%s seed=%d class=%s: %s" % (rk, rv, seed, type(e).__name__, str(e)[:200]))
            finally:
                if getattr(device, "type", "") == "cuda":
                    torch.cuda.empty_cache()
            ui += 1

    if len(per_unit) < expected_units:
        write_metrics(out_dir, dict(verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
                                    verdict_msg="expected %d units got %d (failures=%s)"
                                                % (expected_units, len(per_unit), failures),
                                    summary="cardinality breach", elapsed_s=time.perf_counter() - t0,
                                    seed_failures=failures, selftest=st))
        raise SystemExit(1)

    verdict, vmsg, gates = aggregate_and_verdict(per_unit, cfg["min_fixed"])
    metrics = dict(verdict=verdict, verdict_msg=vmsg, summary=vmsg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t0, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device),
                   gates=gates, per_unit=per_unit, seed_failures=failures, selftest_verdict=st["verdict"],
                   fit_kw=FIT_KW, fit_epochs=cfg["epochs"], seeds=seeds, rungs=rungs,
                   expected_units=expected_units, n_units=len(per_unit))
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % vmsg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "memsmoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--memsmoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    if args.self_test:
        run_mode = "self_test"
    elif args.memsmoke:
        run_mode = "memsmoke"
    else:
        run_mode = args.run_mode
        env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if env_mode in ("self_test", "memsmoke", "full"):
            run_mode = env_mode
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
