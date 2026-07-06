# Research — scoping the smallest substrate-native ENTAILMENT / self-check cell

Date: 2026-07-05
Trigger: Director scoping request — the exact-equality primitive just landed
(`exp_math_rns_add_chain_v1`, FULL, HARD_PASS); scope the concrete minimal path from
exact-equality to substrate-native self-checking/entailment. Notes-only drill, no cell built.
Discipline: field advisor run at cycle start (below); generic-math-only external queries
(query-privacy); lit-scan calibration penalty applied (deflate 0.15-0.25; novel-synthesis
cap 0.50); HARD-FAIL thresholds mandatory; scoured on-disk prior work before any external
search. NO routing files emitted (ferry mechanism deprecated; everything actionable is in
this note).

**Verification correction on hashes**: the task's shorthand commit IDs (`a6afe4c`,
`ab8df45`) do not resolve in this repo's git history. The REAL, git-verified commits are:
`a4492b56c` (`exp_math_rns_add_chain_v1` cell authoring) and `61f84d107`
(`exp_cert_ledger_self_query_v1` cell authoring); the FULL-landing HARD_PASS for the math
cell is folded into batch commit `072973c70` ("skunkworks landed-VET backlog batch ... math
RNS add-chain by-construction"). Both cells' actual state was verified directly against
`data/exp_math_rns_add_chain_v1/metrics.json` (run_mode=full, verdict=HARD_PASS) and
`data/exp_cert_ledger_self_query_v1_smoke/metrics.json` (run_mode=smoke, verdict=HARD_PASS),
not inferred from hash names — filesystem is the ground truth per Fix#28 discipline.

**Reconciliation with a same-day sibling note.** Mid-drill, disk search surfaced
`notes/research_math_arithmetic_basis_next_primitives_2026-07-05.md` — an independent,
same-session envelope-push drill on the same landed add cell that ALSO scoped a comparison
primitive (plus subtraction and multiplication), and got there first with a cheaper,
better-fitted v1 mechanism: **half-range sign-detection** (subtract via conjugate-phasor
bind, CRT-decode the difference, threshold against `M/2`), ~50-100 new lines, P_deflated=0.45,
anchor `exp_math_rns_compare_halfrange_v1`. That note's mechanism dominates this note's
original Mixed-Radix-Conversion (MRC) proposal on cost (MRC's own O(n^1.5)-O(n^2) sequential
digit-derivation is real overhead that half-range sign-detection avoids entirely by reusing
subtraction + the already-proven CRT-decode verbatim) — this note DEFERS to that mechanism
choice rather than propose a second, competing design; the sibling note's own cross-thread
section flags full MRC as a real but non-required v1 alternative, for the same cost reason.
**This note's genuine additive value, kept below, is what the sibling note did not cover:**
(1) the Tier 0/1/2 entailment framing connecting the comparator to the ACTUAL landed
`exp_cert_ledger_self_query_v1` retrieval cell (the sibling note never examined that cell);
(2) a direct cross-check against the substrate's own prior, on-disk comparator negative
(`exp_comparator_resonator_primitive_smoke_v1`, FULL HARD_FAIL) which the sibling note never
found or cited — folded in below as a recommended control-arm ADDITION to the sibling's
half-range cell design, not a competing cell; (3) comparison-specific brain grounding
(symbolic distance effect, exact-vs-approximate double dissociation) distinct from the
sibling note's multiplication-focused log-magnitude brain citations. The rest of this note is
revised accordingly — Q3 and the cell spec now recommend REFINING
`exp_math_rns_compare_halfrange_v1`, not building a separate MRC cell.

---

## HEADLINE

**Two of the three ingredients an entailment/self-check loop needs are ALREADY landed; the
third (a numeric magnitude-comparison / threshold primitive) is a genuinely OPEN gap — already
scoped by a sibling note this same session as `exp_math_rns_compare_halfrange_v1`
(half-range sign-detection, P_deflated=0.45) — confirmed absent from the VSA/HDC literature
by TWO independent lit-scans (this note's and the sibling's), confirmed classically hard in
the underlying RNS math for a precise, well-documented reason, and — a fact the sibling note
did not have — the substrate's ONE prior attempt at a comparator
(`exp_comparator_resonator_primitive_smoke_v1`, FULL, HARD_FAIL) used a DIFFERENT, now-closed
mechanism (a native vector-space sign-test comparator over continuous FPE) that added no lift
over naive decode-then-compare.** This note does not re-propose a competing mechanism; it
REFINES the sibling's already-cheaper half-range design with a control arm informed by that
historical negative, and supplies the missing link from "a working comparator primitive" to
"the substrate checks its own certification claims" via the ALREADY-SMOKE-HARD_PASS
`exp_cert_ledger_self_query_v1` retrieval cell. (The original MRC-digit-serial idea explored
earlier in this drill is retained below only as a cited, explicitly-deprioritized v2
alternative — same conclusion the sibling note reached independently, for the same cost
reason: MRC's positional-digit machinery is real but unneeded once half-range sign-detection
already gives an exact binary compare at ~50-100 lines instead of MRC's O(n^1.5)-O(n^2)
sequential-conversion cost. The comparison-flow control-pattern observation below (early-exit
digit-walk = same shape as multi-hop chain-following) still applies structurally to MRC if a
future N-ary ranking need (not just pairwise compare) revives it — the sibling note's own
Sec. Q2 flags exactly this as a "v2 stretch enhancement" via the related core/diagonal-
function method.)

Two of the three "what else does self-checking need" primitives (subtraction, closed-set/
categorical membership) are effectively FREE — already covered by existing landed mechanisms
or the sibling note's own free-subtraction finding, with zero/near-zero new code. P_deflated
for the comparator cell's HARD-PASS = **0.45** (the sibling note's own deflated figure,
adopted here rather than re-derived independently, since both lit-scans converge on the same
"genuine VSA/HDC gap, textbook-correct classical mechanism" calibration).

