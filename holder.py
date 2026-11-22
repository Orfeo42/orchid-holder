import math
from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    BuildLine,
    BuildSketch,
    Circle,
    Compound,
    Cone,
    Cylinder,
    Part,
    Plane,
    Locations,
    Polygon,
    Polyline,
    Pos,
    Rot,
    Sketch,
    SlotCenterToCenter,
    Spline,
    ThreePointArc,
    export_step,
    export_stl,
    extrude,
    fillet,
    make_face,
    revolve,
)

POT_BOTTOM_D = 86.0
POT_TOP_CIRC = 340.0
POT_H = 105.0
POT_TOP_D = POT_TOP_CIRC / math.pi
POT_TAPER = (POT_TOP_D - POT_BOTTOM_D) / 2 / POT_H

POT_CLEARANCE = 0.3
POT_R0 = POT_BOTTOM_D / 2 + POT_CLEARANCE
FIT_CLEARANCE = 0.1

BASE_T = 2.5
LIP = 5.0
CUP_H = 50.0
WALL = 2.4
RIM_FILLET = 1.0
STRUT_W = 6.0
WINDOW_Z0 = 6.5
WINDOW_Z1 = CUP_H - 5.0

FEET = 8
CORE_H = 5.0
CORE_FILLET = 2.0
LOBE_R = 9.0
LOBE_FILLET = 3.0

BASE_H = 9.0
POCKET_R_IN = POT_R0 + 5.5
CORE_R = POCKET_R_IN - 1.0
LOBE_IN = POCKET_R_IN - 4.0
LOBE_C = POCKET_R_IN + 9.0
POCKET_W = 10.0
FORK_GAP = 2.4
FORK_L = 15.0
GROOVE_Z0 = 4.0
GROOVE_Z1 = 6.0
GROOVE_D = 0.8
GROOVE_X0 = POCKET_R_IN + 0.5
GROOVE_X1 = POCKET_R_IN + 9.0
RIDGE = 0.7
RIDGE_H = 0.6
RIDGE_X0 = POCKET_R_IN + 1.0
RIDGE_X1 = POCKET_R_IN + 8.0
EAR_H = 4.0
EAR_L = 6.0
EAR_FILLET = 1.5
TIE_X0 = POCKET_R_IN + 11.5
TIE_L = 3.0
TIE_H = 1.6
NOTCH_GAP_X = 0.4
NOTCH_GAP_Z = 0.5

RING_R_IN = POT_R0 + 36.5
RING_R_OUT = POT_R0 + 44.5
RING_H = 6.0
RING_GAP = 1.0
SPOKE_W_ROOT = 10.0
SPOKE_W_RING = 7.0
SPOKE_SWIRL = 12.0
RING_EDGE_R = 3.5

TONGUE_X0 = POCKET_R_IN + FIT_CLEARANCE
POCKET_HW = POCKET_W / 2 + FIT_CLEARANCE


def pot_inner_r(z: float) -> float:
    return POT_R0 + POT_TAPER * (z - BASE_T)


def as_part(shape: object, what: str) -> Part:
    if not isinstance(shape, Part):
        raise TypeError(f"{what} did not return a part")
    return shape


def as_sketch(shape: object, what: str) -> Sketch:
    if not isinstance(shape, Sketch):
        raise TypeError(f"{what} did not build a sketch")
    return shape


def polar(r: float, deg: float) -> tuple[float, float]:
    a = math.radians(deg)
    return (r * math.cos(a), r * math.sin(a))


def section_prism(points: list[tuple[float, float]], x0: float, x1: float) -> Part:
    with BuildSketch(Plane.YZ.offset(x0)) as sk:
        Polygon(*points, align=None)
    return as_part(extrude(as_sketch(sk.sketch, "section prism"), amount=x1 - x0), "section prism")


def side_prism(points: list[tuple[float, float]], width: float) -> Part:
    with BuildSketch(Plane.XZ) as sk:
        Polygon(*points, align=None)
    return as_part(extrude(as_sketch(sk.sketch, "side prism"), amount=width / 2, both=True), "side prism")


