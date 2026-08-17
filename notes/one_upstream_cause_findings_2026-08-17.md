# ONE UPSTREAM CAUSE? -- the cue-regime contrast, findings log

**Live file. Updated after EVERY arm.** Started 2026-08-17 at HEAD `258dd96dd`, branch
`dataprep/mcguffey-graded-corpus`. Written by the cell-author agent, working alone (no subagents
spawned, per brief).

**THE HYPOTHESIS UNDER TEST.** Three results are currently read as three separate findings:

1. thematic/additive bridging is a measured NULL (`exp_thematic_..._v2`, B1 rho 0.0270 at n=394);
2. selectional-constraint bridging is a measured NULL and is CI-separated BELOW the incumbent
   (`exp_selectional_constraint_bridge_v1`, S1-I1 = -0.1049 [-0.2041,-0.0057] at n=308) and
   NOT_SEPARATED from a random target (-0.0015 [-0.1391,+0.1361]);
3. the partial cue is capped at ~0.037 even for a circular WordNet ORACLE, while the same pipeline
   reads 0.8787-1.0000 at the exact key.

**The claim: these are ONE finding with ONE upstream cause -- the cue does not carry the target's
identity, so nothing built ON the cue could have worked.**

---

# THE ANSWER, FOR THE NEXT SESSION TO INHERIT

**THE CLAIM IS FALSE, AND WHAT REPLACES IT REVERSES THREE POSITIONS THE PROGRAMME WAS HOLDING.**
Full arithmetic in section 4; every figure below is CI-separated, on a named population, with its
CI half-width beside it, and with a known-answer arm near ceiling and a null arm at chance verified
BEFORE any treatment number was read.

### 1. "THE PARTIAL CUE IS STRUCTURALLY DEAD" -- **WRONG. RETIRE IT.**
It addresses its own item **0.0711 against chance 0.00018 (390x)**, is **+0.0709 +- 0.0080 ABOVE**
a filler with identical marginals, carries a derived **12-18% exact-key-equivalent** against a
measured detection threshold of **5%**, and beats a matched non-informative filler on **7 of 10
rungs in an unbroken run**. *(retrieval instrument, n=3,994 items / 5,491 anchors)*

### 2. THE READ-OUT IS THE CEILING AND IT IS **INDEPENDENT OF THE CUE**.
Hand the system a **perfect** cue -- exact-key addressing **1.0000** -- and hit@1 is **0.0481**,
**CI-separated BELOW** the constant floor **0.1390** (margin **-0.0909 [-0.1034,-0.0786]**, which
is **7.3x its own CI half-width of 0.0124**) and below the spelling floor **0.0873**. **NO rung of
the ladder clears at any cue quality.** So the ~0.037 oracle cap was **TWO defects quoted as one**:
a graded, **non-structural** addressing deficit, and a read-out ceiling that **no cue, translator,
completer or bridge can touch.**

### 3. THE PHASE 2 KILL CONDITION -- **WITHDRAW IT FOR THE THEMATIC BRIDGE; RE-WORD IT FOR THE SELECTIONAL ONE.**
The bridging instrument at n=308 **cannot CI-separate a cue carrying less than 60% of the target's
own exact key.** Measured, not asserted: `lambda_star = 0.60` on **all four ladders**, in **both**
configs, under **all three** definitions. **A cue carrying 45% of the exact key reads
`+0.0854 [-0.0691,+0.2343] NOT_SEPARATED`.**
- **Thematic neighbour-copy carries a derived 23.5-26.1% exact-key-equivalent** -- real
  information, **less than half** what the instrument needs to see. **Its null is a POWER
  statement. The kill does not hold on it.**
- **Selectional carries 0.0-2.6%** and is NOT_SEPARATED from a random word's code
  (**-0.0015 [-0.1391,+0.1361]**, reproducing the landed number exactly). **That mechanism's cue is
  measurably empty** -- but the correct claim is about **that estimator**, never "grounding does not
  propagate through our relations", because nothing under 60% could have been seen either way.
- **Both landed bridge arms report `MARGIN_NARROWER_THAN_ITS_OWN_CI = True`.** This is the
  **FOURTH** underpowered null read as a capability statement this session.

### THE ONE NUMBER THAT SHOULD CHANGE HOW EVERY FUTURE RESULT IS READ
**Detection threshold, each instrument in its OWN units on its OWN population:
retrieval addressing `lambda_star = 0.05` (n=3,994); bridging SimLex pair-Spearman
`lambda_star = 0.60` (n=308). A 12-fold difference in what they can see.** The programme has been
drawing conclusions of equal strength from both. **Report `lambda_star` beside every future null.**

---

## 0. DISCLOSURE (updated live)

- **ONE TOOL CALL WAS DENIED.** The run STOPPED at that step and reported rather than working
  around it. Exact text, verbatim:
  > The user doesn't want to take this action right now. STOP what you are doing and wait for the
  > user to tell you how to proceed.

  Denied call: a `Bash` read of the checkpointed `PRIMARY_COMMON` unit from
  `data/exp_cue_regime_one_variable_v1/` via `tools.exp_checkpoint.load_units`. **No variant was
  retried.** The coordinator later cleared it as `cancelled` (the Director's own plan edit was torn
  down in the same window) and the identical read was re-issued unchanged. **`lambda_star` was NOT
  reported while half-verified.** No other call was denied at any point.
- No deletion token issued, alone or bundled. No `git add -A`. No origin push. No subagent spawned.
- No LLM anywhere in any path.
- `data/foundation/**` never opened. Protected paths listed in the brief were READ ONLY or not
  opened at all.
- `bash tools/substrate_query.sh` was launched for the mandatory prior-work check and **did not
  return within 120 s** -- consistent with the documented `hd_director_kb_continuous_ingest`
  livelock (10.65 GB, self-terminated at its own 45-min limit). Prior-work check was therefore done
  by **filesystem enumeration** instead, which is the stronger method per the standing rule
  ("an absence claim requires an enumeration, not a search"). Result in section 1.

---

## 1. PRIOR-WORK CHECK (enumerated from disk, not searched) -- DONE

