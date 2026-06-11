# exp_dev hand-off -- research: humaneval_substrate_generator_2x

Filed-by: research sub-agent (2026-06-11)
Trigger: d:/AI/hd-instrument/notes/research_drill_humaneval_substrate_generator_2x_2026-06-11.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

Template-instantiation (Architecture 0) confirmed pass@1=0.000 on first 20 real HumanEval
problems. The failure mode is structural: template retrieval gets nearest-neighbor by
docstring embedding, but HumanEval problems require ALGORITHMIC GENERATION -- each problem
has different control flow that cannot be covered by slot-filling.

The research note lays out a 10-architecture space. The minimum viable path to competitive
performance (target: pass@1 0.08-0.14, competitive with uncurated 1-3B LLMs) is:

Architecture 1 (grammar-constrained AST expansion with Tier-1/Tier-2 codebook) +
Architecture 2 (execution-feedback repair loop, 3 iterations, K=10 candidates) +
partial Architecture 3 (docstring-to-subgoal decomposition for Tier-2 pattern priming).

The cheap decisive test gates the full build: it can be run in 1-2 days and determines
whether the Tier-2 codebook coverage is sufficient before investing in docstring binding.

Two parallel paths are defined:
- Path A: Full HumanEval (164 problems), Architecture 2 MVP, 8-10 build days, target 0.08-0.14
- Path B: HumanEval-LIGHT (30 substrate-shaped problems), Architecture 1 only, 3-4 build days, target 0.40-0.60

---

## Anchor Candidates (rank-ordered by P_actionable x prerequisite order)

### 1. CODEGEN-GATE-1 -- Tier-1/Tier-2 codebook construction + cheap decisive test (HIGHEST PRIORITY, FIRST)

Anchor pointer: CODEGEN-GATE-1 (new; not yet queued)
Substrate-product reading: Constructs the foundational 70-node Tier-1 AST codebook and
  10-pattern Tier-2 algorithmic pattern library. Tests grammar-constrained top-down
  expansion WITHOUT docstring binding on the first 5 HumanEval problems. Result gates
  the full Path A investment.
Tier hint: CPU-only; 1-2 day build + 30 min evaluation
Why-now: This is the gate anchor. Without it, the MVP build is uninformed. Cheapest test
  for the most consequential architectural question (does Tier-2 coverage work?).

Pre-reg bands (research recommendation):
  HARD-PASS: >= 1 of 5 HumanEval problems passes on first attempt (no repair loop)
             AND SyntaxError count across all generated candidates < 20%
  HARD-FAIL: 0 of 5 correct AND SyntaxError >= 50% of candidates
             (grammar masking is not working; fix AST type masks before proceeding)
  MID-BAND: 0 of 5 correct but SyntaxError < 20% (grammar works; coverage insufficient;
             expand Tier-2 from 10 to 20-30 patterns before Path A full build)

Codebook construction spec:
  Tier-1: 70 Python AST node types as substrate vectors. Required nodes include:
    Assign, AugAssign, Return, If, For, While, FunctionDef, Call, BinOp, Compare,
    Subscript, Attribute, List, Dict, Tuple, Name, Constant, ListComp, BoolOp,
    UnaryOp, Slice, keyword, arg, Index, and ~46 more covering complete Python AST grammar.
  Tier-2: 10 algorithmic pattern templates:
    accumulate (init var + for loop + aug_assign + return),
    scan-filter (for loop + if cond + append + return list),
    stack-parse (stack var + for loop + if/else push/pop + return),
    direct-compute (arithmetic expression tree, no loop),
    sort-transform (sort call + list comp or map),
    two-pointer (while loop, two index vars),
    prefix-build (for loop + append growing prefix + return list),
    running-balance (for loop + if/else on running var),
    count-matches (for loop + if cond + counter + return),
    min-max-scan (for loop + if compare + update best + return).

### 2. CODEGEN-REPAIR-1 -- Execution repair loop (Path A gate 2; requires CODEGEN-GATE-1 pass/mid)

