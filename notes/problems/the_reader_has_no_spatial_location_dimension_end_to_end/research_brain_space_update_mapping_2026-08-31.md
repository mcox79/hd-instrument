# Research drill — the brain's LANGUAGE→SPATIAL-MODEL update mapping (SPACE dimension)

**Date:** 2026-08-31 · **For:** `the_reader_has_no_spatial_location_dimension_end_to_end`
**Scope:** online literature scan (cite-specific) on the parts of the SPACE build the strategy session is UNSURE about — the language→location-state update computation, robustness under a noisy parse (UAS ~0.79), underspecification/persistence, and categorical/region-hierarchy structure. **Calibration:** lit-scan penalty applied (P deflated 0.15–0.25; novel-synthesis capped at 0.50). Confidences are the drill's read, hypothesis-pending-VET.

**One-line frame:** the already-PINNED design (Zwaan & Radvansky event-indexing SPACE; categorical-topological nodes; Source-Path-Goal with goal dominance; hippocampal allocentric map) is **well-supported by the evidence**. The drill's job is (a) to say *which* pieces are pinned vs open, and (b) for the wall you will hit — weak extraction on real 19c prose — to name the brain mechanism that crosses it, so you know whether the fix is "a better parser" or "a predictive-revision/prior-integration organ." **Headline answer: it is BOTH, but the brain-faithful architecture is prior×likelihood — the parse is noisy EVIDENCE fused with a situation-model PRIOR — so a weak parser is NOT a true ceiling.** See §5.

---

## 1. THE LANGUAGE→SPATIAL-MODEL UPDATE MAPPING

### (a) Source-Path-Goal + the goal-over-source asymmetry

**PINNED-BY-EVIDENCE (with an important refinement):**
- The Source-Path-Goal decomposition of motion (Figure, Ground, Motion, Path) is Talmy's (1985; 2000, *Toward a Cognitive Semantics*) framework and is the correct scaffold. Path is the core schematic element; Source and Goal are its endpoints.
- The **goal-over-source asymmetry is real and robust in BOTH memory and language**: adults and 4-year-olds detect fewer within-category changes to Source objects than Goal objects, and produce fewer Source than Goal references describing the same events; they expect finer lexical distinctions for endpoints (Lakusta & Landau 2005, *Cognition*; Papafragou 2010, *Cognitive Science* 34:1064). It generalizes across event domains — motion, transfer-of-possession, attachment/detachment, change-of-state (Lakusta & Landau 2005). Pre-linguistic infants (~10–14.5 mo) already categorize GOAL paths, and Source paths only when the source is highly salient — so the concept GOAL-PATH precedes the spatial lexicon (Lakusta & Landau 2005/2012).

- **REFINEMENT (this is an AUDIT-relevant correction to the naive "endpoint bias"):** the goal bias is **modulated by intentionality/animacy of the moving figure, not a raw geometric endpoint preference** (Lakusta & Landau 2012, *Cognitive Science* 36:517). Animate, goal-directed agents produce a strong goal bias; inanimate objects being blown/rolled, and "look-back" events where gaze contradicts motion, show **little or no** goal bias in non-linguistic memory. Language nonetheless imposes goal bias *beyond* what memory shows — the linguistic asymmetry persists even where non-linguistic memory is symmetric. Complement: sources are actually **robustly encoded but overlooked at retrieval** — reinstatable under aided recall (Kalénine et al. / "Sources are robustly encoded but overlooked at test," *escholarship*; Ji & Papafragou 2023, *JML* "Sources and goals in memory and language: fragility and robustness").

