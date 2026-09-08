from pathlib import Path
import argparse
from zipfile import ZipFile
from xml.etree import ElementTree


def list_blocks_from_slx(model_path: Path) -> None:
	"""List blocks by reading the XML inside an SLX archive."""
	with ZipFile(model_path) as archive:
		def visit_system(system_ref: str, parent_path: str) -> None:
			system_path = f"simulink/systems/{system_ref}.xml"
			root = ElementTree.fromstring(archive.read(system_path))

			for block in root.findall("Block"):
				block_path = f"{parent_path}/{block.attrib['Name']}"
				print(f"- {block_path} ({block.attrib.get('BlockType', 'Unknown')})")

				subsystem = block.find("System")
				if subsystem is not None:
					visit_system(subsystem.attrib["Ref"], block_path)

		print(f"Blocks in {model_path.name}:")
		visit_system("system_root", model_path.stem)


def list_blocks(model_path: Path) -> None:
	"""Load a Simulink model and print every block in it."""
	try:
		import matlab.engine
	except ModuleNotFoundError:
		list_blocks_from_slx(model_path)
		return

	matlab = matlab.engine.start_matlab()
	model_name = model_path.stem

	try:
		matlab.load_system(str(model_path.resolve()))
		blocks = matlab.find_system(model_name, "Type", "Block", nargout=1)

		print(f"Blocks in {model_path.name}:")
		for block in blocks:
			print(f"- {block}")
	finally:
		matlab.close_system(model_name, 0, nargout=0)
		matlab.quit()


def main() -> None:
	parser = argparse.ArgumentParser(
		description="List all blocks in a Simulink model."
	)
	parser.add_argument(
		"model",
		nargs="?",
		type=Path,
		default=Path(__file__).parents[1] / "matlab_simulink" / "model" / "simple_subsystems.slx",
		help="Path to the .slx model (default: matlab_simulink/model/simple_subsystems.slx)",
	)
	args = parser.parse_args()

	if not args.model.is_file():
		raise FileNotFoundError(f"Simulink model not found: {args.model}")

	list_blocks(args.model)


if __name__ == "__main__":
	main()