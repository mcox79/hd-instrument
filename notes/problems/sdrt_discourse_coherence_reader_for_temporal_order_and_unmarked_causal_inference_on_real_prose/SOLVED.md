---
problem: sdrt_discourse_coherence_reader_for_temporal_order_and_unmarked_causal_inference_on_real_prose
status: PARTIAL
bar: "PASSES only with ALL of: 1. A glass-box SDRT-lite coherence reader (INFER Narration/Result/Explanation/Background/Elaboration from CAUSAL-WORLD-KNOWLEDGE inference, NOT surface connectives; map the relation to (a) a timeline correction fed to temporal_reasoner and (b) an inserted UNMARKED causal link fed to causal_reasoner; copy the Lascarides-Asher/Hobbs abductive-coherence COMPUTATION; SWEEP the world-knowledge source, relation granularity, override-confidence threshold). 2. CI-separated over the naive floor on the OVERRIDE slice AND/OR recovers unmarked causal links, on MODERN gold: (a) TEMPORAL OVERRIDE on TB-Dense reverse-order (iconicity=0.0000) CI-sep over iconicity; (b) UNMARKED CAUSAL on TellMeWhy non-adjacent (adjacency/recency=0.0000) CI-sep over BOTH the connective-only extractor and the adjacency floor. 3. The info-free twin (SHUFFLED coherence labels) LOSES CI-separated. 4. NO-regress on the two live consumers + the world-knowledge is load-bearing, not the marker (connective-only channel does NOT clear the floor while world-knowledge does). 5. One-screen summary. A rigorous NEGATIVE is a FULL PASS (most likely: the world-knowledge asset covers too few causal-plausibility contrasts to discriminate Explanation from Narration on real prose, the same coverage wall the causal reasoner located at CSKG 17.3%, enumerated with counts)."
result: "The MECHANISM is built + brain-faithful + PROVEN, coupled to BOTH landed reasoners with no-regress; the real-prose capability win is the brief's BLESSED LOCATED NEGATIVE (coverage), quantified from BOTH sides + convergent with the causal reasoner's CSKG 17.3%. (MECHANISM, constructed Lascarides-Asher minimal pairs, n=48, NO connectives): relation-4way reader 0.8125 vs connective-only 0.2500 (+0.5625 CI[0.375,0.729]) AND vs the info-free shuffled-label twin 0.2917 (+0.5208 CI[0.333,0.688]) -- twin LOSES CI-sep; order-edit (reverse/forward/overlap) 0.8750 vs iconicity 0.5000 (+0.3750 CI[0.208,0.542]); causal-edge direction 0.7500 (n=24). (TELLMEWHY unmarked-causal, answerable n=1500, non-adjacent n=256): coherence recovers the human cause 0.2773 vs adjacency 0.0000 (+0.2773 CI[0.223,0.336]) AND connective-only 0.0000 (+0.2773) -- CI-sep over both naive floors the bar names; the causal_reasoner graded_necessity over the inferred coherence-typed edges reproduces the cause-ID (coupling 0.25, n=256). (TB-DENSE temporal-override, no-cue cross-sentence n=277): LOCATED NEGATIVE -- the Explanation detector's flip precision 0.4130 is NOT CI-separated above the base rate of reverse-order 0.4368 (diff CI[-0.191,+0.148]); newswire reverse-order is dominated by inverted-pyramid/reporting-mode genre convention, not causal flashback (Zhang & Xue 2018; TB-Dense 47.7% VAGUE). THE COVERAGE WALL (both slices): the directed causal signal on real prose is a minority-class weak signal -- coherence ties the TOPICAL baseline (+0.0273 CI[0.0,0.055]) and the shuffled twin (+0.0156 CI[-0.059,0.094]) on TellMeWhy; matches the landed U8 simulator (+0.030) and CSKG 17.3%. (c IS THE BINDING AXIS): directional correctness rises content-only 0.000 -> base-full 0.792 CI-sep (+0.7917); DEEPENING class-level engines (FrameNet force typer + implicit-causality psych-verb direction) does NOT cross the wall (-0.0417 on constructed; identical 0.2773 on TellMeWhy) -- the lever is KG-scale priors, not deeper class-level engines (research-confirmed)."
floor: "MECHANISM: connective-only reader (no markers present -> NARRATION) 0.2500 = majority-class; the shuffled-label info-free twin 0.2917; iconicity (always-forward) order-edit 0.5000 -- reader CI-sep above ALL three. TELLMEWHY non-adjacent: adjacency (q-1) 0.0000 and connective-only (reader _read_causation cross-sentence) 0.0000 by construction on the non-adjacent subset -- coherence CI-sep above both; the TOPICAL content baseline 0.2500 and the shuffled-score twin 0.2617 are NOT beaten CI-sep (the coverage wall). TB-DENSE: iconicity on the reverse-order subset 0.0000 (the degenerate positive control -- any flip scores); the HONEST floor is base-rate-reverse 0.4368 vs flip_precision 0.4130 (NOT selective) + twin_p95 0.60."
controls: "(1) INFO-FREE TWIN (shuffled coherence labels, count-matched) -- LOSES CI-sep on the MECHANISM control (twin 0.2917 << reader 0.8125); TIES on both real-prose slices (the located coverage wall, reported honestly). (2) CONNECTIVE-ONLY channel -- the reader's own _read_causation: 0.2500 on the mechanism control (== majority, blind without markers) and 0.0000 on TellMeWhy non-adjacent (cross-sentence links are structurally absent -- the proven marker located negative); coherence CI-sep over it. (3) ADJACENCY/RECENCY floor -- 0.0000 on TellMeWhy non-adjacent by construction; CI-sep. (4) FLIP-SELECTIVITY (TB-Dense) -- flip_precision NOT CI-sep above base-rate-reverse: proves the reverse-subset 'win' is a degenerate-metric artifact, not a real signal (the honest located negative). (5) NO-REGRESSION -- temporal_reasoner.before() with the channel OFF is BYTE-IDENTICAL (10/10 passages); channel-ON differs ONLY on Explanation-over-iconicity pairs (additive, confidence-gated); causal sm.causal_links byte-identical with the coherence graph built alongside. (6) ENGINE ABLATION -- content-only (symmetric) scores 0.000 directional correctness (chance); physics/psych add the directed signal (c is the binding axis). (7) DEEPENED-vs-BASE -- the deepened engine does NOT beat base (the wall is coverage, not engine depth)."
files_changed: "experiments/_sdrt_coherence.py (the reusable SDRT-lite coherence reader: DICE relation inference via directed causal-plausibility asymmetry + aspect, confidence-gated); experiments/exp_sdrt_coherence_mechanism_v1.py (constructed Lascarides-Asher minimal-pair mechanism control); experiments/exp_sdrt_temporal_override_tbdense_v1.py (TB-Dense temporal-override located negative + flip-selectivity); experiments/exp_sdrt_unmarked_causal_tellmewhy_v1.py (TellMeWhy unmarked-causal + causal_reasoner coupling); experiments/exp_sdrt_deepen_simulator_v1.py (the upstream deepening / c-is-binding-axis ablation ladder); experiments/exp_sdrt_no_regress_v1.py (byte-identity no-regress on both consumers); verification/test_sdrt_coherence_reader.py (scaffold-free witness, 9/9); notes/problems/sdrt_discourse_coherence_reader_for_temporal_order_and_unmarked_causal_inference_on_real_prose/{SOLVED.md,RESEARCH_coherence_mechanism_and_coverage_2026-09-07.md}. Gold reused (already on disk): data/corpora/{tb_dense,tellmewhy}. NO hdlab write (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_sdrt_coherence_reader.py   # 9/9 PASS (~10s): W0 module mechanism; W1 mechanism control (relation+order-edit CI-sep over connective+twin+iconicity); W2 TB-Dense LOCATED NEGATIVE (flip_precision not selective); W3 TB-Dense mechanism fires; W4 TellMeWhy CI-sep over adjacency+connective; W5 coverage-wall tie; W6 c is binding axis; W7 no-regress byte-identical; W8 causal_reasoner coupling reproduces cause-ID"
---

