---
problem: the_register_write_path_has_a_hard_capacity_wall
status: SOLVED
bar: "PASSES only with ALL of: 1. A CONTINUOUS leaky/recency WRITE on AccumulateRegister.add_event (S = lambda*S + bind(role, item), lambda swept) -- the ASYMMETRIC brain-faithful form (NOT symmetric divisive -- W10 measured dead; NOT a hard queue -- W11 less faithful). Copy the computation; sweep lambda. NO external LLM. 2. Lifts a capacity-bound downstream task CI-separated over the flat-write floor -- recent-event recovery at high store load, AND/OR who-did-what at high load -- the floor = the current flat sum (lambda=1) recomputed on the same population. The info-free twin (shuffled keys, or the flat lambda=1 write) LOSES CI-separated; report CI half-width + null p95; no number crosses populations. A POSITIVE control the metric can move. 3. The recency FORM is the brain's (W11): the recovery-by-recency curve is GRADED/monotonic (intermediate positions), not a step (queue), reproducing the primate-PFC gradient shape. 4. If OLD events also matter: a content/salience-gated commit into the existing HDFactStore (reuse the MDL/schema gate; commit by SALIENCE, not eviction-order) -- MEASURED to preserve old-event recovery the leaky write alone loses, WITHOUT a new consolidation mechanism. 5. One-screen summary: lambda swept -> floor -> twin -> capacity/recency lift -> form-fidelity (graded vs step) -> verdict. A rigorous NEGATIVE is a FULL PASS."
result: "Synthetic controlled load sweep (the correct instrument for a capacity wall -- load is the IV), D=256, V=100, chance=0.01, 30 trials/load, trial-bootstrap 2000x. RECENT-4 recovery (the reader-relevant quantity): the write-time leaky recency gain = 1.000 at EVERY load Nin{16..768}; the STRONGEST flat floor (flat sum + landed serial crosstalk-cancellation readout) holds to N=64 (0.983) then COLLAPSES (0.175@128, 0.100@256, 0.067@384, 0.025@512, 0.067@768). Paired lift LEAKY - flat+SERIAL is CI-separated from N=128 onward: +0.825 [+0.750,+0.892] @128 -> +0.900 [+0.833,+0.958] @256 -> +0.975 [+0.942,+1.000] @512 (ns at N<=64 where the serial readout already saturates -- the lift appears exactly where the floor breaks). SECOND STORE (salience-gated HDFactStore hand-off, N=200, commit budget 20%, 30 trials, 2000x): salient-event recall weighted-OR gate 0.643 [0.620,0.665] vs FIFO/eviction-order floor 0.247 (+0.395 [+0.366,+0.424] SEP); OR > PE-only 0.530 (+0.112 SEP) and > CONG-only 0.539 (+0.103 SEP); leaky-buffer-alone 0.056. Witness 9/9."
floor: "STRONGEST floor, recomputed on the same population: the flat sum (lambda=1) read by decode_serial (the LANDED theta-gamma crosstalk-cancellation readout -- NOT the naive flat+argmax strawman). Recent-4 recovery 0.983 @N=64 -> 0.100 @N=256 -> 0.025 @N=512. Flat+argmax is even weaker (0.60@64 -> 0.125@256). For the second store: the FIFO/eviction-order commit floor = salient-recall 0.247."
controls: "WRITE PATH: (1) info-free twin = read the leaky store at SHUFFLED keys -> collapses to ~0.02 (chance; excludes 'the keys carry it for free'). (2) flat lambda=1 write IS the info-free-write comparison (the floor itself). (3) FORM control = a hard bounded QUEUE (discrete slots): step curve [1.00,1.00,0.01] vs the leaky GRADED monotonic curve [1.00,0.958,0.508] (excludes 'it's just a discrete buffer' -- reproduces the primate 66/45/39 gradient shape). (4) POSITIVE control: at N=256 the leaky write recovers the NEWEST event 1.000 vs flat(argmax|serial) 0.133 (metric moves). SECOND STORE: (5) FIFO/eviction-order floor (excludes 'any commit helps' -- the brain positively rules out eviction-order). (6) info-free RANDOM-commit twin 0.234 (excludes 'the budget alone does it'). (7) SELF-derived-salience NEGATIVE control = commit by the register's own readback confidence -> 0.220, does NOT CI-beat FIFO (-0.028, ns) -- reproduces the on-disk exp_attention_salience_reliability_gate HARD_FAIL; salience MUST be an independent channel. (8) single-channel PE-only / CONG-only each miss one U-shape extreme (excludes 'one axis suffices'). (9) POSITIVE control: OR 0.638 vs leaky-only 0.047 (+0.592) rescues salient-old the buffer loses."
files_changed: "experiments/exp_register_leaky_write_capacity_v1.py, experiments/exp_register_salience_gated_handoff_v1.py, experiments/exp_register_multitimescale_cascade_v1.py, verification/test_register_leaky_write.py, notes/problems/the_register_write_path_has_a_hard_capacity_wall/{SOLVED.md, PROPOSED_HDLAB_DIFF.md, research_consolidation_salience_gate_2026-08-29.md}"
reverify: ".venv/Scripts/python.exe verification/test_register_leaky_write.py"
---

