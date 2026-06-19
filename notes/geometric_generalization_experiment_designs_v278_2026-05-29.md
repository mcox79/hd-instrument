# Geometric generalization experiment designs (v278)

4 experiments testing Paths 1, 2, 3 from the geometric-generalization correction. Each cheap CPU-shippable.

## E1: Continuous-output INTERPOLATION test (Path 2 primary)

**Hypothesis**: W*k_query (pre-argmax continuous vector) encodes geometric interpolation between stored facts when query is between their keys.

**Setup**:
- N=4096, BSC codebook, M=8 anchor facts at known keys k_1..k_8
- Store pairs (k_i, v_i) with v_i chosen so that v_1, v_2, ..., v_8 lie on a known continuous manifold (e.g. v_i = i * direction)
- Query with interpolated keys: k_alpha = alpha*k_1 + (1-alpha)*k_2 for alpha in {0.1, 0.3, 0.5, 0.7, 0.9}
- Measure: continuous_output = W * k_alpha (NO argmax)
- Compare to expected interpolation: v_expected(alpha) = alpha*v_1 + (1-alpha)*v_2

**Metrics**:
- cosine(continuous_output, v_expected) per alpha
- Distance from continuous_output to nearest stored v_i (should be > 0 for alpha in middle)
- Distance from continuous_output to interpolation line (should be < 0.1 of |v_2 - v_1|)

**HARD_PASS**: mean cosine across 5 alpha values >= 0.7 AND interpolation-line distance <= 0.2
**HARD_FAIL**: mean cosine <= 0.3 OR continuous_output clamps to nearest discrete stored value

**Cost**: ~30min CPU at N=4096; smoke testable in 5min at N=512

**Anchor**: `geometric_interpolation_continuous_v1_n4096`

## E2: Vector arithmetic ("king - man + woman") test (Path 2 secondary)

**Hypothesis**: substrate's continuous output supports analogical reasoning via vector arithmetic if relationship dimensions are encoded geometrically.

**Setup**:
- Store 8-12 facts with explicit relational structure:
  - (k_A_male, v_A_role_X), (k_A_female, v_A_role_Y)
  - (k_B_male, v_B_role_X), (k_B_female, v_B_role_Y)
  - (k_C_male, v_C_role_X), (k_C_female, v_C_role_?? — unstored)
- Query: k_test = k_C_male + (k_A_female - k_A_male)
- Measure: continuous_output = W * k_test
- Expected: continuous_output should be close to v_C_role_Y geometrically

**Metrics**:
- cosine(continuous_output, v_C_role_Y_predicted)
- Argmax of (W * k_test) over codebook — does it pick v_C_role_Y? (Discrete check; less important)

**HARD_PASS**: continuous-vector cosine to expected analog >= 0.6 across 3 analogy classes
**HARD_FAIL**: cosine <= 0.2 (no analogical structure)
**MIDDLE_BAND**: 0.2 < cosine < 0.6 (partial structure; codebook design dependent)

**Cost**: ~45min CPU at N=4096

**Anchor**: `vector_arithmetic_analogy_v1_n4096`

## E3: Compositional binding NOVEL-QUERY test (Path 3)

**Hypothesis**: storing facts as (subject ⊗ predicate → value) lets novel (subject ⊗ predicate) compositions retrieve sensible values via geometric structure of binding algebra.

**Setup**:
- 4 subjects (A, B, C, D), 4 predicates (P1, P2, P3, P4) → 16 possible facts
- Store 12 of the 16 explicitly: train_facts = subject_i ⊗ predicate_j → value_{i,j}
- Hold out 4 facts: test_facts = (specific) subject ⊗ predicate combinations
- Query with held-out compositions; measure if substrate returns the held-out value via geometric structure

**Metrics**:
- Accuracy on held-out compositions (top-1 cosine to correct held-out value)
- Comparison to random-baseline (1/16) and to "average-of-stored" baseline

