# Research: ANCHOR_COMPOSE live-substrate integration path

Date: 2026-07-13. Research (Opus synthesis over 2 parallel Sonnet lit-scans + direct code read; no experiments run).

## HEADLINE

ANCHOR_COMPOSE (`experiments/exp_anchor_compose_inductive_entity_cskg_v1.py`) is a mechanism proof built on a
**gradient-descent-trained, low-dimensional (k=24), additive (TransE-style) embedding table with direct
Euclidean-distance readout** — an offline batch experiment with no persistence and no query-time API. The
**live** `hdlab.kg_traversal.KGStore` (note: the file the task named, `hdlab/store.py`, is actually
`TraceStore`, an unrelated trace-persistence class — the real live KG primitive lives in
`hdlab/kg_traversal.py`) is a **fixed-atom, high-dimensional (n_dim ~1024-2048), multiplicative
(Hadamard-bind) one-shot Hebbian outer-product associative memory** with bilinear (E @ W @ key) readout. These
are two different representational regimes (dimensionality ~40-85x apart, bind algebra multiply-vs-add,
training regime none-vs-SGD, readout bilinear-Hebbian-vs-direct-distance). **No free/direct plug-in exists.**
The cheapest legitimate path is not to import ANCHOR_COMPOSE's machinery wholesale, but to first test whether
the store's OWN native multiplicative bind, used with the identical "bundle support-edge estimates" pattern,
already delivers the same induction win — this is a single cheap CPU experiment that resolves which of two very
different-cost integration paths (native-bind cheap vs adjunct-structure costly) is correct, and it should run
BEFORE further magnitude-optimization of the current offline additive recipe.

## Internal feasibility (code-read only; corrected file map)

| Task's assumed file | Actual role | Correct target |
|---|---|---|
| `hdlab/store.py` | `TraceStore` — DuckDB-backed trace-event log (unrelated to KG) | N/A |
| live KGStore | — | `hdlab/kg_traversal.py::KGStore` |

