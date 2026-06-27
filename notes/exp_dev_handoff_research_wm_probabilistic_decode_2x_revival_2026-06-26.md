# exp_dev hand-off — research: WM-FM + soft-topK 2x revival drill

**Filed-by:** research (Opus 4.7 1M)
**Filed-at:** 2026-06-26
**Trigger:** 2x revival of HARD_FAIL anchors per `feedback_route_negatives_to_research_2x_3x_revival_drills_USER_STANDING_2026-06-20.md`. Source research note `notes/research_wm_probabilistic_decode_2x_revival_drill_2026-06-26.md`.

**Pause state:** check `data/orchestrator_paused.flag` per standard exp_dev contract.

**Per [[feedback-no-experiment-design-in-prompts]]** — this hand-off ranks anchor candidates and points at the research note for math + mechanism + bands. It does NOT design cells inline; exp_dev authors cells per autonomy declaration. Per `feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md`: ALL 4 anchors are framed for **compositional infrastructure**, NOT language prediction. Discriminators use typed-KG or synthetic typed slots, never text BPC.

---

## Source research note

`notes/research_wm_probabilistic_decode_2x_revival_drill_2026-06-26.md`

Read it FIRST for: failure-mechanism diagnosis (WM-FM = wrong problem class for lock-in; soft-topK = zero signal source); 4 alternative-mechanism candidates with substrate-physics rationale; pre-registered HARD-PASS / HARD-FAIL bands per anchor; brain analogs (Walsh-Hadamard CDMA-class vs FM-class theta-gamma multiplexing; PFC particle-filter-class vs parietal soft-topK-class); citations; BIAS-13 / O / S audit.

---

## Anchor candidates — rank-ordered

### ANCHOR_1 (TOP — highest P, on chain-grade infra): multi_bank_typed_routing_v1

- **Anchor pointer:** research note section "ALT-WM-2 (Multi-bank typed routing)" + cheap decisive test.
- **Substrate-product reading:** ships **typed slot binding with cross-type query rejection** — foundational primitive for compositional understanding per USER pivot. Multi-bank infrastructure ALREADY chain-grade at K=4096 (`data/exp_phase_diagram_working_memory_multibank_K_extension_to_16384_v1/metrics.json`: MULTI_64x rec=1.000 cv=0.000). Typing is the extension. Every slot's type observable; every rejected query auditable (glass-box). LLMs cannot do typed cross-type rejection naturally; substrate ships it as a primitive.
- **Tier hint:** **MEASURED_MECHANISM** target; promotes to **CHAIN_GRADE** if typed-recall ≥ 0.95 across all 8 types at K=4096 AND refuse-rate ≥ 0.90 on mismatched-type queries AND cv ≤ 0.05. Default tier per Fix #28 = MIDDLE; let cert-owner tier UP from observed metrics.
- **Why now:** USER pivot 2026-06-26 OPENED the compositional-understanding track; typed multi-bank is the primary infrastructure that track requires. Builds DIRECTLY on chain-grade primitive.
- **P_HARD-PASS / P_MIDDLE / P_HARD-FAIL = 0.60 / 0.25 / 0.15** (lit-scan calibrated; brain-grounded prior; substrate already chain-grade on the base mechanism).

### ANCHOR_2 (cheapest decisive test; orthogonal failure-mode probe): walsh_hadamard_CDMA_wm_v1

- **Anchor pointer:** research note section "ALT-WM-1 (Walsh-Hadamard CDMA)" + cheap decisive test.
- **Substrate-product reading:** ships **orthogonal-by-construction channelization** primitive if it lands. Refutes-or-confirms whether the WM-FM HARD_FAIL was a CHANNELIZATION failure (which Walsh-Hadamard fixes) or a bind+sum CAPACITY failure (in which case Walsh-Hadamard ALSO fails, confirming the limit lies elsewhere). Either outcome is informative.
- **Tier hint:** **MEASURED_MECHANISM**; promotes to **CHAIN_GRADE** if cross-slot bleed ≤ 0.02 at K=128 AND K=256, AND recall ≥ 0.95 at K=128 + ≥ 0.85 at K=256, cv ≤ 0.05.
- **Why now:** ~10 min wall on local_cpu_queue; cheapest decisive test of the WM revival; runs in parallel with ANCHOR_1; orthogonal mechanism class so independent evidence.
- **P_HARD-PASS / P_MIDDLE / P_HARD-FAIL = 0.55 / 0.25 / 0.20** (Hadamard CDMA is standard math with provable orthogonality; only risk is bipolar HRR bind+sum capacity at K=256 + N=4096).

