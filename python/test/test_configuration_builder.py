import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch


class FakeSimulationModels:
    def __init__(self):
        self.models = []

    def get_models(self):
        return self

    def add_model(self, model):
        self.models.append(model)


class FakeTarget:
    def __init__(self, name):
        self.name = name
        self.ip_address = None
        self.target_rate = None
        self.simulation_models = FakeSimulationModels()

    def get_simulation_models(self):
        return self.simulation_models


class FakeTargets:
    def __init__(self, target):
        self.target = target

    def get_target_list(self):
        return [self.target]


class FakeRoot:
    def __init__(self, target):
        self.targets = FakeTargets(target)
        self.add_channel_mappings = Mock()

    def get_targets(self):
        return self.targets


class FakeSystemDefinition:
    instances = []
    save_result = (True, "")

    def __init__(self, *arguments):
        target_name = arguments[4] if len(arguments) > 4 else "LoadedTarget"
        self.target = FakeTarget(target_name)
        self.root = FakeRoot(self.target)
        output_path = arguments[-1] if arguments else "loaded.nivssdf"
        self.document_type = SimpleNamespace(document_file_path=str(output_path))
        self.arguments = arguments
        FakeSystemDefinition.instances.append(self)

    def save_system_definition_file(self):
        return self.save_result


class FakeModel:
    def __init__(self, *arguments):
        self.arguments = arguments


niveristand_module = ModuleType("niveristand")
systemdefinitionapi_module = ModuleType("niveristand.systemdefinitionapi")
systemdefinitionapi_module.SystemDefinition = FakeSystemDefinition
systemdefinitionapi_module.Model = FakeModel
niveristand_module.systemdefinitionapi = systemdefinitionapi_module
sys.modules.setdefault("niveristand", niveristand_module)
sys.modules.setdefault("niveristand.systemdefinitionapi", systemdefinitionapi_module)

mapping_module = ModuleType("mapping")
mapping_module.TARGET_MAPPING_FILE = "mapping.txt"
mapping_module.create_mapping_file = Mock()
mapping_module.read_mapping = Mock()
sys.modules.setdefault("mapping", mapping_module)

subsystems_module = ModuleType("subsystems")
subsystems_module.map_goto_from_connections = Mock()
sys.modules.setdefault("subsystems", subsystems_module)

builder_path = Path(__file__).parents[1] / "utilities" / "configuration_builder.py"
builder_spec = importlib.util.spec_from_file_location("configuration_builder", builder_path)
assert builder_spec is not None and builder_spec.loader is not None
builder = importlib.util.module_from_spec(builder_spec)
sys.modules["configuration_builder"] = builder
builder_spec.loader.exec_module(builder)


class TestConfigurationBuilder(unittest.TestCase):
    def setUp(self):
        FakeSystemDefinition.instances.clear()
        FakeSystemDefinition.save_result = (True, "")

    def test_create_configuration_sets_target_properties(self):
        configuration = builder.create_configuration(
            target_name="TestTarget",
            target_type="Linux",
            target_ip="192.168.1.10",
            output_path="output.nivssdf",
        )

        self.assertIsInstance(configuration, FakeSystemDefinition)
        self.assertEqual(configuration.target.name, "TestTarget")
        self.assertEqual(configuration.target.ip_address, "192.168.1.10")
        self.assertEqual(configuration.target.target_rate, 1000)
        self.assertEqual(configuration.arguments[5], "Linux")

    def test_save_configuration_returns_document_path(self):
        configuration = FakeSystemDefinition("output.nivssdf")

        self.assertEqual(builder.save_configuration(configuration), Path("output.nivssdf"))

    def test_save_configuration_raises_when_sdk_save_fails(self):
        FakeSystemDefinition.save_result = (False, "permission denied")
        configuration = FakeSystemDefinition("output.nivssdf")

        with self.assertRaisesRegex(FileNotFoundError, "permission denied"):
            builder.save_configuration(configuration)

    def test_get_compiled_models_finds_matching_files_recursively(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / "top.vsmodel").touch()
            nested = folder / "nested"
            nested.mkdir()
            (nested / "plant.vsmodel").touch()
            (nested / "ignored.txt").touch()

            self.assertEqual(
                {path.name for path in builder.get_compiled_models(folder)},
                {"top.vsmodel", "plant.vsmodel"},
            )

    def test_add_model_attaches_model_to_named_target(self):
        configuration = FakeSystemDefinition("output.nivssdf")
        model = FakeModel("plant")

        self.assertIs(builder.add_model(configuration, model, "LoadedTarget"), configuration)
        self.assertEqual(configuration.target.simulation_models.models, [model])

    def test_add_model_raises_for_unknown_target(self):
        configuration = FakeSystemDefinition("output.nivssdf")

        with self.assertRaisesRegex(ValueError, 'Target with name "Missing" not found'):
            builder.add_model(configuration, FakeModel("plant"), "Missing")

    def test_get_sysdef_constructs_system_definition(self):
        result = builder.get_sysdef("existing.nivssdf")

        self.assertIsInstance(result, FakeSystemDefinition)
        self.assertEqual(result.arguments, ("existing.nivssdf",))

    def test_import_mapping_adds_channels_and_saves(self):
        configuration = FakeSystemDefinition("output.nivssdf")
        builder.mapping.read_mapping.return_value = (["source"], ["destination"])

        with patch.object(builder, "save_configuration") as save_configuration:
            builder.import_mapping(configuration, "mapping.txt")

        configuration.root.add_channel_mappings.assert_called_once_with(
            ["source"], ["destination"]
        )
        save_configuration.assert_called_once_with(configuration)


if __name__ == "__main__":
    unittest.main()