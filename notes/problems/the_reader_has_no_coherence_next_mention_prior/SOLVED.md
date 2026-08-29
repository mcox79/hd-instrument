---
problem: the_reader_has_no_coherence_next_mention_prior
status: REFUTED
bar: "PASSES only with ALL of: 1. A coherence next-mention PRIOR channel (built in experiments/): P(referent) from verb-semantic / coherence-relation expectation, fused into the graded coref posterior as a Bayesian product. Copy the computation; SWEEP the prior's features + fusion weight. 2. On the STRUCTURALLY-DOMINATED residual (the ~19% where grammar gives no signal, recomputed on the same population), likelihood x prior beats the likelihood-only resolver CI-separated; the info-free twin (shuffled prior / random next-mention expectation) LOSES CI-separated; report CI half-width + null p95; no number crosses populations. 3. NO REGRESSION on the structure-decisive cases (where grammar already resolves it, the prior must not corrupt the answer -- byte-or-CI-equal), and a POSITIVE control the metric can move (a coherence-decisive minimal pair the prior gets and the likelihood-only resolver cannot). 4. One-screen summary. A rigorous NEGATIVE is a FULL PASS (e.g. 'a faithful coherence prior lifts the residual < the CI on real prose because a large slice is LitBank annotation-fiat ambiguity -- so the ~0.78 coref ceiling is a REAL bound, not a missing mechanism', with the positive control confirming the metric CAN move on constructed coherence-decisive pairs)."
result: "RIGOROUS NEGATIVE (a full pass per the bar). On the LitBank structurally-dominated pronoun-coref residual (n=205 TEST decisions, the graded likelihood-only resolver's structurally-dominated errors, doc-bootstrap 95% CI), the faithful coherence next-mention PRIOR (SELECTIONAL-fit via the predictive-reader verb-role grounded centroid + THEMATIC/coherence-relation re-mention, fused as a Bayesian product, fusion weight tuned on DEV-residual = its best shot, wp=1.5) recovers 0.0683 [0.0306,0.1078] vs likelihood-only 0.0 (0/205 by construction) -- BUT its own info-free twin (20-shuffle-averaged shuffled prior) recovers MORE, 0.1005 [0.0833,0.1199]; prior-minus-twin = -0.0322 [-0.0671,+0.0050], half-width 0.036, null p95 0.036, band NOT_SEP. The coherence prior does NOT beat its own noise -> it carries no usable signal on the residual. ORACLE ceilings (best-case pick per channel) confirm it: SELECTIONAL 1.5%, THEMATIC 1.0%, COMBINED 2.9% -- vs a fine-grained TOKEN-DISTANCE oracle 37.6%. The residual is intra-sentential SYNTACTIC binding (64%), not coherence-prior-decisive. POSITIVE CONTROL passes: on constructed coherence-decisive minimal pairs the SAME prior mechanism flips the pick correctly -- selectional 8/8, implicit-causality 8/8 -- where the structural likelihood and an info-free shuffle are at chance (~5/8). BRAIN-FAITHFUL cue-based binding (Kush 2013 item-level structural proxies, jointly re-tuned) also recovers 0/205. CROSS-DOMAIN CONFIRMATION (exp_coref_residual_crossdomain_gap_v1, GAP modern Wikipedia prose, clean spaCy parse): on the GAP residual (recency+subjecthood fail, n=437) clean-parse structural cues score 0.256 -- BELOW chance 0.5 -- so a GOOD parse does NOT recover the residual; the wall is SEMANTIC/world-knowledge, not parse-quality (verdict SEMANTIC_WALL_NOT_PARSE_WALL). Scorer = argmax==gold link accuracy on the fixed residual population."
floor: "The strongest floor actually run = the info-free 20-shuffle-averaged coherence-prior twin on the SAME residual population = 0.1005 [0.0833,0.1199]; the real coherence prior 0.0683 [0.0306,0.1078] does NOT clear it (prior-minus-twin -0.0322, NOT_SEP, null p95 0.036). Trivial floor: likelihood-only = 0.0 on the residual (0/205 by construction -- any perturbation 'beats' it, which is why the twin is the meaningful floor). Reachability ceiling (an oracle, not a floor): the fine-grained token-distance channel recovers 37.6% of the residual as a best-case pick, quantifying that the residual IS partly reachable -- by finer syntactic locality, NOT by the coherence prior."
controls: "(1) info-free twin = the coherence prior with per-candidate scores SHUFFLED, averaged over 20 shuffles -> the twin (0.100) BEATS the real prior (0.068), excluding 'the prior carries residual signal'. (2) ORACLE-ceiling decomposition (best-case pick per channel on the residual): selectional 1.5%, thematic 1.0%, combined 2.9%, fine-distance 37.6% -> excludes 'a better fusion weight would rescue the coherence prior' (even the oracle is near-chance) and localizes the reachable signal to fine distance. (3) COHERENCE-prior tradeoff curve (residual acc vs structure-decisive acc across fusion weights): at every weight residual barely rises (max 0.068 @ w=1.5) while structure-decisive collapses 1.000->0.648 -> excludes 'some weight lifts residual without regressing'. (4) FINE-DISTANCE tradeoff curve: residual rises to 0.283 but structure-decisive falls to 0.814 monotonically -> excludes 'the fine-distance signal is gateable non-regressing' (every residual gain costs an equal-or-greater structure-decisive loss). (5) NO-REGRESSION check at the DEV-residual-optimal weight: broke 1279/3638 structure-decisive -> confirms the residual 'lift' is unattainable without catastrophic regression. (6) POSITIVE CONTROL: the prior flips 8/8 constructed selectional pairs + 8/8 implicit-causality pairs; the structural likelihood and info-free shuffle sit at chance (~5/8) -> excludes 'the mechanism is broken / the metric cannot move' (it can; the population lacks the cases). (7) parse-based Hobbs syntactic-antecedent oracle (spaCy, separate diagnostic) = 28.8% on the intra-sentential residual, TYING raw linear-nearest -> excludes 'a dependency parse rescues the syntactic channel' (parse noise on archaic prose). DEV/TEST split by document; the coherence prior's selectional centroids learned on DEV docs only; fusion weight tuned on DEV-residual; all headlines on the disjoint TEST residual."
files_changed: "experiments/exp_coref_coherence_next_mention_prior_v1.py (incl. the brain_faithful_cue_binding arm), experiments/exp_coref_residual_crossdomain_gap_v1.py (the CROSS-DOMAIN GAP test that corrected the diagnosis), verification/test_coref_coherence_next_mention_prior.py, notes/problems/the_reader_has_no_coherence_next_mention_prior/SOLVED.md, notes/problems/the_reader_has_no_coherence_next_mention_prior/research_intrasentential_binding_mechanism_2026-08-29.md. No hdlab/ write (Q111); proposed hdlab direction below."
reverify: ".venv/Scripts/python.exe verification/test_coref_coherence_next_mention_prior.py"
---

