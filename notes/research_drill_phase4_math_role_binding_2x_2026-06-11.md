# research_drill_phase4_math_role_binding_2x_2026-06-11

2x DEEP research drill on role-binding limiter for substrate math word-problem solver.
Generic literature only; ASCII; no substrate-novel mechanism names.

## HEADLINE

Role-binding is the universally-acknowledged ceiling on structured math-word-problem
(MWP) solvers, and the broader literature does NOT validate the conclusion
"dependency parser is the only path forward." Three converging lines of evidence
reframe the problem:

(1) Dominant-error mode "which-number-in-which-role" is the SAME failure mode the
    1990s-2010s symbolic-MWP literature hit; their resolution was NOT dependency
    parsing alone but joint inference under constraints (ILP / CSP over
    candidate role assignments).
(2) Modern SRL has produced multiple no-parser routes: syntax-aware-without-parser
    (joint auxiliary loss), supertag-based shallow parsing, and number-centered
    synthetic semantic graphs - none of which require a separate dep-parser
    component.
(3) Cog-neuro evidence locates thematic-role assignment in PFC working-memory
    plus parieto-temporal verb-argument retrieval - NOT in any "dedicated parser"
    module. The brain solves role-binding as constrained-retrieval-under-WM,
    not as parse-then-bind.

Net: the architect's conclusion "dependency parser needed" is ONE feasible path
but it is empirically dominated in the literature by joint-constraint solvers
that use shallow features + verb argument frames + global integer-programming
inference. Recommended pivot: a constraint-based role-assignment layer (bipartite
matching with verb-frame + unit-cue + position priors) BEFORE committing to a
multi-day dep-parser build.

## Cheap decisive test

Before building a dependency parser, run a 2-3 day prototype of constraint-based
role assignment:

  Inputs (already available in substrate): extracted quantities + unit cues +
  candidate schema templates + verb tokens + linear position.

  Mechanism: For each retrieved schema, formulate role-assignment as a bipartite
  matching problem (numbers <-> schema slots) with cost matrix C[i,j] composed of:
    - unit-cue affinity (existing partial-ceiling signal)
    - verb-argument compatibility (lookup from a small verb-frame table built
      from training set: ~100 high-frequency verbs)
    - linear-position prior (P(role | sentence-position))
    - quantifier-word adjacency feature (per Quantity Tagger lit: numbers
      attend to "every" / "how many" / "each" - cheap n-gram feature)
    - asked-quantity heuristic: question-sentence number gets ASKED role with
      high prior.

  Solve with Hungarian algorithm (O(n^3), n <= 10 typically) per candidate
  schema; pick schema+assignment with min total cost.

  Cost: ~2 days build + lookup-table compile. NO neural training. NO parser.

If this prototype lifts end-to-end accuracy materially over unit-cue-only,
the architect's dep-parser conclusion is REFUTED: the bottleneck is structured
inference over existing features, not deeper syntactic parsing.

## Falsifiable predictions

HARD-PASS: bipartite-matching role-assigner with verb-frame + position + unit
features lifts end-to-end accuracy by >= 10 absolute points over the current
unit-cue-only ceiling on the same held-out problem set, with NO dep-parser.
Implication: dep-parser is NOT the limiter; structured inference is.

HARD-FAIL: bipartite-matching role-assigner lifts < 3 absolute points, OR drops
accuracy. Implication: features available without parsing are genuinely
insufficient; the architect's conclusion stands and dep-parser (or pretrained
SRL model) is justified.

MIDDLE band (3-10 points): partial validation; suggests verb-frame coverage is
the bottleneck, NOT parsing per se - response is expand verb-frame lookup table
(cheap), not build a parser.

Calibration penalty applied: lit-scan agents would estimate P(HARD-PASS) around
0.55-0.65 based on the consistent reports that structured-extraction + symbolic
solving CAN reach SOTA when role-binding is solved (Mitra-Baral 2016 frame-id
solver; Kushman 2014 template-fill; neural-symbolic solvers report 90%+ on
benchmarks with proper extraction). Deflated by 0.20 for substrate-specific
uncertainty: P_deflated(HARD-PASS) = 0.40. P_deflated(HARD-FAIL) = 0.25.
P_deflated(MIDDLE) = 0.35.

## Cross-thread synthesis

Five distinct literatures converge on the same conclusion:

### A. NLP / MWP-solver literature (Q1, Q4, Q5)

- Sundaram 2024 (WIREs survey) and "Why are NLP Models Fumbling at Elementary
  Math?" both identify quantity-to-role mapping as the dominant error mode
  across template-based, seq2seq, seq2tree, and graph-based solvers.
- Microsoft Research 2021 ("Are NLP Models really able to Solve Simple MWPs?")
  showed SOTA neural solvers rely on shallow heuristics and break under
  minor entity-swap perturbations - exact mirror of the substrate's
  role-binding fragility.
- Number-Centered Synthetic Semantic Graph (NC-SSG) explicitly REORGANIZES
  the dependency-tree layout AROUND numerical elements - showing that "dep-parse
  then bind" is the wrong frame; "extract numbers first, structure around them"
  is the productive frame.
- Quantity Tagger (Roy & Roth 2019, EMNLP): latent-variable sequence labeling
  that tags each quantity with operation-relevant info using a learned latent
  span - NO parser. Achieved competitive performance.
- Kushman 2014 (template-based) + Hosseini 2014 (verb-categorization) both
  built competitive systems WITHOUT dependency parsing as the core mechanism;
  template-slot-filling under structural constraints carried the load.
- Neural-symbolic solvers report 90.4% on Math23K with structured
  extraction + symbolic solver - confirming Q5: structured-extraction +
  symbolic solving CAN reach competitive accuracy if role-binding is solved.
- Punyakanok et al. ("The Necessity of Syntactic Parsing for SRL"): full
  dep-parsing is NECESSARY only at the high-accuracy regime; shallow parsing
  with rich features approaches it. For a MWP solver that is currently far
  from SOTA, shallow features are sufficient.

### B. Cognitive neuroscience (Q2)

- Working memory IS the dominant load on MWP solving (Wang et al. 2025;
  Frontiers 2022); central-executive + visuospatial sketchpad + phonological
  loop integrate problem semantics into schema slots.
- Prefrontal cortex stimulation (tDCS) flips role-binding errors from N400
  (semantic anomaly) to P600 (revision/update) signatures - meaning PFC
  performs ACTIVE revision of role assignments under conflict, not one-shot
  parsing.
- Aphasia studies (Brain Communications 2025): thematic role errors come from
  TWO dissociable lesions - morphosyntactic (frontal) AND verb-argument
  retrieval (parieto-temporal). Brain does role-binding via TWO mechanisms,
  not one parser.
- Implication for substrate: matching the brain's architecture means BOTH a
  shallow-syntactic feature stream AND a verb-argument-frame retrieval stream
  feeding a joint-inference module - not a monolithic parser.

### C. Cognitive science / role-filler binding (Q3 + cog-sci portion of Q2)

- Smolensky / Hummel / Holyoak / Plate vector-symbolic role-filler binding
  literature: role-binding solved by tensor-product or circular-convolution
  binding with active dynamic-binding-plus-conjunctive-coding hybrid.
- Schematic-knowledge role-filler binding (Chen et al. 2019 arxiv): networks
  CAN learn role-filler binding from schemas WITHOUT explicit syntactic
  supervision, given the right architectural priors.
- Substrate already has the role-filler binding primitives (per memory index:
  cross-domain SLIPNET relation-type pattern). The bottleneck is the
  ROLE-ASSIGNMENT decision, not the role-filler binding mechanics.

### D. Biology (Q3): role-assignment as bipartite matching

- Ant colony task allocation (Cornejo et al.): distributed randomized algorithm
  with O(log n) convergence to near-optimal division-of-labor using only
  binary feedback. Maps to: role-assignment over numbers as a distributed
  matching problem with cheap local features.
- Artificial Bee Colony algorithm: three-role partition (employed / onlooker /
  scout) is decided per-iteration based on local fitness - exactly the
  role-binding architecture, decided by features not by parsing.
- Generalization: biology solves "which-entity-in-which-role" as iterative
  constraint-satisfaction with local cues + global feedback, NOT as a
  syntactic parse. This is the same mathematical structure as bipartite
  matching with cost matrix.

### E. New math (Q6): graph-theoretic + optimization-theoretic

- Joint constraint-satisfaction SRL (Punyakanok, Roth) used ILP for global
  inference over candidate role labelings - off-the-shelf for substrate.