**HARD_PASS**: held-out accuracy >= 0.65 (beats random by 10x; beats "average" baseline by 3x)
**HARD_FAIL**: <= 0.25 (no compositional structure exploited)

**Cost**: ~30min CPU at N=4096

**Anchor**: `compositional_binding_novel_query_v1_n4096`

## E4: Soft readout with TEMPERATURE SCHEDULE (Path 1 — escapes QE-2 Option-1 saturation)

**Hypothesis**: soft readout fails at fixed high beta (QE-2 Option-1) but might succeed with a SCHEDULED temperature that prevents saturation at meaningful SNR.

**Setup**:
- Standard substrate with M=20 stored facts at N=4096 BSC
- For each query, sweep beta in {0.5, 1.0, 2.0, 4.0, 8.0, 16.0} — find beta_critical where softmax transitions from uniform to delta
- Measure if there's a beta_window where soft readout provides MEANINGFUL probability distribution (entropy > 1 nat but mass concentrated on top-k stored facts)
- Test interpolation queries (like E1) at beta in the meaningful window

**Metrics**:
- entropy(softmax(W*k_query / sqrt(beta))) as function of beta
- For interpolation queries at beta_critical: cosine(soft_output, v_expected)
- top-K coverage at beta_critical

**HARD_PASS**: meaningful beta window exists (>1 dex wide) AND interpolation cosine >= 0.6 in that window
**HARD_FAIL**: no beta window — either saturates to argmax or stays uniform across all beta tested

**Cost**: ~45min CPU at N=4096

**Anchor**: `soft_readout_temperature_schedule_v1_n4096`

## Ship sequence (cheapest-first)

1. **E1 (interpolation)** ~30min — cheapest; validates Path 2 core hypothesis
2. **E3 (compositional)** ~30min — validates Path 3 independently
3. **E4 (temperature schedule)** ~45min — final attempt at Path 1
4. **E2 (analogy)** ~45min — strongest Path 2 stress test; depends on E1 PASS

**Total CPU smoke time**: ~2.5h serial OR ~45min in parallel across 4 anchors. All ship to remote_cpu_queue.

## Branching tree

- **If E1 HARD_PASS** → Path 2 alive → ship `/retrieve_continuous` endpoint extension to hdlab_service (~half engineer-day) → validate on Pattern B integration demo
- **If E1 HARD_FAIL but E3 HARD_PASS** → Path 2 dead, Path 3 alive → compositional-binding becomes the primary generalization path
- **If E1 + E3 both HARD_FAIL but E4 HARD_PASS** → Paths 1+3 alive, soft-readout-with-schedule rescues coherent multi-hop too
- **If all 4 HARD_FAIL** → substrate's geometric generalization closes honestly → positioning locks at 10-property bundle (no generalization upside)

## Pre-commit gate alignment

These 4 experiments cost ~2.5h CPU total. They complement the 5-gate pre-commit sequence already filed (G1 J-L sanity, G2 multi-tenant isolation, G3 provable deletion, G4 compositional retrieval, G5 inference-time updates). Combined gate cost: still under $10K.

The geometric generalization question is highest-leverage AFTER J-L sanity (Property 4) lands, because J-L tests whether substrate atoms preserve LLM-internal-representation similarity (necessary for any continuous-output path to work with LLMs).

## Suggested order

1. **First thing tomorrow**: Property 4 J-L check (1hr CPU, already filed)
2. **If J-L PASS**: ship E1 + E3 + E4 in parallel (~45min)
3. **If E1 PASS**: ship E2 (~45min)
4. **Decision gate**: 1-2 days CPU work tells us if Path 2 / 3 / 1 are real
5. **If real**: extend Pattern B to test continuous-output substrate with Llama 3.1-8B (~half engineer-day)
6. **If not**: lock positioning at 10-property bundle + hybrid multi-hop

Total decision cycle: 3-4 days CPU + half-day engineering before the next strategic decision on Path 2 productization.
