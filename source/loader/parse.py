
from typing import Any, Dict, Optional


Params = Optional[Dict[str, Any]]

class Parsable:
    def parse(self, data: Params): ...