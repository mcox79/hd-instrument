# Research drill (2x deeper) — 5-tier substrate clock hierarchy IMPLEMENTATION

filed: 2026-06-23
drill class: 2x (level-2 operational drill on parent timescale-ratio finding; fills the WHAT/HOW/MEASURE gap)
parent: `notes/research_substrate_brain_timescale_ratio_2x_drill_2026-06-23.md` (declared 5 tiers but did NOT specify implementation)
sibling brain drills referenced:
  - `notes/research_brain_continual_learning_CLS_5x_drill_2026-06-22.md` (CLS dual-store; cortex/hippocampus rate-ratio 10x)
  - `notes/research_brain_hippocampal_SWR_sleep_replay_5x_drill_2026-06-22.md` (SWR machinery; compressed-sequence binding; ~10k-30k SWR events / 8hr sleep)
empirical anchors on substrate (existing/in-flight):
  - dual_trace_RESCUE_corrected_baseline_v1 (overnight; tests TAU_NEG correction)
  - c1 CLS-replay PARTIAL — substrate operating BELOW α=0.5 cliff under codebook-NN cleanup
  - c3 sequence-binding chain-grade ratified (CERT 586)
  - g1b autoregressive generation MEASURED_MECHANISM (CERT 587)
lit-scan calibration: novel-synthesis cap P at 0.50; deflate empirical-precedent P by 0.15-0.25; HARD-FAIL bands mandatory.

---

## HEADLINE — implementation principle in one sentence

**Implement the 5-tier clock hierarchy as ONE master integer counter `master_tick` with each tier defined by integer-division modular arithmetic (`tier_k_tick = master_tick // TIER_K_DIVISOR`), AND each tier owns a SINGLE dict-of-traces with that tier's exponential decay constant — exactly the data structure Fusi-Drew-Abbott cascade-synapse model (Neuron 2005) uses for biological multi-timescale plasticity — so that adding/removing tiers is a config change, not a refactor, and tier-collision bugs become detectable by per-tier write-counter invariants.**

In plain English: ONE integer increments per token. FIVE tiers each watch a different multiple of it (every 1 / every 10 / every 100 / every 1000 / every ~10^5 ticks). Each tier owns its own decay-trace dict + its own update ops + its own metrics. Tiers communicate only by READING each other's traces — never by writing across tiers. This kills the "everything-runs-at-per-chunk" collapse that the parent drill identified.

---

## Per-tier TABLE — the load-bearing artifact

Column legend: `divisor` = ticks-per-tier-event (master_tick % divisor == 0 triggers the tier op); `decay_tau` = exponential decay time constant in that tier's own units; `trace_store` = data structure; `brain analog` = ms-equivalent and brain mechanism; `substrate mechanism` = what runs at that tier today + new; `gating in` = which slower tier GATES this tier (modulates rate, enables/disables ops); `gating out` = which faster tier this tier MODULATES.

