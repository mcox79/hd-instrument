# Strategy -> Exp Dev: post-v158 pipeline routing (queue at 0; fill per [[feedback-pipeline-pacing]])

**Date**: 2026-05-23 ~12:28 EDT
**From**: Strategy session (cycle 178 / v158)
**To**: Exp Dev session
**Trigger**: v158 paired commit per PROT-009 + pipeline queue depth = 0 per [[feedback-pipeline-pacing]]. Two PASS verdicts landed (CROOKS_NOISE_CORRECTED_PASS post-hoc CPU re-analysis + STREAMING_NOISE_ENVELOPE_PASS at FULL); pipeline runner is idle. Orchestrator's first priority is filling the queue.

---

## Strategic context

v158 net effect: both verdicts are envelope EXPANSIONS, not narrowings.

- Cap 1 commercial wedge WIDENS from clean-only (v157) to TIERED noise-tolerance certificate (Tier 1 clean Crooks-FT + Tier 2 Sagawa-Ueda noise-corrected). v157 "narrowing" framing honestly RETRACTED per [[feedback-no-smoke]] as axiom-mismatch artifact.
- Cap 3 Streaming inference noise envelope EXTENDED under bit-flip noise (drift-diffusion NESS robust to realistic perturbation; throughput_ratio >= 0.9 at p in {0.05, 0.10, 0.20} at N=16384).

Strategy v158 chooses the next pipeline picks to:

1. Maintain pipeline depth >= 1 per [[feedback-pipeline-pacing]].
2. Continue envelope-expansion of remaining ✅ caps per [[feedback-strategy-shore-up-capabilities]] item 2.
3. Burn down the stale-row inventory per `notes/audit_dropped_and_review_2026-05-23.md`.

---

## Ranked picks (Strategy preference order)

### Pick 1 (FIRST; CPU exploratory): Online W noise envelope CPU sweep

**Rationale**: Cap 5 (Gap B Online W updates Robbins-Monro+SNAP) is a demonstrated ✅ capability at FULL (cycle 173 v153) but has not been probed under noise. Cap 1 and Cap 3 have now BOTH demonstrated PASS under bit-flip noise at p in {0.05, 0.10, 0.20} (v157/v158 Cap 1 Tier 2 PASS via Sagawa-Ueda + v158 Cap 3 PASS at N=16384). Asking "does Cap 5 Online W also survive bit-flip noise during update?" is the next analogous envelope probe.

**Why CPU exploratory** per [[feedback-pipeline-pacing]]: small-N CPU sweep across multiple noise levels (p in {0, 0.05, 0.10, 0.20}, plus extension {0.30, 0.40} to find the boundary). Cheap (~minutes per cell). The role of CPU exploration is to identify which noise band is the right operating envelope for a deep GPU follow-up. CPU exploration first; GPU depth second.

**Suggested spec**:
- Experiment name: `wave14_online_W_noise_envelope_v1`
- Mode: CPU exploratory sweep
- N: 4096 (CPU-friendly)
- M: matched to v153 Gap B FULL config (Robbins-Monro+SNAP saturation guard)
- noise levels: p in {0.0, 0.05, 0.10, 0.20, 0.30, 0.40}
- n_seeds: 3
- Verdict label semantics:
  - ONLINE_W_NOISE_ENVELOPE_FULL_PASS: 6/6 cells pass online-W retention threshold
  - ONLINE_W_NOISE_ENVELOPE_NARROW: subset pass; boundary p identified
  - ONLINE_W_NOISE_ENVELOPE_KILL: 0/6 noise cells pass
- Wall budget: target <30 min CPU
- Acceptance: define retention threshold matching v153 ONLINE_W_RESISTS_CF protocol

**Output**: noise-band map for Cap 5; informs GPU follow-up choice. Local CPU runner (cpu_runner_local on desktop alive per memory). Remote CPU runner cpu_runner_0 dead since 2026-05-21 -- if you can revive it for parallel CPU throughput, that helps; otherwise local is fine.

### Pick 2 (parallel on GPU; cheap; 5 cycles overdue): wave14_pq_high_resolution_v1 FULL

**Rationale**: This FULL conversion was queued in cycle 172 routing block but has been "still pending FULL conversion" through v153, v154, v155, v156, v157 (5 consecutive cycles per audit D9). It is a cheap GPU run (~20 min) that probes the P(q) substructure at high resolution (200-seed 500-bin). Should ship.

**Reference**: existing experiment file `experiments/exp_wave14_pq_high_resolution_v1.py` per cycle 172 (in untracked files list per git status). If the experiment file exists locally, queue it directly. If it needs re-spec, refer to cycle 171 v151 routing notes.

### Pick 3 (bandwidth-permitting; local CPU + theory): Bet Z.5 vs VAMP-on-chain equivalence check

**Rationale**: Audit Rec 2 (HIGH-LEVERAGE) per `notes/audit_dropped_and_review_2026-05-23.md`. Bet Z.5 (Absorbing Diffusion Ensemble Smoother) is the most concrete stale-candidate row in the queue (13 cap_map versions stale since v144 cycle 160). VAMP-on-chain (cycle 127) rescued multi-hop at FULL via the same posterior-recovery framework. Question: are they structurally the same algorithm in different framing?

**Two-way valuable**:
- If equivalent: close Bet Z.5 as duplicate-of-existing; frees the candidate slot AND provides a re-framing of VAMP-on-chain ("absorbing-diffusion ensemble smoother" framing per arXiv 2507.07586).
- If non-equivalent: confirm Bet Z.5 as strictly stronger primitive with posterior-error certificate + per-codeword variance; justify the 4-6 hr GPU impl.

**Cost**: ~30-60 min local CPU + ~1 hr math derivation. Bandwidth-permitting; Pick 1 and Pick 2 take priority for runner.

**Output**: structural equivalence verdict; either close the row OR confirm strictly stronger axis (per-codeword variance vs aggregate accuracy).

---

## Coordination

- Per [[feedback-pipeline-pacing]] queue depth >= 1 at all times. Pick 1 (CPU sweep) is the fastest fill; ship that FIRST, then Pick 2 on GPU in parallel.
- Per [[feedback-strategy-shore-up-capabilities]] item 2 (expand existing capabilities): all three picks fit (Pick 1 expands Cap 5; Pick 2 closes a long-pending observability probe; Pick 3 closes a stale readout candidate).
- Per [[feedback-no-smoke]]: v157 "narrowing" framing has been honestly retracted at v158; Cap 1 SLA actually widened. Strategy keeps the substrate-product narrative honest.

## Pending engineering blocker

- Bet A continual-edit at N>=16384 is HARD-GATED (v156) pending `build_initial_W` refactor (bf16 matmul or chunked allocation along M axis). Exp Dev pickup of this engineering work is a separate routing track; not in this v158 pipeline routing because it is engineering not exploration. If you have bandwidth for either the refactor OR a Pick (1/2/3), favor the Picks; the hard-gate is non-urgent (Bet A at M_init=8192 N=65536 ✅ already validated as the rescued operating point).

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
