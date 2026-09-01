---
priority: 2
review:
review_text:
---

# PROBLEM: the reader takes its ONE batch parse AS TRUTH, where the brain parses PREDICTIVELY — it holds a distribution over structures, weights the noisy parse by a PRIOR over what is plausible, and REVISES when a prediction is violated. This parse-recall ceiling is the SHARED wall three integrated dimensions hit: who-did-what (p2 `the_forward_prediction_organ…`, EXCELLENT: the reader's residual errors are STRUCTURAL — it confidently binds the grammatically-DEFAULT entity, and "the ~half of errors surprisal misses are parse-COVERAGE failures whose only lever is a BETTER PARSER"), SPACE (`the_reader_has_no_spatial_location_dimension…`, STRONG: "parse-as-TRUTH sits AT the info-free null; the predict-and-revise PRIOR is the lever, a stronger parser does not help"), and BELIEF (`the_belief_dimension…`, EXCELLENT: location/status extraction is "the shared parser-recall ceiling"). The forward-prediction VIOLATION signal is now LIVE (`predict_surprisal` landed 2026-08-31 → `EventRecord.patient_surprisal`), so the missing half is the REVISION: recover the intended structure the single batch parse MISSED, by fusing the parse as EVIDENCE with a plausibility PRIOR and re-parsing where the prediction breaks. Build a predict-and-revise parse pass and prove it recovers who-did-what (and the arguments the batch parse drops) CI-separated over the batch parse-as-truth floor on real prose — or enumerate, precisely, that the residual is irreducible recall (no reading of the available signal recovers the missed structure), which localizes the ceiling and is a full PASS.

**slug:** `the_reader_parses_as_truth_where_the_brain_parses_predictively_predict_and_revise` — **opened:** 2026-08-31
by the strategy session (ARCHITECT HEARTBEAT; owner: "no open problems to assign once these 3 are done — what's the
plan?"). It is the CONVERGENT ceiling-lever three integrated dimensions independently named, now unblocked by the live
`predict_surprisal` violation signal. **status:** OPEN — a BUILD problem (a predict-and-revise parse pass over the
reader's front end). You build + validate in `experiments/`; strategy lands any hdlab wire (Q111, default-off flag,
witness required). Glass-box, NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `2` — HIGH. This is the reader's single most
> CONVERGENT quality lever: parse-recall caps who-did-what, SPACE, causation, and belief simultaneously, and it caps the
> quality of the situation model the LEARNER grows on (clean-foundation). It is now the natural next step because the
> forward-prediction VIOLATION signal it needs is LIVE (`predict_surprisal`, landed this session). Ranked at 2 (the
> reader-quality lever) alongside p3 retrieval-practice (the learner-on lever). **Re-rank per the owner.** ⚠️ Compose
> with the reader's capable flags ON (`python tools/reader_capabilities.py`, incl. `predict_surprisal`).

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
Our reader runs one grammar-parse of each sentence and trusts it completely. Brains don't: they keep several possible
readings alive, lean on what's *plausible* to pick between them, and — crucially — go back and re-read when something
they expected doesn't show up. We already proved the trusting approach hits a wall: when the reader gets "who did what"
wrong, it's because the single parse quietly missed the real structure and the reader fell back on the grammatically
default guess (usually "the first noun is the doer"). We also proved that just swapping in a stronger off-the-shelf parse
doesn't fix it — what helps is *predict-and-revise*: use the parse as a hint (not gospel), combine it with a sense of
what's plausible, and re-parse exactly where the reader's own "that's surprising" signal fires. That surprise signal is
now live. Build the re-reading step that uses it to recover the structure the first parse dropped.

## 2. WHY THIS ONE
It is the reader's most CONVERGENT quality lever: the same missed-structure wall caps who-did-what, where-things-are,
causation, and who-believes-what — and it caps the quality of the situation model the learner grows on. Three integrated
problems independently pointed here, and the piece that was missing (a live signal of *when* the reader is probably
wrong) just landed. Fixing parse-recall lifts several dimensions at once, which is the highest leverage-per-unit-effort
available now.

## MEASURED vs INFERRED
- **MEASURED (inherit; do NOT re-derive):** who-did-what errors are STRUCTURAL — the reader's wrong pick is no more
  similar to gold than a random competitor (0.221 vs 0.229; p2), i.e. it grabs the grammatically-default entity, and
  ~half the errors surprisal MISSES are "parse-COVERAGE failures whose only lever is a better parser." SPACE: parse-as-
  truth sits AT the info-free null; the predict-and-revise PRIOR is the lever. BELIEF: location/status extraction is the
  shared parser-recall ceiling. `predict_surprisal` is LIVE (`EventRecord.patient_surprisal`, the violation signal).
- **INFERRED (you must measure):** whether a predict-and-revise parse pass — parse-as-EVIDENCE fused with a plausibility
  PRIOR, re-parsing where the prediction breaks — RECOVERS the missed structure (who-did-what + dropped arguments) CI-sep
  over the batch parse-as-truth floor on real prose, or whether the residual is irreducible recall (a full-PASS negative
  that localizes the ceiling).

## 3. HOW THE BRAIN DOES THIS (the opening move)
**PINNED — noisy-channel comprehension + predict-and-revise.** The brain does not treat the perceived string/parse as
ground truth; it infers the INTENDED structure by combining the noisy input (evidence, likelihood) with a PRIOR over
plausible structures/messages (Levy 2008 *Cognition*; Gibson, Bergen & Piantadosi 2013 PNAS — comprehenders rationally
"correct" implausible parses toward plausible ones). Parsing is INCREMENTAL and PREDICTIVE (Hale 2001 surprisal;
Altmann & Kamide 1999 anticipatory eye-movements), and REANALYSIS is triggered by a prediction violation — the P600 /
LIFG structural-reanalysis stream, DISTINCT from the N400 thematic-fit stream (Van Herten & Kolk; Thompson-Schill; the
two-stream account confirmed in p2). The computation to COPY: hold the parse as EVIDENCE (not truth), weight candidate
structures by a plausibility PRIOR, and RE-PARSE / re-bind at the loci where the forward prediction is violated (high
`patient_surprisal`) — recovering arguments/attachments the single batch parse dropped.

## 4. PINNED vs OUR-INVENTION (copy the computation, sweep the parameter)
- **PINNED (COPY exactly):** parse-as-evidence + a plausibility prior (noisy-channel posterior); reanalysis GATED by a
  prediction violation; incremental/predictive parsing.
- **OUR-INVENTION-UNDER-TEST (SWEEP, do not adopt a number):** the prior's form (selectional-preference / thematic-fit
  plausibility — reuse the promoted `predictive_reader` / grounded space), the noise model / evidence weight, the
  surprisal threshold that triggers re-parse, and the search over alternative structures. These derive from constraints
  we do not share; sweep them, report the frontier, never hard-code a borrowed constant.

