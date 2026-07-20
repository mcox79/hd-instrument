# Second-order learning-system layer: build-drill + prior-art scour (3x per element)

Filed by: research (Sonnet). Scope: elements 6-9 of the substrate-vs-brain gap list — the
"comes-alive-after-the-base-loop" layer (neuromodulatory multi-axis gating, hierarchical
multi-timescale predictive processing, consolidation/schema-extraction replay, learned
structure-derivation). Base loop = a contrastive predictive-coding reader with learned
similarity-structured codes over VSA/HDC hypervectors, scoped separately, not built yet.

Method: 4 parallel Sonnet lit-scan sub-agents (one per element), each ran a 3x build-drill
(three build angles, glass-box-or-not verdict per angle) + a live WebSearch/WebFetch prior-art
pass against the named papers/authors, then gave a self-deflated confidence + ADOPT/ADAPT/
BUILD-FRESH call + sequencing verdict + credit list. This note applies the standing lit-scan
calibration penalty on top of their self-deflation (cap novel-synthesis P at 0.50) and
synthesizes across the four.

## HEADLINE

Every one of the four gaps has real, glass-box-adoptable prior art — nothing here needs
BUILD-FRESH. Best single adoptable artifact per element: **(6)** Yu & Dayan 2005 (expected-vs-
unexpected uncertainty) formalized by Mathys et al.'s Hierarchical Gaussian Filter — closed-form,
ready to port; **(7)** Numenta's HTM temporal pooler (SDR-native, non-backprop, already does
fast-to-slow bundling) plus Hasson's temporal-receptive-window scrambling method to *derive* the
timescale ratio instead of guessing it; **(8)** Complementary Learning Systems (McClelland et al.
1995/2016) + prioritized-replay-by-error (Schaul et al. 2015) give the architecture and the
priority signal, while VSA bundle/cluster-centroid gist-extraction substitutes cleanly for the
field's usual (non-glass-box) deep generative replay; **(9)** successor-representation
eigenvectors (Dayan 1993; Stachenfeld et al. 2017, already extended to language by Stoewer et al.
2022) plus Hebbian/Oja PCA-with-non-negativity (Dordek et al. 2016) derive relational geometry
from pure transition statistics, no SGD. **Build order:** elements 6, 7, 8 are strict
second-order — each computes its control/summary signal FROM the base loop's own
prediction-error/coherence stream, so none can be built or tested standalone. Element 9 is the
one exception — it operates on raw transition/co-occurrence statistics of the data itself and can
be prototyped in parallel with, or even ahead of, finishing the base loop, then substituted in as
a drop-in replacement for the hand-stipulated structural code once both are ready.

## Cheap decisive test

Target element 9 first, precisely because it does NOT require the base loop to exist — it is the
only one of the four that produces a standalone, falsifiable, CPU-cheap result right now.

**Test:** build the transition/co-occurrence matrix over whatever discrete units the current
hand-stipulated structural code indexes (positions/roles/slots), symmetrize or TD-learn a
successor-representation matrix M, eigendecompose (or run Oja's-rule PCA with a non-negativity
constraint per Dordek et al. 2016), quantize the top-k eigenvectors into the substrate's
hyperdimensional space via a fixed random projection, and compare the derived role-code's
algebraic properties against the current hand-stipulated code on two axes: (a) pairwise
role-vector separation (mean |cosine|) and (b) downstream retrieval/bind-unbind accuracy on a
synthetic task that already exercises the hand-stipulated code. Pure linear algebra + one
retrieval smoke — no base loop, no training run, ~1 day theory + a few hours CPU.

## Falsifiable predictions

### Element 9 (standalone-testable now)
- **HARD-PASS:** derived code's mean pairwise |cosine| among role vectors is statistically
  indistinguishable from (or better-separated than) the hand-stipulated code's, AND downstream
  bind/unbind retrieval accuracy on the existing synthetic task is within 5% of (or exceeds) the
  hand-stipulated baseline.
