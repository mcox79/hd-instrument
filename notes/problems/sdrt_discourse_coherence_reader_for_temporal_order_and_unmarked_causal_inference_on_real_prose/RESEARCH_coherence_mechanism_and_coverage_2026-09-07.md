# Research: the brain's discourse-coherence-inference mechanism + the real-prose coverage wall

Captured in the solver's problem folder (the research drill did not persist a general notes/ file; saved here so
the SOLVED.md citation is not dangling). Verbatim-faithful synthesis of a 3-part literature drill (2026-09-07).
Strategy may fold into a general note at integration.

## 1. The mechanism is PINNED for Narration/Result/Explanation; contested at the edges
- **Hobbs 1985; Hobbs, Stickel, Appelt & Martin 1993 ("Interpretation as Abduction", AI 63:69-142):** discourse
  interpretation is abduction at lowest assumption-cost; Explanation is DEFINED as `Explanation(e1,e2) <- cause(e2,e1)`
  -- recovering the reversed causal link and resolving anaphora happen in the SAME abductive step. PINNED as the LOGIC;
  the implemented system (TACITUS) never scaled past narrow-domain KBs -> pinned as an account, not proven at open scale.
- **Lascarides & Asher 1993 (L&P 16); Asher & Lascarides 2003 (SDRT/DICE):** the five DICE consequences confirmed
  ~verbatim. A defeasible "Causal Law" competes with the default Narration axiom via nonmonotonic conflict resolution
  (Penguin Principle: more-specific defeasible rules override more-general). Once causal direction is fixed, the
  INDEFEASIBLE "Causes Precede Effects" (box-forall e1e2 (cause(e1,e2) -> e1 precedes e2)) mechanically flips temporal
  order. Narration => sequence; Result => forward; **Explanation => infers cause(e2,e1) from world knowledge, THEN
  reverses order**; Background => States-Overlap law (keyed to STATIVITY, NOT causal); Elaboration => mereological /
  preparatory-phase (Moens-Steedman event nucleus, NOT causal).
- **CORRECTION folded into the build:** causal plausibility is the discriminator ONLY for the Narration/Result/
  Explanation family. Background/Elaboration are aspectual/mereological -> route them to the aspect signal, not the
  causal engine.
- **Kehler 2002** (Cause-Effect: Result = "infer P from S0, Q from S1, normally P->Q"; Explanation = reversed
  entailment) independently corroborates SDRT from a different formalism. **Graesser-Singer-Trabasso 1994**
  (constructionist "search after meaning") + **Sanders** (causality-by-default: faster reading, lower connective-marking
  for causal relations) support running causal-plausibility inference as a cheap DEFAULT first pass -- favours this
  architecture.
- **Contested/supplementary:** Marx & Wittenberg 2024/25 -- event dynamicity/aspectual class ALONE (states before
  events) predicts some temporal-order judgments without causal content -> aspect is a genuine supplementary signal
  (as the reader uses it for Background), not a threat to the causal-discriminator claim.

## 2. Coverage reality on real prose -- the located crux, with numbers
- **PDTB 2.0** (Prasad et al. 2008): 39.5% of 40,600 relations are IMPLICIT (no connective). Within implicit:
  Expansion ~53.7%, Contingency ~25.5%, Comparison ~14.9%, **Temporal <6%**. Non-LLM implicit-relation classification
  is hard: Ji & Eisenstein 2015 reach 44.6% on 11-way Level-2; Pitler et al. 2009 per-class F1 ~ base rate (Temporal
  16.8, Contingency 47.1) -- the field's own no-LLM ceiling is LOW on the rarer classes.
- **RST-DT / GUM-eRST:** Elaboration is the plurality (~26-32%); causal-type relations (Cause/Result/Explanation/
  Contingency) ~ **4-11%** of all relations; Joint/paratactic (Narration analog) ~24-30%.