def pot_cone(z0: float, z1: float, dr: float) -> Part:
    return Pos(0.0, 0.0, z0) * Cone(
        pot_inner_r(z0) + dr,
        pot_inner_r(z1) + dr,
        z1 - z0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


def window(angle: float) -> Part:
    step = 2 * math.pi / FEET
    w0 = (pot_inner_r(WINDOW_Z0) + WALL / 2) * step - STRUT_W
    w1 = (pot_inner_r(WINDOW_Z1) + WALL / 2) * step - STRUT_W
    spring = WINDOW_Z1 - w1 / 2
    with BuildSketch(Plane.YZ) as sk:
        Polygon((-w0 / 2, WINDOW_Z0), (w0 / 2, WINDOW_Z0), (w1 / 2, spring), (-w1 / 2, spring), align=None)
        with Locations((0.0, spring)):
            Circle(w1 / 2)
    r_mid = pot_inner_r((WINDOW_Z0 + WINDOW_Z1) / 2) + WALL / 2
    slab = as_part(extrude(as_sketch(sk.sketch, "window"), amount=8.0, both=True), "window extrude")
    return Rot(0, 0, angle) * (Pos(r_mid, 0.0, 0.0) * slab)


def rounded_pad(outline: Sketch, height: float, radius: float) -> Part:
    pad = as_part(extrude(outline, amount=height), "pad extrude")
    top = pad.edges().filter_by_position(Axis.Z, height - 0.01, height + 0.01)
    return as_part(fillet(top, radius=radius), "pad fillet")


def lobe() -> Part:
    inner_c = LOBE_IN + LOBE_R
    with BuildSketch() as sk:
        with Locations(((inner_c + LOBE_C) / 2, 0.0)):
            SlotCenterToCenter(LOBE_C - inner_c, 2 * LOBE_R)
    return rounded_pad(as_sketch(sk.sketch, "lobe"), BASE_H, LOBE_FILLET)


def pocket() -> Part:
    slot = Pos(POCKET_R_IN, 0.0, -1.0) * Box(
        LOBE_C + LOBE_R + 5.0 - POCKET_R_IN,
        2 * POCKET_HW,
        BASE_H + 2.0,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    for s in (1.0, -1.0):
        groove = section_prism(
            [
                (s * (POCKET_HW - 0.5), GROOVE_Z0),
                (s * POCKET_HW, GROOVE_Z0),
                (s * (POCKET_HW + GROOVE_D), GROOVE_Z0 + GROOVE_D),
                (s * (POCKET_HW + GROOVE_D), GROOVE_Z1),
                (s * (POCKET_HW - 0.5), GROOVE_Z1),
            ],
            GROOVE_X0,
            GROOVE_X1,
        )
        slot = slot + groove
    tie = Pos(TIE_X0, 0.0, -1.0) * Box(
        TIE_L, 2 * POCKET_HW + 2.0, TIE_H + 1.0, align=(Align.MIN, Align.CENTER, Align.MIN)
    )
    return as_part(slot - tie, "pocket")


def core() -> Part:
    with BuildSketch() as sk:
        Circle(CORE_R)
    return rounded_pad(as_sketch(sk.sketch, "core"), CORE_H, CORE_FILLET)


def cup() -> Part:
    cavity = pot_cone(BASE_T, CUP_H + 1.0, 0.0)
    floor_hole = Pos(0.0, 0.0, -1.0) * Cylinder(
        POT_R0 - LIP, BASE_T + 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    body = as_part(pot_cone(0.0, CUP_H, WALL) + core() - cavity - floor_hole, "cup shell")
    for i in range(FEET):
        body = as_part(body - window(180.0 / FEET + 360.0 * i / FEET), "window cut")
    for i in range(FEET):
        body = as_part(body + Rot(0, 0, 360.0 * i / FEET) * lobe(), "pad union")
    for i in range(FEET):
        body = as_part(body - Rot(0, 0, 360.0 * i / FEET) * pocket(), "pocket cut")
    top = body.edges().filter_by_position(Axis.Z, CUP_H - 0.01, CUP_H + 0.01)
    return as_part(fillet(top, radius=RIM_FILLET), "rim fillet")


def tongue() -> Part:
    hw = POCKET_W / 2
    ear_x1 = TONGUE_X0 + EAR_L
    ear_top = BASE_H + EAR_H
    body = side_prism(
        [
            (TONGUE_X0, 0.0),
            (LOBE_C + LOBE_R + 1.0, 0.0),
            (LOBE_C + LOBE_R + 1.0, BASE_H),
            (ear_x1, BASE_H),
            (ear_x1, ear_top),
            (TONGUE_X0, ear_top),
        ],
        POCKET_W,
    )
    ear_edges = body.edges().filter_by(Axis.Y).filter_by_position(Axis.Z, ear_top - 0.01, ear_top + 0.01)
    result = as_part(fillet(ear_edges, radius=EAR_FILLET), "ear fillet")
    fork = Pos(TONGUE_X0 - 1.0, 0.0, -1.0) * Box(
        FORK_L + 1.0, FORK_GAP, ear_top + 2.0, align=(Align.MIN, Align.CENTER, Align.MIN)
    )
    result = as_part(result - fork, "fork")
    top = GROOVE_Z1 - FIT_CLEARANCE
    for s in (1.0, -1.0):
        lip = section_prism(
            [
                (s * (hw - 0.3), top),
                (s * (hw + RIDGE), top),
                (s * (hw + RIDGE), top - RIDGE_H),
                (s * hw, top - RIDGE_H - RIDGE),
                (s * (hw - 0.3), top - RIDGE_H - RIDGE),
            ],
            RIDGE_X0,
            RIDGE_X1,
        )
        result = as_part(result + lip, "lip")
    notch = Pos(TIE_X0 - NOTCH_GAP_X, 0.0, -1.0) * Box(
        TIE_L + 2 * NOTCH_GAP_X,
        POCKET_W + 2 * RIDGE + 2.0,
        TIE_H + NOTCH_GAP_Z + 1.0,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    return as_part(result - notch, "tie notch")


def height_envelope() -> Part:
    crest = RING_R_OUT - RING_EDGE_R
    edge = (RING_R_OUT + 0.3, RING_H - RING_EDGE_R)
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine():
            Spline((LOBE_C, BASE_H), (crest, RING_H), tangents=[(1.0, 0.0), (1.0, 0.0)])
            Spline((crest, RING_H), edge, tangents=[(1.0, 0.0), (0.0, -1.0)])
            Polyline(edge, (edge[0], -1.0), (0.0, -1.0), (0.0, BASE_H), (LOBE_C, BASE_H))
        make_face()
    return revolve(as_sketch(sk.sketch, "envelope"), axis=Axis.Z)


def ring_arc() -> Part:
    r_mid = (RING_R_IN + RING_R_OUT) / 2
    cap = (RING_R_OUT - RING_R_IN) / 2
    half = 180.0 / FEET - math.degrees((RING_GAP / 2 + cap) / r_mid)

    def cap_apex(deg: float, sign: float) -> tuple[float, float]:
        return polar(math.hypot(r_mid, cap), deg + sign * math.degrees(math.atan2(cap, r_mid)))

    with BuildSketch() as sk:
        with BuildLine():
            ThreePointArc(polar(RING_R_OUT, -half), polar(RING_R_OUT, 0.0), polar(RING_R_OUT, half))
            ThreePointArc(polar(RING_R_OUT, half), cap_apex(half, 1.0), polar(RING_R_IN, half))
            ThreePointArc(polar(RING_R_IN, half), polar(RING_R_IN, 0.0), polar(RING_R_IN, -half))
            ThreePointArc(polar(RING_R_IN, -half), cap_apex(-half, -1.0), polar(RING_R_OUT, -half))
        make_face()
    return as_part(extrude(as_sketch(sk.sketch, "ring arc"), amount=BASE_H + 1.0), "ring arc")


def spoke_centre(t: float) -> tuple[float, float]:
    r_end = (RING_R_IN + RING_R_OUT) / 2
    return polar(LOBE_C + t * (r_end - LOBE_C), SPOKE_SWIRL * t * t)


def spoke() -> Part:
    steps = 8
    left: list[tuple[float, float]] = []
    right: list[tuple[float, float]] = []
    for k in range(steps + 1):
        t = k / steps
        cx, cy = spoke_centre(t)
        ax, ay = spoke_centre(min(t + 0.01, 1.0))
        bx, by = spoke_centre(max(t - 0.01, 0.0))
        tl = math.hypot(ax - bx, ay - by)
        nx, ny = -(ay - by) / tl, (ax - bx) / tl
        hw = (SPOKE_W_ROOT + t * (SPOKE_W_RING - SPOKE_W_ROOT)) / 2
        left.append((cx + nx * hw, cy + ny * hw))
        right.append((cx - nx * hw, cy - ny * hw))
    with BuildSketch() as sk:
        with BuildLine():
            Spline(*left)
            Polyline(left[-1], right[-1])
            Spline(*reversed(right))
            Polyline(right[0], left[0])
        make_face()
    return as_part(extrude(as_sketch(sk.sketch, "spoke"), amount=BASE_H + 1.0), "spoke")


def foot() -> Part:
    shaped = as_part((spoke() + ring_arc()) & height_envelope(), "foot envelope")
    lobe = Pos(LOBE_C, 0.0, -1.0) * Cylinder(
        LOBE_R + FIT_CLEARANCE, BASE_H + 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    return as_part(shaped - lobe + tongue(), "foot")


def assembly() -> Compound:
    feet = [Rot(0, 0, 360.0 * i / FEET) * foot() for i in range(FEET)]
    return Compound(children=[cup(), *feet])


def pot() -> Part:
    return Pos(0.0, 0.0, BASE_T) * Cone(
        POT_BOTTOM_D / 2,
        POT_TOP_D / 2,
        POT_H,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


def on_bed(part: Part) -> Part:
    bb = part.bounding_box()
    return Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z) * part


if __name__ == "__main__":
    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    c = on_bed(cup())
    f = on_bed(foot())
    for name, part in (("cup", c), ("foot", f)):
        bb = part.bounding_box()
        print(
            f"{name}: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm"
            f"  vol={part.volume / 1000:.1f} cm3  valid={part.is_valid}  solids={len(part.solids())}"
        )
        export_stl(part, str(out / f"{name}.stl"))
        export_step(part, str(out / f"{name}.step"))
    export_stl(assembly(), str(out / "assembly.design.stl"))
    export_stl(pot(), str(out / "pot.design.stl"))
    print(f"min tipping distance from centre: {RING_R_OUT:.0f} mm")
