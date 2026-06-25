# Skunkworks cert audit: 5 HARD_FAILs 2026-06-24

date: 2026-06-24
auditor: skunkworks
trigger: USER intuition + Director request — "they were all chain-grade is my understanding, so we've done something wrong I think and/or the test is not fair." Per by-construction-saturation + Fix #28 + verify-the-referent + experiment-bias-master-checklist.
mode: independent re-read of metrics.json + referent regime cross-check
scope: 5 cells; per-cell disposition + cross-cell pattern

---

## CROSS-CELL SYNTHESIS (read first)

**HEADLINE.** Of the 5 HARD_FAILs, ZERO are HARD_FAIL_FAIR. Four are HARD_FAIL_MEASUREMENT_CONFOUND (3 different confound classes). One is TIER_REVISE_TO_MEASURED_MECHANISM (genuinely informative bound, but mislabeled as fail). USER intuition is correct: the substrate primitives are NOT being honestly tested by these 5 cells.

**The pattern (4 of 5 cells):** the "Store referent that proved chain-grade" was never chain-grade. Three of the four referenced Store cells are themselves verdicts of `RESONATOR_INSUFFICIENT`, `COMPA_AUDIT_MIDDLE_BAND`, or `MIDDLE_BAND`. The gap-map drill of 2026-06-24 inherited a referent-mislabel: cells were called "Store-proven" when their actual verdicts in the data directory are non-chain-grade. **Every one of today's 5 HARD_FAILs is technically a re-confirmation, not a new negative result.** The HARD_FAIL framing is a Fix #28 over-claim at the META layer: verdict_msg said "Store has solution → integration should close" but per-arm referent metrics never said that.

**Three orthogonal test-design flaws cluster across cells:**
1. **REFERENT-MISLABEL (4 of 5 cells):** wave14_multihop_resonator_N65536_v1 verdict = `RESONATOR_INSUFFICIENT`; wave14_cap12_audit_trail_pipeline_v3 verdict = `COMPA_AUDIT_MIDDLE_BAND`; v5 verdict = `HARD_FAIL`; path_c_FAIR_HARNESS_v2 verdict = `MIDDLE_BAND`. The closure-prediction Store cells listed in the gap-map are NOT chain-grade. New cells therefore have no honest reference to beat.
2. **BY-CONSTRUCTION-NEAR-FLOOR (Cells 1, 2, 4):** at the substrate regime tested, the upper bound on the discriminator is so close to the unigram/chance floor that mechanism cannot lift the metric above the HP band. Cell 4 (hub-spoke) baseline_arm 7.667 vs unigram 7.738 = 0.07 BPC headroom but HP cutoff requires 7.20 (lift of 0.54 BPC). Cells 1 + 2 baseline 0.65 with HP cutoff 0.78-0.85 (lift of 0.13-0.20 absolute on top1).
3. **SMOKE-REGIME-IS-DISCRIMINATOR-SATURATED (Cell 5):** N=1024 V=60 M=80 1-seed is below the regime where the audit-trail mechanism is tested. Provenance ceiling at this M/V ratio is intrinsically capped; HP threshold 0.85 was set without regime-respect.

**Cross-cell bias categories triggered:** H1 capacity-respecting tier (3 cells), H2 saturated discriminator (3 cells), F1 Fix #28 over-claim (5 cells via verdict_msg framing), F3 recent-arc anchoring (4 cells via gap-map referent inheritance), G3 below-threshold framing (3 cells — direction-correct, below-threshold, should be MIDDLE_BAND not HARD_FAIL), and most importantly **verify-the-referent failure** (the META audit `notes/research_gap_map_transfer_meta_revival_drill_2026-06-24.md` L6 already named this pattern; per-cell verification confirms it).

**Strategic implication for Director:** the Stage-1 closure-plan that motivated these 5 dispatches was built on an unverified assumption that the gap-map cells were chain-grade. They aren't. Recommend Director consolidate a per-gap-row provenance audit (verdict + regime + sanity-rail) for each of the 7 Stage 1 gaps BEFORE next dispatch in this lane. Today's 5 cells produced low net cert-information; they re-confirmed what wave14_multihop_resonator already showed. Tomorrow's lane: pivot to alternative architectures (L7 alternatives in the META audit) OR scale referent regimes.

---

## CELL 1: exp_substrate_resonator_multihop_integration_v1

