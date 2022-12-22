import re
from classes import Curve, Element, Scratch
import numpy as np


### Curves
##############################################################################

L = Curve(lambda x: np.zeros(len(x)))

S = Curve(lambda x: (-np.cos(x * np.pi) + 1) / 2)

SLogScaler = -1 
SLog = Curve(lambda x: (0.5 + np.sin(x * np.pi - np.pi / 2) / 2) ** ((2 * (1 - x)) ** SLogScaler))

SExScaler = 1
SEx = Curve(lambda x: (0.5 + np.sin(x * np.pi - np.pi / 2) / 2) ** ((2 * (1 - x)) ** SExScaler))

ExScaler = 10
Ex = Curve(lambda x: (np.exp(ExScaler * x) - 1) / (np.exp(ExScaler) - 1))

LogScaler = 100
Log = Curve(lambda x: np.log(LogScaler * x + 1) / np.log(LogScaler + 1))


### Elementary scratch constructor
##############################################################################

def fcl_strings(n, dasq):
    if not dasq:
        return [f'{i}/{n+1}' for i in range(1, n+1)]
    if dasq == "D":
        return [f'{i}/{n+2}' for i in range(1, n+1)]
    if dasq == "A":
        return [f'{i+1}/{n+2}' for i in range(1, n+1)]
    if dasq == "S":
        if n % 2 == 0:
            left =  [f'{i}/{n+2}' for i in range(1, int(n/2)+1)]
            right = [f'{i+1}/{n+2}' for i in range(int(n/2)+1, int(n/2)*2+1)]
            return  left + right
        else:
            left =  [f'{i}/{n+2}' for i in range(1, int(n/2)+1)]
            middle = ["1/2"]
            right = [f'{i+2}/{n+2}' for i in range(int(n/2)+1, int(n/2)*2+1)]
            return  left + middle + right
    if dasq == "Q":
        return  [f'{i+1}/{n+3}' for i in range(1, n+1)]

def make_elementary_scratch(name):
    _h = "(?P<h>h(?:old)?)"
    _gh = "(?P<gh>g(?:host)?h(?:old)?)"
    _g = "(?P<g>g(?:host)?)"
    _b = "(?P<b>b(?:aby)?)"
    _i = "(?P<i>i(?:n)?)"
    _o = "(?P<o>o(?:ut)?)"
    _d = "(?P<d>d(?:ice)?)"
    _f = "(?P<f>f(?:lare)?\d)"
    _if = "(?P<if>if(?:lare)?\d)"
    _of = "(?P<of>of(?:lare)?\d)"
    _df = "(?P<df>df(?:lare)?\d)" # allow as well...?
    _tr = "(?P<tr>tr(?:ansformer)?\d)"
    _D = "(?P<D>D)"
    _A = "(?P<A>A)"
    _S = "(?P<S>S)"
    _Q = "(?P<Q>Q)"
    _Ex = "(?P<Ex>Ex)"
    _Log = "(?P<Log>Log)"
    ELS = re.compile(fr"(?:{_h}|{_gh})$|(?:{_g}|{_b}|{_i}|{_o}|{_d}|(?:{_f}|{_if}|{_of}|{_df}|{_tr})(?:{_D}|{_A}|{_S}|{_Q})?)(?:{_Ex}|{_Log})?$")
    m = ELS.match(name)
    if not m:
        raise ValueError(f'unintelligible name: "{name}"')
    dic = m.groupdict()
    dic = {k:True if v else False for k,v in dic.items()}
    l, h, ys = 1, 1, 0 # default
    crv, crvc = "S", "k" # default
    cl = [] # default
    if dic["h"]:
        crv = "L"
    elif dic["gh"]:
        crv = "L"
        crvc = "w"
    elif dic["g"]:
        crvc = "w"
    else:
        if dic["Log"]:
            crv = "Log"
        elif dic["Ex"]:
            crv = "Ex"
        if dic["i"] or dic["d"] or dic["if"] or dic["tr"] or dic["df"]:
            cl.append("0")
        m = re.match(r"(?:[iod]?f(?:lare)?(?P<fN>\d)|tr(?:ansformer)?(?P<trN>\d))(?P<DASQ>[DASQ])?", name)
        if m:
            md = m.groupdict()
            n = int(md["fN"]) if md["fN"] else int(md["trN"]) - 1
            cl += fcl_strings(int(n), md['DASQ'])
        if dic["o"] or dic["d"] or dic["of"] or dic["tr"] or dic["df"]:
            cl.append("1")
        cl = f'[{", ".join(cl)}]'
    scratch = f"Scratch([Element(curve={crv}, clicks={cl}, xflip=False, yflip=False, length=1, height=1, lift=0, color='{crvc}')])"
    return scratch

 
