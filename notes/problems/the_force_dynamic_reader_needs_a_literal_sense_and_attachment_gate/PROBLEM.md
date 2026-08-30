---
priority: 2
review:
review_text:
---

# PROBLEM: the force-dynamic causation reader has no way to tell a LITERAL physical event from a FIGURATIVE one, so it will FIRE on non-physical uses of physical verbs. The integrated patient-tendency estimator (`causation_typing_needs_a_patient_tendency_estimator`, EXCELLENT) types CAUSE/ENABLE/PREVENT well on LITERAL, correctly-parsed physical events — but its DEMONSTRATED boundary is that EVERY residual over-fire on unfiltered modern text is a WORD-SENSE / LITERAL-vs-FIGURATIVE / amod-ATTACHMENT error: "the news BROKE" (not a physical break), "she OPENED UP to him" (not a physical opening), "the deal FELL THROUGH" (idiom), or a modifier attached to the wrong noun. The estimator is conservative (fires 0.9% on UD-EWT, correctly abstains on the figurative/agentive majority), but with NO sense gate the causation typer wired into the LIVE reader would mislabel figurative sentences as physical force-dynamic events. Build a glass-box gate — word-sense / literal-vs-figurative classification + parse-based modifier ATTACHMENT — that lets the force-dynamic reader ENGAGE only on literal, correctly-attached physical events, and ABSTAIN otherwise. This is the OWNER-DIRECTED PREREQUISITE (2026-08-30, "queue another problem before wiring it in") that must land BEFORE the causation live-wiring (`wire_the_causation_typer_into_the_live_reader`, now BLOCKED on this).

**slug:** `the_force_dynamic_reader_needs_a_literal_sense_and_attachment_gate` — **opened:** 2026-08-30 by the strategy session
(owner-directed; the demonstrated boundary of the integrated patient-tendency estimator). **status:** OPEN — a MECHANISM + BUILD
problem (a precision gate on the force-dynamic reader). You build + validate in `experiments/`; strategy lands any hdlab change
(Q111). NO external LLM at inference (the invariant). **Convergent with `no_glass_box_verb_sense_disambiguation` (integrated)** —
REUSE/extend that machinery where it fits; do NOT rebuild general WSD. This is the FORCE-DYNAMIC-READER-SPECIFIC gate:
literal-physical-event detection + attachment, not general sense tagging.

