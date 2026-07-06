# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (structured / flat_bag / scrambled_roles recovered-structure
#     digests AND composite-vector digests hash-distinct per (LEVELS,V,seed) unit).
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb / capacity-feasibility: block-local per-slot cleanup is exact-by-construction on DISJOINT blocks
#     (no cross-slot interference); the host block carries at most 2 superposed codes (noun + EMBED_HOOK,
#     load L=2) which the proven comprehension cell recovers. The quantity that CAN fail (the ENVELOPE
#     cliff) is the per-block V-way argmax as bs = N/(LEVELS*S) SHRINKS with recursion depth (LEVELS grows
#     -> more blocks -> smaller bs -> more spurious cross-code hits). CITED block-local ceiling: native
#     decoder blocklocal_gsbc exact_ordered=1.000 to D<=26 at V<=1024 (bs=8192/26=315)
#     CITED@data/exp_generation_decoder_gsbc_native_blocklocal_v1. crlb_n_a: no closed-form argmax-noise
#     floor blocks the deliverable (disjoint-block recovery has no within-block superposition beyond L<=2).
# - baseline_in_band: flat_bag and scrambled_roles are NEGATIVE CONTROLS expected AT CHANCE on STRUCTURE
#     (attachment host chance = 1/N_HOST = 0.5 balanced; tree_exact ~ 0) BY CONSTRUCTION. They are EXEMPT
#     from the AG 0.05<baseline<0.95 in-band gate (HP_SCOPE) and carry ONLY the near-chance BIAS/collapse
#     gate (attachment_acc in [0.35,0.65]) that PROVES the STRUCTURE stressor bites. The MECHANISM arm
#     (structured) is the finding, not a baseline.
# - discriminator survives scale: recursion round-trip measured AT full N=8192 across the FULL LEVELS grid
#     in smoke (smoke reduces the V grid to 2 points, seeds to 1, trials -- NEVER N, NEVER S). Gates FIRE
#     in smoke: (1) at the anchor (LEVELS=2,V=256) structured attachment_acc - control attachment_acc >=
#     GAP_MIN (structure recovered where a bag is blind); (2) control attachment_acc near chance 0.5 at
#     every embedding config; (3) structural_audit: flat_bag composite is provably order/level-blind.
# - HARD_PASS strictly above floor (structured tree_exact >= 0.80 [floor 0.50, band_width 0.50, +5%=0.525]
#     at the anchor AND attachment_acc >= 0.90 [chance 0.5] AND terminal_perslot >= 0.90; gap >= GAP_MIN;
#     cv <= CV_MAX at the anchor; envelope reaches LEVELS>=2 at V>=256).
# - HP_SCOPE: chain-grade HP gates (tree_exact/attachment/terminal floors + gap + cv) apply ONLY to the
#     structured arm. flat_bag / scrambled_roles carry ONLY the near-chance collapse gate.
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
#
# GRAMMAR -- recursive/nested constituency + function-word STRUCTURAL OPERATORS via block-local SBC algebra
# ========================================================================================================
# WHY (Director scope: the LAST unbuilt language layer -- the "long pole"):
#   The other 3 language layers are done AS MECHANISMS: LEXICON (177,899-name pool reused), MORPHOLOGY
#   (exp_lex_wug_test_cpu_v1 WUG rule HARD_PASS), SYNTACTIC COMBINATORICS (block-local frame-slot decoder,
#   exact-ordered=1.000 to D<=26). What is UNBUILT (research_language_ingest_glassbox_scoping_2026-07-05.md,
#   Layer C): FUNCTION WORDS (closed class: determiners, prepositions, conjunctions, auxiliaries,
#   complementizers) handled AS STRUCTURAL OPERATORS, plus RECURSIVE/NESTED grammatical structure
#   (embedded clauses) beyond a single fixed SVO frame. No cell anywhere in the corpus attempts it.
#
# WHAT THIS IS (USER-LOCKED FRAMING -- do NOT over-claim): a NARROW, structured, glass-box demonstration
#   that bounded-depth RECURSIVE constituency + closed-class function-word OPERATORS round-trip through the
#   substrate's block/SBC algebra, and that a flat (bag) / scrambled (structure-destroyed) control provably
#   CANNOT. This is the grammatical-STRUCTURE primitive. It is NOT a language model, NOT fluent English,
#   NOT raw-text prediction, and NOT drawn from real language corpora (synthetic clean sparse-bipolar codes
#   only; NO KB referent). It is Stage-3 compositional structure, NOT Stage-4 LM equivalence.
#
# THE ALGEBRA (block-local sparse SBC; reuses the proven decoder + comprehension mechanisms):
#   * A CLAUSE NODE has S=8 typed structural slots (fixed template):
#       0 COMP   (complementizer: closed-class OPERATOR that OPENS an embedded clause; empty in matrix clause)
#       1 DET_S  (determiner on the subject NP; closed class)
#       2 SUBJ   (content noun)
#       3 AUX    (auxiliary; closed class)
#       4 VERB   (content verb)
#       5 PREP   (preposition heading a PP; closed class)
#       6 DET_O  (determiner on the object NP; closed class)
#       7 OBJ    (content noun)
#     => 5 function slots covering 4 closed classes (COMP, DET, AUX, PREP) + 3 content slots per clause.
#   * RECURSION (banded): N=8192 partitioned into LEVELS*S disjoint blocks (bs = N/(LEVELS*S)). Clause node
#     at recursion level L occupies band L (blocks [L*S, (L+1)*S)). An embedded clause (L>=1) is introduced
#     by a COMP operator and ATTACHES to a host content slot (SUBJ or OBJ) of its parent clause (L-1). The
#     encoder is a RECURSIVE function over the constituency tree; the SAME clause template applies at each
#     level (the recursion), linked by the COMP operator + the attachment hook (the structural relation).
#   * FUNCTION WORDS ARE OPERATORS, NOT CONTENT: function slots decode against a SEPARATE closed-class
#     codebook partitioned BY TYPE (selectional restriction). The COMP operator's PRESENCE (block energy)
#     is what the decoder uses to DECIDE whether band L is an embedded clause -- so the complementizer
#     literally GATES the recursion (tested: embed_detection, no hallucinated nesting when COMP absent).
#   * ATTACHMENT (the recursion carrier, structurally relational -- a bag cannot fake it): the embedded
#     clause's host is marked by superposing a fixed EMBED_HOOK code into the HOST content block (load L=2
#     with the host noun). Decoding attachment = argmax over candidate host slots of corr(block, HOOK).
#     In a FLAT bag all blocks merge -> HOOK correlation equal across candidates -> attachment at chance.
#
# ARMS (PAIRED -- same trees + same codebooks across arms, per feedback_paired_trials_mandatory):
#   structured      (PRIMARY, mechanism): banded block-local typed-slot encode + recursive/banded decode.
#   flat_bag        (negative control, live): ALL slot codes (+hooks) superposed into ONE band (block 0);
#                       per-slot decode reads block 0 -> no positional/level separation -> collapses.
#   scrambled_roles (negative control, live): tokens placed into a RANDOM permutation of the (level,slot)
#                       -> block address at ENCODE; decode uses the TRUE map -> mis-addressed -> collapses.
#
# METRICS (report SEPARATELY per Fix #28 -- never collapse to one aggregate; PAIRED across arms):
#   terminal_perslot    = mean over filled slots of P[recovered token == true]  (content + function)
#   function_perslot    = mean over function slots of P[recovered function word == true]  (closed-class)
#   embed_detection_acc = P[correctly detect embedding present/absent via COMP-operator block energy]
#   attachment_acc      = P[embedded-clause host (SUBJ/OBJ) recovered]  (chance 1/N_HOST=0.5; PRIMARY discrim)
#   tree_exact          = P[entire bracketed tree recovered: all terminals + all embed-detections + all
#                           attachments]  (HEADLINE; chance ~ 0 for controls)
#
# Reuses (native block-local sparse construction + role-typed matched filter; do NOT rerun cited ceilings):
#   experiments/exp_generation_decoder_gsbc_native_blocklocal_v1.py  (Stage A/B/C block-local decode)
#   experiments/exp_comprehension_envelope_superposition_vocab_v1.py (role-typed partition-restricted decode)
#   experiments/exp_morph_ruleset_wug_v2_cpu.py                      (morphology layer; sibling)
#
# NO KB_REFERENT declared (synthetic clean sparse-bipolar codes only). ASCII-only. CPU default (matched
# filter + block-argmax; numpy only; no LLM, no GPU). Read-only on substrate.
# Run: python experiments/exp_grammar_recursive_function_word_blocklocal_v1.py [--self-test | --smoke]
#      (bare / runner-injected HDLAB_RUN_MODE=full -> full)

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)  # 17. PRINT-PROGRESS flush on newline

