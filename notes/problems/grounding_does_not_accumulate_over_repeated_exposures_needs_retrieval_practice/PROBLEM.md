---
priority: 3
review:
review_text:
---

# PROBLEM: growing word-meaning by reading does NOT consolidate REPEATED EXPOSURES — a word can be read 4+ times and still never ground, because the acquisition pass is one-shot around a confidence threshold and exposures do NOT accumulate. The measured wall (integrated `the_reader_cannot_choose_what_to_read_next` depth diagnostic, `exp_reading_grounding_depth_diagnostic_v1.py`): the reader REACHES 5.2× more register-controlled target vocab than it GROUNDS (reached 0.338 vs learned 0.064), and **66% of probe words read ≥4× never ground** — decomposed as **59% `CONSOLIDATION_FAIL`** (≥4 coherent traces, the single-averaging consolidation never grounds them) + 36% `TAUTOLOGY_NO_ANCHOR` (abstract words that cannot canonicalize → the separate `reader_meaning_channel`/ATL problem) + 4% correct closed-class refusals + 1% extraction miss. This problem is the 59% CONSOLIDATION_FAIL wall ONLY: **why do repeated coherent exposures of the SAME word not accumulate into durable grounding, and does the brain's mechanism — RETRIEVAL PRACTICE (the testing effect) — fix it?** The brain does not consolidate by re-reading; it consolidates by RETRIEVING: each re-encounter, the learner RETRIEVES its current guess for the word's meaning and the ACT OF RETRIEVAL (not re-exposure) is what strengthens the durable trace (Karpicke & Roediger 2008 — testing produces ~2× long-term retention vs re-study at equal exposure). Build a retrieval-practice consolidation step for the grow-by-reading pass and prove it grounds the repeated-exposure words that single-averaging leaves un-grounded — or show, rigorously, that the 59% wall is representation-bound (not encoding-scheme-bound), which is a full PASS.

**slug:** `grounding_does_not_accumulate_over_repeated_exposures_needs_retrieval_practice` — **opened:** 2026-08-31 by the
strategy session (ARCHITECT HEARTBEAT; owner: "we're going to need another problem to assign very soon"). Surfaced by the
CONVERGENCE of two verdict-independent component scans (`definitional_extraction` writes garbage KB facts on narrative;
`information_foraging`, a high-fidelity MVT organ, cannot beat a fixed reading schedule) — BOTH bottlenecked DOWNSTREAM on
consolidation. **status:** OPEN — a BUILD problem. Fix-site named by the depth diagnostic: `hdlab/grounding_acquisition_loop.py`
+ `substrate.py::profile()` (the shared Library/Trace/consolidation_pass path). You build + validate in `experiments/`;
strategy lands any hdlab wire (Q111, default-off flag, witness required). Glass-box, NO external LLM at inference.

