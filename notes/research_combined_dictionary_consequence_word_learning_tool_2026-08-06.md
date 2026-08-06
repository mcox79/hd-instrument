# FORMALIZE-drill: the COMBINED dictionary-lookup + consequence-learning word-learning tool (2026-08-06)

Research role, spec-only cycle (deliverable = design + pre-reg, NOT a build/run). Direct continuation of
`notes/director_POST_COMPACTION_BACKUP_2026-08-04.md`'s "USER DIRECTION (2026-08-06): THE LEARNING TOOL =
DICTIONARY-LOOKUP + CONSEQUENCE-LEARNING" entry and the decisive Signal-A-primary result that followed it
(commit `093ddc1aa`). Every claim below that cites a number, a function signature, or a file's contents is
a direct read this session, not a recalled label: `hdlab/consequence_learning_loop.py` (read in full, 437
lines), `hdlab/verb_lexical_similarity.py` (seed dicts, `register_acquired_outcome`/`clear_acquired_outcome`/
`ACQUIRED_OUTCOME_VERB_FEATURES`/`acquired_tags_for_polarity`, lines 100-330), `hdlab/self_improving_loop.py`
(`decide_keep_or_revert`, lines 92-102), `preregs/2026-08-06_anchor_propagate_oov_outcome_verb_valence_v1.md`,
`preregs/2026-08-06_consequence_learning_loop_oov_outcome_verb_valence_v1.md`, and
`experiments/data/goal_bearing_modern_eval_v1.jsonl` (re-derived this session: 44 items, 36
`outcome_in_lexicon: false`, 33 unique outcome-verb lemmas, gold 23 met / 13 unmet, majority floor
23/36 = 0.6389 -- matches both source pre-regs' own counts exactly, byte-for-byte).

---

## HEADLINE

**The two halves are not just compatible, they were already converging on the same write-back contract
(`register_acquired_outcome(word, "POS"|"NEG")` into the shared `ACQUIRED_OUTCOME_VERB_FEATURES` Tier-3
overlay) before this drill started -- so the combination is a genuinely small, surgical delta: seed the
consequence loop's per-lemma exposure counter with dictionary-derived PSEUDO-EXPOSURES before the
existing, unmodified `consolidate()` function runs, rather than building a new fusion mechanism from
scratch.** The exact rule (Section 3) is a confidence-weighted Bayesian pseudo-count injection --
precedented directly in the developmental word-learning literature (Frank, Goodman & Tenenbaum 2007/2009,
cross-situational word learning as Bayesian inference over a prior + accumulating evidence; Fazly, Alishahi
& Stevenson 2010, incremental probabilistic word-learning with per-hypothesis strength accumulation) --
where a dictionary sense's own INTERNAL CONFIDENCE (curated antonym relation = full trust; a borderline
WordNet neighbor-vote = partial trust, scaled by its margin) sets how many "consequence-equivalent votes"
it contributes to the SAME margin-based consolidation the validated consequence engine already uses. This
gives, in one mechanism: (a) dense coverage for content verbs consequence structurally cannot reach (the
`093ddc1aa` decisive finding: real content verbs recur only 1-2x per 4-novel corpus, never clearing
`MIN_CONFIRM=3`); (b) a built-in, falsifiable reason light/support verbs should NOT get falsely
polarized (their WordNet neighbor-vote margin is generically weak against a 52-word CONTENT-verb anchor,
so their pseudo-weight is small-to-zero by construction, and any real consequence evidence -- itself
close to balanced for a genuinely compositional verb -- dilutes a fixed-size prior toward the existing
`NEUTRAL_BAND`); (c) a genuine override path when consequence evidence is large enough to outweigh the
prior. One implementation trap is flagged and specified (Section 2): the dictionary prior must be seeded
into the exposure counter ONCE, before the multi-pass bootstrap loop begins, not re-injected every pass
(which would silently triple its effective weight under the existing `N_PASSES=3` default).

---

## 1. The two halves, exactly as already formalized (not re-derived)

