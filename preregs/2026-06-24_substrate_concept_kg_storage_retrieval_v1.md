# Pre-registration: substrate_concept_kg_storage_retrieval_v1

**Date:** 2026-06-24
**Anchor:** substrate_concept_kg_storage_retrieval_v1
**Queue:** local_cpu_queue
**N:** 8192, **Seeds:** [7, 17, 23], **V_concepts:** 200, **V_predicates:** 10

## Scientific question

Per USER reframe 2026-06-24: stop testing the substrate as a statistical LM. Test it as a MEMORY +
COMPOSITION + RETRIEVAL device. If we teach the substrate explicit concepts via knowledge-graph triples
(synthetic, no encoder), does substrate-native HRR storage + chain-bind + analogical generalization
clear absolute substrate-native floors (NOT vs a transformer; against chance baselines)? Four arms:
1-hop recall capacity, 2-hop chained retrieval, generalization to heldout queries on a learned
predicate (PRIMARY), and storage capacity-vs-M.

## Pre-registered bands

**HARD-PASS** (all 4 arms must pass; per-seed cv reported):
- ARM_STORE_RECALL_1HOP: mean top1 >= 0.95 at M=500 (chance = 1/200 = 0.005)
- ARM_STORE_RECALL_2HOP: mean chained-top1 >= 0.80 (chance = 1/200 = 0.005); the substrate must
  chain-bind using its OWN inferred intermediate (NOT ground-truth-x oracle)
- ARM_GENERALIZATION_HELDOUT (PRIMARY): mean trained_top5 >= 0.50 AND sanity_floor_pass on ALL
  seeds (substrate must NOT recover taught association under a NEVER-taught predicate; untaught_top1
  < 0.10 + untaught_top5 < 0.10)
- ARM_CAPACITY_VS_M: minimum-across-seeds m_capacity_at_95pct >= 1500 (the substrate must hold at
  least 1500 facts at 95% recall on the M-grid {100, 500, 1000, 2000, 5000})

**MIDDLE:** 2 or 3 of the 4 arms PASS (per-arm pre-reg floors; rest fail). Reported per-arm
PASS/FAIL flags in verdict.

**HARD-FAIL:** fewer than 2 arms PASS.

## Calibration rationale

These are substrate-native ABSOLUTE floors per USER's Lane-1 framework — not ratio-to-transformer or
ratio-to-baseline bands (the latter are gameable; the phase_d_tier6 lesson). Chosen for what the
substrate SHOULD do as a memory device, given the proven U1 primitives:

- ARM_1 floor 0.95: U1 demonstrated set-recall ~0.99 at M=50k on FB15k-237 with N=8192. At M=500 on
  V_C=200 with N=8192 (much smaller key space, same primitive), top1 should be near-perfect.
- ARM_2 floor 0.80: chained substrate inference compounds error per hop. A 0.80 floor means the
  substrate's hop1 must succeed (~95%) AND its hop2-with-its-own-hop1-result must succeed (~85%),
  giving ~0.80 product. Below this is meaningfully weak chain-binding.
- ARM_3 floor 0.50 on top-5 (PRIMARY): the brain-like test. Substrate must recover the TAUGHT
  deterministic mapping (B_f(i)) for trained subjects under top-5; AND must not hallucinate under a
  never-seen predicate (sanity-floor). 0.50 top-5 is substantively above chance (0.025) but allows
  for top-5 noise; the sanity-floor is a hard zero-shot test the substrate gates correctly.
- ARM_4 floor M=1500: 7.5× the V_concepts=200 (so storage > V) demonstrates true superposition;
  below 1500 is not a substantively-capable substrate at this V_C.

## N-suffix section

Anchor name has no `_n<N>` suffix; PROT-018 does not apply. Production N = 8192 set as
`N_DIM = 8192` in the script (full mode). Smoke mode uses N_DIM = 1024 for fast verification.

## Timeout estimate

Smoke is target ~10-30s at N=1024, 1 seed, smaller M-grid (matches U1 smoke ~12s precedent).
FULL: N=8192, 3 seeds, ARM4 sweeps 5 M-points up to 5000 plus 3 fixed arms; estimated wall ~10-20 min.

formula: ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^scaling_exp * (FULL_seeds/smoke_seeds))
  = ceil(1.5 * 20 * (8192/1024)^1.5 * (3/1))
  = ceil(1.5 * 20 * 22.6 * 3) = 2036s

Add headroom for the ARM4 sweep + multi-arm fanout (5 M-points × all arms): timeout_s = 2400 (40 min).
Well below the PROT-021 4h checkpoint floor (and the cell checkpoints per-seed anyway for resume).

## Bias-control / Lane discipline (per master bias checklist)

- **Lane declared:** Lane 1 (substrate-native capability; no out-of-lane comparison).
- **Baselines:** chance only (1/V_concepts and 5/V_concepts). NO transformer / NO statistical-LM /
  NO word-bigram baselines (per USER directive: "why the fuck are we still testing against things
  like word-bigram?").
- **Encoder leakage:** zero — synthetic random-orthogonal-ish bipolar embeddings, NO word2vec, NO
  pretrained model, NO real corpus text.
- **By-construction saturation:** chance rate (0.005 top1, 0.025 top5) explicitly logged + far
  below pre-reg floors; the floors are not perfect-by-construction. ARM_3 PRIMARY metric pairs the
  trained-recovery floor with the sanity-floor (substrate must NOT hallucinate under untaught
  predicate) so the test cannot be gamed by either over-memorizing or by being uniformly responsive.
- **Per-arm metrics:** every arm reports its primary scalar + supporting diagnostics + chance rate;
  per-seed entries in `per_seed`; cv computed across seeds per arm.
- **Pre-registered PRIMARY arm:** ARM_GENERALIZATION_HELDOUT (the brain-like test; the answer to
  "can the substrate do analogical recall after sparse training, without hallucinating off-graph?").