## What this is

The brief asked me to replace the register's flat running sum (`S = S + bind(role,item)` -- a hard capacity wall) with
the brain's **asymmetric leaky/recency write** (`S = lambda*S + bind(role,item)`) and prove it lifts a capacity-bound
downstream task, with the recency FORM matching the primate gradient and a content/salience-gated hand-off into the
existing `HDFactStore` for the old events the leak decays out. **All five bar items are met (witness 9/9), the
mechanism is copied from primate PFC (operation copied, lambda swept), and every wall was drilled to a brain mechanism via
two research drills.** This is a POSITIVE capability result, not a negative.

## The one thing I checked FIRST that changed the framing (the enabling move)

The brief's floor is "the flat sum (lambda=1)." But the flat sum is not only read by argmax -- `decode_serial` (LANDED,
theta-gamma crosstalk cancellation) recovers the RAW flat sum to ~0.98 @ M=64. **So the honest floor is flat+SERIAL,
not flat+argmax**, or I'd be beating a strawman. I probed it before building anything (`scratchpad/probe_crux`): the
strong serial readout ALSO collapses once load exceeds ~0.25*D (recent-4: 0.98@64 -> 0.18@128 -> 0.10@256 -> ~0@384+),
while the leaky write holds recent-4 = 1.000 to N=768. **The write mechanism is a genuine capability lever OVER the
strongest landed readout, in exactly the book-scale regime (hundreds of events) where the brain uses recency +
consolidation rather than joint cancellation over hundreds of items** -- which is itself the more brain-faithful stance
(no evidence the brain does successive-interference cancellation across a whole superposed history).

## What I built and measured

**1. The leaky/recency write (`exp_register_leaky_write_capacity_v1.py`).** The proposed `AccumulateRegister` diff
mirrored in-experiment: `leak=0.0` is byte-identical to the flat sum; `leak>0` reads the raw recency-weighted sum
`S = sum  (1-leak)^age * event` (argmax cleanup, scale-invariant). Load swept 16->768 (well past the ~0.25*D wall):

| N | flat+argmax | flat+SERIAL (floor) | LEAKY | twin | lift vs flat+serial |
|---|---|---|---|---|---|
| 64 | 0.600 | 0.983 | 1.000 | 0.02 | +0.017 (ns -- floor saturates) |
| 128 | 0.300 | 0.175 | 1.000 | 0.02 | **+0.825 [+0.750,+0.892] SEP** |
| 256 | 0.125 | 0.100 | 1.000 | 0.01 | **+0.900 [+0.833,+0.958] SEP** |
| 512 | 0.067 | 0.025 | 1.000 | 0.02 | **+0.975 [+0.942,+1.000] SEP** |

- **The fundamental single-store trade (W10 confirmed, brain-faithful):** the leaky write buys RECENT recovery by
  DECAYING OLD -- its UNIFORM (all-events) recovery collapses 0.45->0.019. This is not a flaw; it is why a second store
  is needed, and it is exactly the bounded-buffer-plus-consolidation architecture of biological WM.
- **lambda frontier @N=256:** recent = 1.000 across lambda=0.70-0.95 (uniform monotonically trades down 0.10->0.035); lambda=1.0
  (flat) recent=0.208; lambda=0.50 over-decays (recent 0.875). A wide brain-plausible operating band, not a knife-edge.
