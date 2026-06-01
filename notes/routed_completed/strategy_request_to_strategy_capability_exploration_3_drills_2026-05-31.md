# Strategy request: 3 capability-exploration experiments (compositional binding + hierarchical concepts + Bet B ret_A rescue)

## Trigger: research drills 2026-05-31 (3 parallel Sonnet lit-scan + design drills)

Origin: user 2026-05-31 -- shared external Claude evaluation proposing 12 substrate capability-exploration directions; user wants to "eventually deep dive into all of the below" and "start researching these and considering experiments that could show these."

Research session evaluated all 12 directions (audit at `notes/research_capability_exploration_12_directions_audit_v1_2026-05-31.md`) + dispatched 3 parallel Sonnet drills on the highest-leverage subset (Directions 1, 6, 7). All 3 drills returned with concrete experiment designs + falsifiable predictions + cost estimates.

## Finding (one paragraph)

Three experimental designs ready for exp_dev refinement, all Hebbian-compatible (no gradient required) and all targeting capability-exploration claims that meaningfully strengthen substrate's product-positioning moat:

1. **D7 Bet B retention_A rescue (close known cap_map gap)** -- top candidate: interspersed Hebbian replay of Stage-A atoms during Stage B/C/D writes at p_replay=20-30%. P_def=0.57 standalone; combined with orthogonal-codebook substack (Rank 2) → **P_def=0.65**. If retention_A lifts from 0.745 to >=0.80, the Bet B 4-stage continual learning Tier-1 killer capability promotes 🟡 PARTIAL → 🟢 PASS. Mature-probe rescue; ~2-3 weeks engineering.

2. **D6 hierarchical concept formation (cheap instrumentation)** -- SVD on existing post-V2 24h substrate W; measure σ_1/σ_2 spectral concentration + top-K singular vectors vs codeword clusters + cross-relation transfer + null-shuffle discrimination + semantic-ablation test (substitute random value codewords preserving predicate sharing → substrate-physics claim predicts spectral structure SURVIVES). P_def=0.35-0.50. **No new experiment design needed** -- runs against W matrix already accumulated by V2 24h workload. ~1 week instrumentation + analysis.

