---
owner_verdict: DONE
---

SUBMISSION — consolidate_the_arceager_and_arc_double_parse_the_reader_now_parses_every_sentence_twice
status: SOLVED (WIP until owner_verdict: DONE). Glass-box, NO external LLM. NO hdlab/ modified (Q111: strategy lands
the wire). Witness 14/14. Ledger malformed/incomplete: 0.
reverify: .venv/Scripts/python.exe verification/test_double_parse_consolidation.py   # 14/14, deterministic

🚩 PARSER-IMPACT FLAG — this submission TOUCHES THE PARSER (coordinate with concurrent parser work; many parser
problems + in-flight solvers exist). No hdlab/ parser file was modified, but the proposed landings change the parser
layer: (1) RETIRE the arc-factored batch parser from the read path (front-end reads the arc-eager parse); (2) an
OPTIMIZED arc-eager (byte-identical); (3) parser-confidence + predictive-frontier probes. #1/#2 are byte-identical or
no-regress; #3 are located negatives. Flag for the parser owner.

THE CORE RESULT (the assigned problem)
- REPRODUCED: the live reader parses every sentence TWICE — arc-factored BATCH (hdlab/arc_parser, drives space+copular
  via the shared cache) + arc-EAGER INCREMENTAL (hdlab/arceager_parser, drives who-did-what roles). ~2 parses/sentence;
  the batch parse = 1.00s = 4.6% of a 21.71s warm read (309 held-out sentences).
- CONSOLIDATED onto ONE incremental parse (the brain parses once). Exact hdlab diff prototyped at class level
  (exp_double_parse_ideal_wire_v1): _cached_parse_heads decides the parser; _router_roles reads the shared cache.
  6 of 9 consumed dims BYTE-IDENTICAL (events[agent+patient], coref, causal, timeline, suppressed, coref_acc). The 2
  front-end consumers (copular state, space location) are NOT byte-identical but MEASURED NO-REGRESS: copular fix_recall
  identical modern (1.000) + 19c-archaic (0.700), +0.013 neutral on 451 UD-EWT (raw detection +0.111 CI-sep); space
  where_is within noise on 19c and +0.043 on MODERN. Strict byte-identity is impossible-by-construction (two different
  parsers) — no-regress is the honest, achievable, brain-foundational bar, and it passes.
- BRAIN-FOUNDATIONAL (PINNED, researched): arc-eager incremental = a defensible model of human parsing (incremental +
  bounded working-memory stack/buffer + eager-attach-then-revise; Marcus 1980, Nivre 2004, Hagoort 2005, Resnik 1992);
  arc-factored batch = ZERO cognitive correlate → retire from read path. And it's the FASTER parser (0.83s vs 1.00s).
- UPSTREAM+DOWNSTREAM tested: a full default-on read emits ZERO batch parses / one arc-eager parse across ALL consumers;
  the full situation-model board shows ZERO regression on every scored dim (worst delta +0.0000).

PUSHED FURTHER (owner-directed; each with a can-fail control — wins AND honest located-negatives)
- OPTIMIZED arc-eager: byte-identical crc32-memo, 1.26× (0 mismatches / 1200 sents / 15,252 arcs). More headroom
  (arg-keyed memo + numpy) — the sole-parse cost lever now.
- ROLES-CONFIDENCE, closed END-TO-END: the obj-arc-head PROXY (AUC 0.732) OVERSTATED it; on the deployed patient
  readout the margin AUC is 0.538 — a WEAK light-abstain lever only (+0.035 acc-when-answered @80% cov, decays by 40%).
- PREDICTIVE arc-eager (deep frontier): verb-argument pre-activation is a REAL anticipatory signal (MRR 0.393 vs 0.334
  floor, shuffled twin loses) but a LOCATED NEGATIVE on attachment accuracy (composite −0.073 vs word-order; won 141/
  lost 206). Matches Demberg-Keller-Koller 2013 — prediction is a processing-TIME/N400 mechanism, not an accuracy one.