DEVICE = "cpu"  # matched-filter + block-argmax; numpy only (no torch needed)

ANCHOR_NAME = "grammar_recursive_function_word_blocklocal_v1"
REPO = Path(__file__).resolve().parents[1]

N_DIM = 8192          # substrate compositional default (all modes; never reduced)
F_SPARSE = 0.02       # block-local code sparsity fraction (matches proven decoder/comprehension cells)

# ---- Clause template: S=8 typed structural slots ----
SLOT_COMP, SLOT_DET_S, SLOT_SUBJ, SLOT_AUX, SLOT_VERB, SLOT_PREP, SLOT_DET_O, SLOT_OBJ = range(8)
S_SLOTS = 8
CONTENT_SLOTS = (SLOT_SUBJ, SLOT_VERB, SLOT_OBJ)         # decode vs the content codebook
HOST_SLOTS = (SLOT_SUBJ, SLOT_OBJ)                       # an embedded clause attaches to SUBJ or OBJ
N_HOST = len(HOST_SLOTS)                                 # attachment chance = 1/N_HOST = 0.5
# function slot -> closed-class TYPE name (selectional-restriction partition)
FUNC_SLOT_TYPE = {SLOT_COMP: "COMP", SLOT_DET_S: "DET", SLOT_AUX: "AUX",
                  SLOT_PREP: "PREP", SLOT_DET_O: "DET"}
FUNC_SLOTS = tuple(sorted(FUNC_SLOT_TYPE))               # (COMP, DET_S, AUX, PREP, DET_O)
FUNC_TYPES = ("COMP", "DET", "AUX", "PREP", "CONJ")      # full closed class (CONJ reserved for extension)
V_FUNC = 8            # closed-class entries PER TYPE (small, non-productive -- the point of "closed class")

SEEDS = (7, 13, 19)

# ---- Envelope grid axes (recursion depth LEVELS x content vocab V) ----
LEVELS_GRID_FULL = [1, 2, 3]                 # 1=flat clause (no embedding); 2=one embedding (ANCHOR); 3=center-embed
V_GRID_FULL = [64, 256, 1024]                # content vocab per clause
# Boundary MAP probes (ungated; trace the bs-shrink recursion cliff). MEASURED@this-cell (seed7, 60 trials):
#   L4(bs256)=1.000 L8(bs128)=0.983 L12(bs85)=0.500 L16(bs64,k=1)=0.067 -- exact to depth-6, wall at bs<=85.
BOUNDARY_FULL = [(4, 256), (8, 256), (12, 256), (16, 256)]
LEVELS_GRID_SMOKE = [1, 2, 3]                # smoke keeps FULL LEVELS grid at full N (discriminator survives scale)
V_GRID_SMOKE = [64, 256]                     # smoke reduces V grid to 2 points (256 = anchor V)

ANCHOR = (2, 256)                            # LEVELS=2 (one embedding), V=256 -- the HARD_PASS corner
EASY = (2, 64)                               # discriminator-fires corner (structured >> control)

# Pre-registered bands (HYPOTHESIZED@this-cell; verified against smoke before FULL).
#   Primary discriminator = attachment_acc (structured vs control; chance 1/N_HOST = 0.5).
#   Headline = tree_exact (full bracketed round-trip; chance ~ 0 for controls).
FLOOR_TREE = 0.80          # HARD_PASS: structured tree_exact at the anchor (floor 0.50; strict-above +5%)
FLOOR_ATTACH = 0.90        # HARD_PASS: structured attachment_acc at the anchor (chance 0.5)
FLOOR_TERM = 0.90          # HARD_PASS: structured terminal_perslot at the anchor
GAP_MIN = 0.35             # discriminator: structured attachment_acc - max(control attachment_acc) at anchor
TREE_GAP_MIN = 0.60        # discriminator: structured tree_exact - max(control tree_exact) at anchor
CTRL_LO, CTRL_HI = 0.35, 0.65   # BIAS gate: control attachment_acc must stay near chance 0.5 at every embed config
CV_MAX = 0.15              # HARD_PASS: cv of structured tree_exact across seeds at the anchor
HF_TREE = 0.30             # HARD_FAIL: structured tree_exact(anchor) <= this -> mechanism cannot round-trip
HF_GAP = 0.15              # HARD_FAIL: attachment gap over control below this -> structure not attributable

ARMS = ["structured", "flat_bag", "scrambled_roles"]

