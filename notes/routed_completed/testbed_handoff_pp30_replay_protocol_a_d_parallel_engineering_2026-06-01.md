# exp_dev hand-off -- PP-30 replay protocol Tracks A+D parallel engineering

Filed-by: strategy_scribe
Trigger: Round 5 killer-feature follow-ons (research_round5_7_drills_synthesis_2026-06-01.md Drill KF-1)
Pause state: ABSENT (all operations proceed normally)
Date: 2026-06-01
Cap_map version at filing: v319

Per [[feedback-no-experiment-design-in-prompts]]: this file names ANCHORS + POINTERS only. Testbed owns implementation details, branch naming, cert-chain test harness design, and eng-time allocation decisions.

## Context

PP-30 (DR-Merkle-randproj-W-verify) row promoted to EMPIRICAL in cap_map v316 (empirical anchor: random-projection detects W corruption >100 bit flips P>0.95 at N=4096, 5-seed unanimous). Research Round 5 design drill (KF-1 per `notes/research_round5_7_drills_synthesis_2026-06-01.md`) identified Candidates A and D as Tier 1 engineering tracks for production replay protocol.

PP-30 seeded-codebook design mandate is LOAD-BEARING (cap_map v319 annotation in PP-15 row and v316 section): 8-byte seed regenerates entire codebook via `sign(hash(atom_id, seed))`; cert chain (400KB) + seed = ~160x backup compression vs 64MB W matrix. All PP-30 candidate implementations (A/B/C/D) MUST implement seeded-codebook as the underlying primitive.

## Anchor candidates (rank-ordered, Tier 1 first)

### Track A: Full Replay + Seeded Codebook (FP32) -- 3-5 eng-days

**Anchor pointer:** `pp30_track_a_full_replay_seeded_codebook_fp32_v1`
**Substrate-product reading:** seeded-codebook enabling production-scale audit replay with ~160x compression; cross-machine FP32 reproducibility establishes the baseline compliance guarantee.
**Tier:** Tier 1 (ship first; gates Tier 2 Candidate B/C)
**Why now:** seeded-codebook is the foundational algorithmic primitive; Track A validates the design mandate empirically; FP32 is baseline before INT32 (Track D).

Pre-reg HARD-PASS: cross-machine FP32 replay produces bit-identical W within 1 ULP relative tolerance over 1000 ops, seeded-codebook regeneration confirmed.
Pre-reg HARD-FAIL: FP32 replay diverges beyond 1 ULP relative tolerance on ANY of the 1000 ops, OR seeded-codebook regeneration fails to produce identical codebook on second call with same seed.

### Track D: INT32 Deterministic Replay -- 7-10 eng-days

**Anchor pointer:** `pp30_track_d_int32_deterministic_replay_v1`
**Substrate-product reading:** bit-exact cross-machine INT32 reproducibility; strongest HIPAA "exact-copy" claim; enables byte-identical audit replay across heterogeneous hardware.
**Tier:** Tier 1 (parallel with Track A; independent engineering track)
**Why now:** HIPAA exact-copy claim is a compliance differentiator no competitor can make; INT32 determinism eliminates floating-point non-associativity concerns.

Pre-reg HARD-PASS: byte-identical INT32 replay produces identical W across at least 2 machine architectures over 1000 ops.
Pre-reg HARD-FAIL: INT32 replay diverges on ANY machine architecture pair for ANY of the 1000 ops.

## Context pointers

- Cap_map PP-15 row (DR cert-chain, includes seeded-codebook design mandate): `notes/substrate_capability_map.md` line ~535
- Cap_map v316 section (PP-30 EMPIRICAL promotion): `notes/substrate_capability_map.md` lines ~4559-4562
- Round 5 synthesis source: `notes/research_round5_7_drills_synthesis_2026-06-01.md`
- Routing source: `notes/strategy_request_to_strategy_round5_killer_feature_followons_2026-06-01.md`
- Cap_map v319 section (this dispatch): `notes/substrate_capability_map.md` PP-30 design mandate annotation

## Contract

**Pre-reg:** each track has explicit HARD-PASS and HARD-FAIL thresholds stated above. Testbed verifies the spec (seeded-codebook design mandate from cap_map) BEFORE coding.

**Self-test:** validate seeded-codebook compression ratio empirically (~160x vs 64MB W matrix) as part of Track A implementation; report actual ratio in verdict_msg.

**Queue routing:** local testbed queue (engineering tracks, not GPU compute experiments). Estimated wall time: Track A 3-5 eng-days, Track D 7-10 eng-days. Tracks A and D are INDEPENDENT -- dispatch BOTH in parallel.

**Ship command:** testbed uses standard queue_add.sh with anchor names above.

**Tier 2 conditional:** Candidate B (Snapshot + Delta Replay, makes N=65536 viable) + Candidate C (Streaming Auditor Protocol, SOC 2 + HIPAA auditor differentiator) are CONDITIONAL on BOTH Track A AND Track D HARD-PASS. DO NOT dispatch B/C until A+D PASS.

**Sub-property activation:** PP-30a streaming auditor protocol (cap_map v319) activates on Candidate C dispatch (conditional on A+D HARD-PASS).

## Autonomy declaration

Testbed is AUTONOMOUS on:
- Eng-time allocation (1 vs 2 engineers on each track)
- Specific git branch naming convention
- Cert-chain test harness design and implementation detail
- Deliverable file pattern (per existing testbed conventions)
- Order of operations within each track (Track A and Track D are independent)
- Whether to run Track A and Track D truly in parallel or sequentially within the 7-10 day window

Testbed is NOT autonomous on:
- Seeded-codebook design mandate (REQUIRED per cap_map v319; not optional)
- Pre-reg HARD-PASS thresholds (stated above; must be pre-registered before coding)
- Dispatching Tier 2 (B/C) before A+D HARD-PASS
