"""Utilities for working with Simulink subsystems."""

import logging
from pathlib import Path
import json
import matlab.engine


DEFAULT_MODEL = (
	Path(__file__).parents[2]
	/ "matlab_simulink"
	/ "model"
	/ "average_subsystems.slx"
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


def _flatten_handles(matlab_array) -> list[float]:
	"""Flatten a MATLAB handle value into a flat Python list.

	Single handles come back as a plain float instead of a matlab.double array.
	"""
	if isinstance(matlab_array, (int, float)):
		return [matlab_array]
	return [handle for row in matlab_array for handle in row]


def _model_relative_path(full_name: str, model_name: str) -> str:
	"""Strip the leading model name from a Simulink full path."""
	prefix = f"{model_name}/"
	return full_name[len(prefix):] if full_name.startswith(prefix) else full_name


def _resolve_signal_endpoint(
	engine, block_handle, port_handle, port_block_type: str, model_name: str
) -> dict[str, object]:
	"""Resolve a line endpoint to the subsystem port that owns the signal.

	Returns a dict with "subsystem" (model-relative subsystem path, or None if
	the endpoint isn't a subsystem boundary) and "port" (the Inport/Outport
	name on that subsystem, or None).
	"""
	full_name = str(engine.getfullname(block_handle, nargout=1))
	relative_name = _model_relative_path(full_name, model_name)
	if str(engine.get_param(block_handle, "BlockType", nargout=1)) != "SubSystem":
		return {"subsystem": relative_name, "port": None}

	port_number = int(engine.get_param(port_handle, "PortNumber", nargout=1))
	port_blocks = engine.find_system(
		full_name,
		"SearchDepth",
		1,
		"BlockType",
		port_block_type,
		nargout=1,
	)
	for port_block in port_blocks:
		if int(engine.get_param(port_block, "Port", nargout=1)) == port_number:
			port_name = str(engine.get_param(port_block, "Name", nargout=1))
			return {"subsystem": relative_name, "port": port_name}
	return {"subsystem": relative_name, "port": None}


def map_goto_from_connections(
	model_path: Path = DEFAULT_MODEL,
	parameter_file: Path = DEFAULT_PARAMETER_FILE,
) -> list[dict[str, object]]:

	"""Map each Goto/From tag to the subsystem ports sending/receiving its signal.

	For every tag, "sources" lists the subsystem/port feeding the value into
	the tag (from each Goto block) and "destinations" lists the subsystem/port
	consuming it (from each From block). Each list entry is a dict with
	"subsystem" and "port" (port is None when the endpoint isn't a subsystem
	boundary, e.g. a plain signal block).
	"""
	logger.info("Mapping Goto/From signal sources in model: %s", model_path)
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

		goto_blocks = engine.find_system(
			model_name,
			"SearchDepth",
			1,
			"BlockType",
			"Goto",
			nargout=1,
		)
		from_blocks = engine.find_system(
			model_name,
			"SearchDepth",
			1,
			"BlockType",
			"From",
			nargout=1,
		)

		tags: dict[str, dict[str, object]] = {}

		for block in goto_blocks:
			tag = str(engine.get_param(block, "GotoTag", nargout=1))
			entry = tags.setdefault(tag, {"tag": tag, "sources": [], "destinations": []})
			line_handles = engine.get_param(block, "LineHandles", nargout=1)
			inport_line = _flatten_handles(line_handles["Inport"])[0]
			if inport_line > 0:
				source_handle = engine.get_param(inport_line, "SrcBlockHandle", nargout=1)
				source_port_handle = engine.get_param(inport_line, "SrcPortHandle", nargout=1)
				entry["sources"].append(
					_resolve_signal_endpoint(
						engine, source_handle, source_port_handle, "Outport", model_name
					)
				)

		for block in from_blocks:
			tag = str(engine.get_param(block, "GotoTag", nargout=1))
			entry = tags.setdefault(tag, {"tag": tag, "sources": [], "destinations": []})
			line_handles = engine.get_param(block, "LineHandles", nargout=1)
			outport_line = _flatten_handles(line_handles["Outport"])[0]
			if outport_line > 0:
				destination_handles = _flatten_handles(
					engine.get_param(outport_line, "DstBlockHandle", nargout=1)
				)
				destination_port_handles = _flatten_handles(
					engine.get_param(outport_line, "DstPortHandle", nargout=1)
				)
				for dest_handle, dest_port_handle in zip(
					destination_handles, destination_port_handles
				):
					entry["destinations"].append(
						_resolve_signal_endpoint(
							engine, dest_handle, dest_port_handle, "Inport", model_name
						)
					)

		connections = list(tags.values())
		logger.info("Found %d Goto/From tag(s)", len(connections))
		return connections
	finally:
		logger.info("Closing MATLAB Engine")
		if model_loaded:
			engine.close_system(model_name, 0, nargout=0)
		if original_matlab_directory is not None:
			engine.cd(original_matlab_directory, nargout=0)
		engine.quit()


def main() -> None:
	"""Run the subsystem utility with the default model."""
	#print(json.dumps(extract_subsystem_ports(), indent=4))
	#print(json.dumps(find_continuous_blocks(), indent=4))
	print(json.dumps(map_goto_from_connections(), indent=4))

if __name__ == "__main__":
	main()
