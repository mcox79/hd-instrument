# research 2x drill: substrate negative N6 -- Resonator dense V=100 capacity HARD_FAIL
# date: 2026-06-20
# topic: re-examine the V=100 dense resonator HF in light of cleanup-augmented HP (6x) and sparse-block-local K=26 HP
# trigger: USER directive 2026-06-20 "research all negatives 2x"
# verdict: REFRAME SURFACED -- negative is mis-labeled at the capability layer

---

## HEADLINE

The Resonator dense V=100 capacity HARD_FAIL is **algebraically predicted** by the Frady-Sommer
2020 / Kent-Frady-Sommer 2020 M_max ~ c*N^2 scaling law (c ~ 0.95). At N=4096, V=100, K>=5 the
total search space V^K = 10^10 .. 10^22 EXCEEDS the M_max ~ 1.6e7 budget by 2-15 orders of
magnitude -- acc=0.000 is the *expected* outcome of running far past the capacity envelope, not
anomalous loss of capability. The substrate ALREADY ran the rescue path (R2 sparse-block-local
resonator K=26 HARD_PASS at N=5000, all seeds 1.000; cap_map v412) and the contrast experiment
(NEW EXP 3 cleanup-augmented resonator depth HARD_PASS at 6x boost; cap_map v410). The negative
should be relabeled at the capability layer as: "**dense-uncleaned narrow-V resonator at V^K >>
M_max is HF -- which is what Frady-Sommer predicts -- but the resonator family has TWO
independent HARD_PASS variants (block-local sparse + cleanup-augmented) so the resonator
capability row is NOT closed**." The negative-survives-as-stated framing on the scorecard is
operationally misleading; the row is already a V-CONSTRAINT-BYPASSED annotation in cap_map v412
but the scorecard table at line 197 was never updated.

P_deflated (resonator capability has un-explored viable configs beyond V=100 dense): 0.65
P_deflated (V=100 dense HF is permanent boundary for this exact config -- ALGEBRAIC closure): 0.90

---

## CHEAP DECISIVE TEST (already RUN; no new experiment needed)

The decisive contrast already exists in the substrate:

| Anchor | Config | Verdict | Source |
|---|---|---|---|
| substrate_resonator_dense_capacity_ksweep_v1_n4096 | V=100 K=5..11 N=4096 | HF acc=0.000 | cap_map v401 cycle 71 (2026-06-04) |
| substrate_resonator_noise_injection_ksweep_v1_n4096_gpu | V=512 K=5..50 N=4096 + noise anneal | HF acc=0.000 | cap_map v401 cycle 71 (2026-06-04) |
| substrate_sparse_resonator_blocklocal_K26_v1_n5000 | sparse, K=4/8/16/26 N=5000 | **HP acc=1.000 all seeds** | cap_map v412 cycle 83 (2026-06-05) |
| substrate_resonator_augmented_iterated_retrieval_v1_n4096 | cleanup-augmented depth | **HP 6x depth boost** | cap_map v410 (2026-06-05 01:45) |
| substrate_R6_b2_x_sparse_resonator_v1_n5000 | B2-storage x sparse-resonator | HF (composition interferes; resonator-alone OK) | cap_map v413 |

**No new dispatch required.** The follow-up actually needed is a SCORECARD EDIT to reflect the
v412 cap_map annotation: "Resonator V-constraint = parameterization failure, NOT capability
closure; block-local sparse + cleanup-augmented are operational HP variants."

---

## FRADY-SOMMER RE-DERIVATION: is V=100 K>=5 N=4096 ANOMALOUSLY worse than predicted?

Frady-Kent-Sommer 2020 (Neural Computation Part 2) established empirically across F=3..7 factors:

    M_max ~ c * N^2 where c ~ 0.95 (calibrated from N=1024 baseline ~10^6 .. 10^7 search space)

At N=4096 (the test config): M_max ~ 0.95 * 4096^2 ~ 1.6e7.

