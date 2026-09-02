# Brain-fidelity wall-drill + adjacent-component evaluation

Solver deliverable for `the_19c_who_did_what_lever_is_agent_composed_thematic_fit_on_a_cleaned_gold`, answering the
owner's two questions: **"how does the brain do it EXACTLY, where do we differ PRECISELY?"** and **"understand the
capabilities/limitations/opportunities/brain-foundational status of adjacent components to plan the next problems."**
Every claim is either measured on disk (this problem's cells) or cited from the two research drills
(`BRAIN_MECHANISM_DRILL_composition_prediction.md`), which verified all load-bearing citations live.

---

## PART 1 -- THE WALLS, DRILLED (brain mechanism EXACTLY; where WE differ PRECISELY)

### WALL 1 -- Linear position dominates who-did-what SELECTION on canonical direct objects (0.918)
- **How the brain does it, exactly:** Competition Model (MacWhinney & Bates; MacWhinney, Bates & Kliegl 1984).
  Who-did-what is GRADED, PARALLEL cue integration with LEARNED VALIDITIES; in English, word ORDER has the highest
  validity -- when order conflicts with animacy, English speakers follow ORDER (case-marking languages follow
  morphology). Thematic fit is a LOW-validity cue that surfaces only when order is ambiguous/marked.
- **Where we differ: WE DON'T -- this is a MATCH, not a gap.** Our position dominance and the live
  `hdlab/graded_role_assigner` (order-dominant + marked-cue override, validities fit by logistic regression) are
  faithful to the cue hierarchy. The "wall" was a mis-framed test (selection accuracy on the regime where order is
  the correct cue), not an implementation deficit.

### WALL 2 -- Agent x verb composition ties its twin as a SELECTOR, but is real as PREDICTION
- **How the brain does it, exactly:** the Bicknell 2010 / Chersoni agent x verb effect is measured as reading-time /
  N400 (forward PREDICTION / pre-activation -- Altmann & Kamide 1999 fire anticipatory looks to the plausible object
  ~200ms before it is read), on items where SYNTAX ALREADY FIXES the object. Thematic fit changes the SELECTION/parse
  only at points of SYNTACTIC AMBIGUITY (McRae, Spivey-Knowlton & Tanenhaus 1998, reduced relatives).
- **Where we differ: instrument, not mechanism.** We measured composition as which-noun SELECTION on 100%-active
  canonical DOs (no ambiguity), where the brain uses order, not fit. On the brain's ACTUAL instrument (held-out
  forward prediction, MRR) composition IS real: +0.0322 over marginal CI-sep, +0.0403 over agent-shuffle CI-sep
  (`exp_19c_composition_as_prediction_v1`, n=4000). No mechanism gap; it was graded on the wrong test.

### WALL 3 -- Composition ties its twin in the 12-d grounded space, works in the 100-d PPMI space
- **How the brain does it, exactly (TWO dimensionalities -- the key precision):**
  1. **Binding ALGEBRA** (role (X) filler conjunction). The brain encodes who-did-what via conjunctive role-filler
     coding in left mid-superior temporal cortex (Frankland & Greene 2015, PNAS -- distinct agent/patient subregion
     patterns). This is HIGH-D and is NOT the bottleneck; our FHRR/VSA binding is already high-D and faithful.
  2. **Filler CONTENT** (the vector for "mechanic" vs "journalist"). Fine conceptual individuation lives in the
     high-D transmodal ATL HUB, NOT the low-D sensorimotor SPOKES (Controlled Semantic Cognition; Lambon Ralph 2017,
     Nat Rev Neurosci). In a spoke, "mechanic" and "journalist" are near-collinear (both animate human agents), so
     conditioning on the agent adds no information.