# EMBED-detection threshold: a COMP block with a function code has energy ~ k_comp; empty ~ 0. Threshold at
# half the per-code active count is robust (THEORETICAL: sparse bipolar code has exactly k nonzeros of +/-1
# -> L2 energy == k; empty block energy == 0).
EMBED_ENERGY_FRAC = 0.5


# ============================================================
# Defensive error-checking helpers (13/16)
# ============================================================


def _out_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME")
    return REPO / (f"data/exp_{name}" if name else f"data/exp_{ANCHOR_NAME}")


def _say(msg: str) -> None:
    print(msg, flush=True)


def _write_start_marker(output_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, output_dir / "_start_marker.json")


def _heartbeat(output_dir: Path, unit_idx: int, total_units: int, t0: float, extra=None) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": round(time.perf_counter() - t0, 2),
    }
    if extra:
        row["extra"] = extra
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_metrics_atomic(output_dir: Path, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, output_dir / "metrics.json")  # atomic (META_RULE_AH)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "anchor_name": ANCHOR_NAME,
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
    }
    _write_metrics_atomic(output_dir, diag)


def _digest_ints(int_list) -> str:
    return hashlib.sha256(np.asarray(int_list, dtype=np.int64).tobytes()).hexdigest()


def _digest_arr(arr) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(arr, dtype=np.float32)).tobytes()).hexdigest()


# ============================================================
# Codebooks: synthetic clean sparse-bipolar (content + closed-class function + EMBED_HOOK)
# ============================================================


def _sparse_bipolar(V: int, bs: int, k: int, rng: np.random.Generator) -> np.ndarray:
    """V sparse bipolar codes of length bs, exactly k active +/-1 each. (V, bs) float32."""
    idx = np.stack([rng.choice(bs, size=k, replace=False) for _ in range(V)], axis=0)  # (V, k)
    cb = np.zeros((V, bs), dtype=np.float32)
    rows = np.arange(V)[:, None]
    cb[rows, idx] = (rng.integers(0, 2, size=(V, k)).astype(np.float32) * 2.0 - 1.0)
    return cb


class Codebooks:
    """Per-(LEVELS,V,seed) codebooks. bs = N/(LEVELS*S) shrinks with recursion depth (the cliff axis)."""

    def __init__(self, levels: int, V: int, seed: int):
        self.levels = levels
        self.V = V
        self.n_blocks = levels * S_SLOTS
        self.bs = N_DIM // (levels * S_SLOTS)
        assert self.bs * levels * S_SLOTS <= N_DIM, "block partition overflows N"
        self.k = max(1, int(round(F_SPARSE * self.bs)))
        rng = np.random.default_rng(500000 + seed + 1000 * levels + V)
        self.content = _sparse_bipolar(V, self.bs, self.k, rng)                  # (V, bs)
        # closed-class function codebook, partitioned by TYPE (selectional restriction)
        self.func = {t: _sparse_bipolar(V_FUNC, self.bs, self.k, rng) for t in FUNC_TYPES}
        self.hook = _sparse_bipolar(1, self.bs, self.k, rng)[0]                  # EMBED_HOOK marker (bs,)

    def slot_codebook(self, slot: int) -> np.ndarray:
        if slot in CONTENT_SLOTS:
            return self.content
        return self.func[FUNC_SLOT_TYPE[slot]]

    def slot_vocab(self, slot: int) -> int:
        return self.V if slot in CONTENT_SLOTS else V_FUNC


# ============================================================
# Tree sampling: recursive constituency with COMP-gated embedding + SUBJ/OBJ attachment
# ============================================================


def _sample_trees(levels: int, V: int, trials: int, seed: int):
    """Return a list of trees. Each tree is a dict:
      tokens:   {(L, slot): token_id}  filled slots per level (COMP filled only for embedded levels present)
      hosts:    {L: host_slot}         for L>=1: the parent (L-1) content slot this embedded clause attaches to
      has_embed: {L: bool}             whether band L is an embedded clause present (L>=1); band 0 always True
    Half the trees at LEVELS>=2 are MATRIX-ONLY (embedded bands ABSENT: COMP empty, no hook) so the COMP
    operator's embed-detection is a balanced present/absent test (chance 0.5 for a structure-blind control)."""
    rng = np.random.default_rng(90000 + seed + 1000 * levels + V)
    trees = []
    for t in range(trials):
        # balanced: alternate FULL-depth vs matrix-only when embedding is possible (levels>=2)
        full_depth = True if levels == 1 else (t % 2 == 0)
        max_L = (levels - 1) if full_depth else 0     # deepest embedded band present
        tokens = {}
        hosts = {}
        has_embed = {}
        for L in range(levels):
            present = (L == 0) or (L <= max_L)
            has_embed[L] = present
            if not present:
                continue
            # fill content slots
            for cs in CONTENT_SLOTS:
                tokens[(L, cs)] = int(rng.integers(0, V))
            # fill function slots (closed class). COMP filled only for embedded bands (L>=1).
            for fs in FUNC_SLOTS:
                if fs == SLOT_COMP and L == 0:
                    continue                          # matrix clause has no complementizer
                tokens[(L, fs)] = int(rng.integers(0, V_FUNC))
            # attachment: embedded band L (>=1) attaches to a balanced host slot of parent L-1
            if L >= 1:
                hosts[L] = HOST_SLOTS[rng.integers(0, N_HOST)]
        trees.append({"tokens": tokens, "hosts": hosts, "has_embed": has_embed,
                      "levels": levels, "full_depth": full_depth})
    return trees


# ============================================================
# Encoders (3 arms): structured / flat_bag / scrambled_roles
# ============================================================


def _block_slice(block: int, bs: int):
    return slice(block * bs, (block + 1) * bs)


def _encode_structured(tree, cb: Codebooks, addr=None) -> np.ndarray:
    """Banded block-local encode. addr maps (L,slot)->block index; default = L*S+slot (structured).
    scrambled_roles passes a permuted addr. Hooks are placed in the (L-1) host block for each embedded L."""
    bs = cb.bs
    comp = np.zeros(cb.n_blocks * bs, dtype=np.float32)
    for (L, slot), tok in tree["tokens"].items():
        blk = addr[(L, slot)] if addr is not None else (L * S_SLOTS + slot)
        comp[_block_slice(blk, bs)] += cb.slot_codebook(slot)[tok]
    for L, host in tree["hosts"].items():                # host is a slot of parent level L-1
        blk = addr[(L - 1, host)] if addr is not None else ((L - 1) * S_SLOTS + host)
        comp[_block_slice(blk, bs)] += cb.hook           # EMBED_HOOK superposed on the host noun (load L=2)
    return comp


