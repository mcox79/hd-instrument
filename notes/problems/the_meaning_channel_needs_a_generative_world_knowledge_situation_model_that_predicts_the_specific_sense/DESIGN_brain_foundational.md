# Design: the generative world-knowledge situation model that predicts the SPECIFIC sense

Solver, 2026-09-02. The brain-first opening move, recorded before the build hardens. Tags: [PINNED] brain-fixed | [OUR-INVENTION] swept/under-test.

## The lever, inherited and NOT re-derived (parent = owner-DONE EXCELLENT located negative)
The parent decomposed the meaning-channel wall exactly: `net = fired * [ p*a_s - (1-p)*c_d ]`, measured `p~0.48`
(detector precision), **`a_s~0.33`** (override accuracy on the fired-subordinate set = "which SPECIFIC rare sense"),
`c_d~0.64` (dominant disruption). DETECTION is maxed (directional domI AUC ~0.69-0.71). The binding term is `a_s`.
The parent PROVED `a_s` is NOT a readout change **over the cn_syn co-occurrence graph** (a sense-signature readout
over the graph neighbourhood was WORSE, 0.261->0.213). So the lever is a different SOURCE.

Two facts from the disk that reshape the brief (before_you_start + 3 targeted reads):
- **Classic Lesk word-overlap is a CLOSED negative** (WiC 0.522, at floor) -> do NOT re-run it.
- **A gloss/definitional signal as a MEANING VECTOR is the strongest definitional result on disk** (WiC extended-gloss
  embedding 0.619, CI-clears the wall where context cannot; `exp_sense_wall_breakthrough_wic_v1`), and the landed
  `ConceptualChannel` (ATL hub; SimLex rho 0.521, shuffled-gloss twin loses) is an IDF-weighted per-synset definitional
  bag. **NEITHER has ever been run on the SemCor subordinate-selection task.** This is the untested SOURCE.
- Benchmark to beat: `exp_context_override_frequency_wsd_v1` (owner-DONE) reaches **0.39 on the subordinate population**
  with a LEARNED distributional context-likelihood (held-out SemCor prototypes) -- co-occurrence, NOT definitional.

## How the brain does THIS (PINNED)
Sense selection is TOP-DOWN prediction from a hierarchical GENERATIVE model of the SITUATION, not bottom-up
co-occurrence (predictive coding, Rao-Ballard 1999 / Friston 2010; N400 = semantic prediction error, Kutas-Federmeier
2011, Rabovsky-McClelland 2018). Two PINNED pieces the parent did not have:
1. **The sense is a definitional SCHEMA in the ATL amodal hub** (Controlled Semantic Cognition; Lambon-Ralph 2017):
   what a concept IS = its distinctive definitional/taxonomic features, privileging distinctive features. This is the
   sense-SPECIFIC representation -- and it is FREQUENCY-INDEPENDENT (definitional content, not corpus co-occurrence).
   The cn_syn graph the parent read carries co-occurrence/relation edges and defaults to frequency; the gloss does not.
2. **The situation activates UNMENTIONED concepts by schema/script/frame knowledge** (Schank-Abelson scripts;
   Chambers-Jurafsky narrative chains; FrameNet role expectations; McClelland situation-model semantics). "he sat on the
   bank" resolves because prior discourse (fishing/river) has activated {water, boat, current} -- concepts NOT in the
   target sentence. This is the GENERATIVE half: the top-down prediction a local graph cannot supply.

## The mechanism (this build)
For each polysemous target (lemma, pos) with candidate WordNet senses {s_1..s_k} in context (sentence + struct + discourse):
- **Sense signature `sigma(s)` [PINNED: ATL definitional hub]:** per-synset definitional feature set = gloss (+examples,
  SemCor is not built from glosses so no leak) + synonym lemmas + 1-2 level hypernym/relation closure, IDF-weighted
  (distinctive-feature op, reuse `conceptual_meaning`). Also a CONTINUOUS arm: the extended-gloss Binder-65 embedding
  (`exp_sense_wall_breakthrough`) -- the brief's "sense-SPECIFIC continuous representation". [OUR-INVENTION: which
  representation + closure depth -> sweep.]
