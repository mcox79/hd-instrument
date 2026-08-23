---
problem: substrate_never_resumes
status: REFUTED
bar: "This problem is answered by a MEASUREMENT, not by a wiring diff. A pull request that wires the load and asserts it is better does not clear it. ... 3. Then measure the thing that matters: with a foundation loaded vs cold, on matched reading volume, report top-anchor share, distinct anchors / grounded, and grounding precision against an independent gold -- each with its floor and CI."
result: "Wiring proven both ways. On identical 4,000-sentence reads (3 seeds), COLD grounds 168 new meanings, RESUMED grounds 9 -- resuming makes a matched read ~18x LESS productive of new groundings, not more. Grounding precision vs conceptnet_gold_v1 sits at the RANDOM_ANCHOR floor in every arm (COLD 0.0199, 3/151; RESUMED 0/9). The premise 'resuming would help / degeneracy falls as vocabulary grows' is REFUTED."
floor: "PRECISION floor = RANDOM_ANCHOR (same terms, random answer): COLD SUBSTRATE 0.0199 vs RANDOM 0.0000-0.0199, not CI-separated; RESUMED 0/9. DEGENERACY floor = DECOY (loaded anchors, meanings permuted): in the pure-mechanism probe DECOY match-rate == RESUMED match-rate EXACTLY (0/164), proving the effect is anchor bins/geometry, not meaning."
controls: "delta-only (excludes the foundation's carried provenance/refusals -- the 22x-trap); identical test text across arms (exact rate-match, removes the forager confound); RANDOM_ANCHOR (holds terms fixed, randomises the answer -- isolates correctness from term-easiness); DECOY permuted-anchor (isolates meaning from anchor count); SELF-RETURN exclusion in the probe (a self-return is a refusal, not a grounding -- counting it as an anchor is what made resume falsely look less degenerate); stem-junk positive control on the clean snapshot (0.00%, a known chop flags); load-spy positive control (a deliberate load is counted)."
files_changed: "experiments/substrate_resume.py, experiments/exp_substrate_resume_helps_v1.py, verification/test_substrate_resume_wiring.py, verification/test_substrate_resume_measurement.py; artifacts data/exp_substrate_resume_solver/clean_snapshot_full/ and data/exp_substrate_resume_helps_v1/. NO change to hdlab/ (proposed diff below)."
reverify: "cd d:/AI/hd-instrument && .venv/Scripts/python.exe verification/test_substrate_resume_measurement.py"
---

# REFUTED: resuming from a saved foundation does not help grounding

