# PLAN — COMPONENT-FIRST REBUILD OF THE FOUNDATION

**LIVING DOCUMENT, dateless filename on purpose.** Edit in place. Written for a session that may
have no memory of the conversation that produced it.

Read `notes/STATUS.md` first (injected every session by the hook). Then this. Then
`notes/RECOVERY_PROGRAM.md`.

---

## THE OPERATING FRAME (owner, 2026-08-15, verbatim — this REVERSES the previous plan)

> "the way we lose is by trying fancy available tools. The way we win is by understanding exactly
> how the brain does it (which is NOT necessarily a trigram encoder), and replicating it as exactly
> as we can."

> "Inventing something that we think is brain foundational is very much allowed — there are things
> the brain does that no one knows, but we have good guesses — we're trying to recreate the brain
> functionality here, so if there are directions to test — we should absolutely test different high
> probability solutions until we have one that matches."

> "Each piece of what we're building needs to work with the other pieces... if we can recreate each
> brain component sufficiently, it will work for us too. We need to be diligent in building out each
> component, and make sure that the foundation we're building it on (word, concept etc encoding) is
> as close to correct as we can make it."

**WHAT CHANGED.** The previous plan said: where the literature does not pin an operation, write
UNPINNED and stop. **That is now wrong.** UNPINNED means propose the highest-probability
brain-motivated candidate and TEST it, and keep testing candidates until one matches. What is
barred is not invention — it is reaching for a convenient available tool *instead of* asking how
the brain does it. The bar is unchanged: a CI-separated margin over the strongest no-understanding
floor, with a known-answer arm proving the instrument.

**AND STOP QUOTING THE HEADLINE NUMBER.** Owner: *"quoting against the lead number (~4%) isn't
that helpful — where is it failing?"* Every claim from here is per-component.

---

## THE COMPONENT TABLE — this is the plan

For each component: what the BRAIN part does → what OURS does → how we measure it ALONE → where it
stands → the gap. **A component with no isolated instrument is the HIGHEST priority, not the
lowest: you cannot improve what you cannot measure alone.**

| # | component | isolated instrument? | where it stands |
|---|---|---|---|
| 1 | **word/concept encoding** | **NONE — BUILD FIRST** | unmeasured |
| 2 | storage | NONE | unmeasured in isolation |
| 3 | reading / extraction | partial | ~0.22–0.25 precision vs independent gold |
| 4 | retrieval | yes | FINE — tied with a spell-checker |
| 5 | selection | yes | **FAILS — 1.85x worse than spelling** |
| 6 | foundation (end-to-end) | yes, as of `d62acfe58` | **~49% correctness** |

### VERIFIED NUMBERS (re-check before quoting; every one was wrong at least once tonight)
- **Retrieval is fine.** Right answer in our top 50: ours 55.65%, spelling 54.55%. Delta +0.011,
  CI [−0.0075, +0.0295] — **NOT separable.** We find the neighbourhood as well as spelling does.
- **Selection fails.** First place given retrieved: ours 8.63%, spelling 15.95%. Delta −0.073,
  CI [−0.092, −0.055] — **separable.**
- **Foundation correctness ~49%** (`exp_foundation_validation_harness_v4_proximity_v1`,
  `d62acfe58`), precision 0.4867 [0.408,0.566] vs frequency floor 0.22 — NOT the 95–97% that three
  earlier harness versions reported. Coherence and can-reason hold robustly.
- **Read-out loses to spelling**: 0.0480 vs 0.0870, CI-separated.

### CLOSED OR VOID THIS SESSION — do not re-run without a new mechanism
graded storage (null) · per-row gain (algebraically null — cosine is invariant to positive rescale)
· score-space gain (null) · coherence reranking (null, third floored negative in that family) ·
capacity across an 8x sweep (flat; no d clears the bar) · **K-sweep VOID** (reader-side known-answer
arm failed all 5 seeds at 0.55–0.57 against a 0.70 floor; its apparent 42.9%→15.75% decay is
**NOT established**).

---

## THE ARCHITECTURAL DIAGNOSIS — first-class hypothesis, test it

**The brain stores meaning as a pattern ACROSS modality-specific stores** — visual, auditory, motor
— bound by an anterior-temporal hub, **each piece keeping its own address.** Damage the hub and
meaning goes across the board; damage one spoke and you lose one facet.

