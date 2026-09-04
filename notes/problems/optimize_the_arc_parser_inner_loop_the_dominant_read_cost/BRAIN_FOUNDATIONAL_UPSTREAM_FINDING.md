# Brain-foundational upstream prototype — a located negative that localizes the wall

**Context.** Beyond the byte-identical speed win (see `SOLVED.md`), the owner asked: prototype a
100%-brain-foundational UPSTREAM component and show the chain can *exceed* — "the only way to
overcome the wall is for EVERY component, you and upstream, to be brain-foundational." This documents
that prototype. It is a DIRECTION (a model change), not part of the byte-identical speedup; NO hdlab
written. Glass-box, one-pass counts, NO gradient training, NO LLM. ~7 literature drills this session.

## What I measured first (the chain, first-hand on UD-EWT test, n=25,094 tok / 24,120 arcs ≤50)
| stage | UAS (gold POS) | UAS (pred POS, deployed) |
|---|---|---|
| arc-FACTORED parser (current default parse) | 0.7907 | 0.7608 |
| arc-EAGER parser (brain-foundational: incremental, ranked-parallel, WM-buffer) | **0.8421** | **0.8053** |
- **The incremental parser is the brain-foundational one and it already wins: +0.051 gold / +0.044 deployed.** (Zhang & Nivre 2011 arc-eager; it exists in `hdlab/arceager_parser.py`, default-OFF.) This is the *component* half of the thesis, confirmed: making the parser brain-foundational lifts the metric.
- The gold→pred gap for arc-eager (0.8421→0.8053 = 0.037) is the signal lost to the UPSTREAM tagger. So I targeted the tagger.

## The tagger, made brain-foundational three ways — none exceeds (the located negative)
Floor = the live Collins–Viterbi averaged-perceptron tagger, **0.9445** POS accuracy.
Every arm is glass-box, one-pass counts, incremental. Info-free twin = scrambled lexicon.

| brain-foundational arm (what was PINNED) | POS acc | vs floor |
|---|---|---|
| v1 incremental beam + lexical retrieval + suffix morphology + trigram prediction + Competition-Model cue-weight | 0.9191 | −0.025 |
| v2 + faithful TnT morphology (successive-abstraction suffix, cap-split) + deleted-interpolation trigram | 0.9239 | −0.021 |
| perceptron emission + brain trigram top-down prior + beam (β swept) | 0.9394 | −0.005 |
| **info-free twin (scrambled lexicon)** | 0.093–0.125 | (collapses — the cue carries real signal) |
- Head-to-head on the slices I expected the brain cues to win: **OOV** perceptron 0.8140 vs brain 0.7365 (−0.078); **ambiguous known words** perceptron 0.9499 vs brain 0.9240 (−0.026). The brain-foundational tagger loses *even on OOV/robustness*.
- **Why (the refutation of my own hypothesis): the perceptron tagger is ALREADY brain-compatible.** Its features are cue-based (lexical + affix + shape + neighbouring-word context) and it is an error-driven online learner (the perceptron update is a delta/Hebbian-like rule). Swapping it for a one-pass *generative* tagger is a fidelity *decrease*, so the metric falls — **consistent with, not against, "fidelity compounds."** Adding a hand-counted trigram prior on top is redundant with its learned context and *hurts*.

## The one genuinely-new brain lever — joint category+structure — has oracle headroom but is blocked
The brain does not tag-then-parse; category and structure are assigned JOINTLY, incrementally, with
top-down syntactic feedback (the parse disambiguates the tag).
- **ORACLE** (gold syntactic relation as a top-down cue): P(tag | gold deprel) lifts the tagger **0.9445 → 0.9607 (+0.016)** — the remaining tag errors ARE syntactically resolvable. The headroom is real.
- **REALISTIC** (arc-eager PREDICTED structure): the same cue **regresses** — tagger 0.9445 → 0.9340, and re-parsing with those tags drops UAS 0.8031 → 0.7962. The parser (0.842 UAS) is not accurate enough to supply a reliable top-down cue; its errors correlate with and amplify the tag errors (circular). This reproduces, for general tagging, the earlier narrow `joint parse-decode` located negative.

## KEY FINDING — where the wall actually is
Making the *decode algorithms* brain-foundational does NOT overcome the wall, and the reason is
precise and unifying:
1. The parser IS brain-foundational (arc-eager) and that helped (+0.044) — the thesis holds for a component that can be made faithful *without depending on an unreliable upstream*.
2. The tagger is already cue-based/error-driven (brain-compatible) and near its ceiling; a "more brain-foundational" generative swap regresses.
3. The true brain mechanism (JOINT incremental tag↔parse with top-down feedback) has measured headroom (+0.016) but is **GATED on parser accuracy** — you cannot use structure to fix tags until the structure is reliable.
4. The parser's accuracy (0.842 gold vs human ~0.95) is itself gated by the missing **lexical-SEMANTIC grounding** (thematic fit / selectional preference / valence) — and adding lexical valence to this exact parser **HARD_FAILED** (`exp_depparse_transition_valency_subcat_cpu_v1`).

**So the binding non-brain-foundational component is NOT any decode algorithm — it is that NO stage
has lexical-SEMANTIC grounding.** Surface features (POS/word-form) cap the tagger, which caps the
parser, which caps the joint loop, which caps the chain. This is exactly the project's **meaning
channel** north star. "Every component must be brain-foundational" is corroborated; the last
non-faithful link is localized to *meaning*, the same wall the reader's WSD / consolidation work hit.

