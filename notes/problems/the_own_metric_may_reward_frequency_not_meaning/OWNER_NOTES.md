---
owner_verdict: DONE
---

SUBMISSION — the_own_metric_may_reward_frequency_not_meaning
Status: SOLVED. Reverify (scaffold-free, touches no landed dir):
.venv/Scripts/python.exe verification/test_ownmetric_frequency_controlled.py → WITNESS PASS.
Ledger: malformed/incomplete: 0, awaiting strategy re-verify + integration.

The literal problem
Our whole "stage 2 (meaning) is broken" story rests on one home test: for a word the reader grounded, pick ONE partner word; you score a point if that partner is a known relative (a ConceptNet neighbour). On that test plain word-counting beats our meaning organs 2–3×, and p2 showed the score is carried by RAW FREQUENCY — normalise frequency out (PMI) and it collapses ~8×. So the test may be rewarding "guess the commonest neighbour," which is frequency, not meaning. If so, "beat counting on this test" is not a fair bar for a meaning read-out — it asks meaning to win a frequency contest.

The bar (verbatim)
Phase (a) — is the metric fair? Build a frequency-controlled own-metric … candidates frequency-matched to the gold so raw-frequency argmax cannot win by frequency alone, OR gold restricted to non-top-frequency items … keep it powered (≥~300 scorable items). Re-measure counting there. Phase (b) — does meaning win on the fair metric? … does a meaning read-out … beat a FREQUENCY floor CI-separated over its upper bound, info-free twin LOSING? DECISIVE EITHER WAY: if counting's CI-separated advantage DISAPPEARS under frequency control, the metric was scoring frequency and the "stage 2 broken / wiring NO" conclusions must be RE-FRAMED … If counting STILL wins, the metric is fair and meaning genuinely loses — report that.

The instrument
The own metric made frequency-fair — not a new metric. The identical top-1 argmax task, on a candidate POOL where the gold partner and K non-gold co-occurrent distractors are matched on raw co-occurrence count with the term, and all pool members are sensorimotor-covered (so no arm can win by coverage). Two matching schemes: EXACT (distractor count == gold count → counting is flat by construction) and NEAREST (K closest by count → keeps power, tiny residual). Pool sizes K∈{1,4,9} → chance ½, ⅕, ⅒. Scored on data/conceptnet_gold_v1, 3 seeds, term-clustered bootstrap. Powered well past the floor: exact-match n=2066–2371 trials / 465–512 terms; nearest n=2486 / 536.

Distractors are chosen by frequency-similarity to gold, never by meaning-dissimilarity — a matched distractor may itself be a true unlabeled neighbour, which makes the task harder for meaning, so the design is conservative, not circular. I chose it over the brief's alternative ("restrict gold to non-top-frequency items") precisely because that alternative selects items where counting is wrong — the circular selection trap ("a benchmark selected by a resource cannot fairly score that resource").

The answer — decisive, and it reframes the meaning line
Phase (a) — the metric was scoring frequency (airtight, by construction).

