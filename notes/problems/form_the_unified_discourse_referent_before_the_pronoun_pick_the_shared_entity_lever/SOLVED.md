---
problem: form_the_unified_discourse_referent_before_the_pronoun_pick_the_shared_entity_lever
status: SOLVED
bar: "PASS = a UNIFIED-referent representation (one discourse referent per entity, merged across name + common-noun + pronoun, updated incrementally file-change style) that lifts AT LEAST TWO downstream consumers -- the pronoun coref pick AND (affect-experiencer OR entity-KB hard-link) -- CI-separated over the current SEPARATE-TRACKING reader, measured on MODERN annotated gold (GUM or modern OntoNotes, NOT 19c LitBank), with an info-free twin (shuffled identity evidence, same machinery + shape) LOSING and NO-regress on named coref. Report CI half-width + null p95; recompute each floor on the item's OWN population. A rigorous located NEGATIVE ... is a FULL PASS."
result: "On MODERN gold (GUM V12.1.0, 275 docs, held-out TEST=137 docs), scorer=antecedent resolves to correct gold entity. TWO consumers lift CI-separated over the separate-tracking reader with the info-free twin losing: (1) PRONOUN PICK 0.3621->0.4681, +0.1060 CI[+0.079,+0.133] (half-width 0.027), twin(null) 0.2034; (2) ENTITY-KB HARD-LINK (named-entity pronoun files under the name-carrying referent) 0.3963->0.4682, +0.0719 CI[+0.023,+0.120] (half-width 0.048), twin(null) 0.0819. NO-regress on named coref (0.6781->0.6845, +0.0064)."
floor: "Strongest simple floor recomputed per population on TEST: pronoun -- the separate-tracking reader itself 0.3621 (> string-identity 0.307, recency 0.293); unified beats it +0.1060 CI-sep. entity-KB hard-link -- separate reader 0.3963; unified +0.0719 CI-sep. common -- blind head-identity 0.5412 (unified 0.4879 does NOT beat it: located negative). Oracle-unified (gold clusters) ceiling: pronoun 0.584, kb 0.547."
controls: "info-free TWIN (shuffled identity evidence, same machinery+shape) LOSES on both lift consumers (pronoun uni-twin +0.265 CI-sep; kb uni-twin +0.386 CI-sep) -- excludes 'any incremental machinery'. Leave-one-out ablation: gender agreement load-bearing for the pronoun pick (+0.036 CI-sep), ACT-R grammatical-prominence salience load-bearing for the kb hard-link (+0.137 CI-sep) -- excludes 'recency alone'. UPSTREAM control: positional roles (the live _assign_roles) vs gold grammatical roles drops the kb hard-link -0.084 CI-sep -- the downstream benefit requires a brain-foundational upstream role assigner. Dev/test split by doc parity; PINNED ACT-R decay d=2.0 near-optimal on TEST (dev-tuning does not beat it on the pronoun pick)."
files_changed: "experiments/fetch_gum_coref_v1.py, experiments/gum_coref.py, experiments/exp_unified_referent_gum_v1.py, experiments/exp_unified_referent_ablation_gum_v1.py, experiments/exp_unified_referent_optimize_gum_v1.py, experiments/exp_unified_referent_optimizations_gum_v1.py, experiments/exp_commonnoun_wall_gum_v1.py, verification/test_unified_referent_gum.py, verification/test_unified_referent_ablation.py, verification/test_unified_referent_optimize.py, verification/test_commonnoun_wall.py, notes/problems/<slug>/WALLS_RESEARCH_brain_foundational_2026-09-06.md, data/corpora/gum/ (acquired offline asset, gitignored; fetch script pins GUM V12.1.0 @ 22fdf87). NO hdlab/ written (Q111 -- proposed wire only)."
reverify: ".venv/Scripts/python.exe verification/test_unified_referent_gum.py  (5/5; full suite: test_unified_referent_ablation.py 3/3, test_unified_referent_optimize.py 2/2, test_unified_referent_optimizations.py 2/2, test_commonnoun_wall.py 3/3 = 15/15; GUM parse positive control: experiments/gum_coref.py --self-test)"
---

# SOLVED — form the unified discourse referent (the shared entity lever)

