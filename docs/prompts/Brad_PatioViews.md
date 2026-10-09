# Prompt set — Patio renderings: L17 outdoor terrace and L34 pool deck

Same pipeline as the interior views (`Brad_BlenderInteriorViews.md`): Earth frame → Rhino plate export → Blender MCP build-out with the frame beyond → render lands in `03_Design\05_Presentation\Views\` → `tools/composite_views.py` adds the slide. Keys: `Terrace-L17-E` and `Pool-L34-SSW`.

Eye heights (model feet, floor z from `data/levels.json` + 5 ft): L17 floor 263.8 ft → eye 268.8 ft (81.9 m); L34 floor 528.2 ft → eye 533.2 ft (162.5 m). Earth altitude = grade 181 m + eye.

## A — Google Earth chat (3 min): two frames

```
Two frames, same rules as the eight 18:31 views (no UI words, 1456 x 816, Imagery © Google watermark kept, level horizon, 60 deg field of view):
1  L17 terrace, looking east to the Loop:
   https://earth.google.com/web/@41.8839,-87.6469,262.9a,1d,60y,90h,90t,0r
   save as C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\02_Site\Photos_Survey\735WRandolph_Terrace-L17-E_View_v1.1.jpg
2  L34 pool deck, looking south-southwest:
   https://earth.google.com/web/@41.8839,-87.6469,343.5a,1d,60y,202.5h,90t,0r
   save as C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\02_Site\Photos_Survey\735WRandolph_Pool-L34-SSW_View_v1.1.jpg
```

## B — Rhino chat (5 min): two plates

```
5.1d Plate export for the patio views
Project: ARCH 575 — Core_Tower_V14_v1.4.3dm open in Rhino 8. Read only; list_slots first, slot "aardvark" on every call; never save, spawn or close.
Export, for L17 and L34, the geometry Blender needs for one exterior terrace view each: slab outline, the terrace / deck slab edge and any parapet or guardrail line, the enclosed-room outline that the terrace opens from (L17 coworking / juice bar; L34 clubhouse cafe bar and lounge), the pool outline on L34, core walls, the ceiling / soffit of the floor above where it overhangs the terrace, and any 3D furniture blocks. _-Export selected as OBJ (feet, Z up, polygons, materials off) to
  C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\05_Presentation\Views\Plate_L17_v1.0.obj
  C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\05_Presentation\Views\Plate_L34_v1.0.obj
