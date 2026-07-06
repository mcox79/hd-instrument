# Research — mechanism-level self-verification: can the substrate check properties of its OWN design (not its ledger)?

**Date:** 2026-07-06
**Trigger:** Director preparatory scoping drill — a NEW north-star angle distinct from cert-ledger self-reasoning
(currency retrieval / conflict-flagging / global consistency, all already designed or landed against
`cert_ledger.jsonl`). This drill asks whether the now-COMPLETE arithmetic primitive set (add/subtract/compare/
multiply/exact-equality, all FULL HARD_PASS) can be turned on the substrate's own MECHANISM — its codebooks,
moduli, sub-block dimensions — to verify properties of the DESIGN, not the record. Explicitly non-parked (no
`cert_ledger`/referent-gate dependency) and explicitly notes-only: **no cell built, no dispatch.**
**Discipline:** `python tools/orchestrator/research_field_advisor.py` run (no exact-match field in the 22-field
matrix; nearest adjacencies are `coding-theory`, `free-probability`, `random-matrix-theory-beyond-free-prob`,
`sparse-coding-compressed-sensing` — all Tier-1/1b fruit-bearing or under-drilled). Scoured on-disk prior work
FIRST: read the full source of all 4 landed math-arithmetic cells (`exp_math_rns_add_chain_v1`,
`exp_math_rns_subtract_compare_v1`, `exp_math_rns_multiply_star_v1`), 2 prior CRT capacity cells
(`exp_crt_capacity_boost_v1` HARD_FAIL-superseded, `exp_crt_module_scaling_battery_v1` HARD_PASS), and all 4
same-day-adjacent research notes on the cert-ledger self-reasoning ladder, before any external dispatch. 3
parallel Sonnet lit-scans (generic terms only, no substrate-novel mechanism names off-platform, per
[[feedback-query-privacy-decomposition]]). Lit-scan calibration applied (deflate 0.15-0.25; novel-synthesis cap
0.50; HARD-FAIL thresholds mandatory below). NO routing files emitted (ferry mechanism deprecated; the ready
cell spec, if any, is delivered directly in this note per USER-locked override).

---

## HEADLINE

**There is exactly ONE genuine, non-tautological, config-contingent self-check hiding in the four candidates
named in the trigger — and it is narrower and thinner than it first looks.** Two of the four named candidates
(CRT decode collision-freeness given pairwise-coprime moduli; codebook pairwise-distinctness/min-distance) turn
out, on inspection of the substrate's own landed code, to be **the SAME question** — and that question is
**genuinely config-contingent** but has **never actually been swept to its failure boundary**: every one of the
four landed arithmetic cells fixes the sub-block dimension `SB=2730` and the max modulus `m<=43`, and repeats,
verbatim, an un-tested boilerplate comment ("sb=2730 >> max modulus 43, so per-residue argmax is collision-free")
that has been asserted three times and verified zero times at the boundary. That IS a real, falsifiable,
config-dependent property — `SB` vs `m` genuinely determines whether per-sub-block phasor argmax decode succeeds
or collapses, and a fresh 3-way lit-scan this drill confirms this is not a novel question in the world: it is the
textbook Welch-bound / Johnson-Lindenstrauss / M-ary-matched-filter capacity boundary (closed-form/asymptotic,
not something that must be found by Monte Carlo alone), applied to a construction the substrate has never swept.
**The other two candidates — CRT-reconstruction exactness given coprime moduli, and add/multiply homomorphism
exactness — ARE tautological, and a fresh lit-scan this drill supplies the exact theoretical reason why, not
just an assertion:** these are precisely the class of **exact algebraic-redundancy properties** (group
homomorphism, modular multiplication) that Blum-Luby-Rubinfeld's 1993 self-testing theory identifies as
trivially, unconditionally checkable — and the substrate's own landed cells ALREADY check them, at write time,
via plain integer gcd (`_coprime()`) and a `*_homomorphism_selftest()` function present in every one of the 4
cells. Re-running these as a "new self-verification cell" would produce a verdict that cannot come out any way
other than PASS (short of an implementation bug) — that is the literal definition of tautological, now
grounded in the actual theory of what these checks are, not just an intuition. **Net honest recommendation:
build ONE narrow cell — a sub-block-dimension decode-margin sweep, gated by a genuinely falsifiable formula-vs-
measurement comparison — and explicitly do NOT build a cell for CRT-uniqueness or homomorphism-exactness,
because those are correctly-already-covered, by-construction, and re-testing them would not be research, it
would be re-confirming arithmetic.** P_deflated for the one genuine candidate = **0.40** (capped novel-synthesis;
see Sec. 3).

---

## 1. THE FOUR CANDIDATES, SORTED HONESTLY

