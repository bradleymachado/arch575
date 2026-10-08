"""S6 review: diff every number on the site against a literal copy of plan §1,
audit computed-style colours and the plan SVGs.

Usage (repo root, with `python -m http.server 8000` running):
    python tools/review_s6.py
Runs headless Edge on _local/s6_check.html (--dump-dom), reads data/levels.json
and assets/plans/*.svg, prints a report and exits 1 on any mismatch.
"""
import colorsys, html, json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# Plan §1, copied literally (key, label, name, sub, program, box, y0, y1, rows)
F_OFF1 = (7.9, 97.8, 0.3, 39.9)
F_OFF2 = (27.7, 97.8, 0.3, 39.9)
F_HOT = (31.1, 72.5, 3.7, 36.6)
F_POD = (0.0, 97.8, 0.0, 63.4)
HOT_SPLIT = 193.6077
PLAN = [
    ("B1", "B1", "Basement", "Plant", "MEP", F_POD, -5.0, 0.0, [("Area", "43,378 sf")]),
    ("L05", "L05", "Function", "+ Conference", "AMENITY", F_OFF1, 17.5, 23.2, [("Area", "35,143 sf")]),
    ("L06-L15", "L06–15", "Office 1", "Typical", "OFFICE", F_OFF1, 23.8, 77.9,
     [("Floors", "10"), ("Plate", "39,930 sf"), ("Core", "6,386 sf"), ("Efficiency", "84.0 %")]),
    ("L16", "L16", "Mechanical 1", "", "MEP", F_OFF1, 77.9, 80.4, [("Area", "39,930 sf")]),
    ("L17", "L17", "Holodeck", "", "AMENITY", F_OFF1, 80.4, 82.8, [("Area", "25,203 sf")]),
    ("L18-L32", "L18–32", "Office 2", "Executive", "OFFICE", F_OFF2, 83.4, 158.5,
     [("Floors", "15"), ("Plate", "28,578 sf"), ("Core", "4,466 sf"), ("Efficiency", "84.4 %")]),
    ("L33", "L33", "Mechanical 2", "", "MEP", F_OFF2, 158.5, 161.0, [("Area", "28,578 sf")]),
    ("L34", "L34", "Hotel Clubhouse", "+ Pool", "AMENITY", F_OFF2, 161.0, 163.4, [("Area", "11,760 sf")]),
    ("L35-L41", "L35–41", "Hotel A", "", "HOTEL", F_HOT, 164.0, HOT_SPLIT,
     [("Floors", "7"), ("Keys", "23"), ("Plate", "14,040 sf"), ("Core", "2,480 sf"), ("Efficiency", "82.3 %")]),
    ("L42-L47", "L42–47", "Hotel B", "", "HOTEL", F_HOT, HOT_SPLIT, 219.5,
     [("Floors", "6"), ("Keys", "24"), ("Plate", "14,040 sf"), ("Core", "2,480 sf"), ("Efficiency", "82.3 %")]),
]
PROGRAMS = [("OFFICE", "#B5B5B5"), ("HOTEL", "#B5B5B5"), ("AMENITY", "#B5B5B5"), ("OUTDOOR", "#EFD9D2"),
            ("CIRCULATION", "#FFFFFF"), ("NOSTOP", "#F0F0F0"), ("BOH", "#D9D9D9"), ("MEP", "#3A3A3A")]
ACCENT = "#B0431F"
ALLOWED_HUES = {"#B0431F", "#EFD9D2", "#D7A18F"}  # accent + its two tints (§0 D2)
NUM = re.compile(r"\d+(?:,\d{3})*(?:\.\d+)?")

fails = []
def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail else ""))
    if not ok: fails.append(name)

def hexify(c):
    m = re.match(r"rgba?\((\d+), (\d+), (\d+)(?:, ([\d.]+))?\)", c)
    if not m: return None, 1.0
    r, g, b = (int(x) for x in m.groups()[:3])
    return f"#{r:02X}{g:02X}{b:02X}", float(m.group(4) or 1)

