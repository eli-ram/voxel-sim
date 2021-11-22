# version 430

// Adding Edge Value
layout(lines) in;
layout(line_strip, max_vertices = 2) out;

in vec4 position[2];

out float edge;

void main() {
    edge = 0.0;
    gl_Position = position[0];
    EmitVertex();

    edge = 1.0;
    gl_Position = position[1];
    EmitVertex();

    EndPrimitive();
}