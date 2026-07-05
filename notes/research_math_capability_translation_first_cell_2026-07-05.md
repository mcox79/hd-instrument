# Research: does substrate math-capability translate from proven abilities? First math-capability cell design

**Date:** 2026-07-05
**Trigger:** Director task — test the insight that language and math are both structured compositional symbol
systems, and math may be EASIER for the substrate (exact rules, no one-to-many entropy ceiling). Design (not
dispatch) the first math-capability cell.
**Discipline:** scoured existing experiments/notes first (mandatory); 2 parallel Sonnet lit-scans for external
validation (brain math-cognition; VSA-arithmetic/neurosymbolic-math) using generic terms only per
[[feedback-query-privacy-decomposition]]; lit-scan calibration penalty applied (deflate 0.15-0.25; novel-synthesis
cap 0.50); HARD-FAIL thresholds mandatory on every prediction. NO routing files emitted — everything actionable is
in this note (USER-locked ferry-deprecation override).

---

## HEADLINE

**Four of the five named proven abilities transfer to math DIRECTLY and CHEAPLY, and one is arguably ALREADY
proven — but "genuine value arithmetic" (not just addressing) needs one small, well-scoped new-work increment,
not the large 500-1000-line build a prior drill (2026-06-23) estimated.** Re-scouring shows the substrate landed
THREE separate HARD_PASS Residue-Number-System/CRT cells since that drill (`exp_crt_multi_scale_grid_cell_composition_v1`,
`exp_crt_module_scaling_battery_v1`, `exp_generation_decoder_rns_crt_highvocab_v1` — the last FULL, HARD_PASS,
exact-ordered=1.000 @ V=65536/D=26) — these prove EXACT integer encode/decode via modular residues + Chinese
Remainder Theorem reconstruction, chain-grade, brain-grounded (entorhinal grid cells ARE a residue-number-system;
Sreenivasan & Fiete 2011; Fiete/Kymn cited in-substrate already). What they do NOT yet prove is ARITHMETIC
COMPOSITION (encode(a) op encode(b) = encode(a+b)) — today's cells use an arbitrary random codebook per residue
value, which decodes exactly but has no algebraic relationship between codewords. External lit-scan (fresh,
2026-07-05) nails the precise fix: Kymn et al. 2024 (*Neural Computation*, arXiv:2311.04872) show that if residues
are instead encoded as **phase-linear phasors** (m-th roots of unity), "ordinary VSA binding IS modular addition
for free" — a straight group-homomorphism from (Z,+) into unit-modulus complex multiplication. This means ADDITION
needs only a re-encoding of the ALREADY-PROVEN CRT/multi-modulus machinery (est. ~100-200 new lines, reusing the
existing decode/reconstruct step verbatim), not the full dual-binding-operator RHC build (~500-1000 lines) the
2026-06-23 drill scoped for add+multiply+compare jointly. Separately, the substrate's morphological rule-transform
mechanism (`exp_lex_wug_test_cpu_v1`, HARD_PASS, novel-stem generalization 1.000: infer a literal algebraic
transform `R = TAG_rule ⊙ conj(BASE)` from a few before/after example pairs, apply to unseen items) is — per
Marcus's *Algebraic Mind* thesis and a fresh 2025 result (Neuro-Symbolic Convergent Term Rewriting Systems,
arXiv:2507.19372) — THE SAME underlying problem class as symbolic algebra rewrite-rule learning (commute,
distribute, isolate-variable). This transfers at **zero new infrastructure cost** — same code, different corpus.
**Verdict on "is math easier": PARTIALLY YES, PARTIALLY UNTESTED.** Math's exact/discrete representation (residue
tuples with a unique CRT-decodable answer) structurally avoids the near-miss-neighbor-competition problem that
capped the substrate's natural-language one-to-many relational-generalization prize at Hits@10 ~0.75 vs rank-1
~0.09 (per `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-05.md` FRONTIER section) — but this is a
structural argument, not yet a measured one; it is the PRIMARY falsifiable prediction below. P_deflated(overall
math-capability-cell HARD_PASSes on first dispatch) = **0.45** (deflated from raw ~0.70; capped novel-synthesis;
substrate is in uncharted regime for the phase-linear re-encoding specifically, though every ADJACENT step is
independently already chain-grade).

---

## Q1 — DO THE ABILITIES TRANSLATE? (mapping table)

