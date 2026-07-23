# Prereg: multipred_argstruct_agentfix_kbgate_v3

Date: 2026-07-23. Local, inline, foreground-to-completion. Pause-state ACTIVE (verified absent); no
queue_add; not banked (skunkworks VETs separately).

## What this builds

Integrates the TWO levers banked this session into one reader, and closes the specific bound the
29478 (`exp_multipred_depparse_argstruct_recall_v2`) VET localized:

1. **Parse-scoped candidate generation extended to ALL core arguments (agent/subject AND patient).**
   29478's `assign_candidates_to_predicates` assigns a candidate to a predicate ONLY by ascending the
   decoded head-chain until it hits a predicate token or root. MEASURED (manual trace over 29478's own
   12 regressed items, this cell's design probe, 2026-07-23): at least 7/12 regress because the
   out-of-domain, imperfect (UAS=0.7882) transition parser either (a) inverts the aux/modal<->content-verb
   attachment (aux made head, main verb its own dependent -- e.g. `L04_02` "The playful cat **had**
   rubbed against his mimic castle": head(cat)=had, head(rubbed)=had, so ascending from "cat" hits "had"
   [not a predicate] then root, never reaching "rubbed"), or (b) mis-roots the SUBJECT NP itself with the
   predicate as ITS dependent (e.g. `L07_20` "Some men ... **saw** the boys": head(men)=root,
   head(saw)=men). Both are the SAME shape: the predicate is reachable from the candidate via ONE
   head-edge hop in the OPPOSITE direction, not by pure ascent. FIX: a two-pass walk -- PASS 1 = the
   exact old ascend-only walk (zero regression risk for candidates already correctly placed, e.g. direct
   patients); PASS 2 (fallback, engages ONLY when PASS 1 never reaches a predicate) = walk the SAME
   visited chain (candidate + every non-predicate ancestor visited) and, at each node closest-first,
   check for a DIRECT CHILD that is a predicate. This is a strict superset of the old mechanism.
2. **Scaled LLM+KB-vetted selectional knowledge (29479, `scaled_seed_table_v1.json`, 579 verb|noun
   ratings) as a patient-disambiguation gate.** When a predicate has >=2 locally-assigned candidates the
   role-classifier labels PATIENT, keep only the argmax-`sel(verb_lemma, noun)` one (OOV -> no signal,
   loses to any rated candidate; deterministic leftmost tie-break). This directly wires the 29479 lever
   into the multi-predicate reader's patient selection (previously v2 emitted EVERY PATIENT-labeled local
   candidate as a separate tuple with no plausibility-based pruning).

## Arms (six; role-assignment clf, subcat-gate mechanism, and parser training all UNCHANGED per the
ONE-VARIABLE mandate -- the variable is the assignment mechanism + the knowledge gate)

- `BASELINE` -- the real single-main-verb reader (`exp_learned_argstruct_parser_lccp_independent_gold_v1`
  reader_svo), byte-identical reuse. This is 29473's own reader.
- `V2_FRAMES_29478` -- 29478's own landed FRAMES arm, reproduced EXACTLY by calling 29478's own
  `run_all_arms` (same parser weights, same code) -- guarantees byte-identical numbers to the cited
  landed metrics (F1=0.4478, recall_ceiling=0.60, precision=0.3571, n_regressed=12).
- `V3_PARSEFIX_ONLY` -- the fixed two-pass assignment + the SAME learned subcat gate mechanism, NO
  knowledge gate. Isolates the parse-fix's own contribution.
- `V3_INTEGRATED` (HEADLINE) -- fixed assignment + learned subcat gate + knowledge argmax-disambiguation.
- `V3_ARCSCRAMBLE` -- fixed assignment on deterministically SCRAMBLED decoded head arcs (reuses 29478's
  `scramble_heads`) + knowledge gate. MUST-FAIL CONTROL (a): isolates whether the REAL parse structure
  (not just "the new assignment mechanism") carries the signal.
- `V3_KNOWLEDGE_SCRAMBLE` -- fixed assignment + learned subcat gate + the 29479 table's VALUES permuted
  across (verb,noun) keys (fixed seed, `sorted(set)` ordering). MUST-FAIL CONTROL (b): isolates whether
  the knowledge table's CONTENT (not merely engaging an argmax-among-candidates mechanism) carries any
  gain.

## Measured (per arm, vs the SAME independent LCCP gold / same split as 29473/29478)

recall_ceiling, precision, recall, F1 (via `L.score_arm`, byte-identical formula reused); n_regressed /
n_recovered vs BASELINE (via `covered_set` diffs, reused); a REGRESSION-CAUSE classifier
(`diagnose_regression_causes`) that replays 29478's own pipeline (old assignment, old gate) per regressed
item and tags `AGENT_ROUTING_DROP` (patient candidate WAS locally reachable but no agent resolved,
local-or-carried) vs `PATIENT_OR_ENUM_DROP` (patient itself never reached) vs `OTHER_ROLE_OR_GATE_DROP`
vs `VERB_NEVER_ENUMERATED`; then checks what fraction of the `AGENT_ROUTING_DROP`-tagged items are
recovered in `V3_INTEGRATED`'s covered set. Learning curve = the SAME role-assigner clf's F1 on the
V3_INTEGRATED pipeline (assignment + gate + knowledge held fixed) vs ORC.TRAIN fraction
(0.25/0.5/0.75/1.0, 4 points, cardinality-gated) -- the FLEXIBLE/IMPROVING property.

