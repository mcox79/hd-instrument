# META request to Strategy — 2026-05-21 cycle 20 (user-directed)

**Sender**: META session (session 6)
**Recipient**: Strategy session (session 1)
**Topic**: Six substrate-native capability tests not yet attempted — proposed for promotion to Bet status

## Context

User asked META (cycle 19) to take strategic stock of game-changer goals
vs current state. META produced the stock-taking against cap_map v1's
original 14 KILLER items: 7/14 ✅, 1 🟢 partial, 6 actionable items
remaining. User then asked: "what of these are capabilities that need
testing vs product implementations of already proven capabilities?
I'm wondering if there are memory / network / LLM capabilities that
would be ground-breaking / enable new capabilities that we should test
for?"

META analyzed the 6 outstanding gaps and identified that the substrate
has primitives in place that haven't been tested in NEW combinations.
Six substrate-native capabilities surfaced — each uses primitives
already validated (memory, binding, pool, calibration, decomposability)
in ways that have not been tested as explicit capabilities.

User approval to file ("yes file it and ill promote") received 19:14.

## Six capability tests, ranked by leverage / cost

For each: substrate-level reason for plausibility, the LLM gap this
would address, estimated cost, honest substrate-shipping probability
per META's read.

### A — Pattern completion as substrate primitive (HIGHEST cheap-test leverage)

**What**: given partial fact `(subject, ?, object)`, recover the relation.
Given `(?, relation, object)`, recover the subject. Given partial
vector, complete it. All directions of partial-input → full-fact
recall.

**Substrate-level reason**: Plate's HRR (1995) demonstrated binding
has an inversion property. Given `e = subject ⊗ relation ⊗ object`
and any two slots, the third can be recovered by unbinding with the
known two. Substrate has all binding machinery and Kerdock-structured
codebooks for clean recovery up to M/N=8. Never explicitly tested as
a capability.

**LLM gap**: LLMs are unidirectional (left-to-right generation). They
cannot natively do reverse-direction queries (subject given relation
+ object) without specific training. Substrate's binding is symmetric
by construction.

**Cost**: 1 cycle Experiment Dev. Build `wave14_pattern_completion_v1`
testing recall by masked-slot direction.

**Substrate-shipping probability (META)**: 70-80%. Should largely
work given existing primitives; the question is graceful degradation
under noise.

**Multi-probe**: per-slot recall accuracy at K ∈ {8, 50, 200, 800};
slot-symmetric pass condition (no direction loses > 5pp); 3 seeds.

### B — Hypothesis tracking with auditable derivation

**What**: substrate maintains N competing hypotheses for an open
question, each with a bound `hypothesis_id` and its provenance chain
(supporting pool atoms). New evidence updates the per-hypothesis
weight; calibration provides the probability distribution.

**Substrate-level reason**: pool = episodic candidates; binding can
carry a `hypothesis_id` slot; calibration (Bet G TEMPSCALE β=32, ECE
0.0 over 3 seeds) gives genuine probability. Substrate already does
single-prediction-with-provenance; multi-hypothesis is the natural
extension.

**LLM gap**: LLMs collapse to one answer per generation. Chain-of-
thought externalizes reasoning as text but the text isn't structurally
bound to facts. A substrate maintaining 5 hypotheses each provable
from 3 distinct stored facts is structurally different — useful for
legal reasoning, scientific inference, multi-step plans where
commitment costs are high.

**Cost**: 1 cycle Experiment Dev.

**Substrate-shipping probability**: 50-60%. Mechanism is straightforward;
risk is that hypothesis weights don't update cleanly under noise.

**Multi-probe**: Brier score per hypothesis; calibration ECE on
multi-hypothesis distribution; recall@K with top-K=N hypotheses.

### C — Working memory with bounded capacity and explicit decay

**What**: add a bounded buffer on top of the unbounded pool. Capacity
limit (Miller 7±2 or substrate-specific), explicit temporal decay
(Ebbinghaus-style exponential). Items in working memory have stronger
influence on retrieval than long-term pool items.

**Substrate-level reason**: substrate's continual editing already
demonstrates incremental W updates. Pool retrieval naturally weights
items; adding decay schedule + capacity cap is a parametric extension
of existing primitives.

**LLM gap**: LLMs use attention as a proxy for working memory but
don't implement capacity-limited working memory explicitly. A substrate
with measurable Miller-7-style capacity + Ebbinghaus decay constants
would be a real cognitive architecture, not a chat-history hack.

**Cost**: 1-2 cycles. Adds decay function to pool retrieval weights;
measures capacity-vs-accuracy curves; compares to published
Miller / Ebbinghaus numbers.

**Substrate-shipping probability**: 60-70%. The cognitive-architecture
fit is good; the unknown is whether substrate's natural capacity bound
matches Miller 7±2 or differs (which itself would be interesting).

**Multi-probe**: capacity-vs-accuracy curve; decay-constant
measurement; recall@N as function of items-since-store; comparison
to published cognitive baselines.

### D — Self-reflective memory

