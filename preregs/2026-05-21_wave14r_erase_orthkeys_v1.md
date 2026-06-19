# Pre-registration: wave14r_erase_orthkeys_v1

Date: 2026-05-21
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14r_erase_orthkeys_v1.py](../experiments/exp_wave14r_erase_orthkeys_v1.py)
Priority source: [active_priorities.md](../notes/active_priorities.md) Bet 2 (E2),
gated on Research R1 — see [research_R1_GDPR_erase_candidates_2026-05-21.md](../notes/research_R1_GDPR_erase_candidates_2026-05-21.md)
Author: experiment_dev session, cycle 3

## Why

Bet 2 (GDPR-grade surgical erase) is currently ❌ after two independent
failures of anti-Hebbian erase on correlated keys (wave14p_erase_multiprobe,
wave14anneal_selective). R1's Pass-2 drill recommends a Kerdock-coset
structured-codebook key family as the highest-probability rehabilitation
path (75–90% predicted success rate by construction, Variant 2A.i with
snap-to-codebook paraphrase semantics).

**v1 simplification — read carefully.** R1's full-fidelity recipe requires
implementing the Kerdock code construction (Z₄-Gray map, 2^24 codewords) and
a snap-to-codebook decoder. v1 implements the **Hadamard subcode**
(Kerdock-1, the linear subcode), which gives **exactly orthogonal keys** at
M_stored ≤ N. The R1 derivation hinges on bounded pairwise inner products
creating no "bridge" pathways from paraphrase probes back to erased values;
the Hadamard subcode is the *extreme* of this — zero bridges — so it is
the cleanest falsifier of the load-bearing claim "structured keys remove
the bridges that cause Mirage." Three consequences:

1. v1 does not need snap-to-codebook. At M_stored = 200, N = 4096, all
   codeword pairs in the stored subset are exactly orthogonal; a paraphrase
   at Hamming distance h ≤ N/3 is still nearer to its origin codeword
   than any other, so snap is trivially identity and adds no semantic.
2. If v1 PASSES the multi-probe battery, the structured-keys family is
   alive — v2 then implements full Kerdock and snap, which test the
   higher-density codebook regime where snap matters (M > N).
3. If v1 FAILS, structured keys with orthogonality don't break Mirage —
   denser codebooks won't either. Closes the Kerdock-coset family for the
   substrate; routes to paraphrase-aware ROME (Candidate 3' in R1).

This is consistent with R1's design intent (Variant 2A.i is the highest-
probability candidate; v1 tests the cleanest case of its core claim
before drilling implementation depth) AND with the playbook's
"smaller experiments > one big one."

## Hypothesis

Replacing rank-L correlated keys (the wave14p Mirage-failure regime) with
mutually-orthogonal Hadamard-subcode keys, holding everything else
constant, will cause the anti-Hebbian rank-1 erase to pass all five
Mirage probes simultaneously.

Concretely, at N=4096, M_stored=200, anti-Hebbian erase at α∈{1.0, 1.5, 2.0},
5 seeds, n_erase=30 per seed, Hamming-h paraphrase probes at h∈{2,4,8,16}:

- argmax_leak on Hadamard arm < 0.05 (vs correlated arm Mirage failure
  ~0.20–0.50 depending on α)
- mean_rank on Hadamard arm > 100 (vs correlated arm ~5–20)
- norm_ratio on Hadamard arm < 0.15 (vs correlated arm ~0.30–0.70)
- paraphrase_leak at h=8 on Hadamard arm < 0.05 (vs correlated arm
  ~0.20–0.30)
- kept_preservation on Hadamard arm > 0.95 (vs correlated arm comparable;
  this is the side-effect probe)

The correlated arm replicates wave14p_erase_multiprobe's Mirage failure
within the same script, so the comparison is internally controlled.

## Multi-probe success criteria

For Hadamard arm at the best α (per the Mirage paper's 4-probe battery
+ kept-preservation as a 5th):

1. argmax_leak < 0.05
2. mean_rank > 100
3. norm_ratio < 0.15
4. paraphrase_leak < 0.05 at Hamming h=8
5. kept_preservation > 0.95 over 100 random kept facts

AND the correlated arm at the SAME α reproduces a Mirage failure (failing
at least 2 of {rank, norm, paraphrase_leak} per criteria thresholds). The
contrast — Hadamard passes where correlated fails — is the load-bearing
finding.

## Kill criteria (close the structured-keys family at v1)

- Hadamard arm fails ≥ 2 of {rank, norm, paraphrase_leak} at every α: the
  basic claim "orthogonal keys remove Mirage bridges" is false.
- Hadamard arm passes probes only at very-high α where kept_preservation
  drops < 0.85: the substrate can't tolerate the erase magnitude needed.

