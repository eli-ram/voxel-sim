#version 430

layout (location = 2) uniform vec4 COLOR;

// Deformatin values
in float original_dist;
in float deformed_dist;
// Edge position (-1.0 to +1.0)
// in float edge;

// Color out
out vec4 frag_color;

void main()
{
    // Input color (unused...)
    vec4 color = vec4(0,0,0,1);
    color.a = COLOR.a;

    // Distance to center
    // float c = abs(edge);
    // Distance to vertices
    // float v = 1.0 - c;

    // Tint based on deformation
    float d = abs(deformed_dist - original_dist);
    const float epsilon = 0.01;
    if (d < epsilon) {
        // Less green the more deviation
        color.g = 1.0 - smoothstep(0, epsilon, d);
    } else if (deformed_dist > original_dist) {
        // More red the more expansion
        float d = original_dist / deformed_dist;
        color.r = 1.0 - d * 0.5;
    } else {
        // More blue the more compression
        float d = deformed_dist / original_dist;
        color.b = 1.0 - d * 0.5;
    }
    

    // Output color
    frag_color = color;
}