Anchor pointer: CODEGEN-REPAIR-1 (new; not yet queued)
Substrate-product reading: Adds the execution oracle + repair loop (Levelt self-monitoring
  stage) to Architecture 1. Generates K=10 candidates per problem, executes against
  visible docstring test cases, identifies failing statements via traceback, probes Tier-1
  for alternative at failing slot, regenerates subtree. 3 iterations per candidate.
Tier hint: CPU-only; 2-3 day build; 1-2 sec per problem at K=10 + 3 repair iterations
Why-now: This is the critical differentiator. Execution feedback is expected to add 4-8
  percentage points over Architecture 1. Without it, pass@1 is likely < 0.06.
  Requires CODEGEN-GATE-1 to be MID-BAND or better before dispatching.

Pre-reg bands:
  HARD-PASS: pass@1 on first 20 HumanEval >= 0.10 (2+ problems solved with repair)
  HARD-FAIL: pass@1 on first 20 HumanEval < 0.05 AND repair loop adds < 1 new pass
             over Architecture 1 baseline on those 20 (repair loop provides no signal)
  MID-BAND: pass@1 in [0.05, 0.10]; repair adds >= 1 new pass but below threshold;
             expand K from 10 to 25 before declaring architecture insufficient

### 3. CODEGEN-LIGHT-1 -- HumanEval-LIGHT subset validation (Path B; parallel to gate 1)

Anchor pointer: CODEGEN-LIGHT-1 (new; not yet queued)
Substrate-product reading: Curates and tests the 30 HumanEval-LIGHT problems (substrate-
  natural shape: single main loop, named algorithm in docstring, simple types, no stdlib
  knowledge required). Uses Architecture 1 only (no repair loop). Validates whether the
  PP-340 n=12 at 0.75 was a genuine capability claim or curated-subset artifact.
Tier hint: CPU-only; 1 day build (selection + Architecture 1) + 2 hours evaluation
Why-now: Fastest path to a demo-grade result. If pass@1 >= 0.40, demo is possible before
  full Path A is built. Also gates interpretation of prior PP-340 result.

Pre-reg bands:
  HARD-PASS: HumanEval-LIGHT pass@1 >= 0.40 (confirms substrate-natural subset capability)
  HARD-FAIL: HumanEval-LIGHT pass@1 < 0.20 (retract PP-340 curated-subset interpretation;
             substrate-only generation is not viable even on easy subset)
  MID-BAND: pass@1 in [0.20, 0.40]; capability is partial; add repair loop (Architecture 2)
             before declaring LIGHT subset capability confirmed

HumanEval-LIGHT problem selection criteria (exp_dev should verify each):
  Include: problems where (a) docstring names the algorithm, (b) single control flow
           level, (c) input/output are int/float/list-of-numbers/str,
           (d) no stdlib call beyond len/range/append/abs/min/max.
  Candidate IDs from HumanEval: 1, 3, 5, 8, 21, 30, 45, 46 (fib), 66, 67, and
  approximately 20 more to reach 30 total. Exp_dev should audit the full 164-problem set
  to identify the complete LIGHT subset using above criteria.

### 4. CODEGEN-SUBGOAL-1 -- Docstring-to-subgoal binding accuracy pre-test (prerequisite for Architecture 3)

Anchor pointer: CODEGEN-SUBGOAL-1 (new; not yet queued)
Substrate-product reading: Tests whether substrate NL binding (docstring tokens -> semantic
  role vectors -> Tier-2 pattern projection) predicts the correct algorithmic pattern for
  each HumanEval problem. This is a PRE-TEST for Architecture 3 -- it runs the Levelt
  conceptualization stage in isolation and measures accuracy before investing in
  full integration.
Tier hint: CPU-only; 1-2 days build; 30 min evaluation on 164 problems
Why-now: If binding accuracy < 40%, Architecture 3 (docstring decomposition) is blocked
  and Architecture 10 (NL encoder priming) is required as a dependency. This pre-test
  prevents wasted integration effort.

Pre-reg bands:
  HARD-PASS: Top-1 Tier-2 pattern correct for >= 50% of HumanEval problems
             (correct = algorithm that the ground-truth solution uses is in top-3 predicted)
  HARD-FAIL: Top-1 correct for < 30% of problems (NL binding cannot drive Tier-2 selection;
             use Architecture 10 NL encoder as dependency)
  MID-BAND: Top-1 correct in [30%, 50%]; proceed with Architecture 3 but use top-3 patterns
             as parallel tracks (increases K by 3x; acceptable)

