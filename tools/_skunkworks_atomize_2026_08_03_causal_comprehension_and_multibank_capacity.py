"""
A5-gated atomization: (1) causal-link comprehension HARD_PASS on real Anne of
Green Gables gold (fuller N=25 run), (2) multi-bank situation-model memory
capacity fix. AUDIT-ONLY (hdi_skunkworks). Independent .venv recompute off
data/exp_causal_link_comprehension_fuller_v2/metrics.json (per_item_records,
integration vs control split recomputed from item_type field, gates, distance
distribution) and data/exp_situation_model_multibank_capacity_v1/metrics.json
(per_unit array, summary_table_by_n_events), NOT off verdict_msg alone.

Writes TWO atoms (seq 29631-29632, both math corpus) + 2 matching
cert_ledger.jsonl entries, atomically (tmp -> os.replace) per file, then
verify-loads all files. LOCAL-ONLY: no origin push, no remote persist.
"""
import json
import os
import time
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATH_ATOMS_PATH = os.path.join(REPO, "data", "substrate_index", "math", "atoms.jsonl")
LEDGER_PATH = os.path.join(REPO, "data", "substrate_index", "meta", "cert_ledger.jsonl")

SEQ_CAUSAL = 29631
SEQ_MULTIBANK = 29632

ATOM_CAUSAL = {
    "atom_id": (
        "math::causal_link_comprehension_hard_pass_anne_n25_fuller_v2_organ_integration_"
        "0p9167_33of36_vs_most_recent_0p0000_control_0p9286_13of14_vs_most_recent_0p5714_"
        "random_near_chance_all_4_canfail_gates_held_gold_isolated_from_extraction_"
        "distance_genuinely_nonadjacent_median119_max6655_8of25_over500lines_kintsch_"
        "trabasso_causeeffect_metarole_bind_unbind_bundle_argmax_own_fhrr_organ_no_new_"
        "mechanism_no_borrowed_embedding_residual_0p083_bundleload2_cleanup_argmax_"
        "collision_capacity_signature_not_bug_gold_UNVERIFIED_pending_director_spotcheck_"
        "7b0598114_d0832a86b_MEASURED_MECHANISM_LOCAL_ONLY"
    ),
    "seq": SEQ_CAUSAL,
    "op": "insert",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "MEASURED_MECHANISM",
    "grade": "MM",
    "verdict": (
        "STORY-LEVEL CAUSAL COMPREHENSION on real narrative (Anne of Green Gables), "
        "brain-foundational (Kintsch construction-integration / Trabasso causal-network "
        "theory) implemented as CAUSE/EFFECT meta-role bind/unbind/bundle/cleanup-argmax "
        "on the existing FHRR situation-model organ (hdlab.situation_model_accumulate."
        "CausalLinkRegister, subclass of AccumulateRegister) -- NO new mechanism class, "
        "NO borrowed embeddings. Cell reports HARD_PASS; independent recompute off "
        "per_item_records confirms the headline numbers exactly. Distance is genuinely "
        "non-adjacent (median 119 lines, max 6655, 8/25 items >500 lines apart), so this "
        "is cross-context integration, not local-window lookup. Downgraded from the cell's "
        "own HARD_PASS label to MEASURED_MECHANISM for this atom because gold_verified=false "
        "(Director spot-check pending, esp. anne_causal_017/021/023) and this is a GOLD-"
        "ISOLATED organ measurement (fed gold events directly), not an end-to-end-from-raw-"
        "text score -- it isolates the comprehension organ from the ~14.5% coref/extraction "
        "error measured elsewhere in this arc (atom 29629), which is real but must not be "
        "silently folded into this number."
    ),
    "anchor": "causal_link_comprehension_fuller_v2",
    "anchor_name": "causal_link_comprehension_fuller_v2_2026_08_03",
    "cell": (
        "experiments/exp_causal_link_comprehension_fuller_v2.py; "
        "data/exp_causal_link_comprehension_fuller_v2/metrics.json; "
        "organ hdlab/situation_model_accumulate.py::CausalLinkRegister; "
        "commits 7b0598114 (N=25 scale-up), d0832a86b (pilot lineage, atom 29609)"
    ),
    "headline": (
        "On 25 causal-link items (18 require cross-context integration, 7 local-adjacent "
        "control) mined from real Anne of Green Gables text with a densified 697-event "
        "candidate pool (45 real gold events + 652 mined distractors, chance=0.0014): "
        "organ_accuracy_integration=0.9167 (33/36 cause_of+effect_of judgments) vs "
        "most_recent_accuracy_integration=0.0000 (collapses on non-adjacent items as "
        "expected) vs random_accuracy_integration=0.0000. organ_accuracy_control=0.9286 "
        "(13/14) vs most_recent_accuracy_control=0.5714 -- most_recent baseline clears its "
        "own control (as it must, since local-adjacent items are the regime it's good at), "
        "confirming this is a fair one-variable can-fail discriminator, not a rigged "
        "baseline. All 4 gates held: gate_mr_near_floor_integration, gate_mr_clears_control, "
        "gate_random_near_chance_integration/control. Bundle load stayed low (max=2 across "
        "5 entities with multiple bound facts); the residual 8.3% miss (3/36 judgments) is "
        "attributable to FHRR cleanup-argmax collisions at that bundle load, a genuine "
        "capacity signature (documented in bundling_collision_entities), not an "
        "implementation bug."
    ),
    "key_metrics": {
        "n_items_total": 25,
        "n_integration_items": 18,
        "n_control_items": 7,
        "n_unique_events": 697,
        "n_real_gold_events": 45,
        "n_distractor_events_mined": 652,
        "chance": 0.0014367816091954023,
        "organ_accuracy_integration": 0.9166666666666666,
        "organ_accuracy_integration_correct": 33,
        "organ_accuracy_integration_total": 36,
        "organ_accuracy_control": 0.9285714285714286,
        "organ_accuracy_control_correct": 13,
        "organ_accuracy_control_total": 14,
        "most_recent_accuracy_integration": 0.0,
        "most_recent_accuracy_control": 0.5714285714285714,
        "random_accuracy_integration": 0.0,
        "random_accuracy_control": 0.0,
        "gap_organ_vs_best_baseline_integration": 0.9166666666666666,
        "gate_mr_near_floor_integration": True,
        "gate_mr_clears_control": True,
        "gate_random_near_chance_integration": True,
        "gate_random_near_chance_control": True,
        "canfail_ok": True,
        "gate_hard_pass": True,
        "max_bundle_load_per_entity": 2,
        "n_entities_with_bundle_collision": 5,
        "distance_line_gap_min": 7,
        "distance_line_gap_p25": 46,
        "distance_line_gap_median": 119,
        "distance_line_gap_p75": 947,
        "distance_line_gap_max": 6655,
        "n_items_within_50_lines": 7,
        "n_items_over_500_lines": 8,
        "d": 1024,
    },
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "verified_off_data_note": (
        "Independent .venv recompute off data/exp_causal_link_comprehension_fuller_v2/"
        "metrics.json['per_item_records'] (25 records): split into integration (item_type "
        "!= 'local_adjacent_control', n=18) vs control (item_type == 'local_adjacent_"
        "control', n=7) by re-deriving item_type from the raw records rather than trusting "
        "the pre-aggregated summary fields; summed organ_effect_of_correct + organ_cause_of_"
        "correct across each split -> integration 33/36=0.91666... , control 13/14=0.92857... "
        "-- both reproduce metrics.json's organ_accuracy_integration/control byte-exact. Same "
        "recompute on most_recent_*_correct fields -> integration 0/36=0.0, matching. Gates "
        "block (gate_mr_near_floor_integration/gate_mr_clears_control/gate_random_near_chance_"
        "integration/control/canfail_ok/gate_hard_pass) read directly and all True/held. "
        "supporting_event_line_distance_distribution block reproduces min=7/p25=46/median=119/"
        "p75=947/max=6655/n_within_50=7/n_over_500=8 exactly. bundling_collision_entities has "
        "5 entries, max_bundle_load_per_entity=2, matching capacity_note. Cross-checked "
        "hdlab/situation_model_accumulate.py::CausalLinkRegister exists as a subclass of "
        "AccumulateRegister (not a new mechanism class) and git log confirms d0832a86b "
        "(pilot) precedes 7b0598114 (this N=25 scale-up) in the same lineage."
    ),
    "composes_seq": [29609, 29613, 29614, 29615, 29628, 29629],
    "corrects_seq": [],
    "amends_seq": [],
    "cert_delta": 0,
    "net_cert_delta": 0,
    "store_head_at_write": SEQ_CAUSAL - 1,
    "honest_scope": (
        "gold_verified=false on the gold_anne_comprehension_v2.jsonl source (Director "
        "spot-check pending; anne_causal_017/021/023 flagged in the task input as least-"
        "sure items) -- this atom preserves MEASURED_MECHANISM rather than the cell's own "
        "HARD_PASS label pending that spot-check. This is a GOLD-ISOLATED organ measurement "
        "(the cell feeds gold cause/effect events directly into the CausalLinkRegister), "
        "which correctly isolates the comprehension MECHANISM from the coref/extraction "
        "pipeline's own ~14.5% same-gender false-consolidation error (atom 29629) -- but "
        "that means this 91.7% number is NOT an end-to-end from-raw-text comprehension "
        "score and must not be quoted as one. The n_unique_events=697 candidate pool "
        "includes 652 mined raw-text distractor events (not hand-verified individually); "
        "the honest harness-design history is notable: the FIRST version of this cell "
        "HARD_FAILed its own can-fail gate on a sparse distractor pool (most_recent didn't "
        "clear control), and was fixed by densifying to n=697 total candidate events -- "
        "the can-fail gate then fired correctly, which is the intended discipline working "
        "(not evidence the discriminator is fragile, since it caught its own weakness "
        "before being trusted)."
    ),
    "framing_correction": (
        "Task input's HARD_PASS label is preserved as the cell's own verdict but this atom "
        "banks MEASURED_MECHANISM (not chain-grade PASS) because gold_verified is false. "
        "Also flags explicitly, per the task input's own honest framing, that this is "
        "comprehension-organ-scored (gold-isolated), not end-to-end reading accuracy -- "
        "the task input's phrase 'this is now large enough to treat as a scored capability "
        "claim' is accurate for the ORGAN but should not be read as an end-to-end claim."
    ),
    "revival_criteria": (
        "Promote to chain-grade once (a) Director spot-checks gold_anne_comprehension_v2."
        "jsonl (esp. anne_causal_017/021/023) and confirms gold_verified=true, and (b) an "
        "end-to-end-from-raw-text run (extraction+coref+causal-organ chained, not gold-fed) "
        "is measured to show the organ's 91.7% survives realistic upstream error propagation "
        "rather than being reported in isolation. The residual 8.3% cleanup-argmax miss at "
        "bundle_load=2 is a capacity signature worth tracking as bundle_load grows in a "
        "larger multi-book build (forward note in the source metrics.json's capacity_note "
        "already flags multibank as the swap-in if bundle_load exceeds 4)."
    ),
    "primitive_assessment": (
        "Competency #1 of the comprehension library past who-did-what role extraction: "
        "CAUSE/EFFECT causal-link inference implemented via the SAME bind/unbind/bundle/"
        "cleanup-argmax primitives already used for entity-role tracking (CausalLinkRegister "
        "is a subclass, not a new class of mechanism). Reusable pattern: any new relational "
        "construction (e.g. next: temporal sequencing, contrast, enablement) can plausibly "
        "reuse this same meta-role-register pattern rather than requiring bespoke machinery."
    ),
    "hf_attribution": "n/a (MEASURED_MECHANISM, not an HF cell).",
    "fairness_verdict": (
        "FAIR one-variable can-fail test: most_recent baseline clears its OWN control "
        "regime (0.5714 on local-adjacent items, which is its natural strength) while "
        "collapsing to 0.0 on the require-integration subset -- this is the correct shape "
        "for a can-fail discriminator (baseline isn't strawmanned across the board, only "
        "on the dimension the organ is claimed to add value on). Random stays near chance "
        "on both subsets. Symmetric anti-negativity applied: gold-unverified status and "
        "gold-isolation (not end-to-end) are both carried forward as scope limits rather "
        "than smoothed into an uncaveated HARD_PASS claim."
    ),
    "cross_arc_overlap": (
        "substrate_query.sh check (concept: 'causal cause effect meta-role bind unbind "
        "bundle argmax FHRR situation model comprehension') returns top hit at cosine=0.3418 "
        "(a planning note listing situation-model as a comprehension dimension, not a prior "
        "measured result) and a pre-reg note at cosine=0.3027 describing causal chains as "
        "composable from existing P10/P12 primitives conceptually -- neither is a prior "
        "MEASURED result at this scale/corpus; no rediscovery. Composes 29609 (situation-"
        "model accumulate organ, pilot lineage), 29613-29615 (earned coref + situation-"
        "model wiring), 29628-29629 (Anne extraction + consolidation hardening this arc). "
        "Also composes/contrasts with 29626 (McGuffey connective-cued causal-link "
        "collapse -- that negative used lexical-connective adjacency mining and correctly "
        "found no signal on McGuffey's simple prose; THIS atom uses plot-level cause/effect "
        "gold on genuinely harder Anne narrative and finds real cross-context signal, "
        "consistent rather than contradictory: different corpus, different mining method, "
        "different (harder) construction)."
    ),
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
}

