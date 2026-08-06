# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: wired (score_passage, situation_type derived) vs none_arg (score_item,
#   situation_type=None) prediction-sequences on the 12 discourse-decisive target items must differ
#   (asserted below; if identical the wire never fired -- a bug, not a result).
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no swept capacity dimension; sign-accuracy discriminator only (same convention as
#   exp_bridge1_confirmation_test_v1 / exp_bridge1_twostage_event_situation_v2)
# - baseline_in_band: n/a (majority baseline is 0.500 by construction -- the 12 items are 6 exactly-
#   balanced minimal pairs where the target clause is bit-identical within each pair)
# - discriminator survives scale: full-N == smoke-N item sets (12 hand-authored discourse-decisive
#   items); only theta-training steps differ (SMOKE_N_TRAIN_THETA vs FULL_N_TRAIN_THETA), matching
#   the bridge1/v2/confirmation-test precedent exactly
# - cardinality_ok: EXPECTED_N_SEEDS=3; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if fewer land
# - per-unit failure-class instrumentation (no bare except; per-seed crash recorded)
# - calibration_check: default_ok_for_this_regime (bands are the pre-registered HARD_PASS/HARD_FAIL
#   thresholds below, set BEFORE running, matching the confirmation-test / v2 cell convention)
# - deterministic_seeding: torch.Generator + random.Random per seed; hashlib not builtin hash()
# - cell_chunked: false (single measurement unit per seed, 12 items, sub-second per seed)
# - all reported numbers MEASURED@ tagged in the completion report, not this file
"""MEASURE the production situation-bias wire (hdlab/context_grounded_valence.py score_passage +
situation_type_from_affect, commit pending this cell) against a DISCOURSE-DECISIVE item set,
mirroring exp_bridge1_twostage_event_situation_v2's subset-C design but with the situation-bias
SOURCE swapped: v2 derives situation_type via `situation_type_for_prior`, a raw-text threat/benign
lexicon scan over a free-text `prior` sentence. The production wire instead derives situation_type
via `situation_type_from_affect` over the TERNARY AFFECT (HARM/HELP/NA) of a PRIOR EVENT that this
SAME organ (hdlab/context_grounded_valence.score_item) already scored earlier in the passage -- a
production-derivable top-down signal built from the organ's own running output, not a re-scan of raw
narrative text (per notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md Step-0 VET: the source
must come from the running situation model, not raw prior-text re-scanning).

ITEM DESIGN: reuses (imports unmodified) exp_bridge1_confirmation_test_v1.SUBSET_C_PAIRS's 6 target-
clause pairs (approached/grabbed/touched/followed/circled/watched -- governor verbs disjoint from
bridge1's TRAIN vocab, local clause BIT-IDENTICAL within each pair, gold set entirely by discourse).
For each pair, builds a NEW production-derivable PRIOR EVENT (structured tokens/pos/target_idx, using
bridge1's own TRAIN/TEST HARM or HELP governor vocab -- e.g. "wolves attacked the sheep" / "a dog
rescued the kitten") in place of v2's free-text prior sentence. combine_biased_competition situation
> event > governor: the wired path (score_passage([prior_event, target])) should force the target's
sign via the prior event's own scored affect; the None-arg path (score_item(target) alone, current
production default) is architecturally blind to any prior and should sit at chance BY CONSTRUCTION
(local clause identical within each pair -> at most one member of each pair can be correct).

PRE-REGISTERED BANDS (set before running):
  HARD_PASS: discourse_decisive_wired_acc >= 0.90 AND none_arg_acc in [0.30, 0.70] (chance-banded)
             AND scramble_wired_acc <= wired_acc - 0.30 (non-vacuous collapse) AND the animacy-axis
             witness (verification/verify_context_grounded_valence.py) still passes AND full pytest
             verification/ suite is unchanged (220 passed, 3 skipped, checked OUTSIDE this cell by
             the caller/self-test harness, not re-run here for runtime cost).
  HARD_FAIL: discourse_decisive_wired_acc < 0.75, OR none_arg_acc > 0.75 (would falsify the "None-arg
             is chance by construction" architecture claim), OR scramble_wired_acc > wired_acc - 0.10
             (control doesn't collapse -- second hidden cue), OR the animacy-axis witness regresses,
             OR arms_differ_verified fails (wired == none_arg predicted-sequence, wire never fired).
  Anything else: MIDDLE_BAND.
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import random
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "situation_bias_prod_wire_discourse_decisive_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from hdlab.context_grounded_valence import (  # noqa: E402
    score_item, score_passage, situation_type_from_affect, to_ternary,
    FULL_N_TRAIN_THETA, SMOKE_N_TRAIN_THETA,
)
import experiments.exp_bridge1_confirmation_test_v1 as conf  # noqa: E402 (REUSE: subset-C target items)

SEEDS = [0, 1, 2]
EXPECTED_N_SEEDS = len(SEEDS)

# ------------------------------------------------------------------------- production-derivable priors
# Prior EVENTS: structured (tokens/pos/target_idx), scored by the SAME organ via score_item -- their
# own predicted_type's to_ternary() affect (HARM/HELP) is what situation_type_from_affect reads.
# Governor verbs are drawn from bridge1's TRAIN/TEST HARM/HELP class dict (diversified across pairs,
# disjoint from the target clauses' own governors: touch/approach/grab/follow/circle/watch). Objects
# are plain animate nouns never appearing in any event-assembly whitelist, so the prior event's own
# predicted_type is governor-dominated (event-assembly stage abstains) -- exactly like bridge1's own
# collision-item precedent.
PRIOR_EVENT_PAIRS = {
    # verbs restricted to ones whose surface -ed form round-trips correctly through hdlab.
    # thematic_role_labeler.lemma_verb's suffix-strip heuristic (silent-e verbs like shove/save/
    # rescue/soothe mis-lemmatize, e.g. "shoved" -> "shov" not "shove", landing UNK -> abstained;
    # verified empirically via self_test before locking these in).
    "approached": (
        {"tokens": ["wolves", "attacked", "the", "sheep"],
         "pos": ["NOUN", "VERB", "DET", "NOUN"], "target_idx": 3, "target_word": "sheep"},
        {"tokens": ["a", "nurse", "healed", "the", "infant"],
         "pos": ["DET", "NOUN", "VERB", "DET", "NOUN"], "target_idx": 4, "target_word": "infant"},
    ),
    "grabbed": (
        {"tokens": ["a", "man", "punched", "the", "vendor"],
         "pos": ["DET", "NOUN", "VERB", "DET", "NOUN"], "target_idx": 4, "target_word": "vendor"},
        {"tokens": ["a", "medic", "aided", "the", "villager"],
         "pos": ["DET", "NOUN", "VERB", "DET", "NOUN"], "target_idx": 4, "target_word": "villager"},
    ),
    "touched": (
        {"tokens": ["a", "raider", "stabbed", "the", "farmer"],
         "pos": ["DET", "NOUN", "VERB", "DET", "NOUN"], "target_idx": 4, "target_word": "farmer"},
        {"tokens": ["a", "guard", "comforted", "the", "orphan"],
         "pos": ["DET", "NOUN", "VERB", "DET", "NOUN"], "target_idx": 4, "target_word": "orphan"},
    ),
    "followed": (
        {"tokens": ["a", "gang", "beat", "the", "clerk"],
         "pos": ["DET", "NOUN", "VERB", "DET", "NOUN"], "target_idx": 4, "target_word": "clerk"},
        {"tokens": ["a", "doctor", "helped", "the", "patient"],
         "pos": ["DET", "NOUN", "VERB", "DET", "NOUN"], "target_idx": 4, "target_word": "patient"},
    ),
    "circled": (
        {"tokens": ["a", "thug", "kicked", "the", "waiter"],
         "pos": ["DET", "NOUN", "VERB", "DET", "NOUN"], "target_idx": 4, "target_word": "waiter"},
        {"tokens": ["a", "pilot", "protected", "the", "diver"],
         "pos": ["DET", "NOUN", "VERB", "DET", "NOUN"], "target_idx": 4, "target_word": "diver"},
    ),
    "watched": (
        {"tokens": ["a", "soldier", "struck", "the", "prisoner"],
         "pos": ["DET", "NOUN", "VERB", "DET", "NOUN"], "target_idx": 4, "target_word": "prisoner"},
        {"tokens": ["a", "nurse", "healed", "the", "baby"],
         "pos": ["DET", "NOUN", "VERB", "DET", "NOUN"], "target_idx": 4, "target_word": "baby"},
    ),
}


def build_passages():
    """Returns list of dicts: {form, harm_prior, harm_target, help_prior, help_target}. harm_target /
    help_target are conf.SUBSET_C_PAIRS's own items (imported unmodified); harm_prior / help_prior are
    this cell's production-derivable prior events (see PRIOR_EVENT_PAIRS)."""
    out = []
    for form, nonharm_item, harm_item in conf.SUBSET_C_PAIRS:
        harm_prior, help_prior = PRIOR_EVENT_PAIRS[form]
        out.append({"form": form, "harm_prior": harm_prior, "harm_target": harm_item,
                    "help_prior": help_prior, "help_target": nonharm_item})
    return out


PASSAGES = build_passages()
EXPECTED_N_PAIRS = len(conf.SUBSET_C_PAIRS)


def _scramble_pairing(passages, seed):
    """Mispairs prior<->target across the pool (seeded shuffle of the prior-event assignment) --
    same discipline as v2's SCRAMBLED_DISCOURSE control. Event stage / governor stage untouched;
    only which prior event feeds which target changes."""
    priors = []
    for p in passages:
        priors.append(p["harm_prior"])
        priors.append(p["help_prior"])
    rng = random.Random(seed + 9000)
    shuffled = priors[:]
    rng.shuffle(shuffled)
    scrambled = []
    i = 0
    for p in passages:
        scrambled.append({"form": p["form"], "target": p["harm_target"], "gold_type": p["harm_target"]["gold_type"],
                          "prior": shuffled[i]})
        i += 1
        scrambled.append({"form": p["form"], "target": p["help_target"], "gold_type": p["help_target"]["gold_type"],
                          "prior": shuffled[i]})
        i += 1
    return scrambled


def _gold_sign(gold_type: str) -> int:
    return 1 if gold_type == "BLOCK_HIGH" else -1


def run_seed(seed: int, n_train_theta: int) -> dict:
    try:
        wired_results = []
        none_arg_results = []
        for p in PASSAGES:
            for prior_key, target_key in (("harm_prior", "harm_target"), ("help_prior", "help_target")):
                prior_it = p[prior_key]
                target_it = p[target_key]
                passage_out = score_passage([prior_it, target_it], seed=seed, n_train_theta=n_train_theta)
                none_out = score_item(target_it["tokens"], target_it["pos"], target_it["target_idx"],
                                       target_it["target_word"], seed=seed, n_train_theta=n_train_theta)
                wired_results.append({"form": p["form"], "leg": prior_key, "gold_type": target_it["gold_type"],
                                       "prior_affect": to_ternary(passage_out[0]["predicted_type"]),
                                       "situation_type_in": passage_out[1]["situation_type_in"],
                                       "predicted_type": passage_out[1]["predicted_type"],
                                       "sign": passage_out[1]["sign"]})
                none_arg_results.append({"form": p["form"], "leg": prior_key, "gold_type": target_it["gold_type"],
                                          "predicted_type": none_out["predicted_type"], "sign": none_out["sign"]})

        wired_correct = sum(1 for r in wired_results if r["sign"] == _gold_sign(r["gold_type"]))
        none_arg_correct = sum(1 for r in none_arg_results if r["sign"] == _gold_sign(r["gold_type"]))
        n_items = len(wired_results)

        # scramble control: mispair priors <-> targets, re-run wired path
        scrambled = _scramble_pairing(PASSAGES, seed)
        scr_results = []
        for s in scrambled:
            passage_out = score_passage([s["prior"], s["target"]], seed=seed, n_train_theta=n_train_theta)
            scr_results.append({"form": s["form"], "gold_type": s["gold_type"],
                                 "sign": passage_out[1]["sign"]})
        scr_correct = sum(1 for r in scr_results if r["sign"] == _gold_sign(r["gold_type"]))

        # arms-must-differ: wired predicted-sequence must not be bit-identical to none_arg's.
        wired_seq = [r["predicted_type"] for r in wired_results]
        none_arg_seq = [r["predicted_type"] for r in none_arg_results]
        wired_digest = hashlib.sha256(json.dumps(wired_seq).encode()).hexdigest()[:16]
        none_arg_digest = hashlib.sha256(json.dumps(none_arg_seq).encode()).hexdigest()[:16]

        return {
            "seed": seed, "n_items": n_items,
            "wired_correct": wired_correct, "none_arg_correct": none_arg_correct,
            "scr_correct": scr_correct, "n_scr": len(scr_results),
            "wired_acc": wired_correct / n_items, "none_arg_acc": none_arg_correct / n_items,
            "scr_acc": scr_correct / len(scr_results),
            "wired_digest": wired_digest, "none_arg_digest": none_arg_digest,
            "arms_differ": wired_digest != none_arg_digest,
            "wired_results": wired_results, "none_arg_results": none_arg_results,
            "scr_results": scr_results,
            "failure_class": None,
        }
    except Exception as e:
        return {"seed": seed, "failure_class": f"{type(e).__name__}: {str(e)[:300]}",
                "traceback": traceback.format_exc()[:3000]}


def run_animacy_axis_witness():
    """Re-confirms the certified animacy-axis witness (verification/verify_context_grounded_valence.py)
    still passes unmodified -- the no-regression gate for this cell's change to hdlab/context_
    grounded_valence.py. Raises on any check failure (no silent continue)."""
    import verification.verify_context_grounded_valence as witness
    return witness.run()


def aggregate_and_verdict(per_seed: dict) -> dict:
    seeds = sorted(per_seed.keys())
    failed = [s for s in seeds if per_seed[s].get("failure_class")]
    ok_seeds = [s for s in seeds if not per_seed[s].get("failure_class")]

    if len(seeds) < EXPECTED_N_SEEDS or len(ok_seeds) < EXPECTED_N_SEEDS:
        return {"verdict": "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                "verdict_msg": f"landed {len(seeds)} seeds ({len(ok_seeds)} ok, {len(failed)} failed), "
                               f"expected {EXPECTED_N_SEEDS}",
                "summary": "cardinality breach", "n_seeds": len(seeds), "n_ok": len(ok_seeds),
                "failed_seeds": failed}

    def mean(key):
        return sum(per_seed[s][key] for s in ok_seeds) / len(ok_seeds)

    wired_acc = mean("wired_acc")
    none_arg_acc = mean("none_arg_acc")
    scr_acc = mean("scr_acc")
    arms_differ_all = all(per_seed[s]["arms_differ"] for s in ok_seeds)

    try:
        witness_result = run_animacy_axis_witness()
        animacy_axis_ok = True
        animacy_axis_err = None
    except Exception as e:
        animacy_axis_ok = False
        animacy_axis_err = f"{type(e).__name__}: {str(e)[:500]}"
        witness_result = None

    hard_fail = (wired_acc < 0.75) or (none_arg_acc > 0.75) or (scr_acc > wired_acc - 0.10) or \
        (not arms_differ_all) or (not animacy_axis_ok)
    hard_pass = (wired_acc >= 0.90) and (0.30 <= none_arg_acc <= 0.70) and \
        (scr_acc <= wired_acc - 0.30) and animacy_axis_ok and arms_differ_all

    if hard_fail:
        verdict = "HARD_FAIL"
    elif hard_pass:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    summary = (f"wired_acc={wired_acc:.3f} none_arg_acc={none_arg_acc:.3f} scr_acc={scr_acc:.3f} "
               f"arms_differ_all={arms_differ_all} animacy_axis_ok={animacy_axis_ok}")
    return {
        "verdict": verdict, "verdict_msg": f"{verdict}: {summary}", "summary": summary,
        "n_seeds": len(seeds), "n_ok": len(ok_seeds), "failed_seeds": failed,
        "means": {"wired_acc": wired_acc, "none_arg_acc": none_arg_acc, "scr_acc": scr_acc},
        "arms_differ_all": arms_differ_all,
        "animacy_axis_ok": animacy_axis_ok, "animacy_axis_err": animacy_axis_err,
        "animacy_axis_witness": witness_result,
    }


def out_dir_for(run_mode: str) -> str:
    return OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"


def _write_metrics(output_dir, d):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, default=str)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