- **Where we differ, PRECISELY:** our forward-prediction organ (`hdlab/predictive_reader`) computes thematic fit over
  a 12-d sensorimotor SPOKE (Lancaster 11-d: 6 perceptual + 5 action). That is the wrong basis for the agent x verb
  CONJUNCTION -- too coarse to carry agent identity. Measured: in the 12-d grounded space composition ties its
  agent-shuffle twin (+0.0022 ns) and even HURTS vs exemplar-marginal (-0.036); in a 100-d register-native PPMI-SVD
  space (a HUB proxy -- the distributional stream carries the relational structure grounding lacks, Andrews/Vigliocco
  complementarity) composition is real (+0.0395 vs agent-shuffle CI-sep) and the composed-exemplar beats the organ's
  centroid-marginal +0.0140 CI-sep (`exp_predictive_reader_composition_upgrade_v1`, n=4000). **The differ is
  REPRESENTATIONAL (spoke used where a hub is required), NOT algebraic. Remedy: feed hub-grade high-D fillers into the
  conjunction; KEEP FHRR.** (Exemplar>centroid in low-D but centroid~=exemplar in high-D is also brain-consistent: a
  centroid collapses a role's multimodal filler clusters catastrophically only in low-D -- Erk 2010; near-orthogonality
  in high-D lets the centroid retain structure; composed-exemplar-best = instance-based conjunctive conditioning, CLS.)

### WALL 4 -- The canonical-DO residual is 89% structural (NP-head), not semantic
- **How the brain does it, exactly:** NP head-finding (compound Right-hand Head Rule, Williams 1981; genitive
  DP-head) is a SYNTACTIC operation that PRECEDES thematic role assignment -- a different computation at a different
  level. A thematic-fit store cannot repair a head-selection error.
- **Where we differ:** our positional selector picks the nearest post-verbal noun = the FIRST token of the NP
  ("a trade delivery VAN" -> `trade`; "the undertaker's SHOP" -> `undertaker`). The brain picks the HEAD. Measured:
  an NP-head-aware selector beats nearest +0.0433 CI-sep, reaching 0.9611 (`exp_19c_whodidwhat_residual_taxonomy_v1`).
  Gap = no NP-head chunker (compound + genitive). Buildable, structural, brain-independent.

### WALL 5 -- Morphological CASE is a high-validity cue we do NOT use (the missed lever, 19c-matched)
- **How the brain does it, exactly:** morphological case (nominative/accusative pronouns he/him, she/her, they/them;
  and who/whom) is the HIGHEST-validity Competition-Model cue WHERE IT EXISTS -- morphology OVERRIDES word order.
  It resolves position-ambiguous who-did-what (fronted / relative-clause patients) WITHOUT needing thematic fit.
- **Where we differ:** verified on disk -- `hdlab/graded_role_assigner` cue set is
  `[order, adjacency, passive_strong, passive_weak, gap, unacc, byagent, animacy]` -- **no case cue.** And 19c prose
  PRESERVES "whom"/pronoun case far better than modern text, so this cue is MORE available in the target register
  than anywhere else. Cheap surface cue, NOT in the organ's named residual. **This is the strongest fundable
  who-did-what SELECTION lever the sweep found.**

### WALL 6 -- Non-canonical (passive / reduced-relative) who-did-what
- **How the brain does it, exactly:** the same graded cue integration; voice morphology and filler-gap override order
  on marked constructions; reduced relatives need verb subcategorization frames + incremental clause segmentation.
- **Where we differ: mostly covered.** `hdlab/graded_role_assigner` already does the marked-construction override
  (validated: non-canonical slice 0.60 vs 0.5758 +0.024 CI-sep). Its residual is UPSTREAM, and the organ names it:
  verb-subcategorization SUPPLY (from WordNet frames), the incremental clause structure-builder, and an unwired coref
  organ. (This is why a 19c passive build would DUPLICATE existing work -- confirmed, and dropped.)

**No large uncovered who-did-what comprehension lever exists** (both drills swept it): Construction Grammar (Goldberg)
is a reframing of the syntactic cue; discourse/referential event-model (Altmann-Kamide, Metusalem) lives in the same
forward-prediction pathway; cue-based retrieval interference (Lewis & Vasishth 2005, ACT-R) is a real DISTINCT error
mechanism for long/embedded 19c sentences but is mechanism-heavy -- log it, don't fund near-term.

