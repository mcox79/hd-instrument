# exp_dev hand-off -- research: language/math substrate overlap 2x

Filed-by: research sub-agent
Date: 2026-06-11
Trigger: notes/research_drill_language_math_substrate_overlap_2x_2026-06-11.md
Urgency: MEDIUM -- LVH-280 (POS tagger) is the blocking item; the remaining 5 anchors are capability-expansion experiments.

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: pos_tagger_ptb_confirm_v2 -- BLOCKING LVH-280 RESOLUTION

Anchor pointer: Research note Section 3 Exp-6; cap_map LVH-280 annotation (cycle 229 v563)
Substrate-product reading: Re-run POS tagger with correct PTB corpus path. The exp_dev commit e1c4f831 claims tag_acc=0.906 (HARD_PASS Tier A language claim), but local metrics show corpus_load_failed. This is a corpus-path issue, not an architecture issue. Confirming or refuting the 0.906 figure is the gate for all NL-parsing architecture claims including the language/math unified codebook claim.
Tier hint: CPU local, ~15 min. CHEAPEST. Must run first -- gates all language-domain claims.
Why-now: LVH-280 is live. No cap_map credit for POS tagger until confirmed. The research note's language/math unified architecture analysis depends on this being real.

Pre-reg bands:
  HARD-PASS: tag_acc >= 0.85 (LVH-280 resolved; PP row for POS tagger unlocked)
  MIDDLE-BAND: tag_acc 0.70-0.85 (partial; context-dependent tags fail; architecture valid but needs improvement)
  HARD-FAIL: tag_acc < 0.70 (architecture does not generalize to real-corpus distribution; retract NL-parsing claims)

### Anchor 2: lang_math_coexist_v1 -- Shared W interference test

Anchor pointer: Research note Section 3 Exp-1 (LANG-MATH-COEXIST)
Substrate-product reading: Store WUG morphological rules AND algebra simplification rules in the SAME substrate W at N=4096. Run both WUG task and algebra simplification on the joint W. This is the single most decisive test for whether substrate is a unified language/math system or requires separate role-substrates (PP-356 design). If HARD-PASS: unified codebook architecture is valid and product can claim "one substrate for language and math." If HARD-FAIL: route to separate codebook regions (PP-356 pattern).
Tier hint: CPU local, ~15 min. Joint task on single W. Run second, after Anchor 1.
Why-now: Research note identifies this as cheapest decisive test for the shared-W hypothesis (Q1). Directly gates the product positioning claim.

Pre-reg bands:
  HARD-PASS: WUG accuracy >= 0.99 AND algebra accuracy >= 0.99 in joint W (vs single-domain baselines PP-342 and PP-332)
  MIDDLE-BAND: both accuracies >= 0.90 (minor interference; functional)
  HARD-FAIL: either accuracy drops > 5pp vs single-domain baseline (interference; separate role-substrates required)

### Anchor 3: wug_math_productivity_v1 -- Domain-generality of productivity mechanism

Anchor pointer: Research note Section 3 Exp-5 (WUG-MATH)
Substrate-product reading: Apply the WUG morphological productivity protocol (PP-342, 3-shot rule induction) to novel mathematical operators. Define 3-5 novel operators via 3 examples, then test application to new arguments. If HARD-PASS: the rule-induction mechanism is domain-general (not language-specific), which substantially strengthens the "one substrate for language and math" architecture claim. If HARD-FAIL: WUG productivity is language-specific; separate mechanisms required for math operator induction.
Tier hint: CPU local, ~20 min. Requires defining novel operators and test cases.
Why-now: PP-342 WUG result at 1.000 is one of the strongest language capabilities. Testing domain-generality is the natural next step per [[feedback-dont-dismiss-adjacent-methods]].

Pre-reg bands:
  HARD-PASS: novel operator rule application accuracy >= 0.90 on 20 argument pairs per operator, 3 operators minimum
  MIDDLE-BAND: 0.60-0.90 (simple operators work; complex compositions fail)
  HARD-FAIL: < 0.60 (WUG mechanism does not transfer; retract domain-generality claim)

### Anchor 4: word_problem_pipeline_v1 -- NL to math end-to-end

Anchor pointer: Research note Section 3 Exp-3 (WORD-PROBLEM-PIPELINE)
Substrate-product reading: Build 50 one-step arithmetic word problems using only additive/subtractive quantity constructions. Store quantity-language constructions (has-N, gives-N, takes-N) as binding patterns mapping English patterns to math operator structures. Test end-to-end: English sentence -> substrate extracts math structure -> substrate applies arithmetic rule -> output. If HARD-PASS: NL-to-math pipeline is viable substrate-only (no LLM for extraction stage). Product value: enterprise workflow automation for business rules in natural language.
Tier hint: CPU local, ~1 hr including construction inventory build. Medium effort.
Why-now: P_deflated = 0.28 is low but the cost is also low (~$0, ~1 hr). The upside (NL-to-math pipeline without LLM) is a significant product differentiator. Worth the cheap test.