Full metric, reproduced first-hand: raw COUNT 0.0476 / 0.0653 / 0.0590 vs PMI-normalised 0.0045 / 0.0126 / 0.0045 — a 5–13× collapse. Removing frequency makes the score many-fold worse.
On the EXACT-matched pool, COUNT scores exactly chance (0.500 / 0.200 / 0.100, zero-width CI). Verified flat by construction (0 of 692–809 non-flat pools per seed). Counting's entire advantage is raw frequency.
Diagnostic: among covered co-occurrents, count-AUC(gold vs non-gold) = 0.635–0.643 and gold is the single top co-occurrent only 11–12% of the time — the confound is a weak frequency bias that raw-count argmax rides because every meaning transform de-emphasises it and loses harder.
Phase (b) — meaning wins on the fair metric (fully controlled). Strongest frequency floor = PPMI (stronger than the neutralised COUNT because within-item matching doesn't remove global rarity, which PMI exploits). Concreteness-stripped grounded meaning beats it over its upper bound everywhere:

pool	chance	strongest floor	GROUNDED_NO_CONC	paired Δ (CI)	twins
exact K=1	0.500	PPMI 0.555	0.744	+0.190 [+0.162,+0.217]	SHUF 0.478 / RAND 0.500 — LOSE
exact K=4	0.200	PPMI 0.226	0.485	+0.259 [+0.232,+0.284]	0.187 / 0.200 — LOSE
exact K=9	0.100	PPMI 0.112	0.337	+0.226 [+0.202,+0.250]	0.098 / 0.100 — LOSE
nearest K=1	0.500	PPMI 0.598	0.741	+0.142 [+0.109,+0.176]	0.492 / 0.500 — LOSE
Full grounded (12-dim) is marginally higher (0.760 at K=1); concreteness-alone is real but weaker (0.686) and grounded-no-conc beats it → the win is genuine multi-dim sensorimotor meaning, not just concreteness (closes p2's caveat in the top-1 currency). Every meaning read-out — grounded, distributional reading (0.623), taught channel (0.614) — beats the floor CI-separated in exact mode.

Deeper-fidelity iteration — CONVERGED. Two pinned refinements tested on the same pools: ATL-hub agreement = grounded-alone (Δ +0.004–0.006, not separated); semantic-control-gated spoke weighting does not beat grounded-alone (higher gate steepness hurts). The reason is a clean negative — the crossover it assumes is absent: the distributional reading spoke is worse than grounded on both abstract (−0.10) and concrete (−0.14) terms, so there's nothing to gate. At this (archaic McGuffey-derived) corpus scale, the plain concreteness-stripped sensorimotor cosine is the optimal brain-faithful read-out.

Brain frame — PINNED vs OUR-INVENTION
PINNED: the brain assigns the context-appropriate partner, with the most-frequent associate a prior that context overrides (lexical-ambiguity resolution — Duffy/Rayner reordered-access; subordinate-bias effect). A fair meaning test must let the right partner win even when it isn't the most frequent → hold frequency fixed. The meaning channel is cross-modal agreement at the ATL hub / attractor cleanup (Patterson 2007; Lambon Ralph 2017; Rogers 2004) — the grounded sensorimotor spoke.
OUR-INVENTION-UNDER-TEST: the frequency-control construction; the grounded-cosine ranker; the concreteness split. Each is controlled (exact-vs-nearest, twins, concreteness).
Controls (each excludes something)
EXACT match → COUNT flat by construction → exactly chance (phase-a rests on construction, not a p-value).
NEAREST match (tiny genuine residual) → COUNT slightly above chance, yet meaning still beats the stronger resulting floor → excludes "the win needs perfect matching."
Concreteness control → GROUNDED_NO_CONC beats CONC_ONLY and the floor → excludes "only concreteness."
Info-free twins (shuffled grounding, random pick) at chance → excludes "coverage/pool structure alone wins."
Grounded-covered-only pools → twin sits at chance (a whole-vocab shuffle put it below chance via coverage asymmetry) → excludes "coverage masquerading as meaning."
Term-clustered bootstrap → excludes pseudoreplication-inflated CIs.
Proposed hdlab change — NOT landed (strategy owns hdlab, board Q111)
Retire top-1-argmax-over-co-occurrents grounding precision as the arbiter of "is stage 2 broken" — it conflates a weak frequency bias with meaning. Supplement with a frequency-controlled meaning-assignment instrument.
Re-frame p2's "wiring NO." Re-open the wiring on the fair metric: rank candidates by the grounded sensorimotor spoke (not raw count) on the grounded-covered population. ATL-hub agreement is equivalent; do not add control-gated distributional weighting at this corpus scale.
Extend the co-occurrence store to grounded terms (p2's 0/441 wiring gap) so the read-out can address the scored terms live.
Key realizations
The confound is provable by CONSTRUCTION, not a p-value — exact-count matching + an analytic expected-hit (flat pool → exactly 1/(K+1)) makes COUNT read exactly chance. (The enabling fix: a single stochastic tie-break had seed 7's flat arm reading 0.148 and tripped a false "COUNT WINS"; the analytic estimator removed it.)
The strongest frequency floor is PPMI, not raw count — within-item matching leaves global rarity, which PMI rides; gating meaning over PPMI's upper bound is what makes the win rigorous.
p2's discrimination-AUC finding DID cross to the top-1 metric — the bridge was frequency control. Same scorer (accuracy@1), de-confounded; not a different scorer.
Coverage was masquerading as meaning until pools were built from covered candidates only — that put the twin at chance and the win became clean.
The deeper mechanism converged on the simpler one, and the negative is informative — control-gating can't help because the distributional spoke is a frequency proxy that loses to grounded everywhere.
What I did NOT establish / would withdraw first
Withdraw first: nearest-mode wins of the weaker arms (reading/channel) don't clear the stricter nearest floor's upper bound (only paired). Robust and defended last: grounded beats the strongest floor CI-separated in EXACT mode at every K, twins losing; COUNT exactly chance under exact matching.
Context not used — the meaning arm judges word-word relatedness in isolation; the brain's context-driven selection is untested (cache stores provenance pairs, not sentences). A context-free grounded signal beating frequency is enough to reframe the conclusion; the context-faithful mechanism is a next build.
The 3 encoding arms (7B) not run — they refine the reading spoke (the weaker one; the grounded winner is unaffected) and need token positions the cache lacks. The plain reading spoke already beats the floor in exact mode, so their absence can't change the answer. Flagged, not hidden.
Scope: grounded-covered terms only (~55–75%); outside coverage no tested meaning signal beats frequency. Gold incompleteness biases against the meaning arm (conservative).
Reproduction
Cells: experiments/exp_ownmetric_frequency_controlled_v1.py (headline), ..._v2_deeper_mechanism.py (convergence) — self-test + smoke gated, reuse the cached reading, write only their own data/ dirs, ASCII/CPU/deterministic, no network, no LLM.
Witness: verification/test_ownmetric_frequency_controlled.py.
Data: data/exp_ownmetric_frequency_controlled_v1/metrics.json, ..._v2_deeper_mechanism/metrics.json.
Closure: notes/problems/the_own_metric_may_reward_frequency_not_meaning/SOLVED.md.
TLDR
We decide whether the "understand a word" step is broken using one home test: for a word it just read, pick the single best related partner. Word-counting ("what showed up nearby most") beats our meaning tools on it — so we called the step broken and decided not to wire the tools in. We suspected the test was secretly rewarding frequency, not meaning. So we made it fair: force a choice between the right partner and decoys that appear exactly as often, so counting can't win by frequency. With frequency held equal, word-counting drops to pure guessing — its whole edge was frequency — and our meaning signal (the hands-on sensory "feel" of words) picks the right partner far above chance and above every frequency method, on every run. So the home test was scoring frequency, not meaning, and the "step is broken / don't wire it in" verdict was measured on an unfair test. On the fair test, meaning wins — and that conclusion needs revisiting.

Questions
None.

Next steps (for the strategy session — you own hdlab + integration)
Re-verify with the witness command above.
Re-frame the meaning line on the fair metric; re-open p2's "wiring NO."
If wiring: rank by the grounded sensorimotor spoke (not raw count) on the grounded-covered population; extend the store to grounded terms (0/441 gap). Skip control-gated distributional weighting at this corpus scale.
Two next builds this surfaced (out of solver scope): a context-conditioned meaning read-out (use the reading sentence, not isolated word pairs), and testing whether a modern corpus revives the distributional spoke and the concreteness crossover.