---

## PART 2 -- ADJACENT COMPONENTS (capability / limitation / brain-fidelity / opportunity -> next problems)

| organ | brain frame + fidelity | limitation (measured/named) | opportunity -> candidate next problem |
|---|---|---|---|
| **`predictive_reader`** (forward prediction, landed EXCELLENT) | PINNED-faithful in FORM (Altmann-Kamide pre-activation; Levy/Hale surprisal = -log P). | Predicts from the **marginal, role-specific CENTROID over a 12-d sensorimotor SPOKE** -- no agent-composition; filler content too coarse for the conjunction (WALL 3). | **Upgrade to agent-COMPOSED EXEMPLAR over HUB-grade (register-native, high-D) fillers.** Measured gain +0.0140 MRR CI-sep over the organ's method; keep FHRR. This is the brain-faithful HOME of composition. |
| **`graded_role_assigner`** (Competition-Model role assignment, landed EXCELLENT) | PINNED-faithful (MacWhinney-Bates graded cue integration; order-dominant + marked override). HIGH fidelity. | Cue set has **no morphological CASE cue** (WALL 5); reduced-relative residual is upstream (subcat/segmentation/coref). | **Add the morphological-case cue** (he/him, who/whom) -- highest-validity, surface-cheap, MORE available in 19c. Cleanest fundable selection lever. |
| **`verb_role_exemplar_selector`** (the exemplar store, p3/p5, landed) | PINNED-faithful (McRae exemplar / instance distribution). | DOMAIN-BOUND to modern prose (ties its twin on 19c/OOD, its own finding); as a STANDALONE selector it is dominated by position on canonical DOs (this problem). | Its value is (a) as a graded PREDICTION store (via `predictive_reader`, WALL 3) and (b) on the non-canonical slice via `graded_role_assigner`; **NP-head chunking upstream** would stop it mis-picking compound modifiers. |
| **`n400_coherence_monitor`** (event segmentation, ORGAN F5, landed EXCELLENT) | PINNED-faithful (Event Segmentation Theory; N400 = graded coherence error vs running situation gist). | Backward-looking EVENT level; consumes a forward-prediction surprisal that is currently coarse (marginal centroid). | Indirect: a better forward predictor (composed-exemplar, hub-grade fillers) yields a sharper surprisal -> better N400 boundary confidence. |
| **NP-head chunker** (does not exist) | Compound Right-hand Head Rule (Williams 1981) + genitive DP-head -- syntactic, precedes role assignment. | 89% of the clean-DO who-did-what residual; no organ finds NP heads. | **Build an NP-head selector** (compound + genitive head). Measured +0.0433 CI-sep -> 0.9611; helps every downstream selector. |

### Candidate next problems, ranked by leverage x cheapness x brain-fidelity
1. **Morphological-case cue in `graded_role_assigner`** -- cheap, highest-validity, register-matched (19c preserves
   whom/case). The best sweep find; verified absent on disk.
2. **NP-head chunker** (compound + genitive head selection) -- structural, +0.043 CI-sep, helps all selectors, and
   is THE lever for clean 19c who-did-what selection (89% of the residual).
3. **Hub-grade filler representation + agent-composed exemplar for `predictive_reader`** -- the brain-faithful home
   of composition (+0.014 CI-sep measured), a REPRESENTATION swap (spoke->hub proxy), keep FHRR.
4. **(log, do not fund near-term)** cue-based retrieval interference (Lewis-Vasishth ACT-R) for long/embedded 19c
   sentences; verb-subcategorization SUPPLY from WordNet frames (already named by `graded_role_assigner`).

---

## PART 3 -- OPTIMIZATION HEADROOM (measured; `exp_composition_representation_optimization_v1`)

The brain-fidelity finding ("composition is representation-bounded -- spoke fails, hub works") makes a falsifiable
optimization prediction: the composition margin should GROW with representational capacity. It does -- a clean
dose-response (held-out prediction MRR; agent-shuffle margin; n=4000):

