#version 430

layout (location = 0) uniform vec2 aspect;

in vec2 pos;
out vec2 uv;

void main() {
    uv = 0.5 + pos * 0.5; // Bad magic dependency
	gl_Position = vec4(pos * aspect, 0.0, 1.0);
}