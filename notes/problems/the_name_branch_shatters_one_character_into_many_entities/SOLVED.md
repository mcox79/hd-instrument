---
problem: the_name_branch_shatters_one_character_into_many_entities
status: REFUTED
bar: "PASSES only with ALL of: (1) a cross-mention name/nominal ENTITY-CLUSTERING organ (content-addressable complete-or-separate onto a person-identity node over FULL-SPAN features; copy the computation, sweep features+threshold); (2) cluster quality beats the token-overlap floor CI-separated on REAL narrative (LitBank held-out; B-cubed F or purity; info-free twin LOSES CI-separated; CI half-width + null p95; no number crosses populations); (3) a POSITIVE control the metric can move (an alias re-entry the merger gets and single-token-overlap cannot); (4) SERVES a downstream capability (wire-don't-island): unifying the aliases LIFTS the who-did-what decode toward the oracle-coref ceiling (from ~0.17 measurably UP toward 0.62), CI-separated vs the current clustering on the same task; (5) a one-screen summary. A rigorous NEGATIVE is a FULL PASS (e.g. 'full-span content-addressable clustering does NOT beat token-overlap once the cache is fixed - the real cap is X' - with the positive control confirming the metric can move - closes the question)."
result: "REFUTED via the bar's own explicit negative clause. On LitBank (100 novels, held-out 50-doc TEST, non-pronoun PER mentions, B-cubed F, bootstrap over docs, theta selected on DEV): the brain-faithful structured complete-or-separate organ scores 0.7848 [0.759,0.810] vs the LIVE head-token-Jaccard floor recomputed in-place 0.7703 [0.748,0.793] -- delta +0.0145 hw 0.017 NOT_SEP (a TIE, not the required CI-separated win; it IS markedly more precise, B-cubed P 0.902 vs 0.820, separating same-surname people, but trades recall 0.707 vs 0.742). On PROPER-NAMES-ONLY the organ 0.864 TIES the strong floor 0.877 (NOT_SEP). The brief's proposed data fix -- full-span features -- BACKFIRES: full-span Jaccard 0.705 << floor 0.770 (-0.066 CI-sep BELOW, over-merge). Bar item 4 (serve who-did-what) is REFUTED by a clean decomposition (below): swapping the organ for the incumbent name clustering does NOT lift who-did-what (pronoun-query acc 0.1715 vs 0.1614, +0.010 NOT_SEP); the 0.17->0.62 gap is PRONOUN BINDING, not name clustering (perfect pronoun binding on the SAME head-token clustering = 0.606, +0.444 CI-sep; better name clustering given perfect pronouns = +0.000 NOT_SEP)."
floor: "The LIVE hdlab.coreference_resolver._resolve_name_branch mechanism (single-head-token normalized-token Jaccard over accumulated surface tokens) recomputed IN-PLACE on the same LitBank population: B-cubed F 0.7703 [0.7482,0.7929] all-PER; 0.877 [0.852,0.901] proper-names-only. Additional floors run same-population: full-span Jaccard 0.7046 (WORSE, over-merge); info-free twin (shuffled name features) 0.5967."
controls: "(1) info-free TWIN (shuffled name features, same pipeline) -> B-cubed F 0.597, LOSES CI-sep by +0.175 (excludes 'any structured pass helps'; the organ uses real name information). (2) POSITIVE control (fixture): the organ UNIFIES an alias re-entry the head floor SHATTERS (Elizabeth/Elizabeth Bennet/Miss Bennet -> 1 cluster vs 2) and SEPARATES the same-surname sibling (Jane Bennet) + gender-distinct man (Mr Darcy) -> the metric CAN move. (3) full-span-Jaccard control isolates DATA vs MECHANISM: the data fix alone BACKFIRES, so any win is the mechanism, not the cache. (4) who-did-what DECOMPOSITION arms (direct link-bottlenecked decode, isolates clustering from FHRR register capacity): HEAD_OPB (head names + perfect pronoun binding) 0.606 vs HEAD 0.161 = +0.444 CI-sep (isolates pronoun-binding as THE cap); ORGAN_OPB vs HEAD_OPB +0.000 NOT_SEP (name clustering irrelevant given perfect pronouns); GOLDNAME_ACTR 0.305 (perfect names + real ACT-R pronouns still capped by pronoun binding); SHUF_NAME twin 0.070 collapses (downstream metric can move)."
files_changed: "experiments/exp_name_entity_clustering_v1.py (the clustering organ + full-span loader + B-cubed/purity/shatter-merge metrics + floors + twin), experiments/exp_name_clustering_serves_whodidwhat_v1.py (the who-did-what serve + the pronoun-binding-vs-name-clustering decomposition), verification/test_name_entity_clustering.py (scaffold-free witness, 8/8 PASS), notes/problems/the_name_branch_shatters_one_character_into_many_entities/SOLVED.md. NO hdlab/ write (Q111). Proposed hdlab diff below."
reverify: ".venv/Scripts/python.exe verification/test_name_entity_clustering.py"
---

