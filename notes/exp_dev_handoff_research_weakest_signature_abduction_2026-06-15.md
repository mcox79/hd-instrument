# exp_dev hand-off -- research: WEAKEST-SIGNATURE abduction cheap test

**Filed:** 2026-06-15 by Research sub-agent.
**Parent research note:** `notes/research_weakest_signature_abduction_for_gap_driven_promotion_2026-06-15.md`
**Trigger:** USER strategic question -- gap-driven abductive promotion loop; abduction step (reverse-math-style minimal-strength predicate that closes the failure) is the novel kernel.
**Pause state:** Honor `data/orchestrator_paused.flag` at dispatch time. This is a CHEAP CPU-only design probe (< 1 hr). If paused, queue for resume; do not bypass.

Per [[feedback-no-experiment-design-in-prompts]]: this note POINTS at the research note and the 3-mechanism stack synthesis. It does NOT specify the exact implementation -- exp_dev owns design autonomy.

---

## ANCHOR CANDIDATES (rank-ordered)

### Anchor 1 (PRIMARY) -- `abduction-weakest-sig-cheap-test-v1`
- **Substrate-product reading:** measure whether the substrate can compute a SHAPE for the missing predicate that closes a measured capability failure, with reverse-direction minimality certification. First empirical step in operationalizing the gap-driven abductive promotion loop.
- **Tier hint:** Tier 2 candidate; promotes to Tier 1 architectural Claim 16 candidate on HARD-PASS.
- **Why now:** USER 2026-06-15 evening framed the loop; abduction step has now a concrete 3-mechanism stack (CEGAR interpolation + Progol bottom clause + reverse-math-style leave-one-out minimality). Cheap CPU-only test; uses existing 4-gate validator + existing 105 operator signatures + held-out failure set; zero new infrastructure.
- **Pre-reg HARD-PASS:** >= 4/10 (40%) failures yield minimal-certified P closing the gate, AND >= 2 of those P's correspond to corpus atoms that EXISTED but were not load-bearing (recover-known-but-passive case the USER wants).
- **Pre-reg HARD-FAIL:** <= 1/10 (10%) yield minimal-certified P, OR every produced P is corpus-novel (abductor is searching not abducting).
- **Pre-reg MIDDLE BAND:** 2-3/10. Mechanism real but bottom-clause shape too narrow; redesign mode declarations.
- **Calibration:** P(HARD-PASS) deflated to 0.35 per lit-scan calibration penalty (novel synthesis of CEGAR + Progol + reverse-math on substrate's hyperdimensional capability signatures is uncharted in published lit).

### Anchor 2 (FALLBACK if Anchor 1 HARD-FAILs) -- `abduction-LGG-weakest-explanation-v1`
- **Substrate-product reading:** alternative weakest-explanation route via Plotkin LGG / Inoue prime-implicate consequence-finding. Different soundness route (subsumption-lattice minimality) but same end-product.
- **Tier hint:** Tier 3 fallback.
- **Why-now:** queued conditional on Anchor 1 HARD-FAIL. Adjacent finding from Sonnet 3 lit-scan; bounded LGG (Kuzelka-Zelezny 2012) restores polynomial cost so still CPU-feasible.
- **Pre-reg gates:** same 40%/10% thresholds, but interpreted over LGG-minimal P rather than interpolant-minimal P.

### Anchor 3 (FOLLOW-UP only on Anchor 1 HARD-PASS) -- `abduction-predicate-invention-v1`
- **Substrate-product reading:** extend from recover-known-but-passive to INVENT-novel-predicate case (Muggleton W-operators / MIL meta-rules). Tests whether the substrate can also compute the SHAPE of a primitive that does not yet exist in vocabulary.
- **Tier hint:** Tier 2 (Phase 2).
- **Why-now:** ONLY after Anchor 1 demonstrates recovery; invention is harder and unbounded without bias.

---

## CONTEXT POINTERS

- Parent research note (3-mechanism stack synthesis + 10-mechanism ranking + soundness profiles): `notes/research_weakest_signature_abduction_for_gap_driven_promotion_2026-06-15.md`
- Current substrate state (26285 atoms / 5279 relations / 217 axiom-terms / 105 operator signatures + 4-gate validator): `notes/SUBSTRATE_DIRECTOR_STATE.md`
- 4-gate validator location + RelationType enum gotchas: `notes/substrate_schema_gotchas_RelationType_enum_2026-06-15.md`
- USER 2026-06-15 LLM-bootstrap ruling (applies if abductor needs LLM-seeded mode declarations as bootstrap): `MEMORY.md` entry "USER ruling 2026-06-15: LLM-assisted candidate SELECTION OK as bootstrap until substrate self-selects".
- 19th methodology rule "adversarial self-correction of own DETECT output": relevant for the leave-one-out minimality certification step.
- Held-out capability failure set (the 651 currently-open derivations are the failure pool): pick 10 where 4-gate validator outputs HARD-FAIL with "no atom signature covers the goal" failure mode.

---

## CONTRACT

**Deliverable shape:**
1. The 10 selected failure witnesses (query + closest-matching primitive signatures the validator did try + residual goal that did not unify).
2. Per failure: hypothesized predicate P from the 3-mechanism stack (Progol bottom + CEGAR interpolant); whether gate now PASSES with P; leave-one-out minimality certificate (each literal removed -> gate fails again).
3. Counts: minimal-certified-P fraction; corpus-recovered fraction; corpus-novel fraction.
4. HARD-PASS / HARD-FAIL / MIDDLE-BAND call against Anchor 1 pre-reg gates.
5. Status_log entry (event_kind="experiment_result", importance=HIGH on HARD-PASS, MEDIUM otherwise).
6. Entry in `exp_dev_decisions_<date>.md`.

**Cost ceiling:** CPU-only, < 1 hr total. No GPU. No new dependencies (use existing 4-gate validator + signature lattice).

---

## AUTONOMY

Exp_dev decides:
- Which 10 failure witnesses from the 651 open derivations.
- Exact bottom-clause saturation strategy (full mode declarations or restricted).
- Exact interpolant computation (Craig interpolation library, theory, or custom signature-lattice traversal).
- Whether to apply minimality check as leave-one-out at literal level or at clause-subterm level.
- Anchor name and queue entry format.
- Whether to instrument additional diagnostics (e.g. per-failure shape comparison between Progol bottom and CEGAR interpolant -- they should AGREE on the minimal case; disagreement is informative).
- Whether to also run Anchor 2 in parallel as a control (cost-permitting).

---

**End handoff.**