**STATUS: SOLVED** (solver scope; WIP until owner marks DONE). Glass-box, NO external LLM at inference (THE invariant).
NO `hdlab/` written — mechanism proved in `experiments/`; the Q111 wire is proposed, not landed.

## What the disk said that the brief did not (read first)
The brief said "the reader tracks names, common nouns, and pronouns in SEPARATE passes." **On disk it is already
PARTLY unified and default-ON** (`hdlab/situation_reader.py`: `referent_per_np=True`, `commonnoun_situation_gate=True`,
`commonnoun_canonical=True`; the DECOUPLE keeps two mention views). The ONE genuinely-open lever the prior pick-solve
named is **re-keying the pronoun-anaphora overlay entity — keyed today by SURFACE HEAD STRING in
`state_of_mind.EntityState.head` — to ONE canonical referent that accumulates evidence across all three mention types.**
That is what this problem builds and measures, on modern gold. (The +0.020/+0.034/0.605 numbers in the brief are the
PRIOR pick-only 19c result and are not requoted as this result — this headline is on GUM.)

## The obstacle the bar created, and how it was cleared (owner-authorized)
The bar BANS 19c LitBank as load-bearing and demands GUM or modern OntoNotes. **No modern full-chain coref corpus was
on disk** (GAP is pronoun->2-name only; UD-EWT is parse-only). I acquired **GUM (Georgetown University Multilayer),
OntoGUM CoNLL-U coref layer**, as a static offline foundation asset (owner-approved; the no-LLM invariant is about
INFERENCE, not offline gold). Pinned to **release V12.1.0, commit `22fdf87f9c71...`**; reproducible fetch script
`experiments/fetch_gum_coref_v1.py`; provenance in `data/corpora/gum/PROVENANCE.md`. 275 GUM docs (36,332 mentions,
8,400 chains) across 18 modern genres, + 26 GENTLE OOD docs. One file gives gold UD POS (mention type:
PROPN=name/NOUN=common/PRON=pronoun), gold Number, and coref chains — everything the task needs.

## How the brain does this (the opening move)
- **PINNED — Heim(1982)/Kamp DRT FILE-CHANGE semantics:** ONE file card per discourse entity, OPENED on first mention,
  UPDATED (never re-created) by EVERY subsequent mention whatever its surface form. Names, common nouns and pronouns
  all write to the SAME card once bound.
- **PINNED — ACT-R base-level activation for salience** (`hdlab.salience_binder`, reused unchanged): B = ln(Σ w(role)·dt^−d),
  role = Centering Cf-ranking grammatical prominence. The card's activation uses its FULL cross-type mention history —
  the lever the separate passes throw away.
- **PINNED — Ariel (1990) Accessibility Hierarchy** (the finding that made the mechanism correct): the resolution CUE is
  mention-type-specific. Pronouns (high accessibility) → salience/prominence + gender. Definite descriptions → recency.
  Names → identity. Applying the pronoun's salience cue to nominals is WRONG and hurts (measured, below).
- **OUR-INVENTION-UNDER-TEST (swept, not adopted):** the ACT-R decay d (held-out; d=2.0 pinned default, d*=1.5 dev-best
  for kb), the merge gate. Graded/recall-safe agreement (mismatch penalizes, unknown never excludes) is Nref-faithful.

REUSED, not rebuilt: `hdlab.salience_binder` (ACT-R), `hdlab.coref.EntityAliaser` (name-variant merger), the given-name
gazetteer. The mechanism lives in `experiments/exp_unified_referent_gum_v1.py::Resolver` — one incremental resolver with
identical scoring in both arms, differing ONLY in the referent representation (UNIFIED file-card vs SEPARATE surface-head
fragments).

## The result — TWO consumers lift on modern gold (bar MET)
Held-out TEST (137 GUM docs), antecedent-resolution accuracy over anaphoric mentions; doc-level paired bootstrap.

| consumer | separate reader | UNIFIED | Δ (CI, half-width) | info-free twin (null) |
|---|---|---|---|---|
| **PRONOUN PICK** (n=3132) | 0.3621 | **0.4681** | **+0.1060** CI[+0.079,+0.133] hw 0.027 | 0.2034 (uni−twin +0.265 CI-sep) |
| **ENTITY-KB HARD-LINK** (n=1307) | 0.3963 | **0.4682** | **+0.0719** CI[+0.023,+0.120] hw 0.048 | 0.0819 (uni−twin +0.386 CI-sep) |
| NAME (no-regress, n=2488) | 0.6781 | 0.6845 | +0.0064 CI[−0.011,+0.022] | 0.2524 |
| COMMON (located negative, n=2855) | 0.4872 | 0.4879 | +0.0007 | 0.4872 |