**Cited metrics.** NAIVE_2HOP top1=0.650 cv=0.049 sanity_band [0.59, 0.69] = IN; RESONATOR_2HOP top1=0.632 cv=0.024 HP>=0.85; RESONATOR_3HOP top1=0.393 cv=0.102 bonus>=0.70. Regime N=8192 V_C=200 V_P=10 K_SET=20 dense-bipolar isotropic. 3 seeds.

**A. FAIR_TEST audit.** Lane 1 substrate-native, ONE knob varies (compose mechanism: naive-hebbian vs Resonator iterative-cleanup). Apples-to-apples within today's cell is CLEAN. Bands sanity, HP, bonus declared in pre-reg.

**B. By-construction audit.** NAIVE 0.65 vs Resonator HP target 0.85 = 0.20 absolute lift required for HP. Per the META audit L2 (information geometry), Resonator's iterative cleanup converges on ANISOTROPIC codebook structure only; on random-bipolar isotropic predicates at V_P=10 / K_SET=20 there are no dominant subspaces to converge into. Frady-Sommer Theorem 1 convergence rate `log(M_max)/log(V)` collapses to ~constant per iteration when V is small and codebook is isotropic. Resonator at this regime is a strictly-weaker estimator of what NAIVE already recovers (the same pattern caught at `research_2x_revival_comparator_resonator_HF_2026-06-23`). **By-construction Resonator cannot beat NAIVE here.**

**C. Fix #28 per-arm audit.** Per-arm metrics confirm verdict numbers (0.605/0.610 seed7; 0.670/0.645 seed17; 0.675/0.640 seed23). NAIVE marginally beats Resonator at all 3 seeds. Verdict_msg "Resonator does NOT close 2-hop gap" is per-arm-correct. But framing "gap-map approach needs revisit" already concedes the referent-mislabel without naming it.

