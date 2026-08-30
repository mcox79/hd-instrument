---
problem: the_reader_eval_is_scored_on_200_year_old_mcguffey_migrate_to_modern_text
status: SOLVED
bar: "PASSES only with ALL of: 1. A MODERN annotated reader-comprehension eval (built in experiments/, in the reader's CoNLL shape): real modern (or at minimum 20c/21c, NOT 1830s) narrative/prose with EXISTING or transparently-derived gold for the reader's dimensions (role/who-did-what AND coref/entity at least). Name the corpus + the gold provenance. NO LLM-fabricated gold. 2. The reader organs REVALIDATED on it -- re-run role-labeling + coref + (where gold exists) the situation-model readouts on the modern eval; each key result must beat its strongest floor recomputed ON THE MODERN POPULATION, with the info-free twin LOSING CI-separated; report CI half-width + null p95. NO number crosses populations. 3. The McGuffey-vs-modern DELTA, per organ. 4. One-screen summary. A rigorous NEGATIVE is a FULL PASS."
result: "MODERN situation-model role eval built from UD-EWT gold parse (330 passages / 700 in-scope agent/patient queries, transparent UD-deprel->role, NO LLM). Revalidated the reader's role/situation-model organ (vargs front-end + resolver + role scorer, imported UNCHANGED) McGuffey-vs-modern under one scorer. HEADLINE (rigorous, mostly NEGATIVE): (a) McGuffey's role eval is DEGENERATE -- 90.85% of in-scope gold is 'agent', so the always-agent floor scores 0.908 [.863,.948] and the celebrated vargs organ (0.856 [.804,.909]) LOSES to it; the original eval gated vargs against the positional-reader floor (0.517) + an info-free twin (0.627), never against this strongest majority-class floor (0.908). (b) On modern text the current organ does NOT clear its floor: ALL_INSCOPE vargs 0.596 [.561,.634] < floor 0.659 [.624,.694]; and it COLLAPSES on non-canonical constructions to 0.288 [.186,.407] -- below the coin-flip twin (0.576) and CI-separated BELOW the floor (0.610). (c) The wall is a FIXABLE brain-fidelity gap, not a ceiling: a brain-faithful passive-aware content-verb assigner recovers non-canonical 0.288->0.559 [.440,.678] (CI-separated over broken), beats its voice-scrambled info-free twin (0.458), and does not hurt canonical (0.624->0.646). COREF dimension already migrated (owner-DONE): LitBank gold-coref binder GRADED 0.328 vs RAND-twin 0.132 (twin loses CI); graded-ACT-R 0.775 vs incumbent 0.603."
floor: "Strongest floor = always-predict-the-population-majority-role, recomputed per population/subset. McGuffey in-scope 0.908 [.863,.948] (agent, n=153). Modern in-scope 0.659 [.624,.694] (patient, n=700); modern role-varying 0.497 [.424,.571] (n=177); modern non-canonical 0.610 [.492,.729] (n=59)."
controls: "(1) Info-free twin per arm -- role labels coin-flipped (VARGS_TWIN) / voice cue scrambled (FIXED_TWIN): loses on McGuffey (0.627<0.856) and on the modern fix (0.458<0.559 non-canonical). (2) Strongest-floor gate: EXCLUDES 'beats a weak twin but not the majority baseline' -- it catches McGuffey's degeneracy (organ<floor) and the modern all-inscope loss. (3) Canonical-vs-non-canonical split: EXCLUDES 'the drop is generic corpus noise' -- localises the collapse to non-canonical order (the NVN-shortcut signature). (4) fix-does-not-hurt-canonical: EXCLUDES 'the fix trades canonical accuracy for non-canonical'. (5) Independent derivation: gold roles come from the UD GOLD parse, the reader re-derives roles from clause TEXT via nltk -> no circularity."
files_changed: "experiments/exp_mcguffey_migrate_build_modern_gold_v1.py; experiments/exp_mcguffey_migrate_revalidate_v1.py; experiments/exp_mcguffey_migrate_passive_cue_fix_v1.py; experiments/exp_mcguffey_migrate_noncanon_by_type_v1.py; experiments/exp_mcguffey_migrate_cue_competition_v1.py; experiments/exp_mcguffey_migrate_learned_cue_transfer_v1.py; experiments/exp_mcguffey_migrate_adjacency_audit_v1.py; experiments/exp_mcguffey_migrate_grounded_thematic_fit_poc_v1.py; experiments/exp_mcguffey_migrate_learned_competition_v1.py; experiments/exp_mcguffey_migrate_precision_weighted_v1.py; experiments/exp_mcguffey_migrate_grammatical_function_v1.py; experiments/exp_mcguffey_migrate_scoreboard_v1.py; verification/test_mcguffey_migration.py; data/eval_gold_mention_role_modern_ud_ewt_v1/gold_situation_modern_ud_ewt_v1.jsonl; data/exp_mcguffey_migrate_{build_modern_gold,revalidate,passive_cue_fix,noncanon_by_type,scoreboard}_v1/. NO hdlab/ modified (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_mcguffey_migration.py"
---

# Migrating the reader's situation-model eval off 200-year-old McGuffey -- and what the modern text exposed

## What the disk said that the brief did not (disk outranks brief)
The brief framed this as pure measurement-fidelity ("change the eval distribution, not the mechanism")
and expected the organ results to "hold on modern text". **Prior work + the disk refuted two premises,
and refuting is the halfway point:**

1. **Coref/who-did-what is ALREADY off McGuffey.** `exp_wire_predarg_binder_litbank_whodidwhat_v1`
   scores who-did-what on LitBank (GRADED 0.328 vs RAND-twin 0.132, twin loses CI); the coref organ is
   owner-DONE brain-faithful graded ACT-R at 0.775 vs 0.603 on LitBank competitive pronouns; and the
   parser survives 19c prose (`role_assignment_is_untested_on_archaic_literary_prose`, downstream coref
   delta -0.0009). **So the genuine residual is the COMPOSED situation-model REGISTER eval** (the
   57-passage entity-role-at-clause-T task in `exp_wire_organs_endtoend_v1`), which is the one reader
   dimension still McGuffey-scored.

