# Corpus expansion plan (2026-08-12)

Growth is PAUSED pending director decision. This is plan + evidence only; nothing downloaded or ingested.

## 1. Quantified asymmetry (v5 definitional facts vs measured sentence counts)

Source: `data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl` (2092 facts,
`segment` field), sentence counts from `notes/corpus_composition_audit_2026-08-12.md`
(`data/exp_reading_grounding_loop_cycle2_v1/metrics.json:segment_summaries`).

| segment | source | n_sentences | facts | facts/1000 sent |
|---|---|---|---|---|
| bio_new | OpenStax Concepts of Biology (CNXML) | 4500 | 1371 | **304.7** |
| bootstrap | OneStop Ele/Int subset + ALL of process_articles_v1 | 4640 | 281 | 60.6 |
| int_cont | OneStop Intermediate | 4952 | 141 | 28.5 |
| ele_cont | OneStop Elementary | 4623 | 132 | 28.6 |
| adv_new | OneStop Advanced | 7408 | 167 | 22.5 |
| **total** | | **26123** | **2092** | 80.1 avg |

Biology is **5-13x more productive per sentence** than any OneStop level, not merely larger in raw
count (it's only 17.2% of sentences but 65.5% of facts). The asymmetry is real and per-sentence, not
an artifact of corpus size. `bootstrap`'s 2x lift over pure-OneStop (60.6 vs ~26 avg of the other
three) is process_articles_v1 pulling its weight too -- consistent with "dense explicit description"
being the driver, not "biology" specifically. Note process_articles_v1 (512K, small) is already 100%
consumed by bootstrap -- no more headroom there. **Conclusion: proceed. The plan is not wrong.**

## 2. Already on disk (`data/corpora/`, from `corpus_composition_audit_2026-08-12.md` + fresh check)

- `textbook_concepts_biology/` (58M) -- the one dense source in use. Includes `clean_cnxml.py`
  (284 lines, generic CNXML->sentence cleaner, one hardcoded path constant `BASE` at line 15;
  trivially reusable for other OpenStax CNXML titles) + `corpus_stats.py` + raw CNXML mirror +
  `cleaned/concepts_biology.clean.txt` (9599 lines).
- `process_articles_v1` (512K) -- fully consumed already (bootstrap segment), no headroom.
- `onestop` (1.6G) -- fully consumed already (all 3 levels), no headroom for more density (news
  prose, not definitional-dense by nature per section 1).
- Historical/literary (alice, little_women, tom_sawyer, sherlock_holmes, wizard_of_oz,
  anne_of_green_gables, tinyshakespeare, litbank_*) -- confirmed NOT primary-eligible under the
  USER modern-sources rule (`feedback_stop_mcguffey_use_modern_sources_USER_2026-08-08`, and
  same era logic extends to all pre-20c texts here). None currently wired into the foundation
  loaders. Usable only as a HELD-OUT contrast set to test whether the extractor's density gain is
  genre-general (dense old prose) or textbook-specific (dense modern didactic prose) -- see risk
  in section 4. Not proposed as primary.
- mcguffey_graded/mcguffey_readers (9.0M+4.5M) -- historical, already excluded per 08-08 directive,
  not touched by this plan.
- Everything else (arc, race, wiqa, social_iqa, mcscript2, simplewiki, ud_english_ewt, binder,
  breadth_v1, graded_readers_*, agreement, word_image_early_vocab, worldtree) -- NLP
  benchmark/eval sets, not raw prose corpora; out of scope for reading-diet expansion.

**No usable-untapped dense-textbook material currently on disk.** Everything dense (bio_new) is
already fully in the foundation; everything else on disk is either already saturated (onestop,
process_articles_v1) or explicitly excluded (historical). Expansion requires new acquisition.

## 3. Survey of dense explicit sources (license-clean, textbook-shaped)