Report: floor z of each level (ft), the terrace outline corners on each (model axes X east, Y north, footprint corner at origin), which terrace edge faces east (L17) and south-southwest (L34), the L34 pool outline, and the width of the soffit overhang above each terrace. Restore the viewport. One dated PROJECT_LOG.md entry.
STOP - report the two file paths and the terrace corners before I continue.
```

## C — Blender chat: L17 terrace, east

```
5.1e Patio view build-out — L17 outdoor terrace, east
Blender 5.2 via the Blender MCP (attach to the open session; never launch or close Blender; no computer use while Brad is at the machine). Save as C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\05_Presentation\Views\Patio_L17-E_v1.0.blend (new file).
Inputs: Plate_L17_v1.0.obj (feet; import scale 0.3048, Z up; model X east, Y north), the terrace corners from the Rhino chat, and the Earth frame C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\02_Site\Photos_Survey\735WRandolph_Terrace-L17-E_View_v1.1.jpg (1456 x 816, level horizon, 60 deg horizontal field of view, heading 90 deg east, eye at floor + 5 ft).
Build:
1. Import the plate; keep the terrace slab, its edge, the soffit above where it overhangs, and the glazed wall of the coworking / juice bar room behind the terrace (glass plane, IOR 1.45, mullions as 50 mm dark extrusions). Delete the rest of the floor beyond a one-bay margin.
2. Furnish as an outdoor coworking terrace: a 1.1 m glass guardrail on the open edge (no mullions), pale concrete pavers, three communal timber tables with chairs, four lounge chairs in pairs, planters with grasses and two small trees in large pots along the edge, the juice bar counter with stools just inside the glazing, warm timber soffit. Materials in greys and timber, one accent #B0431F on a single element (a sunshade or one chair group). Soft daylight: sun 40 deg altitude from the south-east.
3. The view beyond: the Earth frame as a camera-facing image plane 300 m from the camera, scaled to fill the camera frame exactly at the camera's field of view (plane width = 2 x 300 m x tan(30 deg)), emission strength 1, unlit; horizon at eye height. No glazing in front of it: the view is open air over the guardrail.
4. Camera: on the terrace, eye 1.52 m above the deck, heading 90 deg (east, model +X), level, horizontal field of view 60 deg, sensor fit horizontal, resolution 2912 x 1632. Place it so the guardrail and skyline fill the right two-thirds, a table group enters at the left, the soffit edge at the top.
5. Render EEVEE Next, 128 samples, AO + screen-space reflections on, AgX medium contrast, to C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\05_Presentation\Views\735WRandolph_Terrace-L17-E_Render_v1.0.png. Top-view layout capture as ..._Layout_v1.0.png. One dated PROJECT_LOG.md entry.
STOP - report the render path and the camera values before I continue.
```

## D — Blender chat: L34 pool deck, south-southwest

```
5.1f Patio view build-out — L34 pool deck, south-southwest
Blender 5.2 via the Blender MCP (attach to the open session; never launch or close Blender; no computer use while Brad is at the machine). Save as C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\05_Presentation\Views\Patio_L34-SSW_v1.0.blend (new file).
Inputs: Plate_L34_v1.0.obj (feet; import scale 0.3048, Z up; model X east, Y north), the deck and pool corners from the Rhino chat, and the Earth frame C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\02_Site\Photos_Survey\735WRandolph_Pool-L34-SSW_View_v1.1.jpg (1456 x 816, level horizon, 60 deg horizontal field of view, heading 202.5 deg, eye at floor + 5 ft).
Build:
1. Import the plate; keep the deck slab and edge, the pool outline, the soffit above where it overhangs, and the clubhouse cafe bar / lounge glazing behind the deck (glass plane, IOR 1.45, 50 mm dark mullions). Delete the rest beyond a one-bay margin.
2. Furnish as a hotel pool deck: 1.1 m glass guardrail on the open edges, the pool as water (glass-like, 1.2 m deep, pale tile floor), loungers in pairs along the pool with small side tables, two cabana frames, planters, the bar counter with stools under the soffit at the inner edge, pale stone pavers, timber soffit. Materials in greys, stone and timber; one accent #B0431F on a single element (the cabana canvas or one lounger). Soft daylight: sun 35 deg altitude from the south-west.
3. The view beyond: the Earth frame as a camera-facing image plane 300 m from the camera, scaled to fill the camera frame exactly at the camera's field of view (plane width = 2 x 300 m x tan(30 deg)), emission strength 1, unlit; horizon at eye height. No glazing in front of it.
4. Camera: on the deck, eye 1.52 m above the deck, heading 202.5 deg (south-southwest; direction (-0.383, -0.924, 0) in model axes), level, horizontal field of view 60 deg, sensor fit horizontal, resolution 2912 x 1632. Place it so the pool enters from the left, the guardrail and skyline fill the top half, the bar at the right edge.
5. Render EEVEE Next, 128 samples, AO + screen-space reflections on, AgX medium contrast, to C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\05_Presentation\Views\735WRandolph_Pool-L34-SSW_Render_v1.0.png. Top-view layout capture as ..._Layout_v1.0.png. One dated PROJECT_LOG.md entry.
STOP - report the render path and the camera values before I continue.
```

Refinements (Gemini / ComfyUI) go beside the render as `_Render_v1.1.png`; the deck takes the highest version.