- **Pronoun pick** beats the strongest floor (the separate-tracking reader itself, 0.362; also far above string-identity
  0.307 and recency 0.293) by +0.106 CI-sep. Oracle-unified (gold clusters) ceiling 0.584 → headroom is residual
  clustering error, not the scorer.
- **Entity-KB hard-link** = for a pronoun whose gold entity is NAMED, does it resolve to the referent CARRYING the name
  (so the fact files under the queryable named record)? Separate tracking can resolve a pronoun to a *nameless fragment*
  of the same entity — coref-ish-right but the KB then cannot answer "what did [Name] do." Unification fixes this
  (+0.072 CI-sep). This is the bar's second consumer (entity-KB hard-link option).
- **NO-regress on named coref** holds (+0.006, CI includes 0).

## Which cue carries the lift (leave-one-out ablation, `test_unified_referent_ablation.py`)
- **Pronoun pick:** load-bearing = **gender completion** (−gender −0.036 CI-sep) + the **structural unification itself**
  (~+0.06 residual: one card = complete cross-type history + correct candidate set). ACT-R adds little here (gender does
  the disambiguation on the full pronoun population); the **name-variant aliaser is register-NEUTRAL on modern text**
  (−aliaser ≈ 0, not CI-sep) — corroborating why names don't lift on GUM (below).
- **Entity-KB hard-link:** load-bearing = **ACT-R grammatical-prominence salience** (−ACT-R, i.e. pure recency, −0.137
  CI-sep). Prominence routes the pronoun to the salient NAMED protagonist so the fact files under the name — a clean
  brain-foundational result.

## Upstream must be brain-foundational too (the owner's central point, measured)
The user's directive — *every component, you AND upstream, brain-foundational* — is confirmed with a control. The
referent's upstream is (a) mention introduction (`referent_per_np`, DRT introduce-every-NP, PINNED, default-ON) and
(b) the grammatical-role / prominence signal from the parse. **Replacing gold grammatical roles with the live reader's
POSITIONAL `_assign_roles` (agent=preverbal) drops the entity-KB hard-link −0.084 CI-sep** (the pronoun pick is robust,
+0.016 n.s.). So the downstream benefit is only realized when the upstream role assigner is brain-foundational — exactly
the filed **P2 `swap_the_positional_role_assigner_for_the_brain_foundational_competition_model`** (Competition-Model
cue-competition). The unified referent and the Competition-Model upstream are complementary: land both.

## The located negatives (a full pass under the bar; the deeper truth)
Unification's lift is CUE-SPECIFIC, and this refines the brief's premise that "one shared record is the multiplier the
separate passes throw away" for ALL consumers:
- **COMMON nouns do NOT lift** — blind head-identity (0.541) is the no-LLM ceiling; unified (0.488) does not beat it.
  Definite-NP anaphora is head/recency-driven (Ariel), so the salience/gender that unification completes doesn't reach
  it. Cross-type nominal bridging ("the woman"→"Elizabeth") that WOULD need the unified record requires world knowledge
  the no-LLM invariant bars (the `entity_world_model_resolver` identifiability wall, filed Phase-1).
- **NAME resolution is flat** (+0.006, no-regress) — the `EntityAliaser` variant-merging that gave +0.020 on 19c FAMILY
  NOVELS is register-neutral on modern multi-genre GUM (fewer name variants; its precision-abstention costs the recall
  blind surface-head keying captures). This is a **register effect**, mirroring the referent_per_np register finding
  (introduction is register-invariant; the linker is register-sensitive). The deployable unified referent therefore
  uses aliaser-merge ∪ blind-exact-surface for names (dominates both; no-regress guaranteed).

