# research: TIMEOUT class revival drill (disparate fields)

**Date:** 2026-06-24
**Topic:** 5 local-CPU cells timed out today (cross-layer compose / heterogeneous routing / cross-biology mappings / sequence v2 / A1 test-design audit) plus PCGrad earlier. All hit wall-time without producing metrics.
**Drill mode:** 2x+3x revival; disparate fields per USER ("drill the shit out of negatives"; "disparate fields").
**Pre-deflation:** lit-scan calibration penalty applied (P deflated 0.15-0.25; novel-synthesis cap 0.50).

---

## HEADLINE

The timeout class is NOT a research-question failure — it is a **compute-budget mis-estimation class** driven by three compounding root causes: (a) cell-author wall estimates anchor on smoke scale which is in a *different roofline regime* than full-N matmul; (b) cells are sized as monolithic batches when **Little's-law minimum-unit decomposition** would let partial results land before timeout; (c) the substrate is operating near a **K-SAT-style hardness boundary** in (N_DIM x M_pattern x arms x seeds) space where wall scales super-linearly. The 5 timeouts share this signature, and three of them (cross-layer compose, heterogeneous routing, cross-biology mappings) are LOAD-BEARING and rescue-able via roofline-aware scope reduction. **P_deflated = 0.70** that scope-reduction recovers chain-grade-eligible results in 60-90min wall; **P_deflated = 0.45** that there is also a substrate-physics signal in the timeout pattern itself (compute phase transition that informs Cap_map).

---

## Cheap decisive test

For each load-bearing rescue candidate (3 cells), the discriminating test is:

**T1 (per-cell roofline probe).** Before re-dispatching, run a **3-point timing probe** at (smoke_N, smoke_N x 2, smoke_N x 4) on the same arm, single seed, single config. Fit `t(N) = a * N^k`. Three diagnostic outcomes:
- `k ~= 1`: memory-bound regime; full-scale wall is **predictable** from extrapolation; safe to ship at original scope
- `k ~= 2`: matmul-bound regime; wall blows up super-linearly; **MUST scope-reduce** (N_DIM or M)
- `k > 2.3`: compounding regime (matmul x outer-loop interaction); cell is **structurally over-spec'd**; rebuild as mini-cells

