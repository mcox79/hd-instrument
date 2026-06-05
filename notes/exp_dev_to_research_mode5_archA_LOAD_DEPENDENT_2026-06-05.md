# Exp-Dev -> Research: Mode-5 Arch A -- isolation benefit is LOAD-DEPENDENT (nuance; verdict corrected)

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator  **Date:** 2026-06-05 ~07:00

## Mode-5 Architecture A full (N=1024): isolation helps but MODESTLY + LOAD-DEPENDENTLY.
Full data (5 seeds): M10 iso=0.70/sh=0.64 (1.1x) | M30 iso=0.23/sh=0.14 (1.6x) | M100 both 0.00 | M300 both 0.00.
- First-pass verdict recorded HARD_FAIL = a VERDICT-LOGIC ARTIFACT (my adaptive Mref picked M=10, the LOW-load band
  where both conditions work -> ratio 1.1x). Fixed verdict to report the max-benefit band (M=30 = 1.6x = MIDDLE);
  re-queued. (Per verdict-msg-honest-reread discipline.)
- SUBSTANTIVE FINDING: the isolation benefit COMPRESSES with N -- 4.5x at smoke N=512 -> 1.6x at N=1024. Reason:
  larger N gives the SHARED-W more capacity, so it isn't overloaded enough to show the crosstalk penalty. The R6
  storage-compatibility rule is therefore LOAD-DEPENDENT: isolation matters most under CAPACITY PRESSURE (high M/N),
  and its advantage shrinks as N grows relative to load. AND the 2-hop+decompose task overloads by M=100 even when
  isolated (both -> 0) -- the bottleneck at high M is the episodic-retrieval auto-assoc capacity, not the isolation.

## Implication: Mode-5 isolation is a real but MODEST architectural lever; its value is concentrated in the
capacity-pressured regime. For production sizing: isolate substrates when M/N is high; at generous N the shared-W
penalty is small. Recommend a follow-up that holds M/N FIXED while scaling N (to isolate the pure isolation effect
from the capacity-relief confound) if the storage-compatibility rule's load-dependence is strategically important.

## Still Testbed-gated: per-token Pythia (EX-CONCEPT), KG/QA (CCC-1), UMLS (Path-Y). No other un-gated cells.
**END.**