def _encode_flat_bag(tree, cb: Codebooks) -> np.ndarray:
    """Negative control: superpose ALL slot codes (+hooks) into a SINGLE band (block 0). No positional /
    level separation -> ordered/structural readout collapses. Composite length = n_blocks*bs (block 0 only
    is nonzero) so decode geometry matches the other arms."""
    bs = cb.bs
    comp = np.zeros(cb.n_blocks * bs, dtype=np.float32)
    acc = np.zeros(bs, dtype=np.float32)
    for (L, slot), tok in tree["tokens"].items():
        acc += cb.slot_codebook(slot)[tok]
    for L in tree["hosts"]:
        acc += cb.hook
    comp[_block_slice(0, bs)] = acc
    return comp


def _scramble_addr(levels: int, seed: int):
    """Fixed per-(levels,seed) permutation of the (L,slot)->block address map (NOT identity)."""
    rng = np.random.default_rng(770000 + seed + 1000 * levels)
    keys = [(L, s) for L in range(levels) for s in range(S_SLOTS)]
    blocks = list(range(levels * S_SLOTS))
    perm = blocks[:]
    for _ in range(64):
        rng.shuffle(perm)
        if all(perm[i] != blocks[i] for i in range(len(blocks))):   # derangement -> every address moves
            break
    return {keys[i]: perm[i] for i in range(len(keys))}


# ============================================================
# Decoders (banded block-local) + scoring
# ============================================================


def _decode(comp: np.ndarray, cb: Codebooks, tree, arm: str):
    """Decode a tree from a composite. arm selects which block a slot reads:
      structured      -> block L*S+slot (true banded address)
      flat_bag        -> block 0 for EVERY slot (no separation)
      scrambled_roles -> block L*S+slot (true map) but the composite was encoded under a permuted map
    Returns (rec_tokens{(L,slot):tok}, rec_embed{L:bool}, rec_hosts{L:host_slot})."""
    bs = cb.bs
    levels = cb.levels

    def read_block(L, slot):
        blk = 0 if arm == "flat_bag" else (L * S_SLOTS + slot)
        return comp[_block_slice(blk, bs)]

    # embed detection: band L>=1 present iff its COMP block energy exceeds threshold
    thresh = EMBED_ENERGY_FRAC * cb.k
    rec_embed = {0: True}
    for L in range(1, levels):
        seg = read_block(L, SLOT_COMP)
        rec_embed[L] = bool(float(np.dot(seg, seg)) > thresh)

    # terminals: per (present) slot argmax vs its slot codebook
    rec_tokens = {}
    for L in range(levels):
        if not rec_embed.get(L, False):
            continue
        for slot in range(S_SLOTS):
            if L == 0 and slot == SLOT_COMP:
                continue                              # matrix clause has no COMP
            seg = read_block(L, slot)
            book = cb.slot_codebook(slot)
            rec_tokens[(L, slot)] = int(np.argmax(book @ seg))

    # attachment: for each present embedded band L>=1, which parent host block carries the HOOK
    rec_hosts = {}
    for L in range(1, levels):
        if not rec_embed.get(L, False):
            continue
        corrs = []
        for host in HOST_SLOTS:
            seg = read_block(L - 1, host)
            corrs.append(float(np.dot(cb.hook, seg)))
        rec_hosts[L] = HOST_SLOTS[int(np.argmax(corrs))]
    return rec_tokens, rec_embed, rec_hosts


def _score_tree(tree, rec_tokens, rec_embed, rec_hosts):
    """Return per-tree scores: terminal_perslot, function_perslot, embed_ok, attach frac, tree_exact."""
    # terminal per-slot (over TRUE filled slots)
    true_tok = tree["tokens"]
    n_term = len(true_tok)
    term_hits = sum(1 for k, v in true_tok.items() if rec_tokens.get(k, -1) == v)
    func_keys = [k for k in true_tok if k[1] in FUNC_SLOTS]
    n_func = len(func_keys)
    func_hits = sum(1 for k in func_keys if rec_tokens.get(k, -1) == true_tok[k])

    # embed detection (bands L>=1: present/absent must match)
    levels = tree["levels"]
    embed_ok = all(rec_embed.get(L, False) == tree["has_embed"].get(L, False)
                   for L in range(1, levels)) if levels > 1 else True

    # attachment (over TRUE present embedded bands)
    true_hosts = tree["hosts"]
    n_attach = len(true_hosts)
    attach_hits = sum(1 for L, h in true_hosts.items() if rec_hosts.get(L, -1) == h)

    # tree_exact: all terminals + embed-detection + all attachments correct
    tree_exact = 1.0 if (term_hits == n_term and embed_ok and attach_hits == n_attach) else 0.0
    return {
        "term_hits": term_hits, "n_term": n_term,
        "func_hits": func_hits, "n_func": n_func,
        "embed_ok": 1 if embed_ok else 0,
        "attach_hits": attach_hits, "n_attach": n_attach,
        "tree_exact": tree_exact,
    }


def run_unit(levels: int, V: int, seed: int, trials: int) -> dict:
    cb = Codebooks(levels, V, seed)
    trees = _sample_trees(levels, V, trials, seed)
    scr_addr = _scramble_addr(levels, seed)

    # per-arm accumulators
    acc = {a: {"term_h": 0, "term_n": 0, "func_h": 0, "func_n": 0,
               "embed_h": 0, "embed_n": 0, "attach_h": 0, "attach_n": 0, "exact": 0} for a in ARMS}
    comp_digest = {a: [] for a in ARMS}
    rec_digest = {a: [] for a in ARMS}

    for tree in trees:
        comps = {
            "structured": _encode_structured(tree, cb),
            "flat_bag": _encode_flat_bag(tree, cb),
            "scrambled_roles": _encode_structured(tree, cb, addr=scr_addr),
        }
        for arm in ARMS:
            comp = comps[arm]
            rt, re_, rh = _decode(comp, cb, tree, arm)
            s = _score_tree(tree, rt, re_, rh)
            a = acc[arm]
            a["term_h"] += s["term_hits"]; a["term_n"] += s["n_term"]
            a["func_h"] += s["func_hits"]; a["func_n"] += s["n_func"]
            a["embed_h"] += s["embed_ok"]; a["embed_n"] += 1
            a["attach_h"] += s["attach_hits"]; a["attach_n"] += s["n_attach"]
            a["exact"] += int(s["tree_exact"])
            comp_digest[arm].append(_digest_arr(comp))
            # recovered-structure signature: tokens + embed + hosts flattened deterministically
            sig = [rt.get((L, sl), -1) for L in range(levels) for sl in range(S_SLOTS)]
            sig += [int(re_.get(L, False)) for L in range(levels)]
            sig += [rh.get(L, -1) for L in range(levels)]
            rec_digest[arm].append(_digest_ints(sig))

    out = {"levels": levels, "V": V, "seed": seed, "bs": cb.bs, "k": cb.k, "n_blocks": cb.n_blocks,
           "n_trials": len(trees), "attachment_chance": 1.0 / N_HOST}
    for arm in ARMS:
        a = acc[arm]
        out[arm] = {
            "terminal_perslot": a["term_h"] / max(1, a["term_n"]),
            "function_perslot": a["func_h"] / max(1, a["func_n"]),
            "embed_detection_acc": a["embed_h"] / max(1, a["embed_n"]),
            "attachment_acc": (a["attach_h"] / a["attach_n"]) if a["attach_n"] > 0 else float("nan"),
            "tree_exact": a["exact"] / len(trees),
            "n_attach_total": a["attach_n"],
        }
        out[arm + "_comp_digest"] = _digest_ints(
            [int(x[:8], 16) for x in comp_digest[arm]])   # compress list of hex digests
        out[arm + "_rec_digest"] = _digest_ints([int(x[:8], 16) for x in rec_digest[arm]])
    return out


