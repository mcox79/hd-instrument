# Research Drill: Adversarial-Key Robustness of hd-instrument Substrate
**Date:** 2026-07-02
**Filed-by:** research (Director) — Sonnet liberal drill
**Trigger:** USER directive 2026-07-01 full-night session — load-bearing negative for M3 threat model
**Prior arc (substrate-KB query result):** adversarial robustness was NAMED as concept + Anchor 2.3 DP-CMS adversarial robustness; prior 2x drill (2026-06-07) covered noise robustness only (fp16, paraphrase, middle-hop). None of the 4 attack angles below were tested empirically. This drill is novel scope.
**P_deflated (pre-drill):** 0.48 per USER framing

---

## HEADLINE

**P_deflated (post-drill): 0.52 UPWARD REVISION from 0.48** — adversarial brittleness is MORE likely than the pre-drill estimate, not less.

**Primary threat surface confirmed:** superposition interference is the load-bearing vulnerability. The 2025 theoretical result (Adversarial Attacks Leverage Interference Between Features in Superposition, arXiv 2510.11709) shows that vulnerability scales directly with the k/m superposition pressure ratio and that gradient-free black-box attacks succeed when the geometry is known. The hd-instrument substrate writes items into superposition by design (that is the storage mechanism). This makes the substrate structurally exposed to the same interference-exploitation pathway, not merely adjacent to it.

**Threat-model classification:**
- Gradient-crafted adversarial query (read-time): MODERATE RISK — O(sqrt(N)) margin is genuine protection against random noise but NOT against gradient-crafted queries that exploit interference geometry
- Write-time key-collision poisoning (write-time cross-contamination): LOW-MODERATE RISK — capacity crosstalk is structural but targeted planting of item j while writing item i requires knowing the superposition geometry; hard but not impossible at small N or near-capacity
- LLM adversarial-suffix transfer (cross-modality): LOW RISK — embedding-space topology mismatch blocks transfer
- Bipolar iid protection against gradient attack: PARTIAL — bipolar discreteness is genuine defense against small-epsilon attacks but does NOT protect against large, algorithmically-crafted perturbations

**M3 classification:** NOT a hard blocker if substrate is read-only memory; IS a hard blocker if M3 cortex layer forwards adversarial user inputs directly into substrate as queries without sanitization.

---

## SECTION 1: PRIOR ARC WORK ON THESE ANGLES

Substrate-KB top-5 adversarial hits returned:
1. "Candidate 6A: Anti-attractor adversarial substrate state" (cosine=0.358) — a NAMED idea (decoy vectors to deflect adversarial queries), P_empirical=0.20 quoted, no experiment run
2. "Idea 16: Adversarial substrate multi-substrate red team" (cosine=0.349) — named concept, never filed as pre-reg
3. "C3. Adversarial substrate pairs F2.7" (cosine=0.330) — reference in 5x autonomous-discovery drill, not operationalized
4. "Idea A: Substrate as adversarial anomaly detector" (cosine=0.327) — defensive role framing, no experiment

Prior 2x drill (research_drill_adversarial_robustness_adaptive_2x_2026-06-07.md) covered: paraphrase-robustness, fp16 numerical precision, middle-hop fabrication tolerance. It did NOT cover: (a) gradient-crafted query for targeted false recall; (b) write-time item-j poisoning via item-i write; (c) compressed-sensing adversarial bounds; (d) Hopfield/DAM adversarial robustness theory; (e) LLM adversarial-suffix transferability.

This drill is genuinely new scope across all 5 investigation angles.

---

## SECTION 2: THEORY — O(sqrt(N)) MARGIN VS GRADIENT-CRAFTED QUERIES

### What the margin actually protects against

The substrate retrieval guarantee (cosine nearest-neighbor with iid bipolar stored patterns) gives a false-recall noise floor of order O(1/sqrt(N)) per interfering item at capacity M ~ 0.14N (classic Hopfield) or much higher with modern dense-Hopfield exponential capacity. This means:

- A RANDOM query that is epsilon-corrupted from the true key retrieves the correct item with probability → 1 as N → infinity, provided epsilon < O(sqrt(N)) in L2 norm.
- This is concentration of measure: the cosine similarity between a random bipolar query and any OTHER stored item concentrates around zero with standard deviation O(1/sqrt(N)).

