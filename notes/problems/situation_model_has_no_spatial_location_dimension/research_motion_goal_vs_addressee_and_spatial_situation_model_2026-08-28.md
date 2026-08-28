---
filed_by: research
date: 2026-08-28
problem: situation_model_has_no_spatial_location_dimension
trigger: solver wall — "to X" PP disambiguation (spatial Goal vs Addressee/Recipient) + confirmation of the
  spatial-situation-model architecture (categorical vs metric, persistence, effortfulness)
---

# Research: Goal-vs-Recipient PP disambiguation + spatial situation-model architecture

Four parallel Sonnet lit-scans dispatched: (A) verb-class/thematic-role computational-linguistics account,
(B) neural basis of thematic-role assignment + Goal-over-Source asymmetry + deixis, (C) event-indexing model /
spatial situation models (Zwaan, Speer & Zacks, Radvansky), (D) place/grid-cell cognitive-map neuroscience +
location persistence + coreference binding. Full per-agent citation lists are folded into the sections below.
Per the lit-scan calibration discipline, all P estimates below are already deflated 0.15–0.25 from raw
confidence, and any claim that combines >1 source literature into a novel implementation prescription is capped
at P=0.50.

## HEADLINE

Your verb-class gate is the right **primary** mechanism and matches the standard computational-linguistics
account (VerbNet already encodes exactly this split as two distinct thematic roles — **Destination**
[+ concrete physical location] vs **Recipient** [+ animate] — keyed to verb class). But it is **not sufficient
alone**: a well-documented subclass of caused-motion verbs (*throw, send, pass, hand, kick, mail...*) is
**genuinely ambiguous** between Goal and Recipient for the identical "to"-PP, and verb class carries **zero**
disambiguating signal for that subclass (Rappaport Hovav & Levin 2008; Xia 2014). The brain/reader does not
close this gap with animacy typing alone — Xia (2014) shows event **construal** (often discourse-driven, not
just noun type) governs the reading even for animacy-matched cases. The strongest available free signal for a
system that already tracks entities is **prior discourse status**: if the "to X" head noun already resolves
(via your coreference/entity system) to a previously-established CHARACTER entity, prefer Recipient; if it
resolves to a previously-established LOCATION/SCENE entity, prefer Goal. This is not a new invention — it falls
directly out of the Event-Indexing Model's protagonist dimension (Zwaan & Radvansky 1998) and discourse-model
reference-resolution accounts (Garrod & Sanford) — but it is a correction to a WordNet-hypernym-only account:
animacy typing is a fallback prior for **first mentions**, not the primary mechanism.

On Q2, the architecture you propose (categorical/topological scene membership, presence as an interval,
persistence recoverable at a distance) is strongly and convergently supported — but with one important
correction to bring in from the original 1995 event-indexing data: **spatial discontinuity is empirically the
weakest and most easily eliminated of the five indexing dimensions** (Zwaan, Langston & Graesser 1995) — it
only reliably drove reading-time cost when readers had **explicit prior spatial knowledge** (a memorized floor
plan). This directly supports building the SPACE register as **on-demand/lazy** (populate and query per-entity
presence intervals when something needs "where is X", rather than eagerly maintaining full metric detail for
every entity at every event) rather than as an eagerly-maintained dimension of equal cost to TIME.

P_deflated: Q1 mechanism (verb-class primary + prior-discourse-status tie-break for the ambiguous caused-motion
subclass) = **0.50 (capped, novel synthesis)**. Q2 architecture (categorical/interval/effortful-lazy) = **0.50
(capped)** — component-level: categorical-not-metric representation alone is very well supported directly
(P≈0.65 after deflation, Rinck, Hähnel, Bower & Glowalla 1997 Exp 1–2 explicitly rule out Euclidean distance);
"spatial is optional/effortful" is well supported but not tied to one clean canonical paper (P≈0.45).

## Cheap decisive test

Build a small hand-coded gold set from real literary prose (LitBank sentences already on disk are fine,
n≈150–200 "to X" tokens), stratified into three verb-class buckets using VerbNet class membership:
1. **Pure self-motion** (VerbNet run-51.3.2, escape-51.1; WordNet troponyms of travel/move/go) — expect near-
   unanimous Goal/Destination gold labels.
2. **Pure communication/pure-transfer** (VerbNet say-37.7, give-13.1 non-caused-motion sense, point-behavior) —
   expect near-unanimous Recipient/Addressee gold labels.
