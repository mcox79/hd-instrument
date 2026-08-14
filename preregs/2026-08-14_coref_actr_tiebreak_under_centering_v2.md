# PRE-REGISTRATION: exp_coref_actr_tiebreak_under_centering_v2

**Filed:** 2026-08-14, BEFORE any arm was run. Follow-up to
`preregs/2026-08-14_coref_cue_based_retrieval_actr_activation_v1.md` (prereg 1544d7e2a, cell +
results 277f84c36). Organ 4 / E3.

**Cell:** `experiments/exp_coref_actr_tiebreak_under_centering_v2.py`
**Output:** `data/exp_coref_actr_tiebreak_under_centering_v2/` (+ `_smoke/`)

## 1. WHAT v1 ESTABLISHED (evidence, not assumption)

- **D2 = 1.000 on 89/89 multi-candidate decisions.** `salience = count + 0.5*exp(-0.1*d)` is
  *exactly* `argmax count, recency tiebreak`. The top-ranked fidelity gap is confirmed on data.
- **Fixing that arithmetic helps where it acts:** `actr_base` - `base_salience` = **+0.0543**,
  95% CI [+0.0000, +0.1146] (borderline; lower bound touches 0).
- **But replacing the hard structural constraints with graded parallel cues LOSES:**
  `actr_parallel` 0.5843 vs `base_principle_b` 0.7191, delta **-0.1326**, CI [-0.2500, -0.0337]
  = HARD_FAIL. The fan/parallel layer alone was -0.0322 (CI includes 0).
- **Scramble control:** `actr_parallel` scored 0.5938 on order-SCRAMBLED mentions vs 0.5843 ordered
  — that arm was not doing discourse-order-sensitive retrieval at all.

**Mechanism read:** on this corpus the work is being done by the HARD structural constraints —
Centering's Cb tier (`_pick_strict_cb`, most-recent-subject-clause) and Binding Principle B's
same-clause-agent exclusion — not by graded activation. Converting Centering's ORDERING into
arithmetic loses, whether the arithmetic is ours (beta/lambda) or ACT-R's. That is consistent with
the ORGAN_MAP's own note that the literature supplies an ORDERING, not numbers.

## 2. THE QUESTION THIS CELL ASKS (one variable)

v1 replaced the architecture. This cell KEEPS the winning architecture and fixes only the arithmetic
underneath it. `_pick_strict_cb` (`hdlab/coreference_resolver.py:227-236`) breaks ties, and falls
back when no candidate has subject history, on **`last_pos` = pure recency**:

```
tied = [e for e,c in with_subject if c == best_c]
return max(tied, key=lambda e: e.last_pos)     # tiebreak
return max(compat, key=lambda e: e.last_pos)   # no-subject-history fallback
```

Replace **only that key** with ACT-R base-level activation `B_i = ln(sum_k (now - t_k + 1)^-0.5)`
(d = 0.5 PINNED). Nothing else changes: same Principle B filter, same Cb tier, same name/nominal
branch, same abstention policy (none), same registry.

**Does a commensurate frequency+recency trace beat pure recency as Centering's tiebreaker?**

## 3. ARMS

1. `floor_most_recent` — trivial floor 1 (required)
2. `floor_singleton` — trivial floor 2 (required)
3. `base_principle_b` — current canonical, unchanged (the arm to beat)
4. `pb_actr_tiebreak` — ONLY the tiebreak/fallback key changed to base-level activation
5. `pb_salience_tiebreak` — ONLY the tiebreak/fallback key changed to the DEGENERATE count-primary
   salience. Diagnostic control: separates "the Cb tier is what wins" from "the recency tiebreak is
   what wins". If this arm collapses toward `base_salience`, the tiebreak is load-bearing; if it
   holds near `base_principle_b`, the tier is.

## 4. DATA, METRIC, BANDS — identical to v1 so numbers are directly comparable

Same two gold sets (54 passages, 500 mentions, 136 pronoun decisions, 89 competitive).
**PRIMARY `P`** = pooled link-level pronoun accuracy on the competitive subset (>=2 gn-compatible
candidates). Paired cluster bootstrap over passages, 10,000 resamples, seed 12345.

Judged for `pb_actr_tiebreak`:
- **HARD_PASS** — beats both trivial floors AND delta vs `base_principle_b` >= +0.05, CI excludes 0
- **PASS** — beats both floors AND delta >= +0.02, CI excludes 0
- **MIDDLE_BAND** — beats both floors, delta in (-0.02, +0.02) or CI includes 0
- **FAIL** — fails a trivial floor, OR delta <= -0.02
- **HARD_FAIL** — delta <= -0.05, CI excludes 0

## 5. DISCRIMINATOR (range by construction)

**D1** — competitive-subset decisions where `pb_actr_tiebreak` differs from `base_principle_b`.
Range 0..89. **If D1 < 10 the cell reports VACUOUS, not a band.** This is a real risk here and is
stated in advance: the Cb tier may resolve most decisions before any tiebreak is consulted, in which
case the arms cannot differ and the correct report is "the tiebreak is not reached often enough to
matter" — itself a finding about where the resolver's signal lives.

**D_tier** — count of competitive decisions that reach the tiebreak at all (>=2 candidates tied on
most-recent-subject-clause, or no candidate with subject history). Range 0..89. Reported regardless.

No band may be reached by choosing a dataset or by substituting a secondary metric.

## 6. ENGINEERING

Thread pins at top of file before numpy. Fresh dirs, smoke separate. `metrics.json` once via
tmp + `os.replace`. `sorted(set())`. Per-unit checkpoint via `tools/exp_checkpoint.py`.
`--timeout 900` (v1 measured 0.39s end-to-end; enormous margin). Pure symbolic CPU.
