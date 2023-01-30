#version 430

layout (location = 2) uniform vec4 COLOR;

in float dist;
in float edge;
out vec4 frag_color;

void main()
{
    float I = dist - abs(edge - dist);
    vec4 color = COLOR;
    // Make section of edge close to the node dark
    color.rgb *= smoothstep(0.01, 0.05, I);
    frag_color = color;
}