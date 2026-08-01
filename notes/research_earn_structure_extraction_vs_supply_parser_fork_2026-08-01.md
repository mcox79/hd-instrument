# Earning mention+role extraction from raw text vs supplying a trained parser: the honest fork (2026-08-01)

Scope: decision-support drill (does NOT decide the fork) answering the DECISION CONTEXT — the
substrate is blocked on real prose because it needs oracle-structured input; one path is to
supply the already-trained glass-box `pos_tagger`/`arc_parser` (decode the existing `arc_labeler`
ckpt for real nsubj/obj), the other is to EARN mention/role extraction the substrate's own way,
per the standing lock [[feedback_no_bolt_on_existing_reader_earn_comprehension_own_mechanism_2026-07-27]].
Calibration per [[feedback-lit-scan-calibration-penalty]]: P deflated 0.15-0.25, novel-synthesis
capped at 0.50, CITED@/REASONED@ tagged, hard-fail thresholds included.

**KB-check (mandatory, run first):** `director_kb_query.py --filename-contains "mention detection
referent"` -> zero matches (fallback grep also empty). `director_kb_query.py "unsupervised grammar
induction emergent syntax trees language model"` -> top cosine 0.27 (wordnet/generic concept-node
noise only, no prior synthesis). This drill's two anchor questions (brain mention/referent
detection; self-supervised structure induction as an EARN path) are genuinely new territory —
built on, not duplicating, the two directly-relevant prior notes read in full before this drill:
`notes/brain_syntax_to_role_mechanism_and_forward_predictive_encoder_spec_2026-07-30.md` (brain
mechanism for ROLE assignment + a build-ready causal-predictive-encoder spec, already covers
Friederici ELAN/LAN/P600, Bornkessel-Schlesewsky eADM, TDH, Schrimpf/Goldstein/Caucheteux&King
causal-prediction-as-brain-fit evidence — REUSED verbatim below, not re-derived) and
`notes/research_learned_parser_clause_seg_np_head_blueprint_2026-07-18.md` (glass-box learned
parser blueprint — NP-head-finding + clause-seg via transparent transformation-based/CRF learners
trained on gold spans — this is the exact shape of the "middle case" analyzed in Part 3 below).

---

## HEADLINE

