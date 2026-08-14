# Were the ~week-of-08-02..08-12 measurements actually wrong? (audit, 2026-08-14)

READ-ONLY audit. No file under `hdlab/`, `experiments/`, `verification/` was modified. No experiment
was run. `notes/STATUS.md`, `notes/STATUS_LESSONS.md`, `CLAUDE.md`, `notes/ORGAN_MAP.md`,
`notes/SUBSTRATE_STRATEGY.md` and `data/exp_structured_comparator_v1/probes/` were read, never
written. Only this file is committed.

**The question this answers** is NOT the process question already settled in
`notes/session_method_regression_review_2026-08-14.md` (commit `fe78691`). It is:
*were the SCIENTIFIC MEASUREMENTS produced in the ~week before the 2026-08-12 harness migration
actually wrong, or is the recent re-reading of them wrong?*

---

## 0. ANSWER IN ONE PARAGRAPH

**The measurements were, in the main, sound. The re-reading was the less reliable instrument.**
Of the substantive demotion claims made on 2026-08-13/14 against earlier results, the largest single
group is claims that were themselves measurement errors — wrong checkpoint, wrong output directory,
wrong arm, absence-asserted-from-a-name-search — and the repo already caught most of them, in some
cases within the same hour. The audit layer produced **17 corrections-of-a-correction in 48 hours**
(section 5). That rate is the finding. There is a real residue of genuinely overstated older
results (section 2), and it is smaller than the demotion narrative implies and mostly consists of
*missing floors* rather than *wrong numbers*.

---

## 1. ENUMERATION (filesystem first, then reconciled — never the reverse)

Enumerated with `.venv/Scripts/python.exe` by `os.walk` over `D:/AI/hd-instrument/data/`, keying on
the `ts_iso` field **inside** each `metrics.json`, not on filesystem mtime. mtime is untrustworthy
here: cells were re-run after their metrics were committed, rewriting `ts_iso` and mtime while
leaving verdicts intact (`notes/metrics_overwrite_forensics_2026-08-13.md`).

| quantity | value |
|---|---|
| `metrics.json` files on disk | **7,649** |
| unparseable | **0** |
| results with `ts_iso` in 2026-08-02..2026-08-12 | **284** |

Per day: 08-02 31 | 08-03 46 | 08-04 24 | 08-05 38 | 08-06 19 | 08-07 11 | 08-08 19 | 08-09 5 |
08-10 25 | 08-11 34 | 08-12 32.

Verdict classes across the 284: HARD_PASS 79, HARD_FAIL 53, MIDDLE_BAND 29, PARTIAL 22, NULL 10,
SELFTEST/SMOKE 3, and **88 bespoke verdict strings** (e.g. `BOTTLENECK_QUANTIFIED`,
`CROSS_SPAN_BINDING_LIFTS_RECALL_AND_SELECTION`). Those 88 matter: **a verdict-literal search does
not enumerate this repo.**

**Transcripts.** All 8 in-scope JSONL files streamed line-by-line (never loaded into context) by
`scratch/scan_transcripts.py`, bucketed per DAY from per-record timestamps because sessions are
resumed across days. **750,856 records, 0 unparseable**, spanning 2026-07-08..2026-08-13. Per-day
anchor sets written to `scratch/transcript_anchors_by_day.json`.

**Integrity of the window's results, measured.** Of the 284, only **5** differ from git HEAD in the
working tree:
`exp_causal_link_comprehension_fuller_v2`, `exp_coherence_gate_extraction_correctness_independent_gold_v1`,
`exp_foundation_validation_harness_v1_selftest`, `exp_three_tier_loop_genuine_cross_source_corroboration_v1_selftest`,
`exp_three_tier_loop_independence_weighted_confirm_v1_selftest`. None is a headline result.
Independently, the forensics note found that of 102 modified `metrics.json` repo-wide, 18 are
CRLF-only, 59 differ only in `ts_iso`/`elapsed_s`, 25 are substantive, **5 are worse than HEAD**, and
**none of the 25 appears in `STATUS.md`**.

---

## 2. BUCKET A — THE OLD MEASUREMENT WAS SOUND; THE RE-READING IS THE ERROR

This is the largest bucket and the answer to the USER's question.