> **PRIORITY NOTE (the call is the strategy session's):** filed at `3` — HIGH. This is the CLEAN-FOUNDATION lever the
> North Star (learner-on) most needs RIGHT NOW: the learner live-canary (p3) just PROVED growth is SAFE + beneficial, so
> the next question is making growth STICK — a word read many times should become durably known. Ranked below
> prediction-error (p2, the reasoning lever, already SOLVED-awaiting-review) and above the binding backbone (p4) / belief
> (p5) / reasoning (p6) because it is the measured bottleneck that CAPS every input-side organ (two scans converge here)
> and it is the direct upstream of "clean enough to flip the learner on." **Re-rank per the owner.** ⚠️ Prior-work
> checked (`experiment_index.py query "retrieval practice"` = 0 cells; `"grounding depth"` = 0): the RETRIEVAL-PRACTICE
> angle is genuinely un-built. `one_store_does_two_jobs_and_consolidation_is_a_single_average` (PARTIAL) studied
> interleaved/selective REPLAY for catastrophic FORGETTING and found forgetting is NOT the live constraint (the live
> single-average store is separable-row, never forgets) — a DIFFERENT axis. This problem is DURABLE ENCODING of repeated
> exposures (does a trace STRENGTHEN with retrieval), not retention against interference.

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
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps — AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) — that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill — do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across — never a ceiling.
> Each fire: implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS — but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When the reader learns word meanings by reading, a word it meets four or more times should end up known. It doesn't: about
two-thirds of the words it read ≥4 times never get a durable meaning, and most of that is because the "make it stick" step
just averages the encounters together — which never crosses the line into "known." That is not how brains build durable
memory. Brains build it by TESTING: each time you meet the word again, you first try to RECALL what it means, and the act of
recalling (not just seeing it again) is what strengthens the memory. This is the "testing effect": being quizzed on
something makes it stick far better than re-reading it the same number of times. So: rebuild the "make it stick" step so
that on each re-encounter the reader RETRIEVES its current best guess for the word and strengthens the trace when retrieval
succeeds — and show that words which were read many times but never stuck now stick. If, when you build it faithfully, they
STILL don't stick, that is a real and useful answer too (it would mean the wall is about how meaning is represented, not how
it is consolidated) — say so with the evidence.

## 2. WHY THIS ONE
It is the measured bottleneck that caps the whole clean-foundation program. TWO independent component scans (2026-08-31)
converged here: the definition-reader writes junk into the knowledge base on stories, and the (brain-faithful) "what to
read next" organ cannot beat a fixed schedule — both because the DOWNSTREAM consolidation loses the gains. And the learner
live-canary (p3, just integrated) proved growth is SAFE + beneficial — so the next thing standing between us and flipping
learning ON is making growth actually STICK. Reaching 5.2× more target words than we ground (0.338 reached vs 0.064 learned)
means the input side already works; the loss is durable encoding.

## MEASURED vs INFERRED
- **MEASURED (inherit; do NOT re-derive):** the depth wall itself — `exp_reading_grounding_depth_diagnostic_v1.py`
  (integrated `the_reader_cannot_choose_what_to_read_next`, CI_050, 3000 sentences): reached 0.338 vs learned 0.064 (5.2×
  gap); **66% of words read ≥4× never ground = 59% `CONSOLIDATION_FAIL` + 36% `TAUTOLOGY_NO_ANCHOR` + 4% closed-class +
  1% miss**; `P(ground | k encounters)` is flat/falling past k=4 (grounding is one-shot around `MIN_CONFIRM`, exposures do
  not accumulate). That the live single-average store is separable-row and NEVER forgets (`one_store…single_average` fork
  D) — so FORGETTING is not the constraint. These are the MOTIVATION; do not quote them as your result.
- **INFERRED (you must measure):** whether a brain-faithful RETRIEVAL-PRACTICE consolidation step durably grounds the
  ≥4×-read `CONSOLIDATION_FAIL` words that single-averaging leaves un-grounded, CI-separated over an EXPOSURE-MATCHED
  re-read arm + an info-free twin — i.e. whether the testing effect exists in this substrate, or the wall is
  representation-bound (a full-PASS negative).

## ALREADY TRIED / DO NOT RE-RUN
- `one_store_does_two_jobs_and_consolidation_is_a_single_average` (integrated PARTIAL) — studied interleaved/SELECTIVE
  REPLAY for catastrophic FORGETTING; found sparse pattern-separation is the anti-forgetting lever and that forgetting is
  NOT the live constraint. DIFFERENT axis (retention vs interference). Do NOT re-run a replay-for-forgetting study.
- `interleaved replay` cells exist (`exp_cls_distributed_protection_heldout_replay_v1`, HARD_PASS 2026-07-18) — that is
  distributed PROTECTION of existing memories, not durable ENCODING of repeated new exposures. Prior-work verified:
  `experiment_index.py query "retrieval practice"` = 0 cells; `"grounding depth"` = 0 — this angle is un-built.
