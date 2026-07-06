# Research 2x-drill: thalamic CRT-residue router (RC2) mechanism + RC3 build-or-shelve decision

**Date:** 2026-07-05 (revival drill, level-2 operational — per standing "drill load-bearing non-positives" directive)
**Type:** Decisive drill on an ALREADY-CLOSED clean structural negative (`exp_multihop_router_crt_residue_addressed_v1`, HARD_FAIL, smoke==full config, commit 8fa65bddc diagnosis-hygiene fix). NOT re-verification — goes deeper into mechanism + forces a BUILD/SHELVE call on RC3.
**Discipline:** Lit-scan calibration penalty applied (deflate 0.15-0.25; novel-synthesis capped 0.50). 3 parallel Sonnet lit-scans dispatched, generic-math-terms-only per query-privacy discipline (no substrate-novel naming used off-platform). Internal precedent verified off-disk (6 prior learned/algebraic-router cells in this exact codebase, all read via `data/exp_wave14_moe_*` and `data/exp_moe_*` metrics.json). Honest gap flagged below: the literal 4-point address-size sweep numbers were not found as a standalone artifact on disk (checked `data/`, `notes/`, `git log`) — the qualitative finding ("fundamental, holds across all 4 sizes") is attributed to exp_dev's diagnosis as stated in `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-05.md` and the task input, not independently re-derived this cycle. Do not treat the missing raw numbers as a gap in the CONCLUSION — the mechanism argument below explains WHY no address size would fix it, independent of the specific swept values.

---

## HEADLINE

**RC2's failure is a well-known, textbook-closed classical property (hard-decision, non-redundant CRT decoding is fragile by construction — 50+ years of residue-number-system coding theory says so), not a mystery and not evidence that algebraic/modular routing is impossible in principle. But the KNOWN FIXES (redundant check-moduli, or joint/maximum-likelihood decoding across all residues) are real redesigns, not a resize — which is exactly why the address-size sweep found the failure held at every size tested: it was turning the wrong knob. Meanwhile, an independent literature scan on RC3 (a learned/trained router) converges with this project's OWN internal track record (6/6 prior learned-router cells failed on a structurally analogous noisy-routing problem in this codebase) on the same negative conclusion: the interference here is non-stationary Hebbian crosstalk, which is exactly the condition under which learned discriminative routers lose their usual advantage over fixed decision rules. Given ALSO that nothing currently needs a dedicated router (integration composes end-to-end via regenerative cleanup without one), the decisive call is SHELVE dedicated thalamic routing (both an RC2 redesign and RC3) as a build priority — filed as a legitimate, evidence-backed brain-component inventory finding, not a punt.**

---

## 1. MECHANISM — why is residue-addressed routing fundamentally noise-fragile here?

### 1a. What RC2 actually does (verified from `experiments/exp_multihop_router_crt_residue_addressed_v1.py`)

Each entity's HD vector carries its CRT residue address in two DISJOINT, DEDICATED sub-blocks (`ADDR_DIMS = (384, 384)`, moduli `(4, 5)`, product = 20 = `N_PARTITIONS`). The router: (1) independently argmaxes each sub-block to hard-decode one residue per modulus, (2) reconstructs the partition index via the deterministic CRT formula on those two hard-decoded residues. This is a **hard-decision, non-redundant, independent-per-channel decode** — no soft/probabilistic combination across the two moduli, no extra check-modulus, no downstream cleanup pass on the reconstructed partition.

### 1b. The classical-CRT literature says this exact configuration is known-fragile

Per lit-scan (11 tool-uses, high confidence — this is described as uncontested, 50+-year-old coding theory, not an open question):