# ============================================================
# Structural audit: prove flat_bag is provably level/attachment blind (airtight anchor)
# ============================================================


def structural_audit(seed: int = 7) -> dict:
    """Prove that (a) the flat_bag composite is INVARIANT to swapping the attachment host (bag cannot see
    structure), while (b) the structured composite CHANGES; and (c) the block partition is exact/disjoint."""
    levels, V = 2, 64
    cb = Codebooks(levels, V, seed)
    trees = _sample_trees(levels, V, 4, seed)
    # find a full-depth tree with an embedded band
    tree = next(t for t in trees if t["hosts"])
    L = min(tree["hosts"])                              # an embedded band
    other_host = HOST_SLOTS[1] if tree["hosts"][L] == HOST_SLOTS[0] else HOST_SLOTS[0]
    t2 = {"tokens": dict(tree["tokens"]), "hosts": dict(tree["hosts"]),
          "has_embed": dict(tree["has_embed"]), "levels": levels, "full_depth": True}
    t2["hosts"][L] = other_host                        # swap ONLY the attachment host (same tokens)

    bag1 = _encode_flat_bag(tree, cb)
    bag2 = _encode_flat_bag(t2, cb)
    st1 = _encode_structured(tree, cb)
    st2 = _encode_structured(t2, cb)
    bag_invariant = bool(np.array_equal(bag1, bag2))   # flat bag CANNOT see the attachment swap
    structured_differs = bool(not np.array_equal(st1, st2))
    partition_exact = bool(cb.bs * cb.n_blocks <= N_DIM and cb.bs >= 1)
    return {
        "flat_bag_invariant_under_attach_swap": bag_invariant,
        "structured_differs_under_attach_swap": structured_differs,
        "partition_exact_disjoint": partition_exact,
        "bag_blind_to_structure": bool(bag_invariant and structured_differs),
        "attachment_chance": round(1.0 / N_HOST, 4),
    }


# ============================================================
# Config + aggregation + envelope + verdict
# ============================================================


def get_config(mode: str):
    if mode == "selftest":
        return {"trials": 16, "seeds": (7,), "levels_grid": [1, 2], "V_grid": [64, 256], "boundary": []}
    if mode == "smoke":
        return {"trials": 40, "seeds": (7,), "levels_grid": LEVELS_GRID_SMOKE, "V_grid": V_GRID_SMOKE,
                "boundary": []}
    return {"trials": 80, "seeds": SEEDS, "levels_grid": LEVELS_GRID_FULL, "V_grid": V_GRID_FULL,
            "boundary": BOUNDARY_FULL}


def _grid_points(cfg):
    pts = [(L, V) for L in cfg["levels_grid"] for V in cfg["V_grid"]]
    pts += list(cfg["boundary"])
    return pts


def _cv(vals):
    a = np.asarray(vals, dtype=np.float64)
    m = float(a.mean())
    return float(a.std() / m) if m > 0.0 else float("inf")


def _safe_nanmean(vals):
    """np.nanmean without the empty-slice RuntimeWarning when a column is all-nan (LEVELS=1: no attachment)."""
    a = np.asarray(vals, dtype=np.float64)
    finite = a[np.isfinite(a)]
    return float(finite.mean()) if finite.size else float("nan")


def _agg_cell(per_unit, levels, V):
    rows = [u for u in per_unit if u["levels"] == levels and u["V"] == V]

    def arm_col(arm, key):
        return [u[arm][key] for u in rows]

    cell = {"levels": levels, "V": V, "n_seeds": len(rows), "bs": rows[0]["bs"], "k": rows[0]["k"],
            "n_blocks": rows[0]["n_blocks"], "attachment_chance": rows[0]["attachment_chance"]}
    for arm in ARMS:
        cell[arm] = {
            "terminal_perslot_mean": round(float(np.mean(arm_col(arm, "terminal_perslot"))), 4),
            "function_perslot_mean": round(float(np.mean(arm_col(arm, "function_perslot"))), 4),
            "embed_detection_acc_mean": round(float(np.mean(arm_col(arm, "embed_detection_acc"))), 4),
            "attachment_acc_mean": round(_safe_nanmean(arm_col(arm, "attachment_acc")), 4),
            "tree_exact_mean": round(float(np.mean(arm_col(arm, "tree_exact"))), 4),
            "tree_exact_per_seed": [round(x, 4) for x in arm_col(arm, "tree_exact")],
            "tree_exact_cv": round(_cv(arm_col(arm, "tree_exact")), 4) if len(rows) > 1 else 0.0,
        }
    return cell


def _envelope(grid):
    """A cell HOLDS iff structured tree_exact>=FLOOR_TREE AND structured attachment beats BOTH controls by
    GAP_MIN AND both controls near chance. Report the max recursion depth (LEVELS) that holds at V>=256."""
    holds = {}
    for (L, V), c in grid.items():
        st, fb, sc = c["structured"], c["flat_bag"], c["scrambled_roles"]
        ctrl_attach_max = max(fb["attachment_acc_mean"], sc["attachment_acc_mean"])
        gap = st["attachment_acc_mean"] - ctrl_attach_max
        ctrl_ok = all(CTRL_LO <= x["attachment_acc_mean"] <= CTRL_HI for x in (fb, sc)) if L >= 2 else True
        holds[(L, V)] = bool(st["tree_exact_mean"] >= FLOOR_TREE and gap >= GAP_MIN and ctrl_ok)
    embed_levels_at_v256 = [L for (L, V) in holds if V >= 256 and L >= 2 and holds[(L, V)]]
    return {
        "holds_surface": {f"L{L}_V{V}": holds[(L, V)] for (L, V) in sorted(holds)},
        "max_recursion_depth_at_Vge256": max(embed_levels_at_v256) if embed_levels_at_v256 else 0,
        "n_cells_hold": int(sum(holds.values())),
        "n_cells_total": len(holds),
        "anchor_holds": holds.get(ANCHOR, False),
    }


