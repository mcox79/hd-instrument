# Prereg — K8 Hierarchical concepts (concepts-of-concepts) — local CPU scoping

**Anchor**: `wave14_k8_hierarchical_concepts_v1`
**Queue**: local_cpu_queue (sub-minute scoping per Tier C)
**Filed**: 2026-05-24 by exp_dev

## Hypothesis

K8 KILLER Tier-3 untested. R3 (hierarchical) closed at K>=16 but the
structural test of CONCEPT-OF-CONCEPTS (a 2-level hierarchy where top concept
is bundle-of-mid-concepts which are themselves bundle-of-atoms) has not been
probed at substrate level. This is a LOCAL CPU SCOPING probe to decide
whether a GPU envelope-expansion probe is warranted.

## Pre-registered falsifiers (BEFORE FULL run)

- **HARD-PASS**: 2-level recall cosine >= 0.30 AND >= 3x chance baseline
  across 5 seeds. -> K8 has hierarchical structure; warrants GPU expansion.
- **HARD-FAIL**: 2-level recall cosine < 0.05 OR < 1.5x chance baseline.
  -> K8 KILLER at substrate level; aligned with R3 closure.
- **MIDDLE-BAND**: any intermediate.

## Parameters (exp_dev autonomy)

- N = 1024 (single-config; this is scoping)
- N atoms per mid = 4
- N mids = 4
- N queries = 30
- Seeds = {7, 17, 23, 31, 41}

## ETA

Local CPU FULL ~30-60s.

## Smoke outcome

Smoke single-seed: 2level_cos=0.048 ratio=1.53x chance -> HARD_FAIL borderline.
Multi-seed FULL is structurally same envelope at this Tier-C scoping level.
