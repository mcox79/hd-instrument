# Brain mechanism: syntax->thematic-role assignment, and the forward-predictive/recurrent encoder spec (2026-07-30)

Scope: cited brain-mechanism account (Part 1) + build-ready encoder design spec (Part 2),
answering the measured wall in `exp_syntactic_role_agent_patient_voice_probe_v1` (74d4ea0c1):
frozen v2 MLM encoder cross-voice agent/patient probe = 0.18/0.16 (BELOW chance 0.50,
INVERTS on passives), within-voice = 0.90/0.85. Calibration per
[[feedback-lit-scan-calibration-penalty]]: P deflated 0.15-0.25, novel-synthesis capped
at 0.50, CITED@/REASONED@ tagged, ESTABLISHED/CONTESTED flagged per claim.

KB-check: `substrate_query.sh "syntactic role agent patient active passive voice
invariance encoder probe"` (already run by the probe cell's own author, top cosine=0.40,
no prior brain-mechanism synthesis on this exact question) — genuinely new drill, not a
rediscovery. Two parallel Sonnet lit-scans dispatched this cycle (thematic-role-assignment
mechanism; predictive-parsing-as-cortical-principle); synthesized below.

---

## HEADLINE

The measured failure (position-default, inverts on passive) is the textbook signature of
**Broca's-aphasia agrammatism** (Caramazza & Zurif 1976; Grodzinsky's Trace-Deletion
Hypothesis): a system that lost its structure-building/revision stage reverts to a
cheap "first-noun = agent" linear heuristic, producing systematic *reversal* on
non-canonical (passive) sentences rather than random noise — exactly what we measured.
The brain fixes this with a **staged, cue-integrating, incremental-commit-then-revise**
architecture (Friederici ELAN/LAN/P600; Bornkessel-Schlesewsky eADM), not a single
flat position->role mapping. Separately, the best-replicated brain-encoding evidence
(Schrimpf 2021 PNAS; Goldstein 2022 Nat.Neurosci.) shows **CAUSAL, next-token-predictive**
transformers — not bidirectional masked-LMs — are what best match human cortical
language processing. **This directly implicates our existing forward-predictive plan's
one unexamined choice**: `exp_encoder_latent_pc_arc_v1.py` is masked-SPAN, BIDIRECTIONAL
(I-JEPA-style, "non-causal attention... deliberate", per
`forward_predictive_second_encoder_build_plan_2026-07-30.md` line 76-90) — the same
non-incremental, no-time-asymmetry property the MLM encoder already had, and a real
candidate root cause for *why* the encoder is position-bound: it never has to commit to
a provisional parse and then revise it on a later disambiguating cue (the voice marker
"was ... by"), because it sees the whole sentence in one un-ordered pass. The evidence
this cycle argues for changing that one axis — masked-bidirectional -> causal
next-latent prediction, with a lightweight recurrent/stateful hold-then-revise layer on
top — while reusing every other already-designed piece (VICReg/EMA collapse guards,
OOM-safety via latent-only prediction heads, the three mandatory fixes for the two prior
cell deaths) verbatim.

---

## Part 1 — the brain mechanism (cited, established-vs-debated flagged)

### 1. Thematic role assignment against word order (Broca's / BA44-45)

1. **Caramazza & Zurif (1976)** — agrammatic Broca's aphasics comprehend
   semantically-constrained reversible sentences fine but fail specifically on
   *syntactically*-reversible non-canonical sentences (passives, object-relatives),
   consistent with a fallback "first-noun = agent" heuristic when syntax alone must
   carry the interpretation. **ESTABLISHED** (founding, replicated result).
2. **Grodzinsky (1986, 2000), Trace-Deletion Hypothesis (TDH)** — agrammatic aphasics
   delete the syntactic trace of a moved constituent (the passive object's trace), so
   the moved NP cannot receive its syntactically-assigned theta-role via movement; a
   default linear heuristic then assigns Agent to the first NP, producing **two
   competing Agent assignments** and hence *chance-level, not random*, performance
   specifically on passives/object-relatives, while actives stay well above chance.
   **ESTABLISHED core mechanism**; the universality of TDH across all agrammatic
   profiles and the exact distributional prediction are **CONTESTED** (mapping-hypothesis
   alternatives dispute the precise locus of the deficit).
3. **Friederici (2002, 2011)** — three-stage ERP model: **ELAN** (~150-200ms, automatic
   first-pass phrase-structure building), **LAN** (~300-500ms, morphosyntactic
   feature/case/agreement integration), **P600** (~500-800ms, later controlled
   structural integration/reanalysis, including thematic-role revision).
   Neuroanatomically: posterior **BA44** supports HIERARCHICAL structure-building
   (dorsal pathway, long-distance/movement dependencies); **BA44/45** supports
   thematic-role assignment; ventral pathway handles local/semantic combination.
   **ESTABLISHED** as the standard reference model; the strict "ELAN = universal,
   purely automatic" claim is **CONTESTED** (Steinhauer/Drury argue it is partly a
   word-category-violation design artifact).