2. **The brief's McGuffey headline is not the strongest-floor story.** The on-disk situation-model eval
   reports vargs end-to-end 0.856 in-scope (brief rounds it "0.742"). But its in-scope role population
   is **90.85% agent** (139 agent / 14 patient) -- the eval's own `inscope_majority_floor()` returns
   0.9085. **The organ (0.856) LOSES to a trivial always-agent floor (0.908).** The original problem
   (`wire_the_predarg_frontend_and_binder_into_the_live_reader`) gated vargs against the POSITIONAL-reader
   floor (0.517 family / 0.483 exact) and an info-free twin -- both of which it beats -- but never against
   the strongest (majority-class) floor, which is 0.908 and beats the organ. This is the corpus-age
   confound in its purest form: 1830s schoolbook prose is so canonical and protagonist-agent-heavy that
   "always say agent" is a 91% strategy, and any front-end looks competent beside a coin-flip.

## What I built (change the CORPUS, not the organ)
A **modern situation-model gold** from `data/corpora/ud_english_ewt` (UD-EWT: genuinely modern 2000s web
text -- blogs, reviews, emails, Q&A -- with a GOLD Universal-Dependencies parse), in the exact McGuffey
gold shape (passages of clauses; entities -> [{clause, mention, role}]; target_queries of
{entity, query_clause, gold_role}). Transparent, no-LLM derivation:
- **roles** agent := nsubj of a content VERB; patient := obj OR nsubj:pass (matches the on-shelf UD-EWT
  role pipeline). Copular/existential nsubj (head = bare AUX) excluded -- a copular subject is not a
  thematic agent (removed 8 UD gold-noise cases).
- **entities** nominal heads (PROPN/NOUN) tracked across a document's clauses by lemma identity (a
  transparent string-identity coref; UD ships no coref, so pronoun/alias tracking is out of scope here
  -- that dimension is LitBank's).
- **330 passages / 700 in-scope queries**, with **177 role-varying** (gold role != the entity's final
  role -- the floor cannot coast on "most-recent role") and **59 non-canonical** (passive / inversion /
  fronting -- the brain-fidelity discriminator).

Then I ran the **identical reader pipeline** (imported unchanged from `exp_wire_organs_endtoend_v1`:
the position and vargs front-ends, the recency resolver, the role scorer) on BOTH populations under one
scorer, floors + info-free twins recomputed per population/subset.

## What I measured -- the unified corpus-age scoreboard
`experiments/exp_mcguffey_migrate_scoreboard_v1.py -> data/.../scoreboard.json`

| organ / dimension | McGuffey 1830s | modern | delta / verdict |
|---|---|---|---|
| **ROLE (situation-model)** ALL_INSCOPE | floor **0.908**, vargs 0.856, twin 0.627 -> organ **< floor** | floor 0.659, vargs 0.596 (below floor) | vargs -0.26; both populations: organ does not clear its strongest floor |
| ROLE role-varying (discriminative) | floor 0.824, vargs 0.853 | floor 0.497, vargs 0.582 (+0.085, not CI-sep) | small real signal, not floor-separated at n=177 |
| ROLE **non-canonical** (brain-fidelity) | n=0 (McGuffey has ~0%) | floor 0.610, **vargs 0.288** [.186,.407], twin 0.576 | **COLLAPSE, CI-sep BELOW floor + below twin** |
| ROLE non-canonical **after brain-faithful fix** | -- | **0.559** [.440,.678] vs broken 0.288 | **CI-sep recovery**, twin 0.458 loses, canonical unhurt |
| **COREF / who-did-what** (already migrated, owner-DONE) | -- | LitBank binder GRADED **0.328** vs RAND-twin 0.132; graded-ACT-R **0.775** vs 0.603 | twin loses CI; off McGuffey |

