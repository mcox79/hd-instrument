# Master plan and state — 2026-05-18

This is the single durable snapshot of where the hd-instrument program stands
after a very productive session. It exists so context isn't lost if any
single chat window runs out. Read THIS file first in any new session.

## Session arc (one-line summary)

Started at FHRR baseline 2.4994 bpc on 38KB byte LM. Through 5 literature
audits, 11+ experiments, 6 new substrate prototypes, and 5 buried-treasure
research directions identified, we now have:
- 3 substrates characterized (FHRR/BSC/SBC) with BSC best (2.4344 at N=8192)
- Full continual learning study (3a) showing 80-91% catastrophic forgetting
- Mitigation decomposition (3a.5) showing W_frozen kills forgetting to +0.05
- 6 new substrate prototypes ready to run (Wave 8/9/10/11/12/13)
- 5 buried-treasure research directions identified (CK trees, free prob,
  Tomita-Takesaki, Steenrod, R-matrices)
- Working Hopf-VSA cleanup via resonator (76% recovery vs 0% naive)

## Standing practices (memory-resident)

These rules apply in every session, written to user-level memory:

1. **No smoke** — brutal honesty, no validation theater
2. **Step-back evaluation** — gates between phases
3. **Brain-inspired framing** — neuromodulators, Hebbian, biological mapping
4. **Plain language status updates**
5. **Verify implementations against cited literature** — audit checklist
   before each experiment AND after each major finding
6. **Rehabilitation after rejection** — 3-5 axis combinations before
   abandoning a mechanism
7. **Unbiased research framing** — ask "what does X do?" not "X for AI?"

The research playbook (notes/research_playbook.md) has 6 standing practices:
pre-registration, 5-seed BF stopping, bandit framing for the two bets, full
design-space matrix, verify-lit, biweekly distillation.

## What's done (committed results)

### Wave 1+2: Substrate characterization (9 experiments)

| Substrate | Best bpc | Speed | Notes |
|---|---|---|---|
| FHRR (combined+modReLU) | 2.4994 | 1x | original baseline |
| BSC (signed+ReLU) N=4096 | 2.4817 | 2x | best at N=4096 |
| BSC N=8192 | **2.4344** | 2x | overall best |
| SBC (M=128) | 2.9272 | 2x | sparse codes; worse on perplexity |

Architecture contribution hierarchy:
- pure Hebbian → 5.56 (catastrophic)
- + delta error → 3.43 (cost: +3.07 reduction)
- + softmax cleanup → 2.52 (cost: +0.93 reduction)
- + pool blend α=0.3 → 2.50 (cost: +0.20 reduction)
- + modReLU → 2.4994 (cost: +0.022 reduction)

### Wave 3a continual learning (12 chunks complete)

All three substrates catastrophically forget 80-91% of A when trained on B:
- FHRR: A 2.50 → 4.65 (+2.15 bpc, 86% loss)
- BSC: A 2.48 → 4.54 (+2.05 bpc, 82% loss)
- SBC: A 3.20 → 4.84 (+1.65 bpc, **91% loss** — sparse codes did NOT save us)

Post-audit reframing: this is TYPICAL forgetting (van de Ven 2024, Yildiz 2024
report 40-90% retention loss is standard). Bricken 2023 SDM-as-CL claim was
NOT tested because we lack their specific recipe (Top-K + L2-norm +
positive-W + EWC).

### Wave 3a.5 mitigations (11 chunks)

Decomposed forgetting mechanism:
- **W_frozen_P2** essentially eliminates forgetting (+0.05 to +0.14 bpc)
  but B is barely learned (B_P2 = 4.25-4.50, near random)
- **decay_off_P2** recovers ~0.5-0.8 bpc
- **dual_pool** recovers ~1.0-1.2 bpc

Mechanism rank: W overwrite > pool overwrite > W decay > others. The single
shared W matrix being overwritten is the dominant cause; multiplicative
decay is secondary.

Missing: FHRR/W_frozen_P2 silently failed; need to re-run. BSC and SBC W_frozen
chunks confirmed.

### Wave 13: Hopf-VSA (working cleanup)

