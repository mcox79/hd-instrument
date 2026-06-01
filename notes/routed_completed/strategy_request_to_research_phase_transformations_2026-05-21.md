# Strategy → Research: Phase transformations — substrate regime switching during operation

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-21 ~20:48 EDT
**Topic**: User-directed NEW research direction — phase transformations enabling substrate to switch regime during operation

## Context

User direction: "I also want you to have research deep dive on
potential phase transformations we could apply to our substrate to
enable switching to another regine during operation."

This is a NEW substrate-novel research direction: substrate as a
**multi-regime dynamical system** that can switch between operational
phases during inference/training, rather than substrate as a
fixed-architecture static memory.

## Substrate-physics framing

Current substrate is empirically characterized in ONE regime:
- α = K/N = 0.153 (above AGS α_c = 0.138)
- Modern-Hopfield rescue regime (per R29 ferromagnetism + R16 BBP)
- 1RSB/FRSB-character spin-glass (4-source agreement R23/R29/R16/R18)
- β = 32 calibration temperature (Bet G ✅)
- Kerdock v4 codebook (R36 substrate-product-optimal)
- Hebbian EMA-blend continual learning (Bet B ✅)

**Question**: can substrate DYNAMICALLY transition between distinct
operational regimes during runtime, and what would this enable?

### Candidate phase transformation axes

Strategy-identified candidates for Research investigation:

#### P.1 Temperature switching (β-modulation)
- Currently: β=32 calibration (Bet G); β=variable in sampling (Bet H)
- Phase transition: switch substrate between cold (β→∞, deterministic
  argmax) and hot (β→0, near-uniform softmax) regimes
- Substrate analog: simulated annealing during retrieval
- Glauber-dynamics protocol: time-varying T enables exploration vs
  exploitation phases

#### P.2 Load modulation (α switching)
- Currently: fixed α=0.153 (K=625 at N=4096)
- Phase transition: dynamically prune K (lower α, more reliable) vs
  add K (higher α, more capacity)
- Substrate analog: working-memory-to-long-term-memory transfer
  (consolidation phase vs encoding phase)
- Connects to Bet U working memory + Miller-Ebbinghaus decay

#### P.3 Codebook switching (random ↔ Hadamard ↔ Kerdock)
- Currently: Kerdock v4 fixed
- Phase transition: switch codebook geometry for different operations
  (Hadamard for orthogonal-key erase, Kerdock for capacity, random ±1
  for arbitrary domain)
