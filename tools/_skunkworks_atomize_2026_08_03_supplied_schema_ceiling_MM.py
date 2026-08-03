"""
A5-gated atomization: fork-(b) supplied Schank-Abelson/Trabasso event-schema ceiling
measurement (MEASURED_MECHANISM). AUDIT-ONLY (hdi_skunkworks).

Independent recompute: fresh .venv rerun of experiments/exp_supplied_schema_ceiling_v1.py
(deterministic, seed=20260803) reproduces data/exp_supplied_schema_ceiling_v1/metrics.json
byte-for-byte except elapsed_s/ts_iso timing fields. Cross-checked raw unstated_goal_recovery,
pairing_recovery_goal_mediated_9, end_to_end, and overfit_guard blocks directly (NOT
verdict_msg/summary alone). Also independently confirmed off data/eval_gold_mention_role_
mcguffey_v1/gold_anne_goal_intention_v1.jsonl that only 3 (not 4) gold items are
explicit_vs_inferred=="inferred" (anne_goal_014/016/019), and that anne_goal_014's verbatim
is the paraphrase "I don't think you are a fit little girl for Diana to associate with" with
no lexical desiderative marker -- confirming the schema-miss characterization directly from
the gold text, not merely citing the cell's own claim.

Writes ONE atom (seq 29643, math corpus) + 1 matching cert_ledger.jsonl entry, atomically
(tmp -> os.replace), then verify-loads both files. LOCAL-ONLY: no origin push, no remote
persist.
"""
import json
import os
import time
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATH_ATOMS_PATH = os.path.join(REPO, "data", "substrate_index", "math", "atoms.jsonl")
LEDGER_PATH = os.path.join(REPO, "data", "substrate_index", "meta", "cert_ledger.jsonl")

SEQ_SUPPLIED_SCHEMA_CEILING = 29643

