# Drill 5x #1 — component-by-component inventory: brain reading/comprehension stack vs substrate (2026-07-20)

Research drill 1 of 5 on "what is the real wall for our glass-box reader." Biology-first + ML lit-scan (3x parallel
Sonnet sub-agents, generic-term queries per [[feedback-query-privacy-decomposition]]) synthesized against the
existing filesystem-grounded inventory. Build-on, not rediscovery: `notes/ACCOUNTING_substrate_vs_brain_foundation_discrepancies_2026-07-20.md`
(correspondence table), `notes/SURVEY_reader_chaingrade_prior_work_and_genuine_gaps_2026-07-20.md` (cell-level dedup),
`notes/research_brain_patienthood_affectedness_grounding_2026-07-20.md` (required-component list for patienthood),
`notes/research_brain_building_event_plausibility_web_2026-07-20.md` (event-knowledge acquisition route). This note's
job: lay every brain reading-stack component in ONE table (including two components those docs did not itemize —
visual word recognition and lexical access proper) and answer, precisely, whether the walled component is machinery
or content.

## (a) HEADLINE

Across all 10 components of the brain's reading stack, the substrate has built machinery-equivalents (often mature,
CHAIN_GRADE-verified ones) for 8 of them. The one clean, confirmed wall — thematic-role/patient assignment (who is
affected) — is a **CONTENT gap, not a machinery gap**: the binding operation, the role/filler representation, the
working-memory buffer, and even a self-monitoring/confidence layer all exist and are VET'd; what's missing is the
learned event-plausibility content (Dowty proto-patient entailments / McRae-style generalized event knowledge) that
those mechanisms would consume. The brain's own literature is explicit that this content is normally acquired from
BOTH perceptual/causal experience (pSTS/LOTC/causal-impression, present pre-language) and text-distributional
exposure (Elman/McRae SRNs, LLM thematic-fit near-ceiling on standard norms) — so the gap is not "requires
perception" by default, it is "requires denser/more-explicit event content than typical corpora provide" (the
reporting-bias diagnosis already on record). A second, structurally distinct gap — the hierarchical multi-timescale
predictive-coding loop (Hasson TRW) — is genuinely unbuilt machinery, but it is sequence-gated behind a working base
comprehension loop and would be an un-fireable (can't-fail) cell today, so it is not competitive with the content gap
as "the" load-bearing item right now. P_deflated(content, not machinery, is the dominant lever) = 0.48 (capped near
0.50 as novel-synthesis per calibration discipline, though this reading converges independently across three prior
notes plus this drill's fresh lit-scan, which is unusually strong convergence for a capped estimate).

## (b) Cheap decisive test

**Content-vs-architecture head-to-head, same walled metric.** Take the existing patient-selection precision metric
(the one that HARD_FAILed 6x on self-supervised text signals, per the patienthood note). Run two arms at otherwise
identical config:
- **Arm CONTENT:** inject ONE curated content signal with zero architecture change — Dowty proto-patient entailment
  count via VerbNet causative-inchoative class (lexicon-lookup framing, already ranked #1 candidate in the
  patienthood note), fed as an extra feature into the existing reader.
- **Arm ARCHITECTURE:** add a hierarchical multi-timescale integration wrapper (word -> sentence -> discourse nested
  windows, Hasson-style) around the SAME content the reader already has today (no new event-knowledge signal) —
  purely a structural/architectural change.

Both arms measured against the same frozen held-out patient-selection precision probe used in the 6 prior failed
runs (apples-to-apples with the existing negative result).

## (c) Falsifiable predictions

**HARD-PASS (content is the dominant lever):** Arm CONTENT moves held-out patient-precision by a margin that clears
the design-gate bar (corr>0.2 equivalent, or an absolute precision lift that survives a random-feature control), AND
Arm ARCHITECTURE moves it by materially less (or not at all). This would confirm: the wall is a content/curation
problem, matching the event-density-corpus diagnosis already on record, and would justify prioritizing corpus/content
work over any new architecture investment for this specific capability.

**HARD-FAIL (machinery is competitive or dominant, or neither moves it):** Arm ARCHITECTURE moves the metric as much
or more than Arm CONTENT, OR neither arm clears the bar. The first sub-case would overturn this drill's headline and
mean the hierarchical-timescale gap deserves re-prioritization ahead of its current sequence-gated status. The second
sub-case (neither moves it) would deepen the existing grounding-necessity hypothesis — i.e. even curated proto-patient
content and multi-scale architecture together are insufficient, pointing toward perception/embodiment as the last
resort per the event-plausibility note's own ranking (perception should be the last resort, not skipped-to).

## (d) Component-by-component HAVE / NOT-HAVE table

| # | Brain component | Plain-terms function | Where/how (brain) | Substrate equivalent? | Status |
|---|---|---|---|---|---|
| 1 | **Visual word recognition** (orthographic) | Converts a visual letter string into an abstract, position/font-invariant code | VWFA (left occipitotemporal/fusiform); dual-route DRC/triangle models; well-replicated (pure alexia lesion evidence) | **N/A by design** — substrate ingests already-tokenized/symbolic text, bypassing this stage entirely | Not a gap (architectural choice, not a missing capability) |
| 2 | **Lexical access** (word -> meaning) | Retrieves stored word-meaning association given a wordform | Distributed temporal/frontal network; spreading/interactive activation (McClelland-Rumelhart IA, TRACE); N400 ~300-500ms; ATL hub-and-spoke (Patterson/Lambon Ralph) for amodal integration | **HAVE** — learned codebook (RI/PPMI+SVD content codes) functions as the content-store half; retrieval = argmax-cosine cleanup (the machinery half) | **BUILT, CHAIN_GRADE** (atom 29368) |
| 3 | **Morphosyntactic parsing** (who/what/structure) | Structure-building / dependency-resolution independent of which words fill the slots, but continuously biased by learned distributional structural preferences (lit is explicit this is a HYBRID, not clean machinery-only) | Left IFG/BA44 (movement-distance signal, contested specificity), ELAN(contested)/P600(robust); Gibson DLT vs Lewis-Vasishth cue-based retrieval (competing, both partly supported) | **PARTIAL** — the fixed binding algebra (machinery half) is mature and lossless; the learned distributional-bias half is the positional/frequency-heuristic reader capped at ~0.557 | Machinery mature; **learned distributional half immature** (agrammatic-fallback pattern, see #5) |
| 4 | **Semantic integration / combinatorial meaning** | Composes lexical meanings into a structured whole | ATL amodal hub; early combinatorial effects ~200-250ms | **HAVE** — structure/content factorization + FHRR bind compose losslessly | **BUILT, mature** |
| 5 | **Thematic-role & event-structure assignment** (who did what to whom, patienthood) | Binds fillers to abstract roles AND weighs which filler is most-affected (Dowty proto-patient entailments: change-of-state, incremental theme, causal affectedness) | pSTS/LOTC/causal-impression (perceptual, pre-linguistic); ATL (plausibility); angular gyrus/pMTG/TPJ ("thematic hub," binds incrementally); dopaminergic RPE as the improvement-with-experience signal | **NOT HAVE** — 6 self-supervised text signals HARD_FAILed; VerbNet SELRESTRS coverage-blocked (0.20/0.235) | **THE WALLED COMPONENT** — content gap, see (a) |
| 6 | **Situation-model / discourse** (running mental model) | Maintains an indexed model of entities/space/time/causation across a passage; content-free event-segmentation triggered by prediction-error spikes (Zacks EST) is a SEPARATE mechanism from the model's content | Hippocampal binding + PFC-indexed situation model; Event Segmentation Theory = domain-general chunker | **HAVE** (buffer) / **PARTIAL** (content) — two-layer WM buffer settled/mature; but the CONTENT the model would index (event-plausibility web) is the same gap as #5 | Buffer **SETTLED**; content shares gap w/ #5 |
| 7 | **Predictive-coding comprehension loop** | Top-down prediction vs bottom-up input, error drives update; word-level surprisal (well-replicated, near-linear RT relationship) nested inside a MULTI-TIMESCALE hierarchy (word -> sentence -> narrative, Hasson TRW) — genuinely nested, not one flat loop, and the field is still unsettled on continuous-vs-discrete cross-level updating (a 2025 study, not yet consensus) | Cortical hierarchy of temporal receptive windows; hierarchy's functional payoff is content-gated (disappears for scrambled/rest stimuli in the source manipulation) | `predictive_coding.py` exists but the CPCL loop is non-contrastive (memorizes, contrast_fires=False); flat single-timescale; **hierarchical multi-timescale wrapper is GENUINELY UNBUILT** (verified zero filesystem hits) | **MISSING** — but sequence-gated (base loop not closed; would be a can't-fail cell today per SURVEY doc) |
| 8 | **Memory / consolidation of what's read** | Hippocampal encoding of the situation model, then offline (sleep) systems consolidation to neocortex — a standing, well-replicated view that this is a GENUINELY SEPARATE, different-timescale mechanism from comprehension-time processing | Complementary Learning Systems (McClelland/McNaughton/O'Reilly); sharp-wave-ripple replay | **HAVE** — ~110 `exp_cls_*`/hippocampal-engram cells, mature sub-literature (mixed verdicts, not reader-specific) | **BUILT, extensively** |
| 9 | **Metacognition / confidence** (second-order readout) | Know-in-advance you're likely wrong; abstain | aPFC meta-d' readout | **HAVE** — metacognition/abstain + conformal transfer CG | **BUILT, CHAIN_GRADE** (atoms 29367/29370) |
| 10 | **Attention / selective gating / salience** | Precision-weighting, biased competition, reliability-tracking across sources | Distributed attentional/salience network | **HAVE (partial)** — independent-channel reliability gate + common-mode detector CGs act as a text-domain analog (source-reliability estimation, not perceptual salience) | **BUILT, CHAIN_GRADE** (atoms 29376/29378), scope-bounded to independent-random + correlated-common-mode errors |

Notes on this table vs the 2026-07-20-morning ACCOUNTING doc: items 9 and 10 were listed there as "TOTAL GAP" —
that has since been closed by the self-monitoring-layer build program (5 CGs now landed, per MEMORY). This drill's
table reflects the CURRENT built state, not the ACCOUNTING doc's snapshot at time of writing; the ACCOUNTING doc's
own framing ("mature on fixed-algebra/capacity/WM, missing on learned/self-monitoring") is now itself partially
stale in the direction of MORE built, not less — the self-monitoring axis substantially closed since. The remaining
open axis is specifically the content/grounding one (items 5, 6-content-half, and eventually 7's hierarchy once the
base loop exists).

## (e) Single most load-bearing missing component — machinery or content?

**CONTENT.** Every machinery-flavored component in the stack (binding, role-representation, WM buffer, cleanup-rule,
codebook-retrieval, consolidation/replay, metacognition, reliability/common-mode gating) has a filesystem-verified,
VET'd substrate equivalent. The one component with a clean, repeatedly-confirmed negative (6 failed self-supervised
text signals for patient-selection, per the patienthood note) is not missing an operation — the binding, role-hub,
and WM machinery that would consume a patienthood signal already exist and are proven. What's missing is the DATA:
learned event-plausibility content (which entity typically undergoes change-of-state / is causally affected, at the
graded animate-animate level) at sufficient density/explicitness in the corpus. The brain's own literature (Kauf et
al. 2023; the 2026 plausibility-under-compositional-pressure follow-on) shows this is not a substrate-specific
artifact — it is the SAME sub-capability the wider LLM/cognitive-science field has independently flagged as the
sharpest weak point in text-only systems, with the leading diagnosis being reporting bias (ordinary corpora
under-state explicit outcome/change-of-state language), i.e. a fixable content-composition problem rather than a
missing architecture.

