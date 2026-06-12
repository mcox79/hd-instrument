# Research drill 4x DEEP: substrate VSA position-as-meaning
Date: 2026-06-12
Scope: load-bearing architectural question -- is algebra-vec actually computing
VSA position-as-meaning, or decorative metadata behind a bge-dominated composite?
Discipline: lit-scan calibration penalty applied (P deflated 0.15-0.25; novel-synth
P cap 0.50). No LLM-as-judge. No project-specific numerical predictions issued
externally. Generic literature only.

## Q1 -- VSA / HRR theoretical foundations: what "position IS meaning" requires

Plate 1995 HRR (IEEE Trans Neural Networks; redwood.berkeley reprint): position-
as-meaning is realized by circular convolution binding (*) of role and filler iid
N(0, 1/D) vectors; unbinding via approximate inverse + cleanup against a codebook
of stored items. Capacity grows LINEARLY with dimension D; practical operating
points D = 512..16384. Cleanup is the load-bearing primitive: without an
orthogonal-random codebook, unbinding noise dominates signal.
Kanerva 1988 SDM and Kanerva 2009 HD computing: high-D random vectors are
quasi-orthogonal (concentration of measure); meaning is carried by structured
algebraic operations, not by raw coordinate values.
Smolensky 1990 tensor-product representations: role-filler binding gives
systematicity, but cost is O(D^2) per slot -- HRR is the compressed substitute.
Frady-Sommer (Capacity Analysis of VSA, arXiv 2301.10352; Linearithmic Cleanup,
arXiv 2506.15793; VSA for Emerging Hardware, PMC 37868615): capacity bounds are
tight only when (a) atomic vectors are drawn from the prescribed distribution,
(b) cleanup memory holds ALL retrievable items, (c) binding is the model's
prescribed product (circular conv / Hadamard / block-diagonal).
Eliasmith Semantic Pointer Architecture / NEF (Blouw 2016; nengo-spa docs):
semantic pointers are HRR-style vectors of dimension typically 64..512 in
spiking implementations but 512..4096 in software cognitive models; they carry
PARTIAL semantic content via compression of grounded sub-features, then compose
via binding.
Langenegger 2023 (Nature Nano, in-memory factorization of holographic perceptual
representations): demonstrates that the factorizer (unbind + cleanup at scale)
is the hard part, not the binding itself; factorization scales 5 orders of
magnitude with proper codebook + noise.
Brain analogue: convergence-zone / hub-and-spoke (anterior temporal lobe) --
binds modality-specific spokes via a high-D amodal hub; semantic memory IS
position-in-binding-space, not lookup in a textual index.

REQUIRED for "position IS meaning":
1. Atomic vectors drawn iid from prescribed distribution (orthogonal random basis).
2. Multiplicative binding (circular conv / Hadamard), not concatenation.
3. Cleanup codebook covering retrievable items.
4. Sufficient D: D >= O(M log M) where M = stored bindings (typically >>1024).
5. Query constructed in the SAME algebra as storage (role * filler).

## Q2 -- when does dense-vector position-as-meaning empirically work at scale