## ALREADY TRIED / DO NOT RE-RUN (this is NOT the refuted negative)
- ⛔ **`the_forward_prediction_organ…` (p2, integrated EXCELLENT) already REFUTED role RE-SELECTION from a FIXED parse:**
  using surprisal to auto-revise WHICH already-extracted argument fills a role fails (−0.002; the errors are structural,
  no more similar to gold than random). **This problem is DIFFERENT: it is parse-RECALL — recover the structure/arguments
  the batch parse DROPPED, not re-choose among the ones it kept.** The distinction is load-bearing; a submission that
  merely re-selects roles from the existing parse is a re-tread and will be rejected.
- ⛔ **`wire_the_incremental_parser_as_the_reader_extraction_front_end` (integrated NEGATIVE):** restricting the binder to
  the incremental parser's bounded buffer LOWERED accuracy (role-binding is a separate cue-based stream). Do NOT replace
  the binder with a parser buffer; the predict-and-revise pass AUGMENTS recall, it does not replace the role stream.
- ⛔ Do NOT "swap in a stronger off-the-shelf parser" — SPACE showed a stronger general parser does NOT help; the lever is
  the predict-and-revise PRIOR, not raw parser strength. (An external-LLM parser is barred regardless — the invariant.)

## VERIFY BEFORE YOU START (the disk outranks this brief)
- Run `python tools/reader_capabilities.py` and turn `predict_surprisal` ON — read `hdlab/situation_reader.py`
  `_read_surprisal` + `EventRecord.patient_surprisal` (the live violation signal you build the revision on) and
  `hdlab/predictive_reader.py` (the plausibility model). Read how SPACE operationalized parse-as-evidence + a persistence
  PRIOR (`experiments/_space_reader.py`, `prior_ext` mode) — the template for a noisy-channel fusion.
