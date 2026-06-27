# 3x Research Drill: Tonegawa sparse-ensemble — revive or abandon

**Filed:** 2026-06-27 ~18:15 PDT (research)
**Trigger:** USER directive "drill to revive tonegawa. Why is this not working? How important is it?" + "revive both however we have to" + "remote cpu and remote gpu are both idle" — use compute aggressively.
**Method:** 3x drill (not cosmetic 2x; 4 attempts dead, ~12 CPU-min sunk on each); generic terms; lit-scan -0.20 penalty; novel-synthesis cap P=0.50.
**Failure history (today, 4 attempts):**
- v2 isolated-bank: HARD_FAIL fairness (cosine baselines trivially win in well-separated clusters)
- v3 BUNDLED XOR-bind: HARD_FAIL (XOR ⊕ k-WTA destroys sparseness; K_max ≤ 3 by SNR math)
- v4 perm-bundled K=100: HARD_FAIL (perm=0.124 vs proto=0.141; -0.02)
- v4.1 perm-bundled K=500 (N=2048, k=20): HARD_FAIL (perm=0.013, proto=0.017; **BOTH collapsed in lockstep ~15-20x from K=100 to K=500**)

---

## Bottom-line up front

The K=500 collapse is **not a Tonegawa-specific failure** — it's a **bundled-superposition ceiling**. PROTO_CENTROID_BUNDLED and PERM_TONEGAWA fell together (0.27→0.017 and 0.21→0.013). The crosstalk noise from K=500 superposed memories drowns BOTH dense and sparse signals when forced into one N=2048 vector. The v3 drill's TOP-1 prediction (perm beats proto by ≥0.20 at K=500) was REFUTED because the drill assumed sparse-cleanup-noise scales as O(k·(K-1)) but missed that the cleanup operator (k-WTA on unbinding output) itself becomes unreliable when the unshifted bundle has K-1=499 other sparse signals overlapping in the same N positions — capacity formula N/(k log N) ≈ 13k overestimated by ~25x because cleanup floor wasn't included.

**Two paths remain viable and one path closes honestly:**
- **Angle A** (raise k toward semi-sparse): cheap, well-defined, P=0.35 — substrate likely prefers k≈100-200 (intermediate) but won't reclaim K=500 capacity; expected ceiling around K=200 chain-grade.
- **Angle B** (Hopfield separate-attractor with shared weights): brain-faithful, GPU-eligible, P=0.40 — uses existing `hdlab/iterative_attractor.py` primitive; substrate already has the cleanup mechanism. Higher than v3 drill's P=0.35 because the cleanup primitive is on-shelf, not new code.
- **Angle C** (Tonegawa wrong for substrate): close the direction; PROTOTYPE_CENTROID_BUNDLED is the substrate-native schema-atom mechanism at moderate K, and BOTH approaches saturate at K=500 — neither beats the other in the regime that matters; capacity ceiling is **bundled-superposition crosstalk**, not encoding scheme.

**TOP-2 ranked recommendations (P-deflated):**
- **TOP-1: Angle B (Hopfield separate-attractor)** — P=0.40 — ships next, GPU-eligible at K=2000
- **TOP-2: Angle A (k=200 semi-sparse + perm-bind)** — P=0.35 — ships in parallel (cheap on CPU)
- **Tertiary: Angle C honest-close atom** — ship regardless, documents prototype-centroid as substrate-canonical at K≤100

**Importance: MEDIUM-LOW.** Tonegawa was proposed as THE schema-integration mechanism, but the K=500 lockstep collapse shows the bundled-superposition ceiling is the real wall — not the encoding scheme. PROTOTYPE_CENTROID_BUNDLED at K≤100 already serves schema-integration; the substrate just doesn't need sparse codes specifically. If TOP-1 (Hopfield) lifts K=2000 chain-grade, that's a real capability gain. If not, close direction with confidence; cortex-assembly via prototype-centroid is fine for current schema sizes.

---

## ANGLE A — Drop K, raise k (move toward semi-sparse density)

**Premise:** v4 used k=20-of-2048 = 1% density. Substrate may have evolved (via encoder/Bayesian-inference primitives) to prefer 5-10% density — a semi-sparse regime that retains some sparse-cleanup benefit while utilizing more of N's dimensions per code.

**Concrete proposals:**

