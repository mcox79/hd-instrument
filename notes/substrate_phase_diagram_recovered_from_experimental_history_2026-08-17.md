# The substrate phase diagram, recovered from what is actually on disk

**Written 2026-08-17. Enumeration and synthesis only -- no experiment was authored, run, or
dispatched for this document.** Every number below was read off a file on disk on 2026-08-17 and the
file path is given. Nothing is quoted from memory, from a summary, or from another agent's report.

This exists because of the owner's answer to BOARD Q15:

> "It's fine to do this - but remember this is the phase diagram. you should run each process at the
> optimal point. there is a TON of data in the experimental history on this - I belive we mapped the
> full phase diagram for a significant portion of operation."

and Q13:

> "we have a phase diagram for substrate - we can set all variables, including dimensionality,
> wherever we want for each process. The brain does some in sparse space, some in dense, and we have
> the ability to change them on the fly."

---

## PART 1 -- THE PLAIN-LANGUAGE ANSWER

### The short version

**The owner's INSTRUCTION is right and is now backed by measurement. The owner's RECOLLECTION of
how much we mapped is stronger than the evidence.** Both halves matter and they point in the same
direction: set the knobs per process, and accept that we only actually know the right setting for
about four of them.

### The one finding that vindicates the instruction

Two experiments, both run at full scale, both finished, measured **opposite best settings for the
same knob** because they were doing different jobs. This is the clearest thing in the whole history
and it is worth stating in ordinary words.

The knob is **how many of the numbers in a memory code are allowed to be non-zero** -- "sparse"
means only a few, "dense" means most or all.

- **Job A: store a lot of things and get one back from a damaged reminder.**
  (`data/exp_capacity_sweet_spot_v2_cpu_v1`, full mode, 3 seeds, 4,096 numbers per code, cue 30%
  corrupted.) When the store is nearly empty, dense works fine: at the lightest load, allowing 10%
  of numbers non-zero gets 0.962 recall. When the store is full, **dense collapses**: at the heaviest
  load the same 10% setting gets **0.002** -- effectively nothing -- while allowing only 1%
  non-zero gets **0.775**. The best setting *moves* as the store fills: 2% -> 1% -> 1% -> 1%.
  **Sparse wins, and the denser you go the harder you fall.**

- **Job B: take a half-remembered cue and find the right address in memory.**
  (`data/exp_sparse_address_dense_value_v1`, full mode, 3,994 items, confidence intervals on every
  point.) Exactly backwards. At 2,048 numbers per code with a partial cue, allowing 0.2% non-zero
  scores **0.0038**; allowing 100% non-zero (fully dense) scores **0.0714**. That is **19 times
  better**, and it is monotone -- every step towards dense helps. **Dense wins, and sparse is a
  catastrophe.**

So: **the same knob, turned in opposite directions, for two different jobs, both measured, both at
full scale.** A single global setting cannot serve both. That is the owner's Q13 point, and we did
not have it stated as measurement until now.

There is a sting in Job B worth naming, because it cuts against something we have been saying: the
design we have been calling `LINK-NOT-RECONSTRUCT` / "sparsify the address, keep the value dense"
predicts that a **sparse** address should win. **In the one cell that measured it, dense won at
every dimension.** The design is not thereby dead -- the cell measured one addressing scheme, not
every possible one -- but the version we specified is currently contradicted by our own data and
should not be built as though it were supported.

### What we actually know the right setting for

Only four settings have an answer that survives the project's own evidence rules. In plain terms:

1. **Sparsity, for the storing-and-recalling job: about 1% non-zero.** Strong.
2. **Sparsity, for the address-lookup job: fully dense.** Strong, with error bars.
3. **Code format, for the two-way word-comparison job: keep the fine detail, do not round to
   plus-or-minus-one.** Worth about 5-6 points, with error bars that exclude zero.
4. **The multiply operator (Hadamard vs HRR vs FHRR): it does not matter, pick the cheapest.** But
   see the warning below -- this one is weaker than it has been quoted as.

### What we do NOT know, despite believing we do

- **Dimensionality has no single answer, and where it has an answer it is job-specific.** On a
  word-comparison job, going from 256 to 1,024 numbers is worth +0.0635 with error bars that
  exclude zero -- real. On the address-lookup job with a half-remembered cue, going from 256 to
  8,192 numbers -- **thirty-two times the memory** -- moves the score from 0.0711 to 0.0716, a gap
  **sixteen times smaller than the measurement's own error bar**. That is not an improvement, it is
  noise. So "raise d from 256 to 1024" is a good idea for one job and a waste for another, and we
  have never written that down.
- **How much of the diagram is filled in: about 1%.** Of 7,804 result files on disk, roughly 59
  vary the dimensionality at all, roughly 21 vary sparsity, and exactly 2 cells vary the expansion
  factor. Everything else fixes every knob and varies something else.

### The warning about the multiply operator

The claim in circulation is that the choice of binding operator is "empirically null at full mode
across two cells and six operators". **I checked it and it is half right in a way that matters.**

The strongest piece of it does reproduce exactly: three cells at full mode
(`data/exp_substrate_binding_op_x_capacity_v1_seed_{7,13,19}`) put Hadamard, HRR and FHRR at the
identical capacity number, 750, with zero shift. **But that cell only tested three capacity values
-- 150, 750 and 1,350.** All three operators landing on 750 means all three landed in the *same
middle bucket of a three-bucket instrument*. That is a resolution limit, not a measured equality.
An instrument with three bins cannot report a difference smaller than a bin.

And the other half does **not** reproduce. The "K\* 500/500/500 with 0.000 separation" figure for
cyclic-shift / permutation / phase-rotation is not what is on disk. The full-mode order-binding
cells give scores of 0.2667 / 0.1833 / 0.2167 (seed 7), 0.2333 / 0.2000 / 0.2333 (seed 13) and
0.2167 / 0.2500 / 0.2000 (seed 19) -- **the winner changes with the seed**, the verdict is
MIDDLE_BAND not null, and no confidence interval is reported anywhere in the file.

