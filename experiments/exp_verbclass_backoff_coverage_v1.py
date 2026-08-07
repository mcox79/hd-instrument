"""experiments/exp_verbclass_backoff_coverage_v1.py -- ISOLATED prove-architecture cell (2026-08-07).

QUESTION (Director/Research spawn): does a small, SUPPLY-DATA, Levin/VerbNet-style verb-CLASS
BACKOFF table for OOV/light goal-outcome verbs (get/give/make/find/see/have -- "do" deliberately
EXCLUDED, see SCOPE DECISION below) recover a result-class the bare hdlab.goal_typing.CLASS_REGISTRY
mechanism (Tier-1 exact + Tier-2 shared-feature-similarity, both already production) currently leaves
empty -- the diagnosed root cause in notes/coverage_wall_decomposition_2b_ceiling_and_referent_did_it_
happen_2026-08-06.md: "every desired-state has classes: set() -- the goal verb (get/give/make/find/
see/do/have, OOV or light) yields NO result-class, so congruence_decision has nothing to compare the
outcome against."

PRIOR-WORK CHECK (substrate_query.sh "VerbNet Levin verb class backoff OOV goal verb result-class
coverage", run before authoring): top hits are NOTES, not built cells -- research_grammar_
construction_resources_for_role_assignment_2026-07-20.md (cosine=0.3584, a general grammar-resource
survey) and drill_brain_openvocab_verb_class_membership_2026-08-06.md (cosine=0.3252, the design doc
for the ALREADY-WIRED hdlab/verb_lexical_similarity.py Tier-2 shared-feature-similarity backoff).
Disk-confirmed (read hdlab/verb_lexical_similarity.py in full): that production Tier-2 lexicon does
NOT contain get/give/make/find/see/do/have in either OUTCOME_VERB_FEATURES or GOAL_VERB_FEATURES (grep
-v confirmed), so this cell is a genuinely NEW, narrower increment -- not a rediscovery of the
production Tier-2 mechanism, and not redundant with it (this cell's backoff fires ONLY when Tier-1 AND
Tier-2 AND Tier-3 all abstain).

DOES NOT TOUCH hdlab/ or cert. This cell imports hdlab.goal_typing read-only and, at RUNTIME ONLY,
reassigns two of its module-global function attributes (_verb_classes, _class_relation) so the
ALREADY-OWNED congruence engine (find_desired_state / find_actual_state_candidates /
congruence_decision / congruence_with_lexicon_fallback) picks up the backoff -- Python resolves a bare
name inside a function body via the *enclosing module's* __dict__ at CALL time, so reassigning
`hdlab.goal_typing._verb_classes` changes what every one of that module's OWN internal call sites
(find_desired_state's helpers, find_actual_state_candidates, congruence_decision) sees, with zero
edits to the .py file on disk. The monkeypatch is reverted at the end of this script and a final
baseline re-run over the full 44-item eval confirms byte-identical restoration (self-test gate below).

STRICT-ADD DESIGN (the load-bearing safety property): the patched _verb_classes ALWAYS calls the
ORIGINAL Tier-1/2/3 pipeline first; the LEVIN_BACKOFF table is consulted ONLY when that returns
empty. An item the bare mechanism already classes is therefore NEVER touched by this cell -- no
already-correct verdict can flip (measured, not just argued -- see NO-REGRESSION gate below).

SCOPE DECISION -- "do" EXCLUDED: Levin (1993) / VerbNet do not define a dedicated "do" class -- "do"
is the paradigm semantically-bleached light-verb / pro-verb (Jespersen 1949; "do something" carries no
result-frame of its own, it inherits its result entirely from a nominalized complement or discourse
antecedent). Forcing a class onto it would be a precision risk (over-fire), not a genuine backoff, so
it is deliberately left unclassified and used as an ADVERSARIAL probe below (must stay classes=set()).

CLASS DESIGN (SUPPLY DATA, hand-authored from Levin 1993's class inventory, same convention as
hdlab.goal_typing.CLASS_REGISTRY / DESIDERATIVE_PASS -- NOT induced/tuned against this eval's text):
  LEVIN_POSSESSION  -- Levin 13.5.1 "Obtain verbs" (get, obtain, gain, procure, secure, earn, acquire,
                       win) + "have"-class possession-state verbs (have, possess, own, hold, retain)
                       + "find" (discovery/search-achievement, grouped with the obtain family) +
                       "take" (informal get-class synonym). Result-frame: agent comes to
                       possess/hold the theme.
  LEVIN_TRANSFER    -- Levin 13.1 "Verbs of Future Having" / dative-alternation give-class (give, hand,
                       grant, present, award, offer, provide, lend, pass, deliver). Result-frame:
                       theme's possession moves from agent to recipient.
  LEVIN_CREATION    -- Levin 26.1/26.4 "Build verbs" / "Create verbs" (make, build, create, construct,
                       form, produce, forge, craft). Result-frame: a new entity comes into existence.
  LEVIN_PERCEPTION  -- Levin 30.1 "Verbs of Perception" (see, notice, observe, spot, glimpse, perceive,
                       witness, view). Result-frame: agent gains perceptual/epistemic access to theme.
Each class lists ~8 members; the CORE trigger set actually needed to explain the coverage tail
(get/give/make/find/see/have) is a SUBSET of each class -- 2 members per class are HELD OUT of the
"tuning" narrative entirely (never referenced while designing the coverage-gain test below) and used
ONLY for the separate GENERALIZATION probe (Gate 3), so that gate is not circular.

OPPOSITION: no direct opposition is invented between the 4 new LEVIN_* tags (different frames =
UNRELATED, never forced to "same"); each is registered as OPPOSED to the two EXISTING negative-pole
CLASS_REGISTRY classes FAIL_LOSE / DAMAGE_LOSE (wanting to GET/MAKE/FIND/GIVE/SEE something is the
positive-achievement counterpart of an existing "lost/failed/missed/broke/destroyed" outcome already
in the production registry) -- this is the ONE new comparison rule this cell adds, applied via a
LOCAL wrapper around hdlab.goal_typing._class_relation, never edited on disk.

Run: .venv/Scripts/python.exe experiments/exp_verbclass_backoff_coverage_v1.py
Writes: data/exp_verbclass_backoff_coverage_v1/metrics.json
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

ANCHOR_NAME = "exp_verbclass_backoff_coverage_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
EVAL_PATH = os.path.join(REPO_ROOT, "experiments", "data", "goal_bearing_modern_eval_v1.jsonl")


# ================================================================================================
# SUPPLY DATA: Levin/VerbNet-style class table, built from SURFACE-FORM lists so every lemma_verb
# quirk (documented elsewhere in this codebase: "collaps"/"fil"/"mak"/"giv"/"tak" truncation) is
# computed from the REAL production lemma_verb, never hand-guessed.
# ================================================================================================

# concept -> (class_tag, [surface forms to run through lemma_verb], is_core_trigger)
_CLASS_MEMBERS = {
    "LEVIN_POSSESSION": [
        ("get",     ["get", "gets", "getting", "got"],                    True),   # CORE (task-named)
        ("have",    ["have", "has", "had", "having"],                     True),   # CORE (task-named)
        ("find",    ["find", "finds", "finding", "found"],                True),   # CORE (task-named)
        ("take",    ["take", "takes", "taking", "took", "taken"],         True),   # get-class informal synonym
        ("obtain",  ["obtain", "obtains", "obtaining", "obtained"],       True),
        ("gain",    ["gain", "gains", "gaining", "gained"],                True),
        ("procure", ["procure", "procures", "procuring", "procured"],     False),  # HELD OUT (Gate 3)
        ("secure",  ["secure", "secures", "securing", "secured"],         False),  # HELD OUT (Gate 3)
    ],
    "LEVIN_TRANSFER": [
        ("give",    ["give", "gives", "giving", "gave", "given"],         True),   # CORE (task-named)
        ("hand",    ["hand", "hands", "handing", "handed"],               True),
        ("offer",   ["offer", "offers", "offering", "offered"],           True),
        ("provide", ["provide", "provides", "providing", "provided"],     True),
        ("present", ["present", "presents", "presenting", "presented"],   True),
        ("award",   ["award", "awards", "awarding", "awarded"],           True),
        ("grant",   ["grant", "grants", "granting", "granted"],           False),  # HELD OUT (Gate 3)
        ("deliver", ["deliver", "delivers", "delivering", "delivered"],   False),  # HELD OUT (Gate 3)
    ],
    "LEVIN_CREATION": [
        ("make",     ["make", "makes", "making", "made"],                 True),   # CORE (task-named)
        ("build",    ["build", "builds", "building", "built"],            True),
        ("create",   ["create", "creates", "creating", "created"],        True),
        ("form",     ["form", "forms", "forming", "formed"],              True),
        ("produce",  ["produce", "produces", "producing", "produced"],    True),
        ("craft",    ["craft", "crafts", "crafting", "crafted"],          True),
        ("construct",["construct", "constructs", "constructing", "constructed"], False),  # HELD OUT
        ("forge",    ["forge", "forges", "forging", "forged"],            False),  # HELD OUT (Gate 3)
    ],
    "LEVIN_PERCEPTION": [
        ("see",      ["see", "sees", "seeing", "saw", "seen"],            True),   # CORE (task-named)
        ("notice",   ["notice", "notices", "noticing", "noticed"],        True),
        ("observe",  ["observe", "observes", "observing", "observed"],    True),
        ("spot",     ["spot", "spots", "spotting", "spotted"],            True),
        ("glimpse",  ["glimpse", "glimpses", "glimpsing", "glimpsed"],    True),
        ("witness",  ["witness", "witnesses", "witnessing", "witnessed"], False),  # HELD OUT (Gate 3)
        ("perceive", ["perceive", "perceives", "perceiving", "perceived"],False),  # HELD OUT (Gate 3)
    ],
}

# "do" is DELIBERATELY EXCLUDED (see SCOPE DECISION in module docstring) -- listed here only so the
# adversarial probe below can assert it stays classes=set() through the full pipeline.
ADVERSARIAL_UNRELATED_PROBES = ["whisper", "sneeze", "yawn"]  # no Levin relation to any tag above
ADVERSARIAL_EXCLUDED_LIGHT_VERB = "do"

_NEGATIVE_ACHIEVEMENT_CLASSES = {"FAIL_LOSE", "DAMAGE_LOSE"}  # existing CLASS_REGISTRY negative poles


def _build_backoff_table(lemma_verb_fn):
    """Returns (full_table, core_table, heldout_table): lemma -> frozenset({class_tag})."""
    full, core, heldout = {}, {}, {}
    for class_tag, members in _CLASS_MEMBERS.items():
        for concept, surfaces, is_core in members:
            for surf in surfaces:
                lemma = lemma_verb_fn(surf)
                full[lemma] = frozenset({class_tag})
                (core if is_core else heldout)[lemma] = frozenset({class_tag})
    return full, core, heldout


# ================================================================================================
# Monkeypatch machinery (runtime-only; file on disk never touched)
# ================================================================================================

def _install_patch(gt, backoff_table):
    """Reassigns gt._verb_classes / gt._class_relation to STRICT-ADD wrappers. Returns the two
    ORIGINAL function objects so the caller can restore them exactly."""
    orig_verb_classes = gt._verb_classes
    orig_class_relation = gt._class_relation

    def patched_verb_classes(lemma):
        classes = orig_verb_classes(lemma)  # Tier-1 (literal) + Tier-2 (similarity) + Tier-3 (acquired)
        if classes:
            return classes  # STRICT ADD: never override an existing classification
        return set(backoff_table.get(lemma, set()))

    def patched_class_relation(desired_classes, actual_classes):
        rel = orig_class_relation(desired_classes, actual_classes)
        if rel is not None:
            return rel  # STRICT ADD: never override an existing relation decision
        levin_d = {c for c in desired_classes if c in _CLASS_MEMBERS}
        levin_a = {c for c in actual_classes if c in _CLASS_MEMBERS}
        if levin_d and levin_d & levin_a:
            return "same"
        if levin_d and (actual_classes & _NEGATIVE_ACHIEVEMENT_CLASSES):
            return "opposed"
        if levin_a and (desired_classes & _NEGATIVE_ACHIEVEMENT_CLASSES):
            return "opposed"
        return None

    gt._verb_classes = patched_verb_classes
    gt._class_relation = patched_class_relation
    return orig_verb_classes, orig_class_relation


def _restore_patch(gt, orig_verb_classes, orig_class_relation):
    gt._verb_classes = orig_verb_classes
    gt._class_relation = orig_class_relation


# ================================================================================================
# Eval harness
# ================================================================================================

def _load_items():
    with open(EVAL_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _score(items, congruence_fn):
    """Returns dict id -> {"status": CORRECT|WRONG|NA, "verdict":..., "gold":..., "reason":...}."""
    out = {}
    for it in items:
        verdict, detail = congruence_fn(it["text"])
        gold = it["gold_outcome_polarity"].upper()
        v = verdict.upper()
        if v in ("NA", "NONE", "AMBIGUOUS"):
            status = "NA"
        elif v == gold:
            status = "CORRECT"
        else:
            status = "WRONG"
        out[it["id"]] = {"status": status, "verdict": v, "gold": gold,
                          "reason": detail.get("reason") if isinstance(detail, dict) else None}
    return out


def _diff(baseline, patched):
    coverage_gain = []      # NA -> CORRECT
    na_to_wrong = []        # NA -> WRONG (new mistake, but not a "flip of an already-correct item")
    regressions = []        # CORRECT -> anything else, or WRONG -> different WRONG-but-was-correct
    unchanged = []
    for iid in baseline:
        b, p = baseline[iid], patched[iid]
        if b["status"] == "CORRECT" and p["status"] != "CORRECT":
            regressions.append({"id": iid, "before": b, "after": p})
        elif b["status"] == "NA" and p["status"] == "CORRECT":
            coverage_gain.append({"id": iid, "before": b, "after": p})
        elif b["status"] == "NA" and p["status"] == "WRONG":
            na_to_wrong.append({"id": iid, "before": b, "after": p})
        else:
            unchanged.append(iid)
    return coverage_gain, na_to_wrong, regressions, unchanged


# ================================================================================================
# Gate 3: generalization probe (held-out class-mates, synthetic sentences, never referenced while
# building the coverage-gain test above)
# ================================================================================================

_HELDOUT_PROBES = [
    # (goal_sentence, outcome_sentence, gold_polarity, note)
    ("She wanted to procure a horse for the journey.",
     "But the horse was stolen before she could leave.", "UNMET",
     "LEVIN_POSSESSION held-out member 'procure' vs existing DAMAGE_LOSE-ish steal(OOV)/lost"),
    ("She wanted to secure a loan from the bank.",
     "She lost the loan to a rival buyer.", "UNMET",
     "LEVIN_POSSESSION held-out 'secure' opposed to existing FAIL_LOSE 'lost'"),
    ("The queen wished to grant her knight a title.",
     "The queen gave her knight the title of Sir Rowan.", "MET",
     "LEVIN_TRANSFER held-out 'grant' same-class as CORE 'give'"),
    ("The courier meant to deliver the package before noon.",
     "The courier failed to deliver it in time.", "UNMET",
     "LEVIN_TRANSFER held-out 'deliver' opposed to existing FAIL_LOSE 'failed'"),
    ("The engineers hoped to construct a bridge across the river.",
     "The engineers built the bridge in six months.", "MET",
     "LEVIN_CREATION held-out 'construct' same-class as CORE 'build'"),
    ("The smith wanted to forge a new sword for the king.",
     "The smith lost the metal in the fire.", "UNMET",
     "LEVIN_CREATION held-out 'forge' opposed to existing FAIL_LOSE 'lost'"),
    ("The sailor longed to witness the eclipse from the deck.",
     "The sailor saw the eclipse just before dawn.", "MET",
     "LEVIN_PERCEPTION held-out 'witness' same-class as CORE 'see'"),
    ("The scout hoped to perceive the enemy camp before dark.",
     "The scout missed the camp entirely in the fog.", "UNMET",
     "LEVIN_PERCEPTION held-out 'perceive' opposed to existing FAIL_LOSE 'missed'"),
]


def _run_heldout_probes(gt):
    results = []
    n_correct = 0
    for goal_s, outcome_s, gold, note in _HELDOUT_PROBES:
        passage = goal_s + " " + outcome_s
        verdict, detail = gt.congruence_with_lexicon_fallback(passage)
        ok = verdict.upper() == gold
        n_correct += int(ok)
        results.append({"goal": goal_s, "outcome": outcome_s, "gold": gold,
                         "verdict": verdict.upper(), "correct": ok,
                         "reason": detail.get("reason"), "note": note})
    return results, n_correct


# ================================================================================================
# Gate 4: adversarial over-fire probe
# ================================================================================================

def _run_adversarial_probes(gt, backoff_table):
    results = {}
    # (a) excluded light verb "do" must NOT get a class from the backoff table itself
    results["do_excluded_from_table"] = ADVERSARIAL_EXCLUDED_LIGHT_VERB not in backoff_table
    # (b) "do" through the live patched pipeline on a synthetic goal must still abstain (classes=set())
    desired = gt.find_desired_state("Chen decided to do something about it.")
    results["do_live_classes"] = sorted(desired["classes"]) if desired else None
    results["do_stays_unclassed"] = bool(desired) and desired["classes"] == set()
    # (c) unrelated verbs (no Levin relation to any of the 4 new tags) must not get a spurious class
    for w in ADVERSARIAL_UNRELATED_PROBES:
        results[f"unrelated_{w}_in_table"] = w in backoff_table
    return results


# ================================================================================================
# main
# ================================================================================================

def main():
    t0 = datetime.now(timezone.utc)
    import hdlab.goal_typing as gt
    from hdlab.thematic_role_labeler import lemma_verb

    items = _load_items()
    assert len(items) == 44, f"expected 44 eval items, got {len(items)}"

    # ---- Step 0: baseline (unpatched) full-44 pass -----------------------------------------
    baseline = _score(items, gt.congruence_with_lexicon_fallback)
    n_base_correct = sum(1 for v in baseline.values() if v["status"] == "CORRECT")
    n_base_wrong = sum(1 for v in baseline.values() if v["status"] == "WRONG")
    n_base_na = sum(1 for v in baseline.values() if v["status"] == "NA")

    # ---- Build backoff table (from REAL lemma_verb, not hand-guessed) ----------------------
    full_table, core_table, heldout_table = _build_backoff_table(lemma_verb)

    # ---- Install patch, re-run full-44 ------------------------------------------------------
    orig_verb_classes, orig_class_relation = _install_patch(gt, full_table)
    try:
        patched = _score(items, gt.congruence_with_lexicon_fallback)
        n_patch_correct = sum(1 for v in patched.values() if v["status"] == "CORRECT")
        n_patch_wrong = sum(1 for v in patched.values() if v["status"] == "WRONG")
        n_patch_na = sum(1 for v in patched.values() if v["status"] == "NA")

        coverage_gain, na_to_wrong, regressions, unchanged = _diff(baseline, patched)

        heldout_results, n_heldout_correct = _run_heldout_probes(gt)
        adversarial = _run_adversarial_probes(gt, full_table)
    finally:
        _restore_patch(gt, orig_verb_classes, orig_class_relation)

    # ---- Restoration self-test: baseline MUST reproduce byte-identically after revert ------
    baseline_after_revert = _score(items, gt.congruence_with_lexicon_fallback)
    restoration_ok = baseline_after_revert == baseline

    # ---- Verdict arithmetic -----------------------------------------------------------------
    n_gain = len(coverage_gain)
    n_regress = len(regressions)
    n_na_to_wrong = len(na_to_wrong)
    heldout_pass = n_heldout_correct >= 6  # >=6/8 (75%) held-out generalization bar
    no_overfire = (adversarial["do_stays_unclassed"]
                   and not any(adversarial[f"unrelated_{w}_in_table"] for w in ADVERSARIAL_UNRELATED_PROBES))

    if n_gain >= 3 and n_regress == 0 and heldout_pass and no_overfire:
        verdict = "HARD_PASS"
    elif n_gain == 0 or n_regress > 0 or not no_overfire:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        f"coverage_gain={n_gain} (NA->CORRECT) na_to_wrong={n_na_to_wrong} "
        f"regressions={n_regress} heldout={n_heldout_correct}/8 "
        f"no_overfire={no_overfire} restoration_ok={restoration_ok} verdict={verdict}"
    )
    print(verdict_msg, flush=True)
    for g in coverage_gain:
        print("  GAIN:", g["id"], g["before"], "->", g["after"], flush=True)
    for r in regressions:
        print("  REGRESSION:", r["id"], r["before"], "->", r["after"], flush=True)
    for n in na_to_wrong:
        print("  NA_TO_WRONG:", n["id"], n["before"], "->", n["after"], flush=True)

    elapsed_s = (datetime.now(timezone.utc) - t0).total_seconds()

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "elapsed_s": elapsed_s,
        "ts_iso": t0.isoformat(),
        "run_mode": "full",
        "eval_path": EVAL_PATH,
        "n_items": len(items),
        "baseline": {"correct": n_base_correct, "wrong": n_base_wrong, "na": n_base_na},
        "patched": {"correct": n_patch_correct, "wrong": n_patch_wrong, "na": n_patch_na},
        "coverage_gain_count": n_gain,
        "coverage_gain_items": coverage_gain,
        "na_to_wrong_count": n_na_to_wrong,
        "na_to_wrong_items": na_to_wrong,
        "regression_count": n_regress,
        "regression_items": regressions,
        "restoration_ok": restoration_ok,
        "heldout_generalization": {"n_correct": n_heldout_correct, "n_total": len(_HELDOUT_PROBES),
                                    "pass_bar": 6, "results": heldout_results},
        "adversarial_overfire_probe": adversarial,
        "backoff_table_size": {"full": len(full_table), "core": len(core_table),
                                "heldout": len(heldout_table)},
        "core_trigger_lemmas": sorted(core_table.keys()),
        "heldout_lemmas": sorted(heldout_table.keys()),
        "class_registry_negative_poles_used_for_opposition": sorted(_NEGATIVE_ACHIEVEMENT_CLASSES),
        "gates": {
            "coverage_gain_ge_3": n_gain >= 3,
            "no_regression": n_regress == 0,
            "heldout_generalization_ge_6_of_8": heldout_pass,
            "no_overfire": no_overfire,
            "restoration_ok": restoration_ok,
        },
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final_path = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, final_path)
    print(f"[metrics written] {final_path}", flush=True)
    return metrics


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        diag = {
            "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(e).__name__}: {str(e)[:500]}",
            "summary": f"CELL_CRASHED: {type(e).__name__}",
            "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "anchor_name": ANCHOR_NAME,
        }
        tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
        final_path = os.path.join(OUTPUT_DIR, "metrics.json")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(diag, f, indent=2)
        os.replace(tmp_path, final_path)
        raise
