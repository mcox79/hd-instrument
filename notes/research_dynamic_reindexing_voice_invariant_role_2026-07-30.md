# Research: is voice-invariant thematic role the OUTPUT of a dynamic reindexing process onto a canonical event slot, not a static encoder code? — 2026-07-30

Scope: level-2 design drill. Pressure-tests the hypothesis that all three prior encoder-objective
attempts failed because we built the WRONG FORM of the organ — role is not a static geometric code in
surface encoder geometry, it is the OUTPUT of an incremental, revisable reindexing computation that
writes surface NPs onto a canonical event representation (agent/patient slots), and is voice-invariant
only because it lives in that constructed representation, not in the encoder's hidden states.

Builds ON (does not re-derive) the two dedup files:
- `research_structural_objective_fix_voice_invariant_role_2026-07-30.md` (PRIMARY was token-level
  role-discriminative contrastive ON ENCODER REPS — still a STATIC-geometry constraint).
- `brain_syntax_to_role_mechanism_and_forward_predictive_encoder_spec_2026-07-30.md` (causal + PE-gate
  encoder — now MEASURED-REFUTED: cross-voice 0.017/0.000, inverts by position; a CONTENT problem, not
  a variance/collapse problem).

Calibration per [[feedback-lit-scan-calibration-penalty]]: P deflated 0.15-0.25, novel-synthesis capped
0.50, ESTABLISHED/CONTESTED per claim, CITED@/REASONED@ tagged. 4 parallel Sonnet lit-scans this cycle
(generic-terms-only per [[feedback-query-privacy-decomposition]]): (A) structured/incremental decoders +
novel-verb generalization; (B) grounding-anchor / shared-event pivot necessity; (C) formal static-vs-
dynamic expressivity; (D) computational cue-competition/reindexing process models. Field advisor run
(HDC field map — free-probability/semiconductor top candidates — correctly NOT scoring this out-of-matrix
NL-encoder physics drill). KB-check carried from dispatch (top cosine 0.30, no prior overlap beyond the
two dedup files).

---

## HEADLINE

The wrong-form diagnosis is CONFIRMED, but the literature relocates the fix and sharpens it in TWO ways
the prior notes missed. (1) The decisive published evidence is EMPIRICAL, not formal: on COGS (Kim &
Linzen 2020), flat static seq2seq encoders — transformer AND LSTM alike — score ~0% on structural /
active-passive / novel-verb generalization while scoring 96-99% in-distribution, and the fix that lifts
structural generalization to near-perfect is a **structured, canonical-OUTPUT decoder** (Weissenhorn et
al. 2022, AM-parser; Herzig & Berant 2021, span-based), NOT recurrence per se (LSTM also fails; the RASP
compiled-transformer result shows a static transformer CAN do it when its computation is explicitly
compositional). So the causal lever is "decode to an explicit canonical structured representation," of
which the brain's incremental-revision process (TMS-confirmed reanalysis region for passives,
PMC10158617; Vosse-Kempen competitive relaxation; St.John-McClelland Sentence Gestalt query-readout) is
the biological implementation — recurrence/incrementality is a natural route, not the essence. (2) The
invariance ANCHOR is a constructed EVENT/situation representation that is provably NOT the text-surface
form (Zwaan situation models; Gleitman syntactic bootstrapping indexes an already-represented event) —
BUT the perceptual-grounding-necessity claim (Harnad, Bender & Koller) is a contested philosophical
position under live rebuttal, and CL-SRL shows an ANNOTATION/ALIGNMENT pivot substitutes for perceptual
grounding: **our gold cross-voice alignment can serve as the amodal event-tuple anchor without external
perceptual grounding — PROVIDED we supervise to the canonical event tuple, not to surface encoder
geometry.** TOP RECOMMENDATION: stop trying to make voice-invariant role LIVE in the encoder (measured-
failed 3x); instead build a small glass-box LEARNED recurrent reindexing DECODER on top of the encoder
that reads morphosyntactic cues incrementally, reassigns surface NPs to canonical agent/patient slots,
is CUE-triggered (not PE-triggered), is supervised by a query-based role probe against the canonical
event tuple, and feeds the substrate's existing FHRR role-filler binding. Read the probe off the
DECODER OUTPUT, not the encoder hidden state.

---

## 1. BIOLOGY — the precise computational FORM of the reindexing process

