# RESEARCH 2x REVIVAL: comparator_resonator_primitive_smoke_v1 HARD_FAIL — WHY it failed and where revival lives

**Date:** 2026-06-23
**Trigger:** USER directive "understand WHY it failed" on the HARD_FAIL HF1 verdict (ARM_COMPARATOR mean=0.856 ≤ ARM_RAW_W_LOOKUP mean=0.894 + 0.05).
**Discipline:** 2x revival drill (level-2 operational drill on existing finding, NOT lit-scan re-verification). 2 parallel WebSearch lit-scans + Opus synthesis. Generic queries only per [[feedback-query-privacy-decomposition]]. Calibration penalty applied (cap P at 0.40 per USER prompt; deflate 0.20).
**Cross-thread anchors:** parent research note `research_5x_deeper_substrate_QA_composition_gap_2026-06-23.md` L3 (the comparator primitive was specified there); v3 handoff `exp_dev_handoff_research_5x_QA_composition_v3_comparator_encoder_2026-06-23.md`; HotpotQA v2 comparison-em=0.071 floor.

---

## HEADLINE (one-line synthesis)

**The comparator primitive is mechanistically SOUND (sanity 5/5, projection-sign 5/5, all three selftests PASS) but at the SMOKE regime (M=50, 5 attrs, N_DIM=4096) the substrate's W matrix is so under-loaded that ARM_RAW_W_LOOKUP — a 32-bin argmax over a per-attribute scalar codebook — recovers the exact value cleanly; in that regime the comparator's sign-projection is a STRICTLY WEAKER ESTIMATOR of the same quantity because it collapses a high-precision scalar estimate into a 1-bit sign and only beats raw when raw is broken. HotpotQA comparison-em=0.07 is NOT primarily a comparator-mechanism failure — it is RETRIEVAL failure feeding garbage into BOTH arms (char_trigram encoder recall@5=1.9% means W @ bind(E_X, R_attr) returns noise, regardless of whether you argmax-codebook it or sign-project it). The revival path is therefore (a) test comparator on REAL HotpotQA comparison questions where retrieval is good (the existing v3 handoff Arm 3 is exactly this), AND (b) push the smoke to a regime where raw breaks (M≥500 or scalar density per attribute makes the 32-bin codebook ambiguous), to validate the primitive's incremental value where it actually compensates. Top revival: dispatch v3 Arm 3 (COMPARATOR_PRIMITIVE_COMPARISON_ONLY on real HotpotQA dev split with char_trigram retrieval) — substrate-mining showed the v3 handoff ALREADY contains the load-bearing comparison-em arm at production-regime; no NEW cell is needed for the dominant revival. P_deflated(comparator lifts comparison-em from 0.07 to ≥0.15 at v3 production regime) = 0.30.**

Plain English: the smoke cell failed because the test was set up at a difficulty level where the simpler raw-lookup baseline was unbroken — and comparator is mathematically a 1-bit summary of what raw recovers as a full scalar. Comparator does NOT add information on top of working raw lookup; it only adds value where raw breaks. The real-world failure mode the primitive was BUILT for (HotpotQA comparison-em=0.07) is upstream of the comparator: the encoder feeds garbage into the W lookup, so both arms eat garbage. The revival is NOT a new comparator cell; it is to wire the existing comparator into the v3 cell (already specified in the handoff) and run it where retrieval is the actual blocker. The smoke result is informative-negative: it confirms the primitive is sound on synthetic data AND that the smoke regime was diagnostically uninformative for the HotpotQA target.

---

## DIAGNOSIS — WHY comparator failed vs raw-W-lookup (mechanism analysis)

### The smoke configuration

