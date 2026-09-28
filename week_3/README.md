# Week 3 — Absolute Radiance

    Raytracing with reflections and diffusion.

- **Spec:** [`week3.pdf`](./week3.pdf) — read it first, it is the authority.
- **Template:** [`main.py`](./main.py) — runs as-is, sets and integrates shader into main.py.
- **Template:** [`shader.frag`](./shader.frag) - basic seleton is provided, your task is to fill the missing logic

  Three `TODO` blocks: Ray-Sphere Intersection, tracking the closest hit, and material properties.

- **Setup:** see the [root README](../README.md).

**Due: EOD, 30th September 2026.**

## Your brief goes here

**Replace this file with your assignment brief.** It must contain your answers to
**Question 1** and **Question 2**.

> Question 1. In the ray_color loop, you must ensure rays do not intersect at exactly t = 0.0,
> but rather at a small offset like t = 0.001. If we set the minimum distance to 0.0, the image
> becomes covered in dark noise known as "shadow acne." Why does this happen?
> (Hint: Think about floating-point rounding errors when a ray bounces off a surface)

All our calculations are in finite precision and subject to floating-point rounding
rules when they cannot be represented exactly (mathematically speaking).
Shadow acne occurs when the hit point $\vec{P} = \vec{O} + t\vec{d}$ doesn't lie
exactly on the surface, but rather slightly inside or outside.

The bounced ray starts from $\vec{P}$, since it is slightly inside (or outside) the surface,
it will trigger a hit with the same surface again. This intersection results in a
very small value of $t$

With $t_min = 0$ this self-intersection is accepted, so the
ray is wrongly absorbed or re-scattered by the surface it just left,
producing dark speckles. Using $t_{\min} = 0.001$ rejects these near-zero hits,
since the error is much smaller than that threshold.

Essentially $t_{\min} = 0.001$ makes sure that each ray travels a particular distance
away from its origin to be considered.

> Question 2. In many CPU implementations of raytracing, the ray_color function calls
> itself recursively every time it hits an object to calculate the next bounce.
> In our GLSL fragment shader, we use a for loop instead. Why can’t we use standard
> recursive function calls inside a GPU shader?

Recursion requires a call stack that grows dynamically with recursion
depth. A GPU on the other hand, requires each thread's memory
requirements to be computed at compile time so a stack of unknown depth
per thread can't be supported.

GLSL therefore forbids recursion, which gives a static call graph, and
the compiler can inline all function calls into a single block of code
with control flow handled by jumps.

Some GPU API's do allow recursion but there is a depth limit, and it is not portable.
