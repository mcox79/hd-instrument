# Routing: orchestrator -- Week 0 Missing 7 FAIL + escalation-recipe layer redirect

**From**: testbed session
**To**: orchestrator (strategy + research dispatch)
**Date**: 2026-05-31
**Type**: deliverable + strategic redirect
**Severity**: HIGH (gates tomorrow morning's Week 1 GO/NO-GO)
**Closes**: `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md`
WEEK 0 MISSING 7 section
**Deliverable**: `notes/testbed_missing7_llm_integration_latency_v1_2026-05-31.md`
(filed earlier this turn)

## TL;DR

Week 0 Missing 7 = **FAIL** at integrated p99 217.7ms (vs 150ms FAIL
threshold; 45pct over).

**The handoff's FAIL escalation recipe targets the wrong layer.** Handoff:
"FAIL = substrate-side throughput is the bottleneck; needs research
drill on async-batched or precomputed-prefix variants BEFORE
committing to Week 1 build."

**Actual per-component breakdown rejects that diagnosis.** Substrate is
fine. LLM is the bottleneck. The substrate-LLM bridge architecture in
the handoff is sound in shape.

Decision required: orchestrator + research re-evaluate Week 1 with the
LLM-stage options surfaced below rather than the substrate-side recipe.

## Honest per-component re-read (Step 0 mandatory before any cap_map move)

Source: `data/testbed_missing7/phi3_integrated_latency_cuda.json`
(5 seeds x 20 reps per seed x 2 seq_lens; bridges Xavier-init untrained;
substrate W populated at M=4096; Path D depth=5 K_paths=500).

At production-reference seq_len=512:

| Component | mean (ms) | p99 (ms) | Share of total |
|---|---|---|---|
| reverse_bridge (R^3072 -> R^4096) | 0.80 | 1.63 | 0.7% |
| substrate_path_d (depth=5, K=500) | 17.07 | 27.47 | 12.6% |
| forward_bridge (R^4096 -> R^3072) | 0.65 | 1.05 | 0.5% |
| **phi3_decode_1tok (4-bit NF4 bf16 compute, attn=eager)** | **159.33** | **198.47** | **91.2%** |
| **Integrated total** | **178.16** | **217.72** | **100%** |

Substrate budget the handoff anticipated (<= 50ms p99) is CORRECT in
shape. Substrate component p99 27ms = 13% of integrated total. Phi-3
component p99 198ms = 91% of integrated total. The shape of the
failure points unambiguously at the LLM stage.

## Where the prior measurements stand (#1, #2, #3)

- **#1 substrate alone**: Path D depth=5 p99 19.78ms PASS (script
  verdict reads "PASS (substrate budget; bridge has 20ms headroom)"
  on RTX 4060 Ti 8GB). Substrate Week 0 budget assumption HOLDS.
- **#2 bridge alone**: round-trip B=1 p99 0.59ms PASS. Bridge cost
  effectively zero at this scale.
- **#3 phi3 alone (per-token)**: seq_len=512 p99 131ms. Script's
  printed verdict "FAIL" at end of run is misleading -- script was
  comparing Phi-3 alone against substrate's remaining budget (29ms)
  rather than against the integrated-query budget. Numbers in JSON
  file are correct; the verdict-band logic in the script needs a
  cosmetic fix (flagged in deliverable; does not affect this routing).
- **#4 integrated** (this measurement): p99 217.7ms FAIL as detailed
  above.

## Why this is a "redirect" not just "FAIL"

The handoff anticipated:
- Substrate component would be the budget-dominant cost (50ms target)
- LLM component would be small (10-50ms per-token assumption from
  published Phi-3 reports)
- FAIL would mean substrate is too slow; rework substrate ops