| # | Candidate (as named in the trigger) | Verdict | Why |
|---|---|---|---|
| 1 | CRT decode collision-freeness at a given (SB, moduli) | **REFRAME, then GENUINE (merges with #2)** | As literally stated ("fails if SB too small vs the modulus PRODUCT") this is not quite the right axis — CRT reconstruction uniqueness depends on the dynamic range of the ENCODED VALUE vs `M=prod(moduli)`, a pure O(1) integer fact (`gcd` pairwise-coprime check), already asserted/guarded in every landed cell's `_crt_setup()`. But the trigger's own worked example (SB=2730/mod-43 -> PASS; SB=10/mod-43 -> FAIL) is describing a DIFFERENT, real mechanism: `SB` in the substrate's own code is the per-modulus SUB-BLOCK DIMENSION (`N_DIM // R_MODULI` = 2730 in every landed cell), and decode success is a function of `SB` vs a SINGLE modulus `m` (how many dims are available to keep `m` phasor codewords pairwise-distinguishable), not `SB` vs the CRT product `M`. Re-scoped this way, it is genuine (Sec. 2). |
| 2 | Codebook pairwise-distinctness / min-distance | **SAME QUESTION AS #1** | For the phase-linear codebook used by all 4 landed cells, "are the `m` codewords in a sub-block pairwise distinguishable" and "does per-sub-block argmax decode correctly" are the SAME empirical fact viewed two ways (distance vs. decode accuracy). The multiply cell already computes a related quantity (`nearmiss_frac_below_half` — fraction of decodes whose runner-up similarity is <=0.5x the rank-1 similarity) as a REPORTED, not gated, diagnostic — but only ever at the single fixed default `SB=2730`, where it is always ~1.000 (verified on disk: `exp_math_rns_add_chain_v1` metrics report near-miss fraction 1.000). Nobody has swept `SB` down to see it move. Not a second candidate — folded into #1's cell spec. |
| 3 | Superposition capacity thresholds (how many items before decode breaks) | **GENUINE but NOT the fresh-consumer candidate asked for** | Real and config-contingent, but this is a DIFFERENT mechanism (additive/Hebbian bundling of many ITEMS, e.g. `exp_crt_module_scaling_battery_v1`'s bipolar-sign-code additive superposition, HARD_PASS on module-count scaling; `exp_crt_capacity_boost_v1`'s Hebbian pinv-recall, HARD_FAIL/superseded) from the phase-linear RNS arithmetic set's OWN sub-block decode. It is already well-trodden territory — superposition/bundling capacity cliffs are one of the substrate's most heavily-VET'd axes across many cap_map rows (Modern-Hopfield, coding-theory, free-probability fields, all Tier-1/1b per the field advisor). Building a "self-verification" cell here would mostly re-run existing capacity-curve work under a new name, not open a fresh consumer of the just-completed arithmetic primitives. Deprioritized for THIS drill; not recommended as the first cell. |
| 4 | Decode-fidelity vs noise | **SAME QUESTION AS #1, one framing further** | "Decode-fidelity vs noise" and "collision-freeness vs SB" are the same curve read two ways (fidelity = 1 - P(collision)). Folded into #1. |

**Net: the four named candidates collapse to exactly TWO distinct underlying questions** — (A) the SB-vs-m
decode-margin boundary (candidates 1/2/4, genuinely one question), and (B) additive superposition/bundling
capacity (candidate 3, genuine but already well-covered elsewhere, not the fresh-consumer target). Below, (A) is
scoped as the recommended cell; (B) is explicitly NOT recommended for a new cell at this time.

---

## 2. THE HONESTY GATE, RESOLVED — tautological vs config-contingent, with theory grounding (not just assertion)

### 2a. What is TAUTOLOGICAL (do not build a cell)

**CRT reconstruction exactness given pairwise-coprime moduli**, and **add/subtract/multiply homomorphism
exactness** (`enc(a) . enc(b) = enc(a+b mod m)`; `enc(a) ** b = enc(a*b mod m)`) are BOTH exact algebraic
identities, true by construction of the phase-linear phasor encoding (`codebook[r,j] = exp(i*2*pi*k_j*r/m)`,
integer `k_j` -> exact period-`m` periodicity). A fresh lit-scan this drill (Blum & Kannan 1989/1995, *JACM*;
Blum, Luby & Rubinfeld 1993, *JCSS*) supplies the precise theoretical reason these are the WRONG target for a
"self-verification cell," not just an intuition: BLR's self-testing/self-correcting framework is BUILT
specifically around functions with exact algebraic redundancy (group-homomorphism structure exactly like
`f(x)+f(y)=f(x+y)`), and BLR93 **explicitly gives modular multiplication, integer multiplication, and
exponentiation as its own worked applications** — this substrate's arithmetic cells are, structurally, textbook
instances of the exact class BLR theory says is trivially, unconditionally self-checkable. Concretely: every one
of the 4 landed cells (`exp_math_rns_add_chain_v1`, `_subtract_compare_v1`, `_multiply_star_v1`) already
contains, verbatim, a `crt_selftest()` (checks `_coprime(moduli)` via plain integer `gcd`, then brute-force CRT
round-trip over `[0, min(M,4096))` plus 256 random draws) and a `*_homomorphism_selftest()` (checks the exact
algebraic identity on random operands) — run as a MANDATORY gate BEFORE every smoke/FULL run, already on disk,
already re-verified this drill (`python -c` HARD_PASS re-checks above). Building a NEW "self-verification cell"
that re-derives "is CRT reconstruction exact given coprime moduli" or "is `enc(a)**b == enc(a*b mod m)`" would,
under correct construction, PASS with probability 1 (short of a floating-point/implementation bug) — that is the
literal definition of a tautological check: the verdict is fixed by the mathematics of the construction, not by
anything the substrate could discover. **SAY SO explicitly, per the task's instruction: these two named
candidates are, on inspection, mostly tautological, and this note recommends AGAINST spending a cell on them.**

### 2b. What is GENUINELY CONFIG-CONTINGENT (worth a cell)

The SB-vs-m decode-margin question is a DIFFERENT kind of claim: it is not an exact algebraic identity, it is a
**quantitative, noise/dimension-dependent statistical property** with no closed-form-by-inspection answer — you
cannot decide it by checking `gcd` or re-deriving an identity; you need either a probabilistic/asymptotic
derivation or a measurement. A second, independent lit-scan this drill (RNS hardware / BIST literature) supplies
the exact right analogy and confirms this really is the config-contingent kind: classical RNS dynamic-range
overflow is handled EITHER by a static design-time margin choice (choose the operating range comfortably inside
spec) OR, when that margin can't be guaranteed a priori, by dedicated runtime detection circuits (redundant
modulus checks, core/diagonal-function sign detection) — and digital-logic noise margins (VOH/VOL/VIH/VIL) are
explicitly characterized in that literature as **"conditionally guaranteed... not unconditionally guaranteed...
a genuine constraint that CAN be violated, not a tautology"** (mismatched logic families, insufficient voltage
headroom, out-of-spec loading all genuinely break the margin). This is precisely the substrate's own situation:
`SB=2730` was CHOSEN (a design-time margin decision, `N_DIM // R_MODULI` with `N_DIM=8192` fixed at the
substrate's compositional default) and asserted, informally, to be comfortably inside spec ("sb=2730 >> max
modulus 43") — but that margin claim has never been tested anywhere NEAR its boundary. **Sharpest, most honest
additional finding from the BIST lit-scan:** the substrate's existing formula self-tests (`crt_selftest`,
`*_homomorphism_selftest`) are, in the hardware analogy, exactly **BIST-style stuck-at/functional-correctness
checks** ("does the exact algebra hold at the config I chose") — and the same literature is explicit that BIST
does **NOT** inherently verify margin/corner behavior (that is a separate discipline: IDDQ testing, at-speed
timing-margin analysis). The substrate's math cells have BIST; they have never had a margin/corner test. That
gap is exactly what candidate #1 (Sec. 1) should fill.