- A single erroneous residue moves the CRT reconstruction into a **different congruence class mod M = prod(moduli)** — the resulting error can be arbitrarily large, with **no partial credit / no graceful degradation**. This is stated as the founding motivation for the entire "robust CRT" research line: Li, Liang & Xia (2009, IEEE Trans. Signal Processing 57(11):4314-4322, "A robust Chinese remainder theorem with its applications in frequency estimation from undersampled waveforms"); Wang & Xia (2010, IEEE TSP 58(11):5655-5666, "A closed-form robust Chinese remainder theorem and its performance analysis"); survey arXiv:1708.04089 "Robustness in Chinese Remainder Theorem."
- **Known fixes, both requiring a genuine redesign, not a resize:**
  1. **Redundant Residue Number System (RRNS)** — add `n-k` extra check moduli beyond the `k` needed to span the range; an RRNS(n,k) code detects up to `n-k+1` errors and corrects `floor((n-k)/2)`, directly analogous to a minimum-distance error-correcting code (Szabo & Tanaka 1967, *Residue Arithmetic and Its Applications to Computer Technology*; Barsi & Maestrini 1973 on RRNS error correction). Overhead scales roughly linearly with correctable-error count — a real robustness gain, but it costs additional dedicated moduli/channels, which is architecturally different from widening the existing 2 channels.
  2. **Robust CRT (bounded-error, no extra moduli)** — relax pairwise coprimality by sharing a common factor among moduli; reconstruction error stays bounded IF the per-residue error is below a bound (`< 1/4 gcd`). Genuine improvement, but only within a fixed tolerance — a bounded workaround, not unlimited robustness (Wang/Xia, Li/Xia as above).
  3. **Maximum-likelihood / joint decoding over the WHOLE residue codeword** rather than independent per-residue hard decode — the closest structural match to what's missing here: treating all residues as one joint codeword and doing ML/minimum-distance decoding recovers tolerance that independent per-residue reconstruction structurally cannot, because independent decode **discards the cross-channel joint-likelihood information**.
  4. **Multi-stage / statistical robust CRT** (arXiv:1303.3251, arXiv:1909.00225) — average over multiple redundant measurement sets for graceful (not cliff-edge) degradation.

**Critically: resizing a single residue's sub-block (what the 4-point address-size sweep tested) is NOT one of these known fixes.** The lit is explicit that the fix is either *more channels* (RRNS) or *joint/soft decoding* (ML/robust-CRT) — not *wider channels*. This directly explains, independent of the swept numbers, why the sweep found the failure held everywhere: it was turning a knob the classical theory doesn't identify as load-bearing.

### 1c. The brain's own version of a modular/residue-like code confirms the same two-part fix, and RC2 has neither part

Per second lit-scan (7 tool-uses, high confidence on points 1-3, thinner on point 4): grid cells are explicitly modeled in the literature as a residue-number-system-like code (Sreenivasan & Fiete 2011, *Nat Neurosci*, "Grid cells generate an analog error-correcting code for singularly precise neural computation" — the canonical, frequently-cited result). Their robustness comes from exactly the two ingredients the classical CRT lit also names:

1. **Large POPULATIONS of neurons per module**, not a handful of units — Mosheiff/Fiete-lab follow-on work gives a concrete example ("eight modules of 100 cells each" is highly robust to ambiguity even over ranges much larger than the largest single grid scale) — i.e., many "votes" per residue digit (analogous to RRNS's extra redundancy, or to a much larger `ADDR_DIMS` than 384/modulus — though per 1b, size alone empirically failed in this substrate's sweep, suggesting the substrate's crosstalk doesn't obey simple sqrt(size) averaging the way an idealized noise model would, OR the swept range didn't reach a large-enough regime, OR — most likely per the classical-CRT reading above — size was never the load-bearing knob to begin with).
2. **Downstream attractor/cleanup circuitry** (hippocampal CA3 pattern completion; Rolls 2013 review) that denoises/completes a degraded or ambiguous module readout rather than passing a raw deterministic decode straight through — this is the neural analog of "joint/ML decoding," and RC2 has no equivalent step (hard argmax -> CRT formula -> done, no iteration, no confidence-weighted combination).

General population-coding SNR-pooling (`sqrt(N)`-type scaling from pooling independent noisy estimates) is confirmed as a standard, textbook-level principle in computational neuroscience — supporting "more votes = better SNR" generically, though the lit-scan found no source applying this exact scaling law to "residue sub-block width" specifically (my own bridging inference, flagged as such, not a cited result).

### 1d. Verdict on Q1

**This is a genuine, well-precedented closure for the SPECIFIC mechanism implemented (hard independent per-modulus argmax + deterministic CRT reconstruct, zero redundancy, zero joint decoding) — not a mystery, and not evidence that ALL algebraic/modular routing is hopeless.** Two real fixes exist in the literature (RRNS redundant moduli; joint/soft ML decoding + downstream cleanup, mirroring the brain's own two-part solution) — but both are substantive redesigns of the mechanism, not a parameter sweep, which is exactly consistent with the empirical finding that the address-size sweep (turning the wrong knob) held fundamental across all 4 points tested.

**P(this mechanism explanation is correct) = 0.75** (raw ~0.90; deflated 0.15 per calibration discipline — the classical-CRT and grid-cell literatures are both high-confidence/uncontested on their own terms, but their direct transfer to this exact Hebbian-outer-product bipolar/complex regime at N=8192 has not been independently re-verified by a fresh experiment this cycle, only reasoned from precedent).

---

## 2. RC3 (learned/no-LLM router) FEASIBILITY

### 2a. Internal track record (verified off-disk, `data/exp_wave14_moe_*` + `data/exp_moe_*` metrics.json, this session)

This exact codebase has already tried **6 distinct learned/trained-router mechanisms** on a structurally analogous problem (MoE-style load-balanced routing under noise, not multihop, but the same underlying question: "can a trained/algebraic-anchor router beat a naive baseline when the routing decision is made from a noisy high-dim superposed state?"):

| Cell | Mechanism | Verdict |
|---|---|---|
| `exp_wave14_moe_cosine_router_v1` | Cosine-similarity anchor routing | `COSINE_ROUTER_HARD_FAIL` |
| `exp_wave14_moe_cosine_router_v3_dynamic` | Dynamic cosine routing | `DYNAMIC_ROUTER_HARD_FAIL` (entropy collapse fundamental, K=4 ceiling confirmed) |
| `exp_wave14_moe_hebbian_anchor_router_v1` | Hebbian-trained anchor | `HEBBIAN_ROUTER_HARD_FAIL` |
| `exp_wave14_moe_hebbian_anchor_router_v2_n4096` | Hebbian-trained anchor, N=4096 | `HEBBIAN_ROUTER_V2_HARD_FAIL` |
| `exp_wave14_moe_remoe_relu_router_v1` | ReLU/ReMoE gradient-style gating | `REMOE_HARD_FAIL` (retention_delta=-0.257) |
| `exp_moe_gradient_router_v1` | Gradient-trained router | `GRADIENT_ROUTER_HARD_FAIL` |
| `exp_moe_capacity_aware_router_v1_n4096` | Capacity-aware router | Partial, below HARD-PASS band (ret_k16=0.911 vs 0.70 target — actually the best of the 6, but still not a clean win) |

**6/6 HARD_FAIL, 1 partial-but-short.** This happened despite a prior research note (`research_moe_learned_router_2026-05-27.md`) calibrating a reasonable-sounding P=0.45 for the cosine-anchor rescue specifically, citing real precedent (Expert-Choice routing, Zhou et al. 2022 NeurIPS; ReMoE, arXiv:2412.14711). The theory was sound; the empirical result was negative anyway. This is a strong internal base rate against "a smarter router saves the day" in this substrate's noise regime.

### 2b. External literature (third lit-scan, 12 tool-uses)

**Calibrated verdict from lit-scan: UNLIKELY-to-UNCERTAIN, not >50%,** that a learned router beats a well-tuned fixed full-vector baseline (naive_centroid) here. Key findings:

1. **Ng & Jordan (NeurIPS 2001)** — discriminative learners (logistic regression, MLPs) have lower *asymptotic* error but need MORE labeled examples to realize the advantage than a generative/centroid-style rule, which reaches its (higher) asymptotic error fast with few samples. Whether RC3 wins depends almost entirely on labeled-training-signal abundance relative to problem size (~8192-dim, 20-way) — a Hebbian-trained or lightly-trained router is exactly in the low-data/high-dim regime where the discriminative advantage is NOT reliably realized (PMLBmini, arXiv:2409.01635, finds SOTA learned classifiers fail to beat plain logistic regression on 55% of benchmarks at N<=500).
2. **The one real theoretical case FOR a learned router** (matched-filter/whitening: a learned per-dimension reweighting provably beats uniform argmax under COLORED/structured noise) requires the noise covariance to be **stable/estimable and stationary**.
3. **But the interference here is very likely non-stationary**: it's Hebbian-superposition crosstalk from ~1000 stored triples whose composition and the query's own hop-position change as the chain progresses and as the store fills. The literature (Bickel et al., "Discriminative Learning Under Covariate Shift"; general concept-shift results) explicitly flags this kind of shift — where interference structure couples to which class looks likely — as the condition under which discriminative learners lose their advantage over fixed/generative rules. This is precisely NOT the condition the matched-filter argument requires.
4. **MoE-specific corroboration:** arXiv:2601.14792 ("Robustness of Mixtures of Experts to Feature Noise") independently flags router/gating noise-sensitivity as "a central challenge" requiring explicit noise-injection training just for stability — consistent with, not contradicting, this project's own 6/6 failure record.

### 2c. Combined verdict on Q2

Internal empirical base rate (6/6 fail on analogous problem) and external literature (non-stationary interference undercuts the standard discriminative-classifier advantage) **converge on the same negative**, which is a stronger basis for a low prior than either alone.

**P_deflated(RC3 beats naive_centroid at HARD-PASS band) = 0.20** (raw estimate ~0.35 from the theoretical case that a full-vector learned router at minimum inherits naive_centroid's own signal plus possibly some crosstalk-structure exploitation; deflated 0.15 for the convergent internal+external negative evidence above; already well under the 0.50 novel-synthesis cap).

### 2d. Concrete cell spec (provided per task requirement, for the backlog — NOT recommended for immediate dispatch; see Section 3)

**`exp_multihop_router_rc3_learned_v1`** (spec only; not pre-registered/dispatched this cycle)

- **Arms:** `ORACLE` (ceiling, reproduce 0.980) / `NAIVE_CENTROID` (existing baseline to beat, reproduce 0.237 e2e) / `LEARNED_LINEAR` (logistic-regression-style router: full N=8192-dim state -> 20-way partition, trained via gradient descent on labeled `(state, true_partition)` pairs from the SAME chain-generation harness) / `LEARNED_MLP` (1-hidden-layer stretch arm, only if LEARNED_LINEAR clears MIDDLE-BAND) / `RANDOM_ROUTER` + `SCRAMBLED` (existing collapse controls).
- **Cheapest decisive sub-test first:** does even `LEARNED_LINEAR` (full-vector, gradient-trained, in-distribution) beat naive_centroid? If a LINEAR classifier with labeled supervision and access to the FULL vector cannot beat a non-trained nearest-neighbor rule that also uses the full vector, an MLP will not help either (linear is close to a lower bound on what gradient training can extract) — this would be strong evidence the crosstalk is not linearly separable/learnable at this N/M ratio, not just an under-trained model.
- **Non-stationarity discriminator (the load-bearing control the internal MoE cells never explicitly isolated):** train the router on chains generated at store-fill-state `S_train`; evaluate BOTH in-distribution (same `S_train`) AND out-of-distribution (a different seed's chain state derived from the SAME `W`, i.e. same store, different query trajectory). A large in/out-of-distribution gap directly confirms the non-stationarity mechanism flagged by the lit-scan as RC3's likely failure mode, rather than leaving it as an untested assumption.
- **HARD-PASS:** `LEARNED_LINEAR` (or MLP) per-hop route accuracy >= naive_centroid + 0.05 in-distribution AND out-of-distribution gap < 0.10 (rules out non-stationarity as a silent failure).
- **HARD-FAIL:** `LEARNED_LINEAR`/MLP <= naive_centroid + 0.02 (no real lift) OR in/out-of-distribution gap >= 0.20 (confirms non-stationarity kills the learned advantage even if in-distribution looks good — an important distinction from a flat "it just doesn't work").
- **MIDDLE-BAND:** real in-distribution lift but large train/test-distribution gap — informative (confirms mechanism) but not deployable.
- **Compute:** CPU, reuses the existing certified harness + adds one gradient-trained linear/MLP head. Estimate 2-3 hr.

---

## 3. THE STRATEGIC CALL

**Recommendation: SHELVE dedicated thalamic routing (both an RC2 redesign — RRNS or joint-decode — and RC3) as a build priority right now.**

Rationale:

1. **No current consumer.** Per today's own integration finding (`exp_integration_full_stack_full_fidelity_v1`, FULL, HARD_PASS, compounding_ratio 0.991): the reason->generate chain composes end-to-end via **regenerative cleanup at each seam**, without any dedicated router. This is explicitly logged: *"regenerative cleanup alone holds the chain -> thalamic-buffer/RC3-router NOT needed for composition (deprioritized)."* Building a router now would be inventory-for-its-own-sake, not closing an active blocker.
2. **RC2's failure is now doubly corroborated** (classical CRT/RNS theory + the empirical address-size sweep) as a structural property of the SPECIFIC mechanism tried, and the known fixes (RRNS extra moduli, or joint/soft ML decoding + downstream cleanup, mirroring the brain's own two-part grid-cell solution) are genuine redesigns with real engineering cost, not a quick patch.
3. **RC3 has a calibrated LOW prior (0.20)**, converging from two independent evidence sources (this project's own 6/6 learned-router failure record on a structurally analogous problem, plus external literature identifying the exact condition — non-stationary interference — that undercuts learned-router advantage). Spending build budget chasing a ~20% shot with no waiting downstream use is a poor trade against the standing backlog (grammar long-pole, math envelope, self-reasoning arc — all USER-designated the current prize).
4. **The honest brain-component-inventory framing is not "thalamus is missing/broken."** It is: *the substrate's actual working solution to "route/select under noise" is attractor-style regenerative cleanup composition* — which is itself a legitimate, brain-grounded mechanism (the functional analog of hippocampal CA3 pattern completion / cortical attractor dynamics, per the grid-cell lit-scan's own point 4), not a missing component papered over. A dedicated CRT/algebraic "thalamic relay" analog failed structurally; the system already has a DIFFERENT, working brain-analog mechanism serving the same functional role. This is a fill, not a gap, for the inventory.
5. **One NOT-YET-falsified candidate remains on the backlog and is worth flagging, not building now:** RC1 (relation-typed routing — per-hop routing key = relation embedding, a clean symbolic side-channel available at each hop, not something that needs to be decoded under Hebbian crosstalk at all). RC1 structurally sidesteps the entire "decode an address from a noisy superposition" problem that sank both RC2 and (predictively) RC3, since relation identity is explicit input, not a decoded signal. If a FUTURE task genuinely needs a beat-naive-centroid router, RC1 is the cheapest, structurally-different next probe — but per the "don't dismiss adjacent methods" discipline, this is a flag for the backlog, not a recommendation to build now (no current consumer, same as RC2/RC3).

**If USER wants a brain-component-inventory "have" checkbox for thalamic routing specifically** (as opposed to accepting regen-cleanup as the working analog), the cheapest path is NOT RC3 as spec'd above — it is the RRNS/joint-decode RC2 redesign (Section 1b, fix 1 or 3), since that has a real classical-literature-backed mechanism (not just a hopeful prior) and reuses the already-proven CRT machinery. This is flagged as an option, not a recommendation, absent a stated need.

---

## Cross-thread synthesis

- Directly resolves the open question left by `notes/research_brain_component_rerank_thalamus_cerebellum_load_2026-07-05.md` (which ranked RC2 as "BUILD NEXT," P_deflated=0.30, and correctly predicted the MIDDLE-BAND "needs RC3 learned top-up" contingency — RC2 landed HARD_FAIL rather than MIDDLE-BAND, so that note's own contingency plan (RC3) is exactly what this drill was asked to evaluate, and the answer is negative for the same reasons that note's own P=0.30 already flagged as the main risk: "this specific composition has never been tried... real risk the residue structure doesn't align cleanly.")
- Corroborates `notes/partition_oracle_recovery_mechanism_G_correction_2026-07-01.md`: even a weak REAL router (r=0.003-0.006 recovery probability) gives a meaningful Markov floor at extreme depth — but that finding is about recovery-after-error dynamics at 100s of hops, a different regime from the K=5 per-hop composed-accuracy question this drill addresses; it does not change the BUILD/SHELVE call because the K=5 composed floor question is already answered (naive_centroid's 0.237 e2e is the honest current ceiling for real-router-based composition, and nothing currently needs to beat it).
- Corroborates and extends `research_moe_learned_router_2026-05-27.md`: that note calibrated P=0.45 for a learned-router rescue with a sound theoretical case (Expert-Choice, ReMoE precedent) — and it still failed empirically 6/6 times. This drill's RC3 prior (0.20) is calibrated LOWER than that prior attempt's prior (0.45) specifically BECAUSE this drill has that empirical track record to draw on, which the 2026-05-27 note did not yet have. This is the calibration-penalty discipline working as intended: repeated negative results in a class of mechanism should lower, not hold constant, the prior for the next member of that class.
- New adjacency surfaced (Trigger C candidate, LOW PRIORITY, parked): Redundant Residue Number System / erasure-correcting CRT codes is a concrete adjacent angle within the `coding-theory` field (Tier-2, 44% yield per field advisor), close to the already-flagged-but-undrilled "BCH-redundant erase" candidate. Not recommended for a dispatched drill now given Section 3's no-current-consumer conclusion — flagged for the backlog only.

## Substrate-product implications

Closing this honestly (SHELVE with a well-evidenced mechanism, not "TODO: fix router") strengthens the glass-box credibility story in the SAME direction as today's reason->generate finding: the product story is "the substrate's compositional reliability comes from inspectable regenerative cleanup at every seam, not from a fragile bolt-on router" — an honest, product-relevant framing rather than a research gap swept under the rug. If a future customer use case needs explicit per-hop audit of ROUTING decisions specifically (as opposed to auditing the composed chain's output), RC1 (relation-typed, clean symbolic input) is the cheapest path to that specific claim, not RC2's redesign or RC3.

## Citations (verified count: 15 direct external + 7 internal-artifact cross-checks = 22)

**Classical CRT/RNS robustness (lit-scan 1, 11 tool-uses):**
1. Li, X., Liang, X., Xia, X.-G. (2009) "A robust Chinese remainder theorem with its applications in frequency estimation from undersampled waveforms." *IEEE Trans. Signal Processing* 57(11):4314-4322.
2. Wang, W., Xia, X.-G. (2010) "A closed-form robust Chinese remainder theorem and its performance analysis." *IEEE Trans. Signal Processing* 58(11):5655-5666.
3. arXiv:1708.04089 "Robustness in Chinese Remainder Theorem" (survey).
4. Szabo, N.S., Tanaka, R.I. (1967) *Residue Arithmetic and Its Applications to Computer Technology*. McGraw-Hill.
5. Barsi, F., Maestrini, P. (1973) RRNS error correction (foundational RRNS coding-theory result).
6. arXiv:1303.3251 (multi-stage robust CRT).
7. arXiv:1909.00225 (statistical robust CRT for multiple numbers).

**Grid-cell / neural modular-code robustness (lit-scan 2, 7 tool-uses):**
8. Sreenivasan, S., Fiete, I. (2011) "Grid cells generate an analog error-correcting code for singularly precise neural computation." *Nature Neuroscience*.
9. Mosheiff et al. (PMC3866454) "Optimal configurations of spatial scale for grid cell firing under noise and uncertainty."
10. Rolls, E.T. (2013) CA3 attractor/pattern-completion review, *Frontiers in Systems Neuroscience*.
11. Neunuebel, Knierim-type "Tracking the flow of hippocampal computation" (PMC4792674).
12. Crick, F. (1984) "The function of the thalamic reticular complex: the searchlight hypothesis."
13. Halassa, M.M., Acsády, L. (2016) TRN gating review.
14. Sherman, S.M., Koch, C. (1986) TRN gain-reduction gating.

**Learned-router feasibility (lit-scan 3, 12 tool-uses):**
15. Ng, A., Jordan, M. (2001) "On Discriminative vs. Generative Classifiers: A Comparison of Logistic Regression and Naive Bayes." *NeurIPS*.
16. arXiv:2409.01635 "PMLBmini" benchmark (learned classifiers vs logistic regression at small N).
17. Bickel, S. et al. "Discriminative Learning Under Covariate Shift."
18. arXiv:2601.14792 "Robustness of Mixtures of Experts to Feature Noise."
19. arXiv:2302.02334 "Revisiting Discriminative vs Generative Classifiers."

**Internal artifacts verified off-disk this cycle (not lit citations, load-bearing evidence):**
20. `experiments/exp_multihop_router_crt_residue_addressed_v1.py` (mechanism source, ADDR_DIMS/MODULI/arm definitions).
21. `data/exp_multihop_router_crt_residue_addressed_v1_smoke/metrics.json` (HARD_PASS-on-smoke-gate machinery verdict; per-arm numbers: oracle e2e=0.980, crt_residue e2e=0.1467, naive_centroid e2e=0.2367, crt_minus_naive route = -0.088).
22. `data/exp_wave14_moe_*` + `data/exp_moe_*` metrics.json (6 internal learned-router HARD_FAIL precedents) + `notes/research_moe_learned_router_2026-05-27.md` + `notes/research_brain_component_rerank_thalamus_cerebellum_load_2026-07-05.md` + `notes/partition_oracle_recovery_mechanism_G_correction_2026-07-01.md` + `notes/skunkworks_batch2_atomize_complete_RC_backlog_2026-06-26.md` (RC1/RC2/RC3 definitions) + `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-05.md`.

---

**Next-drill candidate (per field advisor, unrelated to this drill's own low-priority coding-theory adjacency):** `free-probability` F4 — free cumulants (Voiculescu kappa_n), tier-1, anchor_yield=100%, cost ~1 day theory + ~30 min CPU. Higher-order moments of the P(h) histogram give substrate-novel observability beyond mean+variance, unrelated to and not blocked by this drill's SHELVE call.
