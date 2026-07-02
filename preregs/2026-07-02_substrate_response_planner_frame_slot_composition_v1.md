# Pre-reg — substrate_response_planner_frame_slot_composition_v1

**Filed:** 2026-07-02 evening (Director main-thread pre-reg draft during Stage 1 closure lane)
**Author:** Director
**Sister primitive:** M1.9 SemanticParser CG'd today (commit ab4a06f56 cell + c0ef97b5b hdlab extraction)
**Design note:** `notes/research_M1_10_response_planner_primitive_design_2026-07-02.md`
**Anchor:** `substrate_response_planner_frame_slot_composition_v1`

## Framing discipline (LOAD-BEARING)

Per `feedback_never_narrate_synthetic_HD_bundles_as_english_language_capability_USER_2026-07-02`: this cell is a MECHANISM PROOF. Inputs are pre-composed HD bundles from known codebooks (integer indices → HD lookup + bind). NO tokens, NO characters, NO English. Substrate does NOT understand language. Output is an HD that a future (unbuilt) Stage 4 decoder would translate to text.

The primitive being tested: given (intent_id, slot_ids) — same schema as M1.9 OUTPUT — construct a response_hd via:

```
frame_hd = frame_codebook[frame_lookup(intent_id)]     # retrieve response template
role_slot_binds = [bind(role_key[r], slot_dict[r][slot_ids[r]]) for r in range(N_ROLES)]
response_hd = frame_hd + INTENT_WEIGHT * intent_hd + sum(role_slot_binds)
```

## Regime constants

- N_DIM = 8192
- N_INTENTS = 50 (matches M1.9 CG regime)
- N_ROLES = 5 (matches M1.9 K=5)
- SLOT_DICT_SIZE_PER_ROLE = 20 (matches M1.9)
- N_FRAMES = 25 (response templates; 1 frame per 2 intents on average — many-to-one)
- INTENT_WEIGHT = 8.0 (matches M1.9)
- N_test = 200 per seed
- Seeds = [11, 17, 23] (matches M1.9 seed schedule)
- Storage strategy: **SHARDED** (per-role slot_dicts + frame_codebook; per USER-locked storage-strategy CG_META)

## Arms (5 arms × 3 seeds = 15 units expected)

| Arm | Mechanism | Role |
|---|---|---|
| ARM_TEMPLATE_ONLY | `response_hd = frame_hd` (no slot fill) | Baseline: template-selection floor |
| ARM_COMPOSE_ONLY | `response_hd = intent_hd + Σ_r bind(role_key[r], slot_dict[r][slot_ids[r]])` (no frame) | Baseline: pure-composition floor |
| ARM_HYBRID | `response_hd = frame_hd + INTENT_WEIGHT*intent_hd + Σ_r bind(...)` | LOAD-BEARING: recommended M1.10 mechanism |
| ARM_SHUFFLED_RESPONSE_ROLE_KEYS | ARM_HYBRID but role_keys cyclic-derangement-shuffled before bind | Sanity control: mechanism collapse expected |
| ARM_M19_ROUNDTRIP | `response_hd = M1.10_HYBRID(intent, slots)`; parse back via M1.9 SemanticParser; check recovery | STRONGEST proof: bind-unbind roundtrip fidelity |

**Cardinality target:** `EXPECTED_N_UNITS = 5 * 3 = 15`; `arms_differ_verified` required.

## Metrics per arm × seed

