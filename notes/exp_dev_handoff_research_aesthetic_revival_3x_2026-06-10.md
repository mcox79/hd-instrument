# exp_dev hand-off -- research: aesthetic revival 3x

Filed-by: research sub-agent (2026-06-10)
Trigger: notes/research_drill_aesthetic_revival_3x_2026-06-10.md
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

A 3-stream synthesis (brain neuroaesthetics, evolutionary biology, LLM theory) establishes
that aesthetic quality is fundamentally a temporal signal -- prediction error buildup
followed by coherent resolution -- not a static feature of style or genre compliance.
Substrate cleanup margins already proxy this signal: they measure how easily a composition
step resolves. The cleanup-margin trajectory across a passage is a natural frisson proxy.

Three metrics are proposed for immediate empirical test, all CPU-only:
  (1) frisson-proxy: margin-spike events at high-error steps
  (2) anomaly x skill composite: Berlyne optimal incongruity in substrate algebra
  (3) compression-progress: cumulative positive margin improvement across steps

A 4th test (evolutionary tournament) tests whether the substrate can discriminate
human-preferred passages by choosing the one it can more accurately complete.

All 5 pre-tests are laptop CPU, under 1 hour each. No cloud needed.

---

## Anchor Candidates (rank-ordered by P_actionable x cost)

### 1. AES-FRISSON-T1 -- frisson proxy baseline (HIGHEST PRIORITY)

Anchor pointer: AES-FRISSON-T1 (new; not yet queued)
Substrate-product reading: Tests whether substrate cleanup margin dynamics predict human
  aesthetic ratings. If yes, the substrate has a structurally distinct aesthetic quality
  signal that LLMs lack (their RLHF reward models optimize static surface quality, not
  temporal dynamics). Validates the core D2.3 mechanism.
Tier hint: CPU laptop; ~20 min wall; requires 50 short passages with human aesthetic
  ratings 1-10 (use WritingPrompts rated dataset or manually rate a sample).
Why-now: Cheapest possible gate. Either the signal is there (proceed to D2.1, D2.2) or
  it is not (ruling out the aesthetic recovery direction entirely).

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: Pearson r >= 0.40 between frisson_event_count and human rating at N=50
  HARD-FAIL: r < 0.15 after controlling for passage length (signal indistinguishable
             from noise; rules out D2.3 frisson proxy)
  MID-BAND: r in [0.15, 0.40]; scale to 200 passages before conclusion

Implementation note: frisson_event at step t = 1 if:
  cleanup_margin(t) > cleanup_margin(t-1) + delta
  AND cleanup_margin(t-1) < low_threshold
  where delta and low_threshold are hyperparameters to sweep (e.g., delta in [0.05, 0.15];
  low_threshold in [0.3, 0.5]).

### 2. AES-ANOMALY-T2 -- anomaly x skill composite (INDEPENDENT OF T1)

Anchor pointer: AES-ANOMALY-T2 (new; not yet queued)
Substrate-product reading: Tests whether the product form (anomaly_margin x skill_score)
  predicts human aesthetic ratings better than either component alone. This directly
  implements Berlyne optimal incongruity in substrate algebra.
Tier hint: CPU laptop; ~20 min wall; uses same 50-passage set as T1
Why-now: Independent of T1; can run in parallel. Simpler formulation, cleaner
  implementation path.

Pre-reg bands:
  HARD-PASS: Product form improves Kendall tau over best single component by >= 0.05
  HARD-FAIL: Product performs worse than better single component (anomaly and skill are
             not complementary in practice)
  MID-BAND: tau improvement in [0.02, 0.05]; extend to 200 passages

### 3. AES-COMPRESSION-T3 -- compression-progress metric (INDEPENDENT)

Anchor pointer: AES-COMPRESSION-T3 (new; not yet queued)
Substrate-product reading: Tests whether cumulative positive cleanup margin improvement
  (compression-progress proxy) predicts human ratings better than static average margin.
Tier hint: CPU laptop; ~20 min wall; same passage set
Why-now: Independent. If this works better than static margin, it validates the
  temporal-dynamics hypothesis (not just average quality but rate of improvement matters).

Pre-reg bands:
  HARD-PASS: Compression-progress r >= 0.35 AND outperforms static average margin r
  HARD-FAIL: r < 0.15 AND static margin r >= 0.25 (temporal dynamics add nothing)
  MID-BAND: Compression-progress r in [0.15, 0.35] approximately matching static margin

### 4. AES-TOURNAMENT-T4 -- evolutionary tournament discriminability

Anchor pointer: AES-TOURNAMENT-T4 (new; not yet queued)
Substrate-product reading: Tests whether substrate can discriminate human-preferred
  passages from alternatives by choosing the one it can more accurately extend/complete.
  This is the adaptive-adversary mechanism (D2.4) and the most structurally novel test.
Tier hint: CPU laptop; ~30 min wall; requires 25 passage pairs where one is
  human-rated higher than the other