The experimental sweep was V=100, K in {5,6,7,8,9,10,11}. Total search space V^K:

    K=5  -> V^K = 100^5  = 1.0e10   ->  V^K / M_max = 625x over budget
    K=7  -> V^K = 100^7  = 1.0e14   ->  V^K / M_max = 6.25 million-fold over budget
    K=11 -> V^K = 100^11 = 1.0e22   ->  V^K / M_max = 6.25e14 over budget

**Every K in the sweep is 2-15 orders of magnitude past the M_max ceiling.** acc=0.000 is the
algebraically expected outcome -- the resonator network's iterative cleanup has no chance of
finding a unique product in a search space billions of times larger than its capacity. This
is the K_max = log(M_max) / log(V) formula working as documented. The "negative" is the algebra
working correctly; there is no anomaly to explain.

The V=512 noise-injection arm (V=512 K=5..50) is even further past the budget. Same algebraic
verdict: acc=0.000 is what the formula says you get.

**The 2x drill question "is V=100 dense HF anomalously worse than predicted?" has answer NO.
It is exactly what Frady-Sommer predicts.**

---

## WHERE RESONATOR IS VIABLE PER ALGEBRA (the K_max envelope at N=4096)

Solving K_max = log(M_max) / log(V) at N=4096 (M_max ~ 1.6e7):

    V=2   (binary)     -> K_max = 23   <- very deep, binary alphabet only
    V=10               -> K_max = 7.2
    V=26  (letters)    -> K_max = 5.1
    V=40               -> K_max = 4.5
    V=70  (char-LM)    -> K_max = 3.9
    V=100 (the test)   -> K_max = 3.6  <- experimental sweep started at K=5; OUT OF ENVELOPE
    V=500              -> K_max = 2.7
    V=1000             -> K_max = 2.4

**Operational reading:** dense resonator at N=4096 with V=100 has K_max ~ 3, so the K=5..11
sweep was guaranteed to be acc=0. A V=100 K=2 OR V=10 K=5 sweep would have hit the envelope.

This is also why the BLOCK-LOCAL sparse variant works at K=26: the per-block search space is
small (per-block V is tiny because each block is a sparse one-hot fragment of the dense
codebook), so V_eff^K_per_block stays under M_max for each block.

---

## FALSIFIABLE PREDICTIONS

### HARD-PASS (the reframe is correct)

