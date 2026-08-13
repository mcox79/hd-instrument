# Sensorimotor anchoring — scope / coverage decision (2026-08-13)

READ-ONLY analysis. No code modified, nothing committed. All numbers computed off disk with
`.venv/Scripts/python.exe` against:

- `data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv` (39,707 rows loaded)
- `data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt` (39,954 rows loaded)
- `data/exp_grounding_quality_readout_v1/blind_sample.json` + `_joined_verdicts.json` (100 rows, verdicts ON DISK)
- `data/exp_grounding_text_vs_mechanism/blind_sample.json` + `arm_key.json` (100 rows, Director verdicts supplied in task)
- `data/foundation/reading_grounding_v1/store/store_facts.json` (7,966 facts)

Matching is exact lowercase string match on the surface token as stored. Deflation note: every number
below is a **coverage measurement**, which is a fact; every interpretation of it is a **hypothesis**.

---

## 1. Coverage tables (these decide it)

### 1a. Blind-sample subjects

| set | n | in Lancaster | in Brysbaert | in EITHER |
|---|---|---|---|---|
| readout_v1 subjects | 100 | 0.630 | 0.640 | **0.640** |
| text_vs_mechanism subjects | 100 | 0.700 | 0.700 | **0.700** |
| readout_v1 objects | 100 | 0.880 | 0.880 | 0.880 |
| text_vs_mechanism objects | 100 | 0.940 | 0.940 | 0.940 |
| readout_v1 PAIR (subj AND obj) | 100 | 0.570 | — | 0.570 |
| text_vs_mech PAIR (subj AND obj) | 100 | 0.670 | — | 0.670 |

All 100 subjects were unique in each sample, so token- and type-level coverage coincide.
**Lancaster and Brysbaert are near-perfectly nested** — "either" is essentially never larger than
each alone. Owning both buys nothing over owning one.

### 1b. Banked store (`GROUNDED_MEANING`, subject != object)

Verified counts: 3,544 `GROUNDED_MEANING` facts; 2,328 tautological (65.7%, matches the prior
finding); **1,216 non-tautological**.

| set | n | Lancaster | Brysbaert | EITHER |
|---|---|---|---|---|
| non-taut subjects | 1216 | 0.612 | 0.613 | **0.613** |
| non-taut objects | 1216 | 0.656 | 0.657 | 0.657 |
| non-taut PAIR both covered | 1216 | 0.445 | — | **0.445** |
| tautological subjects (contrast) | 2328 | 0.616 | 0.617 | 0.617 |

Tautological and non-tautological subjects have identical coverage — the norms cannot distinguish
the plumbing-only rows from the real ones.

### 1c. **Coverage broken down by verdict — the decisive cut**

`text_vs_mechanism` (Director verdicts; MEANINGFUL {045,096}, RELATED 25 rows, NOISE = other 73):

| verdict | n | Lancaster | Brysbaert | EITHER |
|---|---|---|---|---|
| MEANINGFUL | 2 | 0.000 | 0.000 | **0.000** |
| RELATED | 25 | 0.640 | 0.640 | 0.640 |
| **NOISE** | **73** | **0.740** | **0.740** | **0.740** |

`readout_v1` (verdicts read from `_joined_verdicts.json`: 78 NOISE / 19 RELATED / 3 MEANINGFUL):

| verdict | n | Lancaster | Brysbaert | EITHER |
|---|---|---|---|---|
| MEANINGFUL | 3 | 0.333 | 0.333 | 0.333 |
| RELATED | 19 | 0.632 | 0.684 | 0.684 |
| **NOISE** | **78** | **0.641** | **0.641** | **0.641** |

**Answer to the framing question: NO, the failure words are NOT the uncovered ones.** In both
samples the NOISE rows are covered at least as well as (text_vs_mech: better than) the non-NOISE
rows. 64–74% of the rows we fail on have norms sitting on disk right now. Coverage is therefore
**not** the binding constraint — but note the inverse implication in §1e.

