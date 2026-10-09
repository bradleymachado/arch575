# build_site_glb_v1.1 — This section is intended to export the Rhino site model (read only, rhino3dm) as the
# web context GLB assets/site.glb (buildings minus the on-site footprints, TERRAIN_MESH, Bridges, roads, Site
# outline band; feet -> metres; root rotation as the tower GLB; one grey material per node) and to place the
# tower: fit the F_POD footprint onto the Site polycurve's rectangle, cross-check it against the podium outline
# in Randolph_Master_v1.1.3dm, and write towerOffset / towerYawDeg / removed ids / face counts to data/site.json.
# v1.1 (S17): the context is written as named feature nodes for the slide 02 loop. Buildings -> b_skybridge
# (OSM way 131998285), b_restaurantrow (footprint centroid within 40 m of the W Randolph St OSM centreline
# between N Halsted St and the model's west edge), buildings (rest). Streets -> r_randolph, r_halsted,
# r_washington: ribbon meshes built from the named OSM centrelines (W Randolph St, N+S Halsted St, W Washington
# Blvd/St; carriageway ways only, clipped to the model extent), offset to the full right-of-way width (Randolph
# 24 m, Halsted 24 m, Washington 20 m) with mitred joins, placed 0.4 m above the local road / terrain surface;
# the Roads render mesh stays whole as 'roads'. TERRAIN_MESH, Bridges, Site as before. Same geometry, units,
# root rotation and placement as v1.0. Centrelines from _local/osm_corridor.json (S13 cache) through the S13
# registration (data/site.json transform.modelFtToMercator, inverted). The feature list goes to data/site.json ->
# features; the loop's camera frame (Lake, Madison, Washington, Halsted, Kennedy lines, model ft) to -> siteLoop.
#
# Usage (repo root):  python tools/build_site_glb.py
# Never writes a .3dm. Earth (Google 3D Tiles), Setup::*, TPX_TERRAIN and Rail are never read into the GLB.

import json, math, os, struct, sys
import numpy as np
import rhino3dm

ROOT = r"C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575"
SITE3DM = os.path.join(ROOT, r"02_Site\Arch575_BlenderSite_RhinoModel_v2.0.3dm")
MASTER3DM = os.path.join(ROOT, r"03_Design\00_Master\Randolph_Master_v1.1.3dm")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_GLB = os.path.join(REPO, "assets", "site.glb")
SITE_JSON = os.path.join(REPO, "data", "site.json")

FT = 0.3048
ROOT_ROT = [-0.7071067811865476, 0.0, 0.0, 0.7071067811865476]   # z-up model -> y-up glTF (as tower.glb)
F_POD = (97.84079882, 63.39839761)                                # tower GLB x (N-S) x z (E-W), metres
BAND_FT = 1.0                                                     # Site outline band width
BAND_LIFT_FT = 0.5                                                # above the terrain under the band
EXCLUDE = ("Earth", "Setup", "TPX_TERRAIN", "Rail")
# S5 palette greys (tower.js GREYS), one per node (v1.1: feature nodes share their layer's grey)
GROUPS = [("b_skybridge", "#B5B5B5"), ("b_restaurantrow", "#B5B5B5"), ("buildings", "#B5B5B5"),
          ("TERRAIN_MESH", "#F2F2F0"), ("Bridges", "#D9D9D9"),
          ("r_randolph", "#E4E4E2"), ("r_halsted", "#E4E4E2"), ("r_washington", "#E4E4E2"), ("roads", "#E4E4E2"),
          ("Site", "#9A9A9A")]
OSM_CORRIDOR = os.path.join(REPO, "_local", "osm_corridor.json")
SKYBRIDGE_ID = "131998285"
RIBBON_WIDTH_M = {"r_randolph": 24.0, "r_halsted": 24.0, "r_washington": 20.0}   # full right-of-way
RIBBON_LIFT_M = 0.4         # above the local road / terrain surface
RIBBON_MAX_DIST_M = 12.0    # acceptance: every ribbon vertex within this distance of the centreline
CARRIAGEWAY = {"motorway", "trunk", "primary", "secondary", "tertiary"}   # ribbon ways (no frontage / service roads)
ROW_DIST_M = 40.0           # Restaurant Row: footprint centroid within this distance of the Randolph centreline
STREETS = {                 # feature node -> OSM way names (highway ways; pedestrian / cycle ways excluded)
    "r_randolph": ("West Randolph Street",),
    "r_halsted": ("North Halsted Street", "South Halsted Street"),
    "r_washington": ("West Washington Boulevard", "West Washington Street"),
}
FRAME_STREETS = {"lake": ("West Lake Street",), "madison": ("West Madison Street",),
                 "kennedy": ("Kennedy Expressway",)}
