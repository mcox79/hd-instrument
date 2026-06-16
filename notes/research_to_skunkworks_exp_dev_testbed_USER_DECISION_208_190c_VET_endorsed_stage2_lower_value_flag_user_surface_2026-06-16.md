# Research (Director) -> Skunkworks + Exp-Dev + Testbed + USER: DECISION 208 -- Skunkworks BINDING VET on 190c per-sibling adjudication ENDORSED (Skunkworks read SOURCE metrics.json directly + Exp-Dev's numbers MATCH exactly + per-sibling HONEST-NEGATIVE for clean generalization CONFIRMED + ARM-1 capabilities DISTRIBUTION-SCOPED CONFIRMED + 9th-catch ENDORSED + Stage-2 external-data procurement now LOWER VALUE flag to USER). FINDING atom filing GO -> Testbed ratify chain. USER surface: Stage-2 procurement direction (cardinality external-data; was conditional on Stage-1 pass) now LOWER VALUE per Stage-1 HONEST NEGATIVE; non-blocking on substrate-internal arcs but worth knowing before any procurement spend. Director 190e formal-oracle hookup design memo NEXT on my queue.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~18:51
**Re:** Skunkworks 190c VET binding + ratify chain complete; USER Stage-2 surface; 190e next.

## ACK Skunkworks BINDING VET (source-verified; chain complete)

```
Skunkworks INDEPENDENTLY read data/exp_cardinality_generalization_stage1_190c_cpu_v1/
metrics.json (run_mode=full) -- NOT the orchestrator preview. Exp-Dev's per-sibling
adjudication numbers MATCH the source EXACTLY. VET binding.

ENDORSEMENTS:
   EXACT-COUNT HONEST-NEGATIVE: CONFIRMED (C2 5.60 >> 1.0 bar; ARM-1 hit 0.209).
   MOST(A>B) MIDDLE: CONFIRMED (margin clears; acc misses by 2.5pts).
   ARM-1 capabilities DISTRIBUTION-SCOPED: CONFIRMED.
   9th verify-catch (Exp-Dev's smoke-artifact hypothesis REFUTED): CONFIRMED.
   FINDING-type filing: CONFIRMED.

DECISION-197 flag VINDICATED: RMSE>1.0 at full = HONEST-NEGATIVE, NOT artifact-
   dismissal. Skunkworks's explicit pre-flag operated correctly.

Ratify chain complete: Exp-Dev adjudication + Skunkworks VET match + Director
   ratify (DECISION 207) -> Testbed FINDING atom ratify chain GO.
```

## DECISION 208 -- USER Stage-2 surface (lower-value flag per Stage-1 result)

```
Skunkworks substantive flag: Stage-2 external-data procurement (cardinality
external-data via Steinert-Threlkeld and/or bAbI-7 recast) was CONDITIONAL
on Stage-1 PASS per DECISION 192. Stage-1 yielded HONEST NEGATIVE for clean
generalization. Stage-2 procurement is now LOWER VALUE.

USER surface (substantive update to standing procurement direction):
   Stage-2 was queued conditional on Stage-1 pass; Stage-1 yielded HONEST
   NEGATIVE. ARM-1 capabilities are DISTRIBUTION-SCOPED (work on their
   original regime; do NOT cleanly generalize to shifted higher-count
   distribution at N<=4096 with FROZEN operator).

   Spending procurement on Stage-2 external data (Steinert-Threlkeld
   quantifier data; bAbI-7 counting recast) is now LOWER VALUE because:
   (a) Stage-1 already establishes ARM-1 generalization is BOUNDED by
       distribution; external data would likely confirm the same bounded
       characterization at extra cost;
   (b) honest positives preserved (mechanism directionally transfers;
       N-scaling monotonically improves; HONEST extrapolation untested at
       higher N) -- these can be EXPLORED via additional substrate-internal
       runs at higher N rather than external data;
   (c) future Phase C TIER-3 foundation build (residue-FPE + Hopfield-cleanup)
       may produce capabilities with better generalization surface (the
       continuous-magnitude reasoning is structurally different from
       integer-cardinality counting) -- worth waiting on that surface before
       external-data spend.

   Director RECOMMENDATION: DEFER Stage-2 procurement until at least one of
   the following:
   (i) USER wants substantive external validation of the SCOPING characterization
       (vs. the substrate-internal generalization-not-refit characterization);
   (ii) Phase C TIER-3 foundation build produces new capabilities that need
       external validation;
   (iii) Drill 5 or other research-drill surfaces a new question external
       data could address.

   Otherwise: skip Stage-2 procurement; the Stage-1 HONEST NEGATIVE finding
   suffices to characterize ARM-1 distribution-scoping.

   Your call; non-blocking on substrate-internal arcs.
```

## DECISION 208a -- 190c FINDING atom Testbed ratify chain GO

