# composite_views_v1.2 — This section is intended to use a finished Blender/ComfyUI render when present, else place the Google Earth frames behind the transparent
# Rhino interior captures (03_Design\05_Presentation\Views\735WRandolph_<key>_Capture_v1.0.png) and write
# the deck images assets/views/View_<key>_v1.0.jpg (plus a mirror in the Views folder), then add one image
# slide per view to data/story.json (outro, before the massing images) with the Google attribution.
#
# Usage (repo root):  python tools/composite_views.py            # all keys with a capture present
#                     python tools/composite_views.py --dry      # report only, no files written
import os, sys, json
from PIL import Image, ImageOps

ROOT = r"C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575"
EARTH = os.path.join(ROOT, r"02_Site\Photos_Survey")
VIEWS = os.path.join(ROOT, r"03_Design\05_Presentation\Views")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "assets", "views")
STORY = os.path.join(REPO, "data", "story.json")
W, H = 2912, 1632                    # 2x the Earth frame (1456 x 816)

# key -> (earth frame stem, level label, name, caption)
VIEW_SET = [
    ("O1-L10-E",   "O1-L10-E",   "L10 · Office 1", "Looking east to the Loop",        "View from Office 1, L10, east"),
    ("O1-L10-W",   "O1-L10-W",   "L10 · Office 1", "Looking west over Fulton Market", "View from Office 1, L10, west"),
    ("O2-L25-E",   "O2-L25-E",   "L25 · Office 2", "Looking east to the Loop",        "View from Office 2, L25, east"),
    ("O2-L25-W",   "O2-L25-W",   "L25 · Office 2", "Looking west over Fulton Market", "View from Office 2, L25, west"),
    ("Hotel-L41-E", "Hotel-L41-E", "L41 · Hotel A", "Guest room, looking east",       "View from a guest room, L41, east"),
    ("Hotel-L41-W", "Hotel-L41-W", "L41 · Hotel A", "Guest room, looking west",       "View from a guest room, L41, west"),
    ("L45-SSW",    "L45-SSW",    "L45 · Hotel B",  "Suite, looking south-southwest", "View from a suite, L45, south-southwest"),
    ("L45-W",      "L45-W",      "L45 · Hotel B",  "Suite, looking west",            "View from a suite, L45, west"),
    ("Terrace-L17-E", "Terrace-L17-E", "L17 · Holodeck", "Terrace, looking east to the Loop", "View from the outdoor terrace, L17, east"),
    ("Pool-L34-SSW", "Pool-L34-SSW", "L34 · Clubhouse", "Pool deck, looking south-southwest", "View from the pool deck, L34, south-southwest"),
]
ATTRIB = "Imagery © Google"
FIG_START = 18                       # 4 sketch slides (Fig. 01-04) + 13 level plans (Fig. 05-17) come first


def composite(key, stem, dry):
    # A finished Blender (or ComfyUI) render wins: highest *_Render_v1.N.png in the Views folder, used as is
    import glob, re
    renders = sorted(glob.glob(os.path.join(VIEWS, f"735WRandolph_{key}_Render_v1.*.png")),
                     key=lambda f: int(re.search(r"_v1\.(\d+)\.png$", f).group(1)))
    if renders:
        name = f"View_{key}_v1.0.jpg"
        if not dry:
            os.makedirs(OUT, exist_ok=True)
            im = Image.open(renders[-1]).convert("RGB")
            im.save(os.path.join(OUT, name), quality=88, optimize=True, progressive=True)
        return name, f"{key}: render {os.path.basename(renders[-1])} -> assets/views/{name}"
    cap = os.path.join(VIEWS, f"735WRandolph_{key}_Capture_v1.0.png")
    earth = os.path.join(EARTH, f"735WRandolph_{stem}_View_v1.1.jpg")
    if not os.path.exists(cap):
        return None, f"{key}: no render or capture yet"
    if not os.path.exists(earth):
        return None, f"{key}: no Earth frame ({earth})"
    fg = Image.open(cap).convert("RGBA")
    bg = ImageOps.fit(Image.open(earth).convert("RGB"), fg.size, Image.LANCZOS)   # cover, centre crop
    out = Image.alpha_composite(bg.convert("RGBA"), fg).convert("RGB")
    name = f"View_{key}_v1.0.jpg"
    if not dry:
        os.makedirs(OUT, exist_ok=True)
        out.save(os.path.join(OUT, name), quality=88, optimize=True, progressive=True)
        out.save(os.path.join(VIEWS, name), quality=92)
    return name, f"{key}: {fg.size[0]}x{fg.size[1]} capture over {os.path.basename(earth)} -> assets/views/{name}"


AFTER = {"O1-L10-E": "L06-L15", "O1-L10-W": "L06-L15", "O2-L25-E": "L18-L32", "O2-L25-W": "L18-L32",
         "Hotel-L41-E": "L35-L41", "Hotel-L41-W": "L35-L41", "L45-SSW": "L42-L47", "L45-W": "L42-L47",
         "Terrace-L17-E": "L17", "Pool-L34-SSW": "L34"}


def add_slides(done, dry):
    """story.json 'views': one image slide per view, placed by js/app.js directly after the level in AFTER
    (Brad 2026-10-09 01:40). Figure numbers are assigned at render time by js/app.js. Any copy of a view that
    is still in the outro is removed."""
    d = json.load(open(STORY, encoding="utf-8"))
    views = d.setdefault("views", [])
    have = {v.get("src") for v in views}
    inserted = 0
    for key, stem, label, name, caption in VIEW_SET:
        fn = done.get(key)
        if not fn:
            continue
        src = f"assets/views/{fn}"
        d["outro"] = [s for s in d.get("outro", []) if s.get("src") != src]
        if src in have:
            continue
        views.append({"kind": "image", "src": src, "after": AFTER[key], "label": label, "name": name, "sub": "",
                      "lines": [], "caption": f"{caption} · {ATTRIB}"})
        inserted += 1
    order = [k for k, *_ in VIEW_SET]
    views.sort(key=lambda v: next((i for i, k in enumerate(order) if v["src"].endswith(f"View_{k}_v1.0.jpg")), 99))
    if not dry:
        with open(STORY, "w", encoding="utf-8", newline="\n") as f:
            json.dump(d, f, indent=1, ensure_ascii=False); f.write("\n")
    return inserted


def main():
    dry = "--dry" in sys.argv
    done = {}
    for key, stem, *_ in VIEW_SET:
        fn, msg = composite(key, stem, dry)
        print(msg)
        if fn:
            done[key] = fn
    n = add_slides(done, dry)
    print(f"{len(done)} composites, {n} slides added to data/story.json{' (dry run)' if dry else ''}")


if __name__ == "__main__":
    main()
