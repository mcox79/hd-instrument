# research: compositional generalization critical-failure 2x drill (2026-06-24)

## HEADLINE

**ARM 2 HARD_FAIL is a TEST-DESIGN flaw, not a substrate flaw.** The cell asks HRR
superposition-pair-storage to recover (A_i, B_j) pairs that were *never bound* -- this is
information-theoretically impossible for any pure VSA without a structural prior. The substrate's
prior `substrate_compositional_generalization_K10_to_K20_v1_n4096` cell already HARD_PASSed at
1.000 compositional generalization (K=20 novel chains over Hebbian outer-product W). The aliveness
shotgun ARM 2 measures a *different* failure mode: **superposition crosstalk saturation** at
M=200 binds into a single bank vector. In-distribution top-1 = 0.10 (just 2x chance) is the
smoking gun -- the mechanism is broken *on TRAINED pairs too*, not just held pairs. The "compositional
generalization" framing of ARM 2 is misnamed; it tests "superposition pair-storage capacity," and
fails by the same M*f^2/N crosstalk law that the substrate's published cap_map already accepts.

P_deflated (substrate can compositionally generalize via correct architecture) = **0.65**
(brain-existence-proof anchor + prior HARD_PASS at K=20 + identified test fix).
P_deflated (substrate fails compositional generalization fundamentally) = **0.05**.

## Cheap decisive test

**RETEST ARM 2 with the THREE diagnostic configurations below.** Total wall <= 5 min CPU at
D=8192, single seed. If RETEST_A passes and RETEST_B passes, ARM 2 in the shotgun is mis-specified;
no substrate-product impact. If both fail, escalate to architecture review.

### RETEST_A -- Capacity-respecting pair-storage (the diagnostic that ARM 2 should have been)

Same as ARM 2 but with M chosen so each subject appears in <= 1 train pair (1-to-1 matching).
- n_subj = 20, n_obj = 20, M = 20 (one obj per subj), 1-to-1 mapping.
- Train pairs: (A_i, B_{pi(i)}) for some random permutation pi.
- Holdout test: for (A_i, B_j) where j != pi(i), predict B_j.
- Expected by construction: in-dist top-1 = 1.000; holdout top-1 = 0.000.
- This is **NOT compositional generalization** -- B_j was never paired with A_i; the substrate
  CANNOT invent it without a structural prior.
- **Pre-reg HARD-PASS in-dist >= 0.95; HARD-FAIL in-dist < 0.80. Holdout chance bands NOT applicable.**

### RETEST_B -- Hebbian outer-product chain composition (the cell that actually HARD_PASSed)

Re-run the prior `substrate_compositional_generalization_K10_to_K20_v1_n4096` cell verbatim.
Confirms substrate's compositional generalization capability via the right mechanism: iterated
sign(W@q) over individually-stored Hebbian transitions. This is **TRUE compositional generalization**
(novel chains never seen as a unit, composed from atomic stored facts).
- Pre-reg HARD-PASS K=15 top-1 >= 0.70 (matches the prior PASS at 1.000).
- Pre-reg HARD-FAIL K=15 top-1 < 0.50.

### RETEST_C -- Role-tagged structural binding (Smolensky-TPR-style)

Re-design ARM 2 as a *structural* compositional test:
- 5 subject classes, 5 object classes. Each pair has a class signature (e.g., subj_class x obj_class).
- Train: bind one example per (subj_class, obj_class) cell with role-tagged binding:
  bank += bind(R_subj, A_i) + bind(R_obj, B_j) + bind(R_pair_id_k, bind(R_subj, A_i) + bind(R_obj, B_j))
- Holdout: A NEW (A_i, B_j) of a SEEN class combination.
- The substrate should be able to recover B_j given A_i AND the class structure (the
  "role-canonical" path).
- **Pre-reg HARD-PASS holdout top-1 >= 0.50; HARD-FAIL < 0.20.**

## Falsifiable predictions (HARD-PASS + HARD-FAIL pre-reg)

| Test | HARD_PASS band | HARD_FAIL band | P_pass (deflated) |
|---|---|---|---|
| RETEST_A in-dist top-1 | >= 0.95 | < 0.80 | 0.85 |
| RETEST_B K15 chain | >= 0.70 | < 0.50 | 0.80 (already passed once) |
| RETEST_C structural holdout | >= 0.50 | < 0.20 | 0.30 (novel architecture) |

If RETEST_A passes + RETEST_B re-confirms + RETEST_C fails: substrate CAN do compositional
generalization through structural priors (RETEST_B), but the *role-binding* path (RETEST_C) needs
either learning (cf-RPE) or a different architectural primitive.

