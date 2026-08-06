# WIRE-DON'T-ISLAND PROMOTION WITNESS (2026-08-05). Scaffold-free, tracing=False (no HDC tracing
# used anywhere in this module -- the organ under test does not take a tracing flag).
"""verification/verify_goal_typing.py -- reproduces the end-to-end GOAL-typing numbers off the
PROMOTED organ (hdlab/goal_typing.py), not off the experiment cells directly. Every bank item / gold
label / probe used below is IMPORTED from the certified cells (never re-authored) so this witness
cannot silently drift from the landed record
(data/exp_c5_desiderative_aspectual_partition_goal_typing_v1/metrics.json, commit 5da76bf34).

Three checks, matching the promotion contract:
  (1) explicit_psych: on the recency-trap divergent subset of experiments/data/goal_owner_fair_v1.jsonl
      (N=18), owner-selection accuracy must be 18/18 (1.0) across all 3 seeds, using the PROMOTED
      hdlab.goal_typing.type_goal_events as the typer plugged into the real end-to-end harness
      (real coref resolver + directed-score adoption gate, reused bit-identical from
      experiments/exp_c5_real_coref_endtoend_purpose_infinitival_v1.py).
  (2) action_implied: same harness, N=10 divergent, must be 10/10 (1.0) across all 3 seeds.
  (3) aspectual precision probe (the 7-item hand-authored bank from
      experiments/exp_c5_desiderative_aspectual_partition_goal_typing_v1.py, imported not
      re-authored): the promoted organ must fire GOAL on 0/7 items, all 3 seeds (precision guard --
      "began/started/tried/failed/managed/ceased/continued to VP" must NOT read as goal-ownership).

SCALE NOTE: this witness re-runs the SAME 3-seed, full-bank scale as the certified cell (not a
reduced smoke) because the discriminator (owner-selection accuracy on a small hand-authored bank) is
cheap -- no HDC dimensionality/vector-count scaling involved, so there is no smoke-vs-full gap to
bridge (contrast the FHRR-dimension-scale HDC organs elsewhere in verification/, which DO need a
reduced scale for CI runtime).
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_DIR = os.path.join(REPO_ROOT, "experiments")
for _p in (REPO_ROOT, EXPERIMENTS_DIR, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from hdlab.goal_typing import type_goal_events, has_goal, R_GOAL  # noqa: E402
from hdlab.goal_owner_select import directed_goal_outcome_score  # noqa: E402
from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT  # noqa: E402

# ---- REUSED (imported, not re-authored): the real end-to-end harness's generic helpers ----------
import exp_c5_real_coref_endtoend_purpose_infinitival_v1 as PREVMOD  # noqa: E402
# ---- REUSED (imported, not re-authored): the aspectual precision probe bank ----------------------
import exp_c5_desiderative_aspectual_partition_goal_typing_v1 as DESID  # noqa: E402

SEEDS = PREVMOD.SEEDS  # [0, 1, 2] -- same seed set the certified desiderative cell used


def _promoted_typer(sentence: str, subject):
    """The typer callable, backed entirely by the PROMOTED hdlab.goal_typing organ (all three
    signals: EXPERIENCER-frame + purpose-infinitival + desiderative/aspectual partition)."""
    return type_goal_events(sentence, subject)


def run_item_promoted(item: dict, seed: int) -> dict:
    """Byte-identical logic to exp_c5_desiderative_aspectual_partition_goal_typing_v1.run_item_typer
    / exp_c5_real_coref_endtoend_purpose_infinitival_v1.run_item, with the typer swapped for the
    PROMOTED organ. Reuses PREVMOD's generic (typer-independent) helpers throughout."""
    gold = item["gold_outcome_owner"]
    foil = item.get("foil")

    baseline_owner = PREVMOD.resolve_outcome_recency_positional(item)
    role_seq_b, cluster_ids_b = PREVMOD.build_role_seq(item, baseline_owner, _promoted_typer)
    outcome_pos = PREVMOD._outcome_pos(role_seq_b)

    coref_owner = PREVMOD.resolve_outcome_coref(item)
    role_seq_c, cluster_ids_c = PREVMOD.build_role_seq(item, coref_owner, _promoted_typer)
    assert role_seq_b == role_seq_c, (
        f"{item['id']}: role attribution must be resolver-independent: {role_seq_b} vs {role_seq_c}")

    goal_present = R_GOAL in role_seq_b
    row = dict(id=item["id"], gold=gold, goal_present=goal_present,
               baseline_matches_gold=(baseline_owner == gold))

    if outcome_pos is None:
        row.update(final_owner=None, matches_gold=False)
        return row

    score_b = directed_goal_outcome_score(role_seq_b, cluster_ids_b, seed, outcome_pos)
    score_c = directed_goal_outcome_score(role_seq_c, cluster_ids_c, seed, outcome_pos)
    adopt = decide_keep_or_revert({"content": score_c - score_b}, ABSTAIN_BAND_DEFAULT)
    final_owner = cluster_ids_c[outcome_pos] if adopt == "content" else cluster_ids_b[outcome_pos]
    row.update(final_owner=final_owner, matches_gold=(final_owner == gold))
    return row