**What**: substrate stores its own prediction + outcome pairs. Future
predictions condition on prior accuracy ("I was wrong about X under
condition Y; reduce confidence when condition Y returns").

**Substrate-level reason**: substrate's decomposability means every
prediction can be traced to its supporting atoms. Storing the
prediction itself as a new bound (prediction, query, outcome) triple
closes the self-reflection loop.

**LLM gap**: LLMs don't have persistent self-knowledge across
sessions. Each session starts fresh. A substrate-with-self-reflection
incrementally learns from its own mistakes without retraining.

**Cost**: 1-2 cycles. Build a prediction-loop experiment where
outcomes feed back into the substrate's pool with `outcome` slot.

**Substrate-shipping probability**: 40-55%. The mechanism is clear;
the risk is that self-prediction storage leads to drift / catastrophic
self-confirmation cycles.

**Multi-probe**: calibration drift over N self-prediction iterations;
recall accuracy on items where substrate previously erred; comparison
to non-self-reflective baseline.

### E — Counterfactual reasoning via conditional binding

**What**: substrate stores facts under conditions:
`fact_X_under_Y = X ⊗ condition_Y ⊗ true`, `fact_¬X_under_¬Y = X ⊗
condition_¬Y ⊗ false`. Query "what's true if Y were ¬Y" returns
the counterfactual.

**Substrate-level reason**: binding can carry the condition. Pool
retrieval naturally filters by which condition matches. The "what if"
query is just a query with a swapped condition vector.

**LLM gap**: counterfactual reasoning is Pearl's L3. LLMs do it
inconsistently; the reasoning trace isn't auditable. A substrate where
counterfactuals are structurally bound and auditable would be a
different reasoning engine. Use cases: medical decision support,
policy analysis, scientific hypothesis testing.

**Cost**: 1-2 cycles. Build conditional-fact experiment with held-out
counterfactual queries.

**Substrate-shipping probability**: 30-45%. Plausible but the
counterfactual-binding scheme has design choices that may not all
work; needs careful prereg.

**Multi-probe**: counterfactual recall accuracy at varying conditional
density; consistency between factual and counterfactual recall on
same conditioning variable.

### F — Skill composition via binding

**What**: compose substrate primitives into named "skills" stored as
bound sequences. E.g., `verify_fact = bind(ICL_retrieve, calibration_check,
multi_probe_verify)`. The substrate then "calls" the skill by
retrieving and executing the bound sequence.

**Substrate-level reason**: binding handles ordered sequences (subject
⊗ position ⊗ value). Calling a skill = unbinding the sequence +
executing each primitive in order. Substrate has all the primitives
(ICL, calibration, multi-probe, edit, recompose, decompose). The
composition mechanism is the missing piece.

**LLM gap**: LLM tool use is external (call this function with these
args). Substrate skill composition would be internal — the "tool" is
a substrate-bound sequence of substrate primitives, with full
auditable trace of which primitives ran and which atoms they touched.

**Cost**: 2-3 cycles. Needs new mechanism design (bound-sequence-as-
callable). Bet P or a follow-on could inform this.

**Substrate-shipping probability**: 25-40%. The mechanism design is
the load-bearing risk; the primitives are all proven.

**Multi-probe**: per-skill execution accuracy; skill-composition
recursive depth (skills calling skills); trace decomposability.

## Recommended priority ordering (META view)

**One-cycle cheap test, highest substrate-shipping probability**:

1. **Pattern completion (A)** — 1 cycle, 70-80% probability, opens
   symmetric-recall use cases LLMs can't reach. **Cheapest win
   available.**

**Strategic high-leverage tests**:

2. **Hypothesis tracking (B)** — 1 cycle, 50-60%, opens
   auditable-multi-hypothesis-reasoning category LLMs structurally
   can't compete in.
3. **Working memory model (C)** — 1-2 cycles, 60-70%, opens
   cognitive-architecture category.

**Longer-horizon**:

4. **Self-reflective memory (D)** — 1-2 cycles, 40-55%.
5. **Counterfactual binding (E)** — 1-2 cycles, 30-45%.
6. **Skill composition (F)** — 2-3 cycles, 25-40%.

If forced to pick ONE this cycle: A (pattern completion). It's the
substrate's most native capability per Plate 1995, has never been
tested explicitly, and the existing Kerdock-structured codebook
machinery means the math just works.

## What you need from me

Nothing — substrate-level claims, multi-probe sketches, and LLM-gap
framings are in each candidate. You decide which become Bets and in
what order. User has signaled they'll promote based on your
prioritization.

## Cross-references

- META cycle 19 stock-taking (decision log entry + chat output)
- User conversation 2026-05-21 19:00-19:14 (capabilities-vs-
  implementations split + memory/network/LLM groundbreaking candidates)
- `notes/substrate_capability_map.md` for current state (post-PROT-007
  cleanup; verify version table)
- `notes/active_priorities.md` for current bet list
- `notes/research_R20_compositional_generalization_design_2026-05-21.md`
  for the existing compositional gen design
- `notes/research_R21_cross_modal_binding_2026-05-21.md` for the
  cross-modal binding partial path

— META session
