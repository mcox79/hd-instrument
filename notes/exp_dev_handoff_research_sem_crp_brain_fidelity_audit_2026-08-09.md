# exp_dev hand-off — research: sticky-CRP brain-fidelity audit (match-or-spawn mechanism)

**Filed-by:** research sub-agent, 2026-08-09.
**Trigger:** `notes/research_sem_crp_brain_fidelity_audit_2026-08-09.md` — director-requested adversarial
audit of whether the sticky-CRP mechanism named in
`notes/exp_dev_handoff_research_brain_script_acquisition_consolidation_2026-08-09.md` anchor 3 (the
reuse-existing-`LibraryItem`-vs-spawn-new decision in `hdlab/grounding_acquisition_loop.py`) is a
brain-validated mechanism or a convenient computational-level prior. Finding: SEM's own authors (Franklin,
Norman, Ranganath, Zacks & Gershman 2020, Psych Review) explicitly and repeatedly disclose sticky-CRP as a
computational-level (Marr level 1) rational model, NOT a claimed neural algorithm — "we are agnostic to the
specific details of how it is learned in the brain," "our neural predictions are an open empirical question
for future research." No independent replication of the sticky-CRP mechanism itself by outside authors was
found; one outside benchmark (Basgol/Ayhan/Ugur 2022/2023) found a non-CRP alternative outperforms it, and a
2024 ML review (Nguyen, arXiv:2409.18992) independently argues to replace the fixed CRP prior with a learned
one. No paper — including Gershman's own flagship papers that use explicit CRP concentration parameters
(Sanders/Wilson/Gershman 2020 eLife hippocampal-remapping paper) — proposes a concrete neural/neuromodulatory
implementation for the CRP hyperparameters; SEM's own "Neural Correlates" section assigns brain regions to
OTHER quantities (vmPFC=posterior, dopamine=within-event error) and never mentions ACh/NE/LC/pupil at all.
Separately: dentate gyrus (DG) pattern separation + CA3 pattern completion is a causally-tested
(NMDAR-knockout, Nakazawa et al. 2002), continuously-graded (sigmoidal similarity-response, Leutgeb et al.
2007), competitive-dynamics circuit account of exactly the same functional decision (familiar-reuse vs
novel-spawn) — structurally a materially different SHAPE (continuous similarity-graded competition between
two coupled subsystems, no free global stickiness hyperparameter) than a discrete CRP urn-scheme draw. No
paper compares the two frameworks directly, so recommending DG/CA3-shaped continuous competition as the
anchor-3 mechanism is this drill's own novel-synthesis proposal, not literature-supplied — hence the cheap
decisive test below, sequenced BEFORE the full anchor-3 build.

**Pause state:** check `data/orchestrator_paused.flag` before shipping; this hand-off is filed regardless of
pause state per research-role convention — it is not queue authorization by itself.

Per [[feedback-no-experiment-design-in-prompts]]: this file states WHAT to test and WHY (falsifiable bands,
context pointers) — exp_dev owns exact implementation (exact similarity-threshold function, exact corpus,
exact cell structure, seeds).

## Anchor candidates (rank-ordered)

### 1. `exp_dg_ca3_vs_crp_match_or_spawn_ablation_v1` (primary — insert BEFORE the sister note's anchor 3, cheaper, directly arbitrates the anchor-3 mechanism choice)

**Anchor pointer:** parent note's "Cheap decisive test" section + "Falsifiable predictions" section.

**Substrate-product reading:** if this HARD-PASSes, it replaces anchor 3's planned CRP-style soft-match/spawn
logic with a simpler (fewer free hyperparameters), brain-motivated continuous-similarity mechanism BEFORE any
engineering effort goes into the CRP version — avoids building the less-defensible mechanism first. If it
HARD-FAILs, it still licenses building CRP as originally planned, now with an explicit, correct docstring
label ("rational/computational-level heuristic, not a claimed brain mechanism" — per the parent note's Marr
adjudication) instead of an implicit brain-fidelity overclaim.

**Tier hint:** load-bearing for anchor 3's mechanism choice specifically — this is a one-variable swap-in
test (match-or-spawn decision rule only), independent of anchor 3's other unresolved pieces (relative-
threshold flag, MDL gate), so it can run in parallel with or before those.

**Why now:** cheapest possible arbitration — reuses whatever synthetic multi-script corpus anchor 3 already
requires (or a smaller stand-in), reuses `AccumulateRegister` (already scoped in the sister hand-off) for the
similarity computation, and reuses `grounding_acquisition_loop.py::self_test`'s existing coherent/scrambled/
adversarial invariants as the safety gate for both candidate mechanisms.

**Design (from the research note, exp_dev owns implementation details):**
1. Implement the CRP-style stickiness/concentration draw exactly as the sister hand-off's anchor 3 currently
   specifies (baseline condition A).