**The problem is real; the premise for fixing it is not.** The substrate genuinely discards
everything each run -- confirmed first-hand. But the measurement the brief demands shows that
wiring the load back in does **not** reduce the grounding degeneracy and does **not** improve
grounding correctness. It makes a matched re-read nearly inert. This is the brief's own
failure-mode **(a)** ("loading changes nothing -> the cold-start explanation is refuted ... retires
a standing prediction") combined with **(b)** ("degeneracy falls but precision does not -> variety,
not correctness") -- except the degeneracy did not even fall once measured correctly.

## 1. What I confirmed (the premise, on disk)

- **The substrate never loads.** Instrumenting `foundation_persistence.load_foundation` /
  `save_foundation` around construction + a 400-sentence read: **0 load calls, 0 save calls**, and
  `Substrate(foundation_dir=...)` raises `NotImplementedError`. `live_facts` grows 92 -> 204 within a
  run and a fresh `Substrate()` is back to 92. The brief is accurate.
- **The loader works and is not a build.** `hdlab/foundation_persistence.py` round-trips (its 9/9
  self-tests pass at HEAD). The gap is purely that nothing on the live path calls it -- a wiring job.

## 2. What I built (all in experiments/ + verification/, nothing in hdlab/)

- **`resuming_substrate(dir)`** -- the proposed wiring, prototyped: construct a normal `Substrate`,
  then `state = load_foundation(dir)` and continue `pass_idx` from the manifest. Exactly what the
  constructor diff (below) would do.
- **A clean resumable snapshot, built fresh on HEAD** (the two on-disk snapshots are the
  pre-stemmer-fix contaminated ones). 16,000 sentences over 8 corpora ->
  **207 concept anchors, 390 live facts** (vs the 92-seed cold start), **stem_frac 0.00%**
  (positive control: a known chop flags), so it is not the 7.87% stale artifact. It also carries
  **8,753 PENDING library items** -- a large near-grounded backlog.
- **The measurement** (`exp_substrate_resume_helps_v1`): COLD vs RESUMED (vs DECOY) reading the
  **identical** fixed sentence list (exact rate-match; removes the forager confound), scoring only
  the groundings added by *this* read (delta-only), against the provenance-filtered
  `conceptnet_gold_v1` (reusing the gold + precision + RANDOM_ANCHOR + top-anchor-share definitions
  of the landed cell `exp_grounding_precision_gold_v1`).

## 3. What I measured (3 seeds, identical 4,000-sentence test text)

**Wiring, both ways** (`test_substrate_resume_wiring`, 4/4): OFF (`foundation_dir=None`) -> load
called **0** times, store byte-identical to a plain `Substrate()` seed store; ON -> load called
**exactly once**, store starts populated; an OFF-with-dir arm proves the ablation is real (not
asserted by "off grounds nothing"); a load-spy positive control proves zero means zero.

**End-to-end, delta-only (the headline, deterministic across all 3 seeds):**

| arm | new groundings | precision SUBSTRATE | RANDOM floor |
|---|---|---|---|
| COLD | **168** | 0.0199 (3/151) | 0.0000-0.0199 |
| RESUMED | **9** | 0.0000 (0/9) | 0.0000 |

Resuming makes a matched read **~18x less productive of new groundings**, because the substrate
already knows the recurring vocabulary. No arm's precision is CI-separated above its own
RANDOM_ANCHOR floor.

**Pure-mechanism probe (164 novel words, accumulated context sums held IDENTICAL, only the anchor
space varies -- so any difference is the anchor space alone):**

| anchor space | match rate (word finds ANY anchor >= 0.45) |
|---|---|
| COLD | **161/164** (words match their co-read neighbours: `deprivation`<-10, `rebound`<-10, `stage`<-8) |
| RESUMED | **0/164** (every novel word fails to match any of the 207 loaded anchors -> self-return) |
| DECOY (labels permuted) | **0/164** -- IDENTICAL to RESUMED |

## 4. Why the premise is refuted, and the trap I nearly fell into

- **Resuming does not reduce degeneracy; it prevents grounding.** New words match their *co-read*
  neighbours (same-batch co-occurrence) but not the *cross-run* snapshot anchors -- the 0.45
  similarity gate is never cleared, so they self-return and are refused (`TAUTOLOGY_NO_ANCHOR`
  dominates every arm's refusals).
- **The apparent "degeneracy fell to distinct/grounded = 1.0" was an artifact I caught and fixed.**
  My first metric counted each self-return (canon_obj == the word) as its own anchor, which reads as
  "every word got a distinct meaning". A self-return is canonicalize's NO-MATCH signal -- a refusal,
  not a grounding. Excluding it, the resumed space grounds ~nothing.
- **It is bins, not meaning.** DECOY (loaded anchors, meanings permuted) matches IDENTICALLY to
  RESUMED. A bijection on labels cannot change which vectors clear the threshold, so the loaded
  anchors' *meaning* is irrelevant to the outcome.
- **It buys no correctness.** Precision sits at the random floor in every arm.

This is CLAUDE.md's "a statistic the mechanism optimises is not an outcome" and the brief's failure
mode (b), and it retires the standing prediction that the generic-attractor degeneracy is a
cold-start artifact whose removal would improve grounding. The degeneracy and the poor grounding
have the same cause -- grounding is same-batch co-occurrence -- and a cross-run foundation cannot
supply that. (This is the project's standing diagnosis, arriving on a new instrument; it is the
same wall `reader_meaning_channel` names from the front.)

## 5. What I did NOT establish

- **Precision is under-powered in absolute terms.** COLD scores 3 hits / 151 scorable (the landed
  precision cell's own bar is >= 300 scorable). I lean on precision only for "no improvement / not
  above random", never on an exact correctness number -- the refutation rests on the deterministic
  168-vs-9 grounding gap and the 0/164 match-rate collapse, not on the precision point estimate.
- **I did not test recall/query.** A resumed substrate trivially *knows* 207 words a cold one does
  not; if the goal were "answer about previously-read words", resuming supplies that. But those 207
  are themselves co-occurrence groundings at floor precision, so this is accumulation of quantity,
  not correctness -- not the reading-degeneracy capability the brief is about.
- **Definitions were OFF** in the read driver (distributional path only), to isolate the anchor-space
  mechanism the premise is about. The definitional channel is a separate lever (`reader_meaning_channel`).

## 6. The proposed hdlab diff (for the strategy session to land)

The wiring itself is correct and cheap -- land it for *persistence/accumulation*, but not as a fix
for grounding. In `hdlab/substrate.py.__init__`, replace the raise-block (currently lines 443-448)
and make the seed path conditional:

```python
self.foundation_dir = foundation_dir
# ... existing self._built / _calls / _pass_idx / _seed_vocab setup ...
if foundation_dir is not None:
    from hdlab import foundation_persistence as _fp
    self.state = _fp.load_foundation(foundation_dir)                       # the whole wiring
    self._pass_idx = int(_fp.load_manifest(foundation_dir).get("next_pass_idx", 0))
else:
    store = HDFactStore(n_dim=self.n_dim, seed=self.seed,
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                              MEANING_RELATION: "FUNCTIONAL"}, use_index=True)
    self.state = ReadingLoopState(store=store)
    seed_known_words(self.state, self._seed_vocab, source="substrate_seed")
```

`foundation_dir=None` (the default) keeps behaviour byte-identical (additive, cannot regress).
`next_pass_idx` keeps the Dumay-Gaskell intervening-pass rule correct across the boundary.
**Also:** `verification/test_foundation_dir_does_not_lie.py` asserts the raise and the zero-read; it
must be updated when loading is wired (it will fail on purpose -- the brief and the test's own
docstring both say so).

## 7. Brain framing (honest, per the neuroscientist-first directive)

Consolidation is *defined* by persisting across episodes, so a system that discards its store every
run has no slow/consolidated system at all. That makes the wiring worth doing on brain-fidelity
grounds regardless of this result. But the measurement says the thing it would feed -- distributional
grounding -- is not a meaning mechanism: it links a word to whatever co-occurred in the *same batch*,
which does not transfer across runs. Persistence is necessary for a cortical foundation; it is not
sufficient to make the reading mean anything. That is a statement about our reader, not about brains.

## What I would withdraw first if it turned out to be wrong

The precision claim (under-powered). If a larger-n precision run showed RESUMED grounding CI-above
its random floor, "no correctness gain" would weaken -- but the 168-vs-9 grounding gap and the 0/164
match-rate collapse (both deterministic) would still stand, so the headline (resuming does not reduce
degeneracy and does not increase grounding) would survive.

---

## TLDR (plain language)

The system forgets everything it learns each time it runs, and the plan hoped that letting it
remember would make it read better -- specifically, stop it from deciding dozens of unrelated words
all mean the same thing. I wired the "remember" switch and measured it. Remembering does not help.
When the system starts from a saved memory, a fresh read teaches it almost nothing new (9 new word
meanings, versus 168 from a blank start) -- because it already "knows" the common words, and the
genuinely new ones don't match anything in its saved memory closely enough to stick. And the meanings
it does assign are no more correct than random either way. The reason is that its notion of "meaning"
is really just "what words showed up nearby in the same batch of text", which does not carry over
from an earlier run. So this was the wrong lever: remembering is worth doing so knowledge can pile
up, but it will not fix the reading. That confirms, from a new angle, that the real problem is the
reader's meaning channel, not its memory.

## Questions

None.

## Next steps (for the strategy session)

1. Land the wiring for **persistence/accumulation** (diff in section 6) -- but do not bill it as a
   grounding fix, and retire the "degeneracy falls as vocabulary grows -> better grounding" prediction.
2. Re-point effort at the reader's meaning channel (`reader_meaning_channel`): the measured cause of
   both the degeneracy and the floor-level precision is that grounding is same-batch co-occurrence.
3. When landing, update `verification/test_foundation_dir_does_not_lie.py` (it asserts the now-removed
   raise) so it fails intentionally rather than silently.
