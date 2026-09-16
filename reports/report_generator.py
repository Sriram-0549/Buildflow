import json
import os
import sys
from datetime import datetime


# ==========================================
# GET INCIDENT ID
# ==========================================

if len(sys.argv) < 2:
    print("❌ Please provide an incident ID")
    print("Example: python3 reports/report_generator.py INC-002")
    exit()

incident_id = sys.argv[1]


# ==========================================
# FILE PATHS
# ==========================================
incident_file = f"incidents/incident-{incident_id[4:]}.json"
evidence_file = "evidence/evidence.json"
rootcause_file = "rootcause/result.json"
decision_file = "decision/decision.json"
recovery_file = "recovery/recovery.json"


# ==========================================
# LOAD JSON
# ==========================================

def load_json(file_path):

    with open(file_path, "r") as file:
        return json.load(file)


if not os.path.exists(incident_file):
    print(f"❌ Incident file not found: {incident_file}")
    exit()

incident = load_json(incident_file)
evidence = load_json(evidence_file)
rootcause = load_json(rootcause_file)
decision = load_json(decision_file)
recovery = load_json(recovery_file)


# ==========================================
# BUILD INCIDENT REPORT
# ==========================================

report = {
    "incident_id": incident_id,

    "created_at": datetime.now().isoformat(),

    "incident": {
        "type": incident.get("type"),
        "service": incident.get("service"),
        "symptom": incident.get("symptom"),
        "status": incident.get("status")
    },

    "root_cause_analysis": {
        "root_cause": rootcause.get("root_cause"),
        "confidence": rootcause.get("confidence"),
        "reasoning": rootcause.get("reasoning")
    },

    "decision": {
        "action": decision.get("decision", {}).get("action"),
        "risk": decision.get("decision", {}).get("risk"),
        "mode": decision.get("decision", {}).get("mode")
    },

    "remediation": {
        "status": "applied",
        "description": (
            "Kubernetes Deployment was patched "
            "to correct the startup configuration"
        )
    },

    "recovery": {
        "status": recovery.get("recovery"),
        "pod": recovery.get("pod"),
        "pod_status": recovery.get("pod_status"),
        "restart_count_before": recovery.get(
            "restart_count_before"
        ),
        "restart_count_after": recovery.get(
            "restart_count_after"
        ),
        "health_status": recovery.get(
            "health_status"
        ),
        "health_response": recovery.get(
            "health_response"
        )
    }
}


# ==========================================
# FINAL INCIDENT STATUS
# ==========================================

if recovery.get("recovery") == "confirmed":
    report["final_status"] = "resolved"
else:
    report["final_status"] = "unresolved"


# ==========================================
# CREATE REPORT DIRECTORY
# ==========================================

os.makedirs("reports/history", exist_ok=True)


# ==========================================
# SAVE REPORT
# ==========================================

output_file = f"reports/history/{incident_id}.json"

with open(output_file, "w") as file:
    json.dump(report, file, indent=4)


# ==========================================
# DISPLAY REPORT
# ==========================================

print("\n========================================")
print("         INCIDENT REPORT")
print("========================================")

print(
    json.dumps(
        report,
        indent=4
    )
)

print(f"\n✅ Report saved to: {output_file}")