2. Implement a DG/CA3-motivated alternative (condition B): compute a continuous similarity score between the
   incoming trace's situation-model register (`AccumulateRegister`) and each existing `LibraryItem`'s
   accumulated register — the CA3-style "how close is this to a stored attractor" measure. Pass it through a
   graded threshold whose steepness is a function of local competition among candidate items (a DG-sparsity-
   style suppression term), not a free global concentration hyperparameter. Spawn a new `LibraryItem` only
   when no candidate clears the graded threshold. Per the research note's finding that CRP's "stickiness"
   term has no clean neural analog (hippocampal recency effects are conventionally attributed to
   slowly-drifting temporal-context representations, not a cluster-recency prior — flagged in the parent note
   as background knowledge, not fetch-verified this cycle, so treat that specific sub-claim with appropriately
   lower confidence): condition B should NOT include an explicit recency/stickiness term unless exp_dev can
   independently motivate one.
3. Run both conditions on the identical corpus and report: cluster-purity, reuse-accuracy, and
   false-consolidation-resistance (0% of one-off/adversarial items ever promoted, at any pass) — reusing
   whatever corpus/metrics anchor 3's design already specifies, or a smaller stand-in if anchor 3's full
   corpus isn't built yet.
4. Re-run `grounding_acquisition_loop.py::self_test`'s existing coherent/scrambled/adversarial invariants
   under BOTH conditions to confirm neither introduces a new false-consolidation path.

**Pre-registered bands (from the research note, verbatim):**
- **HARD-PASS**: condition B (continuous-similarity/graded-threshold) matches condition A (CRP)'s
  cluster-purity and reuse-accuracy within 5% AND passes all of `self_test`'s existing invariants with zero
  regressions AND has fewer free hyperparameters (no separate concentration + stickiness constants) —
  adopt B as the anchor-3 mechanism; this converges with Nguyen (2024)'s independent ML-side "replace the
  fixed CRP prior" critique.
- **MIDDLE_BAND**: A and B are statistically indistinguishable on the current (likely small/synthetic) corpus
  — underpowered, not evidence of equivalence; proceed to anchor 3's richer full multi-script corpus before
  concluding redundancy, mirroring the sequencing discipline the sister note already applies to its own
  anchor 1 vs anchor 3.
- **HARD-FAIL**: condition B degrades cluster quality by more than 15% relative to A, OR condition B
  introduces a NEW false-consolidation path that A correctly avoided (any one-off/adversarial item promoted
  under B that A correctly rejected) — in that case build anchor 3 with CRP as originally planned, but update
  its module docstring to explicitly label the mechanism as "a rational/computational-level heuristic
  borrowed from Gershman's cognitive-modeling literature (Franklin/Norman/Ranganath/Zacks/Gershman 2020), not
  a claimed or validated brain mechanism" — never excuse the mislabeling just because CRP wins functionally.

## Context pointers (files, not summaries)

- `notes/research_sem_crp_brain_fidelity_audit_2026-08-09.md` — full synthesis: Marr-level adjudication
  table, all 4 lit-scan lane findings (SEM's own framing, Gershman-Blei-Niv's own framing, DG/CA3 causal
  evidence, and the verified absence of any CRP-to-neuromodulator bridge even in the model's own flagship
  paper), calibration section.
- `notes/exp_dev_handoff_research_brain_script_acquisition_consolidation_2026-08-09.md` — the sister hand-off
  whose anchor 3 this drill directly arbitrates; anchor 3's corpus design, `AccumulateRegister` keying plan,
  and pre-registered bands are the design this drill's condition A/B ablation should reuse rather than
  duplicate.
- `hdlab/grounding_acquisition_loop.py` — the module to extend: `Library`/`LibraryItem`/`Trace` (currently
  lemma-keyed — this drill's target), `self_test` (the existing coherent/scrambled/adversarial invariant
  tests both conditions must continue to pass).
- `hdlab/situation_model_accumulate.py` — `AccumulateRegister` (the register both conditions' similarity
  computation is keyed on).

## Contract section

- exp_dev owns: exact similarity-score function and graded-threshold shape for condition B, exact CRP
  concentration/stickiness constants for condition A, exact corpus (reuse anchor 3's if already built, else a
  smaller stand-in), exact cell/file naming, exact seed handling.
- Research (this hand-off + parent note) fixes: the falsifiable HARD-PASS/MIDDLE_BAND/HARD-FAIL bands, the
  requirement that condition B avoid an unmotivated stickiness term, the mandatory `self_test` invariant
  check under both conditions, the sequencing (this ablation before or alongside anchor 3, not after), and
  the mandatory docstring-relabeling fallback if HARD-FAIL — CRP may still be used, but never presented as
  brain-validated.
- Honest calibration to carry into the pre-reg: P_deflated = 0.60 for the LITERATURE-CHARACTERIZATION claims
  (Marr-level framing, replication status, absence of neuromodulator bridge — unusually well-verified via
  multi-source full-text fetch this cycle). P capped at 0.50 (novel-synthesis rule) for the SPECIFIC claim
  that DG/CA3-shaped continuous competition is the right replacement mechanism and that this ablation design
  will correctly discriminate it — no paper performs this comparison directly, so this piece is this drill's
  own construction.

## Autonomy declaration

exp_dev decides all exact implementation constants named above (similarity function, threshold shape, CRP
constants, corpus, cell/file naming, seeds). The falsifiable bands, the no-unmotivated-stickiness-term
constraint on condition B, the mandatory `self_test` check, the sequencing relative to anchor 3, and the
mandatory relabeling fallback on HARD-FAIL are NOT exp_dev's to loosen or drop without flagging the change
explicitly in the pre-reg.
