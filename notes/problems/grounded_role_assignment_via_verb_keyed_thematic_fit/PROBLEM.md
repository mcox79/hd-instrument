---
priority:
review: STRONG
review_text: "SOLVED (owner-DONE, self-graded PARTIAL) integrated 2026-08-30 — a rigorous NEGATIVE + strategic REDIRECT that refutes the brief's thematic-fit premise WITH POWER and maps the real fix to PARSE QUALITY. Reverified FIRST-HAND: test_grounded_role_gate_organ.py 14/14 (scaffold-free). Built the brain-faithful gate the brief asked for — a JOINT clause-level NOISY-CHANNEL decision (Gibson/Bergen/Piantadosi 2013 + MacWhinney Competition Model + McRae thematic fit): adopt the word-order reading unless the role-SWAP reading is plausible enough to beat a construction prior, waived by reliable passive morphology. TWO-REGIME result: (A) CLEAN-PARSE (modern UD-EWT gold, n=3591): the achievable non-canonical fix is STRUCTURAL ROUTING, NOT thematic fit — route_only (reliable-markedness override, no fit) 0.9858 beats word order +0.049 [0.042,0.056] and the landed graded_role +0.081 [0.072,0.091] CI-sep, canonical/reversible UNregressed; fit does NOT CI-separate from graded_role (a gold parse removes the uncertainty fit resolves; graded_role hides an animacy cue). The brief's premise is REFUTED for clean parses — exactly as noisy-channel theory predicts (a regime artifact). (B) WEAK-PARSER DEPLOYMENT (modern QA-SRL role-balanced gold through the reader's OWN noisy live front-end, non-canonical n=1224): the fit gate DOES beat BOTH floors — word order 0.149 (+0.126 [0.102,0.149]) AND graded_role 0.118 (+0.157 [0.130,0.186]) CI-sep, twin LOSING (+0.052); AND generalizes to held-out UNSEEN (verb,noun) pairs (n=299, +0.067 vs order / +0.054 vs structure CI-sep). BUT it REGRESSES canonical (0.655 vs 0.836) and a full tau sweep shows the tradeoff is IRREDUCIBLE (no threshold beats the non-canonical floor while preserving canonical). So P1 (beat floors + NO regression) FAILS; the bar's P2 rigorous-negative clause is MET WITH POWER. THE MAP TO THE REAL FIX (the deliverable): the non-canonical collapse is a PARSE-QUALITY problem, not a thematic-fit problem — a modern dependency parser (spaCy, substrate-native, NO LLM) scores structural roles 0.9959/0.9915 balanced non-canonical, DOMINATING word order, graded_role, and every fit gate. BRAIN-FAITHFUL TARGET = an INCREMENTAL, cue-integrated PREDICTIVE structure-builder (Lewis-Vasishth; MacDonald; Levy — order + morphology + thematic fit competing DURING attachment; relocates fit to ONLINE where the brain puts it, resolving the canonical tradeoff the post-hoc gate cannot); spaCy is OUR-SUBSTITUTION / reference-ceiling + admissible interim, NOT a brain model. Strong controls (structure-shuffled twin loses; a noisy-channel CORRUPTION CURVE — the gate-minus-structure gap grows monotonically as morphology is masked, the Gibson signature; independent derivation, no circularity). HONEST generalization + a self-correction: the count-fit TWIN edge does NOT survive to unseen pairs (+0.023 NOT_SEP) → the fit signal is largely SEEN-PAIR MEMORIZATION, reported not hidden. Grade STRONG (a rigorous, powerful negative that refutes the premise, maps the real fix, fences the dead-ends, and delivers a landable complementary fix; deflated from EXCELLENT only because the headline capability P1 failed — the honest correct outcome). STRATEGY ACTIONS: (1) hdlab landing QUEUED (Q111) — the routing PRECISION FIX to `graded_role_assigner`: restrict the structural override to RELIABLE strong-passive markedness only (drop the weak bare-participle override) → +0.081 aggregate CI-sep, fit-independent, no regression. ⚠️ needs an END-TO-END live-reader validation before landing (the solver's own phase-gate trap: measure on the live reader, not in isolation) → a careful default-safe landing, not inline. (2) The PARSE-QUALITY REDIRECT + the solver's ready-made `FOLLOW_ON_PROPOSAL_parse_frontend_upgrade.md` (an 8-section brief for the incremental cue-integrated predictive structure-builder) FEED p1 `the_extraction_front_end_recovers_only_a_third_of_events_and_roles` (in-progress) — the p3 finding IS p1's diagnosis (the non-canonical role collapse is parse-quality; spaCy is the admissible-interim ceiling; the incremental predictive parser is the brain-faithful target). NOT packaged as a separate problem (overlaps p1; the FOLLOW_ON_PROPOSAL is ready-to-lift IF p1's diagnosis confirms the incremental-parser is a distinct build). FENCED dead-ends (do NOT re-open): thematic-fit fit-vector work, the post-hoc fit gate (irreducible tradeoff), fused-always / linear-sum / precision-weighted (all hurt canonical). Audit §2b folded."
---