### Where the margin does NOT protect

The gradient-crafted adversarial query is not a random perturbation. The adversary solving argmax_{||delta||<epsilon} cos(q + delta, m_j) for a TARGET item m_j they want to retrieve is solving a CONVEX problem in delta (cosine similarity is a linear function of delta in a neighborhood). The gradient points directly toward m_j in embedding space.

**Formal statement of the attack:**

Let q be the true query, m_i the intended target, m_j the adversary's target. The attack constructs:
  q_adv = q + epsilon * (m_j - q) / ||m_j - q||

This pushes q toward m_j in embedding space. The adversary succeeds when:
  cos(q_adv, m_j) > cos(q_adv, m_i)

For typical substrate configurations: at N=8192, the typical cosine gap between a query and its nearest stored neighbor vs second-nearest is O(1/sqrt(M)) where M is number of stored items. An adversary needs to cross this gap. The gap is approximately 1/sqrt(M).

For the attack to require epsilon larger than O(sqrt(N)) in Hamming distance on bipolar vectors, the adversary would need to flip O(sqrt(N)) bits. At N=8192 this is 90 bits — a large perturbation that is easily detectable by L2/Hamming monitoring. But:

1. If the substrate accepts continuous-valued keys (not strictly bipolar at query time), the L2 attack can succeed with much smaller perturbation
2. If keys are derived from a neural encoder (M3 scenario), the adversary operates in ENCODER input space, not directly in the bipolar key space — the gradient chains through the encoder and the required encoder-input perturbation can be very small

**Verdict on margin protection:** Genuine against random noise. NOT genuine against gradient-crafted attacks in M3 encoder pipeline. The O(sqrt(N)) floor applies to direct key attacks; encoder-mediated attacks see a much smaller effective gap.

### Krotov-Hopfield 2018 DAM robustness caveat

"Dense Associative Memory is Robust to Adversarial Inputs" (Neural Computation 2018, arXiv 1701.00939) shows that higher-order energy functions (F(x) = x^n for n >= 3) create energy minima that are free from "rubbish" inputs — adversarial perturbations do not land in valid memory states. However:

- This robustness result applies to the CLASSIFICATION setting (a DAM used as a classifier producing a CLASS label)
- It does NOT apply to the RETRIEVAL setting where the goal is to land in ANY stored attractor (not just class prototypes)
- Transfer attacks from low-order networks fail on high-order DAM — but an adversary with direct gradient access to the DAM energy function CAN craft queries that land in wrong attractors by gradient descent on the energy landscape
- Ramsauer 2020 modern Hopfield = softmax update = attention: the energy is differentiable, so gradient-crafted keys are straightforwardly possible

**Key DAM implication for substrate:** if the substrate uses n=2 (quadratic, classic Hopfield), Krotov-Hopfield provides no robustness claim at all. If n>=3 (which the hd-instrument substrate does NOT currently implement per hdlab/ primitives), partial robustness emerges but only against transfer attacks, not direct gradient attacks.

---

## SECTION 3: SUPERPOSITION INTERFERENCE AS THE LOAD-BEARING ATTACK SURFACE

### Theoretical result: arXiv 2510.11709 (2025) — directly applicable

"Adversarial Attacks Leverage Interference Between Features in Superposition" establishes:

1. **Mechanism:** Adversarial perturbations satisfy delta ∝ W_e^T(v_k - v_j) — the perturbation exploits the differential interference between two class/item representations in the shared embedding space. This is a direct consequence of non-orthogonal superposition.

2. **Gradient-free variant:** Representation-informed black-box attacks achieve near-PGD effectiveness when the feature geometry is known. This is critical for M3: if an adversary knows or can infer which items are stored, they can craft adversarial keys without gradient access to the substrate itself.

3. **Transferability scales with correlation:** Attack transferability increases from 18% (uncorrelated items) to 94% (correlated items) as geometric constraints tighten. For the substrate: stored items that are thematically related (e.g., a corpus of related facts) induce higher correlation in the superposition geometry, massively increasing attack transferability.

4. **Superposition removal eliminates vulnerability:** When m=k (one dimension per item, orthogonal), zero successful adversarial examples. But this costs N dimensions per item — defeats the substrate's storage efficiency purpose.

