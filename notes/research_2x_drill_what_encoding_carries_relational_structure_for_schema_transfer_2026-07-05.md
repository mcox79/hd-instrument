# 2x drill: what encoding/mechanism carries learnable relational structure for schema transfer?

**Filed:** 2026-07-05 by research (Opus + 3 parallel Sonnet lit-scans)
**Trigger:** decisive landed HARD_FAIL, `schema_bundle_real_corpus_transfer_v1` (remote FULL,
verified off-disk at `data/session_local/skunkworks/remote_schema_bundle_real_corpus_transfer_v1_metrics.json`,
prereg `preregs/2026-07-05_schema_bundle_real_corpus_transfer_v1.md`).
**2x discipline:** operational drill on an existing negative, not a re-verification lit-scan.

## HEADLINE

The negative is real and the diagnosis in the pre-reg was correct as far as it went, but
incomplete: it is not simply "the encoding is orthographic/random instead of semantic." The
literature (3 independent angles, converging) says the bottleneck is that the schema-bundle
mechanism estimates its relation transform by **naive unweighted averaging over training
pairs with no discriminative/negative-sampled training signal** — a documented weak method
for one-to-many relations regardless of how good the underlying entity encoding is. The
substrate's OWN prior landed result (cap_map PP-275, `lap3_rotate_analogy_cpu_v1`, HARD_PASS,
Hits@1=0.899 using **learned** RotatE-style relation embeddings) already proves the fix works
when the relation transform is properly trained. FHRR bind (elementwise phasor multiply) is
mathematically a rotation — the same operator class as RotatE — so the substrate is not
missing the right algebra. It is missing the right ESTIMATOR for the relation transform.

**Verdict on the framing question:** semantic-encoding-alone is not expected to be
sufficient (Option 1, deflated); explicit/learned relational code is the supported direction
(Option 2), reinforced independently by brain evidence (Option 3). But there's a real added
wrinkle the pre-reg didn't separate out: `AtLocation` and `CausesDesire` are one-to-many
relations (a sofa can be in a house, room, or store) and averaging-based estimators are
*structurally* incapable of representing 1-to-N/N-to-1/N-to-N relations even with perfect
semantic content (this is a proven property of TransE, not folklore) — so part of the fix is
encoder-independent: it's an estimator-class problem, separate from whether entities are
encoded with BGE, char-trigrams, or random phasors.

## Verified off-disk (the negative, re-confirmed)

`metrics.json` (`run_mode=full`, `N=8192`, `V<=100`, 3 relations x 4 arms x 5 M x 3 seeds =
180/180 units, `cardinality_ok=true`, `arms_differ_verified=true`):

- `synth_positive_gain_mean = +0.780` (>> 0.15 gate) — mechanism reproduces cleanly on
  synthetic clustered structure. The algebra/cleanup pipeline is not broken.
- `AtLocation`: HARD_FAIL, real_gain=+0.032, real-shuf=+0.016, real-rand=+0.024 — genuinely
  at chance, no confound, no signal.
- `CausesDesire`: HARD_FAIL, real_gain=+0.059 but CONFOUND(shuffle-invariant) flagged in the
  gate diagnostics — most of the apparent signal survives object-label shuffling, meaning it
  reflects codebook/frequency structure, not subject-conditional binding.