- **FORM fidelity (bar item 3):** the recovery-by-recency curve is GRADED/monotonic -- 3-bin newest/mid/oldest
  **[1.00, 0.958, 0.508]** -- reproducing the primate PFC 66/45/39 monotonic gradient SHAPE (Konecky 2017). A hard
  bounded QUEUE is a STEP: **[1.00, 1.00, 0.008]**. So the faithful form is the CONTINUOUS leak, not discrete slots.

**2. The salience-gated second store (`exp_register_salience_gated_handoff_v1.py`).** The displaced old events commit
into the REAL `hdlab.HDFactStore` (glass-box, content-addressed, never-forgets) under a fixed budget. 5-arm gate
discriminator from the salience research drill (salient events = the SLIMM U-shape extremes: high prediction-error OR
high schema-congruence):

| gate | salient-recall | what it excludes |
|---|---|---|
| leaky-only (no 2nd store) | 0.056 | -- the buffer alone loses ~95% of salient events |
| **FIFO / eviction-order (floor)** | 0.247 | the eviction-order rule the brain positively rules out |
| SELF-derived (neg control) | 0.220 | reproduces on-disk HARD_FAIL (commits by recency, not salience) |
| TWIN (random commit) | 0.234 | info-free |
| PE-only | 0.530 | misses the congruent extreme |
| CONG-only | 0.539 | misses the surprising extreme |
| **weighted-OR (U-shape)** | **0.643** | catches both extremes -- commit-most-salient |

OR - FIFO = **+0.395 [+0.366,+0.424] SEP**; OR - PE +0.112 SEP; OR - CONG +0.103 SEP; OR - TWIN +0.409 SEP;
SELF - FIFO -0.028 (ns -- the self-derived gate does NOT beat eviction-order). Positive control: OR 0.638 vs
leaky-only 0.047 (+0.592). **So the register->HDFactStore hand-off recovers the salient old events the leaky write
decays out, the commit must be by SALIENCE not eviction-order, and the salience must come from an INDEPENDENT channel
-- all three matching both the brain (Tse/van Kesteren/Lisman-Grace; VTA/LC compute PE separately) and our own disk.**

## The brain drills (two, primary-source-verified -- this is where the fidelity is)

- **Write mechanism** (`notes/research_register_write_path_asymmetric_recency_suppression_2026-08-29.md`, from the
  parent problem, 13 sources): asymmetric leaky recency = MEASURED/PINNED-WEAK (Warden & Miller 2007 Cereb Cortex;
  Konecky, Smith & Olson 2017 J Neurophysiol -- a monotonic recency gradient in primate PFC single units). Corrects
  the Buschman 2011 citation (that is a LOAD effect, simultaneous display -- not the recency cite).
