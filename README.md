# python-voxels
Rendering for voxels with utilities in Python

## Contents
- [Requirements](#requirements)
- [Application](#application)
- [Controls](#controls)

# Requirements
- Python 3.11

> Create a python virtual environment in top directory:  
>   `python3.11 -m venv .env`

> Install project source module in editable mode:
>   `pip install -e .`

> Install the graphics accelerator:
> [windows]
>   `pip install 'dependencies/PyOpenGL_accelerate-3.1.6-cp311-cp311-win_amd64.whl'`
> [linux]
>   `pip install PyOpenGl_accelerate`

# Application

> The main Application is `tests/gl_parsed.py`
> To specify the configuration file edit the `CONF` variable

# Controls

## General

| Input | Function |
|:-|:-|
| F11 | Fullscreen |
| ESCAPE | Close |

## Orbital Camera

| Input | Function |
|:-|:-|
| Mouse Drag | Svivel Camera |
| CRTL + Mouse Drag | Move Camera |
| Mouse Wheel | Zoom Camera |

> The numpad is bound to some incremental 
> camera movement in the `gl_parsed.py` window.