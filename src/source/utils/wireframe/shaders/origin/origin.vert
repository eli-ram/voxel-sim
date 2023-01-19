#version 430

// Uniforms
layout (location = 0) in vec3 pos;
layout (location = 0) uniform mat4 MVP;

void main() {
    // Set position
    gl_Position = MVP * vec4(pos, 1);
}