| Half | Status | Owning spec | Owning module |
|---|---|---|---|
| DICTIONARY (dense prior) | **spec-only, not yet built** | `preregs/2026-08-06_anchor_propagate_oov_outcome_verb_valence_v1.md` + `notes/research_anchor_propagate_oov_outcome_verb_valence_2026-08-06.md` | `hdlab/wordnet_polarity_propagation.py` (NEW, not yet created) |
| CONSEQUENCE (earned refinement) | **built + validated engine, measured HARD_FAIL when run alone** | `preregs/2026-08-06_consequence_learning_loop_oov_outcome_verb_valence_v1.md` + `notes/research_consequence_learning_loop_oov_outcome_verb_valence_2026-08-06.md` | `hdlab/consequence_learning_loop.py` (built, commit `a892153ea`; re-scored Signal-A-primary at `093ddc1aa`) |

Confirmed on disk this session: `hdlab/wordnet_polarity_propagation.py` does not exist yet (`ls hdlab/`
shows no `wordnet*` file); `ANCHOR_WORDS`/`ANCHOR_POLARITY` are not present anywhere in
`hdlab/verb_lexical_similarity.py` (grepped for the symbols directly). The dictionary half is a real,
detailed, buildable spec that has simply not been implemented yet. The consequence half IS implemented,
IS wired to the same Tier-3 write-back API, and has ALREADY been run twice (the AND-gate config,
`a892153ea`, HARD_FAIL `INSUFFICIENT_YIELD`; the Signal-A-primary config, `093ddc1aa`, HARD_FAIL
grounds-WRONG). Both runs are the empirical evidence motivating this combined design, not a hypothetical.

**The decisive finding this design directly answers (`093ddc1aa`, re-read on disk this session, not
paraphrased):** consequence-alone's teacher signal is NOT sparse in aggregate (112/1431 windows fired) --
the failure is DISTRIBUTIONAL. Density concentrates on high-frequency LIGHT verbs (`be`, `make`, `take`),
which reach `MIN_CONFIRM=3` fast but on a small, easily-skewed sample (measured: `grounded_verb_polarity_
match_rate = 0.333`, below chance; `make`/`take` grounded UNMET when gold is MET). Meanwhile genuine
CONTENT outcome verbs (the note's own examples: `hoist`, `glower`, `squander`, `bedew`) recur only 1-2x
across the whole 4-novel corpus and NEVER clear `MIN_CONFIRM`, regardless of how many passes run. **A
human does not wait to encounter `squander` three times before learning it is bad -- they look it up.**

---

## 2. Integration check: are the two halves' representations compatible?

**Finding: yes, with one signature extension and one timing trap -- not a redesign.**

**(a) No representational incompatibility.** Both halves already terminate at the IDENTICAL API:
`hdlab.verb_lexical_similarity.register_acquired_outcome(word: str, polarity: "POS"|"NEG") -> None`,
writing into the SAME `ACQUIRED_OUTCOME_VERB_FEATURES` dict, consumed by the SAME two call sites
(`goal_typing._verb_classes`'s Tier-3 sentinel and `classify_2way`'s lexicon fallback, confirmed by direct
read of `_features_for`'s choke-point logic in both source pre-regs). This was not designed for
compatibility in advance -- the two lineages were formalized independently, in separate FORMALIZE cycles,
and happen to converge because both correctly identified the SAME existing write-back organ as the
right target. This is itself informative: it means the SIX-symbol acquired tag alphabet
(`acquired_tags_for_polarity`, `hdlab/verb_lexical_similarity.py:271-283`) is a genuine shared
interlingua between a symbolic/relational signal source (WordNet graph structure) and a
statistical/episodic signal source (corpus consequence counts) -- exactly the brain-analogous division
this substrate's own prior audit already named (ATL-hub relatedness / OFC-style valuation as
representationally separate but converging on one small, content-independent polarity code).

**(b) Signature delta required (flagged, not a problem).** The anchor_propagate pre-reg's Section 3c
specifies `wordnet_neighbor_propagate(lemma) -> Optional[str]` -- bare polarity, no confidence. The
combination rule below needs the underlying vote margin (Stage B) or antonym-hit flag (Stage A) to scale
the pseudo-count weight. **This is an additive extension of an unbuilt spec, not a rewrite**: change the
return type to a small `DictLookup` record (`polarity: Optional[str]`, `confidence: float`, `stage:
"antonym"|"neighbor"|"abstain"`, plus `vote_margin`/`n_neighbors` diagnostics) while leaving the underlying
DECISION LOGIC (opposition-first precedence, `NEIGHBOR_FLOOR=0.20`, `VOTE_MARGIN=0.15` abstain floor)
byte-identical to the already-reviewed anchor_propagate Section 3c. Name this function `dictionary_lookup`
in the new module to make the extended contract explicit at the call site (not a silent behavior change
under the old name).

**(c) A genuine implementation trap, caught by reading `learn_corpus`'s actual loop body (not
assumed).** `hdlab/consequence_learning_loop.py:286-354`'s multi-pass driver re-calls
`consolidate(master)` at the END of EVERY pass on the CUMULATIVE running `master` counter (not a
per-pass delta). If a naive implementation re-injected the dictionary's pseudo-counts into `master` at
the START of every pass (rather than once), the prior's effective weight would silently triple under the
pre-registered `N_PASSES_DEFAULT=3`, overwhelming any real consequence evidence that should be diluting
it. **The correct fix, confirmed against the actual code, is a single one-line change**: seed
`master: Dict[str, Dict[str, int]] = {}` (line 306) with the pre-computed dictionary pseudo-counts ONCE,
before the pass loop begins --
`master = {lemma: dict(counts) for lemma, counts in (dictionary_priors or {}).items()}` -- and change
nothing else. This works correctly with zero other edits because line 321's
`master.setdefault(rec["lemma"], {"POS": 0, "NEG": 0})[pole] += 1` already only sets a default when the
key is ABSENT; for a lemma pre-seeded by the dictionary, `setdefault` finds the existing (pseudo-seeded)
entry and accumulates real exposures ON TOP of it, pass over pass, exactly as intended. Verified by
tracing the loop by hand against the actual source, not assumed from the docstring.