- **TimeBank / TB-Dense (newswire):** **47.7% of temporal relations are VAGUE** (order not recoverable in principle);
  only 11.2% of TLINKs carry an explicit signal word (so adverbial reordering is NOT the dominant confound).
  **Zhang & Xue 2018:** news is dominated by OVERLAP (~54%, a stative "reporting mode"); narrative by BEFORE (~53%,
  sequential). => newswire non-chronological structure is MOSTLY a genre/register effect (simultaneous reporting), NOT
  flashback-Explanation. Synthesized (low-confidence) decomposition of newswire reverse-told order: ~50-65%
  style/relevance convention, 15-25% genuine causal flashback, 10-20% reported-speech, ~10% adverbial-resolved.
- **TellMeWhy** (Lal et al. 2021): ~28.8% of why-questions have NO explicit textual answer (need inference); ~71.2%
  text-matchable. Estimated genuinely-causal (Result/Explanation) adjacent-sentence pairs in narrative: ~15-30% (a
  minority). => **+0.03 over a topical baseline is consistent with the field's difficulty ceiling, NOT a broken
  implementation** -- a minority-class problem where non-LLM classifiers cap out well below dense-embedding/LLM scale.

## 3. Brain-faithful no-LLM levers to raise causal-plausibility correctness (ranked)
1. **Implicit-causality verb lexicons** (Garvey-Caramazza 1974; Au 1986; Hartshorne-Snedeker 2013, 502 verbs, 7 Levin
   classes; Ferstl 305 verbs): a per-verb NP1-vs-NP2 causal-bias score, VerbNet/Levin back-off. Zero-LLM, highest
   tractability; needs an adaptation layer from pronoun-antecedent bias to clause-to-clause plausibility. (BUILT here
   as the deepened engine via hdlab.psych_verb_frames SUBJ_EXP/OBJ_EXP; did not raise c -- fires on few pairs.)
2. **Causal-KG priors** -- CauseNet (11M web edges, 83% precision; 198K curated), ConceptNet Causes, ATOMIC-2020
   (1.33M), GLUCOSE (440K story-grounded causal generalizations on ROCStories). Lookup-shaped A->B typicality priors at
   far larger scale than hand-built heuristics. (NOTE: the causal reasoner already showed generic CSKG retrieval is
   coverage-bounded at 17.3%; GLUCOSE is story-grounded but crowd/LLM-derived + ROCStories-specific -> admissibility +
   acquisition caveats.)
3. **Valence-congruence** (NRC-VAD/ANEW sign-match) -- cheap, N400-backed, modest. (BUILT: appraisal engine.)
4. **Force dynamics** (Talmy 1988; Wolff 2007 vector model: tendency/concordance/endstate as a 3-input CAUSE/ENABLE/
   PREVENT table) -- the decision rule is trivial; the 3 feature-extractors must be built off shallow text. (BUILT:
   FrameNet force typer via hdlab.force_dynamics_typer.)
5. **Counterfactual/necessity simulation** (Gerstenberg 2021 CSM) -- psychologically dominant, but needs an existing
   causal-edge library (circular with #2); least turnkey.

## 4. The named wall
There is NO evidence coherence-relation inference is theoretically impossible without an LLM -- SDRT/DICE is pinned and
Hobbs abduction has a working (narrow-domain) implementation history. **The wall is COVERAGE, not theory:**
(a) causal relations are a statistical MINORITY of adjacent-sentence relations (newswire ~4-11% of RST relations,
47.7% VAGUE; narrative ~15-30%); most of what must be resolved is Expansion/Elaboration/Joint, which the causal engine
is not designed to touch; (b) newswire non-chronological structure is mostly genre convention (Zhang-Xue ~54%
OVERLAP), not causal-Explanation -- so improving causal plausibility will NOT move the newswire needle; (c) the field's
own non-LLM implicit-relation ceiling is ~40-45% multiclass, well below dense-embedding scale -- the brain's advantage
is a much larger, continuously-updated associative knowledge base (Kintsch CI net) + situational/perceptual grounding
that no offline symbolic lexicon fully replicates. **Practical steer:** scale class-level heuristics to CauseNet/
GLUCOSE-scale priors rather than deepening class-level engines; and do NOT expect the newswire reverse-order signal to
be a strong eval target for a causal-plausibility engine.

Research confidence: P_deflated ~0.6 (the coverage-wall claim, well-supported by multiple corpus statistics) /
~0.75 (the mechanism-is-PINNED sub-claim).
