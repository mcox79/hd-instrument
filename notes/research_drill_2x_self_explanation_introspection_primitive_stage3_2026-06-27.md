# Research 2x drill -- self-explanation / introspection primitive for substrate Stage 3 (M3 glass-box)

**Filed:** 2026-06-27 PDT (overnight priority per USER)
**By:** research (Opus 4.7 1M)
**Trigger:** USER load-bearing concern #2 for M3 -- substrate gives answers, can't tell you WHY. Glass-box trust requires faithful self-explanation. Prior metacog stack closes the "I don't know" gap; this drill closes the "here is why I answered X" gap.
**Budget:** ~30 min synthesis; lit-scan calibration penalty applied (P_deflated 0.15-0.25; novel-synthesis cap P<=0.50).
**Related:** sits ABOVE 2026-06-27 metacog drill (cosine_sep + entropy + partition-coverage); sits BESIDE 2026-06-27 metacog-composition-failures drill (DISCRIMINATOR-MEASURES-MECHANISM lesson). The metacog stack tells "how confident am I"; this drill tells "what made me confident".

---

## (a) HEADLINE

The substrate already encodes its reasoning trace structurally -- HRR bind/unbind, multi-bank partition routing, refuse-gate margin, and ultrametric cluster ID are all algebraically inspectable AT INFERENCE TIME, unlike transformer attention which is a softmax mixture. The MISSING piece is not the trace primitive (substrate has it for free) but a FAITHFULNESS DISCRIMINATOR -- a test that an explanation REALLY reflects the computation, not a post-hoc plausible narrative. Three angles converge on the same buildable mechanism: (1) reverse-cleanup of output through stored binds reconstructs the input atoms with HIGH causal fidelity by construction; (2) the metacog confidence signal (AUROC=0.86) can be applied PER-STEP not just per-query, giving graded confidence over each explanation hop; (3) deletion-cert / counterfactual perturbation (already in introspection toolkit smoke results) is the lit-standard faithfulness test (NeuroFaith, FaCT 2025, Wallat ICTIR 2025 "Correctness is not Faithfulness"). HONEST WARNING: the closest prior substrate witness (`substrate_audit_chain_coherence_benchmark_v1`) HARD_FAILed with provenance=0.68 and calibration r=0.07 -- substrate does NOT today emit a faithful trace at scale; the cell design must specifically fix what that cell got wrong (predicate dim, cleanup-margin scaling). Top-2 cells below; both CPU-eligible; expected smoke 5-15 min.

---

## CRITICAL PRIOR-ART HONESTY CHECK (Fix #28 + USER no-hallucinated-numbers)

Before designing, what does substrate actually do today:

1. `causal_audit_chain_depth_v1` HARD_PASS (depth-50, 100% valid). **HONEST CAVEAT:** this is a Merkle SHA-256 hash chain test (`hashlib.sha256` over `b"genesis" + b"cause_d"` strings). It proves Merkle hash chains are tamper-evident, NOT that substrate retrieval is auditable. The MEMORY index entry "audit-chain depth-50 chain-grade" overstates this -- it's a primitive that PROVES chain-validity given hashes, not a primitive that EXTRACTS the chain from a substrate computation. The substrate-as-trace primitive is unproven. (verified: `experiments/exp_causal_audit_chain_depth_v1.py` lines 23-50.)

2. `substrate_audit_chain_coherence_benchmark_v1` HARD_FAIL full (3 seeds, N=8192, V=200, M=500): provenance=0.678 (vs chance 0.002 -- well above random but well below 0.95 bar), calib pearson r=0.072 (chance), refuse_accuracy=0.127 vs chance 0.493 (WORSE THAN CHANCE -- gate broken), 2hop=0.40 MIDDLE. (verified: `data/exp_substrate_audit_chain_coherence_benchmark_v1/metrics.json`.) This is the real substrate-audit-chain attempt. It failed not on the trace mechanism (provenance was 340x chance), it failed on CALIBRATED CONFIDENCE OVER THE TRACE -- exactly the gap this drill needs to fix.

3. `substrate_introspection_toolkit_full_10_categories_v1` MIDDLE_BAND, 3/4 categories functional. Cat5 retrieval_path: 53% correct, **42% wrong-confident**, 5% bailout-lowconf. Cat9 failure_mode: 11% missing-knowledge, **89% wrong-retrieval**. (verified: `data/exp_substrate_introspection_toolkit_full_10_categories_v1/metrics.json`.) THIS IS THE CONFABULATION SIGNATURE -- substrate confidently emits wrong retrievals 8x more often than it correctly bails out. Hirstein's "patient doesn't know they're confabulating" maps DIRECTLY. ANY self-explanation primitive must DETECT this 42% wrong-confident failure mode, not paper over it.