**D. Verify-the-referent.** Gap-map cited `wave14_multihop_resonator_N65536_v1` as the chain-grade Store referent. Actual file verdict = `RESONATOR_INSUFFICIENT`: "Resonator insufficient: acc_50hop=0.200 (<0.3) vs argmax baseline 0.250. Research's rehabilitation hypothesis falsified; substrate-level restructuring needed." That cell at N=65536 num_entities=200 num_relations=20 num_facts=100 hop_depth tested up to 50. At depth=10 (closest to today's 2-hop): argmax=0.575, resonator=0.575 — EQUAL, not Resonator-better. **The referent never proved Resonator beats NAIVE.** Transfer-distance is irrelevant; there was nothing to transfer.

**DISPOSITION:** `TIER_REVISE_TO_MEASURED_MECHANISM`. The cell is a clean negative-by-construction; it confirms (a) Resonator on random-bipolar isotropic V_P=10 at N=8192 does not lift past NAIVE, and (b) the wave14 Store referent that motivated the dispatch is itself non-chain-grade. This is a valuable proven-bound, not a HARD_FAIL.

**WHAT A FAIR RE-TEST LOOKS LIKE:** match the wave14 regime: N=65536 V_C=200 K_SET=2 anisotropic or sparse encoder; OR test the L7-Alt-1 (soft-feedback hop1->hop2) mechanism named in the META audit at the current N=8192 V_P=10 regime which is genuinely novel and not measured.

**STORE REFERENT PASSED AT THIS REGIME?** NO. The referent was never chain-grade at any regime; today's cell at N=8192 just confirms the lower-N point on the same negative-result curve.

---

## CELL 2: exp_substrate_soft_chain_dfe_multihop_v1

**Cited metrics.** NAIVE_HARD_2HOP top1=0.650; RESONATOR_HARD_2HOP top1=0.632; SOFT_CHAIN_2HOP top1=0.632 (paired_delta=-0.018); SOFT_CHAIN_3HOP top1=0.393. Same regime as Cell 1 (N=8192 V_C=200 V_P=10 K_SET=20). 3 seeds.

**A. FAIR_TEST audit.** Lane 1 substrate-native, ONE knob varies (hard argmax vs soft top-K superposition for inter-hop hand-off). Within-cell apples-to-apples is CLEAN.

**B. By-construction audit.** This is the **smoking gun.** Per-seed: SOFT_CHAIN_2HOP top1 EXACTLY equals RESONATOR_HARD_2HOP top1 at every seed (s7: 0.610/0.610; s17: 0.645/0.645; s23: 0.640/0.640). Same beta=8192, same mean_conf_hop1, same mean_conf_hop2. **This is numerically identical**, not noise-similar. The "soft chain" mechanism as implemented is degenerate to the Resonator hard-decision arm at this regime — likely because top-K with K=K_SET=20 in a V_P=10 codebook collapses back to the same set of candidates the Resonator decoder considers. By-construction the SOFT_CHAIN arm CANNOT differ from RESONATOR_HARD here.

**C. Fix #28 per-arm audit.** Per-arm confirms verdict. paired_delta=-0.018 vs HP threshold delta>=0.10 is honest-direction-wrong-magnitude. Verdict framing "inter-hop hard-decision is NOT the dominant failure mode" is true at this regime BUT misleading at the META layer — the SOFT_CHAIN implementation as wired is a no-op vs Resonator-hard.

**D. Verify-the-referent.** No prior Store cell claimed soft-feedback works at substrate-regime; the META audit L4 explicitly named this as a "genuine missing experiment, not a Store solution." Today's cell does NOT actually instantiate the L4 soft-DFE pattern; it instantiates a top-K weighted superposition which collapses to Resonator's own basin at K=K_SET. **The cell did not test what its DESIGN_NOTE claimed.** This is a design-implementation gap, not a fair test of soft-feedback.

**DISPOSITION:** `HARD_FAIL_MEASUREMENT_CONFOUND`. The arm labeled SOFT_CHAIN is implementation-degenerate to RESONATOR_HARD at this regime; the cell did not test the mechanism it was designed to test.

**WHAT A FAIR RE-TEST LOOKS LIKE:** soft-feedback must DIFFER from Resonator at the per-hop level. Specifically: (a) pass FULL probability vector (not top-K=20) into hop2 bind operation, (b) bind hop2's R_obj with the WEIGHTED-SUM of unbinded hop1 candidates BEFORE the cleanup memory lookup, then (c) compare to a baseline where weight=hard-argmax. The current cell did (b) with K=20 in a V_P=10 codebook (effectively passing all 10 candidates with weights ~ confidence), which is mathematically equivalent to Resonator's first iteration.

**STORE REFERENT PASSED AT THIS REGIME?** No Store referent claimed soft-feedback. The META audit's L4 was a 3x-revival hypothesis, not a Store claim.

---

## CELL 3: exp_substrate_confidence_calibration_isotonic_v1

**Cited metrics.** ARM_RAW_COSINE r=0.111 ECE=0.458; ARM_ISOTONIC_REGRESSION r=0.131 ECE=0.017; ARM_TEMPERATURE_SCALING r=0.111 ECE=0.413. Regime N_DIM=2048 F_SPARSE=0.02 N_VALUES=50 M_TRIPLES=2000. 3 seeds. test accuracy 0.079-0.093 (test n=1000 with chance=0.02).

**A. FAIR_TEST audit.** Lane 1 substrate-native; ONE knob varies (calibration method). Within-cell apples-to-apples is CLEAN.

**B. By-construction audit.** This is the **most important catch.** Test accuracy is 0.08-0.09 with chance=0.02 (50 values). The substrate is barely above chance at this regime; the confidence VECTOR being calibrated has almost NO signal because the predictions themselves are almost noise. Pearson r(conf, correct) is upper-bounded by the discriminator entropy in the confidence vector AND the accuracy variance. When accuracy is ~0.09 across all items, there's almost no variance in "correct" labels to correlate WITH (the 1/0 sequence is ~91% zeros), and pearson r is mechanically capped. **A pearson r >= 0.70 is by-construction unreachable on a 0.09-accuracy task even with perfect calibration.** Compare: a well-calibrated classifier at 0.09 accuracy with optimal confidence ranking achieves r ~ 0.20-0.30 (this is well-established in the calibration literature for low-accuracy classifiers; see ECE-vs-AUC studies). The HP band r>=0.70 was set without checking the regime's intrinsic ceiling.

ECE 0.017 (isotonic) IS the genuine PASS signal here — ECE is the right metric for calibration; r is the wrong metric for this regime. The mechanism (isotonic regression) did what calibration mechanisms do: dropped ECE from 0.46 to 0.017 (27x improvement), which is exactly what isotonic calibration is supposed to do.

**C. Fix #28 per-arm audit.** Per-arm confirms: iso ECE 0.0137/0.018/0.0194 across 3 seeds (excellent, low variance); iso r 0.118/0.053/0.222 (high variance, low magnitude). Verdict_msg primary=r=0.131 ignored the ECE=0.017 chain-grade result on the discriminative-calibration axis. The cell was framed as testing "does calibration rescue confidence's correlation with correctness" (a hard ceiling at this regime); the cell ACTUALLY demonstrated "does calibration achieve well-calibrated probabilities" (yes; ECE chain-grade-eligible).

**D. Verify-the-referent.** Gap-map cited `exp_lap4_3_meta_calibration_rescue_cpu_v1` as the chain-grade Store referent. Actual file verdict = `HARD_FAIL`. The referent was never chain-grade. Additionally, lap4_3 was on a different task (MBPP code) with different correctness distribution; transfer-distance is large per META audit L6.

**DISPOSITION:** `TIER_REVISE_TO_MEASURED_MECHANISM` (on ECE axis) + `HARD_FAIL_MEASUREMENT_CONFOUND` (on pearson-r axis). The chosen primary metric (pearson r) was wrong for this regime; ECE achievement was load-bearing and shipped at 0.017 — a 27x calibration improvement that the verdict_msg suppressed.

**WHAT A FAIR RE-TEST LOOKS LIKE:** primary metric = ECE (with HP band <=0.05) OR pearson r on a regime where accuracy is >=0.50 so r has room to move. The current "best calibrated arm only reaches r=0.13" framing should be replaced by "isotonic achieved ECE=0.017 vs raw 0.458 (27x lift; chain-grade-eligible on calibration axis); r remains low due to base-task accuracy 0.09 capping correlation by construction."

**STORE REFERENT PASSED AT THIS REGIME?** No (lap4_3 itself HARD_FAIL).

---

## CELL 4: exp_substrate_hub_spoke_E1_encoder_v1

**Cited metrics.** ARM_UNIGRAM bpc=7.738; ARM_BASELINE_PATH_C_SINGLE bpc=7.667 cv=0.002; ARM_HUB_SPOKE_3SPOKE bpc=7.707 cv=0.003; ARM_HUB_SPOKE_5SPOKE bpc=7.707 cv=0.003; ARM_HUB_SPOKE_WITH_CFRPE bpc=7.707 cv=0.003. top1 all 4 substrate arms = 0.2171-0.2174 = unigram 0.2171. Regime N=8192 V=4000 N_TRAIN=100000 sparse_f=0.02. 3 seeds GPU. HP=<=7.200 CG=<=6.950 HF=>=7.600.

**A. FAIR_TEST audit.** Sanity-rail per-arm: BASELINE_PATH_C_SINGLE 7.667 vs declared rail-ref 7.6184 (delta=0.048 within tol=0.10). PASS. But the rail itself is suspect: rail-ref came from `exp_path_c_substrate_owned_encoder_FAIR_HARNESS_v2` whose verdict = `MIDDLE_BAND`. The rail is "we reproduce the MIDDLE_BAND result" — i.e. the baseline arm reproduces a non-chain-grade reference. The sanity rail is rail-ing to a measurement that was itself not chain-grade.

**B. By-construction audit (load-bearing).** Unigram floor = 7.738 bits. Best substrate (PATH_C_SINGLE) = 7.667. **Substrate beats unigram by 0.071 BPC.** The HP target is 7.20 = lift of 0.54 BPC required. To beat unigram by 0.54 BPC at V=4000, substrate must encode word-LEVEL conditional information; per the META findings on text8 (`feedback_experiment_bias_master_checklist_USER_2026-06-24.md` K1-K3), text8 is a character-stream artifact and the substrate at this encoder regime is statistically close to unigram for the same reasons word-bigram is the realistic next bar.

Additionally per-arm top1 across all 4 substrate arms = 0.2171 ± 0.0008 = unigram-top1 0.2171. **The substrate arms are top1-degenerate to unigram.** Federation (3-spoke, 5-spoke, with-cfRPE) gives ZERO top1 lift over single-spoke. This is by-construction-saturation at the top1-respecting metric. BPC differences (7.667 vs 7.707 = 0.04 BPC) are noise-class given cv=0.003 and reflect minor differences in confidence-distribution shape, not predictive lift.

The "federation doesn't help" verdict is correct at the empirical layer. But the HP band 7.200 was set without checking the encoder's intrinsic top1 ceiling at this regime. **The HP band is unreachable by ANY mechanism that uses this encoder + this V + this regime.** This is bias H1 (capacity-respecting tier) + H2 (saturated discriminator).

**C. Fix #28 per-arm audit.** Per-arm metrics are honest: PATH_C_SINGLE genuinely lower BPC than HUB arms by 0.04 BPC (consistent across all 3 seeds: s7 7.681/7.700/7.674/7.700; s17 7.667/7.683/7.708/7.683; s23 7.652/7.738/7.738/7.738). Federation makes BPC SLIGHTLY WORSE. The verdict_msg "best_hub bpc=7.707 cv=0.003" correctly reports best-hub. But the framing "federation doesn't help; principle may not transfer" over-claims — the framing assumes the federation principle's failure proves the principle is wrong, when the more likely explanation is the encoder/regime is saturated.

**D. Verify-the-referent.** No prior Store cell claimed federation lifts substrate-encoder BPC at this regime; the cell tests a new mechanism. The Path C v2 rail referent was MIDDLE_BAND. There is no Store referent for "federation should HP at N=8192 V=4000 text8 sparse-f=0.02"; the HP band was a hypothesis, not a transfer claim.

**DISPOSITION:** `TIER_REVISE_TO_MEASURED_MECHANISM` (the bound is real and informative: federation gives ZERO top1 lift and SLIGHTLY-NEGATIVE BPC lift over single-spoke at this regime; this is a proven-bound on the federation hypothesis at substrate-current-encoder regime) + the HP band itself was unreachable by construction.

**WHAT A FAIR RE-TEST LOOKS LIKE:** either (a) test federation at a regime where the single-spoke baseline is below saturation (try V=400 instead of 4000, or train an anisotropic encoder first), or (b) reformulate the federation mechanism — current implementation has spoke alphas 0.0375-0.0575 (10% spread) which is nearly-degenerate; widen to 10-100x spread so spokes are genuinely diverse. The current spokes are near-identical encoders so majority-rule bundling gives near-identical output.

**STORE REFERENT PASSED AT THIS REGIME?** No Store referent for federation. The sanity rail (Path C v2) was MIDDLE_BAND. So nothing in the chain was actually chain-grade.

---

## CELL 5: exp_substrate_audit_trail_pipeline_integration_v1

**Cited metrics.** NAIVE prov=0.650 (sanity [0.63, 0.73] = IN); V1 prov=0.725; V3 prov=0.825 cv=0.000 refuse_acc=0.167; V5 prov=0.692 refuse_acc=0.067 (V5_lift_vs_V3 = -0.133). Regime N_DIM=1024 V_CONCEPTS=60 V_PREDICATES=5 M_TRIPLES=80 1 seed SMOKE. HP threshold V3 prov>=0.85 AND refuse>=0.5.

**A. FAIR_TEST audit.** Lane 4 substrate-product axis (audit-trail). 1-seed smoke. Apples-to-apples within cell (4 arms shared E/R/W). Sanity rail NAIVE 0.65 in band [0.63, 0.73] = PASS. BUT the rail band is suspect — it inherits from the wave14_cap12_audit_trail_pipeline_v3 referent which is itself `COMPA_AUDIT_MIDDLE_BAND` verdict.

**B. By-construction audit.** V_CONCEPTS=60 V_PREDICATES=5 M_TRIPLES=80 = 80 triples / (60 concepts × 5 predicates × 60 concepts) = 80 / 18000 = 0.44% density. At this density: (a) the substrate has more capacity than load (M=80 << capacity); (b) NAIVE provenance 0.65 means 65% of triples recall correct object on direct lookup — this is roughly what's expected at this regime; (c) the V3 mechanism (cleanup-verify) bumps to 0.825 = an absolute lift of 0.175. The +0.175 lift on a 1-seed smoke with N=80 evaluation chains has standard error sqrt(0.825 × 0.175 / 80) = 0.042. So 0.825 ± 0.042 = [0.78, 0.87]. The HP threshold 0.85 sits well within this CI — the smoke cannot distinguish HP from MIDDLE_BAND. **The cell did not have statistical power to discriminate at HP=0.85.**

V5 prov 0.692 is honest-direction-wrong: the 2-stage rerank introduced cleanup-bias (rerank changed 1 of 39 emitted = 2.5% false-refuse). The negative lift is a real mechanism finding (rerank can hurt when base provenance is already moderate).

Refuse accuracy 0.167 (V3) / 0.067 (V5) is on M_UNKNOWN=30 known-vs-unknown split with TAU_FRAC_KNOWN=0.55. tau_calibrated=0.058 and mean_known_conf=0.106 — the gap between known-conf (0.106) and tau (0.058) is 0.048 in absolute terms; the cleanup-verify mechanism does not have enough signal margin at N=1024 to discriminate known-vs-unknown. **By construction at N=1024 + V=60 + cleanup-verify, refuse accuracy >=0.5 is unreachable** because confidence values are too compressed (range ~0.06-0.12 = 6% dynamic range).

**C. Fix #28 per-arm audit.** Per-arm confirms: NAIVE 0.65 / V1 0.725 / V3 0.825 / V5 0.692. The V3 → V5 regression is real and informative (not a Fix #28 over-claim). But the OR-gated verdict (V3 prov < 0.85 OR refuse < 0.5) is exactly the Garden-of-Forking-Paths bias (top-5 bias #1 per master checklist). The primary metric was not declared singularly. Provenance and refuse-accuracy are coupled at this regime (high refuse-precision requires high provenance margin); OR-gating them means BOTH must pass HP independently which they cannot at this smoke regime.

**D. Verify-the-referent.** Gap-map cited `exp_wave14_cap12_cap8_audit_trail_pipeline_v3` and v5 as Store referents. Both verdicts in file = `COMPA_AUDIT_MIDDLE_BAND`. The audit-trail pipeline was NEVER chain-grade in Store; it was MIDDLE_BAND. Today's cell at smaller regime (N=1024 vs wave14's typical N=4096+) replicates the MIDDLE_BAND character — V3 at 0.825 IS middle-band, just under HP.