**(d) Non-circularity surfaces are additive, not conflicting.** The dictionary half's non-circularity
gate is VOCABULARY-disjointness (`ANCHOR_WORDS` vs the 36-item eval's lemma set, a structural assert in
the anchor_propagate pre-reg). The consequence half's non-circularity gate is TEXT-SPAN exclusion (the
4-novel training corpus vs the eval items' `line_citation` ranges, +/-50 lines, in the consequence
pre-reg). These check two DIFFERENT leakage classes (word-identity leakage vs passage leakage) and both
apply simultaneously to the combined tool with zero interaction -- both gates are cited, reused, and
run together in Section 4 below, not merged into one weaker check.

**No fundamental integration problem found.** The one real risk this drill surfaces is (c) above (a
timing bug an implementer could introduce without noticing) and it is fully specified, not just flagged.

---

## 3. THE COMBINATION RULE (the make-or-break)

### 3.1 Constants (all pre-registered before any run; the two new ones are marked NEW)

| Constant | Value | Source |
|---|---|---|
| `MIN_CONFIRM` | 3 | `hdlab/consequence_learning_loop.py` (imported, single source of truth, never duplicated) |
| `NEUTRAL_BAND` | 0.34 | same, unchanged |
| `NEIGHBOR_FLOOR` | 0.20 | anchor_propagate pre-reg Section 3c (unchanged) |
| `VOTE_MARGIN` | 0.15 | anchor_propagate pre-reg Section 3c (unchanged; Stage-B abstain floor) |
| `VOTE_MARGIN_SATURATE` | 0.50 | **NEW** -- the Stage-B vote margin at which dictionary confidence saturates to 1.0. Chosen a priori (a decisively one-sided WordNet neighborhood vote), not tuned post-hoc. |
| `K_MAX` | `MIN_CONFIRM` (= 3) | **NEW**, but deliberately tied to the existing constant rather than a free second number: a maximally-confident dictionary hit is worth EXACTLY as much trust as a fully-confirmed consequence lock, no more. |

### 3.2 Per-lemma dictionary confidence