If either kill triggers, route to paraphrase-aware ROME (R1 Candidate 3').

## Verdict labels (6)

- `STRUCT_KEYS_FIX_MIRAGE` — Hadamard arm passes all 5 criteria; correlated
  arm reproduces Mirage at same α. Structured keys validated at v1; route
  to v2 for the dense-codebook Kerdock case.
- `STRUCT_KEYS_PARAPHRASE_FAIL` — Hadamard arm passes argmax/rank/norm/kept
  but paraphrase_leak ≥ 5% at h=8. Surprising; rehabilitation suggestions
  in verdict_msg.
- `STRUCT_KEYS_KEPT_FAIL` — Hadamard arm passes 4 probes but
  kept_preservation < 0.95. Erase too aggressive; sweep α down.
- `STRUCT_KEYS_ARGMAX_ONLY` — Hadamard arm reproduces same Mirage failure
  as correlated (rank/norm probes fail). Closes the structured-keys family.
- `STRUCT_KEYS_BASELINE_NOT_BROKEN` — correlated arm UNEXPECTEDLY passes
  multi-probe; the wave14p Mirage failure doesn't reproduce. Indicates a
  test-setup divergence from wave14p — investigate before drawing
  substrate conclusions.
- `STRUCT_KEYS_INCONCLUSIVE` — missing data.

## Oracle assertions (smoke mode)

1. `oracle.assert_in_range("hadamard_orthogonality", max_pairwise_ip_hadamard, (0.0, 0.01))`
   — Hadamard arm pairwise inner products must be essentially zero. If not,
   codebook construction is broken.
2. `oracle.assert_in_range("correlated_pairwise_std", correlated_arm_pairwise_std, (0.03, 0.50))`
   — correlated arm pairwise std must be in the wave14q-replicated range.
3. `oracle.assert_baseline_high("baseline_argmax", baseline_argmax_pre_erase, 0.70)`
   — without erase, both arms must successfully retrieve the stored facts
   under argmax (else storage is broken).
4. `oracle.assert_distinguishable("hadamard_vs_correlated_argmax", hadamard_leak, correlated_leak, min_gap=0.05)`
   — at the smoke's α, the two arms must produce different outcomes;
   if identical, the test isn't measuring the structural difference.

## Pre-mortem (3 failure causes — playbook)

1. **Hadamard codebook construction has off-by-one or sign error**, producing
   approximately-orthogonal but not exactly-orthogonal keys. Mitigation:
   smoke oracle 1 catches it.
2. **Erase under Hadamard keys leaves the erased value as the top non-self
   match for paraphrase probes** (a topology-of-cleanup issue, not a
   bridge issue), reproducing failure-by-a-different-mechanism. Mitigation:
   verdict label `STRUCT_KEYS_ARGMAX_ONLY` distinguishes this from a clean
   Mirage failure; rehabilitation moves to "increase α + measure kept."
3. **Correlated arm fails to reproduce wave14p Mirage**: makes the
   structured-keys comparison meaningless. Mitigation: dedicated verdict
   label `STRUCT_KEYS_BASELINE_NOT_BROKEN`; routes to test-setup audit
   rather than substrate conclusion.

## Operational definition

- **Hadamard arm**: keys drawn without replacement from the 8192-row Sylvester
  Hadamard codebook (4096 rows × ±1 sign). M_stored=200; all pairwise IPs
  are exactly 0.
- **Correlated arm**: keys constructed via
  [`make_correlated_keys(N, rank_L, n_facts)`](../experiments/exp_wave14q_rome_vs_antihebbian.py)
  (signed projection of rank_L=50 binary factors + 0.3-magnitude Gaussian
  noise). M_stored=200; rank-50 bottleneck creates correlation that breaks
  anti-Hebbian.
- **Values**: random bipolar {±1}^N in both arms.
- **W storage**: W = (values.T @ keys) / N (Hebbian outer-product, same as
  wave14q).
- **Erase**: W' = W − α (W k_e)(k_e)^T / ⟨k_e, k_e⟩ (matches wave14q's
  `antihebbian_erase` exactly).
- **Multi-probe battery**: matches wave14q's `probe()` function structure
  with three additions:
  - kept_preservation: argmax-leak on 100 random non-erased facts before vs.
    after erase
  - paraphrase_h sweep: ∈ {2, 4, 8, 16} bits flipped
  - rank computed against the full 200-value codebook

## Parameter-matched comparison (per playbook item 1)

The two arms use IDENTICAL: N, M_stored, n_erase, α sweep, seed, erase
algorithm, multi-probe definitions, value codebook. The ONLY difference is
the key distribution. Causal attribution of any Hadamard-vs-correlated gap
to the key structure is therefore valid.

## Carnap operational definition (specifies the verdict trigger)

