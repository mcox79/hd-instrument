---
slug: improve_the_common_noun_coref_candidate_quality_the_resolver_trails_string_identity
status: INTEGRATED
review:
review_text:
---

# PROBLEM: the live common-noun coreference resolver (the URG unified resolver the board's `common_noun_coref` dim scores) sits BELOW a trivial same-head string-identity baseline -- 0.4879 vs 0.5412 (-0.079 CI) on modern GUM test, n=2855 -- so the located leverage is CANDIDATE GENERATION + RANKING quality INSIDE the unified resolver (brain-faithful salience/accessibility candidate generation: Centering + Ariel accessibility + Lappin-Leass hard-filter-then-rank), NOT world knowledge (a typed-spoke type-license was MEASURED net-negative there); build better candidate generation + ranking so the resolver BEATS string-identity CI-separated on modern GUM common-noun coref, with a shuffled-candidate info-free twin LOSING and no pronoun-dim regress.

**slug:** `improve_the_common_noun_coref_candidate_quality_the_resolver_trails_string_identity` -- **opened:** 2026-09-07
by the strategy session, from this session's coref flip-gate. Common-noun coreference is the shared cap under three
downstream organs (affect experiencers, goal binding, relational reference), and the live resolver is CI-BELOW a trivial
baseline on the board's own scored dim -- so the fix is candidate quality, not more knowledge. **status:** CANDIDATE -- a
BUILD problem. You build + validate in `experiments/`; strategy lands any hdlab change (Q111). Glass-box, NO external LLM
at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's; provisional -- RE-RANK per the owner):** filed at `4` because the
> defect is LIVE and MEASURED on the board's own instrument (0.4879 vs a 0.5412 trivial floor), it caps three downstream
> reasoners at once (87% of the affect-experiencer loss is common-noun entities), and the fix is an extend-existing-organ
> BUILD (candidate/ranking inside the landed URG resolver), not a wiring job. It sits below the spatial/causal
> whole-subgraph front-end (the higher-fan-out relation-extraction lever) and is the SIBLING of the entity-type-KB brief
> (that one extends REACH to proper-name antecedents; this one closes the gap to string-identity). Set the real priority
> when promoted from CANDIDATE to OPEN.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do.
>
> **YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **"CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) -- RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one -- and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps -- AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) -- that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill -- do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across -- never a ceiling.
> Each fire: implement -> test (can-fail, strongest real floor, info-free twin LOSING) -> iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

