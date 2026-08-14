# Is 4.80% below a spelling-only baseline? VET of the orthographic floor claim

Date: 2026-08-14. Auditor pass, read-only on `hdlab/` and `experiments/`. No experiment cell was
run; every number below is read off metrics already on disk, or produced by a runtime import trace
that writes only to `scratch/`.

---

## TLDR

**The claim does not hold as stated, and it fails for a reason nobody had spotted: the arm was
misidentified.**

The two cells ARE fairly comparable — same corpus, same items, same candidate pool, same gold
answers, same scorer, same n. That part of the brief is confirmed, bit-exactly.

But `A5_STRINGCTRL` is **not a spelling-only method**. Its score is
`z(substrate similarity) + w * z(character-trigram similarity)` — the substrate's own signal PLUS a
spelling channel. So `0.1027` is not "what a spell-checker scores." It is "what our system scores
once you bolt spelling onto it." Comparing it to `0.0480` compares *us* to *us plus spelling*, not
*us* to *a speller*.

**Therefore: do NOT propagate "the system underperforms a spell-checker." It is not established by
this cell, and the measurement that would establish it does not exist on disk.**

What IS established, and is still bad news, is a weaker but real statement:

> On this metric, a channel with **zero** semantic content buys more than our meaning assets do.
> Adding pure spelling to the live score lifts hit@1 by **+4.25 points** (0.0480 -> 0.0905);
> adding the trained encoder lifts it by only **+2.70 points**. The cell's own conclusion field
> says so: `encoder_gain_attributable_to_string_similarity: true`.

That means the 4.80% number is **measuring something spelling can largely fake**, so it is not
trustworthy as a measure of understanding — which is a different, and in some ways more damaging,
finding than "we lose to a speller."

---

## 1. Was the comparison fair? YES on pools — verified bit-exactly

The worry was that the two numbers came from different setups. They do not. The reason is
structural: **the meaning-supply cell does not have its own corpus or item builder. It imports the
readout cell and calls its functions.**

`experiments/exp_meaning_supply_separation_v1.py`:

| line | what it reuses from the readout cell |
|---|---|
| 69 | `MASTER_SEED = C3.MASTER_SEED` |
| 382 | `sents = C3.build_corpus(run_mode)` |
| 384 | `buckets, counts = C3.build_buckets(sents)` |
| 386 | `space = C3.build_space(sents, buckets, output_dir)` |
| 390-391 | `C3.MAX_ITEMS`, `items = C3.build_items(...)` |
| 447 | `gold = C3.gold_meaning_set(L)` |

So "same corpus / same items / same gold set" is not an inference from matching numbers — it is the
same code executing.

The matching numbers confirm it anyway. Four statistics agree to every digit reported:

| statistic | readout cell (`204eba1a0`) | meaning-supply cell (`c0e6ec0da`) |
|---|---|---|
| live arm hit@1 | `B5_OPEN_REAL` = 0.048 | `A1_BASE` = 0.048 |
| its 95% interval | [0.04125, 0.05475], sd 0.003414 | [0.04125, 0.05475], sd 0.003414134660129855 |
| scramble floor | `B6_OPEN_SCRAMBLE` = 0.008 | `F_SCRAMBLE` = 0.008 |
| its 95% interval | [0.00525, 0.011], sd 0.001431 | [0.00525, 0.011], sd 0.001430965936002671 |
| n items | 4000 | 4000 |
| n candidate anchors | 5491 | 5491 |
| items before the 4000 cap | 4603 | 4603 |
| items dropped | 404 not in WordNet, 484 no gold anchor, 53 foil fallback | identical three numbers |

Two independent runs producing identical bootstrap standard deviations to 9 decimal places is not a
coincidence; it is the same arm computed twice from the same seed on the same data.

**The scorer is also the same one.** Both use the open-vocabulary argmax: every one of the 5491
anchors is a candidate, except the word's own anchor and its spelling variants, which are removed
before the pick (`exp_grounding_readout_known_answer_v1.py:557-562`). "hit@1" means the single
top-scoring candidate is in the WordNet gold set for that word.

### The six triple-checks, all run