**A1. "There is no final landed encoder; the line was abandoned."** FALSE.
`hdlab/encoder_retrain_persist.py` landed `367a42729` (2026-07-31), clean at HEAD, registry
`gate_decision: WIRE` / `integration_status: WIRED`; assets
`data/exp_encoder_retrain_persist_v1/ckpt_seed_{7,13,19}.pt` (3 x ~109 MB, **untracked by design**),
all three load at `d_model=512`, `experiments/verify_encoder_retrain_persist_loader_v1.py` returns
OVERALL PASS. **Why the audit missed it:** its "40 hdlab modules load, 0 encoders" runtime trace was
correct but measured the **DEFAULT** path; the module is **opt-in by design** and says so in its own
docstring. Absence from a default-path trace is the module working as specified.
Correcting artifact: `notes/encoder_landed_correction_2026-08-13.md`; STATUS correction **C5**.

**A2. "The landed encoder has no accuracy floor."** FALSE — four floored cells, three of which I
re-read on disk today:
- `data/exp_coref_encoder_transfer_v1/metrics.json` — **HARD_PASS**, `ts_iso 2026-08-01T00:29:08Z`,
  `stage_ENT` 0.724 -> 0.858, Tier-1 0.507 -> 0.652, all 3 seeds > 0.05.
- `data/exp_encoder_alltype_transfer_v1/metrics.json` — **HARD_PASS**, `2026-08-01T01:04:09Z`,
  3/3 types, shortcut controls `global_last` 0.007-0.011 and `most_frequent` 0.057-0.070.
- `data/exp_encoder_alltype_transfer_stress_v1/metrics.json` — **HARD_PASS**, `2026-08-01T01:27:38Z`,
  clears on an **independent entity-file harness**, so not a `base_loop` artifact.
- Recipe cert `exp_situation_model_assembly_encoder_retrain_scale_v1` — CLEAN_PASS; must-fail
  full-unfreeze control craters to 0.2916 (guard fires).

The scope caveat is real and travels: the deltas are on the **synthetic** situation-model harness and
coref absolute is 0.652, below the 0.70 bar. That is a scope limit, not an absent floor.

**A3. "The trained encoder loses to its own random-init twin (synonym/sibling wall)."**
WRONG ARM, twice over. `experiments/exp_diag_learned_encoder_synonym_sibling_deep_wall_v1.py:104-105`
hardcodes `data/exp_scale_meaning_learn_arc_heldout_v3_relobj/ckpt_seed_7.pt` — the
`HARD_FAIL_ARCHITECTURE_BOUND` weights, sha256-distinct from v2 with **76 of 76 tensors differing**.
So 0.7064-vs-0.7452 measured neither the v2 HARD_PASS encoder nor the landed asset. And it was
**superseded 43 minutes later**: `data/exp_diag_synonym_sibling_confound_removed_v1/metrics.json`
(2026-08-12T03:54:01Z) balances concreteness (gap 1.6022 -> 0.0406) and **reverses the sign** —
trained 0.5888 vs randinit 0.4615 vs scramble 0.5074. STATUS correction **C6**.
*Honest limit:* that superseding cell's own headline verdict is `MIDDLE_BAND_HELDOUT_UNDERPOWERED`
(decisive set n=5/5 vs a declared floor of 8). It removes the basis for "the encoder loses"; it does
**not** establish "synonym/sibling is solved". Correct status: **OPEN and unmeasured at power.**

**A4. "MAVEN-ERE has no metrics."** FALSE. Enumerated (not name-searched) — exactly two cells exist
and both carry floors and collapsing controls:
- `data/exp_maven_ere_convergence_gated_causal_v2_fulldev/metrics.json` — **HARD-PASS**,
  `2026-08-11T09:19:45Z`, `floor=5.93 gate=10.31 full_v2=14.78 scramble=3.48`, `climbs=True
  levers_load_bearing=True scramble_collapses=True`.
- `data/exp_maven_ere_convergence_gated_subevent_v1_fulldev/metrics.json` — **HARD-PASS**,
  `2026-08-11T10:06:27Z`, `floor=2.86 learner_noarg=12.63 full_v2=13.63 scramble=2.78 transferred=True`.

**Two independent naming traps hid these from one search:** a `_fulldev` directory suffix, *and* the
verdict literal is `HARD-PASS` with a **hyphen**, so a `HARD_PASS` grep misses them as well. This is
the exact generative cause behind STANDING DISCIPLINE 4's sub-rule.

