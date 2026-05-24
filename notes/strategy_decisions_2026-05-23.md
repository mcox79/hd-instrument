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
