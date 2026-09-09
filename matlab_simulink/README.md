# MATLAB / Simulink

## Content

This folder contains MATLAB scripts, functions, and Simulink models used in the
ModelFramework project, including `.m` files, `.mlx` live scripts, `.slx`/`.mdl`
Simulink models, MATLAB projects, and any associated configuration or data
files needed to run them.

## Aim

The aim of this folder is to provide the MATLAB/Simulink models and supporting
code used for modeling, simulation, and analysis within the ModelFramework
project, keeping this content isolated from the other tool-specific folders in
the repository.

## Functions

The `model/` folder contains reusable functions that operate on the included
Simulink models (`simple_subsystems.slx`, `average_subsystems.slx`). Add the
folder to the MATLAB path before calling them:

```matlab
addpath(genpath('matlab_simulink/model'));
```

| Function | Purpose |
| --- | --- |
| `subsystem_port` | List the Inport/Outport blocks of every top-level subsystem. |
| `continuous_blocks` | Compile the model and list every block with a continuous sample time. |
| `extract_map` | Map Goto/From tags to the blocks that generate and consume their signal. |
| `build_subsystems` | Apply configuration parameters and build every top-level subsystem with Simulink Coder. |

```matlab
[inputPorts, outputPorts] = subsystem_port('average_subsystems');
continuousBlocks = continuous_blocks('average_subsystems');
connections = extract_map('average_subsystems');
[subsystems, buildInfo] = build_subsystems('average_subsystems');
```

`simple_subsystems_parameters.m` sets the base-workspace variables consumed by
the included models before they are loaded or built.

See [`example.m`](example.m) for a runnable script that adds the model folder
to the path, lists the available functions, and calls each of them against
`average_subsystems`.