Method: `ls experiments/` (**5,909 files**) filtered for cue / ladder / dose / regime / degradation
names, plus `grep -ril` over `notes/` for the design vocabulary. **Cue-degradation curves ALREADY
EXIST in this repo and are credited, not re-derived:**

| prior cell | what it did | why this run is not a rediscovery |
|---|---|---|
| `experiments/exp_hub_spoke_partial_cue_curve_v1.py` | facet recovery as a curve over cue overlap, hub-and-spoke addressing | addressing/hit regime; no detection threshold; not on the bridging population |
| `experiments/exp_ca3_completion_partial_cue_v1.py` | retrieval as a CURVE OVER CUE OVERLAP with a CA3 completer | same regime; measures a MECHANISM's effect on the curve, not the curve's SENSITIVITY |
| `experiments/exp_readout_sign_cue_overlap_curve_v1.py` | exact-key vs partial-cue cost of the terminal `sign()` | one contrast, two points, not a ladder |
| `exp_substrate_pattern_completion_corruption_cliff_v2_*` | corruption cliff on synthetic codes | synthetic, not the real read-out |

**WHAT IS GENUINELY NEW, and it is narrower than "a cue curve":** using the curve as a **DETECTION
THRESHOLD** to decide whether a LANDED NULL is a capability statement or a power statement, and
expressing two different nulls (bridging, retrieval) in the SAME unit -- exact-key-equivalent
fraction. The two bridging cells measure only the **endpoints** (`K1_OWN_NORMS` = exact key; the
bridge arms = partial cue) and never the curve between them. That missing curve is exactly what
decides how their nulls must be read.

**VERDICT ON NOVELTY: not a rediscovery, but it BUILDS ON four prior cells and says so.**

---

## 2. THE PRE-REGISTRATION (written BEFORE any number was read)

### 2.1 The one variable

Same held-out words, same SimLex pairs, same 12-dim L2-normalised cosine scorer, same gold, same
bootstrap seed, same floors recomputed on the same stratum. **Only the CUE REGIME changes**, as a
continuous mixing fraction `lam` between the target's own stored row (the EXACT KEY) and a filler:

```
cue(w, lam) = lam * l2n(t_w) + (1 - lam) * l2n(filler_w)
```

- `lam = 1.0` -> the cue IS the exact key. Must be bit-identical to `K1_OWN_NORMS`.
- `lam = 0.0` -> the cue is the filler alone. With `filler = bridge code`, must reproduce the
  landed bridge arm exactly.

**PINNED / OURS.** The mixing itself is **OURS, INVENTION UNDER TEST** -- nothing in the biology
says a retrieval cue is a convex combination of an exact trace and a distractor. It is an
*instrument calibration device*, not a model of anything, and is reported as such. Fabricating an
anatomy for it would be exactly the laundering the fidelity gate bans. The adjacent PINNED fact,
carried from `notes/drill_brain_partial_cue_retrieval_...2026-08-16.md` sec 1c, cuts against the
whole framing of both bridging cells and is stated here so it is not lost: **the brain's retrieval
cue is NOT a subset of the stored pattern and arrives on a DIFFERENT WIRE (the direct perforant
path) from the one that wrote the memory (mossy fibre), through a synaptic matrix that was itself
modified during storage.** This cell does not fix that; it measures whether our instrument could
have detected the information even if it were there.

### 2.2 The ladders

Four ladders over `LAMBDAS = (0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.0)`:

| ladder | filler | what it measures |
|---|---|---|
| `E_SEL` | selectional-constraint bridge code (`S1_SELECTIONAL_MEAN`) | mechanism 2's cue |
| `E_INC` | thematic neighbour-copy bridge code (the incumbent) | mechanism 1's cue |
| `D_RANDWORD` | a random ELIGIBLE CORE word's code, 5 seeds, MAX DRAW | **the calibration ladder** |
| `D_GAUSS` | isotropic Gaussian matched to the per-dim mean/sd of core codes, 5 seeds, MAX DRAW | second non-informative filler; if the two D ladders disagree, BOTH are reported |

### 2.3 The primary measure -- `lambda_star`, the DETECTION THRESHOLD

**`lambda_star` = the smallest `lam` at which a `D` ladder arm CI-separates above
`max(F_ORTHOGRAPHIC, F_FREQUENCY_HARDENED, F_SCRAMBLE_PERM_P95, F_CONSTANT_PROTOTYPE)`,
every floor recomputed on this stratum's own population.**

It is the instrument's sensitivity expressed in units of "fraction of the target's own identity",
against a filler that carries none of it.

### 2.4 THE DECISION RULE, and it can fail BOTH ways

- **`lambda_star` SMALL** (the instrument resolves a weakly-identified cue) **and both bridge
  ladders at `lam = 0` sit below the floors** -> the bridges deliver LESS identity information than
  the instrument could have seen. **The cue is the cause; the mechanisms were never the problem;
  the three results collapse into one.**
- **`lambda_star` LARGE** (only a near-exact cue clears) -> **the bridging nulls are POWER
  statements, not capability statements**, and the Phase 2 kill-condition reading must be
  re-labelled. This retracts the current reading rather than confirming it, and is the outcome the
  session's dominant error pattern (an underpowered null read as a capability statement, three
  times in one night) would predict.
- **Either bridge ladder CI-separated ABOVE the matched `D` ladder at ANY `lam`** -> the bridge cue
  carries real identity information and the null is about the READ-OUT, not the cue. Reported with
  the multiplicity correction for 10 rungs.

### 2.5 Derived: the BRIDGE'S EXACT-KEY-EQUIVALENT

Interpolate the `D_RANDWORD` curve `rho(lam)` to the observed bridge rho at `lam = 0`. The result,
`lam_equivalent`, states the bridge cue's identity content **in the same units as the partial-cue
result**, giving the common currency the one-cause hypothesis needs. Reported with the interval
obtained by mapping the bridge rho's CI through the same curve. **This is an interpolation, not a
measurement, and is labelled as a derived quantity everywhere it appears.**

### 2.6 Validity arms, which must fail INDEPENDENTLY

- `KA_EXACT_ONLY` (= `lam = 1.0`): asserted `np.allclose` against the `K1_OWN_NORMS` code matrix and
  must reproduce its rho. Sensitive to the scorer, the pool and the eligibility mask; **insensitive
  to the filler construction.**