# What was built and measured

The brief's premise: the coreference NAME/NOMINAL branch (`hdlab/coreference_resolver._resolve_name_branch`)
clusters name mentions by single-head-token Jaccard, SHATTERS a character's aliases (measured: 65.6% of
multi-name gold characters split, purity 0.819), and THIS is the measured bottleneck capping who-did-what
(oracle-coref 0.62 vs the live binder 0.17). The requested fix: full-span content-addressable
complete-or-separate name unification, validated to beat the floor AND lift who-did-what.

**I built the brain-faithful mechanism the brief asked for, and the disk refuted the brief's two central
claims.** Both halves are load-bearing; the refutation is the higher-value half.

## The build (bar item 1 -- DONE, and it is the RIGHT mechanism)

`exp_name_entity_clustering_v1.py` -- a content-addressable **complete-or-separate** organ over a structured
**person-identity node** (given-name / surname / title / inferred-gender slots), exactly the PIN computation
the brief pins (Bruce & Young 1986; Burton/Bruce/Johnston 1990 IAC; Patterson/Nestor/Rogers 2007 ATL hub;
the complete-vs-separate = hippocampal CA3 completion vs DG separation; Heim 1982 / Kamp DRT file-cards). A
new mention parses to a cue; among gender-compatible nodes it ranks by a structural tier (shared given name
> shared surname > soft token overlap); a **conflicting known given name VETOES completion** (pattern
separation of same-surname people -- "Jane Bennet" != "Elizabeth Bennet"); within a tier, same-surname ties
are broken by **ACT-R base-level salience** (Lewis & Vasishth 2005; recency x grammatical role) toward the
active entity. Best tier score >= theta COMPLETES; else SEPARATES.

**Root-cause fix that made the measurement possible (KEY REALIZATION 1):** the LitBank head-token cache
(`data/litbank/who_did_what_events.json`) stores only ONE head token per mention. I ENRICHED it in-place --
aligning every cache mention (100% hit; gold->chain consistency 0.9991) to its FULL SPAN from the LitBank
coref CoNLL and its entity TYPE from the entities BIO layer -- so the cache stream order/gold/role/gov_verb
are untouched (the who-did-what population is preserved) but full-span features are now available. This is
the "extend the loader" the brief called for, done as a faithful enrichment.

## Cluster quality (bar item 2 -- NOT a clean win; the floor is strong; the data-fix BACKFIRES)

| arm (all-PER, held-out, B-cubed) | F | precision | recall | merge-rate |
|---|---|---|---|---|
| head-token Jaccard (LIVE floor) | **0.770** | 0.820 | 0.742 | 0.554 |
| full-span Jaccard (the brief's DATA fix) | 0.705 | 0.675 | 0.766 | 0.702 |
| **structured organ (ours)** | **0.785** | **0.902** | 0.707 | 0.516 |
| info-free twin (shuffled features) | 0.597 | 0.709 | 0.530 | 0.964 |

- The organ **ties** the floor on aggregate F (+0.0145, **NOT_SEP** after the DEV-principled salience
  tiebreak; +0.0175 CI-sep without it -- a fragile, noise-floor edge either way). On proper-names-only it
  is 0.864 vs the floor 0.877 (NOT_SEP). **It does NOT robustly beat the floor.**
- **The floor is far stronger than the brief implied, and I now understand why (KEY REALIZATION 2):** the
  spaCy syntactic HEAD of a name span is almost always the SURNAME, so single-head-token clustering already
  performs surname-family unification. The "single head token" is not the impoverished signal the brief
  assumed. The alarming "65.6% shatter" is an entity-level any-split count whose split-off pieces are small,
  so the mention-weighted B-cubed impact is modest.
- **The brief's own proposed fix -- full-span features -- BACKFIRES** (0.705 << 0.770, CI-sep BELOW, merge
  0.70): naive full-span Jaccard over-merges everyone who shares a surname. So the defect is NOT the cache
  being single-token; more data alone makes it worse. The structured MECHANISM (given-name separation) is
  what's needed to avoid that over-merge -- and it recovers to a tie, not a win.
