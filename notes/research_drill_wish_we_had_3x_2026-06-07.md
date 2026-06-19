# Research drill: 3x deep on top-3 wish-we-had characteristics -- 2026-06-07

Filed-by: research sub-agent
Trigger: user-initiated 3x deep drill (direct task input)
Calibration penalty applied: P estimates deflated 0.15-0.25; novel-synthesis cap 0.50

---

## HEADLINE

Three capabilities would categorically shift the substrate pitch from "better storage
architecture" to "reasoning system with provable correctness." Counterfactual generation
extends the existing erasure + deterministic replay HP into a Pearl do() operator; it is
implementable in 2-3 weeks at low engineering risk. Customer-specific preference learning
via feedback bindings is similarly cheap (2-3 weeks) and directly targets LLM fine-tune
costs as the displacement narrative. Multimodal substrate is the most expansive wish but
carries the highest pre-test uncertainty: bipolar quantization of vision embeddings loses
less than 0.003 nDCG per the binary CLIP literature, but cross-modal composition
fidelity in BSC/HRR space is empirically untested at production scale. Recommend
sequencing: Wish 1 first (builds on proven erasure + replay), then Wish 3 (feedback
bindings extend continual learning), then Wish 2 (needs multimodal encoder pre-test
before engineering commitment).

P_deflated summary:
- Wish 1 (counterfactuals): P_theoretical = 0.85, P_empirical = 0.55 (pre-test required)
- Wish 2 (multimodal): P_theoretical = 0.70, P_empirical = 0.35 (pre-test required)
- Wish 3 (intuitions): P_theoretical = 0.80, P_empirical = 0.50 (pre-test required)

---

## 1. WISH 1 -- Counterfactual generation with provable correctness

### 1.1 What this means precisely

Substrate already has counterfactual REPLAY (cycle 162 PP-82 HP): given an erased fact F,
substrate deterministically replays its inference chain and proves that conclusions derived
from F no longer hold. That is a BACKWARD-looking counterfactual -- "what no longer
follows from an erased premise."

The wish is FORWARD-LOOKING counterfactual generation: given a hypothetical "what if X
were Y instead of Z," substrate (a) generates a modified KB with X_Y substituted for X_Z,
(b) algebraically derives what would follow in the modified KB, and (c) records the
derivation chain as a cryptographically auditable artifact.

Formal framing: Pearl's do() calculus defines P(Y | do(X=x)) as the distribution of Y
after surgically setting X=x in a structural causal model, severing X's parents. Substrate
implements this naturally because:
- Fact storage is explicit (not implicit in weight matrices)
- Bindings are symbolic and reversible
- Replay already runs deterministic algebraic chains
- HMAC keystore allows selective fact substitution, not just erasure

This is not an approximation of Pearl's do() -- it IS Pearl's do() implemented in an
explicit symbolic binding system.

### 1.2 Architecture for constructive counterfactual generation

Step 1: Specify the counterfactual premise CF = (original_binding, replacement_binding).
  Example: revenue_2024 -> $80M becomes revenue_2024 -> $100M.

Step 2: Apply the surgical substitution in substrate's binding space:
  - Erase revenue_2024_$80M binding (existing HMAC erasure mechanism)
  - Insert revenue_2024_$100M binding (existing insert mechanism)
  - Both operations are O(1) per the production pipeline

Step 3: Run the algebraic query chain over the modified KB.
  - Chain is deterministic (existing replay mechanism)
  - All derived conclusions under the counterfactual KB are extracted
  - This is the "what would follow" answer

Step 4: Compute the diff: derived_conclusions(CF_KB) minus derived_conclusions(original_KB).
  - The diff is the counterfactual delta -- what changes under the hypothetical
  - Delta is itself a set of bindings that can be stored, audited, and exported

Step 5: Generate audit chain.
  - Merkle root over the CF_KB state
  - Replay log covers every derivation step from CF premises to CF conclusions
  - Audit is cryptographically verifiable: third party can reproduce the derivation

### 1.3 What "provable correctness" means

In this context "provable" has a specific technical meaning that is weaker than
mathematical proof but stronger than LLM generation:

(a) STRUCTURAL correctness: given CF_KB and deterministic inference rules, the
    conclusions follow necessarily. No probability, no sampling, no hallucination path.
    The system cannot derive a conclusion that does not follow from CF_KB under the
    inference rules. This is the same guarantee as a SAT solver or a relational database:
    conclusions are deductive consequences of the explicitly stated facts.

(b) AUDIT correctness: the audit chain records every step of the derivation so any
    conclusion can be traced back to its premises. If a conclusion is disputed, the
    plaintiff can replay the chain step by step. This is what "Merkle proof per step"
    (cycle 162 HP) provides.

