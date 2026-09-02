---
priority: 1
review:
review_text:
---

# PROBLEM: the reader's PARSER (the glass-box shallow dependency / predicate-argument front end) is the DEFINITIVELY-MEASURED cross-task ceiling — but it is NOT one job, it is at least EIGHT, and a year of work proved that fixing one BREAKS or fails to help another. When the parse is correct, who-did-what patient selection is 0.989; the entire deficit to ~0.66 is the parser mislabeling or dropping the argument (the 35.2% "gold not attached to the verb" bucket), and the substrate's own `arc_parser` (0.515) LOSES to off-the-shelf spaCy `en_core_web_sm` (0.588, +0.073 CI-sep). Knowledge and integration are SATURATED — no selectional store / combiner / precision trick moves it, only a better parse does. Significantly improve the substrate's OWN glass-box parser so it serves ALL its downstream needs AT ONCE (owner: "we need to improve the parser significantly so it performs well for all tasks") — raising who-did-what toward spaCy CI-separated AND holding a UAS/LAS gain on UD-EWT AND compounding to a second task, WITHOUT regressing the competing needs (argument recall, lemma/POS, 19c robustness, the confidence distribution) — or locate precisely which need cannot be co-satisfied and why.

**slug:** `the_extraction_front_end_parser_is_the_cross_task_bottleneck_needs_a_significantly_better_parse` — **opened:**
2026-09-01 by the strategy session, lifted from the solver-drafted follow-on of the owner-DONE `the_selectional_event_store…register_native_corpus` (which quantified the parser as the sole cross-task lever) + the OWNER's explicit direction that the parser must "perform well for ALL tasks." **status:** OPEN — a BUILD problem (improve the substrate's glass-box parser, multi-objective). Strategy lands any hdlab wire (Q111, default-off, witnessed). Glass-box, NO external LLM at inference (the invariant; spaCy `en_core_web_sm` is a permitted glass-box REFERENCE target, NOT an LLM and NOT used at inference).

> **PRIORITY NOTE (RE-RANK PER THE OWNER):** filed at `1` — the HIGHEST-COMPOUNDING lever in the reader. THREE independent solver lines converge on it: who-did-what (this store submission: parse-correct→0.989, the rest is parser), the world-state register ("parser/extraction front-end = highest-COMPOUNDING lever — gates roles AND lemma/POS"), and p5 ("the sole lever is a better parser"). It gates who-did-what roles, world-state roles, AND the meaning channel's lemma/POS at once. Ranked above the north-star meaning-graph learner (now 2) because it gates that learner's LIVE payoff too (a graph grown on a bad parse inherits the errors).

> **⚠️ THE OWNER'S LOAD-BEARING CONSTRAINT (2026-09-01, why this brief is MULTI-OBJECTIVE): the parser serves MANY needs and improvements DID NOT TRANSFER — "what worked for one (richer content) did not necessarily help this last submission; all needs must be kept in mind."** A single-metric "raise UAS" brief WILL silently regress another need. The measured non-transfers you MUST respect are in §2/ALREADY-TRIED. Optimize the multi-objective in THE BAR, not one number.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** The mission is the most brain-faithful substrate.
> **🧠 OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN do THIS?** Name the structure + the computation, replicate that OPERATION as exactly as you can. It is the FIRST thing you do, not a tiebreaker after your tools plateau.
> **🚀 EXPLORE FAR + WIDE for the mechanism** — read the neuroscience, cross domains; if a MORE brain-foundational method conflicts with this brief, submit THAT instead (say why it is more faithful).
> **🧱 A SHARED WALL = GO DEEPER, not stop.** A wall is a fidelity gap to BUILD ACROSS, never a ceiling.
> **⛔ "CONVERGED" HAS A HIGH BAR** — claim it only with (a) the brain's mechanism identified AND (b) replicated + tested, or a SPECIFIC reason it cannot be. Exhausting engineering variations is NOT convergence.
> **🔁 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`):** each fire — gather high-value adjacent info (a control / curve / ablation / 2nd gold); enumerate what's LEFT + do it; MAP adjacent bottlenecks (name component + on-disk evidence + leverage) and EVALUATE each for brain-fidelity + optimization (seeds the next problem); hit a wall → run a FINER brain-foundational research drill, never stop. Implement → test (can-fail, strongest real floor, twin LOSING) → iterate. CANCEL + submit only when the mechanism bar is met AND the checklist yields nothing more.
> **A rigorous negative is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.**
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`**; inherit its PINNED/INVENTED verdicts; add an AUDIT UPDATE for any deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader works out who-did-what, who-has-what, and what-a-word-means all on top of ONE first step: read the sentence's grammar (which noun is the subject, which is the object, what the verb is). That step — the parser — is the weakest, most-shared part of the system, so its errors cap every ability at once. But it is not one job: at least eight different downstream abilities each need a DIFFERENT property of the parse, and past work repeatedly found a change that helped one and hurt another. Making it "tidier" bought precision but lost recall (and the true answer). The extra roles that fixed who-RECEIVED-what actively hurt who-DID-what. The word-knowledge store that helps when the grammar is broken hurts when it's right. The change that is the biggest win on modern text is a net loss on 200-year-old prose. And a parser that gets more single answers right still would not emit the "how sure am I" signal several parts depend on. So the task is to make the substrate's own grammar-reader significantly better **for all these needs at once**, not to push one accuracy number.

