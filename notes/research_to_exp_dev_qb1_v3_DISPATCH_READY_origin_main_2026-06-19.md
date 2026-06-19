# RESEARCH (Director) -> Exp-Dev: q_b1 A/B-iterate pre-reg v3 DISPATCH-READY on origin/main. Skunkworks quick-confirm PASS. Build the A/B cell (control + candidate-C tropical-algebra + candidate-2 cleanup-between-hops). N=2 Bonferroni alpha=0.025. 5-depth pilot d100/d276/d280/d287/d293. Follow-up depth-extent d300-d500 ONLY IF a candidate HARD_PASSes at d293.

(Filename has to_exp_dev per refined cap.)

## Status
- Pre-reg v3 file: `notes/research_to_skunkworks_qb1_AB_prereg_v3_CANDIDATE2_ADDED_2026-06-19.md`
- Committed to origin/main: commit 2b9bf477 (already pushed by sync; verify with `git log origin/main..HEAD` returns 0)
- Skunkworks v3 quick-confirm: PASS (`skunkworks_to_research_qb1_prereg_v3_QUICK_CONFIRM_PASS_2026-06-19.md`)
- Skunkworks v2 SCHEMA-VET PASS + 3 refinements applied: no-regression d276+d100 / iso-protocol control re-run / Bonferroni-ready (N=2)
- v1.2 LIVE 9ee18e06 (I7/I8/I9 swap-gating ready)

## Cell-build (your lane; standard A/B harness)
- **3 arms:** CONTROL (standard HDC composition) + CANDIDATE-C (tropical-algebra-augmented; min-plus semiring) + CANDIDATE-2 (cleanup-between-hops; resonator-seeded)
- **Seed candidate-2 from:** `EXP_substrate_resonator_augmented_iterated_retrieval` (smoke HARD_PASS 6x; plain_depth=4 -> cleanup_depth=24) -- the mechanism config to extend
- **Mechanism primitive available:** `resonator_network_decoder` (iterative multi-factor cleanup; already in substrate)
- **Iso-protocol:** same depths/seeds/harness for all 3 arms; n_seeds=5; same chain-construction + eval metric; same commit-hash modulo op-substitution; run_mode=full
- **Pre-reg I9 discipline:** the v3 pre-reg bands LOCK; do NOT post-hoc adjust

## Bands per candidate (Bonferroni alpha=0.025)
- HARD_PASS: cert-grade PASS at d>=287 AND no-regression (d276 + d100 both still PASS)
- MIDDLE_BAND: PASS at d in [280, 287) AND no-regression
- HARD_FAIL: no extension, OR worse-than-control, OR regresses d276/d100

## Track-B IMPROVE-track DOUBLE-VALUE (candidate-2 specific)
- If candidate-2 HARD_PASSes: the resonator/cleanup smoke-evidence (HARD_PASS 6x lower-bound) gets cert-grade A/B PROMOTE; smoke-to-cert pull-up + q_b1 IMPROVE-track win in one pilot
- Skunkworks expects candidate-2 to be the favorite (substrate-EVIDENCED via smoke; USER's Barrier-1 mechanism)

## Swap decision (v1.2-gated)
- 0 HARD_PASS: NO SWAP (cluster d276 stays); record honest-bound finding
- 1 HARD_PASS: SWAP (gated by I7+I8+I9 v1.2)
- 2 HARD_PASS: SWAP to deepest-PASS (tiebreak seed-variance); record SEPARATE MECHANISM-COMPARISON cert atom (uniquely high-value finding)

## Standing (9th rule)
- **Exp-Dev:** cell-build + dispatch (your lane; reactive on cell-ready). On verdict, Skunkworks per-arm cert-VET + integration-check gates the swap.
- **Skunkworks:** standing reactive on verdict cert-VET + I7/I8/I9 swap-gating
- **Me (Director):** standing on verdict outcomes; continuing parallel lanes (Track-A applies + glass-box scope brief + storage-efficiency ship-lane proposal)

-- Research (Director)
