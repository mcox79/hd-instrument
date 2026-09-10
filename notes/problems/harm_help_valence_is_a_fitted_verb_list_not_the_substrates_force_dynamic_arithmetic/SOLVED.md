---
problem: harm_help_valence_is_a_fitted_verb_list_not_the_substrates_force_dynamic_arithmetic
status: SOLVED
bar: "Compute harm/help event valence from the substrate's FORCE-DYNAMIC arithmetic (AGONIST tendency x ANTAGONIST force -> RESULT worse/better/unchanged, per Wolff), retiring the verb-LIST membership test AND the in-process read-path parse, and SHOW it matches-or-beats the verb-list on the harm/help metric while GENERALIZING to held-out verbs the list misses (info-free twin LOSING, no downstream regress to causation/affect dims) -- OR a rigorous LOCATED NEGATIVE naming exactly why the force computation cannot match the list on the reader's own metric (with a number; the brain's actual mechanism faithfully built). INVARIANT: recall path + non-valence consumers byte-identical off the changed decision; no external tool/LLM/read-path parse at inference."
result: "Through the LIVE reader on a 36-item modern harm/help gold: force-dynamic arithmetic 0.944 (+/-0.069) vs the current frame-list organ 0.778 (+/-0.125); PAIRED fd-minus-organ = +0.167, bootstrap CI [+0.056, +0.278] (CI-separated from 0), 6 gains / 0 losses. On the 32 social/emotional verbs the frame list misses: fd 0.875 (+/-0.116) vs current organ 0.000 (CI-separated). Info-free twin (scrambled valence+force lexicon) 0.639 live / 0.28 on the generalization set (loses)."
floor: "Strongest floor = the CURRENT LIVE organ hdlab.force_dynamics_valence.harm_help (frame-membership): 0.778 on the live gold, 0.000 on the frame-list-miss set. Also: majority-class (all-NEUTRAL) 0.333; valence_only control (info-bearing, no gate/structure) 0.94 on generalization but 0.00 neutral-precision and 0.43 off-diagonal."
controls: "(1) info-free twin = valence map AND force lexicon SCRAMBLED -> loses (0.639 live vs 0.944; 5/8 vs 8/8 witness). (2) valence_only control (animacy+sign(valence), no affectedness gate, no force structure) -> generalizes but DESTROYS neutral precision (T5 0.00 vs 1.00) and FAILS the off-diagonal force cells (T6 0.43 vs 1.00) -> isolates that BOTH the affectedness gate and the force structure are load-bearing, not the valence lookup alone. (3) LIVE no-regress: every NON-affect SituationModel dimension byte-identical + OCC appraisal (sm.infer_emotion) + emotion register (sm.feels/valence_of) readouts identical across 52 modern docs (only EventRecord.affect moves). (4) off-diagonal population = the Wolff truth-table cells (ENABLE-a-bad, PREVENT-a-good, failed-harm) a bare valence-lookup cannot get."
files_changed: "experiments/exp_fd_harm_help_arithmetic_v1.py (the arithmetic + constructed populations T1-T6), experiments/exp_fd_harm_help_arithmetic_live_v1.py (live no-regress + scored modern gold + paired bootstrap), experiments/exp_fd_harm_help_composed_v1.py (parse-composed generalization of the off-diagonal to real prose), experiments/exp_pos_nominal_head_correction_v1.py (BF upstream POS fix), experiments/exp_fd_harm_help_chain_attribution_v1.py (per-stage performance-vs-brain attribution), experiments/exp_pos_bayesian_category_v1.py (mathematically-BF Bayesian POS category posterior), experiments/exp_fd_harm_help_hard_prose_v1.py (honest real-prose stress: 0.50->1.0), experiments/exp_fd_harm_help_robust_extraction_v1.py (unified BF role extractor: passive/pronoun/plural, confidence-ranked), experiments/exp_fd_harm_help_role_corpus_validation_v1.py (UD-EWT at-scale role validation), experiments/exp_fd_harm_help_coref_pronoun_v1.py (Opportunity 2: coref pronoun-patient attribution 0->0.917), experiments/exp_fd_harm_help_signal_trace_v1.py (stage-by-stage signal-loss trace: POS 30%/heads 36%/labeler 33%), experiments/exp_fd_harm_help_learned_extraction_v1.py (RIGOROUS fix: voice labeler correction + learned argstruct ranker), verification/test_fd_harm_help_arithmetic.py (9/9 witness), verification/test_pos_nominal_head_correction.py (6/6 witness), verification/test_fd_harm_help_robust_extraction.py (8/8 witness), verification/test_fd_harm_help_coref_pronoun.py (2/2 witness), verification/test_fd_harm_help_learned_extraction.py (3/3 witness). NO hdlab/ writes (Q111 -- the exact proposed hdlab diffs are in this doc)."
reverify: ".venv/Scripts/python.exe verification/test_fd_harm_help_arithmetic.py  (+ verification/test_pos_nominal_head_correction.py for the upstream POS fix)"
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

   An **AFFECTEDNESS gate** computed MATHEMATICALLY as GRADED THEMATIC FIT (McRae/Tanenhaus 1998; Beavers
   2011 affectedness hierarchy): affectedness(verb) = **E[proto-patient degree | sense]** = the WordNet
   SemCor sense-frequency-weighted average of each sense's Beavers affectedness (change/body=1.0, contact/
   possession=0.7, ..., communication/perception/cognition~0). Engage iff this graded score >= tau (swept;
   tau=0.40 on a stable 0.38-0.45 plateau) OR a MARKED PREVENT/ENABLE force-class -- MINUS subject-
   experiencer psych verbs (admire/envy: object is the stimulus; reuse `hdlab/psych_verb_frames.py`), plus a
   strong-valence override for communication-dominant verbal harm (betray/slander). This ONE continuous
   quantity replaces the boolean supersense sets + hand thresholds: it fires on change/contact/emotion/
   possession verbs (mug/evict/heal/comfort AND aid/assist/help), and abstains on perception/communication
   (watch/greet/visit/see/call: their sense mass is on non-affecting senses -> low affectedness).