## 2. WHY THIS ONE — the measured cross-task ceiling, AND the measured non-transfers
**It is the ceiling, quantified:** parse-correct → who-did-what 0.989; the dominant loss is the 35.2% "gold not attached to the verb" bucket (attachment failure) + 9.4% verb-not-tagged + 2.9% passive-subject mislabeled `nsubj` not `nsubj:pass`. `arc_parser` 0.515 / `incremental_parser` 0.514 / spaCy `en_core_web_sm` 0.588 (+0.073 CI-sep) on the same structural rule — **we are below a small off-the-shelf model.** Integration is SATURATED (0.474→0.658 by composing a register-native store + the graded organs; no further trick moves it).

**THE EIGHT NEEDS (each wants a different property of the parse — the multi-objective):**
- **N1 who-did-what patient** ← attachment PRECISION on the object + correct VOICE label.
- **N2 argument RECALL** ← high recall / do-not-drop-arguments — the OPPOSITE axis to N1.
- **N3 world-state roles** ← recipient/source/goal PP roles + coref.
- **N4 meaning channel** ← correct LEMMA + tense-agnostic POS (not roles at all).
- **N5 non-canonical / passive / filler-gap** ← attachment + gap resolution where linear order LIES.
- **N6 register robustness** ← a parse that survives 19c/archaic syntax (subject-verb inversion).
- **N7 graded integrator organs** ← a CONFIDENCE / DISTRIBUTION over attachments (soft, not 1-best).
- **N8 agent/speaker on dialogue** ← quotative-inversion ("said Fred"→Fred=agent) + prefix-available incremental structure.
- (**N9 argument PRESENCE** — does the verb take an object at all — served by verb-subcategorization, not attachment.)