ATOM_MULTIBANK = {
    "atom_id": (
        "math::multibank_situation_model_capacity_fix_v1_flat_accumulateregister_"
        "degrades_0p978_to_0p655_events64to256_multibank_nbanks_ge8_holds_ge0p999_"
        "reproduces_anne_decode_regression_magnitude_89p8_to_67p2_pct_qualitatively_"
        "NOT_independently_rerun_on_anne_data_deflated_canfail_fires_hp_flat_below0p85_"
        "hp_multibank_above0p95_arms_differ_verified_d512_not_d8192_chaingrade_envelope_"
        "working_memory_py_has_no_reusable_class_only_envelope_constants_plus_guards_"
        "multibankaccumulateregister_reimplemented_on_binding_bundling_primitives_"
        "8d5ae80e4_MEASURED_MECHANISM_TIERED_LOCAL_ONLY"
    ),
    "seq": SEQ_MULTIBANK,
    "op": "insert",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "MEASURED_MECHANISM",
    "grade": "MM",
    "verdict": (
        "CAPACITY-HEADROOM fix for the flat single-bundle situation-model memory wall: "
        "hdlab.situation_model_multibank.MultiBankAccumulateRegister routes each entity's "
        "events across n_banks independent FHRR sub-bundles via a deterministic content-"
        "anchored hash instead of one flat bundle. Independent recompute off the per_unit "
        "sweep (d=512, events/entity in [64,96,128,192,256], 5 seeds) confirms exactly: "
        "flat AccumulateRegister degrades 0.9781 (n=64) -> 0.6547 (n=256, mean across "
        "seeds), while multibank(n_banks=8) holds >=0.999 across the whole sweep (0.999 "
        "floor hit only at n=256, seed-mean 0.9992; n_banks=16 holds a clean 1.0000 "
        "throughout). Can-fail discriminator genuinely fires: HP_flat_degrade_below=0.85 "
        "trips at n=192 (flat mean 0.724) and n=256 (0.6547); HP_multibank_hold_above=0.95 "
        "holds for n_banks=8/16 at every sweep point. Arms independently verified as "
        "computing different values (not a stub), and the fair one-variable design (only "
        "the memory backend changes; d, n_events, seed, role_vocab matched) is confirmed "
        "against the cell's own DESIGN_NOTE."
    ),
    "anchor": "situation_model_multibank_capacity_v1",
    "anchor_name": "situation_model_multibank_capacity_v1_2026_08_03",
    "cell": (
        "experiments/exp_situation_model_multibank_capacity_v1.py; "
        "data/exp_situation_model_multibank_capacity_v1/metrics.json; "
        "hdlab/situation_model_multibank.py::MultiBankAccumulateRegister; "
        "commit 8d5ae80e4"
    ),
    "headline": (
        "Multi-bank sub-bundling fixes the FHRR situation-model capacity wall at d=512: "
        "flat decode-self-consistency 0.978 (n_events=64) -> 0.655 (n_events=256, mean "
        "of 5 seeds); n_banks>=8 holds decode accuracy >=0.999 across the same range. "
        "TIERED MEASURED_MECHANISM, NOT chain-grade: this cell runs at d=512, and the "
        "hdlab.working_memory envelope (k_per_bank>=64 @ N_DIM=8192, chain-grade-confirmed "
        "constants K_PER_BANK_CHAIN_GRADE_ARM=64, K_PER_BANK_DISCRIMINATING_REGIME_"
        "MINIMUM=64) does NOT numerically transfer to this FHRR complex64 measurement -- a "
        "d>=8192 confirmation cell is required before a formal chain-grade capacity claim "
        "can be made. Also note: hdlab/working_memory.py contains NO reusable class, only "
        "envelope constants (K_PER_BANK_CHAIN_GRADE_ARM, K_PER_BANK_BYCONSTRUCTION_"
        "THRESHOLD, K_PER_BANK_DISCRIMINATING_REGIME_MINIMUM) plus two guard functions "
        "(assert_k_per_bank_in_discriminating_regime, assert_chain_grade_envelope) -- "
        "MultiBankAccumulateRegister was reimplemented from scratch on hdlab.binding/"
        "hdlab.bundling primitives, it does not subclass or reuse anything from "
        "working_memory.py."
    ),
    "key_metrics": {
        "d": 512,
        "n_events_sweep": [64, 96, 128, 192, 256],
        "n_seeds": 5,
        "n_banks_arms": [4, 8, 16],
        "flat_mean_n64": 0.9781,
        "flat_mean_n96": 0.9042,
        "flat_mean_n128": 0.8391,
        "flat_mean_n192": 0.724,
        "flat_mean_n256": 0.6547,
        "multibank4_mean_n256": 0.9594,
        "multibank8_mean_n256": 0.9992,
        "multibank16_mean_n256": 1.0,
        "multibank8_min_across_sweep": 0.9992,
        "multibank16_min_across_sweep": 1.0,
        "hp_flat_degrade_below": 0.85,
        "hp_multibank_hold_above": 0.95,
        "canfail_flat_trips_at_n_events": 192,
        "canfail_multibank8_holds": True,
        "canfail_multibank16_holds": True,
        "working_memory_reusable_class_found": False,
        "anne_ledger_rerun_status": "NOT_FOUND_by_cell_itself",
    },
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "verified_off_data_note": (
        "Independent read of data/exp_situation_model_multibank_capacity_v1/metrics.json "
        "per_unit array (25 records: 5 n_events values x 5 seeds) and summary_table_by_"
        "n_events block -- both reproduce the verdict_msg's cited numbers exactly (flat "
        "0.9781->0.6547 sweep, multibank_16 1.0 throughout, multibank_8 reaching 0.9992 "
        "floor only at n=256). Independently cross-checked the HP_flat_degrade_below=0.85 / "
        "HP_multibank_hold_above=0.95 thresholds against config_version string and against "
        "the raw per_unit numbers: flat first drops below 0.85 at n_events=128 in individual "
        "seeds (0.828-0.859) and consistently at n=192/256 in the mean, multibank_8/16 never "
        "drop below 0.95 in any individual (n_events, seed) cell. arms_differ verified by "
        "inspecting raw per_unit scores dict -- flat/multibank_4/multibank_8/multibank_16 "
        "are 4 genuinely distinct numeric columns, not a stub returning identical values. "
        "Read hdlab/working_memory.py directly: grep for '^class ' returns ZERO matches -- "
        "confirms the cell's own claim that working_memory.py has no reusable class, only "
        "module-level constants (K_PER_BANK_CHAIN_GRADE_ARM=64, K_PER_BANK_BYCONSTRUCTION_"
        "THRESHOLD=32, K_PER_BANK_DISCRIMINATING_REGIME_MINIMUM=64) and guard functions "
        "assert_k_per_bank_in_discriminating_regime / assert_chain_grade_envelope. Read "
        "hdlab/situation_model_multibank.py directly: class MultiBankAccumulateRegister at "
        "line 65, and hdlab/situation_model_accumulate.py: class AccumulateRegister at line "
        "50 -- confirmed as separate classes (multibank does not subclass accumulate)."
    ),
    "composes_seq": [29609, 29613, 29614, 29615, 29628, 29629],
    "corrects_seq": [],
    "amends_seq": [],
    "cert_delta": 0,
    "net_cert_delta": 0,
    "store_head_at_write": SEQ_MULTIBANK - 1,
    "honest_scope": (
        "DEFLATED vs the task input's framing: the task input states this 'reproduces the "
        "Anne decode regression 89.8%->67.2%' (atom 29629's real measured Anne number). This "
        "audit checked the cell's own metrics.json and found the field "
        "'anne_ledger_rerun': 'NOT_FOUND: no Anne/consolidation_ledger/ch6-9-16 match in "
        "repo; skipped honestly' -- the cell EXPLICITLY did not rerun or connect to the Anne "
        "ledger data. The magnitude similarity (flat degrades 0.978->0.655 here vs Anne's "
        "89.8%->67.2%) is a QUALITATIVE / directional echo at best (same failure shape: flat-"
        "bundle capacity wall as event count per entity rises), not an independent "
        "reproduction of the Anne number, and this atom reports it that way rather than "
        "carrying the stronger 'reproduces' framing forward uncorrected. Separately, this is "
        "a d=512 synthetic capacity sweep (n_events per entity, not real narrative text), so "
        "the numbers characterize the FHRR mechanism's capacity envelope in the abstract, not "
        "the Anne pipeline's actual behavior post-fix (that would require rerunning Anne "
        "ch.1-3+ through MultiBankAccumulateRegister directly, not done here). Chain-grade "
        "claim explicitly blocked pending a d>=8192 confirmation cell per the source module's "
        "own REGIME-DISCRIMINATING-REGIME HONESTY docstring section."
    ),
    "framing_correction": (
        "DEFLATED: task input's claim 'reproduces the Anne decode regression 89.8%->67.2%' "
        "is corrected to 'qualitatively consistent in failure SHAPE with (not an independent "
        "numeric reproduction of) the Anne decode regression' -- the cell's own metrics.json "
        "explicitly flags anne_ledger_rerun=NOT_FOUND, meaning no actual cross-check against "
        "Anne data was performed by the cell itself. This atom preserves that honest gap "
        "rather than letting the coincidental magnitude similarity read as confirmed "
        "reproduction."
    ),
    "revival_criteria": (
        "(1) Run a d>=8192 confirmation sweep at the working_memory chain-grade-confirmed "
        "envelope (K_PER_BANK_CHAIN_GRADE_ARM=64) to test whether the n_banks>=8 capacity "
        "hold generalizes beyond d=512 before claiming chain-grade. (2) Directly rerun the "
        "actual Anne ch.1-3+ extraction/coref stream through MultiBankAccumulateRegister "
        "(swap-in for AccumulateRegister) and re-measure situation_model_decode_self_"
        "consistency to test whether it recovers from the measured 67.2% -- this is the real "
        "test of whether the capacity-headroom result actually fixes the Anne regression, and "
        "is explicitly NOT yet done."
    ),
    "primitive_assessment": (
        "New reusable primitive: hdlab.situation_model_multibank.MultiBankAccumulateRegister, "
        "a drop-in add_event/decode/entities replacement for AccumulateRegister that shards "
        "an entity's event history across n_banks FHRR sub-bundles via deterministic content-"
        "anchored hashing (stable_bank_id). Built directly on hdlab.binding/hdlab.bundling "
        "primitives (bind/bundle/cleanup), same primitive class as the causal-link organ "
        "(atom 29631) -- reinforcing that capacity scaling in this substrate is handled by "
        "adding banks/sub-bundles, not by inventing new binding math."
    ),
    "hf_attribution": "n/a (MEASURED_MECHANISM, not an HF cell).",
    "fairness_verdict": (
        "FAIR one-variable test confirmed (memory backend is the only swapped variable at "
        "matched d/n_events/seed/role_vocab per the cell's own DESIGN_NOTE, independently "
        "spot-checked in per_unit records). Symmetric anti-negativity applied: this atom "
        "actively DEFLATES the task input's overstated 'reproduces the Anne regression' claim "
        "to a qualitative-consistency framing based on the cell's own honest anne_ledger_"
        "rerun=NOT_FOUND field, rather than propagating the stronger claim forward uncaveated."
    ),
    "cross_arc_overlap": (
        "substrate_query.sh check (same causal/situation-model concept query used for atom "
        "29631) returns no prior MEASURED capacity-sweep result for multi-bank FHRR memory "
        "at this scale; genuinely novel measurement. Composes with 29609 (situation-model "
        "accumulate organ pilot lineage) and 29628-29629 (the actual Anne decode-self-"
        "consistency regression this capacity fix is MOTIVATED by, per the source commit "
        "message, though not yet independently reconnected -- see honest_scope/revival_"
        "criteria)."
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

    for atom in (ATOM_CAUSAL, ATOM_MULTIBANK):
        atom["ts"] = now
        atom["ts_iso"] = ts_iso
        atom["ts_day"] = ts_day

    ledger_causal = make_ledger_entry(
        SEQ_CAUSAL, ATOM_CAUSAL, "math",
        "MEASURED_MECHANISM CERT +0 (causal-link comprehension organ, gold-isolated, "
        "gold-unverified). Independent recompute off per_item_records reproduces exactly: "
        "organ_accuracy_integration=33/36=0.9167, organ_accuracy_control=13/14=0.9286, "
        "most_recent_accuracy_integration=0.0, all 4 can-fail gates held, distance median "
        "119 lines / max 6655 / 8 of 25 items over 500 lines apart (genuinely non-adjacent). "
        "Downgraded from cell's own HARD_PASS to MEASURED_MECHANISM pending Director "
        "gold-verification spot-check; flagged as gold-isolated (organ score, not "
        "end-to-end-from-raw-text).",
        "AUDIT-ONLY (hdi_skunkworks) independent .venv recompute off "
        "data/exp_causal_link_comprehension_fuller_v2/metrics.json per_item_records, NOT "
        "off verdict_msg summary alone. Commits 7b0598114, d0832a86b. LOCAL-ONLY.",
    )
    ledger_multibank = make_ledger_entry(
        SEQ_MULTIBANK, ATOM_MULTIBANK, "math",
        "MEASURED_MECHANISM CERT +0 (tiered capacity-headroom fix, not chain-grade -- "
        "d=512 below working_memory's d>=8192 chain-grade envelope). Independent recompute "
        "off per_unit sweep reproduces exactly: flat 0.9781(n=64)->0.6547(n=256), "
        "multibank(n_banks=8) floor 0.9992 at n=256, multibank(n_banks=16) holds 1.0000 "
        "throughout, can-fail thresholds (flat<0.85, multibank>0.95) fire/hold correctly. "
        "DEFLATED the task input's 'reproduces the Anne decode regression 89.8%->67.2%' "
        "claim to 'qualitatively consistent in failure shape, NOT independently "
        "reproduced' -- the cell's own metrics.json field anne_ledger_rerun=NOT_FOUND "
        "confirms no actual Anne-data cross-check was performed. Confirmed "
        "hdlab/working_memory.py has zero classes (only envelope constants + guard "
        "functions) and MultiBankAccumulateRegister was built fresh on binding/bundling "
        "primitives, not reused from working_memory.py.",
        "AUDIT-ONLY (hdi_skunkworks) independent .venv recompute off "
        "data/exp_situation_model_multibank_capacity_v1/metrics.json per_unit array, plus "
        "direct source read of hdlab/working_memory.py and hdlab/situation_model_multibank.py "
        "to verify the no-reusable-class claim. Commit 8d5ae80e4. LOCAL-ONLY.",
    )

    # A5-gate: atomic write, math atoms, then ledger entries.
    atomic_append_jsonl(MATH_ATOMS_PATH, ATOM_CAUSAL)
    atomic_append_jsonl(MATH_ATOMS_PATH, ATOM_MULTIBANK)

    atomic_append_jsonl(LEDGER_PATH, ledger_causal)
    atomic_append_jsonl(LEDGER_PATH, ledger_multibank)

    # Verify-load + integrity check
    results = []
    for path, seq, atom_id in (
        (MATH_ATOMS_PATH, SEQ_CAUSAL, ATOM_CAUSAL["atom_id"]),
        (MATH_ATOMS_PATH, SEQ_MULTIBANK, ATOM_MULTIBANK["atom_id"]),
    ):
        found, count = verify_load(path, expect_seq=seq, expect_atom_id=atom_id)
        assert found, f"FAIL: atom seq={seq} not found in {path} after write"
        results.append((path, seq, count))

    for seq in (SEQ_CAUSAL, SEQ_MULTIBANK):
        found, count = verify_load(LEDGER_PATH, expect_seq=seq)
        assert found, f"FAIL: ledger entry seq={seq} not found in {LEDGER_PATH} after write"

    for path, seq, count in results:
        print(f"OK: atom seq={seq} written to {path} ({count} total lines)")
    print(f"OK: 2 ledger entries written to {LEDGER_PATH}")
    print("atom_ids:")
    for atom in (ATOM_CAUSAL, ATOM_MULTIBANK):
        print(f"  seq={atom['seq']} corpus={atom['corpus']} -> {atom['atom_id'][:100]}...")


if __name__ == "__main__":
    main()
