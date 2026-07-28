# Research: engineering resources for the event-plausibility web -- adoptable glass-box foundation (2026-07-20)

Director synthesis of a 3-axis prior-art scan (role-lexicons/thematic-fit; commonsense-event-KBs + the COMET glass-box question; narrative-scripts + fair corpus-density tooling). This is the ENGINEERING-side complement to the brain-side drill (notes/research_brain_building_event_plausibility_web_2026-07-20.md). All resources CREDITED for adopt/build-on, never "steal". P estimates deflated per lit-scan-calibration; every license flag + unverified item from the scans is preserved below.

## HEADLINE

The event-plausibility web our reader is missing has a large, mature, LICENSE-CLEAN, INSPECTABLE (glass-box-safe) engineering-resource base -- it is ENGINEERING RECOMBINATION, not novel research, to adopt it. Three payoffs: (1) a ready LOOKUP RESOURCE for the active-learning loop now building; (2) a clean answer to the COMET glass-box question (usage-mode dependent); (3) a concrete, FAIR, HIGH-POWERED, and NOVEL outcome-dense-corpus recipe that fixes the underpowered density probe (which was ~9K background tokens/arm, n_multi=21, SE~0.108 = genuinely uninformative, NOT a refutation of the reporting-bias hypothesis).

## (1) ADOPTABLE RESOURCES, by function

### Structural role layer (explicit agent-vs-patient / affectedness) -- all static, glass-box-safe
- **PropBank** (Palmer/Gildea/Kingsbury 2005) -- cleanest, most consistent binary signal: Arg0=proto-agent, Arg1=proto-patient/theme; ~1M words WSJ/OntoNotes. Frame files OPEN on GitHub (propbank/propbank-release); **two-tier license caveat: the underlying Penn-Treebank/OntoNotes TEXT is LDC-restricted -- the annotation/frame files may be usable without the text (re-verify against repo README).**
- **VerbNet** (UColorado) -- most EXPLICIT per-class thematic-role declaration (Patient/Theme) + semantic selectional restrictions; 237 top classes/~5,000 senses; XML. UColorado license bundled (described permissive; exact terms not verified).
- **SemLink** (cu-clear/semlink) -- the load-bearing GLUE: maps VerbNet<->PropBank<->FrameNet<->OntoNotes<->WordNet (pb-vn2.json, vn-fn2.json). Lets us unify PropBank's clean Arg0/Arg1 + VerbNet's explicit Patient/Theme into ONE per-verb-sense role lookup instead of reconciling three role vocabularies by hand. Static JSON.
- **FrameNet** (Berkeley/ICSI) -- richer frame-specific roles (Patient/Undergoer/Entity vary by frame); ~1,200+ frames; "expanded licensing" (academic+commercial per 2005 ICSI note; verify current terms). Heterogeneous role vocab complicates a uniform affected-argument signal.

