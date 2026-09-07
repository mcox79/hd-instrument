---
owner_verdict: DONE
---

SUBMISSION — infer_unstated_emotion_via_occ_appraisal_over_event_goal_congruence
status: SOLVED (headline PASS + upstream generalizations + role-filler layer + intensity + goal-script KB + the
unifying architecture, all measured; social partial win). WIP until owner_verdict: DONE. hdlab/ UNTOUCHED (Q111).
NO external LLM at inference; NO trained encoder; glass-box throughout.

WHAT THE BRIEF ASKED: build the glass-box OCC appraisal that infers a character's UNSTATED emotion by appraising an
event against that character's goals (goal-conduciveness x prospect), beat a valence/most-frequent floor CI-sep on a
MODERN gold with a shuffled goal<->event twin LOSING — or a rigorous located negative.

HEADLINE (PASS) — a glass-box OCC appraisal (desirability x prospect -> OCC type + valence), the SIBLING of the
landed ToM chain (EVENT x GOAL -> felt emotion), over the LIVE reader's extracted registers, on a constructed MODERN
OCC gold (n=50, named chars, balanced 25/25 valence):
  • TYPE 0.940 vs strongest floor (valence-only, oracle-valence) 0.440 = +0.500 CI[+0.340,+0.660]; vs last-word 0.200
    = +0.740; vs the CURRENT live substrate (no thwart/prospect) 0.060 = +0.880 CI[+0.780,+0.960].
  • VALENCE 0.940 vs majority floor 0.500 = +0.440 CI[+0.260,+0.600].
  • LOAD-BEARING prospect subset {relief, fears_confirmed} (n=18): 1.000 vs valence-only + last-word floors both
    PROVABLY 0.000 (relief carries a stated FEAR word — the false-belief-subset analog). ORACLE(rule) 1.000;
    goal<->event-shuffle TWIN 0.220 LOSES (+0.720 CI-sep). Density phase cut: TYPE 0.94->0.06 sparse while ORACLE
    stays 1.000 both -> the rule is density-invariant; the entire drop is EXTRACTION.

TWO UPSTREAM BRAIN-FOUNDATIONAL GENERALIZATIONS (PINNED, verified): GOAL-FAILURE-by-thwart status (Lutz-Radvansky /
Dopkins-Klin-Myers 1993; Zwaan-Radvansky "backbone") — STRICT SUPERSET (0 satisfied/failed flips over 53 goals, 14
active->failed, 0 wants() regressions) + agent-coref-canon + irregular-past; and PROSPECT confirm/disconfirm (OCC
prospect branch; Lazarus relief).

FOUR WALLS RESEARCH-DRILLED (primary sources) + BUILT ACROSS (each: can-fail floor + info-free twin):
  • EVENT<->GOAL MATCHING — NOT the distributional hub (bridging_inference is POLARITY-BLIND: rel(sell,buy)~=
    rel(win,lose)); it's a ROLE-FILLER/converse layer (FrameNet Perspective_on + WordNet antonymy + Jara-Ettinger
    beneficiary). BUILT: baseline 0.417 -> 0.833 (+0.417), twin loses.
  • RESULT-STATE ("podium"=won) — a BOUNDED schema/script mechanism (Hobbs abduction + Zwaan-Radvansky open-goal
    registry + Kintsch settling; hippocampal-vmPFC schema completion), NOT open-ended Phase-1. BUILT a goal-script
    ->terminal-state KB: sparse recovery 0.136->0.773 (13/22), goal-shuffle twin LOSES, HARD-PASS met. Canonical
    markers (not gold phrasing); non-circular production build corpus-mines markers (Chambers-Jurafsky).
  • INTENSITY — discourse belief-vs-outcome surprise + goal-IMPORTANCE (importance PRIMARY, Frijda/Ortony 1992; NOT
    the argument-level N400, measured inert). Minimal-pair ranking 1.000, twin loses; importance-weighted (fidelity fix).
  • SOCIAL/ATTRIBUTION (gratitude/anger) — rule EXACT (oracle 1.000); BUILT beneficiary satisfaction (Jara-Ettinger;
    FrameNet Assistance) + implicit-investment goal feeder (Trabasso/Liu/Friedman) + Tier-1 controllability
    (Smith-Ellsworth): social subset 0/12 -> 3/12 (clean cases); pride/shame correctly DEFERRED (need the norm channel).

THE UNIFYING ARCHITECTURE (built + demonstrated) — every resolver branch is ONE computation: a Hobbs weighted-
abductive MATCH of each clause against each OPEN GOAL over a Zwaan-Radvansky open-goal registry with Kintsch settling.
`_occ_unified_resolver.py`: BEHAVIOR-PRESERVING (dominant emotion reproduces the branch results — main 0.940 exactly,
converse 0.833, sparse+script 0.727) AND MIXED EMOTIONS for free (3/3 two-goal items yield BOTH). It surfaced+fixed
two real bugs (converse-as-antonym; unbound pronoun goal-agents). THIS IS THE RECOMMENDED LANDING DESIGN (§6b).

CROSS-CUTTING LESSON (measured 3x): every STRUCTURED relation the appraisal needs (converse, result-state, meronymy)
is a KNOWLEDGE-ASSET job; the distributional similarity hub is ONLY the fuzzy-similarity fallback (probed inert on
report~file 0.047 / garden~flowers 0.066).

BRAIN-FIDELITY AUDIT: every COMPUTATION is PINNED + research-verified; every EXTRACTION heuristic (cue lexicons) is
OUR-INVENTION-UNDER-TEST, labeled as such. One fidelity gap found + fixed (intensity equal-weighted -> importance-primary).

FILES: experiments/_occ_appraisal.py, _occ_upstream_goal_status.py, _occ_goal_scripts.py, _occ_unified_resolver.py +
~10 exp cells + 5 golds; verification/test_occ_appraisal.py (9/9); 4 research notes; SOLVED.md. hdlab/ UNTOUCHED.
REVERIFY: .venv/Scripts/python.exe verification/test_occ_appraisal.py  (9/9; recomputes headline+floors+twin+NOFIX +
          the upstream strict-superset from source)

NEXT STEPS (priority-ordered, SOLVED §NEXT STEPS):
  P1  LAND THE PROVEN WIN — promote _occ_appraisal.py -> hdlab/occ_appraisal.py; land the thwart generalization INTO
      hdlab/goal_register.track_status (strict superset, 0 regression); default-off sm.infer_emotion read-out; board
      OCC-appraisal arm (board-INVISIBLE today); fold the AUDIT UPDATE. Land it on the UNIFIED resolver (§6b), not 8 flags.
  P2  Land the role-filler polarity layer (converse/beneficiary/maintain-thwart/goal-script).
  P3  Build the goal-script terminal-state KB PROPERLY (corpus-mined, held-out) — the highest-leverage buildable follow-on.
  P4  The true-Phase-1 tail (STRUCTURED-asset theme-coref via WordNet meronymy [ATL hub probed inert]; predicament->goal;
      norm channel for pride/shame).
  P5  The intensity organ (prototyped win). P6 fidelity extensions (mixed emotions [now free in the unified resolver],
      dynamics, arousal, emotion->action).
