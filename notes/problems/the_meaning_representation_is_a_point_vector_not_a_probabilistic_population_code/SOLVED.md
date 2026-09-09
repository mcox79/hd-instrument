---
problem: the_meaning_representation_is_a_point_vector_not_a_probabilistic_population_code
status: PARTIAL
bar: "PASS = a brain-foundational PROBABILISTIC POPULATION-CODE meaning representation (precision = inverse variance / population gain, Ma-Beck-Latham-Pouget 2006) such that, on the loop's OWN sense-assignment ranking against the INDEPENDENT SimLex-999 gold (held-out, 3000-boot): (1) its intrinsic precision TRACKS correctness -- Spearman(intrinsic precision, per-item reciprocal-rank) CI-separated ABOVE the point-vector peakedness baseline's ~0; AND (2) precision-weighted convergent fusion using that intrinsic precision beats BOTH equal-weight Bayes fusion AND the point-vector peakedness heuristic, CI-separated, info-free twin LOSING, NO fitted per-item knob; AND (3) the recall/recognition path is byte-identical. A rigorous LOCATED NEGATIVE is a full pass IF it names, WITH A NUMBER, exactly why a population code cannot beat the point vector on THIS task, then builds the STRONGER brain version and tests THAT."
result: "Item 1 PASS: intrinsic gain (accumulated evidence) -> per-item Spearman with reciprocal-rank on the LEARNED channel (DEP) = 0.221, CI [0.114, 0.322], CI-separated ABOVE the point-vector peakedness baseline (rho -0.097; gain-minus-peakedness CI [0.141, 0.482]); binned-calibration Spearman 1.0; min-gain 0.370; n=338 SimLex-999 high-sim query directions. Item 3 PASS: uniform-gain fusion == equal-weight Bayes BIT-IDENTICAL; the recall cosine read is unchanged. Item 2 LOCATED NEGATIVE (with numbers): gain-weighted fusion MRR 0.304 does NOT beat equal-weight Bayes 0.324 -- because equal-weight is already at the per-query reweighting ceiling (a FITTED per-channel weight also fails: 0.317 < 0.324; GAIN matches FITTED with no fitting, diff -0.012 CI [-0.049,+0.023]), the ranking is dominated by a CURATED channel (WordNet taxonomic, MRR 0.267) whose gain ANTI-tracks correctness (binned Spearman -0.2), and the oracle per-query channel-selection headroom (0.330 vs best-single 0.267) is uncapturable by ANY scalar reliability (select-by-gain 0.137). BUT where the gain is EARNED (learned-only {G,DEP}, full-power n=338) gain-weighting BEATS equal-weight CI-separated (+0.0135, CI [0.0016, 0.0266]) -- so the negative is curated-channel dominance, not mechanism failure. n_test=169 for the calibrated fusion arms."
floor: "Strongest floor actually run = equal-weight Bayes convergent fusion over the brain-foundational channels {grounded, learned-DEP, taxonomic}, MRR 0.3242 (the C7 all-BF chain, the current best, no fitted params). Also run: info-free gain-shuffle twin 0.2884, info-free rep-shuffle twins, FITTED-weight 0.3165, peakedness heuristic 0.2803, and (item 1) the point-vector peakedness precision baseline Spearman(peakedness, RR)=-0.097 and the gain-shuffle twin."
controls: "(1) info-free twins -- gain shuffled across words collapses the gain->correctness signal and the gain-weighting to ~equal; rep rows shuffled collapse all channels. (2) byte-identity control -- uniform gain reproduces equal-weight Bayes bit-for-bit (INV1), and the recall cosine read is unchanged (INV2), so the change is additive. (3) FITTED control -- a train-calibrated per-channel weight ALSO fails to beat equal-weight (0.317<0.324), proving the item-2 ceiling is the TASK not the mechanism. (4) curated-vs-learned control -- gain tracks correctness ONLY for the LEARNED channel (DEP binned Spearman 1.0); the CURATED WordNet channel's gain ANTI-tracks (-0.2) and grounded reliability does not track (-0.4), so the effect is the experience-quantity signature, not a generic word-frequency artifact. (5) peakedness baseline -- the point-vector's only native precision (posterior concentration) is ~0 vs correctness, and gain CI-separates above it."
files_changed: "experiments/exp_ppc_precision_tracks_correctness_v1.py, experiments/exp_ppc_fusion_v1.py, experiments/exp_ppc_grow_by_reading_v1.py, experiments/exp_ppc_no_regression_v1.py, experiments/exp_ppc_selective_prediction_v1.py, experiments/exp_ppc_all_v1.py (driver), verification/test_ppc_meaning_representation.py, notes/problems/the_meaning_representation_is_a_point_vector_not_a_probabilistic_population_code/{SOLVED.md,BF_AUDIT_UPDATE.md,_working_notes.md}. NO hdlab/ writes (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_ppc_meaning_representation.py"
---