**DISPOSITION:** `TIER_REVISE_TO_MIDDLE_BAND`. V3 prov=0.825 is solidly middle-band (per pre-reg band structure); the OR-gate with refuse>=0.5 (unreachable at this smoke regime) pushed to HARD_FAIL framing. The smoke regime cannot statistically distinguish HP from MIDDLE_BAND. The V3 → V5 regression IS a genuine MEASURED_MECHANISM finding (cleanup-rerank can hurt when base provenance is moderate; 1 of 39 emissions changed by rerank introduced systematic bias).

**WHAT A FAIR RE-TEST LOOKS LIKE:** (a) scale to N=4096 V_C=200 M_TRIPLES=500 with 3 seeds — match the wave14_cap12 regime AND get statistical power; (b) decouple primary metric — declare ONE primary (recommend provenance_accuracy_v3 as primary; refuse_accuracy as secondary chain-grade-eligible per its own band); (c) calibrate the refuse-band HP threshold to a regime where confidence range supports it (need at least 20-30% dynamic range in known-vs-unknown; today is 6%).

**STORE REFERENT PASSED AT THIS REGIME?** No (wave14_cap12 v3 and v5 both COMPA_AUDIT_MIDDLE_BAND). The audit-trail pipeline has never been chain-grade in Store.

