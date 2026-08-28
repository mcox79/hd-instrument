---
priority: 2
review:
review_text:
---

# PROBLEM: the learn-from-reading learner is PROVEN-worth-continuing but UN-OPTIMISED (a crude batch PPMI-SVD, not the brain's online predictive rule) and NEVER validated to IMPROVE the updated substrate — build the most brain-faithful learner, prove it beats the PPMI baseline AND net-improves the current reader's meaning (fused, demand-routed, controls losing) with a hard SAFETY gate, BEFORE it is ever turned on to grow the foundation

**slug:** `optimize_and_validate_the_learner_before_it_grows_the_foundation` — **opened:** 2026-08-27 by the strategy session
(owner-directed: *"set the learner as a problem to optimize before you turn it on… validate the shit out of it with the
updated substrate before it starts growing the foundation."*). **status:** OPEN — a MECHANISM-OPTIMISATION + SAFETY-VALIDATION
problem. You optimise + validate in `experiments/`; strategy lands any hdlab change (Q111). There is a concrete baseline to
beat, a hard safety gate, and a can-fail bar. **DO NOT turn the learner on / write to the foundation — this problem decides
whether it is SAFE to, it does not do the growing.**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `2`, below p1 (`build_the_composed_scalar_magnitude_meaning_channel`,
> which is SOLVED and integrating). This is the GATEWAY to autonomous foundation-growth and is SAFETY-CRITICAL (an
> un-validated learner that writes to the foundation compounds its own errors), so it ranks above the phase-diagram audit. Re-rank per the owner.

> **🔗 HARD DEPENDENCY — p1 MUST BE LANDED FIRST (owner 2026-08-27):** the substrate-validation half of this problem
> (BAR #3 + #4) must run against the *complete* updated meaning system, which includes p1's `scalar_adjective_operation`
> ruler + the word-class operation-router (currently SOLVED, awaiting the owner's verdict → strategy integrates it, then
> this). Validating the learner against a substrate still missing p1 would measure a stale, moving target. **Sequencing:**
> you MAY start the p1-INDEPENDENT half immediately — optimise the learning RULE and beat the PPMI-SVD baseline (BAR #1 +
> #2). Do the substrate-fusion + safety-gate validation (BAR #3 + #4) only after the strategy session confirms p1 is
> LANDED (watch `hdlab/scalar_adjective_operation.py` + the routed meaning read-out; the brief will be updated when it lands).

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau — it is the FIRST thing you do.
>
> **🚀 YOU ARE ENABLED — AND EXPECTED — TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **⛔ "CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **🔁 THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) — RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one — and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill — do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across — never a ceiling.
> Each fire: implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS — but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch (cortical learning rule; CLS; the
> meaning channels); inherit its PINNED/INVENTED verdicts; put a short **AUDIT UPDATE** in your submission for any
> verdict you find wrong/stale or any new deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE

We proved the reader CAN learn word meaning from reading raw text — a meaning-space read from 38 million words of Simple
Wikipedia beats the strongest baselines by 15–40× and is STILL improving when the text runs out (it's limited by how much
we fed it, not by the idea). That's exciting: it's the door to the reader growing its own knowledge by reading. But two
things are NOT yet true, and both must be before we open that door:

1. **The learner is crude, not brain-faithful.** It's a batch statistical recipe (count word co-occurrences, factorise the
   matrix — PPMI-SVD). The brain does NOT learn that way: it learns **online, one encounter at a time, by prediction error**
   (it predicts the next word / the missing meaning, and adjusts when it's wrong), with fast episodic memory feeding slow
   cortical statistics over time. Build the **best, most brain-faithful learner** and show it beats the crude recipe.
2. **We never checked the learner actually makes the CURRENT reader better** — only that it beats floors in isolation. Before
   it writes anything into the reader's permanent knowledge, prove it is a **net improvement** to the *updated* substrate,
   not a corruption of the meaning the reader already gets right. Because once it starts growing the foundation, its
   mistakes compound — so the bar for "turn it on" is high and this problem is where it's earned.

## 2. WHY THIS ONE

It is the GATEWAY to autonomous foundation-growth (the reader learning by itself) AND it is safety-critical: an
un-validated learner that writes to the foundation poisons the well. The capability is proven and corpus-limited (still
climbing), so the leverage is now in (a) the LEARNING RULE's fidelity and (b) proving it safely improves the *updated*
substrate. Get this right and we can turn on a self-growing reader with confidence; get it wrong quietly and every future
result inherits the corruption.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)

- **PINNED (computational level):** word meaning IS shaped by distributional co-occurrence statistics (the distributional
  hypothesis; Landauer & Dumais LSA; Firth). Learning meaning from reading is a real cortical capability. Q116 settled that
  it is worth continuing.
- **PINNED (the MECHANISM the current learner violates):** cortical learning is **error-driven and online**, not batch
  matrix factorisation. Predictive coding (Rao & Ballard; Friston) — the cortex predicts and learns from the residual;
  this is the substrate's own `predictive_reader` at the word level. Hebbian/associative plasticity accumulates
  co-occurrence *incrementally*. Complementary Learning Systems (McClelland/O'Reilly/Norman): the hippocampus fast-binds
  each episode, and slow cortical semantics are consolidated by **replay** — so the "batch" is really replay-interleaved
  online learning, not a one-shot SVD. **The current `hdlab/learner/core.py` uses MDL model-selection — WRONG-OP (not a
  synaptic update rule) — and the loop "was never measured as a learner" (audit).**
- **OUR-INVENTION-UNDER-TEST:** the exact learning rule + architecture. PPMI-SVD is a computational-level STAND-IN; the
  brain-faithful learner is an **online predictive/Hebbian rule** (predict the context/next word, update on error), optionally
  replay-interleaved (CLS). **COPY the computation** (predictive distributional learning), **SWEEP the parameters** (window,
  dimensionality, surprise/precision weighting, learning rate, replay schedule) — do NOT adopt PPMI-SVD's shape as if pinned.
- **The routing that keeps it faithful (do NOT fuse blindly):** the learned DISTRIBUTIONAL channel is an ASSOCIATIVE/
  relatedness system; `hdlab/conceptual_meaning` is the ATL IDENTITY system. The integrated p3 work PINNED a DOUBLE
  DISSOCIATION (distributional→relatedness, conceptual→identity). So the learned channel must be DEMAND-ROUTED / fused-for-
  rating alongside conceptual_meaning, NOT collapsed into one — exactly the split already validated.

## 4. MEASURED vs INFERRED
- **MEASURED (Q116 `does_learning_from_reading_deserve_to_continue`, owner-DONE — the BASELINE to beat):** the strong arm =
  surprise-weighted PPMI(-SVD) over a word×word co-occurrence matrix from simplewiki (38.09M tokens, vocab 60,085),
  UNFITTED. SimLex-999 ρ 0.2552, SimVerb-3500 ρ 0.1290, WordSim-353 ρ 0.6301 — clears the strongest floors (orthographic,
  idf-count) CI-separated by 15–40×; STILL CLIMBING at the corpus ceiling on all three. Fusion with the supplied grounded
  hub beats hub-alone on WordSim (+0.2096 CI-sep). Population-dependent: WINS relatedness (WordSim), TIES broad similarity
  (SimLex), LOSES verbs (SimVerb). Harness `experiments/exp_learn_from_reading_strong_arm_v1.py`.
- **INFERRED (to test):** a brain-faithful ONLINE PREDICTIVE learner beats the batch PPMI-SVD arm; and the learned channel,
  fused/routed into the UPDATED substrate, NET-IMPROVES its meaning read without regressing what conceptual_meaning already
  wins; and growing the foundation with it is a demonstrable net positive. All UNPROVEN — any could be null (a valid PASS).

## 5. ALREADY TRIED / DO NOT RE-RUN
- The PPMI-SVD strong arm IS the baseline (Q116) — reverify it, then BEAT it; do NOT re-derive it as your result.
- Do NOT re-open "does learning from reading deserve to continue" — answered YES (corpus-limited, still climbing).
- Do NOT turn the learner on / write to the live foundation — this problem decides IF it's safe; the growing is a separate,
  gated step strategy runs only after this passes.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Reverify the baseline: `.venv/Scripts/python.exe verification/test_learn_from_reading_strong_arm.py`.
- Read `hdlab/learner/core.py` (the current MDL learner — the WRONG-OP to replace), `hdlab/predictive_reader.py` (the
  word/feature-level online predictor to build ON), `hdlab/conceptual_meaning.py` + `hdlab/convergent_cue_reader.py` (the
  updated-substrate meaning channels you must fuse/route WITH, not replace).
- Read the Q116 SOLVED + `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (cortical learning rule; CLS; the two-meaning-system split).

## 7. THE BAR
PASSES only with ALL of:
1. **Beats the PPMI-SVD baseline CI-separated** on ≥2 held-out meaning populations, its own strongest floor recomputed per
   population, info-free twin (shuffled co-occurrence / random-init / scrambled reading order) LOSING CI-separated. Report CI
   half-width + null p95. NO number crosses populations/scorers.
2. **Brain-faithful learning RULE:** an ONLINE, error-driven/Hebbian (optionally replay-interleaved CLS) update — NOT batch
   PPMI-SVD — OR a specific, argued reason the batch form IS the computational optimum and the online rule converges to it.
   State the operation (what is predicted, what the error is, how the update works). COPY the computation, SWEEP the params.
3. **NET-IMPROVES THE UPDATED SUBSTRATE (the owner's emphatic requirement — "validate the shit out of it"; p1 LANDED FIRST).**
   The "updated substrate" = the meaning system AFTER p1 lands (`conceptual_meaning` identity + `scalar_adjective_operation`
   magnitude/comparison + the word-class operation-router). Fused/demand-routed alongside these (distributional→relatedness,
   conceptual→identity, ruler→magnitude; the p3 dissociation + the p1 routing), the learned channel lifts the composed
   meaning read CI-separated on the axis it should win, AND does NOT regress what the OTHER channels already win (no
   CI-separated regression on identity/similarity/magnitude — a net-positive canonical-clean route, like the front-end
   hybrid and the operation-router). Show the dissociations are preserved (a fused-into-one-pool control loses). Run this
   half only after strategy confirms p1 is landed (see the HARD DEPENDENCY note above).
4. **THE SAFETY GATE — prove it is safe to GROW the foundation with, before turning it on.** A held-out test that growing the
   substrate's meaning WITH the learner improves a DOWNSTREAM comprehension score (e.g. paraphrase who-did-what / relatedness
   comprehension), with an info-free GROWTH control (grow with shuffled / non-text / random co-occurrence) that must NOT help
   (and ideally HURT) — isolating that the gain is the REAL learned structure, not the act of writing. Quantify the
   corruption risk: does the learner ever DEGRADE a meaning the substrate had right? Report the rate + CI.
5. **Propose the exact hdlab diff** (the learned distributional channel + its fusion/routing into the meaning read-out; the
   online update rule) for strategy to land — WITHOUT enabling foundation-growth (default-off; growth is a separate gated step).
A rigorous NEGATIVE — the best brain-faithful learner does NOT beat PPMI-SVD, or does NOT safely improve the updated
substrate — is a FULL PASS: it says "do not turn it on yet," and why (which sub-bar failed).

## 8. FILES AND ENTRY POINTS
- Baseline: `experiments/exp_learn_from_reading_strong_arm_v1.py`, `verification/test_learn_from_reading_strong_arm.py`.
- Learner + substrate: `hdlab/learner/core.py`, `hdlab/predictive_reader.py`, `hdlab/conceptual_meaning.py`,
  `hdlab/convergent_cue_reader.py`, `hdlab/semantic_control.py`.
- Corpora: simplewiki (Q116's source) + the meaning golds (SimLex/SimVerb/WordSim); read golds via the harness's loaders.
- **Route the heavy corpus-scale runs to the REMOTE GPU box** (`tools/queue_add.py`; standing rule: heavy/long runs go remote).
- Audit: `notes/BRAIN_FOUNDATIONAL_AUDIT.md`. Q116 SOLVED for the proven baseline + the fusion result.

## DO NOT QUOTE / DO NOT REDO
The PPMI-SVD numbers (SimLex 0.255 / SimVerb 0.129 / WordSim 0.630) are the BASELINE to beat, not results to reproduce.
Do NOT turn the learner on or write to the live foundation. Strategy owns any hdlab landing — you propose the diff, you do
not write `hdlab/`, and foundation-growth stays OFF until this problem's safety gate passes and the owner authorises it.
