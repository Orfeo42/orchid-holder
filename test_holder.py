import math

import pytest
from build123d import Part, Rot, Vector

from holder import (
    BASE_T,
    BASE_H,
    GROOVE_Z0,
    GROOVE_Z1,
    POCKET_HW,
    CUP_H,
    FEET,
    POT_R0,
    WALL,
    RING_R_IN,
    RING_R_OUT,
    TIE_H,
    TIE_L,
    TIE_X0,
    TONGUE_X0,
    WINDOW_Z0,
    WINDOW_Z1,
    cup,
    foot,
    on_bed,
    pot,
    pot_inner_r,
)


@pytest.fixture(scope="module")
def cup_part() -> Part:
    return cup()


@pytest.fixture(scope="module")
def foot_part() -> Part:
    return foot()


def on_wall(deg: float, z: float) -> Vector:
    r = pot_inner_r(z) + WALL / 2
    a = math.radians(deg)
    return Vector(r * math.cos(a), r * math.sin(a), z)


def test_cup(cup_part: Part) -> None:
    bb = cup_part.bounding_box()
    assert cup_part.is_valid
    assert len(cup_part.solids()) == 1
    assert bb.min.Z == pytest.approx(0.0, abs=0.01)
    assert bb.max.Z == pytest.approx(CUP_H, abs=0.01)
    assert cup_part.volume < 45_000


def test_cup_floor_is_open(cup_part: Part) -> None:
    assert not cup_part.is_inside(Vector(0.0, 0.0, BASE_T / 2))
    assert not cup_part.is_inside(Vector(30.0, 0.0, BASE_T / 2))
    assert cup_part.is_inside(Vector(0.0, POT_R0 - 2.0, BASE_T / 2))


def test_cup_arches(cup_part: Part) -> None:
    window = 180.0 / FEET
    assert cup_part.is_inside(on_wall(0.0, 25.0))
    assert not cup_part.is_inside(on_wall(window, 25.0))
    assert not cup_part.is_inside(on_wall(window, WINDOW_Z1 - 1.0))
    assert cup_part.is_inside(on_wall(window, WINDOW_Z1 + 1.0))
    assert cup_part.is_inside(on_wall(window, WINDOW_Z0 - 2.0))


def test_cup_pocket(cup_part: Part) -> None:
    groove_z = (GROOVE_Z0 + GROOVE_Z1) / 2 + 0.3
    assert not cup_part.is_inside(Vector(60.0, 0.0, 1.0))
    assert not cup_part.is_inside(Vector(60.0, 0.0, BASE_H - 1.0))
    assert cup_part.is_inside(Vector(55.0, 7.5, 2.0))
    assert cup_part.is_inside(Vector(55.0, -7.5, 2.0))
    assert not cup_part.is_inside(Vector(54.0, POCKET_HW + 0.4, groove_z))
    assert cup_part.is_inside(Vector(54.0, POCKET_HW + 0.4, GROOVE_Z1 + 1.0))
    tie_x = TIE_X0 + TIE_L / 2
    assert cup_part.is_inside(Vector(tie_x, 0.0, TIE_H / 2))
    assert not cup_part.is_inside(Vector(tie_x, 0.0, TIE_H + 1.0))


def test_foot(foot_part: Part) -> None:
    bb = foot_part.bounding_box()
    assert foot_part.is_valid
    assert len(foot_part.solids()) == 1
    assert bb.min.Z == pytest.approx(0.0, abs=0.01)
    assert bb.max.X == pytest.approx(RING_R_OUT, abs=0.5)
    assert foot_part.is_inside(Vector((RING_R_IN + RING_R_OUT) / 2, 0.0, 1.0))
    assert foot_part.is_inside(Vector(TONGUE_X0 + 6.0, 3.0, 6.0))
    assert not foot_part.is_inside(Vector(TONGUE_X0 + 6.0, 0.0, 6.0))
    assert foot_part.is_inside(Vector(TONGUE_X0 + 3.0, 3.0, BASE_H + 2.0))
    assert foot_part.is_inside(Vector(53.0, 5.3, GROOVE_Z1 - 0.5))
    tie_x = TIE_X0 + TIE_L / 2
    assert not foot_part.is_inside(Vector(tie_x, 3.0, TIE_H / 2))
    assert foot_part.is_inside(Vector(tie_x, 3.0, TIE_H + 1.0))


def test_fit(cup_part: Part, foot_part: Part) -> None:
    neighbour = Rot(0, 0, 360.0 / FEET) * foot_part
    assert (cup_part & pot()).volume == pytest.approx(0.0, abs=1e-6)
    assert (cup_part & foot_part).volume == pytest.approx(0.0, abs=1e-6)
    assert (foot_part & neighbour).volume == pytest.approx(0.0, abs=1e-6)


def test_print_poses(cup_part: Part, foot_part: Part) -> None:
    for part in (on_bed(cup_part), on_bed(foot_part)):
        bb = part.bounding_box()
        assert part.is_valid
        assert bb.min.Z == pytest.approx(0.0, abs=0.01)
        assert (bb.min.X + bb.max.X) / 2 == pytest.approx(0.0, abs=0.01)
        assert (bb.min.Y + bb.max.Y) / 2 == pytest.approx(0.0, abs=0.01)
