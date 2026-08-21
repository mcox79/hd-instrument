# READING GROUNDS **ZERO** -- A COLD-START DEADLOCK IN THE DEFAULT ENTRY POINT

> # ✅ **THE CAVEAT IS RESOLVED: `Substrate` CANNOT LOAD A FOUNDATION AT ALL.** (verified 2026-08-21)
> I wrote below that the deadlock might mean *"I ran it without its foundation"*. **It does not.**
> - **`Substrate.__init__` accepts `foundation_dir` -- and `self.foundation_dir` is assigned ONCE and
>   NEVER READ.** One occurrence in the whole file, at the assignment. **The parameter is dead.**
> - **`__init__` ALWAYS builds a fresh `HDFactStore` and a fresh `ReadingLoopState`**, then seeds 107
>   words. **There is no load method** -- the public surface is `read`, `query`, `recall`,
>   `consolidated`.
> - **And the capability EXISTS and works.** `foundation_persistence.load_foundation()` loads six
>   saved foundations cleanly: **4,322 / 1,415 / 907 / 781 / 738 / 360 anchors.**
>
> **➡️ SO THE SUBSTRATE CANNOT BE GIVEN THE ANCHORS IT NEEDS, THROUGH ANY DOCUMENTED ROUTE. The
> deadlock is not "I ran it wrong" -- there is no way to run it right.** *A `save`/`load` pair exists
> and passes its own witness (`R3: "the foundation survives a restart"` = FILLED); the SUBSTRATE
> simply never calls the load half.*
> **That makes this the sharpest instance of WIRE-DON'T-ISLAND in the repo: the system cannot read its
> own saved knowledge back in.**

**Owner: *"Why did we stop working on reading?"*** The answer is sharper than "we drifted".
**`Substrate().read()` with defaults grounds nothing, ever, and the mechanism is circular.**

| reads on ONE substrate (state accumulates) | sentences | flagged | **GROUNDED** | refusals |
|---|---|---|---|---|
| call 1 | 1,200 | 11,070 | **0** | 509 |
| call 3 | +180 | 715 | **0** | 858 |
| call 6 | +420 | 1,770 | **0** | 1,871 |
| **cumulative** | **3,120** | -- | **0** | **1,871** |

---

## 1. 🚨 THE MECHANISM IS A DEADLOCK, AND IT IS VISIBLE IN THREE NUMBERS

| observation | value |
|---|---|
| concept anchors in a FRESH substrate | **0** (seed vocab 107, library items 0) |
| anchors after 600 sentences | **82** |
| dominant refusal | **`TAUTOLOGY_NO_ANCHOR`** -- *"no anchor in the concept space was close enough"* |
| best cosine at refusal | median **0.350**, max **0.447** |

**`ConceptSpace` grows from two sources only:** seeded known words, and **words seeded ONCE AT
GROUNDING TIME**. So:

> **Grounding requires an anchor close enough to canonicalize against.
> Anchors grow when something grounds.
> Nothing grounds, because no anchor is close enough.**

**➡️ THE CONCEPT SPACE CANNOT BOOTSTRAP FROM ZERO.** *After 600 sentences it holds 82 anchors --
essentially the seed vocabulary's coverage and nothing more. My own diagnostics, which call
`observe()` on every content lemma directly, reach 4,250 anchors on 4,096 sentences. The reading
path builds ~50x fewer because the gate that would add them never opens.*

## 2. ✅ **THE CAVEAT IS SETTLED, AND IT WENT THE WORSE WAY** *(see the banner at the top)*

**Facts HAVE been banked historically** -- the 402 provenance rows exist and were hand-scored -- so
grounding is not incapable. **I therefore checked whether the substrate simply needed its foundation
loaded. It cannot load one.** `foundation_dir` is assigned once and never read; `__init__` always
builds a fresh store and state; there is no load method. **Meanwhile `load_foundation()` works and
returns up to 4,322 anchors against the deadlocked substrate's 82.**

**➡️ THE CLAIM IS THEREFORE NO LONGER HEDGED: the default entry point cannot be given the anchors it
needs by any documented route.**

## 3. WHAT IS NOT THE PROBLEM -- MEASURED, SO IT IS NOT RE-INVESTIGATED

- **NOT a read cap.** `read()` visits `max_patches=4` patches of ~300 sentences = **1,200 per call**,
  by design; repeated calls advance the patch cursor. *Asking for 5,000 returns 1,200, which is the
  parameter working, not a silent truncation.*
- **NOT the forager leaving early.** Its leave rule is novel-lemmas-per-sentence and it visited 4
  corpora. *That is marginal-value-theorem behaviour, correct by its own spec.*
- **NOT gate strictness alone.** Only **~32 of 2,164** flagged episodes even REACH a gate decision.
  *The other ~98% never produce a candidate. Loosening the gate would change almost nothing.*

## 4. 🎯 WHAT THIS DOES TO THE WIRING BACKLOG

**I was about to argue for wiring `three_tier_loop`**, whose middle tier retains gate-failures and
re-queries them first -- exactly the owner's *"never throw out useful information"* and *"hierarchical
memory"*. **That is still the right shape. But it would currently retain ~32 items per 300 sentences,
not thousands**, because almost nothing reaches the gate to be retained. *Wiring it now would connect
a good mechanism to a stream that is nearly empty.*

**The bootstrap comes first.** *That is the second time today that measuring before proposing changed
the target -- and this one I caught before writing the brief rather than after.*

## TLDR

You asked why reading stalled. **The system reads, flags thousands of things to learn, and grounds
exactly zero of them — across 3,120 sentences and six sessions, the count never left zero.**

The reason is circular, and it shows up in three numbers. To learn what a new word means, the system
compares it against concepts it already holds. Those concepts only get added when something is
successfully learned. **So it cannot get started from nothing: it needs concepts to learn concepts.**
After 600 sentences it holds 82 concepts — essentially just the 107 words it was handed at birth.

**I checked the obvious excuse, and it made things worse rather than better.** We have a pre-built
63 MB store of knowledge on disk, and a freshly created system does not load it — so perhaps I had
simply started it wrong. **It turns out there is no way to start it right: the setting that would
load that knowledge is accepted and then completely ignored, and there is no other method to do it.**
Meanwhile the loading code itself works fine and returns over four thousand concepts, against the
eighty-two the running system has. **So the system cannot read its own saved knowledge back in.**

Three things I ruled out along the way so nobody re-investigates them: it is not reading too little
(the limit is a deliberate setting), the forager is not quitting early (it is behaving exactly as
specified), and it is not the quality bar being too strict — **98% of candidates never even reach the
bar.**

This also changes what I was about to recommend. The tiered memory you asked for keeps hold of things
that fail the bar instead of discarding them, which is right — **but right now only about 32 things
in 2,164 reach the bar at all.** Connecting it today would attach a good mechanism to an almost empty
stream. **The bootstrap has to come first.**

## QUESTIONS

None. The foundation-loading check is done and is in the banner.

## NEXT STEPS

1. **Wire `load_foundation()` into `Substrate`** -- the dead `foundation_dir` parameter is the
   obvious seam, and the function already works. This is the sharpest WIRE-DON'T-ISLAND case here.
2. If the deadlock survives that, the bootstrap is the top item and outranks all wiring.
3. `three_tier_loop` stays the right shape, but behind the bootstrap.
