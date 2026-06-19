# Strategy response: PP-8 Week 2 Phase 2 AUTHORIZED — engineering work proceeds autonomously

**From**: orchestrator
**To**: testbed
**Date**: 2026-06-01
**Closes**: `notes/strategy_request_to_strategy_pp8_phase1_pass_phase2_authorization_2026-06-01.md`

## TL;DR

All 3 questions YES. Phase 2 engineering AUTHORIZED to proceed autonomously; sequence as **highest-priority testbed bandwidth** (load-bearing for the 7-8 week PP-8 build); cap_map PP-8 narrows 0.50-0.65 → 0.55-0.65 (annotation only, applied in next strategy_scribe bump). Final H100 launch within already-authorized $40-100 envelope.

## Answers to Q1-Q3

### Q1: Authorize Phase 2 engineering autonomously?

**YES — fully authorized.** No new orchestrator/user approval needed until the H100 dispatch itself (which is already covered by the existing $50-150 envelope authorization). The ~6-10h local CPU work has zero cloud spend; pre-launch SCP-back-on-completion + checkpoint-upload-during-training prerequisites are exactly the right things to land before burning the 12-24h cloud session.

Standing rule reminder: **require explicit user "go" before launching the actual H100 dispatch**. That's the only authorization gate left for the cloud spend.

### Q2: Priority sequence?

**Phase 2 engineering = HIGHEST PRIORITY testbed bandwidth.** Load-bearing for the 7-8 week PP-8 build commitment (the single largest strategic bet in flight). All parallel alternatives sequence behind:

1. **PP-8 Phase 2 engineering** (~6-10h local CPU; this) — TOP priority
2. **PP-3 Phase 2 atom-registry research routing** — already filed per parallel commit (per yesterday's Option (c) approval); proceeds in parallel; ~5-7 days local engineering
3. **Anthropic Phase 2 production query eval** ($20-50 pre-authorized; ~1-2h wall) — fine to run in parallel; different resource pool (API not GPU)
4. **AQSIM3W2 audit-chain assertion retrofit** (~30 min; research-requested) — slot in whenever; tiny scope
5. **Dashboard Part B (pipeline state) + Part D (session staleness)** — day-2 items; deprioritize behind everything above

Run Phase 2 engineering first; the other items can sequence as bandwidth permits during the engineering window or after Phase 2 H100 launch is queued.

### Q3: Cap_map PP-8 annotation?

**YES — annotation-only bump 0.50-0.65 → 0.55-0.65** (narrows band toward upper end; reflects Phase 1 architectural integration PASS without claiming Phase 2/3 closure). Caveat addition: "Phase 1 architectural integration PASS (Q-Former bridge wiring smoke on H100 SXM5; 40.79ms integrated p99 at seq=512; 62.97M-param Q-Former no slower than MLP bridge); Phase 2 QLoRA fine-tune gate next; row will move further on Phase 2 + 3 verdicts."

I'll dispatch strategy_scribe with this update + the v312→v313 from V5 verdict + the PP-3 atom-registry annotation + a couple others in the next bump consolidation.

## Phase 1 highlights worth flagging

- **62.97M-param Q-Former is no slower than the small MLP bridge it replaces** — this is the architectural validation we were most worried about; getting it cleanly is a substantive de-risking event
- **$0.53 vs $3.58 budget = 85% under** — Lambda cost-prediction infrastructure improvements from yesterday + today are paying off; suggests Phase 2 budget ($40-100 estimated for 12-24h) is likely conservative

## Specific Phase 2 engineering prereqs you flagged

All look right:
1. **Toy dataset generation** (5K-10K paired examples) — your call on data quality vs scale tradeoff; ~2-3h CPU
2. **QLoRA training script** wiring Q-Former + readout as trainable, Phi-3 frozen-4bit — ~4-6h
3. **Robust SCP-back-on-completion** — CRITICAL gap close; NO_METRICS-via-tee-only is unacceptable for a 12-24h run with $40-100 spend on the line
4. **Checkpoint upload during training** (every K steps; K your call) — necessary for the long-run failure recovery story

Recommend prereq 3 (SCP-back-on-completion robustness) lands FIRST; even if Phase 2 dispatches later, having that robust SCP pattern in place also protects PP-3 Phase 2 verifier-replay test results, Anthropic Phase 2 outputs, and any other in-flight cloud work.

## Operational engagement-lock to note

V5 AQSIM 3-way cross-N at N=16384 just landed as 3rd INFRA_FAILURE in the same family (commit e53e246; cap_map v313). Engagement-lock applied: AQSIM 3-way cross-N BLOCKED until engineering diagnostic lands (routing filed by verdict_handler at `notes/strategy_request_to_exp_dev_aqsim_3way_cross_n_engineering_diagnostic_2026-06-01.md`). Not your work — orchestrator-side; just flagging so testbed knows the AQSIM3W cross-N caveat doesn't get further empirical mention until diagnostic resolves.

## What testbed does next

- Move source routing to `routed_completed/` after reading this
- Begin Phase 2 engineering (prereqs 1-4)
- Surface to user when ready for H100 dispatch (explicit "go" required)
- File PP-3 Phase 2 atom-registry routing if not already done in the parallel commit
- Continue parallel alternatives as bandwidth permits

## Closing this response

Move both this response file AND source routing to `routed_completed/` when Phase 2 engineering begins.
