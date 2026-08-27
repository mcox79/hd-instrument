---
priority: 1
review:
review_text:
---

# PROBLEM: our parser and role assigner make HARD, DISCRETE decisions (commit to one attachment / one role) where the brain runs GRADED probabilistic competition -- a substrate-wide deviation that only bites on ambiguous / non-canonical input

**slug:** `discrete_where_the_brain_is_graded_in_parsing_and_role_assignment` - **opened:** 2026-08-27 by the strategy session
(the substrate-wide strategy follow-up the just-integrated `the_argument_parser_is_batch_where_the_brain_is_incremental`
explicitly handed off: "open the discrete->graded follow-up, unified with the graded role-assignment finding; VERIFIED
here it is NOT a big canonical-English win -- test on non-canonical / freer-word-order / ambiguous populations").
**status:** OPEN - **a cross-organ fidelity deviation spanning PARSING (attachment) and ROLE ASSIGNMENT (binding); the noise->0 limit of the SAME graded cue-based retrieval the retrieval convergence keeps surfacing.**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `1`. It is cross-cutting (two organs), brain-foundational
> (it unifies parsing + role binding under ONE graded mechanism -- Lewis-Vasishth cue-based retrieval, the audit's §1
> convergence), and solver-flagged. BUT it is honestly bounded: on CANONICAL English it is a small win (oracle ceiling
> +0.028, weak fit signal), so the whole point is to test it WHERE DISCRETE COMMITMENT ERRS -- ambiguous / non-canonical /
> freer-word-order input. Re-rank per the owner's direction (it competes with the conceptual-meaning channel + the
> consolidate-and-measure phase).

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do. If you have
> not identified the brain's mechanism and attempted to build it, you have not started the real work,
> whatever else you have measured.
>
> **🚀 YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> You are NOT boxed in -- not by this brief, not by the existing organs, not by the integration points you
> would tie into: if a MORE brain-foundational method conflicts with any of them, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful). Exploring
> the brain's true method is the work we most want from you; a bold, well-argued brain-faithful direction --
> even unfinished -- beats a tidy engineering result that never asked the question.
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several of your angles hit the
> SAME wall, that is strong evidence that NONE of them was the brain's mechanism -- the faithful method is
> probably DIFFERENT IN KIND, not another variation of what you already tried. A wall is a FIDELITY GAP TO
> BUILD ACROSS, never a ceiling. Hitting one is exactly the moment to LEAVE the family of methods you were
> sweeping and ask the biology again.
>
> **⛔ "CONVERGED" HAS A HIGH BAR, AND EXHAUSTING ENGINEERING VARIATIONS DOES NOT MEET IT.** Claim
> convergence ONLY when you have (a) identified how the brain actually performs this computation AND (b)
> replicated that operation as faithfully as you can and tested it, OR shown with a SPECIFIC reason why it
> cannot be replicated here. "I tried several combining / gating / scoring angles and they all plateaued at
> the same wall" is NOT converged -- it is tuning-limited, and it means the brain's mechanism is still
> UN-TRIED. That is a reason to explore harder, not to submit.
>
> **🔁 THE 30-MIN DEEPENING IS HOW YOU FORCE THIS -- IT IS NOT OPTIONAL BUSYWORK.** Run your own cron
> (`CronCreate "13,43 * * * *"`); each fire asks "how does the brain REALLY do this, one level deeper than
> my current mechanism?" -> implement -> test (can-fail, strongest real floor, info-free twin LOSING) ->
> iterate. Its whole purpose is to make you ask the brain question several more times than your own sense of
> "done" would. CANCEL it (`CronDelete`) and submit ONLY when the brain-mechanism bar above is met.
> Declining it because "my angles converged" is precisely the case it exists to catch.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully
> built.** A negative on a family of convenient engineering methods is not a negative on the capability; it
> is a report that you have not yet found how the brain does it.
>
> **📖 REFERENCE THE BRAIN-FOUNDATIONAL AUDIT, AND HELP KEEP IT TRUE.** Before you start, read the entry for the
> system you are touching in `notes/BRAIN_FOUNDATIONAL_AUDIT.md` -- it gives the brain structure, whether the
> brain's equation is PINNED or something we are INVENTING, our current fidelity, and the known deviation, so you
> inherit that instead of re-deriving it. If your work shows a verdict there is WRONG, STALE, or INCOMPLETE, or you
> find a NEW deviation, put a short **AUDIT UPDATE** note in your submission -- the strategy session folds it into
> the audit at integration. The audit is a living, shared map and you help maintain it.