- `NULL_PERMUTED_ASSIGNMENT` (at `lam = 0.80`, i.e. deliberately near the top of the ladder where a
  correct pairing would be near ceiling): exact-key rows assigned to the WRONG held-out words. Must
  collapse to chance. Sensitive to the pairing; **insensitive to whether the scorer is correct.**
- A scorer bug drops `KA` while leaving `NULL` at chance; a pairing/leak bug leaves `KA` at ceiling
  while raising `NULL`. Neither single bug can make both pass.

### 2.7 The gate read BEFORE any `lambda_star`

`MONOTONICITY_GATE`: each `D` ladder's rho must be monotone non-decreasing in `lam`
(Spearman(lam, rho) >= 0.9). **If a ladder is not a dose-response curve, `lambda_star` is
meaningless and is not published for that ladder.**

`G0_POWER_GATE` (inherited from the sibling): if `K1_OWN_NORMS` does not clear this stratum's own
max(4 floors) CI-separated, every arm on the stratum is `POWER_INSUFFICIENT`, never `FAIL`.

### 2.8 Reporting rules this cell is bound by

- **Every margin is published beside its CI half-width AND the scramble null p95 at that n AND the
  analytic null width `1.645/sqrt(n-1)`.** A width is not an effect.
- **Every floor is recomputed on this stratum's own population.** `0.1382`, `0.2070` and `-0.1959`
  are never imported. The constant/prototype floor is published under **all three tie conventions**
  (optimistic / midrank / pessimistic) because a constant code ties every bridged pair.
- No number crosses scorers, pools or populations. Each stratum names its scorer, n, pool and gold.
- `grounded_similarity()` is never the scorer, and the trap is re-measured at runtime.
- `ruler_mode_gate()` (`experiments/exp_task_degeneracy_v1.py:121`) is CALLED, not reimplemented.
  The reduced-grid flag is `--grid reduced`; the token `--smoke` never enters argv.
- `verdict_bar_check.py` will be run and its class reported, and **not relied on** (four false
  passes on record); arm-by-arm margins are stated independently.

---

## 3. ARM LOG (appended after every arm; newest last)

### ARM 0 -- BUILD + SELF-TEST of both cells. **PASS.**

Files: `D:\AI\hd-instrument\experiments\exp_cue_regime_one_variable_v1.py` (bridging side),
`D:\AI\hd-instrument\experiments\exp_cue_regime_one_variable_retrieval_v1.py` (retrieval side).

Both `--self-test --grid reduced` ALL PASS. `ruler_mode_gate()` PASS on both
(`RUN_MODE=full, V=4096, CORPUS_BYTES=64,000,000`); **the token `--smoke` never entered argv.**
Asserted, not assumed: the mixing device on a known answer; `lam=1` reproduces the exact-key code
matrix through the REAL `code_matrix()` (max abs dev 5.96e-08); `lam=0` reproduces the raw bridge
code matrix (1.19e-07); the ladder is a MONOTONE DOSE-RESPONSE on a planted fixture (bridging
0.4874 -> 1.0000; retrieval addressing 0.0 -> 1.0); the three tie conventions are correctly
ordered; the bootstrap can BOTH fire and fail; the four floors are four different functions;
`grounded_similarity()` saturation re-measured at **0.7618 on two values** and it is never the
scorer. `tools/floor_battery.self_test()` PASS (S1-S8, including S8 rejecting the legacy pool).

### ARM 1 (retrieval side) -- REDUCED-GRID SMOKE. **LANDED in 15 s. AND IT ALREADY FALSIFIES THE SIMPLE VERSION OF THE HYPOTHESIS.**

**SCOPE, stated first: `n = 400` items, `N_BOOT = 2000`, 2 filler seeds. THESE ARE SMOKE NUMBERS
ON A 400-ITEM SUBSET AND MUST NOT BE QUOTED AS RESULTS.** The full run is the one that counts. They
are recorded because they changed the design.

Gates, all passing, verified BEFORE any treatment number was read:
- **REGRESSION GATE PASS: `0.0223` against the landed `0.0223`, tol 5e-4, on the full landed open
  pool, `n_scored = 3994`.** The instrument is the landed one.
- **KNOWN-ANSWER: exact-key addressing `1.0000`** (gate 0.95). **NULL: non-informative filler alone
  addresses `0.0000`** against chance `0.00018212`. They fail independently by construction.
- **MONOTONICITY: addressing is a perfect dose-response on all three ladders (Spearman 1.0000).**

The three findings, in descending order of how much they change the picture:

**(a) THE EXACT KEY ALSO FAILS THE READ-OUT.** At `lam = 1.00` the cue IS the item's own stored
row and addressing is `1.0000` -- it finds the right item every single time. hit@1 against WordNet
gold is **`0.0275`, against a binding CONSTANT/PROTOTYPE floor of `0.1250` and an orthographic
floor of `0.1162` recomputed on this population.** Hand the filing system the exact card it holds,
and it still names a synonym 2.75% of the time, below what a ranking that ignores the question
achieves. **On the READ-OUT metric the cue is EXONERATED and the defect is downstream of the
address** -- in what the store's neighbourhood encodes. This is the same object as the banked
"only 0.46% of a word's top-20 store neighbours are its synonyms", now measured with a perfect cue
and against four floors.

