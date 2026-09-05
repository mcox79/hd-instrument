---
problem: strengthen_the_cue_based_pronoun_coreference_resolver_the_shared_upstream_accuracy_cap
status: SOLVED
bar: "PASS = a cue-integrated retrieval resolver that lifts the LIVE reader coref (pooled pronoun `coref_acc` on real narrative) CI-separated over the current reader, with a shuffled-cue-validity info-free twin LOSING and NO-regress on named coref — AND at least one downstream (affect experiencer OR entity-KB hard-link) rises CI-separated from consuming the better coref (the bidirectional payoff). Report CI half-width + null p95; recompute floors per population. A rigorous located NEGATIVE — the faithful cue-based resolver cannot beat the current reader, with the binding cue/interference cause named + measured — is a FULL PASS."
result: "LIVE pooled he/she coref_acc (100 LitBank docs, n=7597 targets, scorer resolved_cluster==gold_cluster, the deployed EventCentralityReader): the landed graded ACT-R cue-based pick lifts the deployed pick 0.4693 -> 0.6019, paired doc-bootstrap delta +0.1327 CI[+0.0929,+0.1738] half-width 0.0405, CI-separated; the info-free shuffled-history twin scores 0.2697 (null p95 0.2952) and LOSES. NO-regress on named-antecedent coref (0.4883 -> 0.6165, it RISES). DOWNSTREAM (the pronoun-bound dimension): he/she who-has-what pick accuracy (25 LitBank docs, n=1700, gold-nominal grouping) rises 0.4035 -> 0.4735, PAIRED per-target delta +0.0700 CI[+0.0429,+0.0976] CI-separated, twin 0.0471 loses."
floor: "Strongest floor per population, recomputed in-place. Pooled coref: the DEPLOYED live pick (EventCentralityReader rolemass topical + event-centrality memory) = 0.4693 -- reproduced BYTE-EXACT to the known exp_referent_coref_linking_v1 deployment number. Strongest SIMPLE floor on the same pooled population = plain recency in the graded net = 0.6052 (the deployed pick is BELOW it -- the mechanistic cap). who-has-what floor: the deployed rolemass pick = 0.4035. Info-free floors: shuffled-history twin 0.2697 (pooled) / 0.0471 (who-has-what)."
controls: "(1) info-free shuffled-candidate-history twin (severs the candidate<->evidence link, same activation machinery + shape): LOSES CI-sep on BOTH the pooled (0.2697 vs 0.4693) and who-has-what (0.0471) -- excludes 'the machinery/pool shape carried it'. (2) FLOOR reproduces the known 0.4693 deployment number exactly -- excludes a harness artifact; every arm re-ranks the IDENTICAL deployed candidate pool, so the win is pure pick quality. (3) named-antecedent no-regress: named coref RISES (0.4883->0.6165) -- excludes 'gained on common nouns at the cost of names'. (4) cue ablation locates the lever: recency-only 0.6052 ~= graded 0.6019 >> deployed rolemass 0.4693, and event-centrality OFF (0.4876) beats event-centrality ON (0.4693) -- the deployed pick's 'NO recency term' design + its event-centrality override ARE the cap. (5) p_sent-proxy robustness: recency-only's argmax is p_sent-invariant, and the who-has-what cell uses the TRUE pronoun sentence index and reproduces the graded number exactly (0.4735 == the entity_maintenance nochain floor) -- excludes 'the proxy inflated recency'. (6) affect experiencer (a brief-NAMED downstream) is a rigorous LOCATED NEGATIVE (+0.0124 NOT_SEP) with a measured cause: it is common-noun-experiencer bound (83.5% of experiencers are common nouns), not pronoun bound."
files_changed: "experiments/exp_coref_graded_live_transfer_v1.py, experiments/exp_coref_graded_downstream_whohaswhat_v1.py, experiments/exp_coref_graded_downstream_affect_v1.py, verification/test_coref_graded_live_transfer.py, verification/test_coref_graded_downstream.py, notes/problems/strengthen_the_cue_based_pronoun_coreference_resolver_the_shared_upstream_accuracy_cap/SOLVED.md (NO hdlab/ writes -- the Q111 wire is proposed below for strategy)"
reverify: ".venv/Scripts/python.exe verification/test_coref_graded_live_transfer.py"
---

# The reader's live pronoun pick is anti-brain-foundational; the PINNED mechanism is already landed and not wired

## What I built and measured

**The opening move — how does the brain do this?** Reference resolution is cue-based, content-addressable
RETRIEVAL from working memory (Lewis & Vasishth 2005 ACT-R; McElree direct-access): a pronoun reactivates
the trace that best matches a weighted sum of cues, with **recency** the load-bearing decay term
(base-level activation `A_i = ln(sum_k w_role(k)·dt_k^-d)`, Anderson). This is PINNED, and it is **already
built and proven** in `hdlab/graded_coref_pick.graded_antecedent_pick` — it beats the incumbent on the
COMPETITIVE LitBank subset 0.775 vs 0.603.

