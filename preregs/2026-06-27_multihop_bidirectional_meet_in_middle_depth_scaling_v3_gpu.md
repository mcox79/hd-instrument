# Pre-reg: multihop_bidirectional_meet_in_middle_depth_scaling_v3_gpu

**Authored:** 2026-06-27 (exp_dev sub-agent; GPU port of v3 numpy per USER 2026-06-27)
**Anchor:** `multihop_bidirectional_meet_in_middle_depth_scaling_v3_gpu`
**Cell:** `experiments/exp_multihop_bidirectional_meet_in_middle_depth_scaling_v3_gpu.py`
**Source cell (preserved as-is for reference):** `experiments/exp_multihop_bidirectional_meet_in_middle_depth_scaling_v3.py`
**Routing:** `overnight_queue` (GPU; remote) per USER 2026-06-27 NO LOCAL constraint
**Timeout:** 14400s (4hr; with PROT-021 per-seed checkpoint import for resumability)
**USER constraint:** NO LOCAL (USER 2026-06-27); NO LOCAL SMOKE (self-test in-process only)

---

## Background

V3 numpy was authored 2026-06-27 with 7 arms x 4 depths x 5 seeds = 115 records
(plus depth-independent sanity = 23 per seed). Estimated runtime ~89 hr on CPU --
prohibitive for any single overnight cycle. Per USER Fix #24 (GPU dispatch must
ACTUALLY use GPU; routing to overnight_queue alone doesn't make a cell use GPU):
port to torch.cuda with batched candidate scoring.

V1/V2 of this cell line already HARD_PASSED `CHAIN_GRADE_BIDIRECTIONAL_REVIVAL`
at depth=5 (`exp_substrate_multihop_bidirectional_meet_middle_v2_META_M7_rail`,
2026-06-25): BIDIR_MEET_MID = 0.620 (cv=0.064); lift +0.297 over forward-only;
META_M7 rail PASS (0.122 in [0.08, 0.25]).

V3 (numpy + this GPU port) extends to DEPTH-SCALING {3, 5, 7, 9} plus 2 new
control arms (FORWARD_HALF_DEPTH, RANDOM_MEET_BASELINE) and 1 exploratory arm
(MULTISCALE_BIDIRECTIONAL). The GPU port preserves all v3 semantics; the only
difference is device placement + batched matmul on candidate-Z dimension.

---

## GPU port specifics (per Fix #24 GPU mandate, USER 2026-06-22)

