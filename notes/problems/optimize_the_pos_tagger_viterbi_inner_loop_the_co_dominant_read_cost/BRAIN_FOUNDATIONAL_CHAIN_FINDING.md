# Brain-foundational chain around the POS tagger — mechanism-diff, the wall, and what the speed enables

**Context.** The assigned problem is a BYTE-IDENTICAL speed optimization (done; witnessed 5.25x, tags
unchanged). Per the owner's standing directive — *"the only way you overcome the wall is for EVERY
component, you and upstream, to be brain-foundational"* — this documents the brain-foundational chain
around the tagger: what is faithful, where we lose signal, and what the speed win ENABLES. It BUILDS
ON the immediately-preceding arc-parser finding (which localized the wall to lexical-semantic
grounding); it does not re-derive it. Glass-box, CPU, NO LLM. Research this session via `hdi_research`
(citations inline). Files: `experiments/exp_pos_tagger_brain_foundational_chain_v1.py`; metrics
`data/exp_pos_tagger_brain_foundational_chain_v1/metrics.json`.

## 1. Mechanism-diff — PINNED vs OUR-INVENTION (checklist items 1, 5, 6)
How the brain assigns lexical category, and how faithfully we replicate each part:

| brain mechanism (structure/computation) | our implementation | fidelity |
|---|---|---|
| **Bottom-up cue integration** — graded classification from word-form + affix + word-shape + neighbouring-word cues, learned by **error-driven, cue-competition** association (Rescorla–Wagner / delta rule) | structured **averaged perceptron**; features = exactly those cues; **Collins-2002 update IS in the Widrow–Hoff/delta-rule family = the Rescorla–Wagner family** | **PINNED — faithful.** A generative P(word\|tag) counter REGRESSES (my prior result) because it double-counts correlated cues (naive independence, no cue competition). [MacDonald 1994; Ramscar 2010; Baayen 2011] |
| **Ranked-parallel graded activation** — multiple candidate categories held in parallel as a *distribution*, resolved incrementally | single global **1-best Viterbi** — collapses to one path, discards the distribution | **OUR-INVENTION gap.** Surprisal/constraint-satisfaction REQUIRE a distribution over analyses. [Levy 2008; MacDonald 1994] |
| **Top-down feedback** — syntactic/semantic context re-ranks candidates (frontal→temporal) | none — emission+transition only, feed-forward | **OUR-INVENTION gap** (semantic feedback PINNED; category-specific *syntactic* feedback is inferred from constraint models). [Lau 2008; Lyu 2023; Kuperberg-Jaeger 2016] |
| **Forward prediction** — pre-activate the likely next category | none | **gap, magnitude CONTESTED** (Federmeier 2007 / DeLong 2005 tempered by Nieuwland 2018 — do not over-claim). |

**The speed optimization changes NONE of this** — it is byte-identical, so the faithful bottom-up
model is preserved exactly and the gaps are unchanged. Speed is hygiene; the fidelity content is the
decode, addressed below.

## 2. WHERE WE LOSE SIGNAL — the wall is MEANING, measured fresh (checklist item 6)
UD-EWT test, gold UPOS, n=24,120 tokens / 2,061 sentences (tagger byte-identical, acc 0.9443):

- **85.1% of all errors (1144/1344) touch a CONTENT class** (NOUN/VERB/ADJ/ADV/PROPN); only **14.9%
  are purely among function classes.** The tagger has essentially SOLVED function words; its residual
  errors are content-word category calls.
- **The single biggest error bucket is PROPN↔NOUN: 380 errors (203 PROPN→NOUN + 177 NOUN→PROPN) = 28%
  of ALL errors.** Proper-name vs common-noun is a *referential/world-knowledge* decision ("Green" the
  surname vs the colour; "Baker" the name vs the trade) — surface form cannot settle it.
- **OOV acc 0.8339 vs known 0.9558** (OOV = 9.5% of tokens): the drop concentrates where morphology
  runs out and meaning is needed.
