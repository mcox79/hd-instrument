---
topic: what is the brain's actual gating signal for what transfers from a recency-limited WM buffer into durable episodic/semantic store, and the most brain-faithful glass-box salience-gate design for the register-to-HDFactStore hand-off
requested_by: solver problem `the_register_write_path_has_a_hard_capacity_wall`
date: 2026-08-29
lit_scan: Opus drill, web-verified primary sources (PMID/PMC fetched where marked HIGH)
calibration: lit-scan calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis capped P<=0.50
prior_thread: notes/research_register_write_path_asymmetric_recency_suppression_2026-08-29.md (established: leaky asymmetric write PINNED-WEAK; CLS consolidation is content/schema-organized NOT recency/eviction-order; do NOT gate hand-off by eviction order)
on_disk_prior_work: experiment_index shows an `exp_attention_salience_reliability_gate_*` family already run -- DERIVED gate = HARD_FAIL (inert/harmful); correlated-error FOOLS a shared channel = HARD_FAIL; only the INDEPENDENT-channel salience variant = HARD_PASS. This is a load-bearing on-disk constraint on Q4.
---

# Research: the consolidation salience gate -- what the brain uses to decide what leaves a recency-limited WM buffer for durable store

## HEADLINE

**The brain does NOT use a single consolidation gate. It uses THREE partly-independent salience pathways -- prediction-error/novelty, schema-congruence, and reward/emotional value -- that all converge on ONE downstream commit-switch: dopamine-D1/D5-gated late-LTP via synaptic tagging-and-capture (STC).** The unifying principle is not a single upstream detector but a single downstream *capture* mechanism with a grace-period, fed by a weighted sum of parallel salience signals. For OUR substrate the faithful reduction is a **weighted-OR of two signals we already possess** -- prediction-error (surprise) as the primary axis and MDL schema-congruence as the second -- committing the *extremes* (very surprising OR very congruent) and letting the mushy middle decay unrecovered. This reproduces the brain's empirically U-shaped consolidation-selection curve (SLIMM) with no new mechanism and no external LLM. The rule is unambiguously **commit the most salient, NOT the oldest-evicted** (PINNED, Tse/SLIMM/replay literature all reject arrival-order). One on-disk constraint is decisive: the substrate's OWN prior `salience_reliability_gate` experiments HARD_FAILED when the gate was *derived from the same representation it gates* -- so the PE signal must come from an **independent channel** (the schema/script model's prediction vs the observed item), never re-derived from the register's own accumulated code.

---

## Q1 -- The brain's gating signal for WM/transient -> durable store: enumerate + grade

**Verdict: a WEIGHTED COMBINATION of parallel salience signals converging on a common STC/late-LTP switch, NOT a single gate.** [PINNED, P=0.78]

### (a) Prediction-error / novelty -- the best-measured ENCODING-time determinant [PINNED, P=0.68]

- **Hippocampal-VTA loop (Lisman & Grace 2005, Neuron 46:703, PMID 15924857 -- HIGH).** The hippocampus detects information "not already stored," the novelty signal routes subiculum->accumbens->ventral pallidum->VTA, VTA dopamine returns to hippocampus and converts *early* LTP into *late* LTP. Direct: "The dopamine released in the hippocampus functions as a permissive signal for late LTP." This is the canonical "novelty gates entry into long-term memory" circuit.
- **LC-hippocampus is the STRONGER novelty channel (Takeuchi et al. 2016, Nature 537:357, PMID 27602521 -- HIGH).** Locus coeruleus TH+ neurons project MORE profusely to hippocampus than VTA does; optogenetic LC-TH+ activation mimics the novelty-enhancement of everyday memory; the effect is *unaffected by VTA inactivation* -- LC co-releases dopamine (not just noradrenaline) into hippocampus and that dopamine boosts retention. Kempadoo et al. 2016 (PNAS) corroborates LC-dopamine.
- **Two-systems synthesis (Duszkiewicz, McNamara, Takeuchi & Genzel 2019, Trends Neurosci 42:102, PMID 30455050 -- HIGH).** "Common novelty" -> VTA-HPC -> initial + systems (semantic) consolidation; "distinct novelty" -> LC-HPC -> detailed episodic long-term memory. Both converge on D1/D5. The authors explicitly frame this as **parallel-yet-distinct pathways**, not one gate.
- **Behavioral confirmation that surprise dominates at encoding (Rouhani & Niv 2021, eLife, PMC8041467 -- HIGH; Rouhani, Norman & Niv 2018 biorxiv).** BOTH signed and unsigned reward-prediction-errors enhance memory; the memory boost "scaled with the reward prediction error experienced when memoranda were presented." Crucially, **surprise/PE is the dominant determinant of *immediate* encoding strength**, whereas pure reward value shows its effect later, over consolidation.

### (b) Schema-congruence -- content-organized, U-shaped [PINNED, P=0.78]

- **Tse et al. 2007 (Science 316:76) / 2011 (Science 333:891).** Schema-congruent material consolidates within ~48h regardless of arrival order; schema-*incongruent* material produced *less* consolidation-related gene expression. Consolidation is organized by CONTENT/congruence, NOT recency or buffer-overflow order.
- **SLIMM framework (van Kesteren, Ruiter, Fernandez & Henson 2012, Trends Neurosci 35:211, PMID 22398180 -- HIGH).** mPFC encoding activity rises *linearly with congruence*; MTL activity rises with *incongruence*. The model is explicitly **U-shaped**: strongly congruent items consolidate fast (mPFC schema absorption), AND strongly incongruent items consolidate well too (the incongruence "elicits a prediction error leading to better memory through the creation of new representations"). The MIDDLE (weakly-congruent, unsurprising) is what gets dropped. **This U-shape is the single most design-relevant brain fact in this drill.**

### (c) Reward / emotional salience + the common capture substrate [PINNED, P=0.72]

- **Synaptic tagging-and-capture / behavioral tagging (Redondo & Morris 2011, Nat Rev Neurosci 12:17, "Making memories last" -- HIGH; Frey & Morris 1997; Moncada & Viola 2007; Ballarini 2009).** A *weak* event sets a synapse-specific TAG (lifetime ~1-3h) that CAPTURES plasticity-related proteins synthesized by a nearby *strong/salient* event. Dopamine released during salience/novelty drives PRP synthesis. **This is the mechanistic convergence point: every salience pathway above ultimately gates the same D1/D5-dependent capture switch.** It is why a weak (would-decay) memory persists if it co-occurs with a salient one -- the grace-period is a *temporal* capture window, not a per-item detector.
- **Reward biases offline replay-selection (Ambrose, Pfeiffer & Foster 2016, Neuron 91:1124, PMID 27568518 -- HIGH).** REVERSE (not forward) hippocampal replay is uniquely up-modulated by increasing reward -- reverse replay is the reward-tagging channel for consolidation. Awake sharp-wave-ripples themselves act as a natural experience-tag for later sleep replay (Yang, Sun, Huszar, Hainmueller & Buzsaki 2023/2024, PMC10659301 -- HIGH; NOTE: this paper shows ripples ARE the tag and occur preferentially at reward, but does NOT itself quantify RPE-tracking -- the RPE-modulation claim rests on Ambrose 2016 and the value-replay lineage, not on the Buzsaki tagging paper. Correcting a citation-conflation trap.).
- **Emotional/amygdala tagging (McGaugh 2004/2013, Trends Neurosci 25:456; Redondo et al. 2014).** Basolateral amygdala + noradrenaline set the *specificity* of what is prioritized (not a blanket boost). This is a THIRD salience axis; in our substrate there is no native "reward/arousal" signal at the register layer, so it is correctly OMITTED as not-applicable (see Q4).

### (d) Attention / active-rehearsal at encoding -- the UPSTREAM necessary gate [PINNED, P=0.70]

- **Aly & Turk-Browne 2016 (PNAS 113:420, PMC4712804 -- HIGH; "Attention stabilizes representations in the hippocampus").** Attention alters the hippocampal state, and the degree of that alteration *predicts whether attended information is stored*. Selective attention gates what is encoded at all. This is logically UPSTREAM of (a)-(c): an item must be attended to enter the buffer before any salience signal can tag it for durable capture. For our register this maps to "what enters the accumulate step in the first place," not the hand-off gate per se.

### Which dominates, single vs weighted?

- **At ENCODING time:** prediction-error/novelty (surprise) is the best-measured *single* determinant of immediate memory strength (Rouhani/Niv; the VTA/LC dopamine literature). It is also the most GENERAL -- schema-*incongruence* is itself a prediction error (SLIMM), so a PE axis subsumes half the schema story.
- **Over CONSOLIDATION (offline):** reward/value biases *which* traces get replayed (Ambrose/Foster; awake-ripple tagging), i.e., a value-weighted selection on top of the encoding tag.
- **Mechanistically:** all pathways converge on one STC/D1-D5 capture switch. So the honest answer is **a weighted combination of parallel salience signals feeding a single downstream commit-switch** -- neither "one gate" nor "many independent gates," but "many detectors, one capture." The best single PROXY, if forced to pick one, is **prediction-error/surprise** (most general, best-measured, subsumes incongruence).

---

## Q2 -- Is the decayed old-item code LOST or REFORMATTED-but-retrievable?

**Verdict: BOTH, split by how far the item has decayed. Recent-but-decayed items are activity-silent-but-pingable (reformatted, still in buffer -> need only a better readout). Genuinely displaced/deprioritized items are NOT reliably ping-recoverable (-> DO need a 2nd store). The exact sequential-PFC ping study is still not run, so this remains partly open -- but the closest 2023-2025 evidence supports our two-store split.** [PINNED-MODERATE that within-capacity silent items are retrievable, P=0.68; SUPPORTED-BUT-OPEN that displaced items are genuinely lost, P=0.55]

- **Pinging reveals activity-silent WM is present, not gone (Wolff, Jochim, Akyurek & Stokes 2017, Nat Neurosci 20:864; corrected reanalyses PLoS Biol 2021/2022, PMC8641864/PMC8956321 -- HIGH).** A visual impulse "ping" during the delay reactivates item-specific information that was undecodable in the silent state -- the code is "hidden," not erased. Later work (biorxiv 2023 impulse-perturbation of colours) even found *uncued* items reactivate, casting doubt on active purging.
- **CRITICAL 2025 nuance (Yang, He & Cai 2025, Cerebral Cortex 35(2):bhae494 -- HIGH).** Two distinct ping mechanisms (noise-reduction reactivation vs context-matched reorganization). But the decisive result for us: **PRIORITIZED-but-silent items reactivate under a ping; DEPRIORITIZED unattended memory items (UMIs) "did not exhibit any reactivation after any ping condition,"** even though both were undecodable in the silent state. "Task priority still modulated the WM storage states." So priority/depth-of-decay determines whether a silent item is recoverable at all.
- **Mapping to the register:** a leaky store `S = lambda*S + bind(role,item)` keeps RECENT items at high effective weight -- these are the "prioritized-silent, pingable" class: still in the buffer, recoverable by a better readout (resonator/clean-up), no 2nd store required. Items decayed below the noise floor are the "deprioritized UMI" class: NOT reliably recoverable -- this is exactly the tail that needs the permanent `HDFactStore`. **So the 2nd-store hand-off is genuinely necessary -- but ONLY for the truly-displaced tail, and the salience gate must fire BEFORE that tail decays past recovery** (the STC grace-period analog: capture must happen inside the decay window).
- **Honest open gap (unchanged from prior drill):** no causal ping study has been run on a genuine sequential-recency PFC design, so "genuinely lost" vs "hidden but retrievable" is not fully closed at our exact regime. The priority-modulated WM ping (Yang 2025) is the closest proxy and it supports the two-class split above.

---

## Q3 -- The recency-decay LAW: geometric vs power vs step; fixed vs activity-adaptive

### Form: geometric/exponential is the FAITHFUL per-trace form; power-law is an AGGREGATE artifact [PINNED, P=0.72]

- **Per single trace with a single decay constant, forgetting is EXPONENTIAL/geometric.** The apparent power-law of forgetting (Wixted & Ebbesen 1991; Kahana & Adler, "Note on the power law of forgetting") is a well-established *emergent* property of **superposing many exponential traces with different decay rates** -- "forgetting is exponential, however, superposition of forgetting rates for different stabilities will make forgetting follow the power law." A pure exponential retention function has the special property that forgetting rate is *age-independent*; power-law arises only when you MIX timescales.
- **Implication for us: our `lambda^age` (geometric) is the correct faithful form for a SINGLE store with a single leak.** Power-law would be faithful only if we modeled a *mixture* of stores/timescales -- which is exactly what a two-store architecture (fast leaky register + never-forget HDFactStore) already IS at the system level. So: geometric inside the register, and the register+HDFactStore *pair* naturally produces power-law-like system retention. This is a clean fit, not a compromise. Do NOT impose a power-law inside the single register.

### Leak: fixed vs activity-adaptive -- adaptive (divisive-normalization) is the higher-fidelity form [PINNED on read-side, MODERATE on write-side, P=0.55]

- Divisive normalization predicts effective per-item gain = activity / (sum over all items) -- i.e., **effective suppression IS stronger when the buffer is fuller** (an adaptive, normalization-like gain). The prior sibling drills established this is the PINNED read-side form (Carandini-Heeger; Bays; Hahn et al. 2021 PMC8660017; Watters et al. 2026 gain-model-wins-88%).
- **Second-order caveat (Louie-lineage, "Adaptive Value Normalization in PFC Is Reduced by Memory Load," eNeuro 2017, PMC5409984 -- HIGH):** the background-suppression MECHANISM that *implements* normalization is itself REDUCED under high WM load -- normalization does not stay perfect as the buffer fills. So a purely-adaptive leak is not a free lunch either.
- **Recommendation: sweep BOTH forms.** A FIXED lambda is an admissible copy of the OPERATION (leaky accumulation) and is the honest first cut. An ACTIVITY-ADAPTIVE leak -- lambda that grows with buffer occupancy / total activity, i.e., divide the store by its running L2 norm before each add -- is the higher-fidelity upgrade and is the SAME divisive-normalization family already PINNED on the read side. Per the OWNER discipline (copy the operation, sweep the parameter): lambda's VALUE is a swept parameter, never adopted from any brain number; the CHOICE fixed-vs-adaptive is a fidelity axis worth an explicit arm.

---

## Q4 -- Most brain-faithful GLASS-BOX salience gate for the register->HDFactStore hand-off

### Recommended design [rule PINNED; specific mapping NOVEL SYNTHESIS capped P<=0.50; independent-channel constraint on-disk-VALIDATED P~0.75]

**Signal (weighted-OR of two axes we already have):**
1. **Prediction-error / surprise (PRIMARY).** `PE(item) = distance( schema_model.predict_next(context) , observed_bind(role,item) )` -- the surprise of the actual item under the script/schema model's prediction. This is the general, best-measured brain axis (Rouhani/Niv; VTA/LC novelty) and it subsumes schema-incongruence.
2. **Schema-congruence (SECOND).** `CONG(item) = drop in MDL description length when the item is absorbed under the current schema` -- the Perfors-Tenenbaum two-part-code gate ALREADY BUILT in `script_grain_acquisition_loop` / `grounding_acquisition_loop`. High congruence = fast cortical absorption (mPFC/SLIMM).

**Comparison / rule (reproduces the brain's U-shape):**
`salience(item) = max( w_pe * PE_norm(item) , w_cong * CONG_norm(item) )`
Commit `item` to `HDFactStore` iff `salience(item) > theta`. This is a **weighted-OR that fires on the EXTREMES** -- very surprising (PE high) OR very congruent (CONG high) -- and lets the weakly-congruent/unsurprising MIDDLE decay out of the register unrecovered. That is exactly the SLIMM U-shaped consolidation curve (van Kesteren 2012), reconstructed from two signals already in the stack.

**Threshold as swept parameter:** `theta` is the admission threshold = the STC "capture" threshold analog; SWEEP it, do not adopt a brain number. Practically it sets the durable-store write rate (precision/recall trade on what the substrate later needs to recall).

**Timing constraint (the STC grace-period):** the gate must fire while the item is still ABOVE the register's recovery floor (Q2) -- i.e., evaluate salience at WRITE/soon-after, not after the item has already decayed. Capture inside the decay window, exactly as STC requires.

**Rule confirmation: commit the MOST SALIENT, NOT the oldest-evicted.** [PINNED, P=0.78] Tse 2007/2011, SLIMM, and reward-replay all reject arrival/eviction-order as the organizing variable. Eviction-order gating is the one design the brain literature positively rules out.

### The decisive on-disk constraint (do NOT re-learn this the hard way)

The substrate ALREADY ran a `salience_reliability_gate` family (experiment_index, 2026-07-20):
- **DERIVED gate = HARD_FAIL_INERT_OR_HARMFUL** -- a salience signal *derived from the same representation it gates* is inert or actively harmful.
- **Correlated-error = HARD_FAIL_CORRELATED_ERROR_FOOLS_CHANNEL** -- if the gate shares error structure with what it gates, correlated errors fool it.
- **INDEPENDENT-channel = HARD_PASS** -- only a salience signal on an INDEPENDENT channel worked.
- **Implication (load-bearing):** the PE signal feeding this gate MUST be computed from an independent predictor -- the schema/script model's prediction vs the observed item -- **NOT re-derived from the register's own accumulated code S.** This is why PE-from-schema-model (independent) is the primary axis and a "how-strong-is-my-own-trace" self-derived confidence is explicitly barred. This constraint is not from the literature; it is a measured, HARD_PASS/HARD_FAIL fact about our own substrate, and it dovetails with the brain (VTA/LC PE is computed by a SEPARATE novelty-detector circuit, not by the hippocampal trace itself).

### Is the simplest content/salience proxy sufficient? YES -- rigorous case.

The dominant, best-measured brain determinant reduces to **prediction-error/surprise**; schema-congruence is the orthogonal second axis and we already hold it as an MDL gate. A weighted-OR of these two, fired on the extremes with a swept threshold, reconstructs the brain's empirically U-shaped consolidation-selection curve with **two signals already in the stack, glass-box, no external LLM, no new mechanism.** The reward/emotional-tagging axis (amygdala/STC) is real in the brain but has no native analog at our register layer, so omitting it is a principled simplification, not a fidelity gap to paper over. The one thing that would be an OUR-INVENTION error is a self-derived confidence gate -- already refuted on disk.

---

## PINNED vs OUR-INVENTION ledger (calibrated P, deflation applied)

| claim | grade | P | basis |
|---|---|---|---|
| Consolidation-selection = weighted combination of parallel salience signals converging on ONE STC/D1-D5 late-LTP capture switch, not a single gate | PINNED | 0.78 | Lisman-Grace 2005; Takeuchi 2016; Duszkiewicz 2019; Redondo-Morris 2011 -- multiple convergent primary |
| Prediction-error/novelty is the dominant, best-measured ENCODING-time determinant | PINNED-MOD | 0.68 | Rouhani-Niv 2021; VTA/LC dopamine lineage; reward effect emerges later so timescale-dependent |
| Schema-congruence is content-organized (U-shaped), NOT recency/eviction-order | PINNED | 0.78 | Tse 2007/2011; van Kesteren SLIMM 2012 |
| Commit-the-most-salient, NOT the oldest-evicted (eviction-order is positively ruled out) | PINNED | 0.78 | Tse + SLIMM + reward-replay all reject arrival order |
| Within-capacity unattended items are activity-silent-but-pingable (reformatted, not lost) | PINNED-MOD | 0.68 | Wolff-Stokes 2017; Yang-He-Cai 2025 |
| Genuinely displaced/deprioritized items are NOT ping-recoverable -> need a 2nd store | SUPPORTED-OPEN | 0.55 | Yang-He-Cai 2025 UMI-no-reactivation; no sequential-PFC ping run yet |
| Geometric/exponential is the faithful per-trace decay form; power-law is a mixed-timescale aggregate | PINNED | 0.72 | Wixted-Ebbesen; Kahana-Adler note on power law |
| Activity-adaptive (divisive-norm) leak > fixed lambda in fidelity (write-side) | MODERATE | 0.55 | read-side PINNED (Bays/Hahn/Watters); write-side extrapolated; eNeuro load-reduces-normalization caveat |
| Salience gate must be an INDEPENDENT channel (self-derived gate fails) | ON-DISK VALIDATED | 0.75 | our own HARD_PASS/HARD_FAIL salience_reliability_gate family + VTA/LC separate-circuit brain fact |
| Specific mapping: PE-primary + MDL-congruence-second weighted-OR, threshold swept, to HDFactStore | NOVEL SYNTHESIS | <=0.50 | this drill's inference connecting real citations to real on-disk organs |

---

## Concrete recommended gate design (build target, not built here)

```
# at (or just after) each register write S = lambda*S + bind(role,item):
PE   = 1 - cos( schema_model.predict_next(context_before_item), bind(role,item) )   # INDEPENDENT channel
CONG = mdl_bits_before - mdl_bits_after_absorbing(item)                              # existing script_grain gate
salience = max(w_pe * z(PE), w_cong * z(CONG))     # z = running standardize; weighted-OR fires on extremes
if salience > theta:                                # theta swept; capture window = while item still above recovery floor
    HDFactStore.commit(bind(role,item))             # content-addressed, never forgets
# else: item is allowed to decay out of the register unrecovered  (the brain drops the mushy middle too)
```

- **signal:** independent-channel prediction-error (surprise) primary; MDL schema-congruence second.
- **comparison:** weighted-OR (max), fires on either extreme -> reconstructs SLIMM U-shape.
- **threshold:** `theta` swept (sets durable-store write rate); the analog of the STC capture threshold; never a brain-adopted constant.
- **timing:** evaluate at/near write, inside the decay window (STC grace-period).
- **barred:** any self-derived "how strong is my own trace" confidence gate (HARD_FAIL on disk).

## Cheap decisive test

Extend the existing write-path harness with a hand-off-gate discriminator (reuses the register + HDFactStore already built):
- **Arm A (floor):** FIFO / commit-the-oldest-evicted (eviction-order gate) -- the design the brain rules out.
- **Arm B:** commit-most-salient by INDEPENDENT-channel PE only.
- **Arm C:** commit-most-salient by MDL-congruence only.
- **Arm D:** weighted-OR (PE, CONG) -- fires on extremes (predicted best; the SLIMM U-shape).
- **Arm E (negative control, predicted HARD_FAIL):** self-derived confidence gate (salience = norm of the register's own accumulated trace) -- must reproduce the on-disk INERT/HARMFUL result; if it does NOT fail here, that is itself informative.
- **Metric:** downstream recall quality on the substrate's real task for items that were displaced from the register. HARD-PASS = Arm D CI-separated above Arm A (eviction-order) AND above the best single-signal arm; HARD-FAIL = Arm A (FIFO) statistically ties Arm D (would mean, for our engineering problem, the brain's content-gating distinction is not load-bearing and simple FIFO suffices -- a real, useful negative).

## Cross-thread synthesis

- Directly continues `research_register_write_path_asymmetric_recency_suppression_2026-08-29.md`: that drill established leaky asymmetric WRITE (PINNED-WEAK) + "hand-off must be content/salience-gated, not eviction-order." This drill CLOSES the open piece it flagged -- the salience gate itself -- and finds the brain's gate is a weighted-OR of PE + schema converging on STC, reducible to two signals we already hold.
- Reinforces `one_store_does_two_jobs_and_consolidation_is_a_single_average` SOLVED.md: its empirical finding (selective replay is a lever only once codes are sparse/separable; content-driven, not order-driven) is the substrate-side twin of this drill's brain-side finding (Tse/SLIMM: content-organized, not eviction-order). Two independent threads converging on the same principle.
- Q3's geometric-per-trace + power-law-from-mixture result gives the *system-level* justification for the whole two-store architecture: geometric leak inside the register + never-forget HDFactStore = a mixture of timescales = power-law-like system retention, which is what the brain actually shows. The two-store split is not two coexisting stores; it IS the mixed-exponential mechanism of realistic forgetting.

## TLDR (plain language)

The brain does not have one rule for deciding which fresh memories become permanent. It has three overlapping "this matters" detectors -- one for surprise/novelty, one for how well the thing fits what you already know, and one for reward/emotion -- and they all pull the same downstream lever that makes a memory stick (a chemical "tag then capture" step with a short grace period). For our system we do not need to copy all three. Two signals we already have -- how surprising an item is (measured against an independent predictor, NOT against the item's own fading copy) and how well it fits the current schema -- are enough. Commit an item to the permanent store when EITHER is high (very surprising or very well-fitting), and let the forgettable middle fade. Never keep something just because it is the oldest about to be pushed out -- that is the one rule the brain positively does not use. On whether faded old items are truly gone: recent-faded ones are still in the buffer and just need a better read-out; genuinely pushed-out ones do look lost, so the permanent store is worth having -- but the gate must fire before they fade past recovery. One hard-won lesson from our own past experiments: a "how confident am I in my own memory" gate does not work; the signal must come from a separate channel.

## QUESTIONS

None -- the design is concrete and the one hard constraint (independent-channel signal) is already validated on our own disk.

## NEXT STEPS

1. Build the hand-off gate as specified (weighted-OR of independent-channel PE + existing MDL congruence; swept threshold; commit-most-salient to HDFactStore) -- reuses the register + HDFactStore + script_grain MDL gate already built; no new mechanism.
2. Run the 5-arm discriminator (FIFO floor / PE-only / CONG-only / weighted-OR / self-derived negative control) on the real task; predicted order D > {B,C} > A, with E reproducing the on-disk HARD_FAIL.
3. In the same harness add the fixed-lambda vs activity-adaptive-leak arm (Q3) -- one extra sweep, answers the fixed-vs-adaptive fidelity question cheaply.
4. (research-scope, LOW/cheap) the sequential-PFC ping reanalysis remains the one open primary gap for Q2 -- same public Kaminski/Daume dataset already flagged for the divisive-norm question; one reanalysis could close both.

## Sources (primary, HIGH-confidence fetched or PMID-verified)

- Lisman & Grace 2005, Neuron 46:703, PMID 15924857 (hippocampal-VTA loop; novelty gates LTM entry)
- Takeuchi et al. 2016, Nature 537:357, PMID 27602521 (LC-dopamine consolidation of everyday memory)
- Duszkiewicz, McNamara, Takeuchi & Genzel 2019, Trends Neurosci 42:102, PMID 30455050 (two-systems: common vs distinct novelty)
- Rouhani & Niv 2021, eLife, PMC8041467 (signed+unsigned RPE enhance memory)
- Tse et al. 2007 Science 316:76 / 2011 Science 333:891 (schema consolidation, content-organized)
- van Kesteren, Ruiter, Fernandez & Henson 2012, Trends Neurosci 35:211, PMID 22398180 (SLIMM, U-shaped congruence)
- Redondo & Morris 2011, Nat Rev Neurosci 12:17 (synaptic tagging-and-capture; the common capture switch)
- Ambrose, Pfeiffer & Foster 2016, Neuron 91:1124, PMID 27568518 (reward modulates reverse replay)
- Yang, Sun, Huszar, Hainmueller & Buzsaki 2023/2024, PMC10659301 (awake ripples = experience tag; note: does NOT itself quantify RPE)
- Aly & Turk-Browne 2016, PNAS 113:420, PMC4712804 (attention stabilizes hippocampal encoding)
- Wolff, Jochim, Akyurek & Stokes 2017, Nat Neurosci 20:864; PLoS Biol reanalyses PMC8641864/PMC8956321 (pinging silent WM)
- Yang, He & Cai 2025, Cerebral Cortex 35(2):bhae494 (priority modulates ping-recoverability; UMIs not reactivated)
- Wixted & Ebbesen 1991; Kahana & Adler "Note on the power law of forgetting" (exponential-per-trace, power-law-from-mixture)
- "Adaptive Value Normalization in PFC Is Reduced by Memory Load" 2017, eNeuro, PMC5409984 (load reduces normalization -- adaptive-leak caveat)
- Hahn et al. 2021 (PMC8660017), Watters et al. 2026 (PMC12893052) -- graded/gain beats slots (read-side, prior drill)