- Hungarian algorithm for assignment problem: O(n^3), n <= 10 typical for
  MWPs. Solvable in microseconds. NO neural training. Cost matrix can be
  hand-engineered then learned.
- Quantum walks on attributed graphs (Rossi 2018) and continuous-time
  matching: graph-theoretic generalizations of bipartite matching with
  attribute-aware weights - relevant if multiple plausible schemas compete.
- Unit Dependency Graphs (Roy & Roth 2017): explicit graph structure between
  units, used for arithmetic word problems - cheap compact alternative to
  dep-parse.
- Heterogeneous Line Graph Transformer for MWPs: directly demonstrates that
  custom graph structures over numbers + descriptive words OUTPERFORM
  dep-parse-based methods on standard benchmarks.

## Substrate-product implications

1. The architect's "dep-parser needed" conclusion is premature. The literature
   consistently shows that for MWP role-binding, structured inference over
   shallow features beats dep-parsing in cost-effectiveness, and matches it
   in accuracy until very-high-accuracy regimes.

2. Recommended substrate move: build a role-assignment LAYER (bipartite
   matching with engineered cost matrix) as Tier-2 substrate bundle. This
   composes with existing extraction + schema retrieval + reasoning primitives
   WITHOUT introducing a new dependency on an external parser.

3. The cost matrix entries (unit-cue affinity, verb-frame compatibility,
   position prior, quantifier adjacency) are all derivable from features the
   substrate already extracts. The substrate-classical NL methods memory
   (count-based statistical methods stored as substrate Tier-2 bundles) is
   the right precedent: build a verb-argument-frame lookup table at Tier-2
   substrate, use it as a feature stream.

4. Substrate-product positioning: "the substrate solves role-binding via
   constraint-optimization rather than parsing" is a clean differentiator from
   LLM-only and parser-based MWP solvers. It also aligns with the existing
   substrate-LLM-boundary memory (substrate = structural reasoning;
   LLM-only = NL parsing) - role-assignment is structural reasoning, not NL
   parsing, contrary to the architect's framing.

5. If the bipartite-matching prototype HARD-PASSES, the multi-day dep-parser
   build is killed. If HARD-FAILS, the dep-parser build is justified WITH the
   added insight that verb-argument-frame retrieval should accompany the
   parser (cog-neuro: parieto-temporal stream).

6. If MIDDLE band: expand the verb-frame lookup table (cheap, days not weeks)
   before committing to parser. Verb-frame coverage is the obvious next bump.

## Exp_dev handoff signal

Findings are exp_dev-actionable. A companion handoff file is being written at
notes/exp_dev_handoff_research_phase4_math_role_binding_2026-06-11.md
proposing: bipartite-matching role-assigner anchor as Tier-2 prototype.

## Citations (verified)

NLP / MWP solvers (Q1, Q4, Q5):
1. Sundaram et al. 2024, WIREs Data Mining: "Does a language model understand high school math? A survey of deep learning based word problem solvers"
   https://wires.onlinelibrary.wiley.com/doi/10.1002/widm.1534
2. Patel et al. 2021, NAACL: "Are NLP Models really able to Solve Simple Math Word Problems?"
   https://arxiv.org/pdf/2103.07191
3. Roy & Roth 2019, EMNLP: "Quantity Tagger: A Latent-Variable Sequence Labeling Approach"
   https://arxiv.org/abs/1909.00176
4. Kushman et al. 2014, ACL: "Learning to Automatically Solve Algebra Word Problems" (template-based)
5. Hosseini et al. 2014, EMNLP: "Learning to Solve Arithmetic Word Problems with Verb Categorization"
6. He et al. 2020+, neural-symbolic solver for MWPs with auxiliary tasks (90.4% on Math23K)
   https://aclanthology.org/2021.acl-long.456.pdf
7. He-Yueya et al. 2023: "Solving Math Word Problems by Combining Language Models With Symbolic Solvers"
   https://arxiv.org/abs/2304.09102
8. Heterogeneous Line Graph Transformer for Math Word Problems
   https://arxiv.org/pdf/2208.05645
9. Number-Centered Synthetic Semantic Graph (NC-SSG):
   https://www.sciencedirect.com/science/article/abs/pii/S0925231225007143
10. Roy & Roth 2017: "Unit Dependency Graph and its Application to Arithmetic Word Problem Solving"
    https://arxiv.org/pdf/1612.00969
