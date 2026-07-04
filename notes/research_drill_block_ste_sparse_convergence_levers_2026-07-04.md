# Research drill: levers to converge a BLOCK-STE sparse code to teacher geometry

Drafted 2026-07-04 (Director research drill) to de-risk the encoder's KNOWN
next bottleneck BEFORE the v2 MLP FULL lands (~14:30-16:30Z). Target reader:
exp_dev, to apply the top lever the instant the FULL BLOCK_K128 number lands.

Cell: `experiments/exp_encoder_migration_step1b_v2_mlp_distill_concept_encoder_v1_core.py`
Sparsifier under study: `_block_ste()` (lines 370-382).

## The bottleneck (exp_dev smoke, restated)

- DENSE_SIGN arm (sign of ALL 4096 dims, 100% active) = spearman 0.825 -> the
  MLP's continuous geometry is GOOD; the readout capacity is there.
- BLOCK_K128 (STE sparsifier, 128 active = 3.125%) = 0.645 @ 150 smoke steps.
- The 0.825 -> 0.645 gap is PURE SPARSIFICATION COST, not MLP capacity.
- exp_dev's call: if FULL lands MIDDLE_BAND despite high dense readout, the
  lever is more steps / K-revisit / sparsifier, NOT more capacity. CONCUR.

## Substrate prior-work check (mandatory, ran before drill)

- `substrate_query "sparse block code convergence straight-through estimator"`
  top hit cosine=0.356 = `notes/wave14e_hierarchical_composition_research.md`
  ("Sparse block codes", Hersche arxiv:2303.13957) -- treats sparse block codes
  as an ANALYTIC ~2x CAPACITY mechanism, NOT as a distillation/STE-CONVERGENCE
  training problem. No overlap on how to TRAIN a sparsifier.
- `substrate_query "Gumbel softmax sparse assignment temperature annealing"`
  top hit cosine=0.31 = pure WordNet/FrameNet noise. Substrate has ZERO prior
  work on Gumbel / temperature-annealing / decoupled-STE.
- Prior arc work on this concept: NONE (capacity-analytic only). This is novel
  synthesis for the project -> lit-scan calibration penalty applied, P capped
  at 0.50, deflated 0.15-0.25.

## GLOBAL INVARIANT (de-risks "without breaking the algebra" entirely)

The DEPLOYED code is produced by `_encode_hard_block()` (argmax, exact
1-active-per-block ternary) REGARDLESS of how training runs. The SBC block-local
circular-convolution roundtrip (=1.000 self-test) is a property of that CODE
STRUCTURE (exactly 1-per-block, ternary), not of the sparsifier gradient. Every
lever below (L1-L5, L7) leaves the forward hard-encode structurally identical ->
algebraic roundtrip stays ~1.0 BY CONSTRUCTION. Only a lever that changed the
deployed structure (>1 active/block, non-ternary values) could threaten it, and
none proposed here does. The convergence work and the algebra are decoupled;
exp_dev can tune the sparsifier freely without re-checking the roundtrip beyond
the existing self-test. (L6 changes K but stays 1-per-block -> roundtrip still
1.0 for any kb, as the self-test already covers kb=16.)

## DECISION TREE -- pick ONE lever from the LANDED FULL numbers

The GPU-once-per-stage discipline means we get ~one more big run; choose right.
When FULL lands, READ `metrics.json` -> `train_diag["BLOCK_K128"]` and the
per-step rkd trace / `_heartbeat.jsonl` BEFORE picking:

1. If verdict = HARD_PASS (spearman >= 0.85, keyed@J5 >= 0.95): done, no lever.
2. If MIDDLE_BAND and block rkd_last is STILL DESCENDING at 40k steps
   (undertrained): -> L3 (more steps) is the cheapest first move. Cheap because
   it is a resume from checkpoint, not a fresh run.
3. If MIDDLE_BAND and block rkd has PLATEAUED but spearman < 0.85 (converged to
   a bad sparse optimum -- the flip-flop exp_dev named): -> L1 (decoupled tau_b
   anneal) is THE move. This is the expected case and the primary deliverable.