verdict = STRUCT_KEYS_FIX_MIRAGE iff:

at some α ∈ {1.0, 1.5, 2.0}, simultaneously across 5 seeds:

  mean(hadamard.argmax_leak) < 0.05 ∧
  mean(hadamard.mean_rank) > 100 ∧
  mean(hadamard.norm_ratio) < 0.15 ∧
  mean(hadamard.paraphrase_leak[h=8]) < 0.05 ∧
  mean(hadamard.kept_preservation) > 0.95 ∧
  [mean(correlated.mean_rank) ≤ 30 ∨
   mean(correlated.norm_ratio) > 0.30 ∨
   mean(correlated.paraphrase_leak[h=8]) > 0.10]

The last clause requires the correlated arm to fail at least one Mirage
probe at the SAME α, ensuring the contrast is real.

## Cited mechanism / sources (R1 verification checklist items)

1. **Hopfield-Feinstein-Palmer 1983**: anti-Hebbian rank-1 erase as
   unlearning operator; foundational.
2. **Hammons-Kumar-Calderbank-Sloane-Solé 1994** (Kerdock construction):
   foundational reference for the Welch-bound family R1 recommends; v1
   uses the Hadamard subcode of this family, the orthogonal limit.
3. **Sylvester 1857**: Sylvester construction of Hadamard matrices at
   N = 2^k; recursive [[H,H],[H,-H]] form used in v1.
4. **Mirage of Model Editing (arXiv:2503.06991)**: the multi-probe
   battery this verdict is calibrated against.
5. **wave14p_erase_multiprobe.md** (own work): the prior Mirage failure
   the correlated arm reproduces.
6. **wave14q_rome_vs_antihebbian.py**: the `make_correlated_keys` and
   `probe` functions; this experiment reuses the exact correlated-key
   construction for direct comparability.

## Materials analog (load-bearing per memory)

Hadamard-subcode storage maps to a **crystalline lattice in {±1}^N**: every
codeword is a lattice point with no defects. Anti-Hebbian erase = remove
one lattice atom. The diffraction pattern (Walsh-Hadamard spectrum of W)
loses exactly one Bragg peak; the lattice elsewhere is undisturbed.
Random-correlated-key storage is an **amorphous solid with quasi-random
disorder**: removing one "atom" perturbs the diffraction pattern globally
in a hard-to-localize way — the same global perturbation that the
multi-probe rank/norm/paraphrase detect as residual presence. This is the
same lens that motivated `wave14xrd_structured_keys` (which already showed
SNR ratio 1.5×10⁷ vs 1.3 for structured vs random keys in WHT space).

## Expected runtime

- Smoke (N=512, M=40, n_erase=5, 1 seed, 1 α, 2 arms): ~5–8 s on CPU
- Full (N=4096, M=200, n_erase=30, 5 seeds, 3 α, 2 arms): estimated 3–8 min
  on the workstation GPU. Most time spent in matmul during multi-probe;
  Hadamard codebook construction is one-time at N²=16M entries.

## What product decision this enables

- `STRUCT_KEYS_FIX_MIRAGE` → Bet 2 moves from ❌ to 🟢 at v1 (orthogonal-
  keys subcase). v2 with full Kerdock + snap is needed before the row
  upgrades to ✅. GDPR-erase product narrative becomes: "with structured
  keys (Hadamard at low density), anti-Hebbian rank-1 passes Mirage."
- `STRUCT_KEYS_PARAPHRASE_FAIL` → diagnose what bridges remain at h=8
  even with zero-IP codewords; potentially indicates the alpha is wrong
  or the snap dimension matters even at low density.
- `STRUCT_KEYS_ARGMAX_ONLY` → the structured-keys family is closed for
  GDPR-erase. Route to paraphrase-aware ROME (R1 Candidate 3').
- `STRUCT_KEYS_BASELINE_NOT_BROKEN` → test-setup issue (not a substrate
  finding); audit the correlated-arm construction against wave14q.

## Rehabilitation list (if v1 fails — per memory feedback)

If Hadamard arm fails any criterion, BEFORE closing the family in cap_map:

1. Sweep α more finely around the failure point ({1.2, 1.3, 1.7} added).
2. Run with M_stored ∈ {50, 100, 400} to test density-dependence.
3. Try a different orthogonal codebook (random orthogonal matrix, not
   Hadamard) to rule out Sylvester-specific artifacts.
4. Add explicit snap-to-codebook (the Variant 2A.i recipe) and re-test —
   maybe snap matters more than R1 predicted at this density.
5. Implement full Kerdock K(12) anyway and test the dense regime that
   v1 cannot probe (M_stored > N).

Strategy session decides between these or closes the family after this
rehabilitation list is exhausted.