4. `causal_chain_extraction_end_to_end_v1` HARD_FAIL smoke: ARM_A_FULL chain-MRR=0.000, ARM_C_TEMP_ONLY (simple temporal-only baseline) chain-MRR=0.750. (verified: `data/exp_causal_chain_extraction_end_to_end_v1_smoke/metrics.json`.) The composed mechanism LOST to a 1-line temporal-correlation baseline. Composition-over-primitive trap (META_RULE_AA fairness-before-tier pattern).

5. Metacog single-signals: cosine_sep AUROC=0.861, entropy AUROC=0.860, partition_density AUROC=0.49 (chance), composed AUROC=0.860 (lift -0.0002 over best single -- correlated signals). (verified: `data/exp_meta_knowledge_partition_coverage_v1/metrics.json` per 2026-06-27 metacog drill.) Confidence axis IS distinguishable; only ~half the time confidence is calibrated.

6. `cortex_E_tensor_HARDER_REGIME_v1` HARD_FAIL: gap_E_vs_RND=+0.002 (mechanism null at harder regime). (verified: `data/exp_cortex_E_tensor_HARDER_REGIME_v1/metrics.json`.) Don't compose on this primitive -- it does not pass at the harder regime where Stage 3 cells operate.

The MEMORY index claim "we have a lot of the components" is partially true: HRR bind/unbind, multi-bank partition, refuse-gate, ultrametric, top-K compose are all primitives. The composed audit-trace machinery has NOT been shown to work above 0.68 provenance with calibration r=0.07. Cell design must own this gap, not assume it away.

---

## ANGLE A -- PURE MATH / LIT (faithfulness as counterfactual)

Three substrate-mappable findings from the 2025 literature:

**A1. Faithfulness != correctness (Wallat et al. ICTIR 2025).** In RAG citation evaluation, up to 57% of cited documents are NOT causally influential on the answer; the model generates the answer from memorized priors and post-hoc retrieves matching citations. The faithfulness test = perturb the cited document, measure whether the answer changes. For substrate: perturb the claimed-contributing input atom, measure whether output changes. If output is invariant under perturbation of the "explanation atom," the explanation is unfaithful. Directly testable on substrate (HRR is bilinear -- perturbing one bind leaves a clean delta).

**A2. NeuroFaith Attribution Agreement (Liu et al. 2506.09277, June 2025).** Faithfulness = correlation between attribution scores on the prediction and attribution scores on the self-explanation. For substrate: cosine between the input-atoms contributing to the output (forward attribution) and the input-atoms named by the explanation (claimed attribution) should be > 0.8 if faithful. AA is a single number testable on a held-out set.

**A3. Deletion-fidelity (mature in mech-interp; FaCT 2510.25512 formalizes C^2-Score 2025).** Delete the top-K attributed atoms, measure output drop. Faithful explanations show output drop monotone in deletion fraction. Substrate's introspection toolkit Cat6 (DELETION-CERT) was the BUG that put toolkit in MIDDLE_BAND -- before=0.06, after=0.01, other_intact=0.00, op=False. The deletion mechanism EXISTS in code but did not operate. This is a fix-the-implementation gap not a mechanism-doesn't-exist gap.

P_deflated A1 = 0.55; A2 = 0.55; A3 = 0.50 (with calibration penalty + cap on novel-synthesis).

---

## ANGLE B -- BRAIN (ACC + lateral PFC + confabulation cautionary)

**B1. Right rostrolateral PFC introspective access (Fleming 2014; PMC11775761 frontopolar-causally-guides-metacognition 2025).** Two-layer brain account: layer-1 first-order task computation; layer-2 metacognitive readout from frontopolar. Substrate maps directly: layer-1 = multi-bank retrieval + refuse-gate (existing); layer-2 = a separate readout HEAD trained to predict layer-1's correctness from its own internal state (cosine_sep, entropy, cleanup margin). The 2025 macaque PFC paper (Cell Neuron S0896-6273(25)00887-6) shows layer-2 INTEGRATES multiple components (remembered locations + uncertainties + trial history + arousal in baseline). Substrate's analog: integrate cosine_sep + entropy + partition_density + bind-margin into a single layer-2 explanation signal. Important: layer-2 must be a SEPARATE pathway from layer-1 (per the macaque paper), otherwise it's not metacognitive, it's just layer-1's output relabeled.

