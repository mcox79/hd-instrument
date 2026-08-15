# The graded path does NOT clear the orthographic floor, and +0.0602 was never a C3 number

**Filed:** 2026-08-14 (late). **Author:** auditor (AUDIT-ONLY -- no cell authored, nothing wired,
no live-path change, no experiment run; every number below re-derived off `metrics.json` with
`.venv/Scripts/python.exe`).
**Cell:** `data/exp_graded_path_vs_orthographic_floor_v1/metrics.json`, run `2026-08-15T00:45:53Z`,
`run_mode=full`, `elapsed_s=344.33`.
**Prereg:** `preregs/2026-08-14_exp_graded_path_vs_orthographic_floor_v1.md`.
**Branch** `dataprep/mcguffey-graded-corpus`, HEAD `d596bbcbc` at filing.

---

## 1. VERDICT, and the numbers that carry it (all verified off disk, not transcribed)

`verdict = DOES_NOT_CLEAR_ORTHOGRAPHIC_FLOOR`;
`on_clears_floor=false  off_clears_floor=false  graded_helps=false  graded_hurts=false`.

n_items = 4000, n_anchors = 5491, bootstrap n_boot = 5000 seed 20260819. Open-vocabulary hit@1.

| arm | hit@1 | 95% CI | median rank | gold in top-50 |
|---|---|---|---|---|
| `A1_GRADED_ON` (graded switch ON = the LIVE default) | **0.04800** | [0.04125, 0.05475] | **37.0** | 0.5565 |
| `A9_GRADED_OFF` (the NOVEL arm) | **0.04650** | [0.04000, 0.05350] | 45.0 | 0.5225 |
| `A5_STRINGCTRL` (spelling) | **0.08700** | [0.07825, 0.09600] | 37.0 | 0.5455 |
| `A7_PREFIX_ONLY` | 0.05875 | [0.05150, 0.06600] | 33.5 | 0.57675 |
| `F_FREQUENCY` | 0.01850 | [0.01450, 0.02275] | -- | -- |
| `F_SCRAMBLE_ON` / `F_SCRAMBLE_OFF` | 0.01375 | [0.01050, 0.01725] | -- | -- |

Deltas, verbatim from `bootstrap.deltas`:

- **ON minus OFF = +0.00150, CI [-0.00550, +0.00825], `ci_excludes_zero = false`.** NULL.
- **ON minus SPELLING = -0.03900, CI [-0.05000, -0.02825], `ci_excludes_zero = true`.** We lose.
- OFF minus SPELLING = -0.04050, CI [-0.05125, -0.02975], excludes zero. We lose either way.
- ON minus PREFIX_ONLY = -0.01075, CI [-0.02050, -0.00050], excludes zero. Prefix beats us too.
- ON minus FREQUENCY = +0.02950, excludes zero. ON minus SCRAMBLE = +0.03425, excludes zero.

**The Director's transcription reproduces exactly.** Every value checked; no correction needed to
any of them. **The ON arm's `median_rank`, which the brief asked for, is 37.0** -- see section 3.

**Instrument checks that PASS, so the null is not a broken harness:**
`a1_graded_on_reproduces_c3_headline_0480_exactly = true` (positive control: the ON arm reproduces
the 0.0480 C3 headline exactly, so this is the same harness that produced the live number);
`self_retrieval` ON 0.7860 / OFF 0.7358 against a declared floor of 0.700, both `ok=true`;
`tautology_rate = 0.0000` on every scored arm.

**One integrity flag, reported rather than buried:** `arms_must_differ.ok = false`. The collision is
`F_SCRAMBLE_ON` == `F_SCRAMBLE_OFF`, digest `4596b30dc13e9692`. Since the digest is
`sha256(hits.astype(int8))` (`experiments/exp_graded_path_vs_orthographic_floor_v1.py:102`), the two
scramble arms produced a **bit-identical per-item hit vector** -- identical rate AND identical items.
The four substantive arms (`A1`, `A9`, `A5`, `A7`) all have distinct digests, so the primary contrast
is unaffected. The collision is itself informative and is used in section 4.

---

## 2. WHERE +0.0602 ACTUALLY CAME FROM -- a DIFFERENT METRIC, read across as if it were this one

**Yes. It was a different metric, misread as this one. That is the finding.**