**`KGStore` (hdlab/kg_traversal.py), what it already provides:**
- `E` [n_ent, n_dim]: entity codebook. Either random bipolar {-1,+1} or content-deterministic char-trigram
  encoding (real-valued, but not gradient-trained — a fixed function of the entity's name string).
  **FIXED after init/ingest** — never gradient-updated.
- `R` [n_rel, n_dim]: relation codebook, random bipolar. **FIXED**, never learned.
- `W` [n_dim, n_dim]: the only *learned* structure, and it's learned by **one-shot Hebbian outer-product
  accumulation** (`W += outer(E[o], key) / n_dim` per triple batch) during `ingest_triples` — no gradient
  descent, no epochs, no loss function.
- `key(s, p) = E[s] * R[p] * sqrt(n_dim)` — **elementwise multiplicative** bind (HRR/MAP-family bind, the
  standard VSA convention), not additive.
- `score_all(key) = E @ (W @ key)` — a **bilinear associative recall** through the Hebbian matrix, not a direct
  distance/dot-product lookup against `E`.
- `predict_one_hop` / `predict_n_hop`: the CERT-584/585 chain-grade multi-hop machinery (36.49x ratio over
  frozen-encoder baseline, refuse-OOD=0.999) — this is the capability that must not regress.
- `E` is **fixed-size** at `__init__`: there is no append/grow method. Inserting a new entity row is not
  supported today.
- `cleanup_family.py` (the sibling cleanup-primitive library): 5 single-vector cleanup primitives
  (`classical_hopfield`, `modern_hopfield_continuous`, `iterative_attractor`, `k_NN_lookup`, `no_cleanup`) + 2
  bundle-set readouts (`flat_topk_readout`, `peel_sic_readout`). These operate on an arbitrary `(query,
  codebook)` pair (numpy, real or complex dtypes) — **decoupled from KGStore's specific bind/Hebbian
  convention**, so they are format-agnostic and could score a composed code in EITHER representational space
  without modification, IF the code and codebook are already dtype/shape-compatible.

**ANCHOR_COMPOSE + its two building blocks, what they actually need:**
- `_kge_anchor1_fit.py::fit_kge_anchor1`: gradient-descent (Adam) fit of `X` [N,k] entity coords and `D`
  [n_rel,k] relation displacements, k=24 (FULL) / 12 (selftest), 250-500 epochs, self-adversarial
  cross-entropy loss + N3 regularization + reciprocal-relation augmentation + minibatch SGD (batch=8192). This
  is a from-scratch KGE training loop, structurally unrelated to KGStore's one-shot Hebbian write.
- `_course_c_rotate_core_v1.py::additive_direct_scores(X, D, hold_edges, ...)`: `score(t) = -||X_h + D_r -
  X_t||` — direct Euclidean distance against the fitted coordinate table. No Hebbian matrix anywhere in this
  path.
- `exp_anchor_compose_inductive_entity_cskg_v1.py::build_anchor_compose_codes`: `E_derived[t] = mean_i(X[h_i] +
  D[r_i])` over t's own support edges (`index_add_` + count-normalize) — a **training-free, degree-invariant
  bundle** of per-edge TransE tail estimates. This is the actual "compose a novel entity" op, and it is the one
  piece with no existing analog anywhere in `KGStore`.

**Minimal integration mapping:**
- Composer's "bind head with relation" (`X_h + D_r`) is *conceptually* parallel to `KGStore.key(s, p)`, but the
  algebra differs (add vs multiply) — not a drop-in.
- Composer's "score all entities against a bound key" is *conceptually* parallel to `KGStore.score_all(key)`,
  but the mechanism differs (direct distance vs bilinear Hebbian recall) — not a drop-in.
- Composer's `build_anchor_compose_codes` bundling op (mean of per-edge additive estimates) has **no existing
  equivalent** in `KGStore` at all — this is the one genuinely missing primitive, but it is procedurally simple
  to add **in either geometry**: for the store's own multiplicative convention, the direct analog is bundling
  (superposition + majority-sign or normalized-sum) of `key(h_i, p_i)` vectors across support edges — a
  well-established native VSA operation (see external synthesis below), just never wired up or measured here.
- `KGStore` also has **no append/grow method for E** — inserting a derived code so it becomes re-queryable
  requires either pre-allocated slack rows or a concatenated "overflow" side-table at score time. This is a
  small, clean gap (needed regardless of which bridge is chosen).

**Code-format compatible? NO — bridge required.** Store: n_dim ~1024-2048, bipolar/near-orthogonal fixed atoms,
multiplicative bind, untrained (zero-epoch) Hebbian recall. Composer: k=24, continuous, gradient-trained
(Adam, hundreds of epochs), additive bind, direct-distance recall. Neither dimensionality nor algebra nor
training regime matches; a naive attempt to call `KGStore.key()/score_all()` on the composer's `(X, D)` outputs
would silently produce meaningless numbers (wrong dimensionality) rather than erroring — this is the sharpest
operational hazard of doing this integration carelessly.

**Single biggest integration risk:** the representational mismatch itself. There is no cost-free unification;
every path listed below either (a) bolts a second, differently-trained structure alongside the proven
Hebbian/multiplicative one (adjunct — architecturally safe, but doubles maintenance and needs a re-fit-cadence
policy), or (b) reformulates the store's core bind/readout (touches the CERT-584/585 hot path directly —
highest regression risk to an already-proven 36.49x capability), or (c) reuses the store's own native
multiplicative bind for the bundling op (cheapest, zero new representational format, but completely unvalidated
whether bundling *multiplicative* keys preserves the degree-invariant genuine-induction property that VET
`a7688ea3` measured specifically for the *additive* geometry — rotation was found degree-confounded there;
whether the store's fixed-atom multiplicative bind is closer to "additive" or "rotation" in that sense is an
open, cheaply-answerable question, see Cheap decisive test below). Whichever bridge is chosen, the composer's
own fairness apparatus (POP baseline, degree tertiles, SCRAMBLE must-fail, RANDOM null, ORACLE transductive
must-fire) must be re-run against it — this is not a formality, it is the actual test of whether the bridge
preserves the win.

## External grounding (safe internet research; generic terms only)

**Two parallel Sonnet lit-scans dispatched** (KGE/VSA angle; hippocampal/CLS angle). Full text preserved in
session; synthesis below.

