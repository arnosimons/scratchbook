import re
from globals import FORMULA_SYMBOLS

### Tutorials
##############################################################################

static_links = {
    'ab': 'nqzwiWkKV_s',
    'aqua': '7GXOhZbuvIg',
    'boom': 'c2IrbYGs0eU',
    'boom_roll': 'c2IrbYGs0eU',
    'brbhp': 'REVf6rnZPBc',
    'cboom': '5mB80n1sZmo',
    'cf1': 'DUaY6gMONmA',
    'cogf': 'DPC6LJar6DY',
    'cogf_roll': 'DPC6LJar6DY',
    'cts': 'FllVjK2nv3c',
    'delete': 'Hpzb9wALU04',
    'dr': 'rtqTmUVjsuY',
    'eg': 'fPOTkGvLtL0',
    'eg_roll': 'fPOTkGvLtL0',
    'hg': 'OVZxorYLHj8',
    'hg_roll': 'OVZxorYLHj8',
    'hp_roll': 'wmiTMz8XViE',
    'internet': '_mxSbVy6y8Y',
    'jc': 'lV5SPCaAnMM',
    'k': 'rQnMymtQ9sg',
    'mf1': 'XbU7whSfp-c',
    'mf2': 'XbU7whSfp-c',
    'mt': 'GpT1Y1aMlWw',
    'of1_i_21': 'V1owPZNNMPI',
    'pr': 'B32m9Jqqrpo',
    'pr_roll': 'B32m9Jqqrpo',
    'rl': 'iMHKliaY7BU',
    'sc': 'rtqTmUVjsuY',
    'scf1': '7zHJShFI7uM',
    'scf2': '7zHJShFI7uM',
    'sf': 'h3o5OTIy-kQ',
    'slico1': 'B_iOaAguNuo',
    'slico2': 'B_iOaAguNuo',
    'spair': 'xxhZ45KcMCY',
    'square': 'qkh_EgsZt3M',
    'ss': '6ZHYnUdPw3g',
    'ta1': '-kuVk_wyNAg',
    'ta1_roll': '-kuVk_wyNAg?t=17',
    'ta2': 'JRaUuXhw6Qk',
    'tt': '7I8ezdTaq88',
    'uzi': 'YjtVcQ39QrU',
    'x': 'aVgurUuDDSw&t=369s',
}

def base(name):
    return re.sub(r"Log|Ex|[DASQ\d]", "", name)

def baseN(name):
    return re.sub(r"Log|Ex|[DASQ]", "", name)

def get_tutorial(name, codebook):
    if name in codebook:
        code = codebook[name]
        if not any(i in code for i in FORMULA_SYMBOLS):
            name = code
    # static links
    if name in static_links:
        return static_links[name]
    # dynamic links
    baseNk = "_".join([baseN(part) for part in name.split("_")[:2]])
    basek = "_".join([base(part) for part in name.split("_")[:2]])
    if baseNk in ["b_b", "b"]:
        return "rtqTmUVjsuY" # Babies
    elif baseNk in ["f1_f1", "f1"]:
        return "irNJitl6xpc" # 1-Click Flares
    elif baseNk in ["f2_f2", "f2"]:
        return  "x-GqD3eH36g" # 2-Click Flares
    elif baseNk in ["f3_f3", "f3"]: 
        return  "x-GqD3eH36g" # 3-Click Flares
    elif basek in ["tr_tr", "tr"]:
        return "XdkNAePjM7o" # Transformers
    elif baseNk == "of1_i_21":
        return "V1owPZNNMPI" # OG Flare
    elif basek == "d_g":
        return "Fl-JlMxQlxc" # Stabs
    elif basek == "o_i": 
        return "pKe3OUKaK2k" # Chirps
    elif basek == "t" or basek == "t_t":
        return "WN8ity9B35U" # Faderless Tears
    return ""