3. **Ambiguous caused-motion** (VerbNet throw-17.1, send-11.1, and neighbors: throw/send/pass/hand/kick/mail) —
   expect a genuinely mixed distribution per Rappaport Hovav & Levin (2008).

Score three gates on bucket 3 only (buckets 1–2 are the sanity check that the gate is not broken on the easy
cases): **Gate A** = verb-class only (VerbNet Destination-vs-Recipient role lookup). **Gate B** = Gate A +
WordNet person-hypernym-vs-location-hypernym tie-break on the "to X" head noun. **Gate C** = Gate A + prior-
discourse-status tie-break (does the head noun corefer to an already-tracked CHARACTER entity vs an already-
tracked LOCATION entity in your existing entity registry?). Compare accuracy/F1 with CIs on bucket 3.

## Falsifiable predictions

**HARD-PASS**
1. Buckets 1 and 2 (pure motion / pure communication) score **>95%** gate-A accuracy against gold, n≥100 each —
   confirms verb-class gate is correct for the unambiguous classes (this is the low-risk part of your design;
   if it fails, something more basic than this research is broken).
2. Bucket 3 (ambiguous caused-motion) gold labels are **genuinely mixed** (not >90% one way) — confirms the
   ambiguity is real in your corpus, not a theoretical worry.
3. On bucket 3, **Gate C beats Gate A by a CI-separated margin** (discourse-status tie-break recovers signal
   verb class alone cannot provide) — this is the mechanism claim under test.
4. Talmy path-satellite gate: held-out/rare-verb + directional-particle combinations ("out", "back",
   "upstairs", "away") pattern with known motion verbs at **>90%** Goal/departure accuracy, confirming the
   particle carries Path independent of verb familiarity (matches the existing PROBLEM.md PINNED finding that a
   manner-verb whitelist is the wrong implementation).

**HARD-FAIL / refute**
1. If buckets 1–2 score **<85%** on gate A — the "easy" verb-class cases are not actually easy in real prose,
   meaning discourse/context regularly overrides verb-class semantics even for unambiguous verbs; this is a
   bigger problem than the one being asked about and should be reported before touching bucket 3.
2. If **Gate B's** CI on bucket 3 overlaps the 50%-chance line, or does not separate from Gate A — confirms Xia
   (2014)'s finding that WordNet animacy/noun-type typing alone is insufficient for the ambiguous subclass; do
   NOT ship a person/location-hypernym-only tie-break as the fix.
3. If **Gate C** also fails to separate from Gate A CI-wise on bucket 3 (i.e., prior discourse status doesn't
   help either) — this would mean the disambiguation genuinely requires event construal / world knowledge not
   recoverable from entity-tracking state alone, and the correct scope decision is to accept residual ambiguity
   (emit both readings with a confidence split, or defer to a downstream consumer) rather than search for a
   fourth gate.
4. If spatial-discontinuity tracking shows **no measurable representational payoff** anywhere downstream (i.e.
   the register is queried but never changes an answer vs. a stateless last-mention baseline) — consistent with
   Zwaan, Langston & Graesser (1995)'s finding that spatial effects are the weakest of the five dimensions —
   this doesn't kill the mechanism but should reprioritize it as a secondary/lazy-only index, not a primary one.

## Cross-thread synthesis

- Confirms and sharpens `notes/BRAIN_FOUNDATIONAL_AUDIT.md` / PROBLEM.md's existing PINNED claims (event-
  indexing SPACE dimension, Talmy path-satellite + deixis-dominates update rule, place/grid-cell allocentric
  map, Speer & Zacks 2009 parahippocampal signature) — these all replicated independently across today's scans
  and should stay PINNED as-is.
- **New finding not in the current PROBLEM.md brief:** the Goal-vs-Recipient "to"-PP ambiguity has its own
  dedicated computational-linguistics literature (VerbNet's Destination/Recipient role split; PropBank's
  ARG2-GOL inconsistency across framesets; Hwang et al. 2017's explicit two-layer construal annotation scheme
  for exactly this "to" ambiguity — SNACS supersenses RECIPIENT vs GOAL, Schneider et al. arXiv:1704.02134).
  This is a solved-in-annotation-theory but NOT solved-in-parsing problem — the field's answer is "annotate
  both layers and let context/construal pick," which is consistent with the recommendation below to fall back
  to entity-tracking state rather than trying to force a single lexical rule.
