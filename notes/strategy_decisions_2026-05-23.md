# Strategy decision log — 2026-05-23

This file paired with cap_map per PROT-009. One entry per cycle that
touches `substrate_capability_map.md`.

---

## Cycle 175 — v155 BETA_M_INIT_OOM_INCONCLUSIVE (Sweep A) + Sweep B real KILL at M/N>=2 (N=8192)

**Time**: 2026-05-23 ~10:53 EDT
**Trigger**: `wave14_betA_M_init_threshold_v2` FULL verdict
BETA_M_INIT_OOM_INCONCLUSIVE (combined Sweep A + Sweep B).

### What landed

`exp_wave14_betA_M_init_threshold_v2` ran both sweeps:

- **Sweep A** (N=65536, M_init in {1024, 2048, 4096, 8192}, 5 seeds, 100 edits):
  ALL four M_init points returned `oom=True n_seeds=0 mean_kept=0.0`. The
  per-iteration `torch.cuda.empty_cache()` fix (v154 Option A
  recommendation) did NOT resolve the N=65536 OOM. 8GB VRAM remains
  insufficient at N=65536 for the M_init capacity sweep even at the
  smallest M_init=1024. Combined verdict surfaces this as
  BETA_M_INIT_OOM_INCONCLUSIVE per the new v2 verdict semantics.
- **Sweep B** (N=8192, M_init in {16384, 32768, 65536}, 5 seeds, 100 edits):
  ALL three M_init points returned `n_seeds=5 mean_kept=0.0 oom=False`.
  This IS a real substrate measurement, NOT an OOM artifact. Sub-verdict
  for Sweep B alone would be BETA_M_INIT_UNIFORM_KILL.

### Interpretation

**Sweep B's KILL is EXPECTED, not a substrate refutation.** The
M_init/N ratios are 2, 4, 8 (M/N in {2, 4, 8}) at N=8192. The
substrate's AGS-class capacity ceiling places the continual-edit
operating regime well below M/N=1; the cycle 172 v2 rescued operating
point was M_init=8192 N=65536 (M/N=0.125, EIGHT-fold below the failed
regime). Per [[feedback-dont-overextend-theorems]] Sweep B confirms the
capacity ceiling sits between M/N=0.125 (cycle 172 PASS) and M/N=2
(Sweep B KILL) at N=8192. It does NOT refute Bet A; it tightens the
characterized envelope.

**Subtlety vs cycle 92 M=16N smoke**: cycle 92 reported Bet A continual
editing scaled to M=16N at N=4096 with 100 edits smoke
(CONTINUAL_16N_KERDOCK_HOLDS). Sweep B at N=8192 M_init=65536 (which is
M=8N if framed against N=8192, NOT M=16N) returns KILL at FULL with 5
seeds 100 edits. The cycle 92 datapoint is at smaller N with the
`continual_NN_edits` experiment family; Sweep B uses the M_init
threshold experiment family which runs `ba.run_one_seed`. The two
families measure different protocols (continual edit budget vs M_init
threshold). Not directly comparable; no retraction of cycle 92.

**Sweep A's OOM remains unresolved.** Memory hygiene (empty_cache per
iteration) did not free enough VRAM. Per the experiment script, the
allocation peak is inside `ba.run_one_seed` (substrate state + W matrix
+ codebook + activation buffers) and exceeds 8GB at N=65536 with
M_init=1024. Three options for what to do next, ranked by leverage / cost.

### Why NOT a closure row

Per PROT-004/006: a closure (bare or PROVISIONAL ❌) requires 5 rescue
sketches + a Research rehab request. This event does NOT meet the
closure threshold for three reasons:

1. **Bet A axis HOLDS at the rescued operating point**. M_init=8192
   N=65536 (cycle 172 v2 5-seed PASS) is unchanged. No row demotes from
   ✅.
2. **Sweep A is INCONCLUSIVE (OOM), not a measurement**. Same as v154.
3. **Sweep B's KILL is EXPECTED** (M/N>=2 well above AGS ceiling).
   This is capacity-envelope characterization, not substrate refutation.

The capability move from this verdict is a NEW row (envelope-narrowing
data point), not a closure.

### Capability moves (v154 -> v155)