The prior spec named the ERP stages (ELAN/LAN/P600) and the theories (TDH, eADM, DLT). This cycle names
the borrowable ALGORITHM and the OUTPUT locus. Three convergent process-model families, all sharing one
property: **role is a query against a constructed event representation the process incrementally builds
and REVISES on cue arrival — it is never read as a fixed function of serial position.**

- **St. John & McClelland 1990 "Sentence Gestalt" (the closest direct analog) — ESTABLISHED, dated.**
  A simple recurrent net reads words incrementally, updating a distributed "Gestalt" state
  (h_t = f(W_in x word_t + W_ctx x h_{t-1})). Role is NOT read off the state directly; it is read via a
  **query-based probe**: present a role query ("AGENT?") to an output stage trained (backprop) to emit
  the correct filler given (Gestalt state, role query). Handles active/passive; revision on the
  disambiguating cue (the voice marker) happens through ordinary recurrent state update. THE
  load-bearing transfer (CITED@): the supervision that installs voice-invariant role is a **query-based
  role-filler readout**, and the invariant lives in the constructed Gestalt state, not surface order.
  Known limitation (CONTESTED / the exact crux for us): novel-word/filler generalization is "unclear"
  and it was demonstrated only on a toy finite verb-role world. Modern revival: Rabovsky, Hansen &
  McClelland 2018 (Nat. Hum. Behav.), same architecture at larger scale; N400 = norm of the Gestalt
  state-change between words (an update-magnitude signal, NOT itself a role-reassignment event).
- **Vosse & Kempen 2000 (Cognition) — the most literal reindexing OPERATION. ESTABLISHED.** A localist
  interactive-activation-and-inhibition network: grammatical-function/role bindings are the STABLE
  POINTS of a competitive relaxation dynamics; a late disambiguating cue (case marker, voice auxiliary)
  shifts the stable state via RENEWED relaxation — i.e. garden-path reanalysis IS the network
  re-settling. Borrowable update rule: cue-triggered competitive relaxation over candidate role-slot
  bindings (winner-take-all with lateral inhibition), which is exactly a "detect cue -> reassign NP to
  canonical slot" operation.
- **eADM cue-competition (Bornkessel-Schlesewsky) + Competition Model (Bates & MacWhinney) —
  ESTABLISHED framework, CONTESTED/underspecified computation.** Role assignment = weighted integration
  of cues (case > agreement > animacy > word order, language-weighted); actor status assigned "as fast
  as possible" then RE-competed when a more prominent candidate appears. Cue validity = availability x
  reliability, LEARNED from corpus statistics — this is the LEARNED-cue-weighting the build needs. Exact
  closed-form update NOT recoverable from primary text this cycle (three PDF extractions failed — flag:
  the "weighted-sum winner-take-all" characterization is secondary-source, not a sourced equation).
- **Neural confirmation that passive role assignment IS a distinct revision step (CITED@, new this
  cycle):** TMS to left posterior parietal (PMC10158617) causally disrupts passive-sentence role
  assignment specifically — the brain's passive solution is architecturally a REANALYSIS step on top of
  a first-pass parse, not a single-shot readout. ERP correlate (ScienceDirect S0911604419301290): a
  distinct later signature for passive vs active thematic assignment. Both support "role = output of a
  revision process," CONTESTED only at the exact locus.

**Is the STATIC-vs-DYNAMIC framing literature-supported — can a static encoding provably NOT hold
voice-invariant role while a recurrent/incremental process can?** PARTIALLY, and the honest answer
CORRECTS the framing:
- FORMAL "provably cannot": WEAK / over-reaches (thread C). Hahn 2020 and Merrill-Sabharwal (log-precision
  transformers = TC0) bound what a fixed-depth pass computes AS INPUT LENGTH GROWS; they do NOT show a
  bounded-length single-sentence canonicalization is outside TC0. Chain-of-thought results (Li et al.
  2024; Merrill-Sabharwal 2024) prove iteration adds serial power for "inherently serial" problems, but
  no work establishes canonicalization is inherently serial. P(formal "provably cannot" holds for
  bounded canonicalization) ~0.30 deflated.
