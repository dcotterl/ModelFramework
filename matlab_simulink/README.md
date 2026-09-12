# MATLAB / Simulink

## Content

This folder contains the MATLAB entry script, Simulink models, model
parameters, and reusable MATLAB utilities used by ModelFramework.

## Aim

The aim of this folder is to provide the MATLAB/Simulink models and supporting
code used for modeling, simulation, and analysis within the ModelFramework
project, keeping this content isolated from the other tool-specific folders in
the repository.

## Utilities

The `utilities/` folder is a sibling of `model/` and contains reusable
functions that operate on the included Simulink models. Add both folders to
the MATLAB path before calling them:

```matlab
addpath(genpath('matlab_simulink/utilities'));
addpath(genpath('matlab_simulink/model'));
```

| Function | Purpose |
| --- | --- |
| [`utilities/subsystem_port.m`](utilities/subsystem_port.m) | List Inport/Outport blocks for every top-level subsystem and return input/output tables. |
| [`utilities/continuous_blocks.m`](utilities/continuous_blocks.m) | Compile a model when possible and return a table of blocks identified as continuous. |
| [`utilities/extract_map.m`](utilities/extract_map.m) | Map Goto/From tags to source and destination block paths and port numbers. |
| [`utilities/build_subsystems.m`](utilities/build_subsystems.m) | Apply model parameters and build each top-level subsystem with Simulink Coder. |

```matlab
[inputPorts, outputPorts] = subsystem_port('average_subsystems');
continuousBlocks = continuous_blocks('average_subsystems');
connections = extract_map('average_subsystems');
[subsystems, buildInfo] = build_subsystems('average_subsystems');
```

## Model parameters

The `model/simple_subsystems_parameters.m` script sets the base-workspace
variables consumed by the included models before they are loaded or built. Run
it after adding the model folder to the MATLAB path:

```matlab
run('matlab_simulink/model/simple_subsystems_parameters.m');
```

See [`example.m`](example.m) for a runnable script that validates the folders,
adds both to the path, lists available MATLAB utility files, displays help
text, and calls each utility against `average_subsystems`.

The remaining root file, `.gitignore`, excludes MATLAB-generated cache,
autosave, build, and temporary artifacts from version control.

## Folder documentation

- [`model/README.md`](model/README.md) documents the Simulink model files and parameter script.
- [`utilities/README.md`](utilities/README.md) documents every MATLAB function and local helper.