The one genuinely-unbuilt MACHINERY component (hierarchical multi-timescale prediction, item 7) is real but does not
compete for "most load-bearing" today: it is explicitly sequence-gated (nothing to hierarchically integrate until a
working flat comprehension loop exists) and would be analytically can't-fail if built now, per the design-gate
discipline and the SURVEY doc's own recommendation to hold it.

## (f) Substrate-product implications

- This reframes "build the missing machinery" (the framing that drove the self-monitoring-layer build program,
  now largely complete) toward "curate/derive the missing content" as the next investment class. That is a
  different KIND of work — corpus composition and lexicon-informed feature engineering, not new cell architectures
  — and should not be conflated with further self-monitoring-layer builds (which are now mostly done).
- The cheap decisive test in (b) is designed to be diagnostic BEFORE committing to either a corpus-curation program
  or a hierarchical-architecture program: it isolates content and architecture as separate levers on the exact
  metric that has failed 6 times, reusing existing infrastructure (no new grounding modality, no new cell family).
- If HARD-PASS: the path is corpus/lexicon curation (VerbNet-informed or corpus-alternation-detection content
  signals), which is squarely inside the "adopt from prior art, recombine" build discipline already in force —
  not a new research program.
- If HARD-FAIL (architecture-competitive or neither moves it): re-open the hierarchical-timescale item ahead of
  schedule (if architecture wins) or treat this as the strongest evidence yet for a genuine
  perception/grounding requirement (if neither wins) — but per the event-plausibility note, perception should
  remain the LAST resort tested, not the second move.
