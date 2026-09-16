import json
import time

import requests
from kubernetes import client, config
from kubernetes.stream import stream

# ==========================================
# KUBERNETES CONNECTION
# ==========================================

config.load_kube_config()

core_api = client.CoreV1Api()

print("Connected to Kubernetes")


# ==========================================
# CONFIGURATION
# ==========================================

namespace = "buildflow"
label_selector = "app=crash-test"


# ==========================================
# FIND POD
# ==========================================

pods = core_api.list_namespaced_pod(
    namespace=namespace,
    label_selector=label_selector
)

if not pods.items:
    print("❌ No crash-test Pod found")

    result = {
        "recovery": "failed",
        "reason": "No matching Pod found"
    }

    with open("recovery/recovery.json", "w") as file:
        json.dump(result, file, indent=4)

    exit()


pod = pods.items[0]

pod_name = pod.metadata.name
pod_status = pod.status.phase


print("\n========================================")
print("        RECOVERY VERIFICATION")
print("========================================")

print("Pod:", pod_name)
print("Pod Status:", pod_status)


# ==========================================
# CHECK CONTAINER STATUS
# ==========================================

if not pod.status.container_statuses:
    print("❌ No container status available")

    result = {
        "pod": pod_name,
        "pod_status": pod_status,
        "recovery": "failed",
        "reason": "Container status unavailable"
    }

    with open("recovery/recovery.json", "w") as file:
        json.dump(result, file, indent=4)

    exit()


container_status = pod.status.container_statuses[0]

restart_count_before = container_status.restart_count

print("Restart Count:", restart_count_before)


# ==========================================
import json
import time

from kubernetes import client, config
from kubernetes.stream import stream


# ==========================================
# KUBERNETES CONNECTION
# ==========================================

config.load_kube_config()

core_api = client.CoreV1Api()

print("Connected to Kubernetes")


# ==========================================
# CONFIGURATION
# ==========================================

namespace = "buildflow"
label_selector = "app=crash-test"


# ==========================================
# FIND POD
# ==========================================

pods = core_api.list_namespaced_pod(
    namespace=namespace,
    label_selector=label_selector
)

if not pods.items:
    print("❌ No crash-test Pod found")

    result = {
        "recovery": "failed",
        "reason": "No matching Pod found"
    }

    with open("recovery/recovery.json", "w") as file:
        json.dump(result, file, indent=4)

    exit()


pod = pods.items[0]

pod_name = pod.metadata.name
pod_status = pod.status.phase


print("\n========================================")
print("        RECOVERY VERIFICATION")
print("========================================")

print("Pod:", pod_name)
print("Pod Status:", pod_status)


# ==========================================
# CHECK CONTAINER STATUS
# ==========================================

if not pod.status.container_statuses:
    print("❌ No container status available")

    result = {
        "pod": pod_name,
        "pod_status": pod_status,
        "recovery": "failed",
        "reason": "Container status unavailable"
    }

    with open("recovery/recovery.json", "w") as file:
        json.dump(result, file, indent=4)

    exit()


container_status = pod.status.container_statuses[0]

restart_count_before = container_status.restart_count

print("Restart Count:", restart_count_before)


# ==========================================
# WAIT BEFORE SECOND OBSERVATION
# ==========================================

print("\nWaiting 10 seconds before second observation...")

time.sleep(10)


# ==========================================
# GET POD AGAIN
# ==========================================

pods = core_api.list_namespaced_pod(
    namespace=namespace,
    label_selector=label_selector
)

if not pods.items:
    print("❌ Pod disappeared during verification")

    result = {
        "pod": pod_name,
        "recovery": "failed",
        "reason": "Pod disappeared during verification"
    }

    with open("recovery/recovery.json", "w") as file:
        json.dump(result, file, indent=4)

    exit()


pod = pods.items[0]

pod_name_after = pod.metadata.name
pod_status_after = pod.status.phase

print("\nSecond observation:")
print("Pod:", pod_name_after)
print("Pod Status:", pod_status_after)


# ==========================================
# SECOND RESTART COUNT
# ==========================================

if not pod.status.container_statuses:
    restart_count_after = -1
else:
    container_status = pod.status.container_statuses[0]
    restart_count_after = container_status.restart_count

print("Restart Count:", restart_count_after)


# ==========================================
# APPLICATION HEALTH CHECK
# ==========================================

health_ok = False
health_status = None
health_response = None

try:
    result = stream(
        core_api.connect_get_namespaced_pod_exec,
        name=pod_name_after,
        namespace=namespace,
        command=[
            "python",
            "-c",
            (
                "import urllib.request; "
                "response=urllib.request.urlopen("
                "'http://127.0.0.1:5000/health', timeout=5"
                "); "
                "print(response.status); "
                "print(response.read().decode())"
            )
        ],
        stderr=True,
        stdin=False,
        stdout=True,
        tty=False
    )

    output = result.strip()

    print("\nHealth Check:")
    print(output)

    lines = output.splitlines()

    if len(lines) >= 2:
        health_status = int(lines[0])
        health_response = lines[1].strip()

        if (
            health_status == 200
            and health_response == "healthy"
        ):
            health_ok = True

except Exception as error:
    print("\n❌ Health check failed")
    print("Error:", error)


# ==========================================
# RECOVERY CONDITIONS
# ==========================================

pod_running = pod_status_after == "Running"

restart_stable = (
    restart_count_after == restart_count_before
)


# ==========================================
# FINAL RECOVERY DECISION
# ==========================================

if pod_running and restart_stable and health_ok:

    recovery_status = "confirmed"

    reason = [
        "Pod is Running",
        "Restart count remained stable",
        "Application /health endpoint returned healthy"
    ]

else:

    recovery_status = "failed"

    reason = []

    if not pod_running:
        reason.append("Pod is not Running")

    if not restart_stable:
        reason.append("Restart count increased")

    if not health_ok:
        reason.append("Application health check failed")


# ==========================================
# FINAL RESULT
# ==========================================

result = {
    "pod": pod_name_after,
    "pod_status": pod_status_after,
    "restart_count_before": restart_count_before,
    "restart_count_after": restart_count_after,
    "health_status": health_status,
    "health_response": health_response,
    "recovery": recovery_status,
    "reason": reason
}


# ==========================================
# SAVE RESULT
# ==========================================

with open("recovery/recovery.json", "w") as file:
    json.dump(result, file, indent=4)


# ==========================================
# DISPLAY RESULT
# ==========================================

print("\n========================================")
print("          RECOVERY RESULT")
print("========================================")

print(
    json.dumps(
        result,
        indent=4
    )
)

if recovery_status == "confirmed":
    print("\n✅ RECOVERY CONFIRMED")
else:
    print("\n❌ RECOVERY FAILED")
