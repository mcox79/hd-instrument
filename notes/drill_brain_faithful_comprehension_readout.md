# Drill: brain-faithful readout for comprehension (row 4 ledger) — DESIGN ONLY, no build/dispatch

Re-dispatched 2026-07-29 (prior run interrupted by overnight process exit, nothing saved). Scope: row 4
of `notes/component_brain_fidelity_ledger.md` (READOUT/decoding) — design a brain-faithful,
glass-box, substrate-native structure-preserving readout, judged on the READOUT'S OWN brain metric
(calibration-first: known reader passes; role-general order/relation decoding), NOT a downstream
task-win. This is a design note; no code is built or dispatched from this drill.

Ledger row 4 status at drill time: IMPROVING (was UNFAITHFUL; learned bilinear/probe readout fix
measured +0.038 mean AUC, cross-boundary +0.21 VET-pending). Gap named in the ledger: "linear where
brain is nonlinear+attentional; mean-pool order-blind." Brain metric: calibration-first construction
(known reader/MiniLM passes >=0.70 AUC or +0.15 acc over scrambled) + role-GENERAL (not
absolute-position) order/relation decodability.

---

## 1. BIOLOGY — how the brain reads population codes for relational/order/comprehension content

**Mixed selectivity + high-dimensional nonlinear readout (Rigotti, Barak, Warden, Wang, Carnevale,
Miller & Fusi, Nature 2013, "The importance of mixed selectivity in complex cognitive tasks").**
PFC neurons encode NONLINEAR (multiplicative/conjunctive) combinations of task variables, not a
weighted sum of them. The mathematical payoff: a population with high-dimensional nonlinear mixed
selectivity supports linearly-separable readout of ANY downstream function of the task variables,
including non-linearly-separable ones (XOR-class problems) — by a SINGLE downstream linear
readout layer. The nonlinearity lives in the population code's construction (upstream), so what
"reads" it can stay linear/simple DOWNSTREAM of that nonlinear expansion — but the expansion itself
must be present, and per Dang/Jaffe/Qi/Constantinidis (2021, J. Neurosci 41:7420) that nonlinear
mixed-selectivity fraction of neurons GROWS WITH TRAINING for a task that needs it (6.2%->12.3%,
p=1.13e-7) and does NOT grow for a task that doesn't (5.8%->6.7%, p=0.31) — i.e. the nonlinear
interaction structure is task-driven and partly LEARNED, not a fixed random expansion. (KB hit,
cosine=0.3125: `notes/drill_brain_nonadditive_interaction_relational_coding_bestinclass_2026-07-14.md`.)

**Attentional / gain-modulated readout.** Downstream areas don't read the whole population
uniformly — attention multiplicatively gain-modulates which subpopulation/dimensions dominate the
readout at a given moment (classic attentional-gain literature, e.g. Reynolds & Heeger normalization
model; task-relevant dimensions are up-weighted, not summed flatly). This is the biological
analog of "attention-pooling" vs "mean-pooling": a content-dependent WEIGHTED combination, where the
weights themselves are a function of the query/context, not fixed.

**Learned, plastic decoders — NOT a fixed geometric rule.** Downstream readout weights are
themselves synapses, tuned by experience/task (this is literally what a "decoder" is in BCI
population-decoding work, and is the direct analog of our "fixed cosine-NN is unfaithful" finding —
a fixed inner-product/cosine readout assumes the SAME projection direction is optimal for every task,
which the brain does not do). The already-measured `learned_relational_readout` win (rank-32
bilinear beats cosine-NN, +0.038 mean AUC) is a genuine first step down this path — but it is
STILL A LINEAR (bilinear/low-rank-linear) transform of the frozen rep, not a nonlinear one, and it
still collapses to a SINGLE fixed projection independent of what's being compared, i.e. it does not
yet have query/content-dependent gain.

