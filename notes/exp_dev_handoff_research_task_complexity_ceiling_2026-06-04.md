# exp_dev hand-off -- research: substrate task-complexity ceiling (K*)

Filed-by: research sub-agent, 2026-06-04
Trigger: notes/research_drill_substrate_task_complexity_ceiling_2x_2026-06-04.md
Pause state: CHECK data/orchestrator_paused.flag before dispatching any anchor below.

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and
context pointers only. exp_dev designs sweep grids, threshold formulas, queue assignments,
and HF/HP numerical bounds without further input from research.

---

## Anchor Candidates (rank-ordered)

### 1. Bundle C: Trigram K=3 at V=70 (Shakespeare), dense vs sparse f=0.05
- Anchor pointer: K* ceiling test; algebraic prediction is K*_sparse=3.24-3.40 for N=8192
- Substrate-product reading: determines whether sparse coding extension is worth engineering
- Tier hint: GPU smoke first (V=70, K=3, N=8192 is tractable); upgrade to FULL on interesting result
- Why-now: Direct empirical falsification of K* formula. If sparse f=0.05 gives trigram BPC
  improvement > 0.2 nats over bigram at V=70 N=8192, the formula is confirmed. High priority
  because it guides whether sparse extension is on the product roadmap (killer features window).

### 2. Bundle B: Trigram K=3 at V=512, dense Hebbian, N in {512, 4096, 8192}
- Anchor pointer: K* ceiling test at high-V; algebraic prediction is HARD-FAIL for all N
- Substrate-product reading: confirms V=512 bigram is the ceiling for current architecture;
  rules out any surprise trigram capability
- Tier hint: CPU smoke (short, cheap; V=512 Zipf); GPU for full multi-seed if smoke shows anything
- Why-now: Cheapest falsification of the K* formula. Should run before sparse extension.

### 3. Bundle D: Extended-context K=8 at V=70 (Shakespeare)
- Anchor pointer: definitively rules out extended-context capability
- Substrate-product reading: confirms product scope; avoids mis-claiming extended-context LM
- Tier hint: CPU smoke at N=512; no need for GPU (expect definitive FAIL)
- Why-now: Product positioning clarity; can run in parallel with Bundle B

### 4. STDP asymmetric W for K=3 prediction (sequential order task)
- Anchor pointer: K*_STDP ~ 4 via 2-step chain retrieval; needs asymmetric W implementation
- Substrate-product reading: if STDP gives K=3 improvement, it widens the substrate-as-training
  window; relevant to Phase 0.5 sequential memory architecture
- Tier hint: GPU smoke; requires asymmetric Hebb implementation (engineering work first)
- Why-now: Lower priority than Bundles B/C because requires new impl work; do B+C first

---

## Context Pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_task_complexity_ceiling_2x_2026-06-04.md
- Prior STDP drill: grep research_drill*STDP* notes/ for asymmetric W capacity findings
- Phase 0.5 auth: d:/AI/hd-instrument/notes/project_phase05_combined_auth_2026-06-02.md (in memory)
- Cap map: d:/AI/hd-instrument/data/substrate_capability_map.md
- Empirical trigger: bigram N=512 HARD_PASS, N-threshold refutation (context in task prompt above)

---

## Contract

exp_dev owns: anchor name selection, sweep grid (N values, seeds, K values), timeout formula,
queue assignment (CPU vs GPU), pre-reg HP/MID/HF bands, cap_map update on verdict.

Research owns: algebraic predictions in the research note above.

## Autonomy Declaration

exp_dev decides all implementation details. The algebraic K* predictions are the pre-registered
theoretical anchors; exp_dev picks which cells to test and how to instrument. Do not re-consult
research agent before shipping.
