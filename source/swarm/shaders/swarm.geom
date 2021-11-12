#version 430

layout (points) in;
layout (line_strip) out;
layout (max_vertices=2) out;

in VertexData {
    vec2 prev;
    vec2 curr;
    float gray;
} vertex[1];

out FragmentData {
    float gray;
};

// float size = 50;

void main() {
    float g = vertex[0].gray;

    // Emit line start
    gray = g;
    gl_Position = vec4(vertex[0].prev, 0.0, 1.0);
    EmitVertex();

    // Emit line end
    gray = g;
    gl_Position = vec4(vertex[0].curr, 0.0, 1.0);
    EmitVertex();

    // Close Primitive
    EndPrimitive();
}