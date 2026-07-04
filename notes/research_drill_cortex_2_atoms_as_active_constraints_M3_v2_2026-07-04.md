# Research drill: cortex-2 atoms-as-active-constraints (M3 v2)

Prior-work check: NONE (2 substrate concept-queries returned WordNet noise + 1
unrelated "Constraint envelope" note). This is novel synthesis — treat P per
lit-scan-calibration-penalty (deflate 0.15-0.25, cap novel-synthesis P at 0.50).

## HEADLINE

No published system does exactly "query a ~100-row learned-law atom store at
every operation boundary and apply matches as live constraints" — but three
independent 40-70yr-old lineages converge on the same computational motif
(match-store-against-current-state, then gate), and at N~100 atoms the
compute cost is trivial (sub-millisecond), so the real design problem is
PRECISION (avoiding false-positive constraint firing), not speed. Recommend
building `hdlab/atom_consultation.py` as a thin Rete-alpha-style tagged-filter
+ cosine-rerank layer, wired into `Cortex.forward()` as a new provenance-only
step 0, with Skunkworks auditing every atom-application decision before any
enforcement is made non-optional.

## (a) Lit-scan: 3-4 tier-1 sources per angle, P_deflated applied

**Classical symbolic (closest analog):**
1. Forgy 1982, "Rete: A Fast Algorithm for the Many Pattern/Many Object
   Pattern Match Problem" (Artificial Intelligence 19(1)) — production-rule
   engine compiles rule conditions into a discrimination network; working-
   memory changes auto-propagate to only the affected rule matches. This IS
   the "operation queries memory automatically" pattern the M3 gap describes,
   already solved and cheap for small rule/fact counts. Rerank cost is
   proportional to the *change*, not full store size.
2. Jaffar & Lassez 1987, CLP scheme (POPL) — constraint store re-consulted
   incrementally on every domain-variable narrowing (arc-consistency
   propagation, Mackworth 1977 AC-3). Directly relevant as the "constraint
   applied live, not compile-time" analog.
3. ASP integrity constraints (Gelfond & Lifschitz 1988; clingo/DLV lineage)
   — solve-time automatic rejection of any candidate violating a stored
   rule. Adjacent: grounding is closer to compile-then-solve than continuous
   consultation, so weight this lower than Rete/CLP.

**Neuro-symbolic / brain analog:**
4. Frank, Loughry & O'Reilly 2001 (Cog Affect Behav Neurosci) + follow-on
   PBWM literature — PFC-basal-ganglia "adaptive gating hypothesis": a
   learned, input-conditioned gate decides what stored context is admitted
   into active working memory, rather than exhaustive re-derivation. This is
   the brain-grounded existence proof the memory-rules require for cortex
   design (per brain-is-best-in-class prior).
5. Graves et al. 2014/2016 (NTM/DNC) + Asai et al. 2023 (Self-RAG) — modern
   ML converges on the same shape: a small controller/gate decides
   what/whether to consult external memory per step, not a hardcoded path.

