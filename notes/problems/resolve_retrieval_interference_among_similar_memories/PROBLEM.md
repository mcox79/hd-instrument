---
priority:
review: EXCELLENT
review_text: "Integrated SOLVED/EXCELLENT 2026-08-26 (owner-DONE). Re-verified scaffold-free first-hand (test_context_interference_resolution.py, 6 assertions PASS incl. the boundary collapse + leak guard). The missing organ for similar-competitor interference is CONTEXT REINSTATEMENT at retrieval -- the SAME additive Lewis-Vasishth rule given one more feature (encoding context, TCM). CTX_ADD 0.928 vs the context-free additive baseline 0.400 at 8 competitors, CI-separated at every K; info-free twins lose; genuinely LEAK-SAFE cue combination (context alone 0.306 << oracle 0.994); residual fan effect exhibited; and it correctly COLLAPSES (0.494) when context is non-separable. Brain-faithful throughout (TCM Howard-Kahana context, Teyler-Rudy indexing, ACT-R noisy read). Notably the solver caught + demoted its OWN soft-oracle (diagnosticity-weighting peeks). SYNTHETIC construction proof on the real organ -- the live capability (is the substrate's REAL context separable across similar memories?) is GATED on the p1 wire-and-measure. No new hdlab organ (AdditiveCueRetrieval is already feature-agnostic -- context is just another feature); the live wiring is folded into p1's retrieval-first composition."
---

# PROBLEM: our memory is fooled by SIMILAR competing memories (the fan effect) -- the brain resolves which one to retrieve using CONTEXT and encoding-time separation, and our feature-only additive cue cannot

