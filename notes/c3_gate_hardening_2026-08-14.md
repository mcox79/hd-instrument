# C3 gate hardening -- a zero-meaning control cleared the gate, so the gate is wrong

> 🔴 **WORDING CORRECTED 2026-08-15 (corrections C16 + C22). THE CONCLUSION OF THIS NOTE STANDS;
> ITS DESCRIPTION OF THE ARM DOES NOT.** This note repeatedly calls `A5_STRINGCTRL` "a zero-meaning
> arm" / "a pure character-trigram control containing no meaning at all" (lines 1, 104, 121, 244,
> 284, 297, 329). **The CHANNEL is zero-meaning; the ARM is not.** Verified in source:
> `experiments/exp_meaning_supply_separation_v1.py:235-240` defines
> `arm_scores(base, aux, w) = _z(base) + w*sum(_z(aux))` and `:469` sets
> `"A5_STRINGCTRL": [aux_t]`, so the arm is **`z(base) + w*z(trigram)` and carries the FULL
> substrate signal plus spelling** -- a decomposition, not a standalone floor.
> **Why the conclusion survives anyway:** an arm differing from the failing base ONLY by a spelling
> channel cleared the old criterion, which is exactly the gameability demonstration this note was
> written to make. The 0.10275 figure is unaffected.
> **The genuinely standalone zero-substrate arm is a different object in a different cell** --
> `exp_orthographic_floor_vet_v1`'s `A6_TRIGRAM_ONLY` (`t_mat[sel] @ tq`, no base term), which
> scores **0.0870 [0.07825, 0.09600]** against our 0.0480 and is the number to quote for
> "spelling alone beats us". Kept in place rather than rewritten: the history of what was believed
> is the audit trail.

**Filed:** 2026-08-14. **Author role:** audit (cert-owner). **Status of this note:** proposal +
executed re-scoring. It does NOT edit `notes/SUBSTRATE_STRATEGY.md` or `notes/STATUS.md`; the exact
replacement text for both is in section 6, ready to apply by whoever owns those files.

**Executable form of everything below:** `tools/c3_gate.py` (`--self-test`, `--score <metrics.json>`).
The gate is now a function, not a sentence. That is the point.

---

## 1. The defect, with its evidence

**The gate, as currently stated:** ">=10% MEANINGFUL against a recorded floor, tautologies <10%."

**Where it is stated** (enumerated, not searched -- method in section 7):

| # | location | text | authority |
|---|---|---|---|
| 1 | `notes/SUBSTRATE_STRATEGY.md` L79-83 | "Revival criterion: **>=10% MEANINGFUL against a recorded floor, tautologies <10%.**" | **AUTHORITATIVE** -- the gate cell's own metrics names it as `revival_criterion.source` |
| 2 | `notes/SUBSTRATE_STRATEGY.md` L76 | the C3 scoreboard row (`hit@1 4.80%` ... `scramble 0.80%`) | the quoted headline |
| 3 | `notes/SUBSTRATE_STRATEGY.md` L129-131 | STEP 1 result: "**half** the 10% revival gate" | derived restatement |
| 4 | `notes/STATUS.md` L11-14 | "5.2pp short of the >=10% gate ... GROWTH PAUSED until quality holds" | the recovery-chain restatement |
| 5 | `notes/HANDOFF_full_project_report_for_new_team_2026-08-14.md` L200, L252, L255 | "~5.2pp short of >=10%"; "does the grounding-quality gate (>=10%) clear"; "growing the foundation before closing quality scales the error" | onboarding restatement |
| 6 | `data/exp_grounding_readout_known_answer_v1/metrics.json` -> `revival_criterion.recorded` (and the `_SMOKE`, `_SMOKE_G0`, `_G0` siblings) | the same sentence, recorded in-cell with a back-pointer to (1) | recorded artifact -- **immutable, do not edit** |

**The measurement that breaks it.** `data/exp_meaning_supply_separation_v1/metrics.json`
(commit `c0e6ec0da`, prereg `preregs/2026-08-14_meaning_supply_separation_v1.md`, filed
`944ff2fa8`) ran a fifth arm the prereg's own bands never mentioned: `A5_STRINGCTRL`, a
row-L2-normalized **hashed character-trigram profile** of the anchor STRING
(`exp_meaning_supply_separation_v1.py:151-175`). No corpus. No training. No meaning of any kind --
it is spelling.