- **Consolidation salience gate** (`research_consolidation_salience_gate_2026-08-29.md`, this problem, primary-verified):
  the brain's transfer gate is a WEIGHTED-OR of prediction-error and schema-congruence converging on ONE synaptic
  tagging-and-capture switch (Redondo-Morris 2011; Lisman-Grace 2005; Takeuchi 2016; van Kesteren 2012 SLIMM
  U-shape); **commit-most-salient, NOT oldest-evicted, is PINNED (P=0.78)**; geometric `lambda^age` is the faithful
  per-trace decay form (power-law is emergent from mixing timescales -- so register(geometric)+store(never-forget) is
  itself the brain's system-level power-law retention); and the on-disk constraint that the PE signal must be an
  INDEPENDENT channel (a self-derived gate is fooled by correlated error -- HARD_FAIL). Q2: pinging-silent-WM work
  (Yang-He-Cai 2025) shows genuinely deprioritized items do NOT reactivate -- so the 2nd-store hand-off IS necessary
  for the displaced tail, not just a better readout.

## What I did NOT establish / would withdraw first

- **Real-text end-to-end.** The capacity sweep is synthetic (random FHRR codes). This is the CORRECT instrument for a
  capacity wall (you must control load as the IV, which real text does not let you do), and the wall is a property of
  the FHRR superposition ALGEBRA, which is content-agnostic -- so a real-corpus run would measure the same algebra at
  whatever loads the corpus happens to reach. But I did not wire the leaky register into the live who-did-what /
  situation-model path and re-measure end-to-end; that is the landing + a measurement follow-on (Next Steps). This is
  the first claim I would qualify: "lifts a capacity-bound downstream task" is proven on the register's own
  recent-recovery readout, not yet on a full reading task's final score.
- **The salience channels are modelled, not read from the live PE/MDL organs.** The 5-arm result proves the GATE
  POLICY (weighted-OR of two independent channels, commit-most-salient) and its controls; it uses modelled PE/CONG
  latents with observation noise, not the live `script_grain` MDL drop / a live prediction-error read. Wiring the
  real channels is the second-store landing's job. The POLICY and its brain-faithfulness are established; the exact
  live-channel reliability is not.
- **lambda and theta are swept parameters, not adopted numbers** -- I report the frontier, not a single tuned value.
- **The activity-adaptive-leak variant UNDERPERFORMED in my impl (recent-4 ~0.5 vs fixed 1.0) -- but that is a weak,
  uncalibrated parameterization (`target=8`), NOT a refutation of the adaptive form.** I did not tune it, because the
  FIXED geometric leak fully meets the bar AND is the better-pinned per-trace form (the research drill: a single store
  should carry ONE geometric leak; the system-level power law is emergent from mixing the register's geometric decay
  with the never-forget store). Adaptive/divisive is the same OUR-EXTENSION class as the read-side divnorm, so fixed
  geometric is the more brain-faithful default; a proper adaptive gain sweep is an optional follow-on, not a wall.

## FIDELITY DEEPENING (post-submission push, owner-requested: "if the brain can do it, we can once we understand it")

Interrogating my OWN solution for the biggest remaining fidelity gap surfaced one, and it is real: **the submitted
register uses a SINGLE exponential timescale, but the brain's WM holds a MEASURED SPECTRUM of timescales.** Grounded
by a dedicated research drill (`research_multitimescale_cascade_2026-08-29.md`, primary-verified): Bernacchia, Seo,
Lee & Wang 2011 (Nat Neurosci, PMID 21317906) MEASURE a power-law RESERVOIR of memory time constants (100s of ms to
10s of s) in monkey PFC single units -- the WM stage; Murray 2014 confirms a hierarchy of intrinsic timescales
across cortex. So "carry a SPECTRUM, not one lambda" is **PINNED (P~0.80)**. So I built and measured a
**MULTI-TIMESCALE register** (`exp_register_multitimescale_cascade_v1.py`): K running sums at leaks spanning
fast->slow (0.5..0.995), each event read from the timescale holding the clearest trace (a gold-blind best-margin
readout -- the same CA1-comparator confidence `decode_gated` already uses).

**CITATION CORRECTION (the drill caught my own overreach):** I first credited Fusi 2005 / Benna-Fusi 2016 for this.
They are the SYNAPTIC-CONSOLIDATION stage and are MODELS; their per-synapse capacity theorem comes from BIDIRECTIONAL
COUPLING (value flows fast->slow) and does NOT transfer to my INDEPENDENT superposition sums. And what I measured is
TEMPORAL REACH (recency window), NOT Benna-Fusi capacity scaling (a superposition register's simultaneous capacity is
set by D). The WM-stage spectrum claim rests on Bernacchia+Murray (measured); the K-independent-sums+best-margin
readout is my OUR-INVENTION implementation of that pinned spectrum.

**MEASURED (D=256, 30 trials, bootstrap 2000x):** the cascade recovers ~3x more of the recency window than a single
leak, CI-separated at every load, WITHOUT sacrificing recent recovery, and -- decisively -- the reach stays FINITE, so
the 2nd store is still needed:

| N | cascade reach (pos>0.5) | single-lambda reach | window recovered cascade vs single |
|---|---|---|---|
| 128 | 29 | 6 | 28.8 vs 7.6  (+21.2 CI-sep) |
| 256 | 21 | 6 | 26.6 vs 7.5  (+19.1 CI-sep) |
| 512 | 20 | 6 | 25.3 vs 7.6  (+17.7 CI-sep) |
| 768 | 18 | 5 | 24.8 vs 7.2  (+17.6 CI-sep) |

cascade recent-4 = 1.000 (does not trade recent for window); info-free shuffled-key twin collapses (~0.01). The
cascade's recovery-vs-position curve is a SMOOTH graded gradient over ~24 positions where the single leak is a sharp
cliff at position 6 -- a materially better match to the brain's graded/power-law retention than my submitted form.

**What this means (honest):** (1) my single-leak solution is a correct FIRST-ORDER approximation that PASSES the bar,
but the higher-fidelity brain form is a **multi-timescale spectrum** -- I flag this as a high-value next-problem seed,
not a silent gap. (2) The spectrum EXTENDS the active buffer ~3x but does NOT replace consolidation -- its reach is
finite at extreme load, so the salience-gated 2nd store is genuinely necessary (this strengthens, not weakens, the
two-store architecture). (3) The gain is partly a resource story (5 sums vs 1) -- the pure-fidelity win is the GRADIENT
SHAPE (graded over a wide window, the brain's measured spectrum) and it composes with the 2nd store. (4) A more
faithful COUPLED superposition cascade (value flowing fast->slow) is possible but ~ a reparameterised bank of leaks
(gamma-shaped kernels), so it changes the forgetting-curve SHAPE not the capability -- a can-fail test to run LAST
(P~0.35-0.40 it beats independent sums). Witness locks the measured result (checks 10-11).

## KEY REALIZATIONS

1. **Recompute the floor as the STRONGEST landed readout before claiming a lift.** The flat sum's real floor is
   flat+SERIAL (decode_serial recovers it to 0.98@M=64), not flat+argmax. Probing that first (a) killed a potential
   strawman and (b) located the exact regime where the write mechanism genuinely wins (past ~0.25*D, where even
   serial cancellation collapses). The lift is honestly "ns" at low load and CI-separated only where the floor breaks.
2. **The capacity wall is a WRITE-stage property, and the two most brain-faithful facts are the same fact.** The brain
   does NOT hold hundreds of events and jointly decode them (our serial trick); it keeps a recency-gated buffer and
   consolidates. So the fidelity argument (recency + consolidation) and the capability argument (leaky beats serial
   past D/4) point the same way -- the rare case where the more brain-faithful mechanism is also the bigger lever.
3. **The single-store trade is not a bug to engineer around -- it is the architecture.** Leaky UNIFORM recovery
   collapsing is the SIGNAL that you need the second store; forcing one store to do both jobs is exactly what the
   flat sum does and why it walls.
4. **A salience gate is only as good as its channel independence.** The self-derived gate (commit by the register's
   own confidence) fails because confidence tracks RECENCY -- it commits events already safe in the buffer. This
   reproduces an on-disk HARD_FAIL AND the brain (PE is computed by a separate VTA/LC circuit). The negative control
   is the same shape as the mechanism's own failure mode.
5. **Geometric decay in ONE store + a never-forget store = the brain's system-level power-law retention** -- so the
   two-store split is not an engineering convenience, it is what produces the empirically-observed forgetting curve.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md -- register / situation_model_accumulate write path)

The parent's section 2b entry flagged the register WRITE path as "the BIGGEST gap found" and predicted the fix. Now MEASURED
on our organ, add:

> **AccumulateRegister WRITE path.** The flat running sum (`S=S+bind(role,item)`) is an OUR-INVENTION with a hard
> capacity wall; even the landed serial crosstalk-cancellation readout collapses past ~0.25*D (recent-4: 0.98@64 ->
> 0.10@256 -> 0.03@512). The brain-faithful fix -- an ASYMMETRIC leaky/recency WRITE `S=lambda*S+bind` -- holds recent-4 =
> 1.000 at ANY load (to N=768), CI-separated over the strongest flat floor from N=128 (+0.83->+0.98), and reproduces
> the primate PFC 66/45/39 monotonic recency-gradient SHAPE (3-bin [1.00,0.96,0.51]) where a discrete queue is a STEP
> ([1.00,1.00,0.01]). Fidelity: asymmetric leaky recency = **MEASURED / PINNED-WEAK** (Warden & Miller 2007; Konecky
> 2017 primate PFC single-unit). Geometric `lambda^age` = the faithful per-trace form (power law is emergent from mixing
> timescales). The leaky write DECAYS OLD events (fundamental single-store trade) -> paired with a **content/salience-
> gated commit into HDFactStore**: commit-most-salient (weighted-OR of prediction-error + schema-congruence, the
> SLIMM U-shape) is **PINNED (P=0.78)**, eviction-order is the one rule the brain rules out, and the salience signal
> must be an INDEPENDENT channel (a self-derived gate HARD_FAILs -- matches on-disk `exp_attention_salience_reliability_gate`
> and the VTA/LC-separate-circuit brain fact). CLS/recency-chunked consolidation stays REFUTED as the 2nd-store analogy.
>
> **NEW FIDELITY NOTE (post-submission deepening):** a SINGLE geometric leak is a FIRST-ORDER approximation; the brain's
> WM holds a MEASURED SPECTRUM of timescales (a power-law reservoir of time constants in primate PFC single units --
> Bernacchia 2011 PMID 21317906; a hierarchy across cortex -- Murray 2014). MEASURED on our organ: a multi-timescale
> register (K leaks fast->slow, read per-event from the clearest-trace level) recovers ~3x more of the recency window
> than a single leak (CI-separated at every load), with a smooth graded gradient, WITHOUT sacrificing recent -- and its
> reach stays FINITE, so the salience-gated 2nd store is still needed. WM multi-timescale spectrum = **PINNED (P~0.80)**.
> CORRECTION: Fusi 2005 / Benna-Fusi 2016 are the CONSOLIDATION stage + MODELS (bidirectional-coupling capacity theorem);
> do NOT cross-credit them to the WM stage, and the measured ~3x is TEMPORAL REACH, not Benna-Fusi capacity scaling.
> **SEPARATE AUDIT UPGRADE (from the same drill, for the VSA-binding entry):** Watters 2026 (PMC12893052) is DIRECT
> single-unit+population evidence that primate frontal cortex holds multi-item WM as a GAIN-WEIGHTED SUPERPOSITION
> (weighted vector sum) beating discrete slots -- so the substrate's superposition-REGISTER FORM (weighted-combination
> readout) is now **PINNED at the population-code level**, a meaningful dent in "VSA binding is unpinned" (caveat: it
> pins the weighted-combination READOUT, NOT the `bind()` algebra itself).

