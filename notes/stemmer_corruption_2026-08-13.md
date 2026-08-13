# Over-stemming corruption in the banked foundation store (2026-08-13)

READ-ONLY investigation. No code changed, nothing committed, **no fix applied** (a fix is a
separate one-variable change). Spun out of `notes/sensorimotor_anchoring_scope_2026-08-13.md` §1e,
which observed ~10% over-stemmed store subjects in passing.

All numbers computed off disk with `.venv/Scripts/python.exe` against:
- `data/foundation/reading_grounding_v1/store/store_facts.json` (7,966 rows, mtime 2026-08-12T13:46:28Z)
- `data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv` (39,707 words)
- `data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt` (39,954 words; union = 39,956)
- WordNet via `nltk.corpus.wordnet` (already vendored; `morphy` + `all_lemma_names`)

---

## VERDICT UP FRONT

**FIXED — the bug is NOT in today's code. The banked store came from an older version.**

`hdlab/thematic_role_labeler.py:235` `lemma_word` — the function on the live reading path — returns
the CORRECT form for every one of the nine test words. The corrupted store tokens are reproduced
*exactly* by `hdlab/thematic_role_labeler.py:301` `lemma_verb`, the old suffix-stripper the reading
path used **before** commit `01093ac1f` (2026-08-12 14:19:43 -0400). The store was written at
2026-08-12 09:46 EDT — **4h33m BEFORE the fix landed**.

So: the corruption is real, it is ~10% of the store's subject vocabulary, and it is **historical
debt in the banked artifact**, not a live defect on the reading path.

---

## 1. Quantification off disk

### Detection rule (checkable, not vibes)

A stored token `t` is counted OVER-STEMMED iff **all three** hold:

1. `t.isalpha()` and `len(t) >= 3`;
2. `t` is **NOT** in DICT, where `DICT = Lancaster ∪ Brysbaert ∪ {w : wordnet.morphy(w) is not None}`
   (157,526 surface forms when WordNet lemma names are included; 39,956 from the norms alone);
3. there exists a single letter `c ∈ [a-z]` such that `t + c` **IS** in DICT.

I.e. *not a word, but one appended letter away from being one* — the exact signature of a stripped
final character. This is deliberately conservative: it will miss corruption where two or more
characters were shaved (e.g. `ad` from `added`, which is itself a word and so is invisible to the
rule), so **every count below is a LOWER BOUND**.

### Counts

| population | distinct types | over-stemmed | % |
|---|---|---|---|
| **all store subjects** | **4,422** | **435** | **9.84%** |
| all store objects | 2,745 | 302 | 11.00% |
| non-tautological `GROUNDED_MEANING` subjects | 1,216 | 135 | 11.10% |
| non-tautological `GROUNDED_MEANING` objects | 922 | 85 | 9.22% |

Token-level (rows, not types): **836 / 7,966 = 10.49%** of all facts have an over-stemmed subject.

Split by provenance — corruption tracks the READING path, not the seed:

| `source` | facts | rows w/ over-stemmed subject | rate |
|---|---|---|---|
| `reading:*` | 7,088 | 802 | **11.31%** |
| `seed_base_vocabulary` | 878 | 34 | 3.87% |

(The 3.87% seed residue is mostly rule false-positives — short proper-noun-ish or abbreviation
tokens; see §1c.)

### 20 examples (stored token -> word recovered by adding back one letter)

```
acquaintanc -> acquaintance     billionair  -> billionaire
ador        -> adore            bottl       -> bottle
announc     -> announce         brak        -> brake
anonymou    -> anonymous        bubbl       -> bubble
atla        -> atlas            cancerou    -> cancerous
barbecu     -> barbecue         chimpanze   -> chimpanzee
belo        -> below            choic       -> choice
bik         -> bike             classmat    -> classmate
analysi     -> analysis         clos        -> close
anxiou      -> anxious          commut      -> commute
```

