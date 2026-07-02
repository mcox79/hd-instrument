# M1.9 Semantic Parser primitive — design drill

**Date:** 2026-07-02
**Author:** research (Director main-thread, inline; no sub-agent delegation per drill directive)
**Trigger:** USER 2026-07-02 confirmed Option 1 priority: M1.11 in flight (Option C ext a66e5ea), M1.9 next, M1.10 later.
**Substrate-KB concept-query performed FIRST (4 queries):** rich prior work found — dual-substrate W_lex + W_gram Wernicke/Broca (research_drill_llm_boundary_is_engineering_3x_2026-06-11.md); TALKS-2 substrate intent parser for conversation acts (research_to_exp_dev_SUBSTRATE_TALKS_ADDENDUM_2026-06-08.md); "Compositional binding LOAD-BEARING for Q3" (research_primitive_decision_linear_vs_recurrent_2026-05-25.md); IntentClassifier already CG at n_intents=50 (hdlab/intent_classifier.py — Hebbian one-shot bound; acc=0.754; maj_mult=4.62; rand_mult=5.19; p95=0.54ms).

**Load-bearing consequence of prior work:** M1.9 is NOT a from-scratch design. The intent-extraction leg is ALREADY substrate-native and chain-grade (IntentClassifier + CharTrigramEncoder). This drill extends the primitive to (a) slot value extraction, (b) context resolution, (c) discourse structure — three legs on top of the existing intent leg.

---

## 1. Brain analog — Wernicke's area, temporal cortex, left STG

The brain does NOT do "semantic parsing" as a single monolithic operation. It's factorized across at least four cortical regions, each of which has a substrate analog we can identify.

**Hickok & Poeppel 2007 dual-stream model** (substrate KB chunk 022 already cites this): acoustic/orthographic input splits into (a) DORSAL STREAM (left STG → inferior parietal → left frontal) doing sound-to-articulation mapping — substrate analog is our sequence-preserving encoder path; (b) VENTRAL STREAM (posterior middle temporal + posterior inferior temporal) doing sound-to-meaning mapping — substrate analog is our lexical retrieval + compositional bind path. The VENTRAL stream is what M1.9 primarily instantiates.

**Fedorenko lab findings on the language network** (Fedorenko et al 2011-2024, Sci Rep 2020 "The language network is recruited but not required for non-linguistic cognition"): the "language network" (left inferior frontal + left superior temporal) is domain-specific — it does language-parsing, not general problem-solving. This is architecturally IMPORTANT for M1.9: the semantic parser should be a SPECIALIZED primitive, not a general classifier that happens to also do parsing. Substrate implication: dedicated codebooks per parsing sub-task (intent codebook, slot codebook per role, reference-resolution codebook), NOT one giant undifferentiated field.

