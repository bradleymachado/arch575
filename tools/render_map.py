# render_map_v1.0 — This section is intended to geo-register the Rhino site model to Web Mercator from its
# OSM-id-named building extrusions (similarity fit, ICP on footprint vertices), and to render the two
# monochrome entry maps (assets/map-city.svg, assets/map-corridor.svg) plus data/site.json from the cached
# Overpass data in _local/osm_*.json (written by tools/fetch_osm.py).
#
# Usage (from the repo root):  python tools/render_map.py
# Reads the site model with rhino3dm only (read only; never saved).
# Map frame (both SVGs, site.json "map" values): x = mercX - origin[0], y = origin[1] - mercY (metres, y down).
import os, json, math, cmath
import numpy as np
import rhino3dm

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LOCAL = os.path.join(REPO, "_local")
ROOT = r"C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575"
SITE3DM = os.path.join(ROOT, r"02_Site\Arch575_BlenderSite_RhinoModel_v2.0.3dm")

R = 6378137.0
FT = 0.3048
CITY = (41.62, -87.98, 42.05, -87.50)          # s, w, n, e
CORRIDOR = (41.878, -87.662, 41.892, -87.618)
CONTEXT_LAYERS = ("buildings", "TERRAIN_MESH", "Bridges", "Roads")   # the S14 GLB layers

# tokens (plan section 0/1 + subdomain handoff section 4)
HAIR_DARK, HAIR_LIGHT = "#B5B5B5", "#D9D9D9"
PALE_WATER, PALE_BLDG = "#F2F1ED", "#E4E4E2"
INK, ACCENT = "#171715", "#B0431F"
MONO = "'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
ATTRIB = "Map data \u00a9 OpenStreetMap contributors"

MAJOR = {"motorway", "trunk", "primary", "secondary", "tertiary", "motorway_link", "trunk_link",
         "primary_link", "secondary_link", "tertiary_link"}
PED = {"footway", "path", "steps", "cycleway", "pedestrian", "corridor", "elevator", "platform",
       "bridleway", "track", "construction", "proposed", "bus_stop", "busway", "via_ferrata"}


def merc(lat, lon):
    return R * math.radians(lon), R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def inv_lat(my):
    return math.degrees(2 * math.atan(math.exp(my / R)) - math.pi / 2)


def load(name):
    with open(os.path.join(LOCAL, name), encoding="utf-8") as f:
        return json.load(f)["elements"]


def way_xy(geom):
    return np.array([merc(p["lat"], p["lon"]) for p in geom if p], dtype=float)


# ---------------------------------------------------------------- site model
def read_model():
    m = rhino3dm.File3dm.Read(SITE3DM)
    lay = {i: l.FullPath for i, l in enumerate(m.Layers)}
    foot, names, lo, hi, site = {}, [], np.array([1e18] * 3), np.array([-1e18] * 3), None
    for o in m.Objects:
        lp = lay[o.Attributes.LayerIndex]
        g = o.Geometry
        if lp in CONTEXT_LAYERS:
            b = g.GetBoundingBox()
            lo = np.minimum(lo, [b.Min.X, b.Min.Y, b.Min.Z]); hi = np.maximum(hi, [b.Max.X, b.Max.Y, b.Max.Z])
        if lp == "buildings" and isinstance(g, rhino3dm.Extrusion):
            n = (o.Attributes.Name or "").strip()
            c = g.Profile3d(0, 0.0)
            if n.isdigit() and isinstance(c, rhino3dm.PolylineCurve):
                pts = np.array([[c.Point(i).X, c.Point(i).Y] for i in range(c.PointCount)])
                names.append(n)
                foot[n] = pts[:-1] if np.allclose(pts[0], pts[-1]) else pts
        if lp == "Site":
            pts = [g.SegmentCurve(i).PointAtStart for i in range(g.SegmentCount)]
            site = np.array([[p.X, p.Y] for p in pts])
    dup = {n for n in names if names.count(n) > 1}
    for n in dup:
        foot.pop(n, None)   # ids used by more than one extrusion are ambiguous; left out of the fit
    return foot, dup, lo, hi, site