### ANCHOR_3 (composes on chain-grade refuse-gate; ships epistemic-humility primitive): cleanup_energy_refuse_gate_v1

- **Anchor pointer:** research note section "ALT-PD-2 (Cleanup-energy refuse-gate)" + cheap decisive test.
- **Substrate-product reading:** ships **epistemic-humility refuse-gate** keyed on cleanup-energy gap (top-1 cosine − top-2 cosine). When gap < tau, substrate declines to commit — refuses rather than confabulates. This IS the substrate-vs-LLM categorical differentiator for the auditable-AI-memory-subsystem product. Composes directly on substrate's chain-grade refuse-gate (per cap_map).
- **Tier hint:** **MEASURED_MECHANISM**; promotes to **CHAIN_GRADE** if typed-correct top-1 ≥ 0.50 at hop-5 on unambiguous chains AND refuse-rate ≥ 0.80 on ambiguous AND ≤ 0.15 on unambiguous (low false-refuse).
- **Why now:** signal source is energy gap (observable from chain-grade cleanup primitive), NOT the failed soft-topK distribution-shaping. Cheap (~10 min smoke). Independent of ANCHOR_1 (can run before typed multi-bank lands).
- **P_HARD-PASS / P_MIDDLE / P_HARD-FAIL = 0.50 / 0.30 / 0.20** (composes on chain-grade primitives; brain analog = Friston free-energy refuse).

### ANCHOR_4 (defer; depends on ANCHOR_1; high upside compositional primitive): particle_filter_compositional_v1

- **Anchor pointer:** research note section "ALT-PD-1 (Particle filter over compositional hypotheses)" + cheap decisive test.
- **Substrate-product reading:** ships **substrate-native bayesian compositional inference** — multi-bank slots become hypothesis particles, importance-weighted by composition-validity (type check + relation-consistency). Categorical lift over LLMs: parallel hypothesis tracking at 50-1000 concurrent particles vs LLM's serial autoregression. This is the product story for "substrate hypothesizes, weights by validity, commits or refuses."
- **Tier hint:** **CONCEPTUAL_PROBE** until ANCHOR_1 lands (depends on typed multi-bank infra); promotes to **MEASURED_MECHANISM** after smoke with particle-effective-N ≥ 50%; promotes to **CHAIN_GRADE** if top-1 ≥ 0.80 at hop-3 on ambiguous-by-construction chains AND H(hop-3)/H(hop-0) ≤ 0.5.
- **Why now:** DEFER until ANCHOR_1 lands. Pre-requisite infrastructure (typed multi-bank routing) must be measured before the particle-filter composition is discriminable.
- **P_HARD-PASS / P_MIDDLE / P_HARD-FAIL = 0.40 / 0.35 / 0.25** (novel-synthesis cap honored; signal source is the OPENED compositional-understanding track).

---

## Recommended dispatch order

1. **ANCHOR_2 (Walsh-Hadamard CDMA WM)** FIRST — cheapest decisive test (~10 min); local_cpu_queue; runs in parallel with everything; either outcome informs ANCHOR_1.
2. **ANCHOR_1 (multi-bank typed routing)** — remote_cpu_queue or local; ~30 min; chain-grade-infra extension; LOAD-BEARING for compositional track.
3. **ANCHOR_3 (cleanup-energy refuse-gate)** — local_cpu_queue; ~10 min smoke; independent of 1+2; ships epistemic-humility primitive.
4. **ANCHOR_4 (particle-filter compositional)** — DEFER until ANCHOR_1 lands; then dispatch composing on the typed multi-bank infra.

Bundling: ANCHOR_2 + ANCHOR_3 can ship in parallel immediately (different cells, different queues). ANCHOR_1 spawns its own cell after smoke gate. ANCHOR_4 deferred per dependency.

---

## Context pointers

- Source research note (math + mechanism + bands + brain analogs + citations + bias audit):
  `notes/research_wm_probabilistic_decode_2x_revival_drill_2026-06-26.md`
- Source failures revived:
  - `data/exp_substrate_working_memory_frequency_multiplexed_lock_in_v1/metrics.json` (HARD_FAIL_INTERMOD)
  - `data/exp_soft_topK_cleanup_distribution_preserving_v1_smoke/metrics.json` (HARD_FAIL chance-floor)
- Source preregs:
  - `preregs/2026-06-25_substrate_working_memory_frequency_multiplexed_lock_in_v1.md`
  - `preregs/2026-06-26_soft_topK_cleanup_distribution_preserving_v1.md`
