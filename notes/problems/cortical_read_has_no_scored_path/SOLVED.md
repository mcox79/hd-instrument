---
problem: cortical_read_has_no_scored_path
status: REFUTED
bar: "A TASK SCORE with a CI-separated margin over the strongest floor you actually RUN, on a held-out set."
result: On a CLEAN held-out cloze over the consolidated pool (simplewiki, 3 seeds, n=300 items/seed, ~427-479 consolidated candidates, ranked by hit@k with 2000-sample bootstrap CIs), the best cortical arm (BOTH = context+sensorimotor concat) reaches hit@1 0.057/0.043/0.043 and hit@50 0.37/0.36/0.33, median rank 71/70/87. It reads its cue (beats SCRAMBLE and RANDOM twins) but does NOT clear the strongest floor at ANY k on ANY seed -- best_cortical_clears = False in all 15 seed x k cells. This REPRODUCES and STRENGTHENS the disk's Aug-19 run (exp_cortical_read_consolidated_v1), which the brief wrongly says never happened.
floor: Strongest floor RUN = first-order co-occurrence counting (COOC) over the exact text the substrate read, restricted to the consolidated candidate set: hit@1 0.090/0.103/0.097, hit@50 0.71/0.75/0.70, median rank 22.0/19.5/23.5 -- it BEATS the best cortical arm at every k (e.g. seed 20260819 k=50: COOC 0.7133 CI[0.660,0.767] vs BOTH 0.3667 CI[0.313,0.420], CI-separated). Also ran: FREQ floor (hit@1 ~0.01) and the MANDATED CONCRETENESS-prior floor (hit@1 0.000 all seeds, the weakest floor).
controls: (1) SCRAMBLE (unrelated donor sentence, target kept) hit@1 0.000 -- info-free, LOSES to cortical; EXCLUDES "the arm is a cue-independent constant". (2) RANDOM_twin (per-item random permutation of the pool) hit@1 0.000-0.007 -- info-free, LOSES; EXCLUDES "the rank metric cannot fail safely". (3) CONCRETENESS-prior floor (brief-mandated) hit@1 0.000; cortical beats it; EXCLUDES "the cortical signal is a concreteness artifact" -- the exact confound that killed the last hypothesis on this organ. (4) EPISODIC_FILTERED (episodic route, same candidate set) hit@1 0.000 while surfacing a candidate on 300/300 items -- a FAIR miss, not a reachability failure; EXCLUDES "an episodic-only arm scores the same". (5) CLEAN held-out split (sentences the substrate provably did not read, registries verified deterministic) EXCLUDES the 298-300/300 train-leak found in the Aug-19 cell.
files_changed: experiments/solverB_cortical_scored_path_v1.py, verification/solverB_verify_cortical_scored_path.py, data/solverB_cortical_scored_path_v1/metrics.json, data/solverB_cortical_scored_path_v1/units.jsonl, notes/problems/cortical_read_has_no_scored_path/SOLVED.md (NO hdlab/ change -- proposed change described below)
reverify: cd d:/AI/hd-instrument && .venv/Scripts/python.exe experiments/solverB_cortical_scored_path_v1.py --mode full --seeds 3
---

## THE HEADLINE

**A scored path for the cortical read exists, it runs on clean held-out data, and the answer is a
clean negative: the cortical read reads its cue but is a WORSE retriever than counting
co-occurrences.** On the natural task -- given a held-out sentence with a consolidated word masked
out, rank the consolidated pool and find that word -- first-order co-occurrence counting beats the
cortical read at every operating point, on three seeds, CI-separated at the larger k. The cortical
read is not inert (it beats a content-scrambled cue and a random ranker), and it is not a
concreteness artifact (it beats a concreteness-prior floor). It simply carries less retrieval
signal than the dumbest available baseline that looks at the cue.

This is the cell's own pre-committed READING (B) from `exp_cortical_read_consolidated_v1`: *"every
CORTICAL arm ties or loses to the strongest floor -> the route exists and carries nothing. A real
negative about the ORGAN."*

## THE DISK OUTRANKS THE BRIEF, IN TWO PLACES

