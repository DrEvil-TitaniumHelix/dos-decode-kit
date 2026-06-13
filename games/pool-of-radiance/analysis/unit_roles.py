# Automated per-unit role labeller for GAME.OVR's 34 Turbo Pascal overlay units.
# For each unit: disassemble every public entry point, resolve far-calls to named resident
# segments, tally state-global memory accesses + RNG/video/graphics/loader calls, then score
# the unit against role categories. Output: analysis/unit_roles.json + a markdown table.
import json, os, sys
from collections import Counter, defaultdict
from capstone import Cs, CS_ARCH_X86, CS_MODE_16

HERE = os.path.dirname(__file__)
GAME = r".\games\pool-of-radiance\extracted\poolrad"
ovr = open(os.path.join(GAME, "GAME.OVR"), "rb").read()
segs = json.load(open(os.path.join(HERE, "overlay_segmap.json")))
md = Cs(CS_ARCH_X86, CS_MODE_16)
md.detail = True

# Resident segments resolved during the GAME.OVR campaign (far-call seg -> meaning).
SEG_NAME = {
 0xAF8: "TP_SYSTEM",   # language runtime — discount
 0xBA:  "VIDEO",       # screen/menu/label draw helpers (0xBA:0x26C2 field copy)
 0xB0:  "RNG",         # 0xB0:0x48 = bounded random
 0x709: "GFX",         # picture blit / 40-col text / window (0x709:0xB66/0x9E3/0x768)
 0x7C:  "ECL_LOADER",  # 0x7C:0x57 = load+run ECLn.DAX
 0x802: "RESOURCE",    # 0x802:0x716 = open .DAX resource record
 0x3D0: "COMBAT",      # monster spawn (0x3D0:0x25)
 0x3D5: "ENCOUNTER",   # fixed-encounter config (0x3D5:0x43/0x3E)
 0x2B:  "ECL_VM",      # the ECL operand-fetch helper segment
}
# State globals (addr -> tag) from the ECL VM doc + ledger findings.
GLOBALS = {
 0x6822:"page", 0x6825:"page", 0x5D96:"party_list", 0x4435:"npc_count", 0x442E:"ecl_stop",
 0x49ED:"ecl_pc", 0x84C9:"combat_flag", 0x84E0:"combat_flag", 0x5E24:"window_state",
 0x5E25:"window_state", 0x4766:"ui_clear", 0x6DBF:"ui_clear", 0x6810:"obj_list",
 0x6F70:"call_stack", 0x6F7F:"ecl_opcode", 0x6F78:"ecl_flags", 0x67F4:"res_slots",
}

# VIDEO and RNG are ubiquitous background helpers — weighted low so they only break ties.
ROLE_RULES = [
 # role, signals that boost it (weighted)
 ("ECL/Events",        {"ECL_VM":5, "ecl_pc":4, "ecl_stop":4, "ecl_opcode":4, "ECL_LOADER":2, "call_stack":2}),
 ("Combat/Encounter",  {"COMBAT":5, "ENCOUNTER":5, "combat_flag":4, "RNG":0.5}),
 ("ResourceLoad",      {"RESOURCE":5, "res_slots":4}),
 ("NPC/Object",        {"npc_count":5, "obj_list":4}),
 ("CharacterState",    {"party_list":4, "page":3}),
 ("Render/Display",{"GFX":3, "VIDEO":0.4}),       # GFX = the 0x709 picture/blit segment
 ("UI/Window",         {"window_state":5, "ui_clear":4, "VIDEO":0.6}),
]

def entries_sorted(u):
    return sorted(set(u["entries"]))

def func_span(u, e):
    es = entries_sorted(u)
    nxt = next((x for x in es if x > e), u["csize"])
    return e, min(nxt, e + 600)  # cap per-func disasm window

def analyze_unit(u):
    base = u["ovr_off"]
    sig = Counter()
    helper_hits = Counter()
    for e in entries_sorted(u):
        a, b = func_span(u, e)
        code = ovr[base + a: base + b]
        for ins in md.disasm(code, a):
            m = ins.mnemonic
            if m in ("lcall", "call") and ins.op_str.count(",") == 1 and "0x" in ins.op_str:
                # far call seg, off
                try:
                    seg = int(ins.op_str.split(",")[0].strip(), 16)
                except ValueError:
                    continue
                nm = SEG_NAME.get(seg)
                if nm and nm != "TP_SYSTEM":
                    sig[nm] += 1; helper_hits[f"{nm}({seg:#x})"] += 1
            # memory operand absolute addresses -> state globals
            for tok in ins.op_str.replace("[", " ").replace("]", " ").split():
                if tok.startswith("0x"):
                    try: v = int(tok, 16)
                    except ValueError: continue
                    if v in GLOBALS:
                        sig[GLOBALS[v]] += 1
    return sig, helper_hits

