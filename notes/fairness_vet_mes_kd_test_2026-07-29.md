# FAIRNESS / VALIDITY VET — MES + KD comprehension test (2026-07-29)

Auditor: Skunkworks (AUDIT-ONLY). Independent recompute off construction code + on-disk data.
Scope: are we running MES + KD FAIRLY, and are results what grounded-text-only comprehension
should produce? Highest-priority flag: the structure-alone bar rose to 0.67 at 256 train items.

Sources inspected off disk: `experiments/diag_order_critical_comprehension_calib_v1.py`
(gen_multi_entity_state, gen_knowledge_dependent, _self_test_knowledge_dependent);
`experiments/exp_stateful_core_situation_model_v1.py` (forward_item_batch, make_judge_head,
train_and_eval_arm, run_regime random-init control); `hdlab/slot_attention_wm.py`;
`data/diag_order_critical_comprehension_calib_v1/hardening.json`;
`data/diag_stateful_core_gen_curve_v1/metrics.json`;
`data/exp_stateful_core_mes_data_sufficient_gate_v1_smoke/_heartbeat.jsonl`.

---

## 1. The 0.67 structure-alone signal — SOURCE + verdict

**SOURCE (REASONED@ from construction + WM code): random-features / reservoir decoding of
genuine ORDER information, NOT a bag-of-words / surface leak.**

- The random-init control (`fit_random_init_control` / run_regime block) fits ONLY a linear judge
  head on FROZEN random-init encoder+WM features: `judge_in = [slot_mean(512), surprise,
  write_strength, addr_entropy]` = 515 dims. A random-init TinyTransformer is a *fixed nonlinear
  random feature map* of the token sequence — and it has **position embeddings + self-attention**,
  so it is inherently ORDER-SENSITIVE (unlike bag-of-words). This is an extreme-learning-machine /
  reservoir: a linear readout on random order-sensitive features decodes any signal linearly
  present in the random projection, and it fits BETTER with more judge-training data — exactly the
  RISING curve {64:0.49, 128:0.575, 256:0.67, 512:0.675}.
- WHAT it decodes: in MES, `stream1` (label 1) ends `...target_first(sA)...target_final(sB)`;
  `stream0` (label 0) has the two target sentences SWAPPED so the late "became X" is sA. Word
  multiset, token count, and clause count are byte-identical between labels (verified by the
  in-code multiset self-test, lines 448-456). The ONLY differing signal is the **position/identity
  of the state word in the target's final-update slot** relative to the fixed query — i.e. pure
  ORDER, which position embeddings encode even untrained. So the random core legitimately reads
  order, partially.

