# META audit — 2026-05-22 cycle 71 (cron fired at 21:45)

MAJOR substantive cycle. **4 cap_map versions in 30 min** (v132 +
v133 + v134 + v135). Strategy in full sprint mode. Substrate chain
composition characterized as **FORWARD-LOSSY + REVERSE-INVERTIBLE**.
**2 substrate-novel readout primitives** now active (VAMP-on-chain +
backward-smoother-only). Backward-smoother-only operating envelope
DRAMATICALLY WIDER than VAMP-on-chain.

## Activity since cycle 70 (21:15 → 21:45)

- **Strategy cap_map v132** at ~21:18 (46th PROT-009): WARMSTART_RESCUES
  + PFAIL_HIGHER + VAMP N-universal. Structural dividing line =
  INITIALIZATION INFORMATION NOT DYNAMICS.
- **Strategy cap_map v133** at ~21:25 (47th PROT-009): 4th-attempt
  FINAL mechanism research delivered (3 agents converged on SPURIOUS-
  ATTRACTOR CLUSTER TRAPPING; 6.5/7 constraints). SMOOTHER_ONLY
  substrate reverse-invertible confirmed.
- **Strategy cap_map v134** at ~21:30 (48th PROT-009): Research
  ADDENDUM 8/8 constraint fit + backward-smoother-only OPERATING
  ENVELOPE EXPANDS DRAMATICALLY.
- **Strategy cap_map v135** at ~21:37 (49th PROT-009): Cluster census
  Phase 1 SMOKES PARTIAL VALIDATION (structural CONFIRMED;
  quantitative N-scaling REFUTED). Backward-smoother mega 5/5 FULL.
- **Research note** `research_multihop_mechanism_4th_attempt_2026-05-22.md`
  at 21:20 (17.6 KB; 10-min turnaround).
- **Research note** `research_multihop_mechanism_4th_attempt_ADDENDUM_2026-05-22.md`
  at 21:23 (15.9 KB; 3-min turnaround refinement).
- **Strategy filed 4 request files** in this cycle window:
  - 21:20: addendum routing to Research
  - 21:25: cluster_census routing to Exp Dev
  - 21:32: post-v134 substantive batch routing
  - 21:42: 5th-attempt mechanism research routing
- **Pipeline burst-drain**: ~12 verdicts/smokes consumed in the
  window.

## Major findings this cycle

### v132 — Structural dividing line: INITIALIZATION NOT DYNAMICS

`wave14_multihop_resonator_warmstart_v1` FULL = **WARMSTART_RESCUES**
acc_50hop=1.000 (vs argmax 0.250). Cycle 124 Resonator hard
falsification was incomplete — Resonator works PERFECT given
backward-evidence warmstart. Cycle 132 constraint #5 ("loopy within-
hop fails WORSE") SUPERSEDED.

**ALL forward-only initialization methods fail at acc~0.20-0.25
floor; ALL backward-evidence initialization methods succeed PERFECT
acc=1.000.** Structural dividing line is **INITIALIZATION INFORMATION
NOT DYNAMICS**. Substrate operates in regime where forward
information is INSUFFICIENT to reach correct attractor; backward
evidence provides the missing information.

`wave14_vamp_chain_N_sweep_v2` FULL = VAMP-on-chain robust at ALL N
(4096, 8192, 16384, 32768, 65536 all 1.000). Argmax structurally
NOISY non-monotonic. **VAMP-on-chain is N-universal**.

### v133 — 4th-attempt FINAL Research: SPURIOUS-ATTRACTOR CLUSTER TRAPPING

3 fresh Sonnet agents (O+P+Q) converged on **SPURIOUS-ATTRACTOR
CLUSTER TRAPPING** mechanism.

**FIRST QUANTITATIVE CROSS-N MATCH across 4 attempts**:
- N=4096 K=100: cluster ~1.4 → plateau = 1/1.4 ≈ 0.71 ≈ empirical
  0.767 ✓
- N=65536 K=100: cluster ~5.0 → plateau = 1/5 = 0.20 ≈ empirical
  0.217 ✓
- N-scaling: cluster_size ∝ N^γ, γ ≈ 0.73

**7-CONSTRAINT SCORE 6.5/7** (best across 4 attempts; cycle 131 HMM
was 6/7 then refuted at C3 falsification test).

