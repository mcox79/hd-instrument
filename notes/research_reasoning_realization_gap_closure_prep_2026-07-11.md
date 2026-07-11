# Research: Closing the Reasoning-Realization Gap (geom ~0.23 vs freq ~0.17 vs ceiling ~0.42) — outcome-independent prep

Date: 2026-07-11. Self-contained drill (4 parallel Sonnet lit-scan sub-agents dispatched for breadth, this
thread synthesizes). Directly extends `notes/research_course_c_map_builder_replay_consolidation_design_2026-07-10.md`
(map-builder design), `notes/research_knowledge_density_information_ceiling_relational_inference_2026-07-10.md`
(density floor), `notes/cskg_commonsense_core_kcore_density_gate_2026-07-10.md` (CSKG density gate, PASS),
`notes/convergence_architecture_grounding_is_the_verifier_2026-07-10.md` (verifier architecture),
`notes/research_resonator_reachability_ceiling_2026-07-07.md` and
`notes/research_resonator_decode_capacity_ceiling_crux_v2_2026-07-10.md` (readout/cleanup precision).
Written BEFORE the decisive CSKG map-builder run lands — usable whether that run is a modest WIN or a NEAR-MISS.

**Coordinator sharpening (mid-drill, addressed explicitly below):** the note must (1) document the actual
historical KGE middling->SOTA benchmark deltas so "closing the gap" is calibrated against a real track
record, not vibes; (2) tag every lever GLASS-BOX-PORTABLE vs REQUIRES-OPAQUE and report the honest ceiling
for the glass-box-only subset; (3) flag which levers are NEWER-GROUND (our differentiator, thin prior art)
vs BORROWED-KNOWN (de-risked toolkit). All three are covered in dedicated sections below.

---

## HEADLINE (4-line + calibration note)