# The SDRT-lite coherence reader is BUILT, brain-faithful, and coupled to both reasoners; the real-prose capability is the brief's blessed COVERAGE located negative, quantified from both sides

## What I built (brain mechanism first)
The opening move was the brain's. A reader does NOT read discourse structure off connective words; it INFERS the
coherence relation between adjacent discourse units by defeasible/abductive reasoning over world knowledge, and the
inferred relation CONSTRAINS the temporal and causal interpretation (Hobbs 1985; Hobbs, Stickel, Appelt & Martin 1993
"Interpretation as Abduction"; Kehler 2002; the constructionist "search after meaning" -- Graesser, Singer & Trabasso
1994; Kintsch 1988). SDRT/DICE (Lascarides & Asher 1993; Asher & Lascarides 2003) makes the consequences explicit via
defeasible axioms + the INDEFEASIBLE "Causes Precede Effects". I copied that computation exactly:

`experiments/_sdrt_coherence.py` -- a `CoherenceReader` that infers the relation between adjacent units (a first, b
second) from a directed causal-plausibility ASYMMETRY (f = plausibility a causes b; r = plausibility b causes a),
gated by aspect:
- **NARRATION** (default) => sequence, no override;
- **RESULT** (f >> r) => forward causation, edge a->b;
- **EXPLANATION** (r >> f) => b causes a => REVERSE surface order, edge b->a (the "Max fell. John pushed him."
  flashback -- no marker);
