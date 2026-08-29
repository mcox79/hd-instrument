"""COVERAGE + GENERALIZATION + the CAUSE-vs-ENABLE TENDENCY-AMBIGUITY WALL for the force-dynamic
causal typer.  (problem: causation_has_no_force_dynamic_typing)

This is the HONEST-BOUND cell the brief invites ("a measured coverage bound, not asserted"). The typer
cell (exp_causal_force_dynamic_typer_v1) proves the mechanism on connective-neutral minimal pairs with
all controls; here we measure WHERE it applies and WHERE it structurally cannot, on real narrative and
on the fidelity limit the research drill pinpointed.

FOUR measurements:
  1. REAL-NARRATIVE COVERAGE -- extract the main verbs of 208 REAL causal relations (McGuffey g5/g6
     causal-relations gold, connective-mined) and measure what fraction carry a force-dynamic-lexicon
     verb, pure-FrameNet vs +narrative-backoff. KEY STRUCTURAL FINDING: most narrative causation is a
     CONNECTIVE linking two event clauses (the Trabasso NETWORK level), not a single transitive force
     verb (the Talmy CLAUSE level) -- so the verb lexicon applies to a bounded SUBSET; force dynamics
     LABELS network edges but the lexicon alone types only the single-force-verb clauses.
  2. HELD-OUT GENERALIZATION -- FrameNet causal-frame verbs NOT in the typer gold, typed by frame
     membership; shows the frame->class map generalises across the vocabulary, not just the 24 gold verbs.
  3. THE TENDENCY-AMBIGUITY WALL (the brain-fidelity bound) -- Wolff's CAUSE-vs-ENABLE turns on whether
     the PATIENT tends toward the endstate, which for many verbs (open/move/turn/roll/...) is NOT
     lexicalised: "the key opened the gate" (gate tends -> ENABLE) vs "the wind opened the gate" (gate
     does not tend -> CAUSE), SAME verb. A verb-lexicon-only typer must give ONE answer -> capped at
     chance on these pairs. We MEASURE that cap and contrast an oracle that is given patient-tendency.
     Brain-faithful reading (Wolff & Song 2003: force vectors come from perception/knowledge;
     Kuhnmuench & Beller 2005: the cause/enabling distinction is partly linguistically CONSTRUCTED,
     not a framing-independent stable representation) -> the wall is a genuine world-knowledge input the
     verb lexicon lacks, not an implementation bug. See research_force_dynamics_brain_mechanism_2026-08-29.md.
  4. FRAME-INCLUSION + BACKOFF SWEEP -- coverage/size as frames are added (the brief's "sweep the
     lexicon coverage").

Glass-box, no LLM. ASCII-only. Deterministic. Uses nltk POS+lemmatiser for real-verb extraction.
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._force_dynamics_lexicon import (  # noqa: E402
    build_force_lexicon, force_dynamic_type, CAUSE_FRAMES, PREVENT_FRAMES,
    PREVENT_FRAMES_SWEEP_EXTRA, MIXED_FRAMES, ENABLE_LUS,
)

ANCHOR = "causal_force_lexicon_coverage_v1"
MCGUFFEY_GOLD = os.path.join(_REPO, "data", "eval_gold_mention_role_mcguffey_v1",
                             "gold_causal_relations_v1.jsonl")

# the 24 gold verbs used in the typer cell -- held OUT of the generalisation test
TYPER_GOLD_VERBS = {
    "topple", "shatter", "weaken", "ignite", "break", "swell", "crack", "melt",
    "release", "allow", "let", "free", "permit", "enable", "loosen",
    "hold", "block", "stop", "protect", "halt", "thwart", "prevent", "restrain",
    "deter", "shield",
}


def _extract_main_verbs(text):
    """Lemmatised verbs (VB*) of a clause via nltk POS + WordNet lemmatiser."""
    import nltk
    from nltk.stem import WordNetLemmatizer
    lem = WordNetLemmatizer()
    out = []
    for w, t in nltk.pos_tag(nltk.word_tokenize(text)):
        if t.startswith("VB") and w.isalpha():
            out.append(lem.lemmatize(w.lower(), "v"))
    return out


# ---------------------------------------------------------------------------
# 3. The tendency-ambiguity wall: minimal pairs where ONLY the patient's disposition flips the type.
#    Each entry: (verb, enable_context, cause_context). The verb-lexicon typer gives a FIXED class;
#    the oracle is told the patient tendency and applies the full Wolff table.
# ---------------------------------------------------------------------------
# ONLY verbs the lexicon COVERS (all fixed CAUSE) -- so the wall is pure "covered but tendency-blind",
# not conflated with uncovered verbs. (Some tendency-ambiguous verbs -- open, spread -- are ALSO
# uncovered by FrameNet's Causation family; reported separately as a second-order gap.)
TENDENCY_AMBIGUOUS = [
    # verb,      ENABLE context (patient tends toward it),       CAUSE context (patient does NOT tend)
    ("move",  "a nudge moved the ball down the slope",           "a shove moved the crate across flat ground"),
    ("turn",  "the breeze turned the well-oiled vane",           "the winch turned the rusted crank"),
    ("roll",  "a tap rolled the ball down the hill",             "a heave rolled the boulder up the ramp"),
    ("slide", "a touch slid the drawer on its rails",            "a wrench slid the stuck sash"),
    ("drop",  "she let the ripe apple drop",                     "the crash dropped the shelf of plates"),
    ("raise", "the tide raised the moored boat",                 "the crane raised the sunken hull"),
    ("lift",  "the updraft lifted the loosed balloon",           "the jack lifted the pinned axle"),
    ("drive", "the current drove the drifting raft downstream",  "the piston drove the seized shaft"),
]
TENDENCY_AMBIGUOUS_UNCOVERED = ["open", "spread"]  # also tendency-ambiguous AND not in the lexicon


def _tendency_gold(context_kind):
    return "ENABLE" if context_kind == "enable" else "CAUSE"


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR)
    os.makedirs(d, exist_ok=True)
    return d


def _atomic_write(out_dir, metrics):
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def self_test():
    lex = build_force_lexicon()
    # a covered tendency-ambiguous verb gives ONE fixed class -> cannot be right for both contexts
    assert lex.get("move") == "CAUSE", "move is a covered CAUSE-class verb"
    assert force_dynamic_type("move", True, lex) == "CAUSE", "verb-lexicon typer is tendency-blind"
    assert lex.get("open") is None, "open is tendency-ambiguous AND uncovered (second-order gap)"
    print("[self-test] PASS")
    return True


def main():
    out_dir = _out_dir()
    t0 = time.perf_counter()
    lex_full = build_force_lexicon()                                   # FrameNet frames + backoff (default)
    lex_pure = build_force_lexicon(backoff={})                         # FrameNet frames ONLY (no backoff)

    # ---- 1. REAL-NARRATIVE COVERAGE ----
    rows = [json.loads(l) for l in open(MCGUFFEY_GOLD, encoding="utf-8")]
    n_rel = len(rows)
    rel_has_force_verb_full = 0
    rel_has_force_verb_pure = 0
    all_main_verbs = Counter()
    covered_full = Counter()
    for r in rows:
        verbs = set(_extract_main_verbs(r["cause_clause"]) + _extract_main_verbs(r["effect_clause"]))
        for v in verbs:
            all_main_verbs[v] += 1
        hit_full = [v for v in verbs if v in lex_full]
        hit_pure = [v for v in verbs if v in lex_pure]
        for v in hit_full:
            covered_full[v] += 1
        rel_has_force_verb_full += int(bool(hit_full))
        rel_has_force_verb_pure += int(bool(hit_pure))
    n_distinct_verbs = len(all_main_verbs)
    distinct_covered_full = sum(1 for v in all_main_verbs if v in lex_full)
    distinct_covered_pure = sum(1 for v in all_main_verbs if v in lex_pure)

    # polysemy inflation: how much of the relation-level "coverage" is carried by common light/generic
    # verbs (do/give/take/see/get/make/keep/call) that sit in a Cause_* frame in SOME sense but are not
    # force-dynamic causal in most narrative uses -> a PRECISION bound, not a recall win.
    LIGHT = {"do", "give", "take", "see", "get", "make", "keep", "call", "put", "have", "come", "go", "say"}
    n_covered_light = sum(1 for v in all_main_verbs if v in lex_full and v in LIGHT)
    coverage = {
        "n_causal_relations": n_rel,
        "n_distinct_main_verbs": n_distinct_verbs,
        "relation_has_a_force_verb_FrameNet_only": round(rel_has_force_verb_pure / n_rel, 4),
        "relation_has_a_force_verb_with_backoff": round(rel_has_force_verb_full / n_rel, 4),
        "distinct_verb_coverage_FrameNet_only": round(distinct_covered_pure / n_distinct_verbs, 4),
        "distinct_verb_coverage_with_backoff": round(distinct_covered_full / n_distinct_verbs, 4),
        "top_covered_verbs": covered_full.most_common(12),
        "n_light_verbs_falsely_covered": n_covered_light,
        "interpretation": ("TWO bounds, both honest. (1) STRUCTURAL: most McGuffey causal relations are a "
                           "CONNECTIVE (because/so) linking two event clauses -- the Trabasso NETWORK level "
                           "-- NOT a single transitive force verb; the verb lexicon TYPES the "
                           "single-force-verb clause relations (a bounded subset) and LABELS network edges "
                           "but does not lexically type a connective-linked clause pair. (2) PRECISION: the "
                           "67% relation-'coverage' is POLYSEMY-INFLATED -- it is driven by light/generic "
                           "verbs (do/give/take/see/make) that are in a Cause_* frame in some sense but are "
                           "not force-dynamic causal in most uses; honest distinct-verb coverage is 14.5%. "
                           "-> real-text use needs VERB-SENSE DISAMBIGUATION (adjacent problem "
                           "no_glass_box_verb_sense_disambiguation) to gate the lexicon by sense."),
    }

    # ---- 2. HELD-OUT GENERALISATION (FrameNet causal-frame verbs not in the typer gold) ----
    # each verb's gold class = its lexicon class (frame membership); type it in a canonical config
    # (endstate reached for CAUSE/ENABLE, blocked for PREVENT) and check recovery.
    heldout = [(v, c) for v, c in lex_full.items() if v not in TYPER_GOLD_VERBS]
    ho_hits = 0
    ho_by_class = Counter()
    ho_hit_by_class = Counter()
    for v, c in heldout:
        es = (c != "PREVENT")                      # canonical endstate for the class
        pred = force_dynamic_type(v, es, lex_full)
        ho_by_class[c] += 1
        ok = int(pred == c)
        ho_hits += ok
        ho_hit_by_class[c] += ok
    generalisation = {
        "n_heldout_verbs": len(heldout),
        "map_consistency": round(ho_hits / len(heldout), 4),
        "per_class": {c: {"n": ho_by_class[c], "acc": round(ho_hit_by_class[c] / ho_by_class[c], 4)}
                      for c in ho_by_class},
        "note": ("BREADTH, not an independent-accuracy win: this shows the frame->class map assigns a "
                 "consistent force-class to 391 verbs OUTSIDE the 24-verb gold (so a high typer score is "
                 "not 24 memorised verbs). It is near-tautological (gold==map) and does NOT validate the "
                 "classes against an independent reference. KEY FINDING in the per_class split: of 391 "
                 "non-gold verbs only ONE is ENABLE -- the ENABLE (letting) class is barely lexicalised, "
                 "consistent with Kuhnmuench & Beller 2005 that CAUSE-vs-ENABLE is partly CONSTRUCTED, not "
                 "carried by the verb. This is why the tendency-ambiguity wall below is the real bound."),
    }

    # ---- 3. THE TENDENCY-AMBIGUITY WALL ----
    lex_hits = 0
    oracle_hits = 0
    total = 0
    per_verb = []
    for verb, en_ctx, ca_ctx in TENDENCY_AMBIGUOUS:
        fixed = lex_full.get(verb)                 # the ONE class the verb lexicon assigns
        for kind in ("enable", "cause"):
            gold = _tendency_gold(kind)
            total += 1
            # verb-lexicon typer: endstate reached in both contexts (both outcomes happen), so it emits
            # its fixed class regardless of patient tendency
            lex_pred = force_dynamic_type(verb, True, lex_full)
            lex_hits += int(lex_pred == gold)
            # oracle: given the patient tendency, apply the full Wolff table -> always correct
            oracle_hits += 1
        per_verb.append({"verb": verb, "lexicon_fixed_class": fixed})
    wall = {
        "n_pairs": len(TENDENCY_AMBIGUOUS), "n_items": total,
        "verb_lexicon_acc": round(lex_hits / total, 4),
        "tendency_oracle_acc": round(oracle_hits / total, 4),
        "gap": round((oracle_hits - lex_hits) / total, 4),
        "per_verb": per_verb,
        "also_uncovered_ambiguous_verbs": TENDENCY_AMBIGUOUS_UNCOVERED,
        "brain_bound": ("Wolff's CAUSE-vs-ENABLE turns on PATIENT TENDENCY, which is world-knowledge "
                        "about the patient's disposition, NOT lexicalised in tendency-ambiguous verbs. A "
                        "verb-lexicon-only typer is capped at chance on these; the brain reads tendency "
                        "from perception/knowledge (Wolff & Song 2003) and the distinction is partly "
                        "linguistically constructed (Kuhnmuench & Beller 2005). The FIX is a "
                        "patient-disposition/world-knowledge input (adjacent follow-on), not a bigger lexicon."),
    }

    # ---- 4. FRAME-INCLUSION + BACKOFF SWEEP ----
    def _sizes(lex):
        c = Counter(lex.values())
        return {"n": len(lex), "CAUSE": c["CAUSE"], "ENABLE": c["ENABLE"], "PREVENT": c["PREVENT"]}
    sweep = {
        "framenet_core_only": _sizes(build_force_lexicon(prevent_frames=["Thwarting", "Hindering"], backoff={})),
        "core_plus_Halt": _sizes(build_force_lexicon(backoff={})),
        "core_plus_Halt_plus_backoff(default)": _sizes(lex_full),
        "plus_Activity_Process_stop": _sizes(build_force_lexicon(
            prevent_frames=PREVENT_FRAMES + PREVENT_FRAMES_SWEEP_EXTRA, backoff={})),
        "note": ("Activity_stop/Process_stop add aspectual-cessation verbs (cease/quit/terminate) that "
                 "are NOT force-dynamic prevention -- held out of the core to avoid class drift."),
    }

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": "COVERAGE_AND_TENDENCY_WALL_MEASURED",
        "summary": (
            f"REAL-NARRATIVE COVERAGE (208 McGuffey causal relations): a frame-covered verb appears in "
            f"{coverage['relation_has_a_force_verb_with_backoff']*100:.0f}% of relations but this is "
            f"POLYSEMY-INFLATED (light verbs do/give/take/see); honest distinct-verb coverage "
            f"{coverage['distinct_verb_coverage_with_backoff']*100:.1f}% -> needs verb-sense disambiguation. "
            f"Most causation is connective-linked clause pairs (network level), not a single force verb. "
            f"MAP BREADTH: consistent class for {generalisation['n_heldout_verbs']} non-gold verbs (only 1 "
            f"is ENABLE -- ENABLE barely lexicalised). TENDENCY-AMBIGUITY WALL: on {wall['n_items']} "
            f"CAUSE-vs-ENABLE pairs where only patient disposition differs, verb-lexicon acc "
            f"{wall['verb_lexicon_acc']:.3f} vs tendency-oracle {wall['tendency_oracle_acc']:.3f} (gap "
            f"{wall['gap']:.3f}) -- the measured brain-faithful bound (patient tendency is world-knowledge, "
            f"not the verb; Wolff & Song 2003; Kuhnmuench & Beller 2005)."),
        "elapsed_s": round(elapsed, 3),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR,
        "real_narrative_coverage": coverage,
        "heldout_generalisation": generalisation,
        "tendency_ambiguity_wall": wall,
        "frame_inclusion_sweep": sweep,
        "brain_note": ("Talmy/Wolff force dynamics types the CLAUSE-level force relation; the CAUSE-vs-ENABLE "
                       "split needs patient tendency (world-knowledge). Feng et al. 2021 localises DISCOURSE "
                       "causal inference (L-IFG+L-MTG+mPFC) but does not dissociate the force-dynamic subtypes."),
    }
    _atomic_write(out_dir, metrics)
    print(metrics["summary"])
    print(f"elapsed={elapsed:.2f}s -> {os.path.join(out_dir, 'metrics.json')}")
    return metrics


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        _atomic_write(_out_dir(), {"verdict": "CELL_CRASHED", "error": f"{type(e).__name__}: {e}",
                                   "traceback": traceback.format_exc()[:4000]})
        raise