- EMPIRICAL "static fails, structured succeeds": STRONG (threads A+C). COGS: static seq2seq (transformer
  AND LSTM) ~0% on structural/voice/novel-verb generalization, 96-99% in-distribution — a
  well-replicated demonstration that a flat static readout is genuinely the wrong form (this IS our
  0.016/0.402 inversion in a public benchmark). Weissenhorn et al. 2022 (same COGS splits): a
  compositional/structured DECODER gets near-perfect structural generalization. Herzig & Berant 2021:
  span-structured decoding 61->89. **BUT the causal lever is explicit compositional OUTPUT structure,
  NOT recurrence:** LSTM (recurrent) also fails COGS; the RASP result (arXiv:2504.15349) shows a static
  transformer with compiled/constructed weights ALSO solves COGS structural gen — the failure is what
  gradient descent FINDS, not architectural inevitability. **Net verdict: wrong-FORM confirmed
  empirically; the right form is "produce an explicit canonical structured event representation," and
  the incremental/recurrent revision process is the brain's IMPLEMENTATION of that, not the abstract
  requirement.** This is a real refinement of the topic hypothesis, not a rubber-stamp of it.

## 2. AGGRESSIVE COUNTER-VET — is the wall FAIR, and does the organ need a grounding anchor?

**Is the wall FAIR or construction-determined?** FAIR, with a precise re-reading. COGS establishes that
static seq2seq genuinely fails structural/novel-verb role generalization even with adequate data — so
the 0.017/0.000 wall is NOT merely "underpowered 18k steps," it is a property of asking a flat readout
of static geometry to do canonicalization. The wall is fair; the misdiagnosis was WHERE the invariant
should live (encoder geometry) and WHAT the readout should be (linear probe of hidden state vs. a
decoded structured tuple).

**Can a text-only synthetic active/passive corpus teach voice-invariant role at all, or is it
under-anchored without a shared EVENT pivot?** (thread B)
- Convergent ESTABLISHED finding: the invariant lives in a CONSTRUCTED event/situation representation
  that is explicitly NOT the text-surface form (Zwaan & Radvansky 1998 event-indexing situation models;
  Gleitman syntactic bootstrapping — syntax INDEXES an already-represented event, it does not manufacture
  it; children acquire passive role-reversal LATE and effortfully, ~age 4-6). The role becomes
  position-invariant at the situation-model layer, a separate representation the comprehender builds.
- Is PERCEPTUAL grounding REQUIRED? CONTESTED, not proven. Harnad 1990 (symbol grounding) and Bender &
  Koller 2020 (octopus / form-only cannot learn meaning) are ARGUED philosophical positions under live
  rebuttal (arXiv:2407.21070, 2024) — NOT empirical proofs, and none address agent/patient role
  specifically. Do NOT treat "text can never do it" as a hard ceiling.
- DECISIVE nuance (CITED@): cross-lingual SRL (alignment-free CL-SRL, ACL 2020) successfully propagates
  role structure across surface forms using a PIVOT — but the pivot is human GOLD role annotation (the
  invariance was injected by annotators who did the grounding when they labeled). This is the exact
  structural analog of OUR setup: **gold cross-voice alignment to a canonical event tuple plays the same
  role as the annotation pivot.** So an amodal, symbolic event tuple CAN serve as the invariance anchor
  without perceptual grounding — IF the supervision target is that shared tuple, dense enough to force
  the SAME internal representation for both voices.

**What the brain has that our current setup lacks (name it precisely):** a constructed situation-model
EVENT SLOT that is the invariance locus, PLUS an incremental cue-triggered process that WRITES canonical
role assignments into it and REVISES them. The substrate HAS the slot machinery (FHRR role-filler
binding — the "event tuple" container) but has NO learned process that writes canonical agent/patient
into it FROM raw syntax; and it has been trying to make the invariant live in the ENCODER instead of in
the slot. The missing organ is the reindexing DECODER between them, plus a supervision target that IS
the canonical tuple (not surface geometry).

**Grounding-anchor verdict:** the organ does NOT need external PERCEPTUAL grounding, but it DOES need a
shared canonical EVENT-TUPLE supervision target as the invariance anchor. Our gold cross-voice alignment
+ the existing FHRR slot ARE that anchor, amodal-KB style — consistent with the standing "amodal hub /
KB-as-world-model" framing. P(amodal event-tuple anchor sufficient, perceptual grounding NOT required)
~0.40 deflated; the residual risk (Harnad/Bender-Koller right; alignment-alone insufficient for novel
role-filler combos) is exactly what the can-fail test's held-out-novel-verb split measures.