**Robustness/automaticity verdict:** the goal bias is early, cross-domain, and reliable *for animate intentional motion* (your narrative case — characters moving). It is **NOT** an automatic universal endpoint rule; for inanimate motion it can vanish. **Build implication:** it is brain-faithful to (i) prioritize GOAL extraction, (ii) treat SOURCE as reliably encoded but lower-salience/reinstatable (persist last-known but don't fail if the source PP is missed), and (iii) gate the strength of the goal preference on animacy of the figure — a character "went to the kitchen" pins the goal hard; a ball "rolled off the table" should not over-commit to a goal.

### (b) Deixis as the frame-of-reference selector

**PINNED-BY-EVIDENCE:** deictic verbs and adverbs are anchored to a deictic center (origo): **come = motion toward the deictic center; go = motion away**; here/there and this/that select proximal vs distal relative to the center; return = motion back toward a prior anchored location (Fillmore's *Lectures on Deixis*; Matsumoto et al., *The functional nature of deictic verbs and the coding patterns of Deixis*, Benjamins HCP.59). Deixis is the mechanism that **selects/relocates the reference frame** — in narrative the origo is typically the protagonist's current location (this is exactly the Franklin & Tversky 1990 spatial-framework finding — objects/locations are indexed to the protagonist's body axes and re-indexed as the narrative reorients the observer).

**Build implication:** "came into the room," "went out," "returned" cannot be resolved geometrically — they require the current deictic center (protagonist location = the situation model's current SPACE index). This is a **strength of your architecture**: because you carry per-entity location state, you already hold the origo the deictic verbs need. The tracker *is* the deictic anchor.

### (c) Path off satellites vs the verb — is the brain verb-agnostic?

**PINNED-BY-EVIDENCE (strongly supportive — this is a strength, not a wall):**
- English is **satellite-framed**: Path is carried by the satellite/particle and adpositions ("out," "into," "across," "away"), while the verb typically carries Manner (Talmy 1985/2000). So in "she florped out," Path = departure is read off *out*, and the nonce verb *florped* carries only manner.
- The generalization is underwritten by **construction grammar**: the intransitive-motion / caused-motion CONSTRUCTION supplies the path meaning independent of the verb (Goldberg 1995, *Constructions*). "She sneezed the napkin off the table" gets its caused-motion reading from the construction, not from *sneeze*. The construction is the unit that licenses path from a manner/nonce verb.
- Consistent with noisy-channel/predictive comprehension (§2): the reader predicts a semantic role structure from the construction + adpositions and does **not** require the verb to be a known motion verb.

**Build implication:** extract Path **primarily off the satellites/adpositions + the motion construction**, treating the verb as (usually ignorable) manner. This is **verb-agnostic by design and matches the brain**. It also insulates you from OOV/archaic verbs in 19c prose — the prepositions ("into the parlour," "out of doors," "up the stairs") are stable across the corpus age even when the verbs are dated. This is one of the strongest reasons to expect the SPACE extraction to survive the corpus-age confound better than a verb-lexicon approach would.

---

## 2. ROBUSTNESS / GENERALIZATION UNDER A NOISY PARSE

**This is the load-bearing section for your ceiling-vs-missing-mechanism question.**

**PINNED-BY-EVIDENCE — the brain does NOT rely on a clean local parse:**
- **Noisy-channel comprehension (computational level):** the brain infers the intended message by Bayes-optimally combining a noisy bottom-up signal (likelihood) with a strong prior over plausible meanings — interpretations arise "rationally and gradiently through probabilistic inference" (Levy 2008, EMNLP, *A noisy-channel model of rational human sentence comprehension under uncertain input*; Gibson, Bergen & Piantadosi 2013, *PNAS* 110:8051, *Rational integration of noisy evidence and prior semantic expectations*). Comprehenders even **model the nature of the noise** in the environment (Gibson et al. 2017). Crucially: a locally implausible/misparsed string is repaired *toward the high-prior meaning* — exactly the regime you are in with UAS 0.79.
- **Good-enough processing (algorithmic level):** comprehension uses fast heuristics that yield shallow-but-serviceable representations, tolerating and sometimes ignoring local syntactic detail (Ferreira, Bailey & Ferraro 2002, *Good-enough representations*; Ferreira & Patson 2007). Levy-style noisy-channel and good-enough are **compatible** — good-enough heuristics approximate the Bayes-optimal inference (they target different Marr levels). Both say: **local syntax is not sacred; meaning is recovered by prior-weighted inference.**
- **Predictive/incremental revision:** comprehension is incremental and predictive; readers pre-activate upcoming semantic content (N400 as a prediction-error signal — Kutas & Federmeier 2011), detect inconsistency, **disconfirm and revise** predictive inferences, and recover from garden paths (situation-model revision literature; Chinese narrative predictive-inference revision, *PMC11486713*). Garden-path recovery is the canonical proof that the reader re-analyzes when bottom-up input contradicts the running model.
- **Hippocampal implementation of prior×likelihood:** CA3 performs **pattern completion** — retrieving a full associated representation (here: the location/event) from a partial or degraded cue after minimal learning (canonical CA3 attractor). And **prediction errors disrupt sustained hippocampal representations and drive updating** — greater hippocampal activation preserves memory after expected continuations but *updates* it after surprising ones (Sinclair et al. 2021, *PNAS* 118, *Prediction errors disrupt hippocampal representations and update episodic memories*; Nature Comms 2022, hippocampal representations switch from errors to predictions during learning). The hippocampus is the organ that fills in a location from a partial cue and revises it on surprise.

**The synthesis (NOVEL for this project — P ≤ 0.50, hypothesis-pending-VET):** the brain-faithful spatial-update architecture is **posterior ∝ prior × likelihood**, where the parse is the *likelihood/evidence term* (noisy, weightable) and the running situation model + event schema is the *prior*, with hippocampal pattern-completion doing the fill-in and prediction-error doing the revision. Under this model, **a weak local parse is not a ceiling — it degrades the likelihood term, which a strong prior can compensate for.** Two concrete levers therefore cross the wall, and they are complementary:
1. **A better parser** (the incremental parser, problem p2) — raises the *likelihood* precision. Real, but diminishing: the brain wins with a noisy front-end.
2. **A predictive-revision / prior-integration layer** — fuses parse output *as evidence* with the situation-model prior (last-known location, plausibility of the destination given the scene/region graph, deictic origo), plus a prediction-error revise step. **This is the higher-fidelity lever** and it is currently absent (the adapter treats the parse as ground truth, not as evidence).

**Discriminating test to say which:** run the SPACE extraction two ways — (i) parse-as-truth (current adapter), (ii) parse-as-evidence with a situation-model prior (last-location persistence + region-plausibility + goal-preference weighting). If (ii) recovers where-is accuracy on the parse-error subset where (i) fails, the wall is a **missing predictive-revision mechanism**, not merely a weak parser — and the fix is an organ, not just p2. If (ii) does not help on that subset, the residual is genuinely a likelihood-term (parser) limit and it points cleanly at p2. **This is the experiment that tells you which claim to write in the negative-result branch of your bar (§7 of PROBLEM.md).**

---

## 3. UNDERSPECIFICATION & PERSISTENCE ("carry the state," off-stage, decay)

**PINNED-BY-EVIDENCE:**
- **Persistence is the event-indexing default.** Zwaan & Radvansky (1998, *Psych. Bulletin* 123:162) — the situation model carries five indices (time, space, causation, intentionality, protagonist); the SPACE index **persists as state and is updated only when the text signals a change**. Not restating a location does not clear it. Your "carry the state" property is the pinned behavior.
- **Accessibility decays with distance — the graded signature you want.** Rinck & Bower (1995; 2000, *Memory & Cognition*, *Temporal and spatial distance in situation models*): a **spatial gradient of accessibility** — objects/locations further (in the mental map) from the protagonist's focus are read/verified more slowly; anaphor resolution degrades with spatial *and* temporal distance. Bower & Morrow's map-based studies show the "spotlight" of attention moves with the protagonist and accessibility falls off with map distance. **This directly predicts your distance curve (accuracy vs #intervening events) and it is the correct brain-faithful discriminator.**
- **Event boundaries flush/reorganize the working model — the mechanism behind graded decay.** Event Segmentation Theory (Zacks, Speer, Swallow, Braver, Reynolds 2007, *Psych. Bulletin*; Speer, Reynolds, Swallow & Zacks 2009). Event boundaries occur precisely at feature *changes* — time, **space**, objects, characters, goals, causes — and readers update at those boundaries (Speer & Zacks; "Attentional focus affects how events are segmented," 2017; readers oriented to space are more likely to update at spatial changes). At a boundary the current model is closed and a new one opened — so information across a boundary is **less accessible**, giving the graceful decay.
- **Hippocampal binding is the substrate for both persistence and decay.** The hippocampus obligatorily **binds disparate elements across space and time** and maintains relational bindings even over short retention (Cohen & Eichenbaum relational-memory account; Frontiers 2012, *hippocampus supports multiple cognitive processes through relational binding and comparison*; short-term relational retention depends on hippocampal integrity, *PMC3901041*). Event-boundary **offset** hippocampal–posterior-medial connectivity predicts how much event detail is retained after a 2-day delay (biorxiv 2022 / PubMed 37944517) — the neural correlate of "state survives across events, but graded." Renoult & Rugg-style work situates this in the episodic/relational memory system.

**OPEN / thin in the literature (flag honestly):**
- **Explicit representation of an UNKNOWN / off-stage location.** The literature robustly covers *persistence of a known* location and *accessibility decay*, but there is **little direct experimental work on how the reader represents "departed to an unnamed place / current location unknown."** The defensible inference: the entity's SPACE index becomes **un-bound from the current region** (a placeholder "elsewhere/UNKNOWN," not a forced node), retrievable via pattern completion when re-mentioned — but this is a synthesis (P ≤ 0.45), not a pinned empirical result. **Build implication:** represent UNKNOWN *explicitly*; do NOT force an entity onto a node when the text only says "he left." Abstaining-with-persistence (last-known region held at lowered confidence) is the brain-faithful behavior and also the honest read-out.

---

## 4. CATEGORICAL vs METRIC + REGION HIERARCHY

**PINNED-BY-EVIDENCE (confirms your pinned representation):**
- **Narrative space is categorical/topological, not metric.** Rinck & Bower and Rinck (1997) map-based situation-model work: readers reason over the *mental map's* rooms/regions (categorical relations, containment, connectivity), and distance effects are over that map, not over veridical coordinates. This connects to Kosslyn's (1987) categorical-vs-coordinate spatial-relation distinction (categorical = "in/on/left-of," left-hemisphere-biased; coordinate = metric, right-biased) — narrative comprehension runs mostly on the *categorical* system. **Your categorical-topological-node representation is the pinned-correct choice.**
- **Space is organized into nested REGIONS, and this is hierarchical in the brain.** Hirtle & Jonides (1985, *Memory & Cognition*, *Evidence of hierarchies in cognitive maps*) — people cluster landmarks into hierarchical regions; the clustering distorts distance/direction judgments (an item is judged closer to same-region than cross-region items even when metrically equal). Wiener & Mallot (2003, *fine-to-coarse route planning in regionalized environments*) — navigation planning uses region hierarchy. Recent fMRI confirms **hierarchical cognitive maps for nested spaces (rooms ⊂ buildings ⊂ neighborhoods) in the human brain** (bioRxiv 2025 / *PMC12452280*). Hierarchical coding shows up in directional judgments, position/distance estimates, free recall, and navigational planning.
- **Containment inference IS a cognitive-map operation.** "Is X in the house?" is **transitive region membership on the region hierarchy** — if X is in the parlour and the parlour ⊂ the house, then X is in the house. This is exactly the fine-to-coarse hierarchical query Wiener & Mallot and the hierarchical-map work describe. It is pinned as a *structural* operation (graph reachability on the region tree), though direct *narrative-comprehension* experiments that probe containment queries specifically are thinner than the navigation literature (mark the narrative-specific evidence as MEDIUM, the structural operation as PINNED).

**Build implication:** keep the categorical nodes; give them a **containment/region parent-pointer tree**; answer "is X in the house?" by reachability up the tree from X's current node. Distance-in-the-curve should be measured in **map/region steps or intervening events**, not tokens — that is the brain's metric.

---

## 5. THE WALLS YOU WILL HIT → the brain mechanism that crosses each (most important)

| Wall (on real 19c prose) | Is it a true ceiling? | Brain mechanism that crosses it | Points the fix at… |
|---|---|---|---|
| **Weak local parse (UAS 0.79) misattaches the path PP / drops the goal** | **NO** | Noisy-channel prior×likelihood (Levy 2008; Gibson 2013) + CA3 pattern completion + prediction-error revision (Sinclair 2021). The brain treats the parse as *evidence*, not truth, and repairs toward the high-prior meaning. | **Both, but primarily a NEW predictive-revision/prior-integration organ** (fuse parse-as-evidence with last-location + region-plausibility + goal-weighting + a revise-on-surprise step). A better parser (p2) raises the *likelihood* term — real but secondary. **Run the parse-as-truth vs parse-as-evidence discriminator (§2) to prove which.** |
| **OOV / archaic manner verb ("she florped out"; dated 19c motion verbs)** | **NO** | Satellite-framed path reading (Talmy) + motion CONSTRUCTION supplies path independent of the verb (Goldberg 1995). Prepositions are age-stable. | Extraction design: read path off **satellites/adpositions + construction**, verb as ignorable manner. Not a parser problem; a mapping-design choice. Also *mitigates* the McGuffey corpus-age confound. |
| **Deictic move with no explicit goal ("he came in," "she returned")** | **NO** | Deixis selects the reference frame; origo = protagonist's current SPACE index (Fillmore; Franklin & Tversky 1990). You already hold the origo as state. | Use the tracker's current-location state as the deictic anchor. A strength of the architecture. |
| **Entity departs to an unnamed place ("he left the house")** | Partly OPEN | Un-bind from current region → explicit UNKNOWN placeholder; persist last-known at lowered confidence; pattern-complete on re-mention. | Read-out design: represent + report UNKNOWN explicitly; abstain-with-persistence, don't force a node. (Synthesis, P≤0.45 — VET.) |
| **Location not restated for many sentences; accuracy expected to fall** | It SHOULD fall — that's the signal | Persistence (Zwaan & Radvansky) + accessibility decay with map/event distance (Rinck & Bower) + event-boundary reorganization (Zacks/Speer) + hippocampal-boundary retention (biorxiv 2022). | Measure the **distance curve** in region-steps / #intervening events (not tokens). Graceful decay = a PASS-shaped brain signature, not a failure. |
| **Inanimate motion over-committing to a goal ("the ball rolled off")** | It's a fidelity trap | Goal bias is **intentionality-modulated** (Lakusta & Landau 2012) — animate agents pin goals; inanimate motion does not. | Gate goal-preference strength on figure animacy. (AUDIT refinement — see below.) |

---

## 6. PINNED vs OPEN — summary ledger

**PINNED-BY-EVIDENCE (build on these):**
- Persistence of the SPACE index as state, updated only by motion (Zwaan & Radvansky 1998). ✅ matches PROBLEM.md.
- Goal-dominant Source-Path-Goal reading (Talmy; Lakusta & Landau 2005; Papafragou 2010). ✅ — with the animacy-modulation refinement below.
- Verb-agnostic, satellite/construction-based path extraction (Talmy 1985; Goldberg 1995). ✅ NEW support — a strength vs the corpus-age confound.
- Deixis = reference-frame/origo selection, origo = protagonist location (Fillmore; Franklin & Tversky 1990). ✅
- Categorical/topological space with nested regions + transitive containment (Rinck 1997; Hirtle & Jonides 1985; Wiener & Mallot 2003; hierarchical-map fMRI 2025). ✅ matches PROBLEM.md.
- Accessibility/decay gradient with map + event distance; event boundaries reorganize the model (Rinck & Bower 1995/2000; Zacks/Speer 2007/2009). ✅ this is your distance-curve discriminator.
- Hippocampal pattern completion + prediction-error updating as the neural substrate (Sinclair 2021; CA3 attractor; relational binding). ✅

**OPEN / to decide or VET:**
- **[HIGH VALUE]** Is the weak-parse wall a ceiling or a missing predictive-revision organ? → **Discriminator experiment in §2** (parse-as-truth vs parse-as-evidence-with-prior on the parse-error subset). This decides whether SPACE waits on p2 or gets a new fusion organ. P(prior-integration meaningfully helps) ≈ 0.45–0.50 — VET.
- Explicit UNKNOWN/off-stage representation is a synthesis, not a pinned empirical result (P≈0.45) — VET on your gold.
- Narrative-specific containment-query evidence is thinner than navigation evidence (structural operation PINNED; narrative probe MEDIUM).

**AUDIT UPDATE (for `BRAIN_FOUNDATIONAL_AUDIT.md` §2b):** the pinned claim "Source-Path-Goal with GOAL dominant" should be refined — **the goal-over-source asymmetry is intentionality/animacy-MODULATED (Lakusta & Landau 2012, *Cog Sci* 36:517), not a raw geometric endpoint bias.** Robust for animate/intentional figures (the narrative-character case), weak/absent for inanimate motion; and sources are *encoded-but-overlooked* (reinstatable, Ji & Papafragou 2023 *JML*), so a missed source PP should lower confidence, not erase the source. Recommend the adapter gate goal-preference strength on figure animacy and treat source as persist-but-low-salience.

---

## TLDR (plain English)
When a person reads "Mary went into the kitchen," their brain does not depend on a perfect grammatical analysis of the sentence — it combines a rough, error-prone reading of the words with a strong expectation of what makes sense given where everyone already is, and fills in the gap the way memory completes a half-remembered scene. It keeps each character's location in mind even when the story stops mentioning it, and lets that memory fade gently the more that happens in between. It reads "where did they go" mostly off the little direction words ("into," "out," "up the stairs") rather than the main verb, which is why it still understands an unfamiliar or old-fashioned verb. The map it keeps is a set of rooms-inside-buildings, not exact distances, so "is she in the house?" is answered by checking whether her room is part of the house. **The practical upshot for the build: our weak sentence-parser is probably NOT a hard ceiling. The brain gets by with a noisy parser by leaning on memory and expectation, and we are missing exactly that "lean on the running story" layer. There is one clean experiment that tells us whether to build that layer or just wait for the better parser — run the location extractor twice, once trusting the parse and once treating the parse as a hint on top of last-known location, and see which one recovers the cases the parse gets wrong.** One correction to our current assumption: the "characters care more about where they end up than where they started" rule only holds for people/animals moving on purpose — for objects (a ball rolling) it doesn't, so we should turn that preference on only for animate movers.

## QUESTIONS
None blocking. One judgment call for the owner/strategy, framed in §2: whether to build the predictive-revision/prior-integration layer *inside this problem* (it converts the weak-parser negative branch into a positive result) or to keep this problem scoped to parse-as-truth and let the negative branch cleanly hand SPACE to the parser work (p2). The drill's recommendation is to at least run the cheap discriminator (§2) before writing the negative branch, because it changes what the negative *means*.

## NEXT STEPS
1. Build the SPACE extraction two ways and run the **§2 discriminator** (parse-as-truth vs parse-as-evidence-with-situation-model-prior) on the parse-error subset — this decides "ceiling vs missing organ" with evidence, and is the highest-value adjacent measurement.
2. Read **Path off satellites/adpositions + the motion construction**, verb as ignorable manner (Talmy/Goldberg) — most robust to the McGuffey corpus-age confound; also add a modern held-out passage set.
3. Represent **UNKNOWN/off-stage explicitly** (un-bind + persist-at-lowered-confidence), and gate **goal-preference on figure animacy** (the §6 AUDIT refinement).
4. Measure the **distance curve in region-steps / #intervening events** (Rinck & Bower / Zacks-Speer signature), not tokens — the brain-faithful discriminator and the graded PASS shape.
5. Fold the §6 **AUDIT UPDATE** (animacy-modulated goal bias) into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

---

### Key sources
- Talmy (1985; 2000) *Toward a Cognitive Semantics* — Figure/Ground/Motion/Path; verb- vs satellite-framing; satellites.
- Lakusta & Landau (2005, *Cognition*) — goal-over-source mapping bias, cross-domain.
- Lakusta & Landau (2012, *Cognitive Science* 36:517) — goal bias is intentionality/animacy-modulated; pre-linguistic; not a raw endpoint bias.
- Papafragou (2010, *Cognitive Science* 34:1064) — source-goal asymmetry in production AND comprehension.
- Ji & Papafragou (2023, *JML*) / "Sources robustly encoded but overlooked at test" — sources encoded, reinstatable.
- Goldberg (1995) *Constructions* — construction supplies path independent of the verb.
- Fillmore, *Lectures on Deixis*; Matsumoto et al. (Benjamins HCP.59) — come/go/here/there deictic center.
- Franklin & Tversky (1990) — spatial framework; protagonist-anchored accessibility.
- Levy (2008, EMNLP) — noisy-channel rational comprehension under uncertain input.
- Gibson, Bergen & Piantadosi (2013, *PNAS* 110:8051) — rational integration of noisy evidence + prior.
- Ferreira, Bailey & Ferraro (2002); Ferreira & Patson (2007) — good-enough processing.
- Kutas & Federmeier (2011) — N400 as prediction/prediction-error index.
- Sinclair et al. (2021, *PNAS* 118) — prediction errors disrupt hippocampal representations and update episodic memory; CA3 pattern completion.
- Zwaan & Radvansky (1998, *Psych. Bulletin* 123:162) — event-indexing model; SPACE index persistence.
- Rinck & Bower (1995; 2000, *Memory & Cognition*) — spatial-distance gradient of accessibility in situation models; Rinck (1997) categorical narrative space.
- Zacks, Speer, Swallow, Braver & Reynolds (2007, *Psych. Bulletin*); Speer, Reynolds, Swallow & Zacks (2009) — Event Segmentation Theory; spatial-change boundaries.
- Hirtle & Jonides (1985, *Memory & Cognition*) — hierarchies in cognitive maps.
- Wiener & Mallot (2003) — fine-to-coarse region-based route planning.
- Hierarchical cognitive maps for nested spaces, human fMRI (bioRxiv 2025 / PMC12452280).
- Hippocampal relational binding (Frontiers 2012); event-boundary offset connectivity → retention (biorxiv 2022 / PubMed 37944517).
