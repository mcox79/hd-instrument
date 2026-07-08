"""
exp_cls_ca3complete_consolidation_v1 -- Buzsaki two-stage CLS consolidation loop (CPU, substrate-only).

BIOLOGY-FIRST (notes/research_hippocampal_biology_consolidation_loop_brain_first_2026-07-08.md,
RANK 1 + RANK 2). Continual-learning-without-forgetting, load-bearing now that ingest densifies the
KB. Buzsaki: cortex only ever receives a REPLAYED, CA3-pattern-COMPLETED signal (never the raw event),
and only during a DISCRETE offline phase with a FIXED per-cycle budget. This builds the RESCUE-4 fix
that the cycle-228 two_substrate_fastslow_cls HARD_FAIL diagnosed but never assembled with the
completion detail. Prior exp_cls_rescue4_plus_rescue2 is single-seed, has NO CA3-completion (writes
ground-truth values = answer-storage), NO no-consolidation control, NO discrete-budget phase-gate:
this cell adds all four and reuses the certified attractor-cleanup primitive as the CA3 operator.

MODEL. A stream of T (key -> concept) items arrives in E epochs. The FAST hippocampal buffer is a
recency-decayed associative matrix F (F = DECAY*F + concept outer key): recent items are recoverable,
early (OLD) items decay out -- genuine capacity-limited forgetting (the linear-store argmax readout is
otherwise too robust to forget, META_RULE_AG; recency-decay is the real substrate forgetting driver,
matching the prior rescue4/cycle-228 cells). OLD = epoch-0 items; RECENT = last-epoch items.

ARMS (identical single-step argmax readout across arms; only what is IN the queried store differs):
  NAIVE_NO_CONSOLIDATION (control): fast buffer ONLY, no offline migration. OLD is recalled from F at
    end -> decayed out -> FORGOTTEN. This is the no-consolidation catastrophic-interference control;
    it MUST forget OLD at smoke (discriminator-fires gate).
  CONSOLIDATE_FULL (mechanism): after each epoch, a DISCRETE offline phase (fixed per-phase budget B)
    replays that epoch's items via a PARTIAL cue (SWR reactivates a noisy/partial cue), CA3-completes
    the noisy FAST readout to a clean concept (iterative_cleanup), and writes it to the SLOW store S.
    OLD items are migrated while still fresh in F -> recalled from S at end -> RETAINED.
  CONSOLIDATE_NO_CLEANUP (Rank-1 ablation): same schedule/budget/partial-cue replay but SKIP the CA3
    completion (write the raw noisy readout). Isolates whether the completion (Rank 1) is load-bearing.

Replay regenerates the value FROM the fast buffer (partial cue -> readout -> CA3 completion), never
from ground truth -> honest (no answer-leak), biologically faithful (SWR replay of a partial cue).

PRE-REG (strict bands, META_RULE_L; preregs/2026-07-08_cls_ca3complete_consolidation_v1.md):
  HARD_PASS: CONSOLIDATE_FULL old_retention >= 0.80 AND new_acquisition >= 0.70
             AND NAIVE old_retention <= 0.55 (interference exercised)
             AND (CONSOLIDATE_FULL old_retention - NAIVE old_retention) >= 0.25
             AND discrete fixed-budget phase respected.
  HARD_FAIL: CONSOLIDATE_FULL old_retention <= NAIVE old_retention + 0.05 (consolidation no better)
             OR NAIVE old_retention > 0.55 at FULL (interference regime not real).
  MIDDLE_BAND: partial (one gate short).
Discriminator-fires (assert_discriminator_fires): NAIVE MUST forget OLD at smoke.
Telemetry-sensitivity self-test: corrupting the queried store drops old_retention (metric reads state).

Compute: recency-decayed matrix update is an inherently sequential recurrence (F_t depends on F_{t-1});
per-item outer-product accumulation; ~5s/seed at D=1024,T=600 -> sequential-CPU justified (wall<10s).
numpy-only, CPU-only. ASCII-only. write_metrics. except SystemExit: raise before except Exception.
atomic metrics. per-seed checkpoint via write_partial_key (fast CPU cell; matches att1 template).
"""
from __future__ import annotations
import sys, os, argparse, time, json, platform, traceback, hashlib, math
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
    assert_discriminator_fires,
)
from hdlab.iterative_attractor import iterative_cleanup

ANCHOR_NAME = "cls_ca3complete_consolidation_v1"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# ---- CA3 completion parameters (brain-canonical alpha=0.5 perforant-path re-injection) ----
CA3_TEMP = 4.0
CA3_MAX_STEPS = 6
CA3_ALPHA = 0.5

