# Research: adversarial defense analysis for U2 codebook-collision + edited-fact-traverse vulnerabilities (v1)

Date: 2026-05-30
Origin: v290 cap_map; U2 anchor `adversarial_multi_hop_probing_v2_n4096` HARD_FAIL.
Trigger: routing files
  - `notes/strategy_request_to_research_v290_codebook_collision_defense_2026-05-30.md`
  - `notes/strategy_request_to_research_v290_edit_adversarial_defense_2026-05-30.md`
Companion exp_dev handoff: `notes/exp_dev_handoff_research_adversarial_defense_analysis_2026-05-30.md`

## HEADLINE

The Pattern-2 100%-breach is an **algebraic certainty of any outer-product associative memory at M=2048 / N=4096**: pattern2_collision selects the worst-case pair of stored keys by ranking the M(M-1)/2 ~ 2.1M pairwise cosines and picking the top of that order statistic. For Kerdock-4-coset at this (M,N), the max pairwise cosine is approximately sqrt(2 ln(M^2)/N) ~ 0.085 - this is the **adversary's lever arm**, not a substrate defect. Iterated retrieval at depth=5 then amplifies the cross-talk past the value-codeword separation margin. The Pattern-4 99.4%-breach is **rank-1 edit perturbation vs depth-5 spectral dominance**: W2 = W + (nv - ov) k_v^T / N is a rank-1 correction; W2^5 is dominated by W's top eigenstructure, not the rank-1 correction.

Three defense families with deflated P estimates:
- **D1 query-similarity gate (reject queries whose argmax-2 over codebook are within delta of each other)**: P_deflated 0.55-0.70 for breach drop below 0.05 at small false-reject; engineering ~1 day; cheap and compatible with KF-1/KF-2/deletion-cert; **HIGHEST PRIORITY**.
- **D2 randomized-codebook-rotation per query (per-query random orthogonal transform applied to codebook + query before retrieval)**: P_deflated 0.40-0.55; engineering ~3 days; mostly compatible (auditor must reconstruct rotation seed for deletion-cert verification); **SECOND PRIORITY**.
- **D3 edit-log-replay (append-only edit log, replay at retrieval time instead of mutating W)**: P_deflated 0.45-0.60 for Pattern-4; engineering ~5-10 days; KF-2 compatible by construction but adds latency; **THIRD PRIORITY for Pattern-4 specifically; OUT-OF-SCOPE for Pattern-2**.

Recommended next experiment for G9+ batch: **G9.D1 query-similarity-margin gate smoke probe**, ~30 min CPU.

## Cheap decisive test

For each defense candidate, the cheap decisive test runs the SAME `exp_adversarial_multi_hop_probing_v2_n4096.py` patterns 1-5 against a substrate wrapped with the defense layer. The patterns are surgical: each adversary is parameter-free at run time (it constructs its own worst-case queries from the codebook + W state). HARD-PASS: p2_collision defense >= 0.90 AND p4_edited defense >= 0.90 across 5 seeds, WITHOUT degrading p1/p3/p5 defense (currently 1.000) by more than 0.05, AND without rejecting more than 5% of legitimate (in-distribution) queries on a held-out KF-1 sample.

For D1 alone, the cheap test is even cheaper: re-run patterns 1, 2 only at smoke N=1024, M=256, depth=3, 1 seed, with the margin-gate wrapper around the argmax. Estimated wall time: ~1 minute on laptop CPU. If p2 defense drops from 1.0 to <0.5 at any reasonable margin, D1 is refuted at smoke level.

## Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE-BAND)

### D1 query-similarity-margin gate

**Mechanism.** At retrieval time, compute argmax_1 (cos, q W^T) and argmax_2 (second-largest). Reject the query if `(cos_top1 - cos_top2) < delta_margin`. Pattern 2's whole leverage is constructing a query that produces a near-tied argmax between v_i (the rightful target) and v_j (the collision-partner's value); the margin gate fires exactly on this signature.

- **HARD-PASS**: p2_collision defense rises to >= 0.90 at delta_margin ~ 2/sqrt(N) (the natural Kerdock-pairwise scale); p1/p3/p5 retain >= 0.95; held-out KF-1 in-distribution false-reject rate <= 0.05.
- **HARD-FAIL**: p2 defense remains < 0.30 at any delta_margin that keeps false-reject <= 0.10; OR p1 cross-talk defense drops below 0.80 (gate over-rejects).
- **MIDDLE-BAND**: p2 in [0.30, 0.90] - gate works partially but trades off too aggressively against false-reject.