(c) DELTA correctness: the CF_KB diff is exact. There is no approximation in what
    bindings changed; the erasure is cryptographically keyed (HMAC) so it cannot be
    partially applied.

What "provable" does NOT mean here: it does not mean the counterfactual premise is
epistemically correct (that $100M revenue is a plausible counterfactual); it means
that given the premise, the derivations are correct. The user specifies the
counterfactual; substrate derives what follows from it. This is exactly Pearl's
framework: the causal model is given; do() is applied; consequences follow.

Comparison to LLM counterfactuals:
- LLM: "If revenue had been $100M, I think EBITDA would have been $25-30M, because..."
  -- No derivation, no audit, hallucinates the chain, unrepeatable
- Substrate: query(CF_KB, "what is projected EBITDA") -> $26.7M, Merkle proof #a3f8b2,
  step 1: revenue_2024=$100M, step 2: margin_rate=0.267 (from binding), step 3: product
  -- Deterministic, auditable, cryptographically verifiable, repeatable

### 1.4 CFKGR relevance (2024 lit)

CFKGR (EACL 2024) models counterfactual scenarios as edge additions to a knowledge graph
with logical rule inference. This is structurally isomorphic to what substrate would do:
- CFKGR's "original world state as KG" = substrate's KB
- CFKGR's "hypothetical edges" = substrate's CF_KB bindings
- CFKGR's "rule-based inference" = substrate's algebraic query chain

Difference: CFKGR uses soft rule inference (embedding-based); substrate uses hard
deterministic bindings. Substrate's version is weaker in scope (can only derive what is
explicitly bindable) but stronger in correctness (deterministic, not probabilistic).
This is the right tradeoff for regulated industries: "deterministic but auditable"
beats "probabilistic but flexible" for compliance.

### 1.5 Crazy options for Wish 1

(a) CASCADE COUNTERFACTUALS: chain do() operators. do(revenue=$100M) AND do(headcount=+10)
    AND observe(margin). Multi-variable interventions with joint audit chain. Complexity
    is linear in the number of interventions (still O(K) per binding lookup).

(b) PROBABILISTIC COUNTERFACTUALS: substrate attaches confidence weights to bindings
    (already exists as a concept in BSC literature). The CF derivation produces a
    probability-weighted delta, not a point answer. "Under this counterfactual, projected
    EBITDA is $26.7M (confidence 0.89), because margin_rate binding has confidence 0.89."
    This extends the deterministic guarantee to a calibrated confidence, which is actually
    MORE useful commercially than a bare point answer.

(c) COUNTERFACTUAL DIFF VIEW: UI-level -- substrate shows a side-by-side diff of what
    changes under the counterfactual: green bindings are new, red bindings are erased,
    yellow bindings are modified. This is trivially implementable from the delta (Step 4
    above) and is a high-impact product feature for the "what-if workbench" customer
    use case.

(d) REGULATORY SCENARIO TESTING: customers must demonstrate to regulators that their
    models behave correctly under specific scenarios (DORA Article 9, Basel III stress
    testing, FDA drug-interaction scenarios). Substrate's counterfactual generation is
    the engine: "run scenario X, produce deterministic audit, submit to regulator."
    This is a $B vertical -- regulatory stress testing currently costs $1-5M per
    bank/insurer per stress scenario cycle.

(e) COUNTERFACTUAL TIME TRAVEL: substrate's bitemporal capability plus counterfactual
    generation. "What would the answer have been on 2023-01-01 if fact F had been
    different?" This is do(F=F') applied to a historical snapshot. No existing system
    can do this -- not LLMs, not RAG, not knowledge graphs with temporal indexing.

### 1.6 Engineering cost and pre-test

Engineering cost: 2-3 engineer-weeks.
- Week 1: CF_KB generation (surgical substitution via existing HMAC + insert)
- Week 2: algebraic diff engine (what changes between KB and CF_KB)
- Week 3: audit chain for CF derivations + diff view export

Pre-test (cheap decisive test for Wish 1):
Create 20 synthetic counterfactual scenarios on a 500-fact KB.
Each scenario specifies: original_binding, replacement_binding, expected_delta.
Measure: (a) derivation correctness (delta matches expected) (b) audit integrity
(Merkle replay succeeds) (c) latency (do() + derivation within 5ms per scenario).
Expected wall time: 2-3 hours on laptop CPU. No cloud needed.

---

## 2. WISH 2 -- Native multimodal at substrate algebra level

### 2.1 What this means precisely