At blend weight `w=1.00` that arm scored **hit@1 = 0.10275**, bootstrap CI **[0.0935, 0.11225]**,
against the recorded scramble floor **0.008**. It **clears the gate as written**: >=10%, floored,
zero tautologies.

So the gate that pauses knowledge-base growth for the entire project is passable by surface form.
That is not a hypothetical attack; it is on disk, in a cell that was landed and committed.

**Full re-scored record** (recomputed off `metrics.json`, all three pre-registered weights;
`A1_BASE` is bit-identical across w because w=0 for it, and it reproduces the C3 headline exactly
-- same 0.0480, same CI [0.04125, 0.05475]):

| arm | w | hit@1 | median rank | top-50 | separation margin | crowding nn | crowding/null |
|---|---|---|---|---|---|---|---|
| A1_BASE | any | 0.04800 | 37.0 | 0.5565 | -2.5423 | 0.4553 | 2.0097 |
| A2_NORMS | 0.25 | 0.06200 | 27.0 | 0.6125 | -2.4510 | 0.4484 | 1.9793 |
| A3_ENCODER | 0.25 | 0.06500 | 31.0 | 0.5980 | -2.4778 | 0.4553 | 1.9090 |
| A4_BOTH | 0.25 | 0.07525 | 24.0 | 0.6463 | -2.3924 | 0.4493 | 1.8978 |
| **A5_STRINGCTRL** | 0.25 | 0.06925 | 28.0 | 0.6068 | **-2.6188** | 0.4301 | 2.0060 |
| A2_NORMS | 0.50 | 0.07125 | 23.5 | 0.6420 | -2.3903 | 0.4602 | 1.6064 |
| A3_ENCODER | 0.50 | 0.07500 | 25.5 | 0.6185 | -2.4528 | 0.4668 | 1.6512 |
| A4_BOTH | 0.50 | 0.09400 | 18.0 | 0.6823 | -2.3248 | 0.4697 | 1.4832 |
| **A5_STRINGCTRL** | 0.50 | 0.09050 | 25.0 | 0.6118 | **-3.2045** | 0.3880 | 1.9401 |
| A2_NORMS | 1.00 | 0.08850 | 19.0 | 0.6680 | -2.3424 | 0.5739 | 1.1601 |
| A3_ENCODER | 1.00 | 0.08800 | 21.0 | 0.6475 | -2.4786 | 0.5348 | 1.2184 |
| A4_BOTH | 1.00 | 0.11900 | 13.0 | 0.7040 | -2.3670 | 0.5784 | 1.1327 |
| **A5_STRINGCTRL** | 1.00 | **0.10275** | 31.0 | 0.5867 | **-5.4731** | 0.3967 | 1.2430 |

### 1a. Three framing corrections to how this defect has been described

These matter because they change which hardened gate actually works.

1. **The string control's rank does NOT worsen against the baseline, and its top-50 does NOT drop
   against the baseline.** At w=1.00 it goes 37.0 -> **31.0** (better) and 0.5565 -> **0.5867**
   (better). The "worsens to 31.0 / drops to 0.5867" reading is against A5's OWN w=0.50 values
   (25.0, 0.6118), i.e. it is a NON-MONOTONICITY in w, not a regression against base.
   **Consequence: the natural conjunction "hit@1 >= 10% AND median rank improves AND top-50
   improves" WOULD STILL HAVE PASSED THE TRIGRAM CONTROL.** Adding rank and top-50 does not fix
   this defect. That is the single most important finding in this note and it is asserted in
   `tools/c3_gate.py --self-test` as a regression fixture (case 2).
2. **"Crowding rose in every meaning arm" is true only of the RAW statistic at w>=0.50.** At w=0.25
   crowding FALLS in every meaning arm (0.4484 / 0.4553 / 0.4493 vs base 0.4553), and the cell's
   own scale-free statistic, `ratio_to_null`, FALLS in every meaning arm at every w
   (2.0097 -> 1.13-1.98). Meanwhile the raw statistic falls for the ATTACKER (0.4553 -> 0.3967).
   **Consequence: "crowding does not rise" is an INVERTED condition** -- on the raw number it
   passes the trigram control and fails the genuine arm. Crowding is excluded from the gate below
   on this measured basis, not on taste.
