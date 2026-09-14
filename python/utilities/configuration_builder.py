"""Create and update NI VeriStand system definitions.

The functions in this module connect compiled Simulink models and generated
channel mappings to a VeriStand ``SystemDefinition``. The VeriStand Python
package and its supported NI VeriStand installation are required at runtime.
"""

from pathlib import Path
import logging
import os
from niveristand.systemdefinitionapi import SystemDefinition, Model
import mapping
import subsystems

TARGET_MODEL = "matlab_simulink\\model\\average_subsystems_2025b.slx"
TARGET_VERISTAND_PATH = "veristand\\workflow_example\\workflow_example.nivssdf"
DEFAULT_MODEL_FOLDER = (
	Path(__file__).parents[2]
	/ "matlab_simulink"
)
DEFAULT_TARGET_NAME = "Controller"
logger = logging.getLogger(__name__)

def configure_logging(level: int = logging.INFO) -> None:
	"""Configure the shared application logger for all Python utilities."""
	logging.basicConfig(
		level=level,
		format="%(asctime)s %(levelname)s %(name)s: %(message)s",
	)
	logger.debug("Logging configured at level %s", logging.getLevelName(level))

def create_configuration(target_name : str = DEFAULT_TARGET_NAME, target_type : str = "Windows", target_ip : str = "localhost", output_path=TARGET_VERISTAND_PATH) -> SystemDefinition:
	"""Create a VeriStand system definition with one configured target.

	Args:
		target_name: Name assigned to the first target.
		target_type: VeriStand target type, such as ``Windows``.
		target_ip: IP address or host name assigned to the target.
		output_path: Destination path stored in the system-definition object.

	Returns:
		A configured :class:`SystemDefinition` instance.
	"""

	logger.info(
		"Creating system definition for target %s at %s",
		target_name,
		Path(output_path).resolve(),
	)
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
	logger.debug(
		"Configured target %s with type=%s, ip=%s, rate=%s",
		target_name,
		target_type,
		target_ip,
		target.target_rate,
	)

	return system_definition

def save_configuration(system_definition) -> Path:
	"""Save a system definition and return its document path.

	Raises:
		FileNotFoundError: If the VeriStand API reports that saving failed.
	"""
	filepath = Path(system_definition.document_type.document_file_path)
	logger.info("Saving system definition to %s", filepath)
	saved, error = system_definition.save_system_definition_file()
	if not saved:
		logger.error("Failed to save system definition to %s: %s", filepath, error)
		raise FileNotFoundError(f'Unable to save System Definition to "{filepath}": {error}')
	logger.info("Saved system definition to %s", filepath)
	return filepath

def get_compiled_models(folder, extension = "vsmodel") -> list[Path]:
	"""Return compiled model files found recursively below ``folder``.

	The extension may be supplied with or without its leading period.
	"""
	folder = Path(folder)
	extension = extension if extension.startswith(".") else f".{extension}"
	models = list(folder.rglob(f"*{extension}"))
	logger.info(
		"Found %d compiled model(s) below %s with extension %s",
		len(models),
		folder,
		extension,
	)
	logger.debug("Compiled models: %s", models)
	return models

def add_model(system_definition, model, target_name=None) -> SystemDefinition:
	"""Attach a compiled model to a named target.

	Raises:
		ValueError: If no target with ``target_name`` exists.
	"""

	logger.debug("Adding model %s to target %s", model, target_name)
	target = next((t for t in system_definition.root.get_targets().get_target_list() if t.name == target_name), None)
	if target is None:
		logger.warning("Target %s was not found while adding model", target_name)
		raise ValueError(f'Target with name "{target_name}" not found.')

	simulation_models = target.get_simulation_models()
	simulation_models.get_models().add_model(model)
	logger.info("Added model %s to target %s", model, target_name)
	return system_definition

def create_configuration_with_compiled_models(): # show how to generate a VeriStand system definition with compiled models
	"""Build and save a configuration containing discovered compiled models."""
	logger.info("Building configuration with compiled models")
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
	"""Generate the VeriStand mapping file from Simulink Goto/From links."""
	logger.info("Creating mapping for model %s", TARGET_MODEL)
	mapping.create_mapping_file(subsystems.map_goto_from_connections(TARGET_MODEL), 
							    DEFAULT_TARGET_NAME, 
								mapping.TARGET_MAPPING_FILE)

def get_sysdef(path) -> SystemDefinition:
	"""Load and return a VeriStand system definition from ``path``."""
	logger.info("Loading system definition from %s", path)
	return SystemDefinition(path)

def import_mapping(system_definition, mapping_file=mapping.TARGET_MAPPING_FILE):
	"""Import channel mappings into a system definition and save it."""
	logger.info("Importing channel mappings from %s", mapping_file)
	source, destination = mapping.read_mapping(mapping_file)
	system_definition.root.add_channel_mappings(source, destination)
	logger.debug("Imported %d channel mapping(s)", len(source))
	save_configuration(system_definition)

if __name__ == "__main__":

	configure_logging(
		getattr(logging, os.environ.get("MODEL_FRAMEWORK_LOG_LEVEL", "INFO").upper(), logging.INFO)
	)
	create_configuration_with_compiled_models()
	create_mapping()
	import_mapping(get_sysdef(TARGET_VERISTAND_PATH))