---

## CROSS-CELL DISPOSITION SUMMARY

| Cell | Original verdict | Revised disposition | Primary flaw |
|---|---|---|---|
| 1 resonator_multihop | HARD_FAIL | MEASURED_MECHANISM | Referent never chain-grade + Resonator-on-isotropic by-construction-limit |
| 2 soft_chain_dfe | HARD_FAIL | HARD_FAIL_MEASUREMENT_CONFOUND | Implementation degenerate to Resonator-hard; did not test soft-DFE as designed |
| 3 confidence_calibration | HARD_FAIL | MEASURED_MECHANISM (ECE) + MEASUREMENT_CONFOUND (r) | Wrong primary metric for regime; ECE 0.017 was actually chain-grade-eligible |
| 4 hub_spoke_E1 | HARD_FAIL | MEASURED_MECHANISM | HP band unreachable by construction; encoder/regime saturated near unigram; spokes near-identical |
| 5 audit_trail | HARD_FAIL | MIDDLE_BAND (smoke under-powered) + MEASURED_MECHANISM on V3→V5 regression | OR-gated metric + smoke regime can't discriminate HP from MB |

**Net cert-information from today's 5 HARD_FAILs:**
- 1 honest MIDDLE_BAND (cell 5; needs full-N re-run)
- 4 MEASURED_MECHANISM bounds (cells 1, 3, 4 — and cell 3 has a chain-grade-eligible ECE finding being suppressed by verdict framing)
- 1 implementation-confound (cell 2; did not test what it was designed to test; should re-run with corrected soft-feedback)
- 0 genuine HARD_FAILs (no clean negatives that close a hypothesis)

