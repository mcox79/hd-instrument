# Prioritized roadmap — R-PRIME + 5 fields + 3-capability agenda + Paths 1/3/4/5

**Filed:** 2026-05-24 by orchestrator (v192 paired commit).
**Inputs synthesized:**
- `notes/research_R_PRIME_directions_2026-05-24.md` (user delivery)
- `notes/research_3_capability_deep_agenda_2026-05-24.md` (user delivery)
- `notes/research_existing_data_analyses_2026-05-24.md` (orchestrator zero-compute analysis; key prior shifts)
- Paths 3 / 1 / 5 already shipping (Tier-1 GPT-quality reframe v191)
- v192 verdicts: Allen-Cahn ❌, REPLAY_NORM null, REALTIME_INFERENCE ✅ (already processed v191)

---

## TOP-5 NEXT SHIPS (rank-ordered)

### Ship 1 — R-PRIME-3 task-pair geometry sweep (HIGHEST LEVERAGE)
**Why #1:** Existing-data analysis surfaced the 35% retA drop between same-corpus (retA=0.954) and diff-corpus (retA=0.600) Bet B variants as the DOMINANT mechanism effect. Larger than any structural ablation (Ablation A=0.821, Ablation B=0.846, EWC=0.736). The user's R-PRIME-3 hypothesis (task-pair-geometry-mediated interference) is BIGGER signal than the also-proposed R-PRIME-2 (MoE M_c) based on existing data.
**Design ownership:** exp_dev (per [[feedback-no-experiment-design-in-prompts]]).
**Shape (pointers only):** 6 deliberately-spaced task-pair distances at fixed (M, K, N); measure retention vs mean cosine; promotion gate r > 0.6 with monotone sign.
**Queue:** GPU likely (modest cost). exp_dev decides queue + ETA.

### Ship 2 — Field-A reservoir-computing Lyapunov spectrum
**Why #2:** New-field probe per user's "5 new fields" delivery + [[feedback-periodic-scope-expansion]] cross-framework drill cadence. Substrate dynamics look like edge-of-chaos echo-state — Lyapunov spectrum + memory-capacity curves are mature and falsifiable. If sub-substrate matches reservoir-computing edge-of-chaos signatures, opens echo-state mapping (large algorithmic payoff).
**Design ownership:** exp_dev.
**Shape (pointers only):** measure substrate Lyapunov spectrum at the operating point used for Bet B retention runs; compare to reservoir-computing edge-of-chaos predictions.
**Queue:** CPU-suitable (matrix-spectrum diagnostic).

### Ship 3 — Bet D analyzer pass at K=32 / K=64 (analyzer-only, near-zero compute)
**Why #3:** Existing perplexity points fit Gap(K) concave-saturating; 2 more K points (K=32 + K=64) extend the curve to 6 points enabling AGS-scaling fit. ANALYZER-ONLY — no fresh model training. Synergistic with Path 3 AGS scaling-law extrapolation already shipping (v191).
**Design ownership:** exp_dev — owner of Bet D analyzer.
**Shape (pointers only):** analyzer pass on existing K=32 and K=64 checkpoints; extract per-token perplexity + frequency-rank histogram + extend Gap(K) curve.
**Queue:** local_queue (analyzer-only).

### Ship 4 — R-PRIME-2 MoE M_c falsifier
**Why #4:** Demoted from "Week 1 priority" by existing-data analysis (R-PRIME-3 dominates); still strong signal-to-noise per user's original analysis. Direct probe of "implicit expert allocation" framing.
**Design ownership:** exp_dev.
**Shape (pointers only):** K-sweep at fixed M_total = 64, K in {2,4,6,8,10,12,14,16}; promotion gate retention(K) = f(M_total/K) within 10% on 4+ K values; KILL = flat or non-monotone.
**Queue:** GPU.

