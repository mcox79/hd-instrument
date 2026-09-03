# exp_dev hand-off — research: is-a inheritance wall (copular binding schema)

**Filed-by:** research (4x Sonnet lit-scan + Opus/Sonnet synthesis + 3 direct verification searches), 2026-09-02.
**Trigger:** `notes/problems/the_reader_has_no_copular_is_a_binding_schema/research_isa_inheritance_wall_2026-09-02.md` — full findings, per-question PINNED/OPEN verdicts, falsifiable predictions, and cited mechanism recipe live there. This file is the pointer-only hand-off; do not re-derive the reasoning here, read the cited note.
**Pause state:** `data/orchestrator_paused.flag` — check at pickup time before shipping anything to remote/GPU queues; this cell is CPU-only pattern-matching + an existing eval harness re-run, no GPU needed regardless.

Per [[feedback-no-experiment-design-in-prompts]]: no inline pre-reg, thresholds, or cell code below — the cited research note's "Cheap decisive test" and "Falsifiable predictions" sections have the HARD-PASS/HARD-FAIL bars; the cell-author owns translating those into concrete pre-reg + code.

---

## Anchor candidates (rank-ordered)

1. **[Primary] Hearst-pattern harvest over the reading corpus, unioned with existing symbolic IsA coverage, re-scored on the existing freq-matched 2AFC-vs-WordNet-gold harness.**
   - Anchor pointer: research note "Cheap decisive test" + "HOW TO REPLICATE" Tier 1.
   - Substrate-product reading: this is the first test of whether the reader's is-a facts can come from an actual textual assertion (a sentence that says "X and other Y" / "Y such as X") rather than a guessed similarity score — directly operationalizes the "extraction beats inference" verdict as a running artifact, not just a design note. If it clears, it closes the wall named in the trigger problem folder outright for the covered fraction of cases.
   - Concrete spec (from the research note, not prescriptive beyond this): implement Hearst's canonical lexico-syntactic patterns ("NP_y such as NP_x," "NP_x and/or other NP_y," "NP_y including NP_x," "NP_y, especially NP_x" — Hearst 1992) as regex/dependency-parse matchers over the existing reading corpus; union extracted (hyponym, hypernym) edges with whatever symbolic IsA resource is already wired (the one currently giving ~36% coverage per the trigger's own numbers). Measure (a) coverage gain beyond that 36%, hand-precision-checked on a ~50–100 edge sample; (b) accuracy of "Tier-1 lookup if present, else WeedsPrec/invCL fallback" re-scored on the SAME freq-matched 2AFC population the trigger's 0.676/0.692/0.694/0.477 numbers came from.
   - **HARD-PASS (from research note):** coverage gain ≥10 points beyond the existing ~36% AND the combined lookup+fallback system beats the flat WeedsPrec-only 0.692 ceiling with a CI-separated margin, same population.
   - **HARD-FAIL (from research note):** coverage gain <3 points (corpus too small/narrow-genre for canonical Hearst constructions to occur) OR the combined system fails to CI-separate from 0.692 (extraction too noisy, or newly-covered pairs were already handled fine by the fallback so coverage doesn't translate to accuracy).
   - **MIDDLE_BAND:** coverage gain real (3–10 points) but accuracy margin doesn't CI-separate — diagnose extraction-precision (check the hand-precision sample) vs test-power (too few newly-covered pairs in eval set) before concluding.
   - Tier hint: this is NOT novel-synthesis at the extraction-mechanism level — Hearst-pattern extraction is 30+ years precedented and re-confirmed as recently as 2018 (Roller, Kiela & Nickel) as beating distributional methods on every benchmark tried; the only untested part is corpus-specific coverage/precision on THIS project's own reading corpus, which is cheap to measure directly rather than estimate. P≈0.55-0.60 per research note calibration (higher confidence than typical novel-synthesis cap, because the mechanism itself is not novel).
   - Why now: closes the wall named in the trigger problem folder with the cheapest possible test — no training, no GPU, reuses the existing eval harness, and is directly decisive on the research note's central claim (extraction beats similarity, categorically).

2. **[Secondary, gated on anchor 1 clearing MIDDLE_BAND or better] Read-time Tier-1/Tier-2 pipeline: copula-as-direct-edge insertion + tree-traversal property inheritance with cancellation.**
   - Anchor pointer: research note "HOW TO REPLICATE" Tier 2.
   - Substrate-product reading: turns the static extracted/unioned IsA tree from anchor 1 into a live reading-time mechanism — when the reader parses a genuine copular is-a predication ("X is a doctor"), insert X as a new node with a direct edge to the resolved tree node, then read out inherited properties via ancestor traversal (Collins & Loftus-style spreading activation with cancellation for exceptions), falling back to the capped WeedsPrec/invCL soft-placement only when the target concept is absent from the tree.
   - Tier hint: risk concentrated in two places — (a) correctly resolving which existing tree node a copular predicate's head noun maps to (a lemmatization/lookup problem, same shape as the already-solved `reader_meaning_channel` lemmatization fix — check that fix's lookup-normalization code for reuse before writing a new one); (b) keeping the fallback-vs-extracted distinction visible downstream (never let a soft-placed edge look identical to an extracted one to a consumer of the tree). Defer until anchor 1's verdict is in — building the read-time insertion machinery on top of an unmeasured coverage/accuracy foundation is premature.
   - Why now: not yet — sequenced explicitly behind anchor 1, per the research note's own two-tier ordering (FOUNDATION before READ-TIME).

