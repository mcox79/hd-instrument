---
priority: 4
review:
review_text:
---

# PROBLEM: the reader CONFLATES similar events, so it reasons off the WRONG pair. To answer "did X happen before or after Y" the reader must match a paraphrased question-event to the right stored event — but its coarse grounded-cosine aligner cannot tell WHICH of several SIMILAR events a cue means ("get OUT of the shower" vs the stored "exit"/"get IN"), so it reads the temporal order off the wrong pair ~40% of the time. This is the WALL that caps reasoning (p6 `the_reader_cannot_reason_over_its_own_situation_model…`, PARTIAL): the reasoning STEP is sound (the reused `transitive_ordering` read-out beats a shuffled-order twin CI-sep; recovers true order under narrative reordering), and clean extraction is NECESSARY but NOT SUFFICIENT (the loop-closer REFUTED "extraction is the sole wall"), so the dominant residual is SEMANTIC event-ALIGNMENT precision — the brain's DG/CA3 PATTERN-SEPARATION function (keep similar memories from colliding). Our two built organs each fail a DIFFERENT half: `bound_event_backbone` is conjunctive but EXACT-HASH (OVER-separates → kills paraphrase, the 0.48 symbol-tie); `content_addressable_retrieval` is graded but ADDITIVE (UNDER-separates → the fan effect, the ~40% mis-align). Build a grounded CONJUNCTIVE event aligner with a soft-AND (multiplicative) per-role semantic kernel — full role-filler tokens + path/particle + 2nd argument; grounded fillers so a paraphrase matches WITHIN a slot; PRODUCT across slots so a particle mismatch suppresses the wrong candidate (= DG separation) — and prove it converts the reasoning NEAR-positive (~0.59) into a CLEAN CI-separated positive over both floors, or enumerate the irreducible residual. Keep `transitive_ordering` as the read-out; ONLY the aligner's kernel changes.

