# 2x research drill -- BTSP binary-synapse signal-collapse revival

**Filed-by:** Research (Director, Opus 4.7-1M)
**Date:** 2026-06-27
**Trigger:** `btsp_binary_synapse_one_shot_v2_regime_probed` smoke HARD_FAIL at probe-found fair regime (N_DIM=1024 N_CAT=50 N_TRAIN=5 proto_noise=0.6 alpha=0.0488). BTSP_new=0.020, BTSP_old=0.006, BinHeb=0.306, ContHeb=0.381, tag_fraction=0.505, cv=0.096 (n=3 seeds).
**Discipline:** USER "2x all verified negatives." Probe DID find a fair regime; mechanism collapsed there. Genuine substrate-negative; not a methodology confound.
**Calibration penalty:** P estimates deflated 0.15-0.25; novel-synthesis P capped 0.50.

---

## ROOT-CAUSE DIAGNOSIS (load-bearing finding before either angle)

**Wu-Maass 2025 Nature Comms specifies fp = 0.005 (0.5% input sparsity) and fq = 0.0025 (0.25% gating sparsity).** Our v2 cell ran at **tag_fraction = 0.505 (50.5%).** That's **two orders of magnitude** higher than the regime the paper proves the mechanism works in. The drill TOP-1 mapping wasn't wrong; the implementation simply never instantiated the sparsity regime the proof depends on.

Wu-Maass's mathematical argument for binary one-shot is *contingent on sparse codes*: bimodal weight distribution + sparse input + sparse gating = robust threshold under perturbation. At 50% tag fraction, the bimodal collapses (~half synapses ON, half OFF, indistinguishable from random binary noise after a single write). BTSP_new=0.020 is exactly what you'd expect when half your weights flipped per-pattern overwriting prior structure -- catastrophic interference at write time, not retrieval time.

This reframes the question entirely. The negative is NOT "binary-W consolidation can't do prototype-classification." The negative is "Wu-Maass at substrate-default sparsity gives uniform-random binary W." Sparsity is the actual hyperparameter; tag_fraction is the downstream observable.

The v2 prereg's PROBE_GRID swept (N_DIM, N_CAT, N_TRAIN, proto_noise). It did NOT sweep fp (input sparsity) or fq (gating sparsity). The probe found a "fair baseline regime" by ContHeb saturation, but ContHeb saturation is orthogonal to whether BTSP's sparsity regime is satisfied. **The probe fairness criterion was wrong for the mechanism under test.**

---

## ANGLE A -- TIGHTEN THE BTSP MECHANISM (sparsity regime + eligibility trace)

The mechanism is salvageable IF the literature's load-bearing assumption (sparse binary codes) is actually instantiated in the substrate's input pathway. Three concrete proposals:

**A1. Sparsify input via K-WTA pre-encoder + sweep tag_fraction directly.** Insert K-WTA gate before BTSP write: keep top-k of N_DIM coordinates, zero rest. Sweep k/N in {0.005, 0.01, 0.025, 0.05, 0.10}. Independently sweep tag_fraction parameter (the gating probability fq) in {0.0025, 0.01, 0.05, 0.10, 0.25}. This is a 25-config 2D sweep over the literature's actual load-bearing axes. Expected: at fp~0.005, fq~0.0025 we should see BTSP_new climb from 0.020 toward ContHeb (0.381) or above. If sparse-regime BTSP exceeds dense-regime ContHeb, the mechanism is vindicated; if not, Angle B applies.

**A2. Eligibility-trace decay sweep (tau_e) at fixed sparse regime.** Once A1 finds the sparse regime, sweep tau_e in {0.05, 0.2, 1.0, 5.0} timesteps. Wu-Maass uses BTSP-like seconds-scale traces; cell may have used too-slow decay leaving stale eligibility at consolidation, OR too-fast leaving no trace. The biological grounding (Bittner-Milstein 2017 + Wu-Maass 2025) puts the trace around 5-10 seconds → 5-10 pattern-presentations at substrate's timestep. cv=0.096 at v2 means current implementation is reproducible-bad, not noisy-bad → tau_e mis-tuning, not stochastic failure.

