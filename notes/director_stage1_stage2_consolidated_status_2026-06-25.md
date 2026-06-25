# Stage 1 + Stage 2 consolidated status — 2026-06-25 (post-morning corrections)

Replaces the outdated `director_stage1_closure_synthesis_2026-06-24.md` (the gap-map approach was refuted yesterday + today). This note is the current strategic picture.

## Stage 1 — substrate-product native capabilities

**STATUS: CHAIN-GRADE ALIVE on 8 native capabilities + SEMANTIC battery verified.**

| Capability | Status | Evidence |
|---|---|---|
| Storage (1-hop) | chain-grade | top1=1.000 at M=500/N=8192 |
| Capacity | chain-grade | 25000+ patterns |
| Pattern completion | chain-grade | top1=1.000 from 50% corruption |
| Working memory | chain-grade | cap=30 (beats Miller 7±2) |
| Sequence binding | chain-grade | K=20 lossless |
| Compositional gen (obj-axis) | chain-grade | +0.724 lift |
| CL no-forget | chain-grade | CRISPR forget=0.006 |
| Trained analogical recovery | chain-grade | top5=1.000 |
| SEMANTIC battery v2 FULL | HARD_PASS 6/6 | A3 generalization top1=1.000 |
| Calibration ECE | chain-grade | ECE=0.017 (26.9x reduction) |

**Note:** Cell 3 (SEMANTIC v3 cv-tightening) was ruled MM by Skunkworks — saturation territory; A4 actually degraded with scale. v2 FULL is the definitive Stage 1 SEMANTIC ruling.

## Five barriers — current state

| Barrier | Status | Path forward |
|---|---|---|
| 1. Multi-hop ceiling at 0.65 | **OPEN** (Cell 4 was retracted; was by-construction) | Pointer-chain hybrid spec ready; consolidation v2 PROPER TEST spec ready |
| 2. Substrate-as-LM at bigram floor | **OPEN** | Role-tagged compgen on concept-KG (Cell 5; Wave F redispatched) |
| 3. Same-W stacking | **PARTIAL WIN** (cross-layer indep beats shared +0.376 BPC; MM not chain-grade per Skunkworks) | Lock-in frequency stacking (Cell 6; Wave F rerouted to CPU) tests temporal alternative |
| 4. Random-bipolar isotropic | **OPEN BUT REFRAMED** | Cell H' biology-native unsupervised shotgun (in flight authoring) — replaces label-driven path |
| 5. Audit-trail smear | **OPEN** | Cell E provenance-on-separate-freq spec ready (corollary of Barrier 3 lock-in if it works) |

## Three big findings from today (in addition to landings)

### Finding 1: Cell 4 "consolidation breakthrough" was by-construction (retracted)

K_THRESH=1 wrote answer-tuple directly into W as 1-hop atom; retrieval was recall not chain. NAIVE=0.847 in this cell vs 0.65 in last night's beta-sweep = chain-construction mismatch (not methodology drift). META_M4 + META_M5 atomized. Director over-claimed; Skunkworks correctly under-claimed (Fix #28 recurring). Consolidation v2 PROPER TEST spec written with K_THRESH>1 + held-out chains + matched chain-construction baseline.

### Finding 2: Anisotropy may HURT retrieval (Mu-Viswanath 2018 / Ethayarajh 2019)

Per Cell 7 deepened drill: anisotropy creates cone-collapse — similar items become indistinguishable in dominant directions. Substrate's primary task IS retrieval. **Label-driven encoder cone-collapse may be a red flag at ANY V, not just V=12.** Reinforces USER's basis-vs-use-case principle. Bias category P added to memory.

Open empirical question: does Mu-Viswanath apply to substrate's HRR sparse-bipolar regime, OR is it specific to learned contextual embeddings (BERT-style)? Cell H' shotgun is the empirical test: if all biology-native arms FAIL to beat random at V=4000, anisotropy-doesn't-help is confirmed for substrate; if some pass, anisotropy can help when constructed unsupervised.

### Finding 3: Cell 7 negative was just JL-oversatisfaction at V=12

At N/V=683 (33x JL minimum), random-bipolar is already at margin ~0.989. Subspace division by labels costs more than label structure helps. Cell 7 result is NOT a fundamental failure of engineered anisotropy — it's a wrong-scale test. But the deeper finding (anisotropy may hurt retrieval) suggests label-driven path is wrong anyway. Cell 7 v2 retest at V=4000 = DEPRIORITIZED in favor of Cell H' biology-native.

## Stage 2 cell specs ready for dispatch (all pre-authored; awaiting USER green-light)

| Spec | Barrier | Path | Priority |
|---|---|---|---|
| Cell H' biology-native unsupervised encoder | 4 | author IN FLIGHT (af9da6b05dc7c0a27) | HIGH — Stage 1.5 encoder commit |
| Consolidation v2 PROPER TEST | 1 | spec ready | HIGH — proper test of memory primitive |
| Pointer-chain hybrid multi-hop | 1 | spec ready | HIGH — alternate Barrier 1 path |
| Cell E provenance-on-separate-freq | 5 | spec ready | MEDIUM — depends on Cell 6 lock-in working |
| Cell G Cell 7 top1 re-eval | (Cell 7 retest) | spec ready | LOW — Skunkworks revival; cheap |
| Cell F cleanup+consolidation hybrid | 1 | superseded by consolidation v2 PROPER TEST | DROP |

