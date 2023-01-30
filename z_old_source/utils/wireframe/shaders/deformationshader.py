from ....graphics.shaders import ShaderAttributes, ShaderUniforms, ShaderCache


class DeformationAttributes(ShaderAttributes):
    pos: int
    offset: int


class DeformationUniforms(ShaderUniforms):
    MVP: int
    COLOR: int
    DEFORMATION: int


class DeformationShader(ShaderCache[DeformationAttributes, DeformationUniforms]):
    FILE = __file__
    CODE = ['deformation.vert', 'deformation.geom', 'deformation.frag']
