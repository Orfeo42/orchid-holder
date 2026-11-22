# orchid-holder

3D-printable modular holder for an orchid pot (80 mm bottom diameter, 100 mm diameter at 80 mm up the slanted side). A low cup with round-arched windows grips the bottom of the pot, and eight curved snap-in feet form a ring around it so the top-heavy plant does not tip over. Modelled in Python with [build123d](https://github.com/gumyr/build123d).

## Shape

- Cup: 50 mm tall, a tight fit (0.3 mm gap) around the bottom of the pot; a thin shell with 8 tall round-arched windows, so the sides are mostly open. Each of the 8 struts flares into a rounded pad at the base. The pot sits on a 5 mm inner ledge and the centre of the floor is open.
- Feet: 8 by default. Each is a short curved spoke ending in an arc; together the arcs form a ring of 176 mm diameter around the pot, so the plant can lean up to 88 mm off centre in any direction before tipping.
- Joint: each rounded pad at the cup base has an open-top slot. Press the foot's tongue down into it until it clicks: two ridges on the tongue snap into grooves in the slot walls and hold the foot down. To remove a foot, pinch the two small tabs sticking up from the tongue and lift.

## Build

Requires [uv](https://docs.astral.sh/uv/).

```sh
uv run python holder.py   # writes out/*.stl, out/*.step (~10 s)
uv run python render.py   # writes out/*.png previews
uv run pytest             # geometry and fit tests
```

- `out/cup.stl`, `out/foot.stl` (+ `.step`): print pose, ready to slice. Print 1 cup and 8 feet.
- `out/assembly.design.stl`, `out/pot.design.stl`: assembled pose, for reference.

## Printing

- Both parts print as they stand, with no supports and no brim.
- PETG flexes better than PLA for the snap prongs. Assemble on a flat table: the feet click in when the tongue reaches the table. Print the cup and one foot first to check the joint fit, then the other feet.

## Customising

All dimensions are constants at the top of `holder.py`: pot size, clearances, cup height, strut width, window height, number of feet (also sets the number of arches), ring radius and height, spoke swirl, snap geometry. Change them, rerun `holder.py`, and update the expected values in `test_holder.py`.

## License

Public domain, under [The Unlicense](LICENSE).
