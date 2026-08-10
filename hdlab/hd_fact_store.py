"""HD fact store with SOURCE-TRUST ingest vetting (substrate-native, glass-box).

A FACT is a proposition (subject, relation, object) stored as ONE role-slot-bound
hypervector in the substrate, with SOURCE-id and TRUST-level tags BOUND INTO THE SAME
bundle (native HD binding, not side metadata):

    fact_vec = quantize( bind(REL, rel) + bind(ARG0, subj) + bind(ARG1, obj)
                         + bind(SOURCE, src) + bind(TRUST, trust) )

GLASS-BOX: every field (including provenance + trust) recovers by a role-query unbind +
cleanup -- the store never reads a plaintext copy to answer a query:

    obj_hat    = cleanup_OBJECT ( unbind(fact_vec, ARG1) )
    src_hat    = cleanup_SOURCE ( unbind(fact_vec, SOURCE) )   # provenance
    trust_hat  = cleanup_TRUST  ( unbind(fact_vec, TRUST) )    # trust level

The role-slot binding REUSES hdlab.event_bundle.EventBundleCodec (which reuses the M1.7
RoleSlotSummarizer bipolar primitives byte-identically: bind = elementwise multiply,
bundle = sum, quantize = sign, cleanup = matmul + argmax). This module ADDS three things
on top of that validated binding, none of which reinvent it:
  * per-domain cleanup (the ARG1 slot cleans over OBJECT symbols only, SOURCE over SOURCE
    symbols only, etc.) so a role query returns a symbol from the correct domain;
  * a subject-relation HD SIGNATURE key for NATIVE conflict retrieval (same (s,r) -> a
    bit-identical 2-pair bundle -> cosine 1.0; a distractor sharing only one of the two
    pairs -> cosine ~0.5, below threshold);
  * INGEST-VET: trust-ranked conflict resolution (REPLACE / COMBINE / FLAG / DROP).

INGEST-VET is SOURCE-TRUST vetting, NOT correctness vetting. It trusts curated sources
and resolves same-subject-relation-different-object conflicts by trust rank; it does NOT
check whether a trusted fact is factually TRUE (the deliberate student-model trade: a
student believes the textbook). This INVERTS the failed condenser-auditor, which
false-flagged 53% of CORRECT entries because a thin internal ontology over-rejected rich
knowledge. Here a clean (non-conflicting) fact simply STORES -- there is no internal
uncertainty gate to spuriously trip -- so the clean false-flag rate is ~0 by construction.

ASCII-only. All vectors torch.Tensor bipolar {-1,+1} float32. Determinism: role keys and
the symbol codebook are seeded via torch.Generator; identical inputs -> identical store.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import torch

from hdlab.event_bundle import EventBundleCodec
# Byte-identical reuse of the M1.7 bipolar primitives (via event_bundle's own imports).
from hdlab.role_slot_summarizer import _bipolar_bind, _bipolar_quantize

# ---- role set: fact-content roles + provenance/trust roles, all bound into one bundle --
FACT_ROLES: Tuple[str, ...] = ("REL", "ARG0", "ARG1", "SOURCE", "TRUST")
ROLE_DOMAIN: Dict[str, str] = {
    "ARG0": "SUBJECT", "REL": "RELATION", "ARG1": "OBJECT",
    "SOURCE": "SOURCE", "TRUST": "TRUST",
}

# ---- trust ladder: bound symbol -> numeric level (textbook > article > unknown) --------
TRUST_LEVEL: Dict[str, float] = {
    "TRUST_HIGH": 1.0,   # e.g. curated textbook
    "TRUST_MID": 0.6,    # e.g. article
    "TRUST_LOW": 0.3,    # e.g. unknown / unvetted
}

# Facts still "live" in the store (queryable + eligible to conflict with a newcomer).
ACTIVE_STATUSES = frozenset({"ACTIVE", "COMBINED", "FLAGGED"})


@dataclass
class FactRecord:
    """One stored fact. vec+sr_key are the HD substrate; the plaintext fields are a SHADOW
    ledger used ONLY for grading/inspection -- every query path recovers from `vec` by
    unbind (see recover_fact), proven bit-faithful by the round-trip self-test.
    `status` is symbolic CONTROL state (not part of the asserted proposition)."""
    fid: int
    vec: torch.Tensor
    sr_key: torch.Tensor
    subject: str
    relation: str
    obj: str
    source: str
    trust_sym: str
    trust_level: float
    status: str = "ACTIVE"


@dataclass
class StoreResult:
    """Outcome of one store() ingest-vet decision (glass-box, all fields inspectable)."""
    fid: int
    resolution: str                       # CLEAN_STORE | REPLACE | COMBINE | FLAG | DROP | CONSISTENT_DUP
    detected_conflict: bool               # did native HD retrieval find a same-(s,r)-diff-o fact?
    conflict_fids: List[int] = field(default_factory=list)
    conflict_objs: List[str] = field(default_factory=list)   # recovered by unbind (glass-box)
    new_trust: float = 0.0
    stored_trust: Optional[float] = None
    note: str = ""


class HDFactStore:
    """Substrate-native fact store + source-trust ingest vetting.

    Args:
        n_dim: substrate dimensionality (bipolar vectors of length n_dim).
        seed: torch.Generator seed for role keys + symbol codebook (determinism).
        relation_cardinality: {relation_name: "FUNCTIONAL" | "MULTIVALUED"}. FUNCTIONAL =
            at most one true object (two different -> CONTRADICTORY -> FLAG). MULTIVALUED =
            additive (two different objects both valid -> COMPATIBLE -> COMBINE).
        sr_threshold: cosine threshold on the (subject,relation) signature key for
            native same-(s,r) retrieval. 0.75 cleanly separates same-(s,r) (cos=1.0) from a
            one-pair-shared distractor (cos~0.5).
    """

    def __init__(self, n_dim: int = 8192, seed: int = 0,
                 relation_cardinality: Optional[Dict[str, str]] = None,
                 sr_threshold: float = 0.75, use_index: bool = False) -> None:
        self.n_dim = int(n_dim)
        self.seed = int(seed)
        self.sr_threshold = float(sr_threshold)
        self.use_index = bool(use_index)
        self.codec = EventBundleCodec(n_dim=self.n_dim, roles=FACT_ROLES, seed=self.seed)
        self.relation_cardinality: Dict[str, str] = dict(relation_cardinality or {})
        self._facts: List[FactRecord] = []
        # SUB-LINEAR conflict index (opt-in; default off preserves the O(n) reference path
        # bit-for-bit). The (s,r) HD SIGNATURE is DETERMINISTIC: same (subject, relation) ->
        # a bit-identical 2-pair bundle. That makes same-(s,r) retrieval an EXACT-MATCH lookup,
        # so a content-address of the signature (sha1 of its packed bipolar bytes) is a PERFECT
        # hash: O(1) bucket instead of an O(n) cosine scan, with NO approximation. Distinct (s,r)
        # never collide (their signatures differ), so the bucket is exactly the same-(s,r) set;
        # the SAME glass-box confirm (unbind + subject/relation match) still gates every candidate.
        self._sr_index: Dict[bytes, List[int]] = {}
        self._domain_syms: Dict[str, List[str]] = {d: [] for d in
                                                    ("SUBJECT", "RELATION", "OBJECT",
                                                     "SOURCE", "TRUST")}
        self._domain_seen: Dict[str, set] = {d: set() for d in self._domain_syms}
        # Per-domain stacked-codebook cache. Cleanup argmax scans the WHOLE domain codebook;
        # rebuilding it (torch.stack over V rows) on every _cleanup call was the O(V) hot-spot
        # of the read path. The codebook only changes when a NEW symbol registers, so we cache
        # the stack and invalidate that domain on registration. Bit-identical result (same rows,
        # same order, same argmax); pure constant-factor speedup of recover/query.
        self._cb_cache: Dict[str, torch.Tensor] = {}

    # ---- symbol / domain bookkeeping (deterministic codebook via codec._sym_vec) -------
    def _register_domain(self, domain: str, sym: str) -> None:
        sym = str(sym)
        self.codec._sym_vec(sym)  # deterministic first-sight registration into shared codebook
        if sym not in self._domain_seen[domain]:
            self._domain_seen[domain].add(sym)
            self._domain_syms[domain].append(sym)
            self._cb_cache.pop(domain, None)  # invalidate stacked codebook for this domain

    def _domain_codebook(self, domain: str) -> Tuple[torch.Tensor, List[str]]:
        syms = self._domain_syms[domain]
        if not syms:
            return torch.empty((0, self.n_dim), dtype=torch.float32), syms
        cb = self._cb_cache.get(domain)
        if cb is None or cb.shape[0] != len(syms):
            cb = torch.stack([self.codec._sym_vec(s) for s in syms], 0)
            self._cb_cache[domain] = cb
        return cb, syms

    def _cleanup(self, filler_hat: torch.Tensor, domain: str) -> Tuple[Optional[str], float]:
        cb, syms = self._domain_codebook(domain)
        if not syms:
            return None, 0.0
        scores = cb @ filler_hat
        j = int(torch.argmax(scores).item())
        return syms[j], float(scores[j].item())

    # ---- HD encode -------------------------------------------------------------------
    def _encode_fact(self, subj: str, rel: str, obj: str, src: str, trust_sym: str) -> torch.Tensor:
        self._register_domain("SUBJECT", subj)
        self._register_domain("RELATION", rel)
        self._register_domain("OBJECT", obj)
        self._register_domain("SOURCE", src)
        self._register_domain("TRUST", trust_sym)
        return self.codec.encode_event(
            {"REL": rel, "ARG0": subj, "ARG1": obj, "SOURCE": src, "TRUST": trust_sym})

    def _sr_key(self, subj: str, rel: str) -> torch.Tensor:
        """(subject, relation) HD signature: a 2-pair bundle. Same (s,r) -> identical vec."""
        acc = (_bipolar_bind(self.codec.role_key("ARG0"), self.codec._sym_vec(str(subj)))
               + _bipolar_bind(self.codec.role_key("REL"), self.codec._sym_vec(str(rel))))
        return _bipolar_quantize(acc)

    # ---- GLASS-BOX recovery (the ONLY read path; never touches plaintext) --------------
    def recover_fact(self, vec: torch.Tensor) -> Dict[str, object]:
        """Recover (subject, relation, object, source, trust) from an HD bundle by
        per-role unbind + per-domain cleanup. Glass-box: this is how every query is answered."""
        out: Dict[str, Tuple[Optional[str], float]] = {}
        for role in FACT_ROLES:
            hat = _bipolar_bind(vec, self.codec.role_key(role))  # bipolar unbind == bind
            out[role] = self._cleanup(hat, ROLE_DOMAIN[role])
        return {
            "subject": out["ARG0"][0], "relation": out["REL"][0], "object": out["ARG1"][0],
            "source": out["SOURCE"][0], "trust": out["TRUST"][0],
            "scores": {r: out[r][1] for r in FACT_ROLES},
        }

    # ---- fact append (keeps the sub-linear index in sync when enabled) ----------------
    @staticmethod
    def _sr_key_bytes(sr_key: torch.Tensor) -> bytes:
        """Content-address a (deterministic bipolar) signature key -> a stable hash bucket.
        Same (s,r) -> identical sr_key tensor -> identical bytes -> identical bucket."""
        packed = sr_key.to(torch.int8).numpy().tobytes()
        return hashlib.sha1(packed).digest()

    def _append_fact(self, rec: "FactRecord") -> None:
        self._facts.append(rec)
        if self.use_index:
            self._sr_index.setdefault(self._sr_key_bytes(rec.sr_key), []).append(rec.fid)

    # ---- NATIVE conflict retrieval ---------------------------------------------------
    def _find_same_sr(self, subj: str, rel: str, sr_key: torch.Tensor) -> List[FactRecord]:
        """Retrieve live facts with the SAME (subject, relation). Two equivalent paths:
        the O(n) cosine reference scan (default), or the O(1) content-hash index (use_index).
        Both apply the IDENTICAL glass-box confirm; results are byte-equivalent (verified)."""
        if self.use_index:
            return self._find_same_sr_indexed(subj, rel, sr_key)
        return self._find_same_sr_linear(subj, rel, sr_key)

    def _find_same_sr_linear(self, subj: str, rel: str, sr_key: torch.Tensor) -> List[FactRecord]:
        """O(n) reference: cosine on the signature key over ALL live facts, then confirm."""
        active = [f for f in self._facts if f.status in ACTIVE_STATUSES]
        if not active:
            return []
        M = torch.stack([f.sr_key for f in active], 0)          # (A, n_dim)
        cos = (M @ sr_key) / self.n_dim                          # bipolar cosine = dot / n_dim
        cands: List[FactRecord] = []
        for i, f in enumerate(active):
            if float(cos[i].item()) >= self.sr_threshold:
                rec = self.recover_fact(f.vec)                   # glass-box confirm
                if rec["subject"] == str(subj) and rec["relation"] == str(rel):
                    cands.append(f)
        return cands

    def _find_same_sr_indexed(self, subj: str, rel: str, sr_key: torch.Tensor) -> List[FactRecord]:
        """O(1) bucket: hash the signature key -> candidate fids (same-(s,r) by construction),
        then apply the SAME active-status filter + glass-box confirm as the linear path.
        The cosine>=threshold pre-filter is auto-satisfied (bucket members share cos=1.0)."""
        bucket = self._sr_index.get(self._sr_key_bytes(sr_key))
        if not bucket:
            return []
        cands: List[FactRecord] = []
        for fid in bucket:                                       # append order == linear scan order
            f = self._facts[fid]
            if f.status not in ACTIVE_STATUSES:
                continue
            rec = self.recover_fact(f.vec)                       # glass-box confirm (identical gate)
            if rec["subject"] == str(subj) and rec["relation"] == str(rel):
                cands.append(f)
        return cands

    # ---- INGEST-VET: store(new_fact, source, trust) with trust-ranked resolution -------
    def store(self, subject: str, relation: str, obj: str,
              source: str, trust: str) -> StoreResult:
        subject, relation, obj, source, trust = (str(subject), str(relation),
                                                  str(obj), str(source), str(trust))
        if trust not in TRUST_LEVEL:
            raise KeyError(f"unknown trust level {trust!r}; known={sorted(TRUST_LEVEL)}")
        new_level = TRUST_LEVEL[trust]
        vec = self._encode_fact(subject, relation, obj, source, trust)
        sr_key = self._sr_key(subject, relation)
        fid = len(self._facts)

        same_sr = self._find_same_sr(subject, relation, sr_key)
        # A conflict is a same-(s,r) fact whose OBJECT (recovered by unbind) DIFFERS.
        conflicts: List[FactRecord] = []
        consistent_dup = False
        for f in same_sr:
            rec_obj = self.recover_fact(f.vec)["object"]
            if rec_obj == obj:
                consistent_dup = True
            else:
                conflicts.append(f)

        rec = FactRecord(fid=fid, vec=vec, sr_key=sr_key, subject=subject, relation=relation,
                         obj=obj, source=source, trust_sym=trust, trust_level=new_level)

        if not conflicts:
            # CLEAN (or a consistent duplicate): just store. No spurious flag -- the
            # source-trust store has no internal uncertainty gate to trip.
            rec.status = "ACTIVE"
            self._append_fact(rec)
            res = "CONSISTENT_DUP" if consistent_dup else "CLEAN_STORE"
            return StoreResult(fid=fid, resolution=res, detected_conflict=False,
                               new_trust=new_level,
                               note=("same object already present" if consistent_dup else "no same-(s,r) fact"))

        # Resolve against the HIGHEST-trust conflicting stored fact.
        stored_c = max(conflicts, key=lambda f: f.trust_level)
        conflict_fids = [f.fid for f in conflicts]
        conflict_objs = [self.recover_fact(f.vec)["object"] for f in conflicts]

        if new_level > stored_c.trust_level:
            for f in conflicts:
                f.status = "SUPERSEDED"
            rec.status = "ACTIVE"
            self._append_fact(rec)
            resolution, note = "REPLACE", "new is higher-trust -> override old"
        elif new_level < stored_c.trust_level:
            rec.status = "DROPPED"
            self._append_fact(rec)
            resolution, note = "DROP", "new is lower-trust -> dropped"
        else:
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

        return StoreResult(fid=fid, resolution=resolution, detected_conflict=True,
                           conflict_fids=conflict_fids, conflict_objs=conflict_objs,
                           new_trust=new_level, stored_trust=stored_c.trust_level, note=note)

    # ---- query (glass-box) -----------------------------------------------------------
    def query(self, subject: str, relation: str) -> List[Dict[str, object]]:
        """Return all LIVE facts for (subject, relation), each recovered from HD by unbind."""
        sr_key = self._sr_key(subject, relation)
        return [dict(fid=f.fid, status=f.status, **self.recover_fact(f.vec))
                for f in self._find_same_sr(subject, relation, sr_key)]

    def live_facts(self) -> List[FactRecord]:
        return [f for f in self._facts if f.status in ACTIVE_STATUSES]


# ===================== formula self-tests ==========================================

def _selftest_glassbox_roundtrip() -> None:
    """P1: a stored fact's content + provenance + trust recover from the HD bundle by
    unbind (glass-box, no plaintext read)."""
    st = HDFactStore(n_dim=8192, seed=1)
    r = st.store("paris", "capital_of", "france", "textbook_A", "TRUST_HIGH")
    rec = st.recover_fact(st._facts[r.fid].vec)
    assert rec["subject"] == "paris", rec
    assert rec["relation"] == "capital_of", rec
    assert rec["object"] == "france", rec
    assert rec["source"] == "textbook_A", rec
    assert rec["trust"] == "TRUST_HIGH", rec


def _selftest_sr_key_separates() -> None:
    """The (s,r) signature: same (s,r) -> cosine 1.0; share one pair -> well below 0.75."""
    st = HDFactStore(n_dim=8192, seed=2)
    k_sr = st._sr_key("a", "rel1")
    k_same = st._sr_key("a", "rel1")
    k_diff_subj = st._sr_key("b", "rel1")   # shares REL only
    k_diff_rel = st._sr_key("a", "rel2")    # shares ARG0 only
    k_none = st._sr_key("b", "rel2")
    n = st.n_dim
    cos_same = float((k_same @ k_sr) / n)
    cos_ds = float((k_diff_subj @ k_sr) / n)
    cos_dr = float((k_diff_rel @ k_sr) / n)
    cos_none = float((k_none @ k_sr) / n)
    # NB: _bipolar_quantize maps 0 -> +1, so a 2-pair sum (~50% zero components) carries a
    # systematic +1 bias -> unrelated keys share a ~0.25 baseline cosine (measured, not ~0).
    # The 0.75 threshold still cleanly separates same (1.0) from share-one (max ~0.52).
    assert cos_same > 0.999, cos_same
    assert cos_ds < 0.60, cos_ds
    assert cos_dr < 0.60, cos_dr
    assert cos_none < 0.40, cos_none


def _selftest_four_resolutions() -> None:
    """REPLACE / DROP / COMBINE / FLAG each fire on the intended injected case."""
    st = HDFactStore(n_dim=8192, seed=3,
                     relation_cardinality={"capital_of": "FUNCTIONAL",
                                           "speaks": "MULTIVALUED"})
    # REPLACE: mid then high, same (s,r), diff obj.
    st.store("x", "capital_of", "o1", "art", "TRUST_MID")
    r_rep = st.store("x", "capital_of", "o2", "book", "TRUST_HIGH")
    assert r_rep.resolution == "REPLACE" and r_rep.detected_conflict, r_rep
    # DROP: high stored, low new.
    st.store("y", "capital_of", "o1", "book", "TRUST_HIGH")
    r_drop = st.store("y", "capital_of", "o2", "blog", "TRUST_LOW")
    assert r_drop.resolution == "DROP", r_drop
    # FLAG: equal-trust, functional, contradictory.
    st.store("z", "capital_of", "o1", "artA", "TRUST_MID")
    r_flag = st.store("z", "capital_of", "o2", "artB", "TRUST_MID")
    assert r_flag.resolution == "FLAG", r_flag
    # COMBINE: equal-trust, multivalued, additive.
    st.store("w", "speaks", "english", "artA", "TRUST_MID")
    r_comb = st.store("w", "speaks", "french", "artB", "TRUST_MID")
    assert r_comb.resolution == "COMBINE", r_comb
    # After COMBINE both live; query returns 2.
    live = st.query("w", "speaks")
    assert len({d["object"] for d in live}) == 2, live


def _selftest_clean_no_false_flag() -> None:
    """Clean facts + distractors (same-r-diff-s, same-s-diff-r) NEVER flag as conflict."""
    st = HDFactStore(n_dim=8192, seed=4,
                     relation_cardinality={"rel_a": "FUNCTIONAL", "rel_b": "FUNCTIONAL"})
    flagged = 0
    n = 0
    for i in range(20):
        n += 1
        if st.store(f"s{i}", "rel_a", f"o{i}", "src", "TRUST_MID").detected_conflict:
            flagged += 1
    # same relation, different subjects (NOT a conflict)
    for i in range(20):
        n += 1
        if st.store(f"t{i}", "rel_b", "shared_obj", "src", "TRUST_MID").detected_conflict:
            flagged += 1
    # same subject, different relation (NOT a conflict)
    for i in range(20):
        n += 1
        if st.store(f"s{i}", "rel_b", f"q{i}", "src", "TRUST_MID").detected_conflict:
            flagged += 1
    assert flagged == 0, f"clean false-flag: {flagged}/{n}"


def _selftest_index_equivalence() -> None:
    """The O(1) content-hash index returns byte-identical store() outcomes to the O(n)
    reference on a mixed conflict/clean/distractor sequence (CAN-FAIL equivalence gate)."""
    card = {"capital_of": "FUNCTIONAL", "born_in": "FUNCTIONAL", "speaks": "MULTIVALUED"}
    lin = HDFactStore(n_dim=4096, seed=5, relation_cardinality=card, use_index=False)
    idx = HDFactStore(n_dim=4096, seed=5, relation_cardinality=card, use_index=True)
    ops = []
    for i in range(15):                                  # clean unique facts
        ops.append((f"s{i}", "born_in", f"o{i}", "src", "TRUST_MID"))
    ops += [("x", "capital_of", "o1", "art", "TRUST_MID"),   # then REPLACE
            ("x", "capital_of", "o2", "book", "TRUST_HIGH"),
            ("y", "capital_of", "o1", "book", "TRUST_HIGH"),  # DROP
            ("y", "capital_of", "o2", "blog", "TRUST_LOW"),
            ("z", "capital_of", "o1", "aA", "TRUST_MID"),     # FLAG
            ("z", "capital_of", "o2", "aB", "TRUST_MID"),
            ("w", "speaks", "en", "aA", "TRUST_MID"),         # COMBINE
            ("w", "speaks", "fr", "aB", "TRUST_MID"),
            ("s3", "born_in", "o3", "src", "TRUST_MID")]      # CONSISTENT_DUP
    for a in ops:
        rl = lin.store(*a)
        ri = idx.store(*a)
        assert (rl.resolution == ri.resolution and rl.detected_conflict == ri.detected_conflict
                and sorted(rl.conflict_fids) == sorted(ri.conflict_fids)
                and sorted(rl.conflict_objs) == sorted(ri.conflict_objs)), (a, rl, ri)
    # query() path also equivalent
    for q in [("w", "speaks"), ("x", "capital_of"), ("s7", "born_in"), ("nope", "born_in")]:
        ql = sorted((d["fid"], d["object"]) for d in lin.query(*q))
        qi = sorted((d["fid"], d["object"]) for d in idx.query(*q))
        assert ql == qi, (q, ql, qi)


def _run_all_selftests() -> dict:
    _selftest_glassbox_roundtrip()
    _selftest_sr_key_separates()
    _selftest_four_resolutions()
    _selftest_clean_no_false_flag()
    _selftest_index_equivalence()
    return {"roles": list(FACT_ROLES), "trust_levels": TRUST_LEVEL,
            "reuse": "EventBundleCodec / RoleSlotSummarizer bipolar primitives",
            "sublinear_index": "content-hash sr-signature (O(1)); byte-equivalent to O(n)"}


if __name__ == "__main__":
    print(f"[hd_fact_store selftest] PASS {_run_all_selftests()}")