> ## BRAIN-FOUNDATIONAL CHECKLIST (the owner's standing bar -- work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN -- how does the BRAIN do THIS?** Name the specific structure + computation and replicate that OPERATION as the FIRST move; mark each choice PINNED vs OUR-INVENTION. RESEARCH AGGRESSIVELY wherever you are unsure -- do not build the tractable thing and cite neuroscience after.
> 2. **REUSE -- does an existing organ already do what you need?** Check `tools/substrate_map.py` / `tools/reader_capabilities.py` / `hdlab/` FIRST; extend a matching organ rather than re-deriving it.
> 3. **GENERALIZE -- does this need to generalize, and HOW does the brain generalize it?** Build for that (register / novelty / transfer), not for the single test.
> 4. **HIT A WALL? GO DEEPER, DON'T STOP.** Research-drill WHY. If the brain can do it, it IS possible and we can too, once we understand it. A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, is what failed (fair test: can-fail, one-variable, real baseline).
> 5. **OPTIMIZE BY EXACT REPLICATION.** Evaluate aggressively, with great precision, EXACTLY how the brain does it, and replicate it exactly -- copy the computation, SWEEP (never adopt) the parameters. No half-effort: the closer we are, the better we do.
> 6. **PERFORMANCE vs THE BRAIN.** How does our performance compare to a competent brain/reader on this task? WHERE ALONG THE CHAIN do we lose signal? What EXACTLY differs between our implementation and the brain's mechanism (an itemized mechanism-diff)?
> 7. **ADJACENT COMPONENTS.** Map the capabilities, limitations, opportunities, and brain-foundational status of the adjacent components -- that seeds the next problems to address.
> 8. **COMPLETION BAR.** Is this a COMPLETE, EXCELLENT solved problem? Is it FULLY brain-foundational, conveying ALL the benefits of the brain function we replicate? If not, keep pushing toward a fully complete, exceptional solution.
>
> **(PHASE DIAGRAM -- the substrate is not locked to one regime.)** The substrate's operating point -- store DENSITY vs SPARSITY, dimensionality, binding regime, capacity, decay/gain, indexed-vs-superposed organization -- is FREE to change at ANY time, PER ORGAN. These are parameters to SWEEP, never fixed constraints. A wall "at this configuration" is a cue to MOVE the operating point on the phase diagram BEFORE ever calling it a ceiling.
>
> **(FULL-STACK UPSTREAM -- prototype THIS component AND its upstream, to EXCEL and EXCEED.)** Fully prototype THIS component AND the upstream brain-foundational component it depends on (and ALL the way upstream if the chain is deeper), and SHOW the capability can EXCEL and EXCEED -- make it happen. Then: (a) CONFIRM no other downstream consumer of the upstream optimization REGRESSES; (b) CONFIRM whether those other consumers should be REVISITED to be more brain-foundational, now making use of the newly-optimized upstream capabilities; (c) make SURE, VIA RESEARCH, that what you implement upstream is genuinely brain-foundational. **THE ONLY WAY YOU OVERCOME THIS WALL IS FOR EVERY COMPONENT -- YOU AND UPSTREAM -- TO BE BRAIN-FOUNDATIONAL.** Any wall you encounter must be FULLY RESEARCHED: the brain does it, so we can too -- and to do so we must UNDERSTAND it fully.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When a good reader meets "the doctor" again a page later, they keep a short list of people already mentioned who could be
that doctor and pick the best one by how recently and how prominently each was mentioned. Our reader does worse than a
dumb rule that just says "'the doctor' means the last thing already called 'a doctor'": on modern text it gets
common-noun links right LESS often than that rule does. So the problem is not that we lack facts about the world -- it is
that when the resolver builds its short list of candidate antecedents and ranks them, the list and the ranking are worse
than the simplest possible baseline. This job is to fix the candidate list and the ranking so the resolver at least beats
that dumb rule -- and to prove it with a scrambled-candidate version that falls apart, so we know the real ranking is
doing the work. No outside AI does the resolving; it must be a transparent, inspectable mechanism.

## 2. WHY THIS ONE
The defect is LIVE and MEASURED: on the board's OWN `common_noun_coref` instrument (the URG unified resolver) the reader
scores 0.4879 -- CI-BELOW a trivial same-head string-identity baseline of 0.5412 on modern GUM. A resolver that loses to
string-identity is not knowledge-starved, it is candidate/ranking-starved. And this one organ caps three others: common-
noun coreference is 87% of the end-to-end affect-experiencer loss (83.5% of experiencers are common-noun entities the
reader never tracks well) and it bottlenecks goal and relational binding (`INTEGRATION_LEDGER.md`). Test 4 (does a NUMBER
show the DEFECT costs us, not merely that an alternative exists?): YES -- the resolver is CI-below a trivial baseline on
the live scored dim, and the world-knowledge alternative was tried and REGRESSED it (-0.0196 CI-sep). The remaining,
brain-faithful lever is candidate quality, and it is the highest-leverage coref fix that stays inside the no-LLM invariant.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)
- **PINNED (the computation).** Coreference is INCREMENTAL, SALIENCE-RANKED antecedent retrieval over a small,
  agreement-filtered candidate set. Centering Theory (Grosz, Joshi & Weinstein 1995): a discourse keeps a list of
  forward-looking centers ranked by grammatical salience (subject > object > other) and preferentially re-mentions the
  backward-looking center. Ariel's Accessibility Theory (1990): the FORM of a referring expression signals antecedent
  accessibility -- a full definite common noun retrieves a less-activated, further, or type-identified antecedent, not the
  most-active one a pronoun would take. Lappin & Leass (1994): apply HARD morphosyntactic/agreement filters first (number,
  animacy, binding), THEN a weighted salience RANK (recency + grammatical role + parallelism). ACT-R base-level activation
  (recency + frequency) is the retrieval curve the landed URG resolver already uses. The load-bearing property: the brain
  GENERATES a small accessibility-shaped candidate set and RANKS it by salience -- candidate generation and ranking ARE the
  computation, not a knowledge lookup.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt).** The candidate window; the salience weights (recency vs grammatical
  role vs head-match vs modifier overlap vs parallelism); the abstention threshold; which agreement features are HARD
  filters vs soft cues; and every substrate operating-point knob. SWEEP these, adopt no number.