## Wave F in flight (4 cells)

| Cell | Lane | Status (07:51Z) | ETA |
|---|---|---|---|
| 1 hub-spoke v3 MRC | GPU | RUNNING | ~2-3h |
| 2 heterog v3 full-config | GPU | PENDING | ~4-5h |
| 5 role-tagged compgen KG | remote CPU | RUNNING | ~1-2h |
| 6 lock-in freq stacking | remote CPU | PENDING | ~3-5h |

All 4 likely done by 14:00-16:00Z (early-to-mid afternoon).

## Key disciplines locked from today

- **Category M (production-scale instrument calibration)**: M1 raw-readout-at-T1 not as degeneracy signal; M2 tight-rail-from-different-config; M3 sign-sum bundle health check
- **Category N (Skunkworks 5-cell audit)**: N1 verify-referent-verdict-field; N2 Cramer-Rao-feasibility
- **Category O (USER basis-vs-use-case)**: O1 basis layer unsupervised; O2 use-case layer labels allowed; O3 declare layer per cell
- **Category P (anisotropy-hurts-retrieval per Mu-Viswanath)**: P1 label-driven encoders create cone-collapse; P2 monitor cosine-spread at retrieval; P3 test biology-native unsupervised BEFORE engineered anisotropy; P4 brain alignment (V1 unsupervised → IT labeled readout)

## Stage 2 dispatch sequencing (proposed)

**Wave G — post Wave F landings (3-5h from now):**
1. Cell H' biology-native shotgun (Barrier 4 commit)
2. Consolidation v2 PROPER TEST (Barrier 1 commit)
3. Pointer-chain hybrid (Barrier 1 alt)

**Wave H — after Wave G landings:**
4. Cell E provenance-on-separate-freq (Barrier 5; if Cell 6 lock-in HARD_PASSes)
5. Integration cell that combines best-of-Wave-G mechanisms

## Open strategic questions

1. **Mu-Viswanath applicability to substrate**: Cell H' tests empirically; if all arms fail, substrate-product wants LESS anisotropy not more
2. **Consolidation generalization**: Cell 4 v2 PROPER TEST resolves whether memory primitive genuinely closes Barrier 1
3. **Multi-hop ceiling at depth > 2**: even if 2-hop works, does K=5, K=10 hold? Cell H extended-depth spec ready
4. **Substrate-as-LM beyond bigram**: Cell 5 role-tagged on concept-KG tests role-filler generalization; if HARD_PASS, that's the first Stage 2 LM-side win
5. **Diverse-algorithm federation**: Cell 1 hub-spoke v3 MRC tests within-spoke encoder quality; if PASS, federation principle is validated; if FAIL/MIDDLE, Cell H' takes over the encoder lane

## Files of record

- `notes/director_5_intuitive_barriers_with_analogies_2026-06-25.md` — five barriers with analogies
- `notes/director_substrate_product_corpus_strategy_2026-06-25.md` — text8 wrong corpus; concept-KG right
- `notes/director_encoder_basis_vs_use_case_labels_2026-06-25.md` — USER's basis-vs-use-case principle
- `notes/director_cell_H_prime_biology_unsupervised_encoder_spec_2026-06-25.md` — Stage 1.5 encoder commit
- `notes/director_cell_consolidation_v2_proper_test_spec_2026-06-25.md` — proper memory primitive test
- `notes/director_barrier1_pointer_chain_multihop_cell_spec_2026-06-25.md` — alt Barrier 1 path
- `notes/research_optimal_anisotropic_encoder_construction_5x_drill_2026-06-25.md` — drill that identified D-prime
- `notes/research_cell7_label_driven_lost_random_2x_drill_2026-06-25.md` — Cell 7 negative drill
- `notes/research_biology_unsupervised_anisotropy_no_labels_3x_drill_2026-06-25.md` — biology mechanisms
- `notes/skunkworks_tier_ruling_cell3_cell4_consolidation_2026-06-25.md` — Cell 4 retraction
- `notes/skunkworks_tier_ruling_3cells_post_drill_2026-06-25.md` — yesterday's 3-cell audit
- `notes/director_CRITICAL_CONTEXT_PRECOMPACTION_2026-06-24.md` — survives compaction

## Net read of where we are

Stage 1 is solid: 8 chain-grade native capabilities + SEMANTIC battery proves substrate is the concept-learner. Stage 2 had two scares this morning (Cell 4 over-claim retracted; label-driven encoder lost to random) — but both were correctly diagnosed, and the strategic picture is cleaner now than yesterday:

- We know LABELS at basis = wrong (USER's principle + Mu-Viswanath + Cell 7 empirical)
- We know consolidation needs proper test (not K_THRESH=1 saturation)
- We know corpus choice matters (concept-KG for Stage 1/2; text8 only for architecture stress-testing)
- We have pre-authored specs for the next 5+ cells

Once Wave F lands (3-5h), we'll know:
- Does diverse-algorithm federation (hub-spoke v3 MRC) work? → if yes, Stage 1.5 encoder might be done
- Does role-tagged context on concept-KG let substrate generalize? → if yes, first Stage 2 LM-side win
- Does heterog routing transfer at full config? → if yes, validates v2_RESCUE finding
- Does lock-in frequency separation work on CPU? → if yes, Barrier 3 has temporal-separation alternative + Cell E provenance-on-freq unlocked

That's a substantial information landing in the next 3-5h.
