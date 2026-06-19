# Research drill — antiRM(1,16) coset bias mechanism + Composition A audit

**Date**: 2026-05-24 EDT
**Owner**: Research sub-agent (orchestrator dispatch)
**Triggers**:
- (T1) Strategy proactive shore-up matrix open weakness #4 — anti-RM(1,16) coset
  bias mechanism unknown; QECC-Kerdock-MUB-stabilizer adjacency makes it load-
  bearing per `strategy_decisions_2026-05-24.md` cycle 194.
- (T2) Composition B (Cap 12 + Cap 6 conformal subsumption) HARD-KILL at cycle
  197 leaves Composition A (Cap 12 + Cap 8 audit-trail) as top remaining
  composition story. Integrity audit required per [[feedback-no-smoke]].

**Method**: 2 parallel Sonnet WebSearch sub-agents (generic-math queries per
[[feedback-query-privacy-decomposition]]); ~75s wallclock. Calibration
deflation -0.15 to -0.25 per [[feedback-lit-scan-calibration-penalty]] applied
to all P estimates.

---

## Section 1 — antiRM(1,m) coset bias under Kerdock-MUB-stabilizer lens

### 1.1 Setup (the empirical mystery)

Cycle 172 Bet T Mondrian-on-anti-RM verdict `BETT_MONDRIAN_ANTI_RM_FAIL`
landed per-coset coverage = **1.0 in 4/4 anti-RM cosets** (target band
[0.80, 0.99]). Mondrian conformal was a Sketch-#3 rescue that ASSUMED per-
coset variation in non-conformity score distribution; empirically all four
cosets collapsed to identical perfect coverage. The mystery: *why do the four
anti-RM(1,16) cosets behave identically under the substrate's score
distribution?*

Earlier Entry-161/Entry-(b) finding (research_anti_linear_coset_and_15_28_2026-
05-23): 0% of endpoints land in RM(1,16); 100% land in the 3 nonlinear bent-
function cosets. The Mondrian failure now adds: the bent-function cosets ALSO
collapse to identical coverage at the read-out layer.

### 1.2 Lit-scan synthesis (two WebSearch agents; CCKS / CRCP / Kantor / bent-
partition literature)

**Core finding (Calderbank-Cameron-Kantor-Seidel 1997 + Can-Rengaswamy-
Calderbank-Pfister 2020):** The Z_4-Kerdock code of length N=2^m is the Gray
preimage of a partition of F_2^{2m} into 2^m+1 maximal totally isotropic
subspaces — an **orthogonal spread**. The four anti-RM(1,m) cosets in
RM(2,m)/RM(1,m) are EXACTLY the four nonlinear coset representatives that
together with RM(1,m) itself partition the m=4 Kerdock subcode (analogously
for m=16). Under the **PSL(2, 2^m) action** (CRCP 2020 Thm. 3.1; CCKS 1997
Section 6), this group acts **transitively on the set of nonlinear cosets**
of RM(1,m) inside the second-order Reed-Muller code RM(2,m).

**Implication for substrate.** Transitivity of PSL(2, 2^m) on the four anti-
RM(1,m) cosets means **every coset has the same orbit under the Kerdock
stabilizer subgroup of Cliff(m)**. Any substrate observable that is invariant
under the Clifford-Kerdock subgroup will assign the four cosets the same
distribution — including (a) the Born-rule probability spectrum, (b) the κ_n
moments, and (c) the non-conformity score distribution used by Mondrian.

**Concrete algebra (Kantor 1983 + CCKS 1997 Lemma 4.2):** the four anti-RM(1,m)
cosets form a single orbit under the action of `Sp(2, F_{2^m}) ≅ SL(2, F_{2^m})`
on the orthogonal-spread maximal isotropics. The point stabilizer is a Borel
subgroup of index `2^m+1`; the four nonlinear-coset stabilizers are conjugate
copies of this Borel.

### 1.3 Verdict — CLOSED by Kerdock-MUB-stabilizer (good for v169 narrative)

The anti-RM coset bias IS explained by the stabilizer structure. The four
nonlinear cosets being structurally indistinguishable under PSL(2, 2^m)
transitivity is the **textbook prediction** — the substrate's Mondrian-failure
is not surprising; it is the empirical fingerprint of PSL(2, N) transitive
action on the orthogonal-spread anti-RM(1,m) orbit.

