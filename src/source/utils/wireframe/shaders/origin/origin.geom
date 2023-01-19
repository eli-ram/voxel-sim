# version 430


// Creating lines in (X, Y, Z) from a point
layout(points) in;
layout(line_strip, max_vertices = 6) out;

// Reuse MVP matrix
layout (location = 0) uniform mat4 MVP;

// Outgoing information
out vec3 color;

// Fn scope
struct Scope {
    vec4 origin;
    mat3 matrix;
};

void proc(in Scope s, vec3 dir) {
    // Use direction as color
    color = dir; 
    // First vertex is @ origin
    gl_Position = s.origin;
    EmitVertex();
    // Second vertex is @ direction
    gl_Position = s.origin + vec4(s.matrix * dir, 0);
    EmitVertex();
    // End line strip
    EndPrimitive();
}

void main() {
    Scope s = Scope(
        gl_in[0].gl_Position, // use transformed origin
        mat3(MVP), // Only use rotation + scale partition
    );
    // Run for cardinal directions
    proc(s, vec3(1, 0, 0)); // X, R
    proc(s, vec3(0, 1, 0)); // Y, B
    proc(s, vec3(0, 0, 1)); // Z, G
}