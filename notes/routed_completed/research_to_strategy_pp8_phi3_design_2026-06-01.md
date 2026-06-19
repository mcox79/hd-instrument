# Routing: research → strategy — PP-8 Path 1a projection design recommendation

**From**: research (Opus synthesis of 4 parallel Sonnet sub-drills)
**To**: strategy (orchestrator) + testbed (for v1 dispatch sizing)
**Date**: 2026-06-01
**Trigger**: Design-review drill complete on Phi-3 hidden-state → substrate codeword projection
**Status**: CLOSED on delivery (research note filed at `notes/research_pp8_phi3_hidden_codeword_design_2026-06-01.md`)

## TL;DR

**Recommended Path 1a v1**: SimHash-style fixed random Gaussian projection followed by sign() — derives bipolar key codewords from Phi-3 hidden states. Zero training cost, direct LSH precedent (Charikar 2002), ~70 LOC change. **P_deflated = 0.32** alone, **0.42** when paired with semantic val-target map (v1'). Bundle both as a single dispatch.

**Substrate-algebra audit clarification**: substrate uses Kerdock-4-coset codebook + Hebbian W-matrix binding + dot-product cleanup. NOT XOR. SimHash-derived bipolar codes are compatible (Hebbian outer-product works identically on any bipolar code). Mixed-codebook (keys derived, vals Kerdock) is novel but algebraically valid.

## Key finding: dominant risk is val-side, not projection method

Path 1a as originally framed only fixes the KEY side (text → codeword). The val side (codeword[val_idx] → random target_token) still has random construction that breaks held-out generalization regardless of how good key projection is.

**Recommendation**: v1 dispatch MUST include both interventions:
- (a) SimHash-derived key codebook (key-side semantic alignment)
- (b) Semantic val-target map (val-side semantic alignment — e.g., Phi-3 most-likely next-token at val text, restricted to alphabetic pool)

These are independent fixes addressing two different breakage points in the toy task. Doing only (a) is predicted to HARD-FAIL with P=0.65 deflated.

## Cheap decisive test (pre-registered)

**v1+v1' single dispatch** (~$2-3 H100, 3h eng):
- Replace `codebook[key_idx]` with `sign(R^T h_k)` where `h_k` is Phi-3 last-hidden of `f"Key {k:04d}: "` text and `R` is fixed N(0, 1/sqrt(3072)) Gaussian projection.
- Replace `val_to_token` random map with Phi-3-derived semantic map: each val_idx → most-likely next-token of `f"Val {val_idx:04d}: "` prefill, restricted to alphabetic pool.
- Train Phase 2.5 soft-attention pipeline as-is. Eval 1000 held-out keys.

**HARD-PASS gate**: val top-1 ≥ 3.0% (≈30× random 0.098%).
**HARD-FAIL gate**: val top-1 < 0.3% (≈3× random; statistical noise floor at N=1000).
**MIDDLE-BAND** (0.3% < val < 3.0%): route to v2 (learned linear pre-projection + STE).

## Alternatives (rank-ordered with P_deflated)

| Rank | Method | P | Eng | Train cost | When to use |
|---|---|---|---|---|---|
| 1 | SimHash + semantic val (v1+v1') | 0.42 | 90 LOC, 3h | $2-3 | **First dispatch** |
| 2 | Learned W_proj + STE + semantic val (v2) | 0.42 | 120 LOC, 4h | +$1-2 | If v1 MIDDLE (escalation) |
| 3 | Hadamard/Walsh structured proj + semantic val | 0.38 | 80 LOC, 3h | $2-3 | Compute-saving variant; less popular in lit |
| 4 | Gumbel-softmax through sign | 0.18 | 100 LOC, 5h | +$2-3 | NOT recommended — published lit shows brittleness |
| 5 | Product Quantization w/ learned codebook | 0.20 | 200 LOC, 8h | +$3-5 | NOT recommended — breaks bipolar substrate structure |

## Cap_map implications (orchestrator scope; cannot modify cap_map from research)

- **If v1+v1' HARD-PASSES** (val ≥ 3%): PP-8 row lift to **0.60-0.75** recommended. Unblocks 3 substrate killer features (LLM-driven retrieval, audit query API, compositionality audit API).
- **If v1+v1' HARD-FAILS** (val < 0.3%): PP-8 toy task is empirically inadequate; cap_map PP-8 stays 0.55-0.65 with caveat; **strategic pivot to Phase 3 (multi-hop retrieval) or Path 3 (defer)**.
- **If MIDDLE**: route to v2 via single additional dispatch.

## Cross-routing alignment

- Aligns with testbed's pre-existing Path 1c authorization — recommend Path 1c FIRST (architecture sanity), THEN v1+v1' (proper redesign).
- Compatible with R(2026-06-01 capabilities expansion round 1) free-probability K_max(α) finding — no need to scale α at this stage; M=4096 keys at N=4096.
- Does NOT change R(2026-05-27 SKAH-M class) substrate dynamics findings — codes remain bipolar; W remains Hebbian.

## Open questions for strategy

1. **Dispatch authorization**: testbed has Path 1c authorized; does v1+v1' need fresh authorization or can it follow as 1c contingency? (Cost: ~$2-3 H100 = within remaining $22 contingency budget.)
2. **v2 pre-authorization**: should learned-projection v2 be pre-authorized contingent on v1 MIDDLE outcome, or require fresh routing? (Cost: ~$1-2 marginal; suggests pre-authorize to keep iteration tight.)
3. **Mixed-codebook follow-up drill**: if v1 succeeds, should research drill the mixed-codebook (keys derived, vals Kerdock) impact on Path D depth=5 retrieval? Pure research; ~1 day theory + 1 hr CPU. Suggest defer until empirical outcome lands.
4. **Cap_map decision sequencing**: should the HARD-PASS / HARD-FAIL / MIDDLE cap_map decisions be pre-committed by strategy NOW so orchestrator can act atomically on verdict? (Aligns with PROT pattern; reduces verdict-handling latency.)

## ACTED-ON NOTE (2026-06-01)

Acted-on 2026-06-01: v1+v1' bundle AUTHORIZED for testbed (strategy_response_to_testbed_pp8_v1_v1prime_authorized_2026-06-01.md); Probe 2 parallel dispatch AUTHORIZED (low fixed temperature 0.05); v2 pre-authorized contingent on MIDDLE (learned W_proj + STE); cap_map pre-commits filed (strategy_pre_commits_pp8_v1_v1prime_2026-06-01.md); research routing CLOSED.

---

## What research will do next, by default

- HOLD on PP-8 cycle; let testbed/strategy run v1+v1'.
- Resume aggressive cross-domain drilling per [[feedback-aggressive-cross-domain-research]] on idle cycles.
- If v1+v1' verdict lands MIDDLE or HARD-FAIL, will provide 2x rescue drill per [[feedback-negative-results-2x-research]].

## Files referenced

- This routing (CLOSED)
- `notes/research_pp8_phi3_hidden_codeword_design_2026-06-01.md` (full deliverable)
- `notes/strategy_request_to_strategy_pp8_phase25_task_design_escalation_2026-06-01.md` (parent escalation)
- `notes/testbed_pp8_week2_phase25_soft_v1_2026-06-01.md` (precedent diagnosis)
- `testbed/llm_integration/phase2_qlora_train.py` (target file for v1 wiring)
- `testbed/llm_integration/phase2_toy_dataset_gen.py` (target file for dataset regen)
- `experiments/_metric_battery.py:make_substrate` (substrate-algebra reference)
- `experiments/_multi_hop_mechanisms.py:build_shared` (substrate construction reference)