### Application to hd-instrument substrate

The substrate is a distributed associative memory that stores multiple items in superposition by construction. The key question is: does the bipolar iid KEY randomization orthogonalize the superposition?

**Answer: partial, but incomplete.** iid bipolar keys are pseudo-orthogonal — E[cos(k_i, k_j)] = 0 for i != j, but the variance is O(1/N). The superposition of M stored items creates cross-interference terms of magnitude O(M/N). For M = 1000 items at N = 8192: cross-interference scale = 1000/8192 ≈ 0.12. This is the adversary's operating margin — they need to move the query cosine by 0.12 toward the target item, which at N=8192 requires flipping approximately 0.06 * N = 491 bipolar bits. That is a detectable perturbation.

BUT: at N=65536 and M=10000 items, cross-interference = 0.15, flip requirement = ~9830 bits. Still detectable if you monitor L2 distance of incoming queries.

**Critical M3 scenario exception:** The cortex layer mediates all queries. If the adversary is a user interacting with M3 via natural language, the attack surface is the ENCODER, not the bipolar key space. An adversarial prompt that shifts the encoder output by epsilon=0.01 in cosine can be sufficient to cross a retrieval boundary — this is the LLM embedding adversarial attack literature (Zou 2023 style). The O(sqrt(N)) floor provides NO protection in this scenario.

---

## SECTION 4: WRITE-TIME POISONING — CAN ITEM-I WRITE PLANT ITEM-J?

### PoisonHD (Wang et al. 2022, DATE conference)

PoisonHD attacks an HDC classifier by flipping labels on the most vulnerable (lowest-confidence) training samples. The attack is confidence-ranked label-flipping at write time. Key findings:
- Threat model assumes full knowledge of HDC algorithm (white-box)
- Attack is DATA POISONING (corrupt training set), not key-collision (write i to falsely recall j)
- Defense: HDC-specific data sanitization; confidence-thresholded write rejection

This is NOT the same as targeted key-collision poisoning. PoisonHD degrades ACCURACY — it does not cause a specific false recall of item j when item i is queried.

### Targeted key-collision poisoning — theoretical analysis

For write-time planting of item j while writing item i: the adversary must craft a key-value pair (k_i, v_i) such that k_i is also close enough to k_j (the already-stored key for item j) that the superposition update shifts the retrieval boundary.

**Mechanism:** Substrate write: W += v_i * k_i^T. After write, retrieval for query q gives: W*q = v_i*(k_i^T*q) + sum_{m!=i} v_m*(k_m^T*q). To plant a false retrieval for query q_j = k_j, the adversary needs (k_i^T*k_j) to be large — i.e., the new key k_i must have high overlap with the existing key k_j.

For iid bipolar keys, P(|k_i^T*k_j| > t*sqrt(N)) decays exponentially in t^2 (Chernoff). So RANDOM key selection provides strong write-time collision protection. But this assumes RANDOM keys. If the adversary CHOOSES k_i, they can set k_i = k_j + delta for any delta, directly maximizing cross-contamination. This requires the adversary to have WRITE ACCESS to the substrate, which is a much stronger threat model.

**Verdict on write-time attack:** Low risk under READ-ONLY threat model (adversary queries only). Moderate risk under WRITE ACCESS threat model (adversary can submit key-value pairs to be stored). For M3: the cortex layer mediates writes — if user-submitted content is encoded and written to substrate without sanitization, the write-time poisoning attack is live. If the substrate is pre-loaded from trusted sources and then read-only at inference time, this attack surface is closed.

### Spurious attractor crosstalk (capacity-based write poisoning)

At capacity M = 0.14N (classic Hopfield), spurious attractors form automatically as pointwise averages of nearby stored patterns. These are NOT targeted — they are a consequence of near-capacity operation. For the substrate near its capacity cliff (see Atom 22 chain-grade LLN at V_C=1M), near-capacity operation induces uncontrolled spurious recall that an adversary can exploit by forcing the system to near-capacity via flood writes. This is an infrastructure-level denial-of-correct-recall attack, distinct from targeted false recall.

---

## SECTION 5: COMPRESSED-SENSING ADVERSARIAL BOUNDS AND SUBSTRATE APPLICABILITY