# What was built and measured

The brief hypothesised that the coreference resolver's ~19% structurally-dominated residual is the **prior-decisive**
half of a two-term Bayesian computation (Kehler & Rohde 2013): `P(referent|pronoun) prop P(pronoun|referent) [the
Centering LIKELIHOOD the graded resolver computes] x P(referent) [a coherence-driven NEXT-MENTION PRIOR we do not
compute]`. The task: build the missing coherence prior, fuse it as a Bayesian product, and show it lifts the residual.

**I built the faithful coherence next-mention PRIOR -- both channels the literature pins -- and it does NOT lift the
residual on real narrative. The disk refuted the brief's mechanism, and a finer analysis identified the REAL missing
capability.** All measurements are on LitBank (100 novels, DEV/TEST split by document), the residual defined by the
landed graded likelihood-only resolver (`exp_coref_graded_cue_retrieval_litbank_v1`), recomputed in-place.

## The coherence prior, built and fused (bar item 1)

Two channels, each copied from the pinned computation, features + fusion weight swept (never adopted):
- **SELECTIONAL-FIT** (Altmann-Kamide 1999; McRae 1998; the substrate's `predictive_reader`): the pronoun's clause
  verb + role pre-activates the expected argument's grounded features (a verb-role grounded centroid learned on DEV
  docs, in-domain, glass-box); each candidate entity is scored by grounded cosine to that expectation.
- **THEMATIC / COHERENCE-RELATION re-mention** (Kehler-Rohde; Bott & Solstad 2014): a causal connective
  (because/so/since/as...) in the pronoun's pre-context biases re-mention toward the affected/object of the prior clause.
