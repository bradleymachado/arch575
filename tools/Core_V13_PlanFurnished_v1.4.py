# -*- coding: utf-8 -*-
"""Core_V13_PlanFurnished_v1.3 - SVG output, oxide accent, generator switch (arch575.bradmachado.com, plan S3).
v1.4 (2026-10-08): rooms on L1/L2 plans classed OFFICE (exec offices were reading as HOTEL/AMENITY grey); file names v1.4.
v1.3 (2026-10-08): accent #B0431F (main-site system), OUTDOOR #EFD9D2, POOL #D7A18F; --fmt svg|png (default svg,
PNG at 450 dpi); --accent HEX; --nogen L1,L2 skips the generated furniture for the listed plan prefixes so the
model's ExecOffice / OpenOffice objects carry it; writes PlanColor_<key>_v1.3.<fmt> and legend_v1.3.json.
v1.2 - monochrome plan + one accent on the program the level is about (HERO); outdoor / pool = accent tints;
white furniture and trees, dark figures.
v1.1 - Rayon-style furnished program plans for the mid-review deck.
v1.1 (Brad 2026-10-07): shafts follow the model StopAtLevel flag (no stop = pale grey + X); service cars and their
lobby = back of house; the passenger lobby is cut through the core wall on office floors; Office 2 reception and
waiting sit at the two lobby exits; writes legend_v1.1.json (programs drawn per level) for the deck script.
Program colours + thin walls (as PlanColor v1.1), plus: model furniture / plumbing / doors where they exist (hotel),
generated furniture by room name everywhere else, and top-view people. No text, no leaders. Read-only on the model.
Usage: python Core_V13_PlanFurnished_v1.3.py <PlanPrint_v1.2.py> <model.3dm> <out_dir> [V14] [key ...]
       [--fmt svg|png] [--accent HEX] [--nogen L1,L2]"""
import sys, os, re, math, json, random, importlib.util, argparse
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, Polygon

spec = importlib.util.spec_from_file_location("pp", sys.argv[1]); pp = importlib.util.module_from_spec(spec); spec.loader.exec_module(pp)
MM = pp.MM

VERSION = "v1.4"
ACCENT = "#B0431F"                                 # oxide red, main-site accent (plan v1.1 D2)
COL = {"OFFICE": "#B5B5B5", "HOTEL": "#B5B5B5", "AMENITY": "#B5B5B5", "OUTDOOR": "#EFD9D2",
       "CIRCULATION": "#FFFFFF", "BOH": "#D9D9D9", "MEP": "#3A3A3A"}
POOL = "#D7A18F"; WALL = "#111111"; NOSTOP = "#F0F0F0"
HERO = {"K": "MEP", "U": "AMENITY", "L1": "OFFICE", "M": "MEP", "V": "AMENITY", "L2": "OFFICE", "N": "MEP",
        "W": "AMENITY", "L3A": "HOTEL", "L3B": "HOTEL"}             # the program each level is about = the accent
F_FC, F_EC, F_LW = "#FFFFFF", "#6E6E6E", 0.07      # furniture: white, thin grey edge
EQ_FC = "#F2F2F2"                                  # mech equipment (on dark MEP / accent)
PERSON = "#4A4A4A"; TREE_FC, TREE_EC = "#FFFFFF", "#9A9A9A"
NOGEN = set()                                      # plan prefixes whose generated furniture is skipped (--nogen)

RULES = [
    ("MEP",         r"MEP|MECH|ELECTRICAL|GENERATOR|WATER SERVICE|TELEPHONE|BOILER|FAN ROOMS|COOLING|DOMESTIC|CHW|SUBSTATION"),
    ("AMENITY",     r"^SPA|OFFICE POD"),
    ("CIRCULATION", r"LOBBY|CORRIDOR|RAMP"),
    ("BOH",         r"STORAGE|BOH|BACK OF HOUSE|PANTRY|SERVICE STRIP|BACK BAR|BLDG MGMT|TOILET|RESTROOM"),
    ("HOTEL",       r"SUITE|DLX|STD"),
    ("OUTDOOR",     r"TERRACE|LOGGIA|PATIO|DECK|OUTDOOR"),
    ("POOL",        r"^POOL"),
    ("OFFICE",      r"^OFFICE"),
]
BASE = {"K": "BOH", "U": "AMENITY", "L1": "OFFICE", "V": "AMENITY", "L2": "OFFICE", "M": "MEP", "N": "MEP", "W": "AMENITY"}