**B2. ACC conflict-detection as graded explanation-confidence (Botvinick 2004; Carter 2007).** ACC fires when first-order computation is in conflict (multiple competing responses). Substrate has refuse-gate at V_REL=256 -- binary today. Upgrade to CONTINUOUS conflict signal = cosine_top1 - cosine_top2 (margin). Per-step explanation includes per-hop conflict; high-conflict hops get flagged as "uncertain step in explanation," matching the brain's introspective access to ITS OWN ambiguity. This is a 10-line addition to the existing 2hop_chain code.

**B3. Confabulation cautionary (Hirstein 2009 / 2024 ACL "Confabulation: Surprising Value"; Wikipedia entry on neural-net confabulation as architectural pattern).** When introspection FAILS, brain (and LLMs) emit plausible-coherent-confident-WRONG narratives. The substrate's introspection toolkit Cat5 result -- 42% wrong-confident -- is exactly this. The fix is NOT to suppress the explanation (substrate would just go silent more often), it is to ATTACH faithfulness-confidence to each explanation so downstream consumers can route low-faithfulness explanations to "I cannot explain this" rather than to a plausible-but-fabricated trace. Brain doesn't always know when it's confabulating; the substrate-product opportunity is that substrate's algebra CAN tell when (deletion-fidelity test gives ground truth) -- the architecture is potentially BETTER than the brain on this axis. (P_deflated 0.50 with novel-synthesis cap.)

P_deflated B1 = 0.55 (brain existence-proof bump per MEMORY); B2 = 0.55; B3 = 0.50.

---

## ANGLE C -- CROSS-DOMAIN ML (mechanistic interpretability + sparse autoencoders + VSA-as-probe)

