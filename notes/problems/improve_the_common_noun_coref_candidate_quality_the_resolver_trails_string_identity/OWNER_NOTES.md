---
owner_verdict: DONE
---

SUBMISSION -- improve_the_common_noun_coref_candidate_quality_the_resolver_trails_string_identity
status: SOLVED (WIP until owner_verdict: DONE). Glass-box, NO external LLM at inference. NO hdlab/ written
(Q111 -- four proposed wires + reference impl provided). Wrote only experiments/, verification/,
notes/problems/<slug>/. Ledger --check clean (malformed 0). Reuses the LANDED hdlab.typed_spokes organ + GUM (modern gold).

REVERIFY (6 witness suites, 28 checks; the first is the headline WIN):
  .venv/Scripts/python.exe verification/test_commonnoun_typed_identity.py            # 9/9 WIN + optimality/mechanism/merge-view
  .venv/Scripts/python.exe verification/test_commonnoun_candidate_diagnostic.py      # 4/4 reproduces the defect + localizes it
  .venv/Scripts/python.exe verification/test_commonnoun_lever_ceilings.py            # 3/3 splitting/bridging capped
  .venv/Scripts/python.exe verification/test_commonnoun_metric_audit.py              # 3/3 string-identity strong on CoNLL too (not a metric artifact)
  .venv/Scripts/python.exe verification/test_commonnoun_recallsafe_bridge_resolver.py# 6/6 naive levers fail (the wall)
  .venv/Scripts/python.exe verification/test_commonnoun_diffhead_anatomy.py          # 3/3 residual is 84% world-knowledge

HEADLINE. On the board's OWN common_noun_coref instrument (URG resolver, modern GUM TEST, n=2855 anaphoric
common-noun mentions), a brain-foundational candidate-generation + identity-representation upgrade scores
0.5671 vs same-head string-identity 0.5412 -- +0.0259 CI[+0.0134,+0.0385] CI-SEPARATED -- and vs the live
incumbent 0.4879, +0.0792. Info-free twin LOSES CI-sep; pronoun/kb byte-identical (+0.0000); name +0.0241.
LADDER: incumbent 0.4879 -> typed-view 0.5317 -> string-identity 0.5412 -> WIN 0.5671 -> gold-cluster oracle 0.5825.