- **HARD-FAIL:** derived code's role-vector separation collapses toward the random-codebook
  null (quantization into fixed-D hyperdimensional space destroys the eigenbasis's relational
  structure), OR downstream retrieval accuracy drops >=5% relative to the hand-stipulated
  baseline. This would confirm the real risk flagged by the sub-agent: eigenvector geometry may
  not survive projection into a discrete/bounded hypervector space even though the underlying
  linear algebra is sound.

### Elements 6, 7, 8 (base-loop-gated — sequencing claim is the falsifiable unit right now)
- **HARD-PASS (sequencing claim):** once the base loop lands and emits a real prediction-error /
  coherence stream, each of the three second-order axes (RPE-like value weighting, ACh-like
  encode/retrieve gate, NE-like regime-reset; residual-stacking timescale hierarchy; schema
  gist-extraction) can be computed purely from that stream with NO additional external signal,
  and measurably shifts a downstream metric (retention rate, forgetting rate, or contrastive-loss
  trajectory) in the direction the mechanism predicts, at smoke scale.
- **HARD-FAIL (sequencing claim):** an axis is inert (produces no measurable downstream effect)
  even when correctly wired to a live base-loop signal. Per the standing discipline that
  inert-reading of a load-bearing ingest signal is a presumed IMPLEMENTATION bug, not license to
  prune — a HARD-FAIL here triggers a wiring/impl audit before any claim that the mechanism itself
  is non-load-bearing.
- A secondary, harder falsifier for elements 6-8 as a GROUP: if attempting to compute any of
  them *before* the base loop exists (e.g., feeding them synthetic/stand-in error signals) produces
  no coherent behavior, that is direct confirmation of the strict-prerequisite sequencing claim
  (as opposed to merely assumed).

## Cross-thread synthesis

- **Doya's (2002) four-way neuromodulator-as-meta-parameter mapping** (DA=RPE, 5-HT=discount/
  timescale, NE=exploration-gain, ACh=memory-update-rate) is a direct external validation of the
  standing anchor `project_surprise_decomposes_unexpectedness_times_importance_fourth_signal_
  downstream_reach_2026-07-16` — both independently arrive at "more than one axis, don't sum them,
  treat as separable meta-parameters." Doya's framing plus Yu-Dayan's two-axis (expected/unexpected
  uncertainty) split, formalized by Mathys et al.'s Hierarchical Gaussian Filter, gives a
  literature-grounded quantitative backbone for the `ALL-3-INGEST-SIGNALS-LOAD-BEARING`
  anchor (surprise + schema-fit + recurrence) — the HGF's precision hierarchy is essentially those
  three signals made into one closed-form filter.
- **Element 7's Hasson temporal-receptive-window scrambling method** and **event-segmentation
  theory's error-spike boundary detection** both directly operationalize a data-driven (not
  hand-tuned) way to set the multi-sentence/discourse integration window — this is the concrete
  mechanism underneath the `project_roadmap_to_conversational_substrate_textbook_waypoint_
  discourse_state_of_mind_2026-07-17` anchor's "state-of-mind = same machinery for reading AND
  conversation" claim: the same error-spike-triggered nested-segmentation rule that stacks
  sentence -> discourse levels in reading is the same rule that would stack turn -> conversation
  levels in dialogue.
- **Element 8's CLS/schema literature** (Tse et al. 2007's ~48h vs. weeks-long consolidation gap
  for schema-congruent material) gives a real, non-invented, quantitative acceptance-test target
  for "schema-congruent items should integrate with drastically fewer replay passes" — useful as
  a calibration anchor for whatever replay-count multiplier the substrate ends up using.
- **Element 9's finding that structure-derivation is NOT base-loop-gated** is the most
  strategically actionable result of this scour: it means the `PIVOT — BUILD THE IDEAL KNOWLEDGE
  FOUNDATION` work (deriving structure from data rather than hand-stipulating it) can start now,
  in parallel with base-loop construction, rather than waiting in a dependency queue behind three
  other elements that genuinely must wait.
- **VSA field's own prior consensus** (Plate 1995, Kanerva 2009: role vectors should be fixed
  and random, not learned, to preserve generalization) is the thing element 9 proposes to
  overturn — flagged explicitly as a real design risk to carry forward (a derived/learned
  structural code must be checked for the same overfitting/generalization failure mode the field
  warns learned embeddings are prone to), not dismissed.

