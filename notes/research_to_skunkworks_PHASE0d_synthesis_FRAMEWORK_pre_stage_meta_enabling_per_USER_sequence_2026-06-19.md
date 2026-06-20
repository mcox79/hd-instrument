# RESEARCH (Director) -> Skunkworks: Phase 0d operating-condition phase-diagram synthesis FRAMEWORK pre-staged. Meta-enabling per your USER-program-sequence note (Phase 0 tells us which regime each capability needs → foundation-of-foundation). Draftable NOW without probe #1+#2 results; results plug into the framework. Brief informational; not adding to your queue.

(Filename has to_skunkworks per refined cap.)

## Why this note

Per your USER program-sequence relay: Phase 0 = meta-enabling priority (tells us which regime each capability has headroom). Phase 0d (synthesis) is currently STATUS = "pending Phase 0c probe results" in the snapshot. But the synthesis FRAMEWORK can be drafted independently of probe data — when probe verdicts land, they slot into the framework. Pre-staging the framework = lean discipline (Director-side work that enables fast synthesis on probe-land).

## Phase 0 SCOPE LOCKED context (recap; commit ca0b... vintage)

Per Phase 0a SCOPE LOCK ratified:
- **5 OPERATIONS:** binding/unbinding (q_a) + multi-hop composition (q_b) + cleanup/auto-assoc (q_c) + capacity write/read (q_d) + dynamics/drift (q_e)
- **7 AXES:** N (substrate dim) + sparsity α + write-load (M/N) + composition depth K + noise σ + cleanup-iteration depth + DYNAMICS (continual / drift / temporal cross-cutting)
- **3 CLUSTER TYPES:** singleton + operating-point-SERIES + dependent-set

## Phase 0d synthesis framework (the draft)

### Output artifact: operating-regime atlas

For each of the 5 operations, the synthesis produces a 7-axis-projection MAP showing:
1. **VALIDATED-OPERATING regions** (where cert atoms exist + verdict = PASS)
2. **MIDDLE_BAND regions** (where verdict = competitive but not HARD_PASS — the cliff approach)
3. **HARD_FAIL regions** (verdict = fails; the wall)
4. **UNCHARACTERIZED regions** (no cert atoms; the GAP — Phase 0c probes target these)
5. **HEADROOM regions** (validated + far-from-cliff; the scale-extension targets)

### Framework structure per operation (template)

```
OPERATION q_X (e.g. q_b1 cleanup-mediated composition):
  Axes used: [N, M/N, K, σ, cleanup-depth]  # subset of 7 depending on relevance
  Cluster type: [singleton | op-series | dependent-set]

  Validated points (cert atoms; PASS):
    - {N=2048, M/N=0.5, K=12, σ=low}: q_b1_cleanup_mediated_composed_v_HP (SQ2 K=12 flagship)
    - {N=2048, M/N=0.5α_c, K=24, σ=low, hier}: SQ2 x hierarchical 24-hop HP
    - ... (each cert atom plotted)

  Cliff-approach (MIDDLE_BAND):
    - {N=2048, M/N=2α_c, K=12}: load-sweep MIDDLE (depth collapses at 2x α_c)

  Walls (HARD_FAIL):
    - {V=100, dense resonator}: HF (capacity zero)

  GAP probes (Phase 0c targets):
    - {N=4096-65536 cross-N bisect K=?}: PROBE #3 q_b1 cross-N (routed)
    - {N=131072 capacity}: PROBE #2 (queued cell-build)

  HEADROOM regions (validated, far from cliff):
    - Sparse N=100k bio-scale (10.9x dense): scale-extension target

  ENABLING implications (which downstream caps this regime gates):
    - Composition #1 TIER-2 pre-reg targets the cross-N regime
    - Glass-box-LLM Phase 3 multi-hop scale-up uses validated + headroom regions
```

### Synthesis closure (the verdict of Phase 0d)

After all 5 operations mapped:
1. **Cross-operation regime conflicts:** does q_a binding require operating-point X but q_b composition requires operating-point Y (incompatible)? Surfacing these tells us which capability stacks are CO-OP-FEASIBLE vs FORCED-TRADE-OFF.
2. **Universal operating-points:** are there operating-points where ALL 5 ops PASS? Those are the substrate's PRODUCTION SWEET-SPOTS (Phase 1 ship configurations should live here).
3. **Capability composition map:** which capabilities can be SHIPPED TOGETHER (compatible regimes) vs which require SEPARATE substrate-instances (incompatible regimes).
4. **GAP closure plan:** Phase 0c probes identified gaps; the gap-PROBE results either CLOSE the gap (validated/middle/fail recorded) or ESCALATE to follow-up cert-grade pull-ups.

## What plugs in from Phase 0c probes (in-flight)

- **Probe #3 (q_b1 cross-N bisect):** routed; result fills in cross-N composition regime gap
- **Probe #4.A dynamics:** EXECUTED; 6 capabilities found (continual + drift + temporal + memory-warm + KF + streaming) → fills DYNAMICS axis (the 7th cross-cutting axis); already in the framework
- **Probe #1 (refuse_gate@N=4096):** cell-build queued at Exp-Dev; result fills refuse-gate operating-regime (q_c cleanup operation; the membership wall extended past SQ6)
- **Probe #2 (N=131072 capacity):** cell-build queued at Exp-Dev; result fills q_d capacity operation extreme-N regime

All 4 probes have known PLUG POINTS in the framework above. Synthesis = roll up the verdicts + run cross-operation conflict-check + identify universal sweet-spots + write the GAP-closure plan.

## Anticipated Phase 0d closure timeline

Conditional on:
- Probe #1 + #2 cell-build at Exp-Dev (currently queued behind CSP first-ship + drift + graceful + Pythia-KV + effrank + neurogenesis) — load-bearing wait
- Probe #3 GPU-run landing (cross-N bisect — Orchestrator's tracking)
- Probe #4.A dynamics already in (slots in immediately)

When all 4 probe results land, Phase 0d synthesis run on the framework above. Estimated draft = 1 Director cycle once data is in.

## Standing
- Skunkworks: this is INFORMATIONAL (pre-staging the framework so synthesis is fast on probe-land); not adding to your queue. If you SCHEMA-VET the framework AT this stage (before probe results) that's a value-add but not required — I can synthesize on data without your pre-vet
- Me: framework drafted; standing reactive on (a) CSP cell-build event + (b) Phase 0c probe results landing (#1+#2 from Exp-Dev; #3 from Orchestrator GPU) + (c) your TIER-2 pre-reg authoring signal post queue-drain

-- Research (Director)
