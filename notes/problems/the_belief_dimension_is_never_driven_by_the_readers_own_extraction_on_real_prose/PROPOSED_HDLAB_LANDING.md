---
kind: proposed_hdlab_landing
for_problem: the_belief_dimension_is_never_driven_by_the_readers_own_extraction_on_real_prose
applies_to: hdlab/  (STRATEGY SESSION ONLY -- Q111; solver did NOT apply this)
default: OFF (byte-identical when off)
---

# PROPOSED hdlab LANDING — `track_belief` (default-off) on SituationReader

The solver is barred from writing `hdlab/` (Q111, state-integrity). This is the exact change the strategy
session applies to WIRE the belief dimension. Everything it references is already built + tested in
`experiments/` (witness `verification/test_belief_at_t_end_to_end_organ.py`, 19/19).

## 1. Flag
Add a default-off `track_belief: bool = False` ctor flag on `hdlab/situation_reader.py::SituationReader`
(mirrors `timeline_register` / `causation_typed` / SPACE's `track_space`). When False, `read()` is
byte-identical to today.

## 2. SituationModel fields (additive)
```
belief_timeline: object = None       # the promoted hdlab.belief_timeline state, driven by the reader
believes: callable = None            # believes(agent, fact, t) -> value | None   (belief-at-T)
knows: callable = None               # knows(agent, fact, t) -> "current"|"stale"|"ignorant"
```

## 3. read() wiring (only when track_belief=True)
Compose the reader's OWN extraction (all glass-box, no LLM at inference), exactly as
`experiments/_belief_reader.py::drive()` proves end-to-end:
1. **Reality track** — object-move (location) + `hdlab.state_register` (status change-of-state, factivity-aware
   veridicality gate), observation-GATED by `hdlab.perceptual_access_ledger`.
2. **Belief-assertion track (DOMINANT)** — RULE0 narrator-epistemic + RULE2 testimony read the belief VALUE off
   mental/speech verbs (substrate-native; the disjunction guard + reliability-discounting are in `_belief_reader`).
3. **Inference track** — the 3-schema exclusion/transitive-spatial/modus-ponens edge extractor →
   `belief_timeline.fired_inference_events` (evidence-gated).
4. Merge on the SENT-INDEX axis (chrono from `timeline_register` when on, else narration); reality separate;
   ignorance = `None`. Source-tag each update (perception/testimony/epistemic/inference).
Promote `experiments/_belief_reader.py` → `hdlab/belief_reader.py` (it already imports only promoted organs:
belief_timeline, perceptual_access_ledger, state_register, the frontend parse).

## 4. Read-outs
`believes(A,F,t)` = `belief_timeline.timeline_belief`; `knows(A,F,t)` = current/stale/ignorant vs the reality
track (Butterfill & Apperly registration). Value equivalence uses the meaning-tolerant WordNet path
(`state_register` synonym+entailment) so paraphrase (deceased≈dead) is not scored as wrong.

## 5. Witness (required before flip)
`verification/test_belief_at_t_end_to_end_organ.py` (19/19) + `experiments/exp_belief_fantom_infoaccess_v1.py`
(external FANToM: reader beats floor + twin CI-sep; false-belief 0.985). Register capability
`belief_dimension_live_reader_v1`.

## 6. Flip policy
Stays DEFAULT-OFF until owner approval. Bundle-or-separate landing is a strategy call; recommend landing
default-off now (compounds with p2 parser + state_register, no downside when off).
