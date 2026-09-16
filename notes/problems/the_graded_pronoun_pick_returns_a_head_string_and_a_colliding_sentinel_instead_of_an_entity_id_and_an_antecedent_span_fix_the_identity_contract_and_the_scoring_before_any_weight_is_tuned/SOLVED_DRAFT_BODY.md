# (draft body -- merged into SOLVED.md when the measured rows land; delete this file before commit)

## 0. THE OPENING MOVE -- how the brain does THIS (PINNED vs OUR-INVENTION)

A pronoun is not resolved to a word. It is resolved to a **discourse entity**: a **file card** (Heim 1982,
file-change semantics; Karttunen 1976 discourse referents) / an **object file** (Kahneman & Treisman 1992),
opened when the entity is introduced and updated at every later reference. Retrieval is **content-addressable
and cue-based** (Anderson & Schooler 1991 base-level activation; Lewis & Vasishth 2005; McElree direct
access): the probe's cues (person/gender/number, animacy) are matched against the FILE's accrued card, the
activation is summed over the FILE's whole reference history, and what comes back is the FILE. The **mention
that supplied the evidence** is the antecedent -- a position in the text, not a string. The binding domain of
a plain pronoun **excludes its clause-mate co-argument** (Chomsky 1981 Principle B; Reinhart 1983), and a
reflexive **requires** one (Principle A) -- a relation over the PARSE, and an exclusion on the co-argument's
FILE.

| piece | status |
|---|---|
| the pronoun resolves to a FILE, and the file accrues features + history over its mentions | **PINNED** (Heim; Kahneman-Treisman) |
| ACT-R base-level activation over the file's history, cues summed (not filtered) | **PINNED** (Anderson & Schooler; Lewis & Vasishth) |
| the ANTECEDENT is the mention that supplied the evidence (a span) | **PINNED** (object-file reviewing: the token is re-presented at a location) |
| Principle B / Principle A over clause-mate CO-ARGUMENTS | **PINNED** (categorical universals) |
| impletion: a resolved pronoun is written into the file's history | **PINNED** (Kahneman-Treisman-Gibbs; ACT-R presentation) |
| the discrete record, the tie rule, the accessibility window, the exact cue weights | **OUR-INVENTION** (swept, never adopted) |
| scoring outcomes (nullable, per-item scoreability, the four counts) | **NOT a brain claim at all** -- it is instrumentation, and it belongs OUTSIDE the inference result |

**The consequence that IS the fix:** if the answer is a head STRING, then (a) two files the reader opened
separately cannot be told apart by any consumer, (b) the mention that supplied the evidence is gone, so the
scorer can only ask "does this head name the right entity ANYWHERE in the document", and (c) the pick cannot
express Principle B, because the exclusion is on the co-argument's FILE. All three of the deep review's
findings on this rung (D02, D05, D06) are the same missing object: **the discourse entity**.

## 1. THE DEFECT, REPRODUCED FIRST-HAND

Every claim below is from the LIVE `SituationReader().read()` on constructed text, in the cell's `--self-test`
(14/14), with the shipped organ and the proposed organ **in one process**:

| the review's finding | reproduced here | witness |
|---|---|---|
| D05: the pick keys candidates by `m["head"].lower()` | the shipped organ answers with a head string and NO entity: `resolved_entity=None`, `resolved_cluster=None` | W1b |
| D02: `-1` is both the sentinel and the first live entity | the reader's live entity ids on a 4-sentence passage are `[-9,-8,-7,-6,...]` -- **`-1` is a valid file**, and after strategy's landing guard the graded record carries `None` | W3 |
| D02: `goal_register.make_canonicalizer` reads `names.get(r.resolved_cluster)` | the shipped organ canonicalises **nothing** through a pronoun (the guard made the collision safe by making the link empty) | W8b |
| D02: `_read_world_state` keeps only `rc >= 0` | with the shipped organ the possession fact is **lost entirely** (no holder recorded at all), because the negative online id is dropped and the binder then has nothing to bind | W9 |
| D06.1: `coref_acc` is 0 where there is no answer key | the shipped organ reports `coref_acc = 0.0` on annotation-free text | W4b |
| D06.2: the comparator is the main result | the branch returned `(out, side, side)`; the executed single-sentence comparator **disagrees** on the same questions | W6 |
| D06.3: head membership credits a wrong same-head antecedent | the shipped scorer's head map hits and marks `correct=True` for a pick on the OTHER doctor | W5b |

## 2. WHAT I BUILT (the diff, four rungs)

1. **The identity contract** (`hdlab/coref.py`): `entity_key(m)` = the reader's own online file id
   (`m["cluster"]`, written by `entity_resolver.cluster` as `-(file+1)`); the pick's history, feature card,
   Centering focus and impletion are all keyed by it; `mention_span(m)` gives the antecedent span. The record
   is now `{resolved_entity, resolved_head, antecedent_span, candidates, abstain_reason, ...}` -- and
   `resolved_entity is None` is the unresolved value, so no valid id is ever a sentinel.
