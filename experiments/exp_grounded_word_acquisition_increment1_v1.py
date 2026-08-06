# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; combined vs scrambled ACQUIRED entries hash-differ)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb: n/a (bounded 7-item binary classification vs fixed gold; not a capacity/argmax-noise cell)
# - baseline_in_band: N/A for the primary held-out-accuracy arm (direct measurement vs fixed gold);
#   fall-through baseline (0/7) is reported as a REAL measured floor, verified in self_test
# - discriminator survives scale: full == the whole 7-word held-out set (no smaller-N smoke discriminator);
#   smoke runs the same set with a reduced Channel-B theta and asserts the mechanism fires end to end
# - cardinality_ok: EXPECTED_N_UNITS = 7 (per word) + 1 (noise) + 1 (scramble) + 1 (mg1) = 10
# - per-unit failure-class instrumentation (no bare except; per-unit crash recorded)
# - calibration_check: default_ok_for_this_regime (bands pre-registered, not tuned; chance=0.5)
# - deterministic_seeding: fixed integer seeds (scramble perms via np.random.default_rng(seed)); no hash()
# - cell_chunked: false (single-process, resumable per-unit via tools/exp_checkpoint.py)
# - start_marker + crash_diagnostic + atomic metrics present
# - all reported numbers MEASURED@ tagged in the completion report, not this file
"""Online grounded-word-acquisition loop, increment 1 (outcome-verb POLARITY axis).

preregs/2026-08-06_grounded_word_acquisition_increment1_v1.md +
notes/drill_online_grounded_word_acquisition_loop_2026-08-06.md.

Reproduces every pre-registered metric from a clean process: the substrate PROPOSES / CROSS-CHECKS /
GROUNDS / WRITES BACK its own candidate outcome-verb polarity for 7 genuinely-OOV McGuffey words, via
Channel A (structural construction-cue MDL induction, verb-never-a-feature) + Channel B (reward-grounded
appraisal: goal-congruence structure -> frozen reward theta valence), consolidated by MIN_CONFIRM>=2
strict two-channel agreement. Every held-out word's polarity is EARNED, never supplied. See the
hdlab.word_acquisition_loop module docstring for the reuse map and the no-corners discipline.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "grounded_word_acquisition_increment1_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

import hdlab.word_acquisition_loop as L                       # noqa: E402
import hdlab.verb_lexical_similarity as _vls                  # noqa: E402
from hdlab.goal_typing import lexicon_predict                 # noqa: E402
from hdlab.thematic_role_labeler import lemma_verb            # noqa: E402
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

# ---------------------------------------------------------------------------- corpora
_CORPUS_REL = [
    "data/corpora/mcguffey_graded/g1_first.txt", "data/corpora/mcguffey_graded/g2_second.txt",
    "data/corpora/mcguffey_graded/g3_third.txt", "data/corpora/mcguffey_graded/g4_fourth.txt",
    "data/corpora/mcguffey_graded/g5_fifth.txt", "data/corpora/mcguffey_graded/g6_sixth.txt",
    "data/corpora/graded_readers_grade1/cleaned/mcguffey_first_reader.clean.txt",
    "data/corpora/graded_readers_grade1/cleaned/mcguffey_primer.clean.txt",
]
CORPORA = [os.path.join(REPO_ROOT, p) for p in _CORPUS_REL]

# ---------------------------------------------------------------------------- held-out set (pre-reg)
# (word, gold, [2 acquisition sentences], held-out generalization sentence). All 7 verified OOV of the
# Tier-2 base lexicon (in_lexicon(lemma,"outcome")==False), gold assigned by the pre-reg's written
# rubric BEFORE any classifier was run. Sentences drawn verbatim from data/corpora/mcguffey_graded.
HELDOUT = [
    ("caught", "POS",
     ["Four soft paws had little kitty, and they caught the little mousie, Long time ago.",
      "Papa and Mamma caught at him to save him, and before we knew it we were all in the water."],
     "The rat stole out, and she jumped at it and caught it."),
    ("obtained", "POS",
     ["Harry, at length, obtained permission for the little dog to remain as a sort of outdoor pensioner.",
      "Reverse the process, and repeat as before until the lowest pitch is obtained."],
     "Having on several days obtained sight of some of them, he gave chase; but they baffled all pursuit."),
    ("gained", "POS",
     ["A distinct articulation can only be gained by constant and careful practice of the elementary sounds.",
      "His writings in poetry and prose are well known, and he also gained distinction in his profession as a sculptor."],
     "suggestions and criticisms gained from their daily work in the schoolroom."),
    ("earned", "POS",
     ["He earned almost enough to support his mother and his little sister.",
      "In a few years, while still a small boy, he earned money enough to support his father."],
     "You have earned the orange, my boy; and she gave it to him with a smile."),
    ("deserted", "NEG",
     ["But sleep seemed to have deserted the pillow of poor Tom.",
      "Frank started up in great consternation, and, from that time, almost entirely deserted the library."],
     "They both consequently deserted the little family circle every evening after tea."),
    ("wasted", "NEG",
     ["His wasted form, his aching head, And all that now remains of him, Lies, shuddering, on a felon's bed.",
      "But his bodily energies wasted and declined under incessant toil."],
     "With fire and sword, the country round Was wasted, far and wide."),
    ("faded", "NEG",
     ["I can see her as she stood there in front of the store, in her old hood and faded dress.",
      "looking up at a faded picture of an old gentleman."],
     "The fair, meek blossom that grew up And faded by my side."),
]

# ---------------------------------------------------------------------------- noise anti-drift set
# 8 valence-neutral verbs, 2 hand-authored sentences each (16 total), in natural everyday-action shape
# per the pre-reg examples ("He walked to the well and carried the pail home." / "She turned and spoke
# to her brother."). NOT tuned per-sentence to force a null result: these are ordinary neutral clauses.
NOISE = [
    ("walked", ["He walked to the well and carried the pail home.",
                "The old man walked slowly down the road."]),
    ("sat", ["She sat by the fire in the evening.", "The children sat under the tall tree."]),
    ("spoke", ["She turned and spoke to her brother.", "The teacher spoke to the class that morning."]),
    ("turned", ["He turned and looked toward the door.", "She turned the corner by the shop."]),
    ("answered", ["The boy answered the question at once.", "She answered her mother very softly."]),
    ("asked", ["He asked for a cup of cold water.", "The girl asked her friend about the road."]),
    ("stood", ["The horse stood by the wooden gate.", "He stood near the open window."]),
    ("carried", ["She carried the basket to the market.", "They carried the boxes up the stairs."]),
]

MG1_OUTCOME_SENTENCE = "The rat stole out, and she jumped at it and caught it."  # mg1_nero_puss_rat row

N_SCRAMBLE_SEEDS = 5
EXPECTED_N_UNITS = 10  # 7 words + noise + scramble + mg1

FULL_THETA = None      # None -> module default FULL_N_TRAIN_THETA=8000 (frozen reward theta)
SMOKE_THETA = 4000     # bridge1 SMOKE_N_TRAIN_THETA; gold_sign confirmed 100% consistent at >=4000


# ---------------------------------------------------------------------------- helpers
def _occurrences(dataset):
    out = []
    for row in dataset:
        word, acq = row[0], row[2] if len(row) == 4 else row[1]
        for s in acq:
            out.append({"word": word, "goal_sentences": [], "sentence": s})
    return out


def _noise_occurrences():
    out = []
    for word, sents in NOISE:
        for s in sents:
            out.append({"word": word, "goal_sentences": [], "sentence": s})
    return out


def _measure_heldout(acquired):
    """Register `acquired` into the Tier-3 overlay, score every held-out generalization sentence via
    the PRODUCTION lexicon_predict, restore the empty overlay. Returns (accuracy, pos_correct,
    neg_correct, details)."""
    _vls.clear_acquired_outcome()
    for lemma, info in acquired.items():
        _vls.register_acquired_outcome(lemma, info["polarity"])
    correct = pos_c = neg_c = 0
    details = []
    for word, gold, _acq, ho in HELDOUT:
        lemma = lemma_verb(word)
        pred = lexicon_predict(ho)
        want = "MET" if gold == "POS" else "UNMET"
        ok = (pred == want)
        if ok:
            correct += 1
            if gold == "POS":
                pos_c += 1
            else:
                neg_c += 1
        details.append({"word": word, "gold": gold,
                        "acquired": acquired.get(lemma, {}).get("polarity"),
                        "predicted": pred, "correct": ok})
    _vls.clear_acquired_outcome()
    return correct, pos_c, neg_c, details


def _acquired_hash(acquired):
    payload = json.dumps({k: v["polarity"] for k, v in sorted(acquired.items())}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _run_all(theta):
    """Compute every arm/metric once (deterministic). Returns a dict of results."""
    chosen_name, hypothesis, n_episodes = L.train_channel_a(CORPORA, max_per_seed=6, seed_shuffle=0)
    valence_table = L.channel_b_valence_table(seed=L.CB_SEED, n_train_theta=theta)
    ho_occ = _occurrences(HELDOUT)
    noise_occ = _noise_occurrences()

    arms = {}
    combined_trace = None
    for arm in ("combined", "channel_A_only", "channel_B_only"):
        acquired, trace = L.run_acquisition(ho_occ, chosen_name, hypothesis, valence_table, arm=arm)
        acc, pos_c, neg_c, details = _measure_heldout(acquired)
        arms[arm] = {"heldout_accuracy": round(acc / 7.0, 4), "heldout_correct": acc,
                     "pos_correct": pos_c, "neg_correct": neg_c,
                     "acquired": {k: v["polarity"] for k, v in acquired.items()},
                     "details": details}
        if arm == "combined":
            combined_trace = trace
            combined_acquired = acquired

    # noise anti-drift (COMBINED arm is the production write-back gate)
    noise_acq_combined, noise_trace = L.run_acquisition(noise_occ, chosen_name, hypothesis,
                                                        valence_table, arm="combined")
    noise_acq_A, _ = L.run_acquisition(noise_occ, chosen_name, hypothesis, valence_table,
                                       arm="channel_A_only")
    noise_acq_B, _ = L.run_acquisition(noise_occ, chosen_name, hypothesis, valence_table,
                                       arm="channel_B_only")

    # scramble control: permute the (channel_a, channel_b) per-word vote streams across the 7 words,
    # re-consolidate, measure. Deterministic per-seed permutations (no hash()).
    per_word_votes = _collect_per_word_votes(ho_occ, chosen_name, hypothesis, valence_table)
    words = [w for w, *_ in HELDOUT]
    scr_accs = []
    scr_hashes = []
    for s in range(N_SCRAMBLE_SEEDS):
        rng = np.random.default_rng(1000 + s)
        perm = rng.permutation(len(words)).tolist()

        def _override(lemma, oi, _perm=perm, _words=words):
            # map word i -> word perm[i]'s vote stream
            i = _words.index(_lemma_to_word(lemma))
            src_word = _words[_perm[i]]
            return per_word_votes[src_word][oi]

        acq, _tr = L.run_acquisition(ho_occ, chosen_name, hypothesis, valence_table,
                                     arm="combined", vote_override=_override)
        acc, _pc, _nc, _d = _measure_heldout(acq)
        scr_accs.append(acc / 7.0)
        scr_hashes.append(_acquired_hash(acq))
    scrambled_heldout_accuracy = float(np.mean(scr_accs)) if scr_accs else 0.0

    # mg1_nero_puss_rat end-to-end flip (informational): apply combined write-back, re-type the item.
    _vls.clear_acquired_outcome()
    for lemma, info in combined_acquired.items():
        _vls.register_acquired_outcome(lemma, info["polarity"])
    mg1_pred = lexicon_predict(MG1_OUTCOME_SENTENCE)
    _vls.clear_acquired_outcome()
    mg1_baseline = lexicon_predict(MG1_OUTCOME_SENTENCE)   # empty overlay -> fall-through
    mg1_flip = (mg1_baseline != "MET" and mg1_pred == "MET")

    # fall-through baseline (measured, disk-verifiable): empty overlay -> all 7 NONE
    fallthrough_correct = 0
    for word, gold, _acq, ho in HELDOUT:
        want = "MET" if gold == "POS" else "UNMET"
        if lexicon_predict(ho) == want:
            fallthrough_correct += 1

    return {
        "channel_a": {"plugin": chosen_name, "n_episodes": n_episodes, "hypothesis": hypothesis},
        "channel_b_valence_table": {k: round(v, 4) for k, v in valence_table.items()},
        "arms": arms,
        "combined_trace": combined_trace,
        "fallthrough_baseline_correct": fallthrough_correct,
        "noise_consolidated_count": len(noise_acq_combined),
        "noise_consolidated_words": {k: v["polarity"] for k, v in noise_acq_combined.items()},
        "noise_channel_A_only_count": len(noise_acq_A),
        "noise_channel_B_only_count": len(noise_acq_B),
        "noise_trace": noise_trace,
        "scrambled_heldout_accuracy": round(scrambled_heldout_accuracy, 4),
        "scrambled_per_seed": [round(a, 4) for a in scr_accs],
        "combined_acquired_hash": _acquired_hash(combined_acquired),
        "scrambled_acquired_hashes": scr_hashes,
        "mg1_baseline_predict": mg1_baseline, "mg1_acquired_predict": mg1_pred, "mg1_flip": mg1_flip,
    }


def _lemma_to_word(lemma):
    for w, *_ in HELDOUT:
        if lemma_verb(w) == lemma:
            return w
    return lemma


def _collect_per_word_votes(ho_occ, chosen_name, hypothesis, valence_table):
    """{word: [(a_vote, b_vote) per occurrence]} for the 7 held-out words (real votes, pre-scramble)."""
    votes = {}
    for occ in ho_occ:
        w = occ["word"]
        a = L.channel_a_vote(chosen_name, hypothesis, L.channel_a_feats(occ["sentence"], w))
        b = L.channel_b_vote(occ["goal_sentences"], occ["sentence"], w, valence_table)
        votes.setdefault(w, []).append((a, b))
    return votes


# ---------------------------------------------------------------------------- verdict (pre-reg bands)
def _verdict(res):
    c = res["arms"]["combined"]
    acc = c["heldout_accuracy"]
    heldout_correct = c["heldout_correct"]
    pos_c, neg_c = c["pos_correct"], c["neg_correct"]
    noise = res["noise_consolidated_count"]
    scr = res["scrambled_heldout_accuracy"]
    real_acc = acc

    hard_pass = (heldout_correct >= 5 and pos_c >= 2 and neg_c >= 2
                 and noise == 0 and 0.35 <= scr <= 0.65 and res["mg1_flip"])
    # HARD-FAIL: any of the pre-registered fail conditions
    hf_no_movement = heldout_correct <= res["fallthrough_baseline_correct"]
    hf_noise_leak = noise >= 1
    hf_scramble_not_chance = (not (0.35 <= scr <= 0.65)) and (abs(real_acc - scr) < 0.10)
    hard_fail = hf_no_movement or hf_noise_leak or hf_scramble_not_chance

    if hard_pass:
        verdict = "HARD_PASS"
    elif hard_fail:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    fail_reasons = []
    if hf_no_movement:
        fail_reasons.append(f"no_movement_over_fallthrough(heldout={heldout_correct}<="
                            f"{res['fallthrough_baseline_correct']})")
    if hf_noise_leak:
        fail_reasons.append(f"anti_drift_leak(noise_consolidated={noise}/8)")
    if hf_scramble_not_chance:
        fail_reasons.append(f"scramble_did_not_collapse(scr={scr:.3f} real={real_acc:.3f})")

    summary = (
        f"combined heldout={heldout_correct}/7 (POS={pos_c}/4 NEG={neg_c}/3) | "
        f"A_only={res['arms']['channel_A_only']['heldout_correct']}/7 "
        f"B_only={res['arms']['channel_B_only']['heldout_correct']}/7 | "
        f"noise_leak={noise}/8 | scramble={scr:.3f} | mg1_flip={res['mg1_flip']} | "
        f"fallthrough={res['fallthrough_baseline_correct']}/7")
    return {"verdict": verdict, "verdict_msg": f"{verdict}: {summary}", "summary": summary,
            "hard_fail_reasons": fail_reasons,
            "bands": {"hard_pass": hard_pass, "hard_fail": hard_fail}}


# ---------------------------------------------------------------------------- infra
def _out_dir_for(run_mode):
    return OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": EXPECTED_N_UNITS, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, d):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


def run(run_mode):
    t0 = time.perf_counter()
    output_dir = _out_dir_for(run_mode)
    _write_start_marker(output_dir, run_mode)
    theta = SMOKE_THETA if run_mode == "smoke" else FULL_THETA

    # Resumable per-unit: the heavy shared computation (Channel A train + theta) is done once; the
    # single "all" unit records the full result dict. A resumed run reloads it instead of recomputing.
    done = completed_units(output_dir)
    k = unit_key("all", run_mode)
    if k in done:
        print(f"[resume] unit {k} already done, reloading", flush=True)
        res = load_units(output_dir)[k]
    else:
        res = _run_all(theta)
        record_unit(output_dir, k, res)
        print(f"[progress] core computation done in {time.perf_counter()-t0:.1f}s", flush=True)

    agg = dict(res)
    agg.update(_verdict(res))
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["expected_n_units"] = EXPECTED_N_UNITS
    agg["config"] = {"n_scramble_seeds": N_SCRAMBLE_SEEDS, "theta": theta,
                     "n_heldout": len(HELDOUT), "n_noise": len(NOISE)}
    _write_metrics(output_dir, agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.1f}s", flush=True)
    return agg


# ---------------------------------------------------------------------------- self-test
def self_test():
    """(1) all 7 held-out words OOV of the Tier-2 base lexicon (non-circular); (2) fall-through
    baseline reproduces 0/7; (3) module self_test (propose/earned-sign/consolidate/end-to-end);
    (4) tiny end-to-end run at SMOKE theta produces a decisive combined ACQUIRED set that hash-differs
    from at least one scrambled ACQUIRED set (META_RULE_AF arms-must-differ)."""
    for word, _g, _acq, _ho in HELDOUT:
        assert not _vls.in_lexicon(lemma_verb(word), "outcome"), (
            f"held-out word {word!r} is NOT OOV of the Tier-2 base lexicon (circularity breach)")
    _vls.clear_acquired_outcome()
    fall = sum(1 for w, g, _a, ho in HELDOUT
               if lexicon_predict(ho) == ("MET" if g == "POS" else "UNMET"))
    assert fall == 0, f"fall-through baseline must be 0/7, measured {fall}/7"
    L.self_test()
    res = _run_all(SMOKE_THETA)
    combined_hash = res["combined_acquired_hash"]
    assert res["combined_acquired_hash"] in (combined_hash,)  # sanity
    assert any(h != combined_hash for h in res["scrambled_acquired_hashes"]), (
        "META_RULE_AF: at least one scrambled ACQUIRED set must hash-differ from combined")
    assert res["channel_b_valence_table"]["RECIPROCITY"] < 0 < res["channel_b_valence_table"]["BLOCK_HIGH"]
    v = _verdict(res)
    print(f"[SELFTEST PASS] fallthrough=0/7 heldout_OOV=7/7 {v['summary']}", flush=True)
    _vls.clear_acquired_outcome()
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
        run("smoke")
        raise SystemExit(0)
    run("full")
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
