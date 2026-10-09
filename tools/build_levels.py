# -*- coding: utf-8 -*-
"""build_levels.py - emit data/levels.json for arch575.bradmachado.com from the deck script's LEVELS table.

Content source: <ROOT>\\05_Analysis_Tools\\MidReview_LevelDeck_v1.5.py (LEVELS, PROG, KEY_ORDER), loaded with importlib.
It imports MidReview_LevelDeck_v1.2.py (F_OFF1/F_OFF2/F_HOT/F_POD/HOT_SPLIT/ORBIT) and python-pptx, so run from a
Python that has python-pptx, lxml and Pillow (3.10.11 on this machine).
Legend: <ROOT>\\03_Design\\05_Presentation\\MidReview\\PlanFurnished_V14_v1.2\\legend_v1.2.json (keys per level).
Colours: plan v1.1 section 1 program key (oxide accent, OUTDOOR tint); the deck script's navy values are NOT used.
Also copies the GLB to assets/tower.glb and the site image to assets/site.jpg (<= 2400 px long edge, JPEG q85).

Usage (from the repo root):  python tools/build_levels.py [--no-assets]
"""
import sys, os, json, shutil, importlib.util

ROOT = r"C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575"
DECK = os.path.join(ROOT, r"05_Analysis_Tools\MidReview_LevelDeck_v1.5.py")
LEGEND = os.path.join(ROOT, r"03_Design\05_Presentation\MidReview\PlanFurnished_V14_v1.2\legend_v1.2.json")
GLB = os.path.join(ROOT, r"03_Design\05_Presentation\Web\Assets\TowerModel_GLB_v1.0.glb")
SITE = os.path.join(ROOT, r"03_Design\05_Presentation\TechReport1_Process\TR1_v2_cover_ssw.jpg")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "data", "levels.json")

# plan v1.1 section 1: program key colours (the level's own program takes the accent on screen)
ACCENT = "#B0431F"
PLAN_ACCENT = "#E3BDB1"   # v1.5 plans: hero program fill = 35 % tint of the accent (key swatch); the tower keeps ACCENT
COLOURS = {"OFFICE": "#B5B5B5", "HOTEL": "#B5B5B5", "AMENITY": "#B5B5B5", "OUTDOOR": "#F6E9E4",
           "CIRCULATION": "#FFFFFF", "NOSTOP": "#F0F0F0", "BOH": "#D9D9D9", "MEP": "#3A3A3A"}
CAMERA = {"azDeg": 31.95, "pitchDeg": -7.74, "rollDeg": -4.11}
TITLE = {"eyebrow": "ARCH 575 / Mid-review", "h1": "West Loop Gateway",
         "lines": ["Mixed-use tower, 725 W. Randolph St.", "ARCH 575 mid-review, Fall 2026"]}
SITE_TEXT = {"label": "Site", "name": "725 W. Randolph St.", "sub": "West Loop, Chicago",
             "lines": ["Randolph to Washington.", "Kennedy Expressway to the east.", "Gateway to Restaurant Row."]}
MAX_EDGE, JPEG_Q = 2400, 85

# Podium L01-L03 (Brad 2026-10-08; L04 not shown): line plans from the team's PDFs, not in the deck script's LEVELS table,
# inserted after B1. SVGs from <ROOT>\05_Analysis_Tools\Podium_PlanSVG_v1.0.py (1 in = 40 ft, north right).
# Floor-to-floor [18, 12, 12, 12] ft per Core_V14_Build_v1.3; L05 at z 54 ft = y 17.5, so y = z * 17.5 / 54.
# box = the B1 / podium footprint. No program key: the plans carry no program fills.
_Y = 17.5 / 54.0
PODIUM = [
    {"key": "L01", "label": "L01", "north": "right", "name": "Ground", "sub": "+ Randolph",
     "description": "Grand lobby, Randolph restaurant and kitchen, loading dock, bike storage, employee entrance.",
     "rows": [["Elevation", "+0 ft"], ["Floor to floor", "18 ft"]],
     "program": "", "box": [0.0, 97.8, 0.0, 63.4], "y": [0.0, round(18 * _Y, 4)], "keys": [],
     "plan": "assets/plans/PlanPodium_L01_v1.2.svg"},
    {"key": "L02", "label": "L02", "north": "right", "name": "Mezzanine", "sub": "+ Parking",
     "description": "Lobby mezzanine and pavilion lounge; first parking deck and ramps.",
     "rows": [["Elevation", "+18 ft"], ["Floor to floor", "12 ft"]],
     "program": "", "box": [0.0, 97.8, 0.0, 63.4], "y": [round(18 * _Y, 4), round(30 * _Y, 4)], "keys": [],
     "plan": "assets/plans/PlanPodium_L02_v1.0.svg"},
    {"key": "L03", "label": "L03", "north": "right", "name": "Parking", "sub": "Podium deck",
     "description": "Parking around the core, ramped deck to deck.",
     "rows": [["Elevation", "+30 ft"], ["Floor to floor", "12 ft"]],
     "program": "", "box": [0.0, 97.8, 0.0, 63.4], "y": [round(30 * _Y, 4), round(42 * _Y, 4)], "keys": [],
     "plan": "assets/plans/PlanPodium_L03_v1.0.svg"},
]


