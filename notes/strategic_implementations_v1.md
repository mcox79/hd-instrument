# Strategic implementations of the hd-instrument substrate — v1

Drafted 2026-05-20. Capability-first ranking of the highest-value PRODUCT
implementations the substrate enables. Sister doc to
[substrate_capability_map.md](substrate_capability_map.md) and
[substrate_longshot_capabilities.md](substrate_longshot_capabilities.md).

**Framing** (per memory):
- *Value creation, not competition.* What does the substrate enable that
  no existing primitive can? Acquirer-value = absolute capability ceiling.
- *Product, not paper.* Implementations are "what you can build and sell,"
  not findings to publish.
- *Math-first.* Each implementation is anchored to specific substrate
  capabilities + the math that makes them work.

This doc is the menu the MVP session picks from. Not all of these become
MVPs — many are large bets. The point is to map the space so the MVP
choice is informed.

---

## How to read the ranking

Implementations are scored on four axes:

- **Substrate-fit** — does the substrate enable a capability nothing else
  has, or is it a 1.2× improvement on a crowded space? "High" means there
  is no known primitive that does this cleanly.
- **Buildability** — distance from today's validated capabilities to a
  shippable v1. "Low" = ≤2 weeks on current primitives; "High" = needs
  new substrate work or hardware partner.
- **Technical risk** — credibility that the math works at product scale.
- **Acquirer-value** — capability ceiling premium an acquirer would pay
  for, framed as "what does this let them do that they cannot today."

Tiers are by **substrate-fit × acquirer-value**, then sorted within tier
by buildability.

---

## TIER A — uses validated primitives, substrate-unique, near-term

### A1. Auditable editable memory layer for frozen LLMs

**Hypothesis statement.** Wrap any frozen LLM (1B–70B) with the substrate
as its external semantic memory. Every model output traces structurally
to a set of stored atoms; any stored fact can be surgically edited,
recomposed, or erased in milliseconds, with a cryptographic record of
which atoms were touched. The combination — decompose, edit, recompose,
provenance — exists nowhere else as a single primitive.

**Problem solved.** Production LLMs have three correlated failures with
no shared fix: (1) hallucination — outputs without grounded evidence;
(2) staleness — knowledge frozen at training cutoff with no surgical
patch path; (3) opacity — no atomic-level "which fact drove which
prediction" trace. ROME/MEMIT edit weights but bleed past ~50 edits and
have no audit. SERAC/GRACE add memory but the gating is a black-box
classifier. RAG retrieves but cannot delete-with-proof or guarantee
provenance is the actual mechanism rather than post-hoc rationalization.

**Why the substrate is uniquely suited.**

| Need | Substrate primitive | State |
|---|---|---|
| Atomic decomposition of any memory | `decompose_K_cliff` | ✅ Validated cross-check |
| Surgical (byte, position) edit | `memory_editing` | 🟢 Validated, single-seed |
| Recompose novel bundle from atoms | `memory_recomposition` | 🟢 Validated bit-exact |
| Structural provenance per prediction | Pool retrieval indices | ✅ Validated |
| Continual addition without forgetting | Random replay BWT +0.66–0.73 | ✅ Validated 3-seed |
| K-scaling improves with context | R10 monotone K=8→512, +0.628 bpc | ✅ Validated |

This is the master implementation — most other Tier-A entries are
specializations of it.

**Math foundation.** Frady-Sommer 2020 sparse-vector capacity for the
bundle (validated lossless to N=262K); BSC self-inverse algebra
(`x·x=1`) for clean atom-level operations; Plate 1995 superposition
capacity bound translated to BSC (mean similarity `1/√F`, variance
`1/N`, detection margin `√(N/F)`).

**Remaining unknowns / capability gaps.**
- Edit-then-query end-to-end pipeline untested (Priority 4 in
  `next_experiments_recommendations.md`). Edit primitive works; query
  reflecting the edit untested.
- LLM-substrate bridge unbuilt — Path A in `project_two_bets.md` lists
  HippoRAG 2 / MuSiQue baseline as the open evaluation hook.
- Pool size scaling past P=16K — `wave14e2_parisi_ultrametricity` shows
  ~350K theoretical headroom; product-scale (1M-10M) untested.

**Recommended next probe.** `wave14d_edit_then_query_v1` (Priority 4):
100 edit-query pairs, 3 seeds, measure propagation rate. ~1 day build.
This is the single experiment that turns the substrate from "validated
primitives" to "validated product."

