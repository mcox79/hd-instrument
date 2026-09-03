---
priority:
review: EXCELLENT
review_text: INTEGRATED 2026-09-03 (reverified 45/45 first-hand). SOLVED (NP-head chunker) + brain-faithful located negative (case cue = the Competition Model's own prediction, 0/669 availability). THE high-value structural fix: reducing candidates to their NP head lifts EVERY who-did-what consumer +0.20 (0.683->0.888), the full stack +0.30, +0.35 end-to-end; at/above the 19c parse ceiling (spaCy 0.9297 < ours 0.9806). Q111 WIRE LANDED default-off at both sites the solver proved -- the shared hdlab/np_head_reduce helper + np_head_reduce flags on the primitives (resolve_patient/hybrid_role_patient/competition_pick/route_predicate_arguments) AND on SituationReader (positional noms-reduction + router pass-through). Witness 3/3; reader default-off byte-identical, flag-on fires. Flip-default-ON = a separate owner decision; the ~20 output organs must re-validate on the new outputs. 22% coverage gap filed separately.
---

# PROBLEM: powering the cleaned 19c who-did-what gold PROVED the patient-selection residual is 89% STRUCTURAL, not semantic — position already gets 0.918 on clean direct objects (English is word-order-dominant) and an NP-head chunker lifts it +0.043 CI-separated to ~0.981, while thematic-fit selection value is exactly 0; so build the glass-box NP-HEAD CHUNKER (compound + genitive) and the morphological CASE cue (measured ABSENT, cheapest, better preserved in 19c) into the reader's role assignment, raising clean 19c who-did-what selection CI-separated over the position floor with the info-free twin LOSING — or a located negative naming the structural ceiling.

**slug:** `the_who_did_what_selection_residual_is_structural_np_head_chunking_and_case_not_meaning` — **opened:** 2026-09-02 by the strategy session, lifted from the owner-DONE located-negative `the_19c_who_did_what_lever_is_agent_composed_thematic_fit_on_a_cleaned_gold` (which powered the cleaned gold and REFUTED composition-as-selection, then decomposed the residual: 89% structural, measured levers A1/A2). **status:** OPEN — a small glass-box STRUCTURAL build (chunker + case cue), NOT a meaning-store or parser-retrain task (both refuted). Strategy lands any hdlab wire (Q111, default-off, witnessed). Glass-box, NO external LLM at inference (the invariant).

> **PRIORITY NOTE:** filed at `2` — the MEASURED, de-risked, non-representation who-did-what lever (A2 chunker +0.043 CI-sep, A1 case cue cheapest), separate from the north-star meaning representation at 1. A clean, bounded win.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** The mission is the most brain-faithful substrate.
> **🧠 OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN do THIS?** Name the structure + the computation, replicate that OPERATION as exactly as you can. It is the FIRST thing you do, not a tiebreaker.
> **🚀 EXPLORE FAR + WIDE for the mechanism** — read the neuroscience, cross domains; if a MORE brain-foundational method conflicts with this brief, submit THAT instead (say why it is more faithful).
> **🧱 A SHARED WALL = GO DEEPER, not stop.** A wall is a fidelity gap to BUILD ACROSS, never a ceiling.
> **⛔ "CONVERGED" HAS A HIGH BAR** — claim it only with (a) the brain's mechanism identified AND (b) replicated + tested, or a SPECIFIC reason it cannot be.
> **🔁 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`):** each fire — gather a high-value control/curve/ablation/2nd-gold; enumerate what's LEFT + do it; MAP adjacent bottlenecks + EVALUATE each for brain-fidelity + optimization; a wall → a FINER research drill, never stop. Implement → test (can-fail, strongest real floor, twin LOSING) → iterate.
> **A rigorous negative is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.**
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`**; inherit its PINNED/INVENTED verdicts; add an AUDIT UPDATE for any deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The just-finished investigation cleaned the old-prose "who did what" answer key and proved that picking which noun the verb acts on is a GRAMMAR-STRUCTURE job, not a meaning job: the plain "noun right after the verb" rule already gets about 92% right, exactly the way the brain handles English word order, and the few remaining misses are almost all about grouping words into the right noun-phrase ("the blacksmith's hammer" — is the argument "hammer" or "blacksmith?") and about the little word-endings that old prose still marks. Chunking the noun phrase correctly was measured to add a real, clean four points (to ~98%). So the job is two small, faithful pieces: a noun-phrase-head chunker (handle compounds and possessives) and a word-ending (case) cue that old prose preserves — wired into how the reader assigns roles.

## 2. WHY THIS ONE — a measured, de-risked, cheap structural win
The parent decomposed the cleaned-gold residual: 89% is STRUCTURAL (NP-head chunking), only ~11% semantic, and thematic-fit selection value is exactly 0 in this regime. The NP-head chunker was measured at +0.043 CI-sep (→0.981); the morphological case cue is MEASURED ABSENT from `graded_role_assigner` and is the cheapest lever (better preserved in 19c than word order in some constructions). This is the who-did-what selection cap that is NOT the meaning representation (that is the north-star at 1) — a clean, orthogonal, bounded build.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: comprehension segments the input into CONSTITUENTS and identifies each phrase's HEAD before role assignment (constituent structure; the parser's chunking stage). Role assignment is CUE-BASED (Competition Model, Bates & MacWhinney 1989): word order and morphological CASE are competing cues weighted by their validity in the language/register — English weights word order highly, but case is a high-validity cue where marked, and older/literary registers preserve more case marking. Mark PINNED vs OUR-INVENTION: NP-head identification + cue-based role competition (order + case) = PINNED; the specific chunker rules / case-cue lexicon / cue weights = OUR-INVENTION-under-test.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive — from the parent):** on the CLEANED 19c direct-object gold (n=669, precision 98.5%), nearest post-verbal = patient 0.918 (position dominates); an NP-head chunker lifts selection +0.043 CI-sep → 0.981; thematic-fit selection value = 0 (best w_fit = 0.0); the residual is 89% structural, ~11% semantic; morphological case is MEASURED ABSENT from the role assigner. (Sources: `exp_19c_composed_cleaned_gold`, `exp_19c_whodidwhat_residual_taxonomy`, `verification/test_19c_composed_cleaned_gold.py` W19.)
- **INFERRED (you must measure):** whether an NP-head chunker (compound + genitive) + a morphological case cue, wired into `graded_role_assigner`, lift clean 19c who-did-what patient selection CI-separated over the position floor (target ~0.98) with an info-free twin LOSING; whether the case cue adds ORTHOGONAL value over the chunker (or is redundant); whether the gain holds on held-out docs and does not regress modern.

