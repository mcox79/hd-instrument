---
priority: 3
review:
review_text:
---

# PROBLEM: the reader assigns who-did-what by WORD ORDER, which is ~96% valid on canonical English but COLLAPSES on non-canonical clauses (passives, clefts, fronting) — exactly where 19c literary prose lives. On those clauses positional agent = 0.00 and animacy = 0.07, but GROUNDED MEANING already picks the agent at 0.43. The brain resolves this by the Competition Model: when the word-order cue is INVALID, the semantic/selectional cue decides. Build the grounded-meaning role cue into the live role competition so who-did-what holds where syntax misleads.

**slug:** `grounded_meaning_role_cue_for_non_canonical_who_did_what_where_word_order_misleads` — **opened:** 2026-09-05 by the strategy session (the non-canonical tail is the dominant who-did-what residual, and grounding is MEASURED to carry role exactly there). **status:** OPEN. Glass-box, NO external LLM. Strategy lands the Q111 wire.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** Iterate to the OPTIMAL brain-foundational solution; do NOT submit the first thing that clears. The OPENING MOVE is "how does the BRAIN actually do this?" — name the structure/circuit + replicate the OPERATION. A located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed. Run a 30-min deepening cron; cancel + submit only when the brain-mechanism bar is met AND nothing more of value remains.

> ## 🧠 BRAIN-FOUNDATIONAL CHECKLIST (work through IN ORDER; not done until every box holds)
> 1. **OPEN — how does the BRAIN do THIS?** Name the structure + computation; PINNED vs OUR-INVENTION. RESEARCH where unsure.
> 2. **REUSE — does an existing organ already do it?** Check `tools/substrate_map.py` / `hdlab/` FIRST.
> 3. **GENERALIZE — how does the brain generalize it?** Build for that.
> 4. **HIT A WALL? GO DEEPER.** A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, failed.
> 5. **OPTIMIZE BY EXACT REPLICATION.** Copy the computation, SWEEP the parameters.
> 6. **PERFORMANCE vs THE BRAIN.** Where do we lose signal? The mechanism-diff.
> 7. **ADJACENT COMPONENTS.** Map the neighbours — seeds the next problems.
> 8. **COMPLETION BAR.** COMPLETE + EXCELLENT + conveys the full benefit?

## 1. THE PROBLEM IN PLAIN LANGUAGE
"The letter was written by the clerk" — who did the writing? Word order says "letter" (wrong); meaning says "clerk" (right). The reader leans on word order, which works almost always in plain modern sentences but fails on passives and other inverted constructions — and old novels are full of them. The fix: when word order can't be trusted, let *meaning* (who plausibly does this action to what) decide, the way the brain does.

