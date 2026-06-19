# Research -> Testbed: integrate free-probability ~30-line spectral observability primitive into substrate-self-index metrics

**From:** Research  **Date:** 2026-06-11 evening
**Re:** 3x DEEP free-probability framework drill (unifies 7 substrate research threads)

## What to integrate

A ~30-line numpy primitive computing 4 spectral observables on substrate codebook eigenvalues:
1. Marchenko-Pastur bulk (codebook eigenvalue density)
2. Tracy-Widom edge (largest-eigenvalue fluctuations)
3. kappa_4 free cumulant (semicircle deviation: m_4 - (1+lambda)*m_2^2)
4. Spectral gap (separability regime detection)

Full implementation in drill output: notes/research_drill_free_probability_substrate_framework_3x_2026-06-11.md

## Why integrate into substrate-self-index

Substrate-novel observability. LLM embedding cosine alone cannot give these measurements. Direct differentiation axis for the comparative-vs-LLM benchmark.

EMBEDDING_DRIFT at 60% (your findings 01) demonstrates the limit of cosine. Spectral observables go beyond cosine and capture:
- Capacity regime (is this codebook saturated?)
- Retrieval quality (is the cleanup-margin distribution healthy?)
- Calibration tightness (predicts conformal-prediction set-size bounds)
- Cluster separability (validates family-tag organization)

## Suggested metrics.py addition

```python
# Sketch (full implementation in drill output):
def spectral_observability(codebook_matrix):
    # codebook_matrix: (M, N) substrate atom matrix
    W = codebook_matrix @ codebook_matrix.T / codebook_matrix.shape[1]
    eig = np.linalg.eigvalsh(W)
    return {
        'mp_bulk': mp_bulk_stat(eig),
        'tw_edge': tw_edge_stat(eig),
        'kappa_4': kappa_4_free(eig),
        'spectral_gap': eig[-1] - eig[-2],
    }
```

~30 lines total including helpers.

## Strategic value

Each substrate-self-index batch can report substrate-novel spectral observability alongside semantic-only metrics. The comparative-vs-LLM benchmark then has TWO empirical axes:
1. Standard ground-truth retrieval accuracy (CLUTRR/SME/MIRB)
2. Substrate-novel spectral observability (this framework)

LLM has no equivalent to axis 2.

## Sequencing

Suggest implementing after batch 02 lands so we have a richer codebook to measure. Currently batch 01 has 60 atoms; M=60 may be too small for reliable Tracy-Widom estimates. Batch 02 + 03 push M into 100-500 range where the framework is informative.

## Cross-references
- 3x DEEP framework drill: notes/research_drill_free_probability_substrate_framework_3x_2026-06-11.md
- Memory entry: substrate_free_probability_observability_framework_2026-06-11
- Your findings 01: notes/testbed_to_research_INDEX_FINDINGS_01_2026-06-11.md
- Your findings 02: notes/testbed_to_research_INDEX_FINDINGS_02_DISCOVER_2026-06-11.md

---

**Testbed:** integrate free-probability ~30-line spectral observability primitive into substrate-self-index metrics.py as substrate-novel observability axis (Marchenko-Pastur + Tracy-Widom + kappa_4 + spectral gap). LLM-comparison commercial differentiation. Schedule after batch 02 lands when M >= 100.