def classify(mode, audit, grid, env, n_units, exp_units, boundary_pts=frozenset()):
    if n_units < exp_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: {n_units}/{exp_units} units")

    # embedding configs (L>=2) for control-near-chance BIAS gate. Boundary MAP points (deep recursion,
    # ungated capability map) are EXCLUDED: at tiny bs the control tie-break + finite samples make control
    # attachment high-variance, and a deep-map point must not gate the anchor finding.
    embed_cells = [(k, c) for k, c in grid.items() if k[0] >= 2 and k not in boundary_pts]
    ctrl_out = []
    for (L, V), c in embed_cells:
        for arm in ("flat_bag", "scrambled_roles"):
            a = c[arm]["attachment_acc_mean"]
            if not (CTRL_LO <= a <= CTRL_HI):
                ctrl_out.append((arm, L, V, round(a, 3)))

    easy = grid[EASY]
    easy_gap = (easy["structured"]["attachment_acc_mean"]
                - max(easy["flat_bag"]["attachment_acc_mean"],
                      easy["scrambled_roles"]["attachment_acc_mean"]))
    anc = grid.get(ANCHOR)

    def cell_str(tag, c):
        return (f"{tag} L{c['levels']}V{c['V']}(bs={c['bs']}): structured tree_exact="
                f"{c['structured']['tree_exact_mean']:.3f} attach={c['structured']['attachment_acc_mean']:.3f} "
                f"term={c['structured']['terminal_perslot_mean']:.3f} func="
                f"{c['structured']['function_perslot_mean']:.3f} embed="
                f"{c['structured']['embed_detection_acc_mean']:.3f} | flat_bag tree_exact="
                f"{c['flat_bag']['tree_exact_mean']:.3f} attach={c['flat_bag']['attachment_acc_mean']:.3f} | "
                f"scrambled tree_exact={c['scrambled_roles']['tree_exact_mean']:.3f} attach="
                f"{c['scrambled_roles']['attachment_acc_mean']:.3f}")

    diag = (f"ENVELOPE: max_recursion_depth@V>=256={env['max_recursion_depth_at_Vge256']}, cells_hold="
            f"{env['n_cells_hold']}/{env['n_cells_total']}; {cell_str('ANCHOR', anc) if anc else 'ANCHOR n/a'}; "
            f"{cell_str('EASY', easy)}")

    # BIAS: flat_bag must be provably structure-blind (attachment-swap invariant), structured must change
    if not audit["bag_blind_to_structure"]:
        return ("BLOCK_DISPATCH_BIAS_BAG_NOT_BLIND",
                f"flat_bag composite is NOT invariant to an attachment-host swap (bag_invariant="
                f"{audit['flat_bag_invariant_under_attach_swap']}, structured_differs="
                f"{audit['structured_differs_under_attach_swap']}): the STRUCTURE stressor does not bite. {diag}")

    # BIAS: controls must sit near chance on attachment at every embedding config
    if ctrl_out:
        return ("BLOCK_DISPATCH_BIAS_CTRL_NOT_AT_CHANCE",
                f"control attachment_acc OUT of near-chance band [{CTRL_LO},{CTRL_HI}] (chance "
                f"{1.0/N_HOST:.2f}) at {ctrl_out[:4]}: a structure-blind control is recovering (or losing) "
                f"attachment it should not -> degenerate test. {diag}")

    # Discriminator FIRES: at the easy corner structured recovers attachment the controls cannot
    if easy_gap < GAP_MIN:
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"easy-corner structured-vs-control attachment gap={easy_gap:.3f} < {GAP_MIN}: the structured "
                f"encoding did not out-recover a flat/scrambled control even at the easy corner -> structure "
                f"signal not attributable to the banded block-local mechanism. {diag}")

    if mode == "smoke":
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: recursion depth 1->3 x vocab 64->256 run end-to-end AT N={N_DIM}; the "
                f"structured-vs-control ATTACHMENT discriminator FIRES at the easy corner (gap={easy_gap:.3f}); "
                f"both controls stay near chance at every embedding config; structural_audit proves flat_bag is "
                f"structure-blind. Envelope preview: {env['n_cells_hold']}/{env['n_cells_total']} cells hold, "
                f"max_recursion_depth@V>=256={env['max_recursion_depth_at_Vge256']}. The pre-registered grammar "
                f"band is FULL-only (canonical = remote multi-seed). {diag}")

    # --- FULL pre-registered bands ---
    if anc is None:
        return ("HARD_FAIL", f"anchor {ANCHOR} missing from grid (config error). {diag}")
    st = anc["structured"]
    ctrl_attach_max = max(anc["flat_bag"]["attachment_acc_mean"],
                          anc["scrambled_roles"]["attachment_acc_mean"])
    ctrl_tree_max = max(anc["flat_bag"]["tree_exact_mean"], anc["scrambled_roles"]["tree_exact_mean"])
    attach_gap = st["attachment_acc_mean"] - ctrl_attach_max
    tree_gap = st["tree_exact_mean"] - ctrl_tree_max

    if st["tree_exact_mean"] <= HF_TREE or attach_gap < HF_GAP:
        return ("HARD_FAIL",
                f"grammar wall at shallow recursion: structured tree_exact(anchor)={st['tree_exact_mean']:.3f} "
                f"(HF<= {HF_TREE}) OR attachment gap over controls={attach_gap:.3f} (HF< {HF_GAP}) -> the banded "
                f"block-local mechanism does NOT round-trip recursive constituency / function-word structure at "
                f"the anchor; a different mechanism is needed. {diag}")

    if (env["anchor_holds"] and st["tree_exact_mean"] >= FLOOR_TREE
            and st["attachment_acc_mean"] >= FLOOR_ATTACH and st["terminal_perslot_mean"] >= FLOOR_TERM
            and attach_gap >= GAP_MIN and tree_gap >= TREE_GAP_MIN and st["tree_exact_cv"] <= CV_MAX):
        return ("HARD_PASS",
                f"RECURSIVE CONSTITUENCY + FUNCTION-WORD OPERATORS ROUND-TRIP through the substrate's block/SBC "
                f"algebra: at the anchor (LEVELS=2 = one embedded clause, V=256) the structured encoding recovers "
                f"the FULL bracketed tree tree_exact={st['tree_exact_mean']:.3f} (>= {FLOOR_TREE}), attachment "
                f"host attachment_acc={st['attachment_acc_mean']:.3f} (>= {FLOOR_ATTACH}, chance "
                f"{anc['attachment_chance']:.2f}), terminals terminal_perslot={st['terminal_perslot_mean']:.3f}, "
                f"function words function_perslot={st['function_perslot_mean']:.3f}, embed-detection "
                f"{st['embed_detection_acc_mean']:.3f}. A flat bag AND a scrambled-role control provably CANNOT "
                f"(attachment gap={attach_gap:.3f} >= {GAP_MIN}; tree gap={tree_gap:.3f} >= {TREE_GAP_MIN}; both "
                f"controls at chance). Envelope holds to recursion depth "
                f"{env['max_recursion_depth_at_Vge256']} at V>=256. NARROW glass-box structure primitive -- NOT "
                f"a language model, NOT fluent English. {diag}")

    return ("MIDDLE_BAND",
            f"partial grammar envelope with a recursion CLIFF: the structured encoding beats the flat/scrambled "
            f"controls on structure, but the anchor does NOT meet the full HARD_PASS bar (tree_exact="
            f"{st['tree_exact_mean']:.3f} vs {FLOOR_TREE}; attachment={st['attachment_acc_mean']:.3f} vs "
            f"{FLOOR_ATTACH}; max_recursion_depth@V>=256={env['max_recursion_depth_at_Vge256']}) -- report the "
            f"depth/vocab cliff. {diag}")