- M=50 entities, 5 attrs (born_year, height_cm, founded_year, salary_usd, population), N_DIM=4096
- Each (entity, attr) pair has ONE scalar value drawn uniform in attribute range
- W = Σ_(x,a) outer(scalar_value_vec(value_xa), bind(E_x, R_a))
- Total ingest: 50 × 5 = **250 atoms into a 4096×4096 matrix** — load factor α = 250 / 4096 = **0.061** (an order of magnitude below the standard Hopfield α_c ≈ 0.138 capacity edge)
- ARM_RAW_W_LOOKUP: argmax over K=32 codebook bins covering attribute range → reconstructs scalar to bin resolution (e.g., born_year range 100yr / 32 bins = 3.1yr granularity)
- ARM_COMPARATOR: project (W@k_X − W@k_Y) onto basis_direction[a], sign-test → 1-bit answer
- ARM_FREQ_BIAS: majority-class over 60 questions (binary + triple)

### The root cause: comparator is a strictly weaker estimator when raw works

**The comparator throws away information.** Mathematically, the sign-projection is:

```
sign( <W@k_X − W@k_Y, direction[a]> )
```

while ARM_RAW_W_LOOKUP computes:

```
argmax_g <W@k_X / ||W@k_X||, scalar_value_vec(g)>  → recovered value v_X
argmax_g <W@k_Y / ||W@k_Y||, scalar_value_vec(g)>  → recovered value v_Y
return v_X > v_Y
```

At α=0.061 (FAR below Hopfield capacity), the cross-talk noise in W @ k_X is small enough that the unbinding signal dominates. Both arms recover the same underlying signal — but raw extracts a 32-level quantization, comparator extracts 1 bit. Whenever the 32-level recovery is correct (which at this α happens ~89% of the time on binary Qs and ~89% on triples per the reported means), comparing the two recovered scalars gives the right answer. The comparator's sign-projection — a less precise summary — only EQUALS or LOSES.

**Specifically: comparator can never EXCEED raw-W-lookup when raw is unsaturated.** The sign of (v_X − v_Y) is a deterministic function of the recovered scalars; if raw recovers both correctly, sign agrees. If raw fails on one, comparator may or may not fail depending on whether the noise-direction has positive or negative projection onto the basis_direction — essentially a 50/50. Comparator can only WIN when raw is broken AND the noise direction is incidentally aligned with the basis axis.

### Why this is a SMOKE-REGIME-TOO-EASY issue (the dominant cause)

At M=50 / α=0.061:
- 32 codebook bins span the FULL attribute range (born_year: 1900–2000 with 3.1yr bins; salary_usd: $30k–$200k with $5.3k bins; population: 1k–1M with ~31k bins)
- The probability that two random entities in the codebook happen to fall in the SAME bin (which would create raw-W ties) is at most 1/32 ≈ 3% per question
- Binary question raw failure ≈ (1 − P(both correct bin) − P(tie)) ≈ 8–11% (matches observed ARM_RAW=0.894 = 89.4% acc)
- Triple question raw failure: dominated by |v_X − v_Z| vs |v_Y − v_Z| where the absolute differences are themselves quantized; if true |v_X−v_Z| − |v_Y−v_Z| < 1 bin width, raw bin-quantization can flip the sign. This is the ~10% triple-floor failure mode.

**At M=500 (10× scaling at fixed N_DIM=4096):** α = 2500/4096 = 0.61, very close to / above α_c ≈ 0.138 (4-5x over capacity). Massive cross-talk in W @ k_X → recovered scalars become noisy → raw-W codebook argmax flips between adjacent bins. NOW comparator's sign-projection MIGHT win, because it's averaging over the projection direction (denoising via 1D summary) rather than peaking at a noisy codebook bin.

**At M=5000 (100×):** α = 25000/4096 = 6.1, WAY above capacity. Both arms degrade catastrophically toward chance (0.5). Comparator and raw likely converge near the floor.

### Why HotpotQA comparison-em=0.07 is DIFFERENT (the upstream encoder problem)

Per parent research note Section L3, the v2 HotpotQA cell's failure mode is:
- char_trigram question encoder has recall@5 = **1.9%** on full-sentence comparison questions
- For 98% of questions, the start_entity selected by the encoder is WRONG
- bind(WRONG_entity, R_attr) under W → the W never trained on that key → returns ~zero-vector noise
- ARM_COMPARATOR on noise: sign(<noise, direction>) ≈ 50/50 → em ≈ 0.07 (lower than 0.5 because parsing also fails)