- Visual word recognition (item 1) is confirmed as correctly out-of-scope: the substrate's design choice to ingest
  tokenized text bypasses this stage entirely, matching how blind readers (Braille) and any post-OCR text pipeline
  also bypass VWFA-specific machinery without loss of comprehension capability — this is not a gap, it's an
  intentional and brain-consistent shortcut.

## Citations (verified count)

This drill's 3 fresh sub-agent lit-scans returned 36 distinct new sources (16 visual-word-recognition/lexical-access,
10 morphosyntax, 10 predictive-coding/consolidation), each with author/year or direct URL; sub-agents flagged their
own confidence per claim (well-replicated vs single-study/contested) per the calibration discipline — contested
items (ELAN as a genuine syntax-specific component; N400 lexical-vs-integration interpretation; TDH vs
general-WM-capacity account of agrammatism; continuous-vs-discrete cross-level predictive updating) are called out
inline in (d), not smoothed over. Combined with the 24 citations in the event-plausibility note and ~11 in the
patienthood note's neural sub-scan (both already independently verified in their own notes), this synthesis rests on
~71 cumulative citations, not re-verified beyond each note's own verification pass.

## Key new citations (this drill)

Dehaene & Cohen 2011 (VWFA); Vogel et al. 2014; Chen et al. 2019 (VWFA); Coltheart et al. (DRC/triangle dual-route);
McClelland & Rumelhart 1981 (IA); TRACE (McClelland & Elman); Kutas & Federmeier 2011 (N400); Patterson/Lambon Ralph
(hub-and-spoke, ATL); Santi & Grodzinsky (BA44 movement-distance fMRI); Steinhauer & Drury 2012 (ELAN critique);
Frazier (garden-path); MacDonald/Trueswell/Tanenhaus (constraint-based); Hale 2001, Levy 2008 (surprisal); Gibson
1998/2000 (DLT); Lewis & Vasishth 2005 (cue-based retrieval); Grodzinsky (Trace Deletion Hypothesis); Friston &
Kiebel (free-energy/predictive coding); Wilcox et al. 2023 (surprisal, 11 languages, TACL); Hasson et al. 2008
(temporal receptive windows, J Neurosci); PNAS 2022 narrative-construction TRW follow-up; Commun. Biology 2025 /
bioRxiv 2025.03.27.645665 (continuous-vs-discrete cross-level updating, flagged single-study/emerging); McClelland,
McNaughton & O'Reilly 1995 (CLS); sleep/systems-consolidation reviews (Neuron 2023, Science Advances 2019).