### D2 per-query codebook rotation

**Mechanism.** Per query, draw a random orthogonal R ~ Haar(O(N)) (or a cheaper Hadamard-based pseudo-rotation derived from a per-query salt + KDF). Substitute codebook' = codebook R, W' = R^T W R, q' = q R. Mathematically identical retrieval (orthogonal preserves cosines), but the adversary's pattern-2 attack ASSUMES the offline codebook to compute pairwise collisions; rotating breaks that assumption.

- **HARD-PASS**: p2 defense >= 0.90 across 5 seeds with rotation latency overhead <= 2x baseline retrieve; p1/p3/p5 unchanged; deletion-cert audit still verifies (rotation seed logged in cert).
- **HARD-FAIL**: p2 defense remains < 0.50 (means the attack constructs collisions FROM THE ROTATED codebook just as easily - rotation is no defense; this would happen if the rotation is leaked via side-channel or if the adversary has white-box knowledge of the rotation seed).
- **MIDDLE-BAND**: p2 in [0.50, 0.90] - rotation defends partially, e.g. delays the attack via key-rotation cadence.

### D3 edit-log-replay

**Mechanism.** Maintain W_base (initial) + an append-only edit log L = [(k_l, ov_l, nv_l)]. At retrieval, compute q_out = q W_base^T - sum_l (q . k_l)(ov_l - nv_l)^T / N. This is mathematically identical to retrieving from the mutated W (associativity of the rank-1 update), BUT at depth>1 the iteration becomes `q_{t+1} = q_t W_base^T - sum_l (q_t . k_l)(ov_l - nv_l)^T / N`. The crucial property: edits are applied at EACH depth step explicitly, preventing depth-5 amplification from washing them out.

