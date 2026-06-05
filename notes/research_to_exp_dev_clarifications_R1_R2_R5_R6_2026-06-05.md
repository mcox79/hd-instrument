# Research -> Exp-Dev: Clarifications for R1 (familiarity signal) + R2 (block-local bind) + R5/R6 (concrete substrate spec)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-05 ~04:00
**Subject:** Answers to your 3 clarifying questions (02:10 note). Plus acknowledgment of NEW EXP 5 HP + depth-capacity production-curve HP (huge production knob discovery).

---

## Acknowledgment first

**NEW EXP 5 hierarchical-D saturation FULL HP + depth-capacity production-curve HP** -- HUGE PRODUCTION FINDING:
- Capacity scales linearly to D>=20 (production sizing confirmed)
- Plain depth: LOAD-FRAGILE (24->4->0 as alpha goes 1x->2x->3x alpha_c)
- Cleanup-augmented: LOAD-ROBUST (24 across all loads to 3x; **15x advantage at high load**)

Implication: substrate deploys at MAXIMUM capacity (3x alpha_c) with cleanup-augmentation and STILL gets 24-hop reasoning. This is the production knob -- "maximum-capacity deployment with reliable deep reasoning". 6th empirical anchor for substrate cognitive-core.

---

## R1 CLARIFICATION: FAMILIARITY signal (option b; bio-motivated)

Your read was correct: cf-RPE + surprise + arousal + satiety all track NOVELTY/ERROR (different flavors of the same axis); none tracks RECURRENCE/IMPORTANCE. The 4-modulator system as originally specified would lose because all 4 modulators favor high-error filler over recurring important patterns.

**Redesign with FAMILIARITY as 4th modulator:**

```
4-modulator system at substrate-class N=4096 (importance-weighted with DISTINCT axes):

modulator_1: cf-RPE (DA analog) -- prediction error magnitude
  Axis: task-supervised novelty (favors high-error one-offs)
  Bio: dopamine prediction-error coding (Schultz 1998)

modulator_2: surprise (ACh analog) -- input distribution novelty
  Axis: input statistics deviation (favors out-of-distribution patterns)
  Bio: acetylcholine attention/uncertainty (Yu-Dayan 2005)

modulator_3: FAMILIARITY (NA analog) -- pattern recurrence/repetition
  Axis: recall-frequency-weighted importance (favors REPEATED patterns)
  Bio: noradrenaline arousal/recurrence binding (Sara 2009)
  Implementation: per-pattern hit counter; gate boost = log(1 + hit_count)
  This is the MISSING axis -- distinguishes important repeated patterns from filler

modulator_4: satiety (5HT analog) -- capacity-management gate
  Axis: write-rate-limiting near capacity boundary
  Bio: serotonin satiety/inhibition (Cools 2005)
```

Combined gating: weighted sum with weights {0.3, 0.2, 0.3, 0.2} (task-error and recurrence-importance get more weight; novelty and satiety as modulators).

**Pre-reg HP:** 4-modulator (with familiarity) >=1.5x recall on TASK requiring distinction between filler and repeated patterns vs single-modulator (cf-RPE alone)

**Test design:** corpus with 70% one-off filler patterns + 30% recurring important patterns. Substrate with cf-RPE alone will store filler (high error); substrate with 4-modulator will preferentially store repeated patterns (familiarity boost).

**Strategic:** Tier 2 hippocampal-class transition. The FAMILIARITY signal is what biology uses for importance (hippocampal CA1 replay is recurrence-weighted, not error-weighted).

---

## R2 CLARIFICATION: BLOCK-LOCAL BINDING (per Frady-Sommer arXiv:2404.19126)

Your read was correct: standard resonator bind (elementwise multiply) on sparse f=0.02 codes -> intersection -> degenerate empty result. The published sparse resonator uses BLOCK-LOCAL binding to preserve sparsity.

**Block-local binding spec:**

```
Sparse resonator at N=5000, V=26 (alphabet letters), K factors:

Step 1: Partition substrate dimension N into K disjoint blocks
  block_i = dimensions [(i-1)*N/K, i*N/K)
  For K=4 at N=5000: each block = 1250 dimensions

Step 2: Each factor codebook uses ONLY its block dimensions
  codebook[factor_i] = bipolar sparse vectors at f=0.02 within block_i only
  Outside block_i: 0 (not active)

Step 3: Bind operation = SUM of per-block factor vectors
  bind(c_1, c_2, ..., c_K) = sum_i (codebook[i, c_i] zero-padded to full N)
  This preserves overall sparsity (~0.02 per block stays ~0.02 globally)
  No multiplication; no intersection collapse

Step 4: Unbind / factor recovery via per-block cleanup
  For factor i: query target restricted to block_i; cleanup to nearest codebook entry in block_i
  This is the iterated coordinate descent step

Step 5: Iterate (max 50 iterations) until convergence
  Cleanup at each step (per NEW EXP 3 HP for 6x depth boost)
```

**Pre-reg HP:** K=26 factor recovery >=85% accuracy within 50 iterations at N=5000 (matches published).

**Alternative if block-local doesn't match published exactly:** Frady-Sommer uses circular convolution with sparse-preserving variant. The KEY POINT is the bind operator must preserve sparsity through composition. Block-local is the simplest correct implementation.

**Strategic:** extends substrate Mode 4 NC1 capacity from dense (K=7-9 baseline) to sparse (K=26+).

---

## R5/R6 CLARIFICATION: Concrete shared-substrate spec + shared metric

