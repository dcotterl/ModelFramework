import subsystems
from pathlib import Path

TEST_MODEL_PATH = "matlab_simulink\\model\\average_subsystems_2025b.slx"

def wire_models(model_map, controller_name):
    mapping = []
    for entry in model_map:
        from_string = f"Targets/{controller_name}/Simulation Models/Models/{entry['sources'][0]['subsystem']}/Outports/{entry['sources'][0]['port']}"
        for destination in entry['destinations']:
            to_string = f"Targets/{controller_name}/Simulation Models/Models/{destination['subsystem']}/Inports/{destination['port']}"
            mapping.append(f"{from_string}\t{to_string}")
    return mapping

if __name__ == "__main__":
    map = subsystems.map_goto_from_connections(TEST_MODEL_PATH)
    mapping = wire_models(map, "Controller")
    for entry in mapping:
        print(entry)