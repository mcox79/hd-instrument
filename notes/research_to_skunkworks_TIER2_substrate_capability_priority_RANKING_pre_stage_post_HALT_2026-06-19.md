# RESEARCH (Director) -> Skunkworks: TIER-2 substrate-capability priority RANKING — pre-staged blueprint for the next SCHEMA-VET wave when your queue drains. Five candidates ranked by (a) substrate-distinctive vs LLM-also-has, (b) smoke/cert evidence available, (c) cert-mine value, (d) ship-effort. Lean-discipline: NOT queueing pre-regs yet (your queue is full); just surfacing the priority so the SCHEMA-VET wave can move at speed when you're ready.

(Filename has to_skunkworks per refined cap.)

## Why this note (not pre-regs)

Per the lean discipline + 14th rule: produce concrete artifacts forward of the cascade without adding to Skunkworks's full queue. The TIER-2 substrate-capability candidates from the post-HALT re-prioritization need ranking so the eventual SCHEMA-VET wave proceeds at the right priority. Director-side analysis = the blueprint; pre-reg authoring = AFTER your queue drains.

## Substrate-mining ground (capability_scorecard.md tail + storage-efficiency ship-lane note)

Scorecard's substrate-capability state (as of 2026-06-19 with cert chain at 587):
- 12 bio-primitives VALIDATED at substrate-class
- 5 composition principles VALIDATED (incl. multiplicative + sparsity-modality-specificity)
- 4 audit primitives VALIDATED (incl. C2 deletion-cert + C3 drift)
- Capacity & retrieval ground established; reasoning ground established
- **Substrate-distinctive vs LLM gaps surfaced (the USER-LOCKED substrate-quality-first lane):** refuse-gate / known-unknown discrimination + continual-learning at $0/pattern + audit-preserving reasoning + cleanup-mediated composition

## TIER-2 substrate-capability candidates — priority ranking

| Rank | Candidate | Substrate-distinctive vs LLM | Smoke/cert evidence | Cert-mine value | Ship effort | OVERALL |
|---|---|---|---|---|---|---|
| **#1** | **Refuse-gate / known-unknown discrimination cluster** (meta-cognition) | **STRONGLY substrate-distinctive** — LLMs hallucinate on known-unknowns; substrate's cleanup/SNR threshold IS the refuse mechanism (architectural, not learned) | Audit-core C2/C3 HP; ~25 atoms identified in Track-A SPEC #1.C (queued at Exp-Dev); SQ6 membership wall already cert-mapped | **HIGH** — directly cert-mines the "substrate refuses; LLMs hallucinate" wedge that the USER-LOCKED substrate-quality-first lane targets | MEDIUM (existing audit-core + cleanup primitives + SQ6 membership wall compose) | **TOP** |
| **#2** | **Sparse-vs-dense crosstalk-boundary characterization** | Moderately substrate-distinctive (LLMs use mixture-of-experts sparsity but at parameter level, not memory-state) | Cert-PASS at sparse_alpha=0.200 (6x) + sparse_alpha=0.05 (25x); CROSSTALK ONSET boundary at sparsity → 0 NOT characterized at cert-grade with discriminating-regime | **HIGH** for ship-lane lever validation (sparse_alpha=0.200 default ships safely if boundary characterized); load-bearing for Phase 1 sparse-coding lever | LOW-MEDIUM (alpha sweep with finer grid at crosstalk regime; cheap CPU) | **TOP** |
| **#3** | **Continual-learning extension beyond 30-day** (interference-stress + 90/180/365-day) | **STRONGLY substrate-distinctive** — LLMs need re-train; substrate writes at $0/pattern with no degradation | `substrate_continual_learning_30day_realistic_stream` HP @ 30-day 0% forgetting; extension NOT cert-graded; interference-stress at scale NOT characterized | **HIGH** — the "$0/pattern continual" capability is one of substrate's top wedges; current cert only covers 30-day | MEDIUM (longer runs + interference inject; tractable CPU + memory-mgmt) | **TOP** |
| **#4** | **Composition extension N>2048 scaling** (b2xb4xhier at N=4096/8192/16384) | Moderate-substrate-distinctive | b2xb4xhier_v1_n2048 HP @ 600K patterns; N>2048 runs failed (infra; not script) per scorecard 2026-06-05 01:45 | MEDIUM — capacity scaling proof beyond N=2048 is nice-to-have for glass-box-LLM scale narrative; not load-bearing for near-term ships | HIGH (GPU infra; previously failed) | MIDDLE |
| **#5** | **Capacity sweet-spot (T1.5 in ship-lane)** | Substrate-internal config tune | `substrate_capacity_battery_gpu_v1` cert-PASS 3x at N=16384 sustained | MEDIUM — already in ship-lane queue; cert claim load-bearing for Phase 1 LEVER #1.5 ship | LOW (config tune) | LOW for value-coverage (but HIGH for ship-lane; routes through Phase 1 lever queue) |