The brain builds mentions+roles incrementally from raw input via a staged predict-commit-revise
cycle (already established in the 07-30 note for ROLES; this drill adds the MENTION side:
discourse-referent introduction is signaled by indefinite-NP encounter and held/updated in a
working-memory buffer, ERP-dissociable from referent re-activation — Gundel/Heim DRT theory,
ACT-R memory-chunk models, biorxiv ERP/oscillation evidence). The field has a genuinely mature,
ALREADY-EXISTING third option beyond "supply the trained parser" vs "build a StructFormer from
scratch": **self-supervised structure induction** (Manning et al. 2020 PNAS; StructFormer;
ON-LSTM/PRPN) — architectures that induce dependency/constituency trees as a byproduct of their
OWN next-word/masked-word prediction objective, with **zero gold parse ever touching training** —
this is the most constraint-clean EARN option and is a direct, low-marginal-cost extension of the
causal-predictive-encoder ALREADY spec'd in the 07-30 note (same causal-LPC architecture, add a
syntactic-distance readout). **The honest fork (Part 3) is sharper than "fast-but-forbidden vs
slow-but-clean": training OUR OWN parser on UD-EWT (the middle case) is argued here to still sit
on the SUPPLIED side of the line**, because what makes a mechanism "earned" is not who ran the
training loop but whether the structure categories came from the substrate's own predictive error
on its own experience (self-supervised induction) or from fitting an externally-authored human
labeling scheme (UD's treebank categories) — flagged explicitly as a REASONED interpretation of
the lock's intent, not a USER ruling, pending clarification.

---

## Part 1 — brain mechanism: raw text -> mentions + roles, incrementally (cited, deflated)

### 1.1 Roles (REUSED from 07-30 note, not re-derived)

Full citation chain already banked: Caramazza & Zurif 1976 + Grodzinsky TDH (first-noun-agent
default when structure-building fails); Friederici ELAN/LAN/P600 staged model (BA44/45); Bornkessel-
Schlesewsky eADM (cue-weighted, not linear-order-only, role computation); Osterhout & Holcomb P600
revision-on-disambiguation. **Net picture: role assignment is staged — a cheap canonical/linear
default computed early, held, and REPLACED (not blended) when a later cue (case marking, voice
morphology, "by"-phrase) forces revision.** ESTABLISHED core mechanism, CONTESTED at the precise
locus/universality level (see 07-30 note for the full established-vs-contested breakdown; not
repeated here).

### 1.2 Mentions — the piece the prior notes did NOT cover (new this cycle)

1. **Discourse Representation Theory (Kamp; Heim's novelty/familiarity condition)** — indefinite
   NPs conventionally INTRODUCE a new discourse referent; definite NPs/pronouns require the
   referent to already exist in the discourse model. This is a structural, not merely lexical,
   distinction: novelty-vs-familiarity is computed at the point of NP processing, not deferred.
   **ESTABLISHED** as the standard formal-semantics account; the exact processing-time claim
   (novelty checked online, not post-hoc) is the psycholinguistic extension below.
2. **ACT-R discourse-processing models (cited via cognitive-modeling literature on reference
   production/comprehension)** — each discourse referent encountered is represented as a memory
   CHUNK with an activation level; referent introduction creates a new chunk, referent
   re-mention/anaphora retrieves and re-activates an existing chunk via the general
   declarative-memory activation equations (recency+frequency), not a special coreference module.
   **CITED@, ESTABLISHED as a cognitive-architecture account; the specific activation-equation
   parameters are CONTESTED/model-fit-dependent**, not a universal brain constant.
3. **ERP dissociation of referent ACTIVATION vs INTEGRATION** (biorxiv preprint, "Dissociating
   activation and integration of discourse referents: evidence from ERPs and oscillations") —
   distinct electrophysiological signatures for (a) activating/introducing a referent into working
   memory vs (b) integrating a re-mentioned referent into the ongoing situation model. This is
   the MENTION-side analog of the ROLE-side P600-revision dissociation already in the 07-30 note:
   two functionally and temporally separate sub-processes, not one flat "process the NP" step.
   **CITED@, single-study strength — CONTESTED/needs-replication at the specific-signature level**,
   same caveat class as the passive-P600 finding already flagged in the 07-30 note.
4. **"Computing and recomputing discourse models" (ERP, MPG)** — the discourse model is actively
   UPDATED (not merely appended to) at each new sentence, consistent with the same hold-then-
   revise/update-on-prediction-error class of mechanism already used for roles (07-30 Part 2(b))
   and for the across-clause situation model (Kintsch CI, Zacks/Franklin SEM, already banked).
   **ESTABLISHED as consistent with the broader predictive-update literature; not itself a novel
   claim this cycle** — it is the mention-side confirmation that the SAME class of mechanism
   (predict, hold, update-on-PE) operates at the referent-introduction granularity too.

**Synthesis (established, load-bearing):** mention detection and role assignment are NOT two
independent modules bolted together in the brain — both are instances of the SAME general
mechanism (incremental commitment to a working-memory representation, updated/replaced on a
later cue or prediction-error spike), just triggered by different cue classes (indefinite
determiner + novelty-checking for mentions; case/voice/word-order cues for roles). This matters
directly for Part 2(c) below: the causal-predictive-encoder + PE-gated hold-then-revise machinery
already spec'd in the 07-30 note for ROLES is, on this evidence, the SAME organ that should also
be doing MENTION introduction — not a second bolt-on component.

---

## Part 2 — concrete glass-box options for EARNING mention+role extraction

### Option A — supply the already-trained `pos_tagger`/`arc_parser` (the baseline being compared against)

Decode the existing trained `arc_labeler` checkpoint for real nsubj/obj labels. Near-zero
additional build cost (checkpoint already exists, per DECISION CONTEXT). Not analyzed further
here as an "EARN" option — it is the supply-side anchor Part 3 compares against.

### Option B — self-supervised / unsupervised structure induction (NEW this cycle, most constraint-clean EARN path)

**Manning, Clark, Hewitt, Khandelwal, Levy 2020, PNAS, "Emergent linguistic structure in
artificial neural networks trained by self-supervision"** — networks trained ONLY on a masked/
next-word prediction objective (no gold parse, no treebank) develop internal representations from
which syntactic dependency structure and even anaphoric coreference can be RECOVERED (via probes),
without that structure ever being a training target. **ESTABLISHED, well-cited (PNAS, 300+
citations), directly on-point.**

**StructFormer (2020/2021)** — a concrete ARCHITECTURE (not just a post-hoc probe on an ordinary
transformer): adds a syntactic-distance + syntactic-height inductive bias to a transformer trained
purely on masked-language-modeling, and reads OUT both dependency and constituency trees as a
byproduct, fully unsupervised (no gold parse at any point). **ESTABLISHED architecture, direct
prior-art template for a "we build a structure-inducing head on our own encoder" option.**

**ON-LSTM / PRPN (Shen et al. 2018)** — earlier, simpler versions of the same idea: order neurons
by a learned "syntactic distance" so tree structure falls out of the recurrent state update.
**ESTABLISHED**, credited as the lineage StructFormer built on.

**Honest accuracy floor (deflating factor):** unsupervised constituency/dependency parsers
historically underperform supervised ones by a LARGE margin on standard English benchmarks (early
neural unsupervised parsers scored well below supervised parsers' 90+ F1; more recent variants
have narrowed but not closed this gap). **This is the single biggest feasibility cost of Option B**
— it is conceptually clean and directly reuses the 07-30 causal-LPC encoder's architecture (same
`TinyTransformer`, add a distance/height readout head), but the induced trees will be noisier than
either a supervised parser or hand rules, especially at our small scale (~158M tokens, small model).

**Brain-fidelity:** HIGH — this is architecturally the closest match to "structure emerges from
the substrate's own predictive processing of its own experience," which is exactly what Part 1
describes the brain doing (no external parse is ever handed to a human infant either — construction
grammar/usage-based acquisition, already cited in the 07-18 note, is the developmental analog of
self-supervised induction). **Glass-box-ness:** the syntactic-distance/height values are numeric,
inspectable, auditable — same transparency class as the hand-rule parser, better than an opaque
attention-probe-only account (StructFormer's readout IS the mechanism, not a post-hoc correlate).

### Option C — incremental predict-and-revise over the causal encoder stream (extends the 07-30 spec, does NOT require a separate induction head)

Directly reuse the causal-LPC encoder + PE-gated hold-then-revise state (`h_role`) already
spec'd in the 07-30 note, and extend it per Part 1.2's synthesis: the SAME PE-gate that revises
role hypotheses on a disambiguation spike should ALSO fire on indefinite-NP encounter to spawn a
NEW entity slot (mention introduction), using the discourse-referent-introduction mechanism as the
trigger condition. This is the cheapest option in marginal build cost (Part 4 below) because the
machinery already exists on paper; it is a NARROWER claim than Option B (it detects mentions/roles
as a side-effect of an existing predictive-coding pipeline rather than inducing full syntactic
trees), so it is lower-risk but also answers a smaller question (mention+role only, not full parse).

### Option D — distillation: existing trained parser as TEACHER, not as the deployed mechanism

Use the existing `pos_tagger`/`arc_parser` checkpoint's OUTPUT as a soft-label training signal to
pretrain/regularize Option B or C's structure-inducing head (StructFormer-style distance targets
initialized toward the teacher's parse, then fine-tuned on the substrate's own self-supervised
objective, teacher signal annealed out). This is a genuine middle path with a real precedent class
(knowledge distillation, teacher-student), analyzed for constraint-fit in Part 3.

---

## Part 3 — the honest fork (decision-support, not a decision)

### Supply-the-trained-parser (Option A)

- **Effort:** near-zero. Checkpoint exists; work is decode/wire only.
- **Feasibility:** HIGH, immediate. Already diagnosed as "partially usable... graceful
  degradation" per DECISION CONTEXT.
- **Brain-fidelity:** LOW-MODERATE. The parser's CATEGORIES (nsubj/obj, UD label inventory) come
  from a human-linguist-authored annotation scheme (Universal Dependencies), not from anything the
  substrate discovered through its own error-driven experience. The MECHANISM (transition-based/
  CRF architecture) has no principled brain-fidelity claim either way — it's an engineering choice,
  not a cognitive-architecture claim.
- **Constraint fit:** this is very plausibly exactly what
  [[feedback_no_bolt_on_existing_reader_earn_comprehension_own_mechanism_2026-07-27]] rules out —
  "every existing-reader use was a DISASTER... supplying the reading MECHANISM = anti-pattern."
  A trained arc-parser IS the reading mechanism (spans -> mentions -> roles), supplied wholesale.
- **Risk:** repeating the exact failure class the lock was written to prevent, with no new
  evidence this time is different.

### Earn-it-fully (Options B/C, self-supervised)

- **Effort:** HIGH for Option B (StructFormer-class induction head is a real architecture/training
  build, plausibly comparable in scope to the causal-LPC encoder build already spec'd — GPU-hours
  in the same 15-20h class per run, PLUS the induction-specific training instability StructFormer's
  own literature reports needs tuning). Effort MODERATE for Option C (reuses the 07-30 PE-gate
  verbatim, only adds a trigger condition + entity-slot allocation logic — smaller marginal build).
- **Feasibility:** Option B's accuracy ceiling at our scale is a real open question (unsupervised
  parsers underperform supervised significantly in the general literature; our tiny-model/158M-
  token regime is likely worse, not better, than the papers cited). Option C's scope is narrower
  (mention+role signal, not full trees) so is more likely to reach a usable bar, but has not
  itself been tested for mention-detection specifically (Part 1.2's synthesis connecting the
  PE-gate to referent-introduction is a NEW inference this cycle, not previously proposed or
  tested — REASONED@, not CITED@ for this specific application).
- **Brain-fidelity:** HIGH for both — this is the closest match to "structure emerges from the
  substrate's own predictive processing," the developmental/usage-based-acquisition analog already
  credited in the 07-18 note.
- **Constraint fit:** clean — no external parse, no external labeled treebank, ever touches
  training. Unambiguously on the EARN side of the lock.
- **Risk:** could cost real GPU-time/calendar-time and land at a noisier structure signal than the
  hand-rule parser already diagnosed as "partially usable," i.e. a genuine possibility of spending
  more to get less, at least on a first attempt — an honest cost, not hidden.

### The middle case — "we trained OUR OWN parser on UD-EWT" — where does it sit?

This is the sharpest open question and the one most likely to need direct USER adjudication.
**REASONED@ analysis (not a USER ruling — flagged explicitly as such):**

The operational test proposed here for "earned" vs "supplied" is: **did the structure categories
arise from the substrate's own predictive/comprehension objective operating on its own experience
(earned), or from fitting to an externally-authored human labeling scheme (supplied)** — regardless
of who ran the training loop or where the weights live. Under that test:

- Training a CRF/transition-based parser ourselves on UD-EWT's gold nsubj/obj/etc. labels is
  **still on the SUPPLIED side**. The substrate is not discovering "agent" and "patient" through
  its own error signal on its own comprehension task — it is being FIT to reproduce a linguist's
  pre-existing categorical scheme, exactly as if we had pulled spaCy off the shelf, just self-hosted
  and glass-box-transparent instead of a black-box library call. Self-hosting changes the
  transparency/auditability profile (a real, non-trivial improvement — this is why the 07-18 note's
  B1/B2 blueprint is still valuable engineering) but does NOT change which side of the
  earned-vs-supplied line the mechanism sits on, under the lock's stated rationale ("supplying
  the reading MECHANISM = anti-pattern" — UD's tagset + a treebank-fit parser IS a reading
  mechanism, transplanted rather than grown).