Actual observations:
- Substrate component p99 = 27ms (under target; LLM-component p99 not
  yet measured at handoff time but the handoff itself flagged "Phi-3-
  mini-4bit on 4060-class GPUs is ~15-40ms/token at seq_len=512;
  likely PASS")
- LLM component p99 = 198ms (5-13x the handoff's per-token assumption;
  substantially over the budget)
- FAIL means LLM choice + hardware is too slow on this specific path;
  substrate-side rework would chase the wrong target

The handoff's escalation recipe is correct for the failure shape it
anticipated. The observed failure has a different shape and warrants
a different escalation.

## Four LLM-stage options surfaced (cost order; testbed evaluation)

Reproduced from the deliverable; testbed will not auto-dispatch any of
these (they all require orchestrator + user budget + possibly research
drill).

1. **Larger / different GPU** (lowest engineering risk; cloud-cost
   gate). Phi-3-mini-4bit on RTX 3090 24GB (fp16, no 4-bit overhead;
   5-10x faster) or H100 (substantially faster) brings per-token
   toward 20-50ms p99 = integrated ~50-80ms p99 = MIDDLE band or
   PASS. Single-config change; ~1 day to validate via cloud rental
   (~$2-5/hr Lambda H100 spot; ~$5-15 total for a 2-3 hour validation
   run). RECOMMEND THIS AS THE GO/NO-GO REVALIDATION PATH.
2. **Different base LM** (quality gate). TinyLlama-1.1B at fp16 on
   8GB would land ~30-60ms per-token = integrated ~60-90ms = MIDDLE.
   Phi-2-2.7B at 4-bit ~50-100ms = MIDDLE-FAIL boundary. Quality
   regression vs Phi-3-mini; needs re-evaluation of the "1-3B is the
   right scale" research-side decision.
3. **Quantization variant** (cheap exploration). AWQ instead of
   bnb NF4 OR pre-quantized `microsoft/Phi-3-mini-4k-instruct-bnb-4bit`
   variant; may run faster than current path on 4060 Ti. ~1 day to
   compare 2-3 variants on same hardware. Modest payoff if any.
4. **Cloud LLM API for inference** (architecture change). Substrate
   stays local; LLM via Anthropic Claude Haiku at ~50-150ms p99.
   Substrate-bridge integration becomes API-call boundary instead of
   in-process prefix-injection. Reuses today's already-validated
   Tier 2b Anthropic client (Phase 1 100% PASS at $0.45 today;
   cumulative session Anthropic spend $0.45). Different architecture
   trade-offs: cost scales with usage; network latency variance; but
   it's a clean fast path for production demos. ~1-2 weeks
   engineering.

**Not recommended** (testbed-side judgment, not auto-dispatched):
- Substrate-side async-batched retrieval (handoff's escalation recipe).
  Would help amortize substrate cost across multiple queries but DOES
  NOT help the LLM-stage bottleneck per-query. Wrong target for
  observed failure mode.

## Research drill candidates for orchestrator dispatch

Suggested but NOT prescribed (orchestrator owns this decision):

- **Drill candidate 1**: "Per-token decode latency for Phi-3-mini-4bit
  and similar-scale models across 4060 Ti / 3090 / H100; what's the
  realistic per-token p99 across base LMs in [1B, 4B] params on
  available hardware tiers?" Estimated 3-5h research; informs option 1
  vs 2 decision.
- **Drill candidate 2**: "Cloud LLM API per-call latency variance and
  cost-per-1000-queries on substrate-augmented workloads; is option 4
  cost-viable at production scale?" Estimated 3-5h research; informs
  option 4 decision and overlaps with Anthropic Phase 2 spec.
- **Drill candidate 3**: "Is the Tier 1.5 VQ-Bottleneck fallback
  (external-reviewer Update 1 in the LLM integration handoff) still
  valuable if the LLM-stage gets faster?" Estimated 2-3h research; the
  VQ-Bottleneck rationale is train/test distribution shift mitigation,
  independent of LLM speed; likely yes still valuable.

## Cap_map implications (testbed view; orchestrator owns the move)

- **PP-8 (substrate-LLM deep-integration) row**: testbed view says
  band UNCHANGED. P_def 0.30-0.45 was conditioned on "8GB local GPU
  path"; the Week 0 FAIL doesn't reduce P_def per se because the
  failure points at LLM-stage not substrate-stage, AND the LLM-stage
  options surfaced have varying budget. Suggest annotation only:
  "Week 0 Missing 7 measurement (testbed) surfaced LLM-stage as the
  bottleneck on 4060 Ti 8GB path; substrate-side budget HOLDS;
  P-band conditional on LLM-stage path TBD (4 options surfaced;
  research drill pending)."
- **PP-5 (latency budget closure) row**: this row was the artifact
  that motivated Week 0 Missing 7. Week 0 result CLOSES the row for
  the specific question "does substrate fit in 50ms?" with PASS.
  Open: "does substrate + bridge + LLM fit in 50ms on 4060 Ti?" with
  FAIL. Suggest row annotation: "substrate-side 50ms budget
  CONFIRMED at 30ms p99 on 4060 Ti 8GB; LLM-stage exceeds budget on
  same hardware; LLM-stage path-dependent re-measurement deferred to
  Week 1 GO/NO-GO LLM-stage choice."
- Other rows untouched.

## Timing

Week 1 GO/NO-GO is "tomorrow morning per orchestrator/research"
correspondence in this session. Orchestrator + research should ingest
this routing before that decision. The 4 LLM-stage options each have
materially different cost / wall-time / engineering profiles; the
choice substantially affects Week 1-6 build commit.

If a quick GO/NO-GO is required without the research drills above,
option 1 (rent a cloud H100 for 2-3 hours and re-run Missing 7 #4
there) is the cheapest decisive revalidation; ~$5-15 spend; could
land before Week 1 commit.

## What testbed will do next (no orchestrator action needed)

- Move this routing file to `notes/routed_completed/` AFTER orchestrator
  acknowledges (next testbed session checks; do not move earlier).
- Idle on Week 0 work; Week 1 testbed engagement depends on
  orchestrator's LLM-stage choice + GO/NO-GO.
- Pending pre-authorized but not-yet-spent: Anthropic Phase 2
  ($20-50) is unblocked; hard-neg full 50K run ($50-350) is gated
  on user-explicit budget approval.
- Cosmetic fixes (N=8192 store, phi3_token_latency.py verdict band)
  do not affect this routing; will be batched in next testbed turn.

## Files of interest

- This routing
- `notes/testbed_missing7_llm_integration_latency_v1_2026-05-31.md`
  (the deliverable)
- 4 measurement JSONs in `data/testbed_missing7/`
- 4 scripts in `testbed/llm_integration/`
- `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md`
  (source handoff, sec WEEK 0 MISSING 7)
- Today's commits: bfd1878 (Lambda v2 scripts), cfc1cd9 (Phase 1
  harness fixes), b1882fa (launch_batch.py stringer), 029f7e8
  (hard-neg infra), 6f53db3 (Phi-3 trust_remote_code fix), a2c4312
  (Phi-3 #4 int-cast fix)