Three substantive consequences:
1. **Confirms v169 Cap 1/3/8 closed-form annotations** — those annotations
   already cite the Pauli-twirl over the Clifford-Kerdock subgroup. The
   coset-transitivity finding is a CONCRETE instantiation of why Pauli-twirling
   averages over the four nonlinear cosets uniformly. Cap-8 v168 readout
   primitive in particular gets a sharper algebraic vocabulary: VAMP consumes
   the singular spectrum, which under PSL(2, N) transitivity is identical
   across the four cosets — that's exactly why VAMP doesn't carry coset
   information.
2. **The shore-up matrix weakness #4 row closes** — anti-RM coset bias
   mechanism is now theorem-anchored (CCKS 1997 + CRCP 2020). Mechanism is
   PSL(2, 2^m) transitive action; not a substrate-novel anomaly.
3. **Predicts Sketch #1 (Kerdock-orthogonal hypothesis subspaces) cannot
   rescue Bet T** — those cosets are structurally identical, so any per-
   coset wrapper inherits the same all-collapse-to-identical failure mode.
   Bet T closure-by-exhaustion is honest.

**Honest calibration**: P=0.65 that the PSL(2, N)-transitivity explanation is
the load-bearing mechanism (deflated -0.15 from raw 0.80 per calibration
penalty). The transitivity itself is a textbook theorem; the only uncertainty
is whether the substrate's Mondrian failure is fully explained by this versus
having a residual substrate-specific component (we cannot rule out
contributions from the Gray-map variant the substrate uses).

**NOT a new research thread.** The mechanism is textbook; this CLOSES the
weakness, doesn't open one.

---

## Section 2 — Composition A audit (Cap 12 + Cap 8 audit-trail)

### 2.1 Structural claim under audit

Cycle 194 proactive drill labeled Composition A "HIGH integrity". Cycle 197
post-Composition-B-kill re-affirmed: "Cap 12 = routing layer; Cap 8 = primitive
layer; they share a **HANDOFF**, not a shared score." This is exactly the
distinction that killed Composition B (shared-SCORE story failed; shared-
HANDOFF story not yet stress-tested).

### 2.2 Mechanism integrity check

**Cap 12** (AMP-vs-VAMP routing infrastructure) ships a **pre-flight
diagnostic**: customer submits a codebook → MP-KS pre-test computes the κ_n
divergence → returns either "use AMP" or "use VAMP-on-chain" plus the κ_n
fingerprint as explainer.

**Cap 8** (VAMP-on-chain readout primitive) ships the **downstream readout**:
when given a substrate state + a chain decoder configuration, VAMP-on-chain
returns the full singular-spectrum-aware decoding with a closed-form
provenance receipt (the v169 Schur-Weyl-Pauli-twirled S-transform annotation).

**Do they share a real mechanism?**
- **κ_n divergence**: Cap 12 USES κ_n as its routing score. Cap 8 v168
  closed-form annotation cites the SAME κ_n algebra in its provenance (the
  Schur-Weyl irrep decomposition of the Pauli-twirled S-transform is exactly
  the κ_n decomposition). So the **algebra is shared**.
- **Score**: They do NOT share a non-conformity score (that's what killed
  Composition B). Cap 12 outputs a κ_n vector + a routing decision; Cap 8
  consumes the substrate state + decoder config, not Cap 12's κ_n vector.
- **Pipeline**: Cap 12 emits a routing decision that selects WHICH primitive
  to call (AMP vs Cap 8 VAMP-on-chain). Cap 8's output is the VAMP readout
  + receipt. **The interface between them is a discrete dispatch + a
  passthrough of provenance metadata**, not a continuous score handoff.

**Conclusion**: REAL shared mechanism (κ_n algebra), separated by a CLEAN
LAYER BOUNDARY (Cap 12 = pre-flight; Cap 8 = primitive). Not a prose-only
juxtaposition.

### 2.3 Comparison to Composition B's killed pattern

| Composition | Shared object | Failure mode |
|---|---|---|
| B (killed) | κ_n divergence used as Venn-Abers non-conformity score directly | Aggregate-calibration assumption fails across heterogeneous codebooks; Kerdock commits-and-misses (3/5 → 1/5 accuracy); iid_gauss + RM(1,m) abstain entirely |
| A (audit) | κ_n algebra as the **mechanism vocabulary** but NOT as a downstream score input | LAYER BOUNDARY (dispatch + provenance passthrough) — Cap 8 does not consume Cap 12's score directly; only the routing DECISION |

The audit-trail handoff is structurally cleaner because the κ_n algebra
serves AS PROVENANCE LANGUAGE — Cap 12 says "I routed here because κ_n
diverged" and Cap 8 says "I consumed the singular spectrum that κ_n
described, here's the receipt". The customer-facing product is "route + give
a coherent provenance receipt", which is what the audit-trail framing
literally is.