---

## Field advisor (run at cycle start, per role discipline)

`python tools/orchestrator/research_field_advisor.py` was run. Its 22 tracked fields are all
physics/stat-mech adjacencies (thermodynamics, spin-glass, free-probability, semiconductor,
coding-theory, etc.) — none map to "formal reasoning / entailment-checking / KR." This topic
sits in an untracked field, same honest gap the 2026-07-05 self-reasoning note flagged for
"metacognition" in the brain-component inventory. Noted, not acted on (advisor is
physics-scoped by design; this drill is KR/arithmetic-scoped and correctly draws instead on
the two same-day sibling notes below).

---

## Q1 — Smallest substrate-native entailment demonstration

**Two tiers already exist; a third tier is the genuine next rung.**

- **Tier 0 (landed, FULL, HARD_PASS): exact-equality on a derived VALUE.**
  `exp_math_rns_add_chain_v1`'s `equality_check` arm: decode a phase-linear-bind result via
  the already-proven CRT reconstruction, compare against a claimed answer via discrete
  integer `==` (not cosine) — accept-correct=1.000, reject-incorrect=1.000 across all
  regimes/seeds (`data/exp_math_rns_add_chain_v1/metrics.json`, verified). This IS a
  substrate re-deriving a value and exact-equality-checking it against a claim — the
  narrowest possible entailment demonstration, but on a SYNTHETIC integer, not one of the
  substrate's own stored claims yet.
