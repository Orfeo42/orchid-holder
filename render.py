from pathlib import Path

import pyvista as pv

pv.OFF_SCREEN = True

Cam = list[tuple[float, float, float]]


def bed(size: float) -> pv.PolyData:
    return pv.Plane(center=(0, 0, -0.3), i_size=size, j_size=size)


def render_print(stl: Path, out: Path, bed_size: float, scale: float) -> None:
    mesh = pv.read(str(stl))
    b = mesh.bounds
    sx, sy, sz = b[1] - b[0], b[3] - b[2], b[5] - b[4]
    d = bed_size
    cams: dict[str, Cam] = {
        "iso": [(d, -d, d * 0.8), (0, 0, sz / 2), (0, 0, 1)],
        "top": [(0, 0, d * 2), (0, 0, 0), (0, 1, 0)],
        "side": [(0, -d * 2, sz / 2), (0, 0, sz / 2), (0, 0, 1)],
        "front": [(d * 2, 0, sz / 2), (0, 0, sz / 2), (0, 0, 1)],
    }
    pl = pv.Plotter(shape=(2, 2), window_size=[1400, 1200], off_screen=True)
    for i, (name, cam) in enumerate(cams.items()):
        pl.subplot(i // 2, i % 2)
        pl.add_text(name, font_size=11)
        pl.add_mesh(bed(bed_size), color="#2f3540")
        pl.add_mesh(mesh, color="lightgrey", smooth_shading=False)
        pl.camera_position = cam
        pl.camera.parallel_projection = name != "iso"
        pl.camera.parallel_scale = scale
    pl.subplot(0, 0)
    pl.add_text(f"print pose {sx:.1f} x {sy:.1f} x {sz:.1f} mm - no brim", position="lower_left", font_size=11)
    pl.screenshot(str(out))
    pl.close()


def render_assembly(stl: Path, pot_stl: Path, out: Path) -> None:
    mesh = pv.read(str(stl))
    pot = pv.read(str(pot_stl))
    cams: dict[str, Cam] = {
        "iso": [(260, -300, 220), (0, 0, 40), (0, 0, 1)],
        "iso, no pot": [(260, -300, 220), (0, 0, 20), (0, 0, 1)],
        "top": [(0, 0, 500), (0, 0, 0), (0, 1, 0)],
        "side": [(0, -500, 60), (0, 0, 60), (0, 0, 1)],
    }
    pl = pv.Plotter(shape=(2, 2), window_size=[1400, 1200], off_screen=True)
    for i, (name, cam) in enumerate(cams.items()):
        pl.subplot(i // 2, i % 2)
        pl.add_text(name, font_size=11)
        pl.add_mesh(bed(340), color="#2f3540")
        pl.add_mesh(mesh, color="#8fbf7f", smooth_shading=False)
        if name != "iso, no pot":
            pl.add_mesh(pot, color="#d9d9ff", opacity=0.35)
        pl.camera_position = cam
        pl.camera.parallel_projection = name in ("top", "side")
        pl.camera.parallel_scale = 155.0
    pl.screenshot(str(out))
    pl.close()


if __name__ == "__main__":
    out_dir = Path(__file__).parent / "out"
    render_print(out_dir / "cup.stl", out_dir / "cup.png", 180, 72.0)
    render_print(out_dir / "foot.stl", out_dir / "foot.png", 110, 48.0)
    render_assembly(out_dir / "assembly.design.stl", out_dir / "pot.design.stl", out_dir / "assembly.png")