Also omitted from the summary: **two operators are not null at all, they are catastrophic.** In
`data/exp_substrate_seqbind_binding_op_family_v2_seed_7` (full mode), the three algebraic operators
score 0.816 / 0.836 / 0.772 while XOR-on-binary scores **0.072** and sum-modulo-N scores **0.000**.
Saying "six operators, null" hides a result that is about as separated as results get.

**The correct statement is:** among the three standard algebraic operators the difference is smaller
than the instrument can see, and we have never built an instrument that could see it; two
non-algebraic operators are decisively worse. "We tested it and it does not matter" and "we have
never been able to tell" are different claims, and only the second is supported.

### What to do with this

1. **Stop asking "what is our sparsity" and "what is our dimensionality".** Ask per job. Two jobs
   already have opposite answers on disk.
2. **The d=256 -> 1024 raise (PLAN.md item 7) is justified for the comparison job and NOT justified
   for the address-lookup job.** Raise it where the comparator runs; leave it alone where the
   addressing runs. That is the concrete cash value of Q15.
3. **Treat the sparsity-vs-load curve as the one real phase diagram we own** and reuse its shape
   rather than re-measuring it.
4. **Do not build "sparsify the address" as currently specified** until the contradiction in Job B
   above is resolved.

Everything from here on is the working: how the count was done, what each cell actually measured,
and which squares of the grid are empty.

---

## PART 2 (a) -- EXACTLY HOW I ENUMERATED, AND HOW MANY ARTIFACTS I COVERED

**Filesystem first, registry never.** No registry, index, capability map or KB query was used to
decide what exists. `director_kb_query.py` was not run (its ingest is livelocked and its answers
are stale). The 2026-06-30 coverage note was read only AFTER the walk, and only as something to
check against -- not as the frame of the audit.

### Step 1 -- the walk

```
os.walk('data'), skipping data/foundation/ (read-only, gitignored, not to be touched)
-> 8,661 directories visited
-> 7,804 files named metrics.json found
-> written to data/_phase_diag_metrics_list.txt
```

This is the denominator for every "N of 7,804" statement below. It is a complete enumeration of
`metrics.json` under `data/`, not a sample and not a search.

### Step 2 -- SHAPE scan #1 (a parameter taking more than one value in one file)

`data/_phase_diag_scan.py`, run over all 7,804 files, 0 read errors. A sweep is defined by SHAPE:
**a substrate parameter that takes two or more distinct values inside the same artifact.** No
verdict string, tier name or anchor name was used, because that vocabulary has drifted from 13 to
444 distinct strings and a keyword scan over it is worthless.

Result: **836 of 7,804 artifacts (10.7%)** contain at least one multi-valued substrate parameter.
Broken down by parameter, and by whether the artifact is full mode:

| parameter | artifacts with >1 value | of those, `run_mode == full` |
|---|---|---|
| code format (bipolar / graded / phasor / int8 ...) | 346 | 160 |
| bundling / cleanup family | 333 | 174 |
| binding operator | 292 | 148 |
| **dimensionality d** | **59** | **25** |
| (seeds -- excluded, a replication not a sweep) | 50 | 31 |
| **write/read sparsity** | **21** | **10** |
| top-k / k-winners | 9 | 4 |
| **expansion factor** | **1** | **1** |

**Read the top three rows with suspicion and the bottom four with confidence.** The format, bundle
and binding regexes match a word anywhere in the file including prose notes and arm labels, so
those counts are UPPER BOUNDS on candidates, not counts of sweeps. The dimensionality, sparsity,
top-k and expansion regexes require a numeric value adjacent to a parameter name, so those are much
closer to real.

Run-mode split of all 836: full 408, smoke 267, none 74, selftest 65, self_test 13, reduced 4,
other 5. **Fewer than half of everything that looks like a sweep was ever run at full scale.**

Collapsing `_smoke` / `_selftest` / `_seed_N` suffixes gives **504 distinct cell families**, of
which **314 have at least one full-mode artifact with a non-terminal verdict** (not a crash, OOM,
timeout, selftest or UNKNOWN).

### Step 3 -- SHAPE scan #2 (an explicit swept-values list)

`data/_phase_diag_scan2.py` parsed all 7,804 files as JSON and looked for a different shape: **a
literal list of two or more values stored under a key whose NAME names a parameter.** This catches
sweeps that scan #1's regexes miss and is independent of prose.

Result: **118 distinct sweep-list key names** across the corpus. That number is itself the finding:
the same axis is stored under a dozen different names, which is exactly why a keyword-first audit
of this corpus fails.

- **Dimensionality is stored under at least 12 different key names:** `N_DIM_sweep` (32 artifacts),
  `cap_dims` (4), `ORTHO_DIMS` (4), `dims` (3), `dims_list` (2), `ndims` (2), `dim_lever_N` (2),
  `n_dim_grid` (1), `N_DIM_GRID` (1), `NDIM_GRID` (1), `proj_dim_grid` (1), `HOX_AXIS_DIMS` (1).
- **Sparsity under at least 14:** `M_fracs` (32), `m_fracs` (21), `fracs` (17), `density_dial_sweep`
  (16), `SPARSITY_SWEEP` (5), `mfracs` (4), `c_fracs` (3), `sparsities` (3), `kfracs` (2),
  `alpha_fracs` (2), `FRACS` (2), `KCAP_FRACS` (2), `k_fracs` (1), `m_frac_sweep` (1).
- **Expansion factor under 3:** `ACTIVE_EXPANSION_FACTORS` (4), `expansion_factors_active` (4),
  `expansion_factors_canonical` (4) -- all the same **2 cells** plus their smokes.

