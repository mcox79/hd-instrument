# Research drill: a plausibility-trained coherence signal for the settling loop (glass-box build)

**Date:** 2026-07-22. **Trigger:** fresh measurement — the comprehension-loop's settling coherence-gate
is NULL over grounded identity vectors (coherent vs incoherent separate by ~0.003; both collapse to a
fixed point instantly). Reproduces the earlier settling_fix HARD_FAIL mode. Diagnosis handed in by the
Director: the codebook the loop settles over was never trained on plausibility, only on identity.
LOCAL-ONLY drill (no web-auth); builds on notes already cited below, does not re-derive their biology.
Calibration per [[feedback-lit-scan-calibration-penalty]]: P deflated 0.15-0.25, novel-synthesis capped
at 0.50. Field-advisor run for cadence-adjacency (`tools/orchestrator/research_field_advisor.py`) surfaces
only the substrate-physics track (free-probability, semiconductor, Glauber/Metropolis) — not this arc's
field; noted for completeness, not used to steer this drill, since this is a targeted mechanism question
with its own prior-note thread.

## HEADLINE

The ~0.003 null is not a settling-dynamics bug — it is a **content gap in the codebook**. The cleanup
memory the loop settles over stores only IDENTITY atoms ("is this a known concept"), so a bound
role-filler structure decodes cleanly as long as its *components* are known atoms, regardless of whether
the *combination* is typical. Coherent and incoherent inputs are equally well-formed sums of known atoms,
so residual-of-settling — a signal defined entirely over atom-membership — cannot see the difference. The
fix is not a new mechanism: it is **reusing the class-smoothed thematic-fit table already built and
banked** in `experiments/exp_graded_thematic_fit_integrated_reader_gate_v1.py`
(`build_gfit_model()`, `data/exp_graded_thematic_fit_integrated_reader_gate_v1/metrics.json`) and
**re-wiring it from a role-DECISION feature into a settling-ENERGY bias term** — the same resource, a
different wiring point in the architecture. P(this closes the ~0.003 gap to a measurable effect) = 0.45,
deflated, novel-synthesis-capped.

## (1) The glass-box plausibility-codebook build

**Data source (reuse, do not rebuild):** `build_gfit_model()` in the v1 cell already computes a
verb x WordNet-noun-supersense co-occurrence table over the McGuffey mining corpora (~99k tokens),
class-smoothed a la Clark & Weir 2002 ("Class-Based Probability Estimation Using a Semantic Hierarchy"):
`typ_class(verb, class) = count(verb, class) / max_class_count`, backoff to `global_typ_mean` for OOV.
Banked stats: 26 noun-supersense classes, 182 verbs with their own association counts, `global_typ_mean
= 0.3124`. This table is Resnik-style selectional-association machinery (per
`research_brain_precision_lever_selectional_error_driven_loop_2026-07-17.md`), a closed-form frequency
table, fully dumpable/auditable — no black box.

**Representation (composes with FHRR role-binding):** for each verb-role (e.g. patient-of-"broke"),
build one FHRR vector `P_role` = a phase-weighted bundle over class-centroid vectors, weight =
`typ_class(verb, class)`. This lives in the same N-dim FHRR space as the identity codebook, so it binds
and unbinds by the same `role (x) filler` algebra already in use — it is a second codebook, not a
foreign data structure. Inspectable: dump `typ_class` + class membership to reconstruct exactly why any
`P_role` has the shape it has.

