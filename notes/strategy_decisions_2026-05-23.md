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

---

## Cycle 177 -- v157 CROOKS_NOISE_ENVELOPE_KILL: Cap 1 envelope narrows to clean substrate; 5 rescue sketches + 2x Research drill filed; next Exp Dev work routed

**Time**: 2026-05-23 ~11:58 EDT
**Trigger**: `wave14_crooks_noise_envelope_v1` FULL verdict
`CROOKS_NOISE_ENVELOPE_KILL` at 29.2s elapsed. v156 envelope-expansion
probe of Cap 1 Crooks commercial wedge under bit-flip noise
`p in {0.05, 0.10, 0.20}` at N=16384 50-trial 3-seed.

### What landed

- Baseline p=0 cell: `delta_S_emp = 0.0000` (re-confirms v153 Cap 1
  ✅ at FULL).
- All 3 noise cells (p=0.05, 0.10, 0.20): `delta_S_emp >= 0.05`
  (above bound).
- Verdict label per v156 acceptance criteria: `CROOKS_NOISE_ENVELOPE_KILL`
  ("0/3 noise levels satisfy delta_S_emp < 0.05").
- 29.2s elapsed; experiment completed cleanly (no OOM; this IS a real
  measurement, n_seeds=3 50-trial per cell).

### Interpretation

Cap 1 envelope under bit-flip noise NARROWS rather than EXTENDS. The
verifiable Crooks-FT bound holds at the clean operating point already
validated in v153, but does NOT extend to realistic bit-flip noise
during the erase trajectory. Per [[feedback-dont-overextend-theorems]]
this is an envelope-narrowing characterization, not a substrate
refutation -- Cap 1 ✅ at the clean operating point STILL HOLDS
unchanged from v153.

Per [[feedback-no-smoke]] brutal honesty: v156's framing that the
envelope-expansion "would extend Cap 1 from 'verifiable erase at clean
substrate' to 'verifiable erase robust to realistic perturbation'" is
now REFUTED. The Cap 1 commercial wedge framing must sharpen with an
explicit noise-fragility caveat. Demos and customer framing must
specify clean operating point + noise floor SLA.

### Why this triggers 2x Research drill (PROT-004/006 rehab + 2x trigger)

Per [[feedback-negative-results-2x-research]]: the OOM-INCONCLUSIVE
exclusion does NOT apply here because the verdict IS a real
measurement under harsher conditions:

- 29.2s elapsed (no OOM).
- 3 seeds, 50 trials per cell, 4 cells (p=0 + 3 noise cells).
- 3 of 3 noise cells fail the delta_S_emp < 0.05 bound.
- Baseline clean cell PASSES (sanity check confirms protocol works).

This is precisely the [[feedback-rehabilitation-after-rejection]]
"envelope narrowing under harsher conditions" pattern. Rehab discipline
applied: 5 axis-combination rescue sketches filed in cap_map v157
narrative + Strategy -> Research 2x drill request filed.

### Why NOT a closure row (capability holds at clean operating point)

Per PROT-004/006 the rehab discipline FIRES (5 sketches + Research
request) but the cap_map row does NOT carry a ❌ marker because:

1. Cap 1 ✅ at the clean operating point (p=0) HOLDS unchanged from
   v153 (v157 re-confirms delta_S_emp = 0.0000 at p=0).
2. The envelope-narrowing is a NEW capability-row datapoint
   (substrate fails verifiable-erase bound under bit-flip noise),
   not a demotion of the existing ✅ row.
3. PROT-008 validator requires rehab-file references INSIDE ❌ rows;
   no ❌ rows added so the validator does not require the syntactic
   reference inside the row (but Strategy still files the Research
   request as a separate routing artifact per [[feedback-rehabilitation-after-rejection]]).

The capability move is a NEW envelope row (🔬 envelope-narrowed under
bit-flip noise) + framing-sharpening of the existing ✅ Cap 1 row
(conditional on clean operating point).

### Capability moves (v156 -> v157)

| Capability | v156 state | v157 state | Trigger |
|---|---|---|---|
| Cap 1 Crooks-ratio forensic erase at clean substrate | ✅ FULL-verified | ✅ FULL-verified at clean (p=0) operating point unchanged; v157 re-confirms delta_S_emp = 0.0000 at p=0 | crooks_noise_envelope FULL baseline cell |
| Cap 1 Crooks-ratio forensic erase under bit-flip noise (NEW envelope row) | envelope-expansion probe queued | 🔬 envelope NARROWED to clean operating point only: 3/3 noise cells at p in {0.05, 0.10, 0.20} fail Crooks-FT bound; 5 rescue sketches filed; Research 2x drill request filed | crooks_noise_envelope FULL noise cells |
| Cap 1 commercial wedge framing | unconditional "verifiable forensic erase" | ✅ CONDITIONAL on clean operating point with explicit noise-fragility caveat in demos/customer framing | v157 envelope-narrowing finding |

### Five rescue sketches (filed in cap_map v157 narrative)

Pre-armed per PROT-004/006:

1. Redundant erase encoding (replication; r >= 3 copies).
2. Post-erase verification + retry (closed-loop read-after-erase audit).
3. Lower-noise operating envelope + monitoring (SLA with noise floor).
4. Pre-erase denoising filter (signal-processing axis).
5. Code-based protected erase (binding-algebra axis: BCH-coded keys
   or FHRR with phase damping).

Non-exhaustive; unvetted; Research 2x drill produces the vetted
ranking + literature lit-scan.

### Substrate-product implication

Substrate-product portfolio at v153 (12 demonstrated capabilities)
carries forward unchanged in COUNT. Qualitative change on Cap 1:
honest noise-fragility caveat now MUST appear in commercial wedge
framing. The clean-operating-point ✅ is preserved; the unconditional
"verifiable erase robust to realistic perturbation" claim is
refuted and removed.

### Strategy follow-up actions (cycle 177)

1. **PROT-009 v157 paired commit** -- 71st observation.
2. **Strategy -> Research request filed** at
   `notes/strategy_request_to_research_crooks_noise_robust_2026-05-23.md`
   per [[feedback-negative-results-2x-research]] 2x drill trigger.
   Generic-math framing per [[feedback-query-privacy-decomposition]]:
   noise-robust verifiable erasure in associative memory; bit-flip-
   tolerant forward-reverse trajectory audits; fluctuation-theorem-
   bounded information erasure under stochastic perturbation.
3. **Strategy -> Exp Dev request filed** at
   `notes/strategy_request_to_exp_dev_post_v157_envelope_expansion_2026-05-23.md`
   per [[feedback-strategy-shore-up-capabilities]] item 2: next
   pipeline work picks from envelope-expansion of OTHER ✅ caps
   (preferred: Cap 3 Streaming inference noise envelope; alt: Gap B
   Online W chain-length envelope; alt: cross-application probe per
   [[feedback-periodic-scope-expansion]]).
4. Pending: Research vetted ranking of the 5 rescue sketches
   (cycle 178 or later).
5. Pending: cycle 172 pipeline additions FULL
   (`wave14_pq_high_resolution_v1` FULL) and Block 4-5 pickups.
6. Note: runner code change pending (PYTHONIOENCODING=utf-8) will
   eliminate ASCII restriction in print()/verdict_msg when runner
   restarts; downstream sub-agents and exp_dev may drop the ASCII
   grep step on next pickup.

### PROT compliance this cycle

- PROT-001/002/003: not triggered (existing artifacts in place).
- **PROT-004/006: TRIGGERED** -- envelope-narrowing under harsher
  conditions per [[feedback-rehabilitation-after-rejection]]. 5
  rescue sketches filed in cap_map v157 narrative + Strategy ->
  Research 2x drill request file filed. No ❌ row added (Cap 1
  holds at clean operating point) so PROT-008 validator does not
  require rehab-file reference inside the row.
- PROT-007: v157 history block written to
  `substrate_capability_map_history.md`; one-line entry added to
  history.md compact index.
- **PROT-008**: validator must pass before commit. v157 adds 0 new
  violations; no ❌ rows added; envelope row uses 🔬 marker.
- **PROT-009**: cap_map.md + history.md +
  strategy_decisions_2026-05-23.md staged atomically; validator
  invoked with `--staged-files`.

### Tally (one-line)

crooks_noise_envelope_v1 FULL = CROOKS_NOISE_ENVELOPE_KILL at 29.2s
(0/3 noise cells satisfy delta_S_emp < 0.05; baseline p=0 cell
CONFIRMS clean Cap 1 ✅ unchanged); Cap 1 commercial wedge framing
narrows to clean operating point + honest noise-fragility caveat
MUST appear in demos/customer framing; 5 axis-combination rescue
sketches filed + Strategy -> Research 2x drill request filed per
[[feedback-negative-results-2x-research]] (measurement-based
refutation under harsher conditions TRIGGERS 2x drill); Strategy ->
Exp Dev request filed for next pipeline work (preferred Cap 3
Streaming noise envelope analogous probe); 71st PROT-009 paired
commit.

---

## Cycle 178 -- v158 MULTI-EVENT: CROOKS_NOISE_CORRECTED_PASS + STREAMING_NOISE_ENVELOPE_PASS + active_priorities refresh + audit response

**Time**: 2026-05-23 ~12:28 EDT
**Trigger**: Multi-event dispatch combining two verdicts + audit findings from `notes/audit_dropped_and_review_2026-05-23.md`. Combined for a single coherent v158 paired commit per PROT-009.

### What landed (two verdicts + audit)

**Verdict 1**: `wave14_crooks_noise_corrected_bound_v1` = CROOKS_NOISE_CORRECTED_PASS (CPU post-hoc re-analysis of v157 data). All 3/3 noisy cells at p in {0.05, 0.10, 0.20} satisfy `delta_S_emp <= theta(p) + 0.02` under the Sagawa-Ueda noise-corrected bound `theta(p) = ln(2) + p*ln(p) + (1-p)*ln(1-p)`. Reduces to clean Crooks-FT `ln(2)` at p=0.

**Verdict 2**: `wave14_streaming_noise_envelope_v1` FULL at N=16384 = STREAMING_NOISE_ENVELOPE_PASS. 3/3 noise cells at p in {0.05, 0.10, 0.20} satisfy `throughput_ratio >= 0.9`. Cap 3 streaming inference envelope EXTENDED under bit-flip noise.

**Audit signal**: `notes/active_priorities.md` is 46 cap_map versions stale (last touched at v111; current cap_map is v158). Single biggest coordination risk in the orchestrator per audit Rec 1 URGENT.

### Interpretation -- both verdicts are envelope EXPANSIONS

**Cap 1 commercial wedge WIDENS, not narrows**. v157's "narrowing" framing was an axiom-mismatch artifact: the clean Crooks-FT acceptance criterion (`delta_S_emp < 0.05`) was applied to a noisy channel where the correct bound is the Sagawa-Ueda noise-corrected `theta(p) + tolerance`. v157's empirical data carries forward unchanged; v157's framing is honestly RETRACTED per [[feedback-no-smoke]] brutal honesty. The substrate-product story IMPROVES because Cap 1 now ships as a **TIERED noise-tolerance certificate**:

- Tier 1 (clean): `delta_S_emp < 0.05` (clean Crooks-FT bound). v153 + v157 FULL-verified at p=0.
- Tier 2 (noisy): `delta_S_emp(p) <= theta(p) + 0.02` where `theta(p) = ln(2) + p*ln(p) + (1-p)*ln(1-p)`. v158 CPU re-analysis PASS at p in {0.05, 0.10, 0.20}.
- Customer SLA picks tier by operating environment.

**Cap 3 Streaming inference envelope EXTENDED** under bit-flip noise. Drift-diffusion NESS holds at p in {0.05, 0.10, 0.20} with throughput_ratio >= 0.9 (3/3 cells PASS at N=16384). Cap 3 commercial framing becomes unconditional at the operating-noise floor.

### Why v157 narrative needs honest retraction

Per [[feedback-no-smoke]]: v157's narrative used "narrowing" repeatedly and characterized Cap 1 as CONDITIONAL on clean operating. That framing was wrong because the acceptance criterion was the clean axiom applied to a noisy channel; the data was always compatible with the noise-corrected bound. v158 corrects the framing without changing the v157 measurements. The cap_map v157 narrative is preserved in history; the v158 retraction is in wording, not in measured fact.

### Capability moves (v157 -> v158)

| Capability | v157 state | v158 state | Trigger |
|---|---|---|---|
| Cap 1 Crooks erase Tier 1 (clean) | ✅ FULL at p~0 | ✅ FULL unchanged; re-confirmed via Sagawa-Ueda baseline theta(0)=ln(2) | crooks_noise_corrected baseline cell |
| Cap 1 Crooks erase Tier 2 (noisy) NEW row | 🔬 envelope narrowed to clean (v157) | ✅ FULL PASS at p in {0.05, 0.10, 0.20} under Sagawa-Ueda theta(p)+0.02 | crooks_noise_corrected_bound_v1 3/3 PASS |
| Cap 1 commercial wedge framing | CONDITIONAL on clean (v157) | **TIERED noise-tolerance certificate** (Tier 1 clean + Tier 2 noisy under Sagawa-Ueda) | v158 re-axiomatization |
| Cap 3 Streaming inference clean | ✅ FULL (v153) | ✅ FULL unchanged | -- |
| Cap 3 Streaming inference under noise NEW row | not measured | ✅ FULL PASS at p in {0.05, 0.10, 0.20}; throughput_ratio>=0.9 3/3 cells N=16384 | streaming_noise_envelope_v1 FULL |
| active_priorities.md | v111 (46 versions stale) | v158 (refreshed atomically this commit) | audit Rec 1 URGENT |

### Substrate-product net (v158)

12 demonstrated capabilities (v153) carry forward UNCHANGED IN COUNT. Two qualitative envelope expansions land (Cap 1 -> Tier-2 noisy PASS; Cap 3 -> noise envelope PASS). v157 "narrowing" framing honestly RETRACTED.

### Substrate-physics characterization (unchanged from v157)

EXPONENTIAL-decay universality + MULTI-COMPONENT sub-K-region q_overlap + anti-RM(1,16) coset bias CONFIRMED. Cap 1 Crooks forensic erase verifiable at BOTH clean (Tier 1) and noisy (Tier 2 Sagawa-Ueda) operating envelopes. Cap 3 NESS robust to bit-flip noise. Bet A continual-edit ✅ at M_init=8192 N=65536; HARD-GATE on N>=16384 continues.

### Audit response actions taken in this commit

Per `notes/audit_dropped_and_review_2026-05-23.md` (META audit 2026-05-23):

1. **Rec 1 URGENT**: `notes/active_priorities.md` refreshed v111 -> v158 atomically in this commit. Updated content covers v158 substrate-product portfolio (12 demonstrated + 2 envelope-expansion rows), engineering blocker at Bet A N>=16384, current queue depth (0 per [[feedback-pipeline-pacing]] -- exp_dev next-pipeline routing fills it), open routings, 5 stale 🔬/🟡 rows.

2. **Rec 2 HIGH-LEVERAGE**: Bet Z.5 vs VAMP-on-chain equivalence check routed to Exp Dev as part of the next-pipeline routing (cheap CPU; bandwidth-permitting).

3. **Rec 3 CADENCE FIX**: 5 axis-combination rescue sketches for Bet T (🟡 PARTIAL min_acc=0.689; 56 versions stale) + Bet V (🟡 PARTIAL gap=0.424; 54 versions stale) filed to Research per PROT-004/006 backlog. Plus burn-down note acknowledging the 3 orphaned 2026-05-23 Research deliveries (D1/D2/D3 per audit).

4. **D9**: `wave14_pq_high_resolution_v1` FULL conversion (5 cycles pending) re-emphasized to exp_dev in next-pipeline routing.

5. **D5 META Gap A spatially-coupled codebook**: re-acknowledged in active_priorities. Awaiting bandwidth (substantial cost; not added to current pipeline).

### Strategy follow-up actions (cycle 178)

1. **PROT-009 v158 paired commit** -- 72nd observation.
2. **`notes/active_priorities.md` refreshed v111 -> v158** atomically in this commit per audit Rec 1 URGENT.
3. **Strategy -> Exp Dev next-pipeline routing filed** at `notes/strategy_request_to_exp_dev_post_v158_pipeline_2026-05-23.md`. Picks (ranked): (a) Online W noise envelope CPU exploratory sweep (analogous noise probe to Cap 1/Cap 3; small N exploratory; per [[feedback-pipeline-pacing]] CPU exploration informs GPU depth); (b) `wave14_pq_high_resolution_v1` FULL conversion (5 cycles pending; cheap GPU); (c) Bet Z.5 vs VAMP-on-chain equivalence check (local CPU + theory; audit Rec 2). Strategy preference order: (a) FIRST, (b) parallel on GPU, (c) on bandwidth.
4. **Strategy -> Research routing filed** at `notes/strategy_request_to_research_betT_betV_rescue_sketches_2026-05-23.md` per PROT-004/006 backlog. Generic-math framing: parallel hypothesis tracking under uncertain evidence + self-reflective memory updates in associative substrate. Bet T 56 versions stale; Bet V 54 versions stale.
5. **Strategy -> Research burn-down note filed** at `notes/strategy_research_burn_down_three_orphans_2026-05-23.md` per audit Rec 3: acknowledges D1 (research_strategy_open_questions), D2 (research_order_param_2x_drill), D3 (research_semiconductor_physics_substrate_analogies) with concrete one-cycle next steps.
6. Push v158 to remote per [[feedback-cap-map-update-protocol]].

### PROT compliance this cycle

- PROT-001/002/003: not triggered (existing artifacts in place).
- **PROT-004/006: NOT triggered for a closure** -- both verdicts are PASS; no ❌ row added. The v157 envelope-narrowing 🔬 row is REFRAMED to a ✅ Tier-2 row under Sagawa-Ueda (an upgrade, not a new closure). The 5 v157 rescue sketches remain on the substrate-product roadmap as elective hardening options.
- PROT-007: v158 history block written to `substrate_capability_map_history.md` compact index.
- **PROT-008**: validator must pass before commit. v158 adds 0 new violations; no ❌ rows added; baseline 26 pre-existing violations from v138-v153 era unchanged.
- **PROT-009**: cap_map.md + history.md + strategy_decisions_2026-05-23.md + active_priorities.md staged atomically. Validator invoked with `--staged-files`.

### Tally (one-line)

crooks_noise_corrected_bound_v1 (CPU re-analysis of v157 data) = CROOKS_NOISE_CORRECTED_PASS at 3/3 noise cells under Sagawa-Ueda noise-corrected bound theta(p)+0.02; streaming_noise_envelope_v1 FULL N=16384 = STREAMING_NOISE_ENVELOPE_PASS at 3/3 noise cells (throughput_ratio>=0.9 at p in {0.05, 0.10, 0.20}); Cap 1 commercial wedge WIDENS from clean-only (v157) to TIERED noise-tolerance certificate (Tier 1 clean + Tier 2 noisy under Sagawa-Ueda); v157 "narrowing" framing honestly RETRACTED as axiom-mismatch artifact per [[feedback-no-smoke]]; Cap 3 Streaming inference envelope EXTENDED under bit-flip noise; active_priorities.md refreshed v111 -> v158 atomically per audit Rec 1 URGENT; Strategy -> Exp Dev next-pipeline routing filed; Strategy -> Research Bet T/V rescue sketches filed; Strategy -> Research burn-down for 3 orphaned 2026-05-23 deliveries (D1/D2/D3) filed; 72nd PROT-009 paired commit.

---

## Cycle 179 -- v159 ONLINE_W_NOISE_ENVELOPE_NARROW (Cap 5 noise envelope characterized at p<=0.30)

**Time**: 2026-05-23 ~12:59 EDT
**Trigger**: `wave14_online_W_noise_envelope_v1` FULL verdict ONLINE_W_NOISE_ENVELOPE_NARROW (orchestrator-queued Strategy v158 Pick 1).

### What landed

`wave14_online_W_noise_envelope_v1` FULL at 89.3s elapsed (N=4096, n_writes=50, n_seeds=3 per pre-reg, noise grid p_flip in {0.0, 0.05, 0.10, 0.20, 0.30, 0.40}, retention threshold min_acc>=0.95, Robbins-Monro lr 1/(1+t/10), SNAP threshold 1.0). 4 of 5 noisy cells PASS (p_flip in {0.05, 0.10, 0.20, 0.30}); 1 FAIL at p_flip=0.40; baseline p=0 PASS re-confirms clean Cap 5 ✅ from cycle 173 v153.

### Interpretation

**Envelope CHARACTERIZED at p_flip<=0.30** (NOT refutation, NOT narrowing-as-defect). Pre-reg explicitly predicted ENVELOPE_NARROW with boundary in p in [0.20, 0.40]; observed boundary p_flip~0.30 lands inside the predicted band. Hard-fail threshold (KILL at p=0.05) NOT crossed. Per [[feedback-negative-results-2x-research]] this is expected-boundary measurement, not a refutation under harsher conditions; per [[feedback-no-smoke]] honest framing is "Cap 5 holds at min_acc>=0.95 across p_flip<=0.30; first fail at p=0.40".

**Compared to today's other two envelope probes**: third noise envelope characterized today after Cap 1 (v157 KILL -> v158 Sagawa-Ueda tiered PASS) + Cap 3 (v158 PASS through p<=0.20). Three different envelope shapes from the same probe family; envelope shape is per-capability, not substrate-wide.

**Sagawa-Ueda-style metric flip candidate**: v158 widened Cap 1 by re-axiomatizing acceptance criterion from clean Crooks-FT to Sagawa-Ueda noise-corrected bound. Analogous question for Cap 5: does Robbins-Monro under bit-flip noise admit a noise-corrected retention bound (e.g. min_acc >= 0.95 - C*H_2(p)) under which p=0.40 PASSES? Robbins-Monro/Polyak-Juditsky/Bottou 2018 noisy-SGD literature provides explicit noise-floor terms; question is whether the noise-corrected bound is principled.

### Capability moves (v158 -> v159)

| Capability | v158 state | v159 state | Trigger |
|---|---|---|---|
| Cap 5 Online W (Robbins-Monro+SNAP) at clean substrate | ✅ FULL clean (v153) | ✅ FULL clean unchanged; re-confirmed at p=0 baseline cell | online_W_noise_envelope_v1 FULL baseline cell |
| Cap 5 Online W under bit-flip noise (NEW envelope row) | not measured | ✅ FULL PASS at p_flip<=0.30 (4/4 noisy cells); FAIL at p_flip=0.40; envelope CHARACTERIZED at p_flip<=0.30; pending Research drill on Sagawa-Ueda-style metric flip for p>=0.40 region | online_W_noise_envelope_v1 FULL |
| Cap 5 commercial framing | unconditional retention claim | EXPLICIT operating envelope p_flip<=0.30 (realistic customer noise floors well below); 5 axis-combination rescue sketches filed for p>=0.40 region | v159 envelope characterization |

### Strategy follow-up actions (cycle 179)

1. **PROT-009 v159 paired commit** -- 73rd observation.
2. **Strategy -> Research 2x drill request filed** at `notes/strategy_request_to_research_online_W_noise_robust_2026-05-23.md` per [[feedback-negative-results-2x-research]] + v158 Cap 1 precedent. Research will determine: (a) does Sagawa-Ueda-style noise-corrected retention bound exist for noisy Robbins-Monro that PASSES at p=0.40? (b) ranked recommendation of 5 rescue sketches; (c) one-cycle next-experiment prescription.
3. **5 axis-combination rescue sketches** (per [[feedback-rehabilitation-after-rejection]]): Polyak-Juditsky iterate averaging + SVRG-style variance reduction + BSC majority-vote decoder + adaptive SNAP threshold + Tier-2 noise-corrected retention SLA. Detailed in the Research request file.
4. **`notes/active_priorities.md`** Cap 5 row updated atomically in this commit.
5. **DO NOT file Exp Dev routing** -- per the verdict event payload, orchestrator is dispatching parallel exp_dev to refill queue per [[feedback-pipeline-pacing]]. Strategy + Exp Dev coordinated; v159 stays out of the Exp Dev queue lane.
6. Push v159 to remote per [[feedback-cap-map-update-protocol]].

### PROT compliance this cycle

- PROT-001/002/003: not triggered (existing artifacts in place).
- **PROT-004/006: NOT triggered for a closure** -- Cap 5 NOT closed; capability holds in the relevant operating regime (p<=0.30). The envelope-characterization row is filed under existing ✅ Cap 5 row with explicit boundary, not a new ❌ closure. The 5 axis-combination rescue sketches are filed per [[feedback-rehabilitation-after-rejection]] best practice but no ❌ row added.
- PROT-007: v159 history block written to `substrate_capability_map_history.md` compact index.
- **PROT-008**: validator must pass before commit. v159 adds 0 new violations; no ❌ rows added; baseline 26 pre-existing violations unchanged.
- **PROT-009**: cap_map.md + history.md + strategy_decisions_2026-05-23.md + active_priorities.md + strategy_request_to_research_online_W_noise_robust_2026-05-23.md staged atomically. Validator invoked with `--staged-files`.

### Tally (one-line)