## ALREADY TRIED / DO NOT REDO (check `experiment_index` first)
- **Composition / thematic-fit as the SELECTOR** — REFUTED at power (value = 0 in this word-order-dominant, all-active regime). Do NOT re-open a meaning store for SELECTION (it is real for PREDICTION — a separate follow-on).
- **Parse/POS-data acquisition, PP-attachment, register tagging** — refuted by the grandparent (`register_native_parse_and_pos...`). Not the lever.
- **A position-ambiguous / non-canonical 19c gold to expose the thematic-fit regime (A3)** — the data is ABSENT and an auto-build is BLOCKED by 19c parser robustness (measured). Do NOT sink time into building it here; note it as the boundary.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- **FIRST STEPS:** (1) understand ALL organs — `python tools/substrate_map.py`, `python tools/reader_capabilities.py`, skim `hdlab/`; (2) read IN FULL the parent `notes/problems/the_19c_who_did_what_lever_is_agent_composed_thematic_fit_on_a_cleaned_gold/{SOLVED.md, BRAIN_MECHANISM_DRILL_*.md}` (the residual taxonomy + the A1/A2 measurements); (3) `python tools/before_you_start.py "np head chunker case cue who did what selection"`.
- Reproduce on your own recompute: the 0.918 position floor + the +0.043 chunker lift on the cleaned gold (the can-fail target).
- Inspect what you will REUSE: `hdlab/graded_role_assigner.py` (where the chunker + case cue land), the cleaned-gold builder `experiments/exp_19c_composed_cleaned_gold.py`, `hdlab/pos_tagger.py` (case/morph features).

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = an NP-head chunker (compound + genitive) + a morphological case cue in the reader's role assignment (glass-box, NO LLM) that lifts clean 19c who-did-what patient selection CI-separated over the nearest-post-verbal position floor (target ~0.98) on held-out cleaned 19c direct-object gold, with an info-free twin (shuffled chunk boundaries / shuffled case) LOSING CI-separated, and NO modern regression. Report CI half-width + null p95; recompute the floor on the same population. A rigorous located NEGATIVE — the chunker/case cue cannot be built glass-box above the position floor, with the reason — is a FULL PASS. If wired: a live 19c who-did-what lift through the reader.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE: `hdlab/graded_role_assigner.py`, `hdlab/pos_tagger.py` (morph/case features), the cleaned-gold builder `experiments/exp_19c_composed_cleaned_gold.py` + `exp_19c_whodidwhat_residual_taxonomy_v1.py`. Strategy lands any hdlab wire (Q111, default-off, witnessed — a default-off chunker/case path on the role assigner). Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## DO NOT QUOTE
- Do NOT quote a thematic-fit/composition SELECTION gain — it is 0 in this regime (refuted at power).
- Do NOT quote the parent's "+0.158 over position" — that beat a WEAK farthest-noun floor; the real floor is nearest-post-verbal 0.918.
- Do NOT re-open parse/POS-data or PP-attachment — refuted.
- Do NOT use an external LLM for chunking or role assignment (the invariant); a glass-box chunker + case lexicon is the deliverable.