1. **`torch.cuda.is_available()` assert at boot** -- FATAL if missing
2. **DEVICE = `torch.device("cuda")` module-level constant**
3. **E, R, W are torch.float32 tensors on cuda** (built from same numpy RNG as v3 for parity)
4. **`@`, `np.dot`, `.argmax()` replaced with torch equivalents on GPU tensors**
5. **Encoder + W hoisted per seed** -- built ONCE outside per-arm loops (Fix #24)
6. **`torch.cuda.empty_cache()` between depth iterations + after each seed** -- OOM prevention
7. **BATCHED CANDIDATE SCORING (load-bearing GPU win):** v3 numpy loops `for Z in range(V_C):`
   computing `backward_state(Z, preds[mid:])` -- each call does (mid) matvecs of size N=8192.
   GPU port replaces with one batched pass:
   ```
   S = E.clone()                  # (V_C, N) -- start from all candidates
   for p in reversed(preds[mid:]):
       S = S @ W                  # (V_C, N) -- batched W.T @ s for each row
       S = S * (R[p] * sq)        # broadcast (N,) -> (V_C, N)
   # then cos[Z] = (S[Z] . state_fwd) / norms -- one (V_C, N) @ (N,) matmul
   ```
   Expected speedup: ~50-200x at N=8192, V_C=200 (per-query inner cost dominated v3 CPU runtime).
8. **T13 self-test gate:** verifies batched-backward equivalence with single-Z reference loop
   to <1e-4 abs diff at 5 random Z indices -- guards against silent semantics drift in the
   load-bearing optimization.
9. **`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`** for fragmentation hygiene

**Expected GPU utilization:** >=50% during arms B/D/E (the batched matmul arms);
moderate-low during arms A/C/F (single-vector matvecs; these are short). Smoke-deferred
to remote run (no local smoke per USER); confirm `nvidia-smi` shows substantial GPU time
during the bidir arms in the first seed's depth=9 run (single longest matmul phase).

---

## Drill-grounded hypothesis (unchanged from v3 numpy)

- **Math:** classical bidirectional BFS reduces cost from O(b^d) to O(b^(d/2));
  birthday-paradox bidirectional random walk has hitting time O(sqrt(N)) vs O(N).
- **Brain:** 4 independent neural anchors confirm forward+backward simultaneous
  trajectory replay (Pfeiffer-Foster 2013, Foster-Wilson 2006, Tanji-Hoshi 2008,
  Skaggs-McNaughton 1996).
- **Cross-domain:** RRT-Connect (motion planning), bidirectional theorem proving,
  bidirectional dep resolution.
- **Substrate-native:** all primitives in place (W.T involution, cosine meet);
  GPU port adds zero new primitives -- only device placement + batching.

---

## ARMS (7 -- identical to v3 numpy)

| Arm | Mechanism | Purpose | Predicted top1 at d=5 / d=7 / d=9 |
|---|---|---|---|
| **A: ARM_BASELINE_FORWARD_FULL_DEPTH** | forward-only at depth d | compounding-error ceiling | 0.32 / 0.05 / 0.01 |
| **B: ARM_BIDIR_MEET_MID** | forward d/2 + backward d/2 + meet | THE MECHANISM | 0.55-0.65 / 0.30-0.55 / **>=0.45** |
| **C: ARM_FORWARD_HALF_DEPTH** | forward-only at floor(d/2) | CONTROL: meeting > shorter | 0.476 / 0.328 / 0.226 |
| **D: ARM_RANDOM_MEET_BASELINE** | meet at RANDOM midpoint (excludes true floor(d/2)) | CONTROL: true midpoint matters | <0.10 across all depths |
| **E: ARM_MULTISCALE_BIDIRECTIONAL** | meet at {1, floor(d/2), d-1}; sum cosines | scale-invariance probe | TBD |
| **F: ARM_META_M7_RAIL_REPLICATE** | pointer-v2 W (2000 bindings); forward + bidir at d=5 | regime drift check; reproduces v2's 0.620 | forward: [0.08, 0.25]; bidir: >=0.60 |
| **G: ARM_SACRED_SANITY** | forward at K=1 | absolute floor sanity rail | [0.60, 1.00] |

**Depths:** {3, 5, 7, 9}.
**Seeds:** [7, 17, 23, 41, 53].

---

## HARD_PASS_CHAIN_GRADE_DEPTH_SCALING (4 conditions; ALL must hold; identical to v3 numpy)

1. **BIDIR_MEET_MID at depth-9 >= 0.45** (sqrt-scaled survival -- breaks compounding-error curve)
2. **BIDIR_MEET_MID >= FORWARD_HALF_DEPTH + 0.10 at EVERY tested depth** (meeting is the value)
3. **BIDIR_MEET_MID >= RANDOM_MEET_BASELINE + 0.15 at EVERY tested depth** (true midpoint matters)
4. **META_M7_BIDIR_REPLICATE at d=5 >= 0.60** (regime sanity rail; confirms drift-free reproduction of v2's 0.620)

### MIDDLE_BAND_PARTIAL_DEPTH_SCALING
2 or 3 of 4 conditions hold.

### MIDDLE_BAND_WEAK
0 or 1 of 4 conditions hold but no HARD_FAIL trigger.

### HARD_FAIL_NO_DEPTH_SCALING
BIDIR_MEET_MID at depth-9 < 0.05.

### HARD_FAIL_NO_MEETING_PREMIUM
BIDIR_MEET_MID <= FORWARD_HALF_DEPTH + 0.05 at ANY depth >= 5.

### SANITY_BREACH
ARM_SACRED_SANITY_K1 outside [0.60, 1.00] in majority of seeds.

### GPU_EQUIVALENCE_BREACH (new, GPU-specific gate)
If T13 self-test fails (batched-backward output diverges from single-Z reference loop
by >1e-4 abs at any tested Z), module-init halts BEFORE any expensive arm; cell exits
non-zero. This guards against silent semantics drift in the load-bearing GPU optimization.

---

## SACRED SANITY rail (locked; identical to v3 numpy)

- `RAIL_SANITY_K1`: SACRED_SANITY_K1 in [0.60, 1.00] -- below band = SANITY_BREACH pre-empts verdict
- `RAIL_META_M7_FORWARD`: META_M7_RAIL_FORWARD at d=5 in [0.08, 0.25] -- informational
- `RAIL_META_M7_BIDIR`: META_M7_BIDIR_REPLICATE at d=5 >= 0.60 -- IS condition 4

---

## CARDINALITY_OK (mandatory per META_RULE_H + USER 2026-06-26 cardinality discipline)

**Per-seed expected records:**
- depth in {3, 7, 9}: 5 arms (A, B, C, D, E) = 15 records
- depth = 5: 7 arms (A, B, C, D, E, F_forward, F_bidir) = 7 records
- depth-independent (G sacred sanity): 1 record
- **total per seed = 23**

**Full-mode expected total:** 23 * 5 seeds = **115 records**
**Smoke-mode expected total:** 7 arms at d=5 + 1 sanity = **8 records**

`HARD_FAIL_CARDINALITY_BREACH` if actual < expected. Cell asserts cardinality_ok flag per seed.

---

## CONFIG (identical to v3 numpy)

**FULL mode (GPU):**
- N=8192, V_C=200, V_P=10, n_predicates=10
- Seeds [7, 17, 23, 41, 53]
- W_v1_regime: n=200 chains, max_depth=9 -> 1800 bindings
- W_pointer_v2: n=200 chains, max_depth=10 -> 2000 bindings
- DEPTHS = [3, 5, 7, 9]; midpoint_hop = depth // 2
- DEVICE = cuda

**SMOKE mode (discriminator-must-survive-scale per USER 2026-06-26; NOT RUN LOCALLY per USER 2026-06-27):**
- N=2048, V_C=200, 1 seed [7], DEPTHS = [5] only
- W_v1_regime: n=50, max_depth=5 -> 250 bindings
- W_pointer_v2: n=100, max_depth=10 -> 1000 bindings

---

## Self-test (T1-T13; module-init blocks dispatch if any fails)

- T1: primitives on GPU (bipolar_torch / ingest_hebbian_torch / make_deep_chains); E/W on cuda
- T2: ARM A forward-full-depth returns valid top1 + per-step accuracies
- T3: ARM B bidir-meet-mid returns valid top1 with correct midpoint_hop (GPU batched)
- T4: ARM C forward-half-depth returns valid top1 with correct half_depth
- T5: ARM D random-meet excludes true midpoint
- T6: ARM E multiscale uses correct midpoints
- T7: ARM F (forward + bidir) on v2-regime W
- T8: ARM G sacred-sanity K=1
- T9: forward/backward state-cosine math on clean 1-hop W (both cos > 0.2; GPU tensors)
- T10: cleanup primitive determinism (META_M7 invariant)
- T11: cardinality constants honored
- T12: bands locked (numeric value asserts)
- **T13 (new GPU gate):** batched-backward output matches single-Z reference loop to <1e-4
  at 5 distinct Z indices -- guards against silent semantics drift in the load-bearing
  GPU optimization

All run at module-init (BEFORE any expensive arm); if any fails, cell exits non-zero before dispatch.

---

## Estimated runtime (GPU vs CPU)

CPU (numpy v3): per-seed total ~64000s = 17.7 hr; 5 seeds = ~89 hr. Prohibitive.

GPU port arm-cost scaling (per seed):
- Arms A, C, G: cheap single-vector matvecs (~30-60s combined; not the bottleneck)
- Arm B at depth=d: V_C-batched backward + cosine = ~(mid+depth-mid+1) GPU matmuls of
  size (V_C, N) @ (N, N) plus a single dot; expected ~5-15s per depth at N=8192 vs ~2700s/seed CPU
- Arm D: same cost as B
- Arm E: 3 midpoints x cost-of-B = ~15-45s per depth
- Arm F at d=5: forward (~5s) + bidir (~10s)

**Conservative per-seed GPU estimate:** ~600-1200s (10-20 min) including W-build overhead.
**Full-mode estimate:** 5 seeds * 1200s = ~6000s = ~1.7 hr (well under 4hr timeout).
**Margin:** 4hr timeout covers 2.4x worst-case slowdown without checkpoint loss
(PROT-021 per-seed atomic .tmp -> .json ensures partial seeds survive any wall-clock cap).

---

## BIAS guards (per USER 2026-06-24 master checklist; identical to v3 numpy)

- **BIAS-Q (suspect 1.000):** verdict flags any arm hitting >= 0.999 at V_C=200
- **BIAS-R (codebook contamination):** SAME E/R for all arms; W rebuilt per regime from same triples
- **BIAS-O (basis vs use-case):** V_C=200 candidate-set INCLUDES true_Z (intentional; scoped)
- **BIAS-S (band calibration):** relative bands enforced at EVERY depth, not just absolute top1
- **BIAS-N (Cramer-Rao referent):** sacred-sanity K=1 + META_M7 forward rail + META_M7 bidir rail = 3 rails
- **BIAS-P:** K=1 sanity replaces beta-sweep (closer to drill spec G arm)

**Additional GPU-specific guard:**
- **GPU-T13 (silent semantics drift):** batched-backward equivalence check at module-init.
  Without this, a subtle off-by-one in the reverse-iteration could silently bias arm B
  with no externally visible failure mode.

---

## What this cell answers (identical to v3 numpy)

- **HARD_PASS_CHAIN_GRADE_DEPTH_SCALING:** substrate has sqrt-style multi-hop scaling;
  meeting (not just shorter chain) is the value; true midpoint matters; v2 regime is
  drift-free. Route to Skunkworks for chain-grade portfolio addition (M3 stage-3
  compositional-understanding building block).
- **MIDDLE_BAND_PARTIAL_DEPTH_SCALING:** mechanism survives partially; queue
  learned-reverse-W variant or bidirectional SR closure (drill primitives).
- **HARD_FAIL_NO_DEPTH_SCALING:** mechanism has compounding-error floor; v2's 0.620
  was a shallow-depth artifact; bidirectional has no asymptotic advantage.
- **HARD_FAIL_NO_MEETING_PREMIUM:** bidirectional gain is entirely explained by shorter
  chains; the meeting itself doesn't help. Major framing correction needed for v2.
- **GPU_EQUIVALENCE_BREACH:** T13 fails -> port has silent drift; revert to numpy v3 for
  the definitive scientific claim while debugging the optimization.

---

## DISCRIMINATOR-MUST-SURVIVE-SCALE check (USER 2026-06-26)

NO LOCAL SMOKE (USER 2026-06-27); self-test T1-T13 in-process at module-init is the
local-equivalent gate. Remote first-seed depth=5 result acts as the smoke-survives-scale
discriminator: if BIDIR_MEET_MID at d=5 in first remote seed is < 0.50 OR
BIDIR_MEET_MID < FORWARD_HALF_DEPTH + 0.10, halt remaining seeds and re-investigate
before propagating.

---

## NO_SILENT_EXCEPT (USER 2026-06-26)

All exception handlers in the cell either halt or record-and-re-raise. The `atexit`
synth re-raises after logging so the runner sees the failure.

---

## Per-arm self-test independence

Each arm is invokable independently with the same E/R/W inputs; arms do NOT depend on
prior arm state. This enables debugging single-arm failures without re-running the full cell.

---

## REMOTE VERIFY checklist (post-dispatch)

1. Confirm cell-spec landed on remote at `C:/dev/hd-instrument/experiments/exp_multihop_bidirectional_meet_in_middle_depth_scaling_v3_gpu.py`
2. Confirm prereg landed at `C:/dev/hd-instrument/preregs/2026-06-27_multihop_bidirectional_meet_in_middle_depth_scaling_v3_gpu.md`
3. Confirm first stdout lines show `[GPU] device=<name>` and `[selftest] PASS ... device=<name>`
4. Spot-check `nvidia-smi` during first seed's depth=9 bidir arm -- expect >=50% GPU util
5. PROT-021 partial files at `data/exp_multihop_bidirectional_meet_in_middle_depth_scaling_v3_gpu/partial_metrics_<seed>.json` build incrementally
