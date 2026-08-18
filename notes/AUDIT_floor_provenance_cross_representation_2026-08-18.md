# AUDIT: which arms are gated against a floor not computed on their own representation?

Auditor: skunkworks (audit-only). Date 2026-08-18. HEAD at audit start `7d5f53f16`.
Bound by `notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md` sec 6.40 pre-committed readings (i)/(ii)/(iii).
No band moved, no prereg touched, no experiment authored or run.

## VERDICT: BRANCH (i) FIRED -- AND (iii) FIRED ALONGSIDE IT

**(i) SOME arms are found gated against an imported cross-representation floor.**
**3 cells, 21 arms** banded against a floor computed on a different representation. All three
conclusions are marked **SUSPENDED, NOT REFUTED** -- *a wrong floor makes a verdict UNSUPPORTED; it
does not establish the opposite.*

**This is NOT a programme-wide crisis, and the Director's alarm was correctly calibrated but
over-scoped in one respect:** the repo's own write-rule ladder already implements the correct
discipline per-arm (see "WHAT IS CLEAN"). The defect is confined to the family of cells that
CONSUME `exp_dissociation_score_instrument_v1`'s CACHED floors instead of recomputing them.

**(iii) ALSO FIRED, and it is the more durable finding:** no `metrics.json` in this repo records the
REPRESENTATION a floor was computed on. Provenance is recorded along the POPULATION axis only.
Every determination below required reading source; none was decidable from `metrics.json`.

---

## HOW I ENUMERATED (an absence claim requires an enumeration, not a search)

1. `ls experiments/` at NAME level -> **5,946 entries**, then name-filtered for the programme family.
2. **Exhaustive content scan of ALL 5,872 `experiments/*.py`** via
   `data/session_local/skunkworks/floor_provenance_scan.py` (.venv python), markers:
   `0.5431`, `F_CONSTANT_PROTOTYPE`, `dissociation_score_instrument`, `max(four floors)`,
   `max_floor`, `FLOOR_NAMES`, `EXPECTED_AUC`, `EXPECTED_CACHED`.
   Result cached at `data/session_local/skunkworks/floor_scan_result.json`: **44 files with any
   marker, 6 carrying the literal `0.5431`.** This is the complete code surface.
3. Targeted bounded `ls data/<name>/metrics.json` per enumerated candidate. **No `os.walk` over
   `data/`.**
4. `tools/substrate_query.sh` NOT used (returns zero bytes, exits 0; its silence is not evidence).

Tooling note for future lanes: recursive `grep`/ripgrep over `experiments/` **times out** on this
disk (`experiments/data/` subtree; a flat `grep experiments/*.py` exceeded 5 minutes). A background
.venv Python scan of all 5,872 files completes in ~1 minute. `git log --diff-filter=A` is USELESS for
date-bounding here -- the whole tree shows as added since 2026-08-15.

---

## THE MECHANISM (the line that decides it)

`experiments/exp_dissociation_score_instrument_v1.py` L99-108 -- the floors, and their own rule:

```
THE FOUR FLOORS, PAIRWISE ANALOGUES (Gate 3, recomputed on THIS pair population, never imported):
  F_ORTHOGRAPHIC   cos(trigram_vec(w1), trigram_vec(w2)) -- aux['t_mat'] ...
  F_FREQUENCY      max(log1p(freq(w1)), log1p(freq(w2))) ...
  F_SCRAMBLE       cos() under FB.scramble_null(mat, seed) ...
  F_CONSTANT_PROTOTYPE  mean(FB.constant_prototype_floor(w1), ...) -- cosine-to-mean-direction ...
```

**Two of the four floors are computed FROM THE STORE MATRIX `mat`: `F_SCRAMBLE` and
`F_CONSTANT_PROTOTYPE`.** They are therefore REPRESENTATION-BOUND. `F_ORTHOGRAPHIC` (trigrams) and
`F_FREQUENCY` (corpus counts) are representation-independent.

**The sting: the bar is `max(four floors)`, and in every instance below the max is owned by one of
the two representation-bound floors** -- `F_CONSTANT_PROTOTYPE` (0.5431) on the WordNet instrument,
`F_SCRAMBLE` (0.5943) on the human instrument. *The bar IS the representation-bound quantity.*