1. **The KGE middling->SOTA climb is a well-documented, mostly BORROWED-KNOWN, mostly GLASS-BOX-PORTABLE
   climb — and training-recipe tuning alone (loss function, negative sampling, regularization) has
   historically bought MORE than a full architecture generation.** Ruffinelli et al. 2020 ("You CAN Teach an
   Old Dog New Tricks") retuned 2011-2018-vintage models with no architecture change and got RESCAL from
   0.270->0.357 MRR (+32% relative) on FB15k-237 — beating RotatE (0.338) outright — purely via loss-function
   choice, reciprocal-relations reformulation, and regularization. TransE->RotatE (the "add rotation"
   architectural jump) bought +0.044 MRR / +0.068 Hits@10 (+15%/+15% relative); loss-function tuning ALONE
   (holding architecture fixed) bought comparable or larger absolute gains. **This is the single most
   load-bearing, calibrating fact in this drill: a large fraction of "closing the gap" is proven,
   de-risked, nearly-free training-recipe work, not novel mechanism design.**
2. **The remaining opaque-GNN-vs-glass-box gap is real but modest in the regime that matters for us
   (transductive, known-entity-pair completion): ~4-5 Hits@10/MRR points (~7-12% relative)** — best glass-box
   tuned/ensembled (ComplEx-N3 / ComplEx+RP, ~0.37-0.39 MRR) vs. best opaque GNN (NBFNet, 0.415 MRR). A 2024
   paper (arXiv:2412.05114) further argues **~50% of even that residual gap is GNNs exploiting
   benchmark-construction artifacts (negative-pattern leakage from standard preprocessing), not a proven
   architectural-expressiveness wall** — no clean no-free-lunch/expressiveness proof exists showing static
   geometric embeddings *cannot* reach GNN-tier scores on transductive completion. **The honest glass-box
   ceiling for our task class is high — roughly 90-95% of opaque SOTA — not a small fraction of it.**
3. **CALIBRATION WARNING (the humbling part):** external Hits@10 numbers run 0.42 (untuned TransE) to 0.60
   (NBFNet) on FB15k-237 — a 1-hop, denser (avg-deg ~37), larger-entity-count (14,541) benchmark. Our own
   declared **ceiling (0.42) sits at almost exactly untuned-TransE's raw Hits@10 (0.465)**, and our task is
   **genuine-L2 (2-hop) held-out inference**, strictly harder than the 1-hop completion task every external
   number above measures. This is NOT an apples-to-apples benchmark match (flagged honestly, not asserted
   as either good or bad news) — but it means: **do not expect "closing the gap to ceiling" to land us in
   NBFNet-tier absolute territory.** The ceiling itself is architecturally consistent with a "TransE-tier"
   absolute band for a harder (2-hop) task on a comparable-density graph, which is a coherent, honest place
   for a 2-hop reasoning ceiling to sit. Reaching it is still the correct, ambitious, well-motivated target —
   it is just not "SOTA" in the external-benchmark sense, and should never be marketed as such.
4. **The single highest-leverage FIRST optimization to run the moment the decisive result lands is the SAME
   move whether it's a WIN or a NEAR-MISS: re-fit whichever arm produced the geom number with the
   BORROWED-KNOWN training-recipe trio (correct loss function + self-adversarial negative sampling + N3/L3
   regularization) BEFORE touching architecture or attempting replay-consolidation.** This is cheap (no new
   design, hours not days), well-precedented (Section 2), and directly falsifiable: if it materially moves
   the geom number, the "gap" was partly a training-recipe artifact, exactly Ruffinelli's finding replicated
   on our own arm — cheapest possible test of the most commonly-confounded variable in this literature.

**Deflated P estimates** (per-lever, see Section 3 table): borrowed-known glass-box training-recipe levers
carry **P 0.55-0.70** (well-precedented externally, deflated only for lack of on-substrate-exact-combination
precedent — NOT capped at the novel-synthesis 0.50 ceiling since these are not novel syntheses, they are
direct ports of externally-proven techniques). Newer-ground levers (replay-consolidation depth, grid-code
multi-module precision, sequential phase-coded readout) remain capped at **P<=0.50** per discipline, several
lower (0.20-0.35) reflecting genuinely thin or absent direct precedent — see Section 4.

---

## Part 1 — Track record: the actual KGE middling->SOTA deltas (FB15k-237, filtered, standard 1-hop link prediction)

All numbers below verified this cycle via WebSearch/WebFetch against primary sources (RotatE paper Table 5/7/13,
Ruffinelli et al. Table 2/3, Lacroix et al. Table 2, TuckER paper, NBFNet repo README, A*Net paper, Zhu et al.
RED-GNN/AdaProp, arXiv:2110.02834). Standard caveat: TransE (2013) predates FB15k-237 (introduced 2015); all
"TransE on FB15k-237" numbers are later re-implementations.

| Method | MRR | Hits@10 | Class | Delta vs prior |
|---|---|---|---|---|
| TransE (re-impl., untuned) | 0.294 | 0.465 | glass-box | baseline |
| DistMult (untuned) | 0.241 | 0.419 | glass-box | -0.053 / -0.046 vs TransE |
| ComplEx (untuned) | 0.247 | 0.428 | glass-box | roughly flat vs DistMult |
| ConvE | 0.325 | 0.501 | opaque (small CNN) | +0.031/+0.036 vs TransE |
| **RotatE** (architecture: rotation) | 0.338 | 0.533 | glass-box | +0.044/+0.068 vs TransE (+15%/+15% rel) |
| RESCAL (Ruffinelli-tuned, NO arch. change) | 0.357 | 0.541 | glass-box | +0.087 abs MRR vs untuned RESCAL 0.270 (**+32% rel**) |
| ComplEx (Ruffinelli-tuned, NO arch. change) | 0.348 | 0.536 | glass-box | +0.101 abs MRR vs untuned 0.247 (**+41% rel**) |
| DistMult (Ruffinelli-tuned, NO arch. change) | 0.343 | 0.531 | glass-box | +0.102 abs MRR (**+42% rel**) |
| ComplEx-N3 (Lacroix reg.) | ~0.37 | ~0.56 | glass-box | +0.02-0.03 abs MRR vs plain tuned ComplEx |
| TuckER | 0.358 | 0.544 | glass-box | comparable to ComplEx-N3 |
| ComplEx+RP (aux. relation-prediction objective) | 0.388-0.393 | 0.568 | glass-box | best pure glass-box number found |
| RED-GNN | 0.374 | 0.558 | opaque (GNN) | below ComplEx-N3 on MRR |
| AdaProp | 0.392 | 0.555 | opaque (GNN) | roughly tied w/ ComplEx+RP |
| **NBFNet** | 0.415 | 0.599 | opaque (GNN) | +0.022-0.045 abs MRR vs best glass-box (**+6-12% rel**) |
| A*Net | ~0.411 | ~0.586 | opaque (GNN, pruned) | -0.004/-0.013 vs NBFNet (efficiency trade, not accuracy gain) |

**Reading this table for "how much of the climb is proven and usable":**
- TransE(untuned) -> RotatE (the architectural jump most people picture as "the improvement"): **+15% relative Hits@10.**
- ComplEx(untuned) -> ComplEx(Ruffinelli-tuned), architecture UNCHANGED: **+25% relative Hits@10** — bigger
  than the architectural jump above, for a training-recipe fix alone.
- Best glass-box (ComplEx+RP, 0.568 H@10) -> best opaque (NBFNet, 0.599 H@10): **+5.5% relative** — the
  remaining gap after both architecture AND training recipe are maxed out on the glass-box side.
- The `arXiv:2412.05114` "negative pattern" paper estimates roughly HALF of even that last 5.5% gap is
  benchmark-construction artifact (a specific "Remove-One-Hop" preprocessing quirk GNNs implicitly exploit),
  not a proven expressiveness wall — treat this as a single-paper, not-yet-broadly-replicated finding,
  flagged as thin evidence, but directionally consistent with "the glass-box ceiling is closer than the raw
  numbers suggest."

**Inductive setting (closer to our "never directly told" framing) — a categorical, not incremental, gap:**
static embedding methods (TransE/RotatE/ComplEx/TuckER) **cannot run at all** on held-out-entity inductive
benchmarks (no mechanism to embed a never-seen entity) — this is a hard structural exclusion, not a lower
score. The real inductive comparison is GNN/path methods vs. RULE-BASED methods (RuleN, GraIL): GraIL beat
RuleN by +2.2 to +10.9 Hits@10 points depending on dataset (Teru et al. 2020) — a real, dataset-dependent
margin that does NOT categorically exclude rule/structure-based reasoning the way pure embeddings are
excluded. **This directly supports the substrate's already-chosen design (FPE/SSP continuous entity coding +
generate-and-test hard verifier, not a frozen embedding table) — it is in the right family (structure-aware,
not table-lookup) to avoid the categorical inductive exclusion.**