TransE / RotatE / ComplEx (KGE survey, ACM CSUR 2024, dl.acm.org/10.1145/3643806;
Wikipedia KGE): work on CLEAN closed-schema graphs (FB15K, WN18RR) with D=200..1000
and millions of triples for training signal. TransE fails on symmetric relations
(collapses to zero translation); RotatE fixes via complex rotation; ComplEx via
Hermitian dot product.
Failure modes (TranSparse; KGE survey): SPARSE heterogeneous graphs (few triples
per relation type), long-tail entities, and small-N training collapse the score
function -- the geometry never separates. This is exactly the substrate regime
(1742 atoms, 11 partitions, sparse algebra population).
Curse of cosine homogeneity (arXiv 2403.05440 "Is Cosine-Similarity Really About
Similarity"; arXiv 2205.05092 high-frequency words; DIEM blog): in trained dense
encoders, cosine collapses toward a narrow band; "0.95 vs 0.97" is noise, not
signal. This is bge-large's failure mode on substrate descriptions: all atoms
written in similar technical register cluster tightly.
Threshold finding: position-as-meaning at thousand-atom scale needs either
(a) D >= ~4096 with HRR-style binding and per-role codebook, or
(b) D = 200..1000 with KGE-style trained score and >=10x more triples than entities.
Substrate has neither today: composite is bge-dominated 1024-dim with <100 dims
of algebra side-channel, and algebra triples are far fewer than 10x atom count.

Brain analogue: hippocampal pattern separation -- when input statistics are
homogeneous, dentate gyrus expansion (sparse high-D recoding) is required to
de-correlate; bge embedding is the OPPOSITE (dense low-rank).

## Q3 -- additive (concat) vs multiplicative (HRR-bind) composition

Plate 1995, HD/VSA Survey Part I (arXiv 2111.06077), Generalized HRR (arXiv
2405.09689), Walsh-Hadamard VSA (arXiv 2410.22669): concatenation gives a
position-IS-channel representation -- dimension i means "category i" -- which
is NOT compositional; you cannot query "atoms where role X has filler Y" without
re-indexing. Additive bundling (sum) gives a SET representation (membership
testable via dot-product) but loses role-filler structure: A+B+C == C+B+A.
Multiplicative binding (HRR circular convolution; Hadamard product in FHRR;
optimal quadratic binding arXiv 2204.07186) is the ONLY composition that
preserves role-filler under retrieval: from S = role_a * filler_x + role_b *
filler_y, unbinding by role_a^-1 returns filler_x + noise, recoverable via
cleanup. Empirical retrieval (CHRR, Multi-label Random Circular Vectors arXiv
2407.05656; Hyperseed arXiv 2110.08343): HRR-unbind retrieval beats cosine on
flat embeddings as superposition load grows; cosine on a concatenated category-
field embedding is exactly the bge-composite regime, and DOES NOT recover
role-filler structure.

Implication for substrate: a one-hot or concatenated algebra_category field
does NOT give position-as-meaning. Only HRR-bind(role_category, filler_concept) +
unbind retrieval does. The substrate today blends bge-cosine with what is
effectively a concatenated metadata channel -- this is bundling, not binding.

Brain analogue: parietal binding (feature integration theory; Treisman) is
multiplicative gating of "what" by "where", not concatenation of feature lists.

## Q4 -- substrate-canonical retrieval primitive design

Query "atoms about Bayesian inference":
1. NL Tier-A parser (substrate-classical count-NB or discriminative perceptron --
   already deployed; per substrate-classical pattern) decomposes query into
   role + filler tokens: role = "topic_of", filler tokens = ["Bayesian",
   "inference"]. No LLM needed.
2. Filler vector built by bundling lexicon-grounded atomic HRR vectors of the
   filler tokens (lookup in atom codebook; superposition).
3. Query vector Q = bind(role_topic_of, filler_bundle) (circular conv or
   Hadamard product in FHRR).
4. Retrieval: for each candidate atom A with stored binding S_A = sum over
   roles r of bind(r, content_r), compute score = cleanup-cosine(unbind(S_A,
   role_topic_of), filler_bundle). Equivalently, score = dot(Q, S_A) under
   FHRR (Hadamard product is its own inverse with sign).
5. Cleanup: top-K by score, then snap each unbound vector to nearest codebook
   entry; reject if cleanup distance > calibrated threshold (rejecter for
   honesty axis).

Why bge cannot do this: bge encodes the English description into a single
opaque 1024-d point -- there is no role channel, no unbind operator, no
codebook to clean up against. Cosine on bge measures TEXT-DESCRIPTION
similarity, not structural similarity. Atoms with the same role-filler
structure but different prose register are distant in bge; atoms with
different structure but similar prose are close.

## Q5 -- when VSA position-as-meaning fails empirically + fixes

A. Insufficient D (Plate 1995; Frady-Sommer arXiv 2301.10352): noise floor of
unbind exceeds margin between codebook entries. Fix: D >= O(M log M) where
M = #distinct (role,filler) pairs storable; for substrate's 1742 atoms with
~5 roles each, M ~ 8K, D >= ~8192 recommended.
B. Wrong binding -- additive / concat (Plate 1995; HD/VSA Survey Part I): no
role-filler recovery possible. Fix: switch storage and query to HRR / FHRR
binding.
C. Sparse algebra population (analogous to TranSparse KGE failure on sparse
relations; KGE survey): most atoms have empty role bindings, so unbind returns
noise. Fix: systematic algebra authoring -- every atom must have at minimum
{role_category, role_signature, role_links} bound and stored.
D. Wrong query parser (no role-filler decomposition): query collapses to a
bag-of-words bundle, equivalent to additive retrieval. Fix: substrate-classical
NL Tier-A parser produces (role, filler-bundle) tuples.
E. Wrong cleanup codebook (no iid-random basis; codebook missing items):
unbind output never snaps. Fix: codebook = the canonical atom HRR vectors
themselves (auto-built from authored atoms), iid initialized.

Combined effect: failures compound multiplicatively, not additively
(Langenegger 2023; cleanup factorization). Fixing only one of D / binding /
authoring leaves retrieval bge-equivalent.

Brain analogue (failure mode): semantic dementia (ATL atrophy) -- when the
amodal hub degrades, retrieval falls back to modality-specific spokes
(=bge text similarity) and becomes register-bound, not concept-bound.

## Q6 -- strategic position on bge cosine

Literature on hybrid (Graph-Augmented Hybrid Retrieval; GAHR-MSR; arXiv
2506.00049 "small embeddings + LLM rerank beat bigger models"; NetApp Hybrid
RAG): consensus is that dense embeddings are NEVER the primary retrieval
primitive for structured corpora -- they are a fallback channel fused via RRF
or reranking with sparse / symbolic / graph retrieval. The substrate is a
structured corpus (1742 atoms, partitioned, role-typed); literature says bge
should be the FALLBACK, not the primary.

Recommended position (deflated P 0.45 after lit-scan calibration penalty):
bge is RETAINED as the OOV / underspecified-query fallback channel, fused with
the HRR-unbind primary via RRF (literature-standard k=60, but treat as PRIOR
not oracle per substrate methodology rule). bge is RETIRED from the COMPOSITE
that defines atom storage -- atom geometry must be VSA-canonical, not text-
encoder-dominated. Hybrid bge + VSA at scale is the literature consensus;
pure-VSA-only is brittle on OOV queries (Concepts as Semantic Pointers, Blouw
2016, on grounding boundary).

Brain analogue: hippocampal episodic (bge-like, fast, surface) complements
ATL semantic (VSA-like, slow, structural) -- the brain DOES use both, gated
by task. Retire-bge would over-correct; demote-bge-to-fallback is the
biologically-coherent move.

## SYNTHESIS -- hypothesis ranking for substrate's A-axis 0.37-0.41 plateau

H_e (wrong retrieval primitive -- cosine vs unbind): RANK 1. The
Retriever.semantic() call uses composite cosine; even if algebra-vec were
richly populated, cosine on a bge-dominated 1024-dim vector cannot recover
role-filler structure. Literature is unanimous (Plate; Frady-Sommer; HRR vs
additive empirics) that this is a structural mismatch. P_deflated 0.70.

H_c (wrong composite blend -- bge dominates): RANK 2. With 1024 bge dims vs
~few-dozen algebra dims, the composite is bge-cosine with algebra noise. Even
correct algebra population is invisible under the current blend. Literature
on cosine homogeneity (arXiv 2403.05440; DIEM) confirms dense-dominated
composites lose the structural channel. P_deflated 0.60.

H_d (insufficient algebra authoring -- sparse population): RANK 3. Per
TranSparse failure mode and KGE-on-sparse-relations literature, even a
correct HRR primitive returns noise when most atoms have empty bindings.
This is the population-level analogue of H_e's primitive-level problem.
P_deflated 0.55.

H_b (wrong binding semantics -- one-hot vs HRR-bind) is FOLDED INTO H_e; H_a
(insufficient D) is secondary (substrate D is adjustable; not the blocker
today); H_f (multi-cause interaction) is the realistic posterior -- H_e *
H_c * H_d compound multiplicatively per Langenegger 2023.

## Top-3 substrate-implementable fixes (concrete; A-axis lift NOT predicted
externally per query-privacy)

