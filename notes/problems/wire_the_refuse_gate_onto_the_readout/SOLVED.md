---
problem: wire_the_refuse_gate_onto_the_readout
status: REFUTED
bar: "AFTER WIRING: INVENTED WORDS ARE REFUSED AND REAL WORDS ARE STILL ANSWERED. BOTH ARMS, OR THE RESULT IS WORTHLESS."
result: "Wiring the refuse gate (a threshold on the route's top-1 retrieval confidence, atom_consultation OFF) onto recall_sentence and recall_cortical does NOT clear the bar. recall_sentence: real-vs-invented AUC mean 0.624 over 3 seeds (per-seed 95% CIs 0.566-0.679, all above 0.5) -- a real but weak signal; the calibrated gate's held-out balanced accuracy is only 0.568, and at any threshold refusing >=90% of invented words it keeps just 24% of real words (mean of 3 seeds). recall_cortical: AUC mean 0.547 (seed-7 CI 0.484-0.576 includes 0.5), gate balanced 0.524, keeps ~20% of real at >=90% invented-refusal. n=300 real read words vs 300 length/letter-matched invented strings per seed (held-out 150/150), scorer = top-1 route confidence, corpus = simplewiki ~3700-4500 sentences read."
floor: "Info-free twin (a gate refusing the SAME held-out fraction at random): balanced accuracy 95% CI ~[0.447, 0.553], mean 0.500. recall_sentence's gate (0.568) sits at/barely above this floor; recall_cortical's (0.524) is INSIDE it. Also a label-shuffle AUC null, p95 ~0.55."
controls: "(1) info-free twin -- random gate at matched refusal rate scores 0.50 balanced, excluding 'the gate wins merely by refusing a lot'; (2) label-shuffle AUC null (p95 ~0.55), excluding chance separation; (3) invented strings matched to real words on length AND unigram letter frequency and verified ABSENT from the read vocabulary (excluded 0 real words wrongly; every invented string confirmed never-read), foreclosing an orthography/OOV shortcut; (4) positive control -- query() refuses 8/8 invented strings (known=False, decision=REFUSE), proving the harness can detect a working refusal; (5) native-refuse baseline measured at 0/20 for BOTH routes, so every refusal is attributable to the added gate, not to the route; (6) consolidated-subset arm -- real words that reached the cortical store separated at AUC 0.65-0.95, but only 6-11 of 300 sampled words, isolating that the separable signal is STORE MEMBERSHIP, not similarity confidence."
files_changed: "experiments/exp_refuse_gate_on_readout_v1.py, verification/test_refuse_gate_on_readout.py, notes/problems/wire_the_refuse_gate_onto_the_readout/SOLVED.md (proposed hdlab change described below, NOT landed)"
reverify: ".venv/Scripts/python.exe verification/test_refuse_gate_on_readout.py"
---

# REFUTED: the refuse gate does not transfer to the read-out routes, and the reason names the real fix

## What the brief asked, and what I tested

The brief's INFERRED claim (its own label) was that wiring slot `Q3` -- the refuse gate,
`hdlab/refuse_gate.py`, "with `atom_consultation` OFF" -- onto `recall_sentence` and
`recall_cortical` would let them say "I do not know." The brief was explicit that this was not
measured and that a null "sends the work to the retrieval space instead."

The refuse gate is not an organ that inspects a word; it is `calibrate_refuse_threshold(...)` +
`apply_refuse(score, tau)` -- **a threshold on a confidence score**. "Wiring it onto a route,
atom_consultation OFF" therefore means exactly this: take the route's own top-1 retrieval score as
the confidence, calibrate `tau` on read-vs-invented scores, and refuse below `tau`. That is what I
built and measured. A threshold can satisfy the bar only if the confidence SEPARATES read words from
never-read words. It barely does.

## The problem is live (reproduced on disk)

One 400-sentence read, the brief's own probe (`scratch/can_the_readout_say_i_dont_know.py`):
`recall_sentence` and `recall_cortical` each returned a confident five-item answer to **8 of 8**
invented strings; `query()` refused all 8 (`known=False`, `decision=REFUSE`). The witness
re-confirms it at a larger scale: **0/20** native refusals on both routes, `query()` refuses. So the
defect is real and `query()` is a sound positive control -- both as the brief states.

## Why the confidence cannot separate: it is a hash

`context_vector` maps each content word to a `sha256`-seeded bipolar vector and returns the sign of
their sum (`grounding_acquisition_loop.py:117`). For a **bare-word cue** (which is how the brief
asks the question) the cue is a single such vector. So a real word's cue and an invented word's cue
are drawn from the **same distribution** -- an avalanche hash makes orthographic similarity
irrelevant. The only thing that can distinguish them is whether that exact vector participated in
stored episodes. After CA3 settling and sparse-overlap matching, that leaves a faint echo, not a
usable signal.

## The measurement (3 seeds, 300 real read words vs 300 matched invented strings, held-out 150/150)

| route | AUC (real>invented), mean [per-seed CI range] | calibrated-gate balanced acc | at >=90% invented-refusal, real kept |
|---|---|---|---|
| `recall_sentence` | **0.624** [0.566 - 0.679, all > 0.5] | **0.568** | **0.24** (0.273 / 0.213 / 0.227) |
| `recall_cortical` | **0.547** [0.484 - 0.603, seed-7 includes 0.5] | **0.524** | **0.20** (0.133 / 0.207 / 0.253) |
| info-free twin (floor) | 0.500 (label-shuffle null p95 ~0.55) | ~0.500, CI [0.447, 0.553] | -- |

Reading it against the bar ("BOTH ARMS, OR THE RESULT IS WORTHLESS"):