### Human graded-plausibility norms (the affectedness ground-truth we LACK -- yardstick, not bulk)
- **McRae/Ferretti** (McRae/Spivey-Knowlton/Tanenhaus 1998; Ferretti/McRae/Hatherell 2001) -- verb+agent/patient/instrument/location typicality ratings (~1-7). Directly the affectedness signal. SMALL (dozens-to-~100 verbs). **No confirmed machine-readable CSV located (only paper-appendix PDFs); may need manual transcription / author contact.**
- **DTFit** (Vassallo/Chersoni/Santus/Lenci/Blache 2018) -- 395 crowdsourced patient-typicality items, denser than McRae within its narrow scope. **Hosting/license not confirmed; DO NOT conflate with the separate esantus/Thematic_Fit repo (Santus et al. EMNLP 2017 code+data, a different resource).**
- **Baroni & Lenci Distributional Memory** (2010) -- static word-link-word tensor (TypeDM downloadable ~4GB from marcobaroni.org/dm/); INDIRECT (compute similarity, doesn't label roles); permissive-implied, license text not found.

### Commonsense event/outcome KBs (the reporting-bias-FILLING content) -- ranked density x license x glass-box
1. **ATOMIC-2020 / COMET-ATOMIC-2020** (Hwang et al. 2021) -- 1.33M tuples, 23 relations in THREE first-class categories incl. physical-entity commonsense (not incidental). **CC-BY, static downloadable file independent of any model.** TOP PICK for the outcome/affectedness lookup.
2. **ATOMIC** (Sap et al. 2019) -- ~877K if-then triples, 9 relations (x=agent, o=other/affected); CC-BY, static. Ranks just below 2020 on physical-outcome density.
3. **Knowlywood** (Tandon et al. 2015) -- rich typical-participant/duration/location event frames (~965K activities) from movie/TV/novel scenes = directly "who is affected, how, where, how long"; noisy pipeline (~80% acc). **License UNVERIFIED (no CC/Apache marking located) -- flag before use; the reason it isn't ranked higher.**
- **ProPara** (Dalvi et al. 2018) -- 488 procedural paragraphs, ~81K explicit create/move/destroy state-change annotations = direct affectedness tracking, but narrow (procedural/science). Apache-2.0 (dataset file format unverified). Close alternate #3 if clean-license weighted over Knowlywood's content.
- **GLUCOSE** (Mostafazadeh et al. 2020) -- ~670K story-grounded causal statements + generalized rules, 10 dimensions incl. state-change. **CC-BY-NC (non-commercial) caveat.**
- **ConceptNet** (Speer et al.) -- large (~1.6M) but SPARSE for event-outcome/affectedness (ATOMIC paper: 0-7% relation overlap on effect/want/need/react); mostly taxonomic. CC-BY-SA (share-alike constrains derived corpora).
- **PIQA** (Bisk et al. 2020) -- physical-commonsense binary QA; NOT a fact-KB (eval/training signal only). Notable: the paper itself DIAGNOSES reporting bias as the cause of the human-77%/model-95% gap = independent support for our reporting-bias hypothesis. AFL-3.0.

## (2) THE COMET GLASS-BOX LINE (the load-bearing call) -- USAGE-MODE DEPENDENT
COMET (Bosselut et al. 2019) is a Transformer that GENERATES ATOMIC/ConceptNet-style tuples on demand. Verdict splits by usage:
- **Offline KG-expansion (run once over seed events, beam-search, dump to a flat file):** produces a static, inspectable KB dump identical in kind to ATOMIC-2020 itself (indeed ATOMIC-2020 was built partly this way). **GLASS-BOX-LEGAL foundation scaffolding -- a build-time tool, not a runtime dependency.**
- **Live/online query (call COMET per input at inference):** an opaque neural runtime dependency, no different from calling any generative LM live. **VIOLATES the no-runtime-LLM glass-box invariant -- forbidden.**
Code Apache-2.0; weights separate. RULE: COMET only ever in offline-dump mode; the dumped KB is what the substrate ingests/looks-up.

## (3) FAIR, HIGH-POWERED, NOVEL outcome-dense-corpus recipe (fixes the density probe)
Prior probe (exp_event_outcome_density_patient_signal_probe_v1) was FAIR in design but POWER-STARVED: within-genre LOW/MED/HIGH arms had only ~9K background tokens each, n_multi=21, gap=0.0000 exactly, SE~0.108 (>= the 0.08 pass threshold). Uninformative, not a refutation. Recipe to give it real power:
- **Scaffold:** BabyLM-style capacity-control -- FIXED token budget + FIXED model capacity, vary ONLY source composition. **The event/outcome-density axis is a CONFIRMED UNCLAIMED GAP across 3 BabyLM challenge years (child-directed-ratio, genre-mix, syntactic-filtering, paraphrase-aug have been tried; outcome-density has NOT) -> a properly-powered version is NOVEL and decisive, not a re-tread.**
- **High-density arm:** ROCStories (50K five-sentence causal-dense stories, CC-BY-SA, purpose-built consecutive-event state-advance) = best clean pilot; caveat = short/synthetic register not fully genre-decoupled from graded readers. Scale alternative: TF1-EN-3M (3M fable corpus, MIT, consequence-dense) -- caveat: fully LLM-synthetic (construct-validity). Supplementary (license-unverified): WikiHow (230K procedural), GLUCOSE (re-assembled to running text).
- **Low-density arm:** token/vocab/perplexity-matched graded-reader / Wikipedia prose.
- **Frozen yardstick (never touched by any arm):** McRae/DTFit thematic-fit correlation + pseudo-disambiguation (Chambers-Jurafsky style, label-free) + a forced-choice who-is-affected probe. Regress out perplexity/entropy as a nuisance covariate; sweep capacity tiers (must hold at every tier).
- **Overkill flag:** Na et al. 2024 (EMNLP, "Scalable Data Ablation... Modular Training and Merging" -- corrected citation, NOT "Racz") shard-merge trick is unnecessary for a 2-3-arm sweep; back-pocket only if this grows into a multi-way mixture grid.
- **Method-not-data flag:** Chambers-Jurafsky induced narrative schemas are NOT available as a static download (only narrative-cloze eval splits) -- usable as a METHOD to auto-derive an outcome-density signal from a corpus, not as ready-made data.

## (4) REPRESENTATION MAPPING onto the substrate
- **Concepts** (noun/verb meanings) -> reshape the learned CODEBOOK (CG 29368; RI/PPMI+SVD).
- **Facts / plausibility edges** (this verb-sense takes this affected-argument type) -> BIND into the event-plausibility web (free-algebra binding).
- **Active-learning lookup table** -> SemLink-unified PropBank+VerbNet role lookup + ATOMIC-2020 if-then outcomes, consulted by the gap-detect->lookup->verify->bank loop.

## GLASS-BOX INVARIANT (restated)
All of the above are ingested as STATIC content at BUILD/learning time = legal foundation scaffolding. The ONLY red line is a runtime LLM on the reasoning path -- which is exactly and only the COMET-live-query mode (forbidden). Every other resource is inherently static/inspectable.

## P (deflated)
- Adoptable glass-box foundation EXISTS + license-navigable: P~0.75 (multiple independent static resources; main risk = license-verification tail on Knowlywood/DTFit/McRae-CSV/WikiHow).
- A properly-powered ROCStories-vs-graded-reader density retest is FAIR + NOVEL + decisive: P~0.55 (register/genre-decoupling is the live confound to design around; the BabyLM-gap novelty is confirmed).
- COMET-offline-dump is glass-box-legal: P~0.85 (clean mechanical distinction).

## Citations (compiled from the 3 scans; verified author/year, arXiv/DOI where returned)
Role/thematic-fit: McRae/Spivey-Knowlton/Tanenhaus 1998 (J.Mem.Lang 38); Ferretti/McRae/Hatherell 2001 (44); Vassallo/Chersoni/Santus/Lenci/Blache 2018 (LREC LiNCR, DTFit); Santus/Chersoni/Lenci/Blache 2017 (EMNLP, github.com/esantus/Thematic_Fit -- distinct); Baroni & Lenci 2010 (Comp.Ling 36(4), marcobaroni.org/dm/); VerbNet (verbs.colorado.edu/verbnet, github.com/cu-clear/verbnet); FrameNet (framenet.icsi.berkeley.edu); PropBank (Palmer/Gildea/Kingsbury 2005, github.com/propbank/propbank-release); SemLink (github.com/cu-clear/semlink).
Commonsense KBs: Sap et al. 2019 (ATOMIC, arXiv:1811.00146); Hwang et al. 2021 (ATOMIC-2020, arXiv:2010.05953, github.com/allenai/comet-atomic-2020); Bosselut et al. 2019 (COMET, arXiv:1906.05317, github.com/atcbosselut/comet-commonsense); Mostafazadeh et al. 2020 (GLUCOSE, arXiv:2009.07758); Speer/Chin/Havasi 2017 (ConceptNet 5.5); Tandon et al. 2015 (Knowlywood, CIKM); Dalvi et al. 2018 (ProPara, arXiv:1805.06975); Bisk et al. 2020 (PIQA, arXiv:1911.11641).
Narrative/tooling: Chambers & Jurafsky 2008 (P08-1090), 2009 (P09-1068); Mostafazadeh et al. 2016 (ROCStories, N16-1098); Modi/Anikina/Ostermann/Pinkal 2016 (InScript, L16-1555); Findings of 2nd BabyLM Challenge (arXiv:2412.05149) + 3rd (2025.babylm-main.28); Na/Magnusson/Jha/Sherborne/Strubell/Dodge/Dasigi 2024 (EMNLP, "Scalable Data Ablation... Modular Training and Merging", arXiv:2410.15661); Koupaee & Wang 2018 (WikiHow); klusai/ds-tf1-en-3m (arXiv:2504.20605, 2025).

## Unverified / flagged (do not treat as certain without a direct fetch)
McRae/Ferretti machine-readable CSV location (only PDFs confirmed); DTFit hosting/license (do not conflate with esantus repo); VerbNet + FrameNet exact license clauses; PropBank frame-files-without-text usability (LDC text split); Knowlywood license (no marking found); ProPara dataset file format; WikiHow dataset redistribution license; GLUCOSE per-dimension physical-vs-social density; TF1-EN-3M synthetic-origin construct-validity; the 2026-format arXiv IDs from the brain-side companion drill remain format-unverified.
