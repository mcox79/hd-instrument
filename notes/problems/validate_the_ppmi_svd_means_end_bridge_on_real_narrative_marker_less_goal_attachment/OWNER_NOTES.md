---
owner_verdict: DONE
---

SUBMISSION — validate_the_ppmi_svd_means_end_bridge_on_real_narrative_marker_less_goal_attachment
STATUS: SOLVED (solver scope; WIP until owner_verdict: DONE). Glass-box, NO external LLM. hdlab/ UNTOUCHED.
Ledger: clean (malformed 0). Reverify: .venv/Scripts/python.exe verification/test_contextual_goal_attachment_modern.py
  (4/4, the powered+clean win) + test_contextual_goal_attachment.py (5/5) + test_meansend_realtext_validate.py (9/9).

WHAT WAS ASKED vs FOUND: validate the brief's context-free PPMI+SVD means-end bridge on real marker-less goal
attachment. Finding: that mechanism is REFUTED — on real narrative it sits INSIDE the info-free twin band (a
goal-frequency artifact), because it throws away the SITUATION. The brain's ACTUAL mechanism is CONTEXTUAL
inverse planning, and rebuilt that way it WINS. (Owner drove two corrections that were the unlock: wrong
mechanism — context-free not situational; wrong corpus — 200-yr-old text, out-of-distribution for the parser.)

THE MECHANISM (brain-foundational; Baker/Jara-Ettinger inverse planning conditioned on STATE; dmPFC-uncertainty
gate): score each candidate goal by the distributional relatedness of the SITUATION (prev sentence + the action
clause up to the goal marker + the action verb + its object, EXCLUDING the goal clause) to the goal, in the live
associative relatedness store (conceptual_meaning routes relatedness->associative; meaning_fusion phi == this
space); gated. exp_contextual_goal_attachment_{v1,modern_v1}.py.

RESULT (matched-population discrimination, bootstrap CI vs the info-free shuffled-situation twin null p95):
- MODERN GENERAL TEXT (UD-EWT, 797 GOLD-advcl purposes, in-distribution, no parser noise): K1 0.700 [ci-lo 0.680]
  vs twin p95 0.483; K3 0.473 [ci-lo 0.448] vs twin p95 0.232 — BEATS by a wide, clean, powered margin.
- 19c LitBank (n=336): K1 0.634 vs 0.537; K3 0.407 vs 0.295 — BEATS; the context-free ATOMIC bridge on the SAME
  items sits AT the twin (0.548/0.291), isolating the SITUATION as the source.
Signal trace: dist_CONTEXT is the decisive lever (0.708 vs twin 0.600); distributional relatedness > the curated
ATOMIC means-end table.

PARSER — did I touch it? NO. I did NOT modify, retrain, or build any parser. hdlab/arc_parser.py and
arc_labeler.py are REUSED UNCHANGED. I only (a) MEASURED the reader's existing arc parser+labeler on the
advcl(purpose)/xcomp(complement) call, and (b) prototyped a FILTER on top of its output (keep advcl, reject
xcomp). Its advcl/xcomp split is 0.929 on modern text but 0.375 on 19c LitBank — a pure corpus-age (OOD)
artifact, NOT a mechanism failure. Recommendation: no separate 19c parser (I built none); the only lever is
GENERAL narrative parse quality — the already-filed parser problem — which lifts every consumer.

HONEST NEGATIVES KEPT: (1) the context-free ATOMIC bridge fails (within the twin band); (2) the IDF+attention
"optimization" (ATL distinctive-features + object emphasis + attention) does NOT beat the simple situation-
relatedness (-0.033) — the simple mechanism is near-optimal; (3) a single distractor draw lied (a "0.72 pass"
averaging erased); (4) 19c is OOD for the parser. All controls: shuffled-situation twin, context-free ATOMIC
baseline, modern gold-parsed corpus, goal-clause leakage exclusion, matched-population, bootstrap CI, no-regress.

CONSUMER IMPACT: zero regression — the upstream advcl/xcomp purpose filter removes 131 wrong purposes vs 24
genuine (5.5:1, net-positive on the live goal-why consumer); the contextual attachment is a pure ADD on isolated
nodes (connected chains 645/645 byte-identical). Enumerated consumers unaffected.

FOR STRATEGY (Q111 wire — you own it): (1) WIRE the contextual attachment as the reliability-gated edge in
build_goal_graph._link_open_stack, replacing the recency heuristic (it beats the twin; recency did not); (2) DO
NOT wire the context-free ATOMIC bridge; (3) land the upstream advcl/xcomp purpose filter (reader's arc labeler;
net-positive, verdict-independent — ceiling is general parse quality, not a 19c special case); (4) move the goal
eval off 19c LitBank onto modern annotated narrative (this cell already does, UD-EWT).

WHAT IS NOT DONE (the honest asterisk): the hdlab WIRE + the end-to-end in-context deployment measurement (attach
real isolated actions to real open goals on a plot-structure QA arm) — that is the integration step (strategy),
not a solver deliverable. The mechanism itself is validated (powered, clean, modern).

§2b AUDIT UPDATE: marker-less goal attachment — context-free means-end bridge = located NEGATIVE; situation-
conditioned inverse planning WINS CI-sep (modern n=797). Attachment is inverse planning conditioned on STATE; the
signal is the situation's distributional relatedness, NOT a curated table. The recency link_open_stack + any
context-free ATOMIC edge do not clear the info-free floor — replace with the situation-conditioned edge. Upstream
advcl/xcomp is a modern-parse decision; the 19c gap is corpus-age OOD. The winning score(candidate|situation) is
readout-agnostic → one situation-conditioned inverse-planning engine for goal + belief (Baker 2017 unification).

TLDR (plain English): The suggested method — guess a character's unstated goal from a fixed "why people do things"
table — failed on real stories. You pushed that the brain manages it and to test on ordinary modern text. Both
right: the brain reads the SITUATION ("seized the knife" → escape because the scene is dangerous), so I rescored
each candidate goal by how well the surrounding situation relates to it, using the reader's own learned word-
associations. On ~800 modern examples it gets the right goal ~70% of the time vs 48% for a scrambled-situation
control — a big, clean win, where the table version was chance. I did NOT touch the parser; I only measured it and
found the 200-year-old text is just hard for the modern grammar parser (not a real limit). Glass-box, no outside AI.

QUESTIONS: none blocking.
NEXT STEPS: (1) strategy wires the situation-conditioned edge; (2) land the arc advcl/xcomp purpose filter;
(3) keep the goal eval on modern narrative; (4) unify the situation-conditioned engine across goal + belief.
