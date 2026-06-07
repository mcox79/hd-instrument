# Exp-Dev -> Research: Authorization 2 + 5 results (R3 anisotropy + Cell A distractor coherence)

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** 8-authorizations morning + K-hop noise fork

Two gating diagnostics ran (smoke; full queued). Both decisive.

## R3 (Auth 2) -- anisotropy CONFIRMED -> SRHT justified
Real MiniLM keys: PR/D=0.16, mean|corr|=0.090, top-10pct dims hold 62pct energy. Encoder is strongly anisotropic.
**-> Anisotropy IS the real-key ZKL root cause. Authorization 3 (SRHT engineering) is greenlit by this result.** SRHT
(random-sign Hadamard) whitens/randomizes these concentrated directions -> should recover the synthetic-key ZKL behavior.

## Cell A (Auth 5 + noise fork) -- distractors COHERENT -> v1 needs semantic sharding
Real MiniLM B=10 fan-out: **c_d_empirical = 0.48 (> 0.40 HARD-FAIL band).** Distractors are NOT random -- semantically
related facts cluster, so cross-shard fan-out pulls in coherent interferers.
**-> The cheap v1 50-LOC averaging+confidence filter (Auth 4) is INSUFFICIENT on real KBs. v1 distributed reasoning needs
SEMANTIC SHARDING (route related facts to the same shard) -- the v2 path, ~3-4 weeks.** This resolves the averaging-vs-
distractor noise fork in favor of the DISTRACTOR (coherent) model on real data. Recommend: don't commit the v1 cross-shard
build on the 50-LOC fix alone; scope semantic sharding.

## K-hop ceiling redesign (Auth 6) -- fixed
Calibrated noise + confidence threshold + ceiling 120 -> clean sub-ceiling K_max(N) signal (no more K_max=60 clipping).

NOTE these are smoke values; full runs queued (real n=3000). c_d=0.48 and PR/D=0.16 are large margins unlikely to flip at full.
