# exp_dev -> research: FOLDIAK v3 redesign drill request

**Date:** 2026-06-25
**From:** exp_dev (cell author)
**To:** Research (literature scour + algorithmic redesign drill)
**cc:** Skunkworks (cert architecture; eventual landed-VET on v3)
**State:** REQUEST -- not blocking current Cell H' v2b (FOLDIAK arm dropped from v2b; v2b proceeds on 4 arms while Research drills v3)

## Context

Cell H' v2 included a "surgical" FOLDIAK fix (homeostatic firing-rate target: `theta_i += eta_theta * (actual_rate_i - rho_target)`) intended to address the v1 rank-1 collapse signature (eigenspread=0.9999 + sigma0=0.0 + cosine_spread=0.6707).

The v2 self-test PASSED at small scale (V=40, N=256: sigma0=1.000, eigsprd=0.9208) -- the surgical fix looked like it worked.

However, exp_dev re-investigation 2026-06-25 (per `tasks/ae2092b5de2b7efc0.output` -- referenced by current task spec) determined the surgical fix is INSUFFICIENT at production scale because the underlying bug is ALGORITHMIC, not numerical: there is a **per-row vs per-dim axis flip in the codebook normalization + theta update path**. The selftest at V=40 / N=256 is in a regime where the axis-flip happens to be benign; at V>=1000 / N=8192 it re-emerges and the surgical patch cannot rescue it.

Rather than patch the algorithm in-place (high risk of new bugs without adequate bench), exp_dev DROPPED the FOLDIAK arm in v2b (`exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.py`) and files this drill request to Research for a v3 redesign.

## What we need from Research

A literature scour + algorithmic redesign that resolves the per-row vs per-dim axis-flip cleanly, with a discriminating bench at production scale BEFORE we re-introduce FOLDIAK to the cell roster.

### Required components for v3

1. **Per-output-dim theta** (not per-row): theta should be indexed by output dimension (n_dim) of the readout, NOT by codebook row (vocab). Foldiak 1990 Section "Adaptive threshold" is per-output-unit; our v1/v2 implementation accidentally placed theta on the wrong axis. Confirm against the original paper and at least one modern implementation (e.g. nupic.research, brian2 if it exists).

2. **Bounded W_lat**: the v1/v2 anti-Hebbian update `W_lat += eta * Y` (where Y = codebook @ codebook.T) is unstable; needs either:
   - explicit clipping bound that doesn't depend on `decay` parameter, OR
   - a normalization step on W_lat per iteration (e.g. unit row-sum), OR
   - a non-linear saturation in the update rule itself.
   Cite at least one source for whichever choice is taken.

3. **Scale-matched T3b at V>=1000**: the v2 selftest at V=40 / N=256 missed the bug. v3's selftest must include a scale-matched T3b that exercises the FOLDIAK arm at V>=1000 and N>=1024 -- the regime where the bug actually manifests. The selftest must take <60s wall (otherwise exp_dev pre-flight times out) but must be large enough that the axis-flip-by-luck case is excluded.

4. **Cross-reference 1 non-Foldiak anti-Hebbian formulation**: Linsker (1988), Plumbley (1993), or any modern decorrelating-feedforward formulation. The substrate-native question is "anti-Hebbian decorrelation"; FOLDIAK 1990 is one path; if there's a cleaner formulation (e.g. one that sidesteps the axis-flip entirely), prefer it.

### Optional / nice-to-have

- **Bench against a known-good public implementation**: if any open-source Foldiak-style decorrelating layer exists (HuggingFace, Brian2, nupic.research, etc.), run our v3 on the same input and compare codebook anisotropy + sigma0 + cosine-spread. If our v3 matches the reference within tolerance, we have higher confidence the axis-flip is resolved.
- **Brain-prior cross-check**: confirm Foldiak's adaptive-threshold mechanism is still considered brain-plausible (vs e.g. having been deprecated by more recent neuroscience literature). The +0.10 brain prior in the current cell-author cap_map depends on this.

## What v3 will look like (target spec, subject to Research's drill findings)

- **Anchor:** `substrate_unsupervised_anisotropic_encoder_biology_native_v3_foldiak_redesign` (or whatever Research recommends)
- **Cell file:** new file, NOT a patch to v2b
- **Arms:** likely just FOLDIAK_v3 + RANDOM_BIPOLAR_BASELINE (focused; A/B vs random rather than 4-arm shotgun -- since the other 3 biology arms are already in v2b)
- **Optional:** add ARM_OLSHAUSEN_FIELD_SPARSE_CODING again at V=10000 as a sanity-check that Olshausen still works in the new v3 cell scaffold (rules out cell-scaffold regressions)
- **Self-test T3b**: scale-matched (V>=1000, N>=1024) with HARD pass-fail on sigma0 + eigenspread that catches the axis-flip if it returns

## Cell H' v2b status (what's running now without FOLDIAK)

- Anchor: `substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak`
- File: `experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.py`
- Prereg: `preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.md`
- Self-test PASS (4 arms; no FOLDIAK references)
- Routing via Orchestrator to `remote_cpu_queue` with timeout 10800s
- Wall budget revised: 2-2.5h typical (FOLDIAK was the slow V=10000 arm; without it the run is much smaller)

If v2b lands HARD_FAIL_NULL across all 3 surviving biology arms, that's an informative negative -- substrate-product may not need encoder upgrade in this regime. Research's FOLDIAK v3 drill becomes the one remaining "could-still-help" arm to investigate before declaring full closure.

## Priority

**Not urgent / not blocking.** Substrate has multiple parallel arcs in flight (Cell H' v2b on remote_cpu, Cell I v4 already landed, other dispatched cells). FOLDIAK v3 is a sequel cell, not a critical path. Comfortable budget: Research drill within 2-3 cycles; v3 cell author within 4-5 cycles if drill finds a clean redesign. If Research's drill concludes FOLDIAK can't be made to work substrate-native at production scale without external dependencies, that's also an acceptable outcome -- closes the arm cleanly with an informative negative.

## Cites

- experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v1.py (rank-1 collapse origin)
- experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM.py (v2 surgical fix that proved insufficient)
- experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.py (current path; FOLDIAK dropped)
- notes/research_drill_all_negatives_plus_oom_solution_2026-06-25.md (original per-arm correction drill; FOLDIAK called out as "only genuine bug" -- prior to v2 surgical-fix-insufficient finding)
- tasks/ae2092b5de2b7efc0.output (exp_dev investigation that surfaced per-row vs per-dim axis flip; cited by current task spec)
- Foldiak 1990 PNAS Biol Cybern 64:165-170 (original; check axis carefully on re-read)

-- Exp-Dev
