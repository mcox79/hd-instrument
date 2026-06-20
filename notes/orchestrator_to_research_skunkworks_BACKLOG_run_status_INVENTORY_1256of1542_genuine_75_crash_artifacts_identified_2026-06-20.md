# ORCHESTRATOR (run-status custody) -> Research + Skunkworks: COMPLETE backlog run-status inventory for the USER certify-the-backlog directive. 1256/1542 (81%) completed-with-verdict = GENUINE (cert/negative-classify confidently). Crash-artifacts = SMALL + IDENTIFIED: 74 OOM (chunk-fix) + 61 traceback (only 1 enabling). The certification is NOT sitting on a pile of misclassified artifacts.

**Re:** the operational complement to your scientific backlog-certification. (filename has to_research_skunkworks.) The composition-OOM-was-an-artifact lesson, generalized to the whole backlog.

## Backlog run-status (scanned all 1542 overnight_queue logs)
| status | count | % | meaning for certification |
|---|---|---|---|
| **completed-with-verdict** | **1256** | 81% | GENUINE result -> cert-grade or genuine-negative-classify confidently |
| OOM-crash | 74 | 5% | artifact (8GB-GPU large-N wall) -> chunk-fix + re-run BEFORE classifying; the enabling ones (composition/capacity/sparse/KG-sharded) are here |
| traceback-crash (non-OOM) | 61 | 4% | script-bug artifact -> code-fix + re-run before classifying; **only 1 is enabling-relevant** |
| other (incomplete/setup/in-progress) | ~151 | 10% | no verdict keyword -> setup logs / in-flight / partial |

## The actionable crash-artifact subset (re-run BEFORE treating as cert/negative)
- **OOM (74):** chunk-fixable (pythia-KV chunked pattern / existing RESCUE-serialized versions). Enabling ones = composition-extension, large-N capacity, sparse-vs-dense-large-N, KG-sharded-50k. (Detailed in my 8GB-GPU systemic note.)
- **Traceback, ENABLING (1):** `wave14_betX_skill_composition_v1` -- a non-OOM crash (script bug); skill-composition is enabling -> worth a re-run-after-fix before any "skill-composition negative" claim. (The other 60 traceback-crashes are non-enabling.)

## Why this matters (the verify-the-referent point)
- Composition N>2048's "negative/infra-failure" WAS an OOM-crash artifact (the capability was never tested). This inventory ensures the certification + the negatives-2x sweep do NOT cert-grade or negative-classify the ~135 crash-artifacts as if they were genuine results. The 1256 genuine ones are safe to classify; the 75 actionable artifacts (74 OOM + 1 enabling traceback) need a clean re-run first.
- The HIGH-priority cataloged negatives (N6/N7/N2) already CHECKED genuine (separate note) -> not in the artifact set.

## Standing
- Research/Skunkworks: certify the 1256 genuine results confidently; the crash-artifact subset (74 OOM + 1 enabling traceback) = re-run-before-classify (chunked for OOM). I can pull the exact OOM-enabling list (composition/capacity/sparse/KG) on request.
- Me: backlog run-status custody done (complete inventory); I dispatch the re-run cells (chunked, per the 8GB gotcha) when the certification prioritizes them. Reactive on the pipeline + composition cell (now SCHEMA-VET GO).

-- Orchestrator
