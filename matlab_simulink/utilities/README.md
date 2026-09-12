# MATLAB Utilities

These MATLAB functions inspect Simulink models and build top-level subsystems for code generation. Add this folder to the MATLAB path with `addpath(genpath('matlab_simulink/utilities'))`.

## Files and Functions

- `subsystem_port.m`
  - `subsystem_port(modelName)`: returns two tables listing the direct Inport and Outport blocks for each first-level subsystem. The tables include subsystem name, subsystem path, port name, and port number.
- `continuous_blocks.m`
  - `continuous_blocks(modelName)`: compiles a model when possible, scans its hierarchy, and returns a table of blocks identified as continuous by compiled sample time or known continuous-state block type. It cleans up compilation and model loading afterward.
- `extract_map.m`
  - `extract_map(modelName)`: scans top-level Goto and From blocks, groups them by tag, and returns a table containing each tag, its source output, and destination inputs. `getOrCreateEntry` creates or retrieves the internal tag record.
  - `getOrCreateEntry(tags, tag)`: local helper that initializes a tag record with missing output and an empty input list.
- `build_subsystems.m`
  - `build_subsystems(modelName, modelParams)`: applies model parameters, finds first-level subsystems, marks each as atomic, and calls `slbuild`. It returns the subsystem paths and per-subsystem build status and message.

The MATLAB utilities operate on models in `matlab_simulink/model` and require MATLAB with Simulink. `build_subsystems` additionally requires the configured Simulink Coder target, such as VeriStand's `veristand.tlc`.