- **BACKGROUND / ELABORATION** => overlap, routed to the ASPECT signal (stativity), NOT the causal engine.

The directed plausibility REUSES the causal reasoner's U8 generative simulator (the brief's endorsed source):
content relatedness AMPLIFIED by intuitive physics (force-action -> result-state) + intuitive psychology (appraisal
valence-congruence + mental TRIGGER->OUTCOME cascade). PINNED: the SDRT/DICE computation + the causal-plausibility
discriminator (confirmed by a literature drill, `RESEARCH_coherence_mechanism_and_coverage_2026-09-07.md`).
OUR-INVENTION-UNDER-TEST (swept): the engine composition, the override-confidence threshold tau + directional margin,
the relation granularity.

**A research-driven CORRECTION to the brief's frame (folded in):** Background/Elaboration are NOT resolved by causal
plausibility -- they are aspectual (Lascarides-Asher States-Overlap law, keyed to stativity) / mereological
(Moens-Steedman). So the reader routes them to the aspect signal; only Narration/Result/Explanation are decided by
causal plausibility. This is more faithful than typing all five relations off one engine.

## What I measured (one-screen summary; each floor recomputed on its own population)

| slice | population | headline | verdict |
|---|---|---|---|
| **MECHANISM (constructed)** | 48 Lascarides-Asher minimal pairs, NO connectives | relation-4way **0.8125** vs connective 0.2500 (+0.5625) + twin 0.2917 (+0.5208, LOSES CI-sep); order-edit **0.8750** vs iconicity 0.5000 (+0.3750); causal-edge dir 0.75 | MECHANISM PROVEN |
| **TELLMEWHY unmarked-causal** | non-adjacent cause (n=256; adjacency/recency=0) | coherence **0.2773** vs adjacency **0.0000** (+0.2773 CI-sep) + connective-only **0.0000** (+0.2773 CI-sep); coupling graded_necessity 0.25 | position/marker floors CLEARED |
| **... the coverage wall** | same | vs TOPICAL 0.2500 (+0.0273 CI[0.0,0.055]) + twin 0.2617 (+0.0156, TIE) | LOCATED NEGATIVE |
| **TB-DENSE temporal-override** | no-cue cross-sentence (n=277) | flip_precision **0.4130** vs base-rate-reverse **0.4368** (diff CI[-0.19,+0.15], NOT selective); coverage 36.5% | LOCATED NEGATIVE |
| **DEEPEN / c-axis** | 24 directional pairs | content 0.000 -> base-full **0.792** (+0.7917 CI-sep); deepened 0.750 (-0.04) | c IS THE BINDING AXIS |
| **NO-REGRESS** | 10 passages + a doc | temporal channel-OFF byte-identical 10/10; ON diffs all Explanation-over-iconicity; causal links byte-identical | ADDITIVE |

