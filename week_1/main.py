import pygame
import numpy as np
import random

# Configuration

WIDTH = 800
HEIGHT = 800

BOWL_CENTER = np.array([WIDTH / 2, HEIGHT / 2], dtype=float)
BOWL_RADIUS = 300

NUM_PARTICLES = 1

PARTICLE_RADIUS = 10
PARTICLE_SPEED = 500.0

# Pixels per second squared, not m/s^2. Note that +y points DOWN on screen.
GRAVITY = 500.0

# How much speed survives a bounce. 1.0 loses nothing, below 1.0 is weaker.
WALL_RESTITUTION = 1.0
RESTITUTION = 1.0

FPS = 60

COLORS = [
    (230,  25, 75),  ( 60, 180,  75), (255, 225,  25), (  0, 130, 200),
    (245, 130, 48),  (145,  30, 180), ( 70, 240, 240), (240,  50, 230),
    (210, 245, 60),  (250, 190, 212), (  0, 128, 128), (220, 190, 255),
    (170, 110, 40),  (255, 250, 200), (128,   0,   0), (170, 255, 195),
]

positions = []
velocities = []
colors = []

for i in range(NUM_PARTICLES):
    # A random spot inside the bowl, with the whole ball fitting.
    angle = random.uniform(0, 2 * np.pi)
    distance = random.uniform(0, BOWL_RADIUS - PARTICLE_RADIUS)

    positions.append(BOWL_CENTER + distance * np.array([
        np.cos(angle),
        np.sin(angle)
    ]))

    # assign colors from a pallate
    colors.append(COLORS[len(positions) % len(COLORS)])

    # A random direction, at roughly PARTICLE_SPEED.
    # Swap for np.array([0.0, 0.0]) to drop the ball from rest.
    angle = random.uniform(0, 2 * np.pi)

    velocities.append(PARTICLE_SPEED * np.array([
        np.cos(angle),
        np.sin(angle)
    ]))

# Pygame setup

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Particle Simulation")

clock = pygame.time.Clock()

running = True

# Main loop

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Seconds since the last frame. This is your timestep.
    dt = clock.tick(FPS) / 1000.0

    ###########################################################################
    # TODO: Make every ball fall, and bounce it off the wall of the bowl.     #
    #                                                                         #
    # Two things happen here, in an order that matters.                       #
    #                                                                         #
    # First, it falls. Gravity is an acceleration, so ask yourself what it    #
    # changes directly: the position, or the velocity? And once that has      #
    # changed, what does the ball's new position depend on?                   #
    #                                                                         #
    # Second, it has to stay in the bowl. Work out how you would even         #
    # tell that it has escaped, given that you know where the centre of       #
    # the bowl is, how wide the bowl is, and how wide the ball is.            #
    # Careful: the ball is drawn with a radius of its own, so its edge        #
    # reaches the wall before its centre would.                               #
    #                                                                         #
    # Once you know it has escaped, two things need fixing. Where should      #
    # the ball actually be, and what should its velocity become? For the      #
    # velocity, only the part heading into the wall should change. The        #
    # part sliding along the wall carries on untouched. WALL_RESTITUTION      #
    # decides how much of the incoming speed comes back out.                  #
    ###########################################################################

    for (v, r) in zip(velocities, positions):
        v[1] += GRAVITY * dt
        r += v * dt

        d = BOWL_CENTER - r
        d_mag = np.linalg.norm(d)

        # avoid division by zero
        if d_mag == 0:
            continue

        d_hat = d / d_mag

        if d_mag >= BOWL_RADIUS - PARTICLE_RADIUS:
            penetration = d_mag - (BOWL_RADIUS - PARTICLE_RADIUS)
            v -= (1 + WALL_RESTITUTION) * np.dot(v, d_hat) * d_hat
            r += d_hat * penetration

    ###########################################################################
    #                            END OF YOUR CODE                             #
    ###########################################################################

    ###########################################################################
    # TODO: Make the balls bounce off each other.                             #
    #                                                                         #
    # Start with the condition. Given two balls, what has to be true          #
    # about where they are for them to be touching? Every ball has the        #
    # same radius, which makes this simpler than it sounds.                   #
    #                                                                         #
    # Then the response. A collision changes velocities, not positions.       #
    # Which direction does the change act along, and how would you get        #
    # that direction from the two positions you have? Only the motion         #
    # along that direction matters, the rest is unaffected.                   #
    #                                                                         #
    # One trap worth thinking about: two balls that are overlapping but       #
    # already moving apart should be left alone. If you bounce them again     #
    # they will get stuck together. How would you tell "approaching"          #
    # from "separating"?                                                      #
    #                                                                         #
    # Finally, this has to happen for every pair of balls, not just one.      #
    ###########################################################################

    # CODE STARTS HERE.
    r = np.array(positions)

    # transpose and subtract to get displacements
    # :- thanks for the trick Bhuvnesh!
    s = r[:, None, :] - r[None, :, :]

    # s is a 3D matrix (N * N * 2) where 2 is x and y
    # normalize along last (axis=-1) to get distance matrix
    dist = np.linalg.norm(s, axis=-1) 

    # Had to lookup how to map lambdas on matricis,
    # numpy does weird overloading stuffs and creates
    # a matrix of booleans `colliding`
    is_colliding = dist < (2 * PARTICLE_RADIUS)

    # Only extract upper triangle of matrix,
    # since | r_i - r_j | = | r_j - r_i |
    # k = 1 to skip diagonal row (ie. i = j)
    collisions = np.argwhere(np.triu(is_colliding, k=1))

    for i,j in collisions:
        v_i, v_j = (velocities[i], velocities[j])
        vrel = v_i - v_j
        n = s[i,j] / np.linalg.norm(s[i, j])

        if np.dot(vrel, n) > 0:
            continue

        vrel_n = np.dot(vrel, n)

        velocities[i] = v_i - RESTITUTION * vrel_n * n
        velocities[j] = v_j + RESTITUTION * vrel_n * n

        penetration = (2 * PARTICLE_RADIUS) - dist[i, j]
        offset = (penetration / 2) * n
        positions[i] += offset
        positions[j] -= offset

    ###########################################################################
    #                            END OF YOUR CODE                             #
    ###########################################################################

    # Render

    screen.fill((20, 20, 25))

    pygame.draw.circle(
        screen,
        (180, 180, 180),
        BOWL_CENTER.astype(int),
        BOWL_RADIUS,
        width=3
    )

    for color, position in zip(colors, positions):
        pygame.draw.circle(
            screen,
            color,
            position.astype(int),
            PARTICLE_RADIUS
        )

    pygame.display.flip()
    raw = pygame.image.tostring(screen, 'RGBA')

pygame.quit()
