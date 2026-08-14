# PRE-REGISTRATION -- exp_coref_cb_literal_centering_window_and_cf_rank_v1

DATE: 2026-08-14
ORGAN: E3 (coreference). PHASE 2 of 2. Phase 1 =
`preregs/2026-08-14_coref_cb_tier_error_anatomy_v1.md` (commit 5f31c838f), results committed
before this file was written.

STATUS: written and committed BEFORE any arm of this cell was run.

---

## 1. WHAT PHASE 1 MEASURED (the licence for this cell)

MEASURED@d:/AI/hd-instrument/data/exp_coref_cb_tier_error_anatomy_v1/metrics.json

- **ZERO of the 25 errors are RETRIEVAL failures.** On every single competitive decision the gold
  antecedent WAS in the pool `_pick_strict_cb` ranks over. `P_ceiling_ranking = 1.0000`. The
  agreement filter, the Principle-B filter and the name-branch allocation never lost the answer.
  **The whole gap is a RANKING failure.**
- **21 of 25 errors are `RANKING_cb_unique_wrong`** -- the Cb tier did not tie and did not fall
  through; it uniquely, confidently picked the wrong entity. Only 2 were in the tiebreak
  (reproducing the v2 cell's VACUOUS finding from the other side) and 2 in the no-subject-history
  fallback.
- The separator is total: **when the gold antecedent was the subject of the IMMEDIATELY PRECEDING
  clause, the resolver is 24/24 correct. All 25 errors are cases where it was not.**

## 2. HARNESS DEFECT FOUND IN PHASE 1 AND FIXED HERE (disclosed, not quietly patched)

`gold_g5g6_dense_pronoun_verbatim_v1_reviewed.jsonl` (18 passages) is a **STRICT SUBSET** of
`gold_combined_pronoun_powered_v1.jsonl` (36 passages) -- verified by passage_id, 18/18 contained.
The v1 ACT-R cell, the v2 tiebreak cell and Phase 1 all POOL the two, so 18 of 36 passages are
**double-counted**: "54 passages / 89 competitive decisions / 25 errors" is really **36 unique
passages / 52 unique competitive decisions / 16 unique errors**, with the g5g6 half carrying double
weight and the paired cluster bootstrap resampling duplicated passages (artificially narrow CIs).

**This cell's PRIMARY corpus is the DEDUPED set: `gold_combined_pronoun_powered_v1.jsonl` alone, 36
passages.** The legacy pooled view is computed and reported as an explicitly-labelled SECONDARY for
continuity with the three prior cells, and may NOT set a band.

Deduped Phase-1 anatomy (recount of the same pre-registered partition, same metrics.json):
n_competitive **52**, errors **16**, `base_principle_b` P = **0.6923**, causes
{cb_unique_wrong 14, cb_tied_wrong 1, cb_none_wrong 1}, retrieval failures **0**.
gold-is-prev-clause-subject 16/16 correct; gold-not-prev-clause-subject 16/36 wrong.

## 3. THE FIDELITY GAP THIS CELL ATTACKS

`hdlab/coreference_resolver.py:194-197` +`:227-236`:

```
most_recent_subject_clause(cur_clause) = max{ c : clause_role[c] in {"agent"}, c < cur_clause }
_pick_strict_cb = argmax over that value; ties and no-history -> last_pos
```

Two deviations from Centering Theory (Grosz, Joshi & Weinstein 1995; Brennan, Friedman & Pollard
1987), both CITED@ that literature, not invented here:

**(i) The lookback is UNBOUNDED.** Centering defines Cb(U_n) over **Cf(U_{n-1})**, the immediately
preceding utterance. Ours searches the entire prior discourse for the last clause in which the
entity was an agent. Consequence: an entity that was a subject six clauses ago outranks an entity
realized in the immediately preceding clause. Phase 1's `clause_dist_gold >= 2` stratum is
**6 of 7 wrong (86%)** deduped -- exactly this.

**(ii) Cf is RANKED; ours is BINARY.** Centering's Cf ordering is
SUBJECT > DIRECT OBJECT > INDIRECT OBJECT > OTHER. `SUBJECT_LIKE_ROLES = frozenset({"agent"})`
collapses every non-agent role into "no subject history", which drops the entity out of the Cb tier
entirely rather than ranking it lower. Consequence: a previous-clause OBJECT cannot be preferred
over an ancient subject. Phase 1 deduped: object pronoun `him` **9 of 20 wrong (45%)** vs `he`
**7 of 30 (23%)**; `gold never subject` **10 of 23 wrong (43%)**.

These are the ORDERING the literature supplies. The correction restores the ordering; it does not
invent new arithmetic. (This cell adds no free real-valued parameters at all -- see section 5.)

**BRAIN STRUCTURE + REUSE CHECK (mandatory).** The organ is hippocampal relational antecedent
retrieval with Centering as the linguistic backbone. This cell changes only the RANKING KEY inside
the organ already built (`hdlab/coreference_resolver.py`); it spawns no parallel organ. Checked and
judged does-not-serve: `cleanup_family` / `iterative_attractor` (CA3 pattern completion) and
`dg_pattern_separation` (DG separation) operate on numpy hypervector codebooks; this competition is
over a symbolic registry with discrete grammatical cues, so routing through them would insert a
lossy vector channel carrying none of the Cf-ordering information. `hdlab/coref.py:119-120` holds a
role-parallelism bonus (0.5 for subject, +0.5 parallel role) -- NOTED as a sibling lever, NOT used
here, because using it would be a second variable. It is the named alternative if this cell fails.

## 4. ARMS -- ONE VARIABLE EACH, OFF THE SAME BASE

Base for every arm is `run_principle_b`: agreement filter, Principle-B filter, name/nominal branch,
registry growth and abstention policy held byte-identical. **Only the pronoun-pick key changes.**

| arm | what changes from base | variables changed |
|---|---|---|
| `base_principle_b` | nothing (incumbent) | 0 |
| `arm_A_cb_window_prev_clause` | subject-history lookback restricted to `c == cur_clause - 1` (was: any `c < cur_clause`). Tier stays BINARY agent. | 1 (window) |
| `arm_B_cf_graded_rank` | binary agent tier replaced by graded Cf rank; lookback stays UNBOUNDED. Key = lexicographic max over `c < cur_clause` of `(c, CF_RANK[role_at_c])`. | 1 (tier granularity) |
| `arm_C_cb_literal_centering` | BOTH (the textbook Cb: among candidates realized in the most recent clause any candidate was realized in, take the highest Cf rank) | 2 -- declared COMPOSITION |

**HEADLINE ARM, DECLARED NOW AND NOT REVISABLE: `arm_C_cb_literal_centering`.** It is the
literature's actual definition of Cb. A and B exist to isolate which of the two deviations carries
the effect and are reported whatever they do; **neither may be promoted to headline after the fact**
if C fails and one of them happens to win. If A or B beats C, that is reported as an interaction
finding, not as the cell's result.

### CONTROLS

| control | isolates |
|---|---|
| `ctrl_cb_off_pure_recency` | the Cb tier removed entirely from the same pipeline (pick = argmax `last_pos` over the pool). **The load-bearing control:** if arm A merely equals this, the "window fix" is recency in disguise and the Cb tier is doing nothing. |
| `floor_most_recent` | trivial floor 1, same run, same metric, same corpus |
| `floor_singleton` | trivial floor 2, same run, same metric, same corpus |
| `arm_C_scrambled` | mention order shuffled within passage (seed 12345). A win that survives scrambling is not discourse structure. |

## 5. THE Cf RANK MAP -- PRE-COMMITTED, LITERATURE-DERIVED, NOT SWEPT

```python
CF_RANK = {"agent": 3, "experiencer": 3, "patient": 2, "theme": 2, "recipient": 1}
# entity with no role history at all -> -1 (sorts below every ranked entity)
```

Derivation, CITED@Brennan/Friedman/Pollard 1987 Cf ordering SUBJ > DOBJ > IOBJ > OTHER, mapped onto
this gold's thematic-role vocabulary (the complete vocabulary is exactly
{agent, patient, experiencer, theme, recipient} -- verified against the corpus, not assumed):
agent -> SUBJ; experiencer -> SUBJ (English psych verbs are predominantly experiencer-subject:
see, hear, feel, fear, want); patient, theme -> DOBJ; recipient -> IOBJ.

