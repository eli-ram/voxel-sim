#version 430

in vec3 color;
out vec4 frag_color;

void main()
{
    // Emit color
    frag_color = color;
}