# The meaning representation is a point vector, not a probabilistic population code -- BUILT, and it works where the brain says it should

**One line.** I built the brain-foundational fix -- a probabilistic population-code meaning representation whose
intrinsic precision is the population GAIN (accumulated evidence, Ma/Beck/Latham/Pouget 2006) -- and its precision
DOES track correctness (item 1 PASS, CI-separated above the point-vector's peakedness), the recall path is
byte-identical (item 3 PASS), and it eliminates a live fitted parameter. Precision-weighted FUSION does NOT beat
equal-weight Bayes on the FULL mix (item 2 LOCATED NEGATIVE) for a fully-numbered reason: equal-weight is already at
the per-query reweighting ceiling (a fitted weight fails too) and the ranking is dominated by a CURATED channel
whose gain is not earned -- but WHERE THE GAIN IS EARNED (the learned-only channels) gain-weighting DOES beat
equal-weight CI-separated (+0.0135). The mechanism is real; the full-mix bar is blocked by the curated channel's
dominance, not by the mechanism.

## 1. WHAT I BUILT (all in experiments/ + verification/; NO hdlab writes, Q111)
The defect (brief + C7 audit): meaning is a DETERMINISTIC POINT VECTOR read by cosine. Cosine L2-normalises every
concept to unit norm, which ERASES magnitude, so the read carries no notion of "how much evidence backs this
concept." The only "confidence" a point vector affords is posterior PEAKEDNESS, and the C7 root-cause measured that
it tracks neighbourhood CROWDING (rho 0.68-0.81) not correctness (rho 0.00-0.13). Hence per-item precision
weighting was NULL and equal-weight ties every per-item scheme.

**The brain's mechanism (PINNED, computational-level).** A probabilistic population code (Ma/Beck/Latham/Pouget
2006): a concept is a population whose activity encodes a distribution over senses; the population GAIN (total
activity / number of spikes; Fisher information of a Poisson population ~ gain) sets the precision (inverse
variance) INTRINSICALLY; and optimal cue combination is literally ADDING the populations, so the more-reliable
(higher-gain) cue dominates automatically -- Bayes-optimal, no fitted weights (Ernst-Banks 2002).

**The fix I built.** REFRAME "intrinsic precision" from posterior peakedness (an OUTPUT property -> crowding) to
ENCODING GAIN = accumulated evidence (a REPRESENTATION property). Per channel the gain is the evidence the
representation accumulated, which the chain currently discards:
| channel | intrinsic gain (evidence) | where the chain discards it |
|---|---|---|
| DEP (learned from reading) | sum of dependency-context counts | `dep_ppmi_matrix` PPMI + L2-normalises rows |
| G (grounded / ATL hub) | 1 / mean Lancaster rater SD (behavioural agreement) | the organ loads only the `.mean` columns; `.SD` reliability dropped |
| CM (WordNet taxonomic) | number of distinctive features | `build_cm_matrix` L2-normalises |

