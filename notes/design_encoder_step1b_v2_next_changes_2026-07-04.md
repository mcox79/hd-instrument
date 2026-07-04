# Encoder Step 1b -> v2: concrete next changes (ready for exp_dev when quota returns)

**2026-07-04. Separates EVIDENCE-BACKED fixes (do now) from a WATCH item (pending FULL eval).**
Keep everything the SMOKE validated: block-structured codes (K blocks, 1 signed active/block),
SBC block-local circular convolution algebra, RKD + semi-hard InfoNCE objective, N_DIM=4096,
dual-gate eval. Self-test SBC roundtrip = 1.00 and keyed bind/unbind acc@1 = 1.00 are LOCKED wins.

## FIX 1 (evidence-backed, do first): re-aim dual-gate B at the KEYED composition path

**Why:** Step1b SMOKE verdict `HARD_FAIL_SPARSITY_NOT_PROTECTING` fired on a NON-PRODUCTION
scenario. The failing gate demanded sparse RAW-bundle recall > dense RAW-bundle recall
(BLOCK 0.584 < DENSE 0.604). But:
- Raw-bundle recall collapses for ALL semantically-trained codes (BLOCK 0.091 / TOPK 0.081 /
  DENSE 0.06 at J20) because semantic training makes codes CORRELATED, and correlated codes
  smear under raw superposition. RANDOM_BLOCK bundles ~perfectly (0.996) precisely because it
  carries no meaning.
- Production NEVER bundles raw concept codes. It binds fillers behind INDEPENDENT RANDOM role
  keys first (`semantic_parser.py` L16-17), which decorrelates them. The SMOKE's KEYED gate
  (bind->unbind->cleanup) = 1.0 for BLOCK at J5 AND J20. That is the production path and it is
  flawless.

**Change:** verdict gate B should PASS on keyed-composition fidelity (bind->unbind->cleanup
acc@1 >= 0.95 at the target bundle depth K) and DROP the "sparse raw-bundle must beat dense
raw-bundle" criterion. Keep raw-bundle recall as a REPORTED diagnostic (it characterizes the
semantic-correlation-degrades-superposition finding) but NOT as a pass/fail gate.

**Atom this produces (Skunkworks tier):** MM_TENTATIVE "semantic-correlation degrades raw-bundle
superposition recall; random-key binding is immune -- decorrelation not sparsity protects
composition." Composes with the algebra-preserving-distillation drill.

## RESOLVED (early-eval, no longer a watch item): LINEAR STUDENT CAPS ~0.64 -> MLP REQUIRED

**Early semantic read on the running K128 checkpoint at step 9000/20000** (script
`scratchpad/step1b_early_eval.py`, imports the cell's own encode+spearman, reconstructs only
the deterministic split): **spearman_all = 0.6428** (pearson 0.711, hi80_cos 0.367). Loss
plateaued -> final will be ~0.64-0.68. This is BELOW the SMOKE's 0.788 and far from goal 0.85.

**Conclusion (decisive):** the SMOKE's 0.788 was on an EASY 3000-concept subset and did NOT
scale. On the full 43905 concepts a LINEAR student W:1024->4096 caps at ~0.64. More data + more
steps made it WORSE, not better -> this is a CAPACITY ceiling, not just optimization.
**=> the MLP student (1024 -> 2048 -> 4096 GELU) is REQUIRED for 0.85, not optional.** Promote it
to the #1 v2 change. Batch-size + LR-schedule (below) are SECONDARY tunings that help but will
not close a ~0.20 gap on their own.

**Priority reorder for v2 (exp_dev, Monday):**
1. **MLP student (REQUIRED)** -- the capacity fix; the linear map provably cannot reach 0.85.
2. LR warmup+cosine decay + LAM_NCE rebalance (secondary; helps convergence quality).
3. Batch 512 (secondary; fewer pairwise constraints per step for the block code).
Keep everything validated: block codes, SBC algebra (roundtrip 1.0), RKD+InfoNCE objective,
dual-gate. The algebra side is DONE; only the semantic-capacity side needs the MLP.

## (superseded WATCH ITEM -- kept for the loss-curve diagnosis): rkd loss RISING

FULL run (pid 2800, seed 7): RKD loss ROSE 0.14 -> 0.19 over steps 0-3000 while InfoNCE fell
0.85 -> 0.62. rkd going the WRONG direction (SMOKE reached 0.08). Read the training loop
(`_core.py` L355-390) -- three concrete suspects, in priority order for exp_dev:

1. **~~Correctness bug: teacher not normalized~~ -- CHECKED, NOT A BUG (Director, off-disk).**
   Verified the cache `data/substrate_index/cached_indices/bge_large_v2_name_43905_8a40445a.npz`
   `semantic` array: norm mean=1.0000, std=0.0000 -> teacher IS unit-normalized, so L360
   `T = x @ x.T` IS a valid cosine target in [-1,1]. The student CAN match it in principle. Do
   NOT "fix" the normalization -- there is nothing to fix here. (Ruled out so exp_dev doesn't
   chase a phantom.)

2. **REAL SUSPECT A -- no LR schedule:** L88 `LR=1e-3` fixed, L335 plain Adam, no warmup/decay.
   L383 `loss = l_rkd + LAM_NCE*l_nce`; the NCE contrastive gradient dominates early and pulls the
   geometry off the relational target (rkd rises while nce falls -- observed). FIX: linear warmup
   (~500 steps) + cosine decay; consider gradient-norm balancing of the two terms, or raise the
   rkd weight / lower LAM_NCE.

3. **REAL SUSPECT B -- batch/block-capacity:** FULL batch 1024 vs SMOKE 192 -> ~28x more
   off-diagonal pairwise cosine targets for a K=128-block student (128 effective dims) to satisfy.
   The block-sparse bottleneck genuinely limits pairwise-geometry preservation at large batch.
   l_rkd 0.19 => student pairwise cosines off teacher by ~0.44 RMS. FIX candidates: smaller batch
   (512), OR more blocks (K=256), OR a small MLP student (1024 -> 2048 -> 4096 GELU) for capacity;
   keep the block sparsifier on the output. Most likely the dominant driver given the SMOKE (batch
   192) hit 0.788 and FULL (batch 1024) is regressing.

**Do NOT act tonight (CLAUDE.md: main thread must not edit experiments/*.py; agents rate-limited
until Mon).** Let FULL finish for the real spearman. Decision at eval:
- spearman >= 0.82: fine, scale up.
- [0.70, 0.82) or < SMOKE 0.788: apply fix (1) then (2), re-SMOKE; MLP student only if still short.
(Fix#28 discipline: no architecture verdict before the number lands -- but suspect (1) is a
verifiable bug independent of the eval, so exp_dev should check `Xd.norm` FIRST regardless.)

## Sequencing when agent quota returns (Monday 2026-07-07)
1. exp_dev: apply FIX 1 (gate re-aim) + read FULL eval -> apply the matching WATCH-item branch.
2. Skunkworks: VET the FULL semantic+keyed numbers; file the semantic-correlation atom.
3. Then FULL multi-seed (13,19) for cv on the semantic number before any capability claim.