| filler representation | MRR | COMPOSED - AGENT-SHUFFLE |
|---|---|---|
| 12-d grounded sensorimotor (SPOKE -- the organ's current basis) | 0.0594 | +0.0022 **ns (dead)** |
| PPMI-SVD dim 25 | 0.1062 | +0.0224 CI-sep |
| PPMI-SVD dim 50 | 0.1377 | +0.0339 CI-sep |
| PPMI-SVD dim 100 | 0.1590 | +0.0403 CI-sep |
| **PPMI-SVD dim 200** | **0.1638** | +0.0442 CI-sep |
| PPMI-SVD dim 300 | 0.1623 | +0.0456 CI-sep |

**Optimizations, with numbers:**
1. **Swap the 12-d sensorimotor SPOKE for a ~200-d register-native distributional HUB proxy.** This is the big
   lever: MRR 0.059 -> 0.164 (2.8x) and the composition margin 0.002 (dead) -> 0.044 (CI-sep). The margin doubles
   from dim-25 to dim-300 and MRR peaks at ~200 then plateaus -- so ~200 dims is the efficient operating point
   (300 adds noise dims, MRR dips to 0.162). This CONFIRMS "representation is the bottleneck, not the mechanism."
2. **gamma (agent-weight sharpness) ~3.0**, not the default 2.0: margin +0.0483 vs +0.0456. Small, free.
3. **Do NOT naively concatenate spoke+hub.** Measured: HUBSPOKE_concat MRR 0.1167 < HUB-alone 0.1540 -- the coarse
   near-collinear spoke dims DILUTE the hub. Brain-faithful reading: the ATL hub is a DEEP transmodal integration of
   the spokes (Lambon Ralph 2017), not a vector concatenation; use the hub-grade distributional representation, do
   not bolt the raw sensorimotor spoke onto it. (An honest negative that sharpens the "hub, not concat" recommendation.)

### THE IDEAL PREDICTOR, ASSEMBLED (`exp_ideal_composed_predictor_v1`) -- brain-faithful ablation ladder
All ingredients composed into the best configuration and decomposed so each earns its keep (held-out patient
prediction MRR, n=4000; the verb sets the prior, the agent sharpens it -- centroid-marginal base with agent-composed
exemplar sharpening that backs off to the base when the agent is OOV; gamma=2 = MRR-optimal):

| rung | configuration | MRR | increment |
|---|---|---|---|
| R0 ORGAN TODAY | 12-d spoke + centroid + marginal (`predictive_reader` now) | 0.0630 | -- |
| R1 +HUB | 200-d register-native hub + centroid + marginal | 0.1381 | **+0.0751 CI-sep** |
| R2 +exemplar (diagnostic) | hub + exemplar-marginal | 0.1183 | -0.0198 NEG (drop) |
| **R3 IDEAL** | hub + centroid base + agent-COMPOSED exemplar sharpening | **0.1400** | +0.0217 CI-sep over R2 |
| R4 +WordNet smooth | IDEAL + taxonomic OOV back-off | 0.1354 | -0.0046 NEG (drop) |
| control: agent-shuffle twin | | 0.1219 | IDEAL beats it +0.0181 CI-sep |
| control: verb-shuffle twin | | 0.0323 | IDEAL beats it +0.1077 CI-sep |

**IDEAL vs ORGAN = +0.0771 CI[+0.067,+0.087] CI-sep -- a 2.2x held-out prediction MRR.** The honest decomposition:
- **The REPRESENTATION swap (12-d sensorimotor spoke -> 200-d register-native distributional hub) is essentially the
  ENTIRE gain (+0.075 of +0.077).** This is the star; it is what turns the coarse spoke into a hub-grade filler code.
- **Composition is real WHERE IT FIRES** (beats its agent-shuffle twin +0.018 CI-sep; fires on 43% of triples -- the
  fraction with an in-vocabulary agent) **but its NET gain over the strong hub-CENTROID base is small (+0.002 ns on
  the full set).** Composition is a modest topping bounded by agent coverage, not the lever.
- **Two intuitive ingredients are DEAD ENDS here and must be dropped:** exemplar-marginal HURTS (-0.020; in a high-D
  hub the centroid is already expressive -- near-orthogonality preserves cluster structure, Erk 2010), and WordNet
  taxonomic smoothing HURTS (-0.005; adds noise to already-covered fillers).

### DRILLING THE "composition net gain is small" WALL -> it was an ESTIMATOR weakness, and the brain's fix crosses it
The IDEAL showed raw agent-composition adds ~0 net over the strong hub-centroid base (+0.002 ns). Drilled
(`exp_composition_diagnosticity_v1`, gold-blind binning by how much the agent moves the prediction): raw composition
HELPS where the agent barely shifts the verb prior (LOW/MID shift +0.012 / +0.015 CI-sep) but HURTS where it shifts
a lot (HIGH shift -0.013) -- sparse (agent,verb) evidence lets the estimator OVER-COMMIT to a spurious direction.
That is an under-regularization, not a ceiling. The brain-faithful fix is PRECISION-WEIGHTING (Friston free-energy
precision; Kleinschmidt-Jaeger ideal-adapter reliability weighting; and the `predictive_reader` organ's OWN stated
principle "precision-weighted by the verb's selectional-preference concentration" -- which the raw estimator did not
implement): trust the agent shift in proportion to the PRECISION of its evidence (peak agent similarity), and shrink
to the verb prior when no close agent was attested. `score = (1-lam)*centroid + lam*composed`, `lam =
clip((peak_agent_cos - 0.20)/0.35, 0, 1)`.

Result (`exp_composition_precision_weighted_v1`, agent-covered held-out, n=4404): **PRECISION_BLEND beats the
verb-prior centroid base +0.0140 CI[+0.009,+0.020] CI-sep** (raw composition was +0.005 ns -- precision-weighting
~TRIPLED the net gain), beats raw composition +0.009 CI-sep, beats its agent-shuffle twin +0.032 CI-sep; and the
HIGH-shift damage is REMOVED (-0.013 -> +0.004 ns) while LOW/MID gains hold (+0.011 / +0.027 CI-sep). **The
capability is real once regularized the brain's way; the wall was the missing precision term.**

**Net for the `predictive_reader` upgrade next-problem (final recipe):** (1) the dominant win is the REPRESENTATION
swap (12-d sensorimotor spoke -> ~200-d register-native distributional hub, held-out prediction MRR 0.063 -> 0.140,
2.2x); (2) add PRECISION-WEIGHTED agent-composed exemplar sharpening (blend to the verb-prior centroid by peak-agent
precision; gamma 2) -- a real net topping +0.014 CI-sep on the ~43% of inputs with an in-vocab agent, where the RAW
estimator was null-and-sometimes-harmful; (3) do NOT use exemplar-marginal or WordNet smoothing (both hurt). KEEP
FHRR. Every ingredient controlled, decomposed, and each earns its keep or is dropped.

### THE RECIPE, ASSEMBLED AND PROVEN (`exp_ideal_recipe_v1` -- a reusable `IdealComposedPredictor` class)
The whole recipe written as one drop-in predictor (`fit(exposure_triples)` -> `score_pool(verb, agent, ...)`;
hub representation + verb-prior centroid base + precision-weighted agent-composed sharpening + centroid backoff) and
PROVEN end-to-end on held-out forward prediction (n=3429-3769; every contrast CI-separated):

| arm | MRR | hit@1 | hit@10 |
|---|---|---|---|
| ORGAN (12-d spoke + centroid) -- today | 0.0626 | 0.026 | 0.116 |
| + HUB representation | 0.1382 | 0.079 | 0.238 |
| + raw composition | 0.1414 | 0.082 | 0.248 |
| **IDEAL (+ precision-weighting)** | **0.1451** | **0.084** | 0.249 |
| control: agent-shuffle twin | 0.1303 | | |
| control: verb-shuffle twin | 0.0312 | | |

- **IDEAL vs ORGAN = +0.083 CI[+0.072,+0.094] CI-sep -- 2.3x held-out prediction MRR.**
- both info-free twins LOSE CI-sep (agent-shuffle +0.015, verb-shuffle +0.114).
- precision-composition net over the hub-centroid base = **+0.007 CI-sep on the FULL set** (+0.016 on the 43%
  agent-covered) -- where RAW composition was ns; the precision term itself earns its place (IDEAL vs RAW +0.004 CI-sep).
- decomposition: representation +0.075 (the lever) >> precision-composition +0.007 (a real, controlled topping).

This is the fundable `predictive_reader` upgrade, de-risked to a proven class. Reverify:
`.venv/Scripts/python.exe experiments/exp_ideal_recipe_v1.py` (or the witness).

---

## PART 4 -- THE FULLY FUNCTIONAL SYSTEM, and how it compares with the brain (`exp_whodidwhat_full_system_v1`)

One system, three stages, glass-box, doing everything the who-did-what pathway needs; proven on both jobs:

| stage | what it does | result |
|---|---|---|
| 1. NP-head chunking | pick the HEAD of each candidate NP (compound + genitive), not its first token | selection 0.917 -> **0.981 (+0.063 CI-sep)** |
| 2. role SELECTION | Competition-Model cue integration: word ORDER dominant, thematic FIT a precision-weighted secondary cue | **thematic fit's optimal selection weight = 0** (adding it does nothing; positive weight HURTS, below its own shuffle) |
| 3. forward PREDICTION | the proven precision-weighted composed predictor emits the anticipated patient / surprisal | ORGAN 0.063 -> **IDEAL 0.150 MRR = 2.38x** |

**WHY PREDICTION does NOT translate to SELECTION (Q2, demonstrated in-system).** They are DIFFERENT computations at
DIFFERENT processing stages, and the brain uses different cues for each. Prediction is a graded ANTICIPATION of the
upcoming argument BEFORE it is read (Altmann-Kamide anticipatory looks; the N400) -- there the agent x verb
conjunction genuinely constrains the patient (2.38x). Selection is a discriminative role assignment AFTER the nouns
are present -- and in English that is dominated by WORD ORDER (Competition Model), which with NP-head chunking already
solves canonical direct objects at 0.98. So the SAME thematic-fit store that gives 2.38x on prediction gives EXACTLY
0 on selection: once the candidate noun is on the page and its position is known, position tells you it is the
patient; the anticipation has already done its job (easing processing), and re-using it to CHOOSE adds only noise.
This is precisely the brain's division of labour, not a failure of our store.

**HOW IT COMPARES WITH THE BRAIN (Q1).**
- **Mechanism: MATCH.** Order-dominant selection with marked-cue override (Competition Model / eADM); graded
  thematic-fit PREDICTION from a verb prior modulated by the agent (McRae GEK; Bicknell conjunction); precision-
  weighting of the agent cue (Friston; Kleinschmidt-Jaeger); NP-head finding as a distinct syntactic stage; conjunctive
  role-filler binding kept in FHRR (Frankland & Greene). Every operation is one the brain is documented to perform.
- **Where we are BELOW the brain, precisely:** (a) REPRESENTATION -- our filler code is a 200-d distributional HUB
  PROXY; the brain's ATL hub is far higher-D and multimodally grounded, so it individuates fillers (and therefore
  composes) better -- our composition margin GROWS with dimensionality and is still climbing when vocabulary coverage
  caps it. (b) CUE BREADTH -- the brain also integrates DISCOURSE / referential context (which entities are salient in
  the situation model) and full morphology; our selection uses order + NP-head + (missing) case, and our prediction
  ignores the unfolding discourse. (c) COVERAGE -- composition fires on 43% of inputs (in-vocab agent); the brain's
  taxonomic generalisation (ATL) covers the rare tail our sparse hub cannot. None of these is an algebra gap -- they
  are representation, cue-breadth, and coverage gaps, each a fundable direction.