Also present, from the task's own list: `indigenou`, `tortur`, `statu`, `igneou`,
`staphylococcu`, `allel`, `apparatu`, `basi`, `athlet`, `audienc`, `carbohydrat`, `calori`.

### 1c. Causal confirmation (not just pattern-matching)

The detection rule says "one letter short of a word". That is a *signature*, not a *cause*. Causal
test: for each of the 435 over-stemmed subjects, generate the plausible inflections of the recovered
word (`+s/+es/+d/+ed/+ing`, `y->ies/ied`) and ask whether **`lemma_verb` on any of them returns the
stored token exactly**.

**371 / 435 = 85.3% are reproduced verbatim by `lemma_verb`.** Worked examples:

| stored | source surface | `lemma_verb(src)` | `lemma_word(src)` (today) |
|---|---|---|---|
| `analysi` | `analysis` | `analysi` | `analysis` |
| `anonymou` | `anonymous` | `anonymou` | `anonymous` |
| `apparatu` | `apparatus` | `apparatu` | `apparatus` |
| `activat` | `activated` | `activat` | `activate` |
| `announc` | `announced` | `announc` | `announce` |
| `atla` | `atlas` | `atla` | `atlas` |

The residual 64 (`ann`, `archaea`, `aren`, `audi`, `belo`, `coli`, `cal`, `centr`, ...) are mostly
**rule false-positives** — proper-noun fragments, tokenizer debris (`aren` from `aren't`), British
spellings, and `E. coli`-style abbreviations — not stemmer output. So the honest headline is:
**~8.4% of store subject types (371/4,422) are confirmed stemmer corruption**, and the 9.84% figure
is the loose upper edge of that.

---

## 2. The stemmer, located

| role | file:line | status |
|---|---|---|
| entry point on the reading path | `hdlab/reading_grounding_loop.py:102` (`from hdlab.thematic_role_labeler import lemma_word`), called at `hdlab/reading_grounding_loop.py:195` | current |
| **the correct normalizer (live)** | **`hdlab/thematic_role_labeler.py:235` `lemma_word`** | WordNet `morphy` first, guarded suffix fallback that fires only if the output `is_known_word` (`hdlab/thematic_role_labeler.py:225`) |
| **the culprit (legacy)** | **`hdlab/thematic_role_labeler.py:301` `lemma_verb`** | unguarded suffix stripper; still live for 14 other modules / ~105 call sites |

The offending rules inside `lemma_verb` are the **unguarded** plural/participle strips, notably
`hdlab/thematic_role_labeler.py:326-327`:

```python
if w.endswith("s") and len(w) > 3 and not w.endswith("ss"):
    return w[:-1]
```

This has **no `-us` / `-is` / `-ous` exclusion and no is-it-a-word check**, so `status -> statu`,
`igneous -> igneou`, `analysis -> analysi`, `staphylococcus -> staphylococcu`,
`indigenous -> indigenou`. `hdlab/thematic_role_labeler.py:324-325` (`-es -> w[:-2]`) and
`:319-323` (`-ed -> w[:-2]`) contribute the rest (`tortures -> tortur`, `billionaires -> billionair`,
`dressed -> dres`). `lemma_word` fixed exactly this by adding the `not w.endswith(("ss","us","is"))`
guard AND the `_accept`/`is_known_word` gate (`hdlab/thematic_role_labeler.py:261-283`).

---

## 3. Is it still broken? — live code, actual outputs

Ran on today's code, both functions side by side:

| surface | **`lemma_word` (LIVE reading path)** | `lemma_verb` (legacy stripper) | store contains |
|---|---|---|---|
| `billionaire` | `billionaire` | `billionaire` | — |
| `billionaires` | `billionaire` | **`billionair`** | `billionair` |
| `indigenous` | `indigenous` | **`indigenou`** | `indigenou` |
| `torture` | `torture` | `torture` | — |
| `tortures` / `tortured` | `torture` | **`tortur`** | `tortur` |
| `status` | `status` | **`statu`** | `statu` |
| `igneous` | `igneous` | **`igneou`** | `igneou` |
| `staphylococcus` | `staphylococcus` | **`staphylococcu`** | `staphylococcu` |
| `species` | `species` | **`speci`** | — |
| `analysis` | `analysis` | **`analysi`** | `analysi` |
| `bronchiole` | `bronchiole` | `bronchiole` | — |