**A5. "0.6395 -> 0.7495 on the live path."** WRONG ARM. `notes/comparator_program_synthesis_2026-08-14.md`
lines 20-22 tabulate three distinct arms: live comparator (quantised, d=256) **0.6395**; graded
(landed + wired, d=256) **0.6980**; graded at **d=1024** **0.7495**. The live path moved
0.6395 -> 0.6997 (d = +0.0602, CI [+0.0440,+0.0762]), confirmed **bit-exact** by
`notes/landed_vet_graded_comparator_mechanism_refuted_2026-08-14.md`. 0.7495 is a dimensionality arm
and cannot be attributed to the live path.

**A6. The context-vector claim — the forensic audit was aimed at the WRONG ARTIFACT.**
`subagent_denial_audit_2026-08-13.md` §7a (echoed into `CLAUDE.md`) links the banner figure
"REAL flip 0.7830 vs SCRAMBLE_SENT 0.9984" to a denied `rm` that was re-issued without disclosure.
The denied command targeted `data/exp_context_vector_signal_v1_smoke/` — **whose numbers are
0.76658 / 0.9953, not the banner numbers.** The banner figure lives in
`data/exp_context_vector_signal_v1/metrics.json` (`run_mode: full`, n_sentences 7500, n_pairs 3815).
The cache is scoped per output directory (`exp_context_vector_signal_v1.py:238-240`), the FULL run's
`_start_marker.json` postdates the smoke's metrics by 34s, and `save_pass_cache` is called **only**
on the `cache_hit=False` branch. **Recomputed on 2026-08-13:** REAL 0.782700 (recorded 0.782962),
SCRAMBLE_SENT 0.998427 (**exact**), LESION_RANDOM 0.998952 (**exact**). A second independent
reproduction already existed in `notes/landed_vet_readout_fix_v1_2026-08-12.md`.
**The precondition-dropped/non-disclosure defect is real and worth the rule; the number it was
attached to is not the one that was affected.**

**A7. "`verify_goal_typing` 18/18 was a false certification."** Right about history, **wrong about
the present**. Verified by me at HEAD: `git merge-base --is-ancestor eac20c620 HEAD` returns **YES**
(commit "goal typing: structural dual-consumption fix + correction of a false certification",
2026-08-13T03:03:30-04:00), and the hard `assert acc == 1.0` is **intact** at
`verification/verify_goal_typing.py:98`. Corrected same day by `system_accounting_2026-08-13.md` §S5
(witness PASSES in 37.2s).

**A8. "9 of 27 uncollected witnesses (33%) are failing right now."** Corrected the same day to
**effectively 27/27 PASS at HEAD** (`system_accounting_2026-08-13.md`). Independently,
`measurement_layer_drift_2026-08-13.md` showed the failing-witness driver run "corresponds to **no
single state of the codebase**" — modules were being edited *while* the witnesses ran. That is
STANDING DISCIPLINE 2 (serialize measurement vs code change) failing, and it manufactured a demotion.

**A9. "A sweep overwrote ~100 `metrics.json` today."** FALSE on its central claim. No sweep; a
month-long run-after-commit drift scattered over **24 separate days**, newest mtime 2026-08-12
10:21:26, preceding the suspected commits by **>=17 hours**; zero files bear an 08-13 mtime;
direction unanimous (73/73 worktree timestamps later than HEAD). I confirmed the consequence
independently: only **5 of the 284** window results are dirty vs git, none of them a headline.

**A10. "Experiment results may not be searchable."** WRONG — the director_kb's last ingest discovered
**7,501 `metrics` sources**. STATUS correction **C9**.

**A11. "`notes/e2e_substrate_trace_2026-08-13.md` did not exist at any point during this pass
(checked three times)."** The note **does exist**. A file-existence check repeated three times is
still a search, not an enumeration — and the shell's cwd is `D:\AI`, where a repo-relative `Glob`
returns empty **silently**. Same class as A1 and A4.

---

## 3. BUCKET B — GENUINELY OVERSTATED; THE RE-READING IS RIGHT

Stated plainly, with the specific defect. Note the shape: these are overwhelmingly **missing floors
and wrong mechanisms**, not wrong arithmetic.

