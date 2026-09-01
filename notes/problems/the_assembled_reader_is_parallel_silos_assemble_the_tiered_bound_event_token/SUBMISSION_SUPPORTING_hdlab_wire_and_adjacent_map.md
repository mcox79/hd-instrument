# Supporting: proposed hdlab wire + adjacent-component brain-fidelity map

Solver session. I MAY NOT write `hdlab/` (Q111). This is the proposed change for the strategy session to
land after re-verification, plus the adjacent-component evaluation the deepening protocol requires.

## A. THE PROPOSED hdlab WIRE (default-off, additive, byte-identical when off)

The reader's dimensions are parallel silos because `read()` builds per-dimension LISTS and never a bound,
per-event token. The fix is a default-off flag that assembles the tiered bound-event-token backbone from
organs ALREADY in `hdlab/` (none currently imported by `situation_reader.py`).

**`hdlab/situation_reader.py`** — new default-off ctor flag `bind_event_tokens=False`, wired exactly like
the other dimension flags (`__init__` around L554-700; the read hook right before `return sm`, L1060):

```python
# __init__:
self.bind_event_tokens = bool(bind_event_tokens)   # default OFF -> byte-identical

# read(), immediately before `return sm` (additive; runs only when the flag is on):
if self.bind_event_tokens:
    from hdlab.bound_event_backbone import BoundEventBackbone   # NEW thin assembler (see B)
    sm.event_tokens, sm.episodic_store = BoundEventBackbone(d=1024).build(sm.events, sm.locations)
```

`SituationModel` gains two additive default-None fields (`event_tokens`, `episodic_store`); every existing
field is untouched, so with the flag off the p4 byte-identical signatures are preserved.

**`hdlab/bound_event_backbone.py`** — NEW thin assembler module (no new mechanism; it only COMPOSES existing
organs). It is the promotion target of `experiments/exp_tiered_bound_event_token_coref_v1.py`:
- BIND: per event, `token = Σ_r bind(ROLE_r, filler_r)` over {AGENT,PATIENT,PRED,TENSE} using
  `hdlab.binding.bind` + `hdlab.situation_model_accumulate.unit_phase_vec` (the FHRR basis, PINNED).
- CHUNK: `hdlab.n400_coherence_monitor.N400CoherenceMonitor` segments the event content stream at
  prediction-error boundaries; `hdlab.situation_model_multibank.MultiBankAccumulateRegister` is the slotted
  active WM register (small; Cowan).
- STORE: `hdlab.hippocampal_encoder.HippocampalEncoder` (DG-sparse + CA3) is the episodic store; a flushed
  segment is DG-encoded + CA3-written. Coref = CA3 pattern completion from a partial cue.
- QUERY: `episodic_store.resolve(query_attrs) -> best-matching event token / score` (the JOINT coref readout
  proven here). Glass-box, NO external LLM.

**Why byte-identical-when-off matters:** the p4 test's whole finding was that composition without binding is
not integration. This wire is the integration; leaving it default-off keeps the aggregate instrument stable
until the owner decides to flip it (a separate owner call, on this evidence).

**Dependency (stated, not hidden):** a truly in-`read()` canary also needs the meaning/where fields populated
per event; TENSE + AGENT + PATIENT + PRED are already on `EventRecord`; PLACE via `sm.locations.where_is`.
The token is only as faithful as the extraction feeding it (see the parser-wall diagnostic in SOLVED.md).

## B. ADJACENT-COMPONENT BRAIN-FIDELITY + OPTIMIZATION MAP (deepening-protocol step 2)

