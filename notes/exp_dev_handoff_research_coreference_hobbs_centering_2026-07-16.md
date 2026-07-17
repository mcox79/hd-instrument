# exp_dev hand-off — research: coreference resolver (Hobbs' algorithm / Centering Theory), glass-box, no LLM

**Filed-by:** research (Sonnet lit-scan x3 + Sonnet synthesis), 2026-07-16.
**Trigger:** `notes/research_coreference_hobbs_centering_resolver_2026-07-16.md` — full findings, cheap decisive test, falsifiable predictions (A-C) with HARD-PASS/HARD-FAIL bars, and the register-specific honesty note all live there. This file is the pointer-only hand-off; do not re-derive the reasoning here, read the cited note.
**Pause state:** `data/orchestrator_paused.flag` absent at filing time (NOT PAUSED) — re-check at pickup time before shipping anything to remote/GPU queues.

Per [[feedback-no-experiment-design-in-prompts]]: no inline pre-reg, thresholds, or cell code below — the cited research note's sections (b)/(c) have the falsifiable predictions and HARD-PASS/HARD-FAIL bars; the cell-author owns translating those into concrete pre-reg + code.

---

## Anchor candidates (rank-ordered)

1. **[Primary, blocking prerequisite, do FIRST] Corpus-construction: rebuild the coreference fixture rows as genuine local-antecedent discourse pairs, separate from a deliberately-ambiguous fixture set.**
   - Anchor pointer: research note section (b), step 3, and the "Cross-thread synthesis" bullet on the existing `PROSE_CORPUS` coreference rows being mis-specified.
   - Substrate-product reading: the two existing coreference rows in `exp_read_grow_foundation_realprose_glassbox_ie_v2.py`'s `PROSE_CORPUS` (`"It eats the worm."` / `"They chase the mouse."`) are isolated single sentences with their gold antecedent several rows and multiple intervening animal-mentions away in corpus order — not a valid test of local-antecedent resolution under any definition in the literature reviewed. Testing a resolver against these rows as-is would not be decisive. This is a data-construction step, not a resolver-design step, and gates everything below.
   - Tier hint: near-zero risk, cheap — this is writing new test rows (antecedent-sentence + pronoun-sentence pairs, single unambiguous candidate) plus a small set of genuinely-tied discourse fixtures (2+ agreement-compatible candidates, correct-abstain target).
   - Why now: without this, anchor 2 cannot be tested at all — building the resolver against the current mis-specified rows produces an uninformative result either way.