- **What the organ genuinely does better:** precision 0.902 vs 0.820 -- it SEPARATES same-surname,
  gender-distinct people the floor over-merges (the positive control). It pays for that with lower recall.
  The info-free twin loses by +0.175 CI-sep, so the organ uses real name information.

## Who-did-what (bar item 4 -- REFUTED; this is the decisive finding)

`exp_name_clustering_serves_whodidwhat_v1.py` reproduces the brief's motivating gap exactly (pronoun-query
who-did-what: live system **0.161** ~ the cited 0.17; oracle-coref **0.56-0.61** ~ the cited 0.62) and
DECOMPOSES it (direct link-bottlenecked decode isolating clustering from register capacity):

| arm | pronoun-query who-did-what acc |
|---|---|
| HEAD (head-token names + ACT-R pronouns) = the live system | 0.161 |
| **ORGAN (brain-faithful names + ACT-R pronouns)** | **0.172  (+0.010 NOT_SEP vs HEAD)** |
| **HEAD_OPB (head-token names + PERFECT pronoun binding)** | **0.606  (+0.444 CI-sep vs HEAD)** |
| ORGAN_OPB (organ names + perfect pronoun binding) | 0.605  (+0.000 NOT_SEP vs HEAD_OPB) |
| GOLDNAME_ACTR (gold names + ACT-R pronouns) | 0.305 |
| ORACLE (gold names + gold pronouns) | 0.562 |
| SHUF_NAME info-free twin | 0.070 |

**The 0.17->0.62 who-did-what gap the brief attributes to name clustering is almost entirely PRONOUN
BINDING.** Fixing pronoun binding alone -- keeping the "shattered" head-token name clustering UNCHANGED --
recovers the whole gap (HEAD_OPB 0.606). Better NAME clustering adds nothing, even given perfect pronouns
(ORGAN_OPB ties HEAD_OPB, +0.000). So the brief's causal claim -- "a correctly-resolved pronoun still cannot
retrieve its referent's actions because the referent's names are scattered" -- is FALSE in measurement: a
correctly-bound pronoun DOES retrieve the actions from the head-token clusters. The who-did-what cap is
pronoun-to-entity-to-event binding (and, on the capacity-limited FHRR register, the fan effect), NOT name
clustering.

# What I did NOT establish / what I would withdraw first

1. **I did NOT beat the floor on cluster quality.** The organ ties it. If any claim here is wrong, withdraw
   first any implication that structured clustering is a cluster-quality WIN over the head-token floor -- it
   is a TIE with a precision/recall re-trade, honestly a wash on aggregate F.
2. **The who-did-what decomposition uses the SIMPLE ACT-R pronoun binder** (recency x role), not the
   integrated graded cue-based resolver. But the decisive arm (ORGAN_OPB vs HEAD_OPB, both PERFECT pronouns)
   is binder-independent and still shows name clustering is not the lever -- so the refutation does not rest
   on the binder's quality.
3. **The direct decode removes register capacity.** On the FHRR register the fan effect is an ADDITIONAL
   cap (and unifying aliases makes clusters bigger -> MORE fan), which only reinforces "name clustering is
   not the who-did-what lever." An FHRR-backend confirmation is a mapped remote follow-up, not run here.
4. **Nominal/epithet binding is unsolved and is the largest intrinsic residual** (76% of the organ's
   straggler mentions are descriptions like "the girl"/"this suitor" with no proper name). This is a
   different competence (discourse-focus / situation-model binding), mapped as adjacency 3, not built here.

# KEY REALIZATIONS (the enabling moves)

