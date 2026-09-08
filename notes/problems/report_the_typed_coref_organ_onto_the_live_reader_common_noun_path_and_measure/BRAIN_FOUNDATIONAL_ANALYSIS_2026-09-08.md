# Brain-foundational analysis: common-noun resolution -- do we understand WHY, and is the whole chain brain-foundational? (2026-09-08)

Owner's questions: do we fully understand these results? is this + upstream 100% brain-foundational? how EXACTLY does the
brain do this, and why aren't we showing those results? anything to prototype/optimize?

All numbers MEASURED on disk (GUM modern TEST, n=2855 anaphoric common-noun mentions; reverify
`verification/test_commonnoun_binder_live_report.py` 16/16). NO hdlab written (Q111).

## 1. How the brain re-recognises an entity from a plain noun ("the company" -> Google) -- the exact mechanism
PINNED components (well-established; each maps to a substrate organ):
1. **Discourse referents / file cards** (Kamp DRT; Heim File-Change Semantics). One mental file per entity; every mention
   UPDATES it. A definite NP RETRIEVES an existing file. -> our referent cards.
2. **Accessibility governs the RETRIEVAL CUE by referring-form** (Ariel 1990; Gundel-Hedberg-Zacharski givenness). A
   PRONOUN marks the most-ACTIVE entity -> resolved by SALIENCE. A full DEFINITE marks a LESS-active one and carries
   DESCRIPTIVE CONTENT -> resolved by CONTENT/TYPE match, not salience. (Confirmed in our data: the same-head ranking
   twin TIES -> ranking carries no signal for definites; the TYPE cue is the whole lever.)
3. **The type/category match comes from the ATL semantic hub** (Lambon-Ralph controlled semantic cognition): a
   graded, sense-resolved store of taxonomic (is-a, synonym, part-whole) AND encyclopedic (instance-of: Google is-a
   company) AND schematic (restaurant has-a waiter) relations, unified in one hub. -> our typed_spokes (C5 taxonomic
   from WordNet; C8 encyclopedic from DBpedia).
4. **Hold-under-uncertainty** (Nieuwland & Van Berkum Nref): ambiguous reference -> maintain candidates, do not commit.
   -> the NON-WRITING bridge.
5. **Content-addressed parallel cue-based retrieval** (Lewis & Vasishth 2005; McElree): retrieve by weighted features
   (type, gender, number, recency), not hard filter-then-rank. -> the bridge candidate generation.

So the brain's computation = **content-addressed retrieval of the type-compatible file, held under uncertainty, over
identity-carrying file cards, where the type match draws on a hub containing taxonomic + encyclopedic + schematic
knowledge.** Our `hdlab.typed_coref` organ implements 1,2,4,5 and the TAXONOMIC part of 3.

