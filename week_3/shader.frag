#version 330 core

uniform vec2 u_resolution;
uniform float u_time;

out vec4 fragColor;

// (Math & Randomness)
float rand(inout float seed) {
    float result = fract(sin(seed) * 43758.5453123);
    seed += 1.0;
    return result;
}

vec3 random_unit_vector(inout float seed) {
    // Rejection sampling for a random vector in a unit sphere
    for(int i = 0; i < 10; i++) {
        vec3 p = vec3(rand(seed), rand(seed), rand(seed)) * 2.0 - 1.0;
        if(dot(p, p) < 1.0) return normalize(p);
    }
    return vec3(0.0, 1.0, 0.0); // Fallback
}

struct Ray {
    vec3 origin;
    vec3 direction;
};

vec3 ray_at(Ray r, float t) {
    return r.origin + t * r.direction;
}

// Materials: 0 = Lambertian (Diffuse), 1 = Metal (Reflective)
struct Material {
    int type;
    vec3 albedo;
    float fuzz;
};

struct HitRecord {
    float t;
    vec3 p;
    vec3 normal;
    bool front_face;
    Material mat;
};

struct Sphere {
    vec3 center;
    float radius;
    Material mat;
};

// MILESTONE 1: THE INTERSECTION

bool hit_sphere(Ray r, vec3 center, float radius, Material mat, float t_min, float t_max, out HitRecord rec) {
    vec3 c = r.origin - center;
    vec3 d = r.direction;
    float D = 4 * (dot(d, c) * dot(d, c)) - 4 * dot(d, d) * (dot(c, c) - radius * radius);
    if (D <= 0)
        return false;

    // float t = (-2 * dot(d, c) + sqrt(D)) / (2 * dot(d, d);
    float t = (-2 * dot(d, c) - sqrt(D)) / (2 * dot(d, d));
    if (t < t_min || t > t_max)
        return false;

    vec3 p = r.origin + t * d;
    vec3 n = (p - center) / radius;


    rec.t = t;
    rec.p = p;
    rec.normal = n;
    rec.front_face = true;
    rec.mat = mat;

    return true;
}

bool hit_world(Ray r, out HitRecord rec) {
    bool hit_anything = false;
    float closest_so_far = 10000.0;
    HitRecord temp_rec;
    float t_min = 0.001;

    // Hardcoded scene
    Material mat_ground = Material(0, vec3(0.8, 0.8, 0.0), 0.0);
    Material mat_center = Material(0, vec3(0.7, 0.3, 0.3), 0.0);
    Material mat_left   = Material(1, vec3(0.8, 0.8, 0.8), 0.3); // Metal
    Material mat_right  = Material(1, vec3(0.8, 0.6, 0.2), 0.0); // Metal

    Sphere spheres[4] = Sphere[4](
        Sphere(vec3(0.0, -100.5, -1.0), 100, mat_ground),
        Sphere(vec3(0.0, 0.0, -1.0), 0.5, mat_center),
        Sphere(vec3(-1.0, 0.0, -1.0), 0.5, mat_left),
        Sphere(vec3(1.0, 0.0, -1.0), 0.5, mat_right)
    );

    float p_length = 0.0;
    for (int i = 0; i < 4; i++) {
        if (hit_sphere(r, spheres[i].center, spheres[i].radius, spheres[i].mat, t_min, closest_so_far, temp_rec)) {
            hit_anything = true;
            closest_so_far = temp_rec.t;
            rec = temp_rec;
        }
    }

    rec = temp_rec;
    return hit_anything;
}

// MILESTONE 2: LIGHT TRANSPORT (THE RAY TRACER)

vec3 ray_color(Ray r, inout float seed) {
    vec3 final_color = vec3(0.0);
    vec3 attenuation = vec3(1.0);
    
    // We cannot use recursion in GLSL, so we loop for a maximum of 4 bounces.
    for (int i = 0; i < 4; i++) {
        HitRecord rec;
        if (hit_world(r, rec)) {
            r.origin = rec.p;

            if (rec.mat.type == 0) { /* Lambertian */
                r.direction = rec.p + rec.normal + random_unit_vector(seed);
            } else { /* Metallic */
                r.direction = r.direction - 2 * dot(r.direction, rec.normal) * rec.normal;
                r.direction += random_unit_vector(seed) * rec.mat.fuzz;
            }

            attenuation *= rec.mat.albedo;
        } else {
            // Sky gradient (We hit nothing!)
            vec3 unit_direction = normalize(r.direction);
            float t = 0.5 * (unit_direction.y + 1.0);
            vec3 sky = mix(vec3(1.0, 1.0, 1.0), vec3(0.5, 0.7, 1.0), t);
            
            final_color = attenuation * sky;
            break; // Stop bouncing, we flew off into the sky.
        }
    }
    
    return final_color;
}

// MAIN RENDERER (Anti-Aliasing setup)

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;
    
    // Generate a unique random seed for this exact pixel and time
    float seed = gl_FragCoord.x * 19.19 + gl_FragCoord.y * 71.71 + u_time * 113.13;
    
    // Camera setup
    vec3 origin = vec3(0.0, 0.0, 0.0);
    
    vec3 pixel_color = vec3(0.0);
    int samples_per_pixel = 1000;
    
    // Accumulate light for multiple samples to create anti-aliasing
    for(int s = 0; s < samples_per_pixel; s++) {
        // Jitter the UV slightly for anti-aliasing
        vec2 jittered_uv = uv + vec2(rand(seed), rand(seed)) * 0.002;
        vec3 direction = normalize(vec3(jittered_uv, -1.0));
        
        Ray r = Ray(origin, direction);
        pixel_color += ray_color(r, seed);
    }
    
    // Average the samples and apply Gamma 2.0 correction
    pixel_color /= float(samples_per_pixel);
    pixel_color = sqrt(pixel_color);
    
    fragColor = vec4(pixel_color, 1.0);
}
