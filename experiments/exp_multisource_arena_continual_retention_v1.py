"""CONTINUAL / lifelong-learning regime of the multi-source arena -- the RIGHT
currency for the brain-faithful CLS route/gate (retention / interference-avoidance
over sequential ingestion), NOT single-shot accuracy.

WHY THIS CELL EXISTS
--------------------
The single-shot temporal arena HARD_FAILED
(experiments/exp_multisource_arena_temporal_hold_recover_v1.py): a CLS fast/slow
route + STC hold-then-recover mechanism TIED decide-at-arrival on single-item
decision accuracy. The mandatory brain-check
(notes/research_cls_stc_currency_wrong_regime_2026-07-16.md) diagnosed this as
WRONG-CURRENCY, not a real limitation: CLS (McClelland/McNaughton/O'Reilly 1995)
and STC (Frey/Morris 1997) exist to solve CATASTROPHIC INTERFERENCE over
SEQUENTIAL multi-item learning under a shared capacity-limited store, cashed out at
a LATER RETENTION TEST -- never single-trial accuracy. A single-shot i.i.d. race is
structurally incapable of exercising the mechanism's function.

The note's load-bearing precondition (bullet, "Substrate-product implications"):
  "confirm the substrate's slow store actually has a capacity/interference
   precondition (bounded capacity, representational overlap causing crosstalk) --
   if it doesn't, the STC-style gate has nothing to economize."
The classification arena has NO such substrate (it fits signals -> a label; nothing
is stored, nothing overwrites). So this cell BUILDS the interference substrate the
route was actually designed for: a bounded, distributed, OVERLAPPING heteroassoc
superposition memory (W = sum_i v_i k_i^T; recall W k_i), where consolidating a new
(k,v) adds crosstalk to every earlier item -- the McCloskey-Cohen 1989 predicament.
The gate-signal taxonomy (schema-fit / recurrence-corroboration / importance /
reliability) is inherited conceptually from the arena; the STORAGE substrate is new
because it MUST be (per the brain-check).

DECISIVE QUESTION (contract)
----------------------------
In the CONTINUAL regime -- a STREAM of many claims ingested SEQUENTIALLY into a
bounded overlapping store -- does the brain-faithful ROUTE/gate (reliability-gate +
provisional-hold + consolidate-vs-discard keyed on schema-fit + accrued
corroboration) EARN ITS KEEP in its true currency: RETENTION of early items /
resistance to catastrophic forgetting / capacity-economy -- BEATING the engineering
baselines? AND does a SUBSTRATE-NATIVE interference-free store (exact-addressable,
no overwrite) make the brain's route UNNECESSARY (first probe of Frontier 2)?

METRIC = retention of EARLY reliable items after the whole stream has passed (recall
fidelity of the first E reliable items), scored as a function of stream length N and
representational overlap rho. NOT single-shot accuracy on the latest item.

ARMS
----
 (ii) ENGINEERING baselines:
   - consolidate_everything : write EVERY arriving item into the shared store
     immediately (no gate). Max crosstalk; the blind monolithic learner.
   - decide_at_arrival_commit: gate on arrival schema-fit ONLY, commit immediately
     and irrevocably (the "no hold" ablation -- has the gate, lacks the hold window).
 (i) BRAIN-FAITHFUL route:
   - route_gate_hold : provisional buffer (bounded fast store) holds an item across a
     hold window; consolidate-vs-discard decided from schema-fit AND accrued
     within-window corroboration (recurrence); salience one-shot bypass; buffer has
     finite capacity F (the STC finite-capture-window cost). Wins ONLY if corroboration
     carries reliability info beyond the arrival read -- i.e. if the HOLD structure
     extracts value a decide-at-arrival gate cannot. If the arrival read is already
     near-optimal, route TIES decide_at_arrival -> honest HARD_FAIL, same lesson as
     the single-shot cell but now measured in the CORRECT currency.
 (iii) SUBSTRATE-NATIVE (Frontier-2 probe):
   - native_exact_all : exact-addressable slots, bounded capacity C, interference-free
     by construction (no overwrite/crosstalk). Store-everything, evict lowest schema-fit
     when full. NO route. If this dominates BOTH engineering AND the route, the finding
     is Frontier-2: the brain needs the route because of DISTRIBUTED-OVERLAP interference
     the substrate does not natively have -- exact storage removes it (at the documented
     cost of no gist/generalization/graceful-degradation, which is WHY the brain uses a
     distributed code). Reported SEPARATELY; does not change the route's PASS/FAIL.
   - native_exact_routed : the route's OWN consolidated set stored losslessly -- isolates
     the pure interference cost the route pays for using a distributed store.

CAN-FAIL DISCIPLINE (this is NOT an engineered route-win)
---------------------------------------------------------
 (1) Arena params are set A PRIORI (schema/recurrence SNR, noise fraction, window,
     capacities) -- NOT swept until the route helps. The route can add ~0.000 and that
     is a real HARD_FAIL result.
 (2) The demanding baseline is decide_at_arrival_commit (it HAS the gate). Route earns
     HARD_PASS only by beating BOTH engineering baselines AND showing the advantage
     SCALES with interference load (grows with N) -- a flat offset is MIDDLE, not PASS
     (the scaling signature is the brain-check's diagnostic for a genuine interference
     mechanism vs a fixed calibration difference).
 (3) TWO fired positive controls + one anti-rig guard gate interpretability:
     - confirmed_forgetting (mandatory per brain-check): the consolidate_everything
       baseline MUST measurably forget early items as N grows (retention drop >=
       FORGET_MIN_DROP). If it doesn't, the interference precondition is absent, the
       regime is vacuous -> INVALID.
     - route_can_win: in a rigged-FAVOURABLE regime (high noise fraction, high-SNR gate,
       small D) a hold/gate policy PROVABLY beats consolidate-everything by >=
       POSCTRL_MIN_GAP -- proves the harness CAN reward the mechanism when the advantage
       exists (analog of the single-shot cell's fired positive control).
     - null_gate_guard (anti-rig): when the gate signal is PURE NOISE and every item is
       reliable, the route must NOT beat consolidate-everything (nothing to economize;
       gating only false-discards). If it does, the harness is rigged -> INVALID.

Arena-validity discipline: eval truth (reliability label r_i, clean value v_i) is held
SEPARATE from everything the store sees; the gate keys only on observables
(schema_fit, recurrence); retention is scored against the held-out clean v_i. No leak.

Pure-Python (numpy only). No substrate atoms, no torch, no queue/GPU, no origin push.
Runs inline in seconds. Deterministic FIXED-int seeds. Local commit only.

Run:
  python experiments/exp_multisource_arena_continual_retention_v1.py --self-test
  python experiments/exp_multisource_arena_continual_retention_v1.py --profile smoke
  python experiments/exp_multisource_arena_continual_retention_v1.py --profile full

PRE-REG BANDS (primary = mean early-reliable-item recall fidelity, held-out clean v):
  TIE_EPS = 0.010 ; X_BAND = 0.030 ; SCALE_EPS = 0.010
  eng_best(N)  = max(consolidate_everything, decide_at_arrival_commit) at N
  margin       = route_gate_hold - eng_best   (at the largest-N, overlap-averaged regime)
  gap(N)       = route_gate_hold(N) - eng_best(N)
  scaling      = gap(N_max) - gap(N_min) >= SCALE_EPS  (advantage GROWS with interference)
  HARD_PASS : arena valid + BOTH positive controls fired + null-guard held
              + margin > TIE_EPS + scaling present
              (route earns its keep in the CONTINUAL currency, with the interference-
               scaling signature of a genuine capacity mechanism).
  HARD_FAIL_ROUTE_TIES  : controls ok + margin <= TIE_EPS
              (route does NOT help even in continual learning -> deeper question, drill).
  HARD_FAIL_ROUTE_LOSES : controls ok + margin < -X_BAND.
  MIDDLE_STRUCTURE_EDGE_NOT_SCALING : margin > TIE_EPS but scaling absent (flat offset,
              not an interference mechanism).
  INVALID   : arena invalid / a positive control did not fire / null-guard broke.
  FRONTIER-2 (reported SEPARATELY): native_dominates = native_exact_all beats BOTH the
              route and eng_best by > TIE_EPS at N_max.

CELL-TEMPLATE MANDATORY (numpy design/validity cell; queue/substrate mandates n/a):
 - except SystemExit: raise BEFORE except Exception (no BaseException)
 - no bare except; deterministic FIXED-int seeds (no hash()-derived seeds); no list(set())
 - final metrics via tmp + os.replace (atomic; META_RULE_AH tmp_replace)
 - start-marker + crash-diagnostic + per-unit heartbeat written
 - arms_differ: route vs everything vs decide_at_arrival vs native retention-vectors hashed distinct
 - baseline_in_band: consolidate_everything early-item retention checked in (0.05,0.95) at N_max
 - discriminator survives scale: the discriminator IS the N-scaling of retention loss; full sweep runs it
 - CRLB: crlb_n/a = "retention is a bounded recall-fidelity in [0,1]; feasibility anchored on the
   heteroassoc crosstalk SNR = sqrt(D/M) (THEORETICAL), no Cramer-Rao noise floor applies"
 - all reported numbers MEASURED@ this run's metrics.json unless tagged else
 - real code path: the self-test EXERCISES the real storage + all 5 policies at tiny scale
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

ANCHOR_NAME = "multisource_arena_continual_retention_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO, "data", "exp_multisource_arena_continual_retention_v1")

# ---- pre-registered bands (A PRIORI) ----
TIE_EPS = 0.010
X_BAND = 0.030
SCALE_EPS = 0.010
FORGET_MIN_DROP = 0.08      # consolidate_everything must forget by >= this over the N sweep
POSCTRL_MIN_GAP = 0.10      # route must beat everything by >= this in the favourable regime

# ---- a-priori regime constants ----
E_EARLY = 10                # number of earliest RELIABLE items scored for retention
GATE_TAU = 0.0              # standardized-evidence admit threshold (principled, leak-free, per-arm identical logic)
BYPASS_Q = 0.98             # salience one-shot bypass percentile on arrival schema-fit
HOLD_WINDOW = 4             # STC finite hold window (positions)
# two INDEPENDENT noisy cues to reliability (a-priori modelling choice, NOT tuned to win):
MU_SCHEMA = 1.0             # arrival schema-fit signal separation (reliable vs noise), sd=1 -> AUC ~0.76
MU_RECUR = 0.8              # accrued within-window corroboration separation, sd=1 -> AUC ~0.71 (independent channel)

ARMS = ["consolidate_everything", "decide_at_arrival_commit", "route_gate_hold",
        "native_exact_all", "native_exact_routed"]
ENG_ARMS = ["consolidate_everything", "decide_at_arrival_commit"]


# ============================================================================
# stream generation (bounded overlapping store + observable gate cues)
# ============================================================================
def make_stream(D, N, rho, p_noise, mu_schema, mu_recur, rng):
    """A stream of N (key,value) claims with controllable representational overlap.

    keys : k_i = sqrt(1-rho) z_i + sqrt(rho) g, row-normalized  (rho = overlap knob)
    values: v_i in {-1,+1}^D  (clean content = held-out eval truth)
    reliable_i ~ Bernoulli(1 - p_noise)  (held-out eval truth)
    schema_fit_i = mu_schema*(2 reliable_i - 1) + N(0,1)   (observable arrival cue)
    recurrence_i = mu_recur *(2 reliable_i - 1) + N(0,1)   (observable INDEPENDENT
                   within-window corroboration cue accrued over the hold window)
    Cues are standardized on the stream. No cue reveals v_i; retention truth (v_i)
    is independent of the cues given reliability -> no leak."""
    g = rng.standard_normal(D)
    g = g / (np.linalg.norm(g) + 1e-12)
    Z = rng.standard_normal((N, D))
    K = np.sqrt(1.0 - rho) * Z + np.sqrt(rho) * g[None, :]
    K = K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-12)
    V = rng.choice(np.array([-1.0, 1.0]), size=(N, D))
    reliable = (rng.random(N) >= p_noise)
    sgn = (2.0 * reliable.astype(float) - 1.0)
    schema_fit = mu_schema * sgn + rng.standard_normal(N)
    recurrence = mu_recur * sgn + rng.standard_normal(N)
    schema_fit = (schema_fit - schema_fit.mean()) / (schema_fit.std() + 1e-12)
    recurrence = (recurrence - recurrence.mean()) / (recurrence.std() + 1e-12)
    return dict(K=K, V=V, reliable=reliable, schema_fit=schema_fit,
                recurrence=recurrence, D=D, N=N, rho=rho)


# ============================================================================
# storage substrates
# ============================================================================
def recall_superpose(K, V, cons_mask, probe_idx):
    """Heteroassoc superposition recall. W = sum_{i in cons} v_i k_i^T; yhat_j = W k_j.
    Returns per-probe recall fidelity = clip(cosine(yhat_j, v_j), 0, 1). Items NOT
    consolidated are naturally ~0 (only crosstalk, no signal term)."""
    idx = np.where(cons_mask)[0]
    P = np.asarray(probe_idx)
    if len(idx) == 0:
        return np.zeros(len(P))
    Kc, Vc = K[idx], V[idx]              # (M,D)
    Kp = K[P]                            # (Pn,D)
    G = Kc @ Kp.T                        # (M,Pn) key overlaps
    Yhat = Vc.T @ G                      # (D,Pn) superposed readout
    Vp = V[P].T                          # (D,Pn)
    num = np.sum(Yhat * Vp, axis=0)
    den = np.linalg.norm(Yhat, axis=0) * np.linalg.norm(Vp, axis=0) + 1e-12
    return np.clip(num / den, 0.0, 1.0)


def recall_native(keep_set, probe_idx):
    """Exact-addressable recall: 1.0 if the item holds a slot, else 0.0 (no crosstalk)."""
    return np.array([1.0 if int(j) in keep_set else 0.0 for j in probe_idx])


# ============================================================================
# write policies (produce a consolidated mask over the stream)
# ============================================================================
def policy_consolidate_everything(stream):
    return np.ones(stream["N"], dtype=bool)


def policy_decide_at_arrival(stream, tau=GATE_TAU):
    """Gate on arrival schema-fit only; commit immediately, irrevocably (no hold)."""
    return stream["schema_fit"] >= tau


def policy_route_gate_hold(stream, tau=GATE_TAU, window=HOLD_WINDOW, bypass_q=BYPASS_Q,
                           buffer_cap=None):
    """Brain-faithful CLS/STC cascade: provisional bounded buffer holds an item across
    a hold window, then consolidate-vs-discard using arrival schema-fit AND accrued
    within-window corroboration. Salience one-shot bypass for very-high arrival cue.
    Buffer capacity F is finite (STC cost): on overflow the lowest arrival-evidence
    held item is force-decided at arrival (arrival-only evidence)."""
    sf = stream["schema_fit"]
    rc = stream["recurrence"]
    N = stream["N"]
    combined = (sf + rc) / np.sqrt(2.0)               # equal-weight standardized cues (principled, not tuned)
    bypass_hi = float(np.quantile(sf, bypass_q))
    F = buffer_cap if buffer_cap is not None else max(8, N // 4)
    cons = np.zeros(N, dtype=bool)
    buffer = []                                        # indices currently held provisionally
    for i in range(N):
        if sf[i] >= bypass_hi:
            cons[i] = True                             # salience one-shot bypass
        else:
            buffer.append(i)
        while len(buffer) > F:                         # finite fast-store: force-decide overflow at arrival
            j = min(buffer, key=lambda x: sf[x])
            buffer.remove(j)
            cons[j] = sf[j] >= tau                     # arrival-only (could not be held)
        expired = [j for j in buffer if j <= i - window]
        for j in expired:                              # hold window closed: decide with combined evidence
            buffer.remove(j)
            cons[j] = combined[j] >= tau
    for j in buffer:                                   # flush tail with combined evidence
        cons[j] = combined[j] >= tau
    return cons


def native_keep_set(stream, capacity, source_mask=None):
    """Exact-addressable admission. If source_mask given (native_exact_routed) keep
    exactly those items (up to capacity, highest schema-fit first). Else
    (native_exact_all) store-everything and evict lowest schema-fit beyond capacity."""
    sf = stream["schema_fit"]
    if source_mask is not None:
        cand = np.where(source_mask)[0]
    else:
        cand = np.arange(stream["N"])
    order = cand[np.argsort(-sf[cand], kind="stable")]  # highest schema-fit first
    return set(int(j) for j in order[:capacity])


# ============================================================================
# one continual episode -> per-arm early-item retention
# ============================================================================
def early_reliable_idx(stream, e=E_EARLY):
    rel = np.where(stream["reliable"])[0]              # already in arrival order
    return rel[:e]


def run_episode(D, N, rho, p_noise, native_alpha, rng, e=E_EARLY,
                mu_schema=MU_SCHEMA, mu_recur=MU_RECUR):
    """Ingest the whole stream under each policy; measure retention of early reliable
    items. Returns per-arm mean retention + the per-item retention vectors (for
    arms-differ) + bookkeeping."""
    stream = make_stream(D, N, rho, p_noise, mu_schema, mu_recur, rng)
    probe = early_reliable_idx(stream, e)
    K, V = stream["K"], stream["V"]

    m_every = policy_consolidate_everything(stream)
    m_arr = policy_decide_at_arrival(stream)
    m_route = policy_route_gate_hold(stream)
    C = max(1, int(np.ceil(native_alpha * N)))
    keep_all = native_keep_set(stream, C, source_mask=None)
    keep_routed = native_keep_set(stream, C, source_mask=m_route)

    vecs = {
        "consolidate_everything": recall_superpose(K, V, m_every, probe),
        "decide_at_arrival_commit": recall_superpose(K, V, m_arr, probe),
        "route_gate_hold": recall_superpose(K, V, m_route, probe),
        "native_exact_all": recall_native(keep_all, probe),
        "native_exact_routed": recall_native(keep_routed, probe),
    }
    retention = {k: (float(np.mean(v)) if len(v) else 0.0) for k, v in vecs.items()}
    consolidated_counts = {
        "consolidate_everything": int(m_every.sum()),
        "decide_at_arrival_commit": int(m_arr.sum()),
        "route_gate_hold": int(m_route.sum()),
        "native_exact_all": len(keep_all),
        "native_exact_routed": len(keep_routed),
    }
    return dict(retention=retention, vecs=vecs, n_probe=int(len(probe)),
                consolidated=consolidated_counts,
                reliable_frac=float(stream["reliable"].mean()))


# ============================================================================
# controls
# ============================================================================
def positive_control_route_can_win(seed):
    """Rigged-FAVOURABLE regime: high noise fraction + high-SNR gate + small D so
    consolidating noise really hurts. A hold/gate policy PROVABLY beats
    consolidate-everything by >= POSCTRL_MIN_GAP. Proves the harness CAN reward the
    mechanism when the advantage exists."""
    rng = np.random.default_rng(seed + 40000)
    accs_route, accs_every = [], []
    for _ in range(4):
        r = run_episode(D=128, N=90, rho=0.0, p_noise=0.6, native_alpha=0.5, rng=rng,
                        mu_schema=2.2, mu_recur=1.8)
        accs_route.append(r["retention"]["route_gate_hold"])
        accs_every.append(r["retention"]["consolidate_everything"])
    route = float(np.mean(accs_route))
    every = float(np.mean(accs_every))
    return dict(route=route, everything=every, gap=route - every,
                fired=bool(route - every >= POSCTRL_MIN_GAP))


def null_gate_guard(seed):
    """Anti-rig: gate signal is PURE NOISE (mu=0) and every item reliable (p_noise=0).
    Nothing to economize; the route can only false-discard. It must NOT beat
    consolidate-everything (route <= everything + X_BAND). If it does, harness rigged."""
    rng = np.random.default_rng(seed + 50000)
    accs_route, accs_every = [], []
    for _ in range(4):
        r = run_episode(D=256, N=90, rho=0.2, p_noise=0.0, native_alpha=0.5, rng=rng,
                        mu_schema=0.0, mu_recur=0.0)
        accs_route.append(r["retention"]["route_gate_hold"])
        accs_every.append(r["retention"]["consolidate_everything"])
    route = float(np.mean(accs_route))
    every = float(np.mean(accs_every))
    return dict(route=route, everything=every, delta=route - every,
                held=bool(route - every <= X_BAND))


# ============================================================================
# metrics IO + markers
# ============================================================================
def _atomic_write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2)
    os.replace(tmp, path)


def _write_start_marker(expected_units, run_mode):
    _atomic_write(os.path.join(OUTPUT_DIR, "_start_marker.json"),
                  {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
                   "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
                   "expected_n_units": expected_units, "host": platform.node()})


def _write_crash_metrics(exc):
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"),
                  {"verdict": "CELL_CRASHED",
                   "summary": "CELL_CRASHED: %s" % type(exc).__name__,
                   "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:400]),
                   "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
                   "ts_iso": datetime.now(timezone.utc).isoformat(),
                   "anchor_name": ANCHOR_NAME})


def _hash_vec(a):
    return hashlib.sha256(np.asarray(a, dtype=np.float64).round(6).tobytes()).hexdigest()


# ============================================================================
# sweep + verdict
# ============================================================================
def run_sweep(profile, seeds, N_list, rho_list, D, p_noise, native_alpha):
    """Per (seed, N, rho) episode; aggregate retention per arm at each N (rho-averaged
    and seed-averaged)."""
    per_unit = []
    for sd in seeds:
        for N in N_list:
            for rho in rho_list:
                rng = np.random.default_rng(sd * 100003 + N * 101 + int(rho * 1000))
                r = run_episode(D, N, rho, p_noise, native_alpha, rng)
                per_unit.append(dict(seed=sd, N=N, rho=rho, retention=r["retention"],
                                     vecs=r["vecs"], consolidated=r["consolidated"],
                                     reliable_frac=r["reliable_frac"],
                                     n_probe=r["n_probe"]))
    # retention[arm][N] = mean over seeds+rho
    ret_by_N = {a: {} for a in ARMS}
    for N in N_list:
        for a in ARMS:
            vals = [u["retention"][a] for u in per_unit if u["N"] == N]
            ret_by_N[a][N] = float(np.mean(vals))
    return per_unit, ret_by_N


def aggregate_and_verdict(profile, seeds, N_list, rho_list, per_unit, ret_by_N,
                          posctrl, nullg, forget, elapsed, cfg):
    Nmax, Nmin = max(N_list), min(N_list)

    def eng_best(N):
        return max(ret_by_N[a][N] for a in ENG_ARMS)

    route_max = ret_by_N["route_gate_hold"][Nmax]
    eng_max = eng_best(Nmax)
    eng_max_name = max(ENG_ARMS, key=lambda a: ret_by_N[a][Nmax])
    margin = route_max - eng_max
    gap_max = route_max - eng_max
    gap_min = ret_by_N["route_gate_hold"][Nmin] - eng_best(Nmin)
    scaling = (gap_max - gap_min) >= SCALE_EPS

    native_max = ret_by_N["native_exact_all"][Nmax]
    native_dominates = (native_max - route_max > TIE_EPS) and (native_max - eng_max > TIE_EPS)

    # controls
    posctrl_fired = bool(posctrl["fired"])
    nullg_held = bool(nullg["held"])
    forget_fired = bool(forget["drop"] >= FORGET_MIN_DROP)
    controls_ok = posctrl_fired and nullg_held and forget_fired

    baseline_in_band = 0.05 < ret_by_N["consolidate_everything"][Nmax] < 0.95

    # arms-differ over the 4 mechanistically distinct arms at Nmax (representative seed/rho unit)
    unit = next(u for u in per_unit if u["N"] == Nmax)
    key_arms = ["route_gate_hold", "consolidate_everything",
                "decide_at_arrival_commit", "native_exact_all"]
    distinct = len({_hash_vec(unit["vecs"][a]) for a in key_arms})
    arms_differ = distinct >= 3

    # arena validity
    arena_valid = controls_ok and baseline_in_band and arms_differ
    if not controls_ok:
        arena_verdict = "ARENA_INVALID_CONTROL"
    elif not baseline_in_band:
        arena_verdict = "ARENA_INVALID_BASELINE_OUT_OF_BAND"
    elif not arms_differ:
        arena_verdict = "ARENA_INVALID_ARMS_IDENTICAL"
    else:
        arena_verdict = "ARENA_VALID"

    # verdict
    if not controls_ok:
        verdict = "INVALID_CONTROL"
    elif not baseline_in_band:
        verdict = "INVALID_BASELINE_OUT_OF_BAND"
    elif not arms_differ:
        verdict = "INVALID_ARMS_IDENTICAL"
    elif margin > TIE_EPS and scaling:
        verdict = "HARD_PASS"
    elif margin > TIE_EPS:
        verdict = "MIDDLE_STRUCTURE_EDGE_NOT_SCALING"
    elif margin < -X_BAND:
        verdict = "HARD_FAIL_ROUTE_LOSES"
    else:
        verdict = "HARD_FAIL_ROUTE_TIES"

    localization = (
        "route_beats_engineering_with_interference_scaling_earns_keep_in_continual_currency"
        if verdict == "HARD_PASS"
        else "route_beats_engineering_by_flat_offset_not_interference_scaling"
        if verdict == "MIDDLE_STRUCTURE_EDGE_NOT_SCALING"
        else "route_ties_engineering_even_in_continual_regime_no_capacity_economy_benefit"
        if verdict == "HARD_FAIL_ROUTE_TIES"
        else "route_worse_than_engineering_in_continual_regime"
        if verdict == "HARD_FAIL_ROUTE_LOSES" else "uninterpretable")

    native_finding = (
        "NATIVE_DOMINATES: exact-addressable lossless storage beats both the route and "
        "the engineering baselines -> the brain's route addresses distributed-overlap "
        "interference the substrate does not natively have (Frontier-2 signal; caveat: "
        "exact storage forgoes gist/generalization/graceful-degradation)."
        if native_dominates else
        "NATIVE_DOES_NOT_DOMINATE: exact storage does not strictly beat both -- under the "
        "tested capacity bound the distributed arms are competitive.")

    msg = ("profile=%s seeds=%d N=%s rho=%s | %s | RETENTION@Nmax=%d: route=%.3f vs "
           "eng_best[%s]=%.3f (margin=%+.3f TIE=%.3f) | scaling gap(Nmin=%d)=%+.3f -> "
           "gap(Nmax)=%+.3f (delta=%+.3f SCALE_EPS=%.3f present=%s) | native_exact_all=%.3f "
           "-> %s | every@Nmin=%.3f every@Nmax=%.3f forget_drop=%+.3f(fired=%s) | "
           "POSCTRL route-every=%+.3f(fired=%s) NULLGUARD route-every=%+.3f(held=%s) | "
           "ARENA %s | %s" %
           (profile, len(seeds), N_list, rho_list, verdict, Nmax, route_max, eng_max_name,
            eng_max, margin, TIE_EPS, Nmin, gap_min, gap_max, gap_max - gap_min, SCALE_EPS,
            scaling, native_max, "NATIVE_DOMINATES" if native_dominates else "native_no_dom",
            forget["every_small"], forget["every_large"], forget["drop"], forget_fired,
            posctrl["gap"], posctrl_fired, nullg["delta"], nullg_held, arena_verdict,
            localization))

    return {
        "verdict": verdict, "summary": verdict, "verdict_msg": msg,
        "elapsed_s": float(elapsed), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "profile": profile, "run_mode": profile,
        "seeds": list(seeds), "config": cfg,
        "primary_metric": "mean_early_reliable_item_recall_fidelity_heldout_clean_value",
        "bands": {"TIE_EPS": TIE_EPS, "X_BAND": X_BAND, "SCALE_EPS": SCALE_EPS,
                  "FORGET_MIN_DROP": FORGET_MIN_DROP, "POSCTRL_MIN_GAP": POSCTRL_MIN_GAP},
        "retention_by_N": ret_by_N,
        "contract": {
            "route_gate_hold_at_Nmax": route_max,
            "eng_best_at_Nmax": eng_max, "eng_best_name": eng_max_name,
            "margin": float(margin),
            "gap_at_Nmin": float(gap_min), "gap_at_Nmax": float(gap_max),
            "scaling_delta": float(gap_max - gap_min), "scaling_present": bool(scaling),
            "localization": localization,
        },
        "frontier2_native": {
            "native_exact_all_at_Nmax": native_max,
            "native_dominates_both": bool(native_dominates),
            "native_exact_routed_by_N": ret_by_N["native_exact_routed"],
            "finding": native_finding,
        },
        "controls": {
            "confirmed_forgetting": forget,
            "positive_control_route_can_win": posctrl,
            "null_gate_guard": nullg,
            "controls_ok": controls_ok,
        },
        "arena_validity": {"verdict": arena_verdict, "arena_valid": bool(arena_valid),
                           "baseline_in_band": bool(baseline_in_band),
                           "arms_differ_verified": bool(arms_differ),
                           "distinct_arm_outputs": int(distinct)},
        "baseline_in_band": bool(baseline_in_band),
        "arms_differ_verified": bool(arms_differ),
        "per_unit": [{k: u[k] for k in ("seed", "N", "rho", "retention", "consolidated",
                                        "reliable_frac", "n_probe")} for u in per_unit],
    }


# ============================================================================
# self-test (exercises the REAL storage + all 5 policies + both controls + guard)
# ============================================================================
def _run_selftests():
    fails, notes = [], []

    # ST-1 real-code-path: build the real store + run all 5 policies at tiny scale.
    rng = np.random.default_rng(7)
    r = run_episode(D=64, N=24, rho=0.1, p_noise=0.3, native_alpha=0.5, rng=rng, e=5)
    exercised = set(r["retention"].keys())
    notes.append("ST-1 real-code-path: policies exercised = %s; retention=%s"
                 % (sorted(exercised), {k: round(v, 3) for k, v in r["retention"].items()}))
    if set(ARMS) - exercised:
        fails.append("ST-1: not all arms exercised (%s missing)" % (set(ARMS) - exercised))
    # native must be interference-free: routed-native >= superposition route at tiny N is expected
    if not (0.0 <= r["retention"]["route_gate_hold"] <= 1.0):
        fails.append("ST-1: retention out of [0,1]")

    # ST-2 crosstalk monotonicity (the interference precondition): consolidate_everything
    # retention must DROP as N grows at fixed D (more items -> more crosstalk).
    rng = np.random.default_rng(13)
    small = np.mean([run_episode(256, 20, 0.0, 0.0, 0.5, np.random.default_rng(13 + i))
                     ["retention"]["consolidate_everything"] for i in range(3)])
    large = np.mean([run_episode(256, 200, 0.0, 0.0, 0.5, np.random.default_rng(13 + i))
                     ["retention"]["consolidate_everything"] for i in range(3)])
    notes.append("ST-2 crosstalk monotonicity: every@N20=%.3f every@N200=%.3f drop=%+.3f"
                 % (small, large, small - large))
    if not (small - large >= 0.10):
        fails.append("ST-2: consolidate_everything does not forget as N grows "
                     "(drop=%+.3f) -> interference substrate not working" % (small - large))

    # ST-3 native exact recall is lossless: a stored item recalls at exactly 1.0
    keep = native_keep_set(make_stream(64, 10, 0.0, 0.0, 1.0, 0.8, np.random.default_rng(1)),
                           capacity=10)
    v = recall_native(keep, list(range(10)))
    notes.append("ST-3 native lossless: min recall of stored items = %.3f" % float(v.min()))
    if not np.allclose(v, 1.0):
        fails.append("ST-3: native exact store is not lossless (min=%.3f)" % float(v.min()))

    # ST-4 positive control fires (harness CAN reward the mechanism)
    pc = positive_control_route_can_win(11)
    notes.append("ST-4 positive control: route=%.3f everything=%.3f gap=%+.3f fired=%s"
                 % (pc["route"], pc["everything"], pc["gap"], pc["fired"]))
    if not pc["fired"]:
        fails.append("ST-4: route_can_win positive control did NOT fire (gap=%+.3f < %.3f) "
                     "-> harness cannot reward the mechanism; a route tie would be "
                     "uninterpretable" % (pc["gap"], POSCTRL_MIN_GAP))

    # ST-5 null-gate anti-rig guard holds
    ng = null_gate_guard(11)
    notes.append("ST-5 null-gate guard: route=%.3f everything=%.3f delta=%+.3f held=%s"
                 % (ng["route"], ng["everything"], ng["delta"], ng["held"]))
    if not ng["held"]:
        fails.append("ST-5: null-gate guard BROKE (route beats everything by %+.3f with a "
                     "noise gate + no noise items) -> harness is rigged for the route"
                     % ng["delta"])

    # ST-6 no-leak: gate cue correlates with reliability but retention truth (v) is
    # sign-random independent of cues. Structural check: schema_fit informative, v mean ~0.
    s = make_stream(256, 400, 0.0, 0.3, MU_SCHEMA, MU_RECUR, np.random.default_rng(3))
    auc_like = float(s["schema_fit"][s["reliable"]].mean() - s["schema_fit"][~s["reliable"]].mean())
    v_bias = float(np.abs(s["V"].mean()))
    notes.append("ST-6 no-leak: schema_fit reliable-vs-noise sep=%.3f (informative>0); "
                 "|mean(V)|=%.4f (content sign-random, no cue->content leak)"
                 % (auc_like, v_bias))
    if auc_like <= 0.2:
        fails.append("ST-6: schema_fit not informative (sep=%.3f)" % auc_like)
    if v_bias >= 0.05:
        fails.append("ST-6: content V is biased (|mean|=%.4f) -> possible leak" % v_bias)

    return fails, notes


# ============================================================================
# main
# ============================================================================
def _forget_stats(profile, seeds, N_list, rho_list, D, p_noise, native_alpha):
    """confirmed_forgetting positive control read off the MAIN sweep: consolidate_everything
    early-item retention at Nmin vs Nmax (rho-averaged, seed-averaged)."""
    Nmin, Nmax = min(N_list), max(N_list)
    small, large = [], []
    for sd in seeds:
        for rho in rho_list:
            rng = np.random.default_rng(sd * 100003 + Nmin * 101 + int(rho * 1000))
            small.append(run_episode(D, Nmin, rho, p_noise, native_alpha, rng)
                         ["retention"]["consolidate_everything"])
            rng = np.random.default_rng(sd * 100003 + Nmax * 101 + int(rho * 1000))
            large.append(run_episode(D, Nmax, rho, p_noise, native_alpha, rng)
                         ["retention"]["consolidate_everything"])
    es, el = float(np.mean(small)), float(np.mean(large))
    return dict(every_small=es, every_large=el, drop=es - el)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--profile", choices=["smoke", "full"], default="full")
    args = ap.parse_args()
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    t0 = time.perf_counter()

    if args.self_test:
        _write_start_marker(1, "self_test")
        fails, notes = _run_selftests()
        print("=== CONTINUAL-RETENTION CELL SELF-TESTS ===")
        for nline in notes:
            print("  " + nline, flush=True)
        if fails:
            print("SELF-TEST FAILED:")
            for f in fails:
                print("  FAIL: " + f)
            _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"),
                          {"verdict": "SELFTEST_FAIL", "summary": "SELFTEST_FAIL",
                           "verdict_msg": "; ".join(fails),
                           "elapsed_s": time.perf_counter() - t0, "anchor_name": ANCHOR_NAME})
            return 2
        print("SELFTEST_PASS: real code path + crosstalk-forgetting + native-lossless + "
              "positive control fired + null-guard held + no-leak all pass")
        return 0

    profile = args.profile
    if profile == "full":
        seeds = [11, 23, 37, 53, 71]
        N_list = [30, 60, 120]
        rho_list = [0.0, 0.3]
        D, p_noise, native_alpha = 256, 0.35, 0.5
    else:
        seeds = [11, 23]
        N_list = [20, 50]
        rho_list = [0.0, 0.3]
        D, p_noise, native_alpha = 192, 0.35, 0.5
    cfg = dict(D=D, N_list=N_list, rho_list=rho_list, p_noise=p_noise,
               native_alpha=native_alpha, E_EARLY=E_EARLY, HOLD_WINDOW=HOLD_WINDOW,
               MU_SCHEMA=MU_SCHEMA, MU_RECUR=MU_RECUR)

    n_units = len(seeds) * len(N_list) * len(rho_list)
    _write_start_marker(n_units, profile)
    hb_path = os.path.join(OUTPUT_DIR, "_heartbeat.jsonl")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=== profile=%s seeds=%s N=%s rho=%s D=%d p_noise=%.2f ===" %
          (profile, seeds, N_list, rho_list, D, p_noise), flush=True)

    # controls first (interpretability gate)
    posctrl = positive_control_route_can_win(11)
    nullg = null_gate_guard(11)
    forget = _forget_stats(profile, seeds, N_list, rho_list, D, p_noise, native_alpha)
    print("  POSCTRL route_can_win: gap=%+.3f fired=%s | NULLGUARD delta=%+.3f held=%s | "
          "FORGET drop=%+.3f fired=%s" %
          (posctrl["gap"], posctrl["fired"], nullg["delta"], nullg["held"],
           forget["drop"], forget["drop"] >= FORGET_MIN_DROP), flush=True)

    per_unit, ret_by_N = run_sweep(profile, seeds, N_list, rho_list, D, p_noise, native_alpha)
    with open(hb_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                             "unit_idx": n_units, "total_units": n_units,
                             "elapsed_s": time.perf_counter() - t0}) + "\n")

    out = aggregate_and_verdict(profile, seeds, N_list, rho_list, per_unit, ret_by_N,
                                posctrl, nullg, forget, time.perf_counter() - t0, cfg)
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"), out)

    print("\n" + "=" * 78)
    print("CONTINUAL RETENTION -- PRIMARY = mean early-reliable-item recall fidelity")
    print("  %-28s %s" % ("arm \\ N", "  ".join("N=%-6d" % N for N in N_list)))
    for a in ARMS:
        print("  %-28s %s" % (a, "  ".join("%-8.3f" % ret_by_N[a][N] for N in N_list)))
    ct = out["contract"]
    print("\n  CONTRACT @Nmax: route=%.3f vs eng_best[%s]=%.3f  margin=%+.3f (TIE_EPS=%.3f)"
          % (ct["route_gate_hold_at_Nmax"], ct["eng_best_name"], ct["eng_best_at_Nmax"],
             ct["margin"], TIE_EPS))
    print("  scaling: gap(Nmin)=%+.3f gap(Nmax)=%+.3f delta=%+.3f present=%s"
          % (ct["gap_at_Nmin"], ct["gap_at_Nmax"], ct["scaling_delta"], ct["scaling_present"]))
    print("  localization: %s" % ct["localization"])
    f2 = out["frontier2_native"]
    print("\n  FRONTIER-2 NATIVE: native_exact_all@Nmax=%.3f dominates_both=%s"
          % (f2["native_exact_all_at_Nmax"], f2["native_dominates_both"]))
    print("  %s" % f2["finding"])
    cc = out["controls"]
    print("\n  CONTROLS: forgetting drop=%+.3f(fired=%s) | route_can_win gap=%+.3f(fired=%s) | "
          "null_guard delta=%+.3f(held=%s)" %
          (cc["confirmed_forgetting"]["drop"], cc["confirmed_forgetting"]["drop"] >= FORGET_MIN_DROP,
           cc["positive_control_route_can_win"]["gap"], cc["positive_control_route_can_win"]["fired"],
           cc["null_gate_guard"]["delta"], cc["null_gate_guard"]["held"]))
    print("  ARENA: %s (baseline_in_band=%s arms_differ=%s)"
          % (out["arena_validity"]["verdict"], out["baseline_in_band"],
             out["arms_differ_verified"]))
    print("\nTOP-LEVEL VERDICT: %s" % out["verdict"])
    print("  " + out["verdict_msg"])
    print("=" * 78)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit
        _write_crash_metrics(e)
        raise
    sys.exit(rc)