2. **ONE question, ONE outcome** (`discovered_pronoun_targets`): every third-person pronoun is scheduled (the
   retrieval demand exists whether or not a compatible referent is accessible); the pick returns exactly one
   record per question with an explicit `abstain_reason` (`no_candidate` / `no_compatible` / `tie`). So
   `discovered == attempted + abstained`, and a consumer can align to the reader's list by index -- which is
   what the pri 122 board row needs.
3. **Principle B from the reader's OWN parse** (`_coargument_positions`): the other dependents of the same
   governing VERB/AUX, from the shared per-read parse (a cache HIT; no new parse), banning the co-argument's
   FILE. pri 125 built a RANK proxy ("any other core-ranked mention in the sentence"), measured it at
   **-0.104** and refuted it; this is the relation itself, and it is only expressible because the candidates
   are now files.
4. **Scoring outside the inference result** (`hdlab/situation_reader.py`): scoreability decided in BOTH
   branches and reset per read; alignment by the ANTECEDENT SPAN's gold entity rather than document-wide head
   membership; the single-sentence comparator EXECUTED (same organ, file store cleared at each sentence
   boundary); the four counts published (`n_pronouns_discovered / n_coref_attempted / n_coref_abstained /
   n_coref_scoreable`), `coref_acc` keeping its fixed denominator and the conditional-on-attempted rate
   published separately as `coref_attempted_acc`.
   Consumers updated in the same diff: `goal_register.make_canonicalizer` reads `resolved_entity`, and
   `_read_world_state` decides validity by **membership in the read's own entity set**, not by sign.

## 9. ALTERNATE PATHS -- equally or MORE brain-foundational than what I shipped

1. **Make the FILE the unit of introduction, not the mention.** Structure: DRT/FCS file cards built
   incrementally; maths: the introduction organ would emit a file id per NP directly (it currently emits a
   mention and a separate organ clusters them afterwards, so the identity the pick needs is computed twice
   and can disagree). What it would take: `referent_per_np` returning `(mention, file)` with the online
   resolver INSIDE the introduction loop. Why not now: it changes the mention schema every organ reads.
   **More brain-foundational than what I shipped** -- introduction and identification are one act.
2. **Kehler-Rohde as the pick's decision rule** (`P(r | pron) ∝ P(r next-mentioned) · P(pron | r)`; PINNED,
   BRAIN_MATH_REFERENCE §A): my pick is the activation half only. The prior alone saturates ~0.45 and the
   grammar likelihood added +0.093 in `affected_entity_resolver`. What it would take: a next-mention prior
   over FILES (now expressible, because files exist). Why not now: a separate organ's arm, and it needs the
   identity contract first -- which is this brief.
3. **ONE retrieval organ for every anaphor** (the consolidation audit's principle): `EntityTokens` in
   `affected_entity_resolver` already holds ACT-R activation + Centering prominence + Principle A/B +
   impletion; the reader's pick is a second implementation of the same structure. With the identity contract
   landed, the two now agree on what a candidate IS, which is the precondition for merging them. Why not now:
   the merge is a bigger consolidation than this brief's three files.
4. **Score coreference the way the brain's competence is measured: by the CHAIN, not by the pick.** A B-CUBED
   or CEAF over the reader's own files against gold chains measures the identity the reader actually built,
   where the fixed-question instrument measures only the pronoun decisions. Cheap, and it would make the
   clustering's contribution visible without an oracle.

## 10. ADJACENT COMPONENTS (capability / limitation / opportunity / BF status)

| component | status for THIS signal | opportunity |
|---|---|---|
| `entity_resolver.cluster` + `crosstype_live_adapter` (the online files) | **now LOAD-BEARING** for the pick, where it was inert before | its purity is the pick's ceiling (§6) -- the single highest-value upstream target on this rung |
| `referent_per_np` file card (pri 125) | BF, filled at introduction | span-level mentions (it stores `span_toks=[head]`) would give the scorer and the aliaser more to work with |
| `goal_register.make_canonicalizer` | now reads the entity; **but its API is `canon(surface, sent_idx)`** -- two `him` in one sentence with different antecedents collapse to the first | the API needs the token position; the records already carry it (D02 acceptance case 3) |
| `_read_belief` | **receives an EMPTY mention map** (`situation_reader.py:2869`, `by_sent = {i: [] ...}`) -- no reference identity reaches belief AT ALL | that is deep-review D04, filed as pri 132; outside my three files |
| `_read_causal_reasoning` | normalises every event endpoint to its rightmost word (D07) -- the same class of defect as D05, one layer over | pri 132 |
| `world_state_register` op lookup | `lex.get(e.predicate)` uses the SURFACE form, so `took`/`takes` find no operator while `take` does (observed here) | a lemma lookup would make the possession register fire on inflected verbs -- a small, separable fix |
