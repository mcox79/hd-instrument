---
priority: 3
review:
review_text:
---

# PROBLEM: coreference on real multi-character narrative is measured at ~0.65 and it CAPS every organ that resolves who-is-who on prose (the ToM observation cue, entity tracking, the situation model, "where is X?") — build a brain-faithful coreference that beats the ~0.65 incumbent CI-separated on real narrative, OR make a confidence-gated ABSTAIN a first-class signal downstream organs consume so they degrade gracefully instead of silently inheriting a wrong link

**slug:** `coreference_is_capped_at_065_on_real_narrative` — **opened:** 2026-08-28 by the strategy session
(surfaced as a live, quantified bottleneck by the integrated `theory_of_mind_residual_is_the_observation_cue_front_end`
and named in `capability_registry` as "coref abs ~0.65<0.70"). **status:** OPEN — a MECHANISM + INSTRUMENT problem.
You build + validate in `experiments/`; strategy lands any hdlab change (Q111). Builds on the LANDED `hdlab/coreference_resolver.py`.

> **PRIORITY NOTE (the call is the strategy session's):** filed at `3` — HIGH leverage: coref error propagates into the
> ToM belief front-end, entity tracking, the situation model, and the new SPACE/location organ (p1); every one inherits
> the ~0.65 cap on multi-character prose. Two acceptable wins (either passes the bar): raise the accuracy, OR make the
> uncertainty legible so downstream organs stop silently trusting a wrong link. **Re-rank per the owner.**

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
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
To understand a story you must track WHO each "he/she/they/it/the man" refers to. Our coreference resolver
(`hdlab/coreference_resolver.py`) is landed and wired, but its measured accuracy on real multi-character narrative is
only ~0.65 (registry: "coref abs ~0.65<0.70"). That is a live cap: the theory-of-mind observation cue, entity tracking,
the situation model, and the new per-entity location organ all resolve mentions THROUGH this resolver, so each silently
inherits its ~35% error on hard prose — a wrong link becomes a wrong belief, a wrong location, a wrong who-did-what. The
task: either (a) build a MORE brain-faithful resolver that beats ~0.65 CI-separated on real narrative, or (b) make a
confidence-gated ABSTAIN a first-class output the downstream organs consume (so on a low-confidence link they degrade
gracefully / defer, rather than committing to a guess). A rigorous negative on (a) that DELIVERS (b) is a full pass.

## 2. WHY THIS ONE
It is a shared, quantified bottleneck under several already-landed organs and the new SPACE organ (p1). Raising it, or
making its uncertainty legible, lifts the whole reading stack at once — the highest-leverage kind of fix (a component
that caps many capabilities).

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** the brain resolves reference by MEMORY-CUED RETRIEVAL over a discourse model, not a
  syntactic rule table — an antecedent is retrieved by a graded cue-combination (recency/salience/gender-number
  agreement/semantic fit/centering), i.e. CUE-BASED RETRIEVAL from working memory (Lewis & Vasishth 2005 ACT-R
  sentence processing; McElree 2003 content-addressable retrieval; Grosz/Joshi/Weinstein 1995 Centering; Nieuwland &
  Van Berkum N400 on reference). This is the SAME graded cue-competition currency the substrate already uses for role
  assignment (`graded_competition`) — reuse it. UNCERTAINTY is intrinsic: when cues conflict, the retrieval posterior
  is FLAT → the brain-faithful output is a distribution, and a flat one is the signal to defer.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the exact cue weights + the abstain threshold on the retrieval
  posterior's entropy/margin. Copy the COMPUTATION (graded cue-based retrieval over the discourse entity set); SWEEP
  the weights + threshold.
- **NOT brain-faithful:** a hard syntactic/rule pipeline with a single committed answer and no uncertainty — that is
  what makes a wrong link propagate invisibly.

## 4. MEASURED vs INFERRED
- **MEASURED (REUSE):** `hdlab/coreference_resolver.py` ~0.65 on real narrative (registry). LitBank gold coref exists on
  disk (`data/corpora/litbank_coref_conll`) — real multi-character prose with gold clusters.
- **MEASURED (adjacent):** `graded_competition` is landed (the graded cue-based-retrieval currency) + an "honest-mode"
  confidence-gated abstain was prototyped in the ToM/front-end line.
- **INFERRED (to prove):** whether graded cue-based retrieval (reusing `graded_competition`) beats the incumbent
  CI-separated on LitBank, and whether an entropy/margin abstain flag, consumed downstream, recovers accuracy on the
  KEPT subset without abstaining on everything.

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT rebuild a hard rule pipeline — the incumbent is already a committed-answer resolver; the gap is the mechanism
  (graded retrieval) + the uncertainty signal.
- Reuse `graded_competition` (the divisive-normalization softmax over cue activations) rather than a new competition op.
- Do NOT tune to LitBank's gold quirks; report held-out.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/coreference_resolver.py` (the incumbent + how it is wired), `hdlab/graded_competition.py` (the retrieval
  currency to reuse), and the ToM front-end's coref-proxy + honest-mode abstain (`experiments/perceptual_access_ledger.py`).
- `data/corpora/litbank_coref_conll` (gold). `tools/experiment_index.py query "coref"`. Registry line "coref abs ~0.65".
- `notes/BRAIN_FOUNDATIONAL_AUDIT.md` — the coreference entry + the ToM §2b note that coref caps the intact-prose cue.

## 7. THE BAR
PASSES with EITHER track, ALL of its items:
- **Track A (raise accuracy):** a graded cue-based-retrieval resolver beats the incumbent ~0.65 CI-separated on REAL
  narrative (LitBank gold, held-out), recompute the incumbent floor on the SAME population; an info-free twin
  (shuffled cue activations / random-antecedent) LOSES CI-separated; report CI half-width + null p95. A positive control
  that the metric moves (a case the graded resolver gets and the incumbent misses).
- **Track B (legible uncertainty):** an entropy/margin ABSTAIN flag on the retrieval posterior such that, on the KEPT
  (non-abstained) subset, accuracy is CI-separated-higher than the un-gated resolver on the same items, the abstain
  rate is < a stated cap (not "abstain on everything"), and a DOWNSTREAM organ (e.g. the ToM cue) measurably degrades
  GRACEFULLY when fed the flag vs silently inheriting the wrong link. Info-free twin (random abstain) LOSES.
- No number crosses populations/scorers. Route heavy LitBank runs to REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).
A rigorous NEGATIVE is a full pass (e.g. "graded retrieval ties the incumbent on LitBank, but the abstain flag recovers
+X on the kept subset and lets the ToM cue defer" — Track B alone passes).

## 8. FILES AND ENTRY POINTS
- `hdlab/coreference_resolver.py`, `hdlab/graded_competition.py`; `experiments/perceptual_access_ledger.py` (coref proxy
  + honest-mode). Gold: `data/corpora/litbank_coref_conll`. Audit: `notes/BRAIN_FOUNDATIONAL_AUDIT.md`. Heavy → REMOTE.

## DO NOT QUOTE / DO NOT REDO
The ~0.65 is the incumbent floor to BEAT/instrument, not a result to restate. Strategy owns any hdlab landing — you
propose the resolver / the abstain signal, you do not write `hdlab/`.