**Third lit-scan (closed-form high-dimensional capacity bounds) upgrades the cell design from "sweep and eyeball"
to genuine self-verification.** The general principle this scan confirms: JL/Welch-bound concentration, the
Gilbert-Varshamov/Kabatiansky-Levenshtein sphere-packing family, the Donoho-Tanner compressed-sensing phase
transition, and M-ary matched-filter detection ALL give a **closed-form or asymptotic LOCATION for the
boundary, computable IN ADVANCE from the design parameters** (dimension, number of codewords, noise) — Monte
Carlo is needed only for second-order/finite-size corrections, not to locate the leading-order threshold. This
means the genuinely strong version of a "self-verification" cell is not merely "sweep SB, use `compare` to gate
a verdict" (which would be honest but thin — see Sec. 3's honesty caveat on that framing) but: **derive (or
adopt a standard) closed-form prediction for where decode collapses as a function of (SB, m), have the
substrate/cell COMPUTE that predicted boundary from the config parameters, and check whether the PREDICTION
correctly anticipates the MEASURED transition.** That is a real, falsifiable, non-tautological claim — the
formula could be wrong (wrong scaling law, wrong constant), and finding out is genuine information, not a
re-confirmation of already-certain algebra.

### 2c. Is this new, or a repackaging of the arithmetic cells? (task's Q3, answered plainly)