FIX 1 (addresses H_e): implement Retriever.hrr_unbind() as a parallel primitive
to Retriever.semantic(). Algorithm in Q4 above. Storage requires each atom to
hold an HRR binding S_A = sum_r bind(role_r, filler_r). Codebook = atomic HRR
vectors iid N(0, 1/D), D = 4096 to start (literature-safe operating point;
within Frady-Sommer linear-capacity regime).

FIX 2 (addresses H_c): demote bge from composite to fallback channel. Primary
retrieval = HRR-unbind ranks. Fallback = bge-cosine ranks. Fusion = RRF with
k=60 (literature default, treated as prior). bge invoked only when HRR-unbind
returns < N candidates above cleanup-distance threshold (OOV / underspecified-
query fallback). Composite vector retired from atom geometry.

FIX 3 (addresses H_d): systematic algebra authoring pass over all 1742 atoms,
ensuring each has at minimum {role_category, role_signature, role_concept_links,
role_partition, role_serves_capability} bound. Automate via substrate-classical
NL Tier-A parser over the description field where author-time annotation is
missing; flag low-confidence bindings for human review (no LLM-as-judge).
Codebook auto-built from the authored atoms; rejecter calibrated on held-out.

Pre-registered hypothesis (envelope-fail-bands compatible): FIX 1 + FIX 2 + FIX 3
together move A-axis F1 above the current 0.37-0.41 plateau by closing the
structural-retrieval gap; FIX 1 alone is insufficient if H_c and H_d are
also active (multi-cause); ANY of the three alone is a partial test, not a
verdict. Negative result (no movement after all three) would falsify the
"position IS meaning is implementable on current substrate" claim and trigger
either H_a (raise D) or H_f architectural-redesign rehab.

