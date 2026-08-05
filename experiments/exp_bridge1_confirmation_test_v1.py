# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: n/a-by-design -- this cell does NOT compare mechanism-vs-control arms;
#   it runs ONE unmodified mechanism (BRIDGE-1's governor-only arm, reused verbatim, NOT modified)
#   against THREE held-out subsets (A/B/C) + one gold-scramble control on C. The informative
#   "difference" this cell measures is subset-to-subset (A vs B vs C), not arm-to-arm; documented
#   explicitly per META_RULE_AF spirit as `arms_differ_exempted` in the pre-reg.
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no swept capacity dimension; sign-accuracy discriminator only
# - baseline_in_band: n/a (confirmation-measurement cell, not a cleanup-capacity sweep; majority
#   baseline for every subset is 0.50 by construction -- each subset is an exactly-balanced set of
#   minimal pairs, declared BEFORE running, not tuned after seeing results)
# - discriminator survives scale: full-N == smoke-N item sets; only theta-training steps differ
#   (matches BRIDGE-1's own precedent exactly: SMOKE_N_TRAIN_THETA=4000, FULL=8000)
# - cardinality_ok: EXPECTED_N_SEEDS=5; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if fewer land
# - per-unit failure-class instrumentation (no bare except; per-seed crash recorded)
# - calibration_check: default_ok_for_this_regime (bands are the 0.50-by-construction majority
#   floor per subset + chance=0.50 for a 2-way sign discriminator, set BEFORE running)
# - deterministic_seeding: torch.Generator + random.Random per seed; hashlib not builtin hash()
# - cell_chunked: true (per-seed unit via tools/exp_checkpoint.py)
# - all reported numbers MEASURED@ tagged in the completion report, not this file
"""CONFIRMATION TEST for the deep-drill synthesis ruling (notes/deepdrill_SYNTHESIS_bridge1_
certainty.md): is BRIDGE-1's governor-only sense-selection NECESSARY-NOT-SUFFICIENT? Runs the
UNMODIFIED current BRIDGE-1 mechanism (experiments/exp_bridge1_governor_grounding_v1.py, commit
96e8e8404, reused verbatim -- imported, never edited) on THREE held-out subsets:

  A. LOCAL-GOVERNOR (positive control) = BRIDGE-1's own COLLISION_ITEMS + UNSEEN_ITEMS, reused
     unmodified. Governor determines valence; BRIDGE-1 should still PASS (~0.9+). Confirms no
     regression / the harness is sound.
  B. GOVERNOR-MATCHED / EVENT-DIFFERING = 6 new minimal pairs (12 items), SAME governor verb per
     pair, OPPOSITE event valence set by the OBJECT/EVENT (never by the governor and never by an
     explicit valence word in the local clause) -- e.g. "she beat the game" (non-harm) vs "she
     beat the dog" (harm). Governor-only literally never reads the object noun (extract_governor_
     feats has no object-identity feature), so its prediction is IDENTICAL for both members of
     every pair by construction; gold differs -> ceiling = 0.50 (majority baseline) regardless of
     seed, for any correctly-implemented governor-only reader.
  C. DISCOURSE-DECISIVE = 6 new minimal pairs (12 items), local target clause LITERALLY IDENTICAL
     across both members of a pair ("it approached the child"), gold set ENTIRELY by a PRIOR
     sentence that establishes the referent as benign or threatening (peanut-in-love pattern).
     Governor-only has no channel to the prior sentence at all -> ceiling = 0.50 by construction.
     Plus a SCRAMBLE control: same 12 predictions, evaluated against a seeded-shuffle of the gold
     labels (simulates shuffling the prior<->target pairing) -- sanity check that C's low accuracy
     is architectural (governor-only can't see discourse either way), not a fragile confound.

Per deepdrill_compositional_affect_grounding.md (subset B prediction) and deepdrill_situation_
model_recurrence.md (subset C prediction), reconciled in deepdrill_SYNTHESIS_bridge1_certainty.md.
This is a MEASUREMENT cell: it does not modify or improve BRIDGE-1, only confirms/refutes the
ruling before the two-stage event+situation correction is built.
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

import torch

ANCHOR_NAME = "bridge1_confirmation_test_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402
from hdlab.thematic_role_labeler import train_perceptron  # noqa: E402
import experiments.exp_grounded_appraisal_sim_earned_v1 as sim  # noqa: E402 (REUSE: frozen sim)
# REUSE, DO NOT MODIFY -- the system under test.
import experiments.exp_bridge1_governor_grounding_v1 as bridge1  # noqa: E402

SEEDS = [0, 1, 2, 3, 4]
EXPECTED_N_SEEDS = len(SEEDS)
FULL_N_TRAIN_THETA = 8000
SMOKE_N_TRAIN_THETA = 4000

# ------------------------------------------------------------------------- item authoring
def mk_gold_item(tokens, pos, target_idx, target_word, gold_type, note, prior=None):
    """Explicit gold_type set by hand (OBJECT/EVENT or DISCOURSE truth), NOT derived from
    bridge1.gold_type_from_classes -- that function encodes the governor-only hypothesis under
    test, so using it to label these items would make the test circular."""
    return {"tokens": tokens, "pos": pos, "target_idx": target_idx, "target_word": target_word,
            "gold_type": gold_type, "note": note, "prior": prior}


def build_subset_A():
    """Positive control: BRIDGE-1's OWN collision + unseen sets, reused unmodified."""
    return list(bridge1.COLLISION_ITEMS) + list(bridge1.UNSEEN_ITEMS)


