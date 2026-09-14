# Simulink Models

This folder contains the Simulink models and MATLAB parameter script used by the Python, MATLAB, and VeriStand workflows.

## Files

- `average_subsystems.slx`: Simulink model containing the average-subsystem example.
- `average_subsystems_2025b.slx`: version-specific copy of the average-subsystem model used by the current Python and VeriStand paths.
- `simple_subsystems.slx`: simpler subsystem example used by the Python inspection example.
- `simple_subsystems_2025b.slx`: version-specific copy of the simple-subsystem model.
- `simple_subsystems_parameters.m`: assigns base-workspace parameters for the simple-subsystem model, including `dt`, `P`, `I`, `D`, and `setpoint`.

The `.slx` files are binary Simulink model files and must be opened with a compatible MATLAB/Simulink release. The model names are passed without the `.slx` extension to MATLAB functions such as `subsystem_port`, `continuous_blocks`, and `extract_map`.
