# Brain-check drill: selectional-preference coreference — glass-box blueprint

Date: 2026-07-18
Type: biology-led brain-check drill (research/scoping only; NO cell dispatch, NO push)
Trigger gap: VET afd3df89 (Track A v3) — reader coref (overlay maintained-salience) FAILS
"It has a nest" -> resolves "it" to nearer/equal-frequency "tree" instead of "bird".
Maintained-salience cannot break an equal-recency/equal-frequency tie; the brain breaks it
with WORLD KNOWLEDGE (a nest is possessed by a BIRD, not a TREE = SELECTIONAL PREFERENCE on
the possession predicate). We HAVE dictionary grounding (bird=animal, nest=structure birds
build) that could supply this cue but the coref does not use it.

Substrate concept-query pre-check: `substrate_query.sh "pronoun coreference selectional
preference world knowledge resolution"` -> top hits are dictionary-grounding atoms only
(entity 'reference'/'coreference'/'preference' from WordNet/FrameNet, cosine ~0.43). Prior
ARC work on selectional-preference coref: NONE. This is new territory over existing grounding.

---

## (a) BIOLOGY — how the brain folds world knowledge into pronoun resolution as ONE weighted cue

The convergent psycholinguistic finding (lead with biology): pronoun/anaphor resolution is
NOT a lookup on a single feature. It is **constraint-based, weighted competition** — many
soft cues combine in parallel and the strongest coalition wins. World knowledge / selectional
preference is one of those cues, and it is exactly the cue that breaks ties recency and
salience cannot.

The cues the brain integrates (each credited):
- **Morphosyntactic AGREEMENT** (gender, number, person) — near-hard filter; violations are
  fast and strong.
- **SALIENCE / TOPICALITY** — Centering Theory (Grosz, Joshi & Weinstein 1995): the backward-
  looking center / most salient discourse entity is the preferred antecedent; subject-of-
  preceding-sentence and first-mention biases (Hobbs 1978 counted this in corpora).
- **RECENCY** — recency of last mention raises accessibility.
- **IMPLICIT CAUSALITY** — Garvey & Caramazza (1974): interpersonal verbs carry a stored
  causal bias (NP1- vs NP2-biased, e.g. "amaze" NP1 vs "love"/"blame" NP2) that predicts the
  re-mentioned referent; can outrank other constraints (Kehler et al. 2008 recast this as
  coherence-driven).
- **SELECTIONAL PREFERENCE / PLAUSIBILITY (our gap)** — the predicate/verb constrains which
  argument class is plausible. McRae, Ferretti, Hare & Elman (thematic fit / generalized event
  knowledge): verbs and their arguments rapidly activate "typical agent/patient" event
  knowledge (arrest -> cop/thief); thematic fit is computed from the real-world event, not the
  verb alone. Trueswell & Tanenhaus: constraint-based comprehension integrates plausibility
  online.

**How they combine = the integration law.** MacWhinney & Bates **Competition Model**: cues
have weights (validity x availability) and compete additively; the resolved interpretation is
the argmax of the weighted cue coalition. Kehler et al. (2008) give a Bayesian version
(P(antecedent | pronoun) ∝ prior topicality x coherence-driven likelihood). Both say the SAME
operational thing for our purpose: **selectional preference is a co-equal weighted term, and
when recency/salience TIE (weights cancel), the selectional term is decisive.** That is
precisely the bird/nest case.

**Timing — is it immediate or a late repair?** Immediate and automatic, not a late patch.
ERP evidence: Hagoort et al. (2004) — world-knowledge violations elicit an N400 in the SAME
time window as lexical-semantic anomalies (world knowledge integrates as fast as word meaning).
McRae et al.: thematic-fit / typical-role-filler effects appear immediately in eye-movements.
Implication for us: selectional preference should be a **first-class cue inside the resolve
step**, not a post-hoc re-ranking filter bolted on after a salience decision.

**Brain caveat (do not assume the brain-check outcome).** The brain ALSO makes confident wrong
guesses under "good-enough" processing, and its integration is graded/probabilistic. On CLEAN
selectional cases (nest -> bird), a substrate with EXACT grounded lookup could *beat* the
brain's noisy graded competition, not merely match it (Frontier-2, substrate-native). So the
brain gives us the ARCHITECTURE (weighted multi-cue competition with selectional as one term),
not necessarily the CEILING.

---

## (b) CHEAP GLASS-BOX MECHANISM over the EXISTING dictionary/foundation grounding

Claim to test, not assert: the selectional cue for "what HAS a nest?" can be a **table lookup +
is-a subsumption check** over grounding we already hold — no external LLM, fully inspectable.

The mechanism, step by step, for "The bird sat in the tree. It has a nest.":

