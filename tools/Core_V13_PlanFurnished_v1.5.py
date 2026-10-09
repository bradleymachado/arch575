# -*- coding: utf-8 -*-
"""Core_V13_PlanFurnished_v1.5
This section is intended to render the furnished program plans (one SVG or PNG per level) from the V14 Rhino model,
read-only: hero program in a light tint of the accent so the doors read, black door leaves and swings, and people
on every floor plate for scale.
v1.5 (Brad 2026-10-09): HERO_FILL = 35 pct tint of the accent (--hero-tint 0-1, default 0.35 -> #E3BDB1) on the hero
program of every level; OUTDOOR #F6E9E4 (12 pct), POOL #D7A18F unchanged; ACCENT #B0431F kept as a constant (3D tower).
11_Doors in WALL #111111: leaf 0.07, swing arc and opening line 0.035 (x MM), zorder 5.3 above furniture and people.
People pass after furniture on every level, --nogen plans included: rasterised exclusion (walls, shafts, stairs,
elevators, MEP rooms, pool, furniture / plumbing bounding boxes + generated pieces, door swings) with 1.5 ft
clearance; density by room type (room_rule); seated at chairs, standing / walking, some pairs facing; seeded
(crc32 of the level) so re-runs are identical; prints people per plan. Generators no longer place people
themselves (they record seats). B1: the service cars (SV / HS) are the hero; plant rooms BOH grey; MEP closets MEP.
Writes PlanColor_<key>_v1.5.<fmt> and legend_v1.5.json (adds "_colours").
v1.3 - SVG output, oxide accent, generator switch (arch575.bradmachado.com, plan S3).
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
import sys, os, re, math, json, random, importlib.util, argparse, zlib
import numpy as np
from PIL import Image, ImageDraw
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, Polygon

spec = importlib.util.spec_from_file_location("pp", sys.argv[1]); pp = importlib.util.module_from_spec(spec); spec.loader.exec_module(pp)
MM = pp.MM

VERSION = "v1.5"
ACCENT = "#B0431F"                                 # oxide red, main-site accent (plan v1.1 D2); the 3D tower, not the plan
HERO_TINT = 0.35                                   # v1.5: hero fill = this share of the accent mixed with white
tint = lambda hexc, t: "#%02X%02X%02X" % tuple(int(round(t * int(hexc[i:i + 2], 16) + (1 - t) * 255)) for i in (1, 3, 5))
HERO_FILL = tint(ACCENT, HERO_TINT)                # #E3BDB1 at 0.35
COL = {"OFFICE": "#B5B5B5", "HOTEL": "#B5B5B5", "AMENITY": "#B5B5B5", "OUTDOOR": "#F6E9E4",
       "CIRCULATION": "#FFFFFF", "BOH": "#D9D9D9", "MEP": "#3A3A3A", "SERVICE": "#D9D9D9"}
POOL = "#D7A18F"; WALL = "#111111"; NOSTOP = "#F0F0F0"
HERO = {"K": "SERVICE", "U": "AMENITY", "L1": "OFFICE", "M": "MEP", "V": "AMENITY", "L2": "OFFICE", "N": "MEP",
        "W": "AMENITY", "L3A": "HOTEL", "L3B": "HOTEL"}             # the program each level is about = the accent
F_FC, F_EC, F_LW = "#FFFFFF", "#6E6E6E", 0.07      # furniture: white, thin grey edge
EQ_FC = "#F2F2F2"                                  # mech equipment (on dark MEP / accent)
PERSON = "#4A4A4A"; TREE_FC, TREE_EC = "#FFFFFF", "#9A9A9A"
NOGEN = set()                                      # plan prefixes whose generated furniture is skipped (--nogen)
DOOR_LEAF, DOOR_ARC = 0.07, 0.035                  # v1.5 door line weights (mm, x MM -> pt)
LEVEL_KEY = {}                                     # model level -> output key (V14 rename), set in __main__
PEOPLE_COUNT = {}                                  # output key -> people drawn (last render)

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
        self.furnishing = True   # v1.5: furniture phase records obstacles + seats; people come from people_pass()
        self.obst, self.obst_lines, self.swings, self.seats, self.people = [], [], [], [], []

    def poly(self, P, fc, ec="none", lw=0.0, z=4.0):
        self.ax.add_patch(Polygon([self.T(p) for p in P], closed=True, fc=fc, ec=ec, lw=lw * MM, zorder=z, joinstyle="round"))
        if self.furnishing and 4.0 <= z < 5.0:
            self.obst.append(list(P))

    def seat(self, x, y, a, kind="chair"):
        """v1.5: a place a person can sit / lie; a = shoulder line angle (as person())."""
        self.seats.append((x, y, a, kind))

    def furn(self, P, z=4.0):
        self.poly(P, F_FC, F_EC, F_LW, z)

    def person(self, x, y, a, z=5.0):
        if self.furnishing:      # v1.5: the people pass places everyone
            return
        self.people.append((x, y, a, z))
        self.poly(ellipse(x, y, 1.05, 0.55, a), PERSON, "white", 0.04, z)
        self.poly(ellipse(x, y, 0.42, 0.42, a, 14), "#111111", z=z + 0.1)

    def chair(self, x, y, a, occ=0.0):
        """a = direction the sitter faces."""
        self.furn(rect(x, y, 1.7, 1.6, a + math.pi / 2), 4.2)
        bx, by = x - 0.75 * math.cos(a), y - 0.75 * math.sin(a)
        self.furn(rect(bx, by, 1.8, 0.35, a + math.pi / 2), 4.3)
        self.seat(x + 0.1 * math.cos(a), y + 0.1 * math.sin(a), a + math.pi / 2, "chair")

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
    S.seat(*P(-1.6, -3.4), a, "chair"); S.seat(*P(1.6, -3.4), a, "chair")
    S.seat(*P(2.4, 3.4), a + math.pi, "chair"); S.seat(*P(-2.4, 3.4), a + math.pi, "chair")


def chaise(S, cx, cy, rot, occ):
    a = 0.0 if not rot else math.pi / 2
    S.furn(rect(cx, cy, 2.3, 6.4, a))
    S.furn(rect(cx, cy + 2.2, 2.3, 1.6) if not rot else rect(cx - 2.2, cy, 1.6, 2.3), 4.3)   # raised back
    S.seat(cx, cy + (1.2 if not rot else 0), a, "lie")


def tree(r):
    def f(S, cx, cy, rot, occ):
        S.poly(ellipse(cx, cy, r, r, 0, 30), TREE_FC, TREE_EC, 0.08, 4.8)
        S.poly(ellipse(cx, cy, r * 0.18, r * 0.18, 0, 12), TREE_EC, z=4.9)
    return f


def reformer(S, cx, cy, rot, occ):
    a = 0.0 if not rot else math.pi / 2
    S.furn(rect(cx, cy, 2.4, 8.0, a))
    S.furn(rect(cx, cy + (2.6 if not rot else 0), 2.0, 1.8, a) if not rot else rect(cx + 2.6, cy, 2.0, 1.8, a), 4.3)
    S.seat(cx, cy, a, "station")


def massage(S, cx, cy, rot, occ):
    a = 0.0 if not rot else math.pi / 2
    S.furn(rect(cx, cy, 2.5, 6.5, a))
    S.seat(cx, cy, a, "table")


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
    if S.furnishing:                               # v1.5: people come from people_pass()
        return
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


# ---------- v1.5 people pass ----------
# This section is intended to put top-view people on every floor plate after all furniture is drawn: a 0.25 ft
# raster of what a person may not stand on (walls, curtain wall, shafts / stairs / elevators, MEP rooms, pool,
# furniture + plumbing bounding boxes, generated pieces, door swings), grown by 1.5 ft; a room-id raster (smallest
# room wins, the rest of the slab = residual); then per room type a count from the density rule, seated people at
# chairs / stations, standing and walking people on free floor, some pairs facing. Seeded per level.
RES, CLEAR, BODY = 0.25, 1.5, 1.05
SEAT_RX = [("exec", r"Executive Chair"),
           ("chair", r"Task Chair|Guest Chair|Dining Chair|Desk Chair|Bar Stool|Lounge Chair"),
           ("sofa", r"Sofa \d"), ("lie", r"Chaise Lounge|Daybed"), ("station", r"Reformer|Exercise Bike")]
TABLE_RX = r"Desk|Table|Counter|Island"
# density by room type (Brad 2026-10-09): sf per person, or share of seats / stations
RATE = {"OPEN": 250, "LOUNGE": 200, "CAFE": 60, "OUTDOOR": 300, "CORR": 300}


def room_rule(nm, pfx):
    n = nm.upper()
    if n == "_RESIDUAL":
        return {"L1": "OPEN", "L2": "OPEN", "K": "PLANT", "U": "CORR", "V": "CORR", "W": "CORR"}.get(pfx)
    if pfx in ("K", "M", "N"):                     # plant floors: maintenance staff in corridors / back of house only
        return "PLANT" if re.search(r"LOBBY|CORRIDOR|STORAGE|BOH|BLDG MGMT|MAINTENANCE", n) else None
    if re.search(r"^MEP|TOILET|RESTROOM|STORAGE|RAMP|SERVICE STRIP|BACK BAR|PANTRY|^BOH|BACK OF HOUSE|^SERVICE CORRIDOR|^POOL$", n):
        return None
    if re.search(r"TERRACE|PATIO|DECK|LOGGIA|OUTDOOR", n):
        return "OUTDOOR"
    if re.search(r"CORRIDOR", n):
        return "HCORR" if pfx in ("L3A", "L3B") else "CORR"
    if re.search(r"EXEC OFFICE|EXEC SUITE|INDIVIDUAL|FOCUS", n):
        return "PRIVATE"
    if re.search(r"HUDDLE|BOARDROOM|OFFICE POD|CONFERENCE ROOM|MEETING", n):
        return "CONF"
    if re.search(r"OPEN OFFICE|COWORKING|ASSOCIATES", n):
        return "OPEN"
    if re.search(r"CAFE|BAR\b|JUICE", n):
        return "CAFE"
    if re.search(r"PILATES|FITNESS|EXERCISE", n):
        return "FIT"
    if re.search(r"MASSAGE|SPA ROOM", n):
        return "SPA"
    if re.search(r"SUITE|DLX|STD", n):
        return "GUEST"
    return "LOUNGE"                                # reception, lobby, lounge, reading, prefunction, ballroom


def model_seats(S, o, P):
    """Record model chairs / sofas / chaises / stations as seats, desks and tables for chair facing."""
    if not hasattr(S, "mseats"):
        S.mseats, S.tables = [], []
    nm = o["name"]
    for kind, rx in SEAT_RX:
        if re.search(rx, nm):
            S.mseats.append((kind, P))
            return
    if re.search(TABLE_RX, nm):
        S.tables.append(P)


def _bb(P):
    xs = [p[0] for p in P]; ys = [p[1] for p in P]
    return min(xs), min(ys), max(xs), max(ys)


def _resolve_seats(S, rng):
    tb = [_bb(P) for P in getattr(S, "tables", [])]

    def nearest_table(cx, cy, r):
        best = None
        for t in tb:
            if t[0] <= cx <= t[2] and t[1] <= cy <= t[3]:
                continue
            nx, ny = min(max(cx, t[0]), t[2]), min(max(cy, t[1]), t[3])
            d = math.hypot(nx - cx, ny - cy)
            if d < r and (best is None or d < best[0]):
                best = (d, nx, ny)
        return best
    out = list(S.seats)                            # generated seats: (x, y, shoulder angle, kind)
    for kind, P in getattr(S, "mseats", []):
        b = _bb(P); cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2; w, h = b[2] - b[0], b[3] - b[1]
        if kind in ("chair", "exec"):
            t = nearest_table(cx, cy, 4.0)
            f = math.atan2(t[2] - cy, t[1] - cx) if t else rng.uniform(0, 2 * math.pi)
            out.append((cx + 0.1 * math.cos(f), cy + 0.1 * math.sin(f), f + math.pi / 2, kind))
        elif kind == "sofa":
            long_x = w >= h; L = max(w, h)
            t = nearest_table(cx, cy, 6.0)
            sgn = (1 if (t[2] if long_x else t[1]) > (cy if long_x else cx) else -1) if t else rng.choice((-1, 1))
            for k in (-0.25, 0.25):
                if long_x:
                    out.append((cx + k * L, cy + sgn * 0.3, 0.0, "chair"))
                else:
                    out.append((cx + sgn * 0.3, cy + k * L, math.pi / 2, "chair"))
        else:                                      # lie / station: along the long axis, shoulders across it
            out.append((cx, cy, 0.0 if h >= w else math.pi / 2, kind))
    return out


def _dilate(m, r):
    out = m.copy(); n = int(math.ceil(r / RES)); H, W = m.shape
    for di in range(-n, n + 1):
        for dj in range(-n, n + 1):
            if di * di + dj * dj > n * n or (di == 0 and dj == 0):
                continue
            out[max(0, di):H + min(0, di), max(0, dj):W + min(0, dj)] |= m[max(0, -di):H + min(0, -di), max(0, -dj):W + min(0, -dj)]
    return out


def people_pass(S, pfx, ext, slab, outdoor, named, shafts, wall_loops, curtain, seed):
    rng = random.Random(seed)
    X0, Y0, X1, Y1 = ext[0] - 3, ext[1] - 3, ext[2] + 3, ext[3] + 3
    W = int((X1 - X0) / RES) + 2; H = int((Y1 - Y0) / RES) + 2
    pix = lambda P: [((x - X0) / RES, (y - Y0) / RES) for x, y in P]
    ij = lambda x, y: (min(H - 1, max(0, int((y - Y0) / RES))), min(W - 1, max(0, int((x - X0) / RES))))

    def draw(polys, width=0.0, rects=False):
        im = Image.new("1", (W, H), 0); d = ImageDraw.Draw(im)
        for P in polys:
            if len(P) < 2:
                continue
            if rects:
                b = _bb(P); d.rectangle([((b[0] - X0) / RES, (b[1] - Y0) / RES), ((b[2] - X0) / RES, (b[3] - Y0) / RES)], fill=1)
            elif width:
                d.line(pix(P), fill=1, width=max(1, int(round(width / RES))))
            else:
                d.polygon(pix(P), fill=1, outline=1)
        return np.array(im, dtype=bool)

    walls = np.zeros((H, W), bool)
    for P in wall_loops:                           # even-odd per loop: rings stay rings
        if len(P) > 2:
            walls ^= draw([P])
    pools = [P for nm, P in outdoor if nm.startswith("POOL")]
    mep = [P for nm, P in named if program(nm) == "MEP"]
    edges = [list(pp.pts(o["g"])) for o in slab] + [list(P) for nm, P in outdoor]
    hard = walls | draw(curtain, 0.6) | draw([P + P[:1] for P in edges if P], 0.4) | draw(shafts) | draw(mep) | draw(pools)
    furn = draw(S.obst, rects=True) | draw(S.obst_lines, 0.3)
    swing = draw(S.swings, rects=True)
    raw = hard | furn | swing
    stand_ok = ~_dilate(raw, CLEAR)
    stand_tight = ~_dilate(raw, BODY + 0.15)     # fallback for narrow rooms (1 person, body still clear)

    # room id raster: largest first, so the smallest room wins; the rest of the slab is the residual region
    regions = [("_RESIDUAL", pp.pts(o["g"])) for o in slab] + [(nm, P) for nm, P in outdoor if not nm.startswith("POOL")] + list(named)
    regions = [(nm, P) for nm, P in regions if len(P) > 2]
    order = sorted(range(len(regions)), key=lambda i: -abs(pp.sarea(regions[i][1])))
    rid = np.full((H, W), -1, np.int32)
    for i in order:
        rid[draw([regions[i][1]])] = i
    if shafts:                                     # residual pixels inside the core are not floor
        cb = (min(_bb(P)[0] for P in shafts) - 1, min(_bb(P)[1] for P in shafts) - 1,
              max(_bb(P)[2] for P in shafts) + 1, max(_bb(P)[3] for P in shafts) + 1)
        r0, c0 = ij(cb[0], cb[1]); r1, c1 = ij(cb[2], cb[3])
        core = np.zeros((H, W), bool); core[r0:r1 + 1, c0:c1 + 1] = True
        rid[core & np.isin(rid, [i for i, (nm, _) in enumerate(regions) if nm == "_RESIDUAL"])] = -1

    seats = {}
    for x, y, a, kind in _resolve_seats(S, rng):
        r, c = ij(x, y)
        if hard[r, c] or swing[r, c] or rid[r, c] < 0:
            continue
        seats.setdefault(int(rid[r, c]), []).append((x, y, a, kind))
    placed = []                                    # (x, y, seated)

    def far(x, y, d=2.6):
        return all((x - px) ** 2 + (y - py) ** 2 >= d * d for px, py, _ in placed)

    def sit(cands, n):
        cands = [s for s in cands if far(s[0], s[1], 1.6)]
        got = 0
        for x, y, a, kind in rng.sample(cands, len(cands)):
            if got >= n:
                break
            if far(x, y, 1.6):
                S.person(x, y, a, 4.6); placed.append((x, y, True)); got += 1
        return got

    def stand(mask, n, walk=None, pair=0.0, ok=None):
        ok = stand_ok if ok is None else ok
        rr, cc = np.nonzero(mask & ok)
        got = 0
        if len(rr) == 0:
            return 0
        for _ in range(n * 80):
            if got >= n:
                break
            k = rng.randrange(len(rr)); x, y = X0 + (cc[k] + 0.5) * RES, Y0 + (rr[k] + 0.5) * RES
            if not far(x, y):
                continue
            a = (walk + math.pi / 2 + rng.uniform(-0.15, 0.15)) if walk is not None else rng.uniform(0, math.pi)
            S.person(x, y, a, 5.0); placed.append((x, y, False)); got += 1
            if got < n and rng.random() < pair:    # a second person facing the first
                f = a + math.pi / 2; x2, y2 = x + 2.4 * math.cos(f), y + 2.4 * math.sin(f)
                r2, c2 = ij(x2, y2)
                if mask[r2, c2] and ok[r2, c2] and all((x2 - px) ** 2 + (y2 - py) ** 2 >= 2.3 ** 2 for px, py, _ in placed):
                    S.person(x2, y2, a + math.pi, 5.0); placed.append((x2, y2, False)); got += 1
        return got

    rules = [room_rule(nm, pfx) for nm, P in regions]
    centre = lambda P: ((_bb(P)[0] + _bb(P)[2]) / 2, (_bb(P)[1] + _bb(P)[3]) / 2)
    by_type = {}
    for i, t in enumerate(rules):
        if t:
            by_type.setdefault(t, []).append(i)
    log = {}
    group = {"PLANT": [], "HCORR": []}
    for t in ("CONF", "PRIVATE", "FIT", "SPA", "CAFE", "GUEST", "OPEN", "LOUNGE", "OUTDOOR", "CORR", "PLANT", "HCORR"):
        idx = sorted(by_type.get(t, []), key=lambda i: (round(centre(regions[i][1])[0] / 5), centre(regions[i][1])[1]))
        for k, i in enumerate(idx):
            m = rid == i; area = m.sum() * RES * RES
            if area < 25:
                continue
            st = seats.get(i, []); chairs = [s for s in st if s[3] in ("chair", "exec")]
            b = _bb(regions[i][1]); walk = 0.0 if (b[2] - b[0]) >= (b[3] - b[1]) else math.pi / 2
            n = 0
            if t in ("PLANT", "HCORR"):
                group[t].append(m); continue
            if t == "OPEN":
                want = max(1, int(round(area / RATE["OPEN"])))
                n = sit(chairs, int(round(want * 0.7)))
                n += stand(m, want - n, pair=0.4)
            elif t == "PRIVATE":
                if k % 4 == 3:                     # skip 1 in 4
                    continue
                ex = [s for s in st if s[3] == "exec"]
                if not ex and chairs:              # the chair farthest from the door swings
                    dmin = lambda s: min([math.hypot(s[0] - (_bb(P)[0] + _bb(P)[2]) / 2, s[1] - (_bb(P)[1] + _bb(P)[3]) / 2) for P in S.swings] or [0])
                    ex = [max(chairs, key=dmin)]
                n = sit(ex[:1], 1) or stand(m, 1)
            elif t == "CONF":
                n = sit(chairs, max(1, int(round(rng.uniform(0.5, 0.7) * len(chairs))))) if chairs else stand(m, 1)
            elif t == "CAFE":
                if chairs:
                    n = sit(chairs, max(1, min(int(round(area / RATE["CAFE"])), int(round(0.8 * len(chairs))))))
                else:
                    n = stand(m, max(1, int(round(area / RATE["LOUNGE"]))), pair=0.4)
            elif t == "FIT":
                stn = [s for s in st if s[3] == "station"]
                n = sit(stn, max(1, int(round(0.6 * len(stn))))) if stn else stand(m, 1)
            elif t == "SPA":
                tb = [s for s in st if s[3] == "table"]
                n = sit(tb, 1) if tb else stand(m, 1)
            elif t == "GUEST":
                if k % 2 == 1:                     # 1 per 2 rooms
                    continue
                if st and rng.random() < 0.5:
                    n = sit([s for s in st if s[3] in ("chair", "exec")] or st, 1)
                n = n or stand(m, 1)
            elif t in ("LOUNGE", "OUTDOOR"):
                want = max(1, int(round(area / RATE[t])))
                n = sit(st, int(round(want * 0.5))) if st else 0
                n += stand(m, want - n, pair=0.45)
            elif t == "CORR":
                want = max(1, int(round(area / RATE["CORR"])))
                n = stand(m, want, walk=walk if (b[2] - b[0]) / max(1e-6, b[3] - b[1]) > 2.5 or (b[3] - b[1]) / max(1e-6, b[2] - b[0]) > 2.5 else None, pair=0.25)
            if n == 0:                             # at least 1 per occupiable room
                n = stand(m, 1, ok=stand_tight)
            log[t] = log.get(t, 0) + n
            if n == 0:
                log.setdefault("_empty", []).append(regions[i][0])
    for t, lo, hi in (("PLANT", 2, 4), ("HCORR", 3, 4)):
        if group[t]:
            m = np.logical_or.reduce(group[t])
            n = stand(m, rng.randint(lo, hi), pair=0.3 if t == "PLANT" else 0.0)
            log[t] = n
    # check: standing bodies clear of walls, shafts, stairs, furniture, swings; seated centres clear of walls + swings
    bad = 0
    for x, y, seated in placed:
        pts_ = [(x, y)] if seated else [(x, y)] + [(x + BODY * math.cos(2 * math.pi * q / 12), y + BODY * math.sin(2 * math.pi * q / 12)) for q in range(12)]
        chk = (hard | swing) if seated else raw
        bad += any(chk[ij(px, py)] for px, py in pts_)
    S.people_log = dict(log, _bad=bad, _seated=sum(1 for p in placed if p[2]))
    return len(placed)


def render(objs, plan, fpi, out_file, fmt="svg", seed=None):
    pfx, lev, pname, elev, (xa, xb) = plan
    seed = zlib.crc32(("people " + lev).encode()) if seed is None else seed      # v1.5: per-level seed, stable
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
        return POOL if k == "POOL" else (NOSTOP if k == "NOSTOP" else (HERO_FILL if k == HERO.get(pfx) else COL[k]))

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
            S.poly(pp.pts(o["g"]), fillc(k), z=1.6 if k == "POOL" else 1.5)    # v1.5: pool above its deck (was hidden)
            outdoor.append((nm, pp.pts(o["g"])))
    rooms = [pp.pts(o["g"]) for o in geo if o["layer"] == "07_Rooms" and o["type"] == "PolylineCurve"]
    tagged, named = [], []
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
        if best and nm != "RAMP OPENING":
            named.append((nm, best[1]))
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
            k = "SERVICE" if pfx == "K" else "BOH"; svc.append(bbox(P))     # v1.5: B1 hero = the service cars
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
    svc_lobby = set()
    for nm, P in tagged:
        k = program(nm)
        if nm.startswith("LOBBY") and P is not pax_lobby and any(touch(bbox(P), q) for q in svc):
            k = "BOH"; svc_lobby.add(id(P))     # v1.5: service lobbies get no people (except plant floors)
        if pfx == "K" and k == "MEP" and not nm.startswith("MEP CLOSET"):   # v1.5: B1 plant rooms back-of-house grey
            k = "BOH"
        S.poly(P, fillc(k), z=2)

    # model furniture / plumbing / doors (hotel rooms carry them)
    for o in geo:
        L = o["layer"]
        if L not in ("11_Doors", "12_Plumbing", "13_Furniture"):
            continue
        P = pp.pts(o["g"])
        closed = len(P) > 3 and abs(P[0][0] - P[-1][0]) < 1e-6 and abs(P[0][1] - P[-1][1]) < 1e-6
        Q = [T(q) for q in P]
        if L == "11_Doors":                        # v1.5: black, leaf 0.07 / arc + opening 0.035, above furniture
            leaf = o["type"] == "LineCurve" and o["name"].endswith("swing")
            ax.plot([q[0] for q in Q], [q[1] for q in Q], color=WALL, lw=(DOOR_LEAF if leaf else DOOR_ARC) * MM,
                    zorder=5.3, solid_capstyle="butt")
            if o["name"].endswith("swing"):
                S.swings.append(P)
        elif closed:
            S.poly(P, F_FC, F_EC, F_LW, 4.0 if L == "13_Furniture" else 4.1)
            if L == "13_Furniture":
                model_seats(S, o, P)
        else:
            ax.plot([q[0] for q in Q], [q[1] for q in Q], color=F_EC, lw=F_LW * MM, zorder=4.2)
            S.obst_lines.append(P)
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

    # v1.5: people on every plate (after all furniture, --nogen plans included)
    S.furnishing = False
    wall_loops = [pp.pts(o["g"]) for o in geo if o["layer"] in ("02_Walls_Core_12in", "03_Walls_Interior_8in",
                  "04_Walls_Demising_6in", "10_Walls_Partition_5in") and o["type"] == "NurbsCurve"]
    curtain = [pp.pts(o["g"]) for o in geo if o["layer"] == "05_Walls_Curtain"]
    named = [(("BOH " + nm) if id(P) in svc_lobby else nm, P) for nm, P in named]
    PEOPLE_COUNT[LEVEL_KEY.get(lev, lev)] = people_pass(S, pfx, (X0, Y0, X1, Y1), slab, outdoor, named, shafts,
                                                        wall_loops, curtain, seed)
    print("   people %-8s %s" % (LEVEL_KEY.get(lev, lev), S.people_log))

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
    ap.add_argument("--hero-tint", type=float, default=HERO_TINT, help="hero fill = this share of the accent on white, 0-1 (default 0.35)")
    args = ap.parse_args()
    if not 0.0 <= args.hero_tint <= 1.0:
        sys.exit("--hero-tint must be 0-1, got %r" % args.hero_tint)
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", args.accent):
        sys.exit("--accent must be #RRGGBB, got %r" % args.accent)
    ACCENT = args.accent.upper()
    HERO_TINT = args.hero_tint; HERO_FILL = tint(ACCENT, HERO_TINT)
    NOGEN = {s.strip() for s in args.nogen.split(",") if s.strip()}
    objs = pp.load(args.model); out = args.out; os.makedirs(out, exist_ok=True)
    V14 = {"L06": "L05", "L07-L15": "L06-L15"} if "V14" in args.extra else {}
    LEVEL_KEY.update(V14)
    only = [a for a in args.extra if a != "V14"]
    legend = {}
    for plan in pp.PLANS:
        name = V14.get(plan[1], plan[1])
        if only and name not in only:
            continue
        f = os.path.join(out, "PlanColor_%s_%s.%s" % (name, VERSION, args.fmt))
        w, h, used = render(objs, plan, 40.0, f, args.fmt)
        legend[name] = used
        print("%-8s %5.2f x %4.2f in  %9d bytes  people %4d  %s" % (name, w, h, os.path.getsize(f), PEOPLE_COUNT.get(name, 0), ",".join(used)))
    lf = os.path.join(out, "legend_%s.json" % VERSION)
    old = json.load(open(lf)) if os.path.exists(lf) else {}
    old.update(legend)
    old["_colours"] = {"ACCENT": ACCENT, "HERO_TINT": HERO_TINT, "HERO_FILL": HERO_FILL, "OUTDOOR": COL["OUTDOOR"],
                       "POOL": POOL, "PEOPLE": dict(PEOPLE_COUNT)}
    json.dump(old, open(lf, "w"), indent=1)
    print("hero fill", HERO_FILL, "outdoor", COL["OUTDOOR"], "pool", POOL)
    print("accent", ACCENT, "fmt", args.fmt, "nogen", sorted(NOGEN) or "-", "->", lf)
