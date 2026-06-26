# Research drill -- MM-tier promotion paths via phase-diagram discriminators

**Date:** 2026-06-25 (USER directive DRILL 2 of 2; runs parallel with DRILL 1 base-primitive envelopes)
**From:** research (Director)
**Scope:** identify the discrimination regime that promotes each MEASURED_MECHANISM (MM) item to CHAIN_GRADE_CONFIRMED
**Discipline:** Fix #28 default UNDER-claim; verbatim metrics off-data; cite tier-ruling notes verbatim
**Complement:** DRILL 1 covers chain-grade-with-envelope-untested items at EXTENSION; this drill covers MM items needing a DISCRIMINATION REGIME to promote.

---

## Executive verdict (under-claim discipline)

Five items today need a phase-diagram discriminator to promote from MM to chain-grade-confirmed. Of those, **two are URGENT** with discriminator cells either dispatched (anisotropy M=100k, in-flight on overnight_queue) or trivially specifiable (multi-bank WM adversarial regime). The other three (MULTIPLICATIVE_LEVER, capacity-sweet-spot adaptive sparsity, META-reasoning v3) need corpus or task-load engineering before a discriminator cell can be authored.

The honest framing: **MM is not "almost chain-grade." MM is "mechanism is measured; load-bearing claim is undetermined."** Some MM items have a clearly-specifiable discriminator (URGENT category); others have a discriminator that depends on corpus or task design we don't yet have. Mechanism engineering is NOT the gap for any of these five -- the gap is regime engineering.

Two items have a noteworthy structural risk: **MULTIPLICATIVE_LEVER and capacity-sweet-spot adaptive sparsity may NOT promote**. The cells already prove fixed f=0.01 is within-tolerance-of-oracle everywhere; an adaptive regime may not exist at substrate scale where load variance is large enough for f-adaptivity to fire. These are demoted candidates whose path-to-chain-grade may be falsified, not engineered.

---

## Item 1 -- Anisotropy fly-LSH rescue (URGENT, in-flight)

### Verbatim demotion reason (Skunkworks tier ruling 5-artifact wave, 2026-06-25)

> "4 of 4 working arms at >= 0.995. Cell's OWN bands metadata: `Q_SAT=0.995`. All 4 fired. Per by-construction-saturation tiering (Skunkworks-correctly-overrides-Director MEMORY rule 2026-06-23), default classification is MM not chain-grade when arms saturate equivalently. Discriminator-gap regime (M=100k adversarial-similarity keys) is required for chain-grade-confirmed promotion." (Artifact 1; lines 24-47 of `skunkworks_tier_ruling_5_artifact_late_wave_2026-06-25.md`)

Verified off-data at M=10000 (per_unit[seeds].by_M["M10000"], 3 seeds):
- arm1_raw: 0.0180 cv=0.041
- arm_A_cerebellar_K5: 0.0516 cv=0.103
- arm_Ap_dense_5x: 0.0618 cv=0.017
- arm_B_fly_lsh: **0.9971** cv=0.001
- arm_B_charikar: **1.0000** cv=0.000
- arm_C_compose: 0.9960 cv=0.000
- arm_D_meter: **1.0000** cv=0.000

55x rescue magnitude is real (raw 0.018 -> Bfly 0.997). The undetermined question: which mechanism (Bfly sparse-fan-in vs Bcharikar sign-sketch vs D meter calibration) is load-bearing.

### Discrimination regime

**M=100k with adversarial-similarity keys (consecutive-token stride-1 windows of natural prose; adjacent keys share 15/16 tokens by construction)** is the canonical promotion regime per Skunkworks's recommendation. Three differentiating mechanisms get separated:
- **Sparse fan-in expansion (Bfly):** if each KC reads K=5 random PNs, adjacent keys that share 15/16 tokens will sometimes pick distinguishing tokens. Should HOLD at M=100k.
- **Sign-sketch (Bcharikar):** projects whole key vector through random hyperplanes; adjacent keys with 15/16 overlap will land in same sign-bucket more often. Should DEGRADE relative to Bfly.
- **Generic dense Gaussian (AB_CONTROL):** uniformly-random projection without sparse-fan-in or sign quantization; if it saturates too, "any random projection works" and the LSH attribution from v2 is artifact.