PED = {"footway", "path", "steps", "pedestrian", "cycleway", "corridor", "track", "bridleway", "elevator", "platform"}
R_EARTH = 6378137.0


def srgb_to_linear(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [1.0]


def mesh_arrays(m):
    """rhino3dm Mesh -> (V float64 n x 3 ft, F int n x 3); quads split into two triangles."""
    if m is None or len(m.Vertices) == 0:
        return None
    V = np.array([[p.X, p.Y, p.Z] for p in m.Vertices], dtype=np.float64)
    tris = []
    for i in range(len(m.Faces)):
        f = m.Faces[i]
        a, b, c, d = f[0], f[1], f[2], f[3]
        tris.append((a, b, c))
        if c != d:
            tris.append((a, c, d))
    return V, np.array(tris, dtype=np.int64)


def brep_meshes(g):
    out = []
    for i in range(len(g.Faces)):
        r = mesh_arrays(g.Faces[i].GetMesh(rhino3dm.MeshType.Render))
        if r:
            out.append(r)
    return out


def point_in_poly(p, poly):
    x, y = p
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def poly_centroid(P):
    x, y = P[:, 0], P[:, 1]; x1, y1 = np.roll(x, -1), np.roll(y, -1)
    cr = x * y1 - x1 * y
    a = cr.sum() / 2
    if abs(a) < 1e-9:
        return P.mean(0)
    return np.array([((x + x1) * cr).sum() / (6 * a), ((y + y1) * cr).sum() / (6 * a)])


def min_area_rect(P):
    """Oriented minimum-area rectangle over the polygon's edge directions -> (angle rad, centre, w, h)."""
    best = None
    for i in range(len(P)):
        e = P[(i + 1) % len(P)] - P[i]
        if np.hypot(*e) < 1.0:
            continue
        a = math.atan2(e[1], e[0]) % (math.pi / 2)
        R = np.array([[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]])
        Q = P @ R.T
        lo, hi = Q.min(0), Q.max(0)
        area = np.prod(hi - lo)
        if best is None or area < best[0]:
            c = R.T @ ((lo + hi) / 2)
            best = (area, a, c, hi - lo)
    return best[1], best[2], best[3][0], best[3][1]


def read_site():
    m = rhino3dm.File3dm.Read(SITE3DM)
    lay = {i: l.FullPath for i, l in enumerate(m.Layers)}
    parts = {g: [] for g, _ in GROUPS}
    bld = []            # (id, centroid xy, (V, F) list)
    site = None
    seen = {}
    for o in m.Objects:
        lp = lay[o.Attributes.LayerIndex]
        top = lp.split("::")[0]
        seen[lp] = seen.get(lp, 0) + 1
        if top in EXCLUDE:
            continue
        g = o.Geometry
        if lp == "buildings":
            name = (o.Attributes.Name or "").strip() or str(o.Attributes.Id)
            if isinstance(g, rhino3dm.Extrusion):
                ms = [mesh_arrays(g.GetMesh(rhino3dm.MeshType.Any))]
                c = g.Profile3d(0, 0.0)
                if isinstance(c, rhino3dm.PolylineCurve):
                    pts = np.array([[c.Point(i).X, c.Point(i).Y] for i in range(c.PointCount)])
                else:   # curved profile: sample it
                    t0, t1 = c.Domain.T0, c.Domain.T1
                    pts = np.array([[c.PointAt(t).X, c.PointAt(t).Y] for t in np.linspace(t0, t1, 65)])
                if np.allclose(pts[0], pts[-1]):
                    pts = pts[:-1]
                cen = poly_centroid(pts)
            else:
                ms = brep_meshes(g)
                b = g.GetBoundingBox(); cen = np.array([(b.Min.X + b.Max.X) / 2, (b.Min.Y + b.Max.Y) / 2])
            bld.append((name, cen, [x for x in ms if x]))
        elif lp == "TERRAIN_MESH" or lp == "Roads":
            key = "roads" if lp == "Roads" else lp
            parts[key] += brep_meshes(g) if isinstance(g, rhino3dm.Brep) else [mesh_arrays(g)]
        elif lp == "Bridges":
            r = mesh_arrays(g) if isinstance(g, rhino3dm.Mesh) else None
            if r:
                parts["Bridges"].append(r)
        elif lp == "Site":
            pts = [g.SegmentCurve(i).PointAtStart for i in range(g.SegmentCount)]
            site = np.array([[p.X, p.Y, p.Z] for p in pts])
    return parts, bld, site, seen


def terrain_z(parts, xy):
    V = np.vstack([v for v, _ in parts["TERRAIN_MESH"]])
    d = np.hypot(V[:, 0] - xy[0], V[:, 1] - xy[1])
    k = np.argsort(d)[:4]
    w = 1 / np.maximum(d[k], 1e-6)
    return float((V[k, 2] * w).sum() / w.sum())


def site_band(site, parts):
    """1 ft flat band centred on the Site outline, lifted 0.5 ft above the terrain under each vertex."""
    P = site[:, :2]; n = len(P)
    V, F = [], []
    for i in range(n):
        a, b = P[i], P[(i + 1) % n]
        e = b - a; L = np.hypot(*e)
        if L < 1e-6:
            continue
        nrm = np.array([-e[1], e[0]]) / L * BAND_FT / 2
        za = terrain_z(parts, a) + BAND_LIFT_FT; zb = terrain_z(parts, b) + BAND_LIFT_FT
        k = len(V)
        V += [[*(a - nrm), za], [*(a + nrm), za], [*(b + nrm), zb], [*(b - nrm), zb]]
        F += [(k, k + 2, k + 1), (k, k + 3, k + 2)]
    return np.array(V), np.array(F)


def merge(ms):
    Vs, Fs, off = [], [], 0
    for V, F in ms:
        Vs.append(V); Fs.append(F + off); off += len(V)
    return np.vstack(Vs), np.vstack(Fs)


def write_glb(groups, path):
    js = {"asset": {"version": "2.0", "generator": "build_site_glb_v1.1 (rhino3dm + numpy)"},
          "scene": 0, "scenes": [{"nodes": [0]}],
          "nodes": [{"name": "site", "rotation": ROOT_ROT, "children": list(range(1, len(groups) + 1))}],
          "meshes": [], "materials": [], "accessors": [], "bufferViews": [], "buffers": []}
    blob = bytearray()

    def view(data, target):
        while len(blob) % 4:
            blob.append(0)
        off = len(blob); blob.extend(data)
        js["bufferViews"].append({"buffer": 0, "byteOffset": off, "byteLength": len(data), "target": target})
        return len(js["bufferViews"]) - 1

    for gi, (name, colour, V, F) in enumerate(groups):
        Vm = (V * FT).astype(np.float32)
        I = F.astype(np.uint32).ravel()
        pv = view(Vm.tobytes(), 34962); iv = view(I.tobytes(), 34963)
        js["accessors"].append({"bufferView": pv, "componentType": 5126, "count": len(Vm), "type": "VEC3",
                                "min": Vm.min(0).tolist(), "max": Vm.max(0).tolist()})
        js["accessors"].append({"bufferView": iv, "componentType": 5125, "count": len(I), "type": "SCALAR"})
        js["materials"].append({"name": f"{name}_grey", "doubleSided": True,
                                "pbrMetallicRoughness": {"baseColorFactor": srgb_to_linear(colour),
                                                         "metallicFactor": 0.0, "roughnessFactor": 0.95}})
        js["meshes"].append({"name": name, "primitives": [{"attributes": {"POSITION": 2 * gi},
                                                           "indices": 2 * gi + 1, "material": gi}]})
        js["nodes"].append({"name": name, "mesh": gi})
    while len(blob) % 4:
        blob.append(0)
    js["buffers"].append({"byteLength": len(blob)})
    jb = json.dumps(js, separators=(",", ":")).encode()
    jb += b" " * ((4 - len(jb) % 4) % 4)
    total = 12 + 8 + len(jb) + 8 + len(blob)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(jb), 0x4E4F534A)); f.write(jb)
        f.write(struct.pack("<II", len(blob), 0x004E4942)); f.write(blob)
    return total


