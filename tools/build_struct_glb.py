# build_struct_glb_v1.0 — This section is intended to turn the Revit/Rhino structural framing export
# (Downloads\Structural Framing (1).glb, 48 MB, one mesh per member) into a compact web GLB
# assets/structure.glb: all members merged per material, positions only (flat normals are computed
# in three.js), baked into the tower GLB's frame (y up, metres, long axis along x, min corner at the
# origin) so it stands where the tower stands.
#
# Usage (repo root):  python tools/build_struct_glb.py "<source.glb>"
import os, sys, json, struct
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "assets", "structure.glb")
TOWER = {"x": (0.0, 97.84), "z": (0.0, 63.40)}     # tower.glb footprint (m): x N-S long axis, z E-W

CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def read_glb(path):
    b = open(path, "rb").read()
    assert b[:4] == b"glTF"
    ln = struct.unpack("<I", b[12:16])[0]
    js = json.loads(b[20:20 + ln])
    off = 20 + ln
    bl = struct.unpack("<I", b[off:off + 4])[0]
    assert b[off + 4:off + 8] == b"BIN\x00"
    return js, b[off + 8:off + 8 + bl]


def accessor(js, bin_, idx):
    a = js["accessors"][idx]; bv = js["bufferViews"][a["bufferView"]]
    dt = CT[a["componentType"]]; n = NC[a["type"]]
    start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride", 0)
    if stride and stride != n * np.dtype(dt).itemsize:
        raw = np.frombuffer(bin_, dtype=np.uint8, count=stride * a["count"], offset=start)
        return raw.reshape(a["count"], stride)[:, :n * np.dtype(dt).itemsize].copy().view(dt).reshape(a["count"], n)
    return np.frombuffer(bin_, dtype=dt, count=a["count"] * n, offset=start).reshape(a["count"], n)


def node_matrices(js):
    """World matrix per node (column-major glTF -> numpy 4x4)."""
    import math
    def local(n):
        if "matrix" in n:
            return np.array(n["matrix"], dtype=float).reshape(4, 4).T
        t = n.get("translation", [0, 0, 0]); q = n.get("rotation", [0, 0, 0, 1]); s = n.get("scale", [1, 1, 1])
        x, y, z, w = q
        R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                      [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                      [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
        M = np.eye(4); M[:3, :3] = R * np.array(s); M[:3, 3] = t
        return M
    world = {}
    def walk(i, parent):
        M = parent @ local(js["nodes"][i]); world[i] = M
        for c in js["nodes"][i].get("children", []): walk(c, M)
    for r in js["scenes"][js.get("scene", 0)]["nodes"]: walk(r, np.eye(4))
    return world


def member_box(V):
    """Oriented bounding box of a member (PCA axes), as 6 faces x 2 triangles with duplicated vertices
    so three.js computes flat normals. Profiles (W-shapes) collapse to their envelope: at deck scale
    the member reads the same and the file is 30x smaller."""
    c = V.mean(axis=0)
    X = V - c
    _, _, vt = np.linalg.svd(X, full_matrices=False)
    A = vt                     # rows = principal axes
    L = X @ A.T
    lo, hi = L.min(axis=0), L.max(axis=0)
    corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]) @ A + c
    # corner index = (xi<<2)|(yi<<1)|zi
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    Vo, Fo = [], []
    for q in faces:
        b = len(Vo)
        Vo += [corners[i] for i in q]
        Fo += [(b, b + 1, b + 2), (b, b + 2, b + 3)]
    return np.array(Vo, dtype=float), np.array(Fo, dtype=np.uint32)


