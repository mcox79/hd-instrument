# Pre-reg: path_c_atom_graph_encoder_phase1_smoke_v1

Date: 2026-06-23
Anchor: `path_c_atom_graph_encoder_phase1_smoke_v1`
Cell: `experiments/exp_path_c_atom_graph_encoder_phase1_smoke_v1.py`
Queue: `local_cpu_queue` (smoke+full bundled; CPU; numpy + minimal torch for learned-proj arm; expected wall ~30 min)

## Motivation (Path C Phase-1 spoke; first decisive test)

Per `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md` HEADLINE
"hub-and-spoke federation (brain ATL + CLIP/ImageBind convergent) NOT one universal
encoder; ship Phase-1 atom-graph encoder (S2 only, ~1 week) as cheap decisive test."

Encoder dual-gain HARD_FAIL today (all 4 forward-only encoders Shannon-floor). Path
A word2vec running. Path C is the substrate-OWNED backprop-trained encoder lane.
Phase-1 atom-graph encoder is the cheapest Path-C decisive test: substrate trains a
GraphSAGE-style encoder on its OWN atom adjacency graph (substrate's atoms + cert
ledger + compose-with metadata = the supervised signal).

This SMOKE tests whether GraphSAGE-style features on atom-adjacency produce
meaningfully BETTER mechanism-family clustering than `char_trigram` name-encoding.
If HARD_PASS, the FULL Path C Phase-1 build (~1 week) is justified.

## Design

For each chain-grade atom (sample N=100 from `data/substrate_index/math/atoms.jsonl`
joined to `data/substrate_index/meta/cert_ledger.jsonl`):

- `ARM_CHAR_TRIGRAM_NAME` (baseline; same as atom_feature_encoder smoke landed
  MIDDLE_BAND today). Encode atom_id via `hdlab.char_trigram_encoder.CharTrigramEncoder`.
- `ARM_GRAPHSAGE_2HOP` (untrained GraphSAGE). For each atom:
  - Build symmetric adjacency from `composes_with` / `typed_by` / `relabeled_by` /
    `serves_capability` / `algebra.about_topic` references (treat each referenced
    token as a neighbor node; symmetric edge).
  - Base feature per atom = bipolar HV of
    `(cert_tier_token + mechanism_family_token + sigma_regime_token)`.
  - GraphSAGE 2-hop: `feat[atom] = mean(base[neighbors(neighbors(atom)) U
    neighbors(atom) U {atom}])` then sign-bundle.
- `ARM_GRAPHSAGE_2HOP_LEARNED` (learned projection; backprop). Same 2-hop
  aggregated feature, then linear projection W (N_DIM x N_DIM, sparse-init at
  density 0.01) trained via contrastive loss for ~100 epochs:
  - Positive pair = atoms in same mechanism family (random pair per epoch).
  - Negative pair = atoms in different mechanism family (random per epoch).
  - Loss = `max(0, 1 - cos(W @ a_pos, W @ b_pos)) + max(0, cos(W @ a_neg, W @ b_neg) + 0.1)`.
  - SGD lr=1e-2, batch=8 pairs / step, ~100 epochs total. ~5 min CPU at N_DIM=4096.
  - This is the BACKPROP part of Path C (substrate-OWNED learned encoder).

Discriminator: k-means K=10 on N=100 atoms in each arm. Compute mechanism-family
purity per cluster (modal-family fraction); weighted average across clusters.