4. Before committing the big rerun to L1/L2, run L6 (K=256 one-shot diagnostic)
   to confirm convergence-limited vs capacity-limited. If K256 sails to 0.85+,
   L1/L2 will work; if even K256 caps low, the problem is objective/MLP, re-scope.
5. K64 in the current sweep will lag K128 on BOTH counts (see L6) -- do NOT read
   that as sparsifier failure.

## RANKED LEVERS

| # | Lever | Semantic | Roundtrip | Cost | Drop-in? | P_defl |
|---|-------|----------|-----------|------|----------|--------|
| L1 | Anneal backward-surrogate temp tau_b (decoupled STE) | ++ | unchanged | config + ~15 lines plumbing | DROP-IN | 0.45 |
| L2 | Dense->sparse curriculum (continuous-first) | ++ | unchanged | ~30-40 lines | borderline | 0.45 |
| L3 | More steps (checkpoint-gated on rkd non-plateau) | + iff undertrained | unchanged | config (FULL_STEPS) | DROP-IN | 0.30 |
| L4 | Commitment / per-block low-entropy term | + | unchanged | ~15 lines | DROP-IN | 0.35 |
| L7 | Schedule objective balance LAM_NCE/TAU_NCE | + | unchanged | config + small | DROP-IN | 0.30 |
| L5 | Batch-marginal anti-collapse guard (mostly diagnostic) | 0/+ | unchanged | trivial metric | DROP-IN | 0.20 |
| L6 | K / block-config -- DIAGNOSTIC ONLY, not a "fix" | n/a | unchanged | config +1 train | DROP-IN | n/a |

L1 and L2 are the SAME mechanism family (smooth vs staged); pick one integrated
schedule, do not stack. L1 is the recommended instant-apply.

## LEVER DETAIL

### L1 -- Anneal the backward-surrogate temperature tau_b (decoupled STE). TOP.
Root cause: `_block_ste` computes `p = softmax(|z|/TAU_GUMBEL)` with
`TAU_GUMBEL=1.0` FIXED, forward = exact argmax (hard), backward gradient flows
through `p`. The forward is already hard (tau_f -> 0) and the backward is soft at
a FIXED tau=1.0 -- so the cell is ALREADY a decoupled-temperature STE, it just
never TUNES or ANNEALS the backward temp. Because tau_b is fixed at 1.0 the
gradient keeps pointing at a soft mixture even after the hard argmax stabilizes;
that persistent forward/backward mismatch is exactly the "sparse assignments
hadn't converged" symptom. Decoupled-STE (arxiv:2410.13331) shows optimal
(tau_f, tau_b) lie FAR OFF the diagonal tau_f=tau_b and that tuning tau_b beats
Identity STE, Softmax STE, and ST-Gumbel-Softmax. Temperature-annealing lit:
high tau early (smooth gradient, explore which block-member should win) ->
anneal low (backward surrogate sharpens toward the hard forward, shrinking STE
bias). Recipe: add `_tau_at(step, total, warmup)` mirroring the existing
`_lr_at` cosine schedule; anneal tau_b ~2.0 -> ~0.1 (floor tau_min ~0.1 to cap
gradient variance -- low tau amplifies Gumbel/softmax variance). Thread `tau_b`
into `_block_ste(z, kb, blk_l, tau_b)` and pass the scheduled value at the two
call sites (lines 465, 480). Forward argmax is invariant to tau_b -> roundtrip
untouched.
- Effect: semantic spearman ++ (direct attack on the block-lag); roundtrip 1.0.
- Cost: backward-pass-only, ~15 lines. DROP-IN. P_deflated 0.45 (novel-synthesis
  cap; strong lit support but "closes gap to 0.85" is the deflated claim).
- Watch: too-aggressive anneal -> premature collapse to a bad discrete optimum
  (lit warning); keep the schedule at least as long as warmup+cosine LR.