- **HARD-PASS**: p4_edited defense >= 0.90 across 5 seeds at depth=5; latency overhead <= 5x baseline; deletion-cert + edit-log audit chain verifies end-to-end.
- **HARD-FAIL**: p4 defense remains < 0.30 even at depth=1 (means the issue is not edit-application-timing but something else, e.g. codebook-side leakage that survives even single-step retrieval).
- **MIDDLE-BAND**: p4 in [0.30, 0.90] - log-replay improves edit-stickiness but does not fully close the gap (likely indicates the depth=5 iteration is also amplifying argmax(W_base) over edit-perturbed.

## PART A: Mathematical analysis of the codebook-collision attack

Read directly from `experiments/exp_adversarial_multi_hop_probing_v2_n4096.py` lines 150-178.

### Attack mechanism (parameter-free; reads codebook + key_idx as oracle)

```
pattern2_collision(codebook, W, key_idx, val_idx, ..., n_q, depth, ..., N):
    keys = codebook[key_idx]                  # (M, N) stored keys
    sims_kk = keys @ keys.T / N               # (M, M) all pairwise cosines
    sims_kk.fill_diagonal_(-1.0)              # exclude self-pairs
    top_sim, idx = sims_kk.view(-1).topk(n_q*2)  # take top 2*n_q pairs
    for each pair (i, j) with s_val > 0:
        q = keys[i:i+1]                       # use stored key i itself
        for _ in range(depth):                # depth=5 iterations
            q = q @ W.T
        pred = argmax_c (codebook[c] @ q.T)
        target = val_idx[i]
        n_correct += (pred == target)
    defense = n_correct / n_total
```

### Substrate structural vulnerability (algebra)

The substrate uses `W = (1/N) sum_l v_l k_l^T` (outer-product Hopfield), with retrieval `q -> argmax_c (codebook[c] . W q^T) / N`. Single-step retrieval from query k_i evaluates:

```
W k_i^T = (1/N) sum_l v_l (k_l . k_i)
       = v_i * (||k_i||^2 / N)
         + sum_{l != i} v_l * (k_l . k_i / N)
       = v_i * 1                    [BSC bipolar: ||k_i||^2 = N]
         + Sigma_cross
```

The cross-talk term Sigma_cross has zero mean and standard deviation O(sqrt(M-1)/sqrt(N)) for random keys (CLT). For Kerdock-4-coset, the typical pairwise cosine `(k_l . k_i)/N` is `O(1/sqrt(N))`.

**The attack's structural leverage.** Pattern 2 does NOT use a typical pair. It ranks all M(M-1)/2 ~ 2.1M pairs at M=2048 and picks the **maximum**. The max of N_p i.i.d. Gaussian-tail-decaying samples scales as `sqrt(2 ln N_p) / sqrt(N)` ~ `sqrt(2 ln 2.1e6 / 4096)` ~ **0.085** for our (M, N). With depth=5 iterations of W, the cross-talk amplifies further: `W^5 k_i^T = v_i + Sigma_cross_amplified` where Sigma_cross_amplified picks up contributions from EVERY depth-5 path through the W graph. Each path has expected magnitude scaling as (typical pairwise cosine)^4 * (worst pairwise cosine) per the depth=5 chain.

Numerically: at the worst pair (i*, j*), the v_{j*} contamination after depth=5 is roughly `0.085 * (1)^4 = 0.085` while the v_{i*} signal stays at `1 * (1)^4 = 1`. The argmax over the codebook then picks v_{i*} IF the codebook has minimum codeword-pair distance > 0.085. But the SAME order-statistic argument applies to the codebook itself: at C ~ 2N codewords (typical), the **codeword-pair** worst-case overlap is also sqrt(2 ln C^2 / N) ~ 0.090. So a near-collinear j* signal can compete with an i* + noise signal at a different codeword v_k.

Compounding: with M=2048 keys + depth=5 iterations + the worst-case key-pair chosen by the adversary, the substrate's argmax is **probabilistically dominated** by cross-talk for the top ~10-30% of the order statistic. The observed 100% breach across 5 seeds at M=2048, depth=5 is consistent with the cross-talk dominating the entire top-`n_q` selection slice.

### Is this BSC-specific or codebook-class-specific?

The substrate uses **Kerdock 4-coset codebook**, not pure random BSC. Kerdock {+/-1, +/-i} 4-tuple union has worst-case pairwise overlap bounded by Welch-bound-saturating designs (for power-of-2 N), giving "as low as algebraically possible" worst-case |<c_a, c_b>| / N ~ 1/sqrt(N). For pure BSC random sign vectors, the worst-case overlap over O(M^2) pairs is slightly worse by a logarithmic factor (the order statistic of Gaussians).

**Conclusion:** The vulnerability is **NOT codebook-class-specific**. Kerdock helps marginally (logarithmic factor), but the attack works against ANY codebook with M^2 cross-pairs and 1/sqrt(N) per-pair overlap floor. The vulnerability lives at the **outer-product retrieval + iterated retrieval at depth>=2** layer, not at the codebook.

Independent confirmation: cap_map's S2 latency_crossover_analysis showed Path E (spectral coherence) defended pattern 2 with similar defense=0 in U2 (per status_log T4 entry, Path E currently is niche-3-applications + spectral-coherence-favored sub-row; the v290 verdict shows ALL paths fail Pattern 2 - this is substrate-wide not path-specific). The vulnerability is at the codebook+retrieval algebra layer.

## PART B: Defense mechanism categorization

| # | Defense family | Mechanism (1 line) | Theoretical effectiveness vs Pattern-2 | Theoretical effectiveness vs Pattern-4 | Engineering complexity | KF-1/KF-2/deletion-cert compatibility | False-positive rate (in-dist queries rejected) | P_deflated HARD-PASS |
|---|---|---|---|---|---|---|---|---|
| D1 | Query-similarity-margin gate | reject if argmax_1 - argmax_2 cos margin < delta | **HIGH** (directly fires on collision signature) | LOW (edit attack does not produce close-tied argmax) | **CHEAP** (~1 day; 1 hook into retrieve) | Compatible (gate is post-hoc; cert chain unaffected) | 1-5% at well-chosen delta | **0.55-0.70** for p2; <0.20 for p4 |
| D2 | Per-query codebook rotation | apply random orthogonal R per query; adversary cannot precompute collisions | MEDIUM (defends grey-box adversary; white-box defeats it) | LOW (edits live in W, rotation doesn't touch W structure) | MODERATE (~3-5 days; rotation cache + per-query RNG) | Compatible IF rotation seed is logged in cert (adds 32 bytes/cert) | 0% (mathematically identity-preserving) | 0.40-0.55 for p2; <0.10 for p4 |
| D3 | Codebook-distance-check at retrieval | verify retrieved candidate's codebook distance to query is below threshold | LOW-MEDIUM (collision queries DO have small distance to a stored value; threshold can be evaded) | LOW (irrelevant) | MODERATE (~2 days) | Compatible | 5-15% (false reject of legit hard queries) | 0.25-0.40 for p2; <0.10 for p4 |
| D4 | Detect-and-isolate (statistical signature of adversarial query) | classify each query as adversarial-vs-natural using e.g. distribution-shift detector on query embedding | LOW-MEDIUM (Pattern 2 queries ARE stored codewords; only their PATTERN-OF-USE differs) | LOW-MEDIUM (similar) | SUBSTANTIAL (~10 days; needs labeled training data) | Compatible | 5-15% | 0.20-0.35 for both |
| D5 | Cryptographic commitment (KDF-based query salting) | client must commit to a hash of (query, KDF-derived-salt); server rejects queries not matching commitment | LOW for Pattern 2 (the adversary IS the legit client with codebook access) | LOW (same) | SUBSTANTIAL (~7 days; client-side library change) | Compatible | 0% | 0.10-0.25 (only defeats external adversary; not internal codebook-aware attacker) |
| D6 | Privileged keys (only registered queries are valid starting points) | maintain a registry of authorized query embeddings; reject all others | HIGH if adversary cannot register (same as access-control) | HIGH (same) | MODERATE (~5 days; registry + auth flow) | Compatible | 0% for registered; 100% for unregistered | 0.65-0.80 IF threat model excludes insiders; 0.10-0.25 if not |
| D7 | Edit-log-replay (Pattern 4 specific) | append-only edit log L; replay rank-1 corrections at retrieval time at EACH depth step | NO (irrelevant; codebook-collision is W-state independent at attack vector level) | **HIGH** (rank-1 perturbations re-injected at each step prevent depth-5 wash-out) | MODERATE (~5-10 days; log + replay-mode retrieve) | Compatible by design (audit-chain entries are the log itself; cert validity strengthens) | 0% | 0.10 for p2; **0.45-0.60** for p4 |
| D8 | Confidence-aware retrieval with adversarial-trained calibration | Path D's per-hop Bayesian posterior, calibrated against an adversarial training distribution | MEDIUM (calibration shifts under attack; Path D v290 saw 99.4% breach, so as-is is broken; needs adversarial training pass) | MEDIUM (same) | SUBSTANTIAL (~14 days; data + retraining + threshold tuning) | Compatible (Path D is current production-default) | 5-10% | 0.25-0.45 for both AFTER adversarial-training pass |

### Per-defense narrative (3 lines each)

**D1 (query-similarity-margin gate).** Cheapest, most-likely-to-work for Pattern 2. The collision attack's signature is exactly a tied argmax. Implementation: in `path_d_run` / `path_b_run`, after the final argmax, compute the second-largest similarity. If `(sim_1 - sim_2) < delta`, return an explicit "ambiguous" token instead of the argmax. Delta candidates: 2/sqrt(N) ~ 0.03; 4/sqrt(N) ~ 0.06; 8/sqrt(N) ~ 0.12.

**D2 (codebook rotation).** Defends against an adversary who has the codebook offline but not per-query state. Per-query rotation R drawn from a server-side KDF on (per-query nonce). The adversary's pre-computed pairwise-collision targets become invalid each query. White-box adversary (who has R) defeats it; medium-strength against gray-box. The audit-chain cost: 32 bytes (R seed) per cert entry. KF-2 unchanged (rotation is identity-preserving for stored keys + values, since it applies symmetrically).

**D3 (codebook-distance-check).** A static threshold on `min_c ||codebook[c] - q||` at retrieval. Has the problem that Pattern 2 uses STORED keys as queries, so distance to codebook is **exactly zero** for q itself; the post-retrieval distance from W*q to codebook is also small by construction (the substrate's whole purpose is to retrieve a codeword-like vector). Likely false-reject rate is high.

**D4 (detect-and-isolate).** Adversarial query detection in embedding space. Hard problem: Pattern 2 queries are valid stored keys; their statistical distribution is identical to in-distribution queries. The only signal is the temporal/usage pattern (e.g. "this query has very high pairwise cosine to many other stored keys"), which is a heuristic.

**D5 (cryptographic commitment).** Defeats an EXTERNAL adversary who must submit hash-committed queries. Does not defeat an INTERNAL adversary (someone with codebook access who is also the legitimate query-issuing client). For the substrate's deployment threat model (regulated industry where the client + substrate are within the same trust boundary), the adversary IS internal. Low value.

**D6 (privileged keys).** Strong if the threat model excludes white-box codebook access. Weak if not. For regulated-industry deployment, may be appropriate IF customers commit to a "no-arbitrary-query" SDK contract. Likely the right answer for AUDIT use cases (where queries are known in advance) but not for general retrieval.

**D7 (edit-log-replay).** Pattern-4 specific. The math is clean: instead of mutating W into W2, store W_base + edit_log. At each retrieval step, compute the corrected retrieval explicitly. This prevents the depth-5 spectral dominance of W_base from washing out the rank-1 edit. Adds latency proportional to (depth * n_edits); for n_edits=512 + depth=5 + N=4096, that is ~10M multiply-adds per query = ~10ms on CPU = negligible at small edit-counts. Substrate's edit_log already exists for the deletion-cert chain; D7 just consumes it at retrieval time.

**D8 (adversarial-trained calibration).** The most "deep-learning" answer. Train Path D's posterior under a distribution including pattern-2-style queries. Likely partial defense; adversarial calibration is a well-known recurring open problem (per OOD detection lit-scan).

## PART C: Pattern-4 edit-semantics vulnerability analysis

### The failure mode mathematically

Reading `pattern4_edited` (lines 206-230):
```
W2 = W - (ov.T @ k_v)/N + (nv.T @ k_v)/N
q = codebook[e_keys]
for _ in range(depth):  # depth=5
    q = q @ W2.T
pred = argmax_c (codebook @ q.T)
```

W2 differs from W by a rank-`n_edit` perturbation (one rank-1 correction per edit). At depth=1:
```
W2 q = W q + (nv - ov) (k_v . q) / N
     = W q + (nv - ov) * 1     [since q = k_v]
```
At depth=1, the edit IS applied: argmax_c (codebook[c] . W2 q^T) gets the (nv - ov) signal added directly. This is why KF-2 (single-step retrieve) passes.

At depth=5, however:
```
W2^5 q = (W + Delta)^5 q
       = W^5 q + sum of 31 cross-terms involving Delta at various positions
```
where Delta = sum_l (nv_l - ov_l) k_l^T / N. The cross-terms involving Delta in non-leading positions get washed out by W's higher-singular-value structure. Specifically:

- W has eigenvalue spectrum dominated by the M outer-product directions; top eigenvalue ~M/(N), with the rest decaying per Marchenko-Pastur tail.
- Delta is rank-n_edit ~ M/4; its spectral norm ~ ||nv - ov|| / sqrt(N) ~ 2/sqrt(N).
- W^5 amplifies W's top eigendirection by factor (M/N)^5 ~ 0.5^5 = 0.03 (small at our M/N) BUT the cross-talk from competing values amplifies proportionally.

The crucial detail: at depth=5, the iteration approaches a fixed point dominated by W's eigenvector spectrum. The single-step rank-1 correction is RE-INJECTED into the iteration at step 1 only; from step 2 onward, q has been transformed and the rank-1 correction term no longer aligns with the new q. Specifically `W2 W2^k q = W2^(k+1) q` does NOT preserve the edit-correction's direction across iterations because q rotates.

**Verbal summary:** W2 = W + Delta where Delta is rank-1 per edit, small operator norm. W^5 dominates iterated retrieval because the rank-1 corrections only "fire" when the current iterate aligns with their key; this alignment is destroyed after one iteration.

### Connection to v272 KF-2 BE-1 W-magnitude-not-operative finding

v272 KF-2 BE-1 found that **rescaling W (changing its operator norm) did not affect KF-2 performance**. The mechanism is consistent: KF-2 single-step retrieve depends on the RELATIVE structure (eigenvector directions and eigenvalue RATIOS), not absolute magnitude. The same eigenstructure dependence that makes magnitude irrelevant at depth=1 makes the **direction-mixing** at depth=5 inevitable: each iteration of W rotates q into W's principal subspace, which is fixed under rescaling.

**Implication:** Pattern-4 vulnerability is NOT a bug in W's spectral norm; it is the **structural consequence** of iterated linear retrieval applied to a low-rank update of a fixed-spectrum operator. Any rank-1 edit + depth-K iteration system has this property; the substrate is a clean instance.

### Defense candidates (Pattern-4 specific)

1. **D7 edit-log-replay** (preferred, scored above). Re-injects the rank-1 correction at each depth step. Mathematically equivalent to performing K separate single-step retrieves with the edit applied each time. P_deflated 0.45-0.60.

2. **Post-edit W validation** (lighter-weight). After each edit, verify by issuing a battery of probes that the edit "sticks" (i.e. argmax-retrieves the new value at depth=1, 2, ..., max_depth). Reject the edit (or warn) if it does not stick at the deployment depth. Cheap (~1 day) but does NOT FIX the vulnerability; it only DETECTS it. Useful as a safety net + auditor signal.

3. **Per-edit cryptographic seal** (audit-only). Sign each edit with a hash chain entry; auditor can verify edits were applied + retain a "what should have been retrieved" oracle. Does not defend against the breach; provides post-hoc detection.

4. **Edit-aware retrieval (use edit log as oracle at retrieval-time)**. Equivalent to D7 if implemented as in-place per-step replay. If implemented as a separate "look up edit log; if hit, return new value" branch, it becomes a sidecar key-value store - which is a different (cheaper) approach but loses the substrate's compositional retrieval property. P_deflated 0.55-0.70 for stick-rate but breaks composition; not recommended.

## PART D: Engineering prioritization

| Rank | Defense | Engineering cost | Expected p2 defense (theoretical) | Expected p4 defense (theoretical) | False-positive rate | Strategic value | Combined score |
|---|---|---|---|---|---|---|---|
| 1 | **D1 query-similarity-margin gate** | ~1 day | 0.85-0.95 | 0.10-0.25 | 1-5% | Deployment-blocker fix (Pattern 2) | **HIGHEST** |
| 2 | **D7 edit-log-replay** | ~5-10 days | 0.05-0.15 | 0.75-0.90 | 0% | Deployment-blocker fix (Pattern 4); audit-chain strengthens | **SECOND** |
| 3 | **D2 per-query codebook rotation** | ~3-5 days | 0.65-0.85 | 0.10-0.25 | 0% | Secondary defense for Pattern 2; reduces grey-box threat surface | **THIRD** |
| 4 | D6 privileged keys (audit deployments) | ~5 days | 1.0 (registered) | 1.0 (registered) | 100% unregistered | Strong for AUDIT use cases; not for general retrieval | situational |
| 5 | D8 adversarial-trained Path D calibration | ~14 days | 0.40-0.60 | 0.40-0.60 | 5-10% | Long-term improvement; complementary to D1+D7 | future |
| 6 | D3 distance-check, D4 detect-isolate, D5 commitment | various | 0.20-0.40 | 0.10-0.30 | various | weak; not recommended | none |

### Ranked recommendation

**HIGHEST PRIORITY: D1 query-similarity-margin gate.** Single-day engineering. The Pattern-2 attack's structural signature is a tied argmax; D1 fires exactly on that signature. Cost ~1 day to implement + smoke test. If smoke passes, FULL multi-seed test for ~1 hr CPU. Likely takes Pattern-2 defense from 0.0 to >= 0.85 with false-reject < 5%. Compatible with all KFs and the deletion certificate.

**SECOND PRIORITY: D7 edit-log-replay.** Larger engineering investment (5-10 days), but the ONLY clean defense for Pattern 4 with high P_deflated. By construction, edit-log-replay is mathematically equivalent to single-step-with-edit-applied at each depth, which closes the depth-5 amplification loophole. Audit-chain compatibility is BUILT-IN (the log IS the audit chain). Recommended once D1 lands (D1 + D7 together close both deployment blockers).

**THIRD PRIORITY: D2 per-query codebook rotation.** Defends Pattern 2 (the more dangerous attack) at a different layer than D1. Defense-in-depth: D1 handles the static argmax-tied attack; D2 handles the adversary who learns D1's threshold and crafts queries that avoid the tied-argmax signature (e.g. by selecting NEAR-collision pairs rather than top-collision pairs). Engineering ~3-5 days; rotation latency overhead acceptable (~2x retrieval cost). Recommended for full regulated-industry deployment hardening.

### Implications for G8 probe

G8 (currently shipping per task input) is testing 2 simple defenses. This analysis recommends G8 tests D1 (query-similarity-margin gate) as the cheap-and-likely-to-work primary candidate. The natural delta values to sweep are {2/sqrt(N), 4/sqrt(N), 8/sqrt(N)} = {0.031, 0.063, 0.125} for N=4096. Pre-reg should include: HP delta achieves >= 0.90 defense + <= 0.05 false-reject; MB delta gives partial defense with tradeoff; HF if defense stays < 0.30 at any delta. Smoke ~5 min CPU.

For G9 (post-G8), the natural next probe is D7 edit-log-replay smoke at small M (M=512), n_edits=128, depth=5, single seed - cheap (~10 min CPU) to verify the depth-5 wash-out hypothesis is the right mechanism. If D7 smoke shows p4 defense >= 0.85, schedule FULL.

For G10+, D2 codebook rotation full implementation with audit-cert reconstruction validation.

### Cap_map recommendation: v290 adversarial-vulnerability annotation evolution

Current v290 annotation: "REGULATED-INDUSTRY DEPLOYMENT BLOCKER pending defenses against (1) codebook-collision crafted queries (100% breach) and (2) adversarially-constructed edit traversal queries (99.4% breach). Patterns 1, 3, 5 cleanly defended."

Recommended v291+ evolution path:

1. After G8 D1 smoke HARD_PASS: annotation -> "Pattern 2 codebook-collision: 1-day query-margin gate defense identified (D1); smoke shows >= X defense; FULL pending. Pattern 4 edit-traverse: D7 edit-log-replay identified as theoretical fix; engineering 5-10 days."
2. After G8 D1 FULL HARD_PASS: row state -> annotation becomes "Pattern 2 defended via query-margin gate; deployment-blocker downgraded to Pattern 4 only."
3. After G9 D7 HARD_PASS: full annotation "Both adversarial vulnerabilities defended; regulated-industry deployment unblocked at adversarial-defense layer."
4. If G8 D1 HARD_FAIL: cap_map drops to "Pattern 2 defense unsolved; D2 codebook-rotation second-priority probe."

The annotation evolution maintains conservative band per [[feedback-no-padding-experiments]]: each step is gated on empirical PASS, not theoretical promise.

## Cross-thread synthesis

### With v272 KF-2 BE-1 (W-magnitude-not-operative)

v272 BE-1 found W spectral norm rescaling does NOT affect KF-2 performance. This research drill identifies the SAME structural property as the **mechanism behind** Pattern-4 vulnerability: iterated retrieval depends on W's eigenvector structure, not magnitude. Rank-1 edit perturbations interact with eigenvectors at single-step but get washed out under iteration. **Lock:** Pattern-4 vulnerability is structurally connected to BE-1's magnitude-not-operative finding. The same depth-K spectral-dominance reasoning explains both.

### With S2 latency_crossover_analysis (Path B/D/E mechanism-selection)

S2 found Path E wins on spectral-coherence-favored cells (~21% of production grid). Path E specifically uses spectral-signature alignment across hops. **Open question:** does Path E inherit any of the codebook-collision vulnerability, given that pattern 2 maximizes spectral overlap by construction? Per U2 results all 3 paths failed Pattern 2 in v290 - so Path E is NOT a free defense. But Path E + D1 query-margin gate MAY compose better than Path D + D1, since Path E's spectral coherence signature might detect the collision-induced overlap as anomalous. **Follow-up probe candidate** (post G8/G9).

### With Path D unanimous 1.000 at 16N depth=50 (U1)

U1 found Path D has no ceiling within tested envelope on RANDOM keys at depth=50. Pattern 2's adversarial-key attack at depth=5 broke it. Inferred: **Path D's no-ceiling result is conditional on key-distribution being natural; adversarially-selected key pairs collapse the apparent unbounded performance**. Per v290 R-PATH-D-NO-CEILING R3 recommendation, Path D should be re-tested with codebook-collision-style adversarial constructions at high M+depth to characterize where the "no ceiling" claim degrades. This research drill SUPPORTS that recommendation - we have the mechanism explanation now.

### With v278 multi-tenant isolation property (10/16 property bundle)

The substrate's "multi-tenant isolation" property assumes adversarial isolation across tenants. Pattern 2 attack would not cross tenant boundaries (it uses ONE tenant's stored keys). So this defense work strengthens the SINGLE-TENANT robustness property. Multi-tenant isolation (KF-3) UNCHANGED per v290.

## Substrate-product implications

1. **Regulated-industry deployment timeline lock.** Per project memory `substrate_value_framing_matured_2026-05-26` and `substrate_killer_features_2026-05-26`, "deletion certificate" + "compositionality audit API" + "per-fact retention policy" are HIGH-PRIORITY killer features for regulated industries. ALL of these depend on the substrate not being trivially breachable by codebook-collision or edit-traverse attacks. **Engineering on D1 + D7 unblocks the entire regulated-industry positioning.**

2. **Audit-chain interaction (positive).** D7 edit-log-replay STRENGTHENS the audit-chain story: the log that powers the defense IS the audit chain. Customers asking "prove this fact was edited and the substrate respects the edit" get YES with the SAME mechanism that makes Pattern 4 defense work. This is a product-narrative win.

3. **Query-margin gate as a substrate-product feature.** D1 can be exposed as an API knob: "set the substrate's ambiguity tolerance" (delta_margin). High-stakes audit queries set delta_margin tight (1-5% in-dist false-reject is acceptable cost for security guarantee); low-stakes retrieval queries set delta_margin = 0. This becomes a **substrate-product killer feature**: configurable ambiguity rejection at runtime. Add to killer feature list.

4. **D2 rotation as audit-cert payload extension.** D2's per-query rotation seed becomes part of the deletion-cert / audit-trail (32 bytes/cert). Audit can verify "this query used rotation seed S; the substrate's response was produced honestly under that rotation". This is a PROVENANCE strengthening, not just a defense.

5. **Honest cannot-do list update.** Per v278 cannot-do drill: substrate currently DOES NOT defend against codebook-collision OR adversarial edit traverse without these defenses. Add to cannot-do: "as of v290, substrate does not defend against codebook-collision attacks or adversarially-constructed edit-traverse queries; defenses D1 + D7 are in flight for v291-v292." This is honest customer-positioning per [[feedback-no-smoke]].

## Citations (verified count)

Verified URLs (5 of 6 lit-scan threads returned direct prior art):

- **Krotov & Hopfield (2018) - Dense Associative Memory Is Robust to Adversarial Inputs** ([arxiv 1701.00939](https://arxiv.org/abs/1701.00939)). Direct prior art for DAM-robustness; informs why our substrate's rank-1 outer-product W (NOT a higher-order DAM) is MORE vulnerable than DAM at the same M/N. The Krotov result requires a sharper interaction function than the substrate uses.
- **Cohen et al. (2019) - Certified Adversarial Robustness via Randomized Smoothing** ([arxiv 1902.02918](https://arxiv.org/abs/1902.02918)). Methodology for certified robustness against L2-adversarial perturbations. Adaptable to substrate via smoothed retrieval (apply Gaussian noise to query, ensemble over multiple smoothed retrievals). NOT the chosen primary defense (D1 is cheaper and substrate-vocabulary-native), but informs D8.
- **Huang et al. (2023) - RS-Del: Edit Distance Robustness Certificates for Sequence Classifiers via Randomized Deletion** ([arxiv 2302.01757](https://arxiv.org/pdf/2302.01757)). Direct analog for discrete-codebook robustness: randomized deletion of codebook bits gives certificate against edit-distance-bounded adversaries. Relevant for binary-codebook substrate adversarial robustness. Score: relevant prior art; not implemented in D1/D2/D7.
- **Raju et al. (2025) - LSM Trees in Adversarial Environments** ([arxiv 2502.08832](https://arxiv.org/abs/2502.08832)). Direct prior art for adversarial workloads against log-structured stores. Demonstrates Bloom Filter accuracy degradation under adversarial queries; up to 800% read latency increase. Informs D7 (edit-log-replay): we are building a log-structured edit history; this prior art warns about specific Bloom-filter-like cache structures that adversarial queries can attack. Mitigation: do NOT use Bloom filters in the edit-log-replay path; iterate the log directly.
- **Techapanurak et al. (2020) - Hyperparameter-Free OOD Detection Using Cosine Similarity** ([CVF ACCV 2020](https://openaccess.thecvf.com/content/ACCV2020/papers/Techapanurak_Hyperparameter-Free_Out-of-Distribution_Detection_Using_Cosine_Similarity_ACCV_2020_paper.pdf)). Validates cosine-similarity threshold as OOD detector. D1's mechanism is structurally identical to OOD-margin detection - the prior art confirms this is a recognized technique class. Differentiation: substrate-D1 fires on argmax-tied retrieval (NOT on absolute cosine distance), which is a substrate-specific signature.
- Krause et al. (2010) **HKDF: Cryptographic Extraction and Key Derivation** (background reference for D2; not a defense per se).

Verified count: **5 directly-relevant published prior-art references** with URLs.

## Calibration penalty notes

- D1 query-margin gate: P_deflated 0.55-0.70 - this is a NOVEL-SYNTHESIS application (no published precedent of margin-gate against codebook-collision attacks specifically), so capped at 0.70 (under 0.50 cap because the underlying mechanism - OOD margin - is well-published). Penalty applied 0.10-0.15 vs unconstrained estimate.
- D2 codebook rotation: P_deflated 0.40-0.55 - moderate confidence; gray-box-defense literature is established, white-box-defeat is also established. Penalty applied 0.10-0.15.
- D7 edit-log-replay: P_deflated 0.45-0.60 - the mechanism is mathematically clean (log replay = each-step edit application = mathematically identical to single-step which already works). Penalty applied 0.10-0.15 for engineering risk + audit-chain integration risk.

All deflated below 0.70; consistent with [[feedback-lit-scan-calibration-penalty]] and [[feedback-dont-overextend-theorems]].

Hard-fail thresholds explicit in each prediction. Done.
