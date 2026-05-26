# Research field-scope update — 2026-05-24

**Trigger:** user field-yield analysis (2026-05-24).

**Decision:** stop drilling materials/algebraic-topo/inference/quantum-info (saturated/closed). Drill MORE in the top-yielding regimes (thermodynamics, spin-glass, modern-Hopfield, semiconductor). ADD 8 new adjacent fields.

---

## Status changes (in `tools/orchestrator/agents/research.md`)

### Confirmed DROPPED (Tier-3 DO NOT DRILL — unchanged but reaffirmed)

| Field | Reason |
|---|---|
| `algebraic-topo` | Pattern 4 closure (infinite-dim trivializes); 0% yield, 11 drills already |
| `quantum-info` | Harlow theorem closure; 0% yield |
| `inference` | 10% yield; only adjacent to AMP/VAMP candidates |
| `materials-physics` | 31% yield over 16 drills — OVER-DRILLED; only drill ADJACENT (TAP, C_ij eigenvalue, chi_3, FDT-violation) |

### Drill MORE (Tier-1 reaffirmed; modern-hopfield added to table)

- `thermodynamics` (71%, 7 drills) — Jarzynski / Hatano-Sasa / Maes-Netocny / Esposito-Van den Broeck
- `spin-glass` (83%, 6 drills) — 1-RSB / full-RSB ultrametric / cavity / Plefka
- `semiconductor` (100%, 2 drills) — DLTS K-pulse / RTN dwell-time / pn-junction rectifier
- `free-probability` (100%, 1 drill) — Marchenko-Pastur / Tracy-Widom / R-transform / S-transform
- `modern-hopfield` (fruit-bearing) — Krotov/Hopfield-86 generalizations / dense exponential capacity / energy-landscape

### 8 NEW fields added 2026-05-24 (Tier-1b, drill PRIORITY when adjacency edge surfaces)

| New field | Adjacent parent(s) | Substrate question |
|---|---|---|
| `nonequilibrium-stat-mech` | thermodynamics | Jarzynski / Crooks / NESS — Bet B PAC-Bayes floor IS a fluctuation theorem |
| `mesoscopic-transport` | semiconductor, thermodynamics | Landauer-Buttiker — multi-hop d=25 cliff = transport problem |
| `structural-glasses-MCT` | spin-glass, thermodynamics | Mode-coupling theory dynamics — replay + Phase-A/B = MCT relaxation? |
| `percolation-critical-phenomena` | spin-glass, semiconductor | K/N=0.56 cliff, sigma=16, d=25, M_c are percolation-class observables |
| `random-matrix-theory-beyond-free-prob` | free-probability | Tracy-Widom edge / Dyson Brownian / level spacing — microscopic spectral statistics |
| `network-science-graph-theory` | spin-glass, free-probability | Pool retrieval = graph problem; spectral-gap / expander bounds |
| `sparse-coding-compressed-sensing` | free-probability, AMP/VAMP | PPMI direct analog; L1/LASSO phase transitions parallel capacity cliffs |
| `population-genetics-wright-fisher` | thermodynamics (drift-diffusion) | Continual learning = mutation+selection+drift; Wright-Fisher fixation probability |

---

## Rationale

User observation (paraphrased): the top-yielding fields are thermodynamics, spin-glass, modern-Hopfield, semiconductor. Stop redrilling exhausted ones; expand the search RADIUS by adding 8 ADJACENT high-prior fields that were absent from the scope.

Per [[feedback-dont-dismiss-adjacent-methods]] — premature dismissal is the dominant failure mode; the 8 new fields explicitly avoid that by mapping each to a concrete substrate question rather than abstract framings.

Per [[feedback-periodic-scope-expansion]] — cross-framework drills periodically expand search radius; this is the formal addition of those frameworks to the advisor's tier-1b table.

Per [[feedback-lit-scan-calibration-penalty]] — when drilling these new fields, deflate agent P estimates by 0.15-0.25 (uncharted regime for substrate); cap novel-synthesis P at 0.50; always include hard-fail thresholds.

---

## Operational impact

- `tools/orchestrator/agents/research.md` Tier-1 / Tier-1b tables updated.
- `tools/orchestrator/research_field_advisor.py` — no code change needed; the heuristic is `tier_score - cost - saturation + scope_bonus`; new fields will be picked up automatically once the parser reads them from `notes/research_meta_map_and_adjacencies_*.md` and a candidate row exists. Until then they enter via direct anchor mention in routing notes.
- Next 5 research dispatches should bias toward Tier-1 + Tier-1b candidates per the new list.

---

## Filed by

Orchestrator main thread, 2026-05-24, in response to user task batch (Tasks 1-4 multi-coupled cycle).
