# Research: how should the brain combine a distributional and a sensorimotor meaning channel?

Filed by: research sub-agent, 2026-08-23. Topic: `reader_meaning_channel` — is equal-weight
Borda rank-vote (current combination rule) defensible, or does the literature pin a better rule?

## HEADLINE

**No literature source pins a semantic-channel combination FORMULA anywhere — not for
reliability-weighting, not for the hub-and-spoke model.** Reliability-weighting (inverse-variance)
is rigorously proven, but only at the low-level SENSORY scale (Ernst & Banks 2002 and successors);
its extension to semantic/conceptual channels is a single un-tested THEORY paper (Martin 2016),
not a measured result. The hub-and-spoke model's attractor network has spoke-hub CONNECTIVITY
pinned by diffusion tractography, but spoke CONTRIBUTION WEIGHTS are emergent from backprop
training with no formula anywhere in the primary sources — genuinely free, as ORGAN_MAP B5
already states. What IS pinned, at the semantic level specifically, is the DIRECTION of
concreteness-dependent gating (dual coding + independent computational replications) — this is
more directly evidenced for THIS application than reliability-weighting is, even though
reliability-weighting is the more rigorously proven mechanism in general. Equal-weight Borda has
no brain support at all; it is the "no information available" default, not a positive hypothesis.

## Cheap decisive test

Re-score the existing held-out link-classification set (the one that gives equal-weight Borda its
current accuracy) under each candidate rule below, using the SAME items, SAME gold, SAME scorer.
No new corpus read needed — this is a re-weighting of two already-computed channel rankings per
item. Bucket results by concreteness tercile (using the Brysbaert norms already in the sensorimotor
asset) to test whether any gain concentrates where the mechanism predicts it should.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Rule under test: concreteness-gated blend (see ranked list below, rank 1).**

- HARD-PASS: link accuracy improves over equal-weight Borda by a CI-separated margin (report
  CI half-width; a >=3-point wins is the working bar) AND the gain concentrates in the
  high-concreteness tercile (>=2x the gain seen in the low-concreteness tercile). Both conditions
  required — a uniform gain across concreteness bins is not evidence for THIS mechanism, only for
  "reweighting helped for some other reason."
- HARD-FAIL: no CI-separated gain over equal-weight Borda, OR gain is uniform across concreteness
  bins, OR gain is concentrated in the WRONG bin (low-concreteness). Any of the three fails the
  specific mechanism, not just the arm. Per [[feedback-a-null-that-is-exactly-zero]] discipline,
  also print channel-agreement rate per bin before reading the verdict — if the two channels never
  disagree on the high-concreteness tercile, there is nothing for a smarter rule to fix there and a
  flat result is a reachability failure, not a refutation.

P_deflated for HARD-PASS on the concreteness-gated arm: **0.35** (raw estimate ~0.55-0.60 from
converging independent lines of evidence — dual coding, Wang et al. 2018's learned-gate asymmetry,
Hill & Korhonen 2014, and this project's own `exp_verb_event_salient_channel_v1`
`EVENT_SALIENT_CHANNEL_REAL` result — deflated 0.20-0.25 per the mandatory lit-scan penalty because
no study tests this EXACT unfitted read-time formulation). Capped well under 0.50 is not needed here
since the raw estimate itself sits in range, but the deflation is still applied per rule.

## Findings by question, mechanism first

**1. Cue integration / reliability weighting.** PINNED at the sensory scale: Ernst & Banks 2002
(*Nature* 415) — combined estimate is a weighted sum, weight_i = (1/variance_i) / sum_j(1/variance_j),
which produces a measurable precision gain (combined variance below either input alone). Confirmed
in vision-haptics (Ernst & Banks 2002), audio-vision (Alais & Burr 2004), and macaque heading
discrimination via population decoding (Fetsch, Pouget, DeAngelis & Angelaki 2011/2012, *Nat
Neurosci*). Breaks down under large cue conflict, resolved by a causal-inference layer over forced
fusion (Kording et al. 2007, *PLoS ONE*) — the brain infers whether the two cues share a cause
before fusing. **Extension to semantic/conceptual combination is UNPINNED**: Martin 2016 (*Frontiers
in Psychology*) explicitly imports this framework as a hypothesis for language processing and
states outright that "how weights are determined" for semantic cues is unresolved — no behavioral
or neural data confirm inverse-variance combination at the concept level. **Per-item reliability
estimation without gold labels is an open gap** — no semantic-domain study operationalizes it; the
closest hint is Jacobs 2002 showing reliability can in principle be learned from unsupervised
environmental statistics, not demonstrated for this problem.