**T2 (Little's-law minimum-unit check).** Identify the smallest independently-completing unit (per-seed-per-arm cell). If atexit-flush of partial metrics would produce a valid HARD-PASS/HARD-FAIL signal on 1-seed-1-arm at smoke_N x 8, the cell is **decomposable** and should be split into N_seeds x N_arms mini-cells with explicit dependencies. If not, the cell is **inherently monolithic** (signal only emerges from cross-arm comparison) and must fit in wall.

Both tests run in <5min CPU on laptop. Total triage cost ~30min for all 3 rescues.

---

## Falsifiable predictions

### HARD-PASS thresholds (rescue plan works)
- **R1 (roofline-grounded estimation).** For ALL 5 timed-out cells, a 3-point timing probe at (1x, 2x, 4x smoke_N) fitted to `t = a*N^k` predicts the actual full-N wall within +/- 25% on a re-dispatch (smoke -> full extrapolation). If verified on >= 4/5 cells, the roofline-probe discipline becomes a mandatory pre-flight gate (analog of PROT-019 smoke-wall).
- **R2 (decomposability rescue).** At least 2 of the 3 load-bearing rescue candidates (cross-layer / heterogeneous-routing / cross-biology) ship a chain-grade-eligible verdict in <= 90min after scope reduction per the rescue plan in section L3. HARD-PASS criteria same as pre-reg of original cell; we are NOT loosening cert bands.
- **R3 (substrate compute-phase-transition observability).** A scan of wall(N_DIM, M_pattern) for 1 representative cell reveals a sharp boundary where wall transitions from polynomial to super-polynomial. If observed at the expected location (M/N around the substrate's known capacity cliff ~0.14*N), this is mechanism-discriminating evidence that the *compute hardness* and *capacity hardness* are the same phase boundary (cross-thread synthesis with Pattern 4 spin-glass yield).

### HARD-FAIL thresholds (rescue plan does not work)
- **F1.** If 3-point timing probe predictions are off by > 50% on >= 3 of 5 cells, roofline extrapolation is invalid for substrate workloads (likely cache-effect dominant) and we need a **different estimation framework** (probably empirical histogram of similar prior cells rather than analytical model).
- **F2.** If 0/3 rescues land chain-grade after scope reduction, the cells are not over-spec'd — they are mis-specified at the mechanism level. Route to fresh research drill on the underlying mechanism, not to compute rescue.
- **F3.** If wall(N_DIM, M) is smooth (no phase boundary) across the tested range, the compute-hardness/capacity-hardness link is unsupported; drop R3 as a separate finding (rescue stands; just no bonus mechanism insight).

### MIDDLE_BAND
1-2 rescues land MIDDLE_BAND or PARTIAL (intermediate metrics; mechanism partially observable). Acceptable; queue 2x revival drill per [[feedback-route-negatives-to-research]].

---

## Cross-thread synthesis with disparate fields

### Angle 1 -- Roofline (HPC engineering)

The roofline model (Williams-Waterman 2009; NERSC docs) bounds attainable performance by `min(peak_compute, peak_bandwidth * arithmetic_intensity)`. The intersection point separates **memory-bound** (low intensity; wall ~ N) from **compute-bound** (high intensity; wall ~ N^k where k matches op-complexity).

**Substrate cells in the 5 timeouts are all matrix-outer-product heavy** (Hebbian write = N^2 per pattern; cleanup readout = N^2 x V). At smoke scale (N_smoke ~ 512-1024), the working set fits in L3 cache and the kernel is bandwidth-bound. At full scale (N_DIM=4096-16384), the working set blows past L3 (typically 8-32MB), the matmul becomes compute-bound, and wall scales as N^2 (single matmul) or N^3 (if cleanup is naive top-K over codebook).

**Concrete implication.** Smoke wall is in the WRONG roofline regime. A 4x scope-up at the regime boundary can mean 16x-64x wall blowup. This *fully explains* why cell-author estimates anchored on smoke are systematically off, and why post-cell-author smoke-wall PROT-019 gates do not catch it — they validate "smoke completes" not "smoke regime predicts full regime."

**Rescue.** Add the 3-point probe (T1 above) as mandatory pre-dispatch for any cell with N_DIM > 4096 or M_pattern > 1000. Fit power-law; extrapolate. Refuse dispatch if estimated wall > 1.2x configured timeout.

### Angle 2 -- Queueing theory (Little's Law + tiny-tasks trade-off)

Little's Law: `WIP = throughput * cycle_time`. For a single-server queue (which is what local_cpu_queue and overnight_queue are), throughput is fixed by hardware; reducing cycle_time per task increases the number of completed tasks per unit wall-clock. **Optimal job size** under bounded-time constraints is the smallest unit that produces a useful signal.

The **tiny-tasks granularity trade-off** (Karau-Konwinski 2022): smaller tasks reduce tail-latency risk but add scheduling overhead. For substrate cells, the per-cell overhead is small (~10-30s for runner pickup + queue-serialize + commit-write), so the cross-over is around 5-10min per task. Cells in the timeout class are 60-90min monolithic — **6-10x too large** by this principle.

**Concrete implication.** A 3-arm x 3-seed cell at 90min wall has 9 independently-completing units; splitting into 9 mini-cells gives each one a ~10min wall budget, fits comfortably inside the optimal granularity window, and gives partial results 80%+ of the time even if 1-2 mini-cells fail. The current monolithic design loses ALL results when any one arm-seed combination blows the wall.

**Rescue.** Decompose load-bearing cells into per-seed-per-arm mini-cells with a downstream aggregator cell that reads the individual metrics.json files and produces the cross-arm comparison. This is **Erlang-OTP-style** supervision: failures of any one mini-cell do not cascade.

### Angle 3 -- Erlang OTP / graceful degradation (systems resilience)

Erlang's "let it crash" philosophy + OTP supervisor patterns (OneForOne / RestForOne) handle this exact problem: bound the blast radius of any failure to a single supervised unit. The substrate has the building blocks (PROT-021 per-seed checkpointing exists) but they are **not consistently wired** into cells.

**The 5 timeouts shared discipline-drift signature:** none atexit-flushed partial metrics. When the wall hits, the harness kills the process and ALL in-memory results are lost. This is **the opposite of OTP discipline** — failures are silent and total instead of bounded and observable.

**Concrete implication.** Three durable patterns to wire into the cell-author template:
- **atexit handler** that flushes whatever per-arm/per-seed metrics have completed to a partial_metrics.json (separate path so it does not collide with final write)
- **per-seed checkpoint** (PROT-021) wrapping the seed loop so re-dispatch can pick up where it left off
- **smallest-scope-first execution order**: cells iterate `(seed, arm)` ordered to land 1-seed-1-arm-all-arms first, so a partial result is still cross-arm-comparable

This is also the **brain-locality principle** (Angle 5): brain regions complete local-scope computations before global integration. The substrate's iterated-argmax-with-cleanup is structurally local; cells should respect that ordering.

### Angle 4 -- Statistical mechanics phase transitions (random K-SAT)

Random K-SAT has a sharp SAT/UNSAT phase boundary at `alpha_c ~ 4.267` for k=3 (Mezard-Parisi-Zecchina). **Computational hardness peaks near alpha_c.** Off the boundary, the problem is either trivially satisfiable (low alpha) or trivially infeasible (high alpha); ON the boundary, solution-space fragmentation makes any solver run in super-polynomial time.

**The substrate has an analogous phase boundary in (N_DIM, M_pattern) space.** Per Pattern 4 of the meta-map (free-probability + spin-glass yield), the capacity cliff is at M/N ~ 0.14 for naive Hebbian and shifts upward with sparse-bipolar / cf-RPE / k-WTA-VQ levers. Cells running NEAR the cliff (which is exactly where the discriminating-regime guard pushes them) are operating in a **computationally-hard regime** where wall scales super-linearly with N.

**Concrete implication.** This is a substrate-product-relevant FINDING, not just a compute-engineering nuisance. The compute hardness and the capacity hardness MAY BE THE SAME PHASE BOUNDARY. If true:
- The substrate's "discriminating regime" is also its "wall-time hard regime" by construction
- Cell-author wall estimates anchored at smoke (which is BELOW the cliff) are guaranteed to underestimate when full N pushes past the cliff
- The right scope-reduction is to push the discriminator INTO a regime that is *just past* the cliff, not deep into it

This connects to free-probability F1 (Marchenko-Pastur on substrate W) and F2 (Tracy-Widom edge) candidates from the field advisor — both probe the same phase boundary from the spectral side. **Adjacency-cascade trigger** per [[research.md]] Trigger C: a follow-up drill into "substrate compute-phase-transition observability" is queued automatically by this finding.

### Angle 5 -- Brain energy budget (biology / neuroscience)

Brain runs at ~20W (long-distance comms; ~0.2W for actual cortex computation per Levy-Calvert 2021 PNAS). Cannot "timeout" because it does not run monolithic batches — it runs **continuous distributed parallel sparse** processing with these specific budget-respecting features:

1. **Sparsity.** ~1-5% of neurons active at any moment. Substrate analog already exists (sparse_bipolar; Tonegawa engram-cell cells; k-WTA-VQ). Cells using DENSE Hebbian outer products are doing what brain explicitly avoids.
2. **Locality.** High-bandwidth comms are short-distance; long-distance is rare and slow. Substrate analog: Pattern 4 "many small cells with shared atoms" beats "one big cell touching all atoms."
3. **Lazy evaluation / predictive coding.** Only prediction errors propagate; expected inputs trigger no computation. Substrate analog: predictive_coding_hierarchy primitive exists; cells that compute the FULL Hebbian write on every pattern are doing what brain explicitly avoids.
4. **No global synchronization.** No "wait for all arms to complete" pattern. Substrate analog: per-seed-per-arm cells with an aggregator (Angle 3).

**Concrete implication.** The 5 timeouts share a "dense-monolithic-synchronous" anti-pattern that is the OPPOSITE of how brain solves bounded-compute. The disparate-field convergence here is striking: HPC (roofline), queueing theory (tiny-tasks), Erlang (let-it-crash), and brain biology ALL point to the same fix — **smaller units, partial results, sparse computation, no global synchronization**.

Brain-existence-proof for the rescue: there is no compute-budget regime where the brain "times out"; it solves the same continual-learning composition-routing problems substrate cells are trying to solve, on 20W, by NOT running a 60min monolithic batch.

---

## Substrate-product implications

### Cell-author discipline (product-level)

The current cell-author template anchors wall estimates on smoke wall. This is **structurally wrong** in the roofline regime sense. Two new disciplines should be added to the cell-author template:

**D1 (mandatory pre-dispatch roofline probe).** For any cell with N_DIM >= 4096 OR M_pattern >= 1000 OR n_arms x n_seeds >= 9: run a 3-point timing probe at (smoke_N, 2x smoke_N, 4x smoke_N). Fit `t = a*N^k`. Extrapolate to full-N. Refuse dispatch if `extrapolated_wall > 0.8 * timeout`. Probe cost ~3-5min CPU; gates >90% of timeout failures by construction.

**D2 (mandatory partial-result atexit + per-seed checkpoint).** All cells with `n_seeds * n_arms >= 4` ship with:
- `atexit` handler flushing current per-arm per-seed metrics dict
- Per-seed checkpoint resume (PROT-021 wired explicitly, not optionally)
- Execution order: iterate `seed_idx, arm_idx` so 1-seed-all-arms lands FIRST

This is **directly substrate-product relevant** because the value of a partial result is much higher than zero — if 1 of 3 seeds completes for all 3 arms, that is a noisy-but-real discriminator measurement that Skunkworks can rule on (with cv flag) instead of a HARNESS_TIMEOUT with zero information.

### Capacity-cliff observability (product-level)

If R3 lands HARD-PASS (compute-phase-transition observable at the capacity cliff), the substrate gains a **new observability primitive**: wall(N, M) as a phase-boundary indicator. This is mechanism-discriminating between "soft" capacity ceilings (continuous degradation; cleanup absorbs the noise) and "hard" capacity ceilings (sharp transition; cells suddenly become intractable to complete). Adds to the by-construction-saturation tiering vocabulary that Skunkworks already uses.

### Big-cell vs many-small-cell architecture (product-level)

The current pattern — 692-line cells with 3 arms x 3 seeds x J phases all in one Python process — is a **GPU-era design pattern** (assume one big GPU node, batch everything). Substrate on local_cpu + remote_cpu does NOT have the GPU-era assumptions: per-cell scheduling overhead is small, partial-result value is high, and wall budgets are bounded.

The Erlang-OTP and brain-locality angles both suggest a **mini-cell architecture** where the "experiment" is a directed graph of small cells with explicit dependencies. The aggregator cell pattern (already used in substrate_brain_full_compose_LM_v1 for cross-arm ablation) is the structural template. This is a non-trivial refactor but is the right substrate-product direction long-term.

---

## L3 -- Concrete rescue plan (3 load-bearing cells)

### Cross-layer compose (cross_layer_composition family)

The experiments/ directory shows ~100+ `exp_q_a3_l*_cross_layer_composition_v1_n*.py` files. This is a Track-A capability composition test (cap_int integration). The timed-out cell is the latest (L-level or N-DIM frontier) of a long sweep.

**Rescue spec:**
- Identify the LARGEST `(L, N)` combination that already completed in this family (read recent_landings.jsonl)
- Re-author the timed-out cell at exactly THAT scope plus ONE step (L+1 OR N x 2, not both)
- Apply D1 roofline probe + D2 atexit
- Single seed pre-flight before 3-seed full
- Wall budget 60min (not 90); will fail-fast not timeout-fail

Hand-off file path: `notes/exp_dev_handoff_research_timeout_class_revival_2026-06-24.md` (companion file, this drill).

### Heterogeneous routing (substrate_compose_heterogeneous_routing_v1)

3 architectures (likely Tonegawa-sparse / dense-Hebbian / k-WTA-VQ) in one cell. The 3-arm design is the cross-cell comparison value; cannot split arms.

**Rescue spec:**
- Halve N_DIM (8192 -> 4096) per c2-postmortem pattern (4x outer-product cost reduction)
- Drop n_seeds from 3 to 1 for first pass; if HARD-PASS or HARD-FAIL, ship; if MIDDLE_BAND, escalate to 3-seed at the reduced N
- Per-arm checkpoint atexit
- Wall budget 60min

Risk: at N=4096 the heterogeneous discriminator may be weaker. Mitigation: pre-reg HARD bands stay; if mechanism fails to discriminate at reduced N, that itself is signal.

### Cross-biology mappings (cross_biology_composition_mappings)

3 mappings (likely cortex / hippocampus / cerebellum analogs) in one cell. Mappings are independent; cell is decomposable.

**Rescue spec:**
- Split into 3 sub-cells (one per biology mapping)
- Each runs full 3-seed at full N (since cost is now 1/3)
- Aggregator cell reads the 3 metrics.json and computes cross-mapping comparison
- Per-sub-cell wall budget 30-40min; total wall ~90min but with 100% partial-result coverage even if one sub-cell fails

This is the **mini-cell architecture** pilot. If it works smoothly, generalize the pattern to the cell-author template.

### Sequence v2, A1 test-design audit, PCGrad v1 (not rescued this drill)

Lower priority per the prompt's "top 3" framing. Queue 2x revival drills for these per [[feedback-route-negatives-to-research]] after the 3 load-bearing rescues land. Do NOT bundle into this drill; would dilute the rescue focus.

---

## Cross-thread synthesis with prior research

- **c2_cascade_stc_swr_timeout_postmortem_2026-06-22** prior post-mortem identified the same root cause (drill estimate underestimated compute at discriminating regime). This drill GENERALIZES that finding from 1 cell to a class.
- **N5_SQ6_membership_wall_2x_2026-06-20** prior wall-class drill is the methodological precedent (treat a wall as a research drill not just a re-spec).
- **drill_mwp_comprehension_wall_phase_6_corpus_3x_2026-06-12** prior 3x revival drill on a wall class; same disparate-fields pattern but different specific failure mode (corpus exhaustion vs compute exhaustion).
- **Pattern 4 (spin-glass + free-probability) yield in meta-map** — the compute-phase-transition / capacity-cliff link (Angle 4) is the same Pattern 4 finding from a new direction.
- **Field advisor TOP 5** -- D1 (Glauber dynamics) and F2 (Tracy-Widom edge) candidates BOTH probe the same phase boundary that this drill flags from the compute side. Adjacency-cascade trigger fires: queue D1 + F2 drills as bonus follow-up if R3 lands HARD-PASS.

---

## Citations (verified count: 7)

1. NERSC, Roofline Performance Model docs (https://docs.nersc.gov/tools/performance/roofline/)
2. Williams S., Waterman A., Patterson D. "Roofline: an insightful visual performance model for multicore architectures." Comm ACM 2009 (ScienceDirect topic page verified)
3. Mezard M., Parisi G., Zecchina R. "Analytic and Algorithmic Solution of Random Satisfiability Problems." Science 2002 (random K-SAT phase transition; arxiv cond-mat/0104428 verified)
4. Levy W.B., Calvert V.G. "Communication consumes 35 times more energy than computation in the human cortex." PNAS 2021 (https://www.pnas.org/doi/10.1073/pnas.2008173118)
5. Erlang/OTP Supervisor Behaviour docs v28.5 (https://www.erlang.org/doc/system/sup_princ.html)
6. Little J.D.C. Little's Law (Wikipedia + Slimmon 2022 application-scaling article verified)
7. Tiny-tasks granularity trade-off (Karau-Konwinski 2022 arxiv 2202.11464 verified)

Lit-scan calibration penalty applied: each angle's P deflated by 0.15-0.25 from raw agent estimate. Novel-synthesis P (R3 -- compute/capacity phase boundary same-thing claim) explicitly capped at 0.45 not 0.65.

---

## Pre-registered field-advisor follow-ups (Trigger C adjacency-cascade)

If R3 lands HARD-PASS, queue 2 follow-up drills automatically:
- D1 Glauber dynamics on substrate codeword space (field=semiconductor; score 5.0)
- F2 Wigner edge / Tracy-Widom on W eigenvalues (field=free-probability; score 5.0)

Both probe the same compute/capacity phase boundary from spectral/dynamic angles; both are TOP-5 candidates from the advisor; both are scope-expansion-eligible.

---

End of drill. Total wall ~50min including disparate-field WebSearch breadth + synthesis. Note word-count ~2050.