**A3. Verify binarization mapping (continuous activation → binary spike).** The cell maps continuous prototype responses to binary spikes via some threshold. If the threshold is at the wrong percentile (e.g., median = 50% spike rate by construction), tag_fraction~0.5 falls out as an artifact of the binarization, NOT BTSP behavior. Need to audit: does the cell match Wu-Maass's threshold derivation (top-fp fraction fire)? If not, fix the threshold to enforce fp=0.005 spike-rate; tag_fraction should drop to ~0.005 automatically.

**Revival cell from Angle A: `btsp_binary_synapse_v3_sparse_regime_swept`** -- 2D sweep over (fp, fq) at fixed N_DIM=1024 N_CAT=50 N_TRAIN=5. ARMS: BTSP_FULL at each (fp, fq) cell of the 5x5 grid; ContHeb baseline at substrate's natural fp; BinHeb at substrate's natural fp; diagnostic tag_fraction reporter per (fp, fq). HARD_PASS: at some (fp_*, fq_*) with fp_* ≤ 0.05 and fq_* ≤ 0.10, BTSP_new ≥ 0.40 AND BTSP_new > BinHeb at same sparsity by ≥ 0.10 AND old_pattern_acc ≥ 0.30. Cardinality 5x5x3seeds = 75 units. Falsifiable: if NO grid cell satisfies → BTSP-binary structurally infeasible at substrate's task class, atomize as HONEST_NEG, defer to STC/engram-dropout. Smoke discriminator: at smoke regime (fp=0.005, fq=0.0025, n=2 seeds, single config), BTSP_new must already exceed BinHeb by ≥ 0.05 -- if not, HARD_FAIL smoke and re-think before full.

---

## ANGLE B -- IS BTSP THE RIGHT MECHANISM FOR PROTOTYPE-CLASSIFICATION?

Independent of whether A1 succeeds, the literature framing is mismatched. Wu-Maass demonstrates BTSP for **content-addressable memory** (input → retrieve stored pattern). Bittner-Milstein 2017 demonstrates BTSP for **place-cell formation from a single trial** (sequence-context → spatial tuning). Both are **one-shot episodic binding**, not **prototype consolidation over many noisy instances**.

Our substrate's prototype-classification task class (N_CAT prototypes, N_TRAIN noisy instances per cat, retrieve cat identity) is structurally closer to:
- **STC (synaptic tagging-and-capture):** tag weakly-stimulated synapses; capture by PRP triggered by strong stimulus. Continuous W with tag-mask. Naturally aggregates over multiple presentations.
- **Engram-dropout:** inhibitory plasticity gates which neurons are eligible; continuous W; per-pattern allocation but no binarization.
- **3-tier W (Battery 2):** fast-medium-slow timescale weights; explicit consolidation pipeline.

These three preregs already exist (`stc_tag_and_capture_v1`, `engram_dropout_inhibitory_plasticity_v1`, `hierarchical_3_tier_W_v1`). Lit-scan calibration: continuous-W consolidation mechanisms have ~10x the published evidence base for prototype-classification specifically; BTSP's strong evidence is for episodic/sequence one-shot. P(BTSP-binary wins on prototype task) deflated to ~0.25; P(STC wins on prototype task) ~0.55 (cap 0.50 if novel-synthesis applies).

**Honest assessment of Angle B's bottom line:** Even if Angle A's sparse-regime sweep recovers BTSP to ContHeb parity, **STC is the better-matched mechanism for the substrate's actual workload**. BTSP-binary's value-add over ContHeb is robustness to perturbation under tight capacity, not prototype-quality. The substrate isn't capacity-bound at N_DIM=1024 N_CAT=50; it's signal-bound. STC and engram-dropout address the signal-preservation problem directly; BTSP-binary addresses a problem the substrate doesn't have yet.