> ## ✅ SOLVER REVIEW — INTEGRATED 2026-08-30 (grade: STRONG; SOLVED owner-DONE, self-graded PARTIAL)
> **Verdict:** a rigorous, powerful NEGATIVE + strategic redirect. Reverified first-hand (`test_grounded_role_gate_organ.py`
> **14/14**). Built the brain-faithful noisy-channel gate the brief asked for, then found the **two-regime truth**: on CLEAN
> parses the fix is STRUCTURAL ROUTING not thematic fit (premise refuted, route_only 0.9858 beats word-order + graded_role
> CI-sep); in the WEAK-PARSER deployment regime the fit gate beats both floors + generalizes to unseen pairs BUT has an
> **irreducible canonical tradeoff** (P1 fails, the rigorous-negative P2 clause met with power). **The real fix is PARSE
> QUALITY** — spaCy structural roles 0.9959 dominate everything; the brain-faithful target is an incremental cue-integrated
> predictive structure-builder. Honest self-correction (the count-fit edge is seen-pair memorization, doesn't survive to
> unseen). **Grade STRONG.** Strategy: (1) the routing precision-fix to `graded_role_assigner` (+0.081, fit-independent)
> QUEUED (needs end-to-end live-reader validation first — the phase-gate trap); (2) the parse-quality redirect + the ready-made
> `FOLLOW_ON_PROPOSAL_parse_frontend_upgrade.md` FEED p1 (the extraction front-end) — the p3 finding IS p1's diagnosis; NOT
> packaged separately (overlaps p1). Audit §2b folded; `priority:` cleared.

# PROBLEM: the reader assigns thematic roles from SURFACE WORD ORDER, so it COLLAPSES on non-canonical order — the McGuffey→modern migration (`the_reader_eval_is_scored_on_200_year_old_mcguffey_migrate_to_modern_text`, integrated EXCELLENT) MEASURED it: on modern text the role front-end does not clear its floor and drops to 0.288 on non-canonical constructions (passive / fronting / inversion), BELOW a coin-flip twin and CI-separated below the floor; McGuffey's ~0% non-canonical rate structurally HID this (the corpus-age confound made numeric). The migration's de-risk PoC (`exp_mcguffey_migrate_grounded_thematic_fit_poc_v1`) PROVED the brain-faithful fix: a CONSTRUCTION-INDEPENDENT grounded thematic-fit signal (does this noun PLAUSIBLY fill this role for this verb — "a key cannot surround", "a ball cannot kick") clears the non-canonical wall (0.688 vs 0.039 surface word-order, vs 0.05 for a surface-cue learner), and it NEVER uses the test item's word order. What is NOT yet built is the GATE: grounded plausibility must OVERRIDE misleading word order ONLY when order and plausibility CONFLICT (a non-canonical/reversible cue), and stay OUT of the way on canonical, unambiguous sentences — a linear cue-SUM reaches NEITHER domain (0.100 < fit-alone 0.227 on held-out inversion; conflict-validity is a GATE, not a weight). Build the verb-keyed grounded thematic-fit role assigner with a conflict/surprisal recruitment gate, and validate it overrides misleading order ON THE HELD-OUT NON-CANONICAL SUBSET without touching canonical or reversible-ambiguous cases.