# ---- regime (smoke == full-scale params; discriminator-survives-scale option A) ----
D = 1024
T_STREAM = 600      # total stream items
N_EPOCH = 12        # consolidation phases
DECAY = 0.94        # fast-buffer recency decay (early items decay out -> genuine forgetting)
V = 64              # clean concept codebook size
BUDGET_B = 50       # fixed per-phase consolidation budget (>= items-per-epoch here)
CUE_RHO = 0.70      # partial replay cue: cue = rho*key + sqrt(1-rho^2)*random (SWR partial reactivation)

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
else:
    SEEDS = [7]

# pre-reg bands
HP_OLD_FLOOR = 0.80
HP_NEW_FLOOR = 0.70
NAIVE_FORGET_CEIL = 0.55
HP_GAP = 0.25
HF_NO_BETTER_EPS = 0.05

ARMS = ["NAIVE_NO_CONSOLIDATION", "CONSOLIDATE_FULL", "CONSOLIDATE_NO_CLEANUP"]

CONFIG_VERSION = (
    "cls_ca3complete_consolidation_v1; D=%d T=%d E=%d DECAY=%.2f V=%d BUDGET_B=%d CUE_RHO=%.2f "
    "ca3_temp=%.1f ca3_alpha=%.2f ca3_steps=%d seeds=%s mode=%s"
) % (D, T_STREAM, N_EPOCH, DECAY, V, BUDGET_B, CUE_RHO, CA3_TEMP, CA3_ALPHA, CA3_MAX_STEPS, SEEDS, RUN_MODE)


def _l2n(X, eps=1e-12):
    if X.ndim == 1:
        return (X / (np.linalg.norm(X) + eps)).astype(np.float32)
    return (X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)).astype(np.float32)


def _build_stream(seed, d, t_stream, v):
    g = np.random.default_rng(seed)
    VB = _l2n(g.standard_normal((v, d)).astype(np.float32))        # (V, d) clean concept attractors
    K = _l2n(g.standard_normal((t_stream, d)).astype(np.float32))  # (T, d) per-item keys
    val = g.integers(0, v, size=t_stream)                          # concept per item
    return g, VB, K, val


def _readout_acc(store, keys, val_idx, VB):
    """Single-step argmax readout (identical across arms). Returns top-1 accuracy."""
    R = keys.astype(np.float32) @ store.T
    pred = np.argmax(R @ VB.T, axis=1)
    return float(np.mean(pred == val_idx))


def _ca3_complete(vecs, VB):
    out = iterative_cleanup(vecs.astype(np.float32), VB, temp=CA3_TEMP,
                            max_steps=CA3_MAX_STEPS, alpha=CA3_ALPHA)
    return out["state"].astype(np.float32)


def _partial_cue(keys, rng, rho):
    """SWR partial reactivation: cue = rho*key + sqrt(1-rho^2)*random_unit (renormalized)."""
    rnd = _l2n(rng.standard_normal(keys.shape).astype(np.float32))
    return _l2n(rho * keys + math.sqrt(max(1e-6, 1.0 - rho * rho)) * rnd)


def _stream_and_consolidate(seed, d, t_stream, n_epoch, decay, v, budget_b, cue_rho):
    """Run the stream through the fast buffer; run a discrete offline consolidation phase per epoch
    for two slow stores (CA3-cleaned and raw). Returns fast buffer, both slow stores, indices, cycles."""
    g, VB, K, val = _build_stream(seed, d, t_stream, v)
    rng_replay = np.random.default_rng(seed * 7919 + 5)
    ipe = t_stream // n_epoch
    old_idx = np.arange(0, ipe)                    # epoch 0 = OLD
    rec_idx = np.arange(t_stream - ipe, t_stream)  # last epoch = RECENT
    F = np.zeros((d, d), dtype=np.float32)
    S_full = np.zeros((d, d), dtype=np.float32)
    S_nc = np.zeros((d, d), dtype=np.float32)
    per_cycle_counts = []
    for e in range(n_epoch):
        lo, hi = e * ipe, (e + 1) * ipe
        for t in range(lo, hi):                    # WAKE: sequential recency-decayed writes to FAST
            F = decay * F + np.outer(VB[val[t]], K[t]).astype(np.float32)
        # OFFLINE consolidation phase (discrete, fixed budget): replay this epoch via a partial cue.
        idx = np.arange(lo, hi)[:budget_b]
        per_cycle_counts.append(len(idx))
        cue = _partial_cue(K[idx], rng_replay, cue_rho)
        r = cue @ F.T                              # noisy FAST readout of the (partial-cued) items
        cleaned = _ca3_complete(r, VB)             # CA3 pattern completion -> clean concept
        S_full += cleaned.T @ K[idx]               # write CLEAN value to the retained (true) key
        raw = _l2n(r)
        S_nc += raw.T @ K[idx]                      # ablation: write RAW noisy readout (no completion)
    return VB, K, val, F, S_full, S_nc, old_idx, rec_idx, per_cycle_counts