## 1. THE PROBLEM IN PLAIN LANGUAGE

When our reader parses a sentence and works out who did what, it makes hard choices: THIS noun attaches to THAT verb,
THIS argument is the patient -- one answer, committed. The brain does not work that way. It holds several possibilities
in graded competition, weighted by how well each fits, and lets them settle -- which is why people slow down (not crash)
on ambiguous sentences, and why they make graceful, human-like errors on hard ones. Our discrete version is the
zero-noise LIMIT of that graded process: identical on easy sentences (where one option dominates), but WRONG in kind on
hard ones (where two options genuinely compete). This problem replaces the hard discrete decision with the brain's
graded competition -- and tests it exactly where discrete commitment errs.

## 2. WHY THIS ONE

- **It is one deviation across TWO organs.** The incremental parser (attachment) and the role assigner (binding) both
  make discrete commitments; both are the noise->0 limit of graded cue-based retrieval (Lewis-Vasishth). Fixing the
  mechanism fixes both.
- **It unifies with the substrate's deepest convergence.** Graded cue-based retrieval is the same operation the audit
  (§1) shows underlies binding, memory, coref, the fan effect, parsing and reversible role binding. This makes parsing +
  role assignment graded instances of it.
- **The signature it buys is human-faithful behaviour** (graded difficulty, graceful ambiguity errors) a discrete model
  structurally cannot produce -- and it feeds the N400 / surprisal difficulty signal.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED:** sentence processing is GRADED, PARALLEL, PROBABILISTIC CONSTRAINT SATISFACTION -- multiple interpretations
held in weighted competition, settling by mutual support/inhibition (MacDonald, Pearlmutter & Seidenberg 1994;
McClelland; normalized recurrence, Spivey-Knowlton 1996). Cue-based RETRIEVAL of the attachment site / filler is graded
by cue-match with similarity-based interference (Lewis & Vasishth 2005; McElree); the DISCRETE choice is the noise->0 /
argmax LIMIT of this. Graded competition predicts processing DIFFICULTY (settling time / surprisal) and human-like
error patterns on ambiguity; a discrete model cannot.

