# Grounding Anchor Design + First Testbed Decision — 2026-07-10 (Director)

**Purpose:** decide, concretely, WHAT our ground truth is and design the first grounding experiment. Grounding is now central: the consolidation engine (normalized-Laplacian diffusion-with-restart, cell a519) needs EXTERIOR fuel, and grounding gates inductive inference (proven: code-format alone can't; 5 converging negatives). This is the director's decision, not a dispatch.

## The principle, operationalized

Grounding = **agreement between GENUINELY-INDEPENDENT channels + a VERIFIABLE ORACLE that can SURPRISE.** The ball looks soft (channel A: vision/shape) but squeezes hard (channel B: touch/measured) -> the SURPRISE pins the meaning, and "hard" is a real exterior fact the system can be WRONG about. Two requirements fall out:
1. At least two channels that are NOT derivable from each other (or agreement just re-derives shared bias -- the trap).
2. At least one channel that PUSHES BACK -- a verifiable/measured truth, so a prediction can be checked and be wrong (the surprise = the grounding event, and the only thing that breaks a shared-bias fixed point, per the whole arc).

## The decision: first testbed = a small closed domain with independent RELATIONAL + EMPIRICAL-NUMERIC channels + a lawful oracle

**Chosen first testbed: the periodic table of elements** (fallback/parallel: a physical-object set with measured hardness/density/mass -- the literal ball/rock case). Rationale -- it is the cleanest possible mechanism test because it has, in one small self-contained domain:
- **Channel A (relational/structural):** group, period, bonds-with, same-family. A graph -- exactly our substrate's native form.
- **Channel B (empirical/numeric, EXTERIOR):** measured atomic mass, electronegativity, atomic radius, ionization energy, melting point. These are MEASURED FACTS not derivable from the relational graph -- a genuine exterior referent, still self-contained (data, not a borrowed model).
- **The channels genuinely AGREE without being derivable from each other:** group-neighbors have similar measured properties. That agreement IS the grounding signal (correlated-but-not-derivable = exactly the regime grounding needs).
- **A VERIFIABLE ORACLE (the push-back):** periodic law -- properties trend LAWFULLY across periods/down groups. Predict a held-out element's property from its neighbors, check against the TRUE measured value -> the system can be surprised. This is the "predict-and-check-against-exterior-truth" that no purely-symbolic loop can fake.
- **Small enough for a smoke** (~118 elements, ~thousands of relations+properties), **and** "combine to a meaningful location" is directly testable (interpolate a held-out element's properties/position from its neighbors).

Why NOT start on the messy 222k-triple bio KB: we do not yet know if it HAS a genuinely-independent, verifiable second channel. The mechanism must be proven where the two-channel structure is clean and the oracle is lawful, THEN scaled to real ingest. (Scope flag: this proves the GROUNDING MECHANISM; transfer to the messy KB is a separate, later step -- do not conflate, per the synthetic-CG-doesn't-transfer scour lesson.)

## The experiment (mechanism test; exp_dev designs parameters)

Does anchoring the consolidation geometry to CROSS-CHANNEL AGREEMENT (relational A + measured-numeric B) produce a geometry that:
1. **Is degree-invariant** (reuse the retest's degree strata -- rare elements as well-placed as common ones);
2. **Infers held-out facts** -- predict a held-out element's numeric property AND relational position from its consolidated neighbors, MEASURED not assumed (composition-lands-meaningfully);
3. **Is confirmed by the verifiable oracle** -- the predicted property matches the TRUE measured value beyond a mean/degree baseline (the exterior check).

**THE DECISIVE DISCRIMINATOR (grounding = exogenous referent, operationalized):** the EXTERIOR channel must be LOAD-BEARING. ABLATE the numeric channel B (consolidate on the relational graph A alone) -> grounding MUST COLLAPSE (property prediction drops to the mean/degree baseline). If A-alone grounds as well as A+B, then B was not doing exterior work and we have NOT grounded -- we have re-organized internal symbols (the exact failure the arc warns about). HARD_PASS(grounding-real) = A+B beats A-alone AND beats degree/mean baseline AND the oracle confirms AND it is degree-invariant AND channel-independence pre-flight cleared. HARD_FAIL = A-alone ties A+B (no exogenous work) OR oracle-check at chance OR tail-collapses.

## Honest risks (name them before building)

1. **Channel independence is partial, not total.** Group-neighbors ARE similar in properties -- that is the grounding signal, but it means A and B are CORRELATED (not independent). The claim is "B is not DERIVABLE from A" (you cannot compute electronegativity from the bond-graph alone), which is weaker than statistical independence. The pre-flight probe must measure BOTH channels' degree-correlation and their mutual predictability, and the win only counts if B adds exterior information A lacks (measured by the ablation above, which is the real test regardless of the independence subtlety).
2. **The oracle could leak.** If the held-out element's neighbors trivially determine its property (periodic law is very smooth), the "inference" is near-trivial. Guard: hold out HARDER cases (isolated elements, period-boundary cases) and report the difficulty-stratified result, not just the easy interior.
3. **Small-clean-domain -> messy-KB transfer is unproven.** This proves the mechanism; it does not prove grounding scales to real ingest. Explicit scope.
4. **This is grounding via INGESTED measurements (borrowed/layer-2), not active intervention (layer-3).** It is a real exterior referent but a PASSIVE one. The arc's deeper finding was that full grounding may need ACTIVE sampling (Held-Hein). This testbed is the passive-exterior rung; the active rung (a toy world the substrate acts in / a verifiable executable oracle it queries) is the next step if this passes. Do not overclaim this as full grounding.

## Sequencing

Build order: (1) consolidation ENGINE validates first (cell a519 -- does diffusion-with-restart give degree-invariant geometry at all); (2) THEN this grounding cell builds ON the validated engine (the engine is the mechanism, the exterior channel is the fuel). If the engine smoke is clean, this grounding cell is the immediate next dispatch. If the engine fails, fix the engine before adding the exterior channel -- do not confound an engine failure with a grounding failure.

## The verifiable-oracle escalation (the strongest ground truth, queued)

After the passive-exterior rung: the strongest grounding is an EXECUTABLE oracle the substrate can ACTIVELY query and be wrong about -- arithmetic/logic (we have the dual-number bake-in toehold), code execution, or a tiny physics/grid world. That is the layer-3 active-intervention rung and the truest grounding. Periodic-table = the clean first proof; executable oracle = the deep target.