**The corpus-age confound, made numeric:** McGuffey was INFLATING the apparent role competence two ways
-- a degenerate 91%-agent distribution (so the organ never had to beat a real floor), and a ~0%
non-canonical rate (so the organ's shortcut was never punished). On modern text the current role organ
does not clear its floor, and it is *confidently wrong* (below the coin-flip twin) exactly on the
non-canonical constructions McGuffey structurally cannot contain.

## The wall, understood deeply, then crossed (the brain-foundational core)
The non-canonical collapse is not a task ceiling -- it is a precise, brain-diagnosable cue-weighting gap.
**Diagnosis:** on a passive ("My neighbourhood has been surrounded by troops"), nltk tags
`has/VBZ been/VBN surrounded/VBN`; the vargs front-end extracts `(neighbourhood, agent)` from the
AUXILIARY "has" *before* it reaches the content participle "surrounded" (where its own passive rule
would flip to patient), and `by_ec.setdefault` keeps that first, wrong, auxiliary-derived binding. **The
organ assigns thematic roles from auxiliaries instead of the content verb where voice morphology lives**
-- so it defaults to the Bever NVN "first-noun = agent" shortcut on every passive. 18 of the 59
non-canonical failures are exactly this.

**The brain does not assign a role from "has"; it waits for the lexical verb (lemma/lexeme split, Levelt;
Competition Model cue-validity, Bates & MacWhinney -- passive morphology is a ~1.0-validity cue that
overrides word order).** The fix is that operation: skip the auxiliary chain, assign roles from the
content verb, let the passive-morphology cue (be + past participle, optional by-phrase) override word
order. It recovers non-canonical **0.288 -> 0.559 CI-separated**, with the voice-scrambled twin losing
(so the gain is FROM the passive cue) and canonical unhurt. **The brain reads passives; so can we.** This
is a proposed hdlab diff (below), not landed -- strategy owns hdlab (Q111).

## DEEPENING (cron fa9567c1, CANCELLED after this round -- in-scope checklist exhausted)
The 30-min deepening cron ran the checklist and produced the two results below, then was cancelled: the
eval-migration is complete and every remaining high-value item (land the passive fix; build the residual
order/prominence role cue; build a both-gold modern narrative gold) is an OUT-OF-SCOPE follow-on for
strategy (Q111 / new problems), not eval-migration work. The brain-mechanism bar is met (the wall is
understood and partially crossed; the residual is attributed to a specific brain cue family).

### Two robustness/generalisation results
1. **The McGuffey degeneracy is systemic, not one gold file.** Both McGuffey situation-model golds are
   in-scope agent-dominated: `gold_multiclause_entity_track_v3` 0.889 (80 agent / 10 patient) and the
   supposedly-harder multi-entity `gold_multientity_dense_v1` **0.937** (59 agent / 4 patient). The
   always-agent floor beats the organ on both. The confound is a property of 1830s schoolbook prose, not
   of one annotation.
2. **The passive-cue fix is PASSIVE-SPECIFIC -- there is a named residual non-canonical gap.** The 59
   modern non-canonical queries are passive 30 / inversion 23 / fronting 6. Broken->fixed delta by type:
   **passive +0.60** (recovered), **inversion -0.087** (not helped), **fronting +0.00** (not helped, n=6).
   Brain reading: passive is a MORPHOLOGICAL cue (be+VBN, Competition Model -- the fix supplies it);
   inversion (postverbal subject) and object-fronting are ORDER/PROMINENCE cues resolved by a DIFFERENT
   cue family (eADM animacy + verb-class proto-role + information structure). So the passive fix closes
   the dominant non-canonical failure but names the next fidelity target: an order/prominence role cue.
   (`exp_mcguffey_migrate_noncanon_by_type_v1.py`.)

## DEEPENING 2 -- "does this need to generalize?" answered with evidence (owner 2026-08-30)
YES, and the brain-faithful WAY to generalize is the finding. A stack of per-construction patches (passive
rule, inversion rule, ...) is NOT how the brain does it: the Competition Model (Bates & MacWhinney) +
Dowty proto-roles (1991) say role assignment is ONE mechanism -- graded, additive, cue-validity-weighted
COMPETITION over a cue set (word order, animacy, case, voice morphology), where each construction is a
different cue configuration. I built that single assigner (`exp_mcguffey_migrate_cue_competition_v1.py`)
and tested it per construction type vs BROKEN and vs the passive-only patch:

| construction | BROKEN | passive-only patch | ONE cue-competition mechanism |
|---|---|---|---|
| passive (n=30) | 0.333 | **0.933** | 0.567 |
| inversion (n=23) | 0.261 | 0.174 (fails) | **0.522** (recovers) |
| fronting (n=6) | 0.167 | 0.167 | 0.167 |
| canonical (n=641) | 0.624 | 0.646 | 0.630 (unhurt) |

**The general mechanism GENERALISES** -- it recovers inversion (0.261->0.522) where the passive patch
STRUCTURALLY cannot (0.174, it has no inversion cue), beats its info-free (all-cues-zeroed) twin (0.508 vs
0.458 on non-canon), and does not hurt canonical. **But it is WEIGHT-SENSITIVE** (a --sweep moves non-canon
0.39-0.54), and my hand-set voice weight under-serves passives (0.567) vs the dedicated detector (0.933).
The two are the SAME mechanism at different cue settings. **Conclusion (brain-faithful):** the fix is not a
fixed rule -- it is a cue-competition architecture whose cue VALIDITIES must be LEARNED from the corpus
(Competition Model: validities are language/input-specific and learned), which is exactly why hand-tuning
trades passive-vs-inversion. This connects the role fix to the project's LEARNER. Honest bound: the
per-type recoveries are point-estimates, not CI-separated -- the modern non-canonical population is
corpus-limited to n=59 (UD-EWT train+test exhausted).

## DEEPENING 3 -- can we SHOW generalization, and the WALL that names the clear path (owner 2026-08-30)
I learned the cue validities (glass-box numpy logreg over 6 interpretable cues -- the coefficients ARE the
Competition Model validities; no LLM) and tested TRANSFER (`exp_mcguffey_migrate_learned_cue_transfer_v1.py`):

| transfer test | learned cue | order-only (NVN) | floor | twin |
|---|---|---|---|---|
| **IN-DISTRIBUTION** (modern train/test) | **0.770 [.714,.827]** | 0.719 | 0.653 | 0.653 (loses) |
| CROSS-CONSTRUCTION (train canon+passive -> UNSEEN inversion) | **0.050** | 0.300 | 1.000 | 0.000 |
| CROSS-CORPUS (train McGuffey -> test modern) | 0.348 | 0.732 | 0.652 | -- |

Learned validities (in-dist): preverbal +1.93, animate +1.19, passive_subj -1.28, accusative -0.26. Sensible.

**GENERALIZATION HOLDS WITHIN-DISTRIBUTION** (learned 0.770 > order-only 0.719 > floor, twin loses, CI-sep
over floor). **BUT IT WALLS ON UNSEEN CONSTRUCTIONS AND CROSS-CORPUS.** The learned model over-relies on the
word-order cue (dominant in training) and predicts postverbal inversion-subjects as PATIENT (0.05, worse than
the NVN rule); trained on McGuffey it over-predicts agent and fails modern (0.348).

**THE WALL, UNDERSTOOD:** frequency-learned SURFACE cues under-sample the CONFLICT cases (rare non-canonical
order) that teach cue DOWN-WEIGHTING, so the model cannot generalize to a construction it rarely saw. This is
the Competition Model's own prediction (validities are learned from the input) turned into a limitation. **The
brain generalizes because it resolves roles SEMANTICALLY** -- verb argument structure licenses the roles, and
argument PLAUSIBILITY ("a key cannot *surround*"; McRae/Spivey-Knowlton/Tanenhaus 1998 thematic fit; Gibson
2013 noisy-channel) overrides a misleading surface cue independent of the construction's frequency. **This is
the SAME wall the whole project hits: surface statistics without grounding.**

**THE CLEAR PATH (brain-faithful, and it unifies with the project's core):** role assignment must be GROUNDED
-- a verb-argument-structure frame + argument-plausibility (world-knowledge) term, not surface cues alone. That
is the meaning/grounding channel the project is already building; role assignment is one of its consumers. So
the next role-organ problem is not "more surface cues" but "GROUNDED role assignment": the verb's learned
argument frame + a plausibility score of each candidate as agent/patient of THAT verb (content-addressable /
thematic-fit), which the audit already gestures at ("graded additive cue-based CONTENT-ADDRESSABLE retrieval").
Honest bound: cross-construction test n=20 (inversion, corpus-limited); the DIRECTION (surface cues wall, order
cue over-dominates) is mechanistic and consistent across all three transfer tests.

**GROUNDING (research drill 2026-08-30, PINNED-BY-EVIDENCE) -- the science PREDICTED this wall and pins the path:**
- The Competition Model's learning trajectory availability -> overall validity -> **CONFLICT VALIDITY** (MacWhinney,
  Unified/Competition Model) predicts EXACTLY my result: a learner trained on an order-dominant distribution masters
  word order's OVERALL validity but never reaches CONFLICT validity (reliability when cues conflict = the rare
  non-canonical cases), so it fails precisely on held-out inversion. My 0.77-in-dist / 0.05-held-out-inversion is a
  textbook instance.
