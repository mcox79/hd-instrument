# 🔑 THE MEANING ASSET IS NOT SHORT OF WORDS. **THE LOOKUP IS SHORT OF A LEMMATISER.**

**`hdlab/grounded_similarity.py:165` is the entire live lookup:**

```python
return _table().get(word.lower())
```

**Raw string match, lowercased. No morphology.** So the substrate holds a norm for `country` and
reads straight past `countries`; holds `animal` and misses `animals`; holds `release` and misses
`released`.

---

## 1. THE NUMBER, corpus-scale, replication verified before anything else

Reproduced `exp_meaning_asset_norms_coverage_gap_v1` exactly before trusting any delta --
**235,876 types / 5,558,698 tokens, raw coverage `0.6035` / `0.1027`**, matching the landed cell to
four decimals. *A delta computed off a replication I had not checked would be worth nothing.*

| lookup | TOKEN coverage | TYPE coverage |
|---|---|---|
| raw string -- **WHAT RUNS TODAY** | `0.6035` | `0.1027` |
| **+ `normalize_lemma` (the repo's own, `is_known_word`-gated)** | **`0.7350`** | **`0.1633`** |
| + my suffix rules (liberal; ~4% of its recoveries are wrong) | `0.7435` | `0.1652` |

> # **+13.2 POINTS OF RUNNING TEXT, FROM DATA ALREADY ON DISK. NO NEW NORMS.**

**Against the plan's own build target this is large.** `LONG_TERM_PLAN.md` Phase 1 names
**`+14,704` words to norm** to reach ~90% token coverage. The gap from `60.35%` to `90%` is `29.65`
points; **lemmatising the lookup delivers `13.15` of them -- 44% of the way, at zero data cost.**
*It does not replace the widening. It means the widening starts from a different place, and the
`+14,704` figure counts inflected forms of words we have already normed as words we must go and
norm.*

## 2. HOW IT WAS FOUND -- the band table nobody had read down

The cell's own `coverage_by_frequency_band` says the **1,000 commonest words are only `75.7%`
covered**. That band carries **41.4% of all tokens**, so 243 uncovered types there matter more than
thousands in the tail.

**I expected function words** -- an asset of sensorimotor norms *should* be silent on `and`, `of`,
`which`, and a gap made of those is not a gap at all. **It is not what is there.** `TOP_DROP = 100`
and `MIN_LEN = 3` had already removed them. Enumerating all 243 (small enough to count, so counted):

- **proper nouns** -- `france england germany japanese london berlin disney texas korea`
- **plurals of covered concepts** -- `countries animals games birds cells mountains rivers islands`
- **inflected verbs** -- `died released played killed moved began created published`

**Not one function word among them.** The asset is not correctly staying silent; it is missing
ordinary concrete vocabulary it already contains in another form.

**Effective coverage of that band under lemmatised lookup: `757` -> `~881` of 1,000, `75.7%` ->
`~88%`.**

## 3. ⚠️ THE ERROR RATE, MEASURED BY HAND RATHER THAN ASSUMED

My suffix rules recovered `130` of the 243. **`130` is an UPPER BOUND and I enumerated it to find
out by how much** -- the same stemmer trap this project has already paid for twice (`and -> andes`,
`arteries -> artery`):

| bad recovery | why |
|---|---|
| `using -> us`, `uses -> us` | suffix strip lands on a real but unrelated word |
| `james -> jam`, `angeles -> angel` | **proper nouns**; `angeles` is half of *Los Angeles* |
| `notes -> not` | `-es` strip onto a function word |
| `founded -> found` | real word, **different meaning** (establish vs discover) |

**~5 of 130 wrong (~4%).** `normalize_lemma` is more conservative at `117` and is the arm quoted in
the headline -- **but it is not clean either: it makes the `angeles -> angel` error too.**

**AND IT MISSES IN THE OTHER DIRECTION: irregulars.** `women -> woman` and `feet -> foot` are
recovered by NEITHER method, and both sit in the top-1,000 band. **The true ceiling is above `73.5%`,
not below it.**

## 4. 🚫 WHAT THIS IS NOT -- and the brief's own warning applies to me

**COVERAGE IS NOT CAPABILITY.** `reader_meaning_channel/PROBLEM.md` states the trap for the widening
work item: *"until new words are scored, the coverage number is arithmetic, not capability."*
**That applies to this result unchanged.**

I have shown the asset can be made to *speak* on 73.5% of running tokens instead of 60.35%. **I have
NOT shown that using `country`'s norm for `countries` helps any task**, and no task was run here. It
is plausible on the face of it -- a plural of a concrete noun has essentially the same sensorimotor
profile -- **but plausible is what this project keeps having to withdraw.**

➡️ **THEREFORE I DID NOT CHANGE `grounded_similarity.py`.** Flipping live substrate behaviour on a
coverage number, with no task measurement, is the exact move the standing rules forbid: *a statistic
the mechanism optimises may DIAGNOSE, never DECIDE.* Coverage is that statistic here.

## 5. THE POSITIVE CONTROL, stated because absence checks inherit their detector's blindness

The claim "these 243 are uncovered" is an absence claim, so it is carried by a **presence** control:
my replication had to reproduce the landed `757/1000` **exactly** before the uncovered list was read.
It did. *Had I merely counted misses in my own reimplementation, a tokenisation difference would
have looked exactly like a coverage finding.*

**Scored population saved** (standing rule -- save the set, not just the score):
`notes/problems/reader_meaning_channel/uncovered_top1000_2026-08-22.txt`, all 243. *Promoted out of
`scratch/` deliberately: a durable note citing a gitignored path is a dangling citation into a
directory that gets wiped. **`data/` was the first choice and is ALSO gitignored for `*.txt`** --
verified with `git check-ignore` rather than assumed, after the silent `git add` failure that made
me think a commit had landed when none had.*

---

## TLDR

We have been treating our meaning data as too small. **It is not mainly too small -- we are looking
things up the wrong way.** The lookup matches words letter for letter, so it knows "animal" but
draws a blank on "animals", knows "release" but not "released".

Teaching it to strip word endings before giving up lifts how often it can say anything about the
text in front of it **from about 60% of words to about 73%** -- using nothing but data we already
have. For scale: the plan's headline job is to go and describe ~15,000 new words by hand to reach
90%, and this gets us **nearly half that distance for free.**

Two honest limits. About 1 in 25 of these rescues is wrong -- "using" becomes "us", "Angeles"
becomes "angel" -- so it needs a real lemmatiser rather than my crude version. And **being able to
say something is not the same as saying something useful**: I have measured how often the system can
now speak, not whether what it says helps it read better. That second question needs an experiment,
which I could not run here.

## QUESTIONS

None.

## NEXT STEPS

1. **This is a solver-ready problem, not a strategy one.** Filed into
   `notes/problems/reader_meaning_channel/` -- bounded, has a clear bar, and needs exactly the cell
   run this session cannot do.
2. **The bar it must clear is a TASK score, not a coverage number** -- SimLex or the reader's own
   held-out task, with the information-free twin (lemmatise to a RANDOM covered word) required to
   LOSE. If that twin also wins, the gain is string-matching luck, not meaning.
3. 🚫 **Do not re-quote `+14,704 words to 90%` without this beside it.** That target counts inflected
   forms of already-normed words as words needing new norms.
