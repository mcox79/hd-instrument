# exp_dev hand-off — research: codebook design-space generalization (FHRR bundle exact order-statistic)

**Filed:** 2026-07-06 by research (sub-agent context; main thread/orchestrator will dispatch
the exp_dev wrapper).

**Trigger:** `notes/research_codebook_design_space_generalization_2026-07-06.md` — Director's
cadence gap-fill drill asking whether the just-landed RNS exact decode-margin self-prediction
(`rns_subblock_margin_exact_prefactor_v2`, CHAIN_GRADE candidate) generalizes across the
substrate's OTHER codebook families. Answer: yes, in closed form, to the FHRR/HRR superposition-
bundle cleanup-memory family — verified this drill via a direct numeric recompute against 3
ALREADY-LANDED cells (`exp_bundle_capacity_theory_cpu_v1`, `exp_bundle_capacity_largeN_gpu_v1`,
`exp_bundle_capacity_cliff_gpu_v1`) and 10 measured data points spanning N=1024 to N=16384: max
K_crit deviation 3.0% (vs the currently-used `N/(2 ln N)` asymptotic law's 15-58% deviation),
pointwise accuracy RMS <0.3% on a 6-point K-sweep. Read the research note in full before
authoring — it has the derivation, the full numeric-verification tables, and the reasons this
family was chosen over the two runner-up candidates (GSBC one-factor generalization; Family-A
library-ization).

**Pause state:** ACTIVE (`data/orchestrator_paused.flag` absent — verified this session).

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS +
mechanism/bands only. exp_dev designs ALL of: exact N/K/V grid points, seed count, exact
threshold bands, which of the 3 target files gets the new arm first, whether to widen the
existing files in place or author one new standalone cell, queue choice, ETA, smoke/FULL
profiles.

---

## What the research found (one paragraph)

The substrate's FHRR/HRR bundle-cleanup decode arithmetic (`B = sum_k(roles_k * book[fidx_k])`,
unbind `rec = B * roles_q.conj()`, cleanup `argmax(Re(rec @ conj(book).T))`) reduces, by the same
per-dimension i.i.d.-random-phase-decorrelation fact that made the RNS codebook's margin exactly
derivable, to the identical "elevated-mean true score vs i.i.d. zero-mean competitor scores"
order-statistic detection problem — with `sc[true] ~ N(N, N*(K-1)/2)` and `sc[competitor] ~
N(0, N*K/2)` for each of V-1 i.i.d. competitors. `P_correct = E_x[Phi(x/sqrt(N*K/2))^(V-1)]`,
`x ~ N(N, N*(K-1)/2)`. This is a genuinely new derivation for this codebook family (not a copy-
paste of the RNS formula — different mean/variance terms, derived from the bind/unbind
arithmetic, not asserted) and it fits the substrate's own already-measured data far tighter than
the currently-reported `N/(2 ln N)` asymptotic law, particularly at production scale (N=8192,
16384) where that law is 45-58% off and `exp_bundle_capacity_largeN_gpu_v1` currently sits at
only MIDDLE_BAND, not HARD_PASS.

---

## Anchor candidates (rank-ordered)

### 1. FHRR bundle-capacity exact order-statistic arm (PRIMARY — the cell this hand-off is for)

- **Anchor pointer:** `notes/research_codebook_design_space_generalization_2026-07-06.md`, Sec. 4
  ("THE FHRR/HRR EXACT-ORDER-STATISTIC CELL") for the full construction, arms, and pre-registered
  bands; Sec. 1 ("Family B") for the derivation and the already-run numeric verification tables
  this hand-off's bands are calibrated against.
- **Substrate-product reading:** upgrades the substrate's self-knowledge of its own FHRR bundle-
  capacity boundary from a loose asymptotic law to a precise, verified prediction, across the
  single most load-bearing codebook family on the substrate (bundling underlies `binding.py`,
  `memory.py`, `multi_hop.py`, `generation.py`). Unlike the RNS case (already HARD_PASS before
  its own tightening), the highest-value target here (`exp_bundle_capacity_largeN_gpu_v1`) is
  CURRENTLY only MIDDLE_BAND (45-58% deviation) at production N — this is a candidate to close
  an open gap, not just sharpen a passing one.