- **FUSION**: `posterior propto likelihood x prior` -- a log-linear sum of the graded net activation and the z-scored
  prior, the Bayesian product the bar names. Fusion weight tuned on the DEV residual (its best shot).

## The measured negative (bar item 2 -- a rigorous negative is a full pass)

On the TEST residual (n=205), the coherence prior recovers **0.0683 [0.0306, 0.1078]**. But its own **info-free twin**
(the identical prior with per-candidate scores shuffled, averaged over 20 shuffles) recovers **MORE: 0.1005 [0.0833,
0.1199]**. `prior - twin = -0.0322 [-0.0671, +0.0050]`, half-width 0.036, null p95 0.036, band **NOT_SEP**. **The
coherence prior does not beat its own noise** -- the strongest possible form of a negative. (The +0.068 "lift" over
likelihood-only is an artifact: likelihood-only is 0/205 on the residual by construction, so any perturbation "beats"
it; the meaningful floor is the twin, which the prior fails to clear.)

The **ORACLE ceilings** (best-case argmax per channel, no fusion) show this is not a tuning failure: SELECTIONAL
**1.5%**, THEMATIC **1.0%**, COMBINED **2.9%** on the residual -- near chance even as oracles. The coherence prior has
no purchase on this population.

## Why -- the residual is INTRA-SENTENTIAL SYNTACTIC BINDING, not a coherence prior (the diagnosis)

I reconstructed the actual sentences behind the residual. It decomposes cleanly:
- **64% is INTRA-SENTENTIAL** -- the antecedent is in the pronoun's own sentence: "the parson, who, as **he** rode,
  hummed a tune" (he = parson); "a child taking up **her** elders" (her = child); "these new women pay to a man ...
  while **he** is talking" (he = man). The brain resolves these with the **parse tree** (relative-clause attachment,
  c-command, Binding Theory), not a discourse-meaning guess.
- The graded resolver computes recency in **sentence buckets**, so it is blind WITHIN a sentence (every same-sentence
  candidate has identical recency). A **fine-grained TOKEN-DISTANCE** channel -- the same pinned recency/ACT-R currency
  at token granularity, a locality next-mention prior -- recovers **37.6%** of the residual as an oracle where
  sentence-recency scores **0%**. This is the real signal, and it is a *finer resolution of the FIRST (likelihood)
  term*, not a second Bayesian term.
- **But it is UNGATEABLE without a reliable parse.** The fine-distance tradeoff curve: fusing it lifts the residual to
  0.283 but drags structure-decisive accuracy from 1.000 to 0.814 -- **every residual gain costs an equal-or-greater
  structure-decisive regression** (bar item 3 fails for it). Applied globally it is weight-0 on DEV; wholesale it breaks
  517 cross-sentence cases (full 0.775->0.715). A Principle-B-respecting, entropy-gated, and intra-sentential-gated
  version each either nets ~0 on DEV or breaks more structure-decisive cases than it fixes (159 residual fixed vs 432
  structure-decisive broken). The information needed to know "local binding governs here" vs "discourse salience governs
  here" is the parse tree -- and a spaCy Hobbs-style syntactic-antecedent rule TIES raw linear-nearest at 28.8%, because
  the dependency parse is unreliable on 200-year-old literary prose (it mis-attaches the relative clause in the very
  first example: it parses the *mare* as humming the tune, not the parson).

## Leading with biology: the brain mechanism, researched, built, and measured (a 4-lane literature drill)

Because "the brain can do it, so can we" -- I did NOT stop at the coherence-prior negative. I ran a 4-lane literature
drill (`research_intrasentential_binding_mechanism_2026-08-29.md`, persisted verbatim) on HOW the brain resolves
intra-sentential binding, then BUILT the mechanism it surfaced and measured it. The drill's verdict:

- **The brain does NOT bind via an explicit parse tree.** Kush (2013); Kush, Lidz & Phillips (2015): the retrieval
  system cannot use c-command as a hierarchical RELATION; it uses ITEM-LEVEL structural PROXIES (clause-mate-hood, a
  LOCAL-domain feature, subjecthood) as WEIGHTED cues that CORRELATE with c-command, combined NONLINEARLY (Parker 2019).
- **It works on PARTIAL/underspecified structure and degrades gracefully.** Ferreira & Patson (2007) good-enough
  processing; Frazier-Clifton Construal + Swets et al. (2008): relative-clause attachment is the paradigm case of
  goal-modulated underspecification; Hemforth et al. (2000): attachment and binding run in PARALLEL, not gated.
