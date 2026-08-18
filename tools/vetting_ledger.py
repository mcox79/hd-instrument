"""THE VETTING LEDGER -- every claim that has been checked, its verdict, and its DISPOSITION.

WHY THIS EXISTS (owner, 2026-08-18): "make sure these are making it into a clear final wired and/or
well tracked state. Everything should be categorized so we don't lose it again."

The "again" is earned. This project lost track of its own results three separate ways in one day:
  - `tools/substrate_query.sh`, the MANDATORY prior-work check, RETURNS ZERO BYTES AND EXITS 0, so
    every "no prior work found" report from every agent and from the Director was vacuous;
  - the figure "3,544 grounded concepts / 9.87x the hand lexicon" was REFUTED ON OUR OWN DISK by a
    successor cell and was still being quoted in `SUBSTRATE_CHARTER_read_first.md`, the document
    every session is told to read first;
  - `exp_unified_self_learning_loop_v3` was refuted by its OWN v4 five hours later and was still
    sitting on the vetting queue as a HARD_PASS weeks afterwards.
A verdict that lives only in a session transcript is a verdict the project will re-derive or,
worse, keep citing. This file is the durable home.

DISPOSITIONS -- every vetted cell gets exactly one, and nothing is allowed to sit in limbo:
  WIRE            UPHELD. Survives its own controls. Promote and register it.
  WIRE_NARROWED   QUALIFIED. Real but narrower than claimed. Citable ONLY with the narrowing
                  attached, which is recorded in `narrowing` and must travel with the number.
  RERUN_NAMED     SUSPENDED. Cannot be judged as it stands; the specific rerun is named in `rerun`.
  SHELVED_REFUTED REFUTED. Do NOT cite. If a figure from it is quoted anywhere, retire it there too.

THE RECORD SO FAR: 30 cells vetted across five passes -- 13 REFUTED, 5 SUSPENDED, 11 QUALIFIED,
**1 UPHELD**.

THE ORGAN LAYER IS A DIFFERENT POPULATION AND MUST NOT BE JUDGED BY THIS LEDGER'S BASE RATE.
This file audits CLAIMS. `hdlab/` holds 147 modules / 3.15 MB of source, and an experiment's claim
can be refuted while the ORGAN it exercised is perfectly good machinery. Owner, 2026-08-18: "we made
a lot of effort to build fully functional organs and we should make sure we're working off of that
significant effort." The organ accounting is a SEPARATE artifact
(`notes/ORGAN_ACCOUNTING_2026-08-18.md`) and 0-for-30 HERE says nothing about it.
*Correction on the way in: the Director told the owner "only 31 organs declare a self-test". The
real figure is ~82 (81 with a `__main__` self-test, independently matching
`notes/system_accounting_2026-08-13.md`'s 81 of 141). The testable surface is 2.6x larger than
claimed, and the error was a too-narrow regex.*

TWO PREDICTORS, IN ORDER OF STRENGTH. Both were learned from this ledger's own contents:
  1. **DID THE TEST ITEMS EXIST BEFORE THE MECHANISM DID?** This is the strong one. Every survivor
     was scored on items built independently of the rule; every refutation in pass 5 had detectors
     authored against the very items they were scored on. Free to check, and it beats every
     statistical signal we tried.
  2. Does the file carry a CI and a null? Necessary and WEAK -- `tools/verdict_evidence_gate.py`
     measures it (only 13 of 2,678 HARD_PASS carry both), but a cell can carry both and still be
     refuted, and one in this ledger is.

USAGE
  python tools/vetting_ledger.py --write     # regenerate notes/VETTING_LEDGER.md from the rows
  python tools/vetting_ledger.py --summary   # counts by disposition
  python tools/vetting_ledger.py --cite NAME # is this citable, and with what narrowing attached?
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER_MD = REPO / "notes" / "VETTING_LEDGER.md"
LEDGER_JSONL = REPO / "notes" / "vetting_ledger.jsonl"

# cell, verdict, disposition, one-line finding, narrowing-or-rerun, pass
ROWS = [
    # ---- pass 5: the best-evidenced batch (carried both a CI and a null) ----
    ("exp_agreement_depth_productivity_generalization_v1", "UPHELD", "WIRE",
     "Supervised only on depth<=1; 0.7324 [0.7154,0.7494] on 2,597 held-out depth>1 items vs "
     "majority floor 0.5741 (upper 0.5931); margin +0.1223 from the CI LOWER bound; holds OOD at "
     "depth 4+; scramble changes 86.5% of decisions.",
     "TIES the hand-written recursive rule (0.7312), does not beat it. Parity, not supremacy.", 5),
    ("exp_graded_divisive_comparator_v1", "QUALIFIED", "WIRE_NARROWED",
     "Real +0.0602 [0.0440,0.0762] over the live comparator; scramble twin 0.5065.",
     "CI lower bound does NOT clear its own pre-registered d>=0.05, and the 'divisive "
     "normalisation' half of the title contributes +0.00175.", 5),
    ("exp_read_xsent_coref_scene_protagonist_v1", "QUALIFIED", "WIRE_NARROWED",
     "Accuracy 0.2462 -> 0.4003; McNemar CI lower +0.1039 off its own discordant counts.",
     "The mechanism is a 5-sentence WINDOW, not 'scenes'. The cell says so itself.", 5),
    ("exp_multi_turn_loop_realtext_nphead_gate_v1", "SUSPENDED", "RERUN_NAMED",
     "'True zero confident-wrong' is 0 wrong of 18 KEPT (rule-of-three upper 0.167) against a "
     "declared band of 0.01; its new variable fired on 2 items that are the same passage, same "
     "answer, same gold.",
     "RERUN: enough kept items to resolve 0.01, and independent events rather than one passage.", 5),
    ("exp_social_relational_grounding_axis_v1", "REFUTED", "SHELVED_REFUTED",
     "`valence` takes exactly THREE distinct values across all 12 items, and acc_real equals the "
     "WordNet dictionary_lookup accuracy EXACTLY (10/12).",
     "A 3-entry lookup table wearing a substrate; it cannot change any prediction.", 5),
    ("exp_desiderative_negation_channel_v1", "REFUTED", "SHELVED_REFUTED",
     "8 of 8 recoveries lie INSIDE the 10-item set the taxonomy was designed from; 0 of 27 outside "
     "it; channel bit-identical ON vs OFF on both benches (0.6992/0.6992, 0.6623/0.6623).",
     "Pattern (f): the test items did not exist before the mechanism.", 5),
    # ---- pass 4 ----
    ("exp_causal_link_comprehension_pilot_v1", "REFUTED", "SHELVED_REFUTED",
     "Sibling of fuller_v3: the answer is written in and read back.", "", 4),
    ("exp_causal_link_comprehension_fuller_v3_cleaned", "REFUTED", "SHELVED_REFUTED",
     "Re-ran with gold links replaced by RANDOM PAIRS -> organ_integration 0.9722, BIT-IDENTICAL to "
     "the headline. Measures FHRR write/read fidelity at bundle-load 2. Baseline was swept until it "
     "failed ('...while driving mr_integration to 0.0000').", "", 4),
    ("exp_causal_link_comprehension_fuller_v2", "REFUTED", "SHELVED_REFUTED",
     "Same code as fuller_v3; dies with it.", "", 4),
    ("exp_unified_self_learning_loop_v3", "REFUTED", "SHELVED_REFUTED",
     "Its OWN scramble control scored HIGHER (0.0288 vs 0.0243); separation gates are literally "
     "0.0; two arms share a store digest; and its v4 five hours later records teaches_new=False.",
     "", 4),
    ("exp_pivot_selectional_knowledge_richness_2afc_v1", "QUALIFIED", "WIRE_NARROWED",
     "117 rated pairs vs 117 eval pairs is a PERFECT BIJECTION -- an LLM rated exactly the test. But "
     "the dumb twins do NOT reproduce it (0.5508 / 0.5339 / 0.4915).",
     "A CHEATING ORACLE reaches 0.78-0.85; the substrate did none of it. What it proves is that the "
     "knowledge is real AND ABSENT FROM OUR CORPUS -- which is the useful half.", 4),
    ("exp_outcome_valence_goal_congruence_v1", "SUSPENDED", "RERUN_NAMED",
     "The dumbest rule (goal verb lemma == outcome verb lemma) scores 7/8 = EXACTLY the "
     "pre-registered floor; mechanism beats it by one item; CIs overlap; P(8/8|p=0.875)=0.34.",
     "RERUN: >=20 D-type items where lemma-identity and goal-congruence DISSOCIATE, on verbs "
     "outside the hand-authored register, banked by someone who did not write it.", 4),
    ("exp_learned_argstruct_parser_lccp_independent_gold_v1", "QUALIFIED", "WIRE_NARROWED",
     "Arm B (NO LCCP) already clears every gate; adding LCCP moves F1 0.3934->0.4048, two items.",
     "The wrong component is credited, and 'generalizes' is a ONE-SIDED gate that fired because the "
     "held-out subset was EASIER (precision 0.632 vs 0.449). Absolute P=0.50, R=0.34.", 4),
    # ---- pass 3 ----
    ("exp_gap_driven_reader_controlled_v1", "REFUTED", "SHELVED_REFUTED",
     "A 12-line `Counter` with no substrate reproduces the headline 8/8 exactly; the margin is "
     "authored into the templates.", "", 3),
    ("exp_reading_grounding_loop_cycle2_v1", "REFUTED", "SHELVED_REFUTED",
     "Already refuted ON DISK by cycle3 (3544 -> 634). 2,328 of 3,544 GROUNDED_MEANING facts are "
     "SELF-ANCHORED. NOTE: this cell CARRIES a CI and a null and is still refuted -- proof that the "
     "evidence gate is necessary, not sufficient.",
     "RETIRE the figure '3,544 concepts / 9.87x the hand lexicon' wherever it appears.", 3),
    ("exp_reading_grounding_loop_cycle1_v1", "QUALIFIED", "WIRE_NARROWED",
     "Context-scramble control BINDS (removed 132 of 185).",
     "Same 67% self-anchoring applies; its curriculum-order arm is a NULL shipped inside a pass "
     "(0.3297 -> 0.3047).", 3),
    ("exp_verb_class_openvocab_similarity_v1", "REFUTED", "SHELVED_REFUTED",
     "All 26 words -- 10 seeds AND 16 'held-out' -- share ONE hand-written tag vector, so held-out "
     "similarity is exactly 1.0000. 64 decisions, 4 distinct vectors. Its cited baseline of 0.30 "
     "reads 0.6000 on disk and postdates the run.", "", 3),
    ("exp_c5_multigoal_content_coherence_tiebreak_v1", "REFUTED", "SHELVED_REFUTED",
     "Gold is defined by the rule the mechanism applies; bag-of-words overlap scores 12/12 under "
     "all three tie conventions. Margin over the strongest floor: 0.0000.", "", 3),
    ("exp_c5_primacy_trap_endtoend_goal_coherence_candidate_gen_v1", "QUALIFIED", "WIRE_NARROWED",
     "Genuinely LEAK-CLEAN -- it fixed a predecessor's gold leak and proves it with seven "
     "self-tests.",
     "Its four floors are ALL POSITIONAL and read 0.0000 by construction; a lexical-overlap floor "
     "scores 0.80/0.675 and its CI OVERLAPS the system's.", 3),
    # ---- pass 2 ----
    ("exp_context_vector_signal_v1", "QUALIFIED", "WIRE_NARROWED",
     "THE DENIAL QUESTION IS CLOSED CLEAN: heartbeats from unit 0 prove a cache miss, so the run "
     "was a genuine fresh computation and CLAUDE.md's requested clean-slate re-run is NOT needed.",
     "CITE `argmax_in_own_window_rate` 0.2871 vs an exactly bag-matched scramble 0.0050 -- NOT the "
     "ceiling-saturated 0.7830/0.9984 pair. And its HARD_PASS is POST-HOC: the pre-registered "
     "ceiling guard fired and was amended away after the run; prereg-literal tier is MIDDLE_BAND.", 2),
    ("exp_lexicon_coverage_audit_barrier2_v1", "QUALIFIED", "WIRE_NARROWED",
     "The COVERAGE half is UPHELD EXACTLY -- independently re-implemented, every figure reproduces "
     "to 4 dp (union 0.9893/0.9648).",
     "The second half is a SINGLE-RATER, UNBLINDED LLM self-audit of the prediction being tested; "
     "under the stricter rubric the cell itself names, it falls to 0.7417, BELOW its own 0.80 "
     "floor.", 2),
    ("exp_information_foraging_reading_v1", "QUALIFIED", "WIRE_NARROWED",
     "FORAGE genuinely beats RANDOM (185 vs 38 of 3000, z=10.1).",
     "A FLOOR-BEATER, NOT A SHELF-BEATER: FROZEN, the fixed schedule foraging exists to REPLACE, "
     "scores HIGHER (0.0743 vs 0.0617). Any claim it improved reading must say this.", 2),
    ("exp_pivot_scaled_seed_knowledge_table_v1", "REFUTED", "SHELVED_REFUTED",
     "A corpus-attestation floor computable from the cell's OWN cache scores 1.0000 (108/108) vs "
     "the LLM table's 0.6898. And scaling changed NOTHING: scaled and tiny digests identical, "
     "arms_differ_verified=False.", "", 2),
    ("exp_read_grow_adaptor_pyp_kn_breadth_v1", "REFUTED", "SHELVED_REFUTED",
     "Treatment coverage is a STRICT SUPERSET of baseline by construction, so the gate cannot fail; "
     "'3/3 seeds' is one measurement printed three times; a Zipf null reproduces the preemption "
     "correlation; on the only genuine generalization test it is WORSE than its own scramble.",
     "", 2),
    # ---- pass 1 ----
    ("exp_base_reader_grounded_relations_coref_v1", "REFUTED", "SHELVED_REFUTED",
     "Headline p=0.000 is RESAMPLE DEGENERACY -- (2/7)^7 over SEVEN paired differences. Exact "
     "McNemar gives p=0.0625, failing its own alpha. The cell RAN a real floor scoring 5/7 and did "
     "not use it.",
     "SURVIVING SECONDARY: relation_lift over all 25 items, full vs floor exact p=0.0215.", 1),
    ("exp_read_grow_foundation_realprose_glassbox_ie_v1", "SUSPENDED", "RERUN_NAMED",
     "Its only floor is a HARDCODED literal 1.0 imported from a different cell on a different "
     "corpus; no floor was run on its own 34 sentences.",
     "DO NOT CITE v1. CITE `exp_read_grow_foundation_realprose_glassbox_ie_v2` INSTEAD: 46 "
     "sentences, 0.891 vs a REAL STANDALONE baseline 0.565, stub removed.", 1),
    ("exp_online_knowledge_condenser_selectional_v1", "SUSPENDED", "RERUN_NAMED",
     "Best-designed of the first six -- real held-out split, explicit leakage guard, 4,151 mining "
     "sentences -- but n=48; FULL 0.750 [0.6275,0.8725] vs a 0.650 shuffle floor; z=1.07, p=0.285.",
     "RERUN at n~350, which is what separating 0.75 from 0.65 at 80% power requires.", 1),
    ("exp_read_grow_construction_induction_dop_fragments_v1", "QUALIFIED", "WIRE_NARROWED",
     "The strongest of the first six: real external corpus (UD English-EWT, 846 sentences), "
     "deprel-multiset-preserving scramble binding HARD across 3 seeds (2/124 vs 44/124 etc), "
     "CI-separated 0.355 [0.271,0.439], split_overlap=0.",
     "Parses are GOLD-SUPPLIED (upos+deprel read directly) and the metric is COVERAGE, not "
     "correctness (tunable 0.508/0.355/0.25 by min_count). Its own label -- FEASIBILITY PROBE -- is "
     "the honest one.", 1),
    ("exp_read_grow_openvocab_fastmap_v1", "QUALIFIED", "WIRE_NARROWED",
     "Real mechanism; its NO_CONFIRM control binds (removed 2 false facts).",
     "TOY SCOPE: 26 hand-authored sentences, 3 nonce words, 5 query cues; ABSTAIN_BASELINE=0.0 BY "
     "CONSTRUCTION; 5 seeds vary only the codebook, so n=1 dataset; no CI, no floor, no scramble.",
     1),
    ("exp_read_grow_oov_verb_extension_v1", "QUALIFIED", "WIRE_NARROWED",
     "Real residue: the morphology inverter.",
     "`OOV_VERB_BASE_LEX` HARDCODES munch->eats etc, and THE SAME TABLE GENERATES THE SENTENCE AND "
     "SCORES IT; coverage_current_pooled=0.0 by construction, so '+88.2pp' is a gain over a "
     "definitional zero. Its OOS control removed 0 items.", 1),
]


def write() -> int:
    LEDGER_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_JSONL, "w", encoding="utf-8", newline="") as fh:
        for cell, verdict, disp, finding, narrow, p in ROWS:
            fh.write(json.dumps({"cell": cell, "verdict": verdict, "disposition": disp,
                                 "finding": finding, "narrowing_or_rerun": narrow,
                                 "pass": p}, ensure_ascii=True) + "\n")
    c = collections.Counter(r[2] for r in ROWS)
    L = [__doc__.split("USAGE")[0].strip(), "",
         f"**{len(ROWS)} cells vetted.** "
         + " | ".join(f"{k} {v}" for k, v in sorted(c.items())), ""]
    for disp, title, blurb in (
        ("WIRE", "WIRE -- UPHELD, survives its own controls",
         "Promote and register. The claim stands as made."),
        ("WIRE_NARROWED", "WIRE_NARROWED -- QUALIFIED, real but narrower than claimed",
         "**Citable ONLY with the narrowing attached.** The narrowing is not a footnote; it is "
         "part of the result, and every one of these was claimed without it."),
        ("RERUN_NAMED", "RERUN_NAMED -- SUSPENDED, cannot be judged as it stands",
         "Not refuted. The named rerun would settle it."),
        ("SHELVED_REFUTED", "SHELVED_REFUTED -- DO NOT CITE",
         "If a figure from one of these is quoted anywhere, retire it there too -- that is how the "
         "3,544-concept number survived in the charter for weeks after being refuted."),
    ):
        rows = [r for r in ROWS if r[2] == disp]
        L += [f"## {title}  ({len(rows)})", "", blurb, ""]
        for cell, verdict, _d, finding, narrow, p in rows:
            L.append(f"### `{cell}`  <sub>pass {p}</sub>")
            L.append(f"{finding}")
            if narrow:
                key = "RERUN" if disp == "RERUN_NAMED" else "NARROWING (must travel with the number)"
                L.append(f"- **{key}:** {narrow}")
            L.append("")
    LEDGER_MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[ledger] {len(ROWS)} rows -> {LEDGER_MD} and {LEDGER_JSONL}")
    for k, v in sorted(c.items()):
        print(f"    {v:>3}  {k}")
    return 0


def summary() -> int:
    c = collections.Counter(r[2] for r in ROWS)
    v = collections.Counter(r[1] for r in ROWS)
    print(f"[ledger] {len(ROWS)} cells vetted")
    print("  by verdict:     " + ", ".join(f"{k} {n}" for k, n in v.most_common()))
    print("  by disposition: " + ", ".join(f"{k} {n}" for k, n in c.most_common()))
    return 0


def cite(name: str) -> int:
    for cell, verdict, disp, finding, narrow, p in ROWS:
        if cell == name or name in cell:
            print(f"=== {cell}\n  verdict     {verdict}\n  disposition {disp}\n  finding     {finding}")
            if disp == "SHELVED_REFUTED":
                print("  -> DO NOT CITE.")
            elif narrow:
                lbl = "RERUN NEEDED" if disp == "RERUN_NAMED" else "CITE ONLY WITH THIS ATTACHED"
                print(f"  -> {lbl}: {narrow}")
            else:
                print("  -> CITABLE AS CLAIMED.")
            return 0
    print(f"[ledger] '{name}' is NOT in the ledger -- it has not been vetted. "
          f"An unvetted HARD_PASS is an UNVERIFIED CLAIM: 30 vetted, 1 upheld.", file=sys.stderr)
    return 1


def main() -> int:
    if "--write" in sys.argv:
        return write()
    if "--summary" in sys.argv:
        return summary()
    if "--cite" in sys.argv:
        return cite(sys.argv[sys.argv.index("--cite") + 1])
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