**Mostly repackaging of the DECODE mechanism, genuinely new only along ONE axis.** `phasor_codebook()` and
`decode_residues()` are reused VERBATIM from the landed cells (same functions, same construction) — nothing new
is invented in the primitive itself. The genuinely new piece is narrow: (a) sweeping `SB` as an experimental
variable (every landed cell treats it as a fixed background constant, never varied), and (b) deriving/adopting
an explicit closed-form prediction and testing it, rather than only reporting an empirical accuracy number. Per
[[feedback-chain-grade-primitives-not-trivially-composable]], composing "already-proven decode" with "a NEW
formula-vs-measurement comparison, at a config nobody has run" is not automatically proven just because the
pieces are each proven separately — this is a real, if narrow, test. **Being maximally honest about the OTHER
possible framing this note considered and rejects:** one could additionally route the PASS/FAIL judgment itself
through the substrate's own `compare`/`equality` primitives (accumulate per-config accuracy, compare against a
threshold using the landed compare cell's exact machinery, instead of a bare Python `if`). This drill's honest
assessment: **that framing is real but thin, and should NOT be oversold as the substantive contribution.** The
`compare`/`equality` primitives are already EXACT (HARD_PASS at 1.000, cv<=0.10) — routing an already-fully-
determined scalar comparison through them adds a legitimate but small composability check (does
accumulate-many-exact-tallies-then-compare hold at realistic trial counts, respecting the compare cell's own
documented half-range/dynamic-range caveat), NOT new empirical information about the decode mechanism's SB-margin
behavior. The actual research content is 100% in the SB-vs-m sweep-and-predict; the "substrate does its own
verdict arithmetic" layer is a nice-to-have, cheap, honest bonus, not the finding.

---

## 3. THE FIRST CELL — `exp_rns_subblock_margin_selfcheck_v1` (spec only, not authored/dispatched)

**Design principle:** reuse `phasor_codebook()`/`decode_residues()` VERBATIM (import or copy from the landed
`exp_math_rns_add_chain_v1.py`); add a genuinely new SB-sweep axis and a formula-vs-measurement discriminator
that none of the 4 landed cells has ever run.

**Grid:** hold `m` fixed at each of the already-in-use max moduli across the landed regimes (`m in {9, 19, 43}`,
i.e. the largest modulus in the small/mid/large regimes already certified) and sweep `SB in {2730 (proven-good
default, held out as a sanity anchor), 300, 100, 43, 20, 10, 5, 3}` — bracketing from comfortably-safe down to
clearly-insufficient (fewer dims than codewords). `N_DIM = SB * R_MODULI` scales down accordingly per grid point
(a smaller synthetic sub-problem, not the full N=8192 substrate default — explicitly an ABLATION of the design
margin, not a claim about the production configuration).

**Task A (measurement, reused mechanism):** for each `(SB, m)` grid point, run `T` trials of
encode-decode-round-trip on random residues `r` in `[0, m)`; report per-sub-block argmax decode accuracy
(fraction where decoded `r' == r`) and the `nearmiss_frac_below_half` diagnostic (already defined in the landed
cells) as a function of `SB`.