**The two scans disagree in one place and scan #2 is right.** Scan #1 found only ONE expansion-factor
sweep; scan #2 found the second cell, whose values are stored as a bare list `[8, 64, 512, 4096]`
with no adjacent word "expansion". That cell (`exp_substrate_anisotropy_fly_lsh_expansion_sweep_v2_cpu_path`)
is a completed 3-hour full-mode run and scan #1 missed it. **This is stated because it bounds the
whole document: every count here is a LOWER BOUND, and a sweep hiding behind a name neither scan
matched would not appear.** The bound is checkable -- both scripts are on disk and both name their
match rules.

### Step 4 -- reading the artifacts individually

Every cell that appears in the table in Part 3 was opened and read as JSON, and its own
`run_mode`, `n_items` / `n_anchors` / `n_queries`, floors, confidence intervals, cue regime and
grid resolution were read out of the file rather than inferred. `data/_phase_diag_read.py` is the
reader. Where a cell's verdict text disagrees with its own per-arm numbers, the per-arm numbers
are used and the disagreement is stated.

### What this enumeration does NOT cover, stated so the absence claim is bounded

1. **Only `metrics.json`.** Results stored under any other filename were not enumerated. This is a
   real gap and it bit immediately: the sparsity sweep quoted in the owner's own Q13 note
   (`notes/sparsity_and_dimensionality_..._2026-08-16.md`) lives in
   **`scratch/sparsify_right_object/`** -- four JSON files in a directory that `CLAUDE.md` documents
   as gitignored and periodically wiped by `tools/clear_scratch.py`. It has **no cell under `data/`
   and no `metrics.json` at all.** The single sparsity result the project cites in a load-bearing
   note is one maintenance pass away from not existing.
2. **`data/foundation/` was not walked** (read-only, no backup, gitignored -- instructed not to touch).
3. **Remote-only landings** that never synced to local disk are invisible to a local walk.
4. **`preregs/`, `notes/` and `hdlab/` were not enumerated** as result sources; they are design and
   prose, not measurement.


---

## PART 3 (b) -- THE TABLE: PARAMETER x OPERATION -> OPTIMAL VALUE

### The evidence classes, defined before use

| class | meaning |
|---|---|
| **A** | Full mode; its OWN floors recomputed on its own population; confidence intervals on the MARGIN; cue regime stated; n >= 1,000. Actionable. |
| **B** | Full mode; floors OR intervals but not both, or multi-seed spread reported instead of an interval. Directional. |
| **C** | Full mode, but NO floor and NO interval on the margin. **A ranking of noise until proven otherwise.** Use only for the sign of a large effect, never for a small one. |
| **D** | Smoke mode, gate-failed, terminal (crash/OOM/selftest), or output existing only in `scratch/`. **Do not use to set anything.** |

### THE FIRST RULE THIS TABLE OBEYS: these are NOT one diagram

The operations below use **different scorers on different populations against different gold**.
Under the project's own rule a number may not cross scorers or populations. **So this is not one
phase diagram. It is at least five separate diagrams that happen to share parameter names.** They
are printed in one table for convenience and MUST NOT be read across rows.

The five instruments actually in play:

| instrument | scorer | n | pool | gold | cue regime |
|---|---|---|---|---|---|
| **I1 near-neighbour 2AFC** | 2-alternative forced choice, chance 0.5 | 4,000 items / 2,377 anchors | 2 candidates | WordNet dominant-sense sibling as distractor | comparator; neither exact-key nor partial-cue |
| **I2 addressing accuracy** | did the cue address the right slot | 3,994 items | 5,491 anchors, chance 0.000182 | the item's own key | **BOTH regimes measured separately: EXACT_KEY and PARTIAL_CUE** |
| **I3 stored-pattern recall** | fraction of stored patterns recovered from a 30%-corrupted cue | 4,096-dim codes, 3 seeds | the store itself | the stored pattern | corrupted cue, 30% flips |
| **I4 top-1 sequence / pattern-completion retrieval** | top-1 hit on a K-item bundle | 50 queries per grid point | K items | the bound item | exact query |
| **I5 open-vocabulary read-out hit@1** | hit@1 over the full vocabulary | 4,000 items | 5,491 anchors | held-out word | exact-key and partial-cue |

---

### DIMENSIONALITY d