**2. Hub-and-spoke model.** PINNED: the hub computes via ATTRACTOR-NETWORK settling over multiple
cycles (Rogers et al. 2004, *Psychological Review* 111), not a one-shot weighted sum; Chen, Lambon
Ralph & Rogers 2017 (*Nat Hum Behav*) extends this to a deep recurrent net whose hub-spoke
CONNECTIVITY TOPOLOGY is constrained by diffusion tractography — which spokes connect to the hub is
evidenced. **The weight VALUES are not** — they are emergent from backprop training with no formula
anywhere in the primary literature. This directly answers the user's question: the weighting is
genuinely free in the theory, confirming ORGAN_MAP B5's existing note. Concept-type-dependent
engagement is PINNED qualitatively (Binney, Hoffman & Lambon Ralph 2016, *Cerebral Cortex*: superior
ATL differentially engaged for social concepts via limbic connectivity) but no quantitative
combination rule is ever given, by either side of the graded-vs-uniform-hub debate.

**3. Distributional + sensorimotor fusion; concreteness gating.** PINNED complementarity: Bruni,
Tran & Baroni 2014 (*JAIR*) directly measure that a text+image model beats text-only and that the
visual channel "provides complementary semantic information" — not assumed, measured. Andrews,
Vigliocco & Vinson 2009 (*Psych Review*) and Roller & Schulte im Walde 2013 (EMNLP) both show joint
experiential+distributional models fit human data better than either source alone. Contested
counter-view: Louwerse's symbol-interdependency hypothesis argues perceptual structure is already
redundantly encoded in language statistics (unresolved vs. Barsalou-style grounding). **No fusion
method in this literature used rank/score fusion (RRF, Borda)** — all combination was vector-level
(concatenation, joint latent-variable, weighted Gram matrix, gated autoencoder). Best-performing
gating was concreteness-dependent and FITTED: Wang, Zhang & Zong 2018 (AAAI) learn per-item gates
under weak supervision and find the resulting linguistic:visual weight ratio is higher for abstract
words (3.714:1) than concrete words (2.975:1) — automatic downweighting of the sensorimotor channel
for abstract items, consistent with Paivio's dual-coding theory. Hill & Korhonen 2014 similarly find
concreteness governs optimal combination weight. **The weights in both were fitted/trained — no
study publishes a closed-form unfitted concreteness formula** — but concreteness itself (Brysbaert
norms) is available per-word with zero fitting to this task's gold, so a hand-set monotonic function
of it is a legitimate unfitted design even though its exact shape has no direct precedent.

**4. Word-class / POS gating.** PINNED: somatotopic motor cortex activation for action verbs (Hauk,
Johnsrude & Pulvermüller 2004, *Neuron*). **But POS itself is the wrong variable**: Vigliocco et al.
2006 and Moseley & Pulvermüller 2014 show the effect tracks a word's motor/sensory FEATURE CONTENT,
not its grammatical class — concrete nouns and concrete verbs both engage sensorimotor regions;
abstract items of either class do not. A gating rule keyed to raw POS is a confound for a gating
rule keyed to concreteness/feature content, which is the better-supported variable and subsumes the
verb-salience finding rather than sitting beside it.

## Cross-thread synthesis (this substrate's own prior work)

