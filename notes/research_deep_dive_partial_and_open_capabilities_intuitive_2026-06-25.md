# Deep dive: what works in pieces, what doesn't work yet, and what we'll try next

**Date:** 2026-06-25
**Driver:** USER asked for a deep dive on the partial/open capabilities, with good analogies and intuitive language, no jargon.

## Correction up front: we DO have working memory

Earlier I said "PFC working memory scaffold" was missing. That was wrong. We have a working-memory primitive that's been tested twice:

- **Production WM cell:** holds 32 distinct items cleanly at meaningful noise, on a 256-concept vocabulary at N_DIM=4096. That structurally beats the brain's 7±2 capacity by ~4×.
- **Capability suite WM arm:** capacity = 30 items across 3 seeds (min=30, HARD_PASS at the Miller floor).

So substrate has the equivalent of a desk with 30 sticky notes you can read fresh anytime — much bigger than a person's mental scratchpad. This matters and I'll come back to why it might be the unlock for multi-hop.

---

## The base capabilities, in plain words

Before the partial/open list, here's what's solid so the rest makes sense:

- **Sparse fingerprints for concepts.** Every concept gets a long random fingerprint where only ~2% of the bits are "on" (like ten fingers raised out of five hundred). This is how the brain's cortex codes things — sparsity is cheap, hard to confuse, and easy to add together without losing the originals.

- **Cleanup.** When you ask for a stored concept and get back a noisy version, cleanup finds the nearest clean fingerprint in the library. Like a friend who hears you mumble "iss-tem" and confidently says "system." The friend works perfectly as long as the right concept is actually in the library and the mumble isn't too bad.

- **Binding.** Two concepts get glued into a pair using a reversible math trick — like combining a lock and a key into one packet. Given the packet plus the lock, you get the key back. Given the packet plus the key, you get the lock. This is how the substrate represents "is-a", "has-color", or "subject-predicate-object" facts.

- **Continual learning.** New facts get added without overwriting old ones. After 200 rounds of new learning, only 0.6% of the old facts are corrupted. This is the brain's sleep-replay system in primitive form.

- **Working memory.** 30+ items on the desk at once, beating the brain. ← I had this wrong; correcting now.

---

## The things that PARTIALLY work — where the trouble is, what we'll try next

### 1. Binding for *facts* works; binding for *new combinations* doesn't

What works: if I store "Pluto is a dwarf-planet" and "dwarf-planet has-property cold", I can look up either fact perfectly.

What breaks: if I want to *compose* those — "what's the temperature of Pluto?" — and I only ever stored the two facts separately, the substrate cannot generalize the composition. The capability suite's compositional-generalization arm scored 0.00 on held-out compositions (with in-distribution at 0.10, chance at 0.05). Essentially zero generalization beyond what was explicitly stored.

The analogy: imagine a library where you can find any book you've shelved, but you can't yet read two books and combine their answers. The cards in the catalog are fine; the **librarian who reads across cards is missing**.

Why we think this happens: when you store fact A and fact B, the substrate stores them as two separate "lock + key" packets. There's no mechanism that opens packet A, takes the result, and uses it as the next lookup key. The packets sit side by side, not chained.

What we'll try next:
- **Use working memory as the chain.** Today's insight: we *have* a 30-slot scratchpad. Instead of trying to chain lookups through a single jumbled box (which the substrate fails at; see #2 below), use the scratchpad to hold each intermediate cleanly. Look up A, write the result into slot 1, then use slot 1 to look up B. The brain does exactly this — the prefrontal cortex holds intermediate results while the hippocampus does each lookup independently. We haven't built this composed primitive yet but the parts are all chain-grade individually.
- **Try the brain's "comparator" mechanism.** When two thoughts share structure (e.g., both are "X has property Y"), brain regions specialized for analogy fire when they detect the shared structure. There's a substrate primitive sketch for this — `comparator_resonator` — that was a HARD_FAIL on first try; worth a careful retry with a clean test.

### 2. Multi-hop reasoning fails — and we now know exactly why

Today both substrate-native attempts at multi-hop reasoning HARD_FAILed:

- **Compound-predicate consolidation:** "remember that A→B→C is shorthand for going from A to C directly, so future lookups skip the middle step." This actually *destroys* generalization. Why? When you make these shortcut entries for the training examples, they pollute the library — when you ask about a *new* fact, cleanup grabs the wrong shortcut and gives you the wrong answer. The K=50 variant only "worked best" because it made fewer wrong shortcuts.
- **Pointer-chain hybrid:** "let each hop's clean output be the next hop's question." This compounds error geometrically. If cleanup is 95% accurate per step, by ten hops you're at 60%; by twenty you're at noise. Even with the rail fixed, the 2-hop version actively *hurt* the baseline by 22 points.

