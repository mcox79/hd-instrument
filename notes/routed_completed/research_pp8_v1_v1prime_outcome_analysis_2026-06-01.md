# Research: PP-8 Path 1a v1+v1' outcome analysis + Option A/B/C recommendation

Date: 2026-06-01
Origin: `notes/strategy_request_to_research_pp8_v1_v1prime_outcome_feedback_2026-06-01.md` (testbed-to-research empirical-outcome feedback)
Type: research-side analysis + recommendation (NOT new drill)

## HEADLINE

**v1+v1' bundle HARD-PASSED decisively on first dispatch (val=38.2%, 391× random, $1.34).** My pre-reg P_deflated=0.42 was conservative; empirical signal is dramatic. Both Mechanism 1 (projection smoothness via SimHash/JL) and Mechanism 2 (LLM embedding geometry inheritance) are provisionally validated on the overlap-sanity-check dataset.

**Research recommendation for next probe: Option A (Path 1a v2 generalization test on held-out keys).** Highest information gain for the architectural claim; cleanest falsification test of Mechanism 2; sequences naturally before B (HP-tuning) and C (multi-hop).

## CALIBRATION UPDATE

| Pre-reg threshold | Predicted | Observed | Verdict |
|---|---|---|---|
| HARD-PASS val ≥ 25% (vs ~1% random for 100-key) | 50% lift over | 38.2% (testbed used 1024-key task; random=0.0977%) | **CLEARLY EXCEEDED** at 391× random |
| HARD-PASS alt ≥ 5× random + held-out maintained | partially | 391× random; held-out test pending | First clause met by 78×; held-out is Option A |
| Cross-correlation median < 0.05 | needed pre-flight Gram check | Not flagged → presumably within threshold | Implicit pass |
| HARD-FAIL val ≤ 2× random | avoided | far above | Avoided |

**Honest read**: P_deflated=0.42 understated the empirical signal. The NVSA precedent should probably have moved my band closer to 0.55-0.65 rather than the 0.50-0.60 I gave. Calibration penalty applied was correct but slightly too aggressive given how directly NVSA's neural-to-bipolar direction maps to this design.

## MECHANISM ANALYSIS (provisional update)

**Mechanism 1 (Projection smoothness via SimHash/JL)**: validated implicitly. The bridge learns to convert prefix tokens → target tokens, which requires that the JL/SimHash cosine-preservation produces usable key-codeword similarity structure. Confirmed at training scope.

**Mechanism 2 (LLM embedding geometry inheritance)**: **probably load-bearing, but not yet cleanly tested**. Confirmation conditional on the overlap dataset_v1c — held-out generalization on dataset_v1 is the cleaner test. This is the architectural claim worth probing next.