def program(name):
    for k, rx in RULES:
        if re.search(rx, name):
            return k
    return "AMENITY"


# ---------- geometry in model feet ----------
def rect(cx, cy, w, h, a=0.0):
    c, s = math.cos(a), math.sin(a)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]


def ellipse(cx, cy, rx, ry, a=0.0, n=20):
    c, s = math.cos(a), math.sin(a)
    return [(cx + rx * math.cos(t) * c - ry * math.sin(t) * s, cy + rx * math.cos(t) * s + ry * math.sin(t) * c)
            for t in (2 * math.pi * i / n for i in range(n))]


class Sheet:
    def __init__(self, ax, T, fpi, rng):
        self.ax, self.T, self.fpi, self.rng = ax, T, fpi, rng
        self.taken = []          # placed footprints (x0, y0, x1, y1) for people rejection

    def poly(self, P, fc, ec="none", lw=0.0, z=4.0):
        self.ax.add_patch(Polygon([self.T(p) for p in P], closed=True, fc=fc, ec=ec, lw=lw * MM, zorder=z, joinstyle="round"))

    def furn(self, P, z=4.0):
        self.poly(P, F_FC, F_EC, F_LW, z)

    def person(self, x, y, a, z=5.0):
        self.poly(ellipse(x, y, 1.05, 0.55, a), PERSON, "white", 0.04, z)
        self.poly(ellipse(x, y, 0.42, 0.42, a, 14), "#111111", z=z + 0.1)

    def chair(self, x, y, a, occ=0.0):
        """a = direction the sitter faces."""
        self.furn(rect(x, y, 1.7, 1.6, a + math.pi / 2), 4.2)
        bx, by = x - 0.75 * math.cos(a), y - 0.75 * math.sin(a)
        self.furn(rect(bx, by, 1.8, 0.35, a + math.pi / 2), 4.3)
        if self.rng.random() < occ:
            self.person(x + 0.1 * math.cos(a), y + 0.1 * math.sin(a), a + math.pi / 2, 4.6)

    def mark(self, cx, cy, w, h):
        self.taken.append((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))


# ---------- furniture pieces: f(sheet, cx, cy, rot, occ); footprint (w, h) at rot 0 ----------
def desk_cluster(S, cx, cy, rot, occ):          # 3 x 2 benching desks, 5 x 2.5 ft each
    for i in (-1, 0, 1):
        for j in (-1, 1):
            dx, dy = (i * 5.0, j * 1.25) if not rot else (j * 1.25, i * 5.0)
            S.furn(rect(cx + dx, cy + dy, 4.9, 2.4) if not rot else rect(cx + dx, cy + dy, 2.4, 4.9))
            ca = (math.pi / 2 if j < 0 else -math.pi / 2) if not rot else (0.0 if j < 0 else math.pi)
            ox, oy = (i * 5.0, j * 3.6) if not rot else (j * 3.6, i * 5.0)
            S.chair(cx + ox, cy + oy, ca, occ)


def round_table(d, n):
    def f(S, cx, cy, rot, occ):
        S.furn(ellipse(cx, cy, d / 2, d / 2, 0, 28))
        for k in range(n):
            t = 2 * math.pi * k / n
            S.chair(cx + (d / 2 + 1.0) * math.cos(t), cy + (d / 2 + 1.0) * math.sin(t), t + math.pi, occ)
    return f


def lounge_set(S, cx, cy, rot, occ):            # sofa + two armchairs + coffee table
    a = 0.0 if not rot else math.pi / 2
    c, s = math.cos(a), math.sin(a)
    P = lambda x, y: (cx + x * c - y * s, cy + x * s + y * c)
    S.furn(rect(*P(0, -3.6), 7.5, 2.8, a)); S.furn(rect(*P(0, -4.6), 7.5, 0.8, a), 4.3)
    S.furn(rect(*P(0, 0), 4.0, 2.2, a))
    for sx in (-1, 1):
        S.furn(rect(*P(sx * 2.4, 3.6), 2.8, 2.8, a)); S.furn(rect(*P(sx * 2.4, 4.6), 2.8, 0.7, a), 4.3)
    if S.rng.random() < occ:
        S.person(*P(-1.6, -3.4), a, 4.6)
    if S.rng.random() < occ:
        S.person(*P(2.4, 3.4), a + math.pi, 4.6)


