#version 430

layout (points) in;
layout (line_strip) out;
layout (max_vertices=2) out;
layout (location = 1) uniform vec2 aspect;

in VertexData {
    vec2 prev;
    vec2 curr;
    float gray;
} vertex[1];

out FragmentData {
    float gray;
};

// float size = 50;
vec4 pos(vec2 position) {
    return vec4(aspect * position, 0.0, 1.0);
}

void main() {
    float g = vertex[0].gray;

    // Emit line start
    gray = g;
    gl_Position = pos(vertex[0].prev);
    EmitVertex();

    // Emit line end
    gray = g;
    gl_Position = pos(vertex[0].curr);
    EmitVertex();

    // Close Primitive
    EndPrimitive();
}