WHAT WON (the owner's "understand why it failed" push is what unearthed it -- each lever came from a diagnosis):
 1. TYPED CARD IDENTITY. The incumbent trailed string-identity because ~47%-accurate pronoun resolution POLLUTES the
    shared DRT card. Fix: score common-noun coref on the referent's NOMINAL identity (name+common), pronouns keep
    reading the full card -> +0.0439 over incumbent CI-sep, pronoun byte-identical. Brain-faithful (Ariel: identity is
    descriptive, pronouns are transient pointers).
 2. NON-WRITING (Nref) DIFFERENT-HEAD BRIDGE. A definite with no same-head antecedent resolves to the most-salient
    TYPE-compatible antecedent for THIS reference but does NOT commit the merge. +0.0354 over the typed base; carries
    the beat. Brain-faithful (Nieuwland hold-under-uncertainty). PROVEN necessary: committing corrupts the same-head
    chain (same-head 0.769->0.694, bridge items unchanged) because it writes the bridged head into the target.
 3. TYPED-SPOKES SEED (fidelity). Seed the bridge from the LANDED hdlab.typed_spokes.coref_type_license (sense-resolved
    synonym + is-a both dirs + part-whole; Lambon-Ralph) instead of crude WordNet-MFS: +0.0053 CI-sep, more
    brain-foundational, REUSES the organ. NOTE: same organ the brief flagged net-negative AS A WRITING FILTER -- here
    it is a NON-writing candidate seed, which is why it is net-POSITIVE (the write was the cost, confirmed).
 4. CONSUMER-SPECIFIC MERGE VIEW (prototyped, additive/read-only). A third card view (kb_eids) exposes the bridge's
    common->named-entity resolution to the entity-KB consumer ("the company"->Google) -> +0.034 from a 0.000 floor,
    common/pronoun byte-unchanged, pollution-free. Scales with the P31 KB.

CONTROLS. Info-free twin (bridge fires but to a RANDOM antecedent -> type signal destroyed) LOSES CI-sep (+0.0273);
write-vs-nowrite ablation isolates the pollution mechanism; graded commit-gate + soft binding + selector sweep all
REGRESS or WASH (design is optimal, not a compromise); no-regress on pronoun/kb (byte-identical) + name (improves);
gold-cluster oracle 0.5825 + metric audit (string-identity strong on CoNLL too) bound the headroom.

EFFICIENCY. Memoize the type comparator (symmetric key, pure) -> full-test bridge 3.41s -> 0.48s (~7x); the
25,398-pair type-compatibility closure can be PRECOMPUTED OFFLINE as a static asset -> zero inference-time WordNet.
Cascade (same-head first, then type-bridge) == weighted parallel CS with head-match as the dominant cue (Ariel) --
the efficient AND faithful form (same-head override was measured net-negative).

PROPOSED hdlab WIRES (Q111 -- reference impl: experiments/exp_commonnoun_typed_identity_gum_v1.TypedResolver
(binding='incumbent', bridge=True, bridge_write=False, type_comparator='typed_spokes')): the four levers above,
one coherent additive change to the URG common-noun path; heads default byte-identical where off.

BRAIN-FIDELITY SCAN. All computations now faithful (typed identity/Ariel; content-addressable retrieval/L&V;
ACT-R salience; typed-spokes; Nref hold). Remaining not-fully-faithful items are ALL upstream/adjacent and proven
harmless or out-of-scope: (a) hard-gn same-head filter -- an OUR-INVENTION proxy kept for pronoun no-regress,
MEASURED a wash (gender ~6%-sparse), soft version regresses pronoun; (b) gold mention detection -- a measurement
choice, deployed NP-head chunker is a separate organ; (c) pronoun resolution ~47% -- sibling brief, and the typed
view already makes common-noun ROBUST to it.

HIGH-PRIORITY NEXT STEPS:
 * HIGH -- LAND the four wires + the type-comparator memo (0.4879->0.5671, beats string-identity CI-sep, twin loses,
   no consumer regress; re-verify the 6 suites).
 * HIGH -- the ONLY remaining accuracy lever is world-knowledge content: the sibling P31 entity-type-KB (ranking has
   ZERO glass-box headroom -- proven; content is the entire signal). Closes the rest of the headroom to oracle 0.5825
   and raises the merge-view yield above the 43% glass-box bridge precision.
 * MEDIUM -- evaluate the OTHER card consumers (affect experiencer, goal/relational binding) on the typed identity
   view (they read the polluted full card; the nominal view likely lifts them like it lifted name coref +0.024).
 * MEDIUM -- complementary upstream: the sibling compose SOLVED's pronoun stack (+0.082) cleans the full-card read.

KEY REALIZATIONS: (1) a failure understood at the mechanism level hands you the fix -- de-pollution regressed pronoun
because one field served two consumers (->typed view); the bridge netted zero because the WRITE polluted others, not
the resolution (->Nref hold). (2) Separate the resolution decision from the merge commitment -- the board + downstream
need each mention RESOLVED, not permanently MERGED. (3) the entity's identity is nominal, not pronominal. (4) the
info-free twin tells you WHERE the signal is: same-head twin ties (ranking has no headroom); different-head twin loses
(the type signal is the lever) -- so the only path higher is richer world-knowledge content, not ranking.

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT.md sec 2b, E3): common-noun coref now BEATS same-head string-identity on
modern GUM (0.5671 vs 0.5412, CI-sep) via a typed card identity + a non-writing typed-spokes bridge; the prior
"resolver trails string-identity" note is superseded for this dim; the shared-card antagonism is resolved for the
common-noun consumer by the typed view (not by un-unifying); confirms E3's "weighted parallel CS, not filter-then-rank".

DO NOT: chase cluster-F1 by committing bridges (corrupts the same-head chain); use a WRITING type-license filter
(net-negative -- use non-writing); re-tune ranking/agreement/selector (measured washes); split same-head (net-negative
on both metrics); use an external LLM; lean on 19c gold.

TLDR (plain English): our reader was worse than a dumb same-word rule at re-recognising common nouns. Understanding
WHY the obvious fixes failed handed us the fix: give each character record a clean "name/noun identity" separate from
its (only ~half-right) pronoun history, and resolve different-worded mentions ("the company"->Google) for the sentence
without permanently merging them when unsure. Together these brain-faithful changes make the reader BEAT the dumb rule
(a clean statistically-separated margin), a scrambled version falls apart, pronoun/name tracking is untouched, and a
new "fact-tracker view" lets downstream see "the company = Google" for free. I also made it ~7x faster and swapped the
one crude piece for the substrate's proper meaning organ. The only path higher is real world-knowledge (the planned
offline fact store); every ranking knob is proven to have no headroom.

QUESTIONS: none blocking. One scope note: the win is per-mention RESOLUTION accuracy (the board's dim + what
downstream binding needs), not clustering-F1 -- the "hold the merge" step trades cluster shape for resolution
correctness; committing to chase F1 reintroduces the pollution. Recommend keeping the resolution-accuracy win.