**slug:** `the_reader_conflates_similar_events_needs_a_soft_and_conjunctive_grounded_aligner` — **opened:** 2026-09-01
by the strategy session (ARCHITECT HEARTBEAT; owner: "p6 dropped, and points to a wall we need to break through — package it, I can assign"). It is the wall p6 (reasoning) localized to root cause and de-risked: the reasoning-and-learning machine is built and brain-faithful and NEARLY clears the bar; the one remaining lever is SEMANTIC event-alignment precision. **status:** OPEN — a BUILD problem (a soft-AND conjunctive grounded event aligner as the reader's event-matcher). You build + validate in `experiments/`; strategy lands any hdlab wire (Q111, default-off, witness required). Glass-box, NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's; RE-RANK PER THE OWNER):** filed at `4` — HIGH. This is the
> reasoning-SPECIFIC lever: p6 named it "the highest-leverage build to convert the near-positive into a clean positive,"
> and reasoning is the North Star's remaining half. It is de-risked by a headroom drill (below), the brain mechanism is
> PINNED (DG/CA3 pattern separation), and the pieces already exist (`bound_event_backbone` + `content_addressable_
> retrieval` + grounded codes + the reused `transitive_ordering` read-out). Ranked at `4` — below the more UPSTREAM
> who-did-what extraction lever (p2 `the_reader_parses_as_truth…`, priority `2`, which lifts EVERY dimension), because
> this aligner is the reasoning-line successor. If you prefer reasoning-first, raise it to `1`. ⚠️ Compose with the
> reader's capable flags ON (`python tools/reader_capabilities.py`, incl. `bind_event_tokens` — the JOINT event token,
> landed p4).

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
Our reader can now reason about "what happened when" — but it keeps getting the answer wrong for a subtle reason: it
can't tell two *similar* events apart. A question asks about "getting out of the shower"; the story (or the learned
recipe for showering) stored an event it calls "exit" and another it calls "get in." The reader matches by rough
meaning-similarity, and "get out," "exit," and "get in" all look close — so it grabs the wrong one and reads the
before/after order off the wrong pair about 40% of the time. Brains don't make this mistake: a dedicated part of memory
(the hippocampus's dentate gyrus) *pattern-separates* — it deliberately pushes similar events apart so they don't
collide, keying on the little differences that matter (the "out" vs "in"). We already built two pieces that each get
HALF of this right: one matches on exact structure but is too strict (a paraphrase like "print"≈"present" no longer
matches at all), the other matches on soft meaning but is too loose (everything similar blurs together). Marry them:
represent each event by its full parts — the action, its little direction word ("out"/"in"/"up"), and its objects — match
each part by *meaning* (so paraphrases still match), but require *all* the parts to agree at once (so one wrong
direction-word kills the wrong candidate). Then the reasoning we already built should finally beat the simple baselines.

## 2. WHY THIS ONE
Reasoning over the story is the North Star's remaining half, and p6 proved the machinery is built and brain-faithful and
lands a *near*-miss (~59% vs ~52% baselines) — held back by exactly ONE thing: it matches the question's events to the
model by coarse similarity and picks the wrong one among look-alikes. p6 localized this to root cause with an error
drill and a headroom drill, named the brain mechanism (DG/CA3 pattern separation), and showed the fix has large,
MEASURED headroom (below). This is the single build that converts a rigorous near-positive into a clean positive — the
highest-leverage next step on reasoning — and the aligner it builds is reusable wherever the reader must match a
paraphrased mention to a stored event (belief, cued recall, the learner's cross-exposure consolidation).

## MEASURED vs INFERRED
- **MEASURED (inherit from p6; do NOT re-derive):** the reasoning STEP is sound — the reused `transitive_ordering`
  read-out beats a shuffled-order twin CI-sep and recovers true order under narrative reordering (0.74 vs 0.26). Clean
  extraction is NECESSARY but NOT SUFFICIENT (the oracle-spaCy loop-closer raised coverage 0.36→0.74 with accuracy flat
  at chance) → "extraction is the sole wall" is WITHDRAWN; the dominant residual is SEMANTIC cross-narrative ALIGNMENT.
  The compared events are NARRATED for 90–98% of questions (not a knowledge-not-in-text gap). ERROR drill: both the
  passage's own order and the learned schema cap ~0.55–0.59 because a coarse 12-d grounded cosine reads the order off the
  wrong pair ~40% of the time. HEADROOM drill (gold-free): of coarse-cosine-CONFUSABLE within-scenario event pairs, **98%
  (30066/30685) are SEPARABLE by particle/argument/prep** (only 2% identical on all slots = irreducible), and **51% of
  the before/after questions HINGE on a PARTICLE (in/out/up/back…)** the current verb+object code ignores. RESEARCH drill
  verdict: richer CONJUNCTIVE bound event codes (DG/CA3 pattern separation).
- **INFERRED (you must measure):** whether a grounded CONJUNCTIVE aligner with a soft-AND (multiplicative) per-role
  kernel — full role-fillers + path/particle + 2nd arg, grounded within a slot, PRODUCT across slots — pins the RIGHT
  event among similar distractors and lifts end-to-end reasoning CI-separated over BOTH floors, or whether the residual
  is irreducible (truly-unordered pairs + state-before-event commonsense + annotation noise) — a full-PASS located negative.

## 3. HOW THE BRAIN DOES THIS (the opening move)
**PINNED — DG/CA3 PATTERN SEPARATION.** The hippocampal dentate gyrus orthogonalizes similar inputs so overlapping
memories do not collide, and CA3 completes from a partial cue only AFTER that separation (Marr 1971; Treves & Rolls
1994; McClelland/McNaughton/O'Reilly 1995 CLS; Leutgeb et al. 2007; Yassa & Stark 2011 behavioral pattern separation —
small input changes drive large representational changes). Event identity is a role-filler CONJUNCTION individuated by
its ARGUMENTS + PARTICLES ("get OUT" vs "get IN" of the shower are DIFFERENT events sharing a verb), not the predicate
alone (Zwaan & Radvansky event-indexing; the argument/path is criterial). The computation to COPY: represent each event
as a grounded conjunctive code over its full role-fillers (verb + path/particle + arg1 + arg2), and match a paraphrased
cue by a soft-AND — a MULTIPLICATIVE (product) kernel across slots, each slot scored by GROUNDED similarity so a
paraphrase matches WITHIN a slot ("print"≈"present"), the PRODUCT across slots so a mismatch on ANY criterial slot (the
wrong particle) drives the joint score toward zero and suppresses the wrong candidate. That product IS the separation (a
conjunction, not a sum); an ADDITIVE/sum kernel is the FAN EFFECT (Anderson 1974) — the under-separation our current
matcher exhibits.

## 4. PINNED vs OUR-INVENTION (copy the computation, sweep the parameter)
- **PINNED (COPY exactly):** pattern separation of similar events via a CONJUNCTIVE (product / soft-AND) code over
  role-fillers; grounded (meaning-based) matching WITHIN a slot (so paraphrase survives); event identity individuated by
  arguments + particles, not the predicate; the `transitive_ordering` cognitive-map read-out (unchanged, the brain's one
  general relational-integration organ; Behrens 2018).
- **OUR-INVENTION-UNDER-TEST (SWEEP, do NOT adopt a number):** the grounded filler space (reuse the promoted grounded
  meaning codes; the 12-d coarse cosine is EXACTLY what fails — a richer code is the point, sweep it, do not adopt a
  dimensionality), the soft-AND temperature / kernel sharpness, WHICH slots enter the product (verb / particle-path /
  arg1 / arg2) and their weights, the confusable-set definition. Sweep, report the frontier, never hard-code a borrowed constant.

## ALREADY TRIED / DO NOT RE-RUN (this is NOT a re-tread)
- ⛔ **A coarse grounded-cosine aligner (the incumbent) reads order off the WRONG pair ~40% of the time** — do NOT just
  re-tune its threshold or dimensionality in place. The FIX is the CONJUNCTIVE soft-AND KERNEL, not a better cosine.
- ⛔ **`bound_event_backbone` alone (landed p4) is conjunctive but EXACT-HASH → OVER-separates:** it kills paraphrase (the
  0.48 symbol-tie in p6). Do NOT use its exact-match query raw. You want its conjunctive role-filler STRUCTURE with a
  GRADED grounded per-slot kernel.
- ⛔ **`content_addressable_retrieval` alone is graded but ADDITIVE → UNDER-separates** (the fan effect, ~40% mis-align).
  Do NOT use its additive partial-cue matching raw. The fix MARRIES the two: conjunctive structure + graded grounded
  slots + a PRODUCT (soft-AND) between them.
- ⛔ **`script_grain_acquisition_loop` (CA3/DG + MDL script learner) ALREADY HARD_FAILED MCScript2 alone** (same
  signature; surface via `experiment_index`). It needs THIS aligner — do NOT re-run it standalone expecting a different result.
- ⛔ **Do NOT rebuild the reasoning read-out.** `transitive_ordering` (the cognitive-map organ) is PROVEN as the read-out
  (twin loses CI-sep). ONLY the aligner's kernel changes.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- Read p6's `notes/problems/the_reader_cannot_reason_over_its_own_situation_model_on_real_inference/SOLVED.md` — this
  problem is its NEXT STEP #1 — and its `research_precise_event_alignment_mechanism_2026-09-01.md` (the DG/CA3 verdict +
  the headroom drill). Inherit; do not re-derive its numbers.
- Read `hdlab/bound_event_backbone.py` (conjunctive/exact-hash — the OVER-separation half; landed p4) and
  `hdlab/content_addressable_retrieval` (graded/additive — the UNDER-separation half). The fix marries their structures.
  Reuse `hdlab/transitive_ordering` (the read-out, unchanged) + the promoted grounded meaning codes for the per-slot kernel.
- Run `python tools/reader_capabilities.py`; compose over `SituationReader.read()` with the capable flags ON (incl.
  `bind_event_tokens`, the JOINT event token). Use MCScript2 before/after (p6's population, n=1128, chance 0.5) + a
  held-out slice; report n. Extract the PARTICLE / path + the 2nd argument (the criterial slots the current code drops).

## 5. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
PASS = the grounded soft-AND CONJUNCTIVE aligner lifts end-to-end before/after reasoning CI-SEPARATED over BOTH floors —
(a) the SIMILARITY-only floor and (b) the NO-situation-model text-position floor — on MCScript2 (held-out; report CI
half-width + null p95 beside every margin), with the info-free TWIN (an ADDITIVE-only kernel at the same rate, OR a
shuffled-order derangement) LOSING CI-separated, AND a can-fail ISOLATED alignment-precision probe passing first: given a
PARAPHRASED cue and a set of SIMILAR within-scenario distractor events, the soft-AND kernel selects the RIGHT event
CI-separated over both the coarse-cosine and the additive kernels. A PARTICLE/2nd-arg ABLATION (drop the criterial slots
→ accuracy falls toward the additive baseline) is the positive control that the CONJUNCTION does the work. **A rigorous
NEGATIVE is a full PASS if located:** if the soft-AND conjunctive grounded code, faithfully built, does NOT clean-clear
the floors, enumerate the irreducible residual precisely (which pairs are truly unordered / need state-before-event
commonsense / are annotation noise) and localize the ceiling. HONEST CEILING (p6's estimate, not a promise): ~0.59 →
~0.70–0.80 (a clean CI-sep positive over the floors), NOT human ~0.97 (~10–20% irreducible).

## 6. FLOORS + CONTROLS (the strongest trivial methods, actually run)
- **SIMILARITY-only floor** (paraphrase-similarity alone; ~0.527 in p6) + **NO-model text-position floor** (~0.539) —
  RECOMPUTE both on YOUR items with CIs; the strongest actually-run per contrast is the one to beat.
- **Info-free twin:** an ADDITIVE-only (sum) kernel at the same match rate, OR a per-scenario random-order derangement —
  must LOSE CI-sep (excludes "any conjunctive-ish matcher / any extra structure helps").
- **The isolated alignment-precision probe:** coarse-cosine vs additive vs soft-AND on (paraphrased cue → right event
  among similar distractors) — the can-fail discriminator that isolates the KERNEL from the end-to-end noise.
- **PARTICLE / 2nd-arg ablation** (positive control): remove the criterial slots from the code → the soft-AND advantage
  should collapse toward the additive baseline (proves the CONJUNCTION over particles/args is what separates).
- **A stronger-grounded-space arm** to confirm the lever is the SOFT-AND CONJUNCTION, not merely a richer per-slot code.

## 7. CORPUS-AGE + GENERALIZATION (owner priority — a constructed-gold win is not a capability)
Score on HELD-OUT MCScript2 (train-induced schemas only; leakage control over event TYPES not instances, as p6 did).
Report the per-construction breakdown (particle-hinged vs argument-hinged vs truly-unordered) so the win is localized to
the confusions the conjunction is supposed to fix. If you add a second population (another script/temporal benchmark),
say so and report n. A gain that only shows on the tuning set or one scenario type is not a capability.

## 8. FILES AND ENTRY POINTS
Build + validate in `experiments/` (compose over `SituationReader.read()` with capable flags ON; reuse
`bound_event_backbone`'s conjunctive role-filler structure + `content_addressable_retrieval`'s graded matching +
`transitive_ordering` as the read-out + grounded meaning codes for the per-slot kernel). A scaffold-free witness
recomputes, FROM SOURCE: the isolated alignment-precision probe (soft-AND > coarse-cosine > additive), the
particle/2nd-arg ablation, and end-to-end reasoning vs BOTH floors + the info-free twin, through the live reader on
held-out MCScript2. If it clears the bar, strategy lands the hdlab wire (Q111): the soft-AND conjunctive grounded aligner
(likely a thin composer over `bound_event_backbone` + `content_addressable_retrieval`), default-off, byte-identical when
off, witnessed. Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the event-alignment-precision wall = DG/CA3
pattern separation; the two organs each fail a different half).

## DO NOT QUOTE / DO NOT REDO
- 🚫 Do NOT quote p6's numbers (0.593 near-positive, 0.74/0.26 reordered, the 0.527/0.539 floors) as YOUR result — they
  are the MOTIVATION (a different aligner). Re-measure YOUR aligner's precision + end-to-end on your own population. No
  number crosses scorers/populations.
- 🚫 Do NOT quote the headroom stats (98% separable, 51% particle-hinged) as your result — they are the DE-RISK
  motivation, gold-free. Your result is the aligner's MEASURED precision + reasoning lift with CIs.
- 🚫 Do NOT reinvent `transitive_ordering` (reuse the promoted cognitive-map organ as the read-out) — the genuinely-new
  piece is ONLY the soft-AND conjunctive grounded KERNEL.
- 🚫 Do NOT use `bound_event_backbone`'s exact-hash raw (over-separates, kills paraphrase) NOR
  `content_addressable_retrieval`'s additive raw (under-separates, the fan effect) — the fix MARRIES them with a soft-AND
  grounded kernel. A submission that uses either half raw is a re-tread of p6's already-refuted 0.48/0.55 arms.
- 🚫 Do NOT use an external LLM as the semantic kernel or the aligner (the invariant). The per-slot similarity must be the
  substrate's own glass-box grounded/distributional code.
- 🚫 Do NOT claim the win without the isolated alignment-precision probe AND the particle/2nd-arg ablation — the soft-AND
  CONJUNCTION must be shown to do the work (an additive kernel or a particle-blind code winning would mean the conjunction is idle).