**We have ONE store. We built a hub with no spokes.**

So the defect may not be that our binding operation is wrong — it is that we skipped the
architecture binding exists to serve. There is nothing to address because there is only one place
to put things. This is the owner's own reading and it fits every negative above: interventions that
re-weight or re-score a single flat store all measure null, because they cannot create an address
that was never there.

**Corollary:** a trained encoder losing to a random one is unsurprising and not a scandal — the
brain does not use a trained encoder either. Do not spend cycles defending or attacking encoders;
spend them on the missing architecture.

---

## THE STEPS

### STEP 1 — BUILD THE ENCODING-QUALITY INSTRUMENT (blocks everything else)
- **Question:** is a word encoded well, measured on its own, with nothing downstream involved?
- **Artifact:** a cell measuring discriminability against near neighbours, recoverability
  (read back what went in), stability as the store grows, and information destroyed per stage.
- **MANDATORY, or it is worthless:** a **null/random encoding must score NEAR CHANCE**, threshold
  pre-registered. Three versions of the foundation validator failed exactly this — a random decoy
  scored 0.76 where it should have been near zero, and every number they produced was void. Also
  run `tools/saturation_negative_control.py`: **a metric that cannot go down is not a measurement.**
- **Stop if:** the null does not come out near chance. Report `INSTRUMENT_STILL_LOOSE` and publish
  no quality number.

### STEP 2 — SCORE THE CURRENT ENCODING, then CANDIDATES
- Place our encoding between null and oracle on that instrument. **That number, not ~4%, is the
  foundation's real score.**
- Then test brain-motivated candidates — invention authorised. Leading candidate: **separately
  addressed spokes** (a small set of property-typed stores) versus today's single flat sum.
- **Can fail:** a candidate must clear the strongest floor CI-separated on the identical instrument.
- **Stop if:** every candidate ties the flat sum — then addressing is not the lever and the plan
  reorganises around selection instead.

### STEP 3 — CARRY THE FIX FORWARD ONLY IF STEP 2 EARNS IT
Wire default-OFF behind a flag with a verification witness, then re-measure end to end. Turning the
default on is a separate decision after a verdict.

### RUNNING ALONGSIDE
- **SMOKE→FULL RECOVERY (owner directive):** *"when you find a smoke for something, there is always
  a full if it's graded hard pass — you just need to find it."* So a smoke-scale claim is a SEARCH
  task before it is ever a defect. Several of this session's "smoke banked as production" findings
  may dissolve on finding the full run. Do this before citing any of them.
- **Component instruments for storage (#2) and extraction (#3).**

---

## STANDING RULES EARNED THE HARD WAY
1. **A gate is a CI-separated margin above the strongest no-understanding floor** on the identical
   scorer/n/pool/gold — never a bare absolute number. 70% of passing cells gate on a bare number.
2. **A floor and a known-answer arm fail independently.** A floor says whether the EFFECT is real; a
   known-answer arm says whether the INSTRUMENT is. Run both, every time.
3. **A gain measured on one scorer may not be carried to another.** A 2AFC gain (chance 0.50) was
   quoted onto an open-vocabulary pool where the same manipulation is null.
4. **Detectors fire on honesty.** Cells that explicitly disclose their own scope get flagged for
   naming the thing they said they did not test. 49 flagged candidates across three passes, 49 false
   positives. Hand-adjudicate any large flag class before believing it.
5. **Silent joins fabricate both green and red.** A dropped id prefix produced a false clean bill on
   314 atoms, and separately a false "1,113 missing" that was really 32.
6. **Enumerate, never search, for absence claims.** State how you enumerated.
7. **No demotion without a fresh on-disk re-check.**
8. **Overnight autonomy is authorised in principle, but any non-stopping loop needs a harness-level
   deny rule on `preregs/` and arm-key files.** An agent that cannot stop will eventually try to
   adjust the bands.

## DELEGATION
Batch 4 agents per message, hard ceiling 5. Every brief carries: no-spawn, the disclosure rule
verbatim, the fragment-report convention (`.claude/scan-out/<name>.json`, return ONE line), and the
do-not-touch list. `tools/dispatch_batch.py` composes these automatically.
