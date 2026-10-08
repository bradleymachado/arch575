# fetch_osm_v1.0 — This section is intended to download the OpenStreetMap data for the S13 entry maps
# (city bbox, Randolph corridor bbox, and the site-model buildings by OSM way id) from Overpass and cache
# it in _local/osm_*.json; a re-run skips any cache file that already exists.
#
# Usage (from the repo root):  python tools/fetch_osm.py [--force [city|corridor|site ...]]
# Lake Michigan is not natural=coastline in OSM; the city query also returns the lake relation, member
# geometry clipped to the city bbox (second out statement of the same query).
# Reads the site model with rhino3dm only (read only) to collect the way ids from the `buildings` layer names.
import sys, os, json, time, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LOCAL = os.path.join(REPO, "_local")
ROOT = r"C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575"
SITE3DM = os.path.join(ROOT, r"02_Site\Arch575_BlenderSite_RhinoModel_v2.0.3dm")

ENDPOINTS = ["https://overpass-api.de/api/interpreter",
             "https://overpass.kumi.systems/api/interpreter",
             "https://maps.mail.ru/osm/tools/overpass/api/interpreter"]

CITY = (41.62, -87.98, 42.05, -87.50)          # s, w, n, e (plan section 1 "Map data")
CORRIDOR = (41.878, -87.662, 41.892, -87.618)


def bb(b):
    return "%.3f,%.3f,%.3f,%.3f" % b


def q_city():
    b = bb(CITY)
    return f"""[out:json][timeout:180];
(
  way["natural"="coastline"]({b});
  way["waterway"="river"]({b});
  way["natural"="water"]["water"="river"]({b});
  relation["natural"="water"]["water"="river"]({b});
  way["highway"~"^(motorway|trunk|primary|secondary)$"]({b});
  relation["boundary"="administrative"]["admin_level"="8"]["name"="Chicago"]({b});
);
out geom;
relation["natural"="water"]["name"="Lake Michigan"];
out geom({b});"""


def q_corridor():
    b = bb(CORRIDOR)
    return f"""[out:json][timeout:180];
(
  way["highway"]({b});
  way["building"]({b});
  relation["building"]({b});
  way["waterway"="river"]({b});
  way["natural"="water"]({b});
  relation["natural"="water"]({b});
  way["railway"="rail"]({b});
);
out geom;"""


def site_ids():
    import rhino3dm
    m = rhino3dm.File3dm.Read(SITE3DM)
    lay = {i: l.FullPath for i, l in enumerate(m.Layers)}
    ids = set()
    for o in m.Objects:
        if lay[o.Attributes.LayerIndex] == "buildings":
            n = (o.Attributes.Name or "").strip()
            if n.isdigit():
                ids.add(int(n))
    return sorted(ids)


def q_site(ids):
    return "[out:json][timeout:180];\nway(id:%s);\nout geom;" % ",".join(str(i) for i in ids)


def run(query, path):
    data = urllib.parse.urlencode({"data": query}).encode()
    last = None
    for attempt in range(2):
        for ep in ENDPOINTS:
            try:
                req = urllib.request.Request(ep, data=data, headers={"User-Agent": "arch575-site-build/1.0 (bradmachado.com)"})
                with urllib.request.urlopen(req, timeout=240) as r:
                    body = r.read()
                js = json.loads(body)
                if "elements" not in js:
                    raise ValueError("no elements: %r" % body[:200])
                with open(path, "wb") as f:
                    f.write(body)
                print("  %s <- %s  %d elements, %d bytes" % (os.path.basename(path), ep, len(js["elements"]), len(body)))
                return
            except Exception as e:  # try the next endpoint
                last = e
                print("  %s failed: %s" % (ep, e))
                time.sleep(3)
    raise SystemExit("Overpass unreachable: %s" % last)


def main():
    force = "--force" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    os.makedirs(LOCAL, exist_ok=True)
    jobs = [("osm_city.json", q_city), ("osm_corridor.json", q_corridor), ("osm_site.json", None)]
    for name, fn in jobs:
        path = os.path.join(LOCAL, name)
        if os.path.exists(path) and not (force and (not only or name[4:-5] in only)):
            print("skip (cached):", name)
            continue
        if fn is None:
            ids = site_ids()
            print("site ways:", len(ids))
            q = q_site(ids)
        else:
            q = fn()
        print("query:", name)
        run(q, path)


if __name__ == "__main__":
    main()
