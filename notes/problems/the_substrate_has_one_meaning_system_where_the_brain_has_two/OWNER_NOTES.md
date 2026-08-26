---
owner_verdict: DONE
---

SUBMISSION -- SOLVER RESULT: the_substrate_has_one_meaning_system_where_the_brain_has_two
STATUS: PARTIAL  (bar #1 SOLVED: feature system built + proven | bar #2 REFUTED -> two systems better
                  FUSED than SWITCHED, the brief-named valid outcome) | ledger malformed/incomplete: 0
REVERIFY: .venv/Scripts/python.exe verification/test_two_meaning_systems_feature_similarity_and_gate.py  (PASS)
NO hdlab/ MODIFIED (Q111: proposed diff below; strategy lands it). Priority-1 brain-foundational build.

THE ANSWER IN ONE LINE
The missing system was real and I built it: a brain-faithful FEATURE-SIMILARITY system (distinctive-
feature-weighted grounding) beats the associative rep on similarity, CI-separated, on two held-out golds.
The SEMANTIC-CONTROL GATE is NOT the way to combine the two systems for word-pair rating -- a FIXED
multiplicative INTEGRATION beats task-switching, robustly -- because semantic control is context-gated and
a decontextualised pair gives it nothing to gate on. Wire the feature system + the fixed fusion; the gate
belongs to an in-context selection task owned elsewhere.

THE BAR (verbatim, PROBLEM.md S7)
Two can-fail claims, both CI-separated, on held-out populations with floors recomputed on them:
(1) a brain-faithful feature-similarity representation (grounding + structured/local context, distinctive-
    feature weighted) beats (a) the associative/relatedness representation AND (b) the strongest real
    floor's UPPER bound on a held-out SIMILARITY gold, CI-separated, info-free twin LOSING.
