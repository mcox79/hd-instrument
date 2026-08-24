# **THE IDENTITY CODE ON THE LIVE PATH IS A SHA256 RANDOM DRAW. IT SCORES `-0.0026` ON CASE INVARIANCE -- THE VWFA'S DEFINING PROPERTY -- WHERE THE BUILT FORM ORGAN SCORES `+1.0000`, AT NO COST ON THE CONTROLS.**

**This is the strongest brain-foundational case for the wiring the owner conditionally authorised, and
it also fixes the wiring's SHAPE.**

---

## 1. WHAT THE LIVE PATH ACTUALLY USES

*`hdlab/reading_grounding_loop.symbol_vector(sym, d)`:*

```python
seed = int.from_bytes(sha256(sym.encode()).digest()[:8], "big") % 2**32
v = np.random.default_rng(seed).choice([-1.0, 1.0], size=d)
```

***A HASH-SEEDED RANDOM BIPOLAR DRAW. By construction it has NO form structure at all*** -- two spellings
of the same word get independent random codes.

## 2. ✅ MEASURED SIDE BY SIDE ON THE VWFA'S DEFINING TEST

| pair | **HASH (live)** | **FORM organ** |
|---|---|---|
| `cat` / `CAT` | 🔻 **`-0.0391`** | ✅ **`+1.0000`** |
| `doctor` / `DOCTOR` | 🔻 `+0.0000` | ✅ `+1.0000` |
| `running` / `RUNNING` | 🔻 `+0.0312` | ✅ `+1.0000` |
| `cat` / `cats` | `+0.0469` | `+0.4658` |
| `child` / `children` | `+0.0547` | `+0.5059` |
| `walk` / `walked` | `-0.0391` | `+0.4463` |
| `cat` / `democracy` *(control)* | `-0.0312` | `+0.0254` |
| `doctor` / `hammer` *(control)* | `+0.0469` | `+0.0771` |

| | HASH | FORM |
|---|---|---|
| **CASE INVARIANCE mean** | 🔻 **`-0.0026`** | ✅ **`+1.0000`** |
| **INFLECTION mean** | `+0.0208` | `+0.4727` |

> # **THE LIVE CODE TREATS `cat` AND `CAT` AS UNRELATED. THE VWFA IS *DEFINED* BY NOT DOING THAT.**

✅ **AND THE FORM ORGAN COSTS NOTHING ON THE CONTROLS** -- *unrelated pairs stay near zero in both.*
***It ADDS invariance without adding false similarity, which is the only way this could have been a
free win and it is.***

## 3. 🔑 **AND THE BLAST-RADIUS CHECK FIXES THE WIRING'S SHAPE**

*Before proposing to swap `symbol_vector`, I checked what depends on it:*

| finding | consequence |
|---|---|
| **it also encodes RELATION LABELS** -- `symbol_vector("REL:" + rel)`, `"REL:^nmod"`, `"REL:^obj"` | 🔻 **form invariance is MEANINGLESS for a relation tag**; a form code over `REL:^nmod` is noise |
| **`perirhinal_conjunctive.py` imports and accumulates it** | a second live consumer |
| **its codes are DETERMINISTIC per symbol and land in accumulated stores** | 🔻 **swapping it REWRITES EVERY PERSISTED SYMBOL CODE** -- the same hazard already flagged for the `256 -> 1024` change |

> ### **SO THE WIRING MUST BE ADDITIVE -- A SEPARATE FORM-IDENTITY ACCESSOR ALONGSIDE `symbol_vector`, NOT A REPLACEMENT OF IT. WHICH IS EXACTLY "CONNECT BESIDE, DO NOT BLEND", ARRIVED AT INDEPENDENTLY FROM THE STORE CONSTRAINT.**

***THREE INDEPENDENT ARGUMENTS NOW AGREE ON THE SAME SHAPE:*** *(1) the brain -- the VWFA feeds lexical
access rather than being it; (2) the empirical `HARD_FAIL` -- late-combining the streams scored `0.2000`
against `0.2533` for the form stream alone; (3) store compatibility -- replacing `symbol_vector`
invalidates every persisted code.*

## 4. ⚠️ LIMITS

1. **8 word pairs.** *Enough to establish the property and its total absence in the hash; not a rate.*
2. **This shows the form code is a BETTER IDENTITY CODE. It does NOT show that wiring it improves any
   downstream task** -- *the `ORGAN_MAP` A1 margin (`0.0870` vs `0.0480`) is the only task evidence, and
   it carries a spelling-shortcut caveat.*
   > 🔴 **SHARPENED 2026-08-24 — THAT CAVEAT WAS RIGHT AND IT IS NOW DECISIVE: THE MARGIN REVERSES.**
   > The `0.0870` was `~78%` MORPHOLOGICAL LEAKAGE in the WordNet gold. Re-measured in-harness on
   > stripped gold (owner ruling Q117): **the floor is `0.0195` and the live read-out is `0.04575`,
   > so the SUBSTRATE wins.** ➡️ **The only task evidence cited for the form organ now points the
   > OTHER WAY.** *This does NOT touch section 1-3 of this note: the identity-code property
   > (case invariance, graded inflection) is a different criterion and is untouched by the gold
   > defect. The limit above simply became stronger than its author could know.*
3. **I have NOT made the edit.** *The blast-radius finding is why: an additive accessor is safe, a swap
   is not, and that distinction was not obvious before checking.*
4. 🔻 **THE Q102 WATCH CONDITION STILL STANDS** -- *a better index is not better understanding; the tell
   is recognition rising while meaning stays flat.*

## TLDR

The system currently tells words apart by scrambling each spelling into a random fingerprint. **That
means "cat" and "CAT" are, to it, two completely unrelated things** — I measured it at essentially zero
similarity. The brain's word-recognition area is *defined* by not making that mistake.

**The component we already have gets this exactly right**: identical for "cat" and "CAT", partly similar
for "child" and "children", and near zero for unrelated words — **and it is no worse than the current
code on unrelated words**, so there is no trade-off hiding in it.

**Checking what depends on the current code also settled how to connect the new one.** The random
fingerprints are used for two other things: labelling grammatical relations, where spelling similarity is
meaningless, and building up stored memories, where changing the code would silently invalidate
everything already saved.

**So it has to be added alongside rather than swapped in.** That is the same conclusion the brain
reasoning gave, and the same one a failed experiment gave when someone tried mixing the streams
together. **Three separate lines of argument, same answer.**

**What this does not show** is that connecting it improves anything the system is asked to do. It shows
we are using a demonstrably worse identity code than the one sitting unused.

## QUESTIONS

None.

## NEXT STEPS

1. **The wiring is now fully specified: an ADDITIVE form-identity accessor, not a swap** *-- with the
   store-invalidation hazard as the reason, independent of the brain argument.*
2. ⚠️ **`symbol_vector` must keep handling RELATION labels** *-- a form code over `REL:^nmod` is noise.*
3. *Method note: **checking the blast radius changed the design, not just the risk.** "Swap it" and "add
   it beside" look like the same task until you see it also encodes relation tags and lands in stores.*
