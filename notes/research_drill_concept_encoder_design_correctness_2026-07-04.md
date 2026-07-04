# Research Drill: Is the Concept Encoder Design Right? (2026-07-04)

**Author:** Director (Research)
**Trigger:** USER designated the concept encoder as the load-bearing component; wants it "right," not "finished."
**Method:** substrate-KB concept-query (query-first discipline) + 2x web drill (broad sparsity + narrow distillation) + off-disk read of cell/prereg/CG metrics.
**Calibration:** lit-scan penalty applied (deflate 0.15-0.25; novel-synthesis P capped 0.50).

---

## TL;DR (single most load-bearing finding)

The migration mechanism's OWN phase-diagram characterization ceilings at **cat_kitten_cos ~0.49-0.52** on a FAVORABLE, curated, effectively-supervised synthetic corpus (where cat/kitten were constructed to share contexts). The migration targets **0.85 on a HARDER regime** (sparse 970K natural KB, avg ~1.6 atoms/entity) with **no semantic teacher, no contrastive loss, no negatives**. The training objective has **no signal source capable of 0.85**. The design is SOUND as a pipeline artifact-producer but NOT SOUND for the 0.85 semantic-cosine target as currently specified. The fix is **dense-teacher (BGE) distillation**, not "finish the pipeline."

**P_deflated("current Step-1 design hits 0.85 semantic cosine") = 0.05.** (High confidence in the NEGATIVE.)

**Halt-or-continue:** Let Step 1 finish (cheap ~2-4h CPU; honest MM_TENTATIVE framing; produces a real baseline artifact + checkpoint/resume proof) BUT do NOT proceed to Step 4 route-flip on this design, and surface to USER NOW that the 0.85 target requires a design change (add distillation), not a finished pipeline. Run Step 3 gold-verify EARLY as the reality check (expect ~0.2-0.4, far below 0.85).

---

## Per-question verdicts

### Q1 — Sparsity target: k_sparsity = 0.02 (the real knob) -> GROUNDED

Clarification of a misread trap: the selftest literal `mean_nnz in [18,22]` is a **scale-specific smoke band** at N_DIM=1024 (k = round(0.02 x 1024) = 20, +/-2 tie-break). The FULL design uses N_DIM=4096 -> k=82, band [78,86]. The actual design target is **2% active fraction**, not "20 nonzeros."

2% active is grounded on three independent supports:
- **Numenta HTM/SDR standard** operates at ~2% active; the SDR literature treats 2% at moderate N as a canonical operating point (interference scales ~k^2/N; "make layers wider rather than reduce k" resolves the capacity-sparsity tradeoff -- lit-confirmed).
- **Brain sparse-coding fraction ~1-5%** active neurons; 2% sits squarely inside.
- **Substrate's OWN Spoke-1 phase-diagram law** already validated `sparse_rate in [0.01, 0.03]` as an INDEPENDENT axis (cat_kitten_cos invariant across k in that band). k=0.02 is inside the substrate's proven-invariant window.

Note Kanerva SDM runs sparser (0.5% at N=10000) but at much higher N; at N=4096 the 2% choice is defensible, not arbitrary.

**Verdict: GROUNDED.** Minor doc FLAG: the selftest comment should state "[18,22] = 2% x 1024," not read as a raw target, to prevent future misreads. Do NOT spend cycles re-deriving 0.02.

### Q2 — Training objective -> FLAG / NEEDS-RE-DERIVATION (load-bearing)

The objective is **unsupervised competitive-Hebbian aggregation**: per-entity mean of char-positional surface HDs over KB-co-occurrence context strings, then top-2% WTA + sign. There is:
- **NO distillation from BGE** (the migration throws away the 0.54 semantic signal it is trying to beat),
- **NO contrastive / triplet loss** (objective is aggregative, not discriminative),
- **NO negative sampling of any kind.**

The only semantic signal is KB relational co-occurrence at ~1.6 atoms/entity -- near-zero shared context for most concept pairs. The base `CharPositionalEncoder` is self-documented as "SURFACE FEATURES ONLY ... does NOT know semantic identity of any word. Brain analog: V1." So cat/kitten (few shared chars) start near-orthogonal, and the KB provides too little shared context to pull them to 0.85.