- **Citation check on existing PROBLEM.md text:** the brief cites "Papafragou 2008" for deixis-dominates-Path.
  Today's scans independently verified **Papafragou (2010)**, *Cognitive Science* 34(6) — "Source-goal
  asymmetries in motion representation" — as a real, verifiable paper in this space, but did not independently
  verify a 2008 Papafragou paper specifically on deixis. Recommend the solver spot-check this citation year
  before it propagates further (AUDIT UPDATE candidate for `BRAIN_FOUNDATIONAL_AUDIT.md` — flagged, not fixed,
  since this note does not own that file).
- Connects to `experiments/perceptual_access_ledger.py`'s existing PATH-satellite + deixis logic (already
  PRIOR WORK per the PROBLEM.md) — nothing here contradicts it; the new content is specifically about the
  "to"-PP Goal-vs-Recipient split, which is a different ambiguity from the departure/arrival PATH-satellite
  reading already implemented there.
- `hdlab/goal_typing.py` already contains an `_request_object_is_addressee` mechanism (lines ~1155–1250) for a
  *different* addressee ambiguity (embedded-request objects). That is prior art for "addressee-typing exists
  elsewhere in this codebase" but is not directly reusable for the "to X" PP case — flagging for the solver's
  awareness, not claiming equivalence.

## Substrate-product implications

1. **Adopt VerbNet's own Destination-vs-Recipient role labels** as the canonical typing rather than building a
   parallel ad hoc verb whitelist — this is a straight resource-reuse win (foundation-is-free-to-build): VerbNet
   classes already carry the +animate vs +concrete-location selectional restriction per role.
2. **For the ambiguous caused-motion subclass, do not trust a WordNet person/location-hypernym tie-break as the
   primary fix.** Use the entity-tracking system you already have: if the "to X" head resolves via coreference
   to an existing CHARACTER entity, type Recipient; if it resolves to an existing LOCATION/SCENE entity, type
   Goal. This reuses the coreference resolver already flagged in PROBLEM.md (~0.65 on real narrative — degrade
   gracefully) instead of adding a new, weaker WordNet-only heuristic. Reserve WordNet person/location hypernym
   typing as the **fallback for first-mention** "to X" nouns not yet in the entity registry.
3. **Keep the Talmy path-satellite gate as-is** — it is independently well supported (satellite-framed encoding
   is orthogonal to verb identity) and matches the existing "florped out" design requirement.
4. **Model SPACE as lazily-constructed, not eagerly mandatory**, unlike (implicitly) TIME. The original 1995
   event-indexing data show spatial-discontinuity reading-time costs were unreliable except when readers had an
   explicit spatial model already active. Recommend the register populate/verify presence intervals on-demand
   (when a downstream consumer asks "where is X" or a motion event fires) rather than forcing full metric/scene
   bookkeeping eagerly for every entity at every event — this is a cost-control decision, not a fidelity
   compromise, since it mirrors the reader's own effortful/goal-dependent construction.
5. **Represent location categorically (scene/room-ID, itself an entity, allowing containment nesting: room in
   house in city) with an open/close interval — not coordinates.** Rinck, Hähnel, Bower & Glowalla (1997) Exp
   1–2 directly rule out Euclidean/metric effects in favor of a categorical room-count gradient; Radvansky's
   event-horizon model (2012) and the doorway effect (Radvansky & Copeland 2006; Radvansky, Krawietz & Tamplin
   2011 — note: third author is **Tamplin**, not Altman, correcting the framing in the original ask) both
   assume/require a discrete scene-boundary-crossing event, not continuous coordinates. This directly confirms
   the PROBLEM.md's presence-interval design.
6. **Persistence/query-at-distance is well supported as "maintained state, not re-scanned."** Rinck & Bower
   (1995) / Rinck et al. (1997)'s reading-time-by-room-distance paradigm is itself the direct empirical
   demonstration that a stated location persists and is retrievable at a distance without restatement — this
   matches the PROBLEM.md's own measured finding (0.99 at K=0..20 filler sentences, collapsing only under an
   artificially narrow 3-sentence window). O'Brien & Myers's resonance model gives a plausible retrieval-at-a-
   distance mechanism (passive reactivation of backgrounded discourse content) if a neuro-plausible retrieval
   story is wanted later.
