---
problem: harm_help_valence_is_a_fitted_verb_list_not_the_substrates_force_dynamic_arithmetic
status: SOLVED
bar: "Compute harm/help event valence from the substrate's FORCE-DYNAMIC arithmetic (AGONIST tendency x ANTAGONIST force -> RESULT worse/better/unchanged, per Wolff), retiring the verb-LIST membership test AND the in-process read-path parse, and SHOW it matches-or-beats the verb-list on the harm/help metric while GENERALIZING to held-out verbs the list misses (info-free twin LOSING, no downstream regress to causation/affect dims) -- OR a rigorous LOCATED NEGATIVE naming exactly why the force computation cannot match the list on the reader's own metric (with a number; the brain's actual mechanism faithfully built). INVARIANT: recall path + non-valence consumers byte-identical off the changed decision; no external tool/LLM/read-path parse at inference."
result: "Through the LIVE reader on a 36-item modern harm/help gold: force-dynamic arithmetic 0.944 (+/-0.069) vs the current frame-list organ 0.778 (+/-0.125); PAIRED fd-minus-organ = +0.167, bootstrap CI [+0.056, +0.278] (CI-separated from 0), 6 gains / 0 losses. On the 32 social/emotional verbs the frame list misses: fd 0.875 (+/-0.109) vs current organ 0.000 (CI-separated). Info-free twin (scrambled valence+force lexicon) 0.639 live / 0.28 on the generalization set (loses)."
floor: "Strongest floor = the CURRENT LIVE organ hdlab.force_dynamics_valence.harm_help (frame-membership): 0.778 on the live gold, 0.000 on the frame-list-miss set. Also: majority-class (all-NEUTRAL) 0.333; valence_only control (info-bearing, no gate/structure) 0.94 on generalization but 0.00 neutral-precision and 0.43 off-diagonal."
controls: "(1) info-free twin = valence map AND force lexicon SCRAMBLED -> loses (0.639 live vs 0.944; 5/8 vs 8/8 witness). (2) valence_only control (animacy+sign(valence), no affectedness gate, no force structure) -> generalizes but DESTROYS neutral precision (T5 0.00 vs 1.00) and FAILS the off-diagonal force cells (T6 0.43 vs 1.00) -> isolates that BOTH the affectedness gate and the force structure are load-bearing, not the valence lookup alone. (3) LIVE no-regress: every NON-affect SituationModel dimension byte-identical + OCC appraisal (sm.infer_emotion) + emotion register (sm.feels/valence_of) readouts identical across 52 modern docs (only EventRecord.affect moves). (4) off-diagonal population = the Wolff truth-table cells (ENABLE-a-bad, PREVENT-a-good, failed-harm) a bare valence-lookup cannot get."
files_changed: "experiments/exp_fd_harm_help_arithmetic_v1.py (the arithmetic + constructed populations T1-T6), experiments/exp_fd_harm_help_arithmetic_live_v1.py (live no-regress + scored modern gold + paired bootstrap), verification/test_fd_harm_help_arithmetic.py (8/8 scaffold-free witness). NO hdlab/ writes (Q111 -- the exact proposed hdlab diff is in this doc)."
reverify: ".venv/Scripts/python.exe verification/test_fd_harm_help_arithmetic.py"
---

# Harm/help valence as the substrate's OWN force-dynamic arithmetic (not a fitted verb list)

## FINAL SUMMARY (read this first)

**What the defect was.** `hdlab/force_dynamics_valence.py` (one of the 8 live NOT_BF organs) decided harm/help
by **verb-LIST membership**: HARM = the verb is in a set of FrameNet harm-frame lexical units (`Cause_harm`,
`Killing`, `Attack`, ...) plus a hand `HARM_BACKOFF`; HELP = the verb's force class is `PREVENT`/`ENABLE`. That is
lexical lookup, not a force simulation, and it built the harm-verb set by **enumerating FrameNet frames
in-process on the read path** (uncached FrameNet access at inference -- the second flagged defect). Because
FrameNet's Causation family has no lexical unit for social/emotional harm, the organ **abstains on every
social/emotional harm verb** (mug, evict, fire, bully, humiliate, betray, abuse) and **every non-prevent help
verb** (comfort, console, help, heal, cure, feed) -- verified on disk, all return `None`.

**The brain-foundational fix (built, proven, proposed -- not landed, Q111).** Harm/help is not a lexical class;
it is the **sign of the welfare change the affector produces on the patient**, and it DECOMPOSES into two
independently-grounded bits the brain computes separately (Talmy 1988; Wolff 2007 force theory of causation;
OCC appraisal; Russell/Barrett core affect):