### L2 -- Dense->sparse curriculum (continuous-first, discrete-later).
The DENSE_SIGN arm already hits 0.825: the MLP forms teacher geometry fine when
NOT forced sparse. Block-STE from step 0 forces the net to form geometry AND
commit sparse assignments simultaneously. Stage it (arxiv:2605.06870 "Continuous
First, Discrete Later" -- a TWO-PHASE schedule, continuous representation first,
quantization introduced later, so the encoder builds a rich representation
before the discrete bottleneck bites; their collapse mechanism is NOT
MSE-specific): phase 1 (first ~30-40% steps) train on the DENSE/high-tau-soft
code so geometry forms; phase 2 ramp block-STE hardness via a blend
`code = (1-a)*dense_soft + a*block_ste`, a: 0 -> 1, OR simply run L1's tau_b
anneal starting very high so early steps are near-dense. Final `_encode_hard_block`
is always hard -> deploy code + algebra unchanged.
- Effect: semantic ++ (attacks the same root cause as L1, staged form);
  roundtrip 1.0.
- Cost: ~30-40 lines in `_train_student` (blend schedule + dense branch).
  Borderline DROP-IN. P_deflated 0.45. Redundant with L1 -- choose one.

### L3 -- More steps (checkpoint-gated).
exp_dev's own first hypothesis. Smoke was only 150 steps; FULL already bumped to
40k with batch 512. If the landed `train_diag` rkd trace is still descending at
40k, resume-extend to 60-80k (checkpoint/resume already implemented) until rkd
plateaus. If rkd ALREADY plateaued at 40k and spearman is still MB, more steps
will NOT help -- it is a sparsifier problem (-> L1), not undertraining.
- Effect: semantic + ONLY iff undertrained; roundtrip 1.0.
- Cost: config (FULL_STEPS), resume from ckpt. DROP-IN. P_deflated 0.30
  (undertraining plausible from the 150-step smoke, but 40k may already suffice
  -- the trace decides; that conditionality is why it is deflated hard).

### L4 -- Commitment / per-block low-entropy term.
VQ-VAE commitment-loss analog. The argmax block-winner flip-flops because
nothing rewards the MLP for a CONFIDENT (peaked) within-block distribution. Add
`lambda_commit * mean_block_entropy(p)` to the loss (`p` already exists in
`_block_ste`; return it or its per-block entropy). This drives the within-block
|z| to separate -> argmax stabilizes -> STE bias shrinks -> faster/better
convergence. Complements L1 (sharper distribution helps the annealed surrogate).
- Effect: semantic + (stabilizes assignments); roundtrip 1.0.
- Cost: ~15 lines (`_block_ste` exposes entropy; add term at loss line 490).
  DROP-IN. P_deflated 0.35.
- Watch: over-weighting entropy -> premature collapse (same lit warning as L1);
  keep lambda_commit small and pair with L5's usage diagnostic.

### L7 -- Schedule the objective balance (LAM_NCE / TAU_NCE).
v2 already halved batch + added LR warmup because "the NCE contrastive gradient
dominated early and pulled geometry off the relational target" in v1. InfoNCE at
TAU_NCE=0.07 (very sharp) demands separations a 3.125% code struggles to satisfy,
stealing capacity from RKD's pairwise-geometry fit -- and spearman MEASURES that
geometry. Lever: warm up LAM_NCE (0 -> 0.5) like the LR, and/or use a softer
TAU_NCE early, so phase-1 geometry forms under RKD, discriminability comes later.
Pairs naturally with L2's phase schedule.
- Effect: semantic + (frees capacity for the geometry spearman scores);
  roundtrip 1.0.
- Cost: config + small plumbing (schedule LAM_NCE per step). DROP-IN.
  P_deflated 0.30.

### L5 -- Batch-marginal anti-collapse guard (mostly a DIAGNOSTIC).
Distinct from L4's per-SAMPLE entropy: this is the per-block-POSITION usage
across the BATCH. VQ codebook-collapse lit: STE encoder drift can leave some
in-block positions never selected (dead positions), vanishing marginal entropy.
Add a metric = per-block position-usage entropy over the eval set so we can SEE
whether collapse is the failure mode; optionally a small KL(batch-marginal ||
uniform) reg (or WTA-autoencoder "lifetime sparsity"). If collapse is not
occurring, no gain -- so this is primarily instrumentation to disambiguate.
- Effect: 0/+ (only if collapse present); roundtrip 1.0.
- Cost: metric trivial; reg small. DROP-IN. P_deflated 0.20.

