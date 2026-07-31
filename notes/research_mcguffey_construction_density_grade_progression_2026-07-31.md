# McGuffey graded curriculum: construction-density vs vocabulary grading (g1-g6)

Date: 2026-07-31
Author: research (director-dispatched fairness/genuine-signal check)
Corpus: `data/corpora/mcguffey_graded/clean/g1.txt .. g6.txt`
Raw numbers: `notes/mcguffey_construction_density_raw.json`
Measurement script: scratchpad `mcguffey_construction_density2.py`

## Question
Is McGuffey genuinely CONSTRUCTION-graded (new SENTENCE STRUCTURES introduced in a
developmental order), or only VOCABULARY-graded? The multi-competency reading build
assumes "reading a graded curriculum drives encountering NEW construction types grade
by grade"; that premise fails if the grades only get harder words. This is a
genuine-signal check on the real corpus: is there real new structure to discover at
each level?

## Method (which tools, and the honesty caveat)
Used the PROJECT'S OWN trained glass-box reader-parser assets, not a hand-rolled parser
and not an external NLP library (spaCy is not installed here anyway):
- `hdlab.pos_tagger.PosTagger` <- checkpoint `data/frontend_assets/pos_tagger_ud_ewt_upos.json`
- `hdlab.arc_parser.ArcParser`  <- checkpoint `data/frontend_assets/arc_parser_hashed_ud_ewt.npz`

Both are UD-English-EWT-trained averaged-perceptron models already shipped in
`frontend_assets/`. Every sentence was POS-tagged and dependency-parsed; construction
types were then detected from POS tags + the parser's predicted (UNLABELED) arc tree
via documented structural proxies.

INSTRUMENT CAVEATS (deflated read — trust the TRENDS/ordinality, not the absolute %):
- A third checkpoint `arc_labeler_hashed_ud_ewt.json` (full UD deprel set incl.
  `nsubj:pass`, `acl:relcl`, `ccomp`, `advcl`, `mark`) exists but has NO discoverable
  decode/consumer code anywhere in the repo. Reverse-engineering its hashed-feature
  decode risked silently-wrong labels, so I did NOT use gold deprel labels. Detection is
  therefore proxy-based, coarser than a labeled parse.
- `pct_complement_or_adv_clause` = "a VERB whose head is a VERB" — this OVER-counts
  (folds in infinitival xcomp, adverbial clauses, and true ccomp together). Treat as a
  loose "any embedded predicate" signal, not a clean complement-clause rate.
- `pct_coordinate_clause` (CCONJ attached to a VERB) partially over-counts NP/VP
  coordination. `pct_relative_clause` requires a non-initial relativizer whose head verb
  attaches to a noun — reasonably precise but can miss reduced/participial relatives.
- `pct_passive` (BE-AUX + head past-participle) is the most reliable proxy.
- Pronoun density and chain runs are just counts — robust.
- Clause-chain-depth = longest verb->verb head chain — an ordinal complexity proxy, not
  true syntactic depth.

## Per-grade construction-density table

| Metric | g1 | g2 | g3 | g4 | g5 | g6 |
|---|---|---|---|---|---|---|
| n_sentences | 393 | 760 | 328 | 2157 | 3252 | 4382 |
| mean sent length (words) | 11.7 | 16.1 | 22.5 | 23.6 | 23.5 | 24.6 |
| p90 sent length | 21 | 28 | 42 | 43 | 46 | 48 |
| mean clause-chain depth | 1.66 | 1.90 | 2.29 | 2.25 | 2.09 | 1.97 |
| p90 clause-chain depth | 3 | 3 | 4 | 4 | 4 | 4 |
| % passive | 3.3 | 8.0 | 9.8 | **21.7** | 22.2 | 23.7 |
| % relative clause | 3.6 | 11.4 | **23.8** | 24.7 | 22.4 | 21.6 |
| % coordinate clause | 23.9 | 35.1 | 40.9 | 45.6 | 40.3 | 40.8 |
| % embedded-predicate (compl/adv/xcomp, loose) | 42.2 | 55.5 | 65.2 | 65.4 | 59.0 | 55.6 |
| % negation | 16.5 | 22.0 | 27.7 | 24.6 | 22.0 | 21.2 |
| % conditional | 2.5 | 4.7 | 7.6 | 7.6 | 6.1 | 4.7 |
| % question | 17.3 | 6.1 | 11.9 | 7.9 | 8.0 | 6.4 |
| pronouns / 100 words (coref load) | **13.5** | 11.8 | 10.7 | 9.8 | 8.6 | 7.9 |
| n pronoun chains | 86 | 145 | 55 | 405 | 622 | 814 |
| mean pronoun-chain run len | 2.26 | 3.12 | 3.29 | 3.15 | 2.90 | 3.00 |
| max pronoun-chain run len | 15 | 25 | 15 | 27 | 31 | 37 |

## VERDICT (honest, deflated)

**McGuffey is genuinely construction-graded over g1->g4, then SATURATES (mostly
vocabulary/length-graded) over g4->g6.** It is a PARTIAL yes, not a clean yes.

- The lower half (g1->g4) shows a real, ordered ramp of NEW construction types at
  increasing density — this is genuine structural signal a discovery trigger can fire on.
- The upper half (g4->g6) adds almost no new construction density. Every structural
  metric is flat or DECLINING from g4 to g6 (passive 21.7->23.7, relative 24.7->21.6,
  embedded-predicate 65->56, clause depth 2.25->1.97, conditional 7.6->4.7). The g4->g6
  jump is dominated by MORE TEXT (2157->4382 sentences), marginally longer sentences
  (23.6->24.6), and harder vocabulary (the already-confirmed FK ramp) — NOT new syntax.

