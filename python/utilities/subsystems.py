"""Utilities for working with Simulink subsystems."""

import logging
from pathlib import Path
import json
import matlab.engine


DEFAULT_MODEL = (
	Path(__file__).parents[2]
	/ "matlab_simulink"
	/ "model"
	/ "simple_subsystems.slx"
)
DEFAULT_PARAMETER_FILE = (
	Path(__file__).parents[2]
	/ "matlab_simulink" 
	/ "model" 
	/ "simple_subsystems_parameters.m"
	)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def execute_model_parameter_file(
	parameter_file: Path = DEFAULT_PARAMETER_FILE,
	engine=None,
) -> dict[str, object]:
	"""Run a MATLAB parameter script and return its base-workspace variables."""
	logger.info("Executing MATLAB parameter file: %s", parameter_file)
	parameter_file = Path(parameter_file)

	if not parameter_file.is_file():
		raise FileNotFoundError(f"MATLAB parameter file not found: {parameter_file}")
	if parameter_file.suffix.lower() != ".m":
		raise ValueError(f"MATLAB parameter file must have a .m extension: {parameter_file}")

	owns_engine = engine is None
	if owns_engine:
		logger.info("Starting MATLAB Engine")
		engine = matlab.engine.start_matlab()

	try:
		workspace_names_before = {
			str(name) for name in engine.eval("who", nargout=1)
		}
		engine.run(str(parameter_file.resolve()), nargout=0)
		workspace_names_after = {
			str(name) for name in engine.eval("who", nargout=1)
		}
		parameter_names = sorted(workspace_names_after - workspace_names_before)
		return {name: engine.workspace[name] for name in parameter_names}
	finally:
		if owns_engine:
			logger.info("Closing MATLAB Engine")
			engine.quit()


def extract_subsystem_ports(
	model_path: Path = DEFAULT_MODEL,
	parameter_file: Path = DEFAULT_PARAMETER_FILE,
) -> list[dict[str, object]]:
	
	"""Return direct input and output port names for each top-level subsystem."""
	logger.info("Extracting subsystem ports from model: %s", model_path)
	model_path = Path(model_path)

	if not model_path.is_file():
		raise FileNotFoundError(f"Simulink model not found: {model_path}")

	model_name = model_path.stem
	logger.info("Starting MATLAB Engine")
	engine = matlab.engine.start_matlab()
	original_matlab_directory = None
	model_loaded = False

	try:
		original_matlab_directory = str(engine.pwd(nargout=1))
		engine.cd(str(model_path.resolve().parent), nargout=0)
		execute_model_parameter_file(parameter_file, engine=engine)
		logger.info("Loading Simulink model: %s", model_path)
		engine.load_system(str(model_path.resolve()))
		model_loaded = True

		subsystems = engine.find_system(
			model_name,
			"SearchDepth",
			1,
			"BlockType",
			"SubSystem",
			nargout=1,
		)
		subsystem_ports = []

		for subsystem in subsystems:
			logger.info("Inspecting subsystem: %s", subsystem)
			subsystem_name = str(subsystem).rsplit("/", 1)[-1]
			ports = {"subsystem": subsystem_name, "input": [], "output": []}
			for port_type, block_type in (("input", "Inport"), ("output", "Outport")):
				port_blocks = engine.find_system(
					subsystem,
					"SearchDepth",
					1,
					"BlockType",
					block_type,
					nargout=1,
				)
				ports[port_type].extend(
					str(engine.get_param(port, "Name", nargout=1))
					for port in port_blocks
				)
			subsystem_ports.append(ports)

		logger.info(
			"Found %d top-level subsystems",
			len(subsystem_ports),
		)
		return subsystem_ports
	finally:
		logger.info("Closing MATLAB Engine")
		if model_loaded:
			engine.close_system(model_name, 0, nargout=0)
		if original_matlab_directory is not None:
			engine.cd(original_matlab_directory, nargout=0)
		engine.quit()


def find_continuous_blocks(
	model_path: Path = DEFAULT_MODEL,
	parameter_file: Path = DEFAULT_PARAMETER_FILE,
) -> list[str]:
	
	"""Return the full paths of blocks with a continuous compiled sample time."""
	logger.info("Finding continuous blocks in model: %s", model_path)
	model_path = Path(model_path)
	if not model_path.is_file():
		raise FileNotFoundError(f"Simulink model not found: {model_path}")

	model_name = model_path.stem
	logger.info("Starting MATLAB Engine")
	engine = matlab.engine.start_matlab()
	original_matlab_directory = None
	model_loaded = False
	model_compiled = False

	try:
		original_matlab_directory = str(engine.pwd(nargout=1))
		engine.cd(str(model_path.resolve().parent), nargout=0)
		execute_model_parameter_file(parameter_file, engine=engine)
		logger.info("Loading Simulink model: %s", model_path)
		engine.load_system(str(model_path.resolve()))
		model_loaded = True

		empty_argument = matlab.double([])
		engine.feval(
			model_name,
			empty_argument,
			empty_argument,
			empty_argument,
			"compile",
			nargout=0,
		)
		model_compiled = True

		continuous_sample_time = matlab.double([0.0, 0.0])
		blocks = engine.find_system(model_name, "Type", "Block", nargout=1)
		logger.info("Inspecting all blocks in the model for continuous sample time")
		continuous_blocks = [
			str(block)
			for block in blocks
			if engine.isequal(
				engine.get_param(block, "CompiledSampleTime", nargout=1),
				continuous_sample_time,
				nargout=1,
			)
		]

		logger.info("Found %d continuous blocks", len(continuous_blocks))
		return continuous_blocks
	finally:
		if model_compiled:
			engine.feval(
				model_name,
				matlab.double([]),
				matlab.double([]),
				matlab.double([]),
				"term",
				nargout=0,
			)
		logger.info("Closing MATLAB Engine")
		if model_loaded:
			engine.close_system(model_name, 0, nargout=0)
		if original_matlab_directory is not None:
			engine.cd(original_matlab_directory, nargout=0)
		engine.quit()


def main() -> None:
	"""Run the subsystem utility with the default model."""
	#ports = extract_subsystem_ports()
	#print(json.dumps(ports, indent=4))
	print(json.dumps(find_continuous_blocks(), indent=4))

if __name__ == "__main__":
	main()
