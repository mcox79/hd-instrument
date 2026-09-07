# RECON — structured_semantic_matching (solver working notes; SOLVED.md is the final deliverable)

## THE JOB (bar, distilled)
Build ONE glass-box **structured semantic-matching organ**: given an observed EVENT/entity + a target RELATION
(converse / antonym / role-filler / type-membership), return the **SIGNED** match (satisfy vs thwart; is-a vs not;
fills-role vs not) from a STRUCTURED store seeded from **WordNet antonymy/hypernymy + FrameNet Perspective_on +
closed-class converse set + ConceptNet IsA/AtLocation/PartOf**; ABSTAIN to the ATL-hub fuzzy relatedness below a margin.
- COMPLEMENTS the hub (`hdlab/bridging_inference`), does NOT replace it. NO external LLM. Static offline KB = admissible.
- PROVE on a **MODERN** event<->goal congruence gold: beats (a) the distributional-hub baseline (`bridging_inference`
  relatedness thresholded to a sign — MUST lose on antonym/converse items) AND (b) an info-free **shuffled-KB twin**,
  CI-separated; polarity-isolation control (on the antonym subset the hub is at/below chance, matcher CI-sep above).
- TRANSFER the SAME organ to a 2nd consumer (spatial AtLocation/containment TYPE, or temporal script step-match),
  beating its stateless floor with the shuffled-KB twin losing.
- A rigorous LOCATED NEGATIVE is a full pass (likely split: closed-class lexical slice CLEARS; open-ended scene/type
  tail "stood on the podium = won" is a distinct Talmy/Schank script organ — the OCC SOLVED already located this).

## BRAIN FRAME (PINNED)
Two-store split: **ATL hub** = graded distributional relatedness (Lambon Ralph hub-and-spoke) — good at "how related",
blind to "which relation / which direction" (this is `bridging_inference`). The **combinatorial/relational** reading
(is-a, part-of, converse, antonym — the TYPE and SIGN) is a SEPARATE computation on the structured relational network
(angular gyrus / TPJ combinatorial semantics; Binder & Desai 2011). Polarity/direction is a STRUCTURAL fact, not a
similarity magnitude. PINNED relations: CONVERSENESS (Cruse 1986; FrameNet Perspective_on), ANTONYMY (WordNet antonym
edges — the sign flip), ROLE-FILLER/BENEFICIARY (FrameNet Assistance; Primus proto-recipient), TYPE-MEMBERSHIP
(WordNet hypernymy + ConceptNet IsA/AtLocation/PartOf). OUR-INVENTION (sweep): lexicon coverage, abstain margin,
fusion weight, type-similarity threshold.

## ON DISK (confirmed)
- `hdlab/bridging_inference.py`: `BridgeInference(source='hub', beta=0.0, tau=0.0)`, `.relatedness(target, cand, source=None)`,
  `.select(...)`. THE HUB BASELINE + fuzzy fallback. (Confirmed polarity-blind per OCC SOLVED sec5: rel(win,lose)~=rel(sell,buy).)
- `hdlab/goal_register.py`: `FAILURE_VERBS` (L445), `IRREG_PAST` (L462) — closed-class thwart hook. Check `converse=` arg.
- PRIOR ART (extend, don't re-derive): `experiments/exp_occ_converse_matching_v1.py` — BASELINE (converse=False) vs
  CONVERSE (`_occ_upstream_goal_status.track_status_thwart(converse=True)`) vs TWIN (permuted item). +0.417 (0.417->0.833),
  fire 0.50->0.92, twin 0.333. Gold: `experiments/data/occ_converse_probe_v1.jsonl` (n=12 CONSTRUCTED; fields:
  id/char/type/valence/prospect/text/**relation** e.g. converse_sell_buy, converse_lend_borrow, antonym-thwart, beneficiary).
- Reuse organs: `hdlab/occ_appraisal.py` (infer_emotion = 1st consumer), `hdlab/spatial_relational_model.py` +
  `location_register.py` (AtLocation/containment = transfer A), `hdlab/temporal_script_schema.py` + `temporal_reasoner.py`
  (script step = transfer B), `hdlab/meaning_foundation.py` (WordNet MFS fuzzy match).

## PLAN
1. VERIFY: empirically confirm hub polarity-blind on win/lose vs sell/buy via BridgeInference.relatedness; confirm converse hook.
2. Build `experiments/_structured_matcher.py`: a standalone organ. Signed match over WordNet antonym (sign flip),
   closed-class converse set + FrameNet Perspective_on, ConceptNet IsA/AtLocation/PartOf (type), FrameNet role-filler;
   ABSTAIN->hub below margin. Seed from FREE assets, HOLD OUT eval verbs.
3. MODERN event<->goal gold: construct a larger balanced satisfy/thwart set with converse+antonym+type slices (label
   constructed as a control) AND find a modern on-disk gold to lean on (candidates: for type-membership use WordNet/
   ConceptNet held-out pairs; for the 2nd consumer use SpaceEval/SpartQA containment-type or TRACIE script). Avoid 19c.
4. Measure: matcher vs hub-baseline + shuffled-KB twin CI-sep (paired bootstrap, half-width + null p95); polarity isolation.
5. TRANSFER to 2nd consumer (spatial containment-TYPE via WordNet hypernymy: "is a kitchen a room?" on a modern type gold,
   OR temporal script step). Same twin losing.
6. No-regress (matcher off = byte-identical; hub stays). Upstream (the assets / the hub) brain-foundational + no downstream regress.
7. Witnesses + SOLVED.md + `python tools/problem_ledger.py --check`.

## PROVENANCE / CONSTRAINTS
Solver scope: write experiments/, verification/, notes/problems/<slug>/ ONLY. NO hdlab (Q111 — propose diff). NO preregs/arm_key.
data/foundation READ-ONLY. If a tool call is DENIED: STOP, report verbatim. Ignore autoloop/STATUS. NO external LLM at inference.
Determinism: parse/WordNet may be hash-seed sensitive — reuse experiments/_hashseed_guard.py pattern if needed.