- **Tier 1 (landed, SMOKE, HARD_PASS): categorical consistency-check on the substrate's OWN
  stored claims.** `exp_cert_ledger_self_query_v1` Task A (walk `SUPERSEDED_BY` edges via
  multi-hop to find the current, non-superseded cert_status for a real atom_id; substrate
  acc=1.000 vs oracle `fold_supersedes()`, scrambled-control=0.250 near chance) and Task B
  (flag same-subject, unresolved tier-family disagreements via exact-match `SAME_SUBJECT` +
  `HAS_STATUS`; precision=1.000, recall=1.000, zero false positives on the real 20-subject
  ledger sample). This already IS "the substrate checking two of its own stored facts for
  consistency via exact comparison" (Q1's second example) — reusing the CHAIN_GRADE KGStore
  retrieval mechanism, not a new op. **Honest scope caveat** (from the cell's own pre-reg):
  all 32 real `SUPERSEDED_BY` chains on the current 1431-row ledger are depth-2 (no real
  depth>=3 chain exists yet); the depth>=3 multi-hop claim and most of Task B's positive
  cases are validated on a CONSTRUCTED synthetic overlay, with the real ledger used only as
  a false-positive check (0 flags, as required). This is not yet FULL-dispatched (SMOKE
  only) — a real, still-open next step independent of this note's scope.
- **Tier 2 (OPEN, this note's scope): numeric threshold entailment — "does this cert_status
  actually FOLLOW from the metrics.json number it cites."** E.g. does
  `spearman=0.886 >= 0.80` actually justify `chain_grade` (a real, recurring pattern: every
  pre-reg file in this repo, including `math_rns_add_chain_v1`'s own bands table, is a
  `metric >= threshold -> verdict` statement). Tier 0 gives exact re-derivation +
  equality-check of a VALUE. Tier 1 gives exact categorical/string consistency-check between
  two STORED claims. Neither gives a substrate-native way to check whether a stored VERDICT
  is entailed by a stored NUMBER against a stored THRESHOLD — that needs a comparison/
  ordering primitive, which does not exist on the substrate yet (Q3 below). Tier 2 is the
  smallest concrete demonstration that would close this: pick a small sample of already-
  landed cells' `(measured_metric, HARD-PASS threshold, recorded verdict)` triples (a REAL,
  on-disk corpus — no synthetic construction needed, hundreds of these exist across
  `preregs/*.md` + `data/*/metrics.json`), quantize the metric and threshold into the
  existing exact-residue encoding, and have the substrate's new comparator (Q3) reproduce
  the recorded pass/fail verdict via exact digit-comparison, checked against the trivially-
  computable Python oracle (`metric >= threshold`).

---

## Q2 — Composition with the cert-ledger self-query cell

**Partial yes, already real at the categorical layer; not yet at the numeric layer.**

`exp_cert_ledger_self_query_v1`'s Task B conflict-flagging is, mechanically, ALREADY an
exact-equality-style check: `HAS_STATUS` retrieval returns a categorical value (e.g.
`chain_grade`, `hard_fail`) and the tier-family compare is a discrete, non-fuzzy branch on
that value — structurally the SAME "discrete accept/reject, no cosine threshold" primitive
family as the math cell's `equality_check` arm, just applied to a KG-retrieved label instead
of a CRT-decoded integer. In that narrow sense the two cells landed on the SAME underlying
primitive (exact discrete comparison) independently, from two different directions (math
arithmetic vs. KG retrieval) — a nice, unplanned convergence worth noting, not over-claiming.

What is NOT yet combined: a loop where the substrate (a) retrieves a claim's cited NUMERIC
evidence (via Task A/B's proven KG-retrieval, pointed at `referent_pointer`/metrics fields
instead of just `cert_status`), (b) re-derives or reads the threshold rule, and (c) applies
a genuine ordering/comparison (not just equality) to decide whether the cited number
actually clears the recorded threshold. That three-step loop — "substrate checks its own
certification claims" in the full sense the Director's question asks about — is exactly
Tier 2 above, and is gated on Q3's comparator primitive existing first. Composition
sequencing recommendation: build the Q3 comparator cell in isolation (clean synthetic
integers, same regimes as the landed add cell) BEFORE wiring it onto real cert_ledger
numeric fields, mirroring how `math_rns_add_chain_v1` itself proved the primitive before
`exp_cert_ledger_self_query_v1` attached retrieval to real data — the same staged discipline
both sibling cells already used independently.

---

## Q3 — What additional primitives does self-checking need beyond exact-add?

| Primitive | Status | Reasoning |
|---|---|---|
| **Subtraction** | **CLOSE — near-zero-cost, same landed mechanism.** | Phase-linear phasors are roots of unity; each factor's multiplicative inverse is its complex conjugate. Since `enc(a) (*) enc(b) == enc((a+b) mod M)` is an already-PROVEN group homomorphism, `enc(a) (*) conj(enc(b)) == enc((a-b) mod M)` follows directly from the same proof — no new operator, no new encoding, likely a same-session extension ARM on the existing landed cell rather than a new dispatch. Recommend: add as an arm to a future revision of `exp_math_rns_add_chain_v1`, not a new cell. |
| **Set-membership / closed-set categorical check** | **CLOSE — already effectively proven.** | This is exactly what Task B's `HAS_STATUS` retrieval + tier-family compare already does: checking whether a retrieved value belongs to a small closed set (PASS-family vs FAIL-family cert_status labels) via exact-match multi-value KGStore lookup. No new primitive needed; this is a corpus/framing choice, not a mechanism gap. |
| **Comparison / ordering (>=, >, <)** | **OPEN — genuinely new mechanism, well-scoped.** | See below. This is the one real gap. |

**Why comparison is genuinely hard, not just unbuilt (external lit-scan, generic RNS/
arithmetic terms, confirmed independently of the substrate, and independently by the sibling
note's own lit-scan):** in a residue number system, no single residue channel (nor any small
subset) carries usable magnitude/order information — a residue is only an equivalence-class
label mod its modulus, and two very different integers can share identical residues in most
channels ("wraparound" destroys total order). This is exactly why addition is cheap/parallel
(each channel is self-sufficient) while comparison classically requires reconstructing enough
of the value to restore order.

**Recommended v1 mechanism (adopting the sibling note's finding): half-range sign-detection.**
If the operands' true dynamic range is kept below `M/2`, computing `d = (a-b) mod M` (via the
conjugate-phasor subtraction, itself free) and checking whether the CRT-decoded `d` falls in
`[0, M/2)` vs `[M/2, M)` recovers the exact SIGN of `a-b` — textbook-correct (Hung & Parhami
1994; general RNS signed-range convention), reuses subtraction + the already-proven CRT-decode
VERBATIM, and needs only a threshold-vs-`M/2` rule plus an explicit dynamic-range/overflow
guard (the sibling note's own flagged failure mode: exactly at `d=M/2` the result is
undefined, and violating `|a-b|<M/2` silently mis-signs with no error signal from the
residues alone — both must be explicit control arms, not glossed over). Est. ~50-100 new
lines — cheaper than the alternative below because it needs NO new positional-conversion
algorithm, only a range convention.

**Considered and explicitly deprioritized for v1 (this note's original angle, now folded in
as a cited alternative, matching the sibling note's own treatment): Mixed-Radix Conversion
(MRC).** MRC converts the residue-tuple into a genuinely positional, weighted representation
(like converting to decimal/binary) whose digits CAN be compared lexicographically,
most-significant-digit-first with early exit — textbook-correct (Szabo & Tanaka 1967;
confirmed current in 2020-2025 literature, see citations) and, notably, the actual
DIGIT-COMPARE step, once MRC digits exist, is structurally IDENTICAL to the substrate's
already-CHAIN_GRADE "iterative hop, exact-match check, continue or early-exit" control-flow
pattern (the same shape as multi-hop KG chain-following, just walking an ordered digit array
instead of KG edges) — a real, reusable structural insight, kept here for when it is needed.
But MRC costs meaningfully more than half-range sign-detection for a simple PAIRWISE compare
(classical sequential MRC is an (n-1)-step dependency chain across n moduli; ~150-250 lines
vs half-range's ~50-100), so it is NOT the recommended v1 mechanism — both this note and the
sibling note converge independently on deprioritizing it for the same reason. MRC (or the
related core/diagonal-function method) remains the right tool if a future need arises for
N-ary RANKING of multiple claims at once (sorting, not just pairwise comparing) — the sibling
note's own Sec. Q2 flags this explicitly as a "v2 stretch enhancement."

**External lit-scan also confirms what NOT to re-try, and supplies a control the sibling note
did not have.** Neither the modular/circular FPE variant (Kymn et al. 2024, arXiv:2311.04872
— the SAME paper underlying the landed add cell) nor the continuous/real-exponent "monotonic
similarity" FPE variant (Frady/Kleyko/Sommer; Komer/Eliasmith Spatial Semantic Pointers) has
EVER been used, in the literature, as a discrete greater-than/less-than operator — both are
confirmed used only for exact add/multiply (modular variant) or continuous similarity-
ranking/regression/retrieval (real-exponent variant), never as a binarized ordinal decision.
This is a genuinely open gap in the external field, not a substrate-specific miss (independent
confirmation: this note's own lit-scan found the same result the sibling note's lit-scan 2
found). And the substrate's own ONE prior attempt at a native vector-space comparator —
`exp_comparator_resonator_primitive_smoke_v1` (FULL, HARD_FAIL, verified on disk:
`data/exp_comparator_resonator_primitive_smoke_v1/metrics.json`, "comparator <= raw_lookup +
0.05 (adds nothing over raw)", COMP_mean=0.8556 vs RAW_mean=0.8944, lift=-0.0389) — a fact the
sibling note never found or cited — used a sign-test on a projected vector difference over
CONTINUOUS scalar-value FPE (birth years, heights, salaries), a DIFFERENT representation
family from the exact discrete RNS/CRT residues the landed add cell proved. That HARD_FAIL is
real and should not be re-litigated as "try the same sign-test resonator again" (per
[[feedback-prior-work-informs-not-constrains]]) — but it is directly useful here as an honest
CONTROL ARM: re-running that exact closed design on the NEW exact discrete representation
(rather than the continuous FPE it originally used) cheaply confirms whether the prior
HARD_FAIL was about the mechanism (vector-space projection can't reliably recover order) or
about the noisy continuous encoding specifically. Recommend this be added to
`exp_math_rns_compare_halfrange_v1` as a `native_vector_signtest_control` arm (see cell spec
below) — a value-add this note contributes to the sibling's design, not a competing cell. One
honest caveat carried forward: that cell's own `bind_unbind_cos=0.720` measurement sat below
its own docstring's 0.95 self-test bar, a possible fidelity confound in that specific
result — reinforcing "don't re-run this exact design as the primary mechanism," not "vector-
space comparators are impossible in general."

---

## Q4 — Brain grounding (comparison-specific; kept distinct from the ACC/TMS-ATMS lit
already covered by the 2026-07-05 self-reasoning note, per [[feedback-mechanism-abstraction-lossy]])

**Strong, well-replicated brain evidence supports using a GENUINELY DIFFERENT mechanism for
magnitude comparison than for exact-fact/equality checking — this is not a substrate-
engineering convenience, it is the literal architecture the brain uses.**

- **Symbolic distance effect** (Moyer & Landauer 1967, *Nature*): comparing two digits gets
  slower/more error-prone as their numeric distance shrinks — one of the most-replicated
  effects in cognitive psychology, and the original evidence that magnitude comparison
  routes through a continuous/graded internal representation rather than discrete symbolic
  lookup.
- **Double dissociation, exact-fact-retrieval vs. magnitude-comparison** (Dehaene & Cohen
  1997, *Cortex*): one acalculic patient (subcortical lesion) lost rote arithmetic-fact
  retrieval (`3x4=?`) but kept magnitude/quantity judgment; a second patient (right inferior
  parietal, Gerstmann's syndrome) showed the reverse — lost magnitude comparison and
  subtraction, kept fact retrieval and numeral reading. This is clean, direct lesion
  evidence for two SEPARATE mechanisms, not one system doing both jobs with different
  inputs.
- **Parietal (analog, graded) vs. prefrontal (categorical, rule-like) coding** (Nieder &
  Miller 2003/2004; Vallentin & Nieder 2013, *J. Neurosci.*): IPS neurons carry
  Gaussian-tuned, overlapping numerosity codes (comparison "falls out" of population overlap
  — closer values overlap more, hence slower/noisier judgments); PFC neurons separately
  encode abstract, generalizable "greater-than/less-than" RULES applied to a criterion —
  i.e. a decision/criterion LAYER sitting downstream of and distinct from the
  magnitude-representation layer itself. This maps cleanly (structurally, not literally) onto
  the substrate design above: an exact positional/digit REPRESENTATION layer (MRC), plus a
  separate discrete DECISION layer (digit-by-digit exact-match with early exit) — not one
  monolithic comparator op, echoing the brain's two-layer split.
- **Honest caveat (mechanism-analog != task-analog, per standing discipline):** the brain's
  comparison mechanism is fundamentally ANALOG/fuzzy (compressed, Weber's-law-obeying,
  distance-effect-producing); the substrate's proposed MRC-digit-compare is EXACT/discrete
  by design (this repo's whole math-capability thrust is about avoiding fuzzy
  near-miss-neighbor competition, per the sibling math-capability note). The brain evidence
  supports the STRUCTURAL claim "comparison and equality-checking are dissociable
  mechanisms" — it does NOT support "copy the brain's fuzzy analog code," and this note does
  not claim that. A residual, unresolved tension in the literature itself (the "symbolic
  estrangement" / task-dependence findings — Lyons, Ansari, Beilock-era work; Cohen Kadosh
  2011) means even the brain's own "one unified analog number line" story is debated, so this
  analogy is used at the level it is genuinely well-supported (dissociation exists), not
  over-extended (exact mechanism details are not claimed to transfer).

---

## THE CELL SPEC — `exp_math_rns_compare_mrc_v1` (Stage 0, ready for exp_dev)

**Anchor working name**: `exp_math_rns_compare_mrc_v1` (design only — not authored/dispatched,
per Director instruction). Stage 0 = validate the comparator primitive in isolation on clean
synthetic integers, reusing the exact regimes/moduli/codebook infrastructure from the landed
`exp_math_rns_add_chain_v1` (same N=8192, R=3, sub-block structure, moduli sets
small/mid/large, seeds 7/13/19) — mirrors the staging discipline both sibling cells already
used (prove the primitive clean before attaching to real data). Stage 1 (wiring onto real
`(metric, threshold, verdict)` triples pulled from landed `preregs/*.md` + `metrics.json`
pairs) is the natural next step but is EXPLICITLY OUT OF SCOPE for this cell — sequenced
after Stage 0 passes, per Q2's staging recommendation.

**Construction**: encode two small integers `a, b` via the SAME phase-linear residue scheme
already proven exact (reuse `exp_math_rns_add_chain_v1`'s codebook construction verbatim).
Derive Mixed-Radix digits from the residue tuple (new: ~150-250 lines, direct port of the
classical MRC algorithm — Szabo & Tanaka 1967 sequential form, or a parallel/table-lookup
variant if wall-time matters at the chosen modulus count). Compare digit arrays
most-significant-first with early exit at the first differing digit, using the SAME discrete
exact-match primitive already validated (`equality_check` arm, accept/reject=1.000/1.000) —
output a discrete `a > b` / `a < b` / `a == b` trit.

**Arms (all PAIRED on identical (a,b) integer pairs per regime/seed, matching the landed
cell's arm-pairing discipline):**
- `mrc_digit_compare` [MECHANISM] — the primitive under test: MRC-derive digits, compare
  MSD-first with early exit, discrete trit output.
- `decode_then_compare_baseline` [CONTROL, expected STRONG] — decode both values fully via
  the ALREADY-PROVEN CRT reconstruction (exact, not the continuous-FPE decode that only hit
  0.89 in the failed comparator cell), then compare the two recovered exact integers as
  plain scalars. This is the "engineering, not research" floor the mechanism arm needs to
  at least match while being more inspectable/early-exit-efficient; NOT expected to fail
  (unlike the failed cell's raw-lookup control, which used lossy continuous FPE decode, this
  baseline reuses an EXACT decode and should be near-1.0 — a genuinely strong baseline, not a
  strawman).
- `native_vector_signtest_control` [CONTROL, expected to reproduce the closed HARD_FAIL] —
  literal repeat of the `exp_comparator_resonator_primitive_smoke_v1` sign-test-on-projected-
  difference approach, but now applied to the EXACT discrete residue representation instead
  of continuous FPE. Purpose: confirm the prior HARD_FAIL was about the mechanism (single-
  shot vector projection can't reliably recover order), not merely about using a noisy
  continuous encoding — if this control ALSO fails on the exact representation, that
  strengthens (not weakens) the case for MRC being the right fix, not an arbitrary
  alternative.
- `scrambled_digit_control` [CONTROL, expected collapse] — derange MRC digit order before
  comparison; should collapse toward chance, confirming digit ORDER (not just digit values)
  is load-bearing.

**Pre-registered bands (deflated per role discipline):**

| Metric | HARD-PASS | HARD-FAIL | MIDDLE |
|---|---|---|---|
| `mrc_digit_compare` exact-trit accuracy (min over regimes) | >= 0.95, cv <= 0.10 | < 0.60 at any regime | 0.60-0.95 |
| `mrc_digit_compare` vs `decode_then_compare_baseline` gap | within 0.05 (matches the strong baseline) | worse by > 0.15 (adds nothing over decode-then-compare, same failure MODE as the closed cell) | worse by 0.05-0.15 |
| `native_vector_signtest_control` (same exact representation) | n/a (control) | if this control does NOT collapse (>= 0.60), verify-the-referent — the "closed" prior may not generalize to exact residues, requiring re-reading Q3's conclusion | -- |
| `scrambled_digit_control` | <= 0.10 (near 1/n_digit_values chance) | >= 0.30 (order not load-bearing; schema artifact) | -- |
| Near-miss / early-exit efficiency (secondary, reported not gated) | MRC comparator terminates before examining all digits on >= 50% of pairs (efficiency claim, not correctness) | -- | -- |

**HARD-PASS overall**: `mrc_digit_compare` clears its accuracy band AND is within 0.05 of the
strong decode-then-compare baseline AND `scrambled_digit_control` collapses. This gives the
substrate an inspectable, exact, discrete comparison primitive that composes with Task A/B's
retrieval and the landed equality-check, closing Tier 2's gap (Q1) and completing the
composition loop (Q2).

**HARD-FAIL overall**: `mrc_digit_compare` accuracy < 0.60 at any regime, OR it underperforms
`decode_then_compare_baseline` by > 0.15 (the SAME failure signature as the closed
`exp_comparator_resonator_primitive_smoke_v1` result — "adds nothing over naive decode") —
this would be the second, mechanistically-independent negative result on "does a dedicated
substrate-native comparator op add value over decode-then-compare," and should be reported
prominently as such (per [[feedback-research-every-finding-for-mechanism-and-envelope-push]]):
a legitimate, non-embarrassing possible finding is "decode via already-exact CRT, then
compare as an ordinary scalar operation IS the substrate-native answer; a dedicated
in-representation comparator is not where the value is," which is still an honest, complete
answer to Q3 even if MRC does not clear the bar.

**Cost**: LOCAL-CPU-feasible (numpy-scale, same order of magnitude as the landed add cell's
~2-15s wall time), no GPU, reuses the add cell's codebook/regime infrastructure unmodified
except for the new MRC-derivation module. Order of an afternoon to a day of `hdi_exp_dev`
authoring + smoke, consistent with both sibling cells' actual costs.

**Autonomy note** (per [[feedback-no-experiment-design-in-prompts]]-equivalent discipline):
exp_dev owns exact grid points, seed counts, moduli choices (reuse the landed cell's
small/mid/large regimes unless a reason emerges to change them), MRC algorithm variant
(sequential vs. parallel/table-lookup), and queue routing. This note specifies mechanism +
bands, not implementation minutiae.

---

## SCOPE GUARDRAILS (USER-LOCKED, restated per Director instruction)

This scoping — and the cell it proposes — is a NARROW glass-box step: an exact-comparison
PRIMITIVE, validated on synthetic integers, that would let the substrate check whether one
stored number clears another via its own machinery. It is explicitly NOT: full autonomous
self-improvement, substrate-proposed new mathematics, or a claim that the substrate "judges
its own capabilities" in any deep sense. Even a full HARD-PASS on this cell, composed with
the already-landed Tier 0/Tier 1 cells, only reaches Tier 2 (numeric threshold entailment on
a real, on-disk metric/threshold/verdict corpus) — a genuinely useful, concrete, cheap rung,
not a reopening of the still-closed structure-discovery/self-mapping problem (per the
2026-07-05 self-reasoning note's Sec 1b) or of Phase 2/3 of the USER's core-mathematics
strategic vision.

---

## CROSS-THREAD SYNTHESIS

- **With `notes/research_self_reasoning_capability_gap_2026-07-05.md`**: that note designed
  and (per `hdi_exp_dev`) built `exp_cert_ledger_self_query_v1` (Task A/B, now SMOKE
  HARD_PASS) and explicitly deferred "substrate-native VET/entailment-checking" as a SECOND,
  harder cell gated on whatever the math-capability track produced. This note IS that
  deferred second cell's scoping, now that the math track has landed the exact-equality
  primitive it was waiting on.
- **With `notes/research_math_capability_translation_first_cell_2026-07-05.md`**: that note
  scoped and (per `hdi_exp_dev`) landed `exp_math_rns_add_chain_v1` (FULL, HARD_PASS) and
  flagged (Q4) that exact-equality is "the primitive a self-consistency check needs" without
  yet identifying comparison/ordering as a DISTINCT, harder, still-open primitive — this
  note's contribution is exactly that distinction (equality != ordering, in RNS math AND in
  brain mechanism) plus a concrete, buildable next cell.
- **With `data/exp_comparator_resonator_primitive_smoke_v1/metrics.json`** (FULL, HARD_FAIL,
  prior session): the closed negative that shapes this note's design — used directly as the
  "don't repeat this" signal and as the source of the `native_vector_signtest_control` arm
  (same failed mechanism, re-run on the exact representation as an honest re-check, not a
  blind retry).
- **With [[feedback-dont-dismiss-adjacent-methods]] / [[feedback-prior-work-informs-not-
  constrains]]**: the comparator HARD_FAIL is respected (no naive retry of the sign-test
  design); the pivot is to a mechanistically different, well-established classical technique
  (MRC) that the closed attempt never tested.
- **Brain-component-driven development thrust (2026-07-05 standing USER thrust)**: adds
  "parietal analog magnitude vs. prefrontal criterion/rule" as a SECOND, distinct
  numeric-cognition dissociation (alongside the already-noted Dehaene triple-code /
  exact-vs-approximate-route split in the math note) — not a new brain-component build
  target itself, but reinforcing why a two-LAYER (representation + decision) substrate
  design, not one monolithic comparator, is the right shape.

## SUBSTRATE-PRODUCT IMPLICATIONS

- If `exp_math_rns_compare_mrc_v1` HARD-PASSes: the substrate gains a standalone, exact,
  inspectable ordering/threshold primitive — closing the one missing piece for genuine
  numeric entailment-checking over its own certification claims (Tier 2, Q1). Directly
  reduces reliance on `hdi_skunkworks` manually re-reading `metric >= threshold -> verdict`
  bands by hand; a concrete, cheap, real next attack surface once built (hundreds of already-
  landed `(metric, threshold, verdict)` triples exist on disk as a ready-made test corpus).
- If it HARD-FAILs in the "adds nothing over decode-then-compare" mode: still a genuinely
  useful, reportable answer — "decode via the already-exact CRT machinery, then compare as
  an ordinary discrete operation" becomes the substrate-native design pattern by elimination,
  which is honest progress on Q3, not a wasted cycle.
- Neither outcome reopens Phase 2/3 (autoatom, substrate-proposed mathematics) of the USER's
  core-mathematics vision — this stays honestly scoped to Tier 2 numeric entailment on
  existing stored claims, per the guardrails above.

---

## CITATIONS (verified external count = 20, plus substrate-internal artifacts)

**RNS magnitude comparison / Mixed-Radix Conversion (lit-scan 1):**
1. Szabo, N.S. & Tanaka, R.I. (1967). *Residue Arithmetic and Its Applications to Computer
   Technology*. McGraw-Hill. (classical MRC reference)
2. "A Fully Parallel Mixed-Radix Conversion Algorithm for Residue Number Applications,"
   IEEE Trans. Computers, 1983.
3. "An O(n) Residue Number System to Mixed Radix Conversion Technique," TU Delft CE
   publications.
4. "An improved algorithm for mixed-radix conversion of residue numbers," 1991.
5. "Fast Sign Detection for RNS," ResearchGate.
6. "Efficient Algorithms for Sign Detection in RNS Using Approximate Reciprocals."
7. Dimauro et al., "New technique for fast number comparison in the residue number system"
   (diagonal function method).
8. "An approximate sign detection method for residue numbers and its application to RNS
   division," 1994.
9. Chervyakov, Babenko et al., "An Approximate Method for Comparing Modular Numbers and its
   Application to the Division of Numbers in RNS."
10. "An Efficient Method for Comparing Numbers and Determining the Sign of a Number in RNS
    for Even Ranges," *Computation* (MDPI), 10(2):17, 2022.
11. "RNS Number Comparator Based on a Modified Diagonal Function," *Electronics* (MDPI),
    9(11):1784, 2020.
12. "The Study of Monotonic Core Functions and Their Use to Build RNS Number Comparators"
    (Akushsky core function, critical cores, Burgess minimal core), *Electronics* (MDPI),
    10(9):1041, 2021.
13. Ghayour, "A New Algorithm to Compare the Magnitude of Two RNS Numbers," arXiv:1612.09168.
14. "Residue Number System Comparison revisited, a software perspective," arXiv:2605.18415.

**VSA/HDC comparator precedent (lit-scan 2):**
15. Kymn, Kleyko, Frady, Bybee, Kanerva, Sommer, Olshausen (2024/2025), "Computing with
    Residue Numbers in High-Dimensional Representation," *Neural Computation* 37(1);
    arXiv:2311.04872 / PMC10659444 — confirmed: comparison/sign/ordering not discussed
    anywhere, not even as future work.
16. Frady, Kleyko, Sommer (2021), "Computing on Functions Using Randomized Vector
    Representations," arXiv:2109.03429.
17. Komer, Stewart, Voelker, Eliasmith (2019), "A neural representation of continuous space
    using fractional binding," CogSci 2019 (Spatial Semantic Pointers).
18. Frady, Kleyko, Kymn, Olshausen, Sommer (2024), "Improved Cleanup and Decoding of
    Fractional Power Encodings," arXiv:2412.00488.
19. Kleyko, Rachkovskij, Osipov, Rahimi, "A Survey on Hyperdimensional Computing aka Vector
    Symbolic Architectures," Parts I/II, arXiv:2111.06077 / ACM CSUR.

**Brain numeric magnitude comparison (lit-scan 3):**
20. Moyer, R.S. & Landauer, T.K. (1967), "Time required for judgements of numerical
    inequality," *Nature* 215, 1519-1520.
21. Dehaene, S. & Cohen, L. (1997), "Cerebral pathways for calculation: Double dissociation
    between rote verbal and quantitative knowledge of arithmetic," *Cortex* 33(2), 219-250.
22. Nieder, A. & Miller, E.K. (2003/2004), "Coding of cognitive magnitude" / "A
    parieto-frontal network for visual numerical information in the monkey," *PNAS* 101,
    7457-7462.
23. Piazza, M., Izard, V., Pinel, P., Le Bihan, D., Dehaene, S. (2004), "Tuning curves for
    approximate numerosity in the human intraparietal sulcus," *Neuron* 44, 547-555.
24. Vallentin, D. & Nieder, A. (2013), "Representation of Abstract Quantitative Rules
    Applied to Spatial and Numerical Magnitudes in Primate Prefrontal Cortex," *J.
    Neurosci.* 33(17), 7526-7534.
25. "Symbolic Number Comparison Is Not Processed by the Analog Number System" (symbolic
    estrangement / task-dependence caveat), *Frontiers in Psychology*, 2018.

(Counted 20+ verified external; items 20-25 include the honest-caveat source, all fetched/
confirmed by the 3 parallel Sonnet lit-scan sub-agents, not asserted from training memory.)

**Substrate-internal (verified on disk, not counted toward external total but load-bearing):**
- `data/exp_math_rns_add_chain_v1/metrics.json` (FULL, HARD_PASS, verified this session)
- `data/exp_cert_ledger_self_query_v1_smoke/metrics.json` (SMOKE, HARD_PASS, verified this
  session)
- `data/exp_comparator_resonator_primitive_smoke_v1/metrics.json` (FULL, HARD_FAIL, verified
  this session — the closed prior negative this cell's design responds to)
- `preregs/math_rns_add_chain_v1.md`, `preregs/cert_ledger_self_query_v1_2026-07-05.md`
- `notes/research_self_reasoning_capability_gap_2026-07-05.md`,
  `notes/research_math_capability_translation_first_cell_2026-07-05.md` (sibling notes, same
  session)
- `hdlab/kg_traversal.py`, `hdlab/multi_hop.py` (the iterative-hop-with-early-exit control-
  flow pattern this cell's comparison step reuses)

---

*Research complete 2026-07-05. Field advisor run (no matching tracked field; noted).
Internal scour of cert_ledger self-query, math-capability, and comparator-resonator prior
work completed before any external dispatch. 3 parallel Sonnet lit-scans (RNS magnitude
comparison; VSA/HDC comparator precedent; brain numeric magnitude comparison), generic terms
only, no substrate-novel mechanism names off-platform. Lit-scan calibration applied (deflate
0.15-0.25; novel-synthesis cap 0.50). HARD-FAIL thresholds specified. Design only per
Director instruction — no cell built, no routing files (USER-locked ferry-deprecation
override; all actionable content delivered in this note and the exp_dev hand-off companion).*
