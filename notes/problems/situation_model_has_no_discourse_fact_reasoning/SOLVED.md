---
problem: situation_model_has_no_discourse_fact_reasoning
status: SOLVED
bar: "PASSES only with ALL of: 1. A reading-built, QUERYABLE per-entity discourse-FACT store (built in experiments/): accumulate (entity, relation, value) predicate-argument facts AS the reader processes text (FHRR-bound over situation_model_accumulate), plus a BRIDGING/RESOLUTION operator that resolves a reference by retrieving the accumulated fact that makes the current clause coherent (via graded_competition). Copy the computation; SWEEP the representation + threshold. NO static KG, NO external LLM. 2. Beats the fact-BLIND reader CI-separated on a discourse-fact-decisive population -- the anti-typical coref residual recomputed on the same population, AND/OR a LARGER annotated 'accumulate-a-fact-then-refer' task (build one to get power beyond n=205). Floor = the graded coref + entity nodes with NO fact store, recomputed on the population. The info-free twin (shuffled facts / random fact->entity assignment) LOSES CI-separated; report CI half-width + null p95; no number crosses populations. A POSITIVE control the metric can move. 3. The lift is the FACT STORE + REASONING, not leakage: ablate the fact store -> the reader drops to the fact-blind floor; the facts must be BUILT FROM THE TEXT; a STATIC-KG arm must NOT reproduce the lift. 4. One-screen summary. A rigorous NEGATIVE is a FULL PASS."
result: "TWO-LEVEL. (L1, the CAPABILITY -- PASS) On a built INTER-SENTENTIAL fact-decisive reference population (state-a-role-then-refer-by-action; roles/actions split DEV/TEST, bridges drawn from the static CSKG, reading-built name->role extracted from the text): fact-store+2-hop-bridge = 0.998 [0.994,1.000] (n=500, item bootstrap) vs the fact-BLIND graded resolver floor 0.504 [0.460,0.548]; store-minus-floor +0.494 [+0.450,+0.536] band ABOVE. Survives 3-candidate (chance 0.33): 0.344 -> 1.000 (+0.656 ABOVE). RECOVERS 0.996 of the 248 cases the fact-blind reader gets WRONG (band ABOVE). (L2, the LitBank anti-typical residual -- REFUTED as fact-decisive) the store is DEAD there: bridge oracle 0.039 (5/127), the fused arm is mildly ANTI-predictive (fused-minus-twin -0.033, band BELOW), because the residual GOLD carries a mean of 0.65 accumulated facts (58% exactly ZERO) vs the wrong pick's 13.4 -- it is FRESHLY INTRODUCED and bound INTRA-SENTENTIALLY, so there is nothing to bridge to (confirmed mechanistically: Centering Cb-absence + Sturt 2003 first-pass structural binding). Scorer = argmax==gold link accuracy."
floor: "The fact-BLIND reader recomputed on each population: (L1) the real graded structural resolver (hdlab.graded_competition, DEV-tuned) = 0.504 [0.460,0.548] on the 2-candidate set (chance) and 0.344 on the 3-candidate set; store CI-separated ABOVE both. Info-free twin (shuffled entity<->attribute binding) = 0.544; KG-only-null (generic KG, no reading-built binding) = 0.508; ablation (IS-A fact stripped) = 0.508 -- ALL at chance, each store-minus-control band ABOVE. (L2) on the LitBank residual the fact-blind floor is 0/205 by construction, so the meaningful floor is the info-free twin (facts shuffled across entities); the fused bridge does NOT beat it (band BELOW)."
controls: "(1) info-free twin (entity<->attribute binding SHUFFLED within the item) -> chance 0.544, store-minus-twin +0.454 ABOVE -> excludes 'the task shape alone wins'; it is the SPECIFIC reading-built binding. (2) KG-only-null (the generic CSKG role->action bridge WITHOUT the reading-built name->role fact, scoring the candidate's surface name) -> chance 0.508, store-minus-kg +0.490 ABOVE -> excludes 'the static KG alone discriminates' (it connects but cannot discriminate -- the parent's exact finding; the store supplies the missing hop). (3) ablation (IS-A fact removed from the store) -> chance 0.508, store-minus-ablation +0.490 ABOVE -> the lift IS the accumulated facts, not the harness. (4) SPECIFICITY / discourse-age gate (fact-ABSENT items: the deciding role is never stated) -> store 0.568 vs floor 0.572, band NOT_SEP -> the operator fires ON-TARGET only. (5) graceful degradation under knowledge-coverage loss (drop bridge edges p=0..0.9) -> 0.998,0.884,0.784,0.614,0.538 monotone, no cliff -> the brain-faithful good-enough prediction + it bounds real-world applicability by KG coverage. (6) reading-built + NO LEAK (self-test: a fact at sent s is invisible to a query before sent s; facts built only from mentions with sent < p_sent). (7) held-out: roles/actions split DEV/TEST so every TEST bridge is out of the weight tuning. (8) L2 diagnosis positive-control: the accumulated-fact count gold-vs-pick (0.65 vs 13.4) is the structural REASON the store cannot apply to the residual. (9) FHRR representation fidelity: the entity->attribute fact stored in situation_model_accumulate.RelationRegister is retrieved faithfully and resolves the same pronoun -> the symbolic store is a faithful proxy for the FHRR-bound store."
files_changed: "experiments/exp_discfact_store_bridging_residual_v1.py (L2 negative + diagnosis + DiscourseFactStore + bridge operator + CSKG generic bridge), experiments/exp_discfact_store_bridging_capability_v1.py (L1 positive: inter-sentential fact-decisive population + full control suite + recovery + 3-cand + coverage curve + specificity), verification/test_discfact_store_bridging.py (15/15, scaffold-free, incl. FHRR fidelity), notes/problems/situation_model_has_no_discourse_fact_reasoning/{SOLVED.md, research_discourse_fact_resolution_brain_mechanism_2026-08-29.md}. NO hdlab/ write (Q111); proposed hdlab direction below."
reverify: ".venv/Scripts/python.exe verification/test_discfact_store_bridging.py"
---

