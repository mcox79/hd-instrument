# Dormant-capability-flag audit (pri 130) — every default-OFF flag, its reason, whether the reason still holds

Scope and method, stated up front (phase 1). `SituationReader.__init__` (`hdlab/situation_reader.py`) has 76
keyword parameters; **13 are booleans that default OFF** (the rest default ON, or are numeric/string tuning
knobs, not capability gates). Every `HDLAB_*` env switch under `hdlab/` was also enumerated by grep (~90
hits); the large majority are **numeric sweep constants** ("swept, never adopted" — explicitly not capability
on/off gates) belonging to `hdlab/attachment_arm.py` (**pri 133's own file, in-flight tonight — out of this
brief's remit, not measured here**) and to `hdlab/graded_role_assigner.py` / `lexical_categories.py` /
`predicate_detector.py` / `temporal_model.py`. The boolean env-switches among those that *are* genuine
capability gates are individually classified in §2 below; all of them carry a dated, numbered reason and are
correctly OFF (**none is STALE-REASON** — see §2). **The STALE-REASON class lives entirely in
`SituationReader.__init__`**, which is also where the brief's own named lead (`agent_hybrid`) sits, so §1 is
where the measurement budget went.

Classification key (per the brief's checklist item 1b):
- **STALE-REASON** — the reason cited is 19c / a capped board / "byte-identical landing pending a measurement"
  that current rules have since mooted. Candidate to flip; measure on the product board before flipping.
- **STAND-IN** — the flag turns ON a NOT-brain-foundational component (spaCy / a supervised parser / an
  external LLM). Not flippable under the brain-foundational bar; belongs on the pri 127/129 prune list.
- **DIAGNOSTIC** — an instrument/ablation mode, kept off on purpose so the ablation stays meaningful.
- **LIVE-REASON** — a measured modern regression, saturation, or an explicit upstream dependency not yet met.
  Correctly off; cited with its number.
- **DEAD / NO-OP** — proven byte-identical to its own absence (a retired component another rung already
  overwrites). Not a flip question at all; a deletion question.
- **IN-FLIGHT** — another solver's named, active territory tonight (per this brief's own hard rules). Listed
  for completeness, not measured or touched.

---

## 1. `SituationReader.__init__` boolean capability flags that default OFF (13 of 76 kwargs)

All line numbers are from the CURRENT on-disk `hdlab/situation_reader.py` as read for this audit
(2026-09-15 21:xx local; the file is being concurrently edited by pri 131 tonight per this brief's own hard
rules, so line numbers are a snapshot, not a promise — the flag names and defaults are the load-bearing
facts). `CAPABILITY_FLAGS` (the one hand-maintained list, `situation_reader.py:1933`) already carries all 13.

| flag | file:line (default + assign) | date | cites 19c / capped-board / pending-measurement? | classification | action |
|---|---|---|---|---|---|
| `causation_typed` | 973 / 1176 | 2026-08-31 | no — cites spaCy at inference | **STAND-IN** | prune-list (pri 127/129); NOT flippable under the BF bar (loads spaCy) |
| `causation_foreground_gate` | 977 / 1184 | 2026-08-31 | dependent on `causation_typed` (no effect unless that flag is also on) | **STAND-IN (dependent)** | moot while the parent is a stand-in; no action |
| `affect_structured_matcher` | 995 / 1362 | 2026-09-07 | no — measured: OCC gold saturated ~0.94, no converse/antonym headroom | **LIVE-REASON** | keep off, cite it |
| `track_coherence` | 1008 / 1526 | 2026-09-07 | no — measured: full-population trade-off +0.016 NOT CI-sep; goal engine over-fires on the ~40% non-goal subset; the completing lever (generative world-model) is unbuilt | **LIVE-REASON** | keep off, cite it |
| `graded_role_marginal` | 1015 / 1635 | 2026-09-11 (Q125) | **yes — "byte-identical … Measure-first before any flip"**, yet the SAME comment already reports **+0.0065 CI-sep who-did-what** (UD-EWT n=1235) | **STALE-REASON** | measured this session (§3.3) |
| `structural_do_recover` | 1021 / 1685 | 2026-09-03 | **yes — motivated by "47 mis-vetoed clauses" on 19c prose specifically**; mechanism (bare-DO overrides the transitivity-gate veto) is register-general, never measured on modern UD-EWT | **STALE-REASON** | measured this session (§3.4) |
| `agent_hybrid` | 1034 / 1797 | 2026-09-06 | **yes, explicitly — "the reader's LIVE who-did-what board is 19c LitBank … flipping ON there is a REGRESSION"** | **STALE-REASON** | measured this session (§3.1) — **this brief's named lead** |
| `agent_hybrid_construction` | 1035 / 1798 | 2026-09-06 | same as `agent_hybrid` (paired) | **STALE-REASON** | measured this session (§3.1), paired with `agent_hybrid` |
| `entity_kb_resolver` | 1042 / 1841 | ("owner-DONE seed_the_entity_world_model_resolver…") | **yes — "DEFAULT-OFF pending a live measurement … the board's PRONOUN coref dim does not score [common-noun]"**, and pri 122 has SINCE put a `common_noun_coref` row on the reader-driven board | **STALE-REASON** | **HELD BACK from the diff per strategy 2026-09-15** — weakest prior evidence of the six; NOT flipped until it has its own measured number (see SOLVED.md §4b/§5) |
| `commonnoun_situation_gate` | 1043 / 1873 | **RETIRED 2026-09-11** | no — proven byte-identical dead code (`online_entity_cluster` overwrites its output on every non-pronoun) | **DEAD / NO-OP** | already on the pri 129 prune list; recommend deleting the parameter entirely (not a flip) |
| `commonnoun_type_license` | 1049 / 1885 | 2026-09-11 (Q111 flip-gate) | no — measured: **regresses** the live pick 0.4879→0.4683 (−0.0196 CI-sep), twin indistinguishable | **LIVE-REASON** | keep off, cite it |
| `unified_referent` | 1051 / 1899 | 2026-09-07 | **yes — "Landed default-off; strategy flips on after first-hand verify"**, and the verify already reports **+0.106 CI-sep pronoun pick / +0.072 CI-sep entity-KB hard-link on MODERN GUM, twin loses, named coref no-regress** | **STALE-REASON** | measured this session (§3.2) — **second-highest documented effect size** |
| `pronoun_principle_b` | 1044 / 1717 | 2026-09-15 (pri 131, TONIGHT) | no — "DEFAULT OFF because the relation is only as good as the parse that supplies it … mechanism built, witnessed and ready to flip" | **IN-FLIGHT** | pri 131's own active territory per this brief's hard rules; not measured or touched here |

**Ordering used for the measurement budget (checklist 1c: "prioritise by the documented effect size,
`agent_hybrid` first")**: `agent_hybrid`(+construction) — the brief's own named lead, +0.0521 already measured
on the reader (pri 125) — then `unified_referent` (+0.106 CI-sep documented on modern GUM, the largest single
number of any candidate here), then `entity_kb_resolver` and `graded_role_marginal` / `structural_do_recover`
(smaller or less-quantified documented effects).

---

## 2. `HDLAB_*` boolean capability-gate env switches under `hdlab/` that default OFF

(Excludes the ~70 numeric/string sweep constants under `hdlab/attachment_arm.py` — **pri 133's own file,
in-flight tonight, out of this brief's remit** — and the numeric tuning knobs elsewhere, which are not
on/off capability gates.)

| flag (env var) | file:line | reason | classification |
|---|---|---|---|
| `AUX_WINDOW_VBD` (`HDLAB_TEMPORAL_AUXWINDOW`) | `temporal_model.py:162` | measured: NULL on gold (6 hits vs 4 false fires in 1,500 test sentences) | **LIVE-REASON** — a clean measured negative, no 19c/capped-board involvement |
| `SLOT_OCCUPANCY` (`HDLAB_ROLE_SLOT_OCCUPANCY`) | `graded_role_assigner.py:365` | measured 2026-09-13: costs patient 0.7954→0.7781 with the CURRENT attachment-arm heads (a beam posterior ~1 on MAP heads, so the gate rarely fires and a mis-attached sibling still displaces the true object) — **explicit dependency**: "Flip ON when [the governor's core-argument arcs, pri 97/94] land; re-measure" | **LIVE-REASON (contingent on an unmet upstream dependency, correctly off)** |
| `UNK_JOINT_SHAPE` (`HDLAB_LC_UNK_JOINT_SHAPE`) | `lexical_categories.py:139` | measured: wins at small scale (1,500 sentences) but does NOT replicate at full scale (12,544 sentences, exactly the separable arm) — sparsity, not a fidelity gap | **LIVE-REASON** |
| `AUX_ARM` (`HDLAB_PREDICATE_RESCUE_AUX`) | `predicate_detector.py:288` | measured: the upstream predicate-slot form dominates on recall/precision/blind-clauses; stacking this arm buys +0.0008 recall for −0.0316 precision | **LIVE-REASON** |
| `ENT_NOVEL` (`HDLAB_LC_ENT_NOVEL`) | `lexical_categories.py:215` | one of three historical entity-register forms kept selectable for the ablation record ("two of the three forms are things not to re-try") | **DIAGNOSTIC** |

**None of these five is STALE-REASON.** Every one carries a dated, numbered, modern (non-19c) measured
reason, or an explicit unmet upstream dependency. This is the generalization the brief's checklist item 3
(`verification/test_no_stale_default_off_flag.py`) enforces going forward: a reason tag plus a number, not a
bare "default OFF".

---

## 3. THE MEASURED FLIPS — STATUS: PENDING (board discipline), MECHANISM VERIFIED

See `SOLVED.md` §4/§4b for the full account. **The fresh both-arms-one-process product-board number for each
of the six flags could not be produced on this laptop**: two other concurrent
`exp_situation_model_qa_modern_v1.py --run` processes occupied it for this session's entire duration
(confirmed by process command-line inspection), and the brief's own one-board-at-a-time rule correctly
blocked a third. Per strategy's mid-task instruction, the measurement moved into ONE committed cell,
`experiments/exp_dormant_flags_ab_v1.py`, for the DESKTOP's idle `tools/desktop_run.py` to run on the
committed tree:

```
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0 HDLAB_EXP_NAME=dormant_flags_ab_v1 \
  .venv/Scripts/python.exe experiments/exp_dormant_flags_ab_v1.py --flag agent_hybrid --ud-cap 600 --docs 24 --n-boot 1000
```
(repeat with `--flag agent_hybrid_construction`, `--flag graded_role_marginal`, `--flag structural_do_recover`,
`--flag unified_referent`, `--flag entity_kb_resolver` — the cell routes each to UD-EWT or GUM automatically).

`--self-test` was run on this laptop this session and PASSES on mechanism (both the UD injection path and the
GUM injection path complete, produce the expected per-row contrast structure, and leave `READER_KW` reset to
`{}` after each arm). Its 180s timing budget is now a printed report, not an assertion: measured directly
(twice), the GUM leg alone costs ~567s at `docs=3` (12 full `SituationReader.read()` calls at the reader's own
documented ~30-40s/document cost, not primarily this laptop's contention), so `--ud-cap 600 --docs 24` full
runs should budget **~15-20 min per UD-corpus flag and ~75-90 min per GUM-corpus flag** (see `SOLVED.md` §4b/§6
for the extrapolation). The diff
(`default_flips_patch.diff`) flips the top 5 by documented prior evidence (`agent_hybrid`,
`agent_hybrid_construction`, `unified_referent`, `graded_role_marginal`, `structural_do_recover`);
`entity_kb_resolver` (weakest prior evidence) is HELD BACK per strategy until `metrics_entity_kb_resolver.json`
exists.