def _arms_must_differ(arm_store):
    digests = {}
    for name, W in arm_store.items():
        digests[name] = hashlib.sha256(np.ascontiguousarray(W).tobytes()).hexdigest()
    names = list(digests)
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            assert digests[names[a]] != digests[names[b]], (
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical" % (names[a], names[b]))
    return digests


def run_unit(seed, d=D, t_stream=T_STREAM, n_epoch=N_EPOCH, decay=DECAY, v=V,
             budget_b=BUDGET_B, cue_rho=CUE_RHO):
    VB, K, val, F, S_full, S_nc, old_idx, rec_idx, cyc = _stream_and_consolidate(
        seed, d, t_stream, n_epoch, decay, v, budget_b, cue_rho)

    # NAIVE: fast buffer only. OLD recalled from F -> forgotten; RECENT from F -> retained.
    naive_old = _readout_acc(F, K[old_idx], val[old_idx], VB)
    naive_new = _readout_acc(F, K[rec_idx], val[rec_idx], VB)
    # CONSOLIDATE_FULL: OLD + RECENT recalled from the CA3-cleaned slow store.
    full_old = _readout_acc(S_full, K[old_idx], val[old_idx], VB)
    full_new = _readout_acc(S_full, K[rec_idx], val[rec_idx], VB)
    # CONSOLIDATE_NO_CLEANUP: same but raw-readout slow store.
    nc_old = _readout_acc(S_nc, K[old_idx], val[old_idx], VB)
    nc_new = _readout_acc(S_nc, K[rec_idx], val[rec_idx], VB)

    digests = _arms_must_differ({"NAIVE_NO_CONSOLIDATION": F, "CONSOLIDATE_FULL": S_full,
                                 "CONSOLIDATE_NO_CLEANUP": S_nc})
    budget_respected = all(c <= budget_b for c in cyc)

    per_arm = {
        "NAIVE_NO_CONSOLIDATION": {"old_retention": round(naive_old, 4), "new_acquisition": round(naive_new, 4)},
        "CONSOLIDATE_FULL": {"old_retention": round(full_old, 4), "new_acquisition": round(full_new, 4)},
        "CONSOLIDATE_NO_CLEANUP": {"old_retention": round(nc_old, 4), "new_acquisition": round(nc_new, 4)},
    }
    return {
        "seed": seed, "per_arm": per_arm,
        "budget_respected": bool(budget_respected),
        "n_consolidate_phases": len(cyc), "per_cycle_counts": cyc,
        "arm_digests": digests,
        "D": d, "T": t_stream, "E": n_epoch, "V": v, "DECAY": decay, "CUE_RHO": cue_rho,
        "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
    }


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    def am(arm, key):
        return float(np.mean([u["per_arm"][arm][key] for u in units]))
    def asd(arm, key):
        return float(np.std([u["per_arm"][arm][key] for u in units]))

    full_old = am("CONSOLIDATE_FULL", "old_retention"); full_new = am("CONSOLIDATE_FULL", "new_acquisition")
    naive_old = am("NAIVE_NO_CONSOLIDATION", "old_retention"); naive_new = am("NAIVE_NO_CONSOLIDATION", "new_acquisition")
    nc_old = am("CONSOLIDATE_NO_CLEANUP", "old_retention"); nc_new = am("CONSOLIDATE_NO_CLEANUP", "new_acquisition")
    gap = full_old - naive_old
    budget_ok = all(u["budget_respected"] for u in units)

    detail = {
        "CONSOLIDATE_FULL": {"old_retention": round(full_old, 4), "new_acquisition": round(full_new, 4),
                             "old_retention_cv": round(asd("CONSOLIDATE_FULL", "old_retention") / max(full_old, 1e-6), 4)},
        "NAIVE_NO_CONSOLIDATION": {"old_retention": round(naive_old, 4), "new_acquisition": round(naive_new, 4)},
        "CONSOLIDATE_NO_CLEANUP": {"old_retention": round(nc_old, 4), "new_acquisition": round(nc_new, 4)},
        "gap_full_minus_naive_old": round(gap, 4),
        "ca3_cleanup_lift_full_minus_nocleanup_old": round(full_old - nc_old, 4),
        "budget_respected": bool(budget_ok),
        "n_seeds": len(units), "CONFIG_VERSION": CONFIG_VERSION,
        "cites": [
            "notes/research_hippocampal_biology_consolidation_loop_brain_first_2026-07-08.md (RANK 1 + RANK 2)",
            "research_drill_cls_2substrate_rescue_2x_2026-06-11 (RESCUE-4 diagnosis, cycle-228 HF)",
            "hdlab.iterative_attractor.iterative_cleanup (certified CA3-completion primitive)",
        ],
    }
    summary = ("CONSOLIDATE_FULL old=%.3f new=%.3f | NAIVE old=%.3f new=%.3f | NO_CLEANUP old=%.3f new=%.3f | "
               "gap(full-naive old)=%.3f ca3_lift=%.3f budget_ok=%s") % (
               full_old, full_new, naive_old, naive_new, nc_old, nc_new, gap, full_old - nc_old, budget_ok)

    if full_old <= naive_old + HF_NO_BETTER_EPS:
        return ("HARD_FAIL",
                "HARD_FAIL: consolidation no better than no-consolidation control (FULL old=%.3f <= NAIVE old=%.3f "
                "+ %.2f). Consolidation does not prevent forgetting. " % (full_old, naive_old, HF_NO_BETTER_EPS) + summary, detail)
    if RUN_MODE == "full" and naive_old > NAIVE_FORGET_CEIL:
        return ("HARD_FAIL",
                "HARD_FAIL_INTERFERENCE_NOT_EXERCISED: NAIVE old=%.3f > %.2f at FULL -- forgetting regime not real. "
                % (naive_old, NAIVE_FORGET_CEIL) + summary, detail)
    if (full_old >= HP_OLD_FLOOR and full_new >= HP_NEW_FLOOR
            and naive_old <= NAIVE_FORGET_CEIL and gap >= HP_GAP and budget_ok):
        return ("HARD_PASS",
                "HARD_PASS: Buzsaki two-stage CLS consolidation retains OLD (%.3f >= %.2f) AND acquires NEW (%.3f >= %.2f) "
                "while no-consolidation forgets OLD (%.3f <= %.2f); gap=%.3f >= %.2f; discrete fixed-budget phase respected. "
                "Continual-learning-without-forgetting demonstrated. " % (
                    full_old, HP_OLD_FLOOR, full_new, HP_NEW_FLOOR, naive_old, NAIVE_FORGET_CEIL, gap, HP_GAP) + summary, detail)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: consolidation helps but one gate short (need full_old>=%.2f new>=%.2f naive_old<=%.2f gap>=%.2f). "
            % (HP_OLD_FLOOR, HP_NEW_FLOOR, NAIVE_FORGET_CEIL, HP_GAP) + summary, detail)