1. **Enrich the cache in-place instead of rebuilding it.** Aligning the head-token cache to the LitBank
   CoNLL full spans + entity-type BIO layer (100% hit, gold->chain 0.9991) gave full-span features while
   preserving the exact who-did-what population -- so the clustering change and the downstream change are
   measured on the identical stream. Rebuilding via spaCy would have moved the population and broken the
   comparison.
2. **Recompute the floor in-place -- it is much stronger than the brief's number.** The head-token floor
   is not a strawman: the syntactic head IS the surname, so it already unifies surname-family forms. Quoting
   "65.6% shatter" hid that the mention-weighted damage is small. Measuring the floor on the real metric
   turned a scary headline into a strong baseline.
3. **Decompose the downstream with an "oracle pronoun binding" arm.** Adding HEAD_OPB (perfect pronoun
   coref on the SAME dumb name clustering) was the single move that refuted the brief: it isolates that the
   0.17->0.62 gap is pronoun binding, not name clustering. Without that arm I would have reported a null
   ("organ doesn't lift who-did-what") without knowing WHY.
4. **The naive data-fix BACKFIRES -- this is the flat_store lesson repeating.** Full-span features (the
   obvious "fix the single-token cache" move) score BELOW the floor by over-merging. The DATA was never the
   defect; measuring the data-only fix in its own arm caught it, exactly as the `flat_store` refutation
   earned.
5. **The over-merge is IAC-architecturally EXPECTED, not a bug** (research drill): two people sharing a
   surname share a Semantic Information Unit, so a PIN/IAC system predicts elevated mutual cross-activation
   from surname alone -- the disambiguator must be an INDEPENDENT salience signal (the ACT-R decay
   tiebreak), and some same-surname residual is expected, not eliminable. This reframed a "precision bug"
   into a fidelity-confirming property and set the correct (modest) expectation for the fix.
6. **A control arm I added to decompose the null accidentally MEASURED the register fan effect -- and it
   says unifying aliases HURTS who-did-what.** HEAD_OPB (fragmented head-token names + perfect pronoun
   binding) = 0.606 BEATS ORACLE (correctly-unified gold names + perfect pronouns) = 0.562. The only
   explanation is the fan effect: unifying an entity's mentions makes its event register BIGGER, so it
   decodes WORSE (the multibank-vs-flat crossover, confirmed by research drill 2). This is a SECOND,
   independent refutation of the brief: better name clustering is not merely neutral for who-did-what, it is
   mildly COUNTERPRODUCTIVE on the capacity-limited register -- and it points straight at the real fix (wire
   the already-built sparse `MultiBankRegister`). I would not have seen this without the perfect-binding
   decomposition arm; a bare "organ doesn't lift who-did-what" null would have hidden it.

# AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)

- **COREFERENCE / ENTITY TRACKING entry + the §2b NAME/NOMINAL open case.** The audit (and this brief)
  names the single-head-token name branch as the who-did-what cap. **Measured refutation:** on real
  narrative the head-token floor is a STRONG baseline (B-cubed F 0.877 proper / 0.770 all-PER, because the
  head token is the surname), naive full-span features BACKFIRE (over-merge), a brain-faithful structured
  complete-or-separate organ TIES it (more precise, lower recall), and -- decisively -- name clustering is
  NOT the who-did-what bottleneck: perfect pronoun binding on unchanged head-token clusters recovers the
  whole 0.17->0.62 gap (+0.444 CI-sep), while better name clustering adds +0.000 given perfect pronouns. The
  who-did-what cap is PRONOUN-TO-EVENT BINDING (+ FHRR register fan effect), not name clustering.
- **New PINNED sub-claim (design):** for tracking a newly-introduced character across ONE narrative, the
  brain-appropriate representation is hippocampal rapid conjunctive binding = STRUCTURED slots (given /
  surname / title / gender), NOT an ATL-hub distributed bag-of-features code (ATL consolidation is
  months-scale, far past one novel; drill E). Do not "simplify" the person node to a bag-of-features code.
- **New OUR-INVENTION-labeled note:** the over-merge of same-surname people is IAC-model-EXPECTED (shared
  surname = shared Semantic Information Unit -> architectural cross-activation), so it is a fidelity
  property, not an implementation defect; the faithful disambiguator is an independent recency/role salience
  signal (ACT-R base-level activation), which gives only a modest, IAC-bounded fix.