---

## Part 2 — Glass-box portability matrix (every lever tagged)

| Lever | Tag | Evidence-grade gain | Newer-ground or borrowed-known |
|---|---|---|---|
| Rotation-in-embedding-space scoring (RotatE-equiv., already our FHRR primitive) | GLASS-BOX | +15% rel Hits@10 vs TransE | BORROWED-KNOWN, already adopted (Course C design) |
| **Loss-function choice (cross-entropy vs margin/BCE)** | GLASS-BOX | up to +25-41% rel MRR, architecture-independent | BORROWED-KNOWN, cheapest, highest-leverage, NOT YET APPLIED |
| **Self-adversarial negative sampling** | GLASS-BOX | +4-5.6 MRR / +5.3 Hits@10 pts, ablated directly (RotatE Table 13) | BORROWED-KNOWN, directly compatible with FHRR phase-rotation, NOT YET APPLIED |
| N3/nuclear-3-norm regularization | GLASS-BOX | +1-3 MRR/Hits@10 pts, modest, dataset-dependent (bigger on sparser graphs) | BORROWED-KNOWN, cheap, NOT YET APPLIED |
| Reciprocal-relations reformulation | GLASS-BOX | can be very large on some benchmarks (CP 0.33->0.86 MRR on FB15K); more modest but real on FB15k-237-tier sparsity | BORROWED-KNOWN, NOT YET confirmed applied to our arm — check first |
| Ensembling (k independent fits, averaged) | GLASS-BOX | +1-3 pts, reliable but modest; costs Nx compute | BORROWED-KNOWN, low priority (cost/gain worse than the recipe trio above) |
| Curriculum/multi-pass ordering (CL4KGE-style) | GLASS-BOX (in principle) | +0.1-3 Hits@10 pts on already-competitive models; NO paper isolates "changes final generalization" vs "gets there faster" | THIN evidence either way — do not lean on this as proven |
| **Iterative replay/consolidation (recall-consistency gate + validation early-stop)** | GLASS-BOX | UNPROVEN for changing generalization properties specifically (Course C note Section 2.4: zero direct precedent, anywhere) | **NEWER-GROUND — our differentiator, capped P<=0.25 per Course C** |
| Grid-code multi-module (residue-number-system) precision encoding | GLASS-BOX | brain: exponential-in-modules ambiguity-free range (Sreenivasan & Fiete 2011); zero direct KG-embedding precedent for discrete entities | NEWER-GROUND, novel-synthesis, capped P<=0.50 |
| Theta-gamma sequential (one-hop-at-a-time) phase-coded readout vs simultaneous joint factorization | GLASS-BOX | brain: quantified WM-span-vs-cycle-ratio law (Lisman/Idiart); substrate's own prior finding: sequential topology needs soft-decision chaining (P=0.35), NOT plain resonator (P=0.25) | NEWER-GROUND for KG use, but BORROWED for the underlying soft-decision-chaining mechanism (DFE/turbo-decoding is a mature ML/DSP technique) |
| DG-style sparse decorrelation front-end before resonator/attractor cleanup | GLASS-BOX | brain: Treves-Rolls sparse-coding capacity law is rigorous and old; substrate has a validated, unused `DGProjection` primitive | BORROWED mechanism math, NEWER application (never wired to resonator codebook path on this substrate) |
| Prioritized/reliability-gated replay scheduling | GLASS-BOX | brain evidence is the WEAKEST of the 4 hippocampal mechanisms scanned (Section 3 below) — mostly retention/need-gain framing (Mattar & Daw), not directly measured retrieval-PRECISION gains | NEWER-GROUND, thin brain evidence, capped P<=0.30 |
| Resonator/attractor iterative cleanup readout (with restarts, ACF) | GLASS-BOX | already deeply de-risked on this substrate (P_deflated=0.50 capped, `research_resonator_decode_capacity_ceiling_crux_v2_2026-07-10.md`) | BORROWED-KNOWN mechanism, on-substrate application already scoped |
| Grounded-attribute verifier (accept/reject generated candidates) | GLASS-BOX | own convergence-architecture synthesis; load-bearing per Candidate-B ablation (halves ranking when removed) | NEWER-GROUND (own synthesis), orthogonal multiplier on top of any geometry lever |
| NBFNet-style learned path-aggregation / message-passing | **REQUIRES-OPAQUE** | best absolute external number (NBFNet 0.415 MRR) | out of scope — breaks glass-box discipline, excluded from this ranking |