def model_to_scene(xy, z=0.0):
    """Model ft (x east, y north, z up) -> site.glb scene metres after the root rotation (x, y up, z = -north)."""
    return np.array([xy[0] * FT, z * FT, -xy[1] * FT])


def place_tower(site, parts):
    """F_POD (GLB x 0..97.84 N-S with x = 0 at the north end, z 0..63.40 with z = 0 at the east face) centred on
    the Site polycurve's minimum-area rectangle; yaw follows the rectangle's long side."""
    P = site[:, :2]
    ang, cen, w, h = min_area_rect(P)
    # long axis of the rectangle (N-S) as a model-plane unit vector pointing north
    ax = np.array([math.cos(ang), math.sin(ang)]); ay = np.array([-math.sin(ang), math.cos(ang)])
    north = ax if abs(ax[1]) > abs(ay[1]) else ay
    if north[1] < 0:
        north = -north
    long_ft, short_ft = max(w, h), min(w, h)
    south_scene = np.array([-north[0], 0.0, north[1]])        # model (-n) -> scene (x, -y)
    yaw = math.atan2(-south_scene[2], south_scene[0])           # three.js rotation.y: x-axis -> (cos, 0, -sin)
    c, s = math.cos(yaw), math.sin(yaw)
    Ry = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    gz = terrain_z(parts, cen)
    centre_scene = model_to_scene(cen, gz)
    offset = centre_scene - Ry @ np.array([F_POD[0] / 2, 0.0, F_POD[1] / 2])
    corners_t = np.array([[0, 0, 0], [F_POD[0], 0, 0], [F_POD[0], 0, F_POD[1]], [0, 0, F_POD[1]]])
    corners_scene = corners_t @ Ry.T + offset
    corners_model = np.c_[corners_scene[:, 0] / FT, -corners_scene[:, 2] / FT]
    return dict(yawDeg=math.degrees(yaw), offset=offset, Ry=Ry, cornersModelFt=corners_model,
                rectFt=(long_ft, short_ft), rectCentreFt=cen, rectAngleDeg=math.degrees(ang), groundFt=gz)