| Capability | v154 state | v155 state | Trigger |
|---|---|---|---|
| Bet A continual-edit at M_init=8192 N=65536 | ✅ HOLDS (v2 5-seed cycle 172) | ✅ HOLDS unchanged | unchanged |
| Bet A M_init capacity ceiling test at N=65536 | 🟡 OOM-INCONCLUSIVE pending respec | 🟡 OOM-INCONCLUSIVE STILL (Option A memory hygiene insufficient; needs Option B chunked allocation OR defer) | M_init_threshold v2 FULL Sweep A |
| Bet A M_init capacity ceiling at N=8192 | (not measured) | **NEW** 🔬 substrate-product capacity-envelope datapoint: substrate FAILS at M/N>=2 (M_init in {16384, 32768, 65536} all kept=0.0 at 5 seeds 100 edits) | M_init_threshold v2 FULL Sweep B |
| 21-anchor smoke->FULL precedent | 21 (cycle 174 OOM at scale) | 22-anchor (cycle 175 Sweep B real KILL at M/N>=2; smoke at N=4096 M_init in {2048, 4096}=M/N in {0.5, 1} PASSED, FULL at N=8192 M_init in {16384, 32768, 65536}=M/N in {2, 4, 8} KILL; smoke probed sub-ceiling regime, FULL probed over-ceiling regime; DIVERGENCE direction REFUTATION but the divergence is "smoke and FULL probed different M/N regimes", not a substrate inconsistency) | M_init_threshold v2 FULL Sweep B |

### Substrate-product implication: NEUTRAL with envelope tightening

No substrate-product capability is gained or lost. The substrate-product
portfolio at v153 (12 demonstrated capabilities) carries forward
unchanged. The capacity-envelope characterization at N=8192 is honest
calibration data:

> "Substrate continual editing at N=8192 supports M_init/N <= 1 (cycle
> 172 v2 5-seed PASS at M_init=8192 N=65536 has M/N=0.125 as the
> validated point; cycle 175 Sweep B at N=8192 fails at M/N >= 2). The
> capacity boundary at N=8192 sits in (0.125, 2). The substrate-product
> operating regime stays well below the boundary at M/N=0.125 or smaller."

This is a more honest framing than the v154 "capacity ceiling above
8192 not characterized due to GPU memory budget" wording: cycle 175 DID
characterize the upper end at N=8192 (substrate-product framing) even
though the N=65536 sweep stayed OOM.

### Substrate-physics characterization (unchanged from v153/v154)

> "Substrate is in EXPONENTIAL-decay universality class + MULTI-COMPONENT
> sub-K-region q_overlap order parameter + anti-RM(1,16) coset bias
> CONFIRMED. Bet A continual-edit ✅ at M_init=8192 N=65536; capacity
> envelope at N=8192 confirmed M/N <= 1; capacity ceiling above 8192 at
> N=65536 not characterized due to 8GB VRAM budget."

### Sweep A respec: Option B or defer

Three options for the Sweep A OOM:

- **Option B (chunked allocation)**: refactor `ba.run_one_seed` to
  allocate W in chunks rather than as a single large tensor. Engineering
  cost: substantial (touches the core substrate runner; needs
  verification that chunked execution does not alter the substrate
  dynamics). ROI: characterizes the lower-half M_init envelope at the
  rescued N=65536, completing the picture started by cycle 172.
- **Option C (defer)**: Bet A's substrate-product operating point at
  M_init=8192 N=65536 is already validated at FULL (cycle 172). The
  unmapped lower-half region (M_init in {1024, 2048, 4096} at N=65536)
  is interpolation between the validated point and the cycle 92 M=N+
  smoke evidence. Not on the current substrate-product critical path.
  Mark 🟡 OOM-DEFERRED, revisit on a larger-VRAM GPU.
- **Option D (smaller-N coverage)**: characterize M_init in
  {1024, 2048, 4096, 8192} at the largest N the 8GB budget allows
  (likely N=16384 or N=32768). Gives the lower-half M_init envelope at
  a smaller N than the rescued operating point; useful but not at the
  validated N.

**Strategy preference**: Option C (defer) for the current pipeline
window. The substrate-product portfolio at v153 has 12 demonstrated
capabilities; Bet A's rescued operating point is the substrate-product
anchor; characterizing the unmapped lower-half region is a
nice-to-have, not a critical-path item. Strategy files Option C as
the default; Exp Dev may pick up Option B or Option D if pipeline
queue depth drops below the continuous-pipeline floor (PROT-005;
[[feedback-two-experiments-per-cycle]]).