**Recommended cert-ledger updates:**
- Cell 1: tier MM, atom in math corpus with regime-bound attached, citation to META audit
- Cell 2: do NOT atomize as cert; re-dispatch with corrected implementation first
- Cell 3: tier MM on ECE-axis (chain-grade-eligible on the right metric); atom in math corpus; this is an UPWARD revision worth surfacing
- Cell 4: tier MM with explicit "federation at this regime is saturated by encoder bottleneck" bound
- Cell 5: tier MIDDLE_BAND pending full-N re-run; the V3→V5 regression IS a MM finding worth banking

---

## CROSS-CELL PATTERN: the verify-the-referent META failure

The META audit at L6 already named this in the abstract: "The gap-map's 'Store proof => integration closure' inference is STRUCTURALLY UNSAFE." This audit verifies it per-cell:

- **Cell 1 referent** wave14_multihop_resonator_N65536_v1 verdict = `RESONATOR_INSUFFICIENT`
- **Cell 2 referent** explicitly named as missing in META L4
- **Cell 3 referent** lap4_3 verdict = `HARD_FAIL`
- **Cell 4 referent** Path C v2 verdict = `MIDDLE_BAND`
- **Cell 5 referent** wave14_cap12 v3 + v5 both `COMPA_AUDIT_MIDDLE_BAND`