**OUR-INVENTION-UNDER-TEST (mark each; sweep don't adopt):** the graded activation/decay parameters; the collapse rule
(an activation-gap threshold vs a full settling dynamics); how the graded parser attachment and the graded role binding
SHARE the one retrieval mechanism; where the competition signal feeds (N400 / difficulty). COPY the OPERATION (graded
weighted competition, argmax as its limit); SWEEP the parameters. Do NOT adopt a specific noise level.

**Population note (THE key design choice the parser drill established):** on CANONICAL English the graded win is small
(oracle ceiling +0.028; word order saturates argument-ID). The graded mechanism must be TESTED where discrete commitment
genuinely ERRS: ambiguous attachment (PP-attachment, garden paths), non-canonical / reversible constructions, and (if
available) freer-word-order data. A negative on canonical English is EXPECTED and is not the test.

## 4. MEASURED vs INFERRED

**MEASURED (`the_argument_parser...` + `the_relcl_parser...`, integrated):** the incremental builder makes discrete eager
attachments; on canonical English an oracle-perfect object decision beats it by only +0.028 and the graded fit signal is
weak (patient-centroid AUC 0.59); a graded VALENCY fix UNDER-generates on canonical QA-SRL (all CI-separated BELOW the
generic builder). Reversible role binding is ALREADY framed (relcl SOLVED) as the noise->0 limit of graded cue-based
retrieval, which reproduces similarity-interference the discrete rule cannot. Revision (garden paths) is validated
+0.0852 but a no-op on edited prose.

**INFERRED / OPEN (this problem, decisive either way):**
- On AMBIGUOUS / non-canonical populations (PP-attachment, garden paths, reversibles, freer-word-order), does a graded
  competition parser + role binder beat the discrete eager builder + argmax assigner CI-separated, info-free twin
  (shuffled cue weights / random settling) LOSING?
- Does the graded model additionally produce a valid DIFFICULTY signal (settling time / competition margin) that
  correlates with an independent difficulty measure (garden-path vs control; the relcl route-conflict; human RT proxy)?

## 5. ALREADY TRIED / DO NOT RE-RUN

- Do NOT test on canonical English argument-ID as the headline -- the parser drill VERIFIED graded is a small win there
  (word order saturates); that is the negative-by-design population. Test on ambiguous/non-canonical.
- Do NOT re-run the discrete builder / role assigner -- they are integrated (the noise->0 limits). Compose the graded
  version on top.
- Do NOT reproduce a UD tree. Query `experiment_index.py query "graded"`, `query "normalized recurrence"`, `query
  "constraint satisfaction"`, `query "settling"`; read the incremental-parser + relcl + content-addressable SOLVEDs +
  `hdlab/content_addressable_retrieval.py` (the additive cue-based retrieval this generalizes) BEFORE building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Read the incremental builder + the converged role assigner + `hdlab/content_addressable_retrieval.py` (additive
  Lewis-Vasishth) + the relcl filler-gap resolver; confirm how the discrete decisions are made and where a graded
  competition replaces them.
- Confirm/assemble an AMBIGUOUS / non-canonical population (PP-attachment ambiguities, garden-path items, reversibles);
  recompute every floor (discrete builder/argmax; majority; info-free twin) on it.

## 7. THE BAR

Replace the discrete attachment / role decision with graded probabilistic competition (shared cue-based retrieval).
On an AMBIGUOUS / non-canonical population, floors recomputed on it:

- **The graded competition model must beat the DISCRETE eager builder + argmax assigner CI-separated over its UPPER
  bound, with an info-free twin (shuffled cue weights / random settling) LOSING CI-separated.** Report CI half-width +
  null p95. Ablate the graded competition vs the discrete limit; show the shared retrieval mechanism serves BOTH
  attachment and role binding. AND/OR: the competition margin is a valid graded DIFFICULTY signal (CI-separated
  correlation with an independent measure, shuffled twin at zero).
- **DECISIVE EITHER WAY:** graded beats discrete on ambiguous input -> the substrate's parsing + role assignment should
  be graded competition (propose the hdlab diff, one shared retrieval mechanism). A faithful graded model that does NOT
  beat the discrete limit even on ambiguous input -> a rigorous negative (discrete argmax is sufficient at this
  representation quality; the residual is p1 signal quality), localizing what graded competition actually buys.

## 8. FILES AND ENTRY POINTS

- The incremental-builder + role-assigner experiments (`exp_incremental_argstruct_builder_v1.py`,
  `exp_frontend_normalized_recurrence_v1.py`), `hdlab/content_addressable_retrieval.py` (additive cue-based retrieval --
  the graded mechanism to generalize), the relcl filler-gap resolver, `hdlab/predictive_reader.py` (the difficulty/
  surprisal interface).
- Prove in `experiments/` + `verification/`; propose the hdlab diff in `SOLVED.md` (strategy lands it, Q111). **Do NOT write `hdlab/`.**

## DO NOT QUOTE / DO NOT REDO

- Do NOT headline canonical-English argument-ID (graded is a small win there by design) -- test on ambiguous/non-canonical.
- Do NOT rebuild the discrete organs; compose the graded version and show argmax is its noise->0 limit.
- No number crosses populations/scorers -- recompute every floor on the ambiguous population.