### Cell spec

**Anchor:** `substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1`
**Status:** **DISPATCHED 2026-06-25 (overnight_queue / RTX 4060 Ti / commit f81d1567 / 9000s timeout)**
**Cell author:** exp_dev (per `exp_dev_to_research_anisotropy_M100k_adversarial_v1_DISPATCHED_2026-06-25.md`)
**M_SWEEP:** {10k, 50k, 100k}
**Arms:** 8 (raw, cerebellar_K5, dense_5x, Bfly, Bcharikar, compose, meter, AB_CONTROL)
**Pre-reg bands rewritten for discrimination:** HARD_PASS requires winning arm to beat peer LSH by >=0.05 AND beat AB_CONTROL by >=0.10. NOT absolute-threshold; discriminator-gap-only.

### IMPORTANT: USER task-brief framing correction (Fix #28)

USER's task brief states: "the M=10k slice from v3 partial showed: B_fly=0.189, B_char=0.193, AB_CONTROL=0.240, RAW=0.021" and frames this as "AB_CONTROL BEATS BOTH LSH ARMS at adversarial regime."

**Off-data verification: the v3 cell has NOT yet landed.** No metrics.json exists at `data/exp_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1/`. The numbers in USER brief are either from a pre-dispatch smoke not in the canonical artifact path, or from an OOM-aborted partial that was not preserved. Either way, under Fix #28 (read metrics.json before propagating cross-arm narrative) I cannot confirm those numbers off-data this cycle.

What IS true under verification: the v3 dispatch is in flight; the cell pre-reg is honest (AB_CONTROL must saturate <0.85 for chain-grade-confirmed claim to hold). If USER's preliminary numbers are accurate, the outcome will be `HARD_FAIL_CONTROL_ALSO_PASSES` -- which is itself a chain-grade negative-result (refutes v2's LSH attribution; promotes a different research question: "why does random expansion suffice on adversarial keys").

### P(chain-grade-confirmed after discriminator)

- **P(any LSH arm beats AB_CONTROL by >=0.10) = 0.45** -- USER's preliminary suggests LSH is NOT load-bearing on adversarial keys; but cell discipline says wait for full landing.
- **P(BOTH LSH arms collapse <=0.30) = 0.20** -- v2 0.997 was M=10k-easy artifact.
- **P(AB_CONTROL also saturates >=0.85, HARD_FAIL_CONTROL_ALSO_PASSES) = 0.35** -- consistent with USER preliminary; substrate's anisotropy story changes substantially.

