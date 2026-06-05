# Exp-Dev -> Testbed: USER AUTHORIZED -- v7 killed (GPU freed) + run Pythia-160M residual extraction NOW

**From:** Exp-Dev  **To:** Testbed  **Inform:** User + Orchestrator  **Date:** 2026-06-04 ~22:00
**Re:** research_to_exp_dev_unblock_tier6_tier4_stageA USER ACTIONS. User answered both (2026-06-04 ~22:00):

## 1. Llama v7 = KILL NOW (Option A) -- DONE
User authorized Option A (kill v7; defer substrate-audit-on-real-residuals). I removed v7 from overnight_queue +
killed the procs. GPU is now FREE. Substrate-audit-core on real Llama residuals deferred -- re-attempt extraction
later with diagnostic flags (per-batch flush + per-doc hard timeout so a single bad doc fails-fast; both v6 @ doc
70300 and v7 @ doc 0 froze silently). No rush on the Llama npz now.

## 2. Pythia-160M residual extraction = RUN NOW (user authorized YES)
Please run a Pythia-160M last-layer (or specified-layer) residual extraction saving an npz to
data/<...pythia...>/*.npz. Pythia-160M loads reliably on the runner (algorithm1-debug ran) + is small/fast +
independent of the Llama hang. This unblocks (my side):
- EX-CONCEPT-1 REAL (VQ the activations -> concept IDs -> substrate concept-LM; proxy already shipped MIDDLE)
- Tier-4 Hopfield-attention substitution (needs the Pythia scaffold; substitution test itself doesn't need the
  npz, but the extraction confirms the scaffold + feeds EX-CONCEPT)
Ping me (note) when the npz path exists; I build EX-CONCEPT-1-real immediately.

## Meanwhile (my side, CPU, no GPU contention now):
Building Tier-6 Phase D on CPU (Shakespeare) + Stage-A-full + R1 4-modulator + R2 sparse-resonator. GPU now free
for Tier-4 (when I build it) + the capacity-comp N4096/N8192 reruns.
**END.**
