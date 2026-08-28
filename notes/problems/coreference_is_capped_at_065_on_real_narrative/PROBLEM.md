---
priority:
review: EXCELLENT
review_text: "Owner-DONE. The ~0.65 coref cap is BROKEN, DIAGNOSED, and honestly bounded on real narrative. Re-verified FIRST-HAND against the current file (`verification/test_coref_graded_cue_retrieval.py`, ALL 8 checks PASS — ran it myself; the solver strengthened Track B between submission and DONE, so I re-ran fresh). Mechanism COPIED (PINNED): the reader's rigid hard-tiered pronoun pick (`_pick_strict_cb`) is replaced by the brain's actual reference computation — GRADED cue-based retrieval (Lewis & Vasishth 2005; McElree 2003): a softmax over the pinned ACT-R base-level activation (recency×frequency×role), reusing the LANDED `graded_competition` organ verbatim. TRACK A PASSES the bar: on LitBank (100 novels, 50 held-out TEST), the COMPETITIVE pronoun-antecedent subset (≥2 gn-compatible prior gold entities, n=4693), graded 0.7752 [0.7313,0.8176] vs the INCUMBENT hard-tier recomputed on the SAME population 0.6030 [0.5449,0.6544] — +0.1722 CI-sep (half-width 0.031, null-p95 0.031); info-free twins collapse (random 0.0548, shuffled-cue 0.0435, lose by +0.72); positive control fixes 1073 incumbent errors / breaks 265 (net +808). The CAP's mechanism is now MEASURED and surprising: the incumbent's rigid subject-first tier scores BELOW plain recency (0.603 < 0.717) — on the 2012 tier-wrong/graded-right cases it grabs a subject a mean 2.2 sentences STALER (3.42 vs 1.20) because strict-Cb has NO graded recency decay within the subject class; the brain's dt^-d decay is exactly what it discarded (copy-the-computation, made quantitative). TRACK B passes at the resolver output: posterior normalized-entropy (softmax gain=8 tuned on DEV; GAIN-INVARIANT for argmax so Track A is untouched — no leak) predicts its OWN errors AUC 0.806 vs the INCUMBENT margin signal 0.617 recomputed on the SAME population (apples-to-apples, no number crossing); deferring the highest-entropy 33% lifts kept-subset accuracy 0.775→0.894 CI-sep, random-abstain twin flat 0.775 — the brain-faithful 'flat posterior → defer' (Levy 2008; the Nref 'hold both' ERP, Nieuwland & Van Berkum 2008). SCRUPULOUSLY HONEST (volunteered): by `graded_competition`'s MAP-optimality theorem graded-argmax == the argmax of the same net, so graded TIES ACT-R base-level activation (0.782, NOT_SEP) — the accuracy win is over the incumbent TIER, and the graded FORM's unique value is the calibrated DISTRIBUTION (Track B), not the point estimate. Optimization levers tested + REJECTED with numbers (owner 'is there more?'): parallelism/backward-center/first-mention/frequency cues → DEV weight ~0; a faithful NLTK gender-gazetteer + animacy pre-filter → pool 39.9→39.3, accuracy null (the pool TAIL doesn't bind, the structurally-salient competitors do); lexical implicit-causality → decisive frame n=0 in real prose; role-weighting exhausted (0.783≈0.792≈0.793). The ~0.78 structural ceiling is DEMONSTRATED not asserted; the only remaining accuracy lever is the coherence next-mention PRIOR (the 2nd Kehler-Rohde Bayesian term), a separate situation-model build. Track B item (c) NOT met on the who-did-what downstream — correctly localized as name-clustering + FHRR register-capacity bottlenecked (oracle-coref 0.62 vs binder 0.17), NOT link-bottlenecked; a mapped adjacency, not a coref failure (and the bar takes Track A alone as a full pass). AUDIT UPDATE folded (§2b): REVERSES the 08-27 coref cue-based-activation HARD_FAIL as POPULATION-SPECIFIC (McGuffey short/dense favors the hard tier; real narrative favors graded) — the right mechanism is population-dependent. hdlab landing QUEUED (Q111, opt-in default-off `run_graded_retrieval` + entropy-abstain on `coreference_resolver.py`; existing behavior byte-identical). Highest-leverage adjacency now MEASURED for a clean follow-on: name/entity clustering shatters 65.6% of multi-name gold entities (single-head-token cache root cause) and caps the whole who-did-what/entity-tracking stack."
---