def seg_dist(p, a, b):
    ab = b - a; t = np.clip(np.dot(p - a, ab) / max(np.dot(ab, ab), 1e-12), 0, 1)
    return float(np.hypot(*(p - (a + t * ab))))


def edge_to_poly(a, b, poly, n=21):
    """max over samples on edge ab of the distance to the polygon boundary (ft)."""
    best = 0.0
    for t in np.linspace(0, 1, n):
        p = a + t * (b - a)
        best = max(best, min(seg_dist(p, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))))
    return best


def podium_crosscheck(place):
    """Podium outline (00_REF::PODIUM, PODIUM_SITE_LINE_SCHEME4, local copy at z = 66 ft and site copy at z = 0)
    from the master model. The master has no shared frame with the site model, so the outline is brought into
    the tower frame by the same rule as the placement (bbox centred on F_POD, x = 0 at the north end, z = 0 east)
    and each F_POD edge is measured to the nearest outline segment."""
    m = rhino3dm.File3dm.Read(MASTER3DM)
    lay = {i: l.FullPath for i, l in enumerate(m.Layers)}
    out = {}
    for o in m.Objects:
        if lay[o.Attributes.LayerIndex] != "00_REF::PODIUM":
            continue
        c = o.Geometry
        pts = np.array([[c.Point(i).X, c.Point(i).Y, c.Point(i).Z] for i in range(c.PointCount)])
        if pts[0, 2] != 0.0:
            continue                       # take the site copy (z = 0); the local copy is identical in plan
        out[o.Attributes.Name] = pts[:-1, :2] if np.allclose(pts[0], pts[-1]) else pts[:, :2]
    res = {}
    for name, P in out.items():
        lo, hi = P.min(0), P.max(0)
        # tower frame (m): tx = (north - y) * FT, tz = (east - x) * FT, then centre on F_POD
        T = np.c_[(hi[1] - P[:, 1]) * FT, (hi[0] - P[:, 0]) * FT]
        T += np.array([F_POD[0], F_POD[1]]) / 2 - (T.min(0) + T.max(0)) / 2
        R = np.array([[0, 0], [F_POD[0], 0], [F_POD[0], F_POD[1]], [0, F_POD[1]]])
        d = [edge_to_poly(R[i], R[(i + 1) % 4], T) for i in range(4)]
        # outer (bounding) edges of the L outline vs the F_POD rectangle edges, centred
        dx = abs(F_POD[0] - (hi[1] - lo[1]) * FT) / 2; dz = abs(F_POD[1] - (hi[0] - lo[0]) * FT) / 2
        res[name] = dict(sizeFt=[round(float(hi[0] - lo[0]), 2), round(float(hi[1] - lo[1]), 2)],
                         outerEdgeDistM={"north": round(dx, 3), "south": round(dx, 3),
                                         "east": round(dz, 3), "west": round(dz, 3)},
                         edgeMaxDistM={"north": round(d[3], 3), "south": round(d[1], 3),
                                       "east": round(d[0], 3), "west": round(d[2], 3)})
    return res