**THE MEASURED NON-TRANSFERS you must not re-break (the owner's point, with numbers):**
- **Recall vs precision are opposite:** the incremental left-corner builder wins id-F1 (+0.035) ENTIRELY via precision (+0.0998) bought with recall (−0.0928); wired live it regressed candidate recall −0.0365 AND patient acc −0.0145 (it throws away the true answer to stay tidy).
- **Richer PP/oblique roles helped world-state (recipient 0→0.33) but HURT patients −0.051** (a patient is the direct OBJECT; only 2.4% are PP-realized — obliques inject noise).
- **The selectional store helps on parse-BROKEN items (0.308 vs 0.145) but HURTS on parse-CORRECT items** — reliability-weighted, not always-on.
- **The biggest MODERN lever (use the structural parse, +0.096) is a NET LOSS on 19c (STRUCT −0.197 below linear position)** — the modern parser collapses on archaic syntax; there the store is the fallback that carries.
- **1-best accuracy ≠ the distribution:** a graded competition provably cannot beat its own argmax on accuracy (MAP theorem) — its value is the ENTROPY as a difficulty signal (AUC 0.646 vs the shipped 0.512). A 1-best win leaves N7 unserved unless the parser EMITS a distribution.
- **thematic-fit / plausibility as a role cue is regime-gated and mostly net-negative** (adds noise under a clean parse; the fix is a better PARSE, spaCy structural roles 0.9959 in isolation, not a richer fit vector — noun-side fit ceiling ~0.65 regardless of representation).
- **`arc_parser` is HARMFUL for filler-gap** (0.198 < info-free twin 0.305 — route AROUND it there) yet TIES the gold parse for LitBank who-did-what — one parser, opposite verdicts by task.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: comprehension builds structure INCREMENTALLY, left-to-right, under a bounded buffer (Now-or-Never, Christiansen & Chater 2016); structure-building and role-binding are SEPARATE but interacting pools (Matchin & Hickok 2020; Friederici 2011). The parse is NOT hard-committed — it is co-inferred with plausibility (constraint-based, McRae 1998; noisy-channel, Levy 2008 / Gibson 2013) and the parser maintains a DISTRIBUTION over attachments (graded, collapsed only when a task presses — hence N7). Register robustness comes from having READ the register (experience-based statistics), NOT a fixed grammar (hence gold target-register training, not self-training). This is why the faithful shape is position-DOMINANT + cue-OVERRIDE with a maintained confidence, not a 1-best oracle.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** arc/incremental 0.515/0.514 < spaCy 0.588 (+0.073 [+0.060,+0.086]); parse-correct→0.989; the 35.2%/9.4%/2.9%/2.4% signal-loss buckets; integration saturates 0.658; 19c collapse (both parsers FULL ~0.26, non-canonical HARD ~0.005); the in-substrate parser ladder count 0.60→hashed UAS 0.79→arc-eager+dynamic-oracle **dev UAS 0.8109**; global-beam note: local-argmax saturates ~0.81 and the gap to classical 0.86–0.89 is a SEARCH/global-training gap, not a feature gap. (Sources: `exp_error_decomposition_v1`, `exp_parser_headroom_v1`, `exp_brain_foundational_integrator_v1`, the `exp_depparse_*` lab, `notes/parser_global_beam_training_break_local_saturation_2026-07-23.md`.)
- **INFERRED (you must measure):** whether closing the arc_parser→spaCy UAS/LAS gap (via the substrate's OWN glass-box parser-training infra — arc-eager + global structured-perceptron/beam, NOT an LLM) recovers the +0.073 downstream AND holds on ≥1 second task (world-state role recovery or lemma/POS) WITHOUT regressing argument recall / POS / the 19c arm; whether emitting a confidence DISTRIBUTION (reuse `graded_competition`) lets the graded organs recover the confident-wrong bucket; whether GOLD target-register parse data (NOT self-training) fixes the 19c inversion collapse.

## ALREADY TRIED / DO NOT REDO (check `experiment_index` first — this area is dense)
- **Self-training for register/19c adaptation** — REFUTED (stalls). Use GOLD target-register parse data.
- **Richer selectional features / cleverer combiners / more integration tricks** — SATURATED at 0.658 (store-gate, agreement-gate, conflict-driven precision, soft-AND, generative DistMult, grounded-12d, animacy all non-levers).
- **The incremental parser as a patient selector / role-candidate source** — REFUTED end-to-end (precision-only; patient −0.0145, recall −0.0365).
- **Thematic-fit / selectional-preference as a role cue** — net-negative additively; regime-gated; noun-side fit ceiling ~0.65 regardless of representation.
- **Routing filler-gap through `arc_parser`** — HARMFUL (0.198 < random). Route around it (`relcl_resolver`).
- **A flat learned integrator replacing the cue cascade** — NET-NEGATIVE. The lever is ROUTING, not replacement.
- **Cue-FIRST parse replacement (discard spaCy)** — LOST on the ~90% canonical. Faithful shape = position-dominant + cue-override.
- **Richer PP/oblique extraction for PATIENTS** — HURTS −0.051 (patients are objects).
- **Beam DECODE on a locally-trained parser** — HURTS (label bias, UAS 0.75 vs 0.81); the fix is GLOBAL structured-perceptron TRAINING.
- **Surprisal-gated reanalysis of committed picks** — adds nothing; the recoverable gain is drop-filling MISSING args.
- **GloVe-300 / billion-token distributional fit for who-did-what** — TIES the coarse space (who-did-what is word-order-dominant, not fit-bound).

## VERIFY BEFORE YOU START (the disk outranks this brief)
- **FIRST STEPS (do these before proposing anything):** (1) understand ALL existing organs — `python tools/substrate_map.py`, `python tools/reader_capabilities.py`, skim `hdlab/`; (2) read IN FULL the SOLVED.md of the parser lineage that produced §2's non-transfers — at minimum `the_selectional_event_store…register_native_corpus` (+ its `PROPOSED_FOLLOWON_parser_is_the_cross_task_bottleneck.md`, `exp_error_decomposition_v1`, `exp_parser_headroom_v1`), `the_argument_parser_is_batch_where_the_brain_is_incremental`, `wire_the_incremental_parser_as_the_reader_extraction_front_end`, `grounded_role_assignment_via_verb_keyed_thematic_fit`, `the_relcl_parser_is_too_weak_for_filler_gap_role_assignment`, `role_assignment_is_untested_on_archaic_literary_prose`, `discrete_where_the_brain_is_graded_in_parsing_and_role_assignment`, `the_extraction_front_end_recovers_only_a_third_of_events_and_roles`, `wire_the_predarg_frontend_and_binder_into_the_live_reader`. Reuse, don't reinvent.
- Reproduce the baseline on your OWN recomputation: `arc_parser` 0.515 < spaCy 0.588 on the QA-SRL science who-did-what test; the parse-correct→0.989 decomposition.
- Read the parser-training lab: `experiments/exp_depparse_transition_arceager` (dev UAS 0.8109, the strongest in-substrate parser), `exp_depparse_global_beam_earlyupdate` (global training), `exp_depparse_transition_richfeat`/`valency_subcat`; `hdlab/arc_parser.py`, `hdlab/incremental_parser.py`, `hdlab/graded_competition.py`, and the landing-ready `verb_subcat` organ (`experiments/ref_verb_subcat_organ_v1.py` + its assets).

## THE BAR (MULTI-OBJECTIVE; can-fail; CI-separated; the info-free twin must lose)
PASS = the substrate's OWN glass-box parser, improved (via the in-substrate arc-eager + global-training infra, NOT an LLM), simultaneously:
1. **raises who-did-what** structural patient selection CI-separated over the current `arc_parser` (0.515) toward the spaCy level (0.588+) on the held-out QA-SRL science test, reported as **parse-attach PRECISION on ARGUMENTS**, not just overall UAS;
2. **holds a UAS/LAS gain** on the UD-EWT test set (the parse quality is real, not task-overfit);
3. **COMPOUNDS** — measure ≥1 SECOND downstream task (world-state role recovery OR meaning lemma/POS) and show the gain carries;
4. **does NOT regress the competing needs** — an explicit MUST-NOT-REGRESS check on: argument RECALL (N2), POS/lemma (N4), and the 19c arm treated as a SEPARATE sub-goal (do not claim a 19c win from a modern-only improvement);
5. reports the emitted **confidence/distribution** (N7) or states why it is out of scope.
A rigorous located negative — the in-substrate parser CANNOT be brought to spaCy level with the available infra, OR two needs are provably non-co-satisfiable — is a FULL PASS if it names which need, the number, and the mechanism. Report CI half-width + null p95 on every margin. Register-robustness (19c) via GOLD target-register data is an allowed SEPARATE sub-goal; self-training is refuted.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE (do not reinvent): `hdlab/arc_parser.py`, `hdlab/incremental_parser.py`, `hdlab/graded_competition.py` (the distribution output for N7), `hdlab/pos_tagger.py`, `hdlab/relcl_resolver.py` (route filler-gap here, not the arc parser), the `verb_subcat` organ (N9 precision cleanup, landing-ready); the parser-training lab `experiments/exp_depparse_transition_arceager` / `exp_depparse_global_beam_earlyupdate` / `exp_depparse_transition_richfeat` + their assets; spaCy `en_core_web_sm` as the glass-box REFERENCE target (NOT inference). Strategy lands any hdlab wire (Q111, default-off, witnessed). Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the parser is the cross-task ceiling; the multi-objective sub-goals and their non-transfers).

## DO NOT QUOTE
- Do NOT quote 0.658 as a who-did-what ceiling — it is the INTEGRATION ceiling at the CURRENT parser; the parser is what caps it.
- Do NOT claim the incremental parser is worse in general — it is better at argument RECALL (F1 +0.035) but position-like for PATIENT selection; the deficit is attachment PRECISION + relation LABELS.
- Do NOT optimize UAS alone — a UAS win that regresses recall / POS / the 19c arm is a FAIL by THE BAR, not a pass.
- Do NOT use an external LLM as the parser or the trainer (the invariant). spaCy `en_core_web_sm` is a glass-box reference target only, never called at inference.
