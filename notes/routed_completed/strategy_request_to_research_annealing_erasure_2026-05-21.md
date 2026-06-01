# Strategy → Research: Annealing-based erasure for substrate (substrate-novel forensics-resistant erase mechanism)

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-21 ~22:00 EDT
**Topic**: User-directed NEW research direction — thermal/annealing-based erasure as alternative to current Bet 2/C anti-Hebbian rank-1 erase

## Context

User direction (cycle 78 chat): "or annealing for erasing data?"

Current substrate erase primitive is **Bet 2/C** (✅ validated) — anti-
Hebbian rank-1 W subtraction + pool removal; Mirage-grade across all 5
probes; works at M/N ≤ 0.78 (Hadamard subcode) or M/N ≤ 8 (Kerdock v4).
**Surgical, deterministic, requires knowing the value to subtract**,
leaves a rank-1 anti-Hebbian structural trace in W.

**Proposed alternative**: thermal annealing-style erasure. Heat
substrate locally (raise effective T or β around target atoms) to
"melt" their W contributions; cool back to equilibrium. Other stored
facts preserved by surrounding cool regions.

**Why substrate-novel**: literature on thermal erasure in AM-class
systems is essentially absent. Closest analogs:
- HAMR (heat-assisted magnetic recording) in physical media — heat
  to lower coercivity, then write; substrate has Hebbian-only no
  coercivity but conceptual parallel
- Spin-glass quench protocols (Janus collaboration aging)
- Curie-temperature randomization in magnetic media
- None applied to associative-memory erasure as a substrate-product
  primitive

## What Research should investigate

### Pass 1 (external lit-scan, broad)

Per [[feedback-unbiased-research]] + [[feedback-query-privacy-decomposition]]:

Locate substrate-applicable literature on:

**Thermal erasure mechanisms (hardware)**:
- HAMR (heat-assisted magnetic recording) — Plumer-Weller series; coercivity-vs-T
- Curie-temperature randomization protocols in magnetic data storage
- Thermal degaussing / bulk-erase media-level protocols

**Thermal forgetting / annealing in spin-glass / AM systems**:
- Glauber-dynamics protocols with target-region temperature scheduling
- Quench / annealing protocols and which substrate-state aspects survive
- Two-temperature systems (Cugliandolo-Kurchan FDT-violation framework
  per R24) — does region-specific T-bias drive selective forgetting?
- Spin-glass aging / Kovacs protocols and what they erase vs preserve
- Modern Hopfield thermal protocols — does β-modulation provide
  selective forgetting mechanism?