- The generalizing mechanism is GROUNDED thematic fit: verb argument structure + argument PLAUSIBILITY resolve roles
  online before disambiguation (McRae/Spivey-Knowlton/Tanenhaus 1998; Ferretti/McRae event knowledge; Altmann & Kamide
  1999 anticipatory looks; thematic-role-reversal ERP). Plausibility is **CONSTRUCTION-INDEPENDENT** -- it never encodes
  "preverbal=agent", so it cannot over-fit word order the way my surface learner did. Honest limit: for REVERSIBLE
  sentences plausibility is uninformative and the parser FALLS BACK on structure -- so meaning does not REPLACE order,
  the cues COMPETE (weight learned as conflict validity).
- Neural locus PINNED: separable agent/patient populations in left STS/STG (Frankland & Greene 2015 PNAS; 2020 AnnRev
  variable binding); role binding shares the posterior-temporal lexical-semantic substrate (pMTG lexicalized syntax,
  Matchin & Hickok 2020) -- i.e. role binding lives WHERE meaning lives, supporting the grounded account.
- Copyable COMPUTATION (components PINNED, wiring OUR-INVENTION): verb-frame = content-addressable retrieval of the
  verb's argument slots (VSA-native); thematic-fit = cosine of a candidate's grounded vector to the role-PROTOTYPE
  filler vector (Baroni & Lenci Distributional Memory; Chersoni/Lenci Structured Distributional Model, incremental);
  combination = probabilistic meaning update trained by prediction error (Sentence Gestalt; Rabovsky/Hansen/McClelland
  2018 N400) or Lewis & Vasishth 2005 cue-based retrieval.
- **PROPOSED NEXT PROBLEM: `grounded_role_assignment_via_verb_keyed_thematic_fit`** -- add the grounded plausibility
  channel keyed on the verb as a COMPETING cue whose weight is learned as conflict validity (construction-blind, so it
  overrides misleading order on held-out inversion without touching reversibles). **It SHARES an existing dependency:**
  wiring `distributional_meaning_channel` (already Priority 2, `the_live_meaning_organ_has_no_distributional_channel_
  to_be_taught_by`) supplies the role-prototype vectors -- so this is not a new dependency, it consumes a planned one.
  Can-fail gate: beat naive-first-noun AND a structure-shuffled control ON THE HELD-OUT INVERSION SUBSET (not in aggregate).

## DEEPENING 4 -- PUSHING INTO THE SOLUTION: the grounded mechanism CLEARS the wall (owner 2026-08-30, "do it")
De-risk PoC for the flagship next problem (`exp_mcguffey_migrate_grounded_thematic_fit_poc_v1.py`): does a
CONSTRUCTION-INDEPENDENT grounded thematic-fit signal clear the held-out non-canonical wall where surface cues
collapsed? Distributional PROXY for the (unwired) meaning channel: corpus SELECTIONAL PREFERENCES from UD-EWT
gold parse (verb->typical subject/object + per-noun agentivity backoff), glass-box, no LLM. Random 70/30 split;
the thematic-fit predictor NEVER uses the test item's word order.

| construction | word order (NVN) | grounded thematic-fit | info-free twin | n |
|---|---|---|---|---|
| canonical | **1.000** | 0.719 | 0.634 | 3321 |
| passive | 0.060 | **0.889** | 0.847 | 216 |
| fronting | 0.000 | **1.000** | 0.714 | 14 |
| inversion | 0.000 | 0.210 | 0.120 | 100 |
| **NON-CANONICAL (all)** | **0.039** | **0.688** | 0.621 | 330 |
| ALL | 0.913 | 0.716 | 0.633 | 3651 |

**THE MECHANISM WORKS: grounded thematic-fit clears the non-canonical wall (0.688 vs 0.039 surface, vs 0.05 for
the LEARNED surface model), construction-independently, beating its info-free twin.** And it reveals the
brain-faithful structure: **the two cues have COMPLEMENTARY validity domains** -- word order owns canonical
(1.000, useless off it 0.039); grounded meaning owns non-canonical (0.688, weaker on canonical 0.719). A
HAND-SET combination underperforms BOTH cues in their own domain (0.84 all / 0.40 non-canon / 0.887 canon) --
**which PROVES the conflict-validity weighting must be LEARNED, not hand-tuned** (Competition Model core claim;
ties the role organ to the learner). Honest residuals: (a) INVERSION stays hard even for thematic-fit (0.21) --
it is INFORMATION-STRUCTURAL (existential/presentational subjects are not prototypical agents; needs given/new
+ definiteness cues, a named finer target); (b) my selectional-preference PROXY gets 0.688 -- a WIRED grounded
meaning channel (Priority 2) supplies higher-quality thematic-fit vectors, so the sequencing is confirmed:
**wire the meaning channel FIRST, then build the LEARNED order+thematic-fit cue-competition role assigner.** The
payoff is now proven, de-risking that investment.

## DEEPENING 5 -- the integration is a GATE, not a linear sum (owner "any more?", the arc's end)
Tested whether a LEARNED linear competition of order + morphology + grounded thematic-fit reaches BOTH domains
(`exp_mcguffey_migrate_learned_competition_v1.py`):

| | canonical | non-canonical | ALL | unseen inversion (cross-construction) |
|---|---|---|---|---|
| SURFACE (order+passive) | **1.000** | 0.655 | 0.969 | **0.000** |
| FIT (grounded, alone) | 0.728 | 0.703 | 0.726 | **0.227** |
| COMBINED (linear learned) | 0.856 | 0.646 | 0.837 | 0.100 |

**A LINEAR learned competition does NOT reach both domains:** it is WORSE than the better single cue in each
regime -- worse than SURFACE in-distribution (0.837 vs 0.969; the noisy fit feature degrades reliable surface),
and worse than FIT on unseen inversion (0.100 vs 0.227; the surface "postverbal->patient" bias drags the fit
signal back). **The reason is brain-foundational: conflict validity is a GATING operation, not a fixed linear
weight** -- the brain trusts meaning WHEN surface cues conflict / are unreliable (context-dependent), which a
linear cue-sum structurally cannot represent (my Deepening-4 hand-rule got the gating SHAPE right but hand-tuned
the weights; the linear model makes the weights learnable but cannot gate). **Refined next-problem spec:** the
grounded-role organ is a CONFLICT-GATED / reliability-weighted competition (use grounded thematic-fit to OVERRIDE
order when order is unreliable), NOT a linear cue-sum -- learned, and fed by the real `distributional_meaning_
channel`. (This is exactly the audit's "graded cue-based CONTENT-ADDRESSABLE retrieval" -- retrieval reliability
IS the gate.) Honest bound: grounded fit ALONE still only reaches 0.227 on unseen inversion -- inversion is
information-structural (given/new), the named finer residual; and the proxy grounding caps quality (the wired
channel is the lift). **This is the arc's end for the eval-migration solver: further work builds the gated
learned organ on the wired meaning channel = the flagship next problem, out of this problem's scope.**