3. **[Tertiary, explicitly refuted — do not build] Feature-set-intersection over property features (McRae-norm-style or ConceptNet-HasProperty-style) as the is-a decider.**
   - Anchor pointer: research note Q3.
   - This is listed only to say: do not re-propose it. The trigger's own empirical result (ConceptNet semantic-property feature-intersection at chance, 0.509) plus a literature gap (no supporting study found across the lit-scan) closes this route for edge-detection specifically. It may still have a role in scoring which properties transfer once an edge already exists via anchor 2's traversal — a distinct, smaller problem — but not for finding the is-a edge itself.

---

## Context pointers (file paths, not summaries — read these, don't re-derive)

- `notes/problems/the_reader_has_no_copular_is_a_binding_schema/research_isa_inheritance_wall_2026-09-02.md` — this drill's full findings, per-question PINNED/OPEN verdicts, cited mechanism recipe, cheap decisive test, falsifiable predictions, citation list with verification status.
- `notes/problems/reader_meaning_channel/PROBLEM.md` — the "contribute, do not decide" cap-below-link-threshold pattern (`GROUNDED_CAP` below `SIMILARITY_LINK_THRESHOLD`) that anchor 2's WeedsPrec/invCL fallback should replicate; also the already-solved lemmatization/lookup-normalization fix (60.35%→73.50% token coverage, "zero data cost") that anchor 2's tree-node-resolution step should reuse rather than re-derive.
- `notes/problems/teach_the_self_built_space_instead_of_concatenating_it/SOLVED.md` — "weighting sources in general — refuted across four instruments... no monotone blend has headroom" — the reason this hand-off does NOT propose fusing WeedsPrec+invCL+SLQS into a cleverer combined score; the lever that has worked repeatedly in this project's own history is coverage/extraction, not combination-cleverness, which is exactly what anchor 1 targets.
- The existing freq-matched 2AFC-vs-WordNet-gold eval harness that produced the trigger's 0.676/0.692/0.694/0.477 numbers — **not independently located this cycle** (the numbers were supplied in the dispatching prompt, not re-derived from disk); the cell-author must locate this harness first and confirm it can be re-run with an added "Tier-1 lookup" arm before treating anchor 1's spec above as final.
- The existing symbolic IsA resource giving ~36% coverage (ConceptNet and/or WordNet, per the trigger's own framing) — **not independently located this cycle**; locate via the project's registry/organ map rather than assuming a specific file path.

---

## Contract section

- Cell-author owns: locating the existing eval harness and symbolic-IsA-coverage code (both flagged above as not independently located this cycle), concrete pre-reg (exact Hearst pattern set, exact corpus scope, exact hand-precision sample size and selection method), smoke gate, dispatch.
- Must implement the coverage measurement AND the accuracy re-measurement as two separate, separately-reported numbers — a coverage gain with no accuracy re-measurement is not a result (per the research note's own MIDDLE_BAND diagnostic split).
- Must hand-precision-check the harvested edges (~50-100 sample) before trusting coverage-gain numbers — Hearst patterns are high-precision but not perfect, and an unverified coverage number invites the same "arithmetic, not capability" trap this project has hit before with coverage claims (see `reader_meaning_channel` PROBLEM.md §3 for the prior instance of this exact trap).
- HARD-PASS/HARD-FAIL/MIDDLE_BAND bars are pre-registered in the research note's "Falsifiable predictions" section — do not loosen them at pre-reg time without flagging the deviation explicitly in the pre-reg file.
- Do not build anchor 2 before anchor 1's verdict lands. Do not re-propose anchor 3.

## Autonomy declaration

Research does not prescribe exact Hearst pattern regexes, exact corpus scope, exact precision-sample size, or exact dependency-parse tooling beyond naming the canonical Hearst 1992 pattern set and the Snow/Jurafsky/Ng 2004 dependency-path generalization as literature-precedented options. Cell-author has full autonomy over implementation detail (pattern-matching vs dependency-path extraction, exact corpus subset, exact sample size for precision-checking), subject to the falsifiable predictions and HARD-PASS/HARD-FAIL/MIDDLE_BAND bars pre-registered in the cited research note, and subject to locating (not assuming) the existing eval harness and symbolic-coverage baseline before building anything new on top of them.