- **Tier hint:** cheap. The new arithmetic (`pred_acc_exact`/`kcrit_exact`, scipy `norm.cdf`/
  `quad`, same numerical approach as the already-landed RNS sibling arm) is ~25-35 new lines,
  reusing each target file's `cphasor()`/`kcrit()`/binary-search machinery verbatim. CPU for
  `exp_bundle_capacity_theory_cpu_v1`; GPU for `exp_bundle_capacity_largeN_gpu_v1` and
  `exp_bundle_capacity_cliff_gpu_v1` (matching their existing cost profile — low minutes).
- **Why now:** directly parallels a just-landed CG candidacy (same order-statistic family,
  independently re-derived and independently re-verified against a different set of cells this
  drill); recommend `exp_bundle_capacity_largeN_gpu_v1` first since it is the currently-open
  (MIDDLE_BAND) target where tightening is most consequential.
- **Construction summary** (exp_dev owns exact params): add `pred_acc_exact(N,K,V)` (Sec. 4 of
  the research note has the exact docstring/formula) and `kcrit_exact(N,V)` (binary search on K
  for `pred_acc_exact >= 0.9`, reusing the existing binary-search loop shape). Report a
  `theory_exact` arm alongside the existing `theory_asymptotic` (`N/(2*ln(N))`, kept as a live
  control) and `measured` arm. Do NOT touch the measurement machinery (`cphasor`, `run()`,
  `kcrit()`'s empirical binary search) — purely additive.
- **Bands (from the research note, Sec. 4):** HARD-PASS: `theory_exact` K_crit deviation <=5% at
  every tested N on a FRESH FULL/re-landed measurement AND >=3x tighter than `theory_asymptotic`
  at N>=8192 AND cliff_gpu pointwise accuracy RMS (fresh K-sweep) <=1%. HARD-FAIL: deviation >15%
  at any N, or fails the relative-improvement margin vs the asymptotic law. MIDDLE: beats the
  asymptotic law's tightness but doesn't reach the <=5% bar. P_deflated=0.50 (capped novel-
  synthesis per role discipline, despite this drill's own near-perfect retrospective fit — see
  the research note's Sec. 4/CITATIONS for why the cap is kept, including an external-lit-scan
  tool outage this round that could not live-verify supporting citations).

### 2. (Deferred, NOT this cell) Family-A library-ization — reuse `pred_acc_exact` across the 5 other RNS-family cells

- **Anchor pointer:** `notes/research_codebook_design_space_generalization_2026-07-06.md`, Sec. 1
  ("Family A") + Sec. 3 (why this is ranked below the FHRR cell).
- **Substrate-product reading:** cheap infrastructure reuse (NOT a new derivation) — the just-
  landed RNS exact-prefactor formula applies unmodified to `exp_math_rns_add_chain_v1`,
  `exp_math_rns_multiply_star_v1`, `exp_math_rns_subtract_compare_v1`,
  `exp_generation_decoder_rns_crt_highvocab_v1`, and `exp_multihop_router_crt_residue_addressed_v1`
  at their own `(m, sb, sigma)` operating points, replacing each cell's currently-informal
  "sb >> m, collision-free" reachability argument with the exact number.
  - **Tier hint:** trivial per-cell (each already has the phasor construction; adding the formula
    is a few lines per file).
  - **Why now / why deferred:** lower research novelty than anchor #1 (same formula, no new
    derivation) — a good follow-on cadence item, not this cycle's recommendation.

### 3. (Deferred, NOT ready to spec) GSBC one-factor equicorrelated generalization

- **Anchor pointer:** `notes/research_codebook_design_space_generalization_2026-07-06.md`, Sec. 1
  ("Family D") — the one-factor/equicorrelated Gaussian order-statistic route (Dunnett-Sobel /
  Vasicek-style common-factor conditioning) is a standard, well-established closed form
  (confirmed by lit-scan, though not live-verified this drill due to a tool outage), and the
  GSBC block-local codebook's measured mean pairwise correlation ("cone" ~0.5,
  `data/exp_generation_decoder_gsbc_native_blocklocal_v1`) is a plausible fit.
- **Substrate-product reading:** would give the generation/language backbone (GSBC block-local
  codes) the same exact-self-margin-prediction property, if the equicorrelation assumption holds.
- **Tier hint:** needs a PREREQUISITE check first (is the per-pair correlation distribution
  roughly homogeneous/exchangeable, as the one-factor model assumes, or does it have real
  semantic/heterogeneous structure that the model would miss?) before a cell can be meaningfully
  specified — genuinely not ready yet.