## 3. MINIMAL BRAIN-FAITHFUL BUILD — a glass-box LEARNED recurrent reindexing decoder

Design-only (exp_dev owns pre-reg). A small module that is Sentence-Gestalt-faithful in supervision,
Vosse-Kempen-faithful in the revision operation, cue-triggered per the topic ask, and writes to the
existing FHRR slots.

**Form:** a small recurrent DECODER sitting ON TOP of the (frozen or lightly-tuned) token encoder — NOT
another encoder-objective retrain. This is the key departure from both dedup notes: note #1 shaped
encoder geometry (contrastive); note #2 retrained the encoder (causal + PE-gate, refuted). The invariant
is measured-absent from encoder geometry 3x, so we stop putting it there.

- **State:** a small role-hypothesis register `r` (a handful of vectors: provisional agent-slot,
  patient-slot, + tracked NP mentions), INITIALIZED to the canonical default (first-mentioned-NP =
  provisional agent). This default-first is DELIBERATE and brain-faithful (eADM/TDH: the canonical
  default is computed first; the deficit is FAILING TO REVISE it, not computing it).
- **Incremental read + CUE detection (not PE):** step left-to-right over token latents; a small LEARNED
  cue-detector fires on morphosyntactic cues — passive auxiliary + past-participle + "by"-phrase, case
  markers, agreement. Cue detection is a learned classifier over the encoder's OWN latents (glass-box,
  inspectable), NOT an external parse. This directly answers the topic's "triggered by cue-detection,
  not prediction-error" — and distinguishes it from note #2's refuted PE-gate.
- **Reindex OPERATION (Vosse-Kempen relaxation):** on a cue firing, run a short competitive-relaxation /
  gated-swap over `r` that reassigns the surface NPs to canonical slots (e.g. passive marker -> swap
  provisional agent<->patient). Winner-take-all with lateral inhibition; a few iterations, glass-box
  (the reassignment is a readable state change, not a black-box attention smear).
- **Supervision (Sentence-Gestalt query-readout, against the canonical event tuple):** train end-to-end
  with a QUERY-BASED role probe — given (final `r`, "AGENT?"/"PATIENT?"), emit the correct filler; loss
  is against the GOLD canonical (agent=X, patient=Y) tuple from synthetic generation. The alignment-
  pivot (thread B / CL-SRL) is exactly this shared-tuple target for both voices. Optionally add the
  Vosse-Kempen-style auxiliary that the two voices of one event must produce the SAME `r`.
- **Output:** `r`'s canonical slots feed the existing FHRR role-filler binding (the slot container the
  substrate already has). NOTE (CONTESTED, per prior VET): binding-by-synchrony underlying FHRR is a
  contested hypothesis (mixed-selectivity rival better-credentialed) — this build does NOT rest on that;
  it only requires the slot to hold (agent=X, patient=Y), which any conjunctive/TPR binding satisfies.
  Do not over-claim the binding mechanism.

**Allowed vs FORBIDDEN (standing [[feedback_no_bolt_on_existing_reader_earn_comprehension_own_mechanism]]):**
- ALLOWED (this build): a LEARNED cue->reindex competence, trained end-to-end with explicit supervision
  on the reindex operation, operating on the encoder's OWN latents. Gold heads / gold cross-voice
  alignment used at TRAIN time are TRAINING TARGETS generated by the synthetic corpus — the module
  learns to produce them. At INFERENCE the module uses NO external parser: it reads its own cue-detector
  and relaxes its own state. This is an acquired competence, matching the developmental framing.
- FORBIDDEN (explicitly NOT this): supplying a parse from an external parser at inference time, or
  bolting a pretrained SRL/dependency reader onto the pipeline. The distinction is train-time gold
  target (allowed, it is the thing being learned) vs inference-time external parse (forbidden).

This is a NEW module, not a re-skin of note #2's gate: it operates at the token->clause granularity, is
cue-triggered, is a DECODER reading to canonical slots (not an encoder objective), and its supervision
is a query-based readout against a canonical event tuple (not next-latent prediction).

## 4. CHEAP CAN-FAIL TEST (design-only; exp_dev owns pre-reg)

The decisive change from all prior tests: **read the probe off the reindexing DECODER's OUTPUT (the
canonical role-slot assignment / query-probe filler), NOT off the encoder hidden state.** The encoder
probe stays as the already-measured inverted baseline (0.016/0.402).

