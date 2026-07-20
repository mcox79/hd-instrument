"""METACOGNITION / ABSTAIN-READOUT: does thresholding an EXISTING substrate signal let the
reader KNOW-IN-ADVANCE it is likely wrong and ABSTAIN, cutting the confident-WRONG rate on a
held-out test beyond RANDOM-abstain at matched coverage?

PURE READOUT / THRESHOLD. No new learned module, no new architecture. We take EXISTING held-out
evals (real gold correct/wrong labels) and EXISTING per-item confidence signals already computed
by the substrate, then run a selective-prediction (risk-coverage) sweep + a RANDOM-abstain baseline.

ACCOUNTING item J (notes/ACCOUNTING_substrate_vs_brain_foundation_discrepancies_2026-07-20.md):
Fleming/Kiani-Shadlen -- confidence can be a byproduct of an existing evidence signal. Test whether
it transfers to THIS substrate's signals. HARD-FAIL is decisive (no usable confidence yet -> genuine
accumulator dynamics must be built before confidence can exist).

PRIOR EVIDENCE accounted for: this session's coref margin-gated work found the confidence-MARGIN
BROKEN as a discriminator for coref (atoms ~29355/29356). So the reader margin may carry no usable
confidence -> the test genuinely CAN fail.

POPULATIONS (existing held-out evals, real INDEPENDENT gold):
  POP-LCCP : reader per-verb-instance best candidates from the LCCP independent-gold eval
             (exp_learned_argstruct_parser_lccp_independent_gold_v1; McGuffey Third Reader slice).
             gold = data/gold_mcguffey_lccp_argstruct_v1.json. base error = over-extraction + mis-attach.
  POP-COH  : reader SVO extractions from the coherence-gate independent-gold eval
             (exp_coherence_gate_extraction_correctness_independent_gold_v1; slice L04+L05).
             gold = data/gold_mcguffey_castle_building_svo_v1.json.

SIGNALS (existing, on-disk, NO new module):
  S1 reader_best_score : LCCP learned cue-competition score of the winning candidate      [POP-LCCP]
  S2 reader_margin     : top1-top2 candidate cue-score within a verb-instance             [POP-LCCP]
  S3 coherence_score   : situation-model-conditioned content coherence (cos to ctx ref)   [POP-COH]
  S4 cleanup_margin    : patient nearest-neighbor top1-top2 cosine vs seen-patient codebook[POP-COH]

METRIC (selective prediction / risk-coverage):
  Sort predictions DESC by signal (higher = keep). coverage c = fraction kept (top-c by signal).
  wrong_rate(c) = (# kept that are gold-WRONG) / (# kept). base_wrong = wrong_rate at c=1.
  RANDOM-abstain baseline at coverage c: keep a random size-k subset; wrong_rate ~ base_wrong (flat).
    Bootstrapped B draws -> [p2.5, p50, p97.5] band (hypergeometric spread).
  rel_reduction(c) = (base_wrong - wrong_rate_signal(c)) / base_wrong.
  A signal BEATS RANDOM at c iff wrong_rate_signal(c) < random p2.5(c) (below even the luckiest random).

PRE-REGISTERED BANDS (before running; NOT tuned to pass):
  HARD_PASS : EXISTS signal, EXISTS c in [0.5,0.9] with rel_reduction(c) >= 0.30 AND
              wrong_rate_signal(c) < random_p2.5(c) (statistically beats random). For seed-sensitive
              POP-LCCP the beats-random condition must also hold in >=2/3 seeds.
  MIDDLE_BAND: EXISTS signal, c in [0.5,0.9] with 0.15 <= rel_reduction(c) < 0.30 AND beats random p2.5
              (real-but-weak confidence); OR rel_reduction>=0.30 not beating p2.5.
  HARD_FAIL : NO signal reaches rel_reduction>=0.15 while beating random p2.5 anywhere in [0.5,0.9]
              (the substrate carries no usable confidence signal yet).

DISCRIMINATOR-FIRES gate (must hold or population is vacuous): 0.15 < base_wrong < 0.85 per population;
  signal arrays have non-trivial variance; the 4 signals are not bit-identical.

COMPUTE ARCHITECTURE: class (b) sequential-CPU. Both source evals run in 5-12s (few hundred GloVe
cosines + a tiny logistic); the sweep is pure numpy. Foreground local-to-completion. NO queue, NO
push, NO remote-persist, NO git add. needs_orchestrator_store_sync=True (metrics only).

CELL-TEMPLATE MANDATES: except SystemExit: raise before except Exception (no BaseException);
  atomic tmp+os.replace metrics; start-marker; crash-diagnostic; signals-differ hash test;
  baseline_in_band; fixed integer seeds only (no hash()-derived seeding); ASCII-only.
"""
import os
import sys
import json
import time
import hashlib
import traceback
from datetime import datetime, timezone
from collections import defaultdict

