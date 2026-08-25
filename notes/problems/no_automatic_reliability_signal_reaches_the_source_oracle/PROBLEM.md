---
priority: 4
review:
review_text:
---

# PROBLEM: an oracle that picks the best source per question beats everything -- but no AUTOMATIC signal reaches it. Find one.

## 1. THE PROBLEM IN PLAIN LANGUAGE

When the system answers, it has several sources it could trust (its own reading-built statistics, a
supplied knowledge asset, the grounded feel of words). If an ORACLE is allowed to pick the best source
for EACH question, it clearly beats plain word-counting (0.408 vs 0.324) -- so the right answer is
present in our own sources; we just do not know WHICH source to trust for a given question. Every
automatic way we have tried to guess that -- how confident a source is, whether sources AGREE --
carries NO real information (scrambling the signal changes nothing). The missing piece is a per-question
"trust the source that actually knows THIS" signal that works WITHOUT being shown the answers. The same
missing piece shows up in the meaning step AND the recall step -- it is one component, not two.

## 2. WHY THIS ONE

It is the single component two broken/weak stages both need. Stage 2 (decide what words mean) and stage
5 (get it back out) independently converge on it: the knowledge is present, an oracle reaches it, and no
automatic method does. Solve this and both stages gain at once. It is the highest-leverage thing left
that is neither already-proven nor a wiring job.

## 3. HOW THE BRAIN DOES THIS

PINNED: the brain does RELIABILITY-WEIGHTED CUE COMBINATION -- it weights each source by how reliable it
is FOR THE CURRENT input, not at a fixed rate (Ernst & Banks 2002; Ma 2006; Kording 2007). Reliability
is carried in neural GAIN, set per-item, plausibly from the sharpness/variability of a source's OWN
response (Henaff 2020 gain-variability). Copy that OPERATION: estimate each source's per-item reliability
from its OWN response geometry (peakedness, dispersion, self-consistency), NOT from cross-source
agreement or a scalar confidence (both refuted). The brain does not read reliability off agreement; it
reads it off how sharply a source responds.

## 4. MEASURED vs INFERRED

MEASURED: an oracle picking the best source per question scores 0.408 vs counting 0.324, CI-separated
ABOVE -- the headroom is real (stage 5; wire_the_refuse_gate / store_survives_a_partial_cue). A per-item
arbiter over confidence + cross-source AGREEMENT is INERT: its permuted-signal twin REPRODUCES it, and it
only ties a fixed blend (teach_the_self_built, REFUTED). So the SIGNAL, not the arbitration machinery, is
what is missing.
INFERRED (open, fair to overturn): that a per-item reliability signal derived from a source's OWN
response geometry (not agreement/confidence) reaches the oracle. Unknown -- may need a different geometry
or may not be recoverable per-item at our reading scale.

## 5. ALREADY TRIED (do not re-run)

- Confidence + cross-source AGREEMENT as the reliability signal -- REFUTED (permuted twin reproduces it;
  ties a fixed blend). Do NOT re-test these two signals.
- A fixed-weight blend -- helps a little when sources are comparable, hurts when one dominates; it
  captures all the arbiter's gain. The per-item arbiter over the refuted signals adds nothing.
Query `experiment_index.py query "reliability"`, `query "oracle"`, and read
`notes/problems/teach_the_self_built_space_instead_of_concatenating_it/SOLVED.md` (the deep-dive) FIRST.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Read `teach_the_self_built.../SOLVED.md` (the arbitration deep-dive) + the
  `exp_reliability_arbitration_hub_v1` cell; confirm the oracle headroom (0.408 vs 0.324) and that
  confidence/agreement are inert (permuted twin reproduces the arbiter).
- Confirm the owned sources (self-built PPMI+SVD tier; supplied distributional foundation) and the
  source-selection / recall task instrument.

## 7. THE BAR

On the source-selection / recall task (same population and floor as the oracle 0.408 / counting 0.324):
a per-item reliability estimator derived from a source's OWN response geometry must beat the fixed-weight
blend AND plain counting CI-separated, moving toward the oracle, with the mandated info-free twin
(per-item reliability PERMUTED across items) LOSING CI-separated. HOW WE WOULD KNOW IT FAILED, and this
is a full PASS for the brief: the geometry signal is ALSO inert (permuted twin reproduces it) => per-item
reliability is not recoverable from our sources at this scale; recommend a fixed blend and name what a
recoverable signal would require.

## 8. FILES AND ENTRY POINTS

- `notes/problems/teach_the_self_built_space_instead_of_concatenating_it/SOLVED.md` -- the refuted arbiter
  + the oracle headroom.
- `experiments/exp_reliability_arbitration_hub_v1.py` (refuted v1); `exp_cls_hippocampal_cortical_fusion_v1.py`
  (the CLS episodic trace, a candidate geometry source).
- `hdlab/cortical_recall.py` / the store read-out. Prove in `experiments/` + `verification/`; propose any
  hdlab wiring in `SOLVED.md` (strategy lands it, board Q111). Do NOT write `hdlab/`.

## DO NOT QUOTE / DO NOT REDO

- Do NOT quote the oracle 0.408 as an achievable capability -- it SEES the answers; it proves headroom
  exists, not that any automatic method reaches it.
- Do NOT re-test confidence or cross-source agreement as the reliability signal -- both refuted.