**Task B (the genuine discriminator, new):** compute a PREDICTED decode-accuracy curve from a closed-form/
asymptotic formula derived from the lit-scanned theory (candidate form, exp_dev's call to refine per autonomy
declaration below): treat off-diagonal codeword correlation as a mean-zero complex quantity with variance
`~1/SB` (CLT over `SB` i.i.d. unit-phasor terms, per the landed cells' own "SNR ~ sqrt(sb)" comment), giving a
Gaussian-tail/Q-function estimate of per-codeword collision probability, union-bounded over the `m-1` competing
residues (the same `P_e <= (M-1)*Q(sqrt(...))` shape confirmed textbook-canonical by this drill's lit-scan,
Proakis-style M-ary detection). Compare the PREDICTED accuracy curve to the MEASURED curve (Task A) at every
grid point.

**Discriminator / controls:**
- **MECHANISM**: predicted-vs-measured accuracy agree (small residual) across the swept grid, AND both correctly
  identify the SAME collapse region (small `SB`) vs safe region (large `SB`).
- **CONTROL 1 (wrong-scaling-law formula)**: a deliberately mis-specified alternative prediction (e.g., linear-
  in-`SB` or `SB`-independent) that should track the measured curve WORSE than the correct formula — isolates
  that the specific `sqrt(SB)`/log-`m` scaling is load-bearing, not any monotonic-in-`SB` guess.
- **CONTROL 2 (scrambled-codebook)**: reuse the landed cells' existing derangement-before-CRT control pattern —
  should collapse decode accuracy at ALL `SB` including the large "safe" end, confirming the phase-linear
  structure (not just having many dimensions) is what the formula is actually modeling.
- **Real-data anchor**: `SB=2730` (the value every landed cell actually ships with) must land solidly in the
  formula's predicted-safe region with a wide margin — this is the retrospective validity check on the four
  already-HARD_PASS cells' own boilerplate assumption; a genuine finding either way (confirms the 4 landed
  cells' informal margin claim was correct, or reveals it was closer to the edge than assumed).

**Pre-registered bands (deflated per role discipline):**
- **HARD-PASS**: measured accuracy transitions from >=0.95 to <=0.20 within the swept `SB` grid (i.e. the
  boundary is actually reachable at this scale, not just always-safe or always-broken), AND the closed-form
  prediction's transition point is within a factor of ~2x of the measured transition point, AND control 1
  (wrong-scaling formula) misses the transition location by a larger margin than the correct formula, AND
  control 2 (scrambled codebook) stays collapsed at every `SB` including the safe end. P_deflated = **0.40**
  (capped novel-synthesis; the qualitative existence of a collapse boundary is high-confidence given the
  landed cells' own SNR argument, but a *specific formula's* quantitative accuracy at a 2x tolerance is a real,
  not-yet-attempted, prediction with genuine failure modes — e.g. the discrete-integer-frequency codebook may
  have a different constant, or worse tail behavior, than a fully-continuous-random-phasor idealization).
- **HARD-FAIL**: the measured curve never leaves the "safe" region across the swept grid (formula is
  untestable at this scale — grid mis-designed, needs smaller `SB` than swept) OR the closed-form prediction
  misses the transition location by >5x OR control 1 tracks the measured curve AS WELL AS the correct formula
  (would mean the specific scaling law is not actually load-bearing — any reasonable monotonic guess predicts
  it just as well, a real negative worth reporting prominently, not burying).
- **MIDDLE**: transition exists and formula is directionally right (correct qualitative location) but outside
  the 2x quantitative tolerance — a legitimate, reportable partial result (the substrate can identify THAT a
  margin exists but not yet precisely predict WHERE, a real and honestly-scoped gap for a follow-up drill).

**Cost:** cheap, CPU-only, numpy-scale, no GPU, no pool/re-encode dependency (self-contained synthetic codebook,
same class as the 4 landed cells). Estimated ~150-200 new lines (grid-sweep wrapper + the closed-form prediction
function + the wrong-scaling control + reused encode/decode/scramble machinery). No referent gate (does not
touch `cert_ledger.jsonl` or any live pipeline state) — remote-dispatchable to `remote_cpu_queue` now,
independent of the parked cert-ledger self-reasoning FULLs.

**Autonomy note (exp_dev owns):** the exact closed-form formula's constant/shape (whether a Gaussian-tail
Q-function, a simpler Chernoff/union-bound proxy, or an empirically-fit power law is used for the "prediction"
arm), the exact grid points beyond the named minimum, trial/seed counts, and queue/timeout — this note names the
mechanism and the falsifiable comparison, not the implementation, per [[feedback-no-experiment-design-in-
prompts]]-equivalent discipline.

---

## 4. BRAIN GROUNDING (task's Q4) — honest analog, and an honest departure from forcing one

**The most apt grounding for THIS specific check is engineering, not neuroscience, and this note says so
explicitly rather than stretching a brain analogy to fit.** The same lit-scan that supplied Sec. 2b's framing
(RNS hardware overflow detection, BIST, noise-margin analysis) is the substrate's OWN primary reference
tradition for this exact mechanism (Szabo & Tanaka 1967; Hung & Parhami 1994 — already cited in the landed
compare cell) — a static design-time margin choice, verified (or not) against a closed-form spec, IS what this
candidate cell is. Forcing a neuroscience frame onto "did we choose enough sub-block dimensions" would be a
weaker, more strained fit than the literature the substrate already cites for the mechanism itself.

That said, the honest brain-ADJACENT analog, at the right level of generality (per standing
[[feedback-mechanism-abstraction-lossy]] discipline — analogy at the level it is genuinely supported, not
over-extended): **classical signal detection theory** (Green & Swets 1966, *Signal Detection Theory and
Psychophysics*) is the shared mathematical ancestor of BOTH the engineering noise-margin literature above AND
psychophysical threshold/limen research (contrast sensitivity functions, just-noticeable-difference /JND/
curves) — organisms have well-characterized, resource/noise-contingent DETECTION THRESHOLDS (a bat's
echolocation range under signal-to-clutter constraints; a retina's contrast threshold under photon-noise limits)
that are conceptually the SAME kind of claim as "how small can SB get before decode fails" — a capacity boundary
set by a signal-to-noise ratio, not a discrete correctness question. This is a real, well-supported connection
at the level of SHARED MATHEMATICAL STRUCTURE (both are Q-function/ROC-curve problems), but it is NOT evidence
that the brain performs this SPECIFIC kind of introspective margin-check on its OWN representational capacity —
that would be a stronger and unsupported claim, distinct from (and honestly weaker than) the ACC-conflict-
monitoring/Nelson-Narens-monitor-vs-control grounding the sibling cert-ledger self-reasoning notes correctly
use for CONTENT-level self-checking (that framing does not apply cleanly here, and this note does not borrow it).
**Net: engineering analogy is the load-bearing one; brain analogy is a genuine but secondary, weaker, shared-math
connection — reported honestly rather than inflated to satisfy the question's shape.**

---

## Cheap decisive test

Build and run `exp_rns_subblock_margin_selfcheck_v1 --smoke` locally (no GPU, no queue dispatch, reuses existing
verbatim decode functions). If the measured accuracy curve shows a real transition across the swept `SB` grid
AND the closed-form prediction lands within 2x of the measured transition point AND the wrong-scaling control
misses by a wider margin AND the scrambled-codebook control stays collapsed throughout — that is the decisive
confirmation that this is a genuine, falsifiable, config-contingent self-check, not a re-confirmation of already-
exact algebra. If the curve never transitions within the swept grid, the grid was mis-designed (extend `SB`
smaller) before concluding anything about the formula.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL, repeated from Sec. 3 for scan-ability)

