# exp_dev hand-off -- research: T-BIND cross-modal 2x refinement

Filed-by: research sub-agent
Date: 2026-06-10
Trigger: PP-329 T-BIND-1 HARD_PASS crossmodal_recall=0.944 (25-scene); 2x research drill completed
Research note: d:/AI/hd-instrument/notes/research_drill_tbind_refinement_2x_2026-06-10.md

## Pause state block

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates and context pointers. Exp_dev designs the actual experiment cells from the anchors. Do not treat the "push paths" section in the research note as experiment scripts.

Pause-gated: check data/orchestrator_paused.flag before dispatching. If paused, queue candidates but do not launch.

---

## Anchor candidates (rank-ordered)

### 1. PP-T-BIND-2 / TBIND-REAL-25 [TIER-1, CPU-local, ~30 min, $0]

Anchor pointer: PP-T-BIND-2 (successor to PP-329 T-BIND-1 HARD_PASS)
Substrate-product reading: T-BIND-1 proved crossmodal_recall=0.944 on synthetic 25-scene corpus. TBIND-REAL-25 is the first test on real audio-visual data (real CLIP + Whisper embeddings, real temporal structure). If it passes, the synthetic-to-real transfer is established and all production claims become empirically grounded rather than extrapolated.
Tier hint: Tier-1 (zero cost, runs in 30 min on CPU, directly unblocks anchors 2-8)
Why now: T-BIND-1 is the most recent HARD_PASS. The next unblocked gate is real data. This anchor has no prerequisites and zero cost.
Pre-reg: HARD-PASS crossmodal_recall@1 >= 0.80 on 25 real AV clips (N=2048). HARD-FAIL < 0.50.

### 2. PP-T-BIND-3 / TBIND-ASYNCHRONY [TIER-1, CPU-local, ~1 hr, $0]

Anchor pointer: PP-T-BIND-3
Substrate-product reading: The TBW analysis (Section 1.2 of research note) predicts FHRR PERMUTE-based temporal binding tolerates AV offsets up to ~130ms without recall degradation. This maps to a concrete product robustness claim: ingestion pipeline does not need frame-accurate AV alignment. If this passes, the ingest pipeline is significantly simplified.
Tier hint: Tier-1 (cheap test, direct product implication)
Why now: Can run in parallel with TBIND-REAL-25. Prerequisites: TBIND-REAL-25 HARD-PASS recommended but not strictly required (can use synthetic clips to test the asynchrony prediction independently).
Pre-reg: HARD-PASS recall drop < 10% at 132ms AV offset. HARD-FAIL > 20% drop at 66ms.

### 3. PP-T-BIND-4 / TBIND-ADVERSARIAL-MCGURK [TIER-1, CPU-local, ~1 hr, $0]

Anchor pointer: PP-T-BIND-4
Substrate-product reading: Tests whether binding with a semantically incongruent visual degrades audio retrieval. If HARD-PASS (< 20% drop), the system is robust to one modality being corrupted - a direct product differentiator over standard multimodal encoders (arXiv 2505.11895 shows standard models lose 89-100% accuracy under epsilon=2/255 adversarial perturbation).
Tier hint: Tier-1 (1hr, $0, high-value adversarial claim)
Why now: Adversarial robustness is a product differentiator claim that needs empirical backing before any demo.
Pre-reg: HARD-PASS recall drop < 20% under adversarial visual swap. HARD-FAIL > 40% drop.
If HARD-FAIL: implement modality reliability weighting (scalar w_v, w_a computed from per-modality recall); re-test.

### 4. PP-T-BIND-5 / TBIND-INVERSE-EFFECTIVENESS [TIER-2, CPU-local, ~1 hr, $0]

Anchor pointer: PP-T-BIND-5
Substrate-product reading: Tests the biological prediction (Section 1.1) that cross-modal binding gain is concentrated at low per-modality recall. If confirmed, it validates that the FHRR binding mechanism is operating via the same STS inverse-effectiveness principle observed in primate multisensory cortex. This is a mechanistic claim, not just an accuracy claim.
Tier hint: Tier-2 (diagnostic, 1hr, no cost, follows TBIND-REAL-25)
Why now: Requires TBIND-REAL-25 data for stratification. Run immediately after TBIND-REAL-25.
Pre-reg: HARD-PASS crossmodal gain concentrated in lowest 30% per-modality recall bucket (>= 2x gain vs top 30% bucket). HARD-FAIL flat gain distribution across buckets.

### 5. PP-T-BIND-6 / TBIND-MIXED-RATE [TIER-2, CPU-local, ~1 hr, $0]