1. **FORCE STRUCTURE** -- does the affector make the endstate HAPPEN (CAUSE/ENABLE, +1) or BLOCK it (PREVENT,
   -1)? Reuse the PINNED Wolff typer already in the substrate (`hdlab/force_dynamics_lexicon` +
   `patient_tendency`; the same computation `hdlab/causation_typing.py` uses).
2. **ENDSTATE VALENCE for the patient** -- is the reached/blocked endstate good or bad FOR THE PATIENT? Reuse
   `hdlab/affect_lexicon.py` -- grounded Warriner valence = the OFC/amygdala evaluation of a state (the exact
   "patient-outcome polarity" bit the brief's nuance (i) names as the further bit on top of the force structure).

   `harm/help = sign( force_effect x endstate_valence )`:
   `CAUSE/ENABLE x adverse -> HARM ; CAUSE/ENABLE x beneficial -> HELP ; PREVENT x adverse -> HELP ; PREVENT x beneficial -> HARM.`

   An **AFFECTEDNESS gate** (Hopper-Thompson/Beavers/Dowty: does the force actually change the patient's state)
   fires the arithmetic only when the verb has a force class OR a WordNet AFFECTING supersense
   (contact/body/change/emotion/possession/consumption/competition/creation/social) -- suppressing
   perception/cognition/communication verbs (watch/greet/describe: the patient is a stimulus, not an undergoer).

**Both defects are removed:** the harm-frame LU set + `HARM_BACKOFF` are gone (harm/help is derived, not a
membership test), and there is **no in-process FrameNet enumeration** -- the arithmetic reads only the
disk-cached force lexicon, the shipped Warriner CSV, and WordNet supersenses (all admissible static assets;
verified: the decision function references no FrameNet frame).

**The numbers (bar met).**

| population | current organ (frame-list, the floor) | valence_only (naive control) | **fd_arithmetic** | info-free twin |
|---|---|---|---|---|
| social/emotional HARM (frame-list miss) | **0.00** | 0.94 | **0.81** | 0.13 |
| non-prevent HELP (frame-list miss) | **0.00** | 0.94 | **0.94** | 0.44 |
| harm-frame HARM (keep the win) | 1.00 | 1.00 | **1.00** | 0.20 |
| prevent/enable HELP (keep the win) | 1.00 | 1.00 | **1.00** | 0.80 |
| NEUTRAL perception precision | 1.00 | **0.00** | **1.00** | 1.00 |
| off-diagonal force cells | -- | **0.43** | **1.00** | 0.64 |
| **LIVE reader, 36-item modern gold** | **0.778** | -- | **0.944** | 0.639 |

- **Beats the floor, generalizing:** live 0.944 vs 0.778, paired **+0.167 CI [+0.056,+0.278]** (CI-separated, 6
  gains / 0 losses -- strictly dominant); the 6 gains are exactly the frame-list misses (mugged, evicted, fired /
  comforted, consoled, helped) now surfacing HARM/HELP through the real reader.
- **The force structure does non-redundant work** a valence-lookup cannot: the off-diagonal cells (ENABLE-a-bad
  = HARM "let the assassin kill the king"; PREVENT-a-good = HARM "blocked the medic from saving the wounded";
  failed/negated harm = neutral "tried to stab but the vest stopped it") -- fd 1.00 vs valence_only 0.43.
- **The affectedness gate earns precision:** valence_only over-fires HELP on every neutral perception verb (T5
  0.00); the gate keeps it at 1.00 while still generalizing.
- **No downstream regress; info-free twin loses.** Both controls hold.

## WHAT WAS BUILT / MEASURED
- `harm_help_arithmetic()` (the force-structure x grounded-valence decision, with the affectedness gate and the
  full endstate/embedded-endstate handling for the off-diagonal Wolff cells) -- a drop-in for the module-level
  `hdlab.force_dynamics_valence.harm_help`.
- Six constructed populations (T1 social/emotional harm, T2 non-prevent help, T3 harm-frame, T4 prevent/enable,
  T5 neutral precision, T6 off-diagonal) + a generalization aggregate, four arms (current organ / valence_only /
  fd / twin), bootstrap CIs.
- The **live-reader validation**: PART A no-regress (52 modern docs, non-affect dims + OCC/emotion byte-identical)
  and PART B scored modern gold (paired fd-minus-organ CI). The correct live decision point (verified on disk) is
  `hdlab.force_dynamics_valence.harm_help` reached via `situation_reader._assign_affect ->
  context_grounded_valence.score_item -> force_dynamics_event_type -> harm_help`.

## WHAT I DID NOT ESTABLISH (what I would withdraw first)
- **The 36-item modern gold is author-declared, not a corpus gold** (no harm/help-labelled modern corpus exists on
  disk -- the prior work flagged the same). It is DIRECTIONAL live-path evidence; the load-bearing evidence is the
  constructed populations (transparent, adversarial to the gate), the LIVE no-regress, and the info-free twin. If
  one result had to go first, it is the absolute live-gold number (keep the paired direction + the no-regress).
- **The affectedness gate is conservative on pure-communication-supersense verbs** (betray, slander abstain: their
  first WordNet supersense is `communication`, so harm-via-social-consequence is missed). This is the same WSD
  boundary `hdlab/causation_typing.py` faces; it is a NAMED upstream problem, not a mechanism failure.
- **`scratch`-class near-zero-valence verbs abstain** (Warriner valence ~= 0 for genuinely mild-harm verbs) -- a
  grounded-valence coverage boundary, reported.
- I did **not** land any hdlab change (Q111). The exact diff is below; strategy lands + re-verifies.

## THE EXACT hdlab DIFF (proposed; Q111 -- strategy lands)
In `hdlab/force_dynamics_valence.py`, replace the harm-frame-membership machinery with the arithmetic:
- **REMOVE**: `HARM_FRAMES`, `HARM_BACKOFF`, `_harm_verbs()`, `_harm()`, and the `nltk.corpus.framenet` import
  (the in-process read-path FrameNet enumeration -- defect D2).
- **ADD**: `from hdlab.affect_lexicon import AffectLexicon` (grounded endstate valence) + a cached WordNet
  first-supersense lookup (affectedness gate) + `AFFECTING_SUPERSENSES`.
- **REPLACE** the body of `harm_help(verb, animacy)` with `harm_help_arithmetic` (verbatim from
  `experiments/exp_fd_harm_help_arithmetic_v1.py`; the live bare-SVO path uses `endstate_reached=None`).
- `force_dynamics_event_type` (the stage-2 structural gate + animacy) and `_lex()` (the disk-cached force lexicon)
  are UNCHANGED -- the signature and the reader wiring stay byte-identical off the decision.
- Set `__bf_status__ = "BF_SPIRIT"` and update `__bf_note__` (harm/help = Wolff force-structure x grounded-affect
  endstate valence + affectedness gate; no frame-list membership; no read-path FrameNet parse) and append a
  `__bf_corrections__` line.

## KEY REALIZATIONS (the enabling moves)
- **Harm/help = TWO independently-grounded bits, not one lexical class.** The frame list conflated force structure
  and outcome polarity into "which FrameNet frame"; decomposing into force-structure (Wolff typer, reused) x
  endstate-valence (grounded affect, reused) is what generalizes -- and both organs already exist (REUSE, not
  rebuild).
- **The grounded Warriner valence separates the social/emotional verbs the frame list is blind to** (mug -0.21,
  evict -0.59, bully -0.58, humiliate -0.60, abuse -0.87 all negative; comfort +0.56, heal +0.60, cure +0.70 all
  positive) -- the OFC/amygdala outcome evaluation is exactly the missing bit.
- **The affectedness gate is what stops valence from over-firing.** Perception verbs carry incidental positive
  valence (watch +0.11, read +0.43); without a "does the force change the patient" gate a valence readout calls
  them HELP. The gate is why fd keeps precision 1.00 where valence_only collapses to 0.00.
- **The prior live cell's patch target was STALE.** `exp_fd_harm_help_live_modern_v1.py` patched
  `ea.event_type_for_item_real`, but since `force_dynamics_valence` landed, the live path routes through
  `FDV.harm_help` -- patching the old point silently no-ops (fd == organ == twin). The disk decision point
  outranked the prior cell.
- **Where the signal is lost upstream (owner's trace directive):** the 2 remaining LIVE misses are NOT harm/help
  failures. `bullied intern` -> the POS tagger tags the rare noun "intern" as ADJ, so patient-binding fails
  (`patient == agent`) and no event/patient reaches the decision -- an upstream **pos_tagger / role-binding**
  defect. `scratched` -> `scratch` has ~0 Warriner valence -- a grounded-valence coverage boundary. My decision is
  correct in both (bully->HARM, scratch->abstain-on-near-zero); the loss is upstream.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md + notes/bf_status_registry.jsonl)
- `hdlab/force_dynamics_valence.py`: **NOT_BF -> BF_SPIRIT** once the proposed diff lands. New basis: harm/help =
  PINNED Wolff force-structure (CAUSE/ENABLE/PREVENT) x grounded-affect endstate valence (Warriner) + a
  Hopper-Thompson/Beavers affectedness gate; no verb-list membership; no read-path FrameNet parse. Residual
  (keeps it BF_SPIRIT not BF): the affectedness gate uses WordNet first-supersense (OUR-INVENTION cut, context-
  free -> the communication-supersense boundary) and the endstate-valence read is lexical, not a per-clause
  resulting-state simulation.

## ADJACENT / UPSTREAM COMPONENTS (candidate follow-on problems, brain-fidelity + leverage)
- **`hdlab/pos_tagger.py` / predicate-argument extraction (patient binding).** UPSTREAM WALL. Rare/OOV nouns
  ("intern") mistagged ADJ -> patient binds to the agent -> the harm/help signal never reaches the decision (the
  `bullied` live miss). This caps harm/help recall independently of the organ. Evidence: `A coworker bullied the
  intern` -> `patient='coworker'`. In the mega-cluster "the parser" (`notes/CROSS_SOLUTION_IMPROVEMENT_MAP.md`).
- **The verb-sense / literalness gate (`no_glass_box_verb_sense_disambiguation`).** The affectedness gate's
  context-free WordNet-supersense cut is the source of the betray/slander boundary; a context-aware sense pick
  (which the causation typer already lazily imports) would resolve harm-via-communication verbs.
- **`hdlab/causation_typing.py` (BF_SPIRIT, DORMANT).** It ALREADY computes the full force STRUCTURE
  (CAUSE/ENABLE/PREVENT + endstate) from the in-substrate parse, including the off-diagonal constructions
  (prevention-from, resultative, caused-motion). The richest landing is to compute harm/help ON TOP of its
  TypedCausalLinks (embedded-endstate valence from the complement clause) rather than the bare-SVO reduction --
  this is what unlocks the off-diagonal cells on REAL text, not just constructed items.
- **`hdlab/affect_lexicon.py` (BF_SPIRIT).** The endstate-valence supplier; a resulting-STATE valence read (from
  an explicit resultative "beat him unconscious") would beat the verb-valence proxy on benefactive-negative verbs
  (surgery/dentistry: "cut"/"drill" negative valence but helpful) -- the one residual class the verb-valence proxy
  mislabels.

## SUBSTRATE INCORPORATION MANIFEST
- **INCORPORATE**: the `harm_help_arithmetic` decision (force-structure x grounded-valence + affectedness gate) as
  the body of `hdlab.force_dynamics_valence.harm_help`; the removal of the FrameNet harm-frame enumeration.
  Witness `verification/test_fd_harm_help_arithmetic.py` (8/8) gates it.
- **INCORPORATE-AS-DURABLE-NEGATIVE**: the located boundaries -- pure-communication-supersense harm verbs
  (betray/slander) abstain (WSD boundary); near-zero-valence mild-harm verbs (scratch) abstain (valence coverage);
  the `bullied` upstream POS/patient-binding loss (NOT a harm/help defect).
- **DO-NOT-INCORPORATE**: the `valence_only` arm (a control showing the gate + structure are necessary, not a
  shippable decision); the 36-item author-declared gold as a load-bearing metric (directional only).

## TLDR (plain language)
When the reader decides whether an event hurt or helped a character, it used to just look the verb up in a
hand-built list of "harmful" and "helpful" words -- so it silently missed every socially or emotionally harmful
act (being mugged, evicted, bullied, humiliated) and every gentler helpful act (comforting, consoling, healing),
and it re-scanned a big external word database every time it read. I rebuilt the decision the way the brain does
it: combine (a) the physics of the interaction -- did the actor make the outcome happen or block it -- with (b)
whether that outcome is good or bad for the person, read from a standing table of how good or bad each word feels.
Both pieces already existed in the system; I just did the arithmetic. Tested through the real reader on 36 modern
sentences, it went from ~78% right to ~94% right (a solid, statistically clean gain with nothing it used to get
right now broken), and it correctly handles the tricky cases a word-list never can -- "let the killer in" is
harm, "blocked the rescue" is harm, "tried but failed to hurt him" is not harm. It stops re-scanning the external
database. Two cases it still misses are actually the fault of an earlier step (a rare word, "intern", gets
mis-tagged so the victim is lost before the decision even runs) -- I traced and documented that.

## QUESTIONS
None -- the mechanism is built, measured through the live reader against the real floor with the controls, and
the exact hdlab diff is specified. (SOLVED.md is WIP until owner_verdict: DONE.)

## NEXT STEPS
1. Land the proposed `force_dynamics_valence.py` diff (Q111) and re-verify `verification/test_fd_harm_help_arithmetic.py` (8/8).
2. Wire harm/help onto `causation_typing.py`'s TypedCausalLinks so the off-diagonal cells (prevent-a-good,
   enable-a-bad) fire on REAL text via the complement-clause embedded endstate, not just constructed items.
3. Fix the upstream patient-binding loss (rare-noun POS mistag) -- it caps harm/help recall independently (the
   `bullied` miss); route to the parser cluster.
4. Add a resulting-STATE valence read (resultatives) to resolve benefactive-negative verbs (surgical "cut"/"drill").