- **`recall_sentence` carries a real but weak signal.** Its AUC is CI-separated above chance on all
  three seeds. But the best the calibrated gate can do -- the threshold that MAXIMISES balanced
  accuracy -- is 0.568, only a whisker above the 0.50 information-free floor, and it gets there by
  **refusing ~56% of real words** (accept_real mean 0.44, refuse_invented mean 0.70). Push it to a
  usable refusal (>=90% of invented) and it keeps only **24%** of real words. Both arms are never
  high together.
- **`recall_cortical` has no usable signal.** AUC 0.547 with seed-7's CI touching 0.5; the gate's
  balanced accuracy (0.524) is inside the info-free floor and its operating point is unstable across
  seeds (accept_real swings 0.13 -> 0.61). At >=90% invented-refusal it keeps ~20% of real.
- **Survivor precision** (accuracy recomputed on the surviving population, as the bar demands): among
  words the balanced-accuracy gate ACCEPTS, only ~0.60 are real (`recall_sentence`) and ~0.58
  (`recall_cortical`, unstable) -- barely above the 0.50 base rate of the pool. Gating the read-out
  this way does not meaningfully purify what it answers.

## Where the tiny signal comes from -- and it names the real fix

The consolidated-subset arm is the tell. Real words that had reached the **cortical store**
separated from invented strings at AUC 0.65-0.95 (both routes) -- far better than the read
vocabulary at large -- but they are only **6-11 of 300** sampled read words, because consolidation
accepts a small minority. So the separable information is **store membership**, not similarity
confidence. That is exactly the mechanism `query()` already uses: it addresses the store
(`known = bool(store.query(lemma, rel))`) and refuses when nothing is keyed to the cue. The refuse
gate's "atom_consultation OFF" recipe deliberately throws away the one signal that works and keeps
the one that doesn't.

## What would have to change in hdlab, and why (PROPOSED, NOT LANDED)

**Do NOT land the brief's recipe.** Adding a confidence threshold (atom_consultation OFF) to
`Substrate.recall_sentence` (`substrate.py:931`) or `Substrate.recall_cortical` (`:895`) would make
the system refuse three-quarters of the real words it knows in order to catch the invented ones. It
trades a false-confidence defect for a false-refusal defect and moves no honest number.

**What the evidence supports:** if these routes should refuse a bare-word cue, gate them on
**addressed store membership**, i.e. `atom_consultation ON` -- the same test `query()` passes. A
minimal change: before returning a ranking, check whether the cue has any support in what was
actually stored (for a bare-word cue: is the lemma present in the read vocabulary / episodic pool /
consolidated set), and return `[]` when it has none. The similarity score may still ORDER the
survivors; it must not be the thing that decides whether to answer at all. This keeps `query()`
untouched as the reference and does not require the refuse-gate organ.

*Scope note:* this proposal is about the bare-word "do you know this word" case the brief measured.
A genuine multi-word sentence cue poses a different membership question (coverage of the sentence's
content words), which I did not measure and which the retrieval-space follow-up should own.

## What I did NOT establish

- **Sentence-context cueing.** I tested bare-word cues, faithful to the brief's probe and bar. A
  richer confidence signal from a full-sentence cue, or a margin/entropy statistic instead of top-1
  score, might separate better. I did not test these; "the gate cannot work on any cueing" is NOT
  claimed. What is claimed is scoped: the refuse gate as specified (top-1 confidence threshold,
  atom_consultation OFF, bare-word cue) does not clear the bar.
- **A membership gate's numbers.** I argue from `query()`'s existing behaviour and the
  consolidated-subset AUC that membership is the right signal; I did not build and score a
  membership-gated `recall_*`. That is the natural next deliverable.

## What I would withdraw first if it turned out to be wrong

The claim most exposed is that `recall_sentence`'s AUC of 0.624 represents a *floor-clearing* signal
worth chasing. It is CI-separated above 0.5, but it is close to the information-free floor and I have
not shown it survives a stricter, frequency-matched negative (real words are, by definition, more
frequent than never-read strings; some of the AUC is "was this token ever read at all", which is the
membership signal wearing the confidence's coat). If a frequency-matched control collapsed that AUC
toward 0.5, the correct statement would harden to "the similarity confidence carries essentially no
read/never-read signal beyond bare membership" -- which would strengthen, not weaken, the REFUTED
verdict and the membership-gate recommendation.

## TLDR (plain language)

The system answers made-up words as confidently as real ones on two of its three ways of answering,
and the brief hoped that bolting on an existing "confidence check" would fix it. It does not. That
confidence check is just "is the top match's score high enough," and the score is essentially a
coin-flip for telling a learned word from an invented one -- the internal code for a word is a hash,
and a made-up word gets just as clean a hash as a real one. To make the check reject 9 of 10
invented words you must also reject about 8 of 10 real words, which is useless. The one part of the
system that CAN say "I don't know" -- `query()` -- does it by checking whether it actually stored
anything about the word, not by scoring a similarity. That is the fix: have these two routes check
their memory for the word before answering, instead of thresholding a similarity.

## Questions

None.

## Next steps (for the strategy session, which owns integration)

1. Do not land the confidence-threshold gate (atom_consultation OFF) on these routes.
2. If refusal on these routes is wanted, prototype a **membership gate** (atom_consultation ON,
   mirroring `query()`): refuse a bare-word cue with no store support; let similarity only order the
   survivors. Measure it on the same 300/300 read-vs-invented design; the bar is unchanged.
3. Send the "can it refuse a novel word in CONTEXT" question to the retrieval space, as the brief
   anticipated -- that is a different (and harder) instrument than the bare-word case measured here.