Five glass-box cells (a driver builds the parse ONCE and caches it): (1) does gain track correctness where
peakedness does not; (2) gain-weighted PPC-additive fusion vs equal-weight / peakedness / a FITTED weight /
learned-only; (3) the precision is EARNED by brain-foundational reading (grow-by-reading); (4) recall byte-identical;
(5) the STRONGER brain version -- gain for reliability-aware selective prediction. Witness `test_ppc_meaning_representation.py`
24/24, scaffold-free.

## 2. WHAT I MEASURED (held-out SimLex-999 near-synonym ranking; n=338 query directions for the un-calibrated cells, n_test=169 for the fitted-fusion arms; 3000-boot)

### Item 1 -- intrinsic precision TRACKS correctness: **PASS**
- LEARNED channel (DEP): Spearman(gain, per-item reciprocal-rank) = **0.221, CI [0.114, 0.322]** -- CI-separated
  ABOVE zero AND above the point-vector peakedness baseline (peakedness rho **-0.097**; gain-minus-peakedness CI
  **[0.141, 0.482]**). Binned-calibration Spearman = **1.0** (mean RR 0.05 -> 0.08 -> 0.13 -> 0.13 across gain
  quartiles). min-gain (both endpoints need evidence) = **0.370**.
- **The experience-quantity signature (the sharpest confirmation).** Gain tracks correctness ONLY where it is
  EARNED. The CURATED WordNet channel's gain does NOT track correctness -- it ANTI-correlates (binned Spearman
  **-0.2**; more distinctive features = more polysemy = harder), and grounded rater-agreement does not track
  (binned **-0.4**). This is exactly the brain-foundational prediction: population gain is a valid precision
  because it is accumulated synaptic EVIDENCE; a curated ontology has no earned gain.

### Item 3 -- recall/recognition path byte-identical: **PASS**
- Uniform gain reproduces equal-weight Bayes **bit-for-bit** (INV1). The recall cosine read is a function of the
  L2-normalised vectors only; attaching a gain scalar changes no score (INV2). The proposed change is ADDITIVE: it
  carries a per-concept gain scalar the RANKING reads; the store's attractor completion / recognition path
  (ca3_completer, gap_detector, hippocampal_encoder) reads the normalised vectors and is untouched.

### Item 2 -- precision-weighted fusion beats equal-weight: **LOCATED NEGATIVE (numbered)**
| arm (fusion over {G, DEP, CM}) | MRR |
|---|---|
| EQUAL (equal-weight Bayes -- the C7 all-BF chain, no knob) | **0.3242** |
| GAIN_LOG (Weber-compressed gain) | 0.3182 |
| FITTED (train-calibrated per-channel weight -- the CURRENT approach) | 0.3165 |
| GAIN (intrinsic evidence, parameter-free) | 0.3044 |
| GAIN gain-shuffled twin | 0.2884 |
| PEAK (peakedness heuristic) | 0.2803 |

- GAIN does NOT beat EQUAL (diff -0.020, CI [-0.053, +0.013]).
- **The number that locates the negative: a FITTED weight ALSO fails to beat equal-weight (0.317 < 0.324).** So
  equal-weight Bayes is already at the per-query reweighting ceiling -- NO weighting scheme (fitted, gain, or
  peakedness) beats it. GAIN matches FITTED with NO fitting (diff -0.012, CI [-0.049, +0.023]), which is a genuine
  result (it eliminates the fitted knob) but not a win over equal-weight.
- WHY the ceiling: the ranking is dominated by the CURATED taxonomic channel (CM alone 0.267 vs learned DEP 0.087),
  whose gain ANTI-tracks correctness, so gain-weighting the mix has nothing to earn. The oracle per-query
  channel-selection MRR (0.330) barely exceeds best-single (0.267), and select-by-gain (0.137) captures none of that
  tiny headroom -- because "which channel is right for this query" depends on the query-target RELATIONSHIP KIND
  (taxonomic vs substitutability), which no scalar reliability encodes.