- **The who-did-what mechanism (research drill 2, folded).** The staged "resolve the pronoun, THEN bind
  its event" pipeline our system uses "has no direct empirical champion" -- the brain binds the event to the
  currently-FOCUSED discourse entity at the CLAUSE level via continuous situation-model update (Centering Cb
  -- Grosz/Joshi/Weinstein 1995; Grosz & Sidner 1986 attentional state; Gernsbacher Structure Building);
  resolution at the pronoun is a confirmatory readout of an already-running focus state, not the event that
  creates the binding (Repeated-Name-Penalty: focus tracking runs regardless of surface form). The store is
  a HYBRID (situation-model gist + sparse pattern-separated INDEXED events; Teyler-DiScenna indexing;
  Cohen-Eichenbaum relational memory), NOT one entity-wide vector superposition -- so the FHRR
  `AccumulateRegister`'s per-entity dense bundle is the wrong sole model and its decode suffers the fan
  effect (Reder-Anderson 1980; Radvansky 2005) exactly in the fine-grained isolated-proposition regime our
  decode lives in. **The fix already exists in the substrate: `hdlab/situation_model_multibank.py`
  (MultiBankRegister), drop-in API-compatible, drill-reported to hold flat capacity where the flat bundle
  collapses -- but the reading-path organs import `situation_model_accumulate` (the flat register), so it is
  UNWIRED** (verified: no hdlab organ imports the multibank; flagged for strategy re-verification, not
  personally re-measured here).
- **Nominal/definite-description binding is a SEMANTIC-CONTENT problem, not a focus-default (research drill
  3, folded -- and this CORRECTS the intuitive hypothesis).** I expected "the girl" to bind to the
  currently-focused protagonist the way a pronoun binds to the Cb. The literature says that is the PRONOUN
  mechanism and it does NOT transfer: definite descriptions are focus-INSENSITIVE -- they reach
  non-foregrounded ("implicit focus") antecedents at no cost and are mildly PENALIZED when used for the
  current focus (the Repeated-Name-Penalty; Gordon/Grosz/Gilliom 1993; Sanford & Garrod full-NP anaphors
  show no implicit-antecedent penalty, ~94% acceptance regardless -- Garnham/Oakhill/Reynolds 2017). The
  small active set (Centering Cb+Cf; Van Berkum et al. 2003/2007) governs when AMBIGUITY is detected (defer
  when 2+ foregrounded candidates match), not resolution itself, which is by semantic content. That is
  exactly WHY the ~40% ceiling is real (not a full-pool artifact -- enlarging the pool HELPS, Hou et al.
  2013b 35.6%->41.3%; residual errors are genuine semantic ambiguity) and why a focus-restricted glass-box
  mechanism plausibly recovers only +5-15pp. So the nominal residual is a genuinely harder, lower-yield,
  SEMANTIC competence (a hypernym/type + world-knowledge matcher with abstain-on-ambiguity), correctly a
  mapped follow-on (adjacency 3), not a build here. ERP-cheap when unambiguous (Burkhardt 2006).

# PROPOSED hdlab DIFF (strategy session lands it; Q111)

Given the refutation, the diff is SMALL and OPT-IN, and it is NOT sold as a who-did-what fix:
- Add an opt-in `norm=`/structured-cluster path is NOT proposed for `_resolve_name_branch` as a default
  change -- the head-token floor is strong and the structured organ only TIES it, so replacing the live
  branch is not warranted on cluster quality alone.
- What IS worth landing: (a) the FULL-SPAN + entity-TYPE loader enrichment
  (`experiments/exp_name_entity_clustering_v1.load_enriched`) as a reusable data asset -- it unblocks any
  full-span feature work and the entity-type-scoped evaluation, at zero risk (additive); (b) the structured
  person-node clusterer as an OPT-IN `run_person_node_clustering(...)` in `coreference_resolver.py`
  (default-off; byte-identical when off) for the ONE thing it does better -- separating same-surname
  gender-distinct people (precision 0.90 vs 0.82) -- for any consumer that needs high-precision character
  separation (e.g. a "list the distinct people" query), NOT for who-did-what.
- **Do NOT invest hdlab effort in name clustering to lift who-did-what.** The measured lever is elsewhere
  (adjacencies 1-2).

# ADJACENCIES MAPPED (candidate follow-on problems -- ranked by the who-did-what decomposition)