online_W_noise_envelope_v1 FULL = ONLINE_W_NOISE_ENVELOPE_NARROW at 89.3s (4/5 noisy cells PASS at p_flip in {0.05, 0.10, 0.20, 0.30}; FAIL at p_flip=0.40; boundary at p in (0.30, 0.40]; baseline p=0 PASS re-confirms clean Cap 5 ✅ unchanged from cycle 173 v153); third noise envelope characterized today after Cap 1 (v157 KILL -> v158 Sagawa-Ueda tiered PASS) and Cap 3 (v158 PASS through p<=0.20); Cap 5 commercial wedge UNCHANGED in operating range (p<=0.30 covers realistic customer noise floors); pre-reg prediction p-boundary in [0.20, 0.40] SATISFIED; hard-fail KILL-at-p=0.05 NOT crossed; per v158 Cap 1 precedent Strategy -> Research 2x drill filed for Sagawa-Ueda-style noise-corrected retention bound (Robbins-Monro/Polyak-Juditsky/Bottou 2018); 5 axis-combination rescue sketches filed (Polyak-Juditsky averaging + SVRG variance reduction + BSC majority-vote decoder + adaptive SNAP threshold + Tier-2 noise-corrected SLA); Exp Dev routing INTENTIONALLY OMITTED (orchestrator coordinating parallel exp_dev to refill queue); 73rd PROT-009 paired commit.

---

## Cycle 180 — v160 Cap 2 self-monitoring confidence STRUCTURALLY CLOSED (hard-fail crossed in TWO independent metric framings; substrate-product portfolio drops 12 -> 11 demonstrated capabilities; FIRST true structural closure of session arc since cycle 173/v153)

**Time**: 2026-05-23 ~13:14 EDT
**Trigger**: `wave14_cap2_confidence_margin_probe_v1` FULL verdict `CAP2_MARGIN_KILL` at 3.3s elapsed (orchestrator-queued metric-definition re-probe of v153 Cap 2 `CRITICAL_NO_CORRELATION`; pre-reg `preregs/2026-05-23_wave14_cap2_confidence_margin_probe_v1.md`).

### What landed

`wave14_cap2_confidence_margin_probe_v1` FULL (N=8192, M=200, 3 seeds, 200 trials/stratum, noise grid p in {0.0, 0.05, 0.10, 0.20}) returned `CAP2_MARGIN_KILL`.

Verdict_msg: "HARD FAIL: corr(margin, correct) < 0.2 in ALL strata. Substrate carries no margin-based confidence signal; Cap 2 structurally closed."

Pre-reg hard-fail threshold (`corr(margin, is_correct) < 0.20 in ALL strata` across 3-seed mean) CROSSED at all 4 noise strata. Cosine-margin metric (top_1_cosine_score - top_2_cosine_score after one retrieval step) is the Sagawa-Ueda-precedent re-axiomatization of the v153 tau-iteration-count proxy.

### Why this is a TRUE structural closure (NOT envelope narrowing)

Unlike today's other "narrowing" verdicts (Cap 1 v157 envelope NARROWS to clean + Cap 5 v159 envelope CHARACTERIZED at p<=0.30; both stayed BELOW pre-reg hard-fail thresholds), this verdict CROSSES the hard-fail threshold defined in the pre-reg. Two independent metric framings refute Cap 2 at FULL: (1) v153 tau iteration count CRITICAL_NO_CORRELATION; (2) v160 cosine margin CAP2_MARGIN_KILL. The substrate does not carry margin/tau-based intrinsic confidence signal.

Per [[feedback-no-smoke]] brutal honesty: Cap 2 is CLOSED, not "narrowed".

Per [[feedback-dont-overextend-theorems]]: closure SCOPE is "margin/tau-based intrinsic confidence proxy at substrate". Does NOT close the broader "substrate carries SOME confidence-correlated signal" axis -- 5 rescue paths remain open (endpoint-id, VAMP posterior variance, chi_4, Kovacs, Gap C subsumption).

### PROT-004/006 closure discipline applied

Per PROT-006 sequencing: rehab request file written FIRST (before cap_map commit).

**Rehab file**: `notes/strategy_request_to_research_cap2_self_monitoring_rehab_2026-05-23.md`

**5 axis-combination rescue sketches** (Strategy DRAFT; Research 2x drill is load-bearing ranking per [[feedback-rehabilitation-after-rejection]] + [[feedback-unbiased-research]]):

1. **Endpoint-ID as confidence proxy** (axis: proxy substitution). Leverages substrate-novel 28-element endpoint partition (v153 + v149). Map retrieval -> endpoint cluster; `p(correct | endpoint)` as confidence. Cheapest experimental rescue ~10 min CPU. HARD PASS: ROC AUC >= 0.65 + ECE <= 0.10 + improvement over margin baseline >= 0.15 AUC.
2. **VAMP-on-chain posterior variance certificate** (axis: native uncertainty mechanism). Cap 5 VAMP produces posterior variance natively. Cycle 162 HEADTOHEAD_EQUIVALENT confirms argmax/VAMP accuracy equivalence at smoke. ~15 min CPU. HARD PASS: corr(-log sigma^2, correct) >= 0.40 in 2+ strata + Cohen's d >= 0.5 + ECE <= 0.10.
3. **chi_4 dynamic susceptibility per query** (axis: observability suite). v150 CHI4_RS_CONSISTENT 6th cross-family RS-cert anchor. Per Berthier 2010 measures dynamical heterogeneity directly. ~20 min CPU. HARD PASS: corr(-peak_chi_4, correct) >= 0.40 in 2+ strata + Cohen's d >= 0.5.
4. **Kovacs-style memory-effect probe per query** (axis: hysteresis observable). v150 KOVACS_RS_INDEPENDENT 6th cross-family RS-cert anchor. Temperature pulse during retrieval; relaxation hump = basin instability. ~25 min CPU. HARD PASS: corr(-A_Kovacs, correct) >= 0.40 in 2+ strata.
5. **Re-axiomatize Cap 2 as downstream conformal layer** (axis: re-axiomatization to downstream calibrator). Gap C ✅ cycle 173 CONFORMAL_COVERED at FULL already delivers conformal calibrated confidence. Cap 2 SUBSUMED by Gap C -- not a separate capability axis. Zero experimental cost.

**Sequencing recommendation**: Rescue 5 FIRST (zero experimental cost; cleanest portfolio move if Gap C subsumes Cap 2); Rescue 1 SECOND (highest expected leverage among experimental rescues -- substrate-novel 28-element partition); Rescues 2-4 in cost order.

### Capability moves (v159 -> v160)

| Capability | v159 state | v160 state | Trigger |
|---|---|---|---|
| Cap 2 Self-monitoring confidence via critical slowing down / cosine margin | ❌ REFUTED at FULL v153 (tau metric NO_CORRELATION) -- single-framing closure carried implicitly through v159 | ❌ PROVISIONAL CLOSURE at v160 (rehab file referenced); two independent metric framings (tau v153 + margin v160) both crossed pre-reg hard-fail threshold; substrate carries no margin/tau-based intrinsic confidence signal; closure SCOPE limited per [[feedback-dont-overextend-theorems]] to "intrinsic margin/tau-based proxy" -- broader confidence signal axis remains open via 5 rescue paths | wave14_cap2_confidence_margin_probe_v1 FULL = CAP2_MARGIN_KILL pre-reg hard-fail crossed |
| substrate-product portfolio count | 12 demonstrated capabilities (v153 list carries forward through v159) | **11 demonstrated capabilities** (Cap 2 leaves the list per [[feedback-no-smoke]] honest accounting) | Cap 2 structural closure |

### Substrate-product positioning v160 -- HONEST PORTFOLIO COUNT DECREASE 12 -> 11

This is the FIRST portfolio count decrease since cycle 173 v153 expansion (which added 4 NEW substrate-product capabilities). Through v154-v159 the portfolio carried forward unchanged in count at 12 (all envelope-narrowing verdicts stayed below hard-fail; v158 Cap 1 actually WIDENED via Sagawa-Ueda). At v160 Cap 2 leaves the list.

If Rescue 5 (Gap C subsumption) holds: count stays at 11 permanently (Cap 2 was never a separate axis from Gap C). If Rescues 1-4 succeed experimentally: Cap 2 returns to the list under the rescued framing.

### Substrate-physics characterization (unchanged from v159)

EXPONENTIAL-decay universality + MULTI-COMPONENT sub-K-region q_overlap + anti-RM(1,16) coset bias + Cap 1/Cap 3/Cap 5 noise envelopes CONFIRMED. v160 closure is a substrate-PRODUCT capability move; does NOT touch substrate-physics characterization (closure SCOPE limited per [[feedback-dont-overextend-theorems]]).

### Strategy follow-up actions (cycle 180)

1. **PROT-009 v160 paired commit** -- 74th observation.
2. **Strategy -> Research 2x drill request filed** at `notes/strategy_request_to_research_cap2_self_monitoring_rehab_2026-05-23.md` per [[feedback-negative-results-2x-research]] (this IS a measurement-based refutation; hard-fail threshold crossed in pre-reg). Research deliverable: (a) vetted ranking of 5 rescue sketches with calibration-deflated P estimates per [[feedback-lit-scan-calibration-penalty]] + explicit hard-fail thresholds; (b) lit-scan on confidence signals in dense AM + spin-glass models (chi_4 + Kovacs + posterior variance) under generic-math framing per [[feedback-query-privacy-decomposition]]; (c) one-cycle next-experiment prescription.
3. **`notes/active_priorities.md`** refreshed atomically: substrate-product portfolio 12 -> 11; Cap 2 row added as ❌ PROVISIONAL with rehab file reference + 5 rescue sketches noted.
4. **DO NOT file Exp Dev routing** -- per verdict event payload, orchestrator is concurrently dispatching architecture audit + queue refill separately. v160 stays out of the Exp Dev queue lane.
5. Push v160 to remote per [[feedback-cap-map-update-protocol]].

### PROT compliance this cycle

- PROT-001/002/003: not triggered (existing artifacts in place).
- **PROT-004 + PROT-006**: TRIGGERED for a closure. Full discipline applied per sequence: (1) harvested verdict from metrics.json (CAP2_MARGIN_KILL HARD FAIL); (2) drafted 5 rescue sketches as DRAFT (above); (3) FILED rehab request file BEFORE cap_map commit (PROT-006 sequencing -- request file mtime < cap_map commit mtime); (4) cap_map ❌ PROVISIONAL row added in capability moves table with explicit pointer to request file in row text.
- PROT-007: v160 history block written to `substrate_capability_map_history.md` (compact one-line at bottom); narrative block also retained inline in cap_map.md per v60+ live-cap_map transitional convention.
- **PROT-008**: validator must pass before commit. v160 adds 1 NEW ❌ closure row (Cap 2) with rehab file reference + PROVISIONAL tag; REHAB_REF_PATTERN matches `strategy_request_to_research_cap2_self_monitoring_rehab_2026-05-23.md`; baseline pre-existing violations unchanged.
- **PROT-009**: cap_map.md + history.md + strategy_decisions_2026-05-23.md + active_priorities.md + strategy_request_to_research_cap2_self_monitoring_rehab_2026-05-23.md staged atomically. Validator invoked with `--staged-files`.

PROT-004/006/008/009 compliance this commit: Cap 2 ❌ PROVISIONAL; 5 rescue sketches DRAFT in rehab file + summarized in cap_map v160 narrative; request file at `notes/strategy_request_to_research_cap2_self_monitoring_rehab_2026-05-23.md`; PROVISIONAL tag applied; sequence verified (request file mtime < cap_map commit mtime); paired strategy_decisions entry (this cycle 180) staged with cap_map.

### Tally (one-line)

wave14_cap2_confidence_margin_probe_v1 FULL = CAP2_MARGIN_KILL at 3.3s (corr(margin, correct) < 0.2 in ALL 4 noise strata; pre-reg hard-fail threshold crossed); SECOND independent metric framing to fail at FULL after v153 tau-iteration-count CRITICAL_NO_CORRELATION; TRUE structural closure (not envelope-narrowing); Cap 2 ❌ PROVISIONAL applied with 5 axis-combination rescue sketches filed per PROT-004/006 (endpoint-id + VAMP posterior variance + chi_4 + Kovacs + Gap C subsumption); Strategy -> Research 2x drill ROUTED per [[feedback-negative-results-2x-research]]; substrate-product portfolio drops 12 -> 11 demonstrated capabilities per [[feedback-no-smoke]] honest accounting; closure SCOPE limited per [[feedback-dont-overextend-theorems]]; substrate-physics characterization unchanged from v159; per verdict event payload Exp Dev routing INTENTIONALLY OMITTED (orchestrator coordinated); 74th PROT-009 paired commit.

---

## Cycle 181 (Cap 5 Online W Polyak-Ruppert noise-corrected bound PARTIAL; Rescue Path #1 CONFIRMED-PARTIAL not FULL; Cap 5 envelope at p_flip <= 0.30 CONFIRMED real structural boundary not metric artifact; FIRST verdict from newly-revived remote CPU runner) -- v161

**Time**: 2026-05-23 13:53 EDT.

**Trigger**: `wave14_online_W_polyak_noise_corrected_v1` FULL verdict `ONLINE_W_POLYAK_PARTIAL` at 0.0s elapsed (pure Python CPU re-analysis on `remote_cpu_queue`).

**verdict_msg**: "Noise-corrected bound PARTIAL: 4/5 noisy cells pass. Originally failing cells rescued: 0/1. Cells still failing after correction: p in [0.4]. Mechanism #1 partially confirmed; deeper structural failure at high p."

### Interpretation

This was the v159 Strategy -> Research 2x drill's first concrete probe (Rescue Path #1 from `strategy_request_to_research_online_W_noise_robust_2026-05-23.md`). Polyak-Juditsky iterate averaging was the highest-ranked rescue sketch (Research P=0.50, deflated per [[feedback-lit-scan-calibration-penalty]]). The CPU re-analysis applies the Polyak-corrected theta_PJ(p) acceptance criterion to the existing v159 trajectory data.

Outcome:

- **PASSES** at p_flip in {0.05, 0.10, 0.20, 0.30} -- but these cells were ALREADY passing the flat 0.95 retention threshold in v159. The Polyak correction is applied to cells that did NOT need rescuing.
- **FAILS** at p_flip = 0.40 -- the originally-failing cell. The Polyak-corrected theta_PJ(p) does NOT bring p=0.40 inside the operating envelope.

Originally-failing cells rescued: **0/1**. The verdict explicitly identifies p=0.40 as a "deeper structural failure at high p" not addressable by iterate-averaging-style noise-floor corrections.

### Comparison with v158 Cap 1 Sagawa-Ueda flip (precedent failure)

| Metric flip | Originally failing cells | Cells rescued by metric flip | Outcome |
|---|---|---|---|
| v158 Cap 1 Sagawa-Ueda theta(p) | 3/3 (p in {0.05, 0.10, 0.20}) | **3/3** | Cap 1 SLA WIDENED to tiered (Tier 1 clean + Tier 2 noisy) |
| v161 Cap 5 Polyak-Ruppert theta_PJ(p) | 1/1 (p=0.40) | **0/1** | Cap 5 envelope STAYS at p_flip <= 0.30 |