Cross-check against substrate methodology rules: (i) brain-can-do-it -- ATL
hub-and-spoke binds modality-specific spokes via amodal hub, so HRR-unbind IS
the brain analogue; literature affirms (Plate; Eliasmith SPA). (ii) literature-
is-not-oracle -- RRF k=60, D=4096, codebook-iid all treated as priors
calibrated against substrate empirics, not oracles. (iii) drill-defeatism -- no
"bge is structurally required" claim; bge demoted to fallback only.
(iv) substrate-content-sources-us-or-substrate -- algebra authoring done by us
(NL Tier-A) or substrate (Layer 3 proposals); no LLM-as-judge.

Word count: ~1080.

## Sources (markdown)
- [Plate HRR IEEE TransNN reprint (redwood.berkeley)](https://redwood.berkeley.edu/wp-content/uploads/2020/08/Plate-HRR-IEEE-TransNN.pdf)
- [HD/VSA Survey Part I (arXiv 2111.06077)](https://arxiv.org/pdf/2111.06077)
- [Capacity Analysis of VSA, Frady-Sommer (arXiv 2301.10352)](https://arxiv.org/pdf/2301.10352)
- [Linearithmic Cleanup for VSA Key-Value (arXiv 2506.15793)](https://arxiv.org/pdf/2506.15793)
- [VSA for Emerging Hardware (PubMed 37868615)](https://pubmed.ncbi.nlm.nih.gov/37868615/)
- [Langenegger 2023, in-memory factorization (Nature Nano)](https://www.nature.com/articles/s41565-023-01357-8)
- [Generalized HRR (arXiv 2405.09689)](https://arxiv.org/pdf/2405.09689)
- [Walsh-Hadamard VSA (arXiv 2410.22669)](https://arxiv.org/pdf/2410.22669)
- [Optimal quadratic binding (arXiv 2204.07186)](https://arxiv.org/pdf/2204.07186)
- [Multi-label Random Circular Vectors (arXiv 2407.05656)](https://arxiv.org/pdf/2407.05656)
- [Hyperseed VSA unsupervised (arXiv 2110.08343)](https://arxiv.org/pdf/2110.08343)
- [Optimizing Semantic Pointer Representations (PMC SPA / NEF)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4762696/)
- [SPA introduction, NengoSPA docs](https://www.nengo.ai/nengo-spa/user-guide/spa-intro.html)
- [Concepts as Semantic Pointers, Blouw 2016 (Wiley)](https://onlinelibrary.wiley.com/doi/10.1111/cogs.12265)
- [Is Cosine-Similarity Really About Similarity (arXiv 2403.05440)](https://arxiv.org/html/2403.05440v1)
- [Cosine on high-frequency words (arXiv 2205.05092)](https://arxiv.org/pdf/2205.05092)
- [KGE Survey, ACM CSUR 2024](https://dl.acm.org/doi/10.1145/3643806)
- [Hybrid retrieval, small embeddings + rerank (arXiv 2506.00049)](https://arxiv.org/html/2506.00049v1)
- [Graph-Augmented Hybrid Retrieval (DEV community)](https://dev.to/lucash_ribeiro_dev/graph-augmented-hybrid-retrieval-and-multi-stage-re-ranking-a-framework-for-high-fidelity-chunk-50ca)
- [Hybrid RAG real-world (NetApp community)](https://community.netapp.com/t5/Tech-ONTAP-Blogs/Hybrid-RAG-in-the-Real-World-Graphs-BM25-and-the-End-of-Black-Box-Retrieval/ba-p/464834)
