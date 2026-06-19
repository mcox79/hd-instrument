# exp_dev hand-off -- research: extraction-gate concept-coverage rescue

Filed-by: research sub-agent (2026-06-06)
Trigger: research drill notes/research_drill_extraction_gate_concept_coverage_rescue_2x_2026-06-06.md
Pause state: CHECK data/orchestrator_paused.flag before dispatching any anchor.

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and
explains WHY they are ready for empirical test. It does NOT specify sweep grids, threshold
formulas, numerical bounds, queue choices, or pre-committed cap_map decisions. exp_dev
designs the experiment autonomously after reading context pointers.

CRITICAL CONTEXT: This hand-off REFUTES the prior sparse-extraction-entropy-gated hand-off
(notes/exp_dev_handoff_research_sparse_extraction_entropy_gated_2026-06-05.md). The Rank 1
anchor there (embedding-norm discriminability) is now known to be structurally broken by the
Goldilocks zone norm-frequency relationship. Do NOT ship norm-gate or entropy-gate anchors
expecting coverage preservation. Replace with per-cluster stratified keep (see below).

---

## ANCHOR CANDIDATES (rank-ordered)

### Rank 1: Random-gate vs norm-gate vs entropy-gate VQ coverage comparison at g=0.30
Anchor pointer: validates the Goldilocks zone refutation -- confirms that random sampling
  at g=0.30 produces materially better VQ coverage than norm-gate or entropy-gate at the
  same gating ratio.
Substrate-product reading: if random gate produces >90% coverage while norm/entropy gates
  produce <65% (per empirical finding), this closes the norm-gate approach and directly
  motivates the per-cluster stratified keep architecture. This is the cheapest validation
  of the Goldilocks zone structural argument.
Tier hint: Tier 1 (CPU only; synthetic corpus ~10k tokens; no GPU required; <5 min wall).
Why-now: the Goldilocks zone algebraic analysis is strong but has not been verified on an
  actual VQ pipeline with the target substrate codebook. This cell is the decisive test
  before replacing the extraction architecture.

### Rank 2: Per-cluster stratified keep at K={1,10,100} -- coverage and speedup
Anchor pointer: validates the 100% coverage guarantee and speedup at multiple K values.
  Per-cluster K=1 should give 100% coverage at maximum speedup; K=10 gives 100% coverage
  at ~100x speedup for typical corpus sizes.
Substrate-product reading: if HARD PASS (100% coverage at K>=1), the per-cluster architecture
  is immediately production-ready. Speedup is tunable by K. This replaces all norm/entropy
  gating approaches.
Tier hint: Tier 1 (CPU; same 10k token corpus; VQ pre-pass via k-means; <10 min wall).
Why-now: coverage guarantee is algebraically proven but depends on the VQ pre-pass being
  faithful. Cell B tests whether the actual VQ assignment pipeline (k-means codebook on
  real embeddings) satisfies the coverage guarantee in practice.

### Rank 3: Hybrid per-cluster top-K by entropy -- within-cluster variance capture
Anchor pointer: validates whether entropy-based ranking WITHIN each VQ cluster gives better
  information representation than random within-cluster selection.
Substrate-product reading: if within-cluster entropy selection captures >20% more variance
  than random selection, the hybrid architecture (coverage from stratification + quality
  from entropy) is worth the 3-5% first-layer-pass overhead.
Tier hint: Tier 2 (CPU; requires first-layer activation computation; ~30 min wall).
Why-now: this is the "best of both worlds" target architecture. Rank 1 and 2 must pass first
  to establish that per-cluster stratification solves coverage; Rank 3 adds the quality
  improvement layer.

---

## CONTEXT POINTERS

- Research note: notes/research_drill_extraction_gate_concept_coverage_rescue_2x_2026-06-06.md
- Prior refuted drill: notes/research_drill_sparse_activation_extraction_entropy_gated_2x_2026-06-05.md
- Prior refuted hand-off: notes/exp_dev_handoff_research_sparse_extraction_entropy_gated_2026-06-05.md
- Goldilocks norm structure: arXiv:2501.15754, arXiv:2603.26663, arXiv:2409.11253
- Coverage-centric coreset selection (mathematical backing): arXiv:2210.15809 (ICLR 2024)

---

## CONTRACT

exp_dev designs experiment anchors after reading the research note at the context pointer
above. The research note specifies Cell A/B/C protocols, HP/MID/HF thresholds, and
P_deflated estimates. exp_dev uses these as inputs to anchor design, NOT as constraints.

## AUTONOMY DECLARATION

exp_dev selects anchor names, sweep grids, timeout formulas, queue assignment, and pre-reg
bands independently. The research note's Cell A/B/C descriptions are hypothesis framing,
not implementation specs.
