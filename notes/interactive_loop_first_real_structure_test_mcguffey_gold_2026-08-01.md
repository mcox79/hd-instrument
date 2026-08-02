# Interactive loop: cheapest FIRST REAL-STRUCTURE test on McGuffey gold (2026-08-01)

Director build-ready spec. Extends the VALIDATED synthetic interactive-loop probe
(`exp_interactive_extraction_situation_model_loop_probe1_v1`, MIDDLE_PARTIAL, floor held,
interactive lifted passives 0.15->0.55 specifically, placebo clean, commit ba01892e9) to REAL
non-canonical constructions where a feed-forward linear-order baseline PROVABLY fails. CPU-minutes,
no trained encoder, no GPU, no scale. This is fork-(b)'s measurement-first FIRST real step; the
GPU/scale build awaits USER steer.

Calibration: CITED@ = underlying brain/linguistic finding; REASONED@ = transfer to this design.
ESTABLISHED/CONTESTED per brain claim. P deflated; novel-synthesis capped 0.50.

KB-check: queryable index stale + heavy `director_kb_query`/`substrate_query` returned empty this
cycle (box-thrash, coordinator killed the heavy queries); grounding = direct read of the gold
files, the probe1 cell, `hdlab/pos_tagger.py`, and the 2026-08-01 design note (commit 06a8353fb).
No prior note designs a real-gold test of this loop -- this is the new content; the loop mechanism
+ probe1 harness are prior art, reused.

---

## THE DATA (read off disk this cycle -- SMALL, this drives the whole design)
- `data/eval_gold_mention_role_mcguffey_v1/gold_quotative_verified_v1.jsonl`: **20** sentences,
  **19 parser-WRONG** (the hard cases). Fields: `text`, `speech_verb`, `gold_agent_speaker`,
  `gold_addressee`, `parser_agent_was`, `parser_correct`. Signature: postposed speaker
  ("...?" said James -> agent=James; Kate=vocative/addressee, NOT agent). Parser picked the
  vocative/first-noun => 95% wrong on these exact cases (MEASURED@, `parser_correct` field).
- `data/eval_gold_mention_role_mcguffey_v1/gold_passive_verified_v1.jsonl`: **7** sentences,
  **6 parser-WRONG**. Fields: `passive_verb`, `gold_patient_surface_subj`, `gold_agent`(usually
  null/implicit). Signature: "He is called Dodger" -> He=PATIENT, agent implicit. Parser called the
  surface subject the AGENT => wrong (MEASURED@).