ATOM_SUPPLIED_SCHEMA_CEILING = {
    "atom_id": (
        "math::supplied_schema_ceiling_v1_22_schank_abelson_trabasso_event_schemas_"
        "20_real_2_control_unstated_goal_recovery_2of3_recovered_rescue_gratitude_"
        "confession_missed_goal014_fit_little_girl_paraphrase_regex_brittleness_"
        "pairing_5of9_endtoend_insample_recall_0p52_fp_0p04_mandatory_overfit_guard_"
        "two_50_50_splits_max_gap_0p52_OVERFIT_FLAGGED_honest_outofsample_ceiling_"
        "0p25_worst_of_4_halves_2x_content_overlap_cap_0p11_still_far_below_needed_"
        "fork_landscape_finding_neither_earned_cheap_nor_supply_schema_alone_works_"
        "last_mile_relation_inference_needs_deep_content_aware_67c0ed3c9_"
        "MEASURED_MECHANISM_LOCAL_ONLY"
    ),
    "seq": SEQ_SUPPLIED_SCHEMA_CEILING,
    "op": "insert",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "MEASURED_MECHANISM",
    "grade": "MM",
    "verdict": (
        "FORK-(b) SUPPLIED-SCHEMA CEILING, INDEPENDENTLY RE-RUN AND CONFIRMED (not merely read "
        "from the file's own verdict). A hand-authored library of 22 Schank-Abelson script-theory "
        "/ Trabasso goal-plan event-schemas (20 real narrative-type schemas + 2 control schemas, "
        "GET_DRESSED_SCRIPT and RESTAURANT_SCRIPT, included specifically to catch spurious over-"
        "firing) was applied to director-verified gold (gold_anne_comprehension_v3, gold_anne_"
        "goal_intention_v1) to test whether SUPPLIED (allowed-DATA, not gold-derived) schema "
        "knowledge alone can recover unstated goals and propose satisfy/cause causal links, as a "
        "cheaper alternative to earned deep semantic-relation inference. A FRESH independent "
        ".venv rerun of experiments/exp_supplied_schema_ceiling_v1.py this pass reproduces data/"
        "exp_supplied_schema_ceiling_v1/metrics.json byte-for-byte (diffing only elapsed_s/ts_iso "
        "timing fields) -- confirms full determinism, not a one-off artifact. RESULTS (all read "
        "off the raw per-item blocks, not the verdict_msg/summary alone): (1) UNSTATED-GOAL "
        "RECOVERY 2/3 (0.667) on the N=3 gold items with explicit_vs_inferred=='inferred' -- "
        "independently confirmed off the gold file itself that only 3 such items exist (anne_"
        "goal_014/016/019, NOT 4 as the cell's own docstring aspirationally listed before the "
        "gold set was finalized -- a minor internal-inconsistency catch, immaterial to the "
        "measured numbers since the metrics.json's own n_inferred_gold=3 is what was actually "
        "computed). RECOVERED: anne_goal_016 (RESCUE_GRATITUDE) and anne_goal_019 (CONFESSION_"
        "UNDER_CONFINEMENT). MISSED: anne_goal_014 (Mrs. Barry's prohibition, 'I don't think you "
        "are a fit little girl for Diana to associate with') -- independently confirmed off the "
        "gold file itself that this schema-relevant scenario (a prohibition/reconciliation-type "
        "narrative, matching schema PROHIBITION_RECONCILIATION which DID fire on the semantically "
        "adjacent but differently-worded anne_goal_018) failed to fire here purely on regex-"
        "pattern non-match against this specific paraphrase -- a genuine BRITTLENESS finding "
        "(schema TYPE existed in the library; the trigger regex did not generalize to this "
        "phrasing), not a missing-schema gap. (2) SATISFY/CAUSE PAIRING recall 5/9 (0.556) on "
        "the goal-mediated causal-link subset (schema-coherent open+close pairing, i.e. the SAME "
        "schema id must fire on both the cause_event and effect_event sides). (3) END-TO-END "
        "in-sample recall_all_25=0.52, fp_rate=0.04 (8/200 seeded negative cross-pairs) -- clearly "
        "above the content-overlap CAP (0.11) and disk_baseline_recall_goal_mediated (0.1111) if "
        "taken at face value. (4) MANDATORY OVERFIT GUARD (the load-bearing discipline of this "
        "cell): two independent seeded 50/50 splits of the 25 causal items gave recall_half_a/"
        "half_b = 0.25/0.769 (split 1) and 0.583/0.462 (split 2) -- max_gap_all_25=0.519, WELL "
        "ABOVE the cell's own 0.30 overfit-flag threshold -> OVERFIT_DETECTED. The HONEST ceiling "
        "is therefore the WORST of all 4 half-splits = 0.25, NOT the in-sample 0.52 -- a ~2x "
        "inflation from overfitting a fixed, hand-authored 22-schema library against a small "
        "(N=25) gold set that the schema-author had necessarily read in full (the cell's own "
        "docstring discloses this blinding limitation plainly; the split-based guard is the real "
        "defense, not authoring order alone). 0.25 is still roughly 2x the content-overlap cap "
        "(0.11) and the disk baseline (0.1111), so supplied schemas ARE a genuine, if modest, "
        "improvement over pure lexical/content-overlap baselines -- but 0.25 recall is far below "
        "what an end-to-end comprehension pipeline needs. LANDSCAPE FINDING: this closes the "
        "fork-(b) question honestly -- supplied Schank-Abelson/Trabasso schema DATA alone caps "
        "out around 0.25 out-of-sample and is genuinely paraphrase-brittle (regex triggers do "
        "not generalize across phrasings of the same narrative type); combined with atom 29642's "
        "falsification of the fork-(a) coherence-margin transplant (structural-identity signal "
        "cannot discriminate relation CONTENT), the honest cross-fork conclusion is that NEITHER "
        "cheap path (earned-cheap structural signal, nor supplied schema-data) substitutes for "
        "DEEP, CONTENT-AWARE semantic-relation inference on the last-mile unstated-goal / "
        "satisfy-thwart-cause discrimination problem."
    ),
    "anchor": "supplied_schema_ceiling_v1",
    "anchor_name": "supplied_schema_ceiling_v1_2026_08_03",
    "cell": (
        "experiments/exp_supplied_schema_ceiling_v1.py; "
        "data/exp_supplied_schema_ceiling_v1/metrics.json; "
        "data/schemas/event_schema_library_v1.json (22 schemas, 20 real + 2 control); "
        "commits afa12fdd7 (schema library force-add) + 67c0ed3c9 (measurement cell)"
    ),
    "headline": (
        "Supplied 22-schema (Schank-Abelson/Trabasso) event-schema library measured against "
        "director-verified Anne gold for unstated-goal recovery (2/3), satisfy/cause pairing "
        "(5/9), and end-to-end causal-link recall (in-sample 0.52, fp 0.04). MANDATORY overfit "
        "guard (two seeded 50/50 splits) FLAGGED overfitting (max gap 0.52) -> HONEST out-of-"
        "sample ceiling = 0.25 (worst of 4 halves), ~2x the content-overlap cap (0.11) but far "
        "below what's needed. MISSED goal_014 is a genuine paraphrase-regex brittleness (schema "
        "existed, trigger didn't generalize). VERDICT: supply-schema alone caps ~0.25 out-of-"
        "sample and doesn't reliably generalize -- closes the fork-(b) question. Combined with "
        "29642 (fork-a coherence-margin falsification): neither cheap path substitutes for deep "
        "content-aware semantic-relation inference on unstated-goal / satisfy-thwart-cause."
    ),
    "key_metrics": {
        "n_schemas": 22,
        "n_schemas_real": 20,
        "n_schemas_control": 2,
        "recall_unstated_goal": 0.6666666666666666,
        "n_inferred_gold": 3,
        "recall_goal_mediated_pairing": 0.5555555555555556,
        "n_goal_mediated_pairing": 9,
        "recall_end_to_end_all_25_insample": 0.52,
        "recall_end_to_end_all_25_out_of_sample_honest_ceiling": 0.25,
        "fp_rate_end_to_end_insample": 0.04,
        "max_overfit_gap_all_25": 0.5192307692307693,
        "overfit_detected": True,
        "content_overlap_cap": 0.11,
        "disk_baseline_recall_goal_mediated": 0.1111111111111111,
        "disk_baseline_fp": 0.0,
        "random_uniform_control_recall": 0.012077294685990338,
        "missed_unstated_goal_item": "anne_goal_014",
        "missed_reason": "paraphrase_regex_brittleness_schema_type_existed",
    },
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "verified_off_data_note": (
        "Independently RE-RAN the cell fresh (.venv/Scripts/python.exe experiments/exp_supplied_"
        "schema_ceiling_v1.py, after backing up the original metrics.json) and diffed the "
        "regenerated data/exp_supplied_schema_ceiling_v1/metrics.json against the backup: "
        "identical in every field except elapsed_s and ts_iso -- full determinism confirmed, not "
        "assumed. Also ran --self-test mode fresh, SELF_TEST_PASS. Independently read the raw "
        "unstated_goal_recovery.inferred_hits array (anne_goal_014 fired=false schema_ids=[], "
        "anne_goal_016 fired=true RESCUE_GRATITUDE, anne_goal_019 fired=true CONFESSION_UNDER_"
        "CONFINEMENT) giving 2/3=0.6667 -- reproduces the file's recall_unstated_goal exactly. "
        "Independently read pairing_recovery_goal_mediated_9.per_item (5/9 flagged: anne_causal_"
        "001/003/004/005/017) -- reproduces recall=0.5556 exactly. Independently read end_to_end."
        "per_item (13/25 flagged) -- reproduces recall_all_25=0.52 exactly. Independently read "
        "overfit_guard block: split_all_25_seed_offset_1 (0.25/0.769), split_all_25_seed_offset_2 "
        "(0.583/0.462) -- max_gap_all_25=0.519 (computed independently as abs(0.25-0.769)=0.519 "
        "and abs(0.583-0.462)=0.121, max=0.519) matches file exactly; honest_ceiling_recall_all_"
        "25_worst_of_4_halves=min(0.25,0.769,0.583,0.462)=0.25 -- recomputed and matches. "
        "Independently queried data/eval_gold_mention_role_mcguffey_v1/gold_anne_goal_intention_"
        "v1.jsonl directly: grep confirms exactly 3 items have explicit_vs_inferred=='inferred' "
        "(not 4, correcting the cell docstring's own aspirational list of 4 ids written before "
        "gold finalization) and confirmed anne_goal_014's verbatim text ('I don't think you are "
        "a fit little girl for Diana to associate with') matches the reported paraphrase "
        "characterization directly from the gold file, not merely from the cell's claim. Read "
        "experiments/exp_supplied_schema_ceiling_v1.py source directly: confirmed pair_flagged() "
        "requires the SAME schema id to fire open-side and close-side (schema-coherent pairing, "
        "not any-open+any-close), and confirmed the overfit-flag threshold (>=0.30 for all_25, "
        ">=0.50 for the tiny goal_mediated_9 subset) is applied correctly given the measured "
        "gaps. Confirmed arms_differ_verified=True via independent digest comparison of the "
        "schema-flagged pair set vs the baseline (exp_goal_register_causal_link_v1) flagged set. "
        "Cross-checked git log: commits afa12fdd7 and 67c0ed3c9 both present in repo history."
    ),
    "composes_seq": [29634, 29639, 29640, 29642],
    "corrects_seq": [],
    "amends_seq": [],
    "cert_delta": 0,
    "net_cert_delta": 0,
    "store_head_at_write": SEQ_SUPPLIED_SCHEMA_CEILING - 1,
    "honest_scope": (
        "Unstated-goal recovery is N=3, heavily underpowered for a probabilistic claim -- 2/3 "
        "is reported plainly as a small-N number, not generalized. The 0.25 out-of-sample "
        "ceiling itself comes from only 2 independent 50/50 splits of a 25-item gold set (12-13 "
        "items/half) -- noisy but the primary overfit signal per the cell's own design; the "
        "goal_mediated_9 subset splits (N=4-5/half) are explicitly non-load-bearing per the "
        "cell's own caveat, reported but not counted toward the headline ceiling. The schema "
        "library's author read the gold files in full during this cell's design (disclosed "
        "plainly in the cell's own docstring) -- strict textual blinding was not achieved; the "
        "overfit-guard split is the actual defense against this, and it did its job (caught a "
        "genuine 0.52->0.25 gap). This atom does NOT claim supplied schemas are useless -- 0.25 "
        "out-of-sample is a real ~2x lift over the content-overlap cap (0.11) -- only that it is "
        "insufficient on its own and brittle to paraphrase."
    ),
    "framing_correction": (
        "Enforces the task instruction's explicit framing: the IN-SAMPLE 0.52 end-to-end recall "
        "is NOT the number to cite going forward -- the OVERFIT-GUARDED, worst-of-4-halves "
        "OUT-OF-SAMPLE 0.25 is the load-bearing ceiling, and this atom's key_metrics/headline/"
        "verdict fields lead with 0.25, not 0.52, to prevent the in-sample number from being "
        "later miscited as the capability ceiling. Additionally corrects a minor internal "
        "inconsistency in the cell's own docstring (which names 4 candidate inferred-goal ids "
        "including anne_goal_018) against the actual finalized gold file and the cell's own "
        "computed n_inferred_gold=3 -- the 3-item computation is what is banked here, the 4-id "
        "docstring list was pre-finalization scaffolding, not a discrepancy in the measured "
        "result itself."
    ),
    "revival_criteria": (
        "(1) Fix the anne_goal_014-class brittleness by testing schema triggers against a wider "
        "paraphrase corpus (or a learned/fuzzy trigger match instead of literal regex) before "
        "re-measuring unstated-goal recall on an expanded inferred-goal gold set (N=3 is too "
        "small to trust a fixed number either way). (2) Given both fork-(a) (coherence-margin, "
        "atom 29642) and fork-(b) (supplied schema, this atom) are now closed as insufficient "
        "alone, the honest next investment per the composed frontier-synthesis (atom 29640) is "
        "either (a) wiring supplied schemas AS INPUT SIGNAL to a deeper content-aware inference "
        "mechanism (schemas propose CANDIDATES; a real relation-content classifier/register "
        "discriminates among them) rather than treating schema-firing as the final answer, or "
        "(b) the deeper Kintsch-CI construction-integration idea (design doc Section 1, "
        "explicitly NOT falsified by 29642's fork-a negative)."
    ),
    "primitive_assessment": (
        "No new glass-box primitive; this is a MEASUREMENT of an existing allowed-DATA artifact "
        "(the hand-authored schema library) against the standing gold set, with a genuinely "
        "reusable METHODOLOGY: any supplied-knowledge-library capability claim on a small gold "
        "set MUST run the two-independent-seeded-50/50-split overfit guard before quoting an "
        "in-sample number, and must report the worst-of-splits number as the honest ceiling when "
        "the guard fires. This generalizes beyond schemas to any small-N supplied-data ceiling "
        "measurement in this arc."
    ),
    "hf_attribution": (
        "n/a (MEASURED_MECHANISM, a proven CAP/boundary, not a HARD_FAIL). The overfit guard "
        "correctly fired as designed (positive-control-equivalent: it is SUPPOSED to detect "
        "instability and did) -- this is the discipline working correctly, not a test-design "
        "failure."
    ),
    "fairness_verdict": (
        "FAIR, symmetric anti-negativity applied: the in-sample 0.52 recall was NOT allowed to "
        "stand as the headline despite being the more flattering number -- the overfit-guarded "
        "0.25 out-of-sample ceiling is what this atom banks as load-bearing, an honest downward "
        "correction applied with the same rigor as any upward claim would receive. Symmetrically, "
        "the 0.25 ceiling is not deflated below its real value either: it is correctly noted as "
        "~2x the content-overlap cap (0.11), a genuine (if insufficient) improvement, not "
        "dismissed as noise. All cited numbers independently reproduce off a fresh, from-scratch "
        ".venv rerun of the cell (not merely off the existing metrics.json file), which is a "
        "stronger verification bar than reading the file alone."
    ),
    "cross_arc_overlap": (
        "substrate_query.sh check ('event schema script satisfy thwart cause goal inference "
        "relation supplied schema ceiling overfit') returns top hits at cosine<=0.3564: generic "
        "'Schema'/'schema' concept-node entries (WordNet/concept corpus, cosine=0.3564), a prior "
        "hippocampal-schema-integration MWP research-drill note (cosine=0.3291-0.3213, a "
        "DIFFERENT domain -- math word-problem operand-role templates via schema retrieval, not "
        "narrative event-schema relation inference), and 'schematisation' (WordNet, cosine="
        "0.3174). No prior arc cell builds a supplied Schank-Abelson/Trabasso event-schema "
        "library or measures in/out-of-sample recall on these specific Anne gold causal/goal "
        "links -- confirmed novel, not a rediscovery. Composes directly with 29634 (the cheap-"
        "signal probe that named goal/intention tracking as the next lever), 29639 (the goal-"
        "close-pairing semantic CAP that named satisfy-vs-restate discrimination as the residual), "
        "29640 (the frontier-synthesis naming semantic-relation inference as the deep frontier), "
        "and 29642 (the fork-a coherence-margin falsification this atom's fork-b closes out the "
        "other half of)."
    ),
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
}