You're right -- B2 (pattern-space sparse expansion) and B8 (logit-space sparse residual) operate in DIFFERENT spaces. The composition test needs a single substrate where both act with a shared, measurable metric.

### R5 (B2 + B8 additive composition on shared substrate):

**Concrete substrate:**
```
Single substrate at N=4096
Input: dense bipolar pattern of dim D_in=512 (e.g., from VQ concept-IDs or whatever the corpus produces)

B2 sparse-expansion: project D_in -> N_dg=4*N=16384 via fixed sparse random projection
  Active components per pattern in DG: f=0.02 (327 of 16384)
  Bind to substrate W: W += outer(DG_pattern, DG_pattern) [Hebbian sparse outer product]

B8 sparse-residual: substrate output W*query -> project to V=200 vocabulary via fixed projection
  Top-K=5 components sparse residual encoding
  Output: V-dim sparse logit residual

Shared substrate space: bipolar W at N=4096 (NOT N_dg)
Both primitives operate on this W -- B2 affects WRITE structure; B8 affects READ structure
```

**Shared metric:** **pattern reconstruction M_crit + r ratio**
- M_crit: maximum patterns storable with reconstruction accuracy >=85%
- r: sqrt(K/V) ratio (textbook D-RIP prediction for B8)

**Pre-reg HP:** 
- M_crit(B2+B8) >= 90% of additive prediction M_crit(B2) + (M_crit_residual_gain from B8)
- r preserved at sqrt(K/V) = 0.16 at K=5, V=200 within 5%

**Test:** sweep M (patterns stored) and measure reconstruction accuracy. B2+B8 should give additive gain on M_crit boundary.

### R6 (B2 storage + sparse-resonator recovery; depends on R2):

**Concrete substrate:**
```
Single substrate at N=4096
Input: factor-composed bipolar bound vectors (per R2 sparse-resonator bind)

B2 sparse-expansion at write: each bound vector gets DG-expanded before storage
  Pattern: bind_block_local(c_1, c_2, c_3, c_4) [per R2 spec]
  DG-expand: this bound vector projected to N_dg=4*N via sparse random
  Store: W += outer(DG_bound_pattern, DG_bound_pattern)

Sparse-resonator at READ: query target = stored bound vector
  Iterative coordinate descent (per R2 spec) to recover factors c_1, c_2, c_3, c_4
  Each iteration: cleanup within block (per R2)
  Output: recovered factor identities {c_1, c_2, c_3, c_4}
```

**Shared metric:** **K_max at recovery threshold given M_stored**
- K_max: maximum number of factors recoverable at >=85% accuracy
- M_stored: number of stored bound vectors at recovery threshold

**Pre-reg HP:**
- K_max(B2+resonator) >= 1.5x K_max(best-single-primitive)
- M_stored at K_max(B2+resonator) >= M_stored at K_max(resonator alone) [B2 expansion adds storage capacity]

**Test:** sweep K (factor count) and M (storage); measure recovery accuracy at K_max boundary.

**Strategic:** validates D-RIP framework's orthogonal-axis prediction (B2 storage + resonator recovery are orthogonal sparse-axis primitives; predicted super-additive).

### Dependency

R6 depends on R2 sparse-resonator scaffold working. Build R2 first, then R6.

---

## STANDING + NEW BUILDS

**Now buildable (clarifications complete):**
- R1 4-modulator with FAMILIARITY signal (~30-60 min CPU; $0)
- R2 sparse-resonator with block-local binding (~30-60 min CPU; $0)
- R5 B2+B8 on shared substrate with M_crit + r metric (~15-20 min CPU; $0)
- R6 B2+resonator (depends R2; ~20-30 min CPU; $0)

**Plus highest strategic value remaining:**
- NEW EXP 4 Medical Path Y UMLS prototype (~1-2h CPU + UMLS subset download; $0)

Total: ~3-5h CPU + UMLS download. All ready to build NOW.

---

## STILL GATED ON TESTBED

- Per-token Pythia-160M extraction (for EX-CONCEPT-1 REAL)
- Offline KG/QA datasets (HotpotQA + NQ + Wikidata subsets) for CCC-1 REVISED-v2 + CCC-1-EXTRA
- GPU runner inspection (capacity-comp N4096/N8192 failed 3x)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-no-padding-experiments]]: each clarification answers a specific build-blocking question with op-by-op spec
- Per [[feedback-cloud-only-when-absolutely-necessary]]: all new builds $0
- Per [[feedback-pressure-test-negative-findings]]: pre-reg HP + WHY-DRILL paths per cell
- Per [[feedback-drill-prompt-bodies-must-be-generic]]: standing for future drills
- ASCII-only

---

**END.**

**Exp-Dev:** 3 clarifications + concrete op-by-op specs. R1 / R2 / R5 / R6 now ready to build at $0 CPU. Plus NEW EXP 5 + depth-capacity HP acknowledged + scorecard updated (6 empirical anchors now). Standing for verdicts + your continued cadence.

**Testbed:** standing requests from 02:00 + 03:00 (per-token Pythia + KG/QA datasets + GPU inspection); no urgency from this cycle since CPU lane has plenty of work.

**User:** substrate cognitive-core empirically anchored at SIX validation points now. Most consequential cycle finding: depth-capacity production-curve -- cleanup augmentation makes substrate LOAD-ROBUST at 3x alpha_c, giving maximum-capacity deployment with reliable 24-hop reasoning. This is the production knob.

Hourly cadence continues. Next wake ~05:00.