| operation (instrument) | values swept | OPTIMUM | margin and its error bar | cue regime | class | evidence |
|---|---|---|---|---|---|---|
| near-neighbour comparison (I1) | 256, 1024 | **1024** | +0.0635 CI [+0.0477,+0.0790] quantised code; +0.0515 CI [+0.0380,+0.0650] graded. Own scrambled floors 0.4845-0.5095, frequency baseline 0.4803. 5 projection draws, between-draw sd 0.0060-0.0068 | comparator | **A** | `data/exp_capacity_vs_format_2x2_livepath_v1/metrics.json` |
| near-neighbour comparison (I1) | 256, 1024, 4096 | **4096**, monotone, no plateau found | NEAR accuracy quantised [0.6395, 0.7030, 0.7380], graded [0.6980, 0.7495, 0.78225]. **No CI is reported on the d-to-d deltas** -- the published CI is on the near/far GAP, a different quantity | comparator | **B** | `data/exp_capacity_ceiling_near_far_v1/metrics.json` |
| addressing from a PARTIAL cue, DENSE code (I2) | 256, 2048, 8192 | **NO OPTIMUM -- indistinguishable** | 0.0711 / 0.0714 / 0.0716. CIs [0.0633,0.0789] / [0.0636,0.0791] / [0.0636,0.0796]. Half-width 0.0078. **Margin 256 to 8192 = 0.0005, one sixteenth of its own error bar.** 32x the memory buys nothing | **PARTIAL_CUE** | **A** | `data/exp_sparse_address_dense_value_v1/metrics.json` |
| addressing from a PARTIAL cue, SPARSE code a_write=0.002 (I2) | 256, 2048, 8192 | **8192, decisively** | 0.0005 to 0.0030 to 0.0160 with a symmetric read; 0.0005 to 0.0183 to 0.0493 at a_read=0.2. **32x the score.** CIs non-overlapping | **PARTIAL_CUE** | **A** | same file |
| addressing at the EXACT key (I2) | 256, 2048, 8192 | **saturated -- the question is void** | every configuration except d=256 at a_write=0.002 reads exactly **1.0000**, CI [1.0000,1.0000] | **EXACT_KEY** | **A**, but a ceiling | same file |
| KG-store retrieval MRR | 1024, 2048, 4096, 8192 | **8192** | ORACLE MRR 0.0231 / 0.1180 / 0.4135 / 0.7806, a 33.8x climb. **The headline 33.8x is the ORACLE curve. The NATIVE curve is 0.0140 / 0.0243 / 0.0377 / 0.0518 -- a 3.7x climb ending at 0.0518.** 3 seeds, no CI | exact query | **B** oracle / **C** native | `data/exp_kg_store_dim_scaling_ceiling_v1/metrics.json` |
| sequence-binding N-scaling law | 8192 and others | **UNUSABLE** | `HARD_FAIL_POSITIVE_CONTROL_REGRESSION`: the cell's own positive control missed its target by 1.000 log2 against a 0.5 tolerance | -- | **D** | `data/exp_substrate_seqbind_N_dim_scaling_law_v1_seed_7/metrics.json` |

**The dimensionality verdict in one line: d matters a great deal for the comparator and for sparse
addressing, and not at all for dense addressing.** Those are not contradictory results; they are
three different jobs. There is no global best d, and the history never found one.

---

### WRITE SPARSITY a_write

| operation (instrument) | values swept | OPTIMUM | margin and its error bar | cue regime | class | evidence |
|---|---|---|---|---|---|---|
| store-many-and-recall (I3) | 0.002, 0.01, 0.02, 0.05, 0.1 at loads 0.1 / 0.5 / 1.0 / 2.0, N=4096 | **about 0.01, and it MOVES with load** | per-load best 0.020 then 0.010, 0.010, 0.010. **At load 2.0: f=0.100 gives 0.002, f=0.050 gives 0.153, f=0.020 gives 0.482, f=0.010 gives 0.775, f=0.002 gives 0.721.** Best single fixed f=0.010, worst-load gap to the oracle 0.019. 3 seeds, per-load seed cv 0.029-0.558. **No CI** | 30%-corrupted cue | **B** | `data/exp_capacity_sweet_spot_v2_cpu_v1/metrics.json` |
| addressing from a PARTIAL cue (I2) | 0.002, 0.01, 0.05, 0.2, 1.0 crossed with d=256 / 2048 / 8192 | **1.0, fully dense, at every d** | at d=2048: 0.0030, 0.0203, 0.0501, 0.0661, 0.0714 -- monotone. **19x from sparsest to densest, CIs non-overlapping across the range.** 3 projection draws at d=2048, between-draw sd 0.0009-0.0023 | **PARTIAL_CUE** | **A** | `data/exp_sparse_address_dense_value_v1/metrics.json` |
| addressing at the EXACT key (I2) | same | **anything at or above 0.01** | 0.01 and above all read 1.0000. Only a_write=0.002 at d=256, which is ONE active unit, fails -- at 0.1024 | **EXACT_KEY** | **A**, ceiling | same file |
| open-vocabulary read-out hit@1 (I5) | 0.002 through 0.5 | **NO ARM CLEARS ITS FLOOR** | best sparsified arm f=0.100 scores 0.0774 CI [0.0691,0.0859] against dense 0.0744 CI [0.0663,0.0826] -- **overlapping, NOT separated.** Both sit BELOW the zero-query-information constant floor 0.1390 CI [0.1282,0.1495] | EXACT_KEY; the partial-cue arms are NOT_SEPARATED | **D** -- the output exists only in `scratch/`, which is gitignored and periodically wiped | `scratch/sparsify_right_object/decisive.json` and `.../verdict_metrics.json` |

**THE HEADLINE OF THE WHOLE DOCUMENT IS IN THIS BLOCK.** Rows 1 and 2 are both full mode, both
class A or B, and they point in **opposite directions on the same parameter**. Sparse beats dense
by a factor of 380 at heavy load for recall (0.775 against 0.002). Dense beats sparse by a factor
of 19 for partial-cue addressing (0.0714 against 0.0030). **Per-process settings are not a
preference here; they are forced by the data.**

Note what row 2 does to the `LINK-NOT-RECONSTRUCT` design, which says sparsify the address and keep
the value dense. Row 2 measured exactly that, and **the sparse address lost, monotonically, at every
dimension.** The idea is not refuted in general -- one addressing scheme was tested, not all of them
-- but it is not currently supported by our own evidence and must not be built as if it were.

---

### READ SPARSITY a_read, and the write / read asymmetry

| operation (instrument) | values swept | OPTIMUM | margin and its error bar | cue regime | class | evidence |
|---|---|---|---|---|---|---|
| addressing from a PARTIAL cue (I2) | a_read in {symmetric, 0.2, 1.0} crossed with a_write | **read DENSER than you wrote, whenever the write is sparse** | at d=8192, a_write=0.002: symmetric read 0.0160, a_read=0.2 gives 0.0493, a_read=1.0 gives 0.0551 -- **3.4x for reading denser than writing.** At d=256, a_write=0.05: symmetric 0.0135 against a_read=1.0 at 0.0366 -- **2.7x.** CIs non-overlapping in both | **PARTIAL_CUE** | **A** | `data/exp_sparse_address_dense_value_v1/metrics.json` |
| addressing from a PARTIAL cue, DENSE write (I2) | same | **the asymmetry buys nothing once the write is dense** | at a_write=1.0, d=8192: a_read=0.2 gives 0.0716, a_read=1.0 gives 0.0709, symmetric gives 0.0709 -- all inside one CI half-width of 0.0078 | **PARTIAL_CUE** | **A** | same file |