# ============================================================
# Driver
# ============================================================


def run_all(mode: str, output_dir: Path, t0: float):
    cfg = get_config(mode)
    trials, seeds = cfg["trials"], cfg["seeds"]
    pts = _grid_points(cfg)
    per_unit = []
    total_units = len(seeds) * len(pts)
    unit = 0
    for seed in seeds:
        for (L, V) in pts:
            r = run_unit(L, V, seed, trials)
            per_unit.append(r)
            unit += 1
            _heartbeat(output_dir, unit, total_units, t0,
                       extra={"seed": seed, "levels": L, "V": V, "bs": r["bs"],
                              "st_tree": round(r["structured"]["tree_exact"], 3),
                              "st_attach": round(r["structured"]["attachment_acc"], 3)
                              if not math.isnan(r["structured"]["attachment_acc"]) else None,
                              "fb_attach": round(r["flat_bag"]["attachment_acc"], 3)
                              if not math.isnan(r["flat_bag"]["attachment_acc"]) else None})
            st, fb, sc = r["structured"], r["flat_bag"], r["scrambled_roles"]
            _say(f"    [seed {seed}][L={L} V={V} bs={r['bs']} k={r['k']}] "
                 f"structured tree={st['tree_exact']:.3f} attach={st['attachment_acc']:.3f} "
                 f"term={st['terminal_perslot']:.3f} func={st['function_perslot']:.3f} "
                 f"embed={st['embed_detection_acc']:.3f} | flat tree={fb['tree_exact']:.3f} "
                 f"attach={fb['attachment_acc']:.3f} | scram tree={sc['tree_exact']:.3f} "
                 f"attach={sc['attachment_acc']:.3f}")
    return cfg, per_unit, total_units


