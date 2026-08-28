---
cell: experiments/exp_semantic_control_intrinsic_demand_v1.py
mode: full
queue: remote_cpu_queue
timeout_s: 3600
results_path: data/exp_semantic_control_intrinsic_demand_v1/metrics.json
self_test: green
smoke: green
question: Can a GOLD-BLIND, brain-faithful INTRINSIC demand signal -- inter-channel DISAGREEMENT (the spread of the meaning channels' verdicts on a pair) and/or retrieval AMBIGUITY (the entropy of a word's nearest-neighbor similarities) -- route the meaning systems well enough to close the gap between the fixed reliability-weighted blend and the oracle TASKSET arm that is HANDED each item's true task label? I.e. can the substrate route the way the IFG does (from internal competition, no external task tag) instead of needing the label?
gate: PASS iff a gold-blind intrinsic-demand gate (DISAGREEMENT / AMBIGUITY / COMBINED) beats FIXED_BLEND CI-separated (paired Delta-rho on the pooled SimLex+WordSim+SimVerb eval) AND closes a MEANINGFUL fraction of the FIXED_BLEND->TASKSET_ORACLE gap, AND its SHUFFLED_* info-free twin (demand cue permuted across items) does NOT beat FIXED_BLEND. Report fraction-of-gap-closed + per-task rho + the CONFLICT_PRIOR (reused hdlab.semantic_control) baseline it must beat. RIGOROUS_NEGATIVE (a FULL PASS): if NO intrinsic signal beats the blend / closes the gap, that shows per-item routing needs top-down task context -- and the brain is NOT gold-blind (PFC task set; in the integrated reader the demand is available from the reading context), so the TASKSET arm is a FAIR model of the reader's inference-time signal, not an oracle cheat. State which conclusion the data supports and where the substrate's task context comes from at inference.
kb_referents:
  - data/exp_learner_safety_gate_v1/parsed_simplewiki_150000tok_posfixed.jsonl
  - data/exp_structured_context_learner_v1/parsed_simplewiki_15000000tok.jsonl
  - data/encoder_eval_benchmarks/simlex999.txt
  - data/encoder_eval_benchmarks/simverb3500.txt
  - data/encoder_eval_benchmarks/wordsim353_combined.csv
  - data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv
  - data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt
---
# REMOTE_RUN_REQUEST -- exp_semantic_control_intrinsic_demand_v1 (fidelity phase 3, DRILL #7: intrinsic IFG-style demand routing)

Solver-dropped request; the strategy/orchestrator lane runs the fulfiller (validates, writes prereg, ships code+data, queues CPU).

## Brain claim (PINNED)
The IFG/pMTG semantic-control network (Lambon Ralph controlled-semantic-cognition; Jefferies; Badre &
Wagner conflict) routes between meaning systems by detecting demand INTRINSICALLY -- from competition
among currently-active representations -- NOT from a supervised task tag. The prior drill
exp_semantic_control_routing_v1 (WIN) showed the TASKSET arm (given each item's TRUE task tag) beats
the fixed blend, but its GOLD-BLIND CONFLICT arm underperformed (0.253). So the brain routes without
the oracle and our gold-blind mechanism could not match it. This drills whether a more brain-faithful
intrinsic signal -- inter-channel DISAGREEMENT and retrieval AMBIGUITY -- closes the gap.

## Arms (one variable = the routing/control signal; channels DEP/WIN/GRND/SELP, PPMI-SVD k=500, fit on split A score on B)
- FIXED_BLEND [FLOOR] = one global reliability-weight vector for all items.
- TASKSET_ORACLE [CEILING, uses the label] = per-task weights applied by the item's TRUE task tag (the gap to close).
- CONFLICT_PRIOR [gold-blind underperformer] = reuse hdlab.semantic_control conflict/suppression verbatim (reproduce the ~0.253 baseline).
- DISAGREEMENT [NEW, gold-blind] = per-item gain from the population std of the item's z-scored channel values (>=2 channels).
- AMBIGUITY [NEW, gold-blind] = per-item gain from normalized entropy (softmax tau=0.2) of each word's top-10 neighbor cosines, meaned over channels + the pair.
- COMBINED [NEW, gold-blind] = z(disagreement)+z(ambiguity), same gate mechanism.
- SHUFFLED_{DISAGREEMENT,AMBIGUITY,COMBINED} [INFO-FREE TWINS] = demand cue permuted across items (fixed seed). MUST LOSE.
Gain function: theta_lo/theta_hi = 80th/95th pct of the demand stat on split A; per-item gain interpolates w_low->w_high through the same fusion as every arm. Score paired_delta rho + ci_half + null_p95 on pooled + per-task.

## Compute / remote-safety
remote_cpu_queue (numpy/scipy/sklearn; hdlab.semantic_control is pure numpy; hdlab.grounded_similarity
uses torch CPU tensors -- same precedent as exp_semantic_control_routing_v1 / exp_grounding_supply_v1
already on remote_cpu_queue). Loads the 15M PRE-PARSED cache; NEVER parses (no spaCy token in the file;
parse_and_cache never called). bare == FULL (line 824: `smoke = bool(args.smoke) or (args.mode ==
"smoke")`; the remote runner passes no --mode). --self-test (incl. the entropy positive control +
arms-must-differ) + --smoke (13/13 arms hash-distinct, all three new gates calibration_ok) GREEN.
metrics.json written INCREMENTALLY per channel-build (partial:true / arms_done; atomic tmp+os.replace;
mode-keyed _ckpt dir). 150k-smoke reads gap slightly negative (channels data-starved) -- the gate-closing
question is THIS 15M run where DEP/WIN/GRND/SELP carry task-differentiated signal. timeout 3600 (mirrors
the sibling routing cell).

## Results
data/exp_semantic_control_intrinsic_demand_v1/metrics.json (pooled + per-task rho, paired deltas + CIs,
fraction-of-gap-closed, gate booleans, calibration diagnostics), synced back ~20 min. NOTE the standing
infra gotchas: hd_metrics_sync is DISABLED (pull manually via the orchestrator) and the runner writes a
double-prefixed data/exp_exp_<name>/ path (SH-4). Strategy does NOT integrate -- WIP until owner_verdict:
DONE; to be VETTED before folding into SOLVED.md.
