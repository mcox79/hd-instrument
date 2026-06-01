# Strategy pre-commits: PP-8 Phase 2.5 v1+v1' verdict-conditional cap_map decisions

**Date**: 2026-06-01
**Filed by**: strategy_scribe (on behalf of orchestrator)
**Trigger**: PP-8 Phase 2.5 Path 1a v1+v1' dispatch authorized; pre-commits filed per PROT pattern to allow atomic verdict_handler application on verdict landing.
**Purpose**: This is a STRATEGIC PRE-COMMIT DOCUMENT -- it does NOT mutate the cap_map (cap_map only changes on verdict). verdict_handler reads this file when v1+v1' or Probe 2 verdicts land and applies the matching decision atomically.

**HONEST 300 UNCHANGED. LABEL-VS-HONEST 170 UNCHANGED.**
**Cap_map version at time of filing: v314.**

---

## PRE-COMMIT DECISIONS (verdict_handler applies atomically on verdict)

### Scenario 1: v1+v1' HARD-PASS (val >= 3.0%)

**Cap_map action**: PP-8 row LIFT from 0.55-0.65 EXPLORATORY to **0.60-0.75 EXPLORATORY**.

**Annotation to append to PP-8 row**:
> Phase 2.5 Path 1a v1+v1' (Phi-3-derived SimHash keys + Phi-3-derived semantic val targets) demonstrated held-out generalization val >= 3.0% (~30x random 0.098%). Substrate-LLM coupling architecturally validated at toy-task scale. Three substrate killer features unblocked: LLM-driven retrieval (query text -> substrate codeword -> Path D retrieval), audit query API (same pipeline for audit trace), compositionality audit API (multi-hop retrieval via Phi-3 query). Bands lifted 0.55-0.65 -> 0.60-0.75 reflecting architectural validation.

**Downstream routing**: verdict_handler MAY fire exp_dev refill for Phase 3 multi-hop retrieval (Rescue C) if queue depth low and pause flag absent. Research should drill mixed-codebook (keys derived via SimHash, vals Kerdock) impact on Path D depth=5 retrieval.

---

### Scenario 2: v1+v1' HARD-FAIL (val < 0.3%)

**Cap_map action**: PP-8 bands UNCHANGED at 0.55-0.65. NEW CAVEAT appended to PP-8 row.

**Annotation to append to PP-8 row**:
> Phase 2.5 task redesign attempted (Path 1a v1+v1': SimHash-derived key codewords + semantic val targets). Val < 0.3% (statistical noise floor, N=1000). Toy associative-recall task empirically inadequate to demonstrate substrate utility regardless of projection method. Training-dynamics finding (3-point convergence: Phase 2 bypass / STE / soft all val=0%; v1+v1' < 0.3%) closes the toy-task-based Phase 2.5 evidence path. Recommend strategic pivot to Phase 3 multi-hop autonomous retrieval (Rescue C) as next PP-8 evidence approach.

**Downstream routing**: verdict_handler MUST route back to strategy for Phase 3 vs Phase 3 defer decision. Do NOT auto-dispatch next iteration.

---

### Scenario 3: v1+v1' MIDDLE (0.3% <= val < 3.0%)

**Cap_map action**: PP-8 UNCHANGED. CAVEAT ADDITION to PP-8 row noting v2 escalation pending.

**Annotation to append to PP-8 row**:
> Phase 2.5 v1+v1' MIDDLE result (val 0.3-3.0%): substrate-LLM coupling shows signal above noise floor but below substantive-utility threshold. Escalating to v2 (learned W_proj + STE; trainable linear projection instead of fixed R, trained jointly with bridge). Cap_map decision deferred to v2 outcome.

**Downstream routing**: verdict_handler dispatches v2 per pre-authorization (strategy_response_to_testbed_pp8_v1_v1prime_authorized_2026-06-01.md Prong C). No additional routing required for v2 dispatch -- it is pre-authorized.

---

### Scenario 4: Probe 2 PASSES alone (val >= 1.0%) AND v1+v1' HARD-FAILS (val < 0.3%)

**Cap_map action**: PP-8 CAVEAT ADDITION only (no band change).

**Annotation to append to PP-8 row**:
> Probe 2 (low fixed temperature 0.05 + Path 1c architecture) produced val >= 1.0% while v1+v1' HARD-FAILED. Attention sharpness alone produced val signal without semantic key/val alignment -- suggests substrate utility on the toy task IS recoverable via training-dynamics fix rather than full architectural redesign. Defer architectural redesign. Next step: low-temperature + Path 1c v2 architecture as Phase 2.5 iteration, OR carry the finding into Phase 3 as a training-dynamics constraint.

**Downstream routing**: verdict_handler routes back to strategy for next-step decision. No automatic exp_dev dispatch.

---

### Scenario 5: Both v1+v1' and Probe 2 HARD-FAIL

**Cap_map action**: PP-8 CAVEAT ADDITION (bands unchanged; same as Scenario 2 but stronger language).

**Annotation to append to PP-8 row**:
> Phase 2.5 fully exhausted (3-gradient Phase 2/2.5 baseline + Path 1c eval fix + v1+v1' architectural redesign + Probe 2 temperature diagnostic all produce val near random). The toy-task framing is empirically inadequate. Bands held at 0.55-0.65 reflecting Phase 1 architectural integration evidence. Phase 3 multi-hop retrieval (Rescue C) is the only remaining Phase 2.5 evidence path. Recommend pivot.

**Downstream routing**: verdict_handler MUST route to strategy with explicit recommendation to escalate pivot to Phase 3.

---

## NOTES FOR VERDICT_HANDLER

1. The above scenarios are mutually exclusive and cover all pre-reg outcome classes.
2. Cap_map version at time of application will be >= v314 (may have incremented since filing).
3. PP-8 row current bands: 0.55-0.65 EXPLORATORY (as of v314).
4. Annotation must be appended in-place to PP-8 row; cap_map version MUST increment per PROT-007.
5. PROT-008/009 validators MUST pass before commit.
6. Commit message format: `Cap map: PP-8 v1+v1' <outcome> (pp8_v1_v1prime_verdict)`
7. HONEST 300 UNCHANGED. LABEL-VS-HONEST 170 UNCHANGED in all scenarios.

## FILES REFERENCED

- `notes/strategy_response_to_testbed_pp8_v1_v1prime_authorized_2026-06-01.md` (dispatch authorization)
- `notes/research_to_strategy_pp8_phi3_design_2026-06-01.md` (research basis; now routed_completed)
- `notes/research_pp8_phi3_hidden_codeword_design_v1_2026-06-01.md` (full design)
- `notes/substrate_capability_map.md` (target file for verdict_handler edits)

---

**ROUTING STATUS**: Acted-on 2026-06-01: HARD-PASS branch fired; PP-8 LIFT 0.55-0.65->0.60-0.75 applied to cap_map v316->v317
