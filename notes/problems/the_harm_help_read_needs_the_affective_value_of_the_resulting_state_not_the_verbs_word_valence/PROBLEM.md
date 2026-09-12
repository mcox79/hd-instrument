---
priority: 14
slug: the_harm_help_read_needs_the_affective_value_of_the_resulting_state_not_the_verbs_word_valence
status: OPEN
review:
review_text:
---

# PROBLEM: the landed harm/help arithmetic reads the patient's outcome valence from the VERB'S word-level affect norm (Warriner), which conflates the verb's senses — "throttle" rates mildly positive (the engine sense), "batter" near-neutral (the food sense), "bludgeon" has no norm — so the brain-faithful organ now ABSTAINS on clear physical-assault verbs the retired word list caught (a recorded boundary). The brain values the RESULTING STATE the patient is left in (struck, strangled, injured), not the verb's lexical pleasantness. Build that read: the affective value of the verb's result state, from the substrate's own foundation assets, glass-box, and show it recovers the abstentions without re-introducing a verb list.

**slug:** `the_harm_help_read_needs_the_affective_value_of_the_resulting_state_not_the_verbs_word_valence` — **opened:** 2026-09-12 by strategy, at the pri-7 integration (notes/SIGNAL_FLOW_MAP.md §7; BRAIN_FOUNDATIONAL_AUDIT §2b 2026-09-12). A sense-level SYNONYM-valence backoff was tried by strategy the same night and WITHDRAWN: it turned batter/throttle/bludgeon into HELP (the synonym lemmas carry the same word-level sense conflation one step removed). **status:** OPEN.

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate, not the fastest green check.
> **THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure / circuit and the computation it performs, and replicate that OPERATION as exactly as you can — the FIRST move, not a tiebreaker.
> **YOU ARE ENABLED — AND EXPECTED — TO EXPLORE FAR AND WIDE.** Read the neuroscience; cross domains; if a MORE brain-foundational structure than this brief names emerges, submit THAT instead (say what is incompatible and why yours is more faithful).
> **A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
> **"CONVERGED" HAS A HIGH BAR.** Claim it only when you have (a) identified how the brain performs this computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL, and spaCy/GLUCOSE/MAVEN + any off-the-shelf parser/dataset/model are NOT brain-foundational — never reach for a convenient/easy tool without careful consideration** (curated norms / WordNet / VerbNet as static offline FOUNDATION assets are admissible SUPPLY; a verb LIST, a fitted classifier, or an external tool at inference is the defect).
> **🧩 ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS (owner 2026-09-10):** this is the endstate-valence ARM of the existing `hdlab/force_dynamics_valence.py` (`endstate_valence_sign` is the hook, today = word-level sign or abstain) — do NOT mint a new organ. Consult `BRAIN_STRUCTURE_CONSOLIDATION_AUDIT.md` Cluster 7/9 before adding anything.
> **A rigorous negative is a PASS** — but only if what failed was the brain's actual mechanism, faithfully built.
> **REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** (§2b 2026-09-12 pri-7 entry) for the systems you touch; put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale.
> **🧱 WALL-PUSH PROTOCOL (owner 2026-09-12):** before writing wall / ceiling / located negative / information limit / data-blocked / converged, read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` (the owner's pushes, verbatim) and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` (how ~60 declared walls were actually broken: trace upstream to the non-BF part; check the INPUT and the READOUT; oracle-ceiling probe; count don't narrate; check the floor + instrument; move the operating point; supply a missing computation source; find the existing organ / missing join / missing half of the model; change the gold to the ability). A wall is a trace + a stronger brain build, else a SPECIFIC board question.

> ## BRAIN-FOUNDATIONAL CHECKLIST (work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN — how does the BRAIN do THIS?** Outcome valuation (OFC/vmPFC value; amygdala) is over the STATE an agent ends up in, reached by simulating the event (embodied/situation simulation: Barsalou; Zwaan); the verb's lexical affect is only a cue to that state. Causative verbs lexicalise a RESULT STATE (Levin/Rappaport Hovav: "batter" → battered/injured; "throttle" → strangled; "heal" → healthy); the value of the result state is what the brain evaluates. Replicate THAT: verb → result-state predicate(s) → affective value of the result state for an animate patient.
> 2. **REUSE + ONE-STRUCTURE-ONE-ORGAN** — REUSE `force_dynamics_valence.endstate_valence_sign` as the hook, `hdlab/affect_lexicon` (Warriner) for state-word valence, the verb-frame supply (`verb_subcat_frames`, `psych_verb_frames`, FrameNet-derived `force_dynamics_lexicon` frames — the frame's RESULT/Outcome frame element names the state), WordNet verb glosses ("strike violently and repeatedly", "kill by squeezing the throat") and their `causes`/`entails` relations as the result-state source. All offline foundation assets; nothing fitted, no list.
> 3. **GENERALIZE — does it need to, and how does the brain?** Must serve every affecting verb the arithmetic gates in (not the four examples): the result-state value replaces the word-level sign wherever the latter is uninformative (|v| < 0.10 or absent), and should AGREE with it where both exist (a consistency check, not a second opinion).
> 4. **HIT A WALL → GO DEEPER, don't stop.** If the result-state words themselves are valence-uninformative for a slice, name the slice with a count; try the gloss-level read (the valence of the verb's definitional gloss content words, SemCor-weighted) before declaring a ceiling.
> 5. **OPTIMIZE BY EXACT REPLICATION** — copy the operation (state valuation); sweep the uninformative-valence threshold and the sense weighting; never adopt a number.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM** — MEASURE on (a) the solver's populations in `experiments/exp_fd_harm_help_arithmetic_v1.py` (P_HARM_FRAME, P_SOCIAL_HARM, P_NONPREVENT_HELP, P_NEUTRAL — precision on neutral must HOLD), (b) the retired backoff verbs (batter, bludgeon, wrench, throttle, stomp, clobber, wallop …) as the recovery set, (c) the LIVE board arm `affect_harm_help` (0.972 standing; must not regress) and the live witnesses `test_fd_harm_help_arithmetic`, `test_affect_reroute_*`, `test_board_state_closure_and_affect_harm_help`; info-free twin = result-state valences scrambled across verbs (must lose).
> 7. **ADJACENT COMPONENTS.** `occ_appraisal` (OCC emotion type from goal congruence) is the sibling appraisal check — do not merge; the `affected_entity` decision consumes harm/help downstream (measure it). The verb-sense-in-context program (`select_sense`) could pick the result state by context later — note, do not build.
> 8. **COMPLETION BAR.** `endstate_valence_sign` reads the RESULT-STATE value when the word-level norm is uninformative (glass-box, foundation-asset-derived, no list), recovers the abstaining assault verbs to HARM with neutral precision held, twin loses, board `affect_harm_help` ≥ 0.972 and `affected_entity` no-regress, all named witnesses green, registry tag + §2b AUDIT UPDATE — OR a rigorous located negative naming with a number which slice has no foundation-derivable result state and why.
>
> **(PHASE DIAGRAM.)** Threshold for "uninformative", sense weighting, gloss vs relation source — FREE to SWEEP; a wall "at this config" = move the operating point.
> **(FULL-STACK UPSTREAM.)** The decision feeds `context_grounded_valence` → the reader's affect fields → the `affected_entity` and `affect_harm_help` arms; ACCEPT downstream movement and measure it.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When the reader decides whether someone was helped or harmed, it now asks how the verb "feels" as a word. For a few verbs that feeling is misleading because the word has another meaning (throttle an engine, batter for cooking), so the reader says nothing where it used to say "harmed". The brain judges the state the person is left in, not the word. This problem builds that: work out what state the action leaves the person in, and how good or bad that state is.

## 2. WHY THIS ONE — the deep root, under the HARD 100%-BF gate
The owner's rule forbids re-adding a word list to recover the lost cases. The honest fix is the computation the brain performs (value the resulting state). It closes a recorded boundary on a live ability, it is small and well-scoped, and it is the same move the verb-sense program needs later.

## 3. MEASURED vs INFERRED
- **MEASURED (on disk, 2026-09-12):** word-level Warriner valence: batter +0.06, wrench −0.04 (uninformative), bludgeon none, throttle +0.14 (wrong-sense sign) → the organ abstains (batter/wrench/bludgeon) or would mis-sign (throttle, guarded by the threshold). Live arm 0.972 on the 36 gold; synonym-lemma valence backoff → HELP for batter/throttle/bludgeon (withdrawn).
- **INFERRED (to prove WITH A NUMBER):** that a result-state value derived from foundation assets recovers these to HARM with neutral precision held and no live regression.

## 4. ALREADY TRIED / DO NOT REDO
- Do NOT re-add a harm verb list or FrameNet harm-frame membership at inference (the retired NOT_BF stand-in).
- Do NOT average the valence of the verb's SYNONYM lemmas (tried 2026-09-12: wrong answers).
- Do NOT use a fitted classifier or any external model at inference.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read `hdlab/force_dynamics_valence.py` in full (the arithmetic, `endstate_valence_sign`, the withdrawn-backoff note), `notes/SIGNAL_FLOW_MAP.md` §3 and §7, the pri-7 `SOLVED.md` ("REAL-PROSE PERFORMANCE", "MATHEMATICALLY-BF REFINEMENTS"), `notes/RESEARCH_harm_help_and_selectional_math_2026-09-12.md`, `hdlab/affect_lexicon.py`, `hdlab/force_dynamics_lexicon.py`; run `python tools/substrate_map.py`.

## 6. THE BAR (can-fail; a rigorous located-negative naming the exact ceiling WITH a number is a full pass)
A glass-box result-state valuation arm inside `force_dynamics_valence` (foundation-asset-derived, no list) that recovers the abstaining assault verbs to HARM, holds neutral precision, loses to its scrambled twin, keeps `affect_harm_help` ≥ 0.972 and `affected_entity` no-regress with every named witness green — OR a numbered located negative.

## 7. FILES AND ENTRY POINTS
`hdlab/force_dynamics_valence.py` (`endstate_valence_sign`, `harm_help_arithmetic`), `hdlab/affect_lexicon.py`, `hdlab/force_dynamics_lexicon.py`, `hdlab/verb_subcat_frames.py`, `hdlab/psych_verb_frames.py`; `experiments/exp_fd_harm_help_arithmetic_v1.py` (populations + twin helpers); witnesses `verification/test_fd_harm_help_arithmetic.py`, `verification/test_affect_reroute_hdlab_tagger.py`, `verification/test_board_state_closure_and_affect_harm_help.py`; board arm `board_affect_harm_help_dimension` in `experiments/exp_situation_model_qa_modern_v1.py`.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT re-add a verb list or FrameNet-at-inference. Do NOT re-try synonym-lemma valence averaging. Do NOT use spaCy / any external LLM at inference.

## 9. STRATEGY LANDING 2026-09-12 — READ BEFORE STARTING (the first arm is LIVE; the remaining scope is below)
Strategy researched this wall the same night and LANDED the checklist's step 1-2 read as the result-state ARM of `force_dynamics_valence` (no new organ): WordNet-SENSE-keyed
VerbNet result/end-state predicates over the Patient, read over the verb's affecting animate-object senses, valued by the affect lexicon or the innate nociceptive sign; the
word-level norm is now the SECOND read. Asset `data/frontend_assets/verbnet_result_state_v1.json` (builder `tools/build_verbnet_result_state_asset.py`); witness
`verification/test_fd_result_state_arm.py` (15/15). Recovered: batter, bludgeon, pummel, club, throttle (+ clobber/wallop/thrash/whack agree); 31 formerly-abstaining verbs
decided; neutral precision held; twin loses; board gold held. Full numbers + the REJECTED routes (hypernym inheritance 0.65-0.75, synset-mate 0.75, gloss-first breaks harm-frame
verbs, gloss-fallback 0.81 measured NOT landed): `notes/RESEARCH_result_state_valuation_2026-09-12.md`. **Do not rebuild these.**

**REMAINING SCOPE (the bar now):** (a) 822/2926 affecting verbs still abstain (no foundation result state + weak norm) — wrench, maul, oppress, tend among the probe sets: find a
brain-faithful result-state source for them (VerbNet has NO positive result-state predicate; HELP still rides on the word norm), with a number per slice; (b) sense-IN-CONTEXT selection
of WHICH sense's result state applies (the `select_sense` program) rather than the animate-object-frame heuristic; (c) measure `affected_entity` downstream on real prose, not only gold.
A rigorous located negative with counts remains a full pass.
