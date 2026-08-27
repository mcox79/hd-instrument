---
problem: the_live_front_end_mislabels_who_did_what_to_whom
status: PARTIAL
bar: "The improved front-end must beat (a) the current live position-baseline front-end AND (b) the trivial majority floor, CI-separated over its UPPER bound, end-to-end, with an info-free twin (roles assigned by coin-flip / scrambled cues) LOSING CI-separated. Report CI half-width + null p95 beside every margin. Attribute PER CUE (ablate verb-argument / animacy / thematic-fit / quotative). Test on BOTH archaic (McGuffey) and modern (QA-SRL) populations."
result: "McGuffey end-to-end entity-role answering (n=178 target queries, bootstrap-CI scorer): the fair, brain-faithful assigner (core-mention selection + QUOTE EXCLUSION + a SPEECH-VERB/quotative verb-class cue + the organ's learned graded perceptron) = 0.747 [0.680,0.809], hw=0.065, BEATS the live positional baseline 0.483 [0.410,0.556] CI-separated (bar (a)); it TIES the trivial majority floor 0.781 [0.719,0.843] (bar (b) NOT cleared -- the population is 78% 'agent'). Role-balanced (macro) accuracy 0.191 > majority-macro 0.125 (point estimate; the faithful role-comprehension metric). QA-SRL role-labeling, modern prose (n=12,810; two-animate n=564; two-animate+passive n=98): a learned WORD-ORDER(+voice) model = 0.918 [0.895,0.940] on two-animate where ANIMACY is exactly chance 0.500 [0.461,0.541]; adding THEMATIC-FIT does NOT beat order+voice on ANY population (net-negative everywhere)."
floor: "STRONGEST floor = trivial majority 'always-agent' 0.781 [0.719,0.843] on McGuffey all-queries (also: in-scope majority 0.908; the live positional front-end 0.483 as the baseline-to-beat). QA-SRL per-population majority floor 0.500 (balanced); null p95 = 0.500 (label-shuffle)."
controls: "info-free TWIN (roles permuted across the passage) 0.663 [0.590,0.730] -- loses in point estimate; PER-CUE ablation (speech ON/OFF: +0.017 all / +0.019 in-scope; thematic-fit ON/OFF: net NEGATIVE); AUG_BASE (organ base features only) 0.747; NAIVE-WIRING negative control 0.385 (WORSE than the live baseline -- diagnosed: candidate over-generation + no quotative cue); QA-SRL ANIMACY_ONLY (isolates animacy -> chance on two-animate), POSITION_ONLY, thematic-fit-SHUFFLED-centroid twin (loses to themfit but themfit still net-negative vs base). EXCLUDES: that the fix is thematic-fit (refuted); that animacy carries English role assignment (refuted -- word order does); that the organ works wired as-is (refuted)."
files_changed: "experiments/exp_frontend_learned_role_wire_v1.py, experiments/exp_frontend_role_augmented_cv_v1.py, experiments/exp_frontend_thematic_fit_qasrl_v1.py (+THEMFIT_PURE isolation arm), experiments/exp_frontend_verbclass_source_v1.py (deepening: WordNet + distributionally-learned vs hand speech-verb class, null-controlled), experiments/exp_frontend_normalized_recurrence_v1.py (deepening Q2: Spivey-Knowlton normalized recurrence vs perceptron), verification/test_frontend_role_who_did_what.py (6 witnesses), data/exp_frontend_learned_role_wire_v1/, data/exp_frontend_role_augmented_cv_v1/, data/exp_frontend_thematic_fit_qasrl_v1/, data/exp_frontend_verbclass_source_v1/, data/exp_frontend_normalized_recurrence_v1/"
reverify: ".venv/Scripts/python.exe verification/test_frontend_role_who_did_what.py"
---

# SOLVED (PARTIAL): the live front-end mislabels who-did-what-to-whom

**One-line verdict.** The wall is real and a brain-faithful front-end fix recovers most of it (live end-to-end
**0.48 -> 0.75**, CI-separated over the live baseline). But the fix is **NOT the brief's proposed one**, and
two of the brief's premises are **refuted on disk**: (1) naively wiring the existing learned organ makes it
*worse*, and (2) the "fix the animacy-dominance with thematic-fit / selectional preference" route does **not**
help -- on real prose, **word order dominates English role assignment** (the actual brain-faithful cue
hierarchy). The genuine missing pieces are **core-mention selection + quote exclusion + a speech-verb/quotative
cue**, which the islanded organ lacks. On the agent-saturated McGuffey query population the fix ties (does not
clear) the trivial "always-agent" floor -> the brief's **rigorous-negative branch**, with the residual localized.

