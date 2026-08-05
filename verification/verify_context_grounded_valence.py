# WIRE-DON'T-ISLAND PROMOTION WITNESS (2026-08-05). Scaffold-free, tracing=False (no HDC tracing
# used anywhere in this module -- the organ under test does not take a tracing flag).
"""verification/verify_context_grounded_valence.py -- reproduces the CERTIFIED bridge1 numbers off
the PROMOTED organ (hdlab/context_grounded_valence.py), not off the experiment cells directly. Every
item/gold-label/reader used below is IMPORTED from the certified cells (never re-authored) so this
witness cannot silently drift from the landed-VET record (notes/landed_vet_bridge1_foundation.md,
commit f06c06535).

Three checks, matching the promotion contract:
  (1) C-C original-failure payoff: core6 (4 named hard/trick collision items + 2 real-corpus
      word-sense false positives) -- the organ must get all 6 right (majority-of-3-seeds, same bar
      as the certified payoff cell) while resolve_valence_blind (old reader, reused unmodified) is
      wrong on >=4/6.
  (2) animacy-axis differential (Bopen, the open-vocab discriminator from
      exp_bridge1_event_assembly_open_vocab_v1, cert c555bdb34): the organ's real two-stage path
      must clear the pre-registered HARD_PASS band (acc>=0.75, lift over governor-only>=0.15);
      governor-only stays at chance (~0.50 by construction, no object-identity signal).
  (3) controls stay at/near chance: BOW (disjoint train/test vocab) and scrambled-animacy (permuted
      WordNet map) on the same Bopen pool.

SCALE NOTE: uses SMOKE_N_TRAIN_THETA (matches the certified cells' own self_test() scale) for
runtime; predicted_type/to_ternary (checks 1-3's actual pass/fail signal) does not depend on the
sim-theta valuation at all -- only the "valence"/"sign" numeric fields would, and this witness does
not gate on those. The FULL_N_TRAIN_THETA, 5-seed, bit-exact numbers already have an independent
off-disk recompute on record: notes/landed_vet_bridge1_foundation.md (skunkworks AUDIT-ONLY,
2026-08-05). This witness's job is to prove the PROMOTED hdlab organ reproduces the same qualitative
certified pattern, not to re-run the full landed-VET a second time.
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_DIR = os.path.join(REPO_ROOT, "experiments")
for _p in (REPO_ROOT, EXPERIMENTS_DIR, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from hdlab.context_grounded_valence import (  # noqa: E402
    score_item, score_batch, to_ternary, SMOKE_N_TRAIN_THETA,
)
import exp_bridge1_original_failure_payoff_v1 as payoff  # noqa: E402 (core6 items + old reader, reused)
import experiments.exp_bridge1_event_assembly_open_vocab_v1 as ea  # noqa: E402 (Bopen pool, reused)

SEEDS = payoff.SEEDS  # [0, 1, 2] -- same seed set the certified payoff cell used


def _gold_sign(gold_type: str) -> int:
    """Same rule as bridge1.gold_sign: only BLOCK_HIGH is harm-congruent."""
    return 1 if gold_type == "BLOCK_HIGH" else -1


# ---------------------------------------------------------------------------
# (1) C-C original-failure payoff, off the promoted organ
# ---------------------------------------------------------------------------
def check_original_failure_payoff():
    ab_items = payoff.collision_core_items() + payoff.real_corpus_fp_items()
    assert len(ab_items) == 6, f"expected 6 core items, got {len(ab_items)}"

    old_preds = [payoff.old_reader(it["action_text"]) for it in ab_items]
    old_correct = [(p == "HARM") == it["expected_harm"] for p, it in zip(old_preds, ab_items)]
    old_wrong_count = sum(1 for c in old_correct if not c)

    new_preds_per_seed = {s: [] for s in SEEDS}
    for seed in SEEDS:
        for it in ab_items:
            r = score_item(it["tokens"], it["pos"], it["target_idx"], it["target_word"],
                            seed=seed, n_train_theta=SMOKE_N_TRAIN_THETA)
            new_preds_per_seed[seed].append(to_ternary(r["predicted_type"]))

    new_correct_count = 0
    per_item = []
    for i, it in enumerate(ab_items):
        preds = [new_preds_per_seed[s][i] for s in SEEDS]
        corrects = [(p == "HARM") == it["expected_harm"] for p in preds]
        majority_correct = sum(corrects) >= 2
        new_correct_count += int(majority_correct)
        per_item.append((it["eval_id"], old_correct[i], majority_correct, preds))

    assert new_correct_count == 6, (
        f"organ core6 payoff: expected 6/6, got {new_correct_count}/6 -- {per_item}")
    assert old_wrong_count >= 4, (
        f"old reader (resolve_valence_blind) expected >=4/6 wrong (the FPs under replacement), "
        f"got {old_wrong_count}/6")
    print(f"[CHECK 1 PASS] core6 organ=6/6 old_reader_wrong={old_wrong_count}/6")
    return {"new_correct_count": new_correct_count, "old_wrong_count": old_wrong_count,
            "per_item": per_item}


# ---------------------------------------------------------------------------
# (2)+(3) animacy-axis differential + BOW/scrambled controls, off the promoted organ
# ---------------------------------------------------------------------------
def check_animacy_axis_and_controls():
    bopen_items = [it for _f, a, b in ea.SUBSET_B_OPEN_PAIRS for it in (a, b)]
    assert len(bopen_items) == 12

    real = score_batch(bopen_items, seed=0, n_train_theta=SMOKE_N_TRAIN_THETA, control="none")
    bow = score_batch(bopen_items, seed=0, n_train_theta=SMOKE_N_TRAIN_THETA, control="bow")
    scr = score_batch(bopen_items, seed=0, n_train_theta=SMOKE_N_TRAIN_THETA,
                       control="scrambled_animacy")

    def acc(results):
        return sum(1 for it, r in zip(bopen_items, results)
                    if r["sign"] == _gold_sign(it["gold_type"])) / len(bopen_items)

    def governor_only_acc(results):
        return sum(1 for it, r in zip(bopen_items, results)
                    if (1 if r["governor_type"] == "BLOCK_HIGH" else -1) == _gold_sign(it["gold_type"])
                    ) / len(bopen_items)

    acc_real = acc(real)
    acc_governor_only = governor_only_acc(real)
    acc_bow = acc(bow)
    acc_scr = acc(scr)
    lift = acc_real - acc_scr

    # per-pair flip check: within every pair, the real path's sign must differ (animate patient ->
    # BLOCK_HIGH vs inanimate patient -> NEUTRAL, governor held fixed by construction).
    flips_correct = 0
    for _form, a, b in ea.SUBSET_B_OPEN_PAIRS:
        ra = score_item(a["tokens"], a["pos"], a["target_idx"], a["target_word"], seed=0,
                         n_train_theta=SMOKE_N_TRAIN_THETA)
        rb = score_item(b["tokens"], b["pos"], b["target_idx"], b["target_word"], seed=0,
                         n_train_theta=SMOKE_N_TRAIN_THETA)
        if ra["sign"] != rb["sign"] and ra["sign"] == _gold_sign(a["gold_type"]) and \
           rb["sign"] == _gold_sign(b["gold_type"]):
            flips_correct += 1

    assert acc_real >= 0.75, f"Bopen real-path accuracy {acc_real:.3f} below the cert HARD_PASS band (>=0.75)"
    assert lift >= 0.15, f"Bopen lift over scrambled-animacy {lift:.3f} below the cert band (>=0.15)"
    assert 0.40 <= acc_governor_only <= 0.60, (
        f"governor-only Bopen accuracy {acc_governor_only:.3f} should be ~chance by construction")
    assert acc_bow <= 0.60, f"BOW control accuracy {acc_bow:.3f} above chance band (<=0.60)"
    assert acc_scr <= 0.60, f"scrambled-animacy control accuracy {acc_scr:.3f} above chance band (<=0.60)"
    assert flips_correct == len(ea.SUBSET_B_OPEN_PAIRS), (
        f"expected all {len(ea.SUBSET_B_OPEN_PAIRS)} pairs to flip harm<->neutral by animacy, "
        f"got {flips_correct}")

    print(f"[CHECK 2+3 PASS] Bopen real={acc_real:.3f} governor_only={acc_governor_only:.3f} "
          f"bow={acc_bow:.3f} scrambled={acc_scr:.3f} lift={lift:.3f} "
          f"flips_correct={flips_correct}/{len(ea.SUBSET_B_OPEN_PAIRS)}")
    return {"acc_real": acc_real, "acc_governor_only": acc_governor_only, "acc_bow": acc_bow,
            "acc_scrambled": acc_scr, "lift": lift, "flips_correct": flips_correct}


def run():
    r1 = check_original_failure_payoff()
    r2 = check_animacy_axis_and_controls()
    print("[ALL CHECKS PASS] hdlab/context_grounded_valence.py reproduces the certified "
          "bridge1 pattern (core6 C-C payoff, animacy-axis lift, chance-level controls).")
    return {"check1_original_failure_payoff": r1, "check2_animacy_axis_and_controls": r2}


if __name__ == "__main__":
    run()