def atomic_append_jsonl(path, record):
    line = json.dumps(record, ensure_ascii=True) + "\n"
    dir_ = os.path.dirname(path)
    with open(path, "rb") as f:
        existing = f.read()
    fd, tmp_path = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(existing)
            tmp.write(line.encode("utf-8"))
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def verify_load(path, expect_seq=None, expect_atom_id=None):
    found = False
    count = 0
    with open(path, "rb") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            count += 1
            d = json.loads(raw.decode("utf-8"))
            if expect_seq is not None and d.get("seq") == expect_seq:
                found = True
            if expect_atom_id is not None and d.get("atom_id") == expect_atom_id:
                found = True
    return found, count


def make_ledger_entry(seq, atom, corpus, decision, note):
    now = time.time()
    return {
        "seq": seq,
        "atom_id": atom["atom_id"],
        "corpus": corpus,
        "decision": decision,
        "note": note,
        "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True,
        "ts": now,
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%S.000000+00:00", time.gmtime(now)),
        "ts_day": time.strftime("%Y-%m-%d", time.gmtime(now)),
    }


def main():
    now = time.time()
    ts_iso = time.strftime("%Y-%m-%dT%H:%M:%S.000000+00:00", time.gmtime(now))
    ts_day = time.strftime("%Y-%m-%d", time.gmtime(now))

    ATOM_SUPPLIED_SCHEMA_CEILING["ts"] = now
    ATOM_SUPPLIED_SCHEMA_CEILING["ts_iso"] = ts_iso
    ATOM_SUPPLIED_SCHEMA_CEILING["ts_day"] = ts_day

    ledger_entry = make_ledger_entry(
        SEQ_SUPPLIED_SCHEMA_CEILING, ATOM_SUPPLIED_SCHEMA_CEILING, "math",
        "MEASURED_MECHANISM CERT +0 (fork-b supplied event-schema ceiling). Independent FRESH "
        ".venv rerun of experiments/exp_supplied_schema_ceiling_v1.py reproduces data/exp_"
        "supplied_schema_ceiling_v1/metrics.json byte-for-byte except timing fields. Unstated-"
        "goal recovery 2/3 (RESCUE_GRATITUDE, CONFESSION_UNDER_CONFINEMENT recovered; anne_"
        "goal_014 missed -- confirmed paraphrase-regex brittleness against the gold text "
        "directly, schema type existed). Pairing 5/9. End-to-end IN-SAMPLE recall 0.52 fp 0.04 "
        "-- BUT mandatory overfit guard (two seeded 50/50 splits) flagged overfitting (max gap "
        "0.519 >= 0.30 threshold) -> HONEST OUT-OF-SAMPLE CEILING = 0.25 (worst of 4 halves), "
        "the load-bearing number, not 0.52. ~2x content-overlap cap (0.11) but far below what's "
        "needed. Closes the fork-b question: supply-schema alone insufficient + paraphrase-"
        "brittle; combined with 29642 (fork-a falsification), neither cheap path substitutes "
        "for deep content-aware semantic-relation inference.",
        "AUDIT-ONLY (hdi_skunkworks) independent recompute via FRESH .venv rerun of the cell "
        "(not merely reading the existing metrics.json), diffed byte-for-byte against backup "
        "(identical except elapsed_s/ts_iso); plus direct gold-file query confirming N=3 "
        "inferred-goal items and anne_goal_014's exact paraphrase text. Commits afa12fdd7 + "
        "67c0ed3c9. LOCAL-ONLY.",
    )

    atomic_append_jsonl(MATH_ATOMS_PATH, ATOM_SUPPLIED_SCHEMA_CEILING)
    atomic_append_jsonl(LEDGER_PATH, ledger_entry)

    found, count = verify_load(
        MATH_ATOMS_PATH,
        expect_seq=SEQ_SUPPLIED_SCHEMA_CEILING,
        expect_atom_id=ATOM_SUPPLIED_SCHEMA_CEILING["atom_id"],
    )
    assert found, f"FAIL: atom seq={SEQ_SUPPLIED_SCHEMA_CEILING} not found in {MATH_ATOMS_PATH} after write"

    found_ledger, ledger_count = verify_load(LEDGER_PATH, expect_seq=SEQ_SUPPLIED_SCHEMA_CEILING)
    assert found_ledger, f"FAIL: ledger entry seq={SEQ_SUPPLIED_SCHEMA_CEILING} not found in {LEDGER_PATH} after write"

    print(f"OK: atom seq={SEQ_SUPPLIED_SCHEMA_CEILING} written to {MATH_ATOMS_PATH} ({count} total lines)")
    print(f"OK: ledger entry written to {LEDGER_PATH} ({ledger_count} total lines)")
    print("atom_id:")
    print(f"  seq={ATOM_SUPPLIED_SCHEMA_CEILING['seq']} corpus={ATOM_SUPPLIED_SCHEMA_CEILING['corpus']} -> {ATOM_SUPPLIED_SCHEMA_CEILING['atom_id'][:120]}...")


if __name__ == "__main__":
    main()