### L6 -- K / block-config: DIAGNOSTIC ONLY, do NOT use as the "fix".
N=4096, 1-active-per-block: K blocks -> K active, sparsity=K/N, code-bits ~
K*(log2(N/K)+1). K=128 -> 3.125%, ~768 bits. K=64 -> 1.56%, ~448 bits, block_len
64 (HARDER argmax, more competitors). K=256 -> 6.25%, ~1280 bits, block_len 16
(EASIER argmax). The USER encoder goal is ~2% sparse; K=128 is ALREADY over that
(3.125%). Raising K to 256 to hit 0.85 would VIOLATE the sparsity goal -- NOT a
legitimate fix. BUT run K=256 ONCE as a capacity-ceiling diagnostic: if it sails
to 0.85+, the block-lag is convergence/sparsifier-limited (L1/L2/L4 apply); if
even K256 caps below 0.85, it is an MLP-capacity or objective problem -> re-scope
(different fix). Also note: the current sweep drops to K64 (toward the 2% goal)
which is a DOUBLE penalty (fewer bits AND harder convergence) -- expect K64 < K128
on both; do not misread as sparsifier failure. TENSION TO FLAG UPSTREAM: hitting
BOTH 0.85 semantic AND ~2% sparse (K~82, ~543 bits) is genuinely harder than at
K=128; if K=128 only just reaches 0.85, the 2% target may be capacity-bound and
need its own decision (relax to ~3% or accept <0.85 at 2%).
- Effect: diagnostic (disambiguates convergence- vs capacity-limited).
- Cost: config (add 256 to sweep) + 1 extra GPU train. DROP-IN-config. P: n/a.

## RECOMMENDED INSTANT-APPLY (if FULL lands MIDDLE_BAND)

1. READ `train_diag["BLOCK_K128"]` rkd trace first (decision tree above).
2. If plateaued-but-MB (expected): apply L1 (tau_b cosine anneal 2.0->0.1,
   floor 0.1), backward-only, ~15 lines. Optionally stack L4 (small
   lambda_commit) since it is orthogonal and cheap. Add L5 metric for free
   visibility.
3. Run L6 K=256 as the disambiguating diagnostic in the SAME dispatch batch.
4. If rkd still descending: L3 (resume-extend) is cheaper; try first.
All are algebra-safe by the global invariant -- no roundtrip re-verification
needed beyond the existing self-test.

## Sources
- Decoupled STE (separate forward/backward temps; optimal off-diagonal; beats
  Identity/Softmax STE + ST-Gumbel): arxiv:2410.13331
- Continuous First, Discrete Later (two-phase continuous->discrete; avoids
  dimensional collapse; not MSE-specific): arxiv:2605.06870
- Rao-Blackwellized ST-Gumbel-Softmax (variance reduction, faster convergence):
  arxiv:2010.04838
- Gumbel-softmax temperature annealing schedules (exp / monotonic decay;
  aggressive->collapse, too-smooth->indecisive): emergentmind gumbel-softmax topic
- VQ-VAE commitment loss / codebook collapse / entropy-KL-to-uniform;
  NSVQ encoder-drift (arxiv:2606.11363); FSQ never-collapse
- Cosine-annealed dense->sparse cardinality curriculum; KL cost annealing /
  cyclical annealing (warm-restart discrete codes)
- Group sparse coding with WTA networks (block-1-active = group sparse coding;
  l0+l1 optimal capacity-sparsity tradeoff): PMC3403521; WTA-AE arxiv:1409.2752
- Relational KD + contrastive InfoNCE preserve embedding geometry; CRD;
  L2-replay fails to preserve relational geometry: arxiv:2407.12073
- Prior-arc substrate: notes/wave14e_hierarchical_composition_research.md
  (Hersche sparse block codes arxiv:2303.13957, capacity-analytic only)