Sanity self-test (PRE-DISPATCH): planted-graph endpoint check. Build a 9-atom
graph with 3 disconnected components (atoms within component share neighbors;
across components don't). GraphSAGE arms should recover the 3 clusters perfectly
(purity = 1.0). char-trigram baseline is NOT bound by this gate (different
mechanism); we only assert the GraphSAGE arms pass.

## Pre-reg bands (Path C Phase-1 spoke works; chain-grade candidate; >1 week build justified)

HARD_PASS:
- `ARM_GRAPHSAGE_2HOP_LEARNED.purity >= 0.92`
- AND `ARM_GRAPHSAGE_2HOP_LEARNED.purity - ARM_CHAR_TRIGRAM_NAME.purity >= 0.05`
  (learned graph features lift over name-encoding baseline)
- AND `ARM_GRAPHSAGE_2HOP_LEARNED.purity - ARM_GRAPHSAGE_2HOP.purity >= 0.03`
  (learned projection adds value over untrained graph features)
- AND `planted_graph_purity_graphsage_arms == 1.0`
- AND substrate-only-decode preserved (`n_llm_calls == 0`)

HARD_FAIL (graph-feature encoding does not help even with learning; Path C
Phase-1 dead; try Phase-2 different spoke):
- `ARM_GRAPHSAGE_2HOP_LEARNED.purity <= ARM_CHAR_TRIGRAM_NAME.purity + 0.02`
- OR substrate-only-decode violated

MIDDLE_BAND:
- lift over baseline in `(0.02, 0.05)` (positive signal; sub-threshold)

## By-construction-saturation note

The prior atom_feature_encoder smoke landed MIDDLE_BAND today
(`feat_purity=0.940 trig_purity=0.887 lift=+0.053`) because chain-grade atom
names usually CONTAIN the mechanism keyword by naming convention (cleanup,
storage, generation, etc.). The char-trigram baseline is by-construction at the
~0.89 floor on this corpus.

GraphSAGE arms must EXCEED this floor by adding genuinely-graph-structural
signal (the adjacency contains atoms with different naming patterns but
shared functional role). If the GraphSAGE arms also saturate near 0.94, the
substrate's atom-adjacency graph is dominated by name-leakage (composes_with /
typed_by links connect atoms that already share mechanism keywords) and
Path C Phase-1 is by-construction-cert-bound: route to Phase-2 (relation
spoke) or cross-corpus encoder.

## Implementation

- N_DIM=4096 (FULL), K=10, N=100 chain-grade atoms, seeds=[7, 17, 23]
- Smoke: N_DIM=1024, K=5, N=30, seeds=[7], LEARNED epochs=20
- numpy adjacency build + numpy k-means (Lloyd's; cosine-normalized rows)
- pytorch ONLY for the contrastive learned-projection arm
  (torch=2.12.0+cpu confirmed in `.venv`); ~5 min CPU at FULL
- Cell-local; promote to `hdlab/atom_graph_encoder.py` only if HARD_PASS
- Per-seed checkpoint via `experiments/_seed_checkpoint`
- ASCII-only; no emojis; no em-dashes

## Smoke gate result (PRE-DISPATCH)

Cell `--self-test` runs the planted-graph endpoint check.
Cell `--smoke` runs seed=7 at N_DIM=1024 / N=30 / K=5 / LEARNED epochs=20.
Expected smoke wall: ~30s (full at 30 min).

## Discriminating-regime gate (per Research handoff Anchor 1)

- `ARM_GRAPHSAGE_2HOP_LEARNED` HARD_PASS alone -> S2 spoke sufficient; do NOT
  pre-commit federation; queue FULL Path C Phase-1 (~1 week).
- `ARM_GRAPHSAGE_2HOP` HARD_PASS without LEARNED needed -> untrained graph
  features are enough; skip backprop in production build.
- BOTH non-baseline HARD_FAIL -> route to S1 SoftHebb on atom descriptions
  next OR escalate to cross-corpus pool with name-stripped baseline.
- BASELINE_TRIGRAM HARD_PASS alone above 0.92 -> by-construction lexical
  leak dominates; close encoder substitution drill at this corpus boundary;
  test cross-corpus next.

## Self-test command

```
HDLAB_EXP_NAME=path_c_atom_graph_encoder_phase1_smoke_v1_smoke \
  .venv/Scripts/python.exe \
  experiments/exp_path_c_atom_graph_encoder_phase1_smoke_v1.py --self-test
```
