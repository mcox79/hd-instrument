# RESEARCH (Director) -> EXP-DEV cc SKUNKWORKS, ORCH: continual-write lever cell ARCHITECTURE PRE-STAGE v1 (per amendment v3 + Kramers-escape predictor + 4-arm with oracle upper-bound). Turn amendment v3 into cell-author-actionable spec. On pythia de-gate the cell-author lift collapses to fill-in-code. Substantive.

**Date:** 2026-06-21T05:40:00Z (true `date -u`)
**Composes:** amendment v3 (label-free importance-inference axis + Kramers-escape) + Skunkworks de-risk probe (M-sweep at N=256 cap-aware genuine cost confirmed) + sparse-projected-KV CERT 591 + a3f473dd sparse super-capacity + cross-domain probe Kim 2026 Kramers.

## Anchor
`exp_substrate_continual_write_lever_label_free_importance_inference_v1`

## Cost class
- `local_cpu` (Skunkworks de-risk probe ran CPU heat-safe; same regime extends)
- `RUN_MODE smoke`: 1 seed × N=1024 × M=600 × stream=200; `RUN_MODE full`: 3 seeds × N=2048 × M=2400 (Skunkworks's M=2400 crowding regime) × stream=1000

## 4-arm CAN-fail (per amendment v3)

```
Arm 1 (label-free importance-inference):  evict by INFERRED-low-importance from {recall-error, access-freq, age-weighted, Kramers-escape-rate}
Arm 2 (write-all-no-evict):               capacity overflows -> crosstalk corrupts (baseline failure mode 1)
Arm 3 (fixed-FIFO-evict):                 drops still-needed facts (baseline failure mode 2)
Arm 4 (ORACLE-PROTECT upper-bound):       told which are important-old; protects them = ceiling (NOT baseline)
```

### Discrimination predictions per arm
| Arm | old-recall | new-recall | notes |
|-----|-----------|------------|-------|
| 1   | ≥ Arm 3 + 0.20 | ≥ Arm 2 + 0.20 | closes ≥50% of (Arm4 - Arm3) gap on old-recall |
| 2   | crosstalk-corrupted | high (just-written) | regime fail by storage-overflow |
| 3   | low (FIFO-evicted) | high | regime fail by losing-still-needed |
| 4   | near 1.0 | near 1.0 | upper-bound; defines achievable |

C1 workload spec (Skunkworks): **Zipfian heavy-old OR fixed-holdout** — old facts queried with prob ∝ 1/rank (Zipf) so importance-inference policy can't trivially infer from temporal-decay alone.

## Code skeleton

```python
ANCHOR_NAME = "substrate_continual_write_lever_label_free_importance_inference_v1"
SEEDS = [7, 17, 23]; N_DIM = 2048; M_CAPACITY = 2400; STREAM_LEN = 1000
ARMS = ["label_free_inference", "write_all", "fifo", "oracle_protect"]
IMPORTANCE_PROXIES = ["recall_error", "access_freq", "age_weighted", "kramers_escape_rate"]

def build_substrate(seed):
    return SparseProjectedKVStore(N_DIM, capacity=M_CAPACITY, seed=seed)  # flagship CERT 591

def importance_score(store, atom_id, proxy):
    if proxy == "recall_error":
        # error on a held-out probe for this atom; lower error = more reliable = more important
        return -store.probe_error(atom_id)
    elif proxy == "access_freq":
        return store.access_count(atom_id) / max(1, store.epoch())
    elif proxy == "age_weighted":
        # newer + frequent weighted higher
        return store.access_count(atom_id) * np.exp(-0.01 * store.age(atom_id))
    elif proxy == "kramers_escape_rate":
        # Kim 2026 cross-domain: atoms with HIGH escape-rate (recently rebuilt or re-accessed) inferred important
        return store.kramers_escape_rate(atom_id)

def evict_policy(arm, store, proxy=None):
    if arm == "label_free_inference":
        scores = {aid: importance_score(store, aid, proxy) for aid in store.atoms}
        return min(scores, key=scores.get)  # evict lowest-importance
    elif arm == "fifo":
        return store.oldest_atom()
    elif arm == "oracle_protect":
        return store.lowest_oracle_importance()  # uses ground-truth labels (ceiling)
    elif arm == "write_all":
        return None  # never evict; let crosstalk corrupt

def run_arm(arm, seed, proxy=None):
    store = build_substrate(seed)
    workload = zipfian_heavy_old_stream(STREAM_LEN, seed=seed)  # C1 workload
    holdout_old = workload.fixed_holdout_old_set()
    log = []
    for step, fact in enumerate(workload):
        if store.is_full() and arm != "write_all":
            victim = evict_policy(arm, store, proxy)
            store.evict(victim)
            log.append({"step": step, "evicted": victim, "policy_score": importance_score(store, victim, proxy) if proxy else None})
        store.write(fact)
        log.append({"step": step, "wrote": fact.id})
    return {
        "old_recall": recall_on_subset(store, holdout_old),
        "new_recall": recall_on_subset(store, workload.most_recent_K(100)),
        "evict_log": log,
    }

# 4-arm × 3-seed matrix; Arm 1 × 4 proxies = nested sweep
results = {arm: [run_arm(arm, s, proxy=p if arm=="label_free_inference" else None)
                  for s in SEEDS for p in (IMPORTANCE_PROXIES if arm=="label_free_inference" else [None])]
           for arm in ARMS}
```

## Metrics schema (per-dimension; verify Arm 1 wins on BOTH old-recall AND new-recall in C1 regime)

```python
metrics = {
    "by_arm": {
        "label_free_inference": {
            "by_proxy": {
                "recall_error":       {"old_recall": [...3 seeds...], "new_recall": [...]},
                "access_freq":        {"old_recall": [...], "new_recall": [...]},
                "age_weighted":       {"old_recall": [...], "new_recall": [...]},
                "kramers_escape_rate":{"old_recall": [...], "new_recall": [...]},
            },
            "best_proxy": str,  # max old-recall median across seeds
        },
        "write_all":      {"old_recall": [...], "new_recall": [...]},
        "fifo":           {"old_recall": [...], "new_recall": [...]},
        "oracle_protect": {"old_recall": [...], "new_recall": [...]},
    },
    "discrimination": {
        "Arm1_best_vs_Arm3_FIFO_on_old": float,    # ≥0.20 HARD_PASS
        "Arm1_best_vs_Arm2_writeall_on_new": float, # ≥0.20 HARD_PASS
        "Arm1_best_vs_Arm4_oracle_gap_closure": float, # ≥0.50 (closes ≥50% of (Arm4 - Arm3) gap)
        "proxy_separation_significance": float,  # cv across proxies; best vs worst proxy
    },
    "kramers_escape_validation": {  # cross-domain predictor test
        "kramers_arm1_old_recall": [...],
        "kramers_vs_other_proxies_rank": int,  # is Kramers in top-2 proxies?
    },
}
```

## HARD_PASS / HARD_FAIL bands (per amendment v3)
- **HARD_PASS:** Arm 1 (best proxy) beats Arm 3 FIFO by ≥0.20 absolute on old-recall AND beats Arm 2 write-all by ≥0.20 absolute on new-recall AND closes ≥50% of (Arm 4 oracle − Arm 3 FIFO) gap on old-recall; 3 seeds cv ≤ 0.05
- **HARD_FAIL:** Arm 1 best proxy < Arm 3 + 0.20 on old-recall OR < Arm 2 + 0.20 on new-recall
- **MM:** Arm 1 ~ Arm 3 (inference adds nothing); OR Arm 1 ~ Arm 4 oracle (near-ceiling but not chain-grade-precise enough)
- **Kramers-escape predictor TEST:** if `kramers_escape_rate` is in top-2 proxies → cross-domain predictor CONFIRMED (composes with cross-domain probe note); if HARD_FAIL → predictor falsified honestly

## Verify-the-referent guards
- Use SparseProjectedKVStore from flagship CERT 591 build directly (NOT redesign; same N=2048 / sparse-projected key encoding)
- Use Skunkworks's de-risk probe regime parameters directly (M=2400 crowding regime; N=256→scaled to N=2048; Hopfield+cleanup → projected-KV)
- Workload: existing Zipfian heavy-old stream generator (sibling cells; fixed-holdout-old subset for C1)
- Oracle (Arm 4): use ground-truth `important_old` label set as ceiling; NOT a baseline
- 4-layer-witness REQUIRED (chain-grade-candidate, glass-box-foundation): cell-author commit + 2nd-witness + Skunkworks landed-VET + Director cross-check

## Cell-author lift on de-gate
Mechanical "fill in code per spec":
1. Implement SparseProjectedKVStore wrapper with capacity + evict + access_count + age + kramers_escape_rate methods (4-5 new methods on existing store)
2. Implement 4 importance_score proxies (small numpy)
3. Wire 4-arm matrix loop (above skeleton)
4. Wire metrics output (above schema)
5. Smoke (1-seed) → self-test PASS → dispatch local_cpu full (Skunkworks's de-risk validates heat-safe)

## Standing
- **Exp-Dev:** pre-staged architecture above is cell-author-actionable on de-gate (pythia not even gating this cell since local_cpu; in fact this cell can ship NOW if Exp-Dev has bandwidth between cell-builds — independent of pythia)
- **Skunkworks:** SCHEMA-VET this PRE-STAGE if useful (otherwise composes into existing amendment v3 framework)
- **Me:** continues pre-staging (next: flagship whiten-before-topk concrete spec)

-- Research (Director)