- HARD-PASS: measured accuracy transitions from >=0.95 to <=0.20 within the grid; predicted transition point
  within 2x of measured; wrong-scaling control misses by a wider margin; scrambled control stays collapsed at
  every SB. P_deflated = 0.40.
- HARD-FAIL: no transition observed in the swept grid, OR prediction misses by >5x, OR the wrong-scaling control
  tracks the measured curve as well as the correct formula (scaling law not actually load-bearing). P = 0.20.
- MIDDLE: transition exists, formula is qualitatively right but outside 2x tolerance. P = 0.30.
- Explicitly NOT recommended for a cell: CRT-reconstruction-exactness-given-coprime-moduli, and
  add/multiply-homomorphism-exactness — both already checked deterministically at write time in all 4 landed
  cells (`crt_selftest`, `*_homomorphism_selftest`); a new cell here would be a tautological re-confirmation
  (BLR-theory-grounded, Sec. 2a), P(informative finding) is not meaningfully assignable because the outcome is
  fixed by construction.

---

## CROSS-THREAD SYNTHESIS

- **With `notes/research_self_reasoning_capability_gap_2026-07-05.md` / `..._next_rungs_ladder_2026-07-05.md`**:
  those notes correctly scoped self-reasoning about the cert-ledger CONTENT (currency retrieval, conflict
  flagging, global consistency) — all explicitly parked behind the remote-deploy referent gate for their FULL
  runs. This note's cell is the DESIGN/MECHANISM-level complement those notes flagged as out of scope for
  themselves, and it does not share their parked-deploy dependency — it is a purely synthetic-codebook cell,
  same class as the 4 landed math cells, remote-dispatchable now.
- **With `notes/research_math_capability_translation_first_cell_2026-07-05.md`**: that note's Q4 already
  identified VeriCoT/HERMES/SymCode (2025 neurosymbolic self-verification frameworks) converging on "validity
  checking requires translating a claim into a discrete formal substrate" — this note's contribution is the
  NEXT-LEVEL question those frameworks do not address: verifying not a CLAIM but the DESIGN MARGIN of the
  formal substrate itself (does the chosen encoding have enough headroom to be trustworthy at all).
- **With the 4 landed math-arithmetic cells** (`add_chain_v1`, `subtract_compare_v1`, `multiply_star_v1`, all
  FULL HARD_PASS, re-verified on disk this drill): this note's cell is a retrospective VALIDITY AUDIT of an
  assumption all three share verbatim ("sb=2730 >> max modulus 43") — not a criticism of those results (their
  own measured near-miss-fraction of 1.000 at the shipped config is real and solid), but an honest flag that the
  MARGIN claim underlying that solidity has never itself been tested at the boundary, exactly the BIST-vs-
  margin-analysis gap identified in Sec. 2b.
