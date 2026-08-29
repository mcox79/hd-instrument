---
priority:
review: EXCELLENT
review_text: "SOLVED (owner-DONE) integrated 2026-08-29 — a RIGOROUS NEGATIVE that RETIRES a suspected confound + a built brain-faithful fix for the one real exception. Reverified FIRST-HAND: test_role_parse_accuracy_archaic.py 26/26 PASS. THE WHOLESALE FEAR IS REFUTED (organ-level conclusions STAND): spaCy's subject-ID is NOT degraded on 19c literary prose — natural LitBank 0.94 ≥ modern textbook 0.89, FLAT to 40+ token sentences (70% of literary subjects are easy pronouns); the archaic-vs-modern gap is NOT CI-separable (perm null p95 0.098 > gap 0.051). Downstream cost ~0: the coref cache's roles are provably spaCy-derived (19 nominative-pronoun-as-OBJECT labels a human would never write), but correcting ALL 59 errors moves coref accuracy by −0.0009; a sensitivity curve shows ~10–20% error is needed before coref degrades, and spaCy's actual ~0.6% is far below — the confound is REAL but IMMATERIAL to aggregate coref. THE ONE REAL EXCEPTION (register-isolated by content+length-matched minimal pairs): subject-verb INVERSION ('replied he' → spaCy tags 'he' a DIRECT OBJECT) + archaic morphology, +0.22 CI-sep; on real dialogue-tag inversion spaCy is 0.47; incidence ~4–12/1000 verbs (concentrated in dialogue) + archaic morphology 0.77%. THE BRAIN-FAITHFUL FIX (PINNED — Competition Model/eADM; Bresnan; Iatridou & Embick; Pinker & Ullman): a glass-box POSITION-DOMINANT + cue-OVERRIDE subject stage (case / conditional-auxiliary-trigger / locative-inversion unaccusative-class / quote-aware reporting-frame + a small STORED archaic-morphology lexicon) recovers real dialogue inversion 0.47→0.83 CI-sep, info-free twin 0.23 LOSES, register-invariant (archaic 0.91 ≈ modern 0.96), and LIFTS modern too 0.76→0.89 (no regression). PUSHED FURTHER: the solver REFUTED its OWN 'cue-first replacement' instinct (a cue-first REPLACEMENT loses on canonical cases — position-dominant+override is the faithful shape, matching graded_role_assigner's design); and at the EME extreme (Shakespeare, 165× denser morphology) spaCy's POS tagger COLLAPSES (subject accuracy 0.07) but the brain-faithful cascade + stored lexicon RECOVERS it to 0.75 (thee-accusative case control 0.78 — it respects case). Grade EXCELLENT (a rigorous negative retiring a confound with a positive control + a sensitivity curve, PLUS a built PINNED register-invariant fix for the bounded exception, PLUS self-refutation, PLUS the EME extreme). hdlab landing QUEUED (Q111 — coupled): add the position-dominant + cue-override subject stage to graded_role_assigner (reference impls exp_role_cue_repair_inversion_v1.repaired_subject_span + exp_role_cue_first_subject_v1.full_cue_subject) + rebuild data/litbank/who_did_what_events.json through it. AUDIT §2b folded (corpus-age parse confound: SUSPECTED-UNMEASURED → MEASURED-BOUNDED — retired for the aggregate, one characterized inversion exception + the EME register-extreme, both with a built fix). Honest caveat (I concur): the fix is proven on constructed + hand-built inversion sets; automatic-extraction scale-up is implied. NEXT PROBLEMS primed: (1) an archaic-morphology POS/role lexicon (gated on EME/KJV being on the live path); (2) a case-override for incremental_parser (fails dialogue inversion 0.000)."
---