def merc(lat, lon):
    return (R_EARTH * math.radians(lon), R_EARTH * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)))


def osm_streets(site_json):
    """OSM highway ways by name from the S13 corridor cache -> model ft polylines (list of n x 2 arrays) per key,
    plus the way ids. Mercator -> model ft through the inverse of transform.modelFtToMercator."""
    A = np.array(site_json["transform"]["modelFtToMercator"], dtype=float)   # 2 x 3
    M, t = A[:, :2], A[:, 2]
    Minv = np.linalg.inv(M)
    els = json.load(open(OSM_CORRIDOR, encoding="utf-8"))
    els = els.get("elements", els)
    want = {}
    for key, names in {**STREETS, **FRAME_STREETS}.items():
        for n in names:
            want.setdefault(n, []).append(key)
    keys = list(STREETS) + list(FRAME_STREETS)
    lines, ids = {k: [] for k in keys}, {k: [] for k in keys}
    hwy = osm_streets.highway = {}
    for e in els:
        if e.get("type") != "way":
            continue
        tags = e.get("tags") or {}
        name, hw = tags.get("name"), tags.get("highway")
        if name not in want or not hw or hw in PED:
            continue
        geom = e.get("geometry") or []
        if len(geom) < 2:
            continue
        P = np.array([merc(p["lat"], p["lon"]) for p in geom if p], dtype=float)
        Q = (P - t) @ Minv.T                      # model ft
        for key in want[name]:
            lines[key].append(Q); ids[key].append(str(e["id"]))
            hwy.setdefault(key, []).append(hw)
    return lines, ids


def dist_to_lines(P, lines):
    """min distance (ft) from each point in P (n x 2) to a list of polylines (segments), vectorised."""
    best = np.full(len(P), np.inf)
    for L in lines:
        for i in range(len(L) - 1):
            a, b = L[i], L[i + 1]
            ab = b - a; ab2 = float(ab @ ab)
            if ab2 < 1e-9:
                d = np.hypot(*(P - a).T)
            else:
                tt = np.clip(((P - a) @ ab) / ab2, 0, 1)
                proj = a + tt[:, None] * ab
                d = np.hypot(*(P - proj).T)
            best = np.minimum(best, d)
    return best