- **Net:** we have reproduced the brain's OPERATIONS faithfully and hit the brain's OWN division of labour (fit
  predicts, order selects); the remaining distance is representational richness + cue breadth, not mechanism.

---

## PART 5 -- THE "MORE IDEAL" SYSTEM: faithfully built, and an HONEST NEGATIVE (`exp_more_ideal_system_v1`)

The full-system report named three gaps vs the brain (representation, cue breadth, coverage). A research drill
(`BRAIN_MECHANISM_DRILL_more_ideal_implementation.md`) gave the FAITHFUL mechanism for each and one unifying fix: the
brain integrates cues by PER-ITEM, RELIABILITY-WEIGHTED, MULTIPLICATIVE (log-probability) combination (Ernst-Banks
2002; Lenci 2011) -- NOT the additive/unnormalized combination my first draft (and both earlier negatives) used. I
implemented all three gap-closers around that primitive:
- **GAP 1 representation** -> multimodal HUB+SPOKE fusion by Bayesian integration with accuracy-calibrated reliability.
- **GAP 2 cue breadth** -> event/discourse CONTEXT as a third multiplicative cue.
- **GAP 3 coverage** -> dense k-NN agent proxy (place an OOV-in-hub agent via its nearest spoke-neighbours) + graded
  cross-stream fallback.

