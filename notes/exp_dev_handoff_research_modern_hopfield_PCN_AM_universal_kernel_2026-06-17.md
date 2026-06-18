# exp_dev hand-off - research: Modern Hopfield + PCN-as-AM + Universal Hopfield kernel 2x

Filed-by: research (Opus, 2026-06-17 evening)
Trigger: USER strategic request — 2x deep drill on Modern-Hopfield + PCN-as-AM variants for tomorrow's better-designed recapture experiments after tonight's substrate-proven ARCH-B nonlinear-readout lever
Source research note: notes/research_modern_hopfield_PCN_AM_universal_kernel_2x_2026-06-17.md
Pause state: check data/orchestrator_paused.flag at pickup; honor if present

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names anchor candidates with
substrate-product readings and tier hints; it does NOT prescribe pre-reg envelopes or
specific cell configs. exp_dev owns experiment design.

## Anchor candidates (rank-ordered)

### Anchor 1 (highest leverage; substrate-novel literature blind-spot) - PCN-AM compositional-recombination on structured HD codes
- **Pointer**: 3-layer hierarchical PCN trained on stored bind(role_i, filler_i) for i=1..M; query with NOVEL bind(role_j, filler_k) where (j,k) NOT in stored set but j,k individually present; readout = relaxed sensory-layer values; cosine to true bind(role_j, filler_k) target as metric. Baseline: softmax-MHN on same stored matrix, same query.
- **Substrate-product reading**: First empirical evidence that iterative PCN-AM readout recombines stored compositional codes — would open ARCH-C cap_map row (softmax-storage + PCN-AM-readout fork from ARCH-B). HARD-PASS PRED-1: PCN-AM cosine >= 0.55 AND softmax-MHN cosine <= 0.30 at M=200. HARD-FAIL: both readouts < 0.30 -> structured HD codes resist compositional generalization via any nonlinear readout, structural closure of this rescue route.
- **Tier hint**: T2/T3 boundary - zero PCN-AM-on-VSA published precedent; substrate is uniquely positioned to fill the gap.
- **Why-now**: USER explicitly identified ARCH-B nonlinear-readout as biggest proven lever tonight; this anchor extends to the MOST DIFFERENT nonlinear-readout class (iterative vs single-shot) on a regime where substrate already demonstrated capacity (structured codebooks). Cheap CPU-only ~30-60 min.

### Anchor 2 (lit-precedent strong; cheap entropy-knob sweep) - HFYN entropy-parametrized separation sweep on substrate codebook
- **Pointer**: Hopfield-Fenchel-Young Networks (Santos 2024, arXiv 2411.08590) parametrize ALL separation functions as argmin of a Fenchel-Young loss with entropy choice; Shannon -> softmax, Tsallis(alpha=2) -> sparsemax, alpha=1.5 -> intermediate. Sweep alpha across {1.0, 1.25, 1.5, 1.75, 2.0} on substrate codebook recall at iso-budget. Optionally combine with Anchor 4 (similarity-axis sweep).
- **Substrate-product reading**: HFYN gives the substrate a single continuous configuration knob spanning softmax-Hopfield to sparse-entmax-Hopfield. HARD-PASS PRED-3: alpha=1.5 gives >= 0.03 recall improvement over either endpoint (softmax / sparsemax). HARD-FAIL: alpha-sweep flat within 0.02 -> separation choice degenerate on structured HD codes (substrate-novel finding).
- **Tier hint**: T2 - direct lit precedent (HFYN paper); substrate operationalization is the only novelty.
- **Why-now**: substrate already demonstrated softmax (ARCH-B) and entmax (C1) endpoints work; HFYN says there is a continuous family between them; cheapest possible sweep to characterize the full family.

