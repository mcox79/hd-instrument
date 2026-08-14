# PRE-REGISTRATION: exp_coref_cue_based_retrieval_actr_activation_v1

**Filed:** 2026-08-14, BEFORE any arm was run. Organ 4 (E3, coreference as competitive retrieval),
`notes/ORGAN_MAP.md` E3.

**Cell:** `experiments/exp_coref_cue_based_retrieval_actr_activation_v1.py`
**Output:** `data/exp_coref_cue_based_retrieval_actr_activation_v1/` (full),
`data/exp_coref_cue_based_retrieval_actr_activation_v1_smoke/` (smoke, separate dir)

---

## 0. CORRECTION TO THE FLOORS THIS CELL WAS COMMISSIONED AGAINST (filed before the run)

The commissioning brief and `notes/ORGAN_MAP.md` (lines 671-672, 1103-1104) state that two trivial
baselines have ALREADY BEATEN our resolver: **most-recent-mention 0.5439** and **singleton 0.4737**.
Recomputed off disk before writing this cell, that does not hold.

Both cited numbers trace, via `experiments/exp_extraction_quality_gate_neural_coref_v2.py:30-32`, to
`exp_wire_coref_accumulate_situation_model_v1`, metric `query_accuracy_identity_demanding`, eval
`powered`. Aggregating that run's own `data/exp_wire_coref_accumulate_situation_model_v1/units.jsonl`
(270 units) with `.venv/Scripts/python.exe`:

| arm | powered (57 iddem queries) | g5g6_reviewed (25) |
|---|---|---|
| oracle | 0.9298 (53/57) | 0.9600 |
| **strict_cb (ours)** | **0.7193 (41/57)** | 0.7600 |
| earned/salience (ours) | 0.6842 (39/57) | 0.6400 |
| recency_floor | **0.5614 (32/57)** | 0.5200 |
| singleton_floor | **0.3860 (22/57)** | 0.3600 |

`oracle` and `earned` reproduce the citation EXACTLY (0.9298 / 0.6842); the two FLOOR arms do not
(0.5439 = 31/57 and 0.4737 = 27/57 back-solve to different counts). `exp_wire`'s own docstring
records a collision-policy metric bug that inflated the floor arms, "FIXED 2026-08-02"; its
`metrics.json` is stamped `2026-08-02T21:49`, and the citing cell is stamped 2026-08-10 — so the
citing cell quotes pre-fix floor values while quoting post-fix oracle/earned values from the same
run. ORGAN_MAP inherits it one hop further.

Triple-check per CLAUDE.md Evidence discipline §5: (1) right file — `units.jsonl` of the run both
citations name; (2) right version — HEAD, as on disk today; (3) right environment —
`.venv/Scripts/python.exe`; (4) right corpus — `powered` = `gold_combined_pronoun_powered_v1.jsonl`
for every arm in the table; (5) right metric — `q_correct_iddem/q_total_iddem`, the metric the citing
docstring names; (6) right arm — all five arms from that single run.

Separately, the `0.5669` that ORGAN_MAP reports as the NO_GO gate value is `coref_b3_f1` for the
**fastcoref neural** arm on the **`modern_coref_00X`** set (10 passages, 42 mentions) — a different
metric, corpus AND arm from the 0.5439/0.4737 floors. The two were never comparable.

**Consequence for this cell:** the honest bar is HIGHER than commissioned, not lower. Both trivial
floors are carried as required, but the arm that must be beaten is our own `strict_cb`/`principle_b`
at ~0.72, measured in the same run. Bands below are set against that, not against the floors.

---

## 1. FIDELITY AUDIT (done before designing the fix; ORGAN_MAP format)

Brain operation: antecedent resolution = **cue-based content-addressable retrieval** from
declarative memory (hippocampal relational retrieval), NOT positional search. Constituent ops:

| # | operation | BRAIN'S MATH | OURS (exact, file:line) | verdict | predicts a known failure? |
|---|---|---|---|---|---|
| 1 | **Competition / selection** | ACT-R activation `A_i = B_i + sum_j W_j*S_ji`; base level `B_i = ln(sum_k (t-t_k)^-d)`, **d=0.5 PINNED** (Anderson & Schooler 1991, power law of forgetting; Lewis & Vasishth 2005 use this form directly) | `salience = count + 0.5*exp(-0.1*(now-last_pos))`, `coreference_resolver.py:192` = `state_of_mind.py:247` | **WRONG-OP + DEGENERATE** | **YES — top gap** |
| 2 | **Interference** | similarity-based interference via **fan**: `S_ji = S - ln(fan_j)`; a cue matching many items loses diagnosticity (Jaeger, Engelmann & Vasishth 2017 meta-analysis) | **none.** `gn_compatible()` `:127-135` is boolean and fan-blind; two same-gender candidates interfere by exactly 0 | **MISSING** | YES |
| 3 | **Candidate set** | **all items in parallel**, content-addressable; retrieval latency flat in dependency distance (McElree SAT); cues combine by weighted parallel constraint satisfaction, **explicitly not filter-then-rank** | `compat = [e for e in entities if gn_compatible(...)]` `:333`, `:397`, `:444` — hard filter, then rank only survivors | **WRONG-OP** (the one architecture the source rules out) | YES |
| 4 | **Cue construction** | cues posted simultaneously, total attention `W` split `W_j = W/n_cues`; every cue graded | gender/number = boolean gate; role = a **separate later stage** (`_pick_strict_cb:227-236` hard tier); recency = a third stage | **RIGHT-OP-WRONG-PLACE** (serial stages, not one parallel probe) | partly |
| 5 | **Update** | each presentation appends a trace; all traces decay by power law and are summed | `count += 1; last_pos = pos`, `:265-269` — history collapsed to (integer, last timestamp) | **MISSING** (no trace history) | YES — it is what MAKES #1 degenerate |
| 6 | Abstention | reference-set computation matures late (children over-accept to ~10-11 yrs) -> margin gate | top1-top2 relative margin < 0.10, `:341` | **RIGHT-OP** — genuine fidelity win, KEPT | n/a |

**Why #1 is ranked top — it is an analytic degeneracy, not a matter of taste.**
`count` is an integer and `0.5*exp(-0.1*d)` lies in `(0, 0.5]`. Therefore if
`count_a >= count_b + 1` then `salience_a >= count_b + 1 > count_b + 0.5 >= salience_b`, always.
**The recency term can never overturn a count difference of 1.** Our "Centering salience" is
*exactly* `argmax count, ties broken by recency` — a pure frequency rule. The brain's
`ln(sum_k (t-t_k)^-d)` puts frequency and recency on ONE commensurate scale, where a recent single
mention CAN outrank an old frequent one. We made that structurally impossible.

**The failure it predicts:** in turn-taking dialogue with two same-gender participants, every pronoun
goes to the higher-count participant regardless of who was just mentioned — i.e. exactly the regime
where a most-recent-mention floor is competitive with us, and exactly the "agent-vs-agent turn-taking
mispicks" that `run_strict_cb`'s docstring says it was written to patch symptomatically
(`coreference_resolver.py:376-378`). It also explains why the honest-mode gate at relative margin
0.10 is arbitrary: with integer counts, "relative margin < 0.10" reduces to "count gap of 1 at count
>= 10", a quantity with no mechanism behind it.

**Reuse check (owned organs, per the standing rule).** `cleanup_family` / `iterative_attractor` are
CA3 pattern completion over **numpy hypervector codebooks** (`query, codebook -> cleaned vector`,
`cleanup_family.py:16-24`); `dg_pattern_separation` is DG separation over the same. The competition
here is over a **symbolic** entity registry with discrete feature cues and a temporal trace. Routing
it through `cleanup_family` would require first encoding entities as hypervectors, inserting a lossy
vector channel that carries none of the base-level or fan arithmetic that is the actual fix. **Judged
does-not-serve, with that reason.** The fix instead REUSES the resolver's own registry, its
name/nominal branch, its margin-abstention, and its confidence signals unchanged.

---

## 2. THE FIX (one organ, two ablatable layers)

Replace `TrackedEntity.salience` with ACT-R cue-based retrieval activation. Entities gain
`presentations: List[int]` (every mention position, not just the last).

