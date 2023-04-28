#version 430

// Epsilon Uniform to reason about 'stability'
layout (location = 2) uniform float EPSILON = 1E-3;

// Deformatin values
in float original_dist;
in float deformed_dist;

// Color out
out vec4 frag_color;

void main()
{
    vec4 color = vec4(0,0,0,0.5);

    // Tint based on deformation
    float d = abs(deformed_dist - original_dist);
    // const float epsilon = 1E-5;
    if (d < EPSILON) {
        // Less green the more deviation
        color.g = 1.0 - smoothstep(0, EPSILON, d);
    } else if (deformed_dist > original_dist) {
        // More red the more expansion
        float d = original_dist / deformed_dist;
        color.r = 1.0 - d * 0.8;
    } else {
        // More blue the more compression
        float d = deformed_dist / original_dist;
        color.b = 1.0 - d * 0.8;
    }
    
    // Output color
    frag_color = color;
}