**This is the only genuinely two-regime measurement in the history** -- `REGIME_PER_ORGAN` is an
explicit field in that file. Its finding is narrower than the slogan: the asymmetry helps a lot when
the key is sparse and not at all when the key is dense. Since dense keys win outright under a
partial cue, **the asymmetry's practical value at the current operating point is zero.**

---

### CODE FORMAT: graded real, sign() bipolar, binary

| operation (instrument) | values swept | OPTIMUM | margin and its error bar | cue regime | class | evidence |
|---|---|---|---|---|---|---|
| near-neighbour comparison (I1) | graded against sign(), at d=256 and d=1024 | **graded, at both d** | +0.0585 CI [+0.0422,+0.0745] at d=256; +0.0465 CI [+0.0320,+0.0605] at d=1024. Own scrambled-context floors 0.4845-0.5095, frequency baseline 0.4803. Paired item bootstrap, 5 projection draws | comparator | **A** | `data/exp_capacity_vs_format_2x2_livepath_v1/metrics.json` |
| addressing from a PARTIAL cue (I2) | signed against binary at d=2048 | **not separated** | binary against signed: 0.0015/0.0030 at a_w 0.002, 0.0200/0.0203 at 0.01, 0.0521/0.0501 at 0.05, 0.0669/0.0661 at 0.2, 0.0681/0.0714 at 1.0. **Every gap is inside the 0.0078 CI half-width and the SIGN of the gap flips across the sweep** | **PARTIAL_CUE** | **A** | `data/exp_sparse_address_dense_value_v1/metrics.json` |
| open-vocabulary read-out hit@1 (I5) | graded/signed field crossed with graded/signed query | **NO NUMBER MAY BE QUOTED** | the cell's own pre-registered validity gate PV6 FAILED and it says so: *"pre-registered validity gates FAILED ... NO quality number is published"*. The arms happen to read 0.0480 / 0.0465 / 0.0455 / 0.0440, a spread of 0.004 -- do not use them | both | **D** | `data/exp_readout_sign_cue_overlap_curve_v1/metrics.json` |
| pattern-completion recall, the "1-bit substrate" claim | float against bipolar | **claims bipolar +0.050 -- DISREGARD** | `run_mode: smoke`, `n_seeds: 1`, **elapsed 0.368 seconds**, no floors, no CI, a single arm pair -- and it carries the verdict `HARD_PASS` | unstated | **D** | `data/exp_bipolar_quantization_quality_cpu_v1/metrics.json` |
| encoder family: binary-bipolar, HRR-real, FHRR, sparse-bipolar, sparse-real | 5 encoders crossed with an N_DIM sweep | **all five tied, "COMPETITIVE"** | 90 of 90 points, 5 of 5 pass the chain-grade bar, 7 of 10 pairs "differ". `n_seeds: 1`, **elapsed 3.23 s**, no CI. An earlier version of the same cell put sparse-bipolar as DOMINATED; v3 does not | unstated | **C** | `data/exp_substrate_anchor4_encoder_family_phase_diagram_v3_seed_7/metrics.json` |

**Format verdict:** graded beats sign() on the comparator by 5 to 6 points with error bars that
exclude zero. That is the one solid format result. It does **not** transfer to addressing, where it
was measured and came out not separated, and it is **unmeasured** on read-out, where the gate failed.
**The smoke cell that has been justifying sign() quantisation runs for 0.368 seconds on one seed
with no controls, and two full-mode cells since have measured the opposite sign on the comparator.**

---

### BINDING OPERATOR

| operation (instrument) | operators | OPTIMUM | margin and its error bar | grid resolution | class | evidence |
|---|---|---|---|---|---|---|
| working-memory capacity cliff (I4) | Hadamard, circular-convolution HRR, FHRR | **none -- all identical** | K_cliff **750 / 750 / 750**, shift 0.0, reproduced on 3 seeds | **`M_per_bank` was swept over only [150, 750, 1350]** -- a three-bin instrument, and all three operators fell in the middle bin. **A resolution limit, not a measured equality** | **C** | `data/exp_substrate_binding_op_x_capacity_v1_seed_{7,13,19}/metrics.json` |
| pattern completion (I4) | circ-conv, FHRR, Hadamard, outer-product tensor | **outer-product is WORSE; the other three are tied** | top-1 means over 48 grid points, 3 seeds: circ-conv 0.4183 / 0.4125 / 0.4133, Hadamard 0.4125 / 0.4125 / 0.4192, FHRR 0.4100 / 0.4058 / 0.4042, **outer-product 0.3583 / 0.3575 / 0.3392**. The top three swap ranks between seeds. No CI | 48 points, N crossed with corruption | **C** for the trio; **B** for the outer-product gap | `data/exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_{7,13,19}/metrics.json` |
| sequence binding (I4) | Hadamard, circ-conv HRR, tensor product, XOR-on-binary, sum-mod-N | **XOR and sum-mod-N are CATASTROPHIC; the other three are tied** | top-1 means: Hadamard **0.816**, circ-conv **0.836**, tensor **0.772**, XOR **0.072**, sum-mod-N **0.000**. K_cliff 500 / 500 / 500 against 50 / 50. **n = 50 queries per grid point and no CI**; the binomial standard error at n=50 near p=0.8 is about 0.056, and the trio's whole spread is 0.064 | K_SEQ [50, 100, 200, 500, 1000] | **C** for the trio; decisive in magnitude for the XOR and sum-mod-N collapse | `data/exp_substrate_seqbind_binding_op_family_v2_seed_{7,13,19}/metrics.json` |
| order binding (I4) | cyclic shift, random permutation, phase rotation | **none -- the winner changes with the seed** | discrimination points, seed 7: **0.2667 / 0.1833 / 0.2167**; seed 13: **0.2333 / 0.2000 / 0.2333**; seed 19: **0.2167 / 0.2500 / 0.2000**. Max pair difference 0.083 / 0.033 / 0.050. Verdict MIDDLE_BAND on all three. **No CI anywhere in the file** | L crossed with K; discriminator at L=4, K=250 | **C** | `data/exp_substrate_order_binding_family_v2_seed_{7,13,19}/metrics.json` |