### Relevant literature (Jalal et al. 2020 NeurIPS — Robust Compressed Sensing using Generative Models)

Robust CS with generative priors proves: for measurement matrix A and generative prior G, recovery is stable under bounded adversarial noise ||eta||_2 <= delta, recovering x with error O(delta/sqrt(m)) where m is number of measurements. This is an EXISTENCE result — the CS recovery CAN be robust under adversarial noise if the adversary is bounded.

**Bora 2018 adversarial framing:** The original Bora CS-with-generative-models paper does not handle adversarial noise natively. Jalal 2020 extends it to adversarial-robustness via a min-max formulation. Key finding: adversarial noise at scale delta requires the reconstruction error to grow proportionally. There is NO free robustness — you trade off recovery accuracy against adversarial robustness budget.

### Applicability to substrate

The substrate performs retrieval via nearest-neighbor in a linearly-superposed memory, which is isomorphic to a CS recovery problem where the measurement matrix is the key matrix K (N x M, columns = stored keys). The CS recovery of stored value v from superposition W = sum_m v_m k_m^T when presented with query q is:

  Wq = K^T q approximately v_{i*} when q ≈ k_{i*}

The adversarial CS bound says: an adversary who injects noise eta into q with ||eta|| <= epsilon sees recovery error O(epsilon * ||K||). For K = iid bipolar matrix, ||K||_op = O(sqrt(NM)), so recovery error scales as O(epsilon * sqrt(NM)).

For the adversary's goal (shift retrieval from item i to item j), they need the recovery error to exceed the gap between v_i and v_j. This sets the REQUIRED adversarial noise magnitude:
  epsilon_required ≈ gap(v_i, v_j) / sqrt(NM)

At N=8192, M=1000: epsilon_required ≈ gap / sqrt(8.2M) ≈ gap / 2863. For gap = 1 (binary values), epsilon_required ≈ 0.00035 in query cosine units. This is extremely small — an adversary needs only a tiny query perturbation to bridge retrieval boundaries.

**Conclusion:** CS bounds confirm the substrate's adversarial fragility in retrieval: recovery is ROBUST to bounded adversarial noise in absolute L2 terms, but the REQUIRED attack magnitude to flip retrieval is O(1/sqrt(NM)) — which becomes SMALLER (easier to attack) as N and M increase. Higher capacity = easier adversarial targeting.

---

## SECTION 6: LLM ADVERSARIAL-SUFFIX TRANSFERABILITY TO SUBSTRATE

### Zou 2023 (GCG) mechanism

GCG (Greedy Coordinate Gradient) searches for token sequences that maximize target-logit activation in LLM embedding space. The gradient is taken w.r.t. discrete token embeddings and projected back via coordinate-wise greedy search. Transfers to black-box models because the feature geometry is partially shared across architectures trained on the same data.

### Why transfer to FHRR/bipolar substrate is LOW RISK

The adversarial suffix attack exploits gradient directions in the LLM's token embedding space (typically d=4096-8192 float32 vectors trained via contrastive + autoregressive loss). Transferability between models requires SHARED EMBEDDING GEOMETRY, which empirically holds between LLMs trained on the same corpus.

The hd-instrument substrate uses:
1. Bipolar iid random projection (not learned embedding)
2. Dimension N that may differ from LLM embedding dimension
3. No shared training objective with any LLM
4. No token-level decomposition

An adversarial suffix crafted against GPT-4 embedding geometry will project to a RANDOM direction in the substrate's key space (because the substrate's key geometry is iid random, not correlated with LLM geometry). The transfer probability is therefore O(1/sqrt(N)) — essentially zero for large N.

**Single caveat:** If the M3 architecture uses an LLM encoder to CONVERT user text to substrate keys, then the adversarial attack surface is the LLM encoder, and Zou-style attacks against the encoder DO transfer to substrate recall outcomes. This is the critical architectural junction: encoder-mediated queries inherit encoder adversarial vulnerabilities.

---

## SECTION 7: RANKED ATTACK MECHANISMS