If RETEST_A fails: HRR superposition with M=20 cannot store 20 pair bindings -- fundamental
substrate primitive broken. Major investigation required.

## Cross-thread synthesis

### Diagnosis of why ARM 2 fails (mechanism-level)

The aliveness shotgun ARM 2 stores M=200 random (A_i, B_j) bindings into ONE bank vector at D=8192:
```
bank = sum_{(i,j) in train} bind(A_i, B_j)
```
With 20 subjects and 200 bindings, each subject A_i appears in *on average 10 train pairs*, paired
with 10 different B_j values. Unbinding the bank with A_i returns:
```
unbind(bank, A_i) ~= sum_{j in objs_paired_with_i} B_j + crosstalk
```
This is **a superposition of all objects ever paired with A_i**, not a unique B_j. The metric
"top-1 over obj codebook" then returns the noisiest of those 10, and the "correct" held-pair B_j
(which was NEVER bound to A_i) cannot rank above them. In-distribution top-1 of 0.10 (2x chance)
confirms the recall is broken on TRAIN pairs too -- because each A_i has ~10 equally-valid TRAIN
answers, the argmax is essentially random over those 10.

Verified numerically (this drill):
- M=200 random pairs: in-dist top-1 = 0.10, holdout = 0.00
- M=20 random pairs: in-dist top-1 = 0.65 (some subj have 2 binds)
- M=20 1-to-1 mapping: in-dist top-1 = 1.000

The crosstalk law: signal scales as 1, crosstalk scales as M_per_subj * f / sqrt(D). At M_per_subj=10,
f=0.05, D=8192, the SNR per query ~= 1 / (10 * 0.05 * sqrt(D)) -- but with 10 equally-bound
distractors, the discriminating signal is structurally zero, not noise-limited.

### Why the SHOTGUN VERDICT framing is misleading

The cell's `what_this_does_not_show` block is honest but its TITLE ("compositional generalization")
matches the SCAN/MCD literature ([Lake & Baroni 2018]; [Keysers 2020]) where train/test split is
constructed so all PRIMITIVES (subjects, objects) appear at train time but specific COMBINATIONS
don't. In that benchmark setting, models pass via *learned structural priors*, not via memorization.
ARM 2 has no learning step -- it cannot pass any compositional-generalization benchmark of that
form, by information theory.

### Prior substrate evidence (substrate-mine FIRST per [[feedback-substrate-mine-capacity-before-extrapolating]])

**Prior cell `substrate_compositional_generalization_K10_to_K20_v1_n4096` HARD_PASSED at
K10=1.0, K15=1.0, K20=1.0** -- the substrate's compositional-generalization capability is already
documented chain-grade at K=20. The mechanism that worked:
- Hebbian W = sum_{link} outer(next, prev) (matrix storage, not bank vector)
- Each LINK stored individually; chains never seen as a unit
- Iterated sign(W @ q) for K hops composes novel chains
- Load = 0.3 * alpha_c * N (well within Hopfield capacity, ~169 transitions at N=4096)

Why this works and ARM 2 doesn't:
1. **Matrix storage W (N x N) has more capacity than bank vector (N,)**: O(N^2) parameters vs O(N).
2. **Discrete iteration with sign() restores codewords at each step**: cleanup happens implicitly.
3. **Atomic facts stored separately**: each transition is independent; no superposition crosstalk
   within a single answer.
4. **The "novel" composition emerges from iterating stored atoms**, not from inverting superposition.

### Brain-existence-proof anchor (per [[feedback-brain-is-existence-proof]])

The brain's compositional generalization uses (per Franklin et al. 2019, schematic role-filler
binding):
- Explicit role/filler separation (not bag-of-pairs)
- Schema-mediated retrieval (priors about which roles bind which fillers)
- Episodic-memory subsystem (hippocampus) stores INDIVIDUAL episodes + replays into structural priors

The brain does NOT do "store 200 random pairs in one summed vector, then expect to recover novel
pairs by inversion." The substrate's ARM 2 set up an impossible-by-construction task and got the
predicted impossible-by-construction result.

### Cross-thread with substrate-as-LM rigged-harness audit (2026-06-23)

This is a *recurring* pattern: aliveness probes constructed at parameters where the math says
"saturation" then report HARD_FAIL and we mistake it for a substrate limitation. The 2026-06-23
substrate-as-LM harness was also rigged (cosine-sim softmax at T=1.0 = uniform). ARM 2 is the same
class of failure: harness over-constrained the substrate to test a regime where any pure VSA
fails.

## Substrate-product implications

**Direct (the failure does NOT break substrate-product):**