```
Testbed: ratify the 190c FINDING atom per Exp-Dev's proposed draft + Director
endorsement (DECISION 207b) + Skunkworks BINDING VET (this DECISION):

   Atom spec:
      +concept::FINDING_cardinality_arm1_distribution_scoping (or Testbed
        naming convention)
      kind: FINDING (NOT capability)
      metric_type: GENERALIZATION_TRANSFER
      desc: HONEST NEGATIVE + HONEST POSITIVES both stated; mechanism
            directionally transfers + N-scaling monotonically improves;
            untested extrapolation honestly labeled
      DEPENDS_ON: T3/cleanup_distinct_count + CAP_cardinality_recall_exact_count_single_role
                  + CAP_cardinality_quantifier_most (real lineage; NOT
                  floating fact)
      provenance: run_mode=full + n_seeds=5 + VOCAB=200 + N{2048,4096} +
                  operator_cleanup_thresh_LOCKED=0.30 (generalization-NOT-
                  refit preserved) + cell SHA + cpu + elapsed=268.75s
      Net: +1 FINDING atom; cap_pres=1.0 preserved (no capability mutation;
           ARM-1 capabilities unchanged; distribution-scoping CHARACTERIZED).

   STRICT type-discipline enforced (kind:FINDING + metric_type:GENERALIZATION_TRANSFER;
      both labels load-bearing for downstream querying).

ALSO in flight: 190f drift_kappa3 FINDING atom ratify (Exp-Dev 224th + Director
   DECISION 193a + Skunkworks endorsement).

Two FINDING atoms entering substrate this session (distribution-scoping +
drift-detection); both honest characterizations + real lineage; not capability
claims; both have metric_type label distinguishing from capability-recall.
```

## Pipeline state (post-DECISION-208)

```
PHASE C TIER-3 ARC:
   190a CANCELED per Option A
   190b paper-design + R1 + R2 literature base COMPLETE
   190c FINDING atom in Testbed ratify chain (this DECISION) + USER Stage-2
        lower-value flag surfaced
   190d folded
   190e Director hookup design memo: NEXT on my queue (after this commit)
   190f drift_kappa3 FINDING atom in Testbed ratify chain

Sessions:
   Skunkworks: 190c VET DELIVERED + ENDORSED; 190f type-VET on Testbed landing
                pending + 190e hookup VET when drafted; standing
   Exp-Dev: 190c adjudication COMPLETE + 9th-catch documented; PRIMITIVE 2
            cell-gate sketch standing for future foundation build
   Testbed: 190c + 190f FINDING ratify chains (priority; parallel)
   Orchestrator: state collector refreshes; heartbeat_watchdog supervisor
                 wrapper hardening queued (separate sweep; 87th)
   Research (Director): 190e formal-oracle hookup design memo NEXT (after
                        this commit) + 13th-rule active state-check armed

USER standing items UPDATED:
   1. formal-oracle external-rater procurement direction (190e queue; my
      hookup design memo coming)
   2. 190c Stage-2 external-data procurement: NOW LOWER VALUE flag per
      Skunkworks; Director RECOMMENDATION DEFER unless (i)-(iii) above
   3. Phase C TIER-3 foundation-first 2-primitive build timing (R1+R2
      literature base complete; ready for USER GO)
   4. TRACK B-via-Option-C ARM-3 parity-immune redesign (future arc if
      desired)
   5. 3 TRACK D design Q's (palette / tab strategy / corpus scope; iterate at
      visual review)

Substrate state (post-190c + 190f ratifies): +2 FINDING atoms;
   cap_pres=1.0 PRESERVED.
```

## Safety / invariants

- ASCII only
- 11th + 18th + 19th + 21st + 22nd rules preserved
- 19th rule: 88 instance types empirical (no new candidate this turn)
- 22nd rule: progressive (FINDING-atom characterization of ARM-1 distribution-
            scoping is honest substrate-product positioning content)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

208 cumulative decisions. **243+ honest signals.** 88 audit-discipline instance
types empirical. Phase C TIER-3 arc consolidating: 190c FINDING in Testbed
ratify chain; Director 190e queue next.

---

**Skunkworks (Auditor):** BINDING VET ACK; Stage-2 lower-value flag SURFACED
to USER; ratify chain complete. Standing for 190f atom type-VET on Testbed
landing + 190e hookup VET when drafted. R1+R2 lit-scans complete; literature
base ready for foundation build.

**Exp-Dev (Prover):** 190c adjudication END-TO-END complete; FINDING atom in
Testbed ratify chain. 9th verify-catch + 88th candidate documented.

**Testbed (Integrator):** 190c FINDING + 190f drift_kappa3 FINDING ratify
chains parallel (STRICT type-discipline; metric_type labels enforced);
cap_pres=1.0 preserved (no capability mutation in either; both honest
characterizations).

**USER:** Substantive update -- 190c Stage-1 yielded HONEST NEGATIVE for clean
generalization; ARM-1 cardinality capabilities formally characterized as
DISTRIBUTION-SCOPED (real on their original regime; not generally portable).
HONEST POSITIVES preserved (mechanism directionally transfers; N-scaling
monotonically improves; extrapolation untested honestly labeled). Stage-2
external-data procurement (was conditional on Stage-1 pass) is now LOWER
VALUE. Director RECOMMENDATION: DEFER Stage-2 unless you want external
validation of the SCOPING characterization. Non-blocking on substrate-internal
arcs.

Tag: DECISION_208_skunkworks_VET_endorsed_chain_complete_USER_stage2_lower_value_flag_director_recommend_defer_190c_FINDING_testbed_ratify_GO -- Research (Director)
