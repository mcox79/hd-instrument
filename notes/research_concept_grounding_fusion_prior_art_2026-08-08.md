# Research: prior art for fusing/densifying concept groundings from sparse KGs — bind/bundle vs the field

**Filed-by:** research sub-agent, 2026-08-08. Report-only, no code. 4 parallel Sonnet lit-scan
sub-agents dispatched (retrofitting/fusion; KG-embeddings-vs-PPMI; label-propagation/spreading-
activation/hop-featurization; VSA/HDC-native KG grounding), synthesized here.

## (a) HEADLINE

**The typed VSA bundle-of-relations is the right call, and it already has a close, verified
precedent (Cohen et al. 2012, Predication-based Semantic Indexing / PSI, applied to a real sparse
growing biomedical KG) — but the CURRENT bare 1-hop bundle is missing two literature-backed,
glass-box upgrades that directly target the sparsity problem: (1) hop expansion must be
DECAY-WEIGHTED (Katz-index / random-walk-with-restart style), not flat, because unweighted 2-hop
expansion on near-degree-1 graphs is exactly the regime the oversmoothing/noise-dilution
literature warns will backfire; (2) multi-source fusion (ConceptNet + WordNet + FrameNet/VerbNet +
Wikidata + text) should be done by encoding every source into the SAME base hyperdimensional
space with an explicit provenance-role bind and a retrofitting-style per-source weight, not by
training separate embeddings per source and geometrically re-aligning them (ConceptNet
Numberbatz's hardest step, which has no bind/bundle analog and would reintroduce opacity). No
verified method in KG-embedding literature (TransE/DistMult/ComplEx/RESCAL/HolE) beats bind/bundle
on BOTH glass-box-ness and the sparse-graph regime specifically — those methods are opaque AND
have a documented cold-start/low-degree weakness of their own, so switching families would trade
away the invariant without buying fixed-point accuracy.**

## (b) Cheap decisive test

Two small ablation experiments on the EXISTING held-out WordNet-supersense-from-ConceptNet-features
harness (same MDL learner, same held-out split, same gates), changing only the featurization step:

**Test 1 — decay-weighted vs flat hop expansion.** Build three concept-feature variants for the
same concept set: (i) 1-hop-only bundle (current baseline), (ii) flat 2-hop bundle (all 2-hop
neighbors added with equal weight — the naive densification currently being tried), (iii)
decay-weighted 2-hop bundle (2-hop neighbor contribution scaled by a fixed decay factor,
e.g. Katz-style beta in [0.3, 0.5], or restart-probability alpha in a random-walk-with-restart
framing — pick ONE fixed principled scheme, not tuned per-concept). Run all three through the
unchanged MDL learner + held-out gate.

**Test 2 — multi-source shared-space fusion with source-ablation control.** Add WordNet
hypernym/hyponym/meronym edges (already on disk, nltk) as a second bundled source into the SAME
base space as the ConceptNet edges, with an explicit provenance-role bind (`bind(source_id,
relation_edge)`) so the WordNet contribution can be switched off. Compare: (i) ConceptNet-only
(baseline), (ii) ConceptNet+WordNet fused, (iii) ConceptNet+WordNet-fused-then-WordNet-ablated
(same pipeline, WordNet term zeroed at eval time — this is the falsification control: if removing
WordNet does NOT drop accuracy back toward baseline, the "improvement" from (ii) was noise-
tolerance/extra-capacity, not real signal from the second source).

Both tests reuse the existing eval harness end to end; only the featurization function changes.
No new infrastructure, no external network calls, no LLM.

## (c) Falsifiable predictions (HARD-PASS / HARD-FAIL)

**HARD-PASS (both required to call the fusion program validated):**
- Decay-weighted 2-hop beats flat-2-hop by a non-trivial margin (>= 2 percentage points held-out
  accuracy) AND beats 1-hop-only baseline by >= 15% relative (i.e., clears roughly 0.184 -> >=
  0.211 on the same held-out metric the current baseline was measured on), with the
  train/held-out generalization gap not worse than the current 1-hop baseline's gap.
- ConceptNet+WordNet fusion beats ConceptNet-only by a non-trivial margin AND the WordNet-ablation
  control drops back toward the ConceptNet-only baseline (confirming the gain was real
  cross-source signal, not free capacity).

**HARD-FAIL (either triggers a real negative, not a "needs more tuning" excuse):**
- Decay-weighted 2-hop performs no better than flat 2-hop (within noise) — this would mean
  hop-COUNT was never the lever and the problem is graph COVERAGE (too few edges exist at any
  hop-distance), not edge-WEIGHTING; the fix would shift to graph acquisition (pull the full 34M-
  edge ConceptNet, not weighting tricks on the 100k slice).
- ConceptNet+WordNet fusion does not beat ConceptNet-only, OR the WordNet-ablation control shows
  NO drop when WordNet is zeroed out (both outcomes mean the fusion mechanism itself isn't the
  active ingredient — the bottleneck is source-independent, most likely graph density again).

Per lit-scan calibration discipline: this is a novel synthesis of independently-verified but
never-jointly-tested techniques for this exact substrate — P is capped at 0.50 and deflated a
further 0.15-0.25 for zero direct empirical precedent on THIS codebase. **P_deflated ≈ 0.30** that
Test 1 clears HARD-PASS; **P_deflated ≈ 0.25** that Test 2 clears HARD-PASS (multi-source fusion
is the less-precedented of the two — no verified paper does source-provenance-weighted VSA fusion
at all, so this is closer to unexplored territory than Test 1, which has PSI + PPNP/GDC as direct
precedent).

## Ranked prior-art table (elegance x glass-box x fit-to-substrate x addresses-sparsity)

| Rank | Mechanism | Core citation(s) | Glass-box? | Addresses sparsity? | Fit to bind/bundle substrate |
|---|---|---|---|---|---|
| 1 | **Random-Indexing-style incremental bind+bundle directly on KG triples** | Cohen et al., *J. Biomed. Informatics* 2012 (PSI, on SemMedDB — real sparse growing KG); Kanerva, Kristoferson & Holst, CogSci 2000 (Random Indexing origin) | Yes — fixed algebra, no gradient training, incremental | Partially — incremental/self-extending by construction, but does not itself solve neighbor-sparsity; needs pairing with #2 | **This IS effectively what we're already doing** — closest true precedent confirms the approach, not a pivot |
| 2 | **Decay-weighted multi-hop expansion (RWR / Katz / spreading-activation decay) in place of flat k-hop** | Haveliwala, WWW 2002 (topic-sensitive PageRank); Tong, Faloutsos & Pan, ICDM 2006 (fast RWR); Klicpera et al., ICLR 2019 (PPNP/APPNP) and NeurIPS 2019 (GDC) — both explicitly show raw k-hop is "noisy and arbitrarily defined" vs. principled diffusion; Collins & Loftus, *Psych. Review* 1975 (decay-weighted spreading activation, the cognitive-science origin of this exact idea) | Yes — closed-form, single interpretable decay hyperparameter | Directly — this is the literature-endorsed fix for exactly "how far to densify a sparse graph" | Bundle coefficient = decay weight; drop-in replacement for the currently-untested flat-2-hop scheme |
| 3 | **Retrofitting-as-bundle for multi-source fusion (shared base space, per-source weight, no geometric re-alignment)** | Faruqui et al., NAACL 2015 (retrofitting: Jacobi-iteration weighted average = literally a bundle operation); Speer, Chin & Havasi, AAAI 2017 (ConceptNet Numberbatch — shows what NOT to copy: the SVD/Procrustes alignment step for merging independently-trained spaces has no bundle analog) | Yes for the retrofitting core; the thing to AVOID (embedding-space alignment) is opaque | Indirectly — more sources = more signal per sparse node, if fused without drowning any one source | Numberbatch's weighting principle (explicit alpha/beta per source) re-expressed as a bundle coefficient; avoid its SVD-alignment step entirely by keeping all sources in one shared space from the start |
| 4 | **Resonator-network cleanup as an auditable read-out over the densified/fused bundle** | Frady, Kleyko & Sommer, *Neural Computation* 2020 (Resonator Networks I & II) | Yes — fixed algebra, iterative search-in-superposition, no training | N/A (an auditability add-on, not a densification fix) | Gives a concrete "which neighbor-relations actually drove this category inference" trace — strengthens the auditability edge already validated as the project's real differentiator |
| 5 | **Raw PPMI / count-based vectors over KG random walks, stopped before SVD factorization** | Qiu et al., WSDM 2018 (NetMF — proves DeepWalk/node2vec implicitly factorize a PPMI matrix; you can keep the raw sparse PPMI matrix instead of factorizing it) | Yes | Weak — PPMI counts from short walks on a ~1-edge/node graph are themselves sparse and noisy; the field moved to factorization specifically because raw counts don't generalize past observed pairs | Compatible in spirit (count-based, no gradient training) but doesn't add anything bind/bundle doesn't already give; not worth adopting as a separate mechanism |
| 6 (do not adopt) | **Gradient-trained dense KG embeddings** | TransE (Bordes et al., NeurIPS 2013); DistMult (Yang et al., ICLR 2015); ComplEx (Trouillon et al., ICML 2016); RESCAL (Nickel, Tresp & Kriegel, ICML 2011); HolE (Nickel, Rosasco & Poggio, AAAI 2016 — uses circular correlation, the same operator family as Plate's HRR unbind, but on gradient-trained/opaque vectors) | **No** — all are opaque, gradient-trained latent parameters, violates the no-LLM/glass-box invariant's spirit even though they're not LLMs | **No better, arguably worse** — all five have documented cold-start/low-degree weaknesses; sparsity hurts them too, and they have no mechanism to compensate for it except more training data (which the substrate doesn't have either) | Would require abandoning the inspectability invariant to get a family that ALSO doesn't solve sparsity — no case for adoption |

**Direct answer to the user's question:** a typed VSA bundle of multi-source relations is the
right call — the field does NOT have a clearly better glass-box option for the sparse-KG grounding
problem. The nearest true precedent (PSI/Random Indexing on a real sparse biomedical KG) uses
essentially the same approach already. The two concrete upgrades this drill surfaces
(decay-weighted hop expansion; shared-space provenance-weighted source fusion) are both
independently well-precedented — just never jointly applied to this exact combination
(multi-relational sparse KG + VSA-native concept grounding + self-extending loop) before. That
combination is a genuine, fillable gap, not a reinvention and not something the field has already
solved better elsewhere.

## (d) Cross-thread synthesis

This drill connects three previously-separate threads in the project's history:
- The **"grounding wall decomposes"** finding (2026-08-08, `notes/tonight_plan_three_ways_over_
  the_grounding_wall_2026-08-08.md`) established that word-level grounding is tractable and the
  goal<->outcome RELATION is the harder residual — this drill is squarely inside the tractable
  half (concept-category grounding from KG features), so it should NOT be read as addressing the
  relational residual; it strengthens the foundation the relational work sits on top of.
- The **auditability/correctability edge** validated as the project's real product differentiator
  (per the DesireDB reckoning, `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md` top block)
  is directly served by resonator-network cleanup (#4 in the ranked table) — it gives a concrete
  mechanism for "show me which relation-edges drove this inference," which is exactly the
  inspectability claim the project is now leaning on over raw accuracy.
- **HolE (Nickel, Rosasco & Poggio 2016)** is the single most on-point "almost us" paper in the
  entire scan: it uses the literal HRR circular-correlation operator (Plate 1995 — the origin of
  this project's bind/bundle algebra) as a KG scoring function, but trains the vectors by gradient
  descent instead of assigning/counting them. That is precisely the gap between "VSA-flavored" and
  "VSA-native," and it is worth naming explicitly in any external framing of this work: the field
  has come close to the substrate's approach via a completely different route (KG-embedding
  research borrowing an HRR operator) without ever converging on the substrate's actual
  combination (fixed algebra + no gradient training + multi-source + self-extending).

## (e) Substrate-product implications

If Test 1 and/or Test 2 clear HARD-PASS, the concrete product deliverable is a **concept-grounding
densification pass** that plugs into the existing self-extending KB pipeline: given the current
100k-edge ConceptNet slice, it increases usable signal per concept (from ~1.25 raw edges to a
decay-weighted, multi-source, provenance-tagged feature bundle) without adding a single opaque
parameter or external inference call — the entire pipeline stays inspectable end-to-end, which is
the load-bearing invariant. This is the concrete mechanism behind the "modern-lexicon-rebuild /
deep-grounding" fork already floated as a strategic option (fork ii in the pending reckoning
decision) — this note turns that fork from a vague direction into two cheap, falsifiable
experiments that can run before committing to the larger rebuild. If BOTH tests HARD-FAIL, that is
also a real, useful product signal: it would mean the 100k-slice's sparsity is a genuine coverage
ceiling that no weighting/fusion scheme can route around, and the honest next step is acquiring
more of the full 34M-edge ConceptNet (a data-acquisition decision, not a mechanism decision) —
this note's HARD-FAIL bands are written so that outcome is legible rather than something a future
session has to re-diagnose from scratch.

## (f) Citations (verified count)

**28 distinct citations verified** (author/venue/year confirmed against a primary source, DBLP,
ACM, arXiv, or the publisher record) across the four sub-scans:

*Retrofitting/fusion:* Faruqui, Dodge, Jauhar, Dyer, Hovy & Smith (NAACL-HLT 2015); Speer, Chin &
Havasi (AAAI 2017, ConceptNet 5.5 / Numberbatch); Mrkšić et al. (NAACL-HLT 2016, Counter-fitting);
Mrkšić et al. (TACL 2017, Attract-Repel); Tissier, Gravier & Habrard (EMNLP 2017, Dict2vec);
Bartusiak et al. (arXiv 2016, WordNet2Vec) [journal-year detail UNVERIFIED].

*KG embeddings vs PPMI:* Bordes et al. (NeurIPS 2013, TransE); Yang et al. (ICLR 2015, DistMult);
Trouillon et al. (ICML 2016, ComplEx); Nickel, Tresp & Kriegel (ICML 2011, RESCAL); Nickel,
Rosasco & Poggio (AAAI 2016, HolE); Qiu et al. (WSDM 2018, NetMF); Abboud et al. (NeurIPS 2020,
BoxE); Murphy, Talukdar & Mitchell (COLING 2012, NNSE) [relevance as KG-specific UNVERIFIED — it's
a general distributional-semantics paper].

*Label propagation / spreading activation / hop-featurization:* Zhu & Ghahramani (CMU tech report
2002); Zhou, Bousquet, Lal, Weston & Schölkopf (NIPS 2003/2004, cited both ways in the literature);
Collins & Loftus (*Psychological Review* 1975); Anderson (*JVLVB* 1983); Haveliwala (WWW 2002);
Tong, Faloutsos & Pan (ICDM 2006); Liben-Nowell & Kleinberg (2007 survey, Katz/Adamic-Adar); Li,
Han & Wu (AAAI 2018, oversmoothing); Klicpera, Bojchevski & Günnemann (ICLR 2019, PPNP/APPNP);
Klicpera, Weißenberger & Günnemann (NeurIPS 2019, GDC).

*VSA/HDC-native:* Kanerva (*Cognitive Computation* 2009); Plate (*IEEE TNN* 1995, HRR); Kanerva,
Kristoferson & Holst (CogSci 2000, Random Indexing); Cohen et al. (*J. Biomed. Informatics* 2012,
PSI — closest true precedent, real sparse growing KG); Frady, Kleyko & Sommer (*Neural
Computation* 2020, Resonator Networks I & II — counted once); Schlegel, Neubert & Protzel
(*Artificial Intelligence Review* 2022, VSA comparison survey — does not cover KG applications);
Poduval et al. (*Frontiers in Neuroscience* 2022, GrapHD); Dalvi & Honavar (arXiv 2024/WSDM 2025,
HDGL).

**5 details flagged [UNVERIFIED]** (specific sub-claims, not whole citations): Faruqui et al.'s
exact author list (one name could not be confirmed); WordNet2Vec's journal-version year;
"retrofitting = low-pass graph filtering" as a *named* citation (the underlying math equivalence
is solid, verified via the Simplifying-GCN/low-pass-filter literature, but no paper titles
retrofitting that way explicitly); NNSE's relevance as KG-specific rather than general
distributional semantics; HDGL's and GrapHD's evaluation specifically on sparse multi-relational
graphs (both papers exist and are real, but sparsity-specific results were not independently
confirmed).

**Genuine gap confirmed (not just unfound):** no verified paper does explicit source-provenance
role-binding for down-weightable multi-source KG fusion within a VSA framework — this is the one
piece of the recommended mechanism (table rank 3, the provenance-bind half specifically) that
appears to be actually novel rather than merely under-searched.
