"""exp_c5_generative_goal_typing_action_frame_v1 -- GENERATIVE goal-typing: infer a GOAL from an
ACTION frame (telos), not just from an explicit psych/desiderative verb.

PRE-REG: preregs/2026-08-05_c5_generative_goal_typing_action_frame_v1.md

WHY (task brief, gating deliverable): notes/drill_brain_goal_owner_flow.md +
notes/DRILL_SYNTHESIS_goal_owner_brain_and_fairness.md diagnosed goal-typing as LEXICALLY GATED (a
psych/desiderative verb -> GOAL) where the brain GENERATIVELY infers a goal from an action sequence
with no goal-word (Trabasso goal-plans; TPJ/dmPFC mentalizing). The fair instrument
`experiments/data/goal_owner_fair_v1.jsonl` (trap_type=="recency" subset scored by
`exp_c5_fair_goal_owner_v1.py`) has 10 `verb_type=="action_implied"` core items with NO goal-word;
that cell's OWN self-test (#5) asserts ALL of them miss GOAL typing under the current lexicon typer --
an honest, pre-existing, documented gap, not a bug. This cell is the fix + measurement.

Prior-work check (SUBSTRATE-KB, mandatory before authoring):
`tools/substrate_query.sh "generative goal inference action frame purpose infinitive telos goal typing
without desiderative verb"` returned top cosine=0.3516, a theory note about active-inference/
free-energy framing (notes/research_drill_substrate_structured_prediction_2x_2026-06-11.md) -- a
tangential theoretical pointer, NOT a prior implementation of action-frame->goal typing. Not a
rediscovery.

MECHANISM (glass-box, generative, verb-lemma-INDEPENDENT -- the point of the exercise): the ACTION
FRAME that implies a goal is the purpose-infinitival construction "X V ... to VP" (X does an action IN
ORDER TO do something else = X has that something-else as a goal), a general English syntactic
construction, not tied to any specific matrix verb. `action_frame_feats()` below detects it
STRUCTURALLY: a "to" token immediately followed by a token that is NOT a determiner/possessive is an
infinitival complement ("to fetch water"), not a prepositional NP complement ("to the well" -- "the" is
a determiner). This feature never inspects the matrix verb's identity, so it generalizes to any
action-frame verb, not a fixed lexicon (contrast with the OLD lexicon typer's V2_DESIRE word-list,
which is closed and verb-specific).

hdlab/learner (config-only MDL plugin registry -- the SAME reuse pattern as the OOV frame-induction
fix) INDUCES the rule from a small hand-authored FIT set via the `ruleind` plugin (MDL-gated
sequential-covering conjunction search, reused bit-identical): the mechanism is EARNED via MDL
model-selection over declared structural features, not hand-written as an if-statement. FIT-set main
verbs are DISJOINT from the TEST bank's action_implied main verbs -- asserted programmatically
(held-out generalization, not memorization).

WIRE POINT (reuse, not rebuild): the induced typer is spliced in by monkeypatching the single name
`exp_component5_gold_role_isolated_v1.type_sentence_events` -- the module-global that the reused
`build_positions()` function calls at runtime -- inside a context manager. `exp_c5_fair_goal_owner_v1.
run_seed()` and every organ it calls (GeneralRecencyEntityResolver, ContentMatchResolver,
directed_goal_outcome_score, decide_keep_or_revert, the recency/majority/ceiling baselines, the
scramble control) run BIT-IDENTICAL to the fair cell with only the typer swapped. Zero
re-implementation of the scoring harness.

Cites: notes/drill_brain_goal_owner_flow.md; notes/DRILL_SYNTHESIS_goal_owner_brain_and_fairness.md;
experiments/exp_c5_fair_goal_owner_v1.py; hdlab/learner/; hdlab/goal_owner_select.py;
hdlab/self_improving_loop.py.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from contextlib import contextmanager
from datetime import datetime, timezone

ANCHOR_NAME = "c5_generative_goal_typing_action_frame_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

# ---- REUSED BIT-IDENTICAL: the fair instrument harness (baselines, scoring, scramble, gates) ----
import exp_c5_fair_goal_owner_v1 as FAIRMOD  # noqa: E402
# ---- REUSED BIT-IDENTICAL: the module whose global `type_sentence_events` name we splice ----------
import exp_component5_gold_role_isolated_v1 as C5MOD  # noqa: E402
from exp_situation_model_goal_outcome_dimension_v1 import (  # noqa: E402
    R_GOAL, _ordered_tokens,
)
# ---- REUSED BIT-IDENTICAL: config-only MDL plugin registry (the OOV frame-induction reuse pattern) -
from hdlab.learner import apply as learner_apply, learn as learner_learn  # noqa: E402
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

SEEDS = [0, 1, 2]
EXPECTED_N_SEEDS = len(SEEDS)
CONDITIONS = ["lexical_only", "generative"]

# ============================================================================ ACTION-FRAME FEATURES
# Purely STRUCTURAL (verb-lemma-independent): "to VP" (infinitival purpose clause) vs "to NP"
# (prepositional complement), distinguished by whether the token after "to" is a determiner/possessive.
DET_STOP = {
    "the", "a", "an", "his", "her", "its", "their", "this", "that", "my", "your", "our", "to",
}
DIRECTIONAL_PP = {"toward", "towards", "into", "up", "down", "out", "across", "off", "along"}
# CONTROL-VERB exclusion: "to VP" immediately after a control verb (fail/try/manage/want/wish/...)
# is an ARGUMENT-COMPLEMENT of that verb (attempt/desire/enablement semantics, already covered by
# the lexicon typer where relevant, or negation-of-attempt on an OUTCOME clause), NOT the
# adjunct purpose-of-motion construction ("V(motion) ... to VP") this feature targets. Excluding
# these keeps the feature scoped to the genuine telos-of-action reading and prevents it firing
# inside an outcome clause like "failed to gain the pass" (which would spuriously self-attribute a
# GOAL to whichever entity that outcome clause's own subject resolves to).
CONTROL_VERB_STOP = {
    "fail", "fails", "failed", "try", "tries", "tried", "manage", "manages", "managed",
    "begin", "begins", "began", "start", "starts", "started", "decide", "decides", "decided",
    "want", "wants", "wanted", "wish", "wishes", "wished", "hope", "hopes", "hoped",
    "long", "longs", "longed", "need", "needs", "needed", "seem", "seems", "seemed",
    "get", "gets", "got", "choose", "chooses", "chose",
}


def action_frame_feats(sentence: str):
    """Frame-general features over an action clause. Never inspects the matrix verb's identity --
    only the STRUCTURAL position of 'to' relative to a determiner (infinitive vs PP-complement) and
    relative to a control-verb stoplist (adjunct purpose-clause vs argument-complement)."""
    toks = _ordered_tokens(sentence)
    feats = []
    has_purpose_inf = False
    for i in range(len(toks) - 1):
        if toks[i] != "to" or toks[i + 1] in DET_STOP:
            continue
        preceding = toks[i - 1] if i > 0 else None
        if preceding in CONTROL_VERB_STOP:
            continue
        has_purpose_inf = True
        break
    if has_purpose_inf:
        feats.append("purpose_to_no_det")
    if any(w in toks for w in DIRECTIONAL_PP):
        feats.append("has_directional_pp")
    return feats


# ============================================================================ FIT SET (held-out verbs)
# Main verbs used here (ran, hurried, marched, sailed, drove, hiked, sprinted, journeyed) are
# DISJOINT from the TEST bank's action_implied main verbs (set [out], climbed, carried, walked,
# rowed) -- asserted in self-test. This is genuine held-out generalization, not memorization.
FIT_POS_SENTENCES = [
    "Nell ran to the well to fetch water before noon.",
    "Owen hurried to the barn to feed the horses.",
    "Priya marched to the hall to deliver the letter.",
    "Quinn sailed to the island to trade the goods.",
    "Rex drove to the mill to collect the flour.",
    "Sara hiked to the peak to plant the flag.",
    "Theo sprinted to the gate to open the lock.",
    "Uma journeyed to the town to sell the cloth.",
]
FIT_NEG_SENTENCES = [
    "Nell ran to the well early in the morning.",
    "Owen hurried to the barn before the storm.",
    "Priya marched to the hall with the others.",
    "Quinn sailed to the island near the coast.",
    "Rex drove to the mill along the river.",
    "Sara hiked to the peak under the stars.",
    "Theo sprinted to the gate at dawn.",
    "Uma journeyed to the town by cart.",
]
FIT_VERBS = {"ran", "hurried", "marched", "sailed", "drove", "hiked", "sprinted", "journeyed"}
TEST_ACTION_VERBS = {"set", "climbed", "carried", "walked", "rowed"}

HYP_SPACE_SPEC = dict(
    candidate_plugins=["ruleind"], min_coverage=1, purity_thresh=0.9, max_conjunct=2, max_rules=4,
    key_fn=lambda inst: tuple(sorted(inst["feats"])),
)


def build_fit_episodes():
    eps = [{"feats": action_frame_feats(s), "gold_class": "GOAL"} for s in FIT_POS_SENTENCES]
    eps += [{"feats": action_frame_feats(s), "gold_class": "NOT_GOAL"} for s in FIT_NEG_SENTENCES]
    return eps


def induce_hypothesis():
    """MDL model-selection (hdlab.learner, config-only registry) over the declared action-frame
    features. Returns (plugin_name, hypothesis, all_results) -- 'hypothesis' is glass-box (JSON-able)."""
    episodes = build_fit_episodes()
    chosen_name, chosen, all_results = learner_learn(
        episodes, lambda inst: inst["feats"], HYP_SPACE_SPEC)
    return chosen_name, chosen, all_results


# ============================================================================ WIRE POINT (monkeypatch)
def make_generative_typer(orig_typer, plugin_name, hypothesis):
    def typer(sentence, subject):
        events, info = orig_typer(sentence, subject)
        feats = action_frame_feats(sentence)
        pred = learner_apply(plugin_name, hypothesis, feats, key=None, default_class="NOT_GOAL")
        fired = False
        already_goal = any(r == R_GOAL and e == subject for (e, r) in events)
        if pred == "GOAL" and subject is not None and not already_goal:
            events = list(events) + [(subject, R_GOAL)]
            fired = True
        info = dict(info)
        info["generative_goal_fired"] = fired
        info["generative_feats"] = feats
        return events, info
    return typer


@contextmanager
def generative_typing_enabled(plugin_name, hypothesis):
    """Splices the generative typer into the SINGLE module-global name `build_positions()` resolves
    at call time (exp_component5_gold_role_isolated_v1.type_sentence_events). Restores on exit."""
    orig = C5MOD.type_sentence_events
    C5MOD.type_sentence_events = make_generative_typer(orig, plugin_name, hypothesis)
    try:
        yield
    finally:
        C5MOD.type_sentence_events = orig


# ============================================================================ per-condition per-seed run
def run_condition_seed(condition: str, seed: int, plugin_name, hypothesis):
    if condition == "generative":
        with generative_typing_enabled(plugin_name, hypothesis):
            res = FAIRMOD.run_seed(seed)
    elif condition == "lexical_only":
        res = FAIRMOD.run_seed(seed)
    else:
        raise ValueError(f"unknown condition {condition!r}")
    return res


def subset_metrics(core_rows, verb_type):
    rows = [r for r in core_rows if r["verb_type"] == verb_type]
    div = [r for r in rows if r["is_divergent"]]
    n = len(rows)
    n_div = len(div)

    def rate(rows_, key):
        return round(sum(bool(r[key]) for r in rows_) / len(rows_), 4) if rows_ else None

    scr = [r for r in div if r.get("scrambled_final_owner") is not None]
    return dict(
        n=n, n_divergent=n_div,
        recency_floor_divergent=rate(div, "recency_matches_gold"),
        system_accuracy_divergent=rate(div, "matches_gold"),
        system_scrambled_accuracy_divergent=rate(scr, "scrambled_matches_gold"),
        n_typing_miss_goal=sum(r["typing_miss_goal"] for r in rows),
    )


# ============================================================================ aggregate + verdict
def aggregate(per_condition_seed: dict, induction_report: dict):
    seeds = sorted(SEEDS)

    def mean_over_seeds(cond, subset, key):
        vals = [per_condition_seed[cond][s][subset][key] for s in seeds
                 if per_condition_seed[cond][s][subset][key] is not None]
        return round(sum(vals) / len(vals), 4) if vals else None

    summary = {}
    for cond in CONDITIONS:
        summary[cond] = {}
        for subset in ("action_implied", "explicit_psych"):
            summary[cond][subset] = dict(
                n=per_condition_seed[cond][seeds[0]][subset]["n"],
                n_divergent=per_condition_seed[cond][seeds[0]][subset]["n_divergent"],
                recency_floor_divergent=mean_over_seeds(cond, subset, "recency_floor_divergent"),
                system_accuracy_divergent=mean_over_seeds(cond, subset, "system_accuracy_divergent"),
                system_scrambled_accuracy_divergent=mean_over_seeds(
                    cond, subset, "system_scrambled_accuracy_divergent"),
                n_typing_miss_goal=per_condition_seed[cond][seeds[0]][subset]["n_typing_miss_goal"],
            )

    ai_gen = summary["generative"]["action_implied"]
    ai_lex = summary["lexical_only"]["action_implied"]
    ep_gen = summary["generative"]["explicit_psych"]
    ep_lex = summary["lexical_only"]["explicit_psych"]

    gate_lift = (ai_gen["system_accuracy_divergent"] is not None
                 and ai_gen["system_accuracy_divergent"] >= 0.5)
    gate_baseline_was_zero = (ai_lex["system_accuracy_divergent"] == 0.0)
    gate_no_regression_explicit = (
        ep_gen["system_accuracy_divergent"] is not None
        and ep_lex["system_accuracy_divergent"] is not None
        and ep_gen["system_accuracy_divergent"] >= ep_lex["system_accuracy_divergent"])
    gate_positional_baseline_zero = (
        ai_gen["recency_floor_divergent"] == 0.0 and ai_lex["recency_floor_divergent"] == 0.0
        and ep_gen["recency_floor_divergent"] == 0.0 and ep_lex["recency_floor_divergent"] == 0.0)

    gain_unscrambled = (ai_gen["system_accuracy_divergent"] - ai_gen["recency_floor_divergent"]
                         if ai_gen["system_accuracy_divergent"] is not None else None)
    gain_scrambled = (ai_gen["system_scrambled_accuracy_divergent"] - ai_gen["recency_floor_divergent"]
                       if ai_gen["system_scrambled_accuracy_divergent"] is not None else None)
    if gain_unscrambled is not None and gain_unscrambled > 1e-9:
        gate_scramble_collapses = (gain_scrambled is not None
                                    and gain_scrambled <= 0.5 * gain_unscrambled + 1e-9)
        scramble_vacuous = False
    else:
        gate_scramble_collapses = (gain_scrambled is not None and gain_scrambled <= 1e-9)
        scramble_vacuous = True

    gate_verb_disjoint = FIT_VERBS.isdisjoint(TEST_ACTION_VERBS)
    gate_rule_induced = induction_report["chosen_name"] != "KEEP_EPISODIC"
    gate_frame_feature_used = induction_report.get("uses_purpose_feature", False)

    all_hard_pass_gates = dict(
        lift_ge_0p5=gate_lift, baseline_was_zero=gate_baseline_was_zero,
        no_regression_explicit=gate_no_regression_explicit,
        positional_baseline_zero=gate_positional_baseline_zero,
        scramble_collapses=gate_scramble_collapses, verb_disjoint=gate_verb_disjoint,
        rule_induced=gate_rule_induced, frame_feature_used=gate_frame_feature_used,
    )
    if all(all_hard_pass_gates.values()):
        verdict = "HARD_PASS_GENERATIVE_GOAL_TYPING_RECOVERS_ACTION_IMPLIED"
    elif (ai_gen["system_accuracy_divergent"] or 0) > 0 and gate_no_regression_explicit \
            and gate_positional_baseline_zero:
        verdict = "PARTIAL_GENERATIVE_GOAL_TYPING_SOME_RECOVERY"
    else:
        verdict = "HARD_FAIL_GENERATIVE_GOAL_TYPING_DID_NOT_RECOVER"

    msg = (
        f"ACTION_IMPLIED divergent: lexical_only={ai_lex['system_accuracy_divergent']} "
        f"(N_div={ai_lex['n_divergent']}) -> generative={ai_gen['system_accuracy_divergent']} "
        f"(N_div={ai_gen['n_divergent']}, scrambled={ai_gen['system_scrambled_accuracy_divergent']}). "
        f"EXPLICIT_PSYCH divergent (no-regression check): lexical_only="
        f"{ep_lex['system_accuracy_divergent']} -> generative={ep_gen['system_accuracy_divergent']}. "
        f"positional_baseline(recency_floor) all-conditions-zero={gate_positional_baseline_zero}. "
        f"GATES: {all_hard_pass_gates}.")

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {msg}", summary=msg,
        per_condition=summary, gates=all_hard_pass_gates,
        induction=induction_report,
    )


# ============================================================================ infra
def _write_json(path, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, path)


def run(run_mode: str):
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    _write_json(os.path.join(OUTPUT_DIR, "_start_marker.json"),
                {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
                 "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node(),
                 "expected_n_units": EXPECTED_N_SEEDS * len(CONDITIONS)})

    plugin_name, chosen, all_results = induce_hypothesis()
    if chosen is None:
        raise RuntimeError("MDL model-selection returned KEEP_EPISODIC -- no rule induced from FIT set")
    hypothesis = chosen.hypothesis
    induction_report = dict(
        chosen_name=plugin_name, compression_ratio=chosen.compression_ratio,
        n_rules=chosen.metrics.get("n_rules"), hypothesis=hypothesis,
        uses_purpose_feature=any(
            "purpose_to_no_det" in r.get("conjunct", []) for r in hypothesis.get("rules", [])),
    )
    print(f"[induce] plugin={plugin_name} n_rules={induction_report['n_rules']} "
          f"compression_ratio={induction_report['compression_ratio']:.3f} "
          f"uses_purpose_feature={induction_report['uses_purpose_feature']}", flush=True)

    done = completed_units(OUTPUT_DIR)
    per_condition_seed = {c: {} for c in CONDITIONS}
    for cond in CONDITIONS:
        for seed in SEEDS:
            k = unit_key("cond", cond, "seed", seed)
            if k in done:
                print(f"[resume] {cond} seed={seed} done, skip", flush=True)
                continue
            ts = time.perf_counter()
            res = run_condition_seed(cond, seed, plugin_name, hypothesis)
            ai = subset_metrics(res["core_rows"], "action_implied")
            ep = subset_metrics(res["core_rows"], "explicit_psych")
            unit = dict(condition=cond, seed=seed, action_implied=ai, explicit_psych=ep)
            record_unit(OUTPUT_DIR, k, unit)
            print(f"[progress] {cond} seed={seed} {time.perf_counter()-ts:.2f}s "
                  f"action_implied_sys_acc_div={ai['system_accuracy_divergent']} "
                  f"explicit_sys_acc_div={ep['system_accuracy_divergent']}", flush=True)

    units = load_units(OUTPUT_DIR)
    for u in units.values():
        per_condition_seed[u["condition"]][int(u["seed"])] = {
            "action_implied": u["action_implied"], "explicit_psych": u["explicit_psych"]}

    n_landed = sum(len(per_condition_seed[c]) for c in CONDITIONS)
    if n_landed < EXPECTED_N_SEEDS * len(CONDITIONS):
        raise RuntimeError(
            f"META_RULE_H cardinality breach: {n_landed}/{EXPECTED_N_SEEDS * len(CONDITIONS)} units")

    agg = aggregate(per_condition_seed, induction_report)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(seeds=SEEDS, conditions=CONDITIONS,
                         cardinality_ok=(n_landed == EXPECTED_N_SEEDS * len(CONDITIONS)))
    agg["prereg"] = "preregs/2026-08-05_c5_generative_goal_typing_action_frame_v1.md"
    agg["cites"] = [
        "notes/drill_brain_goal_owner_flow.md",
        "notes/DRILL_SYNTHESIS_goal_owner_brain_and_fairness.md",
        "experiments/exp_c5_fair_goal_owner_v1.py (reused bit-identical harness)",
        "hdlab/learner/ (config-only MDL plugin registry, ruleind plugin)",
        "hdlab/goal_owner_select.py; hdlab/self_improving_loop.py",
    ]
    agg["dispatch"] = "LOCAL-ONLY, in-process foreground, not queue-dispatched (per task brief)"
    _write_json(os.path.join(OUTPUT_DIR, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.2f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    # (1) FIT/TEST verb-disjointness (held-out generalization, not memorization)
    assert FIT_VERBS.isdisjoint(TEST_ACTION_VERBS), (
        f"FIT verbs overlap TEST action_implied verbs: {FIT_VERBS & TEST_ACTION_VERBS}")
    print(f"[SELFTEST 1/8] FIT verbs {sorted(FIT_VERBS)} disjoint from TEST action_implied verbs "
          f"{sorted(TEST_ACTION_VERBS)}", flush=True)

    # (2) feature extractor: purpose infinitive detected, prepositional "to NP" NOT falsely fired
    assert "purpose_to_no_det" in action_frame_feats("Nell ran to the well to fetch water before noon.")
    assert "purpose_to_no_det" not in action_frame_feats("Nell ran to the well early in the morning.")
    assert "purpose_to_no_det" not in action_frame_feats("Owen hurried to the barn before the storm.")
    print("[SELFTEST 2/8] action_frame_feats fires on infinitival 'to VP', not on 'to the NP'",
          flush=True)

    # (3) held-out feature check ON THE ACTUAL TEST BANK sentences (verbs never seen in FIT)
    _all_rows, core, _twins = FAIRMOD.load_bank()
    implied = [r for r in core if r["verb_type"] == "action_implied"]
    assert len(implied) >= 5, f"expected a real action-implied subset, got {len(implied)}"
    s1_fires = [it for it in implied
                if "purpose_to_no_det" in action_frame_feats(FAIRMOD._sentences(it["text"])[0])]
    assert len(s1_fires) == len(implied), (
        f"expected the structural feature to fire on ALL {len(implied)} action_implied S1 sentences "
        f"(held-out verbs); fired on {len(s1_fires)}: {[it['id'] for it in s1_fires]}")
    print(f"[SELFTEST 3/8] purpose_to_no_det fires on all {len(implied)} held-out action_implied "
          f"S1 sentences (verbs never in FIT set)", flush=True)

    # (4) MDL induction produces a non-episodic rule that USES the structural feature
    plugin_name, chosen, _all_results = induce_hypothesis()
    assert chosen is not None, "MDL model-selection returned KEEP_EPISODIC on the FIT set"
    hyp = chosen.hypothesis
    uses_feat = any("purpose_to_no_det" in r.get("conjunct", []) for r in hyp.get("rules", []))
    assert uses_feat, f"induced hypothesis does not use purpose_to_no_det: {hyp}"
    print(f"[SELFTEST 4/8] MDL induction (plugin={plugin_name}) promoted a rule using "
          f"purpose_to_no_det (compression_ratio={chosen.compression_ratio:.3f})", flush=True)

    # (5) LEXICAL-ONLY baseline reproduces the documented pre-existing gap (sanity: the gap is real)
    res_lex = FAIRMOD.run_seed(0)
    ai_lex_rows = [r for r in res_lex["core_rows"] if r["verb_type"] == "action_implied"]
    assert all(r["typing_miss_goal"] for r in ai_lex_rows), (
        "expected ALL action_implied items to miss GOAL typing under the lexicon-only typer "
        "(the pre-existing documented gap this cell targets)")
    print(f"[SELFTEST 5/8] lexical-only typer misses GOAL on all {len(ai_lex_rows)} action_implied "
          f"items (confirms the targeted gap is real, not stale)", flush=True)

    # (6) GENERATIVE typer: ARMS-MUST-DIFFER (role_seq differs from lexical-only on >=1 action_implied
    # item) + typing_miss_goal flips to False on the held-out action_implied items.
    with generative_typing_enabled(plugin_name, hyp):
        res_gen = FAIRMOD.run_seed(0)
    ai_gen_rows = [r for r in res_gen["core_rows"] if r["verb_type"] == "action_implied"]
    n_now_typed = sum(1 for r in ai_gen_rows if not r["typing_miss_goal"])
    assert n_now_typed == len(ai_gen_rows), (
        f"expected GOAL to now type on all {len(ai_gen_rows)} action_implied items under the "
        f"generative typer; only {n_now_typed} did -- mechanism did not fire as designed")
    print(f"[SELFTEST 6/8] generative typer types GOAL on {n_now_typed}/{len(ai_gen_rows)} "
          f"action_implied items (was 0 under lexical-only)", flush=True)

    # (7) no-regression: explicit_psych items are IDENTICAL between conditions (same accuracy)
    ep_lex = subset_metrics(res_lex["core_rows"], "explicit_psych")
    ep_gen = subset_metrics(res_gen["core_rows"], "explicit_psych")
    assert ep_gen["system_accuracy_divergent"] == ep_lex["system_accuracy_divergent"], (
        f"explicit_psych regression: lexical_only={ep_lex['system_accuracy_divergent']} "
        f"generative={ep_gen['system_accuracy_divergent']}")
    print(f"[SELFTEST 7/8] explicit_psych divergent accuracy unchanged "
          f"({ep_lex['system_accuracy_divergent']}) -- no regression", flush=True)

    # (8) positional baseline (recency_floor) stays 0.0 on the action_implied divergent subset in
    # BOTH conditions -- the instrument's fairness gate is untouched by this cell.
    ai_lex = subset_metrics(res_lex["core_rows"], "action_implied")
    ai_gen = subset_metrics(res_gen["core_rows"], "action_implied")
    assert ai_lex["recency_floor_divergent"] == 0.0 and ai_gen["recency_floor_divergent"] == 0.0, (
        f"positional baseline nonzero: lexical={ai_lex['recency_floor_divergent']} "
        f"generative={ai_gen['recency_floor_divergent']}")
    print(f"[SELFTEST 8/8] positional (recency) baseline stays 0.0 on action_implied divergent "
          f"subset in both conditions (N_divergent={ai_gen['n_divergent']}); generative system "
          f"accuracy this seed={ai_gen['system_accuracy_divergent']}", flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        raise SystemExit(0 if self_test() else 1)
    run("full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_json(os.path.join(OUTPUT_DIR, "metrics.json"),
                    {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                     "traceback": traceback.format_exc()[:5000],
                     "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
