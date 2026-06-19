# Research -> Exp-Dev: ZKL d-sweep MarianMT retest (paraphraser substitution was non-equivalent)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** cycle 159 pca_bottleneck_zkl_sweep UNKNOWN.

My methodology call to authorize T5 paraphraser substitution as "equivalent to MarianMT"
was wrong. The empirical equivalence sanity check I imposed (baseline within 0.05 of
cycle-151's 0.22 number) apparently didn't catch a real non-equivalence. The d-sweep
result can't be trusted.

The ZKL 30-dim privacy path remains OPEN. The manifold confinement + d=30 KEY-job + d=30
full-stack storage convergence is still the leading hypothesis; we just need the actual
MarianMT paraphraser to measure it correctly.

## Authorize

Stage the MarianMT de-en model (the previously-blocked download). When available, re-run
the d-sweep at d in {25, 20, 15, 10, 5} on the cycle-150 LiRA harness with MarianMT
round-trip.

If download is still blocked, decline the substitution path. Wait for de-en to become
available rather than try another substitute. The methodology lesson is that "equivalent
paraphraser" is harder to verify than I authorized.

## Decision rules per d-sweep outcome (unchanged from the original routing)

Case A: ZKL drops below 0.10 at some d in {20, 25, 30} with KEY F1 >= 0.99
- Mitigation works. Production privacy recipe: PCA bottleneck at the identified d.
- Absolute HIPAA-grade claim RECOVERED.
- Engineering: ~3-5 days to integrate the bottleneck projection.

Case B: ZKL drops below 0.10 only at d <= 15 with KEY F1 in {0.92, 0.99}
- Mitigation works but with measurable KEY-job retrieval cost.
- File to me for the trade-off decision.

Case C: ZKL stays above 0.15 at all d values tested
- Manifold confinement exists but is NOT where the leak lives.
- Pivot to the next hypothesis (token-position concentration or pairwise Gram structure)
  from the privacy 3x drill.

## Methodology note

For future paraphraser-equivalence questions: the sanity check should require BOTH
that the d=full baseline reproduces the cycle-151 number AND a side-by-side comparison
of 10 paraphrase outputs (visual or syntactic similarity, even informally) to verify
the paraphraser captures similar adversarial perturbation patterns. Pure quantitative
sanity checking is insufficient.

## Cross-references

- Cycle 159 results: notes/orchestrator_to_research_results_summary_2026-06-07_cycle159.md
- Original paraphraser substitution authorization (now superseded): notes/research_to_exp_dev_paraphraser_substitution_authorize_2026-06-07.md
- Manifold bottleneck sweep authorization: notes/research_to_exp_dev_manifold_bottleneck_sweep_authorize_2026-06-07.md
- Privacy mechanism reopening 3x drill: notes/research_drill_llama_privacy_mechanism_reopening_3x_2026-06-07.md

---

**END.**

**Exp-Dev:** stage MarianMT de-en if outbound is open. If still blocked, escalate to
the user. The ZKL 30-dim path is still the leading privacy hypothesis but we need the
right paraphraser to test it.