**(b) THE PARTIAL CUE DOES CARRY IDENTITY -- ABOUT 11-18% OF THE EXACT KEY.** Addressing under the
real partial cue is **`0.0725` against chance `0.00018`**, ~400x chance and CI-separated. Inverting
the non-informative calibration ladder puts its **exact-key-equivalent at `0.175`** (vs another
item's partial cue) and **`0.114`** (vs a moment-matched Gaussian). The detection threshold
`lambda_star` is **`0.15`** and **`0.10`** on those two ladders. So the instrument can resolve a
cue carrying ~10-15% of the exact key, and the real cue carries ~11-18%. **"The cue carries
nothing" is not what this measures.**

**(c) THE REAL PARTIAL CUE BEATS A MATCHED NON-INFORMATIVE FILLER** at 7 of 10 rungs on hit@1 and
6 of 10 on addressing (vs another item's partial cue, which has identical marginals). Against the
Gaussian filler it wins only 3-4 of 10 -- **a real partial cue is a STRUCTURED distractor and
interferes more than isotropic noise does**, which is why both D ladders are run and both reported.

### DESIGN CORRECTION FORCED BY THIS SMOKE, DISCLOSED NOT QUIETLY FIXED

The smoke's own verdict string read `CUE_IS_THE_UPSTREAM_CAUSE_INSTRUMENT_RESOLVES_A_WEAKLY_
IDENTIFIED_CUE` **on a run whose own head-to-head block showed the partial cue beating a matched
non-informative filler at 7 of 10 rungs.** The cause was an `if/elif` verdict chain whose branch
order let one gate mask another. **This is the exact shape of the fault that has cost this project
most -- a headline that does not survive its own metrics.json.**

Both cells were corrected BEFORE any full run:
1. **The verdict is now COMPOSED from independent gates**, not selected by branch order:
   `EXACTKEY_READOUT_{CLEARS|BELOW_FLOOR}__CUE_CARRIES_IDENTITY_{YES|NO}__LAMBDA_STAR_{x}`.
   No branch can hide a measured fact.
2. **`EXACT_KEY_READOUT` is now its own top-level block** so finding (a) can never be buried.
3. **The head-to-head decision statistic is now the LONGEST ADJACENT RUN of ABOVE rungs**, not the
   count -- one isolated rung in ten is expected 0.50 times under the null and is not evidence.

**No arm, floor, population, threshold or seed changed. Only the LABEL MAPPING, and it changed
AGAINST the hypothesis being tested.**

---

### ARM 2 (retrieval side) -- **FULL RUN LANDED. 120 s.** `data/exp_cue_regime_one_variable_retrieval_v1/metrics.json`

Verdict string: **`EXACTKEY_READOUT_BELOW_FLOOR__CUE_CARRIES_IDENTITY_YES__LAMBDA_STAR_0p05`**

**THE ANSWER IS NO, AND IT IS NO IN A MORE USEFUL WAY THAN A YES WOULD HAVE BEEN.** See section 4.

### ARM 3 (bridging side) -- **FULL RUN, TWO OF THREE CONFIGS LANDED.** `data/exp_cue_regime_one_variable_v1/units.jsonl`

`PRIMARY_COMMON` 497 s and `COMMON_MORPHBLOCK` 473 s, both **`lambda_star = 0.60` on all four
ladders**. `INCUMDENT_OWN_larger_n` in flight; detached, PID in
`D:\AI\hd-instrument\scratch\cue_regime_bridge_FULL.pid`, logs `cue_regime_bridge_FULL.out`/`.err`.
Full arithmetic in section 4.4. **A DENIED READ INTERRUPTED THIS ARM ONCE** -- see section 0; the
denial was later cleared as `cancelled` and the read re-issued unchanged.

**INDEPENDENT CROSS-CHECK, and it is worth recording.** A slow-path (unvectorised) reduced-grid run
of the same cell ran in parallel throughout and reached `PRIMARY_COMMON` in **1,205 s** against the
fast path's **497 s at 5x the resamples** (~12x speedup). It reported
`lambda_star = 0.60` for `D_RANDWORD` and `E_INC` and `0.80` for `D_GAUSS` and `E_SEL` -- i.e. **the
same conclusion, one rung coarser, at N_BOOT=2,000 with 2 filler seeds instead of 10,000 with 5.**
The disagreement is in the expected direction (fewer resamples, wider CIs, later separation) and is
itself a small power demonstration.

**A performance fix was required to make the full grid land at all, and it is gated, not trusted.**
`exp_meaning_asset_fair_test_v1.boot_rho_diff` is a Python loop over a Python-tie-loop Spearman:
**measured 247 us per correlation and 5.73 s per 2,000-resample call**, and this cell needs ~250 of
them per config, i.e. **~10 hours at the full grid -- the run would not have landed.** The shared
module was **NOT edited**. The same quantity is recomputed with vectorised midranks, drawing the
resample indices from the **identical** generator call, and a **self-test equality gate** asserts
agreement with the landed implementation. Measured on a deliberately tie-heavy fixture (49 and 47
distinct values in 220):

- max abs deviation of the vectorised Spearman from `INS._spearman`, row by row: **0.0**
- max abs deviation of the point estimate and **both** CI bounds from `FT.boot_rho_diff`: **0.0**

**Bit-identical, not approximately equal.** If that assertion ever fails the cell refuses to run.

---

## 4. RESULTS

### 4.1 ARM 2, THE RETRIEVAL SIDE -- THE HYPOTHESIS IS FALSIFIED, AND WHAT REPLACES IT IS BIGGER

**Population, stated once and never crossed:** 5,491 anchors, **n = 3,994 items**, the LANDED OPEN
pool (`mat_ok` minus per-item exclusions), WordNet gold, hit@1 tie-corrected as primary.
Chance addressing **0.00018212**. No matched or balanced pool is used, because `eligB` is on record
admitting a constant at 0.1715 against chance 0.0101.

**GATES, all passed and read BEFORE any treatment number:**

| gate | value | verdict |
|---|---|---|
| REGRESSION -- reproduce the landed partial-cue read-out | **0.0223** vs expected **0.0223**, tol 5e-4, n=3994 | PASS |
| KNOWN-ANSWER -- exact-key addressing | **1.0000** (gate 0.95) | PASS |
| NULL -- non-informative filler alone addresses | **0.00025** against chance **0.00018** | PASS |
| MONOTONICITY -- addressing is a dose-response curve | Spearman(lam, value) = **1.0000** on all three ladders | PASS |
| MONOTONICITY -- hit@1 | 0.9636 / 0.9152 / 0.9636 | PASS |

KA and NULL fail independently by construction: a scorer or store bug drops KA while leaving NULL
at chance; a pairing or leak bug leaves KA at ceiling while raising NULL.

---

#### FINDING A -- **HAND IT THE EXACT CARD AND IT STILL LOSES TO A RANKING THAT IGNORES THE QUESTION.**

At `lam = 1.00` the cue **is** the item's own stored row. Addressing is **1.0000** -- it finds the
right item every single time out of 5,491.

| | value |
|---|---|
| hit@1, tie-corrected, exact-key cue | **0.0481** |
| binding floor (`F_CONSTANT_PROTOTYPE`), recomputed on **this** population | **0.1390** |
| **margin** | **-0.0909  [-0.1034, -0.0786]  BELOW** |
| margin CI half-width | **0.0124** |
| binomial CI half-width at the floor, n=3994 | 0.0107 |

**The margin is 7.3x its own CI half-width. This is an effect, not a width.** All four floors,
recomputed here, under all three tie conventions: orthographic **0.0873** (opt 0.0984 / cons
0.0789), frequency **0.0185**, scramble **0.0120**, constant/prototype **0.1390** (no tie
sensitivity -- it is a distinct-valued channel). The gold-fitted ORACLE constant, **not a floor**,
is **0.1715**.

**The exact key is below the CONSTANT floor AND below the SPELLING floor.** Read literally: the
nearest *eligible* neighbour, in our own store, of a word's own stored row is a WordNet synonym of
that word **4.81%** of the time -- worse than always answering with the most generic anchor.

**Therefore, on the read-out metric, THE CUE IS EXONERATED. It is not the blocker and it never
was.** A better cue, a better address, a translator, a completer, a two-stage cue or a bridge
cannot move this number, because this number is measured with a **perfect** cue.

#### FINDING B -- **NO RUNG OF THE LADDER CLEARS THE FLOOR. NOT ONE.**

`M2_lambda_star = null` on **all three** ladders. hit@1 rises smoothly and monotonically with the
exact-key fraction and never reaches the floor:

| lam | 0.00 | 0.05 | 0.10 | 0.15 | 0.20 | 0.30 | 0.45 | 0.60 | 0.80 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|---|
| E (real partial cue) | 0.0223 | 0.0238 | 0.0243 | 0.0253 | 0.0268 | 0.0310 | 0.0393 | 0.0508 | 0.0513 | 0.0481 |
| D (another item's cue) | 0.0088 | 0.0063 | 0.0060 | 0.0093 | 0.0103 | 0.0143 | 0.0265 | 0.0498 | 0.0498 | 0.0481 |
| D (Gaussian) | 0.0093 | 0.0110 | 0.0115 | 0.0138 | 0.0183 | 0.0313 | 0.0468 | 0.0506 | 0.0516 | 0.0481 |

Best rung anywhere: **0.0516**, still **-0.0874 BELOW** the floor. **There is no quantity of the
target's own identity that lifts this read-out above a constant ranking.**

*(Consistency check built into the design: all three ladders converge to the identical arm at
lam = 1.00 and report the identical margin, -0.0909. They do.)*

#### FINDING C -- **THE PARTIAL CUE CARRIES REAL IDENTITY. ~390x CHANCE, AND 12-18% OF THE EXACT KEY.**

Addressing, the metric that needs no WordNet gold at all:

| ladder | 0.00 | 0.05 | 0.10 | 0.15 | 0.20 | 0.30 | 0.45 | 0.60 |
|---|---|---|---|---|---|---|---|---|
| E, the **real** partial cue | **0.0711** | 0.0994 | 0.1510 | 0.2278 | 0.3593 | 0.7366 | 0.9977 | 1.0000 |
| D, another item's partial cue | 0.00025 | 0.0015 | 0.0040 | 0.0258 | 0.1032 | 0.5463 | 0.9927 | 1.0000 |
| D, Gaussian | 0.00025 | 0.0035 | 0.0288 | 0.1675 | 0.5218 | 0.9945 | 1.0000 | 1.0000 |

- The real partial cue addresses its own item **0.0711** against chance **0.00018** -- **390x
  chance**, and **+0.0709 +- 0.0080 ABOVE** a filler with identical marginals.
- **`lambda_star` = 0.05 on BOTH non-informative ladders.** The instrument CI-separates a cue
  carrying only **5%** of the exact key. **The instrument is not blunt.**
- **Exact-key-equivalent of the real partial cue (DERIVED by inverting the calibration ladder, not
  measured): 0.179** against another item's cue, **0.115** against the Gaussian.

**So the cue carries roughly 12-18% of the target's identity, against a 5% detection threshold.
"The partial cue carries nothing" is FALSE.**

#### FINDING D -- the partial cue also beats a matched non-informative filler ON THE READ-OUT

Unbroken adjacent runs of ABOVE rungs (the multiplicity-robust statistic, not the count):
**7 of 10 in a run of 7** against another item's partial cue; **5 of 10 in a run of 5** against the
Gaussian. Even at `lam = 0`, hit@1 is **+0.0135 [+0.0083, +0.0188] ABOVE** the matched filler.
A single isolated rung would be expected 0.50 times under the null and would not count; a run of
seven is not that.

---

### 4.2 THE SYNTHESIS -- **THE PARTIAL-CUE CAP IS TWO DIFFERENT THINGS THAT HAVE BEEN QUOTED AS ONE**

1. **AN ADDRESSING DEFICIT.** Real, graded, and **not structural**: the cue carries 12-18%
   exact-key-equivalent against a 5% threshold, and addressing recovers smoothly and completely as
   the cue improves. This is the half the oracle result (0.8787 exact vs 0.0365 partial) and the
   "the cap is structural" reading belong to.
2. **A READ-OUT CEILING THAT IS INDEPENDENT OF THE CUE ENTIRELY.** A **perfect** address lands
   0.0481, CI-separated BELOW both the constant floor (0.1390) and the spelling floor (0.0873), and
   no rung of the ladder clears at any cue quality.

**These are different defects with different fixes, and the programme has been treating them as
one.** Every build aimed at the cue -- a translator, a completer, a two-stage cue, a better bridge
-- addresses (1) and **cannot touch (2)**, and (2) is the one that sets the headline number.

**WHAT THIS MEANS FOR THE BRIEF'S HYPOTHESIS:** the claim was that the two bridging nulls and the
partial-cue cap share ONE upstream cause, the cue. **On the retrieval side that is measured and
false.** The cue is better than believed; the store's neighbourhood structure is the binding
defect. The honest common cause candidate is now **what the store encodes, not what the cue
carries** -- and that is upstream of both, so the "one upstream cause" intuition may survive with a
different cause named. ARM 3 tests whether the bridging side shows the same dissociation.

*This paragraph is the Director-style strategic read and is labelled HYPOTHESIS PENDING VET.
Findings A-D are measured.*

### 4.4 ARM 3, THE BRIDGING SIDE -- **`lambda_star = 0.60`. THE INSTRUMENT IS 12x BLUNTER THAN THE ONE IN ARM 2.**

`data/exp_cue_regime_one_variable_v1/units.jsonl`, configs `PRIMARY_COMMON` (497 s) and
`COMMON_MORPHBLOCK` (473 s), both FULL grid, N_BOOT=10,000, N_PERM=2,000, 5 filler seeds.
`INCUMBENT_OWN_larger_n` still in flight.

**Population, stated once and never crossed:** **n = 308 SimLex pairs**, 337 held-out words
(N 259 / V 27 / A 22), scorer = SimLex Spearman rho on 12-dim L2-normalised norms cosine, gold =
SimLex. **Spearman CI half-width at n=308 = 0.1122. Analytic null width 1.645/sqrt(307) = 0.0939.**
Coverage is 100% by construction -- the population is restricted to words EVERY ladder covers,
because `code_matrix()` falls back to the exact key for uncovered words and that would leak the
answer into a ladder arm.

**FLOORS, ALL FOUR RECOMPUTED ON THIS POPULATION, ALL THREE TIE CONVENTIONS.** `0.1382`, `0.2070`
and `-0.1959` are **not imported and do not appear**:

| floor | midrank | optimistic | pessimistic | tie mass |
|---|---|---|---|---|
| `F_ORTHOGRAPHIC` | 0.0503 | 0.0606 | 0.0400 | 0.627 |
| `F_FREQUENCY_HARDENED` | -0.0000 | +0.00002 | -0.00006 | 0.006 |
| `F_CONSTANT_PROTOTYPE` | **-0.2253** | -0.2232 | -0.2274 | 0.253 |
| `F_SCRAMBLE_PERM_P95` (per arm) | **0.0947-0.1010** | -- | -- | -- |

**The constant floor is the WEAKEST of the four here (-0.2253), exactly as retraction 3 predicted
for a pair-correlation instrument. The BINDING floor on every single arm is the scramble p95.**

**VALIDITY, verified BEFORE any treatment number, failing independently:**

| arm | value | verdict |
|---|---|---|
| `KA_EXACT_ONLY` (lam=1.00) | rho **0.3311**, binding floor 0.0961, margin **+0.2350 [+0.0773,+0.3898] ABOVE** | PASS |
| `NULL_PERMUTED_ASSIGNMENT` (exact keys, wrong words) | rho **0.0118 [-0.0967,+0.1226] NOT_SEPARATED** | PASS |
| `G0_POWER_GATE` | PASSED | PASS |
| MONOTONICITY | Spearman(lam, rho) = **1.0000 on all four ladders** | PASS |

**REGRESSION GATES -- the population and scorer are provably the landed ones:**
- `lam=1.00` is bit-equal to the `K1_OWN_NORMS` code matrix on **all four** ladders (max abs
  deviation **1.19e-07**), all four reading rho **0.3311**. A four-way consistency check.
- `lam=0.00` reproduces the landed bridge arms: `E_SEL` **-0.04053** (landed `S1_SELECTIONAL_MEAN`),
  `E_INC` **+0.06434** (landed `I1_NEIGHBOUR_COPY_INCUMBENT`).
- **-0.04053 - 0.06434 = -0.1049, which is the landed cell's published `HEAD_TO_HEAD_S1_minus_I1`
  to four decimal places.** Independent confirmation that this is the same population, scorer, gold
  and eligibility mask.

#### THE CALIBRATION LADDER -- THE DELIVERABLE. `D_RANDWORD`: lam fraction of the target's OWN exact key, diluted with a random real word's code.

| lam | rho | margin over binding floor | **CI half-width** | scramble p95 | band |
|---|---|---|---|---|---|
| 0.00 | -0.0390 | -0.1399 [-0.3071,+0.0275] | 0.1673 | 0.1010 | NOT_SEPARATED |
| 0.05 | -0.0214 | -0.1161 [-0.2725,+0.0440] | 0.1583 | 0.0947 | NOT_SEPARATED |
| 0.10 | -0.0081 | -0.1036 [-0.2716,+0.0610] | 0.1663 | 0.0956 | NOT_SEPARATED |
| 0.15 | +0.0121 | -0.0857 [-0.2456,+0.0769] | 0.1612 | 0.0978 | NOT_SEPARATED |
| 0.20 | +0.0334 | -0.0626 [-0.2217,+0.0945] | 0.1581 | 0.0961 | NOT_SEPARATED |
| 0.30 | +0.0842 | -0.0139 [-0.1633,+0.1409] | 0.1521 | 0.0982 | NOT_SEPARATED |
| **0.45** | **+0.1807** | **+0.0854 [-0.0691,+0.2343]** | 0.1517 | 0.0953 | **NOT_SEPARATED** |
| **0.60** | **+0.2683** | **+0.1731 [+0.0120,+0.3374]** | 0.1627 | 0.0953 | **ABOVE** |
| 0.80 | +0.3172 | +0.2195 [+0.0607,+0.3752] | 0.1573 | 0.0979 | ABOVE |
| 1.00 | +0.3311 | +0.2350 [+0.0773,+0.3898] | 0.1562 | 0.0961 | ABOVE |

**READ THE FOURTH COLUMN. The margin CI half-width is 0.15-0.17 at every rung -- larger than most
of the margins themselves. A cue made of 45% of the target's own exact key CANNOT SEPARATE ON THIS
INSTRUMENT.**

**`lambda_star = 0.60` on all four ladders, in BOTH configs, under all three definitions**
(strongest floor / strongest floor + `T_MARGIN_MIN` 0.05 / all four floors). The morphology-blocked
control -- which deletes every source sharing a stem with the target, closing the spelling leak --
**reproduces 0.60 exactly on all four ladders.**

#### WHERE THE TWO LANDED BRIDGES SIT ON THAT LADDER

| landed arm | rho at lam=0 | margin vs binding floor | **CI half-width** | `MARGIN_NARROWER_THAN_ITS_OWN_CI` |
|---|---|---|---|---|
| `E_SEL` = landed `S1_SELECTIONAL_MEAN` | -0.0405 [-0.1482,+0.0698] | -0.1387 [-0.3120,+0.0318] | **0.1719** | **True** |
| `E_INC` = landed `I1_NEIGHBOUR_COPY` | +0.0643 [-0.0508,+0.1775] | -0.0329 [-0.1924,+0.1267] | **0.1595** | **True** |

**EXACT-KEY-EQUIVALENT (DERIVED by inverting the calibration curve; NOT a measurement):**

| bridge | vs `D_RANDWORD` | vs `D_GAUSS` |
|---|---|---|
| thematic neighbour-copy (`I1`) | **0.261** [0.000, 0.445] | **0.235** [0.000, 0.408] |
| selectional (`S1`) | **0.000** [0.000, 0.272] | **0.026** [0.000, 0.244] |

**HEAD-TO-HEAD vs a non-informative filler: 0 rungs ABOVE in all four comparisons; longest adjacent
run 0; `CARRIES_IDENTITY = False` everywhere.** At `lam=0`, `S1 - D_RANDWORD` =
**-0.0015 [-0.1391,+0.1361] NOT_SEPARATED** -- **which reproduces the landed cell's
`S1 vs N2_NULL_RANDOM_TARGET` to four decimal places.** `I1 - D_RANDWORD` = **+0.1034
[-0.0385,+0.2441] NOT_SEPARATED**: a large point estimate the instrument cannot resolve, CI
half-width **0.1413**.

#### 4.4b THE THIRD CONFIG IS THE DIRECT HIT: `INCUMBENT_OWN_larger_n`, **n = 394** -- THE EXACT STRATUM THE KILL WAS FIRED ON

552 s, FULL grid. Population **n = 394** SimLex pairs, 412 held-out words (N 259 / V 86 / A 49).
Spearman CI half-width **0.0991**; analytic null width **0.0830**.

**THE LANDED, KILLED ARM REPRODUCES BIT-FOR-BIT.** `E_INC` at `lam = 0.00` reads
**rho = +0.0270** -- which *is* `exp_thematic_relation_supply_bridged_grounding_v2`'s published
`B1 rho 0.0270 at n=394`, the number Phase 2's kill condition was fired on. Two further identity
checks land at the same time: the constant floor here computes to **-0.1977**, matching the value
`PLAN_NEXT_24H` retraction 3 records for this exact stratum, and `KA` reads **0.3301**, matching the
landed `K1 0.3301`. **This is the same population, scorer, gold and eligibility mask, verified three
independent ways.**

| | value |
|---|---|
| `KA_EXACT_ONLY` | rho **0.3301**, margin **+0.2461 ABOVE** -- PASS |
| `NULL_PERMUTED_ASSIGNMENT` | rho **-0.0161 NOT_SEPARATED** -- PASS |
| MONOTONICITY | Spearman(lam, rho) = **1.0000** on all three ladders |
| floors (midrank / opt / pess) | ortho **0.0412** / **0.1239** / -0.0419; freq 0.0317; constant **-0.1977** / -0.1959 / -0.1996; scramble p95 **0.0817-0.0881** |

**The calibration ladder at n=394:**

| lam | rho | margin over binding floor | **CI half-width** | band |
|---|---|---|---|---|
| 0.00 | -0.0353 | -0.1235 [-0.2706,+0.0227] | 0.1466 | NOT_SEPARATED |
| 0.15 | -0.0004 | -0.0820 [-0.2205,+0.0563] | 0.1384 | NOT_SEPARATED |
| 0.30 | +0.0708 | -0.0162 [-0.1635,+0.1249] | 0.1442 | NOT_SEPARATED |
| **0.45** | +0.1591 | **+0.0730 [-0.0667,+0.2133]** | 0.1400 | **NOT_SEPARATED** |
| **0.60** | +0.2482 | **+0.1617 [+0.0301,+0.2927]** | 0.1313 | **ABOVE** |
| 1.00 | +0.3301 | +0.2452 [+0.1140,+0.3757] | 0.1309 | ABOVE |

**THE KILLED ARM, IN ITS OWN LADDER'S UNITS:**
- margin vs binding floor **-0.0566 [-0.1901,+0.0771]**, **CI half-width 0.1336 -- 2.4x the
  margin.** `MARGIN_NARROWER_THAN_ITS_OWN_CI = True`.
- **exact-key-equivalent 0.214 [0.000, 0.392]** (vs a random word) and **0.224 [0.000, 0.385]**
  (vs Gaussian).
- **`lambda_star = 0.60`.** At 45% of the target's own exact key the margin is still NOT_SEPARATED.

**So the arm that fired the kill carries roughly 21-22% of the target's identity, on an instrument
that needs 60% to speak. It could not have separated. That is the whole finding.**

**A tie caveat that must travel with this stratum:** the orthographic floor's tie spread here is
enormous -- midrank **0.0412** but **optimistic 0.1239**. Under the optimistic convention the
killed arm (0.0270) is not merely NOT_SEPARATED from a spelling floor, it is **well below** one.
Reported both ways, never the flattering one.

### 4.5 WHAT THE ARITHMETIC SAYS ABOUT THE PHASE 2 KILL

The kill condition fired on two mechanisms reading NOT_SEPARATED against their floors. **Both of
those readings are made on an instrument that requires 60% exact-key equivalence to separate.**

- **THEMATIC NEIGHBOUR-COPY: the kill is WITHDRAWN.** It carries **23.5-26.1%** exact-key-equivalent
  -- **real, and less than half the 60% the instrument needs.** Its margin (-0.0329) is **4.8x
  narrower than its own CI half-width (0.1595)**. **No arm of any quality could have separated
  there.** This is a statement about n=308, not about bridging.
- **SELECTIONAL: the kill is RE-WORDED, not withdrawn.** It carries **0.0-2.6%** and is
  NOT_SEPARATED from a random word's code. **That estimator's cue is measurably empty** -- a real
  finding about the slot-filler mean, and the landed cell's *bridge-vs-bridge* claim
  (`S1 - I1 = -0.1049`, CI-separated) is untouched because it is not a floor comparison. **What
  does NOT survive is generalising it to "grounding does not propagate through our relations."**
  Its exact-key-equivalent CI runs **[0.000, 0.272]**, i.e. up to the instrument's own resolution
  limit -- so even "empty" is bounded by power, not established beyond it.

**THE HONEST SUMMARY: the kill condition was applied to two nulls, one of which is squarely a power
artefact and the other of which supports a much narrower claim than the one drawn from it.
Phase 2's kill should not stand in its current form.**

### 4.6 SO IS THERE ONE UPSTREAM CAUSE? -- **YES, BUT NOT THE ONE IN THE BRIEF**

*(Strategic read. HYPOTHESIS PENDING VET. Sections 4.1 and 4.4 are measured.)*

The brief's candidate -- "the cue does not carry the identity" -- is **measured false on the
retrieval side** (the cue carries 12-18%) and **unresolvable on the bridging side** (the instrument
cannot see anything under 60%). What the two arms share is different and simpler:

**BOTH FAILURES SURVIVE A PERFECT CUE.** On retrieval, an exact key gives perfect addressing and
still lands CI-separated BELOW a constant floor. On bridging, the exact key is the only thing that
clears -- and it clears at rho 0.3311, which is what our 12-dim target space is worth, not what
bridging is worth. **The common factor is not the cue and not the mechanism. It is what our stores
encode and what our instruments can resolve.** Neither is a capability claim, and neither is fixed
by building another acquisition mechanism on top.

### 4.3 WHAT ARM 2 DOES **NOT** CLAIM

- **No number here crosses to the bridging cells.** They score SimLex pair-Spearman on 12-dim
  norms over ~300-400 pairs; this scores hit@1 over 5,491 anchors on 3,994 items. Different
  scorer, pool, gold and population. The `0.0223`, `0.0481`, `0.1390` and `0.0873` here are facts
  about **this** population only.
- **It does not claim the read-out ceiling is a ceiling.** It is a fact about our store as built.
  People retrieve from degraded cues constantly, so the capability is demonstrated.
- **The exact-key hit@1 arm excludes the query word's own anchor** from the eligible pool, because
  the task is to name a synonym and not to name the word back. So 0.0481 is precisely "the store's
  nearest ELIGIBLE neighbour of w's own row is a WordNet synonym of w", which is the right
  question and is stated rather than left implicit.
- The mixing device remains OURS, INVENTION UNDER TEST. No brain structure is claimed for it.

---

### 4.7 `verdict_bar_check.py` -- CLASS REPORTED, **NOT RELIED ON** (four false passes on record)

| cell | class |
|---|---|
| `data/exp_cue_regime_one_variable_v1/metrics.json` (bridging) | **`SATURATED_CEILING`** |
| `data/exp_cue_regime_one_variable_retrieval_v1/metrics.json` (retrieval) | **`AGREES`** |

**The `SATURATED_CEILING` flag on the bridging cell is expected and is a checker artefact, not a
defect.** All four ladders converge to the IDENTICAL arm at `lam = 1.00` -- that convergence is a
deliberate consistency check (max abs deviation 1.19e-07 from the `K1_OWN_NORMS` code matrix) and
it necessarily produces four arms reading exactly 0.3311. A saturation detector sees four identical
top arms and fires. **Every margin in sections 4.4-4.6 is stated arm by arm with its own CI
half-width and does not depend on this tool's verdict either way.**

### 4.8 THE PER-POOL ORACLE CHECK, RUN AND REPORTED

- **Retrieval (ARM 2), open pool, n=3,994:** gold-fitted ORACLE constant = **0.1715**, against a
  binding constant floor of 0.1390. **The open pool is NOT a de-biased pool and is not claimed to
  be** -- the number is published so that nobody reads a margin over it as a margin over chance.
  `eligB` and the matched/balanced pools are **deliberately not used**, because `eligB` is on
  record admitting a constant at **0.1715 against chance 0.0101**.
- **Bridging (ARM 3):** `tools/floor_battery.pool_admits_a_winning_constant` operates on per-item
  **candidate sets** and a **hit@1** scorer. ARM 3's instrument is a **pair-correlation** scorer
  with no candidate sets, so that check is **undefined here and is not manufactured**. Its
  pair-correlation analogue is `F_CONSTANT_PROTOTYPE`, which **is** computed on every stratum,
  under all three tie conventions, and which comes out **the WEAKEST of the four floors on both
  strata (-0.2253 at n=308, -0.1977 at n=394)** -- exactly the reversal retraction 3 predicted for
  this scorer.

---

## 5. WHAT THIS RUN DOES NOT CLAIM

- **ARM 3 does NOT claim thematic bridging works.** It claims the instrument could not have told
  us either way below 60% exact-key-equivalence. **An unfalsified mechanism is not a confirmed
  one.** The right next step is a stratum where the margin can separate, not a louder claim.
- **ARM 3 does NOT rehabilitate the selectional bridge.** Its cue measures 0.0-2.6%
  exact-key-equivalent and is NOT_SEPARATED from a random word's code, reproducing the landed
  number to four decimals. What is withdrawn is only the GENERALISATION from it.
- **`lambda_star` is a property of an INSTRUMENT ON A POPULATION, not of the substrate.** 0.05 and
  0.60 are not comparable as quantities of anything except sensitivity, and no rho, hit@1 or floor
  crosses between ARM 2 and ARM 3 anywhere in this file.
- **The exact-key-equivalent figures are DERIVED by inverting a calibration curve, not measured**,
  and every one of their CIs runs down to 0.000 -- i.e. bounded below by the instrument's own
  resolution. They are labelled `DERIVED_NOT_MEASURED` in the artifact.
- Section 4.6 is a strategic read and is labelled **HYPOTHESIS PENDING VET**.

- Nothing here is a claim about the CAPABILITY. A child acquires most of its vocabulary by exactly
  this route, so the capability is DEMONSTRATED; every null below is a fact about our
  implementation.
- The mixing device in 2.1 is a calibration instrument, not a brain model, and no brain structure is
  claimed for it.
- VSA algebraic binding -- the substrate's core operation -- is **UNPINNED in the brain**, with
  three live accounts and published objections to each. Nothing in this run depends on it being
  correct, and nothing in this run tests it.

---

## 6. PRIOR-WORK ENUMERATION (filled in when the enumeration lands)
