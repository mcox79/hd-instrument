---
problem: upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_posterior
status: PARTIAL
bar: "PASS = a likelihood-trained (CRF-objective) POS tagger with a CALIBRATED posterior — and (the target) a JOINT-DECODED tagger-parser — landed glass-box (NO external LLM at inference; a persisted static model is admissible), that lifts 19c predicate/verb recall PAST 0.806 toward the competent-reader ceiling CI-separated AND improves at least one parser-downstream consumer (who-did-what or PP-attachment) CI-separated over its current live floor, with an info-free twin LOSING and the runtime-dependency story resolved. Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE — the joint decode cannot push 19c past 0.806 within a register-robust budget, with the named cause + number (e.g. the parser's own OOD ceiling) — is a FULL PASS."
result: "LOCATED NEGATIVE on the JOINT DECODE (axis-3) + a hardened, dependency-resolved DEPLOYABLE WIN on the calibrated posterior (axis-1). (1) The likelihood-trained CRF CALIBRATED POSTERIOR alone separates 19c dropped verbs at AUROC 0.9409 (n_drops=55, n_cand=10703) / recovery 0.8727 @ FP<=0.5 (19c LitBank transfer), CI-separated over the info-free twin (delta +0.747), MODERN 0.931 — the axis-1 fix, reproduced. (2) JOINT PARSE-DECODE (axis-3) DOES NOT PUSH PAST IT: adding the force-VERB parse-coherence cue lifts AUROC by +0.0017 with a REGISTER-ROBUST delexicalized parser (recovery 0.8727 @FP<=0.5 = a NO-OP vs CRF-alone) and by +0.0012 with the modern LEXICAL parser (which HURTS the operating point: 0.800). The delexicalized coherence IS the better structural cue (AUROC 0.6184 vs lexical 0.5901 — the parser's register-brittleness is real) but IMMATERIAL because the calibrated posterior already captures the separable signal (AUROC 0.94). (3) PARSER DOWNSTREAM (payoff-2) IS REAL but the lever is the calibrated posterior + PRECISION-GUARDED recovery, NOT the joint decode: on the genuine-drop subpopulation (n=55), recovering the dropped verb lifts who-did-what REACHABILITY +0.3091 CI[0.182,0.455] over base (0.491->0.800) and +0.3636 CI[0.236,0.509] over the info-free random-correction twin, and who-did-what accuracy +0.236; BUT feeding recovered tags at the modern threshold FLOODS the parse (6576 corrections / 3015 records) and COLLAPSES full-pop reachability 0.698->0.497. (4) The residual is a PARSER/TAGGER-FIDELITY gap, not a meaning ceiling: spaCy (offline competent-reader oracle) recovers 0.818 of the drops / 0.881 of in-vocab drops. (5) DEPENDENCY STORY RESOLVED: the CRF posterior is reimplemented GLASS-BOX in pure numpy (linear-chain forward-backward), reproducing sklearn_crfsuite.predict_marginals to max|dP(VERB)|=7.3e-7 (Viterbi tags 100%), so it ships as a dependency-free static json asset — NO crfsuite runtime dep."
floor: "For the JOINT-DECODE question the strongest floor actually run is the CRF-alone calibrated posterior (CRF_POST): recovery 0.8727 @FP<=0.5 on 19c-transfer (AUROC 0.9409); the joint-decode arms tie (delex 0.8727) or lose (lexical 0.800). For the calibrated-posterior-vs-perceptron question the floor is the perceptron max-margin margin (0.582 on 19c drops, parent SS4c). For payoff-2 the floor is base reachability on the genuine-drop subpopulation (lexical parser + committed perceptron tags) = 0.4909, and the info-free random-correction twin = 0.4364 (does NOT lift, -0.0545 vs base)."
controls: "(1) INFO-FREE TWIN payoff-1 (random-verbhood promotion at matched rate) LOSES CI-separated for the calibrated posterior (delta +0.747). (2) INFO-FREE TWIN payoff-2 (force ONE RANDOM gate-eligible token->VERB, same #corrections, wrong token) does NOT lift reachability (twin-base -0.0545 CI[-0.127,0.0] not-sep) and oracle-recovery beats it +0.3636 CI[0.236,0.509] -> the downstream gain is real verb-recovery signal, not a distractor-VERB artifact. (3) AUROC DECOMPOSITION (CRF posterior vs each parse-coherence cue, n_cand=10703) isolates that structure adds ~nothing over the calibrated posterior (delta +0.0017 delex / +0.0012 lexical). (4) LEXICAL-vs-DELEX parser (one variable = word-identity features): the register-robust delex coherence separates better (AUROC 0.618>0.590) — register-brittleness is real — yet immaterial. (5) spaCy OFFLINE ORACLE (reference-only, never at inference): recovers 0.818/0.881 of drops -> the residual is a fidelity gap, NOT a meaning ceiling. (6) MODERN UAS RETENTION: delex parser loses 8 UAS in-domain (0.842->0.762) — quantifies the delexicalization cost and why it is not free. (7) FULL-POP FLOODING vs SUBPOP PRECISION-GUARDED isolates that payoff-2's full-pop collapse (0.698->0.497) is a detector-PRECISION artifact (6576 forced VERBs), not a limit of verb recovery. (8) GLASS-BOX CRF vs crfsuite (max|dP(VERB)|=7.3e-7) verifies the dependency-free asset is byte-faithful."
files_changed: "experiments/exp_joint_decode_register_robust_tagger_parser_v1.py (the delexicalized register-robust parser + both payoff arms), experiments/exp_joint_decode_residual_decomposition_v1.py (AUROC decomposition + spaCy oracle + OOV split), experiments/exp_joint_decode_downstream_bestshot_v1.py (payoff-2 oracle recovery + twin on the drop subpopulation), experiments/exp_crf_glassbox_marginals_v1.py (pure-numpy CRF forward-backward = the dependency resolution), verification/test_joint_decode_register_robust.py (scaffold-free witness, 5/5), data/exp_crf_glassbox_marginals_v1/crf_tagger_glassbox.json (the deployable dependency-free calibrated-posterior asset), data/exp_joint_decode_register_robust_tagger_parser_v1/{metrics.json, arceager_delex_ud_ewt.npz} (NO hdlab file changed — proposed diff below, strategy lands it per Q111)."
reverify: ".venv/Scripts/python.exe verification/test_joint_decode_register_robust.py"
---

