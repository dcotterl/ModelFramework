import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock


class FakeMatlabEngine:
    def __init__(self):
        self.engine = Mock()


matlab_module = ModuleType("matlab")
matlab_engine_module = ModuleType("matlab.engine")
matlab_module.double = lambda value: value
matlab_engine_module.start_matlab = Mock()
matlab_module.engine = matlab_engine_module
sys.modules.setdefault("matlab", matlab_module)
sys.modules.setdefault("matlab.engine", matlab_engine_module)

subsystems_path = Path(__file__).parents[1] / "utilities" / "subsystems.py"
subsystems_spec = importlib.util.spec_from_file_location("subsystems", subsystems_path)
assert subsystems_spec is not None and subsystems_spec.loader is not None
subsystems = importlib.util.module_from_spec(subsystems_spec)
sys.modules["subsystems"] = subsystems
subsystems_spec.loader.exec_module(subsystems)


class TestSubsystems(unittest.TestCase):
    def test_flatten_handles_supports_scalar_and_nested_values(self):
        self.assertEqual(subsystems._flatten_handles(4.0), [4.0])
        self.assertEqual(subsystems._flatten_handles([[1.0, 2.0], [3.0]]), [1.0, 2.0, 3.0])

    def test_model_relative_path_strips_model_prefix(self):
        self.assertEqual(
            subsystems._model_relative_path("demo/Controller/Out1", "demo"),
            "Controller/Out1",
        )
        self.assertEqual(
            subsystems._model_relative_path("Other/Block", "demo"),
            "Other/Block",
        )

    def test_extract_subsystem_ports_reads_ports_and_cleans_up(self):
        engine = Mock()
        engine.pwd.return_value = "original"
        engine.find_system.side_effect = [
            ["demo/Controller"],
            ["demo/Controller/In1"],
            ["demo/Controller/Out1"],
        ]
        engine.get_param.side_effect = ["Reference", "Command"]
        matlab_engine_module.start_matlab.return_value = engine

        with tempfile.TemporaryDirectory() as directory:
            model_path = Path(directory) / "demo.slx"
            model_path.touch()

            result = subsystems.extract_subsystem_ports(model_path)

        self.assertEqual(result, [{
            "subsystem": "Controller",
            "input": ["Reference"],
            "output": ["Command"],
        }])
        engine.close_system.assert_called_once_with("demo", 0, nargout=0)
        engine.quit.assert_called_once_with()

    def test_find_continuous_blocks_returns_matching_blocks_and_terminates_compile(self):
        engine = Mock()
        engine.pwd.return_value = "original"
        engine.find_system.return_value = ["demo/Controller", "demo/Plant"]
        engine.get_param.side_effect = [[0.0, 0.0], [0.1, 0.0]]
        engine.isequal.side_effect = lambda actual, expected, nargout: actual == expected
        matlab_engine_module.start_matlab.return_value = engine

        with tempfile.TemporaryDirectory() as directory:
            model_path = Path(directory) / "demo.slx"
            model_path.touch()

            result = subsystems.find_continuous_blocks(model_path)

        self.assertEqual(result, ["demo/Controller"])
        self.assertEqual(engine.feval.call_args_list[0].args[-1], "compile")
        self.assertEqual(engine.feval.call_args_list[1].args[-1], "term")
        engine.close_system.assert_called_once_with("demo", 0, nargout=0)
        engine.quit.assert_called_once_with()

    def test_map_goto_from_connections_resolves_subsystem_ports(self):
        engine = Mock()
        engine.pwd.return_value = "original"
        engine.find_system.side_effect = [
            ["demo/Goto"],
            ["demo/From"],
            ["demo/Controller/Out1"],
            ["demo/Plant/In1"],
        ]

        def get_param(handle, parameter, nargout):
            values = {
                ("demo/Goto", "GotoTag"): "SignalA",
                ("demo/Goto", "LineHandles"): {"Inport": [[1]]},
                (1, "SrcBlockHandle"): 2,
                (1, "SrcPortHandle"): 3,
                (2, "BlockType"): "SubSystem",
                (3, "PortNumber"): 1,
                (2, "PortNumber"): 1,
                ("demo/Controller/Out1", "Port"): 1,
                ("demo/Controller/Out1", "Name"): "Command",
                ("demo/From", "GotoTag"): "SignalA",
                ("demo/From", "LineHandles"): {"Outport": [[4]]},
                (4, "DstBlockHandle"): [[5]],
                (4, "DstPortHandle"): [[6]],
                (5, "BlockType"): "SubSystem",
                (5, "PortNumber"): 1,
                (6, "PortNumber"): 1,
                ("demo/Plant/In1", "Port"): 1,
                ("demo/Plant/In1", "Name"): "Input",
            }
            if parameter == "fullname":
                return {2: "demo/Controller", 5: "demo/Plant"}[handle]
            return values[(handle, parameter)]

        engine.get_param.side_effect = get_param
        engine.getfullname.side_effect = lambda handle, nargout: {
            2: "demo/Controller",
            5: "demo/Plant",
        }[handle]
        matlab_engine_module.start_matlab.return_value = engine

        with tempfile.TemporaryDirectory() as directory:
            model_path = Path(directory) / "demo.slx"
            model_path.touch()

            result = subsystems.map_goto_from_connections(model_path)

        self.assertEqual(result, [{
            "tag": "SignalA",
            "sources": [{"subsystem": "Controller", "port": "Command"}],
            "destinations": [{"subsystem": "Plant", "port": "Input"}],
        }])
        engine.close_system.assert_called_once_with("demo", 0, nargout=0)
        engine.quit.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()