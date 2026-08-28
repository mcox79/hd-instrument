---
priority: 3
review:
review_text:
---

# PROBLEM: the reader cannot CHOOSE what to read next — its "readable universe" is a hard-coded 4-entry dict against ~34 corpora on disk, and the foraging organ has never seen real text (FROZEN beats FORAGE) — build the brain-faithful reading-foraging policy (MVT leave-rule + value-of-information from the gap/novelty signal, EVC-gated halting) that picks the next reading to maximize learning value, beating frozen-order AND random selection with an info-free twin losing

**slug:** `the_reader_cannot_choose_what_to_read_next` — **opened:** 2026-08-27 by the strategy session (owner asked for a
second high-leverage solver problem to run in parallel with the learner). **status:** OPEN — a MECHANISM-DISCOVERY + BUILD
problem. You build + validate in `experiments/`; strategy lands any hdlab change (Q111). Clean baseline to beat, can-fail bar.

> **PRIORITY NOTE (the call is the strategy session's):** filed at `3`, below the learner (p2). This is the OTHER half of a
> self-growing reader: the learner is HOW to learn from a text; THIS is WHICH text to read next. Independent of p1 and of the
> learner's rule-optimization, so it runs cleanly in parallel. Re-rank per the owner.

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
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch (attention / information foraging;
> metacognition / gap detection); inherit its PINNED/INVENTED verdicts; put a short **AUDIT UPDATE** in your submission.

## 1. THE PROBLEM IN PLAIN LANGUAGE

For the reader to grow by reading, it has to decide WHAT to read next — and right now it can't. Its entire list of things
it is "allowed to read" is a **hard-coded 4-entry dictionary**, even though **~34 text collections sit on disk** (novels,
graded readers, science texts, QA sets). And the part of it that is supposed to decide "keep reading here vs move on to
something else" **has never actually seen real text** — when it was tried, just reading everything in a fixed order (FROZEN)
beat it (FORAGE). So the reader is a passive consumer of whatever it's fed, in whatever order.

Build the brain's mechanism for **choosing what to read next** — the way an animal forages for food, spending effort where
the payoff rate is high and leaving a patch when it drops off — and show that a reader which CHOOSES its reading learns more
(or covers more) than one that reads in a fixed order or at random.

## 2. WHY THIS ONE

It is the OTHER half of a self-growing reader. The learner problem (`optimize_and_validate_the_learner...`) is HOW to learn
from a text; this is WHICH text to read. Autonomous foundation-growth needs BOTH — without foraging, growth is passive and
undirected. It is also a clean, currently-MISSING, brain-foundational capability with a rich pinned theory and a ready-made
value signal already built (the gap detector). And it is INDEPENDENT of p1 and of the learner's rule, so it runs in parallel.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)

- **PINNED — information foraging + the Marginal Value Theorem.** Organisms forage information like food (Pirolli & Card,
  Information Foraging Theory). The MVT leave-rule (Charnov 1976): leave the current patch when its INSTANTANEOUS intake rate
  drops below the ENVIRONMENT'S AVERAGE rate. For reading: keep reading the current source while it is still teaching you
  fast; move on when its rate of new learning falls below what you'd get elsewhere. **The substrate HAS this leave-rule
  (`hdlab/information_foraging.py`) but it "has never seen real text" and was downgraded to MIDDLE_BAND (FROZEN beats
  FORAGE)** — that is the wall to build across, not a settled answer.
- **PINNED — the neural substrate of the leave/switch decision.** The dorsal ACC computes foraging value — the value of
  LEAVING/switching (Kolling, Behrens, Rushworth 2012); the Expected Value of Control (Shenhav, Botvinick & Cohen 2013)
  gates how much effort to spend. The substrate's `self_manager.py` has the ACC/EVC halting hooks.
- **PINNED — the VALUE signal is curiosity / learning progress / novelty.** What makes reading "valuable" is information gain
  / reducible uncertainty (Oudeyer & Kaplan learning-progress; Gottlieb information-seeking; the LC-NE novelty/surprise
  signal). **The substrate's `gap_detector.py` is "the healthiest organ" (AUC 1.000) but its output "has nowhere to go
  because foraging is unbuilt"** — so the value signal you need is BUILT and validated; CONSUME it, do not rebuild it.
- **OUR-INVENTION-UNDER-TEST:** the exact value function (learning-gain vs coverage vs novelty vs gap-closing) and the
  patch/leave granularity (document, section, sentence). **COPY the computation** (MVT leave-rule driven by a value-of-
  information signal, EVC-gated), **SWEEP the parameters** (the environment-average estimate, the leave threshold, the value
  weighting) — do NOT hand-tune a heuristic and call it foraging.

## 4. MEASURED vs INFERRED
- **MEASURED:** the readable universe is a 4-entry dict (`hdlab/corpus_registry.py` docstring: "28 of 36 readable") vs ~34
  corpora on disk (`data/corpora/`); the MVT leave-rule exists but is MIDDLE_BAND (FROZEN beats FORAGE, never saw real text);
  `gap_detector` AUC 1.000 (the value signal, unconsumed).
- **INFERRED (to test):** a brain-faithful foraging policy that consumes the gap/novelty signal to choose the next reading
  BEATS frozen-order + random selection on a real learning/coverage metric. UNPROVEN — could be null (a valid PASS).

## 5. ALREADY TRIED / DO NOT RE-RUN
- The MVT leave-rule EXISTS (`information_foraging.py`) — build ON it, do not re-derive it. The FROZEN-beats-FORAGE
  MIDDLE_BAND is the CURRENT WALL (foraging never saw real text) — break it, do not treat it as the verdict.
- `gap_detector` works (AUC 1.000) — CONSUME its signal as the value-of-information; do NOT rebuild a gap detector.
- The reading EXTRACTOR ("what to write from a text") is a SEPARATE, already-integrated problem — this is "what to READ", not
  "what to extract".

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/information_foraging.py` (the MVT leave-rule), `hdlab/gap_driven_reader.py`, `hdlab/gap_detector.py` (the value
  signal), `hdlab/corpus_registry.py` (THE SHELF — the enumerable ~34-corpus universe), `hdlab/self_manager.py` (ACC/EVC halting).
- Confirm the 4-entry readable universe + enumerate the corpora on disk (`data/corpora/`).
- Read `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (attention/foraging; metacognition/gap-detection).

## 7. THE BAR
PASSES only with ALL of:
1. **A brain-faithful reading-foraging policy that BEATS both baselines CI-separated:** choosing what to read next across the
   real ~34-corpus shelf, it beats (a) FROZEN fixed-order reading AND (b) RANDOM selection, on a real DOWNSTREAM metric —
   learning gain on held-out meaning golds (SimLex/SimVerb/WordSim ρ after reading a fixed budget), OR coverage of a target
   vocabulary/relation set per unit reading. Recompute each floor's upper bound; info-free twin (shuffled value signal /
   random leave-timing) LOSES CI-separated. Report CI half-width + null p95. NO number crosses populations/scorers.
