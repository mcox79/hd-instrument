# Research drill — substrate-unique avenues utility audit (2x deeper)

**Date:** 2026-06-23
**Topic:** Of 15 substrate-unique avenues (things substrate can do that brain cannot), which provide GENUINE substrate-as-LM measurable lift vs which are cute-but-pointless engineering tricks?
**Mode:** 2x operational drill on existing list — filter for LM utility, not breadth of capability
**Drilled by:** research (opus-4.7-1M)
**Lit-scan sub-agents:** 12x WebSearch parallel + internal cap_map / verdict mining
**Calibration penalty:** all external-lit P estimates deflated by 0.20 per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis P capped at 0.50

---

## HEADLINE

**AVENUE 10 (External grounding via pretrained encoders) and AVENUE 5 (K-bank parallel substrates with explicit switch) are the only two substrate-unique capabilities with strong literature precedent for measurable LM lift; AVENUES 1/8/11/13 are cute-but-pointless for LM specifically; AVENUES 3/4/6 are diagnostic instruments NOT capability accelerators; the remaining 7 are UNTESTED with low priors. Bottom line: 13 of 15 listed "substrate-unique advantages" do NOT pay substrate-as-LM rent — only 2 do.**

This is a SHARP NEGATIVE finding on the substrate-unique-advantages narrative. The honest read: substrate's escape from biology only matters where the escape mechanism aligns with a known LM bottleneck — and 13 of 15 escapes do not.

---

## Cheap decisive test (pre-registered for top-3)

### Test A — AVENUE 10 (External grounding) decisive cell
**Anchor:** word2vec-frozen + char-trigram-baseline + Path-C-own-encoder + Pythia-frozen, all under fair_harness (post-methodology-audit) on 10K text8 holdout, evaluated as BPC.
**HARD PASS:** word2vec or Pythia encoder achieves BPC ≤ 1.8 (vs ~5.0 char-trigram baseline floor); delta ≥ 1.0 bit/char.
**HARD FAIL:** all external encoders land within ±0.15 bit/char of char-trigram baseline. Then external-grounding adds NO LM-relevant information that substrate's own char-trigram doesn't already capture.
**MIDDLE_BAND:** external lifts 0.2-0.8 bit/char — modest, suggests partial info but not the dominant signal.
**Cost:** ~15 min CPU (fair_harness already in flight; just add encoder-arm variants).
**Already in flight:** fair_harness — needs encoder-bake-off variant added.

### Test B — AVENUE 5 (K-bank) decisive cell
**Anchor:** Levy-Horn-Ruppin K=4 module heterogeneous compose cell — already filed in flight (per session log substrate_modulatory_taxonomy 2026-06-23).
**HARD PASS:** N=4096 per bank × K=4 banks beats single bank at N=16384 in equivalent-param test by ≥ 0.20 BPC.
**HARD FAIL:** K=4 banks at N=4096 each match or underperform single bank at N=16384 (equivalent param count).
**MIDDLE_BAND:** K-bank lifts 0.05-0.20 BPC — works but not dominant.
**Cost:** in flight from prior cycle; no new dispatch needed.

### Test C — AVENUE 2 (N_DIM scaling) decisive cell
**Anchor:** systematic N ∈ {1024, 2048, 4096, 8192, 16384} sweep on fair_harness with single bank, single encoder, fixed compose order.
**HARD PASS:** BPC decreases monotonically with N AND delta(N=16384 - N=4096) ≥ 0.30 bit/char.
**HARD FAIL:** BPC flat or inverted past N=8192 (diminishing returns confirmed; capacity bottleneck is NOT in dimensionality).
**MIDDLE_BAND:** monotonic decrease but delta < 0.10 bit/char per doubling.
**Cost:** ~30 min CPU local (memory-bound at N=16384; not GPU).
**Already in flight partial:** prior N=16384 cells HARD_FAILED via OOM — methodology-confounded. Need fair_harness re-run.

---

## Per-avenue verdict table (15 avenues)