Why-now: If T1 or T2 HARD-PASS, T4 provides independent validation via a different
  mechanism (utility-based preference rather than margin-dynamics-based scoring).

Pre-reg bands:
  HARD-PASS: Substrate chooser selects human-preferred passage in >= 68% of 25 pairs
             (p < 0.05 vs. chance)
  HARD-FAIL: <= 52% correct (not distinguishable from chance)
  MID-BAND: 53-67% correct; extend to 50 pairs

### 5. AES-LLM-COMPARE-T5 -- LLM baseline comparison (prerequisite: T1 or T2 pass)

Anchor pointer: AES-LLM-COMPARE-T5 (new; not yet queued)
Substrate-product reading: Tests whether substrate aesthetic metrics distinguish
  human creative writing from high-quality LLM-generated text. If substrate metrics
  systematically score human-written passages higher on frisson/anomaly/compression-
  progress than LLM-generated passages rated equivalently by surface quality criteria,
  this is evidence the substrate captures an aesthetic signal orthogonal to LLM RLHF.
Tier hint: CPU laptop; ~40 min wall (requires Pythia-160M inference for LLM baseline)
Why-now: Only queue after T1 or T2 passes; no point testing LLM comparison if base
  substrate metrics do not predict human ratings.

Pre-reg bands:
  HARD-PASS: Substrate metrics distinguish human creative vs. LLM-generated at AUC >= 0.65
  HARD-FAIL: AUC <= 0.52 (substrate metrics cannot separate human from LLM text)
  MID-BAND: AUC in [0.52, 0.65]; test with larger models or fine-tuned LLM text

---

## Passage dataset note

If no rated creative writing dataset is available locally, exp_dev can:
  (a) Use WritingPrompts dataset (publicly available, community-rated) -- 10K+ stories
      with Reddit upvote scores as aesthetic quality proxy (imperfect but usable)
  (b) Use PoetryFoundation dataset with manually assigned quality tiers
  (c) Manually rate 50 short passages (1-2 paragraphs) from literary and non-literary
      sources using a 1-10 scale

The key requirement is variance in aesthetic quality across the passage set. Passages
should span low-quality (generic, schema-fit) to high-quality (surprising, coherent,
emotionally resonant). Do not use passages pre-filtered for genre compliance.

---

## Strategic context for exp_dev

The core hypothesis is that substrate cleanup margin dynamics are an implicit frisson
proxy -- they naturally measure the temporal structure that brain research identifies
as the generator of aesthetic reward. This is NOT a new capability claim: the substrate
already computes cleanup margins for all composition operations. The tests only require
computing those margins on an aesthetic passage set and checking correlation with human
ratings.

If T1-T3 all HARD-FAIL: the margin dynamics do not predict human aesthetic preference.
  This would mean the substrate's retrieval mechanics are orthogonal to aesthetic quality
  and the aesthetic recovery direction should be closed.

If T1 or T2 HARD-PASS: aesthetic scoring becomes a potential product feature. Route to
  orchestrator for cap_map consideration (new row: aesthetic_quality_scoring).

If T4 HARD-PASS (tournament): the adaptive-adversary mechanism works. This is the more
  significant result because it does not depend on margin calibration thresholds. Route
  to orchestrator for cap_map consideration.

Dispatch priority: T1, T2, T3 in parallel (independent, same passage set). T4 after T1-T3
results known. T5 only if T1 or T2 HARD-PASS.

---

## Context pointers

- Research note (full analysis, all 3 streams, 8 crazy mechanisms, 32 citations):
  d:/AI/hd-instrument/notes/research_drill_aesthetic_revival_3x_2026-06-10.md
- Substrate cleanup margin implementation:
  hdlab/ (substrate library; cleanup margin is computed during composition operations)
- Substrate cap_map (no current aesthetic row; new row candidate post-validation):
  d:/AI/hd-instrument/data/substrate_capability_map.md

---

## Contract section

This hand-off provides 5 pre-test specs (T1-T5) as research recommendations. Exp_dev
is responsible for:
- Assembling a 50-passage rated dataset (human aesthetic ratings 1-10)
- Implementing frisson_event counter, anomaly_margin, skill_score, compression_progress
  computations using existing substrate cleanup margin data
- Assigning all tests to correct queue (CPU laptop; all tests run fast)
- Writing verdict notes for each test per standard protocol
- Escalating any HARD-PASS result to orchestrator for cap_map consideration
- NOT dispatching T5 without T1 or T2 passing first

## Autonomy declaration

Exp_dev may dispatch T1, T2, T3, T4 independently without orchestrator approval (all
are CPU pre-tests, under 30-40 min each, low cost, no cloud needed). T5 requires T1 or
T2 HARD-PASS as prerequisite. A HARD-PASS on T1 or T4 that would support adding a new
cap_map row for aesthetic quality scoring MUST be escalated to orchestrator before any
cap_map modification is made.
