import json
import os
import sys


# ==========================================
# CONFIGURATION
# ==========================================

history_dir = "incidents/history"


# ==========================================
# GENERATE INCIDENT ID
# ==========================================

def generate_incident_id():

    os.makedirs(history_dir, exist_ok=True)

    files = os.listdir(history_dir)

    incident_numbers = []

    for file_name in files:

        if file_name.startswith("INC-") and file_name.endswith(".json"):

            number = file_name[4:-5]

            if number.isdigit():
                incident_numbers.append(int(number))

    if incident_numbers:
        next_number = max(incident_numbers) + 1
    else:
        next_number = 1

    return f"INC-{next_number:03d}"


# ==========================================
# CREATE INCIDENT
# ==========================================

def create_incident(incident_type, service, symptom):

    incident_id = generate_incident_id()

    incident = {
        "incident_id": incident_id,
        "type": incident_type,
        "service": service,
        "symptom": symptom,
        "status": "detected"
    }

    output_file = f"{history_dir}/{incident_id}.json"

    with open(output_file, "w") as file:
        json.dump(incident, file, indent=4)

    print("\n========================================")
    print("        NEW INCIDENT CREATED")
    print("========================================")

    print(
        json.dumps(
            incident,
            indent=4
        )
    )

    print(f"\n✅ Incident saved to: {output_file}")

    return incident_id


# ==========================================
# COMMAND LINE INPUT
# ==========================================

if len(sys.argv) < 4:

    print("Usage:")

    print(
        "python3 incidents/incident_manager.py "
        "<type> <service> <symptom>"
    )

    print("\nExample:")

    print(
        'python3 incidents/incident_manager.py '
        '"CrashLoopBackOff" '
        '"buildflow-api" '
        '"Container repeatedly restarted"'
    )

    exit()


incident_type = sys.argv[1]
service = sys.argv[2]
symptom = sys.argv[3]


# ==========================================
# CREATE INCIDENT
# ==========================================

create_incident(
    incident_type,
    service,
    symptom
)
