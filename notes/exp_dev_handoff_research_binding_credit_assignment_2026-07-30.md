# exp_dev hand-off — research: binding credit-assignment / held-out-role addressing generalization

**Filed-by:** research sub-agent, 2026-07-30
**Trigger:** `notes/binding_credit_assignment_structured_prior_research_2026-07-30.md` — literature + brain
synthesis on why the WM's addressing key gets STUCK_FLAT (all queries collapse to cosine ~0.992) when
trained end-to-end from random init on downstream recall loss alone, even though a linear probe with
direct slot-label supervision recovers the address at acc 1.0 and transplanting those weights fixes
addressing immediately. Convergent ML literature (Sukhbaatar linear-start, Locatello slot-collapse fixes,
Csordás/Schmidhuber DNC addressing fixes, Dong/Cordonnier/Loukas attention rank-collapse theory) plus
brain literature (hippocampal fast-Hebbian indexing, grid-cell pre-structured addressing, Complementary
Learning Systems) all say: the fix is a STRUCTURAL warm-start/auxiliary-supervision intervention, not more
gradient steps on the unmodified setup.
**Pause state:** check `data/orchestrator_paused.flag` before shipping; this hand-off is filed regardless
of pause state per research-role convention — exp_dev/director should not treat this as queue authorization.

Per [[feedback-no-experiment-design-in-prompts]]: this file states WHAT to test and WHY (falsifiable bands,
context pointers) — exp_dev owns exact implementation (grid sweep, seeds, exact aux-loss formulation).

## Anchor candidates (rank-ordered)

### 1. `exp_wm_addressing_heldout_role_warmstart_v1` (primary, do this first)

**Anchor pointer:** the held-out-role generalization protocol in
`binding_credit_assignment_structured_prior_research_2026-07-30.md` section (d).

**Substrate-product reading:** if this passes, the substrate can learn NEW binding/addressing tasks by
warm-starting a small auxiliary-supervised probe over its own frozen encoder representations, then
GENERALIZE to roles/slots never explicitly supervised — the "converse about combinations never literally
trained" story, now for LEARNED (not fixed-algebra) addressing, which is the more general case
product-facing schemas will need.

**Tier hint:** load-bearing if HARD-PASS — this would be the first VET-confirmed positive that a learned
(not fixed-projection) addressing key can acquire genuinely generalizing binding via structural warm-start,
resolving the STUCK_FLAT NL working-memory blocker that's been the post-compaction CURRENT FOCUS.

**Why now:** cheap (re-pairs already-existing pieces: the WM module, the encoder, and a probe architecture
already built and proven this session) — no new primitives required, same class of "re-pairing existing
certified parts" that made the 07-16 paging-router note's recommended cell cheap.

**Design (from the research note, exp_dev owns implementation details):**
1. Split roles/slots into TRAIN-ROLES (~80%) / HELD-OUT-ROLES (~20%), disjoint, fixed seed.
2. Train the linear addressing probe with direct slot-label supervision on TRAIN-ROLES ONLY.
3. Warm-start the WM's addressing key from this probe; continue end-to-end downstream-loss training with
   episodes drawn from both train and held-out roles (task exposure is fine; ADDRESS-label supervision on
   held-out roles is NOT allowed — that would invalidate the test).
4. Evaluate addressing accuracy separately on TRAIN-ROLES (sanity floor) vs HELD-OUT-ROLES (decisive
   number).
5. Can-fail control A — no-warm-start baseline (original STUCK_FLAT setup, same role split): must fail on
   both splits, or the test is vacuous (report INVALID, do not interpret further).
6. Can-fail control B — per-role-lookup baseline (k-NN/nearest-train-role table, no shared structure):
   must score near-chance on held-out roles; if warm-started arm matches THIS control on held-out rather
   than its train-role score, that's disguised memorization, not generalization.

**Pre-registered bands (full detail in the research note):**
- HARD-PASS: held-out-role accuracy >= 0.80, gap vs train-role <= 0.15, no-warm-start control stays at/near
  STUCK_FLAT (confirms non-vacuous), warm-started arm clears per-role-lookup control by >= 0.30 on
  held-out roles.
- HARD-FAIL: held-out-role accuracy < 0.40, OR held-out gap > 0.35, OR warm-started arm within 0.10 of the
  per-role-lookup control on held-out roles.
- INVALID: no-warm-start control doesn't reproduce STUCK_FLAT on this split (construction bug); or
  train-role accuracy itself < 0.85 (aux signal didn't even converge on its own supervised set).

### 2. `exp_wm_addressing_longer_schedule_control_v1` (cheap, run alongside #1, NOT instead of)

**Anchor pointer:** research note's Cross-thread synthesis, Olsson et al. induction-head counter-hypothesis.

**Why:** honest live alternative — induction heads form via sudden phase transition from plain next-token
loss alone, no auxiliary supervision, given the right architecture/scale/data. Before fully committing to
"must warm-start," cheaply check whether the SAME architecture/loss, run 5-10x longer/more data with NO
warm-start, also un-sticks late. If it does, the structural verdict in the research note needs revision
(schedule/scale, not structural prior, would be the real lever). If it stays flat at 5-10x, that
strengthens the structural verdict and should be reported alongside #1's result, not run as a substitute.

**Tier hint:** cheap diagnostic/control, not itself load-bearing — its value is in DISAMBIGUATING #1's
result, report both together.

## Context pointers (files, not summaries)

- `notes/binding_credit_assignment_structured_prior_research_2026-07-30.md` — full research synthesis,
  citations, calibration, all pre-registered bands in detail.
- `notes/research_learned_noise_robust_addressing_page_routing_2026-07-16.md` — the fixed-projection
  DG-analog router already proven brain-faithful and generalizing for a different (paging) purpose;
  relevant precedent for what "genuinely generalizing addressing" looks like on this substrate, and a
  fallback design if #1 HARD-FAILs.
- `notes/research_native_binding_compositional_generalization_2026-07-25.md` — fixed-bind + single linear
  readout systematicity result; the addressing-key warm-start in #1 is the same structural move (freeze
  the generalizing part, don't let a free parameter entangle idiosyncrasies) applied to the WM's key
  specifically.
- Wherever the WM module + linear probe + encoder currently live in `experiments/` and `hdlab/` — exp_dev
  should locate the exact files from the session's current STUCK_FLAT cell (not named here since this
  hand-off is written from research's external vantage; the director/exp_dev session has the live paths).

## Contract section

- exp_dev owns: exact role/slot taxonomy and split mechanics, exact aux-probe architecture/loss, exact
  seed count, exact grid over warm-start-only vs warm-start-plus-continued-training, exact longer-schedule
  multiplier for control #2.
- Research (this note) fixes: the falsifiable HARD-PASS/HARD-FAIL/INVALID bands, the two can-fail controls,
  and the brain-faithfulness reasoning (section (c) of the parent note) that should NOT be re-litigated
  without new evidence — cite it, don't re-derive it.
- Per no-bolt-on-reader / no-borrowed-embeddings invariants: the probe MUST be trained on this substrate's
  OWN frozen encoder representations (already the case in the session's existing probe), never an external
  pretrained model; this hand-off does not authorize introducing any external embedding at this step.

## Autonomy declaration

exp_dev decides cell file naming, exact hyperparameters, exact grid density, and whether to run #1 and #2
in the same cell or as separate cells. Falsifiable bands and the two mandatory can-fail controls in #1 are
NOT exp_dev's to loosen without flagging the change explicitly in the pre-reg.