1. **Right file** — absolute paths `D:/AI/hd-instrument/data/exp_meaning_supply_separation_v1/metrics.json`
   and `.../exp_grounding_readout_known_answer_v1/metrics.json`. Directory listings show exactly one
   `metrics.json` in each; there is no `_smoke` or `_selftest` sibling directory that could have
   been read by mistake.
2. **Right version at HEAD** — `c0e6ec0da`, `204eba1a0` and `9316f98ee` all confirmed ancestors of
   HEAD via `git merge-base --is-ancestor`. Both experiment sources and both `metrics.json` files
   are **unmodified in the working tree** (`git status --porcelain` on all four paths returns
   nothing), so what is on disk is what was committed. No later fixing commit exists for either.
3. **Right environment** — `.venv/Scripts/python.exe` for every command; bare `python` never used.
4. **Right corpus** — identical by construction, see the import table above.
5. **Right metric** — both are open-vocabulary hit@1 over 5491 anchors with the self-anchor
   excluded and gold from `C3.gold_meaning_set`. Same definition, same denominator (4000).
6. **Right arm** — `A1_BASE` and `B5_OPEN_REAL` are the same arm; proven by the bit-identical
   statistics above rather than assumed from the names.

**Verdict on fairness: the pools, scorer, n, gold set and anchor set are IDENTICAL. The brief's
prior was correct.**

---

## 2. But the arm is not what the brief thinks it is — this is the finding

`exp_meaning_supply_separation_v1.py`, lines 235-240:

```python
def arm_scores(base: np.ndarray, aux_terms: Sequence[np.ndarray], w: float) -> np.ndarray:
    """z(base) + w * sum(z(aux)). Per-item z over the ELIGIBLE pool makes w scale-free."""
    out = _z(base)
    for a in aux_terms:
        out = out + w * _z(a)
    return out
```

and line 469, which says what each arm's auxiliary channel is:

```python
armaux = {"A1_BASE": [], "A2_NORMS": [aux_g], "A3_ENCODER": [aux_e],
          "A4_BOTH": [aux_g, aux_e], "A5_STRINGCTRL": [aux_t]}
```

`aux_t` is the character-trigram profile. So:

- `A1_BASE` = `z(substrate)` alone. This is the live path. It is the same at every `w` because
  its auxiliary list is empty.
- `A5_STRINGCTRL` = `z(substrate) + w * z(trigram)`. **The substrate is still in there at full
  weight.**

The cell's own docstring for the trigram channel (lines 151-160) is explicit that this arm was
built to answer *"is the encoder's gain bigger than what spelling alone can add on top of the same
base?"* — a **head-to-head between two add-on channels**. It was never built to be a standalone
floor, and it is not one.

**Consequence:** the sentence "a method with zero understanding scores 0.1027" is false. Every point
of that 0.1027 sits on top of the substrate's own contribution. The correct reading of 0.0480 vs
0.1027 is *"adding spelling to our system more than doubles this score"* — which indicts the
**metric**, not (directly) the system.

### The orthography-only number does not exist on disk

I checked. No arm in any metrics file scores character-trigram similarity with the substrate term
removed. `F_SCRAMBLE` (0.008) shuffles the pairings; `F_FREQUENCY` (0.0185) picks by corpus
frequency; `F_PROJDRAW` re-runs the base arm with a different random seed. None of them is spelling
alone.

**So the question the brief asked cannot be answered from existing metrics. It is OPEN, and it is
now the single cheapest high-value measurement available.** Marked NOT DONE deliberately: the brief
constrains this pass to re-scoring off existing metrics, and no new run was made.

A previous session had already drafted the exact recompute and was killed before running it:
`scratch/ortho_floor_vet_trigram_only.py` (adds `A6_TRIGRAM_ONLY`, `A7_PREFIX_ONLY` = shared-stem
heuristic, `A8_MAXORTHO`, and re-derives `A1_BASE` to prove the harness still reproduces 0.0480).
It reuses the C3 harness, so it would be pool-identical by construction. Estimated cost ~10 minutes,
matching the readout cell's 543 s. **Run it before anyone quotes an orthographic floor number.**

---

## 3. Which of w=1.00 and w=0.50 is the legitimate comparison

**w = 0.50.** The cell pre-declares it:

```
"w_headline": 0.5,
"headline_w": "w_0.50",
"max_over_w_is_an_optimistic_upper_bound": true
```

`w` is the knob controlling how loudly the auxiliary channel speaks relative to the substrate.
`w=1.00` is the best of a three-point grid (0.25 / 0.50 / 1.00). Quoting the best grid point as if it
were the result is picking the winner after seeing the scores — which is exactly why the cell wrote
`max_over_w_is_an_optimistic_upper_bound: true` into its own metrics.

There is one genuine asymmetry worth stating, because it will come up again: **when an arm is used
as a FLOOR — a bar you must clear — taking the maximum over its tuning grid is the RIGHT choice**,
because a floor is supposed to be the strongest attack available, and tuning the attacker is fair
play. When an arm is a TREATMENT you are claiming credit for, you must use the pre-declared setting.
Here the point is moot twice over: `A5` is not a floor (section 2), and even at `w=1.00` the meaning
arm `A4_BOTH` scores 0.1190, above `A5`'s 0.1027 at the same `w`.

---

## 4. What the numbers actually say (all at the declared w=0.50 unless noted)

| arm | what it is | hit@1 | median rank | gold in top-50 | separation margin (median) |
|---|---|---|---|---|---|
| `A1_BASE` | the live path | 0.0480 | 37.0 | 0.5565 | -2.109 |
| `A2_NORMS` | + hand/grounded norms | 0.0712 | 23.5 | 0.6420 | -1.967 |
| `A3_ENCODER` | + trained encoder | 0.0750 | 25.5 | 0.6185 | -2.008 |
| `A4_BOTH` | + both meaning assets | 0.0940 | 18.0 | 0.6823 | -1.886 |
| `A5_STRINGCTRL` | + spelling only | 0.0905 | 25.0 | 0.6118 | **-3.178** |
| `F_FREQUENCY` | pick the commonest word | 0.0185 | — | — | — |
| `F_SCRAMBLE` | shuffled pairings | 0.0080 | — | — | — |

Plain reading of each column: **hit@1** is how often the single best guess is right. **Median rank**
is where the right answer sits in the full ranked list of 5491 candidates — lower is better, and it
sees the whole list, not just the winner. **Gold in top-50** is how often the right answer is
anywhere in the top 50. **Separation margin** is how far the best right answer beats the best wrong
answer, measured in standard deviations of that item's candidate scores; it is negative throughout,
which means *the best wrong answer normally outscores the best right answer* — the system is
usually wrong and only occasionally lucky. Higher (less negative) is better.

### 4a. The spelling channel buys more than meaning does

`string_shortcut_control` in the metrics, at the declared headline:

```
"d_A3_ENCODER":    +0.0270      (the trained encoder's contribution)
"d_A5_STRINGCTRL": +0.0425      (pure spelling's contribution)
"encoder_gain_exceeds_string_control": false
"encoder_gain_attributable_to_string_similarity": true
```

The encoder is our meaning asset. Spelling — which knows nothing — outperforms it as an add-on by
57%. Whatever the encoder is contributing on this task is, on this evidence, not distinguishable
from noticing that `neuron` and `neural` share letters.

### 4b. The spelling channel is an argmax-only shortcut, and it shows

Watch what happens to `A5_STRINGCTRL` as the spelling channel is turned up:

| w | hit@1 | median rank | gold in top-50 | separation margin |
|---|---|---|---|---|
| 0.25 | 0.0693 | 28.0 | 0.6068 | -2.278 |
| 0.50 | 0.0905 | 25.0 | 0.6118 | -3.178 |
| 1.00 | 0.1027 | **31.0** | **0.5867** | **-5.537** |

The headline number climbs steadily. Everything else gets **worse**: at `w=1.00` the median rank is
worse than at `w=0.50`, the top-50 rate falls *below* the base arm's 0.5565, and the separation
margin collapses to more than twice the base arm's deficit.

The meaning arms behave the opposite way — `A4_BOTH` improves on hit@1, rank, top-50 and separation
all at once (0.0940 / 18.0 / 0.6823 / -1.886).

**This is the signature the hardened C3 gate exists to catch**, and it is direct empirical support
for the gate's separation-margin condition: a shortcut can lift the winner without moving the
distribution, and separation is the condition that notices.

