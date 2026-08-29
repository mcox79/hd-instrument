# Follow-on problem intel for strategy -- from the solver on `read_terminal_bundle_stores_normalize_per_component_not_pooled`

**Purpose (owner-requested 2026-08-29):** submit strategy ALL the adjacent-component intel gathered while solving this
problem, in a form strategy can file as the next problems. This is a MAP for problem-filing, not a build (solver scope:
I do not write `hdlab/`, `preregs/**`, or other problem folders). Each candidate carries: the on-disk evidence, the
brain mechanism (PINNED vs OUR-INVENTION), MEASURED-vs-INFERRED, the fix direction, the **Test-4 answer** (does a number
show the DEFECT costs us, per `notes/problems/README.md` -- the test that separates a real problem from a hypothesis),
priority rationale, and pointers to the cells/witness that prove each claim. Everything here is reproducible via
`.venv/Scripts/python.exe verification/test_read_terminal_divnorm.py` (14/14) + the five `experiments/exp_read_terminal_divnorm_*.py` cells + the two research notes.

**Reading order by leverage (my recommendation; re-rank per owner):** 1 (encode-path, has a measured brain correlate)
> 2 (sign-family, measured + named sites, cheap) > 3 (register-fidelity reanalysis) > 4/5/6/7 (lower / theory / needs-premise-measured).

**Provenance for every brain claim below:** `notes/research_divisive_norm_decision_stage_reliability_2026-08-29.md`
(decision-stage divnorm PINNED; magnitude-as-reliability) and
`notes/research_hippocampal_pfc_divisive_normalization_memory_register_2026-08-29.md` (memory-register readout still
OUR-EXTENSION; per-component = OUR-INVENTION across 5 mechanism classes; the encode-path + assembly-selective flags).

---

## 1. `register_write_path_may_need_its_own_gain_control` -- HIGH (the only candidate with a MEASURED brain correlate)

**Problem statement.** This whole `read_terminal_bundle_*` family tested normalization only at the READ side of the
register (`bundling.bundle` consumers). Nobody has asked whether the register's WRITE/ENCODE step
(`hdlab/situation_model_accumulate.py::AccumulateRegister.add_event`, and the multibank equivalent) needs its own gain
control -- separate from, and possibly different in form from, the already-landed read-terminal `divnorm`.

**Why this one / Test-4 (does the defect cost us?).** INDIRECT-YES, and it is the strongest of any candidate here:
**Buschman, Siegel, Roy & Miller 2011 (PNAS 108:11252) MEASURED** multi-item target-information suppression in primate
LIP/LPFC/FEF that is **strongest at ENCODING, not maintenance/readout.** That is a measured primate correlate for a
computation we have never tested on our write path. Unlike the read-terminal sweep (which came back "no change needed"
for every un-switched caller), this one starts from a positive measured brain result -- so its first deliverable can be
a genuine premise test with a real prior, not a fishing expedition.

