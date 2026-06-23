# exp_dev hand-off — research: 5x-deeper Path C universal encoder architecture

**Filed-by:** Research (Opus 4.7-1M)
**Date:** 2026-06-23
**Trigger:** Research delivery — `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md`
**Pause state:** check `data/orchestrator_paused.flag` before dispatching.

Per [[feedback-no-experiment-design-in-prompts]] — this handoff names anchors and points at context files; exp_dev owns design.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (Tier-A, Phase-1 atom encoder isolation) — THE CHEAP DECISIVE TEST

- **Anchor pointer:** `enc_atom_graph_neighborhood_v1`
- **Substrate-product reading:** substrate self-mapping is blocked because char_trigram_atom encoder clusters atoms by name-prefix not by mechanism-family. v2c HARD_FAIL traced to encoder bottleneck. Phase-1 of hub-and-spoke federation builds the S2 atom encoder (GraphSAGE-style 2-hop KGStore aggregation + char_trigram base) and tests whether atoms cluster by cert_class + algebra.domain (substrate-internal labels, NOT human-curated v1 lexical families).
- **Tier hint:** Tier-A (cheap decisive test for the whole hub-and-spoke architecture; substrate-product gating capability).
- **Why-now:** USER reframe 2026-06-23 (encoder concern spans ALL 5 substrate data types not just text); substrate_self_mapping_gap drill explicitly named "encoder substitution" as the next move if v2e HARD_FAILS; this Anchor is the encoder-substitution.
- **Expected wall:** ~3-4 days impl + ~2-4 hr full cell on local_cpu_queue
- **P_deflated:** 0.30 (calibrated against 5 prior nulls in substrate self-mapping; novel-synthesis cap 0.45)

### Anchor 2 (Tier-B, Phase-2 relation spoke isolation) — DISPATCH IF ANCHOR 1 PASSES

- **Anchor pointer:** `enc_relation_rotate_v1`
- **Substrate-product reading:** S4 relation spoke; RotatE-style phase encoding for relation types (directed_by, capital_of, etc.) using existing FHRR/FPE primitives from dual-gain drill. Discriminator: do relation embeddings satisfy translation constraint h + r ~= t on cert-grade KG triples?
- **Tier hint:** Tier-B (federation building block; do not dispatch until Anchor 1 verdict).
- **Why-now:** if Anchor 1 PASSES, federation justified; relation spoke is the second-cheapest spoke (RotatE is well-validated lit; substrate has FHRR primitives).
- **Expected wall:** ~3-5 days impl + ~1-2 hr full cell on local_cpu_queue
- **P_deflated:** 0.25

### Anchor 3 (Tier-C, full federation hub composition) — DISPATCH IF ANCHORS 1+2 BOTH PASS

- **Anchor pointer:** `enc_hub_4spoke_v1`
- **Substrate-product reading:** hub-and-spoke alignment layer; cross-spoke contrastive Hebbian update of spoke gating weights; tests whether the shared HD hub representation is consistent across spokes (cos(S_i(X), S_j(X)) > 0.5 for same concept X across modalities).
- **Tier hint:** Tier-C (full architectural commitment; do not dispatch without first 2 verdicts).
- **Why-now:** if both prior anchors PASS, the federation has demonstrated lift on 2 of 4 spokes and the hub composition is the natural integration.
- **Expected wall:** ~5-7 days impl + ~2-4 hr full cell on local_cpu_queue
- **P_deflated:** 0.20

---

## Context pointers (file paths, not summaries)

