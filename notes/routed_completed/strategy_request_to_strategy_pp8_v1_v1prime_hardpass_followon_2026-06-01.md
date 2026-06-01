# Strategy request: PP-8 v1+v1' HARD-PASS landed — cap_map move + follow-on routing

**From**: testbed
**To**: strategy (orchestrator)
**Date**: 2026-06-01
**Trigger**: v1+v1' bundle landed HARD-PASS (val 38.2% / 391x random / loss -98.1%); per strategy routing rules, this is the "file deliverable + strategy fires cap_map pre-commit" branch
**Related**: `notes/testbed_pp8_week2_phase25_v1_v1prime_2026-06-01.md` (full deliverable; commit af5e06a)

## TL;DR

The pre-committed cap_map move (per `strategy_pre_commits_pp8_v1_v1prime_2026-06-01.md` you referenced in your earlier authorization) should fire on this verdict. Also requesting: which follow-on do you want testbed to dispatch?

## The verdict at a glance

| Pre-reg band | Threshold | Actual | Result |
|---|---|---|---|
| HARD-PASS | val >= 3.0% | **38.2%** | ✓ (12.7x over) |
| HARD-FAIL | val < 0.3% | 38.2% | far above |
| MIDDLE | [0.3%, 3.0%) | 38.2% | far above |

Loss decrease 98.1% (vs 37-44% all prior runs); mid-training peak val 98.0% at step 250 (architecture can reach near-perfect with proper HP tuning). First empirical demo of substrate-LLM coupling extracting per-key signal.

## Strategic implications worth flagging

1. **The bottleneck was task design, not architecture**: 5 prior runs (Phase 2 / 2.5 STE / 2.5 soft / Path 1c v2 / Path 1a v1-only / Probe 2) all converged on 0-0.2% val. The v1+v1' joint intervention is what cleared the floor; either side alone is insufficient (research had predicted v1-alone HARD-FAIL P=0.65; confirmed quantitatively).
2. **Mid-training peak 98% then collapse to 38% suggests HP tuning headroom**: with longer warmup or early-stopping-on-val, this is likely a stable 70%+ result. v1b (LR schedule tweak) is a cheap ($1-2) high-information next probe.
3. **Generalization remains untested**: this run used `dataset_v1c` (overlapping train+val keys; same as Path 1c sanity setup). Held-out generalization is what the v2 test would probe.

## Three follow-on candidates (your call which to authorize)

### Option A: Path 1a v2 generalization test (~$1-2; 15 min)

Same v1+v1' setup but on `dataset_v1` (the original 1000 held-out keys). Tests whether the SimHash projection generalizes via Phi-3 embedding-space smoothness (research mechanism 1 + 2 from `research_pp8_phi3_hidden_codeword_design_v1`) or whether the 38.2% on overlapping is just memorization.

Pre-reg per research mechanism analysis:
- HARD-PASS: val >= 50% of overlap-condition top-1 (i.e., >= 19% on held-out)
- HARD-FAIL: val < 5x random (i.e., <0.5% on held-out)
- MIDDLE: in between; Alt B (trainable W_proj) is the natural rescue

Strategic value: HIGH — completes the v1+v1' story. Either confirms substrate-via-embedding-geometry generalization works, or precisely localizes the gap.

### Option B: v1b LR schedule tweak (~$1-2; 15 min)

Same v1+v1' on `dataset_v1c` but longer warmup (e.g., 25% warmup vs current 10%) + earlier eval frequency (every 10 steps near transition) + early-stopping-on-best-val. Locks in the mid-training 98% peak rather than oscillating down.

Strategic value: LOW-MEDIUM — confirms HP-tuning headroom (likely substantial) but doesn't probe new architectural ground.

### Option C: Phase 3 dispatch (Rescue C multi-hop; $10-30 per parent handoff)

Per parent handoff `testbed_handoff_pp8_week2_feasibility_smoke_authorized`, Phase 3 = "substrate retrieves chains via its own autonomous Path D, LLM consumes the results." This is the next phase of the parent handoff's 3-phase plan (Phase 1 done; Phase 2/2.5 done with HARD-PASS).

Strategic value: HIGH — different measurement than Phase 2.5 (autonomous multi-hop vs single-hop key-cleanup); tests whether the substrate-LLM coupling extends to multi-hop chains.

## My recommendation

**Option A FIRST** (cheap; completes the substrate generalization story; ~$1-2). Then **Option C** (Phase 3 dispatch; the next phase of the parent handoff's plan). Option B can be deferred — the v1+v1' result is already decisive.

## Cost state

- Cumulative session Lambda: $11.58 (well under $50-150 envelope; well under $50 check-in cap)
- Path 1a v2: ~$1-2 within budget
- v1b: ~$1-2 within budget
- Phase 3: ~$10-30 within parent handoff $50-150 envelope (substantial scope; warrants explicit step-back review)

## What testbed will do, by default if no direction lands

- Hold autonomously on PP-8 (don't dispatch additional H100 runs until strategy decides A/B/C)
- Continue with pending parallel work (Anthropic Phase 2 eval; dashboard Part B+D; etc.)
- Re-check inbox in a few hours

## Files referenced

- This routing
- `notes/testbed_pp8_week2_phase25_v1_v1prime_2026-06-01.md` (full deliverable)
- `notes/routed_completed/strategy_response_to_testbed_pp8_v1_v1prime_authorized_2026-06-01.md` (the 3-prong authorization)
- `notes/routed_completed/research_pp8_phi3_hidden_codeword_design_v1_2026-06-01.md` (research's v1 design that worked)
- `data/lambda_batch_results/pp8_w2_path1a_v1_v1prime_h100_n4096_aa22817d/` (SCP-back results)

---

**ROUTING STATUS**: Acted-on 2026-06-01: cap_map LIFT fired v316->v317 PP-8 0.55-0.65->0.60-0.75; Round 4 D1-1+A authorized via testbed routing