**Binding verdict:** among Hadamard, HRR and FHRR, nothing has ever been measured that COULD
distinguish them -- the instruments used had three capacity bins, fifty queries per point, and no
confidence intervals. **That is "we cannot tell", not "there is no difference".** Two operators,
XOR on 0/1 binary and sum modulo N, are decisively unusable, and THAT result is trustworthy because
the gap is 0.836 against 0.000.

---

### EXPANSION FACTOR

| operation | values swept | OPTIMUM | margin and its error bar | class | evidence |
|---|---|---|---|---|---|
| fly-LSH anisotropy correction | 8, 64, 512, 4096 | **512** | 0.509, 0.575, 0.609, 0.611 -- monotone, 3 seeds, per-point cv 0.007-0.013. **4096 buys +0.002 over 512, which is smaller than the cv.** And the A/B control at 4096x scores **0.601** against the treatment's 0.611 -- a gap of 0.010 against a cv of about 0.010, so **the control nearly reproduces the effect at the top of the range.** A 10,743-second run | **B** | `data/exp_substrate_anisotropy_fly_lsh_expansion_sweep_v2_cpu_path/metrics.json` |
| the same, on the GPU path | 5, 64, 512, 4096 | **UNUSABLE** | `HARD_FAIL_OOM_AT_EXPANSION_4096` -- 64x, 512x, 4096x and the A/B control all returned `nan`. Only 5x computed, at 0.9987, and the cell itself flags that as suspect saturation | **D** | `data/exp_substrate_anisotropy_fly_lsh_expansion_ratio_sweep_v1/metrics.json` |

**These two cells are the ENTIRE expansion-factor history.** No other cell on disk varies it.

---

### CLEANUP AND BUNDLING

| operation | families swept | OPTIMUM | margin and its error bar | class | evidence |
|---|---|---|---|---|---|
| working-memory multi-bank recall | no-cleanup, classical Hopfield, modern Hopfield continuous, iterative attractor, k-NN lookup | **NO CLEANUP** | mean recall over 50 grid points, K_per_bank 50 to 1000, 8 banks, N=4096, RANDOM and ADVERSARIAL regimes: **no_cleanup 0.4229**, modern Hopfield 0.4139, **classical Hopfield 0.0261**. Cliff K_per_bank 250 for the competitive families against 50 for classical Hopfield. `n_seeds: 1`, no CI | **C** for no-cleanup against modern Hopfield, a gap of 0.009 which is meaningless; **B** for "classical Hopfield is broken", 0.4229 against 0.0261 | `data/exp_exp_substrate_cleanup_family_wm_kcliff_v1p1_seed_7/metrics.json` |
| open-vocabulary read-out | modern Hopfield one-shot | **DO NOT USE -- its output is a constant** | pairwise cosine between the retrieved vectors of DIFFERENT items: minimum **0.99984**, mean **0.99997**. Cosine of the retrieved vector to the population-mean direction: **0.99897**. It scores 0.139 at hit@1 **because it IS the constant-prototype floor**, not because it retrieves anything | **B**, decisive by construction | `scratch/sparsify_right_object/decisive.json` |

**Cleanup verdict: adding a cleanup step has never bought anything measurable, and two of the five
families are actively harmful.** Classical Hopfield destroys recall, 0.026 against 0.423. Modern
Hopfield one-shot returns essentially the same vector for every query. **"No cleanup" is both the
incumbent and the best-measured option.**

---

## PART 4 (c) -- THE EMPTY CELLS OF THE DIAGRAM. THIS IS THE BUILD BACKLOG.

Seven parameters crossed with the six operations named in Part 3 gives **42 squares**. Here is
every one of them, with what is actually in it.

Legend: **A** / **B** = usable, **C** = directional only, **D** = a result exists but must not be
used, **--** = **NEVER MEASURED**.

| parameter | I1 comparator | I2 addressing PARTIAL cue | I2 addressing EXACT key | I3 store-and-recall | I4 bundle retrieval | I5 open-vocab read-out |
|---|---|---|---|---|---|---|
| **dimensionality d** | A | A | A (ceiling) | **--** | C | **--** |
| **write sparsity a_write** | **--** | A | A (ceiling) | B | **--** | D |
| **read sparsity a_read** | **--** | A | A | **--** | **--** | **--** |
| **code format** | A | A | A | **--** | C | D |
| **binding operator** | **--** | **--** | **--** | **--** | C | **--** |
| **expansion factor** | **--** | **--** | **--** | **--** | **--** | **--** |
| **cleanup / bundling** | **--** | **--** | **--** | B | C | B |

**Tally: 13 of 42 squares are usable (10 class A, 3 class B). 4 more are directional only.
2 hold results that must not be used. 23 of 42 -- more than half the diagram -- have never been
measured at all.**

### The five biggest holes, in the order I would fill them

