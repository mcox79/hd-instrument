"""experiments/exp_reading_grounding_depth_diagnostic_v1.py

PROVE THE POINT: for the SOLVED reader (`the_reader_cannot_choose_what_to_read_next`), is the ceiling
SELECTION (which corpus to read) or the ADJACENT component GROUNDING DEPTH (turning repeated encounters
into durable knowledge)? 2026-08-28.

The comprehensible-input reader beats FROZEN + RANDOM register-controlled. But the starvation drill named
grounding DEPTH as the real long-run bottleneck (words need 6-20 coherent encounters; the loop grounds at
MIN_CONFIRM=4; no spacing). This cell MEASURES that directly, on real corpus text, with the proven CI_050
selection policy:

  (1) REACHED vs LEARNED: register-controlled probe coverage at encounter >= {1,2,4,8,16} distinct
      sentences vs GROUNDED coverage. If encounter-coverage >> grounded-coverage, the reader REACHES the
      material and the ceiling is DOWNSTREAM (grounding), not selection.
  (2) THE GROUNDING GAP: probe words ENCOUNTERED >= 4 times but NOT grounded -- reachable-and-repeated
      yet unlearned = pure grounding-depth loss.
  (3) THE DEPTH CURVE: P(grounded | encountered exactly k) for k=1..20 -- does grounding keep rising with
      more encounters (undershoot at 4), and where would it plateau?

A large REACHED>>LEARNED gap + a still-rising depth curve at k=4 PROVES the ceiling is grounding depth --
the adjacent component -- not the (solved) selection policy, and motivates the spaced-revisitation /
more-encounters fix that belongs at the reading<->grounding seam.

Reuses (no reimplementation): the CI_050 selector (choose_source) and reading machinery from
exp_reading_comprehensible_input_zpd_v1; the register-controlled probe from
exp_aimed_reading_register_controlled_v1. Fresh throwaway HDFactStore; NO hdlab/ write. ASCII-only.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import random
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.exp_reading_comprehensible_input_zpd_v1 import (ARMS, CHUNK, N_DIM, SCHEMA_THRESH,
                                                                 SEED_VOCAB_N, SUBSTRATE_SEED,
                                                                 TOKEN, choose_source, TRAVEL_TAU,
                                                                 RHO_HALFLIFE, RHO_SLOW_HALFLIFE, BETA_LEAVE,
                                                                 SEG_WINDOW, SEG_K, SEG_MIN_RUN, SEG_MAX_RUN)
from experiments.exp_information_foraging_reading_v1 import Shelf, UncertaintyMeter, load_base_vocab
from experiments.exp_aimed_reading_register_controlled_v1 import build_register_context, coverage_block
from hdlab.hd_fact_store import HDFactStore
from hdlab.information_foraging import ForagingConfig, ForagingController, SurpriseSegmenter
from hdlab.reading_grounding_loop import (KNOWN_RELATION, MEANING_RELATION, ReadingLoopState,
                                          checkpoint, content_lemmas, process_sentence, seed_known_words)

ANCHOR_NAME = os.environ.get("HDLAB_EXP_NAME", "reading_grounding_depth_diagnostic_v1")
FULL_BUDGET, SMOKE_BUDGET = 5000, 700
ENC_THRESHOLDS = [1, 2, 4, 8, 16]


def _output_dir(run_mode: str) -> str:
    base = ANCHOR_NAME[4:] if ANCHOR_NAME.startswith("exp_") else ANCHOR_NAME
    return os.path.join(REPO_ROOT, "data", f"exp_{base}" + ("_smoke" if run_mode == "smoke" else ""))


def run_diag(budget: int, run_mode: str, seed: int = 0, arm: str = "CI_050") -> dict:
    t0 = time.time()
    mode, param = ARMS[arm]
    seed_words = load_base_vocab(0, SEED_VOCAB_N)
    known_base = set(w.lower() for w in seed_words)
    store = HDFactStore(n_dim=N_DIM, seed=SUBSTRATE_SEED + seed,
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL", MEANING_RELATION: "FUNCTIONAL"},
                        use_index=True)
    state = ReadingLoopState(store=store)
    seed_known_words(state, seed_words, source="seed_base_vocabulary")
    meter = UncertaintyMeter(state)
    shelf = Shelf(run_mode, frozen=False)
    rng = random.Random(SUBSTRATE_SEED + seed)
    cfg = ForagingConfig(travel_step_duration=TRAVEL_TAU, rho_halflife_steps=RHO_HALFLIFE,
                         rho_slow_halflife_steps=RHO_SLOW_HALFLIFE, beta_leave=BETA_LEAVE,
                         stochastic=True, seed=SUBSTRATE_SEED + seed)
    ctrl = ForagingController(cfg)
    seg = SurpriseSegmenter(SEG_WINDOW, SEG_K, SEG_MIN_RUN, SEG_MAX_RUN)

    encounter: Counter = Counter()             # content lemma -> # distinct sentences it appeared in
    diag = {"n_chosen": 0, "n_fallback": 0, "choices": []}
    n_read = pass_idx = since_ckpt = 0
    prev_banked = 0
    current: Optional[str] = None

    def known_set():
        return known_base | {p["subject"] for p in state.provenance}

    while n_read < budget:
        nxt = choose_source(arm, mode, param, shelf, known_set(), rng, current, diag, None)
        if nxt != current:
            if current is not None:
                ctrl.travel()
            current = nxt
            ctrl.enter_patch(current)
        handle = shelf.handles[current]
        while n_read < budget:
            batch = handle.take(1)
            if not batch:
                break
            sentence = batch[0]
            for lem in sorted(set(content_lemmas(sentence))):
                encounter[lem] += 1
            process_sentence(state, sentence, f"{arm}_s{seed}_{n_read}", pass_idx)
            banked_now = len(state.provenance)
            gy = float(banked_now - prev_banked); prev_banked = banked_now
            ctrl.harvest(gy)
            n_read += 1; since_ckpt += 1
            if since_ckpt >= CHUNK:
                checkpoint(state, pass_idx, current, schema_thresh=SCHEMA_THRESH)
                meter.rebaseline(); pass_idx += 1; since_ckpt = 0
            if seg.observe(gy) and ctrl.should_leave():
                break
    if since_ckpt > 0:
        checkpoint(state, pass_idx, current or "final", schema_thresh=SCHEMA_THRESH)

    grounded = {p["subject"] for p in state.provenance}
    # GROUNDING QUALITY: of the (subject, object) meanings the reader DID ground, how many are
    # semantically CORRECT (WordNet-related)? A blind, mechanical check (WordNet plays no part in any
    # decision). Low quality => the 6.4% learned is partly spurious, and lowering the anchor threshold
    # to grab the 0.22-0.45 band would add MORE wrong meanings, not correct ones.
    banked_pairs = [(p["subject"], p["object"]) for p in state.provenance]
    try:
        from experiments.exp_information_foraging_reading_v1 import _wordnet_scores
        grounding_quality = _wordnet_scores(banked_pairs)
    except Exception as _e:
        grounding_quality = {"error": str(_e)[:120]}
    ctx = build_register_context(run_mode)
    probe = set(ctx["probe"])

    # (1) REACHED vs LEARNED on the register-controlled probe (balanced reachable/unreachable)
    def _bal_cov(word_set) -> float:
        r = ctx["reachable"]; u = ctx["unreachable"]
        cr = sum(1 for w in r if w in word_set) / max(1, len(r))
        cu = sum(1 for w in u if w in word_set) / max(1, len(u))
        return 0.5 * cr + 0.5 * cu
    enc_ge = {t: {w for w in probe if encounter.get(w, 0) >= t} for t in ENC_THRESHOLDS}
    reached_vs_learned = {
        "grounded_coverage": round(_bal_cov(grounded), 6),
        **{f"encounter_ge_{t}_coverage": round(_bal_cov(enc_ge[t]), 6) for t in ENC_THRESHOLDS},
    }
    # (2) THE GROUNDING GAP: probe words encountered >=4 but NOT grounded
    enc4 = enc_ge[4]
    gap_words = sorted(enc4 - grounded)
    grounding_gap = {
        "probe_encountered_ge4": len(enc4),
        "of_those_grounded": len(enc4 & grounded),
        "of_those_NOT_grounded": len(gap_words),
        "grounding_rate_on_reached_repeated": round(len(enc4 & grounded) / max(1, len(enc4)), 6),
        "example_gap_words": gap_words[:25],
    }
    # (2b) DRILL THE WALL: WHY did the 66% ungrounded-but-repeated probe words fail? Decompose by
    # failure reason -- this decides whether the fix is CONSOLIDATION (depth), EXTRACTION, or the GATE.
    items = getattr(state.library, "items", {})
    refusal_reason: Dict[str, str] = {}
    refusal_best_cos: Dict[str, float] = {}   # per-lemma MAX best_cos among its NO_ANCHOR refusals
    for r in state.refusals:
        refusal_reason.setdefault(r.get("lemma"), r.get("reason"))
        if r.get("reason") == "TAUTOLOGY_NO_ANCHOR" and r.get("best_cos") is not None:
            lem = r.get("lemma")
            refusal_best_cos[lem] = max(refusal_best_cos.get(lem, -2.0), float(r.get("best_cos")))
    fail_decomp: Counter = Counter()
    fail_examples: Dict[str, List[str]] = {}
    for w in gap_words:                                   # probe words seen >=4x, NOT grounded
        it = items.get(w)
        if it is None:
            cat = "A_never_flagged_extraction_miss"       # read >=4x but never even entered as learnable
        elif w in refusal_reason:
            cat = "B_refused_" + str(refusal_reason[w])    # the consolidation GATE rejected it (by reason)
        else:
            ntr = len(getattr(it, "traces", []) or [])
            if ntr >= 4:
                cat = "C_pending_ge4_traces_CONSOLIDATION_FAIL"  # flagged + >=4 coherent traces, still not grounded
            else:
                cat = "D_pending_lt4_traces_fragmented"    # flagged but <4 usable traces (fragmented evidence)
        fail_decomp[cat] += 1
        fail_examples.setdefault(cat, [])
        if len(fail_examples[cat]) < 12:
            fail_examples[cat].append(w)
    wall_decomposition = {"n_ungrounded_repeated": len(gap_words),
                          "by_failure_reason": dict(sorted(fail_decomp.items(), key=lambda kv: -kv[1])),
                          "examples": fail_examples}
    # DRILL THE ANCHOR WALL: for the NO_ANCHOR-refused words, how close did they get to the 0.45 anchor
    # threshold? near-miss => threshold too strict (cheap, possibly reader-adjacent fix);
    # far below => genuine no grounded anchor exists (the distributional/affective meaning-channel gap).
    THRESH = 0.45
    cos_vals = sorted(refusal_best_cos[w] for w in gap_words if w in refusal_best_cos)
    if cos_vals:
        import statistics as _st
        wall_decomposition["anchor_refusal_cosine"] = {
            "sense_match_thresh": THRESH, "n_with_best_cos": len(cos_vals),
            "median_best_cos": round(_st.median(cos_vals), 4), "max_best_cos": round(cos_vals[-1], 4),
            "min_best_cos": round(cos_vals[0], 4),
            "near_miss_0p35_to_0p45": sum(1 for c in cos_vals if 0.35 <= c < THRESH),
            "moderate_0p20_to_0p35": sum(1 for c in cos_vals if 0.20 <= c < 0.35),
            "far_below_0p20": sum(1 for c in cos_vals if c < 0.20),
            "reading": "near-miss dominant => raise recall by lowering thresh (cheap); far-below dominant "
                       "=> no grounded anchor exists => needs distributional/affective meaning channel."}
    # (3) THE DEPTH CURVE: P(grounded | encountered exactly k), all content words (not just probe)
    by_k_total: Counter = Counter()
    by_k_grounded: Counter = Counter()
    for w, k in encounter.items():
        kk = min(k, 20)
        by_k_total[kk] += 1
        if w in grounded:
            by_k_grounded[kk] += 1
    depth_curve = {str(k): {"n": by_k_total.get(k, 0),
                            "p_grounded": round(by_k_grounded.get(k, 0) / by_k_total[k], 4) if by_k_total.get(k) else None}
                   for k in range(1, 21)}

    return {
        "arm": arm, "seed": seed, "n_sentences_read": n_read, "elapsed_s": round(time.time() - t0, 2),
        "n_grounded_total": len(grounded), "n_distinct_content_words_encountered": len(encounter),
        "reached_vs_learned": reached_vs_learned,
        "grounding_quality_wordnet": grounding_quality,
        "grounding_gap": grounding_gap,
        "wall_decomposition": wall_decomposition,
        "depth_curve_p_grounded_given_k_encounters": depth_curve,
        "headline": ("REACHED(enc>=1)=%.4f vs LEARNED(grounded)=%.4f -> reached/learned ratio %.1fx; "
                     "of probe words seen >=4x, %.0f%% still UNgrounded (pure depth loss)." % (
                         reached_vs_learned["encounter_ge_1_coverage"],
                         reached_vs_learned["grounded_coverage"],
                         (reached_vs_learned["encounter_ge_1_coverage"] / reached_vs_learned["grounded_coverage"])
                         if reached_vs_learned["grounded_coverage"] > 0 else float("nan"),
                         100.0 * grounding_gap["of_those_NOT_grounded"] / max(1, grounding_gap["probe_encountered_ge4"]))),
    }


def self_test() -> dict:
    ctx = build_register_context("smoke")
    assert ctx["reachable"] and ctx["unreachable"]
    # a 1-sentence read grows the library (mechanism fires)
    store = HDFactStore(n_dim=256, seed=1,
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL", MEANING_RELATION: "FUNCTIONAL"},
                        use_index=True)
    state = ReadingLoopState(store=store)
    seed_known_words(state, ["the", "a", "is", "of", "engine"], "seed")
    process_sentence(state, "The velmara engine is of the old kind.", "st0", 0)
    assert "velmara" in state.library.items
    return {"selftest_ok": True, "n_reachable": len(ctx["reachable"]), "n_unreachable": len(ctx["unreachable"])}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["full", "smoke", "self-test"], default="full")
    ap.add_argument("--self-test", dest="selftest", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--budget", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)
    if args.selftest: args.mode = "self-test"
    elif args.smoke: args.mode = "smoke"
    if args.mode == "self-test":
        print(json.dumps(self_test(), indent=2)); print("SELF-TEST PASSED"); return 0
    run_mode = args.mode
    budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
    out = _output_dir(run_mode); os.makedirs(out, exist_ok=True)
    st = self_test()
    res = run_diag(budget, run_mode, seed=args.seed)
    metrics = {"anchor_name": ANCHOR_NAME, "run_mode": run_mode,
               "verdict": "DIAGNOSTIC", "verdict_msg": res["headline"], "summary": res["headline"],
               "ts_iso": datetime.now(timezone.utc).isoformat(), "selftest": st, "result": res}
    tmp = os.path.join(out, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, os.path.join(out, "metrics.json"))
    print(json.dumps(res, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