## What I built (all in `experiments/` + `verification/`; `hdlab/` UNTOUCHED, board Q111)

1. **Reproduced the wall** (trust-the-wall). Live positional front-end end-to-end = 0.483 [0.410,0.556] on the
   57-passage / 178-query McGuffey entity-role gold, BELOW the trivial majority floor 0.781; errors
   MISASSIGNMENT-dominant (role 86 / entity 50 / miss 30) + 104 out-of-scope gold roles. Matches the brief.

2. **Wired the learned organ faithfully but naively** (`exp_frontend_learned_role_wire_v1.py`) -> **0.385
   end-to-end, WORSE than the positional baseline (0.483)**. Diagnosed on disk (`scratchpad/diag_organ.py`):
   - **CandidateGenerator OVER-GENERATES**: mean **9.96** candidate (verb,arg) pairs/clause (max 35; 92% of
     clauses > 2). The organ labels every nominal -- incl. words INSIDE quotes and cross-verb coordination --
     flooding entity resolution. The live reader selects <=2 core mentions per predicate; the naive wiring did not.
   - **NO QUOTATIVE CUE**: every `said Fred` / `said Aunt Annie` / `said her mother` labels the speaker
     **PATIENT** (postverbal + DEFAULT frame). Quotative inversion is THE dominant McGuffey error and the organ
     has no speech-verb cue. -> **This refutes the brief's "just wire the existing organ" premise.**

3. **Built the FAIR, brain-faithful assigner** (`exp_frontend_role_augmented_cv_v1.py`, passage-level 6-fold CV,
   held-out): keep the organ's graded Competition-Model perceptron (NOT a rule cascade) and add the two cues the
   BRAIN uses that the organ was missing, as graded features:
   - **core-mention selection + QUOTE EXCLUSION** (matrix-clause argument identification);
   - a **SPEECH-VERB / quotative** verb-class cue (supplied lexical-semantic verb-argument knowledge, same KIND
     as the organ's PSYCH/DITRANS frames) + a speech x arg-order interaction.
   Result: **AUG = 0.747 [0.680,0.809]**, CI-separated over the live positional baseline (0.483); role-balanced
   macro 0.191 > majority-macro 0.125. Ablation: the **speech cue is the load-bearing lever** (patient recall
   **0.14 -> 0.50**; in-scope +0.019). The info-free twin loses in point estimate (0.663). It **ties** the
   agent-saturated plain-accuracy floor (0.781) -- see "What I did NOT establish".

4. **Tested the brief's thematic-fit hypothesis directly on modern prose** (`exp_frontend_thematic_fit_qasrl_v1.py`,
   32,419 QA-SRL gold-span entries). Built verb->role grounded selectional-preference centroids exactly as the
   predictive reader did (compose, don't duplicate). The two-animate reversibility instrument (animacy
   structurally uninformative -- both arguments agent-capable):

   | population | n | ANIMACY_ONLY | ORDER(+voice) | +THEMATIC-FIT | majority floor |
   |---|---|---|---|---|---|
   | ALL | 12,810 | 0.641 | **0.927** | 0.921 | 0.500 |
   | TWO-ANIMATE | 564 | **0.500** (chance) | **0.918** | 0.901 | 0.500 |
   | non-canonical (passive) | 2,192 | 0.630 | **0.784** | 0.748 | 0.500 |
   | two-animate + passive | 98 | **0.500** | **0.714** | 0.612 | 0.500 |

   **Word order (+voice) dominates AGENT/PATIENT assignment and resolves the reversible cases where animacy is
   exactly chance; adding thematic-fit adds NOISE on every population.** -> **This refutes the brief's
   "fix the animacy-dominance with thematic-fit" route.** It is a brain-faithfulness *confirmation*: English is a
   rigid word-order language, so word order is the highest cue-validity cue (Bates & MacWhinney competition-model
   cross-linguistic result); thematic fit is a low-validity cue precisely because order almost always resolves.

## KEY REALIZATIONS (the enabling moves)