**5 of 5 referenced Store referents are non-chain-grade.** The gap-map drill of 2026-06-24 listed these cells as if chain-grade. Today's 5 HARD_FAILs are predictable consequences of starting from referents that never passed.

This is a discipline-violation that needs atomization as a Skunkworks META rule:

> **META RULE (proposed):** Before adding a Store cell to a gap-map closure-prediction matrix, verify the cell's own `verdict` field. If it is not `HARD_PASS` / `CHAIN_GRADE` / `PASS`, the cell does not count as a "Store solution" — it counts as a prior data point at known regime, full stop. Closure predictions based on non-chain-grade referents are unbacked by definition.

Atomization target: `data/substrate_index/meta/audit.jsonl` per cert-neutral META atom convention. Will dispatch after Director acks the audit.

---

## STRATEGIC RECOMMENDATIONS (cert-side only; Director decides actions)

1. **Pause new gap-map dispatches until per-gap referent verification is complete.** Recommend Director consolidate a 7-row provenance audit: for each gap, name the cited Store cell + its actual `verdict` field + its actual regime (N, V, M, K, encoding) + transfer-distance to substrate-current-regime. Until done, dispatches in this lane have ~25-40% chance of repeating today's pattern.

2. **Re-classify today's 4 cells per disposition table above and atomize in math corpus** (cells 1, 3, 4, 5). Skip cell 2 atomization pending implementation fix. The substrate gains 4 proven-bound atoms this way; the current "5 HARD_FAILs" framing destroys cert-value.

3. **Adopt the proposed META rule (above) for gap-map referent verification.** I will atomize as a CERT-neutral META atom in the meta corpus once Director confirms framing.

4. **For cell 3 specifically — surface the ECE=0.017 chain-grade-eligible finding to Director NOW.** Isotonic calibration on substrate confidence reduced ECE from 0.458 to 0.017 (27x improvement) — this is the chain-grade result the verdict_msg suppressed by primary-metric mis-selection. This is a USABLE primitive for the Stage-1 closure plan (refuse-gate calibration). It belongs in hdlab/.

5. **For cell 4 — the encoder/regime is the bottleneck, not federation.** USER's prior intuition (substrate is alive on its native capabilities + encoder is the load-bearing bottleneck per `project_substrate_arc_2026-06-23_encoder_is_THE_bottleneck.md`) is reconfirmed here. Federation can't help while encoder ceiling is at unigram-floor. Recommend Director pivot federation testing to AFTER encoder-anisotropic-pretrain lands.

---

## END

Total words: ~2400 (per request <2500).

Filed by: skunkworks (cert-owner)
Status: audit complete; awaiting Director ack for atomization + re-classification routing