1. **Predicate extraction** (parser's job): parse the clause into a predicate with a pronoun
   slot: `HAS(possessor = it, possessed = nest)`. The pronoun fills the possessor slot of a
   possession relation whose object is "nest".

2. **Retrieve the slot's selectional-preference class** from grounding. For the possessed noun
   `nest`, look up its stored relations/gloss in the foundation:
   `nest --built_by / made_by / inhabited_by--> bird` and `bird is-a animal`. The typical
   possessor of a nest is therefore the class {bird / animal}. This is a **stored association**
   (Resnik-style, see prior art) already latent in the dictionary grounding ("nest = structure
   birds build"): the predicate slot's preferred filler class = the subject class of the
   relation that DEFINES the possessed object.

3. **Score each candidate antecedent by selectional fit.** For each candidate (bird, tree),
   walk its is-a chain and test intersection with the slot's preference class:
   - `bird is-a animal` ∩ {bird/animal} -> HIT -> high selectional score.
   - `tree is-a plant` ∩ {bird/animal} -> MISS (plant does not have/build a nest) -> ~0.
   The check is a bounded is-a subsumption test + set intersection: cheap, deterministic,
   glass-box (you can print exactly which is-a edge fired).

4. **Feed the score as one weighted term** into the resolve (section c).

Why this is cheap and honest: it is O(candidates x is-a-depth) lookups over a table we already
have. It is Resnik's information-theoretic selectional-preference idea (typical filler class
over a WordNet-style is-a hierarchy) reduced to a subsumption test, because our foundation
already carries the is-a + part-of/has relations. **The load-bearing assumption to VET is
COVERAGE**: does the grounding actually encode "typical possessor of nest = bird"? is-a is
dense; the possession/build relation (nest -> bird) may be sparse. This is an extraction/
coverage question, NOT solved by assuming (honest gap, section e).

---

## (c) PLUG-IN — the overlay's multi-cue resolve

Replace the single maintained-salience argmax with a **weighted competition** (Competition
Model / Kehler-Bayesian), keeping every weight inspectable:

```
resolve(pronoun) = argmax over candidates c of:
      AGREEMENT(c)                       # HARD gate: number/gender mismatch -> disqualify
    * ( w_sal * salience(c)              # existing maintained-salience overlay term
      + w_rec * recency(c)               # existing
      + w_sel * selectional_fit(c)       # NEW term from (b)
      + w_ic  * implicit_causality(c) )  # optional later, if verb carries IC bias
```

- AGREEMENT stays a hard filter (fast/strong in biology).
- The soft cues sum with weights; **when w_sal*salience and w_rec*recency TIE across candidates
  (the exact failure), the w_sel*selectional_fit term decides** -> bird wins.
- Weights are glass-box constants initially (report which cue fired for each resolution);
  optionally tuned on a held-out set of minimal pairs LATER (never learned black-box; keep the
  contribution of each cue printable).
- Selectional is placed INSIDE the resolve (co-equal, per the immediate-integration timing),
  not as a downstream re-rank.

---

## (d) FAIR-TEST DESIGN — Winograd-style minimal pairs (isolate selectional from recency/freq)

The Winograd Schema Challenge (Levesque, Davis & Morgenstern) is exactly "pronoun resolution
that requires world knowledge": a pair of sentences differing in ONE word, flipping the correct
antecedent, with recency/salience/frequency held constant. Use that structure to avoid the
confound that sank the naive test.

Minimal-pair template (the possessed object / predicate is the ONLY thing that varies):
- S1: "The bird sat in the tree. It has a nest."   -> correct: **bird** (nest selects animal)
- S2: "The bird sat in the tree. It has deep roots." -> correct: **tree** (roots select plant)

Both antecedents have equal recency and comparable salience/frequency; ONLY the predicate's
selectional preference flips the answer. A resolver that ignores selectional preference scores
at chance across the pair; a resolver that uses it flips correctly with the predicate.

Required controls (per design-gate discipline — discriminator must be able to fail, real
baseline, difficulty ON, one variable):
- **Neutral-predicate control** ("It is large." / "It is there.") — no selectional cue -> must
  fall back to salience-default, NOT spuriously invoke selectional. Confirms the cue, not a
  leak, is doing the work.
- **Baseline = the current maintained-salience resolver** (real, not strawman); it should score
  ~chance / salience-default on the flipping pairs. If it already passes, the test is confounded.
- **Balance the correct answer** across near/far and subject/object so recency/first-mention
  cannot be gamed to the right answer.
- **Coverage split**: report separately (i) pairs whose selectional relation IS in the
  grounding vs (ii) pairs where it is NOT — so a pass is not inflated by cherry-picked coverage.
  Hold out a clean slice.

Fairness note: the general WSC is HARD and often needs multi-step reasoning; we are testing the
**selectional-preference-solvable subset** (single stored has/is-a relation disambiguates).
Scope the claim to that subset explicitly.

---

## (e) HONEST GAPS (do not over-claim)

1. **Coverage is the real bottleneck, unproven.** is-a grounding is dense; the possession/build
   relation ("typical possessor of nest = bird") may be sparse or absent. If the relation is not
   in the foundation, there is no cue and we fall back to salience. Coverage over a realistic
   predicate set is an empirical question — measure it, do not assume.
2. **Predicate extraction depends on the parser.** The mechanism needs "It has a nest" parsed
   into HAS(it, nest). If the (hand-rules or learned) parser is the wall, the selectional cue
   cannot be applied — this drill assumes a slot the parser must actually deliver.
3. **General WSC is not glass-box-cheap.** Many Winograd items need chained/causal reasoning,
   not one selectional lookup. Target = the selectional-solvable slice (real but bounded); the
   general challenge is out of scope for a single lookup.
4. **Weight calibration risk.** w_sel too high overrides correct salience-driven cases (over-
   application); too low re-creates the tie failure. Needs calibration on held-out minimal
   pairs; the competition must be tuned, not hand-waved.
5. **Selectional preference can be wrong / graded in the world** (a squirrel also uses a nest;
   "nest" metaphors). Exact is-a lookup gives a crisp answer where reality is graded — good on
   clean cases, brittle on edge cases. Report the confidence, allow abstain.
6. **Brain-check is architecture, not ceiling.** Biology says weighted multi-cue competition
   with selectional as an immediate co-equal term. It does NOT say graded probabilistic
   competition is optimal — on clean cases an exact grounded lookup may beat the brain
   (Frontier-2). Keep both the brain-faithful competition AND the native exact-lookup on the
   table; nail the brain-faithful baseline first.

---

## PRIOR ART (learn-from + build-on + credit; borrowed vs new stated honestly)

Biology / psycholinguistics (the architecture + cues):
- Garvey & Caramazza (1974) — implicit causality verbs; NP1/NP2 bias.
- McRae, Ferretti, Hare, Elman (thematic fit / generalized event knowledge; McRae et al. 2005)
  — verbs activate typical argument classes immediately.
- Trueswell & Tanenhaus — constraint-based sentence comprehension (plausibility integrated
  online).
- Grosz, Joshi & Weinstein (1995) — Centering Theory (salience/topicality).
- MacWhinney & Bates — Competition Model (weighted additive cue integration = the integration
  law we adopt).
- Kehler, Kertz, Rohde & Elman (2008) — Bayesian, coherence-driven pronoun interpretation.
- Hagoort et al. (2004) — world-knowledge N400 (immediate integration, timing).

Engineering / glass-box prior art (the mechanism):
- Hobbs (1978) naive syntactic algorithm; Hobbs et al. (1993) "Interpretation as Abduction"
  (world knowledge in resolution).
- Levesque, Davis & Morgenstern — Winograd Schema Challenge (the fair-test framing).
- **Resnik (1996) — information-theoretic selectional preferences over WordNet is-a hierarchy**
  = the DIRECT ancestor of our mechanism (typical filler class over is-a); we reduce it to a
  subsumption test because our grounding already carries the hierarchy.
- Erk (2007) — distributional selectional preferences.
- Rahman & Ng; Peng, Khashabi & Roth "Solving Hard Coreference Problems" — knowledge + features
  for hard/Winograd coref (transparent, non-LLM).
- ASP / answer-set commonsense approaches to WSC — fully symbolic, glass-box injection of world
  knowledge.

What is BORROWED: the weighted-competition integration law (Competition Model/Kehler); the
selectional-preference-over-is-a idea (Resnik); the minimal-pair fair test (Winograd).
What is NEW here: reducing selectional preference to a cheap subsumption test over the
foundation's EXISTING is-a + has/part-of grounding, and slotting it as an immediate co-equal
term into the overlay's maintained-salience resolve to break the exact equal-recency tie.

## Sources
- https://www.psychology.uwo.ca/pdfs/SONA/articles/3-mcrae.pdf (McRae et al. 2005, thematic fit)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC3375826/ (generalized event knowledge, online comprehension)
- https://link.springer.com/article/10.1007/BF02139085 (Garvey & Caramazza, grammatical determinants / implicit causality)
- https://www.frontiersin.org/journals/communication/articles/10.3389/fcomm.2018.00053/full (implicit causality + discourse context in pronoun resolution)
- https://cdn.aaai.org/ocs/4492/4492-21843-1-PB.pdf (Levesque, Winograd Schema Challenge)
- https://cs.nyu.edu/~davise/papers/WinogradSchemas/WS.html (Davis, Winograd Schema Challenge)
- https://arxiv.org/pdf/1907.05524 (Peng/Roth, Solving Hard Coreference Problems)
- https://arxiv.org/pdf/1907.11112 (ASP commonsense reasoning for WSC)
- https://www.sciencedirect.com/science/article/abs/pii/S0926641005002259 (world knowledge N400 / immediate integration, Hagoort-line)
- https://arxiv.org/pdf/1707.05967 (thematic fit with distributional feature overlap; Resnik-lineage selectional preference)
