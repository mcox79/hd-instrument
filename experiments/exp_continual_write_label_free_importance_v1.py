"""continual-write lever -- LABEL-FREE importance-inference (the distinctive axis) on a faithful Hopfield-crowding store.

The REAL lever question (Research amendment v3 + PRE-STAGE v2, off Skunkworks's GREEN demo): under capacity crowding, does a
LABEL-FREE importance-inference eviction policy preserve still-needed (important-old) facts -- WITHOUT being told which they
are -- beating write-all (crosstalk corrupts) + FIFO (drops needed), approaching the ORACLE upper-bound (which IS told)?
Protect-by-label is circular; the distinctive challenge is INFERRING importance from observable signals.

4 arms x {5 label-free proxies for arm 1} x 2 workloads x 3 seeds:
  Arm 1 label_free_inference: evict the active item with the LOWEST inferred importance. Proxies:
     LRU            importance = access-recency (last_access)                [Skunkworks GREEN-witnessed on access-correlated]
     access_freq    importance = access count
     age_weighted   importance = recency - 0.5*write-age
     kramers_escape importance = exp(-(now-last_access)/tau)  [Kim 2026 Kramers-escape: recently-accessed = high rate = high importance; recency-decay form -- MY INTERPRETATION, flag for VET]
     recall_error   importance = current recall-error (1-bitacc); at-RISK/crowded items (incl. silent-important) get protected  [MY INTERPRETATION of the recall-error proxy, flag for VET]
  Arm 2 write_all (no evict) / Arm 3 fifo (oldest) / Arm 4 oracle_protect (told the important set = ceiling)
Workload A access-correlated (important re-queried -> recency signal -> LRU should work); Workload B access-uncorrelated
  (important written-then-silent -> access proxies fail; recall_error is the best-shot to recover oracle; HONEST if it doesn't).

HARD_PASS (amendment v3 + v2): Workload A best-proxy (expect LRU) matches oracle within 0.05 + beats write_all & fifo by >=0.50;
  Workload B best-proxy (expect recall_error) matches oracle within 0.10 (LRU permitted to degrade = honest scope-of-LRU);
  best-proxy SWITCHES A->B = the workload-axis discrimination value. cv<=0.05 per (arm,proxy,workload). 4-layer-witness on land.
C1 reuse: Skunkworks demo core (codebook / recall_frac / W=sum v k^T / sign-readout) VERBATIM. local_cpu. ASCII; no em-dashes; per-seed ckpt.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "continual_write_label_free_importance_v1"
PROXIES = ["LRU", "access_freq", "age_weighted", "kramers_escape", "recall_error"]
ARMS = ["label_free_inference", "write_all", "fifo", "oracle_protect"]
WORKLOADS = ["A_access_correlated", "B_access_uncorrelated"]
REQUERY_EVERY = 3                                          # Workload A: re-query the important set every N writes (demo value)
KRAMERS_TAU = 50.0                                         # recency-decay timescale for the Kramers-escape proxy
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 128; CAP = 40; M = 600; N_IMP = 15
else:
    SEEDS = [1, 2, 3]; N = 256; CAP = 76; M = 2400; N_IMP = 30   # matches Skunkworks GREEN demo (N=256 cap=76 M=2400 n_imp=30)


def codebook(n, N, rng):                                   # VERBATIM Skunkworks demo
    return np.sign(rng.standard_normal((n, N)))


def recall_frac(W, keycb, valcb, ids, rng, noise=0.3):     # VERBATIM Skunkworks demo (frac of ids recalled at bitacc>=0.9)
    if not ids:
        return 1.0
    K = keycb[ids]; Q = K + noise * rng.standard_normal(K.shape)
    rec = np.sign(Q @ W.T); bitacc = (rec == valcb[ids]).mean(axis=1)
    return float((bitacc >= 0.9).mean())


def _bitacc_each(W, keycb, valcb, ids, rng, noise=0.3):    # per-item bitacc (for the recall_error proxy)
    K = keycb[ids]; Q = K + noise * rng.standard_normal(K.shape)
    rec = np.sign(Q @ W.T); return (rec == valcb[ids]).mean(axis=1)


def _importance(proxy, active, last_access, access_count, write_time, i, W, keycb, valcb, er_rng):
    if proxy == "LRU":            return np.array([last_access[x] for x in active], float)
    if proxy == "access_freq":    return np.array([access_count[x] for x in active], float)
    if proxy == "age_weighted":   return np.array([last_access[x] - 0.5 * (i - write_time[x]) for x in active], float)
    if proxy == "kramers_escape": return np.exp(-(i - np.array([last_access[x] for x in active], float)) / KRAMERS_TAU)
    if proxy == "recall_error":   return 1.0 - _bitacc_each(W, keycb, valcb, active, er_rng)   # importance = recall ERROR -> protect at-risk
    raise ValueError(proxy)


def run(arm, proxy, workload, seed):
    rng = np.random.default_rng(seed)
    keycb = codebook(M, N, rng); valcb = codebook(M, N, rng)
    important = list(range(N_IMP)); imp = set(important)
    W = np.zeros((N, N)); active = []; last_access = {}; access_count = {}; write_time = {}
    er_rng = np.random.default_rng(12345)                  # fixed measurement rng for recall_error proxy (deterministic)
    for i in range(M):
        W = W + np.outer(valcb[i], keycb[i]); active.append(i); last_access[i] = i; access_count[i] = 1; write_time[i] = i
        if workload == "A_access_correlated" and i % REQUERY_EVERY == 0:
            for j in important:
                if j in active:
                    last_access[j] = i; access_count[j] += 1   # re-query: important get accessed (label-free recency+count signal)
        # workload B: important written-then-silent -> NO re-query (access proxies cannot infer them)
        if len(active) > CAP:
            if arm == "write_all":
                continue
            elif arm == "fifo":
                victim = active.pop(0)
            elif arm == "oracle_protect":
                cands = [a for a in active if a not in imp] or active; victim = cands[0]; active.remove(victim)
            elif arm == "label_free_inference":
                sc = _importance(proxy, active, last_access, access_count, write_time, i, W, keycb, valcb, er_rng)
                victim = active[int(np.argmin(sc))]; active.remove(victim)   # evict LOWEST inferred importance
            else:
                raise ValueError(arm)
            W = W - np.outer(valcb[victim], keycb[victim])
    rr = np.random.default_rng(999)
    imp_active = [j for j in important if (arm == "write_all" or j in active)]
    imp_present = len(imp_active) / max(1, len(important))
    imp_rec = recall_frac(W, keycb, valcb, imp_active, rr) * imp_present   # dropped important = miss
    all_rec = recall_frac(W, keycb, valcb, active, rr)
    return {"important_old_recall": round(imp_rec, 4), "all_recall": round(all_rec, 4), "imp_present": round(imp_present, 4)}


def _combos():
    for wl in WORKLOADS:
        for arm in ARMS:
            for p in (PROXIES if arm == "label_free_inference" else [None]):
                yield wl, arm, p


def run_seed(seed):
    out = {}
    for wl, arm, p in _combos():
        key = "%s|%s|%s" % (wl, arm, p if p else "-")
        out[key] = run(arm, p, wl, seed)
    return {"seed": seed, "cells": out}


def _ck(wl, arm, p):
    return "%s|%s|%s" % (wl, arm, p if p else "-")


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    def agg(wl, arm, p, field="important_old_recall"):
        xs = [u["cells"][_ck(wl, arm, p)][field] for u in units]
        return float(np.mean(xs)), float(np.std(xs) / (abs(np.mean(xs)) + 1e-9))
    detail = {"by_workload": {}, "proxies": PROXIES, "KRAMERS_TAU": KRAMERS_TAU, "cites": ["skunkworks_continual_write_label_free_demo", "amendment_v3_v2", "kramers_escape_kim2026", "crosstalk_law_7315be3c"]}
    worst_cv = 0.0; wl_pass = {}
    for wl in WORKLOADS:
        oracle, _ = agg(wl, "oracle_protect", None); wall, _ = agg(wl, "write_all", None); fifo, _ = agg(wl, "fifo", None)
        prox = {}
        for p in PROXIES:
            m, cv = agg(wl, "label_free_inference", p); prox[p] = round(m, 4); worst_cv = max(worst_cv, cv)
        worst_cv = max(worst_cv, agg(wl, "oracle_protect", None)[1], agg(wl, "write_all", None)[1], agg(wl, "fifo", None)[1])
        best_p = max(PROXIES, key=lambda p: prox[p]); best_m = prox[best_p]
        within = 0.05 if wl == "A_access_correlated" else 0.10
        matches_oracle = best_m >= oracle - within
        beats_naive = (best_m >= wall + 0.50) and (best_m >= fifo + 0.50) if wl == "A_access_correlated" else (best_m >= wall and best_m >= fifo)
        wl_pass[wl] = matches_oracle and beats_naive
        detail["by_workload"][wl] = {"oracle": round(oracle, 4), "write_all": round(wall, 4), "fifo": round(fifo, 4),
                                     "proxies_important_old_recall": prox, "best_proxy": best_p, "best_recall": round(best_m, 4),
                                     "within_oracle": bool(matches_oracle), "beats_naive": bool(beats_naive), "pass": bool(wl_pass[wl])}
    bpA = detail["by_workload"]["A_access_correlated"]["best_proxy"]; bpB = detail["by_workload"]["B_access_uncorrelated"]["best_proxy"]
    switches = bpA != bpB
    detail["best_proxy_switches_A_to_B"] = bool(switches); detail["worst_cv"] = round(worst_cv, 4)
    seed_stable = worst_cv <= 0.05 or len(units) < 2
    summ = "A[oracle=%.2f best=%s(%.2f) wall=%.2f fifo=%.2f pass=%s] B[oracle=%.2f best=%s(%.2f) wall=%.2f fifo=%.2f pass=%s] switch=%s cv=%.3f" % (
        detail["by_workload"]["A_access_correlated"]["oracle"], bpA, detail["by_workload"]["A_access_correlated"]["best_recall"],
        detail["by_workload"]["A_access_correlated"]["write_all"], detail["by_workload"]["A_access_correlated"]["fifo"], wl_pass["A_access_correlated"],
        detail["by_workload"]["B_access_uncorrelated"]["oracle"], bpB, detail["by_workload"]["B_access_uncorrelated"]["best_recall"],
        detail["by_workload"]["B_access_uncorrelated"]["write_all"], detail["by_workload"]["B_access_uncorrelated"]["fifo"], wl_pass["B_access_uncorrelated"], switches, worst_cv)
    if not seed_stable:
        return ("MIDDLE_BAND", "MIDDLE_BAND: seed-unstable (cv>0.05). " + summ, detail)
    if wl_pass["A_access_correlated"] and wl_pass["B_access_uncorrelated"]:
        return ("HARD_PASS", "HARD_PASS (CHAIN-GRADE-CANDIDATE): label-free importance-inference matches oracle + beats naive on BOTH workloads; best-proxy switches A(%s)->B(%s)=%s = the workload-axis discrimination value. " % (bpA, bpB, switches) + summ, detail)
    if wl_pass["A_access_correlated"]:
        return ("MIDDLE_BAND", "MIDDLE_BAND: Workload A holds (label-free LRU recovers oracle in access-correlated regime) but Workload B best-proxy does NOT recover oracle within 0.10 -> honest scope-bound (label-free importance works iff access-correlated; no proxy recovers the silent-important case). " + summ, detail)
    return ("HARD_FAIL", "HARD_FAIL: label-free inference does not match oracle + beat naive even on access-correlated Workload A -> inference policy adds nothing over FIFO. " + summ, detail)


def _selftest():
    rng = np.random.default_rng(0)
    cb = codebook(4, 16, rng); assert cb.shape == (4, 16) and set(np.unique(cb).tolist()) <= {-1.0, 1.0}, "codebook bipolar"
    # store 2 facts, recall both at low noise -> ~1.0
    K = codebook(2, 64, rng); V = codebook(2, 64, rng); W = V[0:1].T @ K[0:1] + V[1:2].T @ K[1:2]
    assert recall_frac(W, K, V, [0, 1], np.random.default_rng(1), noise=0.0) == 1.0, "recall_frac identity"
    ba = _bitacc_each(W, K, V, [0, 1], np.random.default_rng(1), noise=0.0); assert ba.shape == (2,) and ba.min() >= 0.9, "bitacc_each"
    # importance: LRU evicts least-recent; recall_error returns error array
    act = [0, 1, 2]; la = {0: 5, 1: 1, 2: 9}; ac = {0: 1, 1: 1, 2: 1}; wt = {0: 0, 1: 0, 2: 0}
    sc = _importance("LRU", act, la, ac, wt, 10, None, None, None, None); assert act[int(np.argmin(sc))] == 1, "LRU evicts least-recent"
    sc2 = _importance("kramers_escape", act, la, ac, wt, 10, None, None, None, None); assert act[int(np.argmin(sc2))] == 1, "kramers evicts least-recent (decay)"
    # GREEN-direction micro-check: on access-correlated, LRU important-recall > FIFO (tiny config)
    global N, CAP, M, N_IMP
    sv = (N, CAP, M, N_IMP); N, CAP, M, N_IMP = 64, 20, 300, 8
    lru = run("label_free_inference", "LRU", "A_access_correlated", 1)["important_old_recall"]
    fifo = run("fifo", None, "A_access_correlated", 1)["important_old_recall"]
    N, CAP, M, N_IMP = sv
    assert lru >= fifo, "GREEN-direction: label-free LRU important-recall >= FIFO on access-correlated (lru=%.2f fifo=%.2f)" % (lru, fifo)
    print("[selftest] PASS: codebook + recall_frac + bitacc_each + LRU/kramers eviction + GREEN-direction LRU>=FIFO (%.2f>=%.2f)" % (lru, fifo), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] %s mode=%s seeds=%s N=%d cap=%d M=%d n_imp=%d arms=%s proxies=%s workloads=%s" % (
    ANCHOR_NAME, RUN_MODE, SEEDS, N, CAP, M, N_IMP, ARMS, PROXIES, WORKLOADS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE, "schema": "v2-4arm-5proxy-2workload"}; t0 = time.time()
for seed in SEEDS:
    key = "s%d" % seed
    if key in aggregate_partials(out_dir, [key], run_config=run_config):
        print("[ckpt] %s done; skip" % key, flush=True); continue
    r = run_seed(seed)
    a = r["cells"]; print("  [seed=%d] A:LRU=%.2f/oracle=%.2f/fifo=%.2f | B:recall_error=%.2f/oracle=%.2f/LRU=%.2f" % (
        seed, a[_ck("A_access_correlated", "label_free_inference", "LRU")]["important_old_recall"],
        a[_ck("A_access_correlated", "oracle_protect", None)]["important_old_recall"],
        a[_ck("A_access_correlated", "fifo", None)]["important_old_recall"],
        a[_ck("B_access_uncorrelated", "label_free_inference", "recall_error")]["important_old_recall"],
        a[_ck("B_access_uncorrelated", "oracle_protect", None)]["important_old_recall"],
        a[_ck("B_access_uncorrelated", "label_free_inference", "LRU")]["important_old_recall"]), flush=True)
    write_partial_key(out_dir, key, r)
units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
           "detail": detail, "metrics_source": "measured_cpu_continual_write_label_free_importance_4arm_5proxy_2workload", "per_seed": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