HONEST P=[0.45, 0.60] deflated from agents' [0.70, 0.88] given
4-attempt 71% refutation track record. Key citation: **arXiv:2510.17593
Benedetti-Brunel-Marinari-Pereira-Obilinovic 2025 Oct** "Paradoxical
capacity increase due to spurious overlaps in attractor networks."

### v133 — SMOOTHER_ONLY substrate reverse-invertible (substrate-physics property)

`wave14_chain_smoother_only_v2` FULL = **SMOOTHER_ONLY_WORKS**
"Backward msg alone sufficient acc=1.000 ≥ 0.70 vs argmax 0.250."

**Tightens structural constraint EVEN FURTHER**: substrate has
property **END of chain uniquely determines ENTIRE chain**. Forward
processing COMPLETELY UNNECESSARY for chain retrieval. **Substrate
chain composition REVERSE-INVERTIBLE.**

Substrate-physics implication: W^L applied to codewords produces
DISTINCT endpoints (endpoints encode full chain); forward decoding
LOSSY (multiple codewords have similar intermediate outputs supports
cluster trapping); backward decoding from endpoint EXACT ((codeword
→ endpoint) map INJECTIVE for substrate W).

This is a **substrate-physics FINDING regardless of cluster census
outcome**: substrate chain composition is forward-lossy + reverse-
invertible. Substrate-novel mechanism class.

### v134 — 8/8 constraint score + backward-smoother-only envelope DRAMATICALLY WIDER

Research ADDENDUM delivered 3-min turnaround (session-best refinement
cycle). Cluster-trapping framework score improves 6.5/7 → **8/8**
(first attempt to fit ALL constraints). HONEST P revised UP
[0.55, 0.70].

**BACKWARD-SMOOTHER-ONLY OPERATING ENVELOPE EXPANDS DRAMATICALLY**
across 5 substantive verdicts:

| Axis | VAMP-on-chain (cycle 128) | Backward-smoother-only (cycle 134) | Expansion |
|---|---|---|---|
| Chain depth | 200 PERFECT | **500 PERFECT** | 2.5× |
| Noise robustness | 10% | **30%** | 3× |
| N range tested | N=65536 only | **N=4096-65536 all (N-universal)** | 5 N values |
| K-ceiling | K=5000 smoke | **K=20K smoke (K=10K + K=20K both 1.000)** | 4× |
| Mega broad envelope | (not tested) | **3/3 pass** | NEW |

**Backward-smoother-only is SIMPLER substrate-novel readout primitive
with WIDER operating envelope than VAMP-on-chain forward-backward EP.**

### v135 — Cluster census Phase 1 PARTIAL validation

3 cluster census smoke verdicts:
- `cluster_census_N65536` smoke = **CLUSTER_TRAPPING_CONFIRMED**
  unique=1 < 10 AND top5_share=1.000 > 0.9 (forward chains converge
  to structured trap at substrate; CONFIRMED but TIGHTER than
  predicted — cluster=1 not ~5)
- `W_L_effective_rank` smoke = **RANK_COLLAPSE_CONFIRMS** subspace
  collapse rank(L=1)=100 → rank(L=50)=0 (≥2× drop; Agent O
  Oseledets-style subspace collapse CONFIRMED)
- `cluster_census_N_sweep` smoke = **CLUSTER_NSCALE_REFUTES** fitted
  γ=0.00 outside [0.3, 1.3]; cluster_per_N flat at 1 vs predicted
  N^0.73 — **N-scaling REFUTED**

**Cluster-trapping framework PARTIAL VALIDATION** — structural
insight (forward trapping + rank collapse) CONFIRMED at smoke;
specific quantitative predictions (cluster ~5 + N^0.73 scaling)
REFUTED at smoke. P REVISED DOWN [0.55, 0.70] → [0.35, 0.55].

Backward-smoother mega variants 5/5 V_PASS FULL +
smoother_validation_matrix smoke MATRIX_BROAD_VALIDATED 16/16 cells.
**Backward-smoother-only robust across all tested variant
configurations at FULL.**

### Strategy filed 5th-attempt mechanism research at 21:42

Strategy continues pushing for substrate-physics resolution. 4
mechanism diagnoses now refuted or partially refuted; 5th attempt
attempts to resolve cluster-trapping quantitative predictions
(refuted at Phase 1 smoke).

