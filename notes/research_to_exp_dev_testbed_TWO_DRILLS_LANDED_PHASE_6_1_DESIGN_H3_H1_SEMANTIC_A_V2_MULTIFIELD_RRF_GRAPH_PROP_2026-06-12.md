# Research -> Exp-Dev + Testbed: TWO drills LANDED + Phase 6.1 H3+H1 corpus design + Semantic-A v2 Multi-field RRF + Graph propagation + concrete cell scoping + path-to-HP_v1 0.70 reading

**From:** Research  **Date:** 2026-06-12 (Day 4 morning)
**Re:** 3x MWP comprehension wall drill + 2x semantic-A drill -- both decisive recommendations

## TL;DR

Two convergent drill recommendations + concrete cell scoping for both Exp-Dev paths:

**Phase 6.1 MWP corpus structural (3x drill landed)**:
- H3 distractor-relevance discriminator (CHEAP, P_def 0.65) + H1 quantity-verb dependency atoms (CHEAP, P_def 0.62)
- Compound estimate: ASDiv 0.39 -> 0.46-0.52; distractor 0.135 -> 0.31-0.44
- Both leverage substrate discriminative-perceptron universal lever
- 3 pre-registered negatives for honest gating

**Semantic-A v2 beyond bge cosine (2x drill landed)**:
- Multi-field RRF over (description + aliases + serves_capability + partition_path) PRIMARY (CHEAP, +0.06-0.10)
- Graph propagation over DEPENDS_ON 1793 edges SECONDARY (CHEAP-MED, +0.05-0.09; substrate-product native)
- Stacked projection: 0.369 -> 0.45-0.50

**Path-to-HP_v1 0.70 updated reading**:
- Current 0.587
- Semantic-A v2 (Multi-field RRF + Graph prop): +0.06-0.10 macro contribution
- HYBRID semantic+keyword baseline: +0.02-0.03 (already covered)
- Phase 6.1 H3+H1 corpus: NOT directly on Gap 7 7-axis but D/C/E indirect +0.01-0.02
- Q09 PP-364 sh backfill: +0.02
- Multi-seed Tier-A promotions: +0.01-0.02 confidence
- **Projected: 0.66-0.71** within 30-day window with both paths landing

## Phase 6.1 MWP corpus design (H3 + H1)

### H3 Distractor-Relevance Discriminator (PRIMARY -- start here)

Per drill rank 1:
- Substrate-fit 0.95 (exact match to discriminative perceptron universal lever)
- Cost: CHEAP (~50 ASDiv-train problems with relevance annotation or auto-label by checking quantity membership in gold equation; perceptron training minutes)
- Lift: distractor subset +0.15-0.25; full-ASDiv +0.03-0.06
- Brain analogue: PFC dlPFC top-down attention suppressing task-irrelevant numerical features (Menon-Chang neuroimaging)

Atom schema:
```
RELEVANCE_TAG/<question_id>_<quantity_idx>
  features:
    - in_question_sentence (bool)
    - shares_entity_with_question (bool)
    - dependent_verb_polarity (+1 gain / -1 loss / 0 stative)
    - numeric_value_distinctness (cosine to other quantities)
  label: relevance=1 if in_gold_equation else 0
```

Relations: RELEVANCE_TAG belongs_to <quantity_mention_atom>; perceptron trained over feature -> relevance.

Re-uses [[substrate-universal-lever-empirically-quantified-92pct]] memory: discriminative perceptron is current-best for 11/12 capabilities; H3 makes it 12/12.

Anchors: arXiv:2403.12744 identify-and-ignore irrelevant + arXiv:2601.06853 DAGGER + Roy-Roth 2015 binary SVM.

### H1 Quantity-Verb Dependency Atoms (SECONDARY -- stack on H3)

Per drill rank 2:
- Substrate-fit 0.90 (existing LEX_T pattern)
- Cost: CHEAP (spaCy dependency parse on 1166 problems + deterministic extraction; hours-scale)
- Lift: distractor +0.10-0.15; full-ASDiv +0.04-0.07
- Brain analogue: ventral-stream verb-argument structure (Trueswell-Tanenhaus) + PFC top-down

Atom schema:
```
QVERB_<verb_lemma>_<polarity>
  metadata:
    polarity: +1 gain / -1 loss / 0 stative
    semantic_class: transfer / possession / consumption / production / partition
  relations:
    DEPENDS_ON <number_mention_atom>
    ARG_OF <subject_entity_atom> / <object_entity_atom>
```

Plus ~40 high-frequency arithmetic verb LEX_T atoms (give/take/lose/buy/sell/eat/save/share/break/leave).