### 1d. Technical/biology vs news vocabulary

`text_vs_mechanism` splits cleanly by arm (`arm_key.json`): TEXTBOOK = biology/technical,
NEWS = news.

| arm | subset | n | EITHER |
|---|---|---|---|
| TEXTBOOK | all | 50 | 0.660 |
| TEXTBOOK | NOISE | 35 | 0.714 |
| TEXTBOOK | RELATED | 15 | 0.533 |
| NEWS | all | 50 | 0.740 |
| NEWS | NOISE | 38 | 0.763 |
| NEWS | RELATED | 10 | 0.800 |

`readout_v1` splits by segment:

| segment | n | EITHER |
|---|---|---|
| adv_new | 42 | 0.643 |
| **bio_new** | **17** | **0.471** |
| ele_cont | 18 | 0.722 |
| int_cont | 21 | 0.667 |
| bootstrap | 2 | 1.000 |

Biology vocabulary is the worst-covered slice (0.47 in `bio_new`, 0.53 for TEXTBOOK-RELATED), as
predicted. Uncovered technical terms observed: `aphotic, glucagon, sertoli, bronchiole, erythrocyte,
eukaryote, operon, vesicle, synapsis, trypanosomiasis, intramembranous, pronation` and, in the store,
`allele, centromere, chromatid, covalent, cytosine, deoxyribose, denaturation, codominance,
channelrhodopsin`.

### 1e. What the uncovered residue actually is

Decomposition of uncovered subjects (readout_v1 NOISE, n=28 uncovered):
**21/28 (75%) are proper nouns** by a capitalized-mid-sentence heuristic over the row's own
`source_sentences`: `baffin, tesco, abdullah, blatter, mowat, ingabire, morris, colin, cathy, lewis,
luke, hayatou, justin, bergsland, tim, ifpi, tonagawa, cerf, pizzi, des, sertoli`. The rest are
technical terms (`aphotic, glucagon, meritocratic, injera, abrs, spots`).

Store residue is different and worse. Of the 1,216 non-tautological store subjects:

| bucket | n | share |
|---|---|---|
| exact match in a norm set | 745 | 0.613 |
| recovered by *adding back* a stripped letter ("unstem") | 126 | **0.104** |
| recovered by lemma backoff | 1 | 0.001 |
| genuinely uncovered | 344 | 0.283 |

Examples of the 126: `billionair, clos, indigenou, tortur, chimpanze, statu, igneou, bubbl, plat,
dissolv, retir, dres, staphylococcu, morri, parachut, desmosom`. **~10% of the store's subject
vocabulary is over-stemmed corruption, not vocabulary gap** — the same class of defect as the v5
term-boundary fix. That is a bug finding independent of the norms question. Blind samples do NOT
show this at scale (1/78 and 0/73), so the corruption is in the banked store, not the recent
extraction path.

The genuine 28.3% residue is proper nouns + technical/biology terms — exactly the two classes no
lexical norm table will ever cover, because Lancaster/Brysbaert rate *general English words*.

### 1f. Does the signal actually separate good rows from noise? (extra probe)

Coverage says the norms *reach* the failure rows. That does not say they *discriminate*. Testing on
the 124 of 200 blind rows where subject AND object are both in Lancaster, using the 11-dim modality
mean vector:

| group | n | mean cosine | median |
|---|---|---|---|
| MEANINGFUL+RELATED | 27 | **0.8834** | 0.9152 |
| NOISE | 97 | 0.8071 | 0.8372 |
| **random word pairs (floor)** | 2000 | **0.8060** | 0.8321 |

Difference good−noise = +0.076, one-sided permutation p = 0.0012 (20k shuffles).
|concreteness difference| also separates: good 0.81 vs noise 1.15, p = 0.032.

**The single most interesting number here: the NOISE rows sit exactly on the random-pair floor
(0.8071 vs 0.8060).** Hypothesis (not finding): the substrate's noise output is, on the sensorimotor
axis, indistinguishable from picking a random English word — while its non-noise output is
measurably above that floor.