- **The disk outranked the brief, twice.** The brief's headline ("wire the richer learned organ, it beats the
  hand cascade") and its fix ("integrate cues via thematic-fit selectional preference") were both plausible and
  both wrong when measured. The move that mattered was *building the naive wiring and reading its actual per-clause
  labels* (`diag_organ.py`) -- which showed the failure is over-generation + missing quotative cue, not a
  cue-integration subtlety.
- **The revalidation's "animacy-dominance HARD_FAIL" is partly a strawman artifact.** Its positional baseline is a
  FIXED rule (`pre->AGENT, post->PATIENT`, can never emit EXPERIENCER/RECIPIENT) scoring 0.48; a *learned*
  order+voice model does 0.93. Animacy looked dominant only because it was compared against a broken position
  baseline. The organ's real defect is that its *McGuffey-canonical training* confounds animacy with role, so it
  learns to lean on animacy when it should lean on the higher-validity word-order cue.
- **Pick the metric that measures comprehension, and pick a population with headroom.** On McGuffey plain accuracy
  the floor is unbeatable (78% agent -> "always agent" = 0.78; 16/178 queries need roles the organ can't emit).
  The role-BALANCED metric (getting patients/experiencers right counts as much as agents) is the faithful one,
  and there the fix beats the trivial prior. The clean floor-clearing win lives on the role-balanced modern QA-SRL
  population (order+voice 0.93 vs floor 0.50).
- **A rigorous negative on a plausible cue IS the deliverable.** Thematic-fit was worth testing (McRae is real
  neuroscience) and testing it faithfully -- with the predictive reader's own machinery, on 32K real examples,
  including the exact reversible cases it should help -- is what earns the right to say "word order dominates here."

## What I did NOT establish (what I'd withdraw first if wrong)

- **The plain-accuracy majority floor is NOT cleared end-to-end on McGuffey.** AUG 0.747 ties "always-agent"
  0.781. This is the brief's rigorous-negative branch, caused by agent-saturation of the query population, not by
  a fixable method gap. If a role-balanced McGuffey gold (or a reading population where roles are balanced)
  existed, I expect the fix to clear it -- but I did not build that gold, so this is inference, not measurement.
- **The info-free twin loses only in point estimate on McGuffey** (0.663 vs 0.747; CIs touch) -- because permuting
  roles preserves the 78%-agent marginal, so the twin scores near the majority prior. The stronger controls are
  the CI-separated win over the live baseline + the speech-cue ablation. First thing I'd re-test with a
  scramble-weights twin on a balanced population.
- **QA-SRL role-labeling is a component-level (front-end) measurement, not full end-to-end entity tracking.** The
  0.93 order+voice win is on the front-end's own job (assign roles to gold spans), which is exactly what this
  problem is about, but it is not the full reading loop.
- **experiencer/recipient recall stays low** (0.12-0.25 on 8/1 McGuffey queries) -- the richer inventory helps
  little because psych/ditransitive clauses are rare and CV thins them.

## PROPOSED hdlab CHANGE (NOT landed -- strategy re-verifies + lands, board Q111)

The evidence says wire a *specific* improved assigner into the live reader, and does NOT support the naive organ
wiring or a thematic-fit cue. Concretely, in `hdlab/situation_reader.py` behind a default-OFF flag (identical
downstream; only the assigner changes):

1. **`_pick_role_mentions`: add QUOTE EXCLUSION** -- drop quoted-span nominals from subj/obj selection, and treat
   only non-quoted verbs as matrix predicates. (Biggest single lever; the dominant McGuffey error class.)
2. **Add a SPEECH-VERB class + quotative-inversion frame** to `hdlab/thematic_role_labeler.py`'s supplied
   knowledge: for a speech verb, the nearest animate NP outside the quote (prefer postverbal) is the AGENT/speaker.
   Expose it as a `role_feats` cue (`speechverb:` + `spxorder:`), NOT a hard override. **Derive the class from
   WordNet's `verb.communication` lexical field, NOT a hand list** -- measured to recover the same benefit
   (0.863 in-scope) with a random-verb-class twin losing (0.850), and it drops the hand list's noise (go/went/
   began are not communication verbs). Ideal refinement: the narrower quote-licensing *verba dicendi* subset
   learned from corpus co-occurrence with direct quotes (distributional argument-structure signal).
