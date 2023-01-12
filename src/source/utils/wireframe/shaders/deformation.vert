#version 430

layout (location = 0) in vec3 pos;
layout (location = 1) in vec3 offset;
layout (location = 0) uniform mat4 MVP;
layout (location = 1) uniform float DEFORMATION;

void main() {
    vec3 current = pos + (offset * DEFORMATION);
    gl_Position = MVP * vec4(current, 1);
}