# PARTIAL — the JOINT DECODE (axis-3) is a located negative; the CALIBRATED POSTERIOR (axis-1) is the lever, and it is now dependency-free and delivers both payoffs under precision-guarded recovery

**Status: PARTIAL (WIP until `owner_verdict: DONE`).** No `hdlab/` file changed — mechanism proven in `experiments/` +
`verification/`; the exact `hdlab/` diff is proposed in §6; strategy lands it (Q111, default-off, witnessed).

**The one-line answer.** The brief's proposed mechanism — a JOINT-DECODED tagger-parser that re-estimates category from
structure — does NOT lift 19c verb recall past the CRF calibrated posterior, and is therefore the located negative the
bar explicitly sanctions as a full pass. The reason is precise and measured: the recoverable 19c category signal is a
LEXICAL/EMISSION-level signal that the likelihood-trained (CRF) calibrated posterior already captures (AUROC 0.94), so
the structural re-estimation has essentially nothing left to add (+0.0017 AUROC with a register-robust parser). The real
"one lever, two payoffs" is the CALIBRATED POSTERIOR itself (axis-1): I hardened it, made it GLASS-BOX and
DEPENDENCY-FREE, and showed that recovering a dropped verb with it lifts the parser's downstream who-did-what
reachability +0.31 CI-separated — provided the recovery is PRECISION-GUARDED (the naive joint decode floods the parse).

## 0. First-hand premise reproduction (before building)
Reproduced the parent's axis-1 result on disk: the CRF calibrated posterior recovers 19c dropped verbs where the
perceptron max-margin does not; P(VERB)=0.928 on true verbs / 0.008 on non-verbs, saturation 0.845 (vs the perceptron's
96%) — the calibration story holds. The "0.806" is the recovery @FP<=0.5 at the parent's caps; at my full cap
(lbcap=2500) the same CRF_POST arm gives 0.8727. **This number moves with the population/threshold — it is a soft target,
which is exactly why the brief's DO-NOT-QUOTE flags it. The load-bearing fact is the RELATIVE one: the joint decode does
not beat the calibrated posterior, whatever the population.**

