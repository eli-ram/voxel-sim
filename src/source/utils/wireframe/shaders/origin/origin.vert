#version 430

// Uniforms
layout (location = 0) uniform mat4 MVP;

void main() {
    // Set position @ origin
    gl_Position = MVP * vec4(0, 0, 0, 1);
}