**The two live wins are the MECHANISM (the reader genuinely infers the DICE relation + its temporal/causal
consequence from world knowledge, not connectives -- twin LOSES CI-sep) and the COUPLING + NO-REGRESS (the inferred
coherence-typed edges feed both landed reasoners additively, byte-identical when off).** The real-prose capability win
is the brief's explicitly-blessed LOCATED NEGATIVE.

## The wall, drilled and quantified from BOTH sides (the blessed negative)
The brief predicted the likely negative verbatim: "the world-knowledge asset covers too few causal-plausibility
contrasts to discriminate Explanation from Narration on real prose ... the same coverage wall the causal reasoner
located at CSKG 17.3%, enumerated with counts." That is exactly the result, quantified from two independent sides:

1. **NEWSWIRE (TB-Dense temporal-override):** the Explanation detector flips no-cue pairs to reverse-order, but its
   flip precision (0.4130) is NOT CI-separated above the base rate of reverse-order (0.4368) -- it flips the RIGHT
   (truly-reverse) pairs no better than chance. WHY (drilled + research-confirmed): newswire reverse-order is
   DOMINATED by inverted-pyramid / reporting-mode genre convention, NOT causal flashback (Zhang & Xue 2018 measure
   news as ~54% OVERLAP "reporting mode"; TB-Dense is 47.7% VAGUE; only 11.2% of TimeBank links carry an explicit
   signal). So improving causal plausibility CANNOT move the newswire needle -- most of that signal is genre, not
   inferable causation. (The reverse-order-subset "win" of 0.157 vs iconicity 0.000 is a DEGENERATE-metric artifact:
   on a uniformly-reverse subset ANY flip scores, real or shuffled -- twin_p95 0.60 > coherence 0.53 on the whole
   population. The honest test is flip-selectivity, and it is null.)

2. **NARRATIVE (TellMeWhy unmarked-causal):** coherence recovers the human cause CI-separated over the ADJACENCY and
   CONNECTIVE-only floors (both 0.0000 on non-adjacent -- the naive floors the bar names), but only TIES the topical
   content baseline (+0.0273) and the shuffled twin (+0.0156). The directed causal signal is a minority-class weak
   signal on real prose -- matching the landed U8 generative simulator's own +0.030, and the field's non-LLM
   implicit-relation ceiling (~40-45% multiclass; causal relations are ~4-11% of RST relations, ~15-30% of narrative
   adjacent pairs -- research drill).