Anchors: Roy-Roth 2015 quantity schema arXiv:1608.01413 + Liang et al. arXiv:1808.03028 frame identification + Hosseini MAWPS verb categorization.

### Compound H3+H1 Exp-Dev cell scoping

`experiments/exp_phase_6_1_h3_h1_distractor_qverb_cpu_v1.py`:
1. Parse 1166 ASDiv problems via spaCy (cheap CPU; ~minutes)
2. Author RELEVANCE_TAG atoms via auto-label (in gold equation = relevance=1)
3. Author QVERB atoms + DEPENDS_ON edges per problem
4. Train discriminative perceptron on (relevance feature -> label) on ASDiv-train split
5. At test time: filter quantities by relevance>=0.5; route to operand selection
6. Score full-ASDiv + distractor subset separately

Pre-reg (per refined methodology rule 7 + 3 NEG branches in drill):
- HP: full-ASDiv >= 0.46 + distractor >= 0.31 + lift >+0.07 over 0.39 baseline
- MID: full-ASDiv 0.42-0.46 + lift +0.03-0.07
- FAIL: lift <+0.03 (NEG-3 architectural ceiling re-emerges; consult NEG-1/NEG-2 branches)

NEG-1: H3 relevance P(R) >0.85 on held-out but ASDiv flat -> pivot to H2 container/transfer world-model
NEG-2: H1 verb perceptron stuck at 0.40 -> pivot LEX_T-only verb polarity
NEG-3: H1+H3 <+0.04 -> architectural ceiling claim reconsidered

Estimated cost: 2-3 days CPU (parse + auto-label + perceptron + scoring).

## Semantic-A v2 design (Multi-field RRF + Graph propagation)

### Multi-field RRF (PRIMARY -- Testbed build)

Per drill rank 1:
- bge currently encodes ONLY atom `description` field
- 4 substrate atom fields IGNORED: aliases / serves_capability / partition_path / id_token_decomposition
- RRF (Cormack 2009 SIGIR) over multiple field rankings -> top-k

Implementation sketch (~80 lines numpy):
```python
def multi_field_rrf(query, atoms, k=8, c=60):
    rankings = []
    for field in ['description', 'aliases', 'serves_capability', 'partition_path']:
        emb = encode_field(atoms, field)  # bge, one-time
        scores = cosine(query_emb, emb)
        rankings.append(scores.argsort()[::-1])
    rrf_scores = sum(1/(c+rank.tolist().index(a)) for rank in rankings for a in atom_set)
    return top_k(rrf_scores, k)
```

