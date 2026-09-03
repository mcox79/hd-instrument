# BRAIN MECHANISM DRILL — register-robust event/predicate detection

Dispatched research drill (2026-09-03), synthesized here as the design foundation. Marks PINNED-BY-EVIDENCE vs SPECULATIVE.
This is the brain-foundational basis for the solver's build; it is not a substitute for the on-disk measurements.

## HEADLINE
The brain never assigns predicate-hood as a static per-lexeme tag. It runs continuous, multi-cue probabilistic
constraint integration (frame/closed-class scaffolding + morphology + dependency attachment + verb-frequency prior)
that settles by COMPETITION, not a serial category-then-structure pipeline — and that same architecture is what keeps
frame-based induction from over-generating. The parent's modern-generalization wall is **mostly an implementation
artifact** (a single-cue, hard-AND/OR, structure-only override that discarded load-bearing signal), with a smaller
**genuine residual ceiling** for the hardest confident-but-wrong modern mis-tags that lack any local giveaway and would
need semantic/discourse support even in a human.

## 1. Predictive predicate-slot detection — PINNED
Prediction in comprehension is probabilistic pre-activation across multiple grains simultaneously (Kuperberg & Jaeger
2016), not one lexical guess. Verb argument structure drives anticipatory reference before the noun (Altmann & Kamide
1999). Closed-class scaffolding + agreement pre-activate the category of the upcoming open-class item (Wicha/Moreno/
Kutas; Van Berkum). The syntax-first serial ELAN model is **overturned**: forcing nouns into verb slots yields NO ELAN,
instead N400+late-P600 — syntax and semantics combine additively (Fromont, Steinhauer & Royle 2020), supporting the
constraint-based-lexicalist account (MacDonald, Pearlmutter & Seidenberg 1994): category and structure settle JOINTLY.

## 2. Zero-derivation / category override — PINNED: graded competition
Noun/verb homographs keep the dominant reading partially active even when context forces the other (Lee & Federmeier
2009). "Delayed commitment" is explained by three continuous constraints — usage freq, cooccurrence freq, combinatorial
semantics (MacDonald 1993); categories are attractor basins, resolution is graded settling not symbolic flipping
(Tabor/Juliano/Tanenhaus 1997). Override lands mid-latency (N400→P600), not instantaneous, not binary.

## 3. Register / novel-form invariance + the over-generation puzzle — PINNED
Jabberwocky: the language network fires at ~52% of real-sentence magnitude on structured nonsense — structure-building
is content-independent (Fedorenko lab; Friederici BA44/dorsal pathway). 2-year-olds slot invented verbs ("stipe",
"nerk") from frame alone, no scene needed (Yuan/Fisher/Kandhadai/Fernald 2011) — predicate-hood is SLOT-based,
form-independent, TRANSFERS. **The over-generation fix:** Mintz frequent frames reach .90–.95 accuracy but only
.047–.057 coverage — precise-but-SPARSE (Mintz 2003; PMC2724313). Stripping the anchor's identity to a bare category
collapses accuracy .90→.25. Precision is a COMBINATION, never a single threshold: (i) anchor specificity, (ii)
morphological/phonological compensation for what frames miss (Monaghan/Chater/Christiansen 2005 PDCH), (iii)
frequency-weighted COMPETITION enforcing one-predicate-per-clause (Spivey-Knowlton/Trueswell/Tanenhaus 1993). This is
the direct explanation for the in-house 3.7 false-verbs/sentence: one weak cue (linear content-word-between-args), no
anchor specificity, no morphological gate, no competitive suppression.

## 4. Self-supervised acquisition — PINNED framework
Pure co-occurrence clustering recovers syntactic categories with no labels/semantics (Redington/Chater/Finch 1998). A
Bayesian ideal learner PREFERS hierarchical/structural grammars from ordinary input — abstractness is the rational
inference (Perfors/Tenenbaum/Regier 2011). The learned representation is abstract/slot-based (transfers), resolved
toward transferable structure by the novel-verb result (§3).

## 5/6. Faithful model + wall diagnosis — MIXED (most of the gap is implementation)
Noisy-channel comprehension (Gibson/Bergen/Piantadosi 2013; Levy 2008) = combine a per-word LIKELIHOOD (bottom-up
lexical evidence = a tagger's soft margin) with a structural/semantic PRIOR. Joint POS+dependency parsing cuts exactly
the NN<->VB confusion class (Bohnet & Nivre 2012); joint/soft tagging-parsing beats hard-tag-then-parse pipelines
(Yang 2017; He 2020) — corroborating the brain-level rejection of serial commitment at the computational level.
**Genuine partial ceiling:** good-enough processing leaves a confident initial misanalysis lingering even after
reanalysis (Christianson et al. 2001); implausible-but-grammatical cases need semantic signal, not structure (Kim &
Osterhout 2005). So the hardest confident+structurally-clean modern mis-tags plausibly fail for a human too — that
slice needs semantic/discourse support (a bigger build). Historical-tagging degradation is ordinary domain-shift
magnitude (8–12pp) and is mostly SPELLING, not syntax (Rayson "Tagging the Bard"; Yang & Eisenstein 2016). Under
uncertainty, let weak cases stay AMBIGUOUS rather than force-wrong (set-valued prediction, Heid et al. 2024).
**Verdict: the wall is ~70% implementation artifact, ~30% genuine ceiling** (deflated estimate).

## REGISTER-INVARIANT FEATURE SET (the build spec)
USE, combined by a LEARNED combiner (logistic, glass-box), NOT hand AND/OR:
1. tagger's own verb-MARGIN (emission score VERB minus best non-VERB) — likelihood, never a hard cutoff (Gibson 2013).
2. dependency-attachment: subj/obj-like dependents / head-or-root under a force-VERB read (Bohnet & Nivre 2012).
3. closed-class / frequent-frame anchor match — sparse but precise (Mintz 2003).
4. morphological / agreement finiteness cue — compensates frame sparsity, carries novel/rare forms (Monaghan 2005).
5. verb-subcat freq / one-predicate-per-clause competition (Spivey-Knowlton 1993).
AVOID / down-weight: raw lexical-identity memorization (register-brittle by construction); period-specific
orthography; single-alt hard rules combining noisy cues (precision-collapsing); naive self-training (fails for taggers).

## THE DECISIVE TEST (the drill's proposed cheap experiment — adopted)
A tiny logistic combiner (<10 register-invariant features above) trained on modern auto-labels, re-score the existing
held-out failure sets (19c systematic mis-tags + the modern residual). Reuses hdlab/pos_tagger emission scores +
arceager parser + WordNet + morphology. NO new model, NO LLM.
- HARD-PASS (deflated P~=0.40): modern recovery >=+10pp AND 19c false-verb rate materially below 0.92/sentence ->
  the wall was substantially an implementation artifact.
- HARD-FAIL (deflated P~=0.30): modern recovery ~=16% (no gain over dependency-only) -> genuine local-signal ceiling,
  needs semantic/discourse escalation (a located negative, which the bar sanctions as a full pass).

## CROSS-CHECK
Converges with the same-day sibling drill `register_robust_predicate_id` (independently found MacDonald 1993/1994,
Osterhout & Mobley 1995, Bohnet & Nivre 2012) and `notes/research_thematic_role_parser_architecture_brain_foundational_2026-08-31.md`
(joint arc-eager + POS-emission fusion). Two independent lit-scans converging on "no static tag / joint decoding" is a
meaningful cross-check.