| source | license | format | approx size | pipeline reuse |
|---|---|---|---|---|
| OpenStax Biology 2e | CC BY-NC-SA 4.0 (confirmed same as Concepts of Biology, `PROVENANCE.md` already checked sibling titles) | CNXML, `osbooks-biology-bundle`-style GitHub repo | larger than Concepts of Biology (~2-3x module count; comprehensive vs. concepts-level intro) -- exact module count not yet fetched, needs a `raw.githubusercontent.com` listing pass before download | direct reuse of `clean_cnxml.py`, same book family |
| OpenStax Anatomy & Physiology 2e | CC BY-NC-SA 4.0 (confirmed) | CNXML | large (comprehensive med-adjacent text) | reuse `clean_cnxml.py` |
| OpenStax Microbiology | CC BY-NC-SA 4.0 (confirmed) | CNXML | medium-large | reuse `clean_cnxml.py` |
| OpenStax Psychology 2e | CC BY-NC-SA 4.0 (confirmed) | CNXML | medium-large | reuse `clean_cnxml.py` |
| OpenStax Astronomy 2e | CC BY-NC-SA 4.0 (confirmed) | CNXML | medium | reuse `clean_cnxml.py` |
| OpenStax Chemistry 2e | not yet checked directly, but "none of OpenStax's flagship intro-science textbooks are CC BY" per `PROVENANCE.md` -- assume CC BY-NC-SA 4.0 pending confirm | CNXML | large | reuse `clean_cnxml.py` |
| CK-12 (various science FlexBooks) | mixed, mostly CC BY-NC 4.0 -- verify per-title | HTML/EPUB, not CNXML | varies, many short modular texts | needs a NEW cleaner (different markup); more integration cost than OpenStax siblings |
| Wikibooks (science shelves) | CC BY-SA 3.0/4.0 (more permissive, no NC restriction) | MediaWiki markup | uneven quality/completeness vs. OpenStax; some books incomplete | needs a NEW cleaner (wikitext, not CNXML); more integration cost |

**Ranking by effort-to-reuse:** OpenStax siblings (same repo shape, same license family, same
cleaner, only `BASE`/module-list changes) are near-zero marginal integration cost. CK-12/Wikibooks
are viable backup sources but require a new markup cleaner and separate license verification per
title -- lower priority.

Sizes above marked "approx" / "not yet fetched" are deliberately not firm -- per instructions, no
multi-GB download or even a full repo listing was performed before director sign-off; a follow-up
`raw.githubusercontent.com` module-list fetch (cheap, no download) is the next step once approved.

## 4. Recommendation

**Order:** (1) OpenStax Biology 2e first -- same license already confirmed, same cleaner, largest
single dense-prose gain for near-zero pipeline cost. (2) Anatomy & Physiology 2e and Microbiology
next -- same repo family, adds subject diversity (reduces biology-vocabulary monoculture risk).
(3) Psychology 2e and Astronomy 2e after that for further subject diversity. (4) Chemistry 2e
pending license re-confirm. (5) CK-12/Wikibooks only if OpenStax volume proves insufficient or a
new subject area (not covered by the OpenStax catalog) is wanted.

**Expected yield:** applying the measured bio_new rate (304.7 facts/1000 sentences) as a first-order
estimate, each ~4500-sentence-equivalent OpenStax addition should add on the order of 1000-1400
definitional facts -- roughly matching or exceeding the current total foundation size (2092) per
book added. Actual rate will vary by book (denser glossary-style texts like A&P likely higher;
narrative-style psychology chapters likely lower, closer to the bootstrap 60.6 rate).

**Risk to watch (USER's own framing applies here):** more of the same KIND of text (more biology,
or more OpenStax-style didactic prose in general) may raise fact QUANTITY without raising grounding
QUALITY -- i.e. it could just produce more instances of the same `(X, GROUNDED_MEANING, X)`-adjacent
shallow definitional pattern rather than deeper/more diverse relational grounding, and it stays
single-domain (biology-vocabulary-heavy) even after quantity grows. **The measurement that would
detect this:** re-run the director hand-score protocol (`director_handscore_b3_v5_termboundary_
2026-08-12.md` methodology, same rubric/seed) on a fresh sample drawn from the NEW segment(s) only,
compare MEANINGFUL% against the existing 64% bio_new baseline -- flat or declining % on new dense
text = quantity-only gain, diversify sourcing rather than adding more OpenStax volume. Also watch
subject-word overlap in `subject_head_lemma` across segments (already dominated by biology terms;
a swelling single-domain vocabulary would show the same failure mode as the tautology-heavy count
before it).