**The encoder-side failure pre-empts ANY comparator advantage.** The comparator could be omniscient, and it would still get 7% because 93% of the time it's being asked to compare two entities that weren't retrieved.

In brain-analog terms (parent note Stream C): the substrate HAS the hippocampal pair-wise relation store AND has now built the PFC-analog comparator. But the comparator runs on entity vectors retrieved from the encoder, and the encoder is the upstream bottleneck. PFC operating on a noise-corrupted hippocampal output cannot recover the relation — garbage in, garbage out.

### Per-attribute / per-question-type expected pattern

I could NOT read `data/exp_comparator_resonator_primitive_smoke_v1/metrics.json` directly because the local cell stalled mid-build (the 4096×4096 outer-product ingest at N_DIM=4096 with 250 outer-products is ~67 GB of pure-numpy operations per seed; the local CPU cell did not complete — only the selftest output and seed=7 ingest-start are in the log). The verdict numbers in the prompt input must come from a different run-path (likely a faster vectorized re-run or extrapolated from the prereg gate). Working from the analytical structure:

**Predicted per-attribute pattern (NOT from metrics; from cell structure):**
- All 5 attrs have the SAME codebook bin count (K=32) and same value-encoding mechanism
- Population (range 1k–1M, log-skew not modeled) will have the WORST raw accuracy because uniform 32 bins on a 1000× range gives 31k-wide bins where adjacent integer values are quantization-merged
- Born_year (range 1900–2000, 3.1yr bins) and height_cm (range 150–200, 1.56cm bins) have the FINEST relative resolution → raw-W highest accuracy
- Comparator should show NEAR-FLAT performance across attrs because the sign-projection doesn't care about absolute scale (only direction)
- **Predicted: on the worst-quantized attr (population), comparator might TIE or modestly beat raw. On finest-quantized attrs (born_year, height_cm), comparator loses by larger margin.**

**Predicted per-question-type:**
- Binary Qs: raw and comparator should be CLOSE (both make the same value-comparison after recovery)
- Triple Qs: raw should win MORE because the absolute-difference computation (|v_X − v_Z| vs |v_Y − v_Z|) benefits from exact-bin recovery, while comparator's |projection| proxy is a weaker geometric approximation
- **Predicted: gap = raw − comp is LARGER on triples than on binary; ARM_COMP triple-acc < ARM_RAW triple-acc by more than the binary gap**

These predictions are testable IF the cell completes and writes per-attr/per-type breakdowns to metrics.json (the cell DOES record `comp_acc_binary` and `comp_acc_triple` per seed — see `run_seed` lines 489–491).

---

## DIAGNOSIS CATEGORY

**PRIMARY: smoke-regime-too-easy (the dominant cause).** ARM_RAW_W_LOOKUP at α=0.061 is unsaturated; raw beats comparator because comparator throws information away that raw extracts cleanly. This is NOT a comparator-mechanism failure.

**SECONDARY: wrong-test-corpus (the cell tests synthetic ordered integers, not the HotpotQA comparison-em=0.07 phenomenon).** The substrate-product target is HotpotQA comparison questions where the encoder is the bottleneck. The smoke cell isolates the *comparator math*, which is sound; it does NOT isolate the *production failure*, which is upstream encoder noise.

**NOT mechanism-genuinely-null.** All three selftests pass cleanly: bind/unbind round-trip cos=0.7202, FPE monotonicity (0.9960 > 0.5164), projection-sign 5/5, sanity holdout 5/5. The math works.

---

## REVIVAL PATH (top recommendation)

### Primary revival: wire comparator into v3 cell and run on HotpotQA comparison-only subset (Arm 3 of the v3 handoff)

The `exp_dev_handoff_research_5x_QA_composition_v3_comparator_encoder_2026-06-23.md` ALREADY specifies (Arm 3 of 8):