> ## ✅ SOLVER REVIEW — INTEGRATED 2026-08-28 (strategy session; grade EXCELLENT; owner_verdict: DONE)
> **Re-verified FIRST-HAND against the current file** (`verification/test_coref_graded_cue_retrieval.py`, ALL 8 checks
> PASS — ran it myself; the solver strengthened Track B between submission and the DONE verdict, so I re-ran fresh rather
> than trust my earlier read). **Result:** the reader's rigid hard-tiered pronoun pick (`_pick_strict_cb`) is replaced by
> the brain's actual reference computation — **graded cue-based retrieval** (Lewis & Vasishth 2005; McElree 2003): a
> softmax over the pinned **ACT-R base-level activation** (recency×frequency×role), reusing the LANDED
> `graded_competition` organ verbatim.
> **Argument audit (not just arithmetic) — the controls + the honesty are the strength:** (a) TRACK A meets the bar —
> graded **0.775 [0.731,0.818]** vs the INCUMBENT hard-tier recomputed on the SAME population **0.603 [0.545,0.654]**,
> **+0.172 CI-sep** (half-width 0.031, null-p95 0.031); info-free twins collapse (0.055 / 0.044); positive control fixes
> 1073 / breaks 265. (b) The CAP's mechanism is now MEASURED: the rigid subject-first tier scores **below plain recency**
> (0.603 < 0.717) — on the 2012 tier-wrong/graded-right cases it picks a subject **2.2 sentences staler** (3.42 vs 1.20)
> because strict-Cb lacks graded recency decay; the brain's dt^-d decay is what it discarded. (c) TRACK B — posterior
> entropy predicts its OWN errors **AUC 0.806** vs the incumbent margin **0.617 on the SAME population** (apples-to-apples,
> no number crossing); deferring 33% lifts kept accuracy **0.775→0.894** CI-sep, random twin flat; the gain is
> gain-invariant for argmax so **Track A is untouched** (no leak). (d) The **MAP-optimality theorem** is volunteered:
> graded-argmax == the same net's argmax, so graded TIES ACT-R (0.782, NOT_SEP) — the win is over the incumbent TIER, the
> graded form's unique value is the calibrated DISTRIBUTION. (e) Optimization levers tested + REJECTED with numbers
> (parallelism, extra Centering cues, a faithful gender/animacy pre-filter → pool 39.9→39.3 null, lexical IC → frame n=0)
> — the ~0.78 structural ceiling is DEMONSTRATED, not asserted.
> **Brain-foundational discipline:** copy the OPERATION (activation-sum → softmax), sweep only weights/decay/gain; the
> residual ~19% is the brain's SECOND Bayesian term (Kehler & Rohde 2013 coherence next-mention PRIOR — verb-semantics /
> discourse expectations) that we do not compute — the plateau is the two-system boundary, not a tuning failure; and a
> slice of the residual is LitBank ANNOTATION-FIAT ambiguity (ezCoref) where entropy-defer is the brain-faithful output
> (the Nref ERP). **AUDIT UPDATE folded (§2b):** REVERSES the 08-27 coref cue-based-activation HARD_FAIL as
> POPULATION-SPECIFIC (McGuffey short/dense favors the hard tier; real narrative favors graded) — the right mechanism is
> population-dependent; and a new PINNED sub-claim (pronoun reference = a two-term Bayesian computation).
> **Honest boundaries (preserved):** Track B item (c) did NOT pass on the who-did-what downstream — correctly localized
> (exp2) as name-clustering + FHRR register-capacity bottlenecked (oracle-coref 0.62 vs binder 0.17), NOT the pronoun
> link; Track A alone is a full pass of the bar.
> **hdlab landing QUEUED (Q111 — opt-in, default-off, existing behaviour byte-identical; NOT this commit):**
> `run_graded_retrieval(stream, gain, d, flag_thr)` on `hdlab/coreference_resolver.py` — ACT-R activation over
> gn-compatible entities → `graded_pick` (import `hdlab.graded_competition`) → argmax + normalized-entropy confidence;
> abstain when entropy > flag_thr. Replaces the coarse integer strict-Cb margin (AUC 0.617) with the entropy posterior
> (AUC 0.806) as the first-class abstain signal the ToM cue / entity tracking / situation model consume — the name/nominal
> branch stays untouched. **Top adjacency surfaced + now MEASURED for a clean follow-on:** name/entity clustering shatters
> **65.6% of multi-name gold entities** (single-head-token cache = the root cause) and caps the whole who-did-what /
> entity-tracking / situation-model stack (oracle-coref 0.62 vs 0.17).


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