3. **Wire the learned perceptron (`label_roles`) over the SELECTED core mentions only** (<=2 per predicate), not
   over all CandidateGenerator candidates. Retrain on a distribution where word order competes with animacy (real
   passages incl. quotative + non-canonical) so it does not become animacy-dominant.
4. **Do NOT add a thematic-fit / selectional-preference cue** to the role labeler -- measured net-negative on both
   McGuffey and 32K QA-SRL (English is word-order dominant). Keep the predictive reader's selectional-preference
   machinery for its anticipation/surprisal job, not for role labeling.
5. Expected effect (measured): live end-to-end 0.48 -> ~0.75 on McGuffey; role-balanced role-labeling on modern
   prose ~0.93 vs a 0.50 floor. It will NOT clear the agent-saturated plain-accuracy floor on the current McGuffey
   query gold -- so the honest capability claim is "recovers the front-end wall + resolves reversible roles via
   word order," pending a role-balanced reading gold to show a plain-accuracy floor-clearing lift.

## DEEPENING DRILL (2026-08-27) -- one level deeper, literature-VET'd

The owner's 60-min brain-faithfulness cron forced the question: is "word order dominates; thematic-fit is
noise" actually brain-faithful, or an artifact of a weak thematic-fit implementation used ADDITIVELY? Two
things came out of it, and they CORRECT a small overclaim above ("thematic-fit adds noise"):

- **Thematic-fit is a REAL but LOW-VALIDITY cue, not noise (isolation test, full 32K QA-SRL).** With word
  order fully removed (pure `themfit:` best-fit-role feature only -- the earlier arm leaked order through the
  `tfxo` interaction, a bug the drill caught), pure thematic-fit scores **0.585 [0.543,0.626]** on two-animate
  -- CI-separated ABOVE chance (0.500) and above its shuffled-centroid twin (0.512 [0.470,0.553]). So it
  carries genuine role information. But it is **utterly dominated by word order (0.918)** and, on the
  order-fails subset, cannot beat even the majority-role floor (0.587 vs 0.652). This is the **Competition-Model
  cue-validity hierarchy, confirmed empirically**: thematic fit is a present-but-overridden backup cue in
  English. Adding it additively HURTS because a linear model over-weights a low-validity cue relative to the
  dominant one.
- **The literature VET (research agent, 4 parallel lit-scans) confirms this is brain-faithful, with citations:**
  - "English relies on word order; case/animacy-dominant languages weight animacy" is **PINNED** -- MacWhinney,
    Bates & Kliegl 1984 cue-validity study; the 0.918-on-reversibles result is its direct modern echo.
  - The additive-thematic-fit-HURTS result has a **direct human analog**: Cai, Zhao & Pickering 2022 (*Cognition*)
    -- a plausibility bias can DEGRADE accuracy on already-clear grammatical cues (same direction as our result).
  - The weak-thematic-fit-on-reversibles null **matches Dowty 1991's own Argument Selection Principle** (predicts
    INDETERMINACY exactly on two-animate reversible verbs, with grammatical marking carrying the weight) and
    Kako 2006 (proto-role judgments can be a READOUT of position, not an independent input). So the null is a
    *prediction of the theory*, not a refutation of it.
  - **Where I was UN-PINNED:** the computational-level model. Log-linear/perceptron cue integration is PINNED as
    a *behavioral description* but CONTESTED as literal mechanism; **Bayesian noisy-channel (Levy 2008; Gibson,
    Bergen & Piantadosi 2013) has the best quantitative fit for the role-reversal/implausibility phenomenon
    specifically.** The "shallow default + gated revision" (Ferreira good-enough) vs continuous-integration
    (McRae/MacDonald) debate is genuinely CONTESTED; *dynamic reweighting* (plausibility reliance scales with
    parse cost) is the current reconciliation. Neural locus is CONTESTED too: angular-gyrus role in thematic
    combination (Boylan 2015 vs Matchin 2019 null), and IFG-primacy (Friederici) vs temporal-primacy (eADM,
    Bornkessel-Schlesewsky) is an open cross-linguistic debate.