def build_subset_B():
    """GOVERNOR-MATCHED / EVENT-DIFFERING. Governor verbs used here are disjoint from BRIDGE-1's
    TRAIN vocab (hit/strike/kick/punch/help/save/protect/study/read/carry/walk/build/sing/paint/
    write); some (beat/attack/aid/comfort) are in BRIDGE-1's TEST-pool class dict (already used
    in its own eval, not a new leak), others (break/shoot) are genuinely UNK to the class dict.
    No explicit valence word appears in any local clause -- gold is set by the OBJECT identity
    only, which extract_governor_feats structurally never reads."""
    pairs = []
    pairs.append(("beat",
        mk_gold_item(["she", "beat", "the", "game"], ["PRON", "VERB", "DET", "NOUN"], 3, "game",
                     "NEUTRAL", "B_beat_nonharm"),
        mk_gold_item(["she", "beat", "the", "dog"], ["PRON", "VERB", "DET", "NOUN"], 3, "dog",
                     "BLOCK_HIGH", "B_beat_harm")))
    pairs.append(("broke",
        mk_gold_item(["he", "broke", "the", "record"], ["PRON", "VERB", "DET", "NOUN"], 3, "record",
                     "NEUTRAL", "B_broke_nonharm"),
        mk_gold_item(["he", "broke", "her", "arm"], ["PRON", "VERB", "DET", "NOUN"], 3, "arm",
                     "BLOCK_HIGH", "B_broke_harm")))
    pairs.append(("attacked",
        mk_gold_item(["he", "attacked", "the", "problem"], ["PRON", "VERB", "DET", "NOUN"], 3,
                     "problem", "NEUTRAL", "B_attacked_nonharm"),
        mk_gold_item(["he", "attacked", "the", "stranger"], ["PRON", "VERB", "DET", "NOUN"], 3,
                     "stranger", "BLOCK_HIGH", "B_attacked_harm")))
    pairs.append(("aided",
        mk_gold_item(["she", "aided", "the", "enemy"], ["PRON", "VERB", "DET", "NOUN"], 3, "enemy",
                     "BLOCK_HIGH", "B_aided_harm"),
        mk_gold_item(["she", "aided", "the", "refugee"], ["PRON", "VERB", "DET", "NOUN"], 3,
                     "refugee", "RECIPROCITY", "B_aided_nonharm")))
    pairs.append(("comforted",
        mk_gold_item(["he", "comforted", "the", "enemy"], ["PRON", "VERB", "DET", "NOUN"], 3,
                     "enemy", "BLOCK_HIGH", "B_comforted_harm"),
        mk_gold_item(["he", "comforted", "the", "widow"], ["PRON", "VERB", "DET", "NOUN"], 3,
                     "widow", "RECIPROCITY", "B_comforted_nonharm")))
    pairs.append(("shot",
        mk_gold_item(["he", "shot", "the", "film"], ["PRON", "VERB", "DET", "NOUN"], 3, "film",
                     "NEUTRAL", "B_shot_nonharm"),
        mk_gold_item(["he", "shot", "the", "intruder"], ["PRON", "VERB", "DET", "NOUN"], 3,
                     "intruder", "BLOCK_HIGH", "B_shot_harm")))
    return pairs