`notes/brain_drill_how_meaning_is_stored_and_separated_2026-08-14.md` section 8 names the
signed-vs-graded distinction **"THE SINGLE LARGEST FIDELITY GAP"** and justifies it as *"the only
intervention in its family with a floored positive (**+0.0602 CI [0.0440,0.0762]** against scrambled
0.4975 and frequency 0.4800)"*. Traced to source:

**`data/exp_graded_divisive_comparator_v1/metrics.json`** (HARD_PASS, `38f7a0d5c`), verdict string
verbatim:

> `n=4000 | LIVE(A_SSN)=0.6395 PRIMARY(A_GGZ)=0.6997 | d=0.0602 CI=[0.0440,0.0762] | floors:`
> `SCRAM_PRIMARY=0.5065 SCRAM_LIVE=0.4975 FREQ=0.4800 CHANCE=0.50`

The two cells do not measure the same thing:

| | `exp_graded_divisive_comparator_v1` (source of +0.0602) | `exp_graded_path_vs_orthographic_floor_v1` (tonight) |
|---|---|---|
| task | **near-neighbour 2AFC** -- choose between TWO supplied candidates | **open-vocabulary hit@1** -- argmax over the whole codebook |
| `chance` | **0.50** (stated in the cell: `chance = 0.5`) | ~1/5491 = 0.00018 |
| anchor pool | **2,377** | **5,491** |
| operating point | 0.6395 -> 0.6997 | 0.0465 -> 0.0480 |
| graded contrast | **+0.0602, CI excludes zero** | **+0.0015, CI INCLUDES zero** |

**The same manipulation, in the same direction, on the same substrate -- and the effect does not
transfer.** A +0.0602 lift on a 2AFC scorer whose chance is 0.50 is not evidence of anything about
a 5,491-way open-vocabulary argmax, and it must never again be quoted as a C3 number. The drill note
compounded the error: it also cited **0.6395 -> 0.6980** (section 8 / STATUS.md "OTHER PATH STATE")
as if those were read-out numbers. They are 2AFC accuracies.

**Note what this does and does not touch.** `exp_graded_divisive_comparator_v1` is **not**
invalidated. Its HARD_PASS stands **on its own scorer**, with its own floors (SCRAM 0.5065/0.4975,
FREQ 0.4800) which it clears. What is refuted is the **carry-across**: the inference that a floored
gain on the 2AFC comparator licenses a claim about the C3 open-vocab read-out. That inference is
now measured and it is false.

**This is the third distinct defect in the same claim in one day**, which is the part worth keeping:
(i) the drill note said the graded path was default-OFF (it was default-ON -- corrected in the
banner at `d596bbcbc`); (ii) the banner then said the +0.0602 was *"already banked"* on the 0.0480
headline; that is also wrong -- **it was never in that currency at all**; (iii) the remaining
question the banner left open ("is the persisted anchor field graded?") is now answered by
measurement: turning the whole path off moves C3 hit@1 by +0.0015, null.

---

## 3. WHAT SURVIVES, STATED AS HARD AS THE NEGATIVE (symmetric anti-negativity)

Two things in this cell cut AGAINST the null. Neither rescues the claim; both are on the record.

**(a) The graded switch DOES improve RANKING, just not the top-1 decision.**
`median_rank` 45.0 (OFF) -> **37.0 (ON)**; `frac_gold_in_top50` 0.5225 -> 0.5565. Both move the
right way and neither is a rounding artifact. **Caveat that must travel: the cell computes NO
confidence interval on either statistic**, so this is an uncontrolled observation, not a result.
Note also that ON's `median_rank` of 37.0 exactly equals spelling's 37.0 -- the same coincidence
`exp_orthographic_floor_vet_v1` produced, and the same reading applies: **we rank the right
neighbourhood as well as spelling does and then pick the wrong member of it.** The defect is
WITHIN-NEIGHBOURHOOD SEPARATION, and this cell is further evidence for that, not against it.

**(b) The projection-draw ensemble disagrees with the canonical projection, and this is the
strongest available objection to the null.** Recomputed independently from `projdraw`:

- ON draws [0.05150, 0.05250, 0.05025], mean **0.051417**, sd 0.000920 (reported sd reproduces).
- OFF draws [0.03975, 0.04150, 0.04550], mean **0.042250**, sd 0.002407 (reproduces).
- **Draw-mean delta = +0.009167**, se 0.001822, t = 5.03 on ~2.6 df -- **6x the canonical +0.0015.**
- **The canonical projection is simultaneously the WORST of four samples for ON (0.0480 < all three
  ON redraws) and the BEST of four for OFF (0.0465 > all three OFF redraws).**