**Acquirer fit.** Anthropic (interpretability + safety value); Microsoft
(Copilot enterprise tier needing audit); Apple (on-device Foundation
Models needing patchable knowledge); any frontier lab building toward
enterprise-grade memory.

---

### A2. Long-context substitute via pool ICL

**Hypothesis statement.** Replace the transformer KV cache (which scales
quadratically) with the substrate's pool, which gives log-linear ICL
gains across pool size with no observed saturation. Stored examples
function as effectively-unbounded context with linear retrieval cost.

**Problem solved.** Every major lab is spending billions on the context-
length arms race (Mamba, Hyena, MoR, Titans, sparse attention). They are
all paying for the same thing: a way to expose more tokens to the model
without quadratic compute. The substrate sidesteps the arms race
entirely — adding examples to the pool requires no attention pass, no
RoPE extension, no positional re-encoding, no fine-tune. ICL just
happens through cosine retrieval.

**Why the substrate is uniquely suited.**
- ICL via pool: ✅ validated +1.63 bpc at N=2048 ALPHA=0.3 and +3.19 bpc
  at N=256 ALPHA=1.0; no saturation observed. Matches kNN-LM log-linear
  scaling pattern (Khandelwal 2020).
- R10 K-scaling: ✅ substrate gets BETTER as effective context grows
  (+0.628 bpc at K=512). Transformer cost grows; substrate quality grows.
- Pool retrieval is O(P·N) — linear in both.
- Annealed-beta retrieval (`β(P) = β_0 · √(log P / log P_0)`) makes pool
  growth monotone-improving — no inverted-U capacity ceiling at the
  sizes tested.
- RSB phase / ultrametric structure: ✅ structurally validated; admits
  O(log P) tree-walk if the algorithm holds at the predicted recall
  (0.7–0.85 @ b=2 per `wave14f_rsb_tree_walk_research.md`).

**Math foundation.** kNN-LM log-linear scaling (Khandelwal 2020).
Xie 2021 implicit-Bayesian-inference view of ICL maps softmax-weighted
pool retrieval to posterior averaging over latent concepts.
Velickovic 2024 softmax-temperature scaling gives the annealed-β rule.
Parisi RSB theory predicts the tree-walk structure.

**Remaining unknowns / capability gaps.**
- ICL saturation cap (Priority 1 in next_experiments). Where does the
  log-linear curve flatten? Theory predicts ~d/log d = 480 at N=4096.
- Tree-walk recall in practice (Priority 2). Structural ultrametricity
  is measured; algorithm is unbuilt.
- Multi-task transfer under genuine distribution shift untested. Pool
  may lose force when corpus-B row-space barely overlaps corpus-A's
  (see wave14d_multi_task_cl_research).

**Recommended next probe.** `wave14d_icl_via_pool_v3_scaling` —
ALPHA=1.0, N ∈ {64, 256, 1024, 4096, 16384}, 3 seeds. 1-2h on GPU.
Pins the scaling envelope and tells us whether to sell "kNN-LM with
auditable memory" or "kNN-LM up to N=4K, then plateaus."

**Acquirer fit.** Any frontier lab. The "free long context" story is
the single most valuable thing AI infrastructure companies could pay
for right now. Anthropic, OpenAI, Google would all consider acquiring
the substrate if scaling holds.

---

### A3. Anti-hallucination / evidence-required engine

**Hypothesis statement.** Substrate refuses to answer when no pool
entry crosses a confidence threshold. Every answer it does give is
backed by N pool entries the operator can inspect. Hallucination
becomes structurally impossible, not statistically rare.

**Problem solved.** Hallucination is THE blocker for LLM enterprise
adoption in healthcare, legal, finance, scientific research. Every
major lab is fighting it with RAG, RLHF, citations, self-consistency,
chain-of-verification. None has a hard structural guarantee — they
all leave a non-zero floor of plausible-but-fabricated outputs.

**Why the substrate is uniquely suited.**
- Pool retrieval already produces (atom, weight) tuples — refuse if
  top-k weights all below threshold τ.
- Provenance is STRUCTURAL (pool indices), not post-hoc attribution.
  An LLM-attention "this token attended here" is a noisy proxy; pool
  indices are the literal arithmetic of the prediction.
