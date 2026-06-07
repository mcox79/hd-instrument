# Research -> Exp-Dev: Storage program supplement -- 3 Tier-A unconventional tests

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Storage unconventional 2x drill result.

Three additional Tier-A tests join the existing storage test program. All are pre-engineering
gating checks; if any fail the corresponding engineering path is dropped without time loss.

## 1. Predicate/fact ratio audit on real KB sample

Goal: scope the delta/template compression payoff.

Pick a representative customer KB sample (5K-10K facts). Count how many distinct predicate
patterns the facts share. If 5K facts share 50 patterns, ratio = 100, payoff is 5-20x.
If 5K facts share 4500 patterns (mostly unique), ratio = 1.1, payoff is negligible.

Estimated 30 minutes CPU. No model needed; pattern-matching on text or schema.

Decision: if ratio > 10, queue mechanism-2 engineering for v2 (2-4 weeks delta compression
implementation). If ratio < 3, drop mechanism 2 from the v2 plan.

## 2. Retrieval F1 vs N sweep

Goal: establish the N-reduction floor before committing the engineering for mechanism 7
(encoder distillation) or mechanism 1 (modern Hopfield).

Test substrate retrieval quality at N in {4096, 8192, 16384, 32768, 65536} on a 10K-fact
test set. Use current production write rule. Apply the multi-dimensional acceptance
criteria (retrieval F1, K-hop accuracy, KF-1 AUC, adversarial robustness).

Estimated 1-2 hours GPU smoke; 4-6 hours full.

Decision: identify the smallest N at which all multi-dim criteria stay above 95% of baseline.
That N becomes the target for encoder distillation work. If the floor is N=16384, then 4x W
reduction is achievable; if N=8192, 16x; if N=4096, 64x.

## 3. Exponential energy capacity at N=4096

Goal: test whether the modern Hopfield exponential energy function gives capacity
comparable to quadratic at smaller N.

Implement exponential-energy retrieval (Ramsauer 2020 attention formulation) on N=4096
substrate. Load M facts at varying M/N ratios. Measure capacity ceiling (the M/N at which
retrieval F1 drops below 0.7) vs the quadratic-energy baseline at same N.

Estimated 2 hours CPU. Reference: arxiv 2304.14964 (energy formulations) and Ramsauer 2020.

Decision: if exponential energy maintains alpha_c > 0.4 at N=4096, the modern Hopfield path
is viable and is the highest-leverage N-reduction mechanism. If alpha_c < 0.2, the path
closes; fall back to encoder distillation.

## Follow-on if test 3 passes

The Marchenko-Pastur flat-spectrum finding foreclosed low-rank decomposition under
quadratic energy. The exponential-energy write rule produces a different W. If it does NOT
have a flat spectrum, low-rank decomposition becomes viable again as a fourth orthogonal
reduction axis.

Diagnostic to run as a follow-on: measure the singular value spectrum of W produced by the
exponential-energy write rule at M/N=0.5. If the spectrum is non-flat, file a separate
note for low-rank decomposition rescue and we re-open Path F.

## Integration with existing storage program

Original test program: seven cells covering sparse-W validation at production N, 4-bit
quantization, lower-N substrate, source vector PCA, content-addressable keys, hybrid
sparse-key dense-value, pruning policies.

These three supplement cells run in PARALLEL with the original seven. They are not gated
on anything else. All use $0 of cloud budget.

Apply the same multi-dimensional acceptance criteria (audit + ZKL + K-hop + adversarial +
performance) from the supplement note already on file.

## Cross-references

- Storage 3x drill: notes/research_drill_storage_efficiency_per_fact_3x_2026-06-07.md
- Storage unconventional 2x drill: notes/research_drill_storage_unconventional_mechanisms_2x_2026-06-07.md
- Original test program: notes/research_to_exp_dev_storage_efficiency_test_program_2026-06-07.md
- Multi-dim criteria supplement: notes/research_to_exp_dev_storage_test_multidim_criteria_2026-06-07.md

---

**END.**

**Exp-Dev:** add these three cells to the storage test program as Tier-A priority.
Multi-dim acceptance criteria apply.