**slug:** `resolve_retrieval_interference_among_similar_memories` - **opened:** 2026-08-26 by the strategy session
(the OPEN PROBLEM the integrated `content_addressable_retrieval` result explicitly flagged: *"the honest open problem
underneath the brief is not 'separate the store', it is 'resolve similarity interference among competing memories' ...
open it as its own problem, not a switch here."*)
**status:** OPEN - **first-hand + measured in the content_addressable SOLVED (findings 7-9); a solver-surfaced next gap**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `2` (below the p1 wire-and-measure phase pivot). This
> is the real residual under the just-integrated content-addressable retrieval: an ADDITIVE feature cue recovers a
> partial cue gracefully, but when a competitor memory is genuinely SIMILAR to the target it confidently retrieves the
> WRONG one. That is the fan effect -- real human behaviour a faithful model must EXHIBIT -- but the brain still resolves
> it far better than our feature-only rule, using information our cue does not carry: CONTEXT. Foundational to the whole
> memory/coreference/comprehension line (E2/E3).

> **🔗 COUPLED TO p1 (`wire_the_validated_organs...`, strategy 2026-08-26).** This is the SAME retrieval architecture --
> the audit's #1 live deviation ("we query the wrong memory") -- seen from the INTERFERENCE side. p1's first end-to-end
> composition is the content-addressable retrieval build over the live register; THIS problem is what that build must
> ALSO get right (exhibit the fan effect while resolving it by CONTEXT reinstatement + encoding-time separation, not
> engineer it away). Coordinate: a shared retrieval build serves both, and the CONTEXT signal you add here is the same
> discourse/situation-model state p1 threads through the reader. Do the mechanism here; prove it end-to-end in p1.

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

Our reader can now look a memory up by a rough description (the just-integrated content-addressable retrieval). But when
two stored memories are genuinely SIMILAR -- the same kind of thing, described in similar words -- a vague cue matches
BOTH, and our memory confidently returns the wrong one. People have this weakness too (it is called the "fan effect,"
and it is why more overlapping facts make each one slower and more error-prone to recall) -- so a faithful model must
still SHOW some of it. But the brain resolves it far better than our current rule, because it retrieves using something
our cue throws away: **CONTEXT** -- the situation the memory was formed in ("the bank near the river," not "the bank").
The brain also does part of the work at STORAGE time, pulling similar memories apart so they interfere less later. This
problem asks: build the brain's context-based interference resolution, so the reader recovers the RIGHT one of several
similar memories -- while still exhibiting the residual, brain-correct fan effect.

## 2. WHY THIS ONE

- **The integrated content-addressable result named it as the real open problem**, explicitly, and left it unbuilt on
  purpose ("open it as its own problem, not a switch here").
- **It is foundational to the whole memory / coreference / comprehension line (E2/E3).** Resolving which of several
  competing referents/memories a cue picks is the core of coreference-under-ambiguity and situation-model retrieval --
  the standing open case the audit flags for coref.
- **The naive fix is already refuted**, which sharpens it: DG pattern separation applied at RETRIEVAL did not help
  (content-addressable finding 6). The brain separates at ENCODING and disambiguates at retrieval with CONTEXT -- a
  different-in-kind mechanism from what was tried.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED:** cue-based retrieval interference is resolved by (a) **CONTEXT reinstatement** -- the retrieval cue includes
the encoding CONTEXT, which biases activation toward the trace formed in that context (Lewis & Vasishth 2005 cue-based
retrieval already sums a CONTEXT feature; Howard & Kahana temporal-context model; hippocampal context binding), and (b)
**pattern separation at ENCODING** -- the dentate gyrus orthogonalises similar traces as they are stored, so they
interfere less at retrieval (Yassa & Stark; the DG's actual job is at encoding, not at read). The **residual fan effect**
(Anderson; ACT-R: activation spreads thinner as more items share a cue, so retrieval slows/errs) is real and PINNED --
a faithful model EXHIBITS a graded cost with competitor count; it does not eliminate it.
**OUR-INVENTION-UNDER-TEST:** how CONTEXT enters the additive activation (an additional weighted feature? a multiplicative
context gate on the per-item activation?), and the encoding-time separation strength. COPY the COMPUTATION (context as a
disambiguating retrieval feature + encoding-time separation); SWEEP the PARAMETER (context weight, separation level,
competitor similarity).

**Corpus-age note:** if you use real text cues, the reading corpus (McGuffey) is ~200 years old -- hold corpus era fixed
across arms so the mechanism, not the corpus, is what varies.

## 4. MEASURED vs INFERRED

**MEASURED (content_addressable SOLVED, re-verified; findings 7-9):** with a SAME-CLUSTER (genuinely similar) competitor
cue, the additive feature-only rule is fooled -- at 1 similar feature COMPOSITE 0.863 = ADDITIVE 0.863; at 2 features the
additive advantage reverses; the ACT-R fan penalty HURTS in the graded regime. DG separation applied at retrieval did NOT
help. So a feature-only cue cannot resolve similar competitors, and a retrieval-time separator does not fix it.
**INFERRED (the deliverable):** whether adding **CONTEXT** to the retrieval (and/or **encoding-time** separation) resolves
the RIGHT competitor CI-separated over the context-free additive baseline, while still exhibiting the graded fan-effect
cost -- i.e. resolves interference the brain's way without pretending the fan effect is gone.

## 5. ALREADY TRIED (do not re-run)

- Content-addressable ADDITIVE retrieval (the base) is DONE + landed (`hdlab/content_addressable_retrieval.py`); build ON
  it, do not re-derive it. The additive rule's graceful degradation under a PARTIAL cue is settled.
- DG pattern separation at RETRIEVAL -- rigorous NEGATIVE (no help). If you use separation, it must be at ENCODING.
- The ACT-R fan PENALTY as a retrieval knob -- regime-specific (helped near-orthogonal, hurt graded). Not the lever.
- The multiplicative composite-key match -- refuted (orthogonalises). Additive is the base.
- Query `tools/experiment_index.py query "context"`, `query "coreference"`, `query "interference"`, `query "fan"`;
  read `content_addressable_retrieval_over_a_separated_store/SOLVED.md` findings 7-9 + the audit E2/E3 entries first.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Reproduce the interference failure on the landed organ: build same-cluster competitors and confirm a feature-only
  additive cue picks the wrong one (the base rate to beat). Recompute the strongest floor on that population.
- Confirm what CONTEXT is available in the substrate to reinstate (the situation-model event context, the sentence/scene
  context vector, the reading-loop context) -- and that using it does not just leak the answer (control for that).
- Positive control that the DV can detect resolution at all (an oracle context that uniquely identifies the target ->
  near-ceiling), and that a scrambled/random context is the info-free twin.

## 7. THE BAR

On a retrieval task with genuinely SIMILAR competitors (same-cluster / near-duplicate memories), floor recomputed on its
population: **context-based interference resolution (add the encoding CONTEXT to the additive activation, and/or separate
at ENCODING) must recover the correct competitor CI-separated over the CONTEXT-FREE additive baseline's UPPER bound, with
the info-free twin (SHUFFLED / RANDOM context) LOSING CI-separated**, CI half-width + null p95 reported. AND it must still
EXHIBIT the residual fan effect (recovery/latency degrades gracefully as competitor count rises -- report the curve; a
model that shows ZERO fan cost has leaked the answer, not resolved interference). Sweep context weight / separation level
/ competitor similarity.
**DECISIVE EITHER WAY:** a WIN -> context reinstatement is the missing organ for interference resolution; strategy wires
it into the retrieval/coref path (default-off). A rigorous NEGATIVE (context does NOT resolve it at our representation ->
the interference is irreducible here, and WHY -- e.g. the context codes are themselves too similar, or the substrate has
no separable context to reinstate) is a full PASS and re-points the memory line to supplying separable context.

## 8. FILES AND ENTRY POINTS

- `hdlab/content_addressable_retrieval.py` (the additive base to build on); `hdlab/dg_pattern_separation.py` (separation,
  but at ENCODING); the situation-model context (`hdlab/situation_model_accumulate.py` / `situation_model_multibank.py`,
  `hdlab/reading_grounding_loop.py`'s context vectors); the coref organs (`hdlab/coref.py`, `coreference_resolver.py`) for
  the real competing-referent case.
- `notes/BRAIN_FOUNDATIONAL_AUDIT.md` E2/E3 (cue-based retrieval, coref) + the content_addressable §2b entry. Report any
  correction as an **AUDIT UPDATE**.
- Prove in `experiments/` + a scaffold-free witness in `verification/`; propose the hdlab diff in `SOLVED.md` (strategy
  lands it, Q111). Do NOT write `hdlab/`.

## DO NOT QUOTE / DO NOT REDO

- Do NOT try to ELIMINATE the fan effect -- a faithful model exhibits a graded cost; the goal is to resolve the RIGHT
  competitor when context allows, not to be magically immune.
- Do NOT re-apply DG separation at RETRIEVAL (refuted) or the ACT-R fan penalty as a graded-regime knob (hurts).
- Do NOT let CONTEXT leak the target identity -- control it (a context that uniquely names the target is an oracle, not a
  mechanism); the win must survive a context that only BIASES, not identifies.
- No number crosses the synthetic competitor instrument and a real coref/text task -- recompute the floor on each.

---

## SOLVER REVIEW (strategy session, 2026-08-26 — INTEGRATED, owner-DONE)

**Grade EXCELLENT. Verdict SOLVED** (bar met on the interference instrument; the live-text capability is a separate
gate, shared with every retrieval organ). Re-verified scaffold-free first-hand — `test_context_interference_resolution.py`
6 assertions PASS, reproduced: CONTENT_ONLY bit-identical to the live `AdditiveCueRetrieval` (0 mismatches); CTX_ADD
0.928 vs 0.400 at K=8, CI-separated at every K; info-free twins lose; leak guard (CTX_ALONE 0.306 ≪ oracle 0.994);
residual fan effect present; boundary collapse to 0.494 when context is non-separable.

**Why EXCELLENT (the work quality):** it is brain-faithful end-to-end (TCM Howard-Kahana drifting context, Teyler-Rudy
context-indexing, Lewis-Vasishth additive cue, ACT-R noisy competitive read — the fan cost EMERGES from the read, not a
penalty); it reframes the problem correctly ("which VARIABLE separates these memories" — context, not "match content
better"); the win is genuine CUE COMBINATION, not a leaked oracle (context alone can't identify; the twins that TIE
content prove the signal is real); it characterises the decisive NEGATIVE boundary (non-separable context → collapse);
and — the model-honesty move — **it caught its OWN soft-oracle** (a diagnosticity-weighted arm beat the exact-context
oracle → impossible unless peeking → demoted to a labelled ceiling). The deep drill (owner-directed "is the proximity
machinery faithful?") tested the REAL DG organ (neutral on content → confirms the faithful separator is
context-indexing, not sparsification), showed partial-fragment reinstatement suffices, and found the fan cost in latency.

**What it establishes:** the additive cue-retrieval rule is COMPLETE only WITH a context cue; without it,
similar-competitor interference is irreducible. Context enters ADDITIVELY (one more Lewis-Vasishth feature), not as a gate.

**Honest limit (gated, not a flaw):** SYNTHETIC — FHRR codes + a synthetic TCM context engineered to be separable at the
headline operating point. Whether the substrate's REAL context (bag-of-words, `sign()`-quantized) is separable across
genuinely similar memories is OPEN; the boundary population shows the mechanism collapses when it is not. The faithful
operating point is the CMR content-correlated regime (win weaker but survives, 0.95→0.77) with the GRADED context.

**No new hdlab organ** (Q111): `AdditiveCueRetrieval` is already feature-agnostic, so context reinstatement is a USAGE
(add a `context` feature to the stored items + cue), not a new organ. The live wiring — store the situation-model/
reading-loop GRADED context as a per-item feature — is a COMPOSITION folded into the p1 retrieval-first wire-and-measure,
gated on a live coref/situation-model measurement. AUDIT UPDATEs folded into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b.