- **Grammatical prominence (subjecthood) > linear recency, and is durable** (Gordon-Grosz-Gilliom; Gernsbacher et al.).
- **Principle B is applied early + largely structurally** (Chow-Lewis-Phillips 2014 hard/immediate; Badecker-Straub
  graded -- a live dispute).

**So the brain-faithful mechanism is cue-based retrieval with item-level structural-proxy cues -- NOT the brief's
coherence prior, and NOT a full parse tree. I built exactly that** (`brain_faithful_cue_binding` arm): added fine
linear-distance, clause-mate-hood / Principle-B (from `gov_verb`), relative-clause-head, and local-subjecthood as
WEIGHTED cues to the graded retrieval, jointly re-tuned on DEV. **Result: it recovers 0/205 of the residual.** Only the
Principle-B cue took a small, correct-signed weight (-0.5: a pronoun avoids its clause-mate); the others tuned to 0. DEV
full 0.7985 -> 0.7996 (negligible), TEST full 0.775 -> 0.771 (slightly down).

**Why the faithful mechanism recovers nothing -- the sharpened, research-grounded diagnosis:** the mechanism is correct,
but our item-level structural PROXIES are DEGRADED. The brain computes clause-mate-hood / local-domain features from its
own RELIABLE incremental parse; we compute them from a NOISY spaCy parse on 200-year-old prose, so they carry no usable
signal after the ACT-R currency. And the proxies that DO fire are EXCLUSIONARY (Principle B rules a candidate OUT); they
never POSITIVELY identify which of ~44 remaining candidates is the antecedent, because that needs the relative-clause
attachment RELATION (parson<->he) -- exactly the relational information Kush shows retrieval cannot use without reliable
structure. **The wall is PROXY QUALITY, bottlenecked by the PARSER on archaic prose -- a named, brain-grounded,
ADJACENT-COMPONENT limitation, not a wrong mechanism and not a missing coherence prior.** Good-enough processing
predicts graceful degradation on partial structure; we observe ZERO contribution, i.e. our proxies are below the noise
floor, not merely coarse -- the parse is too unreliable to yield even a weak proxy.

## CROSS-DOMAIN TEST -- and it CORRECTED my own diagnosis (the decisive push)

I claimed above the wall was "proxy quality bottlenecked by the noisy archaic-prose parser." I TESTED that claim on a
CLEAN-parse corpus and it was too optimistic. GAP (Webster et al. 2018 -- modern Wikipedia prose, gender-balanced
ambiguous pronouns, a 2-candidate A-vs-B task) is parsed RELIABLY by spaCy (`exp_coref_residual_crossdomain_gap_v1`).
On the FULL GAP set the clean parse fires and the cues carry signal (subjecthood 0.684 >> recency 0.525 >> chance 0.5).
**But on the GAP RESIDUAL (the analog: recency-wrong AND subjecthood-not-decisive, n=437), the CLEAN-parse structural
cues score 0.16-0.26 -- BELOW chance (0.5).** Dependency-distance 0.160, Principle-B clause-mate 0.167, combined 0.256.

**Structure -- even a perfect parse -- is ANTI-predictive on the residual**, because the residual by construction selects
for cases where structure and salience point the WRONG way and the gold is fixed by SOMETHING ELSE. That something is
SEMANTICS / WORLD-KNOWLEDGE. Even the "syntactic" LitBank cases are really semantic: "the parson, who, as he rode,
hummed" needs the world-fact that the RIDER is the parson, not the mare -- the syntax genuinely attaches the relative
clause to "mare" (spaCy is not even wrong there; the string is ambiguous). **VERDICT: SEMANTIC_WALL_NOT_PARSE_WALL.**

So the corrected, cross-domain-robust diagnosis: the ~0.78 coref residual is a REAL bound set by WORLD-KNOWLEDGE / rich
lexical SEMANTICS -- the no-LLM boundary + the p1 representation lane -- NOT a missing coherence prior (refuted) and NOT
(primarily) a fixable parser (a clean parse does not recover it). The brain-faithful cue-based mechanism is correct and
fires when structure decides (GAP full set, LitBank non-residual); the residual is precisely where structure does NOT
decide, on modern AND archaic prose alike.