# ---------------------------------------------------------------- similarity fit (complex Umeyama + ICP)
def fit(w, z):
    wm, zm = w.mean(), z.mean()
    a = np.sum((z - zm) * np.conj(w - wm)) / np.sum(np.abs(w - wm) ** 2)
    return a, zm - a * wm


def register(foot, osm):
    ids = sorted(set(foot) & set(osm))
    W = {i: foot[i][:, 0] + 1j * foot[i][:, 1] for i in ids}
    Z = {i: osm[i][:, 0] + 1j * osm[i][:, 1] for i in ids}
    a, t = fit(np.array([W[i].mean() for i in ids]), np.array([Z[i].mean() for i in ids]))
    keep = list(ids)
    for it in range(12):
        ws, zs, per = [], [], {}
        for i in ids:
            p = a * W[i] + t
            d = np.abs(p[:, None] - Z[i][None, :])
            j = d.argmin(axis=1)
            per[i] = float(np.sqrt(np.mean(d[np.arange(len(j)), j] ** 2)))
            if i in keep:
                ws.append(W[i]); zs.append(Z[i][j])
        a, t = fit(np.concatenate(ws), np.concatenate(zs))
        med = float(np.median(list(per.values())))
        keep = [i for i in ids if per[i] <= max(3.0, 3 * med)]   # trim buildings edited in OSM since the model
    ws = np.concatenate([W[i] for i in keep])
    zs = []
    for i in keep:
        p = a * W[i] + t
        d = np.abs(p[:, None] - Z[i][None, :])
        zs.append(Z[i][d.argmin(axis=1)])
    zs = np.concatenate(zs)
    res = np.abs(a * ws + t - zs)
    return a, t, ids, keep, per, float(np.sqrt(np.mean(res ** 2))), len(ws)


# ---------------------------------------------------------------- geometry helpers
def dp(pts, tol):
    if len(pts) < 3 or tol <= 0:
        return pts
    keep = np.zeros(len(pts), bool); keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        s, e = stack.pop()
        if e <= s + 1:
            continue
        a, b = pts[s], pts[e]
        ab = b - a; L = math.hypot(*ab)
        seg = pts[s + 1:e]
        if L == 0:
            d = np.hypot(*(seg - a).T)
        else:
            d = np.abs(ab[0] * (seg[:, 1] - a[1]) - ab[1] * (seg[:, 0] - a[0])) / L
        k = int(d.argmax())
        if d[k] > tol:
            keep[s + 1 + k] = True
            stack += [(s, s + 1 + k), (s + 1 + k, e)]
    return pts[keep]


def chain(ways):
    """Join OSM ways (node-id lists + coords) end to end; returns list of (coords, closed)."""
    segs = [(list(w["nodes"]), list(map(tuple, way_xy(w["geometry"])))) for w in ways]
    out = []
    while segs:
        n, c = segs.pop()
        grown = True
        while grown and n[0] != n[-1]:
            grown = False
            for k, (n2, c2) in enumerate(segs):
                if n2[0] == n[-1]:
                    n += n2[1:]; c += c2[1:]
                elif n2[-1] == n[-1]:
                    n += n2[::-1][1:]; c += c2[::-1][1:]
                elif n2[-1] == n[0]:
                    n = n2 + n[1:]; c = c2 + c[1:]
                elif n2[0] == n[0]:
                    n = n2[::-1] + n[1:]; c = c2[::-1] + c[1:]
                else:
                    continue
                segs.pop(k); grown = True
                break
        out.append((np.array(c), n[0] == n[-1]))
    return out


def rings_of_relation(rel, role="outer"):
    ws = [{"nodes": [("%.7f,%.7f" % (g["lat"], g["lon"])) for g in m["geometry"]], "geometry": m["geometry"]}
          for m in rel.get("members", []) if m.get("type") == "way" and m.get("role") == role and m.get("geometry")]
    return [c for c, closed in chain(ws) if closed]