**1. The organ was already scored, three days before the brief said it never had been.**
`experiments/exp_cortical_read_consolidated_v1.py` ran FULL on 2026-08-19 (3 seeds, n=300 items,
`data/exp_cortical_read_consolidated_v1/metrics.json`, spec `v3_floors_at_k`) with the same task,
the same COOC/FREQ floors, and the same scramble control. Its verdict was already
`CONTEXT_clears=False, BOTH_clears=False` at every k on every seed. The brief's `WHY THIS ONE`
("it has never been scored") and its `ALREADY TRIED` (which lists only the similarity-statistic
family) are both stale on this point. I re-verified that cell is at HEAD (`ee4be45a1`,
2026-08-19), on the right corpus, with the right metric -- the triple-check discipline -- before
building on it.

**2. That prior run's "held-out" set was 298-300 of 300 already-read sentences.** The Aug-19 cell
built `held_out = pool[n_read:]`, but `Substrate.read` overshoots `n_sentences` via its own cursor
(`max_patches` behaviour, documented in `substrate.py:486`), so it read ~600 sentences past
`n_read`. Worse, items are drawn from the FRONT of `held_out`, which is exactly the leaked region.
Measured directly in my cell (`aug19_style_heldout_overlap_with_read`): **298/300, 300/300,
300/300** item sentences were already read. So the only prior scoring of this organ was almost
entirely on training data. The leak FAVOURS the cortical arm (its profiles saw those exact
sentences; COOC's counts were built only over `pool[:n_read]`), and the cortical read lost anyway;
on my clean split it loses by more (BOTH hit@1 fell 0.057->0.043 on seed 7-class seeds while COOC
held). **Removing the leak strengthens the negative.**

## WHAT I BUILT

A clean, independent scoring harness (`solverB_cortical_scored_path_v1.py`) that:

- **Draws held-out from `pool[total:]`** where `total` is the substrate's ACTUAL read count,
  reconstructed from an independent `CorpusRegistry` and asserted byte-identical (the leak is real:
  `registries_deterministic=True`). Overlap with the read set is 0 by construction.
- **Builds COOC/FREQ over the exact text the substrate read** (a fair floor), not over a
  slightly-different `pool[:n_read]`.
- **Adds the two controls the brief marks mandatory that the Aug-19 cell lacked:** a
  concreteness-prior floor and a random-ranking information-free twin.
- **Saves the scored population** (items, targets, consolidated pool) -- the Aug-19 cell saved
  scores but not the set it scored, which the standing discipline forbids.

Control machinery is witnessed scaffold-free in `verification/solverB_verify_cortical_scored_path.py`
(the twin loses to a planted signal at every k; the concreteness dimension orders concrete above
abstract; the seen/unseen partition is correct) -- so a negative from this harness is a verdict
about the organ, not a broken scorer.

## THE NUMBERS (CLEAN split, 3 seeds, n=300 items each)

| arm | hit@1 | hit@50 | median rank |
|---|---|---|---|
| **COOC floor** (strongest) | **0.090 / 0.103 / 0.097** | **0.71 / 0.75 / 0.70** | **22 / 20 / 24** |
| cortical BOTH (best cortical) | 0.057 / 0.043 / 0.043 | 0.37 / 0.36 / 0.33 | 71 / 70 / 87 |
| cortical CONTEXT | 0.040 / 0.023 / 0.040 | 0.30 / 0.29 / 0.30 | 143 / 158 / 137 |
| FREQ floor | 0.013 / 0.010 / 0.010 | 0.45 / 0.46 / 0.51 | 56 / 52 / 45 |
| CONC floor (mandated) | 0.000 / 0.000 / 0.000 | 0.12 / 0.10 / 0.11 | 228 / 282 / 237 |
| SCRAMBLE (info-free) | 0.000 / 0.000 / 0.003 | 0.11 / 0.18 / 0.12 | 212 / 197 / 222 |
| RANDOM twin (info-free) | 0.003 / 0.007 / 0.000 | 0.11 / 0.07 / 0.13 | 238 / 229 / 201 |
| EPISODIC_FILTERED | 0.000 / 0.000 / 0.000 (surfaced 300/300) | -- | -- |

- **The bar is not met, decisively.** Best-cortical clears the strongest floor's UPPER CI at **0 of
  15** seed x k cells. At k=50 the gap is CI-separated (COOC ~0.71 vs BOTH ~0.36).
- **The metric fails safe.** Both information-free twins sit at/below the cortical arms; the
  concreteness floor is the weakest of all. So the cortical read's small signal is real (cue-driven,
  not a constant) and not a concreteness effect -- it is just dominated by counting.
