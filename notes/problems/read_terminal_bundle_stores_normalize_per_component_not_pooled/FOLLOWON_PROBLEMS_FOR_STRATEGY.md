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

**Why this one / Test-4 (does the defect cost us?).** YES -- NOW MEASURED (`exp_read_terminal_divnorm_write_path_v1.py`,
witness W9), and it is the biggest, cleanest limitation this whole investigation found. **The register's write path is a
FLAT running sum with a HARD capacity wall** (~0.2-0.25*D events; at D=256, ~50-64). Past the wall, recovery collapses
for ALL events -- including the most RECENT ones (recent-4 recovery falls to 0.14 at N=256, chance=0.01). **And
read-time normalization CANNOT move this wall at all** -- raw==divnorm at EVERY load (argmax is scale-invariant; once
events are summed to saturation the information is destroyed, not merely mis-scaled). This is exactly why the whole
read_terminal sweep came back null: **capacity is set at WRITE, and we were only ever normalizing at READ.**

**The measured fix direction (a capacity lever no read norm can provide).** A WRITE-time leaky/suppressive
accumulation `S_j = (1-a) S_{j-1} + bind(role_j, key_j)` (the Buschman 2011 encoding-suppression analog; each new event
suppresses the existing store, bounding the active set) keeps the most-recent events recoverable at ANY total load:
**leaky recent-4 recovery = 1.000 through N=256**, where the flat sum is at 0.14. Info-free twin (shuffled keys)
collapses to chance. This is graceful degradation (Cowan) vs a hard wall.

**The trade + the FULL brain-faithful solution (this is the design space for strategy).** Leaky is NOT a free win: it
BUYS unbounded recent-context capacity by SACRIFICING old events (uniform/all-event recovery drops -- old events decay
away). So the choice is task-shaped: a READER needs recent context (recency-biased recall -> leaky/recency is right); a
whole-narrative situation model needs ALL events (-> you cannot just decay them). The COMPLETE brain-faithful answer
pairs a bounded/leaky active buffer with CONSOLIDATION of displaced items into a separate store (hippocampal->cortical
transfer; chunking) -- which `hdlab/situation_focus.py::ChunkedFocus` already PROTOTYPES (it chunks the oldest units
into a nested store) but the core `AccumulateRegister` does NOT use. Two partial existing levers are also unwired for
this: the `recency` modulator in `hdlab/bundling.py` (OFF by default -- it IS essentially this leaky write) and the
`multibank` sharding (spreads events across banks -> less per-bank crosstalk = a capacity extension).

**Write-gain FORM fidelity (MEASURED, W10 -- narrows the design space).** The form matters decisively, and it rules
one option OUT: a SYMMETRIC pooled divisive rescale at write (S/(mean|S|) each step) does NOT extend capacity --
uniform recall stays ~= flat (0.192 vs 0.199 @N=192) -- because it preserves the RELATIVE weights, so the crosstalk
collapse still happens; it only bounds magnitude. So the brain's encoding suppression (Buschman) CANNOT be a symmetric
divisive normalization; it must be ASYMMETRIC (new privileged over old = recency), which is the leaky/queue form
(recent recovery 1.0). AND the single-store trade is FUNDAMENTAL: leaky/queue give perfect RECENT but forget OLD
(uniform 0.05); an activity-adaptive leak preserves more TOTAL (uniform 0.207) but weaker recency (0.45). **You cannot
get both recent AND old in one bounded store -- which is precisely why the brain pairs asymmetric WM suppression with
CONSOLIDATION to a second (cortical) store.** So the write-path fix is NOT one op; it is an architecture: asymmetric
recency suppression in the active buffer + a consolidation path for what it displaces.