- `DerivedFrom`: HARD_FAIL (labeled), real_acc=0.913 but real-minus-shuffled = +0.002 —
  CONFOUND(shuffle-invariant): the high raw number is a nearest-substring-object encoding
  artifact (char-trigram surface similarity finds the right-shaped object independent of
  which subject it's paired with), not schema transfer. This is exactly what the pre-reg
  predicted char-trigram *could* fake, and the shuffled control correctly caught it.

So: zero real relation shows genuine subject-conditional novel-entity transfer under the
current encoding + estimator, while the mechanism itself is proven live via the synthetic
positive control. This is a clean, well-instrumented negative — not a harness failure.

## Cross-thread synthesis: cap_map already contains the answer, half-built

Grepping `substrate_capability_map.md` surfaced a directly relevant prior HARD_PASS that the
pre-reg did not cross-reference:

- **PP-275** `lap3_rotate_analogy_cpu_v1` (v550, cycle 216): "FHRR-binding is mathematically
  equivalent to RotatE relation embeddings; proportional analogy (A:B::C:D) achieves
  Hits@1=0.899 at scale (1241 entities, 55 relations, 1393 test)... Mechanism: **learned**
  RotatE relation embeddings provide the relational codebook." This is the single most
  important prior data point: on the same substrate, with the same phasor-rotation binding
  primitive, relational transfer works extremely well **when the relation representation is
  actually trained/optimized**, not averaged.
- **PP-321** `d3_1_structural_alignment_sme_cpu_v1` (MIDDLE_BAND, small n): structural/
  relational retrieval beats surface-similarity retrieval by 14pp — independent confirmation
  that "structure" and "surface similarity" are different signals on this substrate, matching
  the lit-scan-1 finding below.
- **PP-254/282/284** (schema-layer prototype extraction, HARD_PASS at ceiling, 60->220->1000
  schemas): this is a *different* kind of "schema" — unary category-prototype extraction via
  bundle-centroid, not binary subject->object relational transfer. It does not bear on this
  question directly; flagging so it isn't conflated in future framing.
- **STRETCH4-2 / PP-303**: cross-domain analogical mapping is a separate, already-known
  negative. Not directly relevant here (this drill is same-domain, novel-subject), but a
  reminder that not all analogy directions have transferred cleanly even with learned
  transforms.

The failed cell essentially re-ran a **naive, untrained** version of what PP-275 already
proved works when trained. That's the actionable delta.

## Lit-scan angle 1 — linear relational analogy reliability (word2vec/GloVe/BGE-style)

3 sub-questions, MEDIUM/MEDIUM/LOW confidence respectively (deflated further below):

1. Vector-offset analogy ("king - man + woman = queen") is NOT uniformly reliable across
   relation types. Gladkova/Drozd/Matsuoka (BATS, NAACL-SRW 2016) and Rogers/Drozd/Li (*SEM
   2017) show large, systematic accuracy gaps by relation type. The real axis is
   **functional/near-deterministic vs. one-to-many/high-variance**, not "morphology vs.
   semantics" as commonly summarized — encyclopedic-but-functional relations (e.g.
   country-capital) score reasonably; lexicographic one-to-many relations (synonymy,
   hypernymy — structurally close to our `AtLocation`/`CausesDesire`) score poorly.
2. There is a real, structural (not just empirical) reason: Bordes et al. (TransE, NeurIPS
   2013) **prove** the additive/offset operator cannot represent 1-to-N, N-to-1, or N-to-N
   relations — averaging over many valid targets increases variance in the aggregate offset
   instead of collapsing to a clean answer. This directly explains why `AtLocation` (many
   valid locations per subject) is a harder ask than `DerivedFrom` (near-1-to-1 morphological
   function) independent of encoding quality.
3. Weakest-evidenced sub-question: no direct benchmark of analogy/relational-offset accuracy
   was found for modern contrastive sentence embeddings (BGE/SBERT/E5-style). The single most
   relevant hit, "Relational Schemata in BERT Are Inducible, Not Emergent" (arXiv:2506.11485,
   2026 preprint), found pretrained BERT has **no** linear/geometric organization by relation
   type (RSA rho ~= 0.04) — structure only appears (rho ~= 0.77) after supervised
   fine-tuning on the relation itself. This is a preprint and studies token/relation-probing
   representations, not retrieval-style sentence embeddings directly, so treat as suggestive,
   not confirmed, but it points the same direction as (1)+(2): pretrained semantic
   embeddings do not hand you relational geometry for free; fine-tuning/training on the
   relation is what produces it.

## Lit-scan angle 2 — KG embeddings vs semantic similarity