Three phases of S_3 / Sweedler H_4 work:
- **13.1 (S_3 group algebra):** ran, validated non-commutative binding
- **13.2 (Sweedler H_4):** non-trivial Δ implemented; Δ-SVD cleanup FAILED at 0/100
  because Δ is algebra-homomorphism (mixes structure) not rank-preserving
- **13.3 (H_4 + resonator network):** with multi-restart, **76% pair recovery**
  vs 0% naive. The audit-recommended adaptation works.

This is the first reported working cleanup algorithm for non-commutative Hopf
algebra VSA at our scale.

## What's READY but not yet run (prototypes committed)

Need GPU time (or CPU for some). All shipped as committed Python files:

| Wave | Substrate / Idea | File | Compute | Est runtime |
|---|---|---|---|---|
| 12 | qFHRR (4-bit quantized phase) | `exp_wave12_qfhrr.py` | GPU (any) | ~10 min |
| 8 | Clifford G(2,0) geometric algebra | `exp_wave8_clifford_g20.py` | GPU | ~5-10 min |
| 9 | MPS-shape (N=12,288 not 4096) | `exp_wave9_mps_prototype.py` | GPU | ~10-20 min |
| 10A | RG-flow 2-layer Hebbian | `exp_wave10_rgflow_phaseA.py` | GPU | ~5-10 min |
| 11A | LDPC cleanup unit test | `exp_wave11_ldpc_unittest.py` | CPU | ~3-5 min |
| 4.5 | Gradient W with frozen atoms | `exp_wave45_gradient_w_frozen_atoms.py` | GPU | ~15-30 min |
| 4.6 | Gradient W + learnable atom offsets | `exp_wave46_learnable_offsets.py` | GPU | ~30-45 min |
| 3a.6 | Rehearsal+EWC+transformer baseline | **NOT YET WRITTEN** | GPU | ~30 min once written |
| 3b | Induction-head ICL | `exp_induction_head.py` | GPU | ~10 min |
| 6.5 | Schlag-Irie hybrid | **NOT YET WRITTEN** | GPU | TBD |

All have pre-regs in `preregs/`.

## What's DESIGNED but not yet prototyped (need new code)

These are the buried-treasure picks from the pure-math audit on 2026-05-18:

| Wave | Idea | Why it's exciting | Cost |
|---|---|---|---|
| **14** | **Connes-Kreimer tree Hopf algebra** | **Native tree decomposition via Δ that cuts trees into (subtree-above, subtree-below) pairs with closed-form combinatorial rules. The Hopf algebra I should have started with.** | 1-2 weeks |
| 15 | Free probability transforms (R, S) | 30-year-old spectral theory that exactly fits HDC's random-vector setting; gives theoretical guarantees on bundle capacity | 1-2 weeks |
| 16 | Tomita-Takesaki modular flow | Canonical 1-parameter automorphism from algebra+state alone; replaces learned positional encoding | 2-3 weeks |
| 17 | Steenrod-style unary operations | HDC has no unary refining operations; speculative but novel | research-grade |
| 13.4 | Drinfeld double D(S_3) | R-matrix structure on top of working H_4 resonator | 1-2 weeks |

See `notes/buried_treasure_research_directions.md` for details.

## What's STILL OPEN (research directions)

- 5-seed BSC vs FHRR verification (statistical confidence on BSC ≈ FHRR claim)
- BSC at N=16384 with optimized kernel (currently bandwidth-bound)
- Wave 2a 1MB corpus scaling (needs pre-launch audit)
- Wave 6.5 Schlag-Irie hybrid (slow projector + fast Hebbian)
- The "two-bets" bandit re-evaluation per quarterly review
- Dtype acceleration: torch.compile spike + FP16/BF16 (deferred per pin doc)

## Strategic priority (my best read)

If pursuing both perplexity-floor AND capability differentiation:

1. **Wave 14 (Connes-Kreimer)** — most novel, most concrete, most directly
   addresses the question I tried to answer with H_4 and got wrong. CPU work.

2. **Wave 4.5 (gradient W frozen atoms)** — audit predicts 0.10-0.25 bpc gain;
   cheapest backprop test; could put us at parity with tiny transformer (2.39).
   GPU.

3. **Wave 8 Clifford G(2,0)** — top-pick from substrate audit; non-commutative
   binding for free. GPU.