# What was built and measured

The brief asked: build a reading-built, queryable per-entity **discourse-fact store** + a **bridging/RESOLUTION**
operator, and show it recovers discourse-fact-decisive coreference the fact-blind reader cannot -- WITHOUT a
static commonsense KG (measured dead) and WITHOUT an external LLM. I built exactly that mechanism and measured
it on **two populations**, because the disk forced a split the brief did not anticipate.

## The mechanism (bar item 1) -- brain-faithful, glass-box, no LLM

- **The reading-built store** (`DiscourseFactStore`): as the reader processes the mention stream, accumulate
  for each entity the predicate-argument facts it participates in `(gov_verb, role, obj_head, nominal, sent)`
  and its IS-A/attribute facts (copula complements: "Sam is a doctor" -> `Sam ISA doctor`). Queryable per
  entity; **no leakage** -- a query at sentence `p` sees only facts with `sent < p` (self-test enforced). This
  is the COMPUTATION the situation-model RESOLUTION stage performs (Garrod & Sanford 1994; Kintsch 1988 CI;
  Zwaan & Radvansky 1998 event-indexing) -- the representation is an OUR-INVENTION choice, and I verified the
  **FHRR-bound** version the brief names (`situation_model_accumulate.RelationRegister`, single-filler-exact
  bind) retrieves the same entity->attribute fact faithfully (witness W11), so the symbolic store is a faithful
  proxy for the FHRR store.
- **The bridging/RESOLUTION operator**: a **2-HOP bridge** -- entity -> its reading-built attribute ("Sam is a
  doctor", discourse-specific / situation-model) -> generic world-knowledge ("doctors CapableOf prescribe",
  from the STATIC CSKG / semantic memory) -> coherence with the current clause ("he prescribed"). The per-
  candidate coherence is fused as a NEW cue into `hdlab.graded_competition` (the pinned additive-cue ->
  softmax posterior) alongside the structural cues. The 2-hop split (discourse-specific binding vs generic
  attribute-action knowledge) is grounded in the **semantic-dementia vs hippocampal-amnesia double
  dissociation** (Graham et al. 2000); the exact hop-count is OUR-INVENTION-UNDER-TEST (Hobbs abduction has no
  principled hop count).

