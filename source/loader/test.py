# pyright: reportUnknownVariableType=false
from ..utils.directory import script_dir, cwd
from .configuration import Configuration
import yaml

@cwd(script_dir(__file__), '..', '..', 'configurations')
def test_load():
    with open('test.yaml') as f:
        data = yaml.safe_load(f)

    conf = Configuration()
    conf.parse(data)
    print(conf)
    