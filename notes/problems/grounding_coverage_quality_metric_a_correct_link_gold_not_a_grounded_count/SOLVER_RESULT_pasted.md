

## pasted by the owner 2026-09-12 22:33 (raw; strategy reads this)

SOLVER SUBMISSION — grounding_coverage_quality_metric_a_correct_link_gold_not_a_grounded_count

STATUS: SOLVED (the reader's-own-metric bar) + rigorous located negatives on the routes that don't apply.
Glass-box, NO external LLM at inference, modern human-behavioral gold only, NO hdlab/ writes (Q111 — results +
proposed diffs; strategy lands). Reverify: .venv/Scripts/python.exe verification/test_grounding_quality_flat_on_count.py
(3/3). Ledger: malformed 0. READ: notes/problems/grounding_coverage_quality_metric_a_correct_link_gold_not_a_grounded_count/SOLVED.md.

THE PROBLEM: the grounding loop is scored by a COUNT (n_grounded) that can't tell a correct link from a wrong one,
so meaning-fusion QUALITY gains are invisible and grounding-more-tokens-wrong looks like a win. Build a correct-link
QUALITY instrument that moves on quality and is flat on count.

WHAT WAS DELIVERED. The sense-assignment quality half already existed (strategy-landed board arm
grounding_coverage_quality). I built the MISSING half — the FLAT-on-count demonstration — completing the bar's 2x2
(full run, n=247 scorable queries / 4235 targets, live loop): (a) MOVES-on-quality: FUSED - INCUMBENT correct-link
MRR@0.5 = +0.3612 CI[0.298,0.435] (fused 0.382 vs incumbent 0.021); (b) FLAT-on-count: loosening the SDT false-alarm
knob raises the accepted count +63% (2154->3505) while the correct-link ranking-MRR diff = 0.0000 EXACTLY (an
IDENTITY by construction — FA never enters the ranking, proven byte-identical order+z_top on the live ranker, witness
V1) and correct-rate-among-accepted DECLINES 0.235->0.180 (more links, not more correct); (c) scrambled-link twin at
chance (0.013). So the count is decision-quality-blind and the quality metric provably is not.

GOLD IS BRAIN-FOUNDATIONAL AS A GOLD: SimLex/SimVerb are aggregated HUMAN behavioral similarity judgments (the
brain's own answer key), WordNet-independent; the 100%-BF gate is on the inference MECHANISM (already parser-free/BF),
not on the measuring stick.

LOCATED NEGATIVES (all drilled with mechanism): (1) referent-link-to-ENTITY half — the loop makes NO
mention->entity/coref decision (0 coref tokens in 3022 lines), so GUM coref gold has no decision variable here ->
routes to coreference_resolver (NEEDS_ADAPTER). (2) predictive-coding/N400 per-token cloze replacement — surface-
collocation-confounded (fused surprisal CI-sep HIGHER than raw). (3) WiC decision-level replacement — COVERAGE wall
(0/638 OOD contexts ground). All three TRIANGULATE on the chosen SimLex-partner instrument being correct (score the
loop on the decisions it actually makes, on its own field). I caught + retracted my own wrong "granularity" reading
of (3) after a coverage diagnostic.

OPTIMIZATIONS (all four, owner-requested): #1 byte-identity-gated live-state cache = 353s build -> 6.6s reload (~53x);
#2 per-consumer FA precision knob (measured precision/coverage curve; brain-faithful task-dependent SDT criterion,
Yonelinas/Green-Swets; hdlab wire spec); #3 powered instrument (n=247->327, added MEN relatedness as a distinct
construct, full coverage frontier, all CI-sep); #4 the WiC probe (located negative above). Plus G1-G5 upgrades
(graded z_top confidence, principled abstention, WiC arm, cache-in-board, world-model route).

FILES: experiments/exp_grounding_quality_{flat_on_count,state_cache,powered,wic,predictive}_v1.py +
verification/test_grounding_quality_flat_on_count.py + SOLVED.md. hdlab wire specs (count-vs-quality board guard,
per-consumer FA, G1/G2) proposed for strategy to land. QUESTIONS: none blocking. Awaiting owner_verdict: DONE.
