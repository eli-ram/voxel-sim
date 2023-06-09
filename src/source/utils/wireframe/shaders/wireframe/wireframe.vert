#version 430

layout (location = 0) in vec3 pos;
layout (location = 0) uniform mat4 MVP;

// out vec4 position;

void main() {
    gl_Position = MVP * vec4(pos, 1);
}