def run(n_train_theta, run_mode):
    t0 = time.perf_counter()
    output_dir = out_dir_for(run_mode)
    per_seed = {}
    for seed in SEEDS:
        ts = time.perf_counter()
        res = run_seed(seed, n_train_theta)
        per_seed[seed] = res
        if res.get("failure_class"):
            print(f"[FAIL] seed={seed} {res['failure_class']}", flush=True)
        else:
            print(f"[progress] seed={seed} done in {time.perf_counter()-ts:.1f}s "
                  f"wired_acc={res['wired_acc']:.3f} none_arg_acc={res['none_arg_acc']:.3f} "
                  f"scr_acc={res['scr_acc']:.3f} arms_differ={res['arms_differ']}", flush=True)

    agg = aggregate_and_verdict(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = {"seeds": SEEDS, "n_train_theta": n_train_theta, "n_pairs": EXPECTED_N_PAIRS,
                     "n_items": EXPECTED_N_PAIRS * 2}
    agg["per_seed"] = per_seed
    _write_metrics(output_dir, agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.1f}s", flush=True)
    return agg


# ------------------------------------------------------------------------- self-test
def self_test():
    """Off-disk smoke: (1) build_passages() produces EXPECTED_N_PAIRS pairs, each prior event's
    OWN predicted affect matches the intended HARM/HELP direction; (2) one seed of the full
    measurement lands HARD_PASS-consistent numbers (wired beats none_arg, scramble collapses, arms
    differ); (3) the animacy-axis witness still passes (no-regression gate)."""
    passages = build_passages()
    assert len(passages) == EXPECTED_N_PAIRS, f"expected {EXPECTED_N_PAIRS} pairs, got {len(passages)}"

    for p in passages:
        harm_only = score_item(p["harm_prior"]["tokens"], p["harm_prior"]["pos"],
                                p["harm_prior"]["target_idx"], p["harm_prior"]["target_word"],
                                seed=0, n_train_theta=SMOKE_N_TRAIN_THETA)
        help_only = score_item(p["help_prior"]["tokens"], p["help_prior"]["pos"],
                                p["help_prior"]["target_idx"], p["help_prior"]["target_word"],
                                seed=0, n_train_theta=SMOKE_N_TRAIN_THETA)
        assert to_ternary(harm_only["predicted_type"]) == "HARM", (
            f"{p['form']} harm_prior did not score HARM: {harm_only}")
        assert to_ternary(help_only["predicted_type"]) == "HELP", (
            f"{p['form']} help_prior did not score HELP: {help_only}")

    res = run_seed(0, n_train_theta=SMOKE_N_TRAIN_THETA)
    assert res["failure_class"] is None, f"run_seed crashed: {res.get('failure_class')}"
    assert res["wired_acc"] >= 0.75, f"wired_acc {res['wired_acc']:.3f} below smoke floor"
    assert res["none_arg_acc"] <= 0.75, f"none_arg_acc {res['none_arg_acc']:.3f} above chance band"
    assert res["arms_differ"], "META_RULE_AF: wired and none_arg predicted-sequences are identical"
    assert res["scr_acc"] <= res["wired_acc"] - 0.10, (
        f"scramble control did not collapse: wired={res['wired_acc']:.3f} scr={res['scr_acc']:.3f}")

    witness = run_animacy_axis_witness()

    print(f"[SELFTEST PASS] n_pairs={len(passages)} wired_acc={res['wired_acc']:.3f} "
          f"none_arg_acc={res['none_arg_acc']:.3f} scr_acc={res['scr_acc']:.3f} "
          f"arms_differ={res['arms_differ']} animacy_axis_witness=OK", flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        ok = self_test()
        raise SystemExit(0 if ok else 1)
    if args.smoke:
        run(SMOKE_N_TRAIN_THETA, "smoke")
        raise SystemExit(0)
    run(FULL_N_TRAIN_THETA, "full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash(OUTPUT_DIR, e)
        raise
