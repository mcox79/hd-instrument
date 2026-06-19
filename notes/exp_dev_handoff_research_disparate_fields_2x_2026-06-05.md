# exp_dev hand-off -- research: disparate-fields-2x

**Filed-by:** research sub-agent (Sonnet), 2026-06-05
**Trigger:** notes/research_drill_disparate_fields_substrate_capability_plus_process_2x_2026-06-05.md
**Per [[feedback-no-experiment-design-in-prompts]]:** This file hands off anchor CANDIDATES with pointers. Exp_dev designs all sweep grids, thresholds, and pre-reg bands autonomously.

---

## Pause state

Check data/orchestrator_paused.flag before dispatching. If paused, queue this handoff for next resume.

---

## Anchor candidates (rank-ordered by P_deflated x implementation cost)

### TIER-1 (run first -- cheap, high P)

**1. Overlap histogram P(q) for VQ codebook**
- Anchor pointer: compute empirical Parisi overlap distribution for current VQ codebook at 3 load levels
- Substrate-product reading: directly measures whether cavity-method RSB-separation mechanism applies to our codebook; if bimodal P(q) confirmed, opens the cavity-method capacity formula drill
- Tier hint: CPU smoke, ~2 hr wall
- Why-now: Unlocks the cavity-method capacity formula (highest-ranked capability drill). No code changes to substrate required -- pure analysis of existing W matrices. P_deflated = 0.45.

**2. Physarum-weighted retrieval**
- Anchor pointer: implement frequency-preconditioned threshold dynamics; compare basin size vs unweighted at multiple noise levels
- Substrate-product reading: a 3+ percentage point gain at 20% noise level is a direct retrieval quality improvement requiring zero W changes
- Tier hint: CPU smoke, ~30 min wall per noise level
- Why-now: Lowest implementation cost (20 lines); algebraically clean from Physarum flow analogy. P_deflated = 0.42.

### TIER-2 (next batch)

**3. Wright-Fisher lifespan validation**
- Anchor pointer: compute energy gap s_p for each pattern in current 14-anchor suite; apply Kimura formula T_survival ~ N_eff * f(s_p); compare predicted vs observed degradation onset in existing anchor results
- Substrate-product reading: if formula matches within 2x, gives a per-pattern write-cycle durability guarantee for product spec
- Tier hint: theory + CPU, ~1 day
- Why-now: Directly addresses Cap 2 (continual writing) cap_map uncertainty. Needs no new experiments -- validates against EXISTING anchor data. P_deflated = 0.40.

**4. Immune somatic-variant cloud encoding**
- Anchor pointer: for a single high-value concept, write parent + 3 variants (Hamming distance 5-10% of N); measure basin radius vs capacity overhead vs standard single-pattern write
- Substrate-product reading: if basin radius increases with sub-linear capacity cost (rho > 0.8), enables a robustness mode for high-value concept slots
- Tier hint: CPU smoke, ~1 hr wall
- Why-now: Directly applicable to the HP-12 V1 demo use case (high-value concept retrieval). P_deflated = 0.42.

**5. Spectral entropy write-gate**
- Anchor pointer: add spectral entropy monitoring to write pipeline; plot spectral entropy vs M (patterns stored); identify where entropy approaches N*ln2 saturation threshold
- Substrate-product reading: if spectral entropy is a leading indicator of retrieval degradation (rises before quality drops), enables a principled write-gate for the product's live system
- Tier hint: CPU, ~2 hr wall
- Why-now: Enables proactive capacity management without empirical saturation testing. P_deflated = 0.40.

### TIER-3 (after Tier-1/2 results)

**6. LDPC-irregular Hebbian weighting**
- Anchor pointer: test non-uniform write strengths (higher weight for concepts with lower inter-pattern correlation in VQ codebook) vs uniform Hebbian
- Substrate-product reading: capacity improvement from irregular weighting analogous to irregular LDPC code gain over regular LDPC
- Why-now: Requires Tier-1 P(q) results to calibrate weighting. P_deflated = 0.44.

**7. Boolean GRN effective-rank computation**
- Anchor pointer: compute rank of W restricted to each stored pattern's local neighborhood (Hessian eigenvalues at attractor); correlate with retrieval robustness
- Why-now: Provides a per-pattern fragility metric; useful for codebook quality scoring. P_deflated = 0.38.

---

## Process improvements (non-anchor, for orchestrator / exp_dev workflow)

1. **Futility stopping rule**: add conditional-power check after first 30% of sweep in queue_runner. 1 day implementation. ~15-25% compute savings.
2. **Systematic uncertainty budget fields**: add syst/stat error decomposition to anchor spec template. 2-3 days.
3. **Substrate FMEA table**: 3-4 hr write. Identifies top failure modes for next anchor batch planning.
4. **Property-based test suite**: 5 algebraic retrieval properties as pytest. 1-2 days.
5. **Red-team exercise before new capability claims**: 30 min per hypothesis, no code.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_disparate_fields_substrate_capability_plus_process_2x_2026-06-05.md
- Field advisor output: d:/AI/hd-instrument/tools/orchestrator/research_field_advisor.py
- Cap_map: d:/AI/hd-instrument/data/cap_map.md (Cap 2 continual write, Cap 3 capacity -- primary targets)
- Prior spin-glass drills: check notes/research_meta_map_and_adjacencies_*.md for existing RSB coverage

---

## Contract section

Exp_dev OWNS: anchor naming, sweep grid, seed counts, pre-reg HP/MID/HF bands, queue choice, estimated wall time, format of metrics.json output.

Exp_dev MUST NOT: re-read this file as a design spec for numerical thresholds -- the P_deflated values are research calibration estimates, not pre-reg bands. Design pre-reg bands from first principles per envelope-fail-bands protocol.

## Autonomy declaration

Exp_dev has full autonomy over implementation details, sweep parameters, and queue routing for all Tier-1 and Tier-2 candidates above. Tier-3 candidates require Tier-1/2 results as inputs; do not dispatch until prerequisite results are in.
