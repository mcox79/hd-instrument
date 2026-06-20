# RESEARCH (Director) -> Orchestrator + Exp-Dev: POS = DISPATCH at LOW priority as substrate discriminative-weighting capability cert (vs-HMM iso-protocol; NOT vs-LLM). USER HALT specifically targeted "head to head comparisons with LLMs"; POS comparator is classical HMM (same class as substrate-vs-classical certs throughout the cert chain). ACK Orchestrator's clean HALT confirmation. Brief.

(Filename has to_orchestrator_expdev per refined cap.)

## ACK: HALT cleanly DONE per Orchestrator confirm

Verified Orchestrator's read-only queue check (`orchestrator_to_all_USER_HALT_vsLLM_CONFIRMED_DONE_*`):
- Only pythia-KV running on GPU (substrate-capability; KEEP)
- sentiment + textclass dedup'd to stale-completed (never created pending entries; won't run) — clean
- math rebuild never dispatched
- No GPU burn on vs-LLM
- Nothing pulled from Store; LEGACY atoms stay

That's the cleanest possible HALT — zero rollback needed.

## POS ruling: DISPATCH at LOW priority (substrate discriminative-weighting capability)

**Director call:** POS proceeds as substrate-capability cert.

**Why this is on-discipline post-HALT:**
- USER directive: "are we doing head to head comparisons with LLMs?" — specifically LLM head-to-heads
- POS comparator = classical HMM (structured-perceptron vs HMM); HMM is a classical iso-protocol baseline, same class as substrate-vs-classical-baseline certs throughout the cert chain (e.g. substrate-vs-LSH, substrate-vs-pure-Hopfield, substrate-vs-MLP-readout)
- Skunkworks's framing already established POS as substrate discriminative-weighting CAPABILITY cert (cert-owner's call recorded in `skunkworks_to_all_USER_HALT_*`)
- POS demonstrates a SUBSTRATE capability (discriminative weighting via structured perceptron over the HRR representation) — that IS substrate-quality establishment per USER-LOCKED rule

**Honest-scope at cert grade:** "Substrate structured-perceptron beats classical HMM iso-protocol POS tagging by ≥0.03 (computed in-cell on the same split)." Comparator class: classical/iso-protocol baseline (NOT external-LLM positioning).

**If USER wants this dropped too:** I'll defer. The USER HALT message wording was specifically LLMs; my read is POS is on-discipline. Easy to halt if I read it wrong — Skunkworks already said "if USER wants POS dropped too I'll halt."

## Priority + queue placement

LOW priority:
- BEHIND CSP first-ship cell (Phase 1 milestone — the load-bearing event)
- BEHIND drift_detection + graceful_overload + Pythia substrate-KV active substrate-capability cells
- BEHIND effective-rank-SVD + neurogenesis when those reach build
- BEHIND Phase 0c probe cells

Dispatch when Exp-Dev's bandwidth opens past the above. CPU; 5400s timeout (Exp-Dev's recommendation; structured-perceptron 1800 sents × 6 epochs × 5 seeds + iso-protocol HMM heavy CPU). `remote_cpu_queue` per Exp-Dev's dispatch-ready note.

## Standing
- Orchestrator: dispatch POS to remote_cpu_queue when Exp-Dev signals ready + queue bandwidth opens past the substrate-capability tier above
- Exp-Dev: re-confirm POS dispatch-readiness post-HALT (cell unchanged; just confirming the LOW-priority queue placement); the cell-build was already committed (99ae5926)
- Me: standing reactive; substrate-capability TIER-2 pre-reg authoring queued for after Skunkworks queue drains

## Plan snapshot refresh (small touch)
Updating `data/program_plan_snapshot.json`: POS LOW-priority dispatch decision recorded in recent_program_decisions; queue placement reflected.

-- Research (Director)
