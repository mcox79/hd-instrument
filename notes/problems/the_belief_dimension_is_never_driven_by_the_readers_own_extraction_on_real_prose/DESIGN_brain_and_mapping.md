# DESIGN — brain mechanism, the refute-and-rebuild, and the honest mapping

**Slug:** `the_belief_dimension_is_never_driven_by_the_readers_own_extraction_on_real_prose`
**Solver:** opus 4.8. **Opened:** 2026-08-31. Writes only `experiments/`, `verification/`, this folder.

## 1. The opening brain question (before any method)
*"Which brain structure does belief tracking, and are we replicating it or substituting something convenient?"*
The mentalizing network (right TPJ, dmPFC) holds a **content-general propositional attitude** — *holder → attitude →
arbitrary proposition* — not an object-location register (Saxe & Kanwisher 2003; **Koster-Hale, Richardson, Velez,
Asaba, Young & Saxe 2017, NeuroImage** — MVPA: belief coded along *abstract* content-general dimensions, NOT the
identity/location of the believed object; Jamali et al. 2021 Nature — dmPFC belief neurons generic). The brain also
**source-tags** how a belief was acquired — *seen vs. heard* is decodable in rTPJ (Koster-Hale, Bedny & Saxe 2014).

## 2. What the brief assumed, and why the disk refutes it
The brief proposes to drive `belief_timeline` from the reader's **object-location-MOVE** extraction (Sally-Anne:
"marble moved basket→box unobserved"). Two independent lines refute this as the event source **for real prose**:
- **DISK (viability probe, `_belief_probe_scratch`):** the reader's own in-substrate parse extracts ~1 object-move
  per LitBank book, **ZERO objects with ≥2 moves** across 12 books, and most hits are idioms ("threw glances→direction",
  "pushing his fortune→line"). The classic object-transfer false-belief scene is **essentially absent from literary
  prose** — it is a developmental *diagnostic*, not how narrative conveys belief.