- Research note (CONTRACT): `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md`
- Parent encoder drill: `notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md`
- Parent self-mapping drill: `notes/research_5x_deeper_substrate_self_mapping_gap_2026-06-23.md`
- Cross-corpus composition sibling: `notes/research_5x_deeper_cross_corpus_composition_gap_2026-06-23.md`
- Atom corpus (S2 input): `data/substrate_index/math/atoms.jsonl` (177k atoms)
- Cert supervision (S2 label): `data/substrate_index/meta/cert_ledger.jsonl` (688 rulings)
- KGStore primitive: `hdlab/kg_traversal.py`
- Bind primitive: `hdlab/binding.py`
- Bundle primitive: `hdlab/bundling.py`
- Existing baseline encoder: `hdlab/char_trigram_encoder.py`
- Discriminator pre-reg (v2e modularity-Z + LRG): `notes/research_5x_deeper_substrate_self_mapping_gap_2026-06-23.md` section "Cheap decisive test (v2e pre-reg)"

---

## Contract section (research's claim; exp_dev's responsibility to test)

**HARD bands (Anchor 1):**
- HARD_PASS: modularity-Z(gamma*) >= 2.5 AND LRG-stability >= 0.50 AND cert-class-ARI >= 0.30 AND mechanism-family-ARI >= 0.30
- MIDDLE_BAND: Z in [1.5, 2.5) OR one of ARIs in [0.15, 0.30)
- HARD_FAIL: modularity-Z <= 1.5 AT EVERY gamma AND both ARIs <= 0.15

**Discriminating-regime gate:**
- ARM_GRAPH_2HOP HARD_PASS alone -> S2 spoke sufficient; do NOT pre-commit federation
- ARM_GRAPH_PLUS_METRICS HARD_PASS only -> federation justified
- BOTH non-baseline HARD_FAIL -> route to S1 SoftHebb on atom descriptions next
- BASELINE_TRIGRAM HARD_PASS -> v2c was discriminator-bound; close encoder substitution drill

**Pre-reg location:** `preregs/2026-06-23_enc_atom_graph_neighborhood.md` (exp_dev creates)

**Pre-flight gate:**
- schema-vet via `tools/exp_dev/formula_selftests.py`
- sigma=0 sanity recall=1.000 across all arms
- HDLAB_EXP_NAME set
- REQUIRED_FIELDS schema-vet
- run_mode='full'
- commit-first
- per-unit checkpoint + restartable

---

## Autonomy declaration

exp_dev owns:
- Exact cell architecture (which message-passing scheme; how to bind relation type with target atom; how to project cert_ledger metrics into HD)
- Seed selection (recommend 7, 17, 23 per substrate-standard 3-seed)
- Per-unit checkpoint format
- Smoke gate composition
- Self-test invocation
- ARM_GRAPH_PLUS_METRICS feature engineering (which fields of cert_ledger entries to project; how to bind metrics.json features as modality)

Research owns:
- The substrate-physics claim (graph-neighborhood + multi-relational binding gives function-similarity beyond name-similarity)
- The HARD-PASS / HARD-FAIL thresholds
- The discriminating-regime gate
- The cross-spoke federation framing

If exp_dev finds the substrate-physics claim weak or the thresholds wrong, file a research-route-back note BEFORE dispatching.

---

## Notes for exp_dev

1. **177k atoms x 2-hop graph aggregation is laptop-CPU-feasible** at N=4096 in minutes per seed. Do NOT route to remote_cpu unless smoke shows >30min wall.
2. **Cert-class supervision is sparse** (688 / 177k = 0.4%); chain-grade-subset ARI is the right metric, NOT full-Store ARI.
3. **algebra.domain has only ~6 categories**; small-K clustering may be discriminator-bound on this label; check K=6 explicitly.
4. **Reuse v2e discriminator** (modularity-Z gamma sweep + LRG-stability tau sweep) from substrate_self_mapping_gap drill — DO NOT reinvent.
5. **2 of 5 substrate data types tested here** (atom IDs as S2; cert_ledger metrics as fused modality). Other 3 (entity names, relation names, text tokens) deferred to Anchors 2+3.
6. **Honest 1-week budget**: Anchor 1 only. Anchor 2+3 require additional 2-3 weeks.

-- Research (Opus 4.7-1M)
