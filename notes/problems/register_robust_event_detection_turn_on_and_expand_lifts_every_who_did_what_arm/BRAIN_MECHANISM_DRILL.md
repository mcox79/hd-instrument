# Brain mechanism drill — register-robust event/predicate detection for who-did-what

**The opening move (owner's standing bar): how does the BRAIN detect an event/predicate, and are we replicating
the OPERATION or substituting something convenient?** This drill pins the mechanism, marks PINNED vs
OUR-INVENTION, and itemizes exactly where our implementation differs — which is what drove the build.

## 1. What computes "there is an event here" in the brain (PINNED)

- **Predicate-hood is category-independent noisy-channel inference, not a per-lexeme tag.** Category and
  structure settle JOINTLY over continuous multi-cue integration (MacDonald 1994; Fromont/Steinhauer/Royle 2020
  killed the syntax-first ELAN → N400+P600 additive). The computational form is Gibson (2013): category =
  lexical LIKELIHOOD × structural PRIOR, learned jointly; it generalizes to novel/archaic forms (Jabberwocky
  structure-building, Fedorenko; 2-yr-olds slot invented verbs from frame alone, Yuan 2011). → **register-invariant.**
- **Event-hood is NOT tied to the verb category (neo-Davidsonian; Bach 1986 eventuality types).** A predication of
  ANY surface category introduces an eventuality node:
  - **Copular / predicative STATES** ("Sarah is a doctor", "the streets are muddiest") are *Kimian STATES*
    (Maienborn 2005) — property-of-a-holder, ontologically distinct from a dynamic event, bound (HOLDER, PROPERTY)
    not (AGENT, PATIENT). Property attribution routes through LATL (Bemis & Pylkkänen 2011).
  - **Light-verb constructions** ("have a look", "give a start", "make a decision") carry the event in the
    eventive NOMINAL; the light verb is semantically bleached (Jespersen; Grimshaw & Mester 1988; Wittenberg &
    Piñango 2011 — LATL composition cost localizes the event to the nominal).
  - **Deverbal NOMINAL events** ("the destruction of the city") — events hidden in nouns (Grimshaw 1990;
    Garbin 2012, event nouns route through LIFG like verbs).
- **The brain queries a UNIFIED event-participant representation.** Predicate-centred role binding sits in
  lmSTC/pMTG (Frankland & Greene 2015; Matchin & Hickok 2020). "Who did X", "who is X", and "what happened" are
  the SAME retrieval over ONE eventuality inventory — the reader does not keep dynamic events in one store and
  states in an unreachable other.

## 2. What we have already built (REUSE — checked substrate_map / reader_capabilities / hdlab first)

| brain requirement | our organ | status |
|---|---|---|
| noisy-channel open-class predicate recovery | `hdlab/predicate_detector.py` (P6, owner-DONE) | BUILT, wired behind default-OFF `predicate_recall` |
| calibrated category posterior (axis-1) | `hdlab/crf_tagger.py` (P7) | BUILT (not the detector's cue yet) |
| copular STATE (HOLDER, PROPERTY) | `hdlab/copular_binding.py` + `bind_entity_states` (P3) | BUILT, **default-ON**, populates `sm.entity_states` |
| dynamic event detection | `situation_reader._tense_agnostic_extract` | BUILT, default-ON (UPOS==VERB) |
| patient drop-fill | `predict_revise` (default-ON) | complementary (recovers a dropped PATIENT, not a dropped verb) |

## 3. Where we EXACTLY differ (the itemized mechanism-diff — this drove the build)

| # | brain (PINNED) | ours (measured) | consequence (measured) |
|---|---|---|---|
| **i** | ONE unified eventuality inventory; state & event queried alike | **SILOED**: dynamic events → `sm.events` (who-did-what readout reads ONLY this); copular states → `sm.entity_states` (state-dim readout only) | copula-gov who-did-what Qs (~22% of BOTH arms) score ~0.03–0.31 **even though the state IS detected** — the readout can't cross the silo |
| **ii** | predicate-hood = register-invariant noisy-channel category inference | `predicate_detector` is exactly this — but its gate EXCLUDES non-AUX only (AUX-gated) | OPEN-class drops recovered; the copula/aux class is structurally out of its reach |
| **iii** | light-verb event carried by the eventive nominal | no light-verb / possessive predication detector | 'have'/'do' gov Qs largely unanswerable |
| **iv** | category continuously RE-ESTIMATED from context (predictive coding; Kuperberg 2016) | frozen post-hoc patch (P6 v1); the CRF calibrated posterior (P7) is the axis-1 fix, **+0.224 on 19c, un-landed** | 19c open-class recovery capped ~0.56 vs a competent reader's ~1.0 (a fidelity gap, not a ceiling) |

## 4. The build this drives (and what is a located NEGATIVE)

- **(A) Turn ON the open-class noisy-channel recovery (`predicate_recall`) — diff (ii).** It is the brain's
  register-invariant predicate inference already built; the only question is the cross-arm net effect + FP cost.
- **(B) UNIFY the who-did-what readout across the eventuality silo — diff (i), the highest-leverage lever.** The
  faithful fix is NOT to fire states into the dynamic event stream (sort-collapse — the copular solver rightly
  barred that, Maienborn). It is a **sort-aware unified READOUT**: a copula-gov who-did-what query reads the
  HOLDER (agent-slot) / PROPERTY (patient-slot) from the already-detected `sm.entity_states`. This is the brain's
  single-inventory query, restored.
- **Light-verb 'have'/'do' (diff iii)** and **the 19c open-class fidelity gap (diff iv)** are the deeper builds;
  measured here, and where the mechanism is genuinely context-bound (VP-ellipsis for 'do', the CRF/joint-decode
  for iv) they are named as located sub-negatives pointing at the owned successor problems, not faked.