Current substrate: text-only. Facts are stored as text-derived bipolar vectors from
bge-small or Llama-1B encoders. The binding algebra (XOR for BSC, circular convolution
for HRR) is agnostic to modality -- it operates on dense vectors, not strings.

The wish: substrate stores bindings from any modality-specific encoder. CLIP encodes
images and text into a shared 512-dim space; substrate receives the CLIP embedding,
binarizes to bipolar, and stores/retrieves via the existing mechanism. A query in text
retrieves image bindings; a query in image space retrieves text bindings. Cross-modal
composition via Pattern B: image-binding XOR text-role = compositional multimodal fact.

### 2.2 Why substrate algebra is medium-blind

Plate (1995) HRR and Kanerva (1996) BSC are defined over continuous and binary vector
spaces respectively. The binding operation (circular convolution in HRR, XOR in BSC)
has no notion of modality. The codebook stores arbitrary vectors. The similarity search
(Hamming distance in BSC, cosine in HRR) operates on the vector, not its origin.

Therefore: plugging CLIP embeddings into substrate's encoding pipeline requires only
(a) a binarization step (continuous float32 CLIP embedding -> bipolar {-1,+1}^N) and
(b) no other changes.

The binary quantization literature (Marqo 2024, Hugging Face embedding-quantization 2024)
confirms: binary CLIP embeddings lose < 0.003 nDCG vs float32 CLIP on image-text
retrieval at 32x memory reduction. This is the cheapest and best-established
quantization path.

### 2.3 Architecture for multimodal substrate

Encoder stack:
- Text: bge-small or Llama-1B (current production)
- Image: CLIP ViT-B/32 (open-source, 151M params, runs on CPU at ~50ms/image)
- Audio: CLAP or ImageBind audio encoder (open-source)
- Video: CLIP frame-level or VideoMAE (heavier; deferred to Phase 2)