Usability is much weaker than that framing suggests:
AUC = 0.685 (n=27 vs 97). At threshold cos>=0.90: precision 0.400, recall 0.593, from a base rate of
0.218. So it is a **weak soft filter**, not a selector — and it only applies to the 62% of pairs it
covers.

---

## 2. (§5) Where the glass-box line falls

- **PERMITTED — norms as DATA.** Loading a rating table is the same kind of act as ingesting a
  corpus: it supplies facts the system did not have. A Lancaster row is a claim about a word
  ("*apple* scores 4.2 visual, 3.9 gustatory") in the same sense a textbook sentence is.
- **FORBIDDEN — norms as the reasoning organ.** The line is crossed the moment an *inference* is
  performed by table arithmetic that the substrate cannot itself explain. Concretely, forbidden:
  (a) ranking candidate objects by norm-vector cosine and calling the winner the meaning
  (that is a similarity proxy standing where reasoning should be — the exact failure mode the
  brain-fidelity audit names); (b) scoring/grading substrate output with the same table used to
  produce it; (c) any path where removing the table removes the *reasoning*, not just the *facts*.
- **The operational test:** after ingestion, can the substrate state, in its own representation, why
  it made a given binding — with the norm value appearing as a cited premise rather than as an
  opaque scoring function? If the answer requires re-reading the CSV at inference time to
  *rank*, it has become the organ.
- **Second-order risk:** the norms are human introspective ratings. Using them as ground truth for
  grading grounding quality is a ground-by-X/grade-by-X violation if they are also the input.

## 3. (§6) Honest read — is this a real sensory anchor?

**Mostly no; partly yes, and the partly-yes is narrower than it looks.**

Against: a Lancaster row is not perception. It is 3,000 undergraduates' *verbal introspection about*
perception, encoded as 11 numbers, distributed as a text file. It has none of the properties that
make sensory grounding load-bearing — no time course, no modality-specific failure, no ability to
generate a novel prediction about an unseen object, no compositionality (there is no norm row for
"red apple on the left"). Substituting cosine-over-11-norm-dims for cosine-over-HD-context is
swapping one similarity proxy for another; per the standing discipline, a similarity proxy standing
where the brain reasons is an architecture defect, not a fix.

For: it is *externally sourced* and *not derived from our corpus*, so it is genuinely independent of
the text-only circularity — which is why the random-floor result in §1f is not trivially
self-confirming. A signal that is uncorrelated with our failure mode is worth more than a stronger
signal that is correlated with it.

Net: this is worth **one bounded probe as a rejection filter**, not a program. It cannot be the
grounding story. The claim "we grounded meaning in sensorimotor experience" would be false if what
happened is "we joined against a ratings CSV" — and I would expect that overclaim to be made if this
lands, so it should be pre-empted in the pre-registration.

## 4. (§7) Candidate mechanisms with can-fail discriminators

**M1 — Noise rejection gate (n=50 hand-scored; cheapest, testable now).**
Refuse to bank a `GROUNDED_MEANING` fact when subject/object Lancaster cosine is at or below the
random-pair floor and both words are covered.
*Discriminator:* draw 50 rows the gate would REJECT and 50 it would KEEP, blind-score them. FAIL if
the kept set's MEANINGFUL+RELATED rate is not at least 2x the rejected set's, or if the gate keeps
<20% of rows (uselessly strict). Predicted by §1f at ~0.40 vs ~0.10 — but that estimate is derived
from the same 124 rows, so it is an in-sample projection and MUST be tested out-of-sample.
*Kills itself if:* the effect is carried by concreteness alone (add a concreteness-only arm — if
concreteness-only matches the 11-dim arm, the "sensorimotor" framing is unearned and this is just a
concreteness filter).