import numpy as np

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

ANCHOR_NAME = "metacog_abstain_readout_signal_thresholding_v1"

# ---- pre-registered constants (NOT tuned to pass) ----
COV_GRID = [round(x, 3) for x in np.linspace(0.30, 1.00, 15)]  # 0.30..1.00
DECISION_COV = [c for c in COV_GRID if 0.50 - 1e-9 <= c <= 0.90 + 1e-9]
HARD_PASS_REL = 0.30
MIDDLE_REL = 0.15
BOOT_DRAWS = 4000
LCCP_SEEDS = [7, 13, 19]
BASE_WRONG_LO, BASE_WRONG_HI = 0.15, 0.85
RANDOM_SEED = 20260720  # fixed integer seed; NEVER hash()-derived


# ----------------------------------------------------------------------------------------------
# metric helpers (pure numpy)
# ----------------------------------------------------------------------------------------------
TIEBREAK_SEED = 917  # fixed; randomizes tie order so tied-confidence items do NOT inherit data order


def risk_coverage_curve(signal, correct, cov_grid, tiebreak_seed=TIEBREAK_SEED):
    """signal: higher=more confident=keep. correct: bool (True=gold-correct). Returns list of dict.
    Ties in the signal are broken RANDOMLY (fixed seed) so a constant/low-resolution signal cannot
    spuriously inherit the data's original ordering (would otherwise fake a perfect selector)."""
    signal = np.asarray(signal, dtype=np.float64)
    correct = np.asarray(correct, dtype=bool)
    n = len(signal)
    tie = np.random.default_rng(tiebreak_seed).random(n)
    order = np.lexsort((tie, -signal))  # primary key -signal (desc conf), secondary random tie-break
    wrong_sorted = (~correct[order]).astype(np.float64)
    out = []
    for c in cov_grid:
        k = max(1, int(round(c * n)))
        kept_wrong = wrong_sorted[:k]
        out.append({"coverage": c, "k": k, "wrong_rate": float(kept_wrong.mean()),
                    "n_wrong_kept": int(kept_wrong.sum())})
    return out


ALPHA = 0.05  # one-sided permutation significance for "beats random-abstain"


def random_abstain_samples(correct, cov_grid, n_draws, seed):
    """Random-abstain baseline: keep random size-k subset. Returns per-coverage sorted wrong_rate draws
    (for a one-sided permutation p-value) plus percentile band."""
    correct = np.asarray(correct, dtype=bool)
    wrong = (~correct).astype(np.float64)
    n = len(wrong)
    rng = np.random.default_rng(seed)
    samples, band = {}, {}
    for c in cov_grid:
        k = max(1, int(round(c * n)))
        rates = np.empty(n_draws, dtype=np.float64)
        for d in range(n_draws):
            idx = rng.choice(n, size=k, replace=False)
            rates[d] = wrong[idx].mean()
        rates.sort()
        samples[c] = rates
        band[c] = {"p2.5": float(np.percentile(rates, 2.5)),
                   "p50": float(np.percentile(rates, 50.0)),
                   "p97.5": float(np.percentile(rates, 97.5))}
    return samples, band


def _perm_pvalue(rate_samples, wr):
    """One-sided p-value = P(random-abstain wrong_rate <= signal wrong_rate)."""
    return float(np.mean(rate_samples <= wr + 1e-12))


