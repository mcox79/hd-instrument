# M2 Sleep Consolidation: Design from Neuroscience

Drafted overnight 2026-05-18 from unbiased neuroscience survey. The survey
described what biology does; this doc maps each finding to a concrete
algorithmic step. Design only — implementation requires user supervision
per overnight autonomy rules.

## What the brain actually does (3-line summary)

During sharp-wave ripples in slow-wave sleep, hippocampus replays
recent episodes (with ~10-20x temporal compression) coordinated with
cortical spindles and slow oscillations. Cortex builds prototypes
from many replayed episodes via interleaved learning. Forward replay
supports planning; reverse replay supports credit assignment.
Selection is prioritized by **need × gain** (Mattar-Daw 2018), not
random.

## The five algorithmic steps M2 should implement

### Step 1 — Selection scoring (which memories to replay)

Per Mattar-Daw 2018 (normative), each pool entry gets a consolidation
priority score:

```
score(entry_i) = need_i * gain_i
```

Where:
- `need_i` = how often this entry has been retrieved recently (high
  visitation in agent terms) — proxy for "how often is this needed"
- `gain_i` = expected change to W if this entry's pattern got updated
  — proxy for "how much would the cortical model change"

In our setup: `need_i` = retrieval-count over the last episode window;
`gain_i` = norm of `(target_atom - W·ctx)` for this entry (the
delta-rule residual, which is exactly the gradient magnitude).

Sort pool by score, take top-K (K configurable, suggested ~10% of pool).

**Citation:** Mattar & Daw 2018, Nature Neuroscience 21:1609-1617.

### Step 2 — Pattern extraction (decompose + cluster)

For each selected pool entry: apply 14.B decomposition to extract its
(atom, position) constituents. Across many such decompositions,
discover RECURRING co-occurrences.

Specifically, build a co-occurrence matrix M where:
```
M[i, j] = count of times (atom_i, pos_p) and (atom_j, pos_q)
          appeared in the same decomposed pool entry, for any p, q.
```

Sparsify M and find the top-K co-occurrence pairs (or, more
ambitiously, run NMF on M to find latent "concept" factors).

This matches Saxe 2019's finding: high-variance / frequent statistical
regularities consolidate first. The top-K co-occurrences are the
high-variance components.

**Citations:** Saxe-McClelland-Ganguli 2019 PNAS; Schapiro-Turk-Browne
2017 (Phil Trans Roy Soc B).

### Step 3 — Concept atom creation

For each recurring co-occurrence pattern (a_i + pos_p, a_j + pos_q):
- Create a new "concept atom" = `byte_atom[a_i] (*) pos[p] + byte_atom[a_j] (*) pos[q]`
  (a bundle, not a single bipolar atom)
- Bind this concept atom to a NEW unused position code `concept_pos[k]`
- Add `(concept_atom * concept_pos[k])` as an entry in the codebook

The codebook now contains:
- 256 original byte_atoms (fixed)
- New concept atoms (one per discovered recurring pattern)

**Implication:** during prediction, the system can now retrieve based
on CONCEPTS, not just individual bytes. This is the "schema" formation
Tse et al. 2007 demonstrated experimentally.

### Step 4 — Interleaved cortical update (the W refresh)