Regression set from the module's own docstring, for completeness:
`arteries -> artery` (was `arteri`), `dressed -> dress` (was `dres`), `added -> add` (was `ad`),
`trees -> tree` (was `tre`), `calories -> calorie` (was `calori`), `loses -> lose` (was `los`),
`analyses -> analysis` (was `analys`), `skies -> sky` (was `ski`),
`exclusives -> exclusive` (was `exclusiv`). **All nine fixed.**

### Evidence for the FIXED verdict (timeline, off disk)

- `git log -S'def lemma_word' -- hdlab/thematic_role_labeler.py` -> introduced in exactly one commit:
  **`01093ac1f` 2026-08-12 14:19:43 -0400**, "fix(2a): lemma_word never-emit-a-non-word normalizer
  ...; migrate reading-grounding path off lemma_verb suffix-stripper".
- `git log -S'from hdlab.thematic_role_labeler import lemma_word' -- hdlab/reading_grounding_loop.py`
  -> the same single commit `01093ac1f`. The loop used `lemma_verb` for its whole life before that.
- `store_facts.json` mtime = **2026-08-12T13:46:28Z = 09:46:28 EDT**, i.e. **4h33m before** the fix.
  The preceding loop commit is `04b922c0e` (2026-08-12 13:29:51 -0400)... note that is 13:29 EDT,
  *after* the store mtime, so the store in fact predates even that; `e38fd8454` (2026-08-12 01:08:14
  -0400) is the cycle-1 run that produced it. Either way, every candidate producing commit is
  pre-`01093ac1f` and therefore ran on `lemma_verb`.

**Verdict: FIXED in the current reading path (since `01093ac1f`); the banked
`reading_grounding_v1` store is a pre-fix artifact and carries the corruption permanently unless
rebuilt.** This matches the scoping agent's observation that blind samples show it at 1/78 and
0/73 — those came from post-fix runs.

### Caveat — `lemma_verb` is still live elsewhere

The fix was deliberately scoped (see the SCOPE NOTE at `hdlab/thematic_role_labeler.py:201-205`):
only the reading-grounding path was migrated, because 14 hdlab modules / ~105 call sites were
measured under the old behaviour. **`lemma_verb` remains the normalizer for those 14 modules and
will still emit non-words there.** Blast-radius measurement: applied over the 157,526-form
dictionary universe, `lemma_verb` emits **8,182 distinct non-word stems** from **8,750 distinct
surface forms = 5.55% of the dictionary**. That is the count of vocabulary items any remaining
`lemma_verb` consumer would corrupt. **Not fixed here — reported and stopped, per dispatch.**

---

## 4. Downstream consequence — which published numbers are inflated

Any coverage/vocabulary statistic computed off `reading_grounding_v1` is affected, because a
corrupted token is (a) a spurious *distinct* vocabulary item, and (b) automatically "uncovered" by
any lexical norm table, since no norm table lists `statu`.

### `notes/foundation_contents_audit_2026-08-13.md`

| claim | as published | corrected |
|---|---|---|
| "4422 `KNOWN_WORD` rows, **4422 distinct subjects**" (lines 236, 68) | 4,422 distinct | **4,294 distinct** after one-letter repair — **128 of the 4,422 are duplicate concepts under two spellings** (`statue`+`statu`), i.e. the vocabulary count is inflated ~3% and the *type* count is not a concept count |
| "only 3544 were minted by reading" (line 245) | 3,544 | unchanged as a ROW count, but ~11.3% of those rows key on a non-word |
| "distinct subjects among all 3544 grounded facts: **3544** — exactly 1:1" (line 119) | 1:1 | the 1:1 is partly an ARTIFACT: distinct stems inflate the subject count, so "one object per subject" is measured over a padded subject set |
| "noise LOWER BOUND on the 1216 = 384 (31.58%)" (line 263) | 384 | still a valid lower bound but **too low** — 135 of the 1,216 non-taut subjects are non-words, and a fact whose subject is not a word cannot be a meaning assertion. Union not computed; the true lower bound is >=384 and <=519 |
| tautology counts 2328 / 65.69% (lines 94-100) | 2,328 | **NOT affected** — `(X,GM,X)` is tautological whether or not `X` is corrupt; the audit's own `lemma_verb` normalization row confirming 2328 is consistent |

