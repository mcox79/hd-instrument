# exp_dev hand-off — research: 2x revival v2e self-mapping HARD_FAIL

Filed-by: research (Opus 4.7-1M)
Date: 2026-06-23
Trigger: USER 2x revival drill on v2e_modularity_Z_LRG_self_mapping_v1_smoke HARD_FAIL — diagnosis is encoder-bound (graph bit-identical to degree-preserving null at every gamma).
Source research note: `d:/AI/hd-instrument/notes/research_2x_revival_v2e_self_mapping_HF_2026-06-23.md`
Pause state: respect `data/orchestrator_paused.flag` at dispatch time.

**Per [[feedback-no-experiment-design-in-prompts]]:** research does NOT specify cell mechanics, queue choice, smoke parameters, or HARD-band tuning. exp_dev owns those. Below are anchor candidates with substrate-product reading + tier hint + why-now. exp_dev is empowered to re-rank, descope, or substitute mechanism per its own contract.

---

## Anchor candidates (rank-ordered)

### Anchor 1: enc_dual_gain_softhebb_vs_fpe_v1 (PREREQUISITE — already filed)

- **Pointer:** `notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md` (sister 5x drill, pre-registered cell design)
- **Substrate-product reading:** encoder is the load-bearing bottleneck for BOTH Phase 1 self-mapping AND Path A bigram-gap closure. Highest-leverage single dispatch in current arc.
- **Tier hint:** chain-grade-targetable if any non-bipolar arm HARD_PASSES cleanup OR BPC.
- **Why-now:** v2e HARD_FAIL diagnosis (this hand-off) confirms encoder substitution is forced not optional. enc_dual_gain is laptop-CPU cheap (~30-60 min) and resolves the dependency for everything downstream including the next anchor here.
- **Note:** this anchor was already in the queue from the sister 5x drill. The 2x revival drill ESCALATES its priority — it's now the prerequisite for self-mapping revival, not just a dual-gain candidate.

### Anchor 2: v2f_self_map_softhebb_encoder_smoke (POST enc_dual_gain HARD_PASS)

- **Pointer:** `notes/research_2x_revival_v2e_self_mapping_HF_2026-06-23.md` (this drill's HARD_PASS/HARD_FAIL band section)
- **Mechanism class:** swap v2e encoder from `char_trigram_encoder.py` to the winning arm of enc_dual_gain (SoftHebb-3-layer or FPE-phase); keep modularity-Z + LRG + engram-allocation discriminators unchanged from v2e.
- **Substrate-product reading:** validates whether encoder upgrade breaks the bit-degeneracy observed in v2e (REAL and SHUF Q-sweeps were bit-identical at every gamma). Smoke result decides whether to dispatch FULL.
- **Tier hint:** chain-grade-targetable on HARD_PASS (with the v2f-FULL follow-on).
- **Why-now:** conditional on Anchor 1 HARD_PASS. Sequence the dispatch — do NOT pre-queue v2f before encoder dual-gain lands.
- **Discriminator (load-bearing):** Z_real(gamma*) - Z_shuf(gamma*) >= 1.0 at smoke (n=30) on at least one gamma. If yes, dispatch FULL. If no, encoder upgrade was not enough — pivot to Anchor 3.

### Anchor 3 (conditional): adjacency-construction-pivot (POST v2f HARD_FAIL)

- **Pointer:** TBD — would require a fresh research drill if v2f HARD_FAILS with the upgraded encoder
- **Mechanism class:** abandon Hebbian-KG + 2-hop-Jaccard adjacency; build adjacency from direct atom-vector cosine similarity threshold OR cleanup-attractor basin overlaps OR attention-style soft-adjacency.
- **Substrate-product reading:** if encoder upgrade STILL produces a bit-degenerate graph under 2-hop-Jaccard, the Jaccard composition itself is the issue. This would be a 6th attempt at self-mapping; requires fresh research drill before dispatch.
- **Tier hint:** speculative; do NOT pre-queue.
- **Why-now:** ONLY if v2f HARD_FAILS. Otherwise this anchor stays unfilled.

### Anti-anchor: DO NOT dispatch v2e-FULL at n=150 with current encoder

The smoke v2e is bit-degenerate (REAL Q = SHUF Q at every gamma, exactly). n=150 cannot create informative structure where the encoder + Jaccard composition produces a degree-rank-1 adjacency. Dispatching v2e-FULL would burn ~3hr remote_cpu to confirm a null that the smoke already proves. Per [[feedback-no-busy-work]] and [[feedback-substrate-mine-capacity-before-extrapolating]]: substrate-mine first, then dispatch.

---

## Context pointers (paths only, not summaries)

- `d:/AI/hd-instrument/notes/research_2x_revival_v2e_self_mapping_HF_2026-06-23.md` — this revival drill (WHY-failed diagnosis + revival angle)
- `d:/AI/hd-instrument/notes/research_5x_deeper_substrate_self_mapping_gap_2026-06-23.md` — parent 5x drill that designed v2e
- `d:/AI/hd-instrument/notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md` — sister encoder dual-gain drill (Anchor 1 cell design)
- `d:/AI/hd-instrument/notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md` — prior encoder-side ceiling research
- `d:/AI/hd-instrument/data/exp_v2e_modularity_Z_LRG_self_mapping_v1_smoke/metrics.json` — load-bearing data (bit-identical REAL vs SHUF Q sweeps)
- `d:/AI/hd-instrument/data/exp_substrate_self_map_v2d_discriminator_corrected_v1/metrics.json` — prior FULL HARD_FAIL with v1-family confound
- `d:/AI/hd-instrument/hdlab/char_trigram_encoder.py` — current encoder (to be replaced)
- `d:/AI/hd-instrument/hdlab/iterative_attractor.py` — engram-allocation primitive (not broken; awaiting informative input)
- `d:/AI/hd-instrument/hdlab/kg_traversal.py` — KGStore primitive
- `d:/AI/hd-instrument/hdlab/multi_hop.py` — multi-hop primitive (composes with KGStore)

---

## Contract

- exp_dev owns cell mechanics, smoke parameters, queue choice (laptop CPU for Anchor 1 ~30-60 min; remote_cpu for Anchor 2 FULL ~3hr), schema-vet, formula-selftests, and HARD-band tuning.
- exp_dev MAY descope or substitute mechanism per its own contract.
- exp_dev MUST honor `data/orchestrator_paused.flag` at dispatch time.
- exp_dev MUST commit prereg notes to origin/main BEFORE remote dispatch (per [[feedback-commit-prereg-notes-before-remote-dispatch]]).
- exp_dev MUST verify the encoder dual-gain HARD_PASS arm before dispatching Anchor 2 (sequence dependency).

## Autonomy declaration

Research dispatches THIS hand-off as advisory. exp_dev is empowered to:
- Re-rank anchors per its own pre-dispatch verify-the-referent gate (per [[feedback-fix26-predispatch-verify-the-referent-gate]])
- Substitute SoftHebb arm with FPE arm or vice-versa if the dual-gain result indicates
- Descope Anchor 2 to smoke-only and stop if smoke shows no encoder improvement
- Defer if pipeline is at the ≤3-in-flight ceiling (per [[feedback-fix14-spawn-budget]])

Return-of-finding contract: post-dispatch metrics flow to verdict_handler; verdict_handler updates cap_map; research consumes verdict via monitor and decides whether to file a follow-on drill (Anchor 3 conditional path).