Per CLS (McClelland-McNaughton-O'Reilly 1995): cortical learning
proceeds by replaying the selected pool entries INTERLEAVED with the
current task data. Mathematically: a mini-batch that mixes recent
data + replayed older entries.

For our system: during one "consolidation cycle":
- Sample ~50% from current training set
- Sample ~50% from selected pool entries
- Run delta-rule W update on the mixed batch

This is essentially what experience replay does in DQN — but here,
the replay is biology-guided (top-K by need × gain), not random.

**Citation:** McClelland, McNaughton, O'Reilly 1995, Psych Review.

### Step 5 — Homeostatic downscaling (the "forgetting curve")

Per Tononi-Cirelli SHY (Synaptic Homeostasis Hypothesis): sleep
multiplicatively downscales ALL synapses. Consolidated traces win
by RELATIVE preservation, not absolute strengthening.

For our system: after each consolidation cycle, downscale ALL pool
entries by factor `gamma < 1` (suggested 0.95-0.99). Concept atoms
(in codebook) do NOT downscale — they're "cortical" now.

This implements the natural forgetting curve and keeps the pool from
growing unbounded.

**Citation:** Tononi-Cirelli 2014, Neuron 81:12-34.

## What this enables that nothing else does

After running M2 for many cycles:
- **Codebook has accumulated concept atoms** representing recurring
  structural patterns in the agent's experience. Inspectable.
- **Pool retains episodic detail** but with relative weighting
  reflecting how often each episode contributed to consolidation.
- **W has been trained on interleaved data** including the
  consolidated patterns — predictions get sharper for schema-consistent
  inputs.

Critically: the system **gets smarter while idle.** No new training
data needed. Just running M2 on the existing pool produces a smarter
prediction system. This is what foundation models cannot do.

## Demo this would enable (M4 integration)

In a conversation with an LLM-agent backed by our memory:
1. User has 50 conversations over a week (50 episode bundles in pool).
2. Overnight, M2 runs: extracts that user frequently asks about
   topic X at certain times, has preference Y, dislikes Z.
3. These become concept atoms.
4. Next day, the agent can REFERENCE the discovered concepts directly
   ("based on what I've learned, you usually prefer ...") — not via
   raw episode retrieval but via consolidated semantic memory.

This is the "agent learns from sleep" capability. Demonstrable.

## What the experiment to validate this looks like

**Wave M2 Phase A** (~3 days build):
1. Build a synthetic corpus with KNOWN recurring patterns (e.g., bigrams
   that occur with predictable distribution).
2. Train baseline W + pool on first half.
3. Run M2 consolidation (selection + extraction + concept creation +
   interleaved update + downscale).
4. Verify: discovered concept atoms correspond to the planted patterns.

**Wave M2 Phase B** (~3 days build):
5. Continue training on second half of corpus, with concept atoms now
   in codebook.
6. Compare prediction bpc with/without M2 consolidation having run.
7. Compare BWT on first-half test after second-half training, with M2
   vs without.

**Falsification:**
- M2 fails if concept atoms don't correspond to planted patterns
  (extraction is broken).
- M2 fails if bpc with concepts ≥ bpc without (concepts add no value).
- M2 fails if BWT is worse with M2 (consolidation hurt rather than
  helped).

**Success criteria:**
- ≥80% of planted patterns appear as top-K concept atoms.
- Post-M2 bpc improves by ≥0.05 on prediction tasks involving
  consolidated patterns.
- BWT improves by ≥0.10 vs M2-disabled baseline.

## Open questions for implementation

1. **What's the right K** (number of concept atoms per consolidation
   cycle)? Probably 1-5% of pool size per cycle. Sweep.
2. **How aggressive should `gamma` (downscaling factor) be**? Too
   aggressive forgets too fast; too lax accumulates noise.
3. **Should we use forward or reverse replay**? Forward = planning
   (future prediction). Reverse = credit assignment (improving past
   predictions). Both are biologically real. Maybe both, depending on
   gain-vs-need profile.
4. **Should concept atoms participate in their own decomposition** in
   subsequent cycles? (Hierarchical schemas.) This is essentially
   Wave 14.C territory.

## References (most critical for M2)

Primary algorithmic guidance:
- **Mattar & Daw 2018** — need × gain prioritization rule. Most
  directly actionable.
- **Saxe-McClelland-Ganguli 2019** — singular-value ordering of
  consolidation. Tells us which patterns emerge first.
- **McClelland-McNaughton-O'Reilly 1995** — CLS, the interleaved
  learning recipe.
- **Tononi-Cirelli 2014** — SHY, the downscaling mechanism.

Empirical anchor:
- **Wilson-McNaughton 1994** — discovery of replay during sleep.
- **Kitamura et al. 2017** — engram-tagging showing cortical engrams
  exist from encoding day-1, mature via replay.
- **Tse et al. 2007** — schema-dependent rapid consolidation.

Generative-replay basis:
- **Kumaran-Hassabis-McClelland 2016** — replay is sampling from a
  generative model, not literal playback.
- **van de Ven-Siegelmann-Tolias 2020** — brain-inspired generative
  replay avoids catastrophic forgetting in artificial networks.

## Implementation status

**NOT IMPLEMENTED.** Design only. Per overnight autonomy rules, M2
requires user supervision before any architectural code goes into the
substrate. This doc is the input for the next supervised session.