## 1. The brain mechanism, and the one variable I changed
PINNED (parent drill + BRAIN_FOUNDATIONAL_AUDIT): lexical category is a GRADED/CALIBRATED belief (predictive coding;
Kuperberg-Jaeger 2016) that settles JOINTLY with structure (MacDonald 1994; Fromont 2020 — N400+P600 additive, no
syntax-first ELAN). The register-robustness the parent named comes from CONTENT-INDEPENDENT structure-building — the
language network builds structure on Jabberwocky at ~52% magnitude (Fedorenko), 2-year-olds slot invented verbs from
frame alone (Yuan 2011). **The faithful computational form of "register-robust parser" is therefore the DELEXICALIZED
parser** (POS + morphology + configuration, NO word identity; McDonald 2011 — the standard cross-domain transfer tool).
So the ONE VARIABLE I changed to test the brief's "the parser must ALSO be register-robust" claim is the parser's
feature set: I retrained the arc-eager parser (reusing its transition system byte-for-byte) with the 5 word-identity
features removed. **PINNED = the joint-settling computation and the content-independence; OUR-INVENTION-UNDER-TEST = the
delexicalized feature set + the force-VERB coherence localization.**

## 2. What I built
- **A register-robust (DELEXICALIZED) arc-eager parser** (`exp_joint_decode_register_robust_tagger_parser_v1`): the AEO
  transition system + dynamic oracle, retrained on UD-EWT with word-identity features dropped (POS/morph/valency kept).
  Modern UAS 0.762 vs the lexical parser's 0.842 (delexicalization costs 8 UAS in-domain, as expected).
- **The localized JOINT DECODE** = the parent's force-VERB re-parse coherence cue (does forcing token i to VERB make the
  parse cohere — nominal subj/obj attach with higher confidence), fed to the CRF-posterior detector, with the parser
  swapped between LEXICAL and DELEXICALIZED. This is "category re-estimated from structure" localized to the contested
  token (the faithful joint decode for exactly the NN<->VB decision that matters).
- **A pure-numpy GLASS-BOX CRF** (`exp_crf_glassbox_marginals_v1`): extract the linear-chain CRF's state/transition
  weights ONCE (crfsuite used only to build the asset), then compute P(VERB) by log-space forward-backward in numpy.
- **The residual decomposition + downstream best-shot** cells (AUROC per cue, spaCy oracle, OOV split; oracle recovery +
  info-free twin on the drop subpopulation).

## 3. Payoff 1 — the joint decode does NOT push 19c past the calibrated posterior (the located negative)
Recovery of 19c dropped verbs @ FP<=0.5 (19c LitBank transfer, n_pos~55) and the AUROC decomposition (n_cand=10703):

| arm | mechanism | 19c recovery @FP<=0.5 | AUROC (drop vs false-cand) | MODERN |
|---|---|---|---|---|
| perceptron max-margin margin | (parent floor) | 0.582 | — | 0.966 |
| **CRF_POST calibrated posterior** | axis-1 (likelihood) | **0.8727** (twin-sep, delta +0.747) | **0.9409** | 0.931 |
| CRF_POST + parse-coherence, LEXICAL parser | +axis-3 (modern parser) | 0.800 (HURTS) | 0.5901 → CRF+coh 0.9421 (+0.0012) | 0.966 |
| CRF_POST + parse-coherence, DELEX parser | +axis-3 (register-robust) | 0.8727 (NO-OP) | 0.6184 → CRF+coh 0.9426 (+0.0017) | 0.897 |

**The joint decode adds nothing on 19c.** The register-robust (delex) coherence IS a better structural separator than the
register-brittle (lexical) one (AUROC 0.618 > 0.590 — confirming the parent's "the parser is also modern-trained"
diagnosis is REAL), but the calibrated posterior already sits at AUROC 0.94, so there is no headroom for structure to
fill. **CAUSE, with the number:** the recoverable 19c category signal is captured by the likelihood-trained emission
posterior (axis-1); the incremental value of structural re-estimation (axis-3) is +0.0017 AUROC and 0.0 at the FP<=0.5
operating point. This is a rigorous located negative on the brief's headline mechanism.

## 4. Payoff 2 — the downstream who-did-what payoff is REAL, but the lever is the calibrated posterior + precision-guard
The v1 full-pop measurement looked like a disaster: feeding the modern-threshold detector's recovered tags into the
parse forced 6576 VERBs across 3015 records and COLLAPSED who-did-what reachability 0.698 -> 0.497. **That is a
detector-PRECISION (flooding) artifact, not a test of whether verb recovery helps.** Isolating the subpopulation where
the fix acts — the genuine drops (verb_idx tagged non-VERB), n=55 — and correcting ONLY the dropped verb:

| arm (genuine-drop subpop) | reach | who-did-what acc |
|---|---|---|
| base (lexical parser, verb dropped) | 0.4909 | 0.2909 |
| **+ recover the dropped verb (lexical parse)** | **0.8000** | **0.5273** |
| + recover the dropped verb (delex parse) | 0.7455 | 0.4545 |
| info-free twin (force a RANDOM token->VERB) | 0.4364 | 0.2727 |

reach: recover-vs-base **+0.3091 CI[0.1818,0.4545] sep=True**; recover-vs-twin **+0.3636 CI[0.2364,0.5091] sep=True**;
twin-vs-base -0.0545 CI[-0.1273,0.0] NOT-sep. **So recovering the dropped verb genuinely lifts the parser's downstream
who-did-what consumer, CI-separated, twin losing — the "two payoffs" hold.** But the deployable form is a HIGH-PRECISION
recovery (correct only genuine drops), because the parse-flooding FP budget is far tighter than the detection FP budget:
each spurious VERB reroutes argument attachment. The delex parser realizes slightly less of the gain (0.745 vs 0.800) —
it is a weaker parser, not a more register-robust one, on this instrument.

## 4b. Why delexicalization is NOT the register-robustness lever here (a measured sub-finding)
The brief inherited the parent's hypothesis that the parser's register-brittleness is the block. It is real (§3, delex
coherence > lexical coherence) but it is NOT a vocabulary problem a delexicalized parser fixes: **only 23.6% of the 19c
dropped-verb tokens are OOV vs UD-EWT-train (10.3% of all 19c tokens)** — 19c prose is ~90% modern vocabulary with
archaic WORD-ORDER. The lexical hashed-perceptron parser already backs off to POS features on the OOV minority (unseen
`s0w:` -> ~0 weight), so delexicalization mostly discards the lexical signal that still helps on the in-vocab majority,
at a cost of 8 UAS in-domain. The register gap is constructional (word order), which a modern-trained parser — lexical
OR delexicalized — carries a modern bias into.

## 4c. The residual is a fidelity gap, not a meaning ceiling
spaCy (a competent statistical reader, used STRICTLY as an offline diagnostic oracle — never at inference) recovers
0.818 of the 19c drops and 0.881 of the in-vocab drops. So the drops are recoverable by a stronger statistical
tagger/parser (more data / neural representations), NOT only by world-knowledge. This localizes the true next lever:
BASE-MODEL CAPACITY / target-register training data, not the joint-decode architecture and not (for THIS residual) the
meaning hub. (The genuine meaning-hub residual lives in the MODERN confident-mistag 33%, per parent SS4b — a different
population.)

## 5. The dependency story, resolved (the deployable win)
The calibrated CRF posterior was a `sklearn_crfsuite.CRF` pickle — crfsuite is not a tracked substrate dependency and a
pickle is not glass-box. A linear-chain CRF is just state potentials + label-label transitions + forward-backward, and
ALL its weights are introspectable. I extract them once into a plain json (`crf_tagger_glassbox.json`, 1.4MB) and compute
P(VERB) in pure numpy; it reproduces `predict_marginals` to **max|dP(VERB)| = 7.3e-7** and Viterbi tags to 100%. **So the
calibrated posterior ships as a dependency-free static asset — the brief's named admissible alternative to tracking
crfsuite at runtime — and is landable in hdlab with NO new runtime dependency and NO external LLM.**

## 6. PROPOSED hdlab WIRE (strategy lands it — Q111, default-off, witnessed; I do NOT edit hdlab)
1. **Ship** `data/exp_crf_glassbox_marginals_v1/crf_tagger_glassbox.json` -> a frontend asset (e.g.
   `data/frontend_assets/pos_crf_glassbox_ud_ewt.json`).
2. **New glass-box organ** `hdlab/crf_tagger.py` (promote `exp_crf_glassbox_marginals_v1.GlassBoxCRF`): load the json,
   expose `vpost(tokens) -> P(VERB) per token` via pure-numpy forward-backward. NO crfsuite, NO LLM.
3. **Upgrade the landed `predicate_detector`'s category cue** from the perceptron max-margin margin to
   `logit(GlassBoxCRF.vpost)` — tied on modern, the calibrated axis-1 cue on 19c. This is the parent SS4c recommendation,
   now dependency-free.
4. **Do NOT land the joint parse-decode** (§3 located negative — adds +0.0017 AUROC, hurts at the operating point) and
   **do NOT land the delexicalized parser** (§4b — loses 8 UAS in-domain, immaterial on 19c).