## Adjacent-component evaluation (owner-requested -- capability / limitation / optimization / brain-status; seeds next problems)

| component | capability | limitation | optimization opportunity | brain-foundational status |
|---|---|---|---|---|
| `AccumulateRegister` flat write | accumulates a whole event history in O(1) space | hard capacity wall; recent lost past ~0.25*D even with serial readout | **THIS problem: add a `leak` write option (proposed diff)** | flat sum = **OUR-INVENTION** (no biological analogue); leaky recency = PINNED-WEAK |
| **MULTI-TIMESCALE register spectrum** (this deepening) | **MEASURED: recovers ~3x more of the recency window than single-lambda (CI-sep), smooth graded gradient, recent unharmed** | needs K sums (partly a resource story); measures TEMPORAL REACH not capacity; reach still finite -> 2nd store still needed | **high-value next-problem seed: a `leak` SPECTRUM on the register** -- higher-fidelity than the single-lambda I submitted | WM multi-timescale spectrum = **PINNED (P~0.80)** -- power-law reservoir of time constants MEASURED in primate PFC (Bernacchia 2011 PMID 21317906; Murray 2014). NB: Fusi 2005 / Benna-Fusi 2016 are the CONSOLIDATION stage + MODELS -- do NOT cross-credit; their capacity theorem needs bidirectional coupling my independent sums lack |
| `situation_focus.ChunkedFocus` (Cowan ~4-chunk WM focus) | a small attentional focus over the register | **if implemented as a HARD fixed-slot count**, it is the discrete-slot form our own write-path result argues against | **a GRADED gain-weighted focus (effective ~4 from competition, not a literal 4 slots)** -- same graded-beats-slots lesson as this problem | Cowan-4 is behavioral; the strong direct-neural cite is **Watters 2026 (PMC12893052)** -- primate frontal WM is a gain-modulated compositional (weighted-sum) code beating slots. (Corrections: Daume 2024 is theta-gamma PAC control, NOT slots-vs-resource; the 2026 CDA replication UPHELD the asymmetry -- only the slot INTERPRETATION is undermined, by Watters.) A fixed-slot impl is **OUR-INVENTION** worth a fidelity audit |
| `decode_serial` / `decode_serial_pooled` | recovers the flat sum to ~1.0 up to M~0.25*D via crosstalk cancellation | collapses past 0.25*D; O(m*iter); needs ALL keys; **not a brain mechanism** (no evidence of joint cancellation over a whole history) | keep for the MODERATE-load regime; the leaky write is the book-scale answer | theta-gamma readout PINNED-ish; the successive-interference-cancellation USE is our engineering, not circuit-cited |
| `situation_model_multibank` sharding | smaller per-bank load -> milder crosstalk | orthogonal to recency; still flat WITHIN a bank | **compose: apply `leak` per-bank** (each bank smaller -> milder leak, more recent capacity) -- a clean follow-on | routing = our engineering; per-bank capacity = same algebra |
| `HDFactStore` (2nd store) | never-forgets, content-addressed, glass-box, trust-tagged | commit gate not yet wired to live PE/MDL channels | **wire the salience gate to the live prediction-error + `script_grain` MDL-drop channels** (this problem specified + validated the POLICY) | the store is the brain-correct hippocampal-episodic-index analog (established); the missing piece is the gate wiring |
| `bundling.bundle` `recency` modulator | already computes the geometric decay (read-time batch reweight) | global (reweights every in-scope bundle); not per-register | superseded by a per-register `leak` param (proposed diff) -- cleaner, local | the decay OPERATION is the leaky write; making it per-register is the fidelity improvement |
| `script_grain` / `grounding_acquisition_loop` MDL gate | a schema-congruence (description-length) signal already computed | gates LEARNING content, not register eviction | **reuse as the CONG channel of the salience gate** (validated as one of the two U-shape axes) | MDL two-part code = Perfors-Tenenbaum, brain-defensible schema-congruence proxy |