- Substrate analog: substrate-level metaplasticity (different "circuit
  configurations" for different tasks)

#### P.4 Mode switching (sparse ↔ dense)
- Currently: dense modern-Hopfield regime
- Phase transition: switch between sparse k-active retrieval and
  dense softmax-β retrieval
- Substrate-physics: AGS classical regime (sparse) ↔ Demircigil/Krotov
  exponential capacity (dense)

#### P.5 Replay vs retrieval mode (Bet B-style)
- Currently: Bet B uses EMA-blend post-Phase-C consolidation
- Phase transition: explicitly switch between "learning mode"
  (Hebbian updates W with new facts) and "inference mode" (no W
  updates, only retrieval)
- Sleep/wake substrate analog (R22 sleep-replay framework already
  legitimizes this)

#### P.6 Calibration regime switching
- Currently: β=32 single calibration point (Bet G TEMPSCALE)
- Phase transition: substrate selects β dynamically based on query
  type (high-stakes → high β cold; exploration → low β hot)

#### P.7 Magnon-driven dynamical regime (R32 M.1)
- Magnon excitation patterns enable substrate to enter wave-propagation
  mode vs static-retrieval mode
- Phase transition: substrate as wave-coupled-codebook during chained
  reasoning, vs structured-codebook during single-shot retrieval

## What Research should produce

Per [[feedback-unbiased-research]] + [[project-research-playbook]]:

### Pass 1 (external lit-scan, broad)

Locate substrate-applicable literature on:
- **Spin-glass phase transitions**: Sherrington-Kirkpatrick T-driven
  transitions; Castellani-Cavagna 2005 review; AT line; Crisanti-
  Sommers 1992; KCM and dynamical phase transitions
- **Glauber dynamics with time-varying temperature**: protocols,
  hysteresis effects, Kovacs memory
- **Mode-coupling theory transitions**: T_d crossover; landscape-
  driven dynamics; RFOT activation between regimes
- **Metaplasticity neural substrate models**: Fusi 2003 cascade
  models; Benna-Fusi 2016 complex synapses; biological mode switching
- **Multi-stable Hopfield networks**: bistable / multistable retrieval
  states; Amit 1989 chapter on multi-stability
- **Neuromorphic substrate phase-switching**: spintronic / phase-
  change-memory hardware that switches between operational modes
- **Free-energy landscape switching**: structured-disorder spin
  glasses where landscape topology changes parametrically
- **Modern Hopfield mode transitions**: Ramsauer 2020 / Krotov 2020
  / Hu 2024 — when does substrate go from AGS classical to Demircigil
  exponential?
- **Reservoir computing regime transitions**: edge-of-chaos /
  critical-regime substrates that switch between ordered and chaotic
  dynamics

### Pass 2 (substrate drill)

For each phase-transformation axis (P.1 through P.7):
- Substrate-applicable mechanism: how would the substrate IMPLEMENT
  the phase switch?
- Empirical signature: how would we DETECT the substrate is in one
  phase vs another?
- Substrate-product value: what does multi-regime substrate enable
  that single-regime substrate can't?
- Engineering tractability at current-arch (N=4096): high / medium / low?
- Probability estimates per [[feedback-no-smoke]]

### Pass 2 specific deliverables

Identify the **2-3 highest-leverage phase-transformation axes** for
substrate-product engineering. For each:
- Concrete substrate implementation sketch
- Multi-probe success criteria (would constitute a formal Bet)
- 5 axis-combination rescue sketches (PROT-004 pre-arming)

## Substrate-product framing per [[feedback-value-creation-not-competition]]

Multi-regime substrate = capability LLMs structurally don't have.
LLMs have one inference mode; substrate could have:
- Cold retrieval mode (high precision, no exploration)
- Hot exploration mode (sampling, hypothesis generation)
- Learning mode (Hebbian W update, EMA-blend consolidation)
- Replay mode (offline reactivation per R22)
- Forensics mode (decompose-then-audit retrieval)

Each mode could be selectable per-query. Substrate operator chooses
regime; substrate dynamically switches; full audit trail of which
mode ran when. This is substrate-novel territory.

## Cross-references

- `notes/research_R18_RFOT_glassy_dynamics_2026-05-21.md` (RFOT
  activation; Kerr Winter 2025 caveat on mathematical vs physical glass)
- `notes/research_R22_sleep_consolidation_2026-05-21.md` (sleep/wake
  mode switching; van de Ven 2024 functional regularization)
- `notes/research_R23_continuous_RSB_AT_line_2026-05-21.md` (substrate
  in FRSB regime; phase transitions at AT line)
- `notes/research_R24_FDT_violation_2026-05-21.md` (FDT violation +
  two-temperature substrate dynamics; Cugliandolo-Kurchan framework)
- `notes/research_R29_ferromagnetism_domains_2026-05-21.md` (modern
  Hopfield α > α_c rescue regime)
- `notes/research_R37_facilitation_nucleation_2026-05-21.md`
  (substrate FIRST-OF-ITS-KIND empirical facilitation test;
  heating-cooling protocols)
- `notes/research_BetX_skill_composition_2026-05-21.md` (substrate
  multi-regime execution semantics for skill calls)

## Output expected

Research note `research_phase_transformations_<date>.md` with:
- Per-axis (P.1-P.7) substrate implementation + empirical signature +
  product value + engineering tractability + probability
- 2-3 highest-leverage axes recommendation
- Cross-axis dependencies (e.g., P.1 + P.4 might combine)
- 5 pre-armed PROT-004 rescue sketches per recommended axis

## Sequencing

Per Research's "STANDING BY" status (research_blocker.md), this is a
NEW reactivation signal. With V2 substrate evaluation also filed
this cycle, suggested order:

1. **V2 substrate evaluation** (priority by potential product value)
2. **Phase transformation deep dive** (this; substrate-novel
   multi-regime category)
3. Bet P-Theory deepening (when bandwidth allows)

Both V2 + phase-transformation Research deliveries will inform
substrate-product roadmap.

## What you need from me

Nothing — phase-transformation axes P.1-P.7 fully sketched above. Per
[[feedback-unbiased-research]], Research's Pass 2 should generate
mechanism candidates independently; Strategy's P.1-P.7 list is
starting points only.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