**A. Inductive KGE / VSA — serving a novel-entity code from a LIVE store, not a batch benchmark.**
Composing an unseen entity's code from its neighbor-relation bundle at inference time IS established
inductive-KGE practice (GraIL Teru et al. 2020 and NBFNet Zhu et al. 2021 via GNN/path reasoning over the
local subgraph; LAN/oDistMult-style single-layer neighbor aggregation is the closest analog to a plain additive
bundle; NodePiece Galkin et al. 2021 builds compositionally from a fixed anchor/relation token vocabulary).
**But persistent "compose -> write into a live index -> re-query later" as a first-class ONLINE operation is
essentially absent from the inductive-KGE literature itself** — every one of these papers evaluates as
one-shot batch scoring against a fixed held-out split. That online-write pattern instead lives in a
*different*, non-cross-citing literature: production recommender/ANN-serving systems (incremental HNSW inserts
+ cold-start networks that predict a new item's embedding for immediate insertion, e.g. Deezer 2024). Lifelong
KG Embedding (Cui et al., AAAI 2023) is the closest "online" KGE paper, but it operates on discrete graph
snapshots with anti-forgetting regularization, not per-query incremental writes.

On the VSA/HRR side, writing a newly bound item into an associative memory so it's retrievable later is
**native and well-established**: HRR superposition (Plate 1995), classical/modern Hopfield incremental
outer-product updates (Ramsauer et al. 2021 preserves this while gaining exponential capacity), Kanerva's
Sparse Distributed Memory (1988, incremental counter-based writes by construction). This is exactly the shape
of `KGStore.ingest_triples` — already a proven pattern on this substrate, not a gap. One explicit negative
finding: **resonator networks (Frady/Kent/Olshausen/Sommer 2020/2021) are extensively documented for the
read/decode side but not for a "write" step** — composing the product vector is treated as ordinary encoding
outside the resonator literature, meaning the store's existing outer-product Hebbian write is actually MORE
precedented than a resonator-based write would be.

Bridging a low-dim gradient-trained KGE and a high-dim fixed-atom Hebbian VSA memory is **essentially
unaddressed as a direct algorithmic bridge** — no Procrustes/linear-map paper connecting these two specific
families was found (Procrustes/orthogonal mapping shows up for same-family alignment, e.g. bilingual word
embeddings, not cross-family). The closest *conceptual* (not algorithmic) frame is Complementary Learning
Systems theory (McClelland, McNaughton & O'Reilly 1995): fast/sparse hippocampal-like and slow/distributed
cortical-like systems are treated as **complementary and dual**, not merged into one representation — which
argues for an adjunct/parallel-structure design over a forced single-representation unification, if a bridge
of that kind turns out to be needed at all.

**B. Brain: hippocampal integration of a freshly-bound novel representation.**
One-shot encoding is well-established and directly analogous to `ingest_triples`: dentate gyrus performs
pattern separation (sparse, near-orthogonal codes, minimizing interference — Yassa & Stark 2011), CA3's dense
recurrent collaterals form an auto-associative Hopfield-like network that binds a novel conjunction via
one-trial Hebbian LTP (Rolls 2013; Cell 2024 Yoon et al. on CA3 connectivity rules), and hippocampal indexing
theory (Teyler & DiScenna 1986, updated Teyler & Rudy 2007) frames the hippocampus as binding/indexing
distributed cortical ensembles rather than storing content itself — **zero gradient descent, one-shot Hebbian
write, exactly the store's `ingest_triples` shape.**

Immediate usability is the biologically interesting part: a fresh trace is **not quarantined** — associative/
transitive-inference tasks (Bunsey & Eichenbaum 1996; Preston et al. 2004) show hippocampal-dependent inference
over recently-learned overlapping pairs almost immediately, and sharp-wave-ripple replay mixes very recent with
older experience to support both immediate use and later consolidation (Nature Reviews Neuroscience 2018;
Science 2024). The one caveat: raw synaptic stabilization (tag-and-capture, Frey & Morris 1997) takes
~30min-2hr before a trace is durably fixed, even though behavioral/inferential use can be immediate — so
"immediately queryable, durably stabilized later" is itself the biological pattern, not an engineering
compromise.

Systems consolidation (the standard CLS story: McClelland/McNaughton/O'Reilly 1995, updated Kumaran/
Hassabis/McClelland 2016) slowly interleaves hippocampal fast traces into neocortex via replay, normally over
weeks — but Tse et al. (2007, 2011, Science) showed this collapses to ~2 days when the new information is
**schema-consistent**, i.e. cortex can rapidly assimilate a new item once compatible relational scaffolding
already exists. Open/contested: exact "immediately usable" timescale, and whether consolidation is
integration/transformation (index theory, schema-CLS) vs the older systems-level replacement view.

**Synthesis point (the useful cross-thread finding):** biology suggests a **two-timescale design**, not a
single bridge: (1) fast, native, one-shot write for immediate query-time serving (hippocampus-like — maps onto
using the store's OWN multiplicative Hebbian bind for composition, zero new format), plus (2) a slow, periodic,
schema-gated consolidation/re-fit pass that folds accumulated novel-entity writes back into the main structure
on a cadence (cortex-like — maps onto the adjunct low-dim additive geometry, refit periodically). This maps
cleanly onto the staged plan below.

## Cheap decisive test (do this FIRST, before wiring any code)

**Test:** re-run the existing ANCHOR_COMPOSE fairness apparatus (self-test, then FULL) unmodified, EXCEPT
construct `E_derived[t]` by bundling `KGStore.key(h_i, p_i)` vectors across t's support edges (majority-sign or
normalized superposition, the native multiplicative-bind analog of `build_anchor_compose_codes`) instead of the
SGD-trained additive `(X, D)`. Score via `KGStore.score_all`. Reuse the SAME degree-stratified, SCRAMBLE/RANDOM/
ORACLE-must-fire apparatus already built into the composer's self-test — zero new fairness machinery needed,
only the bind/bundle/readout substitution. Cost: cheap (no gradient training at all; CPU-only; ~1 day to wire
the substitution + a CPU smoke). Risk to the proven store: none (read-only probe against `KGStore`, no mutation
of `E`/`R`/`W`).

**Falsifiable predictions (re-using the composer's own pre-registered ceiling-relative bands, applied to the
native-bind arm):**
- HARD-PASS: native-bind-bundle margin over RANDOM >= 0.50 * measured ORACLE headroom (H), AND scramble-bundle
  margin over RANDOM <= 0.25*H, AND ORACLE fires (>=3x RANDOM, >=0.003 abs) -> **native bind already carries
  the induction win; integration is cheap (Stage 0 below), no adjunct structure needed.**
- HARD-FAIL: native-bind-bundle margin over RANDOM < 0.20*H with ORACLE firing -> **the store's fixed random
  atoms genuinely lack what the SGD-trained additive geometry provides; the adjunct-structure path (Stage 0b)
  is required, and the current magnitude-optimization work on the additive recipe is directly load-bearing
  (worth continuing).**
- MIDDLE: between the two -> localize by anchor-support-degree bin (the composer's existing
  `localize_weak_points` stratification) before deciding.

P_deflated for "native bind already suffices" (no direct precedent found in either lit-scan; genuinely
uncharted): raw estimate ~0.45, deflated 0.20 per calibration discipline -> **P ~= 0.25**. This is intentionally
close to a coin-flip because the two lit-scans found literature on both sides of the analogy (VSA superposition
writes are native and well-precedented generally, but no precedent exists for THIS SPECIFIC bundling operation
preserving degree-invariant induction under a fixed-random-atom multiplicative bind specifically).

## Cross-thread synthesis

Connects to: VET `a7688ea3` (additive beats rotation on fair held-out; rotation degree-confounded) — the
open question this note surfaces is whether that additive-vs-rotation finding is about the *bind algebra*
(additive fundamentally superior for this task) or about the *training regime* (gradient-trained geometry
beats fixed-random-atom geometry generally); the Stage-0 test directly separates these two explanations for the
first time. Connects to CERT 584/585 (chain-grade multi-hop, 36.49x ratio) as the capability that must not
regress under any integration option (b)-style core reformulation. Connects to the ongoing
"relational-capability-is-the-core-requirement" program thread (additive/geometric codes = degree-invariant,
reused-across-domains, per the brain-grounding drill) — this note is a direct engineering continuation of that
thread, specifically the "wire it into the live store" half that was previously unaddressed.

## Substrate-product implications

Today, ANCHOR_COMPOSE is a proof that the substrate CAN represent and rank a genuinely novel entity from a
handful of its own edges without any gradient training on that entity — a real capability, but only
demonstrable inside a disposable Python process. Making it live means: a user-facing query mentioning a brand
new entity (never in the KB) could get a useful, ranked, immediately-queryable answer derived purely from
whatever edges that mention brought with it — the same trick that lets a person hear a friend mention a new
acquaintance's name plus two facts and immediately be able to reason about them alongside everyone else they
know. The staged plan below is the difference between "we proved this works in an experiment" and "the product
does this every time it meets someone/something new."

## Staged integration plan

**Stage 0 (cheapest, do first): native-bind decisive test.** As specified above. Dependency: none (uses
existing `KGStore.key`/`score_all` + the composer's existing fairness harness). Cost: cheap (~1 day, CPU-only,
no gradient training). Risk: none (read-only probe).

**Stage 0a (if Stage 0 HARD-PASSes): ship the cheap path.** Add `KGStore.compose_entity_code(support_edges)`
(bundle of `key(h_i,p_i)`, majority-sign/normalize) and `KGStore.insert_entity(code) -> new_idx` (requires
adding slack-row preallocation or an overflow side-table, since `E` is currently fixed-size) directly to
`kg_traversal.py`. Cost: moderate (small, well-scoped module additions; the growth/append gap must be built
either way). Risk: low-moderate (new code path, but reuses proven bind/score primitives verbatim; must re-run
the composer's full fairness apparatus against the live-wired version before trusting it, per the "code format
compatible" caveat above).

**Stage 0b (if Stage 0 HARD-FAILs): adjunct additive-geometry companion.** Promote `fit_kge_anchor1` from
`experiments/` to a maintained `hdlab` module; add a periodically-refit `(X, D)` companion structure alongside
`KGStore`'s existing `E/R/W` (untouched — preserves CERT 584/585), plus the same `compose_entity_code`/
`insert_entity`/score API operating in that separate low-dim space. Cost: bigger (harden the SGD fit loop for
library use, decide a re-fit cadence, add a sync/staleness policy between the two structures). Risk: moderate
(new parallel structure to maintain long-term, but zero regression risk to the proven Hebbian machinery since
it is never touched).

**Stage 1 (after 0a or 0b lands and is VET-confirmed live): fold into multi-hop.** Make a freshly-composed
novel-entity code participate in `predict_one_hop`/`predict_n_hop` so it's reachable by N-hop chains, not just
single direct queries. Cost: bigger (concatenated base+overflow table at every hop, or in-place slack-row
growth; must re-validate CERT 584/585 numbers are unaffected). Risk: moderate-high (touches the hot path of the
proven 36.49x capability directly — the first place a genuine regression could hide).

**Stage 2 (biological "systems consolidation" analog): background consolidation pass.** Periodically fold
accumulated novel-entity writes back into the main structure (periodic Hebbian re-ingest for the Stage-0a path,
or periodic re-fit for the Stage-0b path) — mirrors hippocampus-to-neocortex replay consolidation (weeks
normally, ~2 days if schema-consistent per Tse et al.). Cost: bigger (scheduling, staleness/versioning,
drift-detection). Risk: moderate (mostly a scheduling/ops problem once Stage 0/1 exist, not a new mechanism
risk).

**Integrate-before-or-after magnitude-optimization: INTEGRATE (run Stage 0) FIRST.** Three reasons: (1) Stage 0
is cheap and decisive — it picks between two very-different-cost future paths (0a vs 0b), and tuning the
current offline additive recipe's hyperparameters (k/epochs/gamma) gives zero information toward that fork; (2)
interaction effect — if Stage 0 HARD-PASSes, all further magnitude-optimization spent tuning the SGD additive
recipe (k=24, epochs=500, self-adversarial CE tuning) would be optimizing a component that never ships in the
live capability, wasted work; (3) if Stage 0 HARD-FAILs, that negative result is itself valuable — it
establishes that the SGD-trained additive geometry carries real information the store's fixed atoms lack,
which directly justifies BOTH continuing magnitude-optimization on the additive recipe AND paying Stage 0b's
higher engineering cost with evidence in hand, rather than guessing. Either outcome of Stage 0 tells you where
to spend the next unit of effort; skipping it and optimizing blind does not.

## Citations (verified count: 29)

KGE/VSA lit-scan (14): GraIL (Teru et al. 2020); NBFNet (Zhu et al. 2021); LAN/oDistMult inductive-embedding
survey baseline; NodePiece (Galkin et al. 2021); Lifelong KG Embedding / LKGE (Cui et al., AAAI 2023); Deezer
"Let's Get It Started" (2024, cold-start ANN serving); HRR superposition (Plate 1995); classical Hopfield
outer-product memory; modern Hopfield networks (Ramsauer et al. 2021); Sparse Distributed Memory (Kanerva
1988); Resonator Networks (Frady, Kent, Olshausen, Sommer, 2020/2021); Procrustes/Wasserstein bilingual-
embedding alignment lit; "Hyperdimensional Probes" (2026, LLM-dense-to-VSA decoding); Complementary Learning
Systems (McClelland, McNaughton & O'Reilly, 1995).

Hippocampal/CLS lit-scan (15): Yassa & Stark (2011, pattern separation review); Rolls (2013, CA3 quantitative
theory); Yoon et al. (Cell 2024, human CA3 connectivity); Teyler & DiScenna (1986, indexing theory); Teyler &
Rudy (2007, Hippocampus); CRISP one-shot sequence model (PMC 2024); Bunsey & Eichenbaum (1996, PNAS,
associative/transitive inference); Preston et al. (2004); SWR retrieval+consolidation review (Nature Reviews
Neuroscience 2018); SWR content-selection (Science 2024); Kumaran, Hassabis & McClelland (2016, TICS, CLS
update); Tse et al. (2007, Science, schema-consistent consolidation); Tse et al. (2011, Science, schema-
dependent gene activation); Frey & Morris (1997, synaptic tagging and capture); synaptic tagging review (2025,
Communications Biology).
