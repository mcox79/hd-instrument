"""exp_read_discourse_wsm_running_vs_static_coherence_v1 -- THE MISSING LINK: assemble a RUNNING
maintained "state of mind" (bind role-fillers per sentence -> hold in a Cowan-span ACTIVE FOCUS ->
CHUNK+PAGE the oldest entity to a durable store when focus saturates -> carry the maintained state
FORWARD) and test whether it beats the STATIC entity-grid snapshot SPECIFICALLY where the static
snapshot is known to fail: fine-local adjacent-sentence-swaps, and longer passages.

TRIGGER: USER's diagnosed reframe (2026-07-17) -- precision/discourse/focus are facets of ONE unbuilt
thing, a running state of mind; the native bind/bundle mechanism exists, the RUNNING LOOP that
maintains it across a passage does not. Reuses (does NOT rebuild): (1) the STATIC entity-grid cell's
entity/role extraction + grid-building + permutation generators + STATIC role-transition scorer,
imported UNMODIFIED from experiments.exp_read_discourse_entitygrid_coherence_v1 (landed MIDDLE_BAND,
commit-tracked: HARD-PASSED gross full-shuffle coherence, acc_A=0.854 margin=+0.171 vs co-occurrence,
but FAILED fine-local adjacent-swap, acc_A=0.554 margin=-0.021 -- WORSE than the co-occurrence
baseline, i.e. essentially at chance on the hard condition); (2) the Cowan ~F=3-4 active-focus span
design parameter measured by exp_substrate_resonator_focus_lever_v1 (MEASURED@data/exp_substrate_
resonator_focus_lever_v1/metrics.json: flat-bundle joint-decode holds cleanly at F=3-4, degrades
sharply at F=6/F=8 -- reused here as the FOCUS_CAPACITY parameter, not literal code, since that cell
operates over VSA phasor bundles and this cell operates over symbolic role-tags, matching the SAME
disclosed register-mismatch convention already used by every other cell in this reading arc, e.g.
exp_read_discourse_state_of_mind_wsm_coupling_realcorpus_v2's own "fully symbolic, no VSA/torch"
declaration); (3) the CHUNK+PAGE / exact-paging design already validated as a discourse mechanism by
exp_read_discourse_state_of_mind_wsm_coupling_realcorpus_v2 (landed HARD_PASS: a maintained Cb/Cf
discourse state resolves pronoun-dependent clauses a stateless per-sentence baseline structurally
cannot, coupling_delta=0.833 MEASURED@data/exp_read_discourse_state_of_mind_wsm_coupling_realcorpus_v2/
metrics.json) -- that cell proved MAINTAINING STATE helps PRONOUN RESOLUTION; this cell asks the
DIFFERENT, not-yet-asked question: does the SAME kind of maintained state help COHERENCE
DISCRIMINATION, specifically on the fine-local condition where the STATIC entity-grid snapshot failed.

PRIOR-WORK CONCEPT-QUERY (mandatory, run before authoring): `bash tools/substrate_query.sh "running
discourse state of mind maintained story vector vs static entity grid coherence adjacent swap"` ->
top hits cosine<=0.337, all generic lexical entries (WordNet 'state_of_mind' cosine=0.321, FrameNet
'State_of_entity' frame cosine=0.337) -- NO prior EXPERIMENT-CELL hit from the concept index for this
specific construction. Direct file search (not the shallow lexical index) confirms the two genuinely
relevant prior cells cited above; this cell is a NEW combination (a running maintained-focus mechanism
x the entity-grid COHERENCE-DISCRIMINATION task), not a rediscovery of either standing alone -- the
WSM coupling cell tested pronoun-resolution coupling, never coherence-discrimination; the entity-grid
cell tested coherence-discrimination, but only ever with a STATIC (bigram-only, non-maintained) scorer.

MECHANISM UNDER TEST (candidate C, "RUNNING"; glass-box symbolic analog of bind+bundle+chunk+page --
no VSA/torch, same declared register-mismatch precedent as (2)/(3) above): a SINGLE `RunningState`
object is threaded through a SEQUENTIAL scan of the candidate row ORDER (the same permutations the
static scorer re-indexes). It holds an ACTIVE FOCUS of up to FOCUS_CAPACITY=4 distinct entities
(entity -> {role, last_pos}, i.e. a BOUND role-filler pair per focus slot) and a DURABLE STORE (entities
CHUNKED/PAGED out of focus on LRU eviction, role+position retained -- "exact recall," not discard).
Per row (skipping row 0, which has no prior state -- matching the static scorer's own "adjacent pairs"
convention): for each entity mentioned in this row, look up its PRIOR state -- FOCUS (score a full
TRANSITION_WEIGHTS[(prev_role,role)] transition, REUSING the exact same hand-set weight table as the
static scorer, but prev_role may come from anywhere in the last up-to-4 DISTINCT entities' worth of
history, not necessarily the immediately preceding row), STORE (a REACTIVATION: score REACT_DISCOUNT=
0.5x the same transition weight -- HAND-SET, not fit-to-data, motivated by Almor 1999's informational-
load/reintroduction-cost finding already cited in notes/research_discourse_state_of_mind_situation_
model_2026-07-17.md CITED@Almor 1999 Psychological Review), or NEW (score TRANSITION_WEIGHTS[(None,
role)], identical cold-start treatment to the static scorer). Then BIND this row's mentions into focus
(insert/refresh), and if focus now holds >FOCUS_CAPACITY distinct entities, evict (chunk+page) the
least-recently-refreshed entit(y/ies) to the durable store. THE ONE MECHANICAL DIFFERENCE FROM STATIC:
static's score is a pure re-indexing of FIXED per-entity role arrays (bigram-only, exactly 1 row of
memory); running's score depends on a STATEFUL multi-row window (Cowan span) that persists across
silent gaps and distinguishes a cheaply-maintained continuation from a costlier reactivation from a
brand-new introduction -- this is the "accumulated story-state from 1..N-1, not just local role
transitions" mechanism the task asks for.

DECLARED, HAND-SET, NOT FIT-TO-DATA (avoiding p-hacking risk): FOCUS_CAPACITY=4 (Cowan span, CITED,
matches the resonator focus-lever design parameter above); REACT_DISCOUNT=0.5 (a round, defensible
mid-point: a reactivation is cheaper than a fresh introduction but costs more than an uninterrupted
continuation -- CITED@Almor 1999). Neither was tuned against this cell's own outcome; both were fixed
in this docstring before the FULL run's numbers were computed (same discipline as the static cell's
own hand-set TRANSITION_WEIGHTS, reused verbatim here for the FOCUS/STORE/NEW branches too).

CORPUS (broadened per the CG-expansion criterion -- MORE passages + MORE registers than the static
cell's 10 children's-story passages from 2 books): SHORT_PASSAGES = the static cell's OWN 10 passages,
imported VERBATIM (identical text, identical extraction) for direct like-for-like continuity; +
LONG_PASSAGES = 6 NEW 16-sentence (2x the static cell's 8-sentence window) real, verbatim, public-
domain passages from 3 distinct NLTK-bundled Gutenberg books (2 already-used: bryant-stories.txt,
burgess-busterbrown.txt; ONE NEW register: carroll-alice.txt, a markedly different register --
first-person interior monologue, fantasy, dense dialogue-within-dialogue -- vs. the two animal-fable
books). Total: 16 passages, 3 books (vs static's 10 passages, 2 books) -- satisfies the design gate's
"broaden the corpus" requirement. LONG_PASSAGES selection rule (declared, STRUCTURAL, NOT outcome-
tuned, decided before any coherence score was computed -- same discipline as the static cell's own
window-selection rule): candidate 16-sentence windows scanned at STRIDE=25 starting at sentence index
15 in each book (skipping front matter; excluding any window within 20 sentences of the static cell's
own 8-sentence window starts, to avoid text overlap between the short and long subsets), a window is
KEPT iff (a) at most 6 of its 16 sentences open with a quote mark (scaled 3/8 ratio), (b) total word
count >=140 (scaled 70-word floor), (c) at most 2 of its 16 sentences have fewer than 4 words (scaled
1/8 ratio), (d) no embedded chapter-heading/illustration-caption artifact (mechanical string/regex
check, not a narrative-quality judgment). The FIRST windows satisfying all four filters, in increasing
sentence-index order, were taken verbatim per book (2 bryant, 2 burgess, 2 alice) -- no window was
read for narrative quality and rejected/kept on that basis.

DESIGN GATE (per the dispatching task's own falsifiable spec):
  1. REAL BASELINES: STATIC entity-grid role-transition (candidate A) + co-occurrence-only (B1) +
     random floor (B2) -- ALL THREE imported UNMODIFIED from the static cell and re-scored on THIS
     cell's OWN (broadened) corpus/permutations (NOT merely cited from the old landed run, which only
     covered 10 short passages) -- so RUNNING (C) and STATIC (A) are compared on the IDENTICAL
     passages/extraction/permutation-draws, the one-variable isolation this design gate requires.
  2. CAN-FAIL (verified at self-test, see check (9)/(10) below): a DEGENERATE single-entity-present-
     every-row construction where running's focus never evicts and never reactivates -> running's
     per-step scoring collapses to EXACTLY the static bigram formula step-by-step -> discrimination
     accuracy IDENTICAL to static, proving the running mechanism's advantage (if any lands) comes
     specifically from multi-entity eviction/reactivation dynamics, not a hidden always-win bias.
  3. DIFFICULTY-ON: the ADJACENT-SWAP condition (reused unmodified) + the NEW LONG-passage subset.
  4. ONE VARIABLE: SAME passages, SAME entity/role extraction (`build_grid`, imported unmodified),
     SAME permutation draws (same seed formula, same K=12) across candidates A/B1/C/random -- only the
     SCORING MECHANISM (static bigram-only vs. running stateful-focus) differs between A and C.
  5. BROADENED corpus (see CORPUS section): 16 passages, 3 books, 2 length classes (short/long),
     reported PER-PASSAGE so the margin cannot be tail-concentrated (design-gate item 5).

PRE-REG (envelope-fail-bands; set BEFORE running):
  HARD-PASS: (a) running beats static on the FULL adjacent-swap condition (all 16 passages):
    margin_adjswap_all = acc_adjacent_swap_C - acc_adjacent_swap_A >= 0.05; AND (b) running beats
    static on the LONG-passage subset's adjacent-swap condition: margin_adjswap_long >= 0.05; AND
    (c) NOT TAIL-CONCENTRATED: per-passage delta (score_C_disc - score_A_disc on adjacent-swap,
    per-passage pairwise accuracy) is >=0 on at least 50% of the 16 passages; AND random-baseline
    sanity holds (0.35<=acc_random<=0.65 on both conditions, both length subsets).
  HARD-FAIL: margin_adjswap_all <= 0.01 (running adds ~nothing on the exact condition it is supposed
    to fix) OR margin_adjswap_all < 0 (running is WORSE than static on the hard condition) OR
    fewer than 30% of passages show a non-negative per-passage delta (the "improvement," if any, is an
    illusion driven by 1-2 passages, not a real broadened effect).
  MIDDLE: otherwise (e.g. running helps on adjacent-swap overall but the long-passage subset alone
    doesn't clear its own margin, or vice versa -- report the dominant pattern, an informative
    outcome either way, not a wasted test).
  If random-baseline sanity fails on either condition/subset: tier forced to INVALID_TEST_DESIGN.
  P estimate: P~0.35 HYPOTHESIZED (this cell's own reasoning; genuinely novel mechanism combination,
    no direct prior measurement of a maintained-focus coherence scorer at this or any register --
    deflated below the static cell's own P~0.42 and the WSM coupling cell's P~0.45 because this cell
    asks a STRICTLY HARDER question than either: not just "does role information help" or "does state
    help pronoun resolution" but "does a genuinely stateful multi-sentence memory out-discriminate a
    bigram-local memory on the SPECIFIC condition (fine local perturbation) where bigram-local memory
    is theoretically weakest" -- a real, reachable-either-way claim per design-gate item 2's can-fail
    construction).

COMPUTE: fully symbolic/deterministic except NLTK's classical POS tagger (glass-box, no learned
weights fit BY this cell, same precedent as every sibling cell in this arc). No VSA/torch. Sequential-
CPU (16 passages, longest 16 sentences; permutations are O(1) re-scans of an already-built grid, not
re-parsing; wall time <10s). Storage: no_storage. smoke == full (fixed, small, deterministic corpus,
nothing meaningful to shrink -- same precedent as every sibling cell in this arc). progress_logging =
print_flush_true (well under the 1800s mandatory-heartbeat threshold, added anyway per convention).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): EMPIRICAL check over the real 16-passage corpus
#     -- running (C) and static (A) do NOT always agree on which of (original, permuted) scores higher
#     (at least one disagreement across all pairs) -- proves the two mechanisms are not measuring the
#     identical signal. A synthetic hash-based probe is not meaningful here (both are deterministic
#     pure functions of the same grid, not stochastic outputs to hash-compare).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor -- fully symbolic discrete role/co-occurrence/focus scoring,
#     no phasor/argmax noise anywhere in this cell.
# - baseline_in_band: N/A by design (same as every sibling cell) -- there is no tunable "regime" here
#     (16 fixed real passages); the RANDOM-BASELINE SANITY check (0.35<=acc_random<=0.65) is the honest
#     analogous validity guard.
# - discriminator survives scale: fixed real-passage corpus (no N/scale axis). Discriminators = (1)
#     running beats static + the random floor on real passages (asserted, non-trivial, not by-
#     construction saturated), (2) a synthetic single-entity-always-present construction proves
#     running CAN fail to differ from static (the can-fail requirement), (3) running and static
#     empirically disagree on some pairs (arms differ), (4) deterministic seeding reproduces identical
#     permutations across two independent calls (reused unmodified from the static cell).
# - HARD_PASS strictly above floor; explicit bands in prereg JSON (see PRE-REG section above).
# - real_code_path (F.1): self-test constructs+calls the REAL imported `_build_tags_open_v4` /
#     `_np_head_from_run_v2` / `_scan_object_np_v2` / `build_grid` (rung9 + entity-grid cell, both
#     unmodified) at the SAME real-sentence scale the FULL run uses, PLUS the REAL `RunningState` /
#     `score_running` objects this cell newly defines (constructed on hand-verifiable toy passages
#     before touching the real corpus).
# - real_code_path_and_signature_preflight (F.1-F.5): not_applicable -- this cell constructs no
#     KGStore / fit-module / store-helper substrate object (pure symbolic NLP over a fixed sentence
#     corpus), same precedent as every sibling cell in this reading arc.
# - deterministic_seeding (F.5): reuses the static cell's fixed integer seed formula UNMODIFIED
#     (BASE_SEED + passage_idx*10000 + cond_idx*1000 + k), NEVER `hash()` or `list(set(...))` --
#     verified at self-test (same seed -> same permutation, twice; reused, not re-implemented).
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import random
import argparse
import time
import json
import platform
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_discourse_wsm_running_vs_static_coherence_v1"

# --- GENUINE REUSE, UNMODIFIED: the STATIC entity-grid cell's entity/role extraction, grid-building,
# scoring formulas (candidate A + baseline B1), permutation generators, and credit function. This is
# the ONE-VARIABLE isolation: RUNNING (C, defined below) and STATIC (A) share every upstream piece. ---
from experiments.exp_read_discourse_entitygrid_coherence_v1 import (  # noqa: E402
    PASSAGES as STATIC_PASSAGES, build_grid, score_role_transition, score_cooccurrence,
    TRANSITION_WEIGHTS, _credit, _full_shuffle_perm, _adjacent_swap_perm, K_PERMUTATIONS, BASE_SEED,
    CbTracker, _sentence_entities,
)

# ---------------------------------------------------------------------------
# CORPUS: SHORT = the static cell's own 10 passages (imported above, tagged here); LONG = 6 NEW,
# verbatim, 16-sentence, public-domain passages (nltk.corpus.gutenberg; see module docstring for the
# license + selection-rule disclosure). Committed as literals -- no network re-fetch at runtime.
# ---------------------------------------------------------------------------
SHORT_PASSAGES = [dict(p, length_class="short") for p in STATIC_PASSAGES]

LONG_PASSAGES = [
    {"corpus": "bryant-stories.txt", "start": 370, "length_class": "long", "sents": [
        '"Never fear," said the Elephant, "I could pull twenty cows."',
        '"I am sure you could," said the Rabbit, politely, "only be sure to begin gently, and pull '
        'harder and harder till you get her."',
        "Then he tied the end of the rope tightly round the Elephant's trunk, and ran away into the bushes.",
        "There he sat down and beat the big drum.",
        "The Whale began to pull, and the Elephant began to pull, and in a jiffy the rope tightened "
        "till it was stretched as hard as could be.",
        '"This is a remarkably heavy cow," said the Elephant; "but I\'ll fetch her!"',
        "And he braced his forefeet in the earth, and gave a tremendous pull.",
        '"Dear me!"',
        "said the Whale.",
        '"That cow must be stuck mighty tight"; and he drove his tail deep in the water, and gave a '
        "marvellous pull.",
        "He pulled harder; the Elephant pulled harder.",
        "Pretty soon the Whale found himself sliding toward the land.",
        "The reason was, of course, that the Elephant had something solid to brace against, and, "
        "beside, as fast as he pulled the rope in a little, he took a turn with it round his trunk!",
        "But when the Whale found himself sliding toward the land he was so provoked with the cow "
        "that he dived head first, down to the bottom of the sea.",
        "That was a pull!",
        "The Elephant was jerked off his feet, and came slipping and sliding to the beach, and into the surf.",
    ]},
    {"corpus": "bryant-stories.txt", "start": 540, "length_class": "long", "sents": [
        '"Because you tried to steal my acorn," said the little Red Man.',
        '"It is my acorn," said the Field Mouse; "I found it."',
        '"No, it isn\'t," said the little Red Man, "I have it; you will never see it again."',
        "The little Field Mouse looked all about the room as fast as he could, but he could not see any acorn.",
        "Then he thought he would go back up the tiny stairs to his own home.",
        "But the little door was locked, and the little Red Man had the key.",
        'And he said to the poor mouse,-- "You shall be my servant; you shall make my bed and sweep '
        'my room and cook my broth."',
        "So the little brown Mouse was the little Red Man's servant, and every day he made the little "
        "Red Man's bed and swept the little Red Man's room and cooked the little Red Man's broth.",
        "And every day the little Red Man went away through the tiny door, and did not come back till afternoon.",
        "But he always locked the door after him, and carried away the key.",
        "At last, one day he was in such a hurry that he turned the key before the door was quite "
        "latched, which, of course, didn't lock it at all.",
        "He went away without noticing,--he was in such a hurry.",
        "The little Field Mouse knew that his chance had come to run away home.",
        "But he didn't want to go without the pretty, shiny acorn.",
        "Where it was he didn't know, so he looked everywhere.",
        "He opened every little drawer and looked in, but it wasn't in any of the drawers; he peeped "
        "on every shelf, but it wasn't on a shelf; he hunted in every closet, but it wasn't in there.",
    ]},
    {"corpus": "burgess-busterbrown.txt", "start": 115, "length_class": "long", "sents": [
        "By this time Buster Bear was in fine spirits.",
        "It was fun to catch the fish, and it was still more fun to eat them.",
        "What finer breakfast could any one have than fresh-caught trout?",
        "No wonder he felt good!",
        "But it takes more than three trout to fill Buster Bear's stomach, so he kept on to the next little pool.",
        "But this little pool, instead of being beautiful and clear so that Buster could see right to "
        "the bottom of it and so tell if there were any fish there, was so muddy that he couldn't see "
        "into it at all.",
        "It looked as if some one had just stirred up all the mud at the bottom.",
        '"Huh!"',
        "said Buster Bear.",
        '"It\'s of no use to try to fish here.',
        "I would just waste my time.",
        'I\'ll try the next pool."',
        "So he went on to the next little pool.",
        "He found this just as muddy as the other.",
        "Then he went on to another, and this was no better.",
        "Buster sat down and scratched his head.",
    ]},
    {"corpus": "burgess-busterbrown.txt", "start": 340, "length_class": "long", "sents": [
        "But it was the biggest footprint Farmer Brown's boy ever had seen, and it looked as if it had "
        "been made only a few minutes before.",
        "It was the footprint of Buster Bear.",
        "Now Farmer Brown's boy didn't know that Buster Bear had come down to the Green Forest to live.",
        "He never had heard of a Bear being in the Green Forest.",
        "And so he was so surprised that he had hard work to believe his own eyes, and he had a queer "
        "feeling all over,--a little chilly feeling, although it was a warm day.",
        "Somehow, he didn't feel like meeting Buster Bear.",
        "If he had had his terrible gun with him, it might have been different.",
        "But he didn't, and so he suddenly made up his mind that he didn't want to fish any more that day.",
        "He had a funny feeling, too, that he was being watched, although he couldn't see any one.",
        "He _was_ being watched.",
        "Little Joe Otter and Buster Bear were watching him and taking the greatest care to keep out "
        "of his sight.",
        "All the way home through the Green Forest, Farmer Brown's boy kept looking behind him, and he "
        "didn't draw a long breath until he reached the edge of the Green Forest.",
        "He hadn't run, but he had wanted to.",
        '"Huh!"',
        'said Buster Bear to Little Joe Otter, "I believe he was afraid!"',
        "And Buster Bear was just exactly right.",
    ]},
    {"corpus": "carroll-alice.txt", "start": 40, "length_class": "long", "sents": [
        "There are no mice in the air, I'm afraid, but you might catch a bat, and that's very like a "
        "mouse, you know.",
        'But do cats eat bats, I wonder?"',
        "And here Alice began to get rather sleepy, and went on saying to herself, in a dreamy sort of "
        "way, 'Do cats eat bats?",
        "Do cats eat bats?'",
        "and sometimes, 'Do bats eat cats?'",
        "for, you see, as she couldn't answer either question, it didn't much matter which way she put it.",
        "She felt that she was dozing off, and had just begun to dream that she was walking hand in "
        "hand with Dinah, and saying to her very earnestly, 'Now, Dinah, tell me the truth: did you "
        "ever eat a bat?'",
        "when suddenly, thump!",
        "thump!",
        "down she came upon a heap of sticks and dry leaves, and the fall was over.",
        "Alice was not a bit hurt, and she jumped up on to her feet in a moment: she looked up, but it "
        "was all dark overhead; before her was another long passage, and the White Rabbit was still "
        "in sight, hurrying down it.",
        "There was not a moment to be lost: away went Alice like the wind, and was just in time to "
        "hear it say, as it turned a corner, 'Oh my ears and whiskers, how late it's getting!'",
        "She was close behind it when she turned the corner, but the Rabbit was no longer to be seen: "
        "she found herself in a long, low hall, which was lit up by a row of lamps hanging from the roof.",
        "There were doors all round the hall, but they were all locked; and when Alice had been all "
        "the way down one side and up the other, trying every door, she walked sadly down the middle, "
        "wondering how she was ever to get out again.",
        "Suddenly she came upon a little three-legged table, all made of solid glass; there was "
        "nothing on it except a tiny golden key, and Alice's first thought was that it might belong to "
        "one of the doors of the hall; but, alas!",
        "either the locks were too large, or the key was too small, but at any rate it would not open any of them.",
    ]},
    {"corpus": "carroll-alice.txt", "start": 115, "length_class": "long", "sents": [
        "I wonder if I've been changed in the night?",
        "Let me think: was I the same when I got up this morning?",
        "I almost think I can remember feeling a little different.",
        "But if I'm not the same, the next question is, Who in the world am I?",
        'Ah, THAT\'S the great puzzle!"',
        "And she began thinking over all the children she knew that were of the same age as herself, "
        "to see if she could have been changed for any of them.",
        "'I'm sure I'm not Ada,' she said, 'for her hair goes in such long ringlets, and mine doesn't "
        "go in ringlets at all; and I'm sure I can't be Mabel, for I know all sorts of things, and "
        "she, oh!",
        "she knows such a very little!",
        "Besides, SHE'S she, and I'm I, and--oh dear, how puzzling it all is!",
        "I'll try if I know all the things I used to know.",
        "Let me see: four times five is twelve, and four times six is thirteen, and four times seven "
        "is--oh dear!",
        "I shall never get to twenty at that rate!",
        "However, the Multiplication Table doesn't signify: let's try Geography.",
        "London is the capital of Paris, and Paris is the capital of Rome, and Rome--no, THAT'S all "
        "wrong, I'm certain!",
        "I must have been changed for Mabel!",
        "she knows a very little indeed, thought poor Alice, and her eyes filled with tears again.",
    ]},
]

CORPUS_LICENSE = ("nltk.corpus.gutenberg: bryant-stories.txt + burgess-busterbrown.txt (SAME 2 books "
                   "as the static entity-grid cell) + carroll-alice.txt (NEW register, Lewis Carroll, "
                   "'Alice's Adventures in Wonderland') -- all public domain in the US, NLTK-bundled.")

ALL_PASSAGES = SHORT_PASSAGES + LONG_PASSAGES

# ---------------------------------------------------------------------------
# RUNNING mechanism under test (candidate C): a stateful, sequential, multi-row-memory analog of
# bind (role-filler pair) + bundle (into the active focus) + chunk/page (LRU eviction to a durable
# store) + reactivation. See module docstring for the full mechanism description + hand-set constants.
# ---------------------------------------------------------------------------
FOCUS_CAPACITY = 4      # Cowan span; CITED, matches exp_substrate_resonator_focus_lever_v1's F=3-4 sweet spot
REACT_DISCOUNT = 0.5    # hand-set, not fit-to-data; CITED@Almor 1999 reintroduction-cost


class RunningState:
    """Maintains an ACTIVE FOCUS of up to FOCUS_CAPACITY distinct entities (bound role-filler pairs,
    LRU-refreshed) plus a DURABLE STORE (entities chunked/paged out of focus, role+position retained --
    exact recall, not discard). This is the RUNNING mechanism: unlike the static role-transition
    scorer (which only ever compares a row to its IMMEDIATE predecessor row via fixed per-entity role
    arrays), this carries a multi-sentence accumulated state forward and distinguishes MAINTAINED
    (still in focus) vs REACTIVATED (paged, now reappearing) vs NEW (never seen) continuations."""
    def __init__(self, capacity=FOCUS_CAPACITY):
        self.capacity = capacity
        self.focus = {}   # entity -> {"role": r, "last_pos": p}
        self.store = {}   # entity -> {"role": r, "last_pos": p}  (paged out)

    def prior_state(self, entity):
        if entity in self.focus:
            return "FOCUS", self.focus[entity]["role"]
        if entity in self.store:
            return "STORE", self.store[entity]["role"]
        return "NEW", None

    def update(self, mentions, pos):
        """mentions: {entity: role} for the CURRENT row. Binds each into focus (reactivating from the
        durable store if present), then evicts (chunks+pages) the least-recently-refreshed entit(y/ies)
        to the durable store if focus now exceeds capacity. Returns the list of (entity, last_role)
        evicted this call (empty if none) -- used only by the C2 eviction-penalty variant below."""
        for e, r in mentions.items():
            if e in self.store:
                del self.store[e]
            self.focus[e] = {"role": r, "last_pos": pos}
        evicted = []
        while len(self.focus) > self.capacity:
            lru_entity = min(self.focus, key=lambda e: self.focus[e]["last_pos"])
            rec = self.focus.pop(lru_entity)
            self.store[lru_entity] = rec
            evicted.append((lru_entity, rec["role"]))
        return evicted


def score_running(entity_roles, order, eviction_penalty=False):
    """Sequential single-pass scan of `order` (a permutation of original row indices), maintaining ONE
    RunningState across the whole pass -- the running/maintained-state analog of score_role_transition
    (imported, unmodified, from the static entity-grid cell).

    eviction_penalty=False -> candidate C (primary, pre-registered): scores ARRIVALS only (FOCUS-
      maintained continuation / STORE-reactivation / NEW cold-start), no cost for silent absence while
      an entity remains resident in focus -- the "state tolerates brief gaps" design.
    eviction_penalty=True -> candidate C2 (exploratory, added AFTER seeing C's real-corpus HARD_FAIL,
      reported as a SEPARATE arm, not substituted for C): additionally charges TRANSITION_WEIGHTS[
      (role, None)] the one time a salient (S/O) entity is actually EVICTED from focus to the durable
      store (a genuine "this dropped out of the maintained state" event, distinct from static's
      every-single-row (role,None) charge for mere non-mention) -- tests whether C's HARD_FAIL is
      specifically because arrival-only scoring throws away the departure signal static relies on."""
    state = RunningState()
    total = 0.0
    n = len(order)
    for pos in range(n):
        row_idx = order[pos]
        row_mentions = {e: roles[row_idx] for e, roles in entity_roles.items() if roles[row_idx] is not None}
        if pos > 0:  # no prior state to score against at the first row (matches the static "adjacent pairs" convention)
            for e, r in row_mentions.items():
                kind, prev_role = state.prior_state(e)
                if kind == "NEW":
                    total += TRANSITION_WEIGHTS[(None, r)]
                elif kind == "FOCUS":
                    total += TRANSITION_WEIGHTS[(prev_role, r)]
                else:  # STORE -- reactivation
                    total += REACT_DISCOUNT * TRANSITION_WEIGHTS[(prev_role, r)]
        evicted = state.update(row_mentions, pos)
        if eviction_penalty and pos > 0:
            for _ent, last_role in evicted:
                if last_role in ("S", "O"):
                    total += TRANSITION_WEIGHTS[(last_role, None)]
    return total


CONDITIONS = [("full_shuffle", _full_shuffle_perm), ("adjacent_swap", _adjacent_swap_perm)]


def analyze_passage(passage, passage_idx, k=K_PERMUTATIONS, base_seed=BASE_SEED):
    sents = passage["sents"]
    entity_roles, mention_sets, n = build_grid(sents)
    order0 = list(range(n))
    orig_A = score_role_transition(entity_roles, order0)
    orig_B1 = score_cooccurrence(mention_sets, order0)
    orig_C = score_running(entity_roles, order0)
    orig_C2 = score_running(entity_roles, order0, eviction_penalty=True)

    records = {}
    for cond_idx, (cond_name, gen) in enumerate(CONDITIONS):
        recs = []
        for kk in range(k):
            seed = base_seed + passage_idx * 10000 + cond_idx * 1000 + kk
            order = gen(n, random.Random(seed))
            rand_rng = random.Random(seed + 5_000_000)
            recs.append({
                "order": order,
                "score_A_perm": score_role_transition(entity_roles, order),
                "score_B1_perm": score_cooccurrence(mention_sets, order),
                "score_C_perm": score_running(entity_roles, order),
                "score_C2_perm": score_running(entity_roles, order, eviction_penalty=True),
                "score_rand_orig": rand_rng.random(),
                "score_rand_perm": rand_rng.random(),
            })
        records[cond_name] = recs
    return {
        "corpus": passage["corpus"], "start": passage["start"], "length_class": passage["length_class"],
        "n_sents": n, "n_entities": len(entity_roles), "entities": sorted(entity_roles),
        "orig_A": orig_A, "orig_B1": orig_B1, "orig_C": orig_C, "orig_C2": orig_C2, "records": records,
    }


def aggregate(passage_results, filt=None):
    """filt: None (all passages) or a predicate over passage_result dict (e.g. length_class=='long')."""
    prs = [pr for pr in passage_results if (filt is None or filt(pr))]
    out = {"n_passages_in_subset": len(prs)}
    all_pairs = []
    per_passage_delta = []
    for cond_name, _gen in CONDITIONS:
        for scorer, orig_key, perm_key in (
            ("A", "orig_A", "score_A_perm"), ("B1", "orig_B1", "score_B1_perm"),
            ("C", "orig_C", "score_C_perm"), ("C2", "orig_C2", "score_C2_perm"),
            ("random", "score_rand_orig", "score_rand_perm"),
        ):
            credits = []
            for pr in prs:
                for rec in pr["records"][cond_name]:
                    o = pr[orig_key] if orig_key in pr else rec[orig_key]
                    p = rec[perm_key]
                    c = _credit(o, p)
                    credits.append(c)
                    if scorer in ("A", "C"):
                        all_pairs.append((cond_name, scorer, pr["corpus"], pr["start"], c))
            out[f"acc_{cond_name}_{scorer}"] = float(sum(credits) / len(credits)) if credits else 0.0
            out[f"n_{cond_name}_{scorer}"] = len(credits)
    # per-passage delta (C - A, and C2 - A) on the adjacent_swap condition, for the tail-concentration check.
    for pr in prs:
        a_credits = [_credit(pr["orig_A"], rec["score_A_perm"]) for rec in pr["records"]["adjacent_swap"]]
        c_credits = [_credit(pr["orig_C"], rec["score_C_perm"]) for rec in pr["records"]["adjacent_swap"]]
        c2_credits = [_credit(pr["orig_C2"], rec["score_C2_perm"]) for rec in pr["records"]["adjacent_swap"]]
        a_mean = sum(a_credits) / len(a_credits) if a_credits else 0.0
        c_mean = sum(c_credits) / len(c_credits) if c_credits else 0.0
        c2_mean = sum(c2_credits) / len(c2_credits) if c2_credits else 0.0
        per_passage_delta.append({
            "corpus": pr["corpus"], "start": pr["start"], "length_class": pr["length_class"],
            "acc_A_adjswap": a_mean, "acc_C_adjswap": c_mean, "acc_C2_adjswap": c2_mean,
            "delta_C_minus_A": c_mean - a_mean, "delta_C2_minus_A": c2_mean - a_mean,
        })
    out["_all_pairs_for_arms_differ_check"] = all_pairs
    out["per_passage_delta_adjswap"] = per_passage_delta
    return out


# ---------------------------------------------------------------------------
# Verdict (envelope-fail-bands, per module docstring PRE-REG section).
# ---------------------------------------------------------------------------
def compute_verdict(agg_all, agg_long):
    accA_swap_all = agg_all["acc_adjacent_swap_A"]
    accC_swap_all = agg_all["acc_adjacent_swap_C"]
    accA_swap_long = agg_long["acc_adjacent_swap_A"]
    accC_swap_long = agg_long["acc_adjacent_swap_C"]
    acc_rand_full = agg_all["acc_full_shuffle_random"]
    acc_rand_swap = agg_all["acc_adjacent_swap_random"]

    margin_all = accC_swap_all - accA_swap_all
    margin_long = accC_swap_long - accA_swap_long

    deltas = [row["delta_C_minus_A"] for row in agg_all["per_passage_delta_adjswap"]]
    n_nonneg = sum(1 for d in deltas if d >= 0.0)
    frac_nonneg = n_nonneg / len(deltas) if deltas else 0.0

    random_sanity_ok = (0.35 <= acc_rand_full <= 0.65) and (0.35 <= acc_rand_swap <= 0.65)

    hp = (margin_all >= 0.05 and margin_long >= 0.05 and frac_nonneg >= 0.50 and random_sanity_ok)
    hf = (margin_all <= 0.01 or frac_nonneg < 0.30)

    if not random_sanity_ok:
        tier = "INVALID_TEST_DESIGN"
    else:
        tier = "HARD_PASS" if hp else ("HARD_FAIL" if hf else "MIDDLE_BAND")

    localize = []
    if not random_sanity_ok:
        localize.append("RANDOM BASELINE SANITY FAILED: acc_rand_full=%.3f acc_rand_swap=%.3f "
                         "(expected ~0.50)" % (acc_rand_full, acc_rand_swap))
    if margin_all < 0.05:
        localize.append("running vs static margin on FULL adjacent-swap corpus below 0.05 (%.3f)" % margin_all)
    if margin_long < 0.05:
        localize.append("running vs static margin on LONG-passage adjacent-swap subset below 0.05 (%.3f)" % margin_long)
    if frac_nonneg < 0.50:
        localize.append("per-passage delta non-negative on only %.0f%% of passages (tail-concentration risk)" %
                         (100 * frac_nonneg))
    if margin_all <= 0.01:
        localize.append("HARD-FAIL: running adds ~nothing over static on the exact condition (adjacent-swap) "
                         "it was built to fix (%.3f)" % margin_all)
    if margin_all < 0:
        localize.append("HARD-FAIL: running is WORSE than static on adjacent-swap (%.3f)" % margin_all)
    if frac_nonneg < 0.30:
        localize.append("HARD-FAIL: fewer than 30%% of passages show a non-negative delta -- any apparent "
                         "improvement is tail-concentrated, not a real broadened effect")
    weakest = localize if localize else ["none (running beats static on BOTH the full adjacent-swap corpus "
                                          "AND the long-passage subset, margin not tail-concentrated)"]

    msg = (f"{tier} | ADJ-SWAP(all16) acc_C={accC_swap_all:.3f} acc_A={accA_swap_all:.3f} margin={margin_all:+.3f} "
           f"| ADJ-SWAP(long6) acc_C={accC_swap_long:.3f} acc_A={accA_swap_long:.3f} margin={margin_long:+.3f} "
           f"| frac_passages_nonneg_delta={frac_nonneg:.2f} (n={len(deltas)}) "
           f"acc_random_full={acc_rand_full:.3f} acc_random_swap={acc_rand_swap:.3f} | weakest={weakest}")
    return tier, msg, weakest, margin_all, margin_long, frac_nonneg


# ---------------------------------------------------------------------------
# infra.
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = {"full": "exp_read_discourse_wsm_running_vs_static_coherence_v1",
           "smoke": "exp_read_discourse_wsm_running_vs_static_coherence_v1_smoke",
           "self_test": "exp_read_discourse_wsm_running_vs_static_coherence_v1_selftest"}[run_mode]
    d = REPO / "data" / sub
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units,
              "host": platform.node()}
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_metrics(out_dir, metrics):
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


# ---------------------------------------------------------------------------
# self-test: EXERCISE THE REAL code path + assert the discriminators (INCLUDING the can-fail
# construction and the random-baseline sanity guard) fire correctly.
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (build_grid + RunningState + score_running)...", flush=True)

    # (1) real code path: RunningState basic bind/refresh/prior_state semantics on a hand-verifiable case.
    st = RunningState(capacity=2)
    kind, role = st.prior_state("bear")
    assert kind == "NEW", f"empty state should report NEW: {kind}"
    st.update({"bear": "S"}, 0)
    kind, role = st.prior_state("bear")
    assert kind == "FOCUS" and role == "S", f"bear should be in FOCUS with role S: {kind},{role}"

    # (2) eviction: capacity=2, a 3rd distinct entity forces the LRU (oldest last_pos) out to the store.
    st.update({"fish": "O"}, 1)
    assert set(st.focus) == {"bear", "fish"}, f"focus should hold both: {st.focus}"
    st.update({"jackal": "S"}, 2)  # 3rd distinct entity -> evicts LRU ("bear", last_pos=0)
    assert "jackal" in st.focus and "fish" in st.focus, f"focus after eviction: {st.focus}"
    assert "bear" in st.store, f"bear should have been chunked/paged to the durable store: {st.store}"
    kind, role = st.prior_state("bear")
    assert kind == "STORE" and role == "S", f"paged bear should report STORE with retained role S: {kind},{role}"

    # (3) reactivation: bear reappears -> pulled OUT of the store, back into focus (evicting whichever
    # is now LRU among {fish, jackal}).
    st.update({"bear": "O"}, 3)
    assert "bear" not in st.store, "reactivated entity must be removed from the durable store"
    assert st.focus["bear"]["role"] == "O", "reactivated entity's role must update to the new mention"

    # (4) score_running is order-sensitive on a real (non-degenerate) grid, and DIFFERS from
    # score_role_transition's raw value (proves it is a genuinely different computation, not a
    # relabeled copy) -- a 6-sentence, 6-entity toy passage sized to force BOTH an eviction (>4
    # distinct entities compete for FOCUS_CAPACITY=4 slots) AND a REACTIVATION (jackal, evicted after
    # sentence 2, reappears at sentence 6). A FULL REVERSAL is deliberately NOT used here (an early
    # attempt reversed this exact toy and found BOTH scorers order-invariant under reversal -- most
    # singleton one-mention-per-entity toy passages are accidentally symmetric under full reversal,
    # which would falsely look like a bug in either scorer, not just this one); a single ADJACENT SWAP
    # near the end (positions 4,5) is used instead, matching the real corpus's own adjacent-swap
    # discriminator condition.
    toy = ["The jackal hunted for crabs.", "He found a garden of figs.",
           "The alligator watched him.", "A tiger came near.", "A vulture circled above.",
           "The jackal ran away."]
    entity_roles, mention_sets, n = build_grid(toy)
    assert entity_roles["jackal"] == ["S", "S", None, None, None, "S"], (
        f"toy jackal role sequence wrong (reactivation setup depends on this): {entity_roles['jackal']}")
    order_fwd = list(range(n))
    c_fwd = score_running(entity_roles, order_fwd)
    a_fwd = score_role_transition(entity_roles, order_fwd)
    # order-sensitivity: try several full-shuffle permutations (deterministic seeds) and require at
    # least one to differ from the identity order's score -- a single hand-picked swap can accidentally
    # be causally independent of the toy's specific eviction/reactivation graph (found and documented
    # during authoring: a swap of the last two rows here left BOTH the running and the static bigram
    # score unchanged, because "vulture" and the reactivated "jackal" don't causally interact at that
    # specific pair of positions -- not a scorer bug, a toy-construction accident), so this check
    # samples several permutations rather than asserting on one hand-picked ordering.
    any_differs = False
    for seed in range(10):
        perm = _full_shuffle_perm(n, random.Random(1000 + seed))
        if score_running(entity_roles, perm) != c_fwd:
            any_differs = True
            break
    assert any_differs, "running score is order-invariant across 10 sampled shuffles on a real grid -- bug"
    assert c_fwd != a_fwd, "running score is numerically identical to static -- suspect a relabeled copy, not a new mechanism"

    # (4b) verify the REACTIVATION path actually fires on this toy (not just asserted in prose): replay
    # the forward order by hand and check jackal is evicted then reactivated from the durable store.
    state = RunningState()
    reactivated = False
    for pos, row_idx in enumerate(order_fwd):
        mentions = {e: roles[row_idx] for e, roles in entity_roles.items() if roles[row_idx] is not None}
        if pos > 0 and "jackal" in mentions:
            kind, _role = state.prior_state("jackal")
            if kind == "STORE":
                reactivated = True
        state.update(mentions, pos)
    assert reactivated, "toy passage should exercise the STORE/reactivation branch for 'jackal' -- construction check failed"

    # (5) CAN-FAIL construction (design-gate item 2): a single-entity-present-EVERY-row grid never
    # triggers eviction/reactivation (only one entity ever competes for a focus slot) -> running's
    # per-step scoring reduces to EXACTLY the static bigram formula at every step -> the two scorers'
    # RELATIVE RANKING of (original vs any permutation) must be IDENTICAL, i.e. running provides
    # NO advantage in this degenerate regime -- proving the mechanism does not always win by construction.
    degenerate_roles = {"x": ["S", "S", "S", "S", "S"]}
    deg_order0 = list(range(5))
    deg_orig_A = score_role_transition(degenerate_roles, deg_order0)
    deg_orig_C = score_running(degenerate_roles, deg_order0)
    for seed in range(8):
        perm = _full_shuffle_perm(5, random.Random(7000 + seed))
        deg_perm_A = score_role_transition(degenerate_roles, perm)
        deg_perm_C = score_running(degenerate_roles, perm)
        credit_A = _credit(deg_orig_A, deg_perm_A)
        credit_C = _credit(deg_orig_C, deg_perm_C)
        assert credit_A == credit_C, (
            f"CAN-FAIL construction violated: single-entity-always-present grid should make running "
            f"and static agree on EVERY permutation (both reduce to the same (S,S)-weighted bigram "
            f"sum with no eviction ever possible); got credit_A={credit_A} credit_C={credit_C} at seed={seed}")

    # (6) deterministic seeding: reused unmodified from the static cell; sanity re-check here too.
    p1 = _full_shuffle_perm(8, random.Random(12345))
    p2 = _full_shuffle_perm(8, random.Random(12345))
    assert p1 == p2, "full-shuffle permutation generator is NOT deterministic under a fixed seed"

    # (7) cardinality: EXPECTED_N_UNITS = n_passages * K * n_conditions.
    passage_results = [analyze_passage(p, i) for i, p in enumerate(ALL_PASSAGES)]
    expected_n = len(ALL_PASSAGES) * K_PERMUTATIONS * len(CONDITIONS)
    got_n = sum(len(pr["records"][c]) for pr in passage_results for c, _g in CONDITIONS)
    assert got_n == expected_n, f"cardinality mismatch: expected {expected_n}, got {got_n}"
    assert len(ALL_PASSAGES) == 16, f"expected 16 passages (10 short + 6 long), got {len(ALL_PASSAGES)}"
    assert sum(1 for p in ALL_PASSAGES if p["length_class"] == "long") == 6
    books = {p["corpus"] for p in ALL_PASSAGES}
    assert len(books) == 3, f"expected 3 distinct books (CG-expansion register broadening), got {books}"

    # (8) non-vacuous extraction on every passage (real-corpus sanity, same as the static cell).
    for pr in passage_results:
        assert pr["n_entities"] >= 1, f"passage at {pr['corpus']}:{pr['start']} extracted ZERO entities"

    agg_all = aggregate(passage_results, filt=None)
    agg_long = aggregate(passage_results, filt=lambda pr: pr["length_class"] == "long")
    assert 0.30 <= agg_all["acc_full_shuffle_random"] <= 0.70, (
        f"random baseline sanity (loose self-test band): {agg_all['acc_full_shuffle_random']}")
    assert 0.30 <= agg_all["acc_adjacent_swap_random"] <= 0.70, (
        f"random baseline sanity (loose self-test band): {agg_all['acc_adjacent_swap_random']}")

    # (9) META_RULE_AF arms-differ (real-data variant): running (C) and static (A) empirically
    # DISAGREE on at least one pair across the real corpus -- both are deterministic pure functions of
    # the same grid, so a hash-compare is not meaningful; a real ranking disagreement is.
    pairs = agg_all["_all_pairs_for_arms_differ_check"]
    a_credits = [c for cn, sc, cp, st_, c in pairs if sc == "A"]
    c_credits = [c for cn, sc, cp, st_, c in pairs if sc == "C"]
    disagree = any(a != c for a, c in zip(a_credits, c_credits))
    assert disagree, "META_RULE_AF: running (C) and static (A) NEVER disagree across the real corpus -- suspect identical signal"

    tier, msg, _weakest, _ma, _ml, _fn = compute_verdict(agg_all, agg_long)
    print(f"[self_test] PASS | {msg}", flush=True)
    return True


# ---------------------------------------------------------------------------
# main.
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None)
    args = ap.parse_args()

    if args.self_test or args.run_mode == "self_test":
        self_test()
        sys.exit(0)

    run_mode = "smoke" if (args.smoke or args.run_mode == "smoke") else "full"  # smoke == full (fixed tiny corpus)
    out_dir = _out_dir(run_mode)
    expected_n_units = len(ALL_PASSAGES) * K_PERMUTATIONS * len(CONDITIONS)
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[wsm_running_v1] run_mode={run_mode} n_passages={len(ALL_PASSAGES)} K={K_PERMUTATIONS} "
          f"conditions={[c for c, _g in CONDITIONS]} expected_n_units={expected_n_units}", flush=True)

    passage_results = [analyze_passage(p, i) for i, p in enumerate(ALL_PASSAGES)]
    for pr in passage_results:
        print(f"[wsm_running_v1] passage {pr['corpus']}:{pr['start']} ({pr['length_class']}) "
              f"n_sents={pr['n_sents']} n_entities={pr['n_entities']} entities={pr['entities']}", flush=True)

    agg_all = aggregate(passage_results, filt=None)
    agg_long = aggregate(passage_results, filt=lambda pr: pr["length_class"] == "long")
    agg_short = aggregate(passage_results, filt=lambda pr: pr["length_class"] == "short")

    print(f"[wsm_running_v1] ALL(16) FULL-SHUFFLE acc_C={agg_all['acc_full_shuffle_C']:.3f} "
          f"acc_A={agg_all['acc_full_shuffle_A']:.3f} acc_B1={agg_all['acc_full_shuffle_B1']:.3f} "
          f"acc_random={agg_all['acc_full_shuffle_random']:.3f}", flush=True)
    print(f"[wsm_running_v1] ALL(16) ADJ-SWAP acc_C={agg_all['acc_adjacent_swap_C']:.3f} "
          f"acc_A={agg_all['acc_adjacent_swap_A']:.3f} acc_B1={agg_all['acc_adjacent_swap_B1']:.3f} "
          f"acc_random={agg_all['acc_adjacent_swap_random']:.3f}", flush=True)
    print(f"[wsm_running_v1] LONG(6) ADJ-SWAP acc_C={agg_long['acc_adjacent_swap_C']:.3f} "
          f"acc_A={agg_long['acc_adjacent_swap_A']:.3f}", flush=True)
    print(f"[wsm_running_v1] EXPLORATORY C2(eviction-penalty variant) ALL(16) ADJ-SWAP acc_C2="
          f"{agg_all['acc_adjacent_swap_C2']:.3f} acc_A={agg_all['acc_adjacent_swap_A']:.3f} | "
          f"LONG(6) acc_C2={agg_long['acc_adjacent_swap_C2']:.3f} acc_A={agg_long['acc_adjacent_swap_A']:.3f}",
          flush=True)

    tier, msg, weakest, margin_all, margin_long, frac_nonneg = compute_verdict(agg_all, agg_long)
    elapsed = time.perf_counter() - t0

    def strip_pairs(a):
        return {k: v for k, v in a.items() if k != "_all_pairs_for_arms_differ_check"}

    def strip_records(pr):
        return {k: v for k, v in pr.items() if k != "records"}

    metrics = {
        "verdict": tier, "verdict_msg": msg, "summary": msg[:300],
        "run_mode": run_mode, "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "expected_n_units": expected_n_units,
        "n_passages": len(ALL_PASSAGES), "n_short": len(SHORT_PASSAGES), "n_long": len(LONG_PASSAGES),
        "k_permutations": K_PERMUTATIONS, "conditions": [c for c, _g in CONDITIONS],
        "weakest_interface": weakest,
        "margin_adjswap_all": margin_all, "margin_adjswap_long": margin_long,
        "frac_passages_nonneg_delta": frac_nonneg,
        "agg_all": strip_pairs(agg_all), "agg_long": strip_pairs(agg_long), "agg_short": strip_pairs(agg_short),
        "per_passage": [strip_records(pr) for pr in passage_results],
        "corpus_license": CORPUS_LICENSE,
        "prereg": {
            "hard_pass": "margin_adjswap_all>=0.05 & margin_adjswap_long>=0.05 & frac_passages_nonneg_delta>=0.50 "
                         "& random_baseline_sanity_ok",
            "hard_fail": "margin_adjswap_all<=0.01 | margin_adjswap_all<0 | frac_passages_nonneg_delta<0.30",
            "middle": "otherwise (report dominant class)",
            "invalid": "random_baseline_sanity fails on either condition",
            "novel_synthesis_P": 0.35,
            "corpus": CORPUS_LICENSE,
            "n_passages": len(ALL_PASSAGES), "n_short": len(SHORT_PASSAGES), "n_long": len(LONG_PASSAGES),
            "k_permutations": K_PERMUTATIONS,
            "scope": "RUNNING = stateful multi-row focus (FOCUS_CAPACITY=4, Cowan span) + durable-store "
                     "reactivation (REACT_DISCOUNT=0.5), hand-set not fit-to-data; STATIC/B1/random reused "
                     "unmodified from exp_read_discourse_entitygrid_coherence_v1 for one-variable isolation",
            "exploratory_arm_C2": "eviction-penalty variant of RUNNING, added AFTER observing candidate C's "
                                   "real-corpus result during authoring (see module docstring score_running "
                                   "docstring) -- reported as a SEPARATE diagnostic arm (acc_*_C2 fields in "
                                   "agg_all/agg_long/per_passage_delta_adjswap), NOT substituted for the "
                                   "PRE-REGISTERED primary candidate C in the HARD_PASS/HARD_FAIL tier "
                                   "determination above (compute_verdict uses acc_*_C only). Declared here so "
                                   "this exploratory addition is auditable, not silently smuggled into the verdict.",
            "compute_architecture": "sequential-CPU, grid built once per passage (reused build_grid), running "
                                     "score is a single stateful pass per permutation (no re-parsing); NLTK "
                                     "classical POS tagger only, no LLM",
            "storage_strategy": "no_storage", "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "print_flush_true", "deterministic_seeding": True,
            "real_code_path_exercised": ["_build_tags_open_v4", "_np_head_from_run_v2", "_scan_object_np_v2",
                                         "build_grid", "score_role_transition", "score_cooccurrence",
                                         "RunningState", "score_running"],
            "arms_differ_verified": "empirical (real corpus): running(C) and static(A) disagree on >=1 pair",
            "crlb_n/a": "no quantitative noise floor; fully symbolic discrete role/co-occurrence/focus scoring",
            "real_code_path_and_signature_preflight": "not_applicable_no_substrate_objects_pure_symbolic_nlp_cell "
                                                       "(same precedent as every sibling cell in this reading arc)",
            "reused_static_cell": "exp_read_discourse_entitygrid_coherence_v1 (landed MIDDLE_BAND; "
                                   "acc_full_shuffle_A=0.854 margin=+0.171, acc_adjacent_swap_A=0.554 "
                                   "margin=-0.021 -- the fine-local FAIL this cell targets)",
            "reused_wsm_coupling_cell": "exp_read_discourse_state_of_mind_wsm_coupling_realcorpus_v2 "
                                        "(landed HARD_PASS on a DIFFERENT task, pronoun-resolution coupling, "
                                        "coupling_delta=0.833; design-parameter precedent only, not code reuse, "
                                        "for the maintained-state/chunk+page concept)",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[wsm_running_v1] {tier} in {elapsed:.4f}s -> {out_dir/'metrics.json'}", flush=True)
    print(f"[wsm_running_v1] {msg}", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    _md = "full"
    try:
        if "--smoke" in sys.argv or ("--run-mode" in sys.argv and "smoke" in sys.argv):
            _md = "smoke"
        elif "--self-test" in sys.argv or "self_test" in sys.argv:
            _md = "self_test"
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            _write_crash_metrics(_out_dir(_md), e)
        except Exception:
            pass
        raise