**Portability verdict:** every lever this program can actually use is glass-box-compatible. The REQUIRES-OPAQUE
family (GNN message-passing) is excluded by design, and Part 1 shows the honest cost of that exclusion is
small (~5-12% relative, possibly half-artifact) — a defensible, bounded tradeoff, not a crippling one.

---

## Part 3 — Ranked levers, deflated P + cost + cheap test

Ranked by (deflated P) x (expected gain) / (cost), highest first:

1. **Loss-function tuning (CE, not margin/BCE) on whatever scoring arm produced the geom number.**
   P_deflated=0.65 (borrowed-known, ablated directly in a primary source, architecture-independent — NOT
   novel synthesis, so not capped at 0.50). Expected gain: plausibly the single largest lever found (up to
   +41% relative MRR in the cited ablation). Cost: near-zero — a training-config change, no new code path,
   hours not days. **Cheap test:** re-fit the exact same arm with CE loss vs current loss, same seed/split,
   diff the held-out score. This should be the literal FIRST thing run after the decisive result, win or
   near-miss.
2. **Self-adversarial negative sampling.** P_deflated=0.60 (borrowed-known, directly ablated, RotatE-native —
   our phase-rotation operator already is RotatE-equivalent per Course C Part 2.1, so this ports with zero
   representational change). Expected gain: +5-15% relative Hits@10. Cost: low — a loss-reweighting term
   using the model's own current scores, implementable in an afternoon.
3. **N3/L3 regularization + reciprocal-relations reformulation, together.** P_deflated=0.50. Expected gain:
   modest alone (+1-3 pts) but the reciprocal-relations piece specifically can be large on sparse graphs and
   is nearly free to check (verify whether the current cell already trains both (h,r,t) and (t,r_inv,h)
   directions — if not, this is a one-line fix with disproportionate potential upside per Lacroix et al.).
4. **DG-style sparse decorrelation front-end wired into the resonator/attractor cleanup readout.**
   P_deflated=0.35 (mechanism math is rigorous/borrowed, but causal link to THIS substrate's basin-count
   specifically is unproven — flagged identically in two independent prior drills). Expected gain: unclear
   magnitude, but cheap to wire (`hdlab/hippocampal_encoder.py::DGProjection` already exists, unit-tested,
   never connected to this path). Cost: low (wiring, not new math).