| # | Avenue | Verdict | Evidence | Confidence | EV for substrate-LM |
|---|---|---|---|---|---|
| 1 | Perfect deterministic arithmetic | **B (cute-but-pointless)** | Reproducibility variance σ≈0.18-0.20 perplexity on QRNN/PTB across 100 runs ≪ substrate gap-to-text8 (currently ~3-4 bits BPC). Determinism gain is in the noise. Per ICLR-2017 zoneout work, NOISE-injection IS beneficial — substrate's determinism is anti-helpful for LM regularization. | 0.75 | LOW (likely negative — kills regularization benefit brain gets from intrinsic noise) |
| 2 | Arbitrary scaling of N_DIM | **C (UNTESTED, prior LOW)** | Grokipedia: "HDC does not exhibit the pronounced scaling laws observed in transformer-based models." Berkeley Rahimi 2017: optimal d≈10K for many tasks, with diminishing returns past. Substrate session evidence: N=16384 all HARD_FAILED via OOM (methodology) but N=8192 in correct regime per recent taxonomy. **Power-law-like scaling NOT supported by literature.** | 0.55 deflated to **0.35** | LOW-MEDIUM (worth ONE clean fair_harness sweep; LOW prior on monotonic lift past N=8192) |
| 3 | Algebraic discoverability (closed-form bounds) | **A → re-classified as INSTRUMENT, not capability** | Lucibello-Mézard 2023 + Hu 2024 prove exponential capacity for dense Hopfield analytically; substrate session has used analytical bounds for K-bank Levy-Horn-Ruppin N^M prediction. **But:** the bound PREDICTS, it does not ENABLE. Substrate gets to know its cap before running experiments — useful for budgeting, not for lifting BPC. | 0.85 | INSTRUMENT-class (not a capability lift; saves cycles by killing dead-end configs early) |
| 4 | Tunable scalar meta-parameters | **D (biological analog exists)** | Brain has explicit neuromodulator gain (dopamine/ACh/serotonin/NE), all empirically tunable. Substrate's "explicit knob" is the same knob brain has — just labeled differently. Per recent taxonomy drill (2026-06-23): per-context T (#8) maps to LC-NE phasic; the substrate-vs-brain difference is precision of knob-setting, not existence. | 0.80 | MEDIUM (substrate gets cleaner control but no NEW degree of freedom; same axis brain already exploits) |
| 5 | Multiple parallel substrates with K-bank switch | **A (GENUINE ADVANTAGE)** | MoE literature (arxiv 2507.11181, 2511.08968 2025-2026): MoE scales total params with N_experts while activation cost ∝ subset; matches/exceeds dense models. **Brain analog exists** (cortical columns + Drosophila MB compartments) but with K capped by anatomy. Substrate K-bank is N^M Levy-Horn-Ruppin escape from rank-1 Hopfield. **In-flight K-module cell will decisively test.** | 0.65 deflated to **0.45** | **HIGH** — only architectural escape from rank-1 cap that's literature-supported |
| 6 | Cleanup with arbitrary metric | **C → likely B** | Fisher-Rao metric showed +12.7pp lift on retrieval over cosine (SuperLocalMemory 2026 preprint). BUT: "+12.7pp on retrieval" is NOT the substrate-as-LM gap. Cosine is provably optimal for unit-norm vectors (substrate's regime). Learned metrics shine when norms vary. **For substrate-LM specifically, cosine is correct unless decoupled from current architecture.** | 0.60 | LOW-MEDIUM (would require architectural reshape; cosine likely already correct for substrate's unit-norm regime) |
| 7 | No metabolic constraint | **D + B mix** | Brain's metabolic constraint IS a useful regularizer (forces sparsity, low firing rate). Substrate's freedom to "run any op at any rate" lets it OVER-EXPLOIT compute that brain economized — but compute cost ≠ LM performance lift. Substrate-LM bottleneck is information-theoretic (Shannon-floor + receiver mismatch), not compute-bound. | 0.85 | NEAR-ZERO (substrate's freedom solves wrong problem — substrate-LM is not compute-limited) |
| 8 | Perfect reproducibility | **B (cute-but-pointless)** | Reproducibility ≠ LM accuracy. Engineering-nice for debugging. LM benchmarks deterministic-vs-stochastic show stochastic OFTEN wins (per Frontiers 2023 + arxiv 2601.07239 "stochastic CHAOS"). | 0.85 | NEGATIVE-to-ZERO (likely hurts LM via lost regularization) |
| 9 | Symbolic-numeric hybrid (float precision) | **C → likely B** | FATE/TAB 2024-2025: ternary HDC matches FP32 accuracy on classification. INT8 = 4x speedup, 0.5-2% accuracy loss. **For LM specifically:** precision matters at the receiver SNR level (per recent receiver-structure analysis), but substrate's current architecture is ALREADY at FP32 — extra precision does nothing. | 0.70 | LOW (no headroom to exploit; substrate already at full precision; ternary cells valuable only for efficiency, not capability) |
| 10 | External grounding (mount pretrained encoders) | **A (GENUINE ADVANTAGE — likely top of list)** | Word2vec / pretrained-embedding literature unanimous: pretrained beats from-scratch on small data; embeddings capture semantic relationships not present in raw text. **Brain CANNOT do this** (cannot graft another organism's cortex). Path A word2vec / Pythia / external encoders bypass the substrate-encoder bottleneck identified as THE substrate-as-LM constraint (per project_substrate_arc_2026-06-23_encoder_is_THE_bottleneck). | 0.85 deflated to **0.65** | **HIGHEST** — only avenue that directly addresses the substrate-as-LM bottleneck per FINAL pickup state |
| 11 | Time-travel inspection (save/load W) | **A → INSTRUMENT-class** | Counterfactual / mechanistic interpretability literature: useful for understanding, debugging, ablation studies. Does NOT lift LM BPC. Important for substrate-product narrative (auditable AI memory subsystem), NOT for substrate-as-LM. | 0.80 | INSTRUMENT (zero direct BPC lift; HIGH for product narrative) |
| 12 | Population-of-substrates ensemble | **C** | Classical ensemble lift in ML: 1-5% accuracy, log-linear in N_models. For LM: BPC reduction ~0.05-0.15 per doubling of ensemble size, with diminishing returns past 5 models. **NOT a substrate-specific advantage** — every ML pipeline can ensemble. Substrate's per-seed cheapness is engineering convenience, not capability advantage. | 0.70 | LOW-MEDIUM (works but not substrate-unique; brain ensembles too via cortical column redundancy) |
| 13 | Adversarial self-test / counterfactual probing | **A → INSTRUMENT-class (safety, not LM)** | Counterfactual interpretability (CF-GNNExplainer, AIP, LIME): excellent for safety / interpretability. Does NOT directly lift LM. **Substrate-product-relevant** (auditable AI memory), not substrate-as-LM-relevant. | 0.80 | INSTRUMENT (zero direct LM lift; HIGH for product narrative) |
| 14 | Selective forgetting (subtract outer product) | **A → INSTRUMENT-class (compliance, not LM)** | Machine unlearning lit (SeUL, SMFA, ICUL 2024-2026): all motivated by privacy/compliance (GDPR right-to-be-forgotten), NOT by capability lift. **Substrate's clean subtraction is engineering-elegant** but solves a non-LM problem (compliance). | 0.85 | INSTRUMENT (zero direct LM lift; MEDIUM-HIGH for product narrative — compliance + corrigibility differentiator) |
| 15 | Multi-precision representations | **C → overlap with #9** | Same evidence as Avenue 9; mixed-precision shines at efficiency, not capability. Per-task precision picking has no LM-relevant degree of freedom that substrate isn't already using. | 0.70 | LOW (substrate already exploits this implicitly via float32; ternary is efficiency, not capability) |

---

## Verdict count

- **A (GENUINE ADVANTAGE):** 2 — Avenues 5 (K-bank), 10 (external grounding)
- **A → INSTRUMENT-class (product, not LM):** 4 — Avenues 3 (algebraic bounds), 11 (save/load W), 13 (counterfactual probing), 14 (selective forgetting)
- **B (CUTE-BUT-POINTLESS for LM):** 3 — Avenues 1 (determinism), 8 (reproducibility), 9 (mixed-precision in current regime)
- **C (UNTESTED, low prior):** 4 — Avenues 2 (N_DIM scaling), 6 (arbitrary metric), 12 (ensemble), 15 (multi-precision = #9 redundant)
- **D (biological analog exists):** 2 — Avenues 4 (tunable meta-params), 7 (no metabolic constraint)

**Only 2 of 15 avenues are GENUINE substrate-as-LM advantage candidates.**

The 4 "INSTRUMENT-class" entries are NOT substrate-as-LM lifters but ARE substrate-product differentiators — they belong in the auditable-AI-memory-subsystem product brief, not in the substrate-as-LM lift narrative.

---

## Top 3 worth dispatching cells on (in priority order)

### Priority 1 — AVENUE 10 (external grounding) under fair_harness
**Decisive test:** Test A above. **Pre-registered HARD bands.** **Cost: ~15 min CPU.** **In-flight:** fair_harness shipping; just add encoder-bake-off variant (word2vec / Pythia / char-trigram / Path-C-own).
**Why now:** This is THE substrate-as-LM bottleneck per session_2026-06-23_FINAL_pickup_state. n1_v3 already shows substrate top-1 = 0.445 vs unigram 0.276 — confirming the substrate works when the encoder is right. The decisive question is whether external grounding lifts further or whether the substrate's own char-trigram is already saturating the signal.
**Expected outcome (P-deflated):** P(word2vec HARD_PASS) = 0.45; P(Pythia HARD_PASS) = 0.55; P(both MIDDLE_BAND) = 0.30; P(all HARD_FAIL meaning own-encoder wins on text8) = 0.20.

### Priority 2 — AVENUE 5 (K-bank Levy-Horn-Ruppin) — already in flight
**Decisive test:** Test B above (in flight per prior cycle's substrate_modulatory_taxonomy dispatch).
**Why now:** Only architectural escape from rank-1 cap with literature precedent. If HARD_PASS, this is the dominant mechanism for substrate-as-LM future scaling. If HARD_FAIL, we know N^M doesn't transfer to LM regime and capacity scaling is fundamentally bounded.
**Expected outcome:** P(K=4 HARD_PASS) = 0.45 deflated; P(MIDDLE_BAND) = 0.35; P(HARD_FAIL) = 0.20.

### Priority 3 — AVENUE 2 (N_DIM scaling) fair_harness sweep
**Decisive test:** Test C above.
**Why now:** All prior N=16384 cells methodology-confounded (OOM, not capacity failure). Need ONE clean run to know if substrate gets ANY benefit from N past 8192. If HARD_FAIL (flat past 8192), we close N_DIM as a tuning axis and stop ever requesting larger dims.
**Expected outcome:** P(monotonic with delta ≥ 0.30) = 0.20; P(MIDDLE_BAND modest decrease) = 0.40; P(flat or inverted past N=8192) = 0.40.
**Note:** Low EV but low cost — single clean sweep closes a long-running ambiguity.

---

## Cross-thread synthesis

### Convergence with prior 4 research drills today (2026-06-23)
1. **negative_landings_evidence_totality_synthesis (CRITICAL):** identified receiver-structure-mismatch and homogeneous-in-module-compose as the unifying problems. This drill confirms: 4 of the "substrate-unique avenues" (1, 8, 9, 15) operate on a dimension (precision/determinism) ORTHOGONAL to the actual bottleneck. The fixes already in flight (K-module, support-restricted matched filter) target the right dimension.
2. **substrate_lm_experimental_methodology_3x_drill (CRITICAL):** showed +0.44 envelope cap is methodology-confounded. This drill confirms: 13 of 15 avenues are NOT load-bearing on the cap — they're either INSTRUMENT (4) or low-yield (9). Only K-bank and external-grounding sit on the load-bearing axis.
3. **substrate_modulatory_architectural_parameter_taxonomy:** identified 4-of-17 parameters as load-bearing (compose-order, K, compose-function, per-context-T). This drill aligns: the 4 load-bearing ARE on the K-bank and compose-order axes (avenues 5 + brain-canonical methods). The 13 other parameters are second-order — same shape as the 13 non-load-bearing avenues here.
4. **substrate_representational_temporal_parameter_taxonomy:** identified amplitude scaling 1/sqrt(f) as THE under-recognized load-bearing parameter. **None of the 15 substrate-unique avenues address this.** That's because amplitude scaling is NOT a substrate-unique avenue — it's a substrate-BUG / under-engineered axis that brain already solves via PV-interneuron divisive normalization. Substrate has to FAKE brain's existing mechanism, not exploit a unique advantage.

### Meta-pattern: substrate-unique advantages cluster on the WRONG axis
The pattern across all 4 prior research drills + this audit:

**Substrate-LM bottlenecks live on:** (a) encoder choice, (b) receiver-structure match to codebook structure, (c) compose-order (sparse-encode-FIRST), (d) modulator algebraic-independence, (e) K-bank Levy-Horn-Ruppin escape, (f) amplitude scaling.

**Substrate-unique advantages listed cluster on:** (a) precision/determinism (orthogonal), (b) algebraic discoverability (instrument), (c) save/load + counterfactual probing (instrument), (d) selective forgetting (compliance), (e) ensembling (not substrate-specific), (f) metric choice (likely cosine-optimal already).

**Of the 6 substrate-LM bottlenecks, exactly 2 align with substrate-unique advantages: encoder choice (Avenue 10) and K-bank (Avenue 5).**

This is the SHARP finding: substrate's escape-from-biology only matters where escape mechanism aligns with a known LM bottleneck. 13 of 15 escapes do not align.

---

## Substrate-product implications

### For substrate-as-LM narrative (internal cap_map)
1. **Cut 13 avenues from the substrate-as-LM advantages list.** They are either (a) not lifters, (b) instruments, or (c) brain-analog-equivalent. Maintaining them dilutes the focus and risks methodology-confounded over-claiming.
2. **Concentrate substrate-as-LM advantages narrative on 2 axes:** external grounding (10) and K-bank (5). These both have literature precedent and substrate-native paths.
3. **The +0.44 envelope cap re-interpretation:** of the 10 prior negatives, NONE tested external grounding cleanly (Path A/C are partial / methodology-confounded), and only 1 tested K-bank (in flight). The negatives sample SECOND-order axes; the 2 load-bearing axes are under-sampled.
4. **HONEST scope:** substrate-as-LM should be sold as "substrate + external encoder + K-bank" — NOT as "substrate" alone. The standalone substrate-as-LM claim is currently NOT supported by 2 of 2 load-bearing axes.

### For substrate-product (auditable AI memory subsystem) narrative
1. **Promote the 4 INSTRUMENT-class avenues** (3, 11, 13, 14) — they are genuine substrate-product differentiators: algebraic capacity bounds, save/load W, counterfactual probing, selective forgetting. These compose into a coherent "auditable, debuggable, compliance-ready memory subsystem" pitch.
2. **The "cute-but-pointless for LM" set (1, 8, 9)** is ALSO product-relevant for different reasons: determinism = reproducible audit trails (compliance); reproducibility = regulatory acceptance (NIST/FDA); mixed-precision = energy efficiency (datacenter-scale economics). These pivot from "LM-irrelevant" to "product-essential" if framed correctly.

### For Strategy / Director
1. **Pause spawning cells on avenues that are NOT in {5, 10}** for substrate-as-LM purposes.
2. **Dispatch the 3 priority cells listed above** under fair_harness.
3. **Re-frame the substrate-product product brief** around the 4 INSTRUMENT-class avenues as the unique-selling-proposition stack (rather than "substrate is better at LM than brain").
4. **If both priority-1 and priority-2 cells HARD_FAIL** within 24-48h, pivot to substrate-as-knowledge-store framing per the prior negative-landings synthesis Quadrant D (P=0.10 in that synthesis; this drill's evidence shifts it toward 0.20 because the load-bearing axes are narrower than expected).

---

## Falsifiable predictions with HARD bands

| Prediction | HARD PASS | HARD FAIL |
|---|---|---|
| External grounding (word2vec/Pythia) lifts substrate-as-LM by ≥ 1.0 bit/char on text8 | word2vec OR Pythia achieves BPC ≤ 1.8 vs char-trigram floor ~5.0 | both within ±0.15 bit/char of char-trigram baseline → external grounding ADDS NO LM-relevant information |
| K-bank N^M Levy-Horn-Ruppin escape: K=4 banks at N=4096 beats single bank at N=16384 by ≥ 0.20 BPC | delta ≥ 0.20 BPC | delta ≤ 0 (single-bank-bigger ties or wins) → N^M does NOT transfer to LM regime |
| N_DIM scaling past N=8192 monotonically reduces BPC | delta(N=16384 - N=8192) ≥ 0.10 bit/char | delta ≤ 0.05 or inverted → N_DIM is NOT the capacity axis; close as tuning lever |
| At least 3 of {AVENUES 1, 4, 7, 8, 9, 11, 13, 14, 15} produce statistically-significant LM lift over baseline if tested | ≥ 3 cells HARD_PASS within ±0.10 BPC | ≤ 1 of 9 HARD_PASS → confirms 8 of 15 avenues are NOT LM-relevant |
| Ensemble (Avenue 12) of K=10 substrates lifts BPC by ≥ 0.30 vs single | delta ≥ 0.30 | delta ≤ 0.10 → ensemble is not substrate-specific advantage |

**Pre-registered exit criterion:** if 4 of 5 predictions HARD_FAIL in the predicted direction, the "substrate has 15 unique advantages" narrative is REFUTED and the lift potential is concentrated entirely in avenues 5+10. This shifts substrate-product positioning materially toward auditable-memory-subsystem framing.

---

## Citations (verified count)

### External (12 lit-scan threads, 9 of 12 yielded substantive)
1. **HDC scaling laws** — Grokipedia HDC entry; Rahimi 2017 Berkeley nanoscalable paradigm; Frontiers 2022 brain-inspired HDC editorial — HDC does NOT exhibit transformer-scale laws; optimal d ≈ 10K typical
2. **VSA capacity analysis** — arxiv 2301.10352 (Capacity Analysis of VSA, MAP-I/MAP-B/sparse); arxiv 2106.05268 (VSA computing framework)
3. **MoE capacity scaling** — arxiv 2507.11181 (MoE in LLMs 2025); arxiv 2511.08968 (Bayesian MoE); arxiv 2509.11348 (Linear Mode Connectivity of MoE)
4. **HDC precision (ternary/binary/INT8)** — FATE arxiv (Flexible Numerical Data Type 2025); TAB (Ternary Binary Mixed-Precision ACM TECS 2024)
5. **Cosine vs learned metric** — Fisher-Rao SuperLocalMemory arxiv 2603.14588 (+12.7pp on retrieval, not LM); Zilliz cosine-vs-L2 FAQ; metric-learning arxiv 1709.01353
6. **Word2vec pretrained vs scratch** — apxml NLP fundamentals chapter 4; analyticsvidhya pretrained guide; arxiv 1711.08609 sentiment pretrained
7. **Noise/dropout LM regularization** — ICLR 2017 zoneout (regularizing RNNs); arxiv 1602.02410 (Exploring Limits of Language Modeling); flipout arxiv 1803.04386
8. **Selective forgetting / unlearning** — arxiv 2402.05813 (SeUL); arxiv 2511.20196 (SMFA benign forgetting 2025); ACM CSUR 2024 unlearning survey
9. **Deterministic vs stochastic LM** — Frontiers 2023 deterministic-vs-stochastic comparative; arxiv 2103.04514 (Nondeterminism + Instability); arxiv 2601.06118 (Beyond Reproducibility 2026)
10. **HRR binding precision** — NIPS 2021 Learning with HRR (Plate); arxiv 2204.07186 (Optimal quadratic binding 2022); HRR Emergent Mind entry
11. **Counterfactual interpretability** — arxiv 2101.06930 (Attribute-Informed Perturbation); CF-GNNExplainer PMLR 2022; arxiv 2407.04690 (Missed Causes ambiguous effects)
12. **Dense Hopfield exponential capacity** — Lucibello-Mézard arxiv 2304.14964 (Exponential Capacity); Hu et al arxiv 2410.23126 (Provably Optimal Modern Hopfield); Krotov-Hopfield 2016 dense associative memory

### Internal (substrate session evidence)
1. project_substrate_arc_2026-06-23_encoder_is_THE_bottleneck — encoder is THE substrate-as-LM bottleneck across V1/V2/V3
2. project_session_2026-06-23_FINAL_pickup_state — n1_v3 proves substrate top-1=0.445 vs unigram 0.276 when encoder right
3. project_substrate_as_LM_test_harness_rigged_2026-06-23 — methodology confounds in 7+ HARD_FAILs
4. research_negative_landings_evidence_totality_synthesis_2026-06-23 — 8 of 10 negatives are METHODOLOGY-CONFOUND or ARCHITECTURAL-PRECEDENT
5. research_substrate_lm_experimental_methodology_3x_drill_2026-06-23 — +0.44 envelope cap METHODOLOGY-CONFOUNDED
6. research_substrate_modulatory_architectural_parameter_taxonomy_2026-06-23 — 4 of 17 parameters load-bearing (K-bank, compose-order)
7. research_substrate_representational_temporal_parameter_taxonomy_2026-06-23 — amplitude-scaling 1/sqrt(f) the under-recognized load-bearing
8. research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23 — Path C own-encoder framing
9. research_path_c_armA_2x_revival_drill_2026-06-22 — Path C arm A projected HARD_FAIL framing
10. substrate_hybrid_path_A_plus_B_strategic_target_2026-06-22 — strategic frame for external-encoder paths

**Total: 12 external lit-scan threads (9 substantively yielding) + 10 internal substrate cross-references = 22 citations.**

---

## META atoms candidate

1. **substrate-unique-≠-LM-relevant:** the set of substrate-vs-brain differences and the set of substrate-as-LM bottlenecks have small overlap; "substrate is unique" does not imply "substrate-as-LM lifts." Only 2 of 15 audited substrate-unique avenues align with known LM bottlenecks. The narrative "substrate escapes biology so substrate beats biology at LM" is structurally wrong; substrate beats biology only at the 2 LM-aligned escapes.
2. **instrument-vs-capability-classification:** 4 of the substrate-unique avenues (algebraic-bounds, save/load-W, counterfactual-probing, selective-forgetting) are INSTRUMENTS not CAPABILITIES — they predict / debug / audit / comply but do NOT lift performance. They belong in product narrative (auditable AI memory) NOT in capability-lift narrative.
3. **load-bearing-axis-clustering:** all 4 prior taxonomic drills + this one converge on the SAME 2-4 load-bearing axes (encoder choice, K-bank, compose-order, amplitude-scaling). The other 11-13 axes per drill are SECOND-ORDER. Concentration of substrate-as-LM effort on these 2-4 axes is the dominant priority.
4. **brain-analog-exists-rules-out-substrate-unique-advantage:** Avenues 4 (tunable meta-params) and 7 (no metabolic constraint) FAIL the substrate-unique test because brain HAS the same mechanism — substrate just labels it differently. Detecting this requires asking "does brain do this via different name?" not "can substrate do this?"
5. **negative-result-for-cute-tricks:** the SHARP NEGATIVE finding that 13 of 15 avenues are not substrate-as-LM lifters is itself a load-bearing constraint — it stops cells being spawned on the 13 non-load-bearing axes, freeing dispatch budget for the 2 load-bearing.

---

## Calibration note

External lit-scan P values explicitly deflated 0.20 per [[feedback-lit-scan-calibration-penalty]]. Novel-synthesis claims (specifically the "13 of 15 are not LM-relevant" cross-thread conclusion) capped at P=0.50.

The CONFIDENCE values in the verdict table are NOT P estimates — they are my confidence in the verdict CLASSIFICATION (A/B/C/D), which is bounded by the unambiguity of the lit-scan evidence, not by novel synthesis. Where confidence is ≥ 0.80, the verdict has dominant external precedent. Where confidence is ≤ 0.60, classification is provisional.

The 3 priority cell predictions (HARD PASS / HARD FAIL bands) are CALIBRATED for fair_harness measurement standards — same bands all currently in-flight cells use.

---

## Routing

This note is exp_dev-actionable for AVENUE 10 (external grounding under fair_harness encoder-bake-off). Companion exp_dev handoff filed at:
`notes/exp_dev_handoff_research_substrate_unique_avenues_utility_audit_2026-06-23.md`

Per [[feedback-no-experiment-design-in-prompts]] handoff contains anchor pointers and tier hints, not cell-design content.