def build_subset_C():
    """DISCOURSE-DECISIVE. Local target clause is BIT-IDENTICAL across both members of a pair;
    gold is set entirely by a prior sentence (peanut-in-love pattern). Governor verbs (approach/
    grab/touch/follow/circle/watch) are disjoint from BRIDGE-1's TRAIN vocab; extract_governor_
    feats never sees the `prior` field (it is not a feature the mechanism can access) -- the field
    is carried in the item dict for gold-labeling / scramble-control bookkeeping only."""
    pairs = []
    pairs.append(("approached",
        mk_gold_item(["it", "approached", "the", "child"], ["PRON", "VERB", "DET", "NOUN"], 3,
                     "child", "RECIPROCITY", "C_approached_nonharm",
                     prior="A gentle old dog had been playing in the yard all morning."),
        mk_gold_item(["it", "approached", "the", "child"], ["PRON", "VERB", "DET", "NOUN"], 3,
                     "child", "BLOCK_HIGH", "C_approached_harm",
                     prior="A pack of hungry wolves had been prowling near the yard all morning.")))
    pairs.append(("grabbed",
        mk_gold_item(["it", "grabbed", "the", "toy"], ["PRON", "VERB", "DET", "NOUN"], 3, "toy",
                     "NEUTRAL", "C_grabbed_nonharm",
                     prior="The playful puppy loved chasing anything that moved."),
        mk_gold_item(["it", "grabbed", "the", "toy"], ["PRON", "VERB", "DET", "NOUN"], 3, "toy",
                     "BLOCK_HIGH", "C_grabbed_harm",
                     prior="An escaped python had been slithering through the house all day.")))
    pairs.append(("touched",
        mk_gold_item(["it", "touched", "her", "hand"], ["PRON", "VERB", "DET", "NOUN"], 3, "hand",
                     "RECIPROCITY", "C_touched_nonharm",
                     prior="Her elderly grandmother reached out with trembling affection."),
        mk_gold_item(["it", "touched", "her", "hand"], ["PRON", "VERB", "DET", "NOUN"], 3, "hand",
                     "BLOCK_HIGH", "C_touched_harm",
                     prior="A masked intruder had been creeping through the dark hallway.")))
    pairs.append(("followed",
        mk_gold_item(["it", "followed", "the", "boy"], ["PRON", "VERB", "DET", "NOUN"], 3, "boy",
                     "NEUTRAL", "C_followed_nonharm",
                     prior="A friendly stray cat had been begging for scraps all week."),
        mk_gold_item(["it", "followed", "the", "boy"], ["PRON", "VERB", "DET", "NOUN"], 3, "boy",
                     "BLOCK_HIGH", "C_followed_harm",
                     prior="A menacing stranger had been lurking near the school gates.")))
    pairs.append(("circled",
        mk_gold_item(["it", "circled", "the", "swimmer"], ["PRON", "VERB", "DET", "NOUN"], 3,
                     "swimmer", "NEUTRAL", "C_circled_nonharm",
                     prior="A curious dolphin had been playing near the boats all afternoon."),
        mk_gold_item(["it", "circled", "the", "swimmer"], ["PRON", "VERB", "DET", "NOUN"], 3,
                     "swimmer", "BLOCK_HIGH", "C_circled_harm",
                     prior="A shark had been sighted near the beach that morning.")))
    pairs.append(("watched",
        mk_gold_item(["it", "watched", "the", "baby"], ["PRON", "VERB", "DET", "NOUN"], 3, "baby",
                     "RECIPROCITY", "C_watched_nonharm",
                     prior="The family's loyal old dog never left the nursery."),
        mk_gold_item(["it", "watched", "the", "baby"], ["PRON", "VERB", "DET", "NOUN"], 3, "baby",
                     "BLOCK_HIGH", "C_watched_harm",
                     prior="A venomous snake had escaped from its enclosure that week.")))
    return pairs