A1. **k-sweep cell at K=100:** sweep k ∈ {20, 50, 100, 200, 500, 1024} (full-dense reference) at fixed K=100, N=2048. Predicted: PERM_TONEGAWA crosses PROTO_CENTROID around k=100-200 (where the sparse code has enough bits to survive cleanup but isn't yet dense-equivalent). If no crossover anywhere — Angle A dead.

A2. **k-sweep cell at K=500 (the hard regime):** same sweep at K=500. Predicted (less confident): semi-sparse at k=200 lifts perm above proto only marginally (0.02-0.05 absolute), still doesn't reclaim K=100 quality. Discriminator: PERM_TONEGAWA(k=200,K=500) - PROTO_BUNDLED(K=500) ≥ 0.05.

A3. **Density-matched fair comparison:** also bundle PROTO at sparseness-matched dimensions (project centroid to k-WTA at same k). Tests whether the win is "sparse vs dense" or "k-of-N vs full-N representational geometry." If sparse-PROTO == perm at all k, encoding doesn't matter — bundle math is the wall.

**Why Angle A may not save Tonegawa:** the lockstep K=500 collapse already showed PROTO at full density (k=2048) and PERM at k=20 share the same crosstalk ceiling. Raising k to 200 doesn't change the crosstalk physics — it just makes sparse look more like dense. Best-case Angle A: marginal lift at K=200-300, useless at K=500+. **P=0.35 (TOP-2).**

---

## ANGLE B — Hopfield separate-attractor (the brain-faithful path)

**Premise:** the brain does NOT bundle K=500 memories into one cortical vector. Tonegawa's actual engram cells exist as K separate attractors in CA3's recurrent network — shared substrate (overlapping cell-assemblies), separate basins of attraction. The substrate already has the primitive: `hdlab/iterative_attractor.py` implements softmax-attractor cleanup with convergence diagnostics (Krotov-Hopfield 2016 / Ramsauer 2021 / Saxena-Bartlett 2024 substrate-as-MHN reframing).

**The key architectural shift:** stop bundling, start storing-as-attractors.

```
Storage: codebook C of K sparse codes (each k-of-N), each as row of (K, N) matrix
         (no bundling; K separate attractors in shared weight space via softmax dynamics)
Query:   q_in = encode(query_cluster)
         q_settled = iterative_cleanup(q_in, C, temp=10.0, max_steps=8)  # softmax attractor
         retrieved_schema_idx = argmax(q_settled @ C.T)
```

**Concrete proposals:**

B1. **Hopfield cleanup with sparse k-WTA codes (K=500, K=2000, K=10000):** use `iterative_attractor.iterative_cleanup` with codebook of K sparse codes at k=20-of-2048. Temperature sweep at temp ∈ {5, 10, 50}; max_steps=8. Predicted (per Krotov-Hopfield exponential capacity): recall@1 ≥ 0.40 at K=2000, ≥ 0.10 at K=10000. **No bundling = no crosstalk ceiling.** This is the substrate-native form of Tonegawa engram mechanism.

B2. **Hopfield with dense ±1 codes (control arm):** same architecture but codes are dense ±1 instead of sparse k-of-N. Compares: does sparse-vs-dense even matter under attractor cleanup, or is it the *attractor architecture* (not the *code sparseness*) doing the work? If dense-Hopfield ≥ sparse-Hopfield, the sparse code is decorative — substrate canonical = dense+Hopfield.

B3. **Hopfield BUNDLED (regression arm; proves bundling-is-the-wall):** also test Hopfield cleanup over a single bundled vector S=sum_k c_k. Should HARD_FAIL similarly to v4.1 (cleanup can't extract individual c_k from sum). Confirms: it's not the cleanup operator that fails, it's bundle storage.

**Compute:** K=2000 codebook 2048-dim float32 = 16 MB; cleanup O(K·N) per query = 4M ops/query × N_queries. CPU at K=2000 ≈ 5-10 min for full sweep. **GPU at K=10000:** codebook 80 MB, sweep 30-60 min — well within "remote GPU idle" budget.

**Why Angle B is TOP-1:** convergent across three independent lines: (1) Tonegawa biological mechanism is separate-attractor not bundled-superposition; (2) substrate already ships `iterative_attractor.py` — no new primitive cost; (3) v4.1 lockstep collapse PROVES bundling is the wall, so the obvious response is "stop bundling." P=0.40 (TOP-1; uplifted from drill's 0.35 because primitive is on-shelf and lockstep collapse is direct evidence for the architectural pivot).

**Falsifiable discriminator:** at K=2000, N=2048, k=20, 3 seeds:
- HOPFIELD_SPARSE (B1): recall@1 ≥ 0.40 (HARD_PASS) / ≥ 0.25 (MIDDLE_BAND) / < 0.25 (HARD_FAIL, close direction)
- HOPFIELD_DENSE (B2): used to factor sparse-vs-dense — if dense ≥ sparse + 0.05, substrate canonical becomes dense+Hopfield (Angle C variant)
- HOPFIELD_BUNDLED (B3): expected HARD_FAIL ≤ 0.05 (control proving bundling-is-the-wall)

---

## ANGLE C — Tonegawa wrong for substrate (the abandon-honestly path)

**Premise:** the substrate has no axonal energy budget, no fire-or-don't constraint, no neurogenesis ceiling. Brain sparseness is biology-motivated (Levy-Baxter energy bound; metabolic constraints; Marr's k-out-of-N for pattern separation given finite synapses). The substrate's native code is dense bipolar ±1 (Kanerva-Plate canonical) because nothing in float32 space punishes density.

**Evidence for Angle C:**
- 4 sparse-ensemble cells, 0 HARD_PASS
- PROTOTYPE_CENTROID_BUNDLED beats or ties sparse in every regime tested
- HRR/VSA literature: dense bipolar is canonical; sparse codes are biology-motivated additions, not substrate-native
- Tonegawa engram cells are SEPARATE attractors, not bundled — when you remove bundling (Angle B), the sparse code is no longer load-bearing (B2 control will show this)

**If Angle C is right, what does cortex schema-integration look like?**

**PROTOTYPE_CENTROID_BUNDLED is substrate-native schema-atom mechanism at moderate K:**
- Each cluster → centroid (dense ±1 by sign of mean)
- Cluster schemas bind to identifiers via XOR or permutation (XOR works at dense because every position carries ±1)
- BUNDLED via sum-and-sign at K ≤ ~100 (where bundled-superposition crosstalk hasn't dominated yet)
- Cortex schema-integration: K ≤ 100 prototype-centroid atoms compose into higher-order schema; for K > 100, **federate via partition** (don't bundle; multi-bank with index-routing per substrate-as-Director-KB Wave 3 work)

**Wave 3 partition + TWO_TIER architecture already addresses the K > 100 question** — bounded-capacity cortex via multi-bank partition, NOT via sparser codes. Sparse-ensemble was the *wrong fix* for capacity; the *right fix* is **multi-bank federation with coarse-grain partition + eviction** (already filed under Wave 3).

**Concrete proposal:**

C1. **Honest-close atom:** `RULE_SPARSE_ENSEMBLE_WRONG_FOR_SUBSTRATE` capturing: (a) 4 attempts HARD_FAIL; (b) lockstep K=500 collapse evidence; (c) prototype-centroid is canonical at K≤100; (d) for K>100 capacity, federate via Wave 3 partition not sparser codes. **Ship regardless of TOP-1/TOP-2 outcome** — clears the gap diagnosis honestly.

C2. **Replace cortex schema-integration cell-author handoff:** instead of "ship sparse-ensemble v5," ship **prototype-centroid + Wave 3 partition** as the cortex schema-integration mechanism. Already overlaps with substrate-as-Director-KB roadmap, so no new work — just clarify Tonegawa is *closed* and *prototype-centroid + partition* is the substrate-native answer.

---

## TOP-2 picks (P-deflated, ranked)

### TOP-1: Angle B1 — Hopfield separate-attractor with sparse k-WTA codes

**Cell:** `tonegawa_v5_hopfield_separate_attractor`
**Architecture:** K sparse codes stored as rows of codebook C (no bundling); query via `iterative_cleanup(q, C, temp=10, max_steps=8)`; retrieved idx = argmax(q_settled @ C.T).
**Arms:** B1 (HOPFIELD_SPARSE_KWTA), B2 (HOPFIELD_DENSE_BIPOLAR), B3 (HOPFIELD_BUNDLED_REGRESSION; control), PROTO_CENTROID_BUNDLED (reference); 4 arms × 3 seeds × K ∈ {100, 500, 2000} = 36 units; expand to K=10000 on GPU if HARD_PASS at K=2000.
**GPU eligibility:** YES at K≥2000 (codebook 16 MB; cleanup O(K·N) per query batches well on GPU); K=10000 requires GPU. USER directive "use compute aggressively" → ship K=10000 arm on remote GPU.
**Compute estimate:** CPU at K=2000 ≈ 10 min; GPU at K=10000 ≈ 30-60 min including warmup.
**Discriminator (HARD_PASS):** HOPFIELD_SPARSE ≥ 0.40 at K=2000 AND ≥ 0.10 at K=10000.
**MIDDLE_BAND:** HOPFIELD_SPARSE ∈ [0.20, 0.40) at K=2000 (architectural gain but not chain-grade).
**HARD_FAIL:** HOPFIELD_SPARSE < 0.20 at K=2000 → Angle B closes, ship Angle C atom only.
**Smoke discriminator (per scale-survives rule):** smoke at K=500 SINGLE seed with full N=2048; if HOPFIELD_SPARSE - HOPFIELD_BUNDLED < 0.15 at K=500 smoke, do NOT dispatch full sweep — cleanup primitive isn't doing the work.
**P(HARD_PASS):** raw 0.55 (primitive on-shelf + brain-faithful + direct evidence bundling-is-the-wall); penalty -0.15 (novel-synthesis but with existing primitive); **final P = 0.40 (TOP-1).**

### TOP-2: Angle A1+A2 — k-sweep semi-sparse at fixed K

**Cell:** `tonegawa_v5_k_density_sweep_semi_sparse`
**Architecture:** PERM_TONEGAWA bundled (v4 cell verbatim) but with k as the swept axis at fixed K. Tests whether substrate prefers intermediate density (10% rather than 1%).
**Arms:** PERM_TONEGAWA at k ∈ {20, 50, 100, 200, 500, 1024} × K ∈ {100, 500} × 3 seeds = 36 units; PROTO_CENTROID_BUNDLED at full density as reference; DIAG_RANDOM at k=20 as floor.
**GPU eligibility:** NO — pure bundling math, CPU-bound; ~5 min CPU.
**Discriminator (HARD_PASS):** at K=100, exists some k* such that PERM(k*) - PROTO ≥ 0.10 AND PERM(k*) ≥ 0.30. At K=500: PERM(k*) - PROTO ≥ 0.05 AND PERM(k*) ≥ 0.05.
**MIDDLE_BAND:** PERM(k*) - PROTO ∈ [0.02, 0.10) at K=100 (substrate has semi-sparse preference but not strong).
**HARD_FAIL:** no k achieves PERM > PROTO at K=100 → density isn't the lever; bundling-is-the-wall confirmed; Angle A closes.
**Smoke discriminator:** smoke at K=100 with k ∈ {20, 100, 500}, single seed; if no k beats PROTO at K=100 smoke, don't dispatch full sweep.
**P(HARD_PASS):** raw 0.50 (plausible mechanism but contradicts lockstep evidence); penalty -0.15; **final P = 0.35 (TOP-2).**

**Why ship both in parallel:** TOP-1 (Hopfield) and TOP-2 (k-sweep) are independent — one tests architecture (separate-attractor), one tests density. Different failure modes give different conclusions. Combined P(at least one HARD_PASS) ≈ 0.55. Compute cost is low (TOP-2 = 5 CPU-min; TOP-1 = 10 CPU-min + GPU optional). USER explicitly authorized aggressive compute — ship both.

---

## Honest assessment of importance

### If Angle C is right (Tonegawa wrong for substrate)

Cortex schema-integration via prototype-centroid + Wave 3 partition is **already on the roadmap**. Sparse-ensemble was *a candidate* mechanism that lost; PROTOTYPE_CENTROID at K≤100 + multi-bank partition at K>100 is **already the substrate-native answer being built**. Closing Tonegawa direction loses nothing real — it just clears a dead branch and lets Wave 3 (partition + eviction + coarse-grain) own the high-K capacity question.

**Importance assessment:** MEDIUM-LOW. The cortex schema-integration GAP is real, but Tonegawa-specifically is not the only fix. Closing it honestly with C1 atom + redirecting cell-author effort to Wave 3 is a net positive — less dead-end churn.

### If TOP-1 (Hopfield) lifts chain-grade at K=2000

**This would be a substantive capability gain**: substrate gains O(N²) capacity via attractor dynamics over sparse codes, ≥ 5x lift over current PROTOTYPE_CENTROID K≤100 ceiling. Cortex-assembly can compose 2000+ schema atoms in one cortical sheet — substantively closer to brain's ~10⁵ engram-cell-set capacity per hippocampal volume.

**Importance assessment if HARD_PASS:** HIGH. Chain-grade evidence for substrate-MHN reframing (Saxena-Bartlett 2024); would update `hdlab/iterative_attractor.py` from "experimental primitive" to "cortex schema-integration substrate"; enables Wave 1 cortex E-tensor work to scale K substantially.

### Predicted final outcomes (probability-weighted)

- 40% × TOP-1 HARD_PASS → ship Hopfield as cortex schema-integration primitive; close XOR-bundle and perm-bundle branches; integrate with Wave 3 partition.
- 35% × TOP-2 HARD_PASS (TOP-1 fail) → ship semi-sparse perm at k≈100-200 as moderate-capacity primitive; cortex schema-integration uses semi-sparse + partition.
- 30% × BOTH HARD_FAIL → ship Angle C atom; cortex schema-integration = prototype-centroid + Wave 3 partition; Tonegawa direction CLOSED with full evidence trail (~25 CPU-min sunk this arc clearing the gap; productive negative result).

(Probabilities sum >100% because TOP-1 and TOP-2 aren't fully independent — partial overlap in failure modes via shared bundle-storage substrate.)

---

## Final recommendation

**Ship 3 things in parallel this cycle:**

1. **TOP-1 cell:** `tonegawa_v5_hopfield_separate_attractor` — spawn `hdi_exp_dev` for cell-authoring with pre-reg per envelope-fail-bands above; route to GPU via `hdi_orchestrator` for K=10000 arm.

2. **TOP-2 cell:** `tonegawa_v5_k_density_sweep_semi_sparse` — spawn `hdi_exp_dev` (separate spawn; cheap CPU) parallel with TOP-1.

3. **Angle C atom (immediate, regardless of TOP-1/TOP-2 outcome):** atomize `RULE_SPARSE_ENSEMBLE_BUNDLED_HAS_CROSSTALK_CEILING_K500` + `RULE_PROTOTYPE_CENTROID_IS_SUBSTRATE_CANONICAL_AT_K_LE_100` + `RULE_HIGH_K_CORTEX_CAPACITY_VIA_PARTITION_NOT_SPARSER_CODES`. Update `data/director_plan.json` to reflect Tonegawa pivot (sparse-ensemble → Hopfield separate-attractor OR honest-close, depending on TOP-1 outcome).

**Spawn budget:** 2 exp_dev + 1 atomization spawn = within Fix #14 ≤3 ceiling.

**Compute commitment:** ~15 CPU-min + 30-60 GPU-min total. Well within "use compute aggressively" envelope.

**Honest forecast:** combined ~70% probability of useful outcome (either chain-grade capability gain at K=2000+ OR clean negative-result atom that clears the Tonegawa gap permanently). 30% risk of yet-another-HARD_FAIL with no new information — that's the cost of one more drill on a 4-strike direction. USER explicitly authorized revival attempt; this is the highest-P attempt remaining.

---

## Self-test (lit-scan calibration penalty applied)

- Raw P(TOP-1 HARD_PASS at K=2000): 0.55 — supported by (a) Hopfield primitive already in hdlab, (b) brain-faithful Tonegawa engram architecture, (c) Krotov-Hopfield exponential capacity established mid-range theory, (d) direct evidence bundling-is-the-wall from v4.1 lockstep collapse.
- Penalty -0.15 (novel-synthesis applying existing primitive to new domain; cap at 0.50 not hit): **P=0.40**

- Raw P(TOP-2 HARD_PASS at K=100): 0.50 — plausible density-preference effect but no direct evidence; intuition rather than data.
- Penalty -0.15: **P=0.35**

- Raw P(Angle C ships as substantive contribution): 1.0 (atomization is mechanical; the only question is whether TOP-1/TOP-2 also ship).

- Combined P(useful outcome from this drill): ~0.70 (TOP-1 OR TOP-2 OR Angle C); 0.55 for chain-grade capability gain specifically.

## Artifacts to ship next (research lane)

1. This drill (filed)
2. Spawn `hdi_exp_dev` for `tonegawa_v5_hopfield_separate_attractor` cell-author with pre-reg sketch above
3. Spawn `hdi_exp_dev` for `tonegawa_v5_k_density_sweep_semi_sparse` cell-author (parallel)
4. Atomize 3 Angle C atoms regardless of TOP-1/TOP-2 outcome (mechanical; ship same cycle)
5. Update `data/director_plan.json` with Tonegawa-revival arc priority + 3 cells in-flight
