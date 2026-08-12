# Build plan: DG-analog fixed-projection addressing (held-out-role generalization fix)

**Date:** 2026-07-30
**Trigger:** `exp_wm_addressing_heldout_role_warmstart_v1.py` HARD-FAILED tonight
(HARD_FAIL_PERROLE_LOOKUP_ONLY, both seeds): WARM_STARTED addr_train=1.0 / addr_held=0.0,
recall_held~chance; CONTROL_A (no warmstart) STUCK_FLAT (non-vacuous). The learned per-role
address key (`wm.key`, one row per role, warm-started or gradient-fit) MEMORIZES trained
role-addresses and generalizes ZERO to unseen roles = per-instance lookup, not comprehension.
**Fix under spec:** replace the learned key with a FIXED, non-per-role-trained projection --
the DG-analog (fixed random expand + k-WTA sparsify) already validated for a different purpose
in `notes/research_learned_noise_robust_addressing_page_routing_2026-07-16.md` (henceforth
"the 07-16 note"). This is a build plan, not new research -- reuse the 07-16 mechanism verbatim
where possible.

**KB-check (substrate_query.sh not run standalone here; direct grep + read of the two most
relevant on-disk artifacts substitutes -- both were the exact hits a KB query would surface):**
- `notes/research_learned_noise_robust_addressing_page_routing_2026-07-16.md` -- the DG-analog
  fixed-projection router design + brain citations + prior-negative caution (read in full).
- `data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json` -- certified
  block-local-K sparse resonator, K4_acc=1.00, K8_acc=1.00, HARD_PASS, N=1000 (exact k values
  to reuse for k-WTA sparsity below).
- `notes/design_stage2_concept_encoder_spoke3_sparse_hippocampal_pattern_separation_one_shot_2026-07-02.md`
  -- exact DG-analog parameterization precedent: fixed random projection N->2N (2x expansion),
  top-K threshold at k~1% target sparsity, ternary/signed sparse code, cost O(N x 2N) per input.
  This is the parameterization this plan reuses, not re-derives.
- `experiments/exp_wm_addressing_heldout_role_warmstart_v1.py` -- the HARD-FAILED cell; this
  plan's test is a ONE-VARIABLE swap on top of it (see section 3).
- `experiments/exp_selective_overwrite_recall_nl_wm_readcond_v1.py` -- `ReadCondWM`, `Conditioner`
  (pca_whiten), `_addr_logits`, `_role_reps` -- the exact classes/methods being modified.

No new lit-scan dispatched: this is a mechanism re-pairing of two already-certified primitives
(fixed DG expansion, block-local-K sparsify) onto an already-built WM, not a new research
question. Per [[feedback-dont-dismiss-adjacent-methods]] this is flagged as adjacent-method
reuse, not premature dismissal of alternatives -- section 4 covers the one live open question
(does the fixed projection preserve the low-variance slot signal) with a cheap pre-check.

---

## HEADLINE

