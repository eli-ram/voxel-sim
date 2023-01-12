#version 430

// Uniforms
layout (location = 0) uniform float delta;

in FragmentData {
    float gray;
};

out vec4 color;

vec3 curr = vec3(1, 5, 0) / 255;
vec3 prev = vec3(1, 0, 5) / 255;

void main() {
    color = vec4(mix(curr, prev, gray) * 1.0, 0.0);
}