Confirmed at source that these are built on the BAG store, not an arc store:
`exp_dissociation_score_instrument_human_v3.py` L394 `mat = np.asarray(C["mat"], ...)`,
L558 `scrambled = l2n(FB.scramble_null(mat, MASTER_SEED + 4433))`, L631 `Mn_incumbent = l2n(mat)`
-- the scramble floor and the incumbent bag arm are the SAME matrix.

---

## MIS-GATED: 3 CELLS, 21 ARMS

### A. `exp_typed_role_context_write_rule_dissociation_v1` -- 10 arms (KNOWN, the incident)
Landed `5170c7751`. Arms built on grammatical ARC events. Deciding line, L841:
```python
bar = gate["gate_report"]["recomputed_AUC_PER_ARM"]["F_CONSTANT_PROTOTYPE"]["auc"]
```
"recomputed" is true of the POPULATION and false of the REPRESENTATION -- it recomputes DSI's BAG
floor. Off disk: `BAR_MAX_FLOOR_AUC = 0.5431`; `U1_TYPED_CONTEXT` 0.6669 [0.6184,0.7136] `ABOVE_BAR`,
`U3_ROLE_ONLY` 0.6466, `T2` 0.6128, `U1_COVERAGE_MATCHED` 0.6669 all `ABOVE_BAR`.
Arc-native rebuild (`bfc0e941c`): attestation floor **0.6317 [0.5820,0.6781]**.
**Status: SUSPENDED.** Already correctly retracted by the Director in `2b49c9dbc`.

### B. `exp_typed_role_selectional_asset_writerule_v1` -- 7 arms (**NEW -- NOT PREVIOUSLY FLAGGED**)
Landed `c1d2bc80e`. **No fixing commit is an ancestor** (only one commit ever touched it).
Representation, from its own docstring L79-83: `T1_TYPED_ROLE` = `word x (verb,ROLE) count matrix`
-> `build_ppmi` -> TruncatedSVD 128 -> L2. **A typed-slot representation, not the bag store.**
Deciding lines -- docstring L101 and code L664:
```
BANDS. Bar = max(4 floor AUCs) = 0.5431 (F_CONSTANT_PROTOTYPE), NOT 0.5.
```
```python
bar = max(gate["measured"][f] for f in FLOOR_NAMES)      # gate == DSI's cached BAG floors
```
Off disk (`data/exp_typed_role_selectional_asset_writerule_v1/metrics.json`):
`BAR_MAX_FOUR_FLOORS = 0.5431`; `MARGINS = {"T1_vs_bar_0.5431": 0.0371, "T1_vs_chance_0.5": 0.0802}`.

**Independent representation-native corroboration, computed from THIS cell's own arms (nothing
imported):** its two must-fail identity controls sit **ABOVE the imported bar** --
`N1_LABEL_PERMUTED` **0.5516** [0.5004,0.6025] and `N3_MAGNITUDE_PERMUTED` **0.5630** [0.5108,0.6153]
vs bar 0.5431. A label-permuted null cannot legitimately clear the bar. So this representation's true
floor is **at least ~0.55-0.56**, and the imported bar is too LOW -- same direction and comparable
magnitude to the arc rebuild in cell A. *This is the second independent demonstration that DSI's bag
floors under-state the floor on a typed/structured representation.*

**SUSPENDED: `"T1_TYPED_ROLE clears the bar by +0.0371"`.**
**NOT SUSPENDED, and I want this stated plainly so the cell is not over-punished:** the headline
verdict `WORD_SELECTION_NOT_TYPE` rests on WITHIN-cell, SAME-representation contrasts
(`T2_UNTYPED` 0.5900 >= `T1` 0.5802; `N5_COVERAGE_MATCHED` 0.5217) and is **unaffected by the floor
defect**. Also note T1's CI lower bound 0.5296 < 0.5431, so **T1 never CI-separated above even the
too-low bar** -- the mis-gate did NOT manufacture a positive here.

