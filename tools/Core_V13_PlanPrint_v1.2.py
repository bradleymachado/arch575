# -*- coding: utf-8 -*-
"""Core_V13_PlanPrint_v1.2 - vector presentation plans (one 11x17 landscape PDF per level)
from the RVT_V13 Revit-prep layers of Core_Tower_V13_v1.13.3dm. Read-only on the model.
CPython 3 + rhino3dm + matplotlib (runs outside Rhino).
Usage: python Core_V13_PlanPrint_v1.2.py <model.3dm> <out_dir> [prefix ...]"""
import sys, os, re, collections
import rhino3dm
import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Polygon, FancyArrowPatch
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["font.family"] = "Arial"
matplotlib.rcParams["hatch.linewidth"] = 0.35
RX_UTIL = re.compile(r"MEP|MECH|ELECTRICAL|GENERATOR|WATER SERVICE|TELEPHONE|BOILER|FAN ROOMS|COOLING|DOMESTIC WATER|CHW|SUBSTATION|RISER")
RX_BOH = re.compile(r"BACK OF HOUSE|^BOH|STORAGE|PANTRY|SERVICE STRIP")
H_UTIL, H_BOH = "////", "---"

MM = 72.0 / 25.4                       # mm -> pt
ACC = "#1F3A5F"
INK = "#000000"; GREY = "#6E6E6E"; LIGHT = "#9A9A9A"
TINT = "#E8ECF1"; TINT2 = "#C9D3DE"; NOSTOP = "#E4E4E4"

PLANS = [  # prefix, level, name, elevation, x-range of the RVT plan
    ("K",   "B1",      "BASEMENT PLANT",                     "EL. -20'-0\"",  (58, 193)),
    ("U",   "L06",     "AMENITY 1 - FUNCTION + CONFERENCE",  "EL. +66'-0\"",  (375, 580)),
    ("L1",  "L07-L15", "OFFICE 1 - TYPICAL",                 "EL. +96'-0\"",  (628, 763)),
    ("M",   "L16",     "MECHANICAL 1",                       "EL. +231'-0\"", (812, 947)),
    ("V",   "L17",     "AMENITY 2 - HOLODECK",               "EL. +251'-0\"", (995, 1130)),
    ("L2",  "L18-L32", "OFFICE 2 - TYPICAL",                 "EL. +271'-0\"", (1173, 1308)),
    ("N",   "L33",     "MECHANICAL 2",                       "EL. +496'-0\"", (1357, 1492)),
    ("W",   "L34",     "AMENITY 3 - HOTEL CLUBHOUSE + POOL", "EL. +516'-0\"", (1540, 1675)),
    ("L3A", "L35-L41", "HOTEL A - TYPICAL",                  "EL. +536'-0\"", (1739, 1847)),
    ("L3B", "L42-L47", "HOTEL B - TYPICAL",                  "EL. +616'-6\"", (1923, 2031)),
]
NOTES = {"M": "Model note: RVT_V13 L16 is missing 14 east-half objects (known issue, Core_Handoff_v7.0 sec 5)."}
RENAME = {"STD K": "STANDARD KING", "STD QQ": "STANDARD 2 QUEEN", "DLX K": "DELUXE KING", "BOH": "BACK OF HOUSE"}
BANK = {"OFF1": "OFFICE 1 ELEVATORS", "OFF2": "OFFICE 2 ELEVATORS", "HOTEL": "HOTEL ELEVATORS",
        "HOTELSVC": "HOTEL SERVICE ELEVATORS", "SERVICE": "SERVICE ELEVATOR",
        "BLIND_HOTEL": "HOTEL ELEVATORS", "BLIND_OFF2": "OFFICE 2 ELEVATORS", "BLIND_HOTELSVC": "HOTEL SERVICE ELEVATORS",
        "PIT": "ELEVATOR PITS", "OVERRUN": "ELEVATOR OVERRUNS"}
SCALES = [(16, "1/16\" = 1'-0\""), (20, "1\" = 20'-0\""), (30, "1\" = 30'-0\""), (32, "1/32\" = 1'-0\""), (40, "1\" = 40'-0\""), (64, "1/64\" = 1'-0\"")]