Decisive off-disk evidence (substrate-grounded, not speculation):
- v3-D CG source cited at `cat_kitten_cos_mean=0.492`.
- Spoke-1 investigation: COMPETITIVE_ONLY cat_kitten = 0.522; HYBRID = 0.220.
- Phase-diagram HP bands set at `>= 0.35-0.40`; `< 0.20` = HARD_FAIL boundary.
- These were on a **curated synthetic corpus** where cat/kitten were constructed to co-occur (mechanism-analog-is-not-task-analog / supervised regime per USER-locked memory).

The mechanism tops out ~0.52 on its FRIENDLIEST corpus. 0.85 on a harder natural corpus is a ~0.33-0.35 extrapolation ABOVE the proven ceiling, in the wrong direction (natural KB is sparser than the synthetic). Literature on dense->sparse distillation is explicit: a sparse student that must "preserve the rich semantic quality of existing dense features" learns them FROM the dense teacher; "any degradation in dense features is directly inherited." You cannot manufacture 0.85 semantics from orthography + sparse triples.

Separately, the task's "false-win" risk (high cosine but destroyed FHRR unbinding fidelity) is real and must be a SEPARATE gate -- but it is not yet reachable because cosine won't hit 0.85 in the first place.

**Verdict: NEEDS-RE-DERIVATION.** The objective must become a **contrastive/self-KD distillation from a dense teacher** into the sparse-bipolar code, with a separate algebra-fidelity gate.

### Q3 — Brain analogy -> APT; it FLAGS the same gap

Correct mapping: `CharPositionalEncoder` = V1/primary sensory (self-documented). The concept encoder aspires to the **ATL semantic hub** (hub-and-spokes model; multimodal convergence zone doing conjunctive coding of increasing complexity -- lit-confirmed). Where we can EXCEED the brain: no catastrophic interference (SHARDED table), controllable exact sparsity, exact FHRR algebra, no forgetting, deterministic reproducibility.

But the analogy reveals the SAME gap as Q2: the brain's ATL hub is built from RICH multimodal spoke input (vision, audition, action, and lifetime language distributional co-occurrence). Our hub receives only sparse symbolic KB triples + orthography -- it is missing the distributional/perceptual spoke input that gives ATL its semantic geometry. **A dense-teacher (BGE) distillation is the closest available substitute for that missing lifetime of distributional experience.**

**Verdict: analogy apt; corroborates Q2.**

### Q4 — Negative sampling / hard negatives -> FLAG (absent), contingent on Q2

No negatives of any kind. For a 970K-concept vocabulary, literature is clear: in-batch negatives alone are too easy at scale ("model learns little from truly random negatives"); ANCE-style hard-negative mining from the model's own nearest-neighbor retrievals is standard, mixed with in-batch + corpus negatives (MNS), with balance (all-hard biases the geometry). BUT negatives only matter once the objective is DISCRIMINATIVE. The current objective is aggregative, so "add hard negatives" is strictly downstream of adopting a contrastive/distillation objective (Q2).

