# exp_dev hand-off — research: substrate-unique avenues utility audit (2x drill)

filed-by: research:opus-4.7-1M
trigger: 2x deeper research drill auditing 15 substrate-unique-vs-brain avenues for substrate-as-LM utility
source note: `d:/AI/hd-instrument/notes/research_substrate_unique_avenues_utility_audit_2x_drill_2026-06-23.md`
pause state: check `data/orchestrator_paused.flag` before dispatch

Per [[feedback-no-experiment-design-in-prompts]] — anchors below are POINTERS to substrate-mine candidates, not full pre-reg specs. exp_dev owns smoke + pre-reg + remote-verify per its role contract.

---

## Headline finding driving this hand-off

Of 15 listed substrate-unique avenues, only 2 (AVENUE 10 external grounding, AVENUE 5 K-bank) have literature precedent for measurable substrate-as-LM lift; 4 are INSTRUMENT-class (product narrative, not LM), 3 are CUTE-BUT-POINTLESS, 4 are UNTESTED with low priors, 2 have biological analog (not actually substrate-unique). This hand-off targets the ONE actionable lift candidate not already in flight: external grounding encoder bake-off under fair_harness.

---

## Anchor candidates (rank-ordered)

### PRIMARY (rank 1) — substrate_encoder_bakeoff_under_fair_harness_v1