```
dictionary_lookup(lemma) -> DictLookup(polarity, confidence, stage, vote_margin, n_neighbors)

Stage A (antonym, higher precedence):
  antonyms = _antonyms(lemma) & ANCHOR_WORDS        # lifted PolarityLexicon._antonyms, per anchor_propagate 3c step 1
  if antonyms non-empty:
      polarity = OPPOSITE of majority anchor-polarity among antonyms (tie -> abstain)
      return DictLookup(polarity, confidence=1.0, stage="antonym", vote_margin=1.0, n_neighbors=len(antonyms))

Stage B (neighbor vote, fallback only):
  polarity, margin, n = weighted WordNet-neighbor vote over ANCHOR_WORDS   # per anchor_propagate 3c step 2, UNCHANGED decision logic
  if polarity is None or margin < VOTE_MARGIN:
      return DictLookup(None, confidence=0.0, stage="abstain", vote_margin=margin, n_neighbors=n)
  confidence = clamp((margin - VOTE_MARGIN) / (VOTE_MARGIN_SATURATE - VOTE_MARGIN), 0.0, 1.0)
  return DictLookup(polarity, confidence, stage="neighbor", vote_margin=margin, n_neighbors=n)
```

A margin sitting just above the abstain floor (e.g. 0.16) gets confidence near 0 (contributes ~0 pseudo-
votes -- functionally equivalent to abstaining even though it technically "voted"). A margin at or above
0.50 gets full confidence. This is the FIRST line of defense against the light-verb concern: a
coincidental, borderline WordNet overlap (e.g. `make` sharing a distant hypernym lineage with `build`)
produces a LOW-confidence hit by construction, not a confident one.

### 3.3 Pseudo-count injection (the fusion step, genuinely new code)

```
pseudo_counts_from_dictionary(lookups: Dict[str, DictLookup], k_max: int = K_MAX) -> Dict[str, Dict[str,int]]:
    for lemma, lu in lookups.items():
        if lu.polarity is None: continue                    # abstain -> no entry, zero influence
        n = round(k_max * lu.confidence)
        if n <= 0: continue                                 # confidence rounds to 0 -> no injection
        emit {lemma: {"POS": n if lu.polarity=="POS" else 0, "NEG": n if lu.polarity=="NEG" else 0}}
```

This dict has EXACTLY the shape `consolidate()` already consumes (`Dict[str, Dict[str,int]]`), so
`consolidate()` itself needs **zero code changes** -- it is reused verbatim. The injection happens by
seeding `learn_corpus`'s `master` counter once (Section 2c) before the first pass; every subsequent
pass's real consequence exposures accumulate additively on top via the existing `setdefault`.

### 3.4 Why this satisfies "look up first, confirm/refine/override through experience"

- **No story signal -> the looked-up sense stands.** A confident dictionary hit (antonym, or a decisive
  neighbor-vote margin >= 0.50) reaches `total = K_MAX = MIN_CONFIRM` on pseudo-counts alone, margin =
  1.0, clears `NEUTRAL_BAND` -- locks POS/NEG on pass 1 even if the corpus never produces a single
  consequence exposure for that lemma. This is the direct mechanism for the coverage claim in Section 5.
- **Consequence confirms.** Real exposures agreeing with the dictionary's polarity push the margin further
  from `NEUTRAL_BAND` and raise `total` -- report this as a `confidence_tier` (e.g. `total >= 6` with
  agreement = HIGH) for the completion report, informational only, not a new gate.
- **Consequence refines.** A WEAK dictionary hit (confidence well under 1.0, pseudo-count below
  `MIN_CONFIRM` alone) stays `PENDING` until real exposures arrive; when they do, they combine additively
  with the (small) pseudo-count to reach a verdict the dictionary alone could not have supplied confidently.
- **Consequence overrides when it should.** Since `pseudo_count` is a FIXED additive constant capped at
  `K_MAX=3`, the combined margin `(pseudo_pos + real_pos - pseudo_neg - real_neg) / total` is mathematically
  guaranteed to converge toward whatever the REAL evidence indicates as `real_total` grows arbitrarily
  large, regardless of the prior -- a textbook Bayesian prior-gets-washed-out-by-data property. A
  dictionary POS lock (pseudo_pos=3) facing 8 real NEG exposures: total_pos=3, total_neg=8, margin =
  -5/11 = -0.4545, which clears `-NEUTRAL_BAND` -- flips to NEG. A dictionary POS lock facing only 2 real
  NEG exposures does NOT flip (margin = 1/5 = 0.20, inside the neutral band -- correctly reported as
  MIDDLE / de-confident rather than silently kept at full-confidence POS).

