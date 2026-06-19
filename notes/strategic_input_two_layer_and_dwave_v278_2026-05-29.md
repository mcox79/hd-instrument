# Strategic input integration: two-layer architecture + D-Wave analog (v278)

User delivered substantial strategic input during the research surge. Two complementary frames that both shift exploration direction:

## Frame 1: Two-layer architecture

Substrate has two computational layers:
- **Internal layer** — continuous; rich physics; spectral, entropy, Lyapunov, free-probability all live here
- **Operational layer** — discrete; argmax-dominated; this is where KF-roster, deletion-cert, edit-isolation live

Four operational-layer-invariance witnesses confirm the separation:
- PB-3 critical-slowing exists internally, flat tau operationally
- Axis-4 trajectories exist internally, zero hysteresis operationally
- KF-5 entropy beta-steerable internally, bpc invariant operationally
- BE-1 W-magnitudes vary 32x internally, max_iso identical FP32->INT1

**Three exploration directions emerge** (with most-explored to least):
- Direction A: Operational-layer capabilities (mostly explored)
- Direction B: Internal-layer capabilities (almost entirely unexplored)
- Direction C: Two-layer-coupling capabilities (entirely unexplored)

## Frame 2: D-Wave classical analog

Substrate is structurally the **classical version of adiabatic quantum computation**:
- Energy landscape with multiple basins (W defines retrieval landscape ~ D-Wave Hamiltonian)
- Adiabatic-like dynamics (retrieval rolls toward basin ~ D-Wave annealing)
- Operating-temperature parameter (beta ~ annealing temperature)
- Phase structure (substrate's two-orthogonal-boundary lattice ~ D-Wave gapped/gapless phases)
- Disorder is the substrate of computation (SKAH-M/lR-phase ~ D-Wave spin glass)

**Key differences are FEATURES, not bugs**:
- No tunneling: substrate IS classical, runs on standard hardware
- No entanglement: provable isolation possible (KF-3 multi-substrate) -- quantum systems literally cannot have this
- Deterministic readout: auditable; quantum systems can't

**Positioning shift**: substrate is what D-Wave promised but in shippable classical form with audit primitives. Every D-Wave customer evaluation is a potential substrate customer with pre-existing market education.

## Three quantum-inspired experiments emerge

- **QE-1 Substrate annealing during retrieval** -- beta-annealing schedule (~1 GPU day; smoke scaffolded by Agent C)
- **QE-2 Coherent multi-hop** -- propagate distributions through multi-step ops without intermediate argmax (~1 week eng + 2 GPU days; deep research by Agent A; **single most important quantum-inspired capability** per user; could rescue d=25-50 multi-hop cliff = substrate's biggest weakness vs transformers)
- **QE-3 Syndrome-based error correction** -- Kerdock parity-check active correction (~3-5d eng + 1 GPU day; smoke scaffolded by Agent C)

## Alignment check: what we already shipped that satisfies the new framing

| User's call | Already in queue / done |
|---|---|
| Spectral readout probe FIRST | YES -- `kf45_pre_argmax_joint_probe_v1_n4096` in GPU queue (shipped this turn via exp_dev) |
| Bet B architectural rescue chain | YES -- 3 anchors shipped (TP-HDC / generative replay / MoE-DG-gating) |
| Operating-point basin map | YES -- 1 CPU anchor shipped |
| Cap_map corrections (Saad-Solla overclaim + KF-2 BE-1 floor) | YES -- v278 pushed at 24340d5 |

## What's running now (background agents)

- Coherent multi-hop QE-2 deep research (Opus) -- highest-leverage new direction
- D-Wave classical analog full landscape research (Opus) -- positioning + capability inventory
- QE-1 + QE-3 scaffolding (Opus) -- two cheap quantum-inspired experiments ready to ship

## Recommended next-session pickup

1. When Agent A returns: ship coherent multi-hop QE-2 experiments (potentially game-changing for multi-hop)
2. When Agent B returns: integrate D-Wave-for-classical positioning into product narrative
3. When Agent C returns: push QE-1 + QE-3 scripts, ship anchors
4. Internal-layer capability development: build out Phase 2 (Lyapunov regime classifier, free-probability moments, pre-argmax distribution API)
5. Two-layer coupling capability (Direction C) experiments after Direction B validates

## Honest meta-observation

The substrate's true character is now characterized clearly enough that:
- (a) Direction B (internal-layer readouts) is the highest-payoff unexplored space
- (b) Direction C (two-layer coupling) gives substrate capabilities NO other architecture has
- (c) D-Wave positioning gives substrate a pre-educated market segment without quantum hardware overhead
- (d) Coherent multi-hop is the path to convert substrate's biggest weakness (d=25 cliff) into a competitive strength

The cap_map should likely add a row for "two-layer architecture characterization" as evidence accumulates. Not yet -- waiting for Agent A/B/C returns + first verdicts on the 5 priority anchors.