### Anchor 3 (Drosophila recapture alternative path) - PCN-AM vs sparse-key-dense-value head-to-head on the Drosophila MIDDLE_BAND probe
- **Pointer**: Use the Drosophila-style sparse pattern-capacity probe that gave MIDDLE_BAND tonight; substitute PCN-AM iterative readout in place of the (already proposed in prior research note) sparse-key dense-value fork. Compare three readouts on identical probe: (a) linear baseline, (b) sparse-key dense-value [predecessor research recommendation], (c) PCN-AM 3-layer hierarchical.
- **Substrate-product reading**: Both sparse-key-dense-value and PCN-AM are "supra-linear selection step" mechanisms per the Drosophila lit-scan finding. This anchor tests whether the iterative path (PCN-AM) recaptures the Drosophila gain that the linear-readout substrate failed to capture — alternative to the sparse-key-dense-value recapture path already filed in exp_dev_handoff_research_drosophila_MB_sparse_recapture_2026-06-17.md.
- **Tier hint**: T3 - novel composition of PCN-AM with VSA Drosophila probe; no lit precedent.
- **Why-now**: Drosophila was filed today; if Anchor 1 PCN-AM-on-structured-codes succeeds, this anchor extends the win to Drosophila recapture for free.

### Anchor 4 (one-line config change; lit-precedent direct) - UHN similarity-axis swap: Euclidean / Manhattan vs dot-product
- **Pointer**: Per Millidge 2022 Universal Hopfield: similarity = Euclidean or Manhattan distance with softmax separation outperforms dot-product + softmax on retrieval robustness AND capacity. Swap similarity kernel on substrate ARCH-B (or wherever softmax readout already runs); keep all else identical.
- **Substrate-product reading**: HARD-PASS PRED-2: Euclidean-similarity gives >= 0.05 recall lift over dot-product at iso-budget. HARD-FAIL: < 0.02 lift -> UHN empirical claim does not transfer to structured HD codes (worth recording).
- **Tier hint**: T2 - direct lit precedent; substrate operationalization is a one-line config swap.
- **Why-now**: cheapest possible test in the kernel taxonomy; can run alongside Anchor 2 entropy sweep with no extra infrastructure.

## Anchor priority recommendation

If exp_dev queue has room for 1-2 cells: **Anchor 1 + Anchor 4** (PCN-AM novel-recomb + UHN similarity swap). These cover the two most-different drill axes (iterative-inference + similarity-kernel) and together discriminate ALL three HARD-FAIL signals.

If room for 3-4: add Anchor 2 (HFYN entropy sweep) and Anchor 3 (Drosophila PCN-AM substitution).

## Context pointers (file paths, not summaries)

- Source research note: notes/research_modern_hopfield_PCN_AM_universal_kernel_2x_2026-06-17.md
- Predecessor (frontier): notes/research_nonlinear_readout_frontier_2026-06-17.md
- Cross-thread (Hopfield capacity): notes/research_modern_hopfield_capacity_retrieval_crossover_2026-06-16.md
- Cross-thread (Drosophila MB recapture; sister hand-off): notes/exp_dev_handoff_research_drosophila_MB_sparse_recapture_2026-06-17.md
- USER architectural directive (research as T2/T3 hypothesis layer, not proven core): MEMORY index entry feedback_research_can_be_wrong_only_proven_fully_believed_trust_tier_USER_2026-06-17
- USER compute policy (this hand-off is laptop-CPU-cheap; super-fast not heavy): MEMORY index entry feedback_compute_remote_for_heavy_laptop_for_superfast_C0_cost_underestimate_USER_2026-06-16

## Contract

exp_dev owns:
- pre-registration envelopes (HARD-PASS / HARD-FAIL bands)
- smoke-gate decision
- cell-config and shipping via queue_add.sh (pause-flag gated)
- post-ship REMOTE VERIFY per remote-coverage discipline (corpus-completeness rule)
- self-test per formula-selftests
- atomization to cert-grade EXPERIMENT_RECORD on PASS

research owns:
- T2/T3 claim onboarding via research-finding atoms (the 9 distilled claims in the source note)
- field-advisor update if a new adjacency edge opens
- no experiment design beyond the anchor pointers above

## Autonomy declaration

This hand-off is filed at research-Opus discretion under Trigger E (USER-initiated drill).
exp_dev may pick this up on next emergency-refill cycle or USER-directed pickup; no
mechanical dispatch from research. Per [[feedback-no-experiment-design-in-prompts]], exp_dev
retains full design autonomy over the anchors named here.