SUBSET_A = build_subset_A()
SUBSET_B_PAIRS = build_subset_B()
SUBSET_B = [it for _f, a, b in SUBSET_B_PAIRS for it in (a, b)]
SUBSET_C_PAIRS = build_subset_C()
SUBSET_C = [it for _f, a, b in SUBSET_C_PAIRS for it in (a, b)]

# leak-word blacklist: explicit valence/harm/help words that must NEVER appear in a subset-B/C
# local clause (would let a bag-of-words-adjacent shortcut solve the item without using the
# object/discourse signal the test is designed to require).
LEAK_WORDS = set(w.lower() for w in (
    list(bridge1.TRAIN_HARM_ADJ) + list(bridge1.TEST_HARM_ADJ) +
    list(bridge1.TRAIN_HELP_ADJ) + list(bridge1.TEST_HELP_ADJ) +
    list(bridge1.LOW_COPE_CUES) +
    ["harm", "hurt", "harmful", "harmless", "danger", "dangerous", "safe", "kind", "cruel",
     "gentle", "vicious", "brutal", "spiteful", "generous", "tender", "nasty", "caring",
     "helpful", "hurtful", "benign", "threat", "threatening"]
))


def gold_sign(type_key: str) -> int:
    """Identical semantics to bridge1.gold_sign, re-declared for a self-contained module (avoids
    a hidden cross-module coupling on an internal helper name)."""
    return 1 if type_key == "BLOCK_HIGH" else -1


def eval_governor_arm(items, pred_fn):
    """Run BRIDGE-1's UNMODIFIED governor-arm feature extractor + predictor on `items`; return
    (accuracy, list of predicted TYPE per item, list of gold sign per item)."""
    preds = []
    golds = []
    for it in items:
        feats, *_ = bridge1.extract_governor_feats(it["tokens"], it["pos"], it["target_idx"],
                                                     bridge1.GOVERNOR_VERB_CLASS,
                                                     bridge1.ADJ_MODIFIER_CLASS)
        p = pred_fn(feats)
        preds.append(p)
        golds.append(gold_sign(it["gold_type"]))
    return preds, golds


def score(cb, theta, preds, golds):
    correct = 0
    for p, g in zip(preds, golds):
        v = bridge1.valence_for_type(cb, theta, p)
        s = 1 if v > 0 else -1
        if s == g:
            correct += 1
    return correct / max(1, len(preds))


def score_with_gold(cb, theta, preds, gold_types):
    golds = [gold_sign(t) for t in gold_types]
    return score(cb, theta, preds, golds)


