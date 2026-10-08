# -*- coding: utf-8 -*-
"""build_levels.py - emit data/levels.json for arch575.bradmachado.com from the deck script's LEVELS table.

Content source: <ROOT>\\05_Analysis_Tools\\MidReview_LevelDeck_v1.4.py (LEVELS, PROG, KEY_ORDER), loaded with importlib.
It imports MidReview_LevelDeck_v1.2.py (F_OFF1/F_OFF2/F_HOT/F_POD/HOT_SPLIT/ORBIT) and python-pptx, so run from a
Python that has python-pptx, lxml and Pillow (3.10.11 on this machine).
Legend: <ROOT>\\03_Design\\05_Presentation\\MidReview\\PlanFurnished_V14_v1.2\\legend_v1.2.json (keys per level).
Colours: plan v1.1 section 1 program key (oxide accent, OUTDOOR tint); the deck script's navy values are NOT used.
Also copies the GLB to assets/tower.glb and the site image to assets/site.jpg (<= 2400 px long edge, JPEG q85).

Usage (from the repo root):  python tools/build_levels.py [--no-assets]
"""
import sys, os, json, shutil, importlib.util

ROOT = r"C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575"
DECK = os.path.join(ROOT, r"05_Analysis_Tools\MidReview_LevelDeck_v1.4.py")
LEGEND = os.path.join(ROOT, r"03_Design\05_Presentation\MidReview\PlanFurnished_V14_v1.2\legend_v1.2.json")
GLB = os.path.join(ROOT, r"03_Design\05_Presentation\Web\Assets\TowerModel_GLB_v1.0.glb")
SITE = os.path.join(ROOT, r"03_Design\05_Presentation\TechReport1_Process\TR1_v2_cover_ssw.jpg")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "data", "levels.json")

# plan v1.1 section 1: program key colours (the level's own program takes the accent on screen)
ACCENT = "#B0431F"
COLOURS = {"OFFICE": "#B5B5B5", "HOTEL": "#B5B5B5", "AMENITY": "#B5B5B5", "OUTDOOR": "#EFD9D2",
           "CIRCULATION": "#FFFFFF", "NOSTOP": "#F0F0F0", "BOH": "#D9D9D9", "MEP": "#3A3A3A"}
CAMERA = {"azDeg": 31.95, "pitchDeg": -7.74, "rollDeg": -4.11}
TITLE = {"eyebrow": "ARCH 575 / Mid-review", "h1": "West Loop Gateway",
         "lines": ["Mixed-use tower, 735 W. Randolph St.", "ARCH 575 mid-review, Fall 2026"]}
SITE_TEXT = {"label": "Site", "name": "735 W. Randolph St.", "sub": "West Loop, Chicago",
             "lines": ["Randolph to Washington.", "Kennedy Expressway to the east.", "Gateway to Restaurant Row."]}
MAX_EDGE, JPEG_Q = 2400, 85


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
        keys = [k for k in deck.KEY_ORDER if k in legend[key]]
        levels.append({
            "key": key, "label": label, "name": name, "sub": sub, "description": desc,
            "rows": [[lab, val] for lab, val in rows],
            "program": prog,
            "box": [round(v, 4) for v in box],
            "y": [round(y0, 4), round(y1, 4)],
            "keys": keys,
            "plan": "assets/plans/PlanColor_%s_v1.4.svg" % key,
        })
    return {
        "title": TITLE, "site": SITE_TEXT, "accent": ACCENT,
        "orbitDeg": float(deck.ORBIT), "camera": CAMERA,
        "programs": programs, "levels": levels,
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