**1. THE BINDING OPERATOR HAS NEVER BEEN VARIED ON ANY OPERATION WE CURRENTLY CARE ABOUT.**
This is the biggest empty cell in the diagram and it is not close. All four binding-operator cells
score on ONE instrument: top-1 retrieval from a bundle (I4), with 50 queries per point and no
confidence intervals. **Zero binding cells score on the comparator, zero on addressing, zero on
open-vocabulary read-out.** Yet "the binding operator is empirically null" is being used to close
the question for the whole substrate. It has been measured on one job, coarsely, and the current
programme does not run on that job. **Five of the six squares in that row are blank, and the sixth
is class C.**

The sharp version: our core operation -- the multiply that binds a role to a filler -- has never
been varied on the read-out that our headline number comes from.

**2. THE EXPANSION FACTOR ROW IS COMPLETELY BLANK.**
Two cells exist in the entire history. One crashed with an out-of-memory error at three of its four
points. The other ran for three hours on a fly-LSH anisotropy scorer that is not any of the six instruments
in Part 3, and found the effect plateaus at 512x with an A/B control almost reproducing it. **No
expansion result exists on ANY of the six instruments in the table** -- meaning it cannot be
compared to any other parameter's optimum without crossing scorers, which is barred. Given that expansion
is the operation the dentate gyrus is supposed to be doing, and given that "sparse expanded address"
is the shape of the design we keep proposing, this row being empty is a real gap and not a
bookkeeping one.

**3. NOTHING CROSSES DIMENSIONALITY WITH THE STORE-AND-RECALL JOB.**
Every sparsity-versus-load number we own is at **N=4096 and only N=4096**. So the sentence
"the best sparsity is about 1%" is really "the best sparsity is about 1% at N=4096", and we do not
know whether that 1% is a property of the job or a property of that one N. This matters immediately:
if the optimum is really "a fixed NUMBER of active units" rather than "a fixed FRACTION", then the
1% figure is wrong the moment d changes, and the d=256-to-1024 raise would silently move us off the
optimum. **One 2-D sweep (d crossed with f, at fixed load) closes this, and it has never been run.**

**4. READ SPARSITY EXISTS ONLY INSIDE ONE CELL.**
The write/read asymmetry -- the one live positive result in the current programme -- has been
measured on exactly one instrument, addressing, in exactly one cell. **Four of its six squares are
blank.** In particular nobody has ever asked whether reading denser than you wrote helps the
store-and-recall job, which is the job where sparsity demonstrably matters most.

**5. FORMAT HAS NEVER BEEN TESTED AS A THREE-WAY.**
The comparator cell tests graded against sign(). The addressing cell tests signed against binary.
**No cell anywhere tests the FHRR phasor / complex format against either of them on any of the six
instruments.** The encoder-family cell nominally includes FHRR, but it runs for 3.23 seconds on one
seed with no confidence intervals and reports all five encoders as tied, which is what an instrument
with no resolution reports. So the three-way format question -- bipolar against graded real against
phasor, the actual question -- **is unanswered.**

### Two more holes worth naming

- **No cell crosses TWO substrate parameters at full mode with floors and CIs, except one.**
  `exp_sparse_address_dense_value_v1` crosses d, a_write, a_read and code format in one 120-cell
  grid with intervals. It is the only artifact of its kind in 7,804. Everything else varies one knob
  and pins the rest, which is exactly why we have no interaction terms.
- **Load is a swept variable in only one cell.** `exp_capacity_sweet_spot_v2_cpu_v1` sweeps load and
  finds the optimum MOVES with it. Nothing else in the history sweeps load, so we do not know
  whether any other optimum in this document is load-dependent -- and one of them demonstrably is.

---

## PART 5 -- THE SMOKE / FULL DISAGREEMENTS I FOUND WHILE DOING THIS

`--smoke` in `argv` silently switches the imported ruler to a reduced vocabulary and corpus. This is
not a hypothetical hazard; **the smoke and full runs of the same cell reach opposite conclusions,
repeatedly.** Every pair below is two files on disk from the same anchor.

| cell | SMOKE says | FULL says |
|---|---|---|
| `exp_substrate_binding_op_x_capacity_v1` | `HARD_PASS`, "3-op-distinct", FHRR **0.90** against Hadamard **0.40** -- a 2.25x operator effect | `HARD_FAIL`, "capacity invariant", K_cliff **750/750/750**, shift **0.0** |
| `exp_substrate_seqbind_binding_op_family_v2` | `HARD_PASS_SMOKE`, K_cliff **1000/1000/1000** | `HARD_FAIL`, K_cliff **500/500/500** -- the smoke overstates capacity by **2x** |
| `exp_substrate_pc_hierarchy_fair_harness_v1` | `HARD_FAIL` | `HARD_PASS` |
| `exp_capacity_vs_format_2x2_livepath_v1` | at n=150: `NO_READ_FLOOR_INVALID`; at n=600: agrees with full | `BOTH_CAPACITY_AND_FORMAT` |
| `exp_bipolar_quantization_quality_cpu_v1` | `HARD_PASS`, +0.050 for bipolar, **0.368 s, one seed** | **there is no full run.** This cell has been load-bearing for the sign() choice |

**267 of the 836 sweep-shaped artifacts are smoke mode, against 408 full.** Any statement of the
form "we swept X and found Y" has roughly a one-in-three chance of resting on a smoke run unless the
`run_mode` field was actually checked.

---

## PART 6 (d) -- THE HONEST HEADLINE

### Is there a mapped phase diagram in the history?

**No -- not as a single mapped diagram, and not for "a significant portion of operation".**
But the recollection is not baseless, and the part of it that IS true is the operationally important
part.

**What is true:**

- We own **one genuine multi-parameter phase diagram with confidence intervals**: the 120-point
  d x a_write x a_read x code grid in `exp_sparse_address_dense_value_v1`, measured in BOTH cue
  regimes, with a random-address control at every point. It is real and it is recent.
- We own **one genuine parameter-by-load phase diagram**: sparsity crossed with load in
  `exp_capacity_sweet_spot_v2_cpu_v1`, 3 seeds, full mode, where the optimum visibly moves.
