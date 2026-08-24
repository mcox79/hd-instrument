---
problem: wire_the_refuse_gate_onto_the_readout
status: SOLVED
bar: "AFTER WIRING: INVENTED WORDS ARE REFUSED AND REAL WORDS ARE STILL ANSWERED. BOTH ARMS, OR THE RESULT IS WORTHLESS."
result: "The bar is met -- but NOT by the brief's named mechanism. Gating recall_sentence/recall_cortical on CUE FAMILIARITY (store membership: does the cue lemma carry any encoding trace) clears BOTH arms: accept_real 1.000, refuse_invented 0.999, balanced 0.999 (mean of 3 seeds; 300 real read words vs 300 length/letter-matched invented strings; membership is an exact lookup, no estimation). The brief's proposed mechanism -- the refuse gate as a THRESHOLD on the route's top-1 similarity confidence, atom_consultation OFF -- is REFUTED at the same time: it reaches only 0.568 (recall_sentence) / 0.524 (recall_cortical) balanced, barely above the 0.50 info-free floor, and to refuse >=90% of invented it discards ~76-80% of real words. The refusable signal is CUE FAMILIARITY, not answer confidence."
floor: "Info-free twin (a gate refusing the SAME fraction at random): balanced accuracy 0.500 (95% CI ~[0.447, 0.553]). The similarity-confidence gate (0.568 / 0.524) sits AT this floor; the familiarity gate (0.999) clears it decisively. Second floor for the level analysis: the RECOLLECTION-level gate (query()'s own stricter level -- consolidated fact required) scores balanced 0.515 for ANSWERING, i.e. at the info-free floor, because it refuses ~97% of real read words."
controls: "(1) info-free twin -- random gate at matched refusal rate = 0.50 balanced, excluding 'wins by refusing a lot'; (2) label-shuffle AUC null (p95 ~0.55) for the confidence gate, excluding chance separation; (3) invented strings matched to real on length AND unigram letter frequency and verified absent from the read vocabulary, foreclosing an orthography/OOV shortcut (the residual 0.001 miss is a generated string that LEMMATISES to a read word -- correct familiarity behaviour, not a leak); (4) positive control -- query() refuses 8/8 invented (known=False); (5) native-refuse baseline 0/20 both routes, so refusals are attributable to the added gate; (6) LEVEL control -- the recollection-level membership gate (query()'s own level) does NOT clear the bar (accept_real 0.03), proving the win is specific to the FAMILIARITY level, not 'any membership check passes'; (7) graded-familiarity check -- real cues carry >=1 trace (mean ~3.7), invented carry 0, so the signal is a clean trace-presence boundary."
files_changed: "experiments/exp_refuse_gate_on_readout_v1.py, experiments/exp_refuse_gate_on_readout_v2_membership.py, verification/test_refuse_gate_on_readout.py, notes/problems/wire_the_refuse_gate_onto_the_readout/SOLVED.md (proposed hdlab change described below, NOT landed)"
reverify: ".venv/Scripts/python.exe verification/test_refuse_gate_on_readout.py"
---

# SOLVED -- but the fix is CUE FAMILIARITY, not the confidence gate the brief named

## How the brain knows it does not know (the frame that decided this)

"Do I know this word" is metamemory -- a feeling-of-knowing judgement. The literature splits it two
ways, and the split is the whole result here:

- **Cue familiarity** (Reder): a fast signal on the CUE itself -- a perirhinal/MTL familiarity read
  of "have I encountered this." A never-seen cue evokes no familiarity -> "I do not know." It is a
  judgement made BEFORE, or independent of, the retrieval attempt.
- **Accessibility** (Koriat): the quantity and intensity of PARTIAL INFORMATION the retrieval
  attempt yields. More stuff comes to mind -> higher feeling-of-knowing.