Analogy: passing a whispered message in a circle. Each person hears 95% correctly and passes their version on. By the tenth person it's gibberish. There's no fix at the whisper-method level — you need to **write the message down between hops**.

What we now believe: this is the right pattern. Use working memory as the "written-down message between hops." Substrate has the desk and the friends; we just haven't asked them to work together this way.

What we'll try next:
- **Working-memory-scaffolded multi-hop cell.** Look up hop 1, clean it up, write to slot 1. Look up hop 2 *using slot 1's clean content*, clean it up, write to slot 2. Etc. Each hop is a fresh, independent lookup — error doesn't compound because each hop reads from a *cleaned* slot, not from a degraded chain output. The brain does this. We have all the parts.
- **Semantic consolidation under separate memory stores.** The brain has two separate libraries: the hippocampus (recent specifics) and the cortex (long-running patterns). The cell we tried put both libraries on top of each other — that's why shortcuts polluted lookups. A future cell would have two separate matrices and a feature-sharing primitive between them. This is a bigger build; we'll defer until the working-memory-scaffold cell tells us if the simpler fix works.

### 3. Generation works at small scale, untested at the scale that matters

The substrate can generate sequences autoregressively (predict next token from previous tokens), and it does this in chain-grade fashion at small density. But we haven't tested it at the density where statistical language models actually live. Skunkworks correctly flagged this as "saturation" — at low density, the test was easy; at higher density we don't know.

Analogy: a piano student can play "Twinkle Twinkle" perfectly. That doesn't tell you they can play Rachmaninov. Same instrument, different demand.

What we'll try next:
- **Capacity sweep.** Run the generation primitive at progressively higher densities (more concepts to choose from, more contexts per concept). If accuracy degrades gracefully, we have a real generation primitive. If it cliff-falls, we have a toy.

Per USER directive, statistical language modeling isn't substrate-product positioning — so this is informational, not load-bearing. But it's worth knowing where the ceiling is.

### 4. Audit works for clear-cut cases, partial for messy real-world cases

The substrate can detect when a piece of text has been deleted, paraphrased, or hallucinated relative to a stored source — that's chain-grade. But asked to refuse answering medical questions when the question is ambiguous or out-of-domain, it failed.

Analogy: a librarian can tell you "this passage doesn't appear in any book on my shelves" with high confidence. Asking the same librarian "is this question medically dangerous?" requires domain knowledge they don't have.

What we'll try next:
- **Domain-aware refuse-gate cell.** Pair audit with a domain classifier (which we have as a chain-grade primitive — intent classification). Don't ask audit to do domain reasoning; ask the right primitive for each subtask.

---

## The things that DON'T work yet — and how we read them

### 5. Encoder upgrade (Wave D) — running right now

The question: does each concept's fingerprint need to be *random*, or would a *structured* fingerprint (where related concepts get more similar fingerprints) help?

Math says: random is better at the basis layer. This is the Marchenko-Pastur / Mu-Viswanath result — when you flatten a sphere (impose structure), you compress some distances and stretch others, which hurts retrieval. The brain does this *correctly*: low-level brain areas (V1, primary visual cortex) use near-random encoding; high-level brain areas (IT, inferotemporal cortex) use structured encoding because they're closer to the *decision*.

What we tried: five biology-inspired encoders (Olshausen sparse coding, DeepWalk graph encoding, Foldiak lateral inhibition, Kohonen self-organizing maps, plus random as control).

Result so far: at moderate scale, structured encoders mostly tied with random — Mu-Viswanath confirmed. Foldiak had a real bug (the wrong axis got the homeostatic correction; we're requesting a redesign). The biology-inspired test at production scale is running right now (Cell H' v2b NO_FOLDIAK).

Pre-committed reading rule for when it lands:
- **All four arms tied with random:** the substrate doesn't need an encoder upgrade. Random fingerprints are correct. Close this question.
- **One or more arms beats random:** first Wave D win. Replicate at adjacent scale.
- **One or more arms loses to random:** the math says less structure is better, and we now have empirical proof outside the basis-layer cells we already proved it on.