- `frame_match`: fraction of test queries where nearest-frame-in-codebook to response_hd == ground-truth frame_id
- `slot_fill`: mean per-query fraction of correctly-recovered slot_ids (via cleanup-then-argmax against per-role slot_dict)
- `intent_recovered`: fraction where nearest-intent-in-codebook to response_hd (via k_NN direct-cleanup, mechanism-symmetric to M1.9's intent-cleanup) == ground-truth intent_id
- ARM_M19_ROUNDTRIP-only: `roundtrip_intent`, `roundtrip_slot_fill` (from re-parsing response_hd through M1.9 SemanticParser)

## HP bands (HP_SCOPE: LOAD-BEARING on ARM_HYBRID + ARM_M19_ROUNDTRIP)

**HARD_PASS (CG target):**
- ARM_HYBRID frame_match ≥ 0.85
- ARM_HYBRID slot_fill ≥ 0.80
- ARM_M19_ROUNDTRIP roundtrip_intent ≥ 0.80 AND roundtrip_slot_fill ≥ 0.80
- ARM_HYBRID slot_fill − ARM_TEMPLATE_ONLY slot_fill ≥ 0.30 (compositional lift over template-alone)
- ARM_SHUFFLED_RESPONSE_ROLE_KEYS slot_fill ≤ 0.20 (mechanism-collapse control)
- All 3 seeds independently HP; cv across seeds < 0.10 on ARM_HYBRID slot_fill

**HARD_FAIL (falsification):**
- ARM_HYBRID frame_match < 0.70 OR
- ARM_M19_ROUNDTRIP roundtrip_slot_fill < 0.60 OR
- ARM_SHUFFLED > 0.30 (role-binding NOT load-bearing)

**MIDDLE_BAND:**
- Any seed lands intermediate; roundtrip in [0.60, 0.80); or lift over template in [0.10, 0.30)

## Sanity + integration gates

- ARM_TEMPLATE_ONLY frame_match ≥ 0.95 required — templates should be trivially recoverable when there is no compositional work. If < 0.95: SCHEMA_BROKEN halt.
- ARM_COMPOSE_ONLY roundtrip_slot_fill ≤ ARM_HYBRID roundtrip_slot_fill + 0.03 required — frame retrieval must NOT hurt vs pure composition (would indicate integration bug); if compose-only > hybrid + 0.03: HARD_FAIL integration bug.

## Substrate primitives called

- `hd_bind`, `hd_bundle` (composition)
- `k_NN_lookup` (frame cleanup + intent cleanup + per-role slot cleanup)
- `hdlab.semantic_parser.SemanticParser.parse_batch` (for ARM_M19_ROUNDTRIP; imports the just-extracted M1.9 module at commit c0ef97b5b)
- No hdlab.intent_classifier (bypassed per HEBBIAN_REGIME_NARROW META candidate finding)

## CELL-TEMPLATE MANDATORY compliance

- `arms_differ_verified: True` (5 arms × 3 seeds → 15 distinct per-arm-seed digests)
- `final_metrics_atomicity: tmp_replace` (via `_seed_checkpoint.write_metrics`)
- `except SystemExit: raise` BEFORE `except Exception`
- `crlb_n/a`: "compositional binary discriminators; chance floor 1/50 = 0.02 intent, 1/20 = 0.05 slot-per-role"
- `baseline_in_band`: ARM_TEMPLATE_ONLY expected 0.95 frame / ~0.05 slot; ARM_SHUFFLED expected ~chance
- `discriminator_survives_scale`: N_DIM=8192 (matches CG regime; discriminator smoke at full-N)
- HP strictly above floor: 0.85 frame vs 0.02 floor; 0.80 slot vs 0.05 floor; 0.80 roundtrip vs 0.02
- `HP_SCOPE`: ARM_HYBRID + ARM_M19_ROUNDTRIP load-bearing; ARM_TEMPLATE_ONLY / ARM_COMPOSE_ONLY / ARM_SHUFFLED report + control
- `cardinality_ok`: 15 units expected
- `calibration_check`: default_ok (no learned parameters; deterministic bind/unbind)
- `progress_logging: print_flush_true`
- `start_marker + _heartbeat.jsonl + crash_diagnostic`: standard wiring

## Compute architecture

- (a) batched-CPU-torch or NumPy vectorized (bind/unbind at N=8192 fits in CPU easily; no GPU needed at n_test=200 × 5 arms × 3 seeds)
- Per-seed wall estimate: ~10-30s (M1.9 FULL was 15.35s wall for 3 seeds; M1.10 has more arms but similar operations)
- FULL total: ~1-3 min wall
- Route: `remote_cpu_queue` (single dispatch, no chunking); FULL wall << 1800s timeout

## Dispatch prerequisites

1. Stage 1 substrate-KB closure completes (testbed af135622 in flight)
2. hdlab/semantic_parser.py commit c0ef97b5b on origin (VERIFIED — pushed earlier)
3. Pre-reg SCHEMA-VET by Skunkworks (this file)
4. Smoke gate on local_cpu (USER-locked SMOKE_ONLY_LOCAL_CPU 2026-07-01)

## Post-verdict routing

- **HARD_PASS at CG:** author `hdlab/response_planner.py` following M1.9 SemanticParser extraction pattern (10 selftests, INPUT REGIME discipline, ASCII-only). Cortex primitive stack: M1.3-M1.9 + M1.10 (M1.11 in parallel). Compose M1.9 + M1.10 into cortex.py Phase 4 wiring (separate follow-up).
- **HARD_FAIL:** file CG_HONEST_NEGATIVE; re-scope mechanism; consider (a) alternative to hybrid (transformation-style option (b) from design note), (b) larger N_FRAMES, (c) intent_hd weight tuning.
- **MIDDLE_BAND:** file MM_TENTATIVE; propose v2 changes (scale N_test, tune INTENT_WEIGHT, add richer slot binding).

## Composability + META candidates

- Composes with M1.9 SemanticParser (roundtrip arm) → potential composed META atom if M1.9 + M1.10 both CG at K=5.
- Extends storage-strategy CG_META further (frame_codebook + per-role slot_dicts both sharded).
- No new META candidate at v1 (mechanism is direct sister to M1.9).

## Priors (composable atoms already CG'd today or prior)

- M1.9 SemanticParser CG (commit ab4a06f56 cell; c0ef97b5b hdlab)
- SCALE_FREE_PHYSICS_LAW META (CG_META today, commit 9d3e2b3cb + earlier)
- TOPOLOGY_FREE_PHYSICS_LAW META (CG_META today, commit 0e2a4943e)
- Storage-strategy CG_META (SHARDED for compositional cells)
- HRR bind/unbind primitives (long-standing CG)

## Estimated timeline

- Cell authoring: ~30-45 min (hdi_exp_dev)
- Smoke on local_cpu: ~5-15 min
- SCHEMA-VET (this pre-reg): ~5 min (Skunkworks)
- FULL dispatch on remote_cpu: ~1-3 min wall
- Landed-VET: ~5 min (Skunkworks)
- If CG: hdlab extraction: ~30 min

Total: ~1.5-2 hours from Stage 1 closure to M1.10 primitive availability.
