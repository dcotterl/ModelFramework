# ModelFramework

Utilities and example assets for inspecting and integrating engineering models
across Python, MATLAB/Simulink, NI VeriStand, and NI LabVIEW.

The current Python tools can inspect a Simulink model, extract subsystem port
names, identify continuous-time blocks, and map Goto/From signal connections.
The MATLAB tools cover the same inspection tasks plus building subsystems with
Simulink Coder.

## Repository Structure

| Folder | Description |
| --- | --- |
| [`python/`](python/README.md) | Python code supporting the models (scripts, packages, utilities). |
| [`matlab_simulink/`](matlab_simulink/README.md) | MATLAB scripts and Simulink models. |
| [`veristand/`](veristand/README.md) | NI VeriStand projects and system definitions. |
| [`labview/`](labview/README.md) | NI LabVIEW applications and libraries. |

Each folder has its own `README.md` describing its content and aim, and its
own `.gitignore` tailored to the tool used in that folder.

## Tools

| Tool | Purpose |
| --- | --- |
| Python | Scripting, automation, and data processing |
| MATLAB / Simulink | Modeling and simulation |
| NI VeriStand | Real-time testing and simulation |
| NI LabVIEW | Application development and hardware interfacing |

## Getting Started

The included Python examples require a local MATLAB/Simulink installation and
MATLAB Engine for Python. See the [Python documentation](python/README.md) for
setup requirements, commands, and API examples.

From the repository root, report the continuous-time blocks in the included
model with:

```powershell
python python/utilities/subsystems.py
```

## Versions

| Tool | Version |
| --- | --- |
| Python | 3.10 |
| MATLAB / Simulink | 2026a |
| NI VeriStand | 2025Q3 |
| NI LabVIEW | TBD |

## Python Libraries

[NI VeriStand](https://niveristand-python.readthedocs.io/en/latest/getting_started.html)

```powershell
python -m pip install niveristand
```

MatlabEngine

```powershell
python -m pip install matlabengine 
```