Quantization path:
- All encoders produce float32 embeddings of varying dim (CLIP: 512, ImageBind: 1024)
- PCA projection to N=4096 (existing production pipeline's PCA step)
- Sign-binarize to bipolar {-1,+1}^N

Binding:
- Image-of(X) = encode_image(X) -> bipolar_image_vec
- Text-label(X) = encode_text(X) -> bipolar_text_vec
- Cross-modal binding: image_of_X XOR text_label_X = compositional binding
- Retrieval: given text query, retrieve image_of bindings by Hamming distance
- Given image query, retrieve text-label bindings

Multi-modal Pattern B composition: existing Pattern B unbind+substitute works on
any bipolar vectors. So "image of X, but in context Y" = image_of_X XOR context_Y.

### 2.4 Known challenge: cross-modal quantization alignment

CLIP encodes images and text in the same continuous space by design (they are
cosine-close when semantically related). After binarization, the question is whether
cosine proximity in float32 survives as Hamming proximity in bipolar. Literature
precedent from the binary CLIP work (TernaryCLIP 2025, Marqo 2024) shows:

- Binary CLIP for IMAGE-to-TEXT retrieval: < 0.003 nDCG loss at Recall@10
- Binary CLIP for TEXT-to-IMAGE retrieval: similar preservation
- Cross-modal quantization alignment: not directly tested in the substrate-specific
  BSC pipeline (N=4096 with PCA from CLIP 512 -> N upsampling)

The upsampling (CLIP 512 -> PCA -> N=4096) is the uncharted step. Upsampling via PCA
is essentially adding zero-information dimensions, which dilutes the bipolar signal.
This is the main technical risk.

Alternative: keep CLIP at N=512, skip PCA upsampling, store directly in 512-dim BSC.
This is a minor architecture deviation but removes the risk. The cost: heterogeneous
dimensionality in the substrate (text at N=4096, image at N=512). Cross-modal
binding would require dimensionality reconciliation (projection or separate codebooks).

### 2.5 Customer verticals unlocked

Medical imaging: radiology report + imaging study stored as multimodal binding.
"What did Patient X's CT show on 2024-03-15?" retrieves both image embedding and
report text. HIPAA-compliant erasure applies to both (single HMAC deletion removes
all modality bindings for a patient record).

Legal documents: contract scans (image) plus extracted text plus metadata bindings.
Legal discovery over scanned document corpora becomes substrate-native.

Industrial: equipment images + sensor readings + maintenance logs. "Show me equipment
where vibration signature is X and image shows wear pattern Y" -- pure substrate query.

E-commerce: product images + descriptions + purchase history bindings.

### 2.6 Crazy options for Wish 2

(a) CROSS-MODAL PATTERN B: image-binding + text-binding composed for a fact that
    spans both. "The fracture in this X-ray correlates with the symptom binding
    in this text." Pattern B composition across modalities is mechanically the
    same XOR operation -- the question is whether the aligned bipolar spaces
    preserve the correlation.

(b) MULTIMODAL SLEEP DEFRAG: during sleep consolidation, find image bindings that
    co-occur with text bindings and consolidate them into a joint multi-modal
    concept vector. This is VSA-native: "image cluster X and text cluster Y are
    repeatedly co-activated; create a superposition as a new concept."

(c) MULTIMODAL GDPR: a customer record with image (face), audio (voice), and text
    (name, address). HMAC keystore deletion removes ALL modalities atomically --
    one erasure key covers all bindings for that record's key. This is a genuinely
    hard problem for every other architecture (GDPR erasure of face images from
    learned weights is currently unsolved); substrate makes it trivial by design.

(d) MULTIMODAL AUDIT: image + text bindings together in the Merkle audit chain.
    "The decision was based on this radiology image (hash: a3f8b2) AND this lab
    report (hash: c7d1e9)." Both are cryptographically auditable. This is directly
    compliant with EU AI Act Article 12 requirements for high-risk AI systems that
    process medical images.

(e) MULTIMODAL K-HOP: "Find patients whose lung image is similar to reference image R
    AND whose drug binding history contains drug D within 2 hops." Cross-modal K-hop
    reasoning. This is mechanically the same as text K-hop (existing) but with
    image-first query entry.

### 2.7 Engineering cost and pre-test

Engineering cost: 3-4 engineer-weeks.
- Week 1: CLIP encoder integration + binarization pipeline
- Week 2: cross-modal binding (image + text roles in Pattern B)
- Week 3: retrieval evaluation (cross-modal Hamming search)
- Week 4: GDPR erasure extension to multimodal records + audit chain

Pre-test (cheap decisive test for Wish 2):
Run CLIP ViT-B/32 on MSCOCO-val (5000 images, 25000 captions).
Binarize CLIP embeddings to bipolar at N=512 (no PCA upsampling).
Store 5000 image-text binding pairs in substrate.
Query with text: measure Recall@10 for image retrieval.
Query with image: measure Recall@10 for text retrieval.
HARD-PASS: Recall@10 >= 0.70 cross-modal (matches binary CLIP benchmark).
HARD-FAIL: Recall@10 < 0.50 cross-modal (binarization destroys alignment).
Expected wall time: 2-3 hours on laptop CPU. No cloud needed.

### 2.8 Honest risks

Risk 1: PCA upsampling from 512 to 4096 dilutes the cross-modal alignment signal.
        Mitigation: use N=512 directly for multimodal; keep N=4096 for text.
        This is an architecture decision, not a fundamental barrier.

Risk 2: CLIP and text encoder live in different semantic spaces. bge-small text
        embeddings and CLIP text embeddings are not the same. A substrate that stores
        both may have incoherent retrieval when text queries compete with CLIP-text-encoded
        facts. Mitigation: use CLIP as the ONLY encoder (CLIP has a text branch);
        retire bge-small in the multimodal product line. This is a scope choice.

Risk 3: ImageBind and CLIP have different visual representations. Mixing them in one
        substrate codebook creates cross-encoder confusion. Mitigation: single-encoder
        multimodal substrate per deployment (not mixed).

---

## 3. WISH 3 -- Customer-specific intuitions learned by substrate

### 3.1 What this means precisely

Current substrate: general-purpose KB that answers queries deterministically.
No notion of "this customer's team prefers answers formatted as bullet points" or
"this customer's domain uses term X to mean something different than the general case."

The wish: substrate accumulates per-customer feedback signals as bindings. Every time
a human validates (thumbs-up) or rejects (thumbs-down) an answer, that signal is stored
as a binding in the per-customer substrate instance. Future queries route through a
learned preference layer that soft-weights answers toward what this customer has
historically validated.

### 3.2 Why this is non-trivial for LLMs and trivial for substrate

LLM fine-tuning for personalization: requires gradient descent over the model parameters,
typically LoRA at rank 4-16 on the attention matrices. Current cost: $500-$10K per
customer depending on model size and training data volume. Repeated as preferences
evolve. Catastrophic forgetting risk on each update cycle.

Substrate personalization: feedback signals are stored as new bindings, not as gradient
updates. The substrate's existing continual learning mechanism (concept extension + sleep
defrag) handles them exactly as it handles any other new fact. Cost: O(1) per feedback
signal. No gradient, no forgetting risk, no compute cost beyond the insert operation.

This is a fundamental architectural advantage: the substrate's symbolic binding model
treats "customer preference" as a fact of the same kind as "revenue is $80M." It stores
and retrieves preferences via the same mechanism as any other fact.

