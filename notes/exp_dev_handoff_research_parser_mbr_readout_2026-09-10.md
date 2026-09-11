# exp_dev hand-off — research: parser MBR readout + joint POS/parse co-adaptation

**Filed by:** research (self-read literature+code drill, no sub-agent fan-out), 2026-09-10.

**Trigger:** `notes/research_parser_mbr_readout_joint_pos_dmv_2026-09-10.md` — a focused drill on the
treebank-free reading-learned dependency parser's readout/decode step, requested to hone (1) a
reliability-gated graded-competition readout of the arc marginals, and (2) joint POS/parse
co-adaptation. Direct code read of `hdlab/arc_parser.py` + `hdlab/graded_parser.py` found the shipped
decode explicitly DISCARDS the already-computed Matrix-Tree marginals (arc_parser.py line 26: "greedy
hard-decode discards Matrix-Tree marginals"); the opt-in exact-CLE mode decodes on raw arc scores, not
marginals, and only moves UAS +0.002 (cycle-breaking only). This is a decode-objective mismatch, not a
missing-signal problem, and the fix (Minimum-Bayes-Risk / marginal decoding, Smith & Smith 2007 / Koo
et al. 2007 / McDonald & Satta 2007) reuses code already brute-force self-tested on disk.

**Pause state:** not checked by research (pause-gate is exp_dev/orchestrator's concern); this hand-off
is a pointer, not a dispatch — exp_dev applies its own pause-gate check before shipping.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names the ANCHOR + POINTERS only.
exp_dev designs ALL of: exact function signature/parameter names, N (sentence count), which arc-type
subsets to break out, seed count, HARD-PASS/PARTIAL/HARD-FAIL threshold bands (a starting proposal is
given below per the research note but exp_dev owns the final pre-reg), queue choice, smoke profile.

---

## Anchor candidates (rank-ordered)

1. **MBR / marginal-decode swap for the arc parser (PRIORITY 1 — cheap, decisive, same-day)**
   - Anchor pointer: `notes/research_parser_mbr_readout_joint_pos_dmv_2026-09-10.md`, section "Cheap
     decisive test" (Q1) and "HEADLINE".
   - Substrate-product reading: add a `decode="mbr"` path to `hdlab/arc_parser.py` /
     `hdlab/graded_parser.py` that calls the EXISTING `chu_liu_edmonds(M, n)` with `M` built from
     `single_root_marginals(A, n, temp=1.0)` (i.e. `M[h][i] = marg[i][h]`) instead of the raw score
     matrix `A`. No retraining, no new features, no new dependencies — the marginals and CLE are both
     already brute-force self-tested (`graded_parser.py` lines 364-421). Re-run the oracle decomposition
     that produced the 78%-top5-vs-25%-committed finding, broken out by arc type (PP/clausal vs. other),
     comparing greedy (0.406 baseline) vs exact-on-raw-scores (+0.002 known) vs exact-on-marginals (new).
   - Tier hint: local/CPU (parsing + decode only, no training loop; O(n^3) marginal is already computed
     routinely).
   - Why now: this is the single highest-confidence, lowest-cost lever identified in the drill — the
     code delta is small (feed a different matrix into an already-tested function) and the test is
     same-day. Threshold bands proposed in the research note (HARD-PASS >=8pt PP/clausal gain, PARTIAL
     2-8pt, HARD-FAIL <2pt) are a starting point, not binding — exp_dev may sharpen against the actual
     oracle-decomposition harness's own metric conventions.

2. **Reliability-gated adaptive-k readout for the extraction consumer (PRIORITY 2 — gated on #1)**
   - Anchor pointer: same research note, "Cross-thread synthesis" (precision-control paragraph) and
     `hdlab/graded_competition.py` (`graded_pick`, already-pinned math, zero new invention).
   - Substrate-product reading: replace the flat top-2 marginal readout (which admits ~1.1 extra
     (verb,nominal) pairs per arc) with an entropy/margin-gated adaptive set: emit 1 candidate when the
     per-word marginal's normalized entropy is below a calibrated threshold, emit a cumulative-mass
     prefix only when entropy is high (genuinely ambiguous words, concentrated in PP/clausal
     attachment). Reuses `graded_competition.graded_pick(supports={"marginal": log_marginal},
     weights={"marginal": 1.0})` directly — no new module.
   - Tier hint: local/CPU (post-hoc readout change on existing marginals).
   - Why now: only worth running AFTER #1 lands (if #1 closes most of the gap, the precision-cost
     problem shrinks on its own; if #1 is PARTIAL or HARD-FAIL, this becomes the leading lever for
     controlling the admitted-candidate precision cost on whatever residual ambiguity remains).

3. **One lateen-style POS/parse alternation (PRIORITY 3 — bigger, riskier, do LAST and separately)**
   - Anchor pointer: same research note, "Cheap decisive test" (Q2) and "Falsifiable predictions" (Q2
     HARD-PASS/HARD-FAIL bands).
   - Substrate-product reading: ONE alternation round — freeze closed-class scaffold tags, re-estimate
     open-class tag posteriors from structural-role features aggregated from the arc marginals (mixed
     in log-space with the existing distributional posterior, same additive-log/softmax combination rule
     already pinned in `graded_competition.py`), re-run DMV EM, accept only if the Lateen-EM-style dual-
     objective gate (soft-EM likelihood OR Viterbi cost improves) passes, else roll back. Direct
     precedent: Christodoulopoulos, Goldwater & Steedman 2012 ("Turning the pipeline into a loop")
     reports convergence not drift for this class of loop; Spitkovsky, Alshawi & Jurafsky 2011 ("Lateen
     EM") is the source of the dual-objective anti-drift gate.
   - Tier hint: CPU (full DMV EM re-run per round; more expensive than #1/#2).
   - Why now / why last: this is the higher-uncertainty, higher-cost idea (P(converges not drifts) =
     0.40 per the note's deflated calibration) with a real but partial precedent (Christodoulopoulos
     fetch succeeded but did not yield hard per-iteration numbers — genuine gap flagged in the note).
     Keep it as a SEPARATE, independently falsifiable experiment from #1/#2 so a negative result here
     doesn't confound the (much higher-confidence) decode-fix result.

---

## Context pointers (pointers, not summaries)

- `notes/research_parser_mbr_readout_joint_pos_dmv_2026-09-10.md` — the full drill (math, citations,
  calibration, falsifiable predictions for all three anchors above).
- `hdlab/arc_parser.py` — current decode (greedy default; `decode="exact"` = CLE on raw scores; line 26
  BF-note; lines 875-940 marginal computation, currently side-channel-only).
- `hdlab/graded_parser.py` — `single_root_marginals` (Koo et al. 2007, line 233), `chu_liu_edmonds`
  (line 65), `second_best_tree` (Camerini-Fratta-Maffioli 1980, line 280), all self-tested against
  brute force (lines 364-421). This is where the `decode="mbr"` path should most naturally live.
- `hdlab/graded_competition.py` — the PINNED reliability/entropy/margin readout organ (`graded_pick`,
  `net_activation`, `softmax`) for anchor #2; already landed + owner-DONE, zero new invention needed.
- `notes/problems/discrete_where_the_brain_is_graded_in_parsing_and_role_assignment/RESEARCH_graded_competition_brain_mechanism.md`
  — the primary-verified neuroscience/math backing for anchor #2's readout (McClelland 2013
  Bayesian-softmax identity, MAP-optimality theorem, Levy 2008 entropy currency).

---

## Contract

- Pre-reg per envelope-fail-bands: HARD-PASS + HARD-FAIL (+ PARTIAL) bands BEFORE smoke, per the
  starting proposal in the research note (exp_dev may sharpen).
- Self-test per [[feedback-formula-selftests]]: anchor #1's `decode="mbr"` path should include a
  self-test asserting it reduces to the SAME code path/behavior as `decode="exact"` when marginals are
  replaced by a one-hot/degenerate distribution (sanity check that MBR and MAP coincide in the
  zero-uncertainty limit).
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`.
- status_log entry per anchor with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: exact function/parameter names, N, arc-type subset boundaries, seed count,
final threshold bands, queue choice (Tier A/B/C), ETA, smoke profile, FULL profile. Research passes
anchor POINTERS + the underlying math/citations only, per [[feedback-no-experiment-design-in-prompts]].
If exp_dev judges anchor #3 (joint POS/parse loop) is not yet ripe (e.g. anchor #1's result changes the
priority calculus), that is exp_dev's call — anchor #1 is the only one with a HARD "do this first"
recommendation from research.
