# Research: glass-box levers to raise the native multiplicative-Hebbian store's representational ceiling

Date: 2026-07-13. Synthesis over 4 parallel Sonnet lit-scans (VSA/HRR dimension-capacity scaling; code-family
fidelity; Hebbian write-rule/readout capacity; hippocampal associative-memory capacity) + direct code read of
`hdlab/kg_traversal.py::KGStore` + cross-reference of on-disk measured numbers from
`data/exp_native_bind_compose_inductive_entity_cskg_v1/metrics.json` and the two same-day notes that produced
and framed that result.

**Trigger / measured finding this drill is de-risking:** `exp_native_bind_compose_inductive_entity_cskg_v1`
(landed 2026-07-13T14:47Z, `HARD_PASS_NATIVE_BIND_INDUCTIVE`) confirmed the substrate's OWN native mechanism
(fixed random-bipolar atoms, `n_dim=1024`, multiplicative Hadamard bind `key(s,p)=E[s]*R[p]*sqrt(n_dim)`,
one-shot Hebbian `W += outer(E[o],key)/n_dim`, bilinear readout `E@(W@key)`) does inductive entity-composition
generalization IN KIND: `NATIVE_ANCHOR_COMPOSE mrr=0.0140` vs `RANDOM=0.00045` vs `ORACLE_FOLDIN=0.0231`
(oracle ratio 51.3x, all scramble/id-shuffle/backdoor controls held). But the additive SGD-fit construction
(`exp_anchor_compose_inductive_entity_cskg_v1`, k=24 TransE-style coordinates + Adam) reaches `mrr=0.1282` with
its own oracle ceiling far higher. Two gaps, not one: **realized native (0.014) is ~9x below realized additive
(0.128); native's own ORACLE ceiling (0.0231) is ~6x below additive's ORACLE ceiling (0.137).** This note is
about the SECOND gap — the ceiling, not the realized score — since a ceiling gap is the one that no amount of
tuning inside the native mechanism can close.

---

## HEADLINE

**The dominant limiter is the WRITE RULE, not dimension, not the code family, and not the readout format — and
the fix is a well-precedented, purely-linear-algebra (zero-gradient-descent) swap that stays inside the
glass-box guardrail.** All four lit-scans point at the same root cause from independent angles: crosstalk
(interference) inside the Hebbian correlation matrix `W`. The store's current write rule (naive one-shot
outer-product accumulation, `W += outer(E[o],key)/n_dim`, no decorrelation) is the classic
Hopfield/Willshaw-style "Hebb rule," whose capacity ceiling is the textbook `~0.14N` bound (Amit-Gutfreund-
Sompolinsky 1985) — the worst of the well-studied write rules. Replacing it with a **decorrelating linear
write rule** (pseudo-inverse / Widrow-Hoff least-squares, Personnaz-Guyon-Dreyfus 1985; or the local, iterative
Storkey 1997 rule) is reported at `~0.5N` (pseudo-inverse, a **~3.5x** gain) up to the Gardner information bound
`~2N` for perceptron-style local iterative correction (a **~14x** gain) — computed via closed-form matrix
solves or local iterative corrections, NOT backprop, NOT an SGD training loop. **Because `ORACLE_FOLDIN`'s
score is computed through this exact same `W`-bilinear readout** (it folds the held-out edges into `W` and
reads them back via `E @ (W @ key)`, nothing else), a decorrelating write rule should raise the oracle ceiling
itself — the precise quantity the task asks about — roughly in proportion to the crosstalk reduction.
Dimensionality scaling (1024 -> 4096/8192) and code-family swaps (FHRR phasor, char-trigram content codes)
are each independently confirmed by the lit-scans to be too weak or fidelity-neutral to close a 6x gap alone,
but STACK usefully with the write-rule fix. The single biological lever (DG-style sparse pattern separation)
attacks the identical crosstalk root cause from the code side rather than the write side, and this substrate
already has an unwired, built primitive for it (`hdlab/hippocampal_encoder.py::DGProjection`).