EXCLUDE = {"B1", "L16", "L33"}   # Brad 2026-10-09 01:50: basement and mechanical floors are not slides


def insert_podium(levels):
    """Insert PODIUM after B1 (replacing any earlier copy)."""
    keys = {p["key"] for p in PODIUM} | {"L03-L04"}
    out = [lv for lv in levels if lv["key"] not in keys]
    i = next((k for k, lv in enumerate(out) if lv["key"] == "B1"), -1) + 1
    return out[:i] + [dict(p) for p in PODIUM] + out[i:]


def load_deck(path):
    """Load the deck script as a module without running its __main__ block."""
    spec = importlib.util.spec_from_file_location("deck_v13", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build(deck, legend):
    programs = [{"key": k, "label": deck.PROG[k][0], "color": COLOURS[k]} for k in deck.KEY_ORDER]
    levels = []
    for key, label, name, sub, desc, rows, prog, box, (y0, y1) in deck.LEVELS:
        if key in EXCLUDE:   # Brad 2026-10-09 01:50: no basement or mechanical-floor slides
            continue
        keys = [k for k in deck.KEY_ORDER if k in legend[key]]
        levels.append({
            "key": key, "label": label, "name": name, "sub": sub, "description": desc,
            "rows": [[lab, val] for lab, val in rows if not (prog == "AMENITY" and lab == "Efficiency")],   # Brad 2026-10-09: amenity floors are not rentable
            "program": prog,
            "box": [round(v, 4) for v in box],
            "y": [round(y0, 4), round(y1, 4)],
            "keys": keys,
            "plan": "assets/plans/PlanColor_%s_%s.svg" % (key, "v1.6" if key == "B1" else "v1.5"),
        })
    return {
        "title": TITLE, "site": SITE_TEXT, "accent": ACCENT, "planAccent": PLAN_ACCENT,
        "orbitDeg": float(deck.ORBIT), "camera": CAMERA,
        "programs": programs, "levels": insert_podium(levels),
    }


def copy_assets():
    os.makedirs(os.path.join(REPO, "assets"), exist_ok=True)
    glb_out = os.path.join(REPO, "assets", "tower.glb")
    shutil.copyfile(GLB, glb_out)
    print("tower.glb  %d bytes" % os.path.getsize(glb_out))
    jpg_out = os.path.join(REPO, "assets", "site.jpg")
    try:
        from PIL import Image
        im = Image.open(SITE)
        w, h = im.size
        f = min(1.0, MAX_EDGE / float(max(w, h)))
        if f < 1.0:
            im = im.resize((round(w * f), round(h * f)), Image.LANCZOS)
        im.convert("RGB").save(jpg_out, "JPEG", quality=JPEG_Q, optimize=True, progressive=True)
        print("site.jpg   %dx%d -> %dx%d, q%d, %d bytes" % (w, h, im.size[0], im.size[1], JPEG_Q, os.path.getsize(jpg_out)))
    except ImportError:
        shutil.copyfile(SITE, jpg_out)
        print("site.jpg   copied (no Pillow), %d bytes" % os.path.getsize(jpg_out))


def main(argv):
    deck = load_deck(DECK)
    legend = json.load(open(LEGEND, encoding="utf-8"))
    data = build(deck, legend)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("levels.json  %d levels, %d programs, HOT_SPLIT %.4f" % (len(data["levels"]), len(data["programs"]), deck.HOT_SPLIT))
    if "--no-assets" not in argv:
        copy_assets()


if __name__ == "__main__":
    main(sys.argv[1:])