def clip_box(box):
    x0, y0, x1, y1 = box   # mercator, y north

    def inside(p):
        return x0 <= p[0] <= x1 and y0 <= p[1] <= y1

    def cross(p, q):
        # Liang-Barsky parametric clip of segment p->q; returns (t0, t1) or None
        t0, t1 = 0.0, 1.0
        dx, dy = q[0] - p[0], q[1] - p[1]
        for pp, qq in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
            if pp == 0:
                if qq < 0:
                    return None
            else:
                r = qq / pp
                if pp < 0:
                    t0 = max(t0, r)
                else:
                    t1 = min(t1, r)
        return (t0, t1) if t0 <= t1 else None
    return inside, cross


def clip_line(pts, box):
    """Clip an open polyline to the box; returns inside pieces (each starts/ends on the border unless the line does)."""
    inside, cross = clip_box(box)
    pieces, cur = [], []
    for p, q in zip(pts[:-1], pts[1:]):
        c = cross(p, q)
        if c is None:
            if cur:
                pieces.append(np.array(cur)); cur = []
            continue
        a = p + (q - p) * c[0]; b = p + (q - p) * c[1]
        if not cur:
            cur = [a]
        cur.append(b)
        if c[1] < 1.0:
            pieces.append(np.array(cur)); cur = []
    if cur:
        pieces.append(np.array(cur))
    return [p for p in pieces if len(p) > 1]


def coast_polygons(coast_chains, box):
    """Water polygons from coastline chains (water on the right of the way direction), closed clockwise along the box."""
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    P = 2 * (W + H)

    def tpos(p):   # clockwise perimeter parameter from the NW corner (y north)
        x, y = p
        e = 1e-6 * P
        if abs(y - y1) < e: return (x - x0)
        if abs(x - x1) < e: return W + (y1 - y)
        if abs(y - y0) < e: return W + H + (x1 - x)
        return 2 * W + H + (y - y0)
    corners = [(0.0, (x0, y1)), (W, (x1, y1)), (W + H, (x1, y0)), (2 * W + H, (x0, y0))]
    pieces, islands = [], []
    for c, closed in coast_chains:
        if closed:
            if clip_box(box)[0](c[0]):
                islands.append(c)
            continue
        pieces += clip_line(c, box)
    if not pieces:
        return [], islands
    used = [False] * len(pieces)
    rings = []
    for s in range(len(pieces)):
        if used[s]:
            continue
        ring, k = [], s
        while not used[k]:
            used[k] = True
            ring += list(map(tuple, pieces[k]))
            te = tpos(pieces[k][-1])
            best, bd = None, None
            for j, pc in enumerate(pieces):
                d = (tpos(pc[0]) - te) % P
                if bd is None or d < bd:
                    best, bd = j, d
            for tc, cc in sorted(corners, key=lambda tc: (tc[0] - te) % P):
                if 0 < (tc - te) % P < bd:
                    ring.append(cc)
            k = best
        rings.append(np.array(ring))
    return rings, islands


# ---------------------------------------------------------------- SVG
class Frame:
    def __init__(self, ox, oy):
        self.ox, self.oy = ox, oy

    def m2s(self, pts):
        pts = np.asarray(pts, float)
        return np.column_stack([pts[:, 0] - self.ox, self.oy - pts[:, 1]])


