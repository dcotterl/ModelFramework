import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

sys.modules.setdefault("subsystems", ModuleType("subsystems"))

mapping_path = Path(__file__).parents[1] / "utilities" / "mapping.py"
mapping_spec = importlib.util.spec_from_file_location("mapping", mapping_path)
assert mapping_spec is not None and mapping_spec.loader is not None
mapping = importlib.util.module_from_spec(mapping_spec)
sys.modules["mapping"] = mapping
mapping_spec.loader.exec_module(mapping)


class TestMapping(unittest.TestCase):
    def test_assign_links_creates_links_for_each_destination(self):
        model_map = [
            {
                "sources": [{"subsystem": "Controller", "port": "Output"}],
                "destinations": [
                    {"subsystem": "Plant", "port": "Input"},
                    {"subsystem": "Monitor", "port": "Input"},
                ],
            }
        ]

        self.assertEqual(mapping.assign_links(model_map, "Target"), [
            "Targets/Target/Simulation Models/Models/Controller/Outports/Output\t"
            "Targets/Target/Simulation Models/Models/Plant/Inports/Input",
            "Targets/Target/Simulation Models/Models/Controller/Outports/Output\t"
            "Targets/Target/Simulation Models/Models/Monitor/Inports/Input",
        ])


    def test_create_mapping_file_writes_one_link_per_line(self):
        model_map = [
            {
                "sources": [{"subsystem": "Controller", "port": "Output"}],
                "destinations": [{"subsystem": "Plant", "port": "Input"}],
            }
        ]
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "mapping.txt"

            mapping.create_mapping_file(model_map, "Target", output_path)

            self.assertEqual(output_path.read_text(), (
                "Targets/Target/Simulation Models/Models/Controller/Outports/Output\t"
                "Targets/Target/Simulation Models/Models/Plant/Inports/Input\n"
            ))


    def test_read_mapping_returns_sources_and_destinations(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            mapping_path = Path(temporary_directory) / "mapping.txt"
            mapping_path.write_text(
                "source-one\tdestination-one\n"
                "source-two\tdestination-two\n"
            )

            self.assertEqual(mapping.read_mapping(mapping_path), (
                ["source-one", "source-two"],
                ["destination-one", "destination-two"],
            ))