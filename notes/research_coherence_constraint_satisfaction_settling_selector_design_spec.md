# Design spec: constraint-satisfaction SETTLING selector for role-content relational binding
(goal-owner attribution) — the coherence-based binding organ

Filed by: research sub-agent. Design/analysis only — no cell dispatched, no experiment run.
Scope: spec ONLY. Delivers the mechanism design + pre-registered fair test; does not itself
prove the mechanism works.

## CRITICAL CORRECTION FOLDED IN (mid-drill, disk-verified before finalizing)

An earlier draft of this spec proposed reusing `hdlab/iterative_attractor.py` /
`hdlab/cleanup_family.py` as "the settling engine." That is **wrong and has been corrected**.
Disk-read of both files in full confirms: `iterative_cleanup`'s dynamics are
`state_{t+1} = norm(softmax(beta * state @ codebook.T) @ codebook)` — this settles a noisy
query toward the NEAREST STORED CODEBOOK VECTOR (pattern completion / auto-association;
`classical_hopfield`'s `W = codebook.T @ codebook` is the same family, Hebbian
auto-association of stored items). **The "attractors" are codebook entries; a node wins because
it is SIMILAR to a stored pattern.** That is the exact same computation
`decode_coherence_margins` already performs (cosine/margin over a codebook-like role_vocab) and
the exact reason it is role-content-blind (proven this session: shuffle does not collapse its
signal — `shuffled_reproduces=True`, `shuffled_collapses=False`,
`data/exp_coherence_role_conflict_crosstalk_v1/metrics.json`). Reusing it as "the fix" would
silently reproduce the artifact under new machinery. This is corrected below: the loop
**scaffold** (iterate-to-fixed-point, step-size convergence, softmax relaxation) is reusable;
the **mechanism content** (a similarity-to-stored-codebook matrix) is not, and must be replaced
by a genuinely new connectivity matrix built from role-FIT compatibility, not vector similarity.

## 1. BIOLOGY

**Kintsch Construction-Integration (C-I), two cyclical phases** (already verified this arc,
`notes/research_drill_CI_comprehension_loop_situation_model_brain_mechanism_2026-07-21.md`,
re-confirmed via KB query this cycle, cosine=0.501):
- **CONSTRUCTION**: each new clause activates a loose, PERMISSIVE network of candidate
  propositions — including locally-plausible-but-wrong bindings (e.g. both Henry-as-owner and
  old_gentleman-as-owner are constructed as candidates; nothing yet decides between them).