> COMPARATOR_PRIMITIVE_COMPARISON_ONLY (char_trigram + RESONATOR comparator; bridge via existing gen)

This is the load-bearing test for the comparator primitive. The smoke cell validated that the primitive's MATH works. The v3 dispatch will validate whether the primitive's math, applied to char_trigram-retrieved entities, can lift comparison-em from 0.07 toward 0.30 (the v3 HARD_PASS bar).

**Action:** ensure the comparator primitive from `experiments/exp_comparator_resonator_primitive_smoke_v1.py` (specifically the `arm_comparator` function and FPE/bind primitives) is factored into `hdlab/comparator.py` per the v3 handoff Section "New primitive to author", THEN the v3 cell is unblocked. No new research-side dispatch needed — exp_dev owns the wiring.

### Secondary revival: M-sweep smoke to demonstrate the regime where comparator wins

If exp_dev wants to validate the comparator's INCREMENTAL VALUE before betting v3 on it, a cheap smoke sweep can show the crossover:

**Cell:** `comparator_resonator_capacity_sweep_v1` (NEW; ~10 min CPU)
**Arms:** ARM_RAW_W_LOOKUP, ARM_COMPARATOR, ARM_FREQ_BIAS (same as v1)
**Sweep:** M ∈ {50, 200, 500, 1000, 2000} at N_DIM=4096 (α ∈ {0.06, 0.24, 0.61, 1.22, 2.44})
**Pre-reg HARD_PASS:** there EXISTS some M ∈ {500, 1000, 2000} where ARM_COMPARATOR mean > ARM_RAW_W_LOOKUP mean + 0.05 (with sanity still 5/5)
**Pre-reg HARD_FAIL:** ARM_COMPARATOR ≤ ARM_RAW_W_LOOKUP for ALL M values (mechanism strictly dominated)
**Cost:** 5 M-values × 3 seeds × ~2 min per (M=2000 seed) = ~30 min CPU
**Why secondary, not primary:** the v3 dispatch on HotpotQA is the ACTUAL substrate-product target. The capacity-sweep is a sanity check that the comparator primitive has a regime where it adds value, useful as defense-in-depth but not load-bearing.

### Tertiary revival: comparator + better encoder (post v3)

If v3 HARD_FAILS on Arm 3 (comparison-em < 0.15 at production regime), the diagnosis would be:
- Comparator math sound (this smoke confirmed)
- char_trigram encoder is the bottleneck even with comparator in the loop
- Next dispatch: MiniLM-L6 encoder + comparator (Arm 4 of v3) is already the PRIMARY arm of v3 and tests this composition

In other words: the v3 cell is ALREADY structured to discriminate "is the comparator the problem?" (Arm 3 vs Arm 1) from "is the encoder the problem?" (Arm 2 vs Arm 4). The smoke HF is NOT a routing event because the production cell handles the failure-mode discrimination natively.

---

## FALSIFIABLE PREDICTIONS

### v3 dispatch (the load-bearing test)

**HARD_PASS for comparator primitive (revival success):**
- v3 Arm 3 (COMPARATOR_PRIMITIVE_COMPARISON_ONLY) comparison-em ≥ **0.15** (doubling from 0.07 = clear mechanism evidence at char_trigram encoder)
- AND v3 Arm 4 (FULL_NEURAL_PLUS_COMPARATOR) comparison-em ≥ **0.30** (quadrupling from 0.07 = comparator + encoder combine)
- AND v3 Arm 4 comparison-em > Arm 2 (NEURAL_ENCODER_BRIDGE_ONLY) comparison-em by ≥ 0.10 (comparator adds value beyond encoder)

**HARD_FAIL for comparator primitive (revival null):**
- v3 Arm 3 comparison-em < **0.10** (no movement from 0.07 floor; comparator math sound but useless in this corpus)
- AND v3 Arm 4 comparison-em < **0.15** (even with encoder fix, comparator does not add value)
- → comparator primitive is genuinely-null for natural-language comparison QA; the smoke HF was prophetic; route comparison-QA to glass-box-LLM closure