### 4c. `F_PROJDRAW` is not a floor, and it is quietly alarming

```
"F_PROJDRAW": {"draws": [0.0515, 0.0525, 0.05025], "mean": 0.05142, "sd": 0.00092}
```

Built at line 506 by `build_salted_space(sents, buckets, "PROJDRAW_%d|" % r, ...)`: it rebuilds the
**same base arm** with a different random-projection salt. It is a **re-run reliability estimate,
not a no-understanding baseline** — anyone reading the name as "a floor at 0.0514" is wrong, and it
should be renamed.

But note what it says: **all three reseeds land ABOVE the 0.0480 headline** (0.0503, 0.0515, 0.0525).
The headline 4.80% is one draw of a quantity whose typical draw is nearer 5.1%. That does not rescue
anything — it is still far below the 10% gate — but it does mean the exact figure 4.80% carries
about half a point of seed noise and should not be quoted to three digits or compared against other
numbers at a resolution finer than ~0.001.

---

## 5. The honest current standing

Stated plainly, and preferring the harsher reading where readings differ:

1. **The strongest MEASURED baseline-without-understanding on this identical pool is
   `F_FREQUENCY` = 0.0185** (guess the commonest word). The live path's 0.0480 beats it by 2.6x with
   non-overlapping intervals. **We are above every no-understanding baseline that has actually been
   measured.**
2. **But the strongest one has not been measured.** Spelling-alone is absent from disk, and the
   indirect evidence that it would be high is strong: spelling as an add-on outperforms our trained
   encoder. Until `A6_TRIGRAM_ONLY` is run, the correct status of the orthographic floor is
   **UNMEASURED**, not "beaten" and not "we lose to it."
3. **The metric itself is compromised.** Roughly half the achievable movement on this score is
   reachable by surface string matching. That makes raw hit@1 unfit to answer "did this change help
   understanding?" regardless of where the floor lands.
4. **The framing that must be retired regardless of the floor result** is "4.80% vs a 0.80% scramble
   floor, 5.2 points short of a 10% gate." The 0.80% scramble floor controls only for random
   re-pairing. It is the *weakest* available baseline and it was being used as *the* baseline. A
   bare absolute target like "10%" is meaningless when a spelling channel can move the score by 4+
   points.

### The standing rule this implies

> **A gate must be a confidence-interval-separated MARGIN above the strongest baseline that
> involves no understanding — the maximum of (orthographic, frequency, scramble), each measured on
> the identical scorer, n, candidate pool and gold set — never a bare absolute number.**
>
> And the baseline must be **standalone**: an arm that adds a shortcut channel *on top of* the
> system under test is a decomposition, not a floor. Check what is in the arm before quoting it as
> one. That mistake is what this document exists to record.

---

## 6. Does `char_trigram_encoder` exist, and is it reachable? EXISTS / NOT REACHED

**Exists: yes.** `hdlab/char_trigram_encoder.py`, one public class:

```
CharTrigramEncoder(n_dim: int = 4096, pad_char: str = ' ')
    .encode(text: str) -> np.ndarray
    .encode_batch(texts: Iterable[str]) -> np.ndarray
    .nearest(query: str, codebook: np.ndarray, names: list[str], k: int = 5) -> list[dict]
```

Its registry row claims `status: wired_load_bearing`, `gate_decision: WIRED`, and lists 15+
experiments using it — while simultaneously recording
`pipeline_status: WIRED_BUT_NOT_PIPELINE_REACHABLE`. Per the standing rule that `pipeline_status` is
wrong in both directions, that field decides nothing. Runtime does.

**Reached on the live readout path: no. Measured, not assumed.**

Method — a runtime import trace, never grep (`scratch/ortho_trace_char_trigram.py`):

- A recorder was installed on both `builtins.__import__` and `importlib.import_module`, so **lazy
  imports inside function bodies and dynamic imports are both visible**.
- Eager closure of the live path (`hdlab.reading_grounding_loop` +
  `hdlab.grounding_acquisition_loop` + the C3 readout cell) = **40 `hdlab` modules**.
  `hdlab.char_trigram_encoder` is not among them.
