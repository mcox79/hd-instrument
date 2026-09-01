---
priority: 6
review:
review_text:
---

> ⚠️ **DEMOTED + LIKELY SUBSUMED (strategy, 2026-09-01):** a same-thread solver candidate promoted to
> `promote_the_grounded_semantic_graph_to_an_intrinsic_learnable_organ` (priority 1) found that feature-COSINE sense
> selection — INCLUDING this brief's grounded-hub re-rank — sits at the dominant-sense baseline on gold WSD; the lever is
> the RELATIONAL GRAPH + spreading activation, into which the grounded features fold as NODE content (that problem's
> approach step #1). This narrower feature-re-rank framing is kept only as a fallback angle and is a RETIRE candidate —
> STRATEGY RECOMMENDS folding it into the graph organ. Do NOT assign both to the meaning wall in parallel without the
> owner's call. (p3's grounded-re-rank DID double selection on the CONSOLIDATION_FAIL selection-AUC population — a real
> but population-specific result; the graph framing is the deeper, gold-WSD-robust one.)

# PROBLEM: the reader can RETRIEVE the right word-meaning but cannot SELECT it — the correct sense is in the reader's top handful of guesses ~85% of the time, but from plain reading it can only tell that two words CO-OCCUR (whisky~weddings), not that they MEAN THE SAME KIND OF THING (whisky~brandy), so it picks the topical ASSOCIATE over the correct SENSE. p3 (`grounding_does_not_accumulate…retrieval_practice`, owner-DONE) drilled this to the bottom: for the ~78% of words with an existing correct anchor, the correct anchor is RETRIEVABLE (top-10 recall ~85%) under EVERY encoder incl. the full dependency parser — so the encoder is NOT the wall — but it is SELECTABLE by NO distributional read-out (nearest 0.21 / background-subtraction 0.23 / the distilled-substitutability axis 0.24 / a SUPERVISED logistic 0.22, all ~chance vs the ~0.87 top-10 ceiling). The signal separating correct SENSE from topical ASSOCIATE is genuinely ABSENT from distributional co-occurrence; the lever is GROUNDED / sensorimotor knowledge of what things ARE (the ATL hub-and-spoke — the project's named Phase-1 bottleneck). p3 DEMONSTRATED the fix: re-ranking the distributional top-K by GROUNDED-HUB similarity roughly DOUBLES correct sense selection (~0.20-0.28 → ~0.35-0.48, CI-separated both seeds), and it is UNSUPERVISED (matches the supervised-over-grounded ceiling). Build the grounded sense-SELECTION re-rank as the reader's live meaning read-out (a two-stage LASS cascade: fast distributional SHORTLIST → slow GROUNDED re-rank, grounded-DOMINANT) and prove it selects the correct grounding CI-separated over every distributional read-out on the CONSOLIDATION_FAIL population — or enumerate the irreducible residual.

**slug:** `the_reader_selects_word_sense_by_distribution_needs_a_grounded_atl_re_rank` — **opened:** 2026-09-01
by the strategy session (ARCHITECT HEARTBEAT; owner marked p3 retrieval-practice done + flagged idle solvers). It is
p3's explicitly-named #1 follow-on ("THE lever — a GROUNDED sense-selection read-out, reader_meaning_channel/ATL =
Phase 1, DEMONSTRATED"). **status:** OPEN — a BUILD problem (the grounded sense-selection re-rank as the reader's
meaning read-out). You build + validate in `experiments/`; strategy lands any hdlab wire (Q111, default-off, witness
required). Glass-box, NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's; RE-RANK PER THE OWNER):** filed at `1` — HIGHEST. This is the
> project's NAMED Phase-1 bottleneck (the North Star's clean-foundation lever: the learner grows on word meaning, and
> word meaning is exactly what this selects). p3 proved the fix is real, brain-faithful, and DE-RISKED (an unsupervised
> grounded re-rank doubles correct sense selection and matches the supervised ceiling). It unblocks the meaning channel
> the whole reader/learner stack has been gated on. ⚠️ HONEST BOUND: the demonstrated lift is a PARTIAL one (~0.20-0.28 →
> ~0.35-0.48, NOT the ~0.87 retrieval ceiling) at ~78% grounded coverage — richer grounding + the ~22% uncovered
> abstract words are the remaining work. ⚠️ Compose with the reader's capable flags ON (`python tools/reader_capabilities.py`).

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
When the reader meets a word and tries to pin down its meaning, it lines up its best guesses and — most of the time —
the right meaning IS in that short list. But it picks the wrong one, because from reading alone it only learns which
words keep company with which ("whisky" shows up near "wedding"), not which words are the SAME KIND OF THING ("whisky"
and "brandy"). So it grabs the thing that merely appears in the same contexts instead of the thing that actually means
the same. Brains tell these apart using GROUNDED knowledge — what the thing looks/feels/acts like — held in a hub that
ties words to sensory and emotional experience. We already showed that re-ranking the reader's short list by that
grounded knowledge picks the right meaning about twice as often. Build that: keep the fast "what shows up together"
step to get a short list, then let GROUNDED knowledge choose the winner from it.