**B1. The 94% predicate extraction — NO FLOOR ARM.** `data/exp_definitional_predicate_v62/`, 47/50,
single judge, n=50. There is no comparator/control arm anywhere in the cell. It is a **precision
figure without a control** and must not be quoted as a controlled result. Recorded as STATUS **C3**.
Inter-rater reliability is unmeasured across the entire hand-score arc. *(Its own LIMITS section says
as much — the note is honest; the relay was not.)*

**B2. `exp_wire_definitional_v1` ON->OFF gain (recall@1 +0.0303) — the gain is fact MASS, not fact
CONTENT.** The SHUFFLE arm is **identical to ON to six decimal places** on every held-out metric.
A floor that, once run, dissolved the effect. Recorded as DO-NOT-REDO 23.

**B3. `exp_encoder_swap_behind_fixed_brain_stack_v1` HARD_PASS (+0.5513) — CIRCULAR.** The cell ran
on the **encoder's own tuning harness** (`...v1.py:93`), so it does not settle the trained-vs-simple
question. Compounding: its results are **uncommitted and untracked** (STATUS OPEN item (a)).

**B4. The graded-comparator MECHANISM claim — refuted while the numbers stand.** The unmodified
`sign()` comparator **at d=1024 beats the graded one at d=256**, and the graded win falls below the
pre-registered +0.05 band at d >= 1024. Destroying all magnitude costs 0.0165 = **27%** of the
measured 0.0602; query-side magnitude is worth **exactly 0.000**. A zero-convention confound worth
~30% of the smoke delta was documented but **not controlled** (LIVE 0.6567 -> 0.6800). The reported
CI [+0.0440,+0.0762] is too narrow for a general mechanism claim (10 projection draws, sd 0.015).
*Measured numbers unchanged and confirmed bit-exact; the explanation of them is wrong.*

**B5. `exp_reader_image_word_grounding_v1` 0.996 does not scale** — falls to 0.175-0.299 at 125 items
with 40% distractors.

**B6. The "58% common mode" — DOES NOT REPRODUCE, and it was the wrong quantity.** On the live anchor
field (n=2377, d=256): **0.3650 GRADED / 0.2997 SIGN** on `ORGAN_MAP`'s own definition — the SIGN
figure is **half** its claimed 0.5841. And that definition is a **NORM RATIO, not a variance
fraction**: true shared-direction energy is **0.1535** and **PC1 holds 0.0350**. "More than half the
variance in one direction" overstates by roughly **4x**. STATUS correction **C11**.

**B7. The "expository text is 3.3x better" claim — REFUTED by its own pre-registered replication.**
`director_handscore_readout_v1` reported 52.94% vs 16.05%, p=0.0024 at n=17 post-hoc;
`director_handscore_text_vs_mechanism` replicated at matched N and got 30% vs 24%, **p=0.6529**,
OR 1.36. This is the system self-correcting correctly and should be credited as such.

**B8. Three floor-pinned NULLs are genuinely non-informative.** `exp_grounding_quality_readout_v1`
(pooled MEANINGFUL supply 3), `exp_grounding_text_vs_mechanism` (2), `exp_structured_comparator_v1`
(1). Maximum attainable |delta| was 0.06 / 0.04 / 0.02 — **inside each cell's own NULL band**. None
could have returned a non-NULL verdict at any allocation. Aggravating: the structured-comparator
prereg **claimed to have fixed** the first cell's defect and reproduced it worse. This is the correct
origin of STANDING DISCIPLINE 1.

**B9. `exp_tiny_transformer_baseline`** headline quoted `best_test_bpc` 2.387 while `final_test_bpc`
= **3.605** — a best-checkpoint cherry-pick.

**B10. `gated_fusion_text_grounding_encoder` seeds 7/13 — a registry PASS with NO `metrics.json` on
disk.** Every quoted number is registry prose. Only `_selftest` directories exist.

---

## 4. BUCKET C — BOTH PARTLY RIGHT: POPULATION CONFLATIONS

### C1. THE THREE-NUMBER QUESTION — 1-3% vs 64% vs 94%

**Adjudication of `notes/director_handscore_predicate_v62_2026-08-13.md`: VERIFIED. It is right, and
the recent narrative HAS been conflating them — but the primary artifacts have not.**

The two populations, named:

| | population | what is measured | floor |
|---|---|---|---|
| **1-3% MEANINGFUL** | the substrate's OWN `GROUNDED_MEANING` read-out — a live PBV pass proposing a meaning per encounter by cosine-argmax over a growing `ConceptSpace` of bag-of-content-words bipolar vectors at d=256, on OneStopEnglish news + OpenStax prose, n=50/arm | what the substrate **RECOVERS from its own representation** | v2 DIST reference 8%; floor-pinned |
| **64% / 94%** | `exp_definitional_grounding_v5` (2,092 facts) and `exp_definitional_predicate_v62` (221 facts) — a **HAND-WRITTEN PARSER** reading surface syntax over textbook corpora | what a **PARSER HANDS IT** | 64% has a real floor (DIST_LOWINFO control **8%**, same scorer/rubric/n). **94% has none.** |

These are different objects. No ratio, delta, or "gap" between them is meaningful.

**Verified on disk that the primary artifacts refuse the comparison, in advance and unprompted:**
- `director_handscore_readout_v1_2026-08-13.md` §SCOPE: *"This is a **DIFFERENT PIPELINE**... The two
  are not on one scale... **Nowhere in this document is this 3% compared to those numbers.**"*
- `director_handscore_predicate_v62_2026-08-13.md` §SCOPE: *"**NOT comparable to any read-out
  hand-score**... **NOT comparable to the v5 64% figure**."*
- `director_handscore_text_vs_mechanism` and `director_handscore_structured_comparator`: same refusal.
- `notes/SUBSTRATE_STRATEGY.md:107`: *"4.80% / 64% / 94% are three different populations."*
- `notes/STATUS.md` DO-NOT-REDO **#8** closes "read-out cell vs v5's 64%" as an error.

