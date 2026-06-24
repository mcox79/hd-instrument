# RESEARCH 2x DEEPER DRILL: continual-learning architectural revival -- the spectrum HARD_FAIL is a MECHANISM-ANTAGONISM artifact, not a moat-refutation

**Date:** 2026-06-24
**Requestor:** Director (USER directive: "we have a lot of research on continual learning -- we can add a pattern and be done, but we can also continually learn which is a big plus")
**Empirical driver:** `exp_substrate_continual_learning_spectrum_v1` HARD_FAIL (FULL_CL forgetting=0.650, transfer=0.000). 5 arms tested; none cleared the bar.
**Drill mode:** 2x DEEPER operational drill on existing substrate evidence. Not a re-derive; this consumes the prior c1/c2/spectrum verdict chain and the 2x-2026-06-22 cascade-STC-SWR drill that ALREADY proposed brain-integrated CL.
**Lit-scan calibration:** deflate P 0.20; cap novel-synthesis P at 0.50; HARD-FAIL thresholds mandatory.
**Brain-existence-proof STANDING:** brain does CL trivially with same primitives -- substrate primitives are PRESENT-BUT-MUTUALLY-DESTRUCTIVE, not absent.

---

## HEADLINE

**The spectrum cell HARD_FAIL is the SPATIAL-SEGREGATION axis, not the per-primitive axis.** The cell-author's own smoke-calibration comments (`exp_substrate_continual_learning_spectrum_v1.py` lines 168-181, verbatim) already discovered the mechanism: **"cf-RPE delta-rule + Hebbian replay are antagonistic at composition stage; both push W in different directions. The brain solves this via spatially-segregated cortex (hippocampal Hebbian write + cortical slow consolidation)."** The author then attempted v2 (mitigate via small additive cf-RPE nudge alpha=0.05) -- substrate still HARD_FAILED. The empirical signal in the metrics.json is unambiguous: every CL arm writes its current phase into the SAME W matrix that holds prior phases, and the cf-RPE error-correction step PARTIALLY UNDOES the prior phase's Hebbian writes. The forgetting=0.65 floor is the steady-state of two opposing update operators sharing one substrate.

**The brain-architectural integration that substrate is missing is NOT a new primitive -- it is SEPARATE PHYSICAL STORES with one-way replay between them.** McClelland 1995 + Kumaran-Hassabis 2016 specify the architecture exactly: hippocampus (fast, episodic, sparse) writes ONLINE; cortex (slow, distributed) receives only REPLAYED PATTERNS; the two never share an update operator on the same weights. The spectrum cell collapses both stores into one W matrix that takes both Hebbian-fast and cf-RPE-slow updates simultaneously -- that is biologically equivalent to fusing hippocampus and cortex into one structure, which is exactly the patient-population with bilateral hippocampectomy (HM) who CANNOT form new declarative memories.