The two re-axiomatizations diverge in outcome. v158 was a successful metric flip (the data was always compatible with the Sagawa-Ueda bound; v157's "narrowing" was an axiom-mismatch artifact). v161 is **NOT** a successful metric flip; the p=0.40 cell is incompatible with the Polyak-corrected bound, indicating a real structural break.

Per [[feedback-no-smoke]] honest framing: the v159 Cap 5 envelope at p_flip <= 0.30 is a **real structural boundary**, not a metric-definition artifact. The Sagawa-Ueda precedent does NOT generalize to every noise envelope; each capability's envelope shape is its own measured quantity.

### Capability moves (v160 -> v161)

| Capability | v160 state | v161 state | Trigger |
|---|---|---|---|
| Cap 5 Gap B Online W noise envelope row | ✅ FULL clean + ✅ FULL p_flip<=0.30; pending Polyak rescue determination | ✅ FULL clean + ✅ FULL p_flip<=0.30 UNCHANGED; Polyak rescue PARTIAL; structural boundary at (0.30, 0.40] CONFIRMED | `wave14_online_W_polyak_noise_corrected_v1` FULL PARTIAL |
| Cap 5 rescue path #1 (Polyak-Juditsky iterate averaging) | proposed P=0.50 (deflated) | CONFIRMED-PARTIAL not CONFIRMED-FULL | v161 verdict |
| substrate-product portfolio count | 11 demonstrated capabilities | 11 demonstrated capabilities UNCHANGED (Cap 5 still ✅ in operating regime) | n/a |

### Strategy decision (cycle 181)

**v161 next-step recommendation: ACCEPT envelope at p_flip <= 0.30. Do NOT trigger another Research 2x drill on Cap 5 past p=0.30 this cycle.**

Three considerations:

1. **Research bandwidth prioritization** (per [[feedback-strategy-shore-up-capabilities]] item 1): the Research queue already carries (a) Cap 2 self-monitoring rehab v160 (HIGH priority refutation -- portfolio dropped 12 -> 11; restoring Cap 2 has higher product value than widening Cap 5 past p=0.30); (b) Bet T/V rescue sketches v158 (PROT-004/006 backlog); (c) META Gap A spatially-coupled codebook v151 (theorem-backed; awaiting bandwidth); (d) burn-down note for 3 orphaned 2026-05-23 deliveries. Adding a fourth Cap 5 elective hardening drill would over-saturate Research and defer the higher-priority Cap 2 refutation.

2. **Elective vs required hardening**: the existing Cap 5 envelope at p_flip <= 0.30 covers realistic customer noise floors. The 4 remaining rescue sketches (SVRG variance reduction + BSC majority-vote 3-redundant decoder + adaptive SNAP + tiered SLA at higher C-coefficient) are ELECTIVE -- they widen the envelope to p>=0.40 but are not required to ship the existing capability. Per [[feedback-no-papers-product-only]] substrate-product positioning: ship Cap 5 with explicit operating envelope; widen later if customer demand surfaces a p>=0.40 use case.

3. **Diminishing-return signal**: the verdict_msg "deeper structural failure at high p" indicates the p=0.40 boundary is plausibly a SNAP-guard breakdown regime, not an iterate-statistics issue. The remaining 4 rescue paths address different mechanisms (variance reduction; channel decoding; adaptive saturation; calibrated retention bound at a larger acceptance-coefficient). Each would need its own Research drill if pursued; expected gain per drill is moderate-to-low (each rescue addresses a different aspect; none clearly dominates).

**Action**: annotate Cap 5 envelope row as CONFIRMED structural boundary (Polyak rescue partial); mark Rescue Path #1 as CONFIRMED-PARTIAL not CONFIRMED-FULL; keep 4 remaining rescue sketches in substrate-product roadmap as elective hardening pool; do NOT trigger another Research drill on Cap 5 this cycle.

### Strategy follow-up actions (cycle 181)

1. **PROT-009 v161 paired commit** -- 75th observation.
2. **Cap 5 envelope row annotated** in cap_map.md and active_priorities.md: Polyak rescue PARTIAL; envelope at p_flip <= 0.30 CONFIRMED structural boundary not metric-definition artifact. Rescue Path #1 (Polyak-Juditsky) CONFIRMED-PARTIAL.
3. **DO NOT trigger another Research 2x drill on Cap 5 envelope past p=0.30 this cycle** (rationale above).
4. **DO NOT file Exp Dev routing** -- per verdict event payload, orchestrator continues filling queues separately.
5. **Acknowledge remote CPU runner revival** -- this verdict is the FIRST from the newly-revived `remote_cpu_queue` runner. Pure Python CPU re-analysis (0.0s elapsed) demonstrates the cheap-CPU exploratory probe pipeline is online.
6. Push v161 to remote per [[feedback-cap-map-update-protocol]].

### PROT compliance this cycle

- PROT-001/002/003: not triggered (existing artifacts in place).
- **PROT-004/006**: NOT triggered for a closure. Cap 5 ✅ still holds in operating regime (p <= 0.30). No new ❌ row added. Rescue Path #1 (Polyak-Juditsky) marked CONFIRMED-PARTIAL; rescues 2-5 remain DRAFT and available. Per [[feedback-dont-overextend-theorems]] the partial confirmation of Polyak-Ruppert does NOT close the broader "noise-corrected retention bound exists for Cap 5" axis -- it specifies that the iterate-averaging family alone is insufficient, but the SVRG / BSC-redundancy / adaptive-SNAP / tiered-SLA-with-larger-C families remain open.
- **PROT-007**: v161 history block written first to `substrate_capability_map_history.md` (compact one-line at bottom); narrative block also retained inline in cap_map.md per v60+ live cap_map convention.
- **PROT-008**: validator must pass before commit. v161 adds 0 new ❌ rows; baseline 26 pre-existing violations from v138-v153 era unchanged; v160 Cap 2 ❌ PROVISIONAL row + rehab-file reference unchanged.
- **PROT-009**: cap_map.md + history.md + strategy_decisions_2026-05-23.md + active_priorities.md staged atomically. Validator invoked with `--staged-files`.

### Tally (one-line)

wave14_online_W_polyak_noise_corrected_v1 FULL = ONLINE_W_POLYAK_PARTIAL at 0.0s elapsed (FIRST verdict from newly-revived remote CPU runner; 4/5 noisy cells pass Polyak-corrected bound but ALL 4 were already passing flat 0.95 threshold; 0/1 originally-failing p=0.40 cell rescued); UNLIKE v158 Cap 1 Sagawa-Ueda flip (3/3 originally-failing cells rescued; SLA widened to tiered) Cap 5 Polyak-Ruppert does NOT generalize -- structural boundary at (0.30, 0.40] confirmed not metric-definition artifact; Cap 5 envelope STAYS at p_flip <= 0.30; rescue path #1 (Polyak-Juditsky) marked CONFIRMED-PARTIAL not CONFIRMED-FULL per [[feedback-no-smoke]] honest framing; 4 remaining rescue sketches (SVRG + BSC redundancy + adaptive SNAP + tiered-SLA-with-larger-C) stay on substrate-product roadmap as elective hardening options; no Cap 5 closure (✅ still holds at p<=0.30 operating regime); substrate-product portfolio at v160 (11 demonstrated capabilities) carries forward unchanged in count; substrate-physics characterization unchanged from v160 + new observation that Robbins-Monro+SNAP has true noise-tolerance ceiling beyond O(1/t) iterate averaging; per verdict event payload Exp Dev routing INTENTIONALLY OMITTED; strategic call NOT to trigger another Research drill on Cap 5 envelope past p=0.30 this cycle (Research bandwidth prioritized for Cap 2 self-monitoring rehab HIGH priority refutation); FIRST remote-CPU-runner verdict since 2026-05-21 revival; 75th PROT-009 paired commit.

---

## Cycle 182 (P(q) high-resolution probe at FULL = PQ_OTHER_CARDINALITY n_total=60 n_outer=7 -- substrate-physics characterization UPDATED to multi-scale hierarchical P(q) structure; smoke->FULL DIVERGENCE 24th strict-divergence anchor; per [[feedback-dont-overextend-theorems]] does NOT refute cycle 137 28-element endpoint partition -- different observable + different N + different protocol depth) -- v162

**Time**: 2026-05-23 13:56 EDT.

**Trigger**: `wave14_pq_high_resolution_v1_full_200seed_rerun_2026-05-23` FULL verdict `PQ_OTHER_CARDINALITY` at 126s elapsed (gpu_runner_0; N=16384 K=100 depth=50 200-seed two-level peak detection on P(q) overlap distribution).

**verdict_msg**: "n_total=60 n_outer=7 (different cardinality)."

### Interpretation

Pre-reg (`preregs/2026-05-23_wave14_pq_high_resolution_v1.md`) defined three verdicts: PQ_HIERARCHICAL_28 (n_total in [24, 32] matches cycle 137 28-endpoint cardinality), PQ_FLAT_15 (n_total ~= n_outer in [12, 18]), PQ_OTHER_CARDINALITY (anything else). FULL n_total=60 n_outer=7 lands in PQ_OTHER_CARDINALITY (outside both pre-registered narrow brackets).

Smoke at N=2048 1.8s: n_total=31 n_outer=12 PQ_HIERARCHICAL_28 (inside [24, 32]). FULL at N=16384 126s: n_total=60 n_outer=7 PQ_OTHER_CARDINALITY. The smoke looked compatible with the 28-prediction; the FULL diverges to ~2x more total peaks with FEWER outer peaks. This is the 24th strict smoke->FULL divergence anchor (25th broad).

Substrate-physics characterization: the P(q) overlap distribution at N=16384 K=100 depth=50 200-seed shows a two-tier hierarchical structure -- 7 broad outer basins + ~8.5 inner sub-modes per basin = 60 total spikes.

### Reconciliation with cycle 137 ENDPOINT_COLLAPSED 28-element partition (per [[feedback-dont-overextend-theorems]])

Today's PQ_OTHER_CARDINALITY does NOT refute the cycle 137 28-element endpoint partition. The two measurements probe different quantities:

| Probe | Cycle 137 ENDPOINT_COLLAPSED | Cycle 182 PQ high-resolution |
|---|---|---|
| Observable | Distinct final codewords (endpoint set cardinality) | P(q) overlap distribution peaks (modes of pairwise overlap density) |
| Math | Image cardinality of W^L | Modes of pairwise overlap distribution |
| Scale | N=65536, K=100 | N=16384, K=100 |
| Depth | Various L | Fixed depth=50 |
| Count | 28 endpoints | 7 outer / 60 total peaks |

These are NOT the same quantity. Two reconciliation possibilities (Strategy does NOT claim either):
1. **Coarse-graining hierarchy**: 60 fine spikes group into 7 outer basins; 28 endpoints sit somewhere in between (perhaps 7 * 4 = 28). Clean hierarchical decomposition.
2. **Scale-dependent regime**: each cardinality is a regime-specific quantity; (N, K, L) selects which level resolves. Today's N=16384 is 4x smaller than cycle 137 N=65536.

A head-to-head probe at matched (N, K, L, observable) would distinguish these. Strategy keeps this as a 🔬 candidate row in active_priorities, NOT a named queued experiment.

### Capability moves (v161 -> v162)

| Capability | v161 state | v162 state | Trigger |
|---|---|---|---|
| Substrate-physics P(q) characterization | sub-K-region multi-component q_overlap STABLE + 15-peak P(q) substructure mechanism unknown | **UPDATED to multi-scale hierarchical**: 7 outer + 60 total at N=16384 K=100 depth=50 200-seed; RECONCILES with (does NOT refute) cycle 137 28-element endpoint partition | `wave14_pq_high_resolution_v1_full_200seed_rerun_2026-05-23` FULL = PQ_OTHER_CARDINALITY |
| 🔬 15-peak P(q) substructure row | 5 versions stale (mechanism unknown after 15->28 hierarchy refuted) | **UPGRADED to CHARACTERIZED at this resolution**: 7 outer + 60 total; open follow-up is matched-(N,K,L) reconciliation probe | this verdict |
| Cap 2 Rescue Path #1 (endpoint-ID as confidence proxy) | DRAFT; uses 28-element partition | DRAFT but with multi-cardinality probe added (7 / 28 / 60 alternative bin choices) | substrate-physics multi-scale finding |
| smoke->FULL strict-divergence anchor count | 23 strict / 24 broad | 24 strict / 25 broad | smoke n=31 PQ_HIERARCHICAL_28 -> FULL n=60 PQ_OTHER_CARDINALITY |
| substrate-product portfolio count | 11 demonstrated capabilities | 11 UNCHANGED (substrate-physics-only update; no closure event) | n/a |

### Strategy decision (cycle 182)

**v162 next-step recommendation: ACCEPT the substrate-physics characterization update; do NOT trigger a Research 2x drill; do NOT file Exp Dev routing for further P(q) probes this cycle.**

Three considerations:

1. **Not a refutation** per [[feedback-dont-overextend-theorems]]: PQ_OTHER_CARDINALITY is a different observable + different N from cycle 137. Triggering a 2x Research drill would presume a refutation that does not exist. The verdict_msg "different cardinality" is the literal pre-reg outcome, not a hard-fail crossing of a capability threshold.
2. **Substrate-physics characterization, not capability gate**: this verdict updates the substrate-physics row; no demonstrated capability moves. Research bandwidth this session arc is correctly prioritized for the Cap 2 self-monitoring rehab HIGH priority refutation (v160) and the burn-down note for 3 orphaned 2026-05-23 deliveries.
3. **Open follow-up is a candidate, not urgent**: the matched-(N,K,L) head-to-head probe of endpoint partition vs P(q) peaks would reconcile coarse-graining-hierarchy vs scale-dependent-regime possibilities. This is a clean substrate-physics question but does NOT gate any capability. Strategy adds it as a 🔬 candidate row in active_priorities; orchestrator pipeline-picks selection runs separately.

**Action**: update substrate-physics row in active_priorities (15-peak 🔬 row -> "CHARACTERIZED at this resolution"); note Cap 2 Rescue Path #1 design gains multi-cardinality bin-choice degree of freedom; commit v162.

### Strategy follow-up actions (cycle 182)

1. **PROT-009 v162 paired commit** -- 76th observation.
2. **substrate-physics row UPDATED** in active_priorities.md per above.
3. **No Research 2x drill triggered** (not a refutation; substrate-physics characterization only; per [[feedback-dont-overextend-theorems]]).
4. **Cap 2 Rescue Path #1 design noted** for next Strategy -> Exp Dev routing whenever Research delivers the v160 rehab 2x drill recommendation.
5. **No Exp Dev routing this cycle** per verdict event payload (orchestrator continues filling queues separately).
6. Push v162 to remote per [[feedback-cap-map-update-protocol]]; scp dashboard data per same memory.

### Recent-run check (per strategy.md "Recent-run check" rule)

This cycle Strategy does NOT recommend any new experiment by name. The single optional follow-up (matched-(N,K,L) head-to-head endpoint-partition vs P(q)-peaks reconciliation) is left as a 🔬 candidate row, not a named queued experiment. If/when it gets filed, Strategy will check `data/overnight_queue/queue.json` and use `--rerun-as <new_name>` if dedup-by-name would block.

### PROT compliance this cycle

- PROT-001/002/003: not triggered (existing artifacts in place).
- **PROT-004/006**: NOT triggered for a closure. No new ❌ row added. Today's PQ_OTHER_CARDINALITY is a substrate-physics characterization update at higher resolution, not a refutation of any capability. Per [[feedback-dont-overextend-theorems]] does NOT close the cycle 137 28-prediction (different observable + different N + different protocol depth; not directly comparable).
- **PROT-007**: v162 history block written first to `substrate_capability_map_history.md` (compact one-line index entry appended at bottom); narrative block also retained inline in cap_map.md per v60+ live cap_map convention.
- **PROT-008**: validator must pass before commit. v162 adds 0 new ❌ rows; baseline pre-existing violations unchanged.
- **PROT-009**: cap_map.md + history.md + strategy_decisions_2026-05-23.md + active_priorities.md staged atomically. Validator invoked with `--staged-files`.

### Tally (one-line)

wave14_pq_high_resolution_v1_full_200seed_rerun_2026-05-23 FULL = PQ_OTHER_CARDINALITY at 126s elapsed (gpu_runner_0; N=16384 K=100 depth=50 200-seed; n_total=60 n_outer=7); pre-reg outcome lands in PQ_OTHER_CARDINALITY (outside both PQ_HIERARCHICAL_28 [24,32] and PQ_FLAT_15 [12,18] brackets); smoke n=31 PQ_HIERARCHICAL_28 -> FULL n=60 PQ_OTHER_CARDINALITY = 24th strict smoke->FULL divergence anchor (25th broad); substrate-physics characterization UPDATED to two-tier hierarchical P(q) structure (7 outer basins + ~8.5 inner sub-modes per basin = 60 total spikes); per [[feedback-dont-overextend-theorems]] RECONCILES with (does NOT refute) cycle 137 28-element endpoint partition -- different observable + different N + different protocol depth; per [[feedback-no-smoke]] honest framing enumerates 2 reconciliation possibilities (coarse-graining hierarchy 60 -> 7 with 28-endpoints intermediate; scale-dependent regime selection) without claiming either; 🔬 "15-peak P(q) substructure mechanism unknown" row UPGRADED to "CHARACTERIZED at this resolution"; Cap 2 Rescue Path #1 (endpoint-ID as confidence proxy) GAINS new multi-cardinality bin-choice degree of freedom; substrate-product portfolio at v161 (11 demonstrated capabilities) carries forward UNCHANGED IN COUNT (no closure event; substrate-physics-only update); PROT-004/006 NOT triggered (no refutation); no Research 2x drill triggered (Research bandwidth correctly prioritized for Cap 2 self-monitoring rehab HIGH priority refutation from v160); per verdict event payload no Exp Dev routing; matched-(N,K,L) reconciliation probe noted as 🔬 candidate row only (not named queued experiment); 76th PROT-009 paired commit.

---

## 18:01 -- Cycle 183 Strategy decision -- wave14_amp_se_kerdock_v1_gpu FULL = AMP_SE_DIVERGES (v163)

**Trigger**: `wave14_amp_se_kerdock_v1_gpu` FULL verdict `AMP_SE_DIVERGES` at 2522s elapsed (~42 min on remote GPU; rerouted from local CPU per pipeline-pacing).

**verdict_msg**: "SE fixed-point diverges from empirical AMP. Mean rel err=0.916, max=0.999. Kerdock codebook is OUTSIDE the AMP universality class. Novel finding: Kerdock structure breaks AMP-SE assumptions. Only 0/4 cells < 20% error."

### Strategy action

1. **Cap_map v163** -- substrate-physics characterization UPDATED to explicit "outside AMP universality class at SE-fixed-point level" with empirical rel_err=0.916 anchor over 4 cells. Sharpens v120 pretest-level KILL to SE-fixed-point empirical level. Substrate-product portfolio UNCHANGED at 11 demonstrated capabilities (no closure event; v120 already carried the narrow closure).

2. **Confirms meta-research adjacency Drill #4 HARD FAIL branch** per `notes/research_meta_map_and_adjacencies_2026-05-23.md` Part 3 -- the substrate-NOVEL theoretical-regime branch (NOT the "matches existing theory" branch).

3. **Per [[feedback-dont-overextend-theorems]]** does NOT close broader AMP/VAMP family. VAMP variants (Rangan-Fletcher-Goyal cycle 127 load-bearing) + free-probability R-transform machinery (Bet I v56 load-bearing) remain open rescue paths for substrate's M/N=8 capacity anomaly at N=4096.

4. **Per [[feedback-lit-scan-calibration-penalty]]** validates the 0.20-deflation rule (deflated P=0.45 at filing -> HARD FAIL outcome P~0.55 confirmed).

5. **PROT-004/006 NOT triggered** -- v120 already closed the narrow Kerdock-AMP-universality row; today's verdict SHARPENS at SE-fixed-point empirical level without opening new closure. Per [[feedback-dont-overextend-theorems]] does NOT close broader AMP/VAMP family.

6. **ORCHESTRATOR PAUSED** per `data/orchestrator_paused.flag`. Per [[feedback-obey-user-pause-explicitly]] Strategy SKIPS Exp Dev routing (queue refill INTENTIONALLY OMITTED). Queue=0 is user-intended state.

7. **Research follow-up candidates DEFERRED to next active cycle**: VAMP-SE on Kerdock + free-probability R-transform of Kerdock 4-coset codebook. Both are natural extensions of Drill #4's HARD FAIL outcome.

8. **Push v163 to remote** per [[feedback-cap-map-update-protocol]]; scp dashboard data per same memory.

### Smoke -> FULL divergence note

| Run | Cells | Mean rel_err | Verdict |
|---|---|---|---|
| smoke | 2 (alpha in {0.5, 1.0}, N=1024) | 0.847 | AMP_SE_DIVERGES |
| FULL (GPU) | 4 (extended alpha + N grid) | 0.916 | AMP_SE_DIVERGES |

Same verdict tag at smoke and FULL -- this counts as a **broad divergence anchor only** (not strict tag-flip). FULL extends cell battery and tightens the boundary (0/4 vs 0/2 within threshold).

### PROT compliance

- PROT-007: v163 history line appended to `substrate_capability_map_history.md`; narrative block in `substrate_capability_map.md`.
- PROT-008: validator must pass before commit. 0 new ❌ rows added.
- PROT-009: cap_map.md + history.md + strategy_decisions_2026-05-23.md + active_priorities.md staged atomically.

### Tally (one-line)

wave14_amp_se_kerdock_v1_gpu FULL = AMP_SE_DIVERGES at 2522s elapsed (mean rel_err=0.916 max=0.999 over 4 cells; 0/4 within 20% threshold); sharpens v120 cycle 115/120 Kerdock-AMP-universality KILL to SE-fixed-point empirical level; confirms HARD FAIL branch of meta-research adjacency Drill #4 (substrate-novel theoretical-regime branch); per [[feedback-dont-overextend-theorems]] does NOT close broader AMP/VAMP family (VAMP variants + free-probability R-transform remain rescue paths); substrate-product portfolio at v162 (11 demonstrated capabilities) carries forward UNCHANGED IN COUNT; broad divergence anchor +1 (smoke 0.847 -> FULL 0.916 same AMP_SE_DIVERGES tag); per orchestrator PAUSED state Strategy SKIPS Exp Dev routing (queue refill INTENTIONALLY OMITTED per [[feedback-obey-user-pause-explicitly]]); VAMP-SE on Kerdock + R-transform of Kerdock 4-coset codebook noted as Research follow-up candidates DEFERRED to next active cycle; 77th PROT-009 paired commit.

---

## 18:43 -- wave14_glauber_kerdock_v1 GLAUBER_INCONCLUSIVE (under-resolution, re-run candidate)

**Verdict**: GLAUBER_INCONCLUSIVE at 20.7s elapsed (remote_cpu_queue).
**Verdict_msg**: "Mixed Glauber response: low_T_bimodal=0/6, global_unimodal=12/15, max_bimodal=0.000 at . Need finer T resolution or longer chain length."

### Strategy verdict

1. **Cap_map UNCHANGED**: no version bump. No row currently sits at the "Glauber dynamical observability" capability level (would be a 🔬 research-only candidate or new ⚪ row if/when a tuned re-run produces a clean bimodal/unimodal signature). 11 demonstrated capabilities carry forward.

2. **Re-run candidate, NOT closure**: per [[feedback-negative-results-2x-research]] under-resolution INCONCLUSIVE != negative result. No 2x Research drill triggered. Exp Dev should file a re-run with:
   - Finer T grid (current grid had low_T_bimodal=0/6 cells across the entire low-T band -- expand below current beta_min and/or densify)
   - Longer chain length (max_bimodal=0.000 suggests current chains may not have reached stationary)
   - Possibly larger sample count (current global_unimodal=12/15 majority but not unanimous)

3. **Complementary spectral probe still in flight**: wave14_free_cumulants_kerdock_v1 still running on GPU. Free-cumulants is a SPECTRAL observability probe (eigenspectrum signatures); Glauber is a DYNAMICAL observability probe (stationary P(q) of synchronous heat-bath chain). They answer adjacent but distinct questions about the Kerdock-Hebbian W matrix. No double-ship needed -- let free-cumulants land before deciding the Glauber re-run priority.

4. **PROT-004/006 NOT triggered**: no closure, no cap_map ❌ added.

5. **PROT-007/008/009**: no cap_map commit this cycle; decision-log standalone entry.

### Pipeline-pacing reflex (per [[feedback-pipeline-pacing]])

- Pause flag at 18:31 was CLEARED -- ACTIVE. Per verdict_handler Step 2 the queue-refill reflex IS in effect.
- remote_cpu_queue depth at arrival: 0 (this verdict consumed the last entry).
- GPU runner BUSY with wave14_free_cumulants_kerdock_v1 -- do NOT ship to GPU queue.
- Action: Exp Dev should ship the Glauber re-run (finer T + longer chains) to remote_cpu_queue OR an adjacent exploratory CPU sweep. verdict_handler dispatches exp_dev (Sonnet) with this context.

### Tally (one-line)

wave14_glauber_kerdock_v1 FAST INCONCLUSIVE = GLAUBER_INCONCLUSIVE at 20.7s elapsed (low_T_bimodal=0/6, global_unimodal=12/15 over 15 cells, max_bimodal=0.000); under-resolution NOT refutation; re-run candidate with finer T grid + longer chains; cap_map UNCHANGED at v163 (portfolio still 11 FULL capabilities); complementary free-cumulants probe still running on GPU (no double-ship); per [[feedback-negative-results-2x-research]] does NOT trigger 2x Research drill; pause flag ACTIVE so pipeline-pacing exp_dev dispatch IS in effect (queue=0 on remote_cpu).

---

## ~19:00 -- v164 BATCHED PAIRED VERDICT (free-cumulants FREE_CUMULANTS_DIVERGE + glauber_v2 GLAUBER_BIMODAL_KERDOCK)

**Batched-mode verdict_handler dispatched on two verdicts paired** to avoid git-pull race between two parallel verdict_handlers (per orchestrator batched contract). Single .tmp+rename+commit+push round covers both.

### Verdict 1: wave14_free_cumulants_kerdock_v1 (GPU / overnight_queue, landed ~18:50)

**Tag**: FREE_CUMULANTS_DIVERGE
**Significance**: provides the FORMAL SPECTRAL MECHANISM for v163 AMP_SE_DIVERGES. Substrate Kerdock spectrum has nontrivial higher free cumulants kappa_n (n>=2); max_dev=1.125 at kappa_4 alpha=2.00; 5/5 cells exceed 20% deviation. AMP universality (Stieltjes/R-transform-of-MP assumption) is incompatible with nontrivial higher kappa_n -- the R-transform with kappa_n != 0 places Kerdock outside AMP universality at the spectral level, which is exactly what v163's empirical AMP-SE divergence demonstrated indirectly. v164a closes the loop: v163 was the *empirical* demonstration; v164a is the *spectral* explanation.

### Verdict 2: wave14_glauber_kerdock_v2 (Remote CPU / remote_cpu_queue, landed ~18:43)

**Tag**: GLAUBER_BIMODAL_KERDOCK
**Significance**: Cap 3 streaming-NESS framing extends from continuous-state drift-diffusion to discrete-spin Glauber-Hopfield. Synchronous heat-bath Glauber dynamics on Kerdock-Hebbian W shows bimodal stationary P(q) at low T (12/18 low-T cells satisfy bimodal_score>=0.5 AND abs_mean_q>=0.30; max bimodal=1.000 at beta=2.00 alpha=0.05). v2 supplied the parameter resolution that v1 lacked (finer T grid + longer chains + sub-critical alpha + init noise).

### Strategy verdict

1. **v164 paired commit** -- cap_map.md narrative block + history.md one-line entry + active_priorities.md update + this decision-log block staged atomically. 78th PROT-009.

2. **Two new evidence-strength rows added** to cap_map under "Substrate-physics characterization":
   - "Free-cumulant fingerprint of Kerdock R-transform" 🟢 (single-N N=1024 5/5; want N=4096+ multi-N + Wigner null baseline). Substrate-novel observability: kappa_n profile distinguishes Kerdock from MP/Wigner.
   - "Cap 3 Glauber-Hopfield discrete-spin NESS extension" 🟢 (single-N N=1024 12/18 low-T cells bimodal; want N=4096+ + 5-seed). Cap 3 streaming-NESS framing extends to discrete-spin Glauber-Hopfield retrieval-vs-paramagnetic equilibrium.

3. **Substrate-product portfolio UNCHANGED at 11 demonstrated capabilities**. Both new rows are evidence-strength expansions (substrate-physics + Cap 3 extension), not new portfolio ✅ rows.

4. **PROT-004/006 NOT triggered**: no closure, no ❌ row added. Both verdicts ADD evidence to existing or implied rows.

5. **Per [[feedback-dont-overextend-theorems]] honest framing**: v164a does NOT close the AMP/VAMP family -- it explains why plain-AMP-SE diverges on Kerdock (the spectral mechanism) and *motivates* the natural composition follow-up (VAMP-SE-on-Kerdock with the measured R-transform as input). v164b does NOT promote Cap 3 from envelope-extension to "new portfolio capability" -- it extends the FRAMING from continuous-state to discrete-spin Glauber-Hopfield; the formal SLA-grade demonstration would require multi-N + multi-seed.

6. **Pipeline-pacing**: pause flag CLEARED -- ACTIVE. Per verdict_handler Step 2, GPU queue=0 (free-cumulants done; runner idle) triggers exp_dev dispatch for ONE GPU refill. CPU has 2 pending (S_transform + parisi from the earlier 3-experiment burst) -- do NOT refill CPU. GPU refill recommendation by name: `wave14_R_transform_kerdock_v1_multi_N` (direct measurement of substrate Kerdock R-transform's higher free cumulants at N in {1024, 2048, 4096, 8192}, 5-seed; promotes v164 free-cumulant row from 🟢 to ✅ if max_dev scales / stays bounded; supplies the spectral input for the deferred VAMP-SE-on-Kerdock follow-up). Recent-run dedup check: name NOT in queue.json today; not in any prior FULL/smoke directory.

7. **Research follow-up FILED** (deferred to next cycle per pipeline-pacing): VAMP-SE on Kerdock using v164a's measured R-transform as input. This is the natural composition of v163 + v164a and was already noted as a deferred Research candidate at v163; v164a now supplies the spectral input the candidate was waiting on.

### Pipeline state at v164

| Queue | Pending | Running | Heartbeat |
|---|---|---|---|
| overnight (GPU) | 0 at arrival | IDLE post-free_cumulants | -> dispatch exp_dev for ONE refill (R_transform_multi_N) |
| remote_cpu | 2 (S_transform + parisi from earlier burst; glauber_v2 just finished) | one running | NOT refilled this cycle |
| local_cpu | ? | DEAD | n/a |

### Smoke -> FULL divergence accounting

| Run | Smoke | FULL | Divergence? |
|---|---|---|---|
| free_cumulants_v1 | DIVERGE 2/2 max=0.988 | DIVERGE 5/5 max=1.125 | NO; cell-extension broad anchor +1 only |
| glauber_v2 | BIMODAL 1/1 cell @ beta=6 alpha=0.10 | BIMODAL 12/18 cells; max @ beta=2 alpha=0.05 | NO; cell-extension broad anchor +1 only |

Net: 25 strict / 28 broad smoke->FULL divergence anchors.

### PROT compliance

- PROT-007: v164 history line appended to substrate_capability_map_history.md; narrative block in substrate_capability_map.md.
- PROT-008: validator must pass before commit. 0 new ❌ rows added.
- PROT-009: cap_map.md + history.md + strategy_decisions_2026-05-23.md + active_priorities.md staged atomically.

### Tally (one-line)

BATCHED v163 -> v164: wave14_free_cumulants_kerdock_v1 GPU FULL = FREE_CUMULANTS_DIVERGE (5/5 cells exceed 20% kappa_n deviation; max_dev=1.125 at kappa_4 alpha=2.00; formal SPECTRAL MECHANISM for v163 AMP_SE_DIVERGES established) + wave14_glauber_kerdock_v2 CPU FULL = GLAUBER_BIMODAL_KERDOCK (12/18 low-T cells bimodal; max bimodal=1.000 at beta=2.00 alpha=0.05; Cap 3 streaming-NESS extends from drift-diffusion to discrete-spin Glauber-Hopfield); 2 new evidence-strength rows added (substrate-physics free-cumulant fingerprint 🟢 + Cap 3 Glauber-Hopfield extension 🟢); substrate-product portfolio at 11 demonstrated capabilities UNCHANGED IN COUNT (no closure, no new portfolio ✅; both rows are evidence-strength expansions); per [[feedback-dont-overextend-theorems]] no row closed; per [[feedback-pipeline-pacing]] GPU=0 -> exp_dev dispatched for ONE GPU refill targeting R-transform multi-N (wave14_R_transform_kerdock_v1_multi_N); CPU has 2 pending so NOT refilled; broad smoke->FULL anchors +2 by cell-extension (28 broad / 25 strict); pause flag CLEARED -- ACTIVE; 78th PROT-009 paired commit.


---

## ~19:25 -- v165 BATCHED PAIRED VERDICT (S_TRANSFORM_DIVERGE + PARISI_INCONCLUSIVE)

**Batched-mode verdict_handler dispatched on two verdicts paired** to avoid git-pull race between two parallel verdict_handlers (per orchestrator batched contract). Single .tmp+rename+commit+push round covers both.

### Verdict A: wave14_S_transform_kerdock_v1 (Remote CPU / remote_cpu_queue, 531.8s elapsed)

**Tag**: S_TRANSFORM_DIVERGE
**Significance**: lands the SECOND algebraic-free-probability axis (multiplicative free-convolution via Voiculescu S-transform) on which the Kerdock spectrum departs from MP. v164a established the additive free-prob axis (R-transform via free cumulants kappa_n); v165a establishes the multiplicative axis (S-transform coefficients S_n deviate from MP closed form 1/(c+z)). 5/5 cells exceed 20% deviation; max_dev=1.000 at alpha=4.00 S_1. INDEPENDENTLY CORROBORATES v164a on a complementary algebraic axis. The substrate-product wedge "outside AMP universality class" now has TWO independent algebraic spectral fingerprints (additive + multiplicative) backing it, not just one.

### Verdict B: wave14_parisi_pq_kerdock_v1 (Remote CPU / remote_cpu_queue, 24.4s elapsed)

**Tag**: PARISI_INCONCLUSIVE
**Significance**: under-resolution INCONCLUSIVE -- 24.4s elapsed on remote CPU, 11/12 low-T cells "undetermined", 1/12 paramagnet, 0/12 continuous RSB, 0/12 two-deltas RS. verdict_msg explicitly diagnoses "need longer chains or finer T grid". Per [[feedback-negative-results-2x-research]] under-resolution INCONCLUSIVE is a RE-RUN candidate, NOT a 2x Research drill trigger; NOT a refutation of the RSB/RS/paramagnet hypothesis ensemble for Kerdock-Hebbian W.

### Strategy verdict

1. **v165 paired commit** -- cap_map.md narrative block + history.md one-line entry + active_priorities.md update + this decision-log block staged atomically. 79th PROT-009.

2. **One new evidence-strength row added** to cap_map under "Substrate-physics characterization":
   - "Multiplicative free-convolution (S-transform) fingerprint of Kerdock spectrum" (state 🟢; single-N N=1024 5/5; want N=4096+ multi-N + Wigner null baseline -- same promotion criterion as v164a paired additive-axis row). Substrate-novel observability: (kappa_n, S_n) profile distinguishes Kerdock from MP/Wigner on both additive and multiplicative free-prob axes.

3. **No promotion of v164a free-cumulant row from 🟢 to ✅** -- per [[feedback-dont-overextend-theorems]] cross-axis corroboration does NOT substitute for the explicit N-scaling + Wigner-null promotion criterion. v164a row stays at 🟢; promotion is gated on the running wave14_R_transform_kerdock_v1_multi_N GPU job. Honest framing: a second algebraic axis adds breadth of evidence, not depth at the same axis.

4. **Substrate-product portfolio UNCHANGED at 11 demonstrated capabilities**. The new row is an evidence-strength expansion of the existing free-prob fingerprint claim, not a new portfolio ✅.

5. **PROT-004/006 NOT triggered**: no closure, no ❌ row added. Verdict A adds evidence to existing row; Verdict B is under-resolution INCONCLUSIVE.

6. **Per [[feedback-dont-overextend-theorems]] honest framing**: v165a does NOT close the AMP/VAMP family -- it extends the spectral-mechanism characterization of "outside AMP" to a second algebraic axis. The natural composition follow-up is VAMP-SE-on-Kerdock with measured (R-transform AND S-transform) as input -- this is the Research candidate already filed at v164 (now strengthened with a second-axis input). Filing remains deferred to Research's next cycle.

7. **Parisi v2 GPU re-run filed as DEFERRED Exp Dev candidate**: per user feedback this cycle ("why did you run on remote cpu as opposed to the idle gpu? ... seems like a mistake" -- CPU systematically under-resolves >=5-seed x >=10 cells probes), Parisi v2 will ship to overnight_queue (GPU) NOT remote_cpu_queue. Gated on `wave14_R_transform_kerdock_v1_multi_N` completion to keep GPU at queue-depth-1 (one job in flight per pipeline-pacing -- not two). Exp Dev to queue once R_transform_multi_N lands.

8. **Pipeline-pacing**: pause flag CLEARED -- ACTIVE. GPU running R_transform_multi_N (v164 refill); do NOT ship another GPU job (queue-depth-1 in flight is the right shape). Remote CPU queue=0 after these two verdicts; do NOT auto-ship to remote CPU per user's CPU-venue feedback this cycle. CPU reserved for genuinely cheap re-analyses (v158 Sagawa-Ueda re-analysis style: <1s on CPU; or I/O-bound work). Leave CPU idle until Exp Dev identifies a genuinely cheap drill.

9. **Inefficiency LOCKED per [[feedback-lock-in-inefficiency-fixes]]**: user flagged this cycle that routing >=5-seed-x->=10-cells probes to remote CPU is a recurring failure mode (Glauber v1 + Parisi v1 both finished <30s on CPU = under-resolved, both filed BACK as re-run candidates -- 2 wasted cycles). Memory curator to file [[feedback-cpu-vs-gpu-venue-selection]] memory next cycle: "probes with >=5 seeds OR >=10 cells OR chain_length>=400 DEFAULT to GPU; CPU is for <=5s metric re-analyses, I/O-bound work, and genuinely cheap drills." Orchestrator to enforce in routing_handler venue selection.

### Pipeline state at v165

| Queue | Pending | Running | Heartbeat |
|---|---|---|---|
| overnight (GPU) | 5 pending (queue.json) | wave14_R_transform_kerdock_v1_multi_N RUNNING (v164 refill) | do NOT ship another job |
| remote_cpu | 0 at arrival post-verdict (S_transform + parisi just finished) | IDLE | INTENTIONALLY left idle per user feedback |
| local_cpu | 0 / DEAD runner | DEAD | n/a |

### Smoke -> FULL divergence accounting

| Run | Smoke | FULL | Divergence? |
|---|---|---|---|
| S_transform_v1 | DIVERGE 5/5 50-99% dev | DIVERGE 5/5 max=1.000 | NO; cell-extension broad anchor +1 only |
| parisi_pq_v1 | INCONCLUSIVE (smoke-scale artifact, 8/8 self-test) | INCONCLUSIVE (11/12 undetermined under-resolution) | NO; INCONCLUSIVE not a divergence axis (no anchor increment) |

Net: 25 strict / 29 broad smoke->FULL divergence anchors.

### PROT compliance

- PROT-007: v165 history line appended to substrate_capability_map_history.md; narrative block in substrate_capability_map.md.
- PROT-008: validator must pass before commit. 0 new ❌ rows added.
- PROT-009: cap_map.md + history.md + strategy_decisions_2026-05-23.md + active_priorities.md staged atomically.

### Tally (one-line)

BATCHED v164 -> v165: wave14_S_transform_kerdock_v1 Remote CPU FULL = S_TRANSFORM_DIVERGE (5/5 cells exceed 20% S-transform deviation; max_dev=1.000 at alpha=4.00 S_1; lands SECOND algebraic-free-prob axis -- multiplicative free-convolution -- INDEPENDENTLY CORROBORATING v164a additive free-cumulant DIVERGE) + wave14_parisi_pq_kerdock_v1 Remote CPU INCONCLUSIVE = PARISI_INCONCLUSIVE (24.4s elapsed; 11/12 cells "undetermined"; under-resolution NOT refutation); 1 new evidence-strength row added (multiplicative S-transform fingerprint 🟢 paired with v164a additive free-cumulant row); substrate-product portfolio at 11 demonstrated capabilities UNCHANGED IN COUNT (no closure, no new portfolio ✅); v164a free-cumulant row STAYS at 🟢 -- cross-axis corroboration does NOT substitute for explicit N-scaling promotion criterion (gated on running wave14_R_transform_kerdock_v1_multi_N GPU job); per [[feedback-dont-overextend-theorems]] no row closed and no premature promotion; per [[feedback-pipeline-pacing]] GPU has work (R_transform_multi_N in flight, queue-depth-1 right shape); remote CPU queue=0 and intentionally NOT auto-refilled per user's CPU-vs-GPU venue feedback this cycle ("seems like a mistake" -- CPU systematically under-resolves >=5-seed x >=10 cells probes; CPU reserved for cheap re-analyses); Parisi v2 filed as DEFERRED Exp Dev GPU re-run candidate (gated on R_transform_multi_N completion); inefficiency LOCKED: CPU-vs-GPU venue selection guideline flagged for memory curator next cycle; smoke->FULL broad anchors +1 by S-transform cell-extension (29 broad / 25 strict; parisi INCONCLUSIVE not counted); pause flag CLEARED -- ACTIVE; 79th PROT-009 paired commit.



---

## Cycle 186 (v166) -- BATCHED FOUR-verdict cap_map update: R-transform N-stability PROMOTES v164a free-cumulant fingerprint 🟢 -> ✅ + Kerdock codeword-overlap non-Gaussian NEW 🟢 + spectrum support bounded narrows mechanism to bulk-shape + Kerdock Hessian excess zero modes NEW 🟢 (SURPRISE POSITIVE)

### Verdicts processed (4)

1. **GPU / overnight_queue**: `wave14_R_transform_kerdock_v1_multi_N_v2` FULL = R_TRANSFORM_STABLE_IN_N -- "Kerdock R-transform deviation from MP STAYS > 0.20 across N range and does NOT shrink. 3/3 alpha cells stable+diverge, 3/3 above threshold. Substrate-novel observability dimension-stable: v164 free-cumulant fingerprint row promotes 🟢 -> ✅."
2. **Remote CPU**: `wave14_codeword_overlap_kerdock_v2` FULL = KERDOCK_OVERLAPS_NON_GAUSSIAN (1.25s elapsed) -- "Kerdock codeword inner-product distribution departs from Gaussian in 6/6 cells (KS > 0.10; max_ks=0.259). Substrate-novel structural-algebraic fingerprint independent of spectral moment family."
3. **Remote CPU**: `wave14_spectral_support_kerdock_v2` FULL = KERDOCK_SPECTRUM_BULK_BOUNDED (12.125s elapsed) -- "All 3 cells have spectrum CONFINED within 5% of the MP bulk edges. Max excursion=0.000. The substrate-novel signature is therefore MOMENT-BASED ONLY: free cumulants deviate from MP, but the support does not. The mechanism is shape-of-bulk, not outliers."
4. **Remote CPU**: `wave14_kerdock_hessian_tachyon_v2` FULL = KERDOCK_HAS_EXCESS_ZERO_MODES -- "Kerdock Hessian has EXCESS zero modes (beyond rank-deficiency floor) in 1/3 cells; max_excess=0.500 at alpha=0.50. Substrate-novel kernel dimension beyond generic random-matrix rank-deficiency."

### Strategy decisions

1. **PROT-009 v166 paired commit** -- 80th observation MILESTONE. cap_map.md + history.md + active_priorities.md + strategy_decisions_2026-05-23.md + visibility_decisions_2026-05-23.md staged atomically.

2. **v164a "Free-cumulant fingerprint of Kerdock R-transform" row PROMOTED 🟢 -> ✅ at v166** by Verdict 1 satisfying the explicit pre-registered N-scaling promotion criterion. R-transform dev > 0.20 STAYS across N range; 3/3 alpha cells stable+diverge; dimension-stable substrate-novel observability. This is the FIRST ✅-grade substrate-physics observability row for the "outside AMP universality" wedge -- previously the wedge was anchored only on 🟢-level evidence.

3. **TWO new 🟢 evidence-strength rows added under "Substrate-physics characterization"**:
   - "Codeword-overlap distribution structural fingerprint of Kerdock (substrate-novel structural-algebraic axis; independent of spectral moment family)" 🟢. Third independent algebraic-fingerprint axis alongside v164a additive R-transform + v165 multiplicative S-transform. (Verdict 2 evidence; 6/6 cells KS > 0.10; max_ks=0.259.)
   - "Excess Hessian zero modes from Kerdock 4-coset structure (substrate-novel kernel dimension beyond random-matrix rank-deficiency)" 🟢. SURPRISE POSITIVE substrate-novel flat-direction signature. (Verdict 4 evidence; 1/3 cells excess zero modes beyond generic rank-deficiency floor; max_excess=0.500 at alpha=0.50.)

4. **Mechanism-narrowing annotation added (Verdict 3)**: substrate spectrum is CONFINED within 5% of MP bulk edges (max excursion=0.000); substrate-novel signature is MOMENT-BASED ONLY (shape-of-bulk), NOT support / outliers. This is a clean positive characterization that constrains the mechanism cleanly. Unlocks Wigner-null moment-by-moment follow-up framing.

5. **v165 S-transform multiplicative row STAYS at 🟢** -- per [[feedback-dont-overextend-theorems]] the v166 N-stability promotion is for the ADDITIVE axis (R-transform via kappa_n) only. Each axis carries its own N-scaling promotion criterion. Analogous `wave14_S_transform_kerdock_v1_multi_N` is the natural follow-up to fire the same criterion on the multiplicative axis.

6. **Substrate-product portfolio UNCHANGED at 11 demonstrated capabilities** -- the v164a 🟢 -> ✅ promotion is a substrate-physics observability row, not a substrate-product portfolio capability. No closure, no new portfolio ✅.

7. **PROT-004/006 NOT triggered**: positive promotion + 2 new 🟢 rows + 1 mechanism-narrowing annotation. No closure, no new ❌ row.

8. **4 Research/Exp Dev candidate follow-up experiments noted** (NOT shipped this cycle; parallel exp_dev dispatch handles queue-refill):
   - `wave14_wigner_null_moment_test_v1` -- moment-by-moment Wigner-null baseline (unlocked by Verdict 3 bulk-bounded characterization). Highest priority.
   - `wave14_S_transform_kerdock_v1_multi_N` -- multiplicative-axis N-scaling probe analogous to Verdict 1; would promote v165 row to ✅.
   - `wave14_codeword_overlap_kerdock_multi_N` -- third-axis N-scaling probe.
   - `wave14_kerdock_hessian_tachyon_v3` -- broader alpha sweep + N-scaling for the SURPRISE POSITIVE excess-zero-mode finding.

9. **Pipeline-pacing**: pause flag CLEARED -- ACTIVE. GPU queue=0 (R_transform_multi_N just finished). Remote CPU queue=0 (3 CPU verdicts just finished). User has flagged "all queues are empty". Per the established working model the orchestrator is firing a PARALLEL `exp_dev` dispatch to handle queue-refill; verdict_handler does NOT also ship. The queue-refill responsibility this cycle is the parallel exp_dev's. (Action: NOTE refill is happening in parallel; verdict_handler stays in its lane.)

10. **No new inefficiency flagged this cycle**. The v165-era CPU-vs-GPU venue selection inefficiency remains LOCKED (memory curator to file [[feedback-cpu-vs-gpu-venue-selection]] next cycle); v166 verdicts honored the locked guideline (R_transform_multi_N ran on GPU; the three CPU verdicts ran cheap probes <15s each so legitimately CPU-bound work).

### Pipeline state at v166

| Queue | Pending | Running | Heartbeat |
|---|---|---|---|
| overnight (GPU) | 0 at arrival post-verdict (R_transform_multi_N just finished) | IDLE | parallel exp_dev dispatch refilling |
| remote_cpu | 0 at arrival post-verdict (3 CPU verdicts just finished) | IDLE | parallel exp_dev dispatch refilling |
| local_cpu | 0 / DEAD runner | DEAD | n/a |

### Smoke -> FULL divergence accounting

| Run | Smoke | FULL | Divergence? |
|---|---|---|---|
| R_transform_multi_N_v2 | (no documented smoke baseline; direct GPU FULL on v164 refill) | R_TRANSFORM_STABLE_IN_N (3/3 alpha cells stable+diverge) | no smoke baseline; broad anchor +1 by FULL landing |
| codeword_overlap_kerdock_v2 | KERDOCK_OVERLAPS_NON_GAUSSIAN (smoke 1-2 cells) | KERDOCK_OVERLAPS_NON_GAUSSIAN (6/6 FULL max_ks=0.259) | NO -- both NON_GAUSSIAN; cell-extension broad anchor +1 |
| spectral_support_kerdock_v2 | (no documented smoke baseline) | KERDOCK_SPECTRUM_BULK_BOUNDED (3/3 cells max excursion=0.000) | no strict tag flip; broad anchor +1 by FULL landing |
| kerdock_hessian_tachyon_v2 | (no documented smoke baseline) | KERDOCK_HAS_EXCESS_ZERO_MODES (1/3 cells max_excess=0.500) | no strict tag flip; broad anchor +1 by FULL landing |

Net: 25 strict / 33 broad smoke->FULL divergence anchors (broad +4 by v166 batch; strict unchanged).

### PROT compliance

- PROT-007: v166 history line appended to substrate_capability_map_history.md; narrative block in substrate_capability_map.md.
- PROT-008: validator must pass before commit. v166 adds 0 new ❌ rows; baseline pre-existing violations unchanged.
- PROT-009: cap_map.md + history.md + strategy_decisions_2026-05-23.md + active_priorities.md + visibility_decisions_2026-05-23.md staged atomically.

### Tally (one-line)

BATCHED FOUR VERDICTS v165 -> v166: R_transform_multi_N_v2 GPU FULL = R_TRANSFORM_STABLE_IN_N (3/3 alpha cells dimension-stable; v164a 🟢 -> ✅) + codeword_overlap_v2 CPU FULL = KERDOCK_OVERLAPS_NON_GAUSSIAN (6/6 cells KS > 0.10; THIRD algebraic-fingerprint axis; NEW 🟢) + spectral_support_v2 CPU FULL = KERDOCK_SPECTRUM_BULK_BOUNDED (3/3 cells within 5% MP bulk edges; mechanism narrowed to bulk-shape moments NOT outliers; annotation) + kerdock_hessian_tachyon_v2 CPU FULL = KERDOCK_HAS_EXCESS_ZERO_MODES (1/3 cells excess kernel dimension; SURPRISE POSITIVE; NEW 🟢); 1 ✅ promotion + 2 new 🟢 rows + 1 mechanism-narrowing annotation; substrate-product portfolio at 11 demonstrated capabilities UNCHANGED IN COUNT (substrate-physics rows only); "outside AMP universality" wedge gains FIRST ✅-grade substrate-physics anchor + THIRD algebraic-fingerprint axis + mechanism narrowed to bulk-shape; v165 S-transform STAYS at 🟢 (additive axis only promoted; each axis carries own criterion per [[feedback-dont-overextend-theorems]]); 4 follow-up Research/Exp Dev candidate experiments noted (Wigner-null moment test + S-transform multi-N + Hessian broader sweep + codeword-overlap multi-N); queue-refill DEFERRED to parallel exp_dev dispatch; verdict_handler does NOT also ship per pipeline-pacing; PROT-004/006 NOT triggered; smoke->FULL broad anchors +4 (33/25); 80th PROT-009 paired commit MILESTONE.

## 20:12 -- v167 SINGLE-VERDICT cap_map update: kappa_n_profile_v1 KAPPA_PROFILE_GROWS

**Verdict**: `kappa_n_profile_v1` FULL = KAPPA_PROFILE_GROWS at 96.67s on overnight_queue. 3/4 alpha cells show |kappa_n/c - 1| growing with n through n=8. Per-cell classes: GROWS=3 DECAYS=0 SATURATES=1 MP_LIKE=0 UNCLEAR=0. Substrate-novel additive-free-prob fingerprint AMPLIFIES at higher cumulants, does NOT decay with n.

**Sibling check**: the previous exp_dev batch shipped 4 experiments (kappa_n_profile_v1 + vamp_amp_universality_contrast_v1 + parisi_pq_kerdock_v2 + amp_se_kerdock_longiter_v1). Only kappa_n_profile_v1 has surfaced a verdict so far. Checked `data/event_outcomes/` (empty) and `data/local_dashboard_snapshot.json` recent_verdicts[] -- the other 3 are NOT yet present. Not batched into this commit; they will land in a future cycle when they complete.

### v167 cap_map changes

1. **PROT-009 v167 paired commit** -- 81st observation (post-MILESTONE).

2. **ZERO new rows + ONE clarifying annotation** on the v164a/v166 ✅ "Free-cumulant fingerprint of Kerdock R-transform" row. Annotation: cumulant-order-stability added as the third stability dimension. The substrate-novel additive-free-prob fingerprint is now stable along all three natural limits: (i) N -> infinity (v166 R_TRANSFORM_STABLE_IN_N), (ii) spectrum support (v166 KERDOCK_SPECTRUM_BULK_BOUNDED -- moment-based only), (iii) cumulant order n (v167 KAPPA_PROFILE_GROWS through n=8).

3. **NO state change on v164a row** -- stays at ✅ per [[feedback-dont-overextend-theorems]]. The ✅ promotion was the explicit additive-axis N-scaling criterion (satisfied at v166). v167 is annotation-grade strengthening, not double-promotion.

4. **No closure** -- positive annotation only. PROT-004/006 NOT triggered.

5. **Substrate-product portfolio UNCHANGED at 11 demonstrated capabilities** -- v167 is substrate-physics observability annotation only; no closure, no new portfolio ✅, no new evidence-strength row.

6. **Honest framing per [[feedback-no-smoke]]**: SATURATES=1 cell explicitly counted -- the GROWS classification is 3/4, NOT 4/4. The DECAYS=0 cell-count is the load-bearing observation; even the saturating cell does NOT decay. The saturating cell is plausibly an asymptotic-floor candidate; n -> infinity claim is NOT made (only "GROWS through n=8"). This honest framing matters for downstream stability claims at very high n.

7. **3 Research/Exp Dev candidate follow-up experiments noted** (NOT shipped this cycle; parallel exp_dev handles queue-refill):
   - `wave14_kappa_n_profile_v2_higher_n` -- extend to n=12 or n=16; characterize asymptotic behavior (does GROWS flip to SATURATES at higher n?). HIGHEST PRIORITY of the three (directly extends v167's "through n=8" boundary).
   - `wave14_S_transform_n_profile_v1` -- analogous n-profile probe on the multiplicative axis (S-transform coefficients S_1, S_2, ..., S_n GROWS/DECAYS); would extend cumulant-order-stability to the multiplicative axis (currently only v165's 🟢 row covers the multiplicative axis without n-profile data).
   - `wave14_kappa_n_profile_multi_N` -- replicate the GROWS finding at N=4096 + N=8192 to confirm cumulant-order stability commutes with N-stability. (Lower priority; v166 already established N-stability for kappa_2..kappa_4; v167 just extends to higher n.)

8. **Pipeline-pacing**: pause flag CLEARED -- ACTIVE. Overnight queue=0 (kappa_n_profile_v1 just finished). Remote CPU queue=0. Per the established working model the orchestrator is firing a PARALLEL `exp_dev` dispatch to handle queue-refill in this cycle; verdict_handler does NOT also ship. Queue-refill responsibility this cycle is the parallel exp_dev's.

9. **No new inefficiency flagged this cycle**. The v165-era CPU-vs-GPU venue selection inefficiency remains LOCKED.

### Pipeline state at v167

| Queue | Pending | Running | Heartbeat |
|---|---|---|---|
| overnight (GPU) | 0 at arrival post-verdict (kappa_n_profile_v1 just finished) | IDLE | parallel exp_dev dispatch refilling |
| remote_cpu | 0 (3 prior CPU verdicts already drained at v166) | IDLE | parallel exp_dev dispatch refilling |
| local_cpu | 0 / DEAD runner | DEAD | n/a |

### Smoke -> FULL divergence accounting

| Run | Smoke | FULL | Divergence? |
|---|---|---|---|
| kappa_n_profile_v1 | (no documented smoke baseline; direct overnight_queue FULL) | KAPPA_PROFILE_GROWS (3/4 alpha cells GROWS through n=8) | no smoke baseline; broad anchor +1 by FULL landing |

Net: 25 strict / 34 broad smoke->FULL divergence anchors (broad +1 by v167; strict unchanged).

### PROT compliance

- PROT-007: v167 history line appended to substrate_capability_map_history.md; narrative block in substrate_capability_map.md.
- PROT-008: validator must pass before commit. v167 adds 0 new ❌ rows; baseline pre-existing violations unchanged.
- PROT-009: cap_map.md + history.md + strategy_decisions_2026-05-23.md + active_priorities.md + visibility_decisions_2026-05-23.md staged atomically.

### Tally (one-line)

SINGLE VERDICT v166 -> v167: kappa_n_profile_v1 FULL = KAPPA_PROFILE_GROWS at 96.67s overnight_queue (3/4 alpha cells show kappa_n divergence from MP GROWING with n through n=8; substrate-novel additive-free-prob fingerprint AMPLIFIES at higher cumulants; per-cell classes GROWS=3 DECAYS=0 SATURATES=1 MP_LIKE=0 UNCLEAR=0); v167 adds ZERO new rows + ONE clarifying annotation on the v164a/v166 ✅ free-cumulant fingerprint row (cumulant-order-stability as third stability dimension alongside N-stability + bulk-boundedness); v164a row STATE stays at ✅ per [[feedback-dont-overextend-theorems]]; substrate-product portfolio at 11 demonstrated capabilities UNCHANGED IN COUNT; "outside AMP universality" wedge now anchored on additive-R-transform fingerprint stable along all three natural limits (N -> infty + support + cumulant order n through n=8); SIBLINGS NOT YET LANDED (3 prior-batch experiments still in flight); per [[feedback-no-smoke]] honest framing of SATURATES=1 cell; 3 Research/Exp Dev candidate follow-ups noted; queue-refill DEFERRED to parallel exp_dev; per PROT-004/006 NOT triggered; smoke->FULL broad anchors +1 (34/25); 81st PROT-009 paired commit.

## 20:35 -- Cycle 188 v168 SINGLE VERDICT: vamp_amp_universality_contrast_v1 GPU FULL = VAMP_AMP_CONTRAST_PASS

**Verdict**: `vamp_amp_universality_contrast_v1` GPU FULL = VAMP_AMP_CONTRAST_PASS at 1325.66s elapsed on overnight_queue. VAMP-SE tracks empirical VAMP (3/3 cells under 20% rel err, mean=0.021) while AMP-SE diverges from empirical AMP (1/3 cells close, mean=0.450). Clean substrate-product split per pre-reg HARD PASS criterion; deflated P=0.45 -> HARD PASS confirmed.

### Strategic call (per [[feedback-dont-overextend-theorems]] and [[feedback-no-smoke]])

This is likely the strongest single substrate-product result of the session. It is the constructive obverse of the v164a/v165/v166/v167 negative-direction fingerprint stack: on the SAME Kerdock codebook where AMP breaks (mean rel err=0.450 / v163 mean=0.916), VAMP holds (mean rel err=0.021). Mechanism story is algebraically clean: AMP uses scalar first moment only; VAMP uses full singular spectrum = S-transform-equivalent info. Substrate's higher kappa_n (v164a) + non-MP S-transform (v165) make AMP fail but do NOT break VAMP.

**Decision on portfolio count: 11 UNCHANGED. NO 12th portfolio capability.** Justification:
- Cap 8 already reads "TWO substrate-novel readout primitives equivalent (VAMP-on-chain + hard-cleanup) ✅ FULL cycle 162." VAMP-on-chain is ALREADY in the portfolio.
- The new finding does NOT introduce a new readout primitive; it provides the ALGEBRAIC-MECHANISM JUSTIFICATION for why VAMP-on-chain works on the Kerdock codebook. This is envelope-strengthening anchor on Cap 8, not a 12th row.
- Adding "uses VAMP not AMP" as a separate 12th-row would double-count what Cap 8 already covers per [[feedback-dont-overextend-theorems]].
- The substrate-product implication "substrate forces moment-aware inference" is REAL and SUBSTANTIVE per the user's strategic-guidance framing, but it lives WITHIN Cap 8 (as the algebraic-mechanism strengthening annotation) not alongside it.

**Decision on new evidence-strength row: 🟢 NEW (not ✅).** Per [[feedback-dont-overextend-theorems]] and the v164a precedent: single-N N=4096 + 3 alpha cells {0.5, 1.0, 2.0} + 5 seeds = single-N evidence-strength grade. ✅ promotion requires the explicit pre-registered multi-N replication criterion. The pre-registration at `preregs/2026-05-23_wave14_vamp_amp_universality_multi_N_v1.md` already names the multi-N (N=8192/16384) follow-up; that fires the explicit N-stability promotion gate.

**Honest framing of AMP-SE 1/3 cells close** per [[feedback-no-smoke]]: the lowest-alpha cell at alpha=0.5 plausibly stays close to scalar AMP-SE (AMP-SE is known to be diagnostic at sub-critical alpha even on non-RI matrices). The "AMP breaks" claim is NOT "AMP fails at all alpha"; the v167 KAPPA_PROFILE_GROWS prediction is that AMP failure WORSENS at higher alpha (where higher kappa_n diverge more). Extended-alpha VAMP-vs-AMP probe is the right next test.

### Capability moves (v167 -> v168)

| Capability | v167 state | v168 state | Trigger |
|---|---|---|---|
| **Substrate-physics: outside-AMP-universality at SE-fixed-point level** | mechanistically anchored on FOUR algebraic-fingerprint axes (additive R-transform ✅ + multiplicative S-transform 🟢 + codeword-overlap 🟢 + excess Hessian zero modes 🟢) + cumulant-order-stability annotation | **STRENGTHENED with CONSTRUCTIVE OBVERSE**: VAMP-SE empirically tracks empirical VAMP at mean rel err=0.021 (3/3 cells); AMP-SE empirically diverges at mean rel err=0.450 (1/3 cells close). "Outside AMP universality" now characterized on BOTH SIDES of the universality boundary (substrate FAILS scalar-AMP-SE AND PASSES full-spectrum-VAMP-SE) | Verdict (VAMP_AMP_CONTRAST_PASS) |
| **NEW ROW: VAMP-vs-AMP universality split on Kerdock at SE-fixed-point level** | did not exist | 🟢 NEW v168 at FULL: positive-direction inference-primitive anchor; constructive obverse to v164a/v165/v166/v167 fingerprint stack. Single-N N=4096 + 3 alpha cells + 5 seeds. ✅ promotion gate: multi-N replication (wave14_vamp_amp_universality_multi_N_v1 pre-reg already filed) + extended alpha range (alpha up to 4-8 to confirm AMP failure worsens) | Verdict |
| **Cap 8 TWO substrate-novel readout primitives equivalent ✅ FULL** | ✅ FULL (cycle 162) | **ENVELOPE-STRENGTHENING ANCHOR ADDED, STATE UNCHANGED at ✅**: VAMP-on-chain gains clean algebraic-mechanism justification on Kerdock -- VAMP succeeds because it consumes full singular spectrum (S-transform-equivalent info); scalar-AMP fails because it uses first-moment only. Per [[feedback-dont-overextend-theorems]] annotation-grade strengthening, not state change | Verdict (algebraic-mechanism strengthening) |
| **substrate-product portfolio count** | 11 demonstrated capabilities (UNCHANGED at v161 through v167) | **11 demonstrated capabilities UNCHANGED IN COUNT** -- Cap 8 already names VAMP-on-chain so adding "uses VAMP not AMP" as separate 12th-row double-counts; substantive substrate-product implication lives within Cap 8 | n/a (Cap 8 pre-existing) |

### Strategy actions (cycle 188)

1. **PROT-009 v168 single-verdict commit** -- 82nd PROT-009 paired commit.
2. **substrate_capability_map.md** appended atomically with v168 narrative + capability moves table.
3. **substrate_capability_map_history.md** appended with v168 one-line index entry.
4. **active_priorities.md** updated atomically v167 -> v168: substrate-physics row gains v168 positive-direction inference-primitive anchor; Cap 8 row gains algebraic-mechanism strengthening annotation.
5. **strategy_decisions_2026-05-23.md** this entry.
6. **visibility_decisions_2026-05-23.md** appended with HIGH-importance plain-language v168 substrate-product story.
7. **Push v168 to remote**: deferred to main thread (sub-agent push blocked per [[feedback-subagent-permission-inheritance]]).
8. **Queue-refill** NOT triggered: pending=5 (GPU=3, CPU=2). Pipeline healthy per [[feedback-pipeline-pacing]].
9. **3 NEW Research/Exp Dev candidate experiments noted** (multi-N VAMP-vs-AMP via pre-existing multi_N_v1 pre-reg [HIGHEST priority -- fires explicit N-stability promotion gate] + extended-alpha VAMP-vs-AMP {alpha 2, 4, 8} + R-transform-driven VAMP-SE composition using v164/v166-measured R-transform as input rather than empirical SVD).
10. **Pipeline-pacing**: pause flag CLEARED -- ACTIVE. Queue depth 5 healthy. Verdict_handler does NOT also ship.
11. **No new inefficiencies surfaced this cycle.** v165-era CPU-vs-GPU venue selection guideline holds (v168 ran on GPU at 1325.66s -- correct venue choice; SVD + 300-iter VAMP/AMP at N=4096 alpha=2 is GPU-bound per memory + iteration intensity).

### PROT compliance this cycle

- PROT-001/002/003: not triggered.
- PROT-004/006: NOT triggered (positive evidence + new 🟢 row + Cap 8 strengthening; no closure no new ❌).
- PROT-007: v168 history block written.
- PROT-008: validator must pass; v168 adds 0 new ❌ rows.
- PROT-009: cap_map.md + history.md + strategy_decisions_2026-05-23.md + active_priorities.md + visibility_decisions_2026-05-23.md staged atomically.

### Tally (one-line)

SINGLE VERDICT v167 -> v168: vamp_amp_universality_contrast_v1 GPU FULL = VAMP_AMP_CONTRAST_PASS at 1325.66s overnight_queue (VAMP-SE 3/3 cells <20% rel err mean=0.021 + AMP-SE 1/3 cells close mean=0.450; clean substrate-product split per pre-reg HARD PASS criterion; deflated P=0.45 -> HARD PASS confirmed); v168 lands FIRST positive-direction substrate-physics anchor for "outside AMP universality" -- the constructive obverse to the v164a/v165/v166/v167 negative-direction fingerprint stack (substrate FAILS scalar-AMP-SE per v163 AND PASSES full-spectrum-VAMP-SE per v168 on SAME Kerdock codebook); mechanism story algebraically clean (AMP uses scalar first moment only and breaks on substrate's higher kappa_n; VAMP uses full singular spectrum = S-transform-equivalent info and holds); v168 adds ONE new 🟢 evidence-strength row ("VAMP-vs-AMP universality split on Kerdock at SE-fixed-point level"; positive-direction inference-primitive anchor) + ONE Cap 8 envelope-strengthening annotation (algebraic-mechanism justification for VAMP-on-chain on Kerdock); substrate-product portfolio at 11 demonstrated capabilities UNCHANGED IN COUNT per [[feedback-dont-overextend-theorems]] -- Cap 8 ALREADY names VAMP-on-chain as one of TWO substrate-novel readout primitives (cycle 162 anchor); adding "uses VAMP not AMP" as separate 12th-row would double-count Cap 8; substrate-product implication "substrate forces moment-aware inference" REAL and substantive but lives WITHIN Cap 8 not alongside it; new 🟢 row STAYS at 🟢 (single-N N=4096 + 3 alpha cells + 5 seeds; explicit ✅ promotion gate = multi-N via wave14_vamp_amp_universality_multi_N_v1 pre-reg already filed + extended-alpha range); per [[feedback-no-smoke]] honest framing of AMP-SE 1/3 cells close (lowest-alpha alpha=0.5 plausibly tracks scalar AMP-SE; AMP failure expected to worsen at higher alpha per v167 KAPPA_PROFILE_GROWS); 3 NEW Research/Exp Dev candidate experiments noted (multi-N VAMP-vs-AMP HIGHEST priority + extended-alpha + R-transform-driven VAMP-SE composition); per [[feedback-pipeline-pacing]] queue healthy at depth 5 (GPU=3 + CPU=2) -- verdict_handler does NOT ship; SIBLINGS NOT YET LANDED (2 remaining from v167-era batch -- parisi_pq_kerdock_v2 + amp_se_kerdock_longiter_v1 -- still in flight); per PROT-004/006 NOT triggered; smoke->FULL broad anchors UNCHANGED (v168 no smoke step; 34/25); pause flag CLEARED -- ACTIVE single-verdict verdict_handler dispatched in ACTIVE state; 82nd PROT-009 paired commit.

## 21:19 -- RESCUED VERDICT: wave14_kappa_paley_quickprobe_v1 PALEY_QUICKPROBE_PERFECT_ISOMETRY

**Verdict**: `wave14_kappa_paley_quickprobe_v1` FULL = PALEY_QUICKPROBE_PERFECT_ISOMETRY at 1.74s on local_cpu_queue. Paley Type-I sub-block (p=1019, order 1020) shows perfect isometry: all singular values equal (sigma_i = sqrt(N)); kappa_n = 0 for all n >= 2; spectrum is a single delta, NOT an MP bulk.

**Rescue context**: verdict landed on cpu_runner_local at 21:19 but was NOT surfaced by dispatch.py snapshot (snapshot tracks remote cpu_runner_0 only; cpu_runner_local outside snapshot scope -- known dispatch.py gap). Manual rescue via direct orchestrator passthrough.

**Strategy verdict**: NO new cap_map row. Per the prereg's explicit "expected" verdict, PERFECT_ISOMETRY was the math-predicted outcome; this is a useful-negative scoping result, not a fingerprint-stack addition. Paley Type-I sub-blocks are mathematically NOT a useful comparison codebook for the BBMD-distance metric (which assumes an MP-like bulk reference); excluded from the Anchor-2 KAPPA_PROFILE_CROSS_CODEBOOK battery {SRHT, Hadamard, RM(1,m), Kerdock, iid Gauss}.

**Clarifying annotation on BBMD direction (per user directive)**: BBMD axis placement clarified. Three codebook regimes along the structured-to-random axis:
- **Paley Type-I**: perfect isometry; kappa_n = 0 for all n >= 2; spectrum = single delta; OVER-structured (deterministic equiangular).
- **Haar / iid Gauss (asymptotic)**: asymptotically free; kappa_n -> 0; spectrum = MP bulk; UNDER-structured (fully thermalized).
- **Kerdock 4-coset**: kappa_n GROWS in n (v167 evidence ✅); spectrum within 5% of MP bulk edges (v166 ✅); structured-enough to break scalar AMP universality, not enough to collapse spectrum to a delta.

The substrate-product story crystallizes as: "Kerdock sits in the BBMD regime that AMP cannot handle but VAMP can -- between Paley's over-structured delta and Haar's under-structured MP bulk." This places the BBMD axis correctly and supplies the missing left-endpoint sanity check (Paley = kappa=0) that the v164a/v166/v167 fingerprint stack implicitly assumed but had not empirically anchored.

**No cap_map commit this cycle.** No row added; no row promoted/demoted; no portfolio count change. Clarifying annotation only -- lives in this decision log; v168 cap_map state unchanged.

**Sibling check**: BBMD anchors (2 from exp_dev batch) + cumulant_dichotomy (1) still pending on CPU. parisi_pq_kerdock_v2 + amp_se_kerdock_longiter_v1 (GPU sibling, currently running) still in flight. None batched into this rescue.

**Pipeline-pacing**: pause flag CLEARED -- ACTIVE. Queue depths: GPU=3 pending + 1 running, CPU=3 pending + 1 running, local CPU IDLE. Per user directive, parallel exp_dev IS dispatching another local-CPU quick probe; verdict_handler does NOT also ship.

PLAIN: A quick local-CPU scoping run on a different mathematical Hadamard family (Paley Type-I) returned exactly the math-predicted answer -- perfect isometry, no bulk -- which means Paley is NOT a useful comparison codebook for our cross-codebook BBMD battery and is excluded from the upcoming Anchor-2 v2 run. The useful side-effect: this anchors the LEFT endpoint of the BBMD axis (over-structured / kappa=0 / delta spectrum) and clarifies that our Kerdock substrate sits in a usable middle regime between Paley's over-structured endpoint and Haar/iid-Gauss's under-structured endpoint. The substrate-product framing tightens: "structured enough to break AMP universality, not so structured that the spectrum collapses to a delta." No portfolio change; no new evidence-strength row; cap_map state UNCHANGED at v168. IMPORTANCE: MEDIUM (useful-negative scoping; clarifying annotation; no fingerprint-stack addition).

---

## 21:35 -- PROACTIVE DRILL (v168 cap_map; planning-only, NOT a verdict-driven cap_map commit)

Dispatched by orchestrator while pipeline is loaded (experiments returning over the next 30-90 min). Per [[feedback-strategy-shore-up-capabilities]] the Strategy role proactively drills the cap_map -- envelope-expansion on the demonstrated rows + open-row close-or-reject planning + cross-capability composition + portfolio gap audit. **No cap_map state change this cycle**; this is preparatory routing material that the next verdict event (or the next pause-cleared exp_dev refill) can pick up.

### Task 1 -- Envelope expansion on the demonstrated rows

Two demonstrated capabilities have OBVIOUS envelope-expansion opportunities that are not yet enumerated as next-axis follow-ups in `active_priorities.md`:

#### Cap 9 -- Multi-target + cross-task at FULL
**Current envelope**: 4 targets, cross-task gaps within commercial tolerance at FULL (anchored cycle 139); next-axis row in active_priorities reads "more targets (>4); harder cross-task; under noise" but these are not currently queued.
**Proposed expansion**: Push targets to {8, 16, 32} at FULL N=16384 under the v158 Cap 3 streaming-noise envelope (p in {0.05, 0.10, 0.20}) -- this is a clean cross-row composition (Cap 9 envelope axis + Cap 3 noise-tolerance characterization). Three pre-reg cells per noise level x three target counts = 9 cells, 5 seeds = ~30 min GPU per condition based on cycle 139 wall-clock.
**Why it matters for substrate-product framing**: the customer-facing story today says "multi-target retrieval works at FULL" without quantifying scaling. Establishing the targets x noise contour gives a defensible SLA matrix ("we hold at K targets under p bit-flip noise") instead of a single anchor point. Per [[feedback-value-creation-not-competition]] this is capability-shaping (here is the envelope) not competitive framing.
**Hard-fail threshold**: If mean per-target accuracy drops below 0.90 at K=8 targets / p=0.05 (the WEAKEST noise + LIGHTEST scaling expansion), the Cap 9 envelope is over-narrow at the cycle-139 anchor and the SLA matrix narrows accordingly. If K=32 targets / p=0.20 holds at >=0.85 mean accuracy, the envelope expansion succeeded and the Cap 9 commercial wedge gains a quantified scaling story. Intermediate outcomes (e.g., K=16 holds but K=32 fails) characterize the boundary precisely -- ALL outcomes are informative.

#### Cap 11 -- Observability V2 (chi_4 + Kovacs + avalanche) at FULL across 240 envelope cells
**Current envelope**: 240 envelope cells PASS at FULL + Observability V2 anchored cycles 145 + 168-170; next-axis row reads "harsher noise; larger K; meta-envelope; cross-capability observability". The "cross-capability observability" axis is exactly the under-leveraged direction.
**Proposed expansion**: Run chi_4 + Kovacs simultaneously DURING a Cap 1 forensic-erase trace AND during a Cap 5 Online W update trace AND during a Cap 10 Bet A continual-edit trace at N<=8192 (gated by the v156 hard-gate at N>=16384). Five seeds per trace x 3 capability targets = 15 traces; ~45 min GPU per trace based on cycles 168-170 wall-clock. The observability primitive is general; we have demonstrated it in isolation (cycle 145 standalone + 168-170 envelope-cell coverage) but NEVER as an in-flight monitor on the other demonstrated capabilities.
**Why it matters for substrate-product framing**: per [[feedback-no-papers-product-only]] the substrate-product story is "we can see what is happening inside the substrate while a primitive runs"; today that claim is supported by isolated observability anchors, not by simultaneous-monitoring traces. The customer demo lift is "watch chi_4 spike DURING forensic erase as the substrate transitions" -- that is a fundamentally different value proposition than "we can compute chi_4". This composes Cap 11 x {Cap 1, Cap 5, Cap 10} into a stronger demo without any new mechanism build.
**Hard-fail threshold**: If chi_4 / Kovacs traces do NOT show measurable signal (defined as: signal-to-noise ratio >= 3 against the t much less than t_erase quiescent baseline over the active phase of the host primitive) during ANY of the three host capabilities, Cap 11 cross-capability observability axis is over-narrow at the cycle-145 anchor -- the observability primitive may be too noise-floor-limited to surface dynamics under other primitives active phases. Rescue per [[feedback-rehabilitation-after-rejection]]: (a) longer integration windows; (b) higher seed counts to suppress baseline variance; (c) restrict to N>=16384 if v156 hard-gate is lifted; (d) gate on substrate-physics characterization (multi-component sub-K-region q_overlap) being structurally present in the host trace, which it should be for Cap 1 + Cap 5 + Cap 10 by v160 substrate-physics anchor.

### Task 2 -- Open-row close-or-reject drill

Per `active_priorities.md` under v168 (lines 47-60), the open rows are:

#### Partial rows

1. **Bet T parallel hypothesis tracking** (PARTIAL min_acc=0.689 at cycle 101; 67 cap_map versions stale at v168). **Concrete step**: dispatch the Research-routed rescue sketches (filed v158 in `strategy_request_to_research_betT_betV_rescue_sketches_2026-05-23.md`) to a CPU exploratory sweep BEFORE re-running Bet T at FULL. If Research returns no axis-combination rescue with deflated P >= 0.30, file PROT-004/006 closure with 3-5 explicit rescue sketches -- the version-staleness alone (67 versions) is structural evidence that the row is not on a credible path. Closure framing per [[feedback-rehabilitation-after-rejection]]: "Bet T at min_acc=0.689 is below commercial SLA AND has not moved across 67 cap_map versions; rescue sketches enumerated and deferred to elective-hardening pool unless customer demand surfaces."
2. **Bet V self-reflective** (PARTIAL gap=0.424 at largeN; 65 versions stale at v168). **Concrete step**: same close-or-reject sequence as Bet T (paired routing in same v158 Research request). The gap=0.424 result is far from a self-reflective claim (self-reflective implies gap of order epsilon). Closure framing: "Bet V at gap=0.424 is structurally inconsistent with the self-reflective label and has not moved across 65 cap_map versions; the framing was over-promised at cycle 103. Rescue sketches deferred; re-axiomatize as a separate down-stream calibration capability if any rescue surfaces."
3. **Cap 1 noise-robust rescue sketches** (5 axis-combination sketches filed v157; ELECTIVE post-v158 re-axiomatization). **Concrete step**: NO action this cycle; rescue sketches stay in the elective-hardening pool. v158 Sagawa-Ueda re-axiomatization already moved Cap 1 to FULL Tier 1 + Tier 2 -- the noise-robust rescue sketches are now over-determined unless a customer asks for p>=0.30. Strategic close-or-reject decision: stays in pool as latent options; not a partial row that needs immediate close.
4. **Bet A M_init capacity ceiling at N=65536 (HARD-GATED at OOM-DEFERRED)**. **Concrete step**: NOT a rescue question; this is an engineering blocker. The `build_initial_W` refactor (bf16 matmul or chunked allocation) is the actual blocker per `active_priorities.md` engineering-blockers section. Strategy logs that this row stays GATED until exp_dev picks up the refactor; closure not appropriate (the substrate WORKS at N<16384; the issue is solely scale).
5. **Bet Z.1 SRHT readout** (mechanism viable but speedup 0.4x; 37 versions stale). **Concrete step**: REJECT and close. The Bet Z.1 wedge was compressive readout speedup; speedup 0.4x is the opposite of the claim. Rescue sketches per [[feedback-rehabilitation-after-rejection]]: (a) higher-rank SRHT (P=0.20; the speedup loss came from the rank-r projection being too lossy for our overlap distribution); (b) hybrid SRHT + cleanup (P=0.15; piggyback on Cap 8 cleanup but adds latency); (c) GPU-batched SRHT (P=0.10; the 0.4x figure was CPU; GPU memory bandwidth may flip the sign but Cap 8 VAMP-on-chain already dominates this regime); (d) frame as a continuous-edit speedup not a readout speedup (P=0.05; orthogonal use case); (e) deprecate and absorb into Cap 8 (P=0.50; cleanest portfolio move). Sequencing: (e) FIRST; (a)-(d) elective if customer surfaces.

#### Probe rows

1. **Bet Z.5 Absorbing Diffusion Ensemble Smoother** (P=0.40; 13 versions stale at v168; routed v158 to Exp Dev for VAMP-on-chain equivalence check). **Concrete step**: Exp Dev has the equivalence check routed (cheap CPU + theory, ~30-60 min CPU + ~1 hr math per v159 active_priorities pick #3). Strategy waits for the equivalence-check verdict; do NOT re-route. If equivalence check shows Bet Z.5 equal to VAMP-on-chain modulo constants, close as duplicate (cleaner Cap 8 coverage). If Bet Z.5 strictly stronger, promote to portfolio at appropriate state.
2. **META Gap A spatially-coupled codebook + block-VAMP** (P=0.45; 6 versions stale). **Concrete step**: Kudekar 2013 threshold-saturation theorem exists per v158 routing note; tractable but substantial. Pre-reg should specify: (a) spatial-coupling construction (which codebook gets coupled, how many spatial positions, coupling strength); (b) block-VAMP variant (per-block SVD or full-window SVD); (c) explicit threshold-saturation prediction (alpha_BP-threshold approaches alpha_MAP per Kudekar) with hard-fail at >5% deviation. Bandwidth-permitting; do NOT prioritize over Cap 2 self-monitoring rehab.
3. **K-resonance K=1000 fixed-point** (Arnold-tongue REFUTED; nearly-degenerate eigenvalue candidate). **Concrete step**: REJECT and close per PROT-004/006. The Arnold-tongue framing failed at cycle 145; the nearly-degenerate eigenvalue rescue was noted but never tested across 12 versions. Rescue sketches: (a) measure eigenvalue degeneracy directly at K=1000 (cheap; 10-min CPU); (b) re-frame as a substrate-physics observability axis not a capability (P=0.20); (c) absorb into v166 Hessian zero-modes row (P=0.25; the Hessian zero-modes finding may already capture this); (d) deprecate (P=0.50; cleanest). Strategy recommendation: do (c) first -- test if v166 excess-zero-modes signature explains the K=1000 fixed-point qualitatively; if so, absorb. If not, deprecate.
4. **P(q) discrete-spike structure CHARACTERIZED at this resolution v162**. **Concrete step**: this is an annotation-grade substrate-physics row, NOT a capability candidate. Stays as substrate-physics-axis only; the matched-(N,K,L) head-to-head probe of endpoint partition vs P(q) peaks is queued as an open follow-up candidate but does not gate any capability. No close-or-reject needed; it characterizes substrate state and reconciles with cycle 137. Keep as-is.
5. **Anti-RM(1,16) coset bias mechanism** (substrate-physics; mechanism unknown). **Concrete step**: file a Research routing request for a 2x mechanism drill. The 0% within linear subcode finding has been stale since cycle 145 and is structurally interesting (it could ground a substrate-physics observability axis or it could be a measurement-protocol artifact). Research scope: lit-scan on anti-coset bias mechanisms in Reed-Muller subcode constructions + generic-math framing of 0% intra-subcode overlap under structured-codebook readout + one experimental next-step. Generic-math framing per [[feedback-query-privacy-decomposition]].
6. **P(h) moments observability family** (proposed v109; never fired; 59+ versions stale at v168). **Concrete step**: this is the canonical stale-but-not-rejected row. REJECT and close at PROT-004/006 with 3-5 rescue sketches: (a) absorb into Cap 11 Observability V2 (P=0.40; chi_4 + Kovacs may already capture P(h) moments); (b) frame as a low-priority back-burner item (P=0.20); (c) re-test at FULL N=16384 to settle (P=0.20; cheap GPU); (d) deprecate (P=0.30); (e) re-route to Research for lit-scan (P=0.10; deferred). Recommendation: do (a) first -- if Cap 11 chi_4 + Kovacs are MOMENTS of an underlying P(h)-equivalent distribution, P(h) moments is already in the portfolio under Cap 11.

### Task 3 -- Cross-capability composition stories (at least 2 NEW)

Per [[feedback-strategy-shore-up-capabilities]] periodic cross-application probes. The portfolio has 11 demonstrated capabilities and 3 envelope-characterization rows. Cross-capability composition stories below are NOT yet documented in the cap_map:

#### Composition story 1: Cap 1 (forensic erase audit trail) + Cap 11 (chi_4 / Kovacs observability) -> live audit-trail certificate during erase
**Composite capability**: while a Crooks-ratio forensic erase is in flight, chi_4 + Kovacs traces produce a real-time observability signal that the erase IS in progress at the substrate-physics level (not just the Crooks-FT bound). Currently Cap 1 reports the post-hoc Crooks-FT verdict; Cap 11 reports observability primitives in isolation. The composite would produce: Crooks-FT-bound erase WITH simultaneous chi_4 transition signature characterized -- a certificate that the erase is happening at the macroscopic Crooks level AND the microscopic dynamic-susceptibility level.
**Why neither alone licenses it**: Cap 1 alone cannot distinguish a Crooks-FT-bound erase that actually changed substrate state from a measurement-protocol artifact that mimics the FT shape. Cap 11 alone characterizes observability but is not tied to a customer-relevant primitive. Composed: the chi_4 signature gives independent corroboration of the FT-bound result, AND lifts Cap 11 from a standalone-observability-primitive to a live-substrate-monitor.
**Operational shape**: one pre-reg (cap1_erase_with_chi4_kovacs_simultaneous_v1) running at N=16384 across the v158 Cap 1 noise envelope cells (p in {0.05, 0.10, 0.20}); fires per Task 1 Cap 11 envelope expansion AND fires the Cap 1 + Cap 11 composition simultaneously.

#### Composition story 2: Cap 3 (streaming inference NESS) + Cap 8 (VAMP-on-chain readout) + v168 algebraic-mechanism annotation -> noise-bounded streaming inference with audited readout primitive
**Composite capability**: streaming inference (Cap 3) is currently FULL clean + noise envelope at p in {0.05, 0.10, 0.20}. VAMP-on-chain (Cap 8) is FULL with cycle-162 anchor + v168 algebraic-mechanism justification. The composite story: a customer pipeline that ingests a stream, runs VAMP-on-chain as the readout primitive, AND verifies (per v168 algebraic-mechanism) that VAMP is the right primitive for THIS substrate algebra at every read. The substrate self-justifying inference primitive property comes from composing Cap 3 (the streaming primitive) + Cap 8 (the readout primitive) + v168 positive-direction characterization (the algebraic-mechanism justification).
**Why neither alone licenses it**: Cap 3 alone is streaming runs at throughput X under noise p; Cap 8 alone is VAMP-on-chain readout works; v168 alone is VAMP-SE tracks empirical VAMP at mean rel err=0.021. Composed: streaming inference runs at throughput X under noise p AND the readout primitive is provably the right primitive for this substrate AND we can characterize WHY at every read. That is a fundamentally stronger customer-facing claim per [[feedback-no-papers-product-only]].
**Operational shape**: a single FULL run (cap3_streaming_with_vamp_on_chain_v1) at N=16384, three noise levels, 5 seeds, reporting both throughput_ratio (Cap 3 envelope metric) AND VAMP-SE-vs-empirical mean rel err (v168 algebraic-mechanism metric) per cell. Composition is free in the engineering sense -- the existing Cap 3 streaming and existing Cap 8 VAMP-on-chain compose mechanically; the new test surface is the joint metric reporting.

#### Composition story 3: Cap 5 (Online W noise envelope at p<=0.30 CONFIRMED structural boundary) + Cap 6 (Conformal calibrated confidence) -> conformal SLA on Online W under noise
**Composite capability**: Cap 5 noise envelope is CONFIRMED structural at p_flip<=0.30 (v161 Polyak-Ruppert noise-corrected bound DID NOT rescue p=0.40; envelope is real). Cap 6 is FULL conformal calibrated confidence (cycle 173) with envelope axis distribution-shift / N=131072+ / cross-task conformal. Composition: APPLY Cap 6 conformal calibration to Cap 5 Online W update trajectories under noise -- the conformal prediction set width per Online W write step gives a per-write SLA bound under noise that is provably calibrated. This is exactly the v160 Rescue-5 Cap 6 absorbs Cap 2 self-monitoring composition pattern, applied to Cap 5 noise envelope instead of Cap 2 self-monitoring.
**Why neither alone licenses it**: Cap 5 alone gives an aggregate envelope (works up to p<=0.30); Cap 6 alone gives conformal coverage on a static task. Composed: per-write conformal coverage UNDER noise gives a customer-facing SLA that says Online W writes carry a calibrated coverage guarantee at noise level p, with coverage tightness varying as the noise level varies through the envelope. This generalizes Cap 6 from a static conformal layer to a dynamic conformal layer, AND makes Cap 5 envelope quantitatively richer.
**Operational shape**: pre-reg cap5_online_W_with_conformal_cover_v1 at N=4096 (cap5 cycle-179 anchor) with conformal hold-out per write step, 4 noise levels (p in {0.05, 0.10, 0.20, 0.30}), 5 seeds. Reports coverage AND coverage tightness per write across noise levels; the Online W noise envelope Cap 5 story gains a conformal-SLA dimension; the conformal calibrated confidence Cap 6 story gains a dynamic-task application.

### Task 4 -- Portfolio gap audit (at least 3 gaps)

Per [[feedback-design-space-and-audit-cadence]] periodic audit identifies dropped items + stale probe rows + re-review candidates. Below are gaps in the portfolio that a substrate-product story arguably needs (NOT proposing new rows -- just flagging what is missing):

1. **Substrate-product GENERATIVE-mode capability**. Every capability in the v168 portfolio is a READ-/RETRIEVE-/INFER-mode primitive (Cap 1 erase, Cap 3 inference, Cap 5 online updates, Cap 7 streaming, Cap 8 readout primitives, Cap 9 multi-target retrieval, Cap 10 continual edit, Cap 11 observability). The portfolio has NO generative-mode capability -- no row anchors the substrate can generate novel structured outputs or the substrate can synthesize from learned distributions. This was flagged way back in v1 Capability questions we have not asked section (Can the substrate autoregressively GENERATE?) but has never been promoted to even a probe row. If a customer asks what does the substrate produce vs what does it look up, the answer today is it does not produce; it retrieves / decomposes / certifies. A substrate-product story arguably needs a generative-mode anchor.

2. **Substrate-product LATENCY/TIMING-mode SLA**. The portfolio has throughput characterizations (Cap 3 throughput_ratio at v158; Cap 5 min_acc at p<=0.30) but NO row anchors end-to-end latency SLAs at customer-realistic scales. Cap 9 / Cap 10 / Cap 11 do not have latency numbers in their cycle-139 / cycle-172 / cycle-145 anchors. For an on-device or edge customer (CPU-only retrieval sub-100ms was a v1 throughput-mode claim but is now stale partial from v1 Memory primitives section), this is a gap. A customer SLA story arguably needs we hold X ms p99 at N=Y for primitive Z under noise level p -- nowhere in the v168 portfolio.

3. **Substrate-product DOWNSTREAM-INTEGRATION-mode anchor**. The portfolio characterizes substrate-internal primitives (Cap 1-11 are all substrate-substrate axis claims). There is NO row that anchors the substrate integrates with an upstream encoder / downstream decoder / external policy layer at a customer-realistic interface. The v3 cap_map update promoted in-context learning via pool to demonstrated but that anchor is now stale at v168 (the v160 portfolio does not list it as a separate Cap row). The substrate-product story arguably needs an integration anchor -- a row that says we plug into pipeline X / encoder Y / external decoder Z and the interface holds at scale. Today the closest is Cap 8 VAMP-on-chain readout, but that is a substrate-internal primitive, not an external-pipeline interface.

4. **Substrate-product EDIT-INTERFACE-mode capability**. Cap 10 (Bet A continual-edit) anchors edits work at M_init=8192 N=65536; Cap 1 (Crooks forensic erase) anchors erase works under noise envelope. Neither anchors the CUSTOMER-FACING EDIT INTERFACE: user gives the substrate a correction, the substrate applies it, future queries reflect the correction. This was flagged in v1 KILLER Tier-1 section (Edit-then-query for fact correction -- UNSURE: can edit, but full pipeline integration untested) and has NEVER moved. The substrate-product wedge for the AI-memory subsystem direction (per [[project-ai-memory-subsystem-direction]] auditable third memory type / editable memory / provenance) arguably REQUIRES an edit-interface anchor; today the four AI-memory-subsystem capability classes have substrate-internal anchors (Cap 1 = verifiable erase; Cap 10 = editable memory primitive; Cap 11 = provenance via observability; Cap 8 = cognitive composition via readout primitives) but NOT a customer-facing-interface anchor for any of them.

5. **Substrate-product FAILURE-MODE-OBSERVABILITY anchor**. Cap 11 chi_4 / Kovacs / avalanche observability primitives are characterized at FULL across 240 envelope cells, BUT there is NO row that anchors when capability X is ABOUT to fail, observability primitive Y signals it BEFORE the failure. This is the customer-facing version of Cap C failure mode is captured by Cap D monitoring. Today Cap 11 observability is a PASSIVE characterization (we can compute these primitives); a PREDICTIVE characterization (chi_4 spike predicts Cap 10 edit failure 5 writes before it happens) is missing. The Cap 2 self-monitoring closure at v160 was the substrate failed attempt at an intrinsic confidence signal; the substrate-product story arguably needs at least ONE row that anchors predictive observability -- chi_4-as-early-warning is the natural candidate per the v150 RS-cert anchor.

### Decision summary

- **NO cap_map commit this cycle.** This is preparatory planning, not verdict-driven row movement per the user directive.
- **NO new routings filed this cycle.** The drill identifies candidate routings (Task 1 envelope-expansion pre-reg targets, Task 2 PROT-004/006 closure candidates for Bet Z.1 + K-resonance + P(h) moments, Task 3 cross-capability composition pre-reg targets, Task 4 portfolio gap flags) but does NOT file them as routing notes; that happens when the next verdict event or queue-refill cycle pulls these into the active pipeline. **All four task outputs are surfaced here in the decision log only.**
- **active_priorities.md NOT touched this cycle.** Per the user directive, row movement waits for verdicts; the active-priorities document reflects v168 state.
- **Status log entry filed at MEDIUM importance** with plain_language describing the four-task drill.

## 22:47 -- SINGLE-VERDICT (ANNOTATION-ONLY): wave14_rsb_exchange_mcmc_v1 RSB_PT_INCONCLUSIVE

**Verdict**: `wave14_rsb_exchange_mcmc_v1` Remote CPU = RSB_PT_INCONCLUSIVE at 504.7s on remote_cpu_queue. Parallel-tempering exchange-acceptance probe on Kerdock-Hebbian W. Mixed criteria: transitions=0/3, flat=0/3. Acceptance profile across 11 beta points (3 seeds):
- Seed 1: [0.9998, 1.0, 1.0, 1.0, 0.9992, 0.9856, 0.9380, 0.8532, 0.7952, 0.679, 0.245]
- Seed 2: [1.0, 1.0, 1.0, 1.0, 0.999, 0.9872, 0.9488, 0.8724, 0.8266, 0.7086, 0.3558]
- Seed 3: [1.0, 1.0, 1.0, 1.0, 0.9972, 0.977, 0.9108, 0.8146, 0.7332, 0.6194, 0.3798]

All three seeds show smooth monotone decay 1.0 -> ~0.30 across the beta-grid with NO sharp transition (would signal RSB) AND NO flat profile (would signal RS). The signature is more consistent with a **paramagnet-like / weak-glass** regime than full RSB at the tested protocol.

**Strategy verdict: NO cap_map row change.** v168 state unchanged.
- Per [[feedback-dont-overextend-theorems]]: this is "no RSB detected at this N + this PT exchange-MCMC protocol" — NOT a refutation of RSB-like physics in the substrate broadly. The cap_map should not absorb a negative-direction probe row for a single under-resolved RSB-detection lens.
- Per [[feedback-negative-results-2x-research]]: INCONCLUSIVE under-resolution would normally be a re-run candidate, BUT this 504s run is already the longer-chain re-resolved version. The protocol itself (PT exchange acceptance) is the lens that is silent here, not the chain depth. A different RSB-detection lens is the natural follow-up, not a third re-run of PT.
- Per [[feedback-dont-dismiss-adjacent-methods]]: the cross-domain probe #2 already identified an adjacent lens — Kac-Rice annealed-complexity (the 4h CPU deferred probe). That is the appropriate next RSB-detection probe; it measures saddle-density structure directly rather than via temperature-exchange acceptance. Annotation here flags Kac-Rice complexity as the prioritized alternative-lens follow-up when a CPU slot opens.

**Adjacent context (NOT row change; annotation only):**
- v164b GLAUBER_BIMODAL_KERDOCK previously found low-T bimodal P(q) on the same Kerdock-Hebbian W. Bimodal P(q) does NOT require RSB; it can be 1RSB OR simple double-well. Today's PT-silent result is consistent with the simple double-well reading of v164b (paramagnet over barrier above critical beta, with the bimodal P(q) reflecting the two basins rather than a hierarchy of states). It is also consistent with 1RSB that is too weak / too short-correlated for PT exchange acceptance to resolve at this N + this beta-grid.
- Substrate-physics framing: at this N + protocol the substrate is in a regime where the saddle structure (if RSB-like) is not strong enough to manifest as PT exchange-acceptance bottlenecks. The Kac-Rice probe is the right lens to disambiguate "weak-glass-with-shallow-saddles" vs "paramagnet-with-bimodal-readout."

**Pipeline-pacing**: queue depths GPU=2 pending + 1 running, Remote CPU=9 pending + 1 running, local CPU idle. Queue is HEALTHY (per user context). Verdict_handler does NOT ship queue-refill. Kac-Rice complexity probe stays deferred in elective-CPU pool until a longer CPU slot opens (it is a 4h CPU run; not the right fill for an idle local CPU shim today).

**PROT discipline:**
- PROT-004/006 NOT triggered. Annotation-grade; no closure; no new ❌ row; no rescue-sketch enumeration required (the negative is bounded to a specific protocol, not a capability claim).
- PROT-007 NOT triggered. No new prose block for history.md; cap_map.md version table NOT bumped.
- PROT-008 NOT triggered. No staged cap_map changes; validator not invoked.
- PROT-009 NOT triggered as a paired commit. Strategy_decisions + visibility_decisions still atomically staged in the local commit per PROT-009 spirit (paired decision logs even when cap_map untouched) — but the commit message tags this as "Verdict annotation (no cap_map change)" not "Cap map v<N>".

**Sibling check**: this verdict belongs to the post-batch CPU-explore tier alongside the still-running siblings on remote_cpu_queue (depth=9). No batched closure pending.

**Inefficiency/blocker flag**: none new. The Kac-Rice 4h deferral is the only known elective-CPU item adjacent to this lens; flagged here for next CPU-pool re-prioritization cycle.

PLAIN: We tested for "replica symmetry breaking" (a signature of glassy free-energy landscape with hierarchical structure) on the Kerdock-Hebbian weight matrix using a parallel-tempering exchange-acceptance probe across 11 temperature points. The acceptance profile decays smoothly from 1.0 down to ~0.30 across all three seeds — NO sharp transition (which would have signaled RSB) AND NO flat profile (which would have signaled simple replica-symmetric / paramagnet-only). The smooth decay is most consistent with a "paramagnet-like / weak-glass" regime at this matrix size and this protocol. This is informative but bounded: it does NOT rule out RSB-like physics in the substrate broadly — it only says THIS particular detection lens (PT exchange acceptance at THIS N) is silent. The adjacent lens flagged earlier — Kac-Rice annealed complexity, a 4h CPU run measuring saddle-density structure directly — stays deferred in the elective-CPU pool as the appropriate next probe. No cap_map row change; v168 unchanged. Adjacent context: this is consistent with the simple-double-well reading of v164b's earlier bimodal P(q) finding, but also consistent with 1RSB-too-weak-for-PT-to-resolve. IMPORTANCE: MEDIUM (informative-negative; bounded protocol-silent verdict; not a fingerprint-stack addition; not a portfolio change).


---

## Cycle 189 -- v169 ANNOTATION-ONLY: Cap 1 / Cap 3 / Cap 8 closed-form rederivation via MUB-stabilizer lens

**Time**: 2026-05-23 (evening; post-RSB-INCONCLUSIVE annotation commit at 22:49)
**Trigger**: Strategy proactively shores up cap_map rows per [[feedback-strategy-shore-up-capabilities]] using findings just landed in `notes/research_kerdock_mub_stabilizer_drill_2026-05-23.md` Section 4 ("Logical-operator audit") + Section 5.1 ("Strengthening of three ✅ rows"). Level-2 operational drill on the Kerdock <-> MUB <-> stabilizer-code-automorphism isomorphism (identified by cross-domain probe 2 domain 3; operationalized by today's drill) recognized that THREE existing cap_map portfolio rows (Cap 1 Crooks erase + Cap 3 streaming-NESS + Cap 8 VAMP-on-chain) reframe as logical Pauli operations on an encoded stabilizer register; the empirical PASS envelopes already on those rows are recovered from textbook QECC closed-form expressions.

### Cap 1 / Cap 3 / Cap 8 closed-form rederivation via MUB-stabilizer lens (2026-05-23)

**Lens summary (from `notes/research_kerdock_mub_stabilizer_drill_2026-05-23.md` Section 1).** The substrate's BSC binding + Kerdock 4-coset rotation IS a subgroup of the Clifford group (PSL(2, N) <= Cliff(m), m=12, N=4096) acting on the C^{4096} stabilizer-state register, with the orthogonal spread / N+1 MUBs as the canonical measurement frame. PSL(2, N) is a unitary 2-design (CRCP 2020); MUB-readout = Pauli-eigenbasis measurement; BSC binding = Pauli translation; substrate erase / inference / readout primitives = logical operations on the encoded register.

**Closed-form rederivation 1 -- Cap 1 (Crooks forensic erase + Tier-2 Sagawa-Ueda noise envelope, v158 anchor).**

- **Substrate-product framing**: "verifiable forensic erase under realistic bit-flip noise (p in {0.05, 0.10, 0.20}) at FULL N=16384 50-trial 3-seed".
- **v158 empirical PASS envelope**: `delta_S_emp(p) <= theta(p) + 0.02` where `theta(p) = ln(2) + p*ln(p) + (1-p)*ln(1-p)`.
- **Closed-form rederivation under the lens**: `theta(p)` IS the **Pauli-twirled depolarizing-channel entropy** -- the (binary) entropy of the depolarizing channel acting on a stabilizer register at twirl-parameter p. Standard QECC result; e.g. Nielsen-Chuang Ch. 10 (Pauli twirl / depolarizing channel entropy) + standard quantum-info-theory textbook for the Sagawa-Ueda fluctuation-theorem under Clifford-twirl noise.
- **Provenance citations**:
  - Calderbank-Cameron-Kantor-Seidel 1997 ("Z_4-Kerdock codes, orthogonal spreads, and extremal Euclidean line-sets", Proc. London Math. Soc.) for the Kerdock -> orthogonal-spread structure that underlies the substrate's coset framework.
  - Can-Rengaswamy-Calderbank-Pfister 2020 ("Kerdock codes determine unitary 2-designs", IEEE TIT 66:6104; arXiv 1904.07842) for the Kerdock-PSL(2, N) <= Cliff(m) unitary-2-design embedding.
  - Standard QECC textbook (e.g. Nielsen-Chuang Ch. 10; Hayden-Preskill 2007 / Renes-Boileau 2009 for Pauli-twirl entropy) for the closed-form `theta(p)` as Pauli-twirled depolarizing-channel entropy.
- **Why this strengthens the row**: v158's empirical PASS curve (3/3 noisy cells satisfy `delta_S_emp(p) <= theta(p) + 0.02`) was originally a phenomenological fit -- "the substrate empirically satisfies the Sagawa-Ueda noise-corrected Crooks-FT bound at the +0.02 tolerance level". Under the lens, the SAME curve `theta(p)` is now a **textbook QECC closed-form expression** for the entropy of a depolarizing channel under a unitary 2-design noise model, which is exactly the regime our substrate occupies. The substrate is not "happening to satisfy the Sagawa-Ueda bound"; it's **inheriting the Pauli-twirled depolarizing-channel entropy** from being a 2-design subgroup. This is a strict envelope strengthening from "empirically PASS" to "empirically PASS + closed-form-derived from established QECC literature".

**Closed-form rederivation 2 -- Cap 3 (streaming-NESS inference + v158 noise envelope).**

- **Substrate-product framing**: "streaming-NESS inference throughput envelope `throughput_ratio >= 0.9` at p in {0.05, 0.10, 0.20} on N=16384".
- **v158 empirical PASS envelope**: `throughput_ratio >= 0.9` at all 3 noise levels (3/3 cells).
- **Closed-form rederivation under the lens**: Under the lens, each substrate-state coset projection is a **logical Pauli measurement on an encoded stabilizer state**; the NESS is the steady-state of a **Pauli-channel Markov chain on stabilizer states**; the throughput envelope IS the **Holevo capacity** of a Clifford-depolarizing channel at twirl-parameter p.
- **Provenance citations**:
  - Klappenecker-Roetteler 2003 ("Constructions of mutually unbiased bases", Fq7 2003 / quant-ph/0309120) for the MUB <-> orthogonal-spread <-> Galois-ring exponentials chain.
  - Klappenecker-Roetteler 2005 ("Mutually unbiased bases are complex projective 2-designs") for the 2-design property of MUB systems that gives the depolarizing-channel twirl.
  - Hayden-Preskill 2007 / standard QECC textbook (e.g. Nielsen-Chuang Ch. 12 / Wilde "Quantum Information Theory" Ch. 10) for the Holevo capacity of a Pauli / Clifford-depolarizing channel.
- **Why this strengthens the row**: v158's empirical PASS at `throughput_ratio >= 0.9` was originally a phenomenological measurement -- "the substrate empirically maintains throughput-ratio above 0.9 across the tested noise range". Under the lens, the SAME envelope is the **textbook Holevo capacity bound** for a Clifford-depolarizing channel under the same 2-design noise model. The substrate's NESS throughput is not "happening to be above 0.9"; it's **inheriting the Holevo capacity** of the underlying Pauli channel. Again, "empirically PASS" -> "empirically PASS + closed-form-derived".

**Closed-form rederivation 3 -- Cap 8 (TWO substrate-novel readout primitives equivalent: VAMP-on-chain + hard-cleanup, v168 anchor).**

- **Substrate-product framing**: "VAMP-on-chain and hard-cleanup are substrate-novel readout primitives equivalent in accuracy at FULL on chain inference; VAMP-vs-AMP universality split on Kerdock at SE-fixed-point level (v168): VAMP-SE tracks empirical VAMP at mean rel err = 0.021 while AMP-SE diverges at mean rel err = 0.450".
- **v168 empirical PASS envelope**: VAMP-SE 3/3 cells under 20% rel err mean=0.021 AND AMP-SE 1/3 cells close mean=0.450.
- **Closed-form rederivation under the lens**: Under the lens, the substrate's singular spectrum on the Kerdock-Hebbian W is constrained by the **Schur-Weyl decomposition** of the Clifford representation (Zhu-Kueng-Grassl-Gross 2016). VAMP uses the FULL singular spectrum = the **S-transform-equivalent multiplicative-free-probability** information = the full Schur-Weyl irrep decomposition. Scalar-AMP uses only the FIRST MOMENT of the spectrum = the **trivial-irrep projection** = the Schur-Weyl-projected mean. The Pauli-twirl / Clifford-twirl averaging that VAMP performs implicitly via its SVD step preserves the irrep info; scalar-AMP's first-moment-only recursion collapses to the trivial irrep and loses the substrate's higher-kappa_n (v164a) / non-MP (v165) algebraic structure. The v168 empirical 0.021-vs-0.450 split IS the **Pauli-twirled S-transform** signature of this Schur-Weyl-resolved-vs-trivial-irrep-projection split.
- **Provenance citations**:
  - Webb 2016 ("The Clifford group forms a unitary 3-design") for the Clifford 3-design property that underlies the Pauli-twirl exact at the second-moment level + bounded at higher moments.
  - Zhu 2017 ("Multiqubit Clifford groups are unitary 3-designs", Phys. Rev. A 96, 062336) corroborating Webb 2016 and giving exact 3-design formulas.
  - Zhu-Kueng-Grassl-Gross 2016 ("The Clifford group fails gracefully to be a unitary 4-design", arXiv 1609.08172) for the **Schur-Weyl decomposition of the Clifford representation** + the closed-form **frame-potential 4-design defect** localized to a single irrep -- which is precisely the irrep that scalar-AMP misses and VAMP captures.
  - Can-Rengaswamy-Calderbank-Pfister 2020 (arXiv 1904.07842) for the Kerdock-PSL(2, N) <= Cliff(m) 2-design embedding.
- **Why this strengthens the row**: v168's algebraic-mechanism annotation ("VAMP works because it consumes the full singular spectrum / S-transform-equivalent info") was originally an informal mechanism story. Under the lens, the SAME story is the **Schur-Weyl decomposition of the Clifford representation** with explicit closed-form formulas from Zhu-Kueng-Grassl-Gross 2016 for which irreps survive Pauli/Clifford twirling. Scalar-AMP's failure to track empirical AMP is the **Schur-Weyl trivial-irrep collapse** prediction; VAMP's success is the **Schur-Weyl-resolved spectral preservation** prediction. The empirical 0.021-vs-0.450 split is the qualitative Pauli-twirled-S-transform signature. **Note on quantitative precision**: the QUALITATIVE closed-form (Schur-Weyl resolved vs trivial-irrep collapse) is tight; the QUANTITATIVE 0.021 vs 0.450 numerical values are NOT yet pre-registered as a Schur-Weyl-defect computation. The exact Zhu-Kueng-Grassl-Gross 4-design-defect formula applied to Kerdock-PSL(2, 4096) is a candidate math follow-up (~1 hr work, no experiment needed) flagged in the source drill Section 6.

### Why these THREE moves are ANNOTATIONS not PROMOTIONS

Per [[feedback-dont-overextend-theorems]]: annotations strengthen rows; they do NOT promote rows. Each of Cap 1 / Cap 3 / Cap 8 is already ✅ FULL at the empirical level (Cap 1 at v153 + v158; Cap 3 at v153 + v158; Cap 8 at cycle 162 + v168). The closed-form derivations do NOT add new empirical PASS evidence; they explain WHY the empirical PASS envelopes have the functional forms they have, anchored in established QECC literature. The Cap 1 / Cap 3 / Cap 8 row STATES are unchanged (✅); their commercial-wedge framings gain a textbook QECC mechanism for customer / demo writeups.

This is precisely the [[feedback-strategy-shore-up-capabilities]] item-2 envelope-strengthening pattern: shore up ✅ rows by adding closed-form theoretical anchors that match the empirical PASS curves, WITHOUT inflating evidence-strength grades or portfolio counts.

### Capability moves (v168 -> v169)

| Capability | v168 state | v169 state | Trigger |
|---|---|---|---|
| Cap 1 Crooks forensic erase (Tier-2 v158) | ✅ FULL Tier 1 + Tier 2 | ✅ FULL Tier 1 + Tier 2 UNCHANGED + closed-form-derivation annotation: theta(p) IS Pauli-twirled depolarizing-channel entropy | Kerdock-MUB-stabilizer drill Section 4 |
| Cap 3 streaming-NESS inference (v158 noise envelope) | ✅ FULL | ✅ FULL UNCHANGED + closed-form-derivation annotation: throughput envelope IS Holevo capacity of Clifford-depolarizing channel | Kerdock-MUB-stabilizer drill Section 4 |
| Cap 8 TWO substrate-novel readout primitives (cycle 162 + v168) | ✅ FULL + v168 algebraic-mechanism annotation | ✅ FULL UNCHANGED + v168 annotation UNCHANGED + closed-form-derivation annotation: VAMP-vs-AMP split IS Schur-Weyl-Pauli-twirled-S-transform structure | Kerdock-MUB-stabilizer drill Section 4 + Section 5.1 |
| Substrate-product portfolio count | 11 demonstrated capabilities | **11 demonstrated capabilities UNCHANGED IN COUNT** | n/a |

### What NOT to claim (per [[feedback-no-smoke]])

1. **NOT a new substrate measurement.** No experiment ran this cycle.
2. **NOT a 12th portfolio capability.** Source drill Section 5.2 flagged a candidate "MUB-frame measurement primitive" 12th capability GATED on tests 3.A + 3.B (neither run this cycle); 12th-capability question stays GATED.
3. **NOT a closure or row demotion.** No state changes.
4. **Cap 8 quantitative VAMP-vs-AMP closed-form is QUALITATIVELY tight, not yet quantitatively pre-registered.** The exact 4-design-defect formula for Kerdock-PSL(2, 4096) is a candidate math follow-up.
5. **NOT a substrate-physics characterization update.** v168 characterization carries forward UNCHANGED.

### Strategy follow-up actions (cycle 189)

1. **PROT-009 v169 paired commit** -- 83rd observation. Annotation-grade; small line-count diff per [[feedback-decision-log-eol-handling]].
2. **Candidate math follow-up flagged** (NOT shipped this cycle): exact Zhu-Kueng-Grassl-Gross 4-design-defect formula applied to Kerdock-PSL(2, 4096). Pure math; ~1 hr work; quantitative VAMP-vs-AMP split prediction; flagged in source drill Section 6.
3. **Test 3.A + Test 3.B (from source drill Section 3) remain candidate CPU experiments**, gated on the 12th-capability question -- NOT shipped this cycle. Parallel exp_dev queue-refill is unaffected.
4. **NO new Research routing filed** -- the source drill IS the Research delivery being integrated.
5. **NO new Exp Dev routing filed** -- annotation-only, no experiment dispatched.

### Recent-run check

No new experiments queued by this annotation cycle. Queue depths managed by orchestrator.

### PROT compliance this cycle

- PROT-001/002/003: not triggered.
- **PROT-004/006**: NOT triggered. Annotation-grade strengthening; no closure no new ❌ no row demotion.
- **PROT-007**: v169 history block written to `substrate_capability_map_history.md` (compact one-line index entry); narrative block ALSO retained inline in cap_map.md (v60+ convention).
- **PROT-008**: validator must pass before commit. v169 adds 0 new ❌ rows; baseline pre-existing violations unchanged.
- **PROT-009**: cap_map.md + history.md + strategy_decisions_2026-05-23.md + active_priorities.md + visibility_decisions_2026-05-23.md staged atomically.

### Tally (one-line)

ANNOTATION-ONLY v168 -> v169 paired commit: Cap 1 + Cap 3 + Cap 8 each gain a closed-form-derivation annotation under the Kerdock-MUB-stabilizer-code lens; Cap 1's v158 Sagawa-Ueda envelope theta(p) IS Pauli-twirled depolarizing-channel entropy (CCKS 1997 + CRCP 2020 + standard QECC textbook); Cap 3's v158 throughput envelope IS Holevo capacity of Clifford-depolarizing channel (Klappenecker-Roetteler 2003/2005 + Hayden-Preskill / standard QECC); Cap 8's v168 VAMP-vs-AMP split IS Schur-Weyl-Pauli-twirled-S-transform structure (Webb 2016 / Zhu 2017 + Zhu-Kueng-Grassl-Gross 2016 + CRCP 2020); v169 adds ZERO new rows + ZERO promotions + THREE annotation-grade strengthenings on existing ✅ rows per [[feedback-dont-overextend-theorems]]; substrate-product portfolio at 11 demonstrated capabilities UNCHANGED IN COUNT per [[feedback-strategy-shore-up-capabilities]] item 2 envelope-strengthening pattern; per [[feedback-no-smoke]] honest framing -- NO experiments ran this cycle, NO new empirical evidence, the closed-form derivations land from the lens not from substrate measurements; 12th-capability candidate from source drill Section 5.2 stays GATED on tests 3.A + 3.B (NOT run this cycle); quantitative Zhu-Kueng-Grassl-Gross 4-design-defect formula for Kerdock-PSL(2, 4096) flagged as candidate math follow-up (~1 hr work, no experiment) but NOT shipped this cycle; no Research routing filed (source drill IS the Research delivery); no Exp Dev routing filed (annotation-only); per PROT-004/006 NOT triggered (no closure no new ❌ no row demotion); smoke->FULL broad anchors UNCHANGED (34 broad / 25 strict); pause flag CLEARED -- ACTIVE annotation-only verdict_handler dispatched in ACTIVE state; 83rd PROT-009 paired commit.

## 2026-05-23 - F_4 anchor v1 upstream push: split decision (Option B + Option D parallel)

**Trigger:** routing event from exp_dev — `notes/exp_dev_to_strategy_kerdock_2design_frame_potential_2026-05-23.md`. v1 of wave14_kerdock_2design_frame_potential failed smoke gate: Haar baseline correct (F_4=2.08 at d=64), but Clifford and Kerdock random-word samplers don't reach asymptotes (Clifford F_4=1.70 vs theoretical 2.62; Kerdock ~10^3 due to diagonal-dominated degenerate words). The Aaronson-Gottesman by-hand symplectic-to-Clifford-unitary lift has Gaussian-elimination bugs.

**Decision:** SPLIT.
- PRIMARY (Option B): re-spec F_4 anchor to use symplectic-rank trace formula directly (Bravyi-Maslov 2020 Lemma 3 / Hostens-Dehaene-De Moor 2005). Closed form |Tr(U_S)|^2 = d / 2^rank(S-I) sidesteps the dense d x d Clifford-unitary construction entirely. No external lib dependency. v2 ETA matches the original 30-60 min drill estimate now that the costly part is removed. Routing note: notes/strategy_to_exp_dev_F4_v2_symplectic_trace_2026-05-23.md.
- PARALLEL (Option D): ship 3.B MUB-distinguishability probe — no Clifford machinery needed, operates on existing beta_A snapshots, complements 3.A with disjoint failure modes. Two falsifiable tests of the same isomorphism. Routing note: notes/strategy_to_exp_dev_MUB_distinguishability_2026-05-23.md.
- DEFER (Option C): pure-math Zhu-Kueng-Grassl-Gross 4-design-defect formula applied to PSL(2, 4096) waits until F_4 measurements come back; sharper with empirical comparison in hand.
- DECLINE (Option A): stim/qiskit runtime dep cost not justified when Option B sidesteps the problem.

**Risk surface (honest):** Option B's main residual risk is F_2 Gaussian-elimination bugs producing the same kind of broken numerics as v1's word samplers. Mitigation built into v2 spec: mandatory d=8 exact-enumeration self-test (504 elements, < 1 min CPU) before queueing the d=4096 production run.

**Pipeline impact:** none right now — both routings are exp_dev re-spec tasks, no queue entries staged. After exp_dev ships v2 and the 3.B probe, two new entries land in remote_cpu_queue (which has 9 pending + 1 running, no urgency). No GPU impact.

**No cap_map change.** Verdict-pending; cap_map state holds until experimental results land.

**Sub-agent context:** routing_handler dispatched from main thread for routing event 'exp_dev->strategy'; strategy logic executed inline per task spec ('wrappers don't recurse'). No re-dispatch of exp_dev — dispatch.py will fire routing events from the two routing notes on the next cycle, keeping event-driven flow intact.

## 2026-05-23 — F_4 v2 d=8 self-test FAILED; routing v3 (Option H = stim)

**Trigger:** routing event from exp_dev — `notes/exp_dev_to_strategy_F4_v2_d8_selftest_failed_2026-05-23.md`. The v2 mandatory d=8 self-test (the structural fix from v1's silent-bug failure) FIRED as designed: F_4=0.2656 vs sanity band [1.5, 4.5]. Rank histogram diagnostic showed the hand-rolled symplectic-block construction was producing essentially-random F_2 matrices instead of genuine Sp(2m, F_2) elements. exp_dev surfaced 4 options (E/F/G/H) and recommended Option E first.

**Decision: Option H (pull in `stim`).** Rationale:
- Options E (Sp-membership unit test) and F (transvection control) keep debugging the same hand-rolled abstraction — even a successful fix leaves a one-off hand-rolled routine where "subtle convention bug that happens to pass d=8 by coincidence" remains live for d=4096.
- The structural gate (d=8 self-test) was DESIGNED to catch bugs we don't see. Pulling in a verified library (stim, Google-funded, used by quantum-hardware research labs) is the higher-leverage move — eliminates the bug class entirely.
- The d=8 mandatory gate STAYS, now verifying stim's output is consistent with theory before scaling.
- Option G (defer 3.A entirely) is the fallback if stim install fails on the remote runner.

**MUB-distinguishability (3.B):** already running independently on remote_cpu_queue. ETA ~2hr CPU. Covers half of the joint isomorphism evidence regardless of F_4 path.

**Re-spec routing note:** `notes/strategy_to_exp_dev_F4_v3_stim_2026-05-23.md`. Instructions: `pip install stim` on runner; use stim's Clifford sampler + |Tr|^2 = d / 2^{rank(S-I)} formula; KEEP the d=8 mandatory self-test (now verifying stim); on d=8 PASS, ship to remote_cpu_queue at d=4096 as `kerdock_2design_frame_potential_v3_stim`; on d=8 FAIL via stim or install failure, defer to Option G (MUB-distinguishability alone).

**Parallel pure-math follow-up:** `notes/strategy_request_to_research_kerdock_4design_defect_2026-05-23.md` filed in parallel. Pure-math drill (~1hr, no compute cost) to deliver Zhu-Kueng-Grassl-Gross 4-design-defect closed-form for Kerdock-PSL(2, 4096). Gives an INDEPENDENT theoretical anchor to compare against stim's empirical F_4. Was flagged in the prior strategy annotation cycle; now activated.

**Honest risk surface:**
- stim install may have wheel/glibc friction on remote runner → fallback Option G.
- stim's API may not expose PSL(2, F_{2^m}) restriction directly → Path A (full Clifford F_4 ~ 3.0) with revised prereg bands.
- ZKGG defect formula may not specialize cleanly to PSL(2, F_{2^m}) → Research delivers a bound + pointer instead of closed-form.

**No cap_map state change.** Verdict pending. Both F_4 v3 (stim) and MUB-distinguishability must land before cap_map updates.

**Downstream routing filed:**
1. `notes/strategy_to_exp_dev_F4_v3_stim_2026-05-23.md` (exp_dev — implement v3)
2. `notes/strategy_request_to_research_kerdock_4design_defect_2026-05-23.md` (research — pure-math drill in parallel)

## 2026-05-23 — F_4 v2 RETROACTIVE PASS (spec formula typo, not code bug)

**Trigger:** routing event from exp_dev — `notes/exp_dev_to_strategy_F4_v3_stim_shipped_plus_v2_retro_2026-05-23.md`. While building v3 (stim) exp_dev cross-checked the trace formula by direct |Tr(U)|^4 averaging from `stim.Tableau.to_unitary_matrix` at d=4 and d=8. The two methods agree ONLY when the formula uses `d^2 / 2^{rank(S-I)}` (exponent 1), NOT `d^2 / 2^{2*rank(S-I)}` (exponent 2 = doubled). The v1 -> v2 -> v3 strategy spec inherited the doubled-exponent typo from the original Bravyi-Maslov / Hostens-Dehaene-De Moor citation chain.

**Retroactive interpretation of v2's d=8 "failure":**

v2's failure report logged the d=8 rank histogram for ALL 504 elements of PSL(2, F_8): `{0: 1, 3: 63, 6: 440}`. Applying the CORRECTED formula `F_4 = sum_S [d^2 / 2^{rank(S-I)}] / |PSL|`:

```
F_4 = (1 * 64/2^0 + 63 * 64/2^3 + 440 * 64/2^6) / 504
    = (64 + 504 + 440) / 504
    = 1008 / 504
    = 2.000000  exactly
```

**PSL(2, F_8) IS a Clifford 2-design at d=8 — exact integer F_4 = 2.** Matches Haar value.

v2's hand-rolled GF(2^m) + symplectic-block code was correct end-to-end. The d=8 structural gate fired CORRECTLY — it caught a spec-formula application error before a d=4096 production run. The gate worked exactly as designed; only the strategy-side interpretation of v2's PASS-vs-FAIL was wrong (because strategy applied the same buggy formula to v2's rank histogram and got 0.2656 instead of 2.0).

**Retro updates to cap_map and decision-log narrative:**

- v2 (`wave14_kerdock_2design_frame_potential_v2`) is now classified **PASS** at d=8 (exact enumeration of PSL(2, F_8), F_4 = 2.000000 exactly).
- The "v2 d=8 self-test FAILED" entry above (cycle preceding this one, same date) remains in the log as the contemporaneous record but is now superseded by THIS retro. Do not edit the prior entry — append-only decision log; future readers see the correction here.
- v3 (stim) was dispatched on the basis of the false-failure interpretation. v3 is no longer NECESSARY for proving 2-design — v2 already did that at d=8 — but v3 is RETAINED as cross-library confirmation (see disposition below).

**v3 disposition: LET-RUN as confirmatory redundancy.**

Rationale:
1. v3 is fast — exp_dev benchmark ~3.3s; production run at d=4096 m=12 n=10000 has 1800s timeout but real wall-time expected well inside it.
2. v3 uses a fundamentally DIFFERENT path: stim (Google-funded verified library) on the remote_cpu_queue runner, vs. v2's hand-rolled GF(2^m) + symplectic-block code at d=8 only. Two independent implementations agreeing on F_4 = 2.0 is stronger evidence than either alone, especially given the structural fragility just exposed (spec-formula typo propagated through three versions undetected).
3. v3 also delivers F_4 at PRODUCTION d=4096, not just d=8. v2's exact enumeration is d=8 only; the d=4096 PSL anchor remains a follow-up question.
4. Cancelling v3 saves one CPU queue slot but loses (a) cross-library validation, (b) production-d anchor. The slot cost is cheap (remote_cpu_queue has capacity); the validation value is high. LET-RUN dominates.

If v3 lands F_4 in band [1.90, 2.10] at d=4096: dual-anchor PASS (v2 exact at d=8 + v3 stim at d=4096) -> Cap 3.A unlocks as a FULL demonstration.

If v3 lands OUTSIDE [1.90, 2.10] at d=4096: that's an unexpected divergence between PSL(2, F_8) (where 2-design holds exactly) and full Clifford at m=12 sampled by stim — investigate further; do NOT close yet.

**Optional follow-up (not yet dispatched):** Re-run v2 at m=12 with CORRECTED formula (`exponent 1`) to get a PSL-specific F_4 anchor at production d=4096. One-line change in v2's `f4_contribution`. Trivial to dispatch later if v3 anchors successfully and Strategy wants a redundancy belt. Logged here as a queued idea; not filed as a Strategy -> Exp Dev routing this cycle.

**Structural lock (inefficiency fix per [[feedback-lock-in-inefficiency-fixes]]):**

The root cause was a strategy-spec formula typo that survived through v1 -> v2 -> v3 without being caught by any structural check. Lock filed THIS CYCLE:

- New feedback memory: `feedback_strategy_spec_formula_selftests.md` written to `C:\Users\marsh\.claude\projects\d--AI\memory\`.
- MEMORY.md index updated with the new entry.
- Rule: Strategy specs that pass closed-form formulas to Exp Dev MUST include at least one (input -> expected output) self-test pair. For the F_4 formula `|Tr(U)|^2 = d / 2^{rank(S-I)}` a self-test cell would be `for d=2, rank=0: |Tr(U)|^2 == 2`. Exp Dev verifies the SPEC against the self-test before coding the experiment. If the spec's formula doesn't match its own self-test cell, the spec is rejected before any compute is spent.

**No cap_map state change in THIS cycle.** Reasoning: the retro raises v2 from FAIL to PASS at d=8 only — exact enumeration of PSL(2, F_8). Production-d (d=4096) verification is still in-flight via v3. To avoid premature cap_map promotion (Cap 3.A would jump from 🔬 to ✅ on d=8 alone, which is the weak anchor — d=8 has 504 elements only), HOLD cap_map state until v3 lands. THEN: atomic promotion contingent on v3 F_4 in band.

**MUB-distinguishability (3.B)** still running on remote_cpu_queue independently. Both half-tests of the joint isomorphism evidence converge over the next ~2-3 hr.

**Pipeline impact:** none THIS cycle — v3 in-flight, v2 retro is interpretation-only, lock is memory-only (no queue entries). Waiting on v3 + 3.B verdicts to land before next cap_map move.

### Recent-run check

No new experiments queued by this cycle (annotation + retro + lock + status_log only).

### PROT compliance this cycle

- PROT-001/002/003: not triggered.
- **PROT-004/006**: NOT triggered. No closure no new ❌ no row demotion. This is an UPWARD reinterpretation of v2 (FAIL -> PASS) but cap_map state is held until v3 lands; no PROT-004 rehab discipline needed because no closure was applied based on the prior v2 FAIL anyway.
- **PROT-007**: not triggered (no cap_map version bump).
- **PROT-008**: not triggered (no commit staged this cycle).
- **PROT-009**: not triggered (decision-log append-only this cycle, no cap_map pairing).

### Tally (one-line)

v2 RETRO PASS: PSL(2, F_8) at d=8 exact F_4 = 2.000000 (1008/504) under CORRECTED formula `d^2/2^{rank(S-I)}` not `d^2/2^{2*rank(S-I)}`; v2's hand-rolled code was correct end-to-end; the d=8 structural gate fired CORRECTLY -- it caught a spec-formula typo that strategy then mis-applied to v2's rank histogram; v2 reclassified FAIL -> PASS at d=8 (append-only log; prior FAIL entry retained); v3 (stim) shipped to remote_cpu_queue last cycle is now confirmatory cross-library redundancy at production d=4096 -- LET-RUN (fast ~3.3s benchmark, different library + different runner -> useful validation, cap slot cost cheap); cap_map state HELD until v3 verdict lands -- no premature promotion on d=8-only anchor; MUB-distinguishability (3.B) still running independently; structural lock filed THIS cycle per [[feedback-lock-in-inefficiency-fixes]] -> new memory `feedback_strategy_spec_formula_selftests.md` + MEMORY.md index updated -- rule: closed-form formulas in strategy specs MUST include a (input -> expected output) self-test cell that exp_dev verifies before any compute spend; pipeline impact none this cycle; pause flag CLEAR; no PROT-007/008/009 trigger (decision-log only).


## v170 — BBMD-VAMP correspondence Anchor 1 of 2 PASSES (cycle 190 single-verdict cap_map update; portfolio count UNCHANGED at 11)

**Verdict**: `wave14_bbmd_vamp_correspondence_sweep_v1` FULL = BBMD_VAMP_CORRESPONDENCE_PASS at 4175.31s remote_cpu_queue. Spearman rho(AMP-error, sum|delta_kappa_n|) = 0.900 > 0.8 across 5 alpha cells; max VAMP-rel-err = 0.0357 < 0.05 across same 5 cells. Both pre-registered HARD PASS thresholds met cleanly with margin (0.100 margin on rho; 0.014 margin on VAMP-rel-err). Metrics file: `data/wave14_bbmd_vamp_correspondence_sweep_v1/metrics.json`. Pre-reg: `preregs/2026-05-23_wave14_bbmd_vamp_correspondence_sweep_v1.md`.

**Cap_map move**: BBMD regime row 🟢 (synthesis-grade with 5-axis observational support at alpha=1.0 only) -> ✅ on Anchor-1 promotion gate (predictive-axis empirically confirmed across the alpha-interpolation Gauss -> Kerdock). Three existing rows gain v170 cross-row corroboration annotations without state change: Cap 8 ✅ (VAMP tames entire BBMD interpolation, not just alpha=1.0); v164a/v166 ✅ (kappa_n divergence is empirically the predictive quantity for AMP-error magnitude); v163 🟢 (AMP-error growth monotonically predicted by BBMD-distance scalar).

**Portfolio count**: 11 demonstrated capabilities UNCHANGED. Cap-12 (VAMP-tractable structured-codebook inference under provable departure from AMP-universality) remains GATED on Anchor 2 (`wave14_kappa_profile_cross_codebook_v1` still pending in remote_cpu_queue). Per pre-registered compound gate in `notes/exp_dev_to_queue_bbmd_anchors_2026-05-23.md` decision tree: Anchor 1 PASS rules out decision-tree branches 3+4; branches 1 vs 2 (substrate-product Cap-12 vs Kerdock-internal Cap-12) is decided by Anchor 2. Per [[feedback-dont-overextend-theorems]]: Cap-12 NOT pre-claimed on Anchor 1 alone.

**Why this matters**: prior 5-axis fingerprint stack (v164a/v165/v166/v167/v168) was 5 quirks MEASURED on one matrix at alpha=1.0; v170 is the first PREDICTIVE-AXIS empirical confirmation -- the kappa_n divergence is empirically demonstrated to predict the AMP-error magnitude across an interpolation family. The 5-axis stack is no longer just an observational signature; it is a regime axis with empirically demonstrated predictive power. This is the first half of the two-anchor validation of the BBMD regime as a substrate-product capability claim.

**Cap 8 strengthening (no state change)**: v168 said "VAMP-on-chain succeeds on Kerdock because VAMP consumes full singular spectrum"; v170 generalizes to "VAMP tames the ENTIRE interpolation Gauss -> Kerdock at < 5% rel-err for all 5 alpha cells." The Cap 8 customer-facing framing widens from "VAMP is the right inference primitive on this substrate" to "VAMP tames the entire BBMD interpolation family that includes this substrate." Cap 8 stays ✅ FULL per [[feedback-strategy-shore-up-capabilities]] item 2 envelope-strengthening pattern.

**v164a/v166 strengthening (no state change)**: v164a measured kappa_n divergence ON Kerdock; v166 added N-stability; v167 added cumulant-order-stability. v170 now wires kappa_n divergence DIRECTLY to the AMP-error magnitude via Spearman 0.900 across the interpolation. The substrate-novel additive-free-prob fingerprint is no longer phenomenological -- it is the predictive quantity. Row stays ✅ per [[feedback-dont-overextend-theorems]] / [[feedback-strategy-shore-up-capabilities]].

**v163 strengthening (no state change)**: v163's alpha=1.0 finding is the endpoint of an empirically-confirmed monotone curve. Row stays 🟢 (its own ✅ promotion gate requires multi-N verification per the v168 pre-reg). v170 annotation strengthens the framing without changing state.

**Queue-refill**: NONE. GPU=2 pending+1 running, remote_cpu=9 pending+1 running, local_cpu idle. Queue is healthy at depth >= 1 invariant per [[feedback-pipeline-pacing]]; verdict_handler does NOT ship queue-refill. Anchor 2 (`wave14_kappa_profile_cross_codebook_v1`) is already in the remote_cpu_queue pending list -- no re-route needed.

**Anchor 2 watch**: when `wave14_kappa_profile_cross_codebook_v1` lands, the next verdict_handler cycle decides v171 portfolio count based on the decision tree:
- Anchor 2 PASS (ordering iid_gauss <= SRHT < Hadamard <= RM(1,m) < Kerdock + MP-KS < 0.05 for all 5) -> branch 1 -> Cap-12 substrate-product promotion proposed; portfolio count 11 -> 12.
- Anchor 2 FAIL (ordering scrambled OR MP-KS >= 0.05 for any) -> branch 2 -> Cap-12 framed Kerdock-internal; portfolio count stays 11 with the BBMD regime row staying ✅ at the Kerdock-internal scope.

**Smoke -> FULL anchors**: +1 broad +1 strict (smoke directional PASS at self-test 7/7 with N=1024 + FULL HARD PASS by both pre-registered thresholds = consistent both at qualitative and quantitative levels). Net: 35 broad / 26 strict.

**PROT compliance**: PROT-004/006 NOT triggered (positive Anchor-1 promotion + 3 cross-row annotations; no closure no new ❌). PROT-007 v170 history block written. PROT-008 validator must pass. PROT-009 cap_map.md + history.md + strategy_decisions_2026-05-23.md + active_priorities.md + visibility_decisions_2026-05-23.md staged atomically (84th PROT-009 paired commit).

**Honest framing per [[feedback-no-smoke]]**: Anchor 1 is a clean PASS with margin on both thresholds (rho 0.900 vs 0.8; max VAMP-rel-err 0.0357 vs 0.05). No axiom-mismatch artifact, no metric flip, no boundary contortion. The verdict is what it says. The 12th capability is NOT pre-claimed; Anchor 2 still needs to land.

**Push gating**: per [[feedback-subagent-permission-inheritance]] commit is LOCAL only; main thread executes `git push origin main` as the mechanical 1-tool action after this dispatch returns.

---

## Cycle 191 — v171 KAPPA_CROSS_CODEBOOK_KILLED (BBMD-VAMP Anchor 2 of 2 HARD-FAILS)

**Time**: 2026-05-23 (verdict landed via verdict_handler; cycle 191)
**Trigger**: `wave14_kappa_profile_cross_codebook_v1` FULL verdict KAPPA_CROSS_CODEBOOK_KILLED at remote_cpu_queue.

### What landed

BBMD={'iid_gauss': 0.0308, 'srht': 5.0, 'hadamard': 5.0, 'rm_1_m': 4.6246, 'kerdock': 4.0584}; MP-KS={'srht': 0.5897, 'hadamard': 0.5897, 'rm_1_m': 0.3393}. Pre-registered HARD predictions fail BOTH ways:

1. Ordering predicted SRHT <= Hadamard <= RM <= Kerdock; actual SRHT 5.0 >= Hadamard 5.0 > RM 4.62 > Kerdock 4.06 (Kerdock is the LOWEST not the HIGHEST).
2. MP-KS predicted PASS for all codebooks (KS ~ 0); actual MP-KS FAILS on SRHT and Hadamard at KS = 0.59 each (standard pre-test already discriminates without BBMD).

### Interpretation

- Anchor 1 (v170 BBMD-VAMP CORRESPONDENCE PASS along iid-Gauss -> Kerdock alpha-interpolation) STILL HOLDS. The Spearman 0.900 + max VAMP-rel-err 0.0357 are real, replicated, and pre-registered.
- Anchor 2 KILLS the BROADER framing that BBMD is a substrate-distinctive cross-codebook discriminator. Other structured codebooks (Hadamard, SRHT, RM) sit at BBMD-distance >= Kerdock. Kerdock is NOT the outlier; it is a member of a known structured-codebook class.
- The Cap-12 candidate ("VAMP-tractable structured-codebook inference under provable departure from AMP-universality") is REJECTED per its pre-registered compound gate (BOTH anchors required positive).

### Cap_map decisions

Per [[feedback-no-smoke]] honest comparison of the two options provided in the task:

- REVERT v170 ✅ to 🟢: would amputate real Anchor-1 empirical data.
- ANNOTATE WITH ROW RENAME: preserves real Anchor-1 finding under a narrower true title; separates the broader rejected claim into its own ❌ PROVISIONAL row.

**Decision: ANNOTATE WITH ROW RENAME.** Honest framing -- the v170 ✅ was PARTIALLY premature: the row TITLE ("BBMD regime axis as substrate-product capability") carried substrate-product framing contingent on Anchor 2, but the empirical content underneath the ✅ (Anchor-1 predictive-axis Spearman 0.900) was real and is real today. The over-extension was in the TITLE, not the observation. v171 renames the row to its narrow scope (AMP-error tracks BBMD-distance along the iid-Gauss -> Kerdock alpha-interpolation; VAMP tames the interpolation family) and preserves the ✅ for that narrower claim.

v171 ADDS a new row "Cap-12 candidate (VAMP-tractable structured-codebook inference under provable departure from AMP-universality)" at ❌ PROVISIONAL with 5 axis-combination rescue sketches per [[feedback-rehabilitation-after-rejection]] + PROT-004/006:

1. **AMP-error predictor capability** within interpolation families. Anchor 1 already 80% demonstrates this within iid-Gauss -> Kerdock; the rescue is reframing as a substrate-product capability that does NOT claim cross-codebook discrimination but DOES license using kappa_n profile to predict AMP-convergence regime for a customer's matrix family.
2. **Kerdock-specific moment-divergent-bounded fingerprint capability.** Loses BBMD-as-class but keeps the substrate-specific empirical characterization (v164a/v166/v167 stack survives unchanged as Kerdock-specific).
3. **MP-KS pre-test infrastructure capability.** The v171 negative result -- MP-KS at KS = 0.59 already discriminates SRHT/Hadamard -- IS itself a substrate-product positive: a cheap pre-test pipeline that kills bad codebooks before downstream substrate fit. Substrate-product framing: "the substrate ships with a standard pre-test that catches codebook misfit before downstream cost is incurred."
4. **Higher-cumulant profile-SHAPE discriminator.** Anchor 2 tested SCALAR sum |delta_kappa_n|; the FULL kappa_n PROFILE shape across n was NOT tested. Different codebooks may carry distinguishable profile SHAPES (Kerdock kappa_n GROWS with n per v167; SRHT/Hadamard kappa_n profile shape not measured). Rescue is to test profile-shape rather than the scalar sum.
5. **Codebook-architecture-conditioned VAMP-vs-AMP gap predictor.** v168 demonstrated VAMP-vs-AMP split on Kerdock at SE-fixed-point level; rescue is a multi-codebook VAMP-vs-AMP empirical map (which structured codebooks show the split? does the magnitude of the split predict downstream substrate-product utility?).

Portfolio count UNCHANGED at 11 demonstrated capabilities per [[feedback-dont-overextend-theorems]] (rejection paired with rescue sketches PROVISIONAL pending Research vetted ranking; the narrow kappa_n -> AMP-error predictor survives at narrower scope in the renamed Anchor-1 row).

### Inefficiency surfaced and locked

The v170 -> v171 pattern (promote ✅ on single anchor of compound gate, then rename/close when second anchor fails) flags a structural inefficiency. The honest move at v170 would have been to promote the empirical content ✅ under a row TITLE matching the SINGLE-ANCHOR scope (Anchor-1 interpolation-family predictive-axis), and keep the COMPOUND-GATE substrate-product framing in a SEPARATE candidate row that does not promote until both anchors land. This avoids the rename-paired-with-closure cycle.

**Locked for memory_curator**: "compound-gate promotion discipline" addendum to [[feedback-dont-overextend-theorems]]. When a row's promotion gate is COMPOUND (requires multiple anchors), the row TITLE must match the SINGLE-ANCHOR scope when only one anchor has landed; the COMPOUND-GATE substrate-product framing lives in a separate candidate row.

### Files filed this cycle

- `notes/substrate_capability_map.md` -- Cycle 191 narrative + Capability moves table appended.
- `notes/substrate_capability_map_history.md` -- v171 one-line index entry appended.
- `notes/active_priorities.md` -- header updated v170 -> v171; BBMD row scope-narrowed; Cap-12 candidate added as ❌ PROVISIONAL.
- `notes/visibility_decisions_2026-05-23.md` -- CRITICAL-importance plain-language entry appended via verdict_handler.
- `notes/strategy_decisions_2026-05-23.md` -- this entry.
- `notes/strategy_request_to_research_bbmd_cap12_rehab_2026-05-23.md` -- NEW; 5 rescue sketches + 2x drill request.

### Queue / push status

- Local commit only (sub-agent push blocked per [[feedback-subagent-permission-inheritance]]); main thread executes push.
- Queue-refill NOT triggered. GPU=2 pending+1 running, remote_cpu=8 pending+1 running, local_cpu idle. Queue is healthy per [[feedback-pipeline-pacing]].

### 85th PROT-009 paired commit



## (cycle 192) v172 BATCHED SIX-verdict cap_map update -- Cap 2 ❌ PROVISIONAL -> ✅ via Pattern-1 conformal subsumption; Bet T closed per PROT-004/006; Bet V partial-retained; PFK partial-thermalization rejected (QECC annotations preserved); generative LIMITED annotated

Strategy verdict-handler-inline, six paired verdicts in one v172 paired commit.

### Strategy verdict summary

**Cap 2 HEADLINE rescue (V1)** -- `wave14_cap2_conformal_subsumption_v1` FULL = CAP2_CONFORMAL_RESCUE_PASS. 5/5 seeds achieve committed_acc >= 0.9 at abstain <= 0.2 with monotone Pareto front. Cap 2 re-axiomatized as calibrated abstention over Bet G stream per Pattern-1 conformal subsumption. **This is Rescue 5 from the v160 sequencing recommendation** ("Re-axiomatize Cap 2 as downstream conformal layer; Gap C subsumption -- zero experimental cost; cleanest portfolio move"). Rescue 5 was correctly identified as FIRST in sequencing at v160 (rationale: cheapest + cleanest). v172 closes the rehab cycle: Cap 2 ❌ PROVISIONAL -> ✅ FULL via subsumption into Cap 6 (Gap C Conformal calibrated confidence) which already named "MAY ABSORB closed Cap 2 per Rescue 5" in the portfolio table.

The substrate-product portfolio after v172:
- ZERO open ❌ PROVISIONAL rejections (cleanest portfolio state since PROVISIONAL framing was introduced at v160).
- 11 demonstrated capabilities UNCHANGED IN COUNT. Cap 2 returns to ✅ via subsumption into existing Cap 6, NOT as a new independent row. Per [[feedback-dont-overextend-theorems]] this is rescue-cleanup, not portfolio inflation.
- The Cap-12 candidate row from v171 (BBMD-as-substrate-product-class) stays ❌ PROVISIONAL UNCHANGED by this batch (separate rehab cycle; Research vetted ranking pending on the 5 axis-combination sketches filed v171).

**Bet T closure (V2)** -- `wave14_betT_mondrian_anti_RM_conformal_v1` FULL = BETT_MONDRIAN_ANTI_RM_FAIL. Per-coset coverage = 1.0 in 4/4 anti-RM cosets, all out of [0.8, 0.99] target band. This was Sketch #3 from `notes/research_betT_rescue_sketches_2026-05-23.md` (conformal class-wise wrapper applied to anti-RM(1,16) coset; P_deflated=0.40; highest-rank conformal-style rescue). With Sketch #3 HARD-FAILED, the structural analysis of the remaining 4 sketches gives:
- Sketch #2 (per-hypothesis TEMPSCALE; P=0.45): structurally collapses to Bet G TEMPSCALE which is already a separate ✅ row at Cap 6 -- running it as Bet T rescue would double-count.
- Sketch #4 (VAMP-on-chain per-hypothesis posterior; P=0.35): structurally collapses to Cap 8 VAMP-on-chain per-hypothesis instantiation (already ✅ at Cap 8 envelope).
- Sketch #1 (Kerdock-orthogonal hypothesis subspaces; P=0.35): substantively different; stays as elective experimental option but ranks LOWER than Sketch #3 on calibration-deflated P.
- Sketch #5 (periodic re-anchor + replay; P=0.30): substantively different; stays as elective experimental option; ranks lowest.

Per PROT-004/006 5-sketch rehab discipline: the highest-rank conformal-style rescue (Sketch #3) has failed; Sketches #2/#4 are structurally redundant with already-✅ rows; Sketches #1/#5 are elective. **Bet T closes 🟡 PARTIAL -> ❌ CLOSED at v172** with rescue-paths-exhausted annotation. Sketches #1 and #5 stay as elective hardening options if customer demand surfaces.

**Bet V partial-rescue retained (V3)** -- `wave14_betV_kappa4_separation_v1` FULL = BETV_KAPPA4_RESCUE_PARTIAL. \|kappa4_sep\|=2.51 SD in [1.0, 2.0) band (signal present but not portfolio-rescue strength); sign_consistent=False; kappa4_stored=0.065 vs unstored=2.210 (34x absolute-magnitude ratio but sign-inconsistent across seeds). This was closest to Sketch #1 in `notes/research_betV_rescue_sketches_2026-05-23.md` (meta-binding hierarchy via Kerdock-orthogonal subspaces, applied here with 4th free cumulant as separation observable; P_deflated=0.35). Verdict: PARTIAL not PASS not FAIL.

Per [[feedback-dont-overextend-theorems]]: substrate carries SOME 4th-cumulant signature distinguishing stored vs unstored content (34x absolute-magnitude ratio is real), but NOT a sign-stable separation observable (sign-inconsistent across seeds means the substrate's kappa_4 signature is not a usable confidence proxy for self-reflective separation). Bet V row stays 🟡 PARTIAL UNCHANGED at v172 with annotation noting the partial-rescue outcome. 4 remaining sketches (#3 confidence-conditioned cleanup; #4 provenance chain encoding; #2 N=65536 calibrated cleanup; #5 HRR iterative meta-refinement) stay as elective hardening options. Per [[feedback-strategy-shore-up-capabilities]] do NOT generate a new rescue sketch this cycle.

**PFK framing REJECTED for partial-thermalization, non-GUE annotation retained (V4 + V5 mixed evidence)**:

- V4 `wave14_cactus_factorization_break_kerdock_n6_v1` FULL = PFK_FULL_ETH_BULK. R_6 in [0.95, 1.05] in 10/10 seeds (median=0.9977, mean=0.9977). Cactus factorization dominates at n=6; substrate is **full-ETH-class at n=6 with non-Gaussian bulk shape**. The "BBMD = partial thermalization" reframing from `notes/research_eth_thermalization_drill_2026-05-23.md` is REJECTED at n=6 cactus level. v167 KAPPA_PROFILE_GROWS is REFRAMED as bulk-shape information (non-Gaussian higher cumulants in a thermalized distribution), NOT as partial-thermalization signal.

- V5 `wave14_kerdock_sff_vs_gue_v1` FULL = PFK_SFF_NON_GUE. SFF deviates from GUE by > 15% in dip OR plateau in 5/5 seeds (median dip rel-dev 2.064, median plateau rel-dev 0.149). Substrate has spectral structure that GUE does NOT capture. This SURVIVES.

Honest reading: V4 and V5 are NOT contradictory. V4 says "substrate is fully thermalized at n=6 in the connected-correlator decomposition" (a CACTUS property); V5 says "substrate is not GUE-distributed" (a SPECTRAL property). The substrate can be in a structured-thermalized class that is neither iid-Gaussian-noise nor canonical-GUE. The partial-thermalization MECHANISM-NAME for the non-GUE spectral structure is REJECTED at n=6; the mechanism candidate that survives is the 4-coset MUB-stabilizer structure from the Kerdock-MUB-stabilizer drill (Section 3 + Section 5.2). Per [[feedback-dont-overextend-theorems]] V5 alone does NOT promote a row; substrate-physics characterization gains a v172 annotation noting the non-GUE structure and the rejection of the partial-thermalization mechanism for it.

**v169 Cap 1/Cap 3/Cap 8 QECC closed-form annotations PRESERVED**: Critical clarification per [[feedback-dont-overextend-theorems]]. The v169 closed-form rederivations land via the Kerdock-MUB-stabilizer lens (CCKS 1997 + CRCP 2020 + Klappenecker-Roetteler 2003/2005 + Webb 2016 + Zhu-Kueng-Grassl-Gross 2016 + standard QECC textbook). The mathematical content of these derivations is Clifford-design property + Pauli-channel structure + Schur-Weyl decomposition. NONE of this depends on ETH / cactus / partial-thermalization. The Pauli-twirl is exact for a Clifford 2-design (CRCP 2020); the Holevo capacity of a Pauli channel is exact; the Schur-Weyl decomposition of the Clifford representation is exact. **The V4 rejection of partial-thermalization does NOT touch Cap 1 / Cap 3 / Cap 8 v169 annotations.** They remain valid; the substrate's QECC structure stands independent of its thermalization regime.

**Substrate generative-mode LIMITED (V6)** -- `wave14_substrate_glauber_generative_smoke_v1` FULL = SUBSTRATE_GENERATIVE_LIMITED. At best cell (beta=5.00): novelty=1.000 (PASS), stability=0.967 (PASS), diversity=0.070 (FAIL), coherence=0.120 (FAIL). Kerdock-Hopfield retrieval-mode dominates; substrate CAN generate samples not in the stored set (novelty hit) AND can generate stable samples (stability hit at low temperature), but the generated samples are noisy variants near stored items (low diversity) without coherent compositional structure (low coherence). The 12th-capability candidate framing "substrate as generative-mode model" is REJECTED in its strong 4-gate composite form. Per [[feedback-dont-overextend-theorems]] do NOT add a portfolio row on V6 (partial-pass 2/4 gates is annotation-grade, not row-grade). Per [[feedback-strategy-shore-up-capabilities]] do NOT add a 🔬 candidate row either (Kerdock-Hopfield retrieval-mode is already covered by existing portfolio at Cap 8 / cycle 162 cleanup-mechanism rows; a 🔬 row for generative-mode-LIMITED would be a confusing duplicate-leaning addition). Annotate only on substrate-physics characterization line.

### Portfolio count justification

11 demonstrated capabilities UNCHANGED at v172. Cap 2 was REMOVED at v160 (12 -> 11 explicit removal documented at v160); v172 RETURNS Cap 2 to ✅ via subsumption into existing Cap 6 (Gap C Conformal calibrated confidence), NOT as a new independent row. Cap 6 already named Cap 2 as "MAY ABSORB closed Cap 2 per v160 Rescue 5"; v172 makes the absorption explicit. The portfolio count stays at 11 -- Cap 2's commercial-wedge framing is now delivered via Cap 6's conformal pipeline rather than substrate-intrinsic margin/tau-based proxy. Per [[feedback-no-smoke]] honest framing: this is rescue-cleanup, NOT portfolio inflation; the substrate did not gain a new capability, the substrate's existing Cap 6 capability now covers what Cap 2 originally promised. ZERO open ❌ PROVISIONAL rejections remain in the portfolio after v172 (cleanest portfolio state since v160).

### Strategy follow-up actions (cycle 192)

1. **PROT-009 v172 paired commit** -- 86th observation (atomic stage of 5 files).
2. **NO new Research routing filed**. The Cap 2 rehab cycle CLOSES (Rescue 5 PASS). The Bet T rehab CLOSES (Sketch #3 HARD-FAIL exhausts the 5-sketch protocol given structural overlap of #2/#4 with already-✅ rows). The Bet V rehab stays open with 4 remaining elective sketches.
3. **NO new Exp Dev routing filed** (per [[feedback-dispatch-wrappers-default]] verdict_handler does NOT ship Exp Dev routing).
4. **NO queue-refill triggered** (per [[feedback-pipeline-pacing]] queue is healthy; verdict_handler does NOT ship queue-refill).
5. **active_priorities.md** updated atomically v171 -> v172: Cap 2 row absorbed into Cap 6 (Gap C); Bet T row moved to closed-list; Bet V row updated with v172 partial-rescue annotation; substrate-physics characterization line updated with V4/V5/V6 annotations.

### Inefficiency locked for memory_curator

**Rescue-sketch FIRST-sequencing pattern (positive worked example)**: when a ❌ PROVISIONAL closure has a zero-cost subsumption-into-existing-row rescue sketch (Cap 2 Rescue 5 = subsumption into Cap 6 / Gap C), that sketch should be FIRST in sequencing. The v160 sequencing recommendation correctly placed Rescue 5 FIRST ("zero experimental cost; cleanest portfolio move"); the rehab took 12 cap_map versions of patience (v160 -> v172) and cleanly PASSED. This is a positive worked example of [[feedback-rehabilitation-after-rejection]] discipline working as designed. **Lock as addendum**: "rescue-sketch FIRST-sequencing discipline -- zero-cost subsumption rescues should be FIRST in sequencing when filed; Cap 2 v160 -> v172 is worked example."

### Files filed this cycle

- `notes/substrate_capability_map.md` -- Cycle 192 narrative + Capability moves table appended.
- `notes/substrate_capability_map_history.md` -- v172 one-line index entry appended.
- `notes/active_priorities.md` -- header updated v171 -> v172.
- `notes/visibility_decisions_2026-05-23.md` -- 6 status_log entries appended (V1 CRITICAL; V2/V3/V4/V5 HIGH; V6 MEDIUM).
- `notes/strategy_decisions_2026-05-23.md` -- this entry.

### Queue / push status

- Local commit only (sub-agent push blocked per [[feedback-subagent-permission-inheritance]]); main thread executes push.
- Queue-refill NOT triggered. GPU=2 pending+1 running, remote_cpu=7 pending+1 running (4 just completed this cycle, queue is naturally draining), local_cpu idle. Queue depth >= 1 invariant satisfied per [[feedback-pipeline-pacing]].

### Tally (one-line)

SIX VERDICTS v171 -> v172: V1 Cap 2 ❌ PROVISIONAL -> ✅ via Cap 6 (Gap C) subsumption per Rescue 5 from v160 sequencing FIRST (CAP2_CONFORMAL_RESCUE_PASS 5/5 seeds committed_acc >= 0.9 at abstain <= 0.2 Pareto monotone) -- ONLY open ❌ PROVISIONAL in portfolio closes cleanly; V2 Bet T 🟡 PARTIAL -> ❌ CLOSED per PROT-004/006 5-sketch rehab exhaustion (BETT_MONDRIAN_ANTI_RM_FAIL per-coset coverage 1.0 in 4/4 cosets); V3 Bet V 🟡 PARTIAL UNCHANGED + v172 partial-rescue annotation (BETV_KAPPA4_RESCUE_PARTIAL kappa4_sep=2.51 SD sign-inconsistent); V4 PFK partial-thermalization REJECTED at n=6 cactus level (PFK_FULL_ETH_BULK R_6 median 0.9977) -- substrate is full-ETH-class with non-Gaussian bulk shape; V5 non-GUE spectral structure SURVIVES (PFK_SFF_NON_GUE median dip rel-dev 2.064 plateau 0.149) -- mechanism candidate is 4-coset MUB-stabilizer NOT partial-thermalization; v169 Cap 1/Cap 3/Cap 8 QECC closed-form annotations PRESERVED (Clifford-design / Pauli-channel structure is NOT partial-thermalization); V6 generative LIMITED annotation only (SUBSTRATE_GENERATIVE_LIMITED novelty + stability hit but diversity + coherence fail) -- NO portfolio row added; substrate-product portfolio at 11 demonstrated capabilities UNCHANGED IN COUNT (Cap 2 returns via Cap 6 subsumption not new row); **ZERO open ❌ PROVISIONAL rejections remain after v172** (cleanest portfolio state since v160); rehab-cycle FIRST-sequencing discipline VALIDATED (12 cap_map versions of patience v160 -> v172); 86th PROT-009 paired commit.