- **Those two together prove the owner's Q13 claim as measurement, not assertion.** The same knob
  has opposite optima on two different jobs. That is exactly "the brain does some in sparse space,
  some in dense", demonstrated in our own data.
- Roughly **13 of 42 parameter-by-operation squares** have a usable answer. That is not nothing; it
  is a real asset that was not written down anywhere in one place before this document.

**What is not true:**

- **"We mapped the full phase diagram."** Of 7,804 result files, about **59** vary dimensionality at
  all and about **21** vary sparsity. **Two cells in the entire history vary the expansion factor.**
  More than half the parameter-by-operation grid has never been measured once.
- **"The phase diagram" is singular in the recollection and plural in the evidence.** The results
  live on at least six different scorers with different populations, pools and gold. Under the
  project's own rules they cannot be merged. Anyone who reads them as one surface will
  transfer a number across scorers, which is the fault that has cost this project the most.
- **Most of what looks like a sweep is a ranking of noise.** Of the 42 squares, only 13 carry a
  margin with an error bar. The binding-operator squares in particular carry no intervals at all,
  and the instruments used could not have resolved the differences being declared absent.

### Where the recollection most likely comes from, checked

`notes/director_TRUE_PHASE_DIAGRAM_COVERAGE_2026-06-30.md` exists, is titled "TRUE phase diagram
coverage", and estimates **"~55-60% -> 60-65%"** overall coverage across a 16-axis taxonomy. **That
note is very probably the source of the memory, and reading it carefully supports this document
rather than contradicting it.** Its own rows say:

- Axis B, N dimensionality: *"Outer ~10%; Inner: dominantly N=8192"*, with *"None directly"* under
  outer-axis chain-grade cells.
- Axis C, sparsity: *"None"*, *"Single value per cell"*, coverage ***"<5%"***.
- Cross-products of any two axes: ***"<5%. Nearly all cells fix 13 axes and sweep 1-3."***
- Its own "highest-priority gaps" list, item 5, is literally *"N-dimensionality sweep as a free axis
  -- currently always fixed."*

So the note's headline percentage is an average over sixteen axes on a self-assessed scale, and its
own line items put **the two axes the owner names in Q13 -- dimensionality and sparsity -- at 10%
and under 5%.** The high-level number was carried forward in memory; the line items were not.
**This document is the line items, re-measured from disk fourteen months of work later.**

### The one-sentence answer to Q15

**"Run each process at the optimal point" is exactly right and is now evidenced; but we only know
the optimal point for about a third of the process-parameter pairs, we have never once varied the
binding operator on any operation the current programme runs on, and the biggest single lever the
owner asked about -- dimensionality -- has an answer that is job-specific and, for the job the
programme is currently blocked on, is "it makes no measurable difference".**

---

## APPENDIX -- reproducing this document

Five scripts, all re-runnable. They were written under `data/`, which `.gitignore` line 43 excludes
(`data/*`), so **tracked copies live in `tools/phase_diagram_recovery/`** -- otherwise this document
would cite provenance into a directory git does not keep. Run them from the repo root.

| tracked script | working copy | what it does |
|---|---|---|
| `tools/phase_diagram_recovery/scan1_multivalued_param.py` | `data/_phase_diag_scan.py` | SHAPE scan #1: a parameter taking >1 value inside one artifact. Reads `data/_phase_diag_metrics_list.txt`, writes `data/_phase_diag_scan_out.jsonl` |
| `tools/phase_diagram_recovery/scan2_explicit_sweep_lists.py` | `data/_phase_diag_scan2.py` | SHAPE scan #2: an explicit swept-values list under a parameter-named key. Writes `data/_phase_diag_scan2_out.txt` |
| `tools/phase_diagram_recovery/analyze_families.py` | `data/_phase_diag_analyze.py` | collapses artifacts into cell families; writes `data/_phase_diag_families.txt` |
| `tools/phase_diagram_recovery/read_cell.py` | `data/_phase_diag_read.py` | the per-cell reader used for every number in Part 3 |
| `tools/phase_diagram_recovery/verify_kcliff_claim.py` | `data/_phase_diag_750.py` | the targeted off-disk check of the 750/750/750 binding claim |

`data/_phase_diag_metrics_list.txt` holds the full enumeration of all 7,804 `metrics.json` paths and
is the denominator for every count here. Regenerate it with `os.walk('data')` skipping
`data/foundation/`; the walk visits 8,661 directories and takes about three minutes.

**Corrections this document makes to things currently written down elsewhere**, each verified on
disk today:

1. `notes/COMPACTION_HANDOFF_2026-08-17.md` section 8b(D) states *"K\* 500/500/500 for
   cyclic-shift / permutation / phase-rotation with 0.000 separation."* **That does not reproduce.**
   The full-mode order-binding cells report discrimination points that differ between operators and
   whose ranking changes with the seed; the verdict is MIDDLE_BAND, not null; and 0.000 appears once,
   for one pair, in one seed.
2. The same section says the binding-operator choice is *"empirically null at full mode across two
   cells and six operators."* **The 750/750/750 half reproduces exactly, but on a three-value
   capacity grid**, and the summary omits that two of the operators are catastrophically worse
   (0.072 and 0.000 against about 0.8).
3. The sparsity sweep cited in
   `notes/sparsity_and_dimensionality_are_per_process_not_one_global_setting_owner_2026-08-16.md`
   **has no cell under `data/` and no `metrics.json`.** It lives in `scratch/sparsify_right_object/`,
   which `CLAUDE.md` documents as gitignored and periodically cleared by `tools/clear_scratch.py`.
   Per the repo's own rule -- *"if a durable file cites a scratch script as the provenance of a
   number, promote it"* -- that cell should be promoted to `experiments/` before the next
   scratch clear.