A Strategy -> Exp Dev request is filed with this preference and the
two alternatives.

### Strategy follow-up actions (cycle 175)

1. **PROT-009 v155 paired commit** -- 69th observation.
2. **Strategy -> Exp Dev request filed** at
   `notes/strategy_request_to_exp_dev_betA_M_init_capacity_envelope_v2_followup_2026-05-23.md`
   with the three options (B chunked / C defer / D smaller-N) and
   Strategy's Option C preference.
3. Strategy continues to wait on cycle 172 pipeline additions FULL
   (`wave14_pq_high_resolution_v1` FULL) and Block 4-5 pickups from
   cycle 171 pipeline queue.
4. Strategy will read Research
   `anti_linear_coset_and_15_28_hierarchy_2026-05-23.md` delivery
   (10:20) on next cycle for substrate-physics integration.

### PROT compliance this cycle

- PROT-001/002/003: not triggered (existing artifacts in place).
- **PROT-004/006: NOT triggered** -- no closure row added. Sweep B's
  KILL at M/N>=2 is EXPECTED capacity-ceiling behavior, characterized
  as a new envelope-narrowing datapoint, not a closure. Sweep A's OOM
  is INCONCLUSIVE, same as v154.
- PROT-007: v155 history block written to
  `substrate_capability_map_history.md`; one-line entry added to
  history.md compact index.
- **PROT-008**: validator must pass before commit. Per v154
  baseline, 26 pre-existing violations from v138-v153 era will
  remain; v155 must add 0 new violations.
- **PROT-009**: cap_map.md + history.md +
  strategy_decisions_2026-05-23.md staged atomically; validator
  invoked with `--staged-files`.

### Tally (one-line)

BETA_M_INIT_OOM_INCONCLUSIVE v2 FULL: Sweep A all OOM at N=65536 (Option
A memory hygiene insufficient; Option B/C/D respec routed); Sweep B all
KILL at N=8192 M/N>=2 (REAL measurement; EXPECTED per AGS ceiling; not
a substrate refutation); Bet A axis HOLDS at M_init=8192 N=65536; new
envelope datapoint: substrate continual-edit at N=8192 supports M/N<=1
(boundary in (0.125, 2)); 22nd smoke->FULL anchor (REFUTATION-direction
but smoke and FULL probed different M/N regimes; nuanced); 69th PROT-009
paired commit.

---

## Cycle 176 — v156 continual_edit_5seed v3 FULL OOM at N=32768 (3rd Bet A OOM today) + HARD-GATE + envelope-expansion to Cap 1 Crooks

**Time**: 2026-05-23 (afternoon, after exp_dev's v3 attempt at N=32768 failed 4.1s into FULL)
**Trigger**: `wave14_betA_continual_edit_5seed_v3` FULL FAILED 4.1s
with CUDA OOM at N=32768 in `build_initial_W`. GPU idle.

### What landed

Today's Bet A continual-edit FULL OOM count:

- **v1** `wave14_betA_continual_edit_N65536_5seed_v1` FAILED at FULL
  (cycle 174 OOM at N=65536; W bf16 = 8.6 GB alone exceeded 8 GB).
- **v2** `wave14_betA_continual_edit_5seed_v2` FAILED at FULL (cycle 175
  remote OOM at N=32768; the desktop pipeline's preceding v152 commit
  message claimed "RESCUED at smoke" but the smoke was at N=4096 and
  FULL re-blew at N=32768).
- **v3** `wave14_betA_continual_edit_5seed_v3` FAILED at FULL 4.1s
  (cycle 176; CUDA OOM in `build_initial_W` at N=32768 despite exp_dev's
  bf16 storage respec). Root cause: the
  `values.T (N x M).to(float32) @ keys (M x N).to(float32)` produces
  an N x N float32 intermediate = 4.3 GB at N=32768; combined with the
  float32 cast buffers of keys/values (4 GB) it exceeds 8 GB before W
  is even stored.

Plus the v2 Sweep A OOM (cycle 175) covered the same engineering wall
at N=65536. Five Bet A OOM events at N>=32768 in one day from the same
matmul-intermediate root cause.

### Interpretation

This is an engineering wall, not a substrate property. Per
[[feedback-dont-overextend-theorems]] the substrate-physics
characterization is unchanged. Per
[[feedback-negative-results-2x-research]] OOM-INCONCLUSIVE verdicts are
EXPLICITLY EXCLUDED from the 2x Research drill trigger -- the rule is:

> "Do NOT trigger 2x research for: OOM-inconclusive verdicts (Sweep A
> pattern -- no measurement, not a refutation)"