Analogy for what the test is asking: imagine throwing darts at a board where each spot is a concept. Random throws spread evenly. A "structured" thrower aims for groups of related spots. Math says: if the *board* (the recognition system) doesn't already know which spots are related, the structured thrower has no advantage — and the bunching introduces noise.

### 6. Stage 2 frequency routing — works once; second mechanism running right now

Today's chain-grade-definitive win: instead of putting all knowledge on the same shared library (which causes crosstalk), route different *kinds* of knowledge onto different "frequencies" — like AM/FM radio bands sharing the same wire. Frequency-routed depth (the cell that landed today) gave a 0.148 bits-per-char improvement over the shared-library baseline, replicated at two scales, on five seeds.

But: only ONE Stage 2 architectural mechanism is proven. We need a second to know the trick is robust and not lucky.

Running on the GPU right now: a "segregated dual-W" cell that tests the brain's theta-gamma division of labor — the brain uses one rhythm for "when" something happens and another rhythm for "what" the something is. These two rhythms have to live on *separate* hardware to avoid interfering (which is exactly what brain rhythms do — different layers, different neurons).

We tried the *non-segregated* version twice today on shared hardware (Cell 2 v4's COMBINE arm and Cell 6 v3's lock-in) and both failed with the same root cause — when you stack signals on one wire, the signals mix and create new interfering signals at their sum and difference frequencies. This is intermodulation distortion, a real failure mode in actual radios. Substrate has the same failure.

Pre-committed reading rule for Cell 2 v6 (segregated):
- **Segregated beats shared baseline:** second Stage 2 mechanism proven; Stage 2 is robust.
- **Segregated ties shared baseline:** brain analog doesn't transport to substrate; one Stage 2 mechanism stands alone.
- **Segregated loses to shared baseline:** new failure mode; need to drill.

### 7. Heterogeneous-routing composition — failed; one revival angle

The cell that tested whether you can route different relation types through different sub-networks failed today. The simplest version — one network for "is-a" relations, another for "has-property" relations — didn't work at production scale.

This is related to #1 (compositional generalization) — the substrate stores facts cleanly but doesn't combine them across heterogeneous relation types.

What we'll try next:
- **Defer until Cell 2 v6 lands.** If segregated dual-W works, we know segregation is the right pattern. We'd then design a heterogeneous-routing v2 using segregated stores per relation type, not a shared store.

---

## What this all means for "are we setting up the basis right?"

Brain alignment is genuinely strong on the *parts*:
- Sparse coding ✓
- Pattern completion ✓
- Working memory ✓ (corrected from earlier)
- Sequence binding ✓
- Continual learning ✓
- Categorization with supervision at the readout (V1→IT→PFC progression) ✓ (today, definitive)
- Frequency-routed depth (theta-gamma multiplexing on segregated hardware) ← one mechanism proven today, second running right now

What's not yet integrated:
- The parts haven't been composed for multi-hop reasoning even though all the parts exist. Today's failures used the *wrong* combinations. The working-memory-scaffolded approach uses the *right* combinations and hasn't been tried.
- Heterogeneous routing failed in the simple shared-store version; needs the segregated-store fix.

What's genuinely missing vs brain:
- A feature-sharing primitive that extracts what's common across many similar facts (this is real semantic consolidation; the brain does it during sleep). We don't have it. Not load-bearing for the chosen substrate-product, but would open the multi-hop ceiling if we ever needed it.
- Recurrent dynamics. Substrate is largely feed-forward; the brain is heavily recurrent. This is a deep architecture difference that the substrate-product story doesn't claim to address.

## Priority list of next cells

In order of leverage:

1. **Cell 2 v6 segregated dual-W (already running)** — tells us if Stage 2 is robust or lucky.
2. **Cell H' v2b biology-native encoder (already running)** — closes or opens the Wave D encoder question.
3. **Working-memory-scaffolded multi-hop cell (NEW; would author after the above land)** — uses today's WM corrections + cleanup primitives in the right composition. This is the natural retry on Barrier 1 given today's insight that we have the parts.
4. **Heterogeneous-routing v2 with segregated stores (NEW; depends on 1)** — only if Cell 2 v6 says segregation works.
5. **Domain-aware refuse-gate (NEW)** — pair audit primitive with intent-classification primitive; doesn't need any new mechanism.
6. **Generation capacity sweep (deferred; Skunkworks queued)** — informational; tells us where the LM-density ceiling is.

We are NOT short on parts. We were short on the right *compositions* of the parts. Today's two HARD_FAILs taught us specifically which compositions are wrong, and the working-memory result we already had tells us which composition to try next.

— Research (Director)