- **Corpus (minimal):** N transitive templates -> matched active + passive pairs, CONTROLLED fillers
  (vary determiners/adjectives + a pronominalized variant so cross-voice alignment CANNOT be solved by
  surface string identity). HELD-OUT split of NOVEL verbs AND novel filler nouns never seen in training
  — this is the crux surface (COGS structural gen ~0%; GrAPES novel-label failure; Petty 2022
  novel-verb break; Sentence Gestalt novel-word "unclear"). Non-held-out passes are worthless here.
- **Metric definition:** query-based canonical-role accuracy = P(module emits correct gold filler | 
  sentence, role-query), evaluated separately for active and passive, on held-out novel verbs+fillers.
  PLUS cross-voice consistency = P(active and passive of the SAME event yield the SAME agent/patient
  assignment).
- **Arms:** (A) reindexing decoder on encoder latents (the build); (B) static-encoder linear probe
  (the measured 0.016/0.402 inverted baseline, unchanged); (C) position-default heuristic (first-NP=
  agent) as the explicit floor the decoder must beat on passives; standing floors BoW 0.33, shuffled
  ~0.51.
- **HARD-PASS (pre-registered):** query-based canonical-role accuracy **>= 0.70 for BOTH active AND
  passive on held-out novel verbs+fillers**, AND cross-voice consistency **>= 0.70**, WHILE the static-
  encoder linear-probe baseline (arm B) stays inverted/near-floor (**<= 0.40**, as measured). Aligns
  with the existing cell's ROLE_PROBE_PASS_MIN=0.70.
- **HARD-FAIL (pre-registered):** EITHER voice **<= 0.55** on held-out novel verbs (no better than the
  position-default arm C — the module never learned to revise), OR passes on TRAINED verbs but held-out
  **<= 0.55** (memorization; COGS/Petty signature), OR passive accuracy tracks the first-NP=agent
  default (inversion persists — cue-triggered revision did not fire on novel verbs).
- **PARTIAL / MIDDLE (report explicitly):** held-out both-voice in [0.55, 0.70] with cross-voice
  consistency preserved — no longer inverted, genuinely revising on some novel verbs, not yet at bar.
  Informative (rules the direction in; motivates cue-curriculum / scale). Assessed MORE likely than
  HARD-PASS.
- **Construction-artifact flags (what makes a PASS fake):** (1) pass on trained verbs only -> the
  held-out-novel-verb split is the ONLY valid pass surface. (2) cue-detector degenerates to encoding
  linear position (check it fires on the voice marker specifically, not on token index). (3) alignment
  solvable by surface string identity -> filler-variation + pronominal variants mandatory. (4) if the
  gold-tuple target leaks the answer via a trivial mapping, verify the module generalizes the OPERATION
  (novel verb, held-out) not the lookup.

## P estimate (deflated)

**P_deflated(HARD-PASS on held-out novel verbs) = 0.30.** Base REASONED@ ~0.48 (this directly targets
the measured failure, moves the readout to a structured canonical output which is the EMPIRICALLY-shown
fix on COGS-family benchmarks, supervises against the amodal event-tuple anchor which CL-SRL shows can
substitute for grounding, and borrows a validated process model — Sentence Gestalt query-readout +
Vosse-Kempen relaxation) minus ~0.18 lit-calibration penalty. Penalty is moderate-not-maximal: the
structured-decoder fix is well-replicated (Weissenhorn near-perfect on COGS structural gen), BUT
novel-PREDICATE generalization is the specific unsolved case even for structured systems (GrAPES AMR
parsers fail unseen labels; TPR novel-composition unsolved without added machinery; Sentence Gestalt
novel-word "unclear"), and no published work runs this exact ablation (static-encoder-probe vs
reindexing-decoder on a voice-invariant novel-verb probe). Below the 0.50 novel-synthesis cap.
**MIDDLE/PARTIAL (off-inversion, held-out in [0.55,0.70]) assessed MORE likely than HARD-PASS, P~0.40.**
A HARD-FAIL remains genuinely ambiguous between "amodal alignment-pivot insufficient, perceptual
grounding needed (Harnad/Bender-Koller)" and "right direction, insufficient corpus-diversity / cue
curriculum" — must be reported as such, not as clean refutation.