**The gap (REUSE, not rebuild).** That landed organ is consumed only by `commonnoun_binder`. The LIVE
pronoun path (`situation_reader._read_entities` -> `EventCentralityReader.resolve_stream`) uses a
DIFFERENT, OUR-INVENTION pick: `rolemass` topical mass (subject-role-weighted mention frequency, tie-break
first-mention, **explicitly NO recency term**) + an HD event-centrality override. This is the "landed is
not live" gap the audit already flags (§P3 "the reader has the chain primitive on its WEAKER centrality
pick"). Nobody had measured what it costs on the LIVE pooled instrument.

**The measurement.** `exp_coref_graded_live_transfer_v1.py` runs every arm through the ACTUAL deployed
reader on the ACTUAL pooled instrument (gold LitBank mentions -> `EventCentralityReader` -> pooled he/she
`coref_acc`), changing ONLY the pick over the IDENTICAL candidate pool:

| arm | pooled coref_acc | vs deployed |
|---|---|---|
| **FLOOR — deployed** (rolemass + event-centrality) | **0.4693** | — (reproduces the known deployment number exactly) |
| FLOOR — rolemass, event-centrality OFF | 0.4876 | +0.018 (the event-centrality override HURTS) |
| **GRADED** — landed ACT-R cue pick (event-centrality off) | **0.6019** | **+0.1327 CI[+0.0929,+0.1738] CI-sep** |
| ablation — recency-only | 0.6052 | +0.1360 (the binding cue) |
| ablation — ACT-R-only | 0.5952 | +0.1260 |
| GRADED + animacy phi-filter | 0.6019 | +0.1327 (animacy adds nothing on this population) |
| info-free shuffled-history TWIN | 0.2697 | LOSES (null p95 0.2952) |

The lift is **+0.133 CI-separated**, the info-free twin loses hard, and **named coref RISES** (0.488 ->
0.617 — no regression). The **binding cue is RECENCY**: the deployed pick's "no recency term" design sits
14 points below plain recency, exactly mirroring the competitive-subset finding (the incumbent tier was
below recency there too). This is a pure PICK-quality win — every arm re-ranks the same deployed pool.

