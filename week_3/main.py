"""Week 3 — Absolute Radiance.

Your task: You do not need to edit this file!
This script sets up a Pygame window, creates a graphics card context using ModernGL, 
and draws a single flat rectangle (a Quad) that covers the entire screen. 

It passes two variables to your Fragment Shader every frame:
  1. u_resolution (vec2) - Screen width and height
  2. u_time (float) - Elapsed time in seconds

Run it:  uv run python main.py
(Keep this running! It will automatically hot-reload when you save your shader.)
"""

import os
import sys
import pygame
import moderngl
import numpy as np

# A smaller resolution is highly recommended for path tracing 
# to keep the frame rate smooth while calculating multiple bounces.
WINDOW_SIZE = (800, 450) 
SHADER_FILE = "shader.frag"

# The Vertex Shader: Runs once for each of our 4 corners to draw a flat canvas.
VERTEX_SHADER = """
#version 330 core
in vec2 in_position;
void main() {
    gl_Position = vec4(in_position, 0.0, 1.0);
}
"""

def load_shader(ctx: moderngl.Context, frag_path: str, old_prog=None):
    """Compiles the GLSL code. If there's a syntax error, it prints it and keeps the old shader running."""
    try:
        with open(frag_path, 'r') as f:
            frag_source = f.read()
        return ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=frag_source)
    except Exception as e:
        print(f"\n[GLSL SYNTAX ERROR] >>>\n{e}")
        return old_prog

def main() -> None:
    pygame.init()
    
    # Request an OpenGL 3.3 Core context
    pygame.display.set_mode(WINDOW_SIZE, pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Ray Tracing in One Weekend - GPU Edition")
    
    ctx = moderngl.create_context()
    
    # Define the 4 corners of our screen canvas (X, Y from -1.0 to 1.0)
    vertices = np.array([
        -1.0, -1.0,  
         1.0, -1.0,  
        -1.0,  1.0,  
         1.0,  1.0,  
    ], dtype='f4')
    
    vbo = ctx.buffer(vertices.tobytes())
    
    if not os.path.exists(SHADER_FILE):
        print(f"Error: {SHADER_FILE} not found. Please create it in the same directory.")
        sys.exit()
        
    prog = load_shader(ctx, SHADER_FILE)
    if not prog:
        sys.exit()
        
    vao = ctx.vertex_array(prog, [(vbo, '2f', 'in_position')])
    last_mod_time = os.path.getmtime(SHADER_FILE)

    clock = pygame.time.Clock()
    start_ticks = pygame.time.get_ticks()
    running = True

    print("Engine running! Open shader.frag and start writing the shader.")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        # --- HOT RELOADING ---
        current_mod_time = os.path.getmtime(SHADER_FILE)
        if current_mod_time != last_mod_time:
            new_prog = load_shader(ctx, SHADER_FILE, prog)
            if new_prog != prog:
                prog = new_prog
                vao = ctx.vertex_array(prog, [(vbo, '2f', 'in_position')])
                print("Shader successfully compiled!")
            last_mod_time = current_mod_time

        # --- PASS DATA TO GPU ---
        current_time = (pygame.time.get_ticks() - start_ticks) / 1000.0
        
        if 'u_resolution' in prog:
            prog['u_resolution'].value = WINDOW_SIZE
        if 'u_time' in prog:
            prog['u_time'].value = current_time

        # --- RENDER ---
        ctx.clear(0.0, 0.0, 0.0)
        vao.render(moderngl.TRIANGLE_STRIP)
        pygame.display.flip()
        
        # Cap at 60 FPS so their laptops don't take flight
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
