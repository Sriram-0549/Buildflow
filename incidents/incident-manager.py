import json
import os


history_dir = "incidents"


def generate_incident_id():

    os.makedirs(history_dir, exist_ok=True)

    files = os.listdir(history_dir)

    incident_numbers = []

    for file_name in files:

        if (
            file_name.startswith("incident-")
            and file_name.endswith(".json")
        ):

            number = file_name[9:-5]

            if number.isdigit():
                incident_numbers.append(int(number))

    if incident_numbers:
        next_number = max(incident_numbers) + 1
    else:
        next_number = 1

    return f"INC-{next_number:03d}"


def create_incident(incident_type, service, symptom):

    incident_id = generate_incident_id()

    incident = {
        "incident_id": incident_id,
        "type": incident_type,
        "service": service,
        "symptom": symptom,
        "status": "detected"
    }

    output_file = f"{history_dir}/incident-{incident_id[4:]}.json"

    with open(output_file, "w") as file:
        json.dump(incident, file, indent=4)

    print(f"✅ New incident created: {incident_id}")

    return incident_id