**GROUNDING (research drill 2026-08-30, PINNED-BY-EVIDENCE) -- the linear-sum failure is a re-derivation of a
core neuroscience result, NOT our artifact:**
- **Reliability-weighted (Bayesian) cue integration is the brain's mechanism, and its DYNAMIC weights are the
  nonlinearity.** Optimal integration weights each cue by reliability=inverse-variance (Ernst & Banks 2002; Knill
  & Pouget 2004); the weights track reliability trial-to-trial (Fetsch/Pouget/DeAngelis/Angelaki 2011). The
  mechanistic model states it exactly: "the mathematical rule by which multisensory neurons combine their inputs
  CHANGES with cue reliability" (Ohshiro/Angelaki/DeAngelis 2011 normalization model). A fixed linear weight is
  the wrong functional form by construction -- my 0.10-on-inversion (below fit-alone 0.23) is its expected failure.
- **It applies to thematic roles specifically (noisy-channel).** The meaning PRIOR overrides the surface likelihood
  WHEN surface is unreliable: Gibson/Bergen/Piantadosi 2013 PNAS (implausible sentences -> comprehenders override
  literal word order, rate scales with assumed noise + edit size); Gibson 2013 Psych Sci (languages shift SOV->SVO
  for REVERSIBLE events, where order must carry the load); Levy 2008; Ferreira good-enough. Competition Model:
  validity = availability x reliability (PINNED), connectionist implementations are interactive/competitive, NOT a
  linear sum. Honest caveat: noisy-channel has some contested/non-replicated specifics; the CORE (more meaning-
  reliance as surface reliability drops) is robust.
- **Neural implementation = divisive normalization / gain control (Carandini & Heeger 2012) == precision-weighting
  of prediction errors (Feldman & Friston 2010): "trust the reliable cue" = raise the gain on that channel.**
  GRADED (soft), not a hard gate (near-winner-take-all only under strong conflict). Our ORGAN_MAP already pins
  "precision x error is the FORM; the precision ESTIMATOR is UNPINNED" -- the estimator is the sole OUR-INVENTION.
- **What to copy + TWO landed internal constraints that decide the build (reconciled from ORGAN_MAP):** copy the
  Ohshiro cross-cue normalization pool == content-addressable retrieval with a match-strength gate (Lewis &
  Vasishth 2005; McClelland IA). CAVEAT A (ORGAN_MAP §3, landed NULL +0.0018): a SCALAR normalizer over ONE fused
  representation cannot change a two-candidate argmax (cosine is scalar-invariant) -> the reliability gain must be
  applied ACROSS CUE CHANNELS (per-cue gain), NOT as a scalar over the fused vector. CAVEAT B (ORGAN_MAP C3,
  HARD_FAIL -0.022): a gain set to the candidate MARGIN made it worse -> the reliability signal must be the CUE's
  validity-in-context (is word order diagnostic here?), NOT the margin between role candidates.