7. **Low-priority / do-not-build-now:** grid-cell-style hexagonal coding of abstract/conceptual narrative
   spaces (Constantinescu, O'Reilly & Behrens 2016; Behrens et al. 2018) is a genuinely interesting generalization
   of the cognitive-map machinery beyond physical space, and Cohn-Sheehy et al. (2021, *Current Biology*) shows
   the hippocampus does bridge temporally-distant narrative events the same way it bridges spatial ones — but
   this is a speculative future direction (e.g., for a "social distance" or "scene-similarity" space), not
   something the current per-entity location register needs. P(near-term product relevance) capped at 0.35.

## Citations (verified count)

Across the four parallel scans: **~46 unique citations gathered**, deduplicated (several — Zwaan & Radvansky
1998; Rinck, Hähnel, Bower & Glowalla 1997; Morrow, Greenspan & Bower 1987 — were independently surfaced by
2+ scans, which is itself convergent confirmation). Breakdown:
- **High-confidence, independently verified (title/author/venue/year checked via search):** ~36.
- **Moderate-confidence (core finding verified, but exact author list, volume, or venue not fully pinned):** ~8
  — flagged inline above/in agent transcripts: Grewe et al. 2007 author order; Matchin & Hickok venue; Rinck &
  Hähnel 2003 *Psychological Research* author list; Radvansky, Zwaan, Federico & Franklin 1998 exact cite;
  Garrod & Sanford exact year/venue.
- **Explicit literature gaps found (no citation invented, flagged as absent-from-this-search rather than
  confirmed-absent):** direct ERP/fMRI study isolating online Goal-vs-Recipient thematic assignment timing;
  a dedicated psycholinguistic processing study on deixis (come/go) interacting with the addressee-vs-goal
  ambiguity; a single canonical citation for the "spatial situation models are effortful/optional" claim (it is
  a converging pattern across Zwaan-group papers, not one paper); a prosody study specific to Goal-vs-Recipient
  "to"-PP disambiguation.
- **One unreviewed preprint cited with that caveat stated:** Aliko, Wittenberg, Skipper & Small (2025, bioRxiv)
  on situation models resolving word reference — directly on-point for the coreference-binds-location question
  but not yet peer-reviewed.
- Two corrections to premises supplied in the original research questions, both verified: Peer et al. (2021)'s
  fourth author is **Epstein**, not Moscovitch; Nielson et al. (2015) is in ***PNAS***, not *Nature
  Communications*.

Load-bearing citations for this problem (repeat for solver convenience): Levin (1993); VerbNet (Schuler et al.,
Destination/Recipient roles); FrameNet (Ruppenhofer et al., *FrameNet II*); Rappaport Hovav & Levin (2008,
*J. Linguistics* 44(1)); Xia (2014, *J. Lang. Teaching & Research* 5(1)); Hwang et al. (2017, *SEM 2017*);
Talmy (1985; 2000); Lakusta & Landau (2005, *Cognition* 96; 2012, *Cognitive Sci.* 36(3)); Papafragou (2010,
*Cognitive Sci.* 34(6)); Zwaan, Langston & Graesser (1995, *Psychological Science* 6(5)); Zwaan & Radvansky
(1998, *Psychological Bulletin* 123(2)); Rinck, Hähnel, Bower & Glowalla (1997, *JEP:LMC* 23(3)); Rinck & Bower
(1995, *J. Memory & Language* 34; 2000, *Memory & Cognition* 28(8)); Morrow, Greenspan & Bower (1987, *J.
Memory & Language* 26(2)); Speer, Zacks & Reynolds (2007, *Psychological Science* 18(5)); Speer, Reynolds,
Swallow & Zacks (2009, *Psychological Science* 20(8)); Zacks & Swallow (2007, *Current Directions in
Psychological Science* 16(2)); Baldassano et al. (2017, *Neuron* 95(3)); Radvansky & Copeland (2006, *Memory &
Cognition* 34(5)); Radvansky, Krawietz & Tamplin (2011, *QJEP* 64(8)); Radvansky (2012, *Current Directions in
Psychological Science* 21(4)); O'Keefe & Dostrovsky (1971, *Brain Research* 34); O'Keefe & Nadel (1978, *The
Hippocampus as a Cognitive Map*); Hafting, Fyhn, Molden, Moser & Moser (2005, *Nature* 436); Behrens et al.
(2018, *Neuron* 100(2)); Constantinescu, O'Reilly & Behrens (2016, *Science* 352(6292)); Cohn-Sheehy et al.
(2021, *Current Biology* 31(22)); Kintsch & van Dijk (1978, *Psychological Review* 85(5)); Gernsbacher (1990,
*Language Comprehension as Structure Building*).