### Does the introduction order match the acquisition ladder?
Target ladder: entity -> thematic roles -> cross-sentence COREFERENCE -> non-canonical
order (passive, object-relative) -> complement clauses -> conditionals -> multi-sentence
situation model.

Partially, with two notable mismatches:
- **Passive ramps latest and cleanest** (3.3% g1 -> ~22-24% g4-g6, big jump at g4). This
  MATCHES the ladder (non-canonical role order is a later competency) and matches the
  measured Broca's-like encoder wall expectation (low in g1, rising later). Good.
- **Relative clauses ramp g2->g3** (3.6 -> 11.4 -> 23.8%), sitting just before the passive
  jump. Consistent with the ladder's "non-canonical order" band.
- **MISMATCH #1 — coreference is FRONT-LOADED, not ramping.** Pronoun density is HIGHEST
  in g1 (13.5/100w) and DECLINES monotonically to 7.9 by g6. The ladder wants coreference
  (competency #3) to RAMP; McGuffey does the opposite. Higher grades shift to a more
  nominal style (named entities, fewer pronouns). Mean chain-run length is roughly flat
  (~3) across g2-g6. So per-text coreference LOAD does not increase with grade.
- **MISMATCH #2 — no clean complement-clause / conditional gradient at the top.**
  Conditionals peak at g3 (7.6%) then decline to g4->g6. The loose embedded-predicate
  rate peaks at g3-g4 then declines. Nothing in the upper grades ramps these.

### Per-grade genuinely-NEW construction (something for a trigger to fire on)
- **g1**: baseline — simple SVO, high question density (17%, interactive primer style),
  high pronoun/coref density, light coordination. (This is the "entity + coreference"
  floor, already densest here.)
- **g2**: NEW — relative clauses reach meaningful density (3.6->11.4%); passive doubles
  (3.3->8.0%); subordination/embedding up. YES, new type.
- **g3**: NEW — dense relative clauses (23.8%, ~2x g2) + conditional density peaks (7.6%)
  + clause-chain depth peaks (2.29). YES, new density regime.
- **g4**: NEW — passive JUMPS to high density (9.8->21.7%). This is the single clearest
  new-construction event and aligns with the passive/Broca's target. YES, new type.
- **g5**: NO genuinely-new construction vs g4. Plateau; every structural metric flat or
  down. Adds volume + vocabulary only.
- **g6**: NO genuinely-new construction vs g4/g5. Plateau; marginally longer sentences,
  harder words. No new structural trigger.

So 4 of 6 grades (g1 floor, g2, g3, g4) each introduce a genuinely-new construction
regime; **g5 and g6 do not.** The construction axis effectively tops out at g4.

## Construction types NOT well-covered by McGuffey for competency #3+
1. **A RISING coreference gradient (competency #3) is absent — this is the biggest gap.**
   Pronoun density and per-text coref load do not increase with grade; if anything g1 is
   the coref-densest. McGuffey will NOT drive a "coreference gets harder grade by grade"
   curriculum on its own. Longer entity chains do appear (max run 15->37) but only because
   the texts get longer, not because reference is made structurally harder.
2. **Complement clauses (ccomp) as a distinct, ramping competency** — the corpus has
   embedded predicates throughout but no clean increasing complement-clause gradient, and
   the current instrument cannot cleanly separate ccomp from xcomp/advcl anyway.
3. **Conditionals** peak at g3 and thin out — no upper-grade ramp.
4. **Object-relative / non-canonical relative order** specifically (vs subject-relative)
   is not separable with the unlabeled parse; density of relatives overall plateaus after
   g3, so a specific object-relative ramp is unlikely to be present.

## Recommendation
- **Use McGuffey g1->g4 as the genuine construction ramp** for the lower ladder
  (entity floor -> relative clauses -> passive). It carries real, ordered new-structure
  signal there and its passive gradient is a good match for the encoder wall target.
- **Do NOT rely on g5/g6 for new construction triggers** — they are vocabulary/length
  extensions of g4's structure. Feeding them expecting new construction types to appear
  would produce a flat learning signal for a structural reason (the content genuinely
  lacks new structure), which per the "flat = broken experiment" discipline would need
  diagnosing — so pre-empt it: the flatness at the top is a CORPUS property, expected.
- **Supplement the coreference axis (competency #3) explicitly.** Because McGuffey's coref
  load falls with grade, inject or splice a corpus/probe set where cross-sentence
  reference is made progressively harder (more competing same-gender entities, longer
  antecedent distance) — the coref machinery already exists (`hdlab/coref.py`,
  LitBank pipeline) and is a natural source of a genuine coref gradient.
- **For upper competencies (complement clauses, conditionals, non-canonical relatives),**
  either inject construction-typed material (the `tools/build_construction_gold.py`
  construction-balanced selection is exactly this kind of generator over UD-EWT) or add a
  second graded corpus chosen for a syntactic (not lexical) gradient. McGuffey alone
  saturates the construction axis at ~g4.

## Bottom line
McGuffey is construction-graded where it matters most for the near-term build (g1->g4
gives entity -> relative -> passive with a clean passive ramp), but its top two grades
are vocabulary-graded only, and it provides NO rising coreference gradient. Treat g1-g4
as the construction curriculum, and supply competency #3 (coreference) and the upper
constructions from a dedicated construction-typed source rather than expecting McGuffey's
higher grades to deliver them.