**Classical machine unlearning literature** (where it overlaps with
thermal):
- Machine unlearning via noise injection + retraining
- Privacy-preserving forgetting in differential privacy frameworks
- Verifiable / certified unlearning (vs Bet 2/C's Mirage-probe-based)

**Connection to substrate's existing frameworks**:
- R18 RFOT — substrate is in mixed 1RSB+FRSB regime; activated dynamics
  give thermal mechanism for state transitions
- R24 FDT violation + two-temperature substrate — natural framework
- R37 F.1 heating-cooling protocols — substrate Glauber-T machinery
  already designed
- R22 sleep-replay (cycle 53 v70) — uses temperature-like protocols for
  consolidation; reverse direction = thermal forgetting

### Pass 2 (substrate drill)

For substrate-applicable mechanism:

1. **Mechanism design**: how does substrate implement region-specific
   heating? Options:
   - Local β-reduction in W-rows corresponding to target atoms (Glauber
     analog)
   - Add noise (Gaussian δ) to target W-rows then re-equilibrate
   - Quench protocol: warm whole substrate, cool selectively (target
     stays warm longer)
   - Hybrid: identify target via Mirage-probe-style query + apply
     thermal-perturbation

2. **Empirical signature**: how would we detect that thermal erasure
   worked AND that the structural trace is gone (vs Bet 2/C's
   anti-Hebbian rank-1 signature)?
   - Standard 5 Mirage probes (must pass like Bet 2/C)
   - Bet 3 charge-flipping forensics — can we read back the erased fact
     from W after thermal erase?
   - Walsh-Hadamard peak forensics — does WHT show residual peak at the
     erased atom?

3. **Substrate-product gain over Bet 2/C**:
   - **Forensics-resistance**: can thermal erase leave NO structural trace
     where anti-Hebbian leaves rank-1?
   - **Blind erasure**: works without knowing value (just location/index)?
   - **Soft erase / data minimization**: tunable rate for GDPR
     "minimize storage" not just "delete"?
   - **Bulk erasure efficiency**: erase N facts in one pass vs N
     anti-Hebbian operations?

4. **Substrate-shipping probability** (per [[feedback-no-smoke]]):
   - P(thermal mechanism preserves Mirage-grade pass): ?
   - P(differential value over Bet 2/C anti-Hebbian on ≥1 axis): ?
   - P(forensics-resistance gain materializes): ?
   - P(any substrate-applicable Pass-2 mechanism design): ?

## Expected output

Research note `research_annealing_erasure_<date>.md` with:

- Pass 1 lit synthesis (substrate-applicable references; honest gaps)
- Pass 2 mechanism design (1-3 substrate-compatible mechanisms)
- Per-mechanism gain/loss table vs Bet 2/C anti-Hebbian:
  - Mirage-grade pass probability
  - Forensics signature comparison
  - Blind erasure capability
  - Soft/partial erasure capability
  - Bulk erasure efficiency
  - Compatibility with existing primitives (Bet A edit, Bet C capacity)
- 5 pre-armed PROT-004 rescue sketches per recommended mechanism
- Substrate-product framing per [[feedback-value-creation-not-competition]]:
  what does annealing erasure give substrate over LLM unlearning + over
  current Bet 2/C?
- Lane mapping: Lane C compliance primary; Lane E neuromorphic secondary

## Per [[feedback-no-papers-product-only]]

Frame as substrate-product engineering choice: "additional substrate
erasure mode for forensics-resistance / soft-erase / blind-erase /
bulk-erase use cases" — NOT "novel thermal-erasure framework paper."

## Lane mapping

- **Lane C compliance** (primary): additional erasure mode with
  potential forensics-resistance + GDPR data-minimization mode →
  differential Lane C value proposition
- **Lane E neuromorphic** (secondary): thermal protocols are natural
  on analog/spintronic substrates; HAMR-class hardware compatibility
- Lane A memory layer: marginal (current Bet 2/C already serves)
- Lane B/D/F: marginal

## Sequencing recommendation

Per `notes/research_blocker.md` Research standing by since 21:33;
Research backlog after current cycle:

1. **V2 substrate evaluation deepening** (R36 already partial; further
   sandwich-bound refinement could surface)
2. **Annealing-erasure investigation** (this request; substrate-novel)
3. R27 light-matter / R21 cross-modal / R34 V2 hyperbolic (backlog)

Annealing-erasure is Phase 2+ priority (Lane C feature breadth).
Could combine with R37 F.1 heating-cooling research (same Glauber-T
machinery).

## Cross-references

- `notes/substrate_capability_map.md` Bet 2 + Bet C (current erase ✅)
- `notes/research_R18_RFOT_glassy_dynamics_2026-05-21.md` (substrate
  glass-dynamics framework)
- `notes/research_R24_FDT_violation_2026-05-21.md` (two-temperature
  substrate)
- `notes/research_R37_facilitation_nucleation_2026-05-21.md` (F.1
  heating-cooling protocol; same machinery)
- `notes/research_R22_sleep_consolidation_2026-05-21.md` (temperature
  protocols for consolidation; reverse direction)
- `notes/strategy_research_angles_inventory_2026-05-21.md` (research
  backlog)

## What you need from me

Nothing — substrate-physics anchors fully specified above. Per
[[feedback-unbiased-research]], Research's Pass 2 should generate
mechanism candidates independently; the 4 mechanism-design options
above are starting points only.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