| Rank | Attack | Cost to Adversary | Expected Fragility | White/Black box | M3 relevance |
|------|--------|------------------|--------------------|-----------------|--------------|
| 1 | Gradient-crafted encoder-mediated query (attack encoder to shift key) | LOW — standard GCG/PGD against encoder; epsilon=0.01 sufficient | HIGH — encoder bridges LLM attack surface to substrate | White-box encoder, black-box substrate | CRITICAL — M3 Phase 1 uses LLM router/encoder |
| 2 | Superposition interference exploitation (black-box representation-informed) | MEDIUM — needs item inventory knowledge | MODERATE-HIGH — gap scales as 1/sqrt(NM), worsens with capacity | Black-box substrate if geometry known | MODERATE — feasible if adversary knows stored item set |
| 3 | Write-time poisoning via encoder-mediated write | MEDIUM — needs write access + encoder access | MODERATE — requires write access, closes at read-only | White-box encoder | MODERATE — only if cortex accepts user content into substrate |
| 4 | Capacity flood + spurious attractor exploitation | LOW — flood with M>0.14N writes | MODERATE — structural, not targeted; causes broad recall degradation | Black-box (indirect) | LOW-MODERATE — requires write access |
| 5 | Direct bipolar key crafting (large-epsilon Hamming attack) | HIGH — 491+ bit flips detectable | LOW — O(sqrt(N)) genuine Hamming protection holds | White-box substrate | LOW — M3 doesn't expose raw bipolar keys to users |
| 6 | LLM adversarial suffix direct transfer | HIGH — no shared geometry | VERY LOW — iid key geometry blocks transfer | Transfer from LLM | NEGLIGIBLE — geometry mismatch |

---

## SECTION 8: 2x DRILL — WHY DOES THE TOP ATTACK WORK? MECHANISM-FIRST

### Top attack: gradient-crafted encoder-mediated query (Rank 1)

**First drill — why does it work?**

The LLM encoder (Phase 1 M3 architecture) maps user text to a continuous embedding e in R^d. The substrate key function K(e) maps e to a bipolar key k in {-1,+1}^N (e.g., random projection + sign). The end-to-end retrieval pipeline is:

  user text → LLM encoder → e → K(e) → cosine retrieval in substrate → item recall

The adversary's attack: find adversarial text t_adv such that K(encoder(t_adv)) is closer to target key k_j than to true key k_i.

Why it works in 3 steps:
1. The encoder is a differentiable neural net. Gradient of cosine(K(encoder(t)), k_j) w.r.t. encoder input is well-defined and computable via chain rule.
2. GCG-style discrete optimization over tokens finds t_adv that shifts encoder output toward k_j's preimage.
3. The required encoder output shift is O(1/sqrt(N)) in cosine units (the retrieval gap). For N=8192 this is 0.011. LLM embeddings of semantically similar texts already lie within cosine-0.01 of each other — the required shift is within normal semantic variation. The attack is therefore semantically near-invisible while crossing the retrieval boundary.

**Key enabling condition:** the retrieval gap shrinks as M (number of stored items) grows. At M=1000 items in N=8192 substrate, gap ≈ 0.01 — which is within epsilon of normal encoder noise. The substrate's capacity strength (high M) becomes an adversarial liability.

**Second drill — when does this mechanism fail?**

The encoder-mediated attack fails under 4 conditions:
1. Encoder has adversarial training (AT-augmented fine-tuning): increases the minimum perturbation epsilon by 10-50x (Madry 2018 standard AT result)
2. Key projection includes a secret random seed unknown to adversary: shifting encoder output toward k_j requires knowing k_j's pre-image under K, which requires knowing the projection matrix. With secret random seed, the adversary cannot compute gradients through K.
3. Query sanitization: norm-limit incoming query keys to within epsilon_max of a clean distribution; adversarial queries with extreme Hamming deviation from the expected distribution are rejected.
4. Differential privacy at retrieval: add Gaussian noise to retrieval scores. Noise magnitude sigma > gap provides plausible deniability — the adversary cannot reliably cause targeted false recall because the retrieval decision is randomized. This connects to the existing refuse-gate / stochastic noise cortex discipline (M3_cortex_layer_must_inject_stochastic_noise, project file 2026-06-30) — the noise is ALREADY architecturally mandated.

