# Hidden Phase-Diagram Dimensions — Research Drill 2026-07-01

**Filed:** 2026-07-01 pre-compaction
**Trigger:** USER — "make sure we're not missing any hidden dimensions of the phase diagram"

## Top-3 Load-Bearing Hidden Dimensions

### 1. Dim H — Distributional-shape (power-law vs uniform)
- **P_deflated: 0.38 HARD-PASS**
- **Highest-probability overlooked failure mode**
- Real workloads have Zipfian frequency (power-law); substrate tested only on uniform distributions
- Failure mode: high-frequency items may saturate; long-tail items may crumble
- **Testable:** synthesize Zipfian entity distributions at various α exponents; measure recall
- Adjacent: compressed sensing L1-recovery phase transitions (Donoho-Tanner curves)

### 2. Dim I — Hierarchical-nesting-depth
- **P_deflated: 0.42**
- **Gates all Stage 3 cortex cell design**
- Nested bindings `bind(bind(a,b), bind(c,d))` — capacity as function of nesting level
- Current tests are flat compositions; real language/reasoning is nested
- **Cheapest decisive test** — 45 min CPU
- If nesting depth degrades sub-linearly → deep composition viable
- If super-linear degradation → substrate needs multi-substrate composition

### 3. Dim S — Metric-dependence
- **P_deflated: 0.45**
- Top-1 recall vs top-K recall vs semantic-similarity vs downstream-task-quality
- Different metrics may reveal different capacity boundaries
- **Impact on M3:** conversational quality is not top-1; is semantic-similarity
- May reveal higher effective capacity than top-1 assumes

## Also Identified (Lower-Priority)

- Dim A: Temporal dynamics / forgetting timescales
- Dim C: Retrieval latency percentiles vs accuracy (not just accuracy)
- Dim E: Adversarial robustness (key collision attacks)
- Dim F: Batch throughput scaling
- Dim H (bis): Warm-start vs cold-start (path dependence)
- Dim J: Continuous vs discrete regime
- Dim L: Random-init vs learned encoding
- Dim P: 4/5/6-cortex-primitive compositions
- Dim R: Failure mode taxonomy (silent/loud/hallucination/refuse)
- Dim T: Regime-shift transitions

## Recommended Sequencing

**Before Stage 2 (Stage 1 completion):**
1. Dim I nesting-depth cell (~45 min CPU) — gates Stage 3
2. Dim H distributional-shape cell (~1-2 hr CPU) — highest failure risk

**Early Stage 2:**
3. Dim S metric-dependence sweep (multiple metrics on same landing)
4. Dim L learned encoding baseline

## Follow-up Research Drill Candidate

**Sparse-coding / compressed-sensing** — directly maps Dim H distributional-shape failure to L1-recovery phase transitions. Field drill_count=0. Trigger-B scope-expansion.

## Cross-references

- Prior BACKUP: `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-01_LATE.md`
- Correlated-key research: `notes/research_correlated_key_capacity_hopfield_fhrr_2026-07-01.md`
- Atom 22 LLN CG (Wave 21 commercial extension)
- Cell D v2 CG (Atom 1)