**C1. Hyperdimensional Probe (researchgate 395972393, 2025) -- VSA as interpretability probe FOR LLMs.** External research is using VSAs (the substrate's exact algebra) as a probe for LLM internals because VSA orthogonality + unbind are the cleanest known interpretability operators. Strong outside-validation: the substrate has the explanatory primitive AS its native compute, not as an attached probe. P_deflated 0.60 (highest -- direct lit precedent + substrate-natural).

**C2. Attention-as-Binding (arxiv 2512.14709, December 2025).** Recent transformer interpretability work proposes "explicit binding/unbinding heads and hyperdimensional memory layers" as architectural biases for faithful reasoning -- substrate IS this architecture. The transformer community is trying to retrofit what substrate has by construction. The unbind operation IS the trace primitive -- given output O and stored bind (key K, value O), unbinding O by K^{-1} recovers exactly K. Per-output trace = sequence of unbinds against stored keys. This is O(K*N_DIM) compute, vs transformer attention which is O(seq^2 * d) and uninterpretable.

**C3. Sparse-autoencoder faithful RAG (arxiv 2512.08892, December 2025).** SAEs over RAG decode "which retrieved doc influenced which output token". Substrate's analog: store retrieval into a per-partition SAE-like sparse code at write time; at read time, decode which sparse-code atom contributed to output. The substrate's M=10M partition routing is ALREADY a sparse code (each query routes to a small subset of partitions). The substrate-product framing: substrate is "RAG with native faithful attribution built into the storage primitive," which is what 2025 lit is trying to bolt on.

P_deflated C1 = 0.60; C2 = 0.55; C3 = 0.45 (sparse-autoencoder claim is novel-synthesis cap territory).

---

## TESTABILITY (substrate-eligible; no language dependence; CPU; per USER directive)

All three angles converge on the same buildable test:

**Faithfulness test design (deletion-counterfactual is the lit-standard; substrate executes it natively):**

1. Substrate answers query Q (via existing retrieval), emits answer A and EXPLANATION_TRACE = ordered list of [(input_atom_id, contribution_score, per_step_metacog_confidence)] reconstructed by reverse-cleanup of A through stored binds.
2. For each input_atom_id in EXPLANATION_TRACE, run ablation arm: re-query Q with that atom DELETED from substrate store, observe answer A'.
3. Faithfulness score = correlation(contribution_score_i, distance(A, A'_i)) over the K trace steps. Faithful explanation: deleting high-contribution atoms changes answer; deleting low-contribution atoms doesn't.

Discriminators below specify the bands. Implementations exist in `experiments/exp_substrate_audit_chain_coherence_benchmark_v1.py` (need fix for refuse-gate bug + calibration); `experiments/exp_substrate_introspection_toolkit_*` (need Cat6 deletion-cert to operate).

---

## TOP-2 CELL PROPOSALS (CPU-eligible; falsifiable; rank-ordered)

### Cell #1 -- `self_explanation_deletion_fidelity_v1` (Angle A1 + A3 + C1; recommended Top-1; P_deflated 0.55)

**Mechanism:** Substrate retrieves answer A for query Q. EXPLANATION_TRACE = top-K=5 input atoms by reverse-cleanup contribution score (HRR unbind O against stored keys, sorted by |inner product|). For each atom in trace, perform deletion-counterfactual: re-query Q with that atom's bind subtracted from the partition; measure output delta. Faithfulness = Spearman rho(contribution_score, output_delta) over K=5 atoms x N=500 queries x 3 seeds.

**Arms (3; arms-must-differ per META_RULE_AF):**
- ARM_TRUE_TRACE: top-K by reverse-cleanup contribution score (the substrate's actual explanation).
- ARM_RANDOM_TRACE: K random stored atoms (oracle-explanation strawman; faithfulness should be ~0).
- ARM_COSINE_TRACE: top-K by simple cosine to query Q (a confound -- "the obvious explanation" not necessarily the causal one; faithfulness < TRUE_TRACE if substrate compute uses binds, not raw cosine).

**Discriminator (concrete; HARD-PASS / HARD-FAIL pre-registered):**
- HARD_PASS: ARM_TRUE_TRACE Spearman rho >= 0.70 AND ARM_RANDOM_TRACE rho in [-0.10, +0.10] (chance) AND TRUE_TRACE rho > COSINE_TRACE rho by >= 0.15 (substrate-novel: binds give better attribution than raw similarity).
- HARD_FAIL: ARM_TRUE_TRACE rho < 0.40 (explanation does NOT track output causation -- confabulation regime) OR TRUE_TRACE - COSINE_TRACE <= 0 (no lift over the trivial explainer; substrate's "audit" claim is unsupported).
- MIDDLE_BAND: TRUE_TRACE rho in [0.40, 0.70] OR TRUE_TRACE - COSINE_TRACE in [0.05, 0.15].

**By-construction-saturation check (per META_RULE_H + USER 2026-06-22):** If ARM_COSINE_TRACE alone hits HARD_PASS, attribute the win to substrate's bind being equivalent to cosine at this scale and require N_DIM x M_BINDS regime where binds are non-trivially different (cleanup margin < 0.1) before claiming the chain primitive adds value.

**Substrate prereqs verified:** HRR unbind primitive (hdlab/hrr.py, smoke-tested); multi-bank partition routing (in flight); refuse-gate exists (chain-grade individually). DO NOT compose on cortex_E_tensor (HARD_FAIL at harder regime).

**§9 CRLB pre-validation:** Cramer-Rao on Spearman correlation: with N=500 queries x K=5 = 2500 (rho, delta) pairs, SE(rho) ~ 1/sqrt(N) ~ 0.02. HP threshold (rho >= 0.70) is reachable in ~35 SEs from chance. Discriminator IS measurement-feasible.

**META_RULE_AC (predispatch_check):** run `tools/predispatch_check.py self_explanation_deletion_fidelity_v1` before spawn.

**Critical lesson applied:** `substrate_audit_chain_coherence_benchmark_v1` HARD_FAIL had refuse_threshold = 0.55 * mean_known_conf = 0.025 -- below the noise floor. This cell must compute threshold AFTER measuring noise distribution and set it at the cosine-percentile that maximizes refuse_accuracy on calib set. (Specified in cell author's pre-reg.)

**Compute:** 500 queries x 5 trace-steps x 3 arms x 3 seeds x 2 (with/without deletion) = 45000 retrievals. CPU on laptop ~10-20 min. CARDINALITY_OK pre-reg: EXPECTED_N_UNITS = 45000.

**Smoke discipline (THREE SMOKE DISCIPLINES 2026-06-26):** no silent except; smoke FIRES discriminator (must observe ARM_TRUE_TRACE rho > ARM_RANDOM_TRACE rho at smoke-N before full dispatch); band-floor result = MIDDLE_BAND not HARD_PASS.

---

### Cell #2 -- `self_explanation_per_step_metacog_attribution_v1` (Angle B1 + B2 + A2 NeuroFaith; P_deflated 0.50)

**Mechanism:** For each step in EXPLANATION_TRACE (K=5 reverse-cleanup hops), compute per-step metacognitive confidence using the already-chain-grade single-signal AUROC=0.86 detectors (cosine_sep_per_hop, entropy_per_hop, cleanup_margin_per_hop). Compose into per-step confidence score in [0,1]. Then NeuroFaith Attribution-Agreement test: cosine(forward_attribution_vector, claimed_attribution_vector) where forward = deletion-derived ground truth attribution per atom (from Cell #1's deletion arm), claimed = substrate's emitted per-step confidence-weighted contributions. AA score in [-1, +1].

**Arms (3; structurally distinct):**
- ARM_PER_STEP_METACOG: per-hop confidence integrated via product (independence assumption).
- ARM_GLOBAL_METACOG: single per-query metacog signal (existing chain-grade) applied uniformly across all K steps (control -- does per-step add value?).
- ARM_CONSTANT_CONFIDENCE: confidence = 1.0 uniform (strawman; tests whether confidence-weighting matters at all).

**Discriminator:**
- HARD_PASS: ARM_PER_STEP_METACOG AA >= 0.60 AND AA > ARM_GLOBAL_METACOG AA by >= 0.10 AND AA > ARM_CONSTANT AA by >= 0.20 (per-step confidence adds structurally orthogonal information beyond global confidence; matches metacog-composition-failures lesson 2026-06-27 about signal independence).
- HARD_FAIL: ARM_PER_STEP AA < 0.30 (no attribution agreement -- substrate's claimed attribution is uncorrelated with actual attribution -- this is the confabulation HARD-FAIL band) OR ARM_PER_STEP - ARM_GLOBAL <= 0 (per-step adds no value over global; brain layer-2 mapping doesn't hold for substrate).
- MIDDLE_BAND: AA in [0.30, 0.60].

**Independence pre-check (DISCRIMINATOR-MEASURES-MECHANISM lesson from 2026-06-27):** Before claiming per-step adds value, verify Pearson rho between per-step and global metacog signals < 0.4 on calib set. If correlated >= 0.4, the bar is unfair -- per-step CANNOT add information over global, so HARD_FAIL would be a measurement artifact not a mechanism failure. Cell author must report this rho explicitly.

**Substrate prereqs verified:** cosine_sep AUROC=0.86 (verified `data/exp_meta_knowledge_partition_coverage_v1/metrics.json`); entropy AUROC=0.86 (same); HRR unbind for per-hop margin computation.

**§9 CRLB:** AA is bounded cosine; with K=5 dimensions per atom-vector, SE ~ 1/sqrt(K) ~ 0.45 per query, SE_mean over N=500 queries ~ 0.02. HP threshold AA >= 0.60 reachable in 30 SEs from zero. Measurement-feasible.

**Critical:** Cell #2 depends on Cell #1's deletion-derived ground truth attribution. If Cell #1 HARD_FAILs (substrate's trace is unfaithful at the deletion level), Cell #2 is undefined -- there's nothing for AA to agree with. Run Cell #1 first.

**Compute:** 500 queries x 5 trace-steps x 3 arms x 3 seeds = 22500 forward retrievals + reuse Cell #1's deletion data = ~10-15 min CPU.

---

## CROSS-THREAD SYNTHESIS

This drill closes the M3 glass-box loop ALONGSIDE the existing metacog stack:
- "Do I know this?" -> 2026-06-27 metacog-drill (partition coverage v2 in flight)
- "How confident am I?" -> chain-grade today (cosine_sep AUROC=0.86, entropy AUROC=0.86)
- "WHY did I say X?" -> THIS DRILL (deletion-fidelity + per-step-attribution)
- "When my explanation is wrong, can I detect it?" -> Cell #1 HARD_FAIL band IS this detector (low TRUE_TRACE rho = "do not trust this explanation," route to refuse)

The 4 layers compose into a glass-box stack. Per USER M3 spec (12-18 mo, 10-property test), faithful self-explanation is property 7-8 of the 10. Closing this in Stage 3 unblocks the M3 demo path.

Negative paths considered and rejected this drill:
- "Train a separate explainer head with backprop" -- substrate doesn't use backprop; would violate substrate-native discipline.
- "Have LLM summarize substrate trace post-hoc" -- this is exactly the post-hoc rationalization confabulation pattern; would render the audit story moot.
- "Use the existing audit_chain_depth_v1 Merkle primitive" -- crypto chain doesn't address substrate-internal causation, only tamper-evidence.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

If Cell #1 HARD_PASS: substrate provides faithful per-output attribution (rho >= 0.70 with deletion-counterfactual) -- a CAPABILITY 2025 RAG/LLM lit is actively trying to retrofit (Wallat ICTIR 2025 documents 57% citation-unfaithfulness in LLMs; substrate could ship at <10%). This is the substrate-product differentiator on the "doctor who can show their work" axis, directly addressing the M3 glass-box requirement.

If Cell #2 HARD_PASS additionally: substrate provides PER-STEP CONFIDENCE over its explanation trace -- the brain analog (rostrolateral PFC layer-2 readout) maps cleanly. The substrate-product feature is "I am 0.92 confident about step 1, 0.45 confident about step 2, 0.88 confident about step 3 of my answer," which is a structurally novel feature LLMs cannot ship today (transformer attention does not decompose into discrete confident steps).

If both HARD_FAIL: substrate cannot ship faithful self-explanation at current scale. M3 glass-box target requires either fundamental upgrade to bind primitive (P_low) or external probe (defeats the substrate-native claim). This would be informative -- it would tell us the introspection toolkit MIDDLE_BAND was an upper bound, and M3 timeline needs revision.

If Cell #1 HARD_PASS but Cell #2 HARD_FAIL: substrate has faithful attribution at the atom level but not at the per-step level -- substrate IS auditable but not in a human-narratable form. Substrate-product framing shifts to "machine-checkable provenance, not human-readable rationale" -- still M3-positive but a different demo path.

---

## CITATIONS (verified count: 9 external + 6 internal)

External lit (2024-2025):
1. NeuroFaith: Liu et al. "Evaluating LLM Self-Explanation Faithfulness via Internal Representation Alignment" arxiv 2506.09277 (June 2025) -- AA metric.
2. FaCT: "Faithful Concept Traces for Explaining Neural Network Decisions" arxiv 2510.25512 (October 2025) -- C^2-Score concept-consistency.
3. Wallat et al. "Correctness is not Faithfulness in Retrieval Augmented Generation Attributions" ICTIR 2025 / SIGIR -- 57% unfaithful citations.
4. Frontopolar-PFC causal metacognition: PMC11775761 (2025) -- two-layer metacognition account.
5. Macaque PFC working-memory metacognition: Cell Neuron S0896-6273(25)00887-6 (2025) -- multi-component integration in PFC.
6. Annual Reviews "Metacognition and Confidence" 2024 -- review synthesis.
7. Confabulation as substrate cautionary: Hirstein "Brain Fiction" (2005) + ACL 2024 "Confabulation: Surprising Value" -- coherent-confident-wrong pattern.
8. Hyperdimensional Probe: researchgate 395972393 (2025) -- VSA as LLM interpretability probe (substrate has this natively).
9. Attention-as-Binding: arxiv 2512.14709 (December 2025) -- transformer interp work converging on bind/unbind primitive.

Internal (verified on disk):
- `data/exp_substrate_audit_chain_coherence_benchmark_v1/metrics.json` (HARD_FAIL full)
- `data/exp_substrate_introspection_toolkit_full_10_categories_v1/metrics.json` (MIDDLE_BAND; 42% wrong-confident)
- `data/exp_causal_audit_chain_depth_v1/metrics.json` (HARD_PASS but Merkle hashes only)
- `data/exp_causal_chain_extraction_end_to_end_v1_smoke/metrics.json` (HARD_FAIL smoke)
- `data/exp_cortex_E_tensor_HARDER_REGIME_v1/metrics.json` (HARD_FAIL -- don't compose here)
- `notes/research_drill_3x_substrate_self_monitoring_metacognition_2026-06-27.md` and `notes/research_drill_2x_metacog_composition_failures_2026-06-27.md` -- metacog stack state.

---

## CONTRACT

- Research OWNS mechanism claims + falsifiable bands.
- exp_dev (spawn `hdi_exp_dev` per agent-spawn-only) OWNS cell-spec authoring + smoke + dispatch.
- Skunkworks (spawn `hdi_skunkworks`) OWNS landed-VET classification per by-construction-saturation default (MM until cert-owner tiers up).
- Per Fix #28: read per-arm metrics, not verdict_msg framings.
- CARDINALITY_OK pre-reg fields populated (Cell #1: 45000; Cell #2: 22500).
- Fix #26 predispatch_check before spawn.
- META_RULE_AB lesson applied: independence pre-check before claiming composition lift.
- Per `feedback_test_rationality_encoding_before_readout`: the encoding mechanism here is HRR unbind on stored binds (well-defined, deterministic, substrate-native). Readout test (deletion-fidelity) is downstream and well-specified.

---

## Word count: ~1980