4. **Bornkessel-Schlesewsky & Schlesewsky (2006, 2009), extended Argument Dependency
   Model (eADM)** — comprehension proceeds in phases: (i) constituent-structure
   building without relational interpretation; (ii) argument-role/prominence
   computation using a **cross-linguistically weighted set of cues** (case marking,
   animacy, verb voice/agreement, word order) — NOT linear position alone; (iii) later
   integration with plausibility/discourse. Languages weight these cues differently
   (case-marking languages downweight word order relative to English) — exactly why
   voice/word-order conflicts (passives) are diagnostic cross-linguistically.
   **ESTABLISHED as an influential cross-linguistic framework**; the specific
   "actor-centrality" primitive and exact cue-hierarchy are **CONTESTED/under active
   refinement**.
5. **Osterhout & Holcomb (1992, 1994)** — garden-path/reduced-relative sentences elicit
   a P600 at the disambiguating word when the initially favored (canonical/agent-first)
   parse must be revised. **ESTABLISHED**, one of the most replicated ERP findings in
   the field. **Jackson, Lorimor & van Hell (2020)** and a **pre-registered Indonesian
   replication (2021-22)**: passives elicit a left-anterior positivity (P600-family) at
   ~500-700ms relative to actives, indexing the extra structural/thematic-remapping
   cost. **CONTESTED/single-paradigm** at the specific-signature level (P600-for-syntax
   generally is textbook; this particular passive-vs-active waveform detail is less
   replicated).

**Synthesis (established, load-bearing for the design):** a feed-forward
bag-of-position-cues system that failed on passives would fail *unsystematically*.
The brain instead runs a **staged pipeline** — a cheap, early linear/canonical-order
default computed in parallel with or before costly hierarchical/movement-based
structure-building (BA44/45) — and when the costly stage is damaged (agrammatism) or
must be revised online (garden-path passives -> P600), the system **reverts to or
briefly stalls on the first-noun-agent default** rather than failing randomly. This
produces a *directional bias toward the canonical default*, exactly the measured
signature (0.16-0.18, systematically *inverted*, not merely chance-noisy at 0.50).

### 2. Incremental predictive parsing + revision — is forward-prediction THE cortical principle?

1. **Hale (2001); Levy (2008), surprisal theory** — processing difficulty proportional
   to -log P(word | context) under an incremental probabilistic grammar. **ESTABLISHED**:
   replicated across languages/corpora (Smith & Levy 2013, log-linear relationship over
   6 orders of magnitude; Wilcox et al., 11-language replication). Refinements
   (lossy-context surprisal, Futrell et al. 2020) are **CONTESTED** at the mechanism
   level but the core log-probability/RT relationship is one of the best-replicated
   findings in psycholinguistics.
2. **N400 (semantic fit) vs P600 (structural revision)** — **ESTABLISHED** functional
   dissociation; the *predict -> mismatch -> revise* cycle (garden path = a wrong
   high-probability linear-order parse, later corrected by disambiguating structure)
   is broadly accepted. Component-level computational interpretation (e.g. a distinct
   anterior post-N400-positivity vs posterior P600, reanalysis vs representation-update)
   is **CONTESTED**, actively argued.