### C. `exp_typed_role_context_human_instrument_v1` -- 4 arms (**NEW -- NOT PREVIOUSLY FLAGGED**)
Landed `16475c9c5`. **No fixing commit is an ancestor.** Arms built on ARC events
(`N_ARC_EVENTS_TOTAL` present in its report). This cell is the *subtlest* case and the clearest
illustration of 6.40's diagnosis, because **it explicitly and sincerely re-derives its bar** -- along
the wrong axis. L484-506:
```python
# ======================= FLOORS RECOMPUTED ON *THIS* POPULATION (never imported) ================
cheap = h3_units[unit_key("SCORES_CHEAP", V4.H3.CODE_VERSION, "full")]
...
res["RECOMPUTED_ON"] = "this population (v3 human, n=%d/cell) -- NOT imported" % n_p
bar = max(floors[f]["auc"] for f in FLOOR_NAMES)
```
Those `SCORES_CHEAP` arrays are v3's floors on the **BAG/incumbent store** (v3 L394/L558/L631,
quoted above). Off disk: `BAR_MAX_FLOOR_AUC_DERIVED_HERE = 0.5943`, **`BAR_OWNING_FLOOR =
"F_SCRAMBLE"`** -- a store-dependent floor, on the bag store, applied to arc arms.
**The provenance string in the landed metrics asserts "NOT imported". It is accurate about
population and misleading about representation. This is exactly branch (iii) made concrete.**

**SUSPENDED: the numeric bar 0.5943 and every margin against it.**
**NOT SUSPENDED: branch (B) itself.** `U1_TYPED_CONTEXT` read **0.4125 [0.3148,0.5138]** -- below
chance, and it failed a bar that we now know was too LOW. A failure against a too-low bar stands *a
fortiori*. The cell's own `POWER_DISCLOSURE` (`u1_ci_halfwidth` 0.0995 > `bar_minus_chance` 0.0943,
`halfwidth_exceeds_bar_minus_chance: true`) already forbids converting this into a capability
statement in either direction -- that discipline was applied correctly and I am not disturbing it.

*Minor observation, NOT a finding, flagged for the Director rather than asserted:* in this cell
`U1_TYPED_CONTEXT` auc **0.4125** and the floor `F_CONSTANT_PROTOTYPE` auc **0.4125** coincide to 4
d.p. (CIs differ: [0.3148,0.5138] vs [0.3164,0.5153]). At n=65/cell the AUC grid is ~1/4225, so
coincidence is plausible. I did **not** verify the underlying score arrays are distinct -- the cell's
`ARMS_MUST_DIFFER` digests cover arm-vs-arm, not arm-vs-floor. Cheap to check; I am not calling it.

---

## WHAT IS CLEAN (branch (ii) locally -- and this is the reassuring half)

**The write-rule ladder already got this right, before anyone noticed the bug.**
`exp_readout_writerule_paradigmatic_v1` L90-92 and L663-668, `exp_readout_writerule_binary_profile_v1`
L105-110, `exp_readout_writerule_selection_axis_v1` L100-102:
```
F_SCRAMBLE and F_CONSTANT_PROTOTYPE are store-DEPENDENT and recomputed on EACH arm's own store
rep["FLOORS_PER_ARM_STORE_DEPENDENT"] = ["F_SCRAMBLE", "F_CONSTANT_PROTOTYPE"]
add("F_CONSTANT_PROTOTYPE__%s" % name, FB.as_constant_matrix(cfv, n_items))
```
Per-arm, per-store floors, named `F_CONSTANT_PROTOTYPE__<arm>`. **This is the correct discipline and
it is already implemented in this repo.** Same for `exp_writerule_step_ladder_v1` (L596) and
`exp_writerule_learned_basis_denominator_gate_v1` (L619), which rebuild floors from their own `mat`.