### Ship 5 — Bet M reframe → logarithmic-forgetting fit + literature anchor
**Why #5:** v192 Allen-Cahn rejection consumed the leading Bet M sub-hypothesis. Rescue R1 (logarithmic-forgetting reframe per Wickelgren 1972 / Wixted-Ebbesen 1991) is well-supported by existing data (ret(t) ~= 0.860 - 0.0015*t over t=1..21). This is zero-compute literature-anchor work + closed-form predictor candidate.
**Design ownership:** Research sub-agent.
**Shape (pointers only):** literature drill on power-law forgetting curves; closed-form fit on existing Bet B Allen-Cahn-tsweep data with logarithmic / Wickelgren-power-law forms; promotion gate: rRMS < 5% on the existing t=1..21 sweep + cross-validation on a longer-t rerun.
**Queue:** Research drill (no compute).

---

## ALREADY-SHIPPING (carried from v191 cap_map block)

- **Path 3 — AGS scaling-law extrapolation** (exp_dev hand-off filed v191). Cheapest GPT-quality path.
- **Path 1 — Token-level substrate K=128+ vs GPT-2-small head-to-head** (exp_dev hand-off filed v191). 2-3 day build.
- **Path 5 — Bayes-optimal lower bound via R16+R23+R26 frameworks** (Research drill DISPATCHED v191).
- **Path 4 — Per-document strategic-hedge substrate** (RESERVED).
- **Path 2 — Hybrid kNN-LM-like** (RESERVED).

---

## RESERVED / WEEK-2+ (R-PRIME + 5 fields not in top-5)

| Item | Priority | Why deferred |
|---|---|---|
| R-PRIME-1 PAC-Bayes KL-accumulation floor | 6 | Theoretical drill; gives information-theoretic lower bound; can run in parallel with Ship 1 if Research bandwidth available |
| R-PRIME-5 SSM/HiPPO connection | 7 | Promising but speculative; closed-form fit against HiPPO-LegS / LegT |
| R-PRIME-6 Clifford / TN R5 narrowing | 8 | Operator-spectra probe; needs new diagnostic infrastructure |
| Field-B list-decoding (Johnson bound) | 9 | Maps multi-hop to list-decoding radius; needs Ship 1 result first |
| Field-C statistical-physics-of-inference (replica) | 10 | Closed-form retention predictor via replica ansatz; theoretical |
| Field-D differential-privacy (Renyi-DP composition) | 11 | Reframes replay as DP-SGD; theoretical |
| Field-E neuroscience-replay alt-formulations | 12 | Norm-weighting NULL at v192; novelty/error/uncertainty weightings remain |

---

## TRIAGE NOTES

- **R-PRIME-4 Allen-Cahn**: REJECTED v192. Reframed as logarithmic-forgetting (Ship 5).
- **3-capability deep agenda**: existing-data analyses delivered (v192 V4). Per-capability ship priorities surfaced: Cap 1 = Ship 3 + Ship 1 (multi-hop confound closure); Cap 2 = Ship 1 + Ship 4 + Ship 5; Cap 3 = Ship 3 + Paths 3/1/5 already shipping.
- **Pipeline pacing**: Current GPU queue has backlog; CPU=0. Ship 2 (CPU Lyapunov) + Ship 3 (local analyzer) fill CPU/local. Ship 1 + Ship 4 fill GPU.
- **Pause flag state**: ACTIVE (no pause). Ship dispatches gated only on pipeline-pacing reflex.

---

## DISCIPLINE CITATIONS

- per [[feedback-no-experiment-design-in-prompts]]: roadmap names task SHAPES not parameters; exp_dev / Research own all numerical specs.
- per [[feedback-rehabilitation-after-rejection]]: Bet M Allen-Cahn ❌ has 5 rescues filed inline at v192; R1 logarithmic-forgetting is Ship 5.
- per [[feedback-periodic-scope-expansion]]: Field-A reservoir-computing is the cross-framework drill of the cycle.
- per [[feedback-dont-dismiss-adjacent-methods]]: 5 new fields preserved as queue items even when current evidence doesn't directly demand them.
- per [[feedback-value-creation-not-competition]]: roadmap focuses on capability + math; no product-positioning content.