3. **Schrimpf et al. 2021 PNAS** — transformer LMs best predict fMRI/ECoG brain
   responses during comprehension; predictivity correlates specifically with
   next-word-prediction task performance. **ESTABLISHED but with a live counter-read**:
   Antonello & Huth ("Predictive Coding or Just Feature Discovery?") argue the same
   brain-fit could reflect generic rich feature discovery, not prediction specifically
   — **CONTESTED interpretation, not contested data.**
   **Goldstein et al. 2022 Nat. Neurosci.** — direct ECoG evidence of continuous
   *pre-word-onset* next-word prediction in human cortex, with a measurable post-onset
   surprise signal matching model surprisal. **ESTABLISHED** (single strong
   electrophysiological study, replication ongoing).
   **Caucheteux & King 2022** (Communications Biology + Nature Human Behaviour) —
   transformer next-word-prediction reps only *partially* match brain data; adding
   **long-range/hierarchical forecasts** (not just adjacent next-token) improves the
   fit; the brain's predictions are **hierarchical and longer-range than single
   next-token**. **ESTABLISHED that prediction occurs; CONTESTED/nuanced that it is
   simple adjacent next-token prediction** — evidence favors multi-timescale,
   hierarchical forecasting (directly relevant to architecture choice below).
4. **Rao & Ballard (1999); Friston free-energy; Friston & Frith on language** — general
   predictive-coding cortical theory extended to dyadic communication. **CONTESTED as
   "the" dominant framework** — influential and increasingly mainstream, but competes
   with associative/Hebbian and structural/parsing-only accounts; a leading, not
   uniquely established, framework.
5. **THE CRUX FOR ARCHITECTURE — recurrence vs feedforward.** Direct evidence is
   **mixed/genuinely unresolved**: feedforward (non-recurrent) causal transformers
   trained purely on next-token prediction currently give the *best* brain-encoding
   fits found in the literature (Schrimpf 2021; Caucheteux & King) — prediction *as a
   training objective* does not strictly require a recurrent architecture to produce
   brain-relevant representations. But the brain is anatomically recurrent (feedback
   loops, working-memory maintenance across discourse), and the same Caucheteux & King
   long-range/hierarchical result plus general syntax-processing theory argue the
   brain's predictions are **stateful and multi-timescale** in a way a fixed-window
   feedforward pass does not naturally provide. **Net read (REASONED@ synthesis this
   cycle): the safest brain-faithful design choice is CAUSAL objective (well-supported,
   not falsified) + lightweight recurrence/state for maintaining an evolving
   within-sentence parse across the disambiguation point** — not full RNN-style
   recurrence over every token, which is not required by the cited evidence, but *some*
   persistent state that is updated (not merely recomputed) is what the P600
   revision-cycle and Caucheteux & King's hierarchical-forecast finding both point at.

### 3. Recurrent/stateful situation model (context, not re-derived this cycle)

