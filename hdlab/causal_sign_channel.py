"""CAUSAL SIGN CHANNEL -- the FORMAL-MODEL more/less (increase/decrease) edge-sign reader, ingested LIVE.

GROWN-KNOWLEDGE LIVE INGEST (owner directive 2026-09-10) of the owner-DONE
`grow_the_causal_mechanism_knowledge_foundation_by_mining_directed_causal_linguistic_testimony` (STRONG).

THE PROBLEM IT SOLVES. The more/less SIGN of a causal edge ("does MORE force cause MORE or LESS motion?") is NOT
recoverable from prose co-occurrence -- 7 prose sign sources (co-occurrence, marker-signed, force-dynamic verb
lexicon, explicit signed-proportionality at 78% coverage) all TIE a scrambled-role falsifier (proven, the Causal
Hierarchy Theorem: the story-specific sign does not instantiate from type-level co-occurrence). What DOES work is
the sign COMPUTED FROM A RUNNABLE MODEL'S STRUCTURE: reaction stoichiometry (reactant -1 / product +1), everyday
physics + thermodynamics/ENTROPY couplings (force->motion +, friction->speed -, heat->temperature +, time->decay +).
On WIQA's science slice this is the FIRST sign source to BEAT the scrambled-sign falsifier CI-separated.

THE INSTANTIATION FIX (the brain-foundational move -- Kintsch/Zwaan: generic knowledge is SELECTED by the specific
text). A formal coupling X->Y fires ONLY IF the passage supplies its model's context (a chemical edge needs the
reaction's other participants present; a physics edge needs the passage to be a physics context, >=2 physics
quantities). Passage-context gating GREW coverage from a promiscuous ~9% to 13-14% AND KEPT the falsifier-beating
precision (SIGN arm 0.632 vs scrambled-sign 0.475, +0.157 CI[0.094,0.222] on WIQA n=5005; loose grounding TIED at
26%). Witness `verification/test_causal_sign_integrated.py` (this organ preserves that read byte-identically:
`verification/test_causal_sign_channel_landed.py`).

BRAIN-FOUNDATIONAL BASIS (BF_SPIRIT). Forbus Qualitative Process theory: DIRECT influences (I+/I-) are storable and
falsifier-beating (the sign of a direct structural coupling is model-derivable); NET/regime signs need SIMULATION
(the everyday/social tail, routed to the grounded Delta-Delta world-model program, NOT here). The passage-context
gate = Kintsch construction-integration (generic knowledge instantiated by the specific situation model). Glass-box,
offline curated formal-model couplings (a static FOUNDATION asset -- chemistry/physics/thermo, scale-up = Rhea /
BioModels / ecological), NO external LLM at inference.

SCOPE + HONEST BOUND. Coverage is the science slice (~13-14% of WIQA more/less items); the everyday/biological tail
(~87%, no runnable formal model) still needs the grounded Delta-Delta interventional program. `causal_edge_sign`
returns `covered=False` (an honest abstain) when no gated formal coupling applies -- the caller then falls back to
its other channels. DO NOT extend this with a PROSE sign source (they tie the falsifier -- a durable negative).
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Sequence, Set, Tuple

__all__ = ["causal_edge_sign", "CausalSignChannel", "ground_concepts"]

# --- FORMAL-MODEL KNOWLEDGE (curated offline FOUNDATION; verbatim from the owner-DONE solution's verified store) ---
# REACTIONS: (reactants, products) -- stoichiometric sign (reactant -1 towards a co-reactant, product +1).
REACTIONS: List[Tuple[List[str], List[str]]] = [
    (['carbon dioxide', 'water', 'light'], ['glucose', 'oxygen']),
    (['glucose', 'oxygen'], ['carbon dioxide', 'water', 'energy']),
    (['fuel', 'oxygen'], ['carbon dioxide', 'water', 'heat']),
    (['carbon', 'oxygen'], ['carbon dioxide', 'heat']),
    (['food', 'water'], ['glucose', 'nutrient']),
    (['starch'], ['sugar']),
    (['water', 'heat'], ['water vapor']),
    (['water vapor'], ['cloud', 'water']),
    (['cloud', 'water'], ['rain']),
    (['carbon dioxide', 'water'], ['carbonic acid']),
    (['iron', 'oxygen', 'water'], ['rust']),
    (['nitrogen', 'hydrogen'], ['ammonia']),
    (['rock', 'water', 'acid'], ['sediment', 'mineral']),
    (['magma', 'heat'], ['lava']),
    (['lava'], ['rock']),
    (['seed', 'water', 'nutrient', 'light'], ['plant', 'root']),
    (['plant', 'water', 'light'], ['fruit', 'seed', 'oxygen']),
    (['prey', 'energy'], ['predator']),
    (['nutrient', 'water'], ['growth']),
    (['sunlight', 'water', 'carbon dioxide'], ['sugar', 'oxygen']),
]

# INFLUENCES: (cause, effect, sign) -- everyday physics + thermo/entropy direct couplings.
INFLUENCES: List[Tuple[str, str, int]] = [
    ('force', 'motion', 1), ('force', 'acceleration', 1), ('force', 'speed', 1), ('mass', 'acceleration', -1),
    ('mass', 'weight', 1), ('mass', 'inertia', 1), ('friction', 'speed', -1), ('friction', 'motion', -1),
    ('friction', 'heat', 1), ('height', 'speed', 1), ('height', 'energy', 1), ('slope', 'speed', 1),
    ('gravity', 'weight', 1), ('gravity', 'speed', 1), ('speed', 'distance', 1), ('speed', 'energy', 1),
    ('weight', 'pressure', 1), ('area', 'pressure', -1), ('depth', 'pressure', 1), ('heat', 'temperature', 1),
    ('temperature', 'volume', 1), ('temperature', 'pressure', 1), ('temperature', 'expansion', 1),
    ('heat', 'melting', 1), ('heat', 'evaporation', 1), ('heat', 'speed', 1), ('insulation', 'heat', -1),
    ('insulation', 'cooling', -1), ('temperature', 'energy', 1), ('cold', 'freezing', 1),
    ('temperature', 'heat flow', 1), ('time', 'decay', 1), ('time', 'disorder', 1), ('time', 'erosion', 1),
    ('time', 'cooling', 1), ('heat', 'disorder', 1), ('concentration', 'diffusion', 1), ('energy', 'work', 1),
    ('energy', 'motion', 1), ('disorder', 'energy', -1), ('light', 'brightness', 1), ('light', 'visibility', 1),
    ('distance', 'brightness', -1), ('water', 'erosion', 1), ('wind', 'erosion', 1), ('slope', 'erosion', 1),
    ('vegetation', 'erosion', -1), ('rain', 'flood', 1), ('water', 'flow', 1), ('pressure', 'flow', 1),
    ('predator', 'prey', -1), ('prey', 'predator', 1), ('nutrient', 'growth', 1), ('water', 'growth', 1),
    ('light', 'growth', 1), ('food', 'energy', 1), ('disease', 'health', -1), ('predator', 'survival', -1),
    ('food', 'survival', 1), ('water', 'survival', 1), ('oxygen', 'survival', 1), ('mate', 'offspring', 1),
    ('plant', 'oxygen', 1), ('nutrient', 'plant', 1), ('water', 'plant', 1), ('light', 'plant', 1),
    ('time', 'decay', 1), ('time', 'disorder', 1), ('time', 'wear', 1), ('time', 'rot', 1), ('time', 'rust', 1),
    ('exposure', 'decay', 1), ('exposure', 'rot', 1), ('heat', 'decay', 1), ('heat', 'spoilage', 1),
    ('moisture', 'rot', 1), ('moisture', 'rust', 1), ('use', 'wear', 1), ('use', 'damage', 1),
    ('decay', 'freshness', -1), ('rot', 'food', -1), ('rot', 'freshness', -1), ('wear', 'strength', -1),
    ('wear', 'structure', -1), ('spoilage', 'food', -1), ('damage', 'function', -1), ('erosion', 'land', -1),
    ('mixing', 'concentration', -1), ('mixing', 'order', -1), ('disorder', 'order', -1),
    ('decay', 'structure', -1), ('burning', 'fuel', -1), ('rust', 'metal', -1), ('melting', 'ice', -1),
    ('melting', 'solid', -1),
]

# _SYN: surface/synonym -> canonical formal-model node.
_SYN: Dict[str, str] = {
    'co2': 'carbon dioxide', 'carbon-dioxide': 'carbon dioxide', 'h2o': 'water', 'moisture': 'water',
    'o2': 'oxygen', 'dioxygen': 'oxygen', 'sugar': 'glucose', 'sugars': 'glucose', 'carbohydrate': 'glucose',
    'sunlight': 'light', 'sun': 'light', 'sunshine': 'light', 'solar': 'light', 'atp': 'energy',
    'vapor': 'water vapor', 'vapour': 'water vapor', 'steam': 'water vapor', 'clouds': 'cloud',
    'precipitation': 'rain', 'rainfall': 'rain', 'nutrients': 'nutrient', 'meal': 'food', 'predators': 'predator',
    'plants': 'plant', 'tree': 'plant', 'trees': 'plant', 'seeds': 'seed', 'wood': 'carbon', 'coal': 'carbon',
    'rocks': 'rock', 'minerals': 'mineral', 'push': 'force', 'pull': 'force', 'pressure': 'pressure',
    'movement': 'motion', 'moving': 'motion', 'velocity': 'speed', 'fast': 'speed', 'faster': 'speed',
    'slow': 'speed', 'acceleration': 'acceleration', 'temperature': 'temperature', 'temp': 'temperature',
    'warmth': 'heat', 'hot': 'heat', 'warm': 'heat', 'cold': 'cold', 'cool': 'cooling', 'cooling': 'cooling',
    'friction': 'friction', 'gravity': 'gravity', 'weight': 'weight', 'heavy': 'weight', 'mass': 'mass',
    'height': 'height', 'altitude': 'height', 'tall': 'height', 'slope': 'slope', 'steep': 'slope',
    'energy': 'energy', 'power': 'energy', 'brightness': 'brightness', 'bright': 'brightness',
    'visibility': 'visibility', 'distance': 'distance', 'decay': 'decay', 'rot': 'rot', 'rotting': 'rot',
    'wear': 'wear', 'erosion': 'erosion', 'erode': 'erosion', 'disorder': 'disorder', 'entropy': 'disorder',
    'diffusion': 'diffusion', 'spread': 'mixing', 'flood': 'flood', 'flooding': 'flood', 'flow': 'flow',
    'wind': 'wind', 'vegetation': 'vegetation', 'volume': 'volume', 'expansion': 'expansion',
    'expand': 'expansion', 'melt': 'melting', 'melting': 'melting', 'evaporation': 'evaporation',
    'evaporate': 'evaporation', 'freezing': 'freezing', 'freeze': 'freezing', 'insulation': 'insulation',
    'work': 'work', 'depth': 'depth', 'deep': 'depth', 'area': 'area', 'time': 'time',
    'concentration': 'concentration', 'growth': 'growth', 'grow': 'growth', 'grows': 'growth',
    'growing': 'growth', 'size': 'size', 'bigger': 'size', 'survival': 'survival', 'survive': 'survival',
    'survives': 'survival', 'live': 'survival', 'alive': 'survival', 'die': 'survival', 'death': 'survival',
    'population': 'population', 'offspring': 'offspring', 'baby': 'offspring', 'young': 'offspring',
    'reproduce': 'offspring', 'reproduction': 'offspring', 'mate': 'mate', 'mating': 'mate', 'health': 'health',
    'healthy': 'health', 'sick': 'disease', 'sickness': 'disease', 'illness': 'disease', 'disease': 'disease',
    'strength': 'strength', 'strong': 'strength', 'exercise': 'exercise', 'rest': 'rest', 'predator': 'predator',
    'prey': 'prey', 'habitat': 'habitat', 'competition': 'competition', 'compete': 'competition',
    'shelter': 'shelter', 'weathering': 'weathering', 'eruption': 'eruption', 'erupt': 'eruption',
    'storm': 'storm', 'surface': 'surface', 'smooth': 'surface', 'decays': 'decay', 'decompose': 'decay',
    'rotten': 'rot', 'spoil': 'spoilage', 'spoils': 'spoilage', 'spoilage': 'spoilage', 'spoiled': 'spoilage',
    'worn': 'wear', 'damage': 'damage', 'damaged': 'damage', 'broken': 'damage', 'break': 'damage',
    'rust': 'rust', 'rusts': 'rust', 'rusting': 'rust', 'waste': 'decay', 'wasted': 'decay',
    'fresh': 'freshness', 'freshness': 'freshness', 'mess': 'disorder', 'messy': 'disorder', 'order': 'order',
    'mix': 'mixing', 'mixing': 'mixing', 'mixed': 'mixing', 'disperse': 'mixing', 'degrade': 'decay',
    'exposure': 'exposure', 'expose': 'exposure', 'exposed': 'exposure', 'use': 'use', 'used': 'use',
    'using': 'use', 'structure': 'structure', 'function': 'function', 'metal': 'metal', 'ice': 'ice',
    'solid': 'solid', 'land': 'land',
}


def _stem(w: str) -> str:
    for suf in ("ing", "ed", "es", "er", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: -len(suf)]
    return w


def _build_edge_store() -> Dict[str, Dict[str, List]]:
    """edges[c][e] = list of [sign, context_frozenset, is_physics]. Reaction context = all participants; a physics
    influence has empty context (gated on the passage being a physics context). Byte-faithful to the solution's
    build_ctx_store (scramble path omitted -- that is a control, not a live read)."""
    edges: Dict[str, Dict[str, List]] = defaultdict(lambda: defaultdict(list))
    for reactants, products in REACTIONS:
        ctx = frozenset(reactants) | frozenset(products)
        for r in reactants:
            for p in products:
                edges[r][p].append([1, ctx, False])
        for r in reactants:
            for r2 in reactants:
                if r != r2:
                    edges[r][r2].append([-1, ctx, False])
        for p in products:
            for p2 in products:
                if p != p2:
                    edges[p][p2].append([1, ctx, False])
    for c, e, s in INFLUENCES:
        edges[c][e].append([s, frozenset(), True])
    return edges


_EDGES: Dict[str, Dict[str, List]] = _build_edge_store()
_NODES: Set[str] = set(_EDGES) | {e for c in _EDGES for e in _EDGES[c]}
_PHYS_NODES: Set[str] = {e for (_c, e, _s) in INFLUENCES} | {c for (c, _e, _s) in INFLUENCES}


def ground_concepts(concepts: Sequence[str]) -> Set[str]:
    """Map surface concepts to the formal-model nodes they instantiate (synonym + stem)."""
    out: Set[str] = set()
    for c in concepts:
        cl = c.lower(); st = _stem(cl)
        for v in (cl, st):
            if v in _SYN:
                out.add(_SYN[v])
            if v in _NODES:
                out.add(v)
    return out


def _gated_sign(Xc: Set[str], Yc: Set[str], passage: Set[str]) -> Tuple[int, bool]:
    """Passage-context-gated formal coupling X->Y (byte-faithful to the solution's gated_sign). Returns
    (sign in {+1,-1,0}, covered). A chemical edge fires only if the passage supplies the reaction's context; a
    physics edge only if the passage is a physics context (>=2 physics quantities). 1-hop via a present mediator."""
    phys_ctx = len(passage & _PHYS_NODES) >= 2
    best = 0
    for x in Xc:
        for y in Yc:
            for (s, ctx, is_phys) in _EDGES.get(x, {}).get(y, []):
                ok = phys_ctx if is_phys else (len((ctx - {x, y}) & passage) >= 1)
                if ok and best == 0:
                    best = s
    if best != 0:
        return best, True
    for x in Xc:
        for m in _EDGES.get(x, {}):
            if m not in passage:
                continue
            for (s1, ctx1, ip1) in _EDGES[x][m]:
                ok1 = phys_ctx if ip1 else (len((ctx1 - {x, m}) & passage) >= 1)
                if not ok1:
                    continue
                for y in Yc:
                    for (s2, ctx2, ip2) in _EDGES.get(m, {}).get(y, []):
                        ok2 = phys_ctx if ip2 else (len((ctx2 - {m, y}) & passage) >= 1)
                        if ok2 and best == 0:
                            best = s1 * s2
    return best, best != 0


def causal_edge_sign(x_concepts: Sequence[str], y_concepts: Sequence[str],
                     passage_concepts: Sequence[str]) -> Tuple[int, bool]:
    """THE LIVE READ. Given a causal edge X->Y (as surface concept lists) and the passage's concepts, return
    (more/less SIGN in {+1 increase, -1 decrease, 0}, covered). `covered=False` is an HONEST ABSTAIN (no gated
    formal coupling applies -> the caller falls back to its other channels; ~87% everyday/social tail). The sign,
    when covered, is the falsifier-beating formal-model direct-influence sign, passage-context-gated."""
    Xc = ground_concepts(x_concepts)
    Yc = ground_concepts(y_concepts)
    if not Xc or not Yc:
        return 0, False
    passage = ground_concepts(passage_concepts)
    return _gated_sign(Xc, Yc, passage)


class CausalSignChannel:
    """Object surface for the reader to hold (like sm.causal_reasoner): `.edge_sign(x, y, passage)`. Stateless
    over the shared formal-model store; instantiating it is free."""

    def edge_sign(self, x_concepts: Sequence[str], y_concepts: Sequence[str],
                  passage_concepts: Sequence[str]) -> Tuple[int, bool]:
        return causal_edge_sign(x_concepts, y_concepts, passage_concepts)


__bf_status__ = "BF_SPIRIT"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = ("2026-09-10 grown-knowledge LIVE ingest from grow_the_causal_mechanism (owner-DONE, STRONG): the "
                   "formal-model more/less edge-sign (stoichiometry + physics + thermo/entropy), passage-context-gated "
                   "= the FIRST sign source to beat the scrambled falsifier CI-sep (WIQA science slice +0.157, 14.2% "
                   "cov); prose sign sources all TIE the falsifier (CHT, durable negative); strategy first-hand")
__bf_note__ = ("Forbus QP DIRECT-influence sign (storable) computed from runnable-model STRUCTURE (reaction "
               "stoichiometry / physics / entropy couplings, curated offline FOUNDATION); passage-context gate = "
               "Kintsch construction-integration instantiation (generic knowledge selected by the specific text). "
               "Science slice ~14% coverage; honest abstain (covered=False) on the everyday/social tail (-> grounded "
               "Delta-Delta world-model). NET/regime signs NOT here (Forbus: need simulation). NO prose sign source "
               "(they tie the falsifier). Scale-up = Rhea/BioModels/ecological (registered).")


if __name__ == "__main__":
    # force->motion is +1 in a physics context; friction->speed is -1; abstain off-domain.
    s1, c1 = causal_edge_sign(["force"], ["motion"], ["force", "motion", "speed", "friction"])
    assert c1 and s1 == 1, (s1, c1)
    s2, c2 = causal_edge_sign(["friction"], ["speed"], ["force", "friction", "speed", "motion"])
    assert c2 and s2 == -1, (s2, c2)
    s3, c3 = causal_edge_sign(["happiness"], ["weather"], ["happiness", "weather"])
    assert not c3, ("off-domain must abstain", s3, c3)
    print("SELFTEST PASS: causal_sign_channel force->motion=+1, friction->speed=-1, off-domain abstains; "
          "nodes=%d reactions=%d influences=%d" % (len(_NODES), len(REACTIONS), len(INFLUENCES)), flush=True)
