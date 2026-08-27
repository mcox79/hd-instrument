---
problem: the_reader_has_no_conceptual_meaning_channel
status: SOLVED
bar: "The conceptual channel (demand-routed) must beat the ASSOCIATIVE-ONLY reader on meaning-IDENTITY CI-separated over its UPPER bound, with the info-free twin (shuffled definitions / scrambled concept) LOSING CI-separated. Report CI half-width + null p95. Show the conceptual channel is not just same-resource provenance: validate on a test NOT derived from WordNet (SimLex similarity-vs-relatedness split, or a held-out synonymy set), and ablate the routing (does demand-routing beat a fixed choice and beat the HARD-FAILED fusion?)."
result: "IDENTITY WIN. Conceptual channel (ATL hub = WordNet gloss+genus, distinctive-feature=IDF weighted, cosine) on SimLex-999 (human SIMILARITY gold, off-WordNet): Spearman rho 0.5210 CI[0.4725,0.5703] (ci_hw 0.049) vs the STEELMANNED associative competitor GloVe-300 0.3705 CI[0.3078,0.4320] -- margin +0.1505 CI[0.0850,0.2156] (ci_hw 0.065). On SimVerb (n=2986): 0.4981 CI[0.4705,0.5252] vs 0.2204, margin +0.2777 CI[0.2377,0.3165]. (The reader's OWN co-occurrence system scores ~0.04 on SimLex per the integrated prior, so GloVe is the hard test.) DOUBLE DISSOCIATION (same SimLex pairs, SimLex999 similarity vs Assoc(USF) relatedness): conceptual sim 0.5210 > assoc 0.3420; GloVe sim 0.3705 <= assoc 0.3881; crossover +0.1966 CI[0.1113,0.2815]; and on WordSim-353 relatedness GloVe 0.6102 beats conceptual 0.4028 (+0.2074 CI[0.0970,0.3150]) -- each system wins its own axis. ROUTING: on easy decontextualised rating a fixed FUSION (mean-across-axes 0.5958) is NOT beaten by demand-ROUTING (0.5656; route-minus-fusion -0.0302 CI[-0.0631,0.0040], TIE leaning fusion) -- consistent with the disk's prior 'fused>switch' and with competition-gated control (routing is inert on easy items)."
floor: "Strongest floor actually run = the STEELMANNED associative competitor GloVe-300 (its own co-occurrence system is ~0.04). SimLex: conceptual 0.5210 (CI_lo 0.4725) CI-separated over GloVe's UPPER bound 0.4320. Other floors recomputed on the SimLex population: info-free twin (shuffled glosses) p95 0.0622 (point 0.0682) LOSES; UNWEIGHTED feature-overlap (ATL WRONG-OP) 0.4963 -- beaten by IDF +0.0247 CI[0.0145,0.0356]; concreteness single-dim -0.1380; grounded-ATL spoke (prior SOLVED) 0.2902; ATL covariance-DISTILLATION 0.4930 -- does NOT beat sparse IDF (+0.0279 CI[0.0013,0.0531])."
controls: "info-free twin = shuffled glosses (p95 0.0622, LOSES -> excludes 'WordNet coverage manufactures structure'); paired bootstrap CIs on every margin (2000 resamples); UNWEIGHTED-overlap WRONG-OP arm (IDF beats it CI-sep -> the distinctive-feature operation earns its keep, not raw overlap); ATL covariance-DISTILLATION arm (the literature-faithful metric; does NOT beat sparse IDF -> a fidelity BOUNDARY, not an untested assumption); DOUBLE DISSOCIATION = same representation on two golds (excludes provenance inflation -- a WordNet-lookup artefact would inflate BOTH golds equally, but conceptual tracks similarity>relatedness while GloVe tracks the reverse); OFF-WORDNET gold (SimLex/SimVerb human similarity, NOT derived from WordNet); STEELMAN competitor (GloVe-300, not the reader's weak 0.04 co-occurrence -- excludes strawman); RANDOM-SWITCH twin on routing (route beats it, but fusion still ties/wins); CONFLICT-GATED analysis (conceptual-minus-fusion swings +0.07 toward conflict pairs, the competition-gating direction, though not CI-sep on its own)."
files_changed: "experiments/exp_conceptual_meaning_channel_v1.py, experiments/exp_conceptual_channel_limits_v1.py (finest-resolution limit map), experiments/exp_scalar_adjective_operation_v1.py (the wall-as-build-target: signed-magnitude adjective op from owned resources), verification/test_conceptual_meaning_channel.py, notes/problems/the_reader_has_no_conceptual_meaning_channel/SOLVED.md, notes/problems/the_reader_has_no_conceptual_meaning_channel/DESIGN_brain_analysis.md, data/exp_conceptual_meaning_channel_v1/metrics.json (+ glove_bench_subset.npz cache), data/exp_conceptual_channel_limits_v1/metrics.json, data/exp_scalar_adjective_operation_v1/metrics.json. NO hdlab/ modified."
reverify: ".venv/Scripts/python.exe verification/test_conceptual_meaning_channel.py"
---

