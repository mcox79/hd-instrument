"""Refuse-gate RECAPTURE via NONLINEAR readout attention-CONCENTRATION (LOCKED 2026-06-17; lead nonlinear-readout cell).

V1 6th-module YELLOW recapture. ANCHOR limiter: a LINEAR scalar bge-cosine confidence threshold (tau) cannot separate
present-gold-PARAPHRASED (high cosine, IS present) from ABSENT-gold (should refuse). RECAPTURE: use a NONLINEAR readout's
ATTENTION-CONCENTRATION as the refuse signal -- softmax/entmax over the retrieved-candidate scores CONCENTRATES when a
stored pattern genuinely matches (present, incl. paraphrase -> sharp, high max-weight) and stays DIFFUSE when nothing
matches (absent -> low max-weight / high entropy). refuse iff concentration < c; accept (return the retrieval) iff >= c.

The refuse signal is the SHAPE of the score distribution (concentration), NOT the scalar score value M1 thresholds.

DIRECTOR-LOCKED CONDITION (verify-the-referent at runtime) -- enforced at BOTH smoke AND full per Skunkworks smoke-VET:
the run MUST MEASURE the attention-spread (max-weight / entropy) on the present-paraphrased vs absent mix and CONFIRM the
readout DISCRIMINATES (present -> concentrated, absent -> diffuse). IF absent ALSO goes one-hot (spurious nearest match,
max-weight ~1) OR in-cov and gap concentrations OVERLAP (no separating c) = NON-discriminating -> NON_TEST / HONEST-NEGATIVE
(the self-dominance wall / the fuzzy-separation limit is deeper than the readout), NOT a false HARD-FAIL and NOT a
degenerate "refuse-everything" HARD_PASS.

SMOKE (laptop): SYNTHETIC via the shared spread harness -- present = cluster centroids (stored index); present-PARAPHRASED
queries = centroid + noise (near-duplicate); ABSENT queries = novel random vectors. Validates the MECHANISM + the spread-
detection + the (beta,c) operating point. NOT the recapture claim (synthetic absent = i.i.d.-random = easy).
FULL (REMOTE GPU): the ACTUAL verdict -- real bge index of the substrate corpus + held-out q54-q65 (22nd-rule firewall:
controlled one-shot eval, read-only). Per-question concentration over real bge candidate scores; MEASURE the real in-cov
vs gap concentration distributions; verdict CONDITIONED on a discriminating regime. bge encode = GPU-efficient -> remote.

Bars (= the M1 anchor): exists (beta,c) with gap-refuse>=0.95 AND in-coverage F1-drop<=0.05, AT a discriminating operating
point (in-cov accepted / gap refused; concentrations separated). HDLAB_RUN_MODE / --smoke / --self-test. ASCII-only.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch   # satisfies the overnight_queue GPU-routing gate (q_f5: literal grep for `import torch`); the FULL real
               # branch runs bge (CUDA via sentence-transformers). No module-top CUDA assert so laptop --smoke still runs.

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _spread_attention_harness import make_clustered_keys, cosine_scores, verify_spread
from _cell_provenance import provenance_fields, now_utc

ANCHOR = "substrate_refuse_gate_nonlinear_readout_v1"
# PROT-020 gate renames the run via HDLAB_EXP_NAME and validates data/exp_<HDLAB_EXP_NAME>/metrics.json -- honor it
# (the hardcoded-name vs queue-rename trap queue_add.py warns about); else fall back to the ANCHOR dir for local runs.
_EXP_NAME = os.environ.get("HDLAB_EXP_NAME")
OUT = REPO / "data" / (f"exp_{_EXP_NAME}" if _EXP_NAME else ANCHOR)

DATA_ROOT = REPO / "data" / "substrate_index"
HELDOUT = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"

BETA_GRID = [10.0, 20.0, 40.0, 80.0, 160.0]
C_GRID = [round(x, 3) for x in np.arange(0.10, 0.96, 0.05)]
ALPHA = float(os.environ.get("HDLAB_RF_ALPHA", "1.0"))  # 1.0 softmax; 1.5/2.0 = entmax sparse variant (drill-1/C1)
TOP_K = 20                                               # candidates per question (real branch); softmax over these scores
DISCRIMINATE_MARGIN = 0.10                               # in-cov vs gap concentration median separation required
MIN_INCOV_ACCEPT = 0.80                                  # accept-rate floor (guards against the refuse-everything degenerate pass)


def _rng(seed):
    return np.random.default_rng(seed)


def _short(x):
    return str(x).split("::")[-1].split("/")[-1].strip().lower()


def f1_present(pred: set, present_gold: set) -> float:
    if not present_gold:
        return 1.0 if not pred else 0.0
    inter = len(pred & present_gold)
    p = inter / len(pred) if pred else 0.0
    r = inter / len(present_gold)
    return 2 * p * r / (p + r) if (p + r) else 0.0


def entmax_alpha(Z, alpha, n_iter=30):
    if alpha == 1.0:
        Z = Z - Z.max(axis=1, keepdims=True); E = np.exp(Z); return E / (E.sum(axis=1, keepdims=True) + 1e-12)
    am1 = alpha - 1.0; Zs = am1 * Z
    tau_hi = Zs.max(axis=1, keepdims=True); tau_lo = Zs.min(axis=1, keepdims=True) - 1.0
    for _ in range(n_iter):
        tau = 0.5 * (tau_lo + tau_hi)
        s = (np.clip(Zs - tau, 0.0, None) ** (1.0 / am1)).sum(axis=1, keepdims=True)
        over = s > 1.0; tau_lo = np.where(over, tau, tau_lo); tau_hi = np.where(over, tau_hi, tau)
    p = np.clip(Zs - 0.5 * (tau_lo + tau_hi), 0.0, None) ** (1.0 / am1)
    return p / (p.sum(axis=1, keepdims=True) + 1e-12)


# ---------------------------------------------------------------------------------------------------------------------
# SYNTHETIC smoke (laptop): mechanism + spread-detection + (beta,c) operating point. NOT the recapture claim.
# ---------------------------------------------------------------------------------------------------------------------
def build_synthetic(seed, n, n_present, n_query, paraphrase_noise):
    """present = cluster centroids (stored index); present-paraphrased queries = centroid+noise; absent = novel."""
    g = _rng(seed)
    present, _ = make_clustered_keys(n_present, n, cluster_size=1, g=g)      # distinct gold items
    nq = n_query // 2
    para = np.empty((nq, n), dtype=np.float32)
    kf = max(1, int(paraphrase_noise * n))
    for i in range(nq):
        j = g.integers(0, n_present)
        q = present[j].copy(); idx = g.choice(n, size=kf, replace=False); q[idx] *= -1.0; para[i] = q
    absent = (g.integers(0, 2, size=(nq, n)).astype(np.float32) * 2 - 1)    # novel random (not near any present)
    return present, para, absent


def _concentration_synth(queries, present, beta, alpha):
    W = entmax_alpha(beta * cosine_scores(queries, present), alpha)
    return W.max(axis=1), W


def run_synthetic(fast=False):
    n = 64 if fast else 256
    seeds = [7] if fast else [7]
    n_present = 30 if fast else 60
    n_query = 40 if fast else 120
    spread_report = {}
    spread_ok_any = False
    per = {}
    for seed in seeds:
        present, para, absent = build_synthetic(seed, n, n_present, n_query, 0.10)
        for beta in BETA_GRID:
            cp, _ = _concentration_synth(para, present, beta, ALPHA)
            ca, Wa = _concentration_synth(absent, present, beta, ALPHA)
            absent_spreads = bool(np.median(ca) < 0.9) and verify_spread(Wa)["spreads"]
            spread_report[f"beta{beta}"] = {"present_maxw_med": float(np.median(cp)),
                                            "absent_maxw_med": float(np.median(ca)), "absent_spreads": absent_spreads}
            if absent_spreads:
                spread_ok_any = True
            for c in C_GRID:
                gap_refuse = float((ca < c).mean()); accept_drop = 1.0 - float((cp >= c).mean())
                per.setdefault(f"{beta}_{c}", []).append((gap_refuse, accept_drop, absent_spreads))
    best = {"beta": None, "c": None, "gap_refuse": 0.0, "accept_drop": 1.0}
    for key, vals in per.items():
        gr = float(np.mean([v[0] for v in vals])); ad = float(np.mean([v[1] for v in vals])); sp = all(v[2] for v in vals)
        if sp and gr >= 0.95 and ad <= 0.05 and (gr - ad) > (best["gap_refuse"] - best["accept_drop"]):
            b, c = key.split("_"); best = {"beta": float(b), "c": float(c), "gap_refuse": gr, "accept_drop": ad}
    if not spread_ok_any:
        verdict = "NON_TEST"
        msg = (f"SYNTHETIC NON-TEST (self-dominance): absent ALSO concentrates at all beta -> readout does not discriminate. "
               f"spread_report={spread_report}. (alpha={ALPHA}, n={n}.)")
    elif best["beta"] is not None:
        verdict = "HARD_PASS"
        msg = (f"SYNTHETIC HARD_PASS: nonlinear-readout concentration refuse-gate separates present-paraphrased from absent "
               f"where linear cosine-tau (M1) could not -- (beta={best['beta']}, c={best['c']}): gap-refuse "
               f"{best['gap_refuse']:.3f}>=0.95 AND accept-drop {best['accept_drop']:.3f}<=0.05. MECHANISM + spread-detection "
               f"+ operating point validated; NOT the recapture claim (synthetic absent = i.i.d.-random = easy). REAL held-out "
               f"q54-q65 FULL is the actual verdict. (alpha={ALPHA}, n={n}.)")
    else:
        verdict = "HARD_FAIL"
        msg = (f"SYNTHETIC HARD_FAIL: no (beta,c) reaches the bars in a spread regime. spread_report={spread_report}.")
    return {"mode_path": "synthetic", "verdict": verdict, "verdict_msg": msg, "spread_report": spread_report,
            "spread_ok_any": spread_ok_any, "best": best, "alpha": ALPHA, "n": n}


# ---------------------------------------------------------------------------------------------------------------------
# REAL held-out FULL (REMOTE GPU): the ACTUAL verdict. bge index + held-out q54-q65 (read-only, 22nd-rule firewall).
# ---------------------------------------------------------------------------------------------------------------------
def run_real_heldout():
    if not HELDOUT.exists():
        return {"mode_path": "real", "error": "no_heldout_file:" + str(HELDOUT)}
    try:
        from backend.substrate_index.partition import PartitionedStore
        from backend.substrate_index.encode import AtomEncoder
        from backend.substrate_index.retrieve import Retriever
        from backend.substrate_index.retrieve_cache import rebuild_index_cached
    except Exception as e:
        return {"mode_path": "real", "error": "import_failed:" + str(e)[:120]}
    assert torch.cuda.is_available(), "GPU not available (FULL bge encode needs CUDA; route to GPU queue)"
    pstore = PartitionedStore(DATA_ROOT)
    n_atoms = len(pstore.all_atoms())
    print(f"[{ANCHOR}] real-path: {n_atoms} atoms in store; loading bge encoder...", flush=True)
    try:
        enc = AtomEncoder()
    except Exception as e:
        return {"mode_path": "real", "error": "bge_unavailable:" + str(e)[:100]}
    print(f"[{ANCHOR}] bge loaded; rebuild_index_cached over {n_atoms} atoms (HEAVY if cache miss -- the ~13min step)...", flush=True)
    r = Retriever(pstore, enc); rebuild_index_cached(r, DATA_ROOT)
    sem = getattr(r, "_semantic_matrix", None)
    print(f"[{ANCHOR}] index ready (indexed={None if sem is None else sem.shape[0]}/{n_atoms}); loading held-out + scoring...", flush=True)
    qual = {a.id: a.qualified_id for a in pstore.all_atoms()}
    sset = {_short(a.id) for a in pstore.all_atoms()}
    qs = [json.loads(l) for l in open(HELDOUT, encoding="utf-8") if l.strip()]
    print(f"[{ANCHOR}] {len(qs)} held-out questions; running semantic retrieval per question...", flush=True)
    perq = []
    for _qi, q in enumerate(qs):
        if _qi % 5 == 0:
            print(f"[{ANCHOR}]   scoring question {_qi + 1}/{len(qs)}", flush=True)
        gold = q.get("ground_truth_atoms") or []
        present = {_short(g) for g in gold if _short(g) in sset}
        in_cov = bool(present)
        try:
            cands = r.semantic(q["question"], top_k=TOP_K)
        except Exception:
            cands = []
        scores = np.array([float(getattr(c, "score", 0.0)) for c in cands], dtype=np.float32)
        cand_ids = [_short(qual.get(c.atom_id, c.atom_id)) for c in cands]
        # ungated per-q F1 = accept-everything baseline (predict all top-K candidate ids)
        ungated_f1 = f1_present(set(cand_ids), present) if in_cov else None
        perq.append({"qid": q.get("qid"), "in_cov": in_cov, "present": present, "scores": scores,
                     "cand_ids": cand_ids, "ungated_f1": ungated_f1})
    inc = [x for x in perq if x["in_cov"]]
    gap = [x for x in perq if not x["in_cov"]]
    ungated_in_cov_f1 = float(np.mean([x["ungated_f1"] for x in inc])) if inc else 0.0

    def conc_of(scores, beta):
        if scores.size == 0:
            return 0.0
        W = entmax_alpha((beta * scores)[None, :], ALPHA)
        return float(W.max())

    # spread distributions per beta (the LOCKed verify-the-referent measurement on the REAL mix)
    spread_report = {}
    rows = []
    for beta in BETA_GRID:
        inc_conc = np.array([conc_of(x["scores"], beta) for x in inc], dtype=np.float32)
        gap_conc = np.array([conc_of(x["scores"], beta) for x in gap], dtype=np.float32)
        inc_med = float(np.median(inc_conc)) if inc_conc.size else 0.0
        gap_med = float(np.median(gap_conc)) if gap_conc.size else 0.0
        # discriminating regime: in-cov concentrates ABOVE gap by a margin (not both one-hot, not both diffuse)
        discriminates = (inc_med - gap_med) >= DISCRIMINATE_MARGIN
        spread_report[f"beta{beta}"] = {"in_cov_conc_med": round(inc_med, 4), "gap_conc_med": round(gap_med, 4),
                                        "in_cov_minus_gap": round(inc_med - gap_med, 4), "discriminates": discriminates}
        for c in C_GRID:
            gap_refuse = float((gap_conc < c).mean()) if gap_conc.size else 1.0
            inc_accept = (inc_conc >= c)
            inc_accept_rate = float(inc_accept.mean()) if inc_conc.size else 0.0
            # gated in-cov F1: accepted q keep ungated F1, refused q -> 0
            gated_f1 = float(np.mean([x["ungated_f1"] if acc else 0.0 for x, acc in zip(inc, inc_accept)])) if inc else 0.0
            f1_drop = ungated_in_cov_f1 - gated_f1
            rows.append({"beta": beta, "c": c, "gap_refuse": round(gap_refuse, 4), "in_cov_accept_rate": round(inc_accept_rate, 4),
                         "gated_in_cov_f1": round(gated_f1, 4), "f1_drop": round(f1_drop, 4), "discriminates": discriminates})

    # HARD-PASS: gap-refuse>=0.95 AND f1-drop<=0.05 AT a discriminating operating point (in-cov accepted, concentrations separated)
    ok = [r_ for r_ in rows if r_["gap_refuse"] >= 0.95 and r_["f1_drop"] <= 0.05
          and r_["discriminates"] and r_["in_cov_accept_rate"] >= MIN_INCOV_ACCEPT]
    best = max(ok, key=lambda r_: (r_["gap_refuse"] - r_["f1_drop"])) if ok else None
    any_discriminating = any(s["discriminates"] for s in spread_report.values())
    return {"mode_path": "real", "n_in_cov": len(inc), "n_gap": len(gap), "ungated_in_cov_f1": round(ungated_in_cov_f1, 4),
            "spread_report": spread_report, "any_discriminating_beta": any_discriminating, "sweep": rows, "best": best,
            "alpha": ALPHA, "top_k": TOP_K, "discriminate_margin": DISCRIMINATE_MARGIN, "min_in_cov_accept": MIN_INCOV_ACCEPT}


def verdict_real(r):
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    best = r["best"]
    base = (f"REAL held-out q54-q65 (in-cov={r['n_in_cov']}, gap={r['n_gap']}; ungated in-cov F1={r['ungated_in_cov_f1']}). "
            f"Concentration spread by beta (in-cov vs gap median, the verify-the-referent measurement on the REAL mix): "
            f"{r['spread_report']}.")
    if not r["any_discriminating_beta"]:
        return ("NON_TEST", "NON_TEST (no discriminating regime on the REAL held-out): in-cov and gap concentrations do NOT "
                "separate at any beta (either both one-hot = self-dominance, or both diffuse) -> the present-paraphrased vs "
                "near-present-absent separation is DEEPER than the nonlinear readout. Refuse-gate stays YELLOW; next = learned "
                "adapter, NOT a readout swap. (This is the actual hard question the synthetic smoke could not answer.) " + base)
    if best is not None:
        return ("HARD_PASS", f"HARD_PASS (V1 6th-module refuse-gate RECAPTURED on real held-out): at beta={best['beta']}, "
                f"c={best['c']} -- gap-refuse={best['gap_refuse']}>=0.95 AND in-cov F1-drop={best['f1_drop']}<=0.05 at a "
                f"DISCRIMINATING operating point (in-cov accept-rate={best['in_cov_accept_rate']}>= {r['min_in_cov_accept']}; "
                f"concentrations separated by >= {r['discriminate_margin']}). The nonlinear-readout attention-concentration "
                f"separates present-paraphrased from absent where M1's LINEAR cosine-tau FAILED. measured-bounds: envelope of "
                f"this method (alpha={r['alpha']}, top_k={r['top_k']}) on q54-q65; transfer UNTESTED. " + base)
    return ("HARD_FAIL", "HARD_FAIL (does NOT recapture despite a discriminating beta): no (beta,c) reaches gap-refuse>=0.95 + "
            "F1-drop<=0.05 at a discriminating, non-degenerate (in-cov-accepted) operating point -> the concentration gate "
            "cannot hit both bars without falsely refusing present questions. Honest bound -> learned adapter next. " + base)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="synthetic mechanism + spread-detection check (laptop-safe)")
    ap.add_argument("--self-test", action="store_true", help="PROT-020 fast wiring-check (<30s; tiny synthetic; no bge)")
    ap.add_argument("--full", action="store_true", help="force REAL held-out FULL (remote dispatch; overrides env)")
    args, _ = ap.parse_known_args()
    # Default FULL for remote dispatch (the autonomous GPU runner does NOT export HDLAB_RUN_MODE=full -- matches Action A's
    # proven default). --smoke/--self-test force smoke (the gate + laptop); --full forces full (explicit override).
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full").lower()
    self_test = getattr(args, "self_test", False)
    is_smoke = (args.smoke or self_test or run_mode == "smoke") and not getattr(args, "full", False)
    t0 = time.time()
    run_started_utc = now_utc()

    # BRANCH DIAGNOSTIC (verify-the-referent at runtime): print the exact path BEFORE running, so the remote stdout/gate_log
    # PROVES which path executed -- no more inferring smoke-vs-full from a (possibly stale) metrics.json.
    _path = "self_test_wiring(no-write)" if self_test else ("synthetic_smoke" if is_smoke else "REAL_held_out_q54_q65")
    print(f"[{ANCHOR}] BRANCH: run_mode={run_mode} self_test={self_test} args.smoke={args.smoke} "
          f"args.full={getattr(args, 'full', False)} -> PATH={_path}", flush=True)

    # --self-test is a PURE wiring check (queue_add gate checks exit 0 ONLY). It must NOT write metrics.json: queue_add runs
    # it under HDLAB_EXP_NAME=<entry>, so writing here would pollute data/exp_<entry>/metrics.json with synthetic n=64 output
    # that masquerades as the run if the real FULL is slow/killed/not-overwritten (the stale-n=64 smoke-bug Orchestrator saw).
    if self_test:
        run_synthetic(fast=True)
        print(f"[{ANCHOR}] --self-test wiring OK (synthetic harness imports + runs); NO metrics written (full-path uncontaminated).")
        return 0

    if is_smoke:
        r = run_synthetic(fast=self_test)
        v, vmsg = r["verdict"], r["verdict_msg"]
        path_note = "synthetic smoke (mechanism + spread-detection); REAL held-out FULL is the actual verdict"
    else:
        # FAIL-LOUD-NEVER-SILENT: any exception in the 13-min real path STILL writes a metrics.json (status=UNKNOWN +
        # error + traceback), so a remote failure is never a silent no-metrics death (Orchestrator's REAL_PATH_HIT note).
        try:
            r = run_real_heldout()
        except Exception as e:
            import traceback
            r = {"mode_path": "real", "error": f"EXCEPTION {type(e).__name__}: {str(e)[:200]}",
                 "traceback_tail": traceback.format_exc()[-1800:]}
            print(f"[{ANCHOR}] run_real_heldout EXCEPTION: {type(e).__name__}: {str(e)[:200]}", flush=True)
        v, vmsg = verdict_real(r)
        if r.get("traceback_tail"):
            vmsg = vmsg + " | TRACEBACK_TAIL: " + r["traceback_tail"][-600:]
        path_note = "REAL bge held-out q54-q65 -- the actual V1 6th-module recapture verdict"

    metrics = {"anchor_name": ANCHOR, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "headline": vmsg,
               "alpha": ALPHA, "path": path_note,
               # STRUCTURED METRICS-PROVENANCE (shared helper; Skunkworks gate; field-check not inference)
               **provenance_fields("smoke" if is_smoke else "full", _path,
                                   "real_bge_held_out" if not is_smoke else "synthetic_harness", run_started_utc),
               "recapture_of": "PHASE_V1_6th_module_refuse_gated_retriever_YELLOW (M1 bge-cosine-tau HARD_FAIL gap-refuse>=0.95)",
               "method_delta": "refuse signal = NONLINEAR readout attention-CONCENTRATION (softmax/entmax max-weight over candidate scores) vs LINEAR scalar cosine tau (M1); readout<->readout anchor-match",
               "verify_the_referent_condition": "MEASURE present-vs-absent concentration spread + confirm a discriminating regime (in-cov concentrated, gap diffuse, separable c); else NON_TEST",
               "result": r, "elapsed_s": round(time.time() - t0, 2)}
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")

    print(f"[{ANCHOR}] run_mode={'smoke' if is_smoke else 'full'} alpha={ALPHA} -> {v}")
    print(f"  {vmsg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
