#version 430

layout (location = 0) in vec3 pos;
layout (location = 1) in vec3 offset;
layout (location = 0) uniform mat4 MVP;
layout (location = 1) uniform float DEFORMATION;

// Forward useful information
out vec3 original_pos;
out vec3 deformed_pos;

void main() {
    vec3 cur = pos + (offset * DEFORMATION);
    // Export data
    original_pos = pos;
    deformed_pos = cur;
    // Set position
    gl_Position = MVP * vec4(cur, 1);
}