## 2. WHY THIS ONE
This is the project's named Phase-1 bottleneck: the whole learn-by-reading program grows on word meaning, and word
meaning is precisely what a distributional-only reader cannot pin down (p3 proved it, decisively, ruling out a better
encoder, a better distributional read-out, and even a supervised one). p3 also DEMONSTRATED the fix works (a grounded
re-rank doubles correct selection, unsupervised, matching the supervised ceiling), so this is a de-risked, highest-
leverage build that unblocks the meaning channel the reader and learner have been gated on.

## MEASURED vs INFERRED
- **MEASURED (inherit from p3; do NOT re-derive):** for the ~78% of CONSOLIDATION_FAIL words with an existing anchor,
  the correct anchor is RETRIEVABLE to top-10 ~85% under EVERY encoder incl. the full dependency parser (the encoder is
  NOT the wall), but SELECTABLE by NO distributional read-out (nearest 0.21 / bg-subtract 0.23 / distilled axis 0.24 /
  supervised logistic 0.22, all ~chance vs the ~0.87 ceiling). A GROUNDED-HUB re-rank (11 Lancaster sensorimotor + 3
  Warriner affect dims) selects it: rank-1 0.32/0.35 vs distributional 0.24/0.27 (+0.08/+0.07 both seeds, ~78%
  coverage). The FULL grounded cascade (two-stage LASS, grounded-DOMINANT, predicted-Binder-65 experiential spoke)
  ~DOUBLES it (~0.20-0.28 → ~0.35-0.48, CI-sep both seeds) and MATCHES the supervised-over-grounded ceiling (~0.41) →
  no supervision headroom. Re-FUSING the distributional cue HURTS (it is peaky about TOPIC not SENSE) → the cascade is
  grounded-DOMINANT, not equal fusion. Distributional-selection is a rate-independent NEGATIVE (selection-AUC includes chance).
- **INFERRED (you must measure):** whether a live grounded sense-SELECTION re-rank over the distributional shortlist
  selects the WordNet-correct grounding CI-separated over every distributional read-out on the CONSOLIDATION_FAIL
  population (rate-independent selection-AUC), the info-free grounded-shuffle twin LOSING; and how far richer grounding
  (Binder-65 / a learned grounded selector) + coverage for the ~22% uncovered abstract words closes the residual toward
  the ~0.87 ceiling — or the located ceiling (which words stay unselectable and why).

## 3. HOW THE BRAIN DOES THIS (the opening move)
**PINNED — the ATL HUB-AND-SPOKE + LASS (fast distributional shortlist → slow grounded re-rank).** Concept meaning is a
transmodal HUB in the anterior temporal lobe that binds modality-specific SPOKES — sensorimotor, affective, linguistic
(Patterson, Nestor & Rogers 2007; Lambon Ralph et al. 2017; semantic dementia = ATL hub damage). Word sense is selected
by combining a fast distributional/lexical cue with slow GROUNDED (experiential) knowledge — Language-and-Situated-
Simulation (Barsalou 2008): a fast linguistic form-association pre-activates candidates, a slower situated (grounded)
simulation settles the meaning. Reliability-weighted cue combination is a PRODUCT-OF-EXPERTS / noisy-channel integration
(Ernst & Banks 2002), and sense settling is an ATTRACTOR basin (Rodd, Gaskell & Marslen-Wilson 2004). The computation to
COPY: a fast distributional SHORTLIST of candidate groundings, then a GROUNDED re-rank (ATL experiential features) that
SELECTS the correct sense — grounded-DOMINANT, because the distributional cue is reliable for TOPIC but not for SENSE.