**M2 — Modality-typed relation constraint (structural, not similarity).**
Use the *dominant modality* label, not the vector, as a type: a word whose dominant perceptual
channel is Visual should not be bound to an object whose dominant channel is Interoceptive without
an explicit licensing pattern. This uses the norms as discrete FACTS in a symbolic constraint, not
as a metric — keeping it on the permitted side of §2.
*Discriminator:* the constraint must reject a hand-built set of 20 known-bad pairs AND accept 20
known-good pairs from the existing verdicts, at >=0.70 on both, without a tuned threshold. FAIL if
it needs a continuous cutoff to work — that would mean it is M1 in disguise.

**M3 — Anchor-set restriction for the frontier metric (serves GAP==GROUNDING).**
Define the "grounded frontier" as the covered, high-concreteness subset only, and score new concepts
by shortest relational distance to THAT set rather than to any prior fact. This is a change to the
*evaluation* and to *what-to-read-next*, not to the read-out.
*Discriminator:* if the metric is real, concepts at distance 1 from the anchor set must hand-score
MEANINGFUL at a materially higher rate than concepts at distance >=3. FAIL if the distance
distribution is degenerate (>80% of concepts at one distance) or if hand-score rate is flat across
distance — flat here means the metric is not measuring what it claims, which per standing discipline
is a broken experiment, not a ceiling.

At n=50 hand-scored: **M1** is the one that fits, and it is the honest first cut because it is the
one that can most cleanly fail.

## 5. (§8) Strongest argument against doing this at all

**"You are proposing to filter a read-out that produces 2–3% MEANINGFUL. A filter cannot create
meaning it does not receive. Even a perfect filter over this read-out yields a smaller pile of the
same 2–3%, while producing the appearance of improvement — precision goes up, the mechanism does not.
Meanwhile the norms cover the failure rows at 64–74%, so 'we lacked the anchor' was never the
explanation for those failures; the mechanism failed on words it had every chance to get right.
Building here treats a symptom with a lookup table, and it is the easy path selected over the hard
blocking thing — the read-out/representation itself."**

**Does it defeat the proposal? Largely yes, in its strong form.** As a route to *quality* it is
defeated: coverage data shows the anchor was not the missing ingredient for the words we fail on.
M1's precision gain would be a selection effect on a broken generator and should not be reported as
a grounding improvement.

It does not defeat two narrow residual uses:
1. **As a diagnostic, not a fix.** The §1f random-floor result is an independent, non-circular
   measurement of *how* the read-out fails (its output is sensorimotor-random). That is cheap
   evidence about the mechanism and is worth having regardless of whether any filter ships.
2. **As bounded data supply for the 28% genuinely-uncovered technical vocabulary** — where the answer
   is not norms at all but denser explicit source text, per the don't-generalize-a-narrow-failure
   discipline.

Recommendation (hypothesis, pending VET): **do NOT open a sensorimotor-anchoring program.** Run M1
once as a can-fail *diagnostic* at n=50, with a concreteness-only control arm, explicitly
pre-registered as "does the substrate's noise output sit at the random lexical floor" and NOT as a
quality fix. Separately and independently, file the ~10% store over-stemming corruption (§1e) — that
is a real defect found in passing and it inflates every "uncovered vocabulary" number anyone
computes off the banked store.

---

## 6. What I could NOT verify

- **Whether the §1f separation is causal or an artifact.** Covered words skew common and concrete;
  RELATED rows may simply contain more concrete-concrete pairs. I did not run a
  frequency/concreteness-matched control. The concreteness-only result (p=0.032) is itself evidence
  that at least part of the 11-dim effect is plain concreteness. **The AUC 0.685 and the
  precision/recall numbers are IN-SAMPLE on the 124 rows used to pick the threshold; they are
  projections, not held-out results.**
- **MEANINGFUL-row coverage is statistically meaningless.** n=2 and n=3. The "0.000 coverage for
  MEANINGFUL" cell is a curiosity, not a finding, and must not be cited as "the successes come from
  uncovered words".
