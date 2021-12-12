# version 430

// Adding Edge Value that is varying over the edge
layout(lines) in;
layout(line_strip, max_vertices = 2) out;

out float dist;
out float edge;

void main() {
    dist = distance(gl_in[0].gl_Position, gl_in[1].gl_Position);

    edge = 0.0;
    gl_Position = gl_in[0].gl_Position;
    EmitVertex();

    edge = 2.0 * dist;
    gl_Position = gl_in[1].gl_Position;
    EmitVertex();

    EndPrimitive();
}