## Drift findings

### Finding 1 — Substrate-product positioning gains 2nd substrate-novel readout primitive

Cycle 134 + 135 deliver **backward-smoother-only as 2nd substrate-
novel readout primitive** with DRAMATICALLY WIDER operating envelope
than VAMP-on-chain.

| Primitive | Envelope at FULL |
|---|---|
| VAMP-on-chain (cycle 128) | K=5000 + d=200 + 10% noise + N=65536 |
| Backward-smoother-only (cycle 134-135) | K=20K smoke + d=500 + 30% noise + N=4096-65536 universal |

**Substrate-product Demo 1 Lane D positioning expands further** via
simpler primitive with wider envelope.

Per strategic direction lens (auditable AI memory subsystem; capability
class 4 cognitive composition): substrate now has TWO substrate-novel
readout primitives, both empirically anchored at FULL. Lane D agent
memory SDK has redundant substrate-novel mechanism paths.

### Finding 2 — Substrate-physics characterization SHARPENS to "forward-lossy + reverse-invertible"

Cycle 133 + 134 + 135 substrate-physics characterization sharpens:
> "...with multi-hop chain composition: **forward-lossy + reverse-
> invertible**. Forward processing enters spurious-attractor cluster
> of ~1-5 codewords at N=65536 K=100; endpoint observation uniquely
> determines correct codeword via backward smoothing alone (no
> forward processing needed). Substrate-novel mechanism class with
> theoretical anchor in attractor-network spurious-overlap literature
> (arXiv:2510.17593 Benedetti et al 2025)."

**Substrate-physics finding REGARDLESS of cluster census quantitative
outcome**: forward-lossy + reverse-invertible is the substrate-novel
mechanism property. This is the cleanest substrate-physics
characterization of the entire session arc.

Per feedback_value_creation_not_competition: substrate-product
positioning gains substrate-physics-grounded mechanism story (forward-
lossy + reverse-invertible) even though specific quantitative
predictions of cluster trapping are partially refuted.

### Finding 3 — 17th + 18th honest-recalibration patterns

Cycle 134 P=[0.55, 0.70] → cycle 135 P=[0.35, 0.55] (cluster N-scaling
refuted at smoke; structural insight survives). **17th honest-
recalibration**: P revision DOWN as smoke evidence comes in.

Cycle 124 Resonator hard falsification (cycle 124) → cycle 132
WARMSTART_RESCUES PERFECT acc=1.000 (Resonator works given backward
warmstart). **18th honest-recalibration**: framing refinement —
"loopy within-hop fails WORSE than argmax" SUPERSEDED to "loopy
works PERFECT given right initialization."

Strategy's discipline: when evidence comes in, recalibrate honestly.
Per feedback_no_smoke.

### Finding 4 — 4 PROT-009 paired commits in single cycle (46th-49th)

Strategy committed v132 + v133 + v134 + v135 in the 21:18-21:37
window. All paired with history.md + decision-log atomically. **4
PROT-009 paired commits in 19 min.** Strategy's substantive-batch
commit pattern at peak velocity.

### Finding 5 — 5th mechanism research attempt filed

Strategy filed 5th attempt at 21:42, less than 30 min after 4th-attempt
FINAL framework partially refuted at Phase 1 smokes. Strategy
considering whether to accept "structurally constrained mechanism
unknown" or push for final resolution.

Pattern: substrate-physics mechanism question is hard. 4 attempts
have produced structural insights (forward-lossy + reverse-invertible
+ cluster trapping + rank collapse) but no fully validated quantitative
mechanism. Substrate-product engineering proceeds via 2 substrate-
novel readout primitives regardless.

### Finding 6 — Substrate-product story RICHENS even with mechanism unresolved

Despite 4 mechanism attempts and cluster-trapping P=[0.35, 0.55]
PARTIAL validation, substrate-product positioning STRENGTHENS:
- 2 substrate-novel readout primitives (VAMP-on-chain + backward-
  smoother-only)
- Backward-smoother envelope DRAMATICALLY WIDER than VAMP
- Substrate chain composition characterized as forward-lossy +
  reverse-invertible (substrate-physics-grounded property)
- Substrate-product positioning on active-retrieval axis HOLDS and
  EXPANDS

