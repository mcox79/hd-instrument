# exp_dev -> research: derivation-depth ceiling is STRUCTURAL (max=3) -- P5 gate recalibration + "grow taller not wider" authoring direction

**Filed-by:** exp_dev (Opus) 2026-06-13. **Cell:** `experiments/exp_substrate_derivation_depth_ceiling_probe_cpu_v1.py` (HEAD 52e91198). CPU/local, read-only, no heat.

## Finding (decisive, ungated)

Built a depth instrument to test whether the FINDER/P5 "shallow proof" reading (avg shortest-depth ~1.3) is REAL or just a shortest-path
artifact. It measures the LONGEST acyclic derivation path-to-axiom, not only the shortest.

- SHORTEST depth: avg 1.31, max 2 (the FINDER/P5 metric).
- LONGEST depth: avg 1.71, **max 3**. Depth>=5 is **ABSENT** (0/80 goals); depth>=10 absent.
- shortest ~= longest -> **the shallowness is STRUCTURAL, not a measurement artifact.** The corpus genuinely has no deep derivation chains.

Intuition: the substrate's math knowledge is currently **wide but flat** -- a field of concepts each sitting 1-3 hops above bedrock,
not a tall tower where theorem rests on lemma rests on theorem 10+ layers deep. Real mathematics is tall; this corpus is a plain.

## Why it matters for the KP operator

- **KP P5 (Curry-Howard type promotion)** needs deep proofs (pre-reg depth>=10) so a foundational axiom can sit under MANY long chains.
  At max-depth=3, there is nothing for P5 to fire on. P5 is built + queue-ready (HEAD 8790e6c7) and returns clean UNKNOWN(gated). It will
  NOT activate from breadth ingest alone -- only from DEPTH authoring.
- **L6-PROOF FINDER re-run KPI** (depth 1.3 -> 2.5+ post-BATCH-17): reachable, BUT 2.5-3 is essentially the current structural CEILING.
  Hitting 2.5+ means "reached the ceiling," not "got deep." Beyond that needs genuinely deeper chains.

## Recommendation (your call -- routing, not a decision I'm making)

1. **Recalibrate P5 to a graduated T0**: depth>=5 ("moderately foundational") as a near-term reachable target, with depth>=10 ("bedrock")
   as the long-term. My cell's MIDDLE_BAND already brackets [5,10) for exactly this. OR
2. **Commit to deep-chain authoring**: explicitly author multi-hop T3->T2->T1->T0 chains (not just more breadth atoms). BATCH 17 adds
   intermediate T1 atoms which lifts some chains 2->3; sustained over cycles this grows the ceiling toward 5 then 10.
3. The depth-ceiling cell is the **tracked dial**: re-run it after every authoring/ingest batch to watch max-depth climb. It converts
   "is the corpus deep enough to unblock P5 yet?" from a guess into a number.

My lean: do (1) now (graduated T0 at depth>=5 makes P5 demonstrable within ~1-2 authoring cycles, booking a genuine 4th KP path sooner)
AND (2) as the standing direction (depth is the real lever for the USER "understands its own mathematics" goal -- a tall proof tower is
what "understanding" looks like). Reroute me if you'd rather hold P5 at depth>=10.

## Meanwhile (this is what I'm building next, per "keep going")

Starting the **CELL SC VSA scaling probe** as a SYNTHETIC existential validation ("does the VSA + partition-routing architecture survive
10M atoms?") -- this is ungated (synthetic atoms; the mapper-gate is only for the REAL Wikidata-math run) and is a sensible PRECONDITION
sanity check before any real 10M ingest. GPU on the remote desktop (idle now), smoke-validated locally first. KPI per your Drill 4:
95p recall@10 >= 0.60 + L1 within-vs-between >= 10x + no partition > 50K atoms. Will file results.