## Proposed hdlab change (strategy lands it, Q111)

**Full concrete diff in `PROPOSED_HDLAB_DIFF.md`.** Two additive, default-byte-identical changes:
1. `hdlab/situation_model_accumulate.py`: a `leak` param on `AccumulateRegister` (0.0 = flat, byte-identical;
   >0 = asymmetric leaky recency write reading the raw recency-weighted sum). Thread through
   `make_situation_register` + the multibank backend (per-bank).
2. A thin `register_consolidation` helper: `salience = max(w_pe*PE, w_cong*CONG)`, commit to `HDFactStore` iff
   `> theta` (swept). PE from an INDEPENDENT prediction channel; CONG from the existing MDL drop. Commit-most-salient,
   never eviction-order; never self-derived. No change to `hd_fact_store.py`.

## TLDR (plain language)

The reader's short-term memory adds every new event into one running total, and that total blurs into noise once it
holds more than about 60 events -- at which point even the cleverest read-back trick we already have can't pull out
even the events that JUST happened. The brain doesn't do this: each new event gently pushes down the older ones, so
the most recent things stay crisp no matter how much came before, and whatever fades gets handed off to permanent
memory. I built that. With the new "fading" write, the most recent events stay perfectly readable at ANY load (all
the way to 768 events), where the old flat total scores near zero -- and the fade curve has exactly the smooth,
graded shape measured in monkey prefrontal cortex, not the all-or-nothing shape of a fixed-size buffer. The cost is
that old events fade out -- so I added the brain's second half: a gate that copies the IMPORTANT fading events
(surprising ones or ones that fit the story) into the permanent fact store. That gate recovers 64% of the important
old events where the fading memory alone recovers 6% -- and, crucially, it has to pick by IMPORTANCE, not by "oldest
first," and the importance has to be judged by a SEPARATE signal (judging it from the memory's own confidence fails,
exactly as it failed once before on disk, and exactly as the brain avoids by computing surprise in a different
circuit). Everything is proven in experiments; the strategy session lands the two-line change to the live memory.