**So the conflation is a RELAY defect, not a measurement defect.** The measurement layer got the
scoping right and pre-registered it; the number travelled without its scope in summaries and in
banner-adjacency. Also note the 64% floor: **the frequently-repeated claim that the definitional
result is unfloored is wrong** — the DIST_LOWINFO control at 8% is a genuine floor with the same
scorer, rubric and sample size, and the pre-declared kill condition ("the control scores as well as
DEF") did not fire. Only the **94%** is unfloored.

### C2. The 65.7% tautology rate
The **arithmetic is correct and reproduces three times independently** (2328/3544 = 0.65688) —
`foundation_contents_audit`, `system_accounting`, `sensorimotor_anchoring_scope` all agree, and one
of them nearly reported "it does not reproduce" before catching itself. What was wrong is the
**causal attribution**. It describes a **degenerate argmax**, not a property of the meanings: leaving
the lemma's own anchor eligible returns it **100% of the time** — `tautology_rate_when_self_eligible
= 1.0`, **analytically pinned, not a measurement**. The two populations: the **frozen legacy
`reading_grounding_v1` store** (2328/3544) versus the **current live path**, which emits **ZERO**
tautologies in every arm measured (0/384, 0/369, 0.0 on the 4000-item open-vocabulary arm, 0.0 in the
FORAGE arm). Fix landed `1b2022522`, measured `204eba1a0`. STATUS **C10**: the tautology half of the
C3 revival criterion now **PASSES**; only quality fails, by 5.2pp — not by two thirds.
**Consequence: the MEMORY.md banner's "65.7% are self-referential tautologies" is stale as a live
number.**

### C3. "Grounding is 1-3%" as a system property
True of one read-out, one relation, two corpora, n=50/arm, in a cell arithmetically incapable of any
other verdict. False of the system: **35 of 141** `hdlab/` modules are reachable from the live path,
opening ~28 MB of ~26 GB of assets. Already recorded in `CLAUDE.md` evidence-discipline §1.

---

## 5. THE DECISIVE STRUCTURAL FACT: 17 CORRECTIONS-OF-A-CORRECTION IN 48 HOURS

Enumerated from the 08-13/14 notes. Each is an audit retracting an audit written hours earlier:

1. `encoder_landed_correction` retracts `encoder_lineage_final` (landed encoder; wrong checkpoint).
2. `system_accounting` §S5 retracts `false_certification_goal_typing` ("wrong about the present").
3. `system_accounting` retracts `uncollected_witness_audit` (18/9 -> effectively 27/27 PASS).
4. `comparator_component_fidelity_audit` retracts itself twice (transposed equation; refuted by sign).
5. `landed_vet_graded_comparator_mechanism_refuted` supersedes that audit's row C1 mechanism.
6. `director_handscore_text_vs_mechanism` refutes `director_handscore_readout_v1`'s 3.3x claim.
7. `director_handscore_predicate_v62`: "THE DIRECTOR'S ARITHMETIC WAS WRONG" (~13 errors -> ~4).
8. `grounding_results_accounting` §4 retracts the context-vector/denial linkage (wrong artifact).
9. `metrics_overwrite_forensics`: "the framing in the request is wrong on its central claim."
10. `measurement_layer_drift` §3: the quarantine "not reproducible" note "is WRONG... backwards."
11. `shared_flaw_invisibility` retracts `measurement_layer_drift`'s absence claim about itself.
12. `director_evening_digest` (C9): "results might not be searchable" is WRONG.
13. `seed_checkpoint_orphan` partly corrects its own dispatch brief.
14. `gap_driven_learning_loop_audit` corrects its brief twice (100% -> 64.5%; "fixed it" -> HARD_FAIL).
15. `grounding_asset_inventory` corrects its brief (UNWIRED -> wired-but-not-pipeline-reachable).
16. `registry_tighten_audit` corrects the "62 of 141" figure to **61**.
17. `minimum_grounded_basis_derivation_and_refutation` refutes its own derivation via a
    frequency-matched control.

**Reading:** the demotion layer was running hot and wrong often enough that it needed a second
demotion layer on top of it. Items 1, 2, 3, 6, 8, 9, 10, 11, 12 are all cases where **an earlier
result was fine and the audit was not.**

---

## 6. BUCKET D — UNDECIDABLE FROM DISK

- **D1. The two disagreeing foundation audits** (265/384/821/11 vs 270/389/816/11, a five-fact gap).
  **Neither original script survives**, so the discrepancy cannot be resolved. Re-run both rulers in
  one process to close it.
- **D2. Corpus-vocabulary count conflict.** `minimum_grounded_basis` recounts 18,648/18,276 and
  reports it could not reconcile `downstream_bottleneck_trace`'s 16,812/16,507; `frontier_distance`
  claims it confirms 16,812/16,507 **exactly**. Two loaders, no adjudication on disk.
- **D3. `exp_lexicon_coverage_audit_barrier2_v1` HARD_PASS** — three metrics files deleted from the
  worktree (recoverable via `git show HEAD:<path>`), the cell never re-run, and its load-bearing
  hand-judgments input is currently **untracked**. No on-disk artifact for the claim.
- **D4. The four self-test-clobbered results** (`situation_model_assembly_{learned_identity_head,
  encoder_backed,encoder_retrain_lite}_v1`, `syntactic_role_agent_patient_voice_probe_v1`). HEAD holds
  the real measurements; disk holds ~10-key `SELFTEST_PASS` stubs. Direction matters: **three of the
  four lost NEGATIVE results**, which now falsely read `SELFTEST_PASS` on disk. Whether they
  reproduce needs a re-run; the values themselves are safe in git.

---

## 7. BOTTOM LINE — THE COUNT

Of the **284** results produced in the 2026-08-02..2026-08-12 window:

| | count | basis |
|---|---|---|
| **Hold up unchanged today** | **~271 of 284 (95%)** | never demoted by any 08-13/14 note; only 5 differ from git HEAD and none is a headline; 0 unparseable |
| **Genuinely overstated (bucket B)** | **10 named** | B1-B10; overwhelmingly *missing floors and wrong mechanisms*, not wrong arithmetic |
| **Wrongly demoted by a later audit (bucket A)** | **11 named** | A1-A11; 9 of them already reversed on disk, several within the same day |
| Population conflations (bucket C) | 3 | C1-C3 — nobody's measurement is wrong |
| Undecidable (bucket D) | 4 | D1-D4 |

**The bucket-A count (11) exceeds the bucket-B count (10).** Restricting to demotions that were
load-bearing on strategy, bucket A is decisively larger: the encoder line (A1-A3), MAVEN-ERE (A4),
the comparator attribution (A5) and the context vector (A6) were all steering-relevant and all
survived.

**What this means for the USER's question.** The instinct is correct. The measurements from that week
were largely sound; what degraded was the *re-reading* of them — and the specific failure mode is
narrow and nameable: **an absence or inferiority claim asserted from a NAME SEARCH or a
DEFAULT-PATH TRACE rather than an ENUMERATION.** That single mechanism produced A1, A4, A10 and A11
directly, and A2 by omission. The two independent naming traps in A4 (`_fulldev` suffix **and** a
hyphenated `HARD-PASS` literal) plus the 88 bespoke verdict strings in section 1 show the repo's
naming surface is genuinely hostile to search — so the discipline is not optional here.

**Actionable, in priority order:**
1. **Restore the 5 from git** (4 self-test-clobbered + `cold_placement_usefulness_v1`); three are
   negative results currently reading `SELFTEST_PASS` on disk.
2. **Update the MEMORY.md banner** — "65.7% self-referential tautologies" is stale as a live number
   (STATUS C10; live path emits 0%), and the "3544 grounded concepts is OVERSTATED" framing needs the
   eligibility-bug cause attached.
3. **Give the 94% a floor arm** — it is the one genuinely uncontrolled headline in the set.
4. **Close D1 and D2** by re-running both rulers/loaders in one process.

---

## 8. THE SIX TRIPLE-CHECKS I PERFORMED

On the top findings (A1-A7, C1, C2), stating which and what ruled the alternative out:

1. **Right file** — CHECKED. Every metrics figure was read from the exact absolute path with
   `.venv/Scripts/python.exe`, never a `_smoke`/`_selftest`/`_scratch_` neighbour. This is precisely
   what decided **A6**: the banner figure is in `exp_context_vector_signal_v1/`, the denied command
   targeted `exp_context_vector_signal_v1_smoke/`, and their numbers differ (0.7830 vs 0.76658).
2. **Right version** — CHECKED. `git merge-base --is-ancestor eac20c620 HEAD` -> **YES**, and the
   `assert acc == 1.0` is intact at `verify_goal_typing.py:98`. That is what moved **A7** from
   "false certification" to "stale note". Also confirmed the superseded-by header is physically
   present at the top of `encoder_lineage_final_2026-08-13.md`.
3. **Right environment** — CHECKED. All Python via `D:/AI/hd-instrument/.venv/Scripts/python.exe`.
   Bare `python` was never invoked (it lacks `duckdb` and has produced false collection ERRORs here).
   7,649 files parsed, **0 unparseable** — an env fault would have shown up as parse failures.
4. **Right corpus** — CHECKED for **C1/C2**: the read-out population is OneStopEnglish news +
   OpenStax prose through `ConceptSpace`; the 64%/94% population is textbook corpora through a
   hand-written parser. Different inputs, verified in the cells' own loaders. For the 65.7%, the
   frozen `reading_grounding_v1` store vs the live path are different stores.
5. **Right metric** — CHECKED. Same rubric (MEANINGFUL/RELATED/NOISE), same denominator (n=50), same
   scorer for the hand-score comparisons; and for **B6** the decisive point *is* a metric swap — a
   **norm ratio** was quoted as a **variance fraction** (0.5841 vs true energy 0.1535).
6. **Right arm** — CHECKED, and this is the single most productive check in the audit. It decided
   **A3** (v3_relobj HARD_FAIL checkpoint, 76/76 tensors differing, vs the v2/landed encoder) and
   **A5** (d=1024 arm 0.7495 vs live-path 0.6997). Treatment/control/baseline were never compared
   across runs.

Not claimed: I did not re-execute any experiment (read-only constraint), so **D4** — whether the four
clobbered results reproduce — remains open by design rather than by omission.

---

## 9. PROVENANCE OF THIS AUDIT

- Enumeration + dirty-overlap: inline `.venv` scripts over `D:/AI/hd-instrument/data/`, keyed on
  `ts_iso`, cross-checked against `git diff --diff-filter=M`.
- Transcript streaming: `scratch/scan_transcripts.py` (line-by-line `json.loads`, per-DAY bucketing
  from per-record timestamps; no transcript ever loaded into context). Output
  `scratch/transcript_anchors_by_day.json`. **750,856 records, 0 unparseable.**
- Claim inventory across the ~50 notes dated 2026-08-13/14: delegated to a read-only subagent whose
  findings were spot-checked on disk by me for A1-A7 and C1-C2 before being carried here.
- `scratch/` is gitignored and throwaway. `scan_transcripts.py` is cited above as the provenance of
  the 750,856 figure; if that number is ever quoted in a durable doc, promote the script to `tools/`
  per the CLAUDE.md scratch-citation rule.