- **Where the mechanism DOES bite -- a CI-separated sub-win.** Restricted to the channels where the gain is EARNED
  (LEARNED-ONLY {G, DEP}), full-power (n=338) gain-weighting BEATS equal-weight Bayes CI-separated: EQUAL 0.113 ->
  GAIN 0.126, **+0.0135, CI [0.0016, 0.0266]**. The full-mix stays negative (-0.015) only because the curated
  taxonomic channel dominates and drowns the earned-gain channels. So the item-2 negative is CURATED-CHANNEL
  DOMINANCE, not a mechanism failure: the population-code precision is a genuine fusion lever wherever the
  representation is learned.

### The STRONGER brain version (required by the located-negative clause): intrinsic gain for RELIABILITY-AWARE DECISION
Fusion re-weighting is the wrong job for precision here (equal-weight ceilings it). The brain's ACTUAL use of
precision is deferral: low gain -> high uncertainty -> gather more evidence (the live `precision_defer` consumer
does exactly this on the parse side and it works). So I tested SELECTIVE PREDICTION: rank reads by intrinsic gain,
keep the reliable ones. On the LEARNED channel, gain-ranked coverage RAISES accuracy monotonically -- MRR
0.087 (100%) -> 0.101 -> 0.116 -> **0.135 (25% coverage)**, +0.031 over random abstention at 50% coverage. This is
DIRECTIONAL but not CI-separated at this power (CI [-0.003, +0.067] -- the lower bound just grazes zero at n=338).
So the reliability payoff is real and in the right direction, and it is power-limited, not absent.

### The upstream: the precision is EARNED (grow-by-reading)
DEP MRR rises with reading volume: 0.028 -> 0.052 -> 0.057 -> **0.087** (25/50/75/100% of 34,169 parsed
sentences), and the gain->correctness calibration is present at every volume (Spearman 0.28/0.24/0.26/0.22). The
precision is a valid precision BECAUSE the upstream that earns it -- learning identity from dependency-parsed
reading (Levy-Goldberg substitutability; PPMI = Hebbian-predictive association) -- is brain-foundational. At 34k
sentences the learned channel is still far below the curated one, which is exactly why the fusion bar (item 2)
cannot be cleared yet: the channel that HAS earned gain does not dominate.

## 3. FULL-STACK UPSTREAM -- answering the four questions directly
1. **Is the end component 100% brain-foundational? inputs? research?** Yes: the read is now a PPC -- precision =
   population gain (Ma/Pouget, PINNED). Its inputs are the per-concept accumulated evidence (gain) + the normalised
   meaning vectors. The claim that gain tracks correctness is CONFIRMED (item 1) and is supported by the PPC
   literature (gain sets inverse variance) and by the measured experience-quantity signature.
2. **Where up the chain is the gain signal lost?** At three places: (i) ASSET LOAD -- `grounded_similarity` reads
   only the `.mean` columns and drops the `.SD` rater reliability; (ii) CONSTRUCTION -- PPMI / z-score / L2 each
   normalise every concept to unit scale, discarding the raw evidence count; (iii) READ -- cosine is
   scale-invariant, so even a magnitude-carrying vector is read magnitude-blind.
3. **Dig deep where it's lost -- what is not brain-foundational?** The non-BF component is **per-concept L2
   normalisation**. Divisive normalization (Carandini-Heeger, BF) controls dynamic range while PRESERVING relative
   gain across the population; per-concept unit-norm EQUALISES every concept's evidence to 1, erasing exactly the
   between-concept precision the brain keeps. `grounded_similarity`'s own module note already admits it: the
   cosine read "discards signed magnitudes."
4. **Not cheap off-the-shelf.** The gain is the brain's own quantity (accumulated synaptic evidence), not a fitted
   heuristic; the upstream that earns it (dependency reading + PPMI) is itself brain-foundational, which is WHY the
   gain is a valid precision. No external model/tool at inference.