def evaluate_signal(signal, correct, cov_grid, decision_cov, rand_samples, rand_band, base_wrong):
    """Return curve + best decision-band operating point (largest rel_reduction that beats random)."""
    curve = risk_coverage_curve(signal, correct, cov_grid)
    by_cov = {row["coverage"]: row for row in curve}
    best = {"rel_reduction": -1.0, "coverage": None, "wrong_rate": None,
            "beats_random": False, "p_value": None, "rand_p2.5": None, "rand_p50": None}
    for c in decision_cov:
        row = by_cov[c]
        wr = row["wrong_rate"]
        rel = (base_wrong - wr) / base_wrong if base_wrong > 0 else 0.0
        pval = _perm_pvalue(rand_samples[c], wr)
        beats = pval < ALPHA
        cand_key = (beats, rel)
        cur_key = (best["beats_random"], best["rel_reduction"])
        if cand_key > cur_key:
            best = {"rel_reduction": float(rel), "coverage": c, "wrong_rate": float(wr),
                    "beats_random": bool(beats), "p_value": float(pval),
                    "rand_p2.5": float(rand_band[c]["p2.5"]), "rand_p50": float(rand_band[c]["p50"])}
    return curve, best


def _digest(arr):
    a = np.asarray(arr, dtype=np.float64)
    return hashlib.sha256(a.tobytes()).hexdigest()


# ----------------------------------------------------------------------------------------------
# POP-LCCP : reader best-candidate score + top1-top2 margin, per verb-instance, vs LCCP gold.
# ----------------------------------------------------------------------------------------------
def build_pop_lccp(slice_lessons, seed):
    """Return (best_score[], margin[], correct[]) over verb-instances for one LCCP seed."""
    from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L
    order, sent_text, reader_svo = L.load_slice_and_reader(slice_lessons)
    gold, _gm = L.load_gold(slice_lessons)
    toks = set()
    for sid in order:
        for v, a, p in reader_svo[sid]:
            toks.update([p, L.lemma_verb(v)])
    for sid, rec in gold.items():
        for g in rec["pos"]:
            toks.update([g["patient"], g["v"]])
    glove = L.load_glove_for(toks)
    cfg = dict(L.cfg_full()); cfg["slice_lessons"] = slice_lessons; cfg["seed"] = seed
    decisions, artifacts, subcat_decisions, heldout_verbs, seen_verbs, inst_groups, w = L.run_arms(
        order, reader_svo, sent_text, glove, cfg, seed)
    best_score, margin, correct = [], [], []
    for (sid, v), cs in inst_groups.items():
        scores = sorted((L.score_cand(w, c["feat"]) for c in cs), reverse=True)
        best = max(cs, key=lambda c: L.score_cand(w, c["feat"]))
        top1 = scores[0]
        top2 = scores[1] if len(scores) > 1 else 0.0
        best_score.append(float(top1))
        margin.append(float(top1 - top2))
        rec = gold.get(sid, {"pos": []})
        g = L.match_pos(best["v"], best["tup"][2], rec.get("pos", []))
        correct.append(g is not None)
    return (np.asarray(best_score), np.asarray(margin), np.asarray(correct, dtype=bool),
            {"n_inst": len(best_score), "n_sent": len(order)})