def main(src):
    js, bin_ = read_glb(src)
    world = node_matrices(js)
    mats = js.get("materials", [])
    parts = {}   # material index -> [(V, F)]
    for ni, M in world.items():
        n = js["nodes"][ni]
        if "mesh" not in n: continue
        for prim in js["meshes"][n["mesh"]]["primitives"]:
            P = accessor(js, bin_, prim["attributes"]["POSITION"]).astype(float)
            Ph = np.c_[P, np.ones(len(P))] @ M.T
            V = Ph[:, :3]
            if "indices" in prim:
                F = accessor(js, bin_, prim["indices"]).reshape(-1, 3).astype(np.uint32)
            else:
                F = np.arange(len(V), dtype=np.uint32).reshape(-1, 3)
            parts.setdefault(prim.get("material", -1), []).append((V, F))
    # bake into the tower frame: rotate +90 deg about y (x' = z, z' = -x), then shift min corner to the origin
    allV = np.vstack([v for ps in parts.values() for v, _ in ps])
    R = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]], dtype=float)   # x' = z, y' = y, z' = -x
    rot = allV @ R.T
    lo = rot.min(axis=0); hi = rot.max(axis=0)
    shift = np.array([-lo[0], -lo[1] if lo[1] < 0 else 0.0, -lo[2]])
    print("source extent (rotated):", np.round(lo, 2), np.round(hi, 2), "-> span", np.round(hi - lo, 2))
    print("tower frame span x %.2f z %.2f" % (TOWER["x"][1], TOWER["z"][1]))
    groups = []
    for mi, ps in parts.items():
        Vs, Fs, off = [], [], 0
        name0 = (mats[mi].get("name") if 0 <= mi < len(mats) else "") or ""
        for V, F in ps:
            if len(V) > 24 and "Concrete" not in name0:
                V, F = member_box(V)        # steel / timber members: their oriented bounding box (24 verts, 12 flat tris)
            Vs.append((V @ R.T + shift).astype(np.float32)); Fs.append(F + off); off += len(V)
        V = np.vstack(Vs); F = np.vstack(Fs)
        name = (mats[mi].get("name") if 0 <= mi < len(mats) else None) or f"material_{mi}"
        col = (mats[mi].get("pbrMetallicRoughness", {}).get("baseColorFactor", [0.7, 0.7, 0.7, 1]) if 0 <= mi < len(mats) else [0.7, 0.7, 0.7, 1])
        groups.append((name, col, V, F))
        print(f"  {name}: {len(ps)} members, {len(V)} verts, {len(F)} tris")
    # write GLB (positions + uint32 indices per group, one grey material per group)
    blobs, bvs, accs, meshes, nodes = [], [], [], [], []
    offset = 0
    def add_blob(arr, target):
        nonlocal offset
        raw = arr.tobytes(); pad = (-len(raw)) % 4
        blobs.append(raw + b"\x00" * pad)
        bvs.append({"buffer": 0, "byteOffset": offset, "byteLength": len(raw), "target": target})
        offset += len(raw) + pad
        return len(bvs) - 1
    out_mats = []
    for gi, (name, col, V, F) in enumerate(groups):
        bv = add_blob(V, 34962)
        accs.append({"bufferView": bv, "componentType": 5126, "count": len(V), "type": "VEC3",
                     "min": V.min(axis=0).tolist(), "max": V.max(axis=0).tolist()})
        bi = add_blob(F.astype(np.uint32).ravel(), 34963)
        accs.append({"bufferView": bi, "componentType": 5125, "count": F.size, "type": "SCALAR"})
        out_mats.append({"name": name, "pbrMetallicRoughness": {"baseColorFactor": [0.72, 0.72, 0.70, 1], "metallicFactor": 0, "roughnessFactor": 0.9}, "doubleSided": True})
        meshes.append({"name": name, "primitives": [{"attributes": {"POSITION": 2 * gi}, "indices": 2 * gi + 1, "material": gi}]})
        nodes.append({"name": name, "mesh": gi})
    js_out = {"asset": {"version": "2.0", "generator": "build_struct_glb_v1.0 (arch575)"},
              "scene": 0, "scenes": [{"nodes": [0]}],
              "nodes": [{"name": "structure", "children": list(range(1, len(nodes) + 1))}] + nodes,
              "meshes": meshes, "materials": out_mats, "accessors": accs, "bufferViews": bvs,
              "buffers": [{"byteLength": offset}]}
    jb = json.dumps(js_out, separators=(",", ":")).encode(); jb += b" " * ((-len(jb)) % 4)
    bb = b"".join(blobs)
    glb = b"glTF" + struct.pack("<II", 2, 12 + 8 + len(jb) + 8 + len(bb)) + struct.pack("<I", len(jb)) + b"JSON" + jb + struct.pack("<I", len(bb)) + b"BIN\x00" + bb
    open(OUT, "wb").write(glb)
    print("wrote", OUT, len(glb), "bytes;", len(groups), "groups")


if __name__ == "__main__":
    main(sys.argv[1])