## Optimization (dev/test, `test_unified_referent_optimize.py`)
The only free parameter is the ACT-R decay d. Dev-sweep: the PINNED brain-foundational default **d=2.0 is near-optimal
for the pronoun pick** (dev-tuned d=1.5 does not beat it on TEST, −0.001). A dev-validated **shallower d*=1.5 IMPROVES
the entity-KB hard-link +0.079 on held-out TEST** (a slower base-level decay keeps the frequently-mentioned named
protagonist activated) — a legitimate per-corpus refinement, reported not adopted (d=2.0 matches the validated live
binder; the headline is the conservative d=2.0).

## Brain-foundational optimizations — ALL tested, dev-adopted, test-reported (owner: "do all")
Seven candidate optimizations, each a PINNED brain operation, dev-selected on a pronoun+kb+common objective (adopt
only if it does NOT regress the pronoun pick), reported once on TEST (`exp_unified_referent_optimizations_gum_v1.py`,
`test_unified_referent_optimizations.py` 2/2). **The base unified referent already saturates the CUE-PARAMETER family these optimizations live in** (decay /
agreement / salience / parallelism): the dev-adopted set (is-a bridge + parallelism) MAINTAINS the headline —
pronoun 0.4732 (+0.111 vs separate, CI-sep), kb 0.4828 (+0.087 vs separate, CI-sep), name no-regress, twin loses —
but its gains OVER the base unified are small and not CI-separated. **This is NOT the absolute no-LLM ceiling** — the
remaining headroom is elsewhere: (1) CLUSTERING quality — the unified pronoun pick 0.468 vs the ORACLE-unified (gold
clusters) 0.584 is a 0.116 GLASS-BOX gap (my incremental referents aren't the gold clusters; better mention linking,
the P2 role assigner, close it — no LLM needed); (2) above the oracle, genuine ambiguity where salience+gender+
agreement underdetermine the antecedent — PART world-knowledge/semantics (the no-LLM-barred fraction) and PART the
coherence/next-mention prior (Kehler-Rohde, owner-DONE dead ×2). So "the cue family is saturated" is the honest claim;
the real levers above it are glass-box clustering and (barred) world knowledge, not more cue-tuning. Honest ledger:
- **ADOPTED — glass-box common→name is-a bridge** (Heim file-card familiarity; apposition/copula + head-in-name): dev
  +0.015, small.
- **ADOPTED — Smyth parallelism**: dev +0.020 (marginal; the literature says weak — Kehler et al. 2008: syntactic
  parallelism alone is null, the effect rides the Parallel/Resemblance coherence relation, <2% of continuations — so
  a tiny, non-CI-sep gain is exactly expected; kept as a low-weight tie-breaker).
- **REJECTED — ACT-R decay d=1.5**: a TRADE, not a free win — it lifts kb/common but REGRESSES the pronoun pick −0.02
  on dev (a shallower base-level decay keeps the protagonist active but loses recency discrimination on the pick). Not
  globally adopted; available as a kb-specific tuning if kb is prioritized. (Canonical d=0.5 HURTS badly, −0.074: a
  units-mismatch — d=0.5 was fit on a real-CLOCK range; on a mentions-ago clock the right refit is d≈1.5-2.0, Kahana &
  Adler 2002. The pinned d=2.0 is near-optimal for the pronoun pick.)
- **REJECTED — graded Nref write** (divisive normalization, hold-both): net-NEGATIVE on GUM (dev −0.036). The +0.027
  it earned on LitBank who-did-what does NOT transfer to GUM pronoun/kb resolution — an honest located negative.
- **REJECTED — animacy φ-feature**: 0.0 dev gain (CONFIRMED-REDUNDANT — English pronominal gender IS a natural-gender
  system whose primary axis is animacy: he/she animate, it inanimate, so animacy = gender measured twice; Quirk 1985;
  Corbett 1991; Zaenen 2004). Drop it.
