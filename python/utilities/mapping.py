import subsystems

TEST_MODEL_PATH = "matlab_simulink\\model\\average_subsystems_2025b.slx"
TARGET_MAPPING_FILE = "veristand\\generated_mapping.txt"

def assign_links(model_map, controller_name):
    mapping = []
    for entry in model_map:
        from_string = f"Targets/{controller_name}/Simulation Models/Models/{entry['sources'][0]['subsystem']}/Outports/{entry['sources'][0]['port']}"
        for destination in entry['destinations']:
            to_string = f"Targets/{controller_name}/Simulation Models/Models/{destination['subsystem']}/Inports/{destination['port']}"
            mapping.append(f"{from_string}\t{to_string}")
    return mapping

def create_mapping_file(model_map, controller_name, output_path):
    mapping = assign_links(model_map, controller_name)
    with open(output_path, "w") as f:
        for entry in mapping:
            f.write(f"{entry}\n")

if __name__ == "__main__":
    map = subsystems.map_goto_from_connections(TEST_MODEL_PATH)
    create_mapping_file(map, "Controller", TARGET_MAPPING_FILE)