2. **[Secondary, the blocking architectural prerequisite] Discourse-memory shim: a rolling `(sentence_index, lemma, grammatical_role, number)` list (window 2-3 sentences) threaded through the read-loop.**
   - Anchor pointer: research note section (e) point 1; the HEADLINE's core finding ("the gap is not 'we lack an algorithm,' it is 'the pipeline has nowhere to run one'").
   - Substrate-product reading: `ie_extract(sentence)` is currently a pure, stateless, single-sentence function. Every mechanism in the literature (Hobbs' backward search through prior sentences, Centering's Cb defined relative to Uᵢ₋₁, cue-based retrieval's memory-chunk store) is a discourse-level mechanism and cannot run without this. The role-tagging logic this needs already exists in `ie_extract`; this only persists it across calls.
   - Tier hint: not itself a falsifiable prediction (it's infrastructure), but a hard prerequisite for anchors 3-5. Low engineering risk, small diff.
   - Why now: nothing below this line is buildable without it.

3. **[Tertiary, the resolver itself — Prediction A] Minimal Hobbs/Centering-style resolver: rank discourse memory by recency-then-subject-role, filter by number agreement, bind on exactly one survivor, ABSTAIN on zero or 2+.**
   - Anchor pointer: research note section (c) Prediction A, section (e) point 2.
   - Substrate-product reading: converts the existing `COREF_UNRESOLVED` abstain branch into a resolution attempt for the local-antecedent case. Under 100 lines estimated, no new dependency, fully deterministic, fully provenance-traceable (bound triple carries both current-sentence and antecedent-sentence pointers as its rule-firing record).
   - Tier hint: capped P=0.45 per note (deflated below what the register's grammatical simplicity alone would suggest, because this closed animal-noun lexicon has NO grammatical-gender cue — number agreement is the only hard categorical filter available, a register-specific weakness not covered by any literature source found — this note's own inference, flagged explicitly).
   - Why now: this is the requested deliverable of this drill; ship it only after anchors 1-2 are in place, per the sequencing above.

4. **[Fourth, optional tie-breaker — Prediction B] Wire the existing ingest-gate type-check schema as a SECOND-STAGE tie-breaker, invoked only when number-agreement alone leaves 2+ survivors.**
   - Anchor pointer: research note section (c) Prediction B, section (e) point 5.
   - Substrate-product reading: a direct structural analogy to Hobbs' own selectional-restriction augmentation (which took HIS accuracy 88.3% -> 91.7%) — but this substrate's schema may be too permissive in a small closed vocabulary to break many ties in practice; value is uncertain and should be measured, not assumed.
   - Tier hint: capped P=0.35 per note. Genuinely optional — build only if anchor 3's fixture testing shows ties surviving number-agreement alone are common enough to matter.
   - Why now: cheap to add on top of anchor 3 (reuses existing gate logic) if the tie rate warrants it; skip if anchor 3's own numbers show ties are rare.

5. **[Guardrail, not optional — Prediction C] Deliberately-ambiguous fixture test: confirm the resolver correctly ABSTAINS (does not guess) on genuinely-tied cases.**
   - Anchor pointer: research note section (c) Prediction C.
   - Substrate-product reading: this is the single most important guardrail in the whole roadmap, more load-bearing than anchors 3-4's own HARD-PASS bars — a wrong guess converts a correct "no fact" into an incorrect "wrong fact" bound to the wrong entity, a strictly worse outcome than the status quo and a direct hit against the substrate's zero-hallucination invariant. HARD-FAIL threshold (resolver guesses wrong on >=30% of genuinely-tied cases) should gate ship/no-ship more strictly than anchors 3 or 4 individually passing.
   - Tier hint: P=0.55 per note (closer to a literature-confirmed claim than a novel synthesis — every lane converges on world-knowledge/genuine-tie cases as an irreducible residual).
   - Why now: must be tested alongside anchor 3, not deferred — do not ship anchor 3 without also running this guardrail test on the same pass.

---

## Context pointers (file paths, not summaries — read these, don't re-derive)

- `notes/research_coreference_hobbs_centering_resolver_2026-07-16.md` — this drill's full findings, cheap decisive test, falsifiable predictions A-C, cross-thread synthesis, register-specific honesty note, and full citation list.
- `experiments/exp_read_grow_foundation_realprose_glassbox_ie_v2.py` — the live parser this drill informs. Coreference-relevant code: `ie_extract` lines ~256-262 (`COREF_UNRESOLVED` abstain branch — the pronoun-subject-no-antecedent detection this drill extends, not replaces); `PROSE_CORPUS` lines ~546-550 (the two existing, mis-specified coreference test rows — anchor 1 rebuilds these); `PRONS` set line ~141 (`it`/`they`/`he`/`she`/etc. already tag-recognized; the corpus currently only exercises `it`/`they` — anchor 3 should scope to exactly that, per research note section (e) point 7, not the full pronoun set).
- `notes/research_glass_box_reading_robust_parsing_ceiling_2026-07-16.md` — the parent drill; its Prediction D (P=0.42) first flagged coreference as a load-bearing, non-shrinking gap and recommended budgeting a Hobbs/centering pass by curriculum Rung 3+. This hand-off is that recommendation's concrete follow-up.
- USER directive (memory, referenced descriptively in the dispatching prompt): glass-box-the-reading-no-LLM — this hand-off's anchors 2-3 (discourse-memory shim + deterministic Hobbs/Centering resolver) are a direct, no-neural-component operationalization; no anchor here touches the narrow-neural-syntax-parser carve-out from the parent drill (that carve-out remains scoped to curriculum Rung 5+ structural parsing only, per the parent note).

---

## Contract section

- Cell-author owns: exact discourse-memory window size, exact rebuilt fixture-row wording, exact ranking-tie-break implementation, exact schema-type-check wiring (anchor 4, if pursued), smoke gate, dispatch.
- Anchor 1 (corpus rebuild) MUST land before anchor 3 (resolver) is tested — testing against the current mis-specified rows is not decisive in either direction, per the research note's own cheap-decisive-test framing.
- Anchor 5 (ambiguous-fixture guardrail test) MUST run in the SAME pass as anchor 3, not deferred — do not report anchor 3's HARD-PASS without also reporting anchor 5's result.
- All three predictions (A-C) carry deflated P estimates (0.35-0.55) per lit-scan calibration penalty — treat as genuinely uncertain, not near-certain, going into pre-reg. Prediction A in particular is deflated BELOW what the register's grammatical simplicity would suggest, because of the register-specific agreement-poverty finding (section (e) point 4 / the closing "Register-specific finding" section of the research note) — do not silently round this back up at pre-reg time.

## Autonomy declaration

Research does not prescribe exact code, exact discourse-window size, exact ranking-tie-break logic, or exact fixture wording beyond naming Hobbs'-algorithm/Centering-Theory (recency + subject-role ranking, number-agreement filter) as the literature-precedented glass-box mechanism. Cell-author has full autonomy over implementation detail, exact rule specification, and smoke-scale parameters, subject to the falsifiable predictions and HARD-PASS/HARD-FAIL bars pre-registered in the cited research note, and subject to the anchor-1-before-anchor-3 and anchor-3-with-anchor-5 sequencing constraints above.
