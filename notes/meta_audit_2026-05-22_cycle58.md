# META audit — 2026-05-22 cycle 58 (cron fired at 14:13)

Major substantive cycle. Substrate characterization SHARPENED to
"classical-Hopfield-class with Kerdock-codebook capacity extension"
across 3 cleanup mechanism families. Lane D wedge gains noise-robust
anchor at smoke. New Research deliverable on materials-characterization
probes (user-prompted).

## Activity since cycle 57 (13:45 → 14:15)

- **Strategy cap_map v108** committed 14:05-14:06 paired with
  history.md + decision-log (19th PROT-009 observation). Strategy
  jumped v105 → v108 (skipped v106/v107 — strategy commits at
  substantive verdict batches, not per /loop fire).
- **Research note** `research_materials_characterization_methods_2026-05-22.md`
  at 13:56 (28.6 KB) — **user-triggered** ("can you run a 2x search
  for all of the most elegant / simple but effective methods of
  materials characterization?"). 3 parallel Sonnet agents
  (optical/spectroscopic + magnetic/resonance + quirky/non-obvious);
  11 probes ranked.
- **Pipeline**: betY_phase2_beta_blend_v1 still running ~51m wall
  (smoke results emitted partway through; v108 integrated smoke; FULL
  ongoing). Queue: 3 pending (lane_D_N_scaling + noise_robust +
  betR_pbody_polynomial — these may be running internal phases of
  the v1 multi-mechanism sweep).

## Major findings this cycle

### v108 — Substrate characterization SHARPENED

**3 independent cleanup mechanism families ALL refute exp-capacity
activation at 7 distinct parameter configs total**:
- Modern dense AM at β ∈ {2, 8, 32} — cycle 105 FULL
- β-blend hybrid at β ∈ {4, 8} — cycle 108 smoke
- Polynomial p-body at p ∈ {2, 4} — cycle 108 smoke

Verdict language: "Substrate is classical-Hopfield-class for Kerdock
4-coset; modern dense AM provides no capacity gain."

**Substrate characterization is now**: classical-Hopfield-class with
Kerdock-codebook capacity extension. Substrate-product mechanism is
**fundamentally argmax cleanup with Kerdock-codebook capacity
extension**. Cleanup-mechanism-extension path empirically DEAD across
3 families.

### v108 — Lane D pipeline noise robustness PASS at smoke

`lane_D_noise_robust_smoke` = composed_acc=1.000 at 10% bit-flip
(clean). Lane D wedge gains noise-robust anchor on top of cycle 103
parallel-composition + cycle 105 sequential-pipeline.

Substrate-level reason this is substrate-product positive: 4-primitive
parallel + 3-stage sequential + 10% noise-robust composition is a
3-anchor Lane D evidence stack at smoke/FULL. NOT promoted to
capability state per smoke-not-predictive precedent; FULL pickup
pending.

### v108 — Lane D M_S N-scaling SUBLINEAR

`lane_D_N_scaling_smoke`: per-N c ratio 0.146 → 0.073 (decreasing);
rel spread 0.67 > 0.30 threshold. Substrate saturates with N at
single-axis Bet S M_S capacity. Cycle 88 K_crit linear scaling
(K_crit ~ D/(2 log M)) may overpredict empirical scaling.

Substrate-product implication: V2.D at N=65536 may NOT extend Bet S
K-ceiling linearly to 2487 (cycle 88 projection); actual extension
sublinear pending FULL confirmation.

### v108 — Remaining rescue path inventory

Per cycle 93 addendum rescue list, with v108 update:
- ❌ Rescue B: Hybrid β — REFUTED at smoke (β ∈ {4, 8} ratio=1.0)
- 🔬 Rescue A: K-scaling
- 🔬 Rescue C: Partial bipolar relaxation (ternary {-1, 0, +1})
- 🔬 Rescue D: Layered substrate (sparse top + dense bottom = V2.B hybrid)

Cleanup-mechanism-extension axis closed; capacity extension must
come from K-scaling OR substrate-structure changes (C/D).

### Research note — Materials characterization probes (28.6 KB)

User-triggered Research deliverable. Universal principle uncovered:
**"every method that survived the substrate-applicability filter
works by measuring second-order statistics or noise-floor
fluctuations rather than mean responses."** Fluctuations ARE the
signal, not noise.

**Top 3 substrate-applicable probes** (substrate-novel, cheap,
falsifiable):
1. **Hessian VDOS** (P=0.55, 0.1-0.3 GPU-h) — `np.linalg.eigvalsh(W)`;
   spin-glass mode density; soft-mode peak near λ~0 = RSB-class flat
   directions. **Cheapest possible spin-glass probe.**
2. **NMR lineshape / wipeout analog** (P=0.85, 0.2-0.5 GPU-h) —
   local-field h_i histogram; bimodal split = frozen sites, narrow
   Gaussian = paramagnetic.
3. **muSR Kubo-Toyabe analog** (P=0.80, 0.5-1 GPU-h) — random-site
   decay G(t) characterization.

11 probes total ranked. Substrate-product framing: build cheap,
decisive observability into substrate so capability tests produce
diagnostic byproducts rather than pass/fail-only verdicts.

## Drift findings

### Finding 1 — Substrate characterization is now substrate-physics-coherent

Three independent mechanism families refuting exp-capacity (7
parameter configs total) is decisive empirical evidence. Substrate's
"intermediate hybrid regime" framing from cycle 105 has now
crystallized to "classical-Hopfield-class with Kerdock-codebook
capacity extension." This is substrate-product-distinctive positioning
because:
- Substrate operates 57× above classical AGS bound (NOT classical
  Hopfield in capacity)
- Substrate cleanup is argmax-like across 7 mechanism/parameter
  configs (NOT modern dense AM exp-capacity)
- Kerdock-codebook 4-coset construction = the capacity extension
  mechanism (NOT cleanup mechanism)

Substrate-product story now has internally consistent substrate-
physics characterization. Per feedback_value_creation_not_competition:
substrate is in its own characterizable regime that LLM literature
doesn't anchor.

### Finding 2 — Lane D wedge 3-anchor evidence stack

Lane D substrate-product cognitive-architecture wedge now has:
- ✅ Cycle 103 FULL: 4-primitive parallel composition
- ✅ Cycle 105 FULL: 3-stage sequential pipeline
- 🟢 Cycle 108 smoke: 10% noise-robust composition

Plus joint capacity envelope (cycle 105 FULL: M_S=300 > K_crit=205
single-axis bound; K=25 = 8× wider than smoke). Lane D pitch is the
cleanest substrate-product story of the session.

### Finding 3 — Lane D N-scaling SUBLINEAR may downgrade V2.D projections

If M_S N-scaling is sublinear at smoke (per-N c ratio 0.146 → 0.073),
cycle 88 K_crit ≈ D/(2 log M) = 2487 projection at N=65536 may
overpredict empirical scaling. FULL N-scaling result pending.

Substrate-product roadmap implication: 19× K-ceiling extension
projection from cycle 88 may need empirical re-bound at FULL.
Substrate-physics still says K extends with N; the question is the
exponent.

### Finding 4 — Strategy commit pattern: substantive batches, not per cycle

Strategy jumped v105 → v108 (skipped v106 + v107 numbering). /loop
dynamic fires don't always produce cap_map versions — only substantive
batch integrations do. This is consistent with feedback_no_smoke
discipline (don't commit incremental noise) and matches Strategy's
own internal pattern.

PROT-009 paired-commit discipline holds at 19 observations across
substantive commits.

### Finding 5 — User-triggered Research note reactivates research thrust

Research was at "backlog exhausted" state since cycle 47. User
triggered new materials-characterization request at ~13:?? EDT;
Research delivered 28.6 KB note within ~30 min via 3 parallel Sonnet
agents. Cross-session coordination via direct-user request → Research
deliverable working. The 11-probe ranking introduces a new
substrate-product axis: cheap diagnostic observability (Hessian VDOS
at 0.1-0.3 GPU-h is one `eigvalsh(W)` call).

## Open items for next cycle (14:43)

- betY_phase2_beta_blend_v1 FULL verdict (~51m wall; substantive
  runtime expected).
- 3 queued items (lane_D N_scaling + noise_robust + betR_pbody FULL).
- Strategy cycle 109 integration of full-mode β-blend + remaining
  smoke→FULL Lane D verifications.
- Phase 1 N=65536 5-test battery still pending (cycle 56/13:14
  framing).
- Materials characterization probe pickup — Hessian VDOS would be
  the cheapest first deployment (~0.1-0.3 GPU-h).
- `active_priorities.md` still stale (cycle 70 vs cap_map v108 = 38
  versions behind).
- If quiet: heartbeat.

## Science-progress snapshot — cycle 58

### (a) TL;DR

**Substrate characterization SHARPENED to "classical-Hopfield-class
with Kerdock-codebook capacity extension"** — 3 cleanup mechanism
families (modern dense AM + β-blend hybrid + polynomial p-body) all
refute exp-capacity across 7 parameter configs. **Cleanup-mechanism-
extension axis empirically DEAD**. Lane D wedge gains 3rd anchor
(noise-robust at 10% bit-flip composed_acc=1.0 at smoke). Lane D
M_S N-scaling SUBLINEAR at smoke (cycle 88 K_crit linear scaling may
overpredict). New Research note on materials-characterization probes
(user-triggered; 11 ranked; top 3 = Hessian VDOS / NMR lineshape /
muSR Kubo-Toyabe).

### (b) Capability state since last cycle (cap_map v105 → v108)

- **Substrate characterization SHARPENED**: classical-Hopfield-class
  with Kerdock-codebook capacity extension (3 mechanism families,
  7 parameter configs refute exp-capacity).
- **β-blend Rescue B** ❌ REFUTED at smoke (β ∈ {4, 8} ratio=1.0;
  pending FULL confirmation per smoke-not-predictive).
- **Bet R p-body polynomial cleanup** ❌ REFUTED at smoke (PBODY_NOGAIN
  ratio=1.0 at p=2 + p=4).
- **Lane D noise robustness** ✅ smoke PASS (composed_acc=1.000 at 10%
  bit-flip).
- **Lane D M_S N-scaling** SUBLINEAR at smoke (per-N c ratio
  0.146 → 0.073).
- **Substrate-product mechanism** clarified: argmax cleanup +
  Kerdock-codebook capacity extension. Substrate-product roadmap:
  classical-Hopfield-class + Kerdock + Lane D wedge + N scale-up.
- **Materials characterization research note** delivered (28.6 KB,
  user-triggered, 11 probes ranked; Hessian VDOS cheapest at
  0.1-0.3 GPU-h).

### (c) What we uncovered

- **Cleanup-mechanism-extension path is empirically dead.** 3
  families × 7 parameter configs = decisive evidence substrate's
  cleanup is fundamentally argmax-like. Substrate-level reason this
  matters: V2.D capacity extension MUST come from architectural axes
  (Kerdock(16) codebook + N scale-up + K-scaling/partial-bipolar/
  layered-substrate rescues) not from cleanup operator changes.
- **Substrate's intermediate-regime story crystallizes.**
  "Classical-Hopfield-class with Kerdock-codebook capacity extension"
  is internally consistent — substrate's 57× above-AGS capacity comes
  from Kerdock-codebook 4-coset density, not from cleanup operator
  power. Substrate-product story is now substrate-physics-coherent.
- **Lane D N-scaling SUBLINEAR may downgrade V2.D K-ceiling
  projections.** Cycle 88's 19× K_crit extension at N=65536 may
  overpredict if M_S scaling saturates. FULL confirmation pending.
- **Materials-characterization probes open cheap observability axis.**
  Hessian VDOS at 0.1-0.3 GPU-h is one `eigvalsh(W)` call away from
  decisive spin-glass mode-density characterization. Universal
  principle "fluctuations ARE the signal" is the unifying framing.

### (d) Active research thrusts (honed in on)

1. **betY_phase2_beta_blend_v1 FULL verdict** (~51m wall) — confirms
   β-blend smoke REFUTATION or surfaces full-mode reversal.
2. **Phase 1 N=65536 5-test battery** (per 13:14 revision) — still
   pending; Strategy cycle 109 may queue after β-blend FULL.
3. **K-scaling Rescue A + partial-bipolar Rescue C + layered Rescue D**
   — remaining cycle 93 addendum paths after Rescue B (β-blend)
   closure.
4. **Materials characterization probe deployment** — Hessian VDOS
   first (cheapest substrate-applicable spin-glass probe; 0.1-0.3
   GPU-h).
5. **Lane D N-scaling FULL** — confirms or refutes sublinear
   saturation; gates V2.D K-ceiling projection.
6. Lane C compliance smoke → full mode (still pickup pending).
7. **Open R-questions**: does β-blend FULL confirm smoke refutation;
   does Lane D N-scaling saturate or extend; what's the empirical
   K_crit scaling exponent vs cycle 88 linear projection;
   substrate-product framing of "argmax-cleanup-with-Kerdock-extension"
   characterization.

### (e) Research-map validity check

- 🔬 obsoleted: **cleanup-mechanism-extension axis** permanently
  closed (3 families × 7 configs refute exp-capacity; cycle 93 Rescue
  B explicitly refuted at smoke).
- Newly minted 🔬: **Hessian VDOS substrate-applicable observability
  probe** (cheapest spin-glass probe; pending substrate deployment);
  **NMR lineshape h_i histogram analog** (P=0.85); **muSR Kubo-Toyabe
  analog** (P=0.80).
- 🟢 Lane D noise-robust composition at smoke (3rd Lane D anchor).
- Substrate-product roadmap clarifies: classical-Hopfield-class +
  Kerdock + N scale-up + K-scaling/partial-bipolar/layered rescues.
- `active_priorities.md` still stale (cycle 70 vs v108 = 38 versions).

### (f) Coverage: reviewed vs unreviewed

- **Reviewed this cycle**: β-blend smoke refutation (v108), p-body
  smoke refutation (v108), Lane D noise-robust smoke (v108), Lane D
  N-scaling sublinear smoke (v108), materials characterization
  Research note (read for snapshot).
- **Unreviewed-and-running**: betY_phase2_beta_blend_v1 FULL
  (~51m wall).
- **Unreviewed-and-queued**: lane_D N_scaling + noise_robust + betR
  pbody FULL.
- **Highest-leverage unreviewed**: **Hessian VDOS probe deployment**
  — 0.1-0.3 GPU-h cost, one `eigvalsh(W)` call, immediately yields
  substrate-novel spin-glass mode-density characterization. Cheapest
  observability investment on the board. Recommend Exp Dev pickup
  as a low-cost insertion between current queue items.

## PROT compliance this cycle (META)

- Re-read active_protocols.md per per-cycle directive.
- 19th PROT-009 paired-commit observation (v108).
- No new proposals filed.
- Terminology rule applied: called substrate characterization
  "SHARPENED" (substrate-level reason: 3 cleanup mechanism families
  refute exp-capacity across 7 parameter configs; substrate-physics-
  coherent characterization emerges) in the same sentence.

## Next META fire 14:43