## 4. PINNED vs OUR-INVENTION (copy the computation, sweep the parameter)
- **PINNED (COPY exactly):** the ATL hub-and-spoke experiential representation of concept meaning; the two-stage LASS
  cascade (fast distributional shortlist → slow grounded re-rank); grounded-DOMINANT selection (the distributional cue
  gates the shortlist, the grounded cue SELECTS the winner); reliability-weighted combination.
- **OUR-INVENTION-UNDER-TEST (SWEEP, do NOT adopt a number):** the grounded feature space (Lancaster-11+Warriner-3 vs
  predicted-Binder-65 vs a learned grounded selector — richer is the point; sweep it, the coarse space is a floor not a
  target), the shortlist size K, the grounded-vs-distributional weighting (grounded-dominant — do NOT equal-fuse; p3
  showed fusion HURTS), the coverage/back-off rule for the ~22% uncovered abstract words. Sweep, report the frontier.

## ALREADY TRIED / DO NOT RE-RUN (this is NOT a re-tread — check `experiment_index` FIRST)
> ⚠️ **RUN `python tools/experiment_index.py query "grounded"` / `"sense selection"` / `"meaning read-out"` FIRST** (p6's
> process lesson: it re-derived a known negative by skipping this). Inherit p3's REFUTED arms — do NOT re-run them as a fix:
- ⛔ A DISTRIBUTIONAL read-out re-ranker (nearest / background-subtraction / the distilled-substitutability axis /
  supervised logistic) — ALL ~chance in p3. The distributional signal for SENSE is genuinely absent; a better
  distributional read-out CANNOT select it.
- ⛔ A "better ENCODER" swap (bag-of-words → PPMI+SVD → dependency parser all retrieve to top-10 ~85% but none SELECTS) —
  the encoder is NOT the wall. Do NOT re-run an encoder head-to-head as a selection fix.
- ⛔ A retrieval-practice / consolidation durability step (p3's own refuted premise) — it strengthens a memory, it does
  not decide WHICH sense; it only relaxes the grounding threshold (adds wrong meanings at the base rate). Not a fix.
- ⛔ EQUAL fusion of distributional + grounded — p3 showed re-fusing the distributional cue HURTS (peaky about TOPIC).
  The cascade must be grounded-DOMINANT.
- Reuse p3's BUILT pieces (`build_grounded_hub`, the predicted-Binder-65 experiential spoke `exp_selpref_unseen_lowdata_v1`,
  the CONSOLIDATION_FAIL population + the blind WordNet scorer) — do NOT rebuild them.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- Read p3's `SOLVED.md` (this problem is its NEXT STEP / follow-on #1) — esp. "THE DEMONSTRATED FIX" (grounded-hub
  re-rank) and the `full_lift` frontmatter (the two-stage LASS cascade, the Binder-65 spoke, the grounded-shuffle +
  fusion-hurts controls). Inherit its numbers; do not re-derive.
- Read the grounded-hub organ p3 used (`build_grounded_hub` + the Lancaster/Warriner spokes) + the predicted-Binder-65
  experiential space (`exp_selpref_unseen_lowdata_v1`, rho 0.69, 24978 words) + the CONSOLIDATION_FAIL population + the
  blind WordNet selection-AUC scorer. Check whether `reader_meaning_channel` (the reader-side meaning read-out) exists /
  is wired (the whole meaning stack has been gated on it).
