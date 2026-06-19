"""Build long-night GPU batch: Path-B KBLaM variations with DISCRIMINATIVE facts (fixes encoder-mismatch root cause) + E7 calibration.
Variants per research_drill_path_b_variations_5x: discriminative-data re-de-risk, 1-layer vs every-layer (1.2), +contrastive (1.3), scale."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
KB = (EXP / "exp_t5c_factkb_kblam_heldout_gpu_v1.py").read_text(encoding="utf-8")

# discriminative real-word subject pool (distinct semantics -> distinct frozen-bge-large keys; the de-risk used adj+noun in a
# fixed template that embedded near-identically -- root cause per drill 1.1 encoder-mismatch). Bare distinct nouns across categories.
POOL_DEF = '''
DISC_POOL = ("aardvark albatross alligator antelope armadillo baboon badger barracuda beaver bison buffalo camel "
    "capybara caribou cheetah chimpanzee cobra cougar coyote crocodile dolphin elephant falcon ferret flamingo gazelle "
    "giraffe gorilla hedgehog hippopotamus hyena iguana jackal jaguar kangaroo koala lemur leopard llama lobster lynx "
    "manatee meerkat mongoose moose narwhal ocelot octopus opossum orangutan ostrich otter panther pelican penguin "
    "platypus porcupine puffin raccoon reindeer rhinoceros salamander scorpion seahorse sloth squid stingray tapir "
    "tarantula toucan vulture walrus weasel wolverine wombat "
    "amsterdam antwerp athens bangkok barcelona beirut belgrade bergen bologna bordeaux bremen brisbane bruges "
    "budapest cairo calgary canberra cardiff chennai copenhagen cordoba dakar damascus dresden dublin durban edinburgh "
    "florence geneva glasgow granada hamburg helsinki istanbul jakarta jerusalem karachi kyoto lagos lisbon ljubljana "
    "lyon madras marseille melbourne montreal nairobi naples nantes oslo ottawa palermo perth porto prague quebec "
    "reykjavik riga rotterdam salzburg santiago sapporo seville stockholm stuttgart tangier tbilisi toulouse "
    "valencia valparaiso venice verona warsaw wellington zagreb zurich "
    "almond apricot artichoke asparagus avocado basil beetroot blackberry blueberry broccoli cardamom cashew "
    "cauliflower celery cherry chestnut chickpea cilantro cinnamon clementine coconut coriander cranberry cucumber "
    "currant eggplant fennel ginger grapefruit hazelnut jackfruit kiwi kumquat lavender leek lemongrass lentil "
    "lychee mandarin mango marjoram molasses nectarine nutmeg oregano papaya paprika parsnip peppercorn persimmon "
    "pistachio plantain pomegranate pumpkin quince radish raspberry rhubarb rosemary rutabaga saffron scallion "
    "shallot spinach tamarind tangerine tarragon thyme turmeric turnip vanilla watercress zucchini "
    "accordion balalaika banjo bassoon bagpipe bongo carillon cello clarinet clavichord cornet didgeridoo dulcimer "
    "fiddle flute glockenspiel harmonica harp harpsichord kazoo lute mandolin marimba oboe ocarina piccolo "
    "saxophone sitar tambourine theremin trombone trumpet tuba ukulele vibraphone viola violin xylophone zither").split()
'''

# discriminative make_facts (bare distinct real-word subject; ~600 pool -> sample N distinct)
OLD_MF_START = "def make_facts(tok, g):"
OLD_MF = KB[KB.index(OLD_MF_START): KB.index("def run() -> Dict:")]
NEW_MF = POOL_DEF + '''
def make_facts(tok, g):
    pool = [" violet"," copper"," seven"," marble"," thunder"," willow"," saffron"," glacier"," ember"," quartz",
            " orchid"," harvest"," lantern"," meadow"," falcon"," cinnamon"," velvet"," anchor"," prism"," cobalt",
            " maple"," jupiter"," canyon"," ribbon"," basalt"," nectar"," pebble"," cypress"," marlin"," walnut",
            " amber"," crimson"," silver"," forest"," ocean"," desert"," tiger"," eagle"," raven"," otter"]
    pool = [a for a in pool if len(tok(a, add_special_tokens=False)["input_ids"]) == 1]
    subs = list(dict.fromkeys(DISC_POOL)); g.shuffle(subs)
    if N_FACTS > len(subs):
        subs = (subs * ((N_FACTS // len(subs)) + 1))
    subs = subs[:N_FACTS]
    facts = []
    for i, s in enumerate(subs):
        ans = pool[int(g.integers(0, len(pool)))]
        prompt = "The secret code of %s is" % s; enc_text = "The secret code of %s is%s" % (s, ans)
        facts.append({"subj": s, "prompt": prompt, "aid": tok(ans, add_special_tokens=False)["input_ids"][0], "ans": ans, "enc_text": enc_text})
    return facts

'''

variants = [
    ("t5c_kblam_disc_everylayer_gpu_v1", "every", 2000),   # proper re-de-risk: discriminative + every-layer (KBLaM)
    ("t5c_kblam_disc_1layer_gpu_v1", "single", 2000),      # drill 1.2: 1-layer predicted to win at small scale
    ("t5c_kblam_disc_scale_gpu_v1", "every", 4000),        # scale toward KBLaM regime (more facts)
]
for anchor, layermode, nfacts in variants:
    s = KB.replace("t5c_factkb_kblam_heldout_gpu_v1", anchor).replace("t5c-factkb-kblam-heldout", anchor.replace("_", "-"))
    s = s.replace(OLD_MF, NEW_MF)
    s = s.replace("N_FACTS = 300 if SMOKE else 2000", "N_FACTS = 300 if SMOKE else %d" % nfacts)
    if layermode == "single":
        # hook only the middle layer instead of every layer (drill 1.2)
        s = s.replace("hooks = [mdl.gpt_neox.layers[Li].attention.register_forward_hook(mk(Li), with_kwargs=True) for Li in range(NL)]",
                      "hooks = [mdl.gpt_neox.layers[Li].attention.register_forward_hook(mk(Li), with_kwargs=True) for Li in [6]]  # drill 1.2: single mid layer")
    (EXP / ("exp_" + anchor + ".py")).write_text(s, encoding="utf-8"); print("wrote", anchor, layermode, nfacts)
