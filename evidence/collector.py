import json
from kubernetes import client, config
import requests


# ==============================
# CONFIGURATION
# ==============================

NAMESPACE = "buildflow"
import sys

POD_NAME = sys.argv[1]

PROMETHEUS_URL = "http://localhost:9090/api/v1/query"
LOKI_URL = "http://localhost:3100/loki/api/v1/query_range"


# ==============================
# CONNECT TO KUBERNETES
# ==============================

config.load_kube_config()

v1 = client.CoreV1Api()


# ==============================
# EVIDENCE OBJECT
# ==============================

evidence = {
    "pod": {},
    "events": [],
    "metrics": {},
    "logs": []
}


# ==============================
# 1. POD EVIDENCE
# ==============================

pod = v1.read_namespaced_pod(
    name=POD_NAME,
    namespace=NAMESPACE
)

evidence["pod"]["name"] = pod.metadata.name
evidence["pod"]["status"] = pod.status.phase


# Container information

for container in pod.status.container_statuses or []:

    container_evidence = {
        "name": container.name,
        "restart_count": container.restart_count
    }

    # Current state

    if container.state.waiting:
        container_evidence["state"] = "Waiting"
        container_evidence["reason"] = container.state.waiting.reason

    elif container.state.running:
        container_evidence["state"] = "Running"

    elif container.state.terminated:
        container_evidence["state"] = "Terminated"
        container_evidence["reason"] = container.state.terminated.reason
        container_evidence["exit_code"] = container.state.terminated.exit_code

    # Previous termination

    if container.last_state.terminated:

        container_evidence["last_exit_code"] = (
            container.last_state.terminated.exit_code
        )

        container_evidence["last_reason"] = (
            container.last_state.terminated.reason
        )

    evidence["pod"]["container"] = container_evidence


# Container command and arguments

for container in pod.spec.containers:

    if container.name == evidence["pod"]["container"]["name"]:

        evidence["pod"]["command"] = container.command
        evidence["pod"]["args"] = container.args


# ==============================
# 2. KUBERNETES EVENTS
# ==============================

events = v1.list_namespaced_event(
    namespace=NAMESPACE
)

for event in events.items:

    # Only collect events related to our Pod

    if (
        event.involved_object
        and event.involved_object.name == POD_NAME
    ):

        event_evidence = {
            "reason": event.reason,
            "message": event.message
        }

        evidence["events"].append(event_evidence)


# ==============================
# 3. PROMETHEUS METRICS
# ==============================

query = (
    'kube_pod_container_status_restarts_total'
    '{namespace="buildflow",'
    f'pod="{POD_NAME}"}}'
)

response = requests.get(
    PROMETHEUS_URL,
    params={"query": query}
)

if response.status_code == 200:

    data = response.json()

    results = data["data"]["result"]

    for result in results:

        metric = result["metric"]

        evidence["metrics"] = {
            "pod": metric.get("pod"),
            "container": metric.get("container"),
            "restart_count": result["value"][1]
        }

else:

    evidence["metrics"] = {
        "error": f"Prometheus returned status {response.status_code}"
    }


# ==============================
# 4. LOKI LOGS
# ==============================

loki_query = (
    f'{{instance=~"buildflow/{POD_NAME}.*"}}'
)

headers = {
    "X-Scope-OrgID": "fake"
}

params = {
    "query": loki_query,
    "limit": 20
}

response = requests.get(
    LOKI_URL,
    params=params,
    headers=headers
)

if response.status_code == 200:

    data = response.json()

    results = data["data"]["result"]

    for stream in results:

        for timestamp, log_line in stream["values"]:

            evidence["logs"].append({
                "timestamp": timestamp,
                "message": log_line
            })

else:

    evidence["logs"].append({
        "error": f"Loki returned status {response.status_code}"
    })


# ==============================
# 5. DISPLAY FINAL EVIDENCE
# ==============================

print("\n")
print("========================================")
print("        BUILD FLOW EVIDENCE")
print("========================================")

print("\nPOD EVIDENCE")
print("----------------------------------------")

for key, value in evidence["pod"].items():
    print(f"{key}: {value}")


print("\nKUBERNETES EVENTS")
print("----------------------------------------")

for event in evidence["events"]:
    print("Reason:", event["reason"])
    print("Message:", event["message"])
    print()


print("PROMETHEUS METRICS")
print("----------------------------------------")

print(evidence["metrics"])


print("\nLOKI LOGS")
print("----------------------------------------")

for log in evidence["logs"]:
    print(log)


print("\n========================================")
print("FINAL EVIDENCE OBJECT")
print("========================================")

print(evidence)

with open("evidence/evidence.json", "w") as file:
    json.dump(evidence, file, indent=4)
