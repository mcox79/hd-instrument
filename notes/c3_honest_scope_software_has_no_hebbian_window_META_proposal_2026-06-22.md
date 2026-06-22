# META atom proposal — software-substrate has NO Hebbian temporal window; biological-compression discriminator collapses to ARCHITECTURE-vs-timing in silico (c3 honest-scope, 2026-06-22)

**Date:** 2026-06-22
**Empirical anchor:** `exp_c3_compressed_sequence_replay_v1` smoke + full-config single-seed (timing-run) metrics. Cell commit a27939c5; cert-trail c6a2ac5e. Full 3-seed remote run in flight on cpu_runner_0 (~4.5min wall).

## The finding (one sentence)

Arm D (ONLINE_NO_GAP) reproduces Arm B (COMPRESSED) EXACTLY at every depth in both smoke (K=8 N_DIM=1024 d=[1,3,5]) and full-config single-seed (K=20 N_DIM=4096 d=[1,3,5,7,10]) — both arms hit recall_nn=1.0 — because the substrate is a SOFTWARE system without a biological Hebbian STDP temporal window (50-200ms), so the biological motivation for compressed-replay (squeeze 2s of waking trajectory into the Hebbian window) translates to a NULL in silico discriminator.

## What this means for the substrate (the load-bearing claim)

**The substrate-side win from sleep-replay-style sequence-binding is the ARCHITECTURE (the separate S matrix that binds ordered (k_{t-1}, k_t) pairs), NOT the TEMPORAL COMPRESSION per se.** Biology needs compression because Hebbian plasticity has a hard temporal window; software substrate writes outer-products at full precision regardless of pair-spacing in some external clock. The compression schedule (20x) is a tunable hyperparameter in software but it's NOT load-bearing for the architectural claim.

**What IS load-bearing in c3:**
1. **Arm B vs Arm A delta** (1.0 vs 0.0) — the S matrix is necessary; without it, the substrate has no sequence-binding at all (point-write-only W can't recover order).
2. **Arm B vs Arm C order_delta** (1.0 vs 0.0 at d≥3) — ORDER is the load-bearing factor; pair-density alone doesn't suffice. Shuffled pairs give chance-level recall (0.125 at d=1 = 1/k_seq for k_seq=8 random; 0.0 at d≥3).
3. **W_unchanged_by_sleep_all_arms = True** at every arm — the sleep pass writes to S, NOT to W. This is the architectural separation between content (W) and sequence (S). The cell verified this assertion at every seed × arm × config.

## What is NOT load-bearing (and the honest-scope guards against over-claiming)

- The 20x compression ratio is biologically motivated but software-incidental.
- The "compressed replay" framing inherits cred from neuroscience but the substrate's win is the SEPARATE SEQUENCE STORE, not the schedule.
- The cell does NOT establish that COMPRESSED replay is required IN PRINCIPLE in software; it establishes that the OFFLINE-pass + ORDERED-pair + SEPARATE-S-matrix architecture is the load-bearing combo.

## Atom proposal

**Atom-id candidate:** `META_software_substrate_no_hebbian_window_sequence_binding_is_architecture_not_timing`

**Kind:** META (substrate-design-discipline; cross-cell load-bearing for any future biological-replay-motivated cell)

**Content:** software substrate writes outer-products at arbitrary precision regardless of pair-spacing; biological Hebbian STDP windows (50-200ms) do NOT have software analogue; cells motivated by "compressed replay buys long-range Hebbian associativity" must explicitly include a NULL-DISCRIMINATOR control arm (ONLINE_NO_GAP-style) to disaggregate (a) the ARCHITECTURE primitive being tested from (b) the TIMING-LICENSE biology framing. If the null-discriminator arm matches the proposed-compression arm, the substrate-side win is the architecture, not the schedule.

**Composes with:**
- `META_smoke-VET-must-disaggregate-harness-vs-mechanism` (Fix #16) — same family: every discriminator must be verified to actually discriminate, both in harness sanity and mechanism interpretability.
- `cell-author-time-estimate-must-be-MEASURED-not-quoted` — adjacent; software/biology framings need explicit empirical anchors per cell.
- `verify-the-referent` family — the discriminator's referent (here: "compression buys associativity") must be verified in the target domain (software), not inherited from the source domain (biology).

**SCHEMA-VET status:** DRAFT cert-trail artifact; next-cycle hdi_skunkworks teammate spawned for SCHEMA-VET + atomization (cert-owner authority per A5).

## Implication for adjacent cells in queue

- **g1 (brain-drill #4 generation cell):** uses c3's S matrix as autoregressive engine. The Karuvally-Sejnowski temporally-asymmetric Hebbian + Langevin sampling design needs the same NULL-DISCRIMINATOR guard — does the substrate-side generation work in software regardless of the biological clock-binding (HVC) primitive? Pre-reg must include a no-clock-binding control arm.
- **m1 (brain-drill #6 modular K-macrocolumn cell):** the Larkum two-stream apical/basal context-binding sub-mechanism has a similar biology-vs-software-translation question. Include a no-context-binding control.
- **Any future biological-replay-motivated cell:** same discipline — null-discriminator arm mandatory.

## Why ship this NOW (vs deferring to skunkworks SCHEMA-VET-then-write)

The c3 cell has already DEMONSTRATED the pattern (Arm D = Arm B in both smoke + full-config timing-run with cv=0.0). Drafting the META atom as a cert-trail artifact NOW preserves the empirical evidence + framing while the c3 full 3-seed run is in flight. SCHEMA-VET + Store-atom-write are deferred to next-cycle hdi_skunkworks spawn per Fix #14 budget; this artifact is the durable input.

— Research (Director); c3 honest-scope META proposal; cert-trail durable artifact; no addressee per the no-inter-session-routing rule.
