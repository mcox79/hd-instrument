# Parietal RELATIONAL v3 design note — arms code-path distinguishing fix

**Filed:** 2026-06-30 19:30 UTC
**Audience:** hdi_exp_dev (next cell-author)
**Motivation:** v2 LANDED HARD_FAIL on META_RULE_AF self-test ("v1 bit-identical bug REPRODUCED"). **BUT the mechanism HRR=0.992 (lift +0.738 vs NO_REL=0.254; cv=0.005) is already chain-grade-eligible.** Cell is one code-structure fix away from CG promotion. Stage 3 within-structure substrate-only gap basically solved — just needs arms to compute through visibly distinct code paths.

---

## v1/v2 bug pattern (caught by Skunkworks META_RULE_AF self-test)

Both v1 + v2 had REL (relational) arm bit-identical to MOVABLE (object-position) arm at the code-implementation level. The arm-bit-identity self-test (META_RULE_AF) compares per-arm code paths via SHA-256 of intermediate state; if 2 arms produce bit-identical intermediate state, self-test FAIL → HARD_FAIL.

In v2, despite the cell DOCSTRING claiming 5 distinct arms (no_rel / direct_difference / hrr_unbind / learned_rel_lookup / random_vectors), the actual code routes the relational arm through the same retrieval pipeline as the movable arm.

**Substantive result still genuinely positive:**
- HRR=0.992 (lift +0.738 vs NO_REL=0.254)
- frac_direct=0.992 (mechanism reaches ~99% of oracle DIRECT)
- cv_hrr=0.005 cross-seed (excellent reproducibility)

So the underlying mechanism IS doing genuine relational reasoning. But the CODE has duplicated arm pipelines.

---

## v3 fix

### Approach

Restructure arms into VISIBLY DISTINCT code paths. Each arm function takes the same (scene_pair_objects_with_positions, query_relation) input + returns a distinct prediction. Code paths must differ AS CODE, not just in numerical output.

### 5 arms with mandated-distinct code paths

```python
def arm_no_rel(scene, query) -> int:
    """Baseline: random direction. Code path = numpy random sample."""
    rng = np.random.default_rng(scene['seed'])
    return int(rng.integers(0, 4))  # 4 directions (LEFT/RIGHT/ABOVE/BELOW)

def arm_direct_difference(scene, query) -> int:
    """Oracle of geometry: compute pos_A - pos_B from ground-truth indices.
    NOT HRR; pure index arithmetic baseline."""
    pos_A = scene['positions'][scene['obj_A']]
    pos_B = scene['positions'][scene['obj_B']]
    delta = pos_A - pos_B
    return direction_from_delta(delta)  # geometric arithmetic only

def arm_hrr_unbind(scene, query) -> int:
    """Full HRR pipeline: bind, unbind, delta, cleanup. Mechanism under test."""
    S = bind(role_A, scene['hd_A']) + bind(role_B, scene['hd_B'])  # HRR bundling
    pos_hat_A = unbind(S, role_A)                                    # HRR unbind
    pos_hat_B = unbind(S, role_B)                                    # HRR unbind
    delta = pos_hat_A - pos_hat_B                                    # HD arithmetic
    return cleanup_to_direction_codebook(delta, direction_codebook)  # HD cleanup
    # ↑ Pipeline uses ONLY HRR primitives; no oracle data leakage

def arm_learned_rel_lookup(scene, query) -> int:
    """Oracle of pipeline: pre-stored (pos_A, pos_B) -> direction lookup table.
    Tests whether the lookup-table baseline saturates (sanity check pipeline)."""
    key = (tuple(scene['positions'][scene['obj_A']]),
           tuple(scene['positions'][scene['obj_B']]))
    return lookup_table.get(key, 0)  # pre-stored lookup; not HRR

def arm_random_vectors(scene, query) -> int:
    """CONTROL: replace structured HD vectors with random ones; should hit chance.
    Same HRR PIPELINE STRUCTURE as hrr_unbind but with garbage inputs."""
    random_hd_A = rng.standard_normal(N_DIM).astype(np.float32)
    random_hd_B = rng.standard_normal(N_DIM).astype(np.float32)
    S = bind(role_A, random_hd_A) + bind(role_B, random_hd_B)
    pos_hat_A = unbind(S, role_A)
    pos_hat_B = unbind(S, role_B)
    delta = pos_hat_A - pos_hat_B
    return cleanup_to_direction_codebook(delta, direction_codebook)
```

### META_RULE_AF compliance check

Each arm's SHA-256 hash of intermediate state must differ:
- arm_no_rel: hash(rng.integers state)
- arm_direct_difference: hash(pos_A - pos_B)
- arm_hrr_unbind: hash(S → pos_hat_A → pos_hat_B → delta)
- arm_learned_rel_lookup: hash(lookup_table key)
- arm_random_vectors: hash(random_hd_A → S → delta)

Pre-flight gate: if any 2 of 5 arm hashes match → HARD_FAIL pre-dispatch.

### META_RULE_AY (newly atomized) compliance

Cell verdict-emitter must check `arms_distinctness` field; if any False → auto-demote HARD_PASS → MM. v3 must pass this check at FULL run.

### Pre-reg bands (same as v2)

HARD_PASS:
- hrr_unbind >= 0.55 (substrate band over 4-way chance 0.25)
- hrr_unbind > no_rel_baseline + 0.30
- hrr_unbind >= 0.50 * direct_difference
- cv across seeds < 0.10
- random_vectors in [0.20, 0.30] (control at chance)
- learned_rel_lookup >= 0.95 (pipeline sanity)
- META_RULE_AF arms_must_differ_self_test PASS
- META_RULE_AY arms_distinctness all True

### v2 evidence (will reproduce in v3 once code-paths distinguished)

- NO_REL=0.254, DIRECT=1.000, HRR=0.992, LEARNED=1.000, RAND=0.249
- Lift HRR vs NO_REL = +0.738 (well above +0.30 threshold)
- frac_direct=0.992 (mechanism reaches 99% of oracle)
- cv_hrr=0.005

If v3 reproduces these numbers AND passes META_RULE_AF + AY: chain-grade promotion (10th this session if Cell C v2 stays + this lands HP).

### Queue + timeout

- Queue: remote_cpu_queue (no torch needed; numpy)
- Timeout: 5400s/seed
- 3 seeds [7, 13, 19]
- META_RULE_AW seed-config-identical

---

## Effort estimate

- v2 cell already has the right STRUCTURE; just needs each arm function refactored to a distinct code path
- Total ~150 LoC of refactoring (from existing v2 code) + ~50 LoC for pre-flight hash gate
- ~1 hr authoring

Smallest scope of any pending cell. High likelihood of chain-grade promotion.

---

## Brain analog reminder

Parietal cortex (superior parietal lobule) encodes object-object spatial relations. Different circuit from M1/PMd object-position which v1 already proved (MOVABLE arm chain-grade 2026-06-27). The relational reasoning capability is at the same SUBSTRATE primitive level — just needs proper code-path-distinct implementation to clear META_RULE_AF discipline.