Already covered by prior banked research (reused, not re-scanned): Kintsch
Construction-Integration, Zwaan/Bergen situation models, Zacks/Franklin/Gershman-Norman
Structured Event Memory (SEM) — comprehension = hold a maintained state, update it at
prediction-error spikes, not continuous blending (per
`notes/brain_foundational_confirmation_whole_architecture_2026-07-29.md`, already
VET'd PARTIAL/no-wrong-hill). **Relevant here**: the eADM's phase (iii)
("later integration with plausibility/discourse") and the P600 revision cycle are the
*same class of mechanism* as SEM's hold-then-replace-on-PE-spike, just operating at a
**smaller (within-sentence, token-to-clause) timescale** rather than the
across-clause/across-event timescale the existing bistable WM design already targets.
This is a genuine, reusable structural parallel (see Part 2, section (b)).

### 4. Binding (flagged as contested, already audited — not re-scanned this cycle)

Already covered and VET'd this session: `notes/brain_fidelity_audit_native_binding_
comprehension_2026-07-30.md` — FHRR/VSA synchrony-style binding is Marr-L2-plausible
but rests on a **CONTESTED** binding-by-synchrony hypothesis; mixed-selectivity/
conjunctive coding (Rigotti-Fusi) is a better-credentialed rival; ATL hub (Lambon-Ralph)
is a separate semantic-integration account. Not re-drilled here — this note's crux is
upstream of binding (READING roles off syntax), which the audit itself flagged as the
genuinely untested gap (section "HONEST GAP", `WHERE_WE_ARE_NOW.md` line 31).

---

## Part 2 — the encoder design spec (build-ready, glass-box, brain-faithful, honest)

### What already exists (reuse, do not re-derive)

Per direct read of `notes/forward_predictive_second_encoder_build_plan_2026-07-30.md`
and `experiments/exp_encoder_latent_pc_arc_v1.py`: a fully-authored, never-FULL-run
latent predictive-coding cell already exists with the collapse guards, OOM-safety, and
architecture this spec needs — **except one axis**. The existing cell is:
- masked-**SPAN** prediction (randomly placed context window around a masked span),
- **bidirectional** (non-causal) attention — same as the current MLM v2 encoder,
- EMA-target + stop-grad (BYOL/I-JEPA-style) + VICReg variance/covariance guards,
- a `d_model -> d_model` `LatentPredictor` head only (no `[B,L,vocab]` tensor anywhere
  — this is what makes it categorically immune to the OOM class that killed
  `exp_scale_meaning_learn_arc_heldout_v5_forwardpc.py`'s causal-LM full-vocab-logits
  path),
- and it has never completed a FULL run: it died in shared data-prep (silent hang,
  diagnosed as invisible-not-necessarily-dead, `forward_predictive_second_encoder_
  build_plan` section 2a) and its checkpointing was whole-seed not per-(seed,arm)
  (section 2c).

**This spec changes exactly ONE axis of that already-built cell** (masked-bidirectional
-> causal-incremental) and ADDS one small new component (a lightweight persistent-state
layer implementing the hold-then-revise cycle), while carrying forward every other
already-diagnosed fix verbatim.

### (a) FORWARD-PREDICTIVE OBJECTIVE: causal next-latent prediction, not masked-span bidirectional

**Change:** replace the existing cell's random-span masking + bidirectional attention
with: (1) a **causal attention mask** (each position attends only to positions <= itself
— literally flip `TinyTransformer`'s attention-mask construction from full to lower-
triangular, no other architecture change), (2) the masking target becomes **the next
contiguous span given only LEFT context** (predict latent at positions `[t, t+w)` from
context `[0, t)` only — a left-truncated version of the existing masking logic, not a
new masking mechanism), (3) keep the `LatentPredictor` head, EMA target, stop-grad,
VICReg guards **identical, unchanged** — this preserves the OOM-immunity and collapse-
avoidance machinery verbatim; only the attention mask and the span-selection rule change.

**Why (CITED@, this cycle's decisive addition over the existing plan):** Schrimpf 2021
and Goldstein 2022 (section 1.2 above) — the best brain-encoding-model fits in the
literature come from CAUSAL next-token-predictive transformers, not bidirectional
masked-LMs. The existing bidirectional LPC cell inherits the SAME time-symmetric,
no-incremental-commitment property the current MLM encoder has, which the syntax-role
mechanism account (Part 1.1) argues is exactly why passive sentences invert: a
bidirectional pass never has to provisionally commit to "first-noun = agent" and then
revise it upon reading "was ... by" — it just pools the whole sentence's context in one
un-ordered operation. A causal encoder is FORCED to make an early, revisable commitment
at the same point the brain does (before the disambiguating passive marker arrives),
which is the structural precondition for the P600-style revision mechanism in (b) to
have something to act on. **REASONED@ transfer, capped**: this connects two established
facts (brain-fit favors causal LMs; TDH/eADM show role assignment is staged/revisable)
into a design inference that has not itself been directly tested — flagged accordingly
in the P estimate below.

### (b) RECURRENCE/STATEFULNESS: hold-then-revise, not RNN-everywhere

**Do not build a full token-by-token RNN/SSM over the whole encoder** — the crux finding
in Part 1.2.5 is that causal-objective feedforward transformers already fit brain data
well; the evidence for *architectural* recurrence specifically is weaker than the
evidence for a *causal objective*. Instead, add the **minimum stateful component the
P600/TDH mechanism actually needs**: a small persistent "current role-hypothesis" state,
updated by a **prediction-error-gated hold-vs-revise rule** — structurally the SAME
primitive already built and VET-confirmed for the across-clause situation-model WM
(`hdlab/slot_attention_wm.py`'s per-slot PBWM gate; the bistable hold-then-replace-on-PE-
spike design in `notes/forward_predictive_objective_from_wm_state_design_2026-07-29.md`),
just instantiated at the **within-sentence, token-to-clause granularity** instead of the
across-clause granularity it was designed for:
- state `h_role` (small, e.g. one vector per tracked entity mention) is initialized from
  the cheap linear/canonical-order default (first-mentioned-NP = provisional-agent) —
  this is a DELIBERATE, brain-faithful design choice: the eADM/TDH literature says the
  canonical default is computed FIRST, not that it is wrong to compute — the wrongness
  is in FAILING TO REVISE it.
- at each subsequent token, a small gate compares the running causal-predictor's
  prediction error (from (a)) against a threshold; a spike (e.g. at the passive
  auxiliary "was" + past-participle + "by" sequence, which is a genuine local
  surprisal spike under any reasonable n-gram/transformer LM since "by NP" after a
  passive is a strong but not universal continuation) triggers a REPLACE (not blend)
  of `h_role`'s provisional assignment — reusing the already-implemented bistable gate
  logic verbatim (same threshold-vs-blend mechanism, smaller scope).
- this is genuinely NEW WIRING (the existing gate operates on clause-level slot state,
  not token-level role-hypothesis state) but reuses 100% of the gate mechanism's math —
  low build cost, not a new primitive.

**Brain-fidelity of this choice:** directly matches the P600-as-reanalysis literature
(Osterhout & Holcomb) and the SEM/EST hold-then-replace-on-PE-spike mechanism already
brain-validated for the across-clause case (`brain_foundational_confirmation_whole_
architecture_2026-07-29.md`) — this is the SAME organ operating one level down in
granularity, not a new hypothesis.

### (c) HIERARCHY/STRUCTURE: multi-horizon prediction, not single next-token

**Change:** add a second, cheap prediction head that predicts the latent of the **next
CLAUSE** (not just the next token/span) from the current causal state — i.e. combine
this spec's lever with the ALREADY-RANKED lever #2 in `encoder_representation_lever_
ranking_2026-07-29.md` (Hasson/Chung multi-timescale hierarchy) rather than treating
them as separate, competing levers. **Why (CITED@):** Caucheteux & King 2022 —
long-range/hierarchical forecasts (beyond adjacent next-token) measurably improve
brain-fit over single-next-token prediction alone; Friederici's BA44 hierarchy account
(Part 1.1.3) — thematic-role assignment specifically depends on HIERARCHICAL structure-
building, not local/linear adjacency, which a token-only predictive objective under-
represents relative to one that also predicts clause-level structure. This reuses the
`ForwardPredictor` head already designed in `forward_predictive_objective_from_wm_
state_design_2026-07-29.md` section 2 (predicts next-clause latent from slot state) —
**do not build a second head from scratch; wire the SAME clause-level predictor as a
second loss term on the causal token-level encoder from (a)**, at low marginal cost
(one more `d_model -> d_model` MLP + a smooth-L1/VICReg loss term, same shape/OOM-safety
class as the existing token-level predictor).

### (d) GLASS-BOX / no-borrowed-embedding / no-bolt-on-parser

No change to this axis from the existing plan: same `TinyTransformer` family
(architecture identical to MLM v2 and the existing LPC cell, only the attention mask
and masking-target rule change), trained from scratch on the same corpus, own tokenizer,
own BPE vocab — a causal-attention-mask change and a hold-then-revise gate are
architecture/objective decisions, not borrowed representations. The new gate reuses an
ALREADY-BUILT, ALREADY-audited own-mechanism primitive (`slot_attention_wm.py`'s PBWM
gate), not a bolt-on reader/parser (per the standing anti-pattern discipline) — it
operates on the encoder's own latents, not on any external parse.

### Practical: carrying forward the two death-fixes (mandatory, unchanged from the existing plan)

Both prior deaths were **data-prep and checkpointing bugs, unrelated to the objective
change above** — carry forward VERBATIM, do not re-derive:
1. **Data-prep silent hang** (`forward_predictive_second_encoder_build_plan` section
   2a): merge `count_pass`+`collect_pass` into one single-pass read, add heartbeat
   logging every 500k lines, add a time-bound data-prep-headroom smoke gate
   (`DATA_PREP_OK`/`DATA_PREP_TOO_SLOW`, ceiling 4h) that FAILS LOUD before FULL
   dispatch, cache the prepared bundle to disk keyed by corpus-mtime hash.
2. **CUDA OOM on full-vocab logits** (section 2b): this spec's causal predictor head
   remains `d_model -> d_model` ONLY (never `[B,L,vocab]`) — the same categorical
   immunity the existing bidirectional cell already has; ADD the same runtime shape
   assertion (`zp.shape[-1]==d_model`, no vocab-sized tensor in the loss path) as a
   regression tripwire, now covering the new causal training loop too.
3. **Per-arm checkpoint/resume** (section 2c): `(seed, arm)` unit-keyed via
   `tools/exp_checkpoint.py`, unchanged — now `arm in {ARM_LPC_CAUSAL, ARM_LPC_BIDIR
   (existing bidirectional cell, kept as a control), ARM_MLM (reuse V2 ckpt, no
   retrain), ARM_RANDOM}`.

### The fair test (reuses the ALREADY-BUILT probe cell verbatim, per its own ENCODER_ARM pattern)

`exp_syntactic_role_agent_patient_voice_probe_v1.py` (74d4ea0c1) already reads a
`FrozenV2Encoder`-shaped checkpoint (`state_dict`+`model_cfg`+`tokenizer_json`) via
`SyntaxRoleEncoder(base.FrozenV2Encoder)`. Per the exact reuse pattern the existing
plan already specifies for its own binding-comparison cell (section 3.1, "add a module-
level ENCODER_ARM selector... FrozenV2Encoder.__init__ already only depends on
state_dict/model_cfg/tokenizer_json"), add ONE new arm value pointing at this spec's
new checkpoint (`data/exp_encoder_latent_pc_arc_v1/ckpt_seed_<seed>_ARM_LPC_CAUSAL.pt`,
same save-format already specced in section 2d of the existing plan) — **zero new
loader code, zero new probe code**, only a path swap, exactly as the existing plan's own
`exp_binding_readcond_encoder_compare_v1.py` harness already does for the binding
question. Re-run the SAME closed-form nearest-centroid classification, SAME bands:

- **HARD-PASS** (pre-registered, cell's own bands, unchanged):
  `active_to_passive` AND `passive_to_active` cross-voice accuracy `>= ROLE_PROBE_
  PASS_MIN=0.70`, both directions, on HELDOUT_VERBS (never seen in training) — same
  cell, same construction, same digest/arms-must-differ checks.
- **HARD-FAIL** (pre-registered, cell's own bands, unchanged): either direction
  `<= ROLE_PROBE_FAIL_MAX=0.55` — i.e. no better than the already-measured
  position-only/chance band. Currently BOTH directions are at 0.16-0.18 (BELOW even
  this fail band, inverted) — any result landing back in `[0.35, 0.65]` (the shuffled-
  control band) without reaching 0.70 would be a PARTIAL (no longer inverted, but not
  yet reading true syntactic role), reportable as a distinct, informative middle
  outcome not covered by the cell's binary bands — flag this explicitly when reporting,
  do not force it into PASS or FAIL.
- Position-only/BoW/shuffled floors are UNCHANGED controls, already valid per the
  MEASURED metrics.json (0.50/0.33/0.51) — no re-derivation needed, they do not depend
  on which encoder is under test.

### Cost estimate

Carries forward the existing plan's GPU-hour anchor (MEASURED@ V2's own FULL training:
~2.83 GPU-hours/seed, same architecture size) — the causal-mask change and the two new
prediction heads (token-level causal + clause-level hierarchy) are cheap additions to
the SAME forward/backward pass, not a new model class. **Estimated total: ~15-19
GPU-hours** (2-4h shared data-prep, ~13-15h for 2 seeds x {ARM_LPC_CAUSAL,
ARM_LPC_BIDIR-control} trained arms at ~3.25-3.5h/run including the small extra
clause-head cost, ARM_MLM reused from V2's existing checkpoint at zero cost,
ARM_RANDOM free). The downstream fair-test re-run (probe cell, CPU, closed-form,
no training loop) is under a minute per encoder-arm — negligible. Per CLAUDE.md,
mandatory (seed, arm) unit checkpointing throughout (section above), so a preemption
loses at most one ~3.5h in-flight arm.

### Honest risk read

**Biggest risk (this cycle's calibration-capping factor):** the causal-attention change
HALVES available context per position (no right-context) — the existing MLM/LPC
encoder's own MES whole-sentence probe already showed random-init reps hitting 0.80
("reservoir-decodable", `WHERE_WE_ARE_NOW.md` line 21/24 — an UNTRAINED bidirectional
transformer's position-embedding+attention alone carries a lot of short-passage-order
signal); a causal encoder trained from scratch at our small scale (158M tokens, small
TinyTransformer) could plausibly UNDER-perform the bidirectional baseline on other
(non-role) representation-quality metrics even if it fixes the specific voice-invariant-
role signature — this would be a real, reportable trade-off, not a wash. **Second risk**:
the Antonello & Huth counter-read (Part 1.2.3) that brain-fit from causal LMs may
reflect generic rich-feature-discovery rather than prediction-specifically — if so, the
causal MASK change (which forces incremental commitment) may matter more than the
"prediction objective" framing per se, which is actually consistent with this spec's
own mechanism story (section (a)) but weakens the citation strength of "prediction is
the active ingredient" as opposed to "incremental-commitment-then-revision is the active
ingredient" — a distinction this experiment cannot itself disentangle (would need a
causal-BUT-not-predictive control, e.g. causal-masked reconstruction with a different
loss, to separate them; not in scope for this cell, flagged as a follow-up if the
HARD-PASS lands). **Third risk (soft floor, already established, `encoder_
representation_lever_ranking_2026-07-29.md` section 2):** at ~158M tokens the encoder
may simply lack enough data for ANY objective change to produce a hierarchical/
role-separable representation — a HARD-FAIL here would be genuinely ambiguous between
"causal+recurrent hypothesis wrong" and "right hypothesis, insufficient scale," and
should be reported as such, not collapsed to a clean refutation.

**P_deflated on HARD-PASS: 0.22.** Base REASONED@ confidence ~0.40 (two independently
well-established facts — brain-fit favors causal LMs; role-assignment is staged/
revisable — combine into a plausible, mechanistically-motivated design change that
directly targets the measured inversion signature) minus 0.18 lit-scan-calibration
penalty (uncharted transfer: no direct precedent tests "causal-vs-bidirectional latent
predictive coding on a voice-invariant thematic-role probe" — this is a novel
synthesis, not a replication of a published result) = 0.22, below the 0.50
novel-synthesis cap. **PARTIAL (lands in the [0.35,0.65] no-longer-inverted-but-not-
yet-passing band) assessed as more likely than HARD-PASS**, P~0.35 deflated,
consistent with the program's recurring soft-floor pattern (objective/architecture
levers land in a middle band on first attempt more often than they clear a hard bar).

---

## Cross-thread synthesis with prior entries

- Directly extends and CORRECTS ONE AXIS of `notes/forward_predictive_second_encoder_
  build_plan_2026-07-30.md` (bidirectional -> causal) while reusing 100% of its
  OOM-safety, collapse-guard, and checkpoint-fix machinery — not a competing plan, a
  targeted amendment with a specific new citation (Schrimpf/Goldstein/Caucheteux&King)
  the prior plan did not have.
- Reuses `encoder_representation_lever_ranking_2026-07-29.md` lever #1 (latent-PC) and
  lever #2 (multi-timescale hierarchy) TOGETHER rather than sequenced separately, per
  the Caucheteux & King hierarchical-forecast finding — this is a genuine combination
  the ranking note did not propose (it ranked them as independent, sequential levers).
- Reuses the bistable hold-then-replace PE-gate from
  `notes/forward_predictive_objective_from_wm_state_design_2026-07-29.md` /
  `hdlab/slot_attention_wm.py` at a NEW (smaller) granularity — same VET-confirmed
  organ (WM_PROVEN, commit 88d050955), new wiring point, not a new mechanism claim.
- Confirms and sharpens `WHERE_WE_ARE_NOW.md`'s own framing (line 51): "the
  forward-predictive/recurrent encoder pivot is earned... precisely-scoped for the
  READING/PARSING capability" — this note supplies the specific CITED reason the
  existing bidirectional LPC plan is not yet the right instantiation of that pivot for
  THIS specific target, and the specific minimal fix.

## Substrate-product implications

A voice-invariant thematic-role-reading capability, if it clears even the PARTIAL band,
directly unblocks the "honest gap" already named in `WHERE_WE_ARE_NOW.md` (line 31):
syntactic role assignment without an explicit role word — the genuine reading/parsing
capability distinguishing "the substrate can slot-fill when told who the agent is" from
"the substrate can figure out who the agent is from grammar alone," which is the
product-relevant difference between a templated-composition demo and a real
comprehension capability. This is a from-scratch, glass-box, no-external-LLM-at-
inference capability (per the standing invariant) — no borrowed embeddings, no bolt-on
parser; the causal-mask change and the reused PE-gate are both native, own-mechanism
architecture decisions.

## Anchor candidates for pickup (ranked, no inline experiment design — exp_dev owns the pre-reg)

1. **PRIMARY — causal-mask amendment to `experiments/exp_encoder_latent_pc_arc_v1.py`
   + new fair-test arm on `exp_syntactic_role_agent_patient_voice_probe_v1.py`.**
   Change attention mask non-causal->causal + masking target to left-truncated
   next-span (Part 2(a) above); add the clause-level predictor head (Part 2(c));
   carry forward the three mandatory fixes from `forward_predictive_second_encoder_
   build_plan_2026-07-30.md` sections 2a/2b/2c verbatim (data-prep single-pass merge +
   heartbeat + time-bound smoke gate; OOM-tripwire shape assertion; (seed,arm)-unit
   checkpointing). Tier: GPU FULL, ~15-19 GPU-hours, gated behind the data-prep-
   headroom smoke before dispatch. Why now: the fair test is already built and
   MEASURED at the wall (0.16-0.18) — cheapest already-existing lever to re-test via a
   path-swap once the new checkpoint exists (`ENCODER_ARM` selector pattern, zero new
   probe code).
2. **SECONDARY — bundle a bidirectional-vs-causal control arm into the same dispatch.**
   Train both the new `ARM_LPC_CAUSAL` and the existing `ARM_LPC` (bidirectional) at
   matched budget in the same run, isolating causal-vs-predictive-objective-alone
   (resolves the Antonello & Huth counter-read risk, Part 2 "Honest risk read").
   Near-zero marginal cost over #1 (same data-prep, same (seed,arm) matrix).
3. **TERTIARY (only if #1 lands PASS/PARTIAL) — extend `exp_binding_readcond_
   encoder_compare_v1.py`** (already speced, not yet built, in
   `forward_predictive_second_encoder_build_plan_2026-07-30.md` section 3) with the
   new causal checkpoint, to check whether one encoder fixes both the syntax->role
   reading gap and the separate binding-readability gap. CPU-only, cheap, sequence
   AFTER #1's verdict.

Context pointers for pickup: `experiments/exp_syntactic_role_agent_patient_voice_
probe_v1.py` + its metrics.json; `experiments/exp_encoder_latent_pc_arc_v1.py`;
`notes/forward_predictive_second_encoder_build_plan_2026-07-30.md`;
`notes/encoder_representation_lever_ranking_2026-07-29.md`;
`notes/forward_predictive_objective_from_wm_state_design_2026-07-29.md`;
`hdlab/slot_attention_wm.py`; `notes/WHERE_WE_ARE_NOW.md` ("THE ENCODER WALL" section).

## Citations (verified count)

CITED@ this cycle (2 parallel lit-scans, generic-term WebSearch, query-privacy
compliant): Caramazza & Zurif 1976; Grodzinsky 1986/2000 (TDH); Friederici 2002/2011
(ELAN/LAN/P600, BA44/45); Bornkessel-Schlesewsky & Schlesewsky 2006/2009 (eADM);
Osterhout & Holcomb 1992/1994; Jackson/Lorimor/van Hell 2020 + Indonesian pre-registered
replication 2021-22; Hale 2001; Levy 2008; Smith & Levy 2013; Wilcox et al. (11-language
surprisal replication); Schrimpf et al. 2021 PNAS; Antonello & Huth (counter-read);
Goldstein et al. 2022 Nat. Neurosci.; Caucheteux & King 2022 (Communications Biology +
Nature Human Behaviour); Rao & Ballard 1999; Friston (free-energy); Friston & Frith.
Carried verbatim from prior notes (not re-verified this cycle, already CITED@ in their
originating notes): Rao & Ballard 1999 / Friston 2005 (duplicate anchor, same citation);
LeCun 2022; Assran et al. 2023 (I-JEPA); Bardes et al. 2024 (V-JEPA2); Chen & He 2021
(SimSiam); Bardes et al. 2022 (VICReg); Hasson (temporal-receptive-window hierarchy);
Chung et al. 2017 (HM-RNN). **Verified citation count this cycle: 18 new anchors from
2 lit-scans (14 distinct authors/works across thematic-role and predictive-parsing
threads, some with multiple co-cited papers) + 8 carried/reconfirmed anchors from the
2 prior 2026-07-29/07-30 design notes.** ESTABLISHED/CONTESTED flags applied per-claim
throughout Part 1; no claim in Part 2 is asserted as settled fact — all are tagged
CITED@ (for the underlying brain finding) or REASONED@ (for the transfer to this
encoder design), with the REASONED@ transfer explicitly identified as the single
weakest link and the primary driver of the P_deflated cap.