5. **For the downstream who-did-what payoff** (§4): if a free-text 19c event/role consumer is wired, gate verb recovery
   at a HIGH-PRECISION threshold (correct only confident genuine drops) — the reachability gain is real (+0.31 CI-sep)
   but the parse-flooding FP budget is tight; do NOT feed the modern-calibrated (recall-tuned) detector into the parser.

## KEY REALIZATIONS
- **The calibrated posterior already IS the whole lever; structure has nothing to add.** The enabling move was the AUROC
  decomposition: CRF posterior AUROC 0.94 vs force-VERB coherence AUROC 0.59–0.62. Once you see the posterior separates
  the drops almost perfectly, the "joint decode helps" hypothesis is dead on arrival — the structural cue is redundant,
  not brittle-but-fixable. **A shared wall across lexical AND delexicalized parsers was NOT "the parser isn't good
  enough"; it was "the signal you're trying to add is already accounted for."**
- **The downstream collapse was a precision artifact, and the fix was to isolate the subpopulation.** The full-pop
  reachability crash (0.698->0.497) screamed "verb recovery hurts the parser." It didn't — 6576 false corrections did.
  Correcting only the genuine drop flipped it to +0.31 CI-sep. **Ask whether the experiment could have succeeded (what
  is the fix even allowed to touch?) before reading the aggregate number as the mechanism.**
- **"Register-robust parser" is not "delexicalized parser" when the register gap is word-order, not vocabulary.** 19c is
  90% in-vocab; the OOV-backoff of a hashed perceptron already handles the archaic-word minority. Measuring the OOV rate
  BEFORE building the delex parser would have predicted the null — the delex parser's only honest role here was to prove
  the register-brittleness is real (AUROC 0.62>0.59) yet immaterial.
- **A pickled dependency becomes a glass-box asset by writing out the weights and reimplementing the 20-line math.** A
  linear-chain CRF's marginals are forward-backward; reproducing crfsuite to 7e-7 turned a runtime dependency into a
  static json — the difference between "landable" and "not".

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b)
- **POS tagger category belief (axis-1, PINNED graded/calibrated):** CONFIRMED as the lever. The likelihood-trained CRF
  calibrated posterior captures the recoverable 19c category signal (AUROC 0.94; recovery 0.87 @FP<=0.5 vs perceptron
  0.582), and is now GLASS-BOX + dependency-free (pure-numpy forward-backward, 7e-7 vs crfsuite). Mark the perceptron
  max-margin cue SUPERSEDED by the glass-box calibrated posterior; crfsuite is NOT required at inference.
- **Joint POS+parse decode (axis-3, was named the "deeper build"):** LOCATED NEGATIVE. Force-VERB parse-coherence adds
  +0.0017 AUROC (register-robust delex parser) / +0.0012 (lexical, and it hurts the operating point) over the calibrated
  posterior on 19c — the structural re-estimation is redundant with the calibrated emission posterior. Retire "joint
  decode lifts 19c" as the deeper fidelity target; it does not.
- **Register-robustness of the parser:** the brittleness is REAL (delex coherence AUROC 0.618 > lexical 0.590) but is a
  WORD-ORDER gap (19c 90% in-vocab), not the vocabulary gap a delexicalized parser addresses; delex costs 8 UAS
  in-domain. The 19c verb-drop residual is a PARSER/TAGGER-FIDELITY gap (spaCy recovers 0.82/0.88), closable by base-model
  capacity/target-register data — NOT by the joint-decode architecture and NOT (for this population) by the meaning hub.

