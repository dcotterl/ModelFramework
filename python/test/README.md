# Python Tests

This folder contains unittest-based tests for the Python utilities. The workspace configures VS Code to discover files matching `test_*.py` from this directory.

## Files

- `__init__.py`: marks the test folder as a Python package; it contains no runtime logic.
- `test_mapping.py`: defines `TestMapping` with tests for lazy imports, repository-anchored paths, link generation, mapping-file writing and reading, invalid model entries, and malformed rows. Its nested `test_assign_links_rejects_invalid_model_entries` and `test_read_mapping_rejects_rows_without_exactly_two_fields` functions describe additional cases but are currently nested inside another test method.
- `test_subsystems.py`: defines fake MATLAB support with `FakeMatlabEngine.__init__`; its tests cover handle flattening, model-relative paths, port extraction, continuous-block detection, connected and unconnected Goto/From mapping, mismatched destination arrays, unresolved ports, cleanup failures, compiled-model cleanup, and logging. Local `get_param` and `cd` helpers configure mock-engine behavior for individual cases.
- `test_configuration_builder.py`: defines fake VeriStand support through `FakeSimulationModels.__init__`, `get_models`, `add_model`, `FakeTarget.__init__`, `get_simulation_models`, `FakeTargets.__init__`, `get_target_list`, `FakeRoot.__init__`, `get_targets`, `FakeSystemDefinition.__init__`, `save_system_definition_file`, and `FakeModel.__init__`. `TestConfigurationBuilder.setUp` resets fake state; its tests cover configuration properties, successful and failed saves, recursive compiled-model discovery, model attachment and unknown targets, system-definition loading, and mapping import. Local mock helpers are used to model API behavior.

## Running

From the repository root:

```powershell
.venv\Scripts\python.exe -m unittest discover -v -s ./python/test -p test_*.py
```

The tests use fakes and mocks for MATLAB and VeriStand APIs, so the unit suite does not launch either external application.