## Pre-registered bands (SET BEFORE RUNNING; grounded on the 29478 landed MEASURED anchor -- F1=0.4478,
recall_ceiling=0.60 -- not a blind theoretical estimate, so tight decisive bands are appropriate, not the
calibration-probe ±50% widening reserved for anchor-free probes)

`HARD_PASS_INTEGRATION_LIFTS_PAST_FIND_LEG` -- ALL of:
  - F1(V3_INTEGRATED) >= 0.4678 (0.4478 + 0.02, strictly past 29478's F1, >5% of a reasonable band width)
  - recall(V3_INTEGRATED) >= 0.62 (strictly past 29478's 0.60 recall_ceiling floor-hug)
  - precision(V3_INTEGRATED) >= precision(V2_FRAMES_29478) - 0.03 (precision holds, 29478's own tolerance)
  - F1(V3_INTEGRATED) > F1(V3_PARSEFIX_ONLY) + 0.01 (the knowledge gate itself adds, beyond the parse fix)
  - agent_routing_closure_fraction >= 0.5 (at least half of the classified AGENT_ROUTING_DROP items from
    29478 are recovered in V3_INTEGRATED's covered set)
  - F1(V3_ARCSCRAMBLE) <= F1(V3_INTEGRATED) - 0.05 (must-fail control a: real parse structure carries it)
  - F1(V3_KNOWLEDGE_SCRAMBLE) <= F1(V3_PARSEFIX_ONLY) + 0.02 (must-fail control b: scrambled table adds
    ~nothing over parse-fix-alone -- the knowledge CONTENT, not mere argmax mechanics, carries any gain)

`HARD_FAIL_INTEGRATION_BOUNDED_CEILINGS_COMPOUND` -- ANY of:
  - F1(V3_INTEGRATED) <= 0.4478 (does not lift past the find-leg cell at all)
  - recall(V3_INTEGRATED) <= 0.60 (does not clear 29478's own recall floor)
  - agent_routing_closure_fraction < 0.25 (the localized regression class does not meaningfully close)
  - F1(V3_INTEGRATED) <= F1(V3_PARSEFIX_ONLY) (knowledge gate adds nothing/negative at the integrated
    level -- component ceilings compound per the banked 29462 scale-collapse finding)
  - F1(V3_KNOWLEDGE_SCRAMBLE) >= F1(V3_INTEGRATED) - 0.01 (must-fail control b fails to fail: scrambled
    table does almost as well as the real one -- the gain isn't from knowledge CONTENT)

`MIDDLE_BAND`: otherwise (genuine but partial signal; localize which condition failed).

## Fairness / anti-cheat

Same reader/gold/split as 29473/29478 (FULL_SLICE = L04/L05/L07/L08/L09/L10/L12; SMOKE_SLICE = L04/L05;
gold = `data/gold_mcguffey_lccp_argstruct_v1.json`, independent single-annotator, never read while
authoring the assignment fix or reading the knowledge table). ONE variable = assignment mechanism +
knowledge gate; parser training, role-assignment clf, subcat-gate mechanism all byte-identical reuse of
29478's own code (imported, not re-transcribed) to guarantee a fair, exact `V2_FRAMES_29478` reproduction.
Knowledge table built at BUILD TIME (29479, LLM+KB-vetted), runtime = pure glass-box dict lookup, NO LLM
at inference. Anti-cheat: knowledge-scramble control (must collapse any knowledge-specific gain) +
parse-scramble control (reused from 29478, must collapse the parse-structure-specific gain).

## Compute architecture

Class (b) sequential-CPU with justification -- one dynamic-oracle arc-eager parser training pass (reused
29478 code, ~50-65s foreground) + per-clause greedy decode (ms/clause) + per-predicate role
classification (existing AveragedPerceptron) + O(candidates) dict lookups (assignment walk + knowledge
table). No matmul/storage/GPU-batchable primitive. Storage: no_storage. Runtime invariant: glass-box
(trained parser + curated dict + corpus-observed admissibility table + a build-time-authored knowledge
dict), NO LLM/network/autograd at inference. LOCAL-ONLY, foreground-to-completion, no queue_add, not
banked.

## Timeout / ETA

29478's own FULL run took 219.94s wall (parser train ~62s + 5 arm passes). This cell adds ~1-2 more arm
passes (V3_PARSEFIX_ONLY, V3_INTEGRATED, V3_ARCSCRAMBLE, V3_KNOWLEDGE_SCRAMBLE = 4 new passes vs 29478's
5) plus a diagnostic regression-cause replay (1 more pass, bounded to only the ~12 regressed items'
sentences) plus the learning curve (4 fit+decode passes, reused unchanged). ETA: ~5-7 minutes foreground
(parser training dominates at ~50-65s; each arm pass over 163 FULL_SLICE sentences is a few seconds).
