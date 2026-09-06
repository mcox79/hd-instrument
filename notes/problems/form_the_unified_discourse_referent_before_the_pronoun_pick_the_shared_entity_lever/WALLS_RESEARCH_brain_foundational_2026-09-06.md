# Walls research — how brain-foundational is this to 100% (what didn't pan out, and why)

Owner directive: "research any wall you encounter. we want to understand how brain foundational this is to 100%
when it doesn't pan out." Each wall below has a literature verdict (FIDELITY GAP = brain does X we don't; GENUINE
LIMIT = brain also needs info the no-LLM invariant bars; REDUNDANT/UNITS = not a wall) AND an on-GUM measurement.

## WALL 1 — Common-noun / bridging anaphora (the located negative) — MIXED, quantified
**Measured on GUM TEST** (`exp_commonnoun_wall_gum_v1.py`, `test_commonnoun_wall.py` 3/3). Anaphoric common-noun
mentions decompose: **same_head 64.7%** (blind head-identity resolves — the ceiling, and why unification's
salience/gender completion cannot beat it there), **name_bridge 10.1%** (common→named-entity), **variant 25.2%**
(nominal variant, different head).
- **name_bridge coverage:** text-stated is-a via **apposition/copula 0.7%** + **head-in-name string containment
  18.4%** ("American College of Pediatricians"→"the college") = **19.1% glass-box recoverable; 80.9% needs WORLD
  KNOWLEDGE** the discourse never states (Argentina→"the country", Frontiers→"the publisher", Game of Thrones→"the
  series").
- **The glass-box bridge (built): blind 0.6119 → 0.6193, +0.0074 CI-sep** — a small, real, brain-foundational win
  (Heim file-card familiarity = the copula/apposition writes the type onto the card; Stanford deterministic-sieve
  "Precise Constructs"; Recasens 2009 ranks apposition a top coref feature). The bulk is world-knowledge.
- **Verdict: MIXED.** ~19% is a glass-box FIDELITY GAP (now built); ~81% of name_bridge + most of variant is a
  GENUINE no-LLM LIMIT (semantic is-a/hyponymy from world knowledge — the `entity_world_model_resolver`
  identifiability wall, Phase-1). **Register-dependent:** the literature estimate for biography/news is 65-80%
  text-derivable (appositive occupation-tagging is a stylistic convention there); GUM's academic-heavy multi-genre
  mix carries it weakly — my measured 19% sits right at the research's <20% HARD-FAIL boundary for exactly this
  reason. So the wall is not an implementation miss and not fully a limit: it is a small buildable gap plus a large
  quantified world-knowledge limit, and its size is a register fact.
Refs: Heim 1982 (FCS, definite = card already carries the predicate); Clark 1975 (bridging = the case where direct
matching FAILS); Sanford & Garrod 1981 (scenario slots = pre-stored script knowledge, not text); Poesio & Vieira
1998; Hou 2020 (of bridging cases, 38.6% pure world-knowledge); Lee et al. 2013 (Precise Constructs sieve).

## WALL 2 — Animacy phi-feature — CONFIRMED-REDUNDANT (not a wall)
Adding an animacy filter (it↔inanimate, he/she↔animate) gave **0.0 dev gain**. This is the theoretically CORRECT
result: English pronominal "gender" is a NOTIONAL/natural-gender system whose primary axis IS animacy (Quirk et al.
1985; Corbett 1991; Siemund 2008) — he/she are inherently animate, it inherently inanimate — so animacy and gender
are the same variable measured twice. RAP (Lappin & Leass 1994) folds animacy into the gender value; Orăsan & Evans
2007 literally define "animate" as "referable by he/she." The ship/country/personified-animal counterexamples are
corpus-negligible (Zaenen et al. 2004). **Verdict: not a fidelity gap, not a limit — drop the separate feature.**

## WALL 3 — Structural parallelism (Smyth) — GENUINE SCOPE LIMIT (not a wall to build across)
Parallelism (subject-pronoun→subject-antecedent) gave a tiny, non-replicating gain. The decisive reanalysis —
**Kehler, Kertz, Rohde & Elman 2008** — crossed syntactic parallelism against the discourse COHERENCE relation and
found syntactic parallelism ALONE has no effect (50-52%); the bias comes from being in a Parallel/Resemblance
coherence relation specifically, which occurs in **<2% of natural continuations** (vs Occasion 38% / Elaboration 28%).
A heterogeneous multi-genre corpus like GUM is overwhelmingly Occasion/Elaboration — a null/tiny gain is exactly what
the literature predicts. **Verdict: genuine scope limit of the cue; there is no unbuilt mechanism to add.** (Would
only help gated behind a coherence-relation detector — out of scope, low value.)

## WALL 4 — ACT-R decay constant — UNITS-MISMATCH, correctly recalibrated (not a wall)
Canonical ACT-R d=0.5 (Anderson & Schooler 1991) HURT pronoun resolution badly (−0.074); d≈1.5-2.0 works. d=0.5 was
fit on a REAL-CLOCK memory-retrieval range spanning 4+ orders of magnitude; a power-law's fitted exponent is
range-dependent (Kahana & Adler 2002). On a MENTIONS-AGO clock (range ~5), d=0.5 gives only ~2.2× activation
separation ("barely drops" — the observed symptom); matching separation needs d≈1.5-2.0. The two ACT-R discourse
models that KEPT d=0.5 (Lewis & Vasishth 2005; Li/Hale) did so because they stayed on a real-seconds clock.
**Verdict: not a theory violation — a mis-transplanted constant, now correctly refit for the discourse timescale
(copy the computation, SWEEP the parameter). The pinned d=2.0 is near-optimal for the pronoun pick; a dev-validated
d=1.5 additionally helps the entity-KB hard-link (+0.079 test).**

## Net
Two "walls" were not walls (animacy redundant; decay a units bug, fixed). One (parallelism) is a genuine cue-scope
limit with nothing to build. The common-noun wall is MIXED: a small glass-box fidelity gap (built, +0.0074 CI-sep)
plus a large, quantified world-knowledge limit the no-LLM invariant bars. Nothing here is an unexplained ceiling —
each is understood to mechanism and verdict.
