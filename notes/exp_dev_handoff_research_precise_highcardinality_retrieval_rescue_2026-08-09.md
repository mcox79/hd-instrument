# exp_dev hand-off — research: precise high-cardinality retrieval rescue (Stage 1.5 salted-cardinality gate)

**Filed-by:** research sub-agent, 2026-08-09.
**Trigger:** `notes/research_precise_highcardinality_retrieval_rescue_2026-08-09.md` — brain-fidelity + substrate drill
finding the rescue for the anticipated high-cardinality over-pull-in wall in the Cowan-4 focus simulation-engine
program (`hdlab/situation_focus.py` salience-gated `iterative_attractor` pull-in, validated HARD-PASS at toy scale
via `experiments/exp_focus_pullin_causal_stage1_micro_world_v1.py`). Filed in parallel with Stage-2 sub-test B,
which is measuring the same anticipated failure directly — this hand-off supplies the diagnosed mechanism (extreme-
value inflation of the max-over-M null-similarity score) and the ranked rescue.

**Pause state:** check `data/orchestrator_paused.flag` before shipping; this hand-off is filed regardless of pause
state per research-role convention — it is not queue authorization by itself.

Per [[feedback-no-experiment-design-in-prompts]]: this file states WHAT to test and WHY (falsifiable bands, context
pointers) — exp_dev owns exact implementation (exact distractor construction, exact context-key form, exact cell
structure, seeds).

## Anchor candidates (rank-ordered)

### 1. Salted-cardinality micro-world gate (primary, do this first — cheapest, isolates the cardinality variable alone, no real CSKG dependency)

**Anchor pointer:** research note section "Cheap decisive test" + `experiments/exp_focus_pullin_causal_stage1_micro_world_v1.py` (the Stage-1 cell to extend, not replace — reuse `build_microworld`, `build_causal_facts`, `BipolarCausalRegister`, `pull_in`, `_sweep` verbatim).

**Substrate-product reading:** if the FLAT arm's `false_pull_in_rate` rises with M as predicted AND the CONTEXT-CONDITIONED arm holds flat, this confirms both the diagnosis (EVT cardinality inflation, not a MCScript2-style weak-signal problem) and the rescue (context-conditioned pre-filter + calibrated threshold, reusing the already chain-grade-CERT'd `KGStore`) in one cheap CPU gate, before any real-CSKG-scale wiring is attempted. If the FLAT arm does NOT show the predicted rise, it falsifies this drill's central diagnosis and redirects the investigation (see HARD-FAIL below) — a more informative negative than proceeding to real-scale wiring on an unconfirmed mechanism.

**Tier hint:** load-bearing gate for the Stage-2 CSKG-scale wiring decision. Sequence this BEFORE any full CSKG pull-in wiring attempt — cheap-decisive-first.

**Why now:** every primitive already exists and is independently validated: `hdlab/kg_traversal.py::KGStore` (chain-grade CERT 585, `setrecall@M=100000=1.000`, `refuse_OOD=0.999`, registry WIRED) supplies both the context-conditioned key-bind pattern and the calibrated-threshold pattern (`refuse_gate_calibrate`); `hdlab/cleanup_family.py::iterative_attractor` is the existing `pull_in()` core; `experiments/exp_focus_pullin_causal_stage1_micro_world_v1.py`'s micro-world, causal register, and scramble-control convention (`_deterministic_perm`, hashlib-seeded) are reused unmodified. The only genuinely new work is (a) synthetic distractor generation at 3 cardinality rungs and (b) adapting `refuse_gate_calibrate`'s in/out-of-set split to the pull-in admission task shape (a small wrapper, not a new mechanism).