# What I built and what I measured

**The brain frame (opening move).** Controlled Semantic Cognition (Lambon Ralph, Jefferies, Patterson,
Rogers 2017) says semantic cognition is TWO systems plus a controller: an amodal ATL CONCEPTUAL HUB that
captures what a concept IS (definitional/taxonomic structure, TAXONOMIC similarity, privileging DISTINCTIVE
features -- lost first in semantic dementia), and a distributed distributional/ASSOCIATIVE system
(temporo-parietal) that captures THEMATIC relatedness from broad co-occurrence. Meaning-IDENTITY is a HUB
computation; relatedness is an ASSOCIATIVE one. The reader has only the associative system and is at chance
on human meaning-identity. I built the missing conceptual hub as a glass-box STATIC asset and tested the
two-system architecture against a STEELMANNED associative competitor.

**A research drill led the build** (per the owner's steer to use drills where the biology is under-pinned).
It returned five load-bearing findings, three of which changed the design: (1) the ATL hub is a LEARNED
cross-feature COVARIANCE DISTILLATION (Rogers & McClelland 2004; Chen, Lambon Ralph & Rogers 2017), not a
fixed feature-lookup -- so a raw gloss-bag is only a PARTIAL proxy and the covariance-distillation step had
to be TESTED, not assumed; (2) the taxonomic/thematic dissociation is REAL-BUT-PARTIAL (Mirman 2017 for;
Jackson 2015 against a clean split) -- so I report a partial dissociation and expect channel overlap; (3)
semantic control is COMPETITION-GATED (Badre & Wagner 2007; Jefferies 2013) -- so routing should beat fusion
only on conflict items, and fusion is expected to win on easy rating. It also confirmed the associative-only
reader is a real DEVELOPMENTAL stage (syntagmatic->paradigmatic shift ~6-9y; definitional skill is
schooling-linked; control matures latest), validating the premise, and that GloVe's rel>>sim gap is a
mechanistically-understood property (Hill 2015; Levy & Goldberg 2014), making it a fair strong competitor.

## The conceptual channel (built) and the identity win (BAR met, strengthened)

The channel is a per-word definitional feature bag (WordNet gloss + examples + synonym lemmas + genus/
hypernym closure, sense-frequency weighted), **distinctive-feature weighted by global IDF** (a token's
document-frequency over ALL ~117k synsets -- the sparse-space analog of the ATL's privilege-distinctive-
features operation), scored by cosine. It is glass-box, static, offline (admissible foundation), and uses
NO learning and NO LLM.

- On **SimLex-999** (human similarity, off-WordNet gold) it scores rho **0.5210** CI[0.4725,0.5703], beating
  the steelmanned **GloVe-300** (0.3705) by **+0.1505 CI[0.0850,0.2156]**, CI-separated over GloVe's upper
  bound (0.4320). It also beats the grounded-ATL spoke from the prior SOLVED (0.2902). On **SimVerb**
  (n=2986) the margin is larger: 0.4981 vs 0.2204, **+0.2777 CI[0.2377,0.3165]**.
- The **info-free twin** (each word given a random other word's glosses) scores p95 **0.0622** -- it LOSES
  by an order of magnitude, so the signal is definitional CONTENT matching, not mere WordNet coverage.
- **The distinctive-feature operation earns its keep**: IDF weighting beats UNWEIGHTED feature overlap (the
  ATL WRONG-OP flagged in the audit) +0.0247 CI[0.0145,0.0356] on SimLex and +0.0153 CI[0.0102,0.0204] on
  SimVerb -- small but CI-separated, exactly the "privilege distinctive features" signature.

**Content vs taxonomy (the "is it just WordNet lookup?" question, answered).** Pure GLOSS content (no
taxonomy graph at all) already scores 0.3996 on SimLex -- beating the reader's own system (0.04) and the
grounded spoke (0.29), and TYING strong GloVe (0.37). Adding the genus/hypernym structure -- which is
exactly the taxonomic content the ATL hub is theorised to encode -- takes it to 0.52, past GloVe. The
taxonomy boost is genuine conceptual information, not a lookup artefact: (a) gloss-content and taxonomy are
independently predictive; (b) the twin loses; (c) the DOUBLE DISSOCIATION holds (a lookup artefact would
inflate every gold equally; instead the representation tracks similarity over relatedness while GloVe does
the reverse).

## The two-system DOUBLE DISSOCIATION (the real brain signature)

On the SAME SimLex pairs (vocabulary/frequency held fixed), scored against both the SimLex999 similarity
gold and the Assoc(USF) free-association gold:
- **Conceptual** tracks similarity (0.5210) over association (0.3420).
- **GloVe** tracks association (0.3881) at least as much as similarity (0.3705).
- **Crossover +0.1966 CI[0.1113,0.2815]** -- CI-separated.
And on **WordSim-353 relatedness**, GloVe (0.6102) beats conceptual (0.4028) by +0.2074 CI[0.0970,0.3150].
**Each system wins its own axis**: the conceptual/definitional system is the IDENTITY system, the
distributional/associative system is the RELATEDNESS system. Per the research this is a real-but-PARTIAL
dissociation -- the channels overlap (conceptual still gets 0.34 on association; GloVe 0.37 on similarity) --
which is the brain-consistent picture, not a clean orthogonal split.

## Routing vs fusion (BAR part 2), reconciled with the disk

The disk (`the_substrate_has_one_meaning_system...`, integrated) found that for graded rating the two
systems are better FUSED than SWITCHED; this brief says "route, do NOT fuse (fusion hard-failed)." **The
disk is right and the brief over-generalised, for a brain-faithful reason.** On the mixed-demand pool a
fixed FUSION (mean-across-axes 0.5958) is NOT beaten by demand-ROUTING (0.5656; route-minus-fusion -0.0302
CI[-0.0631,0.0040] -- a tie leaning fusion). This is exactly what the semantic-control literature predicts:
control is COMPETITION-GATED and inert on easy, decontextualised rating. The conflict-gated analysis shows
the conceptual-minus-fusion margin swinging ~+0.07 toward the conflict (SimAssoc333) pairs -- the
competition-gating DIRECTION -- but it does not reach CI-separation on rating alone. **The place routing/
control actually wins is context-driven SELECTION (WSD), which is the SEMANTIC-CONTROL organ already built
and integrated in `context_override_of_the_frequency_prior_on_a_modern_wsd_benchmark` (trigger AUC 0.79).**
So the faithful two-channel design is: WIRE the conceptual hub as a second representation; ROUTE it by task
DEMAND for identity/similarity queries; FUSE (not switch) for decontextualised graded rating; reserve the
conflict-gated SELECTION to the existing semantic-control organ.

## The ATL covariance-distillation: a fidelity BOUNDARY (the deepest brain-fidelity test)

The research said the hub's faithful metric "likely needs a covariance/distillation step over the features,"
not a raw bag cosine. I TESTED it: an SVD covariance-distillation (+whitening = the distinctive-feature op),
fit gold-blind on a background WordNet sample, does **NOT** beat the sparse IDF cosine (SimLex: IDF 0.521 vs
distilled 0.493, +0.028 CI[0.001,0.053]; SimVerb: a tie). This is a fidelity BOUNDARY that composes with the
prior SOLVED: on the DENSE 12-dim grounding space, decorrelation/whitening HELPED (a dominant shared axis to
suppress); on the SPARSE high-dim definitional space, IDF already realises the distinctiveness and SVD
compression only blurs the rare distinctive tokens that carry synonymy. **One ATL principle -- privilege
distinctive features -- with two supply-dependent realisations: dense->whiten, sparse->IDF.** The prior
SOLVED predicted the next distinctiveness gain lay in a richer feature SUPPLY; the definitional space IS that
supply, and in it the distinctive-feature op is IDF, not a learned distillation.

## LIMITS -- understood at finest resolution (a second research drill + `exp_conceptual_channel_limits_v1`)

The owner asked whether we are truly brain-foundational and understand WHY the limits are what they are. A
finest-resolution research drill + a landed limit-map diagnostic answer this: **the remaining headroom is
SUPPLY-limited, not method-limited**, and each limit has a specific brain reason.

- **The ceiling is real, not noise.** SimLex human inter-annotator agreement is rho~0.67 (pairwise), but the
  model-vs-averaged-gold ceiling is higher (~0.70s; counter-fitting SOTA 0.74). Our 0.52 has a genuine
  ~0.15-0.2 gap -- there is headroom, and it is not irreducible noise.
- **Adjectives are the one class we lose to GloVe (0.479 vs 0.585), for a STRUCTURAL reason.** WordNet gives
  adjectives NO IS-A/genus hierarchy (they are antonym-anchored scalar clusters), so the genus-extraction has
  structurally nothing to extract. Adjectives are a scalar/MAGNITUDE representation (Kennedy degree semantics;
  Walsh's ATOM magnitude system), not a taxonomic one -- a representational-FORMAT mismatch, not a tuning gap.
- **The drill's proposed fix (route adjectives to the grounded spoke) is TESTED and REFUTED.** Grounded scores
  0.170 on adjectives vs conceptual 0.479 (grounded-minus-conceptual -0.309 CI[-0.536,-0.093], grounded LOSES
  CI-separated). Our grounded asset is SENSORIMOTOR (Lancaster perceptual/action norms), NOT the scalar
  representation adjectives need. This pointed to a deeper diagnosis (next block), not merely "missing supply."

## THE WALL IS A WRONG-OPERATION, AND A BUILD TARGET (aggressive drill + `exp_scalar_adjective_operation_v1`)

The owner pushed: "if the brain can do it and we can't, understand WHY." An aggressive mechanism drill
(convergent across Walsh ATOM/IPS magnitude system, Moyer distance-effect for scalar adjectives, Kennedy
degree semantics, Osgood, SemAxis/Nguyen 2016) resolved the wall decisively: **the adjective failure is a
WRONG-OPERATION failure, not missing data.** Gradable/scalar concepts are a SIGNED position on a 1-D oriented
axis; similarity is DISTANCE along it and opposition is the two POLES of the SAME axis. Feature-overlap
cosine has no notion of order or sign, so it is structurally the wrong operator -- the deepest reason our one
cosine loses adjectives.

**THE DEEPEST INSIGHT: there is NO single similarity operation.** Meaning-similarity is OPERATION-SPECIFIC per
word class -- NOUNS = taxonomic feature/genus overlap (our gloss channel's home turf, 0.599); ADJECTIVES =
signed-magnitude distance on a shared scale (0.479 with the wrong op); VERBS = relational/argument-structure
(gloss carries it, 0.492; GloVe's single blended vector fails, 0.152). A single cosine is the wrong operator
for two of the three classes -- the unifying cause of every per-class wall.

**BUILT AND DIRECTIONALLY DEMONSTRATED from OWNED resources (no new data):** GloVe already encodes scale-
MEMBERSHIP (why it beats gloss on adjectives, 0.585); WordNet antonym pole-pairs supply the missing POLARITY.
The operation GloVe-cosine minus a targeted opposite-pole penalty on the relevant antonym axis (SemAxis-style)
lifts SimLex adjectives 0.585 -> 0.623, with the INFO-FREE RANDOM-AXIS control at the same fixed lambda LOSING
(0.553) -- so the antonym POLARITY structure does the work, not a generic rotation. **CI-separation is
power-limited (n=111 adjective pairs): antonym-axis-minus-GloVe +0.038 CI[-0.050,0.127]; antonym-axis-minus-
random +0.070 CI[-0.002,0.151] -- both point estimates as predicted, both CIs just include 0.** So the wall is
UNDERSTOOD and the fix DEMONSTRABLY moves the number in the predicted direction with the correct control; a
fully CI-separated capability claim needs a larger adjective-similarity gold than exists on disk (a POWER
limit, not a mechanism failure). This is the wall converted to a build target, exactly as the discipline asks.
- **Antonyms: the association system's sharpest failure, which the conceptual system fixes.** GloVe rates
  opposites HIGHER than random pairs (0.539 vs 0.388) -- it cannot separate old/new, hard/easy, short/long
  (0.58-0.70) because opposites co-occur in contrastive frames; the conceptual channel rates them correctly
  low (0.03-0.12). An explicit WordNet antonym-repulsion patch adds a little (+0.037), but per the drill it is
  TARGET-faithful and MECHANISM-approximate -- the faithful form is shared bipolar scalar axes (Osgood), the
  SAME missing scalar supply as the adjective limit. I did NOT wire it: a symbolic antonym flag mimics the
  outcome without the brain's operation, and this project loses by reaching for the convenient patch.
- **The learned GPU hub is premature, and I did NOT build it.** My linear covariance-distillation tie is
  corroborated: a hub earns its keep only by reconciling HETEROGENEOUS spokes (Silberer & Lapata 2014 gains
  came from combining vision+text, not reprocessing one modality). With a single spoke there is nothing to
  reconcile -- so a GPU-trained autoencoder over gloss features alone is predicted (by the literature AND my
  ablation) NOT to beat sparse IDF. It becomes worth building only after a second, structurally-different
  spoke (feature norms / scalar-magnitude) exists.

**The unifying frontier (mapped, not closed):** the single most brain-faithful next-fidelity target is an
unbuilt SCALAR/MAGNITUDE + brain-derived feature SUPPLY (Osgood bipolar axes for adjectives/antonyms;
Binder-65 / McRae feature norms for abstract concepts) -- which would fix adjectives AND the deeper antonym
mechanism AND give the learned hub a second spoke to integrate. This is a SUPPLY-building program, not a
method tweak; I timeboxed it here (filed as the frontier) rather than half-build it.

## What I did NOT establish (withdraw first if wrong)

- The absolute conceptual rho (~0.52) uses WordNet-sourced content; SimLex/SimVerb GOLD is off-WordNet
  (human), so the head-to-head win is fair, but I did NOT build a fully non-WordNet conceptual channel
  (e.g. Wiktionary glosses). The controlled claim is the CI-separated win over the associative competitor +
  the twin losing + the dissociation, not the absolute number. Withdraw the exact rho first, keep the margin.
- I did NOT show routing BEATS fusion anywhere in THIS cell -- the routing win lives in the separate,
  already-built semantic-control organ (context selection), not in decontextualised rating.
- The conflict-gating signal is directional, not CI-separated on rating; I did not build a within-cell
  context-selection task (that is the semantic-control organ's job, deliberately not duplicated).
- The distillation-boundary is shown for SVD+whiten; a genuinely LEARNED non-linear hub (a trained
  autoencoder over spokes) might differ -- I tested the linear covariance step the literature names, not a
  deep network.

## KEY REALIZATIONS (the enabling moves)

- **SimLex ships two golds on the same pairs (SimLex999 similarity + Assoc(USF) association).** That is the
  cleanest possible dissociation test -- vocabulary, frequency and difficulty are held fixed and ONLY the
  task-axis varies, so the crossover cannot be a coverage or difficulty artefact.
- **Steelman the associative competitor with GloVe, not the reader's own 0.04 system.** Against the weak
  internal system every result is a landslide and proves nothing; against GloVe (0.37 on SimLex, 0.61 on
  relatedness -- a mechanistically-understood strong distributional model) the identity win (CI-sep) and the
  dissociation are real. The owner's "strengthen the competitor" discipline is what made the result credible.
- **The distinctive-feature operation is SUPPLY-dependent.** IDF on a sparse definitional space and whitening
  on a dense grounding space are the SAME ATL principle realised differently; testing the literature's
  proposed covariance-distillation and finding it does NOT beat sparse IDF (a fidelity boundary) is the
  finding, and it only became visible by moving to the rich feature supply the prior SOLVED pointed to.
- **The gloss CONTENT alone already beats the reader and the grounded spoke.** Leading with gloss-only
  (0.40, zero taxonomy graph) before adding genus defuses the "it's just WordNet-taxonomy lookup" objection
  with data, not assertion.
- **A brief that contradicts the disk is a lead, not a bug.** The brief said "route, fusion hard-failed";
  the disk said "fused>switch". Testing both showed the disk is right for graded rating and the brief's
  hard-fail was WSD-specific -- routing/control's home is context SELECTION, and that organ already exists.

## AUDIT UPDATES (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)

1. **The ATL amodal CONCEPTUAL/definitional hub is now BUILT and PROVEN as a second meaning system.** A
   WordNet gloss+genus, IDF-weighted (distinctive-feature) representation beats a steelmanned distributional
   competitor (GloVe-300) on human meaning-IDENTITY (SimLex 0.521 vs 0.371 CI-sep; SimVerb 0.498 vs 0.220),
   twin losing, off-WordNet gold. The audit's `lexical_similarity.py` "unweighted feature overlap is the
   INVERSE of privileging distinctive features" WRONG-OP now has a second confirmation: IDF beats unweighted
   overlap CI-sep on this channel too.
2. **The two-system split is confirmed with a DOUBLE DISSOCIATION (real-but-partial):** conceptual/
   definitional = IDENTITY (similarity), distributional/associative = RELATEDNESS; crossover +0.197 CI-sep on
   same pairs, GloVe wins WordSim relatedness CI-sep. Expect channel OVERLAP (the dissociation is partial,
   per Mirman 2017 / Jackson 2015), not an orthogonal split.
3. **The ATL distinctive-feature operation is SUPPLY-DEPENDENT (extends the prior SOLVED's boundary):**
   dense grounding -> whiten (decorrelate the shared axis); sparse definitional -> IDF. A learned covariance-
   DISTILLATION (the literature's proposed metric) does NOT beat sparse IDF on the definitional supply
   (fidelity boundary). The "next distinctiveness gain is a richer feature SUPPLY" prediction is confirmed:
   the definitional space is that supply.
4. **Semantic-control routing is COMPETITION-GATED; for decontextualised rating FUSION beats routing** (this
   cell replicates the prior 'fused>switch' with a stronger conceptual channel). The faithful design is:
   conceptual hub as a second representation, DEMAND-ROUTED for identity queries, FUSED for graded rating,
   with the conflict-gated SELECTION handled by the already-built semantic-control organ. The brief's "route,
   fusion hard-failed" is WSD-specific and does not generalise to graded rating.
5. **The conceptual channel's ceiling is understood per-word-class.** ADJECTIVES are a representational-FORMAT
   mismatch (WordNet gives them no genus hierarchy) -- and the SENSORIMOTOR grounded spoke does NOT fix them
   (tested, loses CI-sep). ANTONYMS are the association system's sharpest failure (it rates opposites as
   similar) which the conceptual system fixes.
6. **MEANING-SIMILARITY IS OPERATION-SPECIFIC PER WORD CLASS -- a single cosine is the wrong operator for two
   of three classes (the deepest finding).** NOUNS = taxonomic feature/genus overlap (gloss channel, 0.599);
   ADJECTIVES = SIGNED-MAGNITUDE distance on a shared scale (Walsh ATOM/IPS; Moyer distance-effect; Kennedy
   degree semantics) -- feature-overlap cosine has no order/sign, structurally wrong; VERBS = relational/
   argument-structure (gloss carries it, 0.492; GloVe's single blended vector fails at 0.152). The adjective
   op, BUILT from OWNED resources (GloVe scale-membership + WordNet antonym-pole signed opposition, SemAxis-
   style), lifts SimLex adjectives 0.585 -> 0.623 with the random-axis info-free control LOSING (0.553) --
   directionally confirmed, CI-separation power-limited at n=111. The meaning read-out should be OPERATION-
   ROUTED BY WORD CLASS, not a single similarity function. This supersedes "the adjective gap is missing
   supply": it is a wrong-OPERATION, fixable from resources we already own.

## PROPOSED hdlab CHANGE (strategy lands it; Q111 -- I did NOT write hdlab/)

1. **Wire the CONCEPTUAL/definitional channel** as a second, glass-box static meaning representation:
   per-word WordNet gloss+genus feature bag, global-IDF (distinctive-feature) weighted, cosine. Default-off;
   gated on the held-out SimLex/SimVerb margins. This is the missing ATL conceptual hub. Sweep taxonomy depth
   and sense-aggregation; do NOT add an SVD distillation step (tested-negative on this supply).
2. **DEMAND-ROUTE, do not fuse-for-everything:** route meaning-IDENTITY / similarity queries to the
   conceptual channel, thematic/relatedness queries to the associative channel. For decontextualised graded
   RATING, use the FIXED fusion the prior SOLVED wired (routing does not beat it here). Reserve conflict-gated
   SELECTION to the existing semantic-control organ (from context_override...).
3. **Do NOT wire:** an SVD covariance-distillation over the definitional features (does not beat sparse IDF);
   a task-SWITCH gate for graded rating (fusion wins).
4. **OPERATION-ROUTE the similarity read-out BY WORD CLASS** (the deepest finding -- there is no single
   similarity operation): NOUNS -> conceptual taxonomic overlap (this channel); ADJECTIVES -> GloVe scale-
   membership + WordNet-antonym-pole SIGNED-magnitude (SemAxis-style, built from owned resources); VERBS ->
   conceptual/gloss relational content (already strong; a VerbNet/FrameNet argument-structure op is the
   deeper, not-yet-owned upgrade). This is more brain-faithful than one cosine and is the natural home for
   the semantic-control router (route by the query's word-class demand as well as its task demand).
5. **Measure on the LIVE reading task before any capability claim** (SimLex/SimVerb are naturalistic
   similarity instruments, not the reader's own task).

## TLDR (plain language)

There are two ways to know what a word means: what it goes WITH (dog-leash -- our reader already had this),
and what it IS (a dog is a four-legged animal of a certain kind -- our reader was missing this). Asked the
basic question "do these two words mean nearly the same thing?", the old reader was essentially guessing,
because going-together cannot tell "same kind" from "found nearby". I built the missing what-it-IS system
from dictionary definitions and category structure, and it answers that question much better than even a
strong off-the-shelf word-association model -- clearly and repeatably, on human-rated word pairs it was never
tuned on, and it collapses to chance when the definitions are scrambled (so it is really using the meanings).
It also shows the clean brain pattern: the new system is best at "same kind", the old association system is
best at "goes together" -- two different machineries, each winning its own kind of question. I checked the
tempting deeper mechanism the neuroscience suggests (a learned compression of the definition features) and it
did NOT help here -- the simple "weight the rare, telling words more" rule already captures it. And I settled
an apparent contradiction in our own notes: for a plain "how similar are these two words" rating it is better
to BLEND the two systems than to switch between them; switching only pays off when context has to pick a
meaning, which is a different machine we already built.

## QUESTIONS

None blocking. One judgement call for the strategy session: I filed SOLVED because the core bar -- the
conceptual channel beats the associative reader on meaning-IDENTITY CI-separated, off-WordNet, twin losing,
plus the double dissociation -- is met and strengthened against a steelmanned competitor. The routing
sub-clause ("does routing beat fusion?") is a rigorous NEGATIVE (fusion wins for graded rating), which
reconciles the brief with the disk rather than failing the bar; if you would rather see that reflected as
PARTIAL, the identity + dissociation result stands on its own regardless.

## NEXT STEPS

1. Wire the conceptual/definitional channel as a second demand-routed representation (proposed diff above).
2. Route identity/similarity queries to conceptual, relatedness to associative; FUSE for graded rating;
   keep conflict-gated selection in the existing semantic-control organ.
3. Measure on the live reading/coref task before any capability claim.
4. Do NOT pursue (tested-negative / mechanism-approximate): SVD distillation over definitional features; a
   task-switch gate for rating (fusion wins); routing adjectives to the SENSORIMOTOR grounded spoke (loses
   CI-sep); a symbolic antonym-flag as if it were the mechanism; a GPU learned hub over a single spoke.
5. **The mapped frontier (now a WRONG-OPERATION story, mostly buildable from owned resources):** (a) WIRE the
   per-word-class OPERATION ROUTING (noun->overlap, adjective->GloVe+antonym-signed-magnitude, verb->gloss-
   relational) -- highest-leverage, built + directionally validated here, needs only a larger adjective gold
   to reach CI-separation (SimLex has 111 adj pairs -- acquire more, or pool, for the power); (b) a deeper
   VERB argument-structure operation (VerbNet/FrameNet -- the one genuine not-yet-owned resource gap); (c)
   brain-derived feature NORMS (Binder-65/McRae) as a richer noun supply for abstract concepts; (d) only
   AFTER >=2 heterogeneous spokes exist, a learned multimodal hub (then the GPU is the right spend); (e) a
   non-WordNet conceptual channel (Wiktionary) to fully sever provenance.

---

## INTEGRATED_BY_STRATEGY (2026-08-27)

**Grade: EXCELLENT.** Re-verified FIRST-HAND (strategy ran `verification/test_conceptual_meaning_channel.py` -> PASS,
scaffold-free): SimLex conceptual 0.5210 vs steelmanned GloVe 0.3705 (+0.1505 CI[0.0855,0.2149], CI-sep), SimVerb +0.2788,
shuffled-gloss twin loses, IDF beats unweighted overlap CI-sep, double dissociation CI-separated (crossover CI_lo 0.1140;
GloVe wins WordSim relatedness). Bar MET (identity clause, off-WordNet, steelman, twin losing, double dissociation).
Argument adversarially audited and holds: the provenance objection is answered three ways (off-WordNet gold + twin losing +
dissociation asymmetry); gloss content alone ties GloVe (so it is definitional content, not taxonomy lookup); the routing
sub-clause is a reconciling NEGATIVE (fusion ties/beats routing for graded rating -> reconciles the disk's 'fused>switch';
routing's home is context selection = the semantic-control organ); the adjective operation is honestly DIRECTIONAL /
power-limited (n=111) and was correctly not allowed to gate SOLVED. The ATL covariance-distillation ties sparse IDF -> the
distinctive-feature op is SUPPLY-DEPENDENT (dense->whiten, sparse->IDF), a fidelity boundary. Deepest finding (insight):
meaning-similarity is OPERATION-SPECIFIC per word class (one cosine wrong for adjectives=signed-magnitude, verbs=relational).

**hdlab:** NO file landed (Q111 honored). This is p3, the LAST of the 3 in-flight consolidation-gating problems. Per the
consolidation policy the meaning-line landing is QUEUED proven-ready: wire the CONCEPTUAL/definitional channel (per-word
WordNet gloss+genus feature bag, global-IDF distinctive-feature weighted, cosine; default-off, gated on the held-out
SimLex/SimVerb margins) as a second meaning representation; DEMAND-ROUTE (identity->conceptual, relatedness->associative,
FUSE for decontextualised graded rating, conflict-gated SELECTION -> the existing semantic-control organ); OPERATION-ROUTE
the read-out BY WORD CLASS (noun->taxonomic overlap, adjective->GloVe+antonym signed-magnitude, verb->gloss relational). Do
NOT wire the tested-negatives (SVD distillation; task-switch gate for rating; grounded-sensorimotor for adjectives; symbolic
antonym-flag; a GPU hub over one spoke). review: + review_text: + SOLVER REVIEW written to PROBLEM.md; priority cleared;
AUDIT UPDATE folded into BRAIN_FOUNDATIONAL_AUDIT.md (§2b + §6/§7). Committed (no push).

**Consolidation status:** 3 of 3 in-flight now integrated (this + `wire_entity_tracking...` + `discrete_where_the_brain_is_graded...`).
**THE CONSOLIDATION TRIGGER IS MET** -> the CONSOLIDATION PHASE is now ACTIVE (`notes/CONSOLIDATION_PHASE_PLAN.md`),
executed across subsequent focused rounds. NO successor packaged (consolidation policy: the queue has drained to zero, by design).