- **INTEGRATION**: iterative spreading-activation relaxation over a CONNECTIVITY matrix `C`
  encoding which propositions mutually support or inhibit each other. Update:
  `a(t+1) = norm(C · a(t))`, iterated to a fixed point. A candidate binding SURVIVES
  (keeps activation) because it is reinforced by OTHER active, jointly-coherent propositions
  about the same entity; a candidate that is locally clean but globally isolated (unsupported
  by, or in conflict with, the entity's other established roles) LOSES activation over
  iterations and is pruned. Coherence = the settled state, not any single-step read.
- **Three levels**: surface structure -> textbase (locally-connected propositions) ->
  **situation model** (integrated with prior knowledge/discourse context — this is where
  goal-owner binding lives; Zwaan & Radvansky 1998's intentionality index is one of the five
  situation-model dimensions tracked here).

**Neural substrate: CA3 recurrent pattern-completion / attractor settling as the general
relaxation-to-fixed-point mechanism** (Marr; Treves-Rolls; Amari/Wilson-Cowan CAN-bump
dynamics) — the SHAPE of "iterate a recurrent update to convergence" is neurally general and
reused across memory systems. But the CONTENT of the recurrent weight matrix differs by what
is being settled: in CA3 auto-association, the weight matrix stores ITEM patterns (Hebbian
outer-product of stored items — this is what `iterative_attractor.py` faithfully implements).
In Kintsch-style text comprehension integration, the connectivity is hypothesized to run over
PROPOSITION-LEVEL nodes with THEMATIC/ROLE-based edges (semantic and referential overlap
between propositions), not over raw distributed item vectors. Both are "settling," but they
settle DIFFERENT graphs. Halford's relational-complexity framework and Eichenbaum's
relational-memory theory (hippocampal item-in-context binding, prefrontal-parietal control for
multi-relation binding) supply the missing piece: WHO-DID-WHAT-TO-WHOM (role-content) is a
higher relational-complexity operation than WHO-IS-THIS (identity), consistent with this
session's own finding that identity/cleanliness survives load-matching while role-content is
exactly 0.0 there (`notes/research_goal_owner_coherence_vs_mentalizing_framing_audit.md`,
Level 3).

**Why iterative settling can catch role-content errors a single-pass cleanliness read
cannot**: a WRONG role-binding (e.g. old_gentleman-as-goal-owner) can be locally clean — one
proposition, no crosstalk, decodes with a sharp margin in isolation, exactly what
`decode_coherence_margins` measures. But it is globally INCOHERENT with old_gentleman's OTHER
established propositions in the situation model (he is not the AGENT of the
attempt-clause, not the EXPERIENCER of the outcome-clause — he plays a different causal-chain
role entirely). A settling process that lets each candidate binding's activation be shaped by
its fit with the entity's whole established-proposition set will decay the wrong candidate over
iterations even though a single-shot read of that one proposition alone looked fine. This is
the SHAPE gap the prior audit already flagged (Level 2: "genuine SHAPE gap versus the brain
mechanism... no iteration, no pairwise connectivity matrix among established propositions").

## 2. REUSE CHECK (corrected)

Per WIRE-DON'T-ISLAND, checked `notes/capability_reconciliation_invisible_islands_audit.md` for
any settling/relaxation/constraint-satisfaction/spreading-activation primitive we forgot we
built — **grep found nothing matching** (`settl|relax|constraint.satisfaction|spreading.
activation|connectivity matrix` = no hits). **The substrate does NOT already own a
coherence-constraint settling organ.** What exists and what it actually is:

| Module | What it actually does | Reusable for THIS organ? |
|---|---|---|
| `hdlab/iterative_attractor.py` (`iterative_cleanup`) | Pattern-completion: `state_{t+1}=norm(softmax(beta·state@codebook.T)@codebook)`. Settles toward NEAREST STORED CODEBOOK VECTOR by cosine similarity. | **Loop SCAFFOLD only** (iterate-to-fixed-point control flow, step-size convergence check, softmax relaxation weighting). NOT the mechanism — its "connectivity" IS a similarity/auto-association matrix, the same family that made `decode_coherence_margins` role-content-blind. |
| `hdlab/cleanup_family.py` (`classical_hopfield`, `modern_hopfield_continuous`) | Hebbian/dense auto-association, `W=codebook.T@codebook`. Same family as above. | Same as above — loop-mechanics reference only, not the connectivity source. |
| `hdlab/situation_model_accumulate.py` (`AccumulateRegister`, `CausalLinkRegister`) | Per-entity FHRR register = bundle of ALL (role, event-slot) bindings; `CausalLinkRegister` extends it with CAUSE/EFFECT meta-roles between event slots. | **Genuine reuse — provides the NODES.** This is the substrate the settling selector operates OVER (each entity's established propositions, each event's causal links), not a source of coherence itself (proven role-content-blind when read via cosine/decode-margin). |
| `hdlab/self_improving_loop.py` (`decide_keep_or_revert`) | Pure threshold rule: adopt candidate with highest aggregate delta iff it clears an abstain band above 0, else keep baseline/abstain. No data dependency, anti-recency by construction (compares deltas, not positions). | **Genuine reuse — the final SELECT/abstain gate**, applied to the settled activation margin instead of the current one-shot coherence-margin delta. Trivial substitution, no redesign needed. |

**Bottom line, stated plainly per the correction**: only `situation_model_accumulate` (nodes)
and `decide_keep_or_revert` (final gate) are genuine drop-in reuses. The settling MECHANISM —
connectivity matrix `C` + relaxation over `C` — is **new, and is the entire crux of this spec**.
`iterative_attractor` contributes loop mechanics only; it must not be mistaken for, or silently
substituted as, the coherence source.

## 3. THE CRUX — where connectivity matrix `C` comes from (role-FIT, not similarity/load)

**The make-or-break design question.** If `C` is built from FHRR vector cosine similarity
(codebook-style) or from anything that scales with how many events are bundled per entity
(load), it degenerates to the exact same signal `decode_coherence_margins` already computes,
and the "settling win" is the load/cleanliness artifact under new machinery — the single
biggest risk flagged below.

**Design: `C` is a small, SUPPLIED role-compatibility table indexed by (role-type, role-type)
pairs, looked up symbolically — no vector geometry, no event counts, anywhere in its
construction.**

Concretely:

1. **Node set.** For a goal-owner query at outcome-event `E_out`:
   - **Candidate-binding nodes**: one per competing entity, e.g. `(Henry, GOAL_OWNER, E_out)`,
     `(old_gentleman, GOAL_OWNER, E_out)`. These are what we are solving for; activation starts
     tied (e.g. 0.5 each).
   - **Established-proposition nodes**: every OTHER `(role, event_slot)` fact already bound in
     that entity's `AccumulateRegister` / `CausalLinkRegister` (e.g. `(Henry, AGENT,
     E_attempt)`, `(Henry, EXPERIENCER, E_outcome_reaction)`, `(old_gentleman, AGENT,
     E_unrelated)`). These are CLAMPED at fixed activation 1.0 (given facts, not being solved
     for) — they are the "context" the candidate bindings must cohere with.
   - Role labels come from the existing fixed taxonomy already used by
     `CausalLinkRegister`/`AccumulateRegister`'s `role_vocab` (CAUSE, EFFECT, AGENT,
     EXPERIENCER, GOAL, ATTEMPT, OUTCOME, REACTION — Trabasso & van den Broek 1985 causal-chain
     story-grammar categories, already the organizing vocabulary this arc uses).

2. **Edge weights `C_ij` — the supplied structure.** A fixed, hand-specified
   `w(role_a, role_b) in [-1, +1]` lookup table over the small role taxonomy, built from
   Trabasso & van den Broek causal-chain ADJACENCY, not from any per-item vector or count:
   - `w(GOAL_OWNER, AGENT-of-ATTEMPT) = +1` (the one who wanted something is expected to be the
     one who tries for it — direct causal-chain adjacency: goal -> attempt).
   - `w(GOAL_OWNER, EXPERIENCER-of-OUTCOME) = +1` (the one who wanted something is expected to
     be the one affected by the outcome — goal -> outcome/reaction adjacency; this is literally
     what "Henry wanted cherries -> Henry got caught" instantiates).
   - `w(GOAL_OWNER, AGENT-of-an-episode-with-no-causal-link-to-E_out) = 0` (no support, no
     inhibition — orthogonal information).
   - Cross-entity competing candidate-binding nodes for the SAME slot get mutual inhibition,
     `w = -1` (standard localist winner-take-all: two owners can't both hold the slot).
   - `C_ij` for a candidate-binding node `i` and an established-proposition node `j` on the SAME
     entity is `w(role(i), role(j))` read straight from this table; `C_ij` between nodes on
     DIFFERENT entities (other than the inhibition edge above) is 0 (no edge).

3. **Relaxation** (reuses the loop scaffold from `iterative_attractor.py`, content replaced):
   `a(t+1) = norm(clip(C @ a(t)))`, iterate with the same convergence criterion
   (`||a(t+1)-a(t)|| < tol`, `max_steps ~ 8`, brain-referenced to theta-cycle sub-cycles per the
   existing docstring). Candidate-binding nodes' activation evolves under support/inhibition
   from clamped established-proposition nodes plus mutual inhibition from the competing
   candidate; clamped nodes do not update.

4. **Readout**: after settling, take the winning candidate-binding node's activation minus the
   runner-up's (the settled MARGIN) and pass it through `decide_keep_or_revert` exactly as the
   existing controller does with `decode_coherence_margins`'s one-shot delta — only the upstream
   signal changes, the abstain-gate contract is unchanged.

**Why this is not similarity/load in disguise**: `C`'s entries are a fixed lookup over ROLE
LABELS (a handful of symbolic categories), constructed once, independent of the passage. It
contains no cosine terms, no vector dot-products, and no dependence on how many events are
bundled into any entity's register (i.e. it does not vary with load the way
`decode_coherence_margins`'s decode-margin does — that signal comes from FHRR bundle
crosstalk, which IS load-dependent by construction; `C` here is load-invariant by construction,
since it is indexed purely by role-type pairs, not by register occupancy). Supplying this table
by hand is within the standing invariant ("supply knowledge/structure, earn the mechanism") —
the STRUCTURE (which roles causally support which) is supplied; the MECHANISM being tested is
whether iterative relaxation over that structure correctly discriminates the coherent binding
under controls that defeat position/load/similarity explanations.

## 4. FAIR MECHANISM-CAPACITY TEST (pre-registered)

**Scope, stated honestly up front**: this is a MECHANISM-CAPACITY proof (can settling do what
single-pass decode-margin provably cannot), not a real-text capability claim. The corpus has
only ONE clean stated/single-world goal passage (Henry/cherries) — a pass is an existence proof
of the mechanism at N=1; real-data scaling is a separate, later effort (standing data-
availability blocker, already logged in the director backup).

**Item construction** (extends the existing Henry/old_gentleman item,
`experiments/exp_coherence_role_conflict_crosstalk_v1.py`):
- Base item: Henry = true GOAL_OWNER (established AGENT-of-attempt + EXPERIENCER-of-outcome
  roles), old_gentleman = foil, role-conflict-embedded (foil already holds another established
  role, inducing crosstalk under the OLD mechanism — kept as the shared test bed for continuity
  with prior findings).
- **Control 1 — LOAD-MATCHED** (reuse verbatim): assert `owner_load == foil_load` PRE any
  conflict-embedding, exactly as `exp_coherence_role_conflict_crosstalk_v1.py` line ~166 does.
  This rules out load as the explanation for any settling win.
- **Control 2 — SHUFFLE, role-content variant (NEW, stronger than the existing positional
  shuffle)**: the existing `_shuffle_role_seq` reverses role-SEQUENCE order (positional) — it
  is necessary but per this session's own finding (`shuffled_reproduces=True` on the OLD
  mechanism) it is NOT sufficient to detect a role-content-blind signal. Add a SECOND shuffle
  specific to the settling mechanism: permute the `w(role_a, role_b)` lookup table itself (or
  equivalently, scramble which role label is attached to which established-proposition node,
  keeping the SAME set of nodes/edges-count/positions). If the settling mechanism is genuinely
  using role-CONTENT, this must COLLAPSE the discrimination (margin -> near 0 / near-chance
  winner across seeds). If the margin survives this scramble, the "win" is structural-but-not-
  content — i.e., the same artifact class already caught twice this session, now under new
  machinery. This is the single most diagnostic control in this spec.
- **Control 3 — ANTI-RECENCY**: construct or select an item variant where the TRUE coherent
  owner (Henry) is NOT the most-recently-mentioned entity before the outcome clause — the foil
  is nearer in the mention stream. A recency-keyed mechanism (or `_pick_strict_cb`-style
  fallback) would pick the foil; the settling selector, driven by role-fit support/inhibition,
  must still pick Henry. (If no real second passage supports this natively, construct a minimal
  synthetic variant that reorders mention position while holding role-structure and load fixed
  — same discipline as the existing hand-built goal-outcome items.)
- **Positive control**: an unambiguous easy item (no competing foil, or foil has zero
  established roles at all) must settle to near-ceiling margin — sanity-checks the pipeline
  before trusting any negative result.

**HARD-PASS** (settling genuinely uses role-content, not position/load/similarity):
- Settled margin correctly picks Henry (true owner) in the load-matched original AND in the
  anti-recency variant, across all seeds (reuse the existing 5-seed discipline), AND
- Control 2 (role-compatibility-table scramble) COLLAPSES the margin (near-tie or incorrect
  pick, not the same near-1.0 margin the unscrambled version gives), AND
- Positive control fires near-ceiling.
Interpretation: iterative constraint-satisfaction settling over a role-fit connectivity matrix
is a genuine, brain-faithful mechanism for role-content relational binding at this scope
(stated/single-world goal-owner). Promote from spec to a shippable organ; extend the causal-
antecedent instance next (Section 5).

**HARD-FAIL** (settling does not add genuine role-content sensitivity):
- EITHER the settled margin fails to discriminate Henry under load-match + anti-recency
  (ties, or picks the foil) — settling adds nothing beyond the single-pass read it was meant to
  fix — OR the Control-2 role-table scramble REPRODUCES the same margin the unscrambled version
  gives (the `shuffled_reproduces=True` signature already characterized this session,
  `data/exp_coherence_role_conflict_crosstalk_v1/metrics.json`). Interpretation: this is the
  guarded-against failure mode — the settling "win," if any, is actually driven by node
  count/position/graph-traversal order, not role content, i.e. the load/cleanliness artifact
  resurfacing under new machinery. Do NOT promote; do not attempt a second one-shot rescue of
  this instance — the mechanism-class question would then be closed for this design, and the
  next move is either a genuinely different connectivity source or routing this instance to the
  already-built, disk-verified `theory_of_mind_sally_anne_nested_hrr_v1` organ per the framing
  audit's Level 1/5 (for any case that turns out to need abductive/divergent-belief inference
  rather than stated-goal binding).

**MIDDLE** (fires at N=1, mechanism-class not yet generalizable): hypothesis-generating only;
do not promote to "settling solves role-content coherence" until a second, independently-
collidable real item is sourced (same standing blocker as before).

## 5. UNIFICATION — does this settling selector also serve causal-antecedent and multi-hop?

**Causal-antecedent instance (M_backward v1-v4, recency=0.333 baseline)**: YES, in principle,
same organ. `CausalLinkRegister`'s CAUSE/EFFECT nodes are exactly the kind of established-
proposition nodes `C` operates over; a causal-role-compatibility table (support: candidate
antecedent's CAUSE-role is temporally/causally adjacent to the EFFECT matching the explanandum)
replaces M_backward's ad hoc structural-feature heuristic with the same settling engine. This is
a natural SECOND instance of the SAME selector (same `C`-construction discipline: role-type
lookup, not similarity/load), not a new organ — confirms and extends the prior synthesis
(`notes/research_relational_backward_reach_coherence_selector.md`) that SELECT
(`decide_keep_or_revert`) is shared and SCORE is where instance-specific work lives; this spec
adds the SCORE for goal-owner and causal-antecedent both, via the same `C`-construction
template with a different role-compatibility table per instance.

**Multi-hop 3-hop collapse / VAMP-EP**: KEEP DISTINCT, not overlapping. VAMP-EP (per the audit's
pointer, "deep-chain composition, DEPTH_CEILING_HIGH to d=200, SYNTHETIC chains, NL-transfer
untested") solves a different problem — propagating/composing information reliably across MANY
sequential hops in a chain. The settling selector here solves SELECTION among a small set of
candidate bindings AT ONE hop/site, given already-available established propositions. They are
complementary: VAMP-EP's propagated multi-hop signal could in principle supply one of the
"established-proposition" input nodes feeding this selector's `C` at a given site (a hop's
output becomes context for the next site's binding decision), but the settling selector does
not itself do deep-chain composition, and VAMP-EP does not itself do coherence-based binding
selection among competing candidates. Do not conflate the two into one organ.

## 6. P_deflated and biggest risk

**P_deflated = 0.35** (novel-synthesis component — the entire `C`-construction design (Section
3) is this drill's own synthesis, not directly lit-verified for this exact substrate; capped at
0.50 per lit-scan calibration discipline, deflated a further notch because (a) N=1 real item
constrains any eventual result to an existence-proof scope, and (b) this spec itself required a
mid-drill correction after an initial mis-identification of the reuse target — a signal that
the design space here is easy to get subtly wrong, which should discount confidence in the
current design being exactly right on the first attempt even though the KB-disk-verification
now backs it directly).

**Biggest risk** (stated exactly, per the correction that motivated this section): **`C` secretly
re-encodes load or positional/graph-traversal structure instead of genuine role-content, and
the "settling win" is the same artifact under a new name.** Concrete failure paths to watch
for when this spec is implemented: (a) if established-proposition node COUNT per entity
correlates with the compatibility-table lookup in any indirect way (e.g. more established
propositions -> more support edges -> higher activation regardless of role-TYPE match), load
sneaks back in through the node-count side door even though `C`'s entries themselves are
load-invariant; (b) if node ordering/traversal in the relaxation implementation introduces any
position-dependent bias (e.g. iteration order affects which node's activation updates first in
a non-symmetric implementation), a positional artifact could masquerade as a role-fit win; (c)
role-label ASSIGNMENT to established propositions (i.e., how a real clause gets tagged AGENT vs
EXPERIENCER vs GOAL before it ever reaches `C`) is itself a parsing step done upstream and not
part of this settling organ — if that upstream tagging is wrong or systematically correlated
with mention recency, the settling result would inherit a recency confound through the back
door. Control 2 (role-compatibility-table scramble) and Control 3 (anti-recency item) in
Section 4 are specifically designed to catch (a)/(b) and (c) respectively; any implementation of
this spec MUST run both, not just the inherited Control 1 (load-match), or the exact failure
this session already caught twice will resurface a third time under new machinery.

## Citations (verified count: 0 new external this cycle; reused from prior verified drills)

Kintsch C-I (construction-integration, two-phase, `a(t+1)=norm(C·a(t))`), Zwaan & Radvansky
1998 five-index situation model, Trabasso & van den Broek 1985 causal-chain story grammar,
Eichenbaum relational-memory theory, Halford relational-complexity framework, Marr / Treves-
Rolls CA3 pattern completion, Amari/Wilson-Cowan CAN-bump dynamics — all previously verified in
cited prior notes (`notes/research_drill_CI_comprehension_loop_situation_model_brain_mechanism_
2026-07-21.md`, `notes/research_goal_owner_coherence_vs_mentalizing_framing_audit.md`), re-
confirmed this cycle via `tools/director_kb_query.py` (cosine=0.501/0.499) and direct disk-read
of `hdlab/iterative_attractor.py`, `hdlab/cleanup_family.py`, `hdlab/situation_model_accumulate.
py`, `hdlab/self_improving_loop.py`, `data/exp_coherence_role_conflict_crosstalk_v1/metrics.
json` (bands.shuffled_reproduces=True, bands.shuffled_collapses=False — the exact artifact
signature Control 2 above is designed to catch), `data/exp_coherence_fair_load_matched_retest_
v1/metrics.json`, `notes/capability_reconciliation_invisible_islands_audit.md` (grep, no
settling primitive found, confirming this is genuinely new build, not a missed reuse).
