# Week 2 — The Sandbox

Cellular automata with falling sand and water.

- **Spec:** [`week2.pdf`](./week2.pdf) — read it first, it is the authority.
- **Template:** [`temp.py`](./temp.py) — runs as-is, but the physics is missing.
  One `NotImplementedError` in `SandSim.update()`: sand fall/slide and water
  spread. Fire, smoke, and wood are the bonus.
- **Setup:** see the [root README](../README.md).

**Due: EOD, 23rd September 2026.**

## Answers to in-text questions

> Question 1. Why does the swap grid start as a copy of the current state, rather
> than being filled with zeros? What would happen to a grain that does not move
> if G' started empty?

A swap grid is written to while the original grid is read from. If the swap grid
started empty, then only the cells that moved would be written to it and the rest
wouldn't appear in the new grid.

> Question 2. Remove the randomised column order and replace it with a fixed left-to-right
> scan. Run the simulation for a few hundred ticks. What happens to the shape of a sand pile?
> Why?

It appears that the particles prefer falling toward a particular direction.
The final shape of the sand pile is not drastically different but the movement
of the sand appears off.
This is because a fixed left-to-right scan introduces some 'bias'.
