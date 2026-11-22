# orchid-holder

3D-printable modular holder for an orchid pot, modelled with build123d in `holder.py`. Two printed parts: one open arched cup and N feet (default 8). Each foot is a curved spoke ending in an arc; the arcs together form a ring around the pot. `uv run python holder.py` exports `out/cup.stl|step` and `out/foot.stl|step` (print pose), plus `out/assembly.design.stl` and `out/pot.design.stl` (assembled pose, fit check). `uv run python render.py` renders `out/cup.png`, `out/foot.png`, `out/assembly.png`. Tests: `uv run pytest`. Types: `uv run mypy --strict holder.py render.py test_holder.py`. A full build takes ~10 s.

## Design goals (from the user)

Low (well under the pot height), stable against tipping, modular clip-in feet (more than 4, short), as see-through as possible, clean, and "organic" in the sense of less rigid: flowing curves and rounded shapes, not plant motifs. History: solid wall + solid flange rejected ("massive"); v2 straight struts with round arches first called "ugly", then a crossing twisted-strut lattice was built and rejected ("the previous arches were better"). Current: v2 arches on the soft base with ring feet. The user picked "same as v2" over oval windows or leaning arches.

## Target pot (approximate, measured by the user)

Bottom diameter 80 mm (`POT_BOTTOM_D`), 100 mm (`POT_RIM_D`) at 80 mm up the slanted side (`POT_SLANT`, measured along the slope, not vertically): vertical rise `POT_RISE` = sqrt(80^2 - 10^2) = 79.4 mm, taper from that. Earlier rough guess (120 tall, 85/120 diameters) superseded. `POT_H` 120 only sizes the preview pot (top extrapolated to ~110).

## Orientation (design frame = assembled pose)

- Z up, origin at the centre of the cup bottom, table at Z = 0. Pot rests at Z = `BASE_T` (2.5) on a `LIP` (5) inner ledge; the floor centre is open.
- Cup: one conical shell (`WALL` 2.4) following the pot taper with `POT_CLEARANCE` 0.3 mm radial gap (user wants a near-perfect tight fit), Z = 0 .. `CUP_H` (50; the user wants it low, the slant measurement only defines the taper). The first print with the old 85 mm guess + 1 mm gap let the pot slide sideways, plus a low core ring (R `CORE_R` 48, `CORE_H` 5, rounded top). `FEET` (8) round-arched windows are cut between the struts (Z `WINDOW_Z0` 6.5 .. `WINDOW_Z1` = `CUP_H` - 5, struts `STRUT_W` 6 wide at the foot angles), then the 8 rounded pads (stadium in plan, R 45 .. 67, `BASE_H` 9 tall, rounded top) are added after the window cut so each strut flares into its pad. Rim top edges filleted.
- Pocket (one per pad): radial slot open at top, bottom and the outer end, from X = `POCKET_R_IN` (49) outward, half-width `POCKET_HW` (5.25), so the pad becomes a U. No roofs or bridges anywhere (the user rejected the earlier roofed tunnel as "flying material"). Each side wall has a groove, Z `GROOVE_Z0` 4 .. `GROOVE_Z1` 6, X 49.5 .. 58, 0.8 deep: flat top face (holds the foot down), 45 deg bottom. A tie bar (`TIE_X0` 60.5 .. +`TIE_L` 3, Z 0 .. `TIE_H` 1.6) joins the two U walls at the floor so they cannot splay open; the foot tongue has a matching underside notch (3.2 mm bridge when printed).
- Foot (built along +X): 10 mm wide tongue, Z 0 .. `BASE_H`, dropped into the pocket from above; it rests on the table. A 2.4 mm vertical fork slot, `FORK_L` 15 mm from the inner end, splits it into two prongs. Each prong carries a ridge (`RIDGE` 0.7 out, X 50 .. 57) with a flat top at Z 5.75 and a 45 deg ramp underneath: pressing the foot down squeezes the prongs, the ridges click into the grooves. Two ears (`EAR_H` 4 above the pad, `EAR_L` 6 long, rounded) on the prong ends: pinch them to release and lift the foot out. The spoke starts at the pad (concave root matching the pad end R 9 at X 58), curves sideways by `SPOKE_SWIRL` (12 deg), tapers 10 -> 7 mm wide and from ~9 to `RING_H` (6) tall along a smooth spline, and joins an arc (R 80 .. 88) spanning 360/`FEET` deg minus a 1 mm gap, with rounded ends and a rounded outer top edge (`RING_EDGE_R` 3.5). Tipping margin = `RING_R_OUT` (88 mm). Under a tipping load the ground pushes the foot up at the ring, so the groove tops carry the hold-down force (~2x the plant weight).

## Modelling gotchas

- Fillets on the foot (spline spoke + arc + revolved height envelope) fail even at 0.6 mm. Softness is built into the shape instead (spline height profile, rounded ring edge in the revolved envelope, rounded arc ends). Fillets only on simple pads/rings.
- Do not fuse solids that share faces (identical sweep caps, same cone surfaces): OCCT returns a null shape. Build the cup as one shell and cut windows out of it; keep added solids offset from the shell faces.
- Constant names are global: `LIP` (floor ledge) was once silently overwritten by a snap constant of the same name; the floor test caught it.
- Windows, pads and feet share the `FEET` count so struts land on pads. Changing `FEET` changes window width (arch radius = half the window width).

## Print pose

- Cup: upright as designed. Arch tops are round, the near-flat part at the crown is a short bridge. Pockets are open-top, grooves have a 0.8 mm flat overhang. No supports.
- Foot: flat as designed (vertical walls, ridge ramps 45 deg underneath). No supports.

Clearances: `FIT_CLEARANCE` 0.1 mm per side on the joint (0.25 printed loose). Print the cup and one foot first to check the fit.