- Do NOT re-derive the extractor floor (`the_grow_by_reading_pass_has_no_floor`, integrated) — extraction quality is a
  separate, solved axis; this is DURABLE CONSOLIDATION of what is extracted.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/grounding_acquisition_loop.py` + `hdlab/substrate.py::profile()` — find WHERE a re-encounter updates the
  trace (the single-average / `MIN_CONFIRM` one-shot site) and WHY exposures do not accumulate. Read
  `experiments/exp_reading_grounding_depth_diagnostic_v1.py` (`wall_decomposition`, the `P(ground|k)` curve) to get the
  EXACT `CONSOLIDATION_FAIL` population you must ground.
- Confirm on disk that the update is exposure-count-driven, not retrieval-gated (the premise). Run a positive control that
  the current pass really does plateau past k=4 before you change it.
- Reuse `hdlab/cls_growth.py` (keep-both fusion + rollback + anti-drift anchor) for any reversible store update. Pick a
  MODERN held-out grounding gold; do NOT mix eras (corpus-age confound). Read `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the
  2026-08-31 `information_foraging` + `definitional_extraction` scans that converge here) and fold an AUDIT UPDATE.

## 3. HOW THE BRAIN DOES THIS (the opening move)
**PINNED — the testing effect / retrieval-induced consolidation.** Karpicke & Roediger 2008 (Science 319:966): retrieval
practice produces ~2× long-term retention over re-study at EQUAL exposure — retrieval is a memory MODIFIER, not a neutral
read-out. Mechanistically: a successful retrieval reactivates and RE-CONSOLIDATES the hippocampal→neocortical trace
(Antony et al. 2017 retrieval-as-a-fast-route-to-consolidation; Roediger & Butler 2011); errors during retrieval, when
CORRECTED, further boost encoding (the "desirable difficulty"). Spacing interacts (spaced retrieval > massed). The
computation to COPY: on each re-encounter of a word, RETRIEVE the current meaning estimate, SCORE the retrieval (hit /
near-miss / miss), and STRENGTHEN the durable trace as a function of retrieval SUCCESS (and correction on miss) — NOT as a
function of raw re-exposure count. This is why re-reading (the current single-average) plateaus while retrieval accumulates.

## 4. PINNED vs OUR-INVENTION (copy the computation, sweep the parameter)
- **PINNED (COPY exactly):** retrieval-gated strengthening — the trace update is driven by the ACT + OUTCOME of retrieval,
  not by exposure count; spaced > massed; corrected-error boosts encoding.
- **OUR-INVENTION-UNDER-TEST (SWEEP, do not adopt a number):** the retrieval scorer's hit/near-miss threshold, the
  strengthening step size, the spacing schedule, the trace representation used for retrieval. These derive from constraints
  we do not share; sweep them, report the frontier, never hard-code a borrowed constant.