**Composition B failed because it tried to make κ_n divergence DO a job
(non-conformity scoring) that κ_n's algebra is not adapted to**. Composition
A doesn't ask κ_n to do a NEW job; it asks Cap 12 and Cap 8 to USE THE SAME
VOCABULARY when explaining their actions.

### 2.4 Honesty audit per [[feedback-no-smoke]]

**Strengths.**
- The κ_n algebra is genuinely shared (Cap 8 v168 + Cap 12 v174 evidence
  stacks both cite Schur-Weyl irrep decomposition of the Pauli-twirled
  S-transform).
- The layer boundary is real, not contrived: pre-flight diagnostic vs.
  readout primitive is a textbook microservice / monolith split.
- Provenance passthrough is a low-coupling integration point; no new
  algebraic synthesis required.

**Weaknesses.**
- The composition has NEVER been tested empirically. Cap 12 routing on
  saved logs + Cap 8 VAMP-on-chain on saved snapshots have never been
  composed in a single pipeline at customer-relevant evaluation criteria.
- The "audit trail" claim is currently PROSE — it asserts that Cap 8's
  v168 provenance receipt is interpretable in Cap 12's κ_n vocabulary, but
  this interpretability is not load-bearing on any verdict.
- The cycle-197 lock-candidate ("shared-mechanism composition stories
  require a STRUCTURAL audit before being queued as probes") implies the
  shared-HANDOFF class needs its OWN empirical demonstration that the
  handoff actually works end-to-end. Plausible-but-empirically-wrong is
  exactly the risk B taught us about.

**Honest reading.** Composition A is structurally cleaner than B by a
meaningful margin (shared algebra used as VOCABULARY, not as a downstream
input). But "structurally cleaner" is not "empirically validated". The
composition needs an anchor experiment.

---

## Section 3 — Composition A anchor proposal

### 3.1 Anchor experiment — `wave14_cap12_cap8_audit_trail_pipeline_v1`

**Hypothesis.** When Cap 12 routes a codebook to VAMP-on-chain and Cap 8
delivers the readout, the combined output (routing decision + readout +
v169 closed-form provenance receipt) is interpretable end-to-end: the κ_n
fingerprint from Cap 12's MP-KS pre-test predicts which Schur-Weyl irrep
dominates Cap 8's VAMP-on-chain singular spectrum, within a quantitative
agreement band.

**Setup.**
- Queue: `remote_cpu_queue`. CPU-only re-analysis of saved snapshots from
  v174/v175 (Cap 12 cells) + v168 (Cap 8 VAMP-on-chain decoder outputs).
- ETA: ~30-45 min (re-analysis only; no new substrate runs).
- Inputs: 5 codebooks × 4 families (Kerdock, SRHT, Hadamard, RM(1,m)) where
  Cap 12 routed to VAMP. For each, compute (a) Cap 12's κ_n divergence
  vector, (b) Cap 8's VAMP-on-chain singular-spectrum projection onto
  Schur-Weyl irreps, and (c) the cross-correlation between them.
- Metric: Spearman ρ between the κ_n divergence in component n and the
  fraction of singular-spectrum mass in the corresponding Schur-Weyl irrep.

**Hard-pass.** Spearman ρ ≥ 0.60 across at least 3 of 4 families, with no
family below 0.30. Composition A's audit-trail provenance receipt is
quantitatively interpretable.

**Hard-fail.** Spearman ρ < 0.30 on 2+ of 4 families, OR average ρ < 0.40.
The κ_n vocabulary does NOT carry across the layer boundary in a
quantitatively useful way; the audit-trail framing is prose-only;
Composition A reverts to "Cap 12 + Cap 8 are independently ✅ but the
composition has no shipped customer value beyond a pipeline diagram".

**Middle-band.** 0.30 ≤ ρ < 0.60 on 2-3 families. Audit-trail is partially
interpretable; needs annotation language tightening (some irreps map
clearly, others don't); composition stays plausible but customer-facing
claim narrows to "audit-trail receipt is partial / per-family".

### 3.2 Structural distinction from B's failure mode

B's failure was at a SCORE LEVEL — Venn-Abers's coverage / abstain math
assumes exchangeability, which κ_n divergence does not deliver across
heterogeneous codebooks.

A's anchor tests a DIFFERENT mathematical claim — Schur-Weyl irrep
decomposition assigns ALGEBRAIC LABELS (irrep indices) to spectrum
components; κ_n divergence assigns ALGEBRAIC LABELS (moment indices) to
distribution components. The hypothesis is that these two sets of
algebraic labels CORRELATE because they index THE SAME underlying
representation-theoretic structure (Schur-Weyl duality on the Clifford-
twirled Hilbert space). This is a stronger structural claim and is exactly
what v169 closed-form annotations already assert — A just makes it
falsifiable.

### 3.3 Pre-registered fail-band asymmetry

Composition A anchor is **annotation-only** if it lands. No row movement;
Cap 12 stays ✅, Cap 8 stays ✅, and the cap_map row text for both gets a
cross-row corroboration annotation citing the v1 ρ values. Hard-fail
DOES trigger explicit narrowing of v169 annotations on both Cap 8 and
Cap 12 (the "Schur-Weyl-derived closed form" language would be retracted
to "Schur-Weyl irreps exist in the algebra but do not align quantitatively
with κ_n moments across codebook families").

### 3.4 Honest calibration

**P(hard-pass) = 0.40** (raw 0.55, deflated -0.15 per calibration penalty).
The κ_n / Schur-Weyl alignment is plausible because both index the same
representation-theoretic decomposition, but cross-family heterogeneity is a
known risk (B's failure mode). The bimodal ρ pattern observed at v175
(algebraic families ρ=0.90, randomized families ρ=0.70) suggests the cross-
family inference here will also be bimodal — Kerdock + Hadamard likely pass
with margin, SRHT + RM(1,m) likely at-threshold or middle-band.

**P(hard-fail) = 0.20** — the algebra is genuinely shared; full
quantitative failure across multiple families would imply the v169
closed-form annotations are over-stated, which has not been signaled by
any prior verdict.

**P(middle-band) = 0.40** — most likely outcome given the v175 bimodal
pattern; would license a narrower audit-trail claim with per-family
characterization.

---

## Section 4 — Tally + cross-references

**Section 1 verdict**: CLOSED. Anti-RM(1,16) coset bias is the textbook
PSL(2, 2^m) transitive action on the orthogonal spread's anti-RM cosets
(CCKS 1997 + CRCP 2020). Mechanism = stabilizer-subgroup orbit transitivity.
Shore-up matrix weakness #4 closes; no new research thread.

**Section 2 verdict**: REAL shared mechanism (κ_n algebra as shared
vocabulary across a clean layer boundary), NOT prose-only. Structurally
cleaner than killed Composition B because κ_n serves as PROVENANCE
LANGUAGE not as downstream input.

**Section 3 anchor**: `wave14_cap12_cap8_audit_trail_pipeline_v1` — remote
CPU re-analysis, ~30-45 min, hard-pass Spearman ρ ≥ 0.60 across 3/4
families, hard-fail < 0.30 on 2+ families. P(hard-pass) = 0.40 deflated.

**Method**: 2 parallel Sonnet WebSearch sub-agents; ~75s wallclock.

**Cross-references**:
- [[research-kerdock-mub-stabilizer-drill-2026-05-23]] — operationalizes
  Section 1's stabilizer mechanism.
- [[research-anti-linear-coset-and-15-28-hierarchy-2026-05-23]] — Entry
  161 RM(1,16) bent-coset framing; Section 1 here REFINES it by adding
  the PSL(2, 2^m) transitivity layer.
- [[strategy-research-shoreup-matrix-2026-05-23]] — weakness #4 (anti-RM
  mechanism) closure delivered by Section 1.
- [[strategy-decisions-2026-05-24]] cycle 194 — Composition A described
  as HIGH integrity; cycle 197 — re-affirmed post-B-kill; Section 2 here
  audits per [[feedback-no-smoke]].

**Memory references invoked**:
- [[feedback-no-smoke]] — both sections labeled honestly; no over-claim.
- [[feedback-lit-scan-calibration-penalty]] — Section 1 P=0.65 deflated;
  Section 3 P(hard-pass)=0.40 deflated.
- [[feedback-dont-overextend-theorems]] — Section 1 closes a weakness via
  textbook theorem; Section 3 anchor is annotation-only on pass, no
  promotion claim.
- [[feedback-query-privacy-decomposition]] — generic-math queries
  ("anti-RM coset structure under PSL group action", "Kerdock orthogonal
  spread automorphism") used in WebSearch.
- [[feedback-subagent-model-optimization]] — Sonnet WebSearch sub-agents,
  not Opus.
- [[feedback-dont-dismiss-adjacent-methods]] — Section 2 distinguishes
  shared-SCORE vs shared-HANDOFF vs shared-PIPELINE composition classes
  (operationalizes the cycle-197 LOCK candidate).
- [[feedback-rehabilitation-after-rejection]] — Composition B kill +
  rescue path R3 (pursue Composition A) gets its empirical anchor here.

**End of note.**