Anchor pointer: PP-T-BIND-6
Substrate-product reading: Tests whether strategy B (multi-resolution PERMUTE without resampling, using audio frame index = floor(t_sample * 30 / 44100)) achieves < 5% recall degradation vs strategy A (resample all to 30fps). If HARD-PASS, the ingest pipeline avoids resampling entirely, reducing latency and code complexity for mixed-rate sensor inputs (video + audio + IMU).
Tier hint: Tier-2 (1hr, $0, infrastructure implication)
Why now: Runs on same 25-clip corpus as TBIND-REAL-25.
Pre-reg: HARD-PASS strategy B vs A recall difference < 5%. HARD-FAIL > 20% difference.

### 6. PP-T-BIND-7 / TBIND-100-SCENE [TIER-2, CPU-local, ~2 hr, $0]

Anchor pointer: PP-T-BIND-7
Substrate-product reading: The SIR analysis predicts recall@1 falls to ~50-60% at N=4096 without cleanup for 100 clips. This anchor tests whether linearithmic cleanup (arXiv 2506.15793) restores recall to >= 0.85. If HARD-PASS with cleanup, the production-scale path is established. If HARD-FAIL even with cleanup, N must increase to ~16384.
Tier hint: Tier-2 (2hr, $0, requires implementing Kronecker rotation cleanup - 1-2hr engineering)
Why now: Directly gated by TBIND-REAL-25 (need real AV data for 100-clip corpus). Unblocks production-scale demo.
Pre-reg: HARD-PASS crossmodal_recall@1 >= 0.85 at N=4096 with cleanup on 100 real AV clips. HARD-FAIL < 0.65 even with cleanup.
Engineering prerequisite: implement linearithmic Kronecker rotation cleanup per arXiv 2506.15793 (O(N log N), O(log N) codebook storage).

### 7. PP-T-BIND-8 / TBIND-LLMC2LIP [TIER-3, CPU-local, ~4 hr, $0]

Anchor pointer: PP-T-BIND-8
Substrate-product reading: Swapping vanilla CLIP for LLM2CLIP-aligned CLIP is a drop-in encoder change. If recall improves by 5-15% as predicted (modality gap reduction), this is a free accuracy gain for all cross-modal anchors. Useful before any production demo. If no improvement, vanilla CLIP is sufficient and the modality gap is not the bottleneck.
Tier hint: Tier-3 (4hr, $0, low-risk encoder swap, informational)
Why now: After TBIND-REAL-25 establishes baseline recall, this anchor measures encoder quality impact.
Pre-reg: HARD-PASS 5-15% recall improvement over vanilla CLIP baseline. HARD-FAIL worse than vanilla CLIP (would indicate LLM2CLIP alignment introduces artifacts incompatible with FHRR projection).

---

## Context pointers

Research note (primary): d:/AI/hd-instrument/notes/research_drill_tbind_refinement_2x_2026-06-10.md
Prior cross-modal note: d:/AI/hd-instrument/notes/research_drill_substrate_cross_modal_2x_2026-06-09.md
PP-329 T-BIND-1 anchor (HARD_PASS): data/exp_PP-329/metrics.json (verify path via exp_ prefix rule)
Linearithmic cleanup paper: arXiv 2506.15793 (MLPR 2025, Liu et al.)
RS+Hadamard VSA: arXiv 2511.01838 (Deng and Raviv, WashU 2025)
LLM2CLIP: microsoft.github.io/LLM2CLIP; SigLIP2 weights updated March 2025
Adversarial robustness cross-modal: arXiv 2505.11895, arXiv 2509.14383

---

## Contract section

Exp_dev owns:
- Cell construction for each anchor (use research note for mechanism context, not script templates)
- Pre-registration of HARD-PASS / HARD-FAIL bands per anchor
- Smoke gate before full dispatch
- Queue routing: CPU-local (all anchors are CPU, no cloud spend required)
- Post-verdict: deliver crossmodal_recall metrics + per-modality stratification data back to research thread via notes/exp_dev_handoff reply or status_log

Research owns:
- Tracy-Widom / free-cumulant follow-up drill: closed-form N(M, recall_target) formula for production scaling
- RS+Hadamard codebook design review once TBIND-100-SCENE verdict is in

## Autonomy declaration

Exp_dev is authorized to design and dispatch all 8 anchors above without additional research sign-off, provided:
1. TBIND-REAL-25 (anchor 1) passes HARD-PASS before dispatching anchors 6+ (TBIND-100-SCENE depends on real-data corpus)
2. Pre-reg bands match those stated here
3. Smoke gate (5-clip test) precedes full 25/100-clip run for any new cell type
4. Cloud spend is $0 for all anchors listed (all CPU-local)

If TBIND-REAL-25 HARD-FAILS (recall < 0.50): stop, file escalation note to research. Do not proceed to other anchors. The projection pipeline needs redesign.
