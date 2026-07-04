# Stage 1 phase-diagram: genuine open questions after the cross-term collapse

**Filed 2026-07-04 by Director. Parallel to the encoder rescue (USER asked to advance phase-diagram in parallel).**
All claims below verified off-disk against `data/substrate_index/{math,meta}/atoms.jsonl`, the Probe-1 re-audit note, the P16 prereg, and the cell primitives. Sources cited inline.

---

## 0. The one lesson that reshapes everything (verified off-disk)

Two distinct facts fell out of today's collapse, and BOTH constrain future design:

1. **Unpaired max/range-over-arms discriminators manufacture phantom cross-terms** (memory `feedback_paired_trials_mandatory_for_arm_comparison_discriminators_2026-07-04`; commit `642f6394f`). At TR=100 the sampling-noise range of k arms is ~0.10-0.13; the whole "axis moderates CLEANUP_MECHANISM" family read that noise as signal.

2. **The 3 cleanup mechanisms are READOUT-DEGENERATE for the index-argmax readout.** Paired TR=400 (shared salt) gives mechanism range **EXACTLY 0.000000 on all 36 BUNDLED cells (z=-8.88)** — bit-identical accuracy (atom `MATH Probe 1 SPLIT MEASURED_MECHANISM`, commit `bf4408f2e`). The chain readout is `ci = argmax_j Re(Q_clean @ props[j].conj())`; iterative_cosine, modern_hopfield, soft_energy all leave the argmax index unchanged at the cell's beta/alpha, so accuracy (a function of the index alone) is mechanism-invariant BY CONSTRUCTION.

**Consequence for the whole program:** any new cell that (a) uses the index-argmax readout AND (b) compares cleanup mechanisms will find zero mechanism effect **by construction**, not by physics. The mechanism axis is dead for this readout. This is the single most important design constraint below.

---

## 1. Reconciliation table — REAL vs DEMOTED vs UNTESTED

Legend: **arm-cmp?** = is the discriminator a max/range/interaction *over arms* (mechanisms/storage) on independent draws? That is the artifact-prone class.

### REAL / SURVIVED (main effects; artifact-immune or paired-clean)