## The positive control -- the mechanism works, the population lacks the cases (bar item 3)

On CONSTRUCTED coherence-decisive minimal pairs the same prior mechanism flips the pick correctly: **selectional 8/8**
("drink" -> water not jug; path verbs -> passage not animate; the coarse grounded space DOES separate these) and
**implicit-causality 8/8** (Garvey-Caramazza NP1/NP2 by verb class), where the structural likelihood (both candidates
symmetric) and an info-free shuffle are at chance (~5/8). **The metric CAN move; the mechanism is faithful and works --
the real residual simply does not contain these cases.** This is consistent with the parent's measurement that the
implicit-causality-decisive "NP1 verb NP2 because PRON" frame occurs n=0 times in LitBank's ~200K tokens, reconfirmed
here (thematic-connective oracle 2/59).

# What I did NOT establish (and would withdraw first if wrong)

1. **I did NOT prove the residual is irreducible in principle.** The fine-distance oracle (37.6%) proves a large slice
   IS reachable -- by finer *syntactic locality*, i.e. a reliable parse-based binding channel (a different organ),
   NOT by a coherence next-mention prior. The claim is specifically that the *coherence prior* the brief proposes does
   not reach it, and that the reachable part needs the parser + richer semantics + world knowledge. Withdraw first any
   implication that the residual is unrecoverable by *any* route.
2. **The selectional channel is ceiling'd by the coarse 12-dim grounded space (the p1 coupling), not proven impossible
   with richer semantics.** The positive control shows it works on clean object-vs-object pairs; it fails on the
   person-heavy residual because two people have near-identical grounded features. A richer lexical representation
   (p1) might lift the selectional oracle -- untested here (no-LLM invariant + coarse space).
3. **The parse diagnosis used spaCy `en_core_web_sm`, not the substrate's just-integrated incremental parser.** A
   better parser (or the incremental parser) might beat 28.8% -- I did not test it (its interface + archaic-prose
   robustness are the follow-on). The claim is that an OFF-THE-SHELF dependency parse does not rescue the channel.
4. **The residual is n=205 (TEST); CIs are honest but wide (half-widths ~0.036-0.068).** The negative rests on the
   prior failing to beat its own 20-shuffle twin, which is robust, not on a tight point estimate.

# KEY REALIZATIONS (the enabling moves)

1. **Reconstruct the actual sentences before theorising.** Pulling the raw text behind the residual (from the LitBank
   CoNLL) turned an abstract "prior-decisive residual" into a concrete, countable structure: 64% intra-sentential
   ("who, as he rode"), the rest world-knowledge/annotation-fiat. That single move refuted the brief's framing -- the
   residual is a SYNTAX boundary, not a discourse-coherence boundary.
2. **Measure the ORACLE ceiling of each channel before building the fusion.** The selectional oracle (1.5%) and
   thematic oracle (1.0%) are near chance -- so no fusion weight could rescue them. Asking "could this experiment even
   succeed?" (the highest-yield habit) saved building an elaborate fusion around a dead signal, and pointed straight at
   the one channel with signal (fine-distance, 37.6%).
3. **The info-free twin must be the FLOOR, not likelihood-only.** Because likelihood-only is 0/205 on the residual by
   construction, ANY perturbation "beats" it -- so a naive "+0.068 over likelihood" looks like a win. The 20-shuffle
   twin (0.100) is the honest floor, and the real prior fails to clear it. Recomputing the floor as the twin is what
   makes the negative airtight.
4. **The wall is a resolution-granularity gap in the FIRST Bayesian term, not a missing SECOND term.** The brain's
   cue-based retrieval decays activation with *continuous* distance; our resolver discretised it into sentence buckets
   (an OUR-INVENTION parameter). The finer-resolution version of the *same pinned cue* recovers 37.6% of the residual --
   but is ungateable without the parse, which is exactly why the brain uses syntax here. "Copy the computation, sweep
   the parameter" -- our parameter (sentence granularity) was too coarse, and the fix is a different organ (the parser),
   not a coherence prior.
5. **A cue that is right 38% and wrong 62% is worse than useless when applied indiscriminately.** Every gate I built
   (global weight, entropy, intra-sentential presence, Principle-B, parse-Hobbs) broke more structure-decisive cases
   than it fixed residual cases -- the same "precision-gate or it hurts" lesson from the verb-sense solve, here with the
   verdict that the gating *signal itself* (the parse structure) is what we lack.