- **NOT brain-faithful (do NOT do).** An external LLM at inference (the invariant); a WORLD-KNOWLEDGE type-license as the
  common-noun lever -- MEASURED net-negative HERE (do NOT re-file it; the proper-name bridge is the SIBLING entity-type-KB
  brief); scoring a non-merging recency baseline and reading it as the LIVE gain (the flip-gate's documented p12 confound);
  a 19c corpus as load-bearing gold (BANNED 2026-09-06).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE -- do not re-derive):**
  - The board's `common_noun_coref` instrument IS the live URG unified resolver; it scores 0.4879, BELOW same-head
    string-identity 0.5412 (-0.079) on GUM test, n=2855 (this session's coref flip-gate; harness
    `experiments/exp_board_coref_gum_v1.py`). Recompute BOTH floors on your own population.
  - The typed-spoke TYPE-LICENSE (C5 is-a + C6 part-whole as a binary licensing filter) REGRESSES the live pick
    0.4879 -> 0.4683 (-0.0196 CI-sep) and its info-free shuffled-graph twin is indistinguishable -- MEASURED-OFF in the
    flip-gate (`hdlab/situation_reader.py` `commonnoun_type_license`; `board_commonnoun_typelicense_dimension`). World
    knowledge is NOT the common-noun lever here.
  - The URG resolver + the landed p12 coref stack (`compose_the_unified_referent...`) lifted he/she PRONOUN coref +0.0823
    CI-sep on GUM (0.5032 -> 0.5855) via candidate/ranking fixes to EXISTING machinery, named-antecedent no-regress
    (0.6019 -> 0.6555) -- the SAME class of lever this problem needs for common nouns. `hdlab/commonnoun_binder.py`
    (situation-gated head-match former + event-centrality tie-break) is landed + default-ON (+0.0128 CoNLL over
    surface-head).
  - Common-noun coref is 87% of the affect-experiencer end-to-end loss and caps goal/relational binding
    (`notes/INTEGRATION_LEDGER.md`); the modern blind-head no-LLM ceiling is ~0.541 with the ~81%-needs-world-knowledge
    residual BARRED at inference (that residual is the SIBLING entity-type-KB brief's offline asset, not this one).
- **INFERRED (you must prove):** that a brain-faithful CANDIDATE-GENERATION + SALIENCE-RANKING upgrade INSIDE the
  unified/common-noun resolver (agreement HARD-FILTER -> Centering/Ariel/Lappin-Leass salience RANK over an
  accessibility-shaped candidate set) BEATS same-head string-identity CI-separated on modern GUM common-noun coref, with a
  shuffled-candidate info-free twin LOSING and no pronoun-dim regress; OR a rigorous LOCATED NEGATIVE naming the residual
  with counts (e.g. "candidate generation reaches the gold antecedent in the set X% of the time but ranking cannot
  separate it from the same-head distractor because ... enumerated" -- a distinct ranking-feature or mention-detector organ).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-file the WORLD-KNOWLEDGE type-license -- it is MEASURED net-negative on the LIVE instrument (0.4879 -> 0.4683,
  twin indistinguishable). The proper-NAME bridge ("the artist" -> "Zurbaran"), unreachable by WordNet, is a SEPARATE
  problem (the `acquire_wikidata_p31_entity_type_kb_for_name_bridge_coref` brief) -- do NOT fold it here.
- Do NOT rebuild `commonnoun_binder` or the `unified_referent` resolver from scratch -- both landed. EXTEND their
  candidate/ranking path.
- Do NOT score a NON-MERGING recency baseline and read it as the live gain (the flip-gate's p12 confound: the type-license
  SOLVED's +0.0116 was measured on a different, non-merging baseline; on the live URG resolver the same filter REGRESSED).
  Score the LIVE resolver on the board instrument.
- Do NOT use a 19c corpus (McGuffey / LitBank) as load-bearing gold; do NOT use an external LLM at inference.
- Run `python tools/before_you_start.py "<what you are about to do>"` and `tools/experiment_index.py query "coref"` /
  `"candidate"` / `"salience"` / `"centering"` / `"antecedent"` / `"commonnoun"` (SINGLE keywords) before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: run `python tools/substrate_map.py` and `python tools/reader_capabilities.py` -- confirm the URG unified
  resolver is the live `common_noun_coref` scorer and `commonnoun_binder` is default-ON; skim `hdlab/` (`graded_coref_pick`,
  `coreference_resolver`, `event_centrality_coref`, `unified_referent`, `commonnoun_binder`) so you extend the existing pool
  pick, not beside it.
- READ IN FULL (build ON them, credit them): the TWO coref SOLVED.md files --
  `notes/problems/form_a_discourse_referent_for_every_entity_not_just_named_ones_common_noun_coref/SOLVED.md` (surface-head
  OVER-MERGE, the situation gate, and the type-license's MEASURED regression) and
  `notes/problems/compose_the_unified_referent_with_the_incumbent_graded_pick_pool_for_a_live_coref_gain/SOLVED.md` (the
  three stacking candidate/ranking rungs that lifted pronoun coref) -- and `notes/BRAIN_FOUNDATIONAL_AUDIT.md` coref entries.
- INSPECT what you REUSE: `hdlab/unified_referent.py` (the Resolver -- ACT-R base-level over discourse referents);
  `hdlab/commonnoun_binder.py` (head-match-gated former + event-centrality tie-break); `hdlab/graded_coref_pick.py` +
  `hdlab/event_centrality_coref.py` (the pool pick + salience tie-break); the live wire in `hdlab/situation_reader.py`
  (`commonnoun_situation_gate`, `commonnoun_type_license` MEASURED-OFF, `unified_referent`).
- CONSUME the measured wall (do NOT re-derive): `experiments/exp_board_coref_gum_v1.py` (the `common_noun_coref` board dim +
  `board_commonnoun_typelicense_dimension`) -- this is your scorer; recompute string-identity + the live-resolver floors on
  YOUR own population.
- ENUMERATE what the resolver does TODAY (an absence claim requires an enumeration, not a search): for a sample of GUM
  common-noun anaphors list the gold antecedent, whether the resolver's candidate SET contains it, and whether ranking put
  it FIRST; separate "not generated" from "generated but mis-ranked". State how you enumerated in your submission.
- GOLD: modern GUM common-noun coref is on disk (`data/corpora/gum/`). You are PRE-AUTHORIZED to acquire an open MODERN
  coref gold under `data/corpora/<name>/` with a REPRODUCIBLE pinned fetch script in `experiments/` + a provenance note. Do
  NOT lean on 19c LitBank (informational only).

## 7. THE BAR
PASSES only with ALL of:
1. **A glass-box CANDIDATE-GENERATION + SALIENCE-RANKING upgrade INSIDE the unified/common-noun resolver (built +
   validated in `experiments/`; strategy lands any hdlab change, Q111).** COPY the computation (agreement HARD-FILTER then
   Centering/Ariel/Lappin-Leass salience RANK over an accessibility-shaped candidate set; ACT-R activation as the recency
   curve). SWEEP the window, the salience weights, the filter set, the abstention threshold. NO external LLM.
2. **It BEATS same-head string-identity CI-separated on MODERN GUM common-noun coref**, floor recomputed on the SAME
   population (string-identity 0.5412 is the floor to beat; the live URG resolver 0.4879 is the incumbent it must also
   clear). Report CI half-width + null p95; recompute each floor on the item's OWN population; NO number crosses
   populations / scorers.
3. **The info-free twin LOSES CI-separated:** shuffle the candidate set / the salience scores (a random other-mention
   candidate, or permuted scores, same shape + counts) -- the gain must come from THIS candidate set + ranking, not from
   "keeping any candidate helps".
4. **NO pronoun-dim regress + NO named-antecedent regress** (the p12 stack's gains hold): enumerate every live consumer of
   the resolver's clusters (the coref dims, affect experiencers, goal / relational binding) and confirm none regress. A
   can-fail POSITIVE control string-identity CANNOT pass: a DIFFERENT-head same-entity common-noun anaphor ("the doctor" ...
   "the physician") the salience rank links but same-head cannot.
5. **NO-regress full-stack (FULL-STACK UPSTREAM).** Prototype THIS resolver AND its upstream (the mention detector / NP-head
   chunker + the agreement features it filters on) all the way to EXCEL/EXCEED; then CONFIRM no other live consumer regresses
   and note which should be REVISITED to exploit the better clusters. The reader stays byte-identical where the upgrade is off.
6. **One-screen summary:** candidate/ranking design -> modern gold + provenance -> string-identity + live-resolver floors ->
   twin -> common-noun-coref margin (CI half-width + null p95) -> upstream no-regress -> what breaks -> verdict. Heavy -> REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "candidate generation reaches the gold antecedent X% but ranking cannot beat
same-head because the residual is the different-head world-knowledge bridge, N of M, which routes to the entity-type KB not
salience -- located and counted"; OR "salience ranking beats string-identity on the referential subset but the mention
detector floods the candidate set with non-referential heads, enumerated -- a distinct upstream NP-head-chunker organ").

## 8. FILES AND ENTRY POINTS
- **REUSE (landed -- do NOT rebuild):** `hdlab/unified_referent.py` (the Resolver); `hdlab/commonnoun_binder.py`
  (situation-gated former); `hdlab/graded_coref_pick.py` + `hdlab/event_centrality_coref.py` (the pool pick + salience
  tie-break); `hdlab/coreference_resolver.py`; the live wire in `hdlab/situation_reader.py`.
- **CONSUME (the measured wall + the scorer -- do NOT re-derive):** `experiments/exp_board_coref_gum_v1.py`
  (`common_noun_coref` dim + the typelicense dim); `notes/INTEGRATION_LEDGER.md` (the 0.541 no-LLM blind-head context +
  coref-as-shared-cap).
- **Gold:** modern GUM common-noun coref on disk (`data/corpora/gum/`); a pinned modern coref gold under
  `data/corpora/<name>/` if you acquire more.
- **Motivation + fence:** the two coref SOLVED.md files + `notes/BRAIN_FOUNDATIONAL_AUDIT.md` coref entries. Build in
  `experiments/` + `verification/`; strategy lands any hdlab change (Q111). Heavy -> REMOTE
  (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`). Fold an **AUDIT UPDATE** into `notes/BRAIN_FOUNDATIONAL_AUDIT.md`
  (common-noun coref now beats / does-not-beat string-identity via salience candidate-generation + ranking on modern gold).

## DO NOT QUOTE / DO NOT REDO
- Do NOT quote the type-license SOLVED's +0.0116 as a LIVE gain -- it was on a non-merging recency baseline; on the live URG
  resolver the same filter REGRESSED -0.0196 CI-sep. Score the live resolver on the board instrument.
- Do NOT quote 0.4879 / 0.5412 across scorers or populations (GUM test n=2855, board `common_noun_coref` dim); recompute both
  on your own population. No number crosses scorers / populations.
- Do NOT re-file the world-knowledge type-license (measured net-negative), and do NOT fold the proper-name bridge here (that
  is the entity-type-KB brief). Do NOT lean on a 19c corpus as load-bearing gold (BANNED 2026-09-06 -- informational only);
  do NOT use an external LLM at inference (the invariant). Strategy owns any hdlab landing (Q111).

---

**TLDR (plain English):** Our reader is worse at linking repeated common-noun mentions (like a second "the doctor" back to
the first) than a dumb rule that just matches the same word -- so the problem is not missing world knowledge, it is that the
reader builds a poor short-list of possible antecedents and ranks them poorly. The fix is to generate that short-list and
rank it the way people do -- by how recently and prominently each candidate was mentioned, after ruling out ones that do
not agree -- and to prove it beats the dumb same-word rule on modern text, with a scrambled-candidate version falling apart
so we know the real ranking is carrying the load. This one fix lifts the reader's tracking of characters, which in turn caps
how well it reads feelings, goals, and relationships.

**QUESTIONS:** none.

**NEXT STEPS:** the solver runs VERIFY BEFORE YOU START (confirm the URG unified resolver is the live `common_noun_coref`
scorer and that the world-knowledge type-license was measured net-negative there), reads the two coref SOLVEDs in full,
enumerates on GUM whether the gold antecedent is generated-and-ranked-first vs generated-but-mis-ranked vs not-generated,
builds a brain-faithful candidate-generation + salience-ranking upgrade inside the resolver (agreement hard-filter then
Centering/Ariel/Lappin-Leass rank), and reports the common-noun-coref margin over string-identity with the shuffled-candidate
twin and no pronoun-dim regress -- or a located negative naming the residual (the different-head world-knowledge bridge that
routes to the sibling entity-type-KB brief, or the mention detector upstream).