def chaise(S, cx, cy, rot, occ):
    a = 0.0 if not rot else math.pi / 2
    S.furn(rect(cx, cy, 2.3, 6.4, a))
    S.furn(rect(cx, cy + 2.2, 2.3, 1.6) if not rot else rect(cx - 2.2, cy, 1.6, 2.3), 4.3)   # raised back
    if S.rng.random() < occ:
        S.person(cx, cy + (1.2 if not rot else 0), a, 4.6)


def tree(r):
    def f(S, cx, cy, rot, occ):
        S.poly(ellipse(cx, cy, r, r, 0, 30), TREE_FC, TREE_EC, 0.08, 4.8)
        S.poly(ellipse(cx, cy, r * 0.18, r * 0.18, 0, 12), TREE_EC, z=4.9)
    return f


def reformer(S, cx, cy, rot, occ):
    a = 0.0 if not rot else math.pi / 2
    S.furn(rect(cx, cy, 2.4, 8.0, a))
    S.furn(rect(cx, cy + (2.6 if not rot else 0), 2.0, 1.8, a) if not rot else rect(cx + 2.6, cy, 2.0, 1.8, a), 4.3)
    if S.rng.random() < occ:
        S.person(cx, cy, a, 4.6)


def massage(S, cx, cy, rot, occ):
    a = 0.0 if not rot else math.pi / 2
    S.furn(rect(cx, cy, 2.5, 6.5, a))
    if S.rng.random() < occ:
        S.person(cx, cy, a, 4.6)