**MEASURED vs INFERRED.** MEASURED: the flat-write capacity wall; read-norm cannot move it; a write-time leaky gain
gives unbounded recent capacity (W9); the FORM matters and symmetric divisive does not extend capacity (W10). INFERRED
(to prove per strategy's build): the best asymmetric form (fixed vs activity-adaptive leak vs bounded queue), the
consolidation mechanism (reuse ChunkedFocus), and how it composes with multibank sharding + the p2 sparse store.

**Fix direction / first deliverable for strategy.** Decide the register's capacity architecture: (1) turn on/validate
the recency-weighted (leaky) write for reader organs that need recent context; (2) wire a consolidation/chunk path
(reuse ChunkedFocus) for organs that need all events; (3) measure both composed with multibank sharding. The
read-terminal `divnorm` stays as-is (it is the right READ-side op once the write path is fixed).

**Pointers.** `experiments/exp_read_terminal_divnorm_write_path_v1.py` (W9, the measured limitation);
`hdlab/situation_model_accumulate.py::AccumulateRegister.add_event` (the flat write); `hdlab/bundling.py` (the OFF-by-
default `recency` modulator = the leaky write); `hdlab/situation_focus.py::ChunkedFocus` (the consolidation prototype);
`hdlab/situation_model_multibank.py` (sharding = a capacity extension); `notes/research_hippocampal_pfc_divisive_
normalization_memory_register_2026-08-29.md` (d)(2) + Buschman 2011.

---

## 2. `sign_bundles_should_be_graded_at_the_overloading_sites` -- MEDIUM (MEASURED, named sites, cheap, mechanism-backed)

**Problem statement.** The `sign()`-on-a-bundle sites are the bipolar/MAP-VSA analog of per-component renorm: `sign(sum)`
discards the graded vote margin. `norm="divnorm"` does NOT apply (it is FHRR-complex-only) -- the fix is to keep the
GRADED integer sum at the sites where a direction-sensitive read OVERLOADS.

**Why this one / Test-4 (does the defect cost us?).** YES but SMALL -- and this is the CORRECTED, real-caller number
(the synthetic grid OVERSTATED it). On the synthetic random-atom grid (`exp_read_terminal_divnorm_sign_family_v1.py`,
W5) GRADED beats SIGN by +0.173 @m=64. But when I MEASURED it on the REAL overloading callers on their OWN readouts
(`exp_read_terminal_divnorm_sign_real_callers_v1.py`, W8), the effect is **MUCH smaller**: graded >= sign, gap grows
with load, but only **+0.02..0.045 at high overload** (FlatFocus role-recovery +0.038 CI-sep @n=24; encode_sentence
word-membership +0.045 CI-sep @n=12) -- because the real callers have CORRELATED (char-based word HDs) and NESTED
(position->role->filler double-unbind) structure that damps the graded margin, unlike the idealized random-atom
single-level grid. **So this is a real but MODEST win, not the substrate-wide +0.17 the synthetic grid implied.**

**Which real sites (classified + MEASURED by readout+load):**
- `char_positional_encoder.encode_sentence` (sign over many words, single cosine read): **+0.045 CI-sep @12-word
  sentences** -- the ONE landable win, and it sits at realistic sentence lengths. The best candidate.
- `situation_focus.FlatFocus` (sign over N superposed events, NESTED unbind read): +0.038 @n=24 BUT its INTENDED
  operating regime is the Cowan capacity ~4 chunks (ChunkedFocus), where it is a NULL (0.451==0.451 @n=4). So no
  practical benefit at its real load. Keep sign.
- LOW-load / few-role -> `sign()` neutral, leave it: `char_positional_encoder.encode_word` (few chars),
  `event_bundle.encode_event` (4 roles).

**Brain mechanism / fidelity.** `sign()` is a per-component quantiser = the same wrong-op class as per-component FHRR
renorm; per-component magnitude erasure has NO fast biological analogue (OUR-INVENTION, confirmed 5 mechanism classes).
Keeping the graded sum is the brain-faithful direction (graded population codes).

**MEASURED vs INFERRED.** MEASURED: the synthetic bipolar grid (sign loses at overload). INFERRED (first deliverable):
confirm graded beats sign on each REAL overloading caller's OWN validated task + info-free twin.

**Fix direction.** Replace `sign(sum)` with the graded sum read by the SAME cleanup at the SINGLE-read overloading
site that operates at realistic load -- **`char_positional_encoder.encode_sentence`** (drop the sentence-level sign,
keep the word-level; +0.045 CI-sep at 12-word sentences). Do NOT bother with FlatFocus (null at its chunked capacity)
or low-load sites. Cheap (no new store/readout), but a SMALL win -- rank accordingly.

**MEASURED vs INFERRED.** MEASURED: graded>=sign on both real callers (W8), modest, growing with load; synthetic
grid overstates it (W5). The magnitude on the OTHER real sites (grounding_acquisition_loop, role_slot_summarizer) is
INFERRED, not measured.

**Pointers.** `experiments/exp_read_terminal_divnorm_sign_real_callers_v1.py` (the REAL-caller measurement, W8 -- the
authoritative number); `experiments/exp_read_terminal_divnorm_sign_family_v1.py` (synthetic grid, W5, OVERSTATES);
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
| 1 | register write/encode-path capacity | **HIGH (biggest gap found)** | **YES -- MEASURED (W9): flat-write hard capacity wall; read-norm cannot move it; write-time gain gives unbounded recent capacity** | YES (W9) | direction MEASURED (leaky write / consolidation); strategy picks the architecture |
| 2 | sign() -> graded at `encode_sentence` | LOW-MEDIUM | YES but SMALL (+0.045 CI-sep on the REAL caller; synthetic grid's +0.17 OVERSTATED) | YES on 2 real callers (W8) | fix ready but MODEST -- only `encode_sentence` at realistic length; FlatFocus null at its capacity |
| 3 | fit pooled-divnorm to Kaminski/Kyzar data | LOW/research | NO (label only) | absence exhaustively searched | protocol fully specified |
| 4 | goal_achievement 6-attribute dimensioning | LOW | NO (premise unmeasured) | NO | not ready -- measure premise first |
| 5 | assembly-selective vs global divisor | LOW | NO (trend-inferred) | NO | first-deliverable specified |
| 6 | online-learn the typer precision weight | LOW | NO (no accuracy change) | LOO earns-its-keep MEASURED (DRILL 5) | fix specified, low value |
| 7 | theta-gamma <-> pooled-gain (ORGaNICs) seam | LOW/theory | NO (label only) | seam identified | research question |

**One honesty note for strategy (updated after measuring #2 on the real callers):** #2 is ready to land but is a
SMALL win (+0.045 CI-sep at `encode_sentence`, realistic sentence length) -- the synthetic grid's +0.17 did NOT
transfer, because real callers have correlated/nested structure; FlatFocus is a null at its Cowan-chunked capacity.
So #2 is landable-but-low-value, not a substrate-wide win. #1 is the highest LEVERAGE but is a genuine new problem
whose fix must be measured first (best prior of any -- a real primate correlate, Buschman 2011). #4 is the one
component whose limitation I do NOT yet understand well enough to drive a fix -- its first job is to measure its own
premise, not to be filed as a fix. **General lesson this episode taught: measure the fix on the REAL caller, not the
idealized synthetic proxy -- the random-atom single-level grid overstated the win ~4x.**