def clip_polyline(P, box):
    """Clip a polyline (n x 2) to the box (x0, y0, x1, y1) -> list of polylines (Liang-Barsky per segment)."""
    x0, y0, x1, y1 = box
    out, cur = [], []
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]
        d = b - a; t0, t1 = 0.0, 1.0; ok = True
        for pp, qq in ((-d[0], a[0] - x0), (d[0], x1 - a[0]), (-d[1], a[1] - y0), (d[1], y1 - a[1])):
            if abs(pp) < 1e-12:
                if qq < 0: ok = False; break
            else:
                r = qq / pp
                if pp < 0: t0 = max(t0, r)
                else: t1 = min(t1, r)
        if not ok or t0 > t1:
            if cur: out.append(np.array(cur)); cur = []
            continue
        pa, pb = a + t0 * d, a + t1 * d
        if not cur or np.hypot(*(cur[-1] - pa)) > 1e-6:
            if cur: out.append(np.array(cur))
            cur = [pa]
        cur.append(pb)
    if cur: out.append(np.array(cur))
    return [c for c in out if len(c) >= 2]


def surface_z(parts, xy):
    """Local road / terrain surface height (ft): inverse-distance of the 6 nearest Roads render-mesh vertices
    (falls back to the terrain when none within 60 ft)."""
    V = surface_z.V
    d = np.hypot(V[:, 0] - xy[0], V[:, 1] - xy[1])
    k = np.argsort(d)[:6]
    if d[k[0]] > 60.0:
        return terrain_z(parts, xy)
    w = 1 / np.maximum(d[k], 1e-6)
    return float((V[k, 2] * w).sum() / w.sum())


def ribbon(P, half_ft, parts):
    """Polyline (n x 2 ft) -> strip of width 2 x half_ft with mitred joins (mitre limited to 1.5 x half);
    z = local surface + RIBBON_LIFT. Returns (V, F)."""
    P = P[np.r_[True, np.hypot(*(np.diff(P, axis=0)).T) > 0.5]]   # drop repeated points
    if len(P) < 2:
        return None
    segs = np.diff(P, axis=0); segs /= np.hypot(*segs.T)[:, None]
    nrm = np.c_[-segs[:, 1], segs[:, 0]]                         # left normals
    L, R = [], []
    for i in range(len(P)):
        if i == 0: n = nrm[0]; s = 1.0
        elif i == len(P) - 1: n = nrm[-1]; s = 1.0
        else:
            m = nrm[i - 1] + nrm[i]; ml = np.hypot(*m)
            if ml < 1e-6: n = nrm[i]; s = 1.0
            else:
                n = m / ml; cos_half = float(n @ nrm[i]); s = min(1.0 / max(cos_half, 1e-3), 1.5)
        z = surface_z(parts, P[i]) + RIBBON_LIFT_M / FT
        L.append([*(P[i] + n * half_ft * s), z]); R.append([*(P[i] - n * half_ft * s), z])
    V = np.array([v for pair in zip(L, R) for v in pair])
    F = []
    for i in range(len(P) - 1):
        a, b, c, d = 2 * i, 2 * i + 1, 2 * i + 2, 2 * i + 3
        F += [(a, b, c), (b, d, c)]
    return V, np.array(F)


def street_ribbons(parts, lines, box):
    """One ribbon mesh per street from its carriageway ways clipped to the model extent."""
    surface_z.V = np.vstack([v for v, _ in parts["roads"]])
    hw = osm_streets.highway
    out, stats = {}, {}
    for key, width in RIBBON_WIDTH_M.items():
        half_ft = width / 2 / FT
        ms, used, cl = [], 0, []
        for P, h in zip(lines[key], hw.get(key, [])):
            if h not in CARRIAGEWAY:
                continue
            for Q in clip_polyline(P, box):
                r = ribbon(Q, half_ft, parts)
                if r: ms.append(r); used += 1; cl.append(Q)
        if ms:
            V, F = merge(ms)
            out[key] = [(V, F)]
            dmax = float(dist_to_lines(V[:, :2], cl).max() * FT)
            stats[key] = {"ways": used, "widthM": width, "maxVertexDistM": round(dmax, 3),
                          "lengthM": round(sum(float(np.hypot(*np.diff(Q, axis=0).T).sum()) for Q in cl) * FT, 1)}
    return out, stats


def compact(V, F):
    """Drop unreferenced vertices (after a face split)."""
    used, inv = np.unique(F, return_inverse=True)
    return V[used], inv.reshape(F.shape)


