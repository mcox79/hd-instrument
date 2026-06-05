# exp_dev hand-off -- research: cross-domain interference and capacity degradation 2x

**Filed:** 2026-06-04 by research sub-agent.

**Trigger:** 2x depth drill on cross-domain interference and capacity degradation completed.
Findings yield 3 concrete empirical anchors with CPU-scale cheap decisive tests and direct
cap-map implications for Cap-Hebb (write capacity), Cap-Audit (deletion cert), and
Cap-Retrieval (graceful degradation monitoring).

**Pause state:** check `data/orchestrator_paused.flag` before dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only.
exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C),
anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

**Research note:** `notes/research_drill_cross_domain_interference_capacity_degradation_2x_2026-06-04.md`

---

## Summary of actionable findings

1. The AGS degradation curve has TWO operative regimes: GRACEFUL (below ~85% of alpha_c, retrieval
   accuracy > 95%, error follows erf profile) and CATASTROPHIC (at alpha_c = 0.138, first-order-like
   drop in overlap m with simultaneous spin-glass onset). The 85% safety threshold is testable and
   should become a substrate operational constant.

2. Orthogonal domain keys suppress cross-domain crosstalk to effectively zero, allowing each domain
   to independently approach alpha_c. For N_domains orthogonal domains, total capacity =
   N_domains * alpha_c * N (vs single-substrate alpha_c * N). Algebraically plausible but untested.

3. D-ECR (Domain-Aware + Energy-Contribution-Ranked) eviction policy maintains graceful operation
   indefinitely by preemptively evicting lowest-energy-contribution patterns from over-represented
   domains, generating deletion certificates per eviction. This is the audit-preserving eviction
   primitive the product needs.

4. MCT critical slowing down: argmax convergence step count diverges as a power law near alpha_c.
   This is a FREE early-warning signal -- no external oracle required. Substrate self-reports
   approaching capacity via slowing convergence.

---

## Anchor candidates (rank-ordered; exp_dev picks per queue policy)

### 1. Alpha ramp: graceful-to-catastrophic capacity curve tracing

- Anchor pointer: `notes/research_drill_cross_domain_interference_capacity_degradation_2x_2026-06-04.md`
  Sections: SUB-QUESTION (1) Degradation Curve Shape + Cheap Decisive Test + HP1/HP2/HP5 thresholds
- Substrate-product reading: Validates that the safe operational zone (M < 85% of alpha_c * N) is
  empirically confirmed, and that the catastrophic transition at alpha_c is observable. This
  establishes the M_eviction_trigger constant that ships with the product.
  Also tests HP5: does argmax step count diverge near alpha_c (MCT critical slowing down)?
  If yes: convergence monitoring is a FREE capacity early-warning signal.
- Tier hint: CPU local (pure numpy; N=4096, sweep M from 0 to 1.2 * alpha_c * N; < 5 min wall)
- Why now: cheapest possible test of the core operational safety parameter; no GPU needed

### 2. ECR vs LRU eviction comparison at M = 0.90 * alpha_c * N

- Anchor pointer: `notes/research_drill_cross_domain_interference_capacity_degradation_2x_2026-06-04.md`
  Section: SUB-QUESTION (3) Graceful Eviction Policies + HP3 threshold + D-ECR algorithm
- Substrate-product reading: If D-ECR maintains > 95% retrieval accuracy while LRU degrades to
  < 90% at 90% capacity, this validates the audit-preserving eviction primitive that enables
  "indefinite auditable operation past single-substrate limit." Core product differentiator.
- Tier hint: CPU local or remote CPU (N=4096; 1000 sequential writes with eviction; < 10 min)
- Why now: closes the open eviction policy question; algebraic argument is strong but empirical
  comparison to LRU needed for product claim

### 3. Orthogonal vs random domain keys capacity comparison at N_domains = 20

- Anchor pointer: `notes/research_drill_cross_domain_interference_capacity_degradation_2x_2026-06-04.md`
  Section: SUB-QUESTION (2) Per-Domain Interference + HP4 threshold
- Substrate-product reading: If orthogonal keys achieve < 2% per-domain error at total loading
  where random keys fail (> 15%), this empirically validates the hierarchical capacity
  multiplication mechanism. Directly enables "train 100 specialists, aggregate via substrate"
  narrative with concrete performance number.
- Tier hint: CPU local (N_domains=20, N=4096, K_d per domain = alpha_c * N / N_domains; < 10 min)
- Why now: the orthogonal-key mechanism is the single most important architectural choice
  for hierarchical substrate design; testable cheaply; HP4 is falsifiable and specific

---

## Context pointers (file paths only)

- Research note: `d:/AI/hd-instrument/notes/research_drill_cross_domain_interference_capacity_degradation_2x_2026-06-04.md`
- Prior hierarchical drill: `d:/AI/hd-instrument/notes/research_drill_training_speed_hierarchical_architecture_2x_2026-06-04.md`
- Capability map: `d:/AI/hd-instrument/notes/substrate_capability_map.md`
- Meta-map adjacencies: `d:/AI/hd-instrument/notes/research_meta_map_and_adjacencies_2026-05-23.md`
- AGS 1985 PDF (retrieved during drill): https://gwern.net/doc/ai/nn/1985-amit.pdf
- HAM paper: arXiv:2107.06446
- Modern Hopfield synaptic noise: arXiv:2503.00241
- Redundancy maximization: arXiv:2511.02584

---

## Contract

exp_dev MUST:
- Pre-register HARD-PASS / HARD-FAIL / MID-BAND thresholds from the HP1-HP5 section of the
  research note BEFORE coding any anchor
- Use per-anchor `--timeout` (formula: 1.5 * smoke_wall * (FULL_N/smoke_N)^exp * seeds_ratio)
- ASCII-only in print() / verdict_msg (Windows cp1252 runner constraint)
- Emit per-cell stdout progress lines AND write per-cell partial JSON for restartability

exp_dev MUST NOT:
- Design the experiment sweep grid (that is exp_dev's autonomous choice)
- Pre-commit to specific alpha values, N values, or seed counts beyond what's needed for
  smoke vs full distinction
- Interpret verdicts (orchestrator / verdict_handler owns that)

## Autonomy declaration

exp_dev has full autonomy on: anchor naming, sweep parameters, queue routing (CPU vs GPU),
smoke ETA, FULL profile design, pre-reg band widths (within the HP framework from research note),
and whether to run anchors 1/2/3 sequentially or batch.