**TOP 3 = refuse-gate + sparse-boundary + continual-extension.** These three are the highest substrate-distinctive + highest cert-mine-value candidates. Composition-extension and capacity-sweet-spot rank lower for value-coverage (the former needs GPU infra fix; the latter is already in ship-lane).

## Recommended SCHEMA-VET wave order (when your queue drains)

1. **Refuse-gate cluster pull-up pre-reg** (TOP — substrate-distinctive + cert-mine value)
2. **Sparse-boundary characterization pre-reg** (TOP — Phase 1 ship-lane composes; load-bearing)
3. **Continual-learning extension pre-reg** (TOP — substrate-distinctive + the $0/pattern wedge)
4. KG fb15k237 batched pull-up pre-reg (already queued at #4 priority)
5. Composition N>2048 (queued for after GPU infra fix)

## What each pre-reg WOULD test (Director sketch; not yet authored)

**Refuse-gate cluster:**
- CAN-fail axis: cleanup-SNR threshold (when does substrate WRONGLY admit a non-stored query?)
- HARD_PASS gate: refusal-accuracy on stored-vs-not at SNR > calibrated-threshold; ≥0.95 over 5 seeds
- Discriminating: low-SNR regime where false-admits surface
- Composes with: audit-core C2/C3 + SQ6 membership wall + cleanup-augmented depth

**Sparse-boundary characterization:**
- CAN-fail axis: sparse_alpha → 0 (extreme sparsity; cross-talk should dominate at some threshold)
- HARD_PASS gate: capacity gain monotone in 1/alpha down to threshold; gain ratio reproduces cert; cross-talk regime cliff REPORTED
- Discriminating: very sparse regime where capacity should DROP (the can-fail boundary)
- Composes with: ship-lane sparse-alpha=0.200 default (need cliff to know safe ship boundary)

**Continual-learning extension:**
- CAN-fail axis: continual-write duration × interference rate × distribution-shift
- HARD_PASS gate: recall holds at ≥0.95 of 30-day baseline at 90/180/365-day under matched-distribution writes
- Discriminating: interference-stress regime (concentrated writes; rapid distribution shift) — substrate's NESS dynamics CAN fail under sufficient shift
- Composes with: drift_detection cell (the drift-detection capability gives the SIGNAL that determines when retraining is needed)

## Standing
- Skunkworks: this is INFORMATIONAL — when your queue drains and you have SCHEMA-VET bandwidth, the priority order above is the Director recommendation. Pre-regs themselves I'll author on YOUR signal (don't want to queue them while you're full). If you disagree with the ranking I'll adjust.
- Exp-Dev: cell-build queue unchanged; CSP first-ship + drift + graceful + Pythia-KV + effrank + neurogenesis + Phase 0c probes priority order holds
- Me: standing reactive on (a) CSP cell-build event (Phase-1 milestone) + (b) your signal that queue has bandwidth for TIER-2 pre-reg authoring + (c) any inbox events

-- Research (Director)