# ---------------------------------------------------------------------------
# (1)+(2) explicit_psych 18/18 and action_implied 10/10, off the promoted organ
# ---------------------------------------------------------------------------
def check_end_to_end_subset(verb_type: str, expected_n_divergent: int):
    core, _twins = PREVMOD.load_bank(verb_type)
    for seed in SEEDS:
        rows = [run_item_promoted(it, seed) for it in core]
        div = [r for r in rows if not r["baseline_matches_gold"]]
        assert len(div) == expected_n_divergent, (
            f"{verb_type} seed={seed}: expected N_divergent={expected_n_divergent}, "
            f"got {len(div)}")
        acc = sum(r["matches_gold"] for r in div) / len(div)
        assert acc == 1.0, (
            f"{verb_type} seed={seed}: promoted-organ owner-selection accuracy {acc} != 1.0 "
            f"(misses: {[r['id'] for r in div if not r['matches_gold']]})")
    print(f"[CHECK {verb_type}] N_divergent={expected_n_divergent} accuracy=1.0 all {len(SEEDS)} seeds "
          f"(promoted hdlab.goal_typing organ)")
    return {"verb_type": verb_type, "n_divergent": expected_n_divergent, "accuracy_all_seeds": 1.0}


# ---------------------------------------------------------------------------
# (3) aspectual precision probe: 0/7 false GOALs, all seeds
# ---------------------------------------------------------------------------
# p03_ivy_crate_foil_kay ("Ivy tried to lift the crate.") was RECLASSIFIED 2026-08-06 by the
# goal-recognition coverage expansion: `try` moved from ASPECTUAL_STOP to the new CONATIVE_PASS
# class (Talmy 1988 force-dynamics -- an attempt IS a goal signal, recognized even when it fails),
# so this item now CORRECTLY fires GOAL. The remaining 6 items are genuinely aspectual/implicative
# (began/started/failed/managed/ceased/continued to VP) and must still fire 0 GOAL -- that precision
# guard is unchanged. See preregs/2026-08-06_goal_recognition_coverage_expansion_v1.md.
CONATIVE_RECLASSIFIED_IDS = {"p03_ivy_crate_foil_kay"}


def check_aspectual_precision_probe():
    probe = DESID.ASPECTUAL_PRECISION_PROBE
    assert len(probe) == 7, f"expected the certified 7-item probe bank, got {len(probe)}"
    aspectual = [it for it in probe if it["id"] not in CONATIVE_RECLASSIFIED_IDS]
    conative = [it for it in probe if it["id"] in CONATIVE_RECLASSIFIED_IDS]
    assert len(aspectual) == 6 and len(conative) == 1, (
        f"expected 6 genuinely-aspectual + 1 reclassified-conative, got {len(aspectual)}/{len(conative)}")
    max_false_goal = 0
    for seed in SEEDS:
        # (a) the 6 genuinely-aspectual items must STILL fire 0 GOAL (precision guard, unchanged)
        asp_rows = [run_item_promoted(it, seed) for it in aspectual]
        false_goal_count = sum(1 for r in asp_rows if r["goal_present"])
        max_false_goal = max(max_false_goal, false_goal_count)
        assert false_goal_count == 0, (
            f"seed={seed}: promoted organ fired GOAL on {false_goal_count}/6 genuinely-aspectual "
            f"probe items: {[r['id'] for r in asp_rows if r['goal_present']]}")
        # (b) the reclassified conative item ("tried to VP") must NOW fire GOAL (the coverage fix)
        con_rows = [run_item_promoted(it, seed) for it in conative]
        assert all(r["goal_present"] for r in con_rows), (
            f"seed={seed}: reclassified conative 'tried to VP' item must NOW fire GOAL: "
            f"{[r['id'] for r in con_rows if not r['goal_present']]}")
    # sentence-level convenience-wrapper check too (has_goal), seed-independent
    for it in aspectual:
        sentence = PREVMOD._sentences(it["text"])[0]
        assert has_goal(sentence, it["owner"]) is False, (
            f"{it['id']}: has_goal() must be False on a genuinely-aspectual sentence")
    for it in conative:
        sentence = PREVMOD._sentences(it["text"])[0]
        assert has_goal(sentence, it["owner"]) is True, (
            f"{it['id']}: has_goal() must be True on a reclassified conative 'tried to VP' sentence")
    print(f"[CHECK aspectual_precision_probe] N_aspectual=6 false_goal_count(max over seeds)="
          f"{max_false_goal} clean=True; N_conative_reclassified=1 fires_GOAL=True "
          f"(promoted hdlab.goal_typing organ, 2026-08-06 coverage expansion)")
    return {"n_aspectual": 6, "false_goal_count_max": max_false_goal, "clean": True,
            "n_conative_reclassified": 1, "conative_fires_goal": True}


def run():
    r1 = check_end_to_end_subset("explicit_psych", expected_n_divergent=18)
    r2 = check_end_to_end_subset("action_implied", expected_n_divergent=10)
    r3 = check_aspectual_precision_probe()
    print("[ALL CHECKS PASS] hdlab/goal_typing.py reproduces the certified end-to-end pattern "
          "(explicit_psych 18/18, action_implied 10/10, clean aspectual precision probe).")
    return {"check1_explicit_psych": r1, "check2_action_implied": r2,
            "check3_aspectual_precision_probe": r3}


if __name__ == "__main__":
    run()