- `exp_meaning_lift_population_code_v1` (2026-08-16, `BUNDLING_SURVIVED_BUT_NO_MEANING_GAIN`) — a
  prior naive channel-bundling attempt on this substrate SURVIVED but added no meaning gain. This is
  a direct warning: equal-weight Borda risks the same fate unless the combination rule carries real
  information the naive bundle didn't (i.e., concreteness- or reliability-conditioning).
- `exp_verb_event_salient_channel_v1` (2026-08-17, `EVENT_SALIENT_CHANNEL_REAL`) — independent
  on-substrate confirmation that verbs/events carry a real, separable salience signal, consistent
  with (though the literature above reframes it as feature-content- not POS-driven).
- `exp_sensorimotor_channel_discrimination_v1` (2026-08-18,
  `SENSORIMOTOR_DISCRIMINATION__B_AT_OR_NEAR_CONSTANT_PROTOTYPE_FLOOR`) — matches the user's own
  report that the sensorimotor channel alone is weak (~1-in-3 wrong, AUC 0.70): real but thin signal,
  consistent with it being a CONTRIBUTOR rather than a stand-alone channel.
- `exp_rrf_fusion_cpu_v1` (2026-07-03, `HARD_PASS`) — reciprocal rank fusion already validated as
  effective on this substrate for a different retrieval-fusion task; relevant precedent for rank-
  fusion mechanics even though the cognitive-science literature above never tests RRF specifically.
- `exp_thematic_role_labeler_cue_integration_v1` (2026-08-04, `HARD_PASS`) — "cue integration"
  already succeeded on this substrate for a different combination problem (thematic roles); worth a
  follow-up read of its actual weighting rule before the next build cycle (not pulled this cycle —
  metrics.json lookup timed out against the ~26GB `data/` tree; a scoped `Read` on its known path
  next cycle would close this rather than a repeated blind `find`/`Glob`).
- `exp_grounding_multiattribute_fusion_v1` (2026-07-10, `MIDDLE_BAND_PARTIAL`) — earlier partial
  precedent for multi-attribute fusion in grounding; consistent with "naive fusion gets you partway,
  not all the way."

## Substrate-product implications

Equal-weight Borda is not wrong, but it is not brain-grounded either — no source in three
independent lit-scans supports equal weighting as a biological default. The single best-evidenced
next arm is a **concreteness-gated blend**: fixed a priori (unfitted) as a monotonic function of the
Brysbaert concreteness rating already sitting beside the Lancaster sensorimotor asset, requiring no
new data acquisition and no training against gold. If it clears the HARD-PASS bar above, it directly
fixes the "sensorimotor channel wrong 1 in 3" problem by making the channel's vote count only where
it is actually diagnostic (concrete items) and get out of the way where it is noise (abstract
items) — which is a different mechanism from "the channel is bad" and predicts the SAME raw
sensorimotor accuracy (~0.70 AUC) is compatible with a much better COMBINED result. If it HARD-FAILs
in the specific way described (uniform gain, or gain in the wrong bin), that rules out concreteness
as the gating variable and redirects toward reliability-based gating (rank 2) as the next test
rather than abandoning combination altogether.

## Ranked short list — combination-rule arms to test (all UNFITTED, all read-time-computable)