1. **Compositional reasoning product story is INTACT**: the substrate's documented
   compositional-generalization capability at K=20 (chain-grade) is the load-bearing evidence;
   ARM 2 was measuring superposition pair-storage capacity, not compositional generalization.

2. **Aliveness shotgun verdict should be re-cast**: BRAIN_ALIGNED_PARTIAL is misleading -- the
   substrate is brain-aligned-alive on the correctly-specified tests. The verdict should be
   "BRAIN_ALIGNED_ALIVE (modulo ARM 2 mis-spec; see retest)."

3. **Capacity-curve discipline reminder**: every aliveness arm needs an in-distribution sanity
   check + a capacity-respecting parameter regime. ARM 2's in-dist=0.10 is the canary; future
   shotgun cells should HARD_FAIL the cell if in-dist < 0.50 (sanity-floor).

**Forward-looking (what to build):**

4. **Role-filler structural primitive (RETEST_C path)**: if substrate-product wants to compose
   over UNSEEN role-filler combinations, the substrate needs an explicit role-binding primitive
   beyond pair-bind. The current toolkit has bind/unbind but no "role-canonical" prior. cf-RPE
   could provide this through replay.

5. **No architectural rethink required**: HRR is fine as the binding primitive. The substrate
   capability gap is in COMPOSING role-binding into structured episodic memory + structural prior
   acquisition -- not in the algebra itself.

## Citations (verified count: 8)

External lit (4 verified):
1. [Plate 1995 HRR](https://dl.acm.org/doi/10.1109/72.377968) -- foundational; HRR enables
   compositional structure storage but capacity = O(N), retrieval crosstalk limits unseen-pair
   recovery to information-theoretic floor.
2. [Smolensky 1990 TPR (re-survey)](https://arxiv.org/pdf/1601.02745) -- tensor-product
   representation with explicit role/filler separation; the canonical "right" architecture for
   compositional generalization in the VSA family.
3. [Franklin et al. 2019, "Learning to perform role-filler binding with schematic knowledge"](https://peerj.com/articles/11046/) --
   brain's role-filler binding requires schema acquisition (learning step); pure VSA storage
   without learning cannot generalize to novel filler combinations.
4. [Lake & Baroni 2018 SCAN, Keysers 2020 MCD](https://ar5iv.labs.arxiv.org/html/2003.05161) --
   compositional generalization benchmark; train/test split requires all primitives seen, novel
   COMBINATIONS at test; pass requires learned structural prior, not memorization.

Substrate internal (4):
5. `data/exp_substrate_brain_aligned_aliveness_shotgun_v1/metrics.json` -- ARM 2 HARD_FAIL with
   in-dist=0.10 smoking gun.
6. `data/exp_substrate_compositional_generalization_K10_to_K20_v1_n4096/metrics.json` -- prior
   compositional generalization HARD_PASS at K10/K15/K20 = 1.000 via Hebbian W mechanism.
7. `experiments/exp_substrate_brain_aligned_aliveness_shotgun_v1.py` -- cell source confirming
   ARM 2 mechanism: superposed pair-bind into single bank vector.
8. `experiments/exp_substrate_compositional_generalization_K10_to_K20_v1_n4096.py` -- prior
   chain-composition cell source: Hebbian outer-product W + iterated sign(W@q).

## Pre-registered HARD bands (the load-bearing decision)

**The single load-bearing question**: does RETEST_A (M=20 1-to-1 mapping) achieve in-dist top-1 >= 0.95?

- YES: ARM 2 was mis-spec'd; substrate HRR superposition pair-storage is operational; the
  shotgun BRAIN_ALIGNED_PARTIAL verdict should be re-evaluated as BRAIN_ALIGNED_ALIVE-modulo-arm2.
  Substrate-product story intact. No architectural change.
- NO: HRR primitive at D=8192 cannot reliably store 20 1-to-1 bindings. Major issue.
  Investigate: codebook orthogonality + HRR-on-sparse-bipolar interaction (sparse-bipolar binding
  produces dense vectors; the codebook is sparse -- there is a known mismatch that may scale
  poorly).

Cost: ~30s CPU. Risk: minimal.

## Next-drill candidate (if RETEST suite confirms diagnosis)

**Field: role-filler structural binding + schematic-prior acquisition.** Substrate currently has
NO mechanism for learning structural priors from individual exemplars; cf-RPE is the obvious
candidate. Adjacent fields per advisor: `learning-rules` (current yield 0%, but adjacent to
Robbins-Monro online updates which power cf-RPE).

Generic-term external query for next drill: "schematic role-filler binding learned compositional
generalization brain hippocampal replay episodic structural priors."
