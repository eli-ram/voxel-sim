#version 430

layout (binding = 0) uniform sampler3D VOXELS;
layout (binding = 1) uniform sampler1D COLORS;
layout (location = 3) uniform bool ENB_OUTLINE = true;
layout (location = 4) uniform float MOD_ALPHA = 1.0;

in vec3 tex;
out vec4 frag_color;
const vec4 BLACK = vec4(0.0,0.0,0.0,0.25);
const vec2 BOX = vec2(0.01, 0.1);

float box_outline(vec3 texel, float inset, float fade)
{
    // Center uv [-1 <> 0 <> +1]
    vec3 uv = abs(texel - 0.5) * 2.0;
    float l = 1.0 - inset;
    vec3 outer = smoothstep(l - fade, l, uv);
    float c = dot(outer, outer.yzx);
    return 1.0 - clamp(c, 0.0, 1.0);
}

void main() {
    // Check if valid voxel
    float voxel = texture(VOXELS, tex).r;
    if (voxel < 1.0) {
        discard;
    }

    // Get voxel color
    float index = (voxel - 1.0) / (textureSize(COLORS, 0) - 1.0);
    vec4 color = texture(COLORS, index);

    // Gray scale
    // color = vec4(vec3(index), 1.0);

    // Modify color alpha
    color.a *= MOD_ALPHA;

    // Set voxel outline
    if (ENB_OUTLINE) {
        vec3 uv = fract(tex * textureSize(VOXELS, 0));
        float outline = box_outline(uv, BOX.x, BOX.y);
        color = mix(BLACK, color, outline);
    }

    // Commit color
    frag_color = color;
}