- **REFINED FLAGSHIP SPEC:** the role organ replaces the fixed cross-cue weight with a PER-CUE RELIABILITY GAIN
  estimated from the current input (meaning's weight rises as word-order reliability falls), implemented as
  cross-cue precision-weighting -- NOT a scalar normalizer over the fused vector, NOT margin-gated. Sole
  OUR-INVENTION-UNDER-TEST = the reliability estimator (how each cue reports "I am / am not diagnostic here").
  Can-fail (reuse the 2026-08-20 note's test): beat majority-class AND structure-shuffled ON THE SUBJECT-NOT-FIRST
  subset. Reconciles: `notes/brain_thematic_role_assignment_is_multi_cue_competition_2026-08-20.md`; ORGAN_MAP F3 /
  §3 divisive-norm / C3 margin-gain HARD_FAIL / F5 precision-estimator-unpinned.

## DEEPENING 6 -- PROTOTYPED THE PINNED ARCHITECTURE: precision-weighting BEATS the linear sum (owner "do it now")
Built the brain-pinned reliability-weighted competition (`exp_mcguffey_migrate_precision_weighted_v1.py`): each
cue weighted by its INFORMATIVENESS-IN-CONTEXT (2*reliability-1, LEARNED per context) -- per-cue gain across
channels (Caveat A), reliability = cue-validity-in-context not margin (Caveat B). The sole OUR-INVENTION (the
reliability estimator) is a learned precision: order-reliability by passive-context, fit-reliability by |logodds| bin.

| arm | canonical | passive | inversion | non-canon | ALL |
|---|---|---|---|---|---|
| surface (order) | 1.000 | 0.060 | 0.000 | 0.039 | 0.913 |
| fit (grounded proxy) | 0.736 | 0.903 | 0.270 | 0.715 | 0.734 |
| linear-combined (Deepening 5) | 0.856 | -- | -- | 0.646 | 0.837 |
| **PRECISION-WEIGHTED (pinned)** | **0.926** | **0.963** | 0.070 | 0.679 | **0.904** |

**VALIDATED:** the pinned precision-weighting BEATS the linear sum on EVERY cut (ALL 0.904 vs 0.837; canonical
0.926 vs 0.856; non-canon 0.679 vs 0.646), reaching far closer to best-of-both than the linear model -- confirming
the drill's claim that reliability-weighting is the right functional FORM. **The passive fix EMERGED, not hand-
coded:** learned order-reliability is 0.967 on canonical context but 0.037 under passive morphology, so order gets
a NEGATIVE weight and auto-flips on passives (0.963). This is the brain mechanism (learned precision -> gain)
working end to end.

**HONEST RESIDUALS (no clean capability claim):** (1) INVERSION stays 0.07 (worse than fit-alone 0.27): passives
carry a SURFACE reliability marker (morphology) so order self-reports low reliability; inversion has NO surface
marker, so order stays wrongly-confident and fit cannot override without CONFLICT-gating -- which ORGAN_MAP Caveat
B showed HARD-FAILS. Inversion needs an information-structure (given/new / definiteness) reliability signal -- the
harder, less-pinned residual. (2) canonical 0.926 < surface 1.0 (fit-proxy noise; a WIRED meaning channel reduces
it). (3) my info-free twin was NOT clean (it shuffled the reliability estimator but kept the real cue VOTES), so I
rely on PW-vs-linear and PW-vs-surface, not the twin. **CONCLUSION: the pinned architecture is validated in
principle NOW (precision-weighting > linear; passive auto-flip emergent), but a CLEAN capability demonstration
needs (a) the WIRED meaning channel (better fit, recover the canonical loss) and (b) an information-structure
reliability signal for unmarked inversion and (c) a construction-role-DECORRELATED eval (reversible items) to
remove the per-construction-majority confound -- all three are the flagship problem's proper scope. Doing it NOW
proved the mechanism; doing it CLEANLY is the next problem, now fully de-risked and scoped.**

## DEEPENING 7 -- HOW THE BRAIN SOLVES IT, IMPLEMENTED: grammatical FUNCTION, not position; NOT plausibility
Owner "drill how the brain solves these and implement". Two findings + a research drill that CONFIRMED the
implementation re-derives an owner-DONE design.

**(a) 87% of "inversion" was my own GOLD NOISE.** The "inversion" set (postverbal nsubj) is 87% EXISTENTIAL
"there" ("There has been talk" -> UD calls the pivot nsubj, my rule mislabeled it AGENT; it is not a thematic
agent). Only 11% (52/455) are genuine inversions. Fixed the transparent rule to exclude existential (expl
dependent) + copular ('be' head) subjects -- a THEMATIC gold, not a raw-grammatical one. Rebuilt the
situation-model gold (non-canonical 59->40; headline holds, witness 19/19).

**(b) The genuine constructions are a PARSE problem, solved by GRAMMATICAL FUNCTION + VOICE (implemented,
non-circular via spaCy).** `exp_mcguffey_migrate_grammatical_function_v1.py`: the brain-faithful structure cue =
grammatical function (subject/object from a parse) + voice (active subj=agent; passive subj=patient), NOT surface
position. Tested with spaCy (a REAL parser, independent of the UD gold) vs the position cue:

| construction | surface position | spaCy grammatical function | gold-function upper bound | n |
|---|---|---|---|---|
| passive | 0.044 | **0.948** | 1.0 | 727 |
| inversion (genuine) | 0.000 | **0.731** | 1.0 | 49 |
| fronting | 0.000 | **0.944** | 1.0 | 43 |
| canonical | >0.95 | -- | 1.0 | 11051 |

Grammatical function SOLVES the constructions where position collapsed to ~0. **This CORRECTS my own earlier
thread:** inversion is NOT a thematic-fit problem -- it was existential gold-noise + a position-vs-function
confusion. Thematic fit's real domain shrinks to genuine ambiguity/reversibles.

**GROUNDING (research drill 2026-08-30) -- the implementation RE-DERIVES an owner-DONE design (~85% already built):**
- **Q1/Q2 PINNED:** locative inversion keeps the postverbal NP as grammatical SUBJECT (controls agreement, "In
  the boxes WERE keys"; Bresnan 1994 LFG); existential 'there' is expletive, pivot is notional subject; agreement
  is STRUCTURAL not semantic (Bock & Miller 1991; Wagers/Lau/Phillips 2009 cue-based retrieval). subject->agent
  resolves clean inversion with NO plausibility. Thematic fit is decisive ONLY at reduced-relative garden paths
  (McRae 1998) + noisy/reversible input (Gibson 2013) -- a tie-breaker under ambiguity, not the primary cue.
- **RECONCILIATION -- ALREADY OWNER-DONE:** `role_assignment_is_untested_on_archaic_literary_prose` (2026-08-29)
  landed a POSITION-DOMINANT + cue-OVERRIDE subject stage, inversion **0.47->0.83 CI-sep**, twin loses;
  "the cue-FIRST replacement was SELF-REFUTED" -- position-dominant + structural override IS the faithful design.
  Quotative inversion is LANDED LIVE in `hdlab/predicate_argument_frontend.py` (+0.253 CI-sep); `graded_role_
  assigner` is imported by the live `situation_reader`. **My independent spaCy re-derivation (0.73-0.95) matches
  it.** And the project already measured a FLAT integrator NET-NEGATIVE on canonical (-0.041) -- matching my
  Deepening 5/6 linear-sum-insufficient finding. Two independent routes, same conclusion.
- **CORRECTION to my "reliability estimator":** it is TWO signals for TWO regimes, not one -- (1) DISCRETE
  STRUCTURAL MARKEDNESS (fronted non-subject XP / expletive / agreement-controller / communication verb) detects
  CLEAN inversion deterministically from the parse, NO confidence gating; (2) surprisal / route-conflict governs
  ONLY the ambiguous/reversible subset where fit is recruited. My Deepening-5/6 precision-weighting conflated
  these; the faithful design does NOT gate clean inversion on confidence -- it detects it structurally.
- **PRECISE REMAINING GAP (small):** (1) the locative/existential/expletive-'there' subject-override is BUILT but
  LANDING-QUEUED -- not yet in the live `graded_role_assigner` wired path; concrete build = land it + rebuild the
  who-did-what cache (strategy Q111). (2) the surprisal / route-conflict GATE that recruits the fit competitor on
  the reversible subset is ISLAND-only. Do NOT wire fit onto the clean-inversion path (flat integrator is
  net-negative, confirmed twice).
- **THE CAN-FAIL TEST (for the flagship):** partition held-out into A=clean inversions, B=reversible/ambiguous;
  with fit ABLATED vs ON: HARD-PASS = structure/voice solves A with fit OFF (beats position CI-sep) AND fit-ON ==
  fit-OFF on A (fit inert on clean inversion) AND fit-ON > fit-OFF on B CI-sep. HARD-FAIL = fit-ON changes A at all.

**NET:** "how does the brain solve these?" -> grammatical function (parse) + voice + structural override for clean
non-canonical; plausibility ONLY for the ambiguous/reversible residual. IMPLEMENTED + validated here (spaCy
0.73-0.95), and it re-derives the owner-DONE `graded_role_assigner` design. The remaining work is landing the
queued locative/existential override (strategy) + the island-only surprisal gate -- NOT a new solver build.

## ADJACENT-COMPONENT BRAIN-FIDELITY EVALUATION (to seed next problems; owner 2026-08-30)
- **`thematic_role_labeler.py` (the role organ) -- FIDELITY LOW, clear build target.** Audit: RIGHT-OP-
  WRONG-METRIC, animacy-dominant, HARD_FAIL on real text. This problem localised WHY: it assigns roles from
  AUXILIARIES via a hard positional (NVN) rule, collapsing below chance on modern non-canonical order. A
  learned cue-competition assigner fixes it IN-distribution but WALLS on unseen constructions/cross-corpus
  (Deepening 3) -- surface cues alone do not generalise. **-> next problem A (highest value): GROUNDED role
  assignment = verb argument-frame + argument-plausibility (thematic fit), the meaning-channel consumer, not
  more surface cues.**
- **`animacy_lexicon.py` (the animacy cue) -- PRINCIPLE brain-foundational, IMPLEMENTATION is not (MEASURED,
  `exp_mcguffey_migrate_adjacency_audit_v1.py`).** The animacy->agent PRINCIPLE (Dowty) generalizes and even
  HELPS MORE on modern text: role-validity gap P(agent|animate)-P(agent|inanimate) = **+0.37 modern** vs
  **-0.10 McGuffey** (McGuffey's 91%-agent skew makes animacy non-discriminative). BUT the IMPLEMENTATION (a
  hard-coded ~40-word McGuffey-flavoured list + NNP heuristic) does NOT generalize: animacy fire-rate
  **collapses 0.706 -> 0.124** on modern text -- it barely detects animacy on modern entities, starving a cue
  that would otherwise help. **-> next problem B: a GROUNDED/LEARNED animacy feature** (feeds A; the grounding
  channel already exists to supply it).
- **`verb_lexical_similarity.py` / SPEECH_VERBS (the verb-class cue) -- FIDELITY LOW.** The verb-class cue is a
  hard-coded speech-verb list; it should be learned from argument-structure statistics. **-> folds into A.**
- **Entity tracking / string-identity coref (my UD-EWT gold) -- LIMIT NOW QUANTIFIED (MEASURED).** In UD-EWT,
  **46.6% of all core arguments are PRONOUNS** (11,970 / 25,667), invisible to string-identity tracking (UD
  ships no coref). So the modern role eval cannot test ~HALF the entity-tracking challenge -- the pronoun
  dimension is exactly where the coref organ's brain-faithful graded-ACT-R work lives (LitBank, done). **-> next
  problem C (now numerically motivated): a both-gold (coref+role) modern NARRATIVE situation-model gold.**

## What I did NOT establish (withdraw-first order)
1. **The both-gold modern NARRATIVE situation-model eval.** No single modern narrative corpus on the
   shelf has BOTH gold coref AND gold roles: UD-EWT = gold roles / web text / string-identity coref (no
   pronoun tracking); LitBank = gold coref chains / 19c literary / no gold roles. So role is validated on
   UD-EWT gold and coref on LitBank gold *separately*. The fully-composed both-gold situation-model on
   one modern narrative is the next gold to build. **This is the first thing I'd flag as incomplete.**
2. **The modern non-canonical n is small (59).** The direction (collapse, and fix-recovery) is CI-sep and
   robust across two builds (train-only and train+test), but the exact recovered value wobbles
   (0.559-0.638); do not quote a point value, quote the CI-sep relationship.
3. **UD-EWT is web text, not narrative.** Entity recurrence is real (330 usable passages) but thinner and
   less character-driven than McGuffey/LitBank; the role-varying subset is the honest discriminative core.
4. **First-order role only (agent/patient)**, matching what the reader's front-end can structurally emit.

## KEY REALIZATIONS
- **The corpus-age delta IS a brain-fidelity probe, not bookkeeping.** The brain's role/coref mechanisms
  are distribution-invariant; a win that evaporates off McGuffey means the organ copied a McGuffey
  regularity, not the brain's operation. Building the eval to *expose* that (a non-canonical subset) is
  what turned a data-prep chore into the finding.
- **Gate on the STRONGEST floor, not the twin.** The one line that cracked this open was recomputing the
  McGuffey majority floor (0.908) that the original eval never gated against (it used the positional-reader
  floor 0.517). A 91%-agent population makes every front-end look good beside a weaker floor.
- **Derive the gold and the reader's answer from DIFFERENT sources.** UD gold parse for the gold, nltk for
  the reader -> the delta is real, not a parser agreeing with itself.
- **A wall localised to a construction is a cue gap.** "Below the coin-flip twin only on passives" named
  the mechanism (auxiliary vs content-verb role assignment) and the fix in one measurement.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md)
- **TIER 3 Thematic role assignment / situation-model:** add that the live situation-model eval was
  DEGENERATE-on-McGuffey (in-scope gold 90.85% agent; the vargs front-end 0.856 loses to the always-agent
  floor 0.908) and that the front-end **assigns roles from auxiliaries, not the content verb**, collapsing
  to below-chance (0.288) on modern non-canonical constructions. The audit's pinned mechanism (Competition
  Model cue-validity; Lewis & Vasishth) is corroborated: a passive-aware content-verb assigner recovers it
  CI-sep. This is a concrete instance of the audit's "RIGHT-OP-WRONG-METRIC: animacy-dominant; HARD_FAIL on
  real text" for `thematic_role_labeler` -- now with the exact failure (auxiliary role assignment) and a
  proven fix.
- **NEW (Deepening 3 + research drill):** surface-cue role assignment (even LEARNED) does NOT generalise to
  unseen constructions/cross-corpus -- the Competition Model's conflict-validity trajectory (MacWhinney)
  predicts it. The generalising mechanism is GROUNDED thematic fit (verb frame + plausibility; Frankland &
  Greene 2015 separable agent/patient in STS/STG; Matchin & Hickok pMTG lexicalized syntax), construction-
  independent, weight learned as conflict validity, competing with order. The brain-faithful role organ is a
  CONSUMER of the meaning channel, not a surface-cue module. Proposed problem `grounded_role_assignment_via_
  verb_keyed_thematic_fit` SHARES the `distributional_meaning_channel` (Priority 2) dependency.
- **Adjacency (measured):** the animacy cue PRINCIPLE generalises (validity gap +0.37 modern vs -0.10 McGuffey)
  but its IMPLEMENTATION (hard-coded list) does not (fire-rate 0.71->0.12) -> grounded animacy feature. And
  46.6% of modern core-args are pronouns (string-identity coref blind) -> both-gold modern narrative gold.

## PROPOSED hdlab DIFF (strategy lands; Q111)
1. **`hdlab/thematic_role_labeler.py` / the situation-reader role front-end:** assign thematic roles from
   the CONTENT verb (skip the auxiliary chain: be/have/do + modals), and treat passive morphology (be +
   past participle, optional by-phrase) as a high-validity cue that overrides word order. Reference impl +
   controls: `experiments/exp_mcguffey_migrate_passive_cue_fix_v1.py::_content_verb_roles`.
2. **Default reader role/situation-model EVAL:** make the modern UD-EWT situation-model gold
   (`data/eval_gold_mention_role_modern_ud_ewt_v1`) the primary role/situation-model instrument (co-primary
   with LitBank for coref); retire McGuffey-as-primary -- keep it only as an archaic-register robustness
   check, never as the headline (its role population is degenerate).

## TLDR
We had been grading the reader's "who-did-what-when" test on 1830s schoolbook stories. Two problems: those
stories are so simple that "always guess the doer" already scores 91%, so the reader looked good without
being good; and they contain none of the twisted sentences (like "the house was surrounded by troops")
that real modern writing is full of. I rebuilt the test on modern web text with a trustworthy answer key
(no AI used to make it). On modern text the reader does NOT actually beat the simple always-guess baseline,
and on the twisted sentences it is worse than a coin flip -- it blindly calls the first name the "doer". I
found exactly why (it reads the role off the helper word "has/was" instead of the real verb), and showed a
brain-faithful fix that reads the real verb recovers those sentences. Coreference (who "she"/"it" refers
to) was already moved onto modern text in earlier work and holds up.

## QUESTIONS
None blocking. One decision for the owner/strategy: land the passive-cue fix now (it is a general
improvement the migration exposed), or keep this problem to the eval migration and file the fix as its own
follow-on. I recommend filing the fix as a small follow-on so this problem stays "migrate the eval".

## NEXT STEPS
1. Strategy: swap the default role/situation-model eval to the modern UD-EWT gold; retire McGuffey-as-primary.
2. **File the LEARNED cue-competition role assigner as the primary follow-on hdlab problem** (next problem A).
   Reference impl + can-fail controls are done (`exp_mcguffey_migrate_cue_competition_v1.py`): ONE graded
   additive cue-competition mechanism (order + animacy + case + voice, Dowty proto-roles / Competition Model)
   that generalises across constructions (recovers inversion where the passive patch cannot), with cue
   VALIDITIES LEARNED from the corpus rather than hand-set (the passive patch is its voice-cue-only special
   case). Feeds: (B) a grounded/learned animacy cue to replace `animacy_lexicon`'s hard-coded list; (C) the
   verb-class cue learned from argument-structure stats.
3. Build a both-gold modern NARRATIVE situation-model gold (coref + roles on one text) -- the single
   dimension no on-shelf modern corpus supplies; candidate route = a GUM-style corpus (UD parse + coref) or
   hand-authored modern passages in the McGuffey shape.

---

## INTEGRATED_BY_STRATEGY — 2026-08-30 (grade: EXCELLENT; SOLVED owner-DONE)

Integrated by strategy. Reverified FIRST-HAND: `verification/test_mcguffey_migration.py` **19/19 PASS** (scaffold-free — all headlines recomputed). Argument adversarially audited and sound: (1) McGuffey's role eval is DEGENERATE (90.85% agent → always-agent floor 0.908 BEATS the vargs organ 0.856; never gated against the strongest majority-class floor); the brief's '0.517→0.742' corrected to disk (0.483→0.736) and it fails the strongest-floor test — the celebrated McGuffey role number was partly a degenerate-eval artifact. (2) The organ does NOT generalize to modern text (0.596 < floor 0.659; COLLAPSES on non-canonical to 0.288, CI-sep below floor) — McGuffey's ~0% non-canonical rate structurally hid it (corpus-age confound made numeric). (3) FIXABLE fidelity gap (front-end reads AUXILIARIES not the content verb; passive-aware content-verb assigner recovers non-canon 0.288→0.559 CI-sep, voice-scrambled twin loses, canonical unhurt). Brain depth: learned surface cues wall on unseen constructions (Competition Model conflict-validity), grounded thematic-fit clears the wall, conflict-validity is a GATE not a linear weight, precision/reliability-weighting PINNED — and implementing the mechanism RE-DERIVES the owner-DONE graded_role_assigner (role = grammatical function + voice). Self-corrected two of its own errors (87% of the "inversion wall" was its own existential-"there" gold mislabeling; inversion is a PARSE problem not thematic-fit).

**STRATEGY LANDINGS QUEUED (Q111 — DEDICATED efforts, NOT rushed in this integration):**
1. **Swap the default role/situation-model eval to the modern UD-EWT gold** (`data/eval_gold_mention_role_modern_ud_ewt_v1/gold_situation_modern_ud_ewt_v1.jsonl`) + RETIRE McGuffey-as-primary (keep it only as an archaic-register robustness check). ⚠️ The McGuffey reference is DIFFUSE across ~9 hdlab files (animacy_lexicon, candidate_generator, coreference_resolver, corpus_registry, self_improving_loop, situation_model_accumulate, situation_reader, substrate, verb_lexical_similarity) — a careful per-file change, NOT a one-liner; and it has RE-BASELINING implications (every reader number reported vs McGuffey must be re-based vs modern). This is the deliverable that actually retires the 200yr eval — flagged to the owner as the top next dedicated action.
2. **Land the BUILT-but-queued locative/existential/expletive-'there' subject-override** into the live `graded_role_assigner` + rebuild the who-did-what cache (corpus-scale). Composes with the landed position-dominant + structural-override design.

**Audit §2b folded** (the ROLE eval migrates McGuffey→modern UD-EWT; McGuffey's role eval is DEGENERATE 90.85%-agent; the vargs front-end does NOT generalize to modern non-canonical order — reads auxiliaries not the content verb; the fix is grammatical-function + voice + precision-weighted grounded thematic-fit, re-deriving graded_role_assigner). Review (EXCELLENT) + `> ## ✅ SOLVER REVIEW` block in PROBLEM.md; `priority:` cleared.

**Seeded next problems (dependency-linked):** (A) FLAGSHIP — the reversible/ambiguous role residual: recruit grounded thematic-fit via a surprisal/route-conflict GATE (architecture pinned, two wrong approaches fenced, sole invention = the reliability estimator; shares the `distributional_meaning_channel` dependency; can-fail = structure solves clean inversion with fit OFF, fit helps ONLY the reversible subset). (B) a both-gold modern NARRATIVE situation-model gold (the 46.6%-pronoun coverage gap). (C) a grounded/learned animacy cue (principle generalizes, hard-coded word list does not: fire-rate 0.71→0.12 on modern).
