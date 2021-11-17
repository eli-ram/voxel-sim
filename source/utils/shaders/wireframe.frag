#version 430

layout (location = 1) uniform vec4 COLOR;

out vec4 frag_color;

void main()
{
    frag_color = COLOR;
}