**Role-general decodability (Frankland & Greene, 2015, "An architecture for encoding sentence
meaning in left mid-superior temporal cortex").** lmSTC AGENT/PATIENT decoding is invariant to
surface position (active vs passive voice) — the same neural code decodes "who did what to whom"
regardless of where the agent/patient sit in the sentence. This is a BINDING/keying property, not
a readout-architecture property per se, but it constrains what the readout must be able to
decode FROM: a code that keys by semantic ROLE, not string/token position. Our own probe (07-28,
`probe_v5_bind_readout_derisk`) independently found the SAME thing from the other direction:
absolute-position binding only reaches 0.52 self-consistency vs mean-pool's 0.95 — i.e. binding by
position is close to useless; whatever the readout reads must be role-keyed content, not slot index.

**Why fixed cosine-NN and order-blind mean-pool are unfaithful, stated precisely.**
- Cosine-NN readout = a single fixed (identity) linear projection + a fixed similarity metric. It
  has no mixed-selectivity expansion (no nonlinear interaction terms available to a linear reader),
  no gain-modulation (same weighting regardless of query), and is not learned (not plastic). It is
  the "weighted sum" case Rigotti et al. show is INSUFFICIENT for XOR-class (relational) decoding.
- Mean-pool over tokens is order-blind by construction (commutative aggregation) — it structurally
  cannot carry which-argument-is-which information (an XOR-class problem: "A hit B" vs "B hit A"
  average to the same pooled vector). This is not a training deficiency, it is a representational
  ceiling built into the aggregation operator itself, which is why clause-split-concat (a token-order-
  preserving but still linear scheme) already beat it by +0.03 — even a crude nonlinearity-avoidant
  fix (concatenation preserves position, at least at clause granularity) helps, confirming order-
  blindness (not lack of information) was the specific defect being fixed.

---

## 2. TRANSLATE to our own mechanism (frozen encoder's hidden states)

Constraints (repeated from dispatch prompt, load-bearing): PRESERVE dimensionality (the slot-gate
prior design failed by compressing an entire situation down to 3 scalars, discarding almost all the
population code's capacity before the readout ever got a chance — this is the anti-lesson: don't
collapse before reading); reuse `hdlab/binding.py` for role-general binding (not position-index
binding — HRR circular convolution/FHRR elementwise-complex bind, both role-general: bind(role,
filler) is symmetric in role identity, not a positional slot); NO borrowed embedding as the meaning
organ; NO external LLM; NO bolt-on parser (the readout is a LEARNED head on OUR OWN frozen hidden
states, not a supplied comprehension mechanism).

Three components map directly from the biology to buildable pieces, in increasing order of cost:

**(a) Nonlinear expansion stage — the mixed-selectivity substitute.**
The Rigotti argument requires an actual NONLINEAR interaction term to be available to the readout,
not just a bigger linear map. Concretely: augment the existing bilinear probe
(`experiments/_learned_relational_readout.py::fit_bilinear_probe`) with an explicit low-rank
QUADRATIC term — score = cosine(Px, Py) + x^T A y (a genuine bilinear cross term between the two
compared reps, not two independent linear projections of each) — this is literally "nonlinear mixed
selectivity" in miniature: the score depends on a MULTIPLICATIVE combination of features from both
inputs, which a purely linear/additive readout cannot express (this is exactly the XOR-class gap
Rigotti's argument targets). `fit_bilinear_probe` already has the low-rank machinery (P: d->r); the
minimal extension is fitting a second small r x r interaction matrix A jointly, same TRAIN-TRAIN
leak-proof harness, same held-out-NEW eval. Cheapest lever, directly reuses code that already won.

**(b) Attention-pooled / gain-modulated readout — the aggregation-operator fix.**
Replace order-blind mean-pool with a QUERY-CONDITIONED weighted pool: given the frozen per-token
hidden states H (T x d) for a passage and a query/probe vector q (e.g. the entity/relation being
asked about), compute attention weights a = softmax(H W_a q) and pool = sum_t a_t H_t. This is
"attention is all you need"-style but SMALL — a single learned W_a (d x d or low-rank), trained on
the SAME calibration-first task, not a transformer stack. This directly implements "gain-modulated
readout" (weights depend on content/query, not fixed) and, unlike mean-pool, is NOT order-blind
IF query-relevant tokens are order-dependent in context (the weighting can differ per adjacent
occurrence of the same token type depending on surrounding context, since H_t is already
contextualized by the frozen encoder). This is the direct fix for "mean-pool order-blind."

**(c) Role-general content-keyed HRR/binding readout — for role-general (not positional) relation
decoding.**
Reuse `hdlab/binding.py::bind/unbind` (role-general, content-keyed, NOT position-index): at
comprehension time, bind each token/clause's contextualized hidden state to a small learned set of
ROLE vectors (AGENT/PATIENT/RELATION — reuse the `sequence_memory.SequenceMatrix` write primitive
for the association store, per the frontier-scoping doc's design A/C) via a LEARNED role-assignment
head (not a hand-coded parser — the assignment of which token fills which role is itself a trained
small classifier over frozen hidden states, same "learned head on frozen reps, no retrain" class as
the readout fix). Readout for "who did what to whom" = unbind(situation_vector, ROLE_AGENT) etc,
which is role-general by construction (bind/unbind commute with which position the filler happened
to sit at). This is the ESCALATION step (most expensive of the three) but is the piece that most
directly answers Frankland-Greene role-generality and is what design A (entity-slot + learned
write-gate) in the frontier-scoping doc already anticipates as the write side; this drill's payload
is doing the analogous thing for the READ/decode side.

**Ordering recommendation:** (a) is cheapest and reuses code that already won (+0.038) — do it
FIRST as a one-line-of-math extension to the existing harness. (b) is the direct fix for the
named "mean-pool order-blind" gap and is next-cheapest (one small learned matrix, same frozen
reps, no new store). (c) is the most brain-faithful for role-generality specifically but is the
most expensive (needs a role-assignment head + bind/unbind wiring) — defer to AFTER (a)/(b) are
measured, since the comprehension frontier's design A (row 5, entity-slot+write-gate) already
covers closely-related ground on the WRITE side and (c) would be redundant to build twice; better
to let design A's slot representation (once built) BE the role-keyed content that (c) would
otherwise need to construct from scratch.

---

## 3. RECOMMENDATION — single most brain-faithful + cheapest design, and the can-fail test

**Recommended: (a) + (b) combined into ONE readout cell** — "attention-pooled + bilinear-interaction
readout" (`AttnBilinearReadout`): 
1. Compute query-conditioned attention pool over frozen per-token hidden states (fixes order-
   blindness / implements gain-modulation) — replaces mean-pool.
2. Score pairs via cosine(Px,Py) + x^T A y (bilinear interaction term) — implements the minimal
   nonlinear-mixed-selectivity substitute — replaces the pure linear/bilinear-only probe.
Both stages are LEARNED heads on the frozen encoder's existing hidden states (no retrain, no new
data, no grounding, no borrowed embedding, no external LLM) — same intervention CLASS as the
already-banked learned-readout fix (+0.067-class cheap win). (c) role-keyed bind/unbind is
correctly deferred to compose with row-5's entity-slot design rather than being built in parallel.

**One-variable can-fail test on the calibration-first instrument**
(`experiments/diag_order_critical_comprehension_calib_v1.py`, extend in place per frontier-scoping
doc — keep its leak-proof split + scramble control + calibration gate):

- **Fixed:** encoder (frozen, both seeds seed_7/seed_13), data, construction, split. Only the
  readout head changes.
- **Arms:** MEAN_POOL (existing baseline) vs BILINEAR_ONLY (existing, +0.038 reference) vs
  ATTN_BILINEAR (new, this drill's design) vs SHUFFLE_CONTROL vs untrained/random-init
  ATTN_BILINEAR (mandatory structure-vs-learning control, per the frontier-scoping doc's
  random-init discipline — this session's prior random-init-beats-trained scare, 0.704 vs 0.592 on
  entity-state, means this control is non-negotiable here too).
- **Calibration gate (must pass before the comparison means anything):** MiniLM/BGE diagnostic-only
  reader clears >=0.70 AUC (or +0.15 acc over scrambled) on whatever new cross-boundary/relational
  construction this extension adds. A construction no known reader passes is broken, not measuring
  comprehension.
- **HARD_PASS bands:** ATTN_BILINEAR beats BILINEAR_ONLY (the current best, not mean-pool — mean-
  pool is already superseded) by >=+0.03 mean AUC, BOTH seeds; SHUFFLE_CONTROL at chance; untrained
  random-init ATTN_BILINEAR does NOT show the gain (structure-alone ruled out) — mirrors the
  frontier-scoping doc's HARD_PASS band exactly, applied to this specific architectural swap.
- **HARD_FAIL:** ties/loses BILINEAR_ONLY both seeds, OR untrained-ATTN_BILINEAR matches trained
  (architecture alone did it, no learning needed) -> the readout isn't the bottleneck at this
  margin; escalate attention to row 5/6 (comprehension mechanism / working memory) instead of
  continuing to spend on readout architecture.
- **MIDDLE:** +0.01-0.03 or single-seed -> do not bank; the interaction/attention terms are a real
  but marginal readout-side lever; hold as an auxiliary-loss candidate, don't gate design on it.

Cost: CPU-capable (small learned heads over already-computed frozen reps, no GPU retrain needed) —
can run in parallel with any in-flight GPU work, same profile as the original learned-readout win.

---

## 4. PRIOR-WORK CHECK (director_kb_query + substrate_query + capability_registry_query)

Concept-query run (per USER-locked SUBSTRATE-KB mandatory-before-dispatch discipline):
`bash tools/substrate_query.sh "brain faithful readout nonlinear attentional decoder mixed
selectivity role general binding"` — confidence=0.3125, top hits:
1. cosine=0.3125 `notes/drill_brain_nonadditive_interaction_relational_coding_bestinclass_2026-07-14.md`
   (Rigotti/Fusi mixed-selectivity + Dang/Jaffe/Qi/Constantinidis training-dependence — the primary
   biology source used in section 1 above).
2. cosine=0.2949 `notes/reader_chaingrade_component_dossier_scour_plus_braindive_2026-07-23.md`
   (structural-reanalysis-vs-learned-classifier framing; tangential, not directly reused here).
3. cosine=0.2832 same nonadditive-interaction drill, second chunk (Rigotti dimensionality-expansion
   argument, XOR-solvability claim — reused directly in section 1).
4. cosine=0.2812 `notes/research_brain_compositional_role_binding_structure_content_factorization_2026-07-18.md`
   (conjunctive coding / tensor-product-binding ranking — corroborates section 2c's bind/unbind
   choice as the "strongest" binding mechanism per that lane's ranking).
5. cosine=0.2812 `agreement_tem_on_vsa_trained_codes_v1` cert-ledger entry (HARD_FAIL: trained VSA
   codes + fixed/linear readout still ties on buried-subject novel-lexeme; wall identified as
   INPUT-DEPENDENT SELECTION, "linear readout only fixed weighting needs bilinear" — this is a
   DIRECT prior negative result confirming exactly the gap this drill targets: a fixed/linear
   readout was already shown insufficient once before; the bilinear+attention design here is the
   correction that result calls for).

**Prior arc work on this concept: bilinear-content-dependent readout was already flagged as the
missing ingredient by `agreement_tem_on_vsa_trained_codes_v1` (cosine=0.2812) — this drill's
design (bilinear interaction + attention pool) is a direct, credited continuation of that finding,
not a novel claim.**

Capability registry (`tools/capability_registry_query.py --serves ...`):
- `learned_relational_readout` — WIRE, TRAPPED_SHARED, used by
  `experiments/exp_relational_readout_promote_v1.py` +
  `experiments/exp_scale_meaning_learn_arc_heldout_v4_breadth.py`; serves "rank-32 bilinear beats
  cosine-NN ~+0.038 mean, leak-proof, controls at chance" — this is the (a)-stage base to extend
  with the quadratic interaction term, not rebuild.
- `readout` (hdlab-module) — ALREADY_WIRED, general cleanup/top-K/cosine readout, used by the
  cleanup_family / swr_v3 cells — a different readout (attractor cleanup, not relational-pair
  scoring); not directly reusable for this drill's pair-scoring task but confirms the module
  namespace to extend into if `AttnBilinearReadout` gets promoted to `hdlab/`.
- `cleanup_attractor` (hdlab-module) — ALREADY_WIRED, "iterative attractor settling / resonator
  cleanup" — a candidate NONLINEAR iterative-settle mechanism (attractor dynamics ARE a form of
  nonlinear readout via energy-minimization) that could be an alternative/complementary route to
  (a)'s explicit quadratic term; noted as a fallback if the explicit bilinear-interaction extension
  underperforms, but NOT recommended first (higher engineering cost, less directly targeted at the
  named gap than the quadratic-term extension).
- `sequence_binding` (hdlab-module, `hdlab/sequence_memory.py::SequenceMatrix`) — ALREADY_WIRED,
  "position-tagged sequence/stack semantics" — this is the write primitive the frontier-scoping doc
  (row 5) already designates for the entity-slot write-gate; section 2(c) above correctly points to
  reusing whatever slot representation THAT produces, rather than duplicating a second bind/unbind
  role-store here.
- `_learned_relational_readout.py` (module read directly) — confirms `fit_bilinear_probe` already
  has the low-rank P:d->r machinery the (a)-extension needs; the quadratic-interaction term A is a
  small, additive extension to this existing fit loop (same TRAIN-TRAIN leak-proof harness,
  `arms_must_differ_hashes` META_RULE_AF hash-test already present and reusable for the new arm).
- `hdlab/binding.py` (module read directly) — confirms `bind`/`unbind` dispatch on dtype
  (FHRR complex mul / HRR circular convolution via FFT), both role-general (not position-indexed),
  ready to reuse for section 2(c) if/when that stage is built.

No existing cell already builds the attention-pooled + bilinear-interaction combination proposed
here; it is a genuine (small) extension of `learned_relational_readout`, not a duplicate.

---

## STATUS

Design-only drill, complete. No code built, no cell dispatched, no queue touched. Recommendation
for the next exp_dev/skunkworks handoff: extend `_learned_relational_readout.py` with a
quadratic-interaction term (stage a) + build a small attention-pool head (stage b) as ONE combined
readout arm (`ATTN_BILINEAR`), pre-registered against the bands in section 3, run on
`diag_order_critical_comprehension_calib_v1.py`'s cross-boundary extension, CPU-capable, both
seeds, mandatory untrained-random-init control.