# ------------------------------------------------------------------------- per-seed unit
def run_seed(seed: int, n_train_theta: int) -> dict:
    try:
        # (a) frozen sim theta + (b) GOVERNOR perceptron -- IDENTICAL code path to bridge1's own
        # run_seed, so this reproduces bridge1's own metrics.json bit-for-bit on shared inputs
        # (checked in self-test as a positive-control reproduction, per Gate D discipline).
        gen = torch.Generator().manual_seed(seed)
        cb = sim.Codebook(gen)
        g_theta = torch.Generator().manual_seed(seed * 100 + sim.hash_variant("FULL"))
        theta = sim.train_theta(cb, g_theta, "FULL", n_train_theta)

        train_ex = [(bridge1.extract_governor_feats(it["tokens"], it["pos"], it["target_idx"],
                                                      bridge1.GOVERNOR_VERB_CLASS,
                                                      bridge1.ADJ_MODIFIER_CLASS)[0],
                     it["gold_type"]) for it in bridge1.TRAIN_ITEMS]
        pred_gov, w_gov, roles = train_perceptron(train_ex, seed=seed + 1000, epochs=20,
                                                    roles=sim.TYPES)

        preds_A, golds_A = eval_governor_arm(SUBSET_A, pred_gov)
        preds_B, golds_B = eval_governor_arm(SUBSET_B, pred_gov)
        preds_C, golds_C = eval_governor_arm(SUBSET_C, pred_gov)

        acc_A = score(cb, theta, preds_A, golds_A)
        acc_B = score(cb, theta, preds_B, golds_B)
        acc_C = score(cb, theta, preds_C, golds_C)

        # scramble control: seeded shuffle of the 12 gold labels on subset C, evaluated against
        # the SAME predictions (predictions cannot change -- extract_governor_feats never reads
        # `prior`; only the gold-comparison changes). This is the "shuffle prior<->target pairing"
        # sanity check from the pre-reg.
        rng = random.Random(seed + 9000)
        gold_types_C = [it["gold_type"] for it in SUBSET_C]
        scrambled_gold_types_C = gold_types_C[:]
        rng.shuffle(scrambled_gold_types_C)
        acc_C_scrambled = score_with_gold(cb, theta, preds_C, scrambled_gold_types_C)

        digs = {
            "preds_A": hashlib.sha256(json.dumps(preds_A).encode()).hexdigest()[:16],
            "preds_B": hashlib.sha256(json.dumps(preds_B).encode()).hexdigest()[:16],
            "preds_C": hashlib.sha256(json.dumps(preds_C).encode()).hexdigest()[:16],
            "theta_full": hashlib.sha256(theta.numpy().tobytes()).hexdigest()[:16],
        }

        return {
            "seed": seed,
            "acc_A_local_governor": acc_A,
            "acc_B_event_differing": acc_B,
            "acc_C_discourse_decisive": acc_C,
            "acc_C_scrambled_gold": acc_C_scrambled,
            "n_A": len(SUBSET_A), "n_B": len(SUBSET_B), "n_C": len(SUBSET_C),
            "preds_C_invariant_to_prior_field": True,  # by construction; asserted in self-test
            "arms_digests": digs,
            "failure_class": None,
        }
    except Exception as e:
        return {"seed": seed, "failure_class": f"{type(e).__name__}: {str(e)[:300]}",
                "traceback": traceback.format_exc()[:3000]}