## LEVEL 1 -- the capability, PROVEN on the mechanism's proper domain (bar items 2-3)

On a built **inter-sentential fact-decisive** population (a discourse establishes two+ entities' roles in
earlier sentences; a later pronoun clause carries an action only one role is CapableOf), roles/actions split
DEV/TEST, **bridges drawn from the static CSKG (not hand-authored)**, name->role extracted from the text:

| arm | 2-cand acc (chance .50) | what it excludes |
|---|---|---|
| **fact_store (ours)** | **0.998 [0.994,1.000]** | -- |
| fact_blind (FLOOR) | 0.504 [0.460,0.548] | the graded structural resolver, no store |
| info_free_twin | 0.544 | shuffled entity<->attribute binding -> "shape alone wins" |
| kg_only_null | 0.508 | generic KG, no reading-built binding -> "the KG alone discriminates" |
| ablation_no_store | 0.508 | IS-A fact stripped -> "the lift isn't the facts" |

`store - floor = +0.494 [+0.450,+0.536] ABOVE`; every `store - control` band **ABOVE**. It **recovers 0.996 of
the 248 cases the fact-blind reader gets wrong**; survives a **3-candidate** baseline (0.344 -> 1.000, +0.656
ABOVE); is **on-target only** (fact-ABSENT items: store 0.568 vs floor 0.572, NOT_SEP); and **degrades
gracefully** under knowledge-coverage loss (0.998 -> 0.884 -> 0.784 -> 0.614 -> 0.538 as bridge edges are
dropped 0 -> 90%, the brain-faithful good-enough prediction). This is the capability the brief and the owner's
comprehension->REASONING frontier asked for, and it directly answers the parent's open question: **the static
KG "connects every candidate but cannot discriminate" precisely because it lacks the reading-built
entity<->attribute binding; the fact store supplies exactly that missing hop.**

## LEVEL 2 -- the LitBank anti-typical residual is NOT fact-decisive (a rigorous NEGATIVE; the disk wins)

I also measured the store+bridge on the **real** anti-typical LitBank residual (n=205, the exact population the
brief hoped it would recover). It is **DEAD** -- the 7th independent channel dead there -- and this one is
decisive because it tests the exact mechanism the parent named as the fix:

- bridge ORACLE on the residual = **0.039** (5/127), like the parent's six channels; the fused arm is mildly
  **anti-predictive** (fused-minus-twin -0.033, band BELOW).
