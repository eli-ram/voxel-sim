from ...graphics.shaders import ShaderCache, ShaderUniforms, ShaderAttributes


class VoxelAttrs(ShaderAttributes):
    t: int


class VoxelUniforms(ShaderUniforms):
    MVP: int
    COLORS: int
    VOXELS: int
    LAYER_DIR: int
    MOD_ALPHA: int
    ENB_OUTLINE: int


class VoxelShader(ShaderCache[VoxelAttrs, VoxelUniforms]):
    FILE = __file__
    CODE = ['voxel.vert', 'voxel.geom', 'voxel.frag']
