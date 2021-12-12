from ...utils.shaders import ShaderCache, ShaderUniforms, ShaderAttributes


class RenderAttributes(ShaderAttributes):
    position: int
    velocity: int
    direction: int


class RenderUniforms(ShaderUniforms):
    pass


class RenderCache(ShaderCache[RenderAttributes, RenderUniforms]):
    FILE = __file__
    CODE = ['swarm.vert', 'swarm.geom', 'swarm.frag']


class ComputeAttributes(ShaderAttributes):
    pass


class ComputeUniforms(ShaderUniforms):
    environment: int
    time: int


class ComputeCache(ShaderCache[ComputeAttributes, ComputeUniforms]):
    FILE = __file__
    CODE = ['swarm.comp']