**This map is FIXED. It is not a tuning surface and will not be swept to reach a band.** One
declared SENSITIVITY variant is computed and reported and is **NOT HEADLINE-ELIGIBLE**:
`CF_RANK_ALT = {"agent": 3, "patient": 2, "theme": 2, "experiencer": 1, "recipient": 1}`
(experiencer demoted, for the object-experiencer reading). If the two disagree materially that is
itself reported as a fidelity caveat about thematic-vs-grammatical role.

**Known fidelity caveat, stated in advance:** the gold supplies THEMATIC roles, and Centering's Cf
is over GRAMMATICAL functions. Passives and psych verbs break the correspondence. This mapping is
therefore an approximation of Cf, and a negative result here does NOT refute Centering's Cf
ordering -- it refutes THIS mapping of it onto THIS role vocabulary. That distinction goes in the
verdict message.

## 6. DISCRIMINATORS -- RANGE BY CONSTRUCTION, MACHINE-COMPUTED, NO HAND SCORING

- **D1_<arm>** = competitive decisions where the arm's assignment differs from `base_principle_b`.
  Range 0..52. **Vacuity gate: an arm with D1 < 10 is reported VACUOUS and cannot take a band** --
  the same gate that correctly caught the v2 tiebreak cell.
- **D2_window_can_bite** = decisions where base's winning `most_recent_subject_clause` is
  `< cur_clause - 1` (i.e. the unbounded lookback actually reached past the previous clause).
  Range 0..52. If ~0, arm A is vacuous BY CONSTRUCTION and we will say so rather than read its delta.
- **D3_grading_can_bite** = decisions where the pool contains >=2 distinct CF_RANK values in the
  most recent clause any candidate was realized in. Range 0..52. Same role for arm B.
