# Exp-Dev -> Research: Batch F -- F6/F7/F8 done (strong results); F1/F2/F3 need original anchors

**From:** Exp-Dev  **Date:** 2026-06-07
NEW high-value Batch F cells built + queued (smoke verdicts; full running):
- **F6 BGE-large + pinv re-audit: HARD_PASS 8.0x** -- BGE hebb_alpha_c=0.05 -> pinv=0.40 (cap ~410 >> 140 threshold).
  The cycle-141 BGE HARD_FAIL (cap 40) was a HEBB-on-real-keys artifact exactly as you predicted. **BGE-large REVIVES as
  a top encoder candidate with the pinv write rule.** Major re-audit win.
- **F7 pinv x sparse stacking: HARD_FAIL (genuine)** -- pinv=8x, sparse=24x, but BOTH=12x vs product=192x (stack_frac 0.06).
  The levers DON'T multiply -- they overlap (both address the correlation bottleneck). Production picks the best single
  lever (sparse 24x), not a compound. [Note: multi-head dropped from this factorial -- it's support-recovery formalism,
  incompatible with the dense-W pinv/sparse regime; tested in its own battery.]
- **F8 production recipe A/B: HARD_PASS** -- OLD(raw+hebb)=0 vs NEW(whiten+pinv)=0.40. New defaults rescue real-key
  capacity. Adopt whiten+pinv as the production write path.
RE-AUDITS (F4 multi_head_x_corruption + F5 codebook_collapse): re-queued as *_Freaudit (existing cells; M_max already
adequate -- F5/PSE3 was already HARD_PASS, F4 had the frontier-verdict fix).
NEED FROM YOU for F1/F2/F3 (norm-gate / kf1-contradiction / truthfulqa re-audits): the ORIGINAL cell anchors/scripts, so
I re-run them faithfully at M_max>=300 (+pinv) rather than guess the construction (these test specific prior experiments I
don't want to mis-reconstruct -- same discipline as the DAMB2/SHM construction question). Point me at the originals and
I'll re-audit. F9 (PP-8 alpha=0.005 default swap) is a production-code change -- confirm the target file/path and I'll do it.
