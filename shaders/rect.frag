#version 430

layout (binding = 0) uniform sampler2D src;

in vec2 uv;
out vec4 color;

void main() {
    vec4 c = texture(src, uv);
    // c.r = smoothstep(c.r, max(c.r, 0.05), 0.01) - c.r;
    c.r *= 1.5;
    color = c * 10.0;
}