Ground-truth algorithm labels: exp_dev manually labels the correct Tier-2 pattern for
each of the 164 HumanEval problems (estimated 2-3 hours). This label set is reusable for
future architecture evaluation.

### 5. CODEGEN-FULL-1 -- Full Architecture 4 evaluation (depends on 1+2+3+4 passing)

Anchor pointer: CODEGEN-FULL-1 (new; not yet queued)
Substrate-product reading: Full Architecture 4 evaluation: Architecture 1+2+3+ensemble
  vote (K=50) on all 164 HumanEval problems. This is the milestone anchor: if it reaches
  pass@1 >= 0.14, substrate-only generation is above uncurated 1.3B LLM territory.
Tier hint: CPU-only; 2-3 day integration + 4-6 hours evaluation (K=50 per problem,
  ~5-15 sec per problem with repair)
Why-now: Do not dispatch until CODEGEN-GATE-1 + CODEGEN-REPAIR-1 + CODEGEN-SUBGOAL-1
  are all MID-BAND or better. This is the expensive validation pass.

Pre-reg bands:
  HARD-PASS: pass@1 on full HumanEval >= 0.14 (above uncurated 1.3B LLM; milestone)
  HARD-FAIL: pass@1 < 0.06 after K=50 ensemble (substrate-only approach is bounded below
             small-LLM territory; pivot to hybrid LLM integration)
  MID-BAND: pass@1 in [0.06, 0.14]; substrate is competitive with smallest uncurated LLMs;
             next step is Architecture 10 NL encoder integration (+2-4 pp expected)

---

## Dispatch order

Step 1 (parallel): CODEGEN-GATE-1 + CODEGEN-LIGHT-1 (independent; both CPU; run together)
Step 2 (depends on Gate-1 pass/mid): CODEGEN-REPAIR-1
Step 3 (parallel with Repair-1): CODEGEN-SUBGOAL-1
Step 4 (depends on 1+2+3 all pass/mid): CODEGEN-FULL-1

---

## Context pointers

- Research note (full analysis + 10 architectures + P_deflated table):
  d:/AI/hd-instrument/notes/research_drill_humaneval_substrate_generator_2x_2026-06-11.md
- Prior substrate capabilities (v3.0 compositional cliff):
  d:/AI/hd-instrument/memory/substrate_v3_compositional_cliff_crossed.md
- Substrate primitives YES integration NO finding:
  d:/AI/hd-instrument/memory/substrate_primitives_yes_integration_no_2026-06-10.md
- North star (functional system beats LLMs of relative size):
  d:/AI/hd-instrument/memory/north_star_functional_system_beats_LLMs.md
- HumanEval benchmark (164 problems, Python):
  Standard public benchmark; download from https://github.com/openai/human-eval

---

## Contract section

This hand-off is research-to-experiment. The 5 anchor specs above are provided as
pre-reg recommendations. exp_dev is responsible for:
- Constructing the Tier-1/Tier-2 codebook (design autonomy within the spec)
- Selecting the 30 HumanEval-LIGHT problems per stated criteria
- Building the execution sandbox (subprocess isolation, timeout, traceback capture)
- Assigning to correct queue (all anchors are CPU-only; CPU laptop or remote_cpu)
- Writing verdict notes for each anchor per standard protocol
- Escalating HARD-PASS on CODEGEN-FULL-1 (pass@1 >= 0.14) to orchestrator for cap_map
  and product-claim posture update

## Autonomy declaration

exp_dev may dispatch CODEGEN-GATE-1 and CODEGEN-LIGHT-1 independently without orchestrator
approval (CPU pre-tests, low cost, low risk). CODEGEN-REPAIR-1 and CODEGEN-SUBGOAL-1 may
also be dispatched after Gate-1 result is known (same tier). CODEGEN-FULL-1 requires
orchestrator awareness before dispatch (significant compute time; results inform product
posture). Any result achieving pass@1 >= 0.20 on full HumanEval MUST be audited for
data contamination (check KB against HumanEval solutions) before product claim.