| Tier | divisor (per master_tick) | decay_tau (units of THIS tier) | trace_store data structure | brain analog (ms-equivalent) | substrate mechanism @ this tier | gating IN (slower modulates this) | gating OUT (this modulates faster) |
|------|---------------------------|--------------------------------|----------------------------|-------------------------------|--------------------------------|-----------------------------------|------------------------------------|
| **TIER_0** per-token | 1 | n/a (instantaneous) | none (event-only) | ~10ms; single spike; AP firing | per-token Hebbian write to W; cf-RPE delta per write; per-context T; phasic ACh per query; phasic NE | T_3 mood-baseline gates write magnitude; T_4 sleep-mode gates write-vs-frozen | emits e_pos / e_neg events read by T_1 |
| **TIER_1** per-chunk (STDP window) | 10 (=> ~10 tokens) | TAU_POS=5, TAU_NEG=10-15 (corrected from 50) | `{e_pos: Tensor[N_DIM], e_neg: Tensor[N_DIM]}` exponentially-decaying dual trace | ~20-60ms; STDP window; theta-gamma binding (P_gamma=7 sub-cycles, brain-canonical) | dual-trace LTP/LTD; theta-gamma lock-in (k_gamma=31 audit recommended); pattern-completion attractor iterations | T_2 trace-half-life gates whether STDP write fires at all | emits "chunk-summary" event read by T_2 |
| **TIER_2** per-window (E-LTP) | 100 (=> ~100 tokens) | TRACE_HALF_LIFE=100-300 (NEW parameter; default = 200 ticks at T_2 = ~20k master_tick) | `{tagged_traces: dict[atom_id -> (trace_strength, age, tag_count)]}` synaptic-tag dict (Frey-Morris 1997 analog) | ~1-2 hours; E-LTP (protein-synthesis-independent); synaptic tagging without trigger | trace tagging: atoms WRITE-recently tagged with strength; un-tagged traces decay; tagged-but-untriggered fade after 200 T_2 ticks; **MISSING TIER** in current substrate | T_3 mood-baseline modulates tag threshold | emits "ready-for-consolidation" event read by T_3 + T_4 |
| **TIER_3** per-mini-epoch (tonic modulator) | 1000 (=> ~1000 tokens) | tau_tonic = 5-10 (slow baseline drift, ~5-10 T_3 ticks = 5k-10k master_tick) | `{g_DA_tonic: float, g_5HT_tonic: float, g_ACh_tonic: float, g_NE_tonic: float, context_id: int}` baseline-modulator scalars + active-context | minutes-tens-of-minutes; tonic dopamine baseline; 5HT mode; ACh arousal; context-switching | tonic-DA baseline drift (Schultz minutes-scale); 5HT bank-select (serotonin_mode_switch_bank_select_LM_v1 in flight); ACh arousal mode; per-context T learned baseline; **PARTIAL** in current substrate | T_4 sleep-mode gates whether tonic-baselines update (frozen during sleep) | modulates T_0 write magnitude + T_1 STDP gain + T_2 tag-threshold |
| **TIER_4** per-epoch (CLS / L-LTP) | ~10^5 (= N_TRAIN tokens) | N_REPLAY_PASSES = 10-100 (replay-count not decay) | `{episode_buffer: ReservoirSample[N_BUFFER atoms], replay_priority: dict[atom_id -> RPE_score], consolidation_phase: bool}` episodic-buffer + priority queue | hours-days; L-LTP (protein-synthesis-dependent); SWR replay during NREM sleep; systems consolidation | CLS-replay (PARTIAL: single-pass currently; brain does 10-100x); compressed-sequence binding (c3 ratified primitive); engram reactivation; prioritized-replay sampling (Mattar-Daw 2018; SWR-prioritization Michon 2025) | none (top tier; gated by external epoch boundary) | freezes T_0 writes during consolidation_phase=True; modulates T_3 contexts learned + T_2 tag thresholds |