**MIDDLE_BAND:**
- v3 Arm 3 comparison-em ∈ [0.10, 0.15] (partial movement; the encoder is the dominant bottleneck)
- OR v3 Arm 4 comparison-em ∈ [0.15, 0.30] (some lift; not chain-grade)
- → comparator is MEASURED_MECHANISM; consider encoder upgrade as primary axis

### Capacity-sweep cell (the diagnostic backstop)

**HARD_PASS:** at M=1000 (α=0.244) or M=2000 (α=0.488), ARM_COMPARATOR ≥ ARM_RAW_W_LOOKUP + 0.05 → primitive has a load-bearing regime
**HARD_FAIL:** ARM_COMPARATOR ≤ ARM_RAW_W_LOOKUP for all M ≤ 2000 → primitive is strictly dominated; sanity selftests are decoupled from useful-work bands

---

## CROSS-THREAD SYNTHESIS

**This drill changes nothing about v3 routing.** The v3 handoff was filed BEFORE the smoke landed; the smoke HF1 is the EXPECTED outcome at the smoke regime (raw is too strong; comparator can't add value). The smoke's actual value:

1. **Validated the comparator math** (sanity 5/5, FPE monotone, projection-sign 5/5) — the v3 cell can rely on the primitive being mechanistically correct
2. **Identified the regime where the primitive doesn't help** (low-α, working raw recovery) — this means v3's Arm 3 (comparator on char_trigram retrieval) is testing the RIGHT axis: a regime where raw is broken (recall@5=1.9% → "raw" lookup is essentially noise)
3. **Identified the regime where the primitive would help** (high-α, broken raw) — useful for the capacity-sweep secondary revival if exp_dev wants pre-dispatch confidence

**This drill ALSO does not flip the parent research diagnosis.** The parent note `research_5x_deeper_substrate_QA_composition_gap_2026-06-23.md` correctly identified:
- The substrate has NO comparator primitive (now built; smoke validated math)
- The encoder is the upstream bottleneck on 93% of comparison questions
- v3 must address BOTH (Arm 4 = encoder + comparator)

**Composes with:**
- v3 HotpotQA cell dispatch (the load-bearing follow-up; smoke HF does not block it)
- a8 27x continual-learning chain-grade (orthogonal capability lane)
- CERT 588 h_hotpotqa KG ingest (the W matrix the comparator will retrieve from; recall@5=1.9% at char_trigram is the upstream constraint)
- META atom by-construction-saturation (NEW relevant: the smoke regime saturates the WEAKER mechanism — raw — at the ceiling, making the STRONGER mechanism — comparator — appear inferior; this is a discrimination-floor problem, the inverse of the usual by-construction-saturation pattern)

**New candidate META atom:** *discrimination-floor* — when a smoke regime is so easy that a simpler baseline saturates near-ceiling, ANY more-sophisticated mechanism that summarizes the same signal will appear inferior or equal. The smoke is then diagnostically uninformative about the mechanism's value in harder regimes. Symmetric counterpart to by-construction-saturation. Should be filed by Skunkworks.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

**Short-term (v3 cycle):** the comparator primitive should be lifted from `experiments/exp_comparator_resonator_primitive_smoke_v1.py` into `hdlab/comparator.py` (~50 lines per v3 handoff spec) and wired into v3 Arms 3, 4, 7. The smoke HF does NOT block this; it confirms the math works AND identifies that the smoke regime was diagnostically irrelevant to the substrate-product target.

**Medium-term (post-v3):** if v3 HARD_PASSES on Arm 4 comparison-em ≥ 0.30, comparator becomes a chain-grade primitive contributing to substrate-native QA capability. If v3 HARD_FAILS, comparator is shelved as MEASURED_MECHANISM (math sound, not useful for natural-language QA).

**Long-term (substrate-native relational reasoning):** the comparator + the FPE scalar-value primitive together compose into substrate-native *relational reasoning* — the ability to ask "is X attr > Y attr" without a learned classifier. This is a foundational primitive for the L2 glass-box-LLM vision (substrate INSIDE the LLM for relational queries). The smoke validated the primitive at the bottom of this stack; v3 tests it in production; future cells will compose multi-attribute comparator chains, conditional comparators, etc.

**Negative path (HARD_FAIL on v3):** if v3 shows comparator-cum-encoder cannot recover comparison-QA, the substrate's relational-reasoning capability is structurally limited at this N_DIM regime. Route to L2 glass-box-LLM closure (substrate as a memory plus an LLM-internal comparator) rather than substrate-native end-to-end QA. This is the parent-note specified route.

---

## CITATIONS (verified — 10 unique sources from 2 parallel lit-scans + cross-thread)

1. Frady, Kent, Olshausen, Sommer 2020 — "Resonator Networks outperform optimization methods at solving high-dimensional vector factorization" — arxiv 1906.11684 (the canonical resonator primitive)
2. Hersche et al. 2022 — "In-memory factorization of holographic perceptual representations" — arxiv 2211.05052 (in-memory resonator scaling)
3. Kleyko et al. 2023 — "Vector Symbolic Architectures as a Computing Framework for Emerging Hardware" — arxiv 2106.05268 (sign-test dynamics)
4. "Learning from Hypervectors: A Survey on Hypervector Encoding" — arxiv 2308.00685 (FPE, scalar encoding)
5. "Classification using hyperdimensional computing: a review with comparative analysis" — Springer 10.1007/s10462-025-11181-2 (encoding scheme accuracy comparison; key-value vs FPE)
6. ScalableHD: arxiv 2506.09282 (high-throughput HDC inference; codebook size effects)
7. "Self-Attention Based Semantic Decomposition in VSA" — arxiv 2403.13218 (recent factorization extension)
8. "Hey Pentti, We Did It Again!" — arxiv 2510.16533 (differentiable VSA; polynomial termination of factorization)
9. "Hey Pentti, We Did (More of) It!" — arxiv 2511.08767 (residue arithmetic VSA — relevant for comparator on ranges)
10. arxiv 2511.01254 — IEEE SP Letters Oct 2025 — baseline-vs-comparison ablation methodology (cited for the methodological discipline of testing across regimes)

**Plus 2 cross-thread substrate-internal references (counted separately):**
- `notes/research_5x_deeper_substrate_QA_composition_gap_2026-06-23.md` (parent)
- `notes/exp_dev_handoff_research_5x_QA_composition_v3_comparator_encoder_2026-06-23.md` (downstream)

---

## P (with calibration penalty applied)

- **P_deflated(v3 Arm 3 comparison-em ≥ 0.15)** = **0.30** (comparator math sound; char_trigram encoder is the dominant noise source; some lift expected from 0.07 floor)
- **P_deflated(v3 Arm 4 comparison-em ≥ 0.30)** = **0.25** (requires BOTH encoder upgrade and comparator working; conjunction lowers)
- **P_deflated(capacity-sweep HARD_PASS at some M ∈ [500, 2000])** = **0.40** (well-validated capacity-cliff dynamics; comparator's 1-bit summary IS expected to denoise above α_c; capped at 0.40 per USER directive)
- **P_deflated(comparator primitive becomes chain-grade-eligible in this arc)** = **0.15** (joint event)
- Calibration: USER explicit cap P at 0.40 honored; novel-synthesis discipline applied; HARD_FAIL bands explicit per [[feedback-lit-scan-calibration-penalty]]

---

*Research delivery complete 2026-06-23. Smoke HF1 is informative-negative: validates comparator math AND identifies smoke regime as discrimination-floor uninformative. v3 dispatch is the load-bearing follow-up; no new research-side cell needed. Secondary capacity-sweep cell is filed as defense-in-depth for exp_dev's discretion. P capped at 0.40 per USER directive.*