## QUESTIONS

None.

## NEXT STEPS

1. (strategy) Re-verify `verification/test_register_leaky_write.py` (**11/11**) and land the `PROPOSED_HDLAB_DIFF.md`
   change 1 (`leak` param on `AccumulateRegister` + thread through `make_situation_register`/multibank). Fold the AUDIT
   UPDATE into `notes/BRAIN_FOUNDATIONAL_AUDIT.md`.
The research drill's recommended next-problem order is **B -> C -> A** (highest-value first):
1b. (NEXT PROBLEM **B**, highest value -- from the drill) **STAGE-appropriate timescales, not one global lambda.** The
   WM timescale spectrum increases up the cortical hierarchy (Murray 2014, PINNED). Concrete testable gap: the
   situation-model / discourse integrator should carry a SLOWER timescale than the register; if it currently shares the
   register's leak, that is a fidelity gap. Test at the long-range / low-data regime, can-fail, one-variable.
   ANTI-INFLATION CAUTION (from disk): two prior multi-timescale cells HARD_FAILED (`exp_substrate_fast_slow_weights_LM_v1`,
   `exp_c2_cascade_stc_swr_continual_v2`) and `exp_timescale_gated_predictive_hierarchy_tgph_v1` LANDED -- BUILD ON tgph,
   do not re-derive, and expect naive multi-timescale to be fragile.