- Option D (distillation, teacher signal annealed to zero) sits closer to the middle but still
  imports the teacher's categorical scheme as an initialization bias — defensible as a
  bootstrapping/curriculum trick (analogous to how the brain's own construction-grammar
  acquisition is scaffolded by caregiver input, which is itself an external signal) but weaker on
  constraint-cleanliness than Option B's from-scratch self-supervision.
- Option B/C, by contrast, never require the categories "agent/patient/nsubj/obj" to exist at all
  during training — whatever tree/distance/entity-slot structure the model induces is validated
  post-hoc against downstream tasks or, at most, against a small held-out human-annotated eval set
  used ONLY for measurement, never for training gradient. That is the structurally different case.

**This is offered as decision-support, not settled: the USER may reasonably conclude "we trained it
ourselves" is close enough to earned (esp. combined with the 07-18 note's grounding-biased,
substrate-native head-selector feature, which IS a genuine substrate contribution on top of the
borrowed base). The analysis above is the clearest articulation available of why it might NOT
satisfy the lock, for the USER to weigh with full information.**

---

## Part 4 — the one most tractable EARN-path first step (measurement-first, can-fail)

**Step 0 (no compute, do regardless of which fork is chosen):** hand-annotate a small held-out
slice (~50-100 sentences of the existing grade-3 narrative corpus) for gold discourse-referent-
introduction spans (indefinite-NP-introduced mentions) and gold agent/patient role spans. This is
needed as an EVAL set under either fork and costs no GPU time.