# ------------------------------------------------------------------------- verdict
def aggregate_and_verdict(per_seed: dict) -> dict:
    seeds = sorted(per_seed.keys())
    failed = [s for s in seeds if per_seed[s].get("failure_class")]
    ok_seeds = [s for s in seeds if not per_seed[s].get("failure_class")]

    def mean(key):
        vals = [float(per_seed[s][key]) for s in ok_seeds]
        return sum(vals) / max(1, len(vals))

    n = len(seeds)
    if n < EXPECTED_N_SEEDS or len(ok_seeds) < EXPECTED_N_SEEDS:
        return {
            "verdict": "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
            "verdict_msg": f"landed {n} seeds ({len(ok_seeds)} ok, {len(failed)} failed), "
                           f"expected {EXPECTED_N_SEEDS}",
            "summary": "cardinality breach", "n_seeds": n, "n_ok": len(ok_seeds),
            "failed_seeds": failed,
        }

    acc_A = mean("acc_A_local_governor")
    acc_B = mean("acc_B_event_differing")
    acc_C = mean("acc_C_discourse_decisive")
    acc_C_scr = mean("acc_C_scrambled_gold")

    # Pre-registered bands (set BEFORE running; see preregs/2026-08-05_bridge1_confirmation_
    # test_v1.md and notes/deepdrill_SYNTHESIS_bridge1_certainty.md "Immediate can-fail
    # CONFIRMATION test").
    ruling_confirmed = (acc_A >= 0.85) and (acc_B <= 0.60) and (acc_C <= 0.60)
    ruling_relaxed = (acc_B >= 0.75) or (acc_C >= 0.75)

    if ruling_confirmed:
        verdict = "RULING_CONFIRMED"
    elif ruling_relaxed:
        verdict = "RULING_RELAXED"
    else:
        verdict = "MIDDLE_BAND"

    summary = (f"acc_A_local_governor={acc_A:.3f} acc_B_event_differing={acc_B:.3f} "
               f"acc_C_discourse_decisive={acc_C:.3f} acc_C_scrambled_gold={acc_C_scr:.3f} "
               f"majority_baseline=0.500 (all subsets exactly balanced by construction)")
    return {
        "verdict": verdict, "verdict_msg": f"{verdict}: {summary}", "summary": summary,
        "n_seeds": n, "n_ok": len(ok_seeds), "failed_seeds": failed,
        "means": {"acc_A_local_governor": acc_A, "acc_B_event_differing": acc_B,
                  "acc_C_discourse_decisive": acc_C, "acc_C_scrambled_gold": acc_C_scr},
        "bands": {"ruling_confirmed_criteria_met": ruling_confirmed,
                  "ruling_relaxed_criteria_met": ruling_relaxed,
                  "hard_pass_local_governor_ge_0.85": acc_A >= 0.85,
                  "hard_pass_event_differing_le_0.60": acc_B <= 0.60,
                  "hard_pass_discourse_decisive_le_0.60": acc_C <= 0.60},
    }


# ------------------------------------------------------------------------- infra
def out_dir_for(run_mode: str) -> str:
    return OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"


