# pyright: reportUnknownVariableType=false
from ..utils.directory import script_dir, cwd
from .parse import all as p
from .parse.indent import Format
from .configuration import Configuration
import yaml


def load(parser: p.Parsable, filename: str) -> bool:
    with open(filename) as f:
        data = yaml.safe_load(f)
    
    try:
        parser.parse(data)

    except Exception as e:
        parser.changed = False
        print(e)
    
    return parser.changed


@cwd(script_dir(__file__), '..', '..', 'configurations')
def test_load():
    files = ['test_1.yaml', 'test_2.yaml']
    conf = Configuration()
    fmt = Format(keep_unchanged=False).init()
    print("\n[#] Initial Parse:")
    for file in files:
        if load(conf, file):
            print(f"\n[#] Changes: {conf.format(fmt)}")
    