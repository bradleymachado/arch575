# Prompt — Interior view captures in Rhino (for the Rhino MCP conversation)

Brad runs this in a Claude desktop chat that has the Rhino MCP. The web conversation cannot reach Rhino. Eight transparent-background captures come back to `03_Design\05_Presentation\Views\`; the web conversation composites the matching Google Earth frames behind them (`tools/composite_views.py`) and adds the view slides.

```
5.1 Interior View Captures
Project: ARCH 575 — 725 W Randolph tower (Core_Tower_V14_v1.4.3dm, open in Rhino 8). Read only: never save, spawn or close a slot. Rhino MCP: list_slots first, then pass slot "aardvark" on every call. No computer use while Brad is at the machine; restore Brad's active viewport camera at the end.
Goal: eight perspective captures from inside the building with a TRANSPARENT background and the glazing hidden, so the web conversation can place the matching Google Earth frame (02_Site\Photos_Survey\735WRandolph_<view>_View_v1.1.jpg, 1456 x 816, camera at 41.8839 -87.6469, level horizon) behind each one.
Views (key · floor · heading · eye height = floor z + 5 ft, model feet; floor z from the model's level data, fallback values given):
  1 O1-L10-E   · L10 open office   · east (target = eye + (+1000, 0, 0))  · eye z 154 ft
  2 O1-L10-W   · L10 open office   · west (eye + (-1000, 0, 0))           · eye z 154 ft
  3 O2-L25-E   · L25 executive     · east                                  · eye z 394 ft
  4 O2-L25-W   · L25 executive     · west                                  · eye z 394 ft
  5 Hotel-L41-E · L41 guest room   · east                                  · eye z 626 ft
  6 Hotel-L41-W · L41 guest room   · west                                  · eye z 626 ft
  7 L45-SSW    · L45 suite         · heading 202.5 deg (direction (-0.383, -0.924, 0))  · eye z 683 ft
  8 L45-W      · L45 suite         · west                                  · eye z 683 ft
Model axes: X east, Y north, feet, footprint corner at the origin.
Steps:
1. list_slots; confirm the open document is Core_Tower_V14_v1.4.3dm. Record the current Perspective camera (location, target, lens) to restore later. Read the level elevations from the model (level layers or the stacked-plan data); if they disagree with the fallback eye heights by more than 2 ft, use the model's and report the values.
2. For each view: eye = on the floor's plate, on the plate centreline, 2/3 of the way from the core face toward the facade the view faces (inside the room, not in the glazing zone); target = eye + direction; lens 31 mm (about 60 deg horizontal, matching the Earth frames' 60y; verify on view 3 that the horizon sits at mid-height). Viewport size 1456 x 816 (same aspect as the Earth frames).
3. Display: the furnished plan layers for that floor visible (walls, core, furniture, people if any), floors above and below hidden except the ceiling slab of the room, ALL glazing / curtain-wall glass layers hidden (mullions stay), display mode Arctic or Shaded in greys (no coloured materials), ground plane off, no grid.
4. Capture: _-ViewCaptureToFile at 2912 x 1632, TransparentBackground=Yes, to C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\05_Presentation\Views\735WRandolph_<key>_Capture_v1.0.png (keys exactly as listed, e.g. 735WRandolph_O1-L10-E_Capture_v1.0.png). Check each file exists and is > 200 kB with an alpha channel.
5. Restore Brad's viewport camera and layer states. Report one line per view: key, eye (x, y, z ft), lens, file path, size. Append one dated entry at the top of PROJECT_LOG.md.
STOP - report the eight file paths before I continue.
```