All three outcomes are decision-grade. The cell is well-designed for sound discrimination; the regime engineering is done. The OOM USER mentions is in cell-runtime mechanics (matmul Qtc @ Ktc.t() needs batched chunking at 100k); the v3 dispatch includes a 2.5h budget with 2x headroom and the cell-author confirmed remote self-test passed at 4.0s on .venv. If OOM recurs at full M=100k, the fix is `python -u` batched matmul refactor (Fix #20 + chunked-batch); cell-author can ship within one cycle.

### Cell needed if v3 OOMs at full

**Anchor:** `substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched_matmul`
- Same arms / M_SWEEP / pre-reg as v3
- `Qtc @ Ktc.t()` rewritten with `torch.chunk(Qtc, n_chunks=8, dim=0)` loop accumulating per-chunk argmax_dot; reduces peak memory ~8x
- `python -u` to avoid Fix #20 subprocess pipe deadlock
- Dispatch via `hdi_orchestrator` -> `overnight_queue` (Fix #24: torch.cuda + batched ops + >=50% GPU util smoke)

---

## Item 2 -- Multi-bank WM routing (Cell Y' / today's striking result)

### Verbatim cell verdict (cell self-tag, NOT YET tier-ruled by Skunkworks)

> "RAIL_SANITY_BREACH_NAIVE_OUT_OF_CELL_D_BAND: ... best_multi_K256=ARM_MULTI_BANK_8x32_K256 recall=1.0000 cv=0.0000 route_acc=1.0000 lift_over_naive_K256=+0.5352 | K1024_stretch recall=1.0000 cv=0.0000 route_acc=1.0000 | n_multi_K256_lift_pass=4/4 [Q-DISCIPLINE: suspect saturation -- recall >= 0.995; UNDER-CLAIM tier]"

Verified off-data (3 seeds, N=4096, CODEBOOK=1024):
- ARM_NAIVE_SINGLE_BANK_K32: 1.0000 cv=0.0 (route_acc=1.0)
- ARM_NAIVE_SINGLE_BANK_K128: 0.8815 cv=0.020 (REAL seed variance; rail expected [0.85, 0.94] -> WITHIN rail)
- ARM_NAIVE_SINGLE_BANK_K256: **0.4648** cv=0.032 (rail expected [0.51, 0.60] -> BELOW rail; RAIL SANITY BREACH)
- ARM_MULTI_BANK_8x32_K256: 1.0000 cv=0.0
- ARM_MULTI_BANK_4x64_K256: 0.9987 cv=0.0018
- ARM_MULTI_BANK_2x128_K256: 0.8659 cv=0.018
- ARM_MULTI_BANK_16x16_K256: 1.0000 cv=0.0
- ARM_MULTI_BANK_32x32_K1024: 1.0000 cv=0.0

4/4 multi-bank arms at K=256 saturate at 1.000 cv=0.0. Also K=1024 stretch saturates. NAIVE_K256 was supposed to land in [0.51, 0.60] band but came in at 0.4648 (BELOW; rails breached). The rail breach itself is a methodology / regime concern.

### Discrimination regime

The mechanism under test is "multi-bank routing extends K-ceiling past single-bank capacity." At K=256, single-bank=0.46, multi-banks=0.87-1.0 -- mechanism IS doing work. But 4/4 multi-bank arms saturating identically means we cannot discriminate WHICH bank arrangement is load-bearing. Three bank arrangements all hit 1.000 cv=0.0 at K=256: 8x32, 16x16, 32x32. They differ by an order of magnitude in bank-count but achieve the same recall.

The adversarial regime that should discriminate:
1. **K_total > 1024**, e.g., K=2048 / 4096 / 8192 -- multi-bank arrangements eventually saturate; the question is at what K does 8x32 (small banks; partition becomes binding) diverge from 32x32 (large banks; per-bank cleanup binds first). Different bank x slot products encode different capacity-vs-routing tradeoffs.
2. **Items with shared features** (vs the current uniform-random items) -- if two items in different banks share enough features that the routing query is ambiguous, the routing-accuracy ceiling (currently 1.000 across all 9 arm/seed cells) drops. The mechanism's robustness to query ambiguity is the discriminator.
3. **Cross-bank crosstalk via correlated keys** -- the cell currently uses uniform random keys; if keys are correlated (anisotropic Pythia residuals from another cell), routing_acc may drop differently for different bank arrangements.

### Cell spec

**Anchor:** `substrate_working_memory_multi_bank_routing_K_extension_v2_adversarial`
**Routing:** `local_cpu_queue` (CPU-feasible at this scale; ~30s wall per seed at K=4096)
- **K_SWEEP:** {256, 512, 1024, 2048, 4096} -- extend until at least one arm cliffs
- **Arms (5):** NAIVE_SINGLE_BANK_K_full, MULTI_BANK_8x32 (extended bank-count proportionally), MULTI_BANK_4x64, MULTI_BANK_16x16, MULTI_BANK_32x32 (extended slot-count proportionally) -- all arms scale K_per_bank x N_banks to match K_total
- **Adversarial key regime:** binary keys with controlled feature-overlap rate (10/20/30% shared bits between items) -- creates query ambiguity at routing layer
- **Pre-reg bands rewritten for discrimination:**
  - HARD_PASS: at K_total where ALL multi-bank arms drop below 0.95, ranking of arms is stable across seeds (cv on ranking <= 1 position swap) AND winner beats runner-up by >=0.05 absolute
  - MIDDLE_BAND: all arms saturate identically through K=4096 (corpus still too easy at substrate scale)
  - HARD_FAIL: routing_acc collapses uniformly for all arms (mechanism doesn't survive query ambiguity at all)
- **Q-discipline guard:** if any arm hits >=0.995 EVEN AT K=4096 with feature-overlap=30%, BIAS-Q flag fires; corpus regime is fundamentally too easy

### P(chain-grade-confirmed after discriminator)

- **P(specific bank arrangement wins by >=0.05 at K=2048+) = 0.55** -- bank arrangements DO encode different capacity-vs-routing tradeoffs in theory; substrate should be expressive enough at N=4096 to surface the difference
- **P(all multi-bank arms saturate identically through K=4096) = 0.20** -- N=4096 is large; uniform random keys at any K may all fit cleanly
- **P(routing_acc collapses uniformly under adversarial query) = 0.15** -- depends on whether routing query is dot-product with cleanup or full HRR-decode
- **P(useful intermediate / partial discrimination) = 0.10**

Default expectation: **MIDDLE_BAND chain-grade-candidate** at K=2048 with feature-overlap=20%; one bank arrangement wins by ~0.10 absolute over runner-up; clean Q-discipline pass. Skunkworks tier-rule probable: chain-grade-confirmed.

---

## Item 3 -- MULTIPLICATIVE_LEVER

### Verbatim demotion reason (per USER task brief framing; Skunkworks demoted today)

> "selector picks fixed f=0.01 for EVERY task in envelope (degenerate, not adaptive); v2 already proves fixed f=0.01 never beaten"

Verified off-data via `exp_capacity_sweet_spot_v2_cpu_v1/metrics.json`:
- verdict: MEASURED_MECHANISM
- verdict_msg verbatim: "the per-load OPTIMAL sparsity MOVES with load (oracle_opt_moves=True), and the cost mechanism (crosstalk-vs-error-correction balance under cue-noise) is real -- BUT the recall surface is BROAD: a single fixed sparsity ['f0.010'] stays within BEAT of the ORACLE optimum at EVERY load (worst-load gap 0.019), so even a best-possible selector's gain is marginal."
- sel_f_by_load: `{0.1: 0.1, 0.5: 0.05, 1.0: 0.02, 2.0: 0.01}` (selector picks 4 different f-values across the load grid; selector IS adaptive but ORACLE OPTIMUM curve is broad)
- best_fixed=f0.010 worst_gap=0.019 (fixed f=0.01 stays within 0.019 of oracle at every load)
- within_BEAT_of_oracle_everywhere = ['f0.010']
- earns_keep = False

The key intuition: selector IS adaptive (picks different f per load); the ORACLE truth is that the surface is broad enough that a single fixed f=0.010 is always within 0.019 of oracle. The mechanism is real but doesn't earn its keep -- a constant beats the adaptive selector within margin.

### Discrimination regime

For MULTIPLICATIVE_LEVER to chain-grade, we need a regime where the recall surface is NARROWER -- where fixed f=0.01 IS beaten by an adaptive selector. The current cell sweeps `loads = [0.1, 0.5, 1.0, 2.0]` and `F_sweep = [0.1, 0.05, 0.02, 0.01, 0.002]` at N=4096 with flip_cue=0.3. To narrow the surface, candidates are:

1. **Wider load range:** loads `[0.01, 0.1, 1.0, 10.0, 100.0]` -- at extreme loads (0.01 light, 100.0 dense) the broad-recall-surface assumption may break; fixed f=0.01 may not survive both light and dense extremes.
2. **Heterogeneous noise per-task:** vary flip_cue per task ({0.1, 0.3, 0.5, 0.7}); at high noise, error-correction dominates over crosstalk; at low noise, crosstalk dominates. The optimal f shifts substantially; fixed f=0.01 may not survive.
3. **Constraint-coupled tasks:** tasks with shared structure (e.g., tasks at load=0.5 with flip_cue=0.7 AND tasks at load=2.0 with flip_cue=0.1) -- adaptive f selection couples the optimal across tasks.

### Cell spec

**Anchor:** `substrate_capacity_sweet_spot_v3_wide_load_heterogeneous_noise`
**Routing:** `local_cpu_queue`
- **Loads:** `[0.01, 0.1, 0.5, 1.0, 2.0, 10.0, 50.0]` (wider; extreme ends)
- **F_sweep:** `[0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002]` (wider; for the new load extremes)
- **flip_cue grid:** `{0.1, 0.3, 0.5, 0.7}` -- vary noise per task
- **Selector pre-reg:** must beat best_fixed_f by >=0.05 absolute at worst-case (load, flip_cue) operating point
- **Pre-reg bands:**
  - HARD_PASS: adaptive selector beats best_fixed_f by >=0.05 at worst-case operating point AND cv of selector recall across seeds <= 0.07
  - MIDDLE_BAND: selector beats fixed in [0.02, 0.05] OR cv noisy
  - HARD_FAIL: best_fixed_f stays within 0.02 of selector at every (load, flip_cue) operating point (mechanism still doesn't earn keep at wider regime)

### P(chain-grade-confirmed after discriminator)

- **P(adaptive selector beats fixed by >=0.05 at extreme operating points) = 0.30** -- mathematically plausible but cell-author needs to verify the recall surface is genuinely steeper at the corners
- **P(HARD_FAIL recurs: broad surface persists at wide regime) = 0.45** -- the cell's current finding (surface broad) is theoretically founded in superposition-memory math; widening loads may not narrow it
- **P(MIDDLE_BAND partial) = 0.25**

Default expectation: **HARD_FAIL_RECURS**. The MULTIPLICATIVE_LEVER mechanism may be structurally unable to chain-grade at substrate scale because the recall surface is genuinely broad. Honest framing: this MM may stay MM permanently; the lever isn't load-bearing in the regime where substrate operates.

**Composition note:** if this cell HARD_FAILs the chain-grade promotion, the MULTIPLICATIVE_LEVER measured mechanism is still a real bound (oracle-optimal f-curve IS measured, selector recall IS measured) -- the cert is honest. Just not chain-grade. Substrate-product positioning: drop the "adaptive sparsity selector" claim, keep the "fixed f=0.01 is provably within 0.019 of oracle across loads" claim (which is a CHAIN_GRADE robustness result inverted from a HARD_FAIL adaptivity claim).

---

## Item 4 -- Capacity sweet-spot adaptive sparsity

### Same root cause as Item 3

Per USER task brief: "Similar to MULTIPLICATIVE_LEVER: selector likely picks fixed f". Verified by the same cell metrics.json (Item 3 IS this same primitive at a different framing). The selector mechanism IS adaptive in principle; the cell's finding is that the recall surface is broad enough that adaptivity doesn't beat best-fixed.

### Recommendation: compose into ONE cell with Item 3

**Anchor:** same as Item 3 (`substrate_capacity_sweet_spot_v3_wide_load_heterogeneous_noise`) -- the discriminating regime is identical because the underlying mechanism is identical. Both MM items promote together OR both stay MM. No separate cell needed.

### P(chain-grade-confirmed)

Identical to Item 3: 0.30 chain-grade-confirmed; 0.45 HARD_FAIL recurs (likely outcome).

---

## Item 5 -- META-reasoning v3 (today's HARD_PASS at 1.000 perfect)

### Verbatim cell verdict (cell self-tag from v3 NAMED corpus stratified)

> "HARD_PASS_CHAIN_GRADE_META_REASONING: substrate META-reasoning (CHTV-1) generalizes to a NAMED operator corpus stratified across 4 categories with adversarial decoys. ARM_TP_MERGE=1.0000 >= 0.85 cv=0.0000 <= 0.07, ARM_FP_MERGE=0.0000 <= 0.10, ARM_FN_MISS=0.0000 <= 0.20, ARM_BOUNDARY_F1=1.0000 >= 0.80, all 4 categories above per-category floor 0.70."

NOT YET tier-ruled by Skunkworks (landed late 2026-06-25; tier-ruling pending). Per Fix #28 default UNDER-claim and the standing recurring pattern (Skunkworks correctly overrides Director on by-construction-saturation 2026-06-23 MEMORY rule), the **expected Skunkworks tier-rule is MM**, not chain-grade. Reasoning:
- All 4 arms hit 1.000 with cv=0.0; classic Q-discipline saturation pattern
- per_category math/programming/substrate/statistical = 1.0 / 1.0 / 1.0 / 1.0 (all 4 categories saturated)
- The corpus is hand-authored to test CHTV-1's typed-signature equality rule; achieving 1.000 is the rule applied perfectly to its designed corpus, NOT novel discovery
- Same anti-pattern as g1 generation cell (USER 2026-06-22 explicitly endorsed Skunkworks-overrides-Director on by-construction-saturation)

### Discrimination regime

Per `research_distill_verify_META_reasoning_multi_drill_2026-06-25.md` (today's META drill), the substrate-self-discovered NAMED corpus is the discrimination regime. Drill findings:
- 177360 atoms in Store; only 62 atoms have >=3 typed-signature fields populated
- 47 unique typed-signatures across those 62 atoms
- ZERO typed-signatures shared across DIFFERENT names (immediate self-bootstrap pool empty)
- 20 duplicate-name groups (v2's corpus -- but only 1 NAMED operator in entire set)
- 93 capability-shared cross-name groups -- the workable pool for SHARED_ABSTRACTION / THEOREM_LINKED / CROSS_DOMAIN_ABSTRACTION cell-B triage

The discrimination regime is **substrate-self-discovered corpus where CHTV-1 cannot trivially pre-resolve all pairs because the corpus contains substrate-internal name conflicts that the verifier might miss-classify**. The hand-authored corpus is too clean; substrate's actual algebra_dict authoring has gaps, drift, and capability-sharing patterns that the verifier was not pre-tuned for.

### Cell spec

**Anchor:** `substrate_distill_verify_v4_substrate_self_discovered_corpus`
**Routing:** `local_cpu_queue` (CHTV-1 is microsecond-scale per pair; 100+ groups x 3 seeds = total runtime ~10s)
**Corpus engineering pre-flight (BEFORE cell dispatch):**
- Author tool: `tools/substrate_self_corpus_extract.py` that:
  - Scans `data/substrate_index/*/atoms.jsonl` for cross-name capability-shared groups
  - For each of the 93 cap-shared groups, extract algebra_dict per member
  - Author ground-truth labels per group: MERGEABLE / SHARED_ABSTRACTION / THEOREM_LINKED / CROSS_DOMAIN_ABSTRACTION / INVERSE_PAIR / DISTINCT (requires light human/Director review; ~93 groups x 2min = 3h calendar)
  - Output: `data/meta_reasoning_corpus/substrate_self_discovered_v1.json` with `{group_id, names[], algebra_dicts[], capabilities[], ground_truth_relationship}` schema

**Cell pre-reg bands:**
- **HARD_PASS:** ARM_TP_MERGE >= 0.85 cv <= 0.10 + ARM_FP_MERGE <= 0.10 + ARM_FN_MISS <= 0.20 + per-relationship-class F1 >= 0.70 + at least 3 distinct ground-truth relationship-classes represented in held-out fold
- **MIDDLE_BAND:** ARM_TP_MERGE 0.60-0.85 OR ARM_FP_MERGE 0.10-0.25 OR per-class F1 missing on 1-2 classes
- **HARD_FAIL:** ARM_TP_MERGE < 0.60 OR ARM_FP_MERGE > 0.25 (verifier doesn't generalize to substrate-self-discovered corpus)
- **Q-discipline guard:** if all arms hit >=0.995, BIAS-Q fires; corpus regime didn't have enough hardness (this would be the "v4 still saturates" outcome -- escalate corpus difficulty further)

### P(chain-grade-confirmed after discriminator)

- **P(generalizes to substrate-self-discovered corpus at >=0.85) = 0.55** -- CHTV-1 mechanism is sound per v3-overmerge controls; corpus is harder than v3 NAMED but rule is the same
- **P(MIDDLE_BAND; some categories saturate, others noisy) = 0.30** -- the 93 cap-shared groups are heterogeneous; some classes may be too sparse for cv-rail
- **P(HARD_FAIL; corpus exposes a soundness gap in CHTV-1) = 0.10** -- mechanism has been carefully designed; soundness gap would be surprising
- **P(still saturates at 1.000 -- corpus not hard enough) = 0.05** -- requires v5 with even harder construction

Default expectation: **chain-grade-candidate** with high probability (0.55) of full chain-grade-confirmed on substrate-self-discovered corpus. Honest UNDER-claim: this v4 cell promotes META-reasoning v3 from "MM expected" to "chain-grade-confirmed eligible" with the corpus engineering complete.

**Strategic significance:** META-reasoning chain-grade-confirmed unlocks Stage 4 self-improvement scaffold per the USER strategic-vision memory atom. The 4 downstream capabilities (self-test / self-correct / self-discover / self-optimize) become substrate-deployable; substrate becomes self-aware about its own equivalence claims.

---

## Item 6 -- Permutation-indexed binding (Cell 4 today)

### USER task brief notes

> "Chain-grade on multi-occurrence subset; general composition untested. Cell needed: general HRR query that uses permutation-indexed binding in a non-multi-occurrence context. Already covered in DRILL 1's scope."

Per Skunkworks 4cell ruling 2026-06-25 Cell 4, this primitive landed chain-grade today (substrate basis HRR-tier extends by 1 chain-grade primitive). Per USER brief, the chain-grade extension to general HRR queries is DRILL 1 scope. This drill defers to DRILL 1 to avoid scope duplication.

**Cross-reference:** DRILL 1 will cover the "general HRR query that uses permutation-indexed binding in a non-multi-occurrence context" cell spec. No action in this drill.

---

## Prioritized dispatch order

| Priority | Item | Cell anchor | Status | Routing | Wall |
|---|---|---|---|---|---|
| **URGENT 1** | Anisotropy fly-LSH M=100k | `substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1` | **DISPATCHED 2026-06-25 (in-flight)** | overnight_queue (GPU) | 9000s budget |
| **URGENT 2** | Anisotropy v2 if v1 OOMs | `substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched_matmul` | NEEDS AUTHORING (contingent on v1 OOM) | overnight_queue (GPU) | 9000s budget |
| **HIGH 1** | Multi-bank WM K-extension adversarial | `substrate_working_memory_multi_bank_routing_K_extension_v2_adversarial` | NEEDS AUTHORING | local_cpu_queue (CPU) | ~5min |
| **HIGH 2** | META-reasoning v4 substrate-self corpus | `substrate_distill_verify_v4_substrate_self_discovered_corpus` (pre-flight: `tools/substrate_self_corpus_extract.py`) | NEEDS AUTHORING (corpus engineering blocks cell) | local_cpu_queue (CPU) | ~10s cell; ~3h pre-flight curation |
| **LOW 1** | Capacity sweet-spot v3 wide regime | `substrate_capacity_sweet_spot_v3_wide_load_heterogeneous_noise` | NEEDS AUTHORING (likely HARD_FAIL_RECURS) | local_cpu_queue (CPU) | ~10min |
| **DEFERRED** | Permutation-binding general HRR | (DRILL 1 scope) | DRILL 1 owns | DRILL 1 | DRILL 1 |

### Sequencing recommendation

**Cycle N (this cycle):** ship this drill deliverable. Spawn budget: ZERO additional. Item 1 already in flight; wait for landing.

**Cycle N+1:** (a) if anisotropy v1 lands -> Skunkworks tier-rule cycle; (b) if anisotropy v1 OOMs -> Item 2 cell-author spawn; (c) regardless: dispatch Item 3 (multi-bank WM adversarial) via exp_dev (cheap, CPU, ~5min wall).

**Cycle N+2:** (a) anisotropy follow-up tier-ruling; (b) META-reasoning v4 corpus-engineering spawn (skunkworks or exp_dev for the corpus extraction tool); (c) optionally Item 5 (capacity sweet-spot v3) -- but flag the high-probability HARD_FAIL_RECURS in pre-reg.

**Cycle N+3:** META v4 cell-author + dispatch; tier-rule landing.

### Spawn budget for this drill's recommendations

- **0 spawns required this cycle** (Item 1 in flight; Item 2 contingent)
- **2 spawns Cycle N+1** (Item 2 cell-author IF anisotropy OOM; Item 3 cell-author)
- **2 spawns Cycle N+2** (META v4 corpus extraction; Item 5 cell-author)
- **1 spawn Cycle N+3** (META v4 cell-author)

Total: 5 spawn-events across 4 cycles, well under Fix #14 ceiling of 3-in-flight at any time.

---

## Flag: URGENT items requiring immediate attention

1. **Anisotropy v1 in-flight on overnight_queue** -- monitor for landing or OOM completion; budget allows 2.5h. If OOM, immediately dispatch Item 2 (batched matmul refactor) -- the engineering fix is well-specified.

2. **USER task brief preliminary numbers (B_fly=0.189, B_char=0.193, AB_CONTROL=0.240, RAW=0.021) are NOT verified off-data this cycle.** Under Fix #28 default UNDER-claim, I am not propagating those as chain-grade evidence. The dispatched v1 cell will land authoritative numbers; if USER's preliminary holds, the outcome is `HARD_FAIL_CONTROL_ALSO_PASSES` which is itself a chain-grade negative-result (refutes v2's LSH attribution; demands new research question).

---

## Cross-drill coordination with DRILL 1

DRILL 1 covers: chain-grade-with-envelope-untested items at EXTENSION (sequence_memory at long sequences, kg_traversal at higher edge densities, permutation-binding at general HRR queries, etc.).

DRILL 2 (this drill) covers: MM items needing DISCRIMINATION REGIME to promote (anisotropy LSH, multi-bank WM, MULTIPLICATIVE_LEVER, capacity sweet-spot, META-reasoning).

No scope overlap: DRILL 1 extends working chain-grade mechanisms to new regimes; DRILL 2 discriminates which mechanism is load-bearing among saturating MM arms. Permutation-binding general HRR query is the one item that touches both drills; per USER task brief, DRILL 1 owns it.

---

## Disciplines honored

- **Verify-OFF-DATA**: read metrics.json directly for v2 calibrated meter, multi-bank WM, capacity sweet-spot v2, META v3 (NOT verdict_msg framing)
- **Fix #28 default UNDER-claim**: flagged USER task brief preliminary numbers (B_fly=0.189 etc.) as NOT VERIFIED off-data this cycle; expected Skunkworks ruling on META v3 = MM not chain-grade despite cell self-tag HARD_PASS
- **By-construction-saturation tiering**: applied to META v3 (4/4 arms at 1.000 cv=0.0) and multi-bank WM (4/4 multi-arms at 1.000)
- **Symmetric anti-negativity**: I did not inflate USER's preliminary AB_CONTROL=0.240 into a falsified-LSH narrative; I marked it as needs-landing-to-verify. I did not deflate META v3 1.000 into a fraud claim; it's by-construction-saturation expected pattern
- **Cap-dev is goal; cert-grade is instrument**: deliverable IS a capability-development sequencing plan (5 cells across 4 cycles with spawn-budget honesty), not a chain-grade chase
- **Verify-the-referent**: checked that anisotropy M=100k cell does NOT yet exist on disk; checked DISPATCHED note for cell-author confirmation; checked META v3 corpus existence at `data/meta_reasoning_corpus/`
- **Generic terms only / 2x research drill / lit-scan calibration penalty**: no external web searches this cycle (substrate-internal drill); calibration penalty N/A
- **ASCII only**; no emojis

---

-- research (Director; DRILL 2 of 2 MM-tier promotion paths; 2026-06-25)