Converges cleanly: text/semantic embeddings alone are described across multiple independent
KG-completion papers (KG-BERT, Yao et al. 2019; "Structure-Augmented Text Representation
Learning," arXiv:2004.14781) as an auxiliary signal, never a substitute for a
structurally-trained relation representation — the entire "structure-augmented" sub-literature
exists because pure text/semantic scoring underperforms. RotatE (Sun et al. 2019,
arXiv:1902.10197) and TransE define relations as an **operator** (rotation / translation) whose
competence comes from being jointly optimized against real triples with negative sampling —
architecturally independent of entity semantic content (entities are typically randomly
initialized and jointly trained). Most directly relevant: One-Shot Relational Learning for
KGs (Xiong et al. 2018, arXiv:1808.09040) and the few-shot-KGE line explicitly motivate their
work because **naive one-shot/few-shot relation-transform estimation (simple averaging of
example pairs, no negative sampling) is known-weak, especially for complex/one-to-many
relations** — this is close to a direct description of exactly what
`schema_bundle_real_corpus_transfer_v1`'s `M_R = mean_i bind(B_i, inv(A_i))` estimator does.

Important nuance the lit-scan flagged as a gap: standard KGE benchmarks (TransE/RotatE/
FB15k-237, and by inference PP-275) are **transductive** — held-out triples, not held-out
*entities*; the entity still has other training triples. `schema_bundle_real_corpus_transfer_v1`
tested strictly **novel-subject** transfer (subject never seen at all), which is closer to
*inductive* KG completion (a harder, less mature sub-field: NodePiece, GraIL, text-based
inductive link prediction). This means PP-275's Hits@1=0.899 is encouraging precedent but not
a guarantee the same recipe transfers cleanly to the strictly-inductive setting this drill
cares about. Confidence on sub-answers: MEDIUM-HIGH / MEDIUM / MEDIUM-HIGH (frozen-random-
entity-only ablation not directly found, inferred from architecture).

## Lit-scan angle 3 — brain grounding

Strong, convergent: the Tolman-Eichenbaum Machine (Whittington et al. 2020, *Cell*) explicitly
factorizes an abstract **structural code** (entorhinal-like, learned across many
structurally-similar but content-different environments/graphs, generalizes to brand-new
graphs on first exposure) from a **content code** (sensory/item identity), bound via a
hippocampal-like conjunctive layer. The model's own internal contrast is the evidence: the
structural layer generalizes across environments; the conjunctive/content layer does not.
Independent corroboration: Constantinescu/O'Reilly/Behrens (*Science* 2016) grid-like codes
for abstract (non-spatial) conceptual spaces; Samborska/Butler/Walton/Behrens/Akam (*Nat.
Neurosci.* 2022) anatomically dissociates PFC (abstract task-structure, generalizes across
physically different problems) from hippocampal CA1 (remaps per-problem, content-specific).
Eichenbaum/Cohen relational-memory + transitive-inference lesion studies independently support
a dedicated relational-linkage mechanism distinct from item memory. No source found arguing a
rich content code alone suffices for novel-item relational transfer (absence-of-evidence,
confidence deflated to MEDIUM per calibration discipline rather than treated as proof).

This directly answers the "does biology hedge with a separate learned structural code"
question in the drill brief: **yes**, and the substrate's own PP-275 (learned RotatE-
equivalent transform) is an unwitting structural analog of exactly this factorization,
while the failed cell's naive-mean estimator is closer to "hoping the content code carries
it," which both the lit and the brain evidence say is the weaker bet.

## Cheap decisive test (single highest-EV next experiment)

**`schema_relation_transform_estimator_ablation_v1`** (proposed, not yet built): reuse the
EXACT data pipeline, entities, relations (`AtLocation`, `CausesDesire`, `DerivedFrom`), split
(novel-subject holdout), codebook (V<=100), and HP/HF band structure from
`schema_bundle_real_corpus_transfer_v1`. Cross TWO factors in a 2x2 (plus existing controls):

- **Estimator**: `NAIVE_MEAN` (current, `M_R = mean_i bind(B_i, inv(A_i))`, no negative
  sampling) vs. `TRAINED` (gradient/margin-optimized relation-rotation-angle vector, trained
  with negative sampling against the same V<=100 codebook — a bounded, CPU-cheap, off-the-
  shelf recipe; zero LLM calls preserved if entities stay char-trigram/random-phasor).
- **Encoding** (secondary, cheaper arm): keep `char-trigram`/`random-phasor` (zero-LLM, as
  now) vs. a bounded `BGE-reencode` probe of ONLY these ~100-object codebooks + train/test
  subject sets per relation (a few hundred entities total — NOT a full store re-encode).

This isolates whether the fix is (a) the estimator (predicted primary lever per lit-scans 1+2
and PP-275 precedent), (b) the encoding (predicted secondary/weaker lever per lit-scan 1's
finding that pretrained semantic embeddings don't hand you relational geometry for free), or
(c) neither — a genuine inductive-relational-transfer wall for one-to-many relations
regardless of estimator or encoding, which would be the honest bad-news outcome.

**Pre-registered HARD-PASS**: `TRAINED` estimator clears `gain(ARM_REAL) >= 0.2075` (same band
as the parent cell) on `AtLocation` OR `CausesDesire` (the genuinely semantic, non-confounded
relations) at held-out novel subjects, with `gain(ARM_SHUFFLED) <= 0.05` (rules out the
DerivedFrom-style confound recurring).

**Pre-registered HARD-FAIL**: `TRAINED` estimator on char-trigram/random-phasor encoding still
`<= 0.05` gain on both `AtLocation` and `CausesDesire` at M_OP — this would mean the estimator
fix alone is insufficient and the inductive setting (truly novel entities, no lookup table) is
the binding constraint, redirecting the program toward inductive-relational-embedding methods
(entity-feature-based scoring, e.g. text-description-conditioned relation scoring) rather than
a bigger training budget.

**Bounded probe, not a HELD full-store re-encode.** Same tiny V<=100-per-relation codebook,
same handful of relations, CPU-only, restartable, does not touch the production KG store's
actual entity encoding. The optional `BGE-reencode` secondary arm is likewise scoped to only
the codebooks under test (a few hundred embeddings), not a store-wide re-encode.

## Substrate-product implications

If `TRAINED` estimator clears HARD-PASS: schema/relational transfer becomes a genuinely
buildable feature for the "turn stored facts into transferable knowledge" goal, with a known,
cheap recipe (train a small per-relation rotation via negative sampling — no new algebra
needed since FHRR bind already IS the RotatE operator class; PP-275 is the existence proof).
This would let a user ask the substrate for a NEW fact about a relation type it has many
examples of but has never seen for this specific entity, and get a correct-in-expectation
prediction rather than chance — a distinctive continual-learning capability most LLM-adjacent
systems handle only via retrieval, not native algebra.

If HARD-FAIL: honest reading is that "one-shot/few-shot schema transfer to a truly unseen
entity" is a harder, less-mature problem across the whole field (inductive KG embedding is a
known-hard, actively-researched sub-area, not a solved one) — the substrate would not be
behind the field here, but the product claim needs to shrink from "any relation, any novel
entity" to "relations with enough training density AND some entity-level compositional
signal" (closer to `DerivedFrom`'s morphological case, once its confound is separately fixed).