- Chain-grade WM infrastructure ANCHOR_1 + ANCHOR_4 build on:
  `data/exp_phase_diagram_working_memory_multibank_K_extension_to_16384_v1/metrics.json` (MULTI_64x K=4096 rec=1.000 cv=0.000; MULTI_128x K=8192 rec=1.000 cv=0.000)
- Chain-grade single-carrier lock-in (the precedent the FM cell mis-extended):
  `data/exp_lock_in_amplifier_hd_frequency_v1_FULL/metrics.json` (P64 16.39x SNR lift at sigma=64; cv=0)
- USER pivot context (compositional understanding OPENED; language CLOSED):
  `notes/research_STRATEGIC_PIVOT_language_track_closed_compositional_understanding_opens_2026-06-26.md`
- Standing USER lock (do not test against language):
  `memory/feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md`
- Compositional understanding drill 1 (typed KG composition; ANCHOR_1 + ANCHOR_4 composable with):
  `notes/exp_dev_handoff_research_compositional_understanding_drill1_typed_KG_composition_2026-06-26.md`
- Gap A probabilistic reasoning research note (background on soft-topK class + alternative mechanism inventory):
  `notes/research_gap_A_probabilistic_reasoning_2026-06-26.md`
- Bias master checklist (BIAS-13 regime mismatch + BIAS-O basis-vs-use-case + BIAS-Q saturation + BIAS-S band-calibration):
  `memory/feedback_experiment_bias_master_checklist_USER_2026-06-24.md`

---

## Contract section

- Pre-reg discipline per `[[feedback-envelope-expansion-fail-bands]]`: HARD-PASS + HARD-FAIL bands above are pre-registered HERE; exp_dev MUST lift them into the cell's prereg note verbatim before dispatch.
- Self-test per `[[feedback-formula-selftests]]`.
- Multi-seed FULL on smoke clearance.
- Queue routing per Tier A/B/C in `agents/exp_dev.md` Section 0 (recommend local_cpu_queue for ANCHOR_2 + ANCHOR_3; remote_cpu_queue for ANCHOR_1).
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`.
- Per-arm metrics-read per Fix #28 — DO NOT trust verdict_msg framing; read metrics.json per-arm before any cross-cell convergence claim.
- Post-ship REMOTE VERIFY per Fix #11 pipeline template.
- Default tier MIDDLE per Fix #28; let cert-owner tier UP from observed metrics.
- BIAS-13 + BIAS-S regime audit MANDATORY in prereg (per source research note): ensure the discriminator's signal-source regime is non-trivial. Specifically:
  - ANCHOR_3 + ANCHOR_4: synthetic typed-KG must NOT collapse to uniform stationary distribution by hop-5 (the soft-topK failure mode); verify with a regime-sanity self-test that baseline argmax achieves > 1/V_C at hop-5 on unambiguous chains.
  - ANCHOR_1 + ANCHOR_2: cross-slot bleed measured per-slot, not aggregated (the WM-FM failure mode where aggregate recall looked fine but per-slot bleed was 0.421).

---

## Autonomy declaration

exp_dev decides:
- Cell author (manual vs spawn cell-author sub-agent)
- Smoke seed + smoke timeout
- N_DIM choice (recommend N=4096 for ANCHOR_2 to apples-to-apples the WM-FM failure; N=8192 for ANCHOR_1 to match multi-bank chain-grade; N=4096 or 8192 for ANCHOR_3 per smoke wall)
- V_C / type-count / number-of-banks per typed routing design
- Synthetic typed-KG construction (number of entities + types + relations + ambiguity rate) — recommend 64 entities + 8 types + 32 binary relations + 50% ambiguity rate as initial probe
- Queue routing per recommendations above
- Discriminator extension (e.g. add perturbation-stability arm if cheap)
- Whether to bundle ANCHOR_2 + ANCHOR_3 into one 5-arm cell or ship separately (recommend separately — different problem classes, different bands)
- Whether ANCHOR_4 dispatch is gated on ANCHOR_1 HARD_PASS or HARD_PASS_PARTIAL (recommend HARD_PASS_PARTIAL — typed multi-bank only needs to be observable, not chain-grade, for ANCHOR_4 to be discriminable)

Research's authority ends at the anchor list + bands + brain-mechanism math + failure diagnosis. exp_dev is the cell-design authority.

Recommended FIRST dispatch: ANCHOR_2 + ANCHOR_3 in parallel on local_cpu_queue; ANCHOR_1 on remote_cpu_queue after smoke gate. ANCHOR_4 deferred.

---

-- research (Opus 4.7-1M)