**Brain mechanism / fidelity.** Divisive normalization at a DECISION/sensory population = PINNED. At a memory-register
= OUR-EXTENSION (see #3). Encoding-stage suppression = MEASURED (Buschman 2011), but the original authors did not label
it "divisive normalization" (later theory did), so the FORM of the write-path gain is INFERRED, not pinned.

**MEASURED vs INFERRED.** MEASURED: the read-path is norm-null/harmful for every un-switched caller (this problem);
encoding-stage suppression exists in primate cortex (Buschman 2011). INFERRED (to prove): whether our
`AccumulateRegister` write path benefits from a gain control, and in what form (per-event decay? pooled gain at
accumulate time? a write-time divisive step?).

**Fix direction / first deliverable.** Add a write-time gain option to a COPY of the accumulate path in `experiments/`
(do not touch `hdlab/`); measure serial + argmax readout accuracy vs the current write path at overload, with an
info-free twin and the register's own can-fail floor. If a write-time gain beats the read-only `divnorm` at overload
CI-separated -> a real new capability; if null -> a clean closure with the Buschman prior explained.

**Pointers.** `hdlab/situation_model_accumulate.py::AccumulateRegister.add_event`;
`notes/research_hippocampal_pfc_divisive_normalization_memory_register_2026-08-29.md` (d)(2) + Buschman 2011 citation;
the register witness `verification/test_register_divisive_norm_organ.py` (the read-side baseline to beat).

---

## 2. `sign_bundles_should_be_graded_at_the_overloading_sites` -- MEDIUM (MEASURED, named sites, cheap, mechanism-backed)

**Problem statement.** The `sign()`-on-a-bundle sites are the bipolar/MAP-VSA analog of per-component renorm: `sign(sum)`
discards the graded vote margin. `norm="divnorm"` does NOT apply (it is FHRR-complex-only) -- the fix is to keep the
GRADED integer sum at the sites where a direction-sensitive read OVERLOADS.

**Why this one / Test-4 (does the defect cost us?).** YES -- MEASURED. On the bipolar readout+load grid
(`exp_read_terminal_divnorm_sign_family_v1.py`, witness W5): at low load SIGN==GRADED==1.000 (no gap); at overload
GRADED beats SIGN with a GROWING margin (+0.038 @m=32, +0.123 @m=48, **+0.173 @m=64**). POOLED==GRADED (a global scalar
is argmax-invariant), so **the lever is DROPPING `sign()`, not adding a pooled gain.** The audit's pre-existing
"GRADED beats SIGN, growing margin" flag is now mechanism-backed by the unified readout+load rule.

**Which real sites (classified by readout+load, from reading the code):**
- OVERLOAD -> drop sign for graded: `char_positional_encoder.encode_sentence` (sign_bundle over many words),
  `situation_focus` (bounded-capacity superposition AT capacity), `event_bundle` (many-role events).
- LOW-load -> `sign()` neutral, leave it: `char_positional_encoder.encode_word` (few chars), few-role events.

**Brain mechanism / fidelity.** `sign()` is a per-component quantiser = the same wrong-op class as per-component FHRR
renorm; per-component magnitude erasure has NO fast biological analogue (OUR-INVENTION, confirmed 5 mechanism classes).
Keeping the graded sum is the brain-faithful direction (graded population codes).

**MEASURED vs INFERRED.** MEASURED: the synthetic bipolar grid (sign loses at overload). INFERRED (first deliverable):
confirm graded beats sign on each REAL overloading caller's OWN validated task + info-free twin.

**Fix direction.** At each overloading site, replace `sign(sum)` (or `bsc_bundle`) with the graded sum read by
dot/cosine cleanup; re-validate on that caller's task. Cheap (no new store, no new readout).

**Pointers.** `experiments/exp_read_terminal_divnorm_sign_family_v1.py`; witness W5;
`hdlab/char_positional_encoder.py` (`_sign_bundle`, `encode_word/encode_sentence`), `hdlab/situation_focus.py`,
`hdlab/event_bundle.py`, `hdlab/grounding_acquisition_loop.py` (`_bundle`), `hdlab/role_slot_summarizer.py`. This is the
adjacency map's follow-on #2, now with the mechanism + the per-caller load discriminator.

---

## 3. `fit_the_pooled_divisive_norm_equation_to_human_intracranial_wm_data` -- LOW / research-scope (fidelity LABEL only)

**Problem statement.** Upgrade (or refute) the register/multibank `divnorm` brain-fidelity label from
OUR-EXTENSION-UNDER-TEST to PINNED by fitting the pooled Carandini-Heeger form to real hippocampal/PFC multi-item WM data.

**Why this one / Test-4.** NO substrate cost -- this informs the LABEL, not behavior. Per the README's own ranking logic
that is LOW priority unless the label becomes load-bearing for a bigger design decision. Included for completeness and
because it is genuinely cheap (public data + analysis, no wet-lab, no hd-instrument compute).

**Brain mechanism / fidelity.** Pooled divisive normalization at a memory-register readout is currently
OUR-EXTENSION-UNDER-TEST -- an exhaustively-searched absence (4 lanes, ~28 sources): no paper fits the equation to real
hippocampal/PFC multi-item WM data. WM-capacity THEORY converges on it (Schneegans/Bays 2024; Wei/Wang/Compte 2012) =
right computational CLASS. Closest measured misses (ruled out): Bhatia 2019 CA1 "subthreshold divisive normalization"
(single-cell feedforward, wrong locus); Hahn 2021 divisive-norm fit (crow NCL, wrong species/region).

**Fix direction (fully specified in the research note).** Pull the public NWB dataset (Kamiński 2017 / Kyzar 2024, DANDI
#469; hippocampus + medial-frontal, load 1-3, 902 Sternberg neurons); fit `R = drive^p/(sigma^p + Sum_j drive_j^p)` with
a single shared sigma vs (i) additive, (ii) hard-capacity-step, (iii) flat null; test the iso-suppression signature
(suppression predicted by SUMMED other-item drive, identity-independent). HARD-PASS: pooled form beats alternatives
>=10% AIC/BIC + iso-suppression holds in >50% of load-sensitive neurons. HARD-FAIL: pooled form indistinguishable, or
suppression is identity-specific -> refuted at that locus.

**Pointers.** `notes/research_hippocampal_pfc_divisive_normalization_memory_register_2026-08-29.md` (a)/(c) +
falsifiable-predictions section (the full protocol).

---

## 4. `goal_achievement_attribute_vocabulary_may_be_under_dimensioned` -- LOW, and PREMISE-UNMEASURED (honest gap)

**Problem statement.** `hdlab/goal_achievement.py::ATTRIBUTES` is a hand-authored set of exactly 6 attributes. Its utility
bundle therefore can hold at most 6 items -> it structurally cannot overload -> `divnorm` is provably neutral for it
(this problem, witness W4). But 6 hand-authored attributes may be UNDER-dimensioned for real desires.

**Why this one / Test-4.** NO -- there is NO number showing the 6-attribute set costs us anything. This is the ONE
adjacent component I do NOT understand well enough to drive a fix: I have not measured whether 6 attributes bottlenecks
the utility channel, nor what the brain-faithful target dimensioning is. **Its first deliverable MUST be to measure its
own premise** (does the utility channel miss real desires because the attribute set is too small?) -- exactly the
`flat_store`/`lookup_does_not_lemmatise` failure mode the README warns about. File it only if that premise measures out.

**Brain mechanism / fidelity.** The 6-attribute set is an OUR-INVENTION dimensioning choice; the brain-faithful target
(how many, and learned-vs-fixed) is UNKNOWN to me -- would need its own research drill (utility/value attribute
dimensionality in OFC/vmPFC).

**Fix direction.** UNSPECIFIED until the premise is measured. Do not build a fix yet.

**Pointers.** `hdlab/goal_achievement.py::ATTRIBUTES` (n=6), witness W4.

---

## 5. `sparse_store_should_use_an_assembly_selective_divisor_not_a_global_one` -- LOW (direction known, benefit UNMEASURED)

**Problem statement.** The landed register/multibank `divnorm` uses ONE global scalar over the whole store. The 2025
CA3-modeling literature (Kim & Kim 2025, PLOS Comput Biol) argues the field is moving AWAY from global/pooled inhibition
toward ASSEMBLY-SELECTIVE inhibition (one divisor per stored assembly/pattern). If a pooled-divisor store is extended
(e.g. the multibank sparse store), an assembly-selective divisor (one scalar per bank/pattern) may be higher-fidelity
than one global scalar.

**Why this one / Test-4.** NO measured cost yet -- INFERRED from a modeling-trend paper. Lower priority; a refinement of
an already-working mechanism, not a fix to a measured defect.

**Brain mechanism / fidelity.** Global pooled inhibition (Treves-Rolls) vs assembly-selective (Kim & Kim 2025) is an
active split in the CA3 literature; our current global scalar sits on the older side.

**Fix direction / first deliverable.** In `experiments/`, compare a per-bank (assembly-selective) divisor vs the global
divisor on the multibank register at overload; info-free twin; the register's serial-readout floor.

**Pointers.** `hdlab/situation_model_multibank.py`; Kim & Kim 2025 (in the hippocampal research note (d)(1)).

---

## 6. `learn_the_typer_precision_weight_online_instead_of_batch_loo` -- LOW (fidelity only, NO accuracy change)

**Problem statement.** The typer's `shard_weights_` is a good, brain-defensible LEARNED precision weight (it EARNS its
keep -- DRILL 5 showed magnitude-as-reliability loses to it by -0.19 CI-sep because the typer's magnitude encodes binding
strength, not class-discriminativeness). Its only non-brain-faithful aspect is being BATCH-fit (offline LOO) rather than
ONLINE-learned (incremental synaptic reweighting, PMC9393257).

**Why this one / Test-4.** NO accuracy cost -- online learning would compute the SAME weight values incrementally. Pure
fidelity/streaming refinement. Filed only if online/streaming operation becomes a requirement.

**Fix direction.** Replace the batch LOO fit with an incremental precision-weight update; verify it converges to the
same `shard_weights_` and preserves 0.8333.

**Pointers.** `hdlab/selection_weighted_sharded_typer.py` (`_shard_loo_accuracy`, `shard_weights_from_loo_acc`);
DRILL 5 (`experiments/exp_read_terminal_divnorm_typer_v1.py::weight_mode_drill`, witness W7);
`notes/research_divisive_norm_decision_stage_reliability_2026-08-29.md` (d).

---

## 7. `connect_theta_gamma_serial_readout_to_a_pooled_gain_ORGaNICs` -- LOW / theory-scope (fidelity seam)

**Problem statement.** Our `decode_serial_pooled` couples a theta-gamma serial decode (Lisman-Idiart) with a
least-squares pooled gain. In the brain these are TWO literatures that don't talk: Lisman-Idiart theta-gamma has NO gain
term; Heeger-Mackey 2019 ORGaNICs has a literal pooled-divisor equation that ALSO emits gamma oscillations emergently --
never cited together. Our organ is effectively a NOVEL (theoretically-motivated, not circuit-cited) bridge of the two.

**Why this one / Test-4.** NO substrate cost -- it is a fidelity-label/theory question about a mechanism that already
works. Included so the seam is on record.

**Fix direction.** Research/theory: does an ORGaNICs-style recurrent pooled-gain circuit reproduce our serial-decode
gain-matching AND the theta-gamma phase code jointly? Would inform whether `decode_serial_pooled` can be relabeled from
OUR-INVENTION-bridge toward PINNED.

**Pointers.** `hdlab/situation_model_accumulate.py::decode_serial_pooled_slots`; hippocampal research note Q3 (Heeger &
Mackey 2019, ORGaNICs, PNAS 116:22783).

---

## Summary table (for the problems tab / ranking)

| # | slug | leverage | Test-4 (defect costs us?) | measured? | fix ready? |
|---|---|---|---|---|---|
| 1 | register write/encode-path gain control | HIGH | INDIRECT-YES (Buschman 2011 primate correlate) | read-side null MEASURED; write-side to prove | scope ready, fix TBD by the problem |
| 2 | sign() -> graded at overloading sites | MEDIUM | YES (+0.17 @overload, measured) | YES (synthetic grid + site classification) | **fix ready** (drop sign, keep graded, named sites) |
| 3 | fit pooled-divnorm to Kaminski/Kyzar data | LOW/research | NO (label only) | absence exhaustively searched | protocol fully specified |
| 4 | goal_achievement 6-attribute dimensioning | LOW | NO (premise unmeasured) | NO | not ready -- measure premise first |
| 5 | assembly-selective vs global divisor | LOW | NO (trend-inferred) | NO | first-deliverable specified |
| 6 | online-learn the typer precision weight | LOW | NO (no accuracy change) | LOO earns-its-keep MEASURED (DRILL 5) | fix specified, low value |
| 7 | theta-gamma <-> pooled-gain (ORGaNICs) seam | LOW/theory | NO (label only) | seam identified | research question |

**One honesty note for strategy:** only #2 is a fix that is ready to land as-is (measured effect + named sites + known
direction). #1 is the highest LEVERAGE but is a genuine new problem whose fix must be measured first (it has the best
prior of any of them -- a real primate correlate). #4 is the one component whose limitation I do NOT yet understand well
enough to drive a fix -- its first job is to measure its own premise, and it should not be filed as a fix.