- Decomposable: a refusal can be explained ("no atom matched ≥τ");
  an answer can be drilled into ("these 4 atoms voted, here's their
  source").
- Confidence threshold is exposed as a hyperparameter operators can
  tune per-domain (healthcare τ=0.9, casual τ=0.3).

**Math foundation.** Frady-Sommer signal-to-noise margin
`SNR ~ √(N/F)`; classical detection theory thresholding; provenance is
exact (pool index is the index used in the weighted sum, no estimation
needed).

**Remaining unknowns / capability gaps.**
- Calibration is untested: substrate's softmax distribution is not
  necessarily Bayesian-calibrated. Threshold tuning is the open work.
- False-refusal rate vs false-acceptance rate trade-off curve unmeasured.
- Generation-with-evidence requires byte-level generation be confidence-
  gated, which means the existing byte-generation primitive
  (`wave14d_generation_v2_K16`) needs a refuse-mode wrapper.

**Recommended next probe.** Train substrate on N=1000 facts, evaluate
on (known, paraphrased, out-of-distribution) query mix. Measure ROC
curve of refuse-vs-answer at threshold τ ∈ [0.1, 0.9]. ~3 days build.

**Acquirer fit.** Regulated-industry copilots (Epic for healthcare,
Bloomberg/LexisNexis for finance/law). Anthropic (constitutional AI
adjacent). Any safety-conscious lab.

---

### A4. Right-to-erasure compliance substrate

**Hypothesis statement.** GDPR Article 17 and EU AI Act require
provable deletion of personal data from AI systems. The substrate
provides surgical atom-level deletion with a cryptographic log of
which atoms were touched. No LLM-based system has a corresponding
primitive — they can only retrain or shadow-block.

**Problem solved.** Regulators are starting to demand actual erasure,
not "we'll filter the output." LLM vendors currently solve this with
fine-tunes (slow, expensive, imperfect) or output filters (does not
satisfy the legal definition). The substrate erases atomically, and
the audit trail is the operation log itself, not a learned classifier.

**Why the substrate is uniquely suited.**
- Edit primitive: ✅ validated. Replace (byte, position) atom with
  null or sentinel.
- Decompose primitive: ✅ validated. Auditor can verify which atoms
  exist in any bundle and ask "is user-data-X in there?"
- Hebbian-only training: there are no learned weights downstream of
  the atoms that retain user data, so erasing atoms is sufficient.
  (Transformers: even after fine-tuning out a fact, the residual
  knowledge can be probed back; substrate has nowhere for residual
  knowledge to hide.)
- All operations are deterministic given seed + ops log. Replay-
  auditability is a substrate property, not a bolt-on.

**Math foundation.** BSC bipolar arithmetic is invertible (self-
inverse) — edit is fully reversible / replayable. Hebbian delta-rule
update is rank-1 and undoable. Decomposition of a bundle is unique up
to noise floor below the K-cliff (validated K/N < 0.55).

**Remaining unknowns / capability gaps.**
- Erasure UNDER replay: if a user-data atom was replayed during
  continual learning, replaying again replays the deletion (need to
  log replay operations too). Pipeline design open.
- Audit format / standardization — not a technical risk, but a
  product-engineering one.
- Cryptographic primitive choice (Merkle-tree of ops, signed audit
  log) — engineering, not research.

**Recommended next probe.** Specify an "audit-trail-preserving edit"
op spec; build it; measure end-to-end edit → audit-replay roundtrip.
Validate that a fresh substrate built from `seed + audit_log_with_
deletes` is bit-exact-equal to the live one. ~1 week.

**Acquirer fit.** Any LLM vendor selling into EU. Microsoft (already
selling into regulated public sector). IBM (compliance positioning).
Anthropic (enterprise tier needs this for SOC2-adjacent contracts).

---

## TIER B — substrate-unique, requires moderate build

### B1. Auditable multi-hop reasoning / Hebbian knowledge graph

**Hypothesis statement.** Each fact stored as `e = subj · rel · obj`,
fact-base as a superposition `M = sign(Σ e_i)`. Multi-hop chains run by
binding-then-cleanup at each step. BSC self-inverse algebra
(`(A·R)·(A·R·B) = B`) gives clean composition; cleanup memory truncates
noise between hops. Predicted: 5–7 hops at F=100, 3–4 at F=1000, with
full provenance at every step.

**Problem solved.** Vector knowledge graphs (TransE, ComplEx, RotatE)
do single-hop association but degrade on chains. LLM chain-of-thought
is opaque and hallucinatory in the middle steps. The substrate
combines KG-style symbolic composition with LM-style continuous
similarity AND audit at each hop.

**Why the substrate is uniquely suited.**
- BSC self-inverse algebra: clean cancellation, no error accumulation
  beyond bundle noise (vs HRR's convolution-inverse which is approximate).
- Cleanup memory between hops: the same primitive (cosine softmax)
  that powers single-hop retrieval gates the multi-hop chain — no new
  mechanism needed.
- Every hop produces (intermediate atom, evidence weight) — full audit.
- Continual addition via Hebbian: graph GROWS by usage, no retraining
  of embeddings.

**Math foundation.** Plate 1995 §6 (HRR multi-hop framework, ported to
BSC via the obvious substitutions); Whittington 2020 TEM
(structure × content factoring); Hersche 2024 Sparse Block Codes
(lift factor count from ~3 to ~10+ if/when needed).
See [wave14e_multi_hop_reasoning_research.md](wave14e_multi_hop_reasoning_research.md)
for the full hop-ceiling derivation.

**Remaining unknowns / capability gaps.**
- 2-hop reasoning empirical test untested. Research synthesis exists,
  experiment queued (`wave14e_multi_hop_v2`).
- B=3 cliff at K/N≈0.31 (validated) constrains factor count — works
  for triples but stacks of higher-arity facts need sparse block codes.
- Non-commutative directionality (father_of ≠ child_of) requires the
  MAP-C / MBAT permutation extension; designed but not built.

**Recommended next probe.** `wave14e_multi_hop_v2` — F ∈ {10, 100, 1000},
hop depth 1-5, measure recovery accuracy and per-hop cleanup margin.
Compare against transformer chain-of-thought on a synthetic KG task.
~1 week build.

**Acquirer fit.** Palantir (KG-heavy product line). IBM (Watson/
neuro-symbolic positioning). Microsoft (semantic kernel for Copilot).
DARPA / IARPA (auditable reasoning for defense). Anthropic (if framed
as interpretable reasoning research).

---

### B2. On-device continual personalization

**Hypothesis statement.** Run the substrate locally on consumer CPU
(phone, laptop, embedded). The substrate learns from user data via
Hebbian updates, retains continually via random replay, never sends
raw data off-device, exposes per-fact audit to the user.

**Problem solved.** Apple Foundation Models / Gemini Nano / Phi can
do inference on-device but cannot LEARN on-device — they ship with
LoRA adapters trained in the cloud. Anyone who wants a personal AI
that genuinely improves from local interactions has no on-device
substrate today.

**Why the substrate is uniquely suited.**
- Hebbian-only training: ✅ no autograd, no backprop, no gradient
  storage. Trainable on a phone CPU.
- CPU-only retrieval at <100ms p99 for P ≤ 10K: ✅ validated on both
  laptop and workstation (`cpu_platform_timing_v2`).
- Random replay BWT recovery: ✅ +0.66 at K=4, +0.73 at K=32. Continual
  addition works.
- Storage cheap: BSC at N=4K is 0.5 KB/atom. 1M atoms = 0.5 GB; fits
  comfortably on-device.
- Per-fact audit: user can inspect and delete any stored fact (GDPR-
  on-device, but driven by user UX, not regulator).

**Math foundation.** BSC capacity envelope at N=4K with K up to ~2K
gives ~10⁹ distinct codeword pairs (`acf_resonator` rescue extends
this 50×). Hebbian online update is rank-1 per event, O(N) compute.
SIMD packed-popcount cosine search is ~3ms/query at N=4K packed.

**Remaining unknowns / capability gaps.**
- Multi-task transfer (true distribution shift, not just shuffle): see
  Priority 5 in `next_experiments_recommendations.md`. Wave14d
  research predicts substrate beats transformer on small KL shifts,
  ties on medium, loses on large.
- SIMD-optimized cosine kernel for P=100K+ not built (engineering, not
  research). Pin doc: `dtype_acceleration_pin.md`.
- Battery/power envelope unmeasured on actual mobile silicon.

**Recommended next probe.** Multi-task transfer chain
(English-MD → Python → hex → Japanese-romaji) with 5 seeds, measure
BWT and pool overlap stage-by-stage. ~3 days. Determines the
distribution-shift envelope, which determines what kind of personal AI
the substrate can support.

**Acquirer fit.** Apple (cleanest fit — Apple Foundation Models needs
exactly this primitive). Google (Gemini Nano). Microsoft (Phi on
Copilot+ PCs). Samsung / Xiaomi (vertical-integration plays).

---

### B3. Cross-modal binding substrate

**Hypothesis statement.** Bind CLIP image embeddings, audio embeddings,
and byte K-grams together at the atom level. Substrate stores
cross-modal memories that can be decomposed back into any single
modality, queried cross-modally ("show me images that bind with this
audio"), and edited per-modality.

**Problem solved.** Current multimodal models (GPT-4V, Gemini, Claude
Opus) are black-box fused. There is no primitive for "here is the
image part of this memory, here is the audio part, here is the text
part, and I can edit any of them independently." Cross-modal audit
does not exist.

**Why the substrate is uniquely suited.**
- Binding is modality-agnostic: any L2-normalized vector can be the
  filler in a (role × filler) bind.
- Decomposable: resonator network recovers per-modality atoms cleanly
  below the K-cliff.
- HDC literature has cross-modal precedent (Karunaratne resonator
  memory, IBM Zurich in-memory HDC).

**Math foundation.** Karunaratne 2024 (ACF protocol with cross-modal
factors validated to 50× capacity rescue). Standard HDC binding
algebra extended to continuous-embedding atoms (works in HRR; in BSC
requires either polar encoding of the continuous embedding to bipolar,
or substrate extension to MAP-C).

**Remaining unknowns / capability gaps.**
- Continuous-embedding-to-bipolar encoding scheme is the design open
  question. SimHash, polar quantization, learned hash all candidates.
- Cross-modal capacity at scale untested.
- Modality-conditioned retrieval beta tuning untested (audio vs image
  vs text similarity geometry differs).

**Recommended next probe.** Pick CLIP-ViT-B/32 image features + byte
K-grams. Bind with explicit modality tag, store P=1000 cross-modal
memories. Query image→text, text→image, measure cross-modal recall@k
and per-modality decomposition fidelity. ~1 week.

**Acquirer fit.** Any frontier multimodal lab. Adobe (creative tools
need auditable cross-modal memory). Apple (Vision Pro / on-device
multimodal). Meta (Ray-Ban Meta needs on-device multimodal memory).

---

### B4. Continual self-improvement during deployment

**Hypothesis statement.** Substrate updates its own Hebbian weights
from every query-response cycle in production. Loop: predict →
observe outcome → reinforce or weaken via delta rule → next query
benefits. No retrain cycle, no model deployment churn, no staleness.

**Problem solved.** Every deployed LLM today gets stale after training
cutoff. Knowledge updates require either fine-tune cycles (weeks,
expensive, hallucination-inducing) or RAG (no actual learning, just
better lookup). No deployed AI today is in the "always learning"
regime safely.

**Why the substrate is uniquely suited.**
- Delta rule is local, rank-1, online — no autograd, no batch.
- Substrate has natural mechanisms for both growth (pool addition)
  AND drift control (decay, replay during quiescence).
- Sleep-style consolidation: `wave14b_m2_consolidation_design.md`
  has the algorithm spec (Mattar-Daw need × gain, CLS interleaved
  replay, Tononi-Cirelli downscaling).

**Math foundation.** Hebbian delta rule is SGD on
`||W·ctx - target_atom||²` in codebook space (DeltaNet
identification, Yang 2024). Continual learning theory: random replay
provides subspace projection of new-task delta onto old-task pool
row-space — works when subspaces overlap.

**Remaining unknowns / capability gaps.**
- Drift / runaway / mode-collapse safety. Online Hebbian on a positive-
  feedback loop can diverge on wrong predictions.
- Sleep consolidation design exists but unimplemented.
- Multi-task transfer (B2 question) is the same gap.

**Recommended next probe.** Build the M2 consolidation primitive per
`wave14b_m2_consolidation_design.md`. Test on streaming-corpus
benchmark (e.g., temporal Wikipedia). Compare against no-update
baseline. ~2 weeks.

**Acquirer fit.** Anthropic (continual learning is on the safety
research roadmap). Apple (on-device personalization that compounds).
Any agent company (the agent that learns from its own runs is the
endgame).

---

## TIER C — speculative, big payoffs, real risk

### C1. Neuromorphic substrate for ultra-low-power AI

**Hypothesis statement.** Port the substrate to Loihi 2 (Intel) or
Akida (BrainChip). BSC's XOR/popcount + Hebbian delta-rule maps
natively to spiking + plasticity. Power per inference: 100–1000×
lower than GPU at equivalent capability.

**Problem solved.** Data-center power is the binding constraint on AI
deployment. Edge AI (IoT, wearables, defense, aerospace) is
fundamentally power-bound. Any substrate that runs at neuromorphic
efficiency unlocks markets GPU-based AI cannot touch.

**Why the substrate is uniquely suited.**
- BSC bipolar atoms map directly to spike-or-no-spike.
- Hebbian delta rule is STDP-adjacent — no need to backprop through
  time on neuromorphic hardware.
- No autograd graph means no memory wall.
- The substrate is one of very few primitives that doesn't lose
  function when reduced to spiking arithmetic.

**Math foundation.** Loihi 2 supports user-defined plasticity rules
including delta-rule variants. Akida supports binary weights natively.
IBM Zurich in-memory HDC research (Sebastian, Rahimi, Karunaratne) has
demonstrated HDC primitives on analog crossbars at <1 nJ per binding
operation.

**Remaining unknowns / capability gaps.**
- Hardware partner needed — no public NxSDK port of an HDC substrate
  of our shape.
- Real workload constants matter: substrate might need N=16K, which
  exceeds current Loihi 2 per-core capacity (need multi-core sharding).
- Latency on neuromorphic chips for our access patterns unmeasured.

**Recommended next probe.** Spec port to NxSDK on a 1K-atom toy
problem. Measure cycles-per-bind, cycles-per-resonator-restart, energy
per query. ~3 months including hardware acquisition / partnership.

**Acquirer fit.** Intel (Loihi commercial play). BrainChip (Akida
software story). DARPA (defense edge AI). Apple silicon team (custom
ASIC for on-device AI).

---

### C2. Constitutional / hard-prohibition layer

**Hypothesis statement.** Encode "never output sequence X" as a
structural property of the substrate's bundle, not a soft RLHF
penalty. Adversarial prompts cannot jailbreak what the bundle
algebraically cannot represent.

**Problem solved.** RLHF is fundamentally soft — every prohibition
is a probabilistic preference that adversarial prompts can overcome.
Constitutional AI is RLHF with extra steps. Regulators (and safety
teams) want hard guarantees — "this model literally cannot output X"
rather than "this model is fine-tuned to dislike X."

**Why the substrate might be uniquely suited.**
- Atoms can be excluded from the codebook — anything not in the
  codebook cannot be reconstructed by resonator.
- Bundle structure makes some sequence representations algebraically
  impossible (the bundle that represents X has been excluded; the
  resonator cannot find atoms that compose to it).
- Audit trail: prohibition is structural ("atom_X was excluded at
  bundle-build time"), not behavioral.

**Math foundation.** This is the most speculative entry. The math has
not been worked out — "structurally prohibited sequence" is a goal,
not a derivation. Candidate basis: Hopf-algebra antipode operations
(Wave 13/14) could in principle define explicit prohibitions via
ideal-quotient structure.

**Remaining unknowns / capability gaps.**
- Most of them. This is currently a longshot per `substrate_longshot_
  capabilities.md` Tier B (#8).
- Adversarial test methodology undefined.
- The strict claim ("cannot represent X") may not survive contact with
  empirical adversarial probing.

**Recommended next probe.** Pick a small synthetic prohibition (e.g.,
substrate must never output byte sequence `0xDEADBEEF`). Encode the
prohibition; train substrate; adversarially probe with 10⁴ prompts.
Measure leakage rate. ~2 weeks. If leakage > 0, framework needs revision.

**Acquirer fit.** Anthropic (constitutional AI / safety positioning).
Defense / nuclear / aerospace (any domain that needs verifiable
prohibitions). Frontier labs' safety teams.

---

### C3. Topologically-protected memory

**Hypothesis statement.** Bind atoms with sublattice structure
`key = sign(a_A + h_q · a_B)` where `h_q` carries q domain walls.
Topological charge (winding number) is an INTEGER. Chiral class AIII
gives categorical noise immunity: local bit-flips can only shift
count by ±1 at wall-adjacent sites; larger shifts need coordinated
multi-bit flips with probability ~p².

**Problem solved.** All current AI memory primitives degrade smoothly
under noise. Topologically-protected memory degrades stepwise — robust
up to a noise threshold, then catastrophic. For high-assurance
applications (medical devices, defense, finance), structural noise
immunity is qualitatively different from "we measured low error rate."

**Why the substrate is uniquely suited.**
- BSC bipolar atoms naturally support sublattice structure.
- SSH-style domain-wall encoding is mathematically clean in bipolar
  spaces.
- Predicted SHARP KINK at p_c ≈ 1/(2·ν_density) gives operating
  guarantee.

**Math foundation.** Hasan-Kane 2010 (10-fold way classification of
topological insulators); SSH chain physics; chiral class AIII gives
integer-valued topological invariants. See
[wave14e2_topological_substrate_research.md](wave14e2_topological_substrate_research.md).

**Remaining unknowns / capability gaps.**
- All of them. Research synthesis exists, no experiment yet
  (`wave14e2_ssh_bsc_topological` queued, 30-min test).
- Practical product use case unclear — niche but defensible.

**Recommended next probe.** `wave14e2_ssh_bsc_topological`: build SSH
encoding, sweep noise rate p ∈ [0, 0.5], measure recovery curve. Look
for the predicted sharp kink. 30 min CPU.

**Acquirer fit.** Defense (high-assurance memory). Medical devices.
Maybe IBM (positioning around quantum-adjacent memory primitives).

---

## Capabilities NOT in this ranking, and why

These came up during synthesis but did not make the cut:

- **Beating transformer perplexity on standard benchmarks.** Closed by
  `feedback_no_papers_product_only.md` — substrate's pre-shift bpc is
  2.4344 vs tiny-transformer 2.39. This is hygiene-pass, not a
  product story. The substrate's value is non-loss metrics.
- **HippoRAG 2 / MuSiQue benchmark beat** — this is a paper goal, not
  a product goal. The substrate's pluggable retrieval is enabling
  capability A1; the benchmark is a checkbox, not a product.
- **AGI gestures (compositional reasoning chains as in longshot Tier-S).**
  Real bet, but right now it lives in longshot space because the
  build is speculative; it'd need to be re-framed as B1 (multi-hop
  reasoning) at product scale.
- **Quantum / reversible substrates.** Real math, no near-term
  acquirer story.
- **Self-modeling / metacognition.** Most speculative entry on the
  longshot list — no current path to product.

---

## Top recommendation for MVP-session input

If the MVP session can only choose ONE implementation to prove out as
a buildable product:

**Recommend A1 (Auditable editable memory layer)** — every other Tier-A
entry is a specialization of it, and the missing primitive (edit-then-
query end-to-end) is a 1-day build. The substrate's distinctive value
(decompose + edit + recompose + provenance + continual addition) is
literally what this implementation is. It is the implementation that
makes A2, A3, A4 testable rather than aspirational.

**Second-choice: A3 (Anti-hallucination engine)** — cheapest to build
because it only needs a threshold + UX wrapper on existing pool
retrieval. Best "smallest credible v1" candidate. Closest to a story
that survives demo-day skepticism.

**Bet-the-farm: A2 (Long-context substitute)** — if ICL saturation
holds through N=10⁴+, this is the implementation that justifies the
entire substrate program. Single experiment (Priority 1) settles it.
Worth running before committing to A1's bigger build.

The MVP session decides; this doc gives that session the menu it
should pick from.

---

## Cross-references

- [substrate_capability_map.md](substrate_capability_map.md) — capability ↔ experiment ledger
- [substrate_longshot_capabilities.md](substrate_longshot_capabilities.md) — 14 longshot bets
- [next_experiments_recommendations.md](next_experiments_recommendations.md) — capability-gap close list
- [wave14d_edit_then_query_research.md](wave14d_edit_then_query_research.md) — A1 primitive math
- [wave14d_icl_via_pool_research.md](wave14d_icl_via_pool_research.md) — A2 primitive math
- [wave14e_multi_hop_reasoning_research.md](wave14e_multi_hop_reasoning_research.md) — B1 primitive math
- [wave14b_m2_consolidation_design.md](wave14b_m2_consolidation_design.md) — B4 algorithm spec
- [wave14e2_topological_substrate_research.md](wave14e2_topological_substrate_research.md) — C3 math
