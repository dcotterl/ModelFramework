# Python

## Content

This folder contains Python code related to the ModelFramework project, such as
scripts, packages, notebooks, and utilities used to build, analyze, or support
the models handled by this repository.

## Aim

The aim of this folder is to provide Python-based tooling for interacting with,
processing, or automating tasks around the models (for example: data
processing, code generation, testing, or integration scripts), keeping this
code isolated from the other tool-specific folders in the repository.

## Simulink model inspection

`hello.py` lists every block and every explicitly named signal in a Simulink
`.slx` model. By default, it reads:

```text
matlab_simulink/model/simple_subsystems.slx
```

Run it from the repository root with the default model:

```powershell
python python/hello.py
```

To inspect another model from Python, pass its path to `inspect_model`:

```python
from python.hello import inspect_model

inspect_model("path/to/model.slx")
```

`inspect_model()` uses the default model when no path is provided. It requires
MATLAB Engine for Python, loads the model through MATLAB, and uses Simulink's
API to inspect blocks and explicitly named signals.

The script logs progress at INFO level automatically:

```text
INFO: Starting MATLAB Engine
INFO: Loading Simulink model: ...
INFO: Found ... blocks
INFO: Found ... signal lines
INFO: Closing Simulink model and MATLAB Engine
```
