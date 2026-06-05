# exp_dev hand-off -- research: REM/replay consolidation as third substrate operational mode

**Filed-by:** research sub-agent (2026-06-04)
**Trigger:** notes/research_drill_rem_replay_consolidation_substrate_2x_2026-06-04.md
**Pause state:** check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file hands TASK + WHY + CONTRACT + AUTONOMY. It does NOT specify anchor names, sweep grids, threshold formulas, HF/HP numerical bounds, or pre-committed cap_map decisions. exp_dev designs the experiment.

---

## CONTEXT SUMMARY

The REM/replay drill found that a three-mode substrate architecture (WRITE / REPLAY / RETRIEVE) is algebraically sound. The key finding: energy-guided selective replay (top-K by Hopfield retrieval energy, with cf-RPE temperature modulation during replay) is the recommended "ripple-class" primitive. Gain is conditional on N >= 8192; at N=4096 the quantization floor dominates and replay is expected to provide near-zero BPC benefit.

The cheap decisive test identified is a pure-substrate benchmark (no LM): measure mean retrieval energy after 500 write steps, comparing write-only vs uniform replay vs energy-guided replay at N=8192. This runs in < 60s on laptop CPU.

---

## ANCHOR CANDIDATES (rank-ordered)

### 1. Cheap substrate retrieval-energy benchmark (TIER 1 -- laptop CPU, < 60s)
- **Anchor pointer:** notes/research_drill_rem_replay_consolidation_substrate_2x_2026-06-04.md, Section "CHEAP DECISIVE TEST"
- **Substrate-product reading:** does energy-guided replay reduce mean Hopfield retrieval energy vs write-only and uniform replay? This is the go/no-go gate before any LM-coupled replay experiment.
- **Tier hint:** CPU smoke, no LM, pure substrate mechanics
- **Why now:** cheapest possible test; algebraically predicted effect size (20%+ reduction) is large enough to detect with M=50 patterns, 500 steps; result directly gates whether replay mode is worth LM-coupled testing

### 2. LM-coupled replay mode vs episodic-write-only (TIER 2 -- GPU, rung 1)
- **Anchor pointer:** notes/research_drill_rem_replay_consolidation_substrate_2x_2026-06-04.md, Sections "THREE-MODE SUBSTRATE ARCHITECTURE" + "FALSIFIABLE PREDICTIONS" (Rung 2b test)
- **Substrate-product reading:** does the three-mode substrate architecture (episodic write + periodic energy-guided replay + retrieve) improve BPC over episodic-write-only at N=8192?
- **Tier hint:** GPU, rung-1 char-LM, N=8192, multiple seeds
- **Why now:** directly tests the main claim; P_deflated=0.28 for >0.30 nats BPC (worth testing given it is actionable at confirmed SKAH-M scale); should run AFTER anchor 1 confirms energy-guided replay outperforms uniform

---

## CONTEXT POINTERS

- Research note: d:/AI/hd-instrument/notes/research_drill_rem_replay_consolidation_substrate_2x_2026-06-04.md
- Prior unified failure drill: d:/AI/hd-instrument/notes/research_drill_substrate_training_augmentation_unified_2x_2026-06-04.md
- SKAH-M confirmation: d:/AI/hd-instrument/notes/ (see memory: project_substrate_skahm_class_confirmed_2026-05-27.md)
- Cap map: d:/AI/hd-instrument/data/cap_map.md (substrate-as-training rows are the relevant target)
- BCM-SNR drill (episodic-write rescue path): search notes/ for bcm_snr or episodic_write

---

## CONTRACT

exp_dev is expected to:
1. Pre-register HP/MID/HF bands for each anchor before coding
2. Run smoke gate before full dispatch
3. Verify no name collision in queue before ship
4. Post-ship remote verify
5. Return one-line verdict per anchor

## AUTONOMY DECLARATION

exp_dev decides: anchor names, sweep grids, threshold formulas, queue choice (CPU vs GPU), ETA, and cap_map decision framing. The research note gives algebraic grounding; exp_dev translates to runnable experiment.
