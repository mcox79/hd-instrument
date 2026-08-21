# I RECOMMENDED CARRYING ON WITH F5 **BEFORE** DOING THE THREE READS ON E3 -- AND E3 IS **THE ONE PLACE TODAY WHERE THE SUBSTRATE BEATS ITS FLOORS**

**Reversing my own board recommendation, filed one turn ago.** I recommended *"carry on with the
coherence monitor"* and only then ran the three prior-work reads on the alternative. **That is the
same ordering error as the one I had just finished documenting** -- recommending before reading --
and the reads changed the answer.

---

## 1. **E3 IS NOT A MISSING ORGAN. IT IS A WORKING ONE, ABOVE ITS FLOORS.**

`ORGAN_MAP` STEP 4, in its own words: **"This step is therefore a WIDEN-THE-MARGIN step on a working
organ, not a rescue."**

| on the 36-passage McGuffey corpus, same run, same metric | |
|---|---|
| **our resolver** | **0.7193** |
| most-recent-mention floor | 0.5614 |
| singleton / subject-position-majority floor | 0.3860 |
| oracle ceiling | 0.9298 |
| honest earned figure | 0.6842 |

**WE ARE ABOVE BOTH FLOORS.** `WIRED: YES`. **After a day in which every measurement put us at or
below counting** -- untrained 0, trained substrate +16.3, counting +29.4, and the paired test
confirming we are *measurably behind* -- **this is the one place on the map where the substrate is
demonstrably ahead of its trivial baselines.**

## 2. THE THREE READS, DONE PROPERLY THIS TIME

| read | result |
|---|---|
| `organ_map_cite.py E3` | **no constraint on E3 itself** -- only *E4* presupposes it. Its entry: *"Independent. Parallel with steps 1 and 2."* |
| `experiment_index.py query "coreference"` | **3 landed cells**, incl. `exp_wire_coref_accumulate_situation_model_v1` = `BOTTLENECK_QUANTIFIED` -- which is where the floors above come from |
| registry / `hdlab/` | `coreference_resolver.py`, `coref.py`, `state_of_mind.py` all present and wired |

**And the map carries a CORRECTION the citation tool surfaced:** an earlier-quoted floor pair
(recency 0.5439 / singleton 0.4737) comes from a **different corpus, metric and run** and **must not
be placed beside a situation-model score.** *Exactly the cross-population error the standing rules
forbid, already caught and recorded by someone else.*

## 3. ⚠️ **AND THE HARD_PASS BEHIND E3 IS n=10**

`exp_read_coref_hobbs_centering_resolver_v1` is `HARD_PASS` at **1.000 on n=10.** The map does not
hide this -- its can-fail test reads **"at n in the hundreds -- not n=10."** *A 1.000 on ten items is
the underpowered-result-as-capability failure, and it is already flagged in the document rather than
by me.*

## 4. 🎯 **WHY THIS REVERSES MY RECOMMENDATION**

| | F5 | E3 (step 4) |
|---|---|---|
| exists? | **no** | **yes, wired** |
| position vs floors | untested (organ absent) | **above both** |
| what the work is | build a missing organ | **widen a measured margin** |
| fidelity target | reference point pinned, **norm/update/precision all UNPINNED** | **named precisely**: replace invented arithmetic (β=0.5, λ=0.1 are ours) with parallel cue-based retrieval + similarity interference; score by the semantic comparator, not token Jaccard; **keep** the margin abstention, which is already brain-faithful |
| scheduling | **queued behind step 4; Phase B; "not started by accident"** | **independent, startable now** |
| risk | most likely outcome is another arm between substrate and counting | improving something already ahead |

**E3's fidelity fix is more precisely specified than F5's design**, because the brain source gives an
ORDERING and we can see exactly which arithmetic we invented on top of it. **F5's norm and update
rule are unpinned, so more of it would be our invention under test.**

## 5. WHAT I AM NOT SAYING

**Not that F5 is wrong.** Its reference point is genuinely pinned, the read-back gap it addresses is
real, and the owner endorsed it. **The claim is narrower: I recommended it over an alternative I had
not read, and having read the alternative I no longer think my recommendation was the better one.**

**And nothing about today's measurement work depends on this.** The item set, hand-scores, harness
and three-way comparison are properties of the anomaly task and the substrate.

## TLDR

One turn ago I asked you whether to carry on with the coherence monitor or do the pronoun-resolution
step first, and I recommended carrying on. **Then I actually read up on the pronoun step, and I now
think my recommendation was wrong.**

Pronoun resolution is not a missing piece — **we already built it, it is switched on, and it beats
both of its simple comparison baselines** (0.72 against 0.56 and 0.39). After a day where every
single measurement put us at or below plain word-counting, **this is the one place on the map where
our system is measurably ahead of the obvious cheap alternative.**

The document also spells out precisely what is wrong with it — we invented two numbers where the
research only gave an ordering, and we compare names by spelling rather than meaning — so the work is
"fix these three named things and widen a lead we already have", rather than "build something new and
hope".

There is one caveat the document itself flags: the original success was measured on **ten examples**,
which is far too few to trust. Testing it properly on hundreds is part of the job.

**I am not saying the coherence monitor is a bad idea.** I am saying I recommended it over something
I had not yet read, and having read it, I would now recommend the other way.

## QUESTIONS

The board question stands; my recommendation on it is reversed and re-filed.

## NEXT STEPS

1. Re-file the recommendation so the owner is not acting on the superseded one.
2. Either branch: the anomaly-task apparatus is unaffected.