- **Situation `S` [the generative model]:** `S_mentioned` = IDF-weighted bag of context content lemmas (sentence + struct
  + discourse pool). `S_expanded` = `S_mentioned` (+) world-knowledge-inferred concepts [the GENERATIVE part, brief (b)]:
  FrameNet frame the head verb/noun evokes -> its core FE names + co-LU lemmas; ConceptNet (100k EN) AtLocation/UsedFor/
  Causes/CapableOf neighbours of context words; event-chain continuations (`thematic_edges_v1.pkl`). Inferred concepts
  down-weighted vs mentioned. [OUR-INVENTION: which sources, expansion weight -> sweep + ablate.]
- **Score `coh(s) = coherence(sigma(s), S)`** (IDF sparse cosine, or Binder cosine). This is the top-down sense
  prediction. It scores ALL senses, dominant included -- deliberately, to attack `c_d`, not only `a_s`.

## How it attacks the WHOLE net, not just a_s (the see-saw, bar item 2)
Break-even at `p~0.48, c_d~0.64` needs `a_s~0.69`, unreachable by a_s alone. So the mechanism must ALSO lower `c_d`.
Two brain-faithful moves:
- **Graded PRECISION-weighted combination** [PINNED Feldman-Friston], NOT a binary detect-then-inhibit gate:
  `final(s) = log prior(s) + lam * pi * coh_norm(s)`, `pi` = precision of the coherence distribution (peakedness /
  1-normalized-entropy). Flat/uninformative situation -> `pi` low -> prior wins -> dominant KEPT -> `c_d -> 0`. Sharp,
  specific situation -> override. [OUR-INVENTION: lam, pi form -> sweep.]
- The definitional signal is FREQUENCY-INDEPENDENT, so (unlike the reliability-weighted-cue-combination negative, which
  failed because its grounded cue's errors were 95.65% frequency-correlated) its wrong picks should NOT default to the
  higher-frequency sense. **This is a testable precondition I will MEASURE (error-vs-frequency correlation) before
  claiming net gain** -- if the gloss signal is also frequency-correlated on its errors, combination cannot help and I
  report that as the located sub-component.

## THE BAR maps to these controls (can-fail; CI-separated; twin must lose)
1. `a_s` CI-separated over the parent's ~0.33 on the POWERED fired-subordinate population (reproduce the parent's
   cn_syn-readout a_s on the SAME fired set first, then swap in the definitional readout). Driven by the generative rep,
   not a co-occurrence-graph readout.
2. NET gain over the MFS floor on the full polysemous population WITHOUT the see-saw (report `c_d`; precision-weighted).
3. **Shuffled-situation twin LOSES** CI-separated (item i gets another item's S, same sense-count bucket).
4. **World-knowledge ablation** (bar's attribution test): `a_s(S_expanded)` vs `a_s(S_mentioned)`. If the expansion is
   load-bearing -> the generative source is validated. If NOT -> the lever is the sense-specific REPRESENTATION and I say
   so (the brief's specific "unmentioned-concept inference" mechanism refuted-in-part; the real problem still solved).
   Plus the bootstrapping loop's effect (does re-carve/iterate converge, or does one pass suffice).

## Reachability-first (could it even succeed?) -- the first smoke measurement
On 4 SemCor files, fired-subordinate set: `a_s(cn_syn readout, reproduce ~0.33)` vs `a_s(IDF gloss-bag readout)` vs
`a_s(gloss-bag + world-knowledge expansion)` vs `a_s(Binder gloss-embedding)`. If the DEFINITIONAL readout does not beat
the cn_syn readout even before expansion, the representation premise is wrong and I pivot. If it does, expansion + net
gain are the next levers.

## Reuse (no reinvention) + brain status
`conceptual_meaning.ConceptualChannel` / `_def_bag` / global IDF [PINNED ATL hub, landed]; the extended-gloss Binder-65
embedding + `_ext_gloss_vec` from `exp_sense_wall_breakthrough_wic_v1` [validated]; the parent harness
`exp_topdown_situation_sense_selector_v1` (`_semcor_docs`, `_parse_structural`, prior, subordinate defn, directional
detector, `_eval_gated`, bootstrap) for the a_s attribution + fired set; `hdlab/semantic_control` (LIFG) as the graded
gate; FrameNet (nltk), ConceptNet 100k (`data/datasets/conceptnet5_en_100k.jsonl`), `data/thematic_relations_v1/
thematic_edges_v1.pkl` for the generative expansion; SemCor + Raganato gold. spaCy parse LOCAL, cached (reuse parent's).
Glass-box, NO external LLM at inference. AUDIT UPDATE target: BRAIN_FOUNDATIONAL_AUDIT sec 2b -- the sense-selection
binding limit is the GENERATIVE definitional/world-knowledge situation model; detection + read path validated.