## 7. Adjacent-component map (capabilities / limitations / brain status / next problems)
| component (hdlab) | capability now | limitation | brain status | opportunity -> next problem |
|---|---|---|---|---|
| **POS tagger** (`pos_tagger.py`) | perceptron Viterbi UPOS 0.945; max-margin argmax | max-margin posterior saturated (uncalibrated); OOD-brittle | calibrated graded belief = PINNED | **land the glass-box calibrated CRF posterior** as the category cue (this problem's deployable win) |
| **arc-eager parser** (`arceager_parser.py`) | UAS 0.842 modern; force-VERB coherence cue | register gap is WORD-ORDER (modern-trained), NOT fixable by delexicalization; coherence redundant with the posterior | joint settling = PINNED; the modern-train bias = OUR limitation | a target-register / higher-capacity BASE parser (more data), or neural — the real 19c parse lever |
| **predicate_detector** (`predicate_detector.py`) | learned noisy-channel recovery, wired default-off | category cue = perceptron margin | calibrated cue = PINNED | swap the cue to `logit(glassbox CRF P(VERB))` — the §6 wire |
| **who-did-what selection** (`predicate_argument_frontend`) | reachability + chain_pick through the parse | gated by ARGUMENT SELECTION (meaning), not the verb's tag once the verb is present | thematic-fit selection = PINNED (meaning hub) | register-native REFUTED grammar as the lever; this is the meaning-hub program's consumer |
| **glass-box CRF** (new, `exp_crf_glassbox_marginals_v1`) | pure-numpy linear-chain marginals, 7e-7 vs crfsuite | none material (byte-faithful) | n/a (engineering) | reuse as the substrate's calibrated-tag provider wherever a posterior is needed |

## What I did NOT establish (would withdraw first if wrong)
- I did NOT build a FULL beam joint decoder (Bohnet-Nivre global search over (tag, action)); I built the force-VERB
  coherence LOCALIZED to the contested token. **I argue a full beam would not change the conclusion** — the AUROC
  decomposition shows the structural cue itself carries little separating signal beyond the calibrated posterior
  (0.62 vs 0.94), and a global search cannot manufacture signal that is not in the features. If withdrawn, this is the
  first thing to test — but it is a low-prior rescue of a well-measured null.
- The 19c recovery numbers are on the LitBank who-did-what pop's supplied `verb_idx` (a known real verb the live tagger
  missed) — the clean who-did-what slice, not a fully free-text 19c verb gold (no 19c POS treebank exists; register-native
  established this). The genuine-drop subpopulation is n=55; the payoff-2 CIs are wide but separated.
- spaCy is an OFFLINE diagnostic oracle only (parent's admissible exception), never at inference; its recovery frac is a
  reference ceiling, not a deployable number.
- "0.806" is population/threshold-sensitive; I report the RELATIVE result (joint decode does not beat the calibrated
  posterior on the SAME population) rather than an absolute cross of 0.806.

---

### TLDR (plain language)
Our reader tags each word's part of speech, then parses the sentence. On old/unusual prose it sometimes mislabels a real
verb as a noun, and the event is lost. The plan was to make the tagger report an honest, graded confidence (a
probability) instead of an over-sure yes/no, AND to let the tagger and the sentence-structure parser correct each other
as they decide. I built both. The honest-confidence tagger works and is the real fix: on its own it correctly flags ~87%
of the old-prose verbs the current tagger drops (up from ~58%), and when it recovers a dropped verb, the reader's
"who-did-what" for that clause improves a lot (right answer rate roughly 0.49 → 0.80 on the affected sentences — a real,
statistically clean gain, and a random guess does not do it). BUT letting the parser also vote on the part of speech adds
essentially nothing — the honest-confidence tagger has already captured the signal, so the extra "joint" machinery is not
worth building. Two useful bonus findings: (1) making the parser "content-blind" (the brain-inspired idea) does not help
here, because old prose is 90% ordinary vocabulary — the difficulty is old word ORDER, not old words; and (2) I removed a
software dependency by rewriting the confidence-tagger's math in plain code that matches the original to seven decimal
places, so it can be shipped as a simple data file. Net: the graded-confidence tagger is a keeper and is ready to wire;
the "joint decode" part of the plan is a dead end, for a clearly measured reason.

### QUESTIONS
None blocking. One judgement call for strategy at landing: the downstream who-did-what gain needs a HIGH-PRECISION verb-
recovery threshold (correcting every low-confidence candidate floods the parser and erases the gain). That is a
precision-vs-recall dial for the parse, not a correctness question — pick a conservative threshold, or gate recovery on a
free-text event consumer where the flooding is acceptable.

### NEXT STEPS
1. **Land the deployable win** (strategy, Q111, default-off, witnessed): ship the glass-box CRF json, add
   `hdlab/crf_tagger.py`, swap `predicate_detector`'s category cue to `logit(CRF P(VERB))` (dependency-free). §6.
2. **Do NOT pursue the joint decode or the delexicalized parser** — both measured null/immaterial here (§3, §4b).
3. **The real 19c parse lever is base-model capacity / target-register data** (§4c: spaCy recovers 0.82/0.88 of the
   drops) — a higher-capacity or target-register-adapted BASE tagger/parser, filed as the successor to this problem.
4. **The 19c who-did-what residual is a SELECTION/meaning problem** (§7: reachability is gated by argument selection once
   the verb is present) — a consumer of the meaning-hub / learner-on program, consistent with register-native's REFUTED
   grammar lever.
