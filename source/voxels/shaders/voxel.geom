#version 430

// Converting Points to Planes
layout(points) in;
layout(triangle_strip, max_vertices = 4) out;

// Model View Projection [transforms from (-1 <-> +1) for all directions]
layout(location = 0) uniform mat4 MVP;

// Layer Stack Direction
layout(location = 1) uniform int LAYER_DIR;

// Voxel grid & inferred size
layout (binding = 0) uniform sampler3D VOXELS;


// Slice Offset
in float offset[1];

// 3D texture coord
out vec3 tex;


void emitPoint(float x, float y, float z) {
    // Texture3D-uv
    tex = vec3(x, y, z);
    // Scale & transform the grid
    gl_Position = MVP * vec4(tex, 1.0);
    // Submit vertex
    EmitVertex();
}

void main() {
    float t = offset[0];
    int side = LAYER_DIR;

    // Calculate plane offset based on heading
    // Important to render the furthest plane first !
    float o = (side >= 3) ? t : 1.0 - t;
    float l = 0.0;
    float r = 1.0;

    // Get a side plane of the standard box
    switch(side % 3) {
        case 0: // X
            emitPoint(o, r, r);
            emitPoint(o, r, l);
            emitPoint(o, l, r);
            emitPoint(o, l, l);
            break;
        case 1: // Y
            emitPoint(r, o, r);
            emitPoint(r, o, l);
            emitPoint(l, o, r);
            emitPoint(l, o, l);
            break;
        case 2: // Z
            emitPoint(r, r, o);
            emitPoint(r, l, o);
            emitPoint(l, r, o);
            emitPoint(l, l, o);
            break;
    }
    EndPrimitive();
}