- **Did I test the deeper "gated revision" mechanism? YES, and it does not earn its keep here.** On the
  order-fails subset (where the shallow word-order parse is wrong), pure thematic-fit (0.587) is weakly above
  chance but BELOW the subset's majority floor (0.652) -- the residual there is dominated by VOICE/passive
  parse errors, not thematic implausibility. So a gated hand-off to thematic-fit would not beat just predicting
  the majority role. The next-deeper lever on those cases is better VOICE detection, not richer plausibility.

**Second + third deepening pass (2026-08-27): is the load-bearing SPEECH-VERB cue a convenient hand-patch, or a
real semantic class the brain LEARNS -- and does it survive a proper info-free control?**
(`exp_frontend_verbclass_source_v1.py`.) My biggest lever was a HAND-LISTED speech-verb class -- the kind of
"convenient available tool" this project loses by. Two more brain-faithful derivations, both tested:
- **WordNet `verb.communication`** (a glass-box stand-in for anterior-temporal communication-verb semantics):
  recovers the hand list's benefit and correctly DROPS my hand list's noise (go/went/began/return are not
  communication verbs). But it is BROADER than the quotative class (also catches teach/deceive/persuade).
- **DISTRIBUTIONALLY LEARNED from quote co-occurrence** (the most brain-faithful: how a child learns which verbs
  report speech -- argument-structure learning, not a dictionary): learns exactly the *verba dicendi* --
  say (260/302 uses adjacent to a quote), reply (20/20), answer (14/14), exclaim (10/10), + interrupt/laugh/urge.
- **THE METHODOLOGICAL CORRECTION THE DRILL FORCED (supersedes a fire-2 overclaim):** a SINGLE random verb-class
  is NOT a valid info-free twin -- an arbitrary verb partition is a free feature the perceptron can exploit, and a
  lucky 12-verb draw scored 0.895 (above every real class). The proper control is a NULL DISTRIBUTION over 40
  random draws. Result (McGuffey CV): **in-scope acc** OFF 0.856 / HAND 0.863 / WORDNET 0.863 / LEARNED 0.869
  vs **null p95 0.876** -> NO semantic class beats the null on plain accuracy (agent-saturation swamps a small
  effect). **Role-balanced macro** OFF 0.173 / WORDNET 0.198 / HAND 0.214 / **LEARNED 0.215** vs **null macro
  p95 0.173** -> **the semantic classes DO beat the null on the faithful role-comprehension metric, and the
  distributionally-LEARNED class is best.** So the cue's value is genuinely SEMANTIC and specific to the non-agent
  (quotative-speaker) roles -- and the class is brain-faithfully LEARNABLE FROM EXPOSURE, not hand-enumerated --
  but the effect is small and shows only on the role-balanced metric, not the agent-saturated plain accuracy.

**Fourth deepening pass (2026-08-27): is the averaged PERCEPTRON a faithful stand-in, or should it be the
brain's constraint-satisfaction DYNAMICS (Q2)?** The perceptron is a convenient feedforward classifier; the PINNED
mechanism-level account is Spivey-Knowlton (1996) NORMALIZED RECURRENCE / McRae-S-K-T competition-integration --
interpretation units mutually inhibit (normalization) while weighted cues feed graded support, settling into one
interpretation, and the SETTLING TIME predicts processing difficulty (a signal a perceptron cannot produce).
Built + tested (`exp_frontend_normalized_recurrence_v1.py`, 32K QA-SRL two-arg entries):
- **POSITIVE (mechanism fidelity):** normalized recurrence over the same cues is a VALID, accuracy-equivalent
  integrator (0.852 [0.843,0.861], order-dominant) -- so there is no accuracy reason to prefer the perceptron;
  the dynamics version is strictly more brain-faithful at equal accuracy.
- **HONEST NEGATIVE (its distinctive output is NOT validated here):** the settling-difficulty signal is in the
  right direction (two-animate 4.98 cycles vs one-animate 4.56) but NOT CI-separated, AND -- the catch the drill
  forced -- a SHUFFLED-VALIDITY twin shows a COMPARABLE gap (4.78 vs 4.15), so the two-animate slowdown is NOT
  cleanly attributable to correct cue-validity competition (it is partly a structural artifact of animacy sitting
  at 0.5). **I do NOT claim a clean brain-faithful difficulty signal.** On this word-order-dominant corpus, order
  resolves most items fast, so settling barely competes. Validating settling-time as a genuine difficulty signal
  needs HUMAN reading-time data or a corpus engineered for cue-CONFLICT (flagged). This is a fair test of the
  right mechanism that returned a partial: the mechanism upgrade is defensible; its payoff signal is unproven here.