| Proven substrate ability (status per BACKUP 2026-07-05) | Math analog | Transfer class | Evidence |
|---|---|---|---|
| **Compositional binding** (bind/unbind, Hadamard or FHRR-complex; frame-slot recovery MEASURED_MECHANISM, holds V=1000/D=8) | Algebraic expression tree structure: `(op, left-operand, right-operand)` as a role-typed frame, recursively nestable | **DIRECT** — same primitive, different corpus. An expression tree IS a frame with typed slots (OPERATOR, LEFT, RIGHT); nesting = the same recursive-binding the substrate already does for comprehension's constituent structure. | comprehension order/frame-slot cells; USER HRR-derivation composition algebra |
| **Frame-slot production** (content-conditioned role-typing / selectional restriction, role-blind decode collapses to 0.0 — selectional restriction PROVEN NECESSARY) | Equation/operator templates: an operator slot only accepts an operand of matching type (can't add a string to a number; can't apply `sqrt` to a negative in real-only mode) | **DIRECT** — selectional restriction IS type-checking. The exact mechanism that rejects a semantically-wrong filler in a sentence frame rejects a type-mismatched operand in an equation frame. | comprehension envelope cell (adf6b19, HARD_PASS, role-blind ablation) |
| **Multi-hop reasoning (CG)** — regenerative-cleanup + keyslot-sharding, CHAIN_GRADE ~10 usable hops, extendable to 16-18+ via richer key-capacity (collision-bound, not noise-bound) | Multi-step derivation/proof chains: each derivation step = one hop (apply one rule/operation, cleanup, proceed) | **DIRECT, with the SAME caveat.** Depth ceiling is collision-bound (key-slot capacity), identical physics to natural-language multi-hop. A 5-step arithmetic derivation is well inside the proven ~10-hop CHAIN_GRADE envelope. | `exp_reasoning_depth_keyslots_sharding_v1` (31f53bff6, HARD_PASS FULL, MIDDLE_BAND honest-scoped) |
| **Rule-based transform (morphology)** — infer transform `R = TAG_rule ⊙ conj(BASE)` from a few example pairs, apply to novel stems; extended to 8-rule allomorph-conditioned dual-route (regular-rule vs memorized-exception, Pinker/Prince) | Algebra rewrite rules: commute (`a+b -> b+a`), distribute (`a(b+c) -> ab+ac`), isolate-variable (`ax=b -> x=b/a`); "irregulars" analog = special-case identities (`x*0=0`, `x/x=1` domain caveats) | **DIRECT — the STRONGEST transfer, zero new infrastructure.** Confirmed by external lit: Marcus's *Algebraic Mind* frames morphological rule-extrapolation and algebraic rule-extrapolation as the SAME symbol-manipulation problem (operations over variables/slots, generalizing outside training distribution); a fresh 2025 paper (arXiv:2507.19372, Neuro-Symbolic Convergent Term Rewriting Systems) independently builds exactly this for algebra and reports strong OOD generalization. | `exp_lex_wug_test_cpu_v1` (HARD_PASS, novel-stem gen 1.000); `exp_morph_ruleset_wug_v2_cpu.py` (8-rule conditioned extension, in-flight); Marcus 1999 *Science*; arXiv:2507.19372 |
| **Sequential ordering** — order-recovery holds 0.964-1.000 across the WHOLE grid to 8 constituents/V=1000, no in-grid cliff (comprehension envelope, adf6b19) | Ordered notation: `3-5 != 5-3`; operator precedence; left-to-right read order in an expression | **DIRECT, and EASIER** — math notation order-sensitivity is a STRICT SUBSET of full natural-language constituent order (fewer roles, rigid grammar, no free word order); the substrate's hardest full-parse cliff (extreme corner D8×V1000=0.520) doesn't even apply here since expressions have far fewer simultaneous fillers than an 8-constituent sentence. | comprehension envelope cell, order-recovery sub-result |

**Which are DIRECT vs need new work:** all five map DIRECTLY at the STRUCTURAL/architectural level — this is
the headline finding. The one thing that needs genuinely NEW (but small) work is the semantic/numeric layer under
binding: today's binding composes SYMBOLS (roles, relations, tags) correctly, but the substrate's existing
numeric representation (RNS/CRT residue codebooks) is not YET wired so that binding also respects VALUE algebra
(`encode(3) ⊙ encode(4) = encode(7)`). That is a representation-swap (random codebook -> phase-linear phasor),
not a new operator or new architecture — see Q2.

**Is math genuinely easier than language for this substrate?** Partially yes, structurally, on the axis that
matters most (the entropy-ceiling that gated the natural-language generalization prize):
- Math's answer space is DISCRETE and EXACT (one unique CRT-decodable integer for a given residue-tuple) —
  there is no "near-miss semantic neighbor" competing for rank-1 the way `food`/`animal`/`clothing` hub-words
  crowd out the true object in ConceptNet-style relational retrieval (per the FRONTIER section of the BACKUP:
  hubness + near-miss-neighbor-competition capped rank-1 at ~0.09 even though Hits@10 recovered to ~0.75).
  A well-formed arithmetic query (`2+3=?`) has exactly ONE correct residue-tuple, not a fuzzy neighborhood of
  plausible ones.
- Math's compositional rules are EXACT and TOTAL (an operator's behavior is fully specified for its domain) —
  no register/context-dependent ambiguity the way natural language selectional restriction is often
  probabilistic/soft.
- BUT math is not automatically noise-free: chain-depth noise accumulation (the collision-bound reasoning-depth
  physics) and quantization noise in a phase-linear re-encoding are still real, measured risks (see HARD-FAIL
  bands below) — "no ambiguity" does not mean "no error." This is why the verdict is PARTIALLY, not FULLY, yes.

---

## Q2 — WHAT MATH FIRST? (the smallest decisive math-capability cell)

### Candidates considered

1. **Multi-step arithmetic derivation** (compose operations over a chain) — reuses the MOST proven machinery
   (3 landed HARD_PASS CRT cells + CHAIN_GRADE multi-hop reasoning), but needs the phase-linear re-encoding
   increment.
2. **Symbolic algebra rewrite** (apply rewrite rules to transform an expression) — reuses the morphology
   mechanism at ZERO new infrastructure cost, but tests only SYNTACTIC pattern transfer, not value semantics.