- **N=27 verified gold total (25 hard). This is the single most important design fact.** It forces
  leave-one-out CV, low-capacity learning, and a pooled mechanism -- and it is the weakest link
  (below). Optional N-boost (exp_dev's call, not required): the same dir has `gold_PP`,
  `gold_relative`, `gold_referent` verified files (more non-canonical constructions) that could
  enrich the SHARED marker-overrides-order training signal; scope here is the two named files.

---

## THE CHEAP ENCODING (glass-box, our-own-mechanism, NO borrowed embedding)
Per token, a feature vector assembled ONLY from things we already own. Each element flagged
brain-grounded / structure-supplied / engineering:

1. **POS tag** -- `hdlab/pos_tagger.py::PosTagger.tag(tokens) -> [tag,...]`; small learned tag
   embedding (or one-hot->proj). *Flag:* POS categories are linguistically real, but the tagger is
   a supervised learned component of OURS -- "supplied STRUCTURE" (glass-box), not a brain mechanism
   and not a borrowed semantic embedding. **Noise source:** trained on PTB, applied to 1800s
   McGuffey prose -> domain shift; report the tagger's tag-accuracy on the gold as a diagnostic.
2. **Linear position** -- normalized index + a fixed random positional FHRR code. *This is the cue
   the OFF baseline latches onto.* Structure-supplied.
3. **Quote membership / boundary** -- is-token-inside-quotes; is-token-immediately-after-a-closing-
   quote. Detected from quote chars in the raw text. *Flag:* orthographic -- a WRITING convention,
   NOT a cue the brain uses for speech; it is a glass-box SURFACE PROXY for the discourse/prosodic
   speaker-change cue the brain actually uses. Engineering proxy, flagged honestly.
4. **Verb adjacency** -- distance to nearest verb (POS VB*/VBD/VBZ/VBN); immediately-follows-a-verb
   flag. Structure-supplied (the quotative-inversion postposed-subject signature is structural).
5. **Passive-context** -- be-aux (POS + closed-class be-forms is/are/was/were) + following VBN;
   presence of "by" (closed-class IN). Structure-supplied (closed-class, construction-agnostic).
6. **Lexical identity** -- random FHRR id per token-TYPE (seeded hash of lowercased token ->
   random unit vector). IDENTITY ONLY, no semantics. Own-mechanism. Held-out entities get fresh ids
   so "James=agent" cannot be memorized.
7. **Mention flag** -- candidate entity mention = POS in {NNP, PRP, NN-head}; identifies the
   role-filler candidates the role decision ranges over.

**CRITICAL HONESTY CONSTRAINT (the line, per slot_attention_wm docstring):** we SUPPLY the features
(1-7 = structure, allowed). We do NOT supply the construction->role MAPPING -- that is LEARNED by a
low-capacity top-down MLP. Hand-coding "speech-verb -> postposed-NNP = agent" would be a bolt-on
parser rule (forbidden) AND would cheat the floor. exp_dev must LEARN the mapping, and the placebo +
weight inspection must confirm it is learned, not hardcoded.

---

## THE PROBE (one variable, can-fail, reuse probe1 harness)

**Two sub-tasks, ONE shared loop mechanism** (top-down construction expectation biases the role
decision against linear order):
- QUOTATIVE: select which mention = agent/speaker (softmax over mentions). Gold = `gold_agent_speaker`.
- PASSIVE: classify the surface-subject's role (agent vs patient). Gold = patient (surface subj).

**ONE VARIABLE: interactive top-down feedback ON vs OFF** (identical features, identical LOOCV,
identical harness):
- **ARM_OFF (feed-forward, linear-order baseline):** role decision consumes ONLY position + mention
  flag (features 2,7); agent = first/subject-position mention. NO construction-marker consumption,
  NO top-down feedback. This is the ~ parser we KNOW is 95%/86% wrong.
- **ARM_ON (interactive):** adds the top-down predictor `p_td = g(construction_features)` (learned
  low-capacity MLP over features 1,3,4,5) that biases the mention/role decision, reusing probe1's
  `logits = tok . role_query + gain * (tok . p_td)` form + the graded-PE / precision machinery.

**LEARNING:** pool both constructions (N=27) so the SHARED "markers override linear order" signal
has the most examples; evaluate per-construction. **Leave-One-Out CV** (no sentence overlap; N=27
folds), low-capacity `g` (few params) to resist overfit. Deterministic folds.

**PRE-REGISTERED BANDS** (evaluated on the HARD subset, `parser_correct=false`; already-correct
cases reported separately, must-not-regress >= 0.80):
- **CAN-FAIL FLOOR (must hold or encoding is too generous -> fix it):** ARM_OFF quotative agent-acc
  <= **0.15** AND ARM_OFF passive patient-acc <= **0.15**. We KNOW these hold (parser 95%/86% wrong);
  if OFF does NOT fail, a feature is leaking the answer -- STOP and remove it.
- **HARD-PASS (ARM_ON, held-out LOOCV):** quotative agent-acc >= **0.60** AND >= floor+0.40;
  passive patient-acc >= **0.55** AND >= floor+0.35 (lower bar -- N=7 underpowered); lift
  CONCENTRATED on the inverted cases; already-correct cases not regressed.
- **MIDDLE/PARTIAL:** ARM_ON in (floor+0.15, HARD-PASS) -> no longer inverted, not yet reading role;
  distinct informative outcome, do NOT force into PASS/FAIL.
- **HARD-FAIL:** ARM_ON <= floor+0.10 -> top-down feedback did not resolve the real construction.

**CONTROLS:**
- **RANDOM-FEEDBACK placebo (CRITICAL):** ARM_ON wiring intact but the construction features feeding
  `g` are SHUFFLED across sentences (verb-class permuted). MUST NOT help (stays ~floor). Proves it
  is the real construction CONTENT, not merely having a feedback connection. If placebo helps ~as
  much as true -> artifact, HARD-FAIL the claim.
- **NO-TOPDOWN control:** ARM_ON architecture with `p_td` zeroed -> must equal OFF floor (sanity).
- **Glass-box inspection dump (per sentence):** detected construction, `p_td` expectation, per-
  mention scores, chosen agent/patient, gold, and which feature drove the choice. Inspectable.

---

## COST
CPU-minutes. N=27, LOOCV (27 folds x tiny MLP x few epochs), `pos_tagger.tag` is fast. Well under
~5 CPU-min all arms. Reuse `exp_interactive_extraction_situation_model_loop_probe1_v1.py`: swap the
synthetic oracle task-gen for real-gold feature extraction; keep the ARM_OFF/ARM_ON/placebo scaffold,
`decide_verdict`, per-(arm,seed/fold)-unit checkpoint (`tools/exp_checkpoint.py`), atomic
`os.replace`, `_arms_must_differ` self-test. Do NOT rebuild.

---

## SINGLE WEAKEST LINK: DATA-THINNESS (N=27; passive N=7)
Severe and honest. Three compounding failure modes, each pre-registered so a null is interpreted
correctly (per flat-learning-is-broken-experiment discipline -- a null here means too-few-examples,
NOT mechanism-refuted):
1. **Underpowered learning.** Learning a GENERALIZING top-down feedback from ~20-27 examples with
   held-out generalization is thin; passive N=7 is near-anecdotal. A HARD-FAIL is ambiguous between
   "mechanism wrong" and "insufficient gold" -- report as such; the fix is MORE VERIFIED GOLD, not
   abandoning the loop. Treat quotative (N=20) as primary, passive (N=7) as exploratory.
2. **Honesty knife-edge (bolt-on temptation).** The encoding MUST supply construction-agnostic
   structural features and LEARN the role mapping. If exp_dev hand-codes the construction->role rule,
   the probe becomes a bolt-on parser that trivially "passes" and cheats the floor -- proving nothing.
   Guard: `g` is a learned low-capacity MLP; the placebo (shuffled construction -> no help) + weight
   inspection must confirm the mapping is learned, not hardcoded.
3. **Feature noise from tagger domain shift.** `pos_tagger` (PTB-trained) on 1800s McGuffey prose
   injects label noise into the very features the mechanism depends on -- could suppress the lift.
   Report tagger tag-accuracy on the gold as a diagnostic; a suppressed lift under bad tags is a
   feature-quality problem, not a mechanism refutation.

## WAYS THE ENCODING COULD CHEAT THE FLOOR (flag + guard, per coordinator ask)
- (a) A feature that directly encodes the target role (an `is_speaker`/`is_patient` flag, or the
  gold-derived construction label as input) -> ON (or even OFF) trivially wins. GUARD: features are
  surface/POS/position/quote/identity ONLY; the ROLE mapping is learned, never a feature.
- (b) OFF baseline given construction markers + capacity could learn to use them and NOT fail.
  GUARD: OFF consumes ONLY position + mention flag; construction markers are consumed ONLY by the
  top-down path that ON adds.
- (c) Train/test leakage under tiny N (same sentence or same speaker in both). GUARD: LOOCV (no
  sentence overlap) + fresh FHRR id for held-out entities so it is STRUCTURAL generalization, not
  lexical memorization.
- (d) Hand-coded rule masquerading as learned -> see weakest-link #2; caught by placebo + inspection.

## NOT-CLEANLY-BRAIN-GROUNDED (honest)
- POS-tags-as-features: linguistically real category, but a supervised learned tagger, not a brain
  mechanism ("supplied structure, glass-box").
- Quote-boundary feature: orthographic writing convention, NOT a brain cue for speech -- a glass-box
  SURFACE PROXY for the discourse/prosodic speaker-change signal the brain uses. Engineering.
- The construction->role readout MLP: a learned readout consistent with the loop; the brain-grounded
  part is the TOPOLOGY (top-down construction expectation biases extraction), same "brain-grounded
  PRINCIPLE, substrate-native OPERATION" caveat as the design note. "Brain-foundational" applies to
  the architecture/topology, not every op inside it.

## P_DEFLATED
**P_deflated (full pattern: floor holds + ARM_ON HARD-PASS held-out on BOTH constructions + placebo
clean): 0.25.** The floor holding is ~certain (measured 95%/86% wrong). The mechanism resolving REAL
constructions is plausible (it worked on synthetic: 0.15->0.55), but on N=27 real gold with tagger
noise and a genuinely-learned (not oracle) construction signal, held-out generalization on BOTH
constructions is a hard, underpowered ask -- MIDDLE_PARTIAL is the more likely outcome (P~0.40),
consistent with the synthetic result and the program's recurring first-attempt middle-band pattern.
Quotative-alone HARD-PASS is higher (~0.35, N=20); passive-alone is the drag (N=7).

## RECOMMENDED NEXT ACTION
Hand to `hdi_exp_dev` to build as `exp_interactive_loop_real_gold_mcguffey_v1` (Tier-1 CPU, reuse
probe1 harness). VET the CAN-FAIL floor + the placebo BEFORE trusting any HARD-PASS. Report
quotative and passive separately + the tagger-accuracy diagnostic. Verdict to USER before any
real-text/GPU scale step.
