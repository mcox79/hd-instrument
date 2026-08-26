---
priority: 4
review:
review_text:
---

# PROBLEM: the brain LEARNS and UPDATES by prediction error -- its single most pervasive computation -- and we do neither (we learn by cloze and never update on surprise)

**slug:** `the_substrate_does_not_learn_or_update_by_prediction_error` - **opened:** 2026-08-26 by the strategy session
(packaged from `notes/BRAIN_FOUNDATIONAL_AUDIT.md` deviation #6 -- a genuinely foundational, unqueued deviation)
**status:** OPEN - **first-hand in ORGAN_MAP G1/G2/E2/F5 + the component fidelity ledger; re-verify before quoting**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `4` -- in the FOUNDATIONAL tier (above the
> downstream meaning-wiring/parser), below the three blocking/central foundations already in flight
> (representation p1, memory-read p2, binding p3). It is the brain's core LEARNING + UPDATE signal, so it is
> foundational; but it is diffuse (it touches the encoder objective, the plasticity gate, and situation-model
> segmentation), so the solver should pick the single highest-leverage entry, not boil the ocean. Re-rank freely.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do. If you have
> not identified the brain's mechanism and attempted to build it, you have not started the real work,
> whatever else you have measured.
>
> **🚀 YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> You are NOT boxed in -- not by this brief, not by the existing organs, not by the integration points you
> would tie into: if a MORE brain-foundational method conflicts with any of them, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful). Exploring
> the brain's true method is the work we most want from you; a bold, well-argued brain-faithful direction --
> even unfinished -- beats a tidy engineering result that never asked the question.
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several of your angles hit the
> SAME wall, that is strong evidence that NONE of them was the brain's mechanism -- the faithful method is
> probably DIFFERENT IN KIND, not another variation of what you already tried. A wall is a FIDELITY GAP TO
> BUILD ACROSS, never a ceiling. Hitting one is exactly the moment to LEAVE the family of methods you were
> sweeping and ask the biology again.
>
> **⛔ "CONVERGED" HAS A HIGH BAR, AND EXHAUSTING ENGINEERING VARIATIONS DOES NOT MEET IT.** Claim
> convergence ONLY when you have (a) identified how the brain actually performs this computation AND (b)
> replicated that operation as faithfully as you can and tested it, OR shown with a SPECIFIC reason why it
> cannot be replicated here. "I tried several combining / gating / scoring angles and they all plateaued at
> the same wall" is NOT converged -- it is tuning-limited, and it means the brain's mechanism is still
> UN-TRIED. That is a reason to explore harder, not to submit.
>
> **🔁 THE 30-MIN DEEPENING IS HOW YOU FORCE THIS -- IT IS NOT OPTIONAL BUSYWORK.** Run your own cron
> (`CronCreate "13,43 * * * *"`); each fire asks "how does the brain REALLY do this, one level deeper than
> my current mechanism?" -> implement -> test (can-fail, strongest real floor, info-free twin LOSING) ->
> iterate. Its whole purpose is to make you ask the brain question several more times than your own sense of
> "done" would. CANCEL it (`CronDelete`) and submit ONLY when the brain-mechanism bar above is met.
> Declining it because "my angles converged" is precisely the case it exists to catch.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully
> built.** A negative on a family of convenient engineering methods is not a negative on the capability; it
> is a report that you have not yet found how the brain does it.
>
> **📖 REFERENCE THE BRAIN-FOUNDATIONAL AUDIT, AND HELP KEEP IT TRUE.** Before you start, read the entry for the
> system you are touching in `notes/BRAIN_FOUNDATIONAL_AUDIT.md` -- it gives the brain structure, whether the
> brain's equation is PINNED or something we are INVENTING, our current fidelity, and the known deviation, so you
> inherit that instead of re-deriving it. If your work shows a verdict there is WRONG, STALE, or INCOMPLETE, or you
> find a NEW deviation, put a short **AUDIT UPDATE** note in your submission -- the strategy session folds it into
> the audit at integration. The audit is a living, shared map and you help maintain it.

## 1. THE PROBLEM IN PLAIN LANGUAGE