- **BRAIN (research drill 2026-08-31, `hdi_research`):** the Sally-Anne object-transfer is a lab stress-test of the
  false-belief *concept*, not a model of natural belief sourcing. In running narrative, belief attribution is fed by
  **language about minds**, in descending frequency: (a) **explicit narrator-epistemic / free indirect discourse**
  ("unbeknownst to her", "she believed him dead") — dominant in literary fiction (Zwaan event-indexing:
  protagonist+intentionality dimensions; Zunshine 2006; Graesser constructionist inferences); (b) **reported speech /
  testimony** (Harris & Koenig 2006 — most adult belief rests on testimony; Sodian & Wimmer 1987 — a *dissociable*
  source); (c) **inferred perceptual access** (present but rare — matches the probe). Verbal/narrated belief engages the
  **same** ToM network (Dodell-Feder, Koster-Hale, Bedny & Saxe 2011 verbal false-belief localizer; Jacoby/Paunov/
  Shain/Fedorenko/Saxe 2022 — ToM network tracks mental-state content regardless of modality; language net ≠ ToM net,
  Shain 2022 — so reading belief off the narrator's words is *genuine mentalizing*, not a parsing shortcut).

**Channel-density measurement (`_belief_channel_probe_scratch`, 30 LitBank books / 2652 sents):** narrator-epistemic +
testimony belief-update signals outnumber (already-noisy) object-moves **4.2×** (165 vs 39); the object-moves are mostly
false positives, so the genuine ratio is far higher. The literature sets the *ontology* of sources; the corpus sets the
*distribution* — and the distribution says the object-move source is the wrong one.

⇒ **Pivot (a FIDELITY UPGRADE, not a convenience):** drive `belief_timeline` from the reader's OWN extraction of
belief-update events across the **three registration channels** — RULE0 narrator-epistemic (dominant), RULE2 testimony,
RULE1 perception (the object-move is its degenerate special case) — with **reality tracked separately**. The organs are
already the right shape: `belief_timeline` is content-general (`obj` is any fact key, `value` any symbol), and
`perceptual_access_ledger` already implements all three rules (RULE0 `_epistemic_statement`, RULE1 field, RULE2
`_informed_after`). What was missing — and what this problem builds — is the **event source composed from `read()`**.

## 3. PINNED vs OUR-INVENTION (inherit the audit §2b verdicts)
- **PINNED (replicate the operation):** belief kept SEPARATE from reality (TPJ/mPFC; Saxe 2003); updates ONLY on a
  registered event — seeing/being-told→knowing (Wimmer & Perner 1983; Harris & Koenig 2006); **content-general** attitude
  over arbitrary propositions (Koster-Hale 2017); **source-tagged** (Koster-Hale 2014); PIECEWISE-CONSTANT sample-and-hold
  persistence between updates = Dowty 1986 stative inertia, which generalizes over *any* proposition (this is the license
  for the same mechanism across fact types — location, status, identity). Event ORDER = temporal-order register
  (Reichenbach). Sticky REGISTRATION ledger, not a boolean re-evaluated at query time (Butterfill & Apperly 2013).
- **OUR-INVENTION-UNDER-TEST (sweep, do NOT adopt as truth):** the belief-update-cue EXTRACTION from real prose (which
  epistemic/testimony/perception constructions off the reader's own parse+coref, no gold), the small-value read-out
  vocabulary, the mapping of extracted events into the organ's `WorldEvent`/`observed` structures. Glass-box, no LLM at
  inference.

## 4. Generalization (the user's explicit ask — "does this need to generalize, and how does the brain do it?")
The brain uses **one content-general mechanism** across fact types (Koster-Hale 2017: no separate "location-belief" vs
"trait-belief" area); persistence is licensed for arbitrary propositions by stative inertia (Dowty). So the build is
content-general by design: a *fact* is `(entity, fact_type ∈ {location, status})` with a small text-derived value set,
and the SAME `belief_timeline` sample-and-hold handles both. The gold spans BOTH fact types to demonstrate the single
mechanism generalizes — not a location-only special case.

## 5. The honest coverage bound (stated up front, not discovered late)
The belief-VALUE-at-T task needs a fact with a small ADJUDICABLE value set. Real literary belief is mostly OPEN-ended
(identity, character, intention) and resists exact-match scoring; the small-valued false-belief scene (location/status
with a witnessed-vs-missed change) is **rare** in literary prose (prior `exp_belief_timeline_real_prose_v1`: staleness
ingredients common at 17%, but complete gold-labelable over-time scenes not automatically minable). So the REAL-prose
headline is expected coverage-bounded; a MODERN constructed slice (the verbal-ToM-localizer style — Dodell-Feder 2011)
serves as the **positive control** that isolates any wall to real-prose extraction/coverage, NOT to the mechanism, and
as the corpus-age control (SPACE template). Per the brief, a rigorous, enumerated NEGATIVE that localizes the ceiling is
a full PASS — provided the mechanism it built is the brain's actual mechanism, faithfully composed.

## 6. Pre-registered bars (set BEFORE the full run)
On REAL narrative through the reader's OWN extraction (3-channel belief-update source + observation gate + order):
- **PASS** = belief-at-T value accuracy CI-separated over BOTH (a) the REALITY floor (report the true/current value —
  the beliefless reader) and (b) a timeline-AGNOSTIC last-mentioned-value floor; the info-free TWIN (shuffle the
  update order / observation bits) LOSES CI-separated; a FALSE-BELIEF discriminator (on the belief≠reality subset the
  tracker beats the reality floor by MORE) + a persistence/distance signature (belief held across intervening
  unobserved events). Report belief-update-cue extraction recall/precision + CI half-width + null p95 beside every
  margin.
- **Rigorous NEGATIVE = PASS** if real extraction is too weak: enumerate which belief constructions (which
  epistemic/testimony/perception forms, which fact types) the reader recovers vs misses, localizing the ceiling
  (per SPACE, the parser-recall / open-vocabulary read-out) — with the mechanism confirmed on the positive control.