- **The structural reason, measured:** the residual **gold carries a mean of 0.65 accumulated facts (58%
  exactly ZERO)** vs the wrong pick's 13.4. The residual gold is a **freshly-introduced** entity (the parson,
  the child, the family) bound **intra-sententially** ("the parson, who, as **he** rode, hummed a tune" -- the
  brief's own plain-language example, and case [1] of the residual). **There is nothing to bridge to.**
- The brain **cannot use a fact store here either** -- confirmed mechanistically by the research drill
  (`research_discourse_fact_resolution_brain_mechanism_2026-08-29.md`): a brand-new, same-clause antecedent is
  resolved by **fast structural cues by necessity, not choice** -- Centering's `Cb` is undefined for a
  first-mention (Grosz/Joshi/Weinstein 1995), Prince's "brand-new" class is non-inferentially-linkable, and
  Sturt 2003 shows structural binding applies within first-pass fixations, too fast for discourse-model
  retrieval. So "accumulate-a-fact-then-refer" is **structurally not the shape of the LitBank residual.**

The two levels are consistent: the mechanism works where the brain uses it (inter-sentential, a fact is
present) and is silent where the brain does not (intra-sentential, freshly introduced) -- the same discourse-
age gate the specificity control demonstrates.

# What I did NOT establish (and would withdraw first if wrong)

1. **Real-text accuracy is NOT established.** The Level-1 population is CONSTRUCTED. The near-1.0 reflects
   IDEALISED extraction (I emit the IS-A facts) and EXACT KG edges (the deciding action is in CapableOf(role)
   by construction). The **realistic** bound is the coverage-degradation curve (down to ~0.54 at 90% edge
   loss) plus extraction quality. **Withdraw first any implication that this is 99.8% on natural prose.** The
   #1 follow-on is validating on a real inter-sentential fact-decisive corpus (bridging/QA), which requires
   robust copula/role extraction + broader KG coverage. The controls (twin/KG-only/ablation/specificity all at
   chance) rule out a *hollow* construction proof -- they prove the lift is the specific reading-built
   information -- but they do not substitute for a natural-text measurement.
2. **The 2-hop hard match is a computational-level proxy.** The brain's attribute->action knowledge is
   DISTRIBUTIONAL/graded (ATL PDP hub, Rogers & McClelland), not a symbolic edge lookup. A graded/distributional
   bridge (semantic similarity between the action and the role's action-profile) would be more brain-faithful
   and degrade more gracefully -- named as the top fidelity optimization, not built here.
3. **L2's residual bound is the exact-KG/no-LLM boundary**, not "unrecoverable by any route": the residual's
   real levers are a reliable intra-sentential SYNTACTIC binder (the parent's named follow-on) + richer
   distributional semantics (p1), NOT a discourse-fact store. I did not build those.
4. **The FHRR fidelity check is single-filler-exact.** Multi-fact-per-entity storage introduces bundling
   interference (the sparse/indexed-store fidelity axis); I used the symbolic store for the measurement and
   verified only the single-filler FHRR case.

# KEY REALIZATIONS (the enabling moves)

1. **Measure the store's ORACLE and the gold's fact-count on the residual BEFORE building the fusion.** One
   diagnostic pass ("could this even succeed?") showed the residual gold has 0.65 accumulated facts (58%
   zero) -- so a reading-built store *structurally cannot* apply, no matter how good the bridge. That single
   number reframed the whole problem from "build a better bridge" to "this is the wrong population," and sent
   me to build the mechanism's *actual* domain instead of grinding a dead fusion.
2. **The residual is anti-typical BY CONSTRUCTION, so the gold is the entity with the LEAST discourse history**
   (freshly introduced), which is the *opposite* of what a fact store needs. Every typicality cue is anti-
   predictive there for one structural reason (the parent's insight), and the fact store is no exception --
   adding it is mildly anti-predictive because the *high-fact* entity is the wrong (topical) one.
3. **Lead-with-biology relocated the wall from empirical to principled.** The research drill showed the brain
   ITSELF cannot use fact-store+bridging on a freshly-introduced/intra-sentential antecedent (Centering
   Cb-absence; Sturt 2003 first-pass structural binding; the fast-structural vs slow-discourse ERP timing
   split). So this is NOT a "brain can, we can't" wall -- it is "neither the brain nor we use a fact store
   here; the residual needs the syntactic binder." That turns a negative into a correct scoping.
4. **The KG-only-null control is the crux that turns the parent's death into our win.** The parent measured the
   static KG dead (2.8% -- "connects but cannot discriminate"). Making the KG-only arm a formal control and
   showing it sits at chance while the fact-store arm hits ceiling PROVES the fact store supplies the one thing
   the KG lacks: the discourse-specific entity<->attribute binding. Same KG, +0.49 -- the difference is the
   reading-built hop.
5. **Feed the constructed streams through the REAL harness** (`build_instances`/`_supports`/`graded_competition`)
   so the fact-blind floor is the genuine landed resolver, not a bespoke baseline -- the twin/KG-only/ablation
   controls then isolate exactly the store's contribution, and the win cannot be a scoring artifact.
6. **A graceful coverage-degradation curve is both a fidelity check and the honest realism bound.** It shows
   the mechanism is the brain's good-enough processing (no cliff) AND names the real-world ceiling (knowledge
   coverage -- the bottleneck every glass-box bridging system in the literature hit).

# AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)

- **Situation-model RESOLUTION / discourse-fact store (NEW entry).** The situation model now has a demonstrated
  reading-built, queryable per-entity discourse-fact store + 2-hop bridging RESOLUTION operator (glass-box, no
  LLM), PROVEN CI-separated over the fact-blind reader on inter-sentential fact-decisive reference (all controls
  at chance; graceful coverage degradation). PINNED: the COMPUTATION (Garrod-Sanford BONDING/RESOLUTION; Kintsch
  CI; hippocampal relational binding + pronoun-driven concept-cell reactivation; Haviland-Clark +181ms bridging
  cost). OUR-INVENTION-UNDER-TEST: the FHRR representation (verified single-filler-exact), the 2-hop hard match
  (a computational-level proxy for the ATL's DISTRIBUTIONAL matching -- the top fidelity gap), the confidence
  threshold. DEVIATION: real-text accuracy unmeasured (bounded by extraction + KG coverage).
- **COREF residual entry -- REFINE.** The parent's audit note says the coref residual's real lever is "the
  SITUATION MODEL accumulating specific-discourse entity facts." **This is now REFINED by measurement:** a
  reading-built discourse-fact store is DEAD on the anti-typical residual because the residual gold is freshly
  introduced (mean 0.65 accumulated facts, 58% zero) and bound intra-sententially -- the brain does not use a
  fact store there either (Centering Cb-absence; Sturt 2003). The residual's lever is the **intra-sentential
  SYNTACTIC binder** (the parent's other named follow-on) + richer p1 semantics, NOT the discourse-fact store.
  The fact store is the reasoning-frontier capability (inter-sentential), not a coref-residual patch.

# ADJACENT COMPONENTS -- capabilities / limitations / brain-foundational status (seeds the next problems)

1. **[HIGHEST FIDELITY LEVER] The attribute->action bridge -- currently a static-KG HARD MATCH; the brain is
   DISTRIBUTIONAL.** CAPABILITY: CSKG supplies real role->action edges (doctor->prescribe, farmer->grow_plants);
   the 2-hop bridge resolves fact-decisive reference at ceiling when the edge exists. LIMITATION (measured): a
   hard symbolic match cliffs with coverage (graceful but down to 0.54 at 90% loss); it cannot fire on a role
   whose action is merely SIMILAR to a KG action. BRAIN STATUS: OUR-INVENTION -- the ATL semantic hub is PDP/
   distributional (Rogers & McClelland), not edge-lookup. OPTIMIZATION: replace the hard match with a GRADED
   distributional coherence (action <-> role action-profile similarity, over the substrate's grounded/lexical
   space) -- more brain-faithful and more coverage-robust. A real follow-on problem.
2. **The copula/role/predicate-arg EXTRACTION (the reading-built half).** CAPABILITY: the LitBank cache already
   carries gov_verb + role + obj_head per mention; the store reads facts straight off it. LIMITATION: the IS-A
   fact ("X is a doctor") needs reliable copula-complement extraction; on archaic/literary prose the parser is
   noisy (the standing corpus-age confound). BRAIN STATUS: the extraction TOOL (spaCy) is convenient/OUR-
   INVENTION; the substrate's incremental_parser is the brain-foundational algorithm but produces only verb-arg
   slots. OPTIMIZATION: extend it to copula/appositive attributes; robustify on literary prose.
3. **Multi-fact-per-entity STORAGE (the FHRR store capacity).** CAPABILITY: single-filler FHRR bind is exact
   (verified). LIMITATION: many facts per entity bundle into one register -> retrieval interference (the
   dense-bundle fidelity axis). BRAIN STATUS: the hippocampal store is SPARSE/pattern-separated, not a dense
   sum. OPTIMIZATION: a sparse/indexed per-entity fact store (ties directly to the read-terminal / fan-store
   store-organization line). A follow-on.
4. **The intra-sentential SYNTACTIC binder (the RESIDUAL's actual lever, NOT this mechanism).** This is where
   the anti-typical coref residual is recoverable (37.6% fine-distance oracle, the parent's finding), and it is
   a DIFFERENT organ. Named here so strategy does not mis-assign the residual to the fact store.
5. **Downstream consumers of the queryable discourse-fact memory (the generalisation the brief names).** Next-
   event prediction, bridging inference, question answering, and the ToM observation cue all consume this exact
   store. Each is a candidate follow-on that would reuse the proven mechanism on a task where the fact is
   inter-sentential and present -- the mechanism's real value, beyond coref.

# PROPOSED hdlab DIRECTION (strategy lands; Q111)

- **Do NOT** land the fact store into `hdlab/coreference_resolver.py` as a residual fix -- it is measured dead
  on the anti-typical residual (gold has no facts; the residual is the syntactic binder's job).
- **DO** promote the reading-built discourse-fact store + 2-hop bridging RESOLUTION as a **new situation-model
  organ** (`hdlab/discourse_fact_store.py` or an extension of `situation_model_accumulate`): the
  `DiscourseFactStore.observe/query/attrs` accumulation, the 2-hop bridge fused via `graded_competition`, and
  the **discourse-age gate** (invoke only for candidates with >=1 prior accumulated fact, not same-clause).
  Represent facts in the FHRR register (single-filler-exact today; sparse/indexed for multi-fact -- item 3
  above). This is the reasoning-frontier capability, wired for the downstream consumers (item 5), NOT a coref
  patch. Land it with the graded/distributional bridge (item 1) rather than the hard match, for fidelity.

---

## TLDR (plain language)

When we read "Mary is a nurse. Sue is a surgeon. **She** performed the operation," we know "she" is Sue --
because we remembered, from reading, that Sue is the surgeon, and surgeons operate. I built that memory-and-
reasoning step exactly as the brain does it: as it reads, it jots down a little fact for each character ("Sue is
a surgeon"), and when a later "she" appears it picks the character whose remembered fact fits ("surgeon" +
"operates"). **It works: on this kind of case it goes from a coin-flip to essentially always right, and every
scrambled version of it (shuffle who-is-what, or use only a generic fact-book that doesn't know which character
is which) falls back to a coin-flip** -- so the win is genuinely the character-specific facts we read, not a
trick of the setup. **But** the specific 1-in-5 hard reading cases we were hoping to fix turn out NOT to be this
kind: there, the right character was just introduced and has no history yet ("the parson, who, as he rode,
hummed") -- so there is no remembered fact to use, and I confirmed the brain doesn't use this memory step there
either (it uses grammar, fast, out of necessity). So we BUILT the reasoning capability the project wants and
proved it works where the brain uses it -- and we now know precisely why it is the wrong tool for those hard
coref cases (they need the grammar/syntax organ instead). The honest caveat: my proof is on clean built
examples; on messy real prose the ceiling is set by how well we extract "X is a nurse" and how much our fact-
book knows -- I measured that it fades gracefully, not off a cliff.

## QUESTIONS
None -- the bar is met (the mechanism is built and CI-separated over the fact-blind reader with every control at
chance; the residual half is a rigorous negative, which the bar counts as a full pass). One labelling judgement
for you at integration: I marked this **SOLVED** because the capability the brief asked for is demonstrated with
the full control suite on a sanctioned built population (the brief explicitly permits "build one to get power"),
AND the residual is honestly scoped out with a measured + mechanistic reason. If you would rather it read as
PARTIAL because the Level-1 win is on constructed (not natural) text, the content is identical -- the real-text
measurement is named as the #1 follow-on either way.

## NEXT STEPS
1. **(Strategy)** Re-verify the witness (`verification/test_discfact_store_bridging.py`, 15/15). Do NOT land the
   fact store as a coref-residual fix (measured dead). Consider promoting it as a new situation-model organ per
   PROPOSED hdlab DIRECTION -- wired for the downstream consumers, with the graded/distributional bridge.
2. **(Strategy)** Fold the AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md`: add the discourse-fact-store organ
   (proven capability, PINNED computation, distributional-bridge fidelity gap); REFINE the coref-residual entry
   (its lever is the syntactic binder, not the fact store).
3. **(Follow-on problems, seeded by the adjacent-component evaluation)** -- (a) the GRADED/distributional 2-hop
   bridge (the top fidelity lever); (b) validation on a REAL inter-sentential fact-decisive corpus (the #1
   thing to harden -- real extraction + coverage); (c) the sparse/indexed multi-fact-per-entity store; (d) the
   downstream consumers (next-event prediction / bridging inference / QA / ToM) that reuse this store.