**Design (from the research note, exp_dev owns implementation details):**
1. Reuse Stage-1's exact 5-cluster x 6-event micro-world unmodified (same planted long-distance relations). Generate `N_DISTRACTOR` synthetic distractor events via the same `EventBundleCodec` construction, disjoint symbol namespace, no causal/associative relation to the 5 real clusters or each other. Three cardinality rungs: M~1,000 / M~10,000 / M~100,000 (exp_dev picks exact counts and whether to checkpoint per-rung).
2. **Arm FLAT:** current `pull_in()` unmodified — `iterative_attractor` over the full salted codebook, fixed `GATE_THRESH=0.28` (or whatever Stage-1's calibrated value is at cell-authoring time). Measure `false_pull_in_rate` at each rung.
3. **Arm CONTEXT-CONDITIONED:** bind the probe with the current `ChunkedFocus`'s active-context (exp_dev picks the exact context-key construction — e.g. a `KGStore`-style `E[context]*R[relation]` pre-bind restricting the candidate pool to a coarse shortlist) BEFORE running `iterative_attractor` within that shortlist; set the admission threshold via a `refuse_gate_calibrate()`-style in-set/out-of-set calibration instead of the fixed constant. Measure `false_pull_in_rate` at each rung.
4. **Arm NULL-SWEEP:** query every distractor against the full salted codebook (no real relation exists by construction) at each rung; record the empirical max-cosine distribution. Compare against the EVT prediction `E[max] ~ sqrt(2*ln M)` (exp_dev picks exact fit/comparison method).
5. MANDATORY: keep the existing Stage-1 scramble control and off-topic sweep structure intact at M=30 as a regression check (the salted-cardinality gate must not silently break the already-HARD-PASSed Stage-1 result).
6. Report per-rung, per-arm `false_pull_in_rate`, `in_cluster_correct_retrieval_rate`, and the null-sweep max-cosine curve vs. the EVT prediction — glass-box, every admission decision inspectable (candidate, score, admitted/gated, which arm).

**Pre-registered bands (from the research note, verbatim):**
- **HARD-PASS:** FLAT arm `false_pull_in_rate` at M=100,000 >= 2x its M=1,000 value AND CONTEXT-CONDITIONED arm `false_pull_in_rate` at M=100,000 <= 1.5x the Stage-1 M=30 baseline AND null-sweep max-cosine growth from M=1,000 to M=100,000 is within +/-30% of the EVT `sqrt(2*ln M)` prediction.
- **HARD-FAIL:** CONTEXT-CONDITIONED arm ALSO rises >= 2x by M=100,000 (context-conditioning insufficient — escalate to Rank-2/Rank-3, see research note) OR FLAT arm does NOT show the predicted rise (wall is not primarily an EVT/cardinality effect — re-diagnose before any further scale-up work).
- **MIDDLE_BAND:** everything else (e.g. context-conditioning slows but does not bound the rise — informative, motivates layering Rank-3 expansion+sparsify under Rank-1 rather than treating Rank-1 as sufficient alone).

### 2. Resonator-factorized retrieval probe (do only if #1 HARD-FAILs on the CONTEXT-CONDITIONED arm, or as a parallel scale-ceiling probe if #1 HARD-PASSes but real-CSKG cardinality (~1.24M) is far beyond the tested 100,000 rung)

**Anchor pointer:** research note section "Rank 2 — resonator factorized retrieval" + `experiments/exp_resonator_dg_crosstalk_disentangler_v1.py` (reuse its oracle-unbind-margin measurement methodology directly rather than building a second harness) + `experiments/exp_substrate_resonator_focus_lever_v1.py` (hierarchical 2-group decomposition pattern to reuse for factoring the causal-fact space).

**Design:** decompose the causal-fact representation into K factors (exp_dev picks the exact factoring, e.g. predicate-type x subject-entity x object-entity) each with its own smaller per-factor codebook; measure oracle-unbind margin and false-pull-in-rate at the same cardinality rungs as anchor #1, compared against anchor #1's best arm.

**Why now:** bigger structural lift than #1 (re-designing the causal-fact representation as a K-factor bound product), so sequence AFTER #1 establishes whether the cheaper context-conditioned fix suffices. The resonator machinery itself is already substrate-validated (`exp_resonator_factorization_v1.py`, chain-grade family); the crosstalk math for exactly this M^K-vs-N^2 regime is already worked out in `exp_resonator_dg_crosstalk_disentangler_v1.py` (Tsodyks-Feigelman framing) — reuse it, do not re-derive.

**Pre-registered bands:** deferred to exp_dev pre-reg at ship time, conditioned on anchor #1's actual result (research note flags this as Rank-2, not yet cell-ready — the exact K-factor construction is exp_dev's design call).

## Context pointers (files, not summaries)

- `notes/research_precise_highcardinality_retrieval_rescue_2026-08-09.md` — full brain-fidelity + substrate synthesis, 4 lit-scan lanes, EVT quantitative grounding, 4 ranked rescue candidates, MCScript2-vs-Stage-2-B failure-mechanism distinction.
- `experiments/exp_focus_pullin_causal_stage1_micro_world_v1.py` — Stage-1 cell (HARD-PASS at toy scale); `build_microworld`, `build_causal_facts`, `BipolarCausalRegister`, `pull_in`, `_sweep`, `_deterministic_perm` scramble convention, `GATE_THRESH=0.28` current fixed value.
- `hdlab/situation_focus.py` — `ChunkedFocus` (Cowan-4 bounded focus), `FlatFocus`.
- `hdlab/kg_traversal.py` — `KGStore.key(s,p)` (context-conditioned bind), `KGStore.refuse_gate_calibrate()` (calibrated threshold via in-KB/OOD split), CERT 585 provenance in module docstring (`setrecall@M=100000=1.000`, `refuse_OOD=0.999`).
- `hdlab/cleanup_family.py` + `hdlab/iterative_attractor.py` — `iterative_attractor`/`iterative_cleanup` (the `pull_in()` core), `peel_sic_readout` (Rank-4 post-retrieval competitor-deflation refinement, CERT-validated).
- `experiments/exp_resonator_dg_crosstalk_disentangler_v1.py` — Tsodyks-Feigelman crosstalk-capacity framing (M^K vs N^2 cliff), oracle-unbind-margin methodology to reuse for anchor #2.
- `experiments/exp_substrate_resonator_focus_lever_v1.py` + `experiments/exp_resonator_factorization_v1.py` — resonator hierarchical decomposition + core factorization primitives for anchor #2.
- `data/capability_registry.jsonl` — `cleanup_attractor` (WIRED_BUT_NOT_PIPELINE_REACHABLE — flags that `iterative_attractor` is validated but not yet in the live focus query path, consistent with this hand-off's wiring framing) and KGStore's registry entry.

## Contract section

- exp_dev owns: exact distractor-generation construction, exact context-key binding form for the CONTEXT-CONDITIONED arm, exact `refuse_gate_calibrate`-adaptation details, exact cardinality-rung counts (1,000/10,000/100,000 are the research note's suggested rungs, not mandatory exact values), exact cell/file naming, exact seed handling, whether to checkpoint per-rung (recommended given M=100,000 rung cost).
- Research (this hand-off + parent note) fixes: the falsifiable HARD-PASS/MIDDLE_BAND/HARD-FAIL bands, the mandatory Stage-1 regression check (M=30 result must not silently break), the mandatory null-sweep arm (do not skip — it is what separates the EVT diagnosis from a MCScript2-style weak-signal misdiagnosis), the cheap-decisive-first sequencing (anchor #1 before anchor #2), the glass-box/no-LLM-at-inference invariant, and the requirement that every admission decision be inspectable (candidate, score, admitted/gated, which arm).

## Autonomy declaration

exp_dev decides the exact distractor construction, exact context-key form, exact calibration wrapper, exact cell/file naming, exact rung counts, and exact seed count. The falsifiable bands, the mandatory null-sweep arm, the mandatory Stage-1 regression check, and the cheap-decisive-first anchor ordering (#1 before #2) are NOT exp_dev's to loosen or drop without flagging the change explicitly in the pre-reg.
