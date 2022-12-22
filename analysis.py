from construction import fcl_strings, L, S, Log, Ex


def fcl_floats(n, dasq):
  """ Converts fcl string representation of clicks into floats """
  return [int(i.split("/")[0]) / int(i.split("/")[1]) for i in fcl_strings(n, dasq)]

def get_info(scratch):
    info = {}
    info["elements"] = set()
    info["combos"] = set()
    info["sounds"] = 0
    info["length"] = scratch.length
    info["FO"] = 0
    info["FC"] = 0
    info["PO"] = 0
    info["PC"] = 0
    info["variations"] = False
    lasteld = {}
    for el in scratch.elements:
        eld = {}
        eld["name"] = "NONAME"
        eld["curve"] = el.curve
        eld["ypos"] = el.ypos
        eld["iclick"] = el.iclick
        eld["oclick"] = el.oclick
        eld["forward"] = el.forward
        eld["fN"] = el.fN
        info["FO"] += eld["iclick"] + eld["fN"]
        info["FC"] += eld["oclick"] + eld["fN"]
        info["PO"] += int(bool(not eld["iclick"]))
        info["PC"] += int(bool(not eld["oclick"]))
        eld["ExLog"] = "Ex" if el.curve == Ex else "Log" if el.curve == Log else ""
        eld["DASQ"] = ""
        for letter in "DASQ":
            if (
                el.fclicks not in [[], [0], [1/2], [1]] 
                and el.fclicks == fcl_floats(eld["fN"], letter)
            ):
                eld["DASQ"] = letter
                break
        if not info["variations"] and (eld["ExLog"] or eld["DASQ"]):
            info["variations"] = True
        eld["opposite"] = True if (
            lasteld 
            and not eld["name"] in ["hold", "ghosthold"]  
            and not eld["forward"] == lasteld["forward"]) else False # opposite direction than previous
        isorbit = (
            eld["opposite"]
            and eld["ypos"] == lasteld["ypos"]
            and eld["iclick"] == lasteld["oclick"]
            and eld["oclick"] == lasteld["iclick"]
        )
        # if isorbit: # Do I still need this?
        #     if eld["curve"] == lasteld["curve"] == S:
        #         info["s-curved"] += 1 
        #     elif eld["curve"] == lasteld["curve"] == Log:
        #         info["tazers"] += 1 
        #     elif eld["curve"] == lasteld["curve"] == Ex:
        #         info["ex-tazers"] += 1 
        #     elif not eld["forward"] == lasteld["forward"] and eld["curve"] == Log and lasteld["curve"] == Ex:
        #         info["phantazms"] += 1 
        #     elif not eld["forward"] == lasteld["forward"] and eld["curve"] == Ex and lasteld["curve"] == Log:
        #         info["phantazms"] += 1 
        if not el.clicks:
            if not el.curve == L:
                if el.color == "k":
                    info["sounds"] += 1
                    eld["name"] = f'baby{eld["ExLog"]}'
                    if isorbit and lasteld["name"].startswith("baby"):
                        info["combos"].add("babyorbit")
                else:
                    eld["name"] = "ghost"
                    if isorbit and lasteld["name"].startswith("dice"):
                        info["combos"].add("stab")
            else:
                if el.color == "k":
                    eld["name"] = "hold"
                else:
                    eld["name"] = "ghosthold"
        else:
            info["sounds"] += eld["fN"] + 1
            if eld["iclick"]:
                if eld["oclick"]:
                    if el.fclicks:
                        eld["name"] = f'transformer{eld["fN"] + 1}{eld["DASQ"]}{eld["ExLog"]}'
                        if isorbit and lasteld["name"].startswith("transformer"):
                            info["combos"].add(f'tr{lasteld["fN"] + 1}_tr{eld["fN"] + 1}')
                    else:
                        eld["name"] = f'dice{eld["ExLog"]}'
                        if isorbit:
                            if lasteld["name"] == "ghost":
                                info["combos"].add("offstab") # <------ change to stab and remove offstab from library.py?
                            elif lasteld["name"].startswith("dice"):
                                info["combos"].add("diceorbit")
                else:
                    if el.fclicks:
                        eld["name"] = f'iflare{eld["fN"]}{eld["DASQ"]}{eld["ExLog"]}'
                    else:
                        eld["name"] = f'in{eld["ExLog"]}'
                        if isorbit:
                            if lasteld["name"].startswith("out"):
                                info["combos"].add("chirp")
                            if lasteld["name"].startswith("oflare1"): # <------ only oflare1 or also oflareN?
                                info["combos"].add("ogflare")
            else:
                if eld["oclick"]:
                    if el.fclicks:
                        eld["name"] = f'oflare{eld["fN"]}{eld["DASQ"]}{eld["ExLog"]}'
                    else:
                        eld["name"] = f'out{eld["ExLog"]}'
                        if isorbit and lasteld["name"].startswith("in"):
                            info["combos"].add("slice")
                elif el.fclicks:
                    eld["name"] = f'flare{eld["fN"]}{eld["DASQ"]}{eld["ExLog"]}'
                    if isorbit and lasteld["name"].startswith("flare"):
                        info["combos"].add(f'f{lasteld["fN"]}_f{eld["fN"]}')
        info["elements"].add(eld["name"])
        lasteld = eld
    info["F"] = max([info["FO"], info["FC"]])
    info["P"] = max([info["PO"], info["PC"]])
    info["elements"] = sorted(info["elements"])
    info["combos"] = sorted(info["combos"])
    return info