Every wall was researched to a literature verdict (FIDELITY GAP vs GENUINE LIMIT) — detail in
`WALLS_RESEARCH_brain_foundational_2026-09-06.md`.
- **Common-noun wall (MIXED — a small glass-box FIDELITY GAP + a large quantified no-LLM LIMIT):** researched to 100%
  (`exp_commonnoun_wall_gum_v1.py`, `test_commonnoun_wall.py` 3/3). Anaphoric common nouns are 64.7% same-head (blind
  head resolves), 10.1% common→named-entity, 25.2% variant. Of the common→name cases, a GLASS-BOX bridge
  (apposition/copula 0.7% [Heim file-card familiarity; Stanford Precise-Constructs sieve] + head-in-name string
  containment 18.4% ["American College of Pediatricians"→"the college"]) recovers **19.1%; the other 80.9% needs WORLD
  KNOWLEDGE** the discourse never states (Argentina→"the country", Frontiers→"the publisher"). The glass-box bridge
  (built) lifts common-noun resolution +0.0074 CI-sep. **Register fact, not a bug:** the literature estimate is 65-80%
  text-derivable on biography/news (appositive occupation-tagging convention); GUM's academic-heavy mix carries it
  weakly — my 19% sits right at the research's <20% HARD-FAIL boundary. So the located negative is a genuine,
  quantified, mostly-world-knowledge limit — understood to mechanism, not an implementation miss.

## No downstream consumer regresses
On modern gold, every consumer is up-or-flat: pronoun +0.106, entity-KB hard-link +0.072, name +0.006 (no-regress),
common +0.0007 (flat). The mechanism does NOT reintroduce the `referent_per_np` turn-on coref-collapse (0.48→0.02): that
was caused by flooding the pronoun pool with FEATURE-BLANK fresh-singleton NP referents; this re-keys EXISTING referents
and never adds blank distractors to the pool. The live-LitBank consumer re-validation is the strategy session's at
integration (I am scope-barred from the live reader); the no-regression evidence here is on modern gold.

## PROPOSED hdlab WIRE (Q111 — strategy lands it; do NOT land from here)
1. **Re-key the pronoun-anaphora overlay entity to the unified referent.** In `situation_reader.py`, where the pronoun
   path builds `state_of_mind` overlay entities keyed by `EntityState.head` (surface head string), maintain ONE referent
   per discourse entity that accumulates (time, role) history + gender + number across name+common+pronoun mentions, and
   resolve pronouns by ACT-R activation (`hdlab.salience_binder`) over these unified referents with recall-safe
   gender/number agreement. Names merge via `EntityAliaser` ∪ blind-exact-surface (no-regress); common nouns by
   head-lemma + recency (Ariel). This is the "run graded retrieval over the resolver stream" the organ already queues,
   with the referent unified.
2. **Guardrails (measured):** keep event-centrality OFF (prior net-negative); do NOT apply the salience cue to nominal
   resolution (Ariel — hurts names/commons); the name aliaser is register-gated (helps 19c, neutral modern) — keep the
   blind-surface union so names never regress; the entity-KB hard-link benefit needs the P2 Competition-Model upstream
   to be fully realized (positional roles cost −0.084).
3. **DO NOT** wire gender propagation, recall-safe-only agreement, or the aliaser-alone name path as improvements — they
   are register/consumer-specific.

## KEY REALIZATIONS (the enabling moves)
- **"Feed the SAME ACT-R binder unified vs fragmented histories" isolates the lever cleanly** — the contrast is purely
  the referent representation, not the resolver. That reframed a messy multi-pass comparison into a one-variable test.
- **The cue is mention-type-specific (Ariel), and I was applying the pronoun's salience cue to nominals.** The first
  runs had the twin BEATING unified on common nouns — the tell that salience-max was the wrong cue there. Switching
  nominals to identity/recency fixed the over-merge and revealed the true, pronoun-concentrated lever.
- **The entity-KB hard-link is where cross-type unification uniquely pays off** — not raw coref accuracy, but "does the
  fact file under the NAMED record." That is the consumer that separates unified from separate without being a tautology
  (the twin loses hard, 0.082).
- **Acquiring the right MODERN gold was the unlock.** Every prior unification number was 19c; the finding that the
  name-variant aliaser is register-specific only became visible once measured on modern multi-genre text.
- **Decomposing a wall by resolution-TYPE separates a fidelity gap from a genuine limit.** The common-noun located
  negative looked like a flat "world-knowledge" wall; measuring same-head vs name-bridge vs variant, then splitting
  name-bridge into text-derivable (appos/copula 0.7% + head-in-name 18.4%) vs world-knowledge (80.9%), turned "it
  doesn't help" into "19% is a glass-box gap I can build, 81% is barred" — and caught that my first is-a extractor
  (appos/copula only, 0.7%) was mis-reading the wall until I inspected the actual GUM cases and added head-in-name.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md §2b, COREFERENCE / ENTITY TRACKING)