## 2. Fidelity ledger -- is every component (this + upstream) 100% brain-foundational?
| component | brain structure | our impl | brain-foundational? |
|---|---|---|---|
| referent file cards | DRT/File-Change | typed 3-view card | YES (operation); the 3-view is an OUR-INVENTION IMPLEMENTATION of identity-vs-pointer, defensible |
| form->cue (definite=content, pronoun=salience) | Ariel accessibility | content-addressed definite bridge; salience pronoun pick | YES (confirmed: ranking twin ties for definites) |
| hold-under-uncertainty | Nieuwland Nref | non-writing bridge | YES |
| cue-based retrieval | Lewis-Vasishth | parallel candidate generation | YES (operation); reduced cue set, but ranking is a measured wash |
| **type comparator -- TAXONOMIC route** | ATL hub (lexical) | C5 = WordNet is-a/synonym/part-whole | YES operation; BUT DEGRADED in this working copy: the ConceptNet PartOf/HasA/MadeOf assets are ABSENT (WordNet-only), so even the taxonomic route is under-powered here |
| **type comparator -- ENCYCLOPEDIC route** | ATL hub (encyclopedic, instance-of) | PROTOTYPED (WordNet instance-of + person-typing, +0.0102 CI-sep, twin loses); STRONG C8 DBpedia spoke EXISTS in `hdlab.typed_spokes` but asset unshipped + not wired into `typed_coref` | operation YES; **knowledge INCOMPLETE (strong asset absent) -- the main gap** |
| **type comparator -- SCHEMA/SCENARIO route** | ATL hub + situation model (scripts) | NONE (needs ConceptNet AtLocation/HasA; asset+API unavailable) | **NO -- missing (blocked on acquisition)** |
| deployed resolution binding | content/recency-addressed definite resolution | AS DEPLOYED = commonnoun_binder (LitBank cluster-F1: person-gate + modifier-split + event-centrality) -> NOT brain-foundational; AS PROPOSED (this problem's fix) = typed_coref binding -> brain-foundational, proven +0.0252 CI-sep, NOT YET WIRED | **NO as-deployed; YES as-proposed (wire pending, Q111)** |
| downstream consumer | -- | the reader scores NO common-noun resolution dim; downstream binding reads clusters (sm.entities), not per-mention resolution | **MISSING instrument-arm + resolution-stream consumer** |
| mention detection + parse (real text) | incremental predictive parse | GOLD on GUM (controlled); on real text = the substrate pos_tagger/arc_parser (BATCH, not incremental) + reader mention extraction -- separate organs, unverified HERE | controlled on GUM; real-text fidelity is separate/owned; the batch (non-incremental) parser is a known longer-horizon fidelity gap |

## 2b. FULL-CHAIN VERDICT: is it 100% brain-foundational? NO -- three named gaps, one fixed-pending-wire.
1. **The deployed BINDING is not brain-foundational** (LitBank cluster-F1 organ used for resolution). FIXED as-proposed
   (typed_coref, +0.0252 CI-sep, proven on the live schema) -- but NOT yet wired (Q111). This is the headline deliverable.
2. **The type comparator's KNOWLEDGE is incomplete** -- the dominant remaining gap. Operation is brain-foundational
   (ATL hub retrieval); knowledge has only the taxonomic route wired (and even that is DEGRADED here: ConceptNet
   part-whole assets absent -> WordNet-only). The encyclopedic route is prototyped (+0.0102 CI-sep) but its STRONG asset
   (DBpedia C8) is unshipped; the schema route is blocked on ConceptNet. THE KNOWLEDGE GAP (see below).
3. **No downstream resolution consumer / instrument** -- the win is board-invisible until a resolution dim + a consumer
   that reads per-mention resolution (not just clusters) exist.
Everything else (file cards, form->cue, hold-under-uncertainty, cue-based retrieval) IS brain-foundational and confirmed.

## 2c. EFFICIENCIES (measured / available)
- **Precompute the type-compatibility closure OFFLINE** as a static asset (the ~25k-pair closure over the head vocab
  warms once) -> the bridge becomes O(set-lookup), ZERO inference-time WordNet work. Already the substrate's design for
  the C8 compact npz (7x smaller than the 548MB sqlite). Invariant-safe (offline foundation asset).
- **The bridge fires ONLY on the different-head slice (~34%)** -- the 66% same-head path is untouched (cascade =
  weighted-parallel constraint satisfaction with head-match as the dominant cue, the efficient AND faithful form).
- **Comparator memoization** (symmetric-key `coref_type_license`, `_wn_instance_lemmas`, `_agent_verbs`) is already in
  place (~7x on the bridge). No further work needed.
- **Non-writing bridge = labels byte-identical** -> the resolution stream is an ADDITIVE read-only overlay; no
  recompute of clustering / sm.entities / pronoun coref (no-regress by construction, zero downstream cost).

## 2d. UPGRADE OPPORTUNITIES (brain-fidelity), ranked
- **[knowledge] Ship the DBpedia C8 encyclopedic asset (offline dump build) + wire it** -- the biggest KB lever
  (+0.0955 sibling-proven on the name slice; +0.18 oracle headroom). THE high-priority knowledge-gap follow-on.
- **[knowledge] Acquire a ConceptNet slice** -> adds the schema/associative route AND restores the DEGRADED taxonomic
  part-whole route (currently WordNet-only here). Reproducible open static asset (fetch when the API/dump is reachable).
- **[program] The generative world-model** for the genuine multi-description residual (situation-model inference) --
  a separate larger effort; do not expect a comparator to cover it.
- **[minor] Single graded file card** instead of the 3-view (content-weighted retrieval is closer to one graded store
  than 3 discrete views) -- a fidelity refinement, not a number-mover (the 3-view is measured-equivalent).
- **[minor/longer-horizon] Incremental predictive parser** (Friederici/Hale) upstream -- a known batch-vs-incremental
  fidelity gap, not the binding constraint for this task.

Two components are NOT brain-foundational: (i) the deployed resolution BINDING (uses the LitBank clustering binder --
THIS problem's headline; fix = the typed_coref binding), and (ii) the type comparator's KNOWLEDGE is incomplete (only
the taxonomic route wired; the encyclopedic + schema routes missing).

## 3. Why we aren't showing the brain's results -- QUANTIFIED (this is the answer)
Two distinct signal losses, measured:
- **Loss 1 -- wrong binding (the deployed path).** The LitBank clustering binder scores 0.4904 on resolution, BELOW the
  dumb string-identity floor 0.5412. Swapping to the brain-foundational typed_coref binding recovers this and beats the
  floor: 0.5664 on the live schema, +0.0252 CI-sep. (THIS problem's fix.)
- **Loss 2 -- incomplete type knowledge (the dominant loss).** Oracle test (perfect type comparator = license iff
  gold-coreferent, SAME bridge structure): resolution would reach **0.7492** -- **+0.1828 over our WordNet-seeded fix**
  CI[+0.1625,+0.2059], **+0.2081 over the floor** CI[+0.1847,+0.2344]. So the type comparator is the DOMINANT lever, and
  **~88% of the achievable headroom (0.183 / 0.208) is world knowledge WordNet lacks.** The comparator's OPERATION is
  brain-foundational (the oracle uses the identical content-addressed retrieval structure); only its KNOWLEDGE BASE is
  the gap. The missing knowledge is ENCYCLOPEDIC instance-of (Google->company, Argentina->country) + SCHEMA/SCENARIO
  associative anaphora (restaurant->the waiter).
- **The residual above 0.749 (~0.25 to ceiling)** = anaphors with NO antecedent-linkable prior (first-mention definites,
  bridging inference, split/plural antecedents) -- genuine situation-model INFERENCE, not antecedent-linking. A human
  gets some of these; they are a different (harder) mechanism, honestly out of the retrieval-organ's scope.

## 3b. Refined decomposition of the +0.18 headroom (measured) -- how much is KB-addressable vs inference?
The 2855 anaphoric common mentions split: 66.3% same-head (string-identity gets these); 31.6% (902) different-head WITH
a prior antecedent (the bridge's target). Of the 902:
- **243 (8.5%) have a NAME antecedent** -> the ENCYCLOPEDIC route (instance-of). WordNet instance-of reaches only 11.9%
  of these (noisy: Toyota->city, Amazon->river; missing: Google/FBI/Obama). This is the DBpedia C8 slice.
- **659 (23.1%) have a COMMON antecedent.** Inspecting the oracle-resolved pairs: MOST are NOT taxonomic -- they are
  discourse MULTI-DESCRIPTION (the president/the leader; data/information; site/website) or parse/annotation NOISE
  (task<-collect [verb], claim<-be [verb], study<-17 [number]). WordNet's coref_type_license licenses only 14.4%. A KB
  lookup does NOT solve the bulk of this; it is SITUATION-MODEL INFERENCE (does description X co-apply to entity Y?).
=> The oracle +0.18 is an UPPER bound that INCLUDES inference-only + noisy pairs. A KB-based type comparator (encyclopedic
+ schema) recovers the NAME slice + the genuinely-taxonomic/associative common subset; the majority of the common slice
is the reasoning/world-model program, not a comparator upgrade.

## 4. What to prototype / optimize (ordered by oracle-measured leverage) -- WITH PROTOTYPE RESULTS
STATUS KEY: [DONE] proven in this cell; [PROTOTYPED] lower-bound measured, strong version gated on an asset; [BLOCKED]
needs an offline asset unavailable this turn; [PROGRAM] a larger separate effort.
1. **[DONE] Wire the brain-foundational binding (typed_coref) as the reader's resolution consumer** -- THIS problem's
   deliverable, proven on the live schema (0.5664, +0.0252 CI-sep, twin loses, no-regress). Drop-in ref:
   `typed_coref_liveschema_resolve`.
2. **[PROTOTYPED] ENCYCLOPEDIC route (instance-of + person-typing).** Prototyped OFFLINE (`encyc=True` arm), TWO
   brain-foundational sub-routes from the ATL hub's typing of a named entity: (a) WordNet INSTANCE-OF (Argentina->country,
   Einstein->physicist) for lexicalized entities; (b) PERSON-typing -- a person-name antecedent (gold/gazetteer gender
   m/f, the same name/morphology cue the brain uses) types the entity PERSON and licenses person-category anaphors
   ('the monk'/'the composer'/'the author' <- a person name), catching the person-DOMINATED name-bridge slice WordNet
   misses (given names are not WordNet-lexicalized). Result: **0.5765, +0.0102 over the taxonomic-only fix
   CI[+0.0054,+0.0157] CI-sep, +0.0354 over the floor, twin LOSES +0.0326 CI-sep**. Non-writing -> labels byte-identical
   -> no-regress by construction. STRONG version = the built-but-unshipped C8 DBpedia entity-type spoke (`type_licenses`;
   sibling measured +0.0955 CI-sep on the name slice); PREREQUISITE: rebuild/ship its asset from the offline DBpedia dump
   (a naive LIVE Wikidata-API acquisition was tried and REFUTED: ~65% API-fail rate + noisy full-span name surfaces +
   ~15min/mostly-empty -> the disambiguated offline dump is required, not a live API). Highest single KB lever.
3. **[BLOCKED] SCHEMA/SCENARIO route (associative anaphora, restaurant->the waiter; Sanford-Garrod).** The WordNet part
   (meronymy) is ALREADY inside `coref_type_license`; the incremental value is ConceptNet AtLocation/HasA beyond WordNet
   meronymy. NOT prototyped this turn: the ConceptNet API is DOWN (persistent 502) and the full dump (~1GB) + the
   `data/bridge_relation_assets_v1/` + `conceptnet5_en_100k.jsonl` assets are ABSENT in this working copy. Acquisition (a
   reproducible fetch of an open static asset, owner-pre-authorized) is the prerequisite. Note: rebuilding ConceptNet
   would ALSO restore `coref_type_license`'s part-whole route (currently WordNet-only here).
4a. **[PROTOTYPED -> LOCATED NEGATIVE] The REASONING program (situation-model role-fit).** Prototyped the brain-
   foundational reasoning mechanism for the multi-description slice: an agentive nominalization ("the leader") resolves
   to the entity that filled the matching AGENT role in prior events ("X led ..."), via WordNet agentive derivation
   (leader->lead) + thematic roles from the parse -- inference over event structure, NOT taxonomy or salience (salience
   was already refuted for definites). RESULT: `reason=True` arm = +0.0014 over the fix, CI[0.0,+0.0032] NOT CI-sep --
   a WASH. Sizing: only ~6/2855 anaphors are role-resolvable (412 are agentive nominalizations, but most are same-head;
   of the 123 different-head, the antecedent explicitly filled the matching agent-role in prior context in only ~6).
   MEANING: for common-noun RE-RECOGNITION, entity re-description is KNOWLEDGE-bound (is-a / world facts about the
   entity), NOT local-event-role-bound -- so the local reasoning module is not the lever HERE. Combined all-routes
   (taxonomic + encyclopedic + role-fit) = +0.0074 CI-sep over the fix, but that is encyclopedic-dominated.
4b. **[PROGRAM] The genuine residual = the GENERATIVE WORLD-MODEL.** The multi-description cases that are neither
   type-recoverable nor local-role-recoverable ("the president"/"the leader" where neither is stated) need the full
   generative world-model + global world knowledge about the entity -- a separate, larger program (the substrate's main
   event), not a comparator or a local role-fit module. Do NOT expect the encyclopedic/schema KBs OR local role-fit to
   recover it; the oracle +0.18 over-counts it (it includes inference-only + parse-noise pairs).
5. **[wire] Add a scored common-noun RESOLUTION instrument-arm** so these gains are board-visible (the reader has none today).
6. **[fidelity follow-on] de-restrict the binder person-gate** for its CLUSTERING consumer too (+0.0235 CI-sep inside it).

## 5. Bottom line
We fully understand the results. The organ's mechanism IS brain-foundational; the two things holding us below the brain
are (a) the deployed path uses the wrong (LitBank-clustering) BINDING -- fixed here, proven CI-sep -- and (b) the type
comparator has only the taxonomic route wired, missing the encyclopedic (built, unshipped) and schema (unbuilt) routes,
which the oracle shows is ~88% of the remaining headroom. Both fixes are static offline, brain-foundational, invariant-safe
(no inference LLM). The path to the brain's level is clear and measured, not mysterious.