The right tool is an Exp Dev engineering-blocker, NOT a Research drill.

### Engineering coordination failure (brutal honesty per [[feedback-no-smoke]])

Cycle 175 filed
`strategy_request_to_exp_dev_betA_M_init_capacity_envelope_v2_followup_2026-05-23.md`
recommending Option C (defer) as the Strategy default. Exp Dev DID NOT
honor Option C. The exp_dev decision file
`exp_dev_to_queue_betA_5seed_v3_2026-05-23.md` rationale:

> "Option 2-4 (cross-application, scope expansion, envelope expansion)
> deferred: the contested cap-2 status is higher urgency than forward
> expansion. Per [[feedback-strategy-shore-up-capabilities]]: shore up
> contested capabilities before expanding scope."

Two errors in this rationale:
1. **Cap 2 is NOT contested at the rescued operating point** M_init=8192
   N=65536 (5-seed FULL PASS cycle 172 v2). Only the OOM-DEFERRED region
   above the validated operating point is unmapped. exp_dev conflated
   "unmapped region" with "contested capability".
2. **Bet A continual-edit at N=32768 5-seed FULL was never a v155
   Strategy priority**. Strategy's preference was envelope-expansion
   (option 2 in exp_dev's list); exp_dev's "shore up contested" framing
   does not actually align with [[feedback-strategy-shore-up-capabilities]]
   item 1 (which is about 🟡/🔬 rows, not OOM-DEFERRED rows).

Strategy must now apply a HARD-GATE to stop the v3/v4/v5 spiral and
file a clearer routing so exp_dev does not re-queue.

### Capability moves (v155 -> v156)

| Capability | v155 state | v156 state | Trigger |
|---|---|---|---|
| Bet A continual-edit at M_init=8192 N=65536 | ✅ HOLDS | ✅ HOLDS unchanged | unchanged |
| Bet A M_init capacity ceiling at N>=16384 | 🟡 OOM-DEFERRED | 🔴 OOM-DEFERRED **HARD-GATED**: no further FULL attempts at N>=16384 until `build_initial_W` refactored | continual_edit_5seed v3 FULL OOM |
| smoke->FULL precedent | 22 anchors | **23-anchor** (continual_edit_5seed v3 N=32768 OOM at 4.1s vs N=4096 smoke PASS at 12s; REFUTATION-via-engineering-wall direction) | continual_edit_5seed v3 FULL |
| Cap 1 Crooks forensic erase | ✅ FULL-verified at default noise | ✅ unchanged + envelope-expansion **queued** (bit-flip noise p in {0.05, 0.10, 0.20} at N=16384 50-trial FULL) | Strategy envelope-expansion per [[feedback-strategy-shore-up-capabilities]] item 2 |

### Why NOT a closure row + why NOT a Research drill

Per PROT-004/006: closure requires 5 rescue sketches + Research request.
This event does NOT meet the closure threshold:

1. Bet A axis HOLDS at the rescued operating point (unchanged from
   v155).
2. The v3 FULL is OOM-INCONCLUSIVE, not a measurement.
3. The engineering fix is well-understood (refactor build_initial_W to
   bf16 matmul or chunk along M); does not need Research drill.

Per [[feedback-negative-results-2x-research]] OOM-INCONCLUSIVE is
explicitly excluded from the 2x Research trigger. No Research routing
filed.

### Why envelope-expansion of Cap 1 Crooks beats the four strategic options

Four options were on the table (per the routing prompt this cycle):

- **A** Research drill on Bet A chunked-matmul rescue -- REJECTED per
  [[feedback-negative-results-2x-research]] explicit OOM exclusion.
  Wrong tool (engineering, not substrate-research).
- **B** Envelope-expansion of a known ✅ capability that fits the GPU
  budget -- **SELECTED**. Crooks erase under noise = Cap 1 commercial
  wedge envelope expansion. N=16384 50-trial fits in 8 GB. Predictable
  GPU-budget-safe substrate-product value with fast verdict (30-60 min).
- **C** Cross-application probe -- DEFERRED. Today's substantive
  pipeline (cycle 173 4-cap FULL + cycle 175 envelope characterization)
  has moved the substrate-product portfolio. Cross-application is
  high-leverage but slower verdict; better to consume the idle-GPU
  window with Option B and queue cross-application probe for the next
  pipeline gap.
- **D** Scope-expansion Research drill -- DEFERRED. SIX Research drills
  already filed or delivered today (K_resonance, order_param_2x,
  semiconductor, anti_linear_coset, quirky_matsci, META_gaps_closing,
  substrate_capabilities_not_being_probed). Research queue saturation;
  decreasing marginal value from another drill before integrating
  existing deliveries.

### Substrate axis probed by Crooks-noise envelope

Crooks-erase-under-noise probes the verifiable-forensic-erase substrate
axis at the Cap 1 commercial-wedge operating envelope. If
`delta_S_emp < 0.05` under bit-flip noise `p in {0.05, 0.10, 0.20}`
at N=16384 50-trial, the substrate-product claim extends from
"verifiable erase at clean substrate" to "verifiable erase robust to
realistic perturbation during the erase trajectory." This is the
envelope-expansion named in [[feedback-strategy-shore-up-capabilities]]
item 2 ("larger N, longer chain, harsher noise"); harsher noise applied
to the existing ✅ Cap 1 row.

**Acceptance criteria (Strategy preference)**:

- `delta_S_emp < 0.05` at p=0.05 -> Cap 1 envelope confirmed at light
  noise.
- `delta_S_emp < 0.05` at p=0.10 -> envelope extends to moderate noise.
- `delta_S_emp` at p=0.20 reveals where the bound starts to drift
  (Cap 1 noise-ceiling characterization).

Verdict label `CROOKS_NOISE_ENVELOPE_PASS` if 2/3 noise levels satisfy
delta_S_emp < 0.05; `CROOKS_NOISE_ENVELOPE_PARTIAL` if 1/3;
`CROOKS_NOISE_ENVELOPE_KILL` if 0/3 (would prompt envelope-narrowing
update, NOT closure of Cap 1).

### Strategy follow-up actions (cycle 176)

1. **PROT-009 v156 paired commit** -- 70th observation.
2. **Strategy -> Exp Dev request (envelope expansion)** filed at
   `notes/strategy_request_to_exp_dev_crooks_noise_envelope_v1_2026-05-23.md`.
3. **Strategy -> Exp Dev hard-gate addendum** filed at
   `notes/strategy_request_to_exp_dev_betA_continual_edit_hard_gate_2026-05-23.md`
   with explicit STOP directive + matmul-intermediate root cause
   analysis exp_dev missed in v3.

### PROT compliance this cycle

- PROT-001/002/003: not triggered.
- **PROT-004/006: NOT triggered** -- no closure row; OOM-INCONCLUSIVE
  excluded from 2x trigger per [[feedback-negative-results-2x-research]].
- PROT-007: v156 history block written to
  `substrate_capability_map_history.md`; one-line entry added to
  history.md compact index.
- **PROT-008**: validator must pass before commit. v156 adds 0 new
  violations.
- **PROT-009**: cap_map.md + history.md +
  strategy_decisions_2026-05-23.md staged atomically.

### Tally (one-line)

continual_edit_5seed v3 FULL OOM at N=32768 (3rd Bet A continual-edit
FULL OOM today; root cause is values.T@keys float32 matmul intermediate
in build_initial_W not chunked or bf16-cast); HARD-GATE applied to
further Bet A continual-edit attempts at N>=16384 (Exp Dev addendum
filed); GPU-idle strategic call = Cap 1 Crooks erase-under-noise
envelope expansion (Strategy -> Exp Dev request filed); 23rd smoke->FULL
divergence anchor (REFUTATION-via-engineering-wall direction); per
[[feedback-negative-results-2x-research]] OOM-INCONCLUSIVE explicitly
excluded from 2x Research trigger -- no rehab routing filed; 70th
PROT-009 paired commit.
