---
priority: 4
review:
review_text:
---

# PROBLEM: with a COMPLETE referent-per-NP candidate set, the biggest remaining who-did-what loss is multi-direct-object COMPETITION (84% of residual errors) — the reader's proximity-primary selector picks the wrong one. The submission proved the fix is CONSTRUCTIONAL, not lexical: a Goldberg construction-aware selector (double-object → recipient; naming/object-complement → complement) lifts the ideal pipeline 0.873 → 0.913 (+0.040 CI-sep; +0.146 on the multi-DO subset), while a distributional selectional-preference re-rank adds only +0.007 n.s. OVER the constructions. BUILD that construction-aware SELECTOR as the who-did-what role pick over the referent-per-NP / expanded candidate set, glass-box, and prove it CI-separated with the info-free twin losing — or a located negative.

**slug:** `construction_aware_selector_for_multi_do_who_did_what_over_the_referent_set` — **opened:** 2026-09-03 by the strategy session, the READY selection successor of the owner-DONE `open_a_discourse_referent_for_every_np_not_just_coref_mentions` (its §6 explicitly scoped the selector as a SEPARATE successor; §"further improvement" #1 prototyped it 0.805→0.913). **status:** OPEN. Strategy lands any hdlab wire (Q111, default-off, witnessed). Glass-box, NO external LLM.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** 🧠 OPENING MOVE: how does the BRAIN do THIS? Name the structure + computation, replicate it. Mark PINNED vs OUR-INVENTION. A rigorous located NEGATIVE is a PASS if the brain's actual mechanism, faithfully built, is what failed. 📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## 1. THE PROBLEM IN PLAIN LANGUAGE
Once the reader sees every noun phrase as a candidate (the referent-per-NP fix), the hard remaining errors are sentences with TWO possible objects — "she gave the man a book", "they called the place a haven" — where it must pick which noun fills which role. Today it mostly picks by position (nearest noun after the verb), which is wrong on these. The submission found the brain's cue here is the CONSTRUCTION (the sentence pattern itself: a double-object frame means the first noun is the recipient; a naming/object-complement frame means the second is the complement), NOT how often that verb co-occurs with that noun. The job: build a selector that reads the construction and assigns the roles accordingly, and show it beats the positional pick on multi-object clauses.

## 2. WHY THIS ONE — the biggest measured remaining who-did-what lever, already de-risked
From the parent (through the live reader / ideal composition): referent-per-NP source 0.805; the parent's structural-DO/Competition-Model selector reaches 0.873; the PROTOTYPED construction-aware selector reaches **0.913 (+0.040 CI[+0.013,+0.074], +0.146 CI-sep on the multi-DO subset)** — 84% of the residual errors are multi-DO competition. KEY FINDING (reconciles the literature): the distributional selectional-preference re-rank adds only **+0.007 n.s.** over the constructions (though it beats its own shuffled twin +0.067) — so on canonical multi-DO clauses the "fit" the brain uses is CONSTRUCTIONAL, not lexical co-occurrence. This explains the parent's fenced grounded-fit negative. (Sources: parent SOLVED.md §"selection improvement" + `exp_referent_per_np_selection_improvement_v1.py` + `selection_improvement_construction_aware_2026-09-03.md`.)

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: Construction Grammar (Goldberg 1995) — the argument-structure CONSTRUCTION carries meaning independent of the verb (ditransitive → transfer/recipient; caused-motion; resultative; naming/object-complement); Competition Model cue integration (Bates & MacWhinney) with the CONSTRUCTION as a high-validity cue; predictive role assignment (Altmann & Kamide 1999). OUR-INVENTION: the exact construction detectors + how they compose with position + the tie-break (sweep). Mark PINNED vs OUR-INVENTION. Do NOT use lexical co-occurrence as the primary selector (measured near-zero marginal over constructions).

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive — from the parent):** ideal composition 0.873; construction-aware selector 0.913 (+0.040 CI-sep; +0.146 multi-DO); distributional re-rank +0.007 n.s. over constructions (but +0.067 over its own shuffled twin); 84% of residual = multi-DO competition; proximity-primary is the deviation from thematic-fit-dominant.
- **INFERRED (you must measure):** whether a glass-box construction-aware SELECTOR, wired over the referent-per-NP / expanded candidate set on the LIVE reader, raises effective who-did-what CI-separated over the current selector (structural-DO / proximity), with an info-free twin (shuffled constructions) LOSING and NO regression on canonical single-DO clauses; the residual + whether it needs the meaning channel (the genuine-ambiguity tail, gated/filed).

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: `python tools/substrate_map.py`, `python tools/reader_capabilities.py`; read IN FULL the parent `notes/problems/open_a_discourse_referent_for_every_np_not_just_coref_mentions/SOLVED.md` (the selection sections) + `selection_improvement_construction_aware_2026-09-03.md` + `IDEAL_who_did_what_composition_2026-09-03.md`; read `hdlab/graded_role_assigner.py` (the landed 8-cue Competition-Model pick), `hdlab/thematic_role_labeler.py` (cue-integration organ, currently wired for LABELING not SELECTION), `hdlab/situation_reader.py` (`_read_events_wired` role pick).
- Reproduce first-hand: the multi-DO subset where construction-aware beats proximity (+0.146) — the can-fail contrast.
- Inspect what you will REUSE: `experiments/exp_referent_per_np_selection_improvement_v1.py` (the prototype), `experiments/exp_referent_per_np_ideal_composition_v1.py`, `hdlab/graded_role_assigner.py`, `hdlab/np_head_reduce.py`.

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a glass-box construction-aware SELECTOR (Goldberg argument-structure constructions as high-validity cues over the referent-per-NP candidate set; NO external LLM) that raises the LIVE reader's effective who-did-what CI-separated over the current selector, with a shuffled-construction info-free twin LOSING CI-separated and NO regression on canonical single-DO clauses. Report CI half-width + null p95; lead with a CLEAN gold (the 19c who-did-what gold is ~76% oblique-contaminated). A rigorous located NEGATIVE — the construction cues do not net-help live beyond the structural-DO selector, with the named cause — is a FULL PASS. Strategy lands the Q111 wire (default-off, witnessed).

## ALREADY TRIED / DO NOT REDO
- Proximity-primary / structural-DO selection — the parent-landed baseline; this improves ON it, do not re-derive.
- A DISTRIBUTIONAL selectional-preference re-rank as the primary selector — measured near-zero marginal over constructions (+0.007 n.s.); the parent's grounded-fit selection was fenced. Do NOT re-open lexical-fit-as-primary.
- The meaning-fit selector for genuine ambiguity — GATED on the meaning channel (separate filed problem); the residual to oracle, not this problem.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE the parent's `exp_referent_per_np_selection_improvement_v1.py` (the prototype to promote), `hdlab/graded_role_assigner.py`, `hdlab/situation_reader.py`. Strategy lands any hdlab wire (Q111, default-off, witnessed). Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## DO NOT QUOTE
- Do NOT quote absolute numbers on the ~76% oblique-contaminated 19c gold — lead with the cleaned-DO instrument.
- Do NOT use lexical co-occurrence as the primary selector (measured near-zero over constructions).