### `notes/sensorimotor_anchoring_scope_2026-08-13.md`

**Affected (all §1b store rows, and §1e's store decomposition):**

| claim | as published | recomputed |
|---|---|---|
| §1b non-taut subjects, EITHER coverage | **0.613** | **0.7007** after one-letter repair — the published figure understates coverage by **+8.8 points** |
| §1b non-taut objects 0.657, PAIR 0.445 | as published | both understated by a similar margin (9.2% of objects corrupt); not separately recomputed |
| §1b tautological-subject coverage 0.617 | as published | same understatement; the "identical coverage" conclusion is unaffected (both arms share the defect) |
| §1e "126 recovered by unstem (10.4%)" and "344 genuinely uncovered (28.3%)" | 126 / 344 | my independent rule gives **135** for the same bucket; the "genuinely uncovered" residue is correspondingly ~135-not-126 smaller. Direction confirmed, magnitude within noise of the crude heuristic the scoping agent flagged |

**NOT affected — the decision-bearing numbers survive.** §1a, §1c, §1d and §1f are computed on the
**blind samples** (`exp_grounding_quality_readout_v1`, `exp_grounding_text_vs_mechanism`), which come
from post-`01093ac1f` runs and show the corruption at 1/78 and 0/73. So the NOISE-vs-non-NOISE
coverage cut (0.740 / 0.641 vs 0.640), the random-floor result (0.8071 vs 0.8060, p=0.0012) and
AUC 0.685 **stand as published**. The SHELVE decision recorded in that note does not turn on any
corrupted number.

### General rule for anyone computing off this store

> Any "the substrate knows N concepts" / "X% of its vocabulary is uncovered" figure taken from
> `data/foundation/reading_grounding_v1` is inflated: ~10% of its subject vocabulary is stemmer
> debris that is guaranteed to miss every dictionary join. Repair-then-count, or state the store
> is a pre-`01093ac1f` artifact.

---

## 5. What I did NOT do / could not verify

- **No fix applied.** Not to `lemma_verb`, not to the 14 downstream modules, not to the store. The
  dispatch was explicit: report and stop.
- **Did not rebuild the store.** Whether re-running the loop on today's `lemma_word` reproduces the
  same fact count with correct spellings is untested and is the obvious next measurement — note it
  would change fact identity, so it is a rebuild, not a repair.
- **The one-letter-repair rule can over-recover.** `coli -> colic`, `belo -> below`, `audi -> audio`
  are almost certainly wrong recoveries; that is why §1c's causal 371/435 is the number to quote,
  not 435.
- **Two-or-more-letter corruption is invisible to the rule** (`added -> ad`, `trees -> tre`,
  `stopped -> stop`) because the truncation lands on a real word. Every count here is a floor.
- **Object-side repair coverage** was measured only for the type count, not re-joined to the norms
  pair statistic.
- **I did not examine** `hdlab/definitional_extraction.py`, `hdlab/definitional_predicate_v61.py`,
  `data/exp_definitional_predicate_v62/` or `data/exp_structured_comparator_v1/` — concurrently
  owned. Note for the owners: both definitional modules import `lemma_word` (aliased as
  `lemma_verb`) at `definitional_extraction.py:55` and `definitional_predicate_v61.py:82`, i.e.
  they are on the FIXED normalizer, not the legacy one, despite the alias name.