1. **Concreteness-gated linear blend** — `w_sensorimotor(word) = f(concreteness_rating(word))`,
   `f` a fixed monotonic map (e.g. linear rescale of the [1,5] Brysbaert scale to a [0.15, 0.75]
   blend weight, chosen a priori, never fit to this task's gold); `score = w*sensorimotor_rank +
   (1-w)*distributional_rank`. **Brain justification**: dual coding (Paivio) + hub-and-spoke's
   qualitative concept-type gradient (Binney, Hoffman & Lambon Ralph 2016) + two independent
   computational replications of the DIRECTION of the effect (Wang et al. 2018; Hill & Korhonen
   2014) all converge on concreteness as the gating variable, and concreteness is available with
   zero fitting. Ranked first because it is the only candidate with semantic-level (not just
   sensory-level) empirical support for the DIRECTION of the rule.

2. **Reliability/inverse-variance blend** — `reliability_sensorimotor(word)` estimated as
   `1/variance` across the 11 Lancaster rating dimensions for that word (a tight cross-modal
   cluster = confident signal; a flat/noisy spread = unreliable) and
   `reliability_distributional(word)` estimated as a monotonic function of the word's distinct-context
   count in the corpus (more independent observations = lower estimation variance); combine via
   Ernst & Banks' `w_i proportional to 1/variance_i`. **Brain justification**: this is the single
   most rigorously proven combination MECHANISM found in any of the three scans (Ernst & Banks 2002
   and five confirming studies) — but its application to semantic channels is Martin (2016)'s
   untested theoretical proposal only, with no direct evidence at this level. Ranked second, below
   concreteness-gating, specifically because the mechanism's rigor is at the wrong scale for this
   application.

3. **Feature-content-gated rank fusion** — keep Borda/RRF machinery (already `HARD_PASS`-validated
   on this substrate via `exp_rrf_fusion_cpu_v1`) but condition its per-channel weight on motor/
   sensory feature content rather than raw POS tag — in practice this collapses toward option 1 once
   POS is replaced by its better-evidenced proxy (Vigliocco et al. 2006; Moseley & Pulvermüller
   2014 both show POS alone is confounded with feature content). Ranked third as a fusion-mechanics
   variant of option 1, not an independent hypothesis — worth testing only if option 1's linear blend
   underperforms and a rank-based combination is suspected to matter more than the weighting curve.

4. **Equal-weight Borda (current)** — retain strictly as the CONTROL arm. No source in any of the
   three scans offers positive evidence for equal weighting as a brain-preferred rule; it is the
   "no information about differential reliability" default, not a hypothesis under test.

## Citations (verified count)

29 distinct primary sources cited across the three lit-scans, each with author/year/venue supplied
by the sub-agent from live WebSearch/WebFetch (not from memory): Ernst & Banks 2002; Alais & Burr
2004; Knill & Pouget 2004; Fetsch, Pouget, DeAngelis & Angelaki 2011/2012; Jacobs 2002; Kording et
al. 2007; Martin 2016; Andrews, Vigliocco & Vinson 2009; Rogers et al. 2004; Lambon Ralph et al.
2016/2017; Silberer & Lapata 2012/2014; Rogers, Lambon Ralph, Garrard, Bozeat, McClelland, Hodges &
Patterson 2004; Chen, Lambon Ralph & Rogers 2017; Binney, Hoffman & Lambon Ralph 2016; Patterson,
Nestor & Rogers 2007; Bonner & Price 2013; Farah & McClelland 1991; Bruni, Tran & Baroni 2014;
Roller & Schulte im Walde 2013; Lynott & Connell 2013 / Connell & Lynott 2012; Louwerse 2011/2018;
Johns & Jones 2012; Günther, Rinaldi & Marelli 2019; Kiela & Bottou 2014; Hill & Korhonen 2014;
Wang, Zhang & Zong 2018; Hauk, Johnsrude & Pulvermüller 2004; Vigliocco et al. 2006; Moseley &
Pulvermüller 2014. Not independently re-verified against primary text by this synthesizer (lit-scan
sub-agent claims only) — treat citation existence as high-confidence (major, well-known venues named
correctly) but specific numeric details (e.g. exact weight ratios) as sub-agent-reported, not
hand-checked against the original PDF.

## Caveats on this note

- Per the mandatory lit-scan calibration penalty, all P estimates above are deflated 0.15-0.25 from
  the raw synthesis estimate, and novel-synthesis P is capped at 0.50.
- No new field-advisor field taxonomy applies cleanly here (`research_field_advisor.py`'s fields are
  built for substrate-physics/statistical-mechanics topics, not cognitive-semantics literature) — run
  and checked at cycle start per the standing ritual, but its ranked candidates (free-probability,
  semiconductor Glauber dynamics, etc.) are not adjacent to this question and are not cited above.
- This note does not itself run the cheap decisive test — that is the next actionable step, using
  data already on disk (no new corpus read required).