### Tear constructor
##############################################################################

def tearParts(steps, el):
    if int(steps) <= 1:
        raise ValueError("Steps must be an int > 1")
    return [
        f"({el}/(1/{steps})//(1/{steps})){f'**({i}/{steps})' if not i==0 else ''}" 
        for i in range(steps)]

def tear_to_formula(name):
    _t = "(?P<t>((?P<ft>f)|(?P<trt>tr))?t(?:ear)?(?P<tN>\d))"
    _i = "(?P<i>i)"
    _o = "(?P<o>o)"
    _d = "(?P<d>d)"
    _iod = f"(?:{_i}|{_o}|{_d})"
    _crv = "(?P<crv>Ex|Log)"
    TRS = re.compile(fr"{_iod}?{_t}{_crv}?(?:__(?P<el>(?:d?f(?:lare)?\d|tr(?:ansformer)?\d)[DASQ]?))?$")
    m = TRS.match(name)
    if not m or name.startswith("otr") or name.startswith("itr"):
        raise ValueError(f'unintelligible name: "{name}"')
    dic = m.groupdict()
    if dic["el"]:
        dic["el"] = f'{dic["el"]}{dic["crv"] or ""}'
    else:
        if dic["trt"]:
            dic["el"] = f'd{dic["crv"] or ""}' 
        else:
            dic["el"] = f'b{dic["crv"] or ""}'    
    parts = tearParts(int(dic['tN']) + 1, dic['el']) # <--- tN means N + 1 slices (like sounds in flares)
    # handle clicks between tear parts
    if dic["ft"] or dic["trt"]:
        if dic["el"].startswith("b"):
            parts[0] = parts[0].replace("b", "o")
            parts[-1] = parts[-1].replace("b", "i")
        elif dic["el"].startswith("f"):
            parts[0] = parts[0].replace("f", "of")
            parts[-1] = parts[-1].replace("f", "if")
        for i in range(1, len(parts)-1):
            if dic["el"].startswith("b"):
                parts[i] = parts[i].replace("b", "d")
            elif dic["el"].startswith("f"):
                parts[i] = parts[i].replace(
                    f'f{dic["el"][1]}', f'tr{int(dic["el"][1]) + 1}')          
    # handle iod clicks
    elements = [re.sub(r"[-+*/%~\[\]\(\).:]|\b\d*\b", " ", i).strip() 
        for i in parts]
    if (dic["i"] or dic["d"] or dic["trt"]) and not any(
        dic["el"].startswith(i) for i in ["i","d","tr"]):
        if elements[0].startswith("b"):
            parts[0] = parts[0].replace("b", "i")
        elif elements[0].startswith("of"):
            parts[0] = parts[0].replace(
                f'of{dic["el"][1]}', f'tr{int(dic["el"][1]) + 1}')
        elif elements[0].startswith("o"):
            parts[0] = parts[0].replace("o", "d").replace("Ldg", "Log")            
        elif elements[0].startswith("f"):
            parts[0] = parts[0].replace("f", "if")
    if (dic["o"] or dic["d"] or dic["trt"]) and not any(
        dic["el"].startswith(i) for i in ["o","d","tr"]):
        if elements[-1].startswith("b"):
            parts[-1] = parts[-1].replace("b", "o")
        elif elements[-1].startswith("if"):
            parts[-1] = parts[-1].replace(
                f'if{dic["el"][1]}', f'tr{int(dic["el"][1]) + 1}')
        elif elements[-1].startswith("i"):
            parts[-1] = parts[-1].replace("i", "d")            
        elif elements[-1].startswith("f"):
            parts[-1] = parts[-1].replace("f", "of")
    # wrap up
    elements = [re.sub(r"[-+*/%~\[\]\(\).:]|\b\d*\b", " ", i).strip() 
        for i in parts]
    element_dics = [make_elementary_scratch(el)[1] for el in elements]
    formula = " + ".join(parts)
    return formula

