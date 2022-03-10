# pyright: reportUnknownVariableType=false
from ..utils.directory import script_dir, cwd
from .parse import all as p
from .parse.indent import Format
from .configuration import Configuration
import yaml


def load(parser: p.Parsable, filename: str) -> bool:
    with open(filename) as f:
        data = yaml.safe_load(f)

    # Check if config corrected an error
    had_error = bool(parser.error)

    print("\n[#] Parsing:", filename)
    parser.parse(data)
    fmt = Format(prefix=' |', list_unchanged=False, list_errors=True).init()
    print(f"[#] Result: \n V{parser.format(fmt)}\n A")
    print(f"[#] Changed: {parser.changed}")
    print(f"[#] Error: {bool(parser.error)}")

    # Check if config gained an error
    has_error = bool(parser.error)

    return not has_error and parser.changed or had_error


@cwd(script_dir(__file__), '..', '..', 'configurations')
def test_load():
    files = ['test_1.yaml', 'test_1.yaml', 'test_2.yaml', 'test_2.yaml']
    conf = Configuration()
    for file in files:
        load(conf, file)