| Claim | Tier / evidence | arm-cmp? | Verify note |
|---|---|---|---|
| **STORAGE main effect** (SHARDED >> BUNDLED readout quality) | T2 SPLIT survivor of P1; median gap 0.935/0.93/0.92, 36/36 pairs positive, 3-seed | Paired, huge, real | `MATH Probe 1 SPLIT survivor`. **Caveat: SHARDED ceiling-saturated (=1.0 everywhere in tested grid) → gap is a LOWER bound; the boundary where it collapses is UNMAPPED.** cert delta 0 (re-confirms atom #56). |
| **P16 SHARDED cliff (M x corr) at N=512, F=1** | MM_STANDARD, 3-seed FULL, `cliff_amp=0.907`, **cv=0.023** | No (single-arm shape metric) | `probe_16_SHARDED_cliff_MN_interpolation`. Corr sweep 0.80->0.90 drives acc 0.99->0.13; M sweep 4000->5600 barely moves it. **Corr-dominated, M-flat — at ONE (N,F) point only.** Artifact-immune template. |
| **P9v2 N x L additive composition (BUNDLED)** | T2 BOUNDED_NULL, 3-seed FULL, cross-seed sign-consistency audit | No (additive-residual, null-gated) | `MATH Probe 9 v2 BOUNDED_NULL`. 0/12 cells sign-consistent at 0.10; per-seed firings are codebook-draw variance. **Real composition rule: N and L compose additively at BUNDLED near-capacity.** The model for "how to test composition honestly." |
| **L main effect on capacity** (P12) | filed CHAIN_GRADE, cv=0.049, 8.27x margin, 3/3 HP | No (single-arm, accuracy vs L) | `probe_12_L_marginal_effect`. Main effect is real & artifact-immune. **FRAMING CONTESTED:** filed as "distinct 5th axis"; the 07-03 backup (Fix#28 #16) argued L is a REGIME_EXTENSION of atom #3, and L=1->16 spread 0.875 is theory-trivial SNR decay. Needs reconciliation, but NOT part of the collapse. |
| **5 main-effect physics laws** (SCALE_FREE, TOPOLOGY_FREE=F, STORAGE_STRATEGY, M-scaling, ALGEBRA_SCALES) | prior CG_META atoms | mostly no | Main effects survive. **Flag:** `PHYSICS_LAW_cleanup_mechanism_M_scaling` was "CONFIRMED via Probe 1 [cross-term] evidence" — that support is now gone; the M-scaling *main* effect (acc vs M at fixed mechanism) stands but should be re-cited without the fallen cross-term. |
| **M-sweep = a real 5th sweep dimension (codebook M)** | established 2026-07-03 | n/a | Real as an *axis*; but see UNTESTED below — the *comprehensive M-sweep experiment* as proposed would re-manufacture the artifact. |

### DEMOTED (mechanism cross-terms = unpaired TR=100 noise)

| Claim | Was | Now | Verify note |
|---|---|---|---|
| **P1 STORAGE x CLEANUP** mechanism-moderation | CHAIN_GRADE_META (headline CG) | **DEMOTED to noise-floor** (CG -1) | `MATH Probe 1 CG_META cross-term DEMOTED`, `bf4408f2e`. Paired TR=400 range=0. BUNDLED "signal" = binomial noise; SHARDED "collapse" = ceiling-vacuous. |
| **P1 MM confirmatory replication** ("real regime-cross-term not artifact") | MM_STANDARD | **DEMOTED** | Same commit. |
| **P8 F(ALGEBRA) x CLEANUP** moderation | MM_STANDARD | **DEMOTED to MIDDLE_BAND** | `MATH Probe 8 DEMOTION`; 5-FULL-seed cv=0.1797 > 0.15; z=0.40 vs binomial-only null. Unpaired salt. |
| **P6v2 F x CLEANUP, P7v2 N x CLEANUP** | MM_TENTATIVE / MIDDLE_BAND | **artifact (directional; per re-audit)** | Never promoted (MIDDLE_BAND). P6 `max_per_F_mech_var=0.15` ~= noise floor 0.135; P7 `0.07` well below. Confirm-and-close, low stakes. |
| **P4 "STORAGE moderator is CLEANUP_MECHANISM-specific"** clause | MM_STANDARD | **clause DEMOTED** (depends on the fallen mechanism cross-term) | `probe_4_STORAGE_x_N_non_interaction`. The "STORAGE x N is a *non*-interaction" half is separable (see caveat below); the "mechanism-specific" conclusion is dead. |
| Composite `PHYSICS_LAW_STORAGE_UNIQUELY/MASTER_MODERATOR` | never filed (was being framed toward) | **never valid; do not file** | Multiple 07-03 amendments already killed it. |

### UNTESTED / OPEN (the genuine frontier — Section 3)

| Question | Status |
|---|---|
| Where does the STORAGE advantage COLLAPSE (its regime boundary), PAIRED and non-vacuous? | **UNTESTED** — P4 measured it with SHARDED pinned at ceiling (vacuous). Top experiment. |
| Does P16's corr-dominated / M-flat cliff GENERALIZE across N and F? Single collapse variable? | **UNTESTED** — P16 is one (N=512,F=1) point. |
| Do the surviving main-effect laws compose ADDITIVELY (like P9) or with genuine cross-terms, PAIRED/null-gated? | **UNTESTED** off the SHARDED cliff-drivers (corr x M x F). |
| Comprehensive M-sweep cleanup-family capacity diagram ("blocked on USER") | **UNTESTED and, as designed, would RE-MANUFACTURE the artifact** — see Section 4. |
| Can the mechanism axis be resurrected with a NON-argmax (continuous/confidence) readout? | **UNTESTED** — the only non-vacuous path for the mechanism axis. Speculative. |

---

## 2. Two saturation caveats that make the "survivors" partly untested

- **STORAGE gap is ceiling-pinned.** SHARDED=1.0 everywhere in P1's grid; BUNDLED~0.09. So "gap ~0.93" and "gap is N-invariant (P4)" are both measured in a regime where SHARDED cannot move. The gap's *true* size and its *scaling* are only measurable where SHARDED is in-band — i.e., near the cliff P16 found. This is precisely what makes Experiment 1 non-redundant.
- **"0/36 mechanism variance at SHARDED" carries no weight** — it is saturation (acc=1.0), not evidence of mechanism collapse.

---

## 3. Ranked genuine open questions (P_deflated; lit-scan penalty applied, novel-synthesis capped at 0.50)

1. **STORAGE-advantage regime boundary, PAIRED across corr x F x N** — *does the #1 surviving law have a regime where it breaks, and does the break scale?* **P_deflated 0.75** that we produce a clean boundary map (high value regardless of shape); **0.45** that the gap collapses onto a single load-factor curve (data-collapse). Paired design is the *natural* comparison (SHARDED vs BUNDLED, shared salt). **TOP — Experiment 1.**

2. **SHARDED-cliff generalization + corr x M additive-composition across (N, F)** — *does P16's one-point cliff law generalize, and do corr & M compose additively (P16 H1) or with a genuine M/N cliff-ratio cross-term (Kanerva SDM, H2)?* Single-arm, additive-residual + binomial-null discriminator (P9 method), artifact-immune. **P_deflated 0.50.** **Experiment 2.**

3. **N x L / N x corr additive composition at SHARDED near-capacity** — extend P9's BUNDLED additivity finding to the SHARDED cliff regime. **P_deflated 0.45.** Folds into Exp 2's method; lower marginal value.

4. **Comprehensive single-mechanism M-sweep capacity diagram** — the "blocked on USER" one, *stripped of the mechanism-family comparison.* **P_deflated 0.35** for novel yield beyond P16 (which already showed M-flat near one cliff; risk of saturation-vacuous unless targeted at high M/N). See Section 4.

5. **Mechanism-axis resurrection via non-argmax readout** — continuous cosine-quality / confidence readout so mechanisms *can* differ. **P_deflated 0.35** (novel-synthesis, uncertain the mechanisms differ even then). The only non-vacuous mechanism path; not top-2 but the right long-term move if the mechanism axis matters for M3 routing.

---

## 4. FLAG: the M-sweep, as proposed, would re-manufacture the artifact

The parked proposal (`project_stage1_phase_diagram_gaps_candidate_K_sweep`) is:
> "Sweep M x N x corruption x **mechanism (4 families)** ... establish `PHYSICS_LAW_cleanup_mechanism_M_scaling`."

The **mechanism (4 families)** axis is exactly the READOUT-DEGENERATE comparison that just collapsed. Under the index-argmax readout, the 4 families produce identical accuracy by construction → the "which mechanism wins as M grows" result would be pure unpaired noise, a fresh phantom cross-term. **Do not run it as designed.** Two valid redesigns:
- **(a) single-mechanism capacity map:** drop the family comparison; sweep M x N x corr for ONE mechanism (modern_hopfield). This is a clean main-effect diagram — but P16 already shows M-flat near the N=512 cliff, so it is only worth running where M/N approaches the Kanerva cliff-ratio (high M relative to N). Folds into Experiment 2.
- **(b) non-argmax readout:** keep the family comparison but change the readout to a continuous quality metric (mean cosine to target, or top-1 margin) that is NOT argmax-invariant. This is open question #5, a separate arc.

**Verdict: the comprehensive M-sweep is NOT worth running in its parked form. Its salvageable content is absorbed into Experiment 2 (option a); its mechanism-comparison ambition needs option (b), a different arc.**

---

## 5. Experiment 1 (TOP, dispatchable) — PAIRED STORAGE-advantage regime-boundary map

**Anchor:** `stage1_regime_probe_18_storage_advantage_boundary_paired_v1`
**Primitive:** reuse `eval_phase_point(...)` from `_stage1_regime_probe_16_..._core.py` (already SHARDED+BUNDLED capable via the `storage` arg; `run_chain(storage, ...)`).
**Question:** The STORAGE main effect is real but only measured with SHARDED pinned at ceiling. Where does the SHARDED>>BUNDLED advantage COLLAPSE, and does the boundary move with corr, F, N? Does the paired gap `Delta = acc_SHARDED - acc_BUNDLED` (per shared-salt cell) scale, or is it a single load-factor surface?

### Paired design (MANDATORY — this is an arm comparison)
For each (N, F, M, corr, seed) cell: draw items + corruptions ONCE from `gen(seed*100003+salt)`, then evaluate BOTH `storage="SHARDED"` and `storage="BUNDLED"` on the **same** items + corruptions. `Delta = acc_S - acc_B` is a within-item paired difference.
- **PAIRING_VALID pre-flight gate (exp_dev must verify at smoke):** confirm SHARDED and BUNDLED at a fixed salt consume identical antecedent indices + corruption masks. Current `eval_phase_point` builds rules storage-independently (`build_rules` before `run_chain`) but the two `run_chain` branches may consume the generator differently before the corruption draw. **Required cell change:** refactor so items+corruptions are drawn first (storage-independent) and passed to both storage layouts; assert `pre_cleanup_query_S == pre_cleanup_query_B` bit-for-bit. If the assert fails, pairing is invalid and the cell must not ship.

### Grid (straddle the SHARDED cliff at each (N,F) so SHARDED is IN-BAND, not pinned)
- N in {512, 2048, 8192}; F in {1, 4}; MECH = modern_hopfield (fixed — no mechanism comparison); L=2; M chosen per (N,F) so M/N is near P16's cliff-ratio (start M=4800 at N=512,F=1; exp_dev empirically re-brackets M per (N,F) at smoke, as P16 did).
- **corr grid per (N,F): an adaptive 5-point bracket straddling the SHARDED cliff** (SHARDED has cells >=0.90 AND cells <=0.30). Seed bracket for N=512,F=1: {0.75, 0.80, 0.85, 0.875, 0.90}. exp_dev re-brackets per (N,F) at smoke to guarantee straddle (the cliff moves with N,F — that IS the finding).
- Positive control (Gate D): SATURATION_PC arm (iterative_cosine, M=800, N=2048, corr=0.20, SHARDED) acc>=0.95.

### Discriminators (all within-cell / paired; NONE is a max-over-noisy-arms)
- `delta[N,F,corr]` = acc_SHARDED - acc_BUNDLED (paired).
- `boundary_corr[N,F]` = the corr at which `delta` crosses below 0.5 (linear-interp) = the STORAGE-advantage collapse point.
- `delta_scales_with_N` = range over N of `boundary_corr[N,F=1]` (does the boundary move with N?).
- `delta_scales_with_F` = range over F of `boundary_corr[N=512,F]` (does the boundary move with F? — Frady Resonator predicts YES).
- `collapse_test`: after rescaling corr by a candidate load variable u=f(M,F,N), does `delta(u)` collapse onto one curve across (N,F)? Report R^2 of the collapsed fit.

### Data-driven noise-floor null (per discipline, even though paired)
Because `delta` near the cliff is a difference of two in-band binomials, gate `boundary_corr` and the interaction ranges against a MC binomial null: for each cell draw acc_S ~ Binom(TR, p_S)/TR and acc_B ~ Binom(TR, p_B)/TR (paired: shared latent, so common noise cancels), MC the same boundary/range statistics (NDRAW=2e5). HARD-PASS requires observed > q95 of the null.

### Bands
- **HARD-PASS (STORAGE law has a mapped, moving boundary):** at 3-seed FULL, per (N,F) `boundary_corr` well-defined (cliff straddled) AND (`delta_scales_with_N` > null q95 OR `delta_scales_with_F` > null q95) AND cross-seed cv(boundary_corr) < 0.15.
- **HARD-PASS-NULL (boundary is scale-free — a strong, clean result too):** boundaries well-defined at every (N,F) but `delta_scales_with_*` <= null q95 across all → "STORAGE advantage collapses at a FIXED corr independent of N,F" = scale-free boundary. This is a genuine finding, file as BOUNDED_NULL (like P9), not a failure.
- **MIDDLE_BAND:** interaction between null q95 and cv 0.15, or 1/2 axes fire.
- **HARD-FAIL (design bad, no atom):** any (N,F) fails to straddle the cliff (SHARDED all >0.9 or all <0.3) → bracket wrong, re-author; OR PAIRING_VALID assert fails; OR SATURATION_PC < 0.95; OR cardinality mismatch.

### CARDINALITY_OK
- SMOKE: 3 N x 2 F x 5 corr x 2 storage = 60 paired evals + 1 PC = 61; TR=40. `EXPECTED_N_UNITS_SMOKE=61`.
- FULL: 3 N x 2 F x 5 corr x 2 storage = 60 + PC = 61; TR=200 (raised from 100 — the paired difference near the cliff needs the tighter floor; cells run ~3-11s so cost is trivial). `EXPECTED_N_UNITS_FULL=61`. Verdict emits `HARD_FAIL_CARDINALITY_BREACH` on mismatch.

### Seeds / SMOKE-then-FULL / queue / ETA
- Seeds {7,13,19}; MM_STANDARD requires 3-seed cv<0.15 (arc-continuation vs arc-closure discipline).
- SMOKE: 1 seed (7), TR=40, local_cpu_queue (SMOKE-only-local-cpu, USER-LOCKED). ~5-15 min wall. Gate = infra + PAIRING_VALID + PC + straddle (NOT on HP firing — null-hypothesis smoke discipline).
- FULL: 3 seeds, TR=200, ~61 pts/seed; est ~10-20 min/seed. Route via Orchestrator (GPU once-per-stage or remote_cpu). Total FULL wall ~30-60 min.

---

## 6. Experiment 2 (second) — SHARDED-cliff generalization + corr x M additive-composition

**Anchor:** `stage1_regime_probe_17_sharded_cliff_generalization_corr_x_M_v1`
**Primitive:** same `eval_phase_point`, SHARDED single-arm.
**Question:** P16 mapped the cliff at ONE (N=512, F=1) point: corr-dominated, M-flat, near-additive. Does that generalize? And is the corr x M interaction genuinely additive (P16 H1) or is there a real M/N cliff-ratio cross-term (Kanerva SDM / Cuckoo load-factor, P16 H2) once you look across N and F?

### Design (single-arm SHARDED — no arm comparison; discipline satisfied via null-gate, not pairing)
- N in {512, 2048}; F in {1, 4}; MECH=modern_hopfield; L=2; TR=200 FULL / 40 SMOKE.
- Per (N,F): M grid {0.6, 0.8, 1.0, 1.2}x the cliff-ratio M*(N,F) (exp_dev brackets M*); corr grid straddling the cliff (5 pts, adaptive as in Exp 1).
- Positive control: same SATURATION_PC arm.

### Discriminator (P9-style additive residual, NOT max-over-arms)
For each (N,F) SHARDED (M x corr) grid:
- Fit the 2-way additive model acc ~ a(M) + b(corr); `resid[M,corr]` = observed - additive-fit.
- `max_abs_resid_in_band` over cells in [0.30,0.95] = the genuine M x corr cross-term size.
- **Cross-seed sign-consistency audit (the P9 lesson):** a residual counts only if its sign is consistent across all 3 seeds at |resid|>=0.10; per-seed firings that flip sign are codebook-draw variance, not cross-term.
- Binomial extreme-value null: MC `max_abs_resid` under acc~Binom(TR,p_cell)/TR; HARD-PASS requires observed > q95.

### Bands
- **HARD-PASS H2 (genuine M x corr cross-term / cliff-ratio):** sign-consistent `max_abs_resid_in_band` > 0.10 AND > null q95 at 3-seed FULL, cv<0.15. Atom: `EMPIRICAL_SHARDED_CLIFF_M_x_CORR_CROSS_TERM_v1` (Kanerva cliff-ratio supported).
- **HARD-PASS H1/BOUNDED_NULL (laws compose additively — the P9-grade result):** 0/cells sign-consistent at 0.10, `max_abs_resid` <= null q95 → corr and M compose additively across (N,F); P16's one-point finding generalizes. File BOUNDED_NULL (strong, like P9).
- **Also reports** `cliff_amp[N,F]` and `boundary_corr[N,F]` → generalizes P16's cliff map to (N,F) for free.
- **MIDDLE_BAND / HARD-FAIL:** as Exp 1 (straddle fail, PC fail, cardinality).

### CARDINALITY_OK / seeds / ETA
- FULL: 2 N x 2 F x 4 M x 5 corr = 80 + PC = 81; `EXPECTED_N_UNITS_FULL=81`. SMOKE: 2x2x2x3=24 + PC = 25.
- Seeds {7,13,19}; SMOKE local_cpu; FULL via Orchestrator; ~15-30 min/seed FULL.

**Sequencing:** Exp 1 first (higher value, maps the #1 law's boundary). Exp 2 second (generalizes P16 + settles composition). Both reuse the P16 primitive, so exp_dev authoring is mostly grid + paired-refactor + discriminator, not new mechanism. Both are independent of the encoder rescue (different files entirely).

---

## 7. What NOT to do (artifact-re-manufacture tripwires)

- **No** cleanup-mechanism comparison under the index-argmax readout (READOUT-DEGENERATE → guaranteed phantom).
- **No** max/range-over-arms discriminator on independent salts (the collapsed family).
- **No** interaction claim from a grid where one arm is ceiling- or floor-pinned (saturation-vacuous).
- **No** promotion from single-seed SMOKE (arc-continuation != arc-closure).
- **No** re-run of P6v2/P7v2 FULL to "confirm" mechanism cross-terms — they are already MIDDLE_BAND and the paired TR=400 result proves the family is noise. Close them by citation, don't spend GPU.

---

## 8. Intuitive summary (what this means, why it matters, where we are)

Today a big chunk of the "substrate physics regime map" turned out to be a measurement mirage. We had been excitedly reporting that the *choice of cleanup mechanism* starts to matter in certain regimes — a whole family of "cross-term" findings, one of them our headline chain-grade result. When we finally compared the mechanisms on the *exact same* test items instead of independent random ones, the differences vanished to *exactly zero*: the mechanisms are provably identical for the kind of readout we use, and every prior "difference" was just the wiggle of random sampling that we mislabeled as signal. That is a humbling but clean result, and we filed the discipline (paired trials or a proper noise-floor null are now mandatory) so we never make this specific mistake again.

The good news is that the *real* physics survived intact and is actually more interesting than the mirage. The single biggest, most robust law — that storing rules "sharded" (one slot each) crushes storing them "bundled" (all superposed), by a 0.93 accuracy gap — is rock solid. And we discovered the sharded scheme has a sharp *cliff*: as corruption rises past ~0.85 it falls off a shelf from near-perfect to near-zero, while the codebook size barely matters. But we only measured that cliff at a single setting, and we measured the storage gap only where the sharded side was pinned at 100%, so we've never actually seen *where the storage advantage breaks down*. That is the frontier.

So the two experiments I'm handing to the cell-author are exactly the honest versions of the questions we thought we were answering: (1) map where the storage advantage collapses, comparing the two schemes on *identical* items so the comparison can't lie, and see whether that boundary moves as we change dimension and fan-out; and (2) check whether the cliff we found at one point generalizes, and whether corruption and codebook-size combine cleanly (they add up) or fight (a genuine interaction) — using a residual-and-noise-floor test, not an arm-max, so it can't manufacture a phantom. I also flagged the parked "sweep every cleanup mechanism against codebook size" idea as a trap: run as written it would rebuild the exact artifact we just killed, because those mechanisms are identical under our readout. Its useful half (single-mechanism capacity) is absorbed into experiment 2; its ambitious half needs a completely different, continuous readout — a separate arc for later.

Where we are: Stage 1's phase diagram is smaller but far more trustworthy than it was this morning. We traded a pile of shaky cross-terms for a short list of bomb-proof main effects plus two sharp, dispatchable questions about the boundaries of the one law that matters most. Both experiments are cheap (minutes of compute), reuse an existing cell, run in parallel with the encoder work, and — critically — are built so they *cannot* re-manufacture the mirage.

---

## Provenance
- Off-disk atoms: `data/substrate_index/math/atoms.jsonl` (Probe 1 SPLIT survivor / MEASURED_MECHANISM / cross-term DEMOTED; Probe 8 DEMOTION; Probe 9 v2 BOUNDED_NULL; Probe 16; Probe 4; Probe 12).
- Commits: `bf4408f2e` (Probe 1 re-audit demote/split), `642f6394f` (paired TR=400 definitive), `379ca7cde` (TR=400 revival).
- Re-audit note: `notes/director_preliminary_probe1_cross_term_noise_floor_reaudit_2026-07-04.md`.
- Primitive + template: `experiments/_stage1_regime_probe_16_SHARDED_cliff_MN_interpolation_v1_core.py`; prereg `preregs/2026-07-04_stage1_regime_probe_16_SHARDED_cliff_MN_interpolation_v1.md`.
- Memory: `feedback_paired_trials_mandatory_for_arm_comparison_discriminators_2026-07-04`, `project_stage1_regime_map_of_CG_META_axes_USER_2026-07-03`, `project_stage1_phase_diagram_gaps_candidate_K_sweep_2026-07-03`.