**VERDICT: NOT a construction leak.** The multiset control holds at 256 scale, the group split is
leak-proof, and the signal the random core exploits (order via position embeddings) is exactly the
capability the construction intends to REQUIRE. The 0.67 is the honest "structure-alone" floor that
design-doc D3 explicitly anticipated ("if the untrained core matches, it is structure not
learning"). It is a real property, not a bug, and not an inflating artifact in the label.

---

## 2. The FAIR metric + is the residual detectable?

**Chance at the 256 scale is effectively the scale-matched random-init acc (~0.67), NOT 0.50.**
Confirmed the gate already uses a **scale-matched random-init control** (run_regime fits the
random-init head on the SAME train/eval size; gen_curve pairs each size with its own random-init
fit). Good — the pass bar is correctly *margin over scale-matched random-init*, not margin over 0.5.

**But the residual is at/below the noise floor at our current N (load-bearing):**
- Binomial SE at p=0.67, eval N=200 (100/label) = **0.033** (MEASURED@ arithmetic). SE of the
  DIFFERENCE between two accuracies (~0.67 vs ~0.72) at N=200 = **0.046**, so a **+0.05 margin is
  ~1.09 sigma — indistinguishable from noise** at a single seed.
- The random-init baseline ITSELF has large seed/size variance: the gen-curve seed hit 0.67, but
  the calib gate-B five-seed random-init margins over 0.5 were {0.0125, 0.0125, 0.031, 0.075,
  0.028} (mean 0.032, max 0.075) — i.e. the structure floor wanders ~±0.04 across seeds.

So a mechanism scoring **0.72 would NOT be a reliable +0.05 comprehension margin** — it is inside
the combined (eval-noise + baseline-seed-variance) envelope. The full run's ≥5 random-init seeds is
the right instinct, but the PASS RULE must be *trained > (95th-pct or max of the random-init seed
distribution) by more than the difference-SE*, evaluated at an N large enough to resolve the target
effect. At N=200 the minimum reliably-detectable margin is ~0.07-0.09 (2 sigma), not 0.05.

---

## 3. MES leak / difficulty checklist (at 256 scale)

- **Multiset identity**: HOLDS at scale — enforced pre-sampling in gen_multi_entity_state
  (lines 448-456), independent of judge train size. PASS.
- **Group split leak-proof at scale**: objects(20)×pairs(15)=300 combos, 90 held out; eval combos
  disjoint from train combos (asserted line 385). A probe cannot memorize per-combo order. PASS.
- **Fixed-eval contamination across sizes/seeds**: NONE — gen_curve draws train subsets from
  mc["train"] and eval from mc["eval"] (disjoint combo sets) within a run; each seed regenerates.
  PASS.
- **Length/clause-count cue**: NONE — stream0/stream1 are permutations (same sentence count, same
  tokens). PASS.
- **Can-fail / not saturated / not analytically pinned**: PASS (label-balanced, untrained head
  ~chance, real reader far from ceiling).
- **CAVEAT — task-mismatch in the difficulty calibration**: gate-A (BGE margin +0.19..+0.25,
  coherent ~0.69-0.75, hardening.json) is measured on **coherent-vs-word-SCRAMBLE**, but the
  stateful core is graded on **consistent-vs-VIOLATED (order-swapped)**. These are related but NOT
  identical discriminations, and no known-reader number establishes the consistent-vs-violated task
  is solvable ABOVE the 0.67 structure floor. The order-critical structure is shared, so a BGE-class
  reader very likely clears it, but it is UNMEASURED for the graded task. Flag.

---

## 4. KD fairness + the Arm-B extra-judge-dim confound (IMPORTANT)

**CONFIRMED the Arm A/B judge-head asymmetry** (MEASURED@ code): `make_judge_head(d, arm)` →
`in_dim = d + 3 + (1 if arm=='B' else 0)`, so **Arm A = Linear(515,2), Arm B = Linear(516,2)** —
Arm B always has ONE extra input dimension. In forward_item_batch, Arm B appends real
`kb_consistency` when a KB prior exists, else a **zeros column**.

- **On MES**: generic objects have no CSKG edge → gen_kb_prior returns None → kb_prior_batch=None →
  wm.step emits no kb_consistency → Arm B gets a **constant-zero dead column** = zero added info,
  zero effective capacity. So the asymmetry **cannot explain any MES B-A**. (This also confirms the
  intended "Arm B degrades to Arm A on MES" — good.)
- **On KD**: Arm B gets a genuinely non-constant kb_consistency feature. This is a REAL confound in
  form (B strictly has more readout inputs), but bounded: +1 input over 515 existing features is ~2
  extra weights — pure VC-capacity cannot manufacture the +0.156 KD B-A. AND kb_consistency is
  *derived from the KB prior interacting with the maintained slots* on IDENTICAL text (Arm B does
  not change the KD sentences), so if it correlates with the label that IS the grounding effect by
  construction. So the +0.156, if replicated, is very unlikely to be a pure-capacity artifact.
- **BUT it is not cleanly controlled.** There is no Arm-A-with-placebo-column and no
  shuffled-kb_consistency arm, so we cannot yet *prove* the lift is grounding rather than "an extra
  informative-by-accident dimension." This must be equalized before the gate is trusted.
- **Valence 2x2**: VERIFIED blocked — `_self_test_knowledge_dependent` asserts every (fact_id,cand)
  pair carries BOTH labels (causal×true / noncausal×false cross). PASS. KD-A genuinely deprived:
  KD context states only the action ("left outside in the rain"), never the outcome verb — resolving
  requires the world fact. PASS.
- **CAVEAT — thin held-out fact set**: eval_fact_frac 0.3 over 10 facts = **only 3 held-out
  concepts**. Grounding transfer is judged on 3 facts (high variance). Report per-fact spread or
  widen the fact pool.

---

## 5. Grounded-text-only expectation vs observed

- **MES (maintenance)** needs NO world knowledge → a competent text-only stateful reader SHOULD
  score HIGH (BGE-class, well above 0.67); Arm B SHOULD ≈ Arm A (KB irrelevant — confirmed the dead
  column makes this structural). Observed: both arms sit near the 0.67 structure floor in the
  diagnostics → the maintenance mechanism is **not yet reading above structure**. That is a
  MECHANISM-not-yet-learning read, consistent with the test being fair (not an unfairness deflating
  it).
- **KD (bridging)** SHOULD FAIL text-only (Arm A near floor) and grounding SHOULD LIFT (Arm B > A).
  Observed +0.156 B-A with MES B-A ≈ 0 is the RIGHT SIGN and the intended SELECTIVE signature — but
  its magnitude lives inside the capacity-confound + detectability envelope until fixes below land.

Results are **qualitatively consistent** with grounded-text-only expectations (selective KB lift on
bridging, none on maintenance); they are **not yet quantitatively trustworthy**.

---

## NOTE ON REPRODUCIBILITY
The cited gen-curve numbers {64:0.49,128:0.575,256:0.67,512:0.675} are NOT in the on-disk
`data/diag_stateful_core_gen_curve_v1/metrics.json` — that file currently holds only the SELFTEST
verdict (random_init_control acc=0.625 at N~4-16, itself already-above-0.5, consistent with the
leak). The --run output was not persisted / was overwritten. Non-fatal (the mechanism verdict stands
on the construction code, which I did recompute), but the 0.67 point-values could not be recomputed
off the named file. The data-sufficient-gate metrics.json does not exist yet (smoke in-flight;
heartbeat shows MES A/B eval 0.6875 at tiny N=32, random_init 0.5, KD A 0.5 — do not over-read tiny N).

---

## VERDICT: FAIR-WITH-CAVEATS

The test is fundamentally fair: no construction leak, multiset/valence/group-split controls hold at
256 scale, difficulty is on, and the scale-matched random-init control is the correct chance
baseline. The 0.67 is an honest structure-alone floor (random order-sensitive features), not an
inflating artifact and not a deflating bug.

**MUST-FIX before the bistable-fix gate is trusted:**
1. **State the pass bar as margin over the random-init-seed DISTRIBUTION** (≥5 seeds; trained >
   95th-pct/max of random-init) with a significance test — NOT a point compare, and NEVER over 0.50.
2. **Equalize Arm A/B judge in_dim** (give Arm A a matching placebo column) AND add a
   **shuffled/permuted-kb_consistency placebo arm** to prove the KD +0.156 is grounding, not the
   extra dimension.
3. **Raise eval N (or aggregate across seeds)** so the target effect is resolvable: at N=200 the
   min reliably-detectable margin is ~0.07-0.09 (2 sigma); +0.05 is ~1 sigma = noise. State the
   minimum-detectable-effect at the chosen N in the pre-reg.
4. **Measure a known reader (BGE) on the ACTUAL consistent-vs-violated discrimination** (not just
   coherent-vs-scramble) to confirm the graded task has real signal above 0.67.
5. **KD: widen the held-out fact set or report per-fact variance** (3 eval concepts is thin).