## Substrate-product implications

Framed as product capability, not publication (per standing discipline — no papers, product
only):

- **Element 6** (multi-axis gating) is a differentiator for an *auditable* AI-memory product:
  a closed-form, inspectable multi-axis learning-rate controller (you can point at the exact
  running-variance / CUSUM / precision number that caused a given update to be large or small)
  is a direct sell against black-box neural optimizers where "why did the model update strongly
  here" has no answer. This is load-bearing for any "explainable memory system" product claim.
- **Element 7** (hierarchical timescale stacking) is the mechanism that would let the substrate
  track discourse/conversation coherence over long spans without re-reading the whole history —
  directly relevant to the conversational-substrate roadmap; a product-facing framing is "the
  system remembers what a conversation or document was ABOUT at multiple grains, not just the
  last sentence."
- **Element 8** (schema-extraction) is the mechanism that turns many individual reading/
  conversation episodes into a compact, reusable "gist store" — this is the actual substance of
  the `PIVOT — BUILD THE IDEAL KNOWLEDGE FOUNDATION` project: a store that doesn't grow linearly
  with every experience because recurring structure gets compressed, matching the auditable-AI-
  memory-subsystem product framing (memory that generalizes, not just a growing log).
- **Element 9** (learned structure derivation) reduces hand-engineering/hand-tuning burden and,
  if it survives the cheap decisive test above, strengthens an "explainable by construction, not
  by post-hoc probing" product claim: the structural code would be a direct, auditable function
  of observed statistics rather than an arbitrary engineering choice — a strictly stronger
  transparency story than either a hand-picked code or a black-box learned embedding.

## Citations (verified count)

All citations below were verified live via WebSearch/WebFetch during this scour (title/author/
year/venue confirmed against search results); mechanism *summaries* are drawn from
search-result abstracts/snippets rather than independently re-derived full-text equations —
flagged per-element below where a full-text equation pull would be needed before implementation.

- **Element 6 — 8 verified sources:** Yu & Dayan (2005, *Neuron*); Behrens, Woolrich, Walton,
  Rushworth (2007, *Nat. Neurosci.*); Mathys et al. (HGF, 2011/2014, + 2023 generalization,
  arXiv:2305.10937); Aston-Jones & Cohen (2005, *Annu. Rev. Neurosci.*); Doya (2002, *Neural
  Networks*); Schultz, Dayan & Montague (1997, dopamine-as-TD-RPE, cited in credit); Schmidhuber
  lineage (1992/93/97) + Andrychowicz et al. (2016, arXiv:1606.04474) — cited as the *non-glass-box
  contrast case*; Friston active-inference precision-weighting — flagged UNVERIFIED to a single
  pinned paper, needs follow-up citation nail-down if load-bearing.
- **Element 7 — 9 verified sources:** Rao & Ballard (1999, *Nat. Neurosci.*); Friston
  (free-energy/hierarchical predictive coding, general body of work); Lotter, Kreiman & Cox
  (PredNet, 2017 ICLR, arXiv:1605.08104); Hawkins & Blakeslee (2004) + Numenta HTM/temporal-pooler
  technical papers; Yamashita & Tani (MTRNN, 2008, *PLOS Comp. Biol.*); Hasson et al. (2008, *J.
  Neurosci.* 28(10)); Lerner, Honey, Silbert, Hasson (2011, *J. Neurosci.* 31(8)); Zacks & Swallow
  (2007) + Kurby & Zacks (2008, *TiCS*); Reynolds, Zacks & Braver (2007, *Cognitive Science*).
- **Element 8 — 8 verified sources:** McClelland, McNaughton & O'Reilly (1995, *Psych. Review*);
  Kumaran, Hassabis & McClelland (2016, *TiCS*); Shin, Lee, Kim & Kim (2017, NeurIPS,
  arXiv:1705.08690); van de Ven, Siegelmann & Tolias (2020, *Nat. Commun.*); Tse et al. (2007,
  *Science*); Ans & Rousset (1997) + French (1999, *TiCS*); Wilson & McNaughton (1994, *Science*)
  + SWR review lineage; Schaul, Quan, Antonoglou & Silver (2015/2016 ICLR, arXiv:1511.05952).