def frame_lines(lines, ext_ft):
    """Camera frame for the slide 02 loop, model ft: Halsted x at Randolph, Lake / Madison y near the site,
    the model's west / east edge (from the exported extent)."""
    def median_near(key, axis, other_axis_value, span=800.0):
        pts = np.vstack(lines[key]) if lines[key] else np.zeros((0, 2))
        if not len(pts):
            return None
        sel = np.abs(pts[:, 1 - axis] - other_axis_value) < span
        return float(np.median(pts[sel, axis])) if sel.any() else float(np.median(pts[:, axis]))
    randolph_y = median_near("r_randolph", 1, 1400.0)            # Randolph y near the site (x ~ 1400)
    halsted_x = median_near("r_halsted", 0, randolph_y)           # Halsted x near Randolph
    return {"randolphY": randolph_y, "halstedX": halsted_x,
            "washingtonY": median_near("r_washington", 1, 1400.0),
            "lakeY": median_near("lake", 1, 1200.0), "madisonY": median_near("madison", 1, 1200.0),
            "kennedyX": median_near("kennedy", 0, randolph_y, span=400.0),   # both carriageways near Randolph
            "westEdgeX": ext_ft[0][0], "eastEdgeX": ext_ft[1][0]}


def main():
    parts, bld, site, seen = read_site()
    poly = site[:, :2]
    removed, keep = [], []
    for name, cen, ms in bld:
        (removed if point_in_poly(cen, poly) else keep).append((name, ms))
    d = json.load(open(SITE_JSON, encoding="utf-8"))
    lines, way_ids = osm_streets(d)
    # the model's west edge from the exported geometry (buildings, terrain, bridges, roads), as v1.0's extent
    pre_ext = np.vstack([V for _, ms in keep for V, _ in ms] + [V for k in ("TERRAIN_MESH", "Bridges", "roads") for V, _ in parts[k]])
    ext_ft = [pre_ext.min(0).round(2).tolist(), pre_ext.max(0).round(2).tolist()]
    frame = frame_lines(lines, ext_ft)
    # buildings -> b_skybridge / b_restaurantrow / buildings
    cens = {name: cen for name, cen, _ in bld}
    b_nodes = {"b_skybridge": [], "b_restaurantrow": [], "buildings": []}
    b_ids = {"b_skybridge": [], "b_restaurantrow": [], "buildings": []}
    row_d = dist_to_lines(np.array([cens[n] for n, _ in keep]), lines["r_randolph"]) * FT
    for (name, ms), dd in zip(keep, row_d):
        cx = cens[name][0]
        if name == SKYBRIDGE_ID:
            node = "b_skybridge"
        elif dd <= ROW_DIST_M and ext_ft[0][0] - 1.0 <= cx <= frame["halstedX"]:
            node = "b_restaurantrow"
        else:
            node = "buildings"
        b_nodes[node] += ms; b_ids[node].append(name)
    for k in b_nodes:
        parts[k] = b_nodes[k]
    # streets -> ribbon meshes r_randolph / r_halsted / r_washington; the Roads mesh stays whole as 'roads'
    box = (ext_ft[0][0], ext_ft[0][1], ext_ft[1][0], ext_ft[1][1])
    ribbons, ribbon_stats = street_ribbons(parts, lines, box)
    for k in ("r_randolph", "r_halsted", "r_washington"):
        parts[k] = ribbons.get(k, [])
    parts["Site"] = [site_band(site, parts)]
    groups, faces = [], {}
    for name, colour in GROUPS:
        if not parts[name]:
            continue
        V, F = merge(parts[name])
        groups.append((name, colour, V, F)); faces[name] = int(len(F))
    size = write_glb(groups, OUT_GLB)

    allV = np.vstack([g[2] for g in groups if g[0] != "Site" and not g[0].startswith("r_")])
    ext_ft = [allV.min(0).round(2).tolist(), allV.max(0).round(2).tolist()]
    labels = {"r_randolph": ("randolph", "Randolph St"), "b_restaurantrow": ("restaurantrow", "Restaurant Row"),
              "r_halsted": ("halsted", "Halsted St"), "r_washington": ("washington", "Washington Blvd"),
              "b_skybridge": ("skybridge", "Skybridge"), "Site": ("site", "735 W Randolph")}
    features = []
    for node in ("r_randolph", "b_restaurantrow", "r_halsted", "r_washington", "b_skybridge", "Site"):
        fid, label = labels[node]
        f = {"id": fid, "label": label, "node": node, "faces": faces.get(node, 0)}
        if node.startswith("r_"):
            f["osmIds"] = way_ids[node]; f["buildings"] = 0
            f["ribbon"] = ribbon_stats.get(node)
        elif node.startswith("b_"):
            f["osmIds"] = b_ids[node]; f["buildings"] = len(b_ids[node])
        else:
            f["osmIds"] = []; f["buildings"] = 0
        features.append(f)
    place = place_tower(site, parts)
    poly_ok = all(point_in_poly(p, poly) for p in place["cornersModelFt"])
    # signed overhang of each F_POD corner outside the Site polygon (ft -> m)
    over = [0.0 if point_in_poly(p, poly) else
            min(seg_dist(p, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))) * FT
            for p in place["cornersModelFt"]]
    xc = podium_crosscheck(place)

    d["siteGlb"] = {
        "file": "assets/site.glb", "bytes": size, "units": "m", "up": "y",
        "rootRotation": ROOT_ROT, "origin": "site-model (0, 0, 0) ft",
        "groups": [g[0] for g in groups], "faces": faces, "facesTotal": sum(faces.values()),
        "vertices": {g[0]: int(len(g[2])) for g in groups},
        "colours": {g[0]: g[1] for g in groups},
        "extentFt": ext_ft, "extentM": [[round(v * FT, 3) for v in ext_ft[0]], [round(v * FT, 3) for v in ext_ft[1]]],
        "removedBuildingIds": sorted(n for n, _ in removed), "removedCount": len(removed),
        "excludedLayers": ["Earth (Google 3D Tiles)", "Setup::*", "TPX_TERRAIN", "Rail"],
        "decimated": False,
        "nodes": [g[0] for g in groups]}
    d["features"] = features
    d["siteLoop"] = {"frameFt": {k: (round(v, 2) if v is not None else None) for k, v in frame.items()},
                     "ribbonWidthM": RIBBON_WIDTH_M, "ribbonLiftM": RIBBON_LIFT_M, "ribbonMaxDistM": RIBBON_MAX_DIST_M,
                     "restaurantRowDistM": ROW_DIST_M,
                     "source": "tools/build_site_glb.py v1.1; centrelines from _local/osm_corridor.json (S13)"}
    d["towerOffset"] = [round(float(v), 3) for v in place["offset"]]
    d["towerYawDeg"] = round(place["yawDeg"], 4)
    d["towerPlacement"] = {
        "rule": "F_POD (tower GLB x 0..97.84 m N-S, x = 0 north; z 0..63.40 m, z = 0 east) centred on the Site "
                "polycurve's minimum-area rectangle; tower origin in site.glb scene metres = towerOffset; "
                "tower rotation.y = towerYawDeg; the context is moved by the inverse so the tower stays at the origin",
        "siteRectFt": [round(place["rectFt"][0], 2), round(place["rectFt"][1], 2)],
        "siteRectCentreFt": [round(float(v), 2) for v in place["rectCentreFt"]],
        "siteRectAngleDeg": round(place["rectAngleDeg"], 4),
        "groundFt": round(place["groundFt"], 2),
        "fPodCornersModelFt": [[round(float(x), 2), round(float(y), 2)] for x, y in place["cornersModelFt"]],
        "fPodInsideSite": poly_ok, "fPodCornerOverhangM": [round(v, 3) for v in over],
        "podiumCrossCheck": xc}
    with open(SITE_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(json.dumps({"bytes": size, "faces": faces, "features": features, "siteLoop": d["siteLoop"],
                      "removed": d["siteGlb"]["removedBuildingIds"],
                      "extentFt": ext_ft, "towerOffset": d["towerOffset"], "towerYawDeg": d["towerYawDeg"],
                      "placement": d["towerPlacement"], "layersSeen": seen}, indent=1))


if __name__ == "__main__":
    main()