That coincidence is worth stating plainly rather than explaining away. **It does not change the
verdict, for a reason that is arithmetic and not rhetorical:** even taking the draw-ensemble
estimate at face value, graded-ON sits at ~0.0514 against spelling's **0.0870** -- still short by
**0.0356**, and still far outside spelling's CI lower bound of 0.07825. `DOES_NOT_CLEAR_
ORTHOGRAPHIC_FLOOR` is robust to this objection. What it DOES qualify is the narrower claim
`graded_helps=False`: with n=3 draws per arm, that sub-verdict rests on one projection seed and is
**NOT settled**. Anyone re-opening the graded question should re-open it here, and only here.

**What this cell does NOT license:** it does not license wiring spelling in (a floor is cleared by
understanding, never adopted); it does not license turning the graded switch off (the point estimate
is positive on every summary computed, and self-retrieval is better with it on, 0.7860 vs 0.7358);
and it does not license any claim that the graded path is worthless -- `graded_hurts` is also False.

---

## 4. SCRAMBLE RECONCILIATION -- 0.0080 and 0.01375 are BOTH right, for DIFFERENT donor rules

`notes/STATUS.md` POSITION quoted scramble **0.0080**; this cell measured **0.01375**. Neither is
adopted silently. Traced:

| | STATUS.md's 0.0080 | tonight's 0.01375 |
|---|---|---|
| cell | `exp_grounding_readout_known_answer_v1`, `stage_b.open_vocabulary_readout.hit_at_1.B6_OPEN_SCRAMBLE` | `exp_graded_path_vs_orthographic_floor_v1`, `F_SCRAMBLE_{ON,OFF}` |
| value / CI | 0.00800, CI [0.00525, 0.01100] | 0.01375, CI [0.01050, 0.01725] |
| n_items / anchors | 4000 / 5491 | 4000 / 5491 |
| metric | open-vocab hit@1 | open-vocab hit@1 |
| **donor rule** | **CONFLICT-AVOIDING DERANGEMENT** (`:503`): a donor sharing ANY of `{L, G, F}` with the item is EXCLUDED | **PLAIN `rng.permutation(n)`** (`:357`), NO conflict avoidance |
| query | `space.bundle(donor_L)` -- **GRADED** in that run (`HD_GRADED_COMPARATOR_env=1`, `graded_comparator=true` in its metrics; `reading_grounding_loop.py:504` returns `s.copy()` when the switch is on) | `mat_graded[pos[donor_L]]` (ON arm) / `mat_signed[...]` (OFF arm) |

**So the harness, n, pool, gold, metric AND query format are IDENTICAL (both graded); the DONOR
CONSTRAINT is the whole difference.** (An earlier draft of this table labelled B6's query "signed";
that was wrong -- `bundle` follows the `GRADED_COMPARATOR` switch, which was ON for that run.
Correcting it STRENGTHENS the ruling: query format is now excluded as a candidate explanation.) The graded-path cell retains donors whose gold set overlaps the item's, and those
donors score structural hits that have nothing to do with the substrate's arithmetic. That inflates
its floor. Checked and ruled out as the cause: the plain permutation happens to have **zero fixed
points** at `MASTER_SEED+21 = 20260835` (verified by re-drawing it), so `donor[i]==i` contributes
nothing.

**The bit-identical `F_SCRAMBLE_ON`/`F_SCRAMBLE_OFF` digests corroborate this mechanistically.**
If the scramble hits were produced by vector arithmetic, a graded query and a signed query would
diverge on at least some items. They diverge on none. That is the signature of hits driven by
**donor/item gold-set overlap**, which is invariant to graded-vs-signed -- exactly the population
the conflict-avoiding derangement removes.

**RULING (neither number retired):**
- **0.0080 is the correct scramble floor for the C3 read-out claim** -- it is the arm from the very
  cell that produced the 0.0480 headline, and its donor rule removes gold-overlap contamination.
  STATUS.md should keep it, **but must name the harness**, which it did not.
- **0.01375 is correct and internally consistent within tonight's cell**, and is the more
  CONSERVATIVE floor. Every tonight-cell delta-vs-scramble must use it, not 0.0080.
- **Neither may be quoted bare.** Quote the number with the donor rule, or not at all. The two CIs
  ([0.00525,0.01100] vs [0.01050,0.01725]) barely touch, so they are not statistically at war --
  they are two different questions, and the looser rule gives the higher floor, as it should.

Cross-check on scope: `exp_orthographic_floor_vet_v1` has **NO scramble arm at all** (its `per_arm`
keys are exactly `A1_BASE`, `A6_TRIGRAM_ONLY`, `A7_PREFIX_ONLY`, `A8_MAXORTHO`), so the 0.0080 in
STATUS.md was never sourced from the floor-VET cell despite sitting beside its numbers.

---

## 5. QUALIFICATION OF THE STANDING TOP ITEM (required, and it is material)

STATUS.md's TOP ITEM leans on **conjunctive coding** as the brain-faithful fix, and the drill note
section 4 calls perirhinal conjunctive coding *"the closest published match to our exact failure."*
Four orphaned literature scans were rescued tonight (section 6) and they **materially qualify that
lean.** Both qualifications come from the scans' own verbatim text with their tags intact:

1. **The perirhinal conjunction OPERATION is UNPINNED.** The scan searched specifically and
   repeatedly and found **NO study reporting a quantitative superadditivity/nonlinearity coefficient
   for real perirhinal neurons**. The dendritic supralinearity literature it found (Polsky/Mel/
   Schiller 2004; Losonczy & Magee 2006) is measured in **other cell types and regions** and no
   study connects it to perirhinal conjunctive coding by direct measurement. The one model verified
   in full text -- **Cowell, Bussey & Saksida 2006, *J Neurosci* 26(47):12186-12197** -- implements
   conjunction as a **Kohonen self-organising map with a Euclidean-distance readout**, and its own
   authors frame the Kohonen grid as *"a computational abstraction ... not a claim that perirhinal
   neurons literally compute Euclidean distances."* The scan's own warning, verbatim: *"No equation
   should be adopted as 'the' perirhinal conjunction operation on the basis of this literature."*
   [`notes/lit_scan_perirhinal_conjunctive_coding_operation_2026-08-14.md`]
2. **The feature-ambiguity account is ACTIVELY CONTESTED with genuine FAILED REPLICATIONS.**
   **Clark, Reinagel, Broadbent, Flister & Squire 2011, *Neuron* 70(1):132-140** -- 6 lesion vs 6
   control rats, 14 graded morph levels, 150 probe trials/level -- found both groups fall from ~87%
   to chance and **statistically indistinguishable at EVERY level**, while the same lesioned rats
   WERE impaired on a separate recognition-memory test (**a positive control inside the same
   animals**, which is what makes this a strong null rather than a failed manipulation). Human-side:
   **Levy, Shrager & Squire 2005** and **Shrager et al. 2006** (6 patients, intact on all four
   experiments). The supporting rat study it contradicts is **Norman & Eacott 2004**.
   [`notes/lit_scan_feature_ambiguity_hypothesis_lesion_evidence_2026-08-14.md`]

**What this changes, precisely.** It does **not** refute the TOP ITEM, and it must not be used to.
The TOP ITEM rests on **three of our own floored results** (FACTORED 1.000 vs FLAT 0.003;
CONJUNCTIVE 1.000 vs ADDITIVE 0.273; PERMUTATION 1.0000 vs FHRR 0.0629), which stand on their own
measurements and are untouched by any dispute about perirhinal cortex. What changes is the
**warrant**: conjunctive coding may be pursued as **our engineering choice, justified by our own
floored results**, and may **NOT** be pursued as *"this is what the brain does, pinned."* The brain
side is UNPINNED in its operation and CONTESTED in its lesion evidence. Per the standing rule that
UNPINNED is an answer and no equation is invented and dressed as biology, any conjunctive stage we
build must be labelled an engineering choice at the moment it is built.

---

## 6. FOUR ORPHANED LITERATURE SCANS RESCUED (and a rescue hazard worth recording)

Persisted verbatim, tags intact, per `notes/research_persistence_policy_2026-08-13.md` section 1:

- `notes/lit_scan_perirhinal_conjunctive_coding_operation_2026-08-14.md` (21,890 chars)
- `notes/lit_scan_feature_ambiguity_hypothesis_lesion_evidence_2026-08-14.md` (20,743 chars)
- `notes/lit_scan_perirhinal_purely_mnemonic_counter_position_2026-08-14.md` (23,681 chars)
- `notes/lit_scan_vvs_to_mtl_representational_hierarchy_interference_2026-08-14.md` (21,933 chars)

Eight primary sources registered via `tools/literature_cache.py add`, each with its evidence tag in
the `--claim` field.

> **RESCUE HAZARD -- RECORD THIS.** The transcripts were briefed as living in
> `.../Temp/claude/D--AI/<session>/tasks/<id>.output`. **Three of the four are 0 BYTES there**
> (`a175a9617cb40b4b2`, `a109fef3a83d9f74c`, `a9606ac3ac8d2c36b`; link count 1, i.e. the hardlink
> was truncated), and only `a8a789368260aeef8` survived at 225,600 bytes. **All four survive intact
> in the canonical store** `~/.claude/projects/d--AI/<session>/subagents/agent-<id>.jsonl`
> (240,459 / 317,605 / 227,509 / 225,600 bytes). An absence claim made from `tasks/` alone would
> have been WRONG and would have destroyed four reports. **Enumerate BOTH locations; the
> `subagents/` store is the authoritative one and `tasks/` is a lossy hardlink view.**

This also means the drill note's section 0 enumeration -- *"the three literature drills dispatched
this evening produced ZERO artifacts on disk"* -- was **correct about `notes/` and
`literature_cache/` and wrong as a conclusion about the reports existing.** The reports existed the
whole time, in a location that enumeration did not cover. It is the same fault the standing rule
names: an absence claim requires an enumeration **of the right place**.

---

## 7. DO-NOT-REDO ENTRIES ADDED

**34. FLIPPING THE GRADED SWITCH EXPECTING A C3 GAIN.** MEASURED AND NULL.
`exp_graded_path_vs_orthographic_floor_v1`: ON 0.0480 vs OFF 0.0465, **d=+0.0015 CI
[-0.0055,+0.0083], INCLUDES ZERO**, n=4000, 5491 anchors, positive control
`a1_graded_on_reproduces_c3_headline_0480_exactly=true`. Neither arm clears the orthographic floor
(spelling 0.0870; ON-minus-spelling **-0.0390**, CI excludes zero). **Revival criterion:** the
projection-draw ensemble gives a draw-mean delta of **+0.0092** (t~5.0 on 3 draws/arm) and the
canonical projection is the worst-of-four for ON and best-of-four for OFF -- so a re-run with
**>=10 independent projection draws per arm** could legitimately overturn `graded_helps=False`.
It could **NOT** overturn the floor verdict: +0.0092 leaves us 0.0356 below spelling.

**35. QUOTING +0.0602 (or 0.6395 -> 0.6980/0.69975) AS A C3 NUMBER.** WRONG CURRENCY.
Those are **near-neighbour 2AFC** accuracies from `exp_graded_divisive_comparator_v1`, chance
**0.50**, pool **2,377** anchors. C3 is **open-vocabulary hit@1**, chance ~0.00018, pool **5,491**.
The same manipulation measured in C3 currency is **+0.0015, null**. The source cell's HARD_PASS
stands on its own scorer and is not demoted; only the carry-across is refuted. **Revival criterion:
none -- this is a units error, not a hypothesis.** General form, and the reason it is worth a slot:
**a gain on one scorer is not a gain on another scorer; carry a metric's identity with its number.**

---

## 8. WHAT WAS CHECKED, AND WHAT RULED OUT THE ALTERNATIVES

Per the six-point evidence-discipline check, before calling anything worse than documented:
**right file** -- `data/exp_graded_divisive_comparator_v1/metrics.json` and
`data/exp_grounding_readout_known_answer_v1/metrics.json` at their canonical paths, not
`_SMOKE_`/`_scratch_` neighbours; **right version** -- HEAD `d596bbcbc`, and `38f7a0d5c` confirmed
an ancestor; **right environment** -- `.venv/Scripts/python.exe` throughout, never bare `python`;
**right corpus** -- both C3 cells at n_items 4000 / n_anchors 5491, the graded-comparator cell at
n_items 4000 / n_anchors **2377** (this mismatch is the finding, not an error in the check);
**right metric** -- open-vocab hit@1 vs 2AFC, confirmed by each cell's own declared `chance`
(0.00018-scale vs `chance = 0.5`); **right arm** -- `A_SSN`/`A_GGZ` are the graded-comparator cell's
own pre-designated control/treatment per its `HP_SCOPE`, and `A1_GRADED_ON`/`A9_GRADED_OFF` are
tonight's, never compared across runs. The scramble donor rules were read from the two cells'
**source** (`:503` and `:357`), not inferred from their outputs.
