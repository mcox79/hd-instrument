# The four owner-run solver sessions of 2026-09-13 -- evaluation (strategy, 14:15 local)

Source: the latest segment of each session transcript (from the brief paste to end), read by a sonnet agent; integration results
from the ledger. Sessions: A harm/help (83fd02db), B coordination (e6f6bac1), C object slot (5fb58138), D induced categories (fa9e276f).

| solver | wall time | owner msgs | turns / tools | result | board effect after integration |
|---|---|---|---|---|---|
| A harm/help | 12 h (overnight, unattended) | 6 | 422 / 181 | SOLVED; 4 verbs recovered; CF human-gold 0.932; 3 upstream joins | none on the 7-dim board (named-gap dims); live gold held 35/36 |
| B coordination | 2 h | 7 | 444 / 143 | SOLVED; conj 0.30 -> 0.38 live (CI-sep) | neutral (0.6345 -> 0.6346) |
| C object slot | 3.3 h | 12 | 519 / 202 | PARTIAL; +0.067 OBJ precision on the old parser; null on ours | negative on the live chain (patient -1.7) -> landed OFF |
| D induced categories | 14.5 h (overnight) | 8 | 686 / 295 | SOLVED; closed classes separated; type m2o 0.79 | +0.0007 UPOS as the reading cue; not the live tagger |

**Quality:** higher than strategy would have produced on the same problems in the same hours -- every solution carries scrambled twins,
paired CIs, an independent human gold, and ~5 refuted levers with numbers; A's reverify chain caught three defects in strategy's own
morning flips (wound/wind lemma collision; predicate-recall crash; stale test). **Board impact:** < 0.001 aggregate from all four
together; today's board moves (role validities from perceived heads +6 patient; in-order governor recovering state; category flips)
came from chain-level strategy work. **Speed:** two sessions ran 12-14 h unattended (cheap in owner time, slow in wall time); the
afternoon pair ran 2-3 h with check-ins every 8-16 min.

**Owner guidance = a four-step script broadcast to paired tabs within seconds, often verbatim:** (1) status probe "how are we performing
against the brain, where do we lose signal upstream, are all upstream components BF"; (2) quality push "go after the remaining
opportunities, BF and right not easy"; (3) verdict check "is this a fully complete, excellent submission?"; (4) finalize-documentation
request (identical wording, down to typos, in all four). 5 of 33 messages were judgment calls, all in C and D: "prototype a fully BF
stack", "what would it take to make this fully solved", "path A - try it", "can we try for both" -- they pushed PARTIALs to their
strongest honest form. Median gap between messages 8-53 min.

**Can agents replace the guidance?** Mechanically yes: a SUPERVISOR loop = spawn solver with the brief; after its first result send the
status probe; once, the quality push; then the verdict check against the rubric (witness green, twin loses, CI-separated, bar met); on
PARTIAL ask "what would it take" and try the cheapest path once; then the finalize request; hand SOLVED to strategy; the owner's DONE
stays the human gate. The binding constraint is usage accounting (solvers must be opus sessions; the owner moved them out of the
strategy session to keep Fable under its cap), not capability. Proposed: `hdi_solver_supervisor` runner role.