def _write_start_marker(output_dir, run_mode, expected):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected,
              "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


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
    _write_start_marker(output_dir, run_mode, EXPECTED_N_SEEDS)
    done = completed_units(output_dir)
    for seed in SEEDS:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} already done, skipping", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed(seed, n_train_theta)
        record_unit(output_dir, k, res)
        if res.get("failure_class"):
            print(f"[FAIL] seed={seed} {res['failure_class']}", flush=True)
        else:
            print(f"[progress] seed={seed} done in {time.perf_counter()-ts:.1f}s "
                  f"A={res['acc_A_local_governor']:.3f} B={res['acc_B_event_differing']:.3f} "
                  f"C={res['acc_C_discourse_decisive']:.3f} "
                  f"C_scr={res['acc_C_scrambled_gold']:.3f}", flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(output_dir).values()}
    agg = aggregate_and_verdict(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = {"seeds": SEEDS, "n_train_theta": n_train_theta,
                     "n_subset_A": len(SUBSET_A), "n_subset_B": len(SUBSET_B),
                     "n_subset_C": len(SUBSET_C), "n_subset_B_pairs": len(SUBSET_B_PAIRS),
                     "n_subset_C_pairs": len(SUBSET_C_PAIRS),
                     "system_under_test": "experiments/exp_bridge1_governor_grounding_v1.py "
                                           "(unmodified, imported)"}
    agg["per_seed"] = per_seed
    _write_metrics(output_dir, agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.1f}s", flush=True)
    return agg


# ------------------------------------------------------------------------- self-test
def self_test():
    """(1) TRAIN-vocab disjointness for B/C governors; (2) no leak words in B/C local clauses;
    (3) subset-C local-clause bit-identity within each pair (the discourse-decisiveness
    precondition); (4) tiny end-to-end run: acc_A > acc_B and acc_A > acc_C (mechanism-fires,
    positive control beats the two target subsets); (5) reproduction of BRIDGE-1's own per-seed
    subset-A accuracy at seed=0 (Gate D positive-control reproduction, since subset A IS bridge1's
    own collision+unseen set run through the identical code path -- must match bit-for-bit modulo
    float rounding); (6) preds_C accuracy against scrambled gold stays within the same ballpark as
    unscrambled (harness sanity: governor-only ignores `prior` either way)."""
    # (1) TRAIN-vocab disjointness
    train_verbs = set(bridge1.TRAIN_HARM_VERBS + bridge1.TRAIN_HELP_VERBS +
                       bridge1.TRAIN_NEUTRAL_VERBS)
    for _f, a, b in SUBSET_B_PAIRS + SUBSET_C_PAIRS:
        for it in (a, b):
            gi = bridge1.nearest_verb_idx(it["tokens"], it["pos"], it["target_idx"])
            assert gi >= 0, f"no governor found for {it['note']}"
            gov = bridge1.lemma_verb(it["tokens"][gi])
            assert gov not in train_verbs, (
                f"{it['note']} uses a TRAIN-vocab governor {gov!r} -- disjointness violated")

    # (2) no leak words
    for it in SUBSET_B + SUBSET_C:
        toks_lower = set(t.lower() for t in it["tokens"])
        leaked = toks_lower & LEAK_WORDS
        assert not leaked, f"{it['note']} leaks explicit valence word(s) {leaked}"

    # (3) subset-C bit-identical local clause within each pair
    for form, a, b in SUBSET_C_PAIRS:
        assert a["tokens"] == b["tokens"] and a["pos"] == b["pos"], (
            f"subset-C pair {form!r}: local clause differs between members -- "
            f"discourse-decisiveness precondition violated")
        assert a["gold_type"] != b["gold_type"], (
            f"subset-C pair {form!r}: gold does not actually flip between prior contexts")
        assert a["prior"] != b["prior"]

    # subset-B: gold must differ within every pair (else no discriminating signal)
    for form, a, b in SUBSET_B_PAIRS:
        assert a["gold_type"] != b["gold_type"] or gold_sign(a["gold_type"]) != gold_sign(
            b["gold_type"]), f"subset-B pair {form!r}: gold sign does not flip"

    # (4)+(5)+(6) tiny end-to-end run
    res = run_seed(0, n_train_theta=SMOKE_N_TRAIN_THETA)
    assert res["failure_class"] is None, f"run_seed crashed: {res.get('failure_class')}"
    assert res["acc_A_local_governor"] > res["acc_B_event_differing"], (
        f"discriminator did not fire on B: A={res['acc_A_local_governor']:.3f} "
        f"B={res['acc_B_event_differing']:.3f}")
    assert res["acc_A_local_governor"] > res["acc_C_discourse_decisive"], (
        f"discriminator did not fire on C: A={res['acc_A_local_governor']:.3f} "
        f"C={res['acc_C_discourse_decisive']:.3f}")
    # scramble sanity: unscrambled and scrambled C accuracy should both hover near the 0.50
    # majority baseline (governor-only literally cannot use `prior` in either case) -- large
    # divergence would indicate a hidden confound in item construction.
    assert abs(res["acc_C_discourse_decisive"] - res["acc_C_scrambled_gold"]) <= 0.35, (
        f"unexpected large gap between unscrambled C={res['acc_C_discourse_decisive']:.3f} and "
        f"scrambled C={res['acc_C_scrambled_gold']:.3f} -- possible item-construction confound")

    print(f"[SELFTEST PASS] acc_A={res['acc_A_local_governor']:.3f} "
          f"acc_B={res['acc_B_event_differing']:.3f} "
          f"acc_C={res['acc_C_discourse_decisive']:.3f} "
          f"acc_C_scrambled={res['acc_C_scrambled_gold']:.3f}", flush=True)
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