- Read the p2 SOLVED + its decisive structural-error test so you build the parse-RECALL fix, not the refuted re-selection.
- Pick a role/argument gold on REAL, MODERN prose (QA-SRL v2 dev/test who-did-what; the p2 population) + a held-out slice;
  report n. MIND the corpus-age confound (add a 19c LitBank slice like p2 to show it is not a modern-vocab artifact).

## 5. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
PASS = the predict-and-revise parse pass RECOVERS who-did-what (and the arguments the batch parse drops) CI-SEPARATED
over the strongest REAL floor — the batch parse-as-truth / positional-default reader at EQUAL inputs — on held-out +
MODERN real prose, with the info-free TWIN (revise at the same rate at RANDOM loci, or with a shuffled prior) LOSING
CI-separated, AND a positive control that revision fires exactly where the prediction is violated (not everywhere). Report
CI half-width + null p95 beside every margin. **A rigorous NEGATIVE is a full PASS if located:** if predict-and-revise,
faithfully built, does not beat parse-as-truth (the residual is irreducible recall — the structure is simply not
recoverable from the available signal), name it precisely (which constructions, why the prior cannot disambiguate them)
and localize the ceiling — that tells the assembly where the true front-end limit is.

## 6. FLOORS + CONTROLS (the strongest trivial methods, actually run)
- **Batch parse-as-truth / positional-default** reader at equal inputs (the incumbent; the floor to beat).
- **Info-free twin:** revise at the same RATE but at RANDOM loci, or with a SHUFFLED plausibility prior (excludes "any
  extra re-parsing at this rate helps").
- **Revise-everywhere** (no surprisal gate) vs **surprisal-gated** revision (the positive control that the violation
  signal LOCALIZES the fix, per the brain's gated reanalysis).
- **Non-canonical stratum** (passive / fronted / relative-clause) — where parse-as-truth is weakest and predict-and-revise
  should help most (or fail informatively).
- **A stronger-general-parser arm** (SPACE's control) to confirm the lever is the PRIOR, not raw parser strength.

## 7. CORPUS-AGE + GENERALIZATION (owner priority — a constructed-gold win is not a capability)
Score on HELD-OUT + MODERN role gold (QA-SRL v2), and add a 19c LitBank slice (as p2 did) to show the gain is not a
modern-vocabulary artifact. A gain that only shows on the tuning set or one era is not a capability. Report the per-
construction breakdown (which structures the revision recovers vs which stay recall-bound).

## 8. FILES AND ENTRY POINTS
Build + validate in `experiments/` (compose over `SituationReader.read()` with `predict_surprisal` ON; reuse
`predictive_reader` as the plausibility prior and the SPACE `prior_ext` noisy-channel template). A scaffold-free witness
recomputes who-did-what recovery vs the batch parse-as-truth floor + the info-free twin + the surprisal-gated positive
control, from source through the live reader, on held-out + modern + 19c gold. If it clears the bar, strategy lands the
hdlab wire (Q111): a default-off predict-and-revise pass on the reader's front end, byte-identical when off, witnessed.
Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the parser-recall ceiling that caps who-did-what/SPACE/belief).

## DO NOT QUOTE / DO NOT REDO
- 🚫 Do NOT quote p2's surprisal numbers (AUC 0.651, +0.035 abstain) as YOUR result — they are the MOTIVATION (a
  different measurement: the FLAG, not the parse-recall FIX). Re-measure your recovery on your own population. No number
  crosses scorers/populations.
- 🚫 Do NOT re-run role RE-SELECTION from a fixed parse (p2's refuted negative) — this is parse-RECALL (recover DROPPED
  structure). A re-selection submission is a re-tread.
- 🚫 Do NOT replace the role binder with a parser buffer (`wire_the_incremental_parser…`, integrated NEGATIVE), and do NOT
  swap in a stronger general parser (SPACE showed it does not help). The lever is the predict-and-revise PRIOR.
- 🚫 Do NOT use an external LLM as the parser or the prior (the invariant). The plausibility prior must be the substrate's
  own glass-box selectional-preference / grounded model.
- 🚫 Do NOT claim recovery without the surprisal-GATED positive control — revision must fire where the prediction breaks,
  not everywhere; revise-everywhere winning would mean the surprisal gate is doing no work.