3. **D1 compositional binding algebra at production scope** -- corpus where every multi-hop chain stored but COMPOSED relation-key never written; 20% memorization traps embedded; production envelope M=3-5×M_c (~1700-2800 facts), d={3,4,5}, K=500, 32-64 n_queries/cell, 5 seeds. P_def=0.42. Includes 4-protocol audit-trail verification (binding-op null test corrupts intermediate key → if accuracy doesn't drop, audit log is decorative). Substrate-physics test most worth empirically nailing; ~2-3 weeks.

## Recommended action

**1. Cap_map portfolio annotations / new rows (orchestrator decides; not auto-dispatched).**

| Row | Action | If experiment PASSES |
|---|---|---|
| Bet B 4-stage continual learning (existing 🟡 PARTIAL @ v189; ret_A=0.745) | Annotate with rescue mechanism path | Promote 🟡 → 🟢; ret_A>=0.80 closes Tier-1 killer capability |
| **Hierarchical concept formation** (NEW row OR sub-row under "Concept structure") | Add at 🔬 with P-band 0.35-0.50 | Promote to 🟡 (if substrate-physics) or annotation-only (if corpus-property only) |
| **Compositional binding algebra at production scope** (NEW row) | Add at 🔬 with P-band 0.40-0.50 | Promote to 🟢 if HARD-PASS; substrate-physics moat strengthens substantially |

**2. Three experiments to dispatch (ranked by sequencing recommendation).**

**EXPERIMENT 1: bet_b_ret_a_replay_rescue_v1_n8192 (HIGHEST LEVERAGE)**

- **Anchor**: `bet_b_ret_a_replay_rescue_v1_n8192`
- **Spec sketch (testbed engineering scope)**: extend existing Bet B 4-stage continual-learning probe with replay buffer B_A holding Stage-A (key, value) pairs; during each Stage-B/C/D write, with probability p_replay apply additional outer-product update for random sample from B_A. Sweep p_replay ∈ {0.10, 0.20, 0.30}; 5 seeds; N=8192; same harness as v189/v239.
- **Why first**: closes known cap_map gap (ret_A=0.745 vs >=0.80 threshold); existing probe; rescue mechanism is direct outer-product write (validated substrate primitive); 5.5pp gap is in literature-supported recovery range; engineering cost lowest of the 3.
- **Pre-reg HARD-PASS**: ret_A >= 0.820 at SOME p_replay; ret_B + ret_C don't drop below 0.800 (don't rob Peter to pay Paul).
- **Pre-reg HARD-FAIL**: ret_A < 0.780 across all 3 p_replay values (replay doesn't move the needle).
- **Pre-reg MIDDLE-BAND**: ret_A ∈ [0.800, 0.820] (just-clears-threshold; combined Rank 1+2 follow-on candidate).
- **Cost**: ~2-3 days exp_dev + ~30min CPU per cell × 15 cells × 5 seeds; total ~75 min wall on local CPU.
- **Routing**: orchestrator → exp_dev → queue.

**EXPERIMENT 2: hierarchical_concept_formation_instrumentation_v1 (CHEAPEST)**

- **Anchor**: `hierarchical_concept_formation_v1_n4096`
- **Spec sketch (research/testbed scope; instrumentation not experiment-design)**: run SVD on the W matrix accumulated from V2 24h sustained workload (file location: `data/sustained_workload_24h_baseline_v1_n4096_state.pt` or equivalent). Compute:
  - σ_1/σ_2 spectral gap ratio + effective rank
  - Top-10 singular vectors → project stored key codewords → coherence test
  - k-means clustering on M stored key codewords with K_cluster ∈ {sqrt(M), M/10, M/20}
  - Bind-then-query: bundle 5 class-member keys → query W → measure cosine to held-out class members
  - Cross-relation transfer (predicate extraction via element-wise product)
  - Null-shuffle baseline: 100 random shuffles; PASS = real metrics >2σ above shuffled
  - Dense-RAG baseline: same M facts encoded by sentence-transformer → FAISS → k-means; substrate-distinctive requires structure absent in FAISS clustering
  - Semantic-ablation test: substitute value codewords with fresh random bipolar (preserve predicate sharing); spectral structure should survive if substrate-physics
- **Why second**: literally NO new experiment design required; runs on existing accumulated W. Cheap to falsify the speculative claim.
- **Pre-reg HARD-PASS**: σ_1/σ_2 > 3.0 AND silhouette > 0.25 (vs null < 0.10) AND cross-relation transfer cos > 0.35 AND semantic-ablation preserves structure.
- **Pre-reg HARD-FAIL**: σ_1/σ_2 < 1.5 (indistinguishable from Marchenko-Pastur) OR silhouette ≤ 0.10 OR dense-RAG matches/exceeds substrate clustering.
- **Pre-reg MIDDLE-BAND**: structure present (σ_1/σ_2 > 1.5) but corpus-dependent (dense-RAG shows similar).
- **Cost**: ~1 week instrumentation + analysis; pure CPU; <2h wall for the SVD/k-means/shuffle computation; rest is interpretation.
- **Routing**: testbed instrumentation OR exp_dev as a one-shot analysis anchor.

**EXPERIMENT 3: compositional_binding_production_scope_v1 (HIGHEST DISTINCTIVENESS)**

- **Anchor**: `compositional_binding_production_v1_n4096`
- **Spec sketch (exp_dev refines from drill design)**: fact-graph corpus where every multi-hop chain stored as atomic outer-product writes BUT composed relation-key NEVER stored. 70% compositional queries (absent from W) + 30% stored-chain controls. 20% memorization traps embedded: (a) near-miss entity trap at cos=0.15 from target intermediate, (b) spurious composed-key attractor at cos=0.12 from q_comp, (c) path-shortcut trap (parallel variant with one shortened path; differential accuracy isolates shortcut-dependence). Test substrate Path D (expected PASS) vs Path B (expected FAIL on compositional cells; verifies cosine-not-algebra). Production envelope: M=3-5×M_c (~1700-2800 facts), d ∈ {3,4,5}, K_paths=500, n_queries=32-64 per cell, 5 seeds. Audit-trail verification: 4-step protocol incl. binding-op null test (corrupt intermediate key in audit log → re-run; if accuracy stable, audit decorative).
- **Why third**: highest distinctiveness for substrate-physics moat BUT longest engineering scope (corpus construction is the bulk); validates compositional reasoning claim that distinguishes substrate from any RAG/memory system.
- **Pre-reg HARD-PASS**: compositional accuracy ≥ 0.78 across all depth cells; trap-entity selection ≤ 0.08; Path D - Path B margin ≥ 0.15.
- **Pre-reg HARD-FAIL**: compositional accuracy ≤ 0.55 at d≥4; OR trap selection ≥ 0.25; OR shortcut-variant accuracy ≥ 0.90 while full-corpus ≤ 0.60.
- **Pre-reg MIDDLE-BAND**: compositional accuracy ∈ [0.56, 0.77] with depth-degradation pattern; re-run at lower M or higher N candidate.
- **Cost**: ~2-3 weeks exp_dev + ~2-4 hours GPU wall per full run (M up to 2800 × d=5 × K=500 × n_q=32-64 × 5 seeds).
- **Routing**: orchestrator → exp_dev (corpus construction is the engineering work).

**3. Three NEXT-CYCLE candidates** (after these 3 land OR after substrate-LLM Week 5 returns baseline data):

- **Direction 2 (analogical reasoning)** — natural follow-on if Direction 1 HARD-PASSes; lower marginal cost on top of compositional binding harness.
- **Direction 5 (few-shot generalization)** — SCOPED to N-examples-to-unseen-instances pattern generalization (not single-fact incremental, which is already in substrate-LLM build's real-time-learn-then-query benchmark).
- **Direction 4 (cross-domain transfer)** — substantial multi-domain corpus construction; substrate-LLM Week 5 may inform whether this is in scope.

**4. Five DEFERRED with explicit criteria** (per `notes/research_capability_exploration_12_directions_audit_v1_2026-05-31.md` audit):

- Direction 3 (counterfactual via geometric manipulation) — requires new mechanism design; SVD-cascade falsifier HARD_FAILED (predecessor mechanism parked)
- Direction 8 (meta-learning) — highly speculative; defer until operational definition emerges
- Direction 9 (causal inference engine) — requires new substrate-side causal binding semantics; substantial design
- Direction 11 (differential privacy) — substantial cryptographic work; pilot-deployment-driven
- Direction 12 (universal function approximator) — academic-claim-flavored; product case not yet identified

## Confidence

P_deflated estimates per experiment (calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]):

- **D7 Bet B replay rescue**: 0.57 (standalone Rank 1 replay) / 0.65 (Rank 1+2 combined replay + orthogonal codebook)
- **D6 hierarchical concept formation**: 0.35-0.50 (lower bound: substrate-distinctive; upper bound: any measurable structure beyond null)
- **D1 compositional binding production scope**: 0.42 (range 0.35-0.50)

Calibration:
- D7: novel-synthesis cap not binding; core mechanism (Hebbian replay) is well-grounded literature (Shaham & Chandra 2022; Saighi & Rozenberg 2025)
- D6: cap not binding for instrumentation (cheap to falsify); higher for substrate-physics claim
- D1: cap 0.50 binding for the specific substrate × trap × audit-protocol combination; uncharted regime

## Files of interest

- `notes/research_capability_exploration_12_directions_audit_v1_2026-05-31.md` (12-direction audit + 4-category split + overlap-with-substrate-LLM-build analysis + 5-deferral criteria)
- Drill outputs (returned to research session, not written to files):
  - D1 compositional binding (P_def 0.42 + 4-protocol audit-trail verification)
  - D6 hierarchical concept formation (P_def 0.35-0.50 + SVD instrumentation protocol)
  - D7 Bet B ret_A rescue (P_def 0.57; top candidate Hebbian replay; combined 0.65)
- Internal cross-refs: `notes/substrate_capability_map.md` line 123 (Bet B 4-stage @ ret_A=0.745); v228 NOVEL CLASS rejection; v297 latest (Path D 32N + adversarial RED→YELLOW + compression foothold)
- Substrate-LLM build interaction: `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md` (Phase 1 bespoke benchmarks already test partial aspects of Directions 5, 7, 10)
- Memory: `project_substrate_killer_features_2026-05-26`, `project_substrate_strategic_inversion_48h_2026-05-26`, `feedback_aggressive_cross_domain_research`, `feedback_capabilities_mapping_not_competitive_analysis`

## Sequencing recommendation (orchestrator decides)

**Recommended order**:
1. **D7 Bet B ret_A rescue FIRST** (~1 week exp_dev + ~75min CPU). Closes known cap_map gap; mature probe; lowest novelty risk; promotes Tier-1 killer capability yellow → green if PASS.
2. **D6 hierarchical concept formation IN PARALLEL** (~1 week instrumentation; pure analysis on existing post-V2 W; no GPU). Doesn't compete for compute resources with D7.
3. **D1 compositional binding LAST** (~2-3 weeks exp_dev + ~2-4h GPU per full run). Largest scope; highest distinctiveness; substrate-physics moat. Schedule after D7 + D6 land OR concurrent with Week 1-3 of substrate-LLM build.

**Cumulative cost**: ~4-5 person-weeks engineering + ~5-10 hours compute. No cloud spend required (all local CPU/GPU). Compatible with the parallel substrate-LLM build (~7-8 weeks).

## Not auto-dispatched

This is a research delivery + recommendation. Orchestrator decides:
- (a) Cap_map portfolio annotations / new rows (Bet B annotation; Hierarchical concepts NEW row; Compositional binding NEW row)
- (b) Experiment dispatch timing (D7 first by sequencing recommendation; D6 in parallel; D1 last)
- (c) Engineering ownership (D7 is exp_dev; D6 is testbed instrumentation OR exp_dev one-shot; D1 is exp_dev corpus construction)

No engineering work begins without orchestrator queueing via standard exp_dev path.

---
BULK-ARCHIVED 2026-06-01: previously processed (cap_map v311+ reflects acted-on work); routing closed retroactively per dashboard inbox-clearance Path A.