## Cross-thread synthesis with the two dedup files

- **Supersedes note #1's implicit target.** Note #1's PRIMARY (token-level role-discriminative
  contrastive) still constrains STATIC ENCODER geometry — the same locus measured-empty 3x. This note's
  evidence (COGS: flat static readout ~0%; the fix is a structured OUTPUT decoder) argues the contrastive
  should be REDIRECTED from "pull same-referent encoder token-reps together" to "decode both voices to
  the SAME canonical (agent=X, patient=Y) event tuple." The event tuple is the invariance anchor; the
  encoder reps are not. Note #1's within-voice anti-collapse gate is still valid and carried forward.
- **Explains AND supersedes note #2's refutation.** Note #2 (causal + PE-gate encoder) is refuted; this
  note diagnoses WHY at a deeper level than note #1: it was still an ENCODER objective, and its gate was
  PE-triggered. The brain's passive solution is a CUE-triggered REVISION writing to a canonical slot
  (TMS reanalysis region; Vosse-Kempen), not a prediction-error gate on encoder geometry. The new build
  moves the organ OUT of the encoder into a decoder and swaps PE-trigger for cue-trigger.
- **Reuses the existing fair-test infrastructure with ONE change:** the probe reads the decoder output
  instead of the encoder hidden state — the same 74d4ea0c1 nearest-centroid/query-probe bands, held-out
  novel verbs, within-voice/cross-voice consistency checks. The FHRR slot (WM_PROVEN, 88d050955) is the
  reused output container.
- **Consistent with standing invariants:** from-scratch, glass-box, no-external-LLM-at-inference,
  no-borrowed-embedding, no-bolt-on-parser. The reindexing decoder is a native learned own-mechanism;
  gold-tuple targets are train-time supervision (the thing learned), not inference-time parses.
  Binding-by-synchrony remains CONTESTED and is NOT load-bearing here (only a (agent=X, patient=Y) slot
  is required, satisfiable by any conjunctive/TPR binding).

## Substrate-product implications (never publication-framed)

Voice-invariant role reading is the product line between "the substrate slot-fills when TOLD who the
agent is" and "the substrate figures out who the agent is from grammar alone" — templated-composition
demo vs. real comprehension (`WHERE_WE_ARE_NOW.md` honest gap). The reframe is product-actionable: the
capability is not a better ENCODER, it is a small learned REINDEXING DECODER that writes canonical roles
into the slot the substrate already has — cheaper, glass-box, and inspectable (you can watch the reindex
fire on the voice marker). Even a MIDDLE-band result unblocks the direction; a HARD-PASS would be the
substrate's first measured voice-invariant role-reading capability, and it lands the role in the same
canonical event-tuple form the KB/situation-model already speaks, wiring comprehension INTO the world
model rather than beside it.

## Anchor candidates for pickup (ranked; exp_dev owns pre-reg — no inline experiment design)

1. **PRIMARY** — build the small glass-box LEARNED recurrent reindexing DECODER (Part 3) on the existing
   encoder's latents: role-hypothesis register init to canonical default; LEARNED morphosyntactic
   cue-detector over own latents; Vosse-Kempen competitive-relaxation reindex on cue firing; Sentence-
   Gestalt query-based role-probe supervision against the GOLD canonical (agent,patient) event tuple;
   output feeds existing FHRR slots. Fair-test = the 74d4ea0c1 probe cell, but read off the DECODER
   OUTPUT (new arm), held-out novel verbs+fillers, both-voice + cross-voice-consistency bands from Part
   4. Carry the resumable-per-unit + (seed,arm) checkpoint discipline. Why now: directly targets the
   3x-measured 0.017/0.402 wall by moving the organ out of the encoder, cheapest structured-output route.
2. **SECONDARY (bundle same dispatch)** — redirect note #1's contrastive to a CANONICAL-EVENT-TUPLE
   decode target (both voices -> same tuple) instead of encoder-token-rep pull-together, as a
   mechanism-lighter control arm; isolates whether the explicit reindex OPERATION is needed or whether a
   tuple-decode contrastive alone suffices.