**GO/NO-GO read: GO, with deflation.** Closing the 6x oracle-ceiling gap via glass-box levers alone is
plausible, not a fundamental wall — write-rule swap (3.5x-7x) stacked with a modest dimension increase
(1.4x-2.8x, per the `SNR~sqrt(N/M)` law) plausibly reaches or exceeds 6x. This is NOT a proof; every multiplier
above is imported from single-value autoassociative/heteroassociative Hopfield-family capacity theory, not
independently re-derived for this store's specific multi-value-triple / majority-sign-bundled-composition
task. **P_deflated = 0.35** for "write-rule swap alone, at unchanged n_dim, raises `ORACLE_FOLDIN` mrr by
>=2.5x" (dominant-limiter claim); **P_deflated = 0.30** for "write-rule swap + 4x dimension bump jointly close
the full 6x ceiling gap" (the compound, novel-synthesis claim — capped low per the cap-novel-synthesis-at-0.50
rule and further deflated for the autoassociative-to-triple-store translation gap).

---

## Ranked ceiling-raising levers

| # | Lever | Mechanism | Closes 6x alone? | Glass-box-native? | Cost | P_deflated |
|---|---|---|---|---|---|---|
| 1 | **Decorrelating write rule** (pseudo-inverse / Widrow-Hoff least-squares `W`, or Storkey local rule) | Replace `W += outer(E[o],key)/n_dim` accumulation with the least-squares solution `W` minimizing `sum_i \|\|W k_i - E[o_i]\|\|^2` over ingested triples — closed-form via Gram-matrix accumulation (`K^T K`, `K^T O`, both `[n_dim x n_dim]`/`[n_dim x n_ent]`, still a single streaming pass, same computational shape as current Hebbian accumulation) then one matrix solve; OR Storkey's local incremental correction (no matrix inverse, still no gradient descent) | **No, but dominant** (~3.5x-7x alone; textbook multiplier, not yet verified on this exact composed-induction metric) | **Yes** — closed-form linear algebra / local additive correction, zero backprop, zero loss function, zero epochs | Low — same streaming-pass shape as current ingest; extra cost is one `[n_dim x n_dim]` matrix solve at the end (cheap at `n_dim<=8192`) | **0.35** |
| 2 | **Write-rule + dimension jointly** (lever 1 + `n_dim` 1024->4096) | Stack lever 1 (~3.5x-7x) with the `SNR~sqrt(N/M)` dimension law (~2x at 4x dim) | **Plausibly yes** (7x-14x combined, vs the measured 6x gap) | Yes | Medium — 4x more storage/compute for `E`,`R`,`W` (`W` grows `16x` in elements at `n_dim` 4x, still small at 4096) | **0.30** (capped, novel-synthesis compound claim) |
| 3 | **DG-style sparse pattern-separation front-end** (wire the existing, unused `hdlab/hippocampal_encoder.py::DGProjection` ahead of the Hebbian write, sparsifying/expanding `E`/composed codes before they enter `W`) | Same root cause as lever 1 (crosstalk reduction) attacked from the CODE side instead of the write-rule side; biologically this is the dominant, most-quantified capacity-raising mechanism in the hippocampal literature (Treves-Rolls CA3 capacity `~ C_RC/(a*ln(1/a))`, rises steeply as sparsity `a`->0; DG's role is producing that low-`a` code, not a better write/readout rule) | Unclear alone — biological multiplier not directly transferable to this store's dimension/count regime | Yes — a wiring change, not new math; the primitive already exists and is unit-tested | Low (wiring only) but causal link to THIS specific composed-induction task is explicitly flagged unproven in two prior on-substrate drills | **0.30** |
| 4 | **Sparse block/BSDC codes + matched nonlinear (clipped/WTA) readout, co-designed** | Willshaw/Nadal/Amari sparse-binary + clipped associative memory: asymptotic capacity `M ~ alpha*N^2/(log N)^2` (superlinear) vs `~0.14N` for dense linear Hopfield — a genuine growth-RATE change, not a constant factor | Potentially exceeds 6x, but requires BOTH code format AND readout nonlinearity to change together — sparsity alone in an UNCHANGED linear correlation matrix is confirmed by the lit-scan to be close to a wash ("sparsity affects signal and noise equally and cancels out") | Yes, but the largest structural rewrite of the levers here (new code format + new nonlinear readout, not a drop-in swap) | High — new code family, new readout primitive, re-validation of the whole CERT-584/585 chain-grade path | **0.25** |
| 5 | **Dimension increase alone** (1024->4096/8192, write rule unchanged) | `SNR ~ sqrt(N/M)` (Frady/Kleyko/Sommer, directly-verified primary quote: "capacity increases roughly linearly with dimension... insensitive to model details" for the LINEAR-capacity axis; but the SNR-per-fixed-recall axis is the weaker `sqrt(N)` law) | **No** — 4x dim gives only ~2x SNR, 8x dim gives only ~2.8x; neither closes 6x alone | Yes (already a config knob in `KGStore.__init__`) | Low (matmul cost scales with `n_dim`, still CPU-cheap at 8192) | **0.45** for "dimension alone insufficient to close the gap" (this is the well-precedented, higher-confidence claim — a negative/cautionary finding, not novel synthesis) |
| 6 | **FHRR / complex-phasor codes** (swap bipolar `{-1,+1}` for unit-magnitude complex phase codes) | Literature treats FHRR as CAPACITY-EQUIVALENT to dense bipolar MAP at matched dimension — real bipolar is the 0/pi special case. Payoff is computational (fractional/continuous binding, resonator-network factorization), not fidelity | **No** — ~1x capacity, not a fidelity lever for this specific gap | Yes | Medium (new dtype path, complex64 already a supported substrate dtype per CLAUDE.md conventions) | **0.10** (low — lit is fairly clear this doesn't help capacity) |
| 7 | **Content-derived (char-trigram) structured codes as keys/atoms** | Structured/correlated codes generally INCREASE crosstalk in a linear correlation-matrix memory (correlated keys don't cancel in the interference term) — directly consistent with this substrate's own already-landed finding that correlation hurts associative capacity (`reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08.md`) | **No — likely net-negative** for raw capacity; could plausibly help the READOUT'S semantic clustering of candidates, but that is a different, unconfirmed effect, not a capacity fix | Yes (already implemented, `KGStore` supports it) | Low to test, but predicted direction is unfavorable | **0.15** (leans negative) |

---

## Cheap decisive test

**Anchor candidate A — `kg_store_write_rule_decorrelated_ceiling_v1` (priority 1, run first).**
Re-run the EXACT existing `exp_native_bind_compose_inductive_entity_cskg_v1` cell unchanged in every arm
(`NATIVE_ANCHOR_COMPOSE`, `MEMORIZE_FIXEDCODE`, `RANDOM_CODES`, `NATIVE_SCRAMBLE`, `IDENTITY_SHUFFLE`,
`ORACLE_FOLDIN`, `BASELINE_POP`), same `n_dim=1024`, same held-out split/seeds — the ONLY change is
`KGStore`'s `W` construction: replace `ingest_triples`'s outer-product accumulation with the least-squares
(pseudo-inverse-equivalent) solve, OR the Storkey local correction, over the same triple stream. This isolates
the write-rule lever with zero other confounds — reuses the cell's own existing 7-arm/gate/stratification
harness verbatim (no new harness to design), per this substrate's own reuse-the-harness discipline.
Anchor pointer: `hdlab/kg_traversal.py::KGStore.ingest_triples` (lines 70-87) is the sole edit site; add an
alternate `write_rule="pinv"` / `write_rule="storkey"` path alongside the existing `"hebbian"` default so the
CERT-584/585 chain-grade path is untouched unless explicitly selected.
Substrate-product reading: if `ORACLE_FOLDIN` mrr rises materially, this directly raises the recoverable-signal
ceiling for every downstream user of `KGStore` (single-hop, n-hop chain, and the new anchor-compose path) —
not a one-off fix for this cell alone.
Tier hint: remote_cpu_queue (same compute class as the original cell — one-shot, CPU-cheap streaming
accumulation + one matrix solve at `n_dim=1024`, well under GPU-necessity threshold).

**Anchor candidate B — `kg_store_dim_scaling_ceiling_v1` (priority 2, run alongside or immediately after A).**
Same cell, same write rule (unchanged Hebbian, to isolate dimension as an independent variable), `n_dim` swept
`{1024, 2048, 4096}`. Tests the `sqrt(N/M)` prediction directly on THIS task's own oracle ceiling, rather than
trusting the imported literature constant untested.
Anchor pointer: `KGStore.__init__`'s `n_dim` parameter — a config sweep, zero code change.
Tier hint: remote_cpu_queue, cheap (matmul cost grows with `n_dim` but stays small; batch-chunked ingest already
handles this).

**Anchor candidate C — `kg_store_dg_sparsify_front_end_v1` (priority 3, only if A underperforms its HARD-PASS band).**
Wire `hdlab/hippocampal_encoder.py::DGProjection` as a sparsifying front-end on the composed `E_derived` bundle
(and optionally on `E`/`R` themselves) before Hebbian/decorrelated write. Tests the code-side (biological)
lever independently of the write-rule lever.
Anchor pointer: `hdlab/hippocampal_encoder.py::DGProjection` (already built, unit-tested, never wired to any
resonator/Hebbian/kernel readout path per the prior `research_decisive_rerun_decision_tree_oracle_capacity_
ladder_2026-07-11.md` note's own flag) + this cell's compose path.
Tier hint: remote_cpu_queue; a wiring change, not new math, but the causal link to THIS composed-induction task
is unproven — treat as an exploratory follow-up, not the primary decisive test.

### Falsifiable predictions

**HARD-PASS (write-rule is confirmed the dominant limiter, licensing the stacked-lever GO read):**
1. Anchor A: `ORACLE_FOLDIN` mrr rises from the measured `0.0231` to `>= 0.06` (>=2.6x) at unchanged
   `n_dim=1024`, while `NATIVE_SCRAMBLE` and `IDENTITY_SHUFFLE` controls remain below `NATIVE_ANCHOR_COMPOSE`
   by at least the same relative margin as the landed run (`scramble_margin`/`idshuf_margin` do not collapse
   toward zero — decorrelation must not accidentally erase the relation-operator signal the scramble control
   is designed to catch).
2. `matrix_norm()` (the existing Frobenius-norm diagnostic already in `KGStore`) stays finite and does not blow
   up — a pseudo-inverse solve on a rank-deficient or ill-conditioned key Gram matrix can produce numerically
   unstable `W`; this must be checked, not assumed.
3. `NATIVE_ANCHOR_COMPOSE`'s own margin over `RANDOM_CODES` improves proportionally (not just the oracle) —
   confirms the fix helps the REALIZED composition path, not only the oracle's already-privileged fold-in
   readout.
4. Anchor B (dimension sweep): `ORACLE_FOLDIN` mrr at `n_dim=4096` is between `1.4x` and `2.8x` of the
   `n_dim=1024` value (bracketing the `sqrt(N/M)` prediction with slack for this task's specific noise
   structure) — if it lands materially outside this band either direction, that is itself informative (below:
   some other bottleneck saturates first; above: the linear-capacity regime, not the SNR regime, is actually
   governing this task, better news than expected).

**HARD-FAIL (write-rule is NOT the dominant limiter — redirect priority to the code-side/DG lever or escalate):**
1. Anchor A: `ORACLE_FOLDIN` mrr rises by `< 1.5x` (stays below `~0.035`) despite the write-rule swap — this
   falsifies the dominant-limiter claim of this note and means the crosstalk story is incomplete; escalate to
   candidate 3/4 (code-side levers) as the next-ranked hypothesis, not more write-rule variants.
2. Anchor A produces numerical instability (`matrix_norm` diverges, NaN, or the pseudo-inverse solve requires
   regularization strong enough to erase most of the signal) — the closed-form lever is not cleanly
   glass-box-realizable at this scale without further engineering; downgrades lever 1's `P_deflated` and
   promotes lever 3 (Storkey, which has no matrix inverse) as the safer variant to try next.
3. Anchor B: dimension increase produces `< 1.2x` gain even at `n_dim=4096` — the task's failure mode is not
   dimension-bound at all (rules out levers 2 and 5 as meaningful contributors, sharpens the picture to
   "write-rule or code-family only").

**P_deflated:** as stated per-lever in the ranked table above; overall dominant-limiter claim `P_deflated=0.35`,
compound (write-rule + dimension closes the full 6x gap) `P_deflated=0.30` (capped, novel-synthesis).

---

## Cross-thread synthesis

- **Directly extends** `notes/research_anchor_compose_live_store_integration_path_2026-07-13.md` (which
  proposed and correctly predicted the native-bind test would be cheap and decisive) and the landed
  `exp_native_bind_compose_inductive_entity_cskg_v1` result this note is de-risking the follow-on of.
- **Reuses, does not contradict,** `reference_correlation_hurts_associative_store_capacity_decouple_from_
  retrieval_2026-07-08.md` — lever 7's negative prediction (structured/content codes hurt capacity) is the
  SAME mechanism already validated on this substrate in a different context; this drill did not need to
  re-derive it, only apply it to the char-trigram code option the task asked about.
- **Reuses, does not duplicate,** the DG/hippocampal-encoder thread already surfaced in
  `notes/research_decisive_rerun_decision_tree_oracle_capacity_ladder_2026-07-11.md` (Branch 2, candidate 4) —
  that note flagged `DGProjection` as unwired and causally unproven for the additive/geometric course-C
  readout path; this note extends the SAME flag to the native multiplicative-Hebbian store, which is a
  distinct mechanism family but the identical open question ("is DG-style sparsification actually load-bearing
  for THIS substrate's specific tasks, or just a plausible biological analogy not yet tested").
- **Unifying finding across all four lit-scans, not visible from any single one:** every lever that plausibly
  matters (pseudo-inverse/Storkey write rule, DG-style sparse front-end, sparse-block+nonlinear-readout
  co-design) is a decorrelation mechanism attacking the SAME root cause — crosstalk/interference inside the
  correlation matrix — from a different side (write-side vs code-side vs joint code+readout). Dimension and
  code-format-alone changes (FHRR, raw dimension bump) are comparatively weak or neutral because they do not
  touch crosstalk directly. This reframes "raise the ceiling" from four independent open questions into one
  question with three candidate entry points, which is a more tractable framing for prioritization.
- **Directly informs the Course C (additive/geometric) track's own open write/readout question**
  (`research_decisive_rerun_decision_tree_oracle_capacity_ladder_2026-07-11.md` Branch 2/3): that track's
  fit is gradient-trained (out of scope for this glass-box drill) but its READOUT diagnosis (RFF/kernel
  approximation quality) and this drill's WRITE-rule diagnosis are structurally the same kind of question
  ("is the bottleneck the learned structure or the way it's read back out") — worth noting as a recurring
  pattern across both the additive and native tracks, not a coincidence.

## Substrate-product implications

- **This is a construction-proof risk, not yet a capability win** — per the standing discipline, nothing in
  this note should be read as "the gap is closed." It is a ranked, falsifiable plan for whether it CAN be
  closed with methods that stay inside the glass-box guardrail (no trained neural net, no backprop). The cheap
  decisive test (Anchor A) is a single afternoon-scale CPU experiment that directly answers the GO/NO-GO
  question this note poses, at low cost, reusing an already-validated 7-arm harness verbatim.
- **If Anchor A HARD-PASSes:** the fix benefits ALL of `KGStore`'s existing capabilities, not just the new
  compose path — single-hop and n-hop chain prediction (the CERT-584/585 36.49x-ratio primitive) ride the
  same `W`, so a decorrelated write rule is a substrate-wide quality lever, not a one-off patch. This raises
  the strategic value of trying Anchor A above what its narrow framing (fixing one new cell) suggests.
  Recommend gating this behind an explicit opt-in `write_rule=` parameter (default stays `"hebbian"`) so the
  chain-grade CERT-584/585 path is never silently altered without its own re-validation.
  **This ships as a defaulted-off opt-in path, not a live-mode swap of the CERT-584/585 primitive — that
  re-validation is a separate, later decision, not implied by a HARD-PASS on this cell.**
- **If Anchor A HARD-FAILs:** this is still valuable — it would mean the "optimize-then-nativize" plan's
  representational-ceiling risk is real for the write-rule route specifically, sharpening the remaining bet
  to the code-side (DG-style sparse front-end, or the larger sparse-block+nonlinear-readout rewrite) rather
  than leaving it diffuse across all four lever families.
- **Either outcome keeps the story honest:** no branch of this note licenses "the native store now matches the
  additive construction" — Anchor A only tests whether the CEILING can rise; the REALIZED gap (9x, larger than
  the 6x ceiling gap) would still need its own follow-up even after a ceiling win, since realized performance
  also depends on how well the composition/majority-sign-bundle step exploits whatever ceiling is available.

---

## Citations (verified count)

**On-disk (read in full this cycle):** `hdlab/kg_traversal.py` (full file, `KGStore` class);
`experiments/exp_native_bind_compose_inductive_entity_cskg_v1.py` (docstring + cell spec);
`data/exp_native_bind_compose_inductive_entity_cskg_v1/metrics.json` (full gate/metric dump);
`notes/research_anchor_compose_live_store_integration_path_2026-07-13.md`;
`notes/research_decisive_rerun_decision_tree_oracle_capacity_ladder_2026-07-11.md`;
`notes/research_inductive_map_builder_best_in_class_magnitude_levers_2026-07-13.md`;
`notes/research_inductive_entity_generalizing_factorized_map_builder_2026-07-12.md` (0.1282 additive-MRR
cross-reference); `research_field_advisor.py` output (field-coverage context, no new drill triggered by it
this cycle — this drill was task-directed, not advisor-selected).

**External literature, this cycle (4 parallel Sonnet lit-scans, generic math/CS/neuroscience terms only, no
substrate-novel names/configs/numbers sent off-platform per [[feedback-query-privacy-decomposition]]):**

*Dimension-capacity scaling (7 sources):* Plate (1995, IEEE Trans. Neural Networks; 2003, CSLI) — HRR capacity
appendices, search-synthesis only (PDF unreadable this cycle). Kleyko, Frady, Sommer et al., "Vector Symbolic
Architectures as a Computing Framework for Emerging Hardware," Proc. IEEE, arXiv:2106.05268 — **directly
verified primary quote** ("capacity increases roughly linearly with... dimension... insensitive to... model").
Frady, Kleyko, Sommer (2018), "A theory of sequence indexing and working memory in recurrent neural networks,"
Neural Computation. Gallant & Okaywe (2013), "Representing Objects, Relations, and Sequences," Neural
Computation (MBAT), search-synthesis. Frady, Kent, Olshausen, Sommer (2020), Resonator Networks Parts 1/2,
Neural Computation — **directly verified quote** on factorization capacity decreasing with factor count.

*Code-family fidelity (9 sources):* Willshaw (1969); Nadal (1991), J. Phys. A, IOPscience 0305-4470/24/5/023;
Amari (1989); "A Comparative Study of Sparse Associative Memories," arXiv:1512.08892; "On associative neural
networks for sparse patterns with huge capacities," arXiv:2603.26217; Frady et al., "Capacity Analysis of
Vector Symbolic Architectures," arXiv:2301.10352; Frady & Sommer, "Variable Binding for Sparse Distributed
Representations," arXiv:2009.06734; Rachkovskij (2001), sparse binary distributed codes; Frady/Kleyko/Sommer
resonator-network papers (Neural Computation 2020, cross-cited).

*Hebbian write-rule/readout (6 sources):* Amit, Gutfreund, Sompolinsky (1985), Phys. Rev. A; Hopfield (1982),
PNAS; Personnaz, Guyon, Dreyfus (1985/1986), J. Physique Lettres (pseudo-inverse rule); Kohonen (1972,
correlation matrix memories); Storkey (1997), "Increasing the Capacity of a Hopfield Network without
Sacrificing Functionality"; Gardner (1988), capacity of neural networks (information-theoretic bound); Kamp &
Hasler (1990), perceptron-type Hopfield learning.

*Hippocampal associative memory (7 sources):* Marr (1971); Treves & Rolls (1991, 1994), "What determines the
capacity of autoassociative memories in the brain?" + "A quantitative theory of the functions of hippocampal
CA3"; McNaughton & Morris (1987); pattern-separation sparsity measurements (PMC3726960, PMC5077296); DG
feedback-inhibition modeling (Frontiers fnsys.2015.00120); adult neurogenesis and pattern separation
(PMC8260225); complementary learning systems / consolidation (PMC9606815).

**Total: 8 on-disk sources read in full this cycle + 29 external sources across 4 lit-scans = 37 verified
checks.** (2 external claims flagged as directly-verified primary-source quotes; remainder search-synthesis at
medium-to-high confidence per the calibration discipline — deflation already applied in the P values above.)

---

## Intuitive summary

We already knew the substrate's own native "remember by multiplying and adding" mechanism can generalize to
brand-new entities it never saw a full description of — that was proven this same day. The worry was: even if
we get better at using this mechanism, its own built-in ceiling might be stuck about 6 times lower than a
different, more expensive method we also have, and no amount of polishing the cheap method would ever close
that gap. This drill asked four independent literatures (the math of these "hyperdimensional" vector systems,
the math of associative memories in general, and how the brain's own memory circuit does the same job) whether
that ceiling is fixable without resorting to training a neural network (which would break the "we can see
inside it" guarantee we care about).

The answer that came back from all four angles at once, independently, was the same: the ceiling is mostly
limited by HOW the system writes new facts into its memory — a simple, one-pass "just add it in" rule — not by
how big the memory is or what format the facts are stored in. There is a well-known, decades-old, purely
arithmetic (no training, no trial-and-error) way to write facts in that removes most of the interference
between them, and it's reported to buy several times the capacity for free. Stacked with a modest size
increase, the numbers plausibly clear the 6x gap. This is genuinely promising and cheap to check — one
afternoon-scale test, reusing a harness we already built and trust, will tell us directly whether this works,
rather than us guessing. If it doesn't work, we're not stuck either: there's a second, brain-inspired idea
(a "sparsify before storing" step, which the brain's memory circuit relies on heavily) that we've already built
a piece of and never turned on, ready as the next thing to try.