def conf_table(S, P, occ):                         # one table sized to the room, long axis along the room
    xs = [p[0] for p in P]; ys = [p[1] for p in P]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w, h = x1 - x0, y1 - y0; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    long_x = w >= h
    L = max(6.0, (w if long_x else h) - 9.0); W = min(5.0, (h if long_x else w) - 7.0)
    if W < 2.5:
        return
    S.furn(rect(cx, cy, L, W) if long_x else rect(cx, cy, W, L))
    n = int(L // 2.6)
    for k in range(n):
        t = -L / 2 + 1.3 + k * (L - 2.6) / max(1, n - 1)
        for sgn in (-1, 1):
            if long_x:
                S.chair(cx + t, cy + sgn * (W / 2 + 1.0), -sgn * math.pi / 2, occ)
            else:
                S.chair(cx + sgn * (W / 2 + 1.0), cy + t, math.pi if sgn > 0 else 0.0, occ)
    S.mark(cx, cy, (L if long_x else W) + 4, (W if long_x else L) + 4)


def equipment(S, cx, cy, rot, occ):
    w, h = (8.0, 14.0) if not rot else (14.0, 8.0)
    S.poly(rect(cx, cy, w, h), EQ_FC, F_EC, F_LW, 4)
    S.poly(rect(cx, cy - h / 2 + 2 if not rot else cx, 6.0, 2.0) if not rot else rect(cx - w / 2 + 2, cy, 2.0, 6.0), "white", F_EC, F_LW, 4.1)


# ---------- placement ----------
def inside_all(pts_, P, avoid):
    for q in pts_:
        if not pp.inside(q, P):
            return False
        for a in avoid:
            if a[0] <= q[0] <= a[2] and a[1] <= q[1] <= a[3]:
                return False
    return True


def grid(S, P, piece, fw, fh, px, py, margin, occ, avoid=(), rot=None, every=None):
    xs = [p[0] for p in P]; ys = [p[1] for p in P]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    if rot is None:                                # long side of the piece along the long side of the room
        rot = int(((fw >= fh) != ((x1 - x0) >= (y1 - y0))))
    if rot:
        fw, fh, px, py = fh, fw, py, px
    nx = int((x1 - x0 - 2 * margin - fw) // px) + 1; ny = int((y1 - y0 - 2 * margin - fh) // py) + 1
    if nx < 1 or ny < 1:
        return 0
    sx = (x0 + x1) / 2 - (nx - 1) * px / 2; sy = (y0 + y1) / 2 - (ny - 1) * py / 2
    placed = 0
    for i in range(nx):
        for j in range(ny):
            if every and (i + j) % every == 0:
                continue
            cx, cy = sx + i * px, sy + j * py
            hw, hh = fw / 2 + margin, fh / 2 + margin
            pts_ = [(cx - hw, cy - hh), (cx + hw, cy - hh), (cx + hw, cy + hh), (cx - hw, cy + hh), (cx, cy)]
            if inside_all(pts_, P, avoid):
                piece(S, cx, cy, rot, occ); S.mark(cx, cy, fw, fh); placed += 1
    return placed


def scatter(S, P, sf_per, avoid=(), clump=True):
    xs = [p[0] for p in P]; ys = [p[1] for p in P]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    n = int(abs(pp.sarea(P)) / sf_per)
    got, tries = [], 0
    while len(got) < n and tries < n * 60:
        tries += 1
        x, y = S.rng.uniform(x0 + 1.5, x1 - 1.5), S.rng.uniform(y0 + 1.5, y1 - 1.5)
        if not inside_all([(x, y), (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)], P, avoid):
            continue
        if any(t[0] - 0.8 <= x <= t[2] + 0.8 and t[1] - 0.8 <= y <= t[3] + 0.8 for t in S.taken):
            continue
        if any((x - gx) ** 2 + (y - gy) ** 2 < 6.0 for gx, gy in got):
            continue
        a = S.rng.uniform(0, 2 * math.pi)
        S.person(x, y, a); got.append((x, y))
        if clump and S.rng.random() < 0.45:      # a second person facing the first
            d = 2.4; x2, y2 = x + d * math.cos(a + math.pi / 2), y + d * math.sin(a + math.pi / 2)
            if inside_all([(x2, y2)], P, avoid):
                S.person(x2, y2, a + math.pi); got.append((x2, y2))


def exec_office(S, P, avoid, exits):
    """Office 2 (executive): window suites on the whole perimeter, corridor inside them,
    associate workstations around the core; reception and waiting at the passenger-lobby exits.
    exits = [(x_core_face, side, y_mid)] with side -1 (west face) / +1 (east face)."""
    GLASS = "#7F8C99"
    xs = [p[0] for p in P]; ys = [p[1] for p in P]
    x0, x1, y0, y1 = min(xs) + 0.6, max(xs) - 0.6, min(ys) + 0.6, max(ys) - 0.6
    D, C, G = 15.0, 20.0, 6.0                        # suite depth, corner suite, corridor

    def split(a, b, m=15.0):
        n = max(1, int(round((b - a) / m))); w = (b - a) / n
        return [(a + i * w, a + (i + 1) * w) for i in range(n)]
    suites = []
    for ya, yb in split(y0 + C, y1 - C):
        suites += [((-1, 0), x0, x0 + D, ya, yb), ((1, 0), x1 - D, x1, ya, yb)]
    for xa, xb in split(x0 + C, x1 - C):
        suites += [((0, -1), xa, xb, y0, y0 + D), ((0, 1), xa, xb, y1 - D, y1)]
    corners = [((0, -1), x0, x0 + C, y0, y0 + C), ((0, -1), x1 - C, x1, y0, y0 + C),
               ((0, 1), x0, x0 + C, y1 - C, y1), ((0, 1), x1 - C, x1, y1 - C, y1)]
    for (wx, wy), a0, a1, b0, b1 in suites + corners:
        S.poly([(a0, b0), (a1, b0), (a1, b1), (a0, b1)], "none", GLASS, 0.06, 5.5)
        cx, cy = (a0 + a1) / 2, (b0 + b1) / 2
        depth = (a1 - a0) if wx else (b1 - b0)
        dx, dy = cx + wx * (depth / 2 - 5.0), cy + wy * (depth / 2 - 5.0)      # desk 5 ft off the glass
        horiz = wy != 0                                                       # desk long side parallel to the glass
        S.furn(rect(dx, dy, 6.0, 2.6) if horiz else rect(dx, dy, 2.6, 6.0))
        face_in = math.atan2(-wy, -wx)
        S.chair(dx + wx * 2.1, dy + wy * 2.1, face_in, 0.85)                 # exec chair, back to the view
        for k in (-1.5, 1.5):                                                 # two guest chairs
            gx, gy = (dx + k, dy - wy * 2.3) if horiz else (dx - wx * 2.3, dy + k)
            S.chair(gx, gy, face_in + math.pi, 0.25)
        if horiz:                                                             # plant in the glass corner
            tx, ty = a1 - 1.8, (b1 - 1.8 if wy > 0 else b0 + 1.8)
        else:
            tx, ty = (a1 - 1.8 if wx > 0 else a0 + 1.8), b1 - 1.8
        tree(1.1)(S, tx, ty, 0, 0)
        if (a1 - a0) >= C - 0.1 and (b1 - b0) >= C - 0.1:                      # corner suite: small sofa + table
            sx, sy = cx - wx * 4.0, cy - wy * 4.0
            S.furn(rect(sx, sy - 2.0, 6.0, 2.4) if horiz else rect(sx - 2.0, sy, 2.4, 6.0))
            S.furn(rect(sx, sy + 1.0, 3.2, 1.8) if horiz else rect(sx + 1.0, sy, 1.8, 3.2))
        S.mark(cx, cy, a1 - a0, b1 - b0)
    # interior zone inside the corridor ring
    ix0, ix1, iy0, iy1 = x0 + D + G, x1 - D - G, y0 + D + G, y1 - D - G
    inner = [(ix0, iy0), (ix1, iy0), (ix1, iy1), (ix0, iy1)]
    extra = []
    for n, (xf, side, ym) in enumerate(sorted(exits, key=lambda e: e[1])):
        xe = ix0 if side < 0 else ix1                       # inner edge of the corridor ring on that side
        zone = (min(xf, xe) - 0.5, ym - 15.0, max(xf, xe) + 0.5, ym + 15.0)
        extra.append(zone); S.taken.append(zone)
        if n == 0:                                          # reception: counter facing the lobby exit, staff behind it
            cx = xf + side * 10.0
            S.furn(rect(cx, ym, 3.0, 13.0)); S.furn(rect(cx + side * 1.5, ym + 5.0, 3.0, 3.0))
            for k2 in (-3.0, 3.0):
                S.chair(cx + side * 2.6, ym + k2, 0.0 if side > 0 else math.pi, 1.0)
            S.person(xf + side * 5.5, ym - 1.5, 0.0 if side < 0 else math.pi)
            S.person(xf + side * 5.0, ym + 2.0, 0.3 if side < 0 else math.pi + 0.3)
            tree(1.6)(S, cx, ym - 11.0, 0, 0); tree(1.6)(S, cx, ym + 11.0, 0, 0)
        else:                                               # waiting lounge at the other exit
            cx = xf + side * 11.0
            for k2 in (-4.0, 0.0, 4.0):
                S.furn(rect(cx + side * 2.5, ym + k2, 2.8, 2.8)); S.furn(rect(cx + side * 3.6, ym + k2, 0.6, 2.8), 4.3)
            S.furn(rect(cx - side * 0.5, ym, 2.0, 7.0))
            S.person(cx + side * 2.5, ym - 4.0, math.pi / 2 if side > 0 else -math.pi / 2)
            S.person(xf + side * 4.0, ym + 1.0, 0.0)
            tree(1.6)(S, cx, ym - 11.0, 0, 0); tree(1.6)(S, cx, ym + 11.0, 0, 0)
    grid(S, inner, desk_cluster, 15, 11, 18, 14, 1.5, 0.6, list(avoid) + extra)
    scatter(S, P, 2200, avoid)


def furnish_room(S, name, P, avoid):
    n = name.upper()
    if re.search(r"LOBBY|CORRIDOR", n):
        scatter(S, P, 220, clump=False)
    elif re.search(r"BALLROOM", n):
        grid(S, P, round_table(6.0, 8), 10, 10, 12.5, 12.5, 2.5, 0.55)
    elif re.search(r"PREFUNCTION", n):
        grid(S, P, round_table(2.6, 0), 2.6, 2.6, 14, 14, 4, 0); scatter(S, P, 90)
    elif re.search(r"BOARDROOM|OFFICE POD", n):
        conf_table(S, P, 0.5)
    elif re.search(r"^COWORKING$", n):
        grid(S, P, desk_cluster, 15, 11, 19, 15, 3, 0.5)
    elif re.search(r"MASSAGE", n):
        grid(S, P, massage, 2.5, 6.5, 9, 11, 2.5, 0.6)
    elif re.search(r"PILATES", n):
        grid(S, P, reformer, 2.4, 8.0, 5.5, 11, 3, 0.6)
    elif re.search(r"JUICE|CAFE|WINDOW BAR|BAR \(", n):
        grid(S, P, round_table(2.6, 3), 6.5, 6.5, 8, 8, 1.5, 0.45); scatter(S, P, 400)
    elif re.search(r"LOUNGE|READING|INDOOR-OUTDOOR|SPA LOBBY", n):
        grid(S, P, lounge_set, 9, 11, 16, 15, 3, 0.5); scatter(S, P, 450)
    elif re.search(r"TERRACE|PATIO|DECK|LOGGIA|OUTDOOR", n):
        grid(S, P, tree(4.5), 9, 9, 26, 26, 3, 0, avoid)
        grid(S, P, chaise, 2.3, 6.4, 5, 30, 3, 0.4, avoid, every=2)
        scatter(S, P, 450, avoid)
    elif re.search(r"MECH ZONE|BOILER|FAN|GENERATOR|SUBSTATION|CHW|DOMESTIC|COOLING|MECHANICAL", n):
        grid(S, P, equipment, 8, 14, 12, 18, 3, 0)


def render(objs, plan, fpi, out_file, fmt="svg", seed=7):
    pfx, lev, pname, elev, (xa, xb) = plan
    mine = [o for o in objs if xa - 25 <= o["bb"][0] and o["bb"][2] <= xb + 25 and o["bb"][1] > 1900]
    geo = [o for o in mine if o["type"] != "Text" and o["layer"] not in ("06_Wall_Axis", "09_Titles")]
    slab = [o for o in geo if o["layer"] == "01_Floors" and "slab boundary" in o["name"]]
    X0 = min(o["bb"][0] for o in geo); X1 = max(o["bb"][2] for o in geo)
    Y0 = min(o["bb"][1] for o in geo); Y1 = max(o["bb"][3] for o in geo)
    pad = 2.0
    pw, ph = (Y1 - Y0 + 2 * pad) / fpi, (X1 - X0 + 2 * pad) / fpi

    def T(p):   # 90 deg CCW, north points left (same as the print sheets)
        return ((Y1 + pad - p[1]) / fpi, (p[0] - X0 + pad) / fpi)

    fig = plt.figure(figsize=(pw, ph)); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, pw); ax.set_ylim(0, ph); ax.set_aspect("equal"); ax.axis("off")
    S = Sheet(ax, T, fpi, random.Random(seed))
    used = []

    def fillc(k):
        if k not in used and k != "POOL":
            used.append(k)
        return POOL if k == "POOL" else (NOSTOP if k == "NOSTOP" else (ACCENT if k == HERO.get(pfx) else COL[k]))

    # colour fields
    for o in slab:
        P = pp.pts(o["g"])
        S.poly(P, "white", z=0.5)
        if pfx in BASE:
            S.poly(P, fillc(BASE[pfx]), z=1)
    outdoor = []
    for o in geo:
        if o["layer"] == "01_Floors" and "slab boundary" not in o["name"] and "inner loop" not in o["name"]:
            nm = o["name"].split(" ", 1)[1]
            k = "POOL" if nm.startswith("POOL") else "OUTDOOR"
            S.poly(pp.pts(o["g"]), fillc(k), z=1.5)
            outdoor.append((nm, pp.pts(o["g"])))
    rooms = [pp.pts(o["g"]) for o in geo if o["layer"] == "07_Rooms" and o["type"] == "PolylineCurve"]
    tagged = []
    for t in [o for o in mine if o["layer"] == "07_Rooms" and o["type"] == "Text"]:
        nm = pp.clean(t["g"].PlainText.split("\n")[0])
        k = program(nm)
        if pfx in ("L1", "L2") and k in ("HOTEL", "AMENITY"):   # v1.4: office-floor rooms (exec offices, suites, reception) read as office
            k = "OFFICE"
        p = (t["bb"][0], t["bb"][1]); best = None
        for P in rooms:
            if len(P) > 2 and pp.inside(p, P):
                a = abs(pp.sarea(P))
                if best is None or a < best[0]:
                    best = (a, P)
        if best and k != "OFFICE" and nm != "RAMP OPENING":
            tagged.append((nm, best[1]))
    bbox = lambda P: (min(q[0] for q in P), min(q[1] for q in P), max(q[0] for q in P), max(q[1] for q in P))
    touch = lambda a, b, tol=0.6: a[0] - tol <= b[2] and b[0] - tol <= a[2] and a[1] - tol <= b[3] and b[1] - tol <= a[3]
    shafts, svc, pax = [], [], []
    for o in geo:
        if o["layer"] != "08_Shafts" or o["type"] != "PolylineCurve":
            continue
        P = pp.pts(o["g"]); shafts.append(P)
        src = o["us"].get("Source", o["name"].split()[2] if len(o["name"].split()) > 2 else "")
        stop = o["us"].get("StopAtLevel", "Yes") == "Yes"
        if not stop:
            k = "NOSTOP"
        elif src in ("SERVICE", "HOTELSVC"):
            k = "BOH"; svc.append(bbox(P))
        else:
            k = "CIRCULATION"
            if src != "STAIR":
                pax.append(bbox(P))
        S.poly(P, fillc(k), z=3)
        if src != "STAIR":                                # elevator symbol: thin X
            b = bbox(P)
            for a_, b_ in (((b[0], b[1]), (b[2], b[3])), ((b[0], b[3]), (b[2], b[1]))):
                Q = [T(a_), T(b_)]
                ax.plot([Q[0][0], Q[1][0]], [Q[0][1], Q[1][1]], color="#B5B5B5", lw=0.04 * MM, zorder=3.1)
    # lobbies: the largest one at the passenger cars is the passenger lobby; lobbies at service cars = back of house
    lobbies = sorted([(abs(pp.sarea(P)), nm, P) for nm, P in tagged if nm.startswith("LOBBY")], key=lambda e: -e[0])
    pax_lobby = next((P for a_, nm, P in lobbies if any(touch(bbox(P), q) for q in pax)), None)
    for nm, P in tagged:
        k = program(nm)
        if nm.startswith("LOBBY") and P is not pax_lobby and any(touch(bbox(P), q) for q in svc):
            k = "BOH"
        S.poly(P, fillc(k), z=2)

    # model furniture / plumbing / doors (hotel rooms carry them)
    for o in geo:
        L = o["layer"]
        if L not in ("11_Doors", "12_Plumbing", "13_Furniture"):
            continue
        P = pp.pts(o["g"])
        closed = len(P) > 3 and abs(P[0][0] - P[-1][0]) < 1e-6 and abs(P[0][1] - P[-1][1]) < 1e-6
        if closed and L != "11_Doors":
            S.poly(P, F_FC, F_EC, F_LW, 4.0 if L == "13_Furniture" else 4.1)
        else:
            Q = [T(q) for q in P]
            ax.plot([q[0] for q in Q], [q[1] for q in Q], color=F_EC, lw=(0.05 if L == "11_Doors" else F_LW) * MM, zorder=4.2)
    has_model_furniture = any(o["layer"] == "13_Furniture" for o in geo)

    # generated furniture + people
    core_avoid = []
    for P in rooms + shafts:
        xs = [q[0] for q in P]; ys = [q[1] for q in P]
        if abs(pp.sarea(P)) < 5000:
            core_avoid.append((min(xs) - 4, min(ys) - 4, max(xs) + 4, max(ys) + 4))
    gen = pfx not in NOGEN                                      # --nogen: the model carries the furniture for this plan
    if gen and pfx == "L1":                                     # Office 1, open office: desk clusters around the core
        for o in slab:
            P = pp.pts(o["g"])
            grid(S, P, desk_cluster, 15, 11, 19, 14.5, 4, 0.55, core_avoid)
            scatter(S, P, 1600, core_avoid)
    exits, cuts = [], []
    if pfx in ("L1", "L2") and pax_lobby is not None:          # passenger lobby runs through the core: open both ends
        lb = bbox(pax_lobby)
        for o in geo:
            if o["layer"] == "02_Walls_Core_12in" and touch(o["bb"], lb, 0.2):
                cb = o["bb"]
                if lb[0] - cb[0] < 1.5:
                    cuts.append((cb[0] - 0.3, lb[1] + 0.1, lb[0] + 0.3, lb[3] - 0.1)); exits.append((cb[0], -1, (lb[1] + lb[3]) / 2))
                if cb[2] - lb[2] < 1.5:
                    cuts.append((lb[2] - 0.3, lb[1] + 0.1, cb[2] + 0.3, lb[3] - 0.1)); exits.append((cb[2], 1, (lb[1] + lb[3]) / 2))
        ex = {}
        for e in exits:                                        # one exit per side (outer face of the core wall)
            if e[1] not in ex or (e[0] < ex[e[1]][0] if e[1] < 0 else e[0] > ex[e[1]][0]):
                ex[e[1]] = e
        exits = list(ex.values())
        for c in cuts:
            S.poly([(c[0], c[1]), (c[2], c[1]), (c[2], c[3]), (c[0], c[3])], COL["CIRCULATION"], z=6.5)
    if gen and pfx == "L2":                                     # Office 2, executive: window suites + associates + reception at the lobby
        for o in slab:
            exec_office(S, pp.pts(o["g"]), core_avoid, exits)
    if not gen:
        pass                                                    # model furniture only (drawn above)
    elif not has_model_furniture:
        for nm, P in tagged:
            furnish_room(S, nm, P, core_avoid)
    else:
        for nm, P in tagged:
            if program(nm) == "CIRCULATION":
                scatter(S, P, 260, clump=False)
    for nm, P in outdoor:
        if gen and not nm.startswith("POOL"):
            furnish_room(S, nm if re.search(r"TERRACE|PATIO|DECK|LOGGIA|OUTDOOR", nm) else "TERRACE", P, [r for r in core_avoid] + [
                (min(q[0] for q in R), min(q[1] for q in R), max(q[0] for q in R), max(q[1] for q in R)) for _, R in tagged])

    # walls + slab edge on top
    for lay, lw in (("02_Walls_Core_12in", 0.10), ("03_Walls_Interior_8in", 0.06),
                    ("04_Walls_Demising_6in", 0.05), ("10_Walls_Partition_5in", 0.04)):
        loops = [[T(p) for p in pp.pts(o["g"])] for o in geo if o["layer"] == lay and o["type"] == "NurbsCurve"]
        loops = [L for L in loops if len(L) > 2]
        if loops:
            ax.add_patch(PathPatch(pp.compound(loops), fc=WALL, ec=WALL, lw=lw * MM, joinstyle="miter", zorder=6))
    for o in slab:
        S.poly(pp.pts(o["g"]), "none", WALL, 0.30, 7)
    for o in geo:
        if o["layer"] == "05_Walls_Curtain":
            Q = [T(q) for q in pp.pts(o["g"])]
            ax.plot([q[0] for q in Q], [q[1] for q in Q], color=WALL, lw=0.30 * MM, zorder=7)
    if fmt == "svg":
        fig.savefig(out_file, format="svg", transparent=True)   # vector for the web page
    else:
        fig.savefig(out_file, format="png", dpi=450, transparent=True)
    plt.close(fig)
    return pw, ph, used


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Furnished program plans, one file per level (read-only on the model).")
    ap.add_argument("planprint"); ap.add_argument("model"); ap.add_argument("out")
    ap.add_argument("extra", nargs="*", help="V14 (rename L06->L05, L07-L15->L06-L15) and/or level keys to render")
    ap.add_argument("--fmt", choices=("svg", "png"), default="svg", help="output format (default svg; png = 450 dpi)")
    ap.add_argument("--accent", default=ACCENT, help="accent colour as #RRGGBB (default %s)" % ACCENT)
    ap.add_argument("--nogen", default="", help="comma list of plan prefixes (e.g. L1,L2) whose generated furniture is skipped")
    args = ap.parse_args()
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", args.accent):
        sys.exit("--accent must be #RRGGBB, got %r" % args.accent)
    ACCENT = args.accent.upper()
    NOGEN = {s.strip() for s in args.nogen.split(",") if s.strip()}
    objs = pp.load(args.model); out = args.out; os.makedirs(out, exist_ok=True)
    V14 = {"L06": "L05", "L07-L15": "L06-L15"} if "V14" in args.extra else {}
    only = [a for a in args.extra if a != "V14"]
    legend = {}
    for plan in pp.PLANS:
        name = V14.get(plan[1], plan[1])
        if only and name not in only:
            continue
        f = os.path.join(out, "PlanColor_%s_%s.%s" % (name, VERSION, args.fmt))
        w, h, used = render(objs, plan, 40.0, f, args.fmt)
        legend[name] = used
        print("%-8s %5.2f x %4.2f in  %9d bytes  %s" % (name, w, h, os.path.getsize(f), ",".join(used)))
    lf = os.path.join(out, "legend_%s.json" % VERSION)
    old = json.load(open(lf)) if os.path.exists(lf) else {}
    old.update(legend); json.dump(old, open(lf, "w"), indent=1)
    print("accent", ACCENT, "fmt", args.fmt, "nogen", sorted(NOGEN) or "-", "->", lf)