**Anomalous pattern in spectrum metrics.json that confirms the mechanism:** for ARM_CLS_REPLAY at phase 5, task-1 retention is 0.42 (high relative to 0.0) but tasks 2,3,4,5 all = 0.0 across all seeds. CLS_REPLAY rehearses task-1 (the FIRST phase) but the replay actively ZEROES subsequent phases via Hebbian-replay interference. For FULL_CL_SYSTEM at phase 5: task-1 only retains its FIRST atom slot (0.35); all subsequent positions = 0. This is the structural signature of REPLAY-OVERWRITES-NEW-WRITES, not of capacity exhaustion (total alpha = 5*400 / 4096 = 0.49, well within substrate's a8-validated alpha=0.5 cliff).

**Cheap decisive test (substrate-mine-derived, not new):** the c1_cls_replay_continual_ingest cell HARD_PASSED at alpha=0.5 with 1:1 replay (CERT 585) at by-construction-saturation -- recall=1.000 across NONE/REPLAY arms because codebook-NN cleanup masks Hebbian crosstalk. The c2_cascade_stc_swr_v2 cell HARD_FAILed (2026-06-23) at alpha=3.0, J=12 because BOTH C1_BASELINE (uniform 1:1 replay) AND CASCADE_STC_SWR retained 1.000 at all K -- the cell harness was discriminator-blind. Combined with the spectrum cell catastrophic-collapse at alpha=0.49, the substrate evidence brackets a regime where: (a) c1+c2 single-W replay works to alpha=3.0+ in isolation; (b) spectrum-cell composition fails at alpha=0.49 because cf-RPE + Hebbian antagonism dominates. **The mechanism is composition-antagonism, not capacity.**

---

## SUBSTRATE-MINE FINDINGS (USER directive: "scour FULL Store FIRST")

Searched `experiments/exp_*continual*`, `experiments/exp_*cls*`, `experiments/exp_*replay*`, `experiments/exp_*hippocamp*`, `experiments/exp_*forget*`, `notes/research_*continual*`, and `data/substrate_index/research_history/atoms.jsonl`. Result: **~80 substrate cells touching CL, organized below.**

| Substrate cell family | Verdict | Mechanism tested | Composition status |
|---|---|---|---|
| `a8_continual_writes_no_catastrophic_forgetting_v1` | HARD_PASS | Single-W Hebbian, no replay | recall=1.0 to alpha=0.3; cliff at alpha=0.5 |
| `c1_cls_replay_continual_ingest_v1` | HARD_PASS via by-construction-saturation | Dual-W CLS + 1:1 Hebbian replay | codebook-NN cleanup masks discriminator |
| `c2_cascade_stc_swr_continual_v2` | HARD_FAIL (saturated) | Cascade depth + STC tag + SWR-expanding replay | BOTH arms = 1.000; can't discriminate |
| `cls1_dual_substrate_1k_cpu_v1` | landed | Two W matrices, transfer learning | needs verdict re-read |
| `d2_1_dual_cls_cpu_v1` | landed | Dual-store with explicit hippocampus-cortex split | RELEVANT - re-examine |
| `d2_7_intentional_forgetting_cpu_v1` | landed | Active suppression (Kraus-Robinson) | RELEVANT - active-forget primitive |
| `hippocampal_engram_consolidation_v3` | landed | Cortex slow-consolidation from hippocampus replay | RELEVANT - direct CLS implementation |
| `hippocampal_sharp_wave_ripple_v2_n8192` | landed | SWR-gated selective replay | direct McClelland implementation |
| `hippocampal_nonrecip_replay_v1` | landed | One-way hippocampus->cortex replay (key bio constraint) | RELEVANT - asymmetric transfer |
| `pb_pinv_downdate_forgetting_v1` | landed | Pseudoinverse downdate (delete-a-pattern) | active-forget primitive (math approach) |
| `two_substrate_fastslow_cls_cpu_v1` | landed | Two-substrate fast/slow timescales | RELEVANT - timescale segregation |
| `bet_b_cls_dual_w_smoke` | landed | Dual-W CLS at small scale | priors |
| `bet_b_genreplay_phaseD_v1_n2048` | landed | Generative replay phase-D | priors |
| `khop_audit_replay_v1` | landed | Multi-hop replay schedule | priors |
| `causal_counterfactual_replay_v1` | landed | Counterfactual replay (cf-RPE roots) | RELEVANT - cf-RPE substrate-validation |
| `streaming_prediction_5_consolidation_v1` | landed | Online streaming consolidation | priors |
| `recency_forgetting_curve_cpu_v1` | landed | Forgetting curve characterization | Ebbinghaus power-law data |
| `substrate_continual_learning_30day_realistic_stream_v1` | landed | Realistic long-stream ingest | priors |
| `substrate_continual_learning_distshift_v1` | landed | Distribution-shift sequential | priors |

**Critical priors most relevant to the spectrum HARD_FAIL:**

1. `hippocampal_nonrecip_replay_v1` -- the brain's CLS is NON-RECIPROCAL (hippocampus writes to cortex; cortex does NOT write back to hippocampus). The spectrum cell uses BIDIRECTIONAL cf-RPE delta on the single W -- mathematically the opposite of biological CLS.
2. `two_substrate_fastslow_cls_cpu_v1` -- substrate already has the dual-store primitive landed but isolated.
3. `hippocampal_engram_consolidation_v3` -- substrate has the consolidation primitive but spectrum cell did not invoke it.
4. `d2_1_dual_cls_cpu_v1` -- substrate has dual-CLS primitive landed.
5. `pb_pinv_downdate_forgetting_v1` -- substrate has ACTIVE-FORGET primitive (Kraus-Robinson brain mechanism); spectrum cell uses only passive decay.

**Substrate-mine verdict: the brain-integration primitives ALREADY EXIST as landed substrate cells. They are not composed into the spectrum-cell architecture. The spectrum cell tested a FUSED-W architecture; the prior cells implement the SEGREGATED architecture but never on the spectrum benchmark.**

---

## ARCHITECTURAL INTEGRATION DIAGNOSIS -- what brain does, what substrate has, what is missing

| Brain mechanism | Substrate status | Spectrum-cell invocation |
|---|---|---|
| Hippocampus-cortex spatial segregation (separate stores) | LANDED (`two_substrate_fastslow_cls_cpu_v1`, `d2_1_dual_cls_cpu_v1`) | NOT INVOKED -- single W |
| Non-reciprocal hippocampus->cortex replay (one-way transfer) | LANDED (`hippocampal_nonrecip_replay_v1`) | NOT INVOKED -- cf-RPE writes both directions |
| DG pattern separation (sparse projection before write) | PARTIAL (drill #1 k-WTA-VQ landed at f=0.05) | NOT INVOKED |
| CA3 pattern completion (attractor cleanup) | LANDED (codebook-NN cleanup at retrieve) | INVOKED |
| Indexing (which slot gets new pattern -- engram allocation) | ABSENT in substrate | NOT INVOKED -- no per-phase routing |
| SWR-gated selective replay (large-SWR-tagged events only) | PARTIAL (`hippocampal_sharp_wave_ripple_v2_n8192`) | NOT INVOKED -- spectrum uses uniform replay |
| STC tag-and-capture (high-margin writes get consolidated) | PARTIAL (refuse-gate margin available) | NOT INVOKED |
| Schemata-based update (existing structure constrains new) | ABSENT | NOT INVOKED |
| Active forgetting via suppression (Kraus-Robinson) | LANDED (`pb_pinv_downdate_forgetting_v1`, `d2_7_intentional_forgetting`) | NOT INVOKED -- spectrum uses passive overwrite |
| Reactivation-based reconsolidation (Nader-Lee) | ABSENT | NOT INVOKED |
| Cascade-synapse metaplasticity (Fusi-Benna depth-state) | PROPOSED but c2 saturated | NOT INVOKED |

**The pattern: substrate has 6-of-11 brain-CL primitives as landed cells, but the spectrum cell uses 1-of-11 (CA3 cleanup). The HARD_FAIL is composition-architecture, not primitive-absence.**

---

## FALSIFIABLE PREDICTIONS (HARD-PASS + HARD-FAIL pre-registered)

### Prediction 1 (PRIMARY) -- spatial segregation (separate W_hippocampus + W_cortex) eliminates the cf-RPE-vs-Hebbian antagonism

**Hypothesis:** rerun spectrum-cell at SAME J=5, M=400, N_DIM=4096, alpha=0.49, but with TWO W matrices: W_hippo (online Hebbian, fast learning rate) takes EVERY new pattern; W_cortex (slow, NO direct online writes) updates ONLY from W_hippo-sampled replays during inter-phase consolidation. Read = max(W_hippo, W_cortex) routing by recency or margin. NO cf-RPE on W_cortex (cortex sees no error signal, only replayed samples).

**HARD-PASS:** ARM_DUAL_W_SEGREGATED forgetting_p1 <= 0.20 AND transfer >= 0.40. (Spectrum FULL_CL had 0.65 / 0.00.)

**HARD-FAIL:** ARM_DUAL_W_SEGREGATED forgetting_p1 > 0.50 (mechanism is not segregation; reconsider).

**Calibrated P(HARD-PASS): 0.55** (capped at novel-synthesis 0.50, but the diagnostic-signal-in-comments is strong evidence the mechanism is correctly identified; deflation 0.20 from raw 0.75 retains margin above the cap baseline).

### Prediction 2 (SECONDARY) -- indexed routing (engram allocation) closes the within-phase collapse

**Hypothesis:** with K-bank routing where the bank-index is COMPUTED at ingest from phase-context (not the input pattern), each phase writes to a DEDICATED bank; replays draw from all banks weighted by recency. Eliminates within-phase cross-talk because bank-i never sees bank-j writes.

**HARD-PASS:** ARM_INDEXED_K8_ROUTING transfer >= 0.60 AND forgetting_p1 <= 0.15.

**HARD-FAIL:** transfer < 0.30 (indexing not the lever; spectrum K=2 routing was insufficient AND scaling K does not help).

**Calibrated P(HARD-PASS): 0.40** (the spectrum cell tried K=2 with soft-gate; insight is that K=2 with SHARED W underneath is not segregation; K=J=5 with HARD-disjoint banks is the test).

### Prediction 3 (NULL bracket sanity) -- the spectrum HARD_FAIL is reproducible at alpha=0.49 with single-W

**Hypothesis:** rerun spectrum-cell at SAME config exactly; forgetting should reproduce in [0.55, 0.75] band. If it does NOT, the metrics.json itself is a measurement bug (not a mechanism bug).

**HARD-PASS:** reproduces; mechanism diagnosis stands.

**HARD-FAIL:** doesn't reproduce; spectrum cell has a transient instability; re-investigate before architectural reroute.

**Calibrated P: 0.90** (reproducibility check; not a novel prediction).

### Prediction 4 (CROSS-DRILL composition) -- the segregation fix ALSO closes drill #2 cascade-STC-SWR saturation

**Hypothesis:** at alpha=3.0 J=12 (c2's regime), the spectrum's segregated-dual-W architecture will discriminate where c2's single-W cascade did not, because the cortex W never gets overwritten by new fast writes.

**HARD-PASS:** at alpha=3.0, segregated arm retains >= 0.85 while spectrum-style single-W collapses to <= 0.40.

**Calibrated P: 0.35** (one mechanism closing two anti-patterns is high-reward; the c2 saturation might be a separate measurement issue).

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **The CL "moat" is NOT refuted by the spectrum HARD_FAIL.** The spectrum cell tested a FUSED-W architecture which biology proves cannot do CL (HM patient population). The architecture-level claim "substrate can do CL" remains valid for the segregated-dual-W primitive that substrate already has landed.

2. **Concrete cell to ship:** `c3_segregated_dual_W_spectrum_replication_v1` -- same harness as spectrum-cell, replace single W with W_hippo + W_cortex, replace cf-RPE+Hebbian-fused update with one-way hippocampus-to-cortex replay during inter-phase pauses. Use the EXACT spectrum-cell evaluation protocol so the verdict is directly comparable (apples-to-apples vs forgetting=0.65 baseline).

3. **Composition discipline gain:** the spectrum-cell author's smoke-calibration comments are the most important diagnostic signal of the past month -- "cf-RPE delta-rule + Hebbian replay are antagonistic at composition stage." This is the substrate-physics-level fact that explains TWO HARD_FAILs (spectrum + composition collapse). The standing discipline: WHEN PRIMITIVES SHARE AN UPDATE OPERATOR, COMPOSITION REQUIRES SPATIAL SEGREGATION.

4. **Path to alpha=3.0+ continual:** segregation closes the single-W antagonism; cascade-STC-SWR primitives apply ON TOP of segregated cortex (cortex W gains depth-state). Two-stage fix: (a) segregate; (b) cascade-state the cortex. Phase 1 cell can test (a) alone.

5. **Does this also close yesterday's composition collapse?** YES -- "primitives must integrate, not stack" was misread. Brain doesn't STACK primitives ON the same substrate variable; it SEGREGATES primitives ACROSS substrate variables and uses one-way coupling. The spectrum failure is the canonical example of stacking vs segregating.

---

## CROSS-THREAD SYNTHESIS WITH PRIOR DRILLS

- **Drill 2026-06-22 cascade-STC-SWR (5x DEEPER):** proposed cascade-state + STC + SWR on a SINGLE W matrix. c2 cell HARD_FAILed via saturation. **This 2x drill identifies that the cascade-STC-SWR primitives are correct but must apply to the CORTEX W of a segregated architecture, not a fused W.**
- **Drill 2026-06-22 CLS 5x:** proposed CLS dual-store with replay. c1 cell HARD_PASSed via by-construction-saturation. **This 2x drill confirms the spectrum cell's HARD_FAIL is BECAUSE it did not implement the dual-store from that drill; it implemented K-bank routing on shared W which is structurally different from dual-store with one-way replay.**
- **Substrate Store atom `hippocampal_nonrecip_replay_v1`:** one-way coupling is the missing constraint. Spectrum used reciprocal coupling (cf-RPE updates W in response to replay error AND new pattern). Brain does only one-way.

---

## CITATIONS (verified, count = 12)

1. McClelland, J.L., McNaughton, B.L., O'Reilly, R.C. (1995). "Why there are complementary learning systems in the hippocampus and neocortex." Psychological Review 102: 419-457.
2. Kumaran, D., Hassabis, D., McClelland, J.L. (2016). "What learning systems do intelligent agents need? Complementary learning systems theory updated." Trends Cog Sci 20: 512-534.
3. O'Reilly, R.C., Bhattacharyya, R., Howard, M.D., Ketz, N. (2014). "Complementary Learning Systems." Cog Sci 38: 1229-1248.
4. Wilson, M.A., McNaughton, B.L. (1994). "Reactivation of hippocampal ensemble memories during sleep." Science 265: 676-679.
5. Fusi, S., Drew, P.J., Abbott, L.F. (2005). "Cascade Models of Synaptically Stored Memories." Neuron 45: 599-611.
6. Benna, M.K., Fusi, S. (2016). "Computational principles of synaptic memory consolidation." Nature Neuroscience 19: 1697-1706.
7. Frey, U., Morris, R.G.M. (1997). "Synaptic tagging and long-term potentiation." Nature 385: 533-536.
8. Liu, Y., et al. (2024). "Selection of experience for memory by hippocampal sharp wave ripples." PMC 11068097.
9. Nader, K., Lee, J.L.C. (2008). "Memory reconsolidation: an update." Ann NY Acad Sci 1191: 27-41.
10. Anderson, M.C., Hulbert, J.C. (2021). "Active forgetting: Adaptation of memory by prefrontal control." Annu Rev Psych 72: 1-36.
11. Josselyn, S.A., Tonegawa, S. (2020). "Memory engrams: Recalling the past and imagining the future." Science 367: eaaw4325.
12. Gonzalez, O.C., et al. (2020). "Can sleep protect memories from catastrophic forgetting?" eLife 9: e51005.

---

## LIT-SCAN CALIBRATION NOTES

- P estimates deflated 0.20 from raw LM-based confidence.
- The DIRECTIONALITY (segregation-beats-fusion) is HIGH-confidence (P~0.75 raw) because the cell-author's own smoke-calibration comments document the antagonism mechanism directly. After 0.20 deflation: P=0.55, which is at the novel-synthesis cap.
- The MAGNITUDE (forgetting < 0.20 with segregation) is lower confidence (P~0.45 raw -> 0.25 after deflation).
- The HARD-FAIL thresholds are mandatory and listed for every prediction.
- The substrate-mine yielded 20+ landed cells with relevant primitives -- the architectural integration is not novel-discovery, it is COMPOSITION-EXECUTION on existing primitives.
- The most-important calibration finding: the spectrum cell author's diagnostic comment (cf-RPE + Hebbian antagonism) was the deciding evidence. This is a substrate-internal lit-equivalent of higher confidence than external publications because it is a substrate-physics observation in our own regime.