**Tier-gating directionality (the load-bearing invariant):**
- **Slow → Fast = modulate only** (T_3 changes T_0's effective learning rate; T_4 enables/disables T_0 writes). Slow tiers NEVER write to fast-tier trace structures directly.
- **Fast → Slow = emit events only** (T_0 emits a per-write event read by T_1; T_1 emits chunk-summary read by T_2). Fast tiers NEVER hold references to slow-tier state.
- **No same-tier coupling** (different T_1 trace components, e.g. e_pos and e_neg, communicate via shared input not by writing each other).

This directionality is the bug-detection invariant: a write that goes the wrong direction (fast→slow direct-write, or same-tier cross-write) is a tier-collision bug. Per-tier `write_count` and `cross_tier_read_count` instruments catch it.

---

## L2 — substrate-clock-equivalent mapping (what the tier-clocks LOOK LIKE)

### How many "ticks" per epoch at each tier

For a representative ingest of `N_TRAIN = 10^5 tokens`:

| Tier | divisor | events per epoch | what fires |
|------|---------|-------------------|------------|
| T_0 | 1 | 10^5 (every token) | Hebbian write + cf-RPE + per-context T + phasic ACh/NE |
| T_1 | 10 | 10^4 (every chunk) | dual-trace decay tick; theta-gamma cycle audit; STDP write-or-skip |
| T_2 | 100 | 10^3 (every window) | tag decay; tag-trigger check (if T_4 emits "consolidation_window", convert tagged → consolidated) |
| T_3 | 1000 | 10^2 (every mini-epoch) | tonic-baseline drift; context-switch detection; bank-route update |
| T_4 | ~10^5 | 1 (per epoch) | CLS replay pass (N_REPLAY=10-100 inner replays per stored pattern); episode-buffer flush; consolidation_phase=True for a configurable inner-budget |

**Quantitative budget at N_REPLAY=10:** 1 epoch = N_REPLAY * |B| inner-replay events = 10 * 5000 = 5×10^4 replay write-events per epoch. This is ~50% of forward-pass write cost (5×10^4 vs 10^5 forward writes), matching brain's "consolidation budget approximately equals waking budget" rule per Klinzing-2019.

### What operations happen at each tick

```
on_tick(master_tick, ingest_event):
    # ALWAYS: TIER_0
    T_0_op(ingest_event)                                    # Hebbian write to W; per-context T

    # CONDITIONAL: faster tiers gate the slower ones
    if master_tick % 10 == 0:
        T_1_op(read=T_0_event_buffer,
               modulator=T_3.tonic_state)                   # dual-trace decay + STDP write decision

    if master_tick % 100 == 0:
        T_2_op(read=T_1_chunk_summary,
               consolidation_window=T_4.consolidation_phase) # tag decay + tag-trigger check

    if master_tick % 1000 == 0:
        T_3_op(read=T_0_long_average, T_1_chunk_var,
               sleep_mode=T_4.consolidation_phase)          # tonic baseline drift; context detect

    if master_tick % EPOCH_DIVISOR == 0:
        T_4_op(read=T_2_tagged_traces, T_3.context_history,
               episode_buffer=B)                            # multi-pass CLS replay
```

### What's the substrate-equivalent of "sleep boundary"?

Brain sleep = `T_4.consolidation_phase = True`. Concretely on substrate:
- T_0 forward Hebbian writes FROZEN (no new fact-ingest)
- T_1 STDP DISABLED (no new dual-trace updates)
- T_2 tagged traces become eligible for tag-trigger → consolidation
- T_3 tonic baselines FROZEN (no context drift during sleep, per Born 2010 stable cortex during NREM)
- T_4 runs N_REPLAY inner passes, each sampling from `episode_buffer` with priority weighting `replay_priority` (RPE-biased per Mattar-Daw 2018 + novelty-biased per Michon 2025), Hebbian-writing the sampled pattern through W. Critically: REPLAY USES THE SAME T_0 Hebbian-write primitive — just with the consolidation_phase flag elevating learning rate η_W ~10x per O'Reilly-2014.

Sleep boundary trigger = either (a) external N_TRAIN budget exhausted, OR (b) running-loss metric stagnant for `STAGNATION_WINDOW = 5×10^4` T_0 ticks (brain analog: hippocampus capacity-full triggers ripples per Buzsaki 2015).

---

## L3 — implementation specifics

### Should substrate maintain a separate clock variable per tier, or use modular arithmetic on master?

**RECOMMENDATION: Modular arithmetic on master.** Reasons:

1. **One source of truth** — `master_tick` is the only mutable counter; per-tier ticks are pure functions of it. No drift between tier counters; no concurrency bug class where T_1.tick and T_2.tick get out of sync.
2. **Per-tier ticks are derived** — `T_k.tick = master_tick // T_k_divisor`. Computed on-read; never stored.
3. **Cheap modularity** — divisors are powers/multiples of base unit; integer-mod is O(1).
4. **Composes with replay** — during T_4 replay phase, you OPTIONALLY freeze `master_tick` and run a separate `replay_tick` counter inside the consolidation phase. This keeps the wall-clock-equivalent tier semantics correct: replay events don't count toward T_3 context-drift.
5. **Brain analog matches** — biological cascades (Fusi-Drew-Abbott 2005) similarly derive metaplastic-state-decay-rates from a single neural-activity counter via state-transition probabilities, not parallel clocks.

The ALTERNATIVE (per-tier independent clocks) was used in early multi-timescale-RL implementations (AuGMEnT 2018) and has a well-documented bug: per-tier clocks can desynchronize on long runs due to floating-point accumulation; integer-master-tick is robust. (Source: ScienceDirect AuGMEnT eligibility-traces issue noted in adaptive-eligibility-traces 2021.)

### How does TAU_NEG=10 (brain-canonical 2x) integrate with multi-pass CLS-replay (hours tier)?

**The two corrections live at DIFFERENT tiers and DO NOT INTERACT directly.** TAU_NEG=10 is a T_1 decay constant; N_REPLAY=10-100 is a T_4 multi-pass count. The integration point is:
- **During normal ingest (consolidation_phase=False):** TAU_NEG=10 governs the per-chunk STDP window; N_REPLAY is irrelevant (T_4 hasn't fired yet).
- **During T_4 consolidation phase (consolidation_phase=True):** the inner replay events ARE T_0 writes inside the replay loop, so they trigger T_1 STDP at TAU_POS=5/TAU_NEG=10 with each replay event spaced ~10 replay-ticks apart. This means dual-trace plasticity IS active during replay, and the corrected TAU_NEG=10 (vs old 50) makes the dual-trace WORK DURING REPLAY where previously the long TAU_NEG=50 chunks barely activated.

**Concrete prediction:** TAU_NEG=50 + N_REPLAY=10 might look better than TAU_NEG=50 + N_REPLAY=1 simply because more inner iterations partially compensate for the wrong-tier TAU_NEG. The 2×4 factorial in the parent drill's cheap decisive test will SEPARATE these effects.

### Concrete data structure proposal (Python pseudocode)

```python
@dataclass
class ClockHierarchy:
    """5-tier substrate clock; single master_tick + derived tier-ticks.

    Per-tier trace stores own their own decay logic and metrics.
    Tier-collision detection via per-tier write_count + cross_tier_read_count.
    """
    master_tick: int = 0

    # divisors (config-settable; defaults match brain-canonical ratios)
    DIVISOR_T1: int = 10            # per-chunk
    DIVISOR_T2: int = 100           # per-window
    DIVISOR_T3: int = 1000          # per-mini-epoch
    DIVISOR_T4: int = 100_000       # per-epoch

    # decay-tau parameters
    TAU_POS_T1: int = 5
    TAU_NEG_T1: int = 12            # corrected 2-3x ratio (parent drill)
    TRACE_HALF_LIFE_T2: int = 200   # NEW (in T_2 ticks)
    TAU_TONIC_T3: int = 7           # NEW (in T_3 ticks)
    N_REPLAY_T4: int = 30           # NEW (replay-passes per consolidation phase)

    # per-tier trace stores (load-bearing)
    t0_event_buffer: list = field(default_factory=list)         # short-lived; flushed on T_1 read
    t1_traces: dict = field(default_factory=lambda: {           # dual-trace
        'e_pos': None, 'e_neg': None,                           # Tensor[N_DIM] after init
        'k_theta': 1, 'k_gamma': 31,                            # lock-in audit
    })
    t2_tags: dict = field(default_factory=dict)                 # atom_id -> (strength, age, tag_count)
    t3_state: dict = field(default_factory=lambda: {
        'g_DA_tonic': 1.0, 'g_5HT_tonic': 1.0,
        'g_ACh_tonic': 1.0, 'g_NE_tonic': 1.0,
        'context_id': 0, 'context_history': [],
    })
    t4_state: dict = field(default_factory=lambda: {
        'episode_buffer': None,                                  # ReservoirSample[N_BUFFER]
        'replay_priority': {},                                   # atom_id -> RPE_score
        'consolidation_phase': False,
    })

    # per-tier write_count (collision detection)
    write_count: dict = field(default_factory=lambda: {f'T_{k}': 0 for k in range(5)})
    cross_tier_read_count: dict = field(default_factory=dict)   # (from_tier, to_tier) -> count

    # tier-derived ticks (pure functions of master_tick)
    @property
    def t1_tick(self): return self.master_tick // self.DIVISOR_T1
    @property
    def t2_tick(self): return self.master_tick // self.DIVISOR_T2
    @property
    def t3_tick(self): return self.master_tick // self.DIVISOR_T3
    @property
    def t4_tick(self): return self.master_tick // self.DIVISOR_T4

    def on_token(self, ingest_event):
        """Single entry point per master_tick; dispatches all tier ops."""
        self.master_tick += 1
        self._t0_op(ingest_event)                              # ALWAYS
        if self.master_tick % self.DIVISOR_T1 == 0: self._t1_op()
        if self.master_tick % self.DIVISOR_T2 == 0: self._t2_op()
        if self.master_tick % self.DIVISOR_T3 == 0: self._t3_op()
        if self.master_tick % self.DIVISOR_T4 == 0: self._t4_op()

    # _t0_op / _t1_op / ... implement that tier's tick;
    # only access OWN write_count++; read other tiers via designated
    # read-port that increments cross_tier_read_count;
    # NEVER write to other tier trace stores.
```

This data structure is the **single source of truth** for the clock hierarchy. Existing cells get refactored to receive a `ClockHierarchy` instance, instead of taking individual TAU/replay parameters; the parameters live on the dataclass.

**Storage cost:** ~5 Tensor[N_DIM] + a few dicts + scalars ≈ O(N_DIM) per clock instance — trivial vs the W matrix itself.

**Hot-path cost:** 4 integer-mod checks per token (≤1 ns each); selected tier ops fire only at their divisor — total tier-op cost amortizes to O(1) per token (T_4 fires once per ~10^5 tokens; its cost is amortized over those).

---

## L4 — measurement protocol (validating the hierarchy IS functional)

### The 4 failure modes to instrument

| Failure mode | What it looks like | Metric / detector |
|---|---|---|
| **Tier collision** (op runs at wrong tier) | T_2 tag-write count > expected; per-tier write_count breaks invariant write_count[T_k] ≤ master_tick // DIVISOR_T_k | per-tier `write_count` invariant check at every T_4 boundary; assertion error if violated |
| **Tier collapse** (only one tier active; others never fire) | write_count[T_k] = 0 for k ∈ {1, 2, 3} after N_TRAIN=10^5 | per-tier write_count histogram in dashboard; alert if any T_k=0 at end-of-epoch (excluding T_4 which fires once) |
| **Tier desynchronization** (per-tier traces drift from master_tick) | (NOT POSSIBLE in modular-arithmetic-on-master design); would manifest as t1_tick != master_tick // DIVISOR_T1 | assertion in `@property` checks; if separate-clock impl ever used, periodic sync check |
| **Cross-tier write leakage** (fast tier writes to slow tier store directly) | cross_tier_read_count goes up but write count to other tier ALSO goes up | per-tier write_count instrumented at every store; assertion that only-owning-tier writes |

### Validation experiment design — the cheap decisive cell

**Cell name:** `substrate_clock_hierarchy_tier_activity_validation_v1`

**Design:** Single-arm validation cell on substrate-LM pipeline at N=4096, V=4000, N_TRAIN=10^5 tokens, 3 seeds. Instrument the ClockHierarchy with `write_count`, `cross_tier_read_count` at every tier; run normal ingest. Verify:

1. **TIER ACTIVITY** — each T_k fires exactly `master_tick // DIVISOR_T_k` times by end-of-epoch (modulo final-partial-window for T_2/T_3). No silent tiers.
2. **TIER GATING** — when T_4 fires `consolidation_phase=True`, T_0 write_count freezes for the duration of the consolidation phase.
3. **NO CROSS-TIER WRITE LEAKAGE** — assertion `for k in range(5): write_count[T_k] == DIVISOR_T_k events fired` passes at end-of-epoch.
4. **TONIC-BASELINE DRIFT** — T_3 state[g_DA_tonic] changes monotonically OR drifts within bounded range (per Schultz tonic-DA biology), NEVER spikes (which would indicate phasic leak into tonic store).
5. **TIER-DOWNWARD MODULATION FIRES** — log per-T_3-tick the effective η_W applied at T_0; verify modulation actually changes T_0 behavior.

**HARD_PASS:** All 5 invariants hold; per-tier histograms show all T_k > 0; assertion-failure count = 0.

**HARD_FAIL:** Any invariant violated; signal an implementation bug requiring fix BEFORE running the 2×4 factorial efficacy test from parent drill.

This is a **structural validation, not an efficacy test**. Efficacy lives in the parent drill's `substrate_tau_neg_ratio_sweep_x_n_replay_sweep_2x4_v1` cell. Run the structural validation FIRST to ensure tier-collision bugs aren't confounding the efficacy measurements.

**Cost:** ~5 min CPU local (single arm, modest tokens).

**ROI:** catches implementation bugs cheaply BEFORE 30-45 min efficacy sweep wastes compute on confounded results.

---

## L5 — substrate-product implications

### Does the 5-tier clock unlock new substrate-as-LM capabilities, or just patch existing failures?

**BOTH, but the unlock is the bigger story.**

**Patches (existing failures):**
- TAU_NEG=50 → corrected to T_1 with TAU_NEG=12 (Skunkworks-caught empirical mismatch)
- Single-pass CLS-replay → corrected to T_4 with N_REPLAY=30 (matches brain ratio)
- by-construction-saturation on lock-in cells → T_1 audit identifies k_gamma=31 vs k_theta=1 imbalance

**Unlocks (new capabilities):**

1. **T_2 (E-LTP / synaptic tagging) is a NEW substrate primitive.** No current cell has a trace-half-life parameter. Adding it gives the substrate "forgetting-curve-aware retention" — atoms that get tagged-but-not-triggered fade over T_2 timescale, atoms that get triggered (T_4 consolidation visits them) stabilize. This IS the Ebbinghaus forgetting curve as a substrate property. **Capability:** substrate can decide WHAT to remember (not just what to ingest), based on consolidation gating.

2. **T_3 (tonic modulator baseline) is a NEW context-axis.** Currently substrate has per-context T learned over per-token window; T_3 gives it a slow context-drift baseline (5-10 mini-epochs). This is the substrate equivalent of "mood" or "background-arousal" — the parameter that distinguishes "substrate is in exploratory mode" vs "substrate is in consolidation mode." Composes natively with serotonin_mode_switch_bank_select_LM_v1 in flight.

3. **T_4 prioritized replay (RPE × novelty) is a 2-5x replay efficiency unlock** per Mattar-Daw 2018 + Schaul 2016 DQN-PER. Current substrate CLS-replay is uniform-sampling; prioritized-replay is the same compute cost with 2-5x retention gain. Brain analog: Michon 2025 + Joo-Frank 2018 2-stage prioritization (awake-SWR tags salience; sleep-SWR consolidates tagged).

4. **The 5-tier hierarchy IS the substrate-product time-axis differentiator.** LLMs have zero internal clock hierarchy — every token is one forward pass; no consolidation; no tonic baseline; no synaptic tag; no replay. Substrate with explicit 5-tier clock + brain-canonical ratios + observable per-tier metrics is structurally what LLMs cannot offer.

### Composability with cf-RPE chain-grade candidate (per-token tier)

cf-RPE delta is per-write modulator → lives at **T_0** as gate on Hebbian write magnitude. Integration: `delta_W = eta * input * output * (1 + alpha * cf_RPE)` at T_0. T_3 tonic-DA baseline modulates `eta` directly: `eta_effective = eta_base * g_DA_tonic`. The two compose multiplicatively as in biology (phasic-DA × tonic-DA gain modulation; Schultz-Aston-Jones 2012). **No conflict; clean composition.**

### Composability with K-bank (per-query / per-context tier)

K-bank routing decision (which bank to query) lives at **T_3** (per-context, mini-epoch-scale context-switch detection). T_3 tracks `context_id` and the `serotonin_mode_switch_bank_select_LM_v1` cell already operates at this tier. Tier-binding clarifies: bank-route decisions DON'T happen per-token (T_0) — they happen per-context-shift (T_3). Per-token only sees the SELECTED bank's W slice. **Clean composition; explicitly correct tier-binding.**

### Composability with c3 sequence-binding (chain-grade ratified CERT 586)

c3 compressed-sequence binding fits at **T_4** as the sub-routine that runs INSIDE consolidation_phase. During T_4 replay, c3 binds (k_{t-1}, k_t) pairs sampled from episode_buffer at the compressed-replay rate (Wilson-McNaughton 20x compression). The 5-tier hierarchy explicitly slots c3 into the consolidation cycle, replacing the current "run c3 at every batch boundary" implicit timing. **This is the biggest concrete change for c3:** moves it from ad-hoc per-batch invocation to systematic T_4 consolidation-phase invocation, gives it access to RPE-priority sampling.

### Composability with g1b autoregressive generation (CERT 587 MEASURED_MECHANISM)

g1b generation runs ENTIRELY at **T_0** (per-token forward decode). The clock hierarchy is INERT during inference (no T_1/T_2/T_3/T_4 ops needed for pure read-only decode). This means: clock hierarchy is a TRAIN/INGEST-time structure, not an inference-time overhead. Substrate-product inference performance is NOT changed by adding the hierarchy. **Confirms the clock hierarchy is structural-orthogonal to inference quality.**

---

## Cross-thread synthesis with prior drills

### vs parent timescale-ratio drill

Parent drill identified the 5 tiers + the TAU_NEG correction + multi-pass replay as load-bearing fixes. This drill specifies:
- **WHAT each tier IS** (the table above with brain analog + substrate mechanism)
- **HOW the data structure looks** (ClockHierarchy dataclass with modular arithmetic on master_tick)
- **HOW tiers gate each other** (slow→fast = modulate; fast→slow = emit events; no same-tier coupling)
- **HOW to validate** (5 invariants instrumented via write_count + cross_tier_read_count)

The parent drill's `substrate_tau_neg_ratio_sweep_x_n_replay_sweep_2x4_v1` efficacy cell now has a PRECURSOR: the `substrate_clock_hierarchy_tier_activity_validation_v1` structural cell. Run structural FIRST (catches bugs); efficacy SECOND (measures gains).

### vs CLS-drill #2 (continual-learning 5x)

CLS-drill #2 proposed dual-store (U1 hippocampus + W cortex) + 1:1 Hebbian generative replay. The 5-tier hierarchy formalizes this:
- U1 episodic store ↔ **T_4.episode_buffer** (with reservoir sampling)
- W cortex ↔ T_0-T_3 plastic weights (the substrate's existing W; tier-gated)
- 1:1 replay ratio ↔ T_4.N_REPLAY=10-30 (matches brain ratio + Klinzing-2019 budget)
- The 10x slow-cortex / fast-hippocampus rate ratio ↔ **eta_W during T_0 ingest vs eta_W during T_4 consolidation_phase**

### vs SWR-drill #5 (compressed-sequence binding)

SWR-drill identified compressed-sequence Hebbian binding as the missing sequence-link primitive. In the 5-tier hierarchy, **c3 compressed-replay lives at T_4 consolidation_phase**, with the compression-factor being implicit: T_4 replays at "tick = 1 per replay event" instead of "tick = 1 per master_tick." Replay events effectively SAMPLE pairs (k_{t-1}, k_t) within the T_1 STDP window — exactly what biological compressed-replay does (Mehta 2007 + Wilson-McNaughton 1994 + Liu 2019 inferred-chain reorganization).

This means: the clock hierarchy doesn't add c3 as a new mechanism; it RE-LOCATES c3 to its tier-correct slot (T_4 consolidation, not per-batch ad-hoc).

### vs modulatory-architectural taxonomy

Modulatory taxonomy identified 4 load-bearing axes: compose-function / K / compose-order / per-context-T. In the 5-tier hierarchy:
- compose-function → T_0 (per-token write rule)
- K bank-count → static config (no tier; orthogonal)
- compose-order → T_0 update-rule structure
- per-context-T → T_3 (tonic baseline updates context-T learned param)

The 5-tier hierarchy is **structural-orthogonal to the modulatory taxonomy**: modulatory taxonomy tells you WHAT to compose; clock hierarchy tells you WHEN ops fire. Combined, they fully specify substrate parameter tuning.

---

## Falsifiable predictions (pre-registered)

| Prediction | HARD_PASS | HARD_FAIL | P_deflated |
|---|---|---|---|
| Structural validation cell shows all 5 tiers fire correctly | write_count[T_k] > 0 for all k ∈ {0,1,2,3}; T_4 fires exactly 1x at end | any T_k = 0; cross-tier write leakage detected | 0.80 (mechanically should hold if implemented correctly; high P) |
| Adding T_2 tagging-decay lifts retention on continual ingest | ≥0.05 BPC lift on continual-learning cell at α=0.5 | within 0.02 BPC OR worse | 0.30 (novel mechanism; brain precedent but unclear substrate yield) |
| T_3 tonic-baseline drift improves context-switch handling | ≥0.05 BPC lift on context-switch eval vs T_3-disabled | within 0.02 BPC OR worse | 0.30 (composable with in-flight 5HT cell; brain-supported) |
| T_4 prioritized-replay beats uniform-replay at fixed N_REPLAY | ≥0.10 BPC lift on retention test at N_REPLAY=10 | within 0.05 BPC | 0.40 (strong ML precedent DQN-PER; brain-supported Mattar-Daw + Michon) |
| Tier-collision detection catches at least 1 bug if introduced as control | inject deliberate cross-tier write; assertion fires within 100 ticks | injection goes undetected | 0.90 (testing the test; high P) |
| 5-tier hierarchy unifies all parent-drill corrections (combined) | 3 of 4 efficacy preds HARD_PASS | 0-1 HARD_PASS | 0.35 (combined; novel-synthesis cap @ 0.50; deflated to 0.35) |

P_deflated values include 0.15-0.25 calibration penalty per [[feedback-lit-scan-calibration-penalty]]. All predictions HAVE explicit HARD_FAIL thresholds.

---

## Cheap decisive test (THIS drill's recommended cell)

**PRIMARY CELL:** `substrate_clock_hierarchy_tier_activity_validation_v1`
- Single-arm; structural-validation only; ~5 min CPU local
- Validates implementation BEFORE efficacy sweep wastes compute
- HARD_PASS: all 5 tier invariants hold
- HARD_FAIL: any invariant violated → implementation fix required

**SECONDARY CELL (chains on PRIMARY pass):** parent drill's `substrate_tau_neg_ratio_sweep_x_n_replay_sweep_2x4_v1`
- 2×4 factorial; 8 arms + vehicle; ~30-45 min CPU local
- Tests TAU_NEG correction × N_REPLAY count efficacy
- Only run if PRIMARY validates

**TERTIARY CELL (composability check):** `substrate_clock_hierarchy_t2_tagging_continual_learning_v1`
- 3-arm: (no T_2 tagging) vs (T_2 tagging with TRACE_HALF_LIFE=200) vs (T_2 tagging with TRACE_HALF_LIFE=1000)
- On c1 CLS-replay continual-learning task at α=0.5
- HARD_PASS: medium-T_2 arm beats no-tagging by ≥0.05 BPC
- HARD_FAIL: tagging hurts or no diff

---

## META atoms candidate

1. **clock-hierarchy-implementation-is-modular-arithmetic-on-single-master-tick**: not per-tier independent clocks; integer-div derivation; matches Fusi-Drew-Abbott cascade design pattern.
2. **tier-gating-directionality-slow-modulates-fast-fast-emits-events**: invariant that makes tier-collision bugs detectable; never violated.
3. **per-tier-write-count-and-cross-tier-read-count-are-validation-instruments**: structural correctness instrumented separately from efficacy metrics.
4. **T_2-synaptic-tagging-is-the-missing-substrate-primitive**: trace-half-life parameter; brain analog Frey-Morris 1997 E-LTP synaptic-tagging-and-capture.
5. **clock-hierarchy-is-train-time-structure-not-inference-time-overhead**: g1b decode runs entirely at T_0; hierarchy inert during read-only inference; no inference performance penalty.
6. **c3-and-CLS-replay-and-N_REPLAY-all-live-at-T_4-consolidation_phase**: the right tier-binding for sequence-binding + episodic-replay + prioritized-replay; replaces ad-hoc per-batch invocation.

---

## Citations (verified count: 6 external this drill + 6 internal = 12 total; parent drill's 13 are still in force)

**External (web-search verified THIS drill):**

1. Fusi, Drew & Abbott (2005, Neuron, Vol. 45, No. 4, pp. 599-611) "Cascade models of synaptically stored memories." Multi-state metaplastic-cascade synapse; canonical multi-timescale plasticity data structure. [Penn State](https://pure.psu.edu/en/publications/cascade-models-of-synaptically-stored-memories) [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0896627305001170)

2. Magee group BTSP (Behavioral Timescale Synaptic Plasticity) — plateau-potential-induced seconds-window plasticity in CA1/CA3 place fields; one-shot place-field formation via 100ms-plateau + seconds-window association. Confirms T_2 (seconds-window) tier exists biologically distinct from STDP (T_1) and CLS (T_4). [Bidirectional plasticity rapidly modifies hippocampal representations eLife](https://elifesciences.org/articles/73046) [Behavioral timescale synaptic plasticity Nature Neuroscience](https://www.nature.com/articles/s41593-026-02214-2) [JNeurosci Burst review](https://www.jneurosci.org/content/45/46/e1332252025/tab-figures-data)

3. Multi-timescale memory dynamics + AuGMEnT-style hybrid leaky/non-leaky memory units for RL with attention-gated memory. Confirms per-tier eligibility-trace decay rates μ_l, λ_k as the standard implementation idiom. [PMC AuGMEnT multi-timescale](https://pmc.ncbi.nlm.nih.gov/articles/PMC6055065/) [Adaptive multi-timescale eligibility traces](https://www.sciencedirect.com/science/article/abs/pii/S0921889021002670) [Frontiers AuGMEnT](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2018.00050/full)

4. Mattar & Daw (2018, Nat Neurosci) "Prioritized memory access explains planning and hippocampal replay." Mathematical theory: priority = NEED × GAIN. Substantially outperforms uniform sampling. Plus Schaul 2016 DQN-PER ML re-validation. (Referenced in SWR-drill citations 80-90.)

5. Frey & Morris (1997, Nature, 385:533-536) "Synaptic tagging and long-term potentiation." E-LTP synaptic-tagging-and-capture; T_2 tier brain analog with ~1-2 hour timescale, protein-synthesis-independent traces tagged for later L-LTP consolidation triggered by neuromodulator. [Frey-Morris Nature 1997](https://www.nature.com/articles/385533a0)

6. Nengo/Spaun multi-area modular cognitive architecture (Eliasmith group). Confirms that large-scale neural-cognitive simulators use modular per-area state with shared global integration; precedent for substrate's per-tier modular design. [Nengo Frontiers 2013](https://frontiersin.org/articles/10.3389/fninf.2013.00048/full) [Large-scale Nengo cognitive model design](https://www.sciencedirect.com/science/article/abs/pii/S2212683X16300317)

**Internal substrate notes referenced:**

1. `notes/research_substrate_brain_timescale_ratio_2x_drill_2026-06-23.md` (parent: 5-tier declaration + TAU_NEG correction + multi-pass replay)
2. `notes/research_brain_continual_learning_CLS_5x_drill_2026-06-22.md` (CLS dual-store + Hebbian generative replay)
3. `notes/research_brain_hippocampal_SWR_sleep_replay_5x_drill_2026-06-22.md` (compressed-sequence binding; prioritized-replay; consolidation-phase gating)
4. `notes/research_substrate_modulatory_architectural_parameter_taxonomy_2026-06-23.md` (4 load-bearing modulatory axes)
5. `notes/c1_cls_replay_continual_ingest_complete_2026-06-22.md` (substrate operating below α=0.5 cliff under codebook-NN)
6. CERT 586 (c3 sequence-binding chain-grade) + CERT 587 (g1b autoregressive generation MEASURED_MECHANISM) — substrate self-evidence ratifications

---

## Companion exp_dev hand-off

Filed at `d:/AI/hd-instrument/notes/exp_dev_handoff_research_substrate_5_tier_clock_hierarchy_implementation_2026-06-23.md`.

Primary anchor: `substrate_clock_hierarchy_tier_activity_validation_v1` (structural validation; gate before efficacy).
Secondary anchor: chained to parent drill's `substrate_tau_neg_ratio_sweep_x_n_replay_sweep_2x4_v1` (efficacy after structural pass).
Tertiary anchor: `substrate_clock_hierarchy_t2_tagging_continual_learning_v1` (T_2 tagging composability check on c1 CLS task).

---

End of research note.