**Friederici 2011** (Physiol Rev "The brain basis of language processing"): three-phase syntactic processing model — (I) initial phrase structure ~ 100-200ms in left anterior temporal; (II) syntactic-semantic integration ~ 300-500ms in left posterior superior temporal + left inferior frontal (Broca's); (III) reanalysis if needed. Substrate implication: parsing is INHERENTLY multi-stage; a single Hebbian bind won't capture full semantic parse. Need at least a two-pass architecture where pass-1 extracts intent + surface slots, pass-2 does compositional integration + reference resolution.

**Recent brain-LLM alignment work** (Toneva & Wehbe NeurIPS 2019; Caucheteux & King 2022 Nat Comm; Schrimpf et al PNAS 2021): the strongest brain-alignment scores come from mid-layer representations of LLMs, which are compositional semantic representations. These layers do WHAT M1.9 needs to do: convert token sequences into role-bound compositional vectors. Substrate can mimic this with binding operations on IntentClassifier output.

**Fedorenko-Piantadosi 2024 review** (Nat Rev Neurosci): explicit claim that language regions do NOT support propositional thought — semantic parsing (form → meaning) is separable from reasoning (meaning → new meaning). Direct architectural implication: M1.9 (parse) is separate from M1.4/M1.6/M1.8 (retrieval + gating). Composition order matters — parse BEFORE retrieve BEFORE gate.

**Cite ledger:**
- Hickok & Poeppel 2007 Nat Rev Neurosci "The cortical organization of speech processing"
- Fedorenko, Behr, Kanwisher 2011 PNAS "Functional specificity for high-level linguistic processing in the human brain"
- Friederici 2011 Physiol Rev "The brain basis of language processing"
- Caucheteux & King 2022 Nat Comm "Brains and algorithms partially converge in natural language processing"
- Fedorenko, Piantadosi, Gibson 2024 Nature "Language is primarily a tool for communication rather than thought"

---

## 2. Function decomposition

M1.9 must produce four outputs from an input HD (from CharTrigramEncoder over token sequence):

**(a) Intent extraction** — what type of question/statement is this?
- Codomain: enum over intent-types (Q_FACT, Q_YESNO, Q_FOLLOWUP, STATEMENT, COMMAND, CLARIFY_REQUEST, ...).
- Mechanism: IntentClassifier ALREADY EXISTS. n_intents=50 Hebbian bound; extend to n_intents=~200 for a richer conversational surface. Prior extension EXT-3 documented 50→1000 intents chain-grade.

**(b) Slot value extraction** — what entities/attributes are being referenced?
- Codomain: set of {role: value_hd} pairs. Roles are typed (SUBJECT, OBJECT, ATTRIBUTE, TIME, LOCATION, RELATION).
- Mechanism: compositional bind. Substrate stores a slot-dictionary per role, sharded per storage-strategy CG_META (2026-07-02). Extraction = for each role, unbind role_key from the input HD to recover value_hd, then cleanup against role's slot dictionary.
- This is the LOAD-BEARING new work vs the existing IntentClassifier.

**(c) Context resolution** — are pronouns/references pointing to prior turns?
- Codomain: {reference_span_id: resolved_value_hd | UNRESOLVED}.
- Mechanism: multi-hop retrieval (multi_hop.py) over the M1.5 TwoTierContext STM buffer. If a slot-value HD looks like a pronoun-class HD (similarity to PRONOUN codebook > tau), replace with M1.5 read on the most recent role_key of matching type.
- Depends on M1.5 already existing. Composition tight.

**(d) Discourse structure** — is this a follow-up, topic-change, clarification?
- Codomain: enum {NEW_TOPIC, FOLLOWUP, CLARIFICATION, TOPIC_CHANGE, ANAPHORIC_CONTINUATION}.
- Mechanism: similarity of current-turn intent HD to previous-turn intent HD, plus similarity of slot values to prior turn. Two-threshold gate (like M1.8 ClarifyGate) — high sim → FOLLOWUP; low sim → NEW_TOPIC; mid + shared entities → CLARIFICATION.

**Factorization note (brain-grounded):** legs (a), (b), (d) are ventral-stream operations (Wernicke/temporal); leg (c) crosses hippocampus (M1.5 substrate) for retrieval. This matches PFC not being in the loop until M1.10 (Response Planner). Clean separation.

---

## 3. Stage 3 vs Stage 4 scope decision

**Stage 3 version — structured input, substrate-native, ships FIRST.**

- Input: token sequence over a KNOWN VOCAB (e.g. hdlab/token_vocab.py already exists at 301 lines; supports vocab lookup + HD encoding via CharTrigramEncoder).
- Slots come from a KNOWN SCHEMA (e.g. `{SUBJECT: "kelvin", OBJECT: "hd-instrument", ACTION: "designs"}`).
- Discriminator: intent-match accuracy vs symbolic parser baseline + slot-fill accuracy per role.
- Ships without new infra. Leverages IntentClassifier (CG), sharded storage (CG_META), M1.5 TwoTierContext (M1.5 shipped), multi_hop (chain-grade), CharTrigramEncoder (chain-grade).
- Substrate-doesn't-know-anything discipline honored: substrate never sees "language" it doesn't have a dictionary for — the schema IS the semantics; parse is a structural map from token sequence to role-bound HD.

**Stage 4 version — real language parse, needs language-ingest infra.**

- Input: token sequence over LARGE vocab (BPE or word-level over English corpus).
- Slots come from LEARNED role decomposition (like SRL, semantic role labeling, over parsed constituency trees).
- Requires: lm_eval_harness.py + token_vocab.py + bigram_gap_measurement.py (df8511e82 shipped 2026-06-30) — YES, these exist. But it ALSO requires: (a) a large-vocab codebook (needs ~50k intents-of-tokens for open-vocab), (b) syntactic-role labels ideally from a treebank, (c) MUCH larger slot dictionaries.
- Discriminator: harder to construct — no ground-truth "parse" without treebank. Would need to eval against propbank/framenet gold-standard SRL parses.

**Recommendation: BUILD STAGE 3 FIRST. Reasons:**

1. **Stage-progression discipline (USER LOCKED 2026-06-26):** substrate is at Stage 1/2/3 maturity; Stage 4 LM equivalence is DEFERRED-BUT-ACTUAL per glass-box LLM correction (USER 2026-07-01). Don't skip.
2. **Stage 3 IS the primitive that M3 conversational eval needs.** Any conversational demo with a fixed capability domain (e.g. "personal assistant over a fixed schema of calendar/contacts/tasks") is Stage 3 semantic-parse work. M3 doesn't require Stage 4 open-vocab.
3. **Stage 3 primitive is a scaffold to Stage 4 later.** The mechanism (bind role_key with input → unbind → cleanup) is IDENTICAL between Stage 3 (small dict) and Stage 4 (large dict). Scale-scaling of the slot dictionary is a separate CG'able extension question, not a mechanism question.
4. **Stage 4 discriminators are HARD.** SRL gold is expensive; treebanks are noisy; no clean pass/fail band.
5. **Stage 3 P_CG > Stage 4 P_CG by ~0.2** — Stage 3 leverages three existing CG primitives (IntentClassifier, sharded storage, TwoTierContext), Stage 4 requires new infra + new evals.

**Decision: Stage 3 first (this note designs the Stage 3 cell). Stage 4 filed as follow-on after Stage 3 chain-grades.**

---

## 4. Substrate mechanism candidates

Four candidates for the Stage 3 mechanism, ranked.

**Candidate 1 — RECOMMENDED — Compositional binding of intent-vector + slot-value bundle.**

Mechanism (fits sharded storage CG_META today):
```
input_hd = CharTrigramEncoder(token_sequence)     # (n_dim,)
intent_hd = IntentClassifier.predict(input_hd)    # already CG; use codebook lookup post-argmax to get intent_hd
                                                   # (n_dim,)
for role in ROLES:                                 # SUBJECT, OBJECT, ATTRIBUTE, TIME, LOCATION
    role_key = ROLE_CODEBOOK[role]                # (n_dim,) fixed random
    unbound = unbind(input_hd, role_key)          # circular unbind for HRR; XOR for BSC
    value_hd = SLOT_DICT[role].cleanup(unbound)   # per-role SHARDED dictionary (CG_META fit)
    slots[role] = value_hd

parse_hd = intent_hd
for role, value_hd in slots.items():
    parse_hd = bundle(parse_hd, bind(ROLE_CODEBOOK[role], value_hd))

return {intent, slots, parse_hd}
```

Leverages:
- IntentClassifier (CG at n=50-1000)
- Sharded storage per role (CG_META 2026-07-02, storage-strategy formalization)
- Cleanup primitive (chain-grade)
- HRR/BSC bind-unbind (chain-grade via CG_META)

Failure mode: slot cross-talk — if two roles have similar value distributions, unbind may recover ambiguous HD. Mitigate by role-specific dictionaries with disjoint token subsets (sharded exactly as the CG_META prescribes).

**Candidate 2 — Chunked attention over role-key tape (M1.6 already exists).**

Mechanism: treat the input as a sequence of chunks; run M1.6 chunked_attention_readout for each role_key as query. Wins: reuses cortex.Cortex.forward directly. Losses: doesn't naturally handle compositional slot extraction — attention gives a weighted mixture, not a discrete role-bound HD.

Use as CROSS-CHECK arm in the cell, not primary mechanism.

**Candidate 3 — Multi-hop retrieval for reference resolution (multi_hop.py, chain-grade).**

Not primary parse mechanism; SUPPORTS Candidate 1's leg (c) context resolution. When slot value looks pronoun-like (sim to PRONOUN codebook > tau), invoke multi-hop over M1.5 STM to get the referent.

Composition: 1 → 3.

**Candidate 4 — Novel: substrate as recursive parser (each parse step is a substrate retrieval).**

Idea: for compound queries like "which task did I create yesterday that mentioned kelvin?" — parse as nested (Q_FACT (SUBJECT task) (RELATION mentioned) (OBJECT kelvin) (MODIFIER (TIME yesterday))). Recursion depth ~ 2-3.

Mechanism: recursive slot extraction — for each slot, if the extracted value_hd cleanup falls below tau, RECURSE by treating value_hd as a sub-input and re-running the parser.

Chain-grade RISK: depth explosion + confidence decay per hop. Prior chain-grade multi-hop caps at depth 15-20 with graceful degradation. This is NOVEL SYNTHESIS territory — cap P at 0.50 per lit-scan calibration penalty. Defer to M1.9 v2 after v1 CG.

**Winner: Candidate 1 for Stage 3 M1.9 v1. Candidate 3 folded in for reference resolution. Candidates 2 + 4 as follow-on drills.**

---

## 5. Concrete cell design (Stage 3 v1)

**Anchor:** `substrate_semantic_parser_intent_slot_extraction_v1`

**Substrate-KB concept-query BEFORE ship:** MANDATORY — repeat this drill's query, plus `bash tools/substrate_query.sh "semantic parser cell design intent slot extraction v1"` before cell-author ships.

**Cell file:** `experiments/exp_substrate_semantic_parser_intent_slot_extraction_v1.py`

**Config:**
- `n_dim = 8192` (inherited from cortex primitives)
- `n_intents = 50` (matches IntentClassifier CG state; extend to 200 in v2)
- `n_roles = 5` (SUBJECT, OBJECT, ATTRIBUTE, TIME, LOCATION)
- `slot_dict_size_per_role = 100` (sharded per storage-strategy CG_META)
- `n_train_examples = 500` (Hebbian one-shot; ~10 per intent)
- `n_test_examples = 200` (out-of-training-set; disjoint sample)
- `seeds = [11, 17, 23]` (3-seed smoke gate mandatory per Skunkworks META CG 2026-07-02)
- Token vocab: derived from a synthetic Stage 3 schema (personal-assistant-domain: 500 tokens across intent/entity/attribute types)

**Arms (per-arm smoke at full-N per DISCRIMINATOR_MUST_SURVIVE_SCALE):**
- ARM_BASELINE: symbolic-parser baseline (dict lookup + regex slot extract) over the same synthetic data. Expected: 1.0 on intent, 1.0 on slots (baseline is symbolic ground-truth).
- ARM_SUBSTRATE: Candidate 1 substrate mechanism.
- ARM_INTENT_ONLY: IntentClassifier alone (no slot extraction) — CROSS-CHECK to isolate the slot-extraction contribution.
- ARM_M16_ROUTER: Candidate 2 M1.6 attention as alternate slot-extraction — CROSS-CHECK to demonstrate mechanism choice.
- ARM_SHUFFLED_ROLE_KEYS: sanity control — shuffle role_keys before unbind; slot accuracy MUST collapse toward random (validates that role-binding is doing real work, not just cleanup on any-key).

**Discriminator + bands:**
- Intent-match accuracy on held-out test.
- Slot-fill accuracy per role, averaged.
- Both measured vs the symbolic ground-truth on synthetic data (which we generated, so we know gold).

**Bands:**
- **HARD_PASS:** intent-match ≥ 0.85 (matches IntentClassifier prior CG floor); slot-fill ≥ 0.80 (all roles); 3 seeds; ARM_SHUFFLED_ROLE_KEYS collapses to ≤ 0.20 (verifies role-binding is real).
- **MIDDLE_BAND:** intent-match in [0.70, 0.85) OR slot-fill in [0.60, 0.80) — partial success; investigate role-specific cross-talk.
- **HARD_FAIL:** intent-match < 0.70 OR slot-fill < 0.60 OR ARM_SHUFFLED_ROLE_KEYS > 0.30 (role-binding not doing work).

**Envelope-fail bands:**
- If ARM_BASELINE < 0.99 on any leg: SCHEMA_BROKEN, halt and repair.
- If ARM_INTENT_ONLY intent-match ≥ ARM_SUBSTRATE intent-match by > 0.03: substrate cell has a bug in intent-classifier composition, HARD_FAIL.

**CARDINALITY_OK field:** MANDATORY per META_RULE_H — declare EXPECTED_N_UNITS = 5 arms × 3 seeds × 200 test examples = 3000 rows. HARD_FAIL_CARDINALITY_BREACH if observed_rows < 2800 (allow 7% margin for occasional NaN drops).

**Sharded storage:** slot dictionaries stored per-role in separate S-bank buffers (per storage-strategy CG_META). Sharding key = role_id. Bank size = slot_dict_size_per_role = 100. Total slot storage = 5 × 100 = 500 HD vectors — well within substrate capacity at N=8192.

**Multi-seed smoke gate:** MANDATORY (Skunkworks META CG 2026-07-02). Smoke run must complete all 3 seeds at full-N before FULL dispatch. Per USER 2026-07-01 smoke-only-local-cpu rule: smoke on local, FULL on remote_cpu_queue.

**Runtime estimate:**
- Smoke (3 seeds × 5 arms × 200 test): ~5 min local CPU (Hebbian ops O(n_dim^2) = ~67M float mults per prediction; well under 100ms per predict on CPU).
- FULL (same shape; 1000 test examples, 3 seeds): ~15 min remote CPU. Not GPU-required (no matmul-heavy batch large enough to warrant per GPU-batching-mandatory-when-speedup-available rule); flag as CPU appropriate.

**Metrics.json REQUIRED_FIELDS (per SCHEMA-VET checklist):**
- `intent_match_acc_per_seed_per_arm`
- `slot_fill_acc_per_role_per_seed_per_arm`
- `slot_fill_acc_overall_per_seed_per_arm`
- `arm_shuffled_role_keys_collapse_metric`
- `n_rows_observed`
- `n_rows_expected`
- `cardinality_ok`
- `run_mode` ("smoke" | "full" per METRICS_PATH_DISAMBIGUATION discipline)

---

## 6. P_CG estimate + justification

**P_CG = 0.55.**

Justification (per lit-scan calibration penalty — deflate 0.15-0.25 from initial estimate; cap novel-synthesis P at 0.50):

**Initial estimate before penalty: 0.75.**
- IntentClassifier already CG at n=50-1000 → intent leg is high-probability CG (0.90+).
- Slot extraction via bind-unbind-cleanup is textbook VSA/HRR (Kanerva 2009; Plate 1995 HRR) — established mechanism, not novel synthesis.
- Sharded storage per role is EXACTLY the CG_META (2026-07-02) prescription.
- Symbolic-parser baseline on synthetic data gives us clean ground-truth; no eval ambiguity.
- Composition of intent + slot: prior chain-grade evidence for compositional binding (research_primitive_decision_linear_vs_recurrent_2026-05-25.md — LOAD-BEARING for Q3).

**Deflate 0.20 for:**
- Slot cross-talk risk: unknown until measured. If slot dictionaries have low pairwise separability, cleanup ambiguity could tank slot-fill accuracy. This is an empirical unknown, so penalize.
- Compound mechanism: 4 legs (intent + slot + context + discourse); v1 only ships 2 legs (intent + slot), but the parse_hd bundle representation is untested at this scale.
- Discriminator novelty: slot-fill accuracy metric is new for this substrate; no prior CG evidence of this exact metric.

**Empirical evidence supporting P_CG ~ 0.55:** substrate can host STRIPS planning bit-identical (stretch4_3/2_3 v2 CG'd today) — that's a compositional symbolic task where the substrate implements symbolic ops through binding. Semantic parsing is the same class of task (compositional bind + retrieve). Similar mechanism should work. This session evidence tilts P upward from the pure lit-scan estimate.

**NOT novel synthesis** — this extends existing CG primitives (IntentClassifier, sharded storage, HRR/BSC bind-unbind). So 0.50 cap doesn't apply. 0.55 stands.

**Failure modes and their probability:**
- Slot cross-talk causes HARD_FAIL: P ~ 0.20. Mitigation via disjoint slot dictionaries per role reduces to ~0.10.
- ARM_SHUFFLED_ROLE_KEYS doesn't collapse (role-binding isn't doing work; substrate is just doing intent-only via cross-talk): P ~ 0.10.
- MIDDLE_BAND on partial cross-talk (intent solid, slot partial): P ~ 0.30.
- Cell has a bug in composition: P ~ 0.05 (mitigated by 3-seed smoke gate + arm cross-checks).

**Total P_CG_after_v1_iteration:** 0.55. **P_MB or P_CG after v2 iteration on cross-talk root-cause: 0.75+.**

---

## 7. Composition with existing cortex primitives

Current `Cortex.forward()` (from cortex.py 217-380):
```
query -> [M1.5 write?] -> [M1.3 noise?] -> [M1.6 attn OR M1.5 read] -> M1.4 refuse -> M1.8 clarify -> [M1.7 role_slot_summary?] -> CortexResponse
```

M1.9 slots into this pipeline at the FRONT, before retrieval. Proposed composition:

```
raw_input (token sequence)
  |
  v
[CharTrigramEncoder]  -->  input_hd
  |
  v
[M1.9 SemanticParser]  -->  {intent, slots, parse_hd, discourse_state}
  |                          (this is the NEW primitive)
  v
[M1.3 NoiseChannel]  -->  parse_hd_noisy   (Phase 2b already lives here)
  |
  v
[M1.6 chunked_attention_readout(parse_hd_noisy, context_keys, context_vals)]
  |  OR
  v
[M1.5 TwoTierContext.read(parse_hd_noisy)]
  |
  v
[M1.4 apply_refuse]  -->  refuse_accept flag
  |
  v
[M1.8 ClarifyGate.evaluate]  -->  route
  |
  v
[M1.7 RoleSlotSummarizer (opt)]  -->  provenance role_slots
  |
  v
CortexResponse (extended with M1.9 fields: parse_hd, intent, slots, discourse_state)
```

**Key composition claims:**
- M1.9 output `parse_hd` is a compositional HD (intent bundled with role-bound slots). It's a stronger retrieval query than raw input_hd because roles are explicit.
- Passing `parse_hd` to M1.6 attention gives BETTER max_sim because context_keys can be indexed by role.
- M1.9 output `intent` can be used to gate WHICH context store to query (routing between multiple M1.5 stores per intent-type).
- M1.9 output `discourse_state` can bypass M1.4/M1.8 for CLARIFICATION intents (route immediately to M1.8 output).

**CortexResponse extension required:**
```python
@dataclass
class CortexResponse:
    # existing fields ...
    m19_intent: Optional[int] = None
    m19_slots: Optional[Dict[str, torch.Tensor]] = None
    m19_parse_hd: Optional[torch.Tensor] = None
    m19_discourse_state: Optional[str] = None
```

**Order of ops rationale (brain-grounded):**
- Parse-first mirrors Friederici 2011 phases I + II (100-500ms parsing) preceding integration.
- Retrieve-then-gate mirrors ventral-stream retrieval (M1.6/M1.5) preceding executive gating (M1.4/M1.8) — matches Fedorenko-Piantadosi separation of parse from reasoning.
- Noise injection between parse and retrieve preserves the M1.3 boundary discipline (substrate stays deterministic; cortex injects stochastic coupling).

**When M1.9 lands, cortex.py forward() needs a modest patch: accept an optional `token_sequence` input and, if provided, run M1.9 to produce parse_hd + slots BEFORE the existing pipeline. Backwards-compat by default (accept raw query HD when token_sequence not given).**

---

## Summary

- **Recommended path: Stage 3 first.** Ships without new infra by leveraging IntentClassifier (CG at n=50-1000), sharded storage (CG_META 2026-07-02), CharTrigramEncoder (CG), M1.5 TwoTierContext (M1.5 shipped), multi_hop (CG). Stage 4 open-vocab language parse deferred until Stage 3 chain-grades.
- **Top mechanism: Candidate 1 — compositional binding of intent-vec + role*slot-vec bundle over sharded per-role slot dictionaries.** Extends existing IntentClassifier + adds bind-unbind-cleanup for slot extraction per role.
- **P_CG = 0.55** (deflated from 0.75 initial per lit-scan calibration penalty; extension not novel synthesis, so 0.50 cap doesn't apply; STRIPS-bit-identical this session tilts P upward).
- **Composition:** M1.9 sits at the FRONT of Cortex.forward() before M1.3 noise + M1.6/M1.5 retrieval. `parse_hd` becomes a stronger retrieval query than raw input_hd because roles are explicit.
- **Cell anchor:** `substrate_semantic_parser_intent_slot_extraction_v1` with 5 arms including SHUFFLED_ROLE_KEYS sanity control + INTENT_ONLY cross-check; 3-seed smoke gate; HP intent ≥ 0.85 + slot-fill ≥ 0.80; sharded storage per role.
- **Follow-ons filed:**
  - M1.9 v2: recursive parser (Candidate 4) for compound queries — novel synthesis, P capped 0.50.
  - M1.9 Stage 4: real-language parse with open-vocab + treebank SRL discriminator — deferred until Stage 3 v1 CG.
  - Cortex.forward() patch to accept optional `token_sequence` and invoke M1.9 — backwards-compat default.

**Dispatch decision:** author the Stage 3 v1 cell next; hand off to hdi_exp_dev for cell authoring + pre-reg + smoke gate. Do NOT ship until substrate-KB concept-query re-run + Skunkworks SCHEMA-VET on the pre-reg.