> ## ✅ SOLVER REVIEW — INTEGRATED 2026-08-29 (grade: EXCELLENT; SOLVED owner-DONE — rigorous negative + a built fix)
> **Verdict:** a rigorous negative that RETIRES a suspected confound, plus a built brain-faithful fix for the one real
> exception. Reverified first-hand (`test_role_parse_accuracy_archaic.py` **26/26 PASS**).
> **The wholesale fear is REFUTED — organ-level conclusions STAND:** spaCy's subject-ID is NOT degraded on 19c prose
> (LitBank 0.94 ≥ modern 0.89, flat to 40+ tokens; the archaic-vs-modern gap is NOT CI-separable). **Downstream cost ~0:**
> correcting ALL 59 role errors moves coref accuracy by **−0.0009**; a sensitivity curve shows ~10–20% error is needed to
> degrade coref and spaCy's actual is ~0.6% — real but immaterial. (A positive control — the shuffle — DOES move it, so the
> null is meaningful, not underpowered.)
> **The one real exception:** subject-verb INVERSION ("replied he" → spaCy tags "he" a direct object) + archaic morphology,
> +0.22 CI-sep, ~4–12/1000 verbs (dialogue). **The fix (PINNED — Competition Model/eADM; Bresnan; Pinker & Ullman):** a
> glass-box position-dominant + cue-override subject stage (case / conditional-trigger / locative-inversion / quote-aware +
> a stored archaic-morphology lexicon) recovers inversion **0.47→0.83** CI-sep, twin 0.23 loses, register-invariant, and
> lifts modern too (no regression).
> **Pushed further:** self-refuted its own "cue-first replacement" instinct (position-dominant+override is faithful,
> matching `graded_role_assigner`); and at the Shakespeare EME extreme spaCy collapses (0.07) while the cascade recovers to
> 0.75 (respecting case). **Grade EXCELLENT.**
> **Landing QUEUED (Q111 — coupled):** add the cue-override subject stage to `graded_role_assigner` (ref impls
> `exp_role_cue_repair_inversion_v1.repaired_subject_span`) + rebuild `data/litbank/who_did_what_events.json` through it.
> **Audit** §2b folded: the corpus-age parse confound is **SUSPECTED-UNMEASURED → MEASURED-BOUNDED** (retired for the
> aggregate; one inversion exception + the EME extreme, both with a built fix). **Next primed:** an archaic-morphology lexicon;
> a case-override for `incremental_parser`.

# PROBLEM: every organ that reads a grammatical role (the coref subjecthood cue, the incumbent Centering tier, the SPACE motion gate, the who-did-what reader) gets that role from a spaCy dependency parse of the reading corpus — but the corpus is 100–200-year-old literary prose (LitBank / McGuffey), and spaCy's parser is trained on modern text, so the `nsubj`/`dobj`/`nmod` labels the whole stack trusts may be systematically DEGRADED on archaic long-sentence prose and NO organ has measured it. This is a SUSPECTED-UNMEASURED confound flagged by the coref integration (adjacency 6). MEASURE the parser's role accuracy on archaic prose vs a gold (and vs modern prose), quantify how much it degrades the downstream role cues, and — if it degrades CI-separated — build the brain-faithful fix; a rigorous NULL (the parse is fine, not the bottleneck) is a full pass that RETIRES the confound

