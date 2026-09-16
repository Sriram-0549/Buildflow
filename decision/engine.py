import json

# Load root cause result
with open("rootcause/result.json", "r") as file:
    result = json.load(file)

root_cause = result.get("root_cause")
confidence = result.get("confidence", 0)

decision = {}

# OOM
if root_cause == "Container exceeded its memory limit":
    decision = {
        "action": "Investigate and increase memory limit",
        "risk": "medium",
        "mode": "human_approval"
    }

# Startup failure
elif root_cause == "Container startup process is failing":
    decision = {
        "action": "Inspect and correct container startup configuration",
        "risk": "medium",
        "mode": "human_approval"
    }

# Image pull failure
elif root_cause == "Container image could not be pulled":
    decision = {
        "action": "Verify image name, tag, and registry access",
        "risk": "low",
        "mode": "human_approval"
    }

# Readiness failure
elif root_cause == "Application is failing its readiness check":
    decision = {
        "action": "Investigate application health and readiness configuration",
        "risk": "medium",
        "mode": "human_approval"
    }

# Unknown
else:
    decision = {
        "action": "Escalate incident for manual investigation",
        "risk": "high",
        "mode": "human_approval"
    }

final_decision = {
    "root_cause": root_cause,
    "confidence": confidence,
    "decision": decision
}

print(json.dumps(final_decision, indent=4))

with open("decision/decision.json", "w") as file:
    json.dump(final_decision, file, indent=4)