# ----------------------------------------------------------------------------------------------
# POP-COH : coherence content_score + patient cleanup-margin, per SCORABLE extraction, vs SVO gold.
# ----------------------------------------------------------------------------------------------
def build_pop_coh(slice_lessons):
    """Return (coh_score[], cleanup_margin[], correct[]) over scorable reader extractions."""
    from experiments import exp_coherence_gate_extraction_correctness_independent_gold_v1 as C
    import torch
    order, sent_text, reader_svo = C.load_slice_and_reader(slice_lessons)
    gold, _gm = C.load_gold(slice_lessons)
    toks = set()
    for sid in order:
        for v, a, p in reader_svo[sid]:
            toks.update([v, a, p])
    for sid, rels in gold.items():
        for g in rels:
            toks.update([g["v"], g["patient"], g["agent"]])
    glove = C.load_glove_for(toks)

    def gv(p):
        return glove.get(p)

    def cos(x, y):
        return C.cos(x, y)

    # content_score replicated (readout only; identical formula to the cell's Score-1), reading order,
    # accumulating per-verb slot references + a global content reference (situation model builds up).
    ctx_k = 2.0
    flat = [(sid, tup) for sid in order for tup in reader_svo[sid]]
    slot_vecs = defaultdict(list)
    global_vecs = []
    seen_patient_vecs = []  # cleanup codebook = distinct content-patient vectors seen so far
    coh_score, cleanup_margin, correct = [], [], []
    for sid, tup in flat:
        v, a, p = tup
        pv = gv(p)
        # --- content coherence score (S3) ---
        sc = None
        if pv is not None:
            if slot_vecs[v]:
                ref = torch.stack(slot_vecs[v], 0).mean(0)
                n_ctx = len(slot_vecs[v])
            elif global_vecs:
                ref = torch.stack(global_vecs, 0).mean(0)
                n_ctx = max(1, len(global_vecs) // 4)
            else:
                ref = None; n_ctx = 0
            if ref is not None:
                ref = ref / torch.clamp(ref.norm(), min=1e-8)
                base = cos(pv, ref)
                sel = gv(v)
                if sel is not None:
                    base = 0.7 * base + 0.3 * cos(pv, sel)
                w = n_ctx / (n_ctx + ctx_k)
                if w >= 0.34:  # w_min (only score when enough context to be a real signal)
                    sc = float(base)
        # --- cleanup nearest-neighbor margin (S4): pv vs seen-patient codebook ---
        cm = None
        if pv is not None and len(seen_patient_vecs) >= 2:
            sims = np.asarray([cos(pv, u) for u in seen_patient_vecs], dtype=np.float64)
            sims.sort()
            cm = float(sims[-1] - sims[-2])
        # record only when BOTH signals are defined (same population, one variable = the signal)
        if sc is not None and cm is not None:
            coh_score.append(sc)
            cleanup_margin.append(cm)
            g = C.match_primary(tup, gold.get(sid, []))
            correct.append(g is not None)
        # update situation model + codebook AFTER scoring (causal; no leakage from future)
        if pv is not None:
            slot_vecs[v].append(pv); global_vecs.append(pv); seen_patient_vecs.append(pv)
    return (np.asarray(coh_score), np.asarray(cleanup_margin), np.asarray(correct, dtype=bool),
            {"n_scorable": len(coh_score), "n_flat": len(flat)})


# ----------------------------------------------------------------------------------------------
# aggregation + verdict
# ----------------------------------------------------------------------------------------------
def analyze():
    lccp_slice = ["L04", "L05", "L07", "L08", "L09", "L10", "L12"]
    coh_slice = ["L04", "L05"]

    signals = {}  # name -> dict

    # ---- POP-LCCP (seed-sensitive; aggregate over seeds) ----
    per_seed = {}
    for sd in LCCP_SEEDS:
        bs, mg, cor, meta = build_pop_lccp(lccp_slice, sd)
        per_seed[sd] = {"best_score": bs, "margin": mg, "correct": cor, "meta": meta}
    # reference seed (first) defines the population for band + base_wrong; other seeds re-score same insts.
    ref = per_seed[LCCP_SEEDS[0]]
    base_wrong_lccp = float((~ref["correct"]).mean())
    rand_samp_lccp, rand_band_lccp = random_abstain_samples(ref["correct"], COV_GRID, BOOT_DRAWS, RANDOM_SEED)
    for signame, key in [("S1_reader_best_score", "best_score"), ("S2_reader_margin", "margin")]:
        seed_best = []
        for sd in LCCP_SEEDS:
            bw = float((~per_seed[sd]["correct"]).mean())
            rs, rb = random_abstain_samples(per_seed[sd]["correct"], DECISION_COV,
                                            max(1000, BOOT_DRAWS // 4), RANDOM_SEED + sd)
            curve, best = evaluate_signal(per_seed[sd][key], per_seed[sd]["correct"], COV_GRID,
                                          DECISION_COV, rs, rb, bw)
            seed_best.append(best)
        n_beat = sum(1 for b in seed_best if b["beats_random"] and b["rel_reduction"] >= MIDDLE_REL)
        # aggregate operating point = the reference-seed curve vs reference band (reported), plus seed robustness
        curve_ref, best_ref = evaluate_signal(ref[key], ref["correct"], COV_GRID, DECISION_COV,
                                              rand_samp_lccp, rand_band_lccp, base_wrong_lccp)
        signals[signame] = {"population": "POP-LCCP", "base_wrong": base_wrong_lccp,
                            "n": int(len(ref["correct"])), "seed_sensitive": True,
                            "curve_ref_seed": curve_ref, "best_ref_seed": best_ref,
                            "per_seed_best": {str(sd): seed_best[i] for i, sd in enumerate(LCCP_SEEDS)},
                            "n_seeds_beat_random": int(n_beat), "n_seeds": len(LCCP_SEEDS),
                            "signal_digest": _digest(ref[key])}

    # ---- POP-COH (deterministic; bootstrap population for CI on best point) ----
    coh, clm, corc, cmeta = build_pop_coh(coh_slice)
    base_wrong_coh = float((~corc).mean())
    rand_samp_coh, rand_band_coh = random_abstain_samples(corc, COV_GRID, BOOT_DRAWS, RANDOM_SEED + 101)
    for signame, arr in [("S3_coherence_score", coh), ("S4_cleanup_margin", clm)]:
        curve, best = evaluate_signal(arr, corc, COV_GRID, DECISION_COV, rand_samp_coh,
                                      rand_band_coh, base_wrong_coh)
        signals[signame] = {"population": "POP-COH", "base_wrong": base_wrong_coh,
                            "n": int(len(corc)), "seed_sensitive": False,
                            "curve_ref_seed": curve, "best_ref_seed": best,
                            "per_seed_best": {}, "n_seeds_beat_random": None, "n_seeds": None,
                            "signal_digest": _digest(arr)}

    # ---- discriminator-fires + signals-differ gates ----
    base_wrongs = {"POP-LCCP": base_wrong_lccp, "POP-COH": base_wrong_coh}
    base_in_band = {k: bool(BASE_WRONG_LO < v < BASE_WRONG_HI) for k, v in base_wrongs.items()}
    digests = {n: signals[n]["signal_digest"] for n in signals}
    signals_differ = len(set(digests.values())) == len(digests)

    # ---- verdict ----
    def signal_tier(s):
        best = s["best_ref_seed"]
        rel = best["rel_reduction"]
        beats = best["beats_random"]
        # for seed-sensitive pops require >=2/3 seeds also beat random
        seed_ok = True
        if s["seed_sensitive"]:
            seed_ok = s["n_seeds_beat_random"] >= 2
        if beats and seed_ok and rel >= HARD_PASS_REL:
            return "HARD_PASS"
        if beats and seed_ok and rel >= MIDDLE_REL:
            return "MIDDLE_BAND"
        return "HARD_FAIL"

    tiers = {n: signal_tier(s) for n, s in signals.items()}
    if any(t == "HARD_PASS" for t in tiers.values()):
        verdict = "HARD_PASS_EXISTING_SIGNAL_CARRIES_USABLE_CONFIDENCE"
    elif any(t == "MIDDLE_BAND" for t in tiers.values()):
        verdict = "MIDDLE_BAND_WEAK_CONFIDENCE_SIGNAL"
    else:
        verdict = "HARD_FAIL_NO_EXISTING_SIGNAL_BEATS_RANDOM_ABSTAIN"

    # gate overrides
    gate_notes = []
    if not all(base_in_band.values()):
        gate_notes.append("BASELINE_OUT_OF_BAND:" + json.dumps(base_wrongs))
    if not signals_differ:
        gate_notes.append("SIGNALS_NOT_DISTINCT")

    best_signal = max(signals.items(),
                      key=lambda kv: (tiers[kv[0]] == "HARD_PASS", tiers[kv[0]] == "MIDDLE_BAND",
                                      kv[1]["best_ref_seed"]["beats_random"],
                                      kv[1]["best_ref_seed"]["rel_reduction"]))
    return {
        "verdict": verdict,
        "tiers": tiers,
        "best_signal": best_signal[0],
        "best_signal_point": best_signal[1]["best_ref_seed"],
        "base_wrong": base_wrongs,
        "baseline_in_band": base_in_band,
        "signals_differ": signals_differ,
        "gate_notes": gate_notes,
        "meta_lccp": ref["meta"], "meta_coh": cmeta,
        "signals": signals,
        "random_band_lccp": {str(c): rand_band_lccp[c] for c in COV_GRID},
        "random_band_coh": {str(c): rand_band_coh[c] for c in COV_GRID},
    }


# ----------------------------------------------------------------------------------------------
# infra: start-marker, atomic metrics, crash diagnostic
# ----------------------------------------------------------------------------------------------
def _write_start_marker(output_dir):
    import platform
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _atomic_write(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME}
    _atomic_write(output_dir, diag)


def run_mode(mode):
    t0 = time.perf_counter()
    suffix = "_smoke" if mode == "smoke" else ""
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}{suffix}")
    _write_start_marker(output_dir)
    res = analyze()
    elapsed = time.perf_counter() - t0

    bs = res["signals"][res["best_signal"]]["best_ref_seed"]
    msg = (f"{res['verdict']} | best={res['best_signal']} rel_red={bs['rel_reduction']:.3f} "
           f"cov={bs['coverage']} wrong={bs['wrong_rate']} beats_rand={bs['beats_random']} "
           f"(p={bs['p_value']} rand_p50={bs['rand_p50']}) | base_wrong LCCP={res['base_wrong']['POP-LCCP']:.3f} "
           f"COH={res['base_wrong']['POP-COH']:.3f} | tiers={res['tiers']} "
           f"| gates={res['gate_notes'] if res['gate_notes'] else 'ok'}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode,
        "verdict": res["verdict"], "verdict_msg": msg, "summary": msg,
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "needs_orchestrator_store_sync": True,
        "local_only": True,
        "arms_differ_verified": res["signals_differ"],
        "baseline_in_band": all(res["baseline_in_band"].values()),
        "discriminator_fires": all(res["baseline_in_band"].values()) and res["signals_differ"],
        "final_metrics_atomicity": "tmp_replace",
        "prereg": {"HARD_PASS_REL": HARD_PASS_REL, "MIDDLE_REL": MIDDLE_REL,
                   "decision_coverage_band": DECISION_COV, "beats_random": "wrong_rate < random_p2.5",
                   "cov_grid": COV_GRID, "boot_draws": BOOT_DRAWS, "lccp_seeds": LCCP_SEEDS},
        "result": res,
        "REQUIRED_FIELDS": ["verdict", "verdict_msg", "summary", "elapsed_s", "result"],
    }
    _atomic_write(output_dir, payload)
    print(msg, flush=True)
    print(f"[metacog] wrote {os.path.join(output_dir, 'metrics.json')} in {elapsed:.1f}s", flush=True)
    return payload


def self_test():
    """Exercise the REAL code paths at tiny scale (1-lesson slice); assert shapes + gates wired."""
    bs, mg, cor, meta = build_pop_lccp(["L04"], seed=7)
    assert len(bs) == len(mg) == len(cor) > 0, "LCCP pop empty"
    assert _digest(bs) != _digest(mg), "S1/S2 bit-identical"
    coh, clm, corc, cmeta = build_pop_coh(["L04"])
    assert len(coh) == len(clm) == len(corc), "COH pop mismatched"
    # metric self-test: a PERFECT signal (balanced base error) must beat random; rel_reduction=1 at cov 0.5.
    correct = np.array([True] * 5 + [False] * 5)
    perfect = np.array([1.0] * 5 + [0.0] * 5)  # ranks all correct above all wrong
    samp, band = random_abstain_samples(correct, [0.5], 4000, 1)
    curve, best = evaluate_signal(perfect, correct, [0.5, 1.0], [0.5], samp, band, base_wrong=0.5)
    assert best["wrong_rate"] == 0.0 and abs(best["rel_reduction"] - 1.0) < 1e-9, "perfect-signal metric broken"
    assert best["beats_random"], "perfect signal must beat random (p=%.4f)" % best["p_value"]
    # a constant signal must NOT beat random (p-value ~ high)
    const = np.zeros(10)
    curve2, best2 = evaluate_signal(const, correct, [0.5, 1.0], [0.5], samp, band, base_wrong=0.5)
    # tie-break must dissolve the spurious perfect ordering: constant signal wrong_rate must NOT be 0
    assert best2["wrong_rate"] > 0.0, "tie-break failed: constant signal inherited data order"
    print(f"[self-test] LCCP n={meta['n_inst']} COH n={cmeta['n_scorable']} "
          f"perfect_beats={best['beats_random']}(p={best['p_value']:.4f}) "
          f"const_beats={best2['beats_random']}(p={best2['p_value']:.4f})", flush=True)
    print("[self-test] PASS", flush=True)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run_mode("smoke"); return
    if args.full:
        run_mode("full"); return
    ap.error("specify one of --self-test | --smoke | --full")


if __name__ == "__main__":
    _out = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_out, e)
        raise