**RESULT -- honest negative, with the reason MEASURED.** Coverage rose (agent-conditioning fires 43% -> **98%**), but
NO faithful integration beats the hub-only ideal on held-out prediction MRR:

| arm | MRR vs IDEAL (0.146) |
|---|---|
| Bayesian fusion (per-item reliability) | -0.047 **NEG** |
| Bayesian fusion (accuracy-calibrated) | -0.015 **NEG** |
| additive fusion | +0.001 ns |
| Bayesian context | -0.015 **NEG** |
| context (accuracy-calibrated) | -0.001 ns |
| additive context | +0.007 ns (best combined arm, not CI-sep) |
| MORE_IDEAL (all, calibrated) | -0.008 **NEG** |

**WHY (the crux, measured): cue QUALITY, not the integration operation.** Standalone MRR: hub **0.146**, spoke
**0.061**, context **0.078** (chance 0.021). The secondary streams are 2-2.4x WEAKER than the hub and not
complementary; multiplicative integration lets a confidently-wrong weak cue tank the true patient, and even
accuracy-calibrated down-weighting cannot make a weak non-complementary cue ADD signal to a strong one. Coverage
without quality does not help either -- the kNN-proxy agent is noisy, so conditioning on it is worse than the
centroid backoff. Controls pass (the system beats its ctx-shuffle +0.030 and verb-shuffle +0.091 CI-sep -- it USES
real signal; it just cannot beat the single strong stream).