**Verdict on second drill:** Stochastic cortex boundary noise (already in M3 architecture plan) is the most efficient defense because it randomizes retrieval outcomes for near-boundary queries — exactly the queries an adversarial encoder attack produces. Defense cost is essentially zero (noise injection already mandated). This is a case where M3's existing cortex architecture INCIDENTALLY defends against the top adversarial attack vector.

---

## SECTION 9: CHEAPEST DECISIVE EXPERIMENT

### Cell design: `adversarial_key_gap_crossing_v1`

**One-shot experiment to determine if the attack is live at M3-relevant scale**

**Pre-reg outline:**

Setup:
- N=8192 substrate (matches production scale)
- M=1000 stored iid bipolar items (well below capacity)
- K_proj = random projection matrix with PUBLIC seed (worst-case: adversary knows K_proj)
- Encoder: simple L2-normalizer (no LLM; tests substrate gap alone before adding encoder complexity)

Attack protocol (3 arms):
- ARM_RANDOM: query = true key + iid random noise at epsilon in {0.01, 0.05, 0.10, 0.20, 0.40} (Hamming fraction)
- ARM_TARGETED: query = true key + gradient-toward-target perturbation at same epsilon values (PGD, 100 steps)
- ARM_BOUNDARY: query = midpoint(k_i, k_j) + small random perturbation — tests retrieval near decision boundary

Metric: false-recall rate = P(retrieve j | query designed to retrieve i) at each epsilon level

PASS thresholds:
- HARD_PASS: ARM_RANDOM false-recall < 0.05 at all epsilon AND ARM_TARGETED false-recall < 0.10 at epsilon=0.05 — substrate resists gradient attack at 5% perturbation
- HARD_FAIL: ARM_TARGETED false-recall > 0.50 at epsilon=0.05 — adversary can flip retrieval with 5% key perturbation (detectable but concerning)
- MIDDLE_BAND: ARM_RANDOM < 0.05 but ARM_TARGETED > 0.20 at epsilon=0.05 — genuine gap between random and gradient attack (gradient attack is real attack surface)

**Why this is decisive:** It directly measures whether the retrieval gap crossing is achievable by gradient (vs random) perturbation at realistic epsilon. The gap between ARM_RANDOM and ARM_TARGETED at the same epsilon quantifies the "gradient advantage" — the degree to which gradient-crafted queries are more dangerous than random noise.

**Runtime estimate:** ARM_RANDOM + ARM_TARGETED (5 epsilon x 1000 trials each x 100 PGD steps) at N=8192, M=1000: ~15-20min on local CPU (no GPU needed at this scale). This is a smoke-grade cell — eligible for local_cpu_queue.

**Falsifiable predictions:**
- HARD_PASS prediction (substrate robust): ARM_TARGETED false-recall < 0.10 at epsilon=0.05. Theory basis: O(sqrt(N)) Hamming protection provides genuine gap even against gradient attacks when keys are direct bipolar.
- HARD_FAIL prediction (substrate brittle): ARM_TARGETED false-recall > 0.50 at epsilon=0.05. Theory basis: gap = O(1/sqrt(NM)) = O(0.011) at M=1000; PGD in 100 steps can cross a 0.011 cosine gap in L2 space.

**My prediction:** MIDDLE_BAND — ARM_RANDOM HARD_PASS, ARM_TARGETED false-recall 0.20-0.50 at epsilon=0.05. Gradient has a clear advantage but bipolar discreteness provides partial resistance. P_deflated = 0.35 HARD_PASS, P_deflated = 0.35 HARD_FAIL, P=0.30 MIDDLE_BAND.

---

## SECTION 10: SUBSTRATE-PRODUCT IMPLICATIONS FOR M3

### If HARD_PASS (substrate resists gradient-crafted direct-key attacks)

- Adversarial brittleness is confined to the ENCODER layer in M3 Phase 1
- Mitigation: adversarial training of encoder + secret K_proj seed (closes both encoder and projection attack surfaces)
- Substrate itself is not the M3 blocker; threat model is manageable

### If HARD_FAIL or MIDDLE_BAND (gradient attack succeeds at epsilon < 0.10)