4. **Wave 15 (Free probability)** — theoretical foundations; tells us where
   the floor is. CPU.

5. **Wave 3a.6 rehearsal+EWC** — closes the audit's pushback on Wave 3a.
   GPU.

After those: 9 (MPS), 10A (RG-flow), 16 (Tomita-Takesaki), 13.4 (Drinfeld
double), 17 (Steenrod).

## Audit-driven design rules (from this session)

1. **Audit before launching new experiment** — every time.
2. **Audit after major finding** — also every time. Wave 3a's reframing came
   from this.
3. **Pre-register experiments** with falsification criteria.
4. **Subprocess-chunked runners** for any experiment with multiple cells
   (a single crash mustn't kill the whole run).
5. **Verify implementations against cited literature** — was modReLU
   actually Polsky-Mel-Schiller? (No; it's modReLU from Arjovsky 2016.)
6. **Look at pure math, not just "X applied to AI"** — the pure-math agent
   found Connes-Kreimer that the AI-filtered one missed.

## Files of interest (in d:/AI/hd-instrument/)

- `notes/results_tracker.md` — running cumulative results
- `notes/research_playbook.md` — 6 standing practices
- `notes/design_space.md` — full axes of variation
- `notes/substrate_waves_8_13_designs.md` — original substrate audit results
- `notes/wave9_mps_design.md`, `wave10_rgflow_design.md`, `wave11_ldpc_design.md`,
  `wave13_hopf_design.md`, `hopf_algebra_survey.md`, `hopf_delta_cleanup_algorithm.md`,
  `wave14_connes_kreimer_design.md`, `buried_treasure_research_directions.md`
- `experiments/exp_*.py` — all prototypes
- `preregs/2026-05-18_*.md` — falsification criteria for each
- `data/exp_*/chunk_*.json` — per-condition results

## Memory entries (user-level, persistent across sessions)

- `user_profile.md`, `feedback_no_smoke.md`, `feedback_step_back_eval.md`
- `feedback_brain_inspired.md`, `feedback_plain_language.md`
- `feedback_verify_implementations.md`, `feedback_rehabilitation_after_rejection.md`
- `feedback_unbiased_research.md` (NEW: don't pre-filter research by AI)
- `project_two_bets.md`, `project_observability_layer.md`, `project_research_playbook.md`
- `reference_repo.md`

## Autonomous-session updates (running log)

Started autonomous queue at end of session, with these incremental findings:

- **Wave 11 LDPC unit test (CPU)**: INCONCLUSIVE. Both naive and LDPC achieve
  100% at all noise levels (2-30%). Test was too easy — 1024-dim random
  codewords stay separable even at 30% bit-flip. Re-test needed with higher
  noise or smaller dim before declaring LDPC has no advantage.

- **Wave 8 Clifford G(2,0) (GPU)**: bpc = 3.0569. **+0.55 worse than FHRR**.
  The audit's "grades act like multi-heads, 0.2-0.4 bpc gain" prediction
  was WRONG. Non-commutative geometric product alone doesn't help at byte LM
  scale. Possible reasons: G(2,0) is too small (4-dim slots), or the
  W readout doesn't benefit from the algebraic structure.

- **Wave 12 qFHRR (GPU)**: CRASHED with CUDA stack overrun on Q4. Needs
  debugging. The torch.complex(cos, sin) construction with quantized phases
  might have a shape mismatch or memory issue.

- **Wave 14.A shuffle Hopf (CPU)**: **100% recovery in all conditions** —
  both known-split-position AND all-splits-enumerated. The deconcatenation
  coproduct DOES deliver explicit decomposition. Caveat: test used
  one-hot word encoding which makes NN cleanup trivial. Need Wave 14.B
  with random hypervector encoding to validate at HDC scale.

## How autonomous execution should proceed

When user is away, work the priority queue:
- Launch GPU experiments sequentially (one at a time) via SSH
- Run CPU experiments locally
- After each result lands: 1-line summary to tracker + decide next move
- If a result strongly contradicts a literature prediction, audit before pivoting
- Don't write deep analysis docs in low-context mode; keep tracker entries
  brief and focused on numbers + 1-line interpretation

The session has been substantive. The work product is real research, well
documented, and reproducible. Future sessions can pick up from this doc.