**The held-out-role HARD-FAIL is exactly the failure mode the 07-16 note's own literature
review predicts for a LEARNED key: Hopfield/attractor-style associative addressing has "zero
capacity for genuinely novel content" (07-16 note, A4) -- a per-role learned row, warm-started
or not, is structurally a stored-pattern lookup, and an unseen role has no stored pattern.**
The 07-16 note's proposed fix for exactly this gap is the DG-analog: a FIXED (non-trained)
random expansion + k-WTA sparsify projection that maps ANY input -- trained-role or
never-seen-role alike -- to a well-separated sparse address by construction, because it is a
deterministic function of the input's own geometry, not a lookup into a table of trained rows
(07-16 note A3/A4, LSH-equivalence argument). This plan swaps ONLY the addressing key
(`ReadCondWM._addr_logits` / `wm.key`) for that fixed projection, holding every other
component of the HARD-FAILED cell (encoder, whitening, role-extraction attention, WM
gating/overwrite, readout, training loop, eval protocol, bands) identical, and reuses the
07-16 note's own recommended ablation-ladder discipline to guard against its own documented
prior-negative risk (geometry-works-recall-doesn't pairing mismatch).

P_deflated (novel-synthesis mapping onto this specific WM architecture, capped + lit-scan
calibration penalty applied): **0.35** -- see section 4 and the calibration note at the end.

---

## 1. The exact fixed-projection addressing mechanism

**Where it lives:** replaces `ReadCondWM.key` (currently `nn.Parameter [K_SLOTS, d_enc]`,
learned, one row per role) and `ReadCondWM._addr_logits` in
`exp_selective_overwrite_recall_nl_wm_readcond_v1.py`. New class name suggestion (not binding
on exp_dev): `FixedDGAddressWM` (subclass or fork of `ReadCondWM`).

**Pipeline (in order; nothing upstream of whitening changes):**

1. **Role extraction (UNCHANGED, stays learned):** `role_query` (`nn.Parameter [2, d_enc]`,
   shared across ALL roles, not per-role) attends over the frozen token reps to produce
   `slot_u` (the role-designator rep) exactly as `ReadCondWM._role_reps()` does today. This
   param is not per-role-indexed and is NOT the thing that failed to generalize -- leave it
   learned and end-to-end trained, identical to today.
2. **Whitening (UNCHANGED, stays where it is):** `Conditioner.apply(..., kind="pca_whiten")` is
   applied to the raw token reps BEFORE role-extraction, exactly as in the HARD-FAILED cell.
   This step is load-bearing and must NOT be removed: it is what reduces the query-slot shared
   component (raw cos_mean~0.99 -> pca cos_mean~0.80, per
   `exp_selective_overwrite_recall_nl_wm_readcond_v1.py` conditioning_diagnostic, MEASURED). The
   fixed projection below operates on the WHITENED `slot_u`, not the raw encoder rep -- the DG
   analog separates what is already partially separated, it does not itself decorrelate a
   99%-collinear input (see risk section 4).
3. **Fixed random expansion (NEW, replaces `wm.key`):** a FIXED (`register_buffer`, NOT
   `nn.Parameter`, `requires_grad_(False)`, never touched by the optimizer) random projection
   `E in R^{d_exp x d_enc}`, `E ~ N(0, 1/d_enc)` (unit-norm-in-expectation columns), applied as
   `z = whitened_slot_u @ E.T` -> `[..., d_exp]`. Reuse the Spoke-3 precedent expansion ratio as
   the DEFAULT sweep center: `d_exp = 2 * d_enc` (the design note's own "N -> 2N" parameterization,
   MEASURED@`design_stage2_concept_encoder_spoke3_..._2026-07-02.md` line 97), with `d_exp in
   {2, 4, 8} x d_enc` swept (exp_dev's call, autonomy note below) -- do not hand-pick a single
   factor without checking the cheap pre-run probe in section 4 first.
4. **k-WTA sparsify (NEW, fixed, no learned parameter):** keep only the top-`k` highest-VALUE
   activations of `z` per example (NOT top-k by absolute value -- DG's code is a sparse POSITIVE
   code per the Marr/O'Reilly-McClelland framing in the 07-16 note A3), zero the rest:
   `sparse = z * (z >= kth_largest(z, k))`. Reuse the ALREADY-CERTIFIED block-local-K sparse
   resonator's exact `k` values as the default sweep set: `k in {4, 8}`
   (MEASURED@`data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json`,
   K4_acc=1.00, K8_acc=1.00, HARD_PASS at N=1000) -- do not invent new k values without first
   trying these certified ones. Target sparsity fraction (`k / d_exp`) should land near the
   Spoke-3 precedent's ~1% target (line 71 of the design note) when `d_exp` is large enough;
   report the realized fraction, don't silently drift from the ~1-4% DG-empirical band.
5. **Fixed hash-to-address pooling (NEW, fixed, no learned parameter):** a FIXED assignment
   `bucket_of: {0..d_exp-1} -> {0..K_SLOTS-1}` (a `register_buffer` int tensor, built once at
   construction via `np.random.default_rng(dg_seed).integers(0, K_SLOTS, size=d_exp)`, uniform
   i.i.d. per-coordinate bucket assignment -- the simplest fixed hash family, structurally
   equivalent to a random locality-sensitive hash per 07-16 note A4's Indyk-Motwani citation).
   `addr_logits[k] = sum over i with bucket_of[i]==k of sparse[i]` (a fixed scatter-add, `K_SLOTS`
   output dims -- SAME shape as today's `_addr_logits` output, so the rest of `ReadCondWM`
   (softmax over addr_logits, `wgate`, overwrite loop, `h_read` pooling) is UNTOUCHED). Divide
   by `addr_temp` as before. **Every one of E, bucket_of is fixed at construction time from a
   seed, registered as a buffer (not a Parameter), and asserted never to receive a gradient or
   be modified by `warm_start_key` / `warm_start_key_heldout` (which should simply not be called
   for this arm -- there is no key row to warm-start).**
6. **Downstream (UNCHANGED, stays learned, content-general):** `write_gate`, `value_proj`,
   `readout`, and the overwrite-loop recurrence are ALL UNCHANGED and remain trainable. This is
   the CA3-analog completion stage per the 07-16 note's two-stage framing (B2 table) -- it is
   learned, but it is not indexed per-role (same weights serve every address), so it is
   content-general in the same sense the existing resonator/codebook cleanup is in the 07-16
   note's paging design, and its generalization to unseen roles is not in question (only the
   ADDRESSING was memorizing).

**No per-role learned parameter anywhere in the addressing path** -- `E` and `bucket_of` are
fixed at construction (seeded, never trained); `role_query` is shared-not-per-role and was
never the diagnosed failure point; `write_gate`/`value_proj`/`readout` are content-general
(same weights read/write every address, not one set of weights per role).

---

## 2. Why this generalizes to held-out roles by construction

The learned key that just HARD-FAILED is, structurally, one row of trained parameters PER
role -- an attractor/associative-memory-style stored pattern (07-16 note A4: Hopfield-family
"capacity results are only about explicitly-written patterns; anything not stored is pulled
toward the nearest existing attractor at best"). A held-out role's key row is either left at
random init (warm-start arm) or trained only via the sparse downstream gradient signal from
mixed-role episodes -- there is no mechanism forcing that untouched/undertrained row to be
role-general, so it stays near its initialization and the argmax collapses (addr_held=0.0,
exactly the measured failure).

The fixed projection is the opposite structural class: `E` and `bucket_of` are DETERMINISTIC
FUNCTIONS applied uniformly to any input vector, seen or unseen, trained-role or held-out-role
-- there is no table of trained rows to be missing an entry from. Every whitened `slot_u`,
including one for a role that has NEVER appeared in ANY supervision signal (aux loss, warm-start
probe, or even downstream gradient, since a held-out query's slot rep still routes through the
same fixed `E`/`bucket_of` the very first time it's ever seen), gets mapped to SOME sparse code
and SOME address bucket the moment it is computed -- this is precisely the "generalizes for
free, structurally, not by interpolation" property the 07-16 note attributes to fixed
random-projection routing / locality-sensitive hashing (A4, Indyk & Motwani 1998; Kraska et al.
2018 "learned index structures" as the CS-analogy class) and to DG pattern separation
specifically (A3, Marr 1971; O'Reilly & McClelland 1994: "there is no lookup table to be
missing an entry from").

**Contrast, explicit:** learned key = "does this input match a stored attractor?" (answer:
none exists for a held-out role -> undefined/near-random). Fixed projection = "where does this
input's own geometry fall in a fixed coordinate system?" (answer: always well-defined, for
literally any input, by construction). The 07-16 note's own HARD-PASS/HARD-FAIL bands for its
paging cell make the SAME generalization claim this plan is testing (its condition (iii),
"NOVEL content -- keys constructed the same way but never inserted/trained on") -- this plan
is the first cell to point that exact claim at the addressing-key HARD-FAIL that just occurred,
rather than at the page-table lookup the 07-16 note originally scoped it for. Same mechanism,
same generalization argument, new application.

**What could still go wrong (not free of risk, addressed in section 4):** generalizing "by
construction" only holds if the fixed projection's INPUT (whitened `slot_u`) already carries
enough role-discriminative signal for the random hash to route on. A fixed hash of pure noise
still generalizes "by construction" in the sense of always returning SOME answer, but that
answer would be uncorrelated with role identity -- construction guarantees a well-defined
address for any input, it does NOT by itself guarantee that address is the CORRECT one. Section
4 is the honest treatment of this.

---

## 3. The test -- SAME held-out-role protocol, one-variable swap

**File:** fork `experiments/exp_wm_addressing_heldout_role_warmstart_v1.py` to a new file
(suggested name, not binding: `exp_wm_addressing_heldout_role_fixedproj_v1.py`) or add an arm
inline -- exp_dev's call per the autonomy note in the existing cell. Everything listed below is
REUSED VERBATIM from the HARD-FAILED cell; only item (c) changes.

**Reused verbatim (do not re-derive):**
- 15 roles, `TRAIN_ROLES` (12) / `HELD_OUT_ROLES` (3), same `ROLE_SPLIT_SEED=20260730` disjoint
  split (`HELD_OUT_ROLES` must NEVER appear as a label in any supervision signal for the arm(s)
  that have one -- N/A here since the fixed arm has no learned addressing signal at all, but the
  CONTROL_B ground-truth-restricted lookup still needs it).
- `gen_stream_expanded` / `gen_dataset_expanded` construction, leak-guards (TAIL_MIN,
  TARGET_TAIL_MIN, globally-balanced filler multiset), `construction_selftest`.
- `CONTROL_A_NO_WARMSTART` (conditioning=none, random key init, no aux, trained end-to-end) --
  MUST reproduce STUCK_FLAT on both splits, unchanged, still the can-fail floor.
- `CONTROL_B_PERROLE_LOOKUP_GROUNDTRUTH` (zero-training symbolic ceiling, structurally 0.0 on
  held-out) -- unchanged, still the "is this disguised memorization" ceiling check.
- `CONTROL_A_LONGER_SCHEDULE` (8x steps, Olsson counter-hypothesis diagnostic) -- unchanged,
  reported alongside not instead of.
- The decisive metric: addressing accuracy (query -> argmax over K=15 address logits), scored
  SEPARATELY on train-role vs held-out-role eval queries; end-to-end recall accuracy as
  secondary.
- ALL pre-registered bands, verbatim, NOT loosened:
  - `HARD_PASS`: held-out addr_acc >= 0.80 (both seeds) AND (train_addr_acc - held_addr_acc) <=
    0.15 (both seeds) AND CONTROL_A stays near chance_addr on both splits (both seeds) AND
    held_addr_acc - control_B_heldout_acc >= 0.30 (both seeds).
  - `HARD_FAIL`: held-out addr_acc < 0.40 (any seed) OR gap > 0.35 (any seed) OR
    |held_addr_acc - control_B_heldout_acc| <= 0.10 (any seed).
  - `INVALID`: CONTROL_A does not reproduce near-chance on this split OR train-role addr_acc <
    0.85 on any seed.
  - `MIDDLE_BAND_INCONCLUSIVE`: otherwise.
  - `addr_chance = 1/15 = 0.0667`, `chance_recall = 0.05`, oracle ceiling `1.0` -- unchanged.

**THE ONE HARD VARIABLE (the actual swap):**

Add a new arm, `FIXED_DG_ADDRESS` (the capability under test), replacing `WARM_STARTED`:
- Architecture: `FixedDGAddressWM` per section 1 -- pca_whiten conditioning (unchanged), fixed
  `E`/`bucket_of` (seeded, `register_buffer`, no grad), NO aux slot-address CE loss (there is no
  learned key row to supervise -- the aux loss existed specifically to shape `wm.key`, which no
  longer exists as a learned tensor), NO warm-start call. Trainable params: `role_query`,
  `write_gate`, `value_proj`, `readout` only.
- Training: identical loop (`train_arm_ext` reused, `aux=False` since there is nothing to warm-
  start or aux-supervise in the addressing path), identical steps/lr/batch/early-stop, identical
  seeds `(7, 13)`.
- Everything else in `main()` (dataset construction, CONTROL_A, CONTROL_A_LONGER, CONTROL_B,
  checkpoint/resume via `tools/exp_checkpoint.py`, verdict function, bands) is REUSED UNCHANGED
  by importing/calling into the existing cell's functions rather than re-implementing them --
  minimize the diff to the ONE swapped mechanism per the one-variable discipline this whole
  thread has been enforcing.

**Self-test additions (mirror the existing cell's self-test structure):**
- Assert `E` and `bucket_of` are NOT in `wm.parameters()` (no gradient path) and are bit-
  identical before/after a short training run (fixed-ness is a runtime-asserted invariant, not
  just a docstring claim) -- this is the direct analog of the existing cell's
  `held_out_rows_unchanged_verified` assertion, generalized to "the entire addressing path is
  unchanged," not just the held-out rows of a learned table.
- Assert `addr_logits` shape is `[..., K_SLOTS]` (unchanged interface with the rest of
  `ReadCondWM`/`train_arm_ext`/the verdict function -- no downstream code should need to change).
- Reuse `arms_differ_verified` (FIXED_DG_ADDRESS vs CONTROL_A eval-logit hash) per META_RULE_AF.

**Autonomy note (exp_dev owns):** exact `d_exp` sweep grid (default center 2x per Spoke-3
precedent, sweep `{2,4,8}x`), exact `k` sweep (default `{4,8}` per the certified block-local-K
resonator, may add `{16}` if the pre-check in section 4 suggests more headroom is needed), exact
`dg_seed`, whether `bucket_of` is drawn once globally or independently per seed (recommend: same
`dg_seed` across both seeds 7/13 so the addressing geometry itself is not a confound between
seeds -- only the trainable downstream weights vary by seed; flag this choice in the pre-reg).

---

## 4. Honest risk: does the fixed projection preserve the slot signal, or does expansion swamp it?

**This is the single biggest risk and must be checked BEFORE the full run, cheaply.**

**The diagnosed geometry (MEASURED, from the read-conditioning cell):** raw query-slot cosine
mean ~0.99 (near-total collinearity); PCA-whitened query-slot cosine mean ~0.80 (reduced, NOT
eliminated); top-1 PCA variance share only 0.135 (the shared component is spread over ~8 dims,
not a single dominant direction). This means whitening REDUCES but does not FULLY separate the
role signal -- 0.80 mean pairwise cosine is still fairly high. A fixed random projection is
NOT guaranteed to help here in general: a random projection of a set of vectors that are still
substantially collinear (cos~0.80) will produce expanded vectors that are ALSO substantially
collinear (random projections approximately preserve pairwise angles/distances, per the
Johnson-Lindenstrauss argument the Spoke-3 design note itself cites as the justification for why
expansion-then-threshold works -- but JL preserves distances, it does not manufacture separation
that was not there beforehand). k-WTA sparsification on TOP of a still-correlated expanded
representation could go either way:
- **Optimistic case:** k-WTA is a strongly nonlinear operation (a threshold/competition, not a
  linear projection) -- for two inputs with cos~0.80 but non-identical, expansion to a much
  higher dimension (`d_exp = 2-8x`) increases the ABSOLUTE number of dimensions where they
  differ even if the ANGLE is similar, and taking only the top-k=4-8 winners (a tiny fraction of
  d_exp) means two inputs need only differ in WHICH few coordinates win, not in overall angle,
  to get disjoint active sets. This is exactly the mechanism DG pattern separation is credited
  with in the literature (07-16 note A3: "two overlapping inputs become largely non-overlapping,
  very sparse output codes") and is precisely why the block-local-K resonator (K4/K8 HARD_PASS)
  worked on the substrate's existing near-orthogonal phasor codes.
- **Pessimistic case:** if the shared component (the 0.80 mean cosine) is not just correlated
  overall but specifically concentrated such that the TOP-k highest-activation coordinates of
  `z = whitened_slot_u @ E.T` are dominated by the shared component for every role (i.e., the
  shared direction, even though small in PCA variance share, projects onto a consistent handful
  of expanded coordinates that always win the top-k competition regardless of role), then k-WTA
  would select THE SAME winners for every role -- collapsing exactly like the raw (unwhitened)
  case did (`untrained_addr_distinct` argmax collapsing to a single bucket, MEASURED in the
  original STUCK_FLAT diagnostic). This is the "expansion swamps the signal" failure mode and
  would reproduce a DIFFERENT-LOOKING but MECHANISTICALLY IDENTICAL collapse to the original
  raw-cosine STUCK_FLAT failure, just one stage later in the pipeline.

**Cheap pre-check (run BEFORE the full training run, no training required, <1 minute of compute):**
For each of the 15 role query reps (train AND held-out, computed via the FROZEN encoder + fixed
`role_query` at random init, since `role_query`'s init is shared and not the variable under
test), compute the PCA-whitened `slot_u`, apply the fixed `E` + top-k sparsify at each candidate
`(d_exp, k)` grid point, and report:
1. **Active-set Jaccard overlap** between every pair of the 15 roles' top-k winner index sets
   (want: LOW overlap between roles across the board, not just train-vs-train).
2. **`untrained_addr_distinct`** -- the direct analog of the existing conditioning diagnostic's
   metric (`conditioning_diagnostic`'s `untrained_addr_distinct` field): how many of the 15
   roles route to a DISTINCT bucket under `bucket_of` pooling, with ZERO training (this is a
   pure geometry check, matching the existing cell's own diagnostic pattern, extended one stage
   further through expansion+sparsify+hash).
3. **Held-out-vs-train parity**: is `untrained_addr_distinct` for the 3 held-out roles
   comparably good to the 12 train roles (expected YES if the mechanism is truly role-agnostic;
   a NO here -- e.g. held-out roles systematically collapsing while train roles don't, which
   should be geometrically impossible since the fixed projection has no way to "know" which
   roles were designated train vs held-out -- would itself be a red flag worth investigating
   before spending the full training budget, since it would suggest a non-mechanism-related
   confound, e.g. degenerate held-out query sentences).

**Decision rule for the pre-check:** if `untrained_addr_distinct >= 12/15` (80%, matching the
HARD-PASS `held_addr_acc>=0.80` bar's own magnitude) at ANY point in the `(d_exp, k)` sweep grid
BEFORE any training, that is strong evidence the optimistic case holds and the full run is worth
the compute. If NO grid point clears roughly `8/15` (a lenient floor, well above the `addr_chance
~1` any-bucket-wins-by-luck baseline of order 1, and comfortably below the eventual HARD-PASS
bar so the pre-check does not need to be as strict as the trained result), treat that as an
early pessimistic-case signal and escalate `d_exp` further (16x, 32x) or reduce `k` before
committing to the full training run -- do not skip straight to declaring HARD-FAIL from an
untrained diagnostic alone (the existing conditioning diagnostic showed untrained separation is
informative but not dispositive: e.g. raw untrained_addr_distinct was low yet the WHITENED
untrained case already showed 4/6 separated before any training in the read-cond cell, so
training does add something beyond the bare geometry check -- the pre-check gates whether to
RUN, it does not replace the actual pre-registered bands).

**P_deflated reasoning:** Raw confidence that the DG-analog fixed-projection mechanism is
sound AS A GENERAL BRAIN-FAITHFUL PRINCIPLE is high (~0.80, inherited from the 07-16 note's own
biology calibration, itself already lit-scan-discounted). The SUBSTRATE-SPECIFIC question --
does k-WTA on a random expansion of THIS PARTICULAR whitened representation (cos~0.80 residual
collinearity, not the near-orthogonal synthetic phasors the block-local-K resonator was
certified on) preserve enough role signal to clear 0.80 held-out addressing accuracy -- is
genuinely unknown and is exactly the kind of "novel-synthesis mapping onto a new substrate"
case the calibration discipline caps at 0.50. Further discounted to **0.35** because: (i) the
residual 0.80 cosine after whitening is a WORSE starting point than the resonator's certified
near-orthogonal test bed, so the certified K4/K8 numbers do not transfer directly, only the
mechanism does; (ii) the honest pessimistic case above (shared-component-dominates-top-k) is a
real, structurally plausible failure mode, not a hypothetical one, since it is mechanistically
the SAME failure (shared-component-dominates) that caused the ORIGINAL raw-cosine STUCK_FLAT,
just relocated one stage downstream; (iii) no direct prior cell on this substrate has run this
exact expand+sparsify+hash pipeline on NL role reps specifically (the Spoke-3 design and
block-local-K resonator both validated the mechanism on different representations). The cheap
pre-check in this section exists specifically to resolve (ii)/(iii) BEFORE paying for the full
training run, which is the correct order of operations per the design-gate discipline
([[feedback-experiment-design-gate-can-fail-real-baseline-difficulty-on-before-full-run]]).

---

## 5. Orthogonal lever (flag, not required for this cell)

The forward-predictive encoder (LPC) run in flight (GPU, ~15h per the current BACKUP/session
state) may make frozen reps NATIVELY more separable (lower baseline query-slot cosine before any
whitening at all), which would help BOTH a learned key and a fixed projection -- these levers
compose, they do not compete. Once the MLM-v2-encoder fixed-projection cell above lands
(HARD-PASS, HARD-FAIL, or MIDDLE), the same `FixedDGAddressWM` mechanism should eventually be
re-run against the LPC encoder's reps once that checkpoint is available, to separate "does the
addressing MECHANISM generalize" (this cell's question) from "does a better ENCODER make
addressing easier regardless of mechanism" (a separate, not-yet-answerable question). Do not
conflate the two results when they land -- report which encoder each addressing result used.

---

## Substrate-product implications

- If `FIXED_DG_ADDRESS` HARD-PASSes: the product story becomes "the WM can bind role-filler
  content for roles it has NEVER been trained to address, using a fixed geometric mechanism, not
  a lookup table" -- this is the difference between a system that can only use a fixed,
  pre-enumerated vocabulary of slots/roles and one that can address NOVEL relational structure
  on the fly, which is the actual bar for "comprehension" this whole thread has been chasing
  (per the CURRENT FOCUS framing: comprehension = updating a pre-existing world model with
  genuinely new structure, not replaying memorized instances).
- If it HARD-FAILs with the pessimistic case confirmed (shared-component swamps the fixed
  projection too): that is a real, brain-consistent structural finding about THIS encoder's
  representational geometry, not a refutation of the DG-analog mechanism in general (which
  remains certified for the near-orthogonal resonator case and the page-routing design) -- the
  fix would then be either (a) a stronger conditioning step before the fixed projection (beyond
  plain PCA-whitening -- e.g. a supervised-on-TRAIN-ROLES-ONLY discriminative whitening that
  still leaves held-out roles untouched, since PCA-whitening itself is unsupervised and did not
  fully resolve the shared component), or (b) escalate directly to the LPC encoder (section 5)
  on the hypothesis that the representational problem is upstream of addressing entirely.
- Either way, do not claim "generalizing binding" from a HARD-PASS on TRAIN-role item-level
  generalization alone (the b3bc526ee result) ever again without ALSO clearing this held-out-
  ROLE bar -- that conflation is exactly what produced tonight's false confidence and is the
  reason this specific ablation ladder (CONTROL_B ground-truth-restricted lookup) exists.

## Calibration reasoning (P_deflated = 0.35)

See section 4 for the full reasoning. Summary: biology/mechanism confidence ~0.80 (inherited,
already lit-scan-discounted, from the 07-16 note); substrate-specific novel-synthesis mapping
capped at 0.50 per mandatory novel-synthesis cap; further discounted to 0.35 for (i) worse
starting collinearity than the resonator's certified test bed, (ii) a real structurally-plausible
pessimistic failure mode identified above, (iii) zero direct prior-cell precedent for this exact
pipeline on NL role reps. HARD-FAIL thresholds are the REUSED verbatim bands from the HARD-FAILED
cell (section 3) -- not loosened, not re-derived.

## Citations / context pointers (files, not summaries)

- `notes/research_learned_noise_robust_addressing_page_routing_2026-07-16.md` -- primary
  mechanism source (read in full for this plan; all external citations therein apply here by
  reference, not re-cited).
- `data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json` -- certified k=4/k=8
  sparse-resonator parameterization reused as the default k sweep.
- `notes/design_stage2_concept_encoder_spoke3_sparse_hippocampal_pattern_separation_one_shot_2026-07-02.md`
  -- certified 2x expansion + top-K~1% parameterization reused as the default d_exp sweep center.
- `experiments/exp_wm_addressing_heldout_role_warmstart_v1.py` -- the HARD-FAILED cell this plan
  forks; all bands, controls, split, construction reused verbatim.
- `experiments/exp_selective_overwrite_recall_nl_wm_readcond_v1.py` -- `ReadCondWM`,
  `Conditioner`, `_addr_logits`, `_role_reps`, `conditioning_diagnostic` -- classes/methods
  modified or reused by this plan.
- `notes/exp_dev_anisotropy_dg_pattern_separation_prewrite_v1_SMOKE_HARD_FAIL_2026-06-26.md`
  (via the 07-16 note's own B3 section) -- the prior "geometry works, recall doesn't" pairing-
  mismatch caution this plan's pre-check (section 4) exists specifically to catch early.
