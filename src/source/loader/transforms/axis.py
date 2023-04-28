from typing import Optional
from source.loader.data import Vec3, glm

class Axis(Vec3):

    def fromValue(self, data) -> Optional[glm.vec3]:
        # Intercept string as primary axis
        if isinstance(data, str):
            K = data.strip().upper()
            def _(D): return float(D == K)
            return glm.vec3(_("X"), _("Y"), _("Z"))
        return super().fromValue(data)