| organ | role in the backbone | brain mechanism | fidelity verdict | optimization / follow-on |
|---|---|---|---|---|
| `hdlab.binding` (FHRR) | the bound event token | conjunctive/relational coding (Smolensky TPR; VSA) | **PINNED-COMPUTATIONAL** (SEM/Franklin FHRR model); the algebra is the chosen basis | keep the algebra; the fidelity lever is STORE ORGANIZATION (below), not the binding op |
| `situation_model_multibank` | slotted active WM register | theta-gamma phase slots; Cowan capacity | **HIGH** — routing is a deterministic hash (honest: not noisy-cue) | fine for the active register; the episodic tier (DG/CA3) is what carries passage scale |
| `n400_coherence_monitor` | event-boundary chunker | Event Segmentation Theory (Zacks 2007); N400 (Kutas) | **HIGH on the operation**, but `tau/decay` are OUR-INVENTION tuned to a synthetic stream | **OPTIMIZATION**: tau=1.5 leaves a 283-event max segment on some coherent passages (no boundary fired). Sweep tau/decay on real event content; a learned transition predictor (vs running-mean) is the higher-fidelity predictor the organ's own docstring flags. |
| `hippocampal_encoder` (DG+CA3) | episodic store + pattern completion | Marr 1971 CA3; CLS (McClelland 1995); Treves & Rolls 1994 | **MIXED — DRILLED**: DG SEPARATION is HIGH (holds the store flat to M=256; prior DG HARD_FAILs were on the WRONG tier, re-scope CONFIRMED). But **CA3 COMPLETION is LOW-FIDELITY**: the retrieval path DG-separates the cue (should bypass DG: EC->CA3-direct) and single-steps CA3 (should be recurrent); measured partial-cue completion 0.24-0.56, and iterating COLLAPSES to a dominant attractor (0.02). | **FOLLOW-ON (well-scoped, high-value)**: a brain-faithful CA3 completer — EC->CA3-direct retrieval (DG is encoding-only) + sparse attractor dynamics that don't collapse. The DIRECT similarity path already completes at 1.00, so the store is USABLE today via that route; making the CA3 net itself faithful is its own `hippocampal_encoder` fidelity problem. |
| `slot_attention_wm` | (listed tier) learned content-addressed WM | PBWM (O'Reilly-Frank); slot-attention (Locatello) | **NOT USED HERE — honest gap**: it is a LEARNED torch module needing end-to-end training with an encoder; its learned ADDRESSING is orthogonal to the binding/coref claim, which the (untrained, faithful) multibank register carries | **FOLLOW-ON PROBLEM**: train `slot_attention_wm` as the active register and test whether learned addressing beats the deterministic multibank hash on real streams. Not load-bearing for THIS proof. |

## C. AUDIT UPDATE (for `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b — strategy folds in on re-verify)

- The four tier organs (`slot_attention_wm`, `situation_model_multibank`, `n400_coherence_monitor`,
  `hippocampal_encoder`) were BUILT ISLANDS (none imported by `situation_reader.py`). This problem ASSEMBLES
  three of them (multibank + n400 + hippocampal) + the FHRR bind into a tiered bound-event-token backbone and
  PROVES on REAL event structure (LitBank old fiction + UD-EWT modern) that it stores the JOINT the silos
  cannot: JOINT coref 1.00 vs late-fusion-of-marginals 0.60 (CI-sep +0.40), binding-shuffle collapses it
  (pos-recognition 1.00->0.12), tiered store holds to passage scale where the flat single bundle collapses
  (0.38@M=256).
- `hippocampal_encoder`/DG's prior HARD_FAILs were on the WRONG TIER (active-read); on the EPISODIC store
  (its faithful job) DG/CA3 holds retrieval flat — the brief's re-scope is CONFIRMED. Update DG's audit row.
- NEW deviation logged: `n400_coherence_monitor` tau=1.5 under-segments some long-coherent passages
  (max segment 283 events); tau/decay are OUR-INVENTION and need a real-content sweep (optimization, not a
  fidelity failure of the operation).
- ANALYTIC insight to record: a single passage-level superposition of event tokens is LINEAR, so its readout
  = SUM of marginals — it CANNOT represent the joint (it IS the silo). This is the concrete data-structure
  reason the reader's flat per-dimension registers are silos, and why the faithful shared token must be
  TIERED (chunked + pattern-separated), not one superposition.
- NEW `hippocampal_encoder` deviation (DRILLED, `experiments/_drill_ca3_completion.py`): the CA3 COMPLETION
  path is not brain-faithful — it DG-separates the retrieval cue (DG is an ENCODING op; retrieval should be
  EC->CA3-direct) and single-steps a Hebbian net that COLLAPSES to a dominant attractor under iteration
  (partial-cue completion 0.24-0.56, worsening to 0.02 when iterated). The DIRECT similarity route completes
  at 1.00. Update `hippocampal_encoder`'s audit row: DG-separation HIGH, CA3-completion LOW-fidelity; the fix
  is EC->CA3-direct retrieval + non-collapsing sparse attractor dynamics (a scoped follow-on).
