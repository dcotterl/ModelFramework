"""Build and read NI VeriStand channel mappings from Simulink results.

The module converts the dictionaries returned by
``subsystems.map_goto_from_connections`` into VeriStand channel-link strings.
It can also persist those links as tab-separated text for later import.
"""

import csv
import logging
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TEST_MODEL_PATH = REPOSITORY_ROOT / "matlab_simulink" / "model" / "average_subsystems_2025b.slx"
TARGET_MAPPING_FILE = REPOSITORY_ROOT / "veristand" / "generated_mapping.txt"
logger = logging.getLogger(__name__)


def _validate_endpoint(endpoint, label):
    """Validate one mapping endpoint and identify it in any error message."""
    if not isinstance(endpoint, dict):
        logger.warning("Invalid mapping endpoint %s: expected a mapping", label)
        raise ValueError(f"{label} must be a mapping")
    for field in ("subsystem", "port"):
        value = endpoint.get(field)
        if not isinstance(value, str) or not value:
            logger.warning("Invalid mapping endpoint %s: %s is missing or empty", label, field)
            raise ValueError(f"{label}.{field} must be a non-empty string")

def assign_links(model_map, controller_name):
    """Create VeriStand links for each destination in a model-map entry.

    The current mapping contract uses the first item in each entry's
    ``sources`` list and creates one link for every destination. Invalid input
    raises ``ValueError`` with the entry and field that failed validation.

    Args:
        model_map: List of dictionaries containing ``sources`` and
            ``destinations`` endpoint lists.
        controller_name: VeriStand target name used in each channel path.

    Returns:
        A list of tab-separated source/destination channel-link strings.
    """
    logger.debug(
        "Assigning links for controller %s from %d model entries",
        controller_name,
        len(model_map) if isinstance(model_map, list) else 0,
    )
    if not isinstance(model_map, list):
        logger.warning("Invalid model map: expected a list")
        raise ValueError("model_map must be a list")
    if not isinstance(controller_name, str) or not controller_name:
        logger.warning("Invalid controller name: expected a non-empty string")
        raise ValueError("controller_name must be a non-empty string")

    mapping = []
    for entry_index, entry in enumerate(model_map, start=1):
        logger.debug("Processing model map entry %d", entry_index)
        if not isinstance(entry, dict):
            logger.warning("Invalid model map entry %d: expected a mapping", entry_index)
            raise ValueError(f"model_map entry {entry_index} must be a mapping")
        sources = entry.get("sources")
        if not isinstance(sources, list) or not sources:
            logger.warning("Model map entry %d has no source endpoint", entry_index)
            raise ValueError(f"model_map entry {entry_index}.sources must not be empty")
        _validate_endpoint(sources[0], f"model_map entry {entry_index}.sources[0]")
        destinations = entry.get("destinations")
        if not isinstance(destinations, list):
            logger.warning("Model map entry %d has invalid destinations", entry_index)
            raise ValueError(f"model_map entry {entry_index}.destinations must be a list")

        source = sources[0]
        from_string = f"Targets/{controller_name}/Simulation Models/Models/{source['subsystem']}/Outports/{source['port']}"
        for destination_index, destination in enumerate(destinations, start=1):
            _validate_endpoint(
                destination,
                f"model_map entry {entry_index}.destinations[{destination_index - 1}]",
            )
            to_string = f"Targets/{controller_name}/Simulation Models/Models/{destination['subsystem']}/Inports/{destination['port']}"
            mapping.append(f"{from_string}\t{to_string}")
            logger.debug("Created mapping link: %s -> %s", from_string, to_string)
    logger.info("Created %d mapping link(s) for controller %s", len(mapping), controller_name)
    return mapping

def create_mapping_file(model_map, controller_name, output_path):
    """Write generated channel links to a UTF-8, tab-separated text file.

    Args:
        model_map: Mapping data accepted by :func:`assign_links`.
        controller_name: VeriStand target name used in each channel path.
        output_path: Destination path for the generated mapping file.
    """
    logger.info("Creating mapping file at %s", output_path)
    mapping = assign_links(model_map, controller_name)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        for entry in mapping:
            f.write(f"{entry}\n")
    logger.info("Wrote %d mapping link(s) to %s", len(mapping), output_path)


def read_mapping(mapping_file):
    """Read source and destination channel lists from a mapping file.

    Args:
        mapping_file: Path to a UTF-8 file with exactly two tab-separated
            fields per row.

    Returns:
        A tuple containing the source list and destination list.

    Raises:
        ValueError: If a row does not contain exactly two fields.
    """
    logger.info("Reading mapping file from %s", mapping_file)
    source = []
    destination = []
    with open(mapping_file, encoding="utf-8", newline="") as file:
        file_content = csv.reader(file, delimiter="\t")
        for row_number, content in enumerate(file_content, start=1):
            if len(content) != 2:
                logger.warning(
                    "Invalid mapping row %d in %s: expected 2 fields, got %d",
                    row_number,
                    mapping_file,
                    len(content),
                )
                raise ValueError(
                    f"Invalid mapping row {row_number}: expected 2 tab-separated fields"
                )
            source.append(content[0])
            destination.append(content[1])
    logger.info("Read %d mapping link(s) from %s", len(source), mapping_file)
    return source, destination

	

if __name__ == "__main__":
    import subsystems

    map = subsystems.map_goto_from_connections(TEST_MODEL_PATH)
    create_mapping_file(map, "Controller", TARGET_MAPPING_FILE)