def path_d(polys, nd, closed=False):
    out = []
    f = 10 ** nd
    for p in polys:
        q = np.round(np.asarray(p) * f).astype(np.int64)
        if len(q) < 2:
            continue
        d = np.diff(q, axis=0)
        keep = np.any(d != 0, axis=1)
        d = d[keep]
        if len(d) == 0:
            continue
        def fmt(v):   # v is an integer in units of 10^-nd m
            v = int(v)
            if v < 0:
                return "-" + fmt(-v)
            if nd == 0 or v % f == 0:
                return str(v // f)
            return ("%d.%0*d" % (v // f, nd, v % f)).rstrip("0")
        s = "M%s %s" % (fmt(q[0][0]), fmt(q[0][1])) + "l" + " ".join("%s %s" % (fmt(a), fmt(b)) for a, b in d)
        out.append(s + ("z" if closed else ""))
    return "".join(out)


def stroke_path(pid, polys, colour, nd, width=1, extra=""):
    d = path_d(polys, nd)
    if not d:
        return ""
    return ('<path id="%s" d="%s" fill="none" stroke="%s" stroke-width="%g" vector-effect="non-scaling-stroke" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (pid, d, colour, width, extra))


def fill_path(pid, polys, colour, nd, rule="evenodd"):
    d = path_d(polys, nd, closed=True)
    if not d:
        return ""
    return '<path id="%s" d="%s" fill="%s" fill-rule="%s" stroke="none"/>' % (pid, d, colour, rule)


def svg_doc(vb, groups, title):
    x, y, w, h = vb
    px = max(w / 1920.0, h / 1080.0)          # metres per CSS px when the SVG fills 1920 x 1080 (meet)
    fs = 11 * px
    ax, ay = x + w / 2 + 960 * px - 24 * px, y + h / 2 + 540 * px - 20 * px
    ax, ay = min(ax, x + w - 4 * px), min(ay, y + h - 4 * px)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.1f %.1f %.1f %.1f" preserveAspectRatio="xMidYMid meet" '
            'data-units="web-mercator-metres" data-mpp-1920="%.4f">\n<title>%s</title>\n<g id="map">\n%s\n</g>\n'
            '<text id="attribution" x="%.1f" y="%.1f" text-anchor="end" font-family="%s" font-size="%.2f" fill="%s">%s</text>\n'
            '</svg>\n' % (x, y, w, h, px, title, "\n".join(groups), ax, ay, MONO, fs, INK, ATTRIB))


def main():
    foot, dup, lo, hi, site = read_model()
    osm_site = {}
    for e in load("osm_site.json"):
        if e["type"] == "way":
            xy = way_xy(e["geometry"])
            osm_site[str(e["id"])] = xy[:-1] if np.allclose(xy[0], xy[-1]) else xy
    a, t, ids, keep, per, rms, npts = register(foot, osm_site)
    scale, rot = abs(a), math.degrees(cmath.phase(a))
    lat_site = inv_lat((a * complex(*site.mean(axis=0)) + t).imag)
    expect = FT / math.cos(math.radians(41.88))
    print("matched %d (fit %d buildings, %d vertices) rms %.3f m merc (%.3f m ground)  scale %.5f expect %.5f (%.2f %%)  rot %.3f deg"
          % (len(ids), len(keep), npts, rms, rms * math.cos(math.radians(lat_site)), scale, expect,
             100 * (scale / expect - 1), rot))

    def M(pts):   # model ft (x, y) -> mercator m (x, y north)
        z = a * (pts[:, 0] + 1j * pts[:, 1]) + t
        return np.column_stack([z.real, z.imag])
    ox, oy = round(t.real), round(t.imag)
    F = Frame(ox, oy)
    ext_ft = np.array([[lo[0], lo[1]], [hi[0], lo[1]], [hi[0], hi[1]], [lo[0], hi[1]]])
    ext_m = M(ext_ft)
    site_m = M(site)

    # ---- corridor data
    cor = load("osm_corridor.json")
    ways = [e for e in cor if e["type"] == "way"]
    rels = [e for e in cor if e["type"] == "relation"]
    rnd = [w for w in ways if "Randolph Street" in w.get("tags", {}).get("name", "")
           and w["tags"].get("highway") and w["tags"]["highway"] not in PED]
    mich = [w for w in ways if "Michigan Avenue" in w.get("tags", {}).get("name", "")
            and w["tags"].get("highway") and w["tags"]["highway"] not in PED]
    segs = []
    for w in rnd:
        p = way_xy(w["geometry"])
        segs += list(zip(p[:-1], p[1:]))
    yr = np.median([s[0][1] for s in segs])
    # Michigan Ave crossing x
    xs = []
    for w in mich:
        p = way_xy(w["geometry"])
        for u, v in zip(p[:-1], p[1:]):
            if (u[1] - yr) * (v[1] - yr) <= 0 and u[1] != v[1]:
                xs.append(u[0] + (yr - u[1]) / (v[1] - u[1]) * (v[0] - u[0]))
    x_mich = float(np.median(xs))
    # site-model west edge crossing at Randolph's y
    xw = []
    for u, v in zip(ext_m, np.roll(ext_m, -1, axis=0)):
        if (u[1] - yr) * (v[1] - yr) <= 0 and u[1] != v[1]:
            xw.append(u[0] + (yr - u[1]) / (v[1] - u[1]) * (v[0] - u[0]))
    x_west = min(xw)
    # centreline: mean y of all Randolph carriageways at each x
    cl = []
    for x in np.arange(x_mich, x_west, -10.0).tolist() + [x_west]:
        ys = [u[1] + (x - u[0]) / (v[0] - u[0]) * (v[1] - u[1]) for u, v in segs
              if (u[0] - x) * (v[0] - x) <= 0 and abs(v[1] - u[1]) < 0.2 * abs(v[0] - u[0]) and abs(u[1] - yr) < 60]
        if ys:   # carriageways only (east-west segments), median against ramps
            cl.append((x, float(np.median(ys))))
    cl = dp(np.array(cl), 0.5)
    ground = lambda p, q: math.hypot(*(q - p)) * math.cos(math.radians(inv_lat((p[1] + q[1]) / 2)))
    L = sum(ground(p, q) for p, q in zip(cl[:-1], cl[1:]))
    sx = float(site_m[:, 0].mean())
    L_site = sum(ground(p, q) * (1 if q[0] >= sx else max(0.0, (p[0] - sx) / (p[0] - q[0])))
                 for p, q in zip(cl[:-1], cl[1:]) if p[0] > sx)
    miles = L / 1609.344
    print("Randolph: michigan x %.1f, west edge x %.1f, %d pts, %.1f m = %.3f mi (to site centre %.3f mi)"
          % (x_mich, x_west, len(cl), L, miles, L_site / 1609.344))

    corridor_g = '<g id="corridor">%s</g>' % stroke_path("randolph", [F.m2s(cl)], ACCENT, 1, 3, ' pathLength="1000"')
    sitebox_g = ('<g id="sitebox">%s%s</g>' % (
        '<path id="site-extent" d="%s" fill="none" stroke="%s" stroke-width="1" vector-effect="non-scaling-stroke"/>'
        % (path_d([F.m2s(ext_m)], 1, True), INK),
        fill_path("site", [F.m2s(site_m)], INK, 1)))

    # ---- corridor SVG
    bx = merc(CORRIDOR[0], CORRIDOR[1]) + merc(CORRIDOR[2], CORRIDOR[3])
    cbox = (bx[0], bx[1], bx[2], bx[3])
    bld, bld_rel, water, major, minor, rail = [], [], [], [], [], []
    for w in ways:
        tg = w.get("tags", {})
        p = way_xy(w["geometry"])
        if len(p) < 2:
            continue
        closed = w["nodes"][0] == w["nodes"][-1]
        if "building" in tg and closed:
            bld.append(F.m2s(dp(p, 0.3)))
        elif tg.get("natural") == "water" and closed:
            water.append(F.m2s(dp(p, 0.5)))
        elif tg.get("railway") == "rail":
            rail += [F.m2s(dp(q, 0.5)) for q in clip_line(p, cbox)]
        elif "highway" in tg and tg["highway"] not in PED:
            tgt = major if tg["highway"] in MAJOR else minor
            tgt += [F.m2s(dp(q, 0.5)) for q in clip_line(p, cbox)]
    for r in rels:
        tg = r.get("tags", {})
        rings = [F.m2s(dp(c, 0.5)) for c in rings_of_relation(r, "outer") + rings_of_relation(r, "inner")]
        if "building" in tg:
            bld_rel += rings
        elif tg.get("natural") == "water":
            water += rings
    cx0, cy1 = F.m2s([[bx[0], bx[1]]])[0]
    cx1, cy0 = F.m2s([[bx[2], bx[3]]])[0]
    vb_c = (cx0, cy0, cx1 - cx0, cy1 - cy0)
    rest_c = ('<g id="rest">' + fill_path("water", water, PALE_WATER, 1) + fill_path("buildings", bld, PALE_BLDG, 1, "nonzero")
              + fill_path("buildings-mp", bld_rel, PALE_BLDG, 1) + stroke_path("streets-minor", minor, HAIR_LIGHT, 1)
              + stroke_path("streets-major", major, HAIR_DARK, 1) + stroke_path("rail", rail, HAIR_DARK, 1) + "</g>")
    svg_c = svg_doc(vb_c, [rest_c, corridor_g, sitebox_g], "Randolph St corridor, Michigan Ave to the West Loop")
    with open(os.path.join(REPO, "assets", "map-corridor.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(svg_c)

    # ---- city SVG
    city = load("osm_city.json")
    bx2 = merc(CITY[0], CITY[1]) + merc(CITY[2], CITY[3])
    box2 = (bx2[0], bx2[1], bx2[2], bx2[3])
    coast = [e for e in city if e["type"] == "way" and e.get("tags", {}).get("natural") == "coastline"]
    coast_chains = chain(coast)
    for e in city:   # Lake Michigan: outer member ways (geometry clipped to the bbox, nulls outside) as shore chains
        if e["type"] == "relation" and e.get("tags", {}).get("name") == "Lake Michigan":
            ws = []
            for mbr in e.get("members", []):
                if mbr.get("type") != "way" or mbr.get("role") != "outer" or not mbr.get("geometry"):
                    continue
                run = []
                for g in mbr["geometry"] + [None]:
                    if g:
                        run.append(g)
                    elif len(run) > 1:
                        ws.append({"nodes": ["%.7f,%.7f" % (q["lat"], q["lon"]) for q in run], "geometry": run}); run = []
                    else:
                        run = []
            for c, closed in chain(ws):
                if not closed and c[0][1] > c[-1][1]:
                    c = c[::-1]          # shore runs south -> north with the lake (east / north) on the right
                coast_chains.append((c, closed))
    lake_rings, islands = coast_polygons(coast_chains, box2)
    rwater, rlines, mot, pri, bnd = [], [], [], [], []
    for e in city:
        tg = e.get("tags", {})
        if e["type"] == "way":
            p = way_xy(e["geometry"])
            if len(p) < 2:
                continue
            if tg.get("natural") == "water" and e["nodes"][0] == e["nodes"][-1]:
                rwater.append(F.m2s(dp(p, 3)))
            elif tg.get("waterway") == "river":
                rlines += [F.m2s(dp(q, 8)) for q in clip_line(p, box2)]
            elif tg.get("highway") in ("motorway", "trunk"):
                mot += [F.m2s(dp(q, 8)) for q in clip_line(p, box2)]
            elif tg.get("highway") in ("primary", "secondary"):
                pri += [F.m2s(dp(q, 8)) for q in clip_line(p, box2)]
        elif e["type"] == "relation":
            if tg.get("boundary") == "administrative":
                for mbr in e.get("members", []):
                    if mbr.get("type") == "way" and mbr.get("geometry") and mbr.get("role") in ("outer", "inner", ""):
                        bnd.append(F.m2s(dp(way_xy(mbr["geometry"]), 4)))
            elif tg.get("natural") == "water" and tg.get("name") != "Lake Michigan":
                rwater += [F.m2s(dp(c, 3)) for c in rings_of_relation(e, "outer") + rings_of_relation(e, "inner")]
    lake = [F.m2s(dp(r, 6)) for r in lake_rings + islands]
    x0, y1 = F.m2s([[bx2[0], bx2[1]]])[0]
    x1, y0 = F.m2s([[bx2[2], bx2[3]]])[0]
    vb_city = (x0, y0, x1 - x0, y1 - y0)
    rest_city = ('<g id="rest">' + fill_path("lake", lake, PALE_WATER, 0) + fill_path("river", rwater, PALE_WATER, 0)
                 + stroke_path("river-line", rlines, PALE_WATER, 0, 2)
                 + stroke_path("roads-secondary", pri, HAIR_LIGHT, 0) + stroke_path("roads-major", mot, HAIR_DARK, 0)
                 + stroke_path("city-boundary", bnd, INK, 0) + "</g>")
    svg_city = svg_doc(vb_city, [rest_city, corridor_g, sitebox_g], "Chicago, city of")
    with open(os.path.join(REPO, "assets", "map-city.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(svg_city)
    print("lake rings %d islands %d, river polys %d, motorway %d, primary/secondary %d, boundary %d"
          % (len(lake_rings), len(islands), len(rwater), len(mot), len(pri), len(bnd)))
    print("buildings %d (+%d mp rings), water %d, major %d, minor %d, rail %d" % (len(bld), len(bld_rel), len(water), len(major), len(minor), len(rail)))

    # ---- site.json
    r2 = lambda v: round(float(v), 2)
    mapxy = lambda P: [[r2(x), r2(y)] for x, y in F.m2s(P)]
    A = a.real; B = a.imag
    site_json = {
        "version": "1.0",
        "source": "tools/render_map.py (S13); OSM via Overpass; Map data \u00a9 OpenStreetMap contributors",
        "siteModel": os.path.basename(SITE3DM),
        "units": {"model": "ft", "mercator": "Web Mercator (EPSG:3857) m", "map": "SVG map frame m"},
        "mercatorOrigin": [ox, oy],
        "mercatorOriginLatLon": [round(inv_lat(oy), 7), round(math.degrees(ox / R), 7)],
        "mapFrame": "x = mercX - mercatorOrigin[0], y = mercatorOrigin[1] - mercY (y down, as both SVG viewBoxes)",
        "transform": {
            "modelFtToMercator": [[A, -B, t.real], [B, A, t.imag]],
            "modelFtToMap": [[A, -B, t.real - ox], [-B, -A, oy - t.imag]],
            "scale": scale, "rotationDeg": rot,
            "expectedScale": expect, "scaleErrorPct": 100 * (scale / expect - 1),
            "rmsResidualMercM": rms, "rmsResidualGroundM": rms * math.cos(math.radians(lat_site)),
            "matchedBuildings": len(ids), "fitBuildings": len(keep), "fitVertices": npts,
            "trimmedIds": [i for i in ids if i not in keep], "ambiguousIds": sorted(dup),
        },
        "siteModelExtentFt": {"layers": list(CONTEXT_LAYERS), "min": [r2(v) for v in lo], "max": [r2(v) for v in hi]},
        "siteModelExtentMap": mapxy(ext_m),
        "sitePolygonFt": [[r2(x), r2(y)] for x, y in site],
        "sitePolygonMap": mapxy(site_m),
        "randolph": {"from": "Michigan Ave", "to": "site-model west edge", "centrelineMap": mapxy(cl),
                     "lengthM": round(L, 1), "miles": round(miles, 3), "toSiteCentreMiles": round(L_site / 1609.344, 3)},
        "corridorMiles": round(miles, 2),
        "viewBox": {"city": [r2(v) for v in vb_city], "corridor": [r2(v) for v in vb_c]},
        "attribution": ATTRIB,
    }
    with open(os.path.join(REPO, "data", "site.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(site_json, f, indent=2, ensure_ascii=False)
        f.write("\n")
    for n in ("map-city.svg", "map-corridor.svg"):
        print(n, os.path.getsize(os.path.join(REPO, "assets", n)), "bytes")


if __name__ == "__main__":
    main()