---

## TOP-2 REVIVAL CELLS

**TOP-1 (priority, GPU-eligible, falsifies Angle B):** `stc_tag_and_capture_v1` -- run as priority Battery 2 cell. Discriminator: at fair regime where ContHeb=0.381, STC should achieve ≥ 0.50 (gain ≥ 0.12 over continuous Hebbian by selective consolidation), AND tag-fraction selectivity ≤ 0.15 (5-15% of synapses tagged per pattern, not 50%), AND old_pattern_acc ≥ 0.40 (better retention than BTSP_old=0.006). GPU-eligible only if N_DIM ≥ 8192 + multi-seed batched (Fix #24 mandate; otherwise remote_cpu). Smoke must FIRE the discriminator at smoke-N (Discipline #2). If STC HARD_PASSes, BTSP-binary's drill priority drops to background (no longer load-bearing for Barrier 3).

**TOP-2 (sequential to TOP-1, falsifies Angle A):** `btsp_binary_synapse_v3_sparse_regime_swept` -- 5x5 (fp, fq) sweep per Angle A1+A3. CPU-eligible (numpy outer products at N_DIM=1024). Discriminator: HARD_PASS only if some grid cell satisfies BTSP_new ≥ 0.40 AND BTSP_new > BinHeb at same sparsity by ≥ 0.10. Cardinality 75 units; cv across seeds < 0.15. Smoke at (fp=0.005, fq=0.0025) single config 2 seeds must show BTSP_new > BinHeb by ≥ 0.05 or smoke HARD_FAILs. If TOP-1 STC lands chain-grade FIRST, TOP-2 becomes scientific-completeness-only (atomize regardless of verdict for substrate-mechanism-map); de-prioritize for cycles.

---

## HONEST ASSESSMENT

BTSP-binary is **probably salvageable at sparse regime** (P~0.40) and **probably the wrong fit for prototype-classification anyway** (P~0.65). These two assessments are independent and both true. Recommendation: ship STC TOP-1 first (faster, better-matched, more probable HARD_PASS), then ship BTSP-v3 sparse-regime TOP-2 for substrate-mechanism-map completeness. If STC HARD_PASSes Barrier 3, BTSP-binary's revival becomes pure-science not load-bearing. If STC also collapses, BTSP-v3's sparse-regime answer becomes load-bearing for whether ANY binary-W consolidation can work in this substrate.

**Fairness discipline applied:** both revival cells use probe-found-fair-regime first (STC: same probe as v2; BTSP-v3: explicit fp/fq sweep IS the regime probe). Tag fraction is SWEPT not assumed (TOP-2 Angle A3 audit). No silent except: blocks. CARDINALITY_OK fields mandatory. Smoke must FIRE discriminator before full dispatch.

---

Sources:
- [Wu & Maass 2025, Nature Comms -- binary synapses, one-shot, sparsity fp=0.005 fq=0.0025](https://www.nature.com/articles/s41467-025-56459-9)
- [Wu et al. 2025 bioRxiv v2 -- BTSP for HDC binding](https://www.biorxiv.org/content/10.1101/2025.05.15.654220v2.full)
- [Bittner & Milstein 2017, Science -- BTSP CA1 place fields](https://www.science.org/doi/10.1126/science.aan3846)
- [Synaptic tagging and capture, recurrent network consolidation (Comms Bio 2021)](https://www.nature.com/articles/s42003-021-01778-y)
- [DDSC CaMKII underlies BTSP, seconds-timescale trace](https://pmc.ncbi.nlm.nih.gov/articles/PMC11540904/)
- [Synaptic memory consolidation theories for continual learning (2024)](https://arxiv.org/pdf/2405.16922)

-- Research (Director, Opus 4.7-1M)
