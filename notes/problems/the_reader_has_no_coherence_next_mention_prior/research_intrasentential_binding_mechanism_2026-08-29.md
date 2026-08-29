# Research drill: the brain mechanism of intra-sentential pronoun binding (2026-08-29)

Four parallel literature lanes (WebSearch/WebFetch via the `research` agent), to answer: does the brain resolve
intra-sentential pronoun binding ("the parson, who, as HE rode") via an explicit PARSE TREE + Binding Theory, or via
CUE-BASED RETRIEVAL with syntactic features as graded cues? And is our noisy-parse wall fatal? Persisted verbatim per
the prior-work discipline. **Sourcing caveat (the agents' own flag): many findings are PRIMARY-partial (abstracts /
citing text / PMC-rendered pages), as ScienceDirect/Wiley/ProQuest full text returned 403. Treat effect directions as
solid, exact numbers as unverified.**

## Lane A -- Principle B: hard filter or graded cue?
- **Chow, Lewis & Phillips (2014), Front. Psychol. 5:630 (pronouns, 5 experiments):** NO facilitative interference from
  a structurally-illicit gender-matching antecedent in any ROI -- "structural criteria can immediately restrict the set
  of candidate antecedents during initial memory retrieval." => Principle B applied HARD + IMMEDIATE + structural.
- **Badecker & Straub (2002); Clifton-Kennison-Albrecht (1997); Kennison (2003):** the opposite -- a structurally
  inaccessible but gender-matching NP measurably SLOWS pronoun reading => interference => GRADED/leaky, "binding is one
  weighted cue among several" (interactive parallel-constraint model).
- **VERDICT:** an active, UNRESOLVED dispute. Consensus: Principle B is applied EARLY and largely structurally; whether
  it fully filters or merely up-weights structure is contested. No paper argues for a hard PRE-filter that removes
  non-c-commanders before retrieval; the dominant framing is weighted-cue-during-retrieval.

## Lane B -- can cue-based retrieval ACCESS c-command? (THE PIVOTAL LANE)
- **Kush (2013) dissertation (Maryland; Phillips/Lidz):** grammar states binding via the RELATION c-command, but
  "in incremental processing, antecedents must be retrieved from a cue-based, associative, content-addressable memory
  in which relations such as c-command are difficult to use as cues... the c-command constraints of formal grammars are
  predicted to be POORLY implemented by the retrieval mechanism." Resolution: retrieval does NOT query c-command
  directly; it uses a domain-restricted, NON-RELATIONAL, ITEM-LEVEL "LOCAL" feature (a structural-accessibility proxy)
  that CORRELATES with c-command in tested configurations.
- **Kush, Lidz & Phillips (2015), JML 82 (bound-variable pronouns):** referential NPs are accessed regardless of
  c-command; only QUANTIFICATIONAL antecedents show a hard c-command requirement. "A relational constraint like
  c-command is not an item-based feature... posing a direct implementation challenge for content-addressable retrieval."
- **Parker (2019), Cog. Sci. 43(3):** cues combine NONLINEARLY (multiplicatively/interactively), not as a strict linear
  sum -- full-cue-match antecedents favored more than a linear model predicts.
- **Cunnings & Sturt (2014); Cunnings & Felser (2013):** structural sensitivity is itself GRADED, weighted more heavily
  than feature cues, and resource-/individual-dependent (WM span modulates it) -- not an all-or-nothing filter.
- **VERDICT (the one that reframes our wall):** the brain does NOT compute a parse tree and read c-command off it for
  pronoun retrieval. It uses ITEM-LEVEL structural PROXIES (clause-mate-hood, a LOCAL-domain feature, subjecthood) as
  WEIGHTED, nonlinearly-combined cues. => our approach (add structural proxies as cues) IS the brain-faithful one; a
  full parse tree is NOT required by the brain either.

## Lane C -- linear vs structural distance; relative clauses
- **Gordon, Grosz & Gilliom (1993) Repeated-Name-Penalty:** cost tracks SUBJECTHOOD (the Cb), not surface recency ->
  grammatical prominence > linear distance.
- **Gernsbacher, Hargreaves & Beeman (1989), within single 2-clause sentences:** clause-recency advantage is real but
  TRANSIENT (decays in a few hundred ms); FIRST-MENTION / subject prominence is the DURABLE cue.
- **Kazanina et al. (2007); Sturt (2003):** intra-sentential binding uses EARLY, STRUCTURALLY-GATED active search --
  the parser restricts candidates by clause structure from the earliest moment. Implies binding depends on the parser
  having correctly registered clause STRUCTURE (embedding depth / accessibility), not surface heuristics.
- **Cuetos & Mitchell (1988); van Gompel et al.:** no universal recency preference; attachment competes with a
  structural/predicate-proximity force and is race-based, not fixed-nearest.

## Lane D -- does binding require a FULLY CORRECT parse? (is our noisy parse fatal?)
- **Ferreira & Patson (2007) "good-enough" processing:** comprehenders routinely build shallow, sometimes-incorrect
  representations that suffice for the task -- the system TOLERATES incomplete/incorrect structure without catastrophic
  failure. (Evidence base is thematic-role/attachment, NOT anaphora directly -- a flagged gap.)
- **Frazier & Clifton Construal; Swets et al. (2008):** RELATIVE-CLAUSE ATTACHMENT is the paradigm case of principled,
  goal-modulated UNDERSPECIFICATION -- readers often never commit to an attachment at all. Degree of underspecification
  is gradient with task goals.
- **Hemforth, Konieczny & Scheepers (2000):** RC attachment and anaphoric/discourse-accessibility processes are computed
  IN PARALLEL (a "race"), NOT "parse-first-then-bind" -- attachment and binding interact online.
- **VERDICT:** the brain binds on PARTIAL/underspecified structure and degrades gracefully; a noisy/incomplete parse is
  NOT fatal in principle. GAP (flagged by the agent): no study directly measures 3rd-person-pronoun accuracy as a
  function of a MISPARSED relative clause -- the exact misparse->binding-failure chain is inferred, not proven.

## SYNTHESIS -> what it told us to build, and what we measured
The brain-faithful mechanism is **cue-based retrieval with ITEM-LEVEL structural-proxy cues** (Kush 2013), combined
nonlinearly (Parker), operating on **partial structure with graceful degradation** (Ferreira-Patson, Swets). This is
NOT the brief's coherence next-mention prior, and it does NOT require a full parse tree.

**We built it** (`exp_coref_coherence_next_mention_prior_v1`, the `brain_faithful_cue_binding` arm): added fine
linear-distance, clause-mate-hood / Principle-B (from `gov_verb`), relative-clause-head, and local-subjecthood as
WEIGHTED cues to the graded retrieval, jointly re-tuned on DEV. **Result: it recovers 0/205 of the residual** (only the
Principle-B cue took a small, correct-signed weight; the rest tuned to 0; DEV full 0.7985->0.7996, TEST full slightly
down).

**Why (the sharpened, research-grounded diagnosis):** the mechanism is faithful, but our item-level structural PROXIES
are degraded -- they are extracted from a NOISY spaCy parse on 200-year-old prose (the brain's proxies come from its own
reliable incremental parse). And the proxies that DO fire are EXCLUSIONARY (Principle B rules a candidate OUT); they
never POSITIVELY identify which of ~44 remaining candidates is the antecedent, because that requires the relative-clause
attachment RELATION (parson<->he) -- exactly the relational information Kush shows retrieval cannot use without reliable
structure. So the wall is PROXY QUALITY, bottlenecked by the PARSER on archaic prose -- a named, brain-grounded,
adjacent-component limitation, not a wrong mechanism.