---

## 4. Light-verb / spurious-polarization handling (the task's explicit stress-test)

Two independent lines of defense, stated precisely so the claim is checkable, not asserted:

1. **Structural (Section 3.2):** a light/support verb's WordNet neighborhood, voted against a 52-word
   CONTENT-verb anchor (`mend, fix, sink, break, ...` -- no light verbs in `ANCHOR_WORDS` by construction,
   since `ANCHOR_WORDS = OUTCOME_SEED_POS | OUTCOME_SEED_NEG` and neither seed dict contains a light
   verb), should generically produce either an outright abstain (no sense-overlap clears
   `NEIGHBOR_FLOOR`) or a low-margin, low-confidence hit (a coincidental partial sense overlap, e.g. one
   of `make`'s dozens of senses touching `build`'s hypernym lineage) -- either way, `pseudo_count` rounds
   to 0-1, well under `MIN_CONFIRM=3`, so **a light verb structurally cannot self-lock from the dictionary
   half alone.**
2. **Statistical (the `093ddc1aa`-informed correction):** the measured finding is that light verbs are
   exactly the words that DO accumulate real consequence exposures fastest (high corpus frequency) -- but
   the SAME measurement showed those exposures can be skewed by small-sample noise (`be`/`make`/`take`
   locked to the WRONG pole from as few as 3 exposures). The combined design's `NEUTRAL_BAND=0.34`
   threshold is unchanged from the validated engine, so this specific failure mode is **not fully solved
   by combination alone** -- flagged honestly below as the sharpest pre-registered risk, not swept under
   a claim of "fixed."

**Honest risk, stated precisely:** if a light verb both (a) draws a spuriously-confident Stage-B
dictionary hit AND (b) its first few real exposures happen to agree with that spurious hit by chance, the
combined design will lock it MORE confidently than consequence-alone would have (the pseudo-count and the
skewed sample reinforce rather than correct each other). This is why the pre-reg (Section on falsifiable
predictions) makes the specific, sharp claim **"no `LIGHT_VERB_CANARY` word may reach a POS/NEG lock via
dictionary-pseudo-count alone, zero real exposures"** a HARD-FAIL gate on its own, not folded into the
aggregate light-verb-neutral-rate number the standalone consequence pre-reg already reports. This is the
single most informative test of whether the light-verb protection claim is real or aspirational.

---

## 5. Coverage-gain claim: exactly which words does the dictionary reach that consequence could not

The consequence pre-reg's own `LIGHT_VERB_NO_INHERENT_VALENCE` list (17 lemmas, pre-registered from
lexical type, not gold labels) subtracted from the 33 unique OOV lemmas in the live eval file leaves
**16 content-bearing outcome verbs**, re-derived directly this session:

`admit, agree, befriend, croak, encore, flee, improve, jell, like, rap, refuse, relent, ruin, spoil,
whip, whitewash`

These are the substrate's own concrete analogs of the decisive finding's `hoist/glower/squander/bedew`
class -- low-frequency, lexically-inherent-valence verbs. **Pre-registered (informational) prediction:**
`dictionary_lookup(lemma).polarity is not None` for a majority of these 16 (target reported, not gated,
since the true WordNet-coverage rate for this exact list is unmeasured) -- this is the number that
operationalizes "the dictionary buys coverage consequence structurally cannot reach." Report it exactly
alongside how many of these 16 ever produced even ONE consequence exposure in the `093ddc1aa` run's own
master exposure tally (expected near-zero, per the decisive finding's own "each recurs only 1-2x").

A structural equivalence worth noting for non-circularity: computing dictionary priors over the eval's 33
lemmas (cheap, primary arm) vs. over the full corpus's OOV vocabulary (thousands of lemmas, more
"production-realistic") produce IDENTICAL scoring outcomes, because `congruence_with_lexicon_fallback`
only ever reads the Tier-3 entry for a lemma that actually appears as an `outcome_verb_lemma` in the eval
-- any extra corpus-scoped dictionary entries are inert for scoring purposes. The 33-lemma-scoped version
is therefore not a narrower or unfair test, just a cheaper equivalent one.