3. **TERTIARY (only if #1/#2 land PASS/PARTIAL)** — a HARD-FAIL disambiguator: a well-powered
   text-only-with-dense-alignment run to test the Harnad/Bender-Koller "needs perceptual grounding"
   residual (thread B) vs. "amodal alignment-pivot sufficient" — the one question the primary can't
   itself disentangle.

Context pointers: `experiments/exp_syntactic_role_agent_patient_voice_probe_v1.py` + its metrics.json;
`experiments/exp_encoder_latent_pc_arc_v1.py`; `hdlab/slot_attention_wm.py` (FHRR slot container);
`notes/research_structural_objective_fix_voice_invariant_role_2026-07-30.md`;
`notes/brain_syntax_to_role_mechanism_and_forward_predictive_encoder_spec_2026-07-30.md`;
`notes/WHERE_WE_ARE_NOW.md` ("THE ENCODER WALL").

## Citations (verified count)

Thread A (structured/incremental decoders) — Dyer et al. 2016 (RNNG, arXiv:1602.07776); Hale et al.
2018 / Brennan et al. 2020 / Kuncoro (RNNG brain-fit); Kim & Linzen 2020 (COGS, EMNLP, arXiv:2010.05465,
ESTABLISHED, decisive); Weissenhorn et al. 2022 (arXiv:2202.11937, compositional parser fixes COGS
structural gen); Herzig & Berant 2021 (span-based, arXiv:2009.06040); RASP/ReCOGS compiled-transformer
(arXiv:2504.15349, CONTESTED re recurrence-necessity); GrAPES 2023 (AMR unseen-label/structural gaps);
Smolensky TPR + "RNNs Implicitly Implement TPRs" (arXiv:1812.08718); attention-based iterative TPR
decomposition (arXiv:2406.01012).
Thread B (grounding anchor) — Landau & Gleitman 1985 / Lidz & Swanson (syntactic bootstrapping);
PMC9220815 (Russian passive ERP, late acquisition); Harnad 1990 (symbol grounding, ARGUED); Bender &
Koller 2020 (ACL, octopus, ARGUED/CONTESTED); arXiv:2407.21070 (2024 octopus rebuttal); Bisk et al.
2020 (Experience Grounds Language, EMNLP); CL-SRL alignment-free (ACL/EMNLP 2020) + Bayesian multilingual
SRL induction (arXiv:1603.01514) — annotation-as-pivot; Zwaan & Radvansky 1998 + Zwaan 2025 (situation
models, event-indexing); Regneri et al. 2013 (grounded verb-argument from video).
Thread C (formal static-vs-dynamic) — Hahn 2020 (TACL, self-attention limits); Merrill & Sabharwal 2023
(NeurIPS, log-precision = TC0) + 2024 (ICLR, CoT expressivity); Li/Liu/Zhou/Ma 2024 (ICLR, CoT solves
serial problems); Strobl et al. (TACL survey); Dehghani et al. 2019 (Universal Transformer); depth-
recurrent compositional-gen (2026 preprint); PMC10158617 (TMS passive reanalysis region, CITED@ new);
ScienceDirect S0911604419301290 (passive-vs-active thematic ERP).
Thread D (computational reindexing models) — St. John & McClelland 1990 (Sentence Gestalt, ESTABLISHED,
closest analog); Rabovsky/Hansen/McClelland 2018 (Nat. Hum. Behav., N400-as-update); Vosse & Kempen 2000
(Cognition, competitive-relaxation reindex, ESTABLISHED); Lewis & Vasishth 2005 (ACT-R cue-based
retrieval); Bates & MacWhinney Competition Model (cue validity, ESTABLISHED framework / CONTESTED
computation); Bornkessel-Schlesewsky eADM + Alday computational extension (CONTESTED/underspecified).
Carried from dedup notes (not re-verified): Grodzinsky TDH; Friederici ELAN/LAN/P600; Gibson DLT;
Osterhout & Holcomb P600; Papadimitriou/Futrell/Mahowald 2022; Petty/Wilson/Frank 2022; Schrimpf 2021;
Goldstein 2022; Caucheteux & King 2022; Strubell 2018 (LISA).
**Verified count this cycle: ~34 distinct works across 4 threads** (3 primary-PDF extractions failed in
thread D — cue-validity/eADM exact equations remain secondary-sourced, flagged). ESTABLISHED/CONTESTED
per-claim throughout; the weakest links (novel-predicate generalization for structured decoders; amodal-
vs-perceptual grounding sufficiency; recurrence-vs-compositional-output as the true lever) are named and
drive the P_deflated cap.