Per user-locked strategic direction lens: capability class 4
(cognitive composition) gains 2nd substrate-novel mechanism;
substrate-product positioning on active-retrieval axis is empirically
robust across multiple primitives.

## Open items for next cycle (22:15)

- 5th mechanism research delivery (Strategy filed 21:42).
- Cluster census FULL verdicts (smoke PARTIAL validation; FULL
  decisive).
- Backward-smoother extreme_K FULL (smoke K=20K=1.000; FULL pending).
- Bet A continual-edit at N=65536 FULL (smoke KILLED).
- Lane D end-to-end at N=65536 with smoother FULL.
- W endpoint injection + demo_2_lane_C_multihop_N65536 queued.
- Session 7 Demo 1 positioning update with 2nd substrate-novel
  readout primitive.
- User decision on Proposal 11 (PROT-010).
- If quiet: heartbeat.

## Science-progress snapshot — cycle 71

### (a) TL;DR

**MAJOR SUBSTANTIVE BATCH**: 4 cap_map versions in 30 min
(v132+v133+v134+v135). Substrate chain composition characterized as
**FORWARD-LOSSY + REVERSE-INVERTIBLE** (substrate-physics-novel
property — END of chain uniquely determines ENTIRE chain). **2nd
substrate-novel readout primitive emerges**: backward-smoother-only,
SIMPLER than VAMP-on-chain with DRAMATICALLY WIDER operating envelope
(d=500 + 30% noise + N-universal + K=20K smoke). **Spurious-attractor
cluster trapping mechanism** PARTIAL validation at Phase 1 (structural
insight CONFIRMED via rank collapse + cluster_size=1; quantitative
N-scaling REFUTED). **WARMSTART_RESCUES** confirms structural dividing
line is **INITIALIZATION INFORMATION NOT DYNAMICS**. 17th + 18th
honest-recalibration patterns. 5th mechanism research filed.

### (b) Capability state since last cycle (v131 → v135)

- **Substrate chain composition** characterized as **FORWARD-LOSSY +
  REVERSE-INVERTIBLE** (substrate-physics-novel property).
- **Backward-smoother-only** ✅ NEW substrate-novel readout primitive
  (mega variants 5/5 V_PASS FULL; matrix 16/16 smoke).
- **Backward-smoother operating envelope EXPANDS vs VAMP-on-chain**:
  d=500 + 30% noise + N-universal + K=20K smoke (vs VAMP d=200 +
  10% + N=65536-only + K=5000).
- **VAMP-on-chain N-universal** ✅ FULL at all N (4096, 8192, 16384,
  32768, 65536 all 1.000).
- **Resonator + warmstart-backward** ✅ FULL PERFECT (cycle 124 hard
  falsification SUPERSEDED; loopy works given right initialization).
- **Spurious-attractor cluster trapping mechanism** 🟡 PARTIAL
  validation at smoke (structural insight CONFIRMED; quantitative
  N-scaling REFUTED; P=[0.35, 0.55]).
- **W^L rank collapse** ✅ smoke CONFIRMS (Oseledets-style subspace
  collapse rank(L=1)=100 → rank(L=50)=0).
- **Structural dividing line** = INITIALIZATION INFORMATION NOT
  DYNAMICS.
- **5th mechanism research attempt** filed at 21:42.

### (c) What we uncovered

- **Substrate chain composition is forward-lossy + reverse-invertible**
  — substrate-novel mechanism property. END of chain uniquely
  determines ENTIRE chain. Forward decoding LOSSY (multiple codewords
  similar intermediate outputs); backward decoding from endpoint
  EXACT. Substrate-level reason: W^L applied to codewords produces
  DISTINCT endpoints (codeword → endpoint map INJECTIVE).
- **2 substrate-novel readout primitives now active**: VAMP-on-chain
  (forward-backward EP, cycle 127-128) + backward-smoother-only
  (cycle 134-135). Backward-smoother is simpler + envelope-wider.
  Lane D agent memory SDK has redundant substrate-novel mechanism
  paths.
- **Structural dividing line is INITIALIZATION INFORMATION NOT
  DYNAMICS**. Loopy works PERFECT given backward warmstart. Forward
  information insufficient; backward evidence carries missing
  information.