The 2026-09-04 entry FLAGGED (not landed) "resolution-overlay-by-discourse-entity, keyed by surface token → fragments a
protagonist across name variants, +0.043 CI-sep (gold clusters, 19c)." **Now operationalized and measured GLASS-BOX on
MODERN gold (GUM):** a DRT file-change unified referent lifts the pronoun pick +0.106 CI-sep and the entity-KB hard-link
+0.072 CI-sep over the separate-tracking reader, twin loses, name no-regress. NEW findings to fold in: (1) the lift is
CUE-SPECIFIC per Ariel's Accessibility Hierarchy — unification's completed salience/gender reaches the salience-driven
PRONOUN cue only; nominal resolution is identity/recency-driven and does not lift (common-noun blind head-identity is the
no-LLM ceiling; cross-type nominal bridging is the world-knowledge wall). (2) The surface-head fragmentation the audit
names is a 19c-FAMILY-NOVEL effect — the `EntityAliaser` variant-merger is register-NEUTRAL on modern multi-genre text, so
on modern text "unified" for names ≈ blind surface-head. (3) The entity-KB hard-link benefit REQUIRES the brain-foundational
upstream role assigner: positional roles (live `_assign_roles`) cost −0.084 CI-sep vs gold grammatical roles — cross-links
the P2 Competition-Model problem.

## Adjacent components (seeds for next problems)
- **P2 Competition-Model role assigner** — measured load-bearing for the entity-KB hard-link (+0.084). Land it WITH this.
- **Glass-box common-noun bridge (small, buildable now):** apposition/copula (Heim file-card / Stanford Precise-Constructs)
  + head-in-name string containment recover ~19% of common→named-entity anaphora, +0.0074 CI-sep — a brain-foundational
  refinement to the common-noun binder (stronger on news/bio register than GUM's academic mix).
- **Common-noun / entity-KB WORLD-KNOWLEDGE bridging** — the ~81% remainder is the located no-LLM wall
  (`entity_world_model_resolver` identifiability, Phase-1): Argentina→"the country" needs a semantic is-a/scenario prior.
- **Register-adaptive name aliasing** — the `EntityAliaser` variant-merge helps 19c family novels, is register-neutral on
  modern multi-genre GUM; keep the blind-surface union as the default / gate the aliaser by register.
- **GENTLE OOD (26 docs) acquired** — an out-of-domain robustness arm is available and cheap; next-step corroboration.

---

## TLDR (plain English)
A good reader knows "Elizabeth", "the young woman", and "she" are all ONE person and keeps a single mental record for
her. Our reader kept separate records and re-guessed the identity in each of its three passes. I built the single shared
record — one file per character, updated by every mention — and, because the 19th-century books the project used are
banned as a yardstick, I first downloaded a modern, mixed-genre corpus of real annotated text to test on. The shared
record makes deciding who "he"/"she" means clearly better (about 36% → 47% right, a solid gap a scrambled control can't
fake), and it makes facts file correctly under the right *named* character (about 40% → 47%, another clean gap) — two
separate improvements, both real. It does NOT help with plain descriptions ("the man", "the paintings"): those are
resolved by the word itself, and linking a description to a name needs outside world-knowledge our no-outside-AI rule
forbids — an honest, located limit. A key catch: this only pays off fully if an *upstream* piece (deciding who is the
grammatical subject) is also done the brain's way, not by word position — doing it by position throws away a third of one
of the wins. Nothing is wired into the live system yet; that's one focused change for the other session.

## QUESTIONS
None blocking. One judgement call for the owner: the bar's second consumer was "affect-experiencer OR entity-KB
hard-link"; GUM has no affect annotation, so I measured the **entity-KB hard-link** (the OR-branch), on modern gold. If
you specifically want the affect-experiencer number, that instrument is 19c-LitBank-only today (informational under the
ban) — the mechanism is the same pronoun lift feeding it.

## NEXT STEPS
1. Strategy lands the Q111 wire (re-key the pronoun overlay to the unified referent; guardrails above), then re-verifies
   the two consumers on the live reader.
2. Land the **P2 Competition-Model role assigner** alongside — measured load-bearing for the entity-KB hard-link.
3. The remaining nominal residual is the world-knowledge bridging wall (Phase-1 `entity_world_model_resolver`), not a
   fidelity gap in this component.