3. **c IS THE BINDING AXIS, and DEEPENING class-level engines does not cross it.** The causal reasoner's phase diagram
   collapsed the residual to edge CORRECTNESS c. The coherence reader's Explanation/Result discrimination IS a c
   problem: directional correctness rises content-only 0.000 (symmetric -> chance) -> base-full 0.792 (+0.7917 CI-sep)
   -- the engines carry real directed signal. But DEEPENING them (FrameNet force typer + implicit-causality psych-verb
   direction, the research's top-2 no-LLM levers) does NOT raise c (-0.0417 constructed; identical 0.2773 on
   TellMeWhy). The lever is KG-SCALE causal priors (CauseNet/GLUCOSE-scale), NOT deeper class-level engines -- but the
   causal reasoner already showed generic retrieval (CSKG) is coverage-bounded at 17.3%, and simulation > retrieval;
   the brain-faithful successor is a content-sensitive generative ROLLOUT (the causal reasoner's own P1, a large build).

## What I did NOT establish (withdraw-first if wrong)
- **I would withdraw first any implication of a real-prose CAPABILITY win.** The coherence channel does NOT beat the
  topical baseline or the shuffled twin CI-separated on either real-prose slice. What is proven on real prose is (a)
  the mechanism CLEARS the position/marker floors the bar names (adjacency, connective-only), and (b) the wall is
  COVERAGE, located and quantified from both sides -- a rigorous negative, the one the brief blesses as a full pass.
- The MECHANISM win is on a CONSTRUCTED gold (labelled, can-fail) -- it proves the reader infers the DICE relation
  from world knowledge when the contrast is PRESENT; it is not a real-prose coverage claim (which is the negative above).
- The TB-Dense reverse-order-subset recovery (0.157 vs 0.000) is NOT a positive -- it is a degenerate-metric artifact
  (any flip scores on a uniformly-reverse subset); the honest measurement is flip-selectivity (null).

## KEY REALIZATIONS (the enabling moves)
1. **The reverse-order subset is a DEGENERATE positive control.** On a subset where the answer is uniformly "reverse",
   ANY flip -- real OR the shuffled twin -- scores; the twin p95 (0.60) beats the real channel (0.53) on the whole
   population. The honest discriminator is FLIP SELECTIVITY: does the detector flip the truly-reverse pairs above their
   base rate? It does not on newswire (0.413 vs 0.437). This is the "construct the info-free version and check it
   scores" discipline applied to a positive control that looked like a win.
2. **The coverage wall is the SAME wall from two sides.** The causal reasoner located it as CSKG retrieval 17.3%
   coverage (from the edge-existence side); this reader locates it as newswire flip-precision = base rate AND TellMeWhy
   coherence = topical/twin (from the relation-inference side). Two independent measurements, one wall: directed causal
   plausibility on real prose is a minority-class, low-coverage signal within the no-LLM invariant.
3. **Background/Elaboration are NOT causal -- route them to aspect.** The brief's five-relation inventory implied one
   engine; the research showed Background is the aspectual States-Overlap law and Elaboration is mereological. Routing
   them to stativity (not causal plausibility) made the reader more faithful and stopped the causal engine from
   firing where it structurally cannot.
4. **DEEPENING the engine is the wrong lever; c is coverage-bound, not depth-bound.** The FrameNet force typer + IC
   psych-verb direction (the field's top no-LLM levers) did not raise c -- because where they fire they are redundant
   with the base engines, and most real-prose pairs have no detectable causal contrast at all. The research's own
   steer: scale to KG-size priors, don't deepen class-level engines.
5. **The mechanism is genuinely brain-faithful and genuinely works -- the negative is about the WORLD, not the model.**
   The reader hits 0.81/0.875 on the constructed contrasts with the twin losing CI-sep; the failure on real prose is
   that the causal-plausibility contrasts the mechanism needs are simply not present in most real adjacent-sentence
   pairs (a fact about text, confirmed by PDTB/RST/Zhang-Xue distributions), not a flaw in the mechanism.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md sec.2b)
- **NEW organ (proposed, built in experiments/): a glass-box SDRT-lite DISCOURSE COHERENCE reader** -- the missing
  reader BOTH landed inference organs (temporal_reasoner Wall-1/2, causal_reasoner extraction-sparsity) named as their
  shared top wall. PINNED computation: SDRT/DICE (Lascarides-Asher) coherence-relation inference by abduction over
  world knowledge + the indefeasible Causes-Precede-Effects axiom; the Narration/Result/Explanation discriminator is
  causal plausibility; Background/Elaboration are aspectual/mereological (NOT causal -- a correction to fold in).
  Proven on constructed minimal pairs (twin loses CI-sep); coupled to both reasoners additively (no-regress).
- **The causal-world-knowledge COVERAGE wall is now measured from a SECOND side.** The audit records the causal
  reasoner's CSKG 17.3% coverage bound (edge-existence side). This reader adds the relation-inference side: newswire
  reverse-order flip-precision = base rate (reverse-order is genre convention, not causal -- Zhang & Xue 2018); and
  TellMeWhy coherence = topical/twin (minority-class weak signal). Same wall, converged. Deviation to record: the
  discourse-coherence channel is NOT wired into read() -- the reader has no coherence-relation register; the proposed
  landing is additive + confidence-gated (below).
- **The generative causal-plausibility simulator is confirmed as the c-lever, and DEEPENING class-level engines does
  not raise c.** The audit's Trabasso covariation-causal-graph-inference PINNED-to-BUILD entry recurs here: c
  (correctness) is the binding axis, coverage-bound not depth-bound; the successor is a content-sensitive generative
  rollout / KG-scale priors, not deeper class-level heuristics.

## Adjacent components (evaluated for brain-fidelity + optimization, per owner 2026-08-28)
1. **The generative causal-plausibility simulator (the shared upstream of BOTH reasoners).** *Capability:* directed
   physics + psychology + content, beats topical +0.030. *Limitation:* class-level, coverage-bounded (c ceiling on
   real prose). *Brain status:* PINNED direction (simulation > retrieval); an OUR-INVENTION class-level approximation
   of a content-sensitive rollout. *Opportunity:* the single highest-leverage lift for temporal AND causal AND
   coherence at once -- a grounded generative rollout (intuitive-physics object/force state + inverse-planning social
   sim), the causal reasoner's own P1. This is the next problem, and it is now confirmed by THREE consumers.
2. **temporal_reasoner.before() iconicity fallback.** *Capability:* cue/date/iconicity with provenance. *Limitation:*
   ~76% of pairs fall to iconicity (near-chance on reverse-heavy newswire). *Opportunity:* the coherence override is
   the additive channel for the no-cue subset -- it works on constructed flashbacks (mechanism control) but the
   newswire coverage is genre-bound; it will help on NARRATIVE genres where flashback is causal (a future narrative
   temporal gold, not TB-Dense).
3. **situation_reader._read_causation.** *Capability:* connective + within-sentence mental-bridge links. *Limitation:*
   builds ZERO cross-sentence unmarked links (confirmed: 0.0000 connective-only on TellMeWhy non-adjacent). *Opportunity:*
   the coherence reader's Result/Explanation edges are the additive cross-sentence-link source (a NEW field), gated on
   confidence -- but bounded by the same coverage wall until the simulator deepens.
4. **A modern DISCOURSE-RELATION gold is missing on disk.** GUM has only the conllu (coref/dep) layer locally, not the
   eRST/discourse-relation layer. Acquiring GUM-eRST or RST-DT would let a future problem validate the relation reader
   DIRECTLY (not just the downstream correction) -- the named next instrument.

## Proposed hdlab landing (strategy lands; Q111 -- I do not write hdlab/)
1. **Promote `experiments/_sdrt_coherence.py` as `hdlab/coherence_reader.py`** -- a glass-box `CoherenceReader`
   consuming adjacent discourse units, exposing `relate()` (the DICE relation + confidence + provenance),
   `order_edit()`, `causal_edge()`. Reuses the U8 simulator engines + event_type + affect_lexicon. ADDITIVE.
2. **Wire it CONFIDENCE-GATED + DEFAULT-OFF, and measure the live impact before flipping (per the no-more-default-off
   discipline).** (a) temporal_reasoner.before(): on a no-cue pair, override the iconicity fallback ONLY on a confident
   EXPLANATION (byte-identical off/unconfident -- proven 10/10). (b) causal_reasoner: populate a NEW
   `sm.inferred_coherence_links` field (do NOT touch sm.causal_links -- connective causal QA stays byte-identical) from
   the Result/Explanation edges. Because the real-prose signal is coverage-bound (this negative), the honest live
   impact is ~0 until the simulator deepens -- so land it OFF, wired, with the impact measured, NOT as a claimed lift.
3. Do NOT land a real-prose coherence LIFT claim (the located negative). Do NOT rebuild the temporal/causal reasoners
   or re-derive the U8 simulator / CSKG retrieval (fenced). Fold the AUDIT UPDATE.

## TLDR (plain English)
When we read, we silently work out how each sentence connects to the last -- which came first, what caused what --
even though the text almost never says so. I built the reader that decides that KIND of connection by reasoning about
what is plausible in the world (does the second sentence explain the first? then it happened first and caused it),
not by hunting for a joining word like "because". On clean textbook-style examples it works well: it names the right
connection 81 times in 100 and gets the time-order right 88 times in 100, while a scrambled-connection version drops
to a coin flip -- and it correctly feeds both of the reader's new skills (the timing one and the cause one) without
breaking either. BUT on real published text it hits a wall the brief predicted, and I pinned down exactly what the
wall is, from two directions: (1) in real NEWS, sentences told out of order are almost always just news-writing style
(headline first, background later), NOT genuine cause-and-effect flashbacks -- so a cause-reasoner cannot tell which
is which any better than a coin flip; (2) in real STORIES, genuine unspoken cause-and-effect between sentences is a
minority (most connections are just "and then" or elaboration), and the plausibility signal, while real, is only a
hair above a shuffled baseline -- exactly matching what the cause-reasoner found from its side (its cause-knowledge
lookup covered only 17% of real cause-pairs). I also tried to make the plausibility engine deeper (adding two
research-recommended tricks), and it did not help -- because the wall is COVERAGE (the needed cause-clues just are not
in most sentences), not the engine's depth. The honest verdict: the mechanism is right and brain-faithful and is
wired to help both reasoners, but the world-knowledge it needs is too sparse in real prose to show a win yet -- the
same wall, now measured from three sides, and the fix is a bigger cause-simulation engine, not this reader.

## QUESTIONS
None blocking. One labelling call for the strategy session: I filed **PARTIAL**. The MECHANISM is proven (constructed
control, twin loses CI-sep), the COUPLING + NO-REGRESS hold, and one real-prose floor set (adjacency + connective-only)
is cleared CI-sep -- but the real-prose CAPABILITY win (the twin losing on real prose) is NOT achieved; it is the
brief's explicitly-blessed LOCATED NEGATIVE (coverage), quantified from both sides + convergent with CSKG 17.3% + the
field. The brief states "a rigorous NEGATIVE is a FULL PASS", so if you prefer the label tied to the blessed-negative
clause this is a **SOLVED**; I filed PARTIAL to keep the label honest to "no real-prose capability win". The science is
identical either way.

## NEXT STEPS (priority-ordered)
- **P1 (the real lever, shared by THREE consumers -- temporal, causal, AND coherence).** DEEPEN the generative
  causal-plausibility simulator into a CONTENT-SENSITIVE ROLLOUT (intuitive-physics object/force state + inverse-planning
  social simulation over the resolved participants), composing the landed force_dynamics_typer + goal_register +
  belief_partition + affect_register -- the causal reasoner's own P1, now confirmed as the binding axis c from a third
  side. This is the only route past the coverage wall within the no-LLM invariant (retrieval is coverage-bounded; the
  brain simulates). Large build; the right one.
- **P2 (a fair instrument for the temporal-override).** TB-Dense newswire is the WRONG genre (reverse-order is a genre
  artifact). Acquire a NARRATIVE temporal-order gold with genuine flashback (or annotate the TellMeWhy non-adjacent
  causes for order) to test the Explanation-reverses-order channel where causal flashback actually occurs.
- **P3 (direct relation-reader validation).** Acquire GUM-eRST or RST-DT (modern discourse-relation gold; only GUM's
  conllu layer is on disk) and validate the coherence reader's inferred relation DIRECTLY against gold discourse
  relations, not just the downstream correction.
- **P4 (land the wiring, default-OFF, impact-measured).** Land hdlab/coherence_reader.py per the proposal, wired
  confidence-gated + default-OFF into both consumers, with the live impact measured (currently ~0 by the coverage
  wall) so it is ready to switch on the moment P1 deepens the simulator.
