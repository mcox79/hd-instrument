# Brain mechanism + design — glass-box verb-sense / frame disambiguator

**Solver session, 2026-08-28.** How the brain disambiguates verb sense, why the two landed negatives
missed it, and the mechanism I build. This is my scratch design; the deliverable is `SOLVED.md`.

## 1. How the brain does this (PINNED computation)

Verb-sense selection in the brain is **reordered lexical access + argument-structure construction + thematic
fit, combined as a graded cue competition** — NOT a fixed verb→sense lookup, and NOT fine-grained WordNet WSD.

1. **Frequency-ordered access = the PRIOR (Duffy, Morris & Rayner 1988 "reordered access"; Twilley & Dixon).**
   The dominant sense is retrieved first; context can reorder. Neurally the graded lexical-semantic activation
   (left mid/posterior MTG; N400 as the retrieval index, Lau/Phillips/Poeppel 2008). This IS the MFS prior.
2. **Argument-structure CONSTRUCTION = the near-CATEGORICAL constraint (Goldberg construction grammar; Levin
   1993 diathesis alternations).** The realized syntactic frame — read by the frontotemporal argument-structure
   network (LIFG/BA44-45 for frame, pSTS/MTG for role assignment) — activates the construction whose event
   semantics fit. A that-clause complement forces a communication/cognition sense; a Path/Goal satellite forces
   motion; a physical-Theme direct object forces deposit/transfer. This constraint is **categorical** where it
   fires — and it is exactly the signal the prior cells omitted.
3. **Selectional preference / thematic fit = the GRADED cue (McRae, Ferretti; Bicknell et al. 2010).** The
   argument's semantic TYPE (place / physical-object / proposition / animate / time) graded-matches the sense's
   selectional restriction. ATL hub supplies the type; thematic fit modulates N400.
4. **Cue combination = graded competition (MacDonald/Pearlmutter/Seidenberg 1994; McClelland 2013).** Additive
   cue activation `A_i = sum_c w_c * support_c(i)` → softmax **IS** the FLMP/Bayesian posterior for discrete cue
   integration. When the frame cue is diagnostic + high-reliability it dominates the prior; when the frame is
   neutral the reader stays at the prior = MFS = **underspecification** (Frazier & Rayner 1990: readers do NOT
   commit to a sense unless the context/frame forces it).

**COPY:** `sense = argmax_s softmax[ w_prior·prior(s) + w_frame·frame_support(realized_frame, s)
+ w_fit·thematic_fit(arg_types, s) ]`, in the substrate's `graded_competition` currency.
**SWEEP (OUR-INVENTION-UNDER-TEST):** the cue weights, the frame feature set, the coarse-sense granularity.
**NOT brain-faithful (barred):** fixed verb→sense lookup; a manner-verb whitelist (the ToM solver proved the
whitelist is the implementation trap).

## 2. Why the two landed negatives missed it (reconciliation — disk-read, not summary)

- `exp_entity_typing_selectional_wsd_v1` (real SemCor, HARD_FAIL, +0.0012, McNemar p=0.81): used **only** a
  *learned* thematic-fit feature — `log P(object-supersense | sense)` over the nearest following noun — predicting
  **fine WordNet senses** across **all** polysemous verbs. It **omitted the syntactic-frame construction cue
  entirely** (no ccomp / particle / theme-DO-presence), and diluted the frame-diagnostic verbs into a fine-sense
  population where MFS is unbeatable (base fine-sense 0.5546; base **coarse** lexname already 0.7600, so the
  object-typing feature had almost nothing left to add at either grain: +0.0089 coarse). **The categorical frame
  cue is the missing signal.**
- `exp_wsd_frame_selectional_gate_v1` (toy, MIDDLE_BAND, scramble-fragile): had the right glass-box frame reading
  but only **31 hand-authored** items → underpowered, and on 31 items a random vn-class→signature permutation
  reproduces the gain (scramble-fragile). Never touched a real WSD gold.
- Every OTHER landed negative on a real gold (`context_conditioned` v1/v2, `learned_context`, `context_override`,
  `reader_bayesian_hub`, `reliability_weighted`, `sense_structured_hub`) used **distributional / learned /
  Bayesian-context** mechanisms — NOT glass-box frame-over-parse. `context_override` even *works* distributionally
  on subordinate SemCor but ties MFS on WiC human gold.

**The gap I fill:** the categorical **syntactic-frame construction cue read off the dependency parse**, combined
with the prior + thematic fit via `graded_competition`, predicting a **coarse event-frame** (what the brain
represents and what downstream consumes), on an **adequately-powered real gold**, restricted by a **principled**
frame-alternating-verb criterion fixed in advance (not by peeking at labels).

## 3. Mechanism I build (`experiments/frame_sense_disambiguator.py`)

Glass-box, spaCy `en_core_web_sm` dependency parse (no LLM at inference — the invariant). For a target verb token:
- **Read the realized frame:** has_dobj + dobj semantic type (place/physical-obj/proposition/animate/abstract,
  via WordNet lexname/hypernyms — reuse the location_register place-typing), has_ccomp / that-clause, has_quote,
  verb particle (away/out/back/up), prep+pobj Goal/Source/Recipient type, is_intransitive, subject type (time/animate).
- **Coarse sense inventory** (the two dominant confusions + a small principled set): MOTION, TRANSFER/DEPOSIT,
  COMMUNICATION, PERCEPTION, COGNITION, CHANGE_OF_STATE, STATIVE/ELAPSE.
- **Score each candidate sense** via `graded_competition.net_activation` → softmax: prior cue (MFS) + frame cue
  (near-categorical support) + thematic-fit cue (graded). argmax = sense.
- **Info-free twin:** shuffle the frame features (or randomize the frame→sense support) → collapses to the prior.

## 4. Validation plan (bar §7)

- **GOLD 1 — beats MFS on a real WSD gold:** SemCor, coarse event-frame (WordNet verb lexname → coarse class),
  on frame-alternating verbs selected by a fixed lexicon criterion; MFS-over-coarse recomputed on that population;
  report full AND diagnostic-subpop (gate decided blind by the mechanism); info-free twin; CI half-width + null p95.
- **GOLD 2 — corroborating human gold:** WiC verb subset, predict "same sense iff same coarse frame"; floor =
  majority-class (balanced ~0.5) + always-same / always-different. Human-judged → sidesteps WordNet granularity.
- **POSITIVE CONTROL:** context-flipped minimal pairs (left room/left note; observed swap/observed that; returned
  home/returned reply; passed away/hour passed). MFS gives the SAME sense to both members; the disambiguator flips.
- **DOWNSTREAM LIFT (mandatory, shared-primitive proof):** feed into the ToM motion cue / mined-event precision on
  real intact LitBank passages; suppress the departure reading when "left"/"returned" is deposit/speech →
  precision rises CI-separated vs the un-disambiguated path.

A rigorous NEGATIVE is a full pass (brief §7): if frame-selection ties MFS on the broad gold but the two-confusion
disambiguator still lifts the downstream cue, the downstream lift alone passes.
