# -*- coding: utf-8 -*-
"""Podium_PlanSVG_v1.1 - podium plan PDFs -> web-deck SVGs at 1 in = 40 ft.

v1.1 2026-10-09 (Brad: new ground-floor drawing GroundFloorBlank.pdf for L01; same sheet size as GroundFloor.pdf, same core calibration; only the L01 job runs, output PlanPodium_L01_v1.1.svg).
v1.0 2026-10-08 (Brad: add the podium floors between B1 and L05 on the web deck).
Scale is calibrated per drawing on the core bar width (48 ft outer, Core_Comparison_v1.2):
the measured core width in PDF points sets pt/ft, then every drawing is scaled to
1.8 pt/ft (72 pt = 40 ft), the scale the deck's scale bar assumes.
L2 and L3 are drawn portrait; they are rotated 90 deg clockwise so all three match
the ground floor and the tower plans (core long axis horizontal, north to the right).

Usage: python -I Podium_PlanSVG_v1.0.py <out_dir>
"""
import os
import sys

import pymupdf

ROOT = r"C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575"
PRES = os.path.join(ROOT, "03_Design", "05_Presentation")
TARGET_PT_PER_FT = 72.0 / 40.0
CORE_W_FT = 48.0

# (key, source pdf, measured core width in pt, rotate clockwise)
JOBS = [
    ("L01", os.path.join(PRES, "GroundFloorBlank.pdf"), 257.2, False),
]


def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for key, src, core_pt, rot in JOBS:
        s = TARGET_PT_PER_FT / (core_pt / CORE_W_FT)
        doc = pymupdf.open(src)
        try:
            page = doc[0]
            m = pymupdf.Matrix(s, s)
            if rot:
                # +90 = clockwise on screen: (x, y) -> (-y, x); shift back into view
                m = m * pymupdf.Matrix(90) * pymupdf.Matrix(1, 0, 0, 1, page.rect.height * s, 0)
            svg = page.get_svg_image(matrix=m, text_as_path=True)
            out = os.path.join(out_dir, "PlanPodium_%s_v1.1.svg" % key)
            with open(out, "w", encoding="utf-8") as f:
                f.write(svg)
            r = page.rect * m
            print("%s  scale %.4f  %.1f x %.1f pt  (%.0f x %.0f ft)  -> %s" % (
                key, s, r.width, r.height, r.width / TARGET_PT_PER_FT,
                r.height / TARGET_PT_PER_FT, out))
        finally:
            doc.close()


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except Exception as e:
        print("FAILED: %s" % e)
        sys.exit(1)