2. **BREAKS the current wall:** beat the FROZEN baseline that currently beats foraging — on REAL text, not a synthetic patch.
3. **Brain-faithful MECHANISM (not a tuned heuristic):** the leave decision is the MVT rule (leave when local rate < the
   estimated environment average); the value is information-gain / novelty from the `gap_detector` signal (CONSUMED, not
   re-invented); the effort/halt is EVC-gated. State the operation. COPY the computation, SWEEP the parameters.
4. **Propose the exact hdlab diff** (the foraging policy consuming gap_detector + the MVT leave-rule over the enumerable
   corpus_registry shelf) for strategy to land, default-off. Do NOT enable autonomous live reading — this proves the POLICY
   is better; turning it loose on live growth is a separate gated step (and depends on the learner's safety gate).
A rigorous NEGATIVE — a faithfully-built foraging policy that sees real text still does NOT beat frozen/random — is a FULL
PASS, localising WHY (value signal too weak on these corpora / the corpora too homogeneous to reward selection / the leave
granularity wrong), which itself tells strategy whether directed reading is worth turning on.

## 8. FILES AND ENTRY POINTS
- Organs: `hdlab/information_foraging.py`, `hdlab/gap_driven_reader.py`, `hdlab/gap_detector.py`, `hdlab/corpus_registry.py`,
  `hdlab/self_manager.py`.
- Corpora: `data/corpora/` (~34 collections). Meaning golds for the learning-gain metric: SimLex-999 / SimVerb-3500 /
  WordSim-353 (as used by `experiments/exp_learn_from_reading_strong_arm_v1.py`).
- **Route heavy corpus-scale reading runs to the REMOTE GPU box** (`tools/queue_add.py`; standing rule: heavy/long runs go remote).
- Audit: `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (attention / information foraging; metacognition).

## DO NOT QUOTE / DO NOT REDO
The MVT leave-rule and the gap detector are PRIOR WORK to build ON, not to reproduce. Do NOT enable autonomous live reading /
foundation-growth — this problem proves the SELECTION POLICY is better than frozen/random; turning it loose is a separate,
owner-gated step. Strategy owns the hdlab landing — you propose the diff, you do not write `hdlab/`.