- **With `exp_crt_module_scaling_battery_v1`** (HARD_PASS, module-COUNT scaling under bipolar/additive codes):
  a different mechanism (superposition capacity, candidate #3, Sec. 1) already covers a structurally similar
  "how far can I push this parameter before it breaks" question for a DIFFERENT axis and a DIFFERENT encoding —
  cited as precedent that this general SHAPE of question (sweep-and-find-the-cliff) is a proven, valuable
  pattern for this substrate, reinforcing that the SB-vs-m version is a reasonable, not speculative, next
  application of the same pattern to the arithmetic set specifically.
- **Per [[feedback-research-every-finding-for-mechanism-and-envelope-push]]**: the honest, direct finding this
  drill measured (not asserted) — the near-miss fraction is 1.000 at the shipped `SB=2730` in the landed add
  cell's own metrics, meaning the shipped config sits nowhere NEAR any measured boundary — is itself the
  motivating data point for why the margin has never been probed: everything has always been comfortably safe,
  which is exactly the condition under which an unexamined design-margin assumption can silently persist
  uncorrected for the longest, per the same BIST-vs-margin-analysis logic in Sec. 2b.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

- If the cell HARD-PASSes: the substrate (or, more precisely, a cell built on the substrate's own decode
  primitives) gains a genuine, falsifiable, config-contingent audit of its own arithmetic-set's design margin —
  a real (if narrow) instance of "reasoning about its own mechanism," distinct from and complementary to the
  cert-ledger content-reasoning ladder. This would also retrospectively VALIDATE (not just assume) the shipped
  `SB=2730` choice across all 4 landed math cells, upgrading their informal boilerplate comment into a measured,
  falsified-if-wrong claim.
- If it HARD-FAILs (wrong-scaling control ties the correct formula, or the prediction misses by >5x): this would
  be a genuinely useful negative — it would mean the substrate's decode-margin behavior does not follow the
  textbook Welch-bound/Q-function intuition cleanly at this specific (discrete-integer-frequency) codebook
  construction, and any future capacity claims for this construction should be measured, not assumed from the
  general theory, per [[feedback-measured-bounds-are-method-config-contingent-not-fundamental]].
- **Explicitly out of scope, still:** this stays entirely on the "monitor," never "control," side of the
  Nelson & Narens (1990) boundary already banked by the sibling cert-ledger notes — the cell only ever reports a
  margin/prediction-vs-measurement number in its own `metrics.json`; it never changes `SB`, never edits a landed
  cell's config, never auto-triggers a rebuild. A human (or Strategy) reads the flag and decides. This is
  monitoring of mechanism design, not self-modification of mechanism design — the same honest line the
  self-reasoning-ladder note already drew for content-level checks, restated here for design-level checks.
- **Cap_map row candidate:** if built and it lands, this is grounds for Strategy to consider a
  `cap_math_mechanism_margin_audit` sub-row distinct from the existing arithmetic-composition candidacy — 
  Strategy decides; research does not modify cap_map.

---

## CITATIONS (verified external count this drill: 24, across 3 lit-scans; 0 re-used from sibling notes since
this is a structurally distinct question from the cert-ledger content-reasoning ladder)

**Lit-scan 1 — program self-testing/checking theory (8 sources):**
1. Blum, M. & Kannan, S. (1989/1995). "Designing Programs that Check Their Work." *JACM* 42(1):269-291.
   https://dl.acm.org/doi/10.1145/200836.200880
2. Blum, M., Luby, M., & Rubinfeld, R. (1993). "Self-Testing/Correcting with Applications to Numerical
   Problems." *JCSS* 47(3):549-595. https://www.sciencedirect.com/science/article/pii/002200009390044W
3. Goldreich, O., Goldwasser, S., & Ron, D. (1998). "Property Testing and Its Connection to Learning and
   Approximation." *JACM* 45(4):653-750. https://dl.acm.org/doi/10.1145/285055.285060
4. Rubinfeld, R. & Sudan, M. (1996). "Robust Characterizations of Polynomials with Applications to Program
   Testing." *SIAM J. Comput.* 25(2):252-271. https://epubs.siam.org/doi/10.1137/S0097539793255151
5. Kiwi, M., Magniez, F., & Santha, M. (2001). "Exact and Approximate Testing/Correcting of Algebraic
   Functions: A Survey." LNCS 2292:30-83.
6. Freivalds' algorithm (1979, MFCS) — cheap randomized consistency check (A(Br) vs Cr) in place of
   recomputation; https://en.wikipedia.org/wiki/Freivalds%27_algorithm
7. Rubinfeld, R. "A Mathematical Theory of Self-Checking, Self-Testing and Self-Correcting Programs" (thesis).
   https://people.csail.mit.edu/ronitt/papers/tskel.pdf
8. (Flagged, not a citation): no classical paper found self-testing CRT reconstruction by name specifically;
   the BLR-style extension to CRT is this drill's own structurally-motivated synthesis, not a cited result.

**Lit-scan 2 — RNS hardware overflow / BIST / noise margin (8 sources):**
9. Szabo, N.S. & Tanaka, R.I. (1967). *Residue Arithmetic and its Applications to Computer Technology.*
   McGraw-Hill. (Overflow-via-redundant-modulus / core-function detection, pp.100-104 tradition.)
10. "Fast Overflow Detection in Moduli Set {2^n-1, 2^n, 2^n+1}." ResearchGate 51999853.
11. "RNS Overflow Detection by Operands Examination." IJCA 85(18), 2014.
12. US Patent 5107451, overflow detection in RNS multiplication.
13. "Built-in self-test" overview (signature analysis / LFSR / MISR, stuck-at fault model).
    https://grokipedia.com/page/Built-in_self-test
14. US Patent 6760873, source-synchronous BIST timing-margin extension (flags margin analysis as a distinct
    add-on capability, not default BIST coverage).
15. "Noise margin" (VOH/VOL/VIH/VIL definitions, conditional-not-unconditional guarantee).
    https://grokipedia.com/page/Noise_margin