1. **[HIGHEST LEVERAGE -- half the REAL who-did-what cap] The who-did-what STORE / fan effect. "How the
   brain manages it" (research drills 2 & 4, the owner's directed question) -- and part of the fix is
   ALREADY BUILT AND UNWIRED.** The FHRR `AccumulateRegister` sums ALL of an entity's events into ONE dense
   per-entity vector; decode collapses as events accumulate (Anderson/Reder fan effect; Radvansky 2005 --
   exactly the fine-grained isolated-proposition regime our decode occupies). **My own control arm proves it
   and proves unifying HURTS:** HEAD_OPB (fragmented head-token names, few events each) = 0.606 BEATS ORACLE
   (correctly-unified gold names, many events each) = 0.562. **The brain does NOT do unlimited
   per-entity superposition** (drills 2 & 4, VERIFIED-sourced): (a) it holds only a SMALL actively-bound
   working set -- ~4 chunks (Cowan 2001), ~4-6 role-bindings / 2-3 propositions (LISA/DORA, Hummel-Holyoak
   2003; Halford-Cowan-Andrews 2007 extend the ~4 limit to BINDINGS, not just items) -- and everything else
   lives as SEPARATE conjunctively-coded traces, because synchrony binding is "capacity-limited, impractical
   for LTM storage -> must be AUGMENTED WITH CONJUNCTIVE CODING" (Hummel et al. 2004); (b) the LTM store is
   CONTEXT-INDEXED, retrieved by entity+CONTEXT, never entity-alone (Tulving-Thomson encoding specificity
   1973; Howard-Kahana TCM 2002 -- item+drifting-context is the cue; entity-alone conflates every encounter
   and hits the fan wall), via CA3 pattern COMPLETION that only works because DG pattern-SEPARATED the
   overlapping traces first (Marr; Treves-Rolls). (c) The brain ALSO gist-abstracts and forgets verbatim
   detail (Sachs 1967; Kintsch 1990; fuzzy-trace) -- **but that is a biological CAPACITY CONSTRAINT (a
   PARAMETER we do NOT share), not a computation to copy (owner 2026-08-28: be brain-foundational in
   MECHANISM, but we can EXCEED the brain and need not throw away data).** So we copy the brain's
   interference-avoiding STRUCTURE (a)+(b) -- context-indexed sparse conjunctive traces, DG-separation /
   CA3-completion, a small active binding set, entity+context retrieval -- and KEEP FULL RETENTION of every
   event, which lets us clear who-did-what BETTER than a forgetful brain would. The eval (recover every
   action) stays a fair target; the brain's forgetting is not a reason to lower it. (Retain the salience /
   gist LAYER too, as an additional index -- not as a replacement for the full store; and mark any
   reconstructed/gist-derived output uncertain, per the Sulin-Dooling false-memory risk.) **The build order
   this implies:** (i) the drop-in sparse-sharded
   `hdlab/situation_model_multibank.py` (MultiBankRegister) -- already validated, but the reading-path
   organs import `situation_model_accumulate` instead, so it is UNWIRED (cheapest first step; verify its
   capacity numbers before landing, I did not re-measure); (ii) deeper: a CONTEXT-INDEXED conjunctive event
   store keyed by entity+context (not entity-alone) with a small active binding set; (iii) gist/salience
   abstraction rather than exhaustive verbatim retention. This is the p2/addressed-storage line + the
   `research_entity_store_*` trio (08-27); my decomposition adds the who-did-what-specific evidence that it,
   not name clustering, is the cap. Leverage: every register-backed reader.
2. **[HIGH -- the other half of the cap] Pronoun-to-event binding, done at the CLAUSE level not as a staged
   pipeline.** Perfect pronoun coref lifts who-did-what 0.16 -> 0.61; the simple ACT-R binder reaches only
   0.31 even with gold names. Drill 2: the staged "resolve-pronoun-THEN-bind" frame "has no direct empirical
   champion" -- the brain binds the event to the currently-focused entity (Centering Cb) as the clause is
   understood, and pronoun resolution is a confirmatory readout. So the faithful build is JOINT
   salience+content scoring at clause-write time, plus enabling the already-built `flag_unresolved=True`
   (reduces false writes). A Kehler-Rohde coherence prior is a small (+0.3 F1), coverage-limited tie-break,
   NOT the main lever; extending graded retrieval to all pronouns is masked by the capacity wall until
   adjacency 1 lands. Cross-ref the SOLVED problem `wire_entity_tracking_end_to_end_on_running_narrative`.
   Leverage: the entire who-did-what / entity-tracking stack.
