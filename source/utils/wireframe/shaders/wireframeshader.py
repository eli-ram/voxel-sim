from ....graphics.shaders import ShaderAttributes, ShaderUniforms, ShaderCache


class WireframeAttributes(ShaderAttributes):
    pos: int


class WireframeUniforms(ShaderUniforms):
    MVP: int
    COLOR: int


class WireframeShader(ShaderCache[WireframeAttributes, WireframeUniforms]):
    FILE = __file__
    CODE = ['wireframe.vert', 'wireframe.frag']