# ---------- geometry helpers ----------
def pts(g):
    t = type(g).__name__
    if t == "PolylineCurve":
        return [(g.Point(i).X, g.Point(i).Y) for i in range(g.PointCount)]
    if t == "LineCurve":
        return [(g.PointAtStart.X, g.PointAtStart.Y), (g.PointAtEnd.X, g.PointAtEnd.Y)]
    if t == "NurbsCurve" and g.Degree == 1:
        return [(g.Points[i].X, g.Points[i].Y) for i in range(len(g.Points))]
    d = g.Domain; n = 48; out = []
    for i in range(n + 1):
        p = g.PointAt(d.T0 + (d.T1 - d.T0) * i / n); out.append((p.X, p.Y))
    return out


def inside(p, poly):
    x, y = p; c = False; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def sarea(poly):
    n = len(poly)
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))


def centroid(poly):
    if len(poly) > 1 and poly[0] == poly[-1]:
        poly = poly[:-1]
    a = sarea(poly)
    if abs(a) < 1e-6:
        return (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))
    cx = cy = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % len(poly)]; f = x1 * y2 - x2 * y1
        cx += (x1 + x2) * f; cy += (y1 + y2) * f
    return (cx / (6 * a), cy / (6 * a))


def compound(loops):
    """Orient nested loops alternately so non-zero fill leaves holes open."""
    loops = [L[:-1] if L[0] == L[-1] else L for L in loops]
    verts, codes = [], []
    for i, L in enumerate(loops):
        aL = abs(sarea(L))
        depth = sum(1 for j, M in enumerate(loops) if j != i and abs(sarea(M)) > aL and inside(L[0], M))
        if (depth % 2 == 0) != (sarea(L) > 0):
            L = L[::-1]
        verts += L + [L[0]]
        codes += [Path.MOVETO] + [Path.LINETO] * (len(L) - 1) + [Path.CLOSEPOLY]
    return Path(verts, codes)


def clean(s):
    s = s.replace("\r", "").replace("�", "-").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip()


# ---------- read model ----------
def load(path):
    m = rhino3dm.File3dm.Read(path)
    out = []
    for o in m.Objects:
        L = m.Layers[o.Attributes.LayerIndex].FullPath
        if not L.startswith("RVT_V13::"):
            continue
        g = o.Geometry; t = type(g).__name__
        if t == "Hatch":
            continue
        if t == "Text":
            p = g.Plane.Origin; bb = (p.X, p.Y, p.X, p.Y)
        else:
            b = g.GetBoundingBox(); bb = (b.Min.X, b.Min.Y, b.Max.X, b.Max.Y)
        us = dict(o.Attributes.GetUserStrings()) if o.Attributes.UserStringCount else {}
        out.append(dict(layer=L.split("::")[1], type=t, g=g, bb=bb, name=o.Attributes.Name or "", us=us))
    return out


# ---------- label layout ----------
def spread(items, lo, hi):
    """Push labels apart vertically (desired y = target y), keep them inside [lo, hi]."""
    items.sort(key=lambda d: -d["y"])
    for _ in range(300):
        for i in range(1, len(items)):
            a, b = items[i - 1], items[i]
            need = a["y"] - (a["h"] + b["h"]) / 2.0
            if b["y"] > need:
                b["y"] = need
        if items[-1]["y"] - items[-1]["h"] / 2.0 < lo:
            items[-1]["y"] = lo + items[-1]["h"] / 2.0
            for i in range(len(items) - 2, -1, -1):
                a, b = items[i], items[i + 1]
                need = b["y"] + (a["h"] + b["h"]) / 2.0
                if a["y"] < need:
                    a["y"] = need
        if items[0]["y"] + items[0]["h"] / 2.0 > hi:
            items[0]["y"] = hi - items[0]["h"] / 2.0
        else:
            break
    return items


