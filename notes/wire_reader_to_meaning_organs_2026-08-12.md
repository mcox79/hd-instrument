# Wire reader to meaning organs -- STEP 1 fact-establishment (2026-08-12)

Task: verify the director's islanding hypothesis (a)/(b)/(c) BEFORE building.
Discipline: a refutation is a full result. Do not build to justify the framing.

Prior-work check (substrate_query.sh "superposition context-dependent word meaning
grounding store multiple senses"): TOP HIT AT cosine>0.30 --
`notes/PLAN_B_grounding_word_context_affect_superposition_map_2026-08-07.md::chunk001`
(cosine=0.3037). That note ALREADY specifies this exact design ("a word's meaning is a
superposition of (context -> sense) bindings that COLLAPSES when the situation supplies a
context KEY ... bind(context, affect), BUNDLE, UNBIND with running context + CLEANUP").
=> This is a REDISCOVERY of an already-designed-but-unbuilt plan, NOT a novel idea.
Second hit: `preregs/2026-08-12_foundation_validation_harness_v1.md::chunk003` (0.2998),
which is where the landed store's cardinality config is recorded.

---

## (a) "store structurally unable to hold >1 meaning per word" -- **REFUTED AS STATED**

The prior VET's characterization is materially wrong on two independent counts.

**Count 1 -- multi-object IS supported, by configuration.**
`hdlab/hd_fact_store.py:306-319`:

```python
card = self.relation_cardinality.get(relation, "FUNCTIONAL")
if card == "MULTIVALUED":
    for f in conflicts:
        if f.status == "ACTIVE":
            f.status = "COMBINED"
    rec.status = "COMBINED"
    self._append_fact(rec)
    resolution, note = "COMBINE", "equal-trust + multivalued relation -> merge (both valid)"
else:
    for f in conflicts:
        f.status = "FLAGGED"
    rec.status = "FLAGGED"
    self._append_fact(rec)
    resolution, note = "FLAG", "equal-trust + functional relation -> contradiction, keep both UNRESOLVED"
```

The FLAG branch fires only because `GROUNDED_MEANING` is *configured* FUNCTIONAL, which is
merely the `.get(relation, "FUNCTIONAL")` DEFAULT being taken. Declaring
`relation_cardinality={"GROUNDED_MEANING": "MULTIVALUED"}` switches to COMBINE. That is a
one-line config change, not a structural limit and not a wiring project.

**Count 2 -- FLAGGED facts are NOT unreachable.**
`hdlab/hd_fact_store.py:66`:

```python
ACTIVE_STATUSES = frozenset({"ACTIVE", "COMBINED", "FLAGGED"})
```

`query()` (line 326-330) and `live_facts()` (line 332-333) both filter on ACTIVE_STATUSES, so
BOTH objects remain live and queryable, each returned with its `status`. The claim that the
FLAG makes "two ACTIVE objects unreachable" does not hold: they are reachable; they are
merely marked unresolved.

**What IS true:** the landed foundation took the FUNCTIONAL default.
MEASURED@`preregs/2026-08-12_foundation_validation_harness_v1.md::chunk003` quoting the
frozen snapshot's `store/store_meta.json`:
`relation_cardinality={KNOWN_WORD: FUNCTIONAL, GROUNDED_MEANING: FUNCTIONAL}`.
And the v3 cell constructs the store with NO cardinality at all --
`experiments/exp_definitional_grounding_v3.py:201`: `store = HDFactStore(n_dim=N_DIM, seed=0)`.

**The REAL gap that survives the refutation:** even MULTIVALUED/COMBINE yields an *unordered
set* of objects for a given (subject, relation). There is NO context key, so there is no way
to ask "which of this word's meanings applies HERE". Context-conditioned *retrieval* is the
genuinely absent capability -- not multi-object *storage*.

## (a-bis) The real write-once is in the LIBRARY, not the store -- **CONFIRMED**

`hdlab/grounding_acquisition_loop.py:178-182`:

```python
def flag(self, lemma: str, episode_id: str, pole: str, context_vec: np.ndarray,
         pass_idx: int) -> bool:
    """Append one trace. No-ops (returns False) for an item that already reached a terminal
    status (GROUNDED_* / ESCALATED) -- terminal items accept no further evidence. Returns True
    iff a trace was actually appended."""
```

Once a lemma banks as GROUNDED_*, it accepts no further evidence, ever. So a second sense is
never even ATTEMPTED -- the store's conflict logic is never reached for a second meaning.
This, not the store cardinality, is the mechanism that makes grounding write-once.

## (b) reading loop grounds by flat cosine argmax, single pair -- **CONFIRMED with corrections**

CONFIRMED: `hdlab/reading_grounding_loop.py:203-218` `canonicalize()` is literally an argmax
of `_cos` over `space.anchors()` with a threshold (`SENSE_MATCH_THRESH = 0.45`, tagged
HYPOTHESIZED in-source at line 104). One winner is returned. Then
`reading_grounding_loop.py:440` writes exactly one pair:
`state.store.store(lemma, MEANING_RELATION, canon_obj, f"reading:{source_tag}", trust)`.
No context key is stored anywhere on that fact.

CORRECTION 1 -- "NO encode-time canonicalization" is WRONG. There IS a canonicalization step
(`canonicalize()`), it is just a *local flat-cosine* one over bundled context vectors rather
than the validated learned organ.
CORRECTION 2 -- "NO unbind+cleanup retrieval" is WRONG. `hd_fact_store.recover_fact()`
(lines 187-198) is per-role unbind + per-domain cleanup and is the ONLY read path. What is
absent is unbind+cleanup *over a superposition keyed by context* -- retrieval is per-fact.

CONFIRMED as absent: superposition storage, and any context/state conditioning.

## (a) EMPIRICAL REFUTATION on the actual landed v3 data -- decisive

Replicating `bank_facts` EXACTLY (`exp_definitional_grounding_v3.py:199-204`,
`HDFactStore(n_dim=2048, seed=0)`, no cardinality) over all 1751 v3 DEF facts:

```
stored: 1751   live: 1751
resolutions: Counter({'CLEAN_STORE': 1316, 'FLAG': 435})
statuses:    Counter({'ACTIVE': 1028, 'FLAGGED': 723})
apple -> [('company', 'FLAGGED'), ('valuable', 'FLAGGED')]
aorta -> [('artery', 'FLAGGED'), ('heart', 'FLAGGED')]
acid  -> [('monomer', 'FLAGGED'), ('substance', 'FLAGGED')]
```

**NOTHING IS LOST. 1751 stored, 1751 live.** 723 facts carry status FLAGGED, but FLAGGED is
in ACTIVE_STATUSES, so every one of them is returned by the glass-box `query()` path
(unbind + cleanup). The multi-sense words are ALREADY multi-sense in the landed store and
their senses are ALREADY retrievable.

Collision census over `data/foundation/reading_grounding_v3_definitional/definitional_facts.jsonl`:
- 1751 facts / 1316 distinct subjects
- **288 subjects (21.9%) already hold >1 DISTINCT object**; 723 facts (41.3%) are involved
- examples: `apple->{valuable, company}`, `aorta->{heart, artery}`, `acid->{substance, monomer}`,
  `allele->{variant, factor, dominant, square, hide}`

=> The premise "the grounding store may be structurally unable to hold more than one meaning
per word" is **REFUTED, in code AND on the landed data**. So is "each lemma is grounded
write-once" *for the v3 definitional path* (that path does not use the Library at all; it
banks directly). Write-once is real ONLY for `reading_grounding_loop`, via
`Library.flag()`'s terminal-status no-op -- a different path from the one that produced the
38% win.

## VERDICT ON THE BUILD DECISION: STOP. Do not wire superposition to chase the 38%.

Two independent reasons:

1. **The stated defect does not exist.** Multi-object storage works today; the senses are
   live and queryable. The only genuine absence is a CONTEXT KEY -- there is no way to ask
   "which sense applies HERE". That is a real gap but a much smaller and different one than
   the hypothesis asserts, and it is not what the 38% measures.

2. **Superposition storage cannot move the 50-pair audit rate, by construction.** The audit
   scores EMITTED (subject, object) PAIRS for meaningfulness. All 1751 pairs are already
   stored and already scoreable. Changing the REPRESENTATION of pairs that are already
   retained cannot change what fraction of them a human scores MEANINGFUL. Re-banking
   `allele->{variant, factor, dominant, square, hide}` in superposition leaves `square` and
   `hide` exactly as wrong as they are now. Precision is set by the EXTRACTOR (the v3
   definitional win), not by the store. Running the 50-pair audit against a superposition
   re-bank would be a rigged null: guaranteed ~38% +/- sampling noise, and any movement
   would be sampling noise misread as a mechanism effect.

**What would make me wrong (the result that would re-open this):** if the context key were
wired at EXTRACTION time and used to SUPPRESS emission -- i.e. if context-conditioning acted
as a filter that declines to emit `allele->square` because no context supports it. That is an
extractor change, not a storage change, and it should be pre-registered and measured as such.

## THE MEASUREMENT THAT WOULD ACTUALLY SHOW SUPERPOSITION'S VALUE

Not the 50-pair rubric (it scores single pairs; the whole claim is that meaning is
context-conditioned, which a single-pair rubric cannot see). The right can-fail test is
**context-conditioned sense selection**, on the 288 words that already have >1 sense:

- Held-out sentence containing word W, whose true sense is object O_i out of W's k stored senses.
- Query the store WITH the sentence's context vector as the key; does it return O_i?
- Baseline the flat store CANNOT beat: it has no context input, so its best possible strategy
  is a fixed choice per word -> expected accuracy 1/k (~0.46 at the observed mean k=2.16 for
  multi-sense words), and it is provably incapable of varying its answer with context.
- This is can-fail: superposition + unbind + cleanup can easily land AT or BELOW 1/k if the
  context vectors for a word's two senses are not actually separable.
- Powered on 288 words / 723 facts -- enough for a real effect size.

The honest framing: this measures a capability the flat store cannot have AT ALL, rather than
re-running a precision metric that storage cannot influence.

## (c) -- organ location (delegated search in flight)