- All top confusions (VERB↔NOUN, ADJ↔NOUN, ADJ↔VERB, NOUN↔ADJ) are content-word and meaning-dependent.

**This is the SAME wall the arc-parser finding localized and the reader's WSD/consolidation work hit:
lexical-SEMANTIC grounding.** It is independently confirmed by the mechanism literature — the human
advantage on ambiguous/OOV category assignment is selectional/world-knowledge-driven (Altmann-Kamide
1999 anticipatory eye-movements from verb selectional restrictions; Trueswell 1994 thematic fit
resolves category ambiguity). Making the *decode algorithm* more brain-foundational does not close a
meaning gap; SUPPLYING MEANING does.

## 3. WHAT THE SPEED ENABLES — the honest speed↔fidelity connection (the genuinely new point)
The brain keeps a GRADED ranked-parallel activation, not a hard 1-best. The exact graded signal is the
**forward–backward marginal posterior** P(tag_i | sentence) over the same lattice (the perceptron
scores are the CRF's log-potentials — this is exactly what the calibrated CRF-posterior organ **P7,
`hdlab/crf_tagger.py`**, represents). It is strictly MORE brain-foundational than the hard 1-best but
costs a second DP pass.

Measured (400 UD-EWT sentences): the enriched decode (Viterbi 1-best **byte-identical**, mismatch=0,
PLUS the full FB posterior) runs in **0.632s vs the stock hard-1-best 1.099s — WITHIN budget, indeed
1.74x FASTER than the current output.** So the ~5x byte-identical speed headroom does not just save
time: **it makes a strictly-more-brain-foundational graded decode affordable — cheaper than the hard
1-best we ship today.**

**HONEST CAVEAT (no over-claim):** mechanism-fidelity ≠ accuracy. Mean top-1 posterior mass is 0.992 —
the perceptron is usually confident; the graded candidates convert to accuracy only once **top-down
MEANING (grounding)** re-ranks them, and the prior joint tag↔parse loop REGRESSED without it. So the
speed win ENABLES the brain-foundational decode; **grounding CASHES it.** The chain is:
`faithful bottom-up cues (have it) → graded ranked-parallel decode (now affordable) → top-down meaning
re-ranking (the wall) → competent-reader category assignment`.

## 4. ADJACENT COMPONENTS — consumers to revisit for brain-fidelity (checklist item 7; owner's 3rd ask)
Every downstream consumer collapses the tagger to a HARD 1-best category and gates on it, with NO
uncertainty — the opposite of the brain's graded parallel activation:
- `consequence_learning_loop.py:138` — `[t == "VERB" for t in tag(...)]` (hard VERB gate)
- `referent_per_np.py:119` — NP detection off hard NOUN/PROPN (**the PROPN↔NOUN error, 28% of tagger
  errors, propagates straight into entity/coref here**)
- `predicate_detector.py`, `completeness_checker.py`, `candidate_generator.py`,
  `reading_grounding_loop.py`, `situation_reader` events — all hard categorical gates.

**Brain-foundational upgrade (a FAMILY of follow-on problems, verdict-independent):** with the tagger
fast and the FB/CRF posterior now affordable per read, these consumers can consume the GRADED posterior
(uncertainty-aware, ranked-parallel) instead of a hard 1-best — e.g. entity detection weighting NP
candidates by P(PROPN)+P(NOUN) rather than an all-or-nothing tag. That is a strictly more
brain-foundational interface AND it directly attacks the dominant PROPN↔NOUN error. Highest-leverage
first consumer: `referent_per_np` (entity/coref). This is NOT this problem — it is the adjacent map.

## 5. What I would withdraw first if wrong
The forward-prediction fidelity claim (weakest — Nieuwland 2018 tempers prediction magnitude). If
wrong, the two load-bearing claims stand: (a) the perceptron bottom-up model is brain-faithful
(delta-rule = Rescorla–Wagner), so the byte-identical speed win preserves fidelity; (b) the wall is
meaning (85% content-word errors, PROPN↔NOUN dominant), decode changes don't close it, grounding does.
