# FULL-CHAIN MATHEMATICAL BF AUDIT -- raw text to sense-assignment decision (2026-09-10)

Owner ask: "double-check that the ENTIRE chain is mathematically BF." Every rung of the LIVE sense-assignment
decision is enumerated below with its computation, the brain's actual computation it realizes, the citation, and
its status (PINNED = the brain's mechanism is fixed and we copy it; COMPUTATIONAL-LEVEL = implementation unpinned
but a defensible published brain model; PARAMETER = a constraint we do not share, SWEPT never adopted). Verdict per
rung: BF / BF_SPIRIT / NOT_BF. Scope: this audits the chain THIS problem measures (grounded (+) parser-free SEQ,
fused, gated). No hdlab written (Q111).

## The chain, rung by rung

| # | rung | computation | brain-exact realization | citation | param(s) swept | verdict |
|---|---|---|---|---|---|---|
| 1 | lemma normalize | `normalize_lemma` affix stripping | morphological decomposition in the reading system | Rastle-Davis 2008 | -- | BF_SPIRIT |
| 2 | context window | direction+distance typed neighbours L1/R1/L2/R2 | temporal-order coding / theta-phase sequence window (sequence_memory S-matrix) | Lisman-Idiart 1995; Christiansen-Chater 2016 | window taps (+-1,+-2; capacity) | BF |
| 3 | co-occurrence accrual | online count of (word, typed-context) | Hebbian associative potentiation, accumulated online (no batch train) | Hebb 1949; brain does online learning | -- | BF |
| 4 | PPMI weight | max(0, log p(w,c)/p(w)p(c)) | rectified pointwise MI = Hebbian-predictive surprise / prediction error; SGNS ~ shifted PMI | Levy-Goldberg 2014 | -- | BF |
| 5 | row normalize | L2 per row | divisive normalization | Carandini-Heeger 2012 | -- | BF |
| 6 | grounded ATL rep | distinctive (whitened/ZCA) grounded vector | amodal ATL hub, privilege-distinctive features | Patterson-Nestor-Rogers 2007; Lambon Ralph 2017 | -- | BF (PINNED hub) |
| 7 | similarity readout | cosine over the population | population-vector readout | Georgopoulos 1986 | -- | BF |
| 8 | posterior | softmax(score / tau) | Gibbs/Boltzmann distribution (free-energy) | -- | tau (scale) | BF |
| 9 | fusion | add log-posteriors, weighted by earned-gain RATIO (precision-where-earned; grounded uniform, SEQ saturating log1p gain) | optimal convergent-cue integration = sum of precision-weighted cues; precision = population gain = Fisher info | Ma-Beck-Latham-Pouget 2006; Ernst-Banks 2002 | gain saturation (Weber-Fechner) | BF (gain ratio parameter-FREE) |
| 10 | confidence | top-2 decision-variable MARGIN = balance of evidence (W23: reliability-normalization tested, ties raw margin; margin is the brain-exact form and the best available) | balance-of-evidence on the accumulated DV = P(correct) | Kepecs 2008; Kiani-Shadlen 2009; Pouget-Drugowitsch-Kepecs 2016; Meyniel 2015 | -- | BF_SPIRIT |
| 11 | accept gate | SDT familiarity: accept iff z_top standout > criterion at a target false-alarm rate on the info-free null | signal-detection familiarity + criterion (recognition) | Yonelinas 2002; Bruce-Young | false-alarm rate (precision knob) | BF |
| 12 | learning / growth | grow-by-reading = online Hebbian count accrual; no gradient batch training | online experience-dependent plasticity | (brain does not do long training runs) | reading volume | BF |

## Removed non-BF atoms (the fidelity gain this problem/its siblings delivered)
- **arc-eager parser (`hdlab.arceager_parser`, NOT_BF)** -- greedy hard-decode supervised dependency parse. REMOVED
  from the meaning chain by the parser-free SEQ channel (W19); the identity signal is recovered with NO loss.
- **UPOS tagger (`hdlab.pos_tagger`, NOT_BF)** -- frozen supervised averaged-perceptron + hard Viterbi. REMOVED
  (it only fed the parser; SEQ needs no POS). The live chain now has NO parser and NO POS tagger.
- **unordered pooling bag** -- first-order relatedness, not identity. REMOVED (direction-typed SEQ supersedes it).
- **fixed cosine threshold `SENSE_MATCH_THRESH=0.45`** -- OUR-INVENTION constant. REPLACED by the scale-free SDT
  criterion (rung 11).
- **fitted fusion weight** -- OUR-INVENTION scalar. REPLACED by the parameter-free earned-gain ratio (rung 9).

## Admissible foundation assets (BF_SPIRIT, not defects -- owner 2026-08-16 allows static offline assets)
- grounded ATL sensorimotor norms (Lancaster) and valence (Warriner VAD): curated FOUNDATION assets, NO LLM, NO
  training, NO WordNet in any SimLex-graded channel. Supplied, not learned online -> BF_SPIRIT (admissible).
- FHRR/HRR binding (used elsewhere in the substrate, not on THIS ranking path): BF_UNPINNED at the neural
  implementation, kept as a defensible computational-level model (owner 2026-08-26).

## VERDICT
Every rung from raw text to the sense-assignment decision is BF or BF_SPIRIT; there is NO NOT_BF atom in the live
chain. Each parameter (window taps, tau, gain saturation, SVD rank, genus split, false-alarm rate) is a constraint
we do not necessarily share and is SWEPT, never adopted. The fusion weight and the accept criterion are
parameter-FREE (earned-gain ratio; SDT self-calibration). The two historically load-bearing NOT_BF atoms (parser +
POS tagger) are removed. Residual distance to the brain is KNOWLEDGE/EXPOSURE and the differentia/confidence levers
(W20-W24), not a non-BF stand-in. Witness: `verification/test_meaning_fusion_live_coverage.py` (parser-free import
check W19/W20; brain-exact confidence W23; differentia W24).