- The live entry point was then **actually executed**: `process_sentence(state, sentence,
  episode_id, pass_idx)` ran successfully on three real definitional sentences, returning 5, 6 and 5.
  Modules pulled in by that execution: **none**. Recorded `char_trigram` import events: **none**.
- **Positive control, so that "no imports fired" cannot be confused with "the trace is blind":**
  calling `StructuralEncoder._load()` — which contains function-body imports at
  `hdlab/reading_grounding_loop.py:343-345` — pulled in `hdlab.arc_labeler`, `hdlab.arc_parser`,
  `hdlab.perceptron` and `hdlab.pos_tagger`. **The trace demonstrably sees function-body imports.**
  It saw those four and still saw zero for `char_trigram_encoder`.
- Independent corroboration: an AST scan of every function-body import across all of `hdlab/` lists
  26 lazily-imported targets. `char_trigram_encoder` is not one of them, so there is no lazy call
  site anywhere in `hdlab/` for the runtime trace to have missed.

**This is a real signal we own and discard.** We have a working character-trigram encoder on disk,
and the readout that is currently being defeated by character-trigram similarity does not consult
it — not to use it, and, more importantly, not to *subtract* it.

### What using it would concretely mean

- **Module / function:** `hdlab.char_trigram_encoder.CharTrigramEncoder.encode_batch` over the 5491
  anchor strings once, giving a 5491 x 4096 codebook; then `.encode` per cue.
- **Call site:** `experiments/exp_grounding_readout_known_answer_v1.py:560-562`, the
  `canonicalize_fast("__slot__", qL, space, thresh=-1.0, eligible_mask=open_base)` call. That single
  line is the open-vocabulary argmax the reading loop performs, and it is the one place a spelling
  channel enters or is removed.
- **The arms this makes possible** (none currently exist on disk):
  - `F_ORTHO_ONLY` — score every eligible anchor by trigram cosine against the cue string, with the
    substrate term removed entirely. **This is the missing floor**, and the number that decides
    whether "below a spell-checker" is true or false.
  - `F_ORTHO_MAX` — the same floor tuned over a small grid, since a floor should be the strongest
    attack available (see the asymmetry in section 3).
  - `A_BASE_ORTHO_RESIDUALIZED` — the substrate score after the trigram direction is projected out.
    This answers the question that actually matters: *what does the substrate know that spelling
    does not?* On present evidence that residual could be near zero, and finding out is cheap.
  - `SPLIT_LOW_OVERLAP` — the cheapest honest fix, and arguably the one to do first: report hit@1
    **restricted to items whose gold answer has low string overlap with the cue**. That removes the
    confound from the METRIC rather than adding another arm to argue about, and it can be computed
    from the existing item list.

---

## 7. What this does and does not invalidate

**Not invalidated.** The growth-side results stand: the no-leak checks, the scramble ratio of 0.077,
and the bit-identical persistence round-trip. Those measure a **different claim** — that grounding
tracks the real reading context rather than a shuffled one — and spelling overlap does not touch
that claim, because both the real and the shuffled arm face the same spelling statistics.

**Invalidated.** Two things:
- The **absolute-threshold framing**: "4.80% against a 0.80% floor, short of a 10% gate."
- Any **"did this change help?"** judgement made on raw hit@1 against the scramble floor. Roughly
  half the movable range on that score is reachable without understanding, so a gain there is not
  evidence of a meaning gain unless a standalone string-form control was run and beaten.

## 8. Open, with owners

| # | question | status |
|---|---|---|
| O1 | What does spelling ALONE score on this pool? | **NOT DONE.** Script drafted: `scratch/ortho_floor_vet_trigram_only.py`. Blocking every floor claim. |
| O2 | What does the substrate score once spelling is projected out? | NOT DONE (`A_BASE_ORTHO_RESIDUALIZED`). |
| O3 | Does the 4.80% survive on low-string-overlap items only? | NOT DONE (`SPLIT_LOW_OVERLAP`); cheapest of the three. |
| O4 | `F_PROJDRAW` is named like a floor and is not one | Rename; and note the base arm's reseeds all exceed its own headline. |
| O5 | `char_trigram_encoder` registry row says WIRED, runtime says not reached | Registry row needs reconciling against the runtime trace in section 6. |