# -------------------- defensive error-checking (canonical exp_dev.md sec 13) --------------------
def _write_start_marker(output_dir, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp"); final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp"); final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# -------------------- self-test (mechanism + telemetry-sensitivity + CA3-denoise + discriminator-fires) --------------------
def _selftest():
    # Small-but-genuine regime for a fast mechanism check (must still forget for the discriminator gate).
    d, t, e, dec, v, bud, rho = 384, 240, 8, 0.90, 48, 30, 0.70
    u = run_unit(7, d=d, t_stream=t, n_epoch=e, decay=dec, v=v, budget_b=bud, cue_rho=rho)
    assert set(u["per_arm"].keys()) == set(ARMS), "arm set mismatch"
    vv, msg, det = compute_verdict([u])
    assert vv in ("HARD_PASS", "MIDDLE_BAND", "HARD_FAIL"), "verdict %s" % vv

    # T2: TELEMETRY-SENSITIVITY -- the metric must read store state, not be analytically pinned.
    g, VB, K, val = _build_stream(7, d, t, v)
    S = (VB[val[:60]].T @ K[:60]).astype(np.float32)   # clean store of first 60 items
    acc_full = _readout_acc(S, K[:60], val[:60], VB)
    acc_zero = _readout_acc(np.zeros_like(S), K[:60], val[:60], VB)
    acc_corrupt = _readout_acc(S + 5.0 * g.standard_normal(S.shape).astype(np.float32), K[:60], val[:60], VB)
    assert acc_full > 0.7, "T2: clean store should retain, got %.3f" % acc_full
    assert acc_zero < acc_full - 0.3, "T2: zeroed store must drop (pinned?), got %.3f vs %.3f" % (acc_zero, acc_full)
    assert acc_corrupt < acc_full - 0.1, "T2: corrupted store must drop, got %.3f vs %.3f" % (acc_corrupt, acc_full)

    # T3: CA3 completion denoises a partial-cued noisy readout (raw -> cleaned cosine to true concept up).
    F = np.zeros((d, d), dtype=np.float32)
    for tt in range(60):
        F = dec * F + np.outer(VB[val[tt]], K[tt]).astype(np.float32)
    idx = np.arange(50, 60)
    cue = _partial_cue(K[idx], np.random.default_rng(1), rho)
    r = cue @ F.T
    cleaned = _ca3_complete(r, VB)
    tgt = VB[val[idx]]
    cos_raw = float(np.mean(np.sum(_l2n(r) * tgt, axis=1)))
    cos_cln = float(np.mean(np.sum(_l2n(cleaned) * tgt, axis=1)))
    assert cos_cln > cos_raw, "T3: CA3 completion did not denoise (raw=%.3f cleaned=%.3f)" % (cos_raw, cos_cln)

    # T4: discrete fixed-budget respected.
    assert u["budget_respected"], "T4: budget not respected"

    pa = u["per_arm"]
    print("[selftest] smoke arm snapshot: naive_old=%.3f full_old=%.3f full_new=%.3f nc_old=%.3f ca3_lift=%.3f"
          % (pa["NAIVE_NO_CONSOLIDATION"]["old_retention"], pa["CONSOLIDATE_FULL"]["old_retention"],
             pa["CONSOLIDATE_FULL"]["new_acquisition"], pa["CONSOLIDATE_NO_CLEANUP"]["old_retention"],
             pa["CONSOLIDATE_FULL"]["old_retention"] - pa["CONSOLIDATE_NO_CLEANUP"]["old_retention"]), flush=True)

    # T5: DISCRIMINATOR-FIRES -- at smoke the no-consolidation control MUST forget OLD (fails headline).
    assert_discriminator_fires(
        pa["NAIVE_NO_CONSOLIDATION"]["old_retention"] >= HP_OLD_FLOOR,
        control_name="NAIVE_NO_CONSOLIDATION", headline_name="old_retention>=%.2f" % HP_OLD_FLOOR,
        run_mode="smoke", extra="no-consolidation control must forget OLD (raise DECAY-forgetting / T until it does).")
    print("[selftest] PASS: mechanism + telemetry-sensitivity + CA3-denoise + budget + discriminator-fires", flush=True)


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, len(SEEDS))
    print("[config] %s" % CONFIG_VERSION, flush=True)
    t0 = time.time()
    run_cfg = {"run_mode": RUN_MODE, "D": D, "T": T_STREAM, "E": N_EPOCH, "V": V,
               "schema": "cls-ca3complete-consolidation-v1"}
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        r = run_unit(seed)
        pa = r["per_arm"]
        print("  [seed=%d] naive old=%.3f new=%.3f | full old=%.3f new=%.3f | nc old=%.3f new=%.3f | ca3_lift=%.3f"
              % (seed, pa["NAIVE_NO_CONSOLIDATION"]["old_retention"], pa["NAIVE_NO_CONSOLIDATION"]["new_acquisition"],
                 pa["CONSOLIDATE_FULL"]["old_retention"], pa["CONSOLIDATE_FULL"]["new_acquisition"],
                 pa["CONSOLIDATE_NO_CLEANUP"]["old_retention"], pa["CONSOLIDATE_NO_CLEANUP"]["new_acquisition"],
                 pa["CONSOLIDATE_FULL"]["old_retention"] - pa["CONSOLIDATE_NO_CLEANUP"]["old_retention"]), flush=True)
        write_partial_key(out_dir, key, r)
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE,
        "D": D, "T": T_STREAM, "E": N_EPOCH, "V": V, "n_seeds": len(SEEDS),
        "detail": detail, "per_unit": units,
        "metrics_source": "measured_cpu_cls_ca3complete_consolidation_v1",
        "elapsed_s": time.time() - t0, "summary": msg,
        "substrate_only_decode_gate": "TRUE (HD substrate-native store + cleanup; no encoder)",
        "config_version": CONFIG_VERSION,
    }
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    _out = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_out, e)
        raise