**Cleared, gated against 0.5 rather than against an imported floor** (a separate, already-known
under-gating issue -- NOT the cross-representation defect, and I am not inflating it into one):
- `exp_corpus_capacity_ppmi_svd_ceiling_v1` -- `0.5431` appears ONLY in `EXPECTED_AUC` (a bit-for-bit
  regression gate reproducing DSI's cached values). STOP-IF (ii) reads `CI-separated ABOVE 0.5`.
- `exp_tuned_count_unsupervised_dissociation_v1` -- STOP-IF (ii) `CI-separated ABOVE 0.5`; verdict
  `STOP_IF_iii_...STAYS_BELOW_0.5`. Its floors block is carried from the bag regression gate and
  labelled `FLOORS_RECOMPUTED_ON_THIS_POPULATION` -- accurate on population, silent on
  representation, but no verdict depends on it.
- `exp_predictive_coding_write_gate_dissociation_v1` -- `0.5431` only in `EXPECTED_AUC`; STOP-IF (i)
  gates on `ABOVE 0.5` plus a rate-matched N1.
- `exp_dissociation_score_instrument_human_v2/v3/v4` -- instrument cells; v2 computes `max(four
  floors)` fresh and says so ("read fresh off disk, never hardcoded"); v4's `0.5431` sits in
  `DSI_EXPECTED_CACHED`, a regression gate, while its own bar is 0.5943 re-derived from v3.

Worth recording, off disk, since it bears on how much the bar was ever worth:
`F_CONSTANT_PROTOTYPE` = 0.5431, CI **[0.4922, 0.5953]**, `band: NOT_SEPARATED_FROM_CHANCE`,
half-width 0.0516. **The number quoted for two days as "THE bar" is a point estimate whose own CI
includes 0.5.**

---

## TRIPLE-CHECK PERFORMED before declaring B and C worse than documented

- **Right file:** both landed, `data/<anchor>/metrics.json` present and read via .venv python.
- **Right version / is a fixing commit already an ancestor?** **NO.** `git log` per path: B has
  exactly one commit (`c1d2bc80e`), C has exactly one (`16475c9c5`). `bfc0e941c` (the arc rebuild)
  is a read-only post-hoc drill over cell **A**'s `units.jsonl` only -- it touched neither B nor C.
- **Right environment:** `.venv/Scripts/python.exe` throughout; never bare `python`.
- **Right corpus:** B = SimpleWiki 737,488-sentence selectional asset (its own corpus confound is
  disclosed in its docstring, independent of this defect); C = v3 human population n=65/cell.
- **Right metric:** `DSI.auc_of` / `DSI.auc_bootstrap` (Mann-Whitney AUC) on BOTH sides in every
  comparison -- no number crossed scorers.
- **Right arm:** B `T1_TYPED_ROLE`; C `U1_TYPED_CONTEXT`.
- **I did NOT import the arc-native 0.6317 into B or C.** That floor belongs to cell A's arc-event
  representation. B's floor evidence is computed from B's OWN must-fail controls; C has no
  representation-native floor at all, which is itself part of the finding.

---

## RULE AMENDMENT THE EVIDENCE SUPPORTS

6.40 proposes: *recompute on the item's own population AND its own representation.* The evidence
supports a sharper, mechanically checkable form already proven out by the write-rule ladder:

> **A floor computed FROM a store must be recomputed FROM THE ARM'S OWN STORE, per arm.**
> `F_SCRAMBLE` and `F_CONSTANT_PROTOTYPE` are store-derived; `F_ORTHOGRAPHIC` and `F_FREQUENCY` are
> not. Only the store-derived pair needs per-arm rebuilding -- which is cheap, and is why the ladder
> could afford to do it.

And from branch (iii): **every floor written to `metrics.json` must carry a `COMPUTED_FROM` field
naming the store/representation, not only the population.** The string
`"this population (v3 human, n=65/cell) -- NOT imported"` was written in good faith and is the exact
shape of claim that hid this defect for two days.

## SCOPE LIMITS OF THIS AUDIT (stated so it is not over-read)

- Covers `experiments/*.py` (5,872 files, exhaustive on the 8 markers listed). A cell that gates
  against a store-derived floor using none of those 8 markers would not appear. I judge this
  unlikely for the DSI family but it is not proven.
- `hdlab/`, `tools/` and `preregs/` were not scanned for floor constants (preregs are out of bounds
  per brief).
- I did not re-run any cell. All numbers above are read off landed `metrics.json` or quoted from
  source, with the deciding line reproduced in each case.