**Anchor pointer:** 4-arm encoder bake-off run under the post-methodology-audit fair_harness, all on the SAME text8 10K holdout, same vocab/context/eval pipeline. Arms: (a) char-trigram baseline (substrate's existing forward-only), (b) word2vec frozen pretrained (Path A diagnostic probe), (c) Pythia-410M frozen embedding extract (Path B diagnostic probe), (d) substrate-owned encoder via predictive coding (Path C own-encoder candidate).

**Substrate-product reading:** if word2vec OR Pythia HARD_PASSes (BPC ≤ 1.8 vs ~5.0 char-trigram floor; delta ≥ 1.0 bit/char), confirms external grounding bypasses the substrate-encoder bottleneck identified as THE substrate-as-LM constraint. Frees substrate-product positioning to embrace the hybrid "substrate + external encoder" architecture. If all HARD_FAIL within ±0.15 of baseline, external grounding adds NO LM-relevant signal and substrate-as-LM is bottlenecked by something other than encoder — pivots strategy to receiver-side or compose-side investigation.

**Tier hint:** TRACK_A_APPLY candidate (cap_map impact significant in either direction)
**Why now:** session_2026-06-23_FINAL_pickup_state shows n1_v3 substrate top-1 = 0.445 vs unigram 0.276 when encoder is right — substrate WORKS, the open question is which encoder unblocks LM regime. fair_harness shipping anyway; encoder-bake-off variant is small add. Decisive test for the dominant load-bearing axis.

**Cost estimate:** ~15-20 min CPU local (4 arms × ~3-5 min each on 10K text8 holdout). Word2vec / Pythia weights already cached locally per late-session operational findings.

**Pre-reg HARD bands (research-pre-registered, exp_dev to verify smoke + post-ship):**
- HARD PASS: word2vec OR Pythia BPC ≤ 1.8 (delta ≥ 1.0 vs char-trigram floor)
- HARD FAIL: all 4 arms within ±0.15 BPC of char-trigram baseline
- MIDDLE_BAND: external lifts 0.2-0.8 bit/char (modest, partial info)

**Substrate-mine candidates exp_dev should check:**
- `tools/test_path_a_word2vec_diagnostic.py` or similar pre-existing word2vec probe (per late-session operational findings; gensim install OK'd on remote 2026-06-23)
- existing Path C own-encoder smoke cells in `cells/` matching `path_c_*` or `substrate_owned_encoder_*`
- fair_harness cell template (in-flight, pull from latest dispatch on data/recent_landings.jsonl or queue state)

---

### SECONDARY (rank 2 — DEFER, only if PRIMARY HARD_FAIL or MIDDLE_BAND) — substrate_ensemble_K10_LM_v1

**Anchor pointer:** ensemble lift test — K=10 substrates run with different random seeds, majority-vote or log-probability averaging at decode. Compared against single substrate (K=1) and K=5. Under fair_harness on same text8 10K holdout.

**Substrate-product reading:** AVENUE 12 audit gave LOW-MEDIUM EV; substrate's per-seed cheapness is engineering convenience, not capability advantage. **BUT** if encoder bake-off HARD_FAILs, ensembling becomes a low-cost branch to explore before pivoting strategy. Brain ensembles too via cortical-column redundancy, so this is more "matching brain" than "substrate-unique."

**Tier hint:** MEASURED_MECHANISM (cheap diagnostic; not chain-grade candidate)
**Why now:** ONLY dispatch if PRIMARY HARD_FAILs (signals encoder is not the bottleneck) AND no other higher-priority cell available. Otherwise defer indefinitely.

**Cost estimate:** ~30-40 min CPU local (10 seeds × 3 min for substrate forward pass).

**Pre-reg HARD bands:**
- HARD PASS: K=10 ensemble lifts ≥ 0.30 BPC over K=1
- HARD FAIL: K=10 lifts ≤ 0.10 BPC over K=1 (diminishing returns confirmed)

---

### TERTIARY (rank 3 — DEFER until BOTH PRIMARY and in-flight K-module land) — substrate_n_dim_scaling_fair_harness_sweep_v1

**Anchor pointer:** clean N_DIM ∈ {1024, 2048, 4096, 8192, 16384} sweep on fair_harness with single bank, single chosen encoder (from PRIMARY bake-off winner), fixed compose order. Single seed (3 seeds at chosen N). Focus is closing the N_DIM ambiguity, not exploring.

**Substrate-product reading:** AVENUE 2 audit gave LOW-MEDIUM EV; literature suggests no power-law scaling for HDC past optimal d ≈ 10K. **All prior N=16384 cells methodology-confounded** (OOM under bad harness). Clean fair_harness sweep CLOSES the ambiguity — either N is a tuning axis or it isn't, and we stop ever requesting larger dims.

**Tier hint:** MEASURED_MECHANISM (closure cell, not capability-discovery)
**Why now:** ONLY after PRIMARY lands (need encoder choice) AND in-flight K-module cell lands (need to know if K-bank dominates N). Defer until both. Then this becomes a clean 30-min closure on a long-running ambiguity.

**Cost estimate:** ~30-45 min CPU local (5 N values × 3-9 min each; memory-bound at N=16384).

**Pre-reg HARD bands:**
- HARD PASS: BPC monotonic decrease AND delta(16384 - 4096) ≥ 0.30 bit/char
- HARD FAIL: BPC flat or inverted past N=8192 (delta ≤ 0.05 per doubling)
- MIDDLE_BAND: monotonic but delta < 0.10 per doubling

---

## Context pointers (file paths, not summaries)

**Source research note (this drill):**
- `d:/AI/hd-instrument/notes/research_substrate_unique_avenues_utility_audit_2x_drill_2026-06-23.md`

**Convergent prior drills (all 2026-06-23):**
- `notes/research_negative_landings_evidence_totality_synthesis_2026-06-23.md` (10 negatives → 4-class taxonomy; receiver-structure unifying root cause)
- `notes/research_substrate_lm_experimental_methodology_3x_drill_2026-06-23.md` (+0.44 envelope cap METHODOLOGY-CONFOUNDED)
- `notes/research_substrate_modulatory_architectural_parameter_taxonomy_2026-06-23.md` (4 of 17 parameters load-bearing — K-bank, compose-order, compose-function, per-context T)
- `notes/research_substrate_representational_temporal_parameter_taxonomy_2026-06-23.md` (amplitude scaling 1/sqrt(f) under-recognized load-bearing)
- `notes/research_neuroscience_methodology_for_substrate_lm_3x_drill_2026-06-23.md` (6-arm compose factorial discipline)

**Substrate-as-LM bottleneck framing:**
- `MEMORY:project_substrate_arc_2026-06-23_encoder_is_THE_bottleneck.md`
- `MEMORY:project_session_2026-06-23_FINAL_pickup_state.md` (n1_v3 top-1=0.445 vs unigram 0.276)
- `MEMORY:project_substrate_as_LM_test_harness_rigged_2026-06-23_methodology_audit.md`
- `MEMORY:project_path_c_substrate_owned_encoder_is_the_answer_USER_2026-06-23.md`

**Related in-flight cells (verdicts will inform anchor choice; check `data/recent_landings.jsonl`):**
- `substrate_k_module_heterogeneous_compose_LM_v1` (overnight_queue; AVENUE 5 PRIMARY test for K-bank)
- `fair_harness_*` cells (substrate-as-LM methodology-corrected harness)
- per_context_T / dual_trace cells from prior dispatch (not directly related to this audit's findings)

**Late-session operational findings (encoder candidates infrastructure):**
- `MEMORY:reference_operational_findings_2026-06-23_late_session.md` (gensim install OK'd; word2vec cache nested path)

---

## Contract section

This hand-off is a POINTER, not a cell spec. exp_dev owns:
1. **Smoke gate** — verify each encoder loads + forward-passes on substrate's existing infrastructure (10K text8 dummy run with 1 seed before full ship)
2. **Pre-reg verification** — confirm HARD bands above match exp_dev's measurement standards under fair_harness
3. **Substrate-mine** — check if any of these cells (or close variants) ARE in `data/recent_landings.jsonl` or `data/atoms.jsonl` per Fix #26 pre-dispatch verify-the-referent gate before spawning
4. **Post-ship remote verify** — per role contract
5. **Ship via queue_add.sh** — local_cpu_queue for PRIMARY (small CPU job); overnight_queue for SECONDARY/TERTIARY if dispatched

## Autonomy declaration

exp_dev decides:
- whether smoke clears (gate)
- exact cell-spec content (cell-author owns the implementation; this hand-off is bounded pointers only)
- ship order (PRIMARY only initially; SECONDARY conditional on PRIMARY HARD_FAIL; TERTIARY conditional on PRIMARY AND in-flight K-module both landed)
- whether to consult Skunkworks for VET before ship (recommended for PRIMARY given cap_map impact)

research decides:
- HARD bands per the source note (above)
- which avenues to drill deeper (next 2x cycle, conditional on PRIMARY verdict)
- companion drill dispatch if cells reveal new adjacencies

---

## Per [[feedback-fix26-predispatch-verify-the-referent-gate]]

Before any spawn, exp_dev MUST run `python tools/predispatch_check.py substrate_encoder_bakeoff_under_fair_harness_v1` and check:
- `data/recent_landings.jsonl` for prior bake-off cells (avoid duplicate)
- `data/atoms.jsonl` for prior word2vec / Pythia / Path-C encoder evidence already-banked
- previous-arc HARD_FAIL re-dispatches (n1_v3 already partially answered this; verify what's NEW vs what's already-banked)

If substrate-mine reveals encoder-bake-off was ALREADY DONE under fair_harness, this hand-off is REDUNDANT — exp_dev should defer and notify research for verdict-classification update.