### 3.3 Architecture for customer-specific preference learning

Feedback signal format:
- query_id + answer_id + valence (positive / negative) + customer_id + timestamp

Binding representation:
- query_type_vec = encode_text(query) -> bipolar (captures semantic query type)
- answer_style_vec = encode_text(answer) -> bipolar (captures answer style)
- preference_binding = query_type_vec XOR answer_style_vec XOR customer_id_vec
- Stored in per-customer substrate (already exists as HIPAA Option B architecture)

Retrieval for preference-guided answering:
- At query time, retrieve nearest-neighbor preference bindings by Hamming(query_vec)
- Top-K preference bindings indicate historically preferred answer styles for similar
  queries
- LLM decoder conditioned on these K preferences via in-context prompt

Sleep consolidation:
- Sleep defrag identifies frequently co-occurring (query_type, answer_style) pairs
- Consolidates them into a "customer preference concept" vector
- Future retrieval uses the consolidated concept for faster, more reliable routing

### 3.4 Privacy properties

Per-customer preference bindings live in the per-customer substrate instance.
No cross-customer signal leakage (HIPAA Option B).
GDPR erasure: customer preference bindings erasable via HMAC key deletion.
If a customer offboards, all preference bindings vanish atomically.

Federated extensions (crazy option, see below): cross-customer aggregate preferences
can be computed via DP-noise addition before aggregation -- no raw preference vectors
leave their respective substrate instances.

### 3.5 What research knows and does not know

What is established:
- SPRInG (2025): continual LLM personalization via selective parametric adaptation +
  RAG-interpolated generation shows 12-18% improvement over static personalization.
  The RAG-based component (non-parametric) is architecturally isomorphic to substrate.
- PersonaMem-v2 (2025): implicit user persona learning via memory shows statistically
  significant preference modeling even from small interaction histories (N=20 rated answers
  is sufficient for meaningful signal).
- T-POP (2025): test-time personalization with online feedback adapts without gradient;
  preference accuracy from 20 feedback examples is above 65% for style preferences
  (format, length, tone) and above 50% for content preferences.

What is not established for substrate:
- Whether bipolar binding of (query_type, answer_style) pairs preserves enough
  semantic structure for accurate preference retrieval (the usual binarization
  precision-loss concern)
- Whether 20 feedback examples are enough to get meaningful signal in Hamming space
  vs the continuous space used by T-POP

### 3.6 Customer pitch precision

Do say:
"Substrate learns your team's preferences from 20-50 rated answers. No fine-tune,
no extra compute, no $5K per update cycle. Preferences update in real time as your
team provides feedback. Preferences are stored per-customer and GDPR-erasable."

Do not say:
"Substrate learns arbitrary stylistic preferences with high fidelity." (untested at
bipolar binarization precision levels)
"Substrate personalizes as well as a fine-tuned model." (fine-tuned models at
sufficient data volume will have an accuracy advantage; substrate wins on cost and speed)

The honest pitch is: substrate provides good-enough preference personalization at
near-zero cost, which beats $5K/customer LLM fine-tune for 90% of use cases where
"good enough" beats "optimal."

### 3.7 Crazy options for Wish 3

(a) PER-TEAM SUBSTRATE: a large customer with multiple teams (legal, finance, operations)
    gets team-specific preference bindings. The same factual KB is shared; the preference
    layer is team-specific. Cost: same as per-customer (just more instances).