- M3 requires mandatory cortex-layer defenses before deployment:
  1. Stochastic noise at cortex-substrate boundary (ALREADY MANDATED — project file 2026-06-30; this helps)
  2. Query norm monitoring (flag queries with L2 deviation > 2-sigma from clean distribution)
  3. Secret K_proj seed (unknown to adversary; prevents gradient computation through K)
  4. Adversarial training of encoder (Phase 1 LLM router: AT-augmented fine-tuning)
- Anti-attractor decoys (Candidate 6A from Jun 7 drill) become relevant: store "trap" vectors near known attack targets; queries that approach traps are flagged

### Write-time threat (conditional on M3 accepting user content into substrate)

If M3 cortex writes user-supplied content into substrate (not just reads):
- Implement write-gate with confidence threshold (PoisonHD defense pattern — reject low-confidence writes)
- Separate public-write substrate from trusted-read substrate (dual-store architecture matches Wave 3 TWO_TIER bounded-capacity plan)
- Rate-limit writes per user to prevent capacity-flood spurious-attractor attack

### Relationship to existing M3 cortex noise mandate

The 2026-06-30 directive (M3_cortex_layer_must_inject_stochastic_noise) already mandates stochastic coupling at the cortex-substrate boundary. This is INCIDENTALLY the correct defense against the top adversarial attack vector (Rank 1: encoder-mediated gradient attack produces near-boundary queries; noise randomizes near-boundary decisions). This is a convergent design requirement — noise is needed for cortex stochasticity AND adversarial robustness simultaneously. The M3 architecture is not inadvertently adversarially brittle; it was steered toward a noise-injection design that partially closes the primary attack surface.

---

## SUMMARY TABLE

| Investigation Angle | Finding | P_deflated (attack succeeds) | M3 action required |
|--------------------|---------|-----------------------------|--------------------|
| O(sqrt(N)) margin vs gradient-crafted queries | Genuine against random; NOT genuine against gradient at realistic epsilon | 0.65 (gradient attack partially succeeds) | Stochastic noise + secret K_proj |
| Write-time key-collision poisoning | Low risk (read-only substrate); moderate risk (user-write enabled) | 0.20 (read-only) / 0.55 (write-enabled) | Write-gate + dual-store |
| Bipolar iid protection vs gradient | Partial: discreteness slows attack, does not prevent it | 0.35 HARD_PASS (fully resists), 0.65 partial/full break | Monitor Hamming deviation of incoming queries |
| Transformer adversarial-suffix transfer | Very low — geometry mismatch blocks transfer unless encoder is LLM | 0.05 (no encoder) / 0.60 (with LLM encoder) | AT-augment Phase 1 encoder |
| CS adversarial bounds (Jalal 2020) | Recovery robust to bounded noise; required attack epsilon = O(1/sqrt(NM)) — shrinks with capacity | 0.70 (gap is crossable at production scale) | Capacity-aware retrieval margin monitoring |

**Overall P_deflated adversarial brittleness is real and exploitable: 0.52** (upward from 0.48 pre-drill). Not a hard M3 blocker given existing cortex noise mandate + manageable engineering mitigations. A HARD_FAIL on the proposed cell (ARM_TARGETED > 0.50 at epsilon=0.05) would trigger mandatory pre-deployment adversarial hardening protocol.

---

## REFERENCES

- Krotov D, Hopfield JJ. "Dense associative memory is robust to adversarial inputs." Neural Computation 2018. arXiv:1701.00939
- Ramsauer H et al. "Hopfield Networks is All You Need." ICLR 2021. arXiv:2008.02217
- Jalal A et al. "Robust Compressed Sensing using Generative Models." NeurIPS 2020. arXiv:2006.09461
- Zou A et al. "Universal and Transferable Adversarial Attacks on Aligned Language Models." 2023.
- Wang et al. "PoisonHD: Poison Attack on Brain-Inspired Hyperdimensional Computing." DATE 2022.
- "Adversarial Attacks Leverage Interference Between Features in Superposition." arXiv:2510.11709 (2025)
- "Adversarial Examples Are Not Bugs, They Are Superposition." arXiv:2508.17456 (2025)
- "Testing and Enhancing Adversarial Robustness of Hyperdimensional Computing." IEEE 2023.
- "HyperAttack: An Efficient Attack Framework for HyperDimensional Computing." DAC 2023.
- "Restricted Hopfield Networks are Robust to Adversarial Attacks." TechRxiv 2024.