- **The `text_vs_mechanism` verdict indices were supplied in the task, not re-derived.** I mapped
  index 1..100 to row order in `blind_sample.json` (`rows[i-1]`), which matches the `blind_id`
  ordering in `arm_key.json`. If the Director's numbering was 0-based, every verdict-conditioned
  cell in §1c/§1d is shifted by one. The `readout_v1` cut uses on-disk `_joined_verdicts.json` and
  does not have this exposure — and it agrees directionally, which is the main reassurance.
- **Morphology.** Matching is exact-token. Naive lemma backoff added only +0.013 to blind-sample
  coverage, so the exact-match numbers are close to a proper lemmatized ceiling; the "unstem" bucket
  in §1e used a crude add-a-letter heuristic and may include a few false recoveries.
- **Proper-noun share of the store's 344 uncovered subjects** was not computed — the 75% figure is
  from the readout_v1 blind sample only, where `source_sentences` were available. Store facts were
  not joined to their source text.
- **I did not check whether any hdlab module already implements a norm-based gate.** Prior work
  established only `grounded_similarity.py:82-85` (loader) and `lexical_similarity.py:60-64,615`
  (consumer); I did not re-derive the import graph and did not read the concurrently-owned files.
- **No claim about whether M1 would survive the full control stack** (scramble / prior-lesion /
  ablation / no-leak / attribution). It has not been run.

---

# DECISION (Director, 2026-08-13) — SHELVED

**SHELVED — sensorimotor anchoring of the meaning read-out.**

**Reason.** Coverage is NOT the blocker: the norms cover the NOISE rows at 0.740 (text_vs_mechanism)
and 0.641 (readout_v1), slightly BETTER than the non-NOISE rows (0.640). The lever is therefore
reachable — and it is still the wrong lever. **A filter cannot create meaning that a 2–3% MEANINGFUL
generator never produced.** It buys apparent precision on a broken generator and diverts effort from
the read-out itself, which is the actual defect. This is the scoping agent's own strongest
counter-argument (§5 above) and the Director accepts it in its strong form.

**Retained as evidence (do not re-derive).** On the 124 both-covered blind pairs, NOISE sits on the
random-word-pair Lancaster floor (0.8071 vs 0.8060) while non-NOISE sits at 0.8834 (one-sided
permutation p = 0.0012, 20k shuffles). AUC = 0.685; the AUC and the precision/recall figures are
IN-SAMPLE — the threshold was picked on the same 124 rows. This is a diagnostic about *how* the
read-out fails (its output is sensorimotor-random), not a quality result.

**REVIVAL CRITERIA.** Revisit only if either holds:
(a) **A read-out is achieved that produces a materially higher MEANINGFUL rate.** At that point a
rejection gate on a *working* generator becomes worthwhile, because precision gained on a generator
that produces meaning is a real gain rather than a selection effect. Until then, any precision gain
here is an artifact of subsetting a broken output.
(b) **Sensorimotor grounding is needed as a *generative* anchor rather than a filter** — with a
mechanism that *proposes* candidate bindings rather than *scoring* pre-existing ones. A proposing
mechanism is a different object from M1/M2/M3 above and would need its own brain-fidelity siting
(shape + position + metric), not a threshold.

**Also recorded, so nobody re-measures it.**
- **Lancaster and Brysbaert are near-perfectly nested.** "EITHER" is essentially never larger than
  either alone (0.630/0.640/0.640; 0.612/0.613/0.613). Owning the second file adds ~nothing; do not
  acquire or wire a third norm table expecting union gains.
- **The uncovered residue is ~75% proper nouns plus technical terms** (readout_v1 NOISE, 21/28 by the
  capitalized-mid-sentence heuristic), i.e. exactly the two classes **no lexical norm table will ever
  cover**, because Lancaster/Brysbaert rate general English words. More norms is not a route to the
  residue; denser explicit source text is the only route named.

**Spun out, NOT shelved:** the ~10% over-stemming corruption in the banked store (§1e) is a real
independent defect and is carried forward in `notes/stemmer_corruption_2026-08-13.md`.