## Honest rating: how hard is real schema-transfer

MEDIOCRE-to-BAD as currently attempted (naive averaging on non-compositional/random
encodings), but the negative is diagnostic, not fundamental — no proof-of-impossibility was
found in either the KG-embedding or brain-grounding literature. The single most load-bearing
piece of evidence that this is fixable is internal, not external: PP-275 already reproduces
strong relational transfer on this exact substrate's own algebra, using a properly trained
relation transform. The honest gap is: that prior success was (likely) transductive, this
drill's failure was strictly inductive (novel-subject), and inductive relational embedding is
a genuinely harder open problem field-wide — so P(HARD-PASS on the proposed next cell) is
capped, not assumed high.

## Falsifiable predictions (calibration-penalized)

- P(TRAINED estimator alone clears HARD-PASS on >=1 real relation, novel-subject) = 0.35
  (deflated from a naive ~0.55 given PP-275 precedent, penalized -0.20 for the
  transductive-vs-inductive gap the lit-scan flagged).
- P(BGE-reencode secondary arm alone, naive-mean estimator unchanged, clears HARD-PASS) = 0.15
  (capped low; lit-scan 1 found no evidence pretrained semantic embeddings hand you linear
  relational geometry for free, and the one-to-many relations are structurally resistant to
  averaging regardless of encoding).
- P(both estimator-fix AND encoding-fix needed jointly) = 0.30.
- P(genuine inductive-relational-transfer wall; HARD-FAIL under all combinations) = 0.20 —
  a real, non-zero possibility that should not be dismissed given the field-wide difficulty of
  inductive KGE; if this lands, it is a valuable, well-instrumented negative, not wasted work.

P_deflated (headline claim: "needs explicit/learned relational code, not semantic encoding
alone") = **0.45** (novel-synthesis cap 0.50 applies; deflated further for the uncontested
absence of a direct sentence-embedding analogy benchmark in lit-scan 1 and the inductive-vs-
transductive gap in lit-scan 2).

## Citations (verified count: 15)

Word-embedding analogy (lit-scan 1, 8 sources, 2 flagged low-confidence extraction):
Linzen 2016 (arXiv:1606.07736); Rogers/Drozd/Li *SEM 2017 (ACL Anthology S17-1017);
Gladkova/Drozd/Matsuoka NAACL-SRW 2016 (BATS); Ethayarajh/Duvenaud/Hirst ACL 2019
(arXiv:1810.04882); Allen/Hospedales ICML 2019 (arXiv:1901.09813); Bordes et al. NeurIPS 2013
(TransE); "Relational Schemata in BERT Are Inducible, Not Emergent" (arXiv:2506.11485); Gao et
al. EMNLP 2021 (SimCSE, arXiv:2104.08821).

KG-embedding (lit-scan 2, 7 sources): Sun et al. 2019 (RotatE, arXiv:1902.10197); Trouillon et
al. 2016 (ComplEx, arXiv:1606.06357); Bordes et al. 2013 (TransE); Yao et al. 2019 (KG-BERT);
"Structure-Augmented Text Representation Learning" (arXiv:2004.14781); Xiong et al. 2018
(arXiv:1808.09040); Drozd/Gladkova/Matsuoka COLING 2016.

Brain grounding (lit-scan 3, 5 sources): Whittington et al. 2020 *Cell* (TEM); Behrens et al.
2018 *Neuron* ("What Is a Cognitive Map?"); Samborska et al. 2022 *Nat. Neurosci.*;
Constantinescu/O'Reilly/Behrens 2016 *Science*; Eichenbaum/Cohen relational-memory + transitive-
inference lesion literature.

(Overlap: Bordes 2013 counted once toward the 15 verified-distinct total.)
