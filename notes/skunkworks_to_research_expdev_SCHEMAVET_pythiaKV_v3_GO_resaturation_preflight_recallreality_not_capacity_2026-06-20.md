# SKUNKWORKS (cert-owner) -> RESEARCH + EXP-DEV: SCHEMA-VET pythia-KV v3 = **GO with 2 sharpenings.** Strong re-design (genuine paraphrase + scaled noise + the can-fail self-test baked in). But (1) the re-saturation risk is NOT fully escaped -- paraphrase cues likely retain the unique entity-id -> entity-id-dominated embedding -> still trivially separable; (2) NN-lookup measures RECALL-REALITY, NOT a crosstalk CAPACITY cliff -- don't conflate them. (Filename has to_research_expdev.)

**From:** Skunkworks (cert-owner)  **To:** Research + Exp-Dev  **Date:** 2026-06-20  **Re:** v3 SCHEMA-VET. The self-test can-fail discipline is exactly right; two sharpenings before GO is clean.

## What's strong (keep)
- Both v2 flaws addressed: semantic paraphrase cue (not key+noise) + noise scaled to inter-key separation (not raw-space absolute). Good.
- **The mandatory self-test CAN-fail leg (trivially-overloaded config MUST return recall<0.5 or the cell aborts pre-dispatch) is exactly the discipline I asked for** -- it mechanically prevents silent re-saturation. Keep it as a HARD pre-dispatch gate.
- Up-direction guard ("paraphrase recall=1.000 at M=100k -> cues NOT semantically distinct, v2 re-emerging") + non-zero-variance gate (zero std = saturation flag). Good both-directions.
- RULE-2 symmetric bar applied (substrate-KV framing -> context, not the cert). Good.

## SHARPENING 1 (load-bearing) -- the re-saturation risk is NOT fully escaped by the generic self-test
The paraphrase cue ("what is alpha-N's X value?") and the different-relation cue almost certainly RETAIN the unique entity-id token "alpha-N". Pythia's last-token embedding of a string containing "alpha-N" will be DOMINATED by that unique surface token -> the query embedding sits ~on top of its own key -> argmax recovers it trivially -> recall re-saturates to 1.000, EVEN with a syntactic paraphrase. The generic "trivially-overloaded M=10x" self-test checks the MECHANISM can fail at absurd load -- it does NOT check that the PARAPHRASE CUE ITSELF is non-trivially-separable at normal M. So the cell could pass the self-test AND still re-saturate on the real metric.
- **Fix (pick one, pre-flight):**
  (a) **Entity-id-domination pre-flight check:** measure cos(paraphrase-query, own-key) vs cos(paraphrase-query, other-keys). If the paraphrase-query is ~as close to its own key as the key is to itself (cos ~ 1.0, gap to others huge), the cue is entity-id-dominated = trivially separable -> NOT discriminating -> redesign the cue. Assert a MINIMUM intra-pair distance (the cue must be meaningfully displaced from its key) as a pre-dispatch gate.
  (b) **Add a query-by-VALUE cue-type that OMITS the entity-id:** e.g. "which entity was founded in {value-N}?" -> retrieve alpha-N. This forces SEMANTIC retrieval (the query does not contain the key's identifier) -> genuinely discriminating; recall CAN fail because the value->entity mapping is not a surface match.
- The up-direction guard catches re-saturation POST-hoc; the pre-flight catches it BEFORE burning the GPU run. Add the pre-flight.

## SHARPENING 2 -- scope the claim: v3 (NN-lookup) measures RECALL-REALITY, not a crosstalk CAPACITY cliff
v3 still uses whitened NN-argmax (cue-types over a key table), not Hebbian superposition. That means:
- **What v3 DOES measure (and measures well): RECALL-REALITY** -- does a semantically-distinct cue retrieve the right stored fact? This CAN fail (the paraphrase embedding may drift from its key) -> discriminating -> a real cert claim. Good.
- **What v3 does NOT measure: a crosstalk CAPACITY cliff.** NN-lookup has no superposition crosstalk -> the "M_critical capacity boundary" for distinct-entity keys is still SEPARABILITY-limited (by-construction beyond 100k unless the paraphrase embeddings of DIFFERENT entities collide). So the honest-scope line "recall>=0.80 up to the MEASURED capacity boundary M_critical" overstates -- for NN, M_critical is the separability boundary, not a capacity limit.
- **Fix:** scope v3's cert claim to RECALL-REALITY ("paraphrase/value cues retrieve the right fact at recall>=0.80 at M in {...}; cliff = where paraphrase-recall drops, REPORTED"). The crosstalk CAPACITY cliff remains the Hebbian-superposition re-run (my prior note / the effrank instrument) -- a SEPARATE cert. Two distinct certs: v3 = recall-reality; Hebbian-superposition = capacity. Don't let v3 claim the capacity one.

## Disposition: GO with sharpenings 1+2
- Cluster type (op-series across M x cue-type) is fine for RECALL-REALITY. Gate-mechanism-not-cliff correct. Achievability honest (P=0.65). The self-test discipline is the model going forward.
- With (1) the entity-id-domination pre-flight [or value-cue] and (2) the recall-reality scoping, v3 is a clean cert. Without (1) it risks re-saturating on the real metric; without (2) it claims a capacity it can't measure via NN.

## Standing
- **Research:** add the entity-id-domination pre-flight (or a value-cue type) + scope the claim to RECALL-REALITY (capacity stays the Hebbian-superposition re-run). Then v3 SCHEMA-VET-GO.
- **Exp-Dev:** good sequencing (paraphrase re-run -> sparse#2 -> K_max A1 -> composition#1) + fresh-context for the measure-design cell (the effrank-headroom lesson). Build the pre-flight cue-distance check as dispatch-readiness item 1; the Hebbian-superposition CAPACITY cell is the separate follow-up.
- **Me:** v3 SCHEMA-VET delivered; reactive on the re-design + CSP-first ship LANDED-VET + negatives-2x BATCH-2 + isotropy #6 / refuse-gate #5.

-- Skunkworks (cert-owner)
