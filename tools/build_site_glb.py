# build_site_glb_v1.0 — This section is intended to export the Rhino site model (read only, rhino3dm) as the
# web context GLB assets/site.glb (buildings minus the on-site footprints, TERRAIN_MESH, Bridges, Roads, Site
# outline band; feet -> metres; root rotation as the tower GLB; one grey material per group) and to place the
# tower: fit the F_POD footprint onto the Site polycurve's rectangle, cross-check it against the podium outline
# in Randolph_Master_v1.1.3dm, and write towerOffset / towerYawDeg / removed ids / face counts to data/site.json.
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
# S5 palette greys (tower.js GREYS), one per group
GROUPS = [("buildings", "#B5B5B5"), ("TERRAIN_MESH", "#F2F2F0"), ("Bridges", "#D9D9D9"),
          ("Roads", "#E4E4E2"), ("Site", "#9A9A9A")]


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
            parts[lp] += brep_meshes(g) if isinstance(g, rhino3dm.Brep) else [mesh_arrays(g)]
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
    js = {"asset": {"version": "2.0", "generator": "build_site_glb_v1.0 (rhino3dm + numpy)"},
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


def main():
    parts, bld, site, seen = read_site()
    poly = site[:, :2]
    removed, keep = [], []
    for name, cen, ms in bld:
        (removed if point_in_poly(cen, poly) else keep).append((name, ms))
    parts["buildings"] = [x for _, ms in keep for x in ms]
    parts["Site"] = [site_band(site, parts)]
    groups, faces = [], {}
    for name, colour in GROUPS:
        if not parts[name]:
            continue
        V, F = merge(parts[name])
        groups.append((name, colour, V, F)); faces[name] = int(len(F))
    size = write_glb(groups, OUT_GLB)

    allV = np.vstack([g[2] for g in groups if g[0] != "Site"])
    ext_ft = [allV.min(0).round(2).tolist(), allV.max(0).round(2).tolist()]
    place = place_tower(site, parts)
    poly_ok = all(point_in_poly(p, poly) for p in place["cornersModelFt"])
    # signed overhang of each F_POD corner outside the Site polygon (ft -> m)
    over = [0.0 if point_in_poly(p, poly) else
            min(seg_dist(p, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))) * FT
            for p in place["cornersModelFt"]]
    xc = podium_crosscheck(place)

    d = json.load(open(SITE_JSON, encoding="utf-8"))
    d["siteGlb"] = {
        "file": "assets/site.glb", "bytes": size, "units": "m", "up": "y",
        "rootRotation": ROOT_ROT, "origin": "site-model (0, 0, 0) ft",
        "groups": [g[0] for g in groups], "faces": faces, "facesTotal": sum(faces.values()),
        "vertices": {g[0]: int(len(g[2])) for g in groups},
        "colours": {g[0]: g[1] for g in groups},
        "extentFt": ext_ft, "extentM": [[round(v * FT, 3) for v in ext_ft[0]], [round(v * FT, 3) for v in ext_ft[1]]],
        "removedBuildingIds": sorted(n for n, _ in removed), "removedCount": len(removed),
        "excludedLayers": ["Earth (Google 3D Tiles)", "Setup::*", "TPX_TERRAIN", "Rail"],
        "decimated": False}
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
    print(json.dumps({"bytes": size, "faces": faces, "removed": d["siteGlb"]["removedBuildingIds"],
                      "extentFt": ext_ft, "towerOffset": d["towerOffset"], "towerYawDeg": d["towerYawDeg"],
                      "placement": d["towerPlacement"], "layersSeen": seen}, indent=1))


if __name__ == "__main__":
    main()
