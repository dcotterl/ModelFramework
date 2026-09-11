from pathlib import Path
from niveristand.systemdefinitionapi import SystemDefinition, Model

COMPILED_MODEL_FOLDER = "C:\\Users\\VECU\\Documents\\ModelFramework\\matlab_simulink"
TARGET_VERISTAND_PATH = "C:\\Users\\VECU\\Documents\\ModelFramework\\veristand\\workflow_example\\workflow_example.nivssdf"

def create_configuration(target_type : str = "Windows", target_ip : str = "127.0.0.1", output_path=TARGET_VERISTAND_PATH):
	"""Create a VeriStand system definition and return it."""

	system_definition = SystemDefinition()
	filepath = Path(output_path).resolve()

	system_definition = SystemDefinition(
		filepath.name,
		"System Definition created by ModelFramework",
		"ModelFramework",
		"1.0.0.0",
		"Controller",
		target_type,
		str(filepath),
	)

	target = system_definition.root.get_targets().get_target_list()[0]
	target.ip_address = target_ip

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


def main():
	config = create_configuration()
	models = get_compiled_models(COMPILED_MODEL_FOLDER)
	for model in models:
		model = Model(model.stem,
					  f"Implementation of {model.stem}{model.suffix} from simulink", 
					  str(model),
					  0, 1, 0, True, True, True)
		config = add_model(config, model,"Controller")



	save_configuration(config)


if __name__ == "__main__":

	main()