3. **Equality/consistency checking** — arguably ALREADY implicitly proven: `exact_ordered_mean=1.000` in the
   landed `exp_generation_decoder_rns_crt_highvocab_v1` FULL IS an exact equality check (decoded-id == truth-id)
   over a 65536-way discrete space. Framing it as a standalone NEW cell would be redundant; the correct move is
   to RE-ANALYZE that landed data for near-miss/discriminability structure (does runner-up decode sit far below
   threshold, unlike the NL relational near-miss problem?) plus extend it as a check WITHIN the arithmetic cell
   below (item 1), not as its own cell.

### Recommendation: run BOTH, in this order, same session

**PRIMARY cell — `exp_math_rns_add_chain_v1` (arithmetic derivation + equality-check combined).**
This is THE first math-capability cell: it reuses the heaviest tonnage of proven machinery, tests genuine
VALUE arithmetic (not just symbol-pattern transfer), is the most direct test of the is-math-easier hypothesis,
is brain-grounded via a LITERAL (not analogical) mechanism (grid cells), and produces the exact-equality
byproduct that is the self-reasoning hook (Q4).

- **Construction:** encode two small integers `a`, `b` via the ALREADY-PROVEN multi-modulus residue scheme
  (reuse moduli/config from `exp_crt_module_scaling_battery_v1` or the V=65536 setup in
  `exp_generation_decoder_rns_crt_highvocab_v1`), but with residues re-encoded as **phase-linear phasors**
  (m-th roots of unity per modulus) instead of the current random-codebook-per-residue-value scheme. BIND the
  two phasor-vectors (single existing Hadamard/complex-multiply operator — no new operator). Decode via the
  ALREADY-PROVEN CRT-reconstruction/resonator step, verbatim. Compare decoded value to `(a+b) mod prod(moduli)`
  via EXACT match (not cosine threshold) — this exact-match check is the equality/consistency-checking
  primitive.
- **Chain extension:** compose 3-5 additions in sequence (`((2+3)+4)+1=10`), reusing the ALREADY-CHAIN_GRADE
  multi-hop keyslot-sharded reasoning machinery for the "carry state between steps" bookkeeping (each step's
  output residue-tuple becomes the next step's operand — same regenerative-cleanup-between-hops pattern already
  proven to extend depth 16-18+).
- **Arms:** (A) `PHASE_LINEAR_ADD` — the mechanism under test; (B) `RANDOM_CODEBOOK_BASELINE` — today's proven
  CRT scheme with NO phase structure, expected to FAIL at addition (control — confirms the phase-linear
  ingredient is load-bearing, not just "any CRT scheme happens to add"); (C) `SCRAMBLED_MODULUS_CONTROL` —
  derange one residue codebook before CRT reconstruction (same control pattern as the landed `rns_scram` arm) —
  expected collapse, confirms CRT reconstruction remains load-bearing under the new encoding; (D) chain-depth
  sweep 1/3/5 steps to characterize noise accumulation vs the collision-bound reasoning-depth prior.
- **Reuses proven machinery:** CRT/multi-modulus decomposition (3x HARD_PASS), CRT resonator-decode (3x
  HARD_PASS, exact-ordered=1.000 at V=65536), multi-hop chain-depth bookkeeping (CHAIN_GRADE ~10-18 hops). NEW
  work: phase-linear phasor encoding module (~100-200 lines, direct implementation of the published
  group-homomorphism construction — no novel math, an engineering port).