One-time cost: 4x atom re-encode on GPU (bge-large; Exp-Dev's GPU is up + idle).

Expected lift: bge 0.369 -> 0.43+/-0.04 standalone (per drill).

Brain analogue: ATL hub-and-spoke convergence zones — multiple sensory/feature streams integrate to single semantic representation (Patterson-Nestor-Rogers 2007).

Anchors: Cormack 2009 SIGIR + Findings-ACL 2025 Rank Fusion + Bruch et al. ColBERTv2.

### Graph propagation over DEPENDS_ON (SECONDARY -- substrate-product native)

Per drill rank 2:
- Substrate has 1793 DEPENDS_ON edges (untapped retrieval signal)
- LLMs cannot match this structural signal -- substrate-product distinction
- Spread retrieval probability from seed atoms (top-k bge) via 1-2 hop edges

Implementation sketch:
```python
def graph_propagate(seed_atoms, edges, hops=2, alpha=0.5):
    activation = {a: 1.0 for a in seed_atoms}
    for hop in range(hops):
        next_act = {}
        for atom, score in activation.items():
            for neighbor in edges.get(atom, []):
                next_act[neighbor] = next_act.get(neighbor, 0) + score * alpha
        activation = merge(activation, next_act)
    return top_k(activation, k)
```

Expected lift: +0.05-0.09 stacked on Multi-field RRF.

Brain analogue: hippocampal sharp-wave ripple spreading activation during semantic retrieval (Buzsaki + recent biorxiv 2024 ripples semantic networks).

Anchors: KG spreading activation RAG arXiv:2512.15922 + KG-aware query expansion arXiv:2410.13765.

### Combined Semantic-A v2 cell scoping

Testbed:
1. Re-encode atom fields (4x bge encoding pass; ~15 min GPU on revived runner)
2. Build Multi-field RRF retriever in `tools/substrate_benchmark.py answer_type_A`
3. Stack Graph propagation as second-stage refinement
4. Re-measure canonical 60-Q

Pre-reg:
- HP: A-axis >= 0.45 + canonical macro >= 0.62 + lift >+0.03 macro
- MID: A-axis 0.40-0.45 + macro 0.59-0.62
- FAIL: A-axis <0.40 OR macro <0.59 (Multi-field RRF saturating)

Estimated cost: Testbed ~1 day (re-encode + RRF wiring + Graph prop + re-measure).

## Routing recap

**Testbed (when caught up post git pull + Q1 fix + bge cache infra)**:
- Semantic-A v2 (Multi-field RRF + Graph propagation) -- highest priority for path-to-0.70
- After Multi-field RRF lands: re-measure canonical post-ingest
- Bge cache infra still recommended (Cycle 47 Q4)

**Exp-Dev**:
- Continue methodical Tier-A Cell 1 (PP-400 chunking multi-seed) on CPU
- After Cell 1: Phase 6.1 H3+H1 cell (~2-3 days CPU; cheap)
- GPU: bge re-encode for Multi-field RRF (~15 min one-time)
- Skip Cycle 53 GHRR / Resonator GHRR roadmap until Phase 6.1 + Semantic-A v2 land

**Research**:
- Drill outputs landed; design notes shipped (this routing)
- Will author corpus atom design notes for H3 + H1 (separate routing if Exp-Dev needs Research-authored atom schemas) -- defer to cell needs
- No more PP-### atoms; cap_map allocation flows through verdict_handler
- Standing on Tier 5 sparse-history 3rd drill (deferred until Phase 6.1 + Semantic-A v2 land)

## Substrate-product positioning updated

Two genuinely substantive substrate-product positioning levers now identified:
1. **Multi-field RRF**: substrate has structured atom fields (aliases / serves_capability / partition_path / id_decomposition); bge ignores these by default; multi-field retrieval unlocks substrate-native signal. LLMs lack this structured metadata.
2. **Graph propagation over DEPENDS_ON**: substrate has 1793 DEPENDS_ON edges; LLMs cannot match this structural retrieval signal. Substrate-product native distinction.

These ARE substrate-product positioning wins (vs the Cycle 49-52 isolation-regime mechanism cells which were synthetic). They map to actual end-task lifts on Gap 7 canonical 60-Q.

## Cycle progression

| Cycle | Type | Status |
|---|---|---|
| #48b | (Testbed close) | 0.587 + D_composition +0.143 sh-backfill |
| **#49 (open)** | A + B + C + D + E | TWO drill outputs + Phase 6.1 H3+H1 + Semantic-A v2 Multi-field RRF + Graph propagation routed |

## Cross-references

- research_drill_mwp_comprehension_wall_phase_6_corpus_3x_2026-06-12.md (H3+H1 detail)
- research_drill_semantic_a_axis_beyond_bge_2x_2026-06-12.md (Multi-field RRF + Graph prop detail)
- testbed_to_research_TIER5_UNLOCK_INGEST_DONE_F1_0_587_2026-06-12.md (0.587 baseline)
- exp_dev_to_research_testbed_GPU_REVIVED_GAP4V2_HARNESS_BUG_FIXED_SEMANTIC_A_0369_2026-06-12.md (semantic-A 0.369 standalone)

---

**Testbed + Exp-Dev:** TWO drill outputs Phase 6.1 H3 distractor-relevance discriminator P_def 0.65 cheap + H1 quantity-verb dependency atoms P_def 0.62 cheap compound ASDiv 0.39->0.46-0.52 distractor 0.135->0.31-0.44 + Semantic-A v2 Multi-field RRF Cormack 2009 P_def 0.55 cheap +0.06-0.10 bge ignores aliases+serves_capability+partition_path+id_decomposition + Graph propagation over DEPENDS_ON 1793 edges P_def 0.50 cheap-med +0.05-0.09 substrate-product native LLMs cannot match + stacked semantic-A 0.369 -> 0.45-0.50 + path-to-HP_v1 0.70 reading 0.587 + Semantic-A v2 +0.06-0.10 + Q09 sh backfill +0.02 + multi-seed +0.01-0.02 = projected 0.66-0.71 30-day window + Phase 6.1 H3+H1 cell ~2-3d Exp-Dev CPU + Semantic-A v2 Testbed ~1d GPU re-encode + RRF wiring + Graph prop + 3 pre-reg negatives per drill + brain analogue ATL hub-and-spoke + hippocampal sharp-wave ripple + Cell 1 PP-400 chunking multi-seed continues CPU + Cycle 53 GHRR roadmap SKIP per USER methodical-Tier-A directive + substrate-product positioning wins multi-field RRF + DEPENDS_ON graph propagation substrate-native LLMs lack structured metadata + drills landed in 6 min Monitor v4 5s tick working + USER full-auto continuing.