```
B_i(now) = ln( sum_k (now - t_k + 1)^(-d) )                 d = 0.5   [PINNED]
A_i      = B_i + sum_{j in cues} W_j * (S - ln(fan_j)) * match_ij
W_j      = W / n_cues ;  fan_j = # tracked entities matching cue j ;  match in {0,1}
```
Cues for a pronoun (3): gender, number, `cb_subject` (held a subject-like/agent role in the
immediately preceding clause — Centering's ORDERING entering as a weighted CUE, not a hard tier).

**HONESTY ON PARAMETERS.** `d = 0.5` is pinned by the literature. `W` and `S` are **NOT** pinned for
this task; using ACT-R defaults `W = 1.0`, `S = 1.5` is a choice, and pretending otherwise would
repeat the exact fault the audit charges against `beta`/`lambda`. Mitigation, committed here:
the PRIMARY result is `W=1.0, S=1.5, d=0.5` and **only** that; `S in {1.0, 1.5, 2.0}` is reported as
a SENSITIVITY table and is explicitly NOT eligible to set the headline. No band may be reached by
selecting an S.

---

## 3. ARMS (name/nominal branch byte-identical across arms 4-8; only the pronoun pick varies)

1. `floor_most_recent` — pronoun -> most recently mentioned entity. No features. **trivial floor 1**
2. `floor_singleton` — every mention is its own entity. **trivial floor 2**
3. `floor_chain_all` — `run_recency_floor` (existing chain-everything-to-0 floor)
4. `base_salience` — `run_match_or_allocate` (current `count + beta*exp`)
5. `base_strict_cb` — `run_strict_cb`
6. `base_principle_b` — `run_principle_b` (current canonical; the arm to beat)
7. `actr_base` — B_i only (ln-sum power law), **hard gn filter RETAINED**
8. `actr_parallel` — full: no hard filter, fan-weighted parallel cues

**One-variable controls.** `actr_base` vs `base_salience` differs in the salience function ONLY
(same filter, same argmax, same update, same name branch) -> isolates gap #1 (degeneracy).
`actr_parallel` vs `actr_base` differs in candidate-set/cue treatment ONLY -> isolates gaps #2+#3
(interference, parallelism).

**SCRAMBLE control.** `actr_parallel_scrambled`: mention order shuffled within passage (seed 12345).
If a win survives scrambling it is not discourse structure. Expected to drop; range by construction.

## 4. DATA

`data/eval_gold_mention_role_mcguffey_v1/gold_combined_pronoun_powered_v1.jsonl` (36 passages, 349
mentions, 76 pronoun) + `gold_g5g6_dense_pronoun_verbatim_v1_reviewed.jsonl` (18, 151, 60). Pooled:
54 passages, 500 mentions, 136 pronoun decisions, of which ~89 have >=2 gn-compatible competitors.
Scope stated plainly: this is McGuffey-derived graded reader prose, not open-domain text.

## 5. METRICS AND BANDS (committed before the run)

**PRIMARY `P`** = pooled link-level pronoun accuracy on the **COMPETITIVE subset** (pronoun decisions
with >=2 gn-compatible candidates), via `mention_link_wrong` — the ORGAN_MAP's own CAN-FAIL test
("resolving a pronoun among >=2 plausible candidates"), decision-time-clean and not contaminated by
later mentions. **SECONDARY `S2`** = pooled pronoun-subset B-cubed F1.

Bands on `P`, judged for `actr_parallel`, with **paired cluster bootstrap over passages**
(10,000 resamples, seed 12345; arms share items so pairing is required):

- **HARD_PASS** — beats BOTH trivial floors AND `P(actr_parallel) - P(base_principle_b) >= +0.05`
  with 95% CI on the paired delta excluding 0.
- **PASS** — beats both trivial floors AND delta `>= +0.02` with CI excluding 0.
- **MIDDLE_BAND** — beats both trivial floors, delta in `(-0.02, +0.02)` or CI includes 0.
- **FAIL** — fails to beat either trivial floor, OR delta `<= -0.02`.
- **HARD_FAIL** — delta `<= -0.05` with CI excluding 0.

No band may be reached by choosing S, by choosing a dataset, or by reporting the secondary in place
of the primary. A negative is a result and is reported as one.

## 6. DISCRIMINATORS (range by construction; D1 gates the whole cell)

- **D1 (vacuity gate)** — count of competitive-subset decisions where `actr_parallel`'s pick differs
  from `base_salience`'s pick. Range 0..~89. **If D1 < 10 the cell reports VACUOUS, not a band** —
  arms that never disagree cannot be compared.
- **D2 (degeneracy witness)** — fraction of multi-candidate `base_salience` decisions where
  `argmax salience == argmax count` (recency tiebreak). Range 0.0..1.0. **Audit predicts 1.000**; any
  value below 1.0 falsifies section 1's analytic claim.
- **D3 (fan activity)** — count of competitive decisions where the gender cue's fan >= 2, i.e. where
  the `-ln(fan)` term is actually load-bearing. Range 0..~89. If 0, gap #2's fix could not have acted.

## 7. ENGINEERING

`OMP_NUM_THREADS`/`OPENBLAS_NUM_THREADS` pinned at top of file before numpy import. Fresh output dir;
smoke to a separate dir. `metrics.json` written once via tmp + `os.replace`. `sorted(set())`
throughout. Per-unit checkpoint via `tools/exp_checkpoint.py` (unit = arm x dataset). Pure symbolic
CPU, no torch, no network. `--timeout 900` (measured self-test estimate ~40s; 20x margin).