**Net: the brain-mechanism bar is met for the core question** -- validity-weighted cue competition with word
order dominant is PINNED; I replicated it and it works (0.48->0.75 end-to-end; 0.93 role labeling). The
load-bearing verb-class cue is a genuine semantic class, brain-faithfully learnable from quote co-occurrence
(non-arbitrary vs a null distribution on the role-balanced metric). The cue-integration MECHANISM is more
brain-faithful as normalized-recurrence dynamics than a perceptron, at equal accuracy -- but its distinctive
difficulty-signal payoff is not validated on this corpus. **Remaining untried** (flagged, diminishing returns): a
Bayesian noisy-channel model needs HUMAN error/reading-time data to test (not an accuracy task); proto-role
features on CONSTRUCTED reversible items would confirm a known-rare regime. I judge the front-end mechanism
CONVERGED for natural-corpus role labeling -- the brain's actual mechanism (word-order-dominant cue competition,
optionally as recurrence dynamics) is identified, replicated, and tested; further gains need new DATA (human
difficulty measures; a role-balanced / cue-conflict reading gold), not new mechanisms.

## AUDIT UPDATE (for `notes/BRAIN_FOUNDATIONAL_AUDIT.md`, thematic-role entry)

- **The learned `thematic_role_labeler` "animacy-dominance HARD_FAIL" is partly a measurement artifact** of a
  fixed positional strawman baseline (0.48). A learned word-order(+voice) model does 0.93 on 32K QA-SRL. The
  organ's real deviation is a **training-distribution confound** (McGuffey-canonical confounds animacy with role),
  not an intrinsic cue-integration failure.