# ---------- sheet ----------
def render(objs, plan, sheet_no, sheet_tot, title_txt, out_pdf):
    pfx, lev, pname, elev, (xa, xb) = plan
    PAD = 25.0
    mine = [o for o in objs if xa - PAD <= o["bb"][0] and o["bb"][2] <= xb + PAD and o["bb"][1] > 1900]
    geo = [o for o in mine if o["type"] != "Text" and o["layer"] not in ("06_Wall_Axis", "09_Titles")]
    X0 = min(o["bb"][0] for o in geo); X1 = max(o["bb"][2] for o in geo)
    Y0 = min(o["bb"][1] for o in geo); Y1 = max(o["bb"][3] for o in geo)
    W, H = X1 - X0, Y1 - Y0

    SW, SH = 17.0, 11.0; MARG = 0.45; TB = 0.95; COL = 2.2; GAP = 0.4
    availW = SW - 2 * MARG - 2 * 1.7; availH = SH - 2 * MARG - TB - 0.35
    fpi, slabel = [s for s in SCALES if H / s[0] <= availW and W / s[0] <= availH - 1.6][0]   # plan rotated 90 deg CCW
    pw, ph = H / fpi, W / fpi
    ox = (SW - pw) / 2.0; oy = MARG + TB + 0.2 + (availH - ph) / 2.0

    def T(p):
        return (ox + (Y1 - p[1]) / fpi, oy + (p[0] - X0) / fpi)   # 90 deg CCW: north points left

    fig = plt.figure(figsize=(SW, SH)); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, SW); ax.set_ylim(0, SH); ax.set_aspect("equal"); ax.axis("off")

    def line(o, lw, col=INK, ls="-", z=3):
        P = [T(p) for p in pts(o["g"])]
        ax.plot([p[0] for p in P], [p[1] for p in P], color=col, lw=lw * MM, ls=ls, solid_capstyle="butt", zorder=z)

    # outdoor areas + slab edge
    for o in geo:
        if o["layer"] != "01_Floors":
            continue
        P = [T(p) for p in pts(o["g"])]
        if "slab boundary" in o["name"]:
            ax.add_patch(Polygon(P, closed=True, fc="none", ec=INK, lw=0.35 * MM, zorder=2))
        else:
            pool = "POOL" in o["name"] and "DECK" not in o["name"]
            und = "UNDEFINED" in o["name"].upper()
            ax.add_patch(Polygon(P, closed=True, fc=TINT2 if pool else ("#F4F6F8" if und else TINT),
                                 ec=GREY, lw=0.13 * MM, ls=(0, (4, 2)) if und else "-", zorder=1))
    # poche walls, heaviest first
    for lay, lw in (("02_Walls_Core_12in", 0.60), ("03_Walls_Interior_8in", 0.45),
                    ("04_Walls_Demising_6in", 0.35), ("10_Walls_Partition_5in", 0.30)):
        loops = [[T(p) for p in pts(o["g"])] for o in geo if o["layer"] == lay and o["type"] == "NurbsCurve"]
        loops = [L for L in loops if len(L) > 2]
        if loops:
            ax.add_patch(PathPatch(compound(loops), fc=INK, ec=INK, lw=lw * MM, joinstyle="miter", zorder=6))
        for o in geo:  # operable partitions
            if o["layer"] == lay and o["type"] == "PolylineCurve":
                line(o, 0.25, INK, (0, (3, 1.5)), 6)
    for o in geo:
        L = o["layer"]
        if L == "05_Walls_Curtain":
            line(o, 0.50, INK, "-", 5)
        elif L == "11_Doors":
            if o["type"] == "LineCurve" and "opening" in o["name"]:
                line(o, 1.0 / 25.4 * 72 / MM * 0 + 0.9, "white", "-", 7)   # cut the opening out of the poche
            else:
                line(o, 0.18 if o["type"] == "LineCurve" else 0.09, INK, "-", 8)
        elif L in ("12_Plumbing", "13_Furniture"):
            line(o, 0.09, LIGHT, "-", 4)
        elif L == "08_Shafts":
            poly = o["type"] == "PolylineCurve"
            if poly and o["us"].get("StopAtLevel", "Yes") != "Yes":   # no stop on this level: light grey
                ax.add_patch(Polygon([T(p) for p in pts(o["g"])], closed=True, fc=NOSTOP, ec=LIGHT, lw=0.13 * MM, zorder=3))
            else:
                line(o, 0.18 if poly else 0.09, INK if poly else GREY, "-", 4)

    # ---------- labels ----------
    rooms = [pts(o["g"]) for o in geo if o["layer"] == "07_Rooms" and o["type"] == "PolylineCurve"]
    floors = [pts(o["g"]) for o in geo if o["layer"] == "01_Floors" and "slab boundary" not in o["name"]]
    tags = [o for o in mine if o["layer"] == "07_Rooms" and o["type"] == "Text"]
    groups = collections.OrderedDict(); tagged = []
    for t in tags:
        lines = t["g"].PlainText.split("\n")
        raw = clean(lines[0]); sub = clean(" ".join(lines[1:]))
        nm = RENAME.get(raw, raw)
        if nm.startswith("MECH ZONE: "):
            nm = nm[11:]
        nm = re.split(r"\s{3,}", t["g"].PlainText.split("\n")[0].strip())[0]
        nm = RENAME.get(clean(nm), clean(nm)).replace("MECH ZONE: ", "")
        if "no area" in sub:
            sub = ""
        p = (t["bb"][0], t["bb"][1])
        best = None
        for P in rooms + floors:
            if len(P) > 2 and inside(p, P):
                a = abs(sarea(P))
                if best is None or a < best[0]:
                    best = (a, P)
        tagged.append(dict(nm=nm, sub=sub, p=p, poly=best[1] if best else None))
    share = collections.Counter(id(d["poly"]) for d in tagged if d["poly"] is not None)
    for d in tagged:
        P = d["poly"]; tgt = d["p"]
        if P is not None and share[id(P)] == 1:
            c = centroid(P); tgt = c if inside(c, P) else d["p"]
        if P is not None:
            hk = H_UTIL if RX_UTIL.search(d["nm"]) else (H_BOH if RX_BOH.search(d["nm"]) else None)
            if hk:
                ax.add_patch(Polygon([T(q) for q in P], closed=True, fill=False, hatch=hk, ec=LIGHT, lw=0, zorder=2.5))
        groups.setdefault(d["nm"], []).append(dict(t=T(tgt), sub=d["sub"]))
    labels = []
    for nm, inst in groups.items():
        if len(inst) == 1:
            labels.append(dict(txt=nm, sub=inst[0]["sub"], tgts=[inst[0]["t"]]))
        else:
            labels.append(dict(txt=nm + ", TYP.", sub="", tgts=[i["t"] for i in inst], typ=True))
    # elevator banks (one leader per bank) + stairs
    bysrc = collections.defaultdict(list)
    for o in geo:
        if o["layer"] != "08_Shafts" or o["type"] != "PolylineCurve":
            continue
        parts = o["name"].split(); src = parts[2] if len(parts) > 2 else "?"
        key = o["us"].get("StackKey", parts[-1])
        if src == "STAIR":
            labels.append(dict(txt=key, sub="", tgts=[T(centroid(pts(o["g"])))]))
        else:
            bysrc[src].append((o, key))
    for src, lst in bysrc.items():
        clusters = []
        for o, k in sorted(lst, key=lambda e: (e[0]["bb"][1], e[0]["bb"][0])):
            for c in clusters:
                if any(abs(o["bb"][0] - q["bb"][0]) < 20 and abs(o["bb"][1] - q["bb"][1]) < 20 for q, _ in c):
                    c.append((o, k)); break
            else:
                clusters.append([(o, k)])
        for c in clusters:
            keys = sorted({k for _, k in c}, key=lambda s: [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", s)])
            bx = (sum((q["bb"][0] + q["bb"][2]) / 2 for q, _ in c) / len(c),
                  sum((q["bb"][1] + q["bb"][3]) / 2 for q, _ in c) / len(c))
            nostop = src.startswith("BLIND") and all(q["us"].get("StopAtLevel", "Yes") != "Yes" for q, _ in c)
            ks = keys[0] if len(keys) == 1 else (keys[0] + " TO " + keys[-1] if len(keys) > 2 else ", ".join(keys))
            name = BANK.get(src, src + " SHAFT")
            if len(keys) > 1 and name.endswith("ELEVATOR"):
                name += "S"
            labels.append(dict(txt=name, sub=ks + ("  (NO STOP, SHOWN GREY)" if nostop else ""), tgts=[T(bx)]))
    # ---------- four-edge labelling: each callout goes to the plan edge nearest its room ----------
    import textwrap
    CW, CWS, LH = 0.060, 0.046, 0.105          # in per char (6.4 pt bold / 5.4 pt), line height
    PX0, PX1, PY0, PY1 = ox, ox + pw, oy, oy + ph
    lo, hi = MARG + TB + 0.25, SH - MARG - 0.12
    ROWG = 0.32                                  # plan edge -> row text
    for lb in labels:
        lb["lines"] = textwrap.wrap(lb["txt"], 15) or [lb["txt"]]
        lb["rw"] = max(max(len(s) for s in lb["lines"]) * CW, len(lb["sub"]) * CWS) + 0.14
        lb["cw"] = max(len(lb["txt"]) * CW, len(lb["sub"]) * CWS)

    def pick(lb, e):
        k = {"T": lambda p: -p[1], "B": lambda p: p[1], "L": lambda p: p[0], "R": lambda p: -p[0]}[e]
        return min(lb["tgts"], key=k)

    def dist(lb, e):
        p = pick(lb, e)
        return {"T": PY1 - p[1], "B": p[1] - PY0, "L": p[0] - PX0, "R": PX1 - p[0]}[e]

    room_l, room_r = PX0 - MARG - GAP - 0.1, SW - MARG - PX1 - GAP - 0.1

    def fits(lb, e):
        return not ((e == "L" and lb["cw"] > room_l) or (e == "R" and lb["cw"] > room_r))
    cap = {"T": 0.6 * pw, "B": 0.6 * pw, "L": hi - lo, "R": hi - lo}   # rows kept loose so labels stay near their rooms
    use = {"T": lambda d: d["rw"], "B": lambda d: d["rw"], "L": lambda d: 0.25, "R": lambda d: 0.25}
    band = {e: [] for e in "TBLR"}
    for lb in labels:
        e = min([e for e in "TBLR" if fits(lb, e)], key=lambda e: dist(lb, e))
        lb["edge"] = e; band[e].append(lb)
    for _ in range(400):                          # relieve overfull edges at the least extra leader length
        over = [e for e in "TBLR" if sum(use[e](d) for d in band[e]) > cap[e]]
        if not over:
            break
        e = over[0]; best = None
        for d in band[e]:
            for f in "TBLR":
                if f == e or not fits(d, f) or sum(use[f](x) for x in band[f]) + use[f](d) > cap[f]:
                    continue
                c = dist(d, f) - dist(d, e)
                if best is None or c < best[0]:
                    best = (c, d, f)
        if best is None:
            break
        _, d, f = best; band[e].remove(d); band[f].append(d); d["edge"] = f
    for lb in labels:
        lb["tgts"] = [pick(lb, lb["edge"])]
    seen = []
    for lb in labels:                             # arrowheads never share a point
        tx_, ty_ = lb["tgts"][0]
        while any(abs(tx_ - u) < 0.12 and abs(ty_ - v) < 0.12 for u, v in seen):
            ty_ -= 0.15
        lb["tgts"] = [(tx_, ty_)]; seen.append((tx_, ty_))

    def place(order, e):                          # 1-D spread along the edge, order kept
        k = 0 if e in "TB" else 1
        a0, a1 = (PX0, PX1) if e in "TB" else (lo, hi)
        sz = [use[e](d) for d in order]
        pos = [d["tgts"][0][k] for d in order]
        for i in range(1, len(pos)):
            pos[i] = max(pos[i], pos[i - 1] + (sz[i - 1] + sz[i]) / 2.0)
        if pos and pos[-1] + sz[-1] / 2.0 > a1:
            pos[-1] = a1 - sz[-1] / 2.0
            for i in range(len(pos) - 2, -1, -1):
                pos[i] = min(pos[i], pos[i + 1] - (sz[i] + sz[i + 1]) / 2.0)
        if pos and pos[0] - sz[0] / 2.0 < a0:
            pos[0] = a0 + sz[0] / 2.0
            for i in range(1, len(pos)):
                pos[i] = max(pos[i], pos[i - 1] + (sz[i - 1] + sz[i]) / 2.0)
        for d, v in zip(order, pos):
            d["pos"] = v
            ytxt = v + (0.05 if d["sub"] else 0)
            if e == "T":
                d["anc"] = (v, PY1 + ROWG - 0.06)
            elif e == "B":
                d["anc"] = (v, PY0 - ROWG + 0.06)
            elif e == "L":
                d["anc"] = (PX0 - GAP + 0.18, ytxt)
            else:
                d["anc"] = (PX1 + GAP - 0.18, ytxt)

    def cross(a, b, c, d):
        def o(p, q, r):
            v = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
            return (v > 1e-9) - (v < -1e-9)
        return o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0

    def ncross(lst):
        return sum(1 for i in range(len(lst)) for j in range(i + 1, len(lst))
                   if cross(lst[i]["anc"], lst[i]["tgts"][0], lst[j]["anc"], lst[j]["tgts"][0]))
    for e in "TBLR":
        k = 0 if e in "TB" else 1
        order = sorted(band[e], key=lambda d: d["tgts"][0][k])
        place(order, e)
        for _ in range(400):                      # swap crossing pairs in the order until clean
            hit = None
            for i in range(len(order)):
                for j in range(i + 1, len(order)):
                    if cross(order[i]["anc"], order[i]["tgts"][0], order[j]["anc"], order[j]["tgts"][0]):
                        hit = (i, j); break
                if hit:
                    break
            if not hit:
                break
            i, j = hit; order[i], order[j] = order[j], order[i]; place(order, e)
        band[e] = order
    print("  crossings remaining:", ncross(labels))

    # ---------- draw callouts ----------
    def arrow(a, b):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>,head_length=2.4,head_width=1.0", mutation_scale=1.0,
                                     color=ACC, lw=0.13 * MM, shrinkA=0, shrinkB=0, zorder=8))
    for e in "TBLR":
        for d in band[e]:
            v = d["pos"]
            if e in "TB":
                rows = [(s, 6.4, "bold", INK) for s in d["lines"]] + ([(d["sub"], 5.4, "normal", GREY)] if d["sub"] else [])
                if e == "T":
                    y = PY1 + ROWG
                    for s, fs, fw, c in reversed(rows):
                        ax.text(v, y, s, ha="center", va="bottom", fontsize=fs, fontweight=fw, color=c, zorder=9)
                        y += LH if fw == "bold" else 0.09
                else:
                    y = PY0 - ROWG
                    for s, fs, fw, c in rows:
                        ax.text(v, y, s, ha="center", va="top", fontsize=fs, fontweight=fw, color=c, zorder=9)
                        y -= LH if fw == "bold" else 0.09
                arrow(d["anc"], d["tgts"][0])
            else:
                ha = "right" if e == "L" else "left"
                xl = PX0 - GAP if e == "L" else PX1 + GAP
                ytop = d["anc"][1]
                ax.text(xl, ytop, d["txt"], ha=ha, va="center", fontsize=6.4, fontweight="bold", color=INK, zorder=9)
                if d["sub"]:
                    ax.text(xl, ytop - 0.105, d["sub"], ha=ha, va="center", fontsize=5.4, color=GREY, zorder=9)
                sx = xl + (0.06 if e == "L" else -0.06)
                ax.plot([sx, d["anc"][0]], [ytop, ytop], color=ACC, lw=0.13 * MM, zorder=8)
                arrow(d["anc"], d["tgts"][0])
    # ---------- border + title block ----------
    ax.add_patch(Polygon([(MARG, MARG), (SW - MARG, MARG), (SW - MARG, SH - MARG), (MARG, SH - MARG)],
                         closed=True, fc="none", ec=INK, lw=0.35 * MM))
    yb = MARG + TB
    ax.plot([MARG, SW - MARG], [yb, yb], color=INK, lw=0.35 * MM)
    ax.text(MARG + 0.25, yb - 0.42, lev, fontsize=22, fontweight="bold", color=ACC, va="center")
    lx = MARG + 0.25 + 0.2 * len(lev) + 0.3
    ax.text(lx, yb - 0.27, pname, fontsize=11, fontweight="bold", color=INK, va="center")
    ax.text(lx, yb - 0.50, elev + "    |    " + title_txt + "    |    " + slabel, fontsize=7, color=GREY, va="center")
    ax.text(lx, yb - 0.70, NOTES.get(pfx, ""), fontsize=6, color=GREY, va="center", style="italic")
    rx = SW - MARG - 0.25
    ax.text(rx, yb - 0.24, "ARCH 575  |  735 W. RANDOLPH ST., CHICAGO", fontsize=8, fontweight="bold", color=INK, ha="right", va="center")
    ax.text(rx, yb - 0.45, "Core Tower V13 v1.13  |  Brad Machado  |  2026-10-05", fontsize=7, color=GREY, ha="right", va="center")
    ax.text(rx, yb - 0.66, "SHEET %d OF %d" % (sheet_no, sheet_tot), fontsize=7, fontweight="bold", color=ACC, ha="right", va="center")
    # legend
    lgx, lgy = MARG + 0.3, yb + 0.22
    for i, (hk, fc, txt) in enumerate(((H_UTIL, "none", "UTILITY / MEP"), (H_BOH, "none", "BACK OF HOUSE / STORAGE"),
                                       (None, NOSTOP, "ELEVATOR, NO STOP AT THIS LEVEL"))):
        yy = lgy + i * 0.2
        ax.add_patch(Polygon([(lgx, yy), (lgx + 0.3, yy), (lgx + 0.3, yy + 0.13), (lgx, yy + 0.13)], closed=True,
                             fc=fc, ec=LIGHT if hk else LIGHT, hatch=hk, lw=0.13 * MM))
        ax.text(lgx + 0.4, yy + 0.065, txt, fontsize=5.6, color=GREY, va="center")
    # north arrow + graphic scale, lower right of the drawing field
    nx, ny = SW - MARG - 0.55, yb + 0.55
    ax.add_patch(Polygon([(nx - 0.3, ny), (nx + 0.15, ny - 0.1), (nx + 0.05, ny), (nx + 0.15, ny + 0.1)],
                         closed=True, fc=INK, ec=INK, lw=0.2))
    ax.text(nx - 0.42, ny, "N", ha="center", va="center", fontsize=8, fontweight="bold")
    seg = {16: 8, 20: 10, 30: 20, 32: 16, 40: 20, 64: 32}[fpi]; sx0 = SW - MARG - 0.95 - 4 * seg / fpi; sy = yb + 0.3
    for i in range(4):
        a, b = sx0 + i * seg / fpi, sx0 + (i + 1) * seg / fpi
        ax.add_patch(Polygon([(a, sy), (b, sy), (b, sy + 0.06), (a, sy + 0.06)], closed=True,
                             fc=INK if i % 2 == 0 else "white", ec=INK, lw=0.25 * MM))
    for i in (0, 1, 2, 4):
        ax.text(sx0 + i * seg / fpi, sy - 0.1, "%d'" % (i * seg), ha="center", va="center", fontsize=5.5)
    ax.text(sx0, sy + 0.17, slabel, ha="left", va="center", fontsize=5.5, color=GREY)
    fig.savefig(out_pdf); plt.close(fig)
    return slabel, len(labels)


if __name__ == "__main__":
    model, outdir = sys.argv[1], sys.argv[2]
    only = set(sys.argv[3:])
    objs = load(model)
    titles = {}
    for o in objs:
        if o["layer"] == "09_Titles":
            t = clean(o["g"].PlainText.split("\n")[0])
            mm = re.search(r"plate ([\d.]+) x ([\d.]+) = (\d+)", t)
            for pl in PLANS:
                if pl[4][0] - 2 <= o["bb"][0] <= pl[4][1]:
                    titles[pl[0]] = ("PLATE %s' x %s' = {:,} GSF" % (mm.group(1), mm.group(2))).format(int(mm.group(3))) if mm else ""
    os.makedirs(outdir, exist_ok=True)
    for i, pl in enumerate(PLANS):
        if only and pl[0] not in only:
            continue
        fn = os.path.join(outdir, "Core_V13_%s_Plan_v1.3.pdf" % pl[1].replace("-", "_"))
        s, n = render(objs, pl, i + 1, len(PLANS), titles.get(pl[0], ""), fn)
        print(fn, s, n, "labels")