**slug:** `role_assignment_is_untested_on_archaic_literary_prose` — **opened:** 2026-08-28 by the strategy session (the
SUSPECTED-UNMEASURED confound flagged by the integrated `coreference_is_capped_at_065_on_real_narrative`, adjacency 6:
"both the incumbent tier and this resolver's subjecthood cue read spaCy nsubj→SUBJECT off 200-year-old long-sentence
prose; parse noise there degrades the subjecthood signal for everyone. Not measured here (honest label)"). **status:**
OPEN — a MEASUREMENT-FIRST problem (a probe that may become a build). You build + measure in `experiments/`; strategy
lands any hdlab change (Q111).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `8` — a MEASUREMENT that could re-rank the whole coref
> / role-assignment line: if the parse is the real cap on archaic prose, several "the organ is weak" conclusions are
> actually "the parse is weak", and the fix is upstream. It directly discharges the standing CORPUS-AGE confound the
> owner keeps flagging. A rigorous NULL is as valuable as a positive — it RETIRES a suspicion. **Re-rank per the owner.**

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
Almost every reading organ that needs to know "who is the subject / who is the doer" gets it from an automatic grammar
parser (spaCy) run over the story text. But our stories are old — LitBank novels and McGuffey readers are 100–200 years
old, with long, inverted, archaic sentences the parser was never trained on. If the parser mislabels the subject on that
prose, then EVERY organ downstream — the coreference subjecthood cue, the old Centering tier, the SPACE motion reader,
the who-did-what reader — inherits the error, and we may be blaming the ORGANS for what is really a PARSE problem. Nobody
has measured this. The task: measure how accurately the parser assigns grammatical roles on archaic prose (against a gold,
and against modern prose as a reference), quantify how much any degradation costs the downstream role cues, and — if it
degrades CI-separated — build the brain-faithful fix (the brain does not depend on a modern-newswire grammar). A rigorous
NULL (the parse is accurate enough; it is NOT the bottleneck) is a full pass — it RETIRES the corpus-age parse suspicion
so the organ-level conclusions stand.

## 2. WHY THIS ONE
It is a shared, upstream confound under a whole line of work: if the parse is the real cap on archaic prose, then
"the coref tier is weak", "the role labeler is weak", "the SPACE motion gate misfires" are partly mis-attributed, and the
highest-leverage fix is upstream. It directly discharges the standing CORPUS-AGE confound. And a clean NULL is genuinely
valuable — it lets the substrate trust its role cues on this corpus.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** grammatical-function / role assignment from word order + morphology + agreement is a
  CORE, robust human competence — the brain parses archaic and modern prose alike using cue-based, graded constituency
  (Competition Model cue validity; incremental left-to-right attachment). Crucially the brain does NOT rely on a
  fixed newswire grammar; it uses distributional + morphological + agreement cues that transfer across registers.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** our reliance on a MODERN-trained spaCy dependency parse as the role
  source is an OUR-INVENTION shortcut, not the brain's mechanism — its transfer to archaic prose is the thing to MEASURE.
  If it degrades, the brain-faithful fix is a register-robust cue-based role assignment (agreement + word-order + the
  substrate's own graded cue-combination) rather than a better-trained external parser (barred at inference). SWEEP the
  cue set; copy the graded cue-combination computation.
- **NOT brain-faithful:** trusting `nsubj`/`dobj` labels as ground truth without measuring their accuracy on this
  register; swapping in a bigger external parser at inference (the invariant bars an external model in the loop).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE — do not re-derive):** the coref resolver + incumbent tier both read spaCy `nsubj`→SUBJECT
  (adjacency 6, flagged SUSPECTED-UNMEASURED); the SPACE motion gate + who-did-what reader read the same parse; LitBank
  has gold coref (and constituency in the source PTB-style annotations for some texts) usable to check parse quality.
- **INFERRED (to prove):** the parser's role accuracy on archaic prose, whether it degrades vs modern prose CI-separated,
  how much that degradation costs the downstream role cues, and whether a register-robust cue-based assignment recovers it
  — OR a rigorous null (no meaningful degradation) that retires the confound.

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT swap in a different external parser / LLM at inference (barred). Do NOT re-solve the coref tier or the role
  labeler (this MEASURES their shared input). REUSE the substrate's graded cue-combination for any fix. Keep EXISTS /
  IS-ACCURATE / IS-THE-BOTTLENECK separate (measure each; a positive control that the downstream metric can move).

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read the coref SOLVED (adjacency 6 — the exact claim); the parse consumers (`hdlab/coreference_resolver.py`
  subjecthood cue, the SPACE gate, the who-did-what reader). `tools/experiment_index.py query "parse"` / `"nsubj"` /
  `"dependency"` / `"role"`. Audit: the arc-parser / thematic-role entries + the CORPUS-AGE note (McGuffey ~200yo).
- Gold: a grammatical-role gold on archaic prose (LitBank's source constituency, a hand-checked sample, or a
  modern-vs-archaic matched pair) — state how built + verified. A modern-prose reference arm (OntoNotes / a modern
  novel) to isolate REGISTER from difficulty.

## 7. THE BAR
PASSES only with ALL of:
1. **Measured parser role accuracy on archaic prose** against a real role gold, WITH a modern-prose reference arm
   (isolates register from sentence-length difficulty), recomputed on matched populations. Report the degradation (if
   any) CI-separated with half-width + null p95.
2. **The downstream cost quantified:** how much the parse error propagates into a role cue the organs consume (e.g. the
   coref subjecthood cue accuracy with GOLD roles vs spaCy roles on the same items) — a POSITIVE control that the
   downstream metric CAN move.
3. **EITHER** a register-robust cue-based role assignment that recovers the degradation CI-separated over the spaCy-role
   floor with an info-free twin (shuffled cues) LOSING — **OR** a rigorous NULL (spaCy roles are CI-equal to gold on this
   corpus → the parse is NOT the bottleneck, the confound is RETIRED and the organ-level conclusions stand).
4. **One-screen summary:** parse accuracy (archaic vs modern) → downstream cost → fix-or-null → verdict. Heavy → REMOTE.
A rigorous NEGATIVE is a FULL PASS — a clean null here is a high-value result (it discharges a standing suspicion).

## 8. FILES AND ENTRY POINTS
- Parse consumers: `hdlab/coreference_resolver.py` (subjecthood cue), the SPACE gate (`experiments/location_register.py`),
  the who-did-what reader. Data: LitBank (gold coref + source constituency), a modern-prose reference. Audit:
  `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (arc parser / thematic role + corpus-age). Heavy → REMOTE.

## DO NOT QUOTE / DO NOT REDO
The "SUSPECTED-UNMEASURED" label is the MOTIVATING flag, not a result — MEASURE it. Do NOT swap in an external parser at
inference. Strategy owns any hdlab landing — you propose the measurement + any cue-based fix, you do not write `hdlab/`.