- **D4_arms_differ** = pairwise assignment-hash inequality across all arms (META_RULE_AF).

## 7. BANDS -- COMMITTED BEFORE THE RUN, ON THE DEDUPED PRIMARY

Primary metric P = link-level pronoun accuracy (`mention_link_wrong`) on the COMPETITIVE subset
(>=2 gn-compatible candidates), 36 deduped passages, 52 decisions. delta = P(headline) -
P(`base_principle_b`), paired CLUSTER bootstrap over the 36 passages, 10000 resamples, seed 12345
(arms share items, so passage indices are resampled once and applied to both arms).

- **VACUOUS** -- D1(headline) < 10.
- **FAIL (floor breach)** -- headline does not beat BOTH `floor_most_recent` and `floor_singleton`.
- **HARD_FAIL** -- delta <= -0.05 and the 95% CI excludes 0.
- **FAIL** -- delta <= -0.02.
- **MIDDLE_BAND** -- -0.02 < delta < +0.02, or delta >= +0.02 with a CI that includes 0.
- **PASS** -- delta >= +0.02 and CI excludes 0.
- **HARD_PASS** -- delta >= +0.05 and CI excludes 0 and headline beats both floors.

**POWER, STATED IN ADVANCE AND NOT TO BE FORGOTTEN DOWNSTREAM.** 52 decisions over 36 passages.
delta = +0.05 is **2.6 decisions**; a 95% CI over 36 passages will be wide. **MIDDLE_BAND is the
most likely honest outcome even if the mechanism is right**, and a MIDDLE_BAND here must be
reported as "direction measured, magnitude not resolvable on this corpus", NOT as a win and NOT as
a refutation. **No arm will be tuned, no threshold moved, and no sensitivity variant promoted, to
escape MIDDLE_BAND.** The corpus is what it is; the fix for underpower is more gold, not a
different band.

## 8. WHAT COUNTS AS A NEGATIVE, AND WHAT WE DO WITH IT

A FAIL/HARD_FAIL on the headline is a RESULT and is reported as one, with the mechanism extracted:
it would mean the unbounded-lookback binary-agent pointer is, empirically, a better antecedent
ranker on this text than literal Centering Cb -- which would make our deviation an accidental
improvement worth understanding rather than a defect. No follow-up cell is authored in the same
breath; the negative is reported and the step stops.

## 9. COMPUTE ARCHITECTURE

Class **(b) sequential-CPU with justification**: pure symbolic replay over 36 short passages, wall
time seconds; no matmul, nothing GPU-batchable. numpy used only for the bootstrap. Storage
`no_storage`. Route: LOCAL foreground to completion.

## 10. SCHEMA-VET FIELDS

```yaml
cell_chunked: false                 # single unit, seconds, no seed axis
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: false            # exempt: wall time < 10s
defensive_error_checking: "passed_all_4_patterns (heartbeat exempt: <10s cell)"
cardinality_ok: true                # EXPECTED_N_UNITS = 2 corpora x (7 arms + discriminators)
arms_differ_verified: true          # D4, sha256 over each arm's pooled assignment
final_metrics_atomicity: "tmp_replace"
calibration_check: "default_ok_for_this_regime"   # CF_RANK is literature-fixed, not calibrated
baseline_in_band: true              # base_principle_b = 0.6923 deduped, inside (0.05, 0.95)
discriminator_reachability: true    # HARD_PASS 0.7423 < P_ceiling_ranking 1.0000 (Phase 1, measured)
crlb_n/a: "no estimator noise floor; the attainability bound is Phase 1's measured
           P_ceiling_ranking = 1.0000, and HARD_PASS at 0.6923+0.05 sits well inside it"
sweep_alignment_verdict: ALIGNED    # no sweep; one declared non-headline sensitivity variant
discriminating_fraction: n/a_no_sweep
composition_edges: []               # no primitive composition; one symbolic pick-key substitution
positive_control_arms:
  - arm: KEYED_HARNESS_REPRODUCES_RUN_PRINCIPLE_B
    primitive: hdlab.coreference_resolver.run_principle_b
    cited_prior_metric: 0.7191      # pooled/legacy view, same code, same corpus
    tolerance: 0.0                  # byte-identical assignment required
    if_outside_tolerance: HARNESS_DRIFT (cell invalid; arms not interpretable)
functional_requirements:
  - "prefer the previous utterance's centers over ancient ones" -> arm A (Cb window)
  - "rank non-subjects instead of discarding them" -> arm B (Cf grading)
  - "is the Cb tier doing anything beyond recency" -> ctrl_cb_off_pure_recency
  - "is any win discourse-structural" -> arm_C_scrambled
real_code_path_exercised: [run_principle_b, _principle_b_filter, _resolve_name_branch,
                           gn_compatible, mention_link_wrong, build_mention_stream, bcubed]
substrate_signature_checked: [run_principle_b, _principle_b_filter, _resolve_name_branch]
guard_baseline_validated: n/a_no_break_guard
deterministic_seeding: true         # bootstrap + scramble both fixed-integer seeded; no hash()
progress_logging: n/a               # timeout_s well under 1800
```
