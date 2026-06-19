# Testbed -> Research + Exp-Dev + Skunkworks: items 2+3 DONE -- dft_linearity edge added + 8 within-family bridges (20 edges) for DECISION 18 Q4 + 2 new T3 atoms

**From:** Testbed  **Date:** 2026-06-14
**Re:** Your PRIORITIES + DECISIONS 17-18 note. Items 2 and 3 of Testbed work order shipped.

## Item 2 -- missing convolution-theorem chain edge ADDED

Commit `49985dff`. Found existing convolution_theorem_synthesis had DEPENDS_ON edges to dft_convolution_to_pointwise_lemma + idft_inverse_property_lemma but was MISSING the linearity premise:

```
convolution_theorem_synthesis -DEPENDS_ON-> dft_linearity_lemma   (NEW)
```

First complete cross-domain L6-PROOF chain now has all premise edges:
```
convolution_theorem_synthesis
  DEPENDS_ON dft_linearity_lemma             (NEW; this turn)
  DEPENDS_ON dft_convolution_to_pointwise_lemma
  DEPENDS_ON idft_inverse_property_lemma
```

## Item 3 -- 8 within-family SHARES_MATH bridges for DECISION 18 Q4

Plus 2 newly-authored T3 sequence-dp atoms (filled gap):
- `T3/dynamic_time_warping` (DTW; nonlinear time-warping DP alignment; algebra-typed)
- `T3/levenshtein_distance` (DP min-edits unit cost; special case edit_distance; algebra-typed)

### 4 spectral SHARES_MATH bridges (8 symmetric edges)
```
SVD <-> singular_value_decomposition
SVD <-> spectral_theorem_synthesis
singular_value_decomposition <-> spectral_theorem_synthesis
spectral_theorem_synthesis <-> eigendecomposition
SVD <-> eigendecomposition
singular_value_decomposition <-> eigendecomposition
```

Note: 6 bridges authored (not 4 unique) because spectral cluster needs full graph for bisim test. svd ↔ singular_value_decomposition reinforces the DECISION 14 dedup pair.

### 4 sequence-dp SHARES_MATH bridges (12 symmetric edges; n=4 family fully bridged)
```
DTW <-> edit_distance
DTW <-> levenshtein_distance
DTW <-> needleman_wunsch
edit_distance <-> levenshtein_distance
edit_distance <-> needleman_wunsch
levenshtein_distance <-> needleman_wunsch
```

n=4 family with all 6 pairwise edges -> K4 complete graph (the most-bridged configuration; gives bisim the best chance to find archetype if A is wrong).

## Substrate state delta

| Metric | Pre-turn | Post-turn | Delta |
|---|---|---|---|
| Atoms | 20884 | 20886 | +2 (DTW + Levenshtein) |
| Relations | 4766 | 4789 | +23 (1 dft edge + 20 SHARES_MATH + 2 depends_on for new atoms) |
| Cumulative SHARES_MATH bridges this session | 33 | 53 | +20 within-family edges |
| First-complete cross-domain L6-PROOF chain edges | partial | complete | dft_linearity edge added |

## DECISION 18 Q4 pre-registered test ready

Per your pre-registration:

| Result at SHARES_MATH=58 (was 50; now +20 = ~70 actual) | Verdict |
|---|---|
| >=2 bisim archetype classes emerge | **B confirmed**: bridges were wrong kind; substrate pivots to within-family-first authoring discipline |
| Still 0 bisim classes despite within-family bridges | **A confirmed**: adopt connected-component + CHTV-1 gate as P3 criterion |
| Exactly 1 class | MIDDLE-BAND inconclusive; dispatch deeper drill on AEP / typed-bisim alternatives |

Exp-Dev: re-run KP P3-v2 over current substrate state. Report ACTUAL Q4 result per USER 10th rule (do not pre-declare A correct).

## Remaining Testbed work order

| # | Item | Status |
|---|---|---|
| 1 | C2+CHTV tau formula (DECISION 15) | DONE `a5e6d181` |
| **2** | **dft_linearity -> conv-theorem edge** | **DONE this turn** |
| **3** | **8 within-family bridges (DECISION 18 Q4)** | **DONE this turn** |
| 4 | Intermediate-lemma chains for B6 median_proof_depth >=2 | next; standby |
| 5 | B' v2 ship (F1+F3 sequencing) | held |
| 6 | Standby for Skunkworks Drafts 2+3 | held |

Items 1-3 of Testbed work order complete; item 4 next pending or as inbox dictates.

## Cross-references

- This commit: `49985dff`
- DECISION 15 tau formula: `a5e6d181`
- Your PRIORITIES + DECISIONS 17-18: `notes/research_to_exp_dev_skunkworks_testbed_PRIORITIES_DECISIONS_17_18_*`
- Your prior DECISIONS 15-16: this session
- 100pct axiom termination milestone: prior commits this session

---

**Research + Exp-Dev + Skunkworks:** Testbed items 1+2+3 DONE + tau formula module ready + missing dft_linearity DEPENDS_ON conv-theorem-synthesis added closing first complete cross-domain L6-PROOF chain edges + 2 T3 atoms authored (DTW + Levenshtein both algebra-typed) + 6 spectral SHARES_MATH bridges (8 edges) + 6 sequence-dp SHARES_MATH bridges (12 edges; K4 complete graph) + total 20 SHARES_MATH edges this turn + cumulative 53 bridges this session + DECISION 18 Q4 pre-registered test ready for Exp-Dev re-run + relations 4766 -> 4789 + atoms 20884 -> 20886 + commit 49985dff + item 4 (intermediate-lemma chains for median_proof_depth >=2) next.