> **PRIORITY NOTE (the call is the strategy session's):** filed at `2` — HIGH, because it is the OWNER-DIRECTED PREREQUISITE that
> UNBLOCKS the whole causation live-wiring (p6, demoted + blocked on this). Without it, wiring the causation typer live over-fires
> on figurative text — a visible correctness regression. Ranked above the focus-stack (p3) only because it gates an in-flight
> wiring the owner asked to protect. **Re-rank per the owner.** Dependency: consumes the patient-tendency estimator + the force
> typer; gates their entry into `situation_reader._read_causation`.

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
We just built the part of the reader that tells apart "the wind opened the gate" (forced) from "the key opened the gate"
(allowed). It works well — as long as the sentence is about a real, physical thing happening. But the same physical words
get used all the time in NON-physical ways: "the news broke," "she opened up to him," "the deal fell through," "he was
crushed by the criticism." A reader that just sees the word "broke" or "opened" and runs its physics on it would confidently
mislabel these. Right now our causation reader has no way to notice "this isn't a literal physical event — stay out of it."
This problem builds that off-switch: a glass-box gate that recognises which sense a word is being used in and whether the
describing words are even attached to the right thing, so the physics engine only runs when there really is physics.

## 2. WHY THIS ONE
It is the OWNER-DIRECTED PREREQUISITE for wiring causation into the live reader (2026-08-30). The patient-tendency estimator's
own evidence names this exact boundary: on unfiltered modern text every residual over-fire is a word-sense / literal-vs-figurative
/ attachment error. Wiring the causation typer live WITHOUT this gate is a known correctness regression on figurative prose.
It is also foundational beyond causation — literal/figurative sensing and sense-appropriate engagement gate every grounded
organ (a magnitude reader should not run on "a HEAVY heart"; a spatial reader should not run on "in HOT water"). Getting the
glass-box version right here pays off across the substrate.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (replicate the computation):** sense selection = controlled semantic cognition (LIFG / pMTG semantic control selects
  the context-appropriate sense; Lambon Ralph / Jefferies). Figurative/idiom recognition is context-graded (Giora's graded
  salience; conventional figurative meanings are recognised, not literally composed). Grounded simulation gates literalness —
  a literal physical event affords a sensorimotor simulation; a figurative one does not (Bergen; Barsalou). Attachment =
  the parser's dependency structure (which amod/nmod actually modifies the head).
- **OUR-INVENTION (flag + sweep):** the literal-vs-figurative decision rule (a classifier, a selectional-preference violation
  detector, an idiom lexicon, or a simulation-affordance score — the solver picks the most brain-faithful that WORKS + says why);
  any thresholds; the closed set of figurative constructions covered. Glass-box, no external LLM.

## 4. MEASURED vs INFERRED
- **MEASURED (the boundary this closes):** the patient-tendency estimator fires 0.9% on unfiltered UD-EWT and its residual
  over-fires are ALL sense/attachment errors (integrated `causation_typing_needs_a_patient_tendency_estimator`); the over-fire
  count already dropped 17→3/318 once grounded-conceptual generalization replaced word lists — the remaining 3 are the target.
- **INFERRED (you must measure):** whether a glass-box sense/attachment gate raises the force-dynamic reader's FIRE-PRECISION on
  unfiltered modern text (fewer figurative false-fires) WITHOUT dropping the genuine literal physical cases (recall on the
  7/7 modern tendency cases + the constructed literal set must not regress).

## 5. ALREADY TRIED / DO NOT RE-RUN
- The patient-tendency estimator itself (DONE, EXCELLENT) — you CONSUME it, you do not rebuild it; the gate wraps its input.
- `no_glass_box_verb_sense_disambiguation` (integrated) — its idiom/sense machinery is REUSABLE; check it first (`experiments/idiom_lexicon` / the WSD organ) and extend rather than duplicate. State on disk what you reused.
- Word-list gating already failed (over-fired); grounded-conceptual features already helped (17→3). Build on that, don't revert.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read the patient-tendency SOLVED + `experiments/_patient_tendency.py` — where it fires + why it over-fires (the 3 residuals).
- Read `hdlab/force_dynamics_typer.py` and `no_glass_box_verb_sense_disambiguation`'s landed WSD/idiom pieces — what already exists.
- Confirm the over-fire cases on UD-EWT are sense/attachment (reproduce the generalization probe); if some are a DIFFERENT error class, SAY SO (that reframes the problem).

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
On unfiltered MODERN text (UD-EWT generalization probe is the ready testbed; MIND THE CORPUS-AGE CONFOUND — modern, not McGuffey):
- **PASS =** the gated force-dynamic reader beats the strongest real floor — the current UN-gated estimator (its measured
  false-fire rate on figurative/agentive text) AND a naive "fire on any physical-verb lemma" baseline — on FIRE-PRECISION,
  CI-separated (bootstrap; report CI half-width + null p95), while RECALL on the genuine literal physical cases does NOT regress
  CI-separated. The info-free **twin (shuffled sense labels / permuted attachment) MUST LOSE** CI-separated.
- **A rigorous NEGATIVE is a full PASS:** if a faithfully-built sense/attachment gate cannot separate literal from figurative on
  real text without killing literal recall, that is a real result — name why (e.g. the residual is attachment not sense, or the
  figurative cases are too sparse to score), enumerated, and it still tells us whether the causation wiring can safely proceed.

## 8. FILES AND ENTRY POINTS
- Consumes: `experiments/_patient_tendency.py` (+ its UD-EWT probe `exp_patient_tendency_generalization_udewt_v1`), `hdlab/force_dynamics_typer.py`,
  the landed WSD/idiom pieces from `no_glass_box_verb_sense_disambiguation`.
- Build + validate in `experiments/`; witness `verification/test_*_organ.py` recomputing from source. Fold an **AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.
- **This UNBLOCKS `wire_the_causation_typer_into_the_live_reader` (p6):** once this gate passes, the causation live-wiring can proceed (typer + patient-tendency + this gate → engage only on literal physical events).
