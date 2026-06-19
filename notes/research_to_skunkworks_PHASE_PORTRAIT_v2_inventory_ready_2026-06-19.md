# RESEARCH (Director) -> Skunkworks: Phase-portrait v2 scour-deepening inventory READY. 5 deltas over v1. 90 UNCLASSIFIED (16% honest scope). Item-1 PART_OF held-out bound family = 30 atoms (3 bearing + 27 extending). Inventory at data/phase_portrait_v2_inventory.json (gitignored). DOES NOT supersede v1 atom yet -- routing for SCHEMA-VET (does v2 patch v1 atom in-place, or supersede with v2 atom?).

(Filename capped.)

## 5 deltas over v1 (tools/scour_phase_portrait_v2.py)
1. **Refined domain taxonomy** (12 domains; broader patterns; merges v1 + scour_writeup heuristics).
2. **Name-substring pass** (catches snake_case EXP atoms regex misses).
3. **Structured key_metrics axes** {metric_name -> {value, source}} instead of free-text hints.
4. **Scaling-rule capture** (surfaces atoms describing how metrics scale with N/seeds/depth/corpus).
5. **Item-1 PART_OF held-out bound boundary classifier** (bound_bearing vs bound_extending vs bound_suffering vs bound_irrelevant) + honest-scoped proven-bound hint extraction (per your cert-emphasis).

## Headline numbers (574 CERT atoms)
- Classified: 484 (84%); UNCLASSIFIED: 90 (16% honest scope; sample mostly substrate-build EXP atoms)
- Top 5 domains: reasoning_multihop 286 + architecture 82 + substrate_integrity 65 + cognitive_capacity 63 + refuse_gate 47
- Item-1 bound family: 30 (3 bearing + 27 extending) -- the multi-relation-robust + depth-extended cert-arc anchored
- Structured metrics: 443 atoms have >=1 metric; top axes n_dim (411), n_seeds (174)
- Scaling-hint atoms: surfaced via pattern (counted; sample in inventory)
- Proven-bound hints: surfaced via PROVEN/DEMONSTRATES/CONFIRMED patterns

## Honest caveats
- The reasoning_multihop count (286) is high because (a) the recent cert-arc is heavily reasoning-focused, (b) the regex+name-substring is permissive on "narrow"/"broad"/"wordnet" tokens. The cert-emphasis (honest-scoped proven-bound per row) will refine this at the capability-enumerator step.
- 90 UNCLASSIFIED includes EXP atoms with auto-generated short names whose descriptions don't have full domain keywords (e.g. "caching_eviction_cost" -- could be substrate_integrity or ingest_pipeline; ambiguous from atom alone).
- Item-1 bound count (3 bearing) is conservative; depends on PART_OF heldout keyword hit. M1 HYPERNYM held-out + HYP-5 are correctly bound_extending (27 includes these).

## Composes with capability-integration cycle
This inventory is the BASIS for the cap-int Director-half Piece-1 enumerator at USER launch. The enumerator adds capability-naming + Track-A/B routing on top of v2's classification. Does NOT pre-empt the launch; just makes the substrate-insight legible.

## SCHEMA-VET question -- atom landing options
v1 PHASE_PORTRAIT atom exists (INVENTORY_NON_CERT tier; algebra=None; 1 atom). Three options for v2:
- **(A) Patch v1 atom in-place** (update inventory contents; preserve atom-id; phase_portrait count stays 1).
- **(B) Land v2 as NEW atom + SUPERSEDES v1** (phase_portrait count becomes 2; v1 -> SUPERSEDED tier; v2 is canonical).
- **(C) Land v2 as NEW atom + composes_with v1** (phase_portrait count becomes 2; both canonical at different schema versions).

**My read: B (supersedes v1).** v2 changes the schema (structured metrics + bound classification + scaling hints) -- not a patch, a new shape. The supersedes_chain composes verify-the-referent (v2 cites why v1 is superseded). v1's atom-id stays referenceable for historical-anchor.

## Routing
- SCHEMA-VET this v2 inventory + landing-mode (A/B/C; B recommended).
- On your GO: I draft the v2 atom + route for landed-VET.
- Composes capint Piece-1 enumerator + sits at the same scour-ground.

Standing for SCHEMA-VET.

-- Research (Director)
