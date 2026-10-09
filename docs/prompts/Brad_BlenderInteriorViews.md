# Prompt — Interior views via Blender (Rhino plate export → Blender MCP build-out → Earth frame beyond)

Two desktop chats: the Rhino MCP chat exports the plates; the Blender MCP chat builds the room and renders. The web conversation picks the renders up from `03_Design\05_Presentation\Views\` (`tools/composite_views.py` accepts `*_Render_v1.0.png` as finished images) and adds the view slides. Optional ComfyUI pass after the render, never instead of it.

Order tonight: view 7 (L45 suite SSW) first as the pilot, then 3 (L25 east). The other six only if time allows.

## A — Rhino chat (5 min)

```
5.1a Plate export for Blender
Project: ARCH 575 — Core_Tower_V14_v1.4.3dm open in Rhino 8. Read only; list_slots first, slot "aardvark" on every call; never save, spawn or close.
Export, for L45 and L25, the geometry Blender needs for one interior view each: slab outline, core walls, partitions / demising walls, glazing line and mullion grid of that floor, the ceiling slab above, and any 3D furniture blocks on the floor. Select by level layers; _-Export selected as OBJ (feet, Y up off, Z up, polygons, materials off) to
  C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\05_Presentation\Views\Plate_L45_v1.0.obj
  C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\05_Presentation\Views\Plate_L25_v1.0.obj
Report: floor z and ceiling z of each level (ft), the plate's bounding box (ft, model axes X east Y north, footprint corner at origin), the corner suite on L45 that faces south-southwest (its room outline corners), and the executive office on L25 facing east. Restore the viewport. One dated PROJECT_LOG.md entry.
STOP - report the two file paths and the room corners before I continue.
```

## B — Blender chat (45–60 min for the pilot)

```
5.1b Interior view build-out — L45 suite SSW
Blender 5.2 via the Blender MCP (attach to the open session; never launch or close Blender; no computer use while Brad is at the machine). Save as C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\05_Presentation\Views\Interior_L45-SSW_v1.0.blend (new file, never over an earlier one).
Inputs: Plate_L45_v1.0.obj (feet; import with scale 0.3048 → metres, Z up), the room corners reported by the Rhino chat, and the Google Earth frame C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\02_Site\Photos_Survey\735WRandolph_L45-SSW_View_v1.1.jpg (1456 x 816, level horizon, 60 deg field of view, heading 202.5 deg, eye at floor + 5 ft).
Build:
1. Import the plate; keep slab, ceiling (9 ft 6 in clear), core and partitions; delete everything outside the suite plus a 1-room margin. Glazing: a glass plane on the facade line (IOR 1.45, roughness 0, slight grey tint) with the mullion grid from the plate as 50 mm dark extrusions.
2. Furnish the suite as a hotel corner room: king bed with headboard wall, two nightstands, lounge chair + small table at the window, desk, wardrobe wall, bathroom behind the headboard (door only). Simple clean geometry; no downloaded assets. Materials in greys (warm white walls, pale oak floor, charcoal upholstery) and one accent #B0431F on a single element (the chair or a throw). Soft daylight: sun 35 deg altitude from the south-west plus the HDRI-free world set to the Earth frame (below).
3. The view beyond: the Earth frame as a camera-facing image plane outside the glazing, far enough to clear the facade (300 m from the camera), scaled so it fills the camera frame exactly at the camera's field of view (plane width = 2 x 300 m x tan(30 deg)), emission shader strength 1, unlit by the sun. Horizon of the image at the camera's eye height (the frame was shot level).
4. Camera: inside the room, eye 1.52 m above the floor, heading 202.5 deg (south-southwest; model X east, Y north), level, horizontal field of view 60 deg, sensor fit horizontal, resolution 2912 x 1632 (same aspect as the frame). Place it so the window wall fills the right two-thirds of the frame and the bed edge enters at the left.
5. Render EEVEE Next, 128 samples, AO + screen-space reflections on, colour management Filmic / AgX medium contrast, to C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\05_Presentation\Views\735WRandolph_L45-SSW_Render_v1.0.png. Also save a viewport capture of the scene layout (top view) as ..._Layout_v1.0.png. One dated PROJECT_LOG.md entry.
STOP - report the render path and the camera values before I continue.
```

Then repeat for L25 with `Plate_L25_v1.0.obj`, the executive office facing east, the frame `735WRandolph_O2-L25-E_View_v1.1.jpg`, heading 90 deg, file `735WRandolph_O2-L25-E_Render_v1.0.png`.

## C — Optional ComfyUI pass (10 min per image)

Img2img on the Blender render with depth + lineart ControlNet, denoise 0.30–0.40, prompt limited to materials and light ("hotel suite, oak floor, linen, soft daylight, photographic"), negative "people, text, logos, extra windows". Output `..._Render_v1.1.png` beside the v1.0. The geometry and the view must stay identical to v1.0; if a run changes the window grid or the skyline, discard it. The deck takes the highest version present.