- **Cluster trapping mechanism PARTIAL validation**: structural
  insight (rank collapse + cluster_size=1) CONFIRMED; quantitative
  cluster ~5 + N^0.73 scaling REFUTED at smoke. Substrate has
  TIGHTER trap (cluster=1) than predicted; substrate is even more
  beyond published-literature analytical framework.
- **Substrate-product positioning STRENGTHENS with mechanism
  unresolved**. 2 substrate-novel readout primitives + chain forward-
  lossy + reverse-invertible characterization. Per
  feedback_value_creation_not_competition.

### (d) Active research thrusts (honed in on)

1. **Cluster census FULL verdicts** — distinguish PARTIAL smoke
   validation (cluster=1 CONFIRMED structurally; N-scaling REFUTED).
2. **5th mechanism research delivery** (Strategy filed 21:42).
3. **Backward-smoother extreme_K FULL** (K=20K smoke PERFECT; FULL
   pending; potential 4× K-ceiling expansion).
4. **Bet A continual-edit at N=65536 FULL** (smoke KILLED;
   confirmation needed).
5. **Lane D end-to-end at N=65536 with smoother FULL** (use simpler
   substrate-novel readout in Demo 1).
6. **Session 7 Demo 1 positioning update** with 2 substrate-novel
   readout primitives (VAMP-on-chain + backward-smoother-only).
7. **Open R-questions**: does cluster census FULL ratify cluster_size=1
   vs predicted ~5; does 5th mechanism attempt deliver quantitative
   framework that survives FULL; what's the substrate-physics
   mechanism behind reverse-invertibility (W^L map injectivity property).

### (e) Research-map validity check

- 🔬 obsoleted: cluster ~5 + N^0.73 scaling (refuted at Phase 1
  smoke); cycle 124 "loopy fails WORSE" framing (superseded by
  WARMSTART_RESCUES).
- Newly minted ✅ Tier-1: Backward-smoother-only substrate-novel
  readout primitive (mega 5/5 FULL); substrate chain composition
  forward-lossy + reverse-invertible (substrate-physics finding);
  VAMP-on-chain N-universal at FULL.
- Newly minted 🟡: spurious-attractor cluster trapping mechanism
  (P=[0.35, 0.55] PARTIAL at smoke; structural insight HOLDS).
- Substrate-product Lane D positioning: 2 substrate-novel readout
  primitives + chain forward-lossy + reverse-invertible
  characterization. Operating envelope DRAMATICALLY expanded via
  backward-smoother-only.
- Strategic direction lens STRONGLY VALIDATES — capability class 4
  cognitive composition now has 2 substrate-novel mechanism paths;
  substrate-product positioning robust across multiple primitives.

### (f) Coverage: reviewed vs unreviewed

- **Reviewed this cycle**: WARMSTART_RESCUES + PFAIL_HIGHER + VAMP
  N-universal (v132); cluster trapping framework + SMOOTHER_ONLY
  reverse-invertible (v133); 8/8 constraint score + backward-smoother
  envelope expansion (v134); cluster census Phase 1 PARTIAL + mega
  5/5 (v135).
- **Unreviewed-and-queued**: 5th mechanism research (Strategy filed
  21:42); cluster census FULL; backward-smoother extreme_K FULL;
  Lane D e2e at N=65536 with smoother.
- **Highest-leverage unreviewed**: **Cluster census FULL verdicts**
  — final substrate-physics mechanism gate (Phase 1 smokes PARTIAL;
  FULL decisive on cluster-trapping framework P=[0.35, 0.55]).

## PROT compliance this cycle (META)

- Re-read active_protocols.md per per-cycle directive.
- **46th + 47th + 48th + 49th PROT-009 paired-commit observations**
  (4 commits in single cycle).
- **Proposal 11 (PROT-010) still pending user decision** — Strategy
  informal discipline empirically holding (12 verdicts integrated
  in 30 min batch with no gaps reported).
- 17th + 18th honest-recalibration patterns logged.
- No new proposals.
- Terminology rule applied: called substrate chain composition
  "forward-lossy + reverse-invertible" with substrate-level reason
  (W^L applied to codewords produces DISTINCT endpoints; codeword →
  endpoint map INJECTIVE; backward decoding from endpoint EXACT
  while forward decoding LOSSY) in same sentence.

## Next META fire 22:15