**THE REFINED LESSON (brain-faithful).** The brain's multimodal gain (Andrews-Vigliocco-Vinson 2009: the joint model
beats either stream) requires TWO STRONG, COMPLEMENTARY streams. Our 12-d sensorimotor spoke and bag-of-context are
IMPOVERISHED, largely-redundant streams -- so no integration architecture recovers a gain. **The distance to the
brain is the REPRESENTATIONAL QUALITY of each stream, not the integrator (which we built faithfully) and not the
cue set.** The fundable path to a genuinely more-ideal system is to make each STREAM richer -- an ATL-grade hub
(higher-fidelity, better vocabulary coverage), a richer grounded spoke, a STRUCTURED situation model (Sentence-
Gestalt unbinding readout, not a bag-of-context mean) -- not to bolt more weak cues onto the strong one. This
sharpens the whole chain's headline: representation is the lever, all the way down.

### One-line reconciliation with the audit
The register/selection story is now fully brain-scoped: **English who-did-what SELECTION is word-order-dominant
(we match the brain); thematic-fit/composition is a forward-PREDICTION mechanism that is REPRESENTATION-bounded (spoke
vs hub), not a selection lever; the cheap missing selection cue is morphological CASE; the canonical residual is
NP-head chunking.** Nothing here needs a new binding algebra -- FHRR stays.
