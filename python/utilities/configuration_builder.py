from pathlib import Path


def _load_system_definition_type():
	"""Load the API type after verifying that VeriStand assemblies are available."""
	try:
		from niveristand.systemdefinitionapi import SystemDefinition
	except (ImportError, OSError) as error:
		raise RuntimeError(
			"The niveristand package requires an installed and registered NI "
			"VeriStand installation. The VeriStand .NET assembly "
			"'NationalInstruments.VeriStand.RealTimeSequenceDefinitionApi' "
			"could not be loaded. Install VeriStand 2021 or later, then run "
			"this script from the activated environment again."
		) from None
	return SystemDefinition


def build_veristand_configuration(target_ip, output_path=None):
	"""Build a VeriStand system definition using the System Definition API.

	``localhost`` and ``127.0.0.1`` create a Windows target. Other addresses
	create a Linux_x64 target and are assigned to the first target in the
	definition.
	"""
	if not target_ip:
		raise ValueError("target_ip must be a non-empty string")

	SystemDefinition = _load_system_definition_type()
	filepath = Path(output_path or "new_configuration.nivssdf").resolve()
	is_local = target_ip in {"localhost", "127.0.0.1"}
	target_type = "Windows" if is_local else "Linux_x64"

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
	if not is_local:
		target.ip_address = target_ip

	if output_path:
		saved, error = system_definition.save_system_definition_file()
		if not saved:
			raise FileNotFoundError(
				f'Unable to save System Definition to "{filepath}": {error}'
			)

	return system_definition


if __name__ == "__main__":
	build_veristand_configuration(
		"192.168.1.100",
		output_path="new_configuration.nivssdf",
	)