---

## 6. Cheap decisive test / Falsifiable predictions

Full bands, ablation arms, and controls: `preregs/2026-08-06_combined_dictionary_consequence_word_learning_tool_v1.md`. Summary:

- **Cheap decisive test:** run the SAME 33-lemma dictionary lookup (deterministic, O(1) WordNet calls,
  seconds) against the ALREADY-COMPUTED `093ddc1aa` master exposure tally (no corpus re-scan needed to
  get a first read) -- inject, consolidate, score against the 36-item eval. This reuses a result already
  on disk and answers the primary question (does injecting a dictionary prior into the EXISTING failed
  consequence run turn `0.1944` into something beating `0.6389`) before a full from-scratch multi-pass
  rebuild is even necessary.
- **HARD-PASS (summary; full gates in pre-reg):** combined `primary_accuracy >= 0.75` AND
  `content_verb_subset_accuracy >= 0.70` AND combined beats BOTH the dictionary-only arm and the
  consequence-only arm (the decisive 3-way requirement) AND all non-circularity gates from both source
  pre-regs hold AND zero `LIGHT_VERB_CANARY` words lock via dictionary-pseudo-alone.
- **HARD-FAIL (summary):** combined `<= 0.6389` (majority floor), OR combined `<=` dictionary-only's own
  accuracy (combining made things no better than the dictionary alone -- falsifies the value of adding
  consequence), OR any non-circularity scramble fails to collapse, OR any `LIGHT_VERB_CANARY` word
  self-locks from the dictionary prior with zero real corroborating exposures.

---

## 7. Cross-thread synthesis

Directly resolves the earn-vs-supply fork surfaced across `notes/SYNTHESIS_grounding_wall_definitive_
2026-08-06.md`, `notes/research_anchor_propagate_oov_outcome_verb_valence_2026-08-06.md`, and
`notes/research_consequence_learning_loop_oov_outcome_verb_valence_2026-08-06.md` -- the USER's direct
correction ("the learning tool should be able to LOOK UP THE WORD IN THE DICTIONARY... just like a normal
human") reframed what looked like an either/or choice as a combination, and the `093ddc1aa` decisive
result supplies the empirical reason the combination is necessary, not merely nice-to-have (consequence
alone provably cannot reach the content-verb vocabulary at this corpus scale). This drill's contribution
is the missing THIRD piece: neither prior note specified HOW to combine a deterministic per-lemma
dictionary signal with an accumulating multi-pass statistical signal -- Section 3's pseudo-count injection
is that missing piece, and it required reading `consequence_learning_loop.py`'s actual pass-loop code
(not just its docstring) to avoid the injection-timing trap in Section 2c.

---

## 8. Substrate-product implications

- **Do not build the dictionary half in isolation and call it done.** The anchor_propagate pre-reg's own
  P_deflated (0.42) was for a WordNet-only arm; this drill's combined design is a strict superset (setting
  all real consequence counts to zero recovers dictionary-only exactly), so building the combined version
  from the start costs almost nothing extra (one optional kwarg on an existing function) and avoids a
  second FORMALIZE cycle later to re-integrate consequence.
- **Do not treat `093ddc1aa`'s HARD_FAIL as wasted.** Its own measured exposure tally (112 windows, 11
  grounded words, the specific `be`/`make`/`take` skew) is directly reusable as the cheap decisive test's
  input (Section 6) -- re-running the full multi-pass corpus scan is not required to get a first
  correctness read on the combination rule.
- **The sharpest remaining risk is honestly the light-verb self-lock failure mode (Section 4), not the
  content-verb coverage claim** (which is now backed by the `093ddc1aa` finding directly, not just
  literature precedent). Prioritize disk-verifying that specific gate before trusting any aggregate
  accuracy number from a future run.
- **`hdlab/wordnet_polarity_propagation.py` should be authored with the extended `DictLookup` signature
  from the start** (Section 2b) rather than the bare `Optional[str]` the anchor_propagate pre-reg
  originally specified, so a future cell-author does not have to retrofit the dictionary-only arm's own
  module after the fact.

