from pathlib import Path
from niveristand.systemdefinitionapi import SystemDefinition, Model
from pathlib import Path
import mapping
import subsystems

TARGET_MODEL = "matlab_simulink\\model\\average_subsystems_2025b.slx"
TARGET_VERISTAND_PATH = "veristand\\workflow_example\\workflow_example.nivssdf"
DEFAULT_MODEL_FOLDER = (
	Path(__file__).parents[2]
	/ "matlab_simulink"
)
DEFAULT_TARGET_NAME = "Controller"

def create_configuration(target_name : str = DEFAULT_TARGET_NAME, target_type : str = "Windows", target_ip : str = "localhost", output_path=TARGET_VERISTAND_PATH):
	"""Create a VeriStand system definition and return it."""

	system_definition = SystemDefinition()
	filepath = Path(output_path).resolve()

	system_definition = SystemDefinition(
		filepath.name,
		"System Definition created by ModelFramework",
		"ModelFramework",
		"1.0.0.0",
		target_name,
		target_type,
		str(filepath),
	)

	target = system_definition.root.get_targets().get_target_list()[0]
	target.ip_address = target_ip
	target.target_rate = 1000

	return system_definition

def save_configuration(system_definition):
	"""Save a VeriStand system definition and return the output path."""
	filepath = Path(system_definition.document_type.document_file_path)
	saved, error = system_definition.save_system_definition_file()
	if not saved:
		raise FileNotFoundError(f'Unable to save System Definition to "{filepath}": {error}')
	return filepath

def get_compiled_models(folder, extension = "vsmodel"):
	"""Return a list of Paths for all files in folder (recursively) matching the given extension."""
	folder = Path(folder)
	extension = extension if extension.startswith(".") else f".{extension}"
	return list(folder.rglob(f"*{extension}"))

def add_model(system_definition, model, target_name=None):

	target = next((t for t in system_definition.root.get_targets().get_target_list() if t.name == target_name), None)
	if target is None:
		raise ValueError(f'Target with name "{target_name}" not found.')

	simulation_models = target.get_simulation_models()
	simulation_models.get_models().add_model(model)
	return system_definition

def create_configuration_with_compiled_models(): # show how to generate a VeriStand system definition with compiled models
	config = create_configuration()
	models = get_compiled_models(DEFAULT_MODEL_FOLDER)
	for model in models:
		model = Model(model.stem,
					  f"Implementation of {model.stem}{model.suffix} from simulink", 
					  str(model),
					  0, 1, 0, True, True, True)
		config = add_model(config, model, DEFAULT_TARGET_NAME)
	save_configuration(config)

def create_mapping():
	mapping.create_mapping_file(subsystems.map_goto_from_connections(TARGET_MODEL), 
							    DEFAULT_TARGET_NAME, 
								mapping.TARGET_MAPPING_FILE)

def get_sysdef(path):
	return SystemDefinition(path)

def import_mapping(system_definition, mapping_file=mapping.TARGET_MAPPING_FILE):
	source, destination = mapping.read_mapping(mapping_file)
	system_definition.root.add_channel_mappings(source, destination)
	save_configuration(system_definition)

if __name__ == "__main__":

	create_configuration_with_compiled_models()
	create_mapping()
	import_mapping(get_sysdef(TARGET_VERISTAND_PATH))