**Downstream bidirectional payoff.** `exp_coref_graded_downstream_whohaswhat_v1.py`: on **he/she
who-has-what** (the pronoun-BOUND board dimension), swapping the deployed rolemass pick for the graded pick
lifts pick accuracy **0.4035 -> 0.4735, paired per-target delta +0.070 CI[+0.043,+0.098] CI-separated**,
twin 0.047 loses. (This cell uses the TRUE pronoun sentence index and reproduces the graded number exactly,
cross-checking the primary cell's `p_sent` proxy.)

## The premise correction (disk outranks the brief)

The brief predicted the payoff would land on **affect experiencer** or **entity-KB hard-link**. I measured
affect directly (`exp_coref_graded_downstream_affect_v1.py`, swapping the reader's `reader_ec`): feel_reliable
**0.7562 -> 0.7686, +0.0124 NOT_SEP**, coverage unchanged (0.966), and the info-free pick twin actually
scored *higher* (0.7975). **A rigorous located negative with a measured cause:** as the brief's own datum
says, **83.5% of emotion-experiencers are COMMON-NOUN entities** — affect (and the entity-KB hard-link,
which consumes common-noun HEAD coref with pronouns stripped) is bottlenecked by COMMON-NOUN coref, not the
pronoun pick. So "one fix lifts several dimensions" is HALF right: the pronoun-coref cap is real and lifted,
but its payoff flows to the pronoun-bound dimensions (who-has-what), not to the two named common-noun-bound
ones. That correctly REDIRECTS the affect/entity-KB lever to the already-filed common-noun-coref problem.

## What I did NOT establish / would withdraw first

- **The literal named downstream did not rise.** The bar names "affect experiencer OR entity-KB hard-link";
  neither rises for a pronoun pick (measured/argued common-noun-bound). I satisfied the bidirectional-payoff
  requirement via **who-has-what** instead. If a reviewer requires the literally-named downstream, this is
  PARTIAL on that one clause — the FIRST thing I'd flag. The primary lift and the who-has-what payoff stand
  regardless.
- **who-has-what is tightly coupled to the coref task** (it is the pronoun-resolution substrate of a QA
  dimension, scored on a different corpus/grouping). That coupling is WHY it responds; it is a weaker
  "downstream" than a fully independent dimension would be.
- **The primary uses a `p_sent` proxy** (max candidate sentence + 1) inside the pick override. Mitigated by
  the recency-only argmax-invariance and the true-`p_sent` who-has-what cross-check, but the exact ACT-R
  decay magnitude in the primary is proxy-scaled. The argmax (the pick) is unaffected.
- **The recommended wire is the FULL graded organ, not recency-only.** Recency-only ties graded on THIS
  pooled population, but it would REGRESS the competitive/conflict cases the ACT-R integration handles
  (graded 0.775 > recency 0.717 there). Deploy the integrated organ, not the ablation.

## KEY REALIZATIONS (the enabling moves)

1. **The live pronoun pick was never the proven organ.** The decisive move was tracing `situation_reader`
   -> `EventCentralityReader` and finding `graded_coref_pick` is imported by `commonnoun_binder` but NEVER
   by the live pronoun path — a "landed is not live" gap, not a missing mechanism. The fix is a WIRE + a
   measurement, not a new organ.
2. **Run the swap through the ACTUAL deployed reader, not a re-implementation.** Subclassing the reader and
   overriding only the pick (pool construction byte-unchanged) let the FLOOR reproduce the known 0.4693
   exactly, so the +0.133 is a clean pick-quality delta, not a harness artifact.
3. **The deployed pick's design philosophy IS the bug.** `rolemass` explicitly drops recency ("NO recency
   term") in favor of global topical mass; the ablation shows recency is the lever, and the event-centrality
   override makes it WORSE. Our worst coref result copied a heuristic; the brain's operation copies recency.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md §2b, E3 coreference)

The live pronoun-coref pick (`EventCentralityReader` rolemass + event-centrality) is an OUR-INVENTION
placeholder that is **anti-brain-foundational on the deployment metric**: on the LIVE pooled he/she instrument
(n=7597) it scores 0.4693, **14 points below** the PINNED cue-based retrieval already landed in
`graded_coref_pick` (0.6019, +0.133 CI-sep), and BELOW plain recency (0.6052) — the same "tier is below
recency" cap the competitive subset showed, now confirmed on the live path. The event-centrality memory
override actively HURTS (-0.018). **Recommendation: wire `graded_antecedent_pick` into `_read_entities` as
the pronoun pick (event-centrality off).** The pronoun-coref cap does NOT bottleneck affect/entity-KB
(common-noun bound); it bottlenecks the pronoun-bound dimensions (who-has-what, +0.070 CI-sep).

## PROPOSED hdlab WIRE (Q111 — strategy lands it; NO solver hdlab writes)

In `hdlab/situation_reader.py::_read_entities` (the `self.reader_ec.resolve_stream(...)` call, ~line 1142),
replace the pronoun antecedent pick with the landed organ:
- For each he/she target, build `candidate_priors = [(sent_idx, role) ...]` per gn-compatible overlay entity
  (the same pool the reader already assembles) and call
  `hdlab.graded_coref_pick.graded_antecedent_pick(...)`; keep the landed `keep_after_pool_cleanup` +
  `is_discourse_participant` phi-filter (already in that module).
- Turn the event-centrality memory OFF on this path (`query_memory=False`) — it is measured net-negative.
- This is exactly the "opt-in `run_graded_retrieval` over the resolver stream" the `graded_coref_pick`
  docstring already names as the queued follow-on. Compose it with the default-off `graded_chain`
  (incremental entity-maintenance, §P3) since the loop helps the graded pick but hurts the rigid pick.
- **Do NOT** deploy recency-only (it regresses the competitive/conflict cases the integrated organ handles).

Expected board effect: the coref board dim and who-has-what rise; affect/entity-KB unchanged (common-noun
bound — a separate, already-filed lever).

---

## TLDR (plain English)

When a story says "he" or "she", the program has to decide which character that is. It gets this right
about **47 out of 100 times** — and the reason is a bad rule: it always guesses the character who has been
talked about the most so far, and ignores who was **mentioned most recently**. The brain does the opposite
(recency is a core cue), and a better module that does it the brain's way was already built for a related
job but never plugged into the live reader. I plugged it in and measured it on real books: it jumps to
about **60 out of 100** — a big, clean gain, and a scrambled version fails, so the gain is real. It also
does not hurt the "named character" cases. Feeding this better answer into a follow-on question ("what does
he own?") also improves it. One thing the brief expected did NOT happen: it doesn't help the emotion module,
because most feelings in these books are attached to characters named by a common word ("the old man"), and
those are a *different* weak step, not the "he/she" step I fixed. Nothing here changes the live program yet
— the actual plug-in is a one-function swap for the other session to land.

## QUESTIONS

None blocking. One judgement call for the owner/strategy: the bar named "affect OR entity-KB" as the
downstream to lift; both are common-noun-bound and don't move for a pronoun fix, so I demonstrated the
payoff on who-has-what (pronoun-bound) instead and reported affect as a measured located-negative. If you
want the literally-named downstream to rise, that lever is common-noun coref (already a separate problem).

## NEXT STEPS

1. **Strategy lands the Q111 wire** (graded pick into `_read_entities`, event-centrality off) and re-runs
   the board — expect coref + who-has-what to rise, affect/entity-KB flat.
2. **Compose with `graded_chain`** (§P3 incremental entity-maintenance) once wired — the recurrence helps
   the graded pick (+0.065) but hurts the rigid pick, so they must land together.
3. **The residual is the coherence next-mention PRIOR** (Kehler-Rohde; ~19-29% of errors structurally
   dominated) — already filed as `who_has_what_needs_a_coherence_next_mention_prior_kehler_rohde`; that is
   the deeper frontier once the pick is live.
4. **The affect/entity-KB lever is COMMON-NOUN coref**, not the pronoun pick — pursue it through the
   entity-world-model / common-noun problems, not here.
