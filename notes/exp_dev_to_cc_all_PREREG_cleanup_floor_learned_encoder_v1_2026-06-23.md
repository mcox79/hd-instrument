# PRE-REG cell-design note -- cleanup_floor_learned_encoder_v1 (2026-06-23)

**From:** exp_dev (spawn-and-die author)
**To:** cc_all (cert observability; Skunkworks SCHEMA-VET)
**Anchor:** `cleanup_floor_learned_encoder_v1`
**Cell:** `experiments/exp_cleanup_floor_learned_encoder_v1.py`
**Prereg:** `preregs/2026-06-23_cleanup_floor_learned_encoder_v1.md`
**Routing:** local_cpu_queue (numpy CPU; <5min wall full)

## Role (durable cert-trail entry)

Closes BRANCH #3 of cert ledger row 675 META
`T3/META_cleanup_ceiling_shannon_floor_substrate_operating_envelope_sigma_leq_1p0`.

Branches #1 + #2 closed at SYNTHETIC RANDOM-BIPOLAR codebook (N_DIM-INDEPENDENT 512-16384;
M-INDEPENDENT 25-400). This cell extends META scope-test to LEARNED + STRUCTURED codebook
regimes at N=2048 M=200 sigma in {1.0, 1.5, 2.0}.

NOT chain-grade-candidate on own merits. Informer: parent META scope_clause depends on outcome.

## Substrate-product implications (across 3 codebook types)

Discriminator: sigma=1.5 (where random-bipolar fails at ~0.027).

**SCOPE_NARROW outcome** (max(char_trigram, hub_spoke) recall >= 0.20):
- Substrate-product CAN safely operate at sigma=1.5 IF using anisotropic/structured encoder.
- Parent META scope_clause: "applies to random-bipolar codebook only".
- USER strategic bet validated: substrate's learned/structured signal regime evades a noise
  envelope the synthetic regime cannot.
- Implication for substrate-product: char_trigram-encoded HD cleanup is high-noise-tolerant
  in a way random-bipolar isn't.

**CHAIN_GRADE_ELIGIBLE outcome** (ALL 3 arms recall < 0.10):
- Shannon-floor robust across 3 codebook families (RANDOM + LEARNED + STRUCTURED).
- Parent META META_cleanup_ceiling_shannon_floor moves toward chain-grade tier (cert-owner
  Skunkworks deliberates on the tier-up).
- Substrate operating envelope of sigma <= 1.0 holds broadly; product design must respect
  this floor across encoder choices.

**MIDDLE outcome**:
- Nuanced framing required; one arm partial-lifts. Encoder-quality-vs-noise-tolerance map
  is the deliverable atom.

## Pre-reg disciplines applied

- ASCII-only verdict_msg + cell prints (Style discipline)
- Per-seed _seed_checkpoint partials (Long/multi-unit checkpoint discipline)
- atexit + SIGTERM synthesizer (covers any kill mid-run)
- ship_name uniqueness verified (predispatch_check landings=0)
- Pre-flight selftest: 9 sub-tests (T1-T9) including verdict-triplet on synthetic profiles
- Sanity gate at sigma=0.0: all 3 arms must recall >= 0.99 (HARD_FAIL if violated)
- ARM_RANDOM_BIPOLAR at sigma=1.5 N=2048 expected ~0.027 (validates reproduction of parent data point)
- MANDATORY post-landing peek_arm_metrics.py before verdict_msg framing (Fix #28 remediation)

## Cites

- USER 2026-06-22: empowered-to-experiment-where-lit-says-dismissed
- Skunkworks tiering 2026-06-23: META at MEASURED_MECHANISM until 3 branches close
- cleanup_floor_M_scan_v1: branch #2 close (META_DECISION_M_INDEPENDENT)
- cleanup_floor_N_DIM_scan_v1: branch #1 close
- hdlab/char_trigram_encoder.py: substrate-native text-to-HD encoder (deterministic per-trigram)