- **Element 9 — 11 verified sources:** Whittington et al. (TEM, 2020, *Cell*); Stachenfeld,
  Botvinick & Gershman (2017, *Nat. Neurosci.*); Dayan (1993, *Neural Computation*); Dordek,
  Soudry, Meir & Derdikman (2016, *eLife*); Wiskott & Sejnowski (2002, *Neural Computation*);
  Belkin & Niyogi (2003, *Neural Computation*); Whittington, Warren & Behrens (2022, ICLR,
  arXiv:2112.04035); Stoewer et al. (2022, *Sci. Reports*/arXiv:2202.11190); Plate (1995, *IEEE
  TNN*) + Kanerva (2009, *Cognitive Computation*); Frady, Kleyko & Sommer (2023, *IEEE TNNLS*) +
  Kleyko, Rachkovskij, Osipov, Rahimi et al. (2022, *ACM Comp. Surveys* survey); Jones & Mewhort
  (BEAGLE, 2007, *Psych. Review*) + Sahlgren (2005/2006, Random Indexing).
- **Total distinct verified citations across all 4 elements: ~34** (one source, Friston's
  free-energy body of work, appears in both elements 6 and 7 and is counted once per element
  since the framing differs; counted separately above per the per-element convention).

---

## Per-element summary table

| # | Element | Best adoptable artifact | ADOPT/ADAPT/BUILD-FRESH | Sequencing (needs base loop first?) | Deflated P (calibration-capped) |
|---|---|---|---|---|---|
| 6 | Neuromodulatory multi-axis gating | Yu & Dayan (2005) axes formalized by Mathys HGF (closed-form precision hierarchy) | ADOPT/ADAPT | **YES** — strict prerequisite, axes gate the base loop's own error/coherence stream | 0.50 (capped; sub-agent self-reported 0.55, exceeds the 0.50 novel-synthesis cap — port to VSA distributed codes from scalar/Gaussian cognitive-model formalisms is genuinely unverified) |
| 7 | Hierarchical multi-timescale predictive processing | HTM temporal pooler (non-backprop, SDR-native) + Hasson TRW-scrambling method for deriving window size | ADAPT | **YES** — operates on the base level's residual stream, nothing to stack otherwise | 0.50 (capped; sub-agent self-reported 0.55 — several "glass-box" claims for A1-A3 are construction-time reasoning, not independently verified at scale) |
| 8 | Consolidation / schema-extraction replay | CLS theory (McClelland et al.) + prioritized replay (Schaul et al.) + VSA bundle/cluster gist-extraction substituting for deep generative replay | ADOPT/ADAPT | **YES** — second-layer operation over an already-existing episodic store and its error signal | 0.50 (capped; sub-agent self-reported 0.55 — VSA-specific bundling-capacity-degradation risk not de-risked by literature alone) |
| 9 | Learned structure-derivation | Successor-representation eigenvectors (Dayan 1993; Stachenfeld et al. 2017) + Oja's-rule PCA w/ non-negativity (Dordek et al. 2016) | ADAPT | **NO** — operates on raw transition/co-occurrence statistics, can proceed in parallel with or ahead of the base loop | 0.45 (sub-agent's own figure already under the 0.50 cap; no adjustment needed) |

Note on the 0.50 cap application: elements 6, 7, and 8 each self-reported 0.55 after their own
0.20-0.25 deflation pass. Per the standing lit-scan calibration discipline (novel-synthesis P
capped at 0.50, non-negotiable), this note caps all three at 0.50 rather than accepting the
sub-agent figure verbatim — the underlying reasoning for the deflation is sound (real, credited,
glass-box-adoptable mechanisms exist for each), but the specific composite of "port a scalar/
Gaussian cognitive-model formalism onto a high-dimensional VSA/HDC distributed code" has zero
direct precedent in any cited source and must not be reported above the hard cap.