**slug:** `grounded_role_assignment_via_verb_keyed_thematic_fit` — **opened:** 2026-08-30 by the strategy session (the FLAGSHIP
follow-on the integrated McGuffey migration seeded). **status:** OPEN — a MECHANISM + BUILD problem (extends the role path with a
gated grounded-plausibility competitor). You build + validate in `experiments/`; strategy lands any hdlab change (Q111). NO
external LLM at inference (the invariant). **De-risked:** the migration's PoC already proved the thematic-fit signal clears the
wall — the un-built piece is the RECRUITMENT GATE, not the fit signal.

> **PRIORITY NOTE (the call is the strategy session's):** filed at `3` — HIGH. It is the concrete fix for the generalization
> COLLAPSE the migration just exposed (the owner's first-class generalization concern), the mechanism is de-risked (PoC clears
> the wall), and the architecture is PINNED with two wrong approaches already fenced. Ranked above the QA capstone (p5) — a
> reader that mis-assigns roles on non-canonical order will fail the capstone's questions. **Re-rank per the owner.**
> **DEPENDENCY / SEQUENCING (from the migration):** the grounded thematic-fit VECTORS are supplied best by
> `distributional_meaning_channel` (the meaning organ, already built) — the PoC works with current vectors; the meaning channel
> raises their quality. Wire/consult the meaning channel for the fit vectors; do not rebuild it.

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
Our reader figures out "who did what to whom" mostly from word order — the noun before the verb is the doer. That works for
plain sentences but breaks the moment a sentence is arranged differently: "the ball was kicked by the boy," "the ball, the boy
kicked." We just proved on modern text that the reader collapses on these (worse than a coin flip). The human fix is obvious
once named: you also know a ball can't kick and a boy can, so you use *plausibility* to override the misleading order. The
catch — and the whole difficulty — is that plausibility must only step in when it *disagrees* with word order; on a normal
sentence, or when both nouns could plausibly do the action ("the dog chased the cat"), it must stay quiet and let order/grammar
decide. Build that: a plausibility judge for roles, plus the gate that recruits it only on conflict.

## 2. WHY THIS ONE
It is the concrete fix for the generalization failure the McGuffey→modern migration exposed, and generalization is the owner's
first-class priority. The migration made it numeric (non-canonical 0.288, below chance) and the de-risk PoC already proved the
mechanism clears it (0.688). The remaining work is not a fishing expedition — it is building one named component (the conflict
gate) on a proven signal. It also compounds: correct roles on non-canonical order feed who-did-what, the situation model, and
the QA capstone.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (replicate):** thematic fit — comprehenders use verb-specific argument plausibility to assign roles, immediately and
  gradiently (McRae, Spivey-Knowlton & Tanenhaus 1998; Ferretti/McRae). Integration is PRECISION/RELIABILITY-WEIGHTED with a
  CONFLICT-VALIDITY gate (MacWhinney Competition Model — a cue is recruited in proportion to its validity given the *conflict*;
  Ernst & Banks 2002; Gibson noisy-channel 2013; Feldman & Friston precision=gain). Roles resolve on GRAMMATICAL FUNCTION + VOICE
  (the landed `graded_role_assigner`), with thematic fit as the tie-breaker/override under conflict — NOT a linear cue-sum.
- **OUR-INVENTION (flag + sweep):** the RELIABILITY / surprisal / route-conflict ESTIMATOR that decides *when* to recruit fit
  (the sole un-built piece); the role-prototype construction; thresholds. Fit vectors come from `distributional_meaning_channel`
  (consult, don't rebuild). Glass-box, no external LLM.

## 4. MEASURED vs INFERRED
- **MEASURED (de-risked):** grounded thematic-fit clears the held-out non-canonical wall (PoC: 0.688 vs 0.039 surface, twin at
  chance, fit never sees the test item's order); a LINEAR cue-sum reaches NEITHER domain (0.100 < fit-alone 0.227 on held-out
  inversion) → conflict-validity is a GATE, not a weight; two on-disk wrong approaches are FENCED (scalar-over-fused = inert;
  margin-gating = HARD_FAIL). INVERSION stays hard even for fit (0.21) — it is a PARSE problem, out of scope here.
- **INFERRED (you must measure):** whether a verb-keyed thematic-fit competitor with a conflict/surprisal recruitment gate
  overrides misleading order on the HELD-OUT non-canonical subset WITHOUT touching canonical order or reversible-ambiguous cases.

## 5. ALREADY TRIED / DO NOT RE-RUN
- A LINEAR cue-sum (reaches neither domain); scalar-over-fused (inert); margin-gating (HARD_FAIL) — all fenced; do not revert.
- A pure SURFACE-cue learner (walls on unseen constructions, 0.000/0.05 held-out — the Competition Model's conflict-validity
  predicts it exactly).
- The grounded thematic-fit SIGNAL itself is de-risked (PoC) — you BUILD THE GATE on it, you do not re-prove the signal.
- The existential/expletive-"there" + inversion parse issues are a SEPARATE landing (graded_role_assigner subject-override,
  strategy-queued) — do not fold them in.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read the McGuffey SOLVED §"grounded thematic fit" + `exp_mcguffey_migrate_grounded_thematic_fit_poc_v1.py` +
  `exp_mcguffey_migrate_precision_weighted_v1.py` — the proven signal + the reliability-weighting finding.
- Read `hdlab/graded_role_assigner.py` (the landed grammatical-function role path you extend) and `hdlab/distributional_meaning_channel.py`
  (the fit-vector source). Confirm on disk that the recruitment GATE is the un-built piece.
- Use the MODERN eval gold `data/eval_gold_mention_role_modern_ud_ewt_v1/` (MIND THE CORPUS-AGE CONFOUND — do NOT score on McGuffey).

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
On the MODERN UD-EWT role gold, scored on the HELD-OUT NON-CANONICAL subset (NOT the canonical-dominated aggregate):
- **PASS =** the gated verb-keyed thematic-fit role assigner beats BOTH the strongest floors — naive-first-noun (word order) AND
  the current grammatical-function assigner — on the non-canonical subset, CI-separated (bootstrap; CI half-width + null p95),
  with the info-free **structure-shuffled twin LOSING**; AND it does NOT regress canonical order or the reversible-ambiguous
  subset (the gate must stay OUT when order and fit do not conflict — a fused-always control that hurts canonical FAILS).
- **A rigorous NEGATIVE is a full PASS:** if a faithfully-built conflict gate cannot separate override-when-conflicting from
  leave-alone-when-not without hurting canonical/reversibles, that is a real result — name why (the gate's estimator, the fit
  vector quality, or the meaning-channel dependency), enumerated.

## 8. FILES AND ENTRY POINTS
- Consumes: `exp_mcguffey_migrate_grounded_thematic_fit_poc_v1.py` (the proven signal), `hdlab/graded_role_assigner.py` (extend),
  `hdlab/distributional_meaning_channel.py` (fit vectors), `data/eval_gold_mention_role_modern_ud_ewt_v1/` (modern gold).
- Build + validate in `experiments/`; witness `verification/test_*_organ.py` recomputing from source on the held-out subset.
  Fold an **AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the CAUSATION/role + Competition-Model entries).
- Coordinate: the strategy-queued `graded_role_assigner` subject-override + the meaning-channel wiring; compose, don't collide.


## DO NOT QUOTE / DO NOT REDO
- 🚫 This problem is INTEGRATED — the honest result + caveats are in `review_text` (frontmatter) and `INTEGRATED_BY_STRATEGY` (SOLVED.md). Do NOT quote its numbers across a different scorer / population / representation (standing rule: no number crosses scorers or populations); recompute every floor on the target item's own population.
- 🚫 The direction is CLOSED for re-derivation — build ON it, do not re-run it.