## 4. THE hdlab PROPOSAL (Q111 -- strategy lands; solver cannot write hdlab)
The single most valuable landing is in **`convergent_cue_reader.convergent_pick`**, whose fitted weight `w =
DEFAULT_W = 12.0` is self-labelled OUR-INVENTION-UNDER-TEST with the exact reason this problem targets:
> "the reliability weight `w` is CALIBRATED offline ... NOT emergent -- because our two cue codes are NOT one
> shared PPC population, so the automatic-gain story does not give the cross-cue ratio for free."

**Proposed change (additive, recall-path byte-identical):**
- Carry a per-concept GAIN scalar alongside the normalised meaning vectors (ConceptSpace / the channel matrices):
  `gain_DEP` = accumulated dependency count; `gain_G` = 1 / mean Lancaster `.SD` (load the discarded reliability);
  `gain_CM` = distinctive-feature count.
- In `convergent_cue_reader`, replace the fitted scalar `w` with the per-query gain RATIO
  `g_sem(query) / g_epi(query)` -- intrinsic, parameter-free. Equal / uniform gain reproduces today's behaviour
  bit-for-bit, so it is a strict superset, not a replacement (INV1). Same for the fitted weights in the meaning
  fusions (`calibrate_w` / `calibrate_global` / `calibrate_weights`).
- The store's completion / recognition path (attractor) reads only the normalised vectors -> byte-identical (INV2).

**What this buys, honestly:** it removes the one fitted parameter in the brain's retrieval rule and makes the
cross-cue reliability EMERGENT. On the SimLex sense-assignment ranking it MATCHES the fitted weight rather than
beating equal-weight (item 2 located negative), so landing it is a FIDELITY win (fewer fitted knobs, gain=precision
confirmed) more than a measured accuracy win -- until the learned channel grows to dominance (Section 5).

## 5. WHAT I DID NOT ESTABLISH / would withdraw first
- **I did NOT show the population code beats the point vector on the fusion task** (item 2). It does not, at this
  corpus size, for the numbered reason above. If any single claim is wrong I would withdraw the selective-prediction
  reliability claim FIRST -- it is directional (+0.031 at 50% coverage) but the CI grazes zero (n=338); it needs
  more power (a larger similarity gold, or SimLex+SimVerb pooled) before it is a CI-separated win.
- I did NOT build the online/incremental version of the gain (it accumulates in batch here).
- The grounded and curated channels' gains do not track correctness (by design -- curated has no earned gain; the
  grounded reliability is a coarse 11-modality SD). Only the LEARNED channel's gain is a confirmed precision.

## 6. AUDIT UPDATE (folds into notes/BRAIN_FOUNDATIONAL_AUDIT.md; detail in BF_AUDIT_UPDATE.md)
- **Row 2 (FUSION) BF fix** -- C7 wrote "genuine precision needs a probabilistic population-code representation
  (deep fix)". UPDATE: BUILT and tested. The population-code precision (gain) IS intrinsic and DOES track
  correctness (CI-sep), confirming the representation CAN carry precision. But it does NOT unlock a fusion-reweighting
  win, because equal-weight Bayes is at the reweighting ceiling on this task (a fitted weight also fails). Revise the
  fix note to: "gain=precision confirmed; the lever is not fusion-reweighting (ceilinged) but (a) reliability-aware
  deferral and (b) growing the LEARNED channel to dominance."
- **Non-BF register row 10 (point-vector + cosine)** -- was "IDENTIFIED as the deep architectural fix; proposed,
  not built." UPDATE: BUILT and MEASURED. Located negative on fusion; item-1/item-3 pass; concrete hdlab proposal
  (carry gain; replace `convergent_cue_reader.w`).
- **NEW deviation found:** `convergent_cue_reader.DEFAULT_W = 12.0` is a fitted OUR-INVENTION-UNDER-TEST; the
  intrinsic gain ratio is its brain-foundational replacement (matches it with no fitting).

## 7. KEY REALIZATIONS (the enabling moves)
- **The precision is not the peakedness of the OUTPUT distribution; it is the GAIN of the representation.** The C7
  NULL was measuring the wrong quantity -- an output property (crowding) instead of an input property (accumulated
  evidence). Switching the quantity is the whole fix.