## 2. WHY THIS ONE — the measured non-canonical residual + grounding's proven locus
The who-did-what signal-loss study is decisive: on all transitive clauses word-order picks the agent at 0.961 (English SVO cue validity ~96%), but on NON-CANONICAL (passive) clauses positional = 0.00, animacy = 0.07, and **grounded meaning = 0.43** — meaning is the ONLY cue that carries role where syntax misleads (Competition Model: cue validity is conditional on construction). The reader's 19c corpus has far MORE non-canonical constructions than modern UD, so this tail is bigger on the actual reading material than the UD numbers show. This is the biggest who-did-what lever we have not built, and it is where grounding is proven to belong (role, not the attachment skeleton).

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: role assignment is a CUE COMPETITION (MacWhinney & Bates Competition Model; FLMP) — word order, morphology/voice, animacy, and SELECTIONAL FIT (grounded meaning: does this filler plausibly play this role for this verb — Pado/Resnik selectional preference; syntactic bootstrapping, Gleitman/Fisher) compete, each weighted by its CONDITIONAL validity. When the word-order cue is neutralized (passive/cleft/fronting), the semantic cue's relative weight rises and it decides. REUSE (do NOT re-derive): `hdlab/graded_role_assigner` + `hdlab/graded_competition.net_activation` (the LANDED cue-competition op the agent path already runs — add grounded selectional fit as a NEW self-gating precision-weighted cue), `hdlab/meaning_foundation` + the distributional meaning channel (the grounded vectors), `hdlab/animacy_lexicon`, `hdlab/relcl_resolver.precise_passive` (the voice detector that flags when word order is untrustworthy). Note the arc-labeler exploration's finding: the raw grounded vectors are near-COLLINEAR (cosine 0.92) and need WHITENING (contrast normalization) before the selectional-fit cue separates — whitening flipped the grounded control from losing to +0.020 on hard arcs.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** on non-canonical clauses positional agent 0.00 / animacy 0.07 / grounded 0.43; on canonical, position 0.961 (word-order dominant); animacy is real-but-subordinate (0.950 vs 0.886 scrambled); the raw meaning vectors are collinear (cos 0.92) and whitening is required for the cue to carry; the passive role markers are the catastrophic loss (`obl:agent` LAS 0.0588).
- **INFERRED (you must measure):** whether a whitened grounded selectional-fit cue, self-gated to fire when the word-order cue is low-validity (voice/construction-detected), lifts the LIVE who-did-what AGENT arm on the non-canonical slice CI-separated with a verb-shuffled / scrambled-meaning info-free twin LOSING and NO-regress on canonical clauses; the right precision weight (sweep, do not fix); whether it composes with `cm_agent` without perturbing canonical picks.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: understand ALL role organs (`python tools/substrate_map.py`) + read IN FULL: `swap_the_positional_role_assigner...` (the Competition-Model agent assigner + its cue framework), `the_agent_tie_wall...` (the structure cue added to the same competition), `consume_the_graded_pos_posterior...` (the structure-first patient + the animacy located negative), and the arc-labeler submission's sections H-O (the grounded-role-on-non-canonical measurement + the whiten root-cause/fix). Read `hdlab/graded_role_assigner.py`, `hdlab/graded_competition.py`.
- Reproduce first-hand: the non-canonical agent slice (positional 0.00 vs grounded 0.43) + the whitening effect.

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a whitened grounded selectional-fit role cue, self-gated by word-order cue validity (fires on non-canonical/passive clauses), landed into the live `graded_role_assigner` competition, lifting the LIVE who-did-what AGENT arm on the non-canonical slice CI-separated over the current reader, with a verb-shuffled/scrambled-meaning info-free twin LOSING and NO-regress on the canonical slice or any other dim. Report CI half-width + null p95; recompute floors per population. A rigorous located NEGATIVE — the faithful grounded role cue does not hold end-to-end (e.g. the whitened vectors still do not separate on real prose, with the number), naming the exact cause — is a FULL PASS.

## ALREADY TRIED / DO NOT REDO
- Do NOT re-run the located negatives: raw (un-whitened) grounded meaning ties its scrambled control on role/UAS (4× confirmed); animacy alone is subordinate (does not CI-separate who-did-what); lexical-PMI selectional preference HURTS (word-pair memorization is the wrong grain — the lever is CLASS/subcategorization-level, Klein&Manning 2003).
- Do NOT target the attachment SKELETON with meaning (a located negative — meaning's locus is ROLE, not head-attachment; the parse/attachment side is the SEPARATE parser problem, see COORDINATION).
- Do NOT re-solve the CANONICAL who-did-what (word order already wins there); this is the non-canonical tail only.

## COORDINATION (does NOT conflict with the in-flight substrate streamlining)
This is the ROLE side of the passive/non-canonical wall — an ADDITIVE cue to the already-live `cm_agent` competition (given the parse). Its COMPLEMENT is the PARSE side (the parser attaching `obl:agent` at all), which is the SEPARATE problem `distributed_contextual_representations_into_the_parser...` — cross-reference it; do NOT re-do parser attachment here. Uses the SAME `meaning_foundation` grounded vectors the meaning-wire touches, but as a ROLE cue in `graded_role_assigner` (a different consumer than `select_sense`). Prototype in `experiments/`; strategy lands the Q111 wire. No live-code overlap with the pass.

## FILES AND ENTRY POINTS
Prototype + measure in `experiments/` + `verification/`; the wire is `hdlab/graded_role_assigner.py` (add the grounded selectional-fit cue + its validity gate) + `hdlab/situation_reader.py` role routing. REUSE `hdlab/graded_competition.py`, `hdlab/meaning_foundation.py`, `hdlab/animacy_lexicon.py`, `hdlab/relcl_resolver.precise_passive`. Strategy lands the Q111 wire; fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## DO NOT QUOTE
- Do NOT quote a non-canonical role gain without the scrambled-meaning/verb-shuffled twin LOSING + NO-regress on canonical.
- Do NOT quote raw (un-whitened) grounded vectors as a working cue — they are collinear; whiten first (the measured requirement).
- NO external LLM (the invariant); grounded selectional fit uses the substrate's own meaning vectors, glass-box.