def _run(mode: str) -> int:
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    cfg = get_config(mode)
    exp_units = len(cfg["seeds"]) * len(_grid_points(cfg))
    _write_start_marker(output_dir, mode, exp_units)
    _say(f"[{ANCHOR_NAME}] mode={mode} N={N_DIM} S_SLOTS={S_SLOTS} levels_grid={cfg['levels_grid']} "
         f"V_grid={cfg['V_grid']} boundary={cfg['boundary']} seeds={cfg['seeds']} trials={cfg['trials']} "
         f"expected_units={exp_units}")

    audit = structural_audit()
    _say(f"[{ANCHOR_NAME}] STRUCTURAL audit: {audit}")

    cfg, per_unit, total_units = run_all(mode, output_dir, t0)

    # arms_differ (META_RULE_AF): composite AND recovered-structure digests must be hash-distinct per unit.
    arms_differ_ok = True
    for u in per_unit:
        cds = {u[a + "_comp_digest"] for a in ARMS}
        rds = {u[a + "_rec_digest"] for a in ARMS}
        if len(cds) < len(ARMS) or len(rds) < len(ARMS):
            arms_differ_ok = False
            break
    if not arms_differ_ok:
        raise AssertionError("META_RULE_AF VIOLATION: structured/flat_bag/scrambled composites or "
                             "recovered structures bit-identical across arms")

    grid = {(L, V): _agg_cell(per_unit, L, V) for (L, V) in _grid_points(cfg)}
    env = _envelope(grid)
    verdict, vmsg = classify(mode, audit, grid, env, len(per_unit), exp_units,
                             boundary_pts=frozenset(tuple(b) for b in cfg["boundary"]))
    elapsed = time.perf_counter() - t0

    anc = grid.get(ANCHOR)
    arms = {}
    for arm in ARMS:
        arms[arm] = {
            "tree_exact_by_cell": {f"L{L}_V{V}": grid[(L, V)][arm]["tree_exact_mean"]
                                   for (L, V) in sorted(grid)},
            "attachment_acc_by_cell": {f"L{L}_V{V}": grid[(L, V)][arm]["attachment_acc_mean"]
                                       for (L, V) in sorted(grid)},
            "terminal_perslot_by_cell": {f"L{L}_V{V}": grid[(L, V)][arm]["terminal_perslot_mean"]
                                         for (L, V) in sorted(grid)},
            "function_perslot_by_cell": {f"L{L}_V{V}": grid[(L, V)][arm]["function_perslot_mean"]
                                         for (L, V) in sorted(grid)},
            "embed_detection_by_cell": {f"L{L}_V{V}": grid[(L, V)][arm]["embed_detection_acc_mean"]
                                        for (L, V) in sorted(grid)},
            "anchor_tree_exact": anc[arm]["tree_exact_mean"] if anc else None,
            "anchor_attachment_acc": anc[arm]["attachment_acc_mean"] if anc else None,
        }
    arms["structured"]["anchor_tree_exact_cv"] = anc["structured"]["tree_exact_cv"] if anc else None
    arms["flat_bag"]["attachment_chance"] = 1.0 / N_HOST
    arms["scrambled_roles"]["attachment_chance"] = 1.0 / N_HOST

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: recursive constituency + function-word operators via block-local SBC ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(cfg["seeds"]),
        "n_units": len(per_unit),
        "expected_n_units": exp_units,
        "cardinality_ok": len(per_unit) >= exp_units,
        "arms_differ_verified": arms_differ_ok,
        "envelope": env,
        "config": {
            "N": N_DIM, "S_SLOTS": S_SLOTS, "F_SPARSE": F_SPARSE, "V_FUNC": V_FUNC,
            "levels_grid": cfg["levels_grid"], "V_grid": cfg["V_grid"], "boundary": cfg["boundary"],
            "trials": cfg["trials"], "seeds": list(cfg["seeds"]),
            "content_slots": list(CONTENT_SLOTS), "func_slots": list(FUNC_SLOTS),
            "func_types": list(FUNC_TYPES), "host_slots": list(HOST_SLOTS),
            "recursion_axis": "LEVELS_banded_blocks_bs=N/(LEVELS*S_SLOTS)",
            "vocab_axis": "V_content_per_clause",
            "algebra": "block_local_sparse_superposition_disjoint_bands",
            "position_binding": "disjoint_band_index_per_level_and_slot",
            "attachment_binding": "EMBED_HOOK_superposed_in_host_block",
            "function_word_treatment": "closed_class_type_partitioned_selectional_restriction_COMP_gates_recursion",
            "storage_strategy": "sharded_block_disjoint_per_slot",
        },
        "arms": arms,
        "grid": {f"L{L}_V{V}": grid[(L, V)] for (L, V) in sorted(grid)},
        "per_unit": per_unit,
        "structural_audit": audit,
        "bands": {"FLOOR_TREE": FLOOR_TREE, "FLOOR_ATTACH": FLOOR_ATTACH, "FLOOR_TERM": FLOOR_TERM,
                  "GAP_MIN": GAP_MIN, "TREE_GAP_MIN": TREE_GAP_MIN, "CTRL_LO": CTRL_LO, "CTRL_HI": CTRL_HI,
                  "CV_MAX": CV_MAX, "HF_TREE": HF_TREE, "HF_GAP": HF_GAP,
                  "ANCHOR": list(ANCHOR), "EASY": list(EASY)},
        "hp_scope": {
            "structured": ["FLOOR_TREE", "FLOOR_ATTACH", "FLOOR_TERM", "GAP_MIN", "TREE_GAP_MIN", "CV_MAX",
                           "envelope_reaches_ANCHOR"],
            "flat_bag": ["attachment_near_chance_BIAS_gate_only"],
            "scrambled_roles": ["attachment_near_chance_BIAS_gate_only"],
        },
        "cited_baselines": {
            "blocklocal_decoder": "data/exp_generation_decoder_gsbc_native_blocklocal_v1 "
                                  "(blocklocal exact_ordered=1.000 to D<=26 at V<=1024; block-local Stage A/B/C)",
            "comprehension_role_typing": "data/exp_comprehension_envelope_superposition_vocab_v1 "
                                         "(role-typed partition-restricted decode; superposition load L)",
        },
        "kb_referent_declared": False,
        "framing": "NARROW structured glass-box grammar-structure primitive; NOT a language model, NOT fluent "
                   "English, NOT raw-text prediction; synthetic clean sparse-bipolar codes; Stage-3 not Stage-4",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    }
    _write_metrics_atomic(output_dir, metrics)
    written = json.load(open(output_dir / "metrics.json"))
    assert written["run_mode"] == mode, f"RUN_MODE_MISMATCH {written['run_mode']} != {mode}"

    _say(f"\n[{ANCHOR_NAME}] {verdict}: {vmsg}")
    _say(f"[{ANCHOR_NAME}] metrics -> {output_dir / 'metrics.json'}  elapsed={elapsed:.1f}s")
    return 0


def _run_selftest() -> int:
    t0 = time.perf_counter()
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    audit = structural_audit()
    # invariants: (a) flat_bag provably structure-blind; (b) structured recovers recursion + attachment at
    # the anchor (LEVELS=2, V=256) via disjoint-block decode; (c) controls near chance on attachment; (d)
    # structured >> controls on tree_exact.
    anc = run_unit(2, 256, 7, 24)
    flat = run_unit(1, 64, 7, 24)                        # flat clause sanity (no embedding)
    st, fb, sc = anc["structured"], anc["flat_bag"], anc["scrambled_roles"]
    attach_gap = st["attachment_acc"] - max(fb["attachment_acc"], sc["attachment_acc"])
    tree_gap = st["tree_exact"] - max(fb["tree_exact"], sc["tree_exact"])
    ok = (audit["bag_blind_to_structure"]
          and st["tree_exact"] >= 0.80
          and st["attachment_acc"] >= 0.90
          and st["terminal_perslot"] >= 0.90
          and st["embed_detection_acc"] >= 0.90
          and CTRL_LO <= fb["attachment_acc"] <= CTRL_HI
          and CTRL_LO <= sc["attachment_acc"] <= CTRL_HI
          and attach_gap >= GAP_MIN
          and tree_gap >= TREE_GAP_MIN
          and flat["structured"]["tree_exact"] >= 0.90)
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: bag_blind="
         f"{audit['bag_blind_to_structure']} | anchor(L2V256 bs={anc['bs']}) structured tree_exact="
         f"{st['tree_exact']:.3f} attach={st['attachment_acc']:.3f} term={st['terminal_perslot']:.3f} "
         f"func={st['function_perslot']:.3f} embed={st['embed_detection_acc']:.3f} | flat_bag attach="
         f"{fb['attachment_acc']:.3f} tree={fb['tree_exact']:.3f} | scrambled attach={sc['attachment_acc']:.3f} "
         f"tree={sc['tree_exact']:.3f} | attach_gap={attach_gap:.3f} tree_gap={tree_gap:.3f} | flat_clause(L1V64) "
         f"tree={flat['structured']['tree_exact']:.3f} [{time.perf_counter() - t0:.1f}s]")
    return 0 if ok else 1


def main() -> int:
    if "--self-test" in sys.argv:
        return _run_selftest()
    mode = "smoke" if "--smoke" in sys.argv else \
        ("smoke" if os.environ.get("HDLAB_RUN_MODE", "").lower() == "smoke" else "full")
    return _run(mode)


if __name__ == "__main__":
    _od = None
    try:
        _od = _out_dir()
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        if _od is not None:
            _write_crash_metrics(_od, e)
        raise
