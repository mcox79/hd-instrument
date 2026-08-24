---
owner_verdict: DONE
---

SUBMISSION — problem: reader_meaning_channel — status: REFUTED

WHAT WAS ASKED
"The reader's meaning channel is the wrong modality." Our system works out word meaning from
word-neighborhoods (co-occurrence), which is capped. A grounded channel (human sensory + emotional
ratings) predicts meaning far better. The ask: wire the grounded channel in so the reader gets
meaning from it, and prove the gain survives on unseen text.

THE ANSWER — the diagnosis is wrong. The gap is ARCHITECTURAL, not MODAL.
I built the strongest, most brain-faithful version of the ask: a multi-spoke grounded hub
(sight/sound/touch/action + the EMOTIONAL database), concreteness-gated, combined the way the brain
actually does it — Bayesian sense selection [how-common-each-meaning-is] + [how-well-context-fits],
with a control gate — and tested it on a real behavioral task (pick the right meaning of an ambiguous
word in context), reusing a landed instrument with a real floor and full controls (287 words, 841
trials, unfitted).

  grounded hub, combined (uniform) ....... 0.4702   vs floor 0.4778 → −0.008, CI[−0.033,+0.019], NOT sep
  grounded hub, brain control-gated ...... 0.4844   vs floor 0.4778 → +0.007, CI[−0.017,+0.031], NOT sep
  grounded coherence ALONE ............... 0.4171   (below even the uniform 1/k floor 0.4316)
  FREQUENCY PRIOR (most-frequent-sense) .. 0.4778   ← the strongest floor; beats grounded CI-separated (+0.060 [+0.007,+0.115])

Once you also know how common each meaning is, the sensory/emotional channel adds nothing measurable —
uniform OR brain-control-gated. The one lever that moved the number was the frequency PRIOR, the half
every prior attempt omitted (they all used a too-weak uniform floor).

WHY THIS REFUTES THE PREMISE (the brain-foundational thesis)
Supplying a better MODALITY has now floored on SIX read-time meaning-use instruments (this one + five
cited: pick-one-of-50, cortical read, on-path readout, end-to-end readout, multi-attribute fusion).
The grounded channel's only win is an OFFLINE similarity table — never on the reading path. Meanwhile
the brain literature (Controlled Semantic Cognition; McClelland 2013 proving settling = Bayesian) says
meaning USE = a representation PLUS a control network that applies a frequency prior and overrides it
only on conflict. The reader has the representation and NONE of the control architecture. You cannot
fix a control deficit by adding more spokes. So the reader's meaning problem is not the KIND of
information — it is the missing machinery that USES it.

THE ONE REAL SIGNAL (brain-predicted, too weak to count)
On the hard SUBORDINATE-sense items (true meaning is the rare one), the frequency prior scores 0% by
construction and the grounded channel rescues some to 8% — coherence helps exactly where the brain
says it should, but it's 16% of items and washes out overall.

SCOPE (so it doesn't over-travel)
Refuted: "supplying the grounded modality fixes the reader's read-time meaning use." NOT claimed:
"grounding is useless" — it carries real meaning (offline similarity), and its likely correct home is
graded INFERENCE, not discrimination (untested). NOT tested: the live read() adapter (still unbuilt).

REDIRECT / NEXT
(1) Stop supplying modalities for disambiguation. (2) Build the control architecture: a most-frequent-
sense prior + a conflict-gated override (the additive form is untried and unblocked; the multiplicative-
gain form already failed here). (3) Strongest next experiment (file separately): a positive dissociation —
prove grounding helps INFERENCE where the frequency prior fails, and vice versa.

FILES / REVERIFY
experiments/exp_reader_sense_selection_bayesian_hub_v1.py, experiments/grounding_channels.py,
verification/test_reader_sense_selection_bayesian_hub.py, notes/problems/reader_meaning_channel/SOLVED.md
reverify:  .venv/Scripts/python.exe verification/test_reader_sense_selection_bayesian_hub.py