3. **`w=1.00` is not the headline weight.** The prereg fixes the headline at `w=0.50`
   (`w_headline: 0.5`, `max_over_w_is_an_optimistic_upper_bound: true`). At the headline weight NO
   arm reaches 0.10 at all. The gaming demonstration is real and is the point of this note, but
   the arm that performs it sits at an optimistic upper-bound setting, which the cell itself
   labels as such.

---

## 2. The hardened gate

A C3 claim PASSES only when **all four** hold. Any missing input is **NOT_EVALUABLE**, never PASS.

> **HG1 -- MAGNITUDE, AGAINST A RECORDED FLOOR.** Open-vocabulary hit@1 **>= 0.10** on n >= 1000
> items, with a paired-bootstrap CI on (arm minus the recorded floor) that **excludes zero**, and
> tautology rate **< 0.10**.
>
> **HG2 -- THE DISTRIBUTION MOVED, NOT JUST THE ARGMAX.** Median target rank **strictly improves**
> AND fraction-of-gold-in-top-50 **strictly improves**, both against the SAME cell's base arm on
> the SAME items.
>
> **HG3 -- WITHIN-NEIGHBOURHOOD SEPARATION DID NOT DEGRADE.** The separation margin (best-gold
> minus best-non-gold, in sd units of the item's candidate pool) is **>= the base arm's**. Cells
> must report it **restandardized on the arm's own final score vector** (see 2b).
>
> **HG4 -- THE STRING-FORM CONTROL WAS RUN AND WAS BEATEN.** A zero-meaning character-trigram arm,
> blended by the IDENTICAL mechanism at the IDENTICAL weight, was run and reported; and the paired
> CI on (claimed arm minus string control) **excludes zero**. **Absence of this arm is
> NOT_EVALUABLE, not PASS.**
>
> Reported but explicitly NOT gating: semantic crowding, sister-error conversions, 2AFC.

### 2a. Why this set, and why nothing smaller or larger

Each condition blocks a **distinct, demonstrated-or-pre-registered** failure mode. None is
decorative, and one candidate was measured out.

| condition | the attack it uniquely blocks | evidence it is needed |
|---|---|---|
| HG1 | claiming a win with no floor / at trivial magnitude | the whole H1 hygiene backlog (134 floorless PASSes) |
| HG2 | argmax lottery -- tie-break luck with no distributional movement | pre-registered as `MIDDLE_BAND_ARGMAX_ONLY / SUSPECT`; it is the verdict this very cell landed |
| HG3 | surface-form gaming that raises argmax while collapsing separation | **A5 at w=1.00: -5.4731 vs base -2.5423.** The ONLY condition of the four that stops it |
| HG4 | any shortcut whose gain a zero-meaning arm reproduces | the reason the defect was found at all |

**Excluded, on measurement:** *crowding* (section 1a.2 -- moves the wrong way; would pass the
attacker and fail the real arm), and *non-monotonicity in w* (a genuine tell, but it requires a
w-grid that most cells will not have -- keep it as a diagnostic).

**Why not fewer.** HG3 alone is a "did-not-degrade" condition, satisfiable by an arm that does
nothing; it needs HG1 for magnitude. HG2 alone was shown above to pass the attacker. HG4 alone is
weak in exactly the regime that matters: at w=1.00 the best real arm beats the control by only
+0.01625 hit@1 with heavily overlapping CIs, so HG4 may well not fire where HG3 fires decisively.
**Standing simplification criterion:** if three consecutive C3 claims show HG4 firing wherever HG3
fires, HG3 may be demoted to diagnostic. Until then both stay.

**Why not more.** Five-plus conditions is how a gate becomes unreachable and therefore ignored. The
non-vacuity check in section 3 is what licenses this specific four: real meaning arms already
satisfy HG2 and HG3 today, at every weight. The gate is short on ONE thing -- magnitude -- which is
precisely what C3 is supposed to measure.

### 2b. A measurement defect HG3 must not inherit

`separation_margin_z` as emitted today is in sd units of the candidate pool but computed on a
score `z(base) + w*sum_k z(aux_k)` that is **not itself restandardized**. An arm carrying more aux
weight therefore has a mechanically larger `|margin|`. Left uncorrected this biases HG3 against
heavier arms. Two things follow, and the second is a hard result:

- **Spec:** future cells must emit `separation_margin_z.restandardized` (margin divided by the sd
  of the arm's own final score vector). `tools/c3_gate.py` prefers that field when present.
- **The A5 rejection survives the worst case analytically.** `Var(z(base) + w*z(aux)) =
  1 + w^2 + 2*w*rho <= (1+w)^2`, so at w=1.00 the largest admissible sd is exactly **2.0**. Even
  then A5's corrected margin is **-5.4731 / 2.0 = -2.7365**, still worse than base's **-2.5423**
  (whose sd is exactly 1 by construction). **HG3's rejection of the trigram control cannot be
  explained by the scale artifact.** At w=0.50 and w=0.25 it CAN be (best-case corrected -2.1363
  and -2.0950, both better than base) -- so HG3 fires provably only at the weight where the arm
  actually cleared the gate. Stated plainly because it is a real limit on the current metric.
  A4_BOTH passes HG3 at sd=1 by +0.15 to +0.22 and any sd >= 1 only widens that.

---

## 3. Re-scoring the record -- both directions

Command (recompute off disk, `.venv` python):

```
.venv/Scripts/python.exe tools/c3_gate.py --score data/exp_meaning_supply_separation_v1/metrics.json --tautology 0.0
.venv/Scripts/python.exe tools/c3_gate.py --score data/exp_grounding_readout_known_answer_v1/metrics.json --base-arm B6_OPEN_SCRAMBLE --string-arm __NONE__
```

(`--tautology 0.0` is INHERITED, not assumed: the cell reuses `C3.build_items` and masks the
lemma's own anchors at `exp_meaning_supply_separation_v1.py:441-442`, the same construction that
measured 0 tautologies in every live arm of the C3 cell. Stated because an inherited number is a
claim.)

### `exp_meaning_supply_separation_v1` -- 12 arm-by-w cells, **0 PASS**

| arm | w | HG1 | HG2 | HG3 | HG4 | status |
|---|---|---|---|---|---|---|
| A2_NORMS | 0.25 / 0.50 / 1.00 | FAIL | PASS | PASS | ? | **FAIL** (magnitude) |
| A3_ENCODER | 0.25 / 0.50 / 1.00 | FAIL | PASS | PASS | ? | **FAIL** (magnitude) |
| A4_BOTH | 0.25 / 0.50 | FAIL | PASS | PASS | ? | **FAIL** (magnitude) |
| **A4_BOTH** | **1.00** | **PASS** | **PASS** | **PASS** | **?** | **NOT_EVALUABLE** -- only because the cell never computed the paired CI vs the string control |
| A5_STRINGCTRL | 0.25 / 0.50 | FAIL | PASS | FAIL | ? | **FAIL** |
| **A5_STRINGCTRL** | **1.00** | **PASS** | **PASS** | **FAIL** | ? | **FAIL** -- HG1 and HG2 both pass it; **HG3 alone stops it** |

### `exp_grounding_readout_known_answer_v1` (the gate's own cell) -- **0 PASS**

`B5_OPEN_REAL`: **FAIL** on HG1 (0.0480 < 0.10). NOT_EVALUABLE on HG2, HG3 and HG4 -- **the cell
that produced the 4.80% C3 headline records no median rank, no top-50 fraction, no separation
margin, and ran no string-form control.** It is not merely short of the hardened gate; three
quarters of it are unmeasured there. (Those diagnostics do exist for the same items via
`exp_meaning_supply_separation_v1`'s `A1_BASE`, which reproduces the headline exactly: rank 37.0,
top-50 0.5565, margin -2.5423.)

### Both directions, explicitly

- **Does the hardened gate stop the string control?** Yes. A5 at w=1.00 = FAIL. And the
  weaker candidate conjunction (hit@1 + rank + top-50) does **not** -- verified, section 1a.1.
- **Does the hardened gate fail everything ever measured?** No, and this is the non-vacuity
  evidence: **HG2 passes in 12 of 12 arm-by-w cells; HG3 passes in 9 of 12** (failing exactly the
  three trigram-control cells). A4_BOTH at w=1.00 satisfies HG1, HG2 and HG3 simultaneously and is
  held up only by an uncomputed CI. The hardened gate is reachable; the program is short on
  magnitude, not on gate design.

---

## 4. Making the string control structural rather than advisory

Advisory controls get skipped. **The control that caught this defect appears in NO pre-registration
at all** -- verified: `preregs/2026-08-14_meaning_supply_separation_v1.md` at HEAD contains zero
occurrences of `A5_STRINGCTRL`, "string control" or "string-shortcut"; the arm was added in a
follow-up cell commit (`5db7111f6`, after `aead69d67`) and the prereg was never amended. The
project's most consequential control of the week existed purely because one cell author decided to
add it. That is not a mechanism. Four real ones, in decreasing order of how hard they are to route
around:

1. **The gate is a function, and the function refuses.** `tools/c3_gate.evaluate` returns
   `NOT_EVALUABLE` -- never `PASS` -- when the string-control arm is absent. `--self-test` case 1
   asserts exactly this on an arm that clears every OTHER condition, and the negative control
   (`--_disable_guard`) shows the same arm turning into `PASS` the moment the guard is off, which
   proves the guard is load-bearing rather than decorative.
2. **"Clearing C3" is DEFINED as exit 0 from `tools/c3_gate.py --score <metrics.json>`.** Not as a
   sentence someone quotes. Prose gates get reinterpreted by each new reader; an executable
   predicate does not. The replacement scoreboard text in section 6 says this in the row itself.
3. **The control is supplied, so skipping it is a choice and not a cost.**
   `tools/c3_gate.string_control_scores(query, candidates)` returns the aux similarity vector
   directly -- a C3 cell adds the arm in two lines, using the SAME blend and the SAME weight. No
   cell has to reimplement hashed trigrams, and no cell gets to claim the control was too
   expensive.
4. **Doc-code coupling is marked on both sides** (CLAUDE.md, "a doc parsed by code is coupled to
   it"): the module docstring names `notes/SUBSTRATE_STRATEGY.md` PART 1, and the replacement C3
   text names `tools/c3_gate.py`. Changing one without the other is itself the defect.

Not implemented here, and deliberately left to whoever owns dispatch: a **SCHEMA-VET rule that a
pre-reg naming C3 as its gate is rejected before dispatch unless it declares the string-form arm**.
That is the cheapest possible enforcement point -- it costs nothing to add a control before a run
and costs a whole cell to add one after.

---

## 5. The honest current C3 status

**Plainly: the gate as previously stated was never a meaning gate, so "5.2pp short of a 10% gate"
was measuring the wrong distance.** It is not that C3 was passed and should be un-passed -- C3 has
never been claimed as passed. It is that the *distance to passing* was quoted against a threshold
that a zero-meaning arm has now been measured clearing. A number that a trigram profile can reach
is not a measure of grounding quality, so "4.80% out of a needed 10%" was never a meaningful
fraction of anything.

**The honest current statement:**

- **C3 is NOT PASSED, and under the hardened definition it is NOT YET FULLY MEASURED.**
- The live open-vocabulary read-out is **hit@1 4.80% vs a recorded scramble floor of 0.80%**
  (n=4000, 5491 anchors, delta +4.00pp, CI [+3.30, +4.70], `204eba1a0`). **That number survives
  unchanged** -- it is a real, floored measurement of the base path, and nothing here demotes it.
- What changes is its **interpretation**: 4.80% clears HG1's floor requirement but not its
  magnitude, and the cell reporting it cannot answer HG2, HG3 or HG4 at all. So the correct status
  is "FAILS on magnitude; UNMEASURED on three of four conditions", not "half passed".
- **No arm anywhere on disk passes the hardened gate.** The best (`A4_BOTH` at w=1.00, hit@1
  0.119) satisfies three of four and is blocked by a CI nobody computed -- and it sits at an
  optimistic upper-bound weight the cell itself declines to quote as shipped.
- **GROWTH STAYS PAUSED**, for a now-stronger reason than before: not merely that quality is below
  a threshold, but that the threshold we were measuring against did not distinguish meaning from
  spelling.
- Everything downstream that reported "did this help C3?" using hit@1 alone should be re-read with
  section 3's re-scoring in hand. Nothing in the record is invalidated by this; several things in
  the record are less informative than they read.

---

## 6. Exact replacement text, ready to apply

**Do not apply these yourself if you are not the owner of the file** -- concurrent agents hold
`SUBSTRATE_STRATEGY.md` and `STATUS.md`.

### 6a. `notes/SUBSTRATE_STRATEGY.md` -- replace the C3 row (currently line 76)

```
| **C3** | **Reading-grounding read-out quality** | **NOT PASSED.** Live open-vocabulary **hit@1 4.80%**, n=4000, 5491 anchors; tautology rate **0.0%**. Under the HARDENED gate: FAILS magnitude, and UNMEASURED on 3 of 4 conditions | **scramble 0.80%** — a REAL FLOOR, recorded 2026-08-14 (`204eba1a0`). Delta **+4.00pp**, CI [+3.30, +4.70] | `exp_grounding_readout_known_answer_v1` (STEP 1, REPORTED). Gate HARDENED 2026-08-14 after a zero-meaning trigram control cleared the old one (`c0e6ec0da`) | **separation between sister terms.** hit@1 alone is NOT the gate — a C3 claim with no string-form control arm is NOT EVALUABLE, never PASS |
```

### 6b. `notes/SUBSTRATE_STRATEGY.md` -- replace the revival-criterion paragraph (currently lines 79-83)

```
**C3 IS THE GATE, AND THE GATE WAS GAMEABLE UNTIL 2026-08-14.** A pure character-trigram control
containing no meaning at all scored hit@1 **0.10275** and cleared the old ">=10% against a recorded
floor" criterion (`exp_meaning_supply_separation_v1`, arm A5_STRINGCTRL at w=1.00, `c0e6ec0da`), so
that criterion is RETIRED. Adding rank and top-50 does NOT fix it: the control improves both against
base (37.0 -> 31.0, 0.5565 -> 0.5867). The gate is now FOUR conditions, ALL required, and it is
EXECUTABLE — "C3 is cleared" means `python tools/c3_gate.py --score <metrics.json>` exits 0:

- **HG1 MAGNITUDE** — open-vocabulary hit@1 >= 0.10, n >= 1000, paired-bootstrap CI on
  (arm − recorded floor) excludes zero, tautology rate < 0.10.
- **HG2 DISTRIBUTION MOVED** — median target rank AND frac-gold-in-top-50 both strictly improve vs
  the same cell's base arm on the same items.
- **HG3 SEPARATION NOT DEGRADED** — separation margin >= the base arm's, reported restandardized on
  the arm's own score vector. THIS is the condition that stops the trigram control (−5.4731 vs base
  −2.5423), provably so at w=1.00 even under the worst-case scale correction.
- **HG4 STRING CONTROL RUN AND BEATEN** — a zero-meaning char-trigram arm, blended by the identical
  mechanism at the identical weight, was RUN and REPORTED, and the paired CI on
  (arm − string control) excludes zero. **A claim without this arm is NOT EVALUABLE, never PASS.**

Crowding is REPORTED but NOT gating: measured on the record it moves the wrong way (it falls for the
trigram control and rises for the genuine meaning arms), so gating on it would pass the attacker and
fail the real result. Rationale, the full re-scoring of every arm on disk, and the mandatory-control
mechanism: `notes/c3_gate_hardening_2026-08-14.md`.

**Nothing on disk passes the hardened gate.** Best measured arm is `A4_BOTH` at w=1.00 (hit@1 0.119)
which clears HG1+HG2+HG3 and is NOT_EVALUABLE on HG4 for want of an uncomputed CI — and w=1.00 is an
optimistic upper bound, not the pre-registered headline (w=0.50, where no arm reaches 0.10). The
gate is REACHABLE, not vacuous: HG2 holds in 12 of 12 measured arm-by-w cells and HG3 in 9 of 12.
**While C3 fails, KNOWLEDGE-BASE GROWTH STAYS PAUSED.** Growth multiplies whatever the quality is.
```

### 6c. `notes/SUBSTRATE_STRATEGY.md` -- amend STEP 1 (currently lines 129-131)

Replace `**half** the 10% revival gate` with:

```
FAILS the hardened gate's MAGNITUDE condition, and is UNMEASURED on its other three (this cell
records no rank, no top-50, no separation margin, and no string-form control). "Half the gate" was
a reading of the RETIRED single-number criterion — see the C3 row.
```

### 6d. `notes/STATUS.md` -- replace the POSITION paragraph (currently lines 11-14)

```
## POSITION
C3 read-out HAS A FLOOR: open-vocab hit@1 4.80% vs scramble 0.80% (n=4000, 5491 anchors,
`exp_grounding_readout_known_answer_v1`, 204eba1a0). THE GATE ITSELF WAS GAMEABLE AND IS NOW
HARDENED (2026-08-14): a zero-meaning character-trigram control scored 0.10275 and cleared the old
">=10% vs a floor" criterion (`c0e6ec0da`). C3 now requires FOUR conditions and is EXECUTABLE --
`python tools/c3_gate.py --score <metrics.json>`; a claim with no string-form control arm is NOT
EVALUABLE, never PASS. NOTHING on disk passes it. "5.2pp short" was measured against the retired
criterion; do not re-quote it. Banked-facts arm AT_FLOOR (2.51% vs 1.25%); 2AFC 0.5393 MIDDLE_BAND;
tautologies 0 in EVERY arm (the 65.7% was an eligibility bug, C10). GROWTH PAUSED.
Detail: notes/c3_gate_hardening_2026-08-14.md.
```

### 6e. `notes/HANDOFF_full_project_report_for_new_team_2026-08-14.md` (L200, L252, L255)

Lowest priority (onboarding restatement, not authoritative). Replace each ">=10%" / "5.2pp short"
with "the four-condition hardened C3 gate (`tools/c3_gate.py`; see
`notes/c3_gate_hardening_2026-08-14.md`)". The `data/**/metrics.json` copies of the old sentence
are recorded run artifacts and must NOT be edited -- they are correct records of what the gate said
at the time those cells ran.

---

## 7. Method, and what this note does not establish

**How the gate statements were enumerated** (absence claims require an enumeration, not a search):
started from the back-pointer inside the gate cell itself
(`revival_criterion.source = "notes/SUBSTRATE_STRATEGY.md PART 1 (C3)"`), which identifies the
authoritative site; then grepped `notes/` and `preregs/` on absolute paths for the literals `10%`,
`>=10%`, the unicode `>=`, `revival`, `MEANINGFUL against a recorded floor` and `C3`, and read every
hit in the C3 arc. A full `data/` sweep timed out and was not completed -- the copies there are
recorded artifacts of past runs, immutable by convention, and the four found via the
`revival_criterion` key are listed in section 1. If another authoritative prose site exists outside
`notes/` and `preregs/`, this enumeration would not have found it.

**Verification checks performed** (CLAUDE.md evidence discipline 5): right file (both cited
`metrics.json` paths, not `_SMOKE` / `_G0` neighbours -- those were seen and excluded); right
version (HEAD `c0e6ec0da` on `dataprep/mcguffey-graded-corpus`); right environment
(`.venv/Scripts/python.exe` throughout, never bare `python`); right corpus (A1_BASE reproduces the
C3 headline bit-for-bit, 0.0480 with CI [0.04125, 0.05475] -- same items, same construction); right
metric (hit@1 over the same open-vocabulary argmax, all 5491 anchors eligible, lemma's own anchors
masked); right arm (all comparisons are within one cell, one w, against that cell's own base --
never across runs).

**What this note does NOT establish.** It does not re-derive the per-item scores -- the cells do not
persist them, so HG3's restandardized form could not be computed retroactively and is bounded
analytically instead (section 2b). It does not compute the missing arm-minus-stringctrl paired CIs;
those require the per-item hit vectors and therefore a re-run, which is out of scope here (read-only
on `hdlab/` and `experiments/`, no new experiment runs). It makes no claim about C1, C2 or C4, whose
gates are separate and were not audited.
