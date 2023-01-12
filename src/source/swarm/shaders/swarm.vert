#version 430

// Uniforms

// Agent Data
layout (location = 0) in vec2 position;
layout (location = 1) in float direction;
layout (location = 2) in float velocity;

// Resulting geometry
out VertexData {
    out vec2 prev;
    out vec2 curr;
    out float gray;
};

vec2 heading(float dir) {
    return vec2(sin(dir), cos(dir));
}

void main() {
    curr = position;
    prev = position - heading(direction) * velocity;
    gray = (velocity - 0.001) / (0.002 - 0.001); 
}


