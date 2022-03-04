# pyright: reportUnknownVariableType=false
from typing import Any, Dict, Union
from ..utils.directory import script_dir, cwd
from dataclasses import dataclass
import yaml

Params = Union[Dict[str, Any], None]


@dataclass
class Object:
    type: str
    operation: str
    properties: dict
    transform: dict


def title_print(title: str, data: Params):
    print(f"{title}:")
    for k, v in (data or {}).items():
        print(f"  {k}: {v}")
    print()


def load_config(data: Params):
    title_print("Config", data)


def load_colors(data: Params):
    title_print("Colors", data)


def load_objects(data: Params):
    data = data or {}
    objects = {key: Object(**data) for key, data in data.items()}
    title_print("Objects", objects)


def load_parameters(data: Params):
    title_print("Parameters", data)


def load_configuration(data: Params):
    data = data or {}
    load_config(data.get("config"))
    load_colors(data.get("colors"))
    load_objects(data.get("objects"))
    load_parameters(data.get("parameters"))


@cwd(script_dir(__file__), '..', '..', 'configurations')
def test_load():
    with open('test.yaml') as f:
        data = yaml.safe_load(f)

    load_configuration(data)