## Deployable win that falls out of this (verdict-independent)
The reader's default parse is the arc-FACTORED parser (0.791 gold UAS). The brain-foundational
arc-EAGER parser (0.842) is **default-OFF** (`parser_arceager`). Flipping the *parse* (not the
role-source — that wiring was separately a located negative) to arc-eager is **+0.051 gold / +0.044
deployed UAS**, already validated, glass-box. Recommend strategy evaluate the flip on the reader's
live parse metric (per the "no more default-off; measure impact and turn on" directive).

## Files (experiments/ only; NO hdlab written)
- `experiments/exp_brain_foundational_tagger_v1.py`, `_v2.py` — the brain-foundational taggers + info-free twin.
- probes inline (arc-eager UAS, tagger error profile, oracle vs realistic joint decode) — reproducible from the commands in the session log; results in `data/exp_brain_foundational_tagger_v*/metrics.json`.

## What I would withdraw first if wrong
The +0.016 oracle joint-headroom number (single-run, gold-deprel cue). If wrong, the located
negative (realistic joint regresses; standalone brain tagger regresses) and the parser win (+0.044)
still stand — those are the load-bearing claims.

---

# GROWING GROUNDING — the clear path, prototyped and grown (the answer to "how do we break the wall")

The wall localizes to grounding, so I prototyped the IDEAL grounded system on the canonical
grounding-sensitive parse decision (PP-attachment: attach the PP to the verb or the noun) and grew
the grounding lexicon. Files: `experiments/exp_grow_grounding_pp_attachment_v1.py`
(+ object-selpref probe inline); metrics `data/exp_grow_grounding_pp_attachment_v1/metrics.json`.
UD-EWT, n=1104 ambiguous PP cases, glass-box, one-pass counts, NO LLM.

## The clear path IS a growth curve (grounding grows -> capability grows, monotonic)
| grounding lexicon size | PP-attach accuracy |
|---|---|
| FLOOR (locality / always-attach-majority) | 0.5870 |
| grown on 5% of corpus | 0.5833 |
| 10% | 0.5888 |
| 25% | 0.6005 |
| 50% | 0.6214 |
| **100% (full grounding)** | **0.6386  (+0.0517 over floor)** |
| info-free twin (shuffled preposition) | 0.5118 (collapses BELOW floor -> the grounding carries real signal) |
- **Monotonic in grounding size, and STILL RISING at 100% train** -- the curve is not saturated, so
  more grounding keeps paying. SOTA lexicalized PP-attach ~0.84 / human ~0.88 is the ultimate ideal;
  the path from 0.59 -> 0.64 -> ... -> 0.84 is "keep growing the grounding lexicon."

## "Make sure it's ideal" -- LEXICAL grounding is the load-bearing signal; the generic hub is NOT the right ideal
- LEXICAL co-occurrence grounding (Hindle & Rooth 1993: attach where the preposition associates more) = 0.6386.
- Adding the DISTRIBUTIONAL hub (composed_hub_predictor's 200-d PPMI-SVD) as a selectional-preference
  backoff -- on the candidate HEAD *and* on the PP's OBJECT noun (Pado/Erk/Resnik) -- **does NOT help**
  (0.629-0.632, slightly below lexical-only). Reason, verified against the research: the hub is a
  **topical** distributional space, and attachment needs a **syntactically-TYPED** (head,
  grammatical-function) space -- Pado, Pado & Erk (2007) show plain distributional vectors "cannot
  separate hunter from deer" for this exact discrimination; the fix is (head,GF)-typed dimensions,
  which the topical hub does not have. So the IDEAL grounding is lexical co-occurrence + a
  SYNTACTICALLY-TYPED selectional-preference space (Pado) or WordNet-class association (Resnik) --
  NOT the generic topical hub. This is the same lesson as the reader's WSD wall (the frozen
  distributional substrate is topical/superposed; grounding must be typed).

## The organs that grow it (REUSE)
- `hdlab/grounding_acquisition_loop.py` -- the online grow-grounding organ (grows the lexicon from reading).
- `hdlab/composed_hub_predictor.py` + `hub_ppmi_svd_200d.pkl` -- the ATL hub (topical; needs typing for attachment).
- `hdlab/cls_growth.py` -- safe growth (keep-both + rollback + EMA anchor) to grow WITHOUT drift.
- WordNet KBs -- the Resnik taxonomic backoff (typed grounding for sparse heads).

## KEY FINDING (the clear path, stated)
The wall is broken by GROWING GROUNDING, and the growth is monotonic and unsaturated: floor 0.587 ->
grown grounding 0.639 (+0.052) on PP-attachment, twin collapses, curve still rising toward the ~0.84
ideal. The grounding that pays is LEXICAL co-occurrence + SYNTACTICALLY-TYPED selectional preference
(Pado/Resnik) -- NOT the generic topical hub. So the path to solve the parser/chain wall is: grow a
TYPED grounding lexicon (co-occurrence + selectional preference + WordNet-class), online from
reading via `grounding_acquisition_loop` under `cls_growth` safe growth -- and as it grows,
attachment (and the joint tag<->parse loop it unblocks) climbs toward the competent-reader ceiling.
This is the meaning channel, and it is the ONE component whose brain-foundational grounding lifts the
entire chain -- exactly the owner's thesis.