16. Hung, C.Y. & Parhami, B. (1994). "An approximate sign detection method for residue numbers..." *Computers
    & Mathematics with Applications* 27(4):23-35. (Already cited by the landed compare cell; re-confirmed here
    for the sign/core-function detection tradition specifically.)

**Lit-scan 3 — high-dimensional capacity/separability bounds (8 sources):**
17. Johnson, W.B. & Lindenstrauss, J. (1984). *Contemp. Math.* 26 (JL lemma).
    https://en.wikipedia.org/wiki/Johnson%E2%80%93Lindenstrauss_lemma
18. Welch, L.R. (1974). "Lower bounds on the maximum cross correlation of signals." *IEEE Trans. Inform.
    Theory.* (Welch bound — worst-case floor on pairwise correlation for M unit vectors in D dims.)
19. Cohn, H. & Zhao, Y. (2014). "Sphere packing bounds via spherical codes." arXiv:1212.5966.
20. Kabatiansky, G. & Levenshtein, V. (1978). Spherical-cap packing bound (continuous-alphabet GV/Hamming
    analog).
21. Shannon, C.E. (1959). "Probability of error for optimal codes in a Gaussian channel." *Bell Syst. Tech. J.*
    38(3):611-656. (Sphere-packing bound, continuous/AWGN case.)
22. Donoho, D. & Tanner, J. (2005/2009). Compressed-sensing phase-transition curve. *PNAS*; *Phil. Trans. R.
    Soc. A.*
23. Donoho, D., Maleki, A., & Montanari, A. (2011). "The Noise-Sensitivity Phase Transition in Compressed
    Sensing." arXiv:1004.1218. (Finite-N transition zone shrinks toward the asymptotic cliff as N grows.)
24. Proakis, J. *Digital Communications* — M-ary orthogonal signaling error probability
    `P_e <= (M-1)*Q(sqrt(d^2/2N0))`, Gallager random-coding exponent; textbook-canonical closed-form basis for
    Sec. 3's Task B prediction.

**Substrate-internal (verified on disk this drill, not counted toward external total but load-bearing):**
- `data/exp_math_rns_add_chain_v1/metrics.json` (FULL HARD_PASS, re-verified this drill: near-miss fraction
  1.000 at shipped SB=2730 — the motivating "never near the boundary" data point).
- `data/exp_math_rns_subtract_compare_v1/metrics.json` (FULL HARD_PASS, re-verified this drill).
- `experiments/exp_math_rns_add_chain_v1.py`, `exp_math_rns_subtract_compare_v1.py`, `exp_math_rns_multiply_star_v1.py`
  (all 3 read in full this drill; `crt_selftest()`/`*_homomorphism_selftest()` confirmed present verbatim in all 3;
  `SB = N_DIM // R_MODULI = 2730` and the "sb=2730 >> max modulus 43" comment confirmed verbatim in all 3).
- `experiments/exp_crt_capacity_boost_v1.py` (HARD_FAIL/superseded, read in full), `exp_crt_module_scaling_battery_v1.py`
  (HARD_PASS, read in full) — confirmed as a DIFFERENT mechanism (additive/bipolar bundling) from the phase-linear
  RNS decode this note targets.
- `data/substrate_index/meta/cert_ledger.jsonl` (1451 rows; no `math_rns_*` self-verification-of-mechanism atom
  exists yet — confirmed via targeted query this drill).
- `notes/research_self_reasoning_capability_gap_2026-07-05.md`, `notes/research_self_reasoning_next_rungs_ladder_2026-07-05.md`,
  `notes/research_math_capability_translation_first_cell_2026-07-05.md`, `notes/research_math_arithmetic_basis_next_primitives_2026-07-05.md`
  (all read in full this drill to confirm no overlap/duplication before proposing a new cell).

---

*Research complete 2026-07-06. Internal scour: full read of all 4 landed math-arithmetic cells' source +
metrics.json, 2 prior CRT capacity cells' source, and 4 same-day-adjacent research notes on the cert-ledger
self-reasoning ladder, before any external dispatch. 3 parallel Sonnet lit-scans (program self-testing/checking
theory; RNS hardware overflow/BIST/noise-margin; high-dimensional capacity/separability bounds), generic terms
only, no substrate-novel mechanism names off-platform. Lit-scan calibration applied (deflate 0.15-0.25;
novel-synthesis cap 0.50, applied to the one genuine prediction; the two tautological candidates are explicitly
NOT assigned a dispatch-worthy P, per the task's own instruction to say so when a candidate is by-construction).
HARD-FAIL thresholds specified. Notes-only drill per Director instruction — no cell built, no dispatch, no
routing files (USER-locked ferry-deprecation override; all actionable content, including the ready cell spec,
delivered in this note).*
