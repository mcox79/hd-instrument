# PRE-REG: CAPACITY vs FORMAT, the 2x2, on the live path

Filed 2026-08-14, BEFORE any arm was scored. Branch `dataprep/mcguffey-graded-corpus`.
Cell `experiments/exp_capacity_vs_format_2x2_livepath_v1.py`. Anchor
`exp_capacity_vs_format_2x2_livepath_v1`.

## 0. HONESTY STATEMENT -- THIS IS A WIRE-IT TEST, NOT A DISCOVERY

The capability being tested is already measured and already wired default-OFF into `hdlab`
(`context_vector(graded=)`, `ConceptSpace.freeze_graded()`, `ReadoutConfig(graded_query=)`;
witness `542fb7754`). `data/exp_graded_divisive_comparator_v1` HARD_PASSed at d=256 and
`data/exp_capacity_ceiling_near_far_v1` already ran a 2x3 sweep. **Nothing here is expected to be
new science.** The question is narrower and entirely about whether we may turn a default ON:

1. Does the graded gain survive ON THE LIVE PATH (hdlab's own functions, not a re-implementation)
   at a capacity where the quantised comparator is no longer starved -- d=1024?
2. **Is the effect CAPACITY, FORMAT, or BOTH?** If `d` alone explains it, the format story dies
   and the fix is a config change. If format adds beyond `d`, that is architectural.
3. Does either effect survive a **between-projection-draw standard deviation**? A gain smaller
   than the variation between random projection draws is not a gain. The landed-VET showed the
   item bootstrap is structurally blind to this (draw sd ~0.015 invisible to it), so this gate is
   non-negotiable and is reported whatever it says.

**The withdrawn mechanism claim is NOT re-asserted.** `notes/landed_vet_graded_comparator_mechanism_refuted_2026-08-14.md`
reproduced the win bit-exactly and then withdrew the explanation (per-component magnitude
destruction is NOT the binding constraint: term-space ablation puts magnitude at 27% of the
effect, and unmodified `sign()` at d=1024 beats graded at d=256). This cell measures the
DECOMPOSITION and takes no position on why.

## 1. WHAT IS ON THE LIVE PATH, AND HOW THAT IS PROVEN

Draw 0 -- the projection the substrate actually uses -- is computed by calling **hdlab's own
functions**, not a fork:

| cell | anchors | query |
|---|---|---|
| QUANT | `ConceptSpace(d).observe(context_vector_masked(s, w, d))` then `.anchor_matrix()` | `context_vector_masked(..., d)` |
| GRAD  | `ConceptSpace(d).observe(context_vector_masked(s, w, d, graded=True))` then `.freeze_graded("none")` | `context_vector_masked(..., d, graded=True)` |

Self-test S1 asserts the reusable fast encoder (`exp_capacity_ceiling_near_far_v1._enc`, itself
byte-chained to `exp_graded_divisive_comparator_v1`) is **byte-identical to the hdlab-native
anchor matrices at BOTH d=256 AND d=1024, for BOTH codes**. Only after that assertion is the fast
encoder used, and only for draws 1..4 (the projection-draw control, which hdlab cannot express
because its seed is `sha256(word)` with no draw parameter).

Self-test S2 asserts the 2AFC scorer agrees with `canonicalize_fast` item-for-item at d=256
(read-out non-fork control).

**Scope, stated plainly:** d=1024 is the live CODE with the live config constant `CTX_D` changed.
That is exactly what flipping the capacity default would do, and nothing else in the path differs.

## 2. ARMS

Near-neighbour 2AFC (WordNet dominant-sense sibling distractor), n up to 4000 held-out items,
identical items across every arm.

- `A_d256_QUANT`, `A_d256_GRAD`, `A_d1024_QUANT`, `A_d1024_GRAD` -- the 2x2.
- `F_d256_QUANT_SCRAM`, `F_d256_GRAD_SCRAM`, `F_d1024_QUANT_SCRAM`, `F_d1024_GRAD_SCRAM` --
  in-cell scrambled-context floor at every one of the four cells (donor sentence from a different
  item, both its own words and the target pair masked out).
- `B_FREQ` -- corpus-frequency baseline.
- Draws 1..4: all four 2x2 cells recomputed under 4 INDEPENDENT random projections.

## 3. DISCRIMINATOR AND ITS RANGE

2AFC accuracy, chance 0.50, range [0,1] by construction. The discriminator is failable at every
band: the scrambled arm CAN and previously DID land at chance, and a d-only outcome and a
format-adds outcome produce numerically different, mutually exclusive delta patterns.

## 4. INFERENCE

Arms share items, so **every delta is tested by a PAIRED item bootstrap** (n_boot=5000, seed
20260814) resampling ITEMS and recomputing the difference within the resample.

    F256  = A_d256_GRAD   - A_d256_QUANT          (format at the live capacity)
    F1024 = A_d1024_GRAD  - A_d1024_QUANT         (format at 4x capacity)
    Cq    = A_d1024_QUANT - A_d256_QUANT          (capacity, quantised)
    Cg    = A_d1024_GRAD  - A_d256_GRAD           (capacity, graded)
    INTER = F1024 - F256                          (do they interact)
    HEAD  = A_d1024_GRAD  - A_d256_QUANT          (the full wire-it delta vs the live 0.6395)

**A delta is REAL iff BOTH hold:** its paired-bootstrap 95% CI excludes 0, **AND**
`|delta| >= 2 x sd_between_draws(delta)`, where the draw sd is computed over the 5 projection
draws for that same delta. Reported for every delta whether or not it passes.

## 5. BANDS -- DECLARED HERE, BEFORE ANY ARM RUNS

**VALIDITY GATES. Any failure -> `NO_READ_*`, no interpretation of any delta.**

- G1: all four SCRAM floors within [0.45, 0.55].
- G2: `B_FREQ <= 0.55`.
- G3: `A_d256_QUANT` within +/-0.02 of the landed live value **0.6395**. Outside -> the harness
  drifted, not the hypothesis.
- G4: S1 byte-identity and S2 read-out agreement pass (hard asserts; the cell aborts).

**PRIMARY -- the decomposition. Mutually exclusive, decided by the REAL test in sec 4.**

| verdict | condition |
|---|---|
| `CAPACITY_ONLY` | Cq REAL and positive; F1024 NOT REAL |
| `FORMAT_ONLY` | F1024 REAL and positive; Cq NOT REAL |
| `BOTH_CAPACITY_AND_FORMAT` | both REAL and positive |
| `NEITHER_NULL` | neither REAL |
| `NEGATIVE_DIRECTION` | any REAL delta is negative |

**SECONDARY -- the headline wire-it level, scoped to `A_d1024_GRAD`.**

- `HP` (hard pass): `HEAD >= +0.08`, its CI excludes 0, all validity gates pass.
- `MIDDLE_BAND`: `0 < HEAD < +0.08`.
- `HF` (hard fail): `HEAD <= 0`.

**WIRE GATE -- the default is flipped ON only if ALL of:**

1. primary verdict is `FORMAT_ONLY` or `BOTH_CAPACITY_AND_FORMAT`;
2. F1024 REAL and positive (format still pays at 4x capacity, i.e. it is not a d-proxy);
3. F256 positive with CI excluding 0 (it pays at the capacity the substrate actually runs at,
   which is the only place a flipped default takes effect today);
4. all validity gates pass.

If the gate fails the defaults stay OFF and the report says so. **`CAPACITY_ONLY` is an
acceptable and publishable result** -- it kills the format story and makes the fix a config
change, which is the cheaper and more useful answer.

## 6. WHAT IS NOT CONTROLLED, DECLARED IN ADVANCE

- `hdlab/multi_hop.py`'s degenerate `beta = n_dim` default: **no arm of this cell touches
  `multi_hop`.** Untouched, reported as such.
- `atoms.similarity`'s FHRR/HRR metric split: **this cell compares within ONE representation**
  (real bipolar/graded context vectors, `_cos_rows` throughout). Untouched, reported as such.
- The other 30+ `np.sign` sites named in `notes/ORGAN_MAP.md` sec 1 are untouched. Only the two
  sites on this comparator's path are varied, via the already-wired keyword flags.
- Items come from the same WordNet-sibling construction as the parent cells; no new item claim is
  made.

## 7. ENGINEERING

Threads pinned at the top of the file before `import numpy`. Fresh output dirs
(`data/exp_capacity_vs_format_2x2_livepath_v1`, `..._SMOKE`, `..._SELFTEST`). Per-unit checkpoint
via `tools/exp_checkpoint.py`. `metrics.json` written once via atomic tmp + `os.replace`.
`sorted(set())` throughout. Progress printed with `flush=True` at every stage
(`progress_logging: yes`, required for `timeout_s >= 1800`). `--timeout` 3600 s
(measured parent runtime 381 s for a strictly larger 2x3 sweep; 4x headroom for the extra draws
and the un-cached hdlab-native build).