**"Trained on plausibility" without a black box:** the table itself IS the training — a count, not a
gradient. This preserves the discipline v1's own `claim_ceiling` field already states on disk: the
codebook content is LOOKED-UP/counted (glass-box); only a small scalar (the term's influence weight on
settling, mirroring v1's learned `w[6]`) is gradient-fit. Same separation of concerns, reused verbatim.

## (2) Wiring into the settling loop as the coherence gate

Current failure mode: settling residual = f(identity-atom membership only) -> content-invariant, ~0.003
for both arms. Fix: add a second term to the settle-step energy: `energy_plaus = 1 - cosine(candidate
role(x)filler binding, P_role)` (KL-divergence is the Resnik-primary alternative if cosine underperforms,
per the same 07-17 note's own documented field pitfall — KL sometimes loses to simpler PPMI/cosine
variants; treat as a fallback, not abandonment). Total residual = `identity_residual + lambda *
energy_plaus`, `lambda` a single learned scalar. Coherent (typical) bindings now sit close to `P_role` on
BOTH terms -> low total residual; incoherent (atypical) bindings sit far from `P_role` specifically on the
new term even though `identity_residual` alone stays flat as before -> this is what produces separation
where none existed, because the new term is the only one sensitive to WHICH combination occurred, not
merely whether the atoms are known. This is the concrete build-out of "Score 1" from
`research_coherence_schema_fit_gate_brain_drill_2026-07-19.md`: `P_role` (verb-conditioned expected-filler
distribution) IS the situation-model reference the N400/Sentence-Gestalt literature (Rabovsky, Hansen &
McClelland 2018) says coherence-monitoring should be scored against — replacing that same note's diagnosed
flaw in the first-draft `schema_fit_gate()` (fixed, backward-looking centroid) with a purpose-built
attractor, now framed as a settling-dynamics ENERGY bias rather than a bolted-on decision feature. Cross-
domain framing (useful, not required): this is structurally an external bias field added to a
Hopfield/modern-associative-memory energy landscape — the settle step already IS zero-temperature-like
attractor dynamics; adding a content-conditioned bias field to that energy is the standard move in that
literature (generic term for the Director's own physics-track field-advisor list, which separately flags
modern-Hopfield as fruit-bearing) and gives a second, independent-of-linguistics reason to expect the
mechanism to actually change convergence behavior, not just decorate the score.

## (3) Component #2's plausibility-codebook prerequisite

The 07-19 gate-drill named "Score 1: graded prediction-error-to-situation-model" as a required component
of the two-signal coherence gate and flagged that the codebook it should score against must be
plausibility-conditioned, not a static per-slot centroid. That requirement is exactly what `P_role` above
supplies. The underlying frequency table already exists on disk (v1's `gfit_model_stats`); what's missing
is only the re-wiring from "feature fed to a role-decision classifier" (v1's actual use, which HARD_FAILED
on `P_HELP` — mean_delta_help = -0.024) to "bias term inside the settling energy" (this drill's proposal,
untested). These are different downstream uses of the same table — v1's negative result on role-decision
does not pre-empt this test; it is evidence the codebook alone, feeding a discriminative classifier, is
not enough signal, which is a different question from whether it can bias attractor dynamics.

## (4) Cheapest can-fail measurement

Reuse v1's held-out gold slice (n=163 sentences, McGuffey third reader, excluded from mining — genuinely
independent) and its `build_candidates()` harness. Per gold (verb, role) instance: one coherent candidate
(gold filler) + >=1 incoherent candidate (a filler drawn from a LOW-`typ_class` class for that verb,
frequency/POS-matched to control the surface-confound). Run settling with `lambda=0` (current, expected
to reproduce the ~0.003 null) vs `lambda` fit on a disjoint train split. Report `mean(residual_incoherent)
- mean(residual_coherent)`, Cohen's d.

**HARD-PASS:** with the plausibility term, d >= 0.5 across the held-out set, holding within every
class-frequency band (not one dominant class carrying it), AND the `lambda=0` ablation reproduces the
~0.003 null (confirms the NEW term, not something else, drives the effect).

**Must-fail control (mandatory, not optional):** scramble `typ_class` labels across (verb, class) pairs
before building `P_role` (identical design to v1's arm C scramble-gfit control). Separation under the
scrambled codebook must collapse toward d < 0.1. If the scrambled codebook still separates, the gate is
keying on a confound (length, frequency, lexical familiarity) not plausibility, and the positive result
above is invalid regardless of its effect size.

**HARD-FAIL:** d < 0.2 with the real codebook, OR scrambled codebook reproduces >=50% of the real
codebook's effect size (confound, not plausibility) — either would mean the codebook-content gap is not
the true cause of the ~0.003 null, and the settling-dynamics mechanism itself (not its input codebook)
needs the drill next.

## Cross-thread synthesis

This drill sits directly between two existing threads and resolves a live gap between them:
`research_coherence_schema_fit_gate_brain_drill_2026-07-19.md` specified the two-signal gate design
(graded score + discrete flag) but left "what the graded score's reference vector should physically be"
underspecified beyond "not a fixed centroid" — this drill answers that with a concrete, already-partially-
built resource. `research_graded_thematic_fit...` (v1 cell + its metrics) built the resource but wired it
to the wrong consumer (a role-decision classifier, which HARD_FAILED to benefit) — this drill proposes the
SAME resource wired to a different consumer (settling energy) that the classifier failure does not
address or foreclose. `research_brain_precision_lever_selectional_error_driven_loop_2026-07-17.md`'s
Prediction 4 (KL vs PPMI/cosine fallback) is inherited unchanged as the fallback path if cosine
underperforms. No new biology is claimed here; this is the engineering synthesis the brain-side notes
already licensed.

## Substrate-product implications

If HARD-PASS: the coherence gate becomes a real, inspectable capability — "this sentence is
implausible" becomes a settling-dynamics fact, not a bolted-on classifier score, meaning any downstream
consumer of the settling loop (ingestion gate, self-monitoring layer) gets plausibility-sensitivity for
free without a second pass. This is the concrete instance of the "trustworthy ingestion pipeline" product
story flagged in the 07-19 note. If HARD-FAIL: the honest read is that residual-of-settling is
structurally the wrong signal locus regardless of codebook content (a settling-dynamics limitation, not a
training-data limitation), and the next fork is scoring plausibility as a pre-settle filter (closer to
v1's actual, already-tested wiring) rather than continuing to chase a settling-energy formulation.

## Citations (verified count: reused from prior-note citation lists, not re-fetched this pass)

Clark & Weir 2002 (class-based probability estimation, cited by v1's own code comment); Resnik 1993/1996
(selectional association, KL-divergence); Rabovsky, Hansen & McClelland 2018 (*Nature Human Behaviour*,
Sentence Gestalt); Kutas & Federmeier 2011; McRae, Spivey-Knowlton & Tanenhaus 1998; Kintsch 1988/1998
(CI settling, convergence per the *Journal of Mathematical Psychology* paper already cited in the 07-19
note). All carried forward from `research_brain_precision_lever_selectional_error_driven_loop_2026-07-17.md`
and `research_coherence_schema_fit_gate_brain_drill_2026-07-19.md` — not independently re-verified this
pass per the LOCAL-ONLY constraint on this drill.

## WEB-FETCH REQUESTS (for the Director; this session cannot web-auth)

1. Re-verify arXiv:2604.04825 ("Plausibility as Commonsense Reasoning: Humans Succeed, LLMs Do Not") —
   flagged format-unverified in the 07-20 note; if real, its finding (plausibility knowledge exists but
   fails to deploy under compositional load) is directly relevant to whether a settling-energy wiring
   (deploys plausibility INSIDE the dynamics, not as a post-hoc check) is the right fix class.
2. Any 2023-2026 paper on modern Hopfield / energy-based associative memory with a content-conditioned
   external bias field (search terms: "modern Hopfield network external field," "energy-based associative
   memory selectional bias," "biased attractor dynamics semantic plausibility") — would give a direct
   precedent for the energy-term wiring proposed in section (2), currently this drill's own synthesis.
3. Ramsauer et al. 2020 ("Hopfield Networks is All You Need") — re-check for any documented mechanism of
   adding a per-query bias/prior term to the energy function prior to convergence, as a precedent check
   on the lambda-weighted energy_plaus addition.

## HONEST FRAME

HYPOTHESIS-pending throughout. The codebook-content diagnosis (identity-only vs plausibility-conditioned)
is a defensible read of why residual-of-settling is content-invariant, but untested on this substrate's
actual settling implementation — P capped at 0.45. The reuse of v1's table is high-confidence (it exists,
on disk, verified via metrics.json read this session); the NEW wiring (settling-energy bias term) is
the novel, unverified part and carries the full calibration penalty.