- **The dominant, brain-faithful cue for English who-did-what is WORD ORDER (+ verb-class/quotative)** -- PINNED
  (MacWhinney, Bates & Kliegl 1984 cue-validity). Word order resolves two-animate reversible cases (0.918) where
  animacy is chance (0.500). **Thematic-fit is a REAL but LOW-VALIDITY backup cue** (pure, order-removed: 0.585,
  CI-separated above chance + above its shuffled twin 0.512), **correctly DOMINATED by word order** -- so adding
  it ADDITIVELY hurts (human analog: Cai/Zhao/Pickering 2022). Its weakness on reversibles matches Dowty 1991's
  own indeterminacy prediction + Kako 2006 (proto-roles as a position readout). Mark thematic-fit as
  **OUR-INVENTION-UNDER-TEST -> TESTED: real but low-validity; NOT a role-labeling lever for English** (it
  remains valid for the predictive reader's anticipation/surprisal job).
- **Computational-level model is UN-PINNED / CONTESTED.** The averaged perceptron (log-linear cue integration)
  is PINNED as a behavioral description but not as literal mechanism; **Bayesian noisy-channel (Levy 2008; Gibson
  2013) has the best quantitative fit for the reversal phenomenon.** "Shallow default + gated revision" (Ferreira)
  vs continuous integration (McRae) is contested; *dynamic reweighting* is the reconciliation. Neural locus is
  contested (angular-gyrus thematic role: Boylan 2015 vs Matchin 2019; IFG-primacy vs eADM temporal-primacy).
  These are OUR-INVENTION-UNDER-TEST choices, honestly labeled.
- **The cue-integration MECHANISM: normalized-recurrence dynamics (Spivey-Knowlton 1996) is the more brain-faithful
  form than the perceptron, at EQUAL accuracy (0.852 vs the perceptron's order-dominant ~0.85-0.93).** PINNED as the
  mechanism-level account. Its distinctive settling-time DIFFICULTY signal is, however, NOT validated on this
  word-order-dominant corpus (right direction but not CI-separated; a shuffled-validity twin is not defeated) --
  validating it needs human reading-time data or a cue-conflict corpus. Recommendation: the perceptron is an
  acceptable accuracy-equivalent production stand-in; adopt normalized recurrence only if/when the settling-based
  difficulty signal is wired as shared infrastructure with the N400 monitor + predictive-reader surprisal.
- **The organ, to be wired live, is missing three pieces the live reader needs**: core-mention selection, quote
  exclusion, and speech-verb/quotative frames. Naive all-candidate wiring FAILS (over-generation, 9.96 cand/clause).
- **The SPEECH-VERB cue is a real, brain-faithful SEMANTIC class, LEARNABLE FROM EXPOSURE -- not a hand-patch, but
  its effect is small and role-balanced-specific.** Against a proper NULL DISTRIBUTION (40 random verb-classes; a
  single random draw is NOT a valid twin -- a lucky draw hit 0.895): on plain in-scope accuracy no class beats the
  null p95 (0.876); on the role-balanced macro metric the semantic classes DO (learned 0.215 / hand 0.214 vs null
  p95 0.173). The class is derivable from the lexical-semantic network (WordNet communication) AND distributionally
  learnable from quote co-occurrence (say 260/302 quote-adjacent). PINNED as a lexical-semantic-network fact
  (anterior-temporal verb semantics + argument-structure learning); OUR-INVENTION only in the exact class boundary.

## PROXIMITY MACHINERY AUDIT (deepening Q4 -- is the SURROUNDING machinery brain-faithful?)

The role-INTEGRATION mechanism is converged (above). The machinery it sits in is a mix of faithful and
convenient; ranked by fidelity gap x leverage:

1. **THE PARSER FRONT-END (`hdlab/candidate_generator.py` = a UD-EWT-trained statistical POS tagger + arc
   parser) -- the BIGGEST fidelity gap, and it is NOT in the role assigner.** OUR-INVENTION-UNDER-TEST /
   convenient: the brain does not compute a Universal-Dependencies dependency parse to find candidate arguments;
   it builds structure INCREMENTALLY and predictively (garden-path, good-enough, filler-gap), left-to-right, with
   revision. This is the same "feed-forward where the brain is predictive" gap the predictive-reader session
   owns, one level down (structure, not semantics). **Recommendation: its OWN problem** ("the argument parser is a
   batch statistical dependency parser where the brain is incremental/predictive"), composing with the predictive
   reader + the relcl filler-gap resolver -- NOT a patch here. It is the highest-value front-end fidelity target.
2. **THE VERB FRAME TABLE (`thematic_role_labeler.VERB_FRAMES` = ~150-300 HAND-authored verbs -> PSYCH/DITRANS/
   plain).** OUR-INVENTION / convenient, same shape as the speech-verb hand-list I showed is learnable. The brain
   LEARNS verb argument structure distributionally (pMTG/ATL). **Optimization: derive the whole table from a lexical
   resource (VerbNet classes / WordNet lexnames) or distributional argument-structure learning, as I did for the
   speech-verb subclass.** MODERATE value: the richer roles it enables (experiencer/recipient) are RARE in the gold
   (recall 0.12-0.25), so this is a fidelity win with small measured end-to-end payoff. Buildable, in-scope.
3. **COMPOSE POINTS -- partially tested.** (a) Predictive-reader thematic-fit: TESTED, does not help role labeling
   (word order dominates) -- composed and measured. (b) **Relcl filler-gap resolver: UNTESTED, and it is the one
   place word order GENUINELY fails** -- object-relative clauses ("the boy the girl chased") where both nouns are
   preverbal and only the gap/syntax resolves the roles. This is the natural home for a real accuracy gain that
   the role cues cannot reach; recommend testing the relcl composition on reversible relatives (depends on that
   session's organ). (c) N400 monitor: event-boundary segmentation, orthogonal to role assignment; no compose need
   found here.
4. **SMALLER / ACCEPTABLE:** animacy lexicon (WordNet hypernym person/animal/object/abstract) is a reasonable
   static stand-in for ATL conceptual animacy but is HARD, not graded (the brain's animacy/agency is graded --
   minor INVENTION); the lemmatizer (WordNet morphy) is a defensible stand-in for morphological decomposition
   (VWFA); the quote-mask is ORTHOGRAPHIC, which is CORRECT for a reading substrate (the spoken analog is
   prosodic boundary detection) -- PINNED for reading. None of these is worth a drill.

**Bottom line for a further drill:** the role-assigner MECHANISM does not need more drilling (converged). The real
remaining brain-fidelity work is (1) the incremental/predictive PARSER front-end -- its own problem, highest value
-- and (2) the relcl composition for reversible relatives -- a real but narrow accuracy gap dependent on another
organ. A learned frame table (3) is a clean fidelity win with small payoff. All three are FLAGGED here rather than
built, because further work is either out-of-scope for this problem (parser, relcl) or low-payoff (frame table).

## TLDR (plain language)

The reader's first job -- working out who did what to whom -- was badly broken, and we thought the fix was to
switch on a smarter "who-did-what" module we'd already built and give it a sense of which nouns naturally do which
actions. When measured, both ideas were wrong: switching on the old module made things *worse* (it labels every
word in the sentence, including the words inside quotation marks, and it always gets "said Fred" backwards), and
the "which nouns fit which actions" idea added no value at all. What actually fixes it is simpler and truer to how
the brain reads English: **ignore the words inside quotes, know that verbs like "said/asked" put the speaker after
them, and lean on plain word order** -- because in English, word order is the strongest clue by far (it even sorts
out "the man the woman saw" style cases where knowing both are people tells you nothing). With those, the reader's
score more than doubles (from 48% to 75%). It still can't beat the dumb "just guess the most common answer" on
this particular test set, because 78% of the answers there happen to be the same role -- so we've recovered the
broken step and pinned exactly what's left, but not yet beaten the trivial guesser on this saturated set.

## QUESTIONS

None.

## NEXT STEPS

1. **Land the proposed diff** (quote exclusion + speech/quotative frame + core-mention-selected learned labeling;
   NO thematic-fit) behind a flag; strategy re-verifies via the witness.
2. **Build a role-BALANCED reading gold** (or reuse QA-SRL as the live reading population) so a plain-accuracy
   floor-clearing lift is measurable -- the current McGuffey query gold is agent-saturated (78%).
3. **Fix the organ's training-distribution confound**: retrain the perceptron on data where word order competes
   with animacy so it stops being animacy-dominant (the real root of the HARD_FAIL).
4. Optional: strengthen experiencer/recipient recall (psych/ditransitive detection) -- small, will not change the
   plain-floor verdict.

---

INTEGRATED_BY_STRATEGY: 2026-08-27 -- EXCELLENT / PARTIAL (owner-DONE). Full SOLVED re-read FRESH (standing rule).
Re-verified scaffold-free FIRST-HAND (test_frontend_role_who_did_what.py 6/6 PASS). The front-end wall is RECOVERED
0.48->0.75 CI-separated over the live positional baseline, via the RIGHT brain-faithful cues: core-mention selection +
QUOTE EXCLUSION + a learnable SPEECH-VERB/quotative class + the organ's graded perceptron over selected mentions.
REFUTES two brief premises on disk: naive organ wiring is WORSE (0.385, over-generation + no quotative cue); thematic-fit
is NOT the fix -- WORD ORDER dominates English role assignment (QA-SRL two-animate 0.918 where animacy is chance 0.500;
MacWhinney/Bates cue-validity, PINNED). 4 lit-VET'd deepening passes w/ self-corrections: thematic-fit is real-but-low-
validity (0.585 isolated, dominated by order -- Dowty/Cai); speech-verb class is brain-faithfully LEARNABLE from quote
co-occurrence (beats a proper 40-draw null on the role-balanced metric); normalized-recurrence more faithful than the
perceptron at equal accuracy (difficulty-signal payoff unproven here). VERDICT PARTIAL: ties (does not clear) the
agent-saturated 78% majority floor on McGuffey plain accuracy; the clean win is role-balanced + modern QA-SRL, pending a
role-balanced gold. CONVERGED for natural-corpus role labeling (further gains need DATA, not mechanisms). hdlab landing
EARNED -> QUEUED proven-ready (default-off quote-exclusion + speech-verb + core-mention wiring into situation_reader/
thematic_role_labeler; NO thematic-fit; a multi-part live wiring = a focused deliberate landing). AUDIT UPDATEs folded
(thematic-role entry: word-order dominant PINNED; thematic-fit real-but-low-validity TESTED; normalized-recurrence
faithful; training-distribution confound; the candidate_generator batch-parser = biggest remaining front-end gap).
SUCCESSOR packaged = the_argument_parser_is_batch_where_the_brain_is_incremental (the proximity audit's #1 gap). Review
EXCELLENT + SOLVER REVIEW in PROBLEM.md; priority cleared. Committed. *(2 of 3 batch submissions integrated after this;
next-steps recommendation held until all 3 per owner.)*