The brief's proposed fix -- threshold the route's own similarity confidence -- is the ACCESSIBILITY
proxy. It fails here for a brain-legible reason: in this substrate a cue is a `sha256`-seeded bipolar
vector, so retrieval ALWAYS yields a confident-looking neighbour, real word or nonsense alike.
Accessibility is uninformative when every cue is accessible. The signal that works is **cue
familiarity = store membership**, which is exactly what `query()` uses and what "atom_consultation
OFF" throws away.

## The problem is live (reproduced)

`recall_sentence` and `recall_cortical` each answer **8/8** invented strings with a confident
five-item ranking (the brief's probe); the witness re-confirms **0/20** native refusals on both
routes, while `query()` refuses (`known=False`, `decision=REFUSE`). Real defect, sound positive
control -- as the brief states.

## Two gates on the same instrument (3 seeds, 300 real read words vs 300 matched invented)

| gate | mechanism | accept_real | refuse_invented | balanced | vs 0.50 floor |
|---|---|---|---|---|---|
| **confidence** (brief's Q3, atom_consultation OFF) | threshold on top-1 similarity | 0.44 | 0.70 | **0.568** / 0.524 | at the floor |
| **familiarity** (proposed fix) | refuse a cue with no encoding trace | **1.000** | **0.999** | **0.999** | clears it |
| recollection (query()'s own level) | refuse a cue with no CONSOLIDATED fact | 0.03 | 1.000 | 0.515 | at the floor for ANSWERING |

- **The confidence gate is REFUTED.** Its AUC (real>invented) is 0.624 (recall_sentence, CI-separated
  above 0.5) / 0.547 (recall_cortical, seed-7 CI includes 0.5) -- a real but far-too-weak signal. The
  threshold that MAXIMISES balanced accuracy still only reaches 0.568, and it gets there by refusing
  ~56% of real words. Pushed to a usable refusal (>=90% of invented) it keeps just **24%**
  (recall_sentence) / **20%** (recall_cortical) of real words. Both arms are never high together.
- **The familiarity gate clears the bar.** Refuse a bare-word cue whose lemma carries no encoding
  trace; otherwise answer. accept_real 1.000, refuse_invented 0.999, balanced 0.999, on both routes,
  end to end (the witness drives the actual routes: invented -> `[]`, real -> ranked answer).

## The honest caveat, stated up front: the familiarity win is DEFINITIONAL

The store IS the ground truth of what was read, and the invented strings were generated to be absent
from it. So accept_real 1.0 / refuse_invented ~1.0 is TRUE BY CONSTRUCTION, not an emergent
discrimination. **That is the point, not a weakness:** it proves the refusal information was fully
AVAILABLE and merely unconsulted -- the brief's own thesis, "the part that could is built and
unplugged" -- and that consulting it clears the bar. No learned capability is claimed. This is a
wiring fix, which is exactly what the brief advertised ("a WIRING job ... not a build").

What keeps it from being a hollow lookup is the LEVEL analysis, which is a real decision with a
brain-structure reading:

- **Familiarity level** (any encoding trace; ~6,000 words): the right level for "should I answer at
  all." Clears the bar.
- **Recollection level** (a consolidated meaning fact; ~150 words -- `query()`'s own level): refuses
  ~97% of real READ words, re-introducing the trap. `query()` is calibrated for "can I state a
  meaning," which is stricter than "have I encountered this." Wiring `query()` verbatim onto the
  read-out would make it refuse most real words; the read-out needs the FAMILIARITY level, not the
  recollection level.

The graded-familiarity check substantiates the mechanism: real cues carry >=1 accumulated trace
(mean ~3.7), invented cues carry 0. Familiarity here is a clean trace-presence signal, and a graded
threshold at ">=1 trace" is the membership gate.

## What would change in hdlab, and why (PROPOSED, NOT LANDED)

**Do NOT land the brief's recipe** (a confidence threshold on `recall_sentence` /
`recall_cortical`, atom_consultation OFF). Measured: it would refuse three-quarters of the real words
the system knows to catch the invented ones -- trading false confidence for false refusal.

**Land a familiarity gate instead** (atom_consultation ON, at the familiarity level). Minimal change,
in `hdlab/substrate.py`:

- `recall_sentence` (`:931`) and `recall_cortical` (`:895`): before returning the ranking, for a
  bare-word cue check whether the cue lemma is in the accumulated read vocabulary / has any episodic
  trace (`normalize_lemma(cue) in <familiarity set>`); return `[]` if not. Similarity still ORDERS
  the survivors -- it just no longer decides whether to answer.
- The familiarity set is already computable from live state (`self.profile()` keys / the episodic
  index); no new organ and not the `refuse_gate` module. `query()` stays untouched as the reference.

*Prototype:* `experiments/exp_refuse_gate_on_readout_v2_membership.refusing_recall` is the exact
wrapper the diff implements, measured above.

*Scope:* this is the bare-word "do you know this word" case the brief measured. A multi-word sentence
cue poses a different membership question (coverage of the sentence's content words) and belongs to
the retrieval-space follow-up.

## What I did NOT establish

- **Refusing a KNOWN word whose retrieved ANSWER is wrong.** The familiarity gate refuses only
  never-encountered cues. It does nothing about a real word that retrieves a bad neighbourhood
  (the genericness/`way`-attractor half of the brief's section 3). That is the accessibility problem,
  and this instrument does not touch it.
- **Sentence-context cueing**, and any richer confidence signal (margin, entropy) than top-1 score.
  The confidence gate is refuted for the bare-word, top-1 case only; "no cueing can work" is NOT
  claimed.

## What I would withdraw first if it were wrong

The claim most worth stress-testing is that the familiarity level (not recollection) is the RIGHT one
for the read-out. It clears the bar, but it also means the routes will answer ~6,000 barely-seen
words -- some read once, in one sentence -- with a confident ranking. If the downstream goal is "only
answer words you can actually say something reliable about," the recollection level (or a graded
trace-count threshold between the two) may be the better operating point, at the cost of refusing
more real words. I measured the two endpoints; I did not sweep the trace-count threshold between them,
and that sweep is where the real product decision lives.

## TLDR (plain language)

Two of the system's three answer routes reply to made-up words as confidently as to real ones. The
plan hoped an existing "confidence check" would fix it; it does not, because a word's internal code
is a hash and a made-up word gets just as clean a hash as a real one -- so the confidence is a
coin-flip for telling them apart (to reject 9 of 10 fakes it must also reject ~8 of 10 real words).
The fix that works is the one the system's own working route already uses: check whether it has ever
actually encountered the word before answering. Wired that way, it refuses essentially all made-up
words and keeps all real ones. The honest caveat is that this is a lookup of something the system
already knew and just was not checking -- which is exactly the point: the ability was built and
unplugged, and this plugs it in.

## Questions

None.

## Next steps (for the strategy session, which owns integration)

1. Land the FAMILIARITY gate on `recall_sentence` / `recall_cortical` (prototype cited above); do NOT
   land the confidence-threshold gate.
2. Decide the operating level deliberately: familiarity (answer anything encountered) vs a graded
   trace-count threshold toward recollection (answer only what is well-supported). I measured the two
   ends; the threshold sweep between them is the product call.
3. Send "refuse a wrong answer to a KNOWN word" and "refuse a novel word IN CONTEXT" to the retrieval
   space -- those are the accessibility problems this membership fix does not address.

---

## INTEGRATED_BY_STRATEGY -- 2026-08-23

Re-verified (familiarity gate 1.000). Wiring decision recorded: DEFAULT-OFF. Measured the arm nobody ran -- on real English the substrate has not read, the same gate refuses 85.8% at 5,200 sentences, and coverage is a function of read volume (5.1% -> 14.2% across 800 -> 5,200).

*Appended by the strategy session, which owns integration (board Q111). The solver's text above is unchanged.*