11. Mapping to Declarative Knowledge for Word Problem Solving
    https://arxiv.org/pdf/1712.09391

SRL / parsing alternatives (Q4):
12. "Syntax-aware Semantic Role Labeling without Parsing", TACL
    https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00272/43499
13. "Semantic Role Labelling without Deep Syntactic Parsing", Springer
14. Punyakanok et al.: "The Necessity of Syntactic Parsing for Semantic Role Labeling"
    http://scottyih.org/files/necessity_punyakanok.pdf
15. "Syntax-aware Neural SRL with Supertags"
    https://arxiv.org/pdf/1903.05260
16. "Combination Strategies for SRL" (joint inference, ILP/CSP)
    https://arxiv.org/abs/1110.0029

Cognitive neuroscience (Q2):
17. "Brain imaging provides insights about the interaction between instruction and diagram use for mathematical word problem solving" Frontiers Education 2022
    https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2022.893829/full
18. ScienceDaily / University of Kansas 2025: "Addressing working memory can help students with math difficulty"
19. "The role of working memory updating, inhibition..." Cognition 2022
    https://www.sciencedirect.com/science/article/abs/pii/S0022096522001412
20. "Neuromodulation of prefrontal cortex promotes deep processing during language comprehension: a tDCS/EEG study"
    https://pmc.ncbi.nlm.nih.gov/articles/PMC12464150/
21. "Distinct neural correlates of morphosyntactic and thematic comprehension processes in aphasia" Brain Communications 2025
    https://academic.oup.com/braincomms/article/7/2/fcaf093/8062590
22. "Distributed neural encoding of binding to thematic roles"
    https://arxiv.org/pdf/2110.12342

Cognitive science / role-filler binding (Q3):
23. "Learning to Perform Role-Filler Binding with Schematic Knowledge"
    https://arxiv.org/pdf/1902.09006
24. "The neural binding problem(s)" Feldman 2013

Biology / task allocation (Q3):
25. Cornejo et al.: "Task Allocation in Ant Colonies"
    https://people.cs.georgetown.edu/~cnewport/teaching/cosc844-spring17/pubs/ants-task.pdf
26. "A labor division artificial bee colony algorithm based on behavioral development"
    https://www.sciencedirect.com/science/article/abs/pii/S0020025522004972

Optimization / new math (Q6):
27. Hungarian algorithm / Kuhn-Munkres assignment problem (cp-algorithms reference)
28. "The Application of Bipartite Matching in Assignment Problem"
    https://arxiv.org/pdf/1902.00256

Verified count: 28 sources across 5 disciplines.

## 2x-DEEP second-order observations (where I challenged the obvious answer)

OBVIOUS answer: "if unit-cues plateau, you need richer syntactic features ->
                 dependency parser."

2ND-ORDER challenge: the literature shows the bottleneck is NOT "missing
features" but "missing JOINT INFERENCE over the features you have." The
substrate has features (units, verbs, position, quantifiers). What's missing
is the structured-optimization step that resolves role-assignment under
global constraints (e.g., each slot fills exactly once; schema must be
self-consistent; asked-quantity must be one of the extracted numbers).

OBVIOUS answer: "humans use syntactic parsing for role-assignment."

2ND-ORDER challenge: cog-neuro shows humans use TWO dissociable streams
(morphosyntactic frontal + verb-argument-retrieval parieto-temporal) with
PFC doing active revision under conflict. The "parsing" framing collapses
two functionally distinct mechanisms. Substrate should mirror this:
shallow-syntactic stream + verb-frame-retrieval stream + joint-inference
revision module.

OBVIOUS answer: "this is an NL problem -> needs more NLP machinery."

2ND-ORDER challenge: per substrate-LLM-boundary memory, role-assignment is
STRUCTURAL not NL. The right ontological move is to lift role-assignment
OUT of NL parsing and INTO structured optimization (bipartite matching).
This aligns with the substrate's strength (compositional/structural cognition)
rather than its weakness (arbitrary-English parsing).

## Next-drill candidate

Field: optimization-theoretic / network-science (Tier-1b new fields), edge to
free-probability parent. Specifically: bipartite matching cost-matrix
calibration under noisy features - relevant to Phase-4 follow-on once
prototype lifts above HARD-PASS threshold.
