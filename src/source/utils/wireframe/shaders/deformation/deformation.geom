# version 430

// Adding Edge Value that is varying over the edge
layout(lines) in;
layout(line_strip, max_vertices = 2) out;

// Accept useful information
in vec3 original_pos[2];
in vec3 deformed_pos[2];

// Outgoing information
out float original_dist;
out float deformed_dist;
out float edge;

float dist(vec3 ps[2]) {
    return distance(ps[0], ps[1]);
}

void main() {
    // Compute actual deformation numbers
    original_dist = dist(original_pos);
    deformed_dist = dist(deformed_pos);
    
    edge = -1.0;
    gl_Position = gl_in[0].gl_Position;
    EmitVertex();

    edge = +1.0;
    gl_Position = gl_in[1].gl_Position;
    EmitVertex();

    EndPrimitive();
}