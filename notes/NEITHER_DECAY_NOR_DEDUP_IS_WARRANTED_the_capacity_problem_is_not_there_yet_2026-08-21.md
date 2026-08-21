# **NEITHER DECAY NOR DEDUP IS WARRANTED BY MEASUREMENT** -- AND I ASSERTED BOTH LAST TURN

**Two turns ago the sleep target was a decay mechanism. One turn ago I said decay was wrong and
DEDUP was "the honest build target". Both were assertions. Measured, both are wrong.**

---

## 1. SLOT GROWTH IS **ORDINARY**, NOT PATHOLOGICAL

| sentences | slots | slots/sentence |
|---|---|---|
| 256 | 935 | 3.65 |
| 1,024 | 2,748 | 2.68 |
| 4,096 | 6,217 | **1.52** |

**Heaps exponent `beta = 0.589`.** *That is textbook vocabulary growth (0.4-0.6). Not saturating,
but the per-sentence rate is FALLING steadily -- 3.65 -> 1.52.* **"Unbounded growth" was my word for
it and it was the wrong word.** Sublinear growth in distinct concepts is what reading anything
produces; it is not a pathology and it is not something sleep needs to fix.

## 2. DUPLICATION IS **ABSENT** -- MEASURED AGAINST A FREQUENCY-MATCHED NULL

| band | n | median cos | p95 cos | **> 0.90** | null p95 |
|---|---|---|---|---|---|
| rare (1-2) | 5,809 | 0.005 | 0.122 | **0.03%** | 0.101 |
| mid (3-9) | 2,138 | 0.029 | 0.152 | **0.00%** | 0.103 |
| common (10+) | 1,317 | 0.118 | 0.316 | **0.00%** | 0.102 |

**Essentially no pair of distinct slots holds the same content, in any frequency band.** *Common
words sit higher (median 0.118 vs 0.005) exactly as they should -- they share more contexts -- and
still nowhere near duplication.*

**➡️ THE OWNER'S MIDDLE CLAUSE -- *"a consolidation function so we're not duplicating things"* -- HAS
NOTHING TO CONSOLIDATE.** The concern is entirely reasonable in principle; **the substrate does not
currently exhibit it.**

**AND THE STRATIFICATION WAS NOT DECORATION.** A rare-word pair at cos 0.99 would be an
*undersampled* pair, not a duplicate -- reporting an unstratified number against zero would have
manufactured a duplication problem out of rare words. *The null makes the zero readable: 0.03% sits
below what shuffled profiles produce.*

## 3. 🚨 SO THE SLEEP DIRECTION HAS NOW FAILED THREE WAYS IN THREE TURNS

| proposed | why it does not apply |
|---|---|
| **cascade / graceful decay** (D8) | our slots are **private**; we lack the shared-synapse interference it defends against. Measured slope **-0.031** vs the **-0.50** a Benna-Fusi system gives |
| **cold storage / tiering** | **already built and proven** (`prelim_tier`, *"retain-forever"*) -- a WIRING gap, not a build |
| **consolidation / dedup** | **no duplicates exist to consolidate**, in any frequency band |

**➡️ AT THE SCALE WE ACTUALLY READ AT, THERE IS NO CAPACITY PATHOLOGY TO FIX.** *Sleep is, on today's
evidence, a solution in search of a problem here -- which is a real finding and was cheap to get.*

## 4. THE HONEST LIMITS -- AND ONE IS LOAD-BEARING

- **SCALE.** This is **4,096 sentences and 6,217 slots.** A capacity pathology at 10^6 sentences
  would be invisible here. **`beta = 0.589` does not saturate**, so the count keeps climbing; what it
  costs at two more orders of magnitude is **untested**, and that is the version of the question
  worth asking.
- **ONE REPRESENTATION.** Duplication was measured on accumulated context profiles. Two slots could
  hold the same *fact* while differing as *distributions*.
- **This does not touch the owner's principle**, which stands on its own: we are not capacity-bound
  the way the brain is, so copying biological forgetting would copy a constraint we do not share.

## TLDR

Three turns ago the plan was to build a forgetting mechanism. Two turns ago I found we do not have
the problem it solves. One turn ago I said the real gap was **removing duplicates** instead. **I
measured that today and it is also wrong: there are essentially no duplicates to remove.**

I also checked whether our memory grows out of control, since I had claimed it does. **It does not.**
It grows the way vocabulary always grows when you read — quickly at first, then slower and slower.
That is normal, not a fault.

So the sleep idea has now failed three different ways in three turns: the forgetting mechanism does
not fit how we store things, the cold-storage part already exists and just is not plugged in, and
there is nothing duplicated to consolidate. **At the scale we actually work at, there is no storage
problem to solve.**

**The one caveat that matters:** all of this is measured on four thousand sentences. A problem that
only appears at a million would be invisible here, and our memory does keep growing rather than
levelling off. **That is the version of the question genuinely worth asking, and it is untested.**

Worth noting what made the duplicate result trustworthy: I compared against scrambled versions of the
same data rather than against zero, and split it by how often each word appears. Without that, rare
words seen once or twice would have looked like duplicates of each other and I would have invented a
problem that is not there.

## QUESTIONS

None.

## NEXT STEPS

1. **The scale question is the real one**: what does slot count cost at 10^5-10^6 sentences? Untested,
   and the only version of "capacity" this evidence leaves open.
2. Wiring the proven three tiers into the read path still needs a measured target before it is done.
3. Sleep as decay or dedup is not warranted on current evidence and should not be built on assertion.