- **A faint CLS-consistent signal I will volunteer, because it is the one thing that survives:** the
  cortical read is the ONLY route besides co-occurrence that puts any target at rank 1. The episodic
  route filtered to the same candidate set gets hit@1 = 0.000 on all three seeds while surfacing a
  candidate on all 300/300 items -- so it is a fair miss, and the cortical read (0.043-0.057) does
  beat it at hit@1. The consolidation-read route retrieves the target better than the episodic route
  does. That difference is real and it is tiny, and it is buried under the co-occurrence floor.

## BRAIN-FOUNDATIONAL: THE POINT THE OWNER ASKED ME TO GET RIGHT

The organ's EXISTENCE is brain-foundational and PINNED (CLS; McClelland, McNaughton & O'Reilly
1995: consolidated knowledge is read from cortex, not hippocampus). I did not test that. The
retrieval RULE and SPACE are explicitly OURS-under-test (`cortical_recall.py`: *"There is no pinned
equation for cortical semantic retrieval"*), so testing them and finding them wanting is fair.

**But a cloze-with-a-co-occurrence-floor is biased AGAINST what a cortical read is FOR.** Under CLS
the neocortical read's distinctive value is GENERALISATION beyond raw co-occurrence -- retrieving a
concept from a context it was not directly paired with. A task whose answer is a word literally
present in the sentence rewards exactly the hippocampal/episodic style (predict a co-present word),
which is what counting does best. So "counting wins overall" does not by itself condemn the organ's
brain rationale, and reporting only that would be the USER-08-11 error (generalising a narrow,
unfavourable test to "impossible").

**So I ran the strongest brain version of the test: stratify by whether the target ever co-occurred
with the cue words in the read text.** On the UNSEEN subset, counting has NO signal (COOC median
rank = full pool, hit@k = 0 by construction), so this isolates the CLS-distinctive question: does
the cortical read generalise where the episodic style cannot?

**The answer, underpowered but directionally null: no.** Pooled n=43 unseen items across 3 seeds
(9-17 per seed, below my n>=30 gate, so reported as a HYPOTHESIS not a verdict). On unseen items the
cortical arms (median rank 145-338 of 427-479) are indistinguishable from SCRAMBLE, FREQUENCY and
RANDOM -- all near the middle of the pool. The cortical read does not fill the gap that counting
leaves. **Both regimes agree: the current retrieval space carries a weak co-occurrence-shaped signal
and no generalisation signal.**

Why underpowered: at 16,600 sentences read, almost every consolidated target has already co-occurred
with its cue words, so natural unseen items are rare. A powered generalisation test needs a task
CONSTRUCTED to have many unseen-co-occurrence items -- e.g. held-out drawn from a held-back
domain/corpus, or a sparser read with a large pool. That is the single most useful follow-up and it
is NOT what this cell measured.

## WHAT I DID NOT ESTABLISH

- **That the cortical read is USELESS as an organ.** I showed it loses on THIS task and shows no
  generalisation on a 43-item underpowered subset. The brain-distinctive regime (generalisation
  beyond co-occurrence) is where it might earn its place, and it is exactly the regime I could not
  power. REFUTED here means "does not clear the floor on the scored cloze," not "has no brain value."
- **That the consolidation gate is blind/aware of anything.** I did not touch the gate.
- **A CI-separated generalisation result** in either direction -- the unseen subset is too small.

## WHAT I WOULD WITHDRAW FIRST IF WRONG

The generalisation null (n=43, underpowered) -- it is a direction, not a finding, and I have flagged
it as such. The PRIMARY verdict (cortical read does not clear the co-occurrence floor on the clean
cloze) is the robust claim: it reproduces across two independent scorings (the Aug-19 disk cell and
this one), across 3 seeds, at all 5 k, and survives removing a 100%-item leak that favoured it. If I
had to distrust one number, it would NOT be that.

## PROPOSED hdlab/ CHANGE (for the strategy session to re-verify and land)

**Do NOT wire `cortical_recall` onto the live `read()` path on the strength of retrieval quality.**
The slot `B3'` is `NEEDS_ADAPTER` "because no scored path calls it yet." A scored path now exists,
and the evidence says an adapter that used the current cortical read for retrieval would add nothing
over first-order co-occurrence counting (and would lose to it). Concretely:

1. **Update the `B3'` slot note in `hdlab/substrate.py`** (the `SLOTS` table rationale) from "no
   scored path calls it yet" to a scored, evidence-bearing status: *live and consolidation-dependent
   (Aug-19 8/8), but on a clean held-out consolidated-pool cloze it does NOT clear the co-occurrence
   floor at any k (3 seeds; `data/solverB_cortical_scored_path_v1/metrics.json`), and shows no
   generalisation signal in the (underpowered) unseen-co-occurrence regime.* Keep it
   `NEEDS_ADAPTER`/shelve it with THIS as the revival criterion, not "someone should score it."
2. **The revival criterion, brain-framed:** the cortical read earns a live adapter only if its
   retrieval SPACE beats co-occurrence counting in the GENERALISATION regime (unseen co-occurrence),
   on a task powered for it. The accumulated-context / sensorimotor space it uses today does not.
   That is a change to the SPACE (`build_cortical_index`), not a wiring job.

I cannot make these edits (owner ruling Q111: the strategy session is the sole writer of `hdlab/`).
The mechanism is proven in `experiments/` + `verification/`; the diff above is the answer.

## TLDR

We built a component that is supposed to answer questions from the brain's "settled knowledge"
store, and until now nobody had a fair test of whether it answers WELL. I built that test: hide a
word in a sentence the system never read, and ask the component to guess it from the settled-store.
**It guesses worse than simply counting which words tend to appear together.** It is not broken --
it does better than random and better than guessing by how "concrete" a word is, and slightly better
than the older memory route -- but a dumb word-counter beats it every time. I also found that the
earlier test everyone assumed was "held-out" was actually run almost entirely on sentences the
system had already read, which quietly flattered it; on genuinely unseen sentences it does worse. I
made sure this was a fair test of what the component is FOR (generalising to new situations, not
parroting co-occurrence) by testing the one regime where counting can't help -- and there it shows
no advantage either, though that part of the test was too small to be conclusive.

## QUESTIONS

None. (One open design question, `Board Q114`, about whether the ~30-term consolidated pool per read
is intended, is upstream of this and belongs to the strategy session.)

## NEXT STEPS

1. **Powered generalisation test** -- the highest-value follow-up. Construct a held-out task with
   >=200 unseen-co-occurrence items (held-back domain, or sparse read + large pool). That is the only
   test that can tell "the organ is genuinely useless" from "this cloze task was rigged against it."
2. **Land the slot-note update** (proposed diff above) so `B3'` carries its scored verdict, not
   "unscored."
3. If a live cortical read is still wanted, the lever is the retrieval SPACE, not wiring -- the
   current space loses to counting even before generalisation.


---

## INTEGRATED_BY_STRATEGY 2026-08-22

**Re-verified on the artifact** (`data/solverB_cortical_scored_path_v1/metrics.json`), and I
measured the one thing that would have sunk their own clean split: their held-out set starts where
reading stopped, counted by sentences DELIVERED, so if `read()` CONSUMED more corpus than it
delivered their 'unread' set would contain read sentences -- the exact defect they caught in the
Aug-19 cell. **Cursor advance equals delivery, gap `0` at three settings. The split is clean.**

**ONE CORRECTION, and the truth is tidier than what they wrote:** they attribute the Aug-19 leak
to `read()` running past its request. It does the OPPOSITE -- ask for 3,000 and it delivers 1,150.
**The real cause is loop shape: chunked reading to a 16,000 target lands at 16,600, and the old
cell drew items from the FRONT of its held-out set, which is exactly those 600 sentences.** That
explains `300 of 300`; 'the reader overshoots' does not. *The measurement is unaffected.*

**LANDED (`ed9ce6273`):** slot `B3'` in `hdlab/substrate.py` now carries the scored verdict
instead of 'no scored path calls it yet', with the revival criterion BRAIN-framed rather than
performance-framed. **It stays `NEEDS_ADAPTER` -- but on EVIDENCE rather than on absence of
evidence, which is a different claim.**

**THEIR RECOMMENDED FOLLOW-UP IS NOW FILED** as `notes/problems/cortical_read_never_tested_where_it_matters/`.
*They named it while their own result looked like a clean negative, and flagged their `n=43`
generalisation null as the first thing they would withdraw. That is why it is ranked where it is.*