**Verdict: FLAG; ranked under Q2 (do #2 first, then #3).**

### Q5 — Failure-mode audit (mean_nnz=616.91 crash) -> RESOLVED; robust against recurrence

The `mean_nnz=616.91` crash (N=1024, 30x the k=20 target) is on-disk in the FULL metrics.json at 23:28Z but is **stale from a pre-fix cell version** (likely a quantile-threshold WTA `magnitudes >= pivot` that tied across many dims, or a missing mask). The current cell sparsifies via `np.argpartition(-magnitudes, k)[:k]` -> a mask of exactly k indices -> nnz is **structurally bounded to exactly k by construction** (sign-zero -> +1 only fills within-mask). The 23:50Z smoke confirms `mean_nnz=82.00` EXACTLY at N=4096. NaN/Inf sentinels present; chunk-level failure-class instrumentation present.

**Verdict: GROUNDED against recurrence.** One operational note: the on-disk FULL is still `CELL_CRASHED` (stale pre-fix); FULL has NOT completed and needs a re-dispatch of the fixed cell.

---

## P_deflated

**P("current Step-1 design as specified reaches 0.85 semantic cosine") = 0.05.**

Reasoning: proven mechanism ceiling ~0.52 on the friendliest corpus; target 0.85 on a harder corpus; no semantic teacher; no discriminative objective; no negatives. This is a novel-synthesis extrapolation ABOVE the ceiling -> cap 0.50, then deflate hard against the direct disconfirming evidence -> ~0.05. High confidence in the NEGATIVE.

Framing split (both true):
- **Step 1 as a pipeline artifact-producer:** SOUND (smoke passes, robust, checkpoint/resume works, honest MM_TENTATIVE; prereg item 5 itself flags 0.85 as unlikely and defers the semantic claim to Step 3).
- **The migration's ability to hit USER's 0.85 target:** NOT SOUND as specified.

---

## Design-change recommendations (ranked by expected impact on 0.85)

1. **[HIGHEST] Add dense-teacher distillation.** Change the objective to contrastive + MSE distillation from BGE-large (or a stronger teacher) INTO the sparse-bipolar code. Only path with literature + substrate support to preserve/exceed 0.54 -> 0.85. The sparse student inherits teacher semantics; sparsity + FHRR algebra layer on top. Without this, 0.85 is unreachable.
2. **[HIGH] Two-objective: semantic-match AND algebra-fidelity gate.** Cosine-match to teacher PLUS an explicit gate that bind/bundle/cleanup unbinding accuracy survives sparsification above threshold (the false-win guard the task names). Prevents "high cosine, dead algebra."
3. **[MED] Add hard negatives (ANCE-style)** -- contingent on #1. Mine from the model's own NN retrievals; mix with in-batch + corpus negatives; keep balance to avoid geometry bias.
4. **[MED] If staying teacher-free: densify co-occurrence.** 1.6 atoms/entity is too sparse; expand context via 2-hop KB neighborhoods and/or WordNet gloss expansion. Lower ceiling than distillation but keeps it dependency-free.
5. **[LOW] Keep k_sparsity=0.02.** Grounded; do not re-derive. Optionally sweep [0.01,0.03] per the existing phase-diagram law ONLY if Step 3 shows sparsity-limited signal.

---

## Halt-or-continue

**CONTINUE Step 1 to completion (re-dispatch the fixed cell); HALT the 0.85 claim; PRE-EMPT with a distillation redesign.**

- Letting Step 1 finish is cheap and NOT wasted: it produces a testable baseline artifact, proves the pipeline/coverage/sparsity/resume, and gives Step 3 a concrete gap to measure.
- Do NOT gate downstream (Step 4 route-flip) on this design. Run Step 3 gold-verify EARLY as the honest reality check (expect ~0.2-0.4).
- In parallel, author the distillation variant (recommendation #1) so we are not blocked behind a design that cannot reach the target.

---

## Provenance

- Cell: `experiments/exp_encoder_migration_step1_train_concept_encoder_970K_KB_v1_core.py`
- Prereg: `preregs/2026-07-04_encoder_migration_step1_train_concept_encoder_970K_KB_v1.md`
- Base encoder: `hdlab/char_positional_encoder.py` ("SURFACE FEATURES ONLY ... V1 analog").
- CG ceiling evidence: `notes/design_stage2_concept_encoder_spoke1_predictive_coding_competitive_allocation_2026-07-02.md`, `notes/research_spoke1_pc_earning_complexity_investigation_2026-07-02.md` (COMPETITIVE_ONLY cat_kitten=0.522), `notes/research_spoke1_phase_diagram_extension_axes_and_probe_design_2026-07-02.md` (sparse_rate [0.01,0.03] invariant; HP >=0.35-0.40).
- On-disk state: smoke HARD_PASS mean_nnz=82.00 (23:50Z); FULL CELL_CRASHED stale mean_nnz=616.91 (23:28Z, pre-fix).
- Web calibration: SDR active-fraction (Numenta/Kanerva/HTM); dense->sparse contrastive distillation; ATL semantic hub; ANCE hard-negative mining.

ASCII-only. No emojis. No em dashes.