6. **Leading with the biology relocated the wall precisely (the owner's push, and it paid off).** I assumed the
   intra-sentential residual needed a full PARSE TREE. The literature drill (Kush 2013) said the brain does NOT use
   c-command as a tree relation for retrieval -- it uses ITEM-LEVEL structural PROXIES as weighted cues, on PARTIAL
   structure with graceful degradation. So I built the brain's ACTUAL mechanism (structural-proxy cues, jointly tuned)
   rather than a parse-and-override.
7. **A CROSS-DOMAIN test corrected my OWN diagnosis -- the biggest single realization, and it required pushing past the
   first negative.** After the structural cues recovered 0 on LitBank, I blamed the noisy archaic-prose PARSER. I tested
   that on GAP (modern Wikipedia prose, clean parse) and was WRONG: on the GAP residual, CLEAN-parse structural cues
   score BELOW chance (0.256). A perfect parse does NOT recover the residual. The residual is fixed by SEMANTICS /
   WORLD-KNOWLEDGE ("the RIDER is the parson, not the mare"), on modern AND archaic prose alike -- the no-LLM boundary,
   not the parser. The lesson: when a mechanism fails, test the DIAGNOSIS on a domain where the suspected cause is
   absent, before committing to "fix component X." I nearly filed "fix the parser" as the #1 next problem; the
   cross-domain test showed the real #1 is rich lexical semantics / world-knowledge (p1 + the no-LLM boundary).

# AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)

- **COREF two-term-Bayes sub-claim (line ~214-217).** The audit states "the ~19% structural residual is the
  prior-decisive cases (the two-system boundary)". **This is REFINED/REFUTED by measurement:** the residual is NOT
  coherence-prior-decisive. A faithful coherence next-mention prior (selectional + thematic, fused as a Bayesian
  product) does NOT beat its own info-free twin on the residual (0.068 vs 0.100, NOT_SEP), and its oracle ceiling is
  2.9%. The residual is **64% INTRA-SENTENTIAL SYNTACTIC BINDING** (fine-distance oracle 37.6% vs sentence-recency 0%),
  reachable only by a reliable parse (Binding Theory) -- blocked by archaic-prose parse noise (Hobbs = linear-nearest =
  28.8%) -- plus rich lexical selectional preference (blocked by the coarse 12-dim grounded space, the p1 coupling) plus
  world knowledge (blocked by the no-LLM invariant). **NET: the ~0.78 pronoun-coref ceiling is a REAL bound for a
  glass-box discourse-level coherence prior; the two-system boundary is SYNTAX x SEMANTICS x WORLD-KNOWLEDGE, not
  LIKELIHOOD x coherence-PRIOR.** The coherence PRIOR mechanism itself is faithful and works (positive control 8/8 +
  8/8) -- it is the wrong tool for THIS residual, not a broken tool.
- **New cross-link:** the coref residual and the predictive-reader's "reversible role assignment" residual are the same
  kind of boundary -- where semantics/discourse cannot decide and SYNTAX must carry it. The mapped fix (parse-based
  binding) is the coref-side analogue of the relcl filler-gap parser.

# PROPOSED hdlab DIRECTION (strategy lands; Q111 -- NOT a coherence prior)

Do **NOT** land a coherence next-mention prior into `hdlab/coreference_resolver.py` -- it is refuted for the residual.
The measured, brain-faithful levers, in order:
1. **Finer-resolution recency in the pinned ACT-R currency.** The residual is a sentence-bucket granularity artifact.
   Exposing a token/clause-distance term is cheap and brain-faithful, BUT it must be **gated by syntactic structure**
   (it regresses structure-decisive if applied globally) -- so it is only worth landing *together with* (2).
2. **A parse-based SYNTACTIC-LOCALITY binding channel** (a new problem): use the just-integrated incremental parser to
   identify the pronoun's binding domain (relative-clause head, c-command, Principle B) and prefer the syntactically
   -local antecedent on intra-sentential cases. This is the organ that can recover the 37.6% the fine-distance oracle
   exposes. Gate it to intra-sentential competition so it does not touch cross-sentence structure-decisive cases.
3. **Richer lexical semantics (p1)** would lift the selectional channel's oracle above 1.5% -- the standing
   representation-quality lane, out of scope here.

# ADJACENT COMPONENTS -- capabilities / limitations / opportunities / brain-foundational status (seeds the next problems)

Per the owner's directive (2026-08-29): understanding each adjacent component's capabilities, limitations, optimization
opportunities, and brain-foundational status is how we PLAN the next problems. Each below is a candidate follow-on with
on-disk evidence + leverage. **RANKING CORRECTED by the cross-domain GAP test: WORLD-KNOWLEDGE / rich SEMANTICS (#1) is
the real residual bottleneck; the PARSER (#2) gates the FULL set but NOT the residual (a clean parse leaves the residual
below chance).**

1. **[HIGHEST LEVERAGE -- the real residual bottleneck] WORLD-KNOWLEDGE / rich lexical SEMANTICS (the grounded space +
   the no-LLM boundary).**
   - CAPABILITIES: the grounded space separates concrete object classes (positive control: selectional fit 8/8).
   - LIMITATIONS (MEASURED, cross-domain): the residual is fixed by semantics/world-knowledge, and NO glass-box channel
     reaches it -- selectional oracle 1.5% on LitBank (person-heavy, grounded-blind), and clean-parse structural cues
     score BELOW chance (0.256) on the GAP residual. The disambiguator "the RIDER is the parson not the mare" is
     world-knowledge the no-LLM invariant precludes and the 12-dim grounded space cannot encode.
   - OPPORTUNITY: a richer/contextual lexical-semantic representation (the standing p1 lane) is the ONLY lever that
     could move the residual within the no-LLM invariant; the irreducible remainder (specific world-facts, e.g. who did
     what in a Wikipedia bio) is a genuine bound. Measure how far a richer space lifts the selectional oracle.
   - BRAIN STATUS: the ATL flexible context-dependent hub is far richer than our 12-dim context-free lookup (a known
     deviation); the brain ALSO has world-knowledge our no-LLM substrate deliberately excludes.
2. **The PARSER / `gov_verb`-`role` extraction (spaCy `en_core_web_sm`) -- gates the FULL set, NOT the residual.**
   - CAPABILITIES: supplies governing verb + grammatical role (subjecthood is the strongest single cue -- GAP full-set
     0.684); powers the ACT-R role weighting and the item-level structural proxies where structure DOES decide.
   - LIMITATIONS (MEASURED): unreliable on 200-year-old prose (mis-attaches the first residual example); structural
     proxies built on it recover 0/205 of the LitBank residual. **BUT the cross-domain GAP test shows this is NOT the
     residual's root cause: even a CLEAN parse leaves the residual below chance.** The noisy parse costs us on the
     FULL set (where a better parse would sharpen subjecthood), not on the residual.
   - OPPORTUNITY: a register-robust parser (the brain reads Dickens fine -- this is a training-domain mismatch, not a
     fundamental limit) would improve FULL-set accuracy; the substrate's own `incremental_parser` is brain-foundational
     in ALGORITHM (left-corner, Now-or-Never, good-enough, prediction-based revision -- Christiansen & Chater; Ferreira),
     but it needs POS input and produces only verb-argument slots, not clause-embedding structure. Extending it +
     robustifying POS on literary prose is a real follow-on.
   - BRAIN STATUS: the extraction TOOL (spaCy) is OUR-INVENTION/convenient; the substrate's `incremental_parser`
     ALGORITHM is brain-foundational. Its input (POS) and coverage (no embedding structure) are the gaps.
3. **The GRADED COREF RESOLVER (`exp_coref_graded_cue_retrieval_litbank_v1`, the likelihood).**
   - CAPABILITIES: brain-faithful cue-based retrieval (Lewis-Vasishth/McElree), 0.775 on the competitive subset, a
     calibrated entropy abstain signal. PINNED mechanism.
   - LIMITATIONS: computes recency in SENTENCE buckets (blind within a sentence); the candidate pool is the WHOLE
     document (mean 45) where the brain's attentional focus is ~4 entities; the residual DEFINITION uses GLOBAL cues
     (max-subjecthood over the pool) where the brain uses LOCAL prominence (Cb).
   - OPPORTUNITY: finer (token/clause) recency granularity in the ACT-R currency -- but only worth it GATED by reliable
     structure (the parser, component 2), else it regresses (measured tradeoff curve). A local-focus (Cb) prominence cue
     matching the brain's Centering ranking.
   - BRAIN STATUS: PINNED and faithful; the deviation is the sentence-bucket granularity (an OUR-INVENTION parameter).
   - (The 12-dim GROUNDED SEMANTIC SPACE is folded into component 1: it separates concrete objects 8/8 but cannot
     separate two people, oracle 1.5% -- the p1 representation lane.)
4. **MENTION DETECTION / candidate pool (`data/litbank/who_did_what_events.json`, single-head-token cache).**
   - CAPABILITIES: supplies mentions + gold clusters + roles.
   - LIMITATIONS (MEASURED): stores only a single HEAD TOKEN per mention (parent's flag 4); the pool is polluted with
     mis-extracted "entities" (possessives like "my"/"us", mis-parses like "hwome") and averages 45 gn-compatible
     candidates; the agreement filter barely prunes (parent: pool 39.9->39.3 null).
   - OPPORTUNITY: full mention spans + entity TYPE + a real animacy/type filter would shrink the pool toward the brain's
     small attentional focus and remove pollution -- may make the residual easier for every channel.
   - BRAIN STATUS: OUR-INVENTION placeholder; the brain tracks a small set of discourse-active entities, not 45.
5. **The PREDICTIVE READER (`hdlab/predictive_reader`) as the coherence-prior source (the brief's proposal).**
   - CAPABILITIES: verb-role -> expected-argument grounded features + -log P surprisal (validated, integrated).
   - LIMITATIONS (MEASURED here): as a `P(referent)` source for coref it is dead on the residual (oracle 1.5-2.9%) --
     it predicts feature-space, and the residual is person-heavy (grounded-blind) + intra-sentential (syntax, not
     selectional fit).
   - OPPORTUNITY: it is the RIGHT source for the OBJECT/selectional residual slice IF the grounded space (component 1)
     is richer -- coupled to p1.
   - BRAIN STATUS: PINNED for anticipation; MIS-APPLIED as the coref prior for this population (the brief's error).

---

## TLDR (plain language)

The reader still misses about 1-in-5 of the genuinely hard "who is *she*?" cases. The brief guessed the fix was a
*meaning* step -- guess who the story is about to talk about next. I built that step exactly as the brain does it and
**measured that it doesn't help these cases at all** -- it does no better than a scrambled version of itself. I then
tested every brain-faithful alternative: a finer word-by-word memory cue, and the brain's own structural-binding cues
(the way the brain uses grammar without a full parse tree). None recovered the hard cases. Crucially, I then checked
whether the problem was just our noisy parser on 200-year-old prose by testing on CLEAN modern text (Wikipedia): a
perfect parse *still* does not recover the hard cases (it does worse than a coin flip on them). So the hard residual is
not a grammar problem at all -- it is settled by **world knowledge** ("the one riding the mare is the parson, not the
mare"; "the one who dumped her boyfriend is Cheryl"). Our reader deliberately has no outside AI and only a coarse
12-feature meaning space, so it cannot supply that world knowledge. That is the wall -- and per the owner's push I am now
drilling exactly HOW the brain applies world knowledge to reference, to find a glass-box, no-outside-AI way to replicate
it (a knowledge-base / plausibility cue built from the substrate's static knowledge foundation). See the follow-up drill.

## QUESTIONS
None -- the bar is met as a rigorous negative (the faithful coherence prior fails to beat its info-free twin on the
residual; the positive control confirms the mechanism can move the metric on constructed pairs). One judgement call for
you at integration: I marked this **REFUTED** (the brief's coherence-prior mechanism is the wrong fix for this
residual) rather than SOLVED, because the honest deliverable is the refutation + the redirected real mechanism, not a
lifted number. If you would rather see it labelled SOLVED (a rigorous negative is a full pass per the bar), the content
is identical.

## NEXT STEPS
1. (Strategy) Re-verify the witness; do NOT land a coherence next-mention prior into `hdlab/coreference_resolver.py`
   (refuted for the residual).
2. (Strategy) Fold the AUDIT UPDATE into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (the coref two-term-Bayes sub-claim: the
   residual is syntactic-binding-bound, not coherence-prior-decisive).
3. (Follow-on problem) Parse-based syntactic-locality pronoun binding for the intra-sentential residual, using the
   incremental parser (adjacency 1) -- the real fix, and the highest-leverage remaining coref lever.