## 5. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
PASS = a RETRIEVAL-PRACTICE consolidation arm durably GROUNDS the repeated-exposure words that the current single-averaging
pass leaves un-grounded, CI-SEPARATED over BOTH: (a) the incumbent SINGLE-AVERAGE / RE-READ arm at EQUAL total exposure
(the exposure-matched control — this is the testing-effect design, retrieval vs re-study at equal exposure), AND (b) the
info-free TWIN (retrieval DECISIONS shuffled / random-strengthen at the same rate) — the twin MUST NOT help (ideally hurts).
Measured on the ≥4×-read `CONSOLIDATION_FAIL` population from the depth diagnostic, scored on HELD-OUT + MODERN grounding
gold (WordNet agreement or the register-controlled target-vocab grounding, the reader's own metric), with CIs + the null
p95 beside every margin. **A rigorous NEGATIVE is a full PASS if located:** if retrieval-practice, faithfully built and
exposure-matched, does NOT beat re-reading on this population, then the 59% wall is REPRESENTATION-bound (the trace can't
encode the distinction) not ENCODING-SCHEME-bound — name it, with the evidence (e.g. the retrieval scorer's own accuracy
ceiling on these words), and hand the representation gap to `reader_meaning_channel`/ATL.

## 6. FLOORS + CONTROLS (the strongest trivial methods, actually run)
- **Re-read / single-average arm at EQUAL exposure** (the incumbent; the testing-effect control — retrieval must beat
  re-study at matched exposure, else there is no testing effect).
- **Info-free twin:** shuffle the retrieval outcomes / strengthen at the same rate on RANDOM words (excludes "any extra
  update at this rate helps").
- **Exposure-count control:** strengthen purely by re-exposure count with no retrieval gate (excludes "more passes help").
- **Spaced vs massed** sweep (the PINNED spacing prediction is a positive control the mechanism should show).
- **Corrected-error arm** (miss→correct boosts encoding) vs miss-with-no-correction (the desirable-difficulty prediction).

## 7. CORPUS-AGE + GENERALIZATION (owner priority — a constructed-gold win is not a capability)
The grow-by-reading corpus is already modern (simplewiki); the EVAL grounding gold must be MODERN too (do not score archaic
McGuffey-era vocab on modern gold, or vice versa — the standing corpus-age confound). Report grounding on a HELD-OUT word
set the arm did not tune on, and generalize across at least two genres/registers. A gain that only shows on the tuning set
is not a capability.

## 8. FILES AND ENTRY POINTS
Build + validate in `experiments/` (fix-site reference: `hdlab/grounding_acquisition_loop.py`, `substrate.py::profile()`).
A scaffold-free witness recomputes, from source: durable-grounding rate on the `CONSOLIDATION_FAIL` ≥4×-read population for
the RETRIEVE arm vs the exposure-matched RE-READ arm vs the info-free twin, with CIs + null p95, on held-out + modern gold.
If it clears the bar, strategy lands the hdlab wire (Q111): a default-off retrieval-practice consolidation step in
`grounding_acquisition_loop`/`substrate.profile()`, witnessed, byte-identical when off. Fold an AUDIT UPDATE into
`BRAIN_FOUNDATIONAL_AUDIT.md` §2b.
Do NOT write `hdlab/` (Q111 — strategy lands the wire, default-off, witness required). Use the promoted `hdlab/cls_growth.py`
primitives (keep-both fusion + rollback + the anti-drift anchor) where a store update needs reversibility. STORE-write
hazards apply to any grounding-store write (binary/newline='', git-commit after every bank, NEVER `git add -A` the canonical
store, remote-persist needs USER auth). NO external LLM at inference.

## DO NOT QUOTE / DO NOT REDO
- 🚫 Do NOT quote the depth diagnostic's decomposition numbers (66% loss, 59% CONSOLIDATION_FAIL, reached 0.338 vs learned
  0.064) as YOUR result — they are the MOTIVATION (a different measurement); re-measure your grounding gain on your own
  exposure-matched population. No number crosses scorers/populations.
- 🚫 Do NOT re-run the REPLAY-for-forgetting study (`one_store_does_two_jobs_and_consolidation_is_a_single_average`,
  integrated) — forgetting is NOT the live constraint (the live single-average store is separable-row, never forgets). This
  is DURABLE ENCODING of repeated exposures via retrieval, a different axis.
- 🚫 Do NOT claim a testing effect without the EXPOSURE-MATCHED re-read control — retrieval beating re-study at EQUAL
  exposure is the whole point; a raw-exposure gain proves nothing.
- 🚫 Do NOT fix the 36% `TAUTOLOGY_NO_ANCHOR` (abstract-word) wall here — that is the `reader_meaning_channel`/ATL problem;
  this problem is the 59% consolidation wall only.
- 🚫 Do NOT lower a grounding threshold to manufacture grounding — that adds WRONG meanings (grounding precision is already
  marginal, ~35% WordNet-correct); the retrieval mechanism must RAISE durable-grounding precision, not trade it away.