1c. (NEXT PROBLEM **C**) **`situation_focus.ChunkedFocus` fidelity audit** -- if the Cowan-4 focus is a hard fixed-slot
   count, replace it with a GRADED gain-weighted focus (effective ~4 from competition). Strong cite: Watters 2026
   (PMC12893052, gain-modulated compositional WM code beats slots).
1d. (NEXT PROBLEM **A**, do LAST) **coupled superposition cascade** -- a value-flowing fast->slow cascade is the more
   Benna-Fusi-faithful form, but ~ a reparameterised bank of leaks; P~0.35-0.40 it beats the independent-sums spectrum.
   A can-fail test, not a priority.
1e. (adjacent flag) the salience-gated hand-off (change 2) is a SINGLE-threshold gate; the consolidation literature
   (Benna-Fusi) says transfer is itself multi-timescale FLOW, so a graded flow may be more faithful than a discrete
   gate -- a fidelity refinement to consider when landing change 2.
2. (follow-on, MEDIUM -- build) Wire the salience gate (change 2) to the LIVE prediction-error + `script_grain` MDL
   channels and re-measure on a real reading stream (the policy + controls are validated here; the live-channel
   reliability is the open piece).
3. (follow-on, LOW -- measurement) After landing, wire the leaky register into the live who-did-what / situation-model
   path and re-measure the END-TO-END reading score at high event load (the capability claim is proven on the
   register's recent-recovery readout; the end-to-end lift is the confirming measurement).
4. (follow-on, LOW) compose `leak` with `multibank` sharding (per-bank leak) and sweep -- the two capacity levers are
   orthogonal and should stack.

---

## INTEGRATED_BY_STRATEGY — 2026-08-29 (grade: EXCELLENT; SOLVED owner-DONE — positive capability result)

Integrated by strategy. Reverified FIRST-HAND: `test_register_leaky_write.py` **11/11 PASS**. Argument adversarially audited and sound: the leaky recency write beats the STRONGEST flat floor (flat sum + the landed `decode_serial` readout, not a strawman) CI-separated at overload; graded primate fade-curve (not a queue step); the salience-gated second store beats FIFO; and the self-derived-salience negative control faithfully reproduces an on-disk HARD_FAIL (salience must be an independent channel). Owner-pushed multi-timescale fidelity deepening with two self-caught citation corrections.

**hdlab landing QUEUED (Q111 — full concrete diff in `PROPOSED_HDLAB_DIFF.md`, verdict-independent):** (1) a `leak` param on `AccumulateRegister` (0.0 = flat/byte-identical default; >0 = asymmetric leaky recency write) threaded through `make_situation_register` + the multibank backend; (2) a thin `register_consolidation` helper (salience = max(w_pe·PE, w_cong·CONG), commit to `HDFactStore` iff > θ; PE independent, CONG from `script_grain` MDL; commit-most-salient). Additive/default-off (leak=0.0 is byte-identical). Recorded in the STATUS wire-don't-island debt.

**Audit §2b folded** — including the AUDIT UPGRADE: Watters 2026 (primate frontal WM = gain-weighted SUPERPOSITION beating slots) → the substrate's superposition-register FORM is now PINNED at the population-code READOUT level (a partial retirement of "VSA binding unpinned" — at readout, NOT the bind() algebra). Review + `> ## ✅ SOLVER REVIEW` block in PROBLEM.md; priority cleared.

**Next problem primed:** stage-appropriate multi-timescale registers (the situation-model integrator should run slower than the register — Murray hierarchy; build on the landed `exp_timescale_gated_predictive_hierarchy_tgph_v1`, two prior multi-timescale cells HARD_FAILED so do not re-derive).