P_deflated: convergent-analog claim P=0.45 (down from raw ~0.65-0.70 given
calibration penalty — no source tests HD/VSA substrates specifically, all
analogs are from symbolic or dense-neural literatures, cross-domain transfer
to the substrate's chain-grade/CG_META atom format is unverified).

## (b) Implementation candidate + cost estimate

At N~99 atoms, brute-force cosine/tag scan is the right answer — no index
structure justified (ANN/index crossover is empirically placed near N~1M,
per sklearn/FAISS practitioner literature). Rough cost: ~26ns/dot-product at
768-1024D on CPU SIMD => ~2.6us raw arithmetic for 99 atoms; realistic
wall-clock with Python/dict/object overhead is 0.01-1ms per consultation
call. This is negligible relative to any substrate operation currently
timed in the cell suite (ms-to-second range) — so a per-operation atom
consult is CPU-free in practice. The real cost is precision engineering: a
cheap classifier/router is only worth its own overhead when it prevents
false-positive constraint firing, not for raw speed (memoization
cost-benefit framework, general CS literature).

Atom-class routing recommendation (mirrors Rete alpha-network: cheap
single-condition tag filter before any similarity join):
- **Physics-law atoms (CG_META: SCALE_FREE, TOPOLOGY_FREE, ALGEBRA_SCALES,
  STORAGE_STRATEGY, cleanup_M_scaling)** -> auto-consult on COMPOSITION ops
  (facade construction, primitive chaining). Tag: `applies_to=composition`.
- **Discipline atoms (Fix#28 class)** -> auto-consult on FRAMING/VERIFICATION
  ops (verdict processing, metrics reporting). Tag: `applies_to=framing`.
- **Empirical/measured atoms** -> auto-consult on CAPACITY ops (sizing N/K/M,
  envelope checks) but NEVER as a hard gate — surface as advisory only,
  since measured bounds are method-config-contingent (existing USER-locked
  rule), not universal law.

"Operation class detection" itself should be the SAME motif one level up:
a fixed small enum (COMPOSITION / FRAMING / CAPACITY / RETRIEVAL / VERIFY)
tagged per call-site by the cell-author (explicit, not inferred), then
atom_consultation does exact-tag filter (Rete-alpha-cheap) followed by
cosine rerank only within the matched tag-subset (usually <20 atoms).
Avoid a learned router here — at this store size a learned gate's own
training/maintenance cost exceeds any benefit; explicit tagging is simpler,
auditable, and matches Skunkworks no-silent-enforcement requirement.

## (c) Concrete cortex.py v2 architecture

New module: `hdlab/atom_consultation.py`

```python
@dataclass
class AtomMatch:
    atom_id: str
    atom_kind: str          # e.g. "CG_META_PHYSICS_LAW", "DISCIPLINE_RULE"
    applies_to: str         # operation-class tag, e.g. "composition"
    similarity: float       # cosine sim to current op-context query vector
    constraint_text: str    # human-readable law/rule text (audit trail)

@dataclass
class ConsultationResult:
    matches: list[AtomMatch]      # top-K, empty list allowed
    applied: bool                 # False until Skunkworks/USER promotes
                                   # from advisory to enforced
    provenance: dict              # scalar diagnostics only (facade rule)

class AtomConsultant:
    """NO_STORAGE: stateless query wrapper over the existing
    DirectorKBQuery / load_default_kb interface (hdlab/director_kb_query.py).
    Consultant holds no bundled state of its own -- storage strategy
    inherited verbatim from the underlying KB store, matching the Cortex
    facade's existing MIXED-inherited-per-primitive convention.
    """
    def __init__(self, kb=None, top_k: int = 5):
        self._kb = kb or load_default_kb()
        self._top_k = top_k

    def consult(self, operation_class: str, query_vec) -> ConsultationResult:
        # 1. cheap tag filter (Rete-alpha analog): atoms where
        #    applies_to == operation_class OR applies_to == "any"
        # 2. cosine rerank within filtered subset only
        # 3. return top_k as ADVISORY matches; applied=False always
        #    (enforcement is a separate, explicitly-audited step)
        ...
```

Integration point: `Cortex.forward()`, NEW step **(0)**, before the existing
step (1) M1.5 write. Call `AtomConsultant.consult(operation_class, q_2d)`
where `operation_class` is a new required-or-defaulted `CortexConfig` field
(`atom_consultation_op_class: str = "composition"`), matching the facade's
existing per-call scalar-provenance convention (no bundled state — same
rule that already governs M1.3-M1.8). Emit
`provenance["m_atomcon_matches"] = [m.atom_id for m in result.matches]` and
`provenance["m_atomcon_applied"] = result.applied` (always False until a
separate promotion decision). This is additive-only: default
`atom_consultation_enabled=False` preserves Phase 2/2b backwards-compat
exactly as `noise_channel_enabled` did.

Storage strategy for the new module: **NO_STORAGE** (stateless query
wrapper), consistent with the facade's CG_META compliance docstring already
in cortex.py.

## (d) First-probe cell design (one paragraph)

Build `exp_cortex2_atom_consultation_smoke_v1`: instantiate `Cortex` with
`atom_consultation_enabled=True`, run `forward()` across a small synthetic
battery of calls tagged with each of the 5 operation classes
(COMPOSITION/FRAMING/CAPACITY/RETRIEVAL/VERIFY), and assert (a) consult()
always returns within the sub-ms budget measured directly (wall-clock
assertion, not estimated), (b) the tag-filter step returns a STRICT SUBSET
of the full atom count for every call (never full-scan bypass), and (c) for
at least one hand-constructed case, the matched atom's `constraint_text`
correctly predicts a known CG_META law (e.g. STORAGE_STRATEGY atom fires on
a COMPOSITION-tagged call and its text matches "SHARDED > BUNDLED at
scale"). This is a smoke test of retrieval correctness, NOT of enforcement
(applied stays False) — enforcement is an explicit follow-on decision after
Skunkworks audits a batch of advisory-only consultation logs.

## (e) Anti-drift discriminator

Log every consultation event (matched atom_ids + operation_class + the
downstream operation's actual parameter choice) to a SHARDED per-call
provenance store (never bundled, per storage-strategy law). The
discriminator: bucket calls into (i) "atom matched AND downstream parameter
choice equals the atom's recommended value" vs (ii) "atom matched but
downstream parameter choice differs" vs (iii) "no atom matched." Compute
match-and-honored rate across (i)/(i+ii). HARD-FAIL: if match-and-honored
rate stays <20% after N>=50 calls, atoms are being retrieved but not
actually informing outcomes — consultation is decorative, do not promote
to enforced. HARD-PASS: match-and-honored rate >=70% with zero cases of a
matched physics-law atom being silently contradicted (bucket ii present but
flagged, never silent) — that clears the bar for a Skunkworks-reviewed
promotion to `applied=True` on a narrow, named atom class only (never
blanket-enable).

## (f) Risk callouts + confidence

- Risk: explicit-tag-per-callsite requires cell-authors to correctly tag
  operation class; mis-tagging silently defeats the whole mechanism (same
  failure mode as any manual dispatch it's replacing). Mitigate via
  Skunkworks spot-audit of tag-vs-actual-operation mismatches.
  - CANNOT identify a viable path to eliminating manual tagging without a
    learned classifier, which this drill argues against on cost-benefit
    grounds at N~100 — flag as an open tension, not a resolved design
    decision.
- Risk: advisory-only phase risks becoming permanent (atoms retrieved,
  logged, never actually gated) — this is exactly the failure the
  anti-drift discriminator above is built to catch structurally.
- Confidence: P=0.45 (deflated) that the Rete-alpha-tag + cosine-rerank
  architecture is the right shape for cortex-2; P=0.50 (capped,
  novel-synthesis) that this specific module design survives contact with
  the first probe cell unmodified. No direct precedent exists for atom
  stores of this exact kind (CG_META physics-law + discipline-rule mixed
  corpus) being consulted this way — genuinely novel territory, treat this
  memo as a starting hypothesis, not a validated design.

## Substrate-product implications

If this closes: cortex stops being a facade over hardcoded cell-author
choices and becomes a system that visibly applies its own learned laws —
directly serves the M3 "cortex layer above substrate" vision and gives a
concrete, auditable answer to "does the substrate know what it has
learned." If it fails the anti-drift discriminator (decorative retrieval),
that is still a useful negative result: it would mean the atom corpus
needs a different retrieval representation (e.g. HD-bound tag vectors
instead of plain string tags) before consultation can be causally load-
bearing — route to a 2x-drill on tag-vector encoding if HARD-FAIL triggers.

## Citations (verified count: 9 sources cross-checked across 3 parallel
lit-scan sub-agents; 0 project-specific terms used in any external query
per query-privacy-decomposition)

1. Forgy 1982, Rete algorithm, Artificial Intelligence 19(1)
2. Mackworth 1977, "Consistency in Networks of Relations"
3. Jaffar & Lassez 1987, CLP scheme, POPL
4. Gelfond & Lifschitz 1988, stable model semantics
5. Frank, Loughry & O'Reilly 2001, PFC-BG working memory gating model
6. Graves, Wayne & Danihelka 2014, Neural Turing Machines (arXiv:1410.5401)
7. Graves et al. 2016, Differentiable Neural Computer (Nature)
8. Asai et al. 2023, Self-RAG
9. sklearn/FAISS practitioner docs on brute-force-vs-ANN crossover (~1M items)