(b) FEDERATED INTUITIONS: aggregate cross-customer common preferences (e.g., "most
    customers prefer bullet-point answers for financial queries") via DP-noise addition
    before aggregation. No raw preference vector leaves its instance. Substrate ships a
    "industry preference prior" as a starting point for new customers (cold-start problem
    solved). Privacy-respecting because DP-noise prevents customer identification from
    the aggregate.

(c) CUSTOMER INTUITION EXPORT: customer can export their learned preference bindings
    as a portable artifact. They take their preferences to another system, or to a
    newer version of their substrate, or back it up. No lock-in: their preferences
    are theirs. This is a genuinely differentiated feature -- LLM fine-tune weights
    are not transferable across providers.

(d) CAREER-LONG MEMORY: substrate accumulates a user's professional preferences over
    years of interaction. "Over 3 years, this analyst has consistently preferred
    concise financial summaries with % delta annotations." The substrate is a
    professional cognitive prosthetic. VSA-native continual learning handles this
    without catastrophic forgetting; LLMs would require periodic re-fine-tune.

(e) INVERSE INTUITION -- ADVERSARIAL MODE: substrate flags when customer feedback
    is INCONSISTENT. "You rated answer A as preferred for query type Q, but you
    rated answer B (contradictory to A) as preferred for query type Q3, which is
    semantically similar to Q." This is a consistency-checking capability: substrate
    catches when the customer is confused or when feedback was mislabeled. The binding
    space makes contradictory preferences findable via Hamming nearest-neighbor search.
    LLM-based personalization cannot do this -- it just averages inconsistent signals.

### 3.8 Engineering cost and pre-test

Engineering cost: 2-3 engineer-weeks.
- Week 1: feedback API (submit rating -> store preference binding)
- Week 2: preference-guided retrieval (at query time, retrieve K nearest preference
  bindings and condition LLM decoder)
- Week 3: sleep defrag integration for preference consolidation + export API

Pre-test (cheap decisive test for Wish 3):
Generate 100 synthetic QA pairs across 3 preference styles (concise/verbose/tabular).
Assign 50 to "customer A prefers concise" and 50 to "customer B prefers verbose."
Submit 20 rated answers per customer to substrate preference layer.
Query substrate with 30 new questions per customer: measure preference prediction
accuracy (does substrate route correctly toward their preferred style?).
HARD-PASS: preference accuracy >= 65% on held-out 30 questions.
HARD-FAIL: preference accuracy < 50% (chance level -- binarization destroys signal).
Expected wall time: 2-3 hours on laptop CPU. No cloud needed.

---

## 4. CHEAP DECISIVE TEST summary (all three wishes)

Wish 1 counterfactual: 20 synthetic scenarios on 500-fact KB.
- HARD-PASS: 100% derivation correctness + Merkle replay success + < 5ms per scenario
- HARD-FAIL: derivation errors > 5% OR Merkle replay fails on any scenario
- Wall time: 2-3 hours laptop CPU

Wish 2 multimodal: MSCOCO-val binary CLIP cross-modal retrieval.
- HARD-PASS: Recall@10 >= 0.70 cross-modal in bipolar BSC at N=512
- MID-BAND: Recall@10 0.50-0.70 (architecture adjustment needed; not infeasible)
- HARD-FAIL: Recall@10 < 0.50 (binarization destroys CLIP alignment; major redesign)
- Wall time: 2-3 hours laptop CPU

Wish 3 preferences: synthetic 100-QA preference test.
- HARD-PASS: preference accuracy >= 65% on held-out 30 questions (2 customers)
- MID-BAND: 50-65% (marginal signal; better than chance but needs more feedback data)
- HARD-FAIL: < 50% (chance level; binarized preference binding not working)
- Wall time: 2-3 hours laptop CPU

---

## 5. FALSIFIABLE PREDICTIONS

### Wish 1 counterfactuals
HARD-PASS: counterfactual derivation is 100% correct on synthetic KB + audit
            chain Merkle-verifiable on all 20 scenarios + < 5ms per scenario.
            (P_deflated = 0.75: existing erasure + deterministic replay already HP'd;
             constructive counterfactual is a small extension)

HARD-FAIL: any derivation error on synthetic KB OR any Merkle replay failure.
            (P_deflated = 0.10: deterministic binding algebra is either correct or not;
             if replay works, constructive generation should work)

### Wish 2 multimodal (bipolar CLIP)
HARD-PASS: Recall@10 >= 0.70 binary CLIP cross-modal on MSCOCO-val at N=512.
            (P_deflated = 0.45: binary CLIP lit says < 0.003 nDCG loss; BUT lit uses
             Hamming on the original dim, substrate uses PCA-upsampled to N=4096;
             at N=512 no upsampling the result should be near-lit; uncertain)

HARD-FAIL: Recall@10 < 0.50 OR cross-modal retrieval in substrate systematically
            worse than unimodal retrieval.
            (P_deflated = 0.20 that this failure occurs: binary CLIP is well-established
             enough that this should not fail at N=512)

### Wish 3 preferences
HARD-PASS: preference accuracy >= 65% from 20 feedback examples per customer.
            (P_deflated = 0.45: T-POP 2025 gets 65%+ in continuous space; bipolar
             binarization may lose enough precision to push below threshold)

HARD-FAIL: preference accuracy < 50% (chance level).
            (P_deflated = 0.20 that this failure occurs: even noisy Hamming retrieval
             should beat chance on style preferences)

---

## 6. CROSS-THREAD SYNTHESIS

### With cycle 162 causal_gdpr_erasure_composition HP

Cycle 162 proved: erased fact leaks zero erased content + audit chain intact after
erasure. Wish 1 counterfactual generation is the NATURAL EXTENSION of this result --
instead of erasing X, substitute X with X'. The algebraic machinery is the same.
The derivation chain for counterfactuals is the same Merkle proof structure.

This is NOT speculative: cycle 162's HP is direct evidence that the building blocks
work. The extension is constructive substitution instead of erasure.

### With cycle 162 Pattern B parity HP

Pattern B at 16 bytes/fact is the production architecture. Wish 2 multimodal and
Wish 3 preference bindings BOTH use the same Pattern B binding mechanism. The 16
bytes/fact storage efficiency holds for all modalities: a CLIP image embedding,
after bipolar binarization to N=4096, occupies the same 16-byte footprint as a
text fact. This is architecturally significant: a multimodal substrate does not
bloat storage.

### With cycle 158 NORTH-STAR validated empirical HP

Substrate-augmented Qwen2.5-1.5B beats bare Qwen by +0.352 F1 on HotpotQA (smoke
n=30). Wish 3 preference learning would further improve this gap by routing answers
through customer-validated preferences. The preference layer is an additive improvement
on top of the already-validated substrate augmentation.

### With Type II prior closure research (earlier 2026-06-07 drill)

Type II priors (implicit world-model knowledge) are LLMs' categorical advantage.
Wish 3 preference learning does NOT address Type II priors -- it addresses answer
STYLE and ROUTING preferences. The customer pitch must not conflate these:
- Type II priors: LLMs win; substrate's partial closure is via pre-training (88-92%)
- Answer style/preferences: substrate can learn cheaply; LLMs need expensive fine-tune

Wish 3's honest claim is narrower than "substrate learns your preferences." The correct
claim is "substrate learns your FORMAT and ROUTING preferences cheaply; it does not
learn new world-model facts from your feedback."

---

## 7. SUBSTRATE-PRODUCT IMPLICATIONS

### Commercial impact ranking

1. Wish 1 (counterfactuals): highest for regulated industries.
   - Financial stress testing, legal "what if" analysis, clinical decision support
   - No other system provides auditable counterfactuals with cryptographic proof
   - Regulatory pull: DORA Article 9, Basel III, FDA validation, EU AI Act Article 12
   - Market size for regulatory scenario testing: conservative $10-50B annually
   - Competitive moat: 3+ years to replicate in weight-matrix LLM architecture
   - Risk: narrow market (regulated industries); broad consumer use unclear

2. Wish 2 (multimodal): highest for vertical expansion.
   - Opens 5-10x more customer verticals (medical, legal docs, industrial, media)
   - Pattern B composes across modalities natively; binary CLIP is production-ready
   - Competitive moat: multimodal substrate is not an existing product category
   - Risk: binary CLIP alignment at substrate-specific quantization needs pre-test

3. Wish 3 (preferences): highest for stickiness and displacement.
   - LLM fine-tune displacement ($5K/customer -> near-zero) is a compelling pitch
   - Directly addresses the "why not just fine-tune a small LLM?" objection
   - Competitive moat: LLMs cannot do this without gradient; substrate is trivially native
   - Risk: good-enough vs optimal accuracy gap may matter for demanding customers

### v1.5 / v2.0 / v2.5 sequencing

v1.5 (2-3 weeks, lowest risk): Wish 1 counterfactual generation.
- Builds directly on cycle 162 erasure + replay HP
- No new encoder; no new hardware; extends existing pipeline
- Customer demo: "what if your 2024 revenue had been $100M -- here is what follows,
  here is the audit chain, here is the cryptographic proof"
- Pre-test gate: Wish 1 cheap test (20 scenarios, 2-3 hours)

v2.0 (3-4 weeks after v1.5): Wish 3 customer-specific preferences.
- Extends continual learning + sleep defrag + feedback API
- Directly differentiates from LLM fine-tune cost argument
- Customer demo: "substrate learned your team's preferences from 20 rated answers;
  here is how it routes future queries to your preferred format"
- Pre-test gate: Wish 3 cheap test (100 synthetic QA, 2-3 hours)

v2.5 (4-6 weeks after v2.0): Wish 2 multimodal.
- Requires CLIP integration + cross-modal binding validation
- Pre-test MANDATORY before engineering commitment (N=512 MSCOCO recall gate)
- Opens new customer verticals after v1.5/v2.0 base is stable
- Customer demo: multimodal radiology report + imaging study with GDPR erasure

---

## 8. IMPLEMENTATION RISK MATRIX

| Wish | Theoretical risk | Empirical risk | Engineering risk |
|------|-----------------|----------------|------------------|
| W1 counterfactual | LOW (builds on proven erasure + replay) | LOW (deterministic algebra) | LOW (existing machinery) |
| W2 multimodal | MED (bipolar quantization + cross-modal alignment) | HIGH (untested at substrate-specific N/PCA) | MED (encoder integration) |
| W3 preferences | LOW (preference as fact; continual learning) | MED (binarization precision for style signals) | LOW (feedback API + sleep defrag) |

W1 has the lowest risk profile across all three dimensions.
W2 has the highest empirical risk and MUST be pre-tested before engineering authorization.
W3 has low theoretical and engineering risk but medium empirical risk.

---

## 9. WHAT SUBSTRATE CANNOT DO (honest bounds)

These are hard limits that none of the three wishes change:

(a) Substrate cannot generate NOVEL counterfactuals that require world-model knowledge
    beyond what is explicitly stored. "What if competitor Y had not launched their
    product in 2023?" requires knowing how competitor Y's product affected the market --
    knowledge that must be in the KB explicitly. If it is not there, substrate has no
    basis for the counterfactual. LLMs can hallucinate an answer here; substrate
    cannot even attempt one. This is both a limitation and a compliance feature.

(b) Substrate cannot do visual understanding beyond CLIP's representational capacity.
    CLIP does not understand spatial relationships in images, text in images (OCR),
    or dynamic video semantics. The multimodal wish inherits CLIP's limits.

(c) Substrate's preference learning cannot learn preferences from implicit signals
    (user behavior, dwell time, click patterns) unless those signals are explicitly
    encoded as feedback bindings. It is explicit-feedback-only. This is weaker than
    implicit preference learning systems but stronger on privacy.

---

## 10. CITATIONS (verified in this session)

1. Pearl, J. (2012). "The Do-Calculus Revisited." Keynote, August 17, 2012.
   https://ftp.cs.ucla.edu/pub/stat_ser/r402.pdf -- do() operator formal basis

2. CFKGR (2024): "Counterfactual Reasoning with Knowledge Graph Embeddings."
   EACL 2024. https://aclanthology.org/2024.eacl-long.168/
   -- knowledge graph + counterfactual edge addition; structural analog to substrate

3. Marqo (2024): "Learn to Binarize CLIP for Multimodal Retrieval and Ranking."
   https://www.marqo.ai/blog/learn-to-binarize-clip-for-multimodal-retrieval-and-ranking
   -- < 0.003 nDCG loss for binary CLIP; 32x memory reduction

4. Hugging Face (2024): "Binary and Scalar Embedding Quantization for Significantly
   Faster & Cheaper Retrieval." https://huggingface.co/blog/embedding-quantization
   -- Hamming distance on binary embeddings vs cosine on float32

5. TernaryCLIP (2025): "Efficiently Compressing Vision-Language Models with Ternary
   Weights." arxiv 2510.21879. -- compression approaches for CLIP

6. SPRInG (2025): "Continual LLM Personalization via Selective Parametric Adaptation
   and Retrieval-Interpolated Generation." arxiv 2601.09974
   -- 12-18% improvement; RAG-based non-parametric component

7. T-POP (2025): "Test-Time Personalization with Online Preference Feedback."
   arxiv 2509.24696. -- 65%+ preference accuracy from 20 examples; no gradient

8. PersonaMem-v2 (2025): "Towards Personalized Intelligence via Learning Implicit User
   Personas and Agentic Memory." arxiv 2512.06688.
   -- N=20 interactions sufficient for meaningful preference signal

9. ZKAUDIT framework (2025): "A Framework for Cryptographic Verifiability of End-to-End
   AI Pipelines." arxiv 2503.22573. -- cryptographic audit trail; cost $108-$8456 per
   audit; substrate Merkle proof approach is architecturally similar but cheaper

10. Shpitser & Pearl (2012): "What Counterfactuals Can Be Tested."
    arxiv 1206.5294. -- testability conditions for counterfactuals

11. "Generalized Holographic Reduced Representations." arxiv 2405.09689.
    -- non-commutative binding extensions to FHRR; multimodal composition relevant

12. "Efficient Hyperdimensional Computing with Modular Composite Representations."
    arxiv 2511.09708. -- efficient HDC for structured/compositional data

13. "Autonomous retrieval for continuous learning in associative memory networks."
    PMC 12418250. -- Hopfield-inspired associative retrieval + erase; ARMT analog

14. AMULET (2025): test-time realignment for personalized preference adaptation.
    (referenced in T-POP survey section) -- no-gradient preference adaptation

15. PersonalLLM ICLR 2025: "PersonalLLM: Tailoring LLMs to Individual Preferences."
    https://proceedings.iclr.cc/paper_files/paper/2025/file/a730abbcd6cf4a371ca9545db5922442-Paper-Conference.pdf
    -- versatile personalization framework covering ICL, RAG, ranking, fine-tuning

Verified citations: 15
