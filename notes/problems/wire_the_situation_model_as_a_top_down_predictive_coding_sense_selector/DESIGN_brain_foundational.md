# Design: the brain-foundational mechanism, where we differ, and how it must generalize

Written by the solver, 2026-09-02, while the smoke run computes. This is the brain-first opening move
(owner standing rule) recorded before the build hardens. Tags: [PINNED] brain-fixed | [OUR-INVENTION] swept.

## The brain mechanism for subordinate-sense override (research-confirmed, from the parent's §D + research notes)
Four steps, each PINNED to a source (Duffy/Rayner reordered access; Lin/Wilks selectional preference;
Desimone-Duncan biased competition; Lambon-Ralph/Jefferies LIFG/pMTG semantic control; Feldman-Friston
precision-weighting; Rabovsky/Kuperberg N400 = semantic prediction error):
1. **All senses activate, ORDERED BY FREQUENCY** — a bottom-up, context-independent stream (dominance prior).
2. **IN PARALLEL, a SEPARATE top-down constraint from SYNTAX + SELECTIONAL structure** (verb–argument,
   head–dependent, and — across sentences — the discourse SITUATION: which entities/events are active).
   Crucially this stream is **FREQUENCY-INDEPENDENT**: syntax/structure is orthogonal to word frequency.
3. **SELECT BY INHIBITION**: a subordinate-biasing structural context makes LIFG **suppress the dominant
   competitor** (signed suppression, biased competition). A dominant-biasing context needs no inhibition
   (pure surplus activation) — the asymmetry the neuroscience confirms.
4. **The when-to-suppress DETECTOR = the PRECISION/reliability of the structural constraint** vs the prior
   (precision-weighted prediction error; the N400 is that error against the current situation model).

## Where WE differ (the precise, measured gaps — parent's located negative)
| brain | us (bottom-up readout) | consequence (measured) |
|---|---|---|
| frequency + structure = SEPARATE streams | we BLEND them (log-prior + λ·log-coherence) | monotone blend swamps subordinate (prior_swamps REFUTED) |
| context = SYNTACTIC/situational, freq-independent | BAG-OF-WORDS coherence | topic-contaminated → detector AUC ~0.51 (context_conditioned HARD_FAIL) |
| SELECT by inhibition | linear PPR can only ADD | can't do subordinate override without a see-saw |
| detector = structural-constraint precision | no frequency-independent detector | all bag detectors ~chance; settling readout see-saws (parent #6) |

## The one untested, brain-faithful lever (this problem)
The parent proved (finding #6/#8) that a better LOCAL/bag detector is a **closed negative** (conflict-gated
settling nets +0.0012, null; a validated predictive-precision detector nets ZERO). It also proved SIGNED
SUPPRESSION reaches 0.767 on subordinate but see-saws — *the selection machinery works; the missing piece is
a FREQUENCY-INDEPENDENT when-to-suppress DETECTOR.* The parent tested bag-of-words and predictive-precision
detectors; it did **not** test a **STRUCTURAL-constraint-precision detector for gating signed suppression.**
That is exactly step 4 above, and it is what this brief asks.

**Reachability-first (highest-yield habit — could it even succeed?):** the headline diagnostic is the
**detector AUC** — does the STRUCTURAL conflict signal separate subordinate ("suppress-me") from dominant
items, and beat the BAG detector's ~0.51? Only if syntax/structure is genuinely frequency-independent HERE
can gated suppression net-win. If struct-AUC ≈ bag-AUC ≈ 0.51, the located negative names the detector: even
structural precision is frequency-biased/too-sparse on this data — a full PASS that redirects strategy.

## How this must GENERALIZE (owner's question) — and how the brain does it
The mechanism is ONE thing at TWO scales, and the fix must generalize across both:
- **Within-sentence** structural constraint (verb–argument selectional structure) — tested first (fast).
- **Across-sentence** DISCOURSE SITUATION (entities persisting via coref, the event/script the discourse has
  established) — the `situation_reader`'s actual output. This is the brief's target and the GENERALIZATION:
  the brain's top-down predictor is a running situation model (Kintsch–van Dijk; Zwaan event-indexing), not a
  per-sentence parse. The disambiguating signal for "he sat on the bank" lives in the *prior discourse*
  (fishing/river established), reached by coref, not in the local sentence.
The plan generalizes deliberately: prove the DETECTOR mechanism at the sentence scale, then lift the SAME
gated-inhibition selection onto the discourse situation (structured focal seed, not the flat discourse bag
proto4b already refuted). A win at either scale is the mechanism; the discourse scale is where the parent's
"flat discourse is redundant" leaves the genuine opening (STRUCTURED ≠ flat).

## If we hit a wall (owner's rule: understand WHY, the brain can do it so we should too)
A miss is a fidelity gap to name and build across, never a ceiling. The candidate walls and the deeper drill each triggers:
- **Detector AUC ~ chance** → the structural signal is still frequency-contaminated OR the extraction is too
  sparse (situation_reader event recall ~0.32). Drill: is it the SIGNAL (structure not freq-independent here)
  or the EXTRACTION (parser/coref recall)? Separate them with an oracle-structure arm.
- **Suppression see-saws even when gated** → the inhibition is un-targeted; the brain's asymmetry (suppress
  only the dominant competitor when structure conflicts) needs the precision term, not a flat γ. Drill precision-weighted γ.
- **Discourse redundant with sentence again** → the situation extraction is losing the entity history; drill
  the coref/event backbone (does an ORACLE coref chain carry it?), which localizes the gap to `situation_reader`.

## Reused organs (no reinvention) + brain status
`_settle` competitive attractor settling [PINNED, validated]; `hdlab/semantic_control` LIFG signed suppression
[PINNED, landed]; `_sense_prior` reordered-access frequency prior [PINNED]; the grounded WordNet++ graph
[OUR-INVENTION substrate]; spaCy dependency parse for the structural stream (LOCAL only, cached);
`situation_reader` (events/entities/coref) + `predictive_reader` (forward N400 surprisal) for the discourse
generalization. AUDIT UPDATE target: BRAIN_FOUNDATIONAL_AUDIT §2b — the sense-selection detector is a
frequency-independent structural-precision signal gating LIFG inhibition, not a bag-of-words coherence.