- **Why deferred:** the research note explicitly ranks this below anchor #1 for today's cycle
  because of this unresolved prerequisite; flagged as the natural SECOND research drill, not an
  exp_dev cell yet.

---

## Context pointers (pointers, not summaries)

- `notes/research_codebook_design_space_generalization_2026-07-06.md` — the PRIMARY source for
  this hand-off; full derivation, numeric-verification tables (Sec. 1), cell spec (Sec. 4),
  pre-registered bands, and the full 5-family codebook inventory. Read this FIRST, in full.
- `notes/research_decode_margin_exact_prefactor_derivation_2026-07-06.md` — the parent RNS exact-
  prefactor derivation this drill extends; same order-statistic family, useful for comparing the
  two derivations' structure and the numerical-integration approach (`scipy.integrate.quad`,
  `mean +/- 8..12*std` window) this hand-off's cell should mirror.
- `experiments/exp_bundle_capacity_theory_cpu_v1.py`, `exp_bundle_capacity_largeN_gpu_v1.py`,
  `exp_bundle_capacity_cliff_gpu_v1.py` — the 3 target files; read in full before authoring
  (the research note already read them and quotes the exact `cphasor`/`kcrit`/`run` functions to
  reuse verbatim).
- `data/exp_bundle_capacity_theory_cpu_v1/metrics.json`, `data/exp_bundle_capacity_largeN_gpu_v1/metrics.json`,
  `data/exp_bundle_capacity_cliff_gpu_v1/metrics.json` — the already-landed measured data this
  drill's retrospective numeric check used; re-verify the same numbers before trusting the
  research note's table if any doubt.
- `experiments/exp_rns_subblock_margin_exact_prefactor_v2.py` (if already authored/landed) or
  `experiments/exp_rns_subblock_margin_selfcheck_v1.py` — the sibling RNS cell's exact-prefactor
  arm implementation pattern to mirror structurally (new function + widened report surface,
  measurement machinery untouched).
- `preregs/2026-07_bundle_capacity_theory_cpu_v1.md`, `preregs/2026-07_bundle_capacity_largeN_gpu_v1.md`,
  `preregs/2026-07_bundle_capacity_cliff_gpu_v1.md` — existing preregs for the 3 target cells,
  for context on their current smoke/FULL staging and cost profile.

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands already
  drafted in the research note (Sec. 4); exp_dev finalizes exact numbers/grid.
- Self-test per [[feedback-formula-selftests]] — include a closed-form sanity check (e.g.
  `pred_acc_exact` at K=1 with V small should approach the noiseless/near-1.0 regime; monotone
  decreasing in K) before any arm measurement.
- SMOKE local-only (USER-lock); FULL routes to `remote_cpu_queue`/GPU queue via Orchestrator
  (push harness-denied to exp_dev), matching the 3 target cells' existing dispatch pattern (CPU
  for `theory_cpu`, GPU for `largeN_gpu`/`cliff_gpu`).
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`.
- POST-SHIP REMOTE VERIFY via queue_add.sh exit code per [[feedback-ship-name-collision]].
- status_log entry per anchor with `plain_language` + `importance`.
- **Still monitor-not-control** (USER-locked, per the research note): this is a reporting
  refinement only — never a change to N, K, V, or any landed cell's stored config/artifacts.

## Autonomy declaration

exp_dev decides ALL of: which of the 3 target files gets the new arm first (research note
recommends `exp_bundle_capacity_largeN_gpu_v1` since it is the currently-MIDDLE_BAND highest-
value target), whether to widen each file in place (mirroring the RNS sibling cell's minimal-diff
style) or author one new standalone cell that consumes/extends all 3, exact N/K/V grid points for
a fresh FULL re-landing, seed count, exact quadrature method and integration window, exact 5%/15%
band placement in code, queue routing, ETA, smoke/FULL profiles. Anchor #2 (Family-A library-
ization) and anchor #3 (GSBC one-factor generalization) are explicitly DEFERRED — do not build
either this cycle without a fresh Director/Strategy go-ahead (anchor #3 in particular has an
unresolved prerequisite check named above).

---

## Filed by

research (sub-agent context), 2026-07-06, following the just-landed RNS exact-prefactor
derivation and this drill's own numeric verification of the FHRR/HRR bundle-capacity
generalization against 3 already-landed cells. Hand-off ready for exp_dev pickup (auto-discovered
on next emergency-refill scan of `notes/exp_dev_handoff_*.md` sorted by mtime, or explicit
dispatch).
