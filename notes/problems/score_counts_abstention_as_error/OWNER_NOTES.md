---
owner_verdict: DONE
---

Done. score_counts_abstention_as_error is SOLVED, machine-check clean (malformed/incomplete: 0, exit 0), now awaiting strategy re-verify + integration. No writes outside my lane; no re-run of the landed cell; no denied calls.

What the defect was. The cell's _score did ok = (pred == gold) and never named the readout's abstain outcomes. The engine's own set is _LEVIN_ABSTAIN = ('NA','NONE','AMBIGUOUS') (branched on at goal_typing.py:2200,2214) — so the scorer counted every "I can't tell" as a wrong answer, disagreeing with its own engine.

The disk outranked the brief. The brief named 3 AMBIGUOUS items. The disk has 17 abstentions (14 NONE + 3 AMBIGUOUS), all reason abstain_fallback_to_lexicon, all scored wrong by the old code. NONE abstains under both convention sets, so it never trips .agree — which is why the brief only saw the 3.

What I measured (OOV-36, live readout):

number	value	moves?
coverage-weighted accuracy (gated)	0.3056 = 11/36	no — invariant to the relabel, so no gate/verdict moves (stays HARD_FAIL vs 0.6389)
3-way split	11 correct / 8 wrong / 17 abstained	was reported as 11 / 25-"not-correct"
selective accuracy when committing	0.5789 = 11/19 (engine) vs 0.5000 (narrow)	yes — .agree = False
The one number that moves (0.5789) does not clear its own fair floor (committed-majority = 0.7368), so this is an instrument fix, not a rescue — exactly as the brief predicted.

Controls (all pass, witness): positive — the 3 AMBIGUOUS were correct:False; they move selective accuracy 0.5000→0.5789, and removing exactly those 3 makes the conventions agree. Negative — empty-overlay baseline byte-identical (0.3889), zero AMBIGUOUS. Stability — predictions reproduce 36/36 live from the saved overlay. Engine-coupling — NONE/AMBIGUOUS read present in _LEVIN_ABSTAIN.

Files: the fix (abstention-aware _score, additive + gate-safe), the new witness, and SOLVED.md.

TLDR. The scorer used to count "I can't tell" as wrong; its engine never did. I matched them. The headline number is byte-identical on purpose — what changed is that the instrument now reports "answers 53% of the time, 58% accurate when it does" instead of a flat "31%". The real problem was 17 hidden abstentions, not 3.

Questions. None blocking. One for integration: is NONE an abstention or a commitment? Every signal on disk says abstention; I scored it that way and flagged it as the first thing to withdraw if wrong.

Next steps (strategy session's, not mine). Re-run the cell to refresh the landed metrics.json with the additive fields; optionally replace the guard's hard-coded self-test fixture with a read of the live predictions so its tripwire actually fires; hdlab/ needs no change.
