"""
A5-gated atomize: LANDED-VET of exp_cortex2_provenance_faithfulness_and_calibrated_refuse_v1.
  Director framed HARD_PASS / "first POSITIVE payoff of the glass-box cortex" / decisive go/no-go.
  Skunkworks honest deflated tier: MM_TENTATIVE (measured mechanism; genuine differentiator EXISTS
  but is NARROWER than the faithfulness-0.798 headline and the easy-regime magnitudes are inflated).

CELL: experiments/exp_cortex2_provenance_faithfulness_and_calibrated_refuse_v1.py
ANCHOR: cortex2_provenance_faithfulness_and_calibrated_refuse_v1
METRICS: data/exp_cortex2_provenance_faithfulness_and_calibrated_refuse_v1/metrics.json
COMMIT (Director-cited): c01aadabe
SEEDS: [7,13,19] FULL (N=4096, max_triples=6000, nq_ans=nq_unans=120)

OFF-DISK INDEPENDENT VERIFICATION (this session):
  (1) Full deterministic RE-RUN reproduces BIT-EXACT (all 3 seeds): faith_cortex 0.789/0.813/0.791,
      recall 0.975/0.983/0.933, auroc 1.000, refuse_p 1.000 -- identical to landed metrics.json.
  (2) All 16 agg fields re-aggregate from per_seed to <1e-9.
  (3) faithfulness = flip_rate_cited - flip_rate_noncited confirmed per seed (cortex + bb).
  (4) cross-seed cv: faithfulness_cortex 1.37%, answerable_recall 2.27%, chain_completeness 0.00%.

WHAT REPRODUCES (Director spot-check values all confirmed off-disk):
  faithfulness_cortex 0.798 (std 0.011) vs bb 0.523 ; chain_completeness 1.0 vs 0.510 ;
  flip_noncited 0.202 ; conf_auroc 1.0 ; refuse_precision_unans 1.0 vs bb 0.0 ;
  answerable_recall 0.964 vs shortcut 0.019 vs bb 0.964 ; answerable_retention 0.842.

HONEST TIER REASONING (why MM_TENTATIVE, not the HARD_PASS-implied CG):
  The cell legitimately PASSES its pre-registered gates (I do not dispute the HARD_PASS verdict against
  ITS gates). But as a CERT atom the honest tier is MM_TENTATIVE because the DECISIVE metric is
  partly by-construction and the head-to-head is confounded:

  A. faithfulness_cortex=0.798 is DOMINATED by flip_cited=1.000, which is ~by-construction for a glass
     box: the cortex answer IS computed from the cited path edges (exact linear shard subtraction ->
     ablating a load-bearing edge necessarily changes the hop argmax; the cell's own selftest asserts
     this). The only genuinely MEASURED (not by-construction) component is flip_noncited=0.202 -- the
     cross-talk leakage where ablating a NON-cited edge still flips the answer 20% of the time (the
     superposition is not perfectly insensitive to non-cited terms). So 0.798 = 1.000(by-construction)
     - 0.202(measured leakage).
  B. The head-to-head faithfulness gap (0.798 vs 0.523) is CONFOUNDED by the black-box's citation
     POLICY, not a soundness law. bb cites top-3 s-edges (2 of which are decorative siblings), diluting
     bb_flip_cited to ~0.76. A smarter black-box citing only its top-1 (fact1) would match the cortex on
     hop1 faithfulness. The CELL AUTHOR HONESTLY DE-SCOPES this (verdict source lines 612-615): "the
     honest cortex-only differentiators are refuse + chain-completeness." Director's HARD_PASS framing
     LED WITH faithfulness 0.798 -- the LEAST clean differentiator.
  C. BY-CONSTRUCTION-EASY refuse (agent flagged honestly): AUROC=1.0 and refuse_precision=1.0 (all 3
     seeds, std 0) because unanswerable queries have support FULLY ABSENT -> min-hop cleanup cosine
     collapses to the ~1/sqrt(N) cross-talk floor, trivially separated from real retrieval. Resolved
     tension: raw retrieval reaches a tail on 55.6% of unanswerables, but their CONFIDENCE is floored,
     so the gate refuses them. The differentiator vs bb is GENUINE IN KIND (cortex has an intrinsic
     per-hop confidence gate; bb has none -> refuse 0.0) but INFLATED IN MAGNITUDE (1.0 will not survive
     a near-miss regime where support is present-but-wrong). A harder near-miss test is being built in
     parallel -- REQUIRED before any 1.0 refuse magnitude is load-bearing.

THE HONEST CLEAN-DIFFERENTIATOR SCOPE (what SPECIFICALLY beats a black-box, survives skeptic checks):
  1. CHAIN-COMPLETENESS 1.0 vs 0.510 (STRUCTURAL, cleanest): the cortex cites the INTERMEDIATE reasoning
     step fact2=(mid,p2,tail); a SINGLE-SHOT retrieve-about-the-query-entity black-box structurally
     CANNOT (mid is not the query subject) -> capped at 0.5. Grounded: the "load-bearing path" is
     cortex's ablation-verified edges (flip_cited=1.0). SCOPE CAVEAT: this is "cannot fake" only vs
     SINGLE-SHOT RAG. A multi-hop / agentic (ReAct-style retrieve-about-mid) black-box COULD cite fact2
     and close this gap -> the differentiator is scoped to single-shot retrieve-then-read, NOT all
     black-boxes. Also somewhat definitional (baseline is DEFINED single-shot-about-s).
  2. INTRINSIC-CONFIDENCE-GATE / calibrated-refuse IN KIND (cortex refuse_precision > 0 vs bb = 0): a
     retrieve-then-read black-box has no per-step confidence to gate on. Genuine capability gap; the
     magnitude (1.0) is easy-regime-inflated (see C).
  NOT clean: soundness/faithfulness magnitude 0.798 vs 0.523 (confounded by strawman citation policy).

FRAMING CORRECTIONS vs Director spawn prompt (Fix#28 symmetric, honest-downward):
  (i)  "first POSITIVE payoff / decisive go/no-go" leading with faithfulness 0.798 -- the faithfulness
       headline is the LEAST clean differentiator (by-construction cited_flip + strawman bb citation
       policy). The go/no-go should rest on chain-completeness + the PENDING harder near-miss refuse
       test, NOT on 0.798.
  (ii) "inverting the prior exp_cortex_task_analog HONEST_NEGATIVE" is IMPRECISE. That negative was
       EXPLICITLY scoped "task utility NOT composition fidelity" (predict-then-check downstream utility;
       it even noted composition-fidelity atom_51 was CG and UNCHANGED). This cell measures 2-hop
       retrieval composition-necessity + provenance -- a DIFFERENT axis. It does NOT invert the
       negative; it is orthogonal to it. "Composition necessary" (shortcut floor 0.019 vs recall 0.964)
       is also largely BY TASK CONSTRUCTION: answerable queries ARE defined as real 2-hop chains with
       gold requiring composition, so needing 2 hops is near-definitional (not cherry-picked, but not an
       emergent surprise either).
  (iii) answerable_retention 0.842 (15.8% of correct answers refused) is NOT a fundamental cost: with
        AUROC=1.0 (perfectly separable in the easy regime) an OPTIMAL threshold retains ~100% at 100%
        refuse-precision; the 15.8% loss is a suboptimal midpoint-of-means threshold artifact. Operating
        point is not tuned/validated; a genuine retention/precision tradeoff only appears in a harder
        regime.

CROSS-ARC OVERLAP CHECK: bash tools/substrate_query.sh "glass-box cortex provenance faithfulness
  ablation cited atom flip calibrated refuse chain completeness" -> top hit cosine=0.3027 is a WordNet
  lexical entry 'faithfulness' (source_class=wordnet), NOT a prior experiment; #2 0.288 prereg
  'Provenance chain if PASS' (unrelated LLN cell); #4/#5 ~0.286 FrameNet/WordNet 'Completeness'. NO
  prior arc CELL at cosine>0.30 on this mechanism. Substrate knows nothing general (these are ingested
  lexica). GENUINELY NOVEL -- first provenance-faithfulness ablation cell. No rediscovery pattern.

POSITIVE-CONTROL / TEST-DESIGN CHECK (Auditor 2026-07-01 rule):
  Not a test-design failure -- this is a PASS not a HF, and the arms genuinely differ (cortex/bb
  provenance hashes distinct per seed; arms_differ_verified=True all seeds). The baseline-in-band gate
  (bb chain_completeness < cortex) holds. The concern is not a broken control but an INFLATED headline:
  the by-construction cited_flip and the fully-absent-support separability make two of the three
  head-to-head wins easy-regime artifacts. Verified off substantive per-seed metrics, not verdict_msg.

TIER RULING: math atom MM_TENTATIVE (measured mechanism; genuine but narrow differentiator; easy
  regime; harder near-miss + stronger multi-hop baseline pending). Counts toward CERT N as a proven,
  characterized mechanism-bound (NOT chain-grade: the decisive metric is by-construction/confounded).
EXPANSION CRITERION (MM_TENTATIVE -> MM_STANDARD/CG):
  Promote when BOTH: (a) the harder NEAR-MISS refuse test (support present-but-wrong, distractor mids)
  still shows conf-AUROC clearly > 0.55 AND cortex refuse-precision > bb, AND (b) the chain-completeness
  gap SURVIVES against a MULTI-HOP / agentic black-box baseline (retrieve-about-mid), not just
  single-shot RAG. Until then the glass-box "cannot-fake" claim is scoped to single-shot retrieve-then-read.

GO/NO-GO (audit-only observation, not direction): a GENUINE structural differentiator EXISTS
  (chain-completeness: name the intermediate step; single-shot RAG cannot) plus an intrinsic-confidence
  gate in-kind. That is enough to SUPPORT CONTINUE-on-observability. It is NOT strong enough to bank as
  "first real POSITIVE payoff" until the harder near-miss test lands and the completeness gap is retested
  against a multi-hop baseline. Continue: YES (on chain-completeness + pending near-miss), but the
  faithfulness-0.798 headline is not the load-bearing evidence.

META RULE (reusable auditor discipline for the observability/glass-box arc): when scoring a
  glass-box-vs-black-box "faithfulness/differentiator" head-to-head, SEPARATE the STRUCTURAL
  cannot-fake gap (can the arm even NAME the intermediate step) from a gap that is merely inflated by the
  BASELINE'S citation POLICY (over-citation strawman) or by BY-CONSTRUCTION separability (fully-absent
  support -> confidence at the noise floor -> AUROC/refuse=1.0). A by-construction cited-input->output
  flip is ~tautological for any glass box and is NOT evidence of a differentiator. Bank the structural
  gap; de-scope the strawman/easy-regime magnitudes until a HARDER regime (near-miss) and a STRONGER
  baseline (multi-hop/agentic, not single-shot RAG) are tested.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
META_ATOMS = ROOT / "data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_landed_VET_2026-07-04_cortex2_provenance_faithfulness_MM_TENTATIVE"
LANDED_VET_SESSION = "2026-07-04_cortex2_provenance_faithfulness_and_calibrated_refuse_v1_FULL_VET"
CELL_COMMIT = "c01aadabe"
TS_ISO = "2026-07-05T03:05:00Z"
TS_EPOCH = 1783220700.0

PROV = {
    "cell": "experiments/exp_cortex2_provenance_faithfulness_and_calibrated_refuse_v1.py",
    "commit": CELL_COMMIT,
    "anchor": "cortex2_provenance_faithfulness_and_calibrated_refuse_v1",
    "metrics_path": "data/exp_cortex2_provenance_faithfulness_and_calibrated_refuse_v1/metrics.json",
    "seeds": [7, 13, 19],
    "run_mode": "full",
    "ts_iso": TS_ISO,
    "atomized_by": ATOMIZED_BY,
    "verified_off_data": True,
    "verified_off_data_note": (
        "Full deterministic RE-RUN reproduces BIT-EXACT all 3 seeds (faith 0.789/0.813/0.791, recall "
        "0.975/0.983/0.933, auroc 1.000, refuse 1.000); all 16 agg fields re-aggregate from per_seed "
        "<1e-9; faithfulness=flip_cited-flip_noncited confirmed per seed; cv faith 1.37% recall 2.27% "
        "completeness 0.00%. Verified off substantive per-seed metrics, not verdict_msg."
    ),
}

atom_math = {
    "id": (
        "math::MM_TENTATIVE_v1_cortex2_GLASS_BOX_PROVENANCE_differentiator_is_GENUINE_but_NARROWER_than_"
        "HARD_PASS_headline_3seed_FULL_bit_exact_rerun_faithfulness_cortex_0p798_std_0p011_vs_bb_0p523_"
        "REPRODUCES_but_DOMINATED_by_flip_cited_1p000_which_is_BY_CONSTRUCTION_for_a_glass_box_only_"
        "measured_component_is_flip_noncited_0p202_crosstalk_leakage_and_headtohead_gap_CONFOUNDED_by_bb_"
        "top3_overcitation_strawman_bb_flip_cited_0p76_a_top1_bb_would_match_hop1_CELL_AUTHOR_self_"
        "descopes_honest_differentiators_are_refuse_plus_chain_completeness_CLEAN_differentiator_is_"
        "CHAIN_COMPLETENESS_1p000_vs_0p510_STRUCTURAL_single_shot_RAG_cannot_cite_intermediate_fact2_mid_"
        "not_query_subject_capped_0p5_scoped_to_single_shot_multihop_agentic_bb_could_close_plus_"
        "INTRINSIC_CONFIDENCE_GATE_in_kind_refuse_precision_1p000_vs_bb_0p000_BUT_auroc_1p000_refuse_"
        "1p000_are_BY_CONSTRUCTION_EASY_unanswerable_support_FULLY_ABSENT_minhop_cosine_at_crosstalk_"
        "floor_answered_frac_on_unans_0p556_raw_but_confidence_floored_harder_NEARMISS_test_pending_"
        "answerable_recall_0p964_vs_shortcut_0p019_composition_necessary_BY_TASK_CONSTRUCTION_2hop_chain_"
        "queries_does_NOT_invert_task_analog_HONEST_NEGATIVE_which_was_task_utility_NOT_composition_"
        "fidelity_retention_0p842_is_suboptimal_threshold_artifact_not_fundamental_cost_arms_differ_"
        "verified_baseline_in_band_cardinality_3of3_CONTINUE_on_observability_supported_on_completeness_"
        "plus_pending_nearmiss_NOT_on_0p798_headline_2026-07-04"
    ),
    "name": (
        "MATH MM_TENTATIVE: cortex2 glass-box provenance differentiator is GENUINE but NARROWER than the "
        "HARD_PASS headline. Reproduces bit-exact (3-seed FULL). Clean differentiator = chain-completeness "
        "1.0 vs 0.51 (structural, single-shot RAG cannot cite the intermediate step) + intrinsic confidence "
        "gate in-kind; faithfulness 0.798 vs 0.523 is by-construction cited-flip + strawman-baseline "
        "confounded; AUROC/refuse=1.0 by-construction-easy (fully-absent support). Harder near-miss + "
        "multi-hop baseline pending."
    ),
    "corpus": "math",
    "tier": "MM_TENTATIVE",
    "kind": "experiment_cert_measured_mechanism_tentative_glass_box_differentiator_easy_regime_narrow_scope",
    "cert_status": "mm_tentative_measured_mechanism_glass_box_differentiator_genuine_but_narrow_easy_regime",
    "cert_class": "cortex2_glass_box_provenance_differentiator_chain_completeness_structural_refuse_in_kind_faithfulness_confounded_easy_regime",
    "description": (
        "LANDED-VET of exp_cortex2_provenance_faithfulness_and_calibrated_refuse_v1 (commit c01aadabe, "
        "3-seed FULL, N=4096, 6000 triples, 120 answerable + 120 unanswerable 2-hop FB15k-237 queries). "
        "Director framed HARD_PASS / first POSITIVE glass-box payoff / decisive go/no-go. VERIFICATION: "
        "full deterministic re-run reproduces BIT-EXACT all 3 seeds; all 16 agg fields re-aggregate from "
        "per_seed <1e-9; faithfulness = flip_rate_cited - flip_rate_noncited confirmed per seed; cv "
        "faithfulness 1.37% / recall 2.27% / completeness 0.00%. HONEST DEFLATED TIER = MM_TENTATIVE "
        "(cell legitimately passes its own pre-reg gates; not disputed) because the DECISIVE metric is "
        "partly by-construction and the head-to-head is confounded: (A) faithfulness_cortex=0.798 is "
        "dominated by flip_cited=1.000 which is ~by-construction for a glass box (answer IS computed from "
        "cited edges; exact shard subtraction guarantees flip; cell selftest asserts it); the only "
        "genuinely measured component is flip_noncited=0.202 cross-talk leakage. (B) the 0.798 vs 0.523 "
        "gap is confounded by the black-box's top-3 over-citation policy (bb_flip_cited~0.76, diluted by 2 "
        "decorative sibling edges); a top-1 black-box would match cortex hop1 faithfulness -- the cell "
        "author HONESTLY de-scopes this (verdict source: 'honest cortex-only differentiators are refuse + "
        "chain-completeness'). (C) conf-AUROC=1.000 and refuse-precision=1.000 (all seeds, std 0) are "
        "BY-CONSTRUCTION-EASY: unanswerable support is fully absent -> min-hop cleanup cosine collapses to "
        "the ~1/sqrt(N) cross-talk floor, trivially separable; raw retrieval still reaches a tail on 55.6% "
        "of unanswerables but their confidence is floored so the gate refuses them. THE HONEST CLEAN "
        "DIFFERENTIATOR SCOPE: (1) chain-completeness 1.000 vs 0.510 -- STRUCTURAL: cortex cites the "
        "intermediate step fact2=(mid,p2,tail); a single-shot retrieve-about-query-entity black-box "
        "structurally cannot (mid is not the query subject), capped ~0.5. Scoped to single-shot RAG: a "
        "multi-hop/agentic (retrieve-about-mid) black-box could close it. (2) intrinsic confidence gate / "
        "calibrated-refuse IN KIND (cortex refuse-precision>0 vs bb=0). NOT clean: the soundness magnitude "
        "0.798 vs 0.523. FRAMING CORRECTIONS vs Director: leading the go/no-go with faithfulness 0.798 (the "
        "least clean differentiator); 'inverts task_analog HONEST_NEGATIVE' is imprecise (that negative was "
        "task-utility not composition-fidelity; orthogonal); composition-necessity (shortcut 0.019 vs recall "
        "0.964) is largely by task construction (queries defined as real 2-hop chains); retention 0.842 is a "
        "suboptimal midpoint-of-means threshold artifact (AUROC=1.0 admits ~100% retention at optimal "
        "threshold), not a fundamental cost. GO/NO-GO: a genuine structural differentiator EXISTS "
        "(chain-completeness + intrinsic gate) -> supports CONTINUE-on-observability, but NOT strong enough "
        "to bank as 'first real positive payoff' until the harder near-miss refuse test lands AND the "
        "completeness gap is retested vs a multi-hop baseline. Cross-arc overlap check: NONE at cosine>0.30 "
        "(top hit 0.3027 is WordNet 'faithfulness', not a prior experiment) -- genuinely novel."
    ),
    "provenance": PROV,
    "reproduced_off_disk": {
        "method": "full_deterministic_rerun_bit_exact_plus_agg_reaggregation_from_per_seed",
        "faithfulness_cortex_mean": 0.7979837653836084,
        "faithfulness_cortex_std": 0.010942955587309162,
        "faithfulness_blackbox_mean": 0.5226705745795662,
        "flip_rate_cited_mean": 1.0,
        "flip_rate_noncited_mean": 0.2020162346163917,
        "chain_completeness_cortex_mean": 1.0,
        "chain_completeness_blackbox_mean": 0.5098530216684375,
        "confidence_auroc_mean": 1.0,
        "confidence_auroc_std": 0.0,
        "refuse_precision_unans_mean": 1.0,
        "bb_refuse_precision_unans_mean": 0.0,
        "answerable_recall_at1_mean": 0.9638888888888889,
        "shortcut_recall_at1_mean": 0.019444444444444445,
        "bb_recall_at1_mean": 0.9638888888888889,
        "answerable_retention_mean": 0.8424933798009971,
        "cortex_answered_frac_on_unans_mean": 0.5555555555555556,
        "cv_faithfulness_cortex": 0.0137,
        "cv_answerable_recall": 0.0227,
        "cv_chain_completeness_cortex": 0.0,
    },
    "clean_differentiator_scope": {
        "genuine_structural": "chain_completeness_1.0_vs_0.510_cortex_cites_intermediate_fact2_single_shot_RAG_cannot",
        "genuine_in_kind": "intrinsic_confidence_gate_refuse_precision_>0_vs_bb_0.0",
        "NOT_clean_confounded": "faithfulness_soundness_magnitude_0.798_vs_0.523_by_construction_cited_flip_plus_strawman_bb_over_citation",
        "structural_scope_caveat": "chain_completeness cannot-fake ONLY vs single-shot retrieve-then-read RAG; multi-hop/agentic bb could cite fact2 and close the gap",
        "easy_regime_caveat": "AUROC/refuse=1.0 by-construction (unanswerable support fully absent -> confidence at cross-talk floor); magnitude will not survive near-miss regime",
    },
    "framing_corrections_vs_director": [
        "go/no-go led with faithfulness 0.798 -- the LEAST clean differentiator (by-construction cited_flip + strawman bb citation policy); should rest on chain-completeness + pending near-miss test",
        "'inverts task_analog HONEST_NEGATIVE' is imprecise: that negative was scoped task-utility NOT composition-fidelity (which was CG and unchanged); this cell is orthogonal, not an inversion",
        "composition-necessity (shortcut 0.019 vs recall 0.964) is largely BY TASK CONSTRUCTION (answerable queries defined as real 2-hop chains); real capability but near-definitional not emergent",
        "answerable_retention 0.842 (15.8% refused) is a suboptimal midpoint-of-means threshold artifact, NOT a fundamental cost: AUROC=1.0 admits ~100% retention at an optimal threshold",
    ],
    "expansion_criterion": (
        "Promote MM_TENTATIVE -> MM_STANDARD/CG when BOTH: (a) harder NEAR-MISS refuse test (support "
        "present-but-wrong, distractor mids) still shows conf-AUROC clearly >0.55 AND cortex refuse-"
        "precision > bb; AND (b) chain-completeness gap SURVIVES vs a MULTI-HOP/agentic black-box "
        "baseline (retrieve-about-mid), not just single-shot RAG."
    ),
    "does_not_invert": "cortex_task_analog HONEST_NEGATIVE (task-utility predict-then-check) -- orthogonal axis; composition-fidelity was already CG and unchanged",
    "arms_differ_verified": True,
    "baseline_in_band": True,
    "cardinality_ok": True,
    "n_units": 3,
    "run_mode": "full",
    "cross_arc_overlap_check": "NONE at cosine>0.30 (top hit 0.3027 WordNet 'faithfulness' lexical entry, not a prior experiment); genuinely novel first provenance-faithfulness ablation cell",
    "positive_control_check": "Not a HF/test-design case (a PASS); arms differ (distinct provenance hashes per seed), baseline-in-band gate holds. Concern is inflated headline (by-construction cited_flip + fully-absent-support separability), not a broken control.",
    "cert_increment_delta": 1,
}

atom_meta = {
    "id": (
        "meta::META_when_scoring_a_GLASS_BOX_vs_BLACK_BOX_faithfulness_or_differentiator_head_to_head_"
        "SEPARATE_the_STRUCTURAL_cannot_fake_gap_can_the_arm_even_NAME_the_intermediate_step_from_a_gap_"
        "merely_inflated_by_the_BASELINES_citation_POLICY_over_citation_strawman_or_by_BY_CONSTRUCTION_"
        "separability_fully_absent_support_confidence_at_noise_floor_AUROC_refuse_1p000_a_by_construction_"
        "cited_input_to_output_flip_is_TAUTOLOGICAL_for_any_glass_box_and_is_NOT_evidence_of_a_"
        "differentiator_bank_the_STRUCTURAL_gap_descope_strawman_and_easy_regime_magnitudes_until_a_"
        "HARDER_regime_near_miss_and_a_STRONGER_baseline_multihop_agentic_not_single_shot_RAG_are_tested_"
        "case_cortex2_provenance_faithfulness_0p798_vs_0p523_confounded_but_chain_completeness_1p0_vs_"
        "0p51_structural_clean_MM_TENTATIVE_2026-07-04"
    ),
    "name": (
        "META MM_TENTATIVE (auditor rule, glass-box arc): score glass-box-vs-black-box differentiators by "
        "the STRUCTURAL cannot-fake gap (naming the intermediate step), NOT by faithfulness magnitude "
        "inflated via baseline over-citation strawman or by-construction separability (AUROC/refuse=1.0 "
        "from fully-absent support). A cited-input->output flip is tautological for any glass box."
    ),
    "corpus": "meta",
    "tier": "MM_TENTATIVE",
    "kind": "methodology_rule_measured_mechanism_tentative_auditor_glass_box_differentiator_scoring",
    "cert_status": "mm_tentative_methodology_rule",
    "cert_class": "MM_TENTATIVE_META_RULE_glass_box_differentiator_separate_structural_from_strawman_and_by_construction",
    "description": (
        "Reusable auditor discipline for the observability/glass-box (M3 cortex) arc. When a cell claims a "
        "glass-box beats a black-box on 'faithfulness' or a provenance differentiator via a head-to-head, "
        "DECOMPOSE the win: (1) STRUCTURAL cannot-fake component -- can the black-box even NAME the "
        "load-bearing intermediate step? (single-shot retrieve-about-query cannot cite an intermediate hop "
        "fact). This is the bankable differentiator. (2) BASELINE-POLICY-inflated component -- a gap that "
        "shrinks if the black-box uses a smarter citation policy (e.g. cite top-1 not top-3) is a strawman "
        "artifact, not a law. (3) BY-CONSTRUCTION-EASY component -- AUROC/refuse=1.0 arising because "
        "negatives have support FULLY ABSENT (confidence collapses to the noise floor) is trivially "
        "separable and will not survive a near-miss regime. Also: a cited-input -> output flip is "
        "~tautological for ANY glass box (removing an input the answer is computed from changes the "
        "output), so flip_cited~1.0 is NOT by itself evidence of a differentiator; the measured signal is "
        "the NON-cited leakage (flip_noncited) and the structural completeness gap. RULE: bank the "
        "structural gap; de-scope the strawman/easy-regime magnitudes until tested in a HARDER regime "
        "(near-miss) against a STRONGER baseline (multi-hop/agentic, not single-shot RAG). Case study: "
        "cortex2_provenance -- faithfulness 0.798 vs 0.523 confounded (by-construction cited_flip + top-3 "
        "over-citation strawman) but chain-completeness 1.0 vs 0.51 is structural and clean."
    ),
    "provenance": PROV,
    "expansion_criterion": "Promote to MM_STANDARD when a 2nd independent glass-box-vs-black-box cell applies the same decomposition and the structural gap survives a stronger (multi-hop) baseline.",
    "cert_increment_delta": 1,
}

ledger_math = {
    "ts": TS_EPOCH,
    "ts_iso": TS_ISO,
    "atom_id": atom_math["id"],
    "corpus": "math",
    "cert_status": atom_math["cert_status"],
    "cert_class": atom_math["cert_class"],
    "cert_increment_delta": 1,
    "verified_off_data": True,
    "disposition": "MEASURED_MECHANISM_TENTATIVE_genuine_but_narrow_glass_box_differentiator_deflated_from_HARD_PASS_headline",
    "cert_delta_note": (
        "MM_TENTATIVE +1. Cell PASSES its own pre-reg gates (HARD_PASS not disputed) but honest CERT tier "
        "is MM_TENTATIVE: decisive faithfulness metric is by-construction (cited_flip=1.0) + confounded by "
        "strawman bb over-citation; AUROC/refuse=1.0 by-construction-easy (fully-absent support). Clean "
        "differentiator = chain-completeness 1.0 vs 0.51 (structural, single-shot RAG cannot cite the "
        "intermediate step) + intrinsic confidence gate in-kind. Reproduces BIT-EXACT (full re-run) + agg "
        "re-aggregates from per_seed. Continue-on-observability supported on completeness + pending "
        "near-miss, not on the 0.798 headline."
    ),
    "atomized_by": ATOMIZED_BY,
    "landed_VET_session": LANDED_VET_SESSION,
}

ledger_meta = {
    "ts": TS_EPOCH,
    "ts_iso": TS_ISO,
    "atom_id": atom_meta["id"],
    "corpus": "meta",
    "cert_status": atom_meta["cert_status"],
    "cert_class": atom_meta["cert_class"],
    "cert_increment_delta": 1,
    "verified_off_data": True,
    "disposition": "MM_TENTATIVE_META_RULE_auditor_glass_box_differentiator_scoring",
    "cert_delta_note": "MM_TENTATIVE META +1: separate structural cannot-fake gap from strawman-baseline and by-construction-easy inflation when scoring glass-box-vs-black-box differentiators.",
    "atomized_by": ATOMIZED_BY,
    "landed_VET_session": LANDED_VET_SESSION,
}


def append_jsonl_a5(path: Path, new_row: dict, label: str) -> int:
    pre_lines = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")
    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")
    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id")
    out_text = "\n".join(pre_lines + [new_line]) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    for _attempt in range(10):
        try:
            os.replace(str(tmp_path), str(path))
            break
        except PermissionError:
            if _attempt == 9:
                raise
            time.sleep(0.1 * (2 ** _attempt))
    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1
    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"]
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"]
    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail line {i+1}: {e}")
    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    append_jsonl_a5(MATH_ATOMS, atom_math, "math/atoms (cortex2 provenance MM_TENTATIVE)")
    append_jsonl_a5(META_ATOMS, atom_meta, "meta/atoms (glass-box differentiator scoring META)")
    append_jsonl_a5(CERT_LEDGER, ledger_math, "cert_ledger (math MM_TENTATIVE +1)")
    append_jsonl_a5(CERT_LEDGER, ledger_meta, "cert_ledger (meta MM_TENTATIVE +1)")
    print(f"[A5] DONE OK  math MM_TENTATIVE +1 | meta MM_TENTATIVE +1")


if __name__ == "__main__":
    main()