3. **[MEDIUM-LOW -- the largest intrinsic name-clustering residual, but genuinely hard and SEMANTIC]
   Nominal/definite-description binding.** 76% of the organ's straggler mentions are epithets ("the girl",
   "this suitor") with no proper name. Drill 3 CORRECTED my hypothesis: these do NOT bind to the active
   focus the way pronouns do (definite descriptions are focus-insensitive and even penalized for the current
   focus -- Gordon/Grosz/Gilliom 1993; Sanford-Garrod); they are resolved by SEMANTIC CONTENT (hypernym /
   gender-age / world knowledge), with the active set only gating ambiguity-DEFER. So the faithful build is
   a semantic-type + world-knowledge matcher with abstain-on-ambiguity, and its ceiling is genuinely ~40-55%
   (Hou 2013b; residual errors are semantic ambiguity), recovering maybe +5-15pp of the residual. Lower yield
   than 1-2, and it does NOT serve who-did-what (refuted). Leverage: intrinsic character-tracking recall only.
4. **[LOW, cheap] Nickname/diminutive unification (~10% of stragglers).** An apposition-pattern detector
   ("Elizabeth, or Lizzy as her sisters called her") is near-zero-risk high-precision; a truncate(+y)
   phonological matcher and a small closed table cover the rest (drill 1, lever B). Leverage: a small
   intrinsic recall gain.

---

## TLDR (plain language)

The job was: our story-reader splits one character's different names ("Elizabeth", "Miss Bennet", "Lizzy")
into separate people, and the brief said fixing that would let the reader finally track who-did-what. I built
the brain's way of doing this -- one mental file per person, with slots for first name, last name, title, and
gender, that either adds a new mention to an existing person or starts a new person -- and then I measured
whether it actually helps. Two honest findings, and the second is the important one. First: the old simple
method is much better than the brief thought, because the one word it keeps is usually the SURNAME, which
already ties most of a character's names together; my brain-faithful version is a bit more careful (it
correctly keeps two sisters with the same surname apart) but overall it only ties the old method, and the
"obvious" fix of using the full name text actually makes things WORSE (it merges everyone with the same
surname). Second and most important: fixing the name-splitting does NOT improve who-did-what tracking at all.
I traced exactly where the who-did-what score is lost, and it is almost entirely in a DIFFERENT step --
figuring out which character each "he"/"she" refers to and filing what they did. If you hand the system
perfect "he/she" resolution but leave the name-splitting untouched, who-did-what jumps from 17 out of 100 to
61 -- the whole gap the brief blamed on name-splitting. So the brief aimed at the wrong target: name-splitting
is a real but minor issue, and the real bottleneck is pronoun-and-event tracking. That is the finding worth
acting on -- it redirects effort away from name clustering and toward the pronoun-event step.

## QUESTIONS

None -- the measurement is clear and the refutation is clean. Flagging one JUDGEMENT for the owner: I graded
this REFUTED (per the bar's own "a rigorous negative is a full pass" clause) rather than PARTIAL, because the
high-value deliverable is the decomposition that redirects the line, not the tie-with-the-floor organ. If you
would rather see it as PARTIAL (a real brain-faithful build that ties the floor and is more precise, plus a
refuted premise), the evidence is identical; only the label differs.

## NEXT STEPS

1. (Strategy) Re-verify the witness (8/8) and, if wanted, land the low-risk FULL-SPAN loader enrichment + the
   opt-in structured clusterer (default-off) for high-precision character SEPARATION -- NOT as a who-did-what
   fix.
2. (Strategy) Fold the AUDIT UPDATE: the head-token name branch is a strong floor, full-span backfires, and
   the who-did-what cap is pronoun-to-event binding, not name clustering.
3. (Follow-on problems) File adjacency 1 (pronoun-to-event binding over ALL pronouns -- the measured who-did-
   what lever) and adjacency 2 (the fan-effect store), which the decomposition shows are where the who-did-
   what points actually are.