**Step 1 (cheap, decisive, gated on the 07-30 causal-LPC encoder landing — it does not yet exist
as a trained checkpoint, only as a spec):** once/if the causal-LPC encoder + PE-gate from the
07-30 note is trained, run a CPU-only, closed-form probe (no new training): does the encoder's
OWN already-computed per-token prediction-error stream spike at gold referent-introduction
positions (Option C's hypothesis from Part 1.2/2C)?

- **Metric:** precision/recall of "PE-spike position" as a referent-introduction detector against
  the Step-0 gold spans.
- **Baselines:** (i) chance-matched random-position rate, (ii) a trivial lexical baseline
  ("a"/"an"/bare-indefinite-determiner detector).
- **HARD-PASS (pre-registered):** PE-spike detector beats the LEXICAL baseline by >=10 F1 points
  on referent-introduction spans, AND generalizes to referents introduced WITHOUT an indefinite
  article (bare plurals, proper-name-first-mention) where the lexical baseline scores near 0 —
  i.e., genuine structural signal, not a re-discovery of "a/an" pattern-matching.
- **HARD-FAIL:** PE-spike detector <= lexical baseline, or <= chance-matched random baseline —
  the causal encoder's existing PE signal carries no referent-introduction structure as a free
  byproduct, ruling out the cheapest version of Option C and pointing toward the heavier
  dedicated StructFormer-class induction head (Option B) as the next EARN step instead.

This step is cheap (reuses fully-built machinery once trained, CPU-only probe, no new training
loop) and decisive (a clean pass/fail that resolves whether mention-detection comes "for free" out
of the already-planned encoder work, before committing to the larger Option B build).

**P_deflated on Step-1 HARD-PASS: 0.28.** Base REASONED@ confidence ~0.45 (Part 1.2's
mention/role-same-mechanism synthesis is a plausible, literature-consistent inference) minus 0.17
lit-scan-calibration penalty (novel synthesis — no direct precedent tests "does a causal latent-
predictive-coding PE-gate spike at discourse-referent-introduction points," this exact question has
not been asked in the literature found this cycle) = 0.28, below the 0.50 novel-synthesis cap.
Gated dependency flagged explicitly: this test cannot run until the 07-30 spec's causal-LPC
encoder is actually trained — it is not itself the FIRST thing to build, Step 0 (annotation) is.

---

## Substrate-product implications

If Step 1 passes, mention detection becomes a near-zero-marginal-cost byproduct of the encoder
work already planned for the role-assignment problem — the single most efficient possible outcome
(one build serves both the "who" and "who-did-what-to-whom" halves of comprehension). If it fails,
the fork in Part 3 becomes live and requires a real Option-B investment (StructFormer-class
induction) or a USER decision to accept Option A's constraint risk. Either way this directly
informs the USER's use-parser-vs-earn-it fork named in the DECISION CONTEXT with a costed,
cited comparison rather than an unexamined default to whichever path is cheaper this week.

---

## Citations (verified count)

**NEW this cycle (2 WebSearch rounds, generic-term, query-privacy compliant):** Kamp/Heim DRT
novelty-familiarity condition (discourse referent introduction, indefinite vs definite NPs);
ACT-R discourse-processing / memory-chunk activation models of reference; ERP dissociation of
referent activation vs integration (biorxiv preprint); "Computing and recomputing discourse
models" ERP study (MPG); Manning, Clark, Hewitt, Khandelwal, Levy 2020 PNAS (emergent linguistic
structure from self-supervision); StructFormer (2020/2021, joint unsupervised dependency+
constituency induction via syntactic distance/height); ON-LSTM (ordered neurons) / PRPN (Shen et
al. 2018), cited as StructFormer's architectural lineage. **6 new distinct citation threads this
cycle.** **REUSED verbatim from `notes/brain_syntax_to_role_mechanism_and_forward_predictive_
encoder_spec_2026-07-30.md`** (not re-verified, already CITED@/ESTABLISHED-vs-CONTESTED tagged in
that note): Caramazza & Zurif 1976; Grodzinsky TDH; Friederici ELAN/LAN/P600; Bornkessel-
Schlesewsky eADM; Osterhout & Holcomb; Schrimpf 2021; Goldstein 2022; Caucheteux & King 2022.
**REUSED from `notes/research_learned_parser_clause_seg_np_head_blueprint_2026-07-18.md`**:
Ramshaw & Marcus 1995; Collins 1999; Vadas & Curran 2011; Diessel; Tomasello. All REASONED@
transfers (Part 1.2 synthesis connecting mention-detection to the existing PE-gate; Part 3's
earned-vs-supplied operational test) explicitly flagged as this cycle's novel synthesis, not
established fact, and are the primary driver of the P_deflated cap on Step 1.