def score_roles(sig):
    scored = []
    for role, weights in ROLE_RULES:
        s = sum(sig.get(k, 0) * w for k, w in weights.items())
        if s: scored.append((s, role))
    scored.sort(reverse=True)
    return scored

# --- Render/Display refinement -------------------------------------------------
# The generic "GFX" segment (0x709) serves three distinct jobs, told apart by offset:
#   0x1df / 0xc3f  -> planar VGA pixel blit  (0x1df writes Sequencer port 0x3c4 Map-Mask)
#   0x626 / 0x768  -> text / window paint    (touch window_state 0x5e25, compare space 0x20)
# A unit with no draw primitives but heavy shl/cwde/les + records = Compute/Logic.
GFX_BLIT = {"0xc3f", "0x1df", "0x5eb", "0xcab"}
GFX_TEXT = {"0x626", "0x768"}  # 0xdbe/0xdd3 are alloc/return stubs, not paint — excluded

def render_subrole(u):
    base = u["ovr_off"]
    blit = text = arith = les = total = 0
    for i, e in enumerate(entries_sorted(u)):
        es = entries_sorted(u)
        nxt = es[i+1] if i+1 < len(es) else u["csize"]
        for ins in md.disasm(ovr[base+e: base+min(nxt, e+600)], e):
            total += 1
            o = ins.op_str
            if ins.mnemonic == "lcall" and "0x709" in o:
                off = o.split(",")[1].strip()
                if off in GFX_BLIT: blit += 1
                elif off in GFX_TEXT: text += 1
            if ins.mnemonic in ("mul","imul","shl","shr","sar","div","idiv","cwde"): arith += 1
            if ins.mnemonic == "les": les += 1
    if blit > text:
        return "GfxBlit/Sprite"
    if text > 0:
        return "TextWindowPaint"
    # no draw primitives at all -> compute, unless it's tiny
    if total > 200 and arith / max(total,1) > 0.04:
        return "Compute/Logic"
    return "Render/Display"

def main():
    rows = []
    for u in segs:
        ent = u.get("nent", 0)
        # match ledger record for funcs/entries
        led = next((x for x in json.load(open(os.path.join(HERE,"unit_ledger.json"))) if x["unit"]==u["seg"]), None)
        if not led:
            continue
        sig, helpers = analyze_unit(led)
        scored = score_roles(sig)
        # high function count with almost no public entries = a deep internal helper library,
        # not a feature unit — only override when no strong feature signal exists.
        strong = scored and scored[0][0] >= 8
        if led["nfuncs"] >= 12 and led["nentry"] <= 3 and not strong:
            top = "InternalHelperLib"
        else:
            top = scored[0][1] if scored else "InternalHelperLib"
        # refine the catch-all render bucket into blit / text-paint / compute
        if top == "Render/Display":
            top = render_subrole(led)
        conf = round(scored[0][0] / (sum(s for s,_ in scored) or 1), 2) if scored else 0
        rows.append({
            "unit": f"{u['seg']:#x}", "ovr_off": u["ovr_off"], "size": u["csize"],
            "funcs": led["nfuncs"], "entries": led["nentry"],
            "role": top, "role_score": scored[0][0] if scored else 0,
            "runner_up": scored[1][1] if len(scored) > 1 else "",
            "signals": dict(sig.most_common()),
            "helpers": dict(helpers.most_common(6)),
        })
    rows.sort(key=lambda r: -r["size"])
    json.dump(rows, open(os.path.join(HERE, "unit_roles.json"), "w"), indent=1)
    # markdown
    print(f"{'unit':>5} {'size':>6} {'fn':>4} {'ent':>4}  role (runner-up)         signals")
    for r in rows:
        sig = ",".join(f"{k}:{v}" for k,v in list(r["signals"].items())[:5])
        print(f"{r['unit']:>5} {r['size']:>6} {r['funcs']:>4} {r['entries']:>4}  "
              f"{r['role']:<20s} {('('+r['runner_up']+')') if r['runner_up'] else '':<14s} {sig}")

if __name__ == "__main__":
    main()