5. **Grid-code multi-module (residue-number-system) precision encoding for entity/relation coordinates.**
   P_deflated=0.35 (brain mechanism is rigorously characterized — exponential range scaling — but zero direct
   precedent applying it to discrete KG entities specifically; this is genuinely novel synthesis, capped).
   Expected gain: potentially large for precision/collision-avoidance at scale (14k-25k entities), unclear
   for the specific "reach a held-out 2-hop inference" metric. Cost: moderate (requires redesigning the FPE
   coordinate scheme into multiple incommensurate-scale sub-codes, then combining — non-trivial but bounded
   engineering, reuses the substrate's own FHRR primitive).
6. **Sequential (theta-gamma-style) phase-coded, one-hop-at-a-time readout instead of joint/simultaneous
   multi-factor resonator decode**, IF the failure topology is confirmed sequential (per the crux-v2 note's
   own named risk). P_deflated=0.35 for the sequential case specifically (matches this substrate's own prior
   finding: soft-decision chaining P=0.35 vs plain resonator P=0.25 for sequential topology). Expected gain:
   meaningful IF topology matches, near-zero if the actual failure is simultaneous-composite (in which case
   lever priority reverts to the already-scoped resonator+ACF path). Cost: moderate — requires first
   confirming topology (cheap diagnostic), then a soft-decision-chaining implementation (DFE/turbo-style,
   mature technique, not novel math).
7. **Replay/consolidation depth (recall-consistency gate + validation early-stop, Course C Part 2.2-2.3).**
   P_deflated=0.20-0.25 (Course C's own number, unchanged — the single load-bearing genuinely-untested claim:
   does iterative fitting change GENERALIZATION properties, not just retention). Expected gain: the
   deep/exciting one IF it works ("the system reorganizes overnight"), but the honest literature search this
   cycle (Section 4) found ZERO direct precedent anywhere, biological or ML, for this exact claim. Cost:
   highest of all levers (a full iterative training-loop redesign with reliability gating). **Sequence
   AFTER levers 1-3, not before** — cheaper, better-precedented levers should be exhausted first so that any
   residual gap replay-consolidation is asked to close is the genuine residual, not training-recipe noise.
8. **Prioritized/reliability-weighted replay scheduling specifically (vs. uniform-pass replay).**
   P_deflated<=0.30. Brain evidence is the weakest of the four hippocampal mechanisms scanned this cycle —
   mostly a need x gain PLANNING framework (Mattar & Daw 2018), not directly measured retrieval-precision
   gains. Treat as an enhancement to lever 7 if lever 7 is pursued, not a standalone bet.
9. **Grounded-attribute verifier as an accept/reject gate on generated candidates.** Not a competitor to
   levers 1-8 — it is orthogonal and multiplicative (Part 2's convergence-architecture synthesis). Should be
   wired regardless of which geometry lever wins, since it is separately load-bearing (ablation halves
   ranking quality per Candidate-B note) and does not require picking a side in the geometry-lever debate.

---

## Part 4 — Brain-grounding: hippocampal precision mechanisms, ranked

Four mechanisms scanned this cycle, each with a one-line takeaway (full citations at bottom):

1. **Multi-module grid code (residue-number-system-like).** Ambiguity-free coding range grows EXPONENTIALLY
   in the number of modules (Sreenivasan & Fiete 2011; Wei/Prentice/Balasubramanian 2015 derive the optimal
   ~1.4x scale ratio between modules) — the cleanest, most rigorously quantified of the four, and the one
   with the best closed-form mathematical story (this is why it ranks #5 in Part 3 despite being the
   "sharpest" brain mechanism — it composes naturally with attractor cleanup rather than replacing it, but
   porting it to DISCRETE KG entities specifically has zero direct precedent).
2. **Theta-gamma sequential phase-coded readout.** Capacity/precision set by the RATIO of two oscillation
   periods (~7+/-2 items per theta cycle, Lisman & Idiart 1995; directly correlated with individual WM span
   in human EEG studies) — avoids the interference a simultaneous/parallel superposition readout would incur.
   Directly maps onto this substrate's own already-identified sequential-vs-simultaneous resonator-topology
   distinction (Part 3, lever 6).
3. **CA3 attractor-network cleanup precision vs. capacity.** Classical Hopfield capacity (~0.138N, Amit et al.
   1985) trades directly against basin sharpness; DG sparse coding (Treves-Rolls capacity law, capacity
   proportional to 1/(k ln(1/k)) for sparseness k) is the specific, rigorous, load-bearing reason DG exists —
   it decorrelates inputs so CA3 operates far below its raw capacity ceiling, buying large basins (precision)
   at the cost of raw pattern count. This is the mechanism already partially adopted on this substrate
   (resonator + restarts + ACF, P_deflated=0.50 capped) and the one with the most on-substrate validation.
4. **Replay depth/scheduling and precision.** WEAKEST evidence of the four — strong evidence for biased
   replay affecting WHAT gets consolidated and retention/planning (Mattar & Daw 2018 need x gain framework),
   thinner and more recent/less-consolidated evidence that replay VOLUME specifically sharpens retrieval
   PRECISION (2025-2026 papers on ripple size/duration exist but are new, not yet a settled literature). This
   is the exact mechanism Course C's replay-consolidation design rests on — and the brain literature itself
   does not yet strongly support the specific claim needed (precision from volume/depth, not just retention).
   **This independently corroborates Course C's own P=0.20-0.25 cap — the brain-grounding search this cycle
   did not surface additional support that would justify raising it.**

**Sub-agent's own (flagged, moderate-confidence) synthesis pick for largest expected precision gain if
ported:** the multi-module grid code (#1), because it has the cleanest closed-form justification and
composes with (rather than competes against) attractor cleanup. This drill's own read (Part 3 ranking) puts
it at #5 rather than #1 because of cost (non-trivial FPE-scheme redesign) and honest novel-synthesis
uncertainty about whether the precision gain transfers to a 2-hop discrete-entity KG task specifically, not
because the brain evidence is weak — flagging this divergence explicitly rather than picking one framing.

---

## Best-in-class reference definition (three distinct reference points, not one)

"Best-in-class" for a glass-box, self-contained reasoner needs three separate comparisons, each answering a
different question:

1. **Vs. opaque academic SOTA on the SAME held-out set (the honest bar for "did we leave easy performance on
   the table"):** re-run NBFNet or a similarly-scoped GNN baseline on our OWN genuine-L2 held-out CSKG split,
   not a borrowed FB15k-237 number — Part 1's numbers are informative for calibrating expected magnitude but
   are NOT a substitute for a same-split comparison, since our task (2-hop, different graph) is not identical.
   If never run, "best-in-class" claims about the glass-box ceiling are unverifiable analogy, not measurement.
2. **Vs. the brain (existence-proof ceiling, not a leaderboard number):** human transitive-inference studies
   report ~93.6% accuracy on novel/never-shown pairs in a single-relation, one-dimensional ordering task
   (a 2025 biorxiv study) — narrower than multi-relational KG completion, NOT directly benchmark-commensurable,
   but a legitimate qualitative ceiling reference: healthy brains generalize a learned relation to genuinely
   novel combinations at high accuracy using low-dimensional geometric/ordinal codes, not multi-hop message
   passing over a stored graph — directionally consistent with this program's own additive/geometric-code
   bet, and worth citing as an existence proof, never as a numeric target to hit.
3. **Vs. the glass-box-only ceiling within the ML literature (the actual competitive frame):** best
   documented glass-box performance (ComplEx+RP / TuckER / ComplEx-N3, ~0.37-0.39 MRR / ~0.56-0.57 Hits@10 on
   FB15k-237) sits at ~90-95% of best opaque GNN (NBFNet, 0.415/0.599) — and per the negative-pattern paper,
   maybe closer once benchmark artifacts are subtracted. **This is the honest, defensible "best-in-class for
   an inspectable reasoner" framing: not "we match GNNs," but "a fully self-contained, auditable reasoner
   using only borrowed-known, glass-box-portable levers gets within single-digit percentage points of opaque
   SOTA on the standard task — with a documented, cited literature basis for that specific number, not an
   assumption."**

---

## Cheap decisive test (pre-registered, reusable regardless of WIN/NEAR-MISS)

Once the decisive CSKG map-builder result lands, BEFORE any architecture change or replay-consolidation
build: re-fit the SAME arm that produced the geom number with the three cheapest borrowed-known levers
stacked (CE loss + self-adversarial negative sampling + N3 regularization + reciprocal-relations check),
same seed/split/held-out set. Report the delta.

**HARD-PASS (training-recipe lever confirmed real on this substrate):** the tuned re-fit improves the geom
number by >=10% relative on the SAME held-out genuine-L2 set, with random-code/trivial-baseline margins
intact (no leak). This confirms the substrate is subject to the same training-recipe confound Ruffinelli
found externally, and licenses running the FULL recipe trio before ANY further architecture/replay work.

**HARD-FAIL (training recipe was already adequate, or does not transfer to this regime):** the tuned re-fit
moves the geom number by <3% relative. This is still informative — it means the CSKG map-builder's honest
gap to ceiling is NOT a training-recipe artifact, and the more expensive levers (grid-code precision,
replay-consolidation, sequential readout) are asked to close a genuine residual, not noise. Proceed to lever
4+ in priority order (Part 3).

**Must-fail control:** running the SAME tuned recipe on the frequency-baseline arm (not the geometric arm)
should NOT produce a comparable improvement, if the whole framing (geometry realizes information frequency
does not) is sound — if it does, the "geom vs frequency" distinction itself needs re-examination before
trusting any further result.

---

## Falsifiable predictions

**HARD-PASS (Phase-2 optimization program, all four):**
1. Loss-function + negative-sampling + regularization re-fit (cheap decisive test above) moves the geom
   number by >=10% relative, OR is explicitly ruled out first with a documented null result (either outcome
   satisfies "checked before building anything expensive").
2. Whatever residual gap remains after the cheap borrowed-known levers is closed by AT MOST the next 1-2
   levers in Part 3's ranked list (i.e., the program does not need to invoke replay-consolidation, lever 7,
   to explain the majority of any remaining realized-vs-ceiling gap) — this would mean the "known toolkit"
   (Phase-2a, de-risked) does most of the work, and the novel replay-consolidation bet (Phase-2b, exploratory)
   is a smaller, better-scoped remaining question.
3. The final glass-box-only score, whatever it lands at, is reported alongside a same-split opaque-GNN
   comparison run (Best-in-class Section, point 1) — not compared only to borrowed external Hits@10 numbers.
4. No claim of "best-in-class" or "closing the gap to ceiling" is made without the calibration caveat from
   HEADLINE point 3 (our ceiling is architecturally TransE-tier in absolute terms for a harder 2-hop task,
   not NBFNet-tier) attached.

**HARD-FAIL (any one falsifies the "known toolkit does most of the work" framing):**
1. The cheap decisive test's tuned re-fit moves the geom number by <3% relative AND the frequency-baseline
   control ALSO moves by a comparable amount (confound in the harness itself, not informative about the
   geometry-vs-frequency question) — architecture is untestable until the harness confound is fixed.
2. Closing the majority of the realized-vs-ceiling gap requires invoking replay-consolidation (lever 7,
   P_deflated=0.20-0.25) as the PRIMARY lever, with the cheap borrowed-known levers (1-3) contributing <20%
   of the total gap closed — this would mean Phase-2 is NOT a de-risked climb, it is genuinely novel work
   with the same low P this session already assigned it, and messaging/resourcing should reflect that
   honestly rather than assuming a smooth known-toolkit climb.
3. A same-split opaque-GNN comparison run (once performed) shows the opaque method beating the glass-box
   ceiling by a much larger margin than the ~5-12% external-literature precedent (Part 1) — this would mean
   our specific task/graph has a genuine architecture-dependent expressiveness requirement the external
   FB15k-237 comparison did not predict, and the "glass-box ceiling is 90-95% of opaque SOTA" framing does
   not transfer to our regime.

---

## Cross-thread synthesis

- Directly answers the coordinator's three sharpening asks: Part 1 = track record with real deltas; Part 2 =
  glass-box portability tagging for every lever; Part 3/4 = newer-ground (replay-consolidation depth, grid-
  code precision, prioritized-replay scheduling, grounded-verifier) vs borrowed-known (loss tuning, negative
  sampling, regularization, reciprocal relations, resonator+ACF, ensembling) explicitly flagged per lever.
- Confirms and independently corroborates Course C's own P=0.20-0.25 cap on replay-consolidation (Part 4,
  point 4) — this cycle's brain-grounding search did not surface new evidence that would justify raising it,
  and if anything sharpens WHY it's capped there (the specific "volume/depth sharpens precision, not just
  retention" claim is genuinely thin even in the biological literature, not just the ML literature Course C
  already flagged).
- Reframes the entire Phase-2 program into two honestly-separated sub-phases: **Phase-2a (known toolkit,
  P 0.50-0.65 per lever, cheap, should run FIRST and could plausibly close most of the gap alone per the
  Ruffinelli precedent)** and **Phase-2b (replay-consolidation + grid-code precision + sequential readout,
  P 0.20-0.35 per lever, genuinely exploratory, should only be invoked for whatever gap survives 2a)** — this
  sequencing itself is the single most actionable structural recommendation from this drill.
- Ties into `research_resonator_decode_capacity_ceiling_crux_v2_2026-07-10.md`'s own ranked-lever list
  (restarts -> ACF -> block-sparse codebooks -> DG-decorrelation -> bigger N_DIM) — that list is entirely
  about DECODE/READOUT precision and is compatible with, not competing against, this drill's ENCODE/TRAINING
  lever list; both should run, in their own priority orders, on whatever arm the decisive result names.

## Substrate-product implications

- The honest, defensible product claim after this drill: **"our reasoning engine is fully self-contained and
  inspectable, and gets within single digits of academic black-box state-of-the-art on the standard
  benchmark task-class, using only auditable training-recipe and geometric-scoring techniques — with a cited
  literature basis for that specific number."** This is a strong, differentiated, honestly-bounded claim,
  distinct from "we match SOTA" (false) or "we're just worse" (also false and needlessly self-deprecating).
- The calibration warning (HEADLINE point 3) should be treated as a standing internal discipline, not just a
  one-time caveat: any time the ceiling number (0.42) or a future higher number is discussed externally or
  in product framing, it must be paired with "on a harder 2-hop task than the standard 1-hop benchmark" —
  omitting this would misrepresent an honest, hard-won result as underwhelming, which the number is not once
  correctly contextualized.
- If Phase-2a (borrowed-known levers) closes most of the gap cheaply, that is itself a strong, reusable
  product story: "we found and fixed a training-recipe gap using the same discipline the field itself
  discovered in 2020" — a legitimate, citable engineering win. If Phase-2b (replay-consolidation) is genuinely
  needed and works, that is the more novel, harder-to-replicate differentiator — but per this drill's own
  discipline, it should not be the first story told, since the cheaper explanation must be ruled out first.

---

## Citations (verified count: 4 parallel Sonnet lit-scans this cycle, all external sources fetched/verified, deduplicated)

**KGE track record / glass-box vs opaque (Task 1 agent, 8 sources):** Bordes et al. 2013 (TransE, NeurIPS);
Sun, Deng, Nie, Tang 2019 (RotatE, ICLR, arXiv:1902.10197 — Tables 5/7/13 read directly); Ruffinelli,
Broscheit, Gemulla 2020 ("You CAN Teach an Old Dog New Tricks," ICLR, openreview + readable extract — Tables
2/3 read directly); Lacroix, Usunier, Obozinski 2018 (N3/ComplEx-N3, ICML, arXiv:1806.07297 — Table 2 read
directly); Balazevic, Allen, Hospedales 2019 (TuckER, EMNLP); Zhu et al. 2021 (NBFNet, NeurIPS, repo README
read directly); Zhu et al. 2022/2023 (A*Net, arXiv:2206.04798); Chen et al. 2021 (ComplEx+RP aux. objective,
arXiv:2110.02834).

**Opaque-vs-glass-box gap, inductive setting, rule-based reasoners, brain reference (Task 4 agent, 9
sources):** Zhang & Yao 2022 (RED-GNN); AdaProp (KDD 2023); Teru, Denis, Hamilton 2020 (GraIL, ICML); RuleN
comparison (same); arXiv:2412.05114 (negative-pattern decomposition, 2024 — flagged single-paper/thin);
Neural-LP, DRUM, RNNLogic (rule-mining family numbers); biorxiv 2025 (human transitive-inference ~93.6%
accuracy, flagged single-study/narrow-paradigm).

**Negative sampling / regularization / curriculum / ensembling (Task 3 agent, 5+ sources):** Sun et al. 2019
(self-adversarial negative sampling ablation, same RotatE paper, Table 13 read directly); Lacroix et al. 2018
(N3, same as above); Ruffinelli et al. 2020 (loss-function ablation, Table 3, same as above); CL4KGE
(arXiv:2408.14840, 2024); Xu et al. 2021 (ensembling, arXiv:2104.05003, Table II read directly).

**Hippocampal precision mechanisms (Task 2 agent, 18 sources):** Sreenivasan & Fiete 2011 (Nat. Neurosci.,
grid-cell RNS coding); Fiete, Burak, Brunel 2008 (J. Neurosci.); Wei, Prentice, Balasubramanian 2015 (PNAS);
Mosheiff, Agmon, Moriel, Burak 2017 (PLOS Comp Bio); Lisman & Idiart 1995 (Science, theta-gamma WM); Lisman &
Jensen 2013 (Neuron); Kragel et al. (Nat. Neurosci., human intracranial phase-coding evidence); Mattar & Daw
2018 (Nat. Neurosci., prioritized replay); Ambrose, Pfeiffer, Foster 2016 (Neuron); Amit, Gutfreund,
Sompolinsky 1985 (Hopfield capacity); Treves & Rolls 1990s (sparse-coding capacity law); Leutgeb et al. 2007
(Science, DG/CA3 decorrelation); Neunuebel & Knierim 2014 (Neuron, CA3 pattern completion); plus 5 additional
2024-2026 replay/CA3 papers (recency-flagged, less-consolidated evidence per Part 4).

Total distinct external sources across all 4 lit-scans, deduplicated: approximately 40. All external queries
used generic math/CS/neuroscience terms only (e.g. "self-adversarial negative sampling knowledge graph
embedding," "grid cell residue number system coding capacity," "theta gamma phase coding working memory
capacity," "NBFNet path aggregation inductive knowledge graph") — no substrate-novel mechanism names,
configs, or numbers were sent off-platform, per [[feedback-query-privacy-decomposition]].

## Honest deflated-P summary

- P(borrowed-known glass-box training-recipe levers, stacked, materially close the geom-to-ceiling gap without
  needing replay-consolidation): **0.45** (deflated from a felt ~0.60-0.65; the external precedent — Ruffinelli
  — is very strong, but transfer to a 2-hop, CSKG-specific, differently-metric'd task is an inference, not a
  direct measurement; NOT capped at 0.50 as a hard ceiling since this is a borrowed-known technique
  application, but deflated per standard lit-scan discipline for lack of on-substrate-exact precedent).
- P(replay-consolidation depth is needed AND works, per Course C's own number, unchanged): **0.20-0.25**,
  independently corroborated (not raised or lowered) by this cycle's brain-grounding search.
- P(a genuinely novel grid-code multi-module precision scheme meaningfully improves the 2-hop held-out metric
  specifically): **0.35** (novel-synthesis capped at 0.50, further deflated for the specific task-transfer
  uncertainty named in Part 3, lever 5).

Hard-fail thresholds are pre-registered above (Falsifiable predictions section) so any of these outcomes is
informative regardless of which way the decisive CSKG result lands.