HP1: At N=4096, V=10, K=5..7 dense resonator: acc >= 0.90 at K=5 (within K_max=7.2 envelope).
HP2: At N=4096, V=100, K=2 dense resonator: acc >= 0.95 (well within K_max=3.6).
HP3: Sparse-block-local resonator (v412 HP) reproduces at N=4096 (smaller than v412's N=5000):
     acc >= 0.95 at K=16, acc >= 0.85 at K=26.
HP4: Cleanup-augmented resonator depth boost (v410 HP, 6x) reproduces at V=100 dense codebook
     when chain length is REDUCED to within K_max=3 per recovery step.

### HARD-FAIL (the negative IS a permanent boundary for the V=100 dense config)

HF1: V=10 K=5 dense at N=4096 acc < 0.50 (would refute the Frady-Sommer K_max formula -- the
     experimental V=100 K>=5 HF would then be ANOMALOUS, not predicted).
HF2: Sparse-block-local K=26 fails to reproduce at N=4096 acc < 0.80 (would refute v412 cap_map
     annotation; reopen as TRUE capability closure).
HF3: Any V=100 dense K>=4 N=4096 surprisingly yielding acc >= 0.50 (would refute the algebraic
     interpretation of the V=100 K=5..11 HF; suggest something OTHER than capacity-overrun
     drove the failure; pivot to mechanism investigation).

### Cert pre-reg outline (for the scorecard-row reframe)

Pre-reg: relabel scorecard row 197 from "Resonator dense V=100 capacity HF / Capacity zero at
this V" to "Resonator dense V=100 K>=5 capacity HF (ALGEBRAIC: V^K >> M_max=cN^2; Frady-Sommer
2020 predicted); resonator FAMILY has 2 HP variants (block-local sparse K=26 v412; cleanup-
augmented depth 6x v410); capability row is OPERATIONAL with V-constraint annotation."

Threshold for accepting the reframe: zero additional experiment needed -- the cap_map v412 +
v410 annotations + the algebra in section 1 above are sufficient. The scorecard table at line
197 should be edited inline by Strategy/scribe to reflect the v412 cap_map sub-property
annotation that already exists. Cost: 0 compute. ETA: one cap_map-scribe touch.

---

## CROSS-THREAD SYNTHESIS

This 2x drill is the **third independent verification** that the resonator capability row is
mislabeled at the scorecard layer:

1. **research_drill_resonator_capacity_at_substrate_scale_2x_2026-06-04.md** (2x drill, 2026-06-04):
   produced the K_max table at N=4096 for dense/sparse/noise-injected/hierarchical/position-bound;
   ranked sparse and position-bound as the highest-K variants; predicted K=26 letters at N=5000
   would replicate; that EXACT prediction was confirmed by R2 (v412 HP).

2. **research_drill_substrate_negative_results_structural_analysis_2x_2026-06-04.md** (line 457):
   classified the V=100 dense HF as TYPE 1 (algebraic/structural per Frady-Sommer formula);
   identified arXiv:2404.19126 sparse resonator K=26 as the direct engineering rescue. That
   rescue was DISPATCHED as R2 and CONFIRMED HP.

3. **This drill** (2026-06-20): re-derives the algebra and confirms the negative is exactly
   what Frady-Sommer predicts; surfaces the cap_map v412 + v410 annotations that already exist
   but the scorecard table was never edited to reflect.

The negative has been resolved at the cap_map layer for 16 days (since 2026-06-05). The
scorecard editing is the only remaining action.

Related: research_drill_codebook_capacity_structural_3x_2026-06-10 (modern-Hopfield exponential
capacity; softmax cleanup as next-tier resonator upgrade) provides an additional upgrade path
beyond block-local sparse -- modern-Hopfield-cleanup resonator could push K_max even higher
without sparse-coding overhead. P_deflated (modern-Hopfield resonator HP at N=4096 V=100 K=7):
0.40.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **Stop counting "Resonator dense V=100 capacity HF" as a capability closure in the negative
   inventory.** It is parameterization-overrun, not capability loss. The capability row is
   ALREADY operational with two HP variants. Counting it as a negative misrepresents the
   substrate's NC1/Mode-4 envelope when reasoning about product positioning.

2. **The PRODUCTION-RELEVANT resonator config is block-local sparse OR cleanup-augmented**, not
   plain dense. Both are HP. Both are already empirically anchored. The substrate has a
   working resonator capability at K=26 (alphabet-scale recovery) and 6x depth boost via
   cleanup augmentation -- this is the resonator product story.

3. **The V=100 dense HF is a CALIBRATION ANCHOR**, not a capability claim. It demonstrates
   that the substrate's algebraic prediction tools work: Frady-Sommer formula correctly
   predicted acc=0.000 at V=100 K=5..11 N=4096. Tools that correctly predict negatives are
   substrate-product features (honest envelope characterization).

4. **For substrate-as-cognitive-core / NC1 reasoning**: the resonator-augmented depth 6x boost
   (cap_map v410) is the load-bearing production knob; combined with hierarchical-D scaling
   (NEW EXP 5 HP) this gives 24+ reliable hops at 3x alpha_c overload -- far past LLM CoT's
   K~4 collapse.

5. **One concrete scorecard edit needed** (file Strategy hand-off; no compute):
   `notes/capability_scorecard.md` line 197 should be rewritten to match the cap_map v412
   annotation. The current line ("Capacity zero at this V / Sparse + noise-injection variants
   pending") is 16 days stale -- both rescues have been tested; one HP, one HF.

---

## CITATIONS (verified count: 8 substrate-internal + 4 external)

External:
1. Frady E.P., Kent S.J., Sommer F.T., Kanerva P. (2020). Resonator Networks 1. Neural
   Computation 32(12). arXiv:2007.03748.
2. Kent S.J., Frady E.P., Sommer F.T. (2020). Resonator Networks 2: Factorization Performance
   and Capacity. Neural Computation 32(12):2332. doi:10.1162/neco_a_01330. (M_max ~ N^2; the
   load-bearing algebraic anchor for this drill.)
3. Renner A. et al. (2024). Neuromorphic Visual Scene Understanding with Resonator Networks.
   Nature Machine Intelligence. arXiv:2208.12880v4. (Hierarchical resonator K=6 at N=16384.)
4. Cunningham et al. (2024). Compositional Factorization of Visual Scenes with Convolutional
   Sparse Coding and Resonator Networks. arXiv:2404.19126. (Sparse resonator K=26 at N=5000 --
   this is the algorithm replicated as substrate R2 in cap_map v412.)

Substrate-internal:
1. notes/research_drill_resonator_capacity_at_substrate_scale_2x_2026-06-04.md (prior 2x drill;
   K_max algebraic table at N=4096; ALREADY predicted V=100 K>=5 would fail and sparse K=26
   would pass).
2. notes/research_drill_substrate_negative_results_structural_analysis_2x_2026-06-04.md
   (negative-results taxonomy; V=100 dense HF classified as TYPE 1 algebraic; sparse K=26
   identified as rescue).
3. notes/strategy_decisions_2026-06-04.md lines 1248-1262 (verdicts B and D: V=512 noise-
   injection and V=100 dense both acc=0.000; baseline floor at V=100; V-constraint active).
4. notes/substrate_capability_map.md v412 (2026-06-05) (R2 sparse-block-local K=26 HP;
   V-CONSTRAINT-BYPASSED annotation).
5. notes/substrate_capability_map.md v410 (2026-06-05) (NEW EXP 3 cleanup-augmented depth
   HARD_PASS at 6x boost).
6. notes/substrate_capability_map.md v413 (2026-06-05) (R6 B2 x sparse-resonator HF;
   COMPOSITION interferes, resonator-alone unaffected).
7. notes/capability_scorecard.md line 197 (the stale scorecard row that this drill recommends
   editing).
8. experiments/exp_substrate_resonator_dense_capacity_ksweep_v1_n4096.py (the actual script;
   V=100, K_GRID=[5,6,7,8,9,10,11], confirms the over-budget sweep).

---

## P_deflated SUMMARY

Claim: "the V=100 dense HF is an ALGEBRAIC capacity-overrun, not a resonator capability closure;
the resonator capability row has two HP variants already empirically anchored":

    P_algebraic (Frady-Sommer formula matches observed acc=0.000): 0.90
    P_capability (resonator family is operational via block-local + cleanup-aug): 0.85
    P_scorecard_reframe_needed (scorecard row 197 is stale relative to cap_map v412): 0.95

Calibration: no calibration penalty applied to P_algebraic because the formula M_max ~ cN^2 is
empirically validated in Frady-Sommer 2020 across the SAME N range (1024-16384) and the substrate
N=4096 sits inside that envelope. The 0.90 reflects residual uncertainty about the c constant
between substrate's bipolar codebook vs Frady-Sommer's complex unit-vector codebook. Standard
0.15 deflation applied to P_capability for "rescue replicated at N=4096" (only N=5000 has been
shown HP; assumed to extrapolate).

NEXT-DRILL CANDIDATE FIELD: modern-Hopfield (Tier-1 fruit-bearing). Drill: does softmax-cleanup
modern-Hopfield resonator extend K_max beyond block-local sparse at N=4096? The codebook-capacity-
3x drill (2026-06-10) identified this as a 2-3 day fix giving 10-50x capacity per shard.

---

END.
