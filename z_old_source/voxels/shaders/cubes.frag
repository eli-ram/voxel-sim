#version 430

layout (location = 3) uniform float SIZE = 32.0;

in vec3 tex;
out vec4 color;

vec4 hash43(vec3 p) {
    vec4 p4 = fract(vec4(p.xyzx) * vec4(.1031, .1030, .0973, .1099));
    p4 += dot(p4, p4.wzxy + 33.33);
    return fract((p4.xxyz + p4.yzzw) * p4.zywx);
}

float box(vec3 uv, float inset) {
    vec3 O = vec3(inset);
    vec3 B = step(O, uv);
    vec3 T = step(O, 1.0 - uv);
    vec3 S = B * T;
    return S.x * S.y * S.z;
}

void main() {
    // Todo sample voxel texture
    vec3 voxels = tex * SIZE;
    vec3 uv = fract(voxels);
    vec3 id = clamp(floor(voxels), 0.0, SIZE - 1.0);
    vec4 values = hash43(id);
    float outline = mix(0.2, 1.0, box(uv, 0.2));
    vec3 col = values.rgb * outline;
    float alpha = (values.w > 0.95) ? outline : 0.0;
    color = vec4(col, alpha);
}