---

## Citations (verified count)

**This session's direct code reads (primary evidence, 6 files + 1 data file, cited inline throughout):**
`hdlab/consequence_learning_loop.py` (full read), `hdlab/verb_lexical_similarity.py` (lines 100-330),
`hdlab/self_improving_loop.py` (lines 92-102), `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md`
(lines 1-110, the USER-DIRECTION + decisive-finding blocks), `preregs/2026-08-06_anchor_propagate_oov_
outcome_verb_valence_v1.md` (full read), `preregs/2026-08-06_consequence_learning_loop_oov_outcome_verb_
valence_v1.md` (full read), `experiments/data/goal_bearing_modern_eval_v1.jsonl` (re-derived counts
directly, not assumed).

**Reused, previously verified in the two source notes this drill builds on (not re-fetched this session):**
Turney & Littman (2003); Hamilton, Clark, Leskovec & Jurafsky (2016, SentProp); Kim & Hovy (2004);
Hatzivassiloglou & McKeown (1997); Hu & Liu (2004); Yih, Zweig & Platt (2012); Mrksic et al. (2016/2017).

**New this session (WebSearch-verified, generic academic terms per query-privacy discipline):**
Frank, Goodman & Tenenbaum (2007, "A Bayesian Framework for Cross-Situational Word-Learning," NeurIPS --
confirmed via direct search, cocolab.stanford.edu/nlp.stanford.edu-hosted paper found; combines a prior
over word-meaning hypotheses with evidence accumulated across situations, the direct mathematical analog
of Section 3's pseudo-count-prior + real-evidence-likelihood combination); Frank, Goodman & Tenenbaum
(2009, "Using Speakers' Referential Intentions to Model Early Cross-Situational Word Learning,"
Psychological Science, same lineage); Fazly, Alishahi & Stevenson (2010, "A Probabilistic Computational
Model of Cross-Situational Word Learning," Cognitive Science -- incremental per-hypothesis strength
accumulation, the closest published analog to consolidating pseudo-counts alongside real exposures
pass-over-pass).

**Sources (WebSearch):**
- [A Bayesian Framework for Cross-Situational Word-Learning](https://cocolab.stanford.edu/papers/FrankEtAl2007-NIPS.pdf)
- [A Bayesian Framework for Cross-Situational Word-Learning (NeurIPS proceedings)](https://proceedings.neurips.cc/paper/2007/hash/dd8eb9f23fbd362da0e3f4e70b878c16-Abstract.html)
- [A Probabilistic Computational Model of Cross-Situational Word Learning](https://www.researchgate.net/publication/51119054_A_Probabilistic_Computational_Model_of_Cross-Situational_Word_Learning)
- [Inducing Domain-Specific Sentiment Lexicons from Unlabeled Corpora (Hamilton et al. 2016)](https://nlp.stanford.edu/pubs/hamilton2016inducing.pdf)

**P_deflated:** the general pattern (dictionary/definitional prior + cross-situational evidence, combined
via Bayesian-style pseudo-counts) is well-triangulated against an established developmental
word-learning literature (Frank/Goodman/Tenenbaum, Fazly/Alishahi/Stevenson) AND against this substrate's
own decisive internal evidence (`093ddc1aa` directly motivates exactly this fix, not just a generic
literature analogy). Its APPLICATION -- the specific injection mechanism into `learn_corpus`, the
confidence-scaling formula, and the light-verb self-lock gate -- is this drill's own novel synthesis,
unexecuted. Two concrete uncertainties are not yet resolved by measurement: (1) the dictionary-only arm's
OWN accuracy is still unmeasured (that pre-reg has not been run), so the combined tool's ceiling is
partly inherited from an unproven number; (2) the light-verb self-lock risk (Section 4) is a real,
sharply-specified failure mode this design does not structurally eliminate, only makes less likely than
consequence-alone. Raw ~0.55 (strong precedent + clean mechanical integration + decisive internal
motivating evidence) deflated 0.20 (novel-synthesis, unexecuted, two open empirical uncertainties named
above) -> **P_deflated = 0.35** (below the 0.50 novel-synthesis cap).
