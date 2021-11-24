#version 430

layout (location = 1) uniform vec4 COLOR;

// in float edge;

out vec4 frag_color;

void main()
{
    // float I = abs(edge - 0.5) * 2.0;
    vec4 color = COLOR;
    // color.rgb *= mix(1.0, 0.0, smoothstep(0.75, 0.95, I));
    frag_color = color;
}