def chromatic(hx):
    r, g, b = (int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return max(r, g, b) - min(r, g, b) > 0.04  # > ~10/255 channel spread

# 1. levels.json vs §1
data = json.loads((ROOT / "data/levels.json").read_text(encoding="utf-8"))
L = data["levels"]
check("levels.json: 10 levels", len(L) == 10, str(len(L)))
mism = []
for lv, (key, label, name, sub, prog, box, y0, y1, rows) in zip(L, PLAN):
    for fld, want in [("key", key), ("label", label), ("name", name), ("sub", sub), ("program", prog)]:
        if (lv.get(fld) or "") != want: mism.append(f"{key}.{fld} {lv.get(fld)!r} != {want!r}")
    if [round(v, 4) for v in lv["box"]] != list(box): mism.append(f"{key}.box {lv['box']} != {box}")
    if [round(v, 4) for v in lv["y"]] != [y0, y1]: mism.append(f"{key}.y {lv['y']} != {[y0, y1]}")
    if [tuple(r) for r in lv["rows"]] != rows: mism.append(f"{key}.rows {lv['rows']} != {rows}")
if [(p["key"], p["color"].upper()) for p in data["programs"]] != PROGRAMS: mism.append("programs")
if data["accent"].upper() != ACCENT: mism.append("accent")
if data["orbitDeg"] != 36: mism.append("orbitDeg")
cam = data["camera"]
if (cam["azDeg"], cam["pitchDeg"], cam["rollDeg"]) != (31.95, -7.74, -4.11): mism.append("camera")
check("levels.json vs §1: 0 mismatches", not mism, f"{len(mism)} mismatches " + "; ".join(mism))

# 2. Rendered DOM vs §1
with tempfile.TemporaryDirectory() as prof:
    dom = subprocess.run([EDGE, "--headless=new", f"--user-data-dir={prof}", "--virtual-time-budget=20000",
                          "--window-size=1920,1080", "--dump-dom", "http://localhost:8000/_local/s6_check.html"],
                         capture_output=True, text=True, encoding="utf-8", timeout=180).stdout
m = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
R = json.loads(html.unescape(m.group(1)))
S = R["slides"]
check("rendered: 12 slides", len(S) == 12, str(len(S)))
rmism, nums_seen = [], 0
for s, (key, label, name, sub, prog, box, y0, y1, rows) in zip(S[2:], PLAN):
    got_rows = [tuple(r) for r in s["rows"]]
    want_rows = [(a, b) for a, b in rows]
    if [(a.lower(), b) for a, b in got_rows] != [(a.lower(), b) for a, b in want_rows]:
        rmism.append(f"{label} rows {got_rows}")
    for fld, want in [("label", label), ("name", name), ("sub", sub)]:
        if (s[fld] or "") != want: rmism.append(f"{label}.{fld} {s[fld]!r}")
    # every number in the slide's visible text must come from §1 (label, rows) or the caption/scale furniture
    allowed = set(NUM.findall(label + " " + name + " " + " ".join(b for _, b in rows)))
    allowed |= {f"{s['index'] - 2:02d}", "1", "40", "20", "50", "100", "200"}  # Fig. nn, 1 in = 40 ft, scale bar
    for n in NUM.findall(s["text"]):
        nums_seen += 1
        if n not in allowed: rmism.append(f"{label}: stray number {n}")
    k0 = s["key"][0] if s["key"] else None
    if not k0 or hexify(k0[1])[0] != ACCENT: rmism.append(f"{label}: first key swatch {k0}")
check("rendered numbers vs §1: 0 mismatches", not rmism, f"{nums_seen} numbers checked; " + "; ".join(rmism))

# 3. Brackets on screen
alltext = R["header"] + "\n" + "\n".join(s["text"] for s in S)
br = re.findall(r"\[[^\]]*\]", alltext)
check("no [BRACKETS] on screen", not br, ", ".join(br) or "0 found")

# 4. Computed-style hues
hues = {}
for c, els in R["colours"].items():
    hx, a = hexify(c)
    if hx and chromatic(hx): hues.setdefault(hx, set()).update(els)
check("accent is the only hue (all computed colours)", set(hues) <= ALLOWED_HUES,
      "chromatic colours: " + ", ".join(f"{h} ({len(e)} el)" for h, e in hues.items()))
for row in R["samples"]:
    print("      sample", row)
check("no rounded corners", not R["radius"], ", ".join(R["radius"][:5]))
check("no shadows", not R["shadow"], ", ".join(R["shadow"][:5]))
check("no gradients", not R["gradient"], ", ".join(R["gradient"][:5]))
check("flush-left type on slides", not R["align"], ", ".join(R["align"][:5]))

# 5. Plan SVGs
for lv in L:
    svg = (ROOT / lv["plan"]).read_text(encoding="utf-8").upper()
    cols = set(re.findall(r"#[0-9A-F]{6}", svg))
    bad = {c for c in cols if chromatic(c)} - ALLOWED_HUES
    txt = len(re.findall(r"<TEXT", svg)) + len(re.findall(r"<MARKER", svg))
    nostop = svg.count("#F0F0F0")
    msg = f"{lv['key']}: hues {sorted(c for c in cols if chromatic(c))}, text/marker {txt}, NOSTOP fills {nostop}"
    check(f"plan {lv['key']}: grey + accent only, no callouts", not bad and txt == 0, msg)
    if lv["key"] == "L18-L32":
        check("L18-L32: NOSTOP symbol present + in key", nostop > 0 and "NOSTOP" in lv["keys"], f"{nostop} #F0F0F0 fills")

print("phone deep-link [slide, slide top, tower bottom]:", R["phone"])
print(f"\n{len(fails)} FAIL" if fails else "\nALL PASS")
sys.exit(1 if fails else 0)