if __name__ == "__main__":

    from construction import make_elementary_scratch, make_scratch
    from construction import tear_to_formula, orbit_to_formula
    from analysis import get_info
    import json

    ### Helper Functions 
    ##############################################################################

    def makeLib(f, names):
        lib = {}
        for name in names:
            formula = f(name) if not f == make_elementary_scratch else name
            row = get_info(make_scratch(formula))
            row["Name(s)"] = name
            row["Formula"] = formula
            lib[name] = row
        return lib

    ### ELEMENTS library
    ##############################################################################

    fN, trN = 3, 4
    fs = [f"{io}f{n}{dasq}" for n in range(1, fN + 1) for io in ["", "i", "o"] 
        for dasq in ["", "D", "A", "S", "Q"] if not f"{io}f{n}{dasq}" in [
        "f1S", "f1Q", "if1S", "if1Q", "of1S", "of1Q",]]
    trs = [f"tr{n}{dasq}" for n in range(2, trN + 1) 
        for dasq in ["", "D", "A", "S", "Q"] if not f"tr{n}{dasq}" in [
        "tr2S", "tr2Q",]]
    names = ["h", "gh", "g"] + [f"{base}{crv}" 
        for base in ["b", "i", "o", "d"] + fs + trs for crv in [
        "", "Ex", "Log"]]
    ELEMENTS = makeLib(make_elementary_scratch, names)

    # Add aliases for elements:

    for v in ELEMENTS.values():
        if v["Name(s)"].startswith("b"):
            v["Name(s)"] = "baby" + v["Name(s)"][1:] + ", " + v["Name(s)"]
        elif v["Name(s)"].startswith("f"):
            v["Name(s)"] = "flare" + v["Name(s)"][1:] + ", " + v["Name(s)"]
        elif v["Name(s)"].startswith("if"):
            v["Name(s)"] = "iflare" + v["Name(s)"][2:] + ", " + v["Name(s)"]
        elif v["Name(s)"].startswith("of"):
            v["Name(s)"] = "oflare" + v["Name(s)"][2:] + ", " + v["Name(s)"]
        elif v["Name(s)"].startswith("i"):
            v["Name(s)"] = "in" + v["Name(s)"][1:] + ", " + v["Name(s)"]
        elif v["Name(s)"].startswith("o"):
            v["Name(s)"] = "out" + v["Name(s)"][1:] + ", " + v["Name(s)"]
        elif v["Name(s)"].startswith("d"):
            v["Name(s)"] = "dice" + v["Name(s)"][1:] + ", " + v["Name(s)"]
        elif v["Name(s)"].startswith("tr"):
            v["Name(s)"] = "transformer" + v["Name(s)"][2:] + ", " + v["Name(s)"]
        elif v["Name(s)"].startswith("gh"):
            v["Name(s)"] = "ghosthold, ghold, " + v["Name(s)"]
        elif v["Name(s)"].startswith("h"):
            v["Name(s)"] = "hold, " + v["Name(s)"]
        elif v["Name(s)"].startswith("g"):
            v["Name(s)"] = "ghost, " + v["Name(s)"]

    ### TEARS library
    ##############################################################################

    tN = 3
    names = [f"{base}t{n}{crv}" for n in range(2, tN + 1) 
            for base in ["", "i", "o", "d", "if", "of", "tr"]
            for crv in ["", "Ex", "Log"] ]
    TEARS = makeLib(tear_to_formula, names)
    TEARS

    ### ORBITS library
    ##############################################################################

    base_names = ["g_d", "b_b", "i_o", "o_i", "d_d", "d_g"]
    f_names = [
        f'b_f{n}_1{n+1}'
        for pair in ["b_f", "i_of", "o_if"]
        for n in range(1, fN + 1)
        ] + [
        f'{l}{n}_{r}_{n+1}1' 
        for l,r in [["f","b"], ["if","o"], ["of","i"]]
        for n in range(1, fN + 1)
        ] + [
        f'{l}{n}_{r}{m}{f"_{n+1}{m+1}" if not n == m else ""}' 
        for n in range(1, fN + 1)
        for m in range(1, fN + 1)
        for l, r in [["f","f"], ["if","of"], ["of","if"]]
        ] 
    tr_names = [
        f"{el}_tr{n}_1{n}" 
        for el in "gb"
        for n in range(2, trN + 1)
        ] + [
        f'tr{n}_{el}_{n}1'
        for el in "gb"
        for n in range(2, trN + 1)
        ] + [
        f'tr{n}_tr{m}{f"_{n}{m}" if not n == m else ""}' 
        for n in range(2, trN + 1)
        for m in range(2, trN + 1)
        ]
    names = base_names + f_names + tr_names
    # Add Ex Log to all orbits:
    names += [
        f'{p.split("_")[0]}{l}_{p.split("_")[1]}{r}{"_" + p.split("_")[2] if p.split("_")[2:] else ""}'
        for p in names
        for l in ["", "Ex", "Log"] for r in ["", "Ex", "Log"]
        if not l == r == ""
    ]
    ORBITS = makeLib(orbit_to_formula, names) 

    ### Codebook
    ##############################################################################

    codebook = {

        # Aliases for orbits: 

        "bo":"b_b",
        "babyorbit":"b_b",
        
        "s":"i_o",
        "slice":"i_o",
        
        "c":"o_i",
        "chirp":"o_i",

        "do":"d_d",
        "diceorbit":"d_d",

        "st":"d_g",
        "stab":"d_g",

        "offst":"g_d", # <------ Do I need this scratch?
        "offstab":"g_d", # <------ Do I need this scratch?
        
        "tr2o":"tr2_tr2",
        "trob1":"tr2_tr2",
        "transformerorbit2":"tr2_tr2",
        
        "f1o":"f1_f1",
        "flob1":"f1_f1",
        "flareorbit1":"f1_f1",

        "f2o":"f2_f2",
        "flob2":"f2_f2",
        "flareorbit2":"f2_f2",

        "f3o":"f3_f3",
        "flob3":"f3_f3",
        "flareorbit3":"f3_f3",

        "ogf":"of1_i_21",
        "ogflare":"of1_i_21",

        # Formulas and aliases for combos:

        "cf1":"(c / (1/3) + flob1 / (2/3)) / 2",
        "chirpflare1":"cf1",
        
        "cf2":"c / (1/2) + flob2 / (3/2)",
        "chirpflare2":"cf2",

        "cf3":"(c/(2/5) + f3_f3/(8/5)) / 2",
        "chirpflare3":"cf3",

        "cogf":"(c/.5 + ogf/(3/4)) / 1",
        "chirpogflare":"cogf",
        
        "cogf_roll":"(cogf/1.25) * 4",
        "chirpogflare_roll":"cogf_roll",

        "rawogf":"of1_i",
        "rawogflare":"of1_i",

        "hp":"f1_f2_23",
        "hippo":"f1_f2_23",
        "hippopotamus":"f1_f2_23",    
        
        "hp_roll":"hp * 4",
        "hippo_roll":"hp_roll",
        "hippopotamus_roll":"hp_roll",
        
        "rawhp":"f1_f2",
        "rawhippo":"f1_f2",
        "rawhippopotamus":"f1_f2",

        "brbhp":"bo/.5 + f2/(3/4) + -f1/.5 + h/.25",
        "brbhippopotamus":"brbhp",

        "ta1":"-iLog_of1Log_12",  
        "tazer1":"ta1",

        "ta1_roll":"(ta1 //.5 / .75) * 4",
        "tazer1_roll":"ta1_roll",

        "ta2":"-iLog_of2Log_13",
        "tazer2":"ta2",

        "ta2_roll":"(ta2 * 3) / 4",
        "tazer2_roll":"ta2_roll",

        "sc":"bo * 2 / 1",
        "scribble":"sc",

        "dr":"bo * 4 / 1 // 0.5",
        "drills":"dr",

        "uzi":"bo * 8 / 1 // 0.25",
        
        "mt":"st/.25 + (i + -b + o + -g)/.5//.5 + st/.25 + (i + -b + o + -g)/.5//.5 + st/.25 + gh/.25",
        "military":"mt",
        
        "k":"(c + c) /.5 + flob1 / .5",
        "kermit":"k",
        
        "sf":"(s + do) / 1",
        "swingflare":"sf",
        
        "pr":"(oft1 + -(s//1) + -ift1) / 1 // .75",
        "prizm":"pr",

        "pr_roll":"(pr / 1.5) * 2",
        "prizm_roll":"pr_roll",
        
        "boom":"(s + d/0.5//0.5 + -s + -d/0.5//0.5) / 2",
        "boomerang":"boom",

        "boom_roll":"(boom/(1.5)) * 2",
        "boomerang_roll":"boom_roll",

        "cboom":"c/.5 + (boom%4)/1.5",
        "chirpboom":"cboom",
        "chirpboomerang":"cboom",
        
        "ab":"s/(2/3)//(1/3) + d/(1/3)//(1/3) + (s/(2/3)//(1/3))**(1/3) + (trt1//(2/3)/(2/3))**(1/3) + -trt1/(2/3)",
        "autobahn":"ab",

        "ss":"(s + g/0.5//0.5 + -s + -g/0.5//0.5) / 1",
        "seesaw":"ss",

        "stcr":"st/(1/3) + tr3/(1/2) + -g/(1/6)",
        "stabcrab":"stcr",

        "stcr_roll":"stcr / (9/12) * 16",
        "stabcrab_roll":"stcr_roll",

        "slico1":"(h/(1/8))**(1/3) + -s/(1/4)//(1/3) + (d/(1/8)//(1/3))**(1/3) + (s/(1/4)//(1/3))**(2/3) + (-ift1/(1/4)//(1/3))**(1/3)",
        "slicecombo1":"slico1",

        "slico2":"slico1[:-2] + -(d/(1/8)//(1/3))**(1/3) + -s/(1/4)//(1/3) + (d/(1/8)//(1/3))**(1/3) + (s/(1/4)//(1/3))**(2/3) + -(d/(1/8)//(1/6))**(3/6)  + -(s/(1/4)//(1/3))**(1/6) + (-i/(1/8)//(1/6))**(2/6)",
        "slicecombo2":"slico2",

        "rl":"(c/.5 + ogf/(3/4)) * 2 + c/.5 + ogf",
        "royalline":"rl",

        "eg":"flob1 + f1/.5 + -f2/(3/4)",
        "enneagon":"eg",

        "eg_roll":"eg * 4",
        "enneagon_roll":"eg_roll",
        
        "hg":"c/.5 + ogf/(3/4) + c/.5 + of1_if1",
        "hendecagon":"hg",

        "hg_roll":"hg * 4",
        "hendecagon_roll":"hg_roll",
        
        "tt":"(-i_of2_13 + (gh/(1/4))**1) * 4",
        "turntrans":"tt",
        "turnaroundtransform":"tt",
        
        "internet":"-b/.25 + bo/.5 + f1/.5 + -b/.25 + bo/.5 + b/.5 + -b/.25 + bo/.5 + f2/(3/4)",

        "x":"(f1//.5 + (f2//.5)**.5)/1 + -f3",
        "xenon":"x",

        "cts":"(t1 + -t1) / 1",
        "clovertears":"cts",

        'aqua':'boom % 4',
        'aquaman':'aqua',

        'sw':'(b + -t1) / 1',
        'swirl':'sw',

        "jc":"(c + sw + c) / 1",
        "joecooley":"jc",

        "delete":"(bo + f1 + -bo**.5 + -f1) / 2",

        "square":"((d//(1/3))**(1/3) + (s//(1/3))**(2/3) + -(d//(1/3))**(1/3) + -s//(1/3)) / 1",
        "squareflare":"square",

        "spair": "(bo + flob1) / 1",
        "spairflare": "spair",

        "mf1":"(f1 + -bo**.5 + -f1) / 1",
        "mflare1":"mf1",

        "mf2":"(f2 + -bo**.5 + -f2) / 1",
        "mflare2":"mf2",

        "scf1":"sc + flob1",
        "scribbleflare1":"scf1",

        "scf2":"sc + flob2",
        "scribbleflare2":"scf2",
    }

    ### COMBOS library
    ##############################################################################

    COMBOS = {}
    for k, v in codebook.items():
        if any(i in v for i in FORMULA_SYMBOLS): # any formula, excludes scratch names
            row = get_info(make_scratch(v, codebook))
            row["Name(s)"] = k
            row["Formula"] = v
            COMBOS[k] = row

    ### Feed aliases in the codebook to the libraries
    ##############################################################################

    for k, v in codebook.items():
        for lib in [ELEMENTS, TEARS, ORBITS, COMBOS]:
            if v in lib:
                lib[v]["Name(s)"] = f"{k}, " + lib[v]["Name(s)"]

    ### CORE library
    ##############################################################################

    CORE = {
        k:dict(v)
        for k, v in COMBOS.items()
    }

    CORE.update({
        k:dict(v)
        for k, v in ORBITS.items()
        if k in [
            "b_b", # baby-orbit
            "d_g", # stabs
            "d_d", # dice-orbit
            "i_o", # slice
            "o_i", # chirp
            "f1_f1", # flob1
            "f2_f2", # flob2
            "f3_f3", # 3 click flare
            "f1_f2_23", # hippo
            "f1_f2", # rawhippo
            "of1_i", # rawogf
            "of1_i_21", # ogflare
        ]
    })

    ### Export json
    ##############################################################################

    with open(f'resources/json/codebook.json', 'w') as file:
        json.dump(codebook, file)

    libraries = [
        [CORE, "CORE"],
        [ELEMENTS, "ELEMENTS"],
        [TEARS, "TEARS"],
        [ORBITS, "ORBITS"],
        [COMBOS, "COMBOS"],
    ]

    for lib, libname in libraries:
        for k, v in lib.items():
            v["Preview"] = f"""<img class='libraryPreview' src='/formulas/{k}/preview'>"""
            v["libraries"] = []
            for l, ln in libraries:
                # v[ln] = 1 if k in l else 0
                if k in l:
                    v["libraries"].append(ln)
        # d = {"data":list(lib.values())}
        print(f'Exporting "{libname}" lib with {len(lib)} rows')
        with open(f'resources/json/{libname}.json', 'w') as file:
            json.dump(list(lib.values()), file)

    


    ### Make COMBINED library and previews
    ##############################################################################
    COMBINED = {**ELEMENTS, **TEARS, **ORBITS, **COMBOS} # no need for CORE here
    
    # for name, d in COMBINED.items():
    #     fig = make_scratch(d["Formula"], codebook).preview()
    #     fig.savefig(f'resources/previews/{name}.png', format="png")

    COMBINED = list(COMBINED.values()) # make list now
    print(f'Exporting "COMBINED" lib with {len(COMBINED)} rows')
    with open(f'resources/json/COMBINED.json', 'w') as file:
        json.dump(COMBINED, file)