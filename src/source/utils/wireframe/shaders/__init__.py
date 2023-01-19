from source.graphics.shaders import ShaderAttributes, ShaderUniforms, ShaderCache


class DeformationAttributes(ShaderAttributes):
    pos: int
    offset: int


class DeformationUniforms(ShaderUniforms):
    MVP: int
    COLOR: int
    DEFORMATION: int


class DeformationShader(ShaderCache[DeformationAttributes, DeformationUniforms]):
    FILE = __file__
    GLOB = 'deformation'
    # DEBUG = True


class WireframeAttributes(ShaderAttributes):
    pos: int


class WireframeUniforms(ShaderUniforms):
    MVP: int
    COLOR: int


class WireframeShader(ShaderCache[WireframeAttributes, WireframeUniforms]):
    FILE = __file__
    GLOB = 'wireframe'


class OriginUniforms(ShaderUniforms):
    MVP: int


class OriginShader(ShaderCache[ShaderAttributes, OriginUniforms]):
    FILE = __file__
    GLOB = 'origin'
    # DEBUG = True
