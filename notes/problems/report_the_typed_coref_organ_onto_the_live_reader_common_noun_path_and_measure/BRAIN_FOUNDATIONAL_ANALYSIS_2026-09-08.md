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
| **type comparator -- TAXONOMIC route** | ATL hub (lexical) | C5 = WordNet is-a/synonym/part-whole | YES operation; knowledge OK for taxonomy |
| **type comparator -- ENCYCLOPEDIC route** | ATL hub (encyclopedic, instance-of) | C8 DBpedia spoke EXISTS but NOT wired into typed_coref + asset unshipped here | **NO -- half-wired / absent (the main gap)** |
| **type comparator -- SCHEMA/SCENARIO route** | ATL hub + situation model (scripts) | NONE (associative anaphora unbuilt) | **NO -- missing mechanism** |
| deployed resolution binding | -- | commonnoun_binder (LitBank cluster-F1: person-gate + modifier-split + event-centrality) | **NO -- OUR-INVENTION for a different task; the deployed-path deficit** |
| mention/parse (GUM) | -- | gold | controlled here (not the bottleneck) |

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

## 4. What to prototype / optimize (ordered by oracle-measured leverage)
1. **Wire the brain-foundational binding (typed_coref) as the reader's resolution consumer** -- THIS problem's deliverable,
   proven on the live schema (+0.0252 CI-sep). Drop-in ref: `experiments/exp_commonnoun_binder_live_report_v1.typed_coref_liveschema_resolve`.
2. **Wire the ENCYCLOPEDIC route (C8 DBpedia entity-type spoke) into the bridge** -- the single biggest lever (+0.18
   oracle headroom; sibling measured +0.0955 CI-sep two-route on the name-bridge slice). The organ EXISTS
   (`hdlab.typed_spokes.type_licenses`); rebuild/ship its asset to `data/frontend_assets/` (empty here) and union it with
   the WordNet route (CLS two-route design). Static offline, invariant-safe.
3. **Build a SCHEMA/SCENARIO route for associative (bridging) anaphora** (Sanford-Garrod scenario mapping) -- restaurant
   -> the waiter. A static frame/script association store (FrameNet / ConceptNet AtLocation/UsedFor slices, offline).
   A distinct brain mechanism (script knowledge, not taxonomy) inside the oracle headroom.
4. **Add a scored common-noun RESOLUTION instrument-arm** so these gains are board-visible (the reader has none today).
5. (fidelity follow-on) de-restrict the binder person-gate for its CLUSTERING consumer too (+0.0235 CI-sep even inside it).

## 5. Bottom line
We fully understand the results. The organ's mechanism IS brain-foundational; the two things holding us below the brain
are (a) the deployed path uses the wrong (LitBank-clustering) BINDING -- fixed here, proven CI-sep -- and (b) the type
comparator has only the taxonomic route wired, missing the encyclopedic (built, unshipped) and schema (unbuilt) routes,
which the oracle shows is ~88% of the remaining headroom. Both fixes are static offline, brain-foundational, invariant-safe
(no inference LLM). The path to the brain's level is clear and measured, not mysterious.