Pre-reg bands:
  HARD-PASS: end-to-end accuracy >= 0.80 on 50 one-step problems (pipeline viable)
  MIDDLE-BAND: 0.50-0.80 (extraction works on some constructions; curated subset viable)
  HARD-FAIL: < 0.50 (extraction fails; LLM hybrid required for extraction stage; not just solving)

### Anchor 5: unified_tier1_codebook_v1 -- Math operators as Tier-1 atoms alongside grammatical atoms

Anchor pointer: Research note Section 3 Exp-2 (UNIFIED-TIER1)
Substrate-product reading: Add math operators (+, -, *, /, d_dx, integral, SIGMA) to the Tier-1 codebook alongside English function words (NOT, AND, OR, IF, BECAUSE). Build a hybrid construction that parses a natural-language-with-math expression (e.g., "the derivative of x squared plus three") into a formal expression structure. If HARD-PASS: unified Tier-1 across language and math is empirically viable, substantiating the theoretical Montague/NSM claim that logical operators (NOT, IF, BECAUSE) and math operators are the SAME class of Tier-1 atom.
Tier hint: CPU local, ~30 min. Requires hybrid construction inventory.
Why-now: Theoretical analysis (Section 1.7) identifies this as the convergence point of 5 independent streams. Cheap and theoretically motivated.

Pre-reg bands:
  HARD-PASS: hybrid parse accuracy >= 0.90 on 100 hybrid expressions at depth <= 4
  MIDDLE-BAND: 0.70-0.90 (partial; deep nesting or ambiguous constructions fail)
  HARD-FAIL: < 0.70 (unified codebook causes interference; domains must be separated)

### Anchor 6: latex_fcg_parse_v1 -- LaTeX as FCG constructions

Anchor pointer: Research note Section 3 Exp-4 (LATEX-FCG)
Substrate-product reading: Represent a subset of LaTeX math commands (sum, integral, frac, sqrt, ^, _) as FCG constructions. Test: substrate parses LaTeX expression trees at accuracy >= 0.90 on 200 expressions. If HARD-PASS: substrate can be used as a semantic search engine over LaTeX mathematical content -- significant value for academic/scientific knowledge management.
Tier hint: CPU local, ~2 hr including LaTeX construction inventory build. Highest effort in this batch.
Why-now: Niche but high-value application (scientific paper knowledge graphs). Lower priority than Anchors 1-5 but all-CPU and no external dependencies.

Pre-reg bands:
  HARD-PASS: parse accuracy >= 0.90 on 200 LaTeX expressions at depth <= 5
  MIDDLE-BAND: 0.70-0.90 (shallower depth works; deep LaTeX nesting fails)
  HARD-FAIL: < 0.70 (LaTeX structure incompatible with VSA-FCG at depth > 2; separate mechanism needed)

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_language_math_substrate_overlap_2x_2026-06-11.md
- Cap map language rows: substrate_capability_map.md -- PP-323 (bilingual), PP-331 (paragraph compose), PP-335/PP-343 (proof chains), PP-338 (comm-lex), PP-342 (WUG), PP-332 (algebra), PP-334 (calculus), PP-341 (equations), LVH-280 (pos tagger unconfirmed)
- Prior math drill: d:/AI/hd-instrument/notes/research_drill_substrate_math_capabilities_5x_2026-06-08.md
- Prior cross-language drill: d:/AI/hd-instrument/notes/research_drill_tier1_universals_cross_language_2x_2026-06-10.md
- PP-356 role-substrate design (fallback if shared-W fails): cap_map PP-356 row

---

## Contract section

exp_dev owns: anchor design, cell-grid specification, script authoring, queue dispatch, pre-reg band confirmation
research-owns boundary: theoretical analysis (research note) and anchor routing (this file) are complete
Orchestrator decision point: after Anchor 1 (pos_tagger_ptb_confirm_v2), if LVH-280 HARD-FAIL, the language-side architecture claims are downgraded; report verdict to orchestrator before dispatching Anchors 2-6

---

## Autonomy declaration

exp_dev may dispatch Anchor 1 and Anchor 2 in parallel without further orchestrator approval -- both are ~15 min CPU and gate the main hypothesis. Anchors 3-6 may be dispatched after Anchor 2 verdict is known. The word-problem pipeline (Anchor 4) requires building a new construction inventory; exp_dev should design the construction schema from the research note Section 3 Exp-3 description.
