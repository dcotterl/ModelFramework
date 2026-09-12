# Python Utilities

This folder contains the reusable Python modules that connect Simulink inspection results to NI VeriStand configuration files.

## Files and Functions

- `subsystems.py`
  - `_load_matlab()`: loads MATLAB Engine lazily when a MATLAB-backed operation is requested.
  - `_cleanup_engine(...)`: terminates compiled models, closes models, restores MATLAB's working directory, and quits the engine while logging cleanup failures.
  - `extract_subsystem_ports(model_path)`: returns direct input and output port names for each top-level Simulink subsystem.
  - `find_continuous_blocks(model_path)`: compiles a model and returns full paths whose compiled sample time is continuous.
  - `_flatten_handles(matlab_array)`: converts scalar, nested, or empty MATLAB handle values into a flat list.
  - `_model_relative_path(full_name, model_name)`: removes the model-name prefix from a Simulink block path.
  - `_resolve_signal_endpoint(...)`: resolves a source or destination handle to a subsystem-relative path and port name.
  - `map_goto_from_connections(model_path)`: maps top-level Goto/From tags to source and destination subsystem ports, including unconnected and malformed-handle diagnostics.
  - `main()`: prints JSON for the three inspection operations using the default model.
- `mapping.py`
  - `_validate_endpoint(endpoint, label)`: validates subsystem and port fields.
  - `assign_links(model_map, controller_name)`: converts source/destination model mappings into VeriStand channel-link strings; the current behavior uses the first source entry.
  - `create_mapping_file(model_map, controller_name, output_path)`: writes generated links as tab-separated lines.
  - `read_mapping(mapping_file)`: reads tab-separated source and destination lists and rejects malformed rows.
  - The script entry point obtains a Simulink map and writes `veristand/generated_mapping.txt`.
- `configuration_builder.py`
  - `create_configuration(...)`: creates a VeriStand `SystemDefinition` and configures its first target.
  - `save_configuration(system_definition)`: saves a system definition and returns its output path.
  - `get_compiled_models(folder, extension)`: recursively finds compiled model files.
  - `add_model(system_definition, model, target_name)`: attaches a model to a named VeriStand target.
  - `create_configuration_with_compiled_models()`: builds a configuration from compiled models found under the MATLAB folder.
  - `create_mapping()`: maps Simulink Goto/From connections into the generated mapping file.
  - `get_sysdef(path)`: loads a VeriStand system definition.
  - `import_mapping(system_definition, mapping_file)`: reads channel mappings, adds them to a system definition, and saves it.

MATLAB Engine is required for `subsystems.py` operations. The `mapping.py` tests can run without MATLAB because the subsystem dependency is imported only by the script entry point. VeriStand operations require the `niveristand` package and its supported NI VeriStand installation.
