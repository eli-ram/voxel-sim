from ...utils.shaders import ShaderCache, ShaderUniforms, ShaderAttributes


class RenderAttributes(ShaderAttributes):
    position: int
    velocity: int
    direction: int


class RenderUniforms(ShaderUniforms):
    aspect: int


class RenderCache(ShaderCache[RenderAttributes, RenderUniforms]):
    FILE = __file__
    CODE = ['swarm.vert', 'swarm.geom', 'swarm.frag']


class ComputeUniforms(ShaderUniforms):
    environment: int
    time: int


class ComputeCache(ShaderCache[ShaderAttributes, ComputeUniforms]):
    FILE = __file__
    CODE = ['swarm.comp']


class FadeUniforms(ShaderUniforms):
    diff: int
    decay: int


class FadeCache(ShaderCache[ShaderAttributes, FadeUniforms]):
    FILE = __file__
    CODE = ['fade.comp']


class RectUniforms(ShaderUniforms):
    aspect: int

class RectCache(ShaderCache[ShaderAttributes, RectUniforms]):
    FILE = __file__
    CODE = ['rect.frag', 'rect.vert']