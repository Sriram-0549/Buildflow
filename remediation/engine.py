from kubernetes import client, config

import json

config.load_kube_config()

apps_api = client.AppsV1Api()

print("Connected to Kubernetes")



with open("decision/decision.json", "r") as file:
    decision_data = json.load(file)

root_cause = decision_data.get("root_cause")
confidence = decision_data.get("confidence", 0)
decision = decision_data.get("decision", {})

action = decision.get("action")
risk = decision.get("risk")
mode = decision.get("mode")

print("Root Cause:", root_cause)
print("Confidence:", confidence)
print("Action:", action)
print("Risk:", risk)
print("Mode:", mode)

if mode == "human_approval":
    print("\n⚠️ Human approval required")
    print("Action:", action)
    print("Risk:", risk)

    approval = input("\nApprove remediation? (yes/no): ")

    if approval.lower() == "yes":

        print("\n✅ Approval granted")
        print("Applying remediation...")

        patch = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [
if mode == "human_approval":
    print("\n⚠️ Human approval required")
    print("Action:", action)
    print("Risk:", risk)

    approval = input("\nApprove remediation? (yes/no): ")
                            {
                                "name": "crash-test",
                                "command": None,
                                "args": None
                            }
                        ]
                    }
                }
            }
        }

        apps_api.patch_namespaced_deployment(
            name="crash-test",
            namespace="buildflow",
            body=patch
        )

        print("✅ Remediation applied")

    else:
        print("❌ Remediation cancelled")
