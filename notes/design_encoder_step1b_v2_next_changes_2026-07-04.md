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

## WATCH ITEM (do NOT conclude until FULL eval lands): linear-student rkd plateau

FULL run (pid 2800, seed 7) shows RKD loss plateaued ~0.18 by step ~2000/20000 -- 2x the SMOKE's
0.08 -- while InfoNCE oscillates 0.65-0.74. HYPOTHESIS (unconfirmed): a LINEAR student
W: R^1024 -> R^4096 saturates on the full 39515-concept set; it fit 3000 concepts to spearman
0.788 but may cap below that (and below 0.85) at 13x the concepts.

**Do NOT act on this yet.** The end-of-arm semantic spearman is the arbiter. Decision rule:
- FULL K128 spearman >= 0.82: linear student is fine; scale data/steps, no architecture change.
- FULL K128 spearman in [0.70, 0.82): linear student caps below goal -> v2 candidate: replace
  linear W with a SMALL MLP student (1024 -> 2048 -> 4096, GELU) for capacity to preserve
  pairwise geometry over more concepts. Cheap change; keep block sparsifier on the output.
- FULL K128 spearman < 0.70 AND below SMOKE: also check LR / warmup (nce oscillation suggests LR
  may be slightly high); add cosine LR decay before blaming capacity.

Confirm which case at the eval, THEN pick the v2 change. (Fix#28 discipline: no architecture
verdict before the number lands.)

## Sequencing when agent quota returns (Monday 2026-07-07)
1. exp_dev: apply FIX 1 (gate re-aim) + read FULL eval -> apply the matching WATCH-item branch.
2. Skunkworks: VET the FULL semantic+keyed numbers; file the semantic-correlation atom.
3. Then FULL multi-seed (13,19) for cv on the semantic number before any capability claim.