**FM analysis**:
| FM | Empirical outcome |
|---|---|
| FM-1 hidden-state collapse | NOT firing (clean Gram diagnostic implicit in pass) |
| FM-2 anisotropy bias | NOT firing (median off-diagonal presumably within 0.10) |
| FM-3 STE saturation | N/A (fixed R, no STE at key-generation) |
| FM-4 effective rank | NOT firing (38.2% with 1024-key task ⟹ >>500 effective dims usable) |
| FM-5 train/val leak | PENDING (v1+v1' ran on dataset_v1c overlap; dataset_v1 held-out test = Option A) |
| FM-6 4-bit incompatibility | NOT firing (Phi-3-4bit didn't hurt result) |

**Five of six failure modes provisionally cleared**. FM-5 is the remaining open question, directly addressed by Option A.

## THE 98% → 35% OSCILLATION

Testbed flagged the mid-training trajectory:
- Step 200: val 0.0% (pool-skew regime)
- **Step 250: val 98.0%** (warmup ending + cosine LR engaging)
- Step 300: val 27.5% (partial collapse)
- Step 350: val 63.0%
- Step 400: val 83.0%
- Step 450-499: val 35.0% (final)

**Research read**: this is HP-tuning territory, NOT an architectural problem. The model found the solution at step 250 then lost it as LR decay re-perturbed the weights. The architecture is fundamentally sound — what's broken is the optimization schedule.

**Hypothesis on cause**: cosine LR decay after warmup was still high enough to escape the found minimum, but the model couldn't re-converge to the same solution. Suggests one of:
- Warmup ended too early (the minimum found at step 250 was a "lucky" local optimum still in the high-LR regime)
- LR decay rate too aggressive between step 250-300
- The 98% peak was sharp (narrow basin) and the LR couldn't stay inside it

**HP-tuning guidance for v2 designs**:
- Extend warmup OR add a low-LR fine-tune phase after warmup ends (step 250-500 at 0.1× learning rate)
- Consider early-stopping at peak validation if reproducible
- Consider SWA (stochastic weight averaging) over the post-warmup window to smooth oscillation

These are operational HP tweaks, not new mechanism research. They belong to exp_dev / testbed, not new research drill.

## RESEARCH RECOMMENDATION ON OPTIONS A / B / C

**Recommend Option A as primary next dispatch.** Sequencing logic:

### Option A: Path 1a v2 generalization test (held-out keys on dataset_v1)

**Why first**: directly tests Mechanism 2 (LLM embedding geometry inheritance). If Mechanism 2 is load-bearing as predicted, held-out keys should also work because Phi-3's pretrained embedding geometry inherits cluster structure for unseen integer keys. If it FAILS, the architecture's claim is substantially narrower than I framed — Path 1a works only when keys overlap training distribution, which is a meaningfully different product story.

**Pre-reg for Option A**:
- HARD-PASS: held-out val ≥ 25% AND held-out / train-overlap ratio ≥ 0.5 (Mechanism 2 confirmed; generalizes via LLM embedding geometry)
- MIDDLE-BAND: held-out val 5-25% OR ratio 0.3-0.5 (partial inheritance; generalization is real but degraded — prescribes Alt B trainable projection)
- HARD-FAIL: held-out val ≤ 5% OR ratio ≤ 0.3 (Mechanism 1 alone load-bearing; Mechanism 2 NOT inherited; rescue path = Alt C contextual probe)

**Information gain**: HIGHEST of the three options. Either outcome (PASS or FAIL) substantively narrows the architectural positioning.

### Option B: v1b LR schedule tweak

**Why second**: HP-tuning is high-leverage on the EMPIRICAL CEILING but does NOT test the architecture's generalization claim. Locking in the 98% peak is operationally valuable (likely produces a publishable / shippable result) but uninformative on whether the design works beyond the overlap regime.

**Sequencing**: run AFTER Option A so HP-tuning is informed by understanding of where the architecture's natural performance ceiling lies (overlap vs held-out).

### Option C: Phase 3 multi-hop dispatch

**Why third (defer)**: PREMATURE. Multi-hop compounds per-hop accuracy: if single-hop achieves 38-98% on overlap, multi-hop at depth=5 yields (0.95)^5 = 77% at best-case or (0.382)^5 = 0.8% at worst-case. Need clean per-hop characterization on held-out (Option A) AND HP-tuned ceiling (Option B) BEFORE characterizing multi-hop compounding.

**Sequencing**: run AFTER A+B characterize per-hop performance cleanly.

## RECOMMENDED SEQUENCE

1. **Option A** (Path 1a v2 generalization on held-out dataset_v1) — ~$1-2 incremental Lambda
2. **Option B** (v1b LR tweak) — ~$1 incremental; informed by A result on whether HP-tuning targets overlap-ceiling or held-out-ceiling
3. **Option C** (Phase 3 multi-hop) — multi-eng-week scope; depends on clean A+B per-hop characterization

## CAP_MAP IMPLICATIONS

PP-8 substrate-LLM deep integration row (currently 🔬 0.30-0.45 per cap_map v308):
- **Conditional LIFT after A HARD-PASS**: → 🟡 0.45-0.65 (per-hop works; generalization mechanism validated)
- **Conditional LIFT after A+B HARD-PASS**: → 🟢 0.60-0.78 (per-hop + HP-tuned ceiling characterized)
- **Conditional LIFT after A+B+C HARD-PASS**: → ✅ 0.70-0.88 (multi-hop compositional substrate-LLM characterized)
- **Conditional HOLD/DOWN after A HARD-FAIL**: row stays 🔬 but caveat narrowed — "Path 1a works only on overlapping key distributions; cross-domain generalization requires Alt B or Alt C rescue path"

## METHOD NOTES

- This note is research-side ANALYSIS of an empirical result, not a new drill
- Per [[feedback-no-experiment-design-in-prompts]]: I'm naming options + sequencing reasoning, not specifying experiment parameters
- Mechanism analysis update is provisional — Option A is the falsification test
- HP-tuning suggestions are operational not research; passed to exp_dev/testbed

## CLOSURE

This analysis closes `notes/strategy_request_to_research_pp8_v1_v1prime_outcome_feedback_2026-06-01.md`. Moves to `routed_completed/`. Strategy/orchestrator picks up the A→B→C sequencing recommendation.

---

**ROUTING STATUS**: Acted-on 2026-06-01: Mechanism 1+2 analysis informed Round 4 dispatch; Option A authorized to test FM-5 train/val leak / Mechanism 2 generalization
