# python-voxels
Rendering for voxels with utilities in Python

## Contents
- [Requirements](#requirements)
- [Applications](#applications)
- [Controls](#controls)

# Requirements
- Python 3.9
- Python 3.9 development tools
- [recommended] Python 3.9 venv module

> Should create a python virtual environment in top directory:  
>   `python3.9 -m venv .env`

> Install required modules:  
>   `pip install -r requirements.txt`

# Applications

All test applications are located in the `./tests/` directory.

## gl_voxels

A realtime rendering test-application for rendering voxels.  
Voxel grid resolution may be modified inside `Voxels.setup()`.  
Voxel display-slice resolution may be modified inside `Voxels.setup()`.  
A sphere generator may be enabled inside `Voxels.setup()` (`vox_sphere`).  
A bone model may be displayed by uncommenting `Voxels.bone` (`self.bone`).  
Random Cubes may be set to the voxels randomly from `Voxels.update()`.  

## gl_test

A simple test of open_gl

## gl_swarm

A step-based swarm simulation
Can be reconfigured


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
