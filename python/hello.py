"""List blocks and named signals from a Simulink SLX model using MATLAB Engine.

Usage:
	python python/hello.py
	from python.hello import inspect_model
	inspect_model("path/to/model.slx")
"""

from pathlib import Path
import matlab.engine
import logging

DEFAULT_MODEL = Path(__file__).parents[1] / "matlab_simulink" / "model" / "simple_subsystems.slx"
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def inspect_model(model_path: Path = DEFAULT_MODEL) -> None:
	"""Print the blocks and named signals in a Simulink model."""
	model_path = Path(model_path)
	if not model_path.is_file():
		logger.error("Simulink model not found: %s", model_path)
		raise FileNotFoundError(f"Simulink model not found: {model_path}")

	logger.info("Starting MATLAB Engine")
	engine = matlab.engine.start_matlab()
	model_name = model_path.stem

	try:
		logger.info("Loading Simulink model: %s", model_path)
		engine.load_system(str(model_path.resolve()))

		blocks = engine.find_system(model_name, "Type", "Block", nargout=1)
		logger.info("Found %d blocks", len(blocks))
		print(f"Blocks in {model_path.name}:")
		for block in blocks:
			print(f"- {block}")

		lines = engine.find_system(model_name, "FindAll", "on", "Type", "line", nargout=1)
		logger.info("Found %d signal lines", len(lines))
		print(f"Signals in {model_path.name}:")
		seen_names = set()
		for line in lines:
			signal_name = engine.get_param(line, "Name", nargout=1)
			if signal_name and signal_name not in seen_names:
				print(f"- {signal_name}")
				seen_names.add(signal_name)
	finally:
		logger.info("Closing Simulink model and MATLAB Engine")
		engine.close_system(model_name, 0, nargout=0)
		engine.quit()


if __name__ == "__main__":

	inspect_model()