- CORPUS-AGE confound (owner: "why 200-year-old literature?"): load-bearing numbers are modern (UD-EWT) or
  register-independent; the one 19c-anchored number (space) was RE-RUN on modern and CLOSED (arc-eager +0.043 > floor +
  twin). The 19c −0.015 was the OOD handicap.
- SPACE-RECALL (owner: "why do we lose everything in extraction recall, how does the brain overcome it?"): the
  signal-loss ladder localizes the loss to motion-event EXTRACTION RECALL (0.444; register/readout lossless to 0.79,
  parse-independent). Miss taxonomy: ~⅓ coref, ~⅓ node/timing, ~13% narrow motion lexicon, ~13% stative/deictic; gates
  cost +0.000, naive broadening −0.074. Brain mechanism (researched): a persistent protagonist-anchored WHERE-state
  updated from ANY location-entailing predicate via lazy locative-PP bridging (McKoon-Ratcliff; Zwaan-Radvansky), NOT a
  motion-verb lexicon. PROTOTYPED it (REUSE-first): a lazy locative-PP bridge + WordNet place taxonomy lifts recall
  0.444→0.889 at HIGHER precision (0.571→0.739), where_is +0.128 over the shuffled-place twin. Filed as a follow-on
  brief (SPACE_RECALL_FOLLOWON_BRIEF.md) — reuse EntityBinder (coref) + grounded_semantic_graph ConceptNet AtLocation.

FILES (all experiments/ + verification/; NO hdlab/):
exp_double_parse_consolidation_v1.py, exp_double_parse_frontend_noregress_v1.py, exp_double_parse_ideal_wire_v1.py,
exp_double_parse_ideal_confidence_v1.py, exp_arceager_optimized_v1.py, exp_double_parse_roles_confidence_e2e_v1.py,
exp_arceager_predictive_frontier_v1.py, exp_space_modern_brainfoundational_v1.py, exp_space_recall_brainfoundational_v1.py,
_diagnose_space_recall.py, _diff_entity_states.py; verification/test_double_parse_consolidation.py (14/14);
notes/problems/consolidate_.../SOLVED.md + SPACE_RECALL_FOLLOWON_BRIEF.md.

NEXT STEPS (strategy): (1) land the one-parse wire [coordinate per the parser flag]; (2) land the byte-identical
optimized arc-eager; (3) file the space-recall follow-on (largest reader-accuracy lever, REUSE-heavy); (4) do NOT chase
confidence-weighting / predictive-accuracy / beam / register-retraining (all located negatives); (5) AUDIT UPDATE §2b
(arc-eager = PINNED brain parse; batch = retire; correct the stale "arc-eager copular 19c-negative").

DO NOT QUOTE: a read-time cut as "free/lossless" (copular/space are no-regress, NOT byte-identical); the roles-confidence
proxy (0.732 — overstated; end-to-end 0.538); any space where_is gain without the shuffled-place twin losing; parse
QUALITY as a space-recall lever (it's parse-independent).

TLDR (plain English): the reader was grammar-parsing every sentence twice with two different parsers; the brain parses
once, and the left-to-right one is the brain-faithful choice, so I routed everything onto it — 6 of 9 outputs come out
identical, the other two are measured no worse (one a bit better), it drops ~a second of parsing, and the parser that
stays is the faster one. Pushing further: I made that parser byte-identically faster, showed two "smarter parser" ideas
(confidence-weighting, prediction) don't actually help accuracy (honest dead-ends), re-checked everything on modern
prose (not just 200-year-old books), and — for the one real weakness, the reader missing where characters are — found
exactly why (it only notices explicit "moving" verbs) and prototyped the brain's fix (update location from any
place-phrase), nearly doubling recall.

QUESTIONS: one judgement call — the brief asked for byte-identical output, impossible once you drop to one parse; I
delivered the no-regression version (the brain-foundational goal). If you require strict byte-identity, the answer flips
to the brief's sanctioned located-negative (keep two parses). I recommend the consolidation.