The brain runs one computation almost everywhere: it constantly PREDICTS what comes next, and when it is wrong,
that surprise -- the PREDICTION ERROR -- is both the signal it LEARNS from and the cue to UPDATE its model of
what is happening. Read "the surgeon picked up the..." and your brain predicts "scalpel"; if the next word is
"hammer," the jolt of surprise is what updates your understanding and what you remember. We do neither of these
the brain's way:
- **We LEARN by fill-in-the-blank (bidirectional cloze), not forward prediction.** Our encoder is trained to
  reconstruct blanked words using both sides of the sentence -- which is not how the brain's forward, moment-to-
  moment prediction works, and it is a different learning signal entirely.
- **We do not UPDATE on surprise.** We have a prediction-error organ, but it is unwired and never fires; and the
  reader has NO signal for "the situation just changed" (the brain's N400 surprise response) -- so it cannot tell
  where one event ends and the next begins, which is exactly when a comprehender writes to memory.
This is the most pervasive brain computation we are missing. The question: does a brain-faithful prediction-error
signal -- forward, precision-weighted -- actually beat what we do now, either as the LEARNING signal or as the
UPDATE/segmentation signal? A rigorous negative (the forward structure is already latent, PE does not help here)
is also a real, foundational result.

## 2. WHY THIS ONE

- **It is the brain's core principle, and it is foundational in two ways at once:** the LEARNING signal shapes
  every representation, and the UPDATE signal decides when the reader commits an event to memory. A wrong
  learning signal means representations learned the wrong way; a missing update signal means the reader cannot
  segment events at all.
- **The pieces half-exist and fail informatively:** `hdlab/predictive_coding.py` is built but WIRED NO and
  MIDDLE_BAND (its gate never fired at threshold 0.3), and its residual is computed on a `sign()`-quantised
  prediction -- so it cannot tell a big miss from a small one. That is a concrete, diagnosable starting point.
- **It is genuinely unqueued and genuinely foundational** (audit deviation #6) -- not a capability dressed up as
  a foundation.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED:** forward hierarchical predictive coding -- each level predicts the level below; the RESIDUAL
`x - x_hat` is the learning signal, and it is PRECISION-WEIGHTED (weight each error by how reliable that channel
is) (Rao & Ballard 1999; Friston free-energy). For comprehension specifically, the **N400 = the magnitude of the
update to the CURRENT situation model** (`||Delta situation_model||`), a prediction error against the running
discourse state (Rabovsky, Hansen & McClelland 2018; Kutas & Federmeier). Event segmentation is driven by
prediction-error spikes (Zacks-Franklin SEM): a boundary is where the model's prediction breaks.
**PINNED reference point, UNPINNED equation:** the reference (the current model state) is pinned; the exact norm
and the precision estimator are OURS to choose and test.
**OUR-INVENTION-UNDER-TEST:** how PE is computed and precision-weighted, and where it drives learning vs updating.
Copy the COMPUTATION (residual against a prediction, used as the learn/update signal); SWEEP the parameters
(window, precision estimator, threshold). Do NOT reach for a convenient auxiliary loss -- the point is the
forward-prediction-error signal.

## 4. MEASURED vs INFERRED

**MEASURED (ORGAN_MAP G1/G2/E2/F5 + component ledger, re-verify):**
- Encoder OBJECTIVE = bidirectional MLM cloze -- UNFAITHFUL to forward predictive coding; BUT `~+0.44` forward
  structure is already LATENT in the MLM reps (so the objective may or may not be the bottleneck -- that is the
  test).
- `hdlab/predictive_coding.py` (G2): `predict = sign(W@key)`; residual-gated Hebbian; `residual = 0.5(1-cos)` (a
  cosine scalar, NOT an L2 residual); NO precision term; WIRED NO; MIDDLE_BAND (the gate never fired at thresh
  0.3). The residual is computed on a `sign()`-quantised prediction -- big and small misses look identical
  (couples to p1, the representation fix).
- Situation-model register (E2) has NO PE-driven segmentation -- nothing decides WHEN to write. The N400 monitor
  (F5, `||Delta situation_model||`) is MISSING outright.
**INFERRED (the open question, decisive either way):** whether a brain-faithful prediction-error signal (forward,
precision-weighted, on a NON-quantised prediction) beats the current approach -- as the LEARNING term (vs cloze)
OR as the situation-model UPDATE/segmentation signal (vs none) -- on a downstream measure.

## 5. ALREADY TRIED (do not re-run)

- The ungated / cosine-scalar `predictive_coding.py` gate as-is -- MIDDLE_BAND, the gate never fired. Do NOT
  re-run it unchanged; the point is a FAITHFUL PE signal (forward, precision-weighted, L2 residual on a
  non-quantised prediction).
- Do NOT read the `+0.44` latent-forward-structure number as "PC is unnecessary" -- it is latent structure in
  cloze reps, not a test of a forward-PC learning term.
- Query `experiment_index.py query "predictive"`, `query "prediction error"`, `query "surprise"`,
  `query "segmentation"`, `query "N400"`; read `hdlab/predictive_coding.py`, `hdlab/situation_model_accumulate.py`
  and the encoder (`hdlab/composed_encoder_v3.py` / `concept_encoder.py`) before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Confirm the encoder objective is cloze/MLM and that `predictive_coding.py` is WIRED NO + MIDDLE_BAND with a
  cosine-scalar residual on a `sign()`-quantised prediction.
- Confirm the situation model has NO surprise/segmentation signal today (positive-control the absence: look for a
  place a boundary/update magnitude would be computed and show it is not).
- Pick your ENTRY (learning term vs situation-model update/segmentation) and build its instrument + floor. If you
  test the segmentation angle, the floor is a fixed/random segmentation; if the learning angle, the floor is the
  cloze-trained reps on the SAME downstream measure.

## 7. THE BAR

Pick the single highest-leverage entry. On a held-out downstream measure with the floor recomputed on its
population: **a brain-faithful prediction-error mechanism (forward, precision-weighted, residual on a NON-quantised
prediction) must beat the current baseline CI-separated over the strongest floor's UPPER bound, info-free twin
LOSING** (scrambled prediction / permuted surprise), CI half-width + null p95 reported. Two admissible framings,
either one qualifies:
- **LEARNING:** reps trained with a forward-PC term beat cloze-trained reps on a downstream comprehension/meaning
  measure.
- **UPDATE/SEGMENTATION:** a PE-driven "when to write / event boundary" signal (the N400 `||Delta model||`) beats
  fixed/random segmentation at getting the right thing into the situation model.
**DECISIVE EITHER WAY:** a win -> propose the hdlab change (strategy lands it; note the p1 coupling -- the residual
must be computed on a graded, not `sign()`-quantised, prediction). A rigorous loss -> report that forward PE does
NOT help here (the forward structure is already latent / the ungated update is sufficient); that closes a
foundational question and is a full PASS.

## 8. FILES AND ENTRY POINTS

- `hdlab/predictive_coding.py` (G2 -- the islanded PE gate), `hdlab/situation_model_accumulate.py` /
  `hdlab/event_bundle.py` (E2 -- the register with no PE-segmentation), the encoder
  (`hdlab/composed_encoder_v3.py` / `concept_encoder.py`, G1 -- the cloze objective).
- `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (deviation #6; TIER 5 prediction; TIER 3 F5/E2) + ORGAN_MAP G1/G2/E2/F5 --
  report any correction as an AUDIT UPDATE.
- Prove in `experiments/` + `verification/`; propose the hdlab diff in `SOLVED.md` (strategy lands it, Q111). Do
  NOT write `hdlab/`.

## DO NOT QUOTE / DO NOT REDO

- Do NOT quote the `+0.44` latent-forward-structure as evidence PC is unnecessary -- it is not a test of a
  forward-PC learning term.
- Do NOT compute the residual on a `sign()`-quantised prediction -- that is the p1 deviation confounding this one;
  use a graded prediction, and say so.
- Do NOT carry a number between the learning-angle and segmentation-angle instruments -- different scorers/
  populations; recompute the floor on whichever you run.