- Score on the CONSOLIDATION_FAIL population (p3's, n≈700 words, 3000 modern sentences) blind on WordNet, RATE-INDEPENDENT
  (selection-AUC), so a "grounds more words at base precision" artifact cannot pass. Report n + coverage.

## 5. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
PASS = the grounded sense-SELECTION re-rank (over the distributional shortlist) selects the WordNet-correct grounding
CI-SEPARATED over the STRONGEST distributional read-out actually run (nearest / bg-subtract / distilled / supervised) on
the CONSOLIDATION_FAIL population, measured RATE-INDEPENDENTLY (selection-AUC over covered words), with the info-free
GROUNDED-SHUFFLE twin (shuffle the grounded feature→word assignment) LOSING CI-separated, AND a positive control that
re-FUSING the distributional cue does NOT beat grounded-alone (proves the cascade is grounded-DOMINANT, not fusion).
Report CI half-width + null p95 beside every margin. **A rigorous NEGATIVE is a full PASS if located:** if a grounded
re-rank, faithfully built, does NOT beat the distributional read-out (or only on a narrow slice), name precisely which
senses stay unselectable and why (coverage-bound? feature-space too coarse? genuinely non-grounded abstractions?) and
localize the ceiling. HONEST CEILING (p3): a LARGE lift (~2x, CI-sep) but NOT to the ~0.87 retrieval ceiling — ~0.45 at
~78% coverage; richer grounding + the ~22% uncovered abstractions are the remaining distance.

## 6. FLOORS + CONTROLS (the strongest trivial methods, actually run)
- **The strongest DISTRIBUTIONAL read-out** actually run (nearest / background-subtraction / the distilled-
  substitutability axis / a supervised logistic) — RECOMPUTE on YOUR items with CIs; beat the strongest CI-sep.
- **Info-free GROUNDED-SHUFFLE twin** (shuffle the grounded feature→word map) — must LOSE CI-sep (excludes "any richer
  feature vector helps"; the grounded CONTENT must do the work).
- **Grounded-alone vs grounded+distributional-fusion** (positive control): fusion must NOT beat grounded-alone (proves
  grounded-DOMINANT; p3 showed fusion hurts because the distributional cue is peaky about topic).
- **Measured-Binder vs predicted-Binder** on the human-rated slice (excludes an imputation artifact — p3's control).
- **Coverage split** (grounded-covered ~78% vs uncovered ~22%) — report separately; the uncovered abstractions are the
  located residual, not a hidden win.

## 7. CORPUS-AGE + GENERALIZATION (owner priority — a constructed-gold win is not a capability)
Score blind on WordNet over the modern CONSOLIDATION_FAIL population (simplewiki+news+science). Report per-coverage and
per-sense-type (concrete vs abstract) breakdowns and the rate-independent selection-AUC (not a base-rate precision that
a threshold relaxation could inflate). A gain that only shows at a particular threshold or on the covered subset's easy
words is not a capability.

## 8. FILES AND ENTRY POINTS
Build + validate in `experiments/` (reuse `build_grounded_hub` + the predicted-Binder-65 spoke + the CONSOLIDATION_FAIL
population + the blind WordNet selection-AUC scorer; compose the two-stage LASS cascade — distributional shortlist →
grounded re-rank, grounded-dominant). A scaffold-free witness recomputes, FROM SOURCE, the grounded re-rank's selection-
AUC vs the strongest distributional read-out + the grounded-shuffle twin + the fusion-hurts positive control, blind on
WordNet. If it clears the bar, strategy lands the hdlab wire (Q111): a default-off grounded sense-selection read-out on
the reader's meaning channel (`reader_meaning_channel` / `canonicalize_grounded`), threshold UNCHANGED (no bar-relaxation),
byte-identical when off, witnessed. Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the sense-selection wall
= distributional co-occurrence lacks the SENSE signal; the ATL grounded re-rank supplies it — Phase 1).

## DO NOT QUOTE / DO NOT REDO
- 🚫 Do NOT quote p3's numbers (0.32/0.35 rank-1, ~2x lift, 0.87 ceiling) as YOUR result — they are the MOTIVATION.
  Re-measure your re-rank's selection-AUC on your own population. No number crosses scorers/populations.
- 🚫 Do NOT re-run the REFUTED distributional read-outs / encoder swaps / retrieval-practice as a fix (p3 refuted all).
  This is a GROUNDED sense-SELECTION re-rank — a distinct mechanism.
- 🚫 Do NOT EQUAL-FUSE distributional + grounded (fusion HURTS — grounded-dominant only). A fusion or distributional-
  dominant arm winning means the grounded content is not doing the work.
- 🚫 Do NOT relax the grounding THRESHOLD to "select more" — that adds wrong meanings at the base rate (the brief's
  forbidden move). Selection must be rate-INDEPENDENT (selection-AUC).
- 🚫 Do NOT use an external LLM as the grounded space or the selector (the invariant). The grounded features + re-rank
  must be the substrate's own glass-box experiential representation.
