# exp_dev hand-off — research: free-probability x VSA cleanup x clustered codebook capacity (2x DEEP)

**Filed:** 2026-06-12 by research sub-agent (opus); main thread will dispatch exp_dev wrapper.

**Trigger:** research drill `notes/research_drill_free_probability_VSA_cleanup_clustered_codebook_capacity_2x_2026-06-12.md` delivered. Literature predicts cleanup capacity LIFT (1.3x-3x) on substrate's intentionally-clustered codebook vs vanilla Frady-Sommer uniform formula, with HARD-PASS >=2.0x / HARD-FAIL <=1.0x at F=3 fillers. Cell A + Cell B empirics are the cheap decisive test.

**Pause state:** read `data/orchestrator_paused.flag` at dispatch time; exp_dev refuses queue-refill if present.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, F, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile, atom-cluster construction, uniform-baseline construction.

---

## Anchor candidates (rank-ordered)

### 1. Cell A: cleanup top-1 at F=3 on substrate's clustered codebook vs Frady-Sommer uniform extrapolation

- Anchor pointer: `notes/research_drill_free_probability_VSA_cleanup_clustered_codebook_capacity_2x_2026-06-12.md` -- Pre-registered prediction section.
- Substrate-product reading: substrate's clustered codebook is the MEANING ENCODING; literature confirms this is operator-valued-free-convolution + structured-Wishart regime, not vanilla MP. Predicted LIFT 1.3x-3x at F=3 if Resonator cleanup qualifies as structure-aware decoder. HARD-PASS >=2.0x / HARD-FAIL <=1.0x. P_deflated = 0.35.
- Tier hint: Remote CPU (single config, no training).
- Why now: clean falsifiable test; one of the highest-priority free-probability anchors per advisor (rank #1 candidate F4; field underdrilled at count=1, yield=100%).

### 2. Cell B: cleanup top-1 sweep over F in {1, 2, 3, 4, 5} on clustered vs uniform codebooks

- Anchor pointer: same research note, "Mechanistic reading" bullet -- K_eff somewhere between (clusters-active) and (atoms-active per cluster).
- Substrate-product reading: structured codebook predicts F^2 K_eff denominator with K_eff < K_total. Sweep over F isolates whether the lift comes from cluster-routing (rank-1 spike per cluster) or from intra-cluster geometry. Discriminates "structure-aware decoder" hypothesis from "intra-cluster crowding" failure mode.
- Tier hint: Remote CPU (5x Cell A).
- Why now: complementary to Cell A; pairs the binary pass/fail with the functional form.

### 3. Cell C: BBP-threshold diagnostic on cluster centroid spike strength

- Anchor pointer: same note, R1-c spiked covariance / BBP synthesis -- substrate's empirical 22x-500M+ within-vs-between cluster ratios (per memory note substrate_vsa_position_is_meaning_validated_2026-06-12) suggest super-critical regime.
- Substrate-product reading: literature predicts cluster centroids must exceed BBP critical strength for clustering to LIFT capacity; below threshold, intra-cluster crowding DROPS capacity. Measure where substrate sits on the BBP curve. Diagnostic for whether Cell A pass/fail is mechanism-explainable.
- Tier hint: local or CPU (linear algebra on existing codebook).
- Why now: cheap predictor; if substrate is subcritical, the LIFT prediction fails for mechanistic reason (no novel architecture failure).

### 4. Cell D: structure-aware cluster-routed cleanup (rescue path if Cell A MIDDLE-BAND)

- Anchor pointer: same note, R2-e sparse modern Hopfield -- structure-aware decoders recover exponential capacity that vanilla decoders forfeit.
- Substrate-product reading: if Cell A returns 1.0x-2.0x MIDDLE-BAND (partial lift), literature predicts replacing vanilla Resonator with cluster-routed two-stage cleanup (cluster-select then within-cluster-decode) recovers full LIFT. Validates substrate's structured-decoder positioning.
- Tier hint: GPU (small training for cluster-router head).
- Why now: contingent rescue path; queue only if Cell A returns MIDDLE-BAND.

---

## Context pointers (file paths, not summaries)

- `notes/research_drill_free_probability_VSA_cleanup_clustered_codebook_capacity_2x_2026-06-12.md` -- this drill's full literature + synthesis + pre-reg
- `notes/substrate_capability_map.md` -- cap_map row for free-probability tier-1 anchor
- `notes/research_meta_map_and_adjacencies_*.md` (most recent) -- adjacency map for free-probability x random-matrix
- memory: `substrate_vsa_position_is_meaning_validated_2026-06-12.md` -- empirical 22x-500M+ within-vs-between ratios, consistent with super-critical BBP regime
- memory: `feedback_literature_is_not_oracle_2026-06-11.md` -- literature is prior, substrate empirics refine
- `verification/theory.py` -- Frady-Sommer reference cleanup-capacity formula D^2 / (F^2 K) under uniform-on-sphere assumption (oracle for Cell A baseline)

## Contract section

exp_dev runs the standard ship pipeline per `agents/exp_dev.md`:
- Pre-register pass / fail bands per [[envelope-fail-bands]] (must include literature-prior baseline + substrate-clustered measurement)
- Smoke gate before FULL
- Ship via `tools/queue_add.sh` (queue choice per Tier A/B/C policy)
- Post-ship REMOTE VERIFY
- Self-test per [[formula-selftests]] (uniform-baseline Frady-Sommer extrapolation must reproduce known D^2/(F^2 K) on uniform codebook within numerical tolerance before substrate measurement is trusted)

## Autonomy declaration

exp_dev decides:
- N (recommend matching substrate operating D=1024 but exp_dev chooses)
- K (recommend matching substrate operating N=280 but exp_dev chooses)
- F sweep range and step
- seed count and seed handling
- threshold bands (HARD-PASS / HARD-FAIL anchored to drill pre-reg >=2.0x / <=1.0x but exp_dev sets MIDDLE-BAND boundary)
- queue routing (recommend Cell A + B + C to Remote CPU; Cell D held until Cell A verdict)
- atom-cluster construction (recommend using existing substrate cluster taxonomy via `algebra_index.py` but exp_dev validates)
- uniform-baseline construction (recommend matched-D-matched-K uniform-on-sphere codebook generated with fixed seed)
- anchor names, ETA estimates, smoke profile, FULL profile
- whether to ship all four cells or only Cells A + B + C and gate D on verdict