- **Brain-grounding:** entorhinal grid cells are themselves modular/residue-number-system-like codes
  (Sreenivasan & Fiete 2011, *Nat. Neurosci.*); Constantinescu, O'Reilly & Behrens (2016, *Science*) show the
  SAME grid-like periodic code generalizes to abstract non-spatial magnitude spaces in human fMRI — i.e. this
  is not a metaphor, it is the literal brain mechanism the substrate's existing CRT cells were already built to
  replicate (per the grid_cell_composition cell's own docstring, which predates this task).

**HARD-PASS bands (pre-registered here; exp_dev owns exact grid points/seeds/timeout):**
- Single-step ADD: arm A exact-match accuracy >= 0.90 on `a,b` uniform over a range covering >=3 moduli-products
  worth of dynamic range, cv <= 0.10 across >=3 seeds.
- Control separation: arm B (random-codebook baseline) exact-match accuracy <= 0.15 (confirms phase-linear
  structure is THE load-bearing ingredient, not incidental).
- Control collapse: arm C (scrambled modulus) exact-match accuracy <= 0.05.
- Chain-depth: exact-match accuracy at depth-3 >= 0.75 (some graceful degradation allowed, consistent with the
  collision-bound reasoning-depth prior; must NOT cliff to near-zero before depth-5, matching the CHAIN_GRADE
  ~10-hop envelope already proven for reasoning).
- Near-miss discriminability (the is-math-easier probe): margin between the TRUE decoded residue and the
  RUNNER-UP candidate residue must be >= 3x the margin observed in the natural-language relational
  near-miss-neighbor problem (per the FRONTIER hubness data, runner-up margins were often within noise of
  rank-1) — operationalized as: runner-up cosine <= 0.5 x rank-1 cosine on >=90% of trials.

**HARD-FAIL bands:**
- Arm A < 0.60 on single-step ADD at ANY dynamic-range regime tested -> the phase-linear re-encoding does not
  transfer at substrate scale; route to full complex64/qFHRR build (per 06-23 drift's Path B/C) or close the
  arithmetic-composition lane (addressing-only remains proven, arithmetic-composition does not).
- Arm B (random-codebook control) >= 0.40 -> suspicious; verify-the-referent (likely a leak — e.g. small
  modulus range makes brute-force/argmax accidentally work without real phase structure).
- Chain-depth collapses to <0.20 by depth-3 (steeper than the reasoning-depth collision-bound prior predicts)
  -> arithmetic composition compounds noise WORSE than symbolic reasoning composition; flag as a
  DISTINCT-noise-regime finding, do not assume the reasoning-depth formula transfers unmodified.
- Near-miss margin ratio < 1.5x (i.e. math's answer space is ALSO crowded by near-neighbors) -> directly
  falsifies the "math avoids the entropy ceiling" hypothesis; this would be the single most important negative
  result of the cell, and must be reported as such (not buried).

**SECONDARY cell (near-zero marginal cost, run in parallel) — `exp_math_algebra_rewrite_via_morph_transform_v1`.**
Directly tests Q1's strongest transfer claim with ZERO new infrastructure: reuse
`exp_lex_wug_test_cpu_v1`/`exp_morph_ruleset_wug_v2_cpu.py`'s exact mechanism and code path, swap the corpus
from (verb-stem, inflected-form) pairs to (expression, rewritten-expression) pairs for 2-3 canonical rewrite
rules (commute, distribute, isolate-single-variable), each with a small number of example pairs, tested on
NOVEL unseen expressions (the Berko/Wug paradigm, directly).
- **HARD-PASS:** novel-expression rewrite exact-match >= 0.85 per rule (matching the proven width-1 WUG bar of
  1.000, deflated for the added allomorphy-style conditioning this needs — e.g. distribute behaves differently
  depending on operand arity/shape class, same conditioned-transform-selection mechanism as the 8-rule
  allomorph-conditioned WUG extension already in flight).
- **HARD-FAIL:** < 0.50 on any rule, OR the conditioned-transform-selection mechanism fails to distinguish
  rule-classes (collapses to one blurred-average transform, the same failure mode the WUG cell's own docstring
  flags for un-conditioned allomorphy) -> algebra-rewrite needs a DIFFERENT (non-morphology) mechanism; do not
  assume architectural transfer beyond word-level rules.
- **Cost:** ~0 new lines (same module, new corpus + rule list); can run same-day, before the PRIMARY cell, as a
  fast independent read on Q1's transfer claim.

**Why this combination over the alternatives:** it is the pairing that (a) reuses the largest volume of already
chain-grade/HARD_PASS proven machinery, (b) is fully glass-box (every step — residue encode, phase-bind,
CRT-decode, exact-match compare, rewrite-transform-apply — is independently inspectable, no opaque learned
component required, mirroring the INTEGRATION finding that the substrate's real compositional strategy is
symbolic attractor-cleanup, not a learned bridge), (c) directly tests the is-math-easier hypothesis with a
concrete falsifiable near-miss-margin prediction, and (d) produces the exact-equality primitive Q4 needs, as a
byproduct rather than a separate build.

---

## Q3 — HOW DOES THE BRAIN DO MATH? (fresh lit-scan, 2026-07-05)

- **Dual-route / triple-code model** (Dehaene 1992; Dehaene & Cohen 1995; NeuroImage 2004 fMRI validation):
  numbers are represented via an **analog magnitude code** (compressed "mental number line," bilateral
  horizontal intraparietal sulcus — the Approximate Number System, ANS: fuzzy, ratio-dependent, non-symbolic)
  and a separate **exact symbolic route** (verbal number-fact retrieval + visual Arabic-digit code, left
  perisylvian/angular-gyrus + ventral occipitotemporal). This is a genuine dual-mechanism finding, not a single
  unified "number sense" — the substrate's two candidate cells map onto this split cleanly: the PRIMARY cell
  (exact residue/CRT arithmetic) is the exact-symbolic-route analog; nothing in the current design targets an
  ANS-style approximate/analog-magnitude route (a gap, noted for future work, not required for this first cell).
- **Numerosity coding (IPS):** Nieder & Dehaene (2009, *Annu. Rev. Neurosci.*) and related primate work show
  IPS neurons with overlapping, numerosity-tuned Gaussian receptive fields, supramodal (visual/auditory) and
  present in both parietal and prefrontal cortex; subitizing (rapid exact enumeration <=4) is flat-cost, larger
  exact counts are serial/effortful — a small-exact/large-approximate split echoing the dual-route finding above.
- **Grid cells as a residue-number-system / abstract-magnitude code:** Sreenivasan & Fiete (2011, *Nat.
  Neurosci.*) show entorhinal grid-cell modules implement a mechanism ISOMORPHIC to a Residue Number System —
  multiple periodic (modular) codes combining combinatorially for large-range, error-correcting capacity. This
  is not metaphorical for the substrate: the landed `exp_crt_multi_scale_grid_cell_composition_v1` cell was
  EXPLICITLY built to replicate exactly this mechanism (HARD_PASS, 143x multiplicative capacity gain, 3-scale
  CRT). Separately, Constantinescu, O'Reilly & Behrens (2016, *Science*) found the SAME hexagonally-symmetric
  grid-like code in human fMRI during navigation of a purely ABSTRACT non-spatial magnitude space — direct
  evidence the grid mechanism generalizes beyond literal space to general magnitude/relational cognition, which
  is exactly the re-use the substrate is attempting (spatial-addressing CRT cells -> numeric-arithmetic CRT
  cells; same modular mechanism, different content domain).
- **Frame-slot production reused for notation:** Friederici's work on hierarchical structure-building (Broca's
  area, BA44/45) shows priming BETWEEN parenthetical math structure and sentence syntax — domain-general
  recursive/hierarchical combinatorics shared across language and math AT THE STRUCTURE-BUILDING level, even
  though (per Amalric & Dehaene 2016 *PNAS*, 2019 *NeuroImage*) high-level mathematical CONTENT processing
  in expert mathematicians recruits a network largely SEPARATE from and even SUPPRESSING the language semantic
  network. **This is the precise brain-level analog of the substrate's own architecture split:** the substrate's
  frame-slot/binding machinery (shared architecture, proven in comprehension) is the "hierarchical
  structure-building" layer; the CONTENT (numeric residue-tuples vs word-meanings) is domain-specific and does
  NOT need to share representations — consistent with why the substrate can reuse ITS binding/frame architecture
  for math while needing a DIFFERENT content representation (phase-linear residues) than it uses for language.

---

## Q4 — CONNECTION TO SELF-REASONING

Math/formal reasoning is the enabling capability for the substrate to evaluate its OWN claims, not just
retrieve/generate content. The fresh lit-scan surfaces a precise mechanism for why: VeriCoT (arXiv:2511.04662),
HERMES (arXiv:2511.18760) and SymCode (arXiv:2510.25975) — all 2025 neurosymbolic self-verification frameworks —
converge on the same structural claim: chain-of-thought self-verification REQUIRES translating a claim into a
**discrete formal substrate** (first-order logic, a proof assistant, or a computer-algebra system) precisely
because validity/equality checking in a continuous statistical embedding space cannot CERTIFY exactness — only
approximate it. This is exactly the discrete-vs-fuzzy distinction the PRIMARY cell's exact-match residue check
instantiates: `exact_ordered_mean=1.000` in the landed RNS/CRT cells is not a similarity score, it is a
certificate (the decoded value either equals the truth value exactly, or it doesn't — no partial credit, no
threshold-tuning).

Concretely, the math cell steps toward self-evaluation in three ways:
1. **Exact equality-checking is the primitive a self-consistency check needs.** "Does derivation step N follow
   from step N-1" or "does this generated claim contradict a stored fact" is fundamentally an equality/
   consistency check over structured (not just similarity-scored) representations — the PRIMARY cell's
   exact-match compare IS that primitive, tested in isolation before being asked to bear self-reasoning weight.
2. **Multi-step derivation chains ARE the substrate's existing multi-hop reasoning machinery, re-targeted.**
   A self-check like "trace back through my own reasoning chain and verify each hop was valid" is structurally
   identical to the chain-depth arm of the PRIMARY cell (apply a step, cleanup, verify exact/residue
   consistency, proceed) — the same regenerative-cleanup-between-hops pattern already CHAIN_GRADE for
   multi-hop KG reasoning.
3. **Rule-application-with-verification (Q2's SECONDARY cell) is the mechanism for checking "did I apply this
   rule correctly."** Once a rewrite-rule transform is a first-class, inspectable, glass-box operation (not an
   opaque learned function), checking whether a specific application of that rule was VALID becomes the same
   kind of exact structural comparison as the arithmetic equality-check — i.e. rule-verification and
   value-verification become the SAME primitive, composed differently.

This does not claim the substrate is close to general self-reasoning (that remains gated on much more, per the
USER strategic-vision memory's Phase 3 framing: "substrate proposes new mathematics" is a long-horizon goal).
What this DOES establish: the two math-capability cells above are the smallest concrete step that gives the
substrate an inspectable, exact (non-fuzzy) consistency-checking primitive to build self-evaluation on top of,
rather than that primitive remaining an unaddressed gap.

---

## CHEAP DECISIVE TEST (restated, single line per cell)

- `exp_math_rns_add_chain_v1`: does phase-linear-phasor residue encoding + existing bind operator + existing
  CRT-decode achieve >=0.90 exact-match single-step addition (vs <=0.15 random-codebook control, <=0.05
  scrambled-modulus control), holding >=0.75 through chain-depth 3, with near-miss margin >=3x tighter than the
  natural-language relational near-miss problem?
- `exp_math_algebra_rewrite_via_morph_transform_v1`: does the EXACT proven morphology rule-transform mechanism,
  re-corpused to (expression, rewritten-expression) pairs, generalize to novel unseen expressions at >=0.85
  exact-match per rule (matching the proven WUG bar), at zero new infrastructure cost?

---

## FALSIFIABLE PREDICTIONS (HARD-PASS + HARD-FAIL, consolidated)

1. **Phase-linear residue addition is load-bearing** (PRIMARY, novel-synthesis-capped).
   HARD-PASS: arm A >=0.90, arm B <=0.15, arm C <=0.05 exact-match, cv<=0.10, 3+ seeds.
   HARD-FAIL: arm A <0.60 at any regime, OR arm B >=0.40 (leak).
   P_deflated = **0.50** (capped; every ADJACENT step independently chain-grade, but the specific phase-linear
   re-encoding combination is untested in this substrate).

2. **Multi-step arithmetic chains degrade no worse than the proven multi-hop reasoning collision-bound law.**
   HARD-PASS: depth-3 exact-match >=0.75; depth-5 exact-match tracks (not cliffs steeper than) the reasoning
   cell's own depth-vs-key-capacity curve.
   HARD-FAIL: depth-3 <0.20 (steeper-than-reasoning collapse) -> arithmetic composition is a DISTINCT, harder
   noise regime; do not assume transfer of the reasoning-depth formula.
   P_deflated = **0.40** (deflated further; combining two independently-proven mechanisms for the first time).

3. **Math's exact/discrete answer space structurally avoids the near-miss-neighbor-competition problem that
   capped natural-language relational generalization** (the is-math-easier verdict, PRIMARY novel claim).
   HARD-PASS: runner-up-to-rank-1 margin ratio >=3x tighter (more separated) than measured in the FRONTIER
   hubness data.
   HARD-FAIL: margin ratio <1.5x -> math is ALSO crowded by near-neighbors at this representation; directly
   falsifies "math avoids the entropy ceiling" and must be reported prominently, not buried.
   P_deflated = **0.50** (capped novel-synthesis; structural argument is strong, but untested empirically in
   substrate).

4. **Morphology rule-transform mechanism generalizes to algebra rewrite rules at zero new infrastructure.**
   HARD-PASS: >=0.85 exact-match per rule on novel expressions, 3+ rules, matching the proven WUG width-1 bar.
   HARD-FAIL: <0.50 on any rule, or conditioned rule-selection collapses to a blurred single transform (same
   un-conditioned-allomorphy failure mode already flagged in the WUG cell's own docstring).
   P_deflated = **0.50** (capped; mechanism is proven at width-1 for a DIFFERENT domain — first algebra
   application, so still novel-synthesis despite zero code change).

5. **Exact-match residue/CRT comparison is ALREADY (not prospectively) a self-consistency-checking primitive.**
   This is a re-framing of already-landed data (`exact_ordered_mean=1.000` in `exp_generation_decoder_rns_crt_highvocab_v1`
   FULL), not a new prediction requiring dispatch. P = **0.90** (not novel-synthesis; re-reading existing
   evidence through a new lens; NOT deflated per the calibration rule's own carve-out for non-novel claims).

---

## CROSS-THREAD SYNTHESIS

- **With the 2026-06-23 residue-arithmetic-VSA drill** (`notes/research_drill_residue_arithmetic_vsa_compound_predicates_2026-06-23.md`):
  that drill correctly identified Kymn et al. 2024 as the canonical framework and correctly flagged that FULL
  RHC (add+multiply+compare jointly) needs a second binding operator + qFHRR bridge (~500-1000 lines). This
  note's contribution is a SCOPE-NARROWING finding: ADDITION ALONE needs only the phase-linear re-encoding
  (~100-200 lines), because addition (unlike multiplication) is a group-homomorphism realized by the EXISTING
  single bind operator — confirmed independently by today's fresh lit-scan ("ordinary VSA binding IS modular
  addition for free"). That drill's P_deflated=0.40 for "min-viable RHC" was scoped to the HARDER joint
  add+multiply+compare problem; this note's P_deflated=0.50 for add-only is a genuinely easier, more scoped
  sub-problem, hence the higher (though still capped) confidence.
- **With the landed CRT/RNS cells** (grid_cell_composition HARD_PASS, module_scaling_battery HARD_PASS,
  rns_crt_highvocab HARD_PASS FULL): these prove the DECODE half of the math-capability stack chain-grade
  already. This note's contribution is identifying the precise, small gap between "decode/addressing" (proven)
  and "compose/arithmetic" (not yet built) and specifying the minimal bridge.
- **With `exp_multihop_router_crt_residue_addressed_v1`** (smoke SMOKE_MACHINERY_OK, but measured CRT routing
  only 0.415/0.147 route/e2e vs oracle — a MIDDLE result, not yet chain-grade): this is a DIFFERENT combination
  (CRT residue addressing used for multi-hop ROUTING/retrieval, not arithmetic) and its middling result is a
  cautionary data point — composing CRT with multi-hop machinery does not automatically inherit full
  chain-grade fidelity from either piece alone. The PRIMARY cell's chain-depth arm should be read with this
  precedent in mind (HARD-FAIL band 2 above is calibrated partly off this prior middling result, not just
  optimism from the individually-strong pieces).
- **With the morphology mechanism** (`exp_lex_wug_test_cpu_v1` HARD_PASS, `exp_morph_ruleset_wug_v2_cpu.py`
  in-flight 8-rule conditioned extension): both this note's SECONDARY cell and the in-flight 8-rule extension
  use the SAME underlying mechanism; running the algebra-rewrite variant is nearly free additional evidence
  once (or even before) the 8-rule language extension lands.
- **With the FRONTIER/generalization prize closure** (one-to-many entropy ceiling, ALL levers falsified per
  BACKUP): this is the load-bearing CONTRAST case for the is-math-easier prediction (#3 above). The prize's
  closure gives a precise, already-measured natural-language baseline (Hits@10 ~0.75, rank-1 ~0.09-0.17,
  hubness Gini 0.87-0.95) to compare the math cell's near-miss margins against — this note converts what could
  have been a vague "math feels cleaner" intuition into a specific numeric falsifiable comparison.
- **With the USER core-mathematics strategic vision** (`project_user_strategic_vision_self_improvement_portal_core_mathematics_USER_2026-06-22`):
  that memory frames "core underlying mathematics" as a LONG-HORIZON relational-analysis-of-the-cap-map goal
  (category theory / information geometry on the substrate's OWN capability structure), explicitly gated on
  years-out Phase 3 work. This note's math-capability cells are UNRELATED to that specific long-horizon framing
  — they are near-term, concrete, standard-arithmetic/algebra capability cells, not a claim toward "substrate
  discovers new mathematics." Keeping these threads distinct avoids over-claiming; the math-content-KB-ingest
  thread (`notes/research_drill_math_science_extractor_design_2026-06-27.md`, ProofWiki/OEIS extractors) is
  ALSO a separate thread (ingesting FACTS ABOUT math, vs. this note's DOING math operationally) — both are
  legitimate but should not be conflated in status reporting.
- **With the brain-component-driven-development thrust** (USER standing thrust, 2026-07-05): the PRIMARY cell
  is a genuine brain-component reuse opportunity — entorhinal grid-cell/RNS mechanism, already built for
  addressing, now extended to arithmetic. This is the SAME "multiples improve" pattern the thrust calls for
  (reuse a proven brain-grounded mechanism for a second function), not a new component.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

- **If the PRIMARY cell HARD_PASSes:** the substrate gains standalone (no-LLM-call) exact arithmetic —
  calculator-class capability — grounded in the SAME grid-cell mechanism already used for high-vocabulary
  generation addressing. This is a genuine NEW product-surface expansion (numeric QA, quantity reasoning) that
  composes with the existing 5-op predicate set (per the 2026-06-23 drill) for compound-arithmetic natural
  -language predicates ("X earned twice Y", "X+Y=100"), at roughly 1/4 to 1/8 the infrastructure cost the
  2026-06-23 drill estimated for the full add+multiply+compare build (since multiply and compare remain
  deferred, out of scope for this first cell).
- **If the SECONDARY cell HARD_PASSes:** the substrate demonstrates, at zero marginal infrastructure cost, that
  its ALREADY-SHIPPED language-capability machinery (morphological rule generalization) is a genuinely
  domain-general symbol-rule-abstraction mechanism, not a language-specific trick — directly informing how
  much NEW work future capability expansions actually need (this is evidence for, not just aspiration toward,
  cross-domain architectural reuse).
- **If prediction #3 (is-math-easier) HARD-FAILs:** this would be a major, prominent negative result — it
  would mean the substrate's near-miss-neighbor-competition problem is NOT specific to fuzzy semantic content
  but a more general property of ITS retrieval/cleanup mechanism, materially changing the diagnosis of the
  (already-closed) generalization prize and reopening it as a substrate-wide (not content-domain-specific)
  limitation. Per [[feedback-research-every-finding-for-mechanism-and-envelope-push]], this negative would
  itself need an immediate 2x drill into WHY (cleanup-mechanism property vs representation property).
- **Cap_map row candidate:** if HARD-PASS thresholds are met, this justifies Strategy opening a new row
  (e.g. `cap_math_arithmetic_composition`) distinct from the existing generation/reasoning rows — anchor =
  the PRIMARY cell's exact-match + near-miss-margin metrics. Strategy decides whether to bump (research does
  not modify cap_map).

---

## CITATIONS (verified, external count = 27)

**Brain math-cognition (lit-scan 1, 14 sources):**
1. Dehaene, S. (1992). Varieties of numerical abilities. *Cognition*.
2. Dehaene, S., & Cohen, L. (1995). Towards an anatomical and functional model of number processing.
   *Mathematical Cognition*.
3. Empirical validation of the triple-code model (fMRI, fractions), *NeuroImage*, 2004.
4. Examining the Triple Code Model: an fMRI study, PMC6023115.
5. Spatial arrangement/set-size coding of non-symbolic quantities in IPS, *Frontiers in Human Neuroscience*, 2018.
6. Nieder, A., & Dehaene, S. (2009). Representation of number in the brain. *Annu. Rev. Neurosci.*
7. Supramodal numerosity selectivity of neurons in primate PFC/PPC, *PNAS*, 2012.
8. The neuronal code for number, *Nature Reviews Neuroscience*, 2016.
9. Sreenivasan, S., & Fiete, I. (2011). Grid cells generate an analog error-correcting code. *Nat. Neurosci.*
10. Constantinescu, A.O., O'Reilly, J.X., & Behrens, T.E.J. (2016). Organizing conceptual knowledge in humans
    with a grid-like code. *Science*.
11. Amalric, M., & Dehaene, S. (2016). Origins of the brain networks for advanced mathematics in expert
    mathematicians. *PNAS*.
12. Amalric, M., & Dehaene, S. (2019). A distinct cortical network for mathematical knowledge. *NeuroImage*.
13. Friederici, A.D. et al. — separating hierarchical structure building in language and mathematics, PMC3367687.
14. Hierarchical artificial grammar processing engages Broca's area, *NeuroImage*.

**VSA-arithmetic / neurosymbolic math (lit-scan 2, 13 sources):**
15. Kymn, Kleyko, Frady, Bybee, Kanerva, Sommer, Olshausen (2024). Computing with Residue Numbers in
    High-Dimensional Representation. *Neural Computation* 37(1); arXiv:2311.04872. **PRIMARY REFERENCE for the
    add-is-free-via-bind derivation.**
16. Tomkins-Flanagan & Kelly (2025). Hey Pentti, We Did (More of) It! A Vector-Symbolic Lisp With Residue
    Arithmetic. arXiv:2511.08767.
17. Generalized Holographic Reduced Representations, arXiv:2405.09689.
18. qFHRR: Rethinking FHRR through Quantized Phase and Integer Arithmetic, arXiv:2604.25939.
19. Berko, J. (1958). The child's learning of English morphology. *Word* (the Wug test).
20. Rumelhart, D.E., & McClelland, J.L. (1986). On learning the past tenses of English verbs.
21. Pinker, S., & Prince, A. (1988). On language and connectionism (dual-route rebuttal).
22. Marcus, G. et al. (1999). Rule learning by seven-month-old infants. *Science* 284(5416). (*Algebraic Mind*
    thesis: morphological + algebraic rule-extrapolation are the same underlying problem.)
23. Learning Neuro-Symbolic Convergent Term Rewriting Systems, arXiv:2507.19372.
24. Schlegel, K., & Neubert, P. A comparison of Vector Symbolic Architectures. arXiv:2001.11797.
25. VeriCoT, arXiv:2511.04662.
26. HERMES, arXiv:2511.18760.
27. SymCode, arXiv:2510.25975.

**Substrate-internal (cert_ledger evidence; not counted toward external lit total but load-bearing):**
- `data/exp_crt_multi_scale_grid_cell_composition_v1/metrics.json` (HARD_PASS)
- `data/exp_crt_module_scaling_battery_v1/metrics.json` (HARD_PASS)
- `data/exp_crt_capacity_boost_v1/metrics.json` (HARD_FAIL, superseded by the above two — earlier attempt)
- `data/exp_generation_decoder_rns_crt_highvocab_v1/metrics.json` (HARD_PASS, FULL, exact_ordered=1.000 @ V65536/D26)
- `data/exp_multihop_router_crt_residue_addressed_v1_smoke/metrics.json` (SMOKE_MACHINERY_OK, middling measured CRT-routing)
- `experiments/exp_lex_wug_test_cpu_v1` / `exp_morph_ruleset_wug_v2_cpu.py` (HARD_PASS width-1; 8-rule extension in-flight)
- `notes/research_drill_residue_arithmetic_vsa_compound_predicates_2026-06-23.md` (prior RHC drill, full build scope)
- `notes/research_cardinality_fpe_rns_counting_accuracy_2026-06-16.md` (adjacent quantifier/counting drill)
- `notes/research_drill_math_science_extractor_design_2026-06-27.md` (distinct thread: math-content KB ingest)
- `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-05.md` (proven-abilities scoreboard, FRONTIER
  hubness/near-miss numbers used as the comparison baseline for prediction #3)
- `project_user_strategic_vision_self_improvement_portal_core_mathematics_USER_2026-06-22` (memory; core-mathematics
  long-horizon framing, kept distinct from this note's near-term scope)

---

## PRE-REGISTERED HARD-PASS/HARD-FAIL THRESHOLDS (summary table for exp_dev pickup)

| Cell | HARD-PASS | HARD-FAIL |
|---|---|---|
| `exp_math_rns_add_chain_v1` arm A (phase-linear add) | >=0.90 exact-match, cv<=0.10 | <0.60 at any regime |
| same cell, arm B (random-codebook control) | <=0.15 | >=0.40 (leak) |
| same cell, arm C (scrambled-modulus control) | <=0.05 | >=0.20 |
| same cell, chain-depth 3 | >=0.75 | <0.20 |
| same cell, near-miss margin ratio | >=3x tighter than NL-relational baseline | <1.5x (falsifies is-math-easier) |
| `exp_math_algebra_rewrite_via_morph_transform_v1` | >=0.85 exact-match/rule, 3+ rules | <0.50 any rule, or blurred-transform collapse |

Autonomy note: exp_dev owns exact grid points, seed counts, moduli choices, queue routing, and timeout for both
cells per [[feedback-no-experiment-design-in-prompts]]-equivalent discipline (this note names mechanism +
bands, not implementation minutiae). Both cells are LOCAL-CPU-feasible (numpy-scale, no GPU needed) per the
existing CRT/morphology cells' own measured wall-times.

---

*Research complete 2026-07-05. Internal scour: existing experiments/notes greped for arithmetic/algebra/CRT/RNS/
morphology/residue/self-improvement threads before any external dispatch (per role discipline). 2 parallel
Sonnet lit-scans (brain math-cognition; VSA-arithmetic/neurosymbolic-math), generic terms only, no
substrate-novel mechanism names off-platform. Lit-scan calibration applied (deflate 0.15-0.25; novel-synthesis
cap 0.50, applied to predictions 1-4; prediction 5 exempted as non-novel re-framing of landed data). HARD-FAIL
thresholds mandatory and specified for every prediction. Design only, per Director instruction — no dispatch,
no routing files (USER-locked ferry-deprecation override; all actionable content delivered in this note).*
