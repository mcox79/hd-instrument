# UPSTREAM BRAIN-FOUNDATIONAL AUDIT (operation/math precision) -- the rung-2 situation-sim chain

Owner asked: "have you verified, at great precision, that ALL upstream components are 100% brain-foundational, down to
the specific operations and math?" HONEST ANSWER: NO -- and a precise audit shows SEVERAL upstream components are NOT
brain-foundational at the operation level. Per the owner's standing principle (a brain-foundational component that
fails is starved by a non-brain-foundational UPSTREAM one), this is very likely WHY the rung-2 more/less SIGN is stuck
at/below chance while the necessity/reachability piece (which leans less on the broken upstream) improved (0.703).

Legend: BF = 100% brain-foundational operation; BF-SPIRIT = defensible computational-level model, engineering impl;
NOT-BF = the specific operation/math is not the brain's.

| # | component | exact operation / math | verdict | why |
|---|---|---|---|---|
| 1 | tokenizer (`_TOKRE`) | regex `[A-Za-z]+|[0-9]+|...` split | NOT-BF (low-impact) | mechanical; brain segments via learned units |
| 2 | POS tagger (`hdlab.pos_tagger`) | **averaged structured perceptron** (Collins 2002) w·φ + **Viterbi**; trained once, **FROZEN** | NOT-BF | averaging = a training-time variance trick (not neural); FROZEN (brain learns continuously); SEPARATE from parse (brain LINKS category+syntax, MacDonald 1994) -- 2 audit-documented deviations |
| 3 | arc parser (`hdlab.arc_parser`) | **hashed arc-factored** averaged perceptron, **GREEDY hard-decode** (+cycle-break); exact MAP/Matrix-Tree marginals exist but unused | NOT-BF | arc-factored batch MST != the brain's INCREMENTAL, surprisal-driven, interactive-activation parse; hard-MAP discards the marginals; audit north-star = ONE unified continuously-learning interactive cell. A more-BF `hdlab.incremental_parser` EXISTS but is not used here |
| 4 | lemmatizer (`_lemma`, WordNet morphy) | rule-based suffix strip + WordNet exception lookup | BF-SPIRIT | WordNet = admissible static foundation; form->concept mapping is BF in spirit (ATL codes the concept), impl is rule-based |
| 5 | **`span_concepts` (the concept grain)** | collect VERB+NOUN lemmas into a **SET (bag)**, stopword-filtered | **NOT-BF (load-bearing)** | my OWN research (6 converged literatures; Frankland-Greene lmSTC role-binding) says the brain-faithful unit is a BOUND participant-attribute-VALUE structure, NOT a bag -- a bag DISCARDS the role binding. Explicit grain deviation |
| 6 | `bf_roles` (frame extractor) | root verb = min head==0 VERBAL; AGENT = nearest-preceding nominal dep; PATIENT = nearest-following | NOT-fully-BF | shallow POSITIONAL nearest-nominal proxy over the (non-BF) parse; the brain uses graded competition (MacWhinney) -- a more-BF `graded_role_assigner` exists but bf_roles uses the proxy |
| 7 | **causal store score (`cs_pmi` / signed markers)** | PMI = log(p(c,e)/p_c p_e); sign from PREVENT-class **regex** | **NOT-BF (load-bearing)** | PMI is rung-1 ASSOCIATION (Causal Hierarchy Theorem: can't determine the causal answer); marker-class regex polarity != the brain's force-dynamic computation (Wolff). This is the SIGN's upstream, and it is association+heuristic |
| 8 | situation model (`build_situation_model`) | use WIQA's GIVEN step order (RESULTS_IN) + per-step bf_roles frame | NOT-fully-BF | the step ORDER is a DATA ARTIFACT (provided), not CONSTRUCTED by a brain mechanism (van den Broek online construction); frames inherit the non-BF parse |
| 9 | **magnitude/polarity (`_INC`/`_DEC`)** | count words from a **hand-curated list** | **NOT-BF (load-bearing for SIGN)** | hand-listed lexicon lookup, not a grounded magnitude/valence representation (Lancaster sensorimotor / learned). The more/less SIGN rides on THIS -- and the sign is at/below chance |
| 10 | signed propagation | product of ±1 link signs along the chain | BF-SPIRIT (simplified) | Wolff force-composition in spirit; ±1 product is a simplification of graded signed propagation |

## SYNTHESIS -- why the SIGN fails (the owner's principle, confirmed)
The rung-2 SIMULATION is BF in FORM (Pearl do + Hesslow difference + counterfactual necessity). But the three components
that FEED THE SIGN are all NOT-BF: (7) the causal store's sign is association-PMI + a regex marker, (9) the magnitude
polarity is a hand-list, (5) the concepts are a bag (no bound state to carry a signed attribute). So the more/less sign
is computed from non-brain-foundational inputs -> it is noise (0.34-0.41, at/below chance). The NECESSITY/reachability
piece improved (0.703) precisely because it depends LESS on these (it needs only "is there a causal path", which the
step-chain + coarse concepts can partly supply) -- but even it is capped by the bag grain + frozen parse.

## WHAT A 100%-BF UPSTREAM CHAIN REQUIRES (the real dependency list, each an own program)
- **Concept grain (5,6):** bag -> BOUND participant-attribute-VALUE frames (the frame/state-grain re-mine; `graded_role_assigner` for roles). 
- **Causal store (7):** PMI/regex-sign -> the brain's force-dynamic causal representation computed properly (Wolff CAUSE/ENABLE/PREVENT), NOT association. (And per CHT, even this is rung-1 -- the true sign must come from the SIMULATION over a grounded model, not the text statistic.)
- **Magnitude/polarity (9):** hand-lists -> a GROUNDED magnitude/valence (Lancaster sensorimotor norms / a learned scalar) -- the substrate's grounding program.
- **Parse (2,3):** frozen separate perceptron + hard-MAP -> the unified continuously-learning interactive-activation parse (`incremental_parser` / the pri-1 north-star), keeping the marginals (graded), not hard-decoding.
- **Situation model (8):** given-order -> ONLINE construction from the text (van den Broek landscape).

=> The rung-2 unlock is not just the simulation; it needs a brain-foundational upstream chain, and several links (grounded
magnitude, interactive continuously-learning parse, bound-state grain) are THEMSELVES open north-star programs. The
honest implication: this problem's frontier is a MULTI-ORGAN brain-foundational rebuild, correctly scoped as several
linked problems, not a single cell -- exactly the owner's principle that a failing BF component means a non-BF upstream.
