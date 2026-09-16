import requests
import sys

sys.path.append(".")

from incidents.incident_manager import create_incident

# ==========================================
# PROMETHEUS CONNECTION
# ==========================================

url = "http://localhost:9090/api/v1/query"


# ==========================================
# QUERY RESTART COUNT
# ==========================================

query = 'kube_pod_container_status_restarts_total{namespace="buildflow",pod=~"crash-test-.*"}'


response = requests.get(
    url,
    params={"query": query}
)

print("Status:", response.status_code)

data = response.json()

results = data["data"]["result"]


# ==========================================
# CHECK INCIDENTS
# ==========================================

for result in results:

    metric = result["metric"]

    pod = metric.get("pod")
    container = metric.get("container")

    restart_count = int(float(result["value"][1]))

    print("\nPod:", pod)
    print("Container:", container)
    print("Restart Count:", restart_count)


    # ======================================
    # CHECK ACTUAL POD STATE
    # ======================================

    state_query = (
        'kube_pod_container_status_waiting_reason'
        '{namespace="buildflow",'
        'pod="' + pod + '",'
        'reason="CrashLoopBackOff"}'
    )

    state_response = requests.get(
        url,
        params={"query": state_query}
    )

    state_data = state_response.json()

    state_results = state_data["data"]["result"]


    # ======================================
    # INCIDENT DECISION
    # ======================================

    if state_results:

    incident = {
        "type": "CrashLoopBackOff",
        "namespace": "buildflow",
        "pod": pod,
        "container": container,
        "restart_count": restart_count,
        "status": "detected"
    }

    print("🚨 INCIDENT DETECTED")
    print(incident)

    incident_id = create_incident(
        "CrashLoopBackOff",
        "buildflow-api",
        f"Pod {pod} entered CrashLoopBackOff"
    )

    print("Incident ID:", incident_id)