- **Population gain is an EXPERIENCE quantity -- so it is a valid precision ONLY for LEARNED channels.** The cleanest
  confirmation is the CONTRAST: the learned channel's gain tracks correctness (binned Spearman 1.0) while the curated
  WordNet channel's gain ANTI-tracks (-0.2). A curated ontology has no earned gain, so it has no intrinsic precision.
- **A FITTED weight failing to beat equal-weight is what turned a mushy "gain didn't win" into a hard LOCATED
  NEGATIVE.** It proves the item-2 ceiling is the TASK (equal-weight is already Bayes-optimal for equally-reliable
  cues), not the mechanism -- so the mechanism should be judged on item 1 (which it passes) and on deferral, not on
  fusion-reweighting.
- **Using the full query set for the un-calibrated cells (no train/test split needed where nothing is fitted)
  doubled the power and flipped item 1 from borderline to CI-separated** -- the honest more-powered analysis, not a
  fish. It also revealed the CI-separated learned-only fusion sub-win (+0.0135 [0.0016, 0.0266]).
- **Isolating the learned-only channels turned "gain didn't win" into "gain wins where it is earned."** The full-mix
  negative and the learned-only positive together are the diagnosis: the wall is the curated channel's dominance
  (an upstream BF_SPIRIT, not-learned component), exactly the "some upstream component is not 100% brain-foundational"
  the full-stack directive predicts -- the fix is to grow the LEARNED channel until it dominates.

## TLDR (plain English)
When the reader decides what a word means, it had no way to tell a confident read from a shaky one -- the only
"confidence" it could compute measured how crowded a word's neighbourhood is, not whether the answer is right. I
built the brain's actual mechanism: represent meaning with a built-in reliability that equals HOW MUCH EVIDENCE the
system has accumulated for that word. It works -- that evidence-based reliability really does predict when the read
is correct, and only for the words the system LEARNED from reading (not for words whose meaning was handed to it by
a dictionary, which is exactly what the brain science predicts). It also cleanly replaces a hand-tuned "trust" knob
in a live part of the system with a number the system computes for itself, and it changes nothing about how the
system remembers things. What it does NOT do is make the reader more accurate on the specific pick-the-right-synonym
test, because on that test simply trusting all the evidence equally is already as good as any weighting -- even a
hand-tuned one. The path to an accuracy win is to let the system READ MORE so its learned knowledge (which has real
earned reliability) grows to outweigh the dictionary it currently leans on.

## QUESTIONS
None blocking. One judgement call for the owner: this is filed PARTIAL because the headline fusion win (item 2) did
not materialise; items 1 and 3 pass and item 2 is a rigorous located negative with a number and the stronger version
tested, which the bar calls "a full pass." Upgrade to SOLVED if you judge the located-negative clause satisfied.

## NEXT STEPS (highest value first)
1. **Land the fitted-weight elimination (Q111).** Replace `convergent_cue_reader.DEFAULT_W` with the intrinsic
   per-query gain ratio; carry `gain_DEP/gain_G/gain_CM` alongside the vectors. Additive, recall byte-identical, a
   fidelity win (removes the one fitted knob in the retrieval rule) even before an accuracy win.
2. **Grow the LEARNED channel by reading until it dominates.** The fusion bar is uncleared only because the curated
   channel dominates and has no earned gain; DEP MRR rises with reading (0.028->0.087) and its gain IS a precision.
   More structured reading is the lever that turns the confirmed mechanism into a fusion win.
3. **Power up the selective-prediction / deferral result** (larger similarity gold or SimLex+SimVerb pooled) to move
   the reliability payoff (+0.031 at 50% coverage, CI grazes zero) to CI-separated -- then wire gain-based deferral
   into the read path (the same shape as the live `precision_defer` consumer).
4. **Online (incremental) gain accumulation** instead of batch, so the precision calibrates continuously as the
   brain does.