### Orbit constructor
##############################################################################

_s = "(?:h(?:old)?|g(?:host)?h(?:old)?|g(?:host)?|b(?:aby)?|i(?:n)?|o(?:ut)?|d(?:ice)?|(?:[iod]?f(?:lare)?\d|tr(?:ansformer)?\d)[DASQ]?|(?:[iod]f?|tr)t(?:ear)?\d(?:Ex|Log)?(?:__(?:(?:d?f(?:lare)?\d|tr(?:ansformer)?\d)[DASQ]?))?)"
_c = "(?:Ex|Log)"
_tEl = "(?:__(?:[bd]|(?:f\d|tr\d)[DASQ]?))"

ORB = re.compile(
    fr"(?P<L>{_s}{_c}?{_tEl}?)_(?P<R>{_s}{_c}?{_tEl}?)(?:_(?P<S>\d\d))?$")

def orbit_to_formula(name):
    m = ORB.match(name)
    if not m:
        raise ValueError(f'unintelligible name: "{name}"')
    dic = m.groupdict()
    if dic['S']:
        num1, num2 = dic['S'][0], dic['S'][1]
        den = int(num1) + int(num2)
        formula = f"({dic['L']}/({num1}/{den}) + -{dic['R']}/({num2}/{den})) / 1{' // 0.5' if not any(i.startswith(j) for i in [dic['L'], dic['R']] for j in ['f', 'if', 'of', 'tr']) else ''}"
    else:
        formula = f"({dic['L']} + -{dic['R']}) / 1{' // 0.5' if not any(i.startswith(j) for i in [dic['L'], dic['R']] for j in ['f', 'if', 'of', 'tr']) else ''}"
    return formula


### make_scratch constructor
##############################################################################

def names_in_formula(formula):
    formula = re.sub(r"[-+*/%~\[\]\(\).:]|\b\d*\b", " ", formula)
    return formula.split()

def new(formula, codebook={}):
    """Recursively yield all hiterto unknown scratch names from a function"""
    for name in set(names_in_formula(formula)):
        try:
            exec(name)
        except NameError:
            try:
                exec(make_elementary_scratch(name))
                yield name
            except:
                yield name
                try:
                    for name in new(tear_to_formula(name), codebook):
                        yield name
                except:
                    try:
                        for name in new(orbit_to_formula(name), codebook):
                            yield name
                    except:
                        for name in new(codebook[name], codebook):
                            yield name

# Avoid name space conflicts of python-incompatible scratch names
SLICE = re.compile(r"\bslice\b")            
IN = re.compile(r"\bin\b")
IN_ = re.compile(r"\bin_(?=\w)")
_IN = re.compile(r"(?<=\w)_in\b")        

def make_scratch(formula, codebook={}):
    """Make scratch given formula and codebook"""
    formula = SLICE.sub("s", formula)
    formula = IN.sub("i", formula)
    formula = IN_.sub("i_", formula)
    formula = _IN.sub("_i", formula)
    just_defined = set()
    for n in list(new(formula, codebook))[::-1]:
        if n in just_defined:
            continue
        try:
            exec(f"{n} = {make_elementary_scratch(n)}")
            just_defined.add(n)
        except:
            try:
                exec(f"{n} = {tear_to_formula(n)}")
                just_defined.add(n)
            except:
                try:
                    exec(f"{n} = {orbit_to_formula(n)}")
                    just_defined.add(n)
                except:
                    exec(f"{n} = {codebook[n]}")
                    just_defined.add(n)
    return eval(formula)