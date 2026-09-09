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

## Requirements

- A supported Python version for the installed MATLAB release
- MATLAB with Simulink
- MATLAB Engine for Python installed in the active Python environment

Verify that the engine is available before running the utilities:

```powershell
python -c "import matlab.engine; print('MATLAB Engine available')"
```

Commands in this document assume the current directory is the repository root.

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

## Subsystem utilities

`utilities/subsystems.py` provides APIs for inspecting Simulink subsystems.
They use the included model by default:

```text
matlab_simulink/model/simple_subsystems.slx
```

Run the utility directly to print a JSON array containing the full paths of
all continuous-time blocks:

```powershell
python python/utilities/subsystems.py
```

### Continuous-time blocks

`find_continuous_blocks()` compiles the model and recursively inspects its
blocks. A block is reported as continuous when its compiled sample time is
exactly `[0, 0]`. The returned strings are full Simulink block paths.

```python
from python.utilities.subsystems import find_continuous_blocks

continuous_blocks = find_continuous_blocks()
for block_path in continuous_blocks:
	print(block_path)
```

Pass a `pathlib.Path` or path-like value to inspect another model:

```python
continuous_blocks = find_continuous_blocks("path/to/model.slx")
```

An empty list means that no blocks have a continuous compiled sample time.
The function raises `FileNotFoundError` if the model path does not exist, and
MATLAB reports model compilation errors through MATLAB Engine.

### Subsystem ports

`extract_subsystem_ports()` returns the direct input and output port names for
each top-level subsystem:

```python
from python.utilities.subsystems import extract_subsystem_ports

subsystems = extract_subsystem_ports()
```

The result has this shape:

```json
[
	{
		"subsystem": "Controller",
		"input": ["Reference", "Feedback"],
		"output": ["Command"]
	}
]
```

### Model parameter files

`execute_model_parameter_file()` runs a MATLAB `.m` script in the MATLAB base
workspace and returns the variables created by the script:

```python
from python.utilities.subsystems import execute_model_parameter_file

parameters = execute_model_parameter_file(
	"matlab_simulink/model/simple_subsystems_parameters.m"
)
print(parameters["dt"])
```

By default, the function starts and closes its own MATLAB Engine. Pass an
existing engine when the parameters must remain in the base workspace for a
subsequent model load, simulation, or build:

```python
import matlab.engine

from python.utilities.subsystems import execute_model_parameter_file

engine = matlab.engine.start_matlab()
try:
	execute_model_parameter_file(
		"matlab_simulink/model/simple_subsystems_parameters.m",
		engine=engine,
	)
	engine.load_system("matlab_simulink/model/simple_subsystems.slx")
finally:
	engine.quit()
```

The function raises `FileNotFoundError` for a missing script and `ValueError`
when the supplied file does not have a `.m` extension. MATLAB execution errors
are propagated through MATLAB Engine.

The model-inspection APIs start MATLAB Engine, load the requested model without
opening the Simulink editor, and close the model and engine before returning.