**Both defects are removed:** the harm-frame LU set + `HARM_BACKOFF` are gone (harm/help is derived, not a
membership test), and there is **no in-process FrameNet enumeration** -- the arithmetic reads only the
disk-cached force lexicon, the shipped Warriner CSV, and WordNet supersenses (all admissible static assets;
verified: the decision function references no FrameNet frame).

**The numbers (bar met).**

| population | current organ (frame-list, the floor) | valence_only (naive control) | **fd_arithmetic** | info-free twin |
|---|---|---|---|---|
| social/emotional HARM (frame-list miss) | **0.00** | 0.94 | **0.875** | 0.13 |
| non-prevent HELP (frame-list miss) | **0.00** | 0.94 | **0.94** | 0.44 |
| harm-frame HARM (keep the win) | 1.00 | 1.00 | **1.00** | 0.20 |
| prevent/enable HELP (keep the win) | 1.00 | 1.00 | **1.00** | 0.80 |
| NEUTRAL perception precision (narrow) | 1.00 | **0.00** | **1.00** | 0.88 |
| NEUTRAL precision (BROAD, +psych/minor-sense leaks) | 1.00 | **0.08** | **1.00** | 0.83 |
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

## DEEPENING: composed generalization of the off-diagonal to REAL PROSE SYNTAX
The bare-SVO arithmetic reads only the MATRIX verb, so the decisive off-diagonal force cells (ENABLE-a-bad,
PREVENT-a-good) only fire when the embedded endstate is hand-supplied. To make that force reasoning
**generalize on real sentences**, `exp_fd_harm_help_composed_v1.py` composes the SAME arithmetic on the
in-substrate parse (`hdlab.causation_typing`'s frontend + construction extraction): the force STRUCTURE comes
from the parsed construction (periphrastic/letting, from-prevention, resultative) and the embedded ENDSTATE
VALENCE is the sign of the most-valenced content word in the complement / from-clause / resultative span (the
brain evaluates the prevented/enabled EVENT). On a 19-sentence parsed gold (each sentence must be PARSED; the
embedded endstate is NOT hand-fed):

| arm | acc | what it is |
|---|---|---|
| valence_only (matrix verb sign) | 0.579 | naive |
| bare_svo (arithmetic, matrix verb only) | 0.579 | no embedded endstate |
| **composed (arithmetic + parsed embedded endstate)** | **0.895** | recovers 6 off-diagonal cells the others miss |

Composed reads "let the assassin **kill** the king" -> HARM, "**knocked** the man **senseless**" -> HARM,
"prevented the rescuer from **freeing** the hostage" -> HARM, "saved the child from the **fire**" -> HELP --
where a matrix-verb lookup says the opposite. **The 2 residual misses are UPSTREAM parse-attachment failures**
(the arc parser drops the `from`-clause for "blocked/stopped X from V-ing", and even roots the wrong verb) --
NOT the harm/help logic: the LOCATED CEILING here is the `arc_parser` from-clause attachment (the parser
cluster), and it is named as the wall. Two robustness fixes were needed and are in the cell: a bare PREVENT
verb with no from-clause succeeds by default (endstate_reached=None, so "rescued"/"freed" don't read as failed
prevention), and gerund complements are verb-lemmatized ("robbing"->rob) so the embedded EVENT valence beats
its object's.

## REAL-PROSE PERFORMANCE -- THE HONEST CEILING (do NOT read the 0.9x numbers as "vs the brain")
The live 0.944 and chain 0.958 are on CLEAN ACTIVE SVO the author wrote ("A mugger attacked the tourist").
A competent reader gets ~1.0 on those too -- so those numbers are the DECISION + clean-extraction ceiling,
NOT a real-reading brain comparison. On HARDER realistic prose a competent reader still aces (passives,
pronoun patients, plurals, relative clauses, coordination, fronted PPs), the SAME (pre-extraction-fix) pipeline scored
**0.500 (6/12)** (`experiments/exp_fd_harm_help_hard_prose_v1.py`) -- the gap was NOT the harm/help decision
(near-ceiling given clean inputs) but EXTRACTION on non-trivial syntax (now FIXED below, 0.500 -> 1.000):
- **passive voice** ("was robbed/rescued/comforted"): the patient (surface subject) sits BEFORE the verb,
  so the organ's positional direct-object gate never fires -- OR predicate_argument_frontend binds the
  by-agent as patient ("comforted by a nurse" -> patient=nurse);
- **pronoun patients** ("attacked him"): the pronoun is not resolved to an animate antecedent (coref);
- **plurals/possessives** ("released their hostages"): the parser mislabels the object (xcomp).

**ALL UPSTREAM EXTRACTION CLUSTERS PROTOTYPED-FIXED, BF (`experiments/exp_fd_harm_help_robust_extraction_v1.py`;
witness `verification/test_fd_harm_help_robust_extraction.py` 7/7).** A unified role extractor over the
in-substrate parse, each cluster fixed with its PINNED linguistic mechanism (not statistics):
- **AFFECT-ROUTING** (harm/help organ): route through the reader's `(e.lemma, patient)` -- the predicate is
  in hand at `situation_reader.py:2016` -- not the positional direct-object gate. (0.500 -> 0.667 alone.)
- **PASSIVE VOICE** (`predicate_argument_frontend`): eADM voice remapping (Bornkessel-Schlesewsky) -- be/get +
  past participle => patient = surface SUBJECT, agent = by-object. Robust to the tagger's VBN<->VBD confusion,
  the head-noun ADV/ADJ mistag ('the elderly widow' -> widow=ADV), and copular participles ('was wounded' =
  ADJ predicate) via morphology + a determiner-phrase-head fallback.
- **PRONOUN PATIENTS** (`coreference`): phi-feature animacy -- 'him/her/them' is an animate referential patient
  (the harm/help TYPE needs the feature, not the resolved antecedent).
- **PLURAL/POSSESSIVE OBJECTS** (`arc_parser`): subcategorization recovery -- a nominal after a transitive verb
  mislabeled clausal (xcomp/dep) is the direct object (Levin transitivity).

**Result: hard-prose 0.500 -> 1.000 (12/12), with NO regression on the clean active-SVO chain set (0.958).**
Every passive/pronoun/plural/copular case binds the correct patient AND types harm/help.

**VALIDATED AT SCALE ON REAL CORPUS GOLD (the not-easy test the 12-item set cannot give):**
`experiments/exp_fd_harm_help_role_corpus_validation_v1.py` runs the extractor on UD-EWT test (1,500
sentences) and scores the bound patient against the GOLD dependency undergoer (active `obj` / passive
`nsubj:pass`), restricted to the harm/help-relevant AFFECTING verbs:

| extractor | affecting-verb recall | precision | PASSIVE recall |
|---|---|---|---|
| naive (dep-obj only, the pre-fix path) | 0.676 | 0.845 | **0.000** |
| **robust (voice + pronoun + subcat, confidence-ranked)** | **0.727** | 0.779 | **0.719** |

The passive recovery (0.00 -> 0.72) generalizes to real prose; recall rises 0.68 -> 0.73 at a bounded,
honestly-reported precision cost (0.85 -> 0.78). **KEY REALIZATION (corpus-driven):** the first cut over-fired
(precision 0.71) because a blanket "nearest-noun-after-the-verb" object grab fires on intransitives -- so the
extractor is CONFIDENCE-RANKED: dep-labelled roles first (high precision), then only high-confidence recovery
(passive voice remap, a DETERMINER-introduced object NP "VERB the NOUN", subcat NOUN-mislabeled-clausal,
pronoun phi-features). Witness `verification/test_fd_harm_help_robust_extraction.py` 8/8 gates stress=1.0,
clean-no-regress=0.958, AND the corpus split.

**So: is the component maximized?** The DECISION is at its 0.958 ceiling and fully BF-derived; the EXTRACTION
gap is now closed on the stress constructions and VALIDATED on real corpus (passive 0->0.72, affecting recall
+0.05). **HONEST RESIDUAL:** corpus recall is 0.73 not 1.0 and precision 0.78 not 0.85 -- the remaining misses
are harder parse errors (raising/reporting "said to have been", long-distance passive subjects) and the
precision cost of the fallbacks. These are the proposed `predicate_argument_frontend`/`arc_parser`/coref diffs
(Q111); the deeper parser robustness is that cluster's program, but the harm/help-relevant extraction is now
measured, generalizing, and brain-foundational, not a 12-item claim.

## THE RIGOROUS MATHEMATICALLY-BF EXTRACTION FIX (implemented + witnessed)
From the signal trace, the fixable labeler third is implemented RIGOROUSLY -- reusing the substrate's BF
machinery, not hand rules (`experiments/exp_fd_harm_help_learned_extraction_v1.py`; witness
`verification/test_fd_harm_help_learned_extraction.py` 3/3):
1. **DETERMINISTIC VOICE LABELER CORRECTION** (`label_voice_correct`): an `nsubj` under a be/get-aux +
   past-participle verb is a PASSIVE subject (Bornkessel-Schlesewsky voice diathesis) -> relabel
   `nsubj:pass`. Fixes the labeler's biggest deterministic-recoverable error; lifts undergoer-label recall
   (0.7778->0.7817 on cap-600) with precision HELD. The general arc_labeler post-correction (helps every
   consumer). This is the proposed `hdlab.arc_labeler` diff.
2. **LEARNED PATIENT IDENTIFICATION via the frozen `argstruct_patient_ranker`** (Competition-Model logistic
   = Bayesian cue integration; reuse `predicate_argument_frontend._argstruct_learned_pick`): P(candidate is
   the patient) over cues {Matrix-Tree marginal, has_case, core_obj, frame_obj subcat, postverb, anim, ...}.
   This is the RIGHT obj/obl disambiguation -- the naive rule OVER-FIRED (precision 0.744->0.650); the
   learned cue integration does NOT (precision **0.779**, = the tuned hand rules). Its PROBABILITY doubles as
   the DETECTION gate (fire iff max P >= tau; threshold-robust 0.3-0.7).
harm/help routes through this (predicate, patient). Corpus: **recall 0.718 / precision 0.779** -- matches
the hand extractor but PRINCIPLED (learned ranker + deterministic voice), the correct DEPLOYMENT (reuse the
learned organ, don't island hand rules). This confirms the ~0.75 extraction ceiling is real via BOTH routes;
the residual is the POS (30%) + parser-head (36%) thirds -- upstream tagger/scorer clusters.

## SIGNAL-LOSS TRACE -- CORRECTS the earlier "the parser SCORER is the ceiling" claim
Traced WHERE the who-was-affected (undergoer) signal is lost, feeding each stage GOLD vs predicted on
UD-EWT gold (`experiments/exp_fd_harm_help_signal_trace_v1.py`; n=627 affecting undergoers, 1500 sents).
**The loss is DISTRIBUTED, not scorer-bound -- my earlier conclusion was wrong:**

| condition | undergoer recall | isolates |
|---|---|---|
| full pipeline (all predicted) | 0.7895 | -- (21% lost) |
| gold POS | 0.8581 | POS loss ~0.069 |
| gold heads | 0.8612 | parser-head loss ~0.072 |
| gold POS + gold heads (LABELER ceiling) | **0.9075** | the arc-LABELER loses ~0.093 GIVEN A PERFECT PARSE |

Per-lost-undergoer attribution: **POS 30% / parser-head 36% / arc-LABELER 33%** -- the scorer is only ~1/3.
The arc-LABELER (which I'd never isolated) is a co-equal loss, and its two errors GIVEN A PERFECT PARSE are
SYSTEMATIC + partly DETERMINISTIC: **nsubj:pass->nsubj** (passive voice not detected, 12/49 passives) and
**obj->obl** (a bare core object confused with an oblique, 34/580). A deterministic **VOICE** labeler
correction (be/get aux + participle => nsubj:pass; Bornkessel-Schlesewsky) is a clean net win (recall +,
precision held); the **CASE** correction (obl w/o preposition => obj) OVER-FIRES on genuine obliques
(precision 0.744->0.650) -- **obj/obl genuinely needs the learned subcat ranker** (`argstruct_patient_ranker.
frame_obj`, which the substrate ships for exactly this), not a naive rule. **KEY REALIZATION:** my extractor
already sat near the raw ceiling because its VOICE-REMAP was silently COMPENSATING for the labeler's
passive-mislabeling -- the right fix is the general labeler VOICE correction (helps every consumer), and the
POS/parser-head thirds are the tagger/scorer clusters. The signal loss is now FULLY UNDERSTOOD and attributed. **WHY the POS+parser thirds are NOT targeted-fixable (unlike the labeler's 2 systematic voice/case errors): the POS third is LONG-TAIL (16 distinct error classes, largest 7/40 -- PRON->SCONJ, NOUN->VERB, VERB->AUX...); the parser-head third is DIVERSE attachment errors (patient attached to a wrong VERB 20x / NOUN 16x / ADJ 6x). These are supervised-model errors needing RETRAINING (a BF distributional-category tagger + a constraint-based/graded parser), the tagger/parser clusters' core BF programs -- confirmed by measurement, not assumed.**

## THE THREE OPPORTUNITIES -- RESEARCHED + IMPROVED (mathematically BF, walls researched)
Pushed each named opportunity to a result, reusing the substrate's BF machinery and researching the walls:

1. **PARSER undergoer accuracy -> EXHAUSTIVELY RESEARCHED WALL (the scorer, not the decode/asset/marginals).**
   The parser labels **0.7895** of affecting-verb gold undergoers correctly (UD-EWT 1500, obj/nsubj:pass with
   head=verb) -- that is the hard ceiling. I measured EVERY tractable lever against it:

   | lever | undergoer-label recall | verdict |
   |---|---|---|
   | greedy decode (current) | 0.7895 | baseline |
   | **exact MST decode** (Chu-Liu/Edmonds, `graded_parser`) | 0.7911 | +0.0016 -- greedy already ~exact |
   | Matrix-Tree **marginals** (Koo 2007) | small (+0.0065 per substrate's own landing) | recovers some 1-best misses ("robbed the widow": mu[widow<-robbed]=**0.459** vs subj 0.015) but noisy at scale |
   | **richfeat** parser asset | 0.7799 | WORSE |
   | **mst_retrain** parser asset | 0.7225 | WORSE |
   | raw-arc-labeler extraction (bypass the CT adapter) | 0.719 recall | flat vs the confidence-ranked extractor |

   **CONCLUSION (SUPERSEDED by the SIGNAL-LOSS TRACE above -- see it first): the parser-head loss is only ~36% of the total; the arc-factored scorer's OWN levers are exhausted, but POS (30%) and the LABELER (33%) are co-equal, and the labeler's passive-voice third is deterministically recoverable.**
   Exact inference, the best alternative asset, the exact posterior marginals, and direct label-routing ALL
   fail to lift it materially -- the SCORES themselves are the limit. Lifting it requires RE-TRAINING the
   scorer with better features (a genuine arc_parser cluster program), NOT a targeted fix. The confidence-
   ranked extractor (0.727 recall / 0.779 precision) sits near the achievable operating point below that ceiling.

2. **COREFERENCE for pronoun patients -> BUILT (0.00 -> 0.917).** Reused `hdlab/coreference_resolver.py`
   (Grosz/Joshi/Weinstein Centering Theory + Binding Principle B, glass-box) to resolve a pronoun harm/help
   patient to its antecedent CHARACTER. phi-features already give the harm/help TYPE ("attacked him"=HARM);
   coref adds ATTRIBUTION (WHO). On 12 gendered 2-sentence passages, attribution rises **0.00 (surface
   pronoun) -> 0.917** (`exp_fd_harm_help_coref_pronoun_v1.py`; witness 2/2). REQUIRED a BF SUPPLY FIX: the
   resolver's gender gazetteer misses gendered ROLE nouns (widow/priest/actor/waitress), so I added a
   supplementary gendered-role-noun lexicon (a static offline asset; the proposed gazetteer extension,
   WordNet-hypernym-scalable) -- ablating it drops attribution 0.92->0.67 (load-bearing). RESIDUAL: an
   underspecified-gender competitor ("a soldier"... "her") needs a soft gender PRIOR -- a located boundary.

3. **RESULTING-STATE valence for `scratch` -> RESEARCHED WALL (WSD-bound; narrow win).** The resultative
   case ("beat him unconscious") is already handled (the composed cell reads the result-XP valence). For the
   BARE verb, I researched reading the RESULT-STATE participle's valence instead of the action verb's:
   Warriner mostly normalizes participles to the base lemma (scratched==scratch==-0.013), so it does NOT help
   `scratch` -- **the near-zero valence is genuine sense-conflation (scratch-itch vs scratch-skin), WSD-bound.**
   The ONE real win: verbs with a DISTINCT result-adjective entry -- "break" +0.025 (polysemous action) vs
   "broken" **-0.562** (the resulting STATE) -- so a result-state-adjective read helps break/torn-type verbs.
   The `scratch` bare case remains the `no_glass_box_verb_sense_disambiguation` program (and a bodily-integrity
   "any change to an intact body = adverse" prior was tested and REJECTED -- it over-fires on neutral contact
   like touch/tap/hold).

## DEEP DIVE: the role-extraction ceiling is PARSER-BOUNDED (learned-stack reuse investigated + measured)
Pushing the corpus recall (0.73) deeper: the substrate ALREADY ships the brain-foundational learned
role-assignment stack -- `hdlab/graded_role_assigner.py` (the Competition Model, MacWhinney & Bates: graded
parallel cue integration by LEARNED validities = the softmax/Bayesian posterior), `argstruct_patient_ranker`
(a logistic patient-identification model over cues {core_obj, postverb, locality, frame_obj, anim, ...},
measured 0.885 vs 0.8785 blanket, CI-sep), and `predicate_argument_frontend.structural_patient_pick` (the
reader's deployable extractor: labeled obj/nsubj:pass + precise voice remap + valency, learned-ranker
anchored; 0.745->0.831 on clean UD-EWT). I measured all of them head-to-head on the corpus undergoer task:

| extractor (affecting verbs, UD-EWT 1500) | recall | precision | passive | F1 |
|---|---|---|---|---|
| naive (dep-obj only) | 0.676 | 0.845 | 0.000 | 0.751 |
| **my confidence-ranked hand extractor** | 0.727 | 0.779 | 0.694 | **0.752** |
| Competition Model `hybrid_role_patient` (per verb) | 0.600 | 0.383 | 0.673 | 0.468 |
| reader `structural_patient_pick` (per matrix verb) | 0.671 | 0.499 | 0.592 | 0.573 |

**KEY REALIZATION (corpus-measured, honest):** the learned stack is superb at DISAMBIGUATION (which candidate
is the patient GIVEN there is one -- its 0.83-0.885 test) but, called per-verb, it OVER-FIRES because it always
returns a patient (no DETECTION gate) -- so it scores lower on the raw undergoer task than the confidence-ranked
extractor, whose dep-obj/subcat/determiner-NP presence IS the detection gate. **The task needs detection AND
disambiguation; neither the learned ranker alone nor a naive per-verb call gives both.** In the LIVE reader the
learned stack is properly GATED by event-detection, which is why the affect-routing fix (route harm/help through
the reader's already-gated (predicate, patient)) is the correct DEPLOYMENT -- it reuses the learned stack where
it is strong. My hand extractor is the DIAGNOSTIC that proved passives are recoverable + the validation harness;
its one genuinely novel contribution is the robust PASSIVE voice-remap (patient=surface subject, robust to the
tagger's advmod/VBD mistags) which fixes the cases the reader's stack still mis-binds ("comforted by a nurse"
-> patient=nurse). That belongs as a targeted `predicate_argument_frontend` passive-branch diff, NOT a wholesale
replacement.

**HONEST CEILING:** the raw undergoer extraction is ~0.75 F1, BOUNDED by the in-substrate parser (the arc_labeler
mislabels objects: "robbed the widow" -> widow=nmod, "was comforted" -> widow=advmod). Lifting it further is the
`arc_parser`/`arc_labeler` cluster's program -- e.g., marginals-aware undergoer recovery (`structural_patient_pick`
already accepts parse MARGINALS to reach the top-2 parse-miss, 0.8785->0.885) -- a genuine multi-organ undertaking,
correctly OUT of this problem's lane. The harm/help-relevant extraction is measured, generalizing, and reuses the
substrate's BF learned stack; it is not a hand-rule island.

## MATHEMATICALLY-BF REFINEMENTS + OTHER IMPROVEMENTS EVALUATED
Two heuristic elements were replaced with the brain's actual MATH (measured, not just reasoned):
- **Affectedness gate: boolean supersense sets + hand thresholds -> GRADED THEMATIC FIT** (McRae/Tanenhaus
  1998; Beavers 2011). affectedness = E[proto-patient degree | sense], the SemCor sense-frequency-weighted
  Beavers affectedness. One continuous quantity, engaged at a swept tau on a plateau (0.38-0.45). STRICTLY
  DOMINATES the boolean gate: GEN 0.812 -> 0.875 (recovers aid/assist) AND broad-neutral precision 1.000
  (0 leaks). Live 0.944 unchanged; witness 9/9.
- **POS DP-head fix: WordNet sense-COUNT heuristic -> BAYESIAN CATEGORY POSTERIOR** (`exp_pos_bayesian_
  category_v1.py`; MacDonald/Seidenberg probabilistic constraint satisfaction). P(NOUN|word,DP-head) =
  lexical prior odds x syntactic likelihood ratio (both estimated from UD-EWT; syn-LR=8.08, i.e. nouns head
  DPs 8x more than adjectives). At the Bayes-optimal margin, target recall 0.40 -> 0.70 (recovers civilian);
  the precision "cost" is largely nominalized adjectives (the rich/the accused: semantically nominal,
  UD-convention ADJ, downstream-harmless). Poor resists (strong adjective prior overrides the syntactic
  evidence). This is the mathematically-right version of the previous turn's sense-count guard.
- **OTHER DIRECTIONS EVALUATED (mathematically BF, not adopted this pass):** (i) CONTINUOUS harm/help
  magnitude = affectedness x |force-effect| x |endstate-valence| (Wolff 2007 vector resultant + Russell core
  affect) -- faithful and would give graded intensity for the downstream affect-intensity readout, but the
  DISCRETE harm/help decision is already at its ceiling (0.958) so it moves no current number; queued as the
  intensity upgrade. (ii) The ONE residual (`scratch`) needs the affective value of the RESULT STATE, not the
  verb's lexical valence (compositional resulting-state read / verb-sense-in-context) -- the deepest remaining
  BF step, tied to the `no_glass_box_verb_sense_disambiguation` program.

## PERFORMANCE vs THE BRAIN -- PER-STAGE CHAIN ATTRIBUTION (owner checklist item 6)
`experiments/exp_fd_harm_help_chain_attribution_v1.py` runs harm/help END-TO-END through the real reader on
a 24-sentence stress gold (social/emotional harm, rare role-noun patients, neutral perception) and
attributes every loss to the stage that caused it. A competent reader gets ~100%.

| pipeline | end-to-end harm/help acc | where the losses are (per stage) |
|---|---|---|
| STOCK (frame-list organ + stock tagger) | **0.458** | harm/help ORGAN abstains on social/emotional verbs (9/24), POS rare-noun mistag (3/24), valence coverage (1/24) |
| FIXED (graded-affectedness arithmetic + Bayesian POS) | **0.958** | valence coverage `scratch` (1/24) -- MATCHES the decision ceiling; the whole EXTRACTION gap (organ/POS/parse/binding) is closed |
| ORACLE-ARITHMETIC ceiling (gold verb + gold animacy) | **0.958** | the decision itself, given perfect inputs |

**Reading the chain:** the biggest single loss was the harm/help ORGAN itself (the frame-list stand-in
abstaining on every social/emotional verb -- 9 of 13 stock errors); the force-dynamic arithmetic removes
ALL of them. The rest were POS mistags on rare role nouns (medic/intern/civilian); the Bayesian POS
posterior removes them. The FIXED pipeline goes 0.458 -> **0.958**, which EQUALS the oracle-arithmetic
ceiling (0.958) -- i.e., the extraction chain (organ/POS/parse/patient-binding) now loses NO signal; the
sole residual is the decision's own **valence-coverage** boundary (`scratch`: near-zero Warriner valence,
the scratch-itch vs scratch-skin WSD -- needs a resulting-STATE valence read). The graded WSD gate works
live: watched/greeted/visited/phoned all correctly abstain. **CAVEAT: this 0.958 is on CLEAN ACTIVE
SVO; on harder realistic prose the same pipeline is 0.500 -- see REAL-PROSE PERFORMANCE above. The
extraction chain is at ceiling FOR SIMPLE SYNTAX, not for passives/pronouns/plurals.**

## UPSTREAM FIX PROTOTYPED (BF): the POS tagger, root cause of BOTH named walls
Tracing the two live misses to their root revealed BOTH reduce to ONE upstream error: the `pos_tagger`
(itself flagged NOT_BF -- an interim supervised perceptron) mistags rare/OOV common nouns with
adjectival-looking shape (medic, intern) as ADJ. That single POS error cascades -- the mistagged noun
cannot attach as the verb's object, becomes a spurious ROOT, and the patient / from-clause structure
collapses. **CORRECTION to my earlier attribution:** the "arc_parser from-clause attachment" wall was NOT
a parser defect -- it was DOWNSTREAM of the POS mistag on "medic" (the disk outranked my hypothesis).

**The fix (BF -- constraint-based lexical category resolution; Trueswell & Tanenhaus 1994; MacDonald et al.
1994; the DP hypothesis: a determiner projects a noun phrase whose HEAD is nominal, a documented top-down
category expectation).** A word tagged ADJ in DP-HEAD position (a determiner precedes with only ADJ/ADV
between, and no nominal follows in the phrase) is re-tagged NOUN **iff its stored lexical category prior is
dominantly nominal** (WordNet noun-vs-adjective senses = the mental lexicon's category knowledge). It
integrates the two constraints the lexicalist model says the brain does -- the syntactic FRAME + the
LEXICAL prior -- and leaves genuine nominalized adjectives (the poor/the rich) untouched.

**Measured (UD-EWT test, modern gold; `verification/test_pos_nominal_head_correction.py` 6/6):**
- GLOBAL UPOS accuracy 0.94198 -> 0.94208 (tiny -- the mistag is RARE in-distribution; honestly NOT a
  global POS win). The value is the DOWNSTREAM cascade.
- On the DP-head-ADJ TARGET population the lexical-prior fix beats the INFO-FREE random-retag control on
  BOTH axes: recall 0.40 vs 0.20, precision-error 0.042 vs 0.083 (the lexical prior is load-bearing).
- Harm/help patient-role nouns (medic/intern/tenant/refugee/...): 17/20 -> 19/20 correct NOUN.
- **DOWNSTREAM (the point):** "blocked the medic from saving the wounded" recovers HELP->HARM (POS fix ->
  medic binds as dobj -> from-clause attaches -> composed harm/help types PREVENT-a-good = HARM). And
  "A coworker bullied the intern" recovers HARM through the REAL reader **only when BOTH fixes are live** --
  the POS fix binds the patient (coworker->intern), the arithmetic types the social-harm verb (bully=HARM);
  neither alone. This is the owner's principle demonstrated: the wall clears only when every component in
  the chain -- upstream POS AND this organ -- is brain-foundational.

**Proposed hdlab diff (Q111):** add a `nominal_head_correction(tokens, upos)` post-pass to
`hdlab/pos_tagger.py` (or wrap `PosTagger.tag`) -- glass-box, WordNet lexical prior (admissible), no LLM.
Deeper: the POS tagger being NOT_BF (supervised perceptron) is a standing item; the fully-BF route is
distributional/unsupervised category induction (a separate program).

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
- **The affectedness WSD boundary is now CLOSED on precision, at a small recall cost.** The dominant-sense WSD
  guard (reliable-force-class + FrameNet-over-inclusion guard) takes BROAD-neutral precision 0.889 -> 1.000 (all
  4 leaks visit/call/see/mean fixed; live watched/greeted/visited/phoned abstain). The cost is recall on a few
  WEAK-valence social/communication verbs (aid/assist/swindle -> GEN 0.906 -> 0.812) whose affectedness needs the
  BENEFICIARY/argument distinction (aid a person = affected; visit a person = not) -- a context-driven WSD
  residual. NOTE: the LIVE 36-item metric is UNCHANGED (0.944) -- help survives; the trade is only on constructed
  weak-valence verbs.
- **`scratch`-class near-zero-valence verbs abstain** (Warriner valence ~= 0 for genuinely mild-harm verbs) -- a
  grounded-valence coverage boundary, reported.
- I did **not** land any hdlab change (Q111). The exact diff is below; strategy lands + re-verifies.

## THE EXACT hdlab DIFF (proposed; Q111 -- strategy lands)
In `hdlab/force_dynamics_valence.py`, replace the harm-frame-membership machinery with the arithmetic:
- **REMOVE**: `HARM_FRAMES`, `HARM_BACKOFF`, `_harm_verbs()`, `_harm()`, and the `nltk.corpus.framenet` import
  (the in-process read-path FrameNet enumeration -- defect D2).
- **ADD**: `from hdlab.affect_lexicon import AffectLexicon` (grounded endstate valence) + a cached WordNet
  supersense lookup + `import hdlab.psych_verb_frames` (subject-experiencer exclusion) for the affectedness gate
  (`is_affecting`: force-class OR affecting-first-supersense OR strong-valence+affecting-sense, minus
  subject-experiencer psych verbs) + `AFFECTING_SUPERSENSES` + `TAU_STRONG`.
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
- **`hdlab/pos_tagger.py` (NOT_BF) -- UPSTREAM WALL, now PROTOTYPED-FIXED (see UPSTREAM FIX PROTOTYPED above).**
  Rare/OOV nouns (intern/medic) mistagged ADJ -> patient binds to the agent / from-clause drops -> harm/help
  signal lost. A BF nominal-head correction recovers it (witness 6/6); the stacked live check shows the wall
  clears only with BOTH the POS fix and the organ fix. The deeper NOT_BF root (supervised POS) remains a
  separate program (distributional category induction). In the mega-cluster "the parser".
- **The verb-sense / literalness gate (`no_glass_box_verb_sense_disambiguation`).** The affectedness gate's
  context-free WordNet-supersense cut is the source of the betray/slander boundary; a context-aware sense pick
  (which the causation typer already lazily imports) would resolve harm-via-communication verbs.
- **`hdlab/causation_typing.py` (BF_SPIRIT, DORMANT).** It ALREADY computes the full force STRUCTURE
  (CAUSE/ENABLE/PREVENT + endstate) from the in-substrate parse, including the off-diagonal constructions
  (prevention-from, resultative, caused-motion). The richest landing is to compute harm/help ON TOP of its
  TypedCausalLinks (embedded-endstate valence from the complement clause) rather than the bare-SVO reduction --
  this is what unlocks the off-diagonal cells on REAL text, not just constructed items.
- **`hdlab/psych_verb_frames.py` (BF_SPIRIT, PINNED).** Newly REUSED by the affectedness gate (subject- vs
  object-experiencer split) -- the object-experiencer psych verbs (comfort/console/reassure) fire; the
  subject-experiencer ones (admire/envy/love/fear) are correctly excluded (object = stimulus, not affected).
- **`hdlab/affect_lexicon.py` (BF_SPIRIT).** The endstate-valence supplier; a resulting-STATE valence read (from
  an explicit resultative "beat him unconscious") would beat the verb-valence proxy on benefactive-negative verbs
  (surgery/dentistry: "cut"/"drill" negative valence but helpful) -- the one residual class the verb-valence proxy
  mislabels.

## SUBSTRATE INCORPORATION MANIFEST
- **INCORPORATE**: the `harm_help_arithmetic` decision (force-structure x grounded-valence + affectedness gate) as
  the body of `hdlab.force_dynamics_valence.harm_help`; the removal of the FrameNet harm-frame enumeration.
  Witness `verification/test_fd_harm_help_arithmetic.py` (9/9) gates it.
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
1. Land the proposed `force_dynamics_valence.py` diff (Q111) and re-verify `verification/test_fd_harm_help_arithmetic.py` (9/9).
2. PROTOTYPED (exp_fd_harm_help_composed_v1.py): harm/help composed on `causation_typing.py`'s parse recovers
   the off-diagonal cells on real prose (0.895 vs 0.579). Landing it needs the arc_parser to attach the
   `from`-clause reliably (blocked/stopped X from V-ing) -- route that residual to the parser cluster.
3. Fix the upstream patient-binding loss (rare-noun POS mistag) -- it caps harm/help recall independently (the
   `bullied` miss); route to the parser cluster.
4. Add a resulting-STATE valence read (resultatives) to resolve benefactive-negative verbs (surgical "cut"/"drill").