(2) a task-gated selection (multiplicative gain by the query's demand) beats the best FIXED blend on a
    mixed relatedness+similarity population, CI-separated, recovering BOTH axes. Report CI half-width +
    null p95. DECISIVE EITHER WAY: a loss on #2 (better fused than switched) is a real finding.

=====================================================================================================
BAR #1 -- FEATURE-SIMILARITY SYSTEM (SOLVED, CI-separated)
=====================================================================================================
BRAIN MECHANISM. The ATL amodal hub computes feature/correlational similarity weighted toward DISTINCTIVE
features (Rogers & McClelland; Patterson, Nestor & Rogers 2007; Lambon Ralph). Our grounding carrier
(grounded_similarity.py: 11 Lancaster sensorimotor + Brysbaert concreteness, z-scored, ~36.8k words) holds
the right signal but its own docstring MEASURES the wrong metric: raw cosine can't separate synonym from
sibling (apple/orange 0.952 ~ sofa/couch 0.968) because a DOMINANT SHARED axis (top PC = 26.7% of variance,
~concreteness) swamps the discriminating dims -- the ATL's job stated as a bug. The faithful fix is the
ATL's actual op: privilege distinctive features / suppress shared ones == DECORRELATE: WHITEN away the
shared covariance. A REPRESENTATION-level op, NOT a read-out format (the refuted sign/graded/sparse family).

RESULTS (Spearman rho; hyperparams fit ONLY on SimVerb-dev500; SimLex-999 + SimVerb-test3000 fully held
out; whitening covariance fit gold-blind AND vocab-disjoint = benchmark words excluded):
- Feature system beats the ASSOCIATIVE rep on SIMILARITY, CI-sep, on the fair same-item intersection:
    SimLex-999    DFW 0.236 vs co-occ 0.039  -> +0.197 CI[0.083,0.316]  (n_i=573)
    SimVerb-test  DFW 0.232 vs co-occ -0.002 -> +0.233 CI[0.171,0.298]  (n_i=1525)
- Distinctive-feature weighting beats RAW grounded cosine, CI-sep (the build earning its keep):
    SimLex 0.291 vs 0.245 (+0.046 CI_lo 0.019); SimVerb 0.287 vs 0.264 (+0.023 CI_lo 0.008); and it
    LOWERS relatedness (WordSim 0.412 -> 0.398) -- the exact brain signature (specialises to "alike-in-kind").
- FLOORS (recomputed on each population): info-free twin (shuffled grounding rows) rho 0.014/0.016 (twin_p95
    0.059/0.034) LOSES; CONCRETENESS single-dim -0.138/-0.073; FREQ-product ~0. All cleared.
- STRUCTURED local context (secondary): narrow-window (+/-2) PPMI-SVD linguistic spoke (Levy & Goldberg
    2014: local context -> functional similarity) fused with whitened grounding gives a small dev gain
    (alpha=0.25, dev 0.338 -> 0.351) on the corpus-covered subset. Grounding carries the primary claim.

FINER DRILL (exp_distinctive_feature_mechanism_v1): is the faithful op LINEAR whitening or PER-CONCEPT
NONLINEAR distinctiveness (the sharper semantic-dementia account: distinctive features lost first ->
zebra->horse)? Tested sign(z)*|z|^p, p swept on dev. LINEAR IS SUFFICIENT: p_best=1.0, nonlinear adds
0.000 CI-sep; the zebra->horse SD signature does NOT reproduce (synonym-minus-sibling margin FALLS with p:
0.106@p=0.25 -> 0.052@p=3.0). Read: a 12-dim CONTINUOUS grounding space lacks the binary few-concepts-have-
it structure that account assumes, so linear decorrelation captures the distinctiveness that exists. The
next fidelity gain is a RICHER FEATURE SUPPLY (more modalities / feature norms), NOT a fancier transform.

=====================================================================================================
BAR #2 -- SEMANTIC-CONTROL GATE (REFUTED -> fixed INTEGRATION wins; robust across 3 angles)
=====================================================================================================
BRAIN MECHANISM. IFG semantic control applies a task-gated, roughly MULTIPLICATIVE gain (biased
competition; Thompson-Schill 1997; Jefferies & Lambon Ralph) that selects the task-relevant system and
suppresses the competitor. I built it (per-task alpha on the associative contribution; task = the
INSTRUCTION, never the gold) and tested it three ways -- all say FUSED > SWITCHED:
1. MIXED POOL (SimLex sim + WordSim rel, 50/50 dev/test): gate beats best fixed blend by only +0.017
   CI[0.005,0.028] but TIES its random-switch control (p95 0.017) -> the task signal is not what pays.
   (feature-pure 0.309, fixed 0.311, gate 0.327.)
2. CONFLICT POPULATION (same SimLex pairs, similarity vs USF-association tasks -- perfect vocab control):
   on AGREEMENT pairs gate=fixed 0.597 (no switching needed); on CONFLICT pairs BOTH systems collapse to
   near-chance (gate 0.032, fixed 0.047) so control has nothing to arbitrate; interaction -0.014
   CI[-0.113,0.087] (null).
3. STRONG ASSOCIATIVE SYSTEM (wide-window PPMI-SVD, WordSim 0.338 -- genuinely strong, not the lossy d=256
   bundle): the FIXED BLEND BEATS the gate CI-sep (gate-minus-fixed -0.026 CI[-0.048,-0.006]) and recovers
   both axes best (sim 0.297, rel 0.459, mean 0.378 vs feature-pure 0.309 vs gate 0.352).

THE PRECISE REASON (not an exhausted-engineering wall). Semantic control is CONTEXT-driven; a decontextu-
alised word pair supplies no context to gate on -- only a coarse task label. So for context-free graded
RATING, fixed multiplicative integration is the faithful operation and switching does not help. The gate's
real proving ground is a task where CONTEXT selects among competing senses (homonym WSD -- "bank" near
"river" vs "money"). I deliberately did NOT build that here: it is owned by reader_meaning_channel (whose
exp_context_conditioned_sense_selection_v1/v2 already HARD_FAILED); building it would compete with filed work.

THE ACTUAL ANSWER TO "ONE SYSTEM WHERE THE BRAIN HAS TWO": build the missing feature system + combine the
two by FIXED multiplicative INTEGRATION, which recovers BOTH axes better than either alone (0.378 vs
feature-pure 0.309 vs associative-pure 0.338). Do NOT wire a task-switch gate for rating.

=====================================================================================================
CONTROLS (what each excluded)
=====================================================================================================
info-free twin (shuffled grounding rows -> rho ~0.01, LOSES: excludes the whitening/z-scoring machinery
manufacturing structure); paired bootstrap CIs on every margin; held-out splits (dev = SimVerb-dev500 /
dev-halves only; SimLex-999 + SimVerb-test3000 fully held out); vocab-disjoint gold-blind whitening fit;
RANDOM-SWITCH gate control (task-label scrambled -> ties the gate: excludes "switching machinery, not task
signal, pays"); CONCRETENESS item-gate (dual-coding hypothesis REFUTED: co-occ is subsumed by grounding,
NEGATIVE-rho on abstract pairs); STRONG-associative re-test (excludes "our co-occ was just too weak");
CONFLICT-population test (excludes "the mixed pool diluted the effect"); FEAT-vs-ASSOC on the co-occ
intersection (fair same-item head-to-head); SD behavioural signature (synonym-vs-sibling) for the finer drill.

=====================================================================================================
AUDIT UPDATES (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
=====================================================================================================
1. Tier-2 Sensorimotor spokes / Amodal concept hub -- the RIGHT-OP-WRONG-METRIC deviation now has a FIX +
   a number: the measured ceiling (raw cosine can't separate synonym from sibling) is a MISSING DISTINCTIVE-
   FEATURE WEIGHTING; whitening the grounding space (suppress the 27%-variance shared axis) beats raw
   CI-sep on SimLex (+0.046) and SimVerb (+0.023) and specialises to similarity. FINER: the faithful op AT
   THIS FIDELITY is LINEAR decorrelation -- per-concept nonlinear distinctiveness does not add on 12
   continuous dims and the zebra->horse signature doesn't reproduce; next gain is richer feature SUPPLY.
2. Semantic control (IFG) -- the THIN deviation is DECISION-RELEVANT: for graded rating the faithful op is
   FIXED multiplicative INTEGRATION, NOT a task-SWITCH (gate loses to fixed blend even with a strong
   associative system and on conflict pairs). The gate is context-gated and needs a context-selection task
   (WSD) to bite; do NOT wire it for rating. Re-point the gap: near-term win = the fixed two-system fusion.
3. The two-similarity-systems row (from sign_quantiser) is CONFIRMED and BUILT: feature system = whitened
   grounding (+ narrow PPMI); associative = wide co-occ / PPMI-SVD; when both strong they are best FUSED.

=====================================================================================================
PROPOSED hdlab CHANGE (strategy lands; Q111)
=====================================================================================================
1. Wire the distinctive-feature transform into the grounding carrier as an optional default-off
   `distinctive=True` path: whiten the z-scored grounding vector (population covariance, gold-blind) before
   cosine. Beats raw grounding CI-sep on similarity; keep the raw path for relatedness. (Representation
   option gated on the held-out SimLex/SimVerb margins, not a capability claim.)
2. For a two-system meaning read-out use FIXED multiplicative INTEGRATION (per-pair z-fusion of whitened-
   grounding cosine + a wide-PPMI-SVD associative cosine), NOT a task-switch gate. Recovers both axes (0.378).
3. Do NOT wire a semantic-control task-switch gate for graded rating. File it as a future deliverable
   contingent on a genuine context-selection task (WSD), coordinating with reader_meaning_channel.

=====================================================================================================
KEY REALIZATIONS (the enabling moves)
=====================================================================================================
- The grounding organ's own documented failure IS the ATL's job description -- read the carrier's honesty
  section before reaching for a new mechanism; the brain had already named the fix.
- Distinctive-feature weighting is DECORRELATION (representation), not a read-out format -- different-in-kind
  from the refuted sign/graded/sparse sweep, which is why it worked.
- The gate's null survived every rescue -- and the decisive move was to STRENGTHEN THE COMPETITOR (a real
  wide-PPMI-SVD), not tune the gate: with a strong second system, fusion beat switching MORE clearly. A
  shared wall across weak-assoc / conflict / strong-assoc means switching is the wrong OP, not under-tuned.
- Same pairs, two golds (SimLex sim + USF-assoc) is the cleanest gate test -- holds vocab/frequency fixed so
  only the task varies.
- Drilling the mechanism finer told me WHERE fidelity is SUPPLY-limited vs transform-limited: when a finer
  op stops paying, the next gain is richer features, not a cleverer formula.
- The gate's null is a statement about the TASK, not the mechanism: control is context-gated and a bare
  pair has no context.

=====================================================================================================
WHAT I DID NOT ESTABLISH (withdraw first if wrong)
=====================================================================================================
- The structured-context (narrow PPMI-SVD) add is SMALL and only on the corpus-covered subset; grounding
  carries the bar-#1 claim.
- I did NOT test the gate on a genuine SELECTION task (WSD); my claim is only that it loses to fixed
  integration on context-free RATING. The gate may still be right for selection/interference tasks.
- The whitening is fit on the Lancaster/Brysbaert norm population; gold-blind but not tested for transfer to
  a differently-built grounding source.
- No relation-controlled similarity gold beyond the standard SimLex/SimVerb benchmarks.

=====================================================================================================
DO NOT QUOTE
=====================================================================================================
- Do NOT quote the gate's +0.017 mixed-pool margin as a win -- it ties its random-switch control.
- Do NOT quote raw grounding as "the feature system" -- the build is the WHITENED (distinctive-feature) rep.
- Do NOT carry a number across scorers/populations: SimLex-sim, SimVerb-sim, WordSim-rel, USF-assoc, and the
  co-occ-intersection vs full-grounding-coverage subsets are DIFFERENT; recompute each floor on its own gold.
- Do NOT read the bar-#2 result as "the semantic-control gate is useless" -- it is the wrong op for
  context-free RATING; its proving ground (in-context WSD) was not tested here.

=====================================================================================================
FILES
=====================================================================================================
experiments/exp_feature_similarity_system_v1.py            (bar #1: DFW grounding + PPMI structured context)
experiments/exp_distinctive_feature_mechanism_v1.py        (bar #1 finer: nonlinear vs linear + SD signature)
experiments/exp_semantic_control_gate_v1.py                (bar #2: task-gate vs fixed blend, controls)
experiments/exp_semantic_control_conflict_v1.py            (drill: conflict/competition population)
experiments/exp_semantic_control_strongassoc_gate_v1.py    (drill: gate vs strong wide-PPMI-SVD associative)
verification/test_two_meaning_systems_feature_similarity_and_gate.py   (scaffold-free witness, PASS)
data/exp_*/metrics.json for each.  NO hdlab/ modified.

=====================================================================================================
PLAIN-LANGUAGE TLDR
=====================================================================================================
Our system could tell which words go together (dog-leash) but not which are alike in kind (dog-wolf) --
the brain has two separate machineries for these and we only had the first. I built the missing one. The
key was that our sensory-grounding data already holds the answer, but one loud "how vivid/concrete is this
word" signal drowns out the fine distinguishing details; the brain's known trick is to turn that shared
signal DOWN and the distinguishing ones UP, and doing exactly that made the system clearly and repeatably
better at "alike in kind," on words it was never tuned on. I then tested a "switch" that picks the right
machinery per question -- it does NOT help: it is better to always BLEND the two with a fixed recipe than
to switch, and this held even after I made the second machinery much stronger and even on the hardest
disagreeing pairs. The reason is that the brain's switch runs on CONTEXT (a sentence), and a bare pair of
words has no context to switch on -- so the switch's real job is picking a word's meaning inside a
sentence, a different problem another part of the project already owns. I also drilled the "alike in kind"
trick one level deeper (a fancier version the brain uses, that fails first in dementia) and found the
simple version is already right for our data -- the next improvement is BETTER sensory data, not a smarter
formula. Net: the missing machinery is built and proven; combine the two with a fixed blend, not a switch;
and the next gains are richer sensory data and testing the switch on in-sentence meaning.

QUESTIONS: none blocking. One call: I filed PARTIAL (bar #1 met CI-separated; bar #2 the brief-named
"better fused than switched" outcome). Reads as SOLVED-with-a-refuted-half if you prefer.

NEXT STEPS: (1) wire the whitening transform + the fixed two-system fusion (diffs above); (2) ENRICH the
feature supply (more sensorimotor modalities / feature norms) -- where the next distinctiveness-fidelity
gain is; (3) test the semantic-control gate on an in-context selection task (WSD), coordinating with
reader_meaning_channel; (4) adopt SimLex/SimVerb (feature-similarity axis) into the standing meaning metric
so the feature system is graded on its own axis, not taxonomic WordNet.
