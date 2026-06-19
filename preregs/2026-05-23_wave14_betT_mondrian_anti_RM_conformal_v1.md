# Prereg: wave14_betT_mondrian_anti_RM_conformal_v1

**Trigger**: Strategy x Research shore-up matrix 2026-05-23 Weakness #2 (MEDIUM). Bet T PARTIAL min_acc=0.689 at cycle 101; stale 67 cap_map versions. 2/3 rescues KILLED at FULL (TEMPSCALE per-hyp v158; Mondrian-by-hyp filed but never run). Per meta-map Drill 3 the anti-RM(1,m) coset is the substrate-novel stratifier never tested (v152 REFUTED naive RM(1,16) stratification).

**Hypothesis**:
Mondrian conformal stratified by ANTI-RM(1,m) coset (at the order-1 block, coarsened to 4 classes to match Kerdock 4-coset frame) provides per-coset coverage in [0.85, 0.95] uniformly across all 4 cosets at K_hyp=8. The anti-coset is the natural stratifier the cycle-101 PARTIAL hypothesis-class stratification missed.

**Operating point**: N=1024 (power-of-2 required for Hadamard generator basis), K_hyp=8, n_facts_per_hyp=30, num_entities=200, beta=8, n_cal_per_hyp=80, n_test_per_hyp=120, 5 seeds. Pure CPU.

**Hard PASS** (`BETT_MONDRIAN_ANTI_RM_PASS`):
- Per-coset coverage in [0.85, 0.95] for ALL 4 anti-RM cosets (5-seed mean).
- Mean prediction-set size <= K_hyp / 2 = 4.0.

**Hard FAIL** (`BETT_MONDRIAN_ANTI_RM_FAIL`):
- ANY coset coverage outside [0.80, 0.99], OR
- mean_set_size > K_hyp = 8 (degenerated).

**PARTIAL**: coverage in [0.80, 0.99] for all cosets but outside [0.85, 0.95] target OR mean_set_size in (4, 8].

**Closure implication**:
- PASS → Bet T rescued; cap_map row updated from PARTIAL min_acc=0.689 to ✅ with anti-RM Mondrian conformal coverage guarantee.
- FAIL → Bet T closes per PROT-004/006 — final Mondrian rescue tried. The 67-version-stale row is honestly closed with full audit trail (TEMPSCALE per-hyp KILLED v158; anti-RM Mondrian FAILED v189 [this experiment]).

**Cost**: ~10 min CPU on remote_cpu_queue.

**Risks / caveats**:
- The anti-coset coarsening to 4 classes is a structural choice motivated by the v167 Kerdock 4-coset frame; alternative coarsenings (e.g. 8 anti-cosets at order-2) could give different per-coset coverage. We test the FIRST natural anti-coset partition; a fail does not rule out finer stratifications, but per the v158 audit trail this is the LAST rescue we will attempt before closure.
- Smoke at N=512 K_hyp=3 returned cov=1.0 across all 4 cosets (above ceiling) — small-N artifact of tiny calibration sample; FULL config tests the discriminating regime.

**Lit cross-check**: Mondrian conformal prediction (Vovk 2003; Vovk-Shafer 2005); RC3P / class-conditional conformal (Romano-Sesia-Candes 2020). Anti-coset structure of Kerdock as Z_4-linear lift / unitary-2-design (Calderbank-Cameron-Kantor-Seidel 1997). All textbook; novelty is the substrate-portfolio